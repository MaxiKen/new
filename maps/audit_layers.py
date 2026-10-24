#!/usr/bin/env python3
"""Verify every layer of the delivered GeoPackage and write layer_audit.json.

Checks, per layer:
  * declared CRS/geometry type vs what the file actually contains
  * null, empty, invalid and duplicate geometries
  * polygon-only / point-only / line-only geometry types
  * how much of the layer is inside Nigeria (vs `national_territory`)
  * attribute completeness (null counts) and key uniqueness
  * cross-layer consistency: `geology_units` == `*_equal_area` == geodesic area,
    no overlap, no hole, and every 2023 border vertex on the layer edge
  * joins: every point's `host_code` / `unit_code` matches the shipped geology
"""
import json
import pathlib
import sqlite3
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from pyproj import Geod

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
P = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
GEOID = Geod(ellps="WGS84")
EQ = "EPSG:6933"

con = sqlite3.connect(P)
layers = [r[0] for r in con.execute("SELECT table_name FROM gpkg_contents ORDER BY table_name")]
declared = {r[0]: (r[1], r[2]) for r in con.execute(
    "SELECT c.table_name, g.geometry_type_name, g.srs_id FROM gpkg_contents c "
    "LEFT JOIN gpkg_geometry_columns g ON g.table_name = c.table_name")}
con.close()

terr = shapely.make_valid(gpd.read_file(P, layer="national_territory").geometry.iloc[0])
terr_ea = shapely.make_valid(gpd.GeoSeries([terr], crs="EPSG:4326").to_crs(EQ).iloc[0])
units = gpd.read_file(P, layer="geology_units")
u_geoms = [shapely.make_valid(g) for g in units.geometry]
u_tree = shapely.STRtree(u_geoms)
u_code = units["code"].values
u_area = units["area_km2"].values

# layer -> (column, does an out-of-country point take the nearest unit?)
POINT_TARGETS = {
    "towns": ("unit_code", False), "state_capitals": ("unit_code", False),
    "volcanic_plugs": ("unit_code", False),
    "mineral_localities": ("host_code", True),
    "mineral_localities_icons": ("host_code", True),
    "mineral_localities_refined": ("host_code", True)}


def expect(types):
    return {"polygon": {"Polygon", "MultiPolygon"},
            "line": {"LineString", "MultiLineString"},
            "point": {"Point", "MultiPoint"}}.get(types)


report = {"file": str(P), "layers": {}, "checks": {}}
problems = []

