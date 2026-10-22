import cv2, numpy as np, json, pickle, sys
import pandas as pd, geopandas as gpd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
thr_cal=json.load(open('work/min/thresholds.json'))
tab=pd.read_pickle('work/min/tables_final.pkl')
zoned=pickle.load(open('work/min/map_numbers_zoned2.pkl','rb'))
cand=pickle.load(open('work/min/cand_v6.pkl','rb'))
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':2,'Be':6,'Gm':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Sd':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ks':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Ms':44,'Mu':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'St':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67}
def to_px(x,y): return ((x-74.2397)/0.959996,(y-358.724)/0.959996)
expected={}
for _,r in tab.iterrows():
    key=(r.zone,int(r.link_num))
    legs=expected.setdefault(key,Counter()); seen=set()
    for c in r.codes_list:
        L=CODE2LEG.get(c)
        if L and L not in seen: legs[L]+=1; seen.add(L)
num_state=[]; zoned_fixed=0
for d in zoned:
    px,py=to_px(d['cx'],d['cy'])
    zone=d['zone']; val=int(d['value']); key=(zone,val)
    if key not in expected and d.get('border_dist',999)<35:
        alts=[z for z in 'ABCDEFG' if (z,val) in expected]
        if len(alts)==1: key=(alts[0],val); zoned_fixed+=1
    num_state.append({'num':{'zone':zone,'value':val,'px':px,'py':py},'key':key,
                      'expected':expected.get(key,Counter()),'filled':Counter(),'pts':[]})
print("zone-fallback numbers:",zoned_fixed)
print("expected slots:",sum(sum(ns['expected'].values()) for ns in num_state))
allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
leg_pts={L:[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(L,0)>0] for L in range(1,68)}
leg_trees={L:(cKDTree(np.array(v)) if v else None) for L,v in leg_pts.items()}
def d_exp(L,cx,cy):
    tr=leg_trees[L]; return float(tr.query([cx,cy])[0]) if tr is not None else 9999.0
def thr_free(L):
    p5=C6[str(L)]['self_p5'] if str(L) in C6 else None
    return float(np.clip(p5-0.03,0.90,0.97)) if p5 else 0.95
def thr_ctx(L):
    p5=C6[str(L)]['self_p5'] if str(L) in C6 else None
    v=float(np.clip(p5-0.12,0.72,0.92)) if p5 else 0.88
    if L==39: v=max(v,0.82)
    return v
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        bcx,bcy=C6[str(L)]['center_xy']
        TPL[L]=(t,m,bcx,bcy)
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
# shape gates
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
CTX_ONLY={1,7,8,17,30,48,50,53,55,62,67}
pts=[]
for d in cand:
    L,sc,cx,cx_,cy=d['leg'],d['score'],d['cx'],d['cx'],d['cy']
    cx=d['cx']
    if L==62: continue
    de=d_exp(L,cx,cy); da=float(tree_all.query([cx,cy])[0])
    tier=None
    if de<=42 and sc>=thr_ctx(L): tier='ctx'
    elif L not in CTX_ONLY:
        if sc>=thr_free(L): tier='free'
        elif sc>=thr_free(L)-0.05 and da<=34: tier='near'
    if tier is None: continue
    if not shape_ok(L,cx,cy): continue
    pts.append({'leg':L,'cx':cx,'cy':cy,'score':sc,'tier':tier,'match_type':'complete'})
order={'ctx':0,'near':1,'free':2}
pts.sort(key=lambda p:(order[p['tier']],-p['score']))
acc=[]
for p in pts:
    if any((p['cx']-a['cx'])**2+(p['cy']-a['cy'])**2<16 for a in acc): continue
    acc.append(p)
pts=acc
print("sweep accepted:",len(pts),Counter(p['tier'] for p in pts))
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
relink()
print("filled after sweep:",sum(sum(ns['filled'].values()) for ns in num_state))
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
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
exclude=[(p['cx'],p['cy']) for p in pts]
for rnd,margin,strict_absent in [('A',-0.02,True),('B',0.02,False)]:
    added=0
    for ni,ns in enumerate(num_state):
        for L,cnt in list(ns['expected'].items()):
            if L in (32,49,62): continue
            if rnd=='A' and L in (1,8,48,50,53,55,67): continue
            for _ in range(cnt-ns['filled'][L]):
                floorA=min(thr_ctx(L),max(0.65,float(thr_cal[str(L)]['thr'])))
                floor=floorA if rnd=='A' else max(0.60,floorA-0.07)
                if L in (1,8,48,50,53,55,67): floor=max(floor,0.80)
                r=window_peak(L,ns['num']['px'],ns['num']['py'],42,exclude)
                if r is None or r[2]<floor: continue
                cx,cy,sc=r
                si,_=score_at(L,cx,cy)
                bo=max(score_at(K,cx,cy)[0] for K in LEGS if K!=L)
                if si<bo+margin: continue
                if not shape_ok(L,cx,cy): continue
                pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(float(sc),4),'tier':'win'+rnd,'match_type':'complete','num_idx':ni})
                ns['filled'][L]+=1; ns['pts'].append(len(pts)-1); exclude.append((cx,cy)); added+=1
    print(f"window round {rnd} added:",added)
relink()
print("filled after windows:",sum(sum(ns['filled'].values()) for ns in num_state))
# old-audit recovery
old=gpd.read_file('shapefile_results/minerals/nigeria_mineral_symbols.shp')
tree_pts=cKDTree(np.array([[p['cx'],p['cy']] for p in pts]))
dold,_=tree_pts.query(np.stack([old.px_x.values,old.px_y.values],axis=1))
exclude=[(p['cx'],p['cy']) for p in pts]
rec=0
for (ox,oy),dd in zip(zip(old.px_x.values,old.px_y.values),dold):
    if dd<=8: continue
    best=(-1,None,None)
    for L in LEGS:
        s,cc=score_at(L,float(ox),float(oy),tol=3.0)
        if s>best[0]: best=(s,L,cc)
    s,L,cc=best
    if cc is None: continue
    cx,cy=cc
    ok = s>=thr_free(L) or (s>=thr_ctx(L) and d_exp(L,cx,cy)<=42)
    if not ok: continue
    if any((cx-a)**2+(cy-b)**2<25 for a,b in exclude): continue
    if not shape_ok(L,cx,cy): continue
    pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(float(s),4),'tier':'audit','match_type':'complete'})
    exclude.append((cx,cy)); rec+=1
print("audit recovered:",rec)
relink()
# phosphate via shared glyph (leg31 template)
exclude=[(p['cx'],p['cy']) for p in pts]
for ni,ns in enumerate(num_state):
    if ns['expected'].get(32,0)==0: continue
    r=window_peak(31,ns['num']['px'],ns['num']['py'],42,exclude)
    if r and r[2]>=0.90:
        pts.append({'leg':32,'cx':r[0],'cy':r[1],'score':round(r[2],4),'tier':'ctx','match_type':'complete'})
        exclude.append((r[0],r[1]))
relink()
for ni,ns in enumerate(num_state):
    if ns['expected'].get(32,0)>0 and ns['expected'].get(31,0)==0 and ns['filled'][32]<ns['expected'][32]:
        for p in pts:
            if p['leg']==31 and 'num_idx' not in p and np.hypot(p['cx']-ns['num']['px'],p['cy']-ns['num']['py'])<=42:
                p['leg']=32; break
relink()
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"COMPLETE6 points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
print("tiers:",Counter(p['tier'] for p in pts))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6.pkl','wb'))
