#!/usr/bin/env python3
"""Repair the per-layer defects found by the deep layer-by-layer audit.

Each repair below was found by checking a layer against something other than
itself - its own documentation, its sibling layers, the source it was built from,
or the values it claims to hold. None of them is visible to a geometry or
integrity check. In order of how much damage the defect could do:

1. `mineral_localities_utm32n` is not a copy of `mineral_localities`.
   It carries the coordinates and the columns of `mineral_localities_refined`,
   and the two layers differ by up to 11.9 km in 117 of 999 rows. The name says
   one thing, the contents another. Renaming a published layer would break every
   query written against it, so the layer keeps its name and is documented for
   what it holds (`describe_layers.py`, `LAYERS.md` §7).
2. `mineral_localities.host_era` / `host_period` / `host_age_ma` were stale for
   one row (number 70, host `GIgss`): it said Cenozoic / Quaternary / 0.0117 Ma
   while the shipped geology says Mesozoic / Cretaceous / 93.9 Ma. Recomputed
   from `geology_units` so the denormalised copy cannot drift again.
3. `mineral_localities`, `_refined` and `_utm32n` had no `locality_id`, while the
   documentation names it as the key for the locality family and the three sibling
   layers carry it. Added by row order, after asserting the rows line up.
4. `towns_geonames.elevation_m` was TEXT holding integers, so `elevation_m > 500`
   compared strings (`'9' > '500'` is true). Stored as INTEGER with NULL.
5. `towns_geonames.state_agree` was TEXT holding `'True'`/`'False'`, the only
   boolean in the file not stored as one, so `WHERE state_agree` and
   `WHERE state_agree = 1` both failed. Stored as BOOLEAN (1/0/NULL).
6. `towns_geonames` gained `coord_dp`: the number of decimal places GeoNames
   records for the position. 4,419 of 45,415 entries carry 2 or fewer, which is
   up to kilometres of imprecision that nothing in the layer admitted to.
7. `towns`, `state_capitals` and `volcanic_plugs` stored each point twice - as
   geometry at 12 decimal places and as `lon`/`lat` at 4-6 - and the two copies
   disagreed by up to 0.1 m in 584 rows. The geometry is now exactly the
   `lon`/`lat` pair, so a query cannot get two answers for one point.
8. `geology_era` had no `class_id`, unlike the other two class layers, so a
   legend could not be keyed off a stable integer.

Run:  python repair_layers.py      (idempotent; report in layer_repairs.json)
"""
import json
import pathlib
import sqlite3

import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely
import shapely.geometry

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "layer_repairs.json"
report = {"file": GPKG.name, "repairs": {}}


def columns(con, t):
    return [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]


def declared_types(layer):
    """The declared field types, so a rewrite cannot quietly widen an INTEGER to REAL."""
    con = sqlite3.connect(GPKG)
    d = {r[1]: r[2] for r in con.execute(f'PRAGMA table_info("{layer}")')}
    con.close()
    return d


def rewrite(layer, fn, where=None):
    """Read a layer, apply fn to its GeoDataFrame, write it back in place.

    A plain UPDATE is not available on any layer with a spatial index (the
    GeoPackage rtree triggers call ST_IsEmpty, which the plain sqlite3 driver does
    not have), so attribute repairs go through the dataframe. Declared field types
    are restored on the way out: a round trip turns INTEGER-with-NULL into float.
    """
    types = declared_types(layer)
    g = gpd.read_file(GPKG, layer=layer)
    changed = fn(g)
    for c, t in types.items():
        if c not in g.columns:
            continue
        if t == "INTEGER":
            g[c] = pd.array(pd.to_numeric(g[c], errors="coerce").round(), dtype="Int64")
        elif t == "BOOLEAN":
            g[c] = pd.array([None if pd.isna(v) else bool(v) for v in g[c]], dtype="boolean")
        elif t == "REAL":
            g[c] = pd.to_numeric(g[c], errors="coerce").astype("float64")
    pyogrio.write_dataframe(g, GPKG, layer=layer, driver="GPKG", append=False)
    after = declared_types(layer)
    assert {k: after[k] for k in types} == types, (layer, types, after)
    return changed


