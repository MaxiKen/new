import pymupdf, numpy as np
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf')
p=d[0]
dr=p.get_drawings()
# Long thin lines
verts=[]; horiz=[]
for x in dr:
    r=x['rect']
    if r.width<3 and r.height>500: verts.append((round(r.x0,1),round(r.y0,1),round(r.height,0),x.get('color'),x.get('width')))
    if r.height<3 and r.width>500: horiz.append((round(r.x0,1),round(r.y0,1),round(r.width,0),x.get('color'),x.get('width')))
print("long verticals:", verts[:30])
print("long horizontals:", horiz[:30])
# Small ticks near frame: drawings with rect y0 between 340-380 or 1940-1990, small height
def show(name, sel):
    print(f"\n{name} n={len(sel)}")
    for x in sorted(sel, key=lambda z:z['rect'].x0)[:40]:
        r=x['rect']; print(f" ({r.x0:.1f},{r.y0:.1f})-({r.x1:.1f},{r.y1:.1f}) col={x.get('color')} w={x.get('width')} items={x['items'][:2]}")
show("top edge ticks y 350-375", [x for x in dr if 350<x['rect'].y0<378 and x['rect'].height<30 and x['rect'].width<30])
show("bottom edge ticks y 1945-1980", [x for x in dr if 1945<x['rect'].y0<1985 and x['rect'].height<30 and x['rect'].width<30])
show("left edge ticks x 60-90", [x for x in dr if 55<x['rect'].x0<95 and x['rect'].height<30 and x['rect'].width<30])
# Frame rectangle: large rect strokes
big=[x for x in dr if x['rect'].width>1800 and x['rect'].height>1400]
print(f"\nbig rects n={len(big)}")
for x in big[:10]:
    r=x['rect']; print(f" ({r.x0:.2f},{r.y0:.2f})-({r.x1:.2f},{r.y1:.2f}) col={x.get('color')} fill={x.get('fill')} w={x.get('width')} nitems={len(x['items'])}")
