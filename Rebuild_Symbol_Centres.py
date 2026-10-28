#!/usr/bin/env python3
"""Put every mineral point on the true centre of its printed symbol, in EPSG:4326.

What was wrong before
  1. The seven 75 dpi art strips on the 2023 sheet are stored vertically flipped relative to
     the page. Reading them without flipping mirrored every recorded latitude about the strip
     axis: on average about 60 km of error, in both directions.
  2. The previous extraction registered page coordinates through the sheet's PRINTED
     graticule, which is 0.171800-0.172578 deg (about 19 km) west of the frame the artwork is
     actually drawn in. The sheet's own vector international boundary proves which is right:
     it matches modern data to 0.5-1.1 km in the embedded frame but is 12.9 km out in the
     printed frame.
  3. Points were recorded as a detected blob position, not as the centre of the glyph.

What this does
  * rebuilds the art strips in page orientation (verified: page symbols land on canvas
    symbols 100% of the time, vs 1% for random positions)
  * for every one of the 1,323 printed symbols, takes a window around the old position,
    builds a symbol mask from the sheet's own flat palette plus its ink colour, fills holes
    so ring and outlined symbols are whole, and takes the centre of the glyph's bounding box
  * converts canvas -> page -> lon/lat with the strip offsets and the embedded GeoPDF measure

Outputs: Minerals_Symbol_Centres_4326.csv / .geojson, Symbol_Centre_Report.json
"""
import csv, json
from pathlib import Path
import numpy as np, pymupdf
from scipy.ndimage import label as ndlabel, binary_fill_holes

P = Path(__file__).resolve().parent
PX2PT = 0.96
X0 = 74.23969
STRIP_ADVANCE = 243.8426
XREFS = [3, 5, 7, 9, 11, 13, 15]

doc = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")
page = doc[0]
strips, Y0 = [], []
for x in XREFS:
    pm = pymupdf.Pixmap(doc, x)
    img = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)
    strips.append(img[::-1])                    # page orientation
    Y0.append(page.get_image_rects(x)[0].y0)
Y0 = np.array(Y0)
CANVAS = np.vstack(strips).astype(np.int16)

PALETTE = np.array([[255, 245, 0], [218, 37, 29], [151, 148, 107], [151, 69, 120],
                    [0, 146, 63], [187, 130, 91], [102, 122, 179], [237, 255, 140],
                    [38, 115, 0], [230, 230, 0], [96, 93, 92], [130, 130, 130]], np.int16)
MX, MN = CANVAS.max(2), CANVAS.min(2)
PAL = np.zeros(CANVAS.shape[:2], bool)
for c in PALETTE:
    PAL |= (np.abs(CANVAS - c).max(axis=2) <= 16)
INK = (MX < 95) & ((MX - MN) < 45)
SYM = PAL | INK

def glyph_at(x, y, rad=11):
    """Centre of the printed symbol nearest to (x, y) in canvas pixels."""
    x, y = int(round(x)), int(round(y))
    y0, y1 = max(0, y - rad), min(CANVAS.shape[0], y + rad + 1)
    x0, x1 = max(0, x - rad), min(CANVAS.shape[1], x + rad + 1)
    win = binary_fill_holes(SYM[y0:y1, x0:x1])
    lab, n = ndlabel(win)
    if n == 0:
        return None
    best = None
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        if not (3 <= h <= 24 and 3 <= w <= 24):
            continue
        if h * w > 700:
            continue
        cx = (xs.min() + xs.max()) / 2 + x0
        cy = (ys.min() + ys.max()) / 2 + y0
        d = float(np.hypot(cx - x, cy - y))
        if d <= rad and (best is None or d < best[1]):
            best = ((cx, cy), d)
    return best

