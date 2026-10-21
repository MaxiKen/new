import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
S=pickle.load(open('work/min/link_stage2_v4.pkl','rb'))
objs,num_state=S['objs'],S['num_state']
def half_masks(leg):
    t=cv2.imread(f'work/min/selftpl4/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/selftpl4/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    ys,xs=np.where(m>0)
    if len(ys)<16: return t,[]
    ym=(ys.min()+ys.max())/2; xm=(xs.min()+xs.max())/2
    outs=[]
    for name,cond in [('top',np.mgrid[0:m.shape[0],0:m.shape[1]][0]<=ym),('bot',np.mgrid[0:m.shape[0],0:m.shape[1]][0]>=ym),('left',np.mgrid[0:m.shape[0],0:m.shape[1]][1]<=xm),('right',np.mgrid[0:m.shape[0],0:m.shape[1]][1]>=xm)]:
        mm=m*cond
        if mm.sum()>=10: outs.append((name,mm))
    return t,outs
def peak_with(t,m,cx0,cy0,nx,ny,R,exclude):
    WR=int(R+13)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+cx0; ccy=yy+y0+cy0
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.5)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return (float(x+x0+cx0),float(y+y0+cy0),v)
exclude=[(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]
cand=[]
for ni,ns in enumerate(num_state):
    for leg,c in ns['expected'].items():
        if leg==49: continue
        for _ in range(c-ns['filled'][leg]):
            t,halves=half_masks(leg)
            cx0,cy0=meta[str(leg)]['center_xy']
            best=None
            for name,mm in halves:
                r=peak_with(t,mm,cx0,cy0,ns['num']['px'],ns['num']['py'],40,exclude)
                if r and (best is None or r[2]>best[2]): best=r
            if best and best[2]>=0.62: cand.append((-best[2],ni,leg,best))
cand.sort()
added=0
for negsc,ni,leg,r in cand:
    ns=num_state[ni]
    if ns['filled'][leg]>=ns['expected'][leg]: continue
    x,y,v=r
    if any(np.hypot(x-o['cx'],y-o['cy'])<=5.5 for o in objs if o['claimed_by'] is not None): continue
    objs.append({'cx':x,'cy':y,'scores':{leg:(v,-1)},'claimed_by':(ni,leg),'stage':'2partial'})
    ns['filled'][leg]+=1; ns['objs'].append((len(objs)-1,leg)); added+=1
f=sum(sum(ns['filled'].values()) for ns in num_state); tot=sum(sum(ns['expected'].values()) for ns in num_state)
print(f"partial added {added}; filled {f}/{tot}")
unf=Counter()
for ns in num_state:
    for leg,c in ns['expected'].items():
        if ns['filled'][leg]<c: unf[leg]+=c-ns['filled'][leg]
print("unfilled:",dict(sorted(unf.items())))
pickle.dump({'objs':objs,'num_state':num_state},open('work/min/link_stage2b.pkl','wb'))
