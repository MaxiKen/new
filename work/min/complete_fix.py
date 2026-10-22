import cv2, numpy as np, json, pickle, sys
import pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
baseu=cv2.imread('work/min/mineral_base.png')
gray=cv2.cvtColor(baseu,cv2.COLOR_BGR2GRAY)
thr_cal=json.load(open('work/min/thresholds.json'))
S=pickle.load(open('work/min/complete_v2.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        ys,xs=np.where(m>0)
        TPL[L]=(t,m,(xs.min()+xs.max())/2,(ys.min()+ys.max())/2)
    return TPL[L]
def score_at(L,cx,cy):
    t,m,bcx,bcy=tpl(L); WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ncc=np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=1.6,ncc,-1)
    return float(ncc.max())
LEGS=[L for L in range(1,68) if L!=49]
def argmax_all(cx,cy,exclude=()):
    best=(0,-1)
    for L in LEGS:
        if L in exclude: continue
        v=score_at(L,cx,cy)
        if v>best[1]: best=(L,v)
    return best
def mask_vals(L,cx,cy):
    t,m,bcx,bcy=tpl(L)
    x0=int(round(cx-bcx)); y0=int(round(cy-bcy))
    th,tw=t.shape[:2]
    if x0<0 or y0<0 or x0+tw>BW or y0+th>BH: return None
    return gray[y0:y0+th,x0:x0+tw][m>0]
def ink6(cx,cy):
    v=mask_vals(6,cx,cy)
    if v is None or len(v)==0: return False
    return (v<80).mean()>=0.22 and (v>200).mean()>=0.13
def ringfrac(cx,cy,r=4.0):
    an=np.linspace(0,2*np.pi,16,endpoint=False)
    xs=np.clip((cx+r*np.cos(an)).astype(int),0,BW-1); ys=np.clip((cy+r*np.sin(an)).astype(int),0,BH-1)
    return float((gray[ys,xs]<110).mean())
darkm=(gray<95).astype(np.uint8)
def cc_dark_ok(cx,cy,maxw,maxh):
    x,y=int(round(cx)),int(round(cy))
    x0,y0=max(0,x-11),max(0,y-11); x1,y1=min(BW,x+12),min(BH,y+12)
    sub=darkm[y0:y1,x0:x1]
    n,lab,stats,cent=cv2.connectedComponentsWithStats(sub,8)
    best=None
    for dy in range(-2,3):
        for dx in range(-2,3):
            xx,yy=x-x0+dx,y-y0+dy
            if 0<=xx<sub.shape[1] and 0<=yy<sub.shape[0] and lab[yy,xx]>0: best=lab[yy,xx]; break
        if best: break
    if best is None: return False
    X,Y,W,H,A=stats[best]
    return W<=maxw and H<=maxh and X>0 and Y>0 and X+W<sub.shape[1] and Y+H<sub.shape[0]

keep=[]; relabeled=0
for p in pts:
    L=p['leg']
    if L==62: continue
    if L==6:
        if p['score']<0.97 or not ink6(p['cx'],p['cy']): continue
    if L==32:
        if not ((p['tier']=='ctx' and p['score']>=0.95) or p['score']>=0.99): continue
        if ringfrac(p['cx'],p['cy'])<0.5: continue
        bl,bv=argmax_all(p['cx'],p['cy'])
        if bv>score_at(32,p['cx'],p['cy'])+0.02: continue
    if L==13:
        if not cc_dark_ok(p['cx'],p['cy'],14,9): continue
        bl,bv=argmax_all(p['cx'],p['cy'])
        s13=score_at(13,p['cx'],p['cy'])
        if bv>s13+0.04:
            if bl in (38,59): p=dict(p); p['leg']=bl; p['score']=round(bv,4); relabeled+=1
            else: continue
    if p['leg']==38:
        if not cc_dark_ok(p['cx'],p['cy'],11,14): continue
    keep.append(p)
pts=keep
print("after fix filters:",len(pts),"relabeled coal->lignite/tarsand:",relabeled)
print("leg6:",sum(1 for p in pts if p['leg']==6)," leg32:",sum(1 for p in pts if p['leg']==32),
      " leg13:",sum(1 for p in pts if p['leg']==13)," leg38:",sum(1 for p in pts if p['leg']==38),
      " leg59:",sum(1 for p in pts if p['leg']==59))
# rebuild linkage
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
print("filled after relink:",sum(sum(ns['filled'].values()) for ns in num_state))
# ---- windowed complete round 2 (weak templates, argmax-guarded) ----
WEAK={9,16,19,21,30,34,37,44,45,52,55,56,60,64}
def window_peak(L,nx,ny,R,exclude):
    t,m,bcx,bcy=tpl(L); WR=int(R+14)
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
exclude=[(p['cx'],p['cy']) for p in pts]
added=0
for ni,ns in enumerate(num_state):
    for L,cnt in list(ns['expected'].items()):
        if L not in WEAK: continue
        for _ in range(cnt-ns['filled'][L]):
            floor2=min(0.80,max(0.64,float(thr_cal[str(L)]['thr'])-0.06))
            r=window_peak(L,ns['num']['px'],ns['num']['py'],40,exclude)
            if r is None or r[2]<floor2: continue
            cx,cy,sc=r
            si=score_at(L,cx,cy)
            bl,bv=argmax_all(cx,cy)
            if bv>si+0.02: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'win2','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; ns['pts'].append(len(pts)-1); exclude.append((cx,cy)); added+=1
print("round2 added:",added)
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"COMPLETE v3 points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete_v3.pkl','wb'))
