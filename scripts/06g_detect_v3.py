"""Mineral detection v3 (see header notes in repo README-gen): channel seeds + outline symbols +
pattern patches + cluster template-splitting + masked-NCC classification."""
import sys, json, csv
sys.path.insert(0,"scripts")
import numpy as np, cv2
from collections import Counter, defaultdict

img = cv2.imread("work/mineral_native_map.png")
H_img,W_img = img.shape[:2]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
S=hsv[:,:,1].astype(int); V=hsv[:,:,2].astype(int)
Cink = ((S>58)|((S>28)&(V<215))).astype(np.uint8)
Kink = ((V<125)&(S<=80)).astype(np.uint8)
ALL = ((Cink|Kink)>0).astype(np.uint8)
k2=np.ones((2,2),np.uint8); k3=np.ones((3,3),np.uint8)

seeds=[]  # dict(bbox from grown ink, ink mask small, ox,oy, ch)
def add_seeds_from_labels(lab, keep_ids, ch):
    for i in keep_ids:
        ys,xs=np.where(lab==i)
        x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
        gx0,gx1=max(0,x0-3),min(W_img,x1+4); gy0,gy1=max(0,y0-3),min(H_img,y1+4)
        seed=((lab[gy0:gy1,gx0:gx1]==i)).astype(np.uint8)
        g=cv2.dilate(seed,k3) & ALL[gy0:gy1,gx0:gx1]
        yy,xx=np.where(g>0)
        seeds.append(dict(ix0=int(gx0+xx.min()),ix1=int(gx0+xx.max()),iy0=int(gy0+yy.min()),iy1=int(gy0+yy.max()),ink=g,ox=gx0,oy=gy0,ch=ch))

# colour seeds: open2 comps that are compact OR survive open3
op2=cv2.morphologyEx(Cink,cv2.MORPH_OPEN,k2); op3=cv2.morphologyEx(Cink,cv2.MORPH_OPEN,k3)
n,lab,stats,cent=cv2.connectedComponentsWithStats(op2,8)
keep=[]
for i in range(1,n):
    x,y,w,h,a=stats[i]
    if a<5: continue
    compact = (w<=22 and h<=22 and a/(w*h)>=0.32)
    in3 = op3[y:y+h,x:x+w][lab[y:y+h,x:x+w]==i].sum()>=4
    if compact or in3: keep.append(i)
print("colour seeds:", len(keep), "of", n-1)
add_seeds_from_labels(lab, keep, "C")
# black seeds: open2 solid cores
op2k=cv2.morphologyEx(Kink,cv2.MORPH_OPEN,k2)
n,lab,stats,cent=cv2.connectedComponentsWithStats(op2k,8)
keep=[i for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>=5]
print("black solid seeds:", len(keep))
add_seeds_from_labels(lab, keep, "K")
# outline symbols: raw Kink components of symbol size
n,lab,stats,cent=cv2.connectedComponentsWithStats(Kink,8)
keep=[]
for i in range(1,n):
    x,y,w,h,a=stats[i]
    if 6<=w<=26 and 6<=h<=26 and 12<=a<=320:
        keep.append(i)
print("black outline comps:", len(keep))
add_seeds_from_labels(lab, keep, "O")
print("total seeds:", len(seeds))

