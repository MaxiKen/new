import cv2, numpy as np, json, pickle, sys
import pandas as pd, geopandas as gpd
from shapely.geometry import Point
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter, defaultdict

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
tab=pd.read_pickle('work/min/tables_final.pkl')
legcsv=pd.read_csv('work/min/mineral_legend.csv')
S=pickle.load(open('work/min/link_stage2_v4.pkl','rb'))
objs,num_state=S['objs'],S['num_state']
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':2,'Be':6,'Gm':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Sd':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ks':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Ms':44,'Mu':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'St':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67}
# --- last-chance fill (core mask, thr 0.55, R=42) ---
TPL={}
def get_tpl(leg,core=True):
    k=(leg,core)
    if k not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{leg:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{leg:02d}_mask.png',0).astype(np.float32)/255
        if core:
            ys,xs=np.where(m>0); vals=t[ys,xs]; mu=vals.mean(axis=0)
            contr=np.abs(vals-mu).max(axis=1); cut=np.percentile(contr,38)
            m2=np.zeros_like(m); keep=contr>=cut; m2[ys[keep],xs[keep]]=1
            if m2.sum()>=8: m=m2
        TPL[k]=(t,m)
    return TPL[k]
def window_peak(leg,nx,ny,R,exclude):
    t,m=get_tpl(leg); cx,cy=meta[str(leg)]['center_xy']
    WR=int(R+12)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+cx; ccy=yy+y0+cy
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.5)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return (float(x+x0+cx),float(y+y0+cy),v)
exclude=[(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]
cand=[]
for ni,ns in enumerate(num_state):
    for leg,c in ns['expected'].items():
        if leg==49: continue
        for _ in range(c-ns['filled'][leg]):
            r=window_peak(leg,ns['num']['px'],ns['num']['py'],42,exclude)
            if r and r[2]>=0.55: cand.append((-r[2],ni,leg,r))
cand.sort()
added=0
for negsc,ni,leg,r in cand:
    ns=num_state[ni]
    if ns['filled'][leg]>=ns['expected'][leg]: continue
    x,y,v=r
    if any(np.hypot(x-o['cx'],y-o['cy'])<=5.5 for o in objs if o['claimed_by'] is not None): continue
    objs.append({'cx':x,'cy':y,'scores':{leg:(v,-1)},'claimed_by':(ni,leg),'stage':'2last'})
    ns['filled'][leg]+=1; ns['objs'].append((len(objs)-1,leg)); added+=1
f=sum(sum(ns['filled'].values()) for ns in num_state); tot=sum(sum(ns['expected'].values()) for ns in num_state)
print(f"last-chance added {added}; filled {f}/{tot}")
unf=Counter()
for ns in num_state:
    for leg,c in ns['expected'].items():
        if ns['filled'][leg]<c: unf[leg]+=c-ns['filled'][leg]
print("still unfilled:",dict(sorted(unf.items())))

# --- stage3 sweep ---
num_pts=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
claimed_pts=[(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]
def dist_nearest(pt,arr):
    return float(np.sqrt(((arr-np.array(pt))**2).sum(axis=1)).min())
ACC={32:(0.965,48),6:(0.985,44),25:(0.97,44),30:(0.86,44),26:(0.97,60),12:(0.97,60)}
accepted=[]
for oi,o in enumerate(objs):
    if o['claimed_by'] is not None: continue
    leg=max(o['scores'],key=lambda L:o['scores'][L][0]); sc=o['scores'][leg][0]
    dclaim=min([np.hypot(o['cx']-x,o['cy']-y) for x,y in claimed_pts],default=999)
    if dclaim<6 and not (sc>=0.97): continue
    dnum=dist_nearest((o['cx'],o['cy']),num_pts)
    if leg in ACC:
        thr,md=ACC[leg]
        if sc>=thr and dnum<=md: accepted.append((oi,leg,sc))
    else:
        if sc>=0.93 or (sc>=0.88 and dnum<=44): accepted.append((oi,leg,sc))
print(f"stage3 accepted unnumbered: {len(accepted)}")
acc_by_leg=Counter(l for _,l,_ in accepted)
print(dict(sorted(acc_by_leg.items())))

# --- assemble final points ---
rows_by_key={}
for _,r in tab.iterrows():
    rows_by_key.setdefault((r.zone,int(r.link_num)),[]).append(r)
def px2ll(px,py):
    page_x=px*0.959996+74.2397; page_y=py*0.959996+358.724
    return 0.0063408528*page_x+1.999778, -0.0063497677*page_y+16.326633
name_by_leg=dict(zip(legcsv.legend_no,legcsv.point_attribute_name))
grp_by_leg=dict(zip(legcsv.legend_no,legcsv.commodity_group))
points=[]
def add_point(cx,cy,leg,score,stage,zone,num,locality,table_code,link_type):
    lon,lat=px2ll(cx,cy)
    points.append({'leg_no':leg,'mineral':name_by_leg.get(leg,''),'comm_grp':grp_by_leg.get(leg,''),
                   'id_score':round(float(score),3),'stage':str(stage),'px_x':round(float(cx),2),'px_y':round(float(cy),2),
                   'near_num':f"{zone}{num}" if zone else '','locality':locality or '','table_code':table_code or '',
                   'link_type':link_type,'lon':lon,'lat':lat,'geometry':Point(lon,lat)})
# claimed
for ni,ns in enumerate(num_state):
    n=ns['num']; key=(n['zone'],n['value'])
    rows=rows_by_key.get(key,[])
    for oi,leg in ns['objs']:
        o=objs[oi]; sc=o['scores'].get(leg,(0,))[0]
        # choose row whose codes map to leg
        chosen=None
        for r in rows:
            if leg in {CODE2LEG.get(c) for c in r.codes_list}: chosen=r; break
        if chosen is None and rows: chosen=rows[0]
        loc=chosen.locality if chosen is not None else ''
        codes='.'.join(chosen.codes_list) if chosen is not None else ''
        stage=o.get('stage',1)
        add_point(o['cx'],o['cy'],leg,sc,stage,n['zone'],n['value'],loc,codes,'table row at its number')
# unnumbered accepted
for oi,leg,sc in accepted:
    o=objs[oi]
    # nearest number
    d=np.sqrt(((num_pts-[o['cx'],o['cy']])**2).sum(axis=1))
    j=int(np.argmin(d))
    if d[j]<=48:
        n=num_state[j]['num']; rows=rows_by_key.get((n['zone'],n['value']),[])
        loc=rows[0].locality if rows else ''
        codes='.'.join(rows[0].codes_list) if rows else ''
        add_point(o['cx'],o['cy'],leg,sc,3,n['zone'],n['value'],loc,codes,'nearest number (extra/unnumbered symbol)')
    else:
        add_point(o['cx'],o['cy'],leg,sc,3,'','','','','no number within 48px')
gdf=gpd.GeoDataFrame(points,crs='EPSG:4326')
# global dedup <5px: keep claimed first (link_type table), then score
gdf['prio']=np.where(gdf.link_type=='table row at its number',0,1)
gdf=gdf.sort_values(['prio','id_score'],ascending=[True,False]).reset_index(drop=True)
keep=[]; kept=[]
for i,r in gdf.iterrows():
    if any((r.px_x-x)**2+(r.px_y-y)**2<25 for x,y in kept): continue
    keep.append(i); kept.append((r.px_x,r.px_y))
gdf=gdf.loc[keep].drop(columns='prio').reset_index(drop=True)
gdf.insert(0,'fid',range(1,len(gdf)+1))
print("FINAL points:",len(gdf))
print(gdf.leg_no.value_counts().sort_index().to_string())
gdf.to_pickle('work/min/minerals_final_v1.pkl')
gdf.to_file('work/min/minerals_v1.shp')
pickle.dump({'objs':objs,'num_state':num_state,'accepted':accepted},open('work/min/link_stage3.pkl','wb'))
