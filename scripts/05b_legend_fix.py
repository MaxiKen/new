"""Re-sample 92 legend swatches via pitch model; re-match v2 units; rewrite Geology_Rocks attributes."""
import sys, csv, json
sys.path.insert(0,"scripts")
import numpy as np, cv2
from PIL import Image
import geopandas as gpd
Image.MAX_IMAGE_PIXELS=None
exec(open("scripts/05_geology_legend.py").read().split('print(f"legend rows')[0].split("LEGEND = ")[1].join(["LEGEND = (",""]) ) if False else ""
# Import LEGEND by exec of the list portion safely:
src=open("scripts/05_geology_legend.py").read()
start=src.index("LEGEND = ["); end=src.index("\n]\n", start)+3
LEGEND=None
exec(src[start:end])
print("legend", len(LEGEND))
iso=cv2.imread("NGSA_map_geology_legend_isolated.png"); H,W=iso.shape[:2]
iso_rgb=cv2.cvtColor(iso,cv2.COLOR_BGR2RGB)
hsv=cv2.cvtColor(iso,cv2.COLOR_BGR2HSV)
cx=5469
x_lo,x_hi=cx-35,cx+35
band_sat=hsv[:,x_lo:x_hi,1]; band_val=hsv[:,x_lo:x_hi,2]
rowfrac=((band_sat>16)|(band_val<205)).mean(axis=1)
segs=[]; in_s=False; st=0
for y in range(H):
    if rowfrac[y]>0.30 and not in_s: in_s=True; st=y
    if (rowfrac[y]<=0.30 or y==H-1) and in_s:
        in_s=False
        if y-st>=8: segs.append((st,y-1))
print(f"segments (low thresh): {len(segs)}")
centres=np.array([(a+b)/2 for a,b in segs])
print("pitch diffs:", np.round(np.diff(centres),1))
# Fit arithmetic progression for 92 rows: search pitch p, offset a maximizing centres matched within 5px
best=None
for p in np.arange(34.0,40.01,0.05):
    # offset search via first centre alignment candidates
    for a in centres[:3]:
        pred=a+p*np.arange(92)
        if pred[-1]>H-10: continue
        # count centres with a pred within 5
        d=np.abs(centres[:,None]-pred[None,:]).min(axis=1)
        score=(d<5).sum() - 0.01*np.median(d[d<5]) if (d<5).any() else 0
        if best is None or score>best[0]: best=(score,a,p)
score,a,p=best
print(f"pitch model: a={a:.2f} pitch={p:.3f} score={score} last pred={a+p*91:.1f} (H={H})")
pred_c=a+p*np.arange(92)
d=np.abs(centres[:,None]-pred_c[None,:]).min(axis=1)
print(f"detected centres matched to model (<5px): {(d<5).sum()}/{len(centres)}; unmatched centres: {centres[d>=5]}")
# Sample each row: box rows centre+-7, cols: swatch left part [cx-30,cx+5] to avoid code glyph centre-right? Code text is dark; take median of pixels with val>70 (exclude black text) & not near-white border: use pixels with sat>12 or val<245... median robust anyway if box mostly fill.
seg_rgb=[]
for c in pred_c:
    y0,y1=int(c-7),int(c+8)
    sub=iso_rgb[y0:y1, cx-30:cx+18].reshape(-1,3).astype(float)
    vv=hsv[y0:y1, cx-30:cx+18,2].ravel(); ss=hsv[y0:y1, cx-30:cx+18,1].ravel()
    keep=(vv>75)&(ss>10)
    if keep.sum()<30: keep=(vv>75)
    seg_rgb.append(np.median(sub[keep],axis=0) if keep.any() else np.median(sub,axis=0))
seg_rgb=np.array(seg_rgb)
print("row samples:\n", seg_rgb[:4].round(0), "\n", seg_rgb[-3:].round(0))
# Match v2
v2pil=Image.open("NGSA_map_geology_legend_isolated_v2.png"); pal=v2pil.getpalette(); idx=np.array(v2pil)
units=sorted([int(u) for u in np.unique(idx) if u!=0])
v2rgb=np.array([[pal[u*3],pal[u*3+1],pal[u*3+2]] for u in units],float)
def rgb2lab(rgb):
    im=rgb.clip(0,255).astype(np.uint8).reshape(1,-1,3)
    lab=cv2.cvtColor(im,cv2.COLOR_RGB2Lab).reshape(-1,3).astype(float)
    lab[:,0]*=100/255; lab[:,1]-=128; lab[:,2]-=128
    return lab
