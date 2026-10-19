"""Mineral detection v2: colour/black channel separation, opening seeds, constrained growing,
seed merging, template classification. Centre = ink bbox centre."""
import sys, json, csv
sys.path.insert(0,"scripts")
import numpy as np, cv2
from collections import Counter

img = cv2.imread("work/mineral_native_map.png")
Hhsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
S=Hhsv[:,:,1].astype(int); V=Hhsv[:,:,2].astype(int)
Cink = ((S>58)|((S>28)&(V<215))).astype(np.uint8)
Kink = ((V<125)&(S<=80)).astype(np.uint8)
ALL = ((Cink|Kink)>0)
k2=np.ones((2,2),np.uint8)
def seeds(mask):
    op=cv2.morphologyEx(mask, cv2.MORPH_OPEN, k2)
    n,lab,stats,cent=cv2.connectedComponentsWithStats(op,8)
    out=[]
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]>=5:
            out.append((lab==i))
    return out
seed_masks=[]
# To avoid huge bool arrays per seed, store label maps instead
def seed_labels(mask):
    op=cv2.morphologyEx(mask, cv2.MORPH_OPEN, k2)
    n,lab,stats,cent=cv2.connectedComponentsWithStats(op,8)
    keep=np.zeros(n,bool)
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]>=5: keep[i]=True
    return lab, keep, stats
labC,keepC,statsC = seed_labels(Cink)
labK,keepK,statsK = seed_labels(Kink)
print("colour seeds:", keepC.sum(), " black seeds:", keepK.sum())

# candidate seeds as bboxes from opened stats; grow: dilate seed 2 iterations intersected with ALL ink
cands=[]
H_img,W_img=ALL.shape
def grow_bbox(lab, i, stats):
    x,y,w,h,a = stats[i]
    x0,x1=max(0,x-5),min(W_img,x+w+5); y0,y1=max(0,y-5),min(H_img,y+h+5)
    seed=(lab[y0:y1,x0:x1]==i).astype(np.uint8)
    g=seed.copy()
    for _ in range(2):
        g=cv2.dilate(g,np.ones((3,3),np.uint8)) & ALL[y0:y1,x0:x1].astype(np.uint8)
    yy,xx=np.where(g>0)
    return dict(ix0=int(x0+xx.min()),ix1=int(x0+xx.max()),iy0=int(y0+yy.min()),iy1=int(y0+yy.max()),
                ink=g, ox=x0, oy=y0)
for lab,keep,stats,ch in ((labC,keepC,statsC,"C"),(labK,keepK,statsK,"K")):
    for i in range(1,len(keep)):
        if keep[i]:
            d=grow_bbox(lab,i,stats); d["ch"]=ch; cands.append(d)
print("grown candidates:", len(cands))
# merge candidates whose bboxes overlap or gap<=2 (union-find)
parent=list(range(len(cands)))
def find(a):
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: parent[ra]=rb
def gap(a,b):
    dx=max(0, max(a["ix0"],b["ix0"])-min(a["ix1"],b["ix1"]))
    dy=max(0, max(a["iy0"],b["iy0"])-min(a["iy1"],b["iy1"]))
    return max(dx,dy)
