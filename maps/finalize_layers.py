#!/usr/bin/env python3
"""
Finalise the layers for calculation: stable IDs, lon/lat fields, flags, and
projection-ready copies.

What this fixes
---------------
1. `zone + number` is NOT unique in the source: 39 printed numbers are shared by
   two records (78 rows).  A stable `locality_id` is added, and duplicates are
   flagged with `shared_number`.
2. `mineral_localities_icons` carried geometry but no lon/lat columns; both are
   added and asserted equal to the geometry.
3. Three localities fall just outside the mapped landmass; `dist_to_coast_m`
   records how far, so they can be filtered.
4. Areas cannot be computed in EPSG:4326 (the result is square degrees).  Exact
   equal-area copies are written for the polygon and point layers.

CRS guidance for calculations
-----------------------------
    store / exchange          EPSG:4326        degrees, never for area
    area statistics           EPSG:6933        equal-area, exact (0.000 % error)
    distance, countrywide     geodesic metres  (pyproj.Geod on 4326)
    distance, local           EPSG:32631/2/3   one zone at a time: Nigeria spans
                                              31N (2.7-6 E), 32N (6-12 E), 33N (12-15 E)
    never                     EPSG:3857        +3.66 % area error over Nigeria

Outputs
    mineral_localities_icons          (rewritten, + locality_id, lon, lat, flags)
    mineral_localities_icons_utm32n   (rewritten)
    geology_units_equal_area          (EPSG:6933)
    mineral_localities_equal_area     (EPSG:6933)
    crs_qa_report.json
"""
import json
import pathlib
import sqlite3
import warnings

import geopandas as gpd
import numpy as np
import shapely
from pyproj import Geod

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
MLON = 111320 * np.cos(np.radians(9))
GEOID = Geod(ellps="WGS84")
EQ_AREA = "EPSG:6933"


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


def write(gdf, layer, crs):
    # reprojection can introduce self-intersections: repair before writing
    gdf = gdf.copy()
    gdf["geometry"] = shapely.make_valid(gdf.geometry.values)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
    drop_layer(GPKG, layer)
    gpd.GeoDataFrame(gdf, geometry="geometry", crs=crs).to_file(
        GPKG, layer=layer, driver="GPKG", mode="a")
    n_bad = int((~gdf.geometry.is_valid).sum())
    print(f"  wrote {layer:36s} {len(gdf):6d} features  (invalid after repair: {n_bad})")


icons = gpd.read_file(GPKG, layer="mineral_localities_icons").reset_index(drop=True)
units = gpd.read_file(GPKG, layer="geology_units")

# ---- stable id + shared-number flag ---------------------------------------
icons["locality_id"] = [
    f"{z}{n}" if dup == 0 else f"{z}{n}_{k + 1}"
    for (z, n), dup, k in zip(zip(icons["zone"], icons["number"]),
                              icons.groupby(["zone", "number"])["number"].transform("size") - 1,
                              icons.groupby(["zone", "number"]).cumcount())]
n_shared = int(icons["locality_id"].str.contains("_").sum())
icons["shared_number"] = icons["locality_id"].str.contains("_")

# ---- lon/lat as first-class fields ----------------------------------------
icons["lon"] = icons.geometry.x.round(7)
icons["lat"] = icons.geometry.y.round(7)
assert np.allclose(icons.lon.values, icons.geometry.x.values, atol=1e-7)
assert np.allclose(icons.lat.values, icons.geometry.y.values, atol=1e-7)

# ---- distance outside the mapped landmass ---------------------------------
land = shapely.union_all(units.geometry.values)
dist_out = np.array([
    GEOID.geometry_length(shapely.shortest_line(pt, land)) if not land.contains(pt) else 0.0
    for pt in icons.geometry])
icons["dist_to_coast_m"] = np.round(dist_out, 0)
n_off = int((dist_out > 0).sum())

order = ["locality_id", "zone", "number", "locality", "mineral_1", "group_1", "minerals",
         "n_minerals", "n_icons", "icon_tier", "icon_spread_m", "pos_method",
         "moved_from_label_m", "lon", "lat", "dist_to_coast_m", "shared_number",
         "host_code", "host_boundary_dist_m", "group_centroid_lon", "group_centroid_lat",
         "geometry"]
icons = icons[[c for c in order if c in icons.columns]]

write(icons, "mineral_localities_icons", "EPSG:4326")
write(icons.to_crs("EPSG:32632"), "mineral_localities_icons_utm32n", "EPSG:32632")
write(icons.to_crs(EQ_AREA), "mineral_localities_equal_area", EQ_AREA)

units_ea = units.to_crs(EQ_AREA)
units_ea["geometry"] = shapely.make_valid(units_ea.geometry.values)   # to_crs can self-intersect
units_ea["area_km2_equal_area"] = np.round(units_ea.area.values / 1e6, 3)
write(units_ea, "geology_units_equal_area", EQ_AREA)

# ---- QA report -------------------------------------------------------------
uni = land
true_area = abs(GEOID.geometry_area_perimeter(uni)[0]) / 1e6
areas = {}
for crs in ("EPSG:4326", EQ_AREA, "EPSG:3857", "EPSG:32632"):
    a = gpd.GeoSeries([uni], crs="EPSG:4326").to_crs(crs).iloc[0].area
    areas[crs] = round(a / 1e6, 3) if crs != "EPSG:4326" else round(a, 6)
    if crs != "EPSG:4326":
        areas[crs + "_error_pct"] = round(100 * (a / 1e6 - true_area) / true_area, 4)

layer_crs = {}
import pyogrio
for name, _ in pyogrio.list_layers(GPKG):
    g = gpd.read_file(GPKG, layer=name, rows=1)
    layer_crs[name] = g.crs.to_string() if g.crs else None

report = {
    "layers_total": len(layer_crs),
    "crs_by_layer": layer_crs,
    "all_layers_crs": sorted(set(v for v in layer_crs.values() if v)),
    "geodesic_area_km2": round(true_area, 1),
    "area_by_crs": areas,
    "locality_id_unique": bool(icons["locality_id"].is_unique),
    "localities": len(icons),
    "shared_printed_numbers": int(icons["shared_number"].sum()),
    "offshore_points": n_off,
    "max_dist_to_coast_m": float(np.max(dist_out)),
    "guidance": {
        "store": "EPSG:4326 (degrees) - never compute area in it",
        "area": f"{EQ_AREA} (equal area) - exact; geology_units_equal_area and "
                f"mineral_localities_equal_area are ready",
        "distance": "local: EPSG:32631/32632/32633 by zone; countrywide: geodesic",
        "avoid": "EPSG:3857 (+3.66 % area error over Nigeria)",
    },
}
json.dump(report, open(HERE / "crs_qa_report.json", "w"), indent=2)

print(f"\nlocality_id unique: {report['locality_id_unique']}")
print(f"records sharing a printed number: {report['shared_printed_numbers']}")
print(f"points outside the mapped landmass: {n_off} (max {dist_out.max()/1000:.1f} km)")
print(f"geodesic area {true_area:,.0f} km2 | 6933 {areas[EQ_AREA]:,.0f} | "
      f"3857 {areas['EPSG:3857']:,.0f} ({areas['EPSG:3857_error_pct']:+.2f}%) | "
      f"32632 {areas['EPSG:32632']:,.0f} ({areas['EPSG:32632_error_pct']:+.3f}%)")
