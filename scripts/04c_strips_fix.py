"""Fix west-strip classification (regularized) + Chad neighbour-extension + exact coverage merge."""
import json, sys, time
sys.path.insert(0,"scripts")
import numpy as np, cv2
from PIL import Image
import geopandas as gpd
from shapely.geometry import shape
from shapely.ops import unary_union
from scipy import ndimage
import rasterio
from rasterio.transform import Affine
from rasterio.features import shapes as rio_shapes, rasterize
Image.MAX_IMAGE_PIXELS=None
t0=time.time()
def log(*a): print(f"[{time.time()-t0:5.1f}s]", *a)
gj=json.load(open("work/georef_geology.json")); glon=np.array(gj["glon"]); glat=np.array(gj["glat"])
def lonlat_to_jpg_px(lon,lat): return (np.asarray(lon,float)-glon[1])/glon[0]-0.5, (np.asarray(lat,float)-glat[1])/glat[0]-0.5
Bfinal=gpd.read_file("work/Nigeria_Boundary_FINAL2.geojson").geometry.iloc[0]
pieces=gpd.read_file("work/strip_pieces.geojson")
west=pieces[pieces["PIECE"]=="west_strip"].geometry.iloc[0]
chad=pieces[pieces["PIECE"]=="chad_sector"].geometry.iloc[0]
main=gpd.read_file("work/Geology_Rocks_no_names.geojson")
log(f"main={len(main)}")

jpg=cv2.imread("pic NGSA geological-map-of-nigeria-.jpg"); Hj,Wj=jpg.shape[:2]
jpg_rgb=cv2.cvtColor(jpg,cv2.COLOR_BGR2RGB).astype(float)
v2idx=np.load("work/v2_filled_idx.npy")
reg=json.load(open("work/v2_to_lonlat.json")); A=np.array(reg["A_corrected"],dtype=np.float32)
warped_idx=cv2.warpAffine(v2idx,A,(Wj,Hj),flags=cv2.INTER_NEAREST,borderValue=0)
pal_v2=Image.open("NGSA_map_geology_legend_isolated_v2.png").getpalette()
units_all=sorted([int(u) for u in np.unique(v2idx) if u!=0])
rng=np.random.default_rng(42); kernel=np.ones((5,5),np.uint8)
jpg_pal={}
for u in units_all:
    m=(warped_idx==u).astype(np.uint8)
    if m.sum()<200: jpg_pal[u]=np.array(pal_v2[u*3:u*3+3],float); continue
    me=cv2.erode(m,kernel); ys,xs=np.where(me>0)
    if len(ys)>20000: sel=rng.choice(len(ys),20000,replace=False); ys,xs=ys[sel],xs[sel]
    if len(ys)==0: ys,xs=np.where(m>0)
    jpg_pal[u]=np.median(jpg_rgb[ys,xs],axis=0)
log("palette ready")

# ---- WEST strip regularized classification ----
minlon,minlat,maxlon,maxlat=west.bounds
c0f,r1f=lonlat_to_jpg_px(minlon,minlat); c1f,r0f=lonlat_to_jpg_px(maxlon,maxlat)
c0,c1=int(max(0,np.floor(min(c0f,c1f)))),int(min(Wj-1,np.ceil(max(c0f,c1f))))
r0i,r1i=int(max(0,np.floor(min(r0f,r1f)))),int(min(Hj-1,np.ceil(max(r0f,r1f))))
log(f"west window cols[{c0},{c1}] rows[{r0i},{r1i}]")
# candidate units: in warped v2 within window expanded east 450px (seam continuity) 
cand_region=warped_idx[r0i:r1i+1, c0:min(Wj,c1+450)]
cand=sorted([int(u) for u in np.unique(cand_region) if u!=0])
log(f"candidate units near seam ({len(cand)}): {cand}")
win=jpg_rgb[r0i:r1i+1,c0:c1+1]; wh,ww=win.shape[:2]
aff_win=Affine(glon[0],0,glon[0]*c0+glon[1],0,glat[0],glat[0]*r0i+glat[1])
inside=rasterize([(west,1)],out_shape=(wh,ww),transform=aff_win,fill=0,dtype=np.uint8).astype(bool)
mx=win.max(axis=2); mn=win.min(axis=2); sat=mx-mn
sea_rgb=jpg_rgb[3300,500]
dist_sea=np.sqrt(((win-sea_rgb)**2).sum(axis=2))
valid=inside&(mx>=75)&(mn<=238)&~((sat<28)&(mx>90))&(dist_sea>=38)
P=np.array([jpg_pal[u] for u in cand]); U=np.array(cand)
cls=np.zeros((wh,ww),np.uint8)
flat=win.reshape(-1,3); idxs=np.where(valid.ravel())[0]
for s in range(0,len(idxs),40000):
    ch=flat[idxs[s:s+40000]]
    d=((ch[:,None,:]-P[None,:,:])**2).sum(axis=2)
    cls.ravel()[idxs[s:s+40000]]=U[np.argmin(d,axis=1)]
