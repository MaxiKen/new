"""Geology: gap-fill v2 by NEIGHBOUR EXTENSION (no new classes), polygonize, closed Nigeria boundary."""
import json, sys, time
sys.path.insert(0,"scripts")
import numpy as np, cv2
from PIL import Image
from scipy import ndimage
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union, transform as shp_transform
from shapely.validation import make_valid
import rasterio
from rasterio.transform import Affine
from rasterio.features import shapes as rio_shapes
Image.MAX_IMAGE_PIXELS=None
t0=time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a)

# --- composed transform v2 px (continuous) -> lonlat ---
gj = json.load(open("work/georef_geology.json"))
glon = np.array(gj["glon"]); glat = np.array(gj["glat"])  # lon=glon0*u+glon1, u=jpg continuous X
reg = json.load(open("work/register_v2_final.json")); A = np.array(reg["A"])
# median tile correction (+0.90,+0.14) full jpg px: output jpg point = A(v2)+corr
A_corr = A.copy(); A_corr[0,2]+=0.90; A_corr[1,2]+=0.14
log("A corrected:\n", A_corr)
# OpenCV coords (centre-integer) -> continuous: X = x_cv+0.5 ; Xj = Alin*Xv + (t + 0.5 - Alin@0.5)
Alin = A_corr[:,:2]; tvec = A_corr[:,2]
t_cont = tvec + 0.5 - Alin @ np.array([0.5,0.5])
# lonlat: lon = glon0*Xj + glon1 ; lat = glat0*Yj + glat1
M = np.zeros((2,3))
M[0,:2] = glon[0]*Alin[0,:]; M[0,2] = glon[0]*t_cont[0]+glon[1]
M[1,:2] = glat[0]*Alin[1,:]; M[1,2] = glat[0]*t_cont[1]+glat[1]
log("v2 continuous -> lonlat M:\n", M)
# test centre
cx, cy = 3861.0, 3214.0
lonlat = M[:,:2]@np.array([cx+0.5,cy+0.5])+M[:,2]
xj = A_corr[:,:2]@np.array([cx,cy])+A_corr[:,2]
lonlat2 = np.array([glon[0]*(xj[0]+0.5)+glon[1], glat[0]*(xj[1]+0.5)+glat[1]])
log("centre check composed", lonlat, "two-step", lonlat2, "diff", np.abs(lonlat-lonlat2).max())
def px_to_lonlat(xs, ys):
    """xs,ys in raster continuous coords (pixel (c,r) corner=(c,r), centre=(c+.5,r+.5))."""
    lon = M[0,0]*xs + M[0,1]*ys + M[0,2]
    lat = M[1,0]*xs + M[1,1]*ys + M[1,2]
    return lon, lat
json.dump(dict(M=M.tolist(), A_corrected=A_corr.tolist()), open("work/v2_to_lonlat.json","w"), indent=1)

# --- load v2, gap analysis + fill ---
v2pil = Image.open("NGSA_map_geology_legend_isolated_v2.png")
pal = v2pil.getpalette()
idx = np.array(v2pil)
H,W = idx.shape
log(f"v2 {W}x{H} units present (incl bg): {len(np.unique(idx))}")
fg = idx!=0
# exterior background via flood from border (connected components of background)
nlab, lab = cv2.connectedComponents((~fg).astype(np.uint8), connectivity=4)
border_labels = set(np.unique(np.r_[lab[0,:], lab[-1,:], lab[:,0], lab[:,-1]])) - {0}
is_exterior = np.isin(lab, list(border_labels))
gaps = (~fg) & (~is_exterior)
log(f"background components={nlab-1} exterior labels={sorted(border_labels)}")
log(f"GAP pixels (enclosed white inland): {gaps.sum():,} ({gaps.mean()*100:.4f}% of image; {gaps.sum()/fg.sum()*100:.4f}% of Nigeria area)")
# gap component sizes
ng, lg, stats, _ = cv2.connectedComponentsWithStats(gaps.astype(np.uint8), 8)
sizes = np.sort(stats[1:, cv2.CC_STAT_AREA])[::-1] if ng>1 else np.array([])
log(f"gap components: {ng-1}; largest 15 sizes px: {sizes[:15]}")
log(f" gaps >1000px: {(sizes>1000).sum()}, 100-1000: {((sizes>=100)&(sizes<=1000)).sum()}, <100: {(sizes<100).sum()}")
# largest gap locations (lonlat of centroids approx via moments)
gap_info=[]
if ng>1:
    cents = ndimage.center_of_mass(gaps, lg, range(1,ng))
    order = np.argsort(-stats[1:,cv2.CC_STAT_AREA])[:12]
    for o in order:
        gy,gx = cents[o]; lon,lat = px_to_lonlat(gx+0.5, gy+0.5)
        gap_info.append(dict(px=int(stats[1+o, cv2.CC_STAT_AREA]), lon=float(lon), lat=float(lat)))
        log(f"  gap {stats[1+o,cv2.CC_STAT_AREA]:6d} px at approx Lon {lon:.3f} Lat {lat:.3f}")
