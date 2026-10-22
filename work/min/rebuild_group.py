import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl
from collections import Counter
from scipy.spatial import cKDTree
from scipy.ndimage import maximum_filter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
S=pickle.load(open('work/min/complete_v4.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
cand=pickle.load(open('work/min/cand_v2.pkl','rb'))
def ascii_tpl(t,m,label):
    g=cv2.cvtColor(np.clip(t,0,255).astype(np.uint8),cv2.COLOR_BGR2GRAY)
    print(f"--- {label} ({t.shape[1]}x{t.shape[0]}) ---")
    for y in range(t.shape[0]):
        print(''.join(' ' if m[y,x]==0 else ('#' if g[y,x]<120 else ('.' if g[y,x]>210 else '+')) for x in range(t.shape[1])))
def window_peak_t(t,m,bcx,bcy,nx,ny,R,exclude=()):
    WR=int(R+14)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+bcx; ccy=yy+y0+bcy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.0)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return float(x+x0+bcx),float(y+y0+bcy),v

def harvest_template(L):
    lt=cv2.imread(f'work/min/templates/leg{L:02d}.png').astype(np.float32)
    lm=cv2.imread(f'work/min/templates/leg{L:02d}_mask.png',0).astype(np.float32)/255
    nums=[ns for ns in num_state if ns['expected'].get(L,0)>0]
    print(f"leg{L}: {len(nums)} expected numbers")
    best=None
    for s in [0.55,0.6,0.65,0.7,0.75,0.8,0.85]:
        t2,m2=scale_tpl(lt,lm,s)
        ys,xs=np.where(m2>0); bcx,bcy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
        scores=[]
        for ns in nums:
            r=window_peak_t(t2,m2,bcx,bcy,ns['num']['px'],ns['num']['py'],40)
            scores.append(r[2] if r else 0)
        med=float(np.median(scores)) if scores else 0
        print(f"  scale {s}: median peak {med:.3f}  n>=0.75: {sum(1 for v in scores if v>=0.75)}")
        if best is None or med>best[0]: best=(med,s,t2,m2,bcx,bcy)
    med,s,t2,m2,bcx,bcy=best
    print(f"  chosen scale {s} median {med:.3f}")
    patches=[]; centres=[]
    th,tw=t2.shape[:2]
    for ns in nums:
        r=window_peak_t(t2,m2,bcx,bcy,ns['num']['px'],ns['num']['py'],40)
        if r and r[2]>=0.75:
            cx,cy=r[0],r[1]
            x0,y0=int(round(cx-bcx)),int(round(cy-bcy))
            if x0>=0 and y0>=0 and x0+tw<=BW and y0+th<=BH:
                patches.append(base[y0:y0+th,x0:x0+tw]); centres.append((cx,cy,r[2],ns['key']))
    print(f"  harvest patches >=0.75: {len(patches)}")
    for c in centres: print("   ",c)
    if len(patches)>=3:
        newt=np.median(np.stack(patches),axis=0)
        # consistency
        cons=[]
        for p in patches:
            img=np.pad(p,((2,2),(2,2),(0,0)),mode='edge')
            cons.append(float(masked_ncc(img,newt,m2).max()))
        print("  instance-vs-median NCC:",[round(v,2) for v in cons])
        ascii_tpl(newt,m2,f"NEW leg{L} template (median of {len(patches)})")
        cv2.imwrite(f'work/min/selftpl4/leg{L:02d}.png',np.clip(newt,0,255).astype(np.uint8))
        cv2.imwrite(f'work/min/selftpl4/leg{L:02d}_mask.png',(m2*255).astype(np.uint8))
        return True
    ascii_tpl(t2,m2,f"legend leg{L} scaled {s} (harvest failed)")
    return False

ok32=harvest_template(32)
ok17=harvest_template(17)
print("rebuilt 32:",ok32," 17:",ok17)
pickle.dump({'ok32':ok32,'ok17':ok17},open('work/min/rebuild_flags.pkl','wb'))
