import geopandas as gpd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp")
geo=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
gaps=gpd.read_file("work/geology_gaps.geojson")
print(geo['dup_of'].value_counts(dropna=False).head(20))
print("\ndup_of non-null examples:")
print(geo[geo['dup_of'].notna() & (geo['dup_of'].astype(str)!='') & (geo['dup_of'].astype(str)!='None')][['unit','code','dup_of','area_km2']].head(20).to_string() if 'dup_of' in geo else 'no dup col')
# exact duplicate geometries?
from shapely import wkb
hashes=[wkb.dumps(g) for g in geo.geometry]
from collections import Counter
c=Counter(hashes)
print("exact duplicate geometry groups:", sum(1 for v in c.values() if v>1), "extra copies:", sum(v-1 for v in c.values() if v>1))
# overlap histogram quick via sample already done; check largest overlaps
geo_m=geo.to_crs(6933)
from shapely.strtree import STRtree
geoms=list(geo_m.geometry.values); tree=STRtree(geoms)
ovs=[]
for i,g in enumerate(geoms):
    for j in tree.query(g, predicate='intersects'):
        if j<=i: continue
        a=g.intersection(geoms[j]).area/1e6
        if a>1: ovs.append((a,i,int(j),geo.iloc[i]['code'],geo.iloc[int(j)]['code'], min(g.area,geoms[j].area)/1e6))
ovs.sort(reverse=True)
print(f"\noverlaps >1km2: {len(ovs)}")
for o in ovs[:25]: print(f" overlap {o[0]:.1f} km2 feats {o[1]}/{o[2]} codes {o[3]}/{o[4]} smaller_feat_area {o[5]:.1f} -> overlap/smaller={o[0]/o[5]:.2f}")
# Map plots
fig,ax=plt.subplots(figsize=(14,11))
geo.plot(ax=ax,column='code',legend=False,cmap='tab20',linewidth=0.1,edgecolor='k')
gaps.plot(ax=ax,color='red',edgecolor='darkred',linewidth=0.6)
admin.boundary.plot(ax=ax,color='black',linewidth=1.2)
for i,row in gaps.head(12).iterrows():
    c=row.geometry.centroid; ax.text(c.x,c.y,str(int(row['gap_id'])),fontsize=9,color='red',weight='bold',ha='center')
ax.set_title('Geology polygons (by code) + gaps vs Nigeria Admin0 in RED (numbered largest)')
plt.tight_layout(); plt.savefig("work/geology_gaps_map.png",dpi=150)
print("saved geology_gaps_map")
# NE zoom Borno/Lake Chad
fig,ax=plt.subplots(figsize=(10,8))
geo.plot(ax=ax,column='code',cmap='tab20',linewidth=0.2,edgecolor='k')
gaps.plot(ax=ax,color='none',edgecolor='red',linewidth=1.5)
admin.boundary.plot(ax=ax,color='black',linewidth=1.2)
ax.set_xlim(12.5,15.0); ax.set_ylim(11.0,14.2); ax.set_title('NE zoom: Borno / Lake Chad gap0')
plt.tight_layout(); plt.savefig("work/geology_gap_NE.png",dpi=150)
# SW zoom gap3
fig,ax=plt.subplots(figsize=(10,8))
geo.plot(ax=ax,column='code',cmap='tab20',linewidth=0.2,edgecolor='k')
gaps.plot(ax=ax,color='none',edgecolor='red',linewidth=1.5)
admin.boundary.plot(ax=ax,color='black',linewidth=1.2)
ax.set_xlim(3.0,6.5); ax.set_ylim(5.5,7.5); ax.set_title('SW zoom: Ondo/Edo gap3 etc')
plt.tight_layout(); plt.savefig("work/geology_gap_SW.png",dpi=150)
# Taraba zoom
fig,ax=plt.subplots(figsize=(10,8))
geo.plot(ax=ax,column='code',cmap='tab20',linewidth=0.2,edgecolor='k')
gaps.plot(ax=ax,color='none',edgecolor='red',linewidth=1.5)
admin.boundary.plot(ax=ax,color='black',linewidth=1.2)
ax.set_xlim(9.5,12.5); ax.set_ylim(6.0,8.0); ax.set_title('Taraba zoom gaps 2,7,11,22')
plt.tight_layout(); plt.savefig("work/geology_gap_taraba.png",dpi=150)
print("saved zooms")
