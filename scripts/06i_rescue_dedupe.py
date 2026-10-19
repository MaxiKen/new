"""Rescue detections for numbers lacking nearby candidate; dedupe; triage into main vs review."""
import sys, json, csv
sys.path.insert(0,"scripts")
import numpy as np, cv2
from scipy.spatial import cKDTree
from collections import Counter

img=cv2.imread("work/mineral_native_map.png")
H_img,W_img=img.shape[:2]
rows=list(csv.DictReader(open("work/mineral_cands_v4.csv")))
for r in rows:
    r["cx"]=float(r["cx"]); r["cy"]=float(r["cy"])
    r["score1"]=float(r["score1"]) if r["score1"] not in ("","None") else 0.0
nums=list(csv.DictReader(open("work/mineral_numbers.csv")))
N=np.array([[float(n["nat_x"]),float(n["nat_y"])] for n in nums])

def coverage(pts):
    P=np.array([[p["cx"],p["cy"]] for p in pts]); d,_=cKDTree(P).query(N)
    return d
main=[r for r in rows if r["cls"] in ("sym","pattern")]
d=coverage(rows)
missing=[i for i in range(len(nums)) if d[i]>30]
print(f"numbers without candidate within 30px: {len(missing)}")

meta=json.load(open("work/mineral_templates_meta.json")); tplz=np.load("work/mineral_templates.npz")
TPLS=[]
for i,m in enumerate(meta):
    if m["pattern"]: continue
    TPLS.append((m["name"], cv2.cvtColor(tplz[f"t{i}"],cv2.COLOR_RGB2BGR), m["ink_bbox"]))
from collections import defaultdict

def rescue_search(nx,ny,exist_P):
    W2=48
    x0,x1=max(0,int(nx-W2)),min(W_img,int(nx+W2+1)); y0,y1=max(0,int(ny-W2)),min(H_img,int(ny+W2+1))
    sub=img[y0:y1,x0:x1]
    best=None
    for name,tpl,ib in TPLS:
        for s in (0.28,0.31,0.333,0.36,0.39,0.42,0.45):
            tw,th=max(5,int(round(tpl.shape[1]*s))),max(5,int(round(tpl.shape[0]*s)))
            if tw>=sub.shape[1] or th>=sub.shape[0]: continue
            t=cv2.resize(tpl,(tw,th),interpolation=cv2.INTER_AREA)
            res=cv2.matchTemplate(sub,t,cv2.TM_CCOEFF_NORMED)
            k=np.argmax(res); yy,xx=np.unravel_index(k,res.shape)
            cx=x0+xx+(ib[0]+ib[2])/2*s; cy=y0+yy+(ib[1]+ib[3])/2*s
            if (cx-nx)**2+(cy-ny)**2>44**2: continue
            dd,_=cKDTree(exist_P).query([[cx,cy]])
            if dd[0]<7: continue
            if best is None or res[yy,xx]>best[0]: best=(float(res[yy,xx]),name,cx,cy,tw,th)
    return best

added=[]
exist_P=np.array([[r["cx"],r["cy"]] for r in rows])
for i in missing:
    nx,ny=N[i]
    b=rescue_search(nx,ny,exist_P)
    if b and b[0]>=0.55:
        sc,name,cx,cy,tw,th=b
        r=dict(cx=cx,cy=cy,ix0=int(cx-tw/2),iy0=int(cy-th/2),ix1=int(cx+tw/2),iy1=int(cy+th/2),
               bw=tw,bh=th,area="",nseed=0,cls="sym",src="rescue",chs="",sym1=name,score1=round(sc,3),iou1="",sym2="",score2="")
        added.append(r); rows.append(r); exist_P=np.vstack([exist_P,[cx,cy]])
print("rescued by NCC:", len(added))
d=coverage(rows)
still=[i for i in range(len(nums)) if d[i]>30]
print("still missing:", len(still))
for i in still:
    n=nums[i]
    rows.append(dict(cx=float(n["nat_x"]),cy=float(n["nat_y"]),ix0="",iy0="",ix1="",iy1="",bw="",bh="",area="",
        nseed=0,cls="number_only",src="number_only",chs="",sym1="",score1=0.0,iou1="",sym2="",score2="",
        force_number=f'{n["zone"]}{n["number"]}'))

# Dedupe: sort by priority, suppress <6px; merge 6-9px same sym1
PRIO={"blob":0,"pattern":1,"cluster":2,"rescue":3,"number_only":4}
rows.sort(key=lambda r:(PRIO.get(r["src"],5), -r["score1"]))
kept=[]; keptP=[]
for r in rows:
    if r["cls"]!="number_only" and keptP:
        dd,idx=cKDTree(np.array(keptP)).query([[r["cx"],r["cy"]]])
        if dd[0]<8.5: continue
    kept.append(r)
    if r["cls"]!="number_only": keptP.append([r["cx"],r["cy"]])
print(f"after dedupe: {len(kept)} (was {len(rows)})")
# triage: unnumbered low-score -> review
P=np.array([[r["cx"],r["cy"]] for r in kept]); dn,_=cKDTree(N).query(P)
for r,dist in zip(kept,dn):
    r["dist_nearest_number"]=round(float(dist),1)
    r["review"]=""
    if r["cls"]=="number_only": r["review"]="NUMBER_ONLY"
    elif r["cls"]=="big": r["review"]="BIG_UNRESOLVED"
    elif dist>45:
        thr = 0.68 if r["src"]=="cluster" else (0.55 if r["src"]=="rescue" else 0.45)
        if r["cls"]!="pattern" and r["score1"]<thr: r["review"]="UNNUMBERED_LOW"
main_pts=[r for r in kept if not r["review"]]
rev_pts=[r for r in kept if r["review"]]
print("main:",len(main_pts)," review:",len(rev_pts), Counter(r["review"] for r in rev_pts))
print("main by src:", Counter(r["src"] for r in main_pts))
d=coverage(main_pts+rev_pts)
print("numbers coverage (all kept): <=25px", (d<=25).sum(), "<=30px", (d<=30).sum(), "<=40px", (d<=40).sum(), "/", len(nums))
fields=["cx","cy","ix0","iy0","ix1","iy1","bw","bh","area","nseed","cls","src","chs","sym1","score1","iou1","sym2","score2","dist_nearest_number","review"]
with open("work/mineral_points_v1.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader()
    for r in kept: w.writerow(r)
print("wrote work/mineral_points_v1.csv")
