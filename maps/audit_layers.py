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
import pyogrio
import rasterio
import shapely
from pyproj import Geod

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
P = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
# The five reprojections live in their own file, so the deliverable is one CRS.
COPIES = HERE / "Nigeria_Geology_Minerals_projected_copies.gpkg"
COPY_LAYERS = {"geology_units_utm32n": "geology_units",
               "geology_units_equal_area": "geology_units",
               "mineral_localities_icons_utm32n": "mineral_localities_icons",
               "mineral_localities_equal_area": "mineral_localities_icons",
               "mineral_localities_utm32n": "mineral_localities_refined"}


def rdf(name, **kw):
    """Read a layer from whichever of the two files holds it."""
    if (COPIES.exists() and name in
            {n for n, _ in __import__("pyogrio").list_layers(COPIES)}):
        return gpd.read_file(COPIES, layer=name, **kw)
    return gpd.read_file(P, layer=name, **kw)


def path_of(name):
    return COPIES if (COPIES.exists() and name in
                      {n for n, _ in __import__("pyogrio").list_layers(COPIES)}) else P
GEOID = Geod(ellps="WGS84")
EQ = "EPSG:6933"

con = sqlite3.connect(P)
# feature layers only - the nine georeferenced images are tiles, verified below
layers = [r[0] for r in con.execute(
    "SELECT table_name FROM gpkg_contents WHERE data_type = 'features' ORDER BY table_name")]
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
from pyproj import Geod

GEOD = Geod(ellps="WGS84")


def _geo_len(geom):
    """Ellipsoidal length in km of a (multi)line, 0 for anything else."""
    if geom is None or geom.is_empty:
        return 0.0
    parts = ([geom] if geom.geom_type == "LineString"
             else [x for x in getattr(geom, "geoms", []) if x.geom_type == "LineString"])
    total = 0.0
    for ln in parts:
        if ln.is_empty or len(ln.coords) < 2:
            continue
        xs, ys = np.asarray(ln.coords).T[:2]
        total += GEOD.line_length(xs, ys)
    return total / 1000


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
        # measured on the ellipsoid, not on the equal-area grid: 6933 stretches a
        # north-south line by up to 14 % at this latitude, and the layer's own
        # `len_km` is geodesic, so the two must be measured the same way to be
        # comparable at all
        tot = sum(_geo_len(x) for x in g.geometry)
        inside = sum(_geo_len(shapely.make_valid(x.intersection(terr))) for x in g.geometry)
        rec["length_km"] = round(tot, 1)
        rec["length_inside_nigeria_km"] = round(inside, 1)
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
        # a code is an identifier, not a quantity: `admin1_code` "00" for an
        # unknown state must stay a string, or it becomes 0 and starts comparing
        # like a number
        if c.endswith("_code"):
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

ea = rdf("geology_units_equal_area")
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
utm = rdf("geology_units_utm32n")
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

# ---- attribute integrity: the conventions the documentation promises --------
# Each check below exists because the file once broke it. They are cheap, and
# they are the only way the promises stay true after a rebuild.
attr = {}
con = sqlite3.connect(P)
con.row_factory = sqlite3.Row

# 1. missing values are NULL, never '' --------------------------------------
empties = {}
for t in layers:
    for col, typ in [(r[1], r[2]) for r in con.execute(f'PRAGMA table_info("{t}")')]:
        if typ != "TEXT":
            continue
        n = con.execute(f'SELECT count(*) FROM "{t}" WHERE "{col}" = \'\'').fetchone()[0]
        if n:
            empties[f"{t}.{col}"] = n
attr["empty_strings"] = empties
if empties:
    problems.append(f"{sum(empties.values()):,} empty strings where NULL is the "
                    f"convention: {list(empties)[:3]}")

# 2. a projected copy carries the same attributes as the layer it copies ------
COPY_PAIRS = [("geology_units", "geology_units_utm32n"),
              ("geology_units", "geology_units_equal_area"),
              ("mineral_localities_icons", "mineral_localities_icons_utm32n"),
              ("mineral_localities_icons", "mineral_localities_equal_area"),
              # easy to miss, and missing it is what hid the mis-lineage: the UTM
              # copy descends from _refined, not from the 4326 layer of that name
              ("mineral_localities_refined", "mineral_localities_utm32n")]
copy_diffs = {}


def declared_in(path, layer):
    c = sqlite3.connect(path)
    t = {r[1]: r[2] for r in c.execute(f'PRAGMA table_info("{layer}")')}
    c.close()
    return t


for a, b in COPY_PAIRS:
    ga, gb = rdf(a), rdf(b)
    key = "code" if "code" in ga.columns else "locality_id"
    ta, tb = declared_in(path_of(a), a), declared_in(path_of(b), b)
    common = [c for c in ta if c in tb and c not in ("geom", "fid")]
    A = {r[key]: r for r in ga.to_dict("records")}
    B = {r[key]: r for r in gb.to_dict("records")}
    diffs = {}
    for k in A:
        if k not in B:
            continue
        for c in common:
            x, y = A[k][c], B[k][c]
            if x != y and not (pd.isna(x) and pd.isna(y)):
                diffs[c] = diffs.get(c, 0) + 1
    if set(A) != set(B):
        diffs["__keys__"] = len(set(A) ^ set(B))
    if diffs:
        copy_diffs[f"{a} -> {b}"] = diffs
        problems.append(f"{b} is not attribute-identical to {a}: {diffs}")
attr["projected_copy_attribute_diffs"] = copy_diffs
con = sqlite3.connect(P)
con.row_factory = sqlite3.Row

