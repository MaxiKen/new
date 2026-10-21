import geopandas as gpd, numpy as np, json
from shapely.ops import unary_union
import warnings; warnings.filterwarnings('ignore')
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp")
states=gpd.read_file("shapefiles/nigeria_online_layers/state_boundaries/state_boundaries.shp")
geo=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
adm=admin.geometry.iloc[0]
# gap polygons in lonlat with area via 6933
geo_m=geo.to_crs(6933); adm_m=gpd.GeoSeries([adm],crs=4326).to_crs(6933).iloc[0]
union_m=unary_union(geo_m.geometry.values)
gap_m=adm_m.difference(union_m)
parts=sorted(list(gap_m.geoms) if gap_m.geom_type=='MultiPolygon' else [gap_m], key=lambda g:-g.area)
print(f"gaps total {len(parts)} area {gap_m.area/1e6:.1f} km2")
gap_ll=gpd.GeoSeries(parts,crs=6933).to_crs(4326)
for i,(g,gm) in enumerate(zip(gap_ll,parts)):
    if i>=25: break
    # which state contains centroid
    c=g.centroid
    st=states[states.geometry.contains(c)]
    sname=st.iloc[0]['STATE_NM'] if len(st) else '(border/offshore?)'
    # neighbours: geology polys touching gap (in lonlat use buffer small)
    print(f"gap{i}: {gm.area/1e6:9.2f} km2  centroid=({c.x:.3f},{c.y:.3f}) state={sname} bbox={[round(v,2) for v in g.bounds]}")
# size histogram
areas=np.array([g.area/1e6 for g in parts])
for thr in [100,10,1,0.1,0.01]:
    print(f"gaps > {thr} km2: {(areas>thr).sum()} covering {areas[areas>thr].sum():.1f} km2")
print(f"gaps <=1km2: {(areas<=1).sum()} covering {areas[areas<=1].sum():.2f} km2 (slivers)")
# overlaps: pairwise? Use planar overlay count via union area diff already 21242. Check overlaps by unit pairs sampling with STRtree
from shapely.strtree import STRtree
geoms=list(geo_m.geometry.values)
tree=STRtree(geoms)
ov_pairs=0; ov_area=0.0; examples=[]
for i,g in enumerate(geoms):
    for j in tree.query(g, predicate='intersects'):
        if j<=i: continue
        inter=g.intersection(geoms[j])
        if inter.area>1000:  # >0.001 km2
            ov_pairs+=1; ov_area+=inter.area
            if len(examples)<10:
                examples.append((i,j,inter.area/1e6, geo.iloc[i]['code'], geo.iloc[j]['code']))
print(f"\noverlapping pairs (>{0.001}km2): {ov_pairs}, summed pairwise overlap area {ov_area/1e6:.1f} km2 (multi-overlaps double counted)")
for e in examples: print(e)
# overflow outside admin by unit
out=geo_m.geometry.difference(adm_m)
geo['out_km2']=out.area.values/1e6
print("\ntop overflow units outside Nigeria:")
print(geo.groupby('code')['out_km2'].sum().sort_values(ascending=False).head(15).to_string())
# save gaps for plotting
gdf=gpd.GeoDataFrame({'gap_id':range(len(parts)),'area_km2':areas}, geometry=gap_ll, crs=4326)
gdf.to_file("work/geology_gaps.geojson", driver="GeoJSON")
print("saved work/geology_gaps.geojson")
# interior holes not covered?
print("\ngeology feature area stats km2: min", (geo_m.geometry.area.min()/1e6), "max", geo_m.geometry.area.max()/1e6)
print("features <1km2:", (geo_m.geometry.area/1e6<1).sum(), " <0.1:", (geo_m.geometry.area/1e6<0.1).sum())
