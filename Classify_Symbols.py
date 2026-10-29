#!/usr/bin/env python3
"""Name each consolidated symbol by matching its own printed glyph to the sheet's legend.

Every occurrence on the sheet is drawn as one of the 67 symbols in the EXPLANATIONS panel, so
the legend is a closed set of answers. For each detected symbol we take its printed patch,
compare it with all 67 legend swatches on colour and shape, and record the best match, the
runner-up and the margin. A small margin is reported as a prediction rather than a fact.

Adds to Minerals_Occurrences_4326.csv: legend_symbol, legend_score, second_symbol, margin,
name_confidence, name_source.
"""
import json, pickle
from pathlib import Path
import numpy as np, pandas as pd, pymupdf
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

TPL = pickle.load(open("/tmp/tpls.pkl", "rb"))
S = 20
def norm(img):
    m = img.min(2) < 195
    ys, xs = np.nonzero(m)
    if len(xs) < 6: return None, None
    mm = m[ys.min():ys.max()+1, xs.min():xs.max()+1]
    cc = img[ys.min():ys.max()+1, xs.min():xs.max()+1]
    h = max(2, int(round(S * mm.shape[0] / max(mm.shape))))
    w = max(2, int(round(S * mm.shape[1] / max(mm.shape))))
    z = ndimage.zoom(mm.astype(np.float32), (h / mm.shape[0], w / mm.shape[1]), order=1) > .5
    out = np.zeros((S, S), bool); out[:z.shape[0], :z.shape[1]] = z
    flat = cc[mm]
    return out, np.median(flat, 0)

T = []
for t in TPL:
    m, col = norm(t["img"])
    if m is None: continue
    T.append({"name": " ".join(t["name"].split()), "mask": m, "col": col})
print("legend templates:", len(T))

df = pd.read_csv(P / "Minerals_Occurrences_4326.csv")
def patch_at(cx, cy, r=9):
    x, y = int(round(cx)), int(round(cy))
    return C[max(0, y-r):y+r+1, max(0, x-r):x+r+1]

recs = []
for _, r in df.iterrows():
    p = patch_at(r["cx"], r["cy"])
    m, col = norm(p)
    if m is None:
        recs.append((None, None, None)); continue
    scored = []
    for t in T:
        inter = (m & t["mask"]).sum(); union = (m | t["mask"]).sum()
        iou = inter / max(union, 1)
        dc = float(np.abs(col - t["col"]).max()) / 255.0
        scored.append((iou - 1.1 * dc, iou, dc, t["name"]))
    scored.sort(key=lambda z: -z[0])
    recs.append((scored[0], scored[1] if len(scored) > 1 else None, scored[:3]))
names = [r[0][3] if r[0] else "unidentified" for r in recs]
margins = [round(r[0][0] - r[1][0], 3) if r[0] and r[1] else 0.0 for r in recs]
df["legend_symbol"] = names
df["legend_score"] = [round(r[0][0], 3) if r[0] else 0 for r in recs]
df["second_symbol"] = [r[1][3] if r[1] else "" for r in recs]
df["margin"] = margins
def conf(m, sc):
    if sc < .15: return "low"
    if m >= .12: return "high"
    if m >= .05: return "medium"
    return "low"
df["name_confidence"] = [conf(m, s) for m, s in zip(margins, df["legend_score"])]
df["name_source"] = "legend symbol match on the printed glyph"
df.to_csv(P / "Minerals_Occurrences_4326.csv", index=False)
print("legend symbol distribution:")
print(df.legend_symbol.value_counts().head(15).to_string())
print("distinct names now:", df.legend_symbol.nunique())
print("confidence:", df.name_confidence.value_counts().to_dict())
# agreement with the earlier colour-family naming - a sanity check, not a proof
agree = (df.legend_symbol.str.lower().str.replace(r"[^a-z]", "", regex=True) ==
         df.mineral.str.lower().str.replace(r"[^a-z]", "", regex=True))
print("agrees with the earlier name on", round(100*agree.mean(), 1), "% of points")
json.dump({"templates": len(T), "distinct_names": int(df.legend_symbol.nunique()),
           "agreement_with_previous_pct": round(100*agree.mean(), 1)},
          open(P / "Symbol_Classification.json", "w"), indent=2)
