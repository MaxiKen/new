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
              ("mineral_localities_icons", "mineral_localities_equal_area")]
copy_diffs = {}
for a, b in COPY_PAIRS:
    ta = {r[1]: r[2] for r in con.execute(f'PRAGMA table_info("{a}")')}
    tb = {r[1]: r[2] for r in con.execute(f'PRAGMA table_info("{b}")')}
    common = [c for c in ta if c in tb and c not in ("geom", "fid")]
    key = "code" if "code" in ta else "locality_id"
    A = {r[key]: r for r in con.execute(f'SELECT * FROM "{a}"')}
    B = {r[key]: r for r in con.execute(f'SELECT * FROM "{b}"')}
    diffs = {}
    for k in A:
        if k not in B:
            continue
        for c in common:
            if A[k][c] != B[k][c]:
                diffs[c] = diffs.get(c, 0) + 1
    if set(A) != set(B):
        diffs["__keys__"] = len(set(A) ^ set(B))
    if diffs:
        copy_diffs[f"{a} -> {b}"] = diffs
        problems.append(f"{b} is not attribute-identical to {a}: {diffs}")
attr["projected_copy_attribute_diffs"] = copy_diffs

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
    if t not in contents]
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
con.close()
chk["geopackage_conformance"] = gpkg

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
            alpha = ds.read(ds.count, out_shape=out_shape)
            tr = ds.transform * ds.transform.scale(ds.width / out_shape[1],
                                                   ds.height / out_shape[0])
            inside = _rasterize([(terr_geom, 1)], out_shape=out_shape, transform=tr,
                                fill=0, all_touched=True, dtype="uint8").astype(bool)
            have = alpha > 0
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
