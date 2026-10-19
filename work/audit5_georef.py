import pymupdf, numpy as np, re
from collections import Counter
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf')
p=d[0]
print("get_layers:", d.get_layers())
dr=p.get_drawings()
# Graticule-coloured strokes
for colname, col in [("red-boundary",(0.901960015296936,0,0)), ("pink-grat?",(0.9176499843597412,0.47843000292778015,0.47843000292778015)), ("blue-river",(0.450980007648468,0.8745099902153015,1.0))]:
    sel=[x for x in dr if x.get('color')==col]
    print(f"\n{colname} n={len(sel)}")
    for x in sel[:8]:
        r=x['rect']
        print(f"  rect=({r.x0:.1f},{r.y0:.1f},{r.x1:.1f},{r.y1:.1f}) w={x.get('width')} items={len(x['items'])} first={[i[0] for i in x['items'][:4]]}")
# Frame edge texts (graticule labels)
td=p.get_text("dict")
spans=[]
for bl in td["blocks"]:
    if bl["type"]!=0: continue
    for ln in bl["lines"]:
        for sp in ln["spans"]:
            t=sp["text"].strip()
            if not t: continue
            x0,y0,x1,y1=sp["bbox"]
            spans.append((t,x0,y0,x1,y1,sp.get("size"),ln.get("dir")))
print("\n--- texts near top frame (y<365, x<2100) ---")
for s in sorted([s for s in spans if s[2]<368 and s[1]<2100], key=lambda s:s[1]):
    print([round(v,1) if isinstance(v,float) else v for v in s])
print("\n--- texts near bottom frame (y>1965, x<2100) ---")
for s in sorted([s for s in spans if s[2]>1960 and s[1]<2100], key=lambda s:s[1]):
    print([round(v,1) if isinstance(v,float) else v for v in s])
print("\n--- texts near left frame (x<78) ---")
for s in sorted([s for s in spans if s[1]<80], key=lambda s:s[2]):
    print([round(v,1) if isinstance(v,float) else v for v in s])
print("\n--- texts near right of map frame (2050<x<2090) ---")
for s in sorted([s for s in spans if 2045<s[1]<2095], key=lambda s:s[2]):
    print([round(v,1) if isinstance(v,float) else v for v in s])
