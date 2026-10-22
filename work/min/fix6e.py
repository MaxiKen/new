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
S=pickle.load(open('work/min/complete6d.pkl','rb'))
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
allnum=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree_all=cKDTree(allnum)
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
def montage_pts(selpts,path,cols=7,H29=True):
    cells=[]
    for p in selpts:
        x,y=int(round(p['cx'])),int(round(p['cy']))
        win=np.full((29,29,3),255,np.uint8)
        src=baseu[max(0,y-14):y+15,max(0,x-14):x+15]
        win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
        cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
        cv2.putText(win,f"L{p['leg']} {p['score']:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.32,(0,0,255),1)
        cells.append(cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST))
    if not cells: print(path,"empty"); return
    H=cells[0].shape[0]; W=cells[0].shape[1]; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite(path,canvas); print("saved",path,len(cells))
def build_from_legend(L,scale,peak_floor):
    lt=cv2.imread(f'work/min/templates/leg{L:02d}.png'); lm=cv2.imread(f'work/min/templates/leg{L:02d}_mask.png',0)
    t=cv2.resize(lt,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA).astype(np.float32)
    m=cv2.resize(lm,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA).astype(np.float32)/255
    ys_,xs_=np.nonzero(m>0.3); bcx=(xs_.min()+xs_.max())/2; bcy=(ys_.min()+ys_.max())/2
    slots=[ns for ns in num_state if ns['expected'].get(L,0)>0]
    pk=[]
    for ns in slots:
        r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
        if r: pk.append((r[2],r[0],r[1],ns))
    good=[p for p in pk if p[0]>=peak_floor]
    print(f"build leg{L}: instances>={peak_floor}: {len(good)}/{len(pk)}")
    if len(good)<3: return None
    th,tw=t.shape[:2]; patches=[]; cents=[]; inst=[]
    for v,cx,cy,ns in good:
        px0=int(round(cx-bcx)); py0=int(round(cy-bcy))
        if px0<0 or py0<0 or px0+tw>BW or py0+th>BH: continue
        patches.append(base[py0:py0+th,px0:px0+tw]); inst.append((cx,cy,v))
        g=gray[py0:py0+th,px0:px0+tw]; ink=(g<200)&(m>0.3)
        if ink.sum()>=3:
            yy2,xx2=np.nonzero(ink); cents.append(((xx2.min()+xx2.max())/2,(yy2.min()+yy2.max())/2))
    if len(patches)<3: return None
    newt=np.median(np.stack(patches),axis=0)
    ncx=float(np.median([c[0] for c in cents])); ncy=float(np.median([c[1] for c in cents]))
    cv2.imwrite(f'work/min/selftpl4/leg{L:02d}.png',np.clip(newt,0,255).astype(np.uint8))
    cv2.imwrite(f'work/min/selftpl4/leg{L:02d}_mask.png',(m*255).astype(np.uint8))
    TPL.pop(L,None)
    # self stats
    scs=[]
    for cx,cy,v in inst:
        WR=20
        x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
        win=base[y0:y1,x0:x1]
        ncc=masked_ncc(win,newt.astype(np.float32),m)
        H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
        scs.append(float(np.where(np.hypot(xx+x0+ncx-cx,yy+y0+ncy-cy)<=1.6,ncc,-1).max()))
    p10=float(np.percentile(scs,10)); p50=float(np.median(scs))
    C6[str(L)]={"center_xy":[round(ncx,2),round(ncy,2)],"self_p5":round(p10,3),"self_p10":round(p10,3),
                "self_p50":round(p50,3),"n":len(patches),"src":f"harvest6e-s{scale}"}
    json.dump(C6,open('work/min/centres6.json','w'),indent=1)
    montage_pts([{'leg':L,'cx':cx,'cy':cy,'score':v} for cx,cy,v in inst],f'work/qa/v6e_inst{L}.png')
    print(f"leg{L} template built centre=({ncx:.1f},{ncy:.1f}) p10={p10:.3f} p50={p50:.3f} n={len(patches)}")
    return p10,p50
