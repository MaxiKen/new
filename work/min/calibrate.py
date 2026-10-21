import cv2, numpy as np, json, pickle, sys
import geopandas as gpd, pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
rng=np.random.default_rng(7)
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
land=(cv2.imread('work/min/landmask.png',0)>0)
old=gpd.read_file('shapefile_results/minerals/nigeria_mineral_symbols.shp')
# expected counts from tables (code->leg)
tab=pd.read_pickle('work/min/tables_final.pkl')
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':9,'Be':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67}
from collections import Counter
expct=Counter()
for _,r in tab.iterrows():
    legs=[]
    for c in r.codes_list:
        if c in CODE2LEG: legs.append(CODE2LEG[c])
    for L in set(legs): expct[L]+=1  # per locality per leg (Pb+Zn merged via set)
def local_peak(ncc,cx_top,cy_top,rad=5):
    H,W=ncc.shape
    x0,x1=max(0,cx_top-rad),min(W,cx_top+rad+1)
    y0,y1=max(0,cy_top-rad),min(H,cy_top+rad+1)
    if x1<=x0 or y1<=y0: return -1
    return float(ncc[y0:y1,x0:x1].max())
out={}
for leg in range(1,68):
    if leg==49: continue
    tpl=cv2.imread(f'work/min/selftpl/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/selftpl/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    if tpl is None or m.sum()<6: continue
    ncc=masked_ncc(base,tpl,m)
    cx,cy=meta[str(leg)]['center_xy']
    H,W=ncc.shape
    sub=land[int(round(cy)):int(round(cy))+H,int(round(cx)):int(round(cx))+W]
    if sub.shape==ncc.shape: ncc=np.where(sub,ncc,-1)
    seeds=old[old.leg_no==leg]
    ss=[]
    for _,r in seeds.iterrows():
        tx,ty=int(round(r.px_x-cx)),int(round(r.px_y-cy))
        ss.append(local_peak(ncc,tx,ty,5))
    ss=np.array([s for s in ss if s>-1])
    # background: random land points
    ys,xs=np.where(land)
    idx=rng.integers(0,len(ys),400)
    bg=[]
    for i in idx:
        tx,ty=int(xs[i]-cx),int(ys[i]-cy)
        if 0<=tx<W and 0<=ty<H: bg.append(local_peak(ncc,tx,ty,5))
    bg=np.array(bg)
    if len(ss)>=3:
        thr=float(np.clip(np.percentile(ss,8),0.60,0.93))
    elif len(ss)>=1:
        thr=float(np.clip(np.min(ss)-0.05,0.60,0.93))
    else:
        thr=0.80
    out[leg]={'thr':thr,'seed_n':int(len(ss)),
              'seed_p10':float(np.percentile(ss,10)) if len(ss) else None,
              'seed_p50':float(np.percentile(ss,50)) if len(ss) else None,
              'bg_p999':float(np.percentile(bg,99.9)) if len(bg) else None,
              'bg_p99':float(np.percentile(bg,99)) if len(bg) else None,
              'expected_localities':int(expct.get(leg,0))}
    print(f"leg{leg:02d} thr={thr:.2f} seeds={len(ss)} p10={out[leg]['seed_p10']} p50={out[leg]['seed_p50']} bg99={out[leg]['bg_p99']:.2f} bg999={out[leg]['bg_p999']:.2f} exp={expct.get(leg,0)}")
json.dump(out,open('work/min/thresholds.json','w'),indent=1)
print("saved")
