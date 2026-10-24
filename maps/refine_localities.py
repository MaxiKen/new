#!/usr/bin/env python3
"""
Refine mineral locality positions to the centre of the symbol that depicts them.

Principle
---------
On the 2023 sheet a locality is drawn as (a) a mineral symbol, which IS the
feature, and (b) a printed number, which is only a pointer.  The symbol centre
is therefore the authoritative position; the number is wherever the cartographer
could fit it - on this sheet a median of 9.0 km away.

686 localities were already anchored on their symbol.  This script tries to
recover the symbol for the rest, and it only trusts a rule that has been
back-tested on the 686 known cases:

    rule                     back-test on 686 known points
    nearest same-mineral     within 1 km 95.6 %  |  wrong (>5 km) 3.9 %
    nearest same-colour      within 1 km 95.5 %  |  wrong (>5 km) 4.5 %
    centroid of same-colour
      symbols within 20 km   median error 2.9 km          <- rejected

The centroid of a group of symbols is measurably worse than the single
compatible symbol, because a group mixes symbols belonging to neighbouring
localities.  So the rule used here is always "take ONE symbol centre".

Rules applied in order, each symbol claimed at most once:
    A  same mineral identity, unambiguous, <= 12 km     sigma 3 km
    B  same colour (recorded),  unambiguous, <= 12 km   sigma 3 km
    C  colour inferred from the mineral (>=90 % pure),  <= 12 km   sigma 3 km
    D  no symbol recoverable -> keep the printed number sigma 10 km

The 12 km ceiling is not arbitrary: on simulated hard cases the rule is right
83 % of the time at 9-12 km, 67 % at 12-16 km and 4 % beyond 16 km.

Writes layers mineral_localities_refined and mineral_localities_utm32n, and
maps/locality_reassignments.csv.
"""
import pathlib
import sqlite3
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import STRtree, points

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
MLON = 111320 * np.cos(np.radians(9))
MLAT = 110570

# Recovered positions are given sigma 3 km, not 1 km: measured on simulated hard
# cases (symbol hidden within 8.8 km of the printed number) an unambiguous pick
# up to 12 km away lands on the correct symbol 83 % of the time and on a wrong
# one 15 % of the time, i.e. an rms error near 3 km.  Beyond 16 km the same rule
# is right only 4 % of the time, so no pick beyond 12 km is accepted at all.
SIGMA = {"printed symbol centre": 700,
         "symbol recovered by mineral identity": 3000,
         "symbol recovered by colour": 3000,
         "symbol recovered by inferred colour": 3000,
         "label position only": 10000}
MAX_PICK_M = 12000

loc = gpd.read_file(GPKG, layer="mineral_localities")
sym = gpd.read_file(GPKG, layer="mineral_symbols")
units = gpd.read_file(GPKG, layer="geology_units")

sym = sym[~sym["mineral"].astype(str).str.startswith("not a mineral")].reset_index(drop=True)
sym["m"] = sym["mineral"].astype(str).str.lower().str.strip()
sym["c"] = sym["colour"].fillna("").astype(str).str.lower().str.strip()


def is_colour(v):
    v = str(v).lower().strip()
    return bool(v) and v not in ("nan", "none") and "no symbol" not in v


loc["m"] = loc["mineral_1"].astype(str).str.lower().str.strip()
loc["c"] = loc["sym_colour"].map(lambda v: str(v).lower().strip() if is_colour(v) else "")

# mineral -> dominant colour, where that colour is >= 90 % pure
purity = {}
for m, g in sym[sym["c"] != ""].groupby("m"):
    if len(g) >= 5:
        vc = g["c"].value_counts(normalize=True)
        if vc.iloc[0] >= 0.90:
            purity[m] = vc.index[0]

sx = sym.geometry.x.values * MLON
sy = sym.geometry.y.values * MLAT

out = loc.copy()
out["pos_method"] = np.where(loc["pos_src"] == "raster symbol (colour-consistent)",
                             "printed symbol centre", "label position only")
out["pos_sigma_m"] = out["pos_method"].map(SIGMA)
out["reassigned_from"] = ""

# symbols already spoken for by the 686 anchored localities
claimed = set()
for i, r in loc.iterrows():
    if r["pos_src"] == "raster symbol (colour-consistent)":
        d = np.hypot(sx - r.geometry.x * MLON, sy - r.geometry.y * MLAT)
        claimed.add(int(np.argmin(d)))


def candidates(i, field, value, limit):
    lx, ly = loc.geometry.x.iloc[i] * MLON, loc.geometry.y.iloc[i] * MLAT
    idx = [j for j in range(len(sym))
           if j not in claimed and sym[field].iloc[j] == value]
    out_ = []
    for j in idx:
        d = np.hypot(sx[j] - lx, sy[j] - ly)
        if d < limit * 1.6:
            out_.append((d, j))
    return sorted(out_)


moves = []
pending = [i for i in loc.index if loc.loc[i, "pos_src"] == "label centre"]

# ---- rule A: mineral identity ---------------------------------------------
for i in pending:
    c = candidates(i, "m", loc.at[i, "m"], MAX_PICK_M)
    if not c:
        continue
    d0, j = c[0]
    d1 = c[1][0] if len(c) > 1 else 1e9
    if d0 <= MAX_PICK_M and d1 > 2 * d0:
        claimed.add(j)
        moves.append((i, j, d0, "symbol recovered by mineral identity"))

done = {m[0] for m in moves}

