import pymupdf
from collections import Counter
SRC='Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'
ON, OFF = 0, 2
def col(c):
    if c is None: return None
    return tuple(round(v,3) for v in c)
base=pymupdf.open(SRC)
cfgs=[(c['number'], c['text'].replace('\x00','')) for c in base.layer_ui_configs()]
def collect(only=None):
    d=pymupdf.open(SRC)
    for num,name in cfgs:
        d.set_layer_ui_config(num, ON if num==only else OFF)
    return d, d[0]

d,p=collect(only=-999)
print(f"ALL OFF: drawings={len(p.get_drawings())} words={len(p.get_text('words'))} imginfo={len(p.get_image_info())}")
tot_draw=tot_words=0
for num,name in cfgs:
    d,p=collect(only=num)
    states={c['number']:c['on'] for c in d.layer_ui_configs()}
    dr=p.get_drawings(); words=p.get_text('words'); imgs=p.get_image_info()
    tot_draw+=len(dr); tot_words+=len(words)
    styles=Counter((x['type'], col(x['color']), col(x['fill']), round(x['width'] or 0,2)) for x in dr)
    print(f"\nONLY #{num} {name!r} (on={states.get(num)}): drawings={len(dr)} words={len(words)} images={len(imgs)}")
    for k,v in styles.most_common(4): print(f"    style n={v} {k}")
    if words: print(f"    words sample: {[w[4] for w in words[:15]]}")
    if dr:
        print(f"    bbox x {min(x['rect'].x0 for x in dr):.0f}..{max(x['rect'].x1 for x in dr):.0f} y {min(x['rect'].y0 for x in dr):.0f}..{max(x['rect'].y1 for x in dr):.0f}")
print(f"\nSUM per-layer: drawings={tot_draw} words={tot_words} (all-on totals: 10427 / 8086)")