# 1. document the mis-named copy (data unchanged) -----------------------------
con = sqlite3.connect(GPKG)
a = con.execute("SELECT lon, lat FROM mineral_localities").fetchall()
b = con.execute("SELECT lon, lat FROM mineral_localities_refined").fetchall()
u = con.execute("SELECT lon, lat FROM mineral_localities_utm32n").fetchall()
con.close()
report["repairs"]["mineral_localities_utm32n_identity"] = {
    "rows_matching_mineral_localities": sum(1 for x, y in zip(a, u) if x == y),
    "rows_matching_mineral_localities_refined": sum(1 for x, y in zip(b, u) if x == y),
    "verdict": "this layer is the EPSG:32632 copy of mineral_localities_refined, not of "
               "mineral_localities - documented, not renamed",
}

# 2. refresh the stale host attributes from the shipped geology ---------------
# A rewrite, not an UPDATE: an UPDATE on an rtree-indexed layer fires the
# GeoPackage spatial-index triggers, and those call SpatiaLite functions that
# plain SQLite does not have.
units = {r[0]: r[1:] for r in sqlite3.connect(GPKG).execute(
    "SELECT code, era, period, age_ma_max FROM geology_units")}


def blank(v):
    """NULL and NaN are the same absence; a comparison must not see a drift."""
    return v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and not v)


g = gpd.read_file(GPKG, layer="mineral_localities")
fixed, new_era, new_per, new_age = [], [], [], []
for _, r in g.iterrows():
    hc, era, per, age = r["host_code"], r["host_era"], r["host_period"], r["host_age_ma"]
    want = units.get(hc)
    if want is None:
        new_era.append(era); new_per.append(per); new_age.append(age)
        continue
    w_era, w_per, w_age = want
    same = (blank(era) and blank(w_era) or era == w_era) and \
           (blank(per) and blank(w_per) or per == w_per) and \
           ((blank(age) and blank(w_age))
            or (not blank(age) and not blank(w_age) and abs(float(age) - float(w_age)) < 1e-6))
    if not same:
        fixed.append(dict(number=int(r["number"]), host_code=hc,
                          was=[era, per, None if blank(age) else float(age)],
                          now=[w_era, w_per, None if blank(w_age) else float(w_age)]))
    new_era.append(w_era); new_per.append(w_per); new_age.append(w_age)
if fixed:
    g["host_era"], g["host_period"], g["host_age_ma"] = (
        pd.array(new_era, dtype="string"), pd.array(new_per, dtype="string"),
        pd.array(new_age, dtype="Float64"))
    pyogrio.write_dataframe(g, GPKG, layer="mineral_localities", driver="GPKG", append=False)
report["repairs"]["mineral_localities_host_attributes"] = dict(
    rows_checked=len(g), rows_drifted=len(fixed), rows=fixed[:20],
    note=("every locality's host_era/host_period/host_age_ma is now recomputed from the "
          "shipped geology_units; one row (number 70, host GIgss) carried Cenozoic / "
          "Quaternary / 0.0117 Ma against the geology's Mesozoic / Cretaceous / 93.9 Ma "
          "and was corrected on 2026-10-27. audit_layers.py now checks this every run."))
print(f"  host attributes vs geology: {len(g)} checked, {len(fixed)} drifted "
      f"{[f['number'] for f in fixed][:6]}")

# 3. locality_id on the three layers that lack it ----------------------------
icons = gpd.read_file(GPKG, layer="mineral_localities_icons")
key = list(zip(icons["zone"], icons["number"], icons["locality"]))
ids = list(icons["locality_id"])
added = {}
for t in ("mineral_localities", "mineral_localities_refined", "mineral_localities_utm32n"):
    g = gpd.read_file(GPKG, layer=t)
    if "locality_id" in g.columns:
        added[t] = "already present"
        continue
    assert list(zip(g["zone"], g["number"], g["locality"])) == key, (
        f"{t}: rows do not line up with mineral_localities_icons")
    g.insert(len(g.columns) - 1, "locality_id", ids)
    assert g["locality_id"].is_unique
    pyogrio.write_dataframe(g, GPKG, layer=t, driver="GPKG", append=False)
    added[t] = len(ids)
report["repairs"]["locality_id_added"] = added
print(f"  locality_id added: {added}")

# 4-6. towns_geonames: numeric elevation, real booleans, a precision column ---
g = gpd.read_file(GPKG, layer="towns_geonames")
before = dict(rows=len(g))
g["elevation_m"] = pd.to_numeric(g["elevation_m"], errors="coerce").astype("Int64")


