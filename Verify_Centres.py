#!/usr/bin/env python3
"""Independent check: draw the corrected points on the real PDF page and measure.

The check does not reuse any canvas coordinates. It renders the page, finds symbol glyphs
directly in the render by their palette colours and ink, and asks how far each corrected
point is from the centre of the glyph it lands on.
"""
import csv, json
from pathlib import Path
import numpy as np, pymupdf
from scipy.ndimage import label as ndlabel, binary_fill_holes
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
S = 4                                   # render 4 px per pt
page = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
# invert the embedded measure to get page coords from lon/lat
def ll_to_page(lon, lat):
    return (74.23969 + (np.asarray(lon) - 2.47619) / 12.54519 * 1976.9518,
            358.7239 + (14.04668 - np.asarray(lat)) / 10.20997 * 1608.9773)

rows = list(csv.DictReader(open(P / "Minerals_Symbol_Centres_4326.csv")))
lon = np.array([float(r["lon"]) for r in rows]); lat = np.array([float(r["lat"]) for r in rows])
xp, yp = ll_to_page(lon, lat)

PALETTE = np.array([[255, 245, 0], [218, 37, 29], [151, 148, 107], [151, 69, 120],
                    [0, 146, 63], [187, 130, 91], [102, 122, 179], [237, 255, 140],
                    [38, 115, 0], [230, 230, 0], [96, 93, 92], [130, 130, 130]])
clip = pymupdf.Rect(74.23969, 358.7239, 2051.8313, 1968.6611)
pix = page.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=clip, alpha=False)
A = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.int16)
MX, MN = A.max(2), A.min(2)
PAL = np.zeros(A.shape[:2], bool)
for c in PALETTE:
    PAL |= (np.abs(A - c).max(axis=2) <= 22)
INK = (MX < 95) & ((MX - MN) < 45)
SYM = PAL | INK

def glyph_centre(cx, cy, rad=None):
    rad = rad or int(11 * S / 2)
    x, y = int(round(cx)), int(round(cy))
    y0, y1 = max(0, y - rad), min(A.shape[0], y + rad + 1)
    x0, x1 = max(0, x - rad), min(A.shape[1], x + rad + 1)
    win = binary_fill_holes(SYM[y0:y1, x0:x1])
    lab, n = ndlabel(win)
    size_pt = 24 * S / 2
    best = None
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        if not (3 * S / 2 <= h <= size_pt and 3 * S / 2 <= w <= size_pt): continue
        if h * w > (24 * S / 2) ** 2: continue
        gx = (xs.min() + xs.max()) / 2 + x0
        gy = (ys.min() + ys.max()) / 2 + y0
        d = float(np.hypot(gx - x, gy - y)) / S
        if d <= 11 and (best is None or d < best[1]): best = ((gx, gy), d)
    return best

dist, snap = [], []
for i in range(len(rows)):
    px = (xp[i] - clip.x0) * S; py = (yp[i] - clip.y0) * S
    g = glyph_centre(px, py)
    if g is None: dist.append(np.nan); snap.append((px, py, None)); continue
    dist.append(g[1]); snap.append((px, py, g[0]))
dist = np.array(dist)
ok = np.isfinite(dist)
rep = {"checked": int(ok.sum()), "total": len(rows),
       "on_a_glyph_pct": round(float(ok.mean() * 100), 1),
       "distance_to_glyph_centre_pt_median": round(float(np.median(dist[ok])), 2),
       "distance_to_glyph_centre_km_median": round(float(np.median(dist[ok]) * 0.706), 2),
       "within_1pt_pct": round(float((dist[ok] <= 1).mean() * 100), 1),
       "within_2pt_pct": round(float((dist[ok] <= 2).mean() * 100), 1)}
json.dump(rep, open(P / "Verify_Centres.json", "w"), indent=2)
print(json.dumps(rep, indent=2))

# zoomed proof sheet
order = np.argsort(dist)[::40][:8]
tiles = []
for i in order:
    px, py, _ = snap[i]
    half = int(16 * S)
    x0, y0 = int(px) - half, int(py) - half
    w = A[max(0, y0):y0 + 2 * half, max(0, x0):x0 + 2 * half].astype(np.uint8).copy()
    c = (int(py) - max(0, y0), int(px) - max(0, x0))
    for t in range(-int(2.2 * S), int(2.2 * S) + 1):
        for e in (-2, -1, 1, 2):
            for yy, xx in ((c[0] + t, c[1] + e), (c[0] + e, c[1] + t)):
                if 0 <= yy < w.shape[0] and 0 <= xx < w.shape[1]: w[yy, xx] = [255, 0, 255]
    tiles.append(w)
h = max(t.shape[0] for t in tiles)
tiles = [np.pad(t, ((0, h - t.shape[0]), (0, 0), (0, 0)), constant_values=255) for t in tiles]
plt.imsave(P / "Symbol_Centre_Proof.png", np.hstack(tiles))
