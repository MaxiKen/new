"""Mineral symbol detection PASS 1 (complete matches): multi-scale colour NCC on native raster.
Centre = centre of template ink bounding box at best match (sub-pixel refined)."""
import sys, json, csv
sys.path.insert(0,"scripts")
import numpy as np, cv2
import common as C

canvas = cv2.imread("work/mineral_native_map.png")  # BGR
H,W = canvas.shape[:2]
meta = json.load(open("work/mineral_templates_meta.json"))
tplz = np.load("work/mineral_templates.npz")
SCALES = [0.295, 0.333, 0.375, 0.42]   # legend px -> native px (nominal 0.3333)
THR = 0.68

def ink_mask_rgb(arr):
    a=arr.astype(int); mn=a.min(axis=2); mx=a.max(axis=2)
    return (mn<198)|((mx-mn)>55)

cands=[]
for i,m in enumerate(meta):
    if m["pattern"]: continue
    tpl_rgb = tplz[f"t{i}"]
    tpl = cv2.cvtColor(tpl_rgb, cv2.COLOR_RGB2BGR)
    ib = m["ink_bbox"]  # xmin,ymin,xmax,ymax in legend px
    for s in SCALES:
        tw,th = max(5,int(round(tpl.shape[1]*s))), max(5,int(round(tpl.shape[0]*s)))
        t = cv2.resize(tpl,(tw,th),interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(canvas, t, cv2.TM_CCOEFF_NORMED)
        # local maxima above THR
        mx = cv2.dilate(res, np.ones((5,5),np.uint8))
        ys,xs = np.where((res>=mx-1e-9)&(res>=THR))
        cx_off = (ib[0]+ib[2])/2*s; cy_off=(ib[1]+ib[3])/2*s
        for y,x in zip(ys,xs):
            # subpixel refine 3x3 weighted
            x0,x1=max(0,x-1),min(res.shape[1],x+2); y0,y1=max(0,y-1),min(res.shape[0],y+2)
            wgt=np.clip(res[y0:y1,x0:x1]-THR,0,None)
            if wgt.sum()>0:
                yy,xx=np.mgrid[y0:y1,x0:x1]
                rx=float((xx*wgt).sum()/wgt.sum()); ry=float((yy*wgt).sum()/wgt.sum())
            else: rx,ry=float(x),float(y)
            cands.append(dict(cx=rx+cx_off, cy=ry+cy_off, score=float(res[y,x]), tpl=i,
                              name=m["name"], scale=s, tw=tw, th=th))
    print(f" tpl {i:02d} {m['name'][:34]:34s} cum cands {len(cands)}")
print("raw candidates:", len(cands))
# Global NMS: highest score first; suppress within R px
cands.sort(key=lambda d:-d["score"])
kept=[]
from scipy.spatial import cKDTree
pts=[]
for d in cands:
    if pts:
        tree=cKDTree(np.array(pts))
        dist,_=tree.query([d["cx"],d["cy"]])
        R=max(6.0, 0.45*min(d["tw"],d["th"]))
        if dist < R: continue
    kept.append(d); pts.append([d["cx"],d["cy"]])
print("after NMS:", len(kept))
with open("work/mineral_detect_pass1.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["cx","cy","score","tpl","name","scale","tw","th"])
    w.writeheader()
    for d in kept: w.writerow({k:(round(v,3) if isinstance(v,float) else v) for k,v in d.items()})
from collections import Counter
print(Counter(d["name"] for d in kept).most_common(70))
print("score deciles:", [round(float(np.percentile([d['score'] for d in kept],q)),2) for q in range(0,101,10)])
