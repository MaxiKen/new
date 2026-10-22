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
Bc,Gc,Rc=baseu[:,:,0].astype(int),baseu[:,:,1].astype(int),baseu[:,:,2].astype(int)
orangeF=((Bc<140)&(Gc>60)&(Gc<175)&(Rc>140)&((Rc-Bc)>50)).astype(np.uint8)
# find orange blobs near F numbers
inst=[]
for ns in num_state:
    if ns['expected'].get(22,0)==0: continue
    nx,ny=ns['num']['px'],ns['num']['py']
    x0,y0=int(max(0,nx-50)),int(max(0,ny-50)); x1,y1=int(min(BW,nx+50)),int(min(BH,ny+50))
    sub=cv2.dilate(orangeF[y0:y1,x0:x1],np.ones((3,3),np.uint8))
    n,lab,stats,cent=cv2.connectedComponentsWithStats(sub,8)
    cands=[]
    for i in range(1,n):
        X,Y,W,H,A=stats[i]
        if 8<=W<=18 and 8<=H<=18 and 30<=A<=260:
            cx,cy=x0+cent[i][0],y0+cent[i][1]
            dist=np.hypot(cx-nx,cy-ny)
            if dist<=42: cands.append((dist,cx,cy,W,H,A))
    cands.sort()
    print(f"F {ns['num']['zone']}{ns['num']['value']}: orange blobs {[(round(c[0],1),c[3],c[4],c[5]) for c in cands]}")
    if cands: inst.append((cands[0][1],cands[0][2],ns))
print("blob instances:",len(inst))
if len(inst)>=3:
    FS=15; patches=[]; cents=[]
    lm=cv2.imread('work/min/templates/leg22_mask.png',0)
    m15=cv2.resize(lm,(FS,FS),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    for cx,cy,ns in inst:
        px0=int(round(cx-FS/2)); py0=int(round(cy-FS/2))
        if px0<0 or py0<0 or px0+FS>BW or py0+FS>BH: continue
        patches.append(base[py0:py0+FS,px0:px0+FS])
        g=gray[py0:py0+FS,px0:px0+FS]; ink=(g<210)&(m15>0.3)
        if ink.sum()>=3:
            yy2,xx2=np.nonzero(ink); cents.append(((xx2.min()+xx2.max())/2,(yy2.min()+yy2.max())/2))
    newt=np.median(np.stack(patches),axis=0)
    ncx=float(np.median([c[0] for c in cents])); ncy=float(np.median([c[1] for c in cents]))
    cv2.imwrite('work/min/selftpl4/leg22.png',np.clip(newt,0,255).astype(np.uint8))
    cv2.imwrite('work/min/selftpl4/leg22_mask.png',((m15>0.5)*255).astype(np.uint8))
    C6['22']={"center_xy":[round(ncx,2),round(ncy,2)],"self_p5":0.7,"self_p10":0.72,"self_p50":0.8,"n":len(patches),"src":"harvest6i-blob"}
    json.dump(C6,open('work/min/centres6.json','w'),indent=1)
    print(f"leg22 blob template built centre=({ncx:.1f},{ncy:.1f}) n={len(patches)}")
    # instance montage
    cells=[]
    for cx,cy,ns in inst:
        x,y=int(round(cx)),int(round(cy))
        big=cv2.resize(baseu[max(0,y-10):y+11,max(0,x-10):x+11],None,fx=9,fy=9,interpolation=cv2.INTER_NEAREST)
        cv2.putText(big,f"F{ns['num']['zone']}{ns['num']['value']}",(4,18),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,0,255),2)
        cells.append(big)
    H=cells[0].shape[0]; W=cells[0].shape[1]
    canvas=np.full((H,W*len(cells),3),255,np.uint8)
    for i,c in enumerate(cells): canvas[:,i*W:(i+1)*W]=c
    cv2.imwrite('work/qa/v6i_inst22.png',canvas); print("saved inst22")
# scoring infra
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
if len(inst)>=3:
    t22,m22,bx22,by22=tpl(22)
    wp=[]
    for ns in num_state:
        if ns['expected'].get(22,0)>0:
            rr=window_peak_tpl(t22,m22,bx22,by22,ns['num']['px'],ns['num']['py'],42,[])
            if rr: wp.append(round(rr[2],3))
    print("leg22 blob-tpl F-slot peaks:",sorted(wp,reverse=True))
    confusable={5,10,19,20,51,66}; comp_legs=[5,10,19,51,66,20]
    ncc=masked_ncc(base,t22,m22)
    ys,xs=np.nonzero(ncc>=0.64)
    det=nms([((float(x+bx22),float(y+by22)),float(ncc[y,x])) for y,x in zip(ys,xs)])
    exppts=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(22,0)>0]
    tree_exp=cKDTree(np.array(exppts))
    stats=Counter()
    def try_place(cx,cy,sc,tier):
        x,y=int(round(cx)),int(round(cy))
        if int(orangeF[max(0,y-4):y+5,max(0,x-4):x+5].sum())<10: stats['colour']+=1; return False
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
    for (cx,cy),sc in det:
        de=float(tree_exp.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
        tier=None
        if de<=42 and sc>=0.72: tier='ctx'
        elif sc>=0.88: tier='free'
        elif da<=34 and sc>=0.83: tier='near'
        if tier: try_place(cx,cy,sc,tier)
    relink()
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(22,0)==0: continue
        for _ in range(ns['expected'][22]-ns['filled'][22]):
            r=window_peak_tpl(t22,m22,bx22,by22,ns['num']['px'],ns['num']['py'],42,[])
            if r is None or r[2]<0.70: continue
            if try_place(r[0],r[1],r[2],'ctx'): relink()
    print("leg22 redetect:",dict(stats))
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
        cv2.imwrite('work/qa/v6i_leg22.png',canvas); print("saved v6i_leg22",len(cells))
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
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6i.pkl','wb'))
