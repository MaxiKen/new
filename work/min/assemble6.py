import cv2, numpy as np, pickle, pandas as pd, geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import cKDTree
S=pickle.load(open('work/min/complete6o.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
tab=pd.read_pickle('work/min/tables_final.pkl')
legcsv=pd.read_csv('work/min/mineral_legend.csv')
name_by_leg=dict(zip(legcsv.legend_no,legcsv.point_attribute_name))
grp_by_leg=dict(zip(legcsv.legend_no,legcsv.commodity_group))
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':2,'Be':6,'Gm':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Sd':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ks':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Ms':44,'Mu':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'St':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67}
rows_by_key={}
for _,r in tab.iterrows(): rows_by_key.setdefault((r.zone,int(r.link_num)),[]).append(r)
def px2ll(px,py):
    return 0.0063408528*(px*0.959996+74.2397)+1.999778, -0.0063497677*(py*0.959996+358.724)+16.326633
def row_for(key,leg):
    rows=rows_by_key.get(key,[])
    for r in rows:
        if leg in {CODE2LEG.get(c) for c in r.codes_list}: return r
    return rows[0] if rows else None
num_xy=np.array([[ns['num']['px'],ns['num']['py']] for ns in num_state])
tree=cKDTree(num_xy)
out=[]
for p in pts:
    lon,lat=px2ll(p['cx'],p['cy'])
    if 'num_idx' in p:
        ns=num_state[p['num_idx']]; key=ns['key']
        r=row_for(key,p['leg'])
        near=f"{key[0]}{key[1]}"; loc=r.locality if r is not None else ''
        code='.'.join(r.codes_list) if r is not None else ''
        lt='table row at its number'
    else:
        d,j=tree.query([p['cx'],p['cy']])
        if d<=48:
            ns=num_state[j]; key=ns['key']; r=row_for(key,p['leg'])
            near=f"{key[0]}{key[1]}"; loc=r.locality if r is not None else ''
            code='.'.join(r.codes_list) if r is not None else ''
            lt='nearest number (extra symbol)'
        else:
            near=''; loc=''; code=''; lt='no number within 48px'
    out.append({'leg_no':p['leg'],'mineral':name_by_leg.get(p['leg'],''),'comm_grp':grp_by_leg.get(p['leg'],''),
                'table_code':code,'locality':loc or '','near_num':near,'id_score':round(float(p['score']),3),
                'match_type':p['match_type'],'vis_part':p.get('vis_part',''),'px_x':round(float(p['cx']),2),
                'px_y':round(float(p['cy']),2),'lon':round(float(lon),6),'lat':round(float(lat),6),
                'link_type':lt,'geometry':Point(lon,lat)})
g=gpd.GeoDataFrame(out,crs='EPSG:4326')
g=g.sort_values(['leg_no','near_num','locality']).reset_index(drop=True)
g.insert(0,'fid',range(1,len(g)+1))
print("FINAL v6 points:",len(g))
print(g.match_type.value_counts().to_dict(), g.link_type.value_counts().to_dict())
print(g.leg_no.value_counts().sort_index().to_string())
g.to_file('deliverables_flat/nigeria_mineral_occurrences.shp')
g.to_pickle('work/min/minerals_final_v6.pkl')
# old-extract coverage for README
old=gpd.read_file('shapefile_results/minerals/nigeria_mineral_symbols.shp')
d,_=cKDTree(np.stack([g.px_x.values,g.px_y.values],axis=1)).query(np.stack([old.px_x.values,old.px_y.values],axis=1))
for R in (4,8): print(f"old points with new point within {R}px: {(d<=R).mean()*100:.1f}%")
# legend counts update
leg=pd.read_csv('deliverables_flat/mineral_legend.csv')
cnt=g.leg_no.value_counts()
leg['occurrences_in_dataset']=leg.legend_no.map(cnt).fillna(0).astype(int)
leg.to_csv('deliverables_flat/mineral_legend.csv',index=False)
# QA overlays + sample montage
base=cv2.imread('work/min/mineral_base.png')
def crop_qa(name,cx,cy,half=170):
    x0,y0=max(0,cx-half),max(0,cy-half); x1,y1=cx+half,cy+half
    img=base[y0:y1,x0:x1].copy()
    for _,r in old.iterrows():
        if x0<=r.px_x<x1 and y0<=r.px_y<y1: cv2.circle(img,(int(r.px_x-x0),int(r.px_y-y0)),5,(170,170,170),1)
    for _,r in g.iterrows():
        if x0<=r.px_x<x1 and y0<=r.px_y<y1:
            cv2.drawMarker(img,(int(r.px_x-x0),int(r.px_y-y0)),(0,0,255),cv2.MARKER_CROSS,7,1)
            cv2.putText(img,str(int(r.leg_no)),(int(r.px_x-x0)+4,int(r.px_y-y0)-3),cv2.FONT_HERSHEY_SIMPLEX,0.34,(0,0,255),1)
    cv2.imwrite(f'work/qa/v6final_{name}.png',cv2.resize(img,None,fx=2.6,fy=2.6,interpolation=cv2.INTER_NEAREST))
crop_qa('jos',1225,676); crop_qa('sw',448,1123); crop_qa('sokoto',448,254); crop_qa('ne',1754,364)
import random
random.seed(11)
low=g[g.id_score<0.90]
sel=g.sample(18,random_state=3)
if len(low)>=10: sel=pd.concat([sel,low.sample(10,random_state=5)])
cells=[]
for _,r in sel.iterrows():
    x,y=int(round(r.px_x)),int(round(r.px_y))
    win=np.full((29,29,3),255,np.uint8)
    src=base[max(0,y-14):y+15,max(0,x-14):x+15]
    win[14-(y-max(0,y-14)):14-(y-max(0,y-14))+src.shape[0],14-(x-max(0,x-14)):14-(x-max(0,x-14))+src.shape[1]]=src
    cv2.drawMarker(win,(14,14),(0,0,255),cv2.MARKER_CROSS,7,1)
    cv2.putText(win,f"L{int(r.leg_no)} {r.id_score:.2f}",(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.34,(0,0,255),1)
    cells.append(cv2.resize(win,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST))
H=cells[0].shape[0]; W=cells[0].shape[1]; cols=7
rows=(len(cells)+cols-1)//cols
canvas=np.full((H*rows,W*cols,3),255,np.uint8)
for i,c in enumerate(cells):
    rr,cc=divmod(i,cols); canvas[rr*H:(rr+1)*H,cc*W:(cc+1)*W]=c
cv2.imwrite('work/qa/v6final_sample.png',canvas)
print("QA saved")
