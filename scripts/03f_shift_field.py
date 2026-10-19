"""Shift FIELD by border extremal bands (mineral & geology vs NE) + name-matched mineral towns + diff inventory."""
import sys, re, unicodedata; sys.path.insert(0,"scripts")
import numpy as np, fitz, geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
from common import mineral_pdf_to_lonlat

ne = gpd.read_file("work/NE_Nigeria.geojson").geometry.iloc[0]
def all_coords(geom):
    if geom.geom_type=="Polygon": return np.array(geom.exterior.coords)
    if geom.geom_type=="MultiPolygon": return np.vstack([np.array(g.exterior.coords) for g in geom.geoms])
    if geom.geom_type in ("LineString","LinearRing"): return np.array(geom.coords)
    if geom.geom_type=="MultiLineString": return np.vstack([np.array(g.coords) for g in geom.geoms])
    raise ValueError(geom.geom_type)
NEc = all_coords(ne)
lb = gpd.read_file("work/Nigeria_LandBorder.geojson").geometry.iloc[0]
MINc = np.array(lb.coords)
geo = gpd.read_file("work/Nigeria_Boundary_final.geojson").geometry.iloc[0]
GEOc = all_coords(geo)

def band_compare(C, label):
    print(f"\n=== {label} extremal bands vs NE ===")
    print("WEST (min lon per 1deg lat band): band | NE | map | NE-map")
    for lo in range(4,14):
        a = NEc[(NEc[:,1]>=lo)&(NEc[:,1]<lo+1),0]; b = C[(C[:,1]>=lo)&(C[:,1]<lo+1),0]
        if len(a) and len(b): print(f" {lo}-{lo+1}N: {a.min():.3f} {b.min():.3f} {a.min()-b.min():+.3f}")
    print("EAST (max lon per 1deg lat band):")
    for lo in range(4,14):
        a = NEc[(NEc[:,1]>=lo)&(NEc[:,1]<lo+1),0]; b = C[(C[:,1]>=lo)&(C[:,1]<lo+1),0]
        if len(a) and len(b): print(f" {lo}-{lo+1}N: {a.max():.3f} {b.max():.3f} {a.max()-b.max():+.3f}")
    print("NORTH (max lat per 2deg lon band):")
    for lo in range(2,15,2):
        a = NEc[(NEc[:,0]>=lo)&(NEc[:,0]<lo+2),1]; b = C[(C[:,0]>=lo)&(C[:,0]<lo+2),1]
        if len(a) and len(b): print(f" {lo}-{lo+2}E: {a.max():.3f} {b.max():.3f} {a.max()-b.max():+.3f}")
    print("SOUTH coast (min lat per 2deg lon band):")
    for lo in range(2,15,2):
        a = NEc[(NEc[:,0]>=lo)&(NEc[:,0]<lo+2),1]; b = C[(C[:,0]>=lo)&(C[:,0]<lo+2),1]
        if len(a) and len(b): print(f" {lo}-{lo+2}E: {a.min():.3f} {b.min():.3f} {a.min()-b.min():+.3f}")
band_compare(MINc, "MINERAL land border (land only; south band meaningless)")
band_compare(GEOc, "GEOLOGY v2 boundary")

# diff inventory geology vs NE
print("\n=== Largest NE-minus-Geology pieces ===")
diff = ne.difference(geo)
pieces = [diff] if diff.geom_type=="Polygon" else list(diff.geoms) if diff.geom_type=="MultiPolygon" else []
pieces = sorted([p for p in pieces if p.geom_type=="Polygon"], key=lambda p:-p.area)
for p in pieces[:10]:
    c=p.centroid; print(f" area={p.area:.4f} deg2 (~{p.area*12300:.0f} km2) centroid=({c.x:.3f},{c.y:.3f}) bounds={tuple(round(v,2) for v in p.bounds)}")
print("=== Largest Geology-minus-NE pieces ===")
diff2 = geo.difference(ne)
pieces2 = [diff2] if diff2.geom_type=="Polygon" else list(diff2.geoms) if diff2.geom_type=="MultiPolygon" else []
pieces2 = sorted([p for p in pieces2 if p.geom_type=="Polygon"], key=lambda p:-p.area)
for p in pieces2[:10]:
    c=p.centroid; print(f" area={p.area:.4f} deg2 (~{p.area*12300:.0f} km2) centroid=({c.x:.3f},{c.y:.3f}) bounds={tuple(round(v,2) for v in p.bounds)}")

