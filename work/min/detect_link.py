import cv2, numpy as np, json, pickle, sys, time
import pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import defaultdict, Counter

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
land=(cv2.imread('work/min/landmask.png',0)>0)
tab=pd.read_pickle('work/min/tables_final.pkl')
zoned=pickle.load(open('work/min/map_numbers_zoned.pkl','rb'))

CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':9,'Be':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67,'Gm':23,'Sd':25,'St':55,'Ms':44,'Mu':44,'Ks':34}
# --- fix borderline zones by table existence ---
tabkeys=set(zip(tab.zone,tab.link_num.astype(int)))
def zone_of(x,y):
    if y>=1306.9: return 'F' if x<776.5 else 'G'
    if x<776.5: return 'A' if y<826.4 else 'D'
    h2=994.6+(x-773.8)*0.00263
    if y<h2: return 'B' if x<1411.5 else 'C'
    return 'E'
fixed=0
for d in zoned:
    if d.get('border_dist',99)<=7:
        z0=d['zone']; v=int(d['value'])
        if (z0,v) not in tabkeys:
            # try zones of nearby points (perturb across lines)
            cands=set()
            for dx,dy in [(8,0),(-8,0),(0,8),(0,-8),(8,8),(-8,-8)]:
                cands.add(zone_of(d['cx']+dx,d['cy']+dy))
            for z in cands:
                if (z,v) in tabkeys:
                    d['zone']=z; d['zone_fixed']=True; fixed+=1; break
print(f"borderline zone fixes: {fixed}")
pickle.dump(zoned,open('work/min/map_numbers_zoned2.pkl','wb'))

def to_px(x,y): return ((x-74.2397)/0.959996,(y-358.724)/0.959996)
numbers=[]
for d in zoned:
    px,py=to_px(d['cx'],d['cy'])
    numbers.append({'zone':d['zone'],'value':int(d['value']),'px':px,'py':py})
# expected legs per (zone,value): merge suffix rows
expected={}
rowinfo={}
for _,r in tab.iterrows():
    key=(r.zone,int(r.link_num))
    legs=expected.setdefault(key,Counter())
    seen=set()
    for c in r.codes_list:
        L=CODE2LEG.get(c)
        if L and L not in seen: legs[L]+=1; seen.add(L)
    rowinfo.setdefault(key,[]).append({'suffix':r.link_suffix,'locality':r.locality,'codes':r.codes_list})
print(f"numbers on map: {len(numbers)}; table keys: {len(expected)}")

# --- stage1 detection, high thresholds ---
THR1={6:0.93,52:0.93,26:0.93,13:0.92,3:0.88,31:0.88,32:0.88,39:0.85,27:0.85,43:0.88,55:0.85,28:0.85,30:0.78,25:0.85,65:0.85,35:0.85,62:0.85,47:0.85,42:0.85,7:0.85,9:0.85,16:0.85,46:0.85,1:0.85,8:0.85,48:0.85,50:0.85,67:0.85,19:0.90,37:0.85,11:0.85,21:0.88,51:0.85,17:0.90,4:0.88,5:0.88,59:0.88,60:0.85,63:0.88,44:0.88,64:0.88,53:0.88,57:0.88,61:0.88,66:0.88,45:0.88,40:0.88,29:0.90,22:0.93,18:0.93,2:0.95,15:0.90,23:0.90,33:0.90,54:0.88,56:0.88,42:0.85}
def peaks_nms(ncc,thr,rad):
    ys,xs=np.where(ncc>=thr)
    if len(ys)==0: return []
    vals=ncc[ys,xs]; order=np.argsort(-vals)
    keep=[]; taken=np.zeros(ncc.shape,bool); H,W=ncc.shape
    for i in order:
        y,x=int(ys[i]),int(xs[i])
        if taken[y,x]: continue
        keep.append((x,y,float(vals[i])))
        taken[max(0,y-rad):min(H,y+rad+1),max(0,x-rad):min(W,x+rad+1)]=True
    return keep
def subpix(ncc,x,y):
    if x<=0 or y<=0 or x>=ncc.shape[1]-1 or y>=ncc.shape[0]-1: return float(x),float(y)
    def q(a,b,c):
        d=(a-2*b+c); return 0.5*(a-c)/d if abs(d)>1e-9 else 0.0
    dx=max(-1,min(1,q(ncc[y,x-1],ncc[y,x],ncc[y,x+1])))
    dy=max(-1,min(1,q(ncc[y-1,x],ncc[y,x],ncc[y+1,x])))
    return x+dx,y+dy

