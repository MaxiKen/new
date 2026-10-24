"""Name the printed mineral glyphs, with the accuracy of the naming measured.

Method
------
The source extraction recorded, for each of its 1,514 labelled symbols, a colour and
the printed size (w_px, h_px).  Those labels came from a purpose-built reader working
on this same sheet at this same 75 dpi, and were never the part of that dataset in
doubt -- only the coordinates were.  They are used here as reference appearance
samples.

Each detected glyph is reduced to the same kind of signature:

    body colour   the saturated flat fill sampled inside the glyph's own box, so a
                  hatched fill such as Limestone's green grid still reads as green
    w, h          union bounding box of the glyph's own parts, at 75 dpi

and named by a box kernel over the reference: count the reference symbols of each
mineral that share the colour and lie within +-1 px in both dimensions, and take the
most common.  The kernel is what makes a 10x10 green grid read as Limestone (136 of
them) rather than MarI (5 of them), which a single median size cannot do.

Accuracy is measured by leave-one-out over the reference itself.
"""
import pickle
from collections import Counter

import cv2
import numpy as np
import pyogrio

import find_sites as F

PAL = {(255, 245, 0): "yellow", (218, 37, 29): "red", (151, 148, 107): "khaki",
       (151, 69, 120): "purple", (96, 93, 92): "dark grey", (0, 146, 63): "green",
       (130, 130, 130): "grey", (170, 170, 170): "grey",
       (132, 194, 37): "light green", (102, 122, 179): "blue grey",
       (56, 52, 49): "outline", (187, 130, 91): "tan",
       (0, 255, 0): "bright green", (231, 120, 23): "orange",
       (169, 0, 229): "violet", (0, 0, 0): "outline"}

SATURATED = {"yellow", "red", "khaki", "purple", "dark grey", "green",
             "light green", "blue grey", "tan", "bright green", "orange", "violet"}


