import cv2, numpy as np, json, pickle, sys, time
import pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import defaultdict, Counter

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
thr_cal=json.load(open('work/min/thresholds.json'))
tab=pd.read_pickle('work/min/tables_final.pkl')
zoned=pickle.load(open('work/min/map_numbers_zoned2.pkl','rb'))
S1=pickle.load(open('work/min/dets_v4.pkl','rb'))
dets=S1['dets']
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
# cluster dets -> objs
dets_sorted=sorted(dets,key=lambda d:-d['score'])
objs=[]; grid={}; cell=6
for i,d in enumerate(dets_sorted):
    gx,gy=int(d['cx']//cell),int(d['cy']//cell)
    found=None
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for oi in grid.get((gx+dx,gy+dy),[]):
                o=objs[oi]
                if (o['cx']-d['cx'])**2+(o['cy']-d['cy'])**2<=16: found=oi; break
            if found is not None: break
        if found is not None: break
    if found is None:
        objs.append({'cx':d['cx'],'cy':d['cy'],'scores':{d['leg']:(d['score'],i)},'claimed_by':None,'stage':1})
        grid.setdefault((gx,gy),[]).append(len(objs)-1)
    else:
        o=objs[found]
        if d['leg'] not in o['scores'] or d['score']>o['scores'][d['leg']][0]: o['scores'][d['leg']]=(d['score'],i)
print("objs:",len(objs))
num_state=[]
for n in numbers:
    key=(n['zone'],n['value'])
    num_state.append({'num':n,'key':key,'expected':expected.get(key,Counter()),'filled':Counter(),'objs':[]})
def claim(oi,ni,leg):
    objs[oi]['claimed_by']=(ni,leg); num_state[ni]['filled'][leg]+=1; num_state[ni]['objs'].append((oi,leg))
# pass1
pairs=[]
for oi,o in enumerate(objs):
    for ni,ns in enumerate(num_state):
        n=ns['num']; dist=np.hypot(o['cx']-n['px'],o['cy']-n['py'])
        if dist<=34:
            for leg,(sc,di) in o['scores'].items():
                if ns['expected'].get(leg,0)>0: pairs.append((-sc,dist,oi,ni,leg))
pairs.sort()
for negsc,dist,oi,ni,leg in pairs:
    if objs[oi]['claimed_by'] is not None: continue
    if num_state[ni]['filled'][leg]>=num_state[ni]['expected'][leg]: continue
    claim(oi,ni,leg)
f1=sum(sum(ns['filled'].values()) for ns in num_state)
tot=sum(sum(ns['expected'].values()) for ns in num_state)
print(f"pass1 filled {f1}/{tot}")

# stage2
TPL={}
def get_tpl(leg,core=False):
    k=(leg,core)
    if k not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{leg:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{leg:02d}_mask.png',0).astype(np.float32)/255
        if core:
            ys,xs=np.where(m>0); vals=t[ys,xs]; mu=vals.mean(axis=0)
            contr=np.abs(vals-mu).max(axis=1); cut=np.percentile(contr,38)
            m2=np.zeros_like(m); keep=contr>=cut; m2[ys[keep],xs[keep]]=1
            if m2.sum()>=8: m=m2
        TPL[k]=(t,m)
    return TPL[k]
def thr2(leg):
    return float(np.clip(thr_cal.get(str(leg),{}).get('thr',0.75)-0.02,0.52,0.88))
def window_peak(leg,nx,ny,core,R,exclude):
    t,m=get_tpl(leg,core); cx,cy=meta[str(leg)]['center_xy']
    WR=int(R+12)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+cx; ccy=yy+y0+cy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.5)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    def q(a,b,c):
        d=(a-2*b+c); return 0.5*(a-c)/d if abs(d)>1e-9 else 0.0
    dx=dy=0.0
    if 0<x<W-1: dx=max(-1,min(1,q(ncc[y,x-1],ncc[y,x],ncc[y,x+1])))
    if 0<y<H-1: dy=max(-1,min(1,q(ncc[y-1,x],ncc[y,x],ncc[y+1,x])))
    return (float(x+x0+cx+dx),float(y+y0+cy+dy),v)

def reliability(leg): return meta.get(str(leg),{}).get('med_ncc',0.5)
t0=time.time()
for round_no,(Rmode,use_core_first) in enumerate([(40,False),(46,True)]):
    tasks=defaultdict(list)
    for ni,ns in enumerate(num_state):
        for leg,c in ns['expected'].items():
            for _ in range(c-ns['filled'][leg]): tasks[leg].append(ni)
    if not tasks: break
    for leg in sorted(tasks.keys(),key=lambda L:-reliability(L)):
        if leg==49: continue
        th=thr2(leg) if round_no==0 else max(0.55,thr2(leg)-0.04)
        # candidate claims from existing objs
        cand=[]
        for ni in tasks[leg]:
            ns=num_state[ni]; n=ns['num']
            if ns['filled'][leg]>=ns['expected'][leg]: continue
            for oi,o in enumerate(objs):
                if o['claimed_by'] is not None or leg not in o['scores']: continue
                if np.hypot(o['cx']-n['px'],o['cy']-n['py'])<=Rmode:
                    cand.append((-o['scores'][leg][0],oi,ni,'obj',None))
        cand.sort()
        for negsc,oi,ni,kind,_ in cand:
            if objs[oi]['claimed_by'] is not None: continue
            if num_state[ni]['filled'][leg]>=num_state[ni]['expected'][leg]: continue
            claim(oi,ni,leg)
        # pixel searches: collect then claim by score
        exclude=[(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]
        pcand=[]
        for ni in tasks[leg]:
            ns=num_state[ni]; n=ns['num']
            if ns['filled'][leg]>=ns['expected'][leg]: continue
            r=window_peak(leg,n['px'],n['py'],use_core_first,Rmode,exclude)
            if r and r[2]>=th: pcand.append((-r[2],ni,r,use_core_first))
            elif not use_core_first:
                r=window_peak(leg,n['px'],n['py'],True,Rmode,exclude)
                if r and r[2]>=max(0.60,th): pcand.append((-r[2],ni,r,True))
        pcand.sort()
        for negsc,ni,r,core in pcand:
            ns=num_state[ni]
            if ns['filled'][leg]>=ns['expected'][leg]: continue
            x,y,v=r
            if any(np.hypot(x-o['cx'],y-o['cy'])<=5.5 for o in objs if o['claimed_by'] is not None): continue
            objs.append({'cx':x,'cy':y,'scores':{leg:(v,-1)},'claimed_by':None,'stage':'2core' if core else 2})
            claim(len(objs)-1,ni,leg)
    f=sum(sum(ns['filled'].values()) for ns in num_state)
    print(f"round{round_no}: filled {f}/{tot}  ({time.time()-t0:.0f}s)")
unfilled=Counter()
for ns in num_state:
    for leg,c in ns['expected'].items():
        if ns['filled'][leg]<c: unfilled[leg]+=c-ns['filled'][leg]
print("unfilled:",dict(sorted(unfilled.items())))
print("unclaimed objs:",sum(1 for o in objs if o['claimed_by'] is None)," total objs:",len(objs))
pickle.dump({'objs':objs,'num_state':num_state},open('work/min/link_stage2_v4.pkl','wb'))
