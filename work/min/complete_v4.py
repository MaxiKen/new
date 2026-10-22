import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
gray=cv2.cvtColor(cv2.imread('work/min/mineral_base.png'),cv2.COLOR_BGR2GRAY)
thr_cal=json.load(open('work/min/thresholds.json'))
S=pickle.load(open('work/min/complete_v3.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
cand=pickle.load(open('work/min/cand_v2.pkl','rb'))

TPL={}; INK={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        ys,xs=np.where(m>0)
        TPL[L]=(t,m,(xs.min()+xs.max())/2,(ys.min()+ys.max())/2)
    return TPL[L]
def ink_tpl(L):
    if L not in INK:
        t,m,bcx,bcy=tpl(L)
        bgmask=m==0
        if bgmask.sum()>=10: bg=np.median(t[bgmask],axis=0)
        else:
            ring=np.zeros_like(m); ring[0,:]=1; ring[-1,:]=1; ring[:,0]=1; ring[:,-1]=1
            bg=np.median(t[ring>0],axis=0)
        diff=np.abs(t-bg).max(axis=2)
        ink=((m>0)&(diff>45)).astype(np.float32)
        if ink.sum()<12:
            ys,xs=np.where(m>0); vals=t[ys,xs]; mu=vals.mean(axis=0)
            contr=np.abs(vals-mu).max(axis=1); cut=np.percentile(contr,38)
            ink=np.zeros_like(m); ink[ys[contr>=cut],xs[contr>=cut]]=1
        INK[L]=(t,ink,bcx,bcy)
    return INK[L]
def score_at(L,cx,cy,ink=False):
    t,m,bcx,bcy=ink_tpl(L) if ink else tpl(L)
    WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    return float(np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=1.6,ncc,-1).max())
def dark_near(cx,cy,dx,dy):
    x,y=int(round(cx+dx)),int(round(cy+dy))
    sub=gray[max(0,y-1):y+1,max(0,x-1):x+1]
    return bool((sub<140).any())
def phos_ok(cx,cy):
    corners=sum(dark_near(cx,cy,sx*4,sy*4) for sx in (-1,1) for sy in (-1,1))
    plus=sum(dark_near(cx,cy,dx,dy) for dx,dy in [(0,-2),(0,2),(-2,0),(2,0)])
    return corners>=3 and plus>=3

allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
p32=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(32,0)>0]
tree32=cKDTree(np.array(p32))
existing=[(p['cx'],p['cy']) for p in pts]
added32=0
for d in sorted([d for d in cand if d['leg']==32],key=lambda d:-d['score']):
    cx,cy,sc=d['cx'],d['cy'],d['score']
    de=float(tree32.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
    if not ((de<=40 and sc>=0.95) or (sc>=0.97 and da<=60)): continue
    if not phos_ok(cx,cy): continue
    if any((cx-a)**2+(cy-b)**2<16 for a,b in existing): continue
    pts.append({'leg':32,'cx':cx,'cy':cy,'score':sc,'tier':'ctx' if de<=40 else 'free','match_type':'complete'})
    existing.append((cx,cy)); added32+=1
print("phosphate added:",added32)
# relink (filled accounting)
for ns in num_state: ns['filled']=Counter(); ns['pts']=[]
for p in pts: p.pop('num_idx',None)
pairs=[]
for pi,p in enumerate(pts):
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(p['leg'],0)>0:
            dist=np.hypot(p['cx']-ns['num']['px'],p['cy']-ns['num']['py'])
            if dist<=40: pairs.append((-p['score'],dist,pi,ni))
pairs.sort(); used=set()
for negsc,dist,pi,ni in pairs:
    if pi in used: continue
    p=pts[pi]; ns=num_state[ni]
    if ns['filled'][p['leg']]>=ns['expected'][p['leg']]: continue
    ns['filled'][p['leg']]+=1; ns['pts'].append(pi); used.add(pi); p['num_idx']=ni
print("filled after phos:",sum(sum(ns['filled'].values()) for ns in num_state))

# ---- ink-mask windowed complete fill (round 3) ----
def window_peak_ink(L,nx,ny,R,exclude):
    t,m,bcx,bcy=ink_tpl(L); WR=int(R+14)
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
baseu=cv2.imread('work/min/mineral_base.png')
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
LEGS=[L for L in range(1,68) if L!=49]
exclude=[(p['cx'],p['cy']) for p in pts]
added=0
for ni,ns in enumerate(num_state):
    for L,cnt in list(ns['expected'].items()):
        if L==62: continue
        for _ in range(cnt-ns['filled'][L]):
            r=window_peak_ink(L,ns['num']['px'],ns['num']['py'],40,exclude)
            if r is None: continue
            cx,cy,sc=r
            floor=0.85 if L in (1,8,48,50,67) else 0.78
            if sc<floor: continue
            si=score_at(L,cx,cy,ink=True)
            best_other=max((score_at(K,cx,cy,ink=True) for K in LEGS if K!=L),default=0)
            if best_other>si+0.02: continue
            if not shape_ok(L,cx,cy): continue
            if L==32 and not phos_ok(cx,cy): continue
            if L==53 and score_at(31,cx,cy)>score_at(53,cx,cy)+0.03: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(float(sc),4),'tier':'ink','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; ns['pts'].append(len(pts)-1); exclude.append((cx,cy)); added+=1
print("ink fill added:",added)
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"COMPLETE v4 points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete_v4.pkl','wb'))
