import cv2, numpy as np, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
S=pickle.load(open('work/min/complete_v5.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
# strip leg32; restore the two relabelled points to 31
restored={(794,1350),(66,1122)}
newpts=[]
for p in pts:
    if p['leg']==32:
        if (int(p['cx']),int(p['cy'])) in restored:
            p=dict(p); p['leg']=31; newpts.append(p)
        continue
    newpts.append(p)
pts=newpts
print("after strip:",len(pts),"leg31:",sum(1 for p in pts if p['leg']==31))
def relink(pts):
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
relink(pts)
# window-add glyphs at P numbers using the shared (leg31) glyph template
t31=cv2.imread('work/min/selftpl4/leg31.png').astype(np.float32)
m31=cv2.imread('work/min/selftpl4/leg31_mask.png',0).astype(np.float32)/255
ys,xs=np.where(m31>0); bcx,bcy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
def window_peak31(nx,ny,R,exclude):
    WR=int(R+14)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    ncc=masked_ncc(win,t31,m31)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+bcx; ccy=yy+y0+bcy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.0)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return float(x+x0+bcx),float(y+y0+bcy),v
exclude=[(p['cx'],p['cy']) for p in pts]
for ni,ns in enumerate(num_state):
    if ns['expected'].get(32,0)==0: continue
    r=window_peak31(ns['num']['px'],ns['num']['py'],40,exclude)
    print(ns['key'],"shared-glyph peak:",None if r is None else round(r[2],3), "" if r is None else (round(r[0]),round(r[1])))
    if r and r[2]>=0.90:
        pts.append({'leg':32,'cx':r[0],'cy':r[1],'score':round(r[2],4),'tier':'ctx','match_type':'complete'})
        exclude.append((r[0],r[1]))
relink(pts)
# orphan 31 points near P-only numbers -> 32
for ni,ns in enumerate(num_state):
    if ns['expected'].get(32,0)>0 and ns['expected'].get(31,0)==0 and ns['filled'][32]<ns['expected'][32]:
        for p in pts:
            if p['leg']==31 and 'num_idx' not in p and np.hypot(p['cx']-ns['num']['px'],p['cy']-ns['num']['py'])<=40:
                p['leg']=32; print("orphan 31->32 at",ns['key'],(round(p['cx']),round(p['cy']))); break
relink(pts)
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
pfil=sum(ns['filled'][32] for ns in num_state)
print(f"COMPLETE v6 points={len(pts)} filled={fil}/{tot}  P slots filled={pfil}/13")
print("leg32 points:",sum(1 for p in pts if p['leg']==32)," leg31:",sum(1 for p in pts if p['leg']==31))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete_v6.pkl','wb'))
