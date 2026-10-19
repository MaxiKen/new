import geopandas as gpd, numpy as np
from PIL import Image
from shapely.geometry import Point
from shapely.strtree import STRtree
from shapely.ops import unary_union
import warnings; warnings.filterwarnings('ignore')
geo=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
img=np.array(Image.open("work/geology_native_full.jpg").convert("RGB")).astype(int)
def lonlat_to_px(lon,lat):
    xpt=(lon-1.7544578039042098)/0.006344690965581331
    ypt=(14.47692968473804-lat)/0.00634488747510426
    return xpt*6600/3168, ypt*3675/1764
def hexrgb(h):
    h=str(h).lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],dtype=float)
def sample_median(geom, n=400, seed=1):
    # sample points by rejection in bbox, keep those inside geom, erode by using geom.buffer(-0.01) if possible
    try:
        g2=geom.buffer(-0.008)
        if g2.is_empty or g2.area<geom.area*0.05: g2=geom
    except: g2=geom
    rng=np.random.default_rng(seed)
    minx,miny,maxx,maxy=g2.bounds
    pts=[]
    tries=0
    while len(pts)<n and tries<n*30:
        tries+=1
        x=rng.uniform(minx,maxx); y=rng.uniform(miny,maxy)
        if g2.contains(Point(x,y)): pts.append((x,y))
    cols=[]
    for x,y in pts:
        px,py=lonlat_to_px(x,y)
        ix,iy=int(round(px)),int(round(py))
        if 0<=ix<img.shape[1] and 0<=iy<img.shape[0]: cols.append(img[iy,ix])
    if not cols: return None,0
    return np.median(np.array(cols),axis=0), len(cols)

# Duplicates
print("=== dup_of pairs (src_seq is key) ===")
seq2idx={int(r.src_seq):i for i,r in geo.iterrows()}
for i,r in geo.iterrows():
    if int(r.dup_of)!=0:
        j=seq2idx.get(int(r.dup_of))
        o=geo.iloc[j]
        same_geom = r.geometry.equals(o.geometry)
        med,n=sample_median(r.geometry, n=200, seed=i)
        if med is not None:
            d_new=np.linalg.norm(med-hexrgb(r.fill)); d_old=np.linalg.norm(med-hexrgb(o.fill))
            win = r.code if d_new<d_old else o.code
            print(f"dup idx{i} code={r.code} fill={r.fill} lbl={r.lbl_code} seq={r.src_seq} | orig idx{j} code={o.code} fill={o.fill} lbl={o.lbl_code} seq={o.src_seq} | same_geom={same_geom} sampleRGB={med.round(0)} d_new={d_new:.0f} d_orig={d_old:.0f} -> raster favours {win}")
print("\n=== largest partial overlaps: who wins on printed map? ===")
geo_m=geo.to_crs(6933); geoms_m=list(geo_m.geometry.values); tree=STRtree(geoms_m)
ovs=[]
for i,g in enumerate(geoms_m):
    for jj in tree.query(g,predicate='intersects'):
        j=int(jj)
        if j<=i: continue
        inter=g.intersection(geoms_m[j]); a=inter.area/1e6
        smaller=min(g.area,geoms_m[j].area)/1e6
        if a>20 and a<0.98*smaller:  # partial, not containment/dup
            ovs.append((a,i,j))
ovs.sort(reverse=True)
print(f"partial overlaps >20km2 (not containment): {len(ovs)}")
# convert overlap back to lonlat for sampling: use lonlat geoms intersection (approx fine)
for a,i,j in ovs[:18]:
    inter_ll=geo.geometry.iloc[i].intersection(geo.geometry.iloc[j])
    med,n=sample_median(inter_ll,n=250,seed=i+j)
    ri,rj=geo.iloc[i],geo.iloc[j]
    if med is None: print(i,j,"no sample"); continue
    di=np.linalg.norm(med-hexrgb(ri.fill)); dj=np.linalg.norm(med-hexrgb(rj.fill))
    later = ri.code if ri.src_seq>rj.src_seq else rj.code
    smaller = ri.code if ri.area_km2<rj.area_km2 else rj.code
    win = ri.code if di<dj else rj.code
    print(f"ov {a:.0f}km2 idx{i} {ri.code}(seq{ri.src_seq},area{ri.area_km2:.0f},fill{ri.fill}) vs idx{j} {rj.code}(seq{rj.src_seq},area{rj.area_km2:.0f},fill{rj.fill}) sample={med.round(0)} d=({di:.0f},{dj:.0f}) raster->{win} later->{later} smaller->{smaller}")
print("\n=== containment overlaps (smaller fully inside larger, diff code) sample ===")
cont=[]
for i,g in enumerate(geoms_m):
    for jj in tree.query(g,predicate='intersects'):
        j=int(jj)
        if j<=i: continue
        inter=g.intersection(geoms_m[j]); a=inter.area/1e6; smaller=min(g.area,geoms_m[j].area)/1e6
        if a>20 and a>=0.98*smaller and geo.iloc[i].code!=geo.iloc[j].code and not g.equals(geoms_m[j]):
            cont.append((a,i,j))
cont.sort(reverse=True)
print(f"containments >20km2 diff-code: {len(cont)}")
for a,i,j in cont[:15]:
    small_idx = i if geo.iloc[i].area_km2<geo.iloc[j].area_km2 else j
    med,n=sample_median(geo.geometry.iloc[small_idx],n=250,seed=i+j)
    ri,rj=geo.iloc[i],geo.iloc[j]
    if med is None: continue
    di=np.linalg.norm(med-hexrgb(ri.fill)); dj=np.linalg.norm(med-hexrgb(rj.fill))
    later = ri.code if ri.src_seq>rj.src_seq else rj.code
    win = ri.code if di<dj else rj.code
    print(f"cont {a:.0f}km2 idx{i} {ri.code}(seq{ri.src_seq}) vs idx{j} {rj.code}(seq{rj.src_seq}) small=idx{small_idx} {geo.iloc[small_idx].code} sample={med.round(0)} d=({di:.0f},{dj:.0f}) raster->{win} later->{later} smaller->{geo.iloc[small_idx].code}")
