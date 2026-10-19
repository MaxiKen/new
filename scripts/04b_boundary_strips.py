"""Final boundary (v2 + west strip + Chad sector) and strip geology digitized from Geology JPG."""
import json, sys, time
sys.path.insert(0,"scripts")
import numpy as np, cv2
from PIL import Image
import geopandas as gpd
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely.validation import make_valid
from scipy import ndimage
import rasterio
from rasterio.transform import Affine
from rasterio.features import shapes as rio_shapes, rasterize
Image.MAX_IMAGE_PIXELS=None
t0=time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a)

gj = json.load(open("work/georef_geology.json")); glon=np.array(gj["glon"]); glat=np.array(gj["glat"])
def jpg_px_to_lonlat(col,row):  # pixel indices (centres)
    return glon[0]*(np.asarray(col,float)+0.5)+glon[1], glat[0]*(np.asarray(row,float)+0.5)+glat[1]
def lonlat_to_jpg_px(lon,lat):
    return (np.asarray(lon,float)-glon[1])/glon[0]-0.5, (np.asarray(lat,float)-glat[1])/glat[0]-0.5

ne = gpd.read_file("work/NE_Nigeria.geojson").geometry.iloc[0]
Bgeo = gpd.read_file("work/Nigeria_Boundary_final.geojson").geometry.iloc[0]
Bgeo = make_valid(Bgeo)
if Bgeo.geom_type=="MultiPolygon": Bgeo = unary_union(Bgeo)
diff = ne.difference(Bgeo)
pieces = sorted([p for p in (list(diff.geoms) if diff.geom_type=="MultiPolygon" else [diff]) if p.geom_type=="Polygon"], key=lambda p:-p.area)
log(f"NE-Bgeo pieces: {len(pieces)} top areas={[round(p.area,4) for p in pieces[:4]]}")
west = max(pieces, key=lambda p:p.area if p.centroid.x<4 else 0)
chad = max(pieces, key=lambda p:p.area if p.centroid.x>10 and p.centroid.y>12 else 0)
log(f"west piece area={west.area:.4f} bounds={west.bounds} centroid={west.centroid}")
log(f"chad piece area={chad.area:.4f} bounds={chad.bounds} centroid={chad.centroid}")
Bfinal = unary_union([Bgeo, west, chad])
Bfinal = make_valid(Bfinal)
log(f"Bfinal type={Bfinal.geom_type} area_deg2={Bfinal.area:.4f} bounds={Bfinal.bounds}")
bg = gpd.GeoDataFrame([dict(NAME="Nigeria", SOURCE="NGSA geology outline; west strip (W of 3.01E, S of 9.08N) + Lake Chad sector restored from Natural Earth where supplied v2 was clipped")], geometry=[Bfinal], crs="EPSG:4326")
area_km2 = float(bg.to_crs("EPSG:6933").area.iloc[0]/1e6)
bg["AREA_KM2"]=round(area_km2,1)
log(f"FINAL boundary area={area_km2:,.0f} km2 (NE=907,498; official total=923,768 incl waters)")
bg.to_file("output/02_Shapefiles/Nigeria_Boundary.shp")
bg.to_file("work/Nigeria_Boundary_FINAL2.geojson", driver="GeoJSON")
# save strip pieces for QA
gpd.GeoDataFrame(geometry=[west,chad], crs="EPSG:4326").assign(PIECE=["west_strip","chad_sector"]).to_file("work/strip_pieces.geojson", driver="GeoJSON")

