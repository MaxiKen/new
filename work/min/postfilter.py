import cv2, numpy as np, json, pickle, sys
import geopandas as gpd, pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
legcsv=pd.read_csv('work/min/mineral_legend.csv')
name_by_leg=dict(zip(legcsv.legend_no,legcsv.point_attribute_name))
grp_by_leg=dict(zip(legcsv.legend_no,legcsv.commodity_group))
g=gpd.read_file('work/min/minerals_v2.shp')
# shapefile truncated field names; reload from pickle instead
g=pickle.load(open('work/min/minerals_final_v2.pkl','rb'))
print("start:",len(g))
# (a) weak partials
mask_drop=(g.stage=='2partial')&(g.id_score<0.85)
print("drop weak partials:",int(mask_drop.sum()))
g=g[~mask_drop].copy()

TPL={}
def tpl(leg):
    if leg not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{leg:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{leg:02d}_mask.png',0).astype(np.float32)/255
        TPL[leg]=(t,m)
    return TPL[leg]
def score_at(leg,cx,cy):
    t,m=tpl(leg); ccx,ccy=meta[str(leg)]['center_xy']
    WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx2=xx+x0+ccx; ccy2=yy+y0+ccy
    ncc=np.where(np.hypot(ccx2-cx,ccy2-cy)<=1.6,ncc,-1)
    return float(ncc.max())
# (b) white-circle group rescore for stage3 rows
WG=[3,31,32,62]
drop_idx=[]; reassign=0
for i,r in g.iterrows():
    if r.stage!='3' or r.leg_no not in WG: continue
    scores={L:score_at(L,r.px_x,r.px_y) for L in WG}
    best=max(scores,key=scores.get)
    if scores[best]<0.90: drop_idx.append(i); continue
    if best!=r.leg_no:
        g.at[i,'leg_no']=best; g.at[i,'mineral']=name_by_leg.get(best,''); g.at[i,'comm_grp']=grp_by_leg.get(best,'')
        reassign+=1
print("white-group: dropped",len(drop_idx),"reassigned",reassign)
g=g.drop(index=drop_idx).copy()
# (c) ring/ink checks for stage3 legs 6,25,26,12
def patch_colors(leg,cx,cy):
    t,m=tpl(leg); ccx,ccy=meta[str(leg)]['center_xy']
    th,tw=t.shape[:2]
    x0=int(round(cx-ccx)); y0=int(round(cy-ccy))
    # ring: bbox expanded by 3
    rx0,ry0=max(0,x0-3),max(0,y0-3); rx1,ry1=min(BW,x0+tw+3),min(BH,y0+th+3)
    ring=[]
    inner=None
    if x0>=0 and y0>=0 and x0+tw<=BW and y0+th<=BH:
        sub=base[y0:y0+th,x0:x0+tw]
        inner=sub[m>0]
    big=base[ry0:ry1,rx0:rx1]
    # ring pixels = big minus inner bbox area
    maskbig=np.ones(big.shape[:2],bool)
    maskbig[y0-ry0:y0-ry0+th,x0-rx0:x0-rx0+tw]=False
    ring=big[maskbig]
    return inner,ring
drop2=[]
for i,r in g.iterrows():
    if r.stage!='3' or r.leg_no not in (6,25,26,12): continue
    inner,ring=patch_colors(int(r.leg_no),r.px_x,r.px_y)
    if inner is None or len(inner)==0 or len(ring)==0: continue
    gray_in=inner.mean(axis=1)
    if r.leg_no==6:
        dark=(gray_in<80).mean(); bright=(gray_in>190).mean()
        if not (dark>=0.15 and bright>=0.10): drop2.append(i)
    else:
        med_in=np.median(inner,axis=0); med_ring=np.median(ring,axis=0)
        diff=np.abs(med_in-med_ring).max()
        darkfrac=(gray_in<90).mean()
        if diff<16 and darkfrac<0.08: drop2.append(i)
print("ring/ink drops:",len(drop2))
g=g.drop(index=drop2).copy()
g=g.reset_index(drop=True)
g['fid']=range(1,len(g)+1)
print("FINAL v3:",len(g))
print(g.leg_no.value_counts().sort_index().to_string())
g.to_pickle('work/min/minerals_final_v3.pkl')
g.to_file('work/min/minerals_v3.shp')
