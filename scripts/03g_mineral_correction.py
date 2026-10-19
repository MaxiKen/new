"""Final mineral absolute correction: Chamfer border alignment + reliable named towns. Geology validated ~0."""
import sys, json; sys.path.insert(0,"scripts")
import numpy as np, geopandas as gpd
from scipy import ndimage
from shapely.geometry import Point

ne = gpd.read_file("work/NE_Nigeria.geojson").geometry.iloc[0]
lb = gpd.read_file("work/Nigeria_LandBorder.geojson").geometry.iloc[0]
def coords_of(g):
    if g.geom_type in ("LineString","LinearRing"): return np.array(g.coords)
    if g.geom_type=="Polygon": return np.array(g.exterior.coords)
    if g.geom_type=="MultiLineString": return np.vstack([np.array(x.coords) for x in g.geoms])
    if g.geom_type=="MultiPolygon": return np.vstack([np.array(x.exterior.coords) for x in g.geoms])
    raise ValueError(g.geom_type)
NEp = coords_of(ne.boundary)
# densify both by interpolation along lines for chamfer point sets
def densify(line, step=0.01):
    n=max(100,int(line.length/step)); pts=[line.interpolate(d) for d in np.linspace(0,line.length,n)]
    return np.array([(p.x,p.y) for p in pts])
NEline = ne.boundary
# NE boundary may be MultiLineString (islands/lake): densify each part >1deg length (mainland)
parts = [NEline] if NEline.geom_type=="LineString" else list(NEline.geoms)
NEpts = np.vstack([densify(p) for p in parts if p.length>1.0])
MINpts = densify(lb)
print(f"NE border pts={len(NEpts)} mineral pts={len(MINpts)}")
# Raster EDT for NE border: grid 0.002deg over [2,15.2]x[3.8,14.4]
res=0.002; x0,x1,y0,y1=2.0,15.2,3.8,14.4
W=int((x1-x0)/res)+1; H=int((y1-y0)/res)+1
grid=np.ones((H,W),bool)
ix=np.round((NEpts[:,0]-x0)/res).astype(int); iy=np.round((NEpts[:,1]-y0)/res).astype(int)
ok=(ix>=0)&(ix<W)&(iy>=0)&(iy<H); grid[iy[ok],ix[ok]]=False
edt = ndimage.distance_transform_edt(grid)*res
print("EDT ready", edt.shape)
def chamfer(dx,dy,pts):
    X=pts[:,0]+dx; Y=pts[:,1]+dy
    ix=np.round((X-x0)/res).astype(int); iy=np.round((Y-y0)/res).astype(int)
    valid=(ix>=0)&(ix<W)&(iy>=0)&(iy<H)
    d=edt[iy[valid],ix[valid]]
    # trimmed mean (90%) + median as robust score (use median for search stability + mean90 check)
    return np.median(d), np.mean(np.sort(d)[:int(0.9*len(d))])
print("chamfer at (0,0): median/mean90 =", chamfer(0,0,MINpts))
best=None
for dx in np.arange(0.0,0.351,0.01):
    for dy in np.arange(-0.10,0.151,0.01):
        med,m90 = chamfer(dx,dy,MINpts)
        score=m90
        if best is None or score<best[0]: best=(score,dx,dy,med,m90)
print(f"coarse best mean90={best[0]:.5f} at dx={best[1]:.3f} dy={best[2]:.3f} (median={best[3]:.5f})")
bx,by=best[1],best[2]
for dx in np.arange(bx-0.012,bx+0.013,0.002):
    for dy in np.arange(by-0.012,by+0.013,0.002):
        med,m90=chamfer(dx,dy,MINpts)
        if m90<best[0]: best=(m90,dx,dy,med,m90)