def fold(s):
    """Fold a state name for comparison: no accents, no case, no 'State' suffix."""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().replace("-", " ").replace('\'', "").replace(" state", "")
    return " ".join(s.split())


# `state_agree` is recomputed from the two names, never converted from what is
# already in the column. The earlier version tested `str(v).lower() == 'true'`,
# which is fine on the first run (TEXT 'True') and silently sets every value
# False on the second - the column had lost all 29,470 of its True values while
# still passing every type and NULL check. A repair must be able to run twice.
g["state_agree"] = pd.array(
    [None if (pd.isna(a) or pd.isna(b) or not str(a).strip() or not str(b).strip())
     else fold(a) == fold(b)
     for a, b in zip(g["state"], g["state_gn"])], dtype="boolean")


def decimals(x):
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return len(s.split(".")[1]) if "." in s else 0


g["coord_dp"] = [min(decimals(x), decimals(y)) for x, y in zip(g.geometry.x, g.geometry.y)]
order = ["geonameid", "name", "ascii_name", "alt_names", "feature_code", "feature_type",
         "state", "state_gn", "state_agree", "admin1_code", "admin2_code", "lga",
         "population", "elevation_m", "dem_m", "timezone", "moddate", "in_nigeria",
         "coord_dp", "ngsa_town_km", "dup_group", "geometry"]
g = g[order]
pyogrio.write_dataframe(g, GPKG, layer="towns_geonames", driver="GPKG", append=False)
con = sqlite3.connect(GPKG)
types = {r[1]: r[2] for r in con.execute('PRAGMA table_info("towns_geonames)'.replace(')', '")'))}
dp_counts = dict(con.execute(
    "SELECT coord_dp, count(*) FROM towns_geonames GROUP BY 1 ORDER BY 1").fetchall())
coarse = con.execute("SELECT count(*) FROM towns_geonames WHERE coord_dp <= 2").fetchone()[0]
con.close()
assert types["elevation_m"] == "INTEGER" and types["state_agree"] == "BOOLEAN", types
report["repairs"]["towns_geonames"] = dict(
    rows=before["rows"], elevation_m="TEXT -> INTEGER (NULL where absent)",
    state_agree="TEXT 'True'/'False' -> BOOLEAN 1/0/NULL", coord_dp_added=True,
    coord_dp_distribution=dp_counts, rows_with_coord_dp_at_most_2=coarse)
print(f"  towns_geonames: elevation_m INTEGER, state_agree BOOLEAN, coord_dp added "
      f"({coarse:,} entries at <=2 decimal places)")

# 7. geometry == the lon/lat pair, in the three label layers ------------------
snapped = {}
for t in ("towns", "state_capitals", "volcanic_plugs"):
    g = gpd.read_file(GPKG, layer=t)
    d = np.hypot(g.geometry.x - g.lon, g.geometry.y - g.lat) * 111_000
    moved = int((d > 1e-9).sum())
    g["geometry"] = gpd.points_from_xy(g["lon"], g["lat"])
    pyogrio.write_dataframe(g, GPKG, layer=t, driver="GPKG", append=False)
    back = gpd.read_file(GPKG, layer=t)
    d2 = np.hypot(back.geometry.x - back.lon, back.geometry.y - back.lat) * 111_000
    assert float(np.abs(d2).max()) < 1e-9, (t, np.abs(d2).max())
    snapped[t] = dict(rows=len(g), rows_moved=moved, max_shift_m=round(float(d.max()), 3))
    print(f"  {t:16s} geometry snapped to lon/lat: {moved} rows moved, "
          f"max {d.max()*1000:.1f} mm")
report["repairs"]["geometry_snapped_to_lonlat"] = snapped

# 8. class_id on geology_era, matching the other two class layers -------------
g = gpd.read_file(GPKG, layer="geology_era")
if "class_id" not in g.columns:
    g = g.sort_values("area_km2", ascending=False).reset_index(drop=True)
    g.insert(0, "class_id", range(1, len(g) + 1))
    assert g["class_id"].is_unique
    pyogrio.write_dataframe(g, GPKG, layer="geology_era", driver="GPKG", append=False)
