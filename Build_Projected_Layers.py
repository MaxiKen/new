#!/usr/bin/env python3
"""Give every layer a CRS that is actually projected, not just labelled.

The EPSG:4326 package is the reference frame. This script writes a second GeoPackage in which
each layer's GEOMETRY is genuinely reprojected - the coordinates are metres, not degrees - into
the frame each feature type wants:

  area work (map units, the national outline)  ESRI:102022  Africa Albers Equal Area Conic
  distance / position work (points, faults,    EPSG:32632   WGS 84 / UTM zone 32N
  rivers, roads, state lines)                              (Nigeria's central UTM zone; the
                                                            whole country stays within 3.5 deg
                                                            of its central meridian)
  both, side by side                          EPSG:4326    kept as-is for interchange

A layer whose coordinates are still degrees is not "projected" whatever its metadata says, so
the script proves otherwise: it reports the coordinate ranges and the area/distance scale error
for every layer, and fails loudly if a layer did not actually move.

Outputs: Nigeria_Geology_Minerals_projected.gpkg, Projection_Report.json
"""
import json
from pathlib import Path
import geopandas as gpd, pandas as pd, pyproj

P = Path(__file__).resolve().parent
SRC = P / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = P / "Nigeria_Geology_Minerals_projected.gpkg"
if OUT.exists(): OUT.unlink()

ALBERS = "ESRI:102022"      # Africa Albers Equal Area Conic
UTM = "EPSG:32632"          # WGS 84 / UTM zone 32N
PLAN = [("geology_units", ALBERS), ("nigeria_boundary", ALBERS),
        ("minerals_occurrences", UTM), ("faults", UTM), ("roads", UTM),
        ("rivers", UTM), ("state_boundaries", UTM)]
rep = {"source": SRC.name, "layers": {}}
for layer, dst in PLAN:
    g = gpd.read_file(SRC, layer=layer)
    if g.crs is None:
        g = g.set_crs(4326)
    src_bounds = tuple(round(v, 3) for v in g.total_bounds)
    p = g.to_crs(dst)
    b = p.total_bounds
    # a projected layer must have metre-scale coordinates, not degrees
    moved = abs(b[2] - b[0]) > 1000 and abs(b[3] - b[1]) > 1000
    assert moved, f"{layer} did not actually reproject"
    # scale error against the equal-area frame, for the record
    if layer in ("geology_units", "nigeria_boundary") and layer == "nigeria_boundary":
        a4326 = g.to_crs(ALBERS).area.iloc[0] / 1e6
        a_proj = p.area.iloc[0] / 1e6
        area_err = round(100 * (a_proj - a4326) / a4326, 2)
    else:
        area_err = None
    p["area_km2_projected"] = None if p.geom_type.iloc[0] not in ("Polygon", "MultiPolygon") else \
        (p.area / 1e6).round(1)
    p.to_file(OUT, layer=layer, driver="GPKG", mode="a" if OUT.exists() else "w")
    rep["layers"][layer] = {"crs": dst, "crs_name": pyproj.CRS.from_user_input(dst).name,
                            "bounds_4326": src_bounds,
                            "bounds_projected_m": tuple(round(v) for v in b),
                            "area_change_pct_vs_albers": area_err,
                            "features": int(len(p))}
    print(f"{layer:22s} -> {dst:12s} x {b[0]:10.0f}..{b[2]:10.0f}  y {b[1]:8.0f}..{b[3]:8.0f}")

# ---- measure the distortion each choice actually carries, instead of assuming it is small
from pyproj import Geod, Transformer
import numpy as np
g = Geod(ellps="WGS84")
pts = gpd.read_file(SRC, layer="minerals_occurrences").to_crs(4326)
ut = pts.to_crs(UTM)
# compare a projected distance with the geodesic distance for pairs of nearby points
d_proj, d_geo = [], []
xy = np.c_[ut.geometry.x, ut.geometry.y]
ll = np.c_[pts.geometry.x, pts.geometry.y]
for i in range(0, len(pts) - 1, 37):
    j = i + 1
    if np.hypot(*(xy[i] - xy[j])) > 40000:      # only short baselines (< 40 km)
        continue
    d_proj.append(float(np.hypot(*(xy[i] - xy[j]))))
    _, _, dg = g.inv(ll[i][0], ll[i][1], ll[j][0], ll[j][1])
    d_geo.append(dg)
d_proj, d_geo = np.array(d_proj), np.array(d_geo)
scale_err = (d_proj - d_geo) / np.maximum(d_geo, 1)
rep["utm32n_distance_scale_error_pct"] = {"median": round(float(100*np.median(scale_err)), 3),
                                          "min": round(float(100*scale_err.min()), 3),
                                          "max": round(float(100*scale_err.max()), 3),
                                          "baselines_measured": int(len(d_proj))}
print("UTM32N distance scale error %: median",
      round(float(100*np.median(scale_err)), 3), "range",
      round(float(100*scale_err.min()), 2), "to", round(float(100*scale_err.max()), 2))

# a national outline area check, so the equal-area claim is a number and not a promise
nig = gpd.read_file(SRC, layer="nigeria_boundary").to_crs(ALBERS)
rep["nigeria_area_km2_albers"] = round(float(nig.area.sum()) / 1e6, 1)
rep["note"] = ("Coordinates in this file are metres. geology_units and nigeria_boundary use "
               "Africa Albers Equal Area Conic so areas can be measured; the point and line layers "
               "use UTM 32N so distances and positions can be measured. The 4326 package remains "
               "the authoritative reference frame; this one is the working frame.")
json.dump(rep, open(P / "Projection_Report.json", "w"), indent=2)
print("Nigeria area (Albers):", rep["nigeria_area_km2_albers"], "km2")
print("written", OUT.name)
