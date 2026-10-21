import cv2, numpy as np, json, pickle, os, sys
sys.path.insert(0,'work/min')
os.makedirs('work/min/selftpl4',exist_ok=True)
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
S=pickle.load(open('work/min/link_stage2.pkl','rb'))
objs=S['objs']
from collections import defaultdict
byleg=defaultdict(list)
for o in objs:
    if o['claimed_by'] is None: continue
    ni,leg=o['claimed_by']
    sc=o['scores'].get(leg,(0,))[0]
    byleg[leg].append((sc,o['cx'],o['cy']))
def ncc_shift(T,M,P,dx,dy,ys,xs,off):
    a=T[ys,xs]; b=P[ys+off+dy,xs+off+dx]
    a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    den=np.sqrt(float((a*a).sum())*float((b*b).sum()))
    return float((a*b).sum())/den if den>1e-6 else 0.0
newmeta={}
for leg in range(1,68):
    if leg==49:
        # copy 32
        continue
    t3=cv2.imread(f'work/min/selftpl/leg{leg:02d}.png')
    m3=cv2.imread(f'work/min/selftpl/leg{leg:02d}_mask.png',0)
    if t3 is None: continue
    cents=byleg.get(leg,[])
    cents=[c for c in cents if c[0]>=0.60]
    cx,cy=meta[str(leg)]['center_xy']
    th,tw=t3.shape[:2]
    OFF=6
    patches=[]
    for sc,x,y in cents[:40]:
        x0=int(round(x-cx))-OFF; y0=int(round(y-cy))-OFF
        if x0<0 or y0<0 or x0+tw+2*OFF>BW or y0+th+2*OFF>BH: continue
        patches.append(base[y0:y0+th+2*OFF,x0:x0+tw+2*OFF].copy())
    if len(patches)>=3:
        T=t3.astype(np.float32); M=(m3>0).astype(np.float32)
        ys,xs=np.where(M>0)
        shifted=None; scores=[0]*len(patches)
        for r in range(3):
            shifted=[]
            for i,p in enumerate(patches):
                bb=(-2,0,0)
                for dy in range(-3,4):
                    for dx in range(-3,4):
                        v=ncc_shift(T,M,p,dx,dy,ys,xs,OFF)
                        if v>bb[0]: bb=(v,dx,dy)
                scores[i]=bb[0]
                shifted.append(p[OFF+bb[2]:OFF+bb[2]+th,OFF+bb[1]:OFF+bb[1]+tw])
            T=np.median(np.stack(shifted),axis=0)
        keep=[i for i,v in enumerate(scores) if v>=0.6]
        if len(keep)>=3:
            T=np.median(np.stack([shifted[i] for i in keep]),axis=0)
        cv2.imwrite(f'work/min/selftpl4/leg{leg:02d}.png',np.clip(T,0,255).astype(np.uint8))
        cv2.imwrite(f'work/min/selftpl4/leg{leg:02d}_mask.png',m3)
        newmeta[leg]={'src':'v4_from_claims','n':len(keep),'med':float(np.median([scores[i] for i in keep])) if keep else 0}
        print(f"leg{leg:02d} v4 from {len(keep)} claims med={newmeta[leg]['med']:.2f}")
    else:
        cv2.imwrite(f'work/min/selftpl4/leg{leg:02d}.png',t3)
        cv2.imwrite(f'work/min/selftpl4/leg{leg:02d}_mask.png',m3)
        newmeta[leg]={'src':'v3_kept','n':len(patches)}
        print(f"leg{leg:02d} v3 kept (claims={len(cents)})")
json.dump(newmeta,open('work/min/selftpl4_meta.json','w'),indent=1)
