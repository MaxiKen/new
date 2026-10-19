"""Mineral legend: names (vector text) + symbol templates (native legend strips)."""
import sys, re, json
sys.path.insert(0,"scripts")
import numpy as np, cv2, fitz
doc=fitz.open("Mineral_Resources_Map_of_Nigeria_2023 (2).pdf"); page=doc[0]
dd=page.get_text("dict")
spans=[]
for b in dd["blocks"]:
    if b.get("type")==0:
        for l in b["lines"]:
            for s in l["spans"]:
                spans.append(s)
# Legend mineral names: x0 in [2110,2300], y in [330,1400], size ~9-12, alphabetic
cand=[]
for s in spans:
    x0,y0,x1,y1=s["bbox"]
    t=s["text"].strip()
    if 2105<=x0<=2320 and 330<=y0<=1420 and len(t)>=3 and any(c.isalpha() for c in t):
        cand.append((y0,x0,t,round(s["size"],1),s["font"]))
cand.sort()
print(f"legend-area candidate spans: {len(cand)}")
for c in cand: print(f" y={c[0]:7.1f} x={c[1]:6.0f} size={c[3]} {c[2]!r}")