# ---- JPG-space palette per v2 unit ----
log("building JPG-space palette from overlap...")
jpg = cv2.imread("pic NGSA geological-map-of-nigeria-.jpg")  # BGR
Hj,Wj = jpg.shape[:2]
v2idx = np.load("work/v2_filled_idx.npy")
reg = json.load(open("work/v2_to_lonlat.json")); A = np.array(reg["A_corrected"], dtype=np.float32)
warped_idx = cv2.warpAffine(v2idx, A, (Wj,Hj), flags=cv2.INTER_NEAREST, borderValue=0)
log(f"warped v2 idx onto JPG: fg={np.mean(warped_idx!=0):.3f}")
units = sorted([int(u) for u in np.unique(v2idx) if u!=0])
jpg_rgb = cv2.cvtColor(jpg, cv2.COLOR_BGR2RGB).astype(float)
pal_v2 = Image.open("NGSA_map_geology_legend_isolated_v2.png").getpalette()
jpg_pal={}; v2_pal={}
rng=np.random.default_rng(42)
kernel=np.ones((5,5),np.uint8)
for u in units:
    v2_pal[u]=np.array(pal_v2[u*3:u*3+3],float)
    m=(warped_idx==u).astype(np.uint8)
    if m.sum()<200:
        jpg_pal[u]=v2_pal[u]; continue
    me=cv2.erode(m,kernel)
    ys,xs=np.where(me>0)
    if len(ys)>20000:
        sel=rng.choice(len(ys),20000,replace=False); ys,xs=ys[sel],xs[sel]
    if len(ys)==0:
        ys,xs=np.where(m>0)
    jpg_pal[u]=np.median(jpg_rgb[ys,xs],axis=0)
log("palette built. Examples (unit: v2RGB -> JPGmedianRGB):")
for u in units[:6]: log(f" {u}: {v2_pal[u]} -> {jpg_pal[u].round(1)}")

def classify_window(piece_geom, tag):
    minlon,minlat,maxlon,maxlat = piece_geom.bounds
    c0,r1 = lonlat_to_jpg_px(minlon,minlat); c1,r0 = lonlat_to_jpg_px(maxlon,maxlat)
    c0,c1 = int(max(0,np.floor(min(c0,c1)))), int(min(Wj-1,np.ceil(max(c0,c1))))
    r0i,r1i = int(max(0,np.floor(min(r0,r1)))), int(min(Hj-1,np.ceil(max(r0,r1))))
    log(f"{tag}: JPG window cols[{c0},{c1}] rows[{r0i},{r1i}] ({c1-c0+1}x{r1i-r0i+1})")
    win = jpg_rgb[r0i:r1i+1, c0:c1+1]  # RGB float
    wh,ww = win.shape[:2]
    # mask inside piece (rasterize in window lonlat grid): use pixel-centre lonlat + point-in-polygon via rasterio rasterize with window affine
    aff_win = Affine(glon[0],0,glon[0]*c0+glon[1],0,glat[0],glat[0]*r0i+glat[1])
    inside = rasterize([(piece_geom,1)], out_shape=(wh,ww), transform=aff_win, fill=0, dtype=np.uint8).astype(bool)
    log(f" inside px={inside.sum()}")
    # reject linework/text/sea/white: saturation & value rules in RGB
    mx=win.max(axis=2); mn=win.min(axis=2); sat=mx-mn
    dark = mx<75
    whiteish = mn>238
    greyish = (sat<28)&(mx>90)  # roads/grid/text grey (geology fills are saturated; some pale units risk -> majority+fill recovers)
    sea_rgb = np.array([151.,219.,242.])  # JPG sea RGB approx (BGR 242,219,151 -> RGB 151,219,242?) check: sample below overrides
    # sample sea from JPG gulf px (col 500,row 3300)
    sea_rgb = jpg_rgb[3300,500]
    dist_sea = np.sqrt(((win-sea_rgb)**2).sum(axis=2))
    sea = dist_sea<38
    valid = inside & (~dark) & (~whiteish) & (~greyish) & (~sea)
    log(f" valid classified px={valid.sum()} ({valid.sum()/max(inside.sum(),1)*100:.1f}% of inside); sea_rgb={sea_rgb}")
    # nearest JPG-palette classification (chunked rows)
    U=np.array(units); P=np.array([jpg_pal[u] for u in units])
    cls=np.zeros((wh,ww),dtype=np.uint8)
    flat=win.reshape(-1,3); vf=valid.ravel()
    idxs=np.where(vf)[0]
    for s in range(0,len(idxs),40000):
        chunk=flat[idxs[s:s+40000]]
        d=((chunk[:,None,:]-P[None,:,:])**2).sum(axis=2)
        cls.ravel()[idxs[s:s+40000]]=U[np.argmin(d,axis=1)]
    # majority filter 5x5 over classified (mode via per-unit blur argmax is heavy; use median on cls? median of labels wrong. Use: fill invalid by nearest valid first, then 3x3 mode approx via cv2.medianBlur on label image (labels ordinal not meaningful but locally majority approx - skip; instead small opening per total? Keep as is + neighbour fill)
    # neighbour fill inside piece (extend nearest classified unit)
    unk = inside & (cls==0)
    if unk.any() and valid.any():
        inds=ndimage.distance_transform_edt(cls==0, return_distances=False, return_indices=True)
        cls[unk]=cls[tuple(ind[unk] for ind in inds)]
    log(f" after neighbour fill unfilled inside={int((inside&(cls==0)).sum())}; units in {tag}={sorted(np.unique(cls[inside]).tolist())}")
    cv2.imwrite(f"work/strip_{tag}_classified.png", (cls.astype(np.uint16)*3).astype(np.uint8))
    # polygonize with window affine (lonlat directly)
    rows=[]
    for geom,val in rio_shapes(cls, mask=inside, transform=aff_win):
        if val==0: continue
        g=shape(geom)
        g=g.intersection(piece_geom)
        if g.is_empty: continue
        # simplify ~0.7 JPG px in degrees (0.7*0.003)
        g2=g.simplify(0.0021, preserve_topology=True)
        if g2.is_empty: g2=g
        rows.append((int(val), g2))
    log(f" {tag} polygons={len(rows)}")
    g = gpd.GeoDataFrame(dict(UNIT_IDX=[r[0] for r in rows]), geometry=[r[1] for r in rows], crs="EPSG:4326")
    g=g.explode(index_parts=False).reset_index(drop=True)
    g=g[g.geometry.geom_type=="Polygon"]
    g["SRC"]=tag
    return g

