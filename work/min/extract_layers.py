import pymupdf, pickle, json
from collections import Counter
SRC='Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'
ON,OFF=0,2
base=pymupdf.open(SRC)
cfgs=[(c['number'], c['text'].replace('\x00',''), c['depth']) for c in base.layer_ui_configs()]
# ancestor chains via depth stack
anc={}; stack=[]
for num,name,depth in cfgs:
    while stack and stack[-1][1]>=depth: stack.pop()
    anc[num]=[s[0] for s in stack]
    stack.append((num,depth))
print("ancestors:", {n:(nm,anc[n]) for n,nm,_ in cfgs})

def fetch(onset):
    d=pymupdf.open(SRC)
    for c in d.layer_ui_configs():
        d.set_layer_ui_config(c['number'], ON if c['number'] in onset else OFF)
    p=d[0]
    return p.get_drawings(), p.get_text('words'), p.get_image_info(xrefs=True)

def dsig(x):
    items=[]
    for it in x['items']:
        op=it[0]
        pts=[]
        for a in it[1:]:
            if hasattr(a,'x'): pts.append((round(a.x,3),round(a.y,3)))
            elif hasattr(a,'x0'): pts.append((round(a.x0,3),round(a.y0,3),round(a.x1,3),round(a.y1,3)))
            else: pts.append(str(a))
        items.append((op,tuple(pts)))
    return (x['type'], x['color'], x['fill'], round(x['width'] or 0,3), tuple(items))

def wsig(w):
    return (round(w[0],2),round(w[1],2),round(w[2],2),round(w[3],2),w[4])

layers={}
for num,name,depth in cfgs:
    onset=set(anc[num])|{num}
    dr,wd,im=fetch(onset)
    dr0,wd0,im0=fetch(set(anc[num]))
    # multiset diff
    c0=Counter(dsig(x) for x in dr0)
    keep_d=[]
    for x in dr:
        s=dsig(x)
        if c0[s]>0: c0[s]-=1
        else: keep_d.append(x)
    cw0=Counter(wsig(w) for w in wd0)
    keep_w=[]
    for w in wd:
        s=wsig(w)
        if cw0[s]>0: cw0[s]-=1
        else: keep_w.append(w)
    xrefs0={i['xref'] for i in im0}
    keep_i=[i for i in im if i['xref'] not in xrefs0]
    layers[num]={'name':name,'drawings':keep_d,'words':keep_w,'images':keep_i}
    styles=Counter((x['type'], tuple(round(v,3) for v in x['color']) if x['color'] else None,
                    tuple(round(v,3) for v in x['fill']) if x['fill'] else None, round(x['width'] or 0,2)) for x in keep_d)
    print(f"\n#{num} {name!r}: own drawings={len(keep_d)} words={len(keep_w)} images={len(keep_i)}  (ancestors-only base d={len(dr0)} w={len(wd0)})")
    for k,v in styles.most_common(5): print(f"    n={v} {k}")
    if keep_w: print(f"    words: {[w[4] for w in keep_w[:15]]}")
    if keep_i: print(f"    images: {[(i['xref'], i['width'], i['height']) for i in keep_i]}")

with open('work/min/mineral_layers.pkl','wb') as f:
    pickle.dump(layers,f)
print("\nsaved work/min/mineral_layers.pkl")
print("totals own:", sum(len(v['drawings']) for v in layers.values()), "drawings;",
      sum(len(v['words']) for v in layers.values()), "words (vs all-on 10427/8086; parent-tagged content counted in parent layer)")
