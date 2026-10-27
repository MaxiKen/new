#!/usr/bin/env python3
"""Recompute the gazetteer's published counters from the layer as it ships.

`towns_report.json` is written by `build_towns.py` while the layer is being
built. Some of its counters then stopped being true, because `repair_layers.py`
ran afterwards and took the state name from the repaired polygons and recomputed
`state_agree`:

    geonames_state_vs_polygon   build: 31,486 compared / 29,476 agree / 93.6 %
                                shipped layer: 31,913 / 29,903 / 93.7 %

A published evidence file that contradicts the data it describes is worse than no
file, so this recomputes every layer-derived field from the GeoPackage and keeps
the build-time value of anything that changed under `as_built`. Nothing is
overwritten and nothing is deleted: the difference between the two runs is the
record of what the repairs changed.

One counter is deliberately *not* recomputed. `state_from_polygon` counted the
rows that fell inside a Natural Earth admin-1 polygon; the join source is not in
the GeoPackage, so it cannot be re-derived, and the 427 rows that carry GeoNames'
own state instead are why it is smaller than `with_state`. It is kept and
labelled rather than silently replaced by a number that measures something else.

The spot check against published city coordinates is reproduced too, from the
same `KNOWN` table the build used, so it can be seen to still hold.

Run:  python refresh_towns_report.py
"""
import json
import pathlib

import geopandas as gpd
import numpy as np
from pyproj import Geod
from shapely.ops import nearest_points

from build_towns import KNOWN, NG_AEQD

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "towns_report.json"
GEOID = Geod(ellps="WGS84")

t = gpd.read_file(GPKG, layer="towns_geonames")
old = json.load(open(OUT))
rep = dict(old)
as_built = {}

# ---- the counters that describe the layer ---------------------------------
new = {
    "features": int(len(t)),
    "feature_codes": {k: int(v) for k, v in t.feature_code.value_counts().items()},
    "inside_national_territory": int(t.in_nigeria.sum()),
    "inside_pct": round(100 * float(t.in_nigeria.mean()), 1),
    "with_state": int(t.state.notna().sum()),
    "with_state_pct": round(100 * float(t.state.notna().mean()), 1),
    "with_population": int((t.population > 0).sum()),
    "duplicate_spellings": int(t.dup_group.notna().sum()),
}
for k, v in new.items():
    if old.get(k) != v:
        as_built[k] = old.get(k)
    rep[k] = v

# `state_from_polygon` cannot be re-derived from the file - see the docstring
if "state_from_polygon" in old:
    for k in ("state_from_polygon", "state_from_polygon_pct"):
        as_built[k] = old.get(k)
        rep.pop(k, None)
rep["state_name_source"] = dict(
    note="`with_state` counts every row that carries a state name: from the state "
         "polygons where the point falls in one, from GeoNames' own field otherwise")

new_pairs = {
    "geonames_state_vs_polygon": dict(
        compared=int(t.state_agree.notna().sum()),
        agree=int((t.state_agree == 1).sum()),
        disagree=int((t.state_agree == 0).sum()),
        agree_pct=round(100 * float(t.state_agree.mean()), 1),
        not_comparable=int(t.state_agree.isna().sum())),
}
for k, v in new_pairs.items():
    if old.get(k) != v:
        as_built[k] = old.get(k)
    rep[k] = v

# ---- the spot check against published coordinates -------------------------
cities = {}
for city, (lat, lon) in KNOWN.items():
    g = t[t.name.str.lower() == city.lower()]
    if not len(g):
        continue
    _, _, d = GEOID.inv(np.full(len(g), lon), np.full(len(g), lat),
                        g.geometry.x.values, g.geometry.y.values)
    cities[city] = round(float(np.min(d)) / 1000, 2)
want = dict(cities=cities,
            median_km=round(float(np.median(list(cities.values()))), 2),
            worst_km=max(cities.values()),
            worst_city=max(cities, key=cities.get),
            note="distance from each published coordinate to the nearest gazetteer "
                 "place of that name; KNOWN in build_towns.py")
if (old.get("spot_check") or {}).get("cities") != cities:
    as_built["spot_check"] = old.get("spot_check")
rep["spot_check"] = want

# ---- outside the territory ------------------------------------------------
# measured in the same equidistant projection the build used, so the number is
# comparable with the one it replaces
out = t[~t.in_nigeria]
if len(out):
    terr = gpd.read_file(GPKG, layer="national_territory").geometry.iloc[0]
    terr_m = gpd.GeoSeries([terr], crs=4326).to_crs(NG_AEQD).iloc[0]
    dist = out.to_crs(NG_AEQD).geometry.distance(terr_m) / 1000
    for k, v in {"outside_territory": int(len(out)),
                 "outside_territory_median_km": round(float(dist.median()), 2),
                 "outside_territory_max_km": round(float(dist.max()), 2)}.items():
        if old.get(k) != v:
            as_built[k] = old.get(k)
        rep[k] = v

if as_built:
    rep["as_built"] = dict(
        superseded=as_built,
        note="what build_towns.py measured at build time. The repairs that followed "
             "(state name from the repaired polygons, state_agree recomputed) changed "
             "these; the values above are recomputed from the shipped layer by "
             "refresh_towns_report.py. Nothing was deleted.")
json.dump(rep, open(OUT, "w"), indent=1)

print(f"recomputed {len(new) + len(new_pairs) + 3} layer-derived field(s) from the shipped layer")
for k in ("features", "inside_national_territory", "inside_pct", "with_state",
          "with_state_pct", "with_population"):
    print(f"  {k:26s} {rep[k]}")
print(f"  state agreement            {rep['geonames_state_vs_polygon']}")
print(f"  spot check                 median {rep['spot_check']['median_km']} km, "
      f"worst {rep['spot_check']['worst_km']} km ({rep['spot_check']['worst_city']})")
if as_built:
    print(f"\nkept {len(as_built)} superseded build-time value(s) under `as_built`")
    for k, v in as_built.items():
        print(f"  {k}: {str(v)[:70]}")
print(f"\nwrote {OUT.name}")
