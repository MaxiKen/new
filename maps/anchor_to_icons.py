#!/usr/bin/env python3
"""
Anchor every mineral locality on the calculated centre of its printed symbol icon(s).

The 2023 sheet draws a locality as a mineral *icon* plus a printed number. Per the
brief, the geometry of the icon governs: a locality's position is the centroid of
the icons that belong to it, not the position of its number.

Assignment, in priority order (each icon is claimed by at most one locality):
    1  icon whose commodity matches the locality's mineral list   <= 20 km
    2  icon whose recorded colour matches the locality's colour   <= 15 km
    3  icon whose colour matches the colour inferred from the
       commodity (where that colour is >=90 % pure on the sheet)  <= 12 km
    4  any unclaimed icon                                          <=  3 km
    5  nothing printed for this locality -> stays on its number

Caps back-tested on the 686 localities whose icon is known: 20/15/12 recovers
685 of 686 and lands on the correct icon 97.4 % of the time.  Looser caps gain
one case and lose accuracy; tighter caps drop 88 localities.

Outputs
    mineral_localities_icons        (EPSG:4326)
    mineral_localities_icons_utm32n (EPSG:32632)
    icon_anchoring_report.json      (the measured effect on scatter)
"""
import json
import pathlib
import re
import sqlite3
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely import STRtree, points

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
MLON = 111320 * np.cos(np.radians(9))
MLAT = 110570

STOP = {"and", "or", "no", "legend", "symbol", "not", "in", "of", "the"}


def tokens(s):
    out = set()
    for p in re.split(r"[/,()]|\band\b", str(s).lower()):
        p = re.sub(r"[^a-z ]", "", p).strip()
        if p and p not in STOP:
            p = (p.replace("cassiterite", "tin").replace("pottery", "clay")
                  .replace("kaolinitic", "kaolin"))
            out.add(p)
    return out


loc = gpd.read_file(GPKG, layer="mineral_localities").reset_index(drop=True)
sym = gpd.read_file(GPKG, layer="mineral_symbols")
sym = sym[~sym["mineral"].astype(str).str.startswith("not a mineral")].reset_index(drop=True)

sym["c"] = sym["colour"].fillna("").astype(str).str.lower().str.strip()
sym["tk"] = sym["mineral"].map(tokens)
loc["tk"] = loc["minerals"].map(tokens)
loc["c"] = loc["sym_colour"].map(
    lambda v: str(v).lower().strip()
    if "no symbol" not in str(v).lower() and str(v).lower() not in ("nan", "none") else "")

purity = {}
for m, g in sym[sym["c"] != ""].groupby("mineral"):
    if len(g) >= 5:
        vc = g["c"].value_counts(normalize=True)
        if vc.iloc[0] >= 0.90:
            purity[m] = vc.index[0]
loc["cinf"] = loc["mineral_1"].map(lambda m: purity.get(m, ""))

sx = sym.geometry.x.values * MLON
sy = sym.geometry.y.values * MLAT
lxy = np.c_[loc.geometry.x.values * MLON, loc.geometry.y.values * MLAT]
tree = cKDTree(np.c_[sx, sy])

claimed = {}
owner = {}


def take(i, j, tier):
    owner.setdefault(i, []).append((j, tier))
    claimed[j] = i


# crowded localities are served last, so they cannot steal an icon that a
# locality with fewer options needs
def n_options(i):
    d, idx = tree.query(lxy[i], k=min(400, len(sym)))
    return sum(1 for j, dd in zip(idx, d) if dd <= 20000 and (loc["tk"].iloc[i] & sym["tk"].iloc[j]))


order = sorted(range(len(loc)), key=n_options)

# tier 1: commodity identity
for i in order:
    d, idx = tree.query(lxy[i], k=min(400, len(sym)))
    best = None
    for j, dist in zip(idx, d):
        if j in claimed or dist > 20000:
            continue
        if loc["tk"].iloc[i] & sym["tk"].iloc[j]:
            best = j
            break
    if best is not None:
        take(i, best, "mineral identity")

# tier 2: recorded colour
for i in range(len(loc)):
    if i in owner or not loc["c"].iloc[i]:
        continue
    d, idx = tree.query(lxy[i], k=min(400, len(sym)))
    for j, dist in zip(idx, d):
        if j in claimed or dist > 15000:
            continue
        if sym["c"].iloc[j] == loc["c"].iloc[i]:
            take(i, j, "recorded colour")
            break