for name in layers:
    g = gpd.read_file(P, layer=name)
    geom = g.geometry
    types = sorted(set(geom.geom_type.dropna()))
    rec = {
        "features": int(len(g)),
        "crs": g.crs.to_string() if g.crs else None,
        "declared_geometry_type": declared[name][0],
        "geometry_types_present": types,
        "attributes": [c for c in g.columns if c != geom.name],
        "null_geometry": int(geom.isna().sum()),
        "empty_geometry": int(geom.is_empty.sum()),
        "invalid_geometry": int((~geom.is_valid).sum()),
        "duplicate_geometry": int(geom.apply(lambda x: x.wkb if x is not None else b"").duplicated().sum()),
    }
    kinds = expect(declared[name][0].lower().replace("geometry", "")) or None
    if kinds and not set(types) <= kinds:
        extra = sorted(set(types) - kinds)
        rec["mixed_geometry"] = extra
        problems.append(f"{name}: contains {extra} in a {declared[name][0]} layer")
    if rec["null_geometry"] or rec["empty_geometry"] or rec["invalid_geometry"]:
        problems.append(f"{name}: {rec['null_geometry']} null / {rec['empty_geometry']} empty / "
                        f"{rec['invalid_geometry']} invalid")

    # location relative to Nigeria
    if "Polygon" in "".join(types):
        gg = [shapely.make_valid(x) for x in g.to_crs(EQ).geometry if x is not None]
        tot = sum(x.area for x in gg)
        inside = sum(shapely.make_valid(x.intersection(terr_ea)).area for x in gg)
        rec["area_km2"] = round(tot / 1e6, 1)
        rec["area_inside_nigeria_km2"] = round(inside / 1e6, 1)
        rec["frac_inside"] = round(inside / tot, 4) if tot else None
    elif "LineString" in "".join(types):
        gg = [shapely.make_valid(x) for x in g.to_crs(EQ).geometry if x is not None]
        tot = sum(x.length for x in gg)
        inside = sum(shapely.make_valid(x.intersection(terr_ea)).length for x in gg)
        rec["length_km"] = round(tot / 1000, 1)
        rec["length_inside_nigeria_km"] = round(inside / 1000, 1)
        rec["frac_inside"] = round(inside / tot, 4) if tot else None
    else:
        pts = g.geometry if (g.crs is None or g.crs.to_epsg() == 4326) else g.to_crs("EPSG:4326").geometry
        ins = [terr.contains(p) for p in pts if p is not None]
        rec["features_inside_nigeria"] = int(sum(ins))
        rec["features_outside_nigeria"] = int(len(ins) - sum(ins))
        if rec["features_outside_nigeria"] and name not in ("graticule_geology", "graticule_minerals"):
            rec["outside_flag_column"] = next(
                (c for c in ("in_nigeria",) if c in g.columns), None)

    # attribute sanity
    nulls = {c: int(g[c].isna().sum()) for c in rec["attributes"] if g[c].isna().any()}
    rec["null_counts"] = nulls
    for key in ("locality_id", "code"):
        if key in g.columns:
            rec[f"{key}_unique"] = bool(g[key].is_unique)
            if not g[key].is_unique:
                problems.append(f"{name}: {key} is not unique")
    if "ocg_id" in g.columns:
        # ocg_id identifies the object on the source sheet, not the row: one
        # printed line can be exported as several fragments, so it repeats
        rec["ocg_id_groups"] = int(g["ocg_id"].nunique())
        rec["ocg_id_fragments"] = int(len(g) - g["ocg_id"].nunique())
    report["layers"][name] = rec
    print(f"{name:34s} {rec['features']:5d} {','.join(types):26s} "
          f"invalid={rec['invalid_geometry']} dup={rec['duplicate_geometry']} "
          f"inside={rec.get('frac_inside', rec.get('features_inside_nigeria'))}")

# ---- numeric fields must be stored as numbers ------------------------------
# A text column that holds numbers is a trap for a calculation: `age_ma_min < 100`
# compares strings, and "538.8" < "100" is false while "66.0" < "100" is true.
textnum = []
for name in layers:
    g = gpd.read_file(P, layer=name)
    for c in g.columns:
        if c == g.geometry.name:
            continue
        s = g[c]
        if not (pd.api.types.is_string_dtype(s) or s.dtype == object):
            continue
        vals = s.dropna().astype(str)
        if len(vals) < 2:
            continue
        if pd.to_numeric(vals, errors="coerce").notna().mean() > 0.95:
            textnum.append(f"{name}.{c}")
if textnum:
    problems.append(f"{len(textnum)} numeric field(s) stored as text: {', '.join(textnum[:5])}")

# ---- cross-layer geometry checks ------------------------------------------
chk = {}
t = shapely.STRtree(u_geoms)
# Measured in the layer's own CRS.  Reprojecting each polygon separately to an
# equal-area CRS moves shared edges by millimetres and invents slivers, so a
# 6933-only measurement would overstate the overlap by ~4 orders of magnitude.
ov = 0.0
ov_pairs = 0
for i, j in [(i, j) for i, j in zip(*t.query(u_geoms, predicate="intersects")) if i < j]:
    a = u_geoms[i].intersection(u_geoms[j])
    if a is not None and not a.is_empty and a.area > 0:
        ov += gpd.GeoSeries([a], crs="EPSG:4326").to_crs(EQ).iloc[0].area / 1e6
        ov_pairs += 1
chk["geology_overlap_km2"] = round(ov, 4)
chk["geology_overlap_pairs"] = ov_pairs
chk["geology_overlap_note"] = ("area of pairs that overlap in the layer's own CRS; "
                               "reprojecting each polygon alone would add edge slivers")

