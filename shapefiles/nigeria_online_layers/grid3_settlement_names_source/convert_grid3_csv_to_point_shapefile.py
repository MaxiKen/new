#!/usr/bin/env python3
"""Convert a GRID3 Settlement Names ArcGIS CSV export to a point Shapefile.

The source CSV is not included. Save the downloaded export locally, then run:
  python convert_grid3_csv_to_point_shapefile.py path/to/Settlements_in_Nigeria.csv

Dependencies: pip install pyshp
Output: sibling grid3_settlement_names/ (never overwrites a non-empty folder).
Only FID, LGA_NAME, STATE_NAME, and SET_NAME are written as attributes; XY are
stored as point geometry in EPSG:4326. All valid source rows are retained.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path

import shapefile

# WGS 84 geographic CRS, WKT1 ESRI form.
WGS84_ESRI_WKT = (
    'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
    'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
)

# Known ArcGIS source field aliases. Headers are normalized before matching.
FID_KEYS = {"fid", "objectid", "object_id", "oid"}
LGA_KEYS = {"lganame", "lga_name", "lga"}
STATE_KEYS = {"statename", "state_name", "state"}
SETTLEMENT_KEYS = {"set_name", "settlement_name", "settlementname", "name"}
LON_KEYS = {"x", "lon", "long", "longitude", "x_coord", "xcoordinate", "point_x", "shape_x"}
LAT_KEYS = {"y", "lat", "latitude", "y_coord", "ycoordinate", "point_y", "shape_y"}
GEOMETRY_KEYS = {"geometry", "shape", "esri_geometry"}


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lstrip("\ufeff").lower()).strip("_")


def choose_field(normalized_to_original: dict[str, str], candidates: set[str], label: str) -> str:
    for candidate in candidates:
        if candidate in normalized_to_original:
            return normalized_to_original[candidate]
    raise ValueError(
        f"Could not find a {label} column. CSV headers: {', '.join(normalized_to_original.values())}"
    )


def parse_geometry(value: str):
    """Read point geometry from common ArcGIS CSV forms (JSON or WKT)."""
    text = (value or "").strip()
    if not text:
        raise ValueError("empty geometry")
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            if "x" in obj and "y" in obj:
                return float(obj["x"]), float(obj["y"])
            if obj.get("type", "").lower() == "point":
                coords = obj.get("coordinates", [])
                return float(coords[0]), float(coords[1])
            if "geometry" in obj and isinstance(obj["geometry"], dict):
                geom = obj["geometry"]
                if "x" in geom and "y" in geom:
                    return float(geom["x"]), float(geom["y"])
    except (json.JSONDecodeError, TypeError, ValueError, IndexError):
        pass
    match = re.fullmatch(r"\s*POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)\s*", text, re.I)
    if match:
        return float(match.group(1)), float(match.group(2))
    raise ValueError(f"unsupported point geometry encoding: {text[:120]!r}")


def cell(row: dict, field: str) -> str:
    value = row.get(field, "")
    return "" if value is None else str(value).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Downloaded GRID3 Settlement Names CSV export")
    parser.add_argument(
        "--output-dir", type=Path,
        help="Output directory (default: sibling grid3_settlement_names/)",
    )
    parser.add_argument(
        "--lon-field", help="Override longitude/X field name if it cannot be auto-detected"
    )
    parser.add_argument(
        "--lat-field", help="Override latitude/Y field name if it cannot be auto-detected"
    )
    parser.add_argument(
        "--geometry-field", help="Use a GeoJSON/WKT/Esri point geometry column instead of XY fields"
    )
    args = parser.parse_args()

    csv_path = args.csv_path.expanduser().resolve()
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    source_dir = Path(__file__).resolve().parent
    bundle = source_dir.parent
    output_dir = args.output_dir.expanduser().resolve() if args.output_dir else bundle / "grid3_settlement_names"
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(
            f"Refusing to overwrite non-empty output directory {output_dir}; choose another --output-dir."
        )

    source_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    row_count = 0
    invalid_count = 0
    invalid_examples = []
    bounds = [math.inf, math.inf, -math.inf, -math.inf]
    field_counts = Counter()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        normalized = {normalize_header(name): name for name in reader.fieldnames}
        fid_field = choose_field(normalized, FID_KEYS, "FID")
        lga_field = choose_field(normalized, LGA_KEYS, "LGA name")
        state_field = choose_field(normalized, STATE_KEYS, "state name")
        set_field = choose_field(normalized, SETTLEMENT_KEYS, "settlement name")
        geometry_field = None
        lon_field = args.lon_field
        lat_field = args.lat_field
        if args.geometry_field:
            geometry_field = choose_field(normalized, {normalize_header(args.geometry_field)}, "geometry")
        elif not (lon_field and lat_field):
            for candidate in GEOMETRY_KEYS:
                if candidate in normalized:
                    geometry_field = normalized[candidate]
                    break
            if geometry_field is None:
                lon_field = choose_field(normalized, LON_KEYS, "longitude/X")
                lat_field = choose_field(normalized, LAT_KEYS, "latitude/Y")
        else:
            lon_field = choose_field(normalized, {normalize_header(lon_field)}, "longitude/X")
            lat_field = choose_field(normalized, {normalize_header(lat_field)}, "latitude/Y")

        # Create a temporary shapefile, then publish it only after all rows pass.
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="grid3-csv-to-shp-") as tmp:
            tmp_dir = Path(tmp)
            base = tmp_dir / "grid3_settlement_names"
            writer = shapefile.Writer(str(base), shapeType=shapefile.POINT, encoding="utf-8")
            writer.autoBalance = 1
            writer.field("FID", "N", size=12, decimal=0)
            writer.field("LGA_NAME", "C", size=44)
            writer.field("STATE_NAME", "C", size=22)
            writer.field("SET_NAME", "C", size=158)

            for line_number, row in enumerate(reader, start=2):
                try:
                    if geometry_field:
                        lon, lat = parse_geometry(cell(row, geometry_field))
                    else:
                        lon = float(cell(row, lon_field))
                        lat = float(cell(row, lat_field))
                    if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
                        raise ValueError(f"invalid coordinates {lon}, {lat}")
                    fid_text = cell(row, fid_field)
                    if not fid_text:
                        raise ValueError("missing FID")
                    fid = int(float(fid_text))
                    lga = cell(row, lga_field)
                    state = cell(row, state_field)
                    set_name = cell(row, set_field)
                    for label, value, width in [("LGA_NAME", lga, 44), ("STATE_NAME", state, 22), ("SET_NAME", set_name, 158)]:
                        if len(value.encode("utf-8")) > width:
                            raise ValueError(f"{label} exceeds its DBF width ({width} bytes)")
                    writer.point(lon, lat)
                    writer.record(fid, lga, state, set_name)
                    row_count += 1
                    field_counts["records"] += 1
                    bounds[0] = min(bounds[0], lon)
                    bounds[1] = min(bounds[1], lat)
                    bounds[2] = max(bounds[2], lon)
                    bounds[3] = max(bounds[3], lat)
                except (TypeError, ValueError, IndexError) as exc:
                    invalid_count += 1
                    if len(invalid_examples) < 10:
                        invalid_examples.append({"line": line_number, "error": str(exc)})

            if invalid_count:
                writer.close()
                raise ValueError(
                    f"Rejected export: {invalid_count} invalid rows; examples: {invalid_examples}"
                )
            writer.close()

            # WGS 84 / EPSG:4326 sidecars.
            base.with_suffix(".prj").write_text(WGS84_ESRI_WKT, encoding="utf-8")
            base.with_suffix(".cpg").write_text("UTF-8", encoding="ascii")

            check = shapefile.Reader(str(base), encoding="utf-8")
            if len(check) != row_count or check.shapeType != shapefile.POINT:
                raise RuntimeError("Output Shapefile failed feature-count or geometry-type validation")
            if [field[0] for field in check.fields[1:]] != ["FID", "LGA_NAME", "STATE_NAME", "SET_NAME"]:
                raise RuntimeError("Output DBF schema differs from the requested fields")
            for item in check.iterShapeRecords():
                if item.shape.shapeType != shapefile.POINT or len(item.shape.points) != 1:
                    raise RuntimeError("Output contains a non-point or empty geometry")

            output_dir.mkdir(parents=True, exist_ok=True)
            for component in tmp_dir.iterdir():
                shutil.copy2(component, output_dir / component.name)

    attribution = """GRID3 NGA - Settlement Names attribution\n\nSource: eHealth Africa, Proxy Logics, and Oak Ridge National Laboratory (ORNL). 2020. Settlement Points in Nigeria. Geo-Referenced Infrastructure and Demographic Data for Development (GRID3). https://grid3.gov.ng/\nSource page: https://data.grid3.org/datasets/GRID3::grid3-nga-settlement-names/about\nLicense: Creative Commons Attribution 4.0 International (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/\n\nThis point Shapefile contains the source FID, LGA name, state name, and settlement name. Coordinates are stored as EPSG:4326 point geometry. All valid CSV rows are retained.\n"""
    (output_dir / "ATTRIBUTION.txt").write_text(attribution, encoding="utf-8")
    summary = {
        "source_dataset": "GRID3 NGA - Settlement Names",
        "source_csv": csv_path.name,
        "source_csv_sha256": source_sha,
        "feature_count": row_count,
        "invalid_rows": invalid_count,
        "geometry_type": "Point",
        "crs": "EPSG:4326",
        "fields": ["FID", "LGA_NAME", "STATE_NAME", "SET_NAME"],
        "bounds_lon_lat": [round(x, 8) for x in bounds],
        "license": "CC BY 4.0",
        "source_page": "https://data.grid3.org/datasets/GRID3::grid3-nga-settlement-names/about",
        "note": "Coordinates are stored as point geometry; no records are clipped or dropped based on country-boundary coverage.",
    }
    (output_dir / "validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), **summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