lab_leg=rgb2lab(seg_rgb); lab_v2=rgb2lab(v2rgb)
D=np.sqrt(((lab_v2[:,None,:]-lab_leg[None,:,:])**2).sum(axis=2))
best_i=np.argmin(D,axis=1); bestd=D[np.arange(len(units)),best_i]; second=np.sort(D,axis=1)[:,1]
rows=[]
for k,u in enumerate(units):
    li=int(best_i[k]); code,lith,form=LEGEND[li]
    conf="High" if bestd[k]<8 and (second[k]-bestd[k])>3 else ("Medium" if bestd[k]<14 else "LOW-CHECK")
    rows.append(dict(UNIT_IDX=u,CODE=code,LITHOLOGY=lith,FORMATION=form,LEG_ROW=li+1,DIST=float(bestd[k]),MARGIN=float(second[k]-bestd[k]),CONF=conf,V2_RGB=tuple(int(v) for v in v2rgb[k]),LEG_RGB=tuple(int(v) for v in seg_rgb[li])))
    print(f" U{u:3d} {tuple(int(v) for v in v2rgb[k])} -> r{li+1:2d} {code:6s} d={bestd[k]:5.1f} m={second[k]-bestd[k]:5.1f} {conf:9s} {lith[:50]}")
used=set(int(b) for b in best_i)
print(f"\nmatched legend rows {len(used)}/92; UNMATCHED:")
for i,(code,lith,form) in enumerate(LEGEND):
    if i not in used: print(f" r{i+1} {code} {lith} | swatch {tuple(int(v) for v in seg_rgb[i])}")
import collections
print("multi-unit legend rows:", {LEGEND[k][0]+f"(r{k+1})":v for k,v in collections.Counter(int(b) for b in best_i).items() if v>1})
with open("output/04_Tables/Geology_legend_match.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["UNIT_IDX","CODE","LITHOLOGY","FORMATION","LEG_ROW","Lab_dist","margin","CONFIDENCE","V2_RGB","LEGEND_RGB"])
    for r in rows: w.writerow([r["UNIT_IDX"],r["CODE"],r["LITHOLOGY"],r["FORMATION"],r["LEG_ROW"],round(r["DIST"],2),round(r["MARGIN"],2),r["CONF"],r["V2_RGB"],r["LEG_RGB"]])
with open("output/04_Tables/Geology_legend_transcribed.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["LEG_ROW","CODE","LITHOLOGY","FORMATION","SWATCH_RGB"])
    for i,(code,lith,form) in enumerate(LEGEND): w.writerow([i+1,code,lith,form,tuple(int(v) for v in seg_rgb[i])])
json.dump(rows, open("work/geology_legend_rows.json","w"), indent=1, default=str)
gdf=gpd.read_file("work/Geology_Rocks_complete_no_names.geojson")
lookup={r["UNIT_IDX"]:r for r in rows}
gdf["CODE"]=[lookup[int(u)]["CODE"] for u in gdf["UNIT_IDX"]]
gdf["LITHOLOGY"]=[lookup[int(u)]["LITHOLOGY"] for u in gdf["UNIT_IDX"]]
gdf["FORMATION"]=[lookup[int(u)]["FORMATION"] for u in gdf["UNIT_IDX"]]
gdf["LEG_CONF"]=[lookup[int(u)]["CONF"] for u in gdf["UNIT_IDX"]]
gdf=gdf[["POLY_ID","UNIT_IDX","CODE","LITHOLOGY","FORMATION","LEG_CONF","SRC","R","G","B","HEX","AREA_KM2","geometry"]]
gdf.to_file("output/02_Shapefiles/Geology_Rocks.shp")
gdf.to_file("work/Geology_Rocks_FINAL.geojson", driver="GeoJSON")
print(f"rewrote Geology_Rocks.shp; conf: {gdf['LEG_CONF'].value_counts().to_dict()} (polygons)")
# per-unit confidence summary
print("units by conf:", collections.Counter(r["CONF"] for r in rows))
print("LOW units:", [(r["UNIT_IDX"],r["CODE"],round(r["DIST"],1)) for r in rows if r["CONF"]=="LOW-CHECK"])