print(f"FINE best: dx={best[1]:+.4f} dy={best[2]:+.4f} median_dist={best[3]:.5f}deg (~{best[3]*111:.2f}km) mean90={best[4]:.5f}")
for dx,dy in [(0,0),(0.17,0.0),(0.23,0.065),(best[1],best[2])]:
    print(f" check shift ({dx:+.3f},{dy:+.3f}): median/mean90={chamfer(dx,dy,MINpts)}")
# Geology validation chamfer (boundary points vs NE EDT), search small window
geo = gpd.read_file("work/Nigeria_Boundary_final.geojson").geometry.iloc[0]
gb = geo.boundary
gparts=[gb] if gb.geom_type=="LineString" else list(gb.geoms)
GEOpts=np.vstack([densify(p) for p in gparts if p.length>1.0])
print(f"\nGeology border pts={len(GEOpts)} chamfer(0,0)={chamfer(0,0,GEOpts)}")
gbest=None
for dx in np.arange(-0.05,0.051,0.005):
    for dy in np.arange(-0.05,0.051,0.005):
        med,m90=chamfer(dx,dy,GEOpts)
        if gbest is None or m90<gbest[0]: gbest=(m90,dx,dy,med)
print(f"Geology best shift dx={gbest[1]:+.4f} dy={gbest[2]:+.4f} mean90={gbest[0]:.5f} median={gbest[3]:.5f} (vs 0,0 mean90={chamfer(0,0,GEOpts)[1]:.5f})")

# Reliable towns (label-dot<=15pt from 03f list; reload matched json needs dist - recompute quickly from saved? 03f saved matched with dist as last elem)
mj=json.load(open("work/shift_mineral_named.json"))
matched=mj["matched"]
rel=[m for m in matched if m[6]<=16 and m[0] not in ("Owo","Bida")]
print(f"\nReliable named towns (label-dot<=16pt): n={len(rel)}")
S=np.array([(m[2]-m[4],m[3]-m[5]) for m in rel])
print(f" median shift=({np.median(S[:,0]):+.4f},{np.median(S[:,1]):+.4f}) mean=({S[:,0].mean():+.4f},{S[:,1].mean():+.4f})")
P=np.array([(m[4],m[5],m[2],m[3]) for m in rel])
# translation + isotropic scale about centroid (similarity, no rotation first), then full affine for comparison
X=np.column_stack([P[:,0],P[:,1],np.ones(len(P))])
cx,*_=np.linalg.lstsq(X,P[:,2],rcond=None); cy,*_=np.linalg.lstsq(X,P[:,3],rcond=None)
res=np.hypot(P[:,2]-(cx@X.T), P[:,3]-(cy@X.T))
print(f"town affine: lon'={cx[0]:.6f}lon {cx[1]:+.6f}lat {cx[2]:+.4f} | lat'={cy[0]:+.6f}lon {cy[1]:.6f}lat {cy[2]:+.4f} | resid med={np.median(res):.4f} mean={res.mean():.4f} max={res.max():.4f}")
tr = np.median(S,axis=0)
res_t=np.hypot(P[:,2]-(P[:,0]+tr[0]), P[:,3]-(P[:,1]+tr[1]))
print(f"town translation-only {tr}: resid med={np.median(res_t):.4f} mean={res_t.mean():.4f} max={res_t.max():.4f}")
for m,r in sorted(zip(rel,res_t), key=lambda z:-z[1])[:8]:
    print(f"  largest transl resid: {m[0]} {r:.3f}deg shift=({m[2]-m[4]:+.3f},{m[3]-m[5]:+.3f})")
json.dump(dict(chamfer_dx=float(best[1]), chamfer_dy=float(best[2]), chamfer_median_deg=float(best[3]),
               geology_best_dx=float(gbest[1]), geology_best_dy=float(gbest[2]),
               town_median=[float(tr[0]),float(tr[1])], town_affine_lon=cx.tolist(), town_affine_lat=cy.tolist(),
               town_n=len(rel)), open("work/correction_estimates.json","w"), indent=1)
print("DONE 03g")
