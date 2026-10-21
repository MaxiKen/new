import geopandas as gpd, numpy as np, shapely, json, warnings, pickle
from shapely import STRtree
from PIL import Image
warnings.filterwarnings('ignore')

geo=gpd.read_file('shapefile_results/geology/nigeria_geology_units.shp')
geo['fid']=np.arange(len(geo))
d=pickle.load(open('work/geo/faces.pkl','rb')); faces=d['faces']; in_ref=d['in_ref']
areas=np.array([f.area for f in faces])
src_geoms=geo.geometry.values
tree=STRtree(src_geoms)

# raster sampler
tr=json.load(open('work/geo/geology_transform.json'))
A,B=tr['lon_coef']; C,D=tr['lat_coef']
img=np.asarray(Image.open('work/geo/geology_native.png').convert('RGB')).astype(int)
H,W=img.shape[:2]
def sample_color(poly, nmax=80):
    # sample points inside poly: rep point + bbox grid
    pts=[poly.representative_point()]
    minx,miny,maxx,maxy=poly.bounds
    stepx=(maxx-minx)/8; stepy=(maxy-miny)/8
    if stepx>0 and stepy>0:
        for i in range(1,8):
            for j in range(1,8):
                p=shapely.Point(minx+stepx*i, miny+stepy*j)
                if poly.contains(p): pts.append(p)
    cols=[]
    for p in pts[:nmax]:
        px=int((p.x-B)/A); py=int((p.y-D)/C)
        if 1<=px<W-1 and 1<=py<H-1:
            cols.append(img[py,px])
    if not cols: return None
    return np.median(np.array(cols),axis=0)

def hexrgb(h):
    try: return np.array([int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)],dtype=float)
    except: return None
fills=np.array([hexrgb(h) if isinstance(h,str) else None for h in geo['fill']], dtype=object)

# recompute candidate overlaps for multi-full faces
rows=[]
face_cands={}
for i,f in enumerate(faces):
    if not in_ref[i]: continue
    cand=tree.query(f)
    ovs=[]
    for j in cand:
        ov=f.intersection(src_geoms[j]).area
        if ov>1e-12: ovs.append((j,ov/f.area if f.area else 0))
    face_cands[i]=ovs
pickle.dump(face_cands, open('work/geo/face_cands.pkl','wb'))

multi=[i for i,ovs in face_cands.items() if sum(1 for _,c in ovs if c>=0.99)>=2]
print(f"multi-full-cover faces: {len(multi)}, area {areas[multi].sum()*12266:.0f} km2")
big=[i for i in multi if areas[i]*12266>=5]
print(f"  >=5km2: {len(big)}")
agree_seq=agree_minarea=agree_both=ntest=0
examples=[]
for i in big:
    f=faces[i]
    full=[j for j,c in face_cands[i] if c>=0.99]
    col=sample_color(f)
    if col is None: continue
    dists={}
    for j in full:
        if fills[j] is not None: dists[j]=np.linalg.norm(col-fills[j])
    if not dists: continue
    color_win=min(dists, key=dists.get)
    seq_win=max(full, key=lambda j: geo.src_seq.iloc[j])
    minarea_win=min(full, key=lambda j: geo.geometry.iloc[j].area)
    ntest+=1
    if color_win==seq_win: agree_seq+=1
    if color_win==minarea_win: agree_minarea+=1
    if len(examples)<12:
        examples.append((i, areas[i]*12266, [ (int(j), geo.unit.iloc[j][:26], geo.fill.iloc[j], int(geo.src_seq.iloc[j]), round(dists.get(j,-1),1)) for j in full], int(color_win), int(seq_win), int(minarea_win), col.round(0).tolist()))
print(f"tested {ntest}: color==max_src_seq {agree_seq} ({agree_seq/max(ntest,1):.2%}), color==min_area {agree_minarea} ({agree_minarea/max(ntest,1):.2%})")
for e in examples:
    print(f" face{e[0]} {e[1]:.0f}km2 sampledRGB={e[6]} color_win={e[3]} seq_win={e[4]} minarea_win={e[5]}")
    for j,u,fl,sq,dd in e[2]: print(f"    cand fid={j} unit={u!r} fill={fl} src_seq={sq} colordist={dd}")
