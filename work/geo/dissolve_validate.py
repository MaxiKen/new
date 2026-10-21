import geopandas as gpd, numpy as np, shapely, warnings, pickle, json, time
from shapely.ops import unary_union
from collections import defaultdict, Counter
warnings.filterwarnings('ignore')
t0=time.time()
KM2=12266.0

geo=gpd.read_file('shapefile_results/geology/nigeria_geology_units.shp')
ref=gpd.read_file('shapefiles/nigeria_admin0/nigeria_admin0.shp').geometry.iloc[0]
d=pickle.load(open('work/geo/faces_final.pkl','rb')); faces=d['faces']; in_ref=d['in_ref']
a=pickle.load(open('work/geo/assign_final2.pkl','rb')); assign=a['assign']; method=a['method']
print(f"faces {len(faces)}, active {np.sum(in_ref&(assign>=0))}")

byfid=defaultdict(list)
for i in range(len(faces)):
    if in_ref[i] and assign[i]>=0: byfid[int(assign[i])].append(i)
print(f"features receiving faces: {len(byfid)} / {len(geo)}")
missing=[j for j in range(len(geo)) if j not in byfid]
print(f"source features with NO area inside ref after rebuild: {len(missing)}")
for j in missing:
    g=geo.geometry.iloc[j]
    inter=g.intersection(ref).area
    print(f"  fid{j} unit={geo.unit.iloc[j]!r} area_km2={geo.area_km2.iloc[j]:.1f} inside_ref_km2={inter*KM2:.2f} src_seq={geo.src_seq.iloc[j]}")

rows=[]
for j in sorted(byfid):
    geoms=[faces[i] for i in byfid[j]]
    u=unary_union(geoms)
    if u.geom_type=='GeometryCollection':
        u=unary_union([x for x in u.geoms if x.geom_type in ('Polygon','MultiPolygon')])
    row=geo.iloc[j].copy()
    row['geometry']=u
    rows.append(row)
out=gpd.GeoDataFrame(rows, crs='EPSG:4326').reset_index(drop=True)
print(f"rebuilt features: {len(out)}  [{time.time()-t0:.0f}s]")

# recompute area/perim/centroid/n_rings in EPSG:32632
m=out.to_crs('EPSG:32632')
out['area_km2']=(m.geometry.area/1e6).round(3).values
out['perim_km']=(m.geometry.length/1e3).round(3).values
cen=out.geometry.centroid
out['cen_lon']=cen.x.values; out['cen_lat']=cen.y.values
def nrings(g):
    if g.geom_type=='Polygon': return 1+len(g.interiors)
    if g.geom_type=='MultiPolygon': return sum(1+len(p.interiors) for p in g.geoms)
    return 0
out['n_rings']=[nrings(g) for g in out.geometry]

# qa_flag per feature: gained vs trimmed (compare with original by original index = row order of `rows` from sorted byfid keys)
flags=[]
orig_idx=sorted(byfid.keys())
for k,j in enumerate(orig_idx):
    newg=out.geometry.iloc[k]; oldg=geo.geometry.iloc[j]
    gained=newg.difference(oldg).area*KM2
    outside=oldg.difference(ref).area*KM2
    lost_in=oldg.intersection(ref).difference(newg).area*KM2
    tag=[]
    if gained>=0.05: tag.append('extended')
    if outside>=0.05: tag.append('trimmed')
    if lost_in>=0.05: tag.append('overlap_adj')
    flags.append('+'.join(tag) if tag else 'unchanged')
out['qa_flag']=flags
print("qa_flag:", Counter(flags).most_common())

# ---- validation ----
union_new=unary_union(out.geometry.values)
sym=union_new.symmetric_difference(ref)
sum_area=out.geometry.area.sum()
print(f"\nVALIDATION:")
print(f" union area deg2={union_new.area:.6f} ref={ref.area:.6f} symdiff={sym.area:.8f} deg2 (~{sym.area*KM2:.3f} km2)")
print(f" gap remaining (ref-union): {ref.difference(union_new).area*KM2:.4f} km2")
print(f" overhang (union-ref): {union_new.difference(ref).area*KM2:.4f} km2")
print(f" sum(feature areas)={sum_area:.6f} union={union_new.area:.6f} overlap_excess={(sum_area-union_new.area)*KM2:.4f} km2")
print(f" valid: {out.geometry.is_valid.sum()}/{len(out)}  empty: {out.geometry.is_empty.sum()}")
print(f" geom types: {Counter(out.geometry.geom_type)}")
inv=out[~out.geometry.is_valid]
if len(inv): print(" invalid rows:", inv.index.tolist(), [shapely.validation.explain_validity(g) for g in inv.geometry])

out2=out.copy()
# keep original field order + qa_flag at end (before geometry)
cols=[c for c in geo.columns if c!='geometry']+['qa_flag','geometry']
out2=out2[cols]
out2.to_file('deliverables_flat/nigeria_geology_units.shp', driver='ESRI Shapefile', engine='pyogrio')
print("\nwrote deliverables_flat/nigeria_geology_units.shp")
# re-read check
chk=gpd.read_file('deliverables_flat/nigeria_geology_units.shp')
print(" reread:", len(chk), chk.crs, "fields:", list(chk.columns)[:8], "... total", len(chk.columns))
print(" reread qa_flag sample:", chk.qa_flag.value_counts().to_dict() if 'qa_flag' in chk else 'MISSING')

rep={'source_features':int(len(geo)),'output_features':int(len(out)),
     'dropped_features':[{'fid':int(j),'unit':str(geo.unit.iloc[j]),'area_km2':float(geo.area_km2.iloc[j]),
                           'inside_ref_km2':float(geo.geometry.iloc[j].intersection(ref).area*KM2)} for j in missing],
     'symdiff_km2':float(sym.area*KM2),'gap_remaining_km2':float(ref.difference(union_new).area*KM2),
     'overhang_km2':float(union_new.difference(ref).area*KM2),'overlap_excess_km2':float((sum_area-union_new.area)*KM2),
     'valid':int(out.geometry.is_valid.sum()),'qa_flags':Counter(flags)}
json.dump(rep, open('work/geo/geology_rebuild_report.json','w'), indent=1, default=str)
print("saved report")
