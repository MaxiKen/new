import numpy as np, pandas as pd, geopandas as gpd
from scipy.spatial import cKDTree
cand=pd.read_csv("work/scan_candidates2.csv")
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
pts=minr[['px_x','px_y']].values
order=np.argsort(minr.fid.values); taken=np.zeros(len(pts),bool); keep=[]; tt=cKDTree(pts)
for i in order:
    if taken[i]: continue
    keep.append(i)
    for j in tt.query_ball_point(pts[i],6): taken[j]=True
dedup=minr.iloc[keep].copy()
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
rows=[]
for no in range(1,68):
    sub=dedup[dedup.leg_no==no]; cc=cand[cand.leg_no==no]
    name=leg[leg.legend_no==no].point_attribute_name.values[0]
    if len(sub)==0 or len(cc)==0:
        rows.append(dict(leg_no=no,name=name,n_old=len(sub),hit=0,T=0.66,G=32,gated=int(((cc.score>=0.66)&(cc.dmean<=32)).sum()) if len(cc) else 0,note="no-old" if len(sub)==0 else "no-cand"))
        continue
    tree=cKDTree(cc[['px_x','px_y']].values)
    best=[]
    for _,r in sub.iterrows():
        idx=tree.query_ball_point([r.px_x,r.px_y],4.5)
        if idx:
            j=max(idx,key=lambda k:cc.score.values[k]); best.append((cc.score.values[j],cc.dmean.values[j]))
    hit=len(best); bs=np.array(best) if hit else np.zeros((0,2))
    if hit>=3:
        T=float(np.clip(np.quantile(bs[:,0],0.25)-0.06,0.50,0.86))
        G=float(np.clip(np.quantile(bs[:,1],0.75)+8,22,45))
    else:
        T,G=0.66,32
    gated=int(((cc.score>=T)&(cc.dmean<=G)).sum())
    rows.append(dict(leg_no=no,name=name,n_old=len(sub),hit=hit,hitfrac=round(hit/len(sub),2),
        med_s=round(float(np.median(bs[:,0])),2) if hit else None,p25_s=round(float(np.quantile(bs[:,0],0.25)),2) if hit else None,
        med_d=round(float(np.median(bs[:,1])),1) if hit else None,T=round(T,2),G=round(G),gated=gated,note=""))
df=pd.DataFrame(rows)
pd.set_option('display.width',200)
print(df.to_string(index=False))
df.to_csv("work/thresholds_v1.csv",index=False)
