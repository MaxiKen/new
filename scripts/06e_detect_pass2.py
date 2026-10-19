"""Mineral detection PASS 2: ink-blob segmentation on native raster + template classification.
Centre = centre of blob ink bbox. Large/elongated components deferred to cluster handling."""
import sys, json, csv
sys.path.insert(0,"scripts")
import numpy as np, cv2

img = cv2.imread("work/mineral_native_map.png")  # BGR
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
S = hsv[:,:,1].astype(int); V = hsv[:,:,2].astype(int); Hh = hsv[:,:,0].astype(int)
ink = ((S>58)|(V<125)|((S>28)&(V<215))).astype(np.uint8)
# group fragments <=2px apart
grp = cv2.dilate(ink, np.ones((3,3),np.uint8))
n, lab, stats, cent = cv2.connectedComponentsWithStats(grp, 8)
print("components:", n-1)
meta=json.load(open("work/mineral_templates_meta.json")); tplz=np.load("work/mineral_templates.npz")
def ink_mask_rgb(a):
    a=a.astype(int); return (a.min(axis=2)<198)|((a.max(axis=2)-a.min(axis=2))>55)

# precompute per-template: BGR at scale 0.333, ink mask, ink mean colour(BGR), ink bbox size
tpl_info=[]
for i,m in enumerate(meta):
    t=cv2.cvtColor(tplz[f"t{i}"], cv2.COLOR_RGB2BGR)
    for s in (0.333,):
        ts=cv2.resize(t,(max(5,int(round(t.shape[1]*s))),max(5,int(round(t.shape[0]*s)))),interpolation=cv2.INTER_AREA)
        im=ink_mask_rgb(cv2.cvtColor(ts,cv2.COLOR_BGR2RGB))
        yy,xx=np.where(im)
        tpl_info.append(dict(idx=i,name=m["name"],pattern=m["pattern"],img=ts,mask=im,
            ibw=int(xx.max()-xx.min()+1), ibh=int(yy.max()-yy.min()+1),
            mean=ts[im].mean(axis=0) if im.any() else np.zeros(3)))
def classify(crop_bgr, crop_ink):
    """score templates against blob crop: resize tpl ink to blob ink bbox, compare mask IoU + colour."""
    yy,xx=np.where(crop_ink)
    bw,bh=int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)
    sub=crop_ink[yy.min():yy.max()+1, xx.min():xx.max()+1]
    subimg=crop_bgr[yy.min():yy.max()+1, xx.min():xx.max()+1]
    blob_mean=subimg[sub].mean(axis=0) if sub.any() else np.zeros(3)
    best=[]
    for ti in tpl_info:
        if ti["pattern"]: continue
        ar_t=ti["ibw"]/ti["ibh"]; ar_b=bw/bh
        if not (0.55<ar_b/ar_t<1.8): continue
        tm=cv2.resize(ti["mask"].astype(np.uint8),(bw,bh),interpolation=cv2.INTER_AREA)>0.4
        inter=(tm&sub).sum(); union=(tm|sub).sum()
        iou=inter/max(union,1)
        cd=np.linalg.norm((ti["mean"]-blob_mean)/255.0)
        score=0.72*iou+0.28*max(0,1-cd*1.6)
        best.append((score, ti["name"], round(float(iou),3), round(float(cd),3)))
    best.sort(reverse=True)
    return best[:3]

blobs=[]
H_img,W_img=ink.shape
for i in range(1,n):
    x,y,w,h,a = stats[i]
    if a<10: continue
    # true ink within bbox belonging to this component
    comp = (lab[y:y+h, x:x+w]==i)
    inkc = comp & (ink[y:y+h, x:x+w]>0)
    yy,xx=np.where(inkc)
    if len(yy)<8: continue
    ix0,ix1,iy0,iy1 = x+xx.min(), x+xx.max(), y+yy.min(), y+yy.max()
    bw,bh = ix1-ix0+1, iy1-iy0+1
    area=int(inkc.sum())
    blobs.append(dict(cx=(ix0+ix1)/2, cy=(iy0+iy1)/2, ix0=int(ix0),iy0=int(iy0),ix1=int(ix1),iy1=int(iy1),
                      bw=int(bw),bh=int(bh),area=area, fill=round(area/(bw*bh),3)))
print("blobs >=8 ink px:", len(blobs))
from collections import Counter
def sizeclass(b):
    if b["bw"]<=42 and b["bh"]<=42 and b["area"]<=800: return "S"
    return "L"
print(Counter(sizeclass(b) for b in blobs))
# classify S blobs
out=[]
for b in blobs:
    b["cls"]=sizeclass(b)
    if b["cls"]=="S" and b["area"]>=12:
        pad=2
        x0,x1=max(0,b["ix0"]-pad),min(W_img,b["ix1"]+pad+1)
        y0,y1=max(0,b["iy0"]-pad),min(H_img,b["iy1"]+pad+1)
        crop=img[y0:y1,x0:x1]; cink=ink[y0:y1,x0:x1]>0
        top=classify(crop,cink)
        if top:
            b["sym1"]=top[0][1]; b["score1"]=round(top[0][0],3); b["iou1"]=top[0][2]
            b["sym2"]=top[1][1] if len(top)>1 else ""; b["score2"]=round(top[1][0],3) if len(top)>1 else ""
        else:
            b["sym1"]=""; b["score1"]=0; b["iou1"]=0; b["sym2"]=""; b["score2"]=""
    out.append(b)
with open("work/mineral_blobs_pass2.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["cx","cy","ix0","iy0","ix1","iy1","bw","bh","area","fill","cls","sym1","score1","iou1","sym2","score2"])
    w.writeheader()
    for b in out: w.writerow({k:b.get(k,"") for k in w.fieldnames})
Sblobs=[b for b in out if b["cls"]=="S"]
print("S blobs classified:", len([b for b in Sblobs if b.get("sym1")]))
print(Counter(b["sym1"] for b in Sblobs if b.get("sym1")).most_common(70))
print("score1 percentiles:", [round(float(np.percentile([b["score1"] for b in Sblobs if b.get("sym1")],q)),2) for q in (0,25,50,75,100)])