g = gpd.read_file(GPKG, layer="geology_era")
assert g["class_id"].notna().all() and g["class_id"].is_unique
report["repairs"]["geology_era_class_id"] = dict(
    rows=len(g), class_ids=sorted(int(v) for v in g["class_id"]))
print(f"  geology_era: class_id {sorted(int(v) for v in g['class_id'])}")

# 9. zero-area needles ("slits") in the polygon rings ------------------------
# The paint-order replay leaves, on 19 units and 4 era classes, a hairline where
# a ring runs out along a contact and comes back along the same line: 35 needles
# in geology_units (up to 7.1 km long), 95 in geology_era (up to 13.8 km). They
# enclose no area, so every area, overlap and gap test passes while the boundary
# is non-simple and simplification, rendering and any topology engine trip over
# it. Snapping the affected rings to a 1e-9 deg grid (0.05 mm, six orders of
# magnitude below the 0.7 km ink resolution the layer was read at) and
# re-validating removes them; the point set, the total area and the country's
# coverage are unchanged (asserted below).


def needles(geom):
    """Number of ring vertices where the path reverses along the line it came by."""
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


def polys_only(geom):
    parts = list(geom.geoms) if geom.geom_type.startswith("MultiPolygon") else [geom]
    return shapely.geometry.MultiPolygon([p for p in parts if p.geom_type == "Polygon"])


needle_report = {}
for layer in ("geology_units", "geology_era"):
    g = gpd.read_file(GPKG, layer=layer)
    area_before = float(g.geometry.area.sum())
    before = sum(needles(x) for x in g.geometry)
    rows = 0
    geom = []
    for x in g.geometry:
        if needles(x) == 0:
            geom.append(x)
            continue
        rows += 1
        geom.append(polys_only(shapely.make_valid(shapely.set_precision(x, 1e-9))))
    after = sum(needles(x) for x in geom)
    parts_before = sum(len(x.geoms) if x.geom_type.startswith("Multi") else 1 for x in g.geometry)
    if before and after == 0:
        g["geometry"] = geom
        pyogrio.write_dataframe(g, GPKG, layer=layer, driver="GPKG", append=False)
        back = gpd.read_file(GPKG, layer=layer)
        rel = abs(float(back.geometry.area.sum()) - area_before) / area_before
        # the only area that goes is the 4 sliver parts of < 1e-12 deg2 that the
        # snap collapses to a line: 1.6 m2 in the whole country
        assert rel < 1e-10, rel
        assert back.geometry.is_valid.all() and sum(needles(x) for x in back.geometry) == 0
    parts_after = sum(len(x.geoms) if x.geom_type.startswith("Multi") else 1 for x in geom)
    needle_report[layer] = dict(rows_cleaned=rows, needles_before=before, needles_after=after,
                                parts_before=parts_before, parts_after=parts_after,
                                area_lost_m2=round(abs(float(sum(x.area for x in geom)) - area_before) * 12_200_000_000, 1))
    print(f"  {layer:22s} needles {before} -> {after} over {rows} rows; "
          f"degenerate parts {parts_before - parts_after}, area lost "
          f"{needle_report[layer]['area_lost_m2']} m2")
report["repairs"]["ring_needles_removed"] = needle_report

# 10. the projected copies are rebuilt from the repaired 4326 geometry ---------
# Otherwise the parent is clean and its copies carry the old slits (they had
# fewer only because reprojection happened to collapse some).
g = gpd.read_file(GPKG, layer="geology_units")
utm = g.to_crs("EPSG:32632")
utm["geometry"] = [polys_only(shapely.make_valid(x)) for x in utm.geometry]
pyogrio.write_dataframe(utm, GPKG, layer="geology_units_utm32n", driver="GPKG", append=False)
ea = g.to_crs("EPSG:6933")
ea["geometry"] = [polys_only(shapely.make_valid(x)) for x in ea.geometry]
ea["area_km2_equal_area"] = np.round(ea.area.values / 1e6, 3)
pyogrio.write_dataframe(ea, GPKG, layer="geology_units_equal_area", driver="GPKG", append=False)
copy_needles = {l: sum(needles(x) for x in gpd.read_file(GPKG, layer=l).geometry)
                for l in ("geology_units_utm32n", "geology_units_equal_area")}
assert not any(copy_needles.values()), copy_needles
report["repairs"]["geology_copies_rebuilt"] = dict(
    layers=list(copy_needles), needles=copy_needles,
    equal_area_km2=round(float(ea["area_km2_equal_area"].sum()), 1))