# spatial hash by 32px cells
from collections import defaultdict
cells=defaultdict(list)
for i,d in enumerate(cands):
    cells[(d["ix0"]//32, d["iy0"]//32)].append(i)
for i,d in enumerate(cands):
    cx,cy=d["ix0"]//32, d["iy0"]//32
    for gx in (cx-1,cx,cx+1):
        for gy in (cy-1,cy,cy+1):
            for j in cells.get((gx,gy),[]):
                if j>i and gap(d,cands[j])<=2: union(i,j)
groups=defaultdict(list)
for i in range(len(cands)): groups[find(i)].append(i)
print("merged groups:", len(groups))
final=[]
for r,idxs in groups.items():
    ix0=min(cands[i]["ix0"] for i in idxs); ix1=max(cands[i]["ix1"] for i in idxs)
    iy0=min(cands[i]["iy0"] for i in idxs); iy1=max(cands[i]["iy1"] for i in idxs)
    # union ink in bbox from grown masks
    ink=np.zeros((iy1-iy0+1, ix1-ix0+1), np.uint8)
    for i in idxs:
        d=cands[i]
        sub=ink[d["iy0"]-iy0:d["iy0"]-iy0+d["ink"].shape[0], d["ix0"]-ix0:d["ix0"]-ix0+d["ink"].shape[1]]
        hh=min(sub.shape[0], d["ink"].shape[0]); ww=min(sub.shape[1], d["ink"].shape[1])
        sub[:hh,:ww] |= d["ink"][:hh,:ww]
    area=int((ink>0).sum())
    final.append(dict(ix0=ix0,ix1=ix1,iy0=iy0,iy1=iy1,bw=ix1-ix0+1,bh=iy1-iy0+1,area=area,
                      cx=(ix0+ix1)/2, cy=(iy0+iy1)/2, nseed=len(idxs), ink=ink))
print("final candidates:", len(final))
print("size classes:", Counter("sym" if (f["bw"]<=30 and f["bh"]<=26) else "big" for f in final))

# classification (as in 06e)
meta=json.load(open("work/mineral_templates_meta.json")); tplz=np.load("work/mineral_templates.npz")
def ink_mask_rgb(a):
    a=a.astype(int); return (a.min(axis=2)<198)|((a.max(axis=2)-a.min(axis=2))>55)
tpl_info=[]
for i,m in enumerate(meta):
    t=cv2.cvtColor(tplz[f"t{i}"], cv2.COLOR_RGB2BGR)
    s=0.333
    ts=cv2.resize(t,(max(5,int(round(t.shape[1]*s))),max(5,int(round(t.shape[0]*s)))),interpolation=cv2.INTER_AREA)
    im=ink_mask_rgb(cv2.cvtColor(ts,cv2.COLOR_BGR2RGB))
    yy,xx=np.where(im)
    tpl_info.append(dict(idx=i,name=m["name"],pattern=m["pattern"],img=ts,mask=im,
        ibw=int(xx.max()-xx.min()+1), ibh=int(yy.max()-yy.min()+1),
        mean=ts[im].mean(axis=0) if im.any() else np.zeros(3)))
def classify(b):
    ink=b["ink"]>0
    yy,xx=np.where(ink)
    sub=ink[yy.min():yy.max()+1, xx.min():xx.max()+1]
    crop=img[b["iy0"]+yy.min():b["iy0"]+yy.max()+1, b["ix0"]+xx.min():b["ix0"]+xx.max()+1]
    blob_mean=crop[sub].mean(axis=0) if sub.any() else np.zeros(3)
    bw,bh=sub.shape[1],sub.shape[0]
    scored=[]
    for ti in tpl_info:
        if ti["pattern"]: continue
        if not (0.5<(bw/bh)/(ti["ibw"]/ti["ibh"])<2.0): continue
        tm=cv2.resize(ti["mask"].astype(np.uint8),(bw,bh),interpolation=cv2.INTER_AREA)>0.4
        iou=(tm&sub).sum()/max((tm|sub).sum(),1)
        cd=float(np.linalg.norm((ti["mean"]-blob_mean)/255.0))
        scored.append((0.72*iou+0.28*max(0,1-cd*1.6), ti["name"], round(float(iou),3)))
    scored.sort(reverse=True)
    return scored[:2]

rows=[]
for b in final:
    cls = "sym" if (b["bw"]<=30 and b["bh"]<=26) else "big"
    sym1=sym2=""; sc1=sc2=iou1=""
    if cls=="sym" and b["area"]>=10:
        top=classify(b)
        if top:
            sc1,sym1,iou1=round(top[0][0],3),top[0][1],top[0][2]
            if len(top)>1: sc2,sym2=round(top[1][0],3),top[1][1]
    rows.append(dict(cx=b["cx"],cy=b["cy"],ix0=b["ix0"],iy0=b["iy0"],ix1=b["ix1"],iy1=b["iy1"],
        bw=b["bw"],bh=b["bh"],area=b["area"],nseed=b["nseed"],cls=cls,sym1=sym1,score1=sc1,iou1=iou1,sym2=sym2,score2=sc2))
with open("work/mineral_cands_v2.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
sym=[r for r in rows if r["cls"]=="sym"]
print("sym-class:", len(sym), " classified:", len([r for r in sym if r["sym1"]]))
print(Counter(r["sym1"] for r in sym if r["sym1"]).most_common(70))
# number coverage
nums=list(csv.DictReader(open("work/mineral_numbers.csv")))
from scipy.spatial import cKDTree
for label,subset in [("sym",sym),("sym sc>=0.45",[r for r in sym if r["score1"]!="" and float(r["score1"])>=0.45]),("all",rows)]:
    P=np.array([[r["cx"],r["cy"]] for r in subset]); N=np.array([[float(n["nat_x"]),float(n["nat_y"])] for n in nums])
    d,_=cKDTree(P).query(N)
    print(f" {label}: numbers with cand within 30px: {(d<=30).sum()}/989  within 40px: {(d<=40).sum()}")
# QA overlays
def overlay(name,x0,y0,x1,y1):
    c=img[y0:y1,x0:x1].copy()
    for r in rows:
        if x0<=r["cx"]<x1 and y0<=r["cy"]<y1:
            col=(0,200,0) if r["cls"]=="sym" else (255,0,255)
            cv2.rectangle(c,(r["ix0"]-x0,r["iy0"]-y0),(r["ix1"]-x0,r["iy1"]-y0),col,1)
            cv2.circle(c,(int(r["cx"]-x0),int(r["cy"]-y0)),1,(0,0,255),-1)
    for nn in nums:
        nx,ny=float(nn["nat_x"]),float(nn["nat_y"])
        if x0<=nx<x1 and y0<=ny<y1:
            cv2.circle(c,(int(nx-x0),int(ny-y0)),2,(255,120,0),1)
    cv2.imwrite(name, cv2.resize(c,(c.shape[1]*2,c.shape[0]*2),interpolation=cv2.INTER_NEAREST))
overlay("work/qa_detect_keffi.png",760,760,1160,1060)
overlay("work/qa_detect_sokoto.png",120,60,520,360)
print("QA overlays written")
