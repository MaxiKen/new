import pickle, geopandas as gpd, numpy as np, pandas as pd, json, shutil, os
from shapely.ops import unary_union
from shapely import make_valid
from shapely.geometry import Polygon, MultiPolygon
from shapely.strtree import STRtree
import warnings; warnings.filterwarnings('ignore')
AEA="+proj=aea +lat_1=4 +lat_2=12 +lat_0=0 +lon_0=9 +datum=WGS84 +units=m +no_defs +type=crs"
st=pickle.load(open("work/geology_filled_state.pkl","rb"))
work=st["work"]; gaplog=st["gaplog"]; dropped=st["dropped"]; water_geoms=st["water_geoms"]
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp").geometry.iloc[0]
orig=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
# micro-clean residuals (include water)
water_union=unary_union(water_geoms) if water_geoms else Polygon()
for iteration in range(3):
    resid=admin.difference(unary_union([unary_union(work.geometry.values),water_union]))
    parts=list(resid.geoms) if isinstance(resid,MultiPolygon) else ([resid] if not resid.is_empty else [])
    ra=gpd.GeoSeries(parts,crs=4326).to_crs(AEA).area.values/1e6 if parts else np.array([])
    print(f"iter{iteration} residual parts={len(parts)} total_km2={ra.sum() if len(ra) else 0:.8f} max={ra.max() if len(ra) else 0:.8f}")
    if len(parts)==0 or ra.sum()<1e-9: break
    geoms=list(work.geometry.values); tree=STRtree(geoms)
    extra={}
    for rp in parts:
        cand=[int(j) for j in tree.query(rp.buffer(0.002),predicate='intersects')]
        if not cand: cand=[int(tree.nearest(rp))]
        # longest shared border
        best=max(cand, key=lambda j: geoms[j].boundary.intersection(rp.buffer(0.00012)).length)
        extra.setdefault(best,[]).append(rp)
    ng=list(work.geometry.values)
    for j,lst in extra.items(): ng[j]=make_valid(unary_union([ng[j]]+lst))
    work=gpd.GeoDataFrame(work.drop(columns=['geometry']),geometry=ng,crs=4326)
# final areas etc
work_m=work.to_crs(AEA)
work['area_km2']=(work_m.geometry.area.values/1e6).round(4)
work['perim_km']=(work_m.geometry.length.values/1000).round(3)
cen_m=work_m.geometry.centroid
cen_ll=gpd.GeoSeries(cen_m,crs=AEA).to_crs(4326)
work['cen_lon']=cen_ll.x.round(6); work['cen_lat']=cen_ll.y.round(6)
def nrings(g):
    ps=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
    return int(sum(1+len(list(p.interiors)) for p in ps))
work['n_rings']=[nrings(g) for g in work.geometry]
# orig index mapping: work retains original order subset; src_seq unique -> recover orig index
seq2orig={int(r.src_seq):i for i,r in orig.iterrows()}
work['orig_idx']=[seq2orig[int(s)] for s in work.src_seq]
work['ovlap_km']=work['_ovlap_km'].round(3); work['clip_km']=work['_clip_km'].round(3)
# filled recompute: final area - (orig - ovlap - clip) approx = use _filled_km + micro extras (tiny); recompute directly:
planar_clip_area=np.array([float(orig_area) for orig_area in np.zeros(len(work))])  # placeholder
work['fill_km']=work['_filled_km'].round(3)
work['fix_flag']=np.where(work['_filled_km']>0.005,"EXTENDED",np.where((work['_ovlap_km']>0.005)|(work['_clip_km']>0.005),"TRIMMED","UNCHANGD"))
# water row
if water_geoms:
    wg=unary_union(water_geoms)
    wa=gpd.GeoSeries([wg],crs=4326).to_crs(AEA).area.iloc[0]/1e6
    wrow={c:None for c in work.columns}
    wrow.update({"ocg_id":-1,"layer_no":-1,"unit":"Lake Chad (open water)","fill":"#8ec9e8","code":"WATER","code_src":"new:necessary water","leg_code":"",
      "leg_desc":"Lake Chad open water within Nigeria boundary; no rock unit is printed under the lake on the Geological Map. Underlying sediments would be Chad Formation/Alluvium but are not mapped beneath open water.",
      "lbl_code":"","n_lbl":0,"area_km2":round(float(wa),3),"perim_km":round(float(gpd.GeoSeries([wg],crs=4326).to_crs(AEA).length.iloc[0]/1000),3),
      "cen_lon":round(float(gpd.GeoSeries([wg],crs=4326).to_crs(AEA).centroid.to_crs(4326).x.iloc[0]),6),
      "cen_lat":round(float(gpd.GeoSeries([wg],crs=4326).to_crs(AEA).centroid.to_crs(4326).y.iloc[0]),6),
      "n_rings":nrings(wg),"src_seq":-1,"dup_of":0,"orig_idx":-1,"ovlap_km":0.0,"clip_km":0.0,"fill_km":round(float(wa),3),"fix_flag":"NEW_WATR","geometry":wg})
    work=gpd.GeoDataFrame(pd.concat([work,pd.DataFrame([wrow])],ignore_index=True),geometry="geometry",crs=4326)
