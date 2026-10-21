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
extra=minr[~minr.leg_no.isin(dedup.leg_no.unique())].copy()
rescue_pool=pd.concat([dedup,extra],ignore_index=True)
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv").set_index('legend_no')
# mode: scan | group | rescue | scanqa | grouplabel (no own pool; detected via group templates, labelled by old pts)
OVR={27:(0.84,60,'scan'),3:(0.90,55,'group'),31:(0.78,35,'group'),32:(0.86,35,'group'),49:(9,9,'grouplabel'),
7:(9,45,'rescue'),8:(9,9,'grouplabel'),62:(9,9,'grouplabel'),4:(0.72,28,'scan'),11:(0.66,35,'scan'),
28:(0.55,45,'rescue'),37:(0.60,45,'scan'),45:(0.80,30,'scan'),61:(0.75,35,'scan'),47:(0.88,28,'rescue'),
51:(0.78,45,'rescue'),63:(0.58,30,'rescue'),66:(0.78,55,'rescue'),30:(0.85,30,'rescue'),
6:(9,45,'rescue'),59:(0.85,30,'rescue'),65:(0.75,30,'rescue'),1:(0.55,40,'scanqa'),15:(0.68,35,'scanqa'),
19:(0.60,40,'scanqa'),22:(0.66,35,'scanqa'),48:(0.50,40,'scanqa'),50:(0.68,35,'scanqa'),56:(0.58,40,'scanqa'),
52:(0.78,35,'scanqa'),2:(0.80,25,'scan'),9:(0.72,30,'scanqa'),67:(0.60,40,'rescue'),42:(0.70,35,'scanqa'),
46:(0.60,35,'rescue'),60:(0.62,55,'rescue'),16:(0.62,35,'scan'),18:(0.68,50,'scan'),21:(0.62,55,'rescue'),
40:(0.82,30,'scan'),54:(0.66,35,'scan'),55:(0.85,45,'rescue'),23:(0.80,25,'scan'),29:(0.84,28,'scan'),
35:(0.85,22,'scan')}
CFG={}
for no in range(1,68):
    CFG[no]=OVR[no] if no in OVR else (float(thr.loc[no,'T']),float(thr.loc[no,'G']),'scan')
GROUPS=[{3,7,8,31,32,49,62},{23,33}]
def group_of(no):
    for g in GROUPS:
        if no in g: return g
    return {no}
pool=[]
for no,(T,G,mode) in CFG.items():
    if mode=='grouplabel' or T>2: continue
    pm=0.80 if mode=='rescue' else T
    cc=cand[(cand.leg_no==no)&(cand.score>=pm)&(cand.dmean<=G)]
    for _,r in cc.iterrows(): pool.append(dict(leg_no=no,px_x=r.px_x,px_x2=r.px_x,px_y=r.px_y,score=r.score,dmean=r.dmean,mode=mode))
pool=pd.DataFrame(pool).drop(columns='px_x2')
print("pool",len(pool))
tree=cKDTree(pool[['px_x','px_y']].values)
idxs=tree.query_ball_point(pool[['px_x','px_y']].values,4.0)
legarr=pool.leg_no.values; scarr=pool.score.values; margins=np.zeros(len(pool))
for i,idx in enumerate(idxs):
    g=group_of(int(legarr[i]))
    others=[scarr[j] for j in idx if int(legarr[j]) not in g]
    margins[i]=scarr[i]-max(others) if others else scarr[i]
pool['margin']=margins
pool=pool[pool.margin>=0.03].sort_values('score',ascending=False).reset_index(drop=True)
print("pool after margin",len(pool))
tree=cKDTree(pool[['px_x','px_y']].values)
alive=np.ones(len(pool),bool); acc_idx=[]
xy=pool[['px_x','px_y']].values
for i in range(len(pool)):
    if not alive[i]: continue
    acc_idx.append(i); alive[tree.query_ball_point(xy[i],5.0)]=False
acc=pool.iloc[acc_idx].copy().reset_index(drop=True)
acc['det_src']='SCAN_COMPLETE'; acc['label_src']='glyph-template'; acc['old_fid']=np.nan
print("pass1",len(acc))
# group relabel + old matching
oldtree=cKDTree(rescue_pool[['px_x','px_y']].values)
for i,r in acc.iterrows():
    idx=oldtree.query_ball_point([r.px_x,r.px_y],4.5)
    if not idx: continue
    cand_old=sorted((np.hypot(rescue_pool.px_x.values[j]-r.px_x,rescue_pool.px_y.values[j]-r.px_y),j) for j in idx)
    done=False
    for dist,j in cand_old:
        ono=int(rescue_pool.leg_no.values[j])
        if ono==int(r.leg_no):
            acc.at[i,'old_fid']=int(rescue_pool.fid.values[j]); acc.at[i,'label_src']='glyph+old-agree'; done=True; break
    if done: continue
    for dist,j in cand_old:
        ono=int(rescue_pool.leg_no.values[j])
        if ono in group_of(int(r.leg_no)):
            acc.at[i,'leg_no']=ono; acc.at[i,'old_fid']=int(rescue_pool.fid.values[j]); acc.at[i,'label_src']='old-table-within-glyphgroup'; break
