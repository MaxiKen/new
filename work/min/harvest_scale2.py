import cv2, numpy as np, json, pickle
import sys; sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl
from collections import defaultdict
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
meta=json.load(open('work/min/templates_meta.json'))
cases=pickle.load(open('work/min/harvest_cases.pkl','rb'))
byleg=defaultdict(list)
for c in cases: byleg[c['leg']].append(c)
# focus legs for scale: common & crisp
FOCUS=[34,12,39,14,58,26,31,36,64,20,33,41,10,37,13]
sample=[]
for leg in FOCUS: sample+=byleg[leg][:10]
print("sample",len(sample))
tpls={}
def get_tpl(leg,s):
    if (leg,s) not in tpls:
        t=cv2.imread(f'work/min/templates/leg{leg:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/templates/leg{leg:02d}_mask.png',0).astype(np.float32)/255.0
        tpls[(leg,s)]=scale_tpl(t,m,s)
    return tpls[(leg,s)]
R=40; MAXD=26
for s in [0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.9,1.0]:
    per=defaultdict(list)
    for c in sample:
        t,m=get_tpl(c['leg'],s)
        cx0,cy0=meta[str(c['leg'])]['center_xy']
        x0=int(max(0,c['px']-R)); y0=int(max(0,c['py']-R))
        x1=int(min(base.shape[1],c['px']+R)); y1=int(min(base.shape[0],c['py']+R))
        win=base[y0:y1,x0:x1]
        if win.shape[0]<t.shape[0] or win.shape[1]<t.shape[1]: continue
        ncc=masked_ncc(win,t,m)
        # restrict symbol-center distance to number <=MAXD
        H,W=ncc.shape
        yy,xx=np.mgrid[0:H,0:W]
        ccx=xx+x0+cx0*s; ccy=yy+y0+cy0*s
        dist=np.hypot(ccx-c['px'],ccy-c['py'])
        ncc2=np.where(dist<=MAXD,ncc,-1)
        per[c['leg']].append(float(ncc2.max()))
    allv=np.array([v for vs in per.values() for v in vs])
    print(f"s={s}: median={np.median(allv):.3f} frac>0.8={(allv>0.8).mean():.2f} frac>0.9={(allv>0.9).mean():.2f} | "+" ".join(f"{leg}:{np.median(per[leg]):.2f}" for leg in FOCUS if leg in per))
