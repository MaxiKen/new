"""Georeference Geology JPG + Mineral PDF. Writes GeoTIFFs (EPSG:4326), GCP tables, native stitch."""
import json, csv, sys
sys.path.insert(0, "scripts")
import numpy as np, cv2
import rasterio
from rasterio.transform import Affine
import fitz
from common import (MIN_LON_COEF, MIN_LAT_COEF, MIN_FRAME, mineral_pdf_to_lonlat)

OUT = "output/01_Georeferenced_Rasters"
TAB = "output/04_Tables"

# ---------- GEOLOGY: subpixel grid-line refinement ----------
print("=== GEOLOGY ===")
im = cv2.imread("pic NGSA geological-map-of-nigeria-.jpg")
H, W = im.shape[:2]
gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
dark = (gray[:, :4750] < 160)

def refine_peak(profile, approx, half=4):
    lo, hi = max(0, approx-half), min(len(profile), approx+half+1)
    w = profile[lo:hi].astype(float)
    w = np.clip(w - w.min(), 0, None)  # baseline remove
    if w.sum() == 0: return float(approx)
    idx = np.arange(lo, hi)
    return float((idx*w).sum()/w.sum())

colsum = dark.sum(axis=0); rowsum = dark.sum(axis=1)
GEO_LON_X0 = [408,737,1065,1394,1722,2050,2378,2707,3036,3364,3692,4020]
GEO_LAT_Y0 = [485,813,1141,1470,1798,2126,2454,2783,3111,3440]
lon_x = np.array([refine_peak(colsum, x) for x in GEO_LON_X0])
lat_y = np.array([refine_peak(rowsum, y) for y in GEO_LAT_Y0])
lon_v = np.arange(3., 15.); lat_v = np.arange(13., 3., -1.)
# skew check: refine verticals using top-half vs bottom-half rows only
top = dark[:1800,:].sum(axis=0); bot = dark[1800:,:].sum(axis=0)
lon_xt = np.array([refine_peak(top, x) for x in GEO_LON_X0])
lon_xb = np.array([refine_peak(bot, x) for x in GEO_LON_X0])
left = dark[:, :2200].sum(axis=1); right = dark[:, 2200:4750].sum(axis=1)
lat_yl = np.array([refine_peak(left, y) for y in GEO_LAT_Y0])
lat_yr = np.array([refine_peak(right, y) for y in GEO_LAT_Y0])
print("vertical skew top-bottom (px):", np.round(lon_xt-lon_xb,2), "max", np.abs(lon_xt-lon_xb).max())
print("horizontal skew left-right (px):", np.round(lat_yl-lat_yr,2), "max", np.abs(lat_yl-lat_yr).max())

def fit(x, v):
    A = np.vstack([x, np.ones_like(x)]).T
    c, *_ = np.linalg.lstsq(A, v, rcond=None)
    return c, v-(c[0]*x+c[1])
# fit in centre coords u = px+0.5
glon, glon_r = fit(lon_x+0.5, lon_v)
glat, glat_r = fit(lat_y+0.5, lat_v)
print(f"Geology lon: a={glon[0]:.10f} b={glon[1]:.8f} resid_px={np.round(glon_r/glon[0],2)} RMSpx={np.sqrt(np.mean((glon_r/glon[0])**2)):.3f}")
print(f"Geology lat: a={glat[0]:.10f} b={glat[1]:.8f} resid_px={np.round(glat_r/glat[0],2)} RMSpx={np.sqrt(np.mean((glat_r/glat[0])**2)):.3f}")
print("refined lon_x:", np.round(lon_x,2))
print("refined lat_y:", np.round(lat_y,2))

geo_info = dict(lon_x=lon_x.tolist(), lon_v=lon_v.tolist(), lat_y=lat_y.tolist(), lat_v=lat_v.tolist(),
                glon=glon.tolist(), glat=glat.tolist(),
                rms_lon_px=float(np.sqrt(np.mean((glon_r/glon[0])**2))),
                rms_lat_px=float(np.sqrt(np.mean((glat_r/glat[0])**2))),
                max_skew_v_px=float(np.abs(lon_xt-lon_xb).max()), max_skew_h_px=float(np.abs(lat_yl-lat_yr).max()),
                width=W, height=H)
