import numpy as np, pandas as pd, geopandas as gpd, sys
from scipy.spatial import cKDTree
sys.path.insert(0,"work")
from transforms import min_basepx_to_lonlat
cand=pd.read_csv("work/scan_candidates3.csv")
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
CFG={1:(0,0,'none'),2:(0.82,25,'scan'),3:(9,9,'grouplabel'),4:(0.84,26,'scan'),5:(0.79,39,'scan'),
6:(9,45,'rescue'),7:(9,60,'rescue'),8:(9,9,'grouplabel'),9:(9,35,'special'),10:(0.80,24,'scan'),
11:(0.74,32,'scan'),12:(0.82,22,'scan'),13:(0.69,41,'scan'),14:(0.78,26,'scan'),15:(0.82,30,'scan'),
16:(0.78,32,'scan'),17:(0.86,22,'scan'),18:(0.90,30,'scan'),19:(0,0,'none'),20:(0.86,27,'scan'),
21:(9,55,'rescue'),22:(0,0,'none'),23:(0.82,25,'scan'),24:(0.84,24,'scan'),25:(0.81,25,'scan'),
26:(0.75,32,'scan'),27:(0.84,60,'scan'),28:(9,45,'rescue'),29:(0.84,28,'scan'),30:(9,45,'rescue'),
31:(0.78,35,'group'),32:(0.86,35,'group'),33:(0.81,22,'scan'),34:(0.80,26,'scan'),35:(0.85,22,'scan'),
36:(0.72,32,'scan'),37:(0.70,35,'scan'),38:(0.86,22,'scan'),39:(0.68,28,'scan'),40:(0.82,30,'scan'),
41:(0.81,35,'scan'),42:(0,0,'none'),43:(0.86,22,'scan'),44:(0.55,22,'scan'),45:(0.80,30,'scan'),
46:(9,35,'rescue'),47:(0.88,26,'scan'),48:(0.60,25,'scan'),49:(9,9,'grouplabel'),50:(0,0,'none'),
51:(0.80,35,'scan'),52:(0,0,'none'),53:(0.82,28,'scan'),54:(0.78,32,'scan'),55:(9,45,'rescue'),
56:(0,0,'none'),57:(0.76,33,'scan'),58:(0.72,32,'scan'),59:(0,0,'none'),60:(9,55,'rescue'),
61:(0.75,35,'scan'),62:(9,9,'grouplabel'),63:(0.80,30,'scan'),64:(0.82,30,'scan'),65:(9,35,'rescue'),
66:(0.80,40,'scan'),67:(0.75,35,'scan')}
GROUPS=[{3,7,8,31,32,49,62},{23,33},{10,53}]
def group_of(no):
    for g in GROUPS:
        if no in g: return g
    return {no}
def build_pool(p2=False):
    rows=[]
    for no,(T,G,mode) in CFG.items():
        if mode not in ('scan','group'): continue
        if p2: cc=cand[(cand.leg_no==no)&(cand.score>=T-0.10)&(cand.score<T)&(cand.dmean<=G)]
        else: cc=cand[(cand.leg_no==no)&(cand.score>=T)&(cand.dmean<=G)]
        for _,r in cc.iterrows(): rows.append(dict(leg_no=no,px_x=r.px_x,px_y=r.px_y,score=r.score,dmean=r.dmean,mode=mode))
    return pd.DataFrame(rows)
pool=build_pool()
print("pass1 pool",len(pool))
tree=cKDTree(pool[['px_x','px_y']].values)
idxs=tree.query_ball_point(pool[['px_x','px_y']].values,4.0)
legarr=pool.leg_no.values; scarr=pool.score.values; margins=np.zeros(len(pool))
for i,idx in enumerate(idxs):
    g=group_of(int(legarr[i]))
    others=[scarr[j] for j in idx if int(legarr[j]) not in g]
    margins[i]=scarr[i]-max(others) if others else scarr[i]
pool['margin']=margins
pool=pool[pool.margin>=0.04].sort_values('score',ascending=False).reset_index(drop=True)
tree=cKDTree(pool[['px_x','px_y']].values)
alive=np.ones(len(pool),bool); acc_idx=[]; xy=pool[['px_x','px_y']].values
for i in range(len(pool)):
    if not alive[i]: continue
    acc_idx.append(i); alive[tree.query_ball_point(xy[i],5.0)]=False
