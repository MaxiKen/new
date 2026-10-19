import pymupdf, numpy as np, geopandas as gpd
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import unary_union
import warnings; warnings.filterwarnings('ignore')

admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp").geometry.iloc[0]
AEA="+proj=aea +lat_1=4 +lat_2=12 +lat_0=0 +lon_0=9 +datum=WGS84 +units=m +no_defs +type=crs"
adm_m=gpd.GeoSeries([admin],crs=4326).to_crs(AEA).iloc[0]
adm_line_m=adm_m.boundary

def stats(name, lonlat_pts):
    pts=gpd.GeoSeries([Point(x,y) for x,y in lonlat_pts],crs=4326).to_crs(AEA)
    d=np.array([p.distance(adm_line_m) for p in pts])
    print(f"{name:28s} n={len(d)} median={np.median(d)/1000:.2f}km p90={np.percentile(d,90)/1000:.2f} p95={np.percentile(d,95)/1000:.2f} max={d.max()/1000:.1f} mean={d.mean()/1000:.2f}")
    return d

# --- Mineral red boundary vectors -> page pts sampled ---
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'); p=d[0]
red=[x for x in p.get_drawings() if x.get('color')==(0.901960015296936,0,0)]
page_pts=[]
for dr in red:
    for it in dr['items']:
        if it[0]=='l':
            page_pts.append((it[1].x,it[1].y)); page_pts.append((it[2].x,it[2].y))
        elif it[0]=='c':
            page_pts.append((it[1].x,it[1].y)); page_pts.append((it[4].x,it[4].y))
page_pts=np.array(page_pts)
# subsample by spacing in page coords (keep every nth after dedup-ish)
idx=np.arange(0,len(page_pts),3); page_pts=page_pts[idx]
print(f"mineral red boundary sample pts: {len(page_pts)}")

def grat(px,py): # from graticule LINES: x 341.4386=4E spacing 157.5997/deg (315.199/2); y 523.5256=13N spacing 157.6017/deg
    lon=4+(px-341.4386)/157.5997; lat=13-(py-523.5256)/157.6017; return lon,lat
def vp(px,py):
    u=(px-74.23969)/(2051.1915-74.23969); v=(py-358.7239)/(1967.7011-358.7239)
    return (2.47619+u*(15.02138-2.47619), 14.04668-v*(14.04668-3.83671))
def bf(px,py):
    yb=2160-py
    return (8.999624062683695+6.3408036208710055*(px-1104.0922160059586)/1000, 10.488502044741583+6.350936179071387*(yb-1241.0996111966826)/1000)
for name,f in [("MINERAL graticule",grat),("MINERAL VP",vp),("MINERAL boundary-fit(prev)",bf)]:
    ll=np.array([f(x,y) for x,y in page_pts]); stats(name,ll)
# graticule +0.172 lon shift test
ll=np.array([ (grat(x,y)[0]+0.172, grat(x,y)[1]) for x,y in page_pts]); stats("MINERAL grat+0.172lon",ll)

# --- Geology: outer boundary of union ---
geo=gpd.read_file("shapefile_results/geology/nigeria_geology_units.shp")
uni=unary_union(geo.geometry.values)
# sample points along union boundary every ~2km in AEA then back? simpler: densify boundary lines coords subsample
coords=[]
b=uni.boundary
lines=list(b.geoms) if b.geom_type=='MultiLineString' else [b]
for ln in lines:
    coords.extend(list(ln.coords))
coords=np.array(coords)
print(f"\ngeology union boundary vertices: {len(coords)}")
# Only vertices near admin boundary (<0.15deg) are national-border segments; interior hole boundaries far from admin would inflate stats.
# Pre-filter: distance to admin_line < 25km in AEA
pts_m=gpd.GeoSeries([Point(x,y) for x,y in coords],crs=4326).to_crs(AEA)
d0=np.array([p.distance(adm_line_m) for p in pts_m])
mask=d0<25000
print(f"near-border vertices: {mask.sum()}")
sel=coords[mask]
stats("GEOLOGY as-is (graticule fit)", sel)
for dlon in [-0.172,-0.05,-0.02,0.02,0.05,0.172]:
    stats(f"GEOLOGY shift lon {dlon:+.3f}", sel+np.array([dlon,0]))
for dlat in [-0.05,-0.02,0.02,0.05]:
    stats(f"GEOLOGY shift lat {dlat:+.3f}", sel+np.array([0,dlat]))
# signed east-west analysis: for near-border pts on west/east borders compare lon to nearest admin point lon