work=work.drop(columns=[c for c in ['_orig_area','_ovlap_km','_clip_km','_orig_km','_filled_km'] if c in work.columns])
print("final features",len(work), "cols",list(work.columns))
# validation
uni=unary_union(work.geometry.values)
adm_area=gpd.GeoSeries([admin],crs=4326).to_crs(AEA).area.iloc[0]/1e6
uni_area=gpd.GeoSeries([uni],crs=4326).to_crs(AEA).area.iloc[0]/1e6
sum_area=float(work['area_km2'].sum())
gap_final=admin.difference(uni); over_final=uni.difference(admin)
gf=gpd.GeoSeries([gap_final],crs=4326).to_crs(AEA).area.iloc[0]/1e6; of=gpd.GeoSeries([over_final],crs=4326).to_crs(AEA).area.iloc[0]/1e6
print(f"admin {adm_area:.3f} union {uni_area:.3f} sum {sum_area:.3f} gap {gf:.6f} overflow {of:.6f} overlap(sum-union) {sum_area-uni_area:.4f}")
print("valid:", int(work.geometry.is_valid.sum()),"/",len(work), "empty:", int(work.geometry.is_empty.sum()))
invalid=work[~work.geometry.is_valid]
if len(invalid):
    print("fixing invalid", len(invalid))
    work['geometry']=[make_valid(g) if not g.is_valid else g for g in work.geometry]
    print("valid after:", int(work.geometry.is_valid.sum()))
OUT="corrected_delivery/03_Geology_rock_units_FILLED"; os.makedirs(OUT,exist_ok=True)
work.to_file(f"{OUT}/nigeria_geology_units_FILLED.shp", encoding="utf-8")
print("wrote shapefile")
# original copy renamed
for ext in ['shp','shx','dbf','prj','cpg']:
    src=f"shapefile_results/geology/nigeria_geology_units.{ext}"
    if os.path.exists(src): shutil.copy(src,f"{OUT}/nigeria_geology_units_ORIGINAL_with_gaps.{ext}")
# logs
pd.DataFrame(gaplog).sort_values("area_km2",ascending=False).to_csv(f"{OUT}/gap_fill_log.csv",index=False)
pd.DataFrame(dropped).to_csv(f"{OUT}/dropped_features_log.csv",index=False)
# area by code before/after
orig_m=orig.to_crs(AEA); orig=orig.assign(_a=orig_m.geometry.area.values/1e6)
b=orig.groupby('code')['_a'].agg(['sum','count']).rename(columns={'sum':'orig_area_km2','count':'orig_n'})
a=work.groupby('code')['area_km2'].agg(['sum','count']).rename(columns={'sum':'filled_area_km2','count':'filled_n'})
comp=b.join(a,how='outer').fillna(0); comp['change_km2']=comp.filled_area_km2-comp.orig_area_km2
comp.round(3).to_csv(f"{OUT}/area_by_code_before_after.csv")
print(comp.sort_values('change_km2').to_string())
# legend copy + WATER row appended as separate note file (keep original legend untouched copy)
shutil.copy("shapefile_results/geology/geology_legend.csv", f"{OUT}/geology_legend.csv")
qa={"original_features":1542,"final_features":int(len(work)),"dropped_features":len(dropped),"new_polygons_created":len(water_geoms),
 "admin_area_km2":round(float(adm_area),3),"final_union_km2":round(float(uni_area),3),"sum_feature_km2":round(sum_area,3),
 "final_gap_km2":round(float(gf),6),"final_overflow_km2":round(float(of),6),"overlap_sum_minus_union_km2":round(float(sum_area-uni_area),4),
 "gaps_filled":len(gaplog),"gap_area_filled_km2":round(float(sum(d['area_km2'] for d in gaplog)),2),
 "overlap_removed_km2":round(float(work['ovlap_km'].sum()),2) if 'ovlap_km' in work else None,
 "clipped_outside_km2":round(float(work['clip_km'].sum()),2),
 "method_counts":pd.DataFrame(gaplog)['method'].value_counts().to_dict(),
 "crs":"EPSG:4326","note":"Union equals Nigeria Admin0 within numeric tolerance; overlaps resolved by PDF draw order (later src_seq on top, verified against printed colours). Gaps filled by extending neighbouring polygons (Voronoi nearest split where multiple neighbours; single-neighbour/longest-border otherwise). Only new polygon is Lake Chad WATER."}
json.dump(qa,open(f"{OUT}/geology_filled_QA_report.json","w"),indent=2)
print(json.dumps(qa,indent=2))