acc=pool.iloc[acc_idx].copy().reset_index(drop=True)
acc['det_src']='SCAN_COMPLETE'; acc['label_src']='glyph-template'; acc['old_fid']=np.nan
print("pass1 accepted",len(acc))
# pass2 controlled partials in clusters
p2=build_pool(p2=True)
if len(p2):
    atree=cKDTree(acc[['px_x','px_y']].values)
    d,_=atree.query(p2[['px_x','px_y']].values)
    cnt=[len(atree.query_ball_point(p,18.0)) for p in p2[['px_x','px_y']].values]
    p2=p2[(d>=5.0)&(d<=15.0)&(np.array(cnt)>=2)].copy()
    # margin vs pass1 pool candidates within 4px (approx via pool tree rebuilt on p2+pool subset)
    allc=pd.concat([pool[['leg_no','px_x','px_y','score']],p2[['leg_no','px_x','px_y','score']]],ignore_index=True)
    t2=cKDTree(allc[['px_x','px_y']].values)
    mg=[]
    for _,r in p2.iterrows():
        idx=t2.query_ball_point([r.px_x,r.px_y],4.0)
        g=group_of(int(r.leg_no))
        others=[allc.score.values[j] for j in idx if int(allc.leg_no.values[j]) not in g]
        mg.append(r.score-max(others) if others else r.score)
    p2['margin']=mg
    p2=p2[p2.margin>=0.05].sort_values('score',ascending=False)
    taken=list(acc[['px_x','px_y']].values); new=[]
    for _,r in p2.iterrows():
        if all((r.px_x-a[0])**2+(r.px_y-a[1])**2>=25 for a in taken):
            new.append(r); taken.append([r.px_x,r.px_y])
    if new:
        nr=pd.DataFrame(new); nr['det_src']='SCAN_PARTIAL_CLUSTER'; nr['label_src']='glyph-template'; nr['old_fid']=np.nan
        acc=pd.concat([acc,nr],ignore_index=True)
    print("after pass2",len(acc))
# group relabel via old points
oldtree=cKDTree(rescue_pool[['px_x','px_y']].values)
for i,r in acc.iterrows():
    idx=oldtree.query_ball_point([r.px_x,r.px_y],4.5)
    if not idx: continue
    cand_old=sorted((np.hypot(rescue_pool.px_x.values[j]-r.px_x,rescue_pool.px_y.values[j]-r.px_y),j) for j in idx)
    done=False
    for dist,j in cand_old:
        if int(rescue_pool.leg_no.values[j])==int(r.leg_no):
            acc.at[i,'old_fid']=int(rescue_pool.fid.values[j]); acc.at[i,'label_src']='glyph+old-agree'; done=True; break
    if done: continue
    for dist,j in cand_old:
        ono=int(rescue_pool.leg_no.values[j])
        if ono in group_of(int(r.leg_no)) and CFG[ono][2]!='none':
            acc.at[i,'leg_no']=ono; acc.at[i,'old_fid']=int(rescue_pool.fid.values[j]); acc.at[i,'label_src']='old-table-within-glyphgroup'; break
# rescue
matched_fids=set(acc.old_fid.dropna().astype(int))
cand_by={no:cand[cand.leg_no==no] for no in range(1,68)}
rescued=[]; unverified=[]; contested=[]
VISUAL_NONE={22:"old point checked on raster: sits on Feldspar/river, no Fluorite glyph",42:"old point checked: on Brine/Clay glyphs, no Marcasite glyph",19:"old point checked: on yellow-rect cluster, no Evaporite glyph",59:"old point checked: on Lepidolite/Gold cluster, no Tar Sand glyph",67:"old Calcite points are on Copper glyphs (now Copper points)"}
for _,r in rescue_pool.iterrows():
    fid=int(r.fid); no=int(r.leg_no)
    if fid in matched_fids: continue
    T,G,mode=CFG[no]
    if mode=='none':
        unverified.append(dict(fid=fid,leg_no=no,mineral=r.mineral,px_x=r.px_x,px_y=r.px_y,reason=VISUAL_NONE.get(no,'class has no reliably detectable glyph at source resolution; no glyph verified at old point')))
        continue
    if no==67:  # old Calcite points = Copper glyphs; do not rescue as Calcite
        unverified.append(dict(fid=fid,leg_no=no,mineral=r.mineral,px_x=r.px_x,px_y=r.px_y,reason=VISUAL_NONE[67])); continue
    if no==9: continue  # special below
    atree=cKDTree(acc[['px_x','px_y']].values)
    idx=atree.query_ball_point([r.px_x,r.px_y],5.0)
    same=[j for j in idx if int(acc.leg_no.values[j])==no]
    if same: continue
    cc=cand_by[no]
    near=cc[(np.hypot(cc.px_x-r.px_x,cc.px_y-r.px_y)<=6.0)&(cc.dmean<=G+15)]
    b=near.loc[near.score.idxmax()] if len(near) else None
    floor=0.55 if mode in ('scan','group') else 0.50
    if idx:
        j=idx[np.argmin([np.hypot(acc.px_x.values[k]-r.px_x,acc.px_y.values[k]-r.px_y) for k in idx])]
        if b is not None and b.score>=max(0.55,acc.score.values[j]-0.10):
            acc.at[j,'leg_no']=no; acc.at[j,'old_fid']=fid; acc.at[j,'label_src']='old-table-neartie'; matched_fids.add(fid)
        else:
            contested.append(dict(fid=fid,leg_no=no,mineral=r.mineral,px_x=r.px_x,px_y=r.px_y,accepted_as=int(acc.leg_no.values[j]),acc_score=round(float(acc.score.values[j]),2),own_best_score=round(float(b.score),2) if b is not None else None))
        continue
    if b is not None and b.score>=floor:
        rescued.append(dict(leg_no=no,px_x=b.px_x,px_y=b.px_y,score=b.score,dmean=b.dmean,mode=mode,det_src='RESCUE_RECENTRED',label_src='old',old_fid=fid,margin=np.nan))
    elif mode in ('rescue','grouplabel','group'):
        rescued.append(dict(leg_no=no,px_x=r.px_x,px_y=r.px_y,score=np.nan,dmean=np.nan,mode=mode,det_src='OLD_CENTRE_KEPT',label_src='old',old_fid=fid,margin=np.nan))
    else:
        unverified.append(dict(fid=fid,leg_no=no,mineral=r.mineral,px_x=r.px_x,px_y=r.px_y,reason=f'no template candidate >={floor} within 6px'))
