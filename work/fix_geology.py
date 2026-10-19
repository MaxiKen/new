"""Geology fix: start from ORIGINAL (with holes), planarize by draw order, clip to Nigeria, fill gaps by extending neighbours.
Only ONE new polygon: Lake Chad open water. All other gaps assigned to existing neighbouring features."""
import geopandas as gpd, numpy as np, pandas as pd, json, time
from shapely.ops import unary_union
from shapely import voronoi_polygons
from shapely.geometry import MultiPoint, Polygon, MultiPolygon, GeometryCollection
from shapely import make_valid
from shapely.strtree import STRtree
from scipy.spatial import cKDTree
import warnings; warnings.filterwarnings('ignore')
t0=time.time()
AEA="+proj=aea +lat_1=4 +lat_2=12 +lat_0=0 +lon_0=9 +datum=WGS84 +units=m +no_defs +type=crs"
def area_km2(geoms_ll):
    return gpd.GeoSeries(geoms_ll,crs=4326).to_crs(AEA).area.values/1e6
def polys_only(g):
    if g is None or g.is_empty: return g
    if isinstance(g,(Polygon,MultiPolygon)): return g
    parts=[x for x in getattr(g,'geoms',[]) if isinstance(x,(Polygon,MultiPolygon))]
    # flatten nested
    flat=[]
    for x in parts:
        flat.extend(list(x.geoms) if isinstance(x,MultiPolygon) else [x])
    if not flat: return Polygon()
    return unary_union(flat)

geo=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp").geometry.iloc[0]
print(f"start features {len(geo)} src_seq unique={geo.src_seq.nunique()} [{time.time()-t0:.0f}s]")
orig_area=area_km2(geo.geometry.values)
geo=geo.assign(_orig_area=orig_area)
# order: later drawn (higher src_seq) on top -> process descending, claim unclaimed
order=np.argsort(-geo.src_seq.values)
claimed=Polygon()
newgeom=[None]*len(geo)
for k,idx in enumerate(order):
    g=geo.geometry.iloc[idx]
    if not claimed.is_empty:
        g=g.difference(claimed)
        g=polys_only(make_valid(g)) if not g.is_empty else g
    newgeom[idx]=g
    if g is not None and not g.is_empty:
        claimed=unary_union([claimed,g]) if not claimed.is_empty else g
    if k%300==0: print(f" planar {k}/{len(order)} claimed_parts ok [{time.time()-t0:.0f}s]")
planar_area=area_km2([g if g is not None else Polygon() for g in newgeom])
overlap_lost=geo._orig_area.values-planar_area
print(f"planar done: empty(fully covered/dup)={sum(1 for g in newgeom if g is None or g.is_empty)} overlap area removed total={np.maximum(overlap_lost,0).sum():.1f} km2 [{time.time()-t0:.0f}s]")
# clip to admin
clipped=[]; clip_lost=np.zeros(len(geo))
for i,g in enumerate(newgeom):
    if g is None or g.is_empty: clipped.append(Polygon()); continue
    c=polys_only(make_valid(g.intersection(admin)))
    clipped.append(c)
clip_area=area_km2(clipped)
clip_lost=planar_area-clip_area
print(f"clip done: fully outside={sum(1 for i,g in enumerate(clipped) if g.is_empty and planar_area[i]>0.01)} clipped-away total={np.maximum(clip_lost,0).sum():.1f} km2")
keep=[i for i,g in enumerate(clipped) if not g.is_empty and clip_area[i]>1e-6]
dropped=[]
for i in range(len(geo)):
    if i not in keep:
        r=geo.iloc[i]
        reason="exact/covered duplicate (fully under later-drawn polygons)" if planar_area[i]<=1e-6 else "fully outside Nigeria boundary after clipping"
        dropped.append({"orig_index":int(i),"src_seq":int(r.src_seq),"code":str(r.code),"unit":str(r.unit),"dup_of":int(r.dup_of),"orig_area_km2":round(float(orig_area[i]),3),"reason":reason})
