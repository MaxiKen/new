import geopandas as gpd, numpy as np, shapely, json, warnings, pickle, cv2
import pandas as pd
from shapely import STRtree
from shapely.ops import unary_union
from PIL import Image
from scipy import ndimage
from rasterio import features as rio_features
from rasterio.transform import Affine
warnings.filterwarnings('ignore')
KM2=12266.0

geo=gpd.read_file('shapefile_results/geology/nigeria_geology_units.shp')
d=pickle.load(open('work/geo/faces.pkl','rb')); faces=list(d['faces']); in_ref=d['in_ref']
a=pickle.load(open('work/geo/assign_final.pkl','rb')); assign=list(a['assign']); method=list(a['method'])
areas=np.array([f.area for f in faces])
tr=json.load(open('work/geo/geology_transform.json'))
A,B=tr['lon_coef']; C,D=tr['lat_coef']
img=np.asarray(Image.open('work/geo/geology_native.png').convert('RGB')).astype(float)
H,W=img.shape[:2]
def hexrgb(h): return np.array([int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)],dtype=float)
fills={j:hexrgb(h) for j,h in enumerate(geo['fill']) if isinstance(h,str)}

ftree=STRtree(faces)
def neighbor_per(i):
    f=faces[i]; per={}
    for j in ftree.query(f):
        if j==i: continue
        L=f.boundary.intersection(faces[j].boundary).length
        if L>1e-12 and assign[j]>=0: per[assign[j]]=per.get(assign[j],0)+L
    return per

# candidate donor face lists per feature (current assigned faces)
from collections import defaultdict
feat_faces=defaultdict(list)
for idx,fd in enumerate(assign):
    if fd>=0 and in_ref[idx]: feat_faces[int(fd)].append(idx)

targets=[]
for i in range(len(faces)):
    if not in_ref[i] or method[i]!='gap_border': continue
    if areas[i]*KM2<20: continue
    per=neighbor_per(i)
    units={geo.unit.iloc[j] for j in per}
    if len(units)>=2: targets.append((i,per))
print(f"split targets: {len(targets)} faces, total {sum(areas[i] for i,_ in targets)*KM2:.0f} km2")

log=[]
RES=0.0015
for i,per in targets:
    f=faces[i]; cands=sorted(per.keys())
    minx,miny,maxx,maxy=f.bounds
    # expand bbox a bit for donor proximity context
    pad=0.06
    gx0,gx1,gy0,gy1=minx-pad,maxx+pad,miny-pad,maxy+pad
    nx=int(np.ceil((gx1-gx0)/RES)); ny=int(np.ceil((gy1-gy0)/RES))
    transform=Affine(RES,0,gx0,0,-RES,gy1)
    mask=rio_features.geometry_mask([f], out_shape=(ny,nx), transform=transform, invert=True)
    # pixel centers
    cols=np.arange(nx); rows=np.arange(ny)
    lons=gx0+(cols+0.5)*RES; lats=gy1-(rows+0.5)*RES
    # raster colors
    px=np.clip(((lons-B)/A).astype(int),0,W-1); py=np.clip(((lats-D)/C).astype(int),0,H-1)
    colimg=img[np.ix_(py,px)]  # ny,nx,3
    # donor distance (EDT to donor's current faces rasterized)
    dists=[]; 
    for j in cands:
        donor_geoms=[faces[k] for k in feat_faces[j]]
        dm=rio_features.geometry_mask(donor_geoms, out_shape=(ny,nx), transform=transform, invert=True)
        dist=ndimage.distance_transform_edt(~dm)
        dists.append(dist)
    dists=np.stack(dists)  # ncand,ny,nx
    near=np.argmin(dists,axis=0)
    # color evidence per fill group
    fill_list=[]
    for j in cands:
        fl=geo.fill.iloc[j]
        if fl not in fill_list: fill_list.append(fl)
    farr=np.stack([hexrgb(fl) for fl in fill_list])  # nf,3
    # distance to each fill: (ny,nx,nf)
    dif=colimg[:,:,None,:]-farr[None,None,:,:]
    cdist=np.sqrt((dif**2).sum(axis=3))
    bestf=np.argmin(cdist,axis=2); bestd=np.min(cdist,axis=2)
    white=(colimg>238).all(axis=2); black=(colimg.max(axis=2)<60)
    evid=(bestd<45)&(~white)&(~black)&mask
    # final label: start nearest; where evidence, restrict to cands with best fill then nearest among them
    lab=near.copy()
    cand_fill_idx=np.array([fill_list.index(geo.fill.iloc[j]) for j in cands])
    for fi in range(len(fill_list)):
        idxs=np.where(cand_fill_idx==fi)[0]
        if len(idxs)==0: continue
        sub_near=np.argmin(dists[idxs],axis=0)
        chosen=idxs[sub_near]
        sel=evid&(bestf==fi)
        lab[sel]=chosen[sel]
    lab_u8=np.where(mask, lab+1, 0).astype(np.uint8)
    lab_u8=cv2.medianBlur(lab_u8,3)
    lab_u8=np.where(mask, lab_u8, 0)
    # polygonize
    parts=[]
    for geom,val in rio_features.shapes(lab_u8, mask=mask, transform=transform):
        if val==0: continue
        g=shapely.geometry.shape(geom).intersection(f)
        if g.is_empty: continue
        # explode
        polys=[g] if g.geom_type=='Polygon' else list(g.geoms) if hasattr(g,'geoms') else []
        for p in polys:
            if p.area*KM2>=0.3: parts.append((p, cands[int(val)-1]))
    covered=unary_union([p for p,_ in parts]) if parts else shapely.Polygon()
    resid=f.difference(covered)
    main=max(per, key=per.get)
    resid_polys=[]
    if not resid.is_empty:
        resid_polys=[resid] if resid.geom_type=='Polygon' else [g for g in resid.geoms if g.geom_type=='Polygon']
    # apply: supersede original face
    assign[i]=-2; method[i]='superseded_split'
    per_new={}
    for p,j in parts:
        faces.append(p); assign.append(int(j)); method.append('gap_split')
        per_new[j]=per_new.get(j,0)+p.area*KM2
    for p in resid_polys:
        if p.area<=0: continue
        faces.append(p); assign.append(int(main)); method.append('gap_split_resid')
        per_new[main]=per_new.get(main,0)+p.area*KM2
    print(f" face{i} {areas[i]*KM2:.0f}km2 old->{main}:{geo.unit.iloc[main][:22]!r}  new split: "+
          ", ".join(f"{j}:{geo.unit.iloc[j][:22]}={v:.0f}km2" for j,v in sorted(per_new.items(),key=lambda kv:-kv[1])))
    log.append({'face':i,'area_km2':round(float(areas[i]*KM2),1),'old_fid':int(main),
                'new':';'.join(f"{j}={v:.0f}" for j,v in per_new.items())})

pd.DataFrame(log).to_csv('work/geo/split_log.csv',index=False)
faces_arr=np.array(faces,dtype=object)
in_ref2=np.concatenate([in_ref, np.ones(len(faces)-len(in_ref),dtype=bool)])
pickle.dump({'faces':faces_arr,'in_ref':in_ref2}, open('work/geo/faces_final.pkl','wb'))
pickle.dump({'assign':np.array(assign),'method':np.array(method,dtype=object)}, open('work/geo/assign_final2.pkl','wb'))
print(f"\ntotal faces now {len(faces)} (superseded {sum(1 for m in method if m=='superseded_split')})")