# ---- Name-matched mineral towns ----
print("\n=== Mineral name-matched towns ===")
doc=fitz.open("Mineral_Resources_Map_of_Nigeria_2023 (2).pdf"); page=doc[0]
dots=[]
for d in page.get_drawings():
    if d.get("fill")==(0.0,0.0,0.0):
        r=d["rect"]
        if 1<r.x1-r.x0<8 and 1<r.y1-r.y0<8 and 74<r.x0<2052 and 359<r.y0<1969:
            dots.append(((r.x0+r.x1)/2,(r.y0+r.y1)/2))
dots=np.array(dots)
dd=page.get_text("dict"); spans=[]
for b in dd["blocks"]:
    if b.get("type")==0:
        for l in b["lines"]:
            for s in l["spans"]: spans.append(s)
def norm(t):
    t=unicodedata.normalize("NFKD", t).encode("ascii","ignore").decode()
    return re.sub(r"[^a-z0-9]","", t.lower())
places=gpd.read_file("work/NE_Nigeria_places.geojson")
ne_names={}
for _,r in places.iterrows():
    for key in [r["NAME"], r.get("NAMEASCII")]:
        if isinstance(key,str) and key: ne_names.setdefault(norm(key), (float(r["LONGITUDE"]), float(r["LATITUDE"]), r["NAME"], int(r["POP_MAX"])))
# town name spans: alphabetic, size>=6.5, in frame, title/upper case, len>=3; exclude State/river/road words
exclude={"state","river","riv","plateau","guinea","bight","bonny","lake","chad","gulf"}
town_spans=[]
for s in spans:
    t=s["text"].strip()
    cx,cy=(s["bbox"][0]+s["bbox"][2])/2,(s["bbox"][1]+s["bbox"][3])/2
    if not (74<=cx<=2052 and 359<=cy<=1969): continue
    if len(t)<3 or not any(c.isalpha() for c in t): continue
    if norm(t) in exclude: continue
    town_spans.append((cx,cy,t,s["bbox"]))
matched=[]
used=set()
for (cx,cy,t,bb) in town_spans:
    k=norm(t)
    # try full normalized, also without spaces variants: 'Benin - City'->benincity matches NE 'Benin City'
    if k in ne_names and k not in used:
        # nearest dot within 45pt of label bbox (use label centre + also edges: min dist to bbox)
        d = np.hypot(dots[:,0]-cx, dots[:,1]-cy)
        j=np.argmin(d)
        if d[j]<=50:
            tlon,tlat,name,pop = ne_names[k]
            mlon,mlat = mineral_pdf_to_lonlat(dots[j,0],dots[j,1])
            matched.append((name,pop,tlon,tlat,float(mlon),float(mlat),float(d[j])))
            used.add(k)
matched.sort(key=lambda m:-m[1])
for m in matched:
    print(f" {m[0]:16s} pop{m[1]:8d} true({m[2]:.3f},{m[3]:.3f}) map({m[4]:.3f},{m[5]:.3f}) shift=({m[2]-m[4]:+.3f},{m[3]-m[5]:+.3f}) label-dot {m[6]:.0f}pt")
if matched:
    S=np.array([(m[2]-m[4], m[3]-m[5]) for m in matched])
    print(f"name-matched n={len(matched)} median shift=({np.median(S[:,0]):+.4f},{np.median(S[:,1]):+.4f}) MAD=({np.median(np.abs(S[:,0]-np.median(S[:,0]))):.4f},{np.median(np.abs(S[:,1]-np.median(S[:,1]))):.4f})")
    # affine fit trimmed
    P=np.array([(m[4],m[5],m[2],m[3]) for m in matched])
    mask=np.ones(len(P),bool)
    for _ in range(6):
        X=np.column_stack([P[mask,0],P[mask,1],np.ones(mask.sum())])
        cx,*_=np.linalg.lstsq(X,P[mask,2],rcond=None); cy,*_=np.linalg.lstsq(X,P[mask,3],rcond=None)
        res=np.hypot(P[:,2]-(cx[0]*P[:,0]+cx[1]*P[:,1]+cx[2]), P[:,3]-(cy[0]*P[:,0]+cy[1]*P[:,1]+cy[2]))
        new=res<0.06
        if (new==mask).all(): break
        mask=new
    print(f"affine inliers {mask.sum()}/{len(P)} lon'={cx[0]:.6f}lon {cx[1]:+.6f}lat {cx[2]:+.4f} lat'={cy[0]:+.6f}lon {cy[1]:.6f}lat {cy[2]:+.4f} resid med={np.median(res[mask]):.4f} max={res[mask].max():.4f}")
    print("outliers:", [(matched[i][0], round(float(res[i]),3)) for i in range(len(P)) if not mask[i]])
    import json
    json.dump(dict(matched=matched, affine_lon=cx.tolist(), affine_lat=cy.tolist(), inliers=mask.tolist()), open("work/shift_mineral_named.json","w"), indent=1)
