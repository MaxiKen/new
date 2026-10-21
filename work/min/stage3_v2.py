import cv2, numpy as np, json, pickle, sys
import pandas as pd, geopandas as gpd
from shapely.geometry import Point
sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl
from collections import Counter

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
tab=pd.read_pickle('work/min/tables_final.pkl')
legcsv=pd.read_csv('work/min/mineral_legend.csv')
S=pickle.load(open('work/min/link_stage2b.pkl','rb'))
objs,num_state=S['objs'],S['num_state']
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':2,'Be':6,'Gm':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Sd':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ks':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Ms':44,'Mu':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'St':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67}

# partial claims QA gate
psc=[o['scores'][o['claimed_by'][1]][0] for o in objs if o.get('stage')=='2partial']
print("2partial score pct:", {p:round(float(np.percentile(psc,p)),2) for p in [5,25,50,75,95]} if psc else None)
# drop weak partials (<0.68)
dropped=0
for o in objs:
    if o.get('stage')=='2partial' and o['claimed_by'] is not None:
        ni,leg=o['claimed_by']
        if o['scores'][leg][0]<0.68:
            num_state[ni]['filled'][leg]-=1
            num_state[ni]['objs']=[t for t in num_state[ni]['objs'] if not (t[0]==objs.index(o) if False else False)]
            o['claimed_by']=None; dropped+=1
# fix num_state objs lists after drops (rebuild)
for ns in num_state: ns['objs']=[]
for oi,o in enumerate(objs):
    if o['claimed_by'] is not None:
        ni,leg=o['claimed_by']; num_state[ni]['objs'].append((oi,leg))
print("dropped weak partials:",dropped)

# --- revert leg53 claims; rebuild Na template from C8 glyph ---
for oi,o in enumerate(objs):
    if o['claimed_by'] is not None and o['claimed_by'][1]==53:
        ni=o['claimed_by'][0]
        num_state[ni]['filled'][53]-=1
        o['claimed_by']=None
for ns in num_state: ns['objs']=[t for t in ns['objs'] if objs[t[0]]['claimed_by'] is not None]
# seed patch at C8 glyph
seed_c=(1527.5,187.5)
def extract(cx,cy,half=8):
    x0,y0=int(round(cx))-half,int(round(cy))-half
    return base[y0:y0+2*half+1,x0:x0+2*half+1].copy(),x0,y0
seed_patch,_,_=extract(*seed_c)
# circular mask r=6 on 17x17
mm=np.zeros((17,17),np.float32); cv2.circle(mm,(8,8),6,1,-1)
# find instances near Na numbers
na_centers=[seed_c]
for ns in num_state:
    if ns['expected'].get(53,0)>0:
        n=ns['num']
        if abs(n['px']-seed_c[0])<40 and abs(n['py']-seed_c[1])<40: continue
        x0,y0=int(max(0,n['px']-45)),int(max(0,n['py']-45))
        win=base[y0:int(n['py']+45),x0:int(n['px']+45)]
        if win.shape[0]<18 or win.shape[1]<18: continue
        ncc=masked_ncc(win,seed_patch,mm)
        i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
        cx,cy=x+x0+8,y+y0+8
        if v>=0.72 and np.hypot(cx-n['px'],cy-n['py'])<=34:
            na_centers.append((float(cx),float(cy)))
print("Na candidate centers:",na_centers)
patches=[]
for cx,cy in na_centers:
    p,_,_=extract(cx,cy); patches.append(p)
