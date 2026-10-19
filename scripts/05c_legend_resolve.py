"""Resolve ambiguous geology legend matches using JPG-printed legend swatches + grey-friendly resampling."""
import sys, csv, json, collections
sys.path.insert(0,"scripts")
import numpy as np, cv2
from PIL import Image
import geopandas as gpd
Image.MAX_IMAGE_PIXELS=None
src=open("scripts/05_geology_legend.py").read()
start=src.index("LEGEND = ["); end=src.index("\n]\n",start)+3
exec(src[start:end])
def rgb2lab(rgb):
    im=np.asarray(rgb).clip(0,255).astype(np.uint8).reshape(1,-1,3)
    lab=cv2.cvtColor(im,cv2.COLOR_RGB2Lab).reshape(-1,3).astype(float)
    lab[:,0]*=100/255; lab[:,1]-=128; lab[:,2]-=128
    return lab
# --- iso resample grey-friendly ---
iso=cv2.imread("NGSA_map_geology_legend_isolated.png"); iso_rgb=cv2.cvtColor(iso,cv2.COLOR_BGR2RGB)
hsv_i=cv2.cvtColor(iso,cv2.COLOR_BGR2HSV)
cx=5469; pred_c=116.5+36.05*np.arange(92)
iso_leg=[]
for c in pred_c:
    y0,y1=int(c-7),int(c+8)
    sub=iso_rgb[y0:y1,cx-30:cx+18].reshape(-1,3).astype(float)
    vv=hsv_i[y0:y1,cx-30:cx+18,2].ravel()
    keep=(vv>55)&(vv<248)
    iso_leg.append(np.median(sub[keep],axis=0) if keep.sum()>20 else np.median(sub,axis=0))
iso_leg=np.array(iso_leg)
print("iso grey rows D/ODh/OGS (r60,61,63):", iso_leg[59].round(0), iso_leg[60].round(0), iso_leg[62].round(0))
# --- JPG legend swatches: find band ---
jpg=cv2.imread("pic NGSA geological-map-of-nigeria-.jpg"); Hj,Wj=jpg.shape[:2]
jpg_rgb=cv2.cvtColor(jpg,cv2.COLOR_BGR2RGB)
hsv_j=cv2.cvtColor(jpg,cv2.COLOR_BGR2HSV)
sat=hsv_j[:,:,1]
x_lo,x_hi=int(Wj*0.76),int(Wj*0.88)
colscore=(sat[:,x_lo:x_hi]>50).sum(axis=0)
top=np.argsort(-colscore)[:10]
print("JPG swatch col candidates:", [(int(x_lo+i),int(colscore[i])) for i in top])
cxj=x_lo+int(np.argmax(colscore))
band_sat=sat[:,cxj-30:cxj+30]; band_val=hsv_j[:,cxj-30:cxj+30,2]
rowfrac=((band_sat>20)|(band_val<200)).mean(axis=1)
segs=[]; in_s=False; st=0
for y in range(Hj):
    if rowfrac[y]>0.3 and not in_s: in_s=True; st=y
    if (rowfrac[y]<=0.3 or y==Hj-1) and in_s:
        in_s=False
        if y-st>=6: segs.append(((st+y-1)/2, st, y-1))
print(f"JPG legend segments: {len(segs)} first={segs[:3]} last={segs[-2:]}")
centres=np.array([s[0] for s in segs])
if len(segs)>=80:
    print("pitch median", np.median(np.diff(centres)))
# pitch model for 92 on JPG (search)
best=None
for p in np.arange(30,42.01,0.05):
    for a in centres[:3]:
        pred=a+p*np.arange(92)
        if pred[-1]>Hj-5: continue
        d=np.abs(centres[:,None]-pred[None,:]).min(axis=1)
        sc=(d<4).sum()
        if best is None or sc>best[0]: best=(sc,a,p)
print("JPG pitch model:", best)
_,aj,pj=best; pred_j=aj+pj*np.arange(92)
jpg_leg=[]
for c in pred_j:
    y0,y1=int(c-6),int(c+7)
    sub=jpg_rgb[y0:y1,cxj-26:cxj+16].reshape(-1,3).astype(float)
    vv=hsv_j[y0:y1,cxj-26:cxj+16,2].ravel()
    keep=(vv>55)&(vv<248)
    jpg_leg.append(np.median(sub[keep],axis=0) if keep.sum()>20 else np.median(sub,axis=0))