# Fill gaps by nearest foreground unit (extension of existing polygons; NO new classes)
filled = idx.copy()
if gaps.any():
    # distance_transform_edt on gaps: for gap px, nearest non-gap... need nearest FG: compute on ~fg within interior? Use EDT of fg complement restricted: indices of nearest fg pixel for every pixel
    inds = ndimage.distance_transform_edt(~fg, return_distances=False, return_indices=True)
    filled[gaps] = idx[tuple(ind[gaps] for ind in inds)]
    del inds
log(f"after fill: enclosed gaps remaining = {int(((filled==0)&(~is_exterior)).sum())}; units={len(np.unique(filled))} (must equal before={len(np.unique(idx))})")
new_classes = set(np.unique(filled)) - set(np.unique(idx))
log(f"new classes created by fill: {new_classes} (must be empty set)")
np.save("work/v2_filled_idx.npy", filled)
json.dump(dict(gap_px=int(gaps.sum()), gap_components=int(ng-1), gap_sizes_top=sizes[:30].tolist() if len(sizes) else [], gap_locs=gap_info),
          open("work/geology_gaps.json","w"), indent=1)

# --- write paletted GeoTIFFs (original with holes + filled) ---
aff = Affine(M[0,0], M[0,1], M[0,2], M[1,0], M[1,1], M[1,2])
cmap = {i: tuple(pal[i*3:i*3+3])+(255,) for i in range(256) if pal[i*3:i*3+3]}
def write_pal(path, arr, desc):
    prof = dict(driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1, dtype="uint8",
                crs="EPSG:4326", transform=aff, compress="lzw", tiled=True, blockxsize=256, blockysize=256, nodata=0)
    with rasterio.open(path,"w",**prof) as ds:
        ds.write(arr,1); ds.write_colormap(1, cmap); ds.update_tags(DESCRIPTION=desc)
        ds.build_overviews([2,4,8,16], rasterio.enums.Resampling.nearest)
    log("wrote", path)
write_pal("output/01_Georeferenced_Rasters/Geology_isolated_ORIGINAL_with_holes_georeferenced.tif", idx,
          "Isolated NGSA geology as supplied (v2), georeferenced EPSG:4326. Interior white gaps preserved. Paletted units; 0=background/nodata.")
write_pal("output/01_Georeferenced_Rasters/Geology_isolated_FILLED_georeferenced.tif", filled,
          "Isolated NGSA geology with inland gaps filled by extension of nearest existing unit (no new units). EPSG:4326. Paletted; 0=outside Nigeria.")
log(f"filled GeoTIFF extent: {rasterio.transform.array_bounds(H,W,aff)}")

# --- polygonize filled (in pixel coords, then transform) ---
log("polygonizing filled raster (GDAL)... this may take a few minutes")
mask = filled!=0
# rasterio shapes needs transform; use identity in px then map manually
poly_rows=[]
for geom, val in rio_shapes(filled, mask=mask):
    poly_rows.append((int(val), geom))
log(f"raw polygons: {len(poly_rows)}")
# Build shapely in px coords, simplify coverage-aware-ish: small tolerance then fix in lonlat stage
geoms_px=[]; units=[]
for val, geom in poly_rows:
    g = shape(geom)
    if g.is_empty: continue
    # simplify in px (0.7 px) - shared-edge slivers fixed after transform
    try:
        g2 = g.simplify(0.7, preserve_topology=True)
        if g2.is_empty: g2=g
    except Exception:
        g2=g
    geoms_px.append(g2); units.append(val)
log(f"polygons kept: {len(geoms_px)} total vertices(px stage)={sum(len(g.exterior.coords) if g.geom_type=='Polygon' else sum(len(p.exterior.coords) for p in g.geoms) for g in geoms_px):,}")
# transform to lonlat (coords from rio_shapes with identity transform are (col,row) corner-continuous; y increases downward in image rows but shape coords follow raster transform identity -> (x=col, y=row) ??? 
# rasterio.features.shapes with default transform=identity yields coords in pixel space with y = row (down). Our M expects continuous (X=col, Y=row) same. Good.
def to_ll(g):
    return shp_transform(lambda xs, ys, zs=None: px_to_lonlat(xs, ys), g)