na_tpl=np.median(np.stack(patches),axis=0) if len(patches)>1 else seed_patch
cv2.imwrite('work/min/selftpl4/leg53.png',np.clip(na_tpl,0,255).astype(np.uint8))
cv2.imwrite('work/min/selftpl4/leg53_mask.png',(mm*255).astype(np.uint8))
# gypsum template for discrimination
gy_t=cv2.imread('work/min/selftpl4/leg31.png').astype(np.float32)
gy_m=cv2.imread('work/min/selftpl4/leg31_mask.png',0).astype(np.float32)/255
gy_cx,gy_cy=meta['31']['center_xy']
def peak_score(t,m,cx0,cy0,nx,ny,R,exclude):
    WR=int(R+13)
    x0=int(max(0,nx-WR)); y0=int(max(0,ny-WR)); x1=int(min(BW,nx+WR)); y1=int(min(BH,ny+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return None
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx=xx+x0+cx0; ccy=yy+y0+cy0
    valid=np.hypot(ccx-nx,ccy-ny)<=R
    for (ex,ey) in exclude: valid&=(np.hypot(ccx-ex,ccy-ey)>5.5)
    ncc=np.where(valid,ncc,-1)
    i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
    return (float(x+x0+cx0),float(y+y0+cy0),v)
exclude=[(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]
na_added=0
for ni,ns in enumerate(num_state):
    for _ in range(ns['expected'].get(53,0)-ns['filled'][53]):
        n=ns['num']
        r=peak_score(na_tpl,mm,8,8,n['px'],n['py'],34,exclude)
        if r is None or r[2]<0.72: continue
        g=peak_score(gy_t,gy_m,gy_cx,gy_cy,r[0],r[1],3,[])
        if g and g[2]>r[2]+0.03: continue  # looks more like gypsum
        objs.append({'cx':r[0],'cy':r[1],'scores':{53:(r[2],-1)},'claimed_by':(ni,53),'stage':'2na'})
        ns['filled'][53]+=1; ns['objs'].append((len(objs)-1,53)); na_added+=1
        exclude.append((r[0],r[1]))
print("Na claims added:",na_added)

# --- sweep (tightened) ---
num_pts=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
claimed_pts=[(o['cx'],o['cy']) for o in objs if o['claimed_by'] is not None]
def d_nearest(pt,arr): return float(np.sqrt(((arr-np.array(pt))**2).sum(axis=1)).min())
ACC={32:(0.975,44),62:(0.97,44),6:(0.99,40),25:(0.985,40),30:(0.88,40),26:(0.97,60),12:(0.97,60)}
accepted=[]
for oi,o in enumerate(objs):
    if o['claimed_by'] is not None: continue
    leg=max(o['scores'],key=lambda L:o['scores'][L][0]); sc=o['scores'][leg][0]
    if leg==53: continue
    dclaim=min([np.hypot(o['cx']-x,o['cy']-y) for x,y in claimed_pts],default=999)
    if dclaim<6 and not (sc>=0.97): continue
    dnum=d_nearest((o['cx'],o['cy']),num_pts)
    if leg in ACC:
        thr,md=ACC[leg]
        if sc>=thr and dnum<=md: accepted.append((oi,leg,sc))
    else:
        if sc>=0.93 or (sc>=0.88 and dnum<=44): accepted.append((oi,leg,sc))
print("sweep accepted:",len(accepted),dict(sorted(Counter(l for _,l,_ in accepted).items())))

# --- assemble ---
rows_by_key={}
for _,r in tab.iterrows(): rows_by_key.setdefault((r.zone,int(r.link_num)),[]).append(r)
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
for ni,ns in enumerate(num_state):
    n=ns['num']; rows=rows_by_key.get((n['zone'],n['value']),[])
    for oi,leg in ns['objs']:
        o=objs[oi]; sc=o['scores'].get(leg,(0,))[0]
        chosen=None
        for r in rows:
            if leg in {CODE2LEG.get(c) for c in r.codes_list}: chosen=r; break
        if chosen is None and rows: chosen=rows[0]
        add_point(o['cx'],o['cy'],leg,sc,o.get('stage',1),n['zone'],n['value'],
                  chosen.locality if chosen is not None else '',
                  '.'.join(chosen.codes_list) if chosen is not None else '','table row at its number')
for oi,leg,sc in accepted:
    o=objs[oi]
    d=np.sqrt(((num_pts-[o['cx'],o['cy']])**2).sum(axis=1)); j=int(np.argmin(d))
    if d[j]<=48:
        n=num_state[j]['num']; rows=rows_by_key.get((n['zone'],n['value']),[])
        add_point(o['cx'],o['cy'],leg,sc,3,n['zone'],n['value'],rows[0].locality if rows else '',
                  '.'.join(rows[0].codes_list) if rows else '','nearest number (extra/unnumbered symbol)')
    else:
        add_point(o['cx'],o['cy'],leg,sc,3,'','','','','no number within 48px')
gdf=gpd.GeoDataFrame(points,crs='EPSG:4326')
gdf['prio']=np.where(gdf.link_type=='table row at its number',0,1)
gdf=gdf.sort_values(['prio','id_score'],ascending=[True,False]).reset_index(drop=True)
keep=[]; kept=[]
for i,r in gdf.iterrows():
    if any((r.px_x-x)**2+(r.px_y-y)**2<25 for x,y in kept): continue
    keep.append(i); kept.append((r.px_x,r.px_y))
gdf=gdf.loc[keep].drop(columns='prio').reset_index(drop=True)
gdf.insert(0,'fid',range(1,len(gdf)+1))
print("FINAL v2 points:",len(gdf))
print(gdf.leg_no.value_counts().sort_index().to_string())
print("by stage:",gdf.stage.value_counts().to_dict())
gdf.to_pickle('work/min/minerals_final_v2.pkl')
gdf.to_file('work/min/minerals_v2.shp')
pickle.dump({'objs':objs,'num_state':num_state,'accepted':accepted},open('work/min/link_stage3_v2.pkl','wb'))
unf=Counter()
for ns in num_state:
    for leg,c in ns['expected'].items():
        if ns['filled'][leg]<c: unf[leg]+=c-ns['filled'][leg]
print("unfilled final:",dict(sorted(unf.items())))
