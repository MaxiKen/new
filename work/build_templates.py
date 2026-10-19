import pymupdf, numpy as np, pandas as pd, geopandas as gpd, json, cv2, pickle
from PIL import Image
from scipy.spatial import cKDTree
import warnings; warnings.filterwarnings('ignore')
base=cv2.imread("work/mineral_base_2060x1677.png")  # BGR
base_rgb=cv2.cvtColor(base,cv2.COLOR_BGR2RGB)
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")

# ---------- Legend templates from 300dpi render ----------
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'); p=d[0]
td=p.get_text("dict")
calcite=None
for bl in td["blocks"]:
    if bl["type"]!=0: continue
    for ln in bl["lines"]:
        s="".join(sp["text"] for sp in ln["spans"])
        if "alcite" in s: print("CALCITE line", repr(s), ln["bbox"]); calcite=ln["bbox"]
rows=json.load(open("work/legend_rows.json"))
# centres for leg_no 1..65 from rows[0..64]; 66 Lithium use first line centre; 67 Calcite
centres={}
for i in range(65): centres[i+1]=(rows[i][0]+rows[i][1])/2
centres[66]=(rows[65][0]+rows[65][1])/2 + 6  # two-line label, symbol approx between lines (adjust by ink search anyway)
centres[67]=(calcite[1]+calcite[3])/2 if calcite else centres[66]+31
legimg=np.array(Image.open("work/legend_symbols_300dpi.png").convert("RGB")).astype(int)
CLIPX0,CLIPY0,ZOOM=2082,325,300/72
def extract_legend(legno):
    cy_pt=centres[legno]
    # box in render px: x full clip width (32pt), y +-9pt around cy (search window larger to find ink)
    cx=(2098-CLIPX0)*ZOOM; cy=(cy_pt-CLIPY0)*ZOOM
    x0,x1=0,legimg.shape[1]; y0=int(max(0,cy-11*ZOOM)); y1=int(min(legimg.shape[0],cy+11*ZOOM))
    box=legimg[y0:y1,x0:x1]
    # ink = not near-white
    ink=(np.max(np.abs(box-255),axis=2)>28)
    # connected components, pick component whose centroid closest to (cx, cy-y0) with area>30
    n,lab,stats,cents=cv2.connectedComponentsWithStats(ink.astype(np.uint8),8)
    best=None
    for k in range(1,n):
        if stats[k,cv2.CC_STAT_AREA]<25: continue
        dist=np.hypot(cents[k][0]-cx, cents[k][1]-(cy-y0))
        # also dump nearby glyph parts: use bbox union of components within 45px of best? First find best primary
        if best is None or dist<best[0]: best=(dist,k)
    if best is None: return None
    k=best[1]
    # include all ink comps whose bbox overlaps primary bbox dilated 18px (letters inside symbol may be separate comps enclosed)
    bx,by,bw,bh,_=stats[k]
    mask=np.zeros(ink.shape,bool)
    for kk in range(1,n):
        x,y,w,h,a=stats[kk]
        if a<4: continue
        if x<bx+bw+18 and x+w>bx-18 and y<by+bh+18 and y+h>by-18: mask|=(lab==kk)
    ys,xs=np.where(mask)
    pad=int(3*ZOOM)
    X0,X1=max(0,xs.min()-pad),min(box.shape[1],xs.max()+pad+1); Y0,Y1=max(0,ys.min()-pad),min(box.shape[0],ys.max()+pad+1)
    tpl=box[Y0:Y1,X0:X1].astype(np.uint8)
    m=mask[Y0:Y1,X0:X1]
    # footprint: fill holes of ink (symbol interior enclosed by outline)
    mfill=m.copy()
    # flood fill background from borders on inverse
    inv=(~m).astype(np.uint8)
    nn,ll=cv2.connectedComponents(inv,4)
    border_labels=set(np.unique(np.concatenate([ll[0,:],ll[-1,:],ll[:,0],ll[:,-1]])))-{0}
    interior=np.isin(ll,[v for v in range(1,nn) if v not in border_labels])
    footprint=m|interior
    return tpl, footprint, (tpl.shape[1]/ZOOM, tpl.shape[0]/ZOOM)  # size in pt

legend_tpl={}
for _,r in leg.iterrows():
    no=int(r.legend_no)
    out=extract_legend(no)
    if out is None: print(f"leg{no} FAILED"); continue
    tpl,foot,ptsize=out
    legend_tpl[no]=(tpl,foot)
    print(f"leg{no:2d} {r.point_attribute_name:28s} legend tpl {tpl.shape[1]}x{tpl.shape[0]}px@300dpi = {ptsize[0]:.1f}x{ptsize[1]:.1f}pt footpx={int(foot.sum())}")
pickle.dump({"legend_tpl":legend_tpl},open("work/legend_tpl.pkl","wb"))
# contact sheet of legend templates at native + downscaled to base scale (factor: base 1.0417px/pt vs 4.1667 => 0.25)
cols=8; s=90
rowsn=int(np.ceil(67/cols))
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255))
from PIL import ImageDraw
dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(sorted(legend_tpl)):
    tpl,foot=legend_tpl[no]
    small=cv2.resize(tpl,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)
    big=Image.fromarray(small).resize((small.shape[1]*4,small.shape[0]*4),Image.NEAREST)
    x=(idx%cols)*s; y=(idx//cols)*s
    sheet.paste(big,(x+5,y+16)); dr.text((x+5,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:16]}",fill=(200,0,0))
sheet.save("work/legend_templates_sheet.png")
print("sheet saved; base-scale template sizes (px):")
for no in sorted(legend_tpl):
    tpl,_=legend_tpl[no]; print(no, (round(tpl.shape[1]*0.25,1), round(tpl.shape[0]*0.25,1)), end="; ")
print()
