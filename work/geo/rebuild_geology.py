import geopandas as gpd, numpy as np, shapely, json, warnings, pickle, time
from shapely.ops import unary_union, polygonize
from shapely import STRtree
warnings.filterwarnings('ignore')
t0=time.time()

geo=gpd.read_file('shapefile_results/geology/nigeria_geology_units.shp')
ref=gpd.read_file('shapefiles/nigeria_admin0/nigeria_admin0.shp').geometry.iloc[0]
geo['fid']=np.arange(len(geo))
print(f"source features {len(geo)}")

# 1) Node all boundaries + reference boundary, polygonize to planar faces
lines=[g.boundary for g in geo.geometry.values]+[ref.boundary]
noded=unary_union(lines)
print(f"noded lines: {noded.geom_type}, coords={shapely.get_num_coordinates(noded)}  [{time.time()-t0:.1f}s]")
faces=list(polygonize(noded))
print(f"faces: {len(faces)}  [{time.time()-t0:.1f}s]")
faces=np.array(faces, dtype=object)
areas=np.array([f.area for f in faces])
reps=np.array([f.representative_point() for f in faces], dtype=object)
in_ref=np.array([ref.contains(r) or ref.touches(r) for r in reps])
print(f"faces inside ref: {in_ref.sum()}, outside: {(~in_ref).sum()}")
pickle.dump({'faces':faces,'in_ref':in_ref}, open('work/geo/faces.pkl','wb'))

# 2) Majority assignment from source overlaps
src_geoms=geo.geometry.values
tree=STRtree(src_geoms)
assign=np.full(len(faces), -1, dtype=int)
cover=np.zeros(len(faces))
overlap_multi=np.zeros(len(faces), dtype=bool)
for i,f in enumerate(faces):
    if not in_ref[i]: continue
    cand=tree.query(f)
    best=-1; bestov=0.0; nov=0
    for j in cand:
        ov=f.intersection(src_geoms[j]).area
        if ov>1e-12: nov+=1
        if ov>bestov: bestov=ov; best=j
    if best>=0 and bestov>0:
        assign[i]=best; cover[i]=bestov/f.area if f.area>0 else 0
        overlap_multi[i]=nov>1
print(f"majority-assigned faces: {(assign>=0).sum()}, zero-overlap gap faces inside ref: {((assign<0)&in_ref).sum()}  [{time.time()-t0:.1f}s]")
print(f"  overlap-resolved faces (inside >1 source): {(overlap_multi&in_ref).sum()}")
gap_area_deg=areas[(assign<0)&in_ref].sum()
print(f"  zero-overlap gap area: {gap_area_deg:.4f} deg2 (~{gap_area_deg*12266:.0f} km2)")
print(f"  cover<0.99 assigned faces: {((assign>=0)&(cover<0.99)).sum()} area {(areas[(assign>=0)&(cover<0.99)]).sum()*12266:.1f} km2 (slivers/partial)")
pickle.dump({'assign':assign,'cover':cover,'overlap_multi':overlap_multi,'areas':areas}, open('work/geo/assign_stage1.pkl','wb'))
# gap face size distribution
ga=areas[(assign<0)&in_ref]*12266
if len(ga):
    print(f"  gap faces km2: max={ga.max():.1f} median={np.median(ga):.3f} n>10km2={(ga>10).sum()} n>1={(ga>1).sum()}")
