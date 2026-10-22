import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
thr_cal=json.load(open('work/min/thresholds.json'))
S=pickle.load(open('work/min/complete6b.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
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
# ---- EXACT shape-gate code copied from complete6.py ----
baseu=cv2.imread('work/min/mineral_base.png')
gray=cv2.cvtColor(baseu,cv2.COLOR_BGR2GRAY)
Bc,Gc,Rc=baseu[:,:,0].astype(int),baseu[:,:,1].astype(int),baseu[:,:,2].astype(int)
yellow=((Rc>175)&(Gc>155)&(Bc<115)).astype(np.uint8)
darkm=(gray<95).astype(np.uint8)
orange=((Bc<130)&(Gc>70)&(Gc<190)&(Rc>150)&((Rc-Bc)>60)).astype(np.uint8)
def cc_check(mask_img,cx,cy,maxw,maxh,minw=0,minh=0,central=False):
    x,y=int(round(cx)),int(round(cy))
    x0,y0=max(0,x-11),max(0,y-11); x1,y1=min(BW,x+12),min(BH,y+12)
    sub=mask_img[y0:y1,x0:x1]
    n,lab,stats,cent=cv2.connectedComponentsWithStats(sub,8)
    best=None
    for dy in range(-2,3):
        for dx in range(-2,3):
            xx,yy=x-x0+dx,y-y0+dy
            if 0<=xx<sub.shape[1] and 0<=yy<sub.shape[0] and lab[yy,xx]>0: best=lab[yy,xx]; break
        if best: break
    if best is None: return False
    X,Y,W,H,A=stats[best]
    if W>maxw or H>maxh or W<minw or H<minh: return False
    if X==0 or Y==0 or X+W>=sub.shape[1] or Y+H>=sub.shape[0]: return False
    if central:
        relx=(x-x0-X)/max(W,1); rely=(y-y0-Y)/max(H,1)
        if not (0.2<=relx<=0.8 and 0.2<=rely<=0.8): return False
    return True
def shape_ok(L,cx,cy):
    if L==6:
        t,m,bcx,bcy=tpl(6)
        x0=int(round(cx-bcx)); y0=int(round(cy-bcy)); th,tw=t.shape[:2]
        if x0<0 or y0<0 or x0+tw>BW or y0+th>BH: return False
        v=gray[y0:y0+th,x0:x0+tw][m>0]
        return cc_check(darkm,cx,cy,9,10) and (v<80).mean()>=0.22 and (v>200).mean()>=0.13
    if L==25: return cc_check(yellow,cx,cy,11,11,central=True)
    if L==26: return cc_check(yellow,cx,cy,12,12,minw=7,minh=7,central=True)
    if L==13: return cc_check(darkm,cx,cy,14,9)
    if L==38: return cc_check(darkm,cx,cy,11,14)
    if L in (52,65):
        x,y=int(round(cx)),int(round(cy))
        return int(orange[max(0,y-5):y+6,max(0,x-5):x+6].sum())>=4
    return True
# ---- helpers ----
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
def nms(det,r=4.0):
    det=sorted(det,key=lambda d:-d[1]); kp=[]
    for (cx,cy),sc in det:
        if all((cx-a)**2+(cy-b)**2>r*r for (a,b),_ in kp): kp.append(((cx,cy),sc))
    return kp
def window_peak_tpl(t,m,bcx,bcy,nx,ny,R,exclude):
    WR=int(R+14)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+bcx; ccy=yy+y0+bcy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.0)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return float(x+x0+bcx),float(y+y0+bcy),v
allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
# STEP1: drop bogus-template legs
n0=len(pts)
pts[:]=[p for p in pts if p['leg'] not in (19,44,52)]
print(f"step1 drop 19/44/52: {n0}->{len(pts)}")
# STEP2: real shape gates on 6/25/26/13/38
dropc=Counter()
keep=[]
for p in pts:
    if p['leg'] in (6,25,26,13,38) and not shape_ok(p['leg'],p['cx'],p['cy']):
        dropc[(p['leg'],p.get('tier'))]+=1; continue
    keep.append(p)
pts[:]=keep
print("step2 real shape-gate drops:",dict(dropc), "remaining:",len(pts))
relink()
# STEP3: leg44 redetect (new harvested template in selftpl4)
t44,m44,bx44,by44=tpl(44)
exp44=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(44,0)>0]
tree44=cKDTree(np.array(exp44))
peaks44=[]
for ns in num_state:
    if ns['expected'].get(44,0)>0:
        r=window_peak_tpl(t44,m44,bx44,by44,ns['num']['px'],ns['num']['py'],42,[])
        if r: peaks44.append(r[2])
