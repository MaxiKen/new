"""Quantify absolute (WGS84) shifts of Mineral + Geology bases vs Natural Earth control."""
import sys, json; sys.path.insert(0,"scripts")
import numpy as np, fitz
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from common import mineral_pdf_to_lonlat
import json as js

ne = gpd.read_file("work/NE_Nigeria.geojson").geometry.iloc[0]
ne_bnd = ne.boundary
places = gpd.read_file("work/NE_Nigeria_places.geojson")

# ---- Mineral town dots ----
doc = fitz.open("Mineral_Resources_Map_of_Nigeria_2023 (2).pdf"); page=doc[0]
dots=[]
for d in page.get_drawings():
    if d.get("fill")==(0.0,0.0,0.0):
        r=d["rect"]
        if 1<r.x1-r.x0<8 and 1<r.y1-r.y0<8 and 74<r.x0<2052 and 359<r.y0<1969:
            dots.append(((r.x0+r.x1)/2,(r.y0+r.y1)/2))
dots=np.array(dots)
dlon,dlat = mineral_pdf_to_lonlat(dots[:,0], dots[:,1])
D=np.column_stack([dlon,dlat])
print(f"mineral dots: {len(D)}")
# match NE places POP>=200k: predicted map pos = true + (-0.26,-0.02); nearest dot within 0.20deg
sub = places[places["POP_MAX"]>=200000].copy()
print(f"NE places >=200k: {len(sub)}")
pairs=[]
for _,r in sub.iterrows():
    tlon,tlat = float(r["LONGITUDE"]), float(r["LATITUDE"])
    pred = np.array([tlon-0.26, tlat-0.02])
    dist = np.hypot(D[:,0]-pred[0], D[:,1]-pred[1])
    j=np.argmin(dist)
    pairs.append((r["NAME"], tlon,tlat, D[j,0],D[j,1], dist[j]))
    print(f" {r['NAME']:16s} true({tlon:.3f},{tlat:.3f}) mapdot({D[j,0]:.3f},{D[j,1]:.3f}) shift true-map=({tlon-D[j,0]:+.3f},{tlat-D[j,1]:+.3f}) dist_pred={dist[j]:.3f}")
P=np.array([(p[3],p[4],p[1],p[2]) for p in pairs])  # maplon,maplat,tlon,tlat
sh = P[:,2:]-P[:,:2]
print(f"\nMineral town shift (true-map): median dLon={np.median(sh[:,0]):+.4f} dLat={np.median(sh[:,1]):+.4f} | MAD lon={np.median(np.abs(sh[:,0]-np.median(sh[:,0]))):.4f} lat={np.median(np.abs(sh[:,1]-np.median(sh[:,1]))):.4f} n={len(P)}")
# affine fit with iterative trim (keep resid<0.08)
def fit_affine(P):
    X=np.column_stack([P[:,0],P[:,1],np.ones(len(P))])
    cx,*_=np.linalg.lstsq(X,P[:,2],rcond=None); cy,*_=np.linalg.lstsq(X,P[:,3],rcond=None)
    return cx,cy
mask=np.ones(len(P),bool)
for _ in range(5):
    cx,cy=fit_affine(P[mask])
    pred_lon = cx[0]*P[:,0]+cx[1]*P[:,1]+cx[2]; pred_lat = cy[0]*P[:,0]+cy[1]*P[:,1]+cy[2]
    res=np.hypot(P[:,2]-pred_lon, P[:,3]-pred_lat)
    new = res<0.08
    if (new==mask).all(): break
    mask=new
