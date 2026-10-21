import cv2, numpy as np, json, pickle, sys
import geopandas as gpd, pandas as pd
from shapely.geometry import Point
sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)  # BGR
BH,BW=base.shape[:2]
meta=json.load(open('work/min/selftpl_meta.json'))
legcsv=pd.read_csv('work/min/mineral_legend.csv')
name_by_leg=dict(zip(legcsv.legend_no,legcsv.point_attribute_name))
grp_by_leg=dict(zip(legcsv.legend_no,legcsv.commodity_group))
g=pickle.load(open('work/min/minerals_final_v3.pkl','rb'))
print("start:",len(g))
TPL={}
def tpl(leg,dirn='selftpl4'):
    k=(leg,dirn)
    if k not in TPL:
        t=cv2.imread(f'work/min/{dirn}/leg{leg:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/{dirn}/leg{leg:02d}_mask.png',0).astype(np.float32)/255
        TPL[k]=(t,m)
    return TPL[k]
def peak_near(leg,cx,cy,R=3,dirn='selftpl4',t=None,m=None,cc=None):
    if t is None: t,m=tpl(leg,dirn)
    if cc is None: cc=meta[str(leg)]['center_xy']
    ccx,ccy=cc
    WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return (0.0,cx,cy)
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    ccx2=xx+x0+ccx; ccy2=yy+y0+ccy
    ncc=np.where(np.hypot(ccx2-cx,ccy2-cy)<=R,ncc,-1)
    i=np.argmax(ncc); y,x=np.unravel_index(i,ncc.shape)
    return float(ncc.ravel()[i]), float(x+x0+ccx), float(y+y0+ccy)

# ---------- leg62 rebuild from legend template at Tr numbers ----------
g=g[g.leg_no!=62].copy()
S=pickle.load(open('work/min/link_stage3_v2.pkl','rb'))
num_state=S['num_state']
tab=pd.read_pickle('work/min/tables_final.pkl')
rows_by_key={}
for _,r in tab.iterrows(): rows_by_key.setdefault((r.zone,int(r.link_num)),[]).append(r)
lt=cv2.imread('work/min/templates/leg62.png').astype(np.float32)
lm=cv2.imread('work/min/templates/leg62_mask.png',0).astype(np.float32)/255
def px2ll(px,py):
    return 0.0063408528*(px*0.959996+74.2397)+1.999778, -0.0063497677*(py*0.959996+358.724)+16.326633
cands=[]
for ns in num_state:
    if ns['expected'].get(62,0)>0:
        n=ns['num']
        best=(-1,None,None)
        for s in [0.6,0.7,0.8,0.9]:
            t2,m2=scale_tpl(lt,lm,s)
            by,bx=np.where(m2>0); cc=((bx.min()+bx.max())/2,(by.min()+by.max())/2)
            v,x,y=peak_near(62,n['px'],n['py'],R=30,t=t2,m=m2,cc=cc)
            if v>best[0]: best=(v,(x,y),s)
        cands.append((ns['key'],best))
        print("Tr number",ns['key'],"best",round(best[0],2),best[1],"s",best[2])
newrows=[]
for key,(v,xy,s) in cands:
    if v>=0.85 and xy:
        x,y=xy; lon,lat=px2ll(x,y)
        rows=rows_by_key.get(key,[])
        newrows.append({'leg_no':62,'mineral':name_by_leg[62],'comm_grp':grp_by_leg[62],'id_score':round(v,3),
                        'stage':'2trona','px_x':round(x,2),'px_y':round(y,2),'near_num':f"{key[0]}{key[1]}",
                        'locality':rows[0].locality if rows else '','table_code':'.'.join(rows[0].codes_list) if rows else '',
                        'link_type':'table row at its number','lon':lon,'lat':lat,'geometry':Point(lon,lat)})
print("leg62 rebuilt points:",len(newrows))
if newrows:
    g=pd.concat([g,pd.DataFrame(newrows)],ignore_index=True)

