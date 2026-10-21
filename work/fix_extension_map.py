import geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')
OUT="corrected_delivery/03_Geology_rock_units_FILLED"; QA="corrected_delivery/QA_maps_and_reports"
filled=gpd.read_file(f"{OUT}/nigeria_geology_units_FILLED.shp")
orig=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp")
seq2orig={int(r.src_seq):r.geometry for _,r in orig.iterrows()}
exts=[]
for _,r in filled.iterrows():
    if int(r.src_seq) in seq2orig:
        d=r.geometry.difference(seq2orig[int(r.src_seq)])
        if not d.is_empty: exts.append(d)
ext=gpd.GeoDataFrame(geometry=exts,crs=4326)
water=filled[filled.code=='WATER']
fig,ax=plt.subplots(figsize=(13,10.5))
filled.plot(ax=ax,color='#eeeeee',linewidth=0.05,edgecolor='0.7')
ext.plot(ax=ax,color='red',linewidth=0)
water.plot(ax=ax,color='#3a9ad9',linewidth=0.3,edgecolor='navy')
admin.boundary.plot(ax=ax,color='black',linewidth=1.1)
ax.set_title('Areas ADDED (red = extension of neighbouring polygons; blue NE = single new Lake Chad WATER polygon)\nBorder strips + hundreds of thin inland disconnect slivers (see zooms)',fontsize=11)
plt.tight_layout(); plt.savefig(f"{QA}/QA_geology_extension_areas.png",dpi=160)
print("fixed extension map")
