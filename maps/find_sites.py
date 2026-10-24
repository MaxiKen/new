"""Detect every printed mineral-symbol site in the NGSA 2023 raster (75 dpi).

Symbol bodies are flat-filled compact glyphs drawn opaquely over the map raster.
Running the compact-blob test over every distinct colour in the canvas (see
colour_scan) shows that only a small set of colours form glyph bodies; everything
else that looks compact is a pale wash polygon (>=1e5 px of that colour).

A site is the union of
  * body blobs in those fill colours,
  * symbol-ink mark clusters      (31,26,23),
  * black outline rings           (0,0,0),
  * enclosed white glyph bodies.
"""
import numpy as np
import cv2

FILLS = [(255, 245, 0), (218, 37, 29), (151, 148, 107), (151, 69, 120),
         (96, 93, 92), (0, 146, 63), (130, 130, 130), (170, 170, 170),
         (132, 194, 37), (102, 122, 179), (56, 52, 49), (187, 130, 91),
         (0, 255, 0), (231, 120, 23)]
INK = (31, 26, 23)
BLACK = (0, 0, 0)


def _blobs(mask, amin=8, amax=260, wmin=4, wmax=22, hmin=3, hmax=18, fill=0.45):
    n, lab, st, ce = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    out = []
    for i in range(1, n):
        a, w, h = st[i, 4], st[i, 2], st[i, 3]
        if amin <= a <= amax and wmin <= w <= wmax and hmin <= h <= hmax and a / (w * h) >= fill:
            out.append((float(ce[i][0]), float(ce[i][1]), int(a), int(w), int(h)))
    return out


def sites(canvas):
    c = canvas.astype(np.int16)
    out = []   # (x, y, kind, weight)
    for f in FILLS:
        for x, y, a, w, h in _blobs(np.abs(c - np.array(f)).max(2) <= 0):
            out.append((x, y, "fill", a))
    # ink mark clusters
    m = (np.abs(c - np.array(INK)).max(2) <= 6).astype(np.uint8)
    for x, y, a, w, h in _blobs(cv2.dilate(m, np.ones((3, 3), np.uint8), 1),
                                amin=12, amax=420, wmin=3, wmax=24, hmin=3, hmax=20, fill=0.0):
        out.append((x, y, "ink", a))
    # enclosed white bodies (white regions are separate components when ringed by ink)
    for x, y, a, w, h in _blobs(np.abs(c - 255).max(2) <= 0,
                                amin=8, amax=160, wmin=4, wmax=20, hmin=3, hmax=16, fill=0.55):
        out.append((x, y, "white", a))
    # black outline rings: close, then compact shells
    b = (np.abs(c - np.array(BLACK)).max(2) <= 0).astype(np.uint8)
    b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    for x, y, a, w, h in _blobs(b, amin=14, amax=200, wmin=5, wmax=22, hmin=4, hmax=16, fill=0.5):
        out.append((x, y, "black", a))
    return out


def merge(out, r=5.0):
    order = {"fill": 0, "ink": 1, "white": 2, "black": 3}
    out = sorted(out, key=lambda s: (order[s[2]], -s[3]))
    kept = []
    for x, y, k, a in out:
        hit = None
        for s in kept:
            if (x - s["x"]) ** 2 + (y - s["y"]) ** 2 <= r * r:
                hit = s
                break
        if hit is None:
            kept.append(dict(x=x, y=y, kind=k, area=a, n=1))
        else:
            hit["n"] += 1
            hit["x"] = (hit["x"] * (hit["n"] - 1) + x) / hit["n"]
            hit["y"] = (hit["y"] * (hit["n"] - 1) + y) / hit["n"]
            hit["area"] = max(hit["area"], a)
    return kept


def detect(canvas, r=5.0):
    return merge(sites(canvas), r)


if __name__ == "__main__":
    cv_ = np.load("/tmp/canvas75.npy")
    s = sites(cv_)
    print("raw parts:", len(s), {k: sum(1 for x in s if x[2] == k) for k in ("fill", "ink", "white", "black")})
    m = detect(cv_)
    print("merged sites:", len(m))
    ys = np.array([q["y"] for q in m])
    print("per band:", [int(((ys >= k * 244) & (ys < (k + 1) * 244)).sum()) for k in range(7)])