west_g = classify_window(west, "JPG_west_strip")
chad_g = classify_window(chad, "JPG_chad_sector")

# ---- merge with main geology ----
main = gpd.read_file("work/Geology_Rocks_no_names.geojson")
main["SRC"]="v2"
log(f"main polygons={len(main)} west={len(west_g)} chad={len(chad_g)}")
# ensure main clipped to Bgeo complement (main already covers Bgeo; strips cover pieces; union should tile Bfinal)
allg = gpd.GeoDataFrame(
    dict(UNIT_IDX=list(main["UNIT_IDX"])+list(west_g["UNIT_IDX"])+list(chad_g["UNIT_IDX"]),
         SRC=list(main["SRC"])+list(west_g["SRC"])+list(chad_g["SRC"])),
    geometry=list(main.geometry)+list(west_g.geometry)+list(chad_g.geometry), crs="EPSG:4326")
# final clip to Bfinal + coverage check
allg["geometry"]=allg.geometry.intersection(Bfinal)
allg=allg[~allg.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
allg=allg[allg.geometry.geom_type=="Polygon"]
union_g=unary_union(allg.geometry.values)
gap=Bfinal.difference(union_g)
sumarea=allg.geometry.area.sum()
log(f"MERGED polygons={len(allg)} coverage={union_g.area/Bfinal.area*100:.4f}% gap_deg2={gap.area:.6f} overlap_excess={(sumarea-union_g.area):.6f}")
if gap.area>1e-9:
    # assign residual slivers to nearest polygon (neighbour extension)
    from shapely.ops import nearest_points
    gg=[gap] if gap.geom_type=="Polygon" else [g for g in gap.geoms if g.geom_type=="Polygon"] if gap.geom_type in ("MultiPolygon","GeometryCollection") else []
    log(f" residual gap pieces={len(gg)} - assigning to nearest neighbours")
    sindex=allg.sindex
    adds={}
    for piece in gg:
        cand=list(sindex.intersection(piece.bounds))
        best=None;bd=1e9
        for ci in cand:
            d=piece.distance(allg.geometry.iloc[ci])
            if d<bd: bd=d;best=ci
        if best is None:
            d=allg.geometry.distance(piece); best=int(np.argmin(d.values))
        adds.setdefault(best,[]).append(piece)
    for pos,glist in adds.items():
        allg.geometry.iloc[pos]=unary_union([allg.geometry.iloc[pos]]+glist)
    allg=allg.explode(index_parts=False).reset_index(drop=True)
    allg=allg[allg.geometry.geom_type=="Polygon"]
    union_g=unary_union(allg.geometry.values)
    log(f" after sliver assignment coverage={union_g.area/Bfinal.area*100:.5f}% gap={Bfinal.difference(union_g).area:.8f}")
pal_arr=np.array([[pal_v2[i*3],pal_v2[i*3+1],pal_v2[i*3+2]] if i*3+2<len(pal_v2) else [0,0,0] for i in range(256)])
allg["R"]=[int(pal_arr[u][0]) for u in allg["UNIT_IDX"]]; allg["G"]=[int(pal_arr[u][1]) for u in allg["UNIT_IDX"]]; allg["B"]=[int(pal_arr[u][2]) for u in allg["UNIT_IDX"]]
allg["HEX"]=[f"#{int(pal_arr[u][0]):02x}{int(pal_arr[u][1]):02x}{int(pal_arr[u][2]):02x}" for u in allg["UNIT_IDX"]]
allg["AREA_KM2"]=(allg.to_crs("EPSG:6933").area/1e6).round(4).values
allg=allg.sort_values(["UNIT_IDX","SRC"],kind="stable").reset_index(drop=True)
allg.insert(0,"POLY_ID",range(1,len(allg)+1))
log(f"FINAL geology polygons={len(allg)} units={allg['UNIT_IDX'].nunique()} area={allg['AREA_KM2'].sum():,.0f} km2 by SRC:\n{allg.groupby('SRC')['AREA_KM2'].agg(['count','sum'])}")
allg.to_file("work/Geology_Rocks_complete_no_names.geojson", driver="GeoJSON")
# complete raster from final polygons at ~v2 resolution (0.0015deg)
log("rasterizing complete geology...")
res=0.0015; minx,miny,maxx,maxy = Bfinal.bounds
W=int(np.ceil((maxx-minx)/res)); H=int(np.ceil((maxy-miny)/res))
aff_c=Affine(res,0,minx,0,-res,maxy)
ras=rasterize([(g,int(u)) for g,u in zip(allg.geometry, allg["UNIT_IDX"])], out_shape=(H,W), transform=aff_c, fill=0, dtype=np.uint8)
cmap={i: tuple(int(v) for v in pal_arr[i])+(255,) for i in range(256)}
prof=dict(driver="GTiff",height=H,width=W,count=1,dtype="uint8",crs="EPSG:4326",transform=aff_c,compress="lzw",tiled=True,blockxsize=256,blockysize=256,nodata=0)
with rasterio.open("output/01_Georeferenced_Rasters/Geology_Rocks_raster_COMPLETE.tif","w",**prof) as ds:
    ds.write(ras,1); ds.write_colormap(1,cmap)
    ds.update_tags(DESCRIPTION="Complete geology rasterized from final Geology_Rocks polygons (v2 + restored west strip + Chad sector). Paletted UNIT_IDX, 0=outside Nigeria. EPSG:4326, 0.0015deg.")
    ds.build_overviews([2,4,8,16], rasterio.enums.Resampling.nearest)
log(f"complete raster {W}x{H} wrote")
json.dump(dict(boundary_area_km2=area_km2, n_polygons=int(len(allg)), coverage_pct=float(union_g.area/Bfinal.area*100)), open("work/geology_final_stats.json","w"), indent=1)
log("DONE 04b")