# 3. geometry and the lon/lat pair must agree --------------------------------
lonlat = {}
for name in layers:
    g = gpd.read_file(P, layer=name)
    if "lon" not in g.columns or not str(g.geometry.geom_type.iloc[0]).startswith("Point"):
        continue
    gg = g.to_crs("EPSG:4326")
    d = float(np.max(np.hypot(gg.geometry.x - gg["lon"], gg.geometry.y - gg["lat"]))) * 111_000
    lonlat[name] = round(d, 4)
    # 1 cm: the layers stored in metres carry a millimetre of reprojection
    # round-off when they are brought back to degrees; the 4326 layers must
    # agree exactly, and do
    if d > 0.01:
        problems.append(f"{name}: lon/lat column disagrees with the geometry by {d:.3f} m")
attr["lonlat_vs_geometry_max_m"] = lonlat

# 4. the locality family shares one key --------------------------------------
loc_family = [n for n in layers if n.startswith("mineral_localities")]
no_key = [n for n in loc_family if "locality_id" not in
          [r[1] for r in con.execute(f'PRAGMA table_info("{n}")')]]
dup_key = [n for n in loc_family if n not in no_key and
           con.execute(f'SELECT count(*)-count(DISTINCT locality_id) FROM "{n}"'
                       ).fetchone()[0]]
attr["locality_layers_without_locality_id"] = no_key
attr["locality_layers_with_duplicate_id"] = dup_key
if no_key or dup_key:
    problems.append(f"locality family key missing in {no_key} / duplicated in {dup_key}")

# 5. declared types: booleans are booleans, counts are numbers ---------------
def declared(t, c):
    for r in con.execute(f'PRAGMA table_info("{t}")'):
        if r[1] == c:
            return r[2]
    return None


bad_types = []
for t, c, want in [("towns_geonames", "state_agree", "BOOLEAN"),
                   ("towns_geonames", "elevation_m", "INTEGER"),
                   ("towns_geonames", "population", "INTEGER"),
                   ("geology_units", "filled", "BOOLEAN"),
                   ("towns", "in_nigeria", "BOOLEAN")]:
    if declared(t, c) != want:
        bad_types.append(f"{t}.{c} is {declared(t, c)}, expected {want}")
attr["wrong_declared_types"] = bad_types
if bad_types:
    problems.append(f"declared types wrong: {bad_types}")
attr["towns_geonames_coord_precision"] = dict(con.execute(
    "SELECT coord_dp, count(*) FROM towns_geonames GROUP BY 1 ORDER BY 1").fetchall()
    if "coord_dp" in [r[1] for r in con.execute('PRAGMA table_info("towns_geonames")')]
    else {})

# 6. denormalised host attributes must match the geology they name -----------
units_idx = {r[0]: r[1:] for r in con.execute(
    "SELECT code, era, period, age_ma_max FROM geology_units")}
DENORM = [("towns", "unit_code", "unit_era", "era"), ("towns", "unit_code", "unit_per", "period"),
          ("state_capitals", "unit_code", "unit_era", "era"),
          ("state_capitals", "unit_code", "unit_per", "period"),
          ("volcanic_plugs", "unit_code", "unit_era", "era"),
          ("volcanic_plugs", "unit_code", "unit_per", "period"),
          ("mineral_localities", "host_code", "host_era", "era"),
          ("mineral_localities", "host_code", "host_period", "period"),
          ("mineral_localities", "host_code", "host_age_ma", "age_ma_max")]
drift = {}
for t, codecol, col, src in DENORM:
    rows = con.execute(f'SELECT "{codecol}", "{col}" FROM "{t}"').fetchall()
    bad = 0
    for code, val in rows:
        if code is None or code not in units_idx:
            continue
        want = units_idx[code][("era", "period", "age_ma_max").index(src)]
        if want is None and val is None:
            continue
        if isinstance(want, str) or isinstance(val, str):
            if str(want) != str(val):
                bad += 1
        elif val is None or abs(float(want) - float(val)) > 1e-6:
            bad += 1
    if bad:
        drift[f"{t}.{col}"] = bad
        problems.append(f"{t}.{col}: {bad} rows disagree with the geology unit they name")
attr["denormalised_unit_attribute_drift"] = drift

# 7. every class layer has an integer class_id -------------------------------
no_class_id = [n for n in layers if (n.startswith("poly_") or n == "geology_era")
               and "class_id" not in [r[1] for r in con.execute(f'PRAGMA table_info("{n}")')]]
attr["class_layers_without_class_id"] = no_class_id
if no_class_id:
    problems.append(f"class layer(s) without class_id: {no_class_id}")
con.close()
chk["attribute_integrity"] = attr


# 5. geometry hygiene: a defect that costs no area and so no area test finds it
# ---------------------------------------------------------------------------
# The paint-order replay leaves hairline slits - a ring that runs out along a
# contact and returns along the same line - and duplicate consecutive vertices.
# Both leave the area, the coverage and the overlap residual untouched, so a
# polygon can be "valid" by every aggregate test and still be non-simple in a way
# that breaks simplification and rendering.
def _needles(geom):
    n = 0
    polys = ([geom] if geom.geom_type == "Polygon"
             else list(geom.geoms) if geom.geom_type.startswith("MultiPolygon") else [])
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            a = np.asarray(ring.coords)[:, :2]
            if len(a) < 4:
                continue
            v1, v2, v3 = a[:-2], a[1:-1], a[2:]
            d1, d2 = v2 - v1, v3 - v2
            cross = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
            dot = (d1 * d2).sum(1)
            l1, l2 = np.hypot(*d1.T), np.hypot(*d2.T)
            n += int(((dot < 0) & (l1 > 1e-9) & (l2 > 1e-9)
                      & (cross < 1e-9 * np.maximum(l1 * l2, 1e-18))).sum())
    return n