jpg_leg=np.array(jpg_leg)
print("JPG legend sample rows 1,62,65,68:", jpg_leg[0].round(0), jpg_leg[61].round(0), jpg_leg[64].round(0), jpg_leg[67].round(0))
# v2 colours + JPG-space medians (rebuild jpg_pal quickly for all units from warped overlap)
v2pil=Image.open("NGSA_map_geology_legend_isolated_v2.png"); pal=v2pil.getpalette(); idx=np.array(v2pil)
units=sorted([int(u) for u in np.unique(idx) if u!=0])
v2rgb=np.array([[pal[u*3],pal[u*3+1],pal[u*3+2]] for u in units],float)
v2idx=np.load("work/v2_filled_idx.npy")
reg=json.load(open("work/v2_to_lonlat.json")); A=np.array(reg["A_corrected"],dtype=np.float32)
warped=cv2.warpAffine(v2idx,A,(Wj,Hj),flags=cv2.INTER_NEAREST,borderValue=0)
jpg_med={}; rng=np.random.default_rng(1); kernel=np.ones((5,5),np.uint8)
jpg_rgbf=jpg_rgb.astype(float)
for u in units:
    m=(warped==u).astype(np.uint8)
    if m.sum()<100: jpg_med[u]=v2rgb[units.index(u)]; continue
    me=cv2.erode(m,kernel); ys,xs=np.where(me>0)
    if len(ys)>15000: sel=rng.choice(len(ys),15000,replace=False); ys,xs=ys[sel],xs[sel]
    if len(ys)==0: ys,xs=np.where(m>0)
    jpg_med[u]=np.median(jpg_rgbf[ys,xs],axis=0)
# Match in both spaces
lab_iso=rgb2lab(iso_leg); lab_jpgleg=rgb2lab(jpg_leg)
D_iso=np.sqrt(((rgb2lab(v2rgb)[:,None,:]-lab_iso[None,:,:])**2).sum(axis=2))
v2jpg=np.array([jpg_med[u] for u in units])
D_jpg=np.sqrt(((rgb2lab(v2jpg)[:,None,:]-lab_jpgleg[None,:,:])**2).sum(axis=2))
rows=[]
for k,u in enumerate(units):
    i_iso=int(np.argmin(D_iso[k])); d_iso=float(D_iso[k,i_iso]); s_iso=float(np.sort(D_iso[k])[1])
    i_jpg=int(np.argmin(D_jpg[k])); d_jpg=float(D_jpg[k,i_jpg]); s_jpg=float(np.sort(D_jpg[k])[1])
    # decision: if both agree -> High. If disagree, choose smaller normalized distance; flag.
    if i_iso==i_jpg:
        li, dd, mm, via = i_iso, min(d_iso,d_jpg), min(s_iso-d_iso, s_jpg-d_jpg), "iso+jpg agree"
        conf = "High" if dd<10 else "Medium"
    else:
        # prefer jpg-space if its distance much smaller (print source of v2), else iso
        if d_jpg < d_iso-3:
            li, dd, mm, via = i_jpg, d_jpg, s_jpg-d_jpg, f"jpg (iso said r{i_iso+1} d{d_iso:.1f})"
        elif d_iso < d_jpg-3:
            li, dd, mm, via = i_iso, d_iso, s_iso-d_iso, f"iso (jpg said r{i_jpg+1} d{d_jpg:.1f})"
        else:
            li, dd, mm, via = i_jpg, d_jpg, s_jpg-d_jpg, f"AMBIG iso r{i_iso+1}(d{d_iso:.1f}) vs jpg r{i_jpg+1}(d{d_jpg:.1f}) -> jpg"
        conf = "Medium" if dd<12 else "LOW-CHECK"
        if "AMBIG" in via: conf="Medium"
    alt = int(np.argsort(D_jpg[k])[1]) if ("jpg" in via) else int(np.argsort(D_iso[k])[1])
    code,lith,form=LEGEND[li]
    rows.append(dict(UNIT_IDX=u,CODE=code,LITHOLOGY=lith,FORMATION=form,LEG_ROW=li+1,DIST=dd,MARGIN=float(mm),CONF=conf,VIA=via,
                     ALT_CODE=LEGEND[alt][0], ALT_ROW=alt+1, V2_RGB=tuple(int(v) for v in v2rgb[k]), ISO_RGB=tuple(int(v) for v in iso_leg[li]), JPGLEG_RGB=tuple(int(v) for v in jpg_leg[li])))
    print(f" U{u:3d} -> r{li+1:2d} {code:6s} d={dd:5.1f} {conf:9s} [{via}] alt r{alt[0] if isinstance(alt,tuple) else alt+1} {LEGEND[alt][0]} | {lith[:44]}")
