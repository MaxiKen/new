import cv2, numpy as np, json, pickle, sys
import pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
thr_cal=json.load(open('work/min/thresholds.json'))
tab=pd.read_pickle('work/min/tables_final.pkl')
zoned=pickle.load(open('work/min/map_numbers_zoned2.pkl','rb'))
cand=pickle.load(open('work/min/cand_v2.pkl','rb'))
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':2,'Be':6,'Gm':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Sd':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ks':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Ms':44,'Mu':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'St':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67}
def to_px(x,y): return ((x-74.2397)/0.959996,(y-358.724)/0.959996)
numbers=[]
for d in zoned:
    px,py=to_px(d['cx'],d['cy'])
    numbers.append({'zone':d['zone'],'value':int(d['value']),'px':px,'py':py})
expected={}
for _,r in tab.iterrows():
    key=(r.zone,int(r.link_num))
    legs=expected.setdefault(key,Counter()); seen=set()
    for c in r.codes_list:
        L=CODE2LEG.get(c)
        if L and L not in seen: legs[L]+=1; seen.add(L)
num_state=[]
for n in numbers:
    key=(n['zone'],n['value'])
    num_state.append({'num':n,'key':key,'expected':expected.get(key,Counter()),'filled':Counter(),'pts':[]})
print("total expected slots at numbers:", sum(sum(ns['expected'].values()) for ns in num_state))
# numbers expecting each leg (for context tests)
from scipy.spatial import cKDTree
allnum_xy=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum_xy)
leg_trees={}
for L in range(1,68):
    pts=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(L,0)>0]
    leg_trees[L]=cKDTree(np.array(pts)) if pts else None
def d_exp(L,cx,cy):
    tr=leg_trees[L]
    return float(tr.query([cx,cy])[0]) if tr is not None else 9999.0
def d_any(cx,cy): return float(tree_all.query([cx,cy])[0])

TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        ys,xs=np.where(m>0)
        TPL[L]=(t,m,(xs.min()+xs.max())/2,(ys.min()+ys.max())/2)
    return TPL[L]
def score_at(L,cx,cy,R=1.6):
    t,m,bcx,bcy=tpl(L)
    WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ncc=np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=R,ncc,-1)
    return float(ncc.max())

# ---- shape gates (yellow/dark blob compactness) ----
baseu=cv2.imread('work/min/mineral_base.png')
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
    if L==6:  return cc_check(darkm,cx,cy,9,10)
    if L==25: return cc_check(yellow,cx,cy,11,11,central=True)
    if L==26: return cc_check(yellow,cx,cy,12,12,minw=7,minh=7,central=True)
    return True

CTX_ONLY={7,30,53,62}
pts=[]  # leg,cx,cy,score,tier
for d in cand:
    L,sc,cx,cy=d['leg'],d['score'],d['cx'],d['cy']
    de=d_exp(L,cx,cy); da=d_any(cx,cy)
    tier=None
    if de<=40 and sc>=0.82: tier='ctx'
    elif L==52 and de<=34 and sc>=0.80: tier='ctx'
    elif L==53 and de<=40 and sc>=0.75: tier='ctx'
    if tier is None and L not in CTX_ONLY:
        if L==32:
            if sc>=0.975 and da<=44: tier='free'
            elif de<=40 and sc>=0.90: tier='ctx'
        elif sc>=0.95: tier='free'
        elif sc>=0.90 and da<=34: tier='near'
    if tier is None: continue
    if L==32 and tier=='ctx' and sc<0.90: continue
    if not shape_ok(L,cx,cy): continue
    pts.append({'leg':L,'cx':cx,'cy':cy,'score':sc,'tier':tier,'match_type':'complete'})
print("after tiers+shape:",len(pts), Counter(p['tier'] for p in pts))
# white-circle free/near relabel to argmax among {3,31,32}
for p in pts:
    if p['leg'] in (3,31,32) and p['tier'] in ('free','near'):
        ss={L:score_at(L,p['cx'],p['cy']) for L in (3,31,32)}
        best=max(ss,key=ss.get)
        if ss[best]>=0.85: p['leg']=best; p['score']=round(ss[best],4)
# leg53/62 discrimination: must not look more like gypsum etc.
keep=[]
for p in pts:
    if p['leg']==53:
        if score_at(31,p['cx'],p['cy'])>p['score']+0.03: continue
    if p['leg']==62:
        ss={L:score_at(L,p['cx'],p['cy']) for L in (3,31,32)}
        if ss and max(ss.values())>p['score']: continue
    keep.append(p)
pts=keep
# cross-leg suppression: ctx first, then near, then free (score desc), radius 4px
order={'ctx':0,'near':1,'free':2}
pts.sort(key=lambda p:(order[p['tier']],-p['score']))
acc=[]
for p in pts:
    if any((p['cx']-a['cx'])**2+(p['cy']-a['cy'])**2<16 for a in acc): continue
    acc.append(p)
pts=acc
print("complete (a) accepted:",len(pts))
# link to numbers to fill slots
pairs=[]
for pi,p in enumerate(pts):
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(p['leg'],0)>0:
            dist=np.hypot(p['cx']-ns['num']['px'],p['cy']-ns['num']['py'])
            if dist<=40: pairs.append((-p['score'],dist,pi,ni))
pairs.sort()
used=set()
for negsc,dist,pi,ni in pairs:
    if pi in used: continue
    p=pts[pi]; ns=num_state[ni]
    if ns['filled'][p['leg']]>=ns['expected'][p['leg']]: continue
    ns['filled'][p['leg']]+=1; ns['pts'].append(pi); used.add(pi); p['num_idx']=ni
print("filled after (a):", sum(sum(ns['filled'].values()) for ns in num_state))

# ---- (b) windowed complete fill for unfilled slots ----
def window_peak(L,nx,ny,R,exclude):
    t,m,bcx,bcy=tpl(L)
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
exclude=[(p['cx'],p['cy']) for p in pts]
added=0
for ni,ns in enumerate(num_state):
    for L,cnt in list(ns['expected'].items()):
        for _ in range(cnt-ns['filled'][L]):
            floor=min(0.85,max(0.70,float(thr_cal[str(L)]['thr'])))
            if L==53: floor=0.72
            if L==62: floor=0.85
            r=window_peak(L,ns['num']['px'],ns['num']['py'],40,exclude)
            if r is None or r[2]<floor: continue
            cx,cy,sc=r
            if not shape_ok(L,cx,cy): continue
            if L==53 and score_at(31,cx,cy)>sc+0.03: continue
            if L==62:
                ss={K:score_at(K,cx,cy) for K in (3,31,32)}
                if max(ss.values())>sc: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'win','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; ns['pts'].append(len(pts)-1); exclude.append((cx,cy)); added+=1
print("windowed complete added:",added)
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"COMPLETE points={len(pts)}  filled slots={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete_v2.pkl','wb'))
