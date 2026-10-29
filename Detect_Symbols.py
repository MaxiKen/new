#!/usr/bin/env python3
"""Locate every printed mineral symbol on the 2023 sheet: one point per symbol, at its centre.

The sheet numbers every occurrence and prints that number beside its symbol, so the printed
numbers are the survey's own count of occurrences. Each number is an anchor: in a small window
around it we find the mineral symbol, match it against the 67 legend symbols by colour and
shape, and record that symbol's CENTRE. Anchors that resolve to the same symbol are merged, so
two numbers can never produce two points on one symbol - they produce one point carrying both.

Outputs: Symbol_Inventory.json
"""
import json, pickle
from pathlib import Path
import numpy as np, pymupdf
from scipy import ndimage

P = Path(__file__).resolve().parent
PX2PT, X0 = 0.96, 74.23969
XREFS = [3, 5, 7, 9, 11, 13, 15]

doc = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")
page = doc[0]
strips, Y0 = [], []
for x in XREFS:
    pm = pymupdf.Pixmap(doc, x)
    strips.append(np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 3)[::-1])
    Y0.append(page.get_image_rects(x)[0].y0)
Y0 = np.array(Y0)
C = np.vstack(strips).astype(np.int16)
H, W = C.shape[:2]
print("canvas", C.shape)

def page2canvas(xp, yp):
    k = int(np.clip(np.searchsorted(Y0, yp, side="right") - 1, 0, len(Y0) - 1))
    return (xp - X0) / PX2PT, (yp - Y0[k]) / PX2PT + 255 * k

def canvas2page(cx, cy):
    k = int(np.clip(cy // 255, 0, len(Y0) - 1))
    return X0 + PX2PT * cx, Y0[k] + PX2PT * (cy - 255 * k)

# ---------------------------------------------------------------- anchors: printed numbers
CLIP = pymupdf.Rect(74.23969, 358.7239, 2051.8313, 1968.6611)
import re
anchors = []
for w in page.get_text("words"):
    x0, y0, x1, y1, t = w[0], w[1], w[2], w[3], w[4]
    if not (CLIP.x0 < x0 < CLIP.x1 and CLIP.y0 < y0 < CLIP.y1):
        continue
    m = re.fullmatch(r"(\d{1,3})\.?", t)
    if not m:
        continue
    n = int(m.group(1))
    if n < 1 or n > 260:
        continue
    anchors.append({"num": n, "xp": (x0 + x1) / 2, "yp": (y0 + y1) / 2})
print("numbered anchors:", len(anchors))

# ---------------------------------------------------------------- templates at map scale
TPL_SRC = pickle.load(open("/tmp/tpls.pkl", "rb"))
F = 1.0417 / 4.0
tpls = []
for t in TPL_SRC:
    img = t["img"]
    m = img.min(2) < 195
    ys, xs = np.nonzero(m)
    if len(xs) == 0: continue
    m2 = m[ys.min():ys.max()+1, xs.min():xs.max()+1]
    col = img[ys.min():ys.max()+1, xs.min():xs.max()+1]
    flat = col[m2]
    h = max(4, int(round(m2.shape[0] * F))); w = max(4, int(round(m2.shape[1] * F)))
    mm = ndimage.zoom(m2.astype(np.float32), (h / m2.shape[0], w / m2.shape[1]), order=1) > .5
    tpls.append({"name": re.sub(r"\s+", " ", t["name"]).strip(), "mask": mm,
                 "col": np.median(flat, 0), "h": h, "w": w})
print("templates:", len(tpls))

def colour_dist(a, b):
    return float(np.abs(np.asarray(a, float) - np.asarray(b, float)).max())

def match_at(px, py, rad=11):
    """Best legend symbol whose colour appears within `rad` px, and that symbol's bbox centre."""
    best = None
    y0, y1 = max(0, int(py) - rad), min(H, int(py) + rad + 1)
    x0, x1 = max(0, int(px) - rad), min(W, int(px) + rad + 1)
    win = C[y0:y1, x0:x1]
    if win.size == 0: return None
    for t in tpls:
        d = np.abs(win - t["col"].astype(np.int16)).max(2)
        hit = d <= 30
        if hit.sum() < 8: continue
        lab, n = ndimage.label(ndimage.binary_closing(hit, np.ones((2, 2))))
        if n == 0: continue
        sizes = ndimage.sum(hit, lab, range(1, n + 1))
        k = int(np.argmax(sizes)) + 1
        ys, xs = np.nonzero(lab == k)
        hh = ys.max() - ys.min() + 1; ww = xs.max() - xs.min() + 1
        if hh < 5 or ww < 5 or hh > 30 or ww > 30: continue
        # shape agreement with the template, resized
        blob = np.zeros((hh, ww), bool); blob[ys - ys.min(), xs - xs.min()] = True
        tb = ndimage.zoom(t["mask"].astype(np.float32), (hh / t["h"], ww / t["w"]), order=1) > .5
        inter = (blob & tb).sum(); union = (blob | tb).sum()
        iou = inter / max(union, 1)
        area_pen = abs(hit.sum() / max(hh * ww, 1) - t["mask"].mean())
        score = iou - .5 * area_pen
        cx = x0 + (xs.min() + xs.max()) / 2
        cy = y0 + (ys.min() + ys.max()) / 2
        dd = float(np.hypot(cx - px, cy - py))
        if dd > rad + 6: continue
        if best is None or score > best["score"]:
            best = {"score": score, "iou": iou, "symbol": t["name"], "cx": cx, "cy": cy,
                    "d": dd, "colour": [int(v) for v in t["col"]], "w": ww, "h": hh}
    return best

res = []
for a in anchors:
    cx, cy = page2canvas(a["xp"], a["yp"])
    m = match_at(cx, cy, rad=13)
    if m is None:
        res.append({**a, "cx": None, "cy": None}); continue
    res.append({**a, "cx": m["cx"], "cy": m["cy"], "symbol": m["symbol"], "score": round(m["score"], 3),
                "iou": round(m["iou"], 3), "colour": m["colour"], "w": m["w"], "h": m["h"]})
found = [r for r in res if r["cx"] is not None]
print("anchors matched to a symbol:", len(found), "of", len(anchors))
# ---------------------------------------------------------------- merge anchors on one symbol
groups = []
for r in sorted(found, key=lambda r: -r["score"]):
    for g in groups:
        if np.hypot(g["cx"] - r["cx"], g["cy"] - r["cy"]) <= 4.0:
            g["nums"].append(r["num"]); g["members"].append(r); break
    else:
        groups.append({"cx": r["cx"], "cy": r["cy"], "nums": [r["num"]], "members": [r],
                       "symbol": r["symbol"], "score": r["score"]})
print("distinct symbols (one point each):", len(groups))
print("symbols carrying more than one index number:", sum(1 for g in groups if len(g["nums"]) > 1))
out = []
for g in groups:
    xp, yp = canvas2page(g["cx"], g["cy"])
    out.append({"cx": round(g["cx"], 2), "cy": round(g["cy"], 2), "xp": round(xp, 2), "yp": round(yp, 2),
                "symbol": g["symbol"], "score": g["score"], "index_numbers": sorted(g["nums"]),
                "n_anchors": len(g["nums"])})
json.dump({"canvas": [W, H], "count": len(out), "points": out}, open(P / "Symbol_Inventory.json", "w"), indent=0)
print("written Symbol_Inventory.json with", len(out), "points")
import collections
print(collections.Counter(o["symbol"] for o in out).most_common(8))