geoms_ll=[to_ll(g) for g in geoms_px]
gdf = gpd.GeoDataFrame(dict(UNIT_IDX=units), geometry=geoms_ll, crs="EPSG:4326")
gdf = gdf[~gdf.geometry.is_empty].copy()
log(f"lonlat polygons: {len(gdf)} bounds={gdf.total_bounds}")

# --- boundary from filled mask silhouette ---
log("building boundary...")
bmask = (filled!=0).astype(np.uint8)
bgeoms=[]
for geom, val in rio_shapes(bmask, mask=bmask.astype(bool)):
    bgeoms.append(shape(geom))
bunion = unary_union(bgeoms)
if bunion.geom_type=="MultiPolygon":
    parts = sorted(bunion.geoms, key=lambda p:-p.area)
    log(f"boundary multipolygon parts={len(parts)} areas px2 top5={[round(p.area) for p in parts[:5]]}")
    bmain = parts[0]
    # keep only main + any parts > 5000 px (islands?) as multipolygon
    keep=[p for p in parts if p.area>5000]
    log(f"keeping {len(keep)} boundary parts >5000px")
    bmain = unary_union(keep)
else:
    bmain = bunion
bmain_s = bmain.simplify(0.8, preserve_topology=True)
b_ll = to_ll(bmain_s)
b_ll = make_valid(b_ll)
bg = gpd.GeoDataFrame([dict(NAME="Nigeria", SOURCE="NGSA geology base outline (isolated v2) georeferenced; land border verified vs NGSA Mineral Map 2023 vector")], geometry=[b_ll], crs="EPSG:4326")
area_km2 = bg.to_crs("EPSG:6933").area.iloc[0]/1e6
bg["AREA_KM2"]=round(float(area_km2),1)
log(f"Boundary area: {area_km2:,.0f} km2 bounds={bg.total_bounds}")
# compare vs mineral land border line
lb = gpd.read_file("work/Nigeria_LandBorder.geojson")
line = lb.geometry.iloc[0]
from shapely.ops import nearest_points
# sample land border every ~0.02deg along line: interpolate points, distance to boundary polygon boundary
bnd_line = b_ll.boundary
dists=[]
L=line.length
for d in np.linspace(0, L, 800):
    p = line.interpolate(d)
    dists.append(p.distance(bnd_line))
dists=np.array(dists)
log(f"Mineral land-border vs Geology boundary edge (deg): median={np.median(dists):.5f} (~{np.median(dists)*111:.2f} km) mean={dists.mean():.5f} p90={np.percentile(dists,90):.5f} (~{np.percentile(dists,90)*111:.2f} km) max={dists.max():.5f}")
json.dump(dict(boundary_area_km2=float(area_km2), landborder_median_deg=float(np.median(dists)), landborder_p90_deg=float(np.percentile(dists,90)), landborder_max_deg=float(dists.max())),
          open("work/boundary_compare.json","w"), indent=1)
bg.to_file("output/02_Shapefiles/Nigeria_Boundary.shp")
bg.to_file("work/Nigeria_Boundary_final.geojson", driver="GeoJSON")
lb.to_file("output/02_Shapefiles/Nigeria_LandBorder_NGSA2023.shp")
log("wrote Nigeria_Boundary.shp + land border line")

