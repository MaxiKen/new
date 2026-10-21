import numpy as np, pandas as pd, geopandas as gpd, sys
from scipy.spatial import cKDTree
sys.path.insert(0,"work")
from transforms import min_basepx_to_lonlat
cand=pd.read_csv("work/scan_candidates2.csv")
thr=pd.read_csv("work/thresholds_v1.csv").set_index('leg_no')
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
pts=minr[['px_x','px_y']].values
order=np.argsort(minr.fid.values); taken=np.zeros(len(pts),bool); keep=[]; tt=cKDTree(pts)
for i in order:
    if taken[i]: continue
    keep.append(i)
    for j in tt.query_ball_point(pts[i],6): taken[j]=True
dedup=minr.iloc[keep].copy().reset_index(drop=True)
# classes with raw points but zero after dedup: rescue from raw
extra=minr[~minr.leg_no.isin(dedup.leg_no.unique())].copy()
rescue_pool=pd.concat([dedup,extra],ignore_index=True)
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv").set_index('legend_no')

# ---- per-class config: (T,G,mode) mode: scan | group | rescue | scanqa
OVR={27:(0.84,60,'scan'),3:(0.88,60,'group'),31:(0.78,35,'group'),32:(0.86,35,'group'),49:(0.80,40,'group'),
7:(0.60,70,'group'),8:(0.70,40,'group'),62:(0.75,40,'group'),4:(0.68,40,'scan'),11:(0.62,40,'scan'),
28:(0.55,45,'rescue'),37:(0.60,45,'scan'),45:(0.80,30,'scan'),61:(0.75,35,'scan'),47:(0.82,28,'scan'),
51:(0.78,45,'rescue'),63:(0.58,30,'rescue'),66:(0.78,55,'rescue'),30:(0.85,30,'rescue'),
6:(9,9,'rescue'),59:(0.85,30,'rescue'),65:(0.75,30,'rescue'),1:(0.55,40,'scanqa'),15:(0.68,35,'scanqa'),
19:(0.60,40,'scanqa'),22:(0.66,35,'scanqa'),48:(0.50,40,'scanqa'),50:(0.68,35,'scanqa'),56:(0.58,40,'scanqa'),
52:(0.78,35,'scanqa'),2:(0.80,25,'scan'),9:(0.72,30,'scanqa'),67:(0.60,40,'rescue'),42:(0.70,35,'scanqa'),
46:(0.60,35,'rescue'),60:(0.62,55,'rescue'),16:(0.62,35,'scan'),18:(0.68,50,'scan'),21:(0.62,55,'scan'),
40:(0.70,45,'scan'),54:(0.66,35,'scan'),55:(0.62,45,'scan'),23:(0.80,25,'scan'),29:(0.84,28,'scan')}
CFG={}
for no in range(1,68):
    if no in OVR: CFG[no]=OVR[no]
    else:
        r=thr.loc[no]; CFG[no]=(float(r['T']),float(r['G']),'scan')
GROUPS=[{3,7,8,31,32,49,62},{23,33}]
def group_of(no):
    for g in GROUPS:
        if no in g: return g
    return {no}

# ---- pass 1: gated pool
pool=[]
for no,(T,G,mode) in CFG.items():
    if mode=='rescue' and no!=30 and no!=59 and no!=65: passmark=0.80  # Tier R: only very strong scan finds enter pool
    else: passmark=T
    cc=cand[(cand.leg_no==no)&(cand.score>=passmark)&(cand.dmean<=G)]
    for _,r in cc.iterrows():
        pool.append(dict(leg_no=no,px_x=r.px_x,px_y=r.px_y,score=r.score,dmean=r.dmean,mode=mode))
pool=pd.DataFrame(pool).sort_values('score',ascending=False).reset_index(drop=True)
print("gated pool",len(pool))
# margins: best other-class score within 4px in pool
tree=cKDTree(pool[['px_x','px_y']].values)
pool['margin']=0.0
for i,r in pool.iterrows():
    idx=tree.query_ball_point([r.px_x,r.px_y],4.0)
    others=[pool.score.values[j] for j in idx if pool.leg_no.values[j]!=r.leg_no]
    pool.at[i,'margin']=r.score-max(others) if others else r.score
# greedy competitive acceptance, exclusion 5px
accepted=[]; acc_xy=[]
atree=None
blocked=np.zeros(len(pool),bool)
acc_list=[]
xy=pool[['px_x','px_y']].values
alive=np.ones(len(pool),bool)
for i in range(len(pool)):
    if not alive[i]: continue
    acc_list.append(i)
    idx=tree.query_ball_point(xy[i],5.0)
    alive[idx]=False
acc=pool.iloc[acc_list].copy()
acc['det_src']='SCAN_COMPLETE'
print("pass1 accepted",len(acc))
# ---- pass 2: partial matches in cluster context (Tier scan/group only), score>=T-0.12 & >=0.5, gated, within 16px of an accepted point, >=5px from all accepted
p2=[]
for no,(T,G,mode) in CFG.items():
    if mode not in ('scan','group'): continue
    cc=cand[(cand.leg_no==no)&(cand.score>=max(0.5,T-0.12))&(cand.score<T)&(cand.dmean<=G+5)]
    for _,r in cc.iterrows(): p2.append(dict(leg_no=no,px_x=r.px_x,px_y=r.px_y,score=r.score,dmean=r.dmean,mode=mode))
