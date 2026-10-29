#!/usr/bin/env python3
"""Final snap: put each consolidated occurrence exactly on the centre of its printed symbol.

Consolidation moved some points to the centre of the patch they share; a patch centre and the
symbol's drawn centre are not always the same pixel. This re-runs the independent page-render
glyph detection used for verification and moves each point onto the centre it finds, leaving
the point alone when no glyph is found nearby (so nothing is dragged onto a neighbour).

Writes Minerals_Occurrences_4326.csv in place, and Snap_Final.json with what moved.
"""
import csv, json
from pathlib import Path
import numpy as np, pymupdf
from scipy.ndimage import label as ndlabel, binary_fill_holes

P = Path(__file__).resolve().parent
S = 4
page = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
def ll_to_page(lon, lat):
    return (74.23969 + (np.asarray(lon) - 2.47619) / 12.54519 * 1976.9518,
            358.7239 + (14.04668 - np.asarray(lat)) / 10.20997 * 1608.9773)
def page_to_ll(xp, yp):
    return (2.47619 + (np.asarray(xp) - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (np.asarray(yp) - 358.7239) * 10.20997 / 1608.9773)

PALETTE = np.array([[255,245,0],[218,37,29],[151,148,107],[151,69,120],[0,146,63],[187,130,91],
                    [102,122,179],[237,255,140],[38,115,0],[230,230,0],[96,93,92],[130,130,130]])
clip = pymupdf.Rect(74.23969, 358.7239, 2051.8313, 1968.6611)
pix = page.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=clip, alpha=False)
A = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.int16)
MX, MN = A.max(2), A.min(2)
PAL = np.zeros(A.shape[:2], bool)
for c in PALETTE:
    PAL |= (np.abs(A - c).max(axis=2) <= 22)
SYM = PAL | ((MX < 95) & ((MX - MN) < 45))

def glyph(cx, cy, rad=None):
    rad = rad or int(11 * S / 2)
    x, y = int(round(cx)), int(round(cy))
    y0, y1 = max(0, y - rad), min(A.shape[0], y + rad + 1)
    x0, x1 = max(0, x - rad), min(A.shape[1], x + rad + 1)
    win = binary_fill_holes(SYM[y0:y1, x0:x1])
    lab, n = ndlabel(win)
    best = None
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        if not (3 * S / 2 <= h <= 24 * S / 2 and 3 * S / 2 <= w <= 24 * S / 2): continue
        gx = (xs.min() + xs.max()) / 2 + x0
        gy = (ys.min() + ys.max()) / 2 + y0
        d = float(np.hypot(gx - x, gy - y))
        if d <= 11 and (best is None or d < best[0]): best = (d, gx, gy)
    return best

rows = list(csv.DictReader(open(P / "Minerals_Occurrences_4326.csv")))
xs, ys = ll_to_page([float(r["lon"]) for r in rows], [float(r["lat"]) for r in rows])
moved, dists, missed = 0, [], 0
newx, newy = xs.copy(), ys.copy()
for i in range(len(rows)):
    px, py = (xs[i] - clip.x0) * S, (ys[i] - clip.y0) * S
    g = glyph(px, py)
    if g is None:
        missed += 1; continue
    d, gx, gy = g
    dists.append(d / S)
    if d > 0.05:
        newx[i] = clip.x0 + gx / S; newy[i] = clip.y0 + gy / S
        moved += 1
lon, lat = page_to_ll(newx, newy)
for i, r in enumerate(rows):
    r["lon"] = round(float(lon[i]), 6); r["lat"] = round(float(lat[i]), 6)
with open(P / "Minerals_Occurrences_4326.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
rep = {"points": len(rows), "moved_onto_glyph_centre": moved, "no_glyph_found": missed,
       "median_move_pt": round(float(np.median([d for d in dists if d > .05])), 3) if moved else 0,
       "median_offset_after_pt": round(float(np.median(dists)), 3) if dists else None,
       "median_offset_after_km": round(float(np.median(dists)) * 0.706, 2) if dists else None}
json.dump(rep, open(P / "Snap_Final.json", "w"), indent=2)
print(json.dumps(rep, indent=2))
