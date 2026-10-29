#!/usr/bin/env python3
"""Final symbol centring: match each mineral point to the glyph of its own colour.

The recorded positions are close to the right glyph (within a few pixels) but not exactly on
its centre, and the strip arithmetic cannot be inverted reliably enough to trust alone. This
step therefore works on a real render of the page: it finds every flat-palette glyph, keeps
each one's colour family, and moves each point to the centre of the nearest glyph that has
the same colour family as that point. The colour test stops a point from snapping onto the
neighbouring symbol, which is the failure mode of a plain nearest-neighbour snap.
"""
import csv, json
from pathlib import Path
import numpy as np, pymupdf
from scipy.ndimage import label as ndlabel, binary_closing
from scipy.spatial import cKDTree

P = Path(__file__).resolve().parent
S = 4                                  # render 4 px per pt
PALETTE = {                            # colour -> (family, rgb)
    0: ("yellow", (255, 245, 0)), 1: ("red", (218, 37, 29)),
    2: ("khaki", (151, 148, 107)), 3: ("violet", (151, 69, 120)),
    4: ("green", (0, 146, 63)), 5: ("brown", (187, 130, 91)),
    6: ("blue grey", (102, 122, 179)), 7: ("light green", (237, 255, 140)),
    8: ("bright green", (38, 115, 0)), 9: ("yellow", (230, 230, 0)),
    10: ("tan", (96, 93, 92)), 11: ("outline", (130, 130, 130)),
}
page = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
CLIP = pymupdf.Rect(74.23969, 358.7239, 2051.8313, 1968.6611)
pix = page.get_pixmap(matrix=pymupdf.Matrix(S, S), clip=CLIP, alpha=False)
A = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.int16)

# every flat-palette glyph, with its colour family
comps = []
for k, (fam, rgb) in PALETTE.items():
    m = binary_closing(np.abs(A - np.array(rgb)).max(axis=2) <= 20, np.ones((3, 3)))
    lab, n = ndlabel(m)
    if n == 0: continue
    sz = np.bincount(lab.ravel())
    ys, xs = np.nonzero(lab)
    sx = np.zeros(n + 1); sy = np.zeros(n + 1)
    np.add.at(sx, lab[ys, xs], xs); np.add.at(sy, lab[ys, xs], ys)
    from scipy.ndimage import find_objects
    boxes = find_objects(lab)
    for i in range(1, n + 1):
        if not (30 <= sz[i] <= 2600): continue          # 2-13 pt across at this scale
        sl = boxes[i - 1]
        if sl is None: continue
        hh = sl[0].stop - sl[0].start; ww = sl[1].stop - sl[1].start
        if hh > 60 or ww > 60 or hh < 6 or ww < 6: continue
        if hh * ww and sz[i] / (hh * ww) < 0.25: continue
        comps.append((sx[i] / sz[i] / S + CLIP.x0, sy[i] / sz[i] / S + CLIP.y0, fam, k))
print("glyphs found:", len(comps))

by_fam = {}
for x, y, fam, k in comps:
    by_fam.setdefault(fam, []).append((x, y))
trees = {f: cKDTree(np.array(v)) for f, v in by_fam.items() if len(v) > 3}

rows = list(csv.DictReader(open(P / "Minerals_Symbol_Centres_4326.csv")))
def ll2page(lon, lat):
    return (74.23969 + (lon - 2.47619) / 12.54519 * 1976.9518,
            358.7239 + (14.04668 - lat) / 10.20997 * 1608.9773)
def page2ll(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)

moved, snapped, dists = [], [], []
for r in rows:
    x, y = ll2page(float(r["lon"]), float(r["lat"]))
    fam = (r["colour_family"] or "").strip().lower()
    tree = trees.get(fam)
    got = None
    if tree is not None:
        d, i = tree.query([x, y], k=1, distance_upper_bound=9.0)
        if np.isfinite(d):
            cx, cy = by_fam[fam][i]
            got = (cx, cy, d)
    if got is None:                       # no same-colour glyph nearby: nearest of any colour
        allpts = np.array([(px_, py_) for px_, py_, _, _ in comps])
        if len(allpts):
            d, i = cKDTree(allpts).query([x, y], k=1, distance_upper_bound=6.0)
            if np.isfinite(d):
                got = (allpts[i][0], allpts[i][1], d)
    if got is None:
        moved.append((float(r["lon"]), float(r["lat"]))); snapped.append(0); dists.append(np.nan)
    else:
        lon, lat = page2ll(got[0], got[1])
        moved.append((lon, lat)); snapped.append(1); dists.append(got[2])

dists = np.array(dists)
out = []
for i, r in enumerate(rows):
    d = dict(r)
    d["lon_prev"] = r["lon"]; d["lat_prev"] = r["lat"]
    d["lon"] = round(moved[i][0], 6); d["lat"] = round(moved[i][1], 6)
    d["snap_pt"] = None if not snapped[i] else round(float(dists[i]), 2)
    out.append(d)

names = list(out[0].keys())
with open(P / "Minerals_Symbol_Centres_4326.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=names); w.writeheader(); w.writerows(out)

# geojson, keeping the same properties
gj = json.load(open(P / "Minerals_Symbol_Centres_4326.geojson"))
props = {p["colour_family"] + "|" + str(p["canvas_x_centre"]) + "|" + str(p["canvas_y_centre"]): p
         for p in gj["features"] and [f["properties"] for f in gj["features"]]}
feats = []
for r in out:
    p = dict(r)
    for k in ("geometry", "lon_prev", "lat_prev"):
        p.pop(k, None)
    feats.append({"type": "Feature", "geometry": {"type": "Point",
                  "coordinates": [r["lon"], r["lat"]]}, "properties": p})
gj["features"] = feats
gj["metadata"]["snapped_to_same_colour_glyph_pct"] = round(float(np.mean(snapped)) * 100, 1)
gj["metadata"]["snap_distance_pt_median"] = round(float(np.nanmedian(dists)), 2)
json.dump(gj, open(P / "Minerals_Symbol_Centres_4326.geojson", "w"), separators=(",", ":"))

rep = {"points": len(rows), "snapped_pct": round(float(np.mean(snapped)) * 100, 1),
       "snap_distance_pt_median": round(float(np.nanmedian(dists)), 2),
       "snap_distance_km_median": round(float(np.nanmedian(dists)) * 0.706, 2),
       "within_1pt_pct": round(float(np.nanmean(dists <= 1)) * 100, 1)}
json.dump(rep, open(P / "Symbol_Snap_Report.json", "w"), indent=2)
print(json.dumps(rep, indent=2))