json.dump(geo_info, open("work/georef_geology.json","w"), indent=1)
# GCP csv (line intersections: all combos = 120 points; provide full grid)
with open(f"{TAB}/GCP_Geology_Map.csv","w",newline="") as f:
    wcsv = csv.writer(f); wcsv.writerow(["pixel_col_centre","pixel_row_centre","lon_E","lat_N"])
    for yy, lv in zip(lat_y, lat_v):
        for xx, lov in zip(lon_x, lon_v):
            wcsv.writerow([f"{xx:.2f}", f"{yy:.2f}", lov, lv])
with open(f"{OUT}/Geology_Map_of_Nigeria_NGSA_full_sheet.points","w") as f:
    f.write("mapX,mapY,pixelX,pixelY,enable\n")
    for yy, lv in zip(lat_y, lat_v):
        for xx, lov in zip(lon_x, lon_v):
            f.write(f"{lov},{lv},{xx:.2f},{-yy:.2f},1\n")

def write_tif(path, arr_rgb, transform, description=None):
    h, w = arr_rgb.shape[:2]
    prof = dict(driver="GTiff", height=h, width=w, count=3, dtype="uint8",
                crs="EPSG:4326", transform=transform, compress="jpeg", jpeg_quality=88,
                tiled=True, blockxsize=256, blockysize=256, photometric="YCBCR")
    with rasterio.open(path, "w", **prof) as ds:
        for i in range(3):
            ds.write(arr_rgb[:,:,i], i+1)
        if description: ds.update_tags(DESCRIPTION=description)
        ds.build_overviews([2,4,8,16], rasterio.enums.Resampling.average)
        ds.update_tags(ns="rio_overview", resampling="average")
    print("wrote", path)

rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
transform_full = Affine(glon[0], 0, glon[1], 0, glat[0], glat[1])
print("Geology full extent:", rasterio.transform.array_bounds(H, W, transform_full))
write_tif(f"{OUT}/Geology_Map_of_Nigeria_NGSA_full_sheet.tif", rgb, transform_full,
          "NGSA Geological Map of Nigeria (2011) full sheet georeferenced to 1-degree graticule, EPSG:4326. Legend area carries extrapolated coordinates; use map_only for analysis.")
# Map-only crop inner frame (187,188)-(4313,3525) inclusive -> slice rows 188:3526, cols 187:4314
x0,y0,x1,y1 = 187,188,4313,3525
crop = rgb[y0:y1+1, x0:x1+1]
from rasterio.transform import Affine as Af
t_crop = Af.translation(x0, y0) * transform_full
# NOTE: rasterio Affine translation composition: new = transform * translation? Verify: pixel (0,0) of crop = (x0,y0) of full -> lon = a*x0+c. Affine.translation(x0,y0)*transform maps (0,0)-> transform*(x0,y0)? Affine multiplication applies right first... Use explicit:
t_crop = Affine(glon[0], 0, glon[0]*x0+glon[1], 0, glat[0], glat[0]*y0+glat[1])
print("Geology map-only extent:", rasterio.transform.array_bounds(crop.shape[0], crop.shape[1], t_crop), crop.shape)
write_tif(f"{OUT}/Geology_Map_of_Nigeria_NGSA_map_only.tif", crop, t_crop,
          "NGSA Geological Map of Nigeria map frame only, EPSG:4326.")
geo_info["map_frame_px"] = [x0,y0,x1,y1]
json.dump(geo_info, open("work/georef_geology.json","w"), indent=1)

