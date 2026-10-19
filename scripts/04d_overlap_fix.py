import sys; sys.path.insert(0,"scripts")
import numpy as np, geopandas as gpd
from shapely.ops import unary_union
from shapely.validation import make_valid
allg=gpd.read_file("work/Geology_Rocks_complete_no_names.geojson")
Bfinal=gpd.read_file("work/Nigeria_Boundary_FINAL2.geojson").geometry.iloc[0]
print(f"loaded {len(allg)} polys")
sindex=allg.sindex
geoms=list(allg.geometry)
is_strip=(allg["SRC"]!="v2").values
print("strip polys:", is_strip.sum())
# Priority: main first (keep), strip polys subtract overlapping higher-priority geometry.
# Process strip polys in descending area; maintain list of processed strip geoms for subtraction among strips.
order=np.argsort([-geoms[i].area if is_strip[i] else 0 for i in range(len(geoms))])
strip_order=[i for i in order if is_strip[i]]
fixed=0; removed_area=0.0
for rank,i in enumerate(strip_order):
    g=geoms[i]
    cand=list(sindex.intersection(g.bounds))
    # higher priority = all main + strip earlier in order
    higher=[geoms[j] for j in cand if j!=i and ((not is_strip[j]) or strip_order.index(j)<rank if False else False)]
    # (avoid O(n) index lookup: precompute rank dict)
    if rank==0:
        pass
    # redo with rank dict (computed outside loop in real run below)
    break
rank_of={idx:r for r,idx in enumerate(strip_order)}
for i in strip_order:
    g=geoms[i]; orig_area=g.area
    cand=list(sindex.intersection(g.bounds))
    subs=[]
    for j in cand:
        if j==i: continue
        if (not is_strip[j]) or (rank_of[j]<rank_of[i]):
            try:
                inter=g.intersection(geoms[j])
            except Exception:
                inter=make_valid(g).intersection(make_valid(geoms[j]))
            if not inter.is_empty and inter.area>1e-12:
                subs.append(geoms[j])
    if subs:
        try:
            g2=g.difference(unary_union(subs))
        except Exception:
            g2=make_valid(g).difference(unary_union([make_valid(s) for s in subs]))
        if g2.area<orig_area-1e-12:
            fixed+=1; removed_area+=orig_area-g2.area
        geoms[i]=g2
print(f"strip polys trimmed={fixed} overlap area removed={removed_area:.6f} deg2")
allg["geometry"]=geoms
allg=allg[~allg.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
allg=allg[allg.geometry.geom_type=="Polygon"].reset_index(drop=True)
union_g=unary_union(list(allg.geometry))
print(f"n={len(allg)} sum={float(allg.geometry.area.sum()):.5f} union={union_g.area:.5f} excess={float(allg.geometry.area.sum())-union_g.area:.7f} coverage={union_g.area/Bfinal.area*100:.5f}% gap={Bfinal.difference(union_g).area:.8f}")
allg["AREA_KM2"]=(allg.to_crs("EPSG:6933").area/1e6).round(4).values
allg=allg.sort_values(["UNIT_IDX","SRC"],kind="stable").reset_index(drop=True)
allg["POLY_ID"]=range(1,len(allg)+1)
allg.to_file("work/Geology_Rocks_complete_no_names.geojson", driver="GeoJSON")
print("saved. area km2", float(allg["AREA_KM2"].sum()))
