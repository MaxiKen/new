import cv2, numpy as np, json, pickle, sys, time
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from scipy.ndimage import maximum_filter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
C6=json.load(open('work/min/centres6.json'))
WEAK={19,22,30,39,44,52,59,65,14}
allcand=[]; t0=time.time()
for L in range(1,68):
    if L in (32,49): continue
    t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
    bcx,bcy=C6[str(L)]['center_xy']
    ncc=masked_ncc(base,t,m)
    thr=0.65 if L in WEAK else 0.70
    mx=maximum_filter(ncc,size=7)
    cand=np.argwhere((ncc>=mx-1e-6)&(ncc>=thr))
    pts=sorted([(float(ncc[y,x]),x+bcx,y+bcy) for y,x in cand],reverse=True)
    kept=[]
    for sc,cx,cy in pts:
        if any((cx-a)**2+(cy-b)**2<16 for a,b in kept): continue
        kept.append((cx,cy)); allcand.append({'leg':L,'cx':float(cx),'cy':float(cy),'score':round(sc,4)})
    print(f"leg{L:02d} cand={len(kept):4d} [{time.time()-t0:.0f}s]",flush=True)
pickle.dump(allcand,open('work/min/cand_v6.pkl','wb'))
print("TOTAL:",len(allcand))