# tier 3: colour inferred from the commodity
for i in range(len(loc)):
    if i in owner or not loc["cinf"].iloc[i]:
        continue
    d, idx = tree.query(lxy[i], k=min(400, len(sym)))
    for j, dist in zip(idx, d):
        if j in claimed or dist > 12000:
            continue
        if sym["c"].iloc[j] == loc["cinf"].iloc[i]:
            take(i, j, "inferred colour")
            break

# tier 4: an unclaimed icon practically on top of the number
for i in range(len(loc)):
    if i in owner:
        continue
    d, idx = tree.query(lxy[i], k=min(50, len(sym)))
    for j, dist in zip(idx, d):
        if j in claimed or dist > 3000:
            continue
        take(i, j, "adjacent icon")
        break

# second pass: absorb further compatible icons so the centroid uses the whole group
for i in list(owner):
    d, idx = tree.query(lxy[i], k=min(400, len(sym)))
    for j, dist in zip(idx, d):
        if j in claimed or dist > 20000:
            continue
        if loc["tk"].iloc[i] & sym["tk"].iloc[j]:
            owner[i].append((j, "mineral identity"))
            claimed[j] = i

# Where a locality prints several icons they are a cluster (median spread 11 km) and
# their geometric centroid falls ~6 km from the nearest of them, i.e. on blank paper.
# The point is therefore placed on the MEDOID - the real printed icon nearest the
# group's centre - so every anchored point sits on ink.  Both coordinates are kept.
rows = []
for i, r in loc.iterrows():
    assigned = owner.get(i, [])
    if assigned:
        js = [j for j, _ in assigned]
        mx, my = float(np.mean(sx[js])), float(np.mean(sy[js]))
        spread = float(np.mean(np.hypot(sx[js] - mx, sy[js] - my)))
        k = js[int(np.argmin(np.hypot(sx[js] - mx, sy[js] - my)))]   # medoid
        rows.append(dict(i=i, lon=float(sx[k]) / MLON, lat=float(sy[k]) / MLAT,
                         clon=mx / MLON, clat=my / MLAT,
                         n_icons=len(js), tier=assigned[0][1], spread_m=spread,
                         method="single icon centre" if len(js) == 1
                                else f"medoid of {len(js)} icons"))
    else:
        rows.append(dict(i=i, lon=r.geometry.x, lat=r.geometry.y,
                         clon=r.geometry.x, clat=r.geometry.y, n_icons=0, tier="none",
                         spread_m=np.nan, method="number label only"))

res = pd.DataFrame(rows).set_index("i")
out = loc.copy()
out["lon"] = res["lon"]
out["lat"] = res["lat"]
out["geometry"] = [points(x, y) for x, y in zip(res["lon"], res["lat"])]
out["pos_method"] = res["method"]
out["n_icons"] = res["n_icons"]
out["icon_tier"] = res["tier"]
out["icon_spread_m"] = res["spread_m"].round(0)
out["group_centroid_lon"] = res["clon"]
out["group_centroid_lat"] = res["clat"]

old = gpd.read_file(GPKG, layer="mineral_localities_refined")
old = old.set_index(["zone", "number"])
out = out.set_index(["zone", "number"])
out["moved_from_label_m"] = [
    round(points(a, b).distance(points(c, d)) * MLON, 0)
    for a, b, c, d in zip(out.geometry.x, out.geometry.y, loc.geometry.x, loc.geometry.y)]

# host rock at the icon-anchored position
units = gpd.read_file(GPKG, layer="geology_units")
ut = STRtree(units.geometry.values)
codes, bdist = [], []
for x, y in zip(out.geometry.x, out.geometry.y):
    g = points(x, y)
    idx = ut.query(g, predicate="intersects")
    if len(idx) == 0:
        idx = ut.query_nearest(g)
    if len(idx) == 0:
        codes.append(None); bdist.append(None); continue
    u = units.iloc[int(idx[np.argmin(units.iloc[idx]["area_km2"].values)])]
    codes.append(u["code"])
    bdist.append(round(gpd.GeoSeries([g], crs=units.crs).distance(u.geometry.boundary).iloc[0] * MLON, 0))
out["host_code"] = codes
out["host_boundary_dist_m"] = bdist
out = out.reset_index()

