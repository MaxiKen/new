#!/usr/bin/env python3
"""Correct the mineral map's stored point coordinates.

Why: the 2023 sheet carries two mutually inconsistent coordinate definitions.
The printed graticule and the embedded GeoPDF /Measure give longitudes that differ
by ~0.172 degrees (about 19 km). The sheet's own vector artwork decides which one
is right: its international boundary reproduces the Natural Earth Nigeria border
with a 1.06 km median offset under the embedded measure, but 12.94 km under the
printed graticule. So the embedded measure is the frame the map was drawn in, and
the printed graticule is displaced. Stored mineral points were computed from the
printed graticule, hence they sit ~19 km too far west.

This script rewrites them into the embedded frame. It is a correction of an
internal inconsistency in one sheet, not a datum transformation, and it does not
make the sheet survey-accurate (guess: EPSG:4326 display assumption only).
"""
import csv, json, math
from pathlib import Path

P = Path(__file__).resolve().parent
SRC = P / "Minerals_Symbol_Points_source.csv"

# pixel -> PDF point (75 dpi artwork strips, 0.96 pt/px)
def px_to_pt(cx, cy): return 74.23969 + 0.96 * cx, 358.7239 + 0.96 * cy
# printed graticule (fitted earlier to the drawn meridians/parallels)
def printed(x, y): return (x + 288.95) / 157.5987, (2572.35 - y) / 157.6015
# embedded GeoPDF /Measure (WKT GCS_Assumed_Geographic_1)
def embedded(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)

rows = list(csv.DictReader(open(SRC)))
out, feats = [], []
for r in rows:
    x, y = px_to_pt(float(r["canvas_x"]), float(r["canvas_y"]))
    o_lon, o_lat = printed(x, y); n_lon, n_lat = embedded(x, y)
    # sanity: stored values must be the printed-graticule ones
    assert abs(float(r["lon"]) - o_lon) < 0.002 and abs(float(r["lat"]) - o_lat) < 0.002, r
    d = dict(r)
    d.update(lon_printed=round(o_lon, 6), lat_printed=round(o_lat, 6),
             lon=round(n_lon, 6), lat=round(n_lat, 6),
             shift_east_km=round((n_lon - o_lon) * 111.2 * math.cos(math.radians(o_lat)), 2),
             shift_north_km=round((n_lat - o_lat) * 111.2, 2),
             lon_was=float(r["lon"]), lat_was=float(r["lat"]))
    d.pop("geometry", None)
    out.append(d)
    feats.append({"type": "Feature", "properties": {k: v for k, v in d.items()},
                  "geometry": {"type": "Point", "coordinates": [d["lon"], d["lat"]]}})

fields = list(out[0].keys())
with open(P / "Minerals_Symbol_Points_CORRECTED.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
json.dump({"type": "FeatureCollection",
           "name": "Minerals_Symbol_Points_CORRECTED",
           "crs_note": "EPSG:4326 assigned as display assumption; original datum unverified",
           "source": "Mineral Resources Map of Nigeria, 2nd ed. 2023 (NGSA) glyphs, "
                     "rewritten from the printed graticule into the sheet's embedded "
                     "measure frame after the vector-boundary control in "
                     "Niger_Benue_Alignment_Report.md",
           "licence_note": "Coordinates derived from the printed sheet; check NGSA terms before redistribution",
           "features": feats},
          open(P / "Minerals_Symbol_Points_CORRECTED.geojson", "w"), separators=(",", ":"))
e = [r["shift_east_km"] for r in out]; n = [r["shift_north_km"] for r in out]
print(f"{len(out)} points rewritten")
print(f"east shift {min(e):.2f}..{max(e):.2f} km (median {sorted(e)[len(e)//2]:.2f})")
print(f"north shift {min(n):.2f}..{max(n):.2f} km (median {sorted(n)[len(n)//2]:.2f})")