# --- coverage fix: overlaps + gaps vs boundary (extend neighbours for gaps) ---
log("coverage validation/fix...")
# Intersection with boundary (clip) then check union coverage
gdf["geometry"] = gdf.geometry.intersection(b_ll)
gdf = gdf[~gdf.geometry.is_empty].copy()
gdf = gdf.explode(index_parts=False).reset_index(drop=True)
gdf = gdf[gdf.geometry.geom_type.isin(["Polygon"])].copy()
log(f"after boundary clip+explode: {len(gdf)} polygons")
union_g = unary_union(gdf.geometry.values)
gap_geom = b_ll.difference(union_g)
over_area = union_g.difference(b_ll).area
log(f"gap area deg2={gap_geom.area:.6f} ({gap_geom.area/b_ll.area*100:.4f}% of boundary); overshoot={over_area:.8f}")
gaps_list=[]
if not gap_geom.is_empty:
    gg = [gap_geom] if gap_geom.geom_type=="Polygon" else list(gap_geom.geoms) if gap_geom.geom_type in ("MultiPolygon","GeometryCollection") else []
    gg=[g for g in gg if g.geom_type=="Polygon" and g.area>0]
    log(f"gap pieces to assign: {len(gg)} total {sum(g.area for g in gg):.6f} deg2; largest={max([g.area for g in gg], default=0):.6f}")
    # assign each gap to adjacent polygon with longest shared border (touch via slight buffer)
    sindex = gdf.sindex
    add_rows={}  # gdf index -> list of gap geoms to union
    for gi, gap in enumerate(gg):
        cand_idx = list(sindex.intersection(gap.bounds))
        best=None; best_len=-1
        for ci in cand_idx:
            # position-based: sindex returns positions
            poly = gdf.geometry.iloc[ci]
            shared = gap.intersection(poly.buffer(1e-7)).area  # proxy; better: boundary intersection length
            try:
                bl = gap.boundary.intersection(poly.boundary).length
            except Exception:
                bl=0
            # fallback: if boundaries don't exactly touch (simplification), use distance
            score = bl if bl>0 else -gap.distance(poly)
            if score>best_len: best_len=score; best=ci
        if best is None:
            # nearest polygon overall
            d = gdf.geometry.distance(gap)
            best = int(d.idxmin()) if hasattr(d.idxmin(), "__int__") else int(gdf.index[d.argmin()])
            # convert label to position
            best = gdf.index.get_loc(best) if best in gdf.index else int(d.argmin())
        add_rows.setdefault(best, []).append(gap)
    for pos, glist in add_rows.items():
        gdf.geometry.iloc[pos] = unary_union([gdf.geometry.iloc[pos]]+glist)
    # re-check (unions may create multipolygons; explode again, keep unit)
    gdf = gdf.explode(index_parts=False).reset_index(drop=True)
    gdf = gdf[gdf.geometry.geom_type=="Polygon"]
    union2 = unary_union(gdf.geometry.values)
    gap2 = b_ll.difference(union2)
    log(f"after neighbour-extension assignment: residual gap={gap2.area:.8f} deg2 ({gap2.area/b_ll.area*100:.5f}%) polygons={len(gdf)}")
# overlaps between geology polygons (pairwise) - measure via union vs sum
sum_area = gdf.geometry.area.sum()
union_area = unary_union(gdf.geometry.values).area
log(f"sum polygon areas={sum_area:.5f} union={union_area:.5f} overlap excess={sum_area-union_area:.6f} deg2 ({(sum_area-union_area)/union_area*100:.4f}%) boundary area={b_ll.area:.5f} coverage={union_area/b_ll.area*100:.3f}%")
# attributes
pal_arr = np.array([pal[i*3:(i+1)*3] if i*3 < len(pal) else [0,0,0] for i in range(256)])
gdf["R"]=[int(pal_arr[u][0]) for u in gdf["UNIT_IDX"]]
gdf["G"]=[int(pal_arr[u][1]) for u in gdf["UNIT_IDX"]]
gdf["B"]=[int(pal_arr[u][2]) for u in gdf["UNIT_IDX"]]
gdf["HEX"]=[f"#{int(pal_arr[u][0]):02x}{int(pal_arr[u][1]):02x}{int(pal_arr[u][2]):02x}" for u in gdf["UNIT_IDX"]]
areas = gdf.to_crs("EPSG:6933").area/1e6
gdf["AREA_KM2"]=areas.round(4).values
gdf = gdf.sort_values(["UNIT_IDX"], kind="stable").reset_index(drop=True)
gdf.insert(0,"POLY_ID", range(1,len(gdf)+1))
log(f"final geology polygons={len(gdf)} units={gdf['UNIT_IDX'].nunique()} total area={gdf['AREA_KM2'].sum():,.0f} km2")
gdf.to_file("work/Geology_Rocks_no_names.geojson", driver="GeoJSON")
# save palette table
import csv
with open("output/04_Tables/Geology_colour_table.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["UNIT_IDX","R","G","B","HEX","pixels_filled","area_km2_polygons","n_polygons"])
    for u in sorted(gdf["UNIT_IDX"].unique()):
        sub=gdf[gdf["UNIT_IDX"]==u]
        w.writerow([int(u), int(pal_arr[u][0]),int(pal_arr[u][1]),int(pal_arr[u][2]), f"#{int(pal_arr[u][0]):02x}{int(pal_arr[u][1]):02x}{int(pal_arr[u][2]):02x}", int((filled==u).sum()), round(sub["AREA_KM2"].sum(),2), len(sub)])
json.dump(dict(n_polygons=int(len(gdf)), n_units=int(gdf["UNIT_IDX"].nunique()), total_area_km2=float(gdf["AREA_KM2"].sum()),
               coverage_pct=float(union_area/b_ll.area*100)), open("work/geology_stats.json","w"), indent=1)
log("DONE 04")
