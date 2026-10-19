import geopandas as gpd, numpy as np, pandas as pd
from PIL import Image
from shapely.geometry import Point
from shapely.strtree import STRtree
import warnings; warnings.filterwarnings('ignore')
geo=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp").geometry.iloc[0]
gaps=gpd.read_file("work/geology_gaps.geojson")
leg=pd.read_csv("shapefile_results/geology/geology_legend.csv")
img=np.array(Image.open("work/geology_native_full.jpg").convert("RGB")).astype(int)
def lonlat_to_px(lon,lat):
    xpt=(lon-1.7544578039042098)/0.006344690965581331; ypt=(14.47692968473804-lat)/0.00634488747510426
    return xpt*6600/3168, ypt*3675/1764
def hexrgb(h):
    try:
        h=str(h).lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],dtype=float)
    except: return None
legfills=[]
for _,r in leg.iterrows():
    c=hexrgb(r['fill'])
    if c is not None: legfills.append((str(r['code']),c))
def sample_median(geom,n=300,seed=0,erode=0.01):
    try:
        g2=geom.buffer(-erode)
        if g2.is_empty or g2.area<geom.area*0.05: g2=geom
    except: g2=geom
    rng=np.random.default_rng(seed); minx,miny,maxx,maxy=g2.bounds; pts=[]; tries=0
    while len(pts)<n and tries<n*40:
        tries+=1; x=rng.uniform(minx,maxx); y=rng.uniform(miny,maxy)
        if g2.contains(Point(x,y)): pts.append((x,y))
    cols=[]
    for x,y in pts:
        px,py=lonlat_to_px(x,y); ix,iy=int(round(px)),int(round(py))
        if 0<=ix<img.shape[1] and 0<=iy<img.shape[0]: cols.append(img[iy,ix])
    return (np.median(np.array(cols),axis=0),len(cols)) if cols else (None,0)
tree=STRtree(list(geo.geometry.values))
adm_line=admin.boundary
rows=[]
for _,gr in gaps.iterrows():
    if gr.area_km2<5: continue
    g=gr.geometry
    touches_edge = g.distance(adm_line)<0.002  # ~200m
    cand_idx=[int(j) for j in tree.query(g.buffer(0.002),predicate='intersects')]
    cand_codes=sorted(set(geo.iloc[cand_idx].code.tolist())) if cand_idx else []
    med,n=sample_median(g,n=250,seed=int(gr.gap_id))
    best=None
    if med is not None:
        ds=sorted([(np.linalg.norm(med-c),code) for code,c in legfills])
        best=f"{ds[0][1]}(d{ds[0][0]:.0f}) / 2nd {ds[1][1]}(d{ds[1][0]:.0f})"
        bestcode=ds[0][1]
    else: bestcode=None
    rows.append((int(gr.gap_id),round(float(gr.area_km2),1), "EDGE" if touches_edge else "INLAND", cand_codes, best, "MATCH-NBR" if bestcode in cand_codes else ("OTHER" if bestcode else ""), med.round(0).tolist() if med is not None else None))
for r in rows:
    print(r)
import collections
print(collections.Counter((r[2],r[5]) for r in rows))
# Kainji / other lakes: gaps containing key water points?
for name,(lon,lat) in [("Kainji Lake",(4.55,10.35)),("Lake Chad NG",(13.7,13.2)),("Lagos Lagoon",(3.5,6.45))]:
    pt=Point(lon,lat)
    hit=gaps[gaps.geometry.contains(pt)]
    print(name, "gap:", hit[['gap_id','area_km2']].values.tolist() if len(hit) else "none (covered by geology or outside admin)")