log(f"raw classified valid={valid.sum()}/{inside.sum()}")
# neighbour fill inside
unk=inside&(cls==0)
inds=ndimage.distance_transform_edt(cls==0,return_distances=False,return_indices=True)
cls[unk]=cls[tuple(i[unk] for i in inds)]
# majority (mode) filter 7x7 x2 via one-hot uniform counts (candidates only), restricted to inside
def majority(cls, inside, cand, size=7, iters=2):
    cur=cls.copy()
    for _ in range(iters):
        counts=np.stack([ndimage.uniform_filter((cur==u).astype(float), size=size, mode="nearest") for u in cand])
        nxt=np.array(cand)[np.argmax(counts,axis=0)].astype(np.uint8)
        cur=np.where(inside, nxt, cur)
    return cur
cls=majority(cls, inside, cand, 7, 2)
# MMU: absorb components <25px (set 0, EDT refill), twice
for it in range(2):
    changed=False
    lab,n=ndimage.label(cls!=0)  # not per-unit; do per-unit below
    # per-unit components
    out=cls.copy()
    for u in cand:
        l2,n2=ndimage.label(cls==u)
        if n2==0: continue
        sizes=ndimage.sum(np.ones_like(l2), l2, range(1,n2+1))
        small=[i+1 for i,s in enumerate(sizes) if s<25]
        if small:
            out[np.isin(l2,small)]=0; changed=True
    if changed:
        z=inside&(out==0)
        inds=ndimage.distance_transform_edt(out==0,return_distances=False,return_indices=True)
        out[z]=out[tuple(i[z] for i in inds)]
        cls=out
    else: break
log(f"west regularized units={sorted(np.unique(cls[inside]).tolist())}")
def polygonize_window(cls, inside, aff, piece, simplify_deg=0.0015):
    rows=[]
    for geom,val in rio_shapes(cls, mask=inside, transform=aff):
        if val==0: continue
        g=shape(geom)
        g=g.intersection(piece)
        if g.is_empty: continue
        g2=g.simplify(simplify_deg, preserve_topology=True)
        if g2.is_empty: g2=g
        # re-clip simplified to piece to avoid overshoot into main
        g2=g2.intersection(piece)
        if not g2.is_empty: rows.append((int(val),g2))
    g=gpd.GeoDataFrame(dict(UNIT_IDX=[r[0] for r in rows]), geometry=[r[1] for r in rows], crs="EPSG:4326")
    g=g.explode(index_parts=False).reset_index(drop=True)
    return g[g.geometry.geom_type=="Polygon"].reset_index(drop=True)
def fill_gaps_in_piece(g, piece, tag):
    # assign (piece - union) slivers to neighbouring polygons in g (longest shared border; proper list update)
    geoms=list(g.geometry); units=list(g["UNIT_IDX"])
    union_g=unary_union(geoms)
    gap=piece.difference(union_g)
    if gap.is_empty or gap.area<=0: log(f"{tag}: no gaps"); return g
    gg=[gap] if gap.geom_type=="Polygon" else [x for x in gap.geoms if x.geom_type=="Polygon"] if gap.geom_type in ("MultiPolygon","GeometryCollection") else []
    log(f"{tag}: gap pieces={len(gg)} area={gap.area:.6f} deg2 -> assigning to neighbours")
    tmp=gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326"); sindex=tmp.sindex
    adds={}
    for piece_g in gg:
        cand_i=list(sindex.intersection(piece_g.bounds))
        best=None; best_score=-1e18
        for ci in cand_i:
            bl=piece_g.boundary.intersection(geoms[ci].boundary).length
            score=bl if bl>0 else -piece_g.distance(geoms[ci])-1e-9
            if score>best_score: best_score=score; best=ci
        if best is None: continue
        adds.setdefault(best,[]).append(piece_g)
    for pos,glist in adds.items():
        geoms[pos]=unary_union([geoms[pos]]+glist)
    g2=gpd.GeoDataFrame(dict(UNIT_IDX=units), geometry=geoms, crs="EPSG:4326")
    g2=g2.explode(index_parts=False).reset_index(drop=True)
    g2=g2[g2.geometry.geom_type=="Polygon"].reset_index(drop=True)
    # clip any overshoot from unions back to piece union main? unions of gap+poly stay inside piece. verify:
    u2=unary_union(list(g2.geometry))
    log(f"{tag}: after assignment residual gap in piece={piece.difference(u2).area:.8f} deg2, polys={len(g2)}")
    return g2
