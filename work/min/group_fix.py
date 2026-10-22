import cv2, numpy as np, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
from scipy.ndimage import maximum_filter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
gray=cv2.cvtColor(cv2.imread('work/min/mineral_base.png'),cv2.COLOR_BGR2GRAY)
S=pickle.load(open('work/min/complete_v4.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
cand=pickle.load(open('work/min/cand_v2.pkl','rb'))
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        ys,xs=np.where(m>0)
        TPL[L]=(t,m,(xs.min()+xs.max())/2,(ys.min()+ys.max())/2)
    return TPL[L]
def score_at(L,cx,cy,tol=1.6):
    t,m,bcx,bcy=tpl(L); WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0,None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ncc=np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=tol,ncc,-1)
    i=np.argmax(ncc); y,x=np.unravel_index(i,ncc.shape)
    return float(ncc.ravel()[i]),(float(x+x0+bcx),float(y+y0+bcy))
def window_peak(L,nx,ny,R,exclude=()):
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

# drop dubious leg53 + old leg17 points
pts=[p for p in pts if p['leg'] not in (53,17)]
print("dropped 53/17; pts now",len(pts))
# --- PHOSPHATE: context-only with rebuilt template ---
exclude=[(p['cx'],p['cy']) for p in pts]
print("=== P numbers diagnosis ===")
for ni,ns in enumerate(num_state):
    if ns['expected'].get(32,0)==0: continue
    r=window_peak(32,ns['num']['px'],ns['num']['py'],40,exclude)
    if r is None: print(ns['key'],"no window"); continue
    cx,cy,sc=r
    s31,_=score_at(31,cx,cy); s3,_=score_at(3,cx,cy)
    print(f"{ns['key']} peak32={sc:.3f} at ({cx:.0f},{cy:.0f}) s31={s31:.3f} s3={s3:.3f}")
    if sc>=0.90:
        pts.append({'leg':32,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'ctx','match_type':'complete'})
        exclude.append((cx,cy))
# relabel existing 31 pts near P numbers if clearly phosphate
pnums=[ns for ns in num_state if ns['expected'].get(32,0)>0]
for p in pts:
    if p['leg']==31:
        if any(np.hypot(p['cx']-ns['num']['px'],p['cy']-ns['num']['py'])<=40 for ns in pnums):
            s32,_=score_at(32,p['cx'],p['cy'])
            if s32>=0.95:
                print(f"relabel 31->32 at ({p['cx']:.0f},{p['cy']:.0f}) s32={s32:.3f} was {p['score']}")
                p['leg']=32; p['score']=round(s32,4)
# dedup 32 within 5px keep best
p32=sorted([p for p in pts if p['leg']==32],key=lambda p:-p['score'])
keep32=[]
for p in p32:
    if any((p['cx']-a['cx'])**2+(p['cy']-a['cy'])**2<25 for a in keep32): continue
    keep32.append(p)
pts=[p for p in pts if p['leg']!=32]+keep32
print("phosphate points:",len(keep32))
# --- restore lost Baryte/Gypsum glyphs from cand pool ---
existing=[(p['cx'],p['cy']) for p in pts]
allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
def d_exp(L,cx,cy):
    ps=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(L,0)>0]
    return min(np.hypot(cx-a,cy-b) for a,b in ps) if ps else 9999
restored=0
pool=sorted([d for d in cand if d['leg'] in (3,31)],key=lambda d:-d['score'])
for d in pool:
    cx,cy=d['cx'],d['cy']
    if any((cx-a)**2+(cy-b)**2<16 for a,b in existing): continue
    s3,c3=score_at(3,cx,cy); s31,c31=score_at(31,cx,cy)
    L,sc,cc=(3,s3,c3) if s3>=s31 else (31,s31,c31)
    if cc is None: continue
    cx,cy=cc
    de=d_exp(L,cx,cy); da=float(tree_all.query([cx,cy])[0])
    tier=None
    if de<=40 and sc>=0.82: tier='ctx'
    elif sc>=0.95: tier='free'
    elif sc>=0.90 and da<=34: tier='near'
    if not tier: continue
    if any((cx-a)**2+(cy-b)**2<16 for a,b in existing): continue
    pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':tier,'match_type':'complete'})
    existing.append((cx,cy)); restored+=1
print("restored 3/31:",restored)
# --- DIATOMITE (17): context + strict free ---
exclude=[(p['cx'],p['cy']) for p in pts]
for ni,ns in enumerate(num_state):
    if ns['expected'].get(17,0)==0: continue
    r=window_peak(17,ns['num']['px'],ns['num']['py'],40,exclude)
    if r and r[2]>=0.90:
        pts.append({'leg':17,'cx':r[0],'cy':r[1],'score':round(r[2],4),'tier':'ctx','match_type':'complete'})
        exclude.append((r[0],r[1]))
        print("diatomite ctx",ns['key'],round(r[2],3))
# full-map strict candidates for 17
t,m,bcx,bcy=tpl(17)
ncc=masked_ncc(base,t,m)
mx=maximum_filter(ncc,size=7)
cand17=np.argwhere((ncc>=mx-1e-6)&(ncc>=0.995))
darkm=(gray<95).astype(np.uint8)
def cc_dark_rect(cx,cy):
    x,y=int(round(cx)),int(round(cy))
    x0,y0=max(0,x-11),max(0,y-11); x1,y1=min(BW,x+12),min(BH,y+12)
    sub=darkm[y0:y1,x0:x1]
    n,lab,stats,cent=cv2.connectedComponentsWithStats(sub,8)
    for dy in range(-2,3):
        for dx in range(-2,3):
            xx,yy=x-x0+dx,y-y0+dy
            if 0<=xx<sub.shape[1] and 0<=yy<sub.shape[0] and lab[yy,xx]>0:
                X,Y,W,H,A=stats[lab[yy,xx]]
                return 9<=W<=13 and 6<=H<=9 and X>0 and Y>0 and X+W<sub.shape[1] and Y+H<sub.shape[0]
    return False
n17=0
for y,x in cand17:
    cx,cy=x+bcx,y+bcy; sc=float(ncc[y,x])
    if any((cx-a)**2+(cy-b)**2<16 for a,b in exclude): continue
    if not cc_dark_rect(cx,cy): continue
    others=max(score_at(K,cx,cy)[0] for K in (13,38,59))
    if others>=sc: continue
    pts.append({'leg':17,'cx':float(cx),'cy':float(cy),'score':round(sc,4),'tier':'free','match_type':'complete'})
    exclude.append((cx,cy)); n17+=1
print("diatomite free added:",n17)
# relink
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
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"COMPLETE v5 points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete_v5.pkl','wb'))
