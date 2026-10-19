"""Mineral detection v4: capped merging, grey-outline seeds, pattern patches, cluster splitting."""
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
Oink = ((V<185)&(S<70)).astype(np.uint8)
ALL = ((Cink|Kink|Oink)>0).astype(np.uint8)
k2=np.ones((2,2),np.uint8); k3=np.ones((3,3),np.uint8)

seeds=[]
def add_seeds(lab, keep_ids, ch, grow_on=ALL):
    for i in keep_ids:
        ys,xs=np.where(lab==i)
        x0,x1,y0,y1=int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())
        gx0,gx1=max(0,x0-3),min(W_img,x1+4); gy0,gy1=max(0,y0-3),min(H_img,y1+4)
        seed=(lab[gy0:gy1,gx0:gx1]==i).astype(np.uint8)
        g=cv2.dilate(seed,k3) & grow_on[gy0:gy1,gx0:gx1]
        yy,xx=np.where(g>0)
        seeds.append(dict(ix0=int(gx0+xx.min()),ix1=int(gx0+xx.max()),iy0=int(gy0+yy.min()),iy1=int(gy0+yy.max()),ink=g,ox=gx0,oy=gy0,ch=ch))

op2=cv2.morphologyEx(Cink,cv2.MORPH_OPEN,k2); op3=cv2.morphologyEx(Cink,cv2.MORPH_OPEN,k3)
n,lab,stats,cent=cv2.connectedComponentsWithStats(op2,8)
keep=[]
for i in range(1,n):
    x,y,w,h,a=stats[i]
    if a<5: continue
    if (w<=22 and h<=22 and a/(w*h)>=0.32) or op3[y:y+h,x:x+w][lab[y:y+h,x:x+w]==i].sum()>=4: keep.append(i)
add_seeds(lab,keep,"C"); print("C seeds",len(keep))
op2k=cv2.morphologyEx(Kink,cv2.MORPH_OPEN,k2)
n,lab,stats,cent=cv2.connectedComponentsWithStats(op2k,8)
keep=[i for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>=5]
add_seeds(lab,keep,"K"); print("K seeds",len(keep))
n,lab,stats,cent=cv2.connectedComponentsWithStats(Oink,8)
keep=[]
for i in range(1,n):
    x,y,w,h,a=stats[i]
    if 7<=w<=26 and 7<=h<=26 and 14<=a<=340:
        keep.append(i)
add_seeds(lab,keep,"O"); print("O seeds",len(keep)," total",len(seeds))

# greedy capped merging: pairs sorted by gap; group bbox must stay <=30x26
parent=list(range(len(seeds))); gb={i:(seeds[i]["ix0"],seeds[i]["iy0"],seeds[i]["ix1"],seeds[i]["iy1"]) for i in range(len(seeds))}
def find(a):
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
pairs=[]
cells=defaultdict(list)
for i,d in enumerate(seeds): cells[(d["ix0"]//32,d["iy0"]//32)].append(i)
for i,d in enumerate(seeds):
    for gx in (d["ix0"]//32-1,d["ix0"]//32,d["ix0"]//32+1):
        for gy in (d["iy0"]//32-1,d["iy0"]//32,d["iy0"]//32+1):
            for j in cells.get((gx,gy),[]):
                if j<=i: continue
                e=seeds[j]
                gdx=max(0,max(d["ix0"],e["ix0"])-min(d["ix1"],e["ix1"])); gdy=max(0,max(d["iy0"],e["iy0"])-min(d["iy1"],e["iy1"]))
                if max(gdx,gdy)<=2: pairs.append((max(gdx,gdy),i,j))
pairs.sort()
for g,i,j in pairs:
    ri,rj=find(i),find(j)
    if ri==rj: continue
    a=gb[ri]; b=gb[rj]
    nb=(min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3]))
    if nb[2]-nb[0]+1<=30 and nb[3]-nb[1]+1<=26:
        parent[ri]=rj; gb[rj]=nb
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
                      cx=(ix0+ix1)/2,cy=(iy0+iy1)/2,nseed=len(idxs),ink=ink,src="blob",
                      chs="".join(sorted(set(seeds[i]["ch"] for i in idxs)))))
print("candidates:",len(cands), Counter("sym" if (c["bw"]<=30 and c["bh"]<=26) else "big" for c in cands))

