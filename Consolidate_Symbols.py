#!/usr/bin/env python3
"""One point per printed symbol, at the symbol's centre.

Consolidation rules (they are geometric facts about the sheet, not preferences):
  * A symbol is a connected patch of the sheet's flat symbol palette. Two points that fall on
    the SAME patch are the same symbol, so they are merged into one point, placed at that
    patch's centre. Their names/numbers are kept together, not discarded.
  * Two points on DIFFERENT patches stay separate, however close, because a cluster of
    adjacent symbols is a real cluster of occurrences and must not be collapsed.
  * A point that lands on no patch keeps its measured position, and is only merged if another
    point is within 2.5 px (i.e. the same symbol seen twice).

Outputs: Minerals_Occurrences_4326.csv / .geojson, Symbol_Consolidation.json
"""
import json, csv
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
H, W = C.shape[:2]

# ---- the sheet's symbol palette, measured from the artwork itself
SYMCOL = [(248,240,0),(144,144,104),(80,96,232),(0,144,56),(216,32,24),(96,88,88),
          (144,64,120),(128,192,32),(96,120,176),(192,128,64),(0,248,0),(224,120,16),
          (128,0,168),(0,72,168),(168,0,224),(72,72,72),(184,128,88)]
hit = np.zeros((H, W), bool)
for c in SYMCOL:
    hit |= (np.abs(C - np.array(c, np.int16)).max(2) <= 30)
# black symbol fills too (coal, tar sand, magnetite), but not thin black linework or text
dark = C.max(2) < 70
dark_lab, nd = ndimage.label(dark)
objs = ndimage.find_objects(dark_lab)
dark_ok = np.zeros((H, W), bool)
for i, o in enumerate(objs):
    if o is None: continue
    hh = o[0].stop - o[0].start; ww = o[1].stop - o[1].start
    s = (dark_lab[o] == i + 1).sum()
    if 6 <= hh <= 30 and 6 <= ww <= 30 and s / (hh * ww) > 0.45 and s > 40:
        dark_ok[o] |= (dark_lab[o] == i + 1)
hit |= dark_ok
hit = ndimage.binary_closing(hit, np.ones((2, 2)))
blob, nblob = ndimage.label(hit)
print("symbol patches on the sheet:", nblob, "covering", int(hit.sum()), "px")

def ll2page(lon, lat):
    return (74.23969 + (lon - 2.47619) / 12.54519 * 1976.9518,
            358.7239 + (14.04668 - lat) / 10.20997 * 1608.9773)
def page2canvas(xp, yp):
    k = int(np.clip(np.searchsorted(Y0, yp, side="right") - 1, 0, len(Y0) - 1))
    return (xp - X0) / PX2PT, (yp - Y0[k]) / PX2PT + 255 * k
def canvas2page(cx, cy):
    k = int(np.clip(cy // 255, 0, len(Y0) - 1))
    return X0 + PX2PT * cx, Y0[k] + PX2PT * (cy - 255 * k)
def page2ll(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)

rows = pd.read_csv(P / "Minerals_Symbol_Centres_4326.csv")
print("input points:", len(rows))
recs = []
for i, r in rows.iterrows():
    xp, yp = ll2page(r["lon"], r["lat"])
    cx, cy = page2canvas(xp, yp)
    bid = int(blob[int(round(cy)), int(round(cx))]) if 0 <= int(round(cy)) < H and 0 <= int(round(cx)) < W else 0
    recs.append({"i": i, "lon": r["lon"], "lat": r["lat"], "cx": cx, "cy": cy,
                 "blob": bid, "mineral": r.get("mineral"), "class": r.get("mineral_class"),
                 "tier": r.get("tier"), "colour": r.get("colour_family")})
print("points on a symbol patch:", sum(1 for r in recs if r["blob"] > 0),
      f"({100*sum(1 for r in recs if r['blob']>0)/len(recs):.1f}%)")

# ---- group
by_blob = {}
loose = []
for r in recs:
    if r["blob"] > 0: by_blob.setdefault(r["blob"], []).append(r)
    else: loose.append(r)
groups = list(by_blob.values())
# merge loose points that are duplicates of each other
loose.sort(key=lambda r: (r["cx"], r["cy"]))
used = set()
for a in range(len(loose)):
    if a in used: continue
    grp = [loose[a]]; used.add(a)
    for b in range(a + 1, len(loose)):
        if b in used: continue
        if np.hypot(loose[a]["cx"] - loose[b]["cx"], loose[a]["cy"] - loose[b]["cy"]) <= 2.5:
            grp.append(loose[b]); used.add(b)
    groups.append(grp)
print("symbols after consolidation:", len(groups))
print("points merged away:", len(recs) - len(groups))

out = []
for g in groups:
    bid = g[0]["blob"]
    if bid > 0:
        ys, xs = np.nonzero(blob == bid)
        cx, cy = xs.mean(), ys.mean()          # centre of the patch's ink
        bx = (xs.min() + xs.max()) / 2; by = (ys.min() + ys.max()) / 2
        cx, cy = (cx + bx) / 2, (cy + by) / 2  # blend of centroid and bbox centre: stable
    else:
        cx = float(np.mean([p["cx"] for p in g])); cy = float(np.mean([p["cy"] for p in g]))
    xp, yp = canvas2page(cx, cy)
    lon, lat = page2ll(xp, yp)
    names = [p["mineral"] for p in g if isinstance(p["mineral"], str) and p["mineral"].strip()]
    uniq = sorted(set(names))
    cls = sorted({p["class"] for p in g if isinstance(p["class"], str)})
    tier = sorted({p["tier"] for p in g if isinstance(p["tier"], str)})
    out.append({"lon": round(lon, 6), "lat": round(lat, 6), "symbol_patch": int(bid),
                "n_source_points": len(g), "mineral": uniq[0] if uniq else "unidentified",
                "mineral_alternatives": " | ".join(uniq[1:]),
                "mineral_class": cls[0] if cls else "unknown",
                "classes_seen": " | ".join(cls), "tier": tier[0] if tier else "unidentified",
                "name_source": "printed symbol, colour+code classification",
                "cx": round(cx, 2), "cy": round(cy, 2), "xp": round(xp, 2), "yp": round(yp, 2)})
df = pd.DataFrame(out)
df.to_csv(P / "Minerals_Occurrences_4326.csv", index=False)
gj = {"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
      "features": [{"type": "Feature", "properties": {k: v for k, v in r.items() if k not in ("lon","lat")},
                    "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]}} for r in out]}
json.dump(gj, open(P / "Minerals_Occurrences_4326.geojson", "w"))
rep = {"input_points": len(recs), "on_a_symbol_patch_pct": round(100*sum(1 for r in recs if r["blob"]>0)/len(recs),1),
       "distinct_symbols": len(out), "duplicates_merged": len(recs)-len(out),
       "merged_multi": int((df.n_source_points > 1).sum()),
       "multi_named": int((df.mineral_alternatives != "").sum())}
json.dump(rep, open(P / "Symbol_Consolidation.json", "w"), indent=2)
print(json.dumps(rep, indent=2))