def redetect(L,comp_legs,thr_ctx_v,thr_free_v):
    t,m,bcx,bcy=tpl(L)
    ncc=masked_ncc(base,t,m)
    ys,xs=np.nonzero(ncc>=0.68)
    det=nms([((float(x+bcx),float(y+bcy)),float(ncc[y,x])) for y,x in zip(ys,xs)])
    exppts=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(L,0)>0]
    tree_exp=cKDTree(np.array(exppts))
    exclude=[(p['cx'],p['cy']) for p in pts]
    added=0
    for (cx,cy),sc in det:
        de=float(tree_exp.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
        tier=None
        if de<=42 and sc>=thr_ctx_v: tier='ctx'
        elif sc>=thr_free_v: tier='free'
        elif da<=34 and sc>=thr_free_v-0.05: tier='near'
        if not tier: continue
        if any((cx-a)**2+(cy-b)**2<25 for a,b in exclude): continue
        si=score_at(L,cx,cy)
        bo=max(score_at(K,cx,cy) for K in comp_legs)
        if tier=='ctx' and si<bo-0.02: continue
        if tier!='ctx' and si<bo+0.03: continue
        pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':tier,'match_type':'complete'})
        exclude.append((cx,cy)); added+=1
    print(f"leg{L} sweep added={added}")
    relink()
    n=0
    t,m,bcx,bcy=tpl(L)
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(L,0)==0: continue
        for _ in range(ns['expected'][L]-ns['filled'][L]):
            r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,exclude)
            if r is None or r[2]<thr_ctx_v-0.05: continue
            cx,cy,sc=r
            si=score_at(L,cx,cy); bo=max(score_at(K,cx,cy) for K in comp_legs)
            if si<bo-0.02: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'winA','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; exclude.append((cx,cy)); n+=1
    print(f"leg{L} window added={n}")
    relink()
# leg19
r=build_from_legend(19,0.95,0.68)
if r:
    p10,p50=r
    pts[:]=[p for p in pts if p['leg']!=19]
    t_,m_,bx_,by_=tpl(19)
    wp=[]
    for ns in num_state:
        if ns['expected'].get(19,0)>0:
            rr=window_peak_tpl(t_,m_,bx_,by_,ns['num']['px'],ns['num']['py'],42,[])
            if rr: wp.append(round(rr[2],3))
    print("leg19 new-tpl E-slot window peaks:",sorted(wp,reverse=True))
    redetect(19,[10,5,3,31,34,9],0.80,0.95)
    montage_pts([p for p in pts if p['leg']==19],'work/qa/v6e_leg19.png')
# leg22
r=build_from_legend(22,0.95,0.65)
if r:
    p10,p50=r
    pts[:]=[p for p in pts if p['leg']!=22]
    t_,m_,bx_,by_=tpl(22)
    wp=[]
    for ns in num_state:
        if ns['expected'].get(22,0)>0:
            rr=window_peak_tpl(t_,m_,bx_,by_,ns['num']['px'],ns['num']['py'],42,[])
            if rr: wp.append(round(rr[2],3))
    print("leg22 new-tpl F-slot window peaks:",sorted(wp,reverse=True))
    redetect(22,[5,10,19,51,66,20],0.75,0.92)
    montage_pts([p for p in pts if p['leg']==22],'work/qa/v6e_leg22.png')
# leg52: drop all + diag montage for visual hunt
pts[:]=[p for p in pts if p['leg']!=52]
print("leg52 points dropped (pending visual hunt)")
relink()
lt=cv2.imread('work/min/templates/leg52.png'); lm=cv2.imread('work/min/templates/leg52_mask.png',0)
t=cv2.resize(lt,None,fx=0.75,fy=0.75,interpolation=cv2.INTER_AREA).astype(np.float32)
m=cv2.resize(lm,None,fx=0.75,fy=0.75,interpolation=cv2.INTER_AREA).astype(np.float32)/255
ys_,xs_=np.nonzero(m>0.3); bcx=(xs_.min()+xs_.max())/2; bcy=(ys_.min()+ys_.max())/2
pk52=[]
for ns in num_state:
    if ns['expected'].get(52,0)>0:
        r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
        if r: pk52.append((r[2],r[0],r[1],ns))