print(f"  geology_units_utm32n / _equal_area rebuilt from the repaired geometry; "
      f"equal-area total {ea['area_km2_equal_area'].sum():,.1f} km2")

# 11. sentinel values and fixed-width truncations -----------------------------
# GeoNames writes -9999 where SRTM has no value (all 42 are coastal or riverine,
# where the void is water). Kept, it is an elevation of -9,999 m: any minimum,
# range or `dem_m < 500` query silently counts it as data.
def fix_towns_geonames(g):
    # -9999 is the SRTM void; the two small negatives (Lagos, Rivers) are voids
    # over water too - a coastal village is not 3 m below sea level
    n_void = int(((g["dem_m"] == -9999) | (g["dem_m"] < 0)).sum())
    g.loc[(g["dem_m"] == -9999) | (g["dem_m"] < 0), "dem_m"] = pd.NA
    # two columns were cut by a fixed character budget and in both cases the cut
    # fell inside a token: the alt-name list stopped mid-name ("...ha ke ")
    def whole_names(alt):
        if not isinstance(alt, str):
            return alt
        parts = [x.strip() for x in alt.split(",") if x.strip()]
        keep, used = [], 0
        for x in parts:
            if used + len(x) + 1 > 118:
                break
            keep.append(x)
            used += len(x) + 1
        return ",".join(keep) or None

    before = g["alt_names"].copy()
    g["alt_names"] = [whole_names(v) for v in g["alt_names"]]
    cut = int(sum(1 for a, b in zip(before, g["alt_names"])
                  if isinstance(a, str) and a != b))
    # one place inside Nigeria carried the neighbouring country's time zone
    tz = int(((g["timezone"] == "Africa/Douala") & (g["in_nigeria"] == 1)).sum())
    g.loc[(g["timezone"] == "Africa/Douala") & (g["in_nigeria"] == 1), "timezone"] = "Africa/Lagos"
    return dict(dem_m_void_to_null=n_void, alt_names_cut=cut, timezone_fixed=tz)


tg_fix = rewrite("towns_geonames", fix_towns_geonames)
print(f"  towns_geonames: {tg_fix['dem_m_void_to_null']} x -9999 (SRTM void) -> NULL, "
      f"{tg_fix['alt_names_cut']} alt-name lists cut at a whole name, "
      f"{tg_fix['timezone_fixed']} time zone corrected")
report["repairs"]["towns_geonames_detail"] = tg_fix


def fix_symbols(g):
    bad = "nearest printed number (colour not consi"
    n = int((g["link"] == bad).sum())
    g.loc[g["link"] == bad, "link"] = "nearest printed number (colour not considered)"
    return n


def fix_pop(g):
    n = int((g["class_name"] == "0 - 110,85").sum())
    g.loc[g["class_name"] == "0 - 110,85", "class_name"] = "0 - 110,852"
    return n


n_link = rewrite("mineral_symbols", fix_symbols)
n_pop = rewrite("poly_population", fix_pop)
print(f"  mineral_symbols.link un-truncated ({n_link} rows); "
      f"poly_population class_name '0 - 110,85' -> '0 - 110,852' ({n_pop} rows)")
report["repairs"]["truncated_text"] = dict(mineral_symbols_link=n_link,
                                           poly_population_class_name=n_pop)

# 12. spacing in names ---------------------------------------------------------
# "Gabu(Ogaja)" is the one locality out of 999 written without a space before its
# parenthetical, and one town name carried a double space. Cosmetic, but both are
# join keys: the same name written two ways is two names.
def fix_locality(g):
    if "locality" not in g.columns:
        return 0
    n = int((g["locality"] == "Gabu(Ogaja)").sum())
    g.loc[g["locality"] == "Gabu(Ogaja)", "locality"] = "Gabu (Ogaja)"
    return n


spaced = {}
for layer in ("mineral_localities", "mineral_localities_refined", "mineral_localities_utm32n",
              "mineral_localities_icons", "mineral_localities_icons_utm32n",
              "mineral_localities_equal_area"):
    spaced[layer] = rewrite(layer, fix_locality)


def fix_town_name(g):
    n = int((g["name"] == "Bakin  Diru").sum())
    g.loc[g["name"] == "Bakin  Diru", "name"] = "Bakin Diru"
    return n