used=set(r["LEG_ROW"]-1 for r in rows)
print(f"\nmatched {len(used)}/92 unmatched rows: {[ (i+1,LEGEND[i][0]) for i in range(92) if i not in used]}")
print("conf units:", collections.Counter(r["CONF"] for r in rows))
with open("output/04_Tables/Geology_legend_match.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["UNIT_IDX","CODE","LITHOLOGY","FORMATION","LEG_ROW","Lab_dist","margin","CONFIDENCE","DECISION","ALT_CODE","ALT_ROW","V2_RGB","ISO_SWATCH_RGB","JPG_SWATCH_RGB"])
    for r in rows: w.writerow([r["UNIT_IDX"],r["CODE"],r["LITHOLOGY"],r["FORMATION"],r["LEG_ROW"],round(r["DIST"],2),round(r["MARGIN"],2),r["CONF"],r["VIA"],r["ALT_CODE"],r["ALT_ROW"],r["V2_RGB"],r["ISO_RGB"],r["JPGLEG_RGB"]])
json.dump(rows, open("work/geology_legend_rows.json","w"), indent=1, default=str)
np.save("work/legend_iso_rgb.npy", iso_leg); np.save("work/legend_jpg_rgb.npy", jpg_leg)
gdf=gpd.read_file("work/Geology_Rocks_complete_no_names.geojson")
lookup={r["UNIT_IDX"]:r for r in rows}
gdf["CODE"]=[lookup[int(u)]["CODE"] for u in gdf["UNIT_IDX"]]
gdf["LITHOLOGY"]=[lookup[int(u)]["LITHOLOGY"] for u in gdf["UNIT_IDX"]]
gdf["FORMATION"]=[lookup[int(u)]["FORMATION"] for u in gdf["UNIT_IDX"]]
gdf["LEG_CONF"]=[lookup[int(u)]["CONF"] for u in gdf["UNIT_IDX"]]
gdf=gdf[["POLY_ID","UNIT_IDX","CODE","LITHOLOGY","FORMATION","LEG_CONF","SRC","R","G","B","HEX","AREA_KM2","geometry"]]
gdf.to_file("output/02_Shapefiles/Geology_Rocks.shp")
gdf.to_file("work/Geology_Rocks_FINAL.geojson", driver="GeoJSON")
print("rewrote Geology_Rocks.shp")
# QML refresh with final labels
cats="".join(f'<category symbol="{r["UNIT_IDX"]}" value="{r["UNIT_IDX"]}" label="{r["CODE"]} - {r["LITHOLOGY"].replace("&","and").replace(chr(34),chr(39))}"/>\n' for r in rows)
syms="".join(f'<symbol type="fill" name="{r["UNIT_IDX"]}"><layer class="SimpleFill"><prop k="color" v="{r["V2_RGB"][0]},{r["V2_RGB"][1]},{r["V2_RGB"][2]},255"/><prop k="outline_color" v="60,60,60,255"/><prop k="outline_width" v="0.1"/></layer></symbol>\n' for r in rows)
open("output/02_Shapefiles/Geology_Rocks.qml","w").write(f"<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n<qgis version=\"3.34\"><renderer-v2 type=\"categorizedSymbol\" attr=\"UNIT_IDX\">\n<categories>{cats}</categories><symbols>{syms}</symbols></renderer-v2></qgis>")
print("QML refreshed")