print("leg44 M-slot window peaks pct [0,25,50,75,100]:",np.round(np.percentile(peaks44,[0,25,50,75,100]),3), "n=",len(peaks44))
ncc44=masked_ncc(base,t44,m44)
ys,xs=np.nonzero(ncc44>=0.80)
det44=nms([((float(x+bx44),float(y+by44)),float(ncc44[y,x])) for y,x in zip(ys,xs)])
print("leg44 candidates>=0.80:",len(det44))
COMP44=[3,4,5,10,20,22,23,31,33,40,51,56,57,63,66,67]
exclude=[(p['cx'],p['cy']) for p in pts]
add44=0
for (cx,cy),sc in det44:
    de=float(tree44.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
    tier=None
    if de<=42 and sc>=0.88: tier='ctx'
    elif sc>=1.00: tier='free'
    elif da<=34 and sc>=0.95: tier='near'
    if not tier: continue
    if any((cx-a)**2+(cy-b)**2<25 for a,b in exclude): continue
    si=score_at(44,cx,cy)
    bo=max(score_at(K,cx,cy) for K in COMP44)
    if si<bo-0.02: continue
    pts.append({'leg':44,'cx':cx,'cy':cy,'score':round(sc,4),'tier':tier,'match_type':'complete'})
    exclude.append((cx,cy)); add44+=1
print("leg44 sweep added:",add44)
relink()
n=0
for ni,ns in enumerate(num_state):
    if ns['expected'].get(44,0)==0: continue
    for _ in range(ns['expected'][44]-ns['filled'][44]):
        r=window_peak_tpl(t44,m44,bx44,by44,ns['num']['px'],ns['num']['py'],42,exclude)
        if r is None or r[2]<0.85: continue
        cx,cy,sc=r
        si=score_at(44,cx,cy); bo=max(score_at(K,cx,cy) for K in COMP44)
        if si<bo-0.02: continue
        pts.append({'leg':44,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'winA','match_type':'complete','num_idx':ni})
        ns['filled'][44]+=1; exclude.append((cx,cy)); n+=1
print("leg44 window added:",n)
relink()
# STEP4: leg52 careful ctx-only
lt=cv2.imread('work/min/templates/leg52.png'); lm=cv2.imread('work/min/templates/leg52_mask.png',0)
slots52=[ns for ns in num_state if ns['expected'].get(52,0)>0]
best52=None
for s in [0.75,0.85,1.0]:
    t=cv2.resize(lt,None,fx=s,fy=s,interpolation=cv2.INTER_AREA).astype(np.float32)
    m=cv2.resize(lm,None,fx=s,fy=s,interpolation=cv2.INTER_AREA).astype(np.float32)/255
    ys_,xs_=np.nonzero(m>0.3); bcx=(xs_.min()+xs_.max())/2; bcy=(ys_.min()+ys_.max())/2
    pk=[]
    for ns in slots52:
        r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
        if r: pk.append((r[2],r[0],r[1],ns))
    med=float(np.median([p[0] for p in pk])) if pk else -1
    print(f"leg52 scale {s}: median peak {med:.3f}, >=0.80: {sum(1 for p in pk if p[0]>=0.80)}/{len(pk)}")
    if best52 is None or med>best52[0]: best52=(med,s,t,m,bcx,bcy,pk)
med,s,t52,m52,bx52,by52,pk52=best52
good52=[p for p in pk52 if p[0]>=0.80]
use_new52=False
if len(good52)>=5:
    th,tw=t52.shape[:2]; patches=[]; cents=[]
    for v,cx,cy,ns in good52:
        px0=int(round(cx-bx52)); py0=int(round(cy-by52))
        if px0<0 or py0<0 or px0+tw>BW or py0+th>BH: continue
        patches.append(base[py0:py0+th,px0:px0+tw])
        g=gray[py0:py0+th,px0:px0+tw]; ink=(g<200)&(m52>0.3)
        if ink.sum()>=3:
            yy2,xx2=np.nonzero(ink); cents.append(((xx2.min()+xx2.max())/2,(yy2.min()+yy2.max())/2))
    if len(patches)>=5:
        newt=np.median(np.stack(patches),axis=0)
        ncx=float(np.median([c[0] for c in cents])); ncy=float(np.median([c[1] for c in cents]))
        cv2.imwrite('work/min/selftpl4/leg52.png',np.clip(newt,0,255).astype(np.uint8))
        cv2.imwrite('work/min/selftpl4/leg52_mask.png',(m52*255).astype(np.uint8))
        TPL.pop(52,None)
        C6['52']={"center_xy":[round(ncx,2),round(ncy,2)],"self_p5":0.74,"self_p10":0.75,"self_p50":0.84,"n":len(patches),"src":f"harvest6d-s{s}"}
        json.dump(C6,open('work/min/centres6.json','w'),indent=1)
        use_new52=True
        print(f"leg52 NEW template built scale={s} centre=({ncx:.1f},{ncy:.1f}) n={len(patches)}")
if not use_new52:
    print("leg52: harvest insufficient at 0.75-1.0; using current selftpl4 (0.55-scale) ctx-only strict")
t52,m52,bx52,by52=tpl(52)
ink52=np.array([121.,131.,149.])  # BGR legend ink
exclude=[(p['cx'],p['cy']) for p in pts]
add52=0; cand52=[]
for ni,ns in enumerate(num_state):
    if ns['expected'].get(52,0)==0: continue
    for _ in range(ns['expected'][52]-ns['filled'][52]):
        r=window_peak_tpl(t52,m52,bx52,by52,ns['num']['px'],ns['num']['py'],42,exclude)
        if r is None: continue
        cx,cy,sc=r
        cand52.append((sc,cx,cy,ni))
        if sc<0.78: continue
        x,y=int(round(cx)),int(round(cy))
        patch=baseu[max(0,y-2):y+3,max(0,x-2):x+3].reshape(-1,3).mean(axis=0)
        cold=float(np.linalg.norm(patch-ink52))
        if cold>95 and gray[y,x]>170: continue
        si=score_at(52,cx,cy); bo=max(score_at(K,cx,cy) for K in LEGS if K!=52)
        if si<bo+0.02: continue
        pts.append({'leg':52,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'winA','match_type':'complete','num_idx':ni})
        ns['filled'][52]+=1; exclude.append((cx,cy)); add52+=1
print("leg52 ctx-only added:",add52," (window peaks>=0.78 seen:",sum(1 for c in cand52 if c[0]>=0.78),")")
relink()
# STEP5: leg19/leg22 diagnostics (no points)
def diag(L):
    lt_=cv2.imread(f'work/min/templates/leg{L:02d}.png'); lm_=cv2.imread(f'work/min/templates/leg{L:02d}_mask.png',0)
    slots=[ns for ns in num_state if ns['expected'].get(L,0)>0]
    best=None
    for s in [0.6,0.75,0.85,0.95,1.1,1.25]:
        t=cv2.resize(lt_,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_LINEAR).astype(np.float32)
        m=cv2.resize(lm_,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_LINEAR).astype(np.float32)/255
        ys_,xs_=np.nonzero(m>0.3); bcx=(xs_.min()+xs_.max())/2; bcy=(ys_.min()+ys_.max())/2
        pk=[]
        for ns in slots:
            r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
            if r: pk.append((r[2],r[0],r[1],ns))
        med=float(np.median([p[0] for p in pk])) if pk else -1
        top=sorted([p[0] for p in pk],reverse=True)[:5]
        print(f"diag leg{L} scale {s}: nslots={len(pk)} median={med:.3f} top5={np.round(top,3)}")
        if best is None or med>best[0]: best=(med,s,pk)
    med,s,pk=best
    pk=sorted(pk,reverse=True)[:10]
    cells=[]
    for v,cx,cy,ns in pk:
        nx,ny=ns['num']['px'],ns['num']['py']
        x,y=int(round(nx)),int(round(ny))
        win=np.full((61,61,3),255,np.uint8)
        src=baseu[max(0,y-30):y+31,max(0,x-30):x+31]
        win[30-(y-max(0,y-30)):30-(y-max(0,y-30))+src.shape[0],30-(x-max(0,x-30)):30-(x-max(0,x-30))+src.shape[1]]=src
        cv2.drawMarker(win,(30,30),(255,0,0),cv2.MARKER_CROSS,9,1)
        cv2.drawMarker(win,(int(round(cx-x))+30,int(round(cy-y))+30),(0,0,255),cv2.MARKER_TILTED_CROSS,7,1)
        cv2.putText(win,f"L{L} {ns['num']['zone']}{ns['num']['value']} pk{v:.2f} s{s}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.3,(0,0,255),1)
        cells.append(cv2.resize(win,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
    if cells:
        H=cells[0].shape[0]; W=cells[0].shape[1]; cols=5; rows=(len(cells)+cols-1)//cols
        canvas=np.full((H*rows,W*cols,3),255,np.uint8)
        for i,c in enumerate(cells):
            r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
        cv2.imwrite(f'work/qa/v6d_diag{L}.png',canvas); print(f"saved diag montage leg{L}")
diag(19); diag(22)
# STEP6: arbitration group (excl 19)
GROUP=[2,9,10,21,34,37]; relab=0
for p in pts:
    if p['leg'] in GROUP and p['score']<0.98:
        scs={K:score_at(K,p['cx'],p['cy']) for K in GROUP}
        best=max(scs,key=scs.get)
        if best!=p['leg'] and scs[best]>scs[p['leg']]+0.05:
            p['leg']=best; p['score']=round(scs[best],4); relab+=1
print("group relabelled:",relab)
relink()
order=sorted(range(len(pts)),key=lambda i:-((2 if 'num_idx' in pts[i] else 0)+pts[i]['score']))
keep=[]; keptpos=[]
for i in order:
    p=pts[i]
    if any((p['cx']-a)**2+(p['cy']-b)**2<25 for a,b in keptpos): continue
    keep.append(p); keptpos.append((p['cx'],p['cy']))
print(f"dedup {len(pts)}->{len(keep)}"); pts[:]=keep
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
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6d.pkl','wb'))
# montages
def montage(selpts,path,cols=7):
    cells=[]
    for p in selpts:
        x,y=int(round(p['cx'])),int(round(p['cy']))
        win=np.full((29,29,3),255,np.uint8)
        src=baseu[max(0,y-14):y+15,max(0,x-14):x+15]
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
montage([p for p in pts if p['leg']==44],'work/qa/v6d_leg44.png')
montage([p for p in pts if p['leg']==52],'work/qa/v6d_leg52.png')
# leg14 unfilled windows
t14,m14,bx14,by14=tpl(14)
unf14=[]
for ni,ns in enumerate(num_state):
    if ns['expected'].get(14,0)>0 and ns['filled'][14]<ns['expected'][14]:
        r=window_peak_tpl(t14,m14,bx14,by14,ns['num']['px'],ns['num']['py'],42,[])
        if r: unf14.append((r[2],ni,r[0],r[1]))
unf14.sort(reverse=True)
print("leg14 unfilled:",len(unf14),"peaks pct:",np.round(np.percentile([u[0] for u in unf14],[0,25,50,75,90,100]),3) if unf14 else None)
cells=[]
for v,ni,px,py in unf14[:12]:
    ns=num_state[ni]; x,y=int(round(ns['num']['px'])),int(round(ns['num']['py']))
    win=np.full((61,61,3),255,np.uint8)
    src=baseu[max(0,y-30):y+31,max(0,x-30):x+31]
    win[30-(y-max(0,y-30)):30-(y-max(0,y-30))+src.shape[0],30-(x-max(0,x-30)):30-(x-max(0,x-30))+src.shape[1]]=src
    cv2.drawMarker(win,(30,30),(255,0,0),cv2.MARKER_CROSS,9,1)
    cv2.drawMarker(win,(int(round(px-x))+30,int(round(py-y))+30),(0,0,255),cv2.MARKER_TILTED_CROSS,7,1)
    cv2.putText(win,f"Nb {ns['num']['zone']}{ns['num']['value']} pk{v:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.3,(0,0,255),1)
    cells.append(cv2.resize(win,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
if cells:
    H=cells[0].shape[0]; W=cells[0].shape[1]; cols=4; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite('work/qa/v6d_leg14_unfilled.png',canvas); print("saved leg14 unfilled montage")
