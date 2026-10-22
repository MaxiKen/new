import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
baseu=cv2.imread('work/min/mineral_base.png')
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
S=pickle.load(open('work/min/complete6L.pkl','rb'))
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
gray=cv2.cvtColor(baseu,cv2.COLOR_BGR2GRAY)
Bc,Gc,Rc=baseu[:,:,0].astype(int),baseu[:,:,1].astype(int),baseu[:,:,2].astype(int)
yellow=((Rc>175)&(Gc>155)&(Bc<115)).astype(np.uint8)
darkm=(gray<95).astype(np.uint8)
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
    return True
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
# 1) drop leg7, leg30
n0=len(pts)
pts[:]=[p for p in pts if p['leg'] not in (7,30)]
print(f"dropped leg7/leg30: {n0}->{len(pts)}")
relink()
# 2) leg53 check
drop53=[]
for p in [p for p in pts if p['leg']==53]:
    ni=p.get('num_idx')
    gyexp = num_state[ni]['expected'].get(31,0)>0 if ni is not None else False
    print(f"leg53 pt at ({p['cx']:.0f},{p['cy']:.0f}) num={num_state[ni]['num'] if ni is not None else None} GyExpected={gyexp} s31={score_at(31,p['cx'],p['cy']):.3f} s53={score_at(53,p['cx'],p['cy']):.3f}")
    if gyexp: drop53.append(p)
for p in drop53: pts.remove(p)
print("leg53 dropped (Gy also expected):",len(drop53))
relink()
# 3) leg13 vs leg34 arbitration
fl=0
for p in pts:
    if p['leg']==13:
        s13=score_at(13,p['cx'],p['cy']); s34=score_at(34,p['cx'],p['cy'])
        if s34>s13+0.03:
            p['leg']=34; p['score']=round(s34,4); fl+=1
print("leg13->34 relabelled:",fl)
relink()
order=sorted(range(len(pts)),key=lambda i:-((2 if 'num_idx' in pts[i] else 0)+pts[i]['score']))
keep=[]; keptpos=[]
for i in order:
    p=pts[i]
    if any((p['cx']-a)**2+(p['cy']-b)**2<25 for a,b in keptpos): continue
    keep.append(p); keptpos.append((p['cx'],p['cy']))
print(f"dedup {len(pts)}->{len(keep)}"); pts[:]=keep
relink()
# 4) top-up window round for missed strong peaks
def window_peak_tpl(t,m,bcx,bcy,nx,ny,R,exclude,excl_r=7.0):
    WR=int(R+14)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+bcx; ccy=yy+y0+bcy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>excl_r)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return float(x+x0+bcx),float(y+y0+bcy),v
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
SKIP={1,7,8,30,48,50,52,53,55,67}
exclude=[(p['cx'],p['cy']) for p in pts]
added=[]
for ni,ns in enumerate(num_state):
    for L,c in list(ns['expected'].items()):
        if L in SKIP or L in (32,49,62): continue
        for _ in range(c-ns['filled'][L]):
            t,m,bcx,bcy=tpl(L)
            r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,exclude)
            if r is None or r[2]<0.88: continue
            cx,cy,sc=r
            if L in (6,25,26,13,38) and not shape_ok(L,cx,cy): continue
            si=score_at(L,cx,cy)
            bo=max(score_at(K,cx,cy) for K in LEGS if K!=L)
            if si<bo-0.02: continue
            rec={'leg':L,'cx':cx,'cy':cy,'score':round(float(sc),4),'tier':'winE','match_type':'complete','num_idx':ni}
            pts.append(rec); added.append(rec)
            ns['filled'][L]+=1; exclude.append((cx,cy))
print("top-up winE added:",len(added),dict(Counter(a['leg'] for a in added)))
relink()
# min separation
mind=999
P=np.array([[p['cx'],p['cy']] for p in pts])
for i in range(len(P)):
    d=np.hypot(P[i,0]-P[i+1:,0],P[i,1]-P[i+1:,1])
    if len(d): mind=min(mind,float(d.min()))
print("min pairwise separation (px):",round(mind,2))
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6m.pkl','wb'))
print("saved complete6m.pkl")