# green pattern patches
B,G,R=img[:,:,0].astype(int),img[:,:,1].astype(int),img[:,:,2].astype(int)
green=((G>R+20)&(G>B+10)&(S>110)&(V<220)).astype(np.uint8)
closed=cv2.morphologyEx(green,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
n,lab,stats,cent=cv2.connectedComponentsWithStats(closed,8)
npatch=0
for i in range(1,n):
    x,y,w,h,a=stats[i]
    gpx=int(green[y:y+h,x:x+w][lab[y:y+h,x:x+w]==i].sum())
    if 15<=w<=90 and 8<=h<=70 and gpx>=35 and gpx/(w*h)<0.8:
        x1,y1=x+w-1,y+h-1
        cands=[c for c in cands if not (x<=c["cx"]<=x1 and y<=c["cy"]<=y1)]
        ink=green[y:y1+1,x:x1+1].copy()
        cands.append(dict(ix0=x,ix1=x1,iy0=y,iy1=y1,bw=w,bh=h,area=gpx,cx=(x+x1)/2,cy=(y+y1)/2,nseed=0,ink=ink,src="pattern",chs="P"))
        npatch+=1
print("pattern patches added:",npatch," total cands:",len(cands))

# templates + classify
meta=json.load(open("work/mineral_templates_meta.json")); tplz=np.load("work/mineral_templates.npz")
def ink_mask_rgb(a):
    a=a.astype(int); return (a.min(axis=2)<198)|((a.max(axis=2)-a.min(axis=2))>55)
TPLS=[]
for i,m in enumerate(meta):
    t=cv2.cvtColor(tplz[f"t{i}"],cv2.COLOR_RGB2BGR)
    TPLS.append(dict(idx=i,name=m["name"],pattern=m["pattern"],tpl=t,ib=m["ink_bbox"]))
def classify_v2(b):
    x0,x1,y0,y1=b["ix0"],b["ix1"],b["iy0"],b["iy1"]
    crop=img[y0:y1+1,x0:x1+1]
    bink=(b["ink"]>0); CS=36
    cc=np.full((CS,CS,3),255.0); cm=np.zeros((CS,CS),bool)
    sc=min(CS/crop.shape[1],CS/crop.shape[0])
    rs=cv2.resize(crop,(max(2,int(crop.shape[1]*sc)),max(2,int(crop.shape[0]*sc))),interpolation=cv2.INTER_AREA).astype(float)
    rm=cv2.resize(bink.astype(np.uint8),(rs.shape[1],rs.shape[0]),interpolation=cv2.INTER_AREA)>0.4
    oy,ox=(CS-rs.shape[0])//2,(CS-rs.shape[1])//2
    cc[oy:oy+rs.shape[0],ox:ox+rs.shape[1]]=rs; cm[oy:oy+rs.shape[0],ox:ox+rs.shape[1]]=rm
    scored=[]
    for ti in TPLS:
        if ti["pattern"]: continue
        t=ti["tpl"]; ib=ti["ib"]
        tcrop=t[ib[1]:ib[3]+1,ib[0]:ib[2]+1]
        tmask=ink_mask_rgb(cv2.cvtColor(tcrop,cv2.COLOR_BGR2RGB))
        ts=min(CS/tcrop.shape[1],CS/tcrop.shape[0])
        trs=cv2.resize(tcrop,(max(2,int(tcrop.shape[1]*ts)),max(2,int(tcrop.shape[0]*ts))),interpolation=cv2.INTER_AREA).astype(float)
        trm=cv2.resize(tmask.astype(np.uint8),(trs.shape[1],trs.shape[0]),interpolation=cv2.INTER_AREA)>0.4
        tc=np.full((CS,CS,3),255.0); tm=np.zeros((CS,CS),bool)
        toy,tox=(CS-trs.shape[0])//2,(CS-trs.shape[1])//2
        tc[toy:toy+trs.shape[0],tox:tox+trs.shape[1]]=trs; tm[toy:toy+trs.shape[0],tox:tox+trs.shape[1]]=trm
        m=tm|cm
        if m.sum()<10: continue
        a=cc[m]; bb=tc[m]; a_=a-a.mean(axis=0); b_=bb-bb.mean(axis=0)
        den=np.sqrt((a_**2).sum()*(b_**2).sum())
        ncc=float((a_*b_).sum()/den) if den>0 else 0.0
        iou=float((tm&cm).sum()/max((tm|cm).sum(),1))
        scored.append((0.62*ncc+0.38*iou, ti["name"], round(ncc,3), round(iou,3)))
    scored.sort(reverse=True)
    return scored[:2]

for b in cands:
    b["cls"]="pattern" if b["src"]=="pattern" else ("sym" if (b["bw"]<=30 and b["bh"]<=26) else "big")
    b["sym1"]=b["sym2"]=""; b["score1"]=b["score2"]=""; b["iou1"]=""
    if b["cls"]=="pattern": b["sym1"]="Limestone"; b["score1"]=0.5
    elif b["cls"]=="sym" and b["area"]>=10:
        top=classify_v2(b)
        if top:
            b["score1"],b["sym1"],_,b["iou1"]=round(top[0][0],3),top[0][1],top[0][2],top[0][3]
            if len(top)>1: b["score2"],b["sym2"]=round(top[1][0],3),top[1][1]

# cluster splitting for big / oversized via local NCC
def local_ncc(b, thr=0.60):
    pad=4
    x0,x1=max(0,b["ix0"]-pad),min(W_img,b["ix1"]+pad+1); y0,y1=max(0,b["iy0"]-pad),min(H_img,b["iy1"]+pad+1)
    sub=img[y0:y1,x0:x1]
    dets=[]
    for ti in TPLS:
        if ti["pattern"]: continue
        for s in (0.30,0.333,0.37,0.41):
            tw,th=max(5,int(round(ti["tpl"].shape[1]*s))),max(5,int(round(ti["tpl"].shape[0]*s)))
            if tw>=sub.shape[1] or th>=sub.shape[0]: continue
            t=cv2.resize(ti["tpl"],(tw,th),interpolation=cv2.INTER_AREA)
            res=cv2.matchTemplate(sub,t,cv2.TM_CCOEFF_NORMED)
            mx=cv2.dilate(res,np.ones((5,5),np.uint8))
            ys,xs=np.where((res>=mx-1e-9)&(res>=thr))
            ib=ti["ib"]; cox=(ib[0]+ib[2])/2*s; coy=(ib[1]+ib[3])/2*s
            for yy,xx in zip(ys,xs):
                dets.append(dict(cx=float(x0+xx+cox),cy=float(y0+yy+coy),score=float(res[yy,xx]),name=ti["name"],tw=tw,th=th))
    dets.sort(key=lambda d:-d["score"])
    kept=[]
    for d in dets:
        if all((d["cx"]-k["cx"])**2+(d["cy"]-k["cy"])**2>=36 for k in kept): kept.append(d)
    return kept

final=[]
nsplit=0
for b in cands:
    need = (b["cls"]=="big") or (b["cls"]=="sym" and (b["bw"]>24 or b["bh"]>22 or b["area"]>430))
    if need and b["src"]=="blob":
        dets=local_ncc(b)
        if len(dets)>=2 or (len(dets)==1 and b["bw"]>1.5*dets[0]["tw"]):
            for d in dets:
                final.append(dict(cx=d["cx"],cy=d["cy"],ix0=int(d["cx"]-d["tw"]/2),iy0=int(d["cy"]-d["th"]/2),
                    ix1=int(d["cx"]+d["tw"]/2),iy1=int(d["cy"]+d["th"]/2),bw=d["tw"],bh=d["th"],area=b["area"],
                    nseed=b["nseed"],cls="sym",src="cluster",sym1=d["name"],score1=round(d["score"],3),sym2="",score2="",iou1=""))
            nsplit+=1
            continue
    final.append(b)
print("clusters split:",nsplit," final candidates:",len(final))

nums_fp=list(csv.DictReader(open("work/mineral_numbers.csv")))
from scipy.spatial import cKDTree as _T
_N=np.array([[float(nn["nat_x"]),float(nn["nat_y"])] for nn in nums_fp])
OUTLINE_SYMS={"Baryte","Gypsum","Phosphate","Phosphate Rock","Trona (tr)","Tantalite (ta)","Zircon (zr)"}
before=len(final)
kept=[]
for b in final:
    drop=False
    if b.get("chs")=="O" and b.get("sym1") in OUTLINE_SYMS and b.get("iou1") not in ("",None) and float(b["iou1"])<0.30:
        d,_=_T(_N).query([[b["cx"],b["cy"]]])
        if d[0]>32: drop=True
    if not drop: kept.append(b)
final=kept
print("O-only FP drop:", before-len(final))
rows=[]
for b in final:
    rows.append(dict(cx=round(float(b["cx"]),2),cy=round(float(b["cy"]),2),ix0=int(b["ix0"]),iy0=int(b["iy0"]),ix1=int(b["ix1"]),iy1=int(b["iy1"]),
        bw=int(b["bw"]),bh=int(b["bh"]),area=int(b["area"]),nseed=int(b["nseed"]),cls=b["cls"],src=b["src"],chs=b.get("chs",""),
        sym1=b.get("sym1",""),score1=b.get("score1",""),iou1=b.get("iou1",""),sym2=b.get("sym2",""),score2=b.get("score2","")))
with open("work/mineral_cands_v4.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(Counter(r["cls"]+"/"+r["src"] for r in rows))
nums=list(csv.DictReader(open("work/mineral_numbers.csv")))
from scipy.spatial import cKDTree
N=np.array([[float(nn["nat_x"]),float(nn["nat_y"])] for nn in nums])
for label,subset in [("sym+pattern",[r for r in rows if r["cls"] in("sym","pattern")]),("all",rows)]:
    P=np.array([[r["cx"],r["cy"]] for r in subset]); d,_=cKDTree(P).query(N)
    print(f" {label}: numbers within 25px {(d<=25).sum()}/989 30px {(d<=30).sum()} 40px {(d<=40).sum()}")
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
overlay("work/qa_detect4_keffi.png",760,760,1160,1060)
overlay("work/qa_detect4_sokoto.png",120,60,520,360)
print("done")
