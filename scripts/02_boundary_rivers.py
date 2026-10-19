"""Extract Nigeria boundary (red) + rivers (light blue) vector paths from Mineral PDF."""
import sys; sys.path.insert(0,"scripts")
import numpy as np, fitz, collections
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, Polygon, mapping
from shapely.ops import linemerge, polygonize, unary_union
from shapely.validation import make_valid
from common import mineral_pdf_to_lonlat_corr as mineral_pdf_to_lonlat

doc = fitz.open("Mineral_Resources_Map_of_Nigeria_2023 (2).pdf")
page = doc[0]
drawings = page.get_drawings()

def cubic(p0,p1,p2,p3,n=8):
    t = np.linspace(0,1,n)[:,None]
    P = np.array([(p.x,p.y) for p in (p0,p1,p2,p3)])
    mt = 1-t
    pts = mt**3*P[0] + 3*mt**2*t*P[1] + 3*mt*t**2*P[2] + t**3*P[3]
    return [tuple(r) for r in pts[1:]]

def paths_from_drawing(d):
    """Yield polylines (list of (x,y) pdf pt) from a PyMuPDF drawing."""
    out=[]; cur=[]; curpt=None
    for item in d["items"]:
        op = item[0]
        if op == "l":
            p1,p2 = item[1], item[2]
            if not cur: cur=[(p1.x,p1.y)]
            # break if discontinuity
            if curpt is not None and (abs(curpt[0]-p1.x)>0.6 or abs(curpt[1]-p1.y)>0.6):
                if len(cur)>1: out.append(cur)
                cur=[(p1.x,p1.y)]
            cur.append((p2.x,p2.y)); curpt=(p2.x,p2.y)
        elif op == "c":
            p1,p2,p3,p4 = item[1],item[2],item[3],item[4]
            if not cur: cur=[(p1.x,p1.y)]
            if curpt is not None and (abs(curpt[0]-p1.x)>0.6 or abs(curpt[1]-p1.y)>0.6):
                if len(cur)>1: out.append(cur)
                cur=[(p1.x,p1.y)]
            cur.extend(cubic(p1,p2,p3,p4)); curpt=(p4.x,p4.y)
        elif op == "re":
            r = item[1]
            out.append([(r.x0,r.y0),(r.x1,r.y0),(r.x1,r.y1),(r.x0,r.y1),(r.x0,r.y0)])
        elif op == "qu":
            q = item[1]
            out.append([(q.ul.x,q.ul.y),(q.ur.x,q.ur.y),(q.lr.x,q.lr.y),(q.ll.x,q.ll.y),(q.ul.x,q.ul.y)])
    if len(cur)>1: out.append(cur)
    return out

def to_lonlat_line(pts):
    lon, lat = mineral_pdf_to_lonlat(np.array([p[0] for p in pts]), np.array([p[1] for p in pts]))
    coords = list(zip(lon.tolist(), lat.tolist()))
    # drop consecutive duplicates
    cc=[coords[0]]
    for c in coords[1:]:
        if abs(c[0]-cc[-1][0])>1e-9 or abs(c[1]-cc[-1][1])>1e-9: cc.append(c)
    return cc

# --- classify drawings ---
RED=(0.901960015296936,0.0,0.0); BLUE=(0.450980007648468,0.8745099902153015,1.0)
def is_color(c, ref, tol=0.02):
    return c is not None and all(abs(a-b)<tol for a,b in zip(c,ref))
red_ds = [d for d in drawings if is_color(d.get("color"), RED)]
blue_ds = [d for d in drawings if is_color(d.get("color"), BLUE)]
print(f"red boundary drawings={len(red_ds)} widths={collections.Counter(round(d.get('width') or 0,2) for d in red_ds)}")
print(f"blue river drawings={len(blue_ds)} widths={collections.Counter(round(d.get('width') or 0,2) for d in blue_ds)}")

# --- BOUNDARY (land border line; coast closure after geology registration) ---
lines=[]
for d in red_ds:
    for pts in paths_from_drawing(d):
        cc = to_lonlat_line(pts)
        if len(cc)>10:  # drop 2-pt legend sample
            lines.append(LineString(cc))
print(f"boundary segments kept: {len(lines)} total vertices {sum(len(l.coords) for l in lines)}")
merged = linemerge(MultiLineString(lines))
parts = list(merged.geoms) if merged.geom_type=="MultiLineString" else [merged]
parts.sort(key=lambda g:-g.length)
main_line = parts[0]
print(f"land border merged parts={len(parts)} main vertices={len(main_line.coords)} endpoints W={main_line.coords[0]} E={main_line.coords[-1]}")
lg = gpd.GeoDataFrame([dict(NAME="Nigeria land border (excl coast)", SOURCE="NGSA Mineral Resources Map 2023 PDF red vector")], geometry=[main_line], crs="EPSG:4326")
lg.to_file("work/Nigeria_LandBorder.geojson", driver="GeoJSON")
print("wrote work/Nigeria_LandBorder.geojson (polygon closure in step 04)")

# --- RIVERS ---
rlines=[]; npts=0
for d in blue_ds:
    for pts in paths_from_drawing(d):
        cc = to_lonlat_line(pts); npts+=len(cc)
        if len(cc)>1:
            ls = LineString(cc)
            if ls.length>0: rlines.append(ls)
print(f"river raw polylines: {len(rlines)} vertices={npts}")
merged_r = linemerge(MultiLineString(rlines))
geoms = list(merged_r.geoms) if merged_r.geom_type=="MultiLineString" else [merged_r]
print(f"river merged features: {len(geoms)}")
rg = gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326")
rg = rg[rg.geometry.length>1e-7].copy()
lens_km = rg.to_crs("EPSG:6933").length/1000.0
rg["LEN_KM"]=lens_km.round(3)
rg["RIV_ID"]=range(1,len(rg)+1)
rg["SOURCE"]="NGSA Mineral Resources Map of Nigeria 2023 (PDF vector hydrography)"
rg = rg.sort_values("LEN_KM", ascending=False).reset_index(drop=True)
rg["RIV_ID"]=range(1,len(rg)+1)
print(f"rivers kept: {len(rg)} total length {lens_km.sum():,.0f} km; longest {lens_km.max():.1f} km; median {lens_km.median():.2f} km")
print("length histogram km:", np.histogram(lens_km, bins=[0,1,2,5,10,25,50,100,500,5000])[0], "bins [0,1,2,5,10,25,50,100,500+]")
rg_small = (lens_km<5).sum()
print(f"small streams <5km: {rg_small} ({rg_small/len(rg)*100:.1f}%) - all retained")
rg.to_file("work/Rivers_raw.geojson", driver="GeoJSON")
import json
json.dump(dict(blue_drawings=len(blue_ds), red_drawings=len(red_ds),
               rivers_raw_polylines=int(len(rlines)), rivers_merged=int(len(rg)),
               rivers_total_km_unclipped=float(rg["LEN_KM"].sum())),
          open("work/rivers_extract_stats.json","w"), indent=1)
print("DONE 02 (rivers unclipped in work/Rivers_raw.geojson; final clip after boundary)")
