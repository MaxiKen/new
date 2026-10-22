import cv2, numpy as np, json, pickle, sys
import pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
base_u8=cv2.imread('work/min/mineral_base.png')
base=base_u8.astype(np.float32)
BH,BW=base.shape[:2]
gray8=cv2.cvtColor(base_u8,cv2.COLOR_BGR2GRAY)
C6=json.load(open('work/min/centres6.json'))
thr_cal=json.load(open('work/min/thresholds.json'))
S=pickle.load(open('work/min/complete6b.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
def nms(det,r=4.0):
    det=sorted(det,key=lambda d:-d[1]); kp=[]
    for (cx,cy),sc in det:
        if all((cx-a)**2+(cy-b)**2>r*r for (a,b),_ in kp): kp.append(((cx,cy),sc))
    return kp
def harvest(L):
    lt=cv2.imread(f'work/min/templates/leg{L:02d}.png')
    lm=cv2.imread(f'work/min/templates/leg{L:02d}_mask.png',0)
    slots=[ns for ns in num_state if ns['expected'].get(L,0)>0]
    if not slots: print(L,"no slots"); return None
    best=None
    for s in [0.55,0.65,0.75,0.85,0.95,1.0]:
        t=cv2.resize(lt,None,fx=s,fy=s,interpolation=cv2.INTER_AREA).astype(np.float32)
        m=cv2.resize(lm,None,fx=s,fy=s,interpolation=cv2.INTER_AREA).astype(np.float32)/255
        th,tw=t.shape[:2]
        ys,xs=np.nonzero(m>0.3)
        bcx=(xs.min()+xs.max())/2; bcy=(ys.min()+ys.max())/2
        peaks=[]
        for ns in slots:
            nx,ny=ns['num']['px'],ns['num']['py']; WR=56
            x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
            win=base[y0:y1,x0:x1]
            if win.shape[0]<th+2 or win.shape[1]<tw+2: continue
            ncc=masked_ncc(win,t,m)
            H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
            ncc=np.where(np.hypot(xx+x0+bcx-nx,yy+y0+bcy-ny)<=42,ncc,-1)
            i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
            peaks.append((float(x+x0+bcx),float(y+y0+bcy),v))
        med=float(np.median([p[2] for p in peaks])) if peaks else -1
        if best is None or med>best[0]: best=(med,s,t,m,peaks,bcx,bcy)
    med,s,t,m,peaks,bcx,bcy=best
    th,tw=t.shape[:2]
    good=[p for p in peaks if p[2]>=0.78]
    print(f"harvest leg{L}: scale={s} medpeak={med:.3f} instances>=0.78: {len(good)}/{len(peaks)}")
    if len(good)<3: return None
    patches=[]; cents=[]
    for cx,cy,v in good:
        px0=int(round(cx-bcx)); py0=int(round(cy-bcy))
        if px0<0 or py0<0 or px0+tw>BW or py0+th>BH: continue
        patches.append(base[py0:py0+th,px0:px0+tw])
        g=gray8[py0:py0+th,px0:px0+tw]
        ink=(g<200)&(m>0.3)
        if ink.sum()>=3:
            ys,xs=np.nonzero(ink); cents.append(((xs.min()+xs.max())/2,(ys.min()+ys.max())/2))
    if len(patches)<3: return None
    newtpl=np.median(np.stack(patches),axis=0)
    ncx,ncy=(float(np.median([c[0] for c in cents])),float(np.median([c[1] for c in cents]))) if cents else (bcx,bcy)
    # self stats vs new template
    scs=[]
    for cx,cy,v in good:
        WR=20
        x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
        win=base[y0:y1,x0:x1]
        ncc=masked_ncc(win,newtpl.astype(np.float32),m)
        H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
        d2=np.hypot(xx+x0+ncx-cx,yy+y0+ncy-cy)
        scs.append(float(np.where(d2<=1.6,ncc,-1).max()))
    return dict(tpl=newtpl,mask=m,cx=ncx,cy=ncy,n=len(patches),
                p5=float(np.percentile(scs,5)),p50=float(np.median(scs)))
NEW={}
for L in [19,52,22,44]:
    h=harvest(L)
    if h is None: print(f"leg{L} harvest FAILED - keeping old template/points"); continue
    NEW[L]=h
    cv2.imwrite(f'work/min/selftpl4/leg{L:02d}.png',np.clip(h['tpl'],0,255).astype(np.uint8))
    cv2.imwrite(f'work/min/selftpl4/leg{L:02d}_mask.png',(h['mask']*255).astype(np.uint8))
    C6[str(L)]={"center_xy":[round(h['cx'],2),round(h['cy'],2)],"self_p5":round(h['p5'],3),
                "self_p10":round(h['p5'],3),"self_p50":round(h['p50'],3),"n":h['n'],"src":"harvest6c"}
    print(f"leg{L} NEW template saved centre=({h['cx']:.1f},{h['cy']:.1f}) p5={h['p5']:.3f} p50={h['p50']:.3f} n={h['n']}")
json.dump(C6,open('work/min/centres6.json','w'),indent=1)
# scoring helpers with (possibly new) templates
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        TPL[L]=(t,m,*C6[str(L)]['center_xy'])
    return TPL[L]
def score_at(L,cx,cy,tol=1.6):
    t,m,bcx,bcy=tpl(L); WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    return float(np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=tol,ncc,-1).max())
def relink():
    for ns in num_state: ns['filled']=Counter(); ns['pts']=[]
    for p in pts: p.pop('num_idx',None)
    pairs=[]
    for pi,p in enumerate(pts):
        for ni,ns in enumerate(num_state):
            if ns['expected'].get(p['leg'],0)>0:
                dist=np.hypot(p['cx']-ns['num']['px'],p['cy']-ns['num']['py'])
                if dist<=42: pairs.append((-p['score'],dist,pi,ni))
    pairs.sort(); used=set()
    for negsc,dist,pi,ni in pairs:
        if pi in used: continue
        p=pts[pi]; ns=num_state[ni]
        if ns['filled'][p['leg']]>=ns['expected'][p['leg']]: continue
        ns['filled'][p['leg']]+=1; ns['pts'].append(pi); used.add(pi); p['num_idx']=ni
GROUP=[2,9,10,19,21,34,37]
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
for L,h in NEW.items():
    pts[:]=[p for p in pts if p['leg']!=L]
    exclude=[(p['cx'],p['cy']) for p in pts]
    t,m,bcx,bcy=tpl(L)
    ncc=masked_ncc(base,t,m)
    ys,xs=np.nonzero(ncc>=0.70)
    det=[((float(x+bcx),float(y+bcy)),float(ncc[y,x])) for y,x in zip(ys,xs)]
    det=nms(det)
    thr_free=float(np.clip(h['p5']-0.03,0.90,0.97)); thr_ctx=float(np.clip(h['p5']-0.12,0.72,0.92))
    exppts=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(L,0)>0]
    tree_exp=cKDTree(np.array(exppts))
    added=0
    for (cx,cy),sc in det:
        de=float(tree_exp.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
        tier=None
        if de<=42 and sc>=thr_ctx: tier='ctx'
        elif sc>=thr_free: tier='free'
        elif sc>=max(thr_ctx,thr_free-0.06) and da<=34: tier='near'
        if not tier: continue
        if any((cx-a)**2+(cy-b)**2<25 for a,b in exclude): continue
        # competitor guard vs confusable group (and all legs for free tier if weak template)
        comp=max([score_at(K,cx,cy) for K in GROUP if K!=L]+[0])
        if sc<comp-0.02: continue
        pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':tier,'match_type':'complete'})
        exclude.append((cx,cy)); added+=1
    print(f"leg{L} redetect added={added} (thr_free={thr_free:.2f} thr_ctx={thr_ctx:.2f})")
    relink()
    # window fill
    floor=min(thr_ctx,max(0.65,h['p5']-0.18))
    n2=0
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(L,0)==0: continue
        for _ in range(ns['expected'][L]-ns['filled'][L]):
            nx,ny=ns['num']['px'],ns['num']['py']; WR=56
            x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
            win=base[y0:y1,x0:x1]
            if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: continue
            nccw=masked_ncc(win,t,m)
            H,W=nccw.shape; yy,xx=np.mgrid[0:H,0:W]
            ccx=xx+x0+bcx; ccy=yy+y0+bcy
            valid=np.hypot(ccx-nx,ccy-ny)<=42
            for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.0)
            nccw=np.where(valid,nccw,-1)
            i=np.argmax(nccw); v=float(nccw.ravel()[i]); y,x=np.unravel_index(i,nccw.shape)
            if v<floor: continue
            cx,cy=float(x+x0+bcx),float(y+y0+bcy)
            si=score_at(L,cx,cy); bo=max(score_at(K,cx,cy) for K in LEGS if K!=L)
            if si<bo-0.02: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(v,4),'tier':'winA','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; exclude.append((cx,cy)); n2+=1
    print(f"leg{L} window added={n2}")
    relink()
