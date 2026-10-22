import cv2, numpy as np, json, pickle, sys, time
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from scipy.ndimage import maximum_filter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
CAND={53:0.72, 62:0.85}  # default 0.80
allcand=[]
t0=time.time()
for L in range(1,68):
    if L==49: continue
    t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
    ys,xs=np.where(m>0)
    bcx,bcy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
    ncc=masked_ncc(base,t,m)
    thr=CAND.get(L,0.80)
    mx=maximum_filter(ncc,size=7)
    cand=np.argwhere((ncc>=mx-1e-6)&(ncc>=thr))
    pts=sorted([(float(ncc[y,x]),x+bcx,y+bcy) for y,x in cand],reverse=True)
    kept=[]
    for sc,cx,cy in pts:
        if any((cx-a)**2+(cy-b)**2<16 for a,b in kept): continue
        kept.append((cx,cy)); allcand.append({'leg':L,'cx':float(cx),'cy':float(cy),'score':round(sc,4)})
    c=[d for d in allcand if d['leg']==L]
    print(f"leg{L:02d} cand={len(c):4d} >=.95:{sum(1 for d in c if d['score']>=.95):4d} >=.90:{sum(1 for d in c if d['score']>=.90):4d} [{time.time()-t0:.0f}s]",flush=True)
pickle.dump(allcand,open('work/min/cand_v2.pkl','wb'))
print("TOTAL candidates:",len(allcand))