# ---- rule B: recorded colour ----------------------------------------------
for i in pending:
    if i in done or not loc.at[i, "c"]:
        continue
    c = candidates(i, "c", loc.at[i, "c"], 12000)
    if not c:
        continue
    d0, j = c[0]
    d1 = c[1][0] if len(c) > 1 else 1e9
    if d0 <= MAX_PICK_M and d1 > 2 * d0:
        claimed.add(j)
        moves.append((i, j, d0, "symbol recovered by colour"))
        done.add(i)

# ---- rule C: colour inferred from the mineral ------------------------------
for i in pending:
    if i in done:
        continue
    col = purity.get(loc.at[i, "m"])
    if not col:
        continue
    c = candidates(i, "c", col, 10000)
    if not c:
        continue
    d0, j = c[0]
    d1 = c[1][0] if len(c) > 1 else 1e9
    if d0 <= MAX_PICK_M and d1 > 2 * d0:
        claimed.add(j)
        moves.append((i, j, d0, "symbol recovered by inferred colour"))
        done.add(i)

for i, j, d0, method in moves:
    out.at[i, "geometry"] = points(sx[j] / MLON, sy[j] / MLAT)
    out.at[i, "lon"] = sx[j] / MLON
    out.at[i, "lat"] = sy[j] / MLAT
    out.at[i, "pos_method"] = method
    out.at[i, "pos_sigma_m"] = SIGMA[method]
    out.at[i, "reassigned_from"] = f"label {loc.at[i, 'geometry'].x:.4f},{loc.at[i, 'geometry'].y:.4f}"
    out.at[i, "moved_m"] = round(d0, 0)

# high = anchored on the printed symbol; probable = validated rule (83 %);
# low = only the printed number locates it
out["pos_confidence"] = out["pos_sigma_m"].map(
    lambda s: "high" if s <= 700 else ("probable" if s <= 3000 else "low"))
out["candidate_dist_m"] = out.get("moved_m")

# ---- host unit at the final position ---------------------------------------
ut = STRtree(units.geometry.values)
codes, dists = [], []
for x, y in zip(out.geometry.x, out.geometry.y):
    g = points(x, y)
    idx = ut.query(g, predicate="intersects")
    if len(idx) == 0:
        idx = ut.query_nearest(g)
        dists.append(float(np.nan))
    else:
        u = units.iloc[int(idx[np.argmin(units.iloc[idx]["area_km2"].values)])]
        codes.append(u["code"])
        dists.append(gpd.GeoSeries([g], crs=units.crs).distance(u.geometry.boundary).iloc[0] * MLON)
        continue
    u = units.iloc[int(idx[0])] if len(idx) else None
    codes.append(u["code"] if u is not None else None)
out["host_code"] = codes
out["host_boundary_dist_m"] = [round(d, 0) if np.isfinite(d) else None for d in dists]

order = ["zone", "number", "locality", "mineral_1", "group_1", "minerals", "n_minerals",
         "lon", "lat", "pos_method", "pos_sigma_m", "pos_confidence",
         "reassigned_from", "host_code", "host_boundary_dist_m", "geometry"]
out = out[[c for c in order if c in out.columns]]

pd.DataFrame([dict(zone=loc.at[i, "zone"], number=loc.at[i, "number"],
                   locality=loc.at[i, "locality"], mineral=loc.at[i, "mineral_1"],
                   method=m, from_lon=loc.at[i, "geometry"].x, from_lat=loc.at[i, "geometry"].y,
                   to_lon=sym.geometry.x.iloc[j], to_lat=sym.geometry.y.iloc[j],
                   moved_km=round(d0 / 1000, 2))
              for i, j, d0, m in sorted(moves, key=lambda t: t[2])]
             ).to_csv(HERE / "locality_reassignments.csv", index=False)

n = len(out)
print(f"localities: {n}")
for meth, g in out.groupby("pos_method"):
    print(f"  {meth:40s} {len(g):4d}  ({len(g) / n * 100:4.1f}%)  sigma +-{SIGMA[meth] / 1000:.1f} km")
print(f"  median positional sigma: +-{np.median(out['pos_sigma_m']) / 1000:.1f} km")
print(f"  high: {int((out['pos_confidence'] == 'high').sum())}  "
      f"probable: {int((out['pos_confidence'] == 'probable').sum())}  "
      f"low: {int((out['pos_confidence'] == 'low').sum())}")
if moves:
    mv = np.array([m[2] for m in moves]) / 1000
    print(f"  recovered {len(moves)} points, moved median {np.median(mv):.1f} km (max {mv.max():.1f} km)")


def drop_layer(path, name):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (name,))
    if cur.fetchone()[0]:
        cur.execute('DROP TABLE "%s"' % name)
        for tbl in ("gpkg_contents", "gpkg_geometry_columns", "gpkg_extensions"):
            try:
                cur.execute(f"DELETE FROM {tbl} WHERE table_name=?", (name,))
            except sqlite3.OperationalError:
                pass
        con.commit()
    con.close()


for layer, gdf, crs in (("mineral_localities_refined", out, "EPSG:4326"),
                        ("mineral_localities_utm32n", out.to_crs("EPSG:32632"), "EPSG:32632")):
    drop_layer(GPKG, layer)
    gpd.GeoDataFrame(gdf, geometry="geometry", crs=crs).to_file(
        GPKG, layer=layer, driver="GPKG", mode="a")
    print("wrote layer", layer)