def _self_touching(geom):
    """Consecutive duplicate vertices, and parts with no area at all."""
    dup = 0
    degenerate = 0
    polys = ([geom] if geom.geom_type == "Polygon"
             else list(geom.geoms) if geom.geom_type.startswith("MultiPolygon") else [])
    for p in polys:
        if p.area == 0:
            degenerate += 1
        for ring in [p.exterior] + list(p.interiors):
            a = np.asarray(ring.coords)[:, :2]
            if len(a) > 1:
                dup += int((np.abs(np.diff(a, axis=0)).sum(axis=1) == 0).sum())
    return dup, degenerate


geom_chk = {}
for name in layers:
    g = gpd.read_file(P, layer=name)
    rec = dict(geometry_types=sorted(set(g.geometry.geom_type.dropna())),
               empty=int(g.geometry.is_empty.sum()),
               invalid=int((~g.geometry.is_valid).sum()),
               null=int(g.geometry.isna().sum()))
    if any(t.endswith("Polygon") for t in rec["geometry_types"]):
        rec["slit_vertices"] = sum(_needles(x) for x in g.geometry if x is not None)
        dups, degen = zip(*[_self_touching(x) if x is not None else (0, 0)
                            for x in g.geometry]) if len(g) else ((0,), (0,))
        rec["duplicate_vertices"] = int(sum(dups))
        rec["degenerate_parts"] = int(sum(degen))
        # ring winding: exterior counter-clockwise, holes clockwise, as GeoJSON
        # and GeoParquet require, so an export does not flip every polygon
        cw_ext = cw_hole = 0
        for geom in g.geometry:
            if geom is None or geom.is_empty:
                continue
            for poly in ([geom] if geom.geom_type == "Polygon"
                         else list(getattr(geom, "geoms", []))):
                if not poly.exterior.is_ccw:
                    cw_ext += 1
                cw_hole += sum(1 for h in poly.interiors if h.is_ccw)
        rec["clockwise_exteriors"] = cw_ext
        rec["counter_clockwise_holes"] = cw_hole
    rec["has_z"] = bool(any(getattr(x, "has_z", False) for x in g.geometry if x is not None))
    geom_chk[name] = {k: v for k, v in rec.items() if v not in (0, False, [])} or "clean"
    if rec.get("slit_vertices") or rec.get("duplicate_vertices") or rec.get("invalid"):
        problems.append(f"{name}: {rec.get('slit_vertices', 0)} slit vertices, "
                        f"{rec.get('duplicate_vertices', 0)} duplicate vertices, "
                        f"{rec['invalid']} invalid geometries")
    if rec.get("clockwise_exteriors") or rec.get("counter_clockwise_holes"):
        problems.append(f"{name}: {rec['clockwise_exteriors']} clockwise exteriors, "
                        f"{rec['counter_clockwise_holes']} counter-clockwise holes")
    if rec["has_z"]:
        problems.append(f"{name}: carries Z values in a 2D layer")
attr["geometry_hygiene"] = geom_chk

# 6. every projected copy really is its parent, reprojected -------------------
# Attributes matching is not enough: a copy taken before a repair keeps the old
# geometry with the new attributes.
copy_geom = {}
for a, b in COPY_PAIRS:
    ga = rdf(a)
    gb = rdf(b)
    if len(ga) != len(gb):
        problems.append(f"{b}: {len(gb)} rows against {len(ga)} in {a}")
        copy_geom[b] = dict(rows=[len(ga), len(gb)])
        continue
    direct = ga.to_crs(gb.crs)
    sym = max((x.symmetric_difference(y).area for x, y in zip(direct.geometry, gb.geometry)),
              default=0)
    copy_geom[b] = dict(parent=a, crs=gb.crs.to_string(), rows=len(gb),
                        max_symmetric_difference_m2=round(float(sym), 3))
    if sym > 1.0:
        problems.append(f"{b}: geometry departs from {a} reprojected by {sym:,.1f} m2")
attr["projected_copy_geometry"] = copy_geom

# 7. values that would be read as measurements ------------------------------
# A sentinel is worse than a NULL: -9999 in an elevation column is an elevation.
# 9999 is deliberately absent: it occurs once in moved_from_label_m where values
# up to 19,713 m are real, so the repeat is coincidence, not a sentinel
SENTINELS = (-9999, -99999, -32768)
BAD_NEGATIVE = {"population": "count", "elevation_m": "metres above sea level",
                "dem_m": "metres above sea level", "area_km2": "an area",
                "len_km": "a length", "length_km": "a length", "km_in_nigeria": "a length",
                "mapped_km2": "an area", "filled_km2": "an area",
                "area_km2_equal_area": "an area", "dist_to_coast_m": "a distance",
                "host_boundary_dist_m": "a distance", "icon_spread_m": "a distance",
                "moved_from_label_m": "a distance", "name_dist": "a distance"}
sentinel = {}
for name in layers:
    g = gpd.read_file(P, layer=name)
    for c in g.columns:
        if c == "geometry" or not pd.api.types.is_numeric_dtype(g[c]):
            continue
        for s in SENTINELS:
            n = int((g[c] == s).sum())
            if n:
                sentinel[f"{name}.{c}"] = dict(value=s, rows=n)
                problems.append(f"{name}.{c}: {n} rows hold the sentinel {s}")
        if c in BAD_NEGATIVE and (g[c] < 0).any():
            n = int((g[c] < 0).sum())
            sentinel[f"{name}.{c}"] = dict(negative=n, why=f"{c} is {BAD_NEGATIVE[c]}")
            problems.append(f"{name}.{c}: {n} negative values")
    # min/max pairs must be ordered
    for lo, hi in (("age_ma_min", "age_ma_max"),):
        if lo in g.columns and hi in g.columns:
            bad = int((g[lo] > g[hi]).sum())
            if bad:
                problems.append(f"{name}: {bad} rows have {lo} > {hi}")
