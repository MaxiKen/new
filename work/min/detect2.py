import cv2, numpy as np, json, pickle, sys, time
sys.path.insert(0,'work/min')
from ncc import masked_ncc
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
meta=json.load(open('work/min/selftpl_meta.json'))
land=(cv2.imread('work/min/landmask.png',0)>0)
THR1={6:0.93,52:0.93,26:0.93,13:0.92,3:0.88,31:0.88,32:0.88,39:0.85,27:0.85,43:0.88,55:0.85,28:0.85,30:0.78,25:0.85,65:0.85,35:0.85,62:0.85,47:0.85,42:0.85,7:0.85,9:0.85,16:0.85,46:0.85,1:0.85,8:0.85,48:0.85,50:0.85,67:0.85,19:0.90,37:0.85,11:0.85,21:0.88,51:0.85,17:0.90,4:0.88,5:0.88,59:0.88,60:0.85,63:0.88,44:0.88,64:0.88,53:0.88,57:0.88,61:0.88,66:0.88,45:0.88,40:0.88,29:0.90,22:0.93,18:0.93,2:0.95,15:0.90,23:0.90,33:0.90,54:0.88,56:0.88}
def peaks_nms(ncc,thr,rad):
    ys,xs=np.where(ncc>=thr)
    if len(ys)==0: return []
    vals=ncc[ys,xs]; order=np.argsort(-vals)
    keep=[]; taken=np.zeros(ncc.shape,bool); H,W=ncc.shape
    for i in order:
        y,x=int(ys[i]),int(xs[i])
        if taken[y,x]: continue
        keep.append((x,y,float(vals[i])))
        taken[max(0,y-rad):min(H,y+rad+1),max(0,x-rad):min(W,x+rad+1)]=True
    return keep
def subpix(ncc,x,y):
    if x<=0 or y<=0 or x>=ncc.shape[1]-1 or y>=ncc.shape[0]-1: return float(x),float(y)
    def q(a,b,c):
        d=(a-2*b+c); return 0.5*(a-c)/d if abs(d)>1e-9 else 0.0
    return x+max(-1,min(1,q(ncc[y,x-1],ncc[y,x],ncc[y,x+1]))), y+max(-1,min(1,q(ncc[y-1,x],ncc[y,x],ncc[y+1,x])))
dets=[]; t0=time.time()
for leg in range(1,68):
    if leg==49: continue
    tpl=cv2.imread(f'work/min/selftpl4/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/selftpl4/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    if tpl is None or m.sum()<6: continue
    ncc=masked_ncc(base,tpl,m)
    cx,cy=meta[str(leg)]['center_xy']
    H,W=ncc.shape
    sub=land[int(round(cy)):int(round(cy))+H,int(round(cx)):int(round(cx))+W]
    if sub.shape==ncc.shape: ncc=np.where(sub,ncc,-1)
    thr=THR1.get(leg,0.90)
    rad=max(4,int(0.55*min(tpl.shape[:2])))
    for (x,y,v) in peaks_nms(ncc,thr,rad):
        sx,sy=subpix(ncc,x,y)
        dets.append({'leg':leg,'cx':float(sx+cx),'cy':float(sy+cy),'score':v,'stage':1})
print(f"dets v4: {len(dets)} in {time.time()-t0:.0f}s")
pickle.dump({'dets':dets},open('work/min/dets_v4.pkl','wb'))