spaced["towns"] = rewrite("towns", fix_town_name)
print(f"  'Gabu(Ogaja)' -> 'Gabu (Ogaja)' in {sum(spaced.values())} rows; "
      f"'Bakin  Diru' -> 'Bakin Diru'")
report["repairs"]["name_spacing"] = spaced

# 13. `formation` held an annotation, a dash and two lithologies --------------
# The column is documented as "the formation name where the legend gives one",
# but 12 rows carried a provenance tag typed into the name ("(chart key)"), one
# read "Awgu - Formation" with a dash before the word Formation, one had a double
# space, and three held a lithology ("Sediments", "Mangroves swamps", "Meader
# belt, ...") because the sheet's legend row gave no formation. The tag moves to
# `note`, the names are tidied, and the three lithologies become NULL - what the
# sheet actually says is still in `unit`.
import re


# noqa: E402 - kept next to the code that uses it


def tidy_formation(v):
    if v is None or pd.isna(v):
        return None, None
    raw, note, name = str(v), None, str(v)
    if "(chart key)" in name:
        name = name.replace("(chart key)", "").strip()
        note = "formation name read from the chart key"
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\s+-\s+Formation$", " Formation", name)
    name = re.sub(r"(?<=\w)\s+-\s+(?=\w)", "-", name)
    if name.strip().lower() in ("sediments", "mangroves swamps",
                                "meader belt, back swamps, fresh water swamps"):
        return None, "no formation name on the sheet - the legend gives the lithology only"
    return name.strip(), note


def make_formation_fix():
    def fix(g):
        newf, notes, changed = [], [], 0
        for f, n in zip(g["formation"], g["note"]):
            nf, extra = tidy_formation(f)
            old = None if (f is None or pd.isna(f)) else str(f)
            if (None if nf is None else str(nf)) != old:
                changed += 1
            newf.append(nf)
            notes.append(extra if extra else n)
        if changed:
            g["formation"] = pd.array(newf, dtype=object)
            g["note"] = pd.array(notes, dtype=object)
        return changed
    return fix


tidied = {}
for layer in ("geology_units", "geology_units_utm32n", "geology_units_equal_area"):
    tidied[layer] = rewrite(layer, make_formation_fix())
    print(f"  {layer:24s} formation tidied: {tidied[layer]} rows")
report["repairs"]["formation_tidied"] = tidied
con = sqlite3.connect(GPKG)
formations = [r[0] for r in con.execute(
    "SELECT formation FROM geology_units WHERE formation IS NOT NULL ORDER BY 1")]
print(f"    now {len(formations)} formation names, none carrying '(chart key)'")
report["repairs"]["formation_names"] = dict(count=len(formations), values=formations)
con.close()

# 14. one length measure per row --------------------------------------------
# `len_km` is the geodesic (ellipsoidal) length of the line, but `km_in_nigeria`
# was measured on the EPSG:6933 equal-area grid, which stretches a north-south
# line by up to 14 % at this latitude. The two numbers sat in the same row, so
# `km_in_nigeria` came out *longer* than the whole line in 580 river rows and
# 1,972 geology-boundary rows, and `frac_in_nigeria` (clamped) hid it. Both are
# now geodesic, from the same call, and `frac_in_nigeria` is their ratio - so
# `km_in_nigeria <= len_km` holds by construction.
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
TERRITORY = gpd.read_file(GPKG, layer="national_territory").geometry.iloc[0]


def geo_len(geom):
    """Ellipsoidal length in km of a (multi)line, or 0."""
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


length_rows = {}
# the border carried its length as `length_km` while every other line layer calls it
# `len_km`, and it had no in-Nigeria fields at all. One name, one measure.
_border = gpd.read_file(GPKG, layer="international_boundary")
if "length_km" in _border.columns:


    def rename_border_length(g):
        g["len_km"] = np.round([geo_len(x) for x in g.geometry], 3)
        return len(g)


    rewrite("international_boundary", rename_border_length)
    con = sqlite3.connect(GPKG)
    con.execute('ALTER TABLE "international_boundary" DROP COLUMN "length_km"')
    con.commit()
    con.close()
    print("  international_boundary: length_km renamed len_km (geodesic, as everywhere else)")
    report["repairs"]["international_boundary_length"] = dict(
        renamed="length_km -> len_km",
        length_km=round(float(gpd.read_file(GPKG, layer="international_boundary")["len_km"].sum()), 3))