west_g=polygonize_window(cls, inside, aff_win, west)
west_g["SRC"]="JPG_west_strip"
west_g=fill_gaps_in_piece(west_g, west, "west")
west_g["SRC"]="JPG_west_strip"
log(f"west polygons final={len(west_g)} units={sorted(west_g['UNIT_IDX'].unique().tolist())}")

# ---- CHAD sector by neighbour extension from main geology (raster EDT on lonlat grid) ----
log("Chad sector extension...")
res=0.0015
minlon,minlat,maxlon,maxlat=chad.bounds
pad=0.35
gx0,gy1=minlon-pad*0,maxlat  # grid covering piece + south shore seed band: expand south/west into main
gx_min, gy_min, gx_max, gy_max = minlon-0.05, minlat-0.45, maxlon+0.05, maxlat+0.02
W=int(np.ceil((gx_max-gx_min)/res)); H=int(np.ceil((gy_max-gy_min)/res))
aff_c=Affine(res,0,gx_min,0,-res,gy_max)
# seed: rasterize main polygons (subset intersecting grid bbox)
from shapely.geometry import box as shpbox
sub=main[main.geometry.intersects(shpbox(gx_min,gy_min,gx_max,gy_max))]
log(f"chad seed main polygons={len(sub)}")
seed=rasterize([(g,int(u)) for g,u in zip(sub.geometry, sub["UNIT_IDX"])], out_shape=(H,W), transform=aff_c, fill=0, dtype=np.uint8)
pmask=rasterize([(chad,1)], out_shape=(H,W), transform=aff_c, fill=0, dtype=np.uint8).astype(bool)
fill=seed.copy()
need=pmask&(fill==0)
inds=ndimage.distance_transform_edt(fill==0,return_distances=False,return_indices=True)
fill[need]=fill[tuple(i[need] for i in inds)]
log(f"chad filled units={sorted(np.unique(fill[pmask]).tolist())} counts="+str({int(u):int((fill[pmask]==u).sum()) for u in np.unique(fill[pmask])}))
chad_g=polygonize_window(fill, pmask, aff_c, chad, simplify_deg=0.0015)
chad_g=fill_gaps_in_piece(chad_g, chad, "chad")
chad_g["SRC"]="JPG_chad_sector"
log(f"chad polygons final={len(chad_g)}")

# ---- merge + validate ----
main2=main.copy(); main2["SRC"]="v2"
allg=gpd.GeoDataFrame(dict(UNIT_IDX=list(main2["UNIT_IDX"])+list(west_g["UNIT_IDX"])+list(chad_g["UNIT_IDX"]),
                           SRC=list(main2["SRC"])+list(west_g["SRC"])+list(chad_g["SRC"])),
                      geometry=list(main2.geometry)+list(west_g.geometry)+list(chad_g.geometry), crs="EPSG:4326")