if rescued:
    rr=pd.DataFrame(rescued).sort_values('score',ascending=False,na_position='last')
    taken=list(acc[['px_x','px_y']].values); keep=[]
    for _,x in rr.iterrows():
        if all((x.px_x-a[0])**2+(x.px_y-a[1])**2>=25 for a in taken):
            keep.append(x); taken.append([x.px_x,x.px_y])
        elif x.det_src=='OLD_CENTRE_KEPT':
            unverified.append(dict(fid=int(x.old_fid),leg_no=int(x.leg_no),mineral=leg.loc[x.leg_no,'point_attribute_name'],px_x=x.px_x,px_y=x.px_y,reason='old-centre rescue collided with accepted detection'))
    if keep: acc=pd.concat([acc,pd.DataFrame(keep)],ignore_index=True)
# Brick Clay special: fid474 sits on Calcite disc -> unverified; fid1396 -> nearest Diatomite-class detection/candidate within 8px
for _,r in rescue_pool[rescue_pool.leg_no==9].iterrows():
    fid=int(r.fid)
    if fid==474:
        unverified.append(dict(fid=fid,leg_no=9,mineral='Brick Clay',px_x=r.px_x,px_y=r.px_y,reason='old point sits on a Calcite disc glyph (now a Calcite point)')); continue
    atree=cKDTree(acc[['px_x','px_y']].values)
    idx=[j for j in atree.query_ball_point([r.px_x,r.px_y],8.0) if int(acc.leg_no.values[j])==17]
    if idx:
        j=idx[0]; acc.at[j,'leg_no']=9; acc.at[j,'old_fid']=fid; acc.at[j,'label_src']='old-table (green-rect glyph, Brick Clay vs Diatomite ambiguous)'
    else:
        unverified.append(dict(fid=fid,leg_no=9,mineral='Brick Clay',px_x=r.px_x,px_y=r.px_y,reason='no green-rect glyph detection within 8px'))
print("final",len(acc),"unverified",len(unverified),"contested",len(contested))
acc['mineral']=[leg.loc[int(n),'point_attribute_name'] for n in acc.leg_no]
acc['commodity']=[leg.loc[int(n),'commodity_group'] for n in acc.leg_no]
ll=[min_basepx_to_lonlat(x,y) for x,y in zip(acc.px_x,acc.px_y)]
acc['lon']=[a for a,b in ll]; acc['lat']=[b for a,b in ll]
acc=acc.sort_values(['leg_no','px_y','px_x']).reset_index(drop=True)
acc.to_csv("work/points_v3.csv",index=False)
pd.DataFrame(unverified).to_csv("work/unverified_old_v3.csv",index=False)
pd.DataFrame(contested).to_csv("work/contested_old_v3.csv",index=False)
pd.DataFrame([dict(leg_no=k,T=v[0],G=v[1],mode=v[2]) for k,v in CFG.items()]).to_csv("work/class_config_v3.csv",index=False)
summ=acc.groupby('leg_no').size().rename('n_new')
old=rescue_pool.groupby('leg_no').size().rename('n_old')
tab=pd.DataFrame(index=range(1,68)).join(summ).join(old)
tab['mineral']=[leg.loc[i,'point_attribute_name'] for i in tab.index]
tab['mode']=[CFG[i][2] for i in tab.index]
print(tab.to_string()); print(acc.groupby('det_src').size()); print(acc.groupby('label_src').size())