for layer in ("state_boundaries", "fold_axes", "roads", "rivers", "faults", "geology_boundaries",
              "younger_granite_outlines", "railway", "international_boundary"):
    g = gpd.read_file(GPKG, layer=layer)
    if "len_km" not in g.columns:
        continue
    before_over = int((g["km_in_nigeria"] > g["len_km"] + 1e-6).sum()) if "km_in_nigeria" in g.columns else 0
    old_len, old_in = float(g["len_km"].sum()), (
        float(g["km_in_nigeria"].sum()) if "km_in_nigeria" in g.columns else None)

    def fix(g):
        tot = [geo_len(x) for x in g.geometry]
        g["len_km"] = np.round(tot, 3)
        if "km_in_nigeria" in g.columns:
            ins = [geo_len(shapely.make_valid(x.intersection(TERRITORY))) for x in g.geometry]
            g["km_in_nigeria"] = np.round(ins, 3)
            g["frac_in_nigeria"] = np.round(
                np.where(np.array(tot) > 0, np.array(ins) / np.maximum(np.array(tot), 1e-9), 0.0), 4)
        return len(g)

    rewrite(layer, fix)
    g = gpd.read_file(GPKG, layer=layer)
    after_over = int((g["km_in_nigeria"] > g["len_km"] + 1e-6).sum()) if "km_in_nigeria" in g.columns else 0
    assert after_over == 0, (layer, after_over)
    rec = dict(rows=len(g), len_km_before=round(old_len, 1), len_km_after=round(float(g["len_km"].sum()), 1),
               rows_with_in_nigeria_over_total_before=before_over, after=after_over)
    if old_in is not None:
        rec["km_in_nigeria_before"] = round(old_in, 1)
        rec["km_in_nigeria_after"] = round(float(g["km_in_nigeria"].sum()), 1)
        rec["share_before_pct"] = round(100 * old_in / old_len, 2)
        rec["share_after_pct"] = round(100 * float(g["km_in_nigeria"].sum()) / float(g["len_km"].sum()), 2)
    length_rows[layer] = rec
    print(f"  {layer:24s} len {rec['len_km_before']:>10,.1f} -> {rec['len_km_after']:>10,.1f} km; "
          f"rows with in-Nigeria > total {before_over} -> 0")
report["repairs"]["line_lengths_recomputed"] = length_rows

# 15. water bodies: one measure, and an in-Nigeria area that cannot exceed the
# ---------------------------------------------------------------------------
# The stored areas were close to the geometry's own EPSG:6933 area but not equal
# to it - up to 10 km2 out on Lake Chad (0.07 %) - so the numbers could not be
# reproduced from the file, only believed. The unnamed reservoir's
# `area_in_nigeria_km2` (225.7) was larger than its total area (225.56), giving
# `frac_in_nigeria` 1.0006. Both are recomputed here in the conventions the rest
# of the file uses: area in EPSG:6933 (as `geology_units.area_km2` and the
# `poly_*` layers), perimeter geodesic including the interior rings. The
# perimeter barely moves (Lake Chad 1,569.7 -> 1,570.3 km): it was right.
wb = gpd.read_file(GPKG, layer="water_bodies")
stored = {k: round(float(v), 2) for k, v in zip(
    wb["name"].fillna("unnamed reservoir"), wb["area_km2"])}


def fix_water(g):
    ea = g.to_crs("EPSG:6933")
    g["area_km2"] = np.round(ea.area.values / 1e6, 3)
    ins = [shapely.make_valid(x.intersection(TERRITORY)) for x in g.geometry]
    inside = gpd.GeoSeries(ins, crs="EPSG:4326").to_crs("EPSG:6933").area.values / 1e6
    g["area_in_nigeria_km2"] = np.round(np.minimum(inside, g["area_km2"].values), 3)
    g["frac_in_nigeria"] = np.round(
        np.where(g["area_km2"] > 0, g["area_in_nigeria_km2"] / g["area_km2"], 0.0), 4)
    g["perim_km"] = np.round([geo_len(x) + _ring_len(x) for x in g.geometry], 3)
    return len(g)