# merge seeds bbox gap<=2 if combined <=30x26
parent=list(range(len(seeds)))
def find(a):
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: parent[ra]=rb
cells=defaultdict(list)
for i,d in enumerate(seeds): cells[(d["ix0"]//32,d["iy0"]//32)].append(i)
for i,d in enumerate(seeds):
    for gx in (d["ix0"]//32-1,d["ix0"]//32,d["ix0"]//32+1):
        for gy in (d["iy0"]//32-1,d["iy0"]//32,d["iy0"]//32+1):
            for j in cells.get((gx,gy),[]):
                if j<=i: continue
                e=seeds[j]
                gdx=max(0,max(d["ix0"],e["ix0"])-min(d["ix1"],e["ix1"])); gdy=max(0,max(d["iy0"],e["iy0"])-min(d["iy1"],e["iy1"]))
                if max(gdx,gdy)<=2:
                    cw=max(d["ix1"],e["ix1"])-min(d["ix0"],e["ix0"])+1; chh=max(d["iy1"],e["iy1"])-min(d["iy0"],e["iy0"])+1
                    if cw<=30 and chh<=26: union(i,j)
groups=defaultdict(list)
for i in range(len(seeds)): groups[find(i)].append(i)
cands=[]
for r,idxs in groups.items():
    ix0=min(seeds[i]["ix0"] for i in idxs); ix1=max(seeds[i]["ix1"] for i in idxs)
    iy0=min(seeds[i]["iy0"] for i in idxs); iy1=max(seeds[i]["iy1"] for i in idxs)
    ink=np.zeros((iy1-iy0+1,ix1-ix0+1),np.uint8)
    for i in idxs:
        d=seeds[i]; sub=ink[d["iy0"]-iy0:d["iy0"]-iy0+d["ink"].shape[0], d["ix0"]-ix0:d["ix0"]-ix0+d["ink"].shape[1]]
        hh=min(sub.shape[0],d["ink"].shape[0]); ww=min(sub.shape[1],d["ink"].shape[1]); sub[:hh,:ww]|=d["ink"][:hh,:ww]
    cands.append(dict(ix0=ix0,ix1=ix1,iy0=iy0,iy1=iy1,bw=ix1-ix0+1,bh=iy1-iy0+1,area=int((ink>0).sum()),
                      cx=(ix0+ix1)/2,cy=(iy0+iy1)/2,nseed=len(idxs),ink=ink,src="blob"))
print("candidates after merge:", len(cands))

# green pattern patches (Limestone/Marl)
B,G,R = img[:,:,0].astype(int), img[:,:,1].astype(int), img[:,:,2].astype(int)
green = ((G>R+25)&(G>B+25)&(S>70)).astype(np.uint8)
closed = cv2.morphologyEx(green, cv2.MORPH_CLOSE, np.ones((5,5),np.uint8))
n,lab,stats,cent=cv2.connectedComponentsWithStats(closed,8)
patches=[]
for i in range(1,n):
    x,y,w,h,a=stats[i]
    gpx = green[y:y+h,x:x+w][lab[y:y+h,x:x+w]==i].sum()
    if w>=15 and h>=8 and gpx>=35 and gpx/(w*h)<0.8:
        patches.append((x,y,x+w-1,y+h-1))
print("green pattern patches:", len(patches))
added=0
for (x0,y0,x1,y1) in patches:
    # skip if a sym candidate centre inside and patch small (solid green symbol caught as patch)
    inside=[c for c in cands if x0<=c["cx"]<=x1 and y0<=c["cy"]<=y1]
    if inside and (x1-x0+1)*(y1-y0+1)<700: continue
    ink = green[y0:y1+1,x0:x1+1].copy()
    cands = [c for c in cands if not (x0<=c["cx"]<=x1 and y0<=c["cy"]<=y1)] if inside else cands
    yy,xx=np.where(ink>0)
    cands.append(dict(ix0=x0,ix1=x1,iy0=y0,iy1=y1,bw=x1-x0+1,bh=y1-y0+1,area=int((ink>0).sum()),
                      cx=float(x0+xx.mean()),cy=float(y0+yy.mean()),nseed=0,ink=ink,src="pattern"))
    added+=1
print("patches added as candidates:", added, " total:", len(cands))

# templates
meta=json.load(open("work/mineral_templates_meta.json")); tplz=np.load("work/mineral_templates.npz")
def ink_mask_rgb(a):
    a=a.astype(int); return (a.min(axis=2)<198)|((a.max(axis=2)-a.min(axis=2))>55)
TPLS=[]
for i,m in enumerate(meta):
    t=cv2.cvtColor(tplz[f"t{i}"], cv2.COLOR_RGB2BGR)
    TPLS.append(dict(idx=i,name=m["name"],pattern=m["pattern"],tpl=t, ib=m["ink_bbox"]))

def classify_v2(b):
    """masked colour NCC at fixed nominal scale, blob crop vs template resized to same canvas."""
    x0,x1,y0,y1=b["ix0"],b["ix1"],b["iy0"],b["iy1"]
    crop=img[y0:y1+1,x0:x1+1].astype(float)
    bink=(b["ink"]>0)
    CS=36
    cc=np.full((CS,CS,3),255.0); cm=np.zeros((CS,CS),bool)
    sc=min(CS/crop.shape[1],CS/crop.shape[0])
    rs=cv2.resize(crop.astype(np.uint8),(max(2,int(crop.shape[1]*sc)),max(2,int(crop.shape[0]*sc))),interpolation=cv2.INTER_AREA).astype(float)
    rm=cv2.resize(bink.astype(np.uint8),(rs.shape[1],rs.shape[0]),interpolation=cv2.INTER_AREA)>0.4
    oy,ox=(CS-rs.shape[0])//2,(CS-rs.shape[1])//2
    cc[oy:oy+rs.shape[0],ox:ox+rs.shape[1]]=rs; cm[oy:oy+rs.shape[0],ox:ox+rs.shape[1]]=rm
    scored=[]
    for ti in TPLS:
        if ti["pattern"]: continue
        t=ti["tpl"]; ib=ti["ib"]
        tcrop=t[ib[1]:ib[3]+1, ib[0]:ib[2]+1]
        tmask=ink_mask_rgb(cv2.cvtColor(tcrop,cv2.COLOR_BGR2RGB))
        ts=min(CS/tcrop.shape[1],CS/tcrop.shape[0])
        trs=cv2.resize(tcrop,(max(2,int(tcrop.shape[1]*ts)),max(2,int(tcrop.shape[0]*ts))),interpolation=cv2.INTER_AREA).astype(float)
        trm=cv2.resize(tmask.astype(np.uint8),(trs.shape[1],trs.shape[0]),interpolation=cv2.INTER_AREA)>0.4
        tc=np.full((CS,CS,3),255.0); tm=np.zeros((CS,CS),bool)
        toy,tox=(CS-trs.shape[0])//2,(CS-trs.shape[1])//2
        tc[toy:toy+trs.shape[0],tox:tox+trs.shape[1]]=trs; tm[toy:toy+trs.shape[0],tox:tox+trs.shape[1]]=trm
        m=tm|cm
        if m.sum()<10: continue
        a=cc[m]; bb=tc[m]
        a_=a-a.mean(axis=0); b_=bb-bb.mean(axis=0)
        den=np.sqrt((a_**2).sum()*(b_**2).sum())
        ncc=float((a_*b_).sum()/den) if den>0 else 0.0
        iou=float((tm&cm).sum()/max((tm|cm).sum(),1))
        scored.append((0.62*ncc+0.38*iou, ti["name"], round(ncc,3), round(iou,3)))
    scored.sort(reverse=True)
    return scored[:2]

rows=[]
for b in cands:
    cls="pattern" if b["src"]=="pattern" else ("sym" if (b["bw"]<=30 and b["bh"]<=26) else "big")
    sym1=sym2=""; sc1=sc2=""
    if cls=="pattern":
        sym1="Limestone"; sc1=0.5
    elif cls=="sym" and b["area"]>=10:
        top=classify_v2(b)
        if top:
            sc1,sym1=round(top[0][0],3),top[0][1]
            if len(top)>1: sc2,sym2=round(top[1][0],3),top[1][1]
    rows.append(dict(cx=round(b["cx"],2),cy=round(b["cy"],2),ix0=b["ix0"],iy0=b["iy0"],ix1=b["ix1"],iy1=b["iy1"],
        bw=b["bw"],bh=b["bh"],area=b["area"],nseed=b["nseed"],cls=cls,src=b["src"],sym1=sym1,score1=sc1,sym2=sym2,score2=sc2))
with open("work/mineral_cands_v3.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(Counter(r["cls"] for r in rows))
print(Counter(r["sym1"] for r in rows if r["cls"]=="sym" and r["sym1"]).most_common(70))
nums=list(csv.DictReader(open("work/mineral_numbers.csv")))
from scipy.spatial import cKDTree
N=np.array([[float(nn["nat_x"]),float(nn["nat_y"])] for nn in nums])
for label,subset in [("sym",[r for r in rows if r["cls"]=="sym"]),("sym+pattern",[r for r in rows if r["cls"] in("sym","pattern")]),("all",rows)]:
    P=np.array([[r["cx"],r["cy"]] for r in subset]); d,_=cKDTree(P).query(N)
    print(f" {label}: numbers within 30px {(d<=30).sum()}/989, 40px {(d<=40).sum()}")
def overlay(name,x0,y0,x1,y1):
    c=img[y0:y1,x0:x1].copy()
    for r in rows:
        if x0<=r["cx"]<x1 and y0<=r["cy"]<y1:
            col=(0,200,0) if r["cls"]=="sym" else ((255,0,255) if r["cls"]=="big" else (0,165,255))
            cv2.rectangle(c,(r["ix0"]-x0,r["iy0"]-y0),(r["ix1"]-x0,r["iy1"]-y0),col,1)
            cv2.circle(c,(int(r["cx"]-x0),int(r["cy"]-y0)),1,(0,0,255),-1)
    for nn in nums:
        nx,ny=float(nn["nat_x"]),float(nn["nat_y"])
        if x0<=nx<x1 and y0<=ny<y1: cv2.circle(c,(int(nx-x0),int(ny-y0)),2,(255,120,0),1)
    cv2.imwrite(name, cv2.resize(c,(c.shape[1]*2,c.shape[0]*2),interpolation=cv2.INTER_NEAREST))
overlay("work/qa_detect3_keffi.png",760,760,1160,1060)
overlay("work/qa_detect3_sokoto.png",120,60,520,360)
print("overlays done")
