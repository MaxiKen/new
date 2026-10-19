import pymupdf, numpy as np
from collections import Counter
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'); p=d[0]
dr=p.get_drawings()
blue=[x for x in dr if x.get('color')==(0.450980007648468,0.8745099902153015,1.0)]
print(f"blue drawings {len(blue)} widths {Counter(x.get('width') for x in blue)} item types {Counter(i[0] for x in blue for i in x['items'])}")
print(f"total items {sum(len(x['items']) for x in blue)}")
# rect sizes: are any blue drawings outside map frame (legend samples)?
fr=lambda r: r.x0>=70 and r.x1<=2060 and r.y0>=350 and r.y1<=1980
print("blue outside frame:", sum(1 for x in blue if not fr(x['rect'])))
for x in blue:
    if not fr(x['rect']): print("  outside", x['rect'], len(x['items']))
# black fills survey
bf=[x for x in dr if x.get('fill')==(0.0,0.0,0.0)]
print(f"\nblack-fill drawings {len(bf)}")
areas=[]
for x in bf:
    r=x['rect']; areas.append((r.width*r.height, round(r.width,1), round(r.height,1), round((r.x0+r.x1)/2,0), round((r.y0+r.y1)/2,0), len(x['items'])))
areas.sort(reverse=True)
print("largest 30 black fills (bbox area pt2, w,h, cx,cy, nitems):")
for a in areas[:30]: print(a)
print("bbox area percentiles", np.percentile([a[0] for a in areas],[0,50,90,99,100]))
# where are medium black fills inside map frame? histogram by width
print("width hist", Counter(min(int(a[1]//2*2),30) for a in areas))
# white fills + grey fills (town symbols maybe white circles?)
for name,col in [("white",(1.,1.,1.)),("grey75",(0.7529399991035461,)*3)]:
    sel=[x for x in dr if x.get('fill')==col]
    print(name, len(sel), [(round(x['rect'].x0),round(x['rect'].y0),round(x['rect'].width,1)) for x in sel[:10]])