pk52.sort(key=lambda p:-p[0])
print("leg52 top peaks:",[round(p[0],3) for p in pk52[:8]])
cells=[]
for v,cx,cy,ns in pk52[:10]:
    x,y=int(round(ns['num']['px'])),int(round(ns['num']['py']))
    win=np.full((61,61,3),255,np.uint8)
    src=baseu[max(0,y-30):y+31,max(0,x-30):x+31]
    win[30-(y-max(0,y-30)):30-(y-max(0,y-30))+src.shape[0],30-(x-max(0,x-30)):30-(x-max(0,x-30))+src.shape[1]]=src
    cv2.drawMarker(win,(30,30),(255,0,0),cv2.MARKER_CROSS,9,1)
    cv2.drawMarker(win,(int(round(cx-x))+30,int(round(cy-y))+30),(0,0,255),cv2.MARKER_TILTED_CROSS,7,1)
    cv2.putText(win,f"Q {ns['num']['zone']}{ns['num']['value']} pk{v:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.3,(0,0,255),1)
    cells.append(cv2.resize(win,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
H=cells[0].shape[0]; W=cells[0].shape[1]; cols=5; rows=(len(cells)+cols-1)//cols
canvas=np.full((H*rows,W*cols,3),255,np.uint8)
for i,c in enumerate(cells):
    r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
cv2.imwrite('work/qa/v6e_diag52.png',canvas); print("saved diag52")
# bowl cluster pass (14 & 58)
exclude=[(p['cx'],p['cy']) for p in pts]
SIB={14:58,58:14}
addb=0; shared=Counter()
for L in (14,58):
    t,m,bcx,bcy=tpl(L)
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(L,0)==0: continue
        for _ in range(ns['expected'][L]-ns['filled'][L]):
            r0=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
            if r0 and r0[2]>=0.85:
                dmin=min((np.hypot(r0[0]-p['cx'],r0[1]-p['cy']) for p in pts if p['leg']==L),default=999)
                if dmin<=8: shared[L]+=1; continue
            r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,exclude,excl_r=6.0)
            if r is None or r[2]<0.85: continue
            cx,cy,sc=r
            si=score_at(L,cx,cy); ss=score_at(SIB[L],cx,cy)
            if si<ss+0.03: continue
            bo=max(score_at(K,cx,cy) for K in LEGS if K not in (L,SIB[L]))
            if si<bo-0.02: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'winD','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; exclude.append((cx,cy)); addb+=1
print("bowl cluster pass added:",addb," paper-shared slots:",dict(shared))
relink()
# leg44 low-peak diag montage (no adds)
t44,m44,bx44,by44=tpl(44)
pk44=[]
for ns in num_state:
    if ns['expected'].get(44,0)>0 and ns['filled'][44]<ns['expected'][44]:
        r=window_peak_tpl(t44,m44,bx44,by44,ns['num']['px'],ns['num']['py'],42,[])
        if r: pk44.append((r[2],r[0],r[1],ns))
pk44.sort(key=lambda p:-p[0])
print("leg44 unfilled peaks:",[round(p[0],2) for p in pk44])
cells=[]
for v,cx,cy,ns in pk44[:10]:
    x,y=int(round(ns['num']['px'])),int(round(ns['num']['py']))
    win=np.full((61,61,3),255,np.uint8)
    src=baseu[max(0,y-30):y+31,max(0,x-30):x+31]
    win[30-(y-max(0,y-30)):30-(y-max(0,y-30))+src.shape[0],30-(x-max(0,x-30)):30-(x-max(0,x-30))+src.shape[1]]=src
    cv2.drawMarker(win,(30,30),(255,0,0),cv2.MARKER_CROSS,9,1)
    cv2.drawMarker(win,(int(round(cx-x))+30,int(round(cy-y))+30),(0,0,255),cv2.MARKER_TILTED_CROSS,7,1)
    cv2.putText(win,f"M {ns['num']['zone']}{ns['num']['value']} pk{v:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.3,(0,0,255),1)
    cells.append(cv2.resize(win,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
if cells:
    H=cells[0].shape[0]; W=cells[0].shape[1]; cols=5; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite('work/qa/v6e_diag44.png',canvas); print("saved diag44")
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6e.pkl','wb'))
