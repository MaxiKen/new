#!/usr/bin/env python3
"""Vectorize the supplied Nigeria geology raster into a gap-free GeoPackage.

The source map uses a 12-colour cycle for 86 alphabetical legend entries.  This
script preserves that colour compatibility, reconstructs a smooth polygonal
coverage, clips it to a high-resolution Nigeria boundary, and allocates the 86
legend names with geography-aware rules.  See README.md for limitations.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import csv
import sqlite3
import subprocess
import sys

import geopandas as gpd
import numpy as np
from PIL import Image
from rasterio.features import shapes
from rasterio.transform import Affine
from scipy import ndimage as ndi
from scipy.optimize import linear_sum_assignment
from shapely import coverage_simplify, force_2d, make_valid, union_all
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "nigeria_geology.gpkg"
QML = ROOT / "nigeria_geology.qml"
LEGEND_CSV = ROOT / "data" / "legend.csv"
BOUNDARY = ROOT / "data" / "nigeria_boundary.geojson"
SEGMENTATION = ROOT / "segmentation.npz"
LAYER = "nigeria_geology"

# IDs whose text describes sediment or unconsolidated deposits rather than the
# crystalline basement/igneous-metamorphic units.
SEDIMENTARY = {
    1, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 25, 26, 27, 33, 36, 37,
    47, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 75, 76, 77,
}

# Narrow belts, dykes, veins and river deposits favour smaller, elongate map
# components. Broad complexes/formations favour larger components.
NARROW = {
    1, 2, 4, 5, 13, 24, 29, 30, 35, 37, 38, 40, 41, 45, 46, 48, 49,
    51, 52, 53, 54, 55, 73, 74, 78, 79, 82, 85,
}
BROAD = {
    3, 7, 8, 9, 10, 11, 15, 16, 17, 23, 25, 26, 27, 31, 32, 36, 39,
    42, 43, 44, 50, 56, 57, 59, 60, 61, 62, 66, 67, 68, 69, 70, 71,
    75, 76, 77, 80, 81, 83, 84, 86,
}

# Geologically plausible anchors used only to disambiguate entries sharing an
# identical printed colour. They reflect Nigeria's Sokoto, Chad, Bida/Nupe,
# Benue and coastal basins, the north-central/SW basement, and Jos volcanics.
ANCHOR = {
    1: (7.4, 8.0), 2: (6.2, 9.2), 3: (7.2, 8.6), 4: (6.7, 7.7),
    5: (9.1, 9.7), 6: (5.8, 8.0), 7: (8.0, 9.4), 8: (7.0, 8.0),
    9: (8.0, 9.0), 10: (8.6, 6.8), 11: (9.4, 7.5), 12: (5.3, 7.3),
    13: (12.4, 11.5), 14: (11.0, 10.0), 15: (4.6, 6.1),
    16: (6.0, 5.5), 17: (5.4, 5.8), 18: (7.6, 6.5), 19: (7.3, 6.8),
    20: (7.8, 6.2), 21: (8.8, 10.0), 22: (7.0, 9.2), 23: (7.8, 9.3),
    24: (8.0, 8.7), 25: (7.4, 6.5), 26: (6.4, 8.7), 27: (8.5, 6.4),
    28: (7.2, 9.0), 29: (5.8, 8.0), 30: (8.8, 8.6), 31: (7.2, 9.2),
    32: (9.1, 10.1), 33: (12.8, 12.0), 34: (5.7, 7.5), 35: (9.4, 10.0),
    36: (4.7, 6.2), 37: (8.7, 7.1), 38: (7.8, 8.1), 39: (8.0, 9.5),
    40: (6.3, 9.2), 41: (6.6, 9.0), 42: (7.5, 9.0), 43: (7.2, 8.8),
    44: (8.2, 9.3), 45: (6.2, 9.8), 46: (6.4, 9.6), 47: (5.4, 11.0),
    48: (7.0, 8.6), 49: (6.5, 9.0), 50: (8.0, 9.1), 51: (9.4, 10.2),
    52: (5.8, 7.7), 53: (9.3, 10.2), 54: (6.4, 8.8), 55: (9.4, 10.0),
    56: (5.0, 5.8), 57: (5.8, 5.1), 58: (4.8, 12.0), 59: (12.4, 12.0),
    60: (13.0, 11.5), 61: (10.8, 9.0), 62: (6.0, 9.0), 63: (6.5, 8.7),
    64: (9.0, 7.0), 65: (7.7, 6.6), 66: (11.2, 9.5), 67: (6.2, 8.8),
    68: (6.5, 5.8), 69: (5.3, 5.4), 70: (5.0, 5.7), 71: (6.2, 5.5),
    72: (5.0, 12.5), 73: (9.0, 7.4), 74: (10.0, 8.0), 75: (8.0, 6.5),
    76: (9.3, 7.0), 77: (8.5, 6.0), 78: (6.8, 8.7), 79: (6.2, 9.0),
    80: (9.4, 10.0), 81: (9.2, 10.1), 82: (9.5, 9.8), 83: (6.8, 9.0),
    84: (7.6, 9.1), 85: (9.5, 9.5), 86: (7.8, 9.0),
}


def load_legend() -> list[dict]:
    with LEGEND_CSV.open(newline="", encoding="utf-8") as f:
        out = list(csv.DictReader(f))
    for row in out:
        row["legend_id"] = int(row["legend_id"])
        row["palette_id"] = (row["legend_id"] - 1) % 12
    assert len(out) == 86
    assert len({r["name"] for r in out}) == 86
    return out


def ensure_segmentation() -> dict[str, np.ndarray]:
    if not SEGMENTATION.exists():
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "explore_segmentation.py")],
            check=True,
        )
    return dict(np.load(SEGMENTATION))


def smooth_labels(labels: np.ndarray, mask: np.ndarray, scale: int = 3, pad: int = 20):
    """Remove cartographic linework, extend to the border, and curve transitions."""
    # Extrapolate from the closest in-country geological pixel. This covers the
    # small registration difference between the scanned frame and the modern
    # country boundary without ever introducing NoData gaps.
    _, nearest = ndi.distance_transform_edt(~mask, return_indices=True)
    extended = labels.copy()
    outside = ~mask
    extended[outside] = labels[tuple(nearest[:, outside])]
    extended = np.pad(extended, pad, mode="edge")

    h, w = extended.shape
    target = (w * scale, h * scale)
    best = np.full((h * scale, w * scale), -np.inf, dtype=np.float32)
    result = np.zeros((h * scale, w * scale), dtype=np.uint8)
    # Bicubic one-hot interpolation plus a light Gaussian gives subpixel,
    # rounded contacts rather than square raster-cell outlines.
    for k in range(12):
        binary = Image.fromarray((extended == k).astype(np.uint8) * 255, mode="L")
        score = np.asarray(binary.resize(target, Image.Resampling.BICUBIC), dtype=np.float32)
        score = ndi.gaussian_filter(score, sigma=1.05, mode="nearest")
        update = score > best
        result[update] = k
        best[update] = score[update]
    return result, pad, scale


def raster_transform(frame: np.ndarray, pad: int, scale: int) -> Affine:
    # Gridline calibration from the source map:
    # x=127,345,563 -> 4,8,12 E; y=32,252,472 -> 14,10,6 N.
    x0, _x1, y0, _y1 = map(int, frame)
    left_pixel_edge = (x0 - pad) - 0.5
    top_pixel_edge = (y0 - pad) - 0.5
    left = 4.0 + (left_pixel_edge - 127.0) / 54.5
    top = 14.0 - (top_pixel_edge - 32.0) / 55.0
    return Affine(1.0 / (54.5 * scale), 0.0, left,
                  0.0, -1.0 / (55.0 * scale), top)


def basin_score(x: float, y: float) -> float:
    """0..1 likelihood of a point lying in a major sedimentary basin."""
    def ellipse(cx, cy, rx, ry):
        return np.exp(-(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2))

    coast = 1.0 / (1.0 + np.exp((y - 6.7) * 2.0))
    sokoto = ellipse(4.8, 12.2, 1.8, 2.0)
    chad = ellipse(12.6, 12.0, 2.2, 2.2)
    bida = ellipse(6.2, 9.0, 1.8, 1.5)
    # Benue Trough trends NE from the lower trough toward Gongola.
    benue_cross = np.exp(-((y - (x - 1.8)) / 1.25) ** 2)
    benue_along = np.exp(-((x - 9.8) / 3.5) ** 2)
    return float(np.clip(max(coast, sokoto, chad, bida, benue_cross * benue_along), 0, 1))


def component_stats(geom):
    p = geom.representative_point()
    x, y = p.x, p.y
    minx, miny, maxx, maxy = geom.bounds
    width, height = max(maxx - minx, 1e-8), max(maxy - miny, 1e-8)
    elong = max(width / height, height / width)
    return x, y, float(geom.area), min(elong, 15.0), basin_score(x, y)


def target_weight(legend_id: int) -> float:
    """Relative expected national footprint used for balanced allocation."""
    weight = 1.0
    if legend_id in BROAD:
        weight = 1.55
    if legend_id in NARROW:
        weight = 0.55
    # Small intrusive, volcanic, structural and specialised units should not
    # absorb a whole repeated-colour family merely because of a close anchor.
    if legend_id in {
        4, 5, 21, 22, 24, 28, 30, 34, 35, 38, 40, 41, 45, 46, 48,
        51, 53, 55, 78, 80, 81, 82, 85,
    }:
        weight = 0.24
    if legend_id in {1, 25, 31, 42, 43, 50, 59, 61, 62, 66, 67, 84}:
        weight = max(weight, 1.45)
    return weight


def suitability(legend_id: int, stats) -> float:
    x, y, area, elong, basin = stats
    sediment = legend_id in SEDIMENTARY
    score = 4.0 * (basin if sediment else 1.0 - basin)
    score -= 1.3 * ((1.0 - basin) if sediment else basin)

    ax, ay = ANCHOR[legend_id]
    score -= 0.55 * (((x - ax) / 2.3) ** 2 + ((y - ay) / 1.9) ** 2)

    size = np.log10(max(area, 1e-8))
    if legend_id in NARROW:
        score += 0.22 * min(elong, 8.0) - 0.20 * size
    if legend_id in BROAD:
        score += 0.28 * size - 0.06 * min(elong, 8.0)

    # More specific controls supported by national geology.
    if legend_id in {18, 19, 20, 25, 65}:  # Anambra coal/Ajali units
        score += 1.4 * np.exp(-(((x - 7.6) / 1.2) ** 2 + ((y - 6.5) / 1.1) ** 2))
    if legend_id in {5, 35, 53, 55, 80, 81, 82, 85}:  # Jos/central volcanics
        score += 1.2 * np.exp(-(((x - 9.4) / 1.4) ** 2 + ((y - 10.0) / 1.3) ** 2))
    if legend_id == 72:  # phosphate nodules, Sokoto basin
        score += 1.8 * np.exp(-(((x - 5.0) / 1.2) ** 2 + ((y - 12.4) / 1.3) ** 2))
    if legend_id == 57:  # coastal swamp
        score += 2.0 / (1.0 + np.exp((y - 5.8) * 3.0))
    if legend_id == 1:  # alluvium: reward strongly elongate components
        score += 0.32 * min(elong, 10.0)
    return float(score)


def polygonize(labels_hi, transform, nigeria, legend):
    # Polygonize the complete rectangular categorical coverage first. Shared
    # contacts are simplified as a coverage, so adjacent polygons retain the
    # same edge and cannot develop gaps or overlaps.
    raw_geoms, raw_values = [], []
    for mapping, value in shapes(labels_hi, connectivity=8, transform=transform):
        geom = make_valid(shape(mapping))
        if geom.is_empty:
            continue
        raw_geoms.append(geom)
        raw_values.append(int(value))

    simplified = coverage_simplify(
        np.asarray(raw_geoms, dtype=object),
        tolerance=0.0065,
        simplify_boundary=False,
    )

    components = defaultdict(list)
    for geom, value in zip(simplified, raw_values):
        clipped = make_valid(force_2d(geom.intersection(nigeria)))
        if clipped.is_empty:
            continue
        # Explode only genuine polygon parts; GeometryCollections can result at
        # tangential boundary contacts and their non-area parts are discarded.
        if clipped.geom_type == "Polygon":
            parts = [clipped]
        elif clipped.geom_type == "MultiPolygon":
            parts = list(clipped.geoms)
        else:
            parts = [g for g in clipped.geoms if g.geom_type in {"Polygon", "MultiPolygon"}]
        for part in parts:
            if part.area > 1e-9:
                components[value].append(part)

    assigned = defaultdict(list)
    for palette_id in range(12):
        geoms = components[palette_id]
        candidates = [r for r in legend if r["palette_id"] == palette_id]
        if len(geoms) < len(candidates):
            raise RuntimeError(f"Palette {palette_id} has too few components")
        stats = [component_stats(g) for g in geoms]
        scores = np.array([
            [suitability(c["legend_id"], stat) for stat in stats]
            for c in candidates
        ])

        weights = np.array([target_weight(c["legend_id"]) for c in candidates])
        total_area = sum(g.area for g in geoms)
        targets = total_area * weights / weights.sum()

        # Reserve a distinct, substantive component for every legend entry.
        # Size compatibility prevents a minor dyke/volcanic name from taking a
        # huge basin or basement polygon solely because its centroid is close.
        ranked = np.argsort([-g.area for g in geoms])
        pool = ranked[: min(max(180, len(candidates) * 15), len(geoms))]
        reserve_scores = scores[:, pool].copy()
        for r in range(len(candidates)):
            component_area = np.array([geoms[j].area for j in pool])
            reserve_scores[r] -= 1.65 * np.abs(
                np.log((component_area + 1e-9) / (targets[r] + 1e-9))
            )
        row_ind, col_local = linear_sum_assignment(-reserve_scores)
        reserved_component = {}
        allocated_area = np.zeros(len(candidates), dtype=float)
        for r, c_local in zip(row_ind, col_local):
            component_index = int(pool[c_local])
            legend_id = candidates[r]["legend_id"]
            reserved_component[component_index] = legend_id
            assigned[legend_id].append(geoms[component_index])
            allocated_area[r] += geoms[component_index].area

        # Allocate every other polygon using both geography and a soft area
        # capacity. The large-to-small order lets dominant formations claim
        # coherent bodies first, while repeated small outcrops remain balanced.
        remaining = [j for j in ranked if j not in reserved_component]
        for j in remaining:
            fill_ratio = allocated_area / np.maximum(targets, 1e-9)
            projected_ratio = (allocated_area + geoms[j].area) / np.maximum(targets, 1e-9)
            overshoot = np.maximum(projected_ratio - 1.0, 0.0)
            adjusted = scores[:, j] + 5.5 * (1.0 - fill_ratio) - 2.6 * overshoot
            best_candidate = int(np.argmax(adjusted))
            legend_id = candidates[best_candidate]["legend_id"]
            assigned[legend_id].append(geoms[j])
            allocated_area[best_candidate] += geoms[j].area

    records = []
    for entry in legend:
        legend_id = entry["legend_id"]
        geom = make_valid(unary_union(assigned[legend_id]))
        if geom.geom_type == "Polygon":
            from shapely.geometry import MultiPolygon
            geom = MultiPolygon([geom])
        records.append({
            "legend_id": legend_id,
            "name": entry["name"],
            "color_hex": entry["color_hex"],
            "geometry": geom,
        })
    return records


def write_qml(legend: list[dict]):
    categories, symbols = [], []
    for i, row in enumerate(legend):
        name = (row["name"].replace("&", "&amp;").replace('"', "&quot;")
                .replace("<", "&lt;").replace(">", "&gt;"))
        color = row["color_hex"].lstrip("#")
        rgb = ",".join(str(int(color[j:j+2], 16)) for j in (0, 2, 4)) + ",255"
        categories.append(
            f'      <category value="{name}" symbol="{i}" label="{name}" render="true"/>'
        )
        symbols.append(f'''      <symbol name="{i}" type="fill" alpha="1" clip_to_extent="1">
        <layer class="SimpleFill" enabled="1">
          <Option type="Map">
            <Option name="color" type="QString" value="{rgb}"/>
            <Option name="outline_style" type="QString" value="no"/>
            <Option name="style" type="QString" value="solid"/>
          </Option>
        </layer>
      </symbol>''')
    qml = f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34" styleCategories="Symbology">
  <renderer-v2 type="categorizedSymbol" attr="name" symbollevels="0" enableorderby="0">
    <categories>
{chr(10).join(categories)}
    </categories>
    <symbols>
{chr(10).join(symbols)}
    </symbols>
  </renderer-v2>
  <layerGeometryType>2</layerGeometryType>
</qgis>
'''
    QML.write_text(qml, encoding="utf-8")
    return qml


def embed_qgis_style(qml: str):
    with sqlite3.connect(OUT) as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS layer_styles (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          f_table_catalog TEXT,
          f_table_schema TEXT,
          f_table_name TEXT,
          f_geometry_column TEXT,
          styleName TEXT,
          styleQML TEXT,
          styleSLD TEXT,
          useAsDefault INTEGER,
          description TEXT,
          owner TEXT,
          ui TEXT,
          update_time DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        DELETE FROM layer_styles WHERE f_table_name = 'nigeria_geology';
        ''')
        conn.execute('''
          INSERT INTO layer_styles
          (f_table_catalog,f_table_schema,f_table_name,f_geometry_column,
           styleName,styleQML,styleSLD,useAsDefault,description,owner,ui)
          VALUES ('','','nigeria_geology','geom','Nigeria geology',?,'',1,
                  '86-category style transcribed from source map','','')
        ''', (qml,))
        conn.commit()


def main():
    legend = load_legend()
    seg = ensure_segmentation()
    labels_hi, pad, scale = smooth_labels(seg["labels"], seg["mask"], scale=3)
    transform = raster_transform(seg["frame"], pad, scale)

    boundary = gpd.read_file(BOUNDARY).to_crs(4326)
    nigeria = make_valid(union_all(boundary.geometry.values))
    records = polygonize(labels_hi, transform, nigeria, legend)

    gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
    # Equal-area measurements are useful QA/analysis attributes.
    equal_area = gdf.to_crs(6933)
    gdf["area_km2"] = equal_area.area / 1_000_000.0
    gdf["source"] = "Vectorized from supplied map image; boundary: Natural Earth 10m"
    gdf = gdf[["legend_id", "name", "color_hex", "area_km2", "source", "geometry"]]

    if OUT.exists():
        OUT.unlink()
    gdf.to_file(OUT, layer=LAYER, driver="GPKG", engine="pyogrio", spatial_index=True)
    qml = write_qml(legend)
    embed_qgis_style(qml)

    # Hard QA: 86 names, valid geometries, no duplicate categories, and no
    # uncovered country area beyond floating-point noise.
    reread = gpd.read_file(OUT, layer=LAYER)
    assert len(reread) == 86
    assert reread["name"].nunique() == 86
    assert reread.geometry.is_valid.all()
    covered = union_all(reread.geometry.values)
    missing = nigeria.difference(covered).area
    outside = covered.difference(nigeria).area
    overlap = float(sum(g.area for g in reread.geometry.values) - covered.area)
    if max(missing, outside, abs(overlap)) > 1e-7:
        raise RuntimeError(
            f"Coverage QA failed: missing={missing}, outside={outside}, overlap={overlap}"
        )
    print(f"Wrote {OUT.name}: {len(reread)} polygons/categories")
    print(f"Bounds: {tuple(round(x, 6) for x in reread.total_bounds)}")
    print(f"Coverage QA (square degrees): missing={missing:.3g}, outside={outside:.3g}, overlap={overlap:.3g}")
    print(f"Total equal-area coverage: {reread.area_km2.sum():,.1f} km2")


if __name__ == "__main__":
    main()
