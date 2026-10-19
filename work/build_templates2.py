import numpy as np, pandas as pd, cv2, pickle, json
from PIL import Image, ImageDraw
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
img=np.array(Image.open("work/legend_symbols_300dpi.png").convert("RGB")).astype(int)
ZOOM=300/72
ink=(np.max(np.abs(img-255),axis=2)>28)
n,lab,stats,cents=cv2.connectedComponentsWithStats(ink.astype(np.uint8),8)
comps=[]
for k in range(1,n):
    x,y,w,h,a=stats[k]
    if a<6: continue
    if cents[k][0]>119: continue  # text area
    comps.append((y,y+h,x,x+w,k,a))
comps.sort()
print(f"ink comps kept {len(comps)}")
# cluster by vertical gap < 2.2pt (=9px) between successive comp bboxes (sorted by y0, track cluster ymax)
gap_px=2.2*ZOOM
clusters=[]; cur=[comps[0]]; curymax=comps[0][1]
for c in comps[1:]:
    if c[0]-curymax<=gap_px:
        cur.append(c); curymax=max(curymax,c[1])
    else:
        clusters.append(cur); cur=[c]; curymax=c[1]
clusters.append(cur)
print(f"clusters found: {len(clusters)} (expect 67)")
for i,cl in enumerate(clusters):
    y0=min(c[0] for c in cl); y1=max(c[1] for c in cl); x0=min(c[2] for c in cl); x1=max(c[3] for c in cl)
    print(f"#{i+1} y {y0}-{y1} h_pt={(y1-y0)/ZOOM:.1f} w_pt={(x1-x0)/ZOOM:.1f} comps={len(cl)}")
# If count !=67, print diagnostics around mismatches (merge/split) - compare cluster centre y (pt, page) to label centres
rows=json.load(open("work/legend_rows.json"))
centres={}
for i in range(65): centres[i+1]=(rows[i][0]+rows[i][1])/2
centres[66]=(rows[65][0]+rows[65][1])/2+6; centres[67]=(1373.807+1397.344)/2
CLIPY0=325
for i,cl in enumerate(clusters):
    y0=min(c[0] for c in cl); y1=max(c[1] for c in cl)
    cpage=CLIPY0+((y0+y1)/2)/ZOOM
    nearest=min(centres, key=lambda k: abs(centres[k]-cpage))
    print(f"cluster{i+1} centre_page_y={cpage:.1f} nearest label leg{nearest} (label centre {centres[nearest]:.1f}, diff {cpage-centres[nearest]:+.1f}pt)")
