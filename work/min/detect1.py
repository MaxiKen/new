import cv2, numpy as np, json, pickle, sys, time
import geopandas as gpd
sys.path.insert(0,'work/min')
from ncc import masked_ncc

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
# land mask in base px
adm=gpd.read_file('shapefiles/nigeria_admin0/nigeria_admin0.shp')
def ll2px(lon,lat):
    px=((lon-1.999778)/0.0063408528-74.2397)/0.959996
    py=((16.326633-lat)/0.0063497677-358.724)/0.959996
    return px,py
land=np.zeros((BH,BW),np.uint8)
for geom in adm.geometry:
    polys=[geom] if geom.geom_type=='Polygon' else list(geom.geoms)
    for poly in polys:
        xs,ys=poly.exterior.coords.xy
        px,py=ll2px(np.array(xs),np.array(ys))
        pts=np.stack([px,py],axis=1).astype(np.int32)
        cv2.fillPoly(land,[pts],1)
land=cv2.dilate(land,np.ones((9,9),np.uint8))
print("land px frac", land.mean())
cv2.imwrite('work/min/landmask.png',land*255)

WEAK={30:0.60,35:0.70,25:0.72,65:0.66,47:0.72,52:0.70,62:0.70,42:0.72,28:0.72,1:0.72,8:0.72,48:0.72,50:0.72,55:0.72,67:0.72,7:0.70,9:0.72,16:0.72,46:0.72}
def peaks_nms(ncc,thr,rad):
    ys,xs=np.where(ncc>=thr)
    if len(ys)==0: return []
    vals=ncc[ys,xs]
    order=np.argsort(-vals)
    keep=[]; taken=np.zeros(ncc.shape[:2],bool)
    H,W=ncc.shape
    for i in order:
        y,x=int(ys[i]),int(xs[i])
        if taken[y,x]: continue
        keep.append((x,y,float(vals[i])))
        y0,y1=max(0,y-rad),min(H,y+rad+1); x0,x1=max(0,x-rad),min(W,x+rad+1)
        taken[y0:y1,x0:x1]=True
    return keep
def subpix(ncc,x,y):
    if x<=0 or y<=0 or x>=ncc.shape[1]-1 or y>=ncc.shape[0]-1: return float(x),float(y)
    def q(a,b,c):
        d=(a-2*b+c)
        return 0.5*(a-c)/d if abs(d)>1e-9 else 0.0
    dx=q(ncc[y,x-1],ncc[y,x],ncc[y,x+1]); dy=q(ncc[y-1,x],ncc[y,x],ncc[y+1,x])
    dx=max(-1,min(1,dx)); dy=max(-1,min(1,dy))
    return x+dx,y+dy

all_det=[]
t0=time.time()
for leg in range(1,68):
    if leg==49: continue  # identical to 32; resolved in attribution
    tpl=cv2.imread(f'work/min/selftpl/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/selftpl/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    if tpl is None or m.sum()<6: print(leg,"skip"); continue
    ncc=masked_ncc(base,tpl,m)
    # apply land mask at symbol-centre positions
    cx,cy=meta[str(leg)]['center_xy']
    H,W=ncc.shape
    sub=land[int(round(cy)):int(round(cy))+H, int(round(cx)):int(round(cx))+W]
    if sub.shape==ncc.shape: ncc=np.where(sub>0,ncc,-1)
    thr=WEAK.get(leg,0.80)
    rad=max(4,int(0.55*min(tpl.shape[:2])))
    pk=peaks_nms(ncc,thr,rad)
    for (x,y,v) in pk:
        sx,sy=subpix(ncc,x,y)
        all_det.append({'leg':leg,'cx_px':float(sx+cx),'cy_px':float(sy+cy),'score':v,'stage':'complete'})
    print(f"leg{leg:02d} thr={thr} n={len(pk)}  ({time.time()-t0:.0f}s)")
pickle.dump(all_det,open('work/min/detections_stage1.pkl','wb'))
print("TOTAL",len(all_det))