# --- confusable-group arbitration ---
relab=0
for p in pts:
    if p['leg'] in GROUP and p['score']<0.98:
        scs={K:score_at(K,p['cx'],p['cy']) for K in GROUP}
        best=max(scs,key=scs.get)
        if best!=p['leg'] and scs[best]>scs[p['leg']]+0.05:
            p['leg']=best; p['score']=round(scs[best],4); relab+=1
print("group relabelled:",relab)
# dedup 5px (linked first, then score)
relink()
order=sorted(range(len(pts)),key=lambda i:-((2 if 'num_idx' in pts[i] else 0)+pts[i]['score']))
keep=[]; keptpos=[]
for i in order:
    p=pts[i]
    if any((p['cx']-a)**2+(p['cy']-b)**2<25 for a,b in keptpos): continue
    keep.append(p); keptpos.append((p['cx'],p['cy']))
print(f"dedup {len(pts)}->{len(keep)}"); pts[:]=keep
# --- retro shape gates for 6/25/26/13/38 ---
hsv=cv2.cvtColor(base_u8,cv2.COLOR_BGR2HSV).astype(np.int16)
def shape_ok(L,cx,cy):
    x,y=int(round(cx)),int(round(cy))
    g=gray8[max(0,y-4):y+5,max(0,x-4):x+5].astype(np.int16)
    s=hsv[max(0,y-4):y+5,max(0,x-4):x+5,1]
    darkc=int((g<90).sum()); satc=int((s>130).sum())
    if L in (6,25,26,13):
        yy,xx=np.mgrid[0:g.shape[0],0:g.shape[1]]
        ink=(g<150).astype(np.uint8)
        nlab,lab,stats,_=cv2.connectedComponentsWithStats(ink,8)
        cc=0
        for i in range(1,nlab):
            w,h,area=stats[i,cv2.CC_STAT_WIDTH],stats[i,cv2.CC_STAT_HEIGHT],stats[i,cv2.CC_STAT_AREA]
            if w<=6 and h<=6 and 3<=area<=22: cc+=1
        return 3<=darkc<=35 and cc>=1 and satc<=25
    if L==38: return darkc>=6
    return True
