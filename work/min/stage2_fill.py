import cv2, numpy as np, json, pickle, sys, time
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter, defaultdict

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
thr_cal=json.load(open('work/min/thresholds.json'))
S=pickle.load(open('work/min/link_stage1.pkl','rb'))
objs,num_state=S['objs'],S['num_state']

TPL={}
def get_tpl(leg,core=False):
    k=(leg,core)
    if k not in TPL:
        t=cv2.imread(f'work/min/selftpl/leg{leg:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl/leg{leg:02d}_mask.png',0).astype(np.float32)/255
        if core:
            # top-contrast 62% of mask pixels
            ys,xs=np.where(m>0)
            vals=t[ys,xs]
            mu=vals.mean(axis=0)
            contr=np.abs(vals-mu).max(axis=1)
            cut=np.percentile(contr,38)
            m2=np.zeros_like(m)
            keep=contr>=cut
            m2[ys[keep],xs[keep]]=1
            if m2.sum()>=8: m=m2
        TPL[k]=(t,m)
    return TPL[k]

def thr2(leg):
    base_t=thr_cal.get(str(leg),{}).get('thr',0.75)
    return float(np.clip(base_t-0.02,0.52,0.88))

claimed_centres=[(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]
def refresh_claimed():
    return [(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]

def window_search(leg,nx,ny,core,thr,R=34,exclude=None):
    t,m=get_tpl(leg,core)
    cx,cy=meta[str(leg)]['center_xy']
    WR=44
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR))
    x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape
    yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+cx; ccy=yy+y0+cy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    if exclude:
        for (ex,ey) in exclude:
            valid &= (np.hypot(ccx-ex,ccy-ey)>5.5)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i])
    if v<thr: return None
    y,x=np.unravel_index(i,ncc.shape)
    # subpixel
    def q(a,b,c):
        d=(a-2*b+c); return 0.5*(a-c)/d if abs(d)>1e-9 else 0.0
    dx=dy=0.0
    if 0<x<W-1: dx=max(-1,min(1,q(ncc[y,x-1],ncc[y,x],ncc[y,x+1])))
    if 0<y<H-1: dy=max(-1,min(1,q(ncc[y-1,x],ncc[y,x],ncc[y+1,x])))
    return (float(x+x0+cx+dx),float(y+y0+cy+dy),v)

# tasks grouped by leg, legs ordered by template reliability (med_ncc desc)
def reliability(leg):
    return meta.get(str(leg),{}).get('med_ncc',0.5)
tasks=defaultdict(list)
for ni,ns in enumerate(num_state):
    for leg,c in ns['expected'].items():
        for _ in range(c-ns['filled'][leg]):
            tasks[leg].append(ni)
print("stage2 tasks:",sum(len(v) for v in tasks.values()))
t0=time.time(); filled2=0
for leg in sorted(tasks.keys(),key=lambda L:-reliability(L)):
    if leg==49: continue
    th=thr2(leg)
    for ni in tasks[leg]:
        ns=num_state[ni]; n=ns['num']
        if ns['filled'][leg]>=ns['expected'][leg]: continue
        # 1) existing unclaimed object with this leg within 38px?
        best=None
        for oi,o in enumerate(objs):
            if o['claimed_by'] is not None: continue
            if leg not in o['scores']: continue
            dist=np.hypot(o['cx']-n['px'],o['cy']-n['py'])
            if dist<=38:
                sc=o['scores'][leg][0]
                if best is None or sc>best[0]: best=(sc,oi)
        if best:
            oi=best[1]; objs[oi]['claimed_by']=(ni,leg); ns['filled'][leg]+=1; ns['objs'].append((oi,leg)); filled2+=1; continue
        exclude=refresh_claimed()
        r=window_search(leg,n['px'],n['py'],False,th,exclude=exclude)
        stage=2
        if r is None:
            r=window_search(leg,n['px'],n['py'],True,max(0.60,th),exclude=exclude)
            stage='2core'
        if r is None: continue
        x,y,v=r
        objs.append({'cx':x,'cy':y,'scores':{leg:(v,-1)},'claimed_by':(ni,leg),'stage':stage})
        ns['filled'][leg]+=1; ns['objs'].append((len(objs)-1,leg)); filled2+=1
    print(f"leg{leg:02d} done ({time.time()-t0:.0f}s) filled2_total={filled2}")
filled=sum(sum(ns['filled'].values()) for ns in num_state)
total_exp=sum(sum(ns['expected'].values()) for ns in num_state)
print(f"after stage2: filled {filled}/{total_exp}")
unfilled=Counter()
for ns in num_state:
    for leg,c in ns['expected'].items():
        if ns['filled'][leg]<c: unfilled[leg]+=c-ns['filled'][leg]
print("still unfilled:",dict(sorted(unfilled.items())))
print("unclaimed objects:",sum(1 for o in objs if o['claimed_by'] is None))
pickle.dump({'objs':objs,'num_state':num_state},open('work/min/link_stage2.pkl','wb'))
