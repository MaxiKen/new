import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
from scipy.spatial import cKDTree
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
baseu=cv2.imread('work/min/mineral_base.png')
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
S=pickle.load(open('work/min/complete6e.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
# --- binarize soft masks for harvested templates (19,22,44,52) ---
for L in [19,22,44,52]:
    mp=f'work/min/selftpl4/leg{L:02d}_mask.png'
    m=cv2.imread(mp,0)
    soft=np.unique(m)
    cv2.imwrite(mp,((m>127)*255).astype(np.uint8))
    print(f"leg{L} mask binarized (was {len(soft)} levels)")
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
def montage_pts(selpts,path,cols=7):
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
def redetect(L,comp_legs,thr_ctx_v,thr_free_v,win_floor,collect=0.66):
    pts_local=[p for p in pts if p['leg']==L]
    t,m,bcx,bcy=tpl(L)
    # diagnostics: peaks at expecting slots
    wp=[]
    for ns in num_state:
        if ns['expected'].get(L,0)>0:
            rr=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
            if rr: wp.append(round(rr[2],3))
    print(f"leg{L} slot window peaks (binary mask):",sorted(wp,reverse=True))
    ncc=masked_ncc(base,t,m)
    ys,xs=np.nonzero(ncc>=collect)
    det=nms([((float(x+bcx),float(y+bcy)),float(ncc[y,x])) for y,x in zip(ys,xs)])
    exppts=[(ns['num']['px'],ns['num']['py']) for ns in num_state if ns['expected'].get(L,0)>0]
    tree_exp=cKDTree(np.array(exppts))
    exclude=[(p['cx'],p['cy']) for p in pts]
    added=0; rej=Counter()
    for (cx,cy),sc in det:
        de=float(tree_exp.query([cx,cy])[0]); da=float(tree_all.query([cx,cy])[0])
        tier=None
        if de<=42 and sc>=thr_ctx_v: tier='ctx'
        elif sc>=thr_free_v: tier='free'
        elif da<=34 and sc>=thr_free_v-0.05: tier='near'
        if not tier: continue
        if any((cx-a)**2+(cy-b)**2<25 for a,b in exclude): rej['supp']+=1; continue
        si=score_at(L,cx,cy)
        bo=max(score_at(K,cx,cy) for K in comp_legs)
        if tier=='ctx' and si<bo-0.02: rej['margin']+=1; continue
        if tier!='ctx' and si<bo+0.03: rej['margin']+=1; continue
        pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':tier,'match_type':'complete'})
        exclude.append((cx,cy)); added+=1
    print(f"leg{L} sweep added={added} rejected={dict(rej)}")
    relink()
    n=0
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(L,0)==0: continue
        for _ in range(ns['expected'][L]-ns['filled'][L]):
            r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,exclude)
            if r is None or r[2]<win_floor: continue
            cx,cy,sc=r
            si=score_at(L,cx,cy); bo=max(score_at(K,cx,cy) for K in comp_legs)
            if si<bo-0.02: continue
            pts.append({'leg':L,'cx':cx,'cy':cy,'score':round(sc,4),'tier':'winA','match_type':'complete','num_idx':ni})
            ns['filled'][L]+=1; exclude.append((cx,cy)); n+=1
    print(f"leg{L} window added={n}")
    relink()
# refresh self stats for harvested legs (binary masks) using current points as instances where available
for L in [19,22,44]:
    inst=[p for p in pts if p['leg']==L]
    if len(inst)>=3:
        scs=[score_at(L,p['cx'],p['cy']) for p in inst]
        C6[str(L)]['self_p5']=round(float(np.percentile(scs,5)),3)
        C6[str(L)]['self_p10']=round(float(np.percentile(scs,10)),3)
        C6[str(L)]['self_p50']=round(float(np.median(scs)),3)
        print(f"leg{L} binary-mask self stats from {len(inst)} pts: p5={C6[str(L)]['self_p5']} p50={C6[str(L)]['self_p50']}")
pts[:]=[p for p in pts if p['leg'] not in (19,22,44)]
relink()
redetect(19,[10,5,3,31,34,9],0.80,0.93,0.80)
montage_pts([p for p in pts if p['leg']==19],'work/qa/v6f_leg19.png')
redetect(22,[5,10,19,51,66,20],0.74,0.90,0.72)
montage_pts([p for p in pts if p['leg']==22],'work/qa/v6f_leg22.png')
redetect(44,[3,4,5,10,20,22,23,31,33,40,51,56,57,63,66,67],0.80,0.93,0.78)
montage_pts([p for p in pts if p['leg']==44],'work/qa/v6f_leg44.png')
# refresh stats again post-detection
for L in [19,22,44]:
    inst=[p for p in pts if p['leg']==L]
    if len(inst)>=3:
        scs=[score_at(L,p['cx'],p['cy']) for p in inst]
        C6[str(L)]['self_p5']=round(float(np.percentile(scs,5)),3)
        C6[str(L)]['self_p10']=round(float(np.percentile(scs,10)),3)
        C6[str(L)]['self_p50']=round(float(np.median(scs)),3)
        C6[str(L)]['n']=len(inst)
json.dump(C6,open('work/min/centres6.json','w'),indent=1)
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"points={len(pts)} filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6f.pkl','wb'))