print(f"Mineral affine (inliers {mask.sum()}/{len(P)}): lon'={cx[0]:.6f}*lon {cx[1]:+.6f}*lat {cx[2]:+.5f} | lat'={cy[0]:+.6f}*lon {cy[1]:.6f}*lat {cy[2]:+.5f}")
print(f" inlier resid median={np.median(res[mask]):.4f}deg (~{np.median(res[mask])*111:.1f}km) max={res[mask].max():.4f}")
print(" outliers:", [(pairs[i][0], round(float(res[i]),3)) for i in range(len(P)) if not mask[i]])
# translation-only on inliers
tsh = (P[mask,2:]-P[mask,:2])
print(f" translation-only (inliers) median=({np.median(tsh[:,0]):+.4f},{np.median(tsh[:,1]):+.4f}) mean=({tsh[:,0].mean():+.4f},{tsh[:,1].mean():+.4f})")
# scale check: fit separate 1D linear lon, lat
for ax,name in [(0,'lon'),(1,'lat')]:
    A=np.vstack([P[mask,ax],np.ones(mask.sum())]).T
    c,*_=np.linalg.lstsq(A,P[mask,ax+2],rcond=None)
    print(f" 1D {name}: true={c[0]:.6f}*map {c[1]:+.5f}")

# ---- Border vector shifts (segment-wise) ----
def segment_shifts(line_geom, ref_bnd, label):
    print(f"\n--- {label} vs NE boundary (nearest-point vectors, sampled) ---")
    L=line_geom.length; n=1200
    vecs=[]
    for d in np.linspace(0,L,n):
        p=line_geom.interpolate(d)
        _, q = nearest_points(p, ref_bnd)
        vecs.append((p.x,p.y,q.x-p.x,q.y-p.y))
    V=np.array(vecs)
    def rep(sel, name):
        if sel.sum()<10: print(name,"n=",sel.sum()); return
        print(f" {name:22s} n={sel.sum():4d} median d=({np.median(V[sel,2]):+.4f},{np.median(V[sel,3]):+.4f}) mean=({V[sel,2].mean():+.4f},{V[sel,3].mean():+.4f}) |d|med={np.median(np.hypot(V[sel,2],V[sel,3])):.4f}")
    rep(np.ones(len(V),bool),"ALL")
    rep((V[:,1]>12.2),"NORTH lat>12.2 (dy)")
    rep((V[:,0]<5.0)&(V[:,1]>8),"WEST lon<5,lat>8 (dx)")
    rep((V[:,0]<5.0)&(V[:,1]<=8),"SW lon<5,lat<=8")
    rep(V[:,0]>12.5,"EAST lon>12.5 (dx)")
    rep((V[:,1]<6.0),"SOUTH/coast lat<6 (dy)")
    return V
lb = gpd.read_file("work/Nigeria_LandBorder.geojson").geometry.iloc[0]
Vmin = segment_shifts(lb, ne_bnd, "MINERAL land border (map coords)")
geo_b = gpd.read_file("work/Nigeria_Boundary_final.geojson").geometry.iloc[0]
Vgeo = segment_shifts(geo_b.boundary, ne_bnd, "GEOLOGY v2 boundary (map coords)")
print("\nGeology v2 boundary bounds:", geo_b.bounds, " NE bounds:", ne.bounds)
# westmost points
coords = np.array(geo_b.boundary.coords) if geo_b.boundary.geom_type=="LineString" else np.vstack([np.array(g.coords) for g in geo_b.boundary.geoms])
i=np.argmin(coords[:,0]); print(f"Geology v2 westmost vertex: Lon {coords[i,0]:.4f} Lat {coords[i,1]:.4f}")
i=np.argmax(coords[:,1]); print(f"Geology v2 northmost vertex: Lon {coords[i,0]:.4f} Lat {coords[i,1]:.4f}")
# area of NE not in geology and vice versa
print(f"NE area deg2={ne.area:.3f} geo area={geo_b.area:.3f} NE-minus-geo={ne.difference(geo_b).area:.3f} geo-minus-NE={geo_b.difference(ne).area:.3f}")
json.dump(dict(mineral_towns=[dict(name=p[0],tlon=p[1],tlat=p[2],mlon=p[3],mlat=p[4]) for p in pairs],
               mineral_affine_lon=cx.tolist(), mineral_affine_lat=cy.tolist(), mineral_inliers=mask.tolist()),
          open("work/shift_mineral_towns.json","w"), indent=1)
print("DONE 03e")
