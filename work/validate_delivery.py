import geopandas as gpd, glob, rasterio, json
for f in sorted(glob.glob("corrected_delivery/**/*.shp",recursive=True)):
    d=gpd.read_file(f)
    valid=int(d.geometry.is_valid.sum()); nulls=int(d.geometry.isna().sum())
    print(f"{f.replace('corrected_delivery/','')} n={len(d)} crs={d.crs} valid={valid} null={nulls} bounds={[round(v,2) for v in d.total_bounds]}")
for f in sorted(glob.glob("corrected_delivery/02_Georeferenced_map_pictures/*.tif")):
    with rasterio.open(f) as ds:
        print(f.split('/')[-1], ds.width, ds.height, ds.crs, [round(v,3) for v in ds.bounds])
m=gpd.read_file("corrected_delivery/04_Minerals_RECENTRED/nigeria_mineral_symbols_CORRECTED.shp")
a=m[m.LEG_NO==1]
print("Asbestos point:", a[['LEG_NO','MINERAL','DET_SRC','PX_X','PX_Y']].to_string(index=False), "lonlat", a.geometry.x.values, a.geometry.y.values)
g=gpd.read_file("corrected_delivery/03_Geology_rock_units_FILLED/nigeria_geology_units_FILLED.shp").to_crs(6933)
adm=gpd.read_file("corrected_delivery/01_Nigeria_boundary/nigeria_admin0.shp").to_crs(6933)
from shapely.ops import unary_union
u=unary_union(g.geometry.values); A=unary_union(adm.geometry.values)
print(f"geology union {u.area/1e6:.1f} km2 vs admin {A.area/1e6:.1f}; gap {(A.difference(u)).area/1e6:.3f} overflow {(u.difference(A)).area/1e6:.3f}")