# rescue old points not matched (by old_fid or same-class detection within 5px)
matched_fids=set(acc.old_fid.dropna().astype(int))
atree=cKDTree(acc[['px_x','px_y']].values)
cand_by={no:cand[cand.leg_no==no] for no in range(1,68)}
rescued=[]; unverified=[]; contested=[]
for _,r in rescue_pool.iterrows():
    fid=int(r.fid); no=int(r.leg_no)
    if fid in matched_fids: continue
    # same-class detection nearby?
    idx=atree.query_ball_point([r.px_x,r.px_y],5.0)
    same=[j for j in idx if int(acc.leg_no.values[j])==no]
    if same: continue
    T,G,mode=CFG[no]
    cc=cand_by[no]
    near=cc[(np.hypot(cc.px_x-r.px_x,cc.px_y-r.px_y)<=6.0)&(cc.dmean<=G+15)]
    b=near.loc[near.score.idxmax()] if len(near) else None
    if idx:  # different-class detection occupies this old point -> contest
        j=idx[np.argmin([np.hypot(acc.px_x.values[k]-r.px_x,acc.px_y.values[k]-r.px_y) for k in idx])]
        if b is not None and b.score>=acc.score.values[j]-0.06 and b.score>=0.5:
            acc.at[j,'leg_no']=no; acc.at[j,'old_fid']=fid; acc.at[j,'label_src']='old-table-neartie'
            matched_fids.add(fid)
        else:
            contested.append(dict(fid=fid,leg_no=no,mineral=r.mineral,px_x=r.px_x,px_y=r.px_y,
                accepted_as=int(acc.leg_no.values[j]),acc_score=round(float(acc.score.values[j]),2),
                own_best_score=round(float(b.score),2) if b is not None else None))
        continue
    if b is not None and b.score>=0.45:
        rescued.append(dict(leg_no=no,px_x=b.px_x,px_y=b.px_y,score=b.score,dmean=b.dmean,mode=mode,det_src='RESCUE_RECENTRED',label_src='old',old_fid=fid,margin=np.nan))
    elif mode in ('rescue','grouplabel'):
        rescued.append(dict(leg_no=no,px_x=r.px_x,px_y=r.px_y,score=np.nan,dmean=np.nan,mode=mode,det_src='OLD_CENTRE_KEPT',label_src='old',old_fid=fid,margin=np.nan))
    else:
        unverified.append(dict(fid=fid,leg_no=no,mineral=r.mineral,px_x=r.px_x,px_y=r.px_y,mode=mode,reason='no template candidate >=0.45 within 6px'))
if rescued:
    rr=pd.DataFrame(rescued).sort_values('score',ascending=False,na_position='last')
    taken=list(acc[['px_x','px_y']].values); keep=[]
    for _,x in rr.iterrows():
        if all((x.px_x-a[0])**2+(x.px_y-a[1])**2>=25 for a in taken):
            keep.append(x); taken.append([x.px_x,x.px_y])
        elif x.det_src=='OLD_CENTRE_KEPT':
            unverified.append(dict(fid=int(x.old_fid),leg_no=int(x.leg_no),mineral=leg.loc[x.leg_no,'point_attribute_name'],px_x=x.px_x,px_y=x.px_y,mode=x['mode'],reason='old-centre rescue collided with accepted detection'))
    if keep: acc=pd.concat([acc,pd.DataFrame(keep)],ignore_index=True)
print("final",len(acc),"unverified",len(unverified),"contested",len(contested))
acc['mineral']=[leg.loc[int(n),'point_attribute_name'] for n in acc.leg_no]
acc['commodity']=[leg.loc[int(n),'commodity_group'] for n in acc.leg_no]
ll=[min_basepx_to_lonlat(x,y) for x,y in zip(acc.px_x,acc.px_y)]
acc['lon']=[a for a,b in ll]; acc['lat']=[b for a,b in ll]
acc=acc.sort_values(['leg_no','px_y','px_x']).reset_index(drop=True)
acc.to_csv("work/points_v2.csv",index=False)
pd.DataFrame(unverified).to_csv("work/unverified_old_v2.csv",index=False)
pd.DataFrame(contested).to_csv("work/contested_old_v2.csv",index=False)
pd.DataFrame([dict(leg_no=k,T=v[0],G=v[1],mode=v[2]) for k,v in CFG.items()]).to_csv("work/class_config_v2.csv",index=False)
summ=acc.groupby('leg_no').size().rename('n_new')
old=rescue_pool.groupby('leg_no').size().rename('n_old')
tab=pd.DataFrame(index=range(1,68)).join(summ).join(old)
tab['mineral']=[leg.loc[i,'point_attribute_name'] for i in tab.index]
tab['mode']=[CFG[i][2] for i in tab.index]
print(tab.to_string())
print(acc.groupby('det_src').size())
