import cv2, numpy as np, json, pickle, sys
import pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
thr_cal=json.load(open('work/min/thresholds.json'))
S=pickle.load(open('work/min/complete6.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
cand=pickle.load(open('work/min/cand_v6.pkl','rb'))
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
def thr_ctx(L):
    p5=C6[str(L)]['self_p5'] if str(L) in C6 else None
    return float(np.clip(p5-0.12,0.72,0.92)) if p5 else 0.88
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
exclude=[(p['cx'],p['cy']) for p in pts]
# --- leg52 dedicated pass (no colour gate; competitor-guarded) ---
allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
exp52=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(52,0)>0]
tree52=cKDTree(np.array(exp52))
n52=0
for d in sorted([d for d in cand if d['leg']==52],key=lambda d:-d['score']):
    cx,cy,sc=d['cx'],d['cy'],d['score']
    de=float(tree52.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
    tier=None
    if de<=42 and sc>=0.72: tier='ctx'
    elif sc>=0.93: tier='free'
    elif sc>=0.88 and da<=34: tier='near'
    if not tier: continue
    if any((cx-a)**2+(cy-b)**2<25 for a,b in exclude): continue
    si=score_at(52,cx,cy)
    bo=max(score_at(K,cx,cy) for K in LEGS if K!=52)
    if si<bo-0.02: continue
    pts.append({'leg':52,'cx':cx,'cy':cy,'score':sc,'tier':tier,'match_type':'complete'})
    exclude.append((cx,cy)); n52+=1
print("leg52 sweep added:",n52)
relink()
# leg52 window fill
n=0
for ni,ns in enumerate(num_state):
    if ns['expected'].get(52,0)==0: continue
    for _ in range(ns['expected'][52]-ns['filled'][52]):
        r=window_peak(52,ns['num']['px'],ns['num']['py'],42,exclude)
        if r is None or r[2]<max(0.65,float(thr_cal['52']['thr'])): continue
        cx,cy,sc=r
        si=score_at(52,cx,cy); bo=max(score_at(K,cx,cy) for K in LEGS if K!=52)
        if si<bo-0.02: continue
        pts.append({'leg':52,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'winA','match_type':'complete','num_idx':ni})
        ns['filled'][52]+=1; exclude.append((cx,cy)); n+=1
print("leg52 window added:",n)
relink()
# --- window round C: strong-match override (no margin >=0.88) ---
added=0
for ni,ns in enumerate(num_state):
    for L,cnt in list(ns['expected'].items()):
        if L in (32,49,62,52): continue
        for _ in range(cnt-ns['filled'][L]):
            r=window_peak(L,ns['num']['px'],ns['num']['py'],42,exclude)
            if r is None: continue
            cx,cy,sc=r
            if sc>=0.88:
                ok=True
            else:
                floorA=min(thr_ctx(L),max(0.65,float(thr_cal[str(L)]['thr'])))
                if sc<floorA: continue
                si=score_at(L,cx,cy); bo=max(score_at(K,cx,cy) for K in LEGS if K!=L)
                ok = si>=bo-0.02
            if not ok: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(float(sc),4),'tier':'winC','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; exclude.append((cx,cy)); added+=1
print("window round C added:",added)
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
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6b.pkl','wb'))
# QA montages: leg19 sample, leg52 all, leg53 pts, leg25 sample
def montage(sel,labels,path,cols=7):
    cells=[]
    for (cx,cy),lb in zip(sel,labels):
        x,y=int(round(cx)),int(round(cy))
        win=np.full((29,29,3),255,np.uint8)
        src=cv2.imread('work/min/mineral_base.png')[max(0,y-14):y+15,max(0,x-14):x+15]
        win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
        cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
        cv2.putText(win,lb,(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.32,(0,0,255),1)
        cells.append(cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST))
    if not cells: return
    H=cells[0].shape[0]; W=cells[0].shape[1]; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite(path,canvas); print("saved",path,len(cells))
import random
random.seed(4)
for L in [19,52,25]:
    selpts=[p for p in pts if p['leg']==L]
    s=selpts if len(selpts)<=21 else random.sample(selpts,21)
    montage([(p['cx'],p['cy']) for p in s],[f"L{L} {p['score']:.2f}" for p in s],f'work/qa/v6_leg{L}.png')
s53=[p for p in pts if p['leg']==53]
montage([(p['cx'],p['cy']) for p in s53],[f"L53 {p['score']:.2f}" for p in s53],'work/qa/v6_leg53.png',cols=2)
s7=[p for p in pts if p['leg']==7]
montage([(p['cx'],p['cy']) for p in s7],[f"L7 {p['score']:.2f}" for p in s7],'work/qa/v6_leg7.png',cols=1)
