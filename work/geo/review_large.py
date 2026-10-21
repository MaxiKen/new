import geopandas as gpd, numpy as np, shapely, json, warnings, pickle
import pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

geo=gpd.read_file('shapefile_results/geology/nigeria_geology_units.shp')
d=pickle.load(open('work/geo/faces.pkl','rb')); faces=d['faces']
a=pickle.load(open('work/geo/assign_final.pkl','rb')); assign=a['assign']; method=a['method']
face_cands=pickle.load(open('work/geo/face_cands.pkl','rb'))
areas=np.array([f.area for f in faces])
tr=json.load(open('work/geo/geology_transform.json'))
A,B=tr['lon_coef']; C,D=tr['lat_coef']
img=np.asarray(Image.open('work/geo/geology_native.png').convert('RGB')).astype(int)
H,W=img.shape[:2]
def sample_color2(poly):
    minx,miny,maxx,maxy=poly.bounds
    # erode slightly to avoid boundary lines when possible
    er=poly.buffer(-0.003)
    use=er if (not er.is_empty and er.area>0.2*poly.area) else poly
    pts=[]
    n=25
    for i in range(n):
        for j in range(n):
            p=shapely.Point(minx+(maxx-minx)*(i+0.5)/n, miny+(maxy-miny)*(j+0.5)/n)
            if use.contains(p): pts.append(p)
    if len(pts)<5:
        pts=[poly.representative_point()]
    cols=[]
    for p in pts:
        px=int((p.x-B)/A); py=int((p.y-D)/C)
        if 1<=px<W-1 and 1<=py<H-1: cols.append(img[py,px])
    cols=np.array(cols)
    # drop near-black (lines/text) and very dark blue text? keep water blue (bright). drop max<70
    keep=cols.max(axis=1)>70
    if keep.sum()>=3: cols=cols[keep]
    return np.median(cols,axis=0), len(cols)

def hexrgb(h): return np.array([int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)],dtype=float)
fills={j:hexrgb(h) for j,h in enumerate(geo['fill']) if isinstance(h,str)}

log=pd.read_csv('work/geo/gap_assignment_log.csv')
# adjacency recompute quickly for gap candidates border lengths (only for needed faces)
from shapely import STRtree
ftree=STRtree(faces)
def neighbor_per(i):
    f=faces[i]; per={}
    for j in ftree.query(f):
        if j==i: continue
        L=f.boundary.intersection(faces[j].boundary).length
        if L>1e-12 and assign[j]>=0: per[assign[j]]=per.get(assign[j],0)+L
    return per

rows=[]
targets=log[(log.area_km2>=20)]
for _,r in targets.iterrows():
    i=int(r.face); f=faces[i]
    if r.kind=='gap':
        per=neighbor_per(i); cand=list(per.keys())
    else:
        cand=[j for j,c in face_cands.get(i,[]) if c>=0.99]; per={j:0 for j in cand}
    units={geo.unit.iloc[j] for j in cand}
    col,n=sample_color2(f)
    dists={j: float(np.linalg.norm(col-fills[j])) if j in fills else 999 for j in cand}
    color_win=min(dists, key=dists.get) if dists else -1
    rows.append({'face':i,'area_km2':r.area_km2,'kind':r.kind,'method_used':r.method,
                 'assigned':int(assign[i]),'assigned_unit':geo.unit.iloc[assign[i]],
                 'color_win':int(color_win),'color_win_unit':geo.unit.iloc[color_win],
                 'sample_rgb':str([int(v) for v in col]),'n':n,
                 'dist_assigned':round(dists.get(int(assign[i]),999),1),'dist_colorwin':round(dists.get(int(color_win),999),1),
                 'n_cand_units':len(units),
                 'detail':'; '.join(f"{j}:{geo.unit.iloc[j][:20]} d={dists[j]:.0f} bord={per.get(j,0):.3f}" for j in cand)})
rv=pd.DataFrame(rows).sort_values('area_km2',ascending=False)
rv.to_csv('work/geo/review_large.csv',index=False)
pd.set_option('display.width',250)
print(rv[['face','area_km2','kind','method_used','assigned_unit','color_win_unit','dist_assigned','dist_colorwin','n_cand_units']].to_string())
print("\n--- disagreements (assigned unit != color-win unit) ---")
dis=rv[rv.assigned_unit!=rv.color_win_unit]
for _,r in dis.iterrows():
    print(f"face{r.face} {r.area_km2}km2 {r.kind} assigned={r.assigned_unit!r}(d={r.dist_assigned}) color={r.color_win_unit!r}(d={r.dist_colorwin}) rgb={r.sample_rgb}")
    print(f"   {r.detail}")
