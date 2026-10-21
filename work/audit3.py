import geopandas as gpd, numpy as np
import warnings; warnings.filterwarnings('ignore')
geo=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
cols=['ocg_id','layer_no','unit','fill','code','code_src','leg_code','lbl_code','n_lbl','area_km2','n_rings','src_seq','dup_of']
for idx in [164,165,170,171,193,303,317,318,319,320,321,331,689,1076,482,1251,1174,1175]:
    r=geo.iloc[idx]
    print(idx, {c:r[c] for c in cols})
print("\n--- code_src values ---")
print(geo['code_src'].value_counts(dropna=False).to_string())
print("\n--- layer_no values ---")
print(geo['layer_no'].value_counts(dropna=False).to_string())
print("\n--- ocg_id values top ---")
print(geo['ocg_id'].value_counts(dropna=False).head(30).to_string())
print("\n--- lbl_code vs code agreement ---")
m=geo['lbl_code'].notna()&(geo['lbl_code'].astype(str)!='')
print("with lbl:",m.sum(),"agree:",(geo.loc[m,'lbl_code']==geo.loc[m,'code']).sum())
print(geo[m & (geo['lbl_code']!=geo['code'])][cols].head(30).to_string())
print("\n--- fill vs legend? unique fills", geo['fill'].nunique())
print(geo[['code','fill']].drop_duplicates().sort_values('code').to_string())
