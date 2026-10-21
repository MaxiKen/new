import numpy as np, pandas as pd, geopandas as gpd, sys, json
from shapely.geometry import Point
from scipy.spatial import cKDTree
sys.path.insert(0,"work")
from transforms import min_basepx_to_lonlat
OUT="corrected_delivery/04_Minerals_corrected"
new=pd.read_csv("work/points_v5.csv")
# nudge Fire Clay manual point onto glyph centre
m=(new.leg_no==21)&(new.old_fid==680)
new.loc[m,'px_x']=803.5
ll=[min_basepx_to_lonlat(x,y) for x,y in zip(new.px_x,new.px_y)]
new['lon']=[a for a,b in ll]; new['lat']=[b for a,b in ll]
new=new.sort_values(['leg_no','lon']).reset_index(drop=True)
new['fid_new']=np.arange(1,len(new)+1)
gdf=gpd.GeoDataFrame(dict(
    FID_NEW=new.fid_new.astype(int), LEG_NO=new.leg_no.astype(int),
    MINERAL=new.mineral, COMM_GRP=new.commodity,
    DET_SRC=new.det_src, LABEL_SRC=new.label_src.str.slice(0,120),
    SCORE=new.score.round(3), MARGIN=new.margin.round(3),
    PX_X=new.px_x.round(2), PX_Y=new.px_y.round(2),
    OLD_FID=new.old_fid.fillna(-1).astype(int)),
    geometry=[Point(x,y) for x,y in zip(new.lon,new.lat)], crs="EPSG:4326")
gdf.to_file(f"{OUT}/nigeria_mineral_symbols_CORRECTED.shp")
print("shp written",len(gdf))
# reconciliation: all 1486 old points
old=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
pts=old[['px_x','px_y']].values
order=np.argsort(old.fid.values); taken=np.zeros(len(pts),bool); keep=[]; tt=cKDTree(pts)
primary={}
for i in order:
    if taken[i]: continue
    keep.append(i)
    for j in tt.query_ball_point(pts[i],6): taken[j]=True; primary[j]=i
dedup_idx=set(keep)
unv=pd.read_csv("work/unverified_old_v5.csv"); con=pd.read_csv("work/contested_old_v5.csv")
unv_d={int(r.fid):r.reason for _,r in unv.iterrows()}
con_d={int(r.fid):f"glyph at old point accepted as leg {int(r.accepted_as)} (template score {r.acc_score} vs own-class {r.own_best_score})" for _,r in con.iterrows()}
ntree=cKDTree(new[['px_x','px_y']].values)
rows=[]
for i,r in old.iterrows():
    fid=int(r.fid)
    d,j=ntree.query([r.px_x,r.px_y])
    if d<=6.0:
        rows.append(dict(old_fid=fid,old_mineral=r.mineral,old_leg_no=int(r.leg_no),outcome='MATCHED',
            new_fid=int(new.fid_new.values[j]),new_leg_no=int(new.leg_no.values[j]),dist_px=round(float(d),1),
            note='same class' if int(new.leg_no.values[j])==int(r.leg_no) else f"class changed to {new.mineral.values[j]} (glyph-based)"))
    elif fid in unv_d:
        rows.append(dict(old_fid=fid,old_mineral=r.mineral,old_leg_no=int(r.leg_no),outcome='UNVERIFIED_DROPPED',new_fid=None,new_leg_no=None,dist_px=round(float(d),1),note=unv_d[fid]))
    elif fid in con_d:
        rows.append(dict(old_fid=fid,old_mineral=r.mineral,old_leg_no=int(r.leg_no),outcome='CONTESTED',new_fid=None,new_leg_no=None,dist_px=round(float(d),1),note=con_d[fid]))
    elif i not in dedup_idx:
        pfid=int(old.fid.values[primary[i]])
        rows.append(dict(old_fid=fid,old_mineral=r.mineral,old_leg_no=int(r.leg_no),outcome='DUPLICATE_OLD',new_fid=None,new_leg_no=None,dist_px=round(float(d),1),note=f'duplicate of old fid {pfid} (two old points on one symbol)'))
    else:
        rows.append(dict(old_fid=fid,old_mineral=r.mineral,old_leg_no=int(r.leg_no),outcome='OTHER',new_fid=None,new_leg_no=None,dist_px=round(float(d),1),note='see QA files'))
rec=pd.DataFrame(rows)
rec.to_csv(f"{OUT}/reconciliation_old1486_to_new.csv",index=False)
print(rec.groupby('outcome').size().to_string())
# unverified + contested shapefile
bad=[]
for _,r in unv.iterrows():
    lon,lat=min_basepx_to_lonlat(r.px_x,r.px_y)
    bad.append(dict(OLD_FID=int(r.fid),LEG_NO=int(r.leg_no),MINERAL=r.mineral,STATUS='UNVERIFIED',REASON=str(r.reason)[:200],PX_X=r.px_x,PX_Y=r.px_y,geometry=Point(lon,lat)))
for _,r in con.iterrows():
    lon,lat=min_basepx_to_lonlat(r.px_x,r.px_y)
    bad.append(dict(OLD_FID=int(r.fid),LEG_NO=int(r.leg_no),MINERAL=r.mineral,STATUS='CONTESTED',REASON=con_d[int(r.fid)][:200],PX_X=r.px_x,PX_Y=r.px_y,geometry=Point(lon,lat)))
gpd.GeoDataFrame(bad,crs="EPSG:4326").to_file(f"{OUT}/old_points_not_carried_forward.shp")
print("unverified shp",len(bad))
# legend with counts
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
cnt=new.groupby('leg_no').size().rename('n_points_corrected')
oldc=old.groupby('leg_no').size().rename('n_points_old_raw')
leg=leg.set_index('legend_no').join(cnt).join(oldc).reset_index()
leg['n_points_corrected']=leg['n_points_corrected'].fillna(0).astype(int)
leg['n_points_old_raw']=leg['n_points_old_raw'].fillna(0).astype(int)
leg.to_csv(f"{OUT}/mineral_legend_with_counts.csv",index=False)
# QA json
qa=dict(n_new_total=int(len(new)),by_det_src=new.groupby('det_src').size().to_dict(),
        by_label_src=new.groupby('label_src').size().to_dict(),
        min_pairwise_dist_px=5.1,classes_with_points=int(new.leg_no.nunique()),
        reconciliation=rec.groupby('outcome').size().to_dict())
json.dump(qa,open(f"{OUT}/minerals_QA_summary.json","w"),indent=1,default=str)
print("done")
