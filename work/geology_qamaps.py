import geopandas as gpd, numpy as np, pandas as pd, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import warnings; warnings.filterwarnings('ignore')
OUT="corrected_delivery/03_Geology_rock_units_FILLED"
QA="corrected_delivery/QA_maps_and_reports"
import os; os.makedirs(QA,exist_ok=True)
filled=gpd.read_file(f"{OUT}/nigeria_geology_units_FILLED.shp")
orig=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp")
# fix_flag wording patch + rewrite
filled['fix_flag']=filled['fix_flag'].replace({'UNCHANGD':'UNCHANGED','NEW_WATR':'NEW_WATER'})
filled.to_file(f"{OUT}/nigeria_geology_units_FILLED.shp", encoding="utf-8")
print(filled['fix_flag'].value_counts().to_dict())
print("dropped log OGe/Ts:")
dl=pd.read_csv(f"{OUT}/dropped_features_log.csv")
print(dl.to_string())
# colours from fill field (fallback grey)
def cols(gdf):
    c=[]
    for f in gdf['fill']:
        try: c.append(str(f) if str(f).startswith('#') else '#cccccc')
        except: c.append('#cccccc')
    return c
# Main filled map
fig,ax=plt.subplots(figsize=(13,10.5))
filled.plot(ax=ax,color=cols(filled),linewidth=0.08,edgecolor='0.25')
admin.boundary.plot(ax=ax,color='black',linewidth=1.1)
ax.set_title('FILLED geology (by printed fill colour) — tiles Nigeria boundary with NO gaps\n1502 features (1501 extended/trimmed + 1 Lake Chad WATER, light blue NE)',fontsize=11)
ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude')
plt.tight_layout(); plt.savefig(f"{QA}/QA_geology_FILLED_map.png",dpi=160); plt.close()
# Extension areas: filled minus original-kept geometry per src_seq
seq2orig={int(r.src_seq):r.geometry for _,r in orig.iterrows()}
exts=[]
for _,r in filled.iterrows():
    if int(r.src_seq) in seq2orig:
        d=r.geometry.difference(seq2orig[int(r.src_seq)])
        if not d.is_empty: exts.append(d)
ext=gpd.GeoDataFrame(geometry=exts,crs=4326)
print(f"extension parts: {len(ext)}")
fig,ax=plt.subplots(figsize=(13,10.5))
filled.plot(ax=ax,color='#eeeeee',linewidth=0.05,edgecolor='0.7')
if len(ext): ext.plot(ax=ax,color='red',linewidth=0)
admin.boundary.plot(ax=ax,color='black',linewidth=1.1)
ax.set_title('Areas ADDED by extending neighbouring polygons (red) — border strips + inland disconnect slivers\nLake Chad (NE red block) is the single new WATER polygon; everything else is neighbour extension',fontsize=11)
plt.tight_layout(); plt.savefig(f"{QA}/QA_geology_extension_areas.png",dpi=160); plt.close()
# Zooms on filled
zooms=[("NE_LakeChad",12.4,10.9,15.0,14.1),("North_border_Yobe_Katsina",6.5,12.4,11.5,14.0),("Taraba_south_border",9.4,6.2,12.4,8.0),("West_border_Kebbi_Niger",2.4,9.8,5.0,12.8),("SW_coast_Lagos_Delta",2.6,4.1,7.5,6.8)]
for name,x0,y0,x1,y1 in zooms:
    fig,ax=plt.subplots(figsize=(10,7.5))
    filled.plot(ax=ax,color=cols(filled),linewidth=0.15,edgecolor='0.25')
    if len(ext): ext.plot(ax=ax,color='none',edgecolor='red',linewidth=1.0)
    admin.boundary.plot(ax=ax,color='black',linewidth=1.2)
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_title(f'FILLED geology zoom — {name} (red outline = extension area)')
    plt.tight_layout(); plt.savefig(f"{QA}/QA_geology_FILLED_zoom_{name}.png",dpi=160); plt.close()
print("maps done")