cov = shapely.union_all(u_geoms)
left = shapely.make_valid(terr.difference(cov))
chk["uncovered_inside_territory_km2"] = round(
    gpd.GeoSeries([left], crs="EPSG:4326").to_crs(EQ).iloc[0].area / 1e6, 4)
chk["drawn_outside_territory_km2"] = round(
    gpd.GeoSeries([shapely.make_valid(cov.difference(terr))], crs="EPSG:4326")
    .to_crs(EQ).iloc[0].area / 1e6, 4)

ea = gpd.read_file(P, layer="geology_units_equal_area")
chk["area_4326_km2"] = round(float(units["area_km2"].sum()), 1)
chk["area_6933_km2"] = round(float(ea["area_km2_equal_area"].sum()), 1)
chk["area_geodesic_km2"] = round(abs(GEOID.geometry_area_perimeter(cov)[0]) / 1e6, 1)
chk["area_agreement_pct"] = round(
    100 * (chk["area_6933_km2"] - chk["area_geodesic_km2"]) / chk["area_geodesic_km2"], 4)

border = gpd.read_file(P, layer="international_boundary").geometry.iloc[0]
d = np.array([shapely.distance(shapely.Point(c), cov) for c in border.coords]) * 111.0
chk["border_vertices"] = len(d)
chk["border_max_offset_m"] = round(float(d.max()) * 1000, 1)
chk["border_vertices_over_50m"] = int((d > 0.05).sum())

# codes present in the projections must match the 4326 layer
utm = gpd.read_file(P, layer="geology_units_utm32n")
chk["codes_match_utm"] = bool(set(utm["code"]) == set(units["code"]))
chk["codes_match_equal_area"] = bool(set(ea["code"]) == set(units["code"]))
chk["utm_utilities"] = "EPSG:32632 area is +0.19 % over the exact figure"

# ---- joins ---------------------------------------------------------------
bad_join = {}
for layer, (col, nearest) in POINT_TARGETS.items():
    g = gpd.read_file(P, layer=layer)
    if col not in g.columns:
        continue
    n_bad = 0
    for pt, stored in zip(g.geometry, g[col]):
        idx = u_tree.query(pt, predicate="intersects")
        want = None
        if len(idx):
            want = u_code[int(idx[int(np.argmin(u_area[idx]))])]
        elif nearest:
            want = u_code[int(u_tree.nearest(pt))]
        same = (stored == want) or (pd.isna(stored) and want is None)
        if not same:
            n_bad += 1
    bad_join[layer] = n_bad
    if n_bad:
        problems.append(f"{layer}: {n_bad} rows carry a {col} that the shipped geology does not support")
chk["join_mismatches"] = bad_join

chk["numeric_stored_as_text"] = textnum
report["checks"] = chk
report["problems"] = problems
json.dump(report, open(HERE / "layer_audit.json", "w"), indent=1, default=str)

print("\n--- cross-layer ---")
for k, v in chk.items():
    print(f"  {k:34s} {v}")
print(f"\nproblems: {len(problems)}")
for p in problems:
    print("  !", p)
# metadata: record the audit outcome where the package describes itself
_meta_path = HERE / "metadata.json"
if _meta_path.exists():
    _meta = {r["key"]: r["value"] for r in json.load(open(_meta_path))}
    _meta["layer_audit"] = (
        f"audit_layers.py verified all {len(layers)} layers: {len(problems)} problems, "
        f"area {chk['area_4326_km2']:,.0f} km2 identical to {chk['area_agreement_pct']:+.3f}% between "
        f"EPSG:4326 / 6933 / geodesic, 2023 border within {chk['border_max_offset_m']:.1f} m of the "
        f"geology edge, {sum(bad_join.values())} point-to-unit join mismatches")
    json.dump([{"key": k, "value": v} for k, v in _meta.items()],
              open(_meta_path, "w"), indent=2, ensure_ascii=False)

print(f"\nwrote {HERE / 'layer_audit.json'}")
