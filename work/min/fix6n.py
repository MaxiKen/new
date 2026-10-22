import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
baseu=cv2.imread('work/min/mineral_base.png')
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
S=pickle.load(open('work/min/complete6m.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        TPL[L]=(t,m,*C6[str(L)]['center_xy'])
    return TPL[L]
def score_at(L,cx,cy,tol=1.6,ret_pos=False):
    t,m,bcx,bcy=tpl(L); WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return (0.0,None) if ret_pos else 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ncc=np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=tol,ncc,-1)
    i=np.argmax(ncc); y,x=np.unravel_index(i,ncc.shape); v=float(ncc.ravel()[i])
    return (v,(float(x+x0+bcx),float(y+y0+bcy))) if ret_pos else v
gray=cv2.cvtColor(baseu,cv2.COLOR_BGR2GRAY)
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
def shape6(cx,cy):
    t,m,bcx,bcy=tpl(6)
    x0=int(round(cx-bcx)); y0=int(round(cy-bcy)); th,tw=t.shape[:2]
    if x0<0 or y0<0 or x0+tw>BW or y0+th>BH: return False,0,0
    v=gray[y0:y0+th,x0:x0+tw][m>0]
    return cc_check(darkm,cx,cy,9,10),(v<80).mean(),(v>200).mean()
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
def window_peak_tpl(t,m,bcx,bcy,nx,ny,R,exclude,excl_r=7.0):
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
# --- leg13 tol-3 arbitration vs 34 (recenter on relabel) ---
fl=0
for p in pts:
    if p['leg']==13:
        s13,_=score_at(13,p['cx'],p['cy'],tol=3.0,ret_pos=True)
        s34,pos34=score_at(34,p['cx'],p['cy'],tol=3.0,ret_pos=True)
        if s34>s13+0.03 and pos34:
            p['leg']=34; p['cx'],p['cy']=pos34; p['score']=round(s34,4); fl+=1
print("leg13->34 tol3 relabelled:",fl)
relink()
order=sorted(range(len(pts)),key=lambda i:-((2 if 'num_idx' in pts[i] else 0)+pts[i]['score']))
keep=[]; keptpos=[]
for i in order:
    p=pts[i]
    if any((p['cx']-a)**2+(p['cy']-b)**2<25 for a,b in keptpos): continue
    keep.append(p); keptpos.append((p['cx'],p['cy']))
pts[:]=keep; relink()
print("after dedup:",len(pts))
# --- leg6 missed-slot diagnostics ---
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
exclude=[(p['cx'],p['cy']) for p in pts]
t6,m6,bx6,by6=tpl(6)
cells=[]; verdicts=[]
for ni,ns in enumerate(num_state):
    if ns['expected'].get(6,0)==0 or ns['filled'][6]>=ns['expected'][6]: continue
    r=window_peak_tpl(t6,m6,bx6,by6,ns['num']['px'],ns['num']['py'],42,exclude)
    if r is None or r[2]<0.85: continue
    cx,cy,sc=r
    ok,fd,fb=shape6(cx,cy)
    si=score_at(6,cx,cy)
    comp={K:score_at(K,cx,cy) for K in LEGS if K!=6}
    bk=max(comp,key=comp.get)
    print(f"L6 {ns['num']['zone']}{ns['num']['value']}: peak={sc:.3f} at ({cx:.0f},{cy:.0f}) cc_ok={ok} darkfrac={fd:.2f} brightfrac={fb:.2f} si={si:.3f} best_other=L{bk} {comp[bk]:.3f}")
    verdicts.append((ni,cx,cy,sc,ok,si,bk,comp))
    x,y=int(round(cx)),int(round(cy))
    win=np.full((29,29,3),255,np.uint8)
    src=baseu[max(0,y-14):y+15,max(0,x-14):x+15]
    win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
    cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
    big=cv2.resize(win,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)
    cv2.putText(big,f"{ns['num']['zone']}{ns['num']['value']} pk{sc:.2f}",(2,16),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,255),1)
    cells.append(big)
if cells:
    H=cells[0].shape[0]; W=cells[0].shape[1]
    canvas=np.full((H,W*len(cells),3),255,np.uint8)
    for i,c in enumerate(cells): canvas[:,i*W:(i+1)*W]=c
    cv2.imwrite('work/qa/v6n_leg6_missed.png',canvas); print("saved leg6 missed montage",len(cells))
pickle.dump({'pts':pts,'num_state':num_state,'leg6_verdicts':verdicts},open('work/min/complete6n.pkl','wb'))
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"points={len(pts)} filled={fil}/{tot}")