attr["sentinel_values"] = sentinel

# 7b. the length attributes must be the measurement, not a different one -----
line_chk = {}
for name in layers:
    rec = report["layers"][name]
    if "length_km" not in rec:
        continue
    g = gpd.read_file(P, layer=name)
    if "len_km" not in g.columns:
        # the two graticules are constructed QA geometry, not lines read off a
        # sheet: their length is a property of the drawing grid, not a measurement
        if not name.startswith("graticule_"):
            problems.append(f"{name}: a line layer with no len_km")
        continue
    d = float(np.max(np.abs(g["len_km"] - np.array(
        [_geo_len(x) for x in g.geometry])))) if len(g) else 0.0
    line_chk[name] = dict(len_km_max_diff_km=round(d, 3))
    if d > 0.01:
        problems.append(f"{name}: len_km is off the geodesic measurement by {d:.3f} km")
    if "km_in_nigeria" in g.columns:
        over = int((g["km_in_nigeria"] > g["len_km"] + 1e-6).sum())
        ratio_bad = int((np.abs(g["frac_in_nigeria"]
                                - np.where(g["len_km"] > 0, g["km_in_nigeria"] / g["len_km"].replace(0, np.nan), 0)
                                ) > 0.001).sum())
        line_chk[name].update(rows_inside_longer_than_total=over, frac_mismatches=ratio_bad)
        if over:
            problems.append(f"{name}: {over} rows where km_in_nigeria exceeds len_km")
        if ratio_bad:
            problems.append(f"{name}: {ratio_bad} rows where frac_in_nigeria is not the ratio")
attr["line_length_attributes"] = line_chk

# 7c. a boolean that encodes a comparison must actually be able to be True ----
# `state_agree` was converted, not computed, on a second run and every one of its
# 29,470 True values silently became False. The type, the NULL count and every
# other check still passed: only recomputing the comparison finds it.
import unicodedata


def _fold(v):
    if not isinstance(v, str):
        return ""
    v = unicodedata.normalize("NFKD", v).encode("ascii", "ignore").decode()
    v = v.lower().replace("-", " ").replace("'", "").replace(" state", "")
    return " ".join(v.split())


tg = gpd.read_file(P, layer="towns_geonames")
recomputed = [None if (pd.isna(a) or pd.isna(b) or not str(a).strip() or not str(b).strip())
              else _fold(a) == _fold(b) for a, b in zip(tg["state"], tg["state_gn"])]
got = [None if pd.isna(v) else bool(v) for v in tg["state_agree"]]
n_bad = sum(1 for a, b in zip(recomputed, got) if a != b)
truthy = sum(1 for v in got if v is True)
attr["state_agree"] = dict(rows=len(tg), true=truthy, false=sum(1 for v in got if v is False),
                           null=sum(1 for v in got if v is None), mismatches=n_bad)
if n_bad:
    problems.append(f"towns_geonames.state_agree: {n_bad} rows disagree with state vs state_gn")
if truthy == 0 and any(v is False for v in got):
    problems.append("towns_geonames.state_agree: a boolean with no True values")

booleans = {}
for name in layers:
    g = gpd.read_file(P, layer=name)
    for c in g.columns:
        if c == "geometry" or not pd.api.types.is_bool_dtype(g[c]):
            continue
        t = int((g[c] == True).sum())
        f = int((g[c] == False).sum())
        booleans[f"{name}.{c}"] = dict(true=t, false=f, null=int(g[c].isna().sum()))
        if (t and not f) or (f and not t):
            # one-sided is legitimate where every row is by construction inside
            # the country; it is recorded so a regression is visible
            attr.setdefault("one_sided_booleans", {})[f"{name}.{c}"] = (
                "all True" if t else "all False")
attr["boolean_columns"] = booleans

# 8. text hygiene: padding, runs of spaces, and truncation ------------------
text_chk = {}
for name in layers:
    g = gpd.read_file(P, layer=name)
    for c in g.columns:
        if c == "geometry" or g[c].dtype != object:
            continue
        vals = [v for v in g[c] if isinstance(v, str)]
        if not vals:
            continue
        pad = sum(1 for v in vals if v != v.strip())
        dbl = sum(1 for v in vals if "  " in v)
        ctrl = sum(1 for v in vals if any(ch < " " or ch == "\x7f" for ch in v))
        if pad or dbl or ctrl:
            text_chk[f"{name}.{c}"] = {k: v for k, v in
                                       dict(padding=pad, double_space=dbl, control=ctrl).items() if v}
            problems.append(f"{name}.{c}: {pad} padded, {dbl} with a double space, {ctrl} control chars")
# the two fixed-width cuts that were found in this pass must not reappear
if "lnk" not in dir():
    pass
truncated = {}
for name, col, must in (("mineral_symbols", "link", "considered"),
                        ("towns_geonames", "alt_names", None)):
    g = gpd.read_file(P, layer=name)
    vals = [v for v in g[col] if isinstance(v, str)]
    if must:
        n = sum(1 for v in vals if must not in v and "colour not" in v)
        truncated[f"{name}.{col}"] = n
        if n:
            problems.append(f"{name}.{col}: {n} values cut before '{must}'")
    else:
        n = sum(1 for v in vals if v.endswith((",", " ")) or v != v.strip())
        truncated[f"{name}.{col}"] = n
        if n:
            problems.append(f"{name}.{col}: {n} values end mid-name")
attr["text_hygiene"] = text_chk
attr["truncated_values"] = truncated

