#!/usr/bin/env python3
"""Recompute `crs_qa_report.json` from the shipped file.

The report is written by `finalize_layers.py` during a build, so it describes the
file as it was at that moment: it still said 27 layers when the file had 31, and
its "avoid EPSG:3857 (+3.66 %)" guidance disagreed with the 3.6831 % it had
measured in the same file. This recomputes every field from the GeoPackage that
ships, so the evidence file cannot drift from the data it describes.

Run:  python refresh_crs_report.py
"""
import json
import pathlib

import geopandas as gpd
import numpy as np
import pyogrio
from pyproj import Geod

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "crs_qa_report.json"
EQ_AREA = "EPSG:6933"
COPIES = HERE / "Nigeria_Geology_Minerals_projected_copies.gpkg"
GEOID = Geod(ellps="WGS84")

old = json.load(open(OUT)) if OUT.exists() else {}

terr = gpd.read_file(GPKG, layer="national_territory")
land = terr.geometry.iloc[0]
true_area = abs(GEOID.geometry_area_perimeter(land)[0]) / 1e6

areas = {}
for crs in ("EPSG:4326", EQ_AREA, "EPSG:3857", "EPSG:32632"):
    a = gpd.GeoSeries([land], crs="EPSG:4326").to_crs(crs).iloc[0].area
    areas[crs] = round(a, 6) if crs == "EPSG:4326" else round(a / 1e6, 3)
    if crs != "EPSG:4326":
        areas[crs + "_error_pct"] = round(100 * (a / 1e6 - true_area) / true_area, 4)

layer_crs = {}
for name, _ in pyogrio.list_layers(GPKG):
    g = gpd.read_file(GPKG, layer=name, rows=1)
    layer_crs[name] = g.crs.to_string() if g.crs else None

# the five reprojections are in their own file; record what they are, from that file
copies = {}
if COPIES.exists():
    for n, _ in pyogrio.list_layers(COPIES):
        info = pyogrio.read_info(COPIES, layer=n)
        copies[n] = dict(crs=info["crs"], features=info["features"])

icons = gpd.read_file(GPKG, layer="mineral_localities_icons")
offshore = icons[icons["dist_to_coast_m"] > 0]

report = {
    "layers_total": len(layer_crs),
    "crs_by_layer": layer_crs,
    "all_layers_crs": sorted(set(v for v in layer_crs.values() if v)),
    "geodesic_area_km2": round(true_area, 1),
    "area_by_crs": areas,
    "locality_id_unique": bool(icons["locality_id"].is_unique),
    "localities": len(icons),
    "shared_printed_numbers": int(icons["shared_number"].sum()),
    "offshore_points": int(len(offshore)),
    "max_dist_to_coast_m": float(np.max(offshore["dist_to_coast_m"])) if len(offshore) else 0.0,
    "projected_copies_file": COPIES.name if copies else None,
    "projected_copies": copies,
    "guidance": {
        "store": "EPSG:4326 (degrees) - never compute area in it",
        "area": f"{EQ_AREA} (equal area) - exact; to_crs('{EQ_AREA}') on the 4326 "
                f"layers, or the stored copies in {COPIES.name}",
        "distance": "local: EPSG:32631/32632/32633 by zone; countrywide: geodesic",
        "single_crs": "the deliverable is EPSG:4326 throughout, so layers can be laid "
                      "on each other; the 6933/32632 reprojections live in "
                      "Nigeria_Geology_Minerals_projected_copies.gpkg",
        # computed, not typed: this line used to disagree with the figure above it
        "avoid": f"EPSG:3857 (+{areas['EPSG:3857_error_pct']:.2f} % area error over Nigeria)",
    },
}
json.dump(report, open(OUT, "w"), indent=2)

changed = {k: (old.get(k), report[k]) for k in report
           if json.dumps(old.get(k), sort_keys=True) != json.dumps(report[k], sort_keys=True)}
print(f"{len(layer_crs)} layers, {len(set(layer_crs.values()))} CRS, "
      f"geodesic area {true_area:,.1f} km2")
for k, (a, b) in changed.items():
    print(f"  {k}: {str(a)[:60]} -> {str(b)[:60]}")
print(f"\nwrote {OUT.name}")