# ---------- MINERAL ----------
print("\n=== MINERAL ===")
a_lon, b_lon = MIN_LON_COEF; a_lat, b_lat = MIN_LAT_COEF
print(f"Mineral lon a={a_lon:.10f} b={b_lon:.8f} | lat a={a_lat:.10f} b={b_lat:.8f} (exact graticule, spacing 315.2pt/2deg)")
with open(f"{TAB}/GCP_Mineral_Map.csv","w",newline="") as f:
    wcsv = csv.writer(f); wcsv.writerow(["pdf_x_pt","pdf_y_pt","lon_E","lat_N"])
    for ly, lv in zip([523.5,838.7,1153.9,1469.1,1784.3],[13,11,9,7,5]):
        for lx, lov in zip([341.4,656.6,971.8,1287.0,1602.2,1917.4],[4,6,8,10,12,14]):
            wcsv.writerow([lx, ly, lov, lv])
doc = fitz.open("Mineral_Resources_Map_of_Nigeria_2023 (2).pdf")
page = doc[0]
# full sheet scale 1.5
S=1.5
pix = page.get_pixmap(matrix=fitz.Matrix(S,S))
arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:,:,:3]
t_full = Affine(a_lon/S, 0, b_lon, 0, a_lat/S, b_lat)
print("Mineral full render", arr.shape, "extent", rasterio.transform.array_bounds(arr.shape[0], arr.shape[1], t_full))
write_tif(f"{OUT}/Mineral_Resources_Map_of_Nigeria_2023_full_sheet.tif", arr, t_full,
          "Mineral Resources Map of Nigeria 2023 full sheet, EPSG:4326. Explanation columns carry extrapolated coordinates; use map_only for analysis.")
del arr, pix
# map-only scale 3
S=3.0
fx0,fy0,fx1,fy1 = MIN_FRAME
pix = page.get_pixmap(matrix=fitz.Matrix(S,S), clip=fitz.Rect(fx0,fy0,fx1,fy1))
arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:,:,:3]
t_map = Affine(a_lon/S, 0, a_lon*fx0+b_lon, 0, a_lat/S, a_lat*fy0+b_lat)
print("Mineral map-only render", arr.shape, "extent", rasterio.transform.array_bounds(arr.shape[0], arr.shape[1], t_map))
write_tif(f"{OUT}/Mineral_Resources_Map_of_Nigeria_2023_map_only.tif", arr, t_map,
          "Mineral Resources Map of Nigeria 2023 map frame only, EPSG:4326.")
del arr, pix
# native stitch
print("Stitching native raster strips...")
infos = [i for i in page.get_image_info(xrefs=True) if i["width"]==2060]
infos.sort(key=lambda i: i["bbox"][1])
pxpt = 2060.0/(fx1-fx0)
canvasW = 2060; canvasH = int(round((fy1-fy0)*pxpt))
print("canvas", canvasW, canvasH, "pxpt", pxpt)
canvas = np.full((canvasH, canvasW, 3), 255, dtype=np.uint8)
for inf in infos:
    p = fitz.Pixmap(doc, inf["xref"])
    a = np.frombuffer(p.samples, dtype=np.uint8).reshape(p.h, p.w, p.n)[:,:,:3]
    yoff = int(round((inf["bbox"][1]-fy0)*pxpt))
    print(f" xref {inf['xref']} y0={inf['bbox'][1]:.2f} -> yoff {yoff} h={p.h}")
    canvas[yoff:yoff+p.h, :, :] = a
cv2.imwrite("work/mineral_native_map.png", cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))
t_nat = Affine(a_lon/pxpt, 0, a_lon*fx0+b_lon, 0, a_lat/pxpt, a_lat*fy0+b_lat)
print("native extent", rasterio.transform.array_bounds(canvasH, canvasW, t_nat))
write_tif(f"{OUT}/Mineral_Resources_Map_of_Nigeria_2023_native_symbols_layer.tif", canvas, t_nat,
          "Native 96dpi raster layer extracted from PDF (geology background + mineral symbols, no text/roads). EPSG:4326.")
min_info = dict(a_lon=float(a_lon), b_lon=float(b_lon), a_lat=float(a_lat), b_lat=float(b_lat), frame=list(MIN_FRAME), native_pxpt=float(pxpt), native_w=canvasW, native_h=canvasH)
json.dump(min_info, open("work/georef_mineral.json","w"), indent=1)
print("DONE 01")