dets=[]
t0=time.time()
for leg in range(1,68):
    if leg==49: continue
    tpl=cv2.imread(f'work/min/selftpl/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/selftpl/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    if tpl is None or m.sum()<6: continue
    ncc=masked_ncc(base,tpl,m)
    cx,cy=meta[str(leg)]['center_xy']
    H,W=ncc.shape
    sub=land[int(round(cy)):int(round(cy))+H,int(round(cx)):int(round(cx))+W]
    if sub.shape==ncc.shape: ncc=np.where(sub,ncc,-1)
    thr=THR1.get(leg,0.90)
    rad=max(4,int(0.55*min(tpl.shape[:2])))
    for (x,y,v) in peaks_nms(ncc,thr,rad):
        sx,sy=subpix(ncc,x,y)
        dets.append({'leg':leg,'cx':float(sx+cx),'cy':float(sy+cy),'score':v,'stage':1})
print(f"stage1 dets={len(dets)} in {time.time()-t0:.0f}s")

# --- cross-leg clustering (centres within 4px) ---
dets.sort(key=lambda d:-d['score'])
objs=[]  # {cx,cy,scores:{leg:(score,detidx)}, }
grid={}
cell=6
for i,d in enumerate(dets):
    gx,gy=int(d['cx']//cell),int(d['cy']//cell)
    found=None
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for oi in grid.get((gx+dx,gy+dy),[]):
                o=objs[oi]
                if (o['cx']-d['cx'])**2+(o['cy']-d['cy'])**2<=16:
                    found=oi; break
            if found is not None: break
        if found is not None: break
    if found is None:
        objs.append({'cx':d['cx'],'cy':d['cy'],'scores':{d['leg']:(d['score'],i)},'claimed_by':None})
        grid.setdefault((gx,gy),[]).append(len(objs)-1)
    else:
        o=objs[found]
        if d['leg'] not in o['scores'] or d['score']>o['scores'][d['leg']][0]:
            o['scores'][d['leg']]=(d['score'],i)
print(f"objects after clustering: {len(objs)}")

# --- linkage pass 1: numbers claim expected legs ---
R1=32
num_state=[]
for ni,n in enumerate(numbers):
    key=(n['zone'],n['value'])
    exp=expected.get(key,Counter())
    num_state.append({'num':n,'key':key,'expected':exp,'filled':Counter(),'objs':[]})
# candidate pairs
pairs=[]
for oi,o in enumerate(objs):
    for ni,ns in enumerate(num_state):
        n=ns['num']
        dist=np.hypot(o['cx']-n['px'],o['cy']-n['py'])
        if dist<=R1:
            for leg,(sc,di) in o['scores'].items():
                if ns['expected'].get(leg,0)>0:
                    pairs.append((-sc,dist,oi,ni,leg))
pairs.sort()
for negsc,dist,oi,ni,leg in pairs:
    o=objs[oi]; ns=num_state[ni]
    if o['claimed_by'] is not None: continue
    if ns['filled'][leg]>=ns['expected'][leg]: continue
    o['claimed_by']=(ni,leg); ns['filled'][leg]+=1; ns['objs'].append((oi,leg))
filled=sum(sum(ns['filled'].values()) for ns in num_state)
total_exp=sum(sum(ns['expected'].values()) for ns in num_state)
print(f"pass1: filled {filled}/{total_exp} expected (leg,number) slots across mapped numbers")
unclaimed=[o for o in objs if o['claimed_by'] is None]
print(f"unclaimed objects: {len(unclaimed)}")
unfilled=Counter()
for ns in num_state:
    for leg,c in ns['expected'].items():
        if ns['filled'][leg]<c: unfilled[leg]+=c-ns['filled'][leg]
print("unfilled by leg:",dict(sorted(unfilled.items())))
# numbers without any table row / table rows without number
tab_only=[k for k in expected if k not in {(n['zone'],n['value']) for n in numbers}]
print(f"table keys w/o map number: {len(tab_only)}")
pickle.dump({'objs':objs,'num_state':num_state,'dets':dets},open('work/min/link_stage1.pkl','wb'))