print(f"kept {len(keep)} dropped {len(dropped)}")
work=geo.iloc[keep].copy().reset_index(drop=True)
work['geometry']=[clipped[i] for i in keep]
work['_ovlap_km']=[float(overlap_lost[i]) for i in keep]
work['_clip_km']=[float(clip_lost[i]) for i in keep]
work['_orig_km']=[float(orig_area[i]) for i in keep]
# gaps
union_now=unary_union(work.geometry.values)
gap=admin.difference(union_now)
gparts=sorted(list(gap.geoms) if isinstance(gap,MultiPolygon) else [gap], key=lambda g:-g.area) if not gap.is_empty else []
gareas=area_km2(gparts) if gparts else np.array([])
print(f"gaps to fill: {len(gparts)} total {gareas.sum() if len(gareas) else 0:.1f} km2; largest {gareas[:5]} [{time.time()-t0:.0f}s]")
# Lake Chad water: largest gap, centroid NE
water_ids=[]
for gi,g in enumerate(gparts):
    c=g.centroid
    if gareas[gi]>1000 and c.x>13 and c.y>12.5: water_ids.append(gi)
print("water gap ids:", water_ids)
# neighbour assignment
geoms=list(work.geometry.values)
tree=STRtree(geoms)
assignments={i:[] for i in range(len(work))}  # work index -> list of gap parts
gaplog=[]
def shared_len(a,b):
    try: return a.boundary.intersection(b.buffer(0.00012)).length
    except: return 0.0
for gi,g in enumerate(gparts):
    if gi in water_ids: continue
    cand=[int(j) for j in tree.query(g.buffer(0.002),predicate='intersects')]
    # keep candidates actually touching/very near (dist <0.002 deg ~220m); if none, nearest feature overall
    cand=[j for j in cand if geoms[j].distance(g)<0.0022]
    method=""
    if len(cand)==0:
        j=int(tree.nearest(g)); cand=[j]; method="nearest-feature (isolated gap)"
        assignments[j].append(g); parts_desc=f"{work.iloc[j].code}:100%"
    elif len(cand)==1:
        assignments[cand[0]].append(g); method="single-neighbour extension"; parts_desc=f"{work.iloc[cand[0]].code}:100%"
    else:
        # Voronoi split by densified neighbour boundary seeds near gap
        done=False
        try:
            # seed spacing adaptive: gap mean width approx 2A/P (deg); spacing = width/4 bounded [25m,300m]
            Adeg=g.area; Pdeg=g.length
            wid=2*Adeg/Pdeg if Pdeg>0 else 0.001
            spacing=float(np.clip(wid/4, 0.00022, 0.0027))
            search=g.buffer(max(spacing*3,0.001))
            seeds=[]; labels=[]
            for j in cand:
                bl=geoms[j].boundary.intersection(search)
                lines=list(bl.geoms) if hasattr(bl,'geoms') and bl.geom_type not in ('LineString','LinearRing') else [bl]
                pts=[]
                for ln in lines:
                    if ln.is_empty or not hasattr(ln,'length') or ln.length==0:
                        if hasattr(ln,'coords'): pts.extend(list(ln.coords))
                        continue
                    nseg=max(1,int(ln.length/spacing))
                    pts.extend([(ln.interpolate(d).x, ln.interpolate(d).y) for d in np.linspace(0,ln.length,nseg+1)])
                # fallback: vertices of candidate within search
                if len(pts)<2:
                    pts=[c for part in (list(geoms[j].geoms) if geoms[j].geom_type=='MultiPolygon' else [geoms[j]]) for ring in [part.exterior]+list(part.interiors) for c in ring.coords if search.contains(Point(c))] if False else pts
                seeds.extend(pts); labels.extend([j]*len(pts))
            seeds=np.array(seeds); labels=np.array(labels)
            if len(seeds)>=4 and len(set(labels.tolist()))>=2:
                vor=voronoi_polygons(MultiPoint(seeds.tolist()), extend_to=g)
                cells=list(vor.geoms) if hasattr(vor,'geoms') else [vor]
                kdt=cKDTree(seeds)
                acc={j:[] for j in cand}
                for cell in cells:
                    part=polys_only(cell.intersection(g))
                    if part.is_empty or part.area<=0: continue
                    rp=part.representative_point()
                    _,si=kdt.query([rp.x,rp.y])
                    acc[int(labels[si])].append(part)
                covered=sum(unary_union(v).area if v else 0 for v in acc.values())
                if covered>=0.999*g.area:
                    desc=[]
                    for j,v in acc.items():
                        if v:
                            u=unary_union(v); assignments[j].append(u); desc.append(f"{work.iloc[j].code}:{100*u.area/g.area:.0f}%")
                    residue=g.difference(unary_union([unary_union(v) for v in acc.values() if v]))
                    if not residue.is_empty and residue.area>0:
                        # residue to longest-border candidate
                        lens=[(shared_len(geoms[j],g),j) for j in cand]; jbest=max(lens)[1]
                        assignments[jbest].append(polys_only(residue))
                    method="multi-neighbour Voronoi split (nearest extension)"; parts_desc="; ".join(sorted(desc)); done=True
        except Exception as e:
            pass  # counted in method fallback
        if not done:
            lens=[(shared_len(geoms[j],g),j) for j in cand]; jbest=max(lens)[1]
            assignments[jbest].append(g); method="longest-shared-border extension (Voronoi fallback)"; parts_desc=f"{work.iloc[jbest].code}:100%"
    gaplog.append({"gap_id":int(gi),"area_km2":round(float(gareas[gi]),4),"centroid_lon":round(float(g.centroid.x),5),"centroid_lat":round(float(g.centroid.y),5),
                   "touches_border":bool(g.distance(admin.boundary)<0.002),"method":method,"assigned_to":parts_desc,
                   "neighbour_codes":";".join(sorted(set(str(work.iloc[j].code) for j in cand)))})
    if gi%200==0: print(f" gaps {gi}/{len(gparts)} [{time.time()-t0:.0f}s]")
