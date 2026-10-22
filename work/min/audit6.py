import cv2, numpy as np, json, pickle, sys, random
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter, defaultdict
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
baseu=cv2.imread('work/min/mineral_base.png')
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
S=pickle.load(open('work/min/complete6k.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
# merge kept partials
part=pickle.load(open('work/min/partial6_cands.pkl','rb'))
KEEP={0,1,2,3,4,7}
for i,a in enumerate(part):
    if i in KEEP:
        pts.append({'leg':a['leg'],'cx':a['cx'],'cy':a['cy'],'score':a['score'],'tier':a['tier'],
                    'match_type':'partial','num_idx':a['num_idx'],'vis_part':0.5,'half':a['half']})
print("merged partials:",len(KEEP),"total pts:",len(pts))
# relink
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
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"filled={fil}/{tot}")
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6L.pkl','wb'))
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        TPL[L]=(t,m,*C6[str(L)]['center_xy'])
    return TPL[L]
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
# classify unfilled slots
by_leg_pts=defaultdict(list)
for p in pts: by_leg_pts[p['leg']].append(p)
allpos=[(p['cx'],p['cy']) for p in pts]
cls=Counter(); missed_by_leg=Counter(); missed_examples=defaultdict(list)
for ni,ns in enumerate(num_state):
    for L,c in ns['expected'].items():
        for _ in range(c-ns['filled'][L]):
            if L in (32,49,62): cls['skip']+=1; continue
            t,m,bcx,bcy=tpl(L)
            r0=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
            if r0 is None: cls['nowin']+=1; continue
            cx,cy,v=r0
            dsame=min((np.hypot(cx-p['cx'],cy-p['cy']) for p in by_leg_pts[L]),default=999)
            dall=min((np.hypot(cx-a,cy-b) for a,b in allpos),default=999)
            if v>=0.85 and dsame<=8: cls['shared-sameleg']+=1
            elif v>=0.85 and dall<=7: cls['peak-on-otherpt']+=1
            elif v>=0.85:
                cls['MISSED']+=1; missed_by_leg[L]+=1
                missed_examples[L].append((v,ni))
            elif v>=0.70: cls['weak-peak 0.70-0.85']+=1
            else: cls['no-peak<0.70']+=1
print("unfilled-slot classification:",dict(cls))
print("MISSED by leg:",dict(sorted(missed_by_leg.items(),key=lambda kv:-kv[1])))
for L,ex in sorted(missed_examples.items()):
    exs=sorted(ex,reverse=True)[:4]
    print(f" leg{L} missed examples:",[(num_state[ni]['num']['zone']+str(num_state[ni]['num']['value']),round(v,3)) for v,ni in exs])
# ------- montages -------
def cell29(p,label):
    x,y=int(round(p['cx'])),int(round(p['cy']))
    win=np.full((29,29,3),255,np.uint8)
    src=baseu[max(0,y-14):y+15,max(0,x-14):x+15]
    win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
    cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
    big=cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST)
    cv2.putText(big,label,(2,14),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    return big
def sheet(cells,path,cols):
    if not cells: print(path,"empty"); return
    H=cells[0].shape[0]; W=cells[0].shape[1]; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite(path,canvas); print("saved",path,len(cells))
sus=[]
for L in [7,53,17,30]:
    for p in by_leg_pts.get(L,[]):
        sus.append(cell29(p,f"L{L} {p['score']:.2f}"))
sheet(sus,'work/qa/v6audit_suspects.png',7)
random.seed(11)
samp=[]
for L in [6,25,39,13,34,33,58,12]:
    pool=by_leg_pts.get(L,[])
    for p in random.sample(pool,min(8,len(pool))):
        samp.append(cell29(p,f"L{L} {p['score']:.2f}"))
sheet(samp,'work/qa/v6audit_samples.png',8)
# unfilled windows for major legs (top-3 by far-peak)
cells=[]
for L in [34,12,58,33,6,39,3,25,26,41,64,63]:
    t,m,bcx,bcy=tpl(L)
    cand=[]
    for ni,ns in enumerate(num_state):
        if ns['expected'].get(L,0)>0 and ns['filled'][L]<ns['expected'][L]:
            r=window_peak_tpl(t,m,bcx,bcy,ns['num']['px'],ns['num']['py'],42,[])
            if r:
                dall=min((np.hypot(r[0]-a,r[1]-b) for a,b in allpos),default=999)
                cand.append((r[2],ni,r[0],r[1],dall))
    cand.sort(reverse=True)
    for v,ni,px,py,dall in cand[:3]:
        ns=num_state[ni]; x,y=int(round(ns['num']['px'])),int(round(ns['num']['py']))
        win=np.full((61,61,3),255,np.uint8)
        src=baseu[max(0,y-30):y+31,max(0,x-30):x+31]
        win[30-(y-max(0,y-30)):30-(y-max(0,y-30))+src.shape[0],30-(x-max(0,x-30)):30-(x-max(0,x-30))+src.shape[1]]=src
        cv2.drawMarker(win,(30,30),(255,0,0),cv2.MARKER_CROSS,9,1)
        cv2.drawMarker(win,(int(round(px-x))+30,int(round(py-y))+30),(0,0,255),cv2.MARKER_TILTED_CROSS,7,1)
        big=cv2.resize(win,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
        cv2.putText(big,f"L{L} {ns['num']['zone']}{ns['num']['value']} pk{v:.2f} d{dall:.0f}",(2,16),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,255),1)
        cells.append(big)
sheet(cells,'work/qa/v6audit_unfilled.png',6)