union_g=unary_union(list(allg.geometry))
gap=Bfinal.difference(union_g); over=union_g.difference(Bfinal)
sumarea=float(allg.geometry.area.sum())
# overlaps only possible at seams (simplify wobble of strip polys was clipped to pieces; main inside Bgeo) -> measure pairwise excess
log(f"MERGED n={len(allg)} coverage={union_g.area/Bfinal.area*100:.5f}% gap={gap.area:.7f} over={over.area:.7f} overlap_excess={sumarea-union_g.area:.7f} deg2")
# remove tiny overlaps at seams: clip strip polys already to pieces; if excess>1e-6, subtract main-union from strip polys
if sumarea-union_g.area>1e-6:
    log("removing seam overlaps (strip polys minus main union)...")
    main_union=unary_union(list(main2.geometry))
    geoms=list(allg.geometry)
    nmain=len(main2)
    for i in range(nmain, len(geoms)):
        g=geoms[i].difference(main_union)
        geoms[i]=g
    allg["geometry"]=geoms
    allg=allg[~allg.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
    allg=allg[allg.geometry.geom_type=="Polygon"].reset_index(drop=True)
    union_g=unary_union(list(allg.geometry)); sumarea=float(allg.geometry.area.sum())
    log(f" after de-overlap: n={len(allg)} excess={sumarea-union_g.area:.8f} coverage={union_g.area/Bfinal.area*100:.5f}%")
if Bfinal.difference(union_g).area>1e-7:
    allg=fill_gaps_in_piece(allg, Bfinal, "FINAL")
    # fill_gaps returns without SRC? it reconstructs UNIT only -> restore SRC by re-join on order? Instead handle: redo with SRC preserved
    union_g=unary_union(list(allg.geometry))
    log(f"FINAL coverage={union_g.area/Bfinal.area*100:.5f}% gap={Bfinal.difference(union_g).area:.8f}")
# NOTE: fill_gaps_in_piece drops SRC column when called on allg; guard:
if "SRC" not in allg.columns:
    log("WARNING SRC dropped in final gap fill - reassign by centroid in pieces")
    def src_of(g):
        c=g.centroid
        if west.contains(c): return "JPG_west_strip"
        if chad.contains(c): return "JPG_chad_sector"
        return "v2"
    allg["SRC"]=[src_of(g) for g in allg.geometry]
pal_arr=np.array([[pal_v2[i*3],pal_v2[i*3+1],pal_v2[i*3+2]] if i*3+2<len(pal_v2) else [0,0,0] for i in range(256)])
allg["R"]=[int(pal_arr[u][0]) for u in allg["UNIT_IDX"]]; allg["G"]=[int(pal_arr[u][1]) for u in allg["UNIT_IDX"]]; allg["B"]=[int(pal_arr[u][2]) for u in allg["UNIT_IDX"]]
allg["HEX"]=[f"#{int(pal_arr[u][0]):02x}{int(pal_arr[u][1]):02x}{int(pal_arr[u][2]):02x}" for u in allg["UNIT_IDX"]]
allg["AREA_KM2"]=(allg.to_crs("EPSG:6933").area/1e6).round(4).values
allg=allg.sort_values(["UNIT_IDX","SRC"],kind="stable").reset_index(drop=True)
allg.insert(0,"POLY_ID",range(1,len(allg)+1))
union_g=unary_union(list(allg.geometry))
log(f"FINAL geology n={len(allg)} units={allg['UNIT_IDX'].nunique()} area={allg['AREA_KM2'].sum():,.0f} km2 coverage={union_g.area/Bfinal.area*100:.4f}%")
log("\n"+str(allg.groupby("SRC")["AREA_KM2"].agg(["count","sum"])))
allg.to_file("work/Geology_Rocks_complete_no_names.geojson", driver="GeoJSON")
# complete raster redo
res=0.0015; minx,miny,maxx,maxy=Bfinal.bounds
W=int(np.ceil((maxx-minx)/res)); H=int(np.ceil((maxy-miny)/res))
aff_r=Affine(res,0,minx,0,-res,maxy)
ras=rasterize([(g,int(u)) for g,u in zip(allg.geometry,allg["UNIT_IDX"])], out_shape=(H,W), transform=aff_r, fill=0, dtype=np.uint8)
cmap={i: tuple(int(v) for v in pal_arr[i])+(255,) for i in range(256)}
prof=dict(driver="GTiff",height=H,width=W,count=1,dtype="uint8",crs="EPSG:4326",transform=aff_r,compress="lzw",tiled=True,blockxsize=256,blockysize=256,nodata=0)
with rasterio.open("output/01_Georeferenced_Rasters/Geology_Rocks_raster_COMPLETE.tif","w",**prof) as ds:
    ds.write(ras,1); ds.write_colormap(1,cmap)
    ds.update_tags(DESCRIPTION="Complete geology rasterized from final Geology_Rocks polygons. Paletted UNIT_IDX, 0=outside. EPSG:4326 0.0015deg.")
    ds.build_overviews([2,4,8,16], rasterio.enums.Resampling.nearest)
json.dump(dict(n_polygons=int(len(allg)), coverage_pct=float(union_g.area/Bfinal.area*100), area_km2=float(allg["AREA_KM2"].sum())), open("work/geology_final_stats.json","w"), indent=1)
log("DONE 04c")