# apply extensions
filled_km=np.zeros(len(work))
newg=[]
for i in range(len(work)):
    if assignments[i]:
        u=polys_only(make_valid(unary_union([work.geometry.iloc[i]]+assignments[i])))
        newg.append(u)
    else:
        newg.append(work.geometry.iloc[i])
work['geometry']=newg
after_area=area_km2(work.geometry.values)
before_area=clip_area[[keep.index(i) if False else 0 for i in []]] if False else None
# clip_area aligned to orig index; map:
clip_map={orig_i:clip_area[orig_i] for orig_i in keep}
# work order corresponds to keep order
filled_km=after_area-np.array([clip_area[i] for i in keep])
work['_filled_km']=filled_km
# add water polygon(s)
for gi in water_ids:
    gaplog.append({"gap_id":int(gi),"area_km2":round(float(gareas[gi]),4),"centroid_lon":round(float(gparts[gi].centroid.x),5),"centroid_lat":round(float(gparts[gi].centroid.y),5),
                   "touches_border":True,"method":"NEW POLYGON (necessary): Lake Chad open water","assigned_to":"WATER:100%","neighbour_codes":"Cst"})
print(f"extensions applied. residual check... [{time.time()-t0:.0f}s]")
union2=unary_union(work.geometry.values)
# include water in union check separately
water_union=unary_union([gparts[gi] for gi in water_ids]) if water_ids else Polygon()
resid=admin.difference(unary_union([union2,water_union]))
resid_parts=list(resid.geoms) if isinstance(resid,MultiPolygon) else ([resid] if not resid.is_empty else [])
ra=area_km2(resid_parts) if resid_parts else np.array([])
print(f"RESIDUAL gaps after fill: {len(resid_parts)} total {ra.sum() if len(ra) else 0:.4f} km2 max {ra.max() if len(ra) else 0:.4f}")
# clean micro-residuals to nearest (longest border)
if len(resid_parts)>0 and ra.sum()>1e-6:
    geoms2=list(work.geometry.values); tree2=STRtree(geoms2)
    extra={i:[] for i in range(len(work))}
    for rp in resid_parts:
        cand=[int(j) for j in tree2.query(rp.buffer(0.002),predicate='intersects')]
        if not cand: cand=[int(tree2.nearest(rp))]
        lens=[(shared_len(geoms2[j],rp),j) for j in cand]; jbest=max(lens)[1]
        extra[jbest].append(rp)
    for i in range(len(work)):
        if extra[i]: work.geometry.iloc[i]=polys_only(make_valid(unary_union([work.geometry.iloc[i]]+extra[i])))
    # note: direct iloc set on geometry column - rebuild
    work=gpd.GeoDataFrame(work,geometry='geometry',crs=4326)
    union3=unary_union(work.geometry.values)
    resid2=admin.difference(unary_union([union3,water_union]))
    rp2=list(resid2.geoms) if isinstance(resid2,MultiPolygon) else ([resid2] if not resid2.is_empty else [])
    ra2=area_km2(rp2) if rp2 else np.array([])
    print(f" after micro-clean residual: {len(rp2)} total {ra2.sum() if len(ra2) else 0:.6f} km2")
work.to_file("work/geology_filled_pre.pkl", driver="GeoJSON") if False else None
import pickle
with open("work/geology_filled_state.pkl","wb") as f:
    pickle.dump({"work":work,"gaplog":gaplog,"dropped":dropped,"water_geoms":[gparts[gi] for gi in water_ids],"water_ids":water_ids,"gareas":gareas},f)
print(f"saved state. kept={len(work)} time {time.time()-t0:.0f}s")