p2=pd.DataFrame(p2)
if len(p2):
    atree=cKDTree(acc[['px_x','px_y']].values)
    d,_=atree.query(p2[['px_x','px_y']].values)
    p2=p2[(d>=5.0)&(d<=16.0)].sort_values('score',ascending=False)
    taken_xy=list(acc[['px_x','px_y']].values)
    newrows=[]
    for _,r in p2.iterrows():
        if all((r.px_x-a[0])**2+(r.px_y-a[1])**2>=25 for a in taken_xy):
            newrows.append(r); taken_xy.append([r.px_x,r.px_y])
    if newrows:
        nr=pd.DataFrame(newrows); nr['det_src']='SCAN_PARTIAL_CLUSTER'; nr['margin']=np.nan
        acc=pd.concat([acc,nr],ignore_index=True)
print("after pass2",len(acc))
# ---- group relabel via old points (within 4.5px, same glyph group)
oldtree=cKDTree(rescue_pool[['px_x','px_y']].values)
acc['label_src']='glyph-template'; acc['old_fid']=np.nan
for i,r in acc.iterrows():
    idx=oldtree.query_ball_point([r.px_x,r.px_y],4.5)
    if not idx: continue
    # prefer same class, else same group nearest
    cand_old=[(np.hypot(rescue_pool.px_x.values[j]-r.px_x,rescue_pool.px_y.values[j]-r.px_y),j) for j in idx]
    cand_old.sort()
    for dist,j in cand_old:
        ono=int(rescue_pool.leg_no.values[j])
        if ono==r.leg_no:
            acc.at[i,'old_fid']=int(rescue_pool.fid.values[j]); acc.at[i,'label_src']='glyph+old-agree'; break
        if ono in group_of(int(r.leg_no)):
            acc.at[i,'leg_no']=ono; acc.at[i,'old_fid']=int(rescue_pool.fid.values[j]); acc.at[i,'label_src']='old-table-within-glyphgroup'; break
# ---- rescue: old points (rescue_pool) not matched within 5px by accepted detection
atree=cKDTree(acc[['px_x','px_y']].values)
rescued=[]; unverified=[]
cand_by={no:cand[cand.leg_no==no] for no in range(1,68)}
matched_old=set(acc.old_fid.dropna().astype(int))
for _,r in rescue_pool.iterrows():
    fid=int(r.fid)
    d,_=atree.query([r.px_x,r.px_y])
    if d<=5.0: continue
    no=int(r.leg_no); T,G,mode=CFG[no]
    cc=cand_by[no]
    near=cc[(np.hypot(cc.px_x-r.px_x,cc.px_y-r.px_y)<=5.0)&(cc.dmean<=G+12)]
    if len(near):
        b=near.loc[near.score.idxmax()]
        rescued.append(dict(leg_no=no,px_x=b.px_x,px_y=b.px_y,score=b.score,dmean=b.dmean,mode=mode,det_src='RESCUE_RECENTRED',label_src='old',old_fid=fid,margin=np.nan))
    elif mode=='rescue':
        rescued.append(dict(leg_no=no,px_x=r.px_x,px_y=r.px_y,score=np.nan,dmean=np.nan,mode=mode,det_src='OLD_CENTRE_KEPT',label_src='old',old_fid=fid,margin=np.nan))
    else:
        unverified.append(dict(fid=fid,leg_no=no,mineral=r.mineral,px_x=r.px_x,px_y=r.px_y,mode=mode,reason='no gated template candidate within 5px'))
if rescued:
    rr=pd.DataFrame(rescued)
    # drop rescued that collide <=5px with accepted or each other (keep higher score first)
    rr=rr.sort_values('score',ascending=False,na_position='last')
    taken=list(acc[['px_x','px_y']].values); keep=[]
    for _,x in rr.iterrows():
        if all((x.px_x-a[0])**2+(x.px_y-a[1])**2>=25 for a in taken):
            keep.append(x); taken.append([x.px_x,x.px_y])
        else:
            unverified.append(dict(fid=int(x.old_fid),leg_no=int(x.leg_no),mineral=leg.loc[x.leg_no,'point_attribute_name'],px_x=x.px_x,px_y=x.px_y,mode=x['mode'],reason='rescue collided with accepted detection (same symbol)'))
    if keep: acc=pd.concat([acc,pd.DataFrame(keep)],ignore_index=True)
print("final points",len(acc),"unverified old",len(unverified))
acc['mineral']=[leg.loc[int(n),'point_attribute_name'] for n in acc.leg_no]
acc['commodity']=[leg.loc[int(n),'commodity_group'] for n in acc.leg_no]
ll=[min_basepx_to_lonlat(x,y) for x,y in zip(acc.px_x,acc.px_y)]
acc['lon']=[a for a,b in ll]; acc['lat']=[b for a,b in ll]
acc=acc.sort_values(['leg_no','px_y','px_x']).reset_index(drop=True)
acc.to_csv("work/points_v1.csv",index=False)
pd.DataFrame(unverified).to_csv("work/unverified_old_v1.csv",index=False)
pd.DataFrame([dict(leg_no=k,T=v[0],G=v[1],mode=v[2]) for k,v in CFG.items()]).to_csv("work/class_config_v1.csv",index=False)
summ=acc.groupby(['leg_no','mineral']).size().rename('n_new').reset_index()
old=rescue_pool.groupby('leg_no').size().rename('n_old_pool')
summ=summ.set_index('leg_no').join(old)
alls=pd.DataFrame(index=range(1,68)).join(summ)
alls['mineral']=[leg.loc[i,'point_attribute_name'] for i in alls.index]
print(alls.to_string())
print(acc.groupby('det_src').size())