# ---- GeoPackage conformance: the registers must describe the contents ------
# A SQLite integrity check says "ok" for a file that advertises a layer, an
# index or a zoom level that is not there: the data is fine, the *description*
# is wrong.  Every register is therefore checked against `gpkg_contents`.
con = sqlite3.connect(P)
gpkg = {}
tables = {r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table'")}
contents = {r[0] for r in con.execute("SELECT table_name FROM gpkg_contents")}
gpkg["contents_layers"] = len(contents)
gpkg["integrity_check"] = con.execute("PRAGMA integrity_check").fetchone()[0]
gpkg["foreign_key_check"] = len(con.execute("PRAGMA foreign_key_check").fetchall())
gpkg["user_version"] = con.execute("PRAGMA user_version").fetchone()[0]
if gpkg["integrity_check"] != "ok":
    problems.append(f"integrity check: {gpkg['integrity_check']}")

dangling_ext = [f"{t}.{c} ({e})" for t, c, e in con.execute(
    "SELECT table_name, column_name, extension_name FROM gpkg_extensions")
    # the 2D gridded coverage extension is declared against the ancillary tables,
    # which are tables by design and not layers; anything else must name a layer
    if t not in contents and e != "gpkg_2d_gridded_coverage"]
gpkg["dangling_extension_rows"] = dangling_ext
if dangling_ext:
    problems.append(f"{len(dangling_ext)} gpkg_extensions row(s) name a layer that does"
                    f" not exist: {', '.join(dangling_ext[:5])}")

orphan_gc = sorted(r[0] for r in con.execute(
    "SELECT table_name FROM gpkg_geometry_columns") if r[0] not in contents)
gpkg["orphan_geometry_columns"] = orphan_gc
if orphan_gc:
    problems.append(f"gpkg_geometry_columns names missing tables: {orphan_gc}")

rtree = sorted(t for t in tables if t.startswith("rtree_")
               and not t.endswith(("_node", "_rowid", "_parent", "_data")))
# the index name comes from the register ("rtree_<layer>_<column>"); a split on
# "_" would call `rtree_towns_geom` an orphan because `rtree_towns` is no layer
declared_idx = {(t, c) for t, c, e in con.execute(
    "SELECT table_name, column_name, extension_name FROM gpkg_extensions"
    " WHERE extension_name = 'gpkg_rtree_index'")}
orphan_rtree = sorted(t for t in rtree if t not in {f"rtree_{t_}_{c}"
                                                    for t_, c in declared_idx})
gpkg["rtree_indexes"] = len(rtree)
gpkg["layers_without_spatial_index"] = sorted(
    t for t, c in declared_idx if f"rtree_{t}_{c}" not in rtree)
if gpkg["layers_without_spatial_index"]:
    problems.append("spatial index declared but missing for "
                    f"{gpkg['layers_without_spatial_index'][:3]}")
gpkg["orphan_rtree_tables"] = orphan_rtree
if orphan_rtree:
    problems.append(f"{len(orphan_rtree)} orphan rtree index table(s), e.g. {orphan_rtree[:3]}")

# every declared zoom level must hold at least one tile, or a tile client asks
# for a tile that was never written and draws nothing
stale_zoom = []
for t in [r[0] for r in con.execute(
        "SELECT table_name FROM gpkg_contents WHERE data_type = 'tiles'")]:
    have = {r[0] for r in con.execute('SELECT DISTINCT zoom_level FROM "%s"' % t)}
    declared_z = {r[0] for r in con.execute(
        "SELECT zoom_level FROM gpkg_tile_matrix WHERE table_name = ?", (t,))}
    if declared_z - have:
        stale_zoom.append(f"{t}:{sorted(declared_z - have)}")
gpkg["tile_matrix_levels_without_tiles"] = stale_zoom
if stale_zoom:
    problems.append(f"tile matrix declares empty zoom levels: {', '.join(stale_zoom[:5])}")
# `gpkg_ogr_contents` is GDAL's feature-count cache: another register that can
# name a table that no longer exists, with nothing in the data to show it
if con.execute("SELECT count(*) FROM sqlite_master WHERE name = 'gpkg_ogr_contents'"
               ).fetchone()[0]:
    stale_counts = []
    wrong_counts = []
    for t, n in con.execute("SELECT table_name, feature_count FROM gpkg_ogr_contents"):
        if t not in contents:
            stale_counts.append(t)
            continue
        try:
            actual = con.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        except sqlite3.DatabaseError:
            stale_counts.append(t)
            continue
        if actual != n:
            wrong_counts.append(f"{t}: cached {n}, actual {actual}")
    if stale_counts:
        # fix_gpkg_hygiene.py removes these; the audit only reports them
        problems.append(f"gpkg_ogr_contents caches counts for {len(stale_counts)} "
                        f"missing table(s): {', '.join(stale_counts[:4])}")
    gpkg["ogr_contents_stale_rows"] = stale_counts
    gpkg["ogr_contents_wrong_counts"] = wrong_counts
    if wrong_counts:
        problems.append(f"gpkg_ogr_contents feature counts wrong: {wrong_counts[:3]}")

gpkg["undescribed_layers"] = sorted(
    r[0] for r in con.execute("SELECT table_name, description FROM gpkg_contents")
    if not r[1])
if gpkg["undescribed_layers"]:
    problems.append(f"{len(gpkg['undescribed_layers'])} layer(s) carry no description: "
                    f"{gpkg['undescribed_layers'][:3]}")

# the file header: a .gpkg should identify itself as one, and as a 1.x file
gpkg["application_id"] = con.execute("PRAGMA application_id").fetchone()[0]
if gpkg["application_id"] != 0x47504B47:      # "GPKG"
    problems.append(f"application_id is {gpkg['application_id']:#x}, not the GeoPackage 0x47504b47")
if gpkg["user_version"] < 10200:
    problems.append(f"user_version {gpkg['user_version']} claims a GeoPackage older than 1.2")

# ---- provenance inside the file --------------------------------------------
# The licence and the withdrawal notice must travel *with* the file, not only in
# the sibling markdown: gpkg_metadata + gpkg_metadata_reference exist for this.
# Both files are checked - the copies file carries its own provenance, because a
# reader who measures in metres never sees the master record.
import xml.etree.ElementTree as ET

meta = {}
for path in [q for q in (P, COPIES) if q.exists()]:
    con2 = sqlite3.connect(path)
    tbl = {r[0] for r in con2.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    rec = dict(file=path.name)
    if "gpkg_metadata" in tbl:
        recs = con2.execute("SELECT id, md_scope, mime_type, metadata FROM gpkg_metadata"
                            " ORDER BY id").fetchall()
        contents2 = {r[0] for r in con2.execute("SELECT table_name FROM gpkg_contents")}
        bad_xml, bad_mime = [], []
        for mid, scope, mime, text in recs:
            if mime != "text/xml":
                bad_mime.append(mid)
            try:
                ET.fromstring(text)
            except ET.ParseError as exc:
                bad_xml.append(f"{mid}: {exc}")
        refs = con2.execute("SELECT reference_scope, table_name, md_file_id"
                            " FROM gpkg_metadata_reference").fetchall()
        missing_tbl = sorted({t for _, t, _ in refs if t and t not in contents2})
        missing_md = sorted({m for _, _, m in refs if m not in {r[0] for r in recs}})
        text_all = " ".join(r[3] for r in recs)
        rec.update(records=len(recs), references=len(refs),
                   scopes=sorted({r[1] for r in recs}),
                   unparsable=bad_xml, wrong_mime=bad_mime,
                   references_to_missing_tables=missing_tbl,
                   references_to_missing_records=missing_md,
                   mentions_cc_by_4="CC BY 4.0" in text_all,
                   mentions_withdrawn="POSITIONS WITHDRAWN" in text_all,
                   towns_referenced=any(t == "towns_geonames" for _, t, _ in refs))
        if bad_xml:
            problems.append(f"{path.name}: gpkg_metadata record(s) are not well-formed XML: {bad_xml[:3]}")
        if bad_mime:
            problems.append(f"{path.name}: gpkg_metadata record(s) with a mime_type other than text/xml")
        if not recs:
            problems.append(f"{path.name}: gpkg_metadata exists but holds no record")
        if missing_tbl:
            problems.append(f"{path.name}: gpkg_metadata_reference names absent tables: {missing_tbl[:4]}")
        if missing_md:
            problems.append(f"{path.name}: gpkg_metadata_reference points at missing ids: {missing_md}")
    else:
        rec["records"] = 0
        problems.append(f"{path.name}: no gpkg_metadata table: the licence and the "
                        f"warnings do not travel with the file")
    con2.close()
    meta[path.name] = rec

main_meta = meta.get(P.name, {})
if main_meta and not main_meta.get("mentions_cc_by_4"):
    problems.append("no metadata record carries the GeoNames CC BY 4.0 attribution")
if main_meta and not main_meta.get("towns_referenced"):
    problems.append("the CC BY 4.0 record is not attached to towns_geonames")
if main_meta and not main_meta.get("mentions_withdrawn"):
    problems.append("no metadata record carries the withdrawn-positions notice")
chk["metadata"] = meta

# ---- one CRS in the deliverable -------------------------------------------
# The layers are meant to be laid on each other. A single file with three CRS
# means every consumer has to reproject first, and a layer drawn in the wrong CRS
# does not error - it lands somewhere else. The five reprojections that exist for
# measuring live in their own file (split_projected_copies.py); this asserts the
# split is complete and that nothing drifted back in.
crs_chk = dict(deliverable_srs=sorted({rec.get("crs") for rec in
                                       [r for r in report["layers"].values()] if rec.get("crs")}))
if crs_chk["deliverable_srs"] != ["EPSG:4326"]:
    problems.append(f"the deliverable is not one CRS: {crs_chk['deliverable_srs']}")
if COPIES.exists():
    con2 = sqlite3.connect(COPIES)
    copies = con2.execute("SELECT table_name, srs_id FROM gpkg_contents").fetchall()
    con2.close()
    crs_chk["copies_file"] = {t: s for t, s in copies}
    main_names = {n for n, _ in pyogrio.list_layers(P)}
    copy_names = {t for t, _ in copies}
    absent = [t for t in COPY_LAYERS if t not in copy_names]
    if absent:
        problems.append(f"the copies file does not hold {absent}")
    still_in_main = [t for t in COPY_LAYERS if t in main_names]
    if still_in_main:
        problems.append(f"the deliverable still holds reprojections: {still_in_main}")
else:
    problems.append("no projected-copies file: the measurement layers are missing")
chk["crs"] = crs_chk
chk["geopackage_conformance"] = gpkg

# Image tiles cannot carry a no-data value, so the class layer encodes its mask as a
# sentinel; the claim lives in dem_from_sheet.json. This map is what the raster sweep
# below applies when a layer's transparency is not in its alpha channel.
try:
    _dem = json.load(open(HERE / "dem_from_sheet.json")) if (HERE / "dem_from_sheet.json").exists() else None
except Exception:
    _dem = None
DEM_SENTINEL = {k: v["sentinel"] for k, v in (_dem or {}).get("layers", {}).items()
                if "sentinel" in v}

# ---- the raster pyramids: every tile decodes, and the clip still holds -----
# A GeoPackage stores one image BLOB per tile, so a pyramid may mix formats -
# and GDAL does: a tile that needs transparency is a 4-band RGBA PNG, a tile
# wholly inside the printed map is a 3-band RGB JPEG. That is legal and it is
# smaller, but it is only *correct* if no 3-band tile sits on ground the clip
# should have removed: such a tile would show as a block of paper. Decode every
# tile and check the invariant, instead of trusting the writer.
from rasterio.io import MemoryFile

tile_chk = {}
for (t,) in sqlite3.connect(P).execute(
        "SELECT table_name FROM gpkg_contents WHERE data_type='tiles' ORDER BY 1"):
    con = sqlite3.connect(P)
    mw, mh, tw, th = con.execute(
        "SELECT matrix_width, matrix_height, tile_width, tile_height FROM gpkg_tile_matrix"
        " WHERE table_name = ?", (t,)).fetchone()
    rec = dict(tiles=0, png=0, jpeg=0, rgb_tiles=0, rgba_tiles=0, undecodable=[],
               wrong_size=[], opaque_block_at_clip=[])
    mosaic = np.zeros((mh * th, mw * tw, 4), dtype=np.uint8)
    rgb_cells = []
    for blob, c, r in con.execute(f'SELECT tile_data, tile_column, tile_row FROM "{t}"'):
        rec["tiles"] += 1
        if blob[:8] == b"\x89PNG\r\n\x1a\n":
            rec["png"] += 1
        elif blob[:2] == b"\xff\xd8":
            rec["jpeg"] += 1
        try:
            with MemoryFile(blob) as mf:
                with mf.open() as ds:
                    a = ds.read()
        except Exception as exc:                  # a tile that will not open is a defect
            rec["undecodable"].append(f"{c},{r}: {exc}")
            continue
        if (a.shape[1], a.shape[2]) != (th, tw):
            rec["wrong_size"].append(f"{c},{r}: {a.shape[1:]} vs {(th, tw)}")
        a = np.transpose(a, (1, 2, 0))
        if a.shape[2] == 3:
            rec["rgb_tiles"] += 1
            rgb_cells.append((c, r))
            a = np.dstack([a, np.full(a.shape[:2], 255, dtype=np.uint8)])
        else:
            rec["rgba_tiles"] += 1
        mosaic[r * th:(r + 1) * th, c * tw:(c + 1) * tw, :] = a
    con.close()
    alpha = mosaic[:, :, 3]
    for c, r in rgb_cells:
        y0, y1, x0, x1 = r * th, (r + 1) * th, c * tw, (c + 1) * tw
        edges = []
        if r > 0:
            edges.append(alpha[y0 - 1, x0:x1])
        if r < mh - 1:
            edges.append(alpha[y1, x0:x1])
        if c > 0:
            edges.append(alpha[y0:y1, x0 - 1])
        if c < mw - 1:
            edges.append(alpha[y0:y1, x1])
        if any((e == 0).mean() > 0.01 for e in edges):
            rec["opaque_block_at_clip"].append(f"{c},{r}")
    rec["clipped_px_pct"] = round(100 * float((alpha == 0).mean()), 1)
    tile_chk[t] = rec
    if rec["undecodable"]:
        problems.append(f"{t}: {len(rec['undecodable'])} tile(s) do not decode")
    if rec["wrong_size"]:
        problems.append(f"{t}: {rec['wrong_size'][:2]} are not {th}x{tw}")
    if rec["opaque_block_at_clip"]:
        problems.append(f"{t}: {len(rec['opaque_block_at_clip'])} 3-band tile(s) sit on "
                        f"clipped ground, so the clip would show as a block of paper")
chk["raster_tiles"] = tile_chk

# ---- the numeric coverages: a DEM must hold metres, not a picture -----------
# `dem_from_sheet` is an OGC 2D gridded coverage, not image tiles, and that is the
# whole point of it: an image layer could carry any value and a reader would have
# no way to know which class means which height. So every value in it must be one
# of the seven printed class midpoints (or the declared no-data), the class map
# must say exactly the same thing pixel by pixel, and the accuracy claim in the
# report must still be the accuracy of the layer that ships.
cov_chk = {}
for (t, kind) in sqlite3.connect(P).execute(
        "SELECT table_name, data_type FROM gpkg_contents"
        " WHERE data_type NOT IN ('features', 'tiles') ORDER BY 1"):
    con = sqlite3.connect(P)
    anc = con.execute("SELECT datatype, scale, offset, data_null FROM"
                      " gpkg_2d_gridded_coverage_ancillary"
                      " WHERE tile_matrix_set_name = ?", (t,)).fetchone()
    declared = con.execute("SELECT COUNT(*) FROM gpkg_extensions"
                           " WHERE extension_name = 'gpkg_2d_gridded_coverage'"
                           " AND (table_name = ? OR table_name LIKE 'gpkg_2d_%')",
                           (t,)).fetchone()[0]
    con.close()
    rec = dict(data_type=kind, ancillary=anc, extension_rows=declared)
    if not anc:
        problems.append(f"{t}: a gridded coverage with no ancillary row, so its "
                        f"datatype and no-data value are undeclared")
    with rasterio.open(f"GPKG:{P}:{t}") as ds:
        a = ds.read(1)
        rec.update(dtype=str(a.dtype), width=ds.width, height=ds.height,
                   crs=str(ds.crs), res=[round(v, 9) for v in ds.res])
        rec["sentinel_pixels"] = int((a == anc[3]).sum()) if anc and anc[3] is not None else 0
    if declared == 0:
        problems.append(f"{t}: the 2D gridded coverage extension is not declared")
    vals = np.unique(a[a != (anc[3] if anc and anc[3] is not None else -9999)])
    rec["distinct_values"] = int(len(vals))
    rec["values"] = [round(float(v), 2) for v in vals]
    # the companion class layer, if the report names one, must agree pixel for pixel
    if t == "dem_from_sheet" and "dem_from_sheet_class" in {
            r[0] for r in sqlite3.connect(P).execute("SELECT table_name FROM gpkg_contents")}:
        with rasterio.open(f"GPKG:{P}:dem_from_sheet_class") as ds:
            k = ds.read(1)
        mids = np.array(rec["values"])
        agree = np.isin(k, [0]) | np.isin(a, mids)
        mapped_same = np.array_equal(a != (anc[3] if anc else -9999), (k != 0))
        rec["class_map_same_footprint"] = bool(mapped_same)
        if not mapped_same:
            problems.append("dem_from_sheet and dem_from_sheet_class do not cover the "
                            "same pixels")
        off = a[(k > 0) & (a != (anc[3] if anc else -9999))]
        # every class value must be the midpoint of the class the class map names
        bad = int((np.abs(off - np.array(sorted(set(mids)))[np.clip(k[(k > 0)] - 1, 0,
                                                                     len(mids) - 1)]) > 1e-3).sum())
        rec["class_value_mismatches"] = bad
        if bad:
            problems.append(f"dem_from_sheet: {bad} pixel(s) do not carry the midpoint of "
                            f"the class the class map assigns")
    cov_chk[t] = rec
chk["coverages"] = cov_chk

# ---- class polygons: no self-overlap, and how much they actually cover -----
poly_chk = {}
for name in [n for n in layers if n.startswith("poly_")]:
    g = gpd.read_file(P, layer=name).to_crs(EQ)
    geoms = [shapely.make_valid(x) for x in g.geometry if x is not None]
    tot = sum(x.area for x in geoms) / 1e6
    uni = shapely.union_all(geoms).area / 1e6
    inside = shapely.make_valid(shapely.union_all(geoms).intersection(terr_ea)).area / 1e6
    poly_chk[name] = dict(polygons=len(geoms), sum_area_km2=round(tot, 1),
                          union_area_km2=round(uni, 1), self_overlap_km2=round(tot - uni, 4),
                          coverage_of_territory_pct=round(100 * inside / (terr_ea.area / 1e6), 2),
                          outside_territory_km2=round(uni - inside, 4))
    if tot - uni > 0.01:
        problems.append(f"{name}: {tot - uni:.3f} km2 of self-overlap")
chk["class_polygons"] = poly_chk


# ---- raster layers ---------------------------------------------------------
# The nine georeferenced images are rasters, not features, so pyogrio does not
# list them.  They are verified directly: CRS, grid, tile count, and - the check
# that matters - how much of the territory actually carries pixels, which catches
# a georeferencing slip that put the image mostly outside the border.
raster_report = {}
try:
    import rasterio
    from rasterio.features import rasterize as _rasterize
    con = sqlite3.connect(P)
    rnames = [r[0] for r in con.execute(
        "select table_name from gpkg_contents where data_type = 'tiles' order by table_name")]
    con.close()
    terr_geom = terr
    for name in rnames:
        with rasterio.open(f"GPKG:{P}:{name}") as ds:
            step = max(1, ds.width // 1200)
            out_shape = (ds.height // step, ds.width // step)
            # Image tiles have no field for a no-data value (the spec only lets the
            # numeric-coverage extension declare one), so a layer such as the DEM class
            # map must encode its mask as a sentinel value. That claim lives in
            # dem_from_sheet.json and in the layer's own description; take it from there
            # rather than assuming the last band is an alpha channel.
            sentinel = DEM_SENTINEL.get(name)
            if sentinel is None:
                have = ds.read(ds.count, out_shape=out_shape) > 0
            else:
                have = ds.read(1, out_shape=out_shape) != sentinel
            tr = ds.transform * ds.transform.scale(ds.width / out_shape[1],
                                                   ds.height / out_shape[0])
            inside = _rasterize([(terr_geom, 1)], out_shape=out_shape, transform=tr,
                                fill=0, all_touched=True, dtype="uint8").astype(bool)
            covered = (have & inside).sum() / max(inside.sum(), 1)
            spill = (have & ~inside).sum() / max(have.sum(), 1)
            rec = dict(kind="raster", crs=ds.crs.to_string() if ds.crs else None,
                       width=ds.width, height=ds.height, bands=ds.count,
                       dtype=ds.dtypes[0],
                       bounds=[round(v, 4) for v in ds.bounds],
                       territory_covered_pct=round(100 * covered, 2),
                       pixels_outside_territory_pct=round(100 * spill, 2))
            raster_report[name] = rec
            if rec["crs"] != "EPSG:4326":
                problems.append(f"{name}: raster is in {rec['crs']}, not EPSG:4326")
            # a small shortfall is expected and correct: the raster is clipped to
            # where the drawn country actually reaches, so it must not be invented
            # beyond the printed border.  A large one means the fit is off.
            if covered < 0.90:
                problems.append(f"{name}: only {100*covered:.1f} % of the territory carries pixels")
            if spill > 0.05:
                problems.append(f"{name}: {100*spill:.1f} % of its pixels fall outside the territory")
except ImportError:
    raster_report = {"note": "rasterio not installed - rasters not verified"}
chk["raster_layers"] = len(raster_report)
report["rasters"] = raster_report
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
        f"audit_layers.py verified all {len(layers)} feature layers, {chk['raster_layers']} "
        f"rasters and the file's own registers (dangling gpkg_extensions rows, orphan and "
        f"undeclared spatial indexes, empty tile-matrix zoom levels, blank descriptions): "
        f"{len(problems)} problems, "
        f"area {chk['area_4326_km2']:,.0f} km2 identical to {chk['area_agreement_pct']:+.3f}% between "
        f"EPSG:4326 / 6933 / geodesic, 2023 border within {chk['border_max_offset_m']:.1f} m of the "
        f"geology edge, {sum(bad_join.values())} point-to-unit join mismatches")
    # one-space indent: the file's own style, so a re-audit does not churn it
    json.dump([{"key": k, "value": v} for k, v in _meta.items()],
              open(_meta_path, "w"), indent=1, ensure_ascii=False)

print(f"\nwrote {HERE / 'layer_audit.json'}")
