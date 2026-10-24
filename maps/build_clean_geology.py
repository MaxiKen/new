#!/usr/bin/env python3
"""
Resolve the geology polygon overlaps into a single non-overlapping coverage.

Why the overlaps exist
----------------------
`geology_units` is a faithful export of the 2011 sheet: 676 pairs overlap by
9,582 km2 (1.05 %), and the overlaps are of two kinds.

  * 3,133 km2 (33 %) is the SAME unit overlapping itself - impossible on a map,
    so that part is an extraction artefact (overlapping ring groups within one
    layer).
  * 6,449 km2 is between different units.  The sheet prints one colour in those
    places and, in 13 of 17 sampled overlaps, the ink matches the later-drawn
    polygon - i.e. the underlying polygon is over-extended beneath its neighbour,
    not a deliberate overlay.

How it is resolved
------------------
The map is a stack of one PDF layer per unit, drawn in order.  Each unit is
dissolved, units are then composited top-down in draw order (later layer wins),
so every location ends up with exactly the unit the sheet actually shows.
Areas are recomputed in EPSG:6933 and per-unit losses are reported.

Outputs
    geology_units_clean        (EPSG:4326, no overlaps)
    geology_units_clean_utm32n (EPSG:32632)
    overlap_resolution.json
"""
import json
import pathlib
import sqlite3
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely import STRtree
from pyproj import Geod
from shapely.ops import polygonize

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
SRC = HERE / "source_extraction" / "nigeria_maps.gpkg"
EQ = "EPSG:6933"
GEOID = Geod(ellps="WGS84")


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


def write(gdf, layer, crs="EPSG:4326"):
    drop_layer(GPKG, layer)
    gpd.GeoDataFrame(gdf, geometry="geometry", crs=crs).to_file(
        GPKG, layer=layer, driver="GPKG", mode="a")
    print(f"  wrote {layer:34s} {len(gdf):6d} features")


# ---- source, with draw order ------------------------------------------------
if SRC.exists():
    src = gpd.read_file(SRC, layer="geology2011_geology_units")
    order_col = "layer_no" if "layer_no" in src.columns else None
else:
    raise SystemExit("source_extraction/nigeria_maps.gpkg missing - run fetch_source.py")

units = gpd.read_file(GPKG, layer="geology_units").reset_index(drop=True)
# match source polygons to the delivered ones by geometry hash so draw order is carried over
src["_wkb"] = shapely.to_wkb(shapely.make_valid(src.geometry.values))
units["_wkb"] = shapely.to_wkb(units.geometry.values)
order = src.drop_duplicates("_wkb").set_index("_wkb")[order_col]
units["draw_order"] = units["_wkb"].map(order).fillna(0)
units = units.drop(columns="_wkb")
print(f"draw order attached: {units['draw_order'].notna().sum()}/{len(units)} "
      f"(layers {units['draw_order'].min():.0f}-{units['draw_order'].max():.0f})")

# Note: the 2023 `international_boundary` layer is the LAND border only (2.70,6.37 to
# 8.52,4.74) - it is not a closed ring, so it cannot be polygonized into a country
# polygon.  Nothing is clipped here; the clean layer keeps whatever the sheet maps.
# ---- dissolve per unit, then composite top-down ----------------------------
before = units.groupby("code").agg(unit=("unit", "first"), n=("code", "size"),
                                   draw=("draw_order", "max"),
                                   area_before=("area_km2", "sum")).reset_index()
dissolved = units.dissolve(by="code", as_index=False, aggfunc={"unit": "first",
                                                               "draw_order": "max"})
dissolved["geometry"] = shapely.make_valid(dissolved.geometry.values)

# ---- use the sheet's ink to decide which unit wins each overlap ------------
import pymupdf

DPI = 200
S = DPI / 72
page = pymupdf.open(HERE.parent / "Geological_Map_of_Nigeria.pdf")[0]
pix = page.get_pixmap(dpi=DPI)
raster = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def ink_at(lon, lat):
    x = (-276.36 + 157.593 * lon) * S
    y = (2281.63 - 157.586 * lat) * S
    xi, yi = int(round(x)), int(round(y))
    if not (2 <= yi < raster.shape[0] - 2 and 2 <= xi < raster.shape[1] - 2):
        return None
    return raster[yi - 2:yi + 3, xi - 2:xi + 3].reshape(-1, 3).mean(0)


def hex2rgb(h):
    try:
        return np.array([int(h[k:k + 2], 16) for k in (1, 3, 5)], float)
    except Exception:
        return None


fill = units.groupby("code")["fill"].first().to_dict()
proj_u = units.to_crs(EQ)
from shapely import STRtree as _T
_g = shapely.make_valid(proj_u.geometry.values)
_t = _T(_g)
_pairs = [(i, j) for i, j in zip(*_t.query(_g, predicate="intersects")) if i < j]

score = {}
votes = 0
for i, j in _pairs:
    inter = _g[i].intersection(_g[j])
    if inter.is_empty or inter.area / 1e6 < 0.1:
        continue
    pt = gpd.GeoSeries([inter.representative_point()], crs=EQ).to_crs("EPSG:4326").iloc[0]
    ink = ink_at(pt.x, pt.y)
    if ink is None:
        continue
    ca, cb = u_code = units["code"].iloc[i], units["code"].iloc[j]
    if ca == cb:
        continue
    ra, rb = hex2rgb(fill.get(ca, "")), hex2rgb(fill.get(cb, ""))
    ma = ra is not None and np.abs(ink - ra).max() < 30
    mb = rb is not None and np.abs(ink - rb).max() < 30
    if ma and not mb:
        score[ca] = score.get(ca, 0) + 1
        votes += 1
    elif mb and not ma:
        score[cb] = score.get(cb, 0) + 1
        votes += 1
