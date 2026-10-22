import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
baseu=cv2.imread('work/min/mineral_base.png')
gray=cv2.cvtColor(baseu,cv2.COLOR_BGR2GRAY)
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
S=pickle.load(open('work/min/complete6h.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
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
def window_peak_tpl(t,m,bcx,bcy,nx,ny,R,exclude,excl_r=5.0):
    WR=int(R+14)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+bcx; ccy=yy+y0+bcy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>excl_r)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return float(x+x0+bcx),float(y+y0+bcy),v
def nms(det,r=4.0):
    det=sorted(det,key=lambda d:-d[1]); kp=[]
    for (cx,cy),sc in det:
        if all((cx-a)**2+(cy-b)**2>r*r for (a,b),_ in kp): kp.append(((cx,cy),sc))
    return kp
# --- (a) B/E re-arbitration on existing leg10/leg19 points ---
flips=0
for p in pts:
    if p['leg'] in (10,19):
        s10=score_at(10,p['cx'],p['cy']); s19=score_at(19,p['cx'],p['cy'])
        cur=s10 if p['leg']==10 else s19
        alt=s19 if p['leg']==10 else s10
        if alt>cur+0.02:
            p['leg']=19 if p['leg']==10 else 10; p['score']=round(alt,4); flips+=1
print("B/E flips:",flips)
# --- (b) leg22 from the 3 census discs ---
Bc,Gc,Rc=baseu[:,:,0].astype(int),baseu[:,:,1].astype(int),baseu[:,:,2].astype(int)
orangeT=((Bc<90)&(Gc>80)&(Gc<160)&(Rc>180)&((Rc-Bc)>110)).astype(np.uint8)
seeds=[(1579,944),(1109,1023),(1098,1028)]
FS=15
lm=cv2.imread('work/min/templates/leg22_mask.png',0)
m15=(cv2.resize(lm,(FS,FS),interpolation=cv2.INTER_AREA)>127).astype(np.float32)
patches=[]
for cx,cy in seeds:
    px0=int(round(cx-FS/2)); py0=int(round(cy-FS/2))
    patches.append(base[py0:py0+FS,px0:px0+FS])
newt=np.median(np.stack(patches),axis=0)
cv2.imwrite('work/min/selftpl4/leg22.png',np.clip(newt,0,255).astype(np.uint8))
cv2.imwrite('work/min/selftpl4/leg22_mask.png',(m15*255).astype(np.uint8))
C6['22']={"center_xy":[7.0,7.0],"self_p5":0.7,"self_p10":0.72,"self_p50":0.8,"n":3,"src":"census6j"}
json.dump(C6,open('work/min/centres6.json','w'),indent=1)
TPL.pop(22,None)
t22,m22,bx22,by22=tpl(22)
for cx,cy in seeds:
    print(f"seed ({cx},{cy}) s22={score_at(22,cx,cy):.3f}")
wp=[]
for ns in num_state:
    if ns['expected'].get(22,0)>0:
        rr=window_peak_tpl(t22,m22,bx22,by22,ns['num']['px'],ns['num']['py'],42,[])
        if rr: wp.append((ns['num']['zone']+str(ns['num']['value']),round(rr[2],3)))
print("leg22 census-tpl F-slot peaks:",sorted(wp,key=lambda w:-w[1]))
integ=cv2.integral(orangeT)
def orange11(cx,cy):
    x,y=int(round(cx)),int(round(cy))
    x0,y0=max(0,x-5),max(0,y-5); x1,y1=min(BW,x+6),min(BH,y+6)
    return int(integ[y1,x1]-integ[y0,x1]-integ[y1,x0]+integ[y0,x0])
allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
confusable={5,10,19,20,51,66}; comp_legs=[5,10,19,51,66,20]
stats=Counter()
def try_place(cx,cy,sc,tier,minorange=40):
    if orange11(cx,cy)<minorange: stats['colour']+=1; return False
    si=score_at(22,cx,cy)
    bo=max(score_at(K,cx,cy) for K in comp_legs)
    near=[p for p in pts if (p['cx']-cx)**2+(p['cy']-cy)**2<49]
    near.sort(key=lambda p:(p['cx']-cx)**2+(p['cy']-cy)**2)
    if not near:
        if tier=='ctx' and si<bo-0.02: stats['margin']+=1; return False
        if tier!='ctx' and si<bo+0.03: stats['margin']+=1; return False
        pts.append({'leg':22,'cx':cx,'cy':cy,'score':round(sc,4),'tier':tier,'match_type':'complete'})
        stats['added']+=1; return True
    p0=near[0]; dist=float(np.hypot(p0['cx']-cx,p0['cy']-cy))
    if p0['leg']==22: stats['dup']+=1; return False
    if p0['leg'] in confusable:
        so=score_at(p0['leg'],cx,cy)
        if si>so+0.03:
            p0['leg']=22; p0['cx']=cx; p0['cy']=cy; p0['score']=round(sc,4); p0['tier']=tier+'-relab'
            stats['relab']+=1; return True
        stats['lost-arb']+=1; return False
    if dist>=5.0 and tier=='ctx' and si>=bo-0.02:
        pts.append({'leg':22,'cx':cx,'cy':cy,'score':round(sc,4),'tier':tier,'match_type':'complete'})
        stats['pair-added']+=1; return True
    stats['supp']+=1; return False
pts[:]=[p for p in pts if p['leg']!=22]
exppts=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(22,0)>0]
tree_exp=cKDTree(np.array(exppts))
ncc=masked_ncc(base,t22,m22)
ys,xs=np.nonzero(ncc>=0.62)
det=nms([((float(x+bx22),float(y+by22)),float(ncc[y,x])) for y,x in zip(ys,xs)])
for (cx,cy),sc in det:
    de=float(tree_exp.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
    tier=None
    if de<=42 and sc>=0.70: tier='ctx'
    elif sc>=0.85: tier='free'
    elif da<=34 and sc>=0.80: tier='near'
    if tier: try_place(cx,cy,sc,tier)
relink()
for ni,ns in enumerate(num_state):
    if ns['expected'].get(22,0)==0: continue
    for _ in range(ns['expected'][22]-ns['filled'][22]):
        r=window_peak_tpl(t22,m22,bx22,by22,ns['num']['px'],ns['num']['py'],42,[])
        if r is None or r[2]<0.68: continue
        if try_place(r[0],r[1],r[2],'ctx',minorange=25): relink()
print("leg22 census redetect:",dict(stats))
inst2=[p for p in pts if p['leg']==22]
if len(inst2)>=3:
    scs=[score_at(22,p['cx'],p['cy']) for p in inst2]
    C6['22']['self_p5']=round(float(np.percentile(scs,5)),3)
    C6['22']['self_p10']=round(float(np.percentile(scs,10)),3)
    C6['22']['self_p50']=round(float(np.median(scs)),3)
    C6['22']['n']=len(inst2)
    json.dump(C6,open('work/min/centres6.json','w'),indent=1)
cells=[]
for p in inst2:
    x,y=int(round(p['cx'])),int(round(p['cy']))
    win=np.full((29,29,3),255,np.uint8)
    src=baseu[max(0,y-14):y+15,max(0,x-14):x+15]
    win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
    cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
    cv2.putText(win,f"L22 {p['score']:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.32,(0,0,255),1)
    cells.append(cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST))
if cells:
    H=cells[0].shape[0]; W=cells[0].shape[1]; rows=(len(cells)+6)//7
    canvas=np.full((H*rows,W*7,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,7); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite('work/qa/v6j_leg22.png',canvas); print("saved v6j_leg22",len(cells))
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
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6j.pkl','wb'))