def _ring_len(geom):
    """Geodesic perimeter that geo_len() leaves out (it only walks lines)."""
    if geom is None or geom.is_empty:
        return 0.0
    parts = [geom] if geom.geom_type == "Polygon" else list(getattr(geom, "geoms", []))
    total = 0.0
    for p in parts:
        for ring in [p.exterior] + list(p.interiors):
            xs, ys = np.asarray(ring.coords).T[:2]
            total += GEOD.line_length(xs, ys)
    return total / 1000


rewrite("water_bodies", fix_water)
wb2 = gpd.read_file(GPKG, layer="water_bodies")
assert (wb2["area_in_nigeria_km2"] <= wb2["area_km2"] + 1e-3).all()
assert (wb2["frac_in_nigeria"] <= 1.0).all()
report["repairs"]["water_bodies_geometry_measures"] = dict(
    area_before_km2=stored,
    area_after_km2={k: round(float(v), 2) for k, v in
                    zip(wb2["name"].fillna("unnamed reservoir"), wb2["area_km2"])},
    total_before_km2=round(sum(stored.values()), 1),
    total_after_km2=round(float(wb2["area_km2"].sum()), 1),
    perim_before_km={k: round(float(v), 1) for k, v in
                     zip(wb["name"].fillna("unnamed reservoir"), wb["perim_km"])},
    perim_after_km={k: round(float(v), 1) for k, v in
                    zip(wb2["name"].fillna("unnamed reservoir"), wb2["perim_km"])})
print(f"  water_bodies: area {sum(stored.values()):,.1f} -> {wb2['area_km2'].sum():,.1f} km2 "
      f"(EPSG:6933), perimeter geodesic, in-Nigeria <= total")

# 16. one ring convention: exterior counter-clockwise, holes clockwise ---------
# Every exterior ring in the file was wound clockwise (4,268 of them), the
# shapefile convention. A GeoPackage stores WKB and does not require either
# winding, but GeoJSON (RFC 7946) and GeoParquet require counter-clockwise
# exteriors, so a clockwise file silently flips when it is exported and a
# consumer that trusts ring order gets the interior and the exterior the wrong
# way round. Normalising costs nothing: the point set, the area and the geometry
# are unchanged, only the vertex order along each ring.
wind = {}


def _ccw(geom):
    if geom is None or geom.is_empty or "Polygon" not in geom.geom_type:
        return geom
    return shapely.orient_polygons(geom, exterior_cw=False)


for layer in ("national_territory", "geology_units", "geology_units_utm32n",
              "geology_units_equal_area", "geology_era", "poly_soil_ph",
              "poly_population", "water_bodies"):
    g = gpd.read_file(GPKG, layer=layer)
    parts = lambda geom: ([geom] if geom.geom_type == "Polygon"
                          else list(getattr(geom, "geoms", [])))
    before_cw = sum(1 for geom in g.geometry for p in parts(geom) if not p.exterior.is_ccw)
    before_ccw_interior = sum(
        1 for geom in g.geometry for p in parts(geom)
        for h in p.interiors if h.is_ccw)

    def fix(g):
        g["geometry"] = [_ccw(x) for x in g.geometry]
        return len(g)

    rewrite(layer, fix)
    g2 = gpd.read_file(GPKG, layer=layer)
    after_cw = sum(1 for geom in g2.geometry for p in parts(geom) if not p.exterior.is_ccw)
    after_ccw_interior = sum(1 for geom in g2.geometry for p in parts(geom)
                             for h in p.interiors if h.is_ccw)
    assert after_cw == 0 and after_ccw_interior == 0, (layer, after_cw, after_ccw_interior)
    wind[layer] = dict(clockwise_exteriors_before=before_cw, after=after_cw,
                       clockwise_holes_before=before_ccw_interior, holes_after=after_ccw_interior)
    print(f"  {layer:26s} clockwise exteriors {before_cw:5d} -> 0; "
          f"counter-clockwise holes {before_ccw_interior:3d} -> 0")
report["repairs"]["ring_orientation"] = wind

# a second run finds every repair already applied; keep the first run's record
if OUT.exists():
    prev = json.load(open(OUT))
    if prev.get("repairs") and not report.get("history"):
        report["history"] = prev["repairs"]
        report["note"] = ("every repair below is already applied and verified; `history` is "
                          "what the first run changed")
json.dump(report, open(OUT, "w"), indent=1)
print(f"\nwrote {OUT.name}")