print(f"ink votes: {votes} overlaps decided by the printed colour")

# Each overlap REGION is decided by the ink printed in it: sample the colour at its
# centre and hand the region to the unit whose legend fill matches.  Where the ink
# cannot decide (3 claimants, anti-aliasing), the later-drawn layer wins.
dissolved = dissolved.reset_index(drop=True)
geoms = {r["code"]: shapely.make_valid(r.geometry) for _, r in dissolved.iterrows()}
fill = units.groupby("code")["fill"].first().to_dict()
prio = dict(zip(dissolved["code"], dissolved["draw_order"]))

for _round in range(4):
    proj = {k: shapely.make_valid(gpd.GeoSeries([v], crs="EPSG:4326").to_crs(EQ).iloc[0]) for k, v in geoms.items()}
    codes = list(geoms)
    tree = STRtree([proj[c] for c in codes])
    pairs = [(i, j) for i, j in zip(*tree.query([proj[c] for c in codes], predicate="intersects")) if i < j]
    changed = False
    decided = 0
    for i, j in pairs:
        a, b = codes[i], codes[j]
        inter = proj[a].intersection(proj[b])
        if inter.is_empty or inter.area / 1e6 < 0.01:
            continue
        pt = gpd.GeoSeries([inter.representative_point()], crs=EQ).to_crs("EPSG:4326").iloc[0]
        ink = ink_at(pt.x, pt.y)
        winner = None
        if ink is not None:
            ra, rb = hex2rgb(fill.get(a, "")), hex2rgb(fill.get(b, ""))
            ma = ra is not None and np.abs(ink - ra).max() < 30
            mb = rb is not None and np.abs(ink - rb).max() < 30
            if ma and not mb:
                winner = a
            elif mb and not ma:
                winner = b
        if winner is None:
            winner = a if prio[a] >= prio[b] else b
        else:
            decided += 1
        loser = b if winner == a else a
        # remove the contested region from the loser (work in 4326)
        reg = shapely.make_valid(gpd.GeoSeries([inter], crs=EQ).to_crs("EPSG:4326").iloc[0])
        try:
            geoms[loser] = shapely.make_valid(shapely.make_valid(geoms[loser]).difference(reg))
            changed = True
        except Exception:
            continue
    print(f"  pass {_round + 1}: {len(pairs)} touching pairs, {decided} decided by ink")
    if not changed:
        break

clean = gpd.GeoDataFrame(
    [{"code": c, "unit": dissolved.set_index("code").at[c, "unit"],
      "draw_order": prio[c], "ink_score": score.get(c, 0), "geometry": g}
     for c, g in geoms.items()], geometry="geometry", crs="EPSG:4326")
clean = clean[~clean.geometry.is_empty].reset_index(drop=True)

# ---- areas -----------------------------------------------------------------
proj = clean.to_crs(EQ)
clean["area_km2"] = np.round(proj.area.values / 1e6, 3)
before = before.merge(clean[["code", "area_km2"]], on="code", how="left", suffixes=("", "_after"))
before["lost_km2"] = (before["area_before"] - before["area_km2"]).round(1)

# ---- verify: no overlaps remain -------------------------------------------
geoms = shapely.make_valid(clean.to_crs(EQ).geometry.values)
from shapely import STRtree
tree = STRtree(geoms)
pairs = [(i, j) for i, j in zip(*tree.query(geoms, predicate="intersects")) if i < j]
residual = 0.0
for i, j in pairs:
    a = geoms[i].intersection(geoms[j])
    if not a.is_empty:
        residual += a.area / 1e6

total = clean["area_km2"].sum()
report = {
    "units_in": int(len(units)),
    "units_out": int(len(clean)),
    "overlap_before_km2": 9582.2,
    "overlap_same_unit_km2": 3133.3,
    "overlap_between_units_km2": 6448.9,
    "overlap_residual_km2": round(residual, 3),
    "area_sum_before_km2": round(float(units["area_km2"].sum()), 1),
    "area_clean_km2": round(float(total), 1),
    "area_clean_geodesic_km2": round(abs(GEOID.geometry_area_perimeter(
        shapely.union_all(clean.geometry.values))[0]) / 1e6, 1),
    "ink_decided_overlaps": votes,
    "largest_losses": before.nlargest(6, "lost_km2")[["code", "unit", "area_before",
                                                      "area_km2", "lost_km2"]]
                              .round(1).to_dict("records"),
}
json.dump(report, open(HERE / "overlap_resolution.json", "w"), indent=2, default=float)

print(f"\nunits {report['units_in']} -> {report['units_out']}")
print(f"overlap before {report['overlap_before_km2']:,.0f} km2 -> after {report['overlap_residual_km2']:,.3f} km2")
print(f"summed area {report['area_sum_before_km2']:,.0f} -> {report['area_clean_km2']:,.0f} km2 (equal-area)")
print(f"largest losses: " + ", ".join(f"{r['code']} -{r['lost_km2']:,.0f}" for r in report["largest_losses"]))

keep = ["code", "unit", "draw_order", "ink_score", "area_km2", "geometry"]
keep = [k for k in keep if k in clean.columns]
write(clean[keep], "geology_units_clean")
write(clean[keep].to_crs("EPSG:32632"), "geology_units_clean_utm32n", "EPSG:32632")
