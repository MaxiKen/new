import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
baseu=cv2.imread('work/min/mineral_base.png')
BH,BW=base.shape[:2]
C6=json.load(open('work/min/centres6.json'))
S=pickle.load(open('work/min/complete6k.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
TPL={}
def tpl(L):
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        TPL[L]=(t,m,*C6[str(L)]['center_xy'])
    return TPL[L]
HALF={}
def half_masks(L):
    if L in HALF: return HALF[L]
    t,m,bcx,bcy=tpl(L)
    colmass=m.sum(axis=0); rowmass=m.sum(axis=1)
    def med_split(mass):
        cs=np.cumsum(mass); return int(np.searchsorted(cs,cs[-1]/2))
    sx=med_split(colmass); sy=med_split(rowmass)
    H,W=m.shape; yy,xx=np.mgrid[0:H,0:W]
    out={'L':np.where(xx<=sx,m,0),'R':np.where(xx>=sx,m,0),
         'T':np.where(yy<=sy,m,0),'B':np.where(yy>=sy,m,0)}
    HALF[L]=out; return out
def score_with(mask,L,cx,cy,tol=1.6):
    t,m,bcx,bcy=tpl(L); WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,mask)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    return float(np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=tol,ncc,-1).max())
def score_at(L,cx,cy): return score_with(tpl(L)[1],L,cx,cy)
def window_peak_mask(t,mask,bcx,bcy,nx,ny,R,exclude,excl_r=7.0):
    WR=int(R+14)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,mask)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+bcx; ccy=yy+y0+bcy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>excl_r)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return float(x+x0+bcx),float(y+y0+bcy),v
# exact shape gates from complete6.py
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
SKIP={1,7,8,30,32,48,49,50,52,53,55,62,65,67}
# calibrate half floors from complete points
print("calibrating half floors...")
floors={}
from collections import defaultdict
by_leg=defaultdict(list)
for p in pts: by_leg[p['leg']].append(p)
for L in range(1,68):
    if L in SKIP or L not in by_leg: continue
    t,m,bcx,bcy=tpl(L)
    if min(t.shape[:2])<7: continue
    hm=half_masks(L)
    fl={}
    sample=by_leg[L][:40]
    for hname,hmask in hm.items():
        if hmask.sum()<12: fl[hname]=2.0; continue
        scs=[score_with(hmask,L,p['cx'],p['cy']) for p in sample]
        p10=float(np.percentile(scs,10)) if scs else 0.9
        fl[hname]=float(max(0.82,min(0.93,p10-0.06))) if len(sample)>=8 else 0.88
    floors[L]=fl
print("legs with half floors:",len(floors))
# unfilled slots
LEGS=[L for L in range(1,68) if L not in (32,49,62)]
exclude=[(p['cx'],p['cy']) for p in pts]
accepted=[]
rejc=Counter()
slots=[]
for ni,ns in enumerate(num_state):
    for L,c in ns['expected'].items():
        for _ in range(c-ns['filled'][L]):
            slots.append((ni,L))
print("unfilled slots to try:",len(slots))
for ni,L in slots:
    if L in SKIP or L not in floors: rejc['skip']+=1; continue
    ns=num_state[ni]
    nx,ny=ns['num']['px'],ns['num']['py']
    t,m,bcx,bcy=tpl(L)
    hm=half_masks(L)
    best=None
    for hname,hmask in hm.items():
        r=window_peak_mask(t,hmask,bcx,bcy,nx,ny,42,exclude)
        if r and (best is None or r[2]>best[3]): best=(r[0],r[1],hname,r[2])
    if best is None: rejc['nopeak']+=1; continue
    cx,cy,hname,hsc=best
    if hsc<floors[L][hname]: rejc['floor']+=1; continue
    fsc=score_at(L,cx,cy)
    if fsc<0.55: rejc['full']+=1; continue
    if L in (6,25,26,13,38) and not shape_ok(L,cx,cy): rejc['shape']+=1; continue
    # competitor arbitration
    si_h=score_with(hm[hname],L,cx,cy)
    bad=False
    for K in LEGS:
        if K==L: continue
        fk=score_at(K,cx,cy)
        if fk>=fsc-0.25:
            if K in SKIP or K not in HALF and False: pass
            hmk=half_masks(K)
            if hmk[hname].sum()>=12:
                sk=score_with(hmk[hname],K,cx,cy)
                if sk>si_h+0.01: bad=True; break
    if bad: rejc['compete']+=1; continue
    if L in (14,58):
        SIB=58 if L==14 else 14
        ss=score_with(half_masks(SIB)[hname],SIB,cx,cy)
        if si_h<ss+0.03: rejc['sibling']+=1; continue
    rec={'leg':L,'cx':cx,'cy':cy,'score':round(float(fsc),4),'half':hname,'half_score':round(float(hsc),4),
         'tier':f'partial-{hname}','match_type':'partial','num_idx':ni,
         'znum':ns['num']['zone']+str(ns['num']['value'])}
    accepted.append(rec)
    exclude.append((cx,cy))
print("partial accepted (provisional):",len(accepted),"rejections:",dict(rejc))
print("per-leg:",dict(sorted(Counter(a['leg'] for a in accepted).items())))
pickle.dump(accepted,open('work/min/partial6_cands.pkl','wb'))
for i,a in enumerate(accepted):
    print(f"IDX {i}: leg{a['leg']} {a['znum']} half={a['half']} hsc={a['half_score']} full={a['score']} at ({a['cx']:.0f},{a['cy']:.0f})")
# montages of all accepted (numbered)
def sheet(recs,path,cols=8):
    cells=[]
    for gi,a in recs:
        x,y=int(round(a['cx'])),int(round(a['cy']))
        win=np.full((29,29,3),255,np.uint8)
        src=baseu[max(0,y-14):y+15,max(0,x-14):x+15]
        win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
        cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
        big=cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST)
        cv2.putText(big,f"{gi}:L{a['leg']}{a['half']} {a['half_score']:.2f}",(2,14),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
        cells.append(big)
    if not cells: return
    H=cells[0].shape[0]; W=cells[0].shape[1]; rows=(len(cells)+cols-1)//cols
    canvas=np.full((H*rows,W*cols,3),255,np.uint8)
    for i,c in enumerate(cells):
        r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
    cv2.imwrite(path,canvas); print("saved",path,len(cells))
idx=list(enumerate(accepted))
sheet(idx[:64],'work/qa/v6_partial_0.png')
if len(idx)>64: sheet(idx[64:128],'work/qa/v6_partial_1.png')
if len(idx)>128: sheet(idx[128:],'work/qa/v6_partial_2.png')