before=len(pts)
pts[:]=[p for p in pts if p['leg'] not in (6,25,26,13,38) or shape_ok(p['leg'],p['cx'],p['cy'])]
print(f"shape retro-gate: {before}->{len(pts)}")
relink()
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6c.pkl','wb'))
def montage(selpts,path,cols=7):
    cells=[]
    for p in selpts:
        x,y=int(round(p['cx'])),int(round(p['cy']))
        win=np.full((29,29,3),255,np.uint8)
        src=base_u8[max(0,y-14):y+15,max(0,x-14):x+15]
        win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
        cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
        cv2.putText(win,f"L{p['leg']} {p['score']:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.32,(0,0,255),1)
        cells.append(cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST))
    if not cells: print(path,"empty"); return
    H=cells[0].shape[0]; W=cells[0].shape[1]; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite(path,canvas); print("saved",path,len(cells))
import random
random.seed(4)
for L in [19,52,22,44,14]:
    sel=[p for p in pts if p['leg']==L]
    s=sel if len(sel)<=21 else random.sample(sel,21)
    montage(s,f'work/qa/v6c_leg{L}.png')
# leg14 unfilled windows diagnostic: montage of 12 windows (61px) + peak stats
unf14=[]
t14,m14,bx14,by14=tpl(14)
t58,m58,bx58,by58=tpl(58)
for ni,ns in enumerate(num_state):
    if ns['expected'].get(14,0)>0 and ns['filled'][14]<ns['expected'][14]:
        nx,ny=ns['num']['px'],ns['num']['py']; WR=56
        x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
        win=base[y0:y1,x0:x1]
        nccw=masked_ncc(win,t14,m14)
        H,W=nccw.shape; yy,xx=np.mgrid[0:H,0:W]
        nccw=np.where(np.hypot(xx+x0+bx14-nx,yy+y0+by14-ny)<=42,nccw,-1)
        i=np.argmax(nccw); v=float(nccw.ravel()[i]); y,x=np.unravel_index(i,nccw.shape)
        unf14.append((v,ni,nx,ny,float(x+x0+bx14),float(y+y0+by14)))
unf14.sort(reverse=True)
print("leg14 unfilled windows:",len(unf14),"peak-score percentiles:",
      np.round(np.percentile([u[0] for u in unf14],[0,25,50,75,100]),3) if unf14 else None)
cells=[]
for v,ni,nx,ny,px,py in unf14[:12]:
    x,y=int(round(nx)),int(round(ny))
    win=np.full((61,61,3),255,np.uint8)
    src=base_u8[max(0,y-30):y+31,max(0,x-30):x+31]
    win[30-(y-max(0,y-30)):30-(y-max(0,y-30))+src.shape[0],30-(x-max(0,x-30)):30-(x-max(0,x-30))+src.shape[1]]=src
    cv2.drawMarker(win,(30,30),(255,0,0),cv2.MARKER_CROSS,9,1)       # number = blue
    cv2.drawMarker(win,(int(round(px-x))+30,int(round(py-y))+30),(0,0,255),cv2.MARKER_TILTED_CROSS,7,1)  # peak = red
    cv2.putText(win,f"{num_state[ni]['num']['code']}{num_state[ni]['num']['num']} pk{v:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.32,(0,0,255),1)
    cells.append(cv2.resize(win,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
if cells:
    H=cells[0].shape[0]; W=cells[0].shape[1]; cols=4; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite('work/qa/v6c_leg14_unfilled.png',canvas); print("saved leg14 unfilled montage")