# ---------- CC compactness filters for 6,25,26 ----------
baseu=cv2.imread('work/min/mineral_base.png')  # BGR uint8
gray=cv2.cvtColor(baseu,cv2.COLOR_BGR2GRAY)
Bch,Gch,Rch=baseu[:,:,0].astype(int),baseu[:,:,1].astype(int),baseu[:,:,2].astype(int)
yellow=((Rch>175)&(Gch>155)&(Bch<115)).astype(np.uint8)
dark=(gray<95).astype(np.uint8)
def cc_check(mask_img,cx,cy,maxw,maxh,minw=0,minh=0,central=False):
    x,y=int(round(cx)),int(round(cy))
    x0,y0=max(0,x-11),max(0,y-11); x1,y1=min(BW,x+12),min(BH,y+12)
    sub=mask_img[y0:y1,x0:x1]
    n,lab,stats,cent=cv2.connectedComponentsWithStats(sub,8)
    # component nearest to centre within 2px
    best=None
    for dy in range(-2,3):
        for dx in range(-2,3):
            xx,yy=x-x0+dx,y-y0+dy
            if 0<=xx<sub.shape[1] and 0<=yy<sub.shape[0] and lab[yy,xx]>0:
                best=lab[yy,xx]; break
        if best: break
    if best is None: return False
    X,Y,W,H,A=stats[best]
    if W>maxw or H>maxh or W<minw or H<minh: return False
    if X==0 or Y==0 or X+W>=sub.shape[1] or Y+H>=sub.shape[0]: return False  # touches window edge -> big blob
    if central:
        relx=(x-x0-X)/max(W,1); rely=(y-y0-Y)/max(H,1)
        if not (0.2<=relx<=0.8 and 0.2<=rely<=0.8): return False
    return True
drop=[]
for i,r in g.iterrows():
    if r.leg_no==6:
        if not cc_check(dark,r.px_x,r.px_y,9,10): drop.append(i)
    elif r.leg_no==25:
        if not cc_check(yellow,r.px_x,r.px_y,11,11,central=True): drop.append(i)
    elif r.leg_no==26:
        if not cc_check(yellow,r.px_x,r.px_y,12,12,minw=7,minh=7,central=True): drop.append(i)
print("CC-filter drops:",len(drop), "by leg:", pd.Series(g.loc[drop,'leg_no']).value_counts().to_dict() if drop else {})
g=g.drop(index=drop).copy()

# ---------- rescue uncovered old points ----------
old=gpd.read_file('shapefile_results/minerals/nigeria_mineral_symbols.shp')
from scipy.spatial import cKDTree
tree=cKDTree(np.stack([g.px_x.values,g.px_y.values],axis=1))
d,_=tree.query(np.stack([old.px_x.values,old.px_y.values],axis=1))
unc=old[d>8]
print("rescue candidates:",len(unc))
LEGS=[L for L in range(1,68) if L not in (49,62,53)]
rescued=[]
existing=[(x,y) for x,y in zip(g.px_x,g.px_y)]
for _,r in unc.iterrows():
    best=(-1,None,None)
    for L in LEGS:
        v,x,y=peak_near(L,float(r.px_x),float(r.px_y),R=3)
        if v>best[0]: best=(v,L,(x,y))
    v,L,xy=best
    if v>=0.90 and xy:
        x,y=xy
        if any((x-ex)**2+(y-ey)**2<36 for ex,ey in existing): continue
        lon,lat=px2ll(x,y)
        rescued.append({'leg_no':L,'mineral':name_by_leg.get(L,''),'comm_grp':grp_by_leg.get(L,''),
                        'id_score':round(v,3),'stage':'4audit','px_x':round(x,2),'px_y':round(y,2),
                        'near_num':str(r.near_num) if isinstance(r.near_num,str) else '','locality':str(r.locality) if isinstance(r.locality,str) else '',
                        'table_code':str(r.table_code) if isinstance(r.table_code,str) else '',
                        'link_type':'audit rescue (previous extract, template-verified)','lon':lon,'lat':lat,'geometry':Point(lon,lat)})
        existing.append((x,y))
print("rescued:",len(rescued))
if rescued:
    g=pd.concat([g,pd.DataFrame(rescued)],ignore_index=True)
g=g.reset_index(drop=True); g['fid']=range(1,len(g)+1)
print("FINAL v4 points:",len(g))
print(g.leg_no.value_counts().sort_index().to_string())
print("stages:",g.stage.value_counts().to_dict())
g.to_pickle('work/min/minerals_final_v4.pkl')
g.to_file('work/min/minerals_v4.shp')
# coverage again
tree=cKDTree(np.stack([g.px_x.values,g.px_y.values],axis=1))
d,_=tree.query(np.stack([old.px_x.values,old.px_y.values],axis=1))
print("old coverage <=8px now:",round(float((d<=8).mean())*100,1),"%")