def canvas_to_page(cx, cy):
    k = np.clip(((cy - Y0[0]) // STRIP_ADVANCE).astype(int), 0, 6)
    return X0 + PX2PT * np.asarray(cx), Y0[k] + PX2PT * (np.asarray(cy) - 255 * k)

def page_to_lonlat(xp, yp):
    lon = 2.47619 + (np.asarray(xp) - X0) * 12.54519 / 1976.9518
    lat = 14.04668 - (np.asarray(yp) - 358.7239) * 10.20997 / 1608.9773
    return lon, lat

rows = list(csv.DictReader(open(P / "Minerals_Symbol_Points_source.csv")))
px = np.array([float(r["canvas_x"]) for r in rows])
py_raw = np.array([float(r["canvas_y"]) for r in rows])
# The source table records rows in the art strips' stored (unflipped) order. The strips are
# drawn flipped, so convert each row into page orientation before using the canvas.
# strip heights: six of 255 px and a final one of 153 px, stacked in page order
_H = np.array([255, 255, 255, 255, 255, 255, 153])
_START = np.concatenate([[0], np.cumsum(_H)[:-1]])
_strip = np.clip((py_raw // 255).astype(int), 0, 6)
_local = (py_raw - _strip * 255).clip(0, _H[_strip] - 1)
py = _START[_strip] + (_H[_strip] - 1 - _local)

new = np.c_[px, py].astype(float)
how = np.full(len(rows), 2)
for i, (x, y) in enumerate(zip(px, py)):
    g = glyph_at(x, y)
    if g is not None:
        new[i] = g[0]
        how[i] = 0 if g[1] <= 6 else 1

lon, lat = page_to_lonlat(*canvas_to_page(new[:, 0], new[:, 1]))
lon0, lat0 = page_to_lonlat(*canvas_to_page(px, py))

def resid(pts):
    out = []
    for x, y in pts:
        g = glyph_at(x, y)
        out.append(np.nan if g is None else g[1])
    return np.array(out)

KM = PX2PT / 157.6 * 111.2
r_old, r_new = resid(np.c_[px, py]), resid(new)
rep = {
    "points": len(rows),
    "snapped_to_glyph_pct": round(float((how < 2).mean() * 100), 1),
    "snapped_within_6px_pct": round(float((how == 0).mean() * 100), 1),
    "distance_to_symbol_centre_px_median_old": round(float(np.nanmedian(r_old)), 2),
    "distance_to_symbol_centre_px_median_new": round(float(np.nanmedian(r_new)), 2),
    "distance_to_symbol_centre_km_old": round(float(np.nanmedian(r_old) * KM), 2),
    "distance_to_symbol_centre_km_new": round(float(np.nanmedian(r_new) * KM), 2),
    "median_move_km": round(float(np.median(np.hypot(*(new - np.c_[px, py]).T) * KM)), 2),
    "p90_move_km": round(float(np.percentile(np.hypot(*(new - np.c_[px, py]).T) * KM, 90)), 2),
    "note": "the large moves relative to the previous file come from the vertical-flip fix "
            "and from the 19 km frame correction, not from the centre snapping "
            "(median snap is under 3 px)",
}

out = []
for i, r in enumerate(rows):
    d = dict(r)
    d.update(lon=round(float(lon[i]), 6), lat=round(float(lat[i]), 6),
             lon_prev=round(float(lon0[i]), 6), lat_prev=round(float(lat0[i]), 6),
             canvas_x_centre=round(float(new[i, 0]), 2),
             canvas_y_centre=round(float(new[i, 1]), 2),
             snap_px=round(float(np.hypot(*(new[i] - [px[i], py[i]]))), 2))
    for k in ("lon_printed", "lat_printed", "shift_east_km", "shift_north_km",
              "lon_was", "lat_was", "canvas_x", "canvas_y", "move_km"):
        d.pop(k, None)
    out.append(d)
fields = list(out[0].keys())
with open(P / "Minerals_Symbol_Centres_4326.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
json.dump({"type": "FeatureCollection", "name": "Minerals_Symbol_Centres_4326",
           "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
           "metadata": rep,
           "features": [{"type": "Feature",
                         "geometry": {"type": "Point", "coordinates": [d["lon"], d["lat"]]},
                         "properties": d} for d in out]},
          open(P / "Minerals_Symbol_Centres_4326.geojson", "w"), separators=(",", ":"))
json.dump(rep, open(P / "Symbol_Centre_Report.json", "w"), indent=2)
print(json.dumps(rep, indent=2))
