import geopandas as gpd, numpy as np, pandas as pd
from PIL import Image
import warnings; warnings.filterwarnings('ignore')
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
print("legend rows",len(leg))
cnt=minr.groupby(['leg_no','mineral']).size().reset_index(name='n')
merged=leg.merge(cnt,left_on='legend_no',right_on='leg_no',how='left')
print(merged.to_string())
print("\n--- minerals in points not in legend list ---")
print(sorted(set(minr['mineral'].unique())-set(leg['point_attribute_name'].unique())))
# near duplicates in pixel space
pts=minr[['px_x','px_y']].values
from scipy.spatial import cKDTree
tree=cKDTree(pts)
pairs=tree.query_pairs(6)
print(f"\npairs within 6px: {len(pairs)}")
pairs3=tree.query_pairs(3.5)
print(f"pairs within 3.5px: {len(pairs3)}")
for a,b in sorted(pairs3)[:40]:
    ra,rb=minr.iloc[a],minr.iloc[b]
    d=np.hypot(*(pts[a]-pts[b]))
    print(f" fid{ra['fid']}[{ra['mineral']}] vs fid{rb['fid']}[{rb['mineral']}] d={d:.1f}px px=({ra['px_x']},{ra['px_y']}) src={ra['src_ids']}/{rb['src_ids']}")
pairs10=tree.query_pairs(10)
print(f"pairs within 10px: {len(pairs10)} (many legit clusters expected)")
# distance to nearest neighbour histogram
dd,_=tree.query(pts,k=2)
nn=dd[:,1]
print("NN distance px percentiles:", {p:round(float(np.percentile(nn,p)),1) for p in [0,1,5,10,25,50]})
print("points with NN<4px:", (nn<4).sum(), " <6px:",(nn<6).sum())
# id_score distribution
print("\nid_score describe:\n", minr['id_score'].describe().to_string())
print("\nlow score <0.4 count:", (minr['id_score']<0.4).sum())
print(minr.nsmallest(15,'id_score')[['fid','mineral','id_method','id_score','px_x','px_y']].to_string())
# px coords: are they .0/.5 bbox centres?
print("\npx_x frac:", minr['px_x'].mod(1).value_counts().to_string())
print("sym_color counts:\n", minr['sym_color'].value_counts(dropna=False).to_string())
print("\nname_src:", minr['name_src'].value_counts(dropna=False).to_string())
