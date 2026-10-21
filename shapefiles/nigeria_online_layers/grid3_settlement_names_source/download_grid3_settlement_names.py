#!/usr/bin/env python3
"""Download GRID3 Settlement Names as a compact point Shapefile.

Output attributes are exactly FID, LGA_NAME, STATE_NAME, SET_NAME. Coordinates
are the EPSG:4326 point geometry. This script must be run in an environment
with network access to services3.arcgis.com.

Dependency: pip install pyshp
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import shapefile

SERVICE_LAYER = (
    "https://services3.arcgis.com/BU6Aadhn6tbBEdyk/arcgis/rest/services/"
    "Settlements_in_Nigeria/FeatureServer/0"
)
EXPECTED_COUNT = 292_438
PAGE_SIZE = 2_000
WGS84_ESRI_WKT = (
    'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
    'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
)


def api_get(params: dict, retries: int = 5) -> dict:
    url = SERVICE_LAYER + "/query?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "GRID3-NGA-SettlementNames-export/1.0"},
    )
    last_error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if "error" in payload:
                raise RuntimeError(f"ArcGIS service error: {payload['error']}")
            return payload
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(f"ArcGIS query failed after {retries} attempts: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="Default: sibling grid3_settlement_names/")
    parser.add_argument(
        "--allow-count-change", action="store_true",
        help="Continue if the live service count no longer equals 292,438.",
    )
    args = parser.parse_args()

    source_dir = Path(__file__).resolve().parent
    bundle = source_dir.parent
    output_dir = args.output_dir.resolve() if args.output_dir else bundle / "grid3_settlement_names"
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty output directory: {output_dir}")

    count_result = api_get({"where": "1=1", "returnCountOnly": "true", "f": "json"})
    total = int(count_result["count"])
    if total != EXPECTED_COUNT and not args.allow_count_change:
        raise RuntimeError(
            f"Source reports {total:,} features, not pinned {EXPECTED_COUNT:,}; "
            "review before using --allow-count-change."
        )

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    seen_fids = set()
    bounds = [math.inf, math.inf, -math.inf, -math.inf]
    with tempfile.TemporaryDirectory(prefix="grid3-settlement-names-") as tmp:
        tmp_dir = Path(tmp)
        base = tmp_dir / "grid3_settlement_names"
        writer = shapefile.Writer(str(base), shapeType=shapefile.POINT, encoding="utf-8")
        writer.autoBalance = 1
        writer.field("FID", "N", size=12, decimal=0)
        writer.field("LGA_NAME", "C", size=44)
        writer.field("STATE_NAME", "C", size=22)
        writer.field("SET_NAME", "C", size=158)

        for offset in range(0, total, PAGE_SIZE):
            page = api_get({
                "where": "1=1",
                "outFields": "FID,lganame,statename,set_name",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
                "orderByFields": "FID ASC",
                "resultOffset": offset,
                "resultRecordCount": PAGE_SIZE,
            })
            features = page.get("features", [])
            if not features:
                raise RuntimeError(f"Empty feature page at offset {offset:,}")
            for feature in features:
                props = feature.get("properties") or {}
                geom = feature.get("geometry") or {}
                coords = geom.get("coordinates")
                if geom.get("type") != "Point" or not coords or len(coords) < 2:
                    raise RuntimeError(f"Missing/non-point geometry at offset {offset:,}")
                lon, lat = float(coords[0]), float(coords[1])
                if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
                    raise RuntimeError(f"Invalid coordinates: {lon}, {lat}")
                fid = int(props["FID"])
                if fid in seen_fids:
                    raise RuntimeError(f"Duplicate source FID: {fid}")
                seen_fids.add(fid)
                lga = "" if props.get("lganame") is None else str(props["lganame"])
                state = "" if props.get("statename") is None else str(props["statename"])
                name = "" if props.get("set_name") is None else str(props["set_name"])
                for field, value, width in [("LGA_NAME", lga, 44), ("STATE_NAME", state, 22), ("SET_NAME", name, 158)]:
                    if len(value.encode("utf-8")) > width:
                        raise RuntimeError(f"{field} exceeds DBF width {width} bytes for FID {fid}")
                writer.point(lon, lat)
                writer.record(fid, lga, state, name)
                bounds[0] = min(bounds[0], lon)
                bounds[1] = min(bounds[1], lat)
                bounds[2] = max(bounds[2], lon)
                bounds[3] = max(bounds[3], lat)
            print(f"Downloaded {min(offset + len(features), total):,}/{total:,}", file=sys.stderr)
        writer.close()
        if len(seen_fids) != total:
            raise RuntimeError(f"Downloaded {len(seen_fids):,} unique FIDs; expected {total:,}")

        base.with_suffix(".prj").write_text(WGS84_ESRI_WKT, encoding="utf-8")
        base.with_suffix(".cpg").write_text("UTF-8", encoding="ascii")
        check = shapefile.Reader(str(base), encoding="utf-8")
        expected_fields = ["FID", "LGA_NAME", "STATE_NAME", "SET_NAME"]
        if len(check) != total or check.shapeType != shapefile.POINT:
            raise RuntimeError("Output failed feature-count or geometry-type validation")
        if [field[0] for field in check.fields[1:]] != expected_fields:
            raise RuntimeError("Output fields differ from the requested schema")
        for item in check.iterShapeRecords():
            if item.shape.shapeType != shapefile.POINT or len(item.shape.points) != 1:
                raise RuntimeError("Output contains an empty or non-point geometry")

        output_dir.mkdir(parents=True, exist_ok=True)
        for component in tmp_dir.iterdir():
            shutil.copy2(component, output_dir / component.name)

    attribution = """GRID3 NGA - Settlement Names attribution\n\nSource: eHealth Africa, Proxy Logics, and Oak Ridge National Laboratory (ORNL). 2020. Settlement Points in Nigeria. Geo-Referenced Infrastructure and Demographic Data for Development (GRID3). https://grid3.gov.ng/\nSource page: https://data.grid3.org/datasets/GRID3::grid3-nga-settlement-names/about\nLicense: Creative Commons Attribution 4.0 International (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/\n\nFields: FID, LGA_NAME, STATE_NAME, SET_NAME. Coordinates are EPSG:4326 point geometry.\n"""
    (output_dir / "ATTRIBUTION.txt").write_text(attribution, encoding="utf-8")
    summary = {
        "dataset": "GRID3 NGA - Settlement Names",
        "feature_count": total,
        "geometry_type": "Point",
        "crs": "EPSG:4326",
        "fields": ["FID", "LGA_NAME", "STATE_NAME", "SET_NAME"],
        "bounds_lon_lat": [round(x, 8) for x in bounds],
        "license": "CC BY 4.0",
        "attribution": "eHealth Africa, Proxy Logics, and Oak Ridge National Laboratory (ORNL); GRID3.",
        "source_page": "https://data.grid3.org/datasets/GRID3::grid3-nga-settlement-names/about",
        "feature_service": SERVICE_LAYER,
        "downloaded_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": {},
    }
    for component in sorted(output_dir.iterdir()):
        summary["sha256"][component.name] = hashlib.sha256(component.read_bytes()).hexdigest()
    (output_dir / "validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), **summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
