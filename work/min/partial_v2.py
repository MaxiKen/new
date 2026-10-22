import cv2, numpy as np, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
S=pickle.load(open('work/min/complete_v6.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
SKIP={1,8,48,49,50,53,62,67}
TPL={}
def tpl(L):
    if L==32: L=31  # shared glyph
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        ys,xs=np.where(m>0)
        TPL[L]=(t,m,(xs.min()+xs.max())/2,(ys.min()+ys.max())/2,(ys.min(),ys.max(),xs.min(),xs.max()))
    return TPL[L]
def halves(L):
    t,m,bcx,bcy,(y0,y1,x0,x1)=tpl(L)
    out={}
    yy,xx=np.mgrid[0:m.shape[0],0:m.shape[1]]
    for name,cond in [('top',yy<=bcy),('bottom',yy>=bcy),('left',xx<=bcx),('right',xx>=bcx)]:
        hm=(m*cond).astype(np.float32)
        if hm.sum()>=10: out[name]=hm
    return out
def peak_mask(L,mask,nx,ny,R,exclude):
    t,m,bcx,bcy,_=tpl(L); WR=int(R+14)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,mask)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+bcx; ccy=yy+y0+bcy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.0)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return float(x+x0+bcx),float(y+y0+bcy),v
def full_score(L,cx,cy):
    r=peak_mask(L,tpl(L)[1],cx,cy,1.6,())
    return r[2] if r else 0.0
exclude=[(p['cx'],p['cy']) for p in pts]
cands=[]
for ni,ns in enumerate(num_state):
    for L,cnt in ns['expected'].items():
        if L in SKIP: continue
        if ns['filled'][L]>=cnt: continue
        best=None
        for hname,hm in halves(L).items():
            r=peak_mask(L,hm,ns['num']['px'],ns['num']['py'],40,exclude)
            if r and (best is None or r[2]>best[0]): best=(r[2],r[0],r[1],hname)
        if best is None: continue
        sc,cx,cy,hname=best
        occ=min(np.hypot(cx-a,cy-b) for a,b in exclude) if exclude else 999
        fs=full_score(L,cx,cy)
        ok = sc>=0.85 or (sc>=0.76 and occ<=13 and fs>=0.45)
        cands.append({'ni':ni,'leg':L,'cx':cx,'cy':cy,'score':round(float(sc),4),'full':round(float(fs),3),
                      'vis':hname,'occ':round(float(occ),1),'ok':bool(ok)})
cands.sort(key=lambda c:-c['score'])
accepted=[]
taken=set()
for c in cands:
    if not c['ok']: continue
    if (c['ni'],c['leg']) in taken: continue
    if any((c['cx']-a)**2+(c['cy']-b)**2<25 for a,b in exclude): continue
    ns=num_state[c['ni']]
    if ns['filled'][c['leg']]>=ns['expected'][c['leg']]: continue
    accepted.append(c); taken.add((c['ni'],c['leg']))
    exclude.append((c['cx'],c['cy'])); ns['filled'][c['leg']]+=1
print(f"partial candidates ok={sum(1 for c in cands if c['ok'])} accepted={len(accepted)}")
print("by leg:",dict(sorted(Counter(c['leg'] for c in accepted).items())))
print("score pct:",[round(float(np.percentile([c['score'] for c in accepted],q)),2) for q in (0,25,50,75,100)] if accepted else None)
pickle.dump({'accepted':accepted,'cands':cands},open('work/min/partial_v2.pkl','wb'))
# montage ALL accepted
baseu=cv2.imread('work/min/mineral_base.png')
cells=[]
for i,c in enumerate(accepted):
    x,y=int(round(c['cx'])),int(round(c['cy']))
    win=np.full((31,31,3),255,np.uint8)
    src=baseu[max(0,y-15):y+16,max(0,x-15):x+16]
    win[15-(y-max(0,y-15)):15-(y-max(0,y-15))+src.shape[0],15-(x-max(0,x-15)):15-(x-max(0,x-15))+src.shape[1]]=src
    cv2.drawMarker(win,(15,15),(0,0,255),cv2.MARKER_CROSS,7,1)
    cv2.putText(win,f"#{i} L{c['leg']} {c['score']:.2f} {c['vis'][:3]}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.32,(0,0,255),1)
    cells.append(cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST))
if cells:
    cols=8; H=cells[0].shape[0]; W=cells[0].shape[1]
    rows=(len(cells)+cols-1)//cols
    # split into chunks of <=64
    for ci in range(0,len(cells),64):
        chunk=cells[ci:ci+64]
        rows=(len(chunk)+cols-1)//cols
        canvas=np.full((H*rows,W*cols,3),255,np.uint8)
        for i,cell in enumerate(chunk):
            r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=cell
        cv2.imwrite(f'work/qa/v2_partial_{ci//64}.png',canvas)
    print("montages saved")
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"filled after partial (provisional): {fil}/{tot}")
