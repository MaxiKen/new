import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
baseu=cv2.imread('work/min/mineral_base.png')
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
S=pickle.load(open('work/min/complete6n.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        TPL[L]=(t,m,*C6[str(L)]['center_xy'])
    return TPL[L]
def score_at(L,cx,cy,tol=3.0,ret_pos=False):
    t,m,bcx,bcy=tpl(L); WR=22
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return (0.0,None) if ret_pos else 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ncc=np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=tol,ncc,-1)
    i=np.argmax(ncc); y,x=np.unravel_index(i,ncc.shape); v=float(ncc.ravel()[i])
    return (v,(float(x+x0+bcx),float(y+y0+bcy))) if ret_pos else v
gray=cv2.cvtColor(baseu,cv2.COLOR_BGR2GRAY)
Bc,Gc,Rc=baseu[:,:,0].astype(int),baseu[:,:,1].astype(int),baseu[:,:,2].astype(int)
yellow=((Rc>175)&(Gc>155)&(Bc<115)).astype(np.uint8)
darkm=(gray<95).astype(np.uint8)
def cc_check(mask_img,cx,cy,maxw,maxh,minw=0,minh=0,central=False):
    x,y=int(round(cx)),int(round(cy))
    x0,y0=max(0,x-11),max(0,y-11); x1,y1=min(BW,x+12),min(BH,y+12)
    sub=mask_img[y0:y1,x0:x1]
    n,lab,stats,cent=cv2.connectedComponentsWithStats(sub,8)
    best=None
    for dy in range(-2,3):
        for dx in range(-2,3):
            xx,yy=x-x0+dx,y-y0+dy
            if 0<=xx<sub.shape[1] and 0<=yy<sub.shape[0] and lab[yy,xx]>0: best=lab[yy,xx]; break
        if best: break
    if best is None: return False
    X,Y,W,H,A=stats[best]
    if W>maxw or H>maxh or W<minw or H<minh: return False
    if X==0 or Y==0 or X+W>=sub.shape[1] or Y+H>=sub.shape[0]: return False
    if central:
        relx=(x-x0-X)/max(W,1); rely=(y-y0-Y)/max(H,1)
        if not (0.2<=relx<=0.8 and 0.2<=rely<=0.8): return False
    return True
def shape_ok(L,cx,cy):
    if L==6:
        t,m,bcx,bcy=tpl(6)
        x0=int(round(cx-bcx)); y0=int(round(cy-bcy)); th,tw=t.shape[:2]
        if x0<0 or y0<0 or x0+tw>BW or y0+th>BH: return False
        v=gray[y0:y0+th,x0:x0+tw][m>0]
        return cc_check(darkm,cx,cy,9,10) and (v<80).mean()>=0.22 and (v>200).mean()>=0.13
    if L==25: return cc_check(yellow,cx,cy,11,11,central=True)
    if L==26: return cc_check(yellow,cx,cy,12,12,minw=7,minh=7,central=True)
    if L==13: return cc_check(darkm,cx,cy,14,9)
    if L==38: return cc_check(darkm,cx,cy,11,14)
    return True
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
GROUPS=[{3,31,53,10,19,5},{14,58},{2,9,21,34,13,37,17,45},{12,25,26},{20,33,23}]
gmap={}
for gi,g in enumerate(GROUPS):
    for L in g: gmap[L]=gi
changes=Counter()
for p in pts:
    L=p['leg']
    if L not in gmap or p.get('match_type')=='partial': continue
    g=GROUPS[gmap[L]]
    scur,_=score_at(L,p['cx'],p['cy'],ret_pos=True)
    best=(scur,L,None)
    for K in g:
        if K==L: continue
        sk,posk=score_at(K,p['cx'],p['cy'],ret_pos=True)
        if sk>best[0]: best=(sk,K,posk)
    if best[1]!=L and best[0]>scur+0.04 and best[2]:
        ncx,ncy=best[2]
        if best[1] in (6,25,26,13,38) and not shape_ok(best[1],ncx,ncy):
            changes['blocked-shape']+=1; continue
        changes[f"{L}->{best[1]}"]+=1
        p['leg']=best[1]; p['cx'],p['cy']=ncx,ncy; p['score']=round(best[0],4)
print("group challenge changes:",dict(changes))
relink()
order=sorted(range(len(pts)),key=lambda i:-((2 if 'num_idx' in pts[i] else 0)+pts[i]['score']))
keep=[]; keptpos=[]
for i in order:
    p=pts[i]
    if any((p['cx']-a)**2+(p['cy']-b)**2<25 for a,b in keptpos): continue
    keep.append(p); keptpos.append((p['cx'],p['cy']))
print(f"dedup {len(pts)}->{len(keep)}"); pts[:]=keep
relink()
# integrity
bad=[p for p in pts if not (0<=p['cx']<BW and 0<=p['cy']<BH) or np.isnan(p['cx']+p['cy']+p['score'])]
over1=[p for p in pts if p['score']>1.001]
print("out-of-bounds/NaN:",len(bad)," score>1:",len(over1), [(p['leg'],p['score']) for p in over1][:10])
for p in over1: p['score']=round(score_at(p['leg'],p['cx'],p['cy'],tol=1.6),4)
P=np.array([[p['cx'],p['cy']] for p in pts]); mind=999
for i in range(len(P)):
    d=np.hypot(P[i,0]-P[i+1:,0],P[i,1]-P[i+1:,1])
    if len(d): mind=min(mind,float(d.min()))
print("min separation px:",round(mind,2))
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"FINAL points={len(pts)} filled={fil}/{tot}")
print("match types:",Counter(p['match_type'] for p in pts))
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
unf=Counter()
for ns in num_state:
    for L,c in ns['expected'].items():
        if ns['filled'][L]<c: unf[L]+=c-ns['filled'][L]
print("unfilled:",dict(sorted(unf.items(),key=lambda kv:-kv[1])))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/complete6o.pkl','wb'))
print("saved complete6o.pkl")
