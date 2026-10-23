#!/usr/bin/env python3
"""
Refine the mineral locality positions and publish per-point accuracy.

What this does
--------------
The 2023 sheet prints a number for every locality but only prints a mineral
symbol at some of them.  Where a symbol exists the locality is best placed at
the symbol centre; where it does not, the number label is the only ink and the
cartographer has placed it wherever there was room - on this sheet that is a
median of 9 km away from the symbol of the very same feature.

For the localities that were carried on their label position, this script tries
to recover the symbol by matching BOTH the mineral identity and the geometry,
accepting a match only when it is unambiguous (the best candidate is at least
twice as close as the next one, and within 15 km).  Everything else keeps its
label position and is flagged, because a wrong 7 km snap is worse than an honest
label position.

Adds to the GeoPackage:
    mineral_localities_refined   positions + pos_method + pos_sigma_m
    mineral_localities_utm32n    same points on WGS 84 / UTM zone 32N (EPSG:32632)
and writes maps/locality_reassignments.csv
"""
import pathlib
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely import STRtree, points

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
MLON = 111320 * np.cos(np.radians(9))     # metres per degree lon at 9 N
MLAT = 110570                             # metres per degree lat

# positional sigma attached to each way of locating a point (metres)
SIGMA = {
    "printed symbol centre": 700,          # symbol is ~1 pt wide; +-0.5 pt + 130 m registration
    "symbol recovered by identity + geometry": 1200,
    "label position only": 10000,          # median label->symbol displacement on this sheet
    "label position, no symbol printed at all": 10000,
}

loc = gpd.read_file(GPKG, layer="mineral_localities")
sym = gpd.read_file(GPKG, layer="mineral_symbols")
units = gpd.read_file(GPKG, layer="geology_units")


def norm(s):
    s = str(s).lower()
    for a, b in [("cassiterite", "tin"), ("pottery", "clay"), ("kaolinitic", "kaolin")]:
        s = s.replace(a, b)
    return s.strip()


sym = sym.copy()
sym["m"] = sym["mineral"].map(norm)
loc = loc.reset_index(drop=True)
loc["m"] = loc["mineral_1"].map(norm)

sx = sym.geometry.x.values * MLON
sy = sym.geometry.y.values * MLAT

out = loc.copy()
out["pos_method"] = np.where(
    loc["pos_src"] == "raster symbol (colour-consistent)",
    "printed symbol centre", "label position only")
out["pos_sigma_m"] = out["pos_method"].map(SIGMA)
out["reassigned_from"] = ""

log = []
claimed = set()
for i, row in loc.iterrows():
    if row["pos_src"] != "label centre":
        continue
    lx, ly = row.geometry.x * MLON, row.geometry.y * MLAT
    cand = [j for j in range(len(sym))
            if sym["m"].iloc[j] == row["m"] and j not in claimed
            and np.hypot(sx[j] - lx, sy[j] - ly) < 30000]
    if not cand:
        continue
    cand.sort(key=lambda j: np.hypot(sx[j] - lx, sy[j] - ly))
    d0 = np.hypot(sx[cand[0]] - lx, sy[cand[0]] - ly)
    d1 = np.hypot(sx[cand[1]] - lx, sy[cand[1]] - ly) if len(cand) > 1 else 1e9
    if d0 < 15000 and d1 > 2.0 * d0:
        claimed.add(cand[0])
        out.at[i, "geometry"] = points(sx[cand[0]] / MLON, sy[cand[0]] / MLAT)
        out.at[i, "lon"] = sx[cand[0]] / MLON
        out.at[i, "lat"] = sy[cand[0]] / MLAT
        out.at[i, "pos_method"] = "symbol recovered by identity + geometry"
        out.at[i, "pos_sigma_m"] = SIGMA["symbol recovered by identity + geometry"]
        out.at[i, "reassigned_from"] = f"label {row.geometry.x:.4f},{row.geometry.y:.4f}"
        log.append(dict(zone=row["zone"], number=row["number"], locality=row["locality"],
                        mineral=row["mineral_1"],
                        from_lon=row.geometry.x, from_lat=row.geometry.y,
                        to_lon=sx[cand[0]] / MLON, to_lat=sy[cand[0]] / MLAT,
                        moved_km=round(d0 / 1000, 2)))

pd.DataFrame(log).to_csv(HERE / "locality_reassignments.csv", index=False)

# ---- host unit at the final position + is the point near a contact? ---------
ut = STRtree(units.geometry.values)


def host(x, y):
    g = points(x, y)
    idx = ut.query(g, predicate="intersects")
    if len(idx) == 0:
        idx = ut.query_nearest(g)
    if len(idx) == 0:
        return None, None
    u = units.iloc[int(idx[np.argmin(units.iloc[idx]["area_km2"].values)])]
    # distance to the unit BOUNDARY (0 would just mean "inside the polygon")
    return u["code"], gpd.GeoSeries([g], crs=units.crs).distance(u.geometry.boundary).iloc[0] * MLON


h = [host(x, y) for x, y in zip(out.geometry.x, out.geometry.y)]
out["host_code"] = [a for a, _ in h]
out["host_boundary_dist_m"] = [round(b, 0) if b is not None else None for _, b in h]
out["near_contact"] = [b is not None and b < 2000 for _, b in h]

# ---- accuracy summary ------------------------------------------------------
n = len(out)
summary = out.groupby("pos_method").agg(
    n=("pos_method", "size"),
    sigma_m=("pos_sigma_m", "first")).reset_index()
print(f"localities: {n}")
for _, r in summary.iterrows():
    print(f"  {r['pos_method']:44s} {r['n']:4d}  ({r['n'] / n * 100:4.1f}%)  sigma +-{r['sigma_m'] / 1000:.1f} km")
print(f"  median positional sigma now: +-{np.median(out['pos_sigma_m']) / 1000:.1f} km")
print(f"  points within 2 km of a geological contact: {int(out['near_contact'].sum())}")
if log:
    mv = np.array([l["moved_km"] for l in log])
    print(f"  reassigned {len(log)} points, moved median {np.median(mv):.1f} km (max {mv.max():.1f} km)")
    changed = sum(1 for i, r in out.iterrows()
                  if r["reassigned_from"] and r["host_code"] != loc.at[i, "host_code"])
    print(f"  host unit changed for {changed} of {len(log)} of them")

# ---- write -----------------------------------------------------------------
import sqlite3

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


for layer, gdf in (("mineral_localities_refined", out),
                   ("mineral_localities_utm32n", out.to_crs("EPSG:32632"))):
    drop_layer(GPKG, layer)
    try:
        gpd.GeoDataFrame(gdf.drop(columns=["m"]), geometry="geometry", crs="EPSG:4326" if "utm" not in layer else "EPSG:32632") \
            .to_file(GPKG, layer=layer, driver="GPKG", mode="a")
        print("wrote layer", layer)
    except Exception as e:
        print("could not append", layer, "->", e)