def parts(canvas):
    c = canvas.astype(np.int16)
    out = []
    for f in F.FILLS:
        m = (np.abs(c - np.array(f)).max(2) <= 0).astype(np.uint8)
        n, lab, st, ce = cv2.connectedComponentsWithStats(m, connectivity=8)
        for i in range(1, n):
            a, w, h = st[i, 4], st[i, 2], st[i, 3]
            if 8 <= a <= 260 and 4 <= w <= 22 and 3 <= h <= 18 and a / (w * h) >= 0.45:
                out.append(dict(x=float(ce[i][0]), y=float(ce[i][1]), kind="fill",
                                colour=tuple(int(v) for v in f), w=int(w), h=int(h),
                                area=int(a)))
    m = (np.abs(c - np.array(F.INK)).max(2) <= 6).astype(np.uint8)
    dm = cv2.dilate(m, np.ones((3, 3), np.uint8), 1)
    n, lab, st, ce = cv2.connectedComponentsWithStats(dm, connectivity=8)
    for i in range(1, n):
        a, w, h = st[i, 4], st[i, 2], st[i, 3]
        if 12 <= a <= 420 and 3 <= w <= 24 and 3 <= h <= 20:
            out.append(dict(x=float(ce[i][0]), y=float(ce[i][1]), kind="ink",
                            colour=None, w=int(w), h=int(h), area=int(a)))
    n, lab, st, ce = cv2.connectedComponentsWithStats(
        (np.abs(c - 255).max(2) <= 0).astype(np.uint8), connectivity=8)
    for i in range(1, n):
        a, w, h = st[i, 4], st[i, 2], st[i, 3]
        if 8 <= a <= 160 and 4 <= w <= 20 and 3 <= h <= 16 and a / (w * h) >= 0.55:
            out.append(dict(x=float(ce[i][0]), y=float(ce[i][1]), kind="white",
                            colour=None, w=int(w), h=int(h), area=int(a)))
    b = cv2.morphologyEx((np.abs(c - 0).max(2) <= 0).astype(np.uint8),
                         cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, ce = cv2.connectedComponentsWithStats(b, connectivity=8)
    for i in range(1, n):
        a, w, h = st[i, 4], st[i, 2], st[i, 3]
        if 14 <= a <= 200 and 5 <= w <= 22 and 4 <= h <= 16 and a / (w * h) >= 0.5:
            out.append(dict(x=float(ce[i][0]), y=float(ce[i][1]), kind="black",
                            colour=(0, 0, 0), w=int(w), h=int(h), area=int(a)))
    return out


def group(out, r=5.0):
    order = {"fill": 0, "black": 1, "ink": 2, "white": 3}
    out = sorted(out, key=lambda s: (order[s["kind"]], -s["area"]))
    groups = []
    for s in out:
        hit = None
        for g in groups:
            if (s["x"] - g["x"]) ** 2 + (s["y"] - g["y"]) ** 2 <= r * r:
                hit = g
                break
        if hit is None:
            groups.append(dict(x=s["x"], y=s["y"], parts=[s]))
        else:
            k = len(hit["parts"])
            hit["x"] = (hit["x"] * k + s["x"]) / (k + 1)
            hit["y"] = (hit["y"] * k + s["y"]) / (k + 1)
            hit["parts"].append(s)
    rows = []
    for g in groups:
        ps = g["parts"]
        x0 = min(p["x"] - p["w"] / 2 for p in ps)
        x1 = max(p["x"] + p["w"] / 2 for p in ps)
        y0 = min(p["y"] - p["h"] / 2 for p in ps)
        y1 = max(p["y"] + p["h"] / 2 for p in ps)
        rows.append(dict(x=round(g["x"], 2), y=round(g["y"], 2),
                         w=int(round(x1 - x0)), h=int(round(y1 - y0)),
                         parts=ps))
    return rows


def colour_of(canvas, g):
    x, y, w, h = g["x"], g["y"], g["w"], g["h"]
    x0 = max(0, int(round(x - w / 2))); x1 = min(2060, int(round(x + w / 2)) + 1)
    y0 = max(0, int(round(y - h / 2))); y1 = min(1677, int(round(y + h / 2)) + 1)
    cnt = Counter(map(tuple, canvas[y0:y1, x0:x1].reshape(-1, 3).tolist()))
    best, bn = None, 0
    for c, n in cnt.items():
        k = PAL.get(c)
        if k is None or k not in SATURATED:
            continue
        if n > bn:
            best, bn = k, n
    if bn >= 5:
        return best
    keys = [PAL[p["colour"]] for p in g["parts"]
            if p.get("colour") is not None and p["colour"] in PAL]
    return next((k for k in keys if k in SATURATED), None) or "outline"


def reference(path="source_extraction/nigeria_maps.gpkg"):
    ex = pyogrio.read_dataframe(path, layer="minerals2023_mineral_symbols_raster")
    ex = ex[~ex.mineral.astype(str).str.startswith("not a mineral")].copy()
    ex = ex[(ex.w_px >= 3) & (ex.h_px >= 3)]
    return [(str(r.colour), float(r.w_px), float(r.h_px), str(r.mineral))
            for r in ex.itertuples()]


def name_one(sig, ref, tol=1):
    pool = [r for r in ref if r[0] == sig["colour"]]
    if not pool:
        return None, 0.0
    c = Counter()
    for r in pool:
        if abs(r[1] - sig["w"]) <= tol and abs(r[2] - sig["h"]) <= tol:
            c[r[3]] += 1
    t = tol
    while not c and t < 5:
        t += 1
        for r in pool:
            if abs(r[1] - sig["w"]) <= t and abs(r[2] - sig["h"]) <= t:
                c[r[3]] += 1
    if not c:
        return pool[0][3], 0.0
    b = c.most_common(1)[0]
    return b[0], b[1] / sum(c.values())


def loocv(ref):
    ok = tot = 0
    for i, (c, w, h, m) in enumerate(ref):
        g, _ = name_one(dict(colour=c, w=w, h=h), ref[:i] + ref[i + 1:])
        if g is None:
            continue
        tot += 1
        ok += (g == m)
    return ok, tot


def family_accuracy(ref):
    from collections import defaultdict
    by = defaultdict(lambda: [0, 0])
    for i, (c, w, h, m) in enumerate(ref):
        g, _ = name_one(dict(colour=c, w=w, h=h), ref[:i] + ref[i + 1:])
        if g is None:
            continue
        by[c][1] += 1
        by[c][0] += (g == m)
    return {k: round(100 * v[0] / v[1], 1) for k, v in by.items() if v[1] >= 3}


def run(canvas):
    g = group(parts(canvas))
    ref = reference()
    for s in g:
        s["colour"] = colour_of(canvas, s)
        s["mineral"], s["conf"] = name_one(s, ref)
    return g, ref