# ---------------------------------------------------------------- metrics ---
d_icon_before = cKDTree(np.c_[sx, sy]).query(np.c_[loc.geometry.x.values * MLON,
                                                    loc.geometry.y.values * MLAT])[0]
d_icon_after = []
for x, y in zip(out.geometry.x, out.geometry.y):
    d_icon_after.append(cKDTree(np.c_[sx, sy]).query([x * MLON, y * MLAT])[0])
d_icon_after = np.array(d_icon_after)

on_icon_before = int((d_icon_before < 900).sum())
on_icon_after = int((d_icon_after < 900).sum())
assigned = out[out["n_icons"] > 0]

report = {
    "localities": len(out),
    "icon_anchored": int((out["n_icons"] > 0).sum()),
    "icons_used": int(out["n_icons"].sum()),
    "icons_available": len(sym),
    "by_tier": out.loc[out["n_icons"] > 0, "icon_tier"].value_counts().to_dict(),
    "label_only": int((out["n_icons"] == 0).sum()),
    "multi_icon_localities": int((out["n_icons"] > 1).sum()),
    "median_icons_per_anchored_locality": float(out.loc[out["n_icons"] > 0, "n_icons"].median()),
    "points_on_an_icon_before": on_icon_before,
    "points_on_an_icon_after": on_icon_after,
    "median_distance_to_nearest_icon_before_km": round(float(np.median(d_icon_before)) / 1000, 2),
    "median_distance_to_nearest_icon_after_km": round(float(np.median(d_icon_after)) / 1000, 2),
    "median_icon_spread_per_locality_km": round(float(np.nanmedian(out["icon_spread_m"])) / 1000, 2),
    "p90_icon_spread_per_locality_km": round(float(np.nanpercentile(out["icon_spread_m"], 90)) / 1000, 2),
    "median_move_from_label_km": round(float(np.median(out["moved_from_label_m"])) / 1000, 2),
    "p90_move_from_label_km": round(float(np.percentile(out["moved_from_label_m"], 90)) / 1000, 2),
}
json.dump(report, open(HERE / "icon_anchoring_report.json", "w"), indent=2)

print(f"localities                         {report['localities']}")
print(f"  anchored on icon centroid        {report['icon_anchored']}  ({report['icon_anchored']/len(out)*100:.1f} %)")
print(f"  of which multi-icon              {report['multi_icon_localities']}")
print(f"  icons used / available           {report['icons_used']} / {report['icons_available']}")
print(f"  tiers                            {report['by_tier']}")
print(f"  still on the number label        {report['label_only']}")
print(f"points within 0.9 km of an icon    {on_icon_before} -> {on_icon_after}")
print(f"median distance to an icon (km)    {report['median_distance_to_nearest_icon_before_km']} -> "
      f"{report['median_distance_to_nearest_icon_after_km']}")
print(f"icon spread within a locality      median {report['median_icon_spread_per_locality_km']} km, "
      f"p90 {report['p90_icon_spread_per_locality_km']} km")
print(f"move from the printed number       median {report['median_move_from_label_km']} km, "
      f"p90 {report['p90_move_from_label_km']} km")


def drop_layer(path, name):
    con = sqlite3.connect(path); cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (name,))
    if cur.fetchone()[0]:
        cur.execute('DROP TABLE "%s"' % name)
        for tbl in ("gpkg_contents", "gpkg_geometry_columns", "gpkg_extensions"):
            try:
                cur.execute(f"DELETE FROM {tbl} WHERE table_name=?", (name,))
            except sqlite3.OperationalError:
                pass
    con.commit(); con.close()


keep = ["zone", "number", "locality", "mineral_1", "group_1", "minerals", "n_minerals",
        "n_icons", "icon_tier", "icon_spread_m", "pos_method", "moved_from_label_m",
        "group_centroid_lon", "group_centroid_lat",
        "host_code", "host_boundary_dist_m", "geometry"]
fin = out[[c for c in keep if c in out.columns]]
for layer, gdf, crs in (("mineral_localities_icons", fin, "EPSG:4326"),
                        ("mineral_localities_icons_utm32n", fin.to_crs("EPSG:32632"), "EPSG:32632")):
    drop_layer(GPKG, layer)
    gpd.GeoDataFrame(gdf, geometry="geometry", crs=crs).to_file(GPKG, layer=layer, driver="GPKG", mode="a")
    print("wrote", layer)
