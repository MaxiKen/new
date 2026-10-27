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

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "layer_repairs.json"
report = {"file": GPKG.name, "repairs": {}}


def columns(con, t):
    return [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]


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
g["state_agree"] = pd.array(
    [None if pd.isna(v) else (str(v).strip().lower() == "true") for v in g["state_agree"]],
    dtype="boolean")


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

# a second run finds every repair already applied; keep the first run's record
if OUT.exists():
    prev = json.load(open(OUT))
    if prev.get("repairs") and not report.get("history"):
        report["history"] = prev["repairs"]
        report["note"] = ("every repair below is already applied and verified; `history` is "
                          "what the first run changed")
json.dump(report, open(OUT, "w"), indent=1)
print(f"\nwrote {OUT.name}")
