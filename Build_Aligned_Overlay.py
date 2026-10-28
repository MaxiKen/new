#!/usr/bin/env python3
"""Combined geology + mineral map using the mineral sheet's embedded frame.

Geology: printed graticule (no embedded measure exists).
Minerals: embedded GeoPDF measure, i.e. 0.1718-0.1726 deg east of the printed
graticule. No empirical displacement is applied: the river-fit shift used in the
first draft is withdrawn, because the sheet's own vector international boundary
matches Natural Earth at 1.06 km in the embedded frame and 12.94 km in the
printed frame. Datum remains unverified, so EPSG:4326 is a display assumption.
"""
import json, zipfile
from pathlib import Path
import numpy as np
import pymupdf
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
CROP_G = pymupdf.Rect(80, 90, 2050, 1693)
CROP_M = pymupdf.Rect(80, 359, 2050, 1968)

def render(path, clip):
    p = pymupdf.open(path)[0].get_pixmap(matrix=pymupdf.Matrix(1, 1), clip=clip, alpha=False)
    return np.frombuffer(p.samples, np.uint8).reshape(p.height, p.width, 3).copy()

def geo_lonlat(x, y): return (x + 276.36) / 157.593, (2281.63 - y) / 157.586
def min_lonlat(x, y): return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
                              14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)
def bounds(clip, fn):
    l, t = fn(clip.x0, clip.y0); r, b = fn(clip.x1, clip.y1)
    return l, b, r, t

g = render(P / "Geological_Map_of_Nigeria.pdf", CROP_G)
m = render(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf", CROP_M)  # raster strips removed of vector overlays? no: full render
gb, mb = bounds(CROP_G, geo_lonlat), bounds(CROP_M, min_lonlat)
crs = "EPSG:4326"
gt = from_bounds(*gb, g.shape[1], g.shape[0]); mt = from_bounds(*mb, m.shape[1], m.shape[0])

warped = np.zeros_like(g); cov = np.zeros(g.shape[:2], np.uint8)
for b in range(3):
    reproject(m[:, :, b], warped[:, :, b], src_transform=mt, src_crs=crs,
              dst_transform=gt, dst_crs=crs, resampling=Resampling.nearest)
reproject(np.ones(m.shape[:2], np.uint8), cov, src_transform=mt, src_crs=crs,
          dst_transform=gt, dst_crs=crs, resampling=Resampling.nearest)

blend = g.copy(); v = cov != 0
blend[v] = (g[v].astype(np.float32) * .62 + warped[v].astype(np.float32) * .38).astype(np.uint8)

def tif(path, arr, transform, desc):
    prof = dict(driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=3, dtype="uint8",
                crs=crs, transform=transform, compress="deflate", predictor=2, tiled=True)
    with rasterio.open(path, "w", **prof) as d:
        d.write(np.moveaxis(arr, 2, 0))
        d.update_tags(DESCRIPTION=desc, STATUS="EPSG:4326 is a display assumption; source datum unverified; not survey-accurate",
                      MINERAL_REGISTRATION="embedded GeoPDF measure (vector boundary control: 1.06 km vs Natural Earth)",
                      GEOLOGY_REGISTRATION="printed graticule (coastline control: 1.9 km vs Natural Earth)")

tif(P / "Combined_Geology_Minerals_ALIGNED.tif", blend, gt, "62% geology + 38% minerals; legend colours and symbols cannot be decoded from this composite")
tif(P / "Geology_ALIGNED.tif", g, gt, "2011 sheet, printed graticule")

im = Image.fromarray(blend)
hdr = Image.new("RGB", (im.width, 72), "white"); d = ImageDraw.Draw(hdr)
try:
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
    fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
except OSError:
    fb = fs = ImageFont.load_default()
d.text((12, 5), "COMBINED GEOLOGY + MINERALS - mineral layer on the sheet's embedded frame", fill="#123d6b", font=fb)
d.text((12, 36), "Legend colours and mineral symbols are not readable in a blend: use the original PDFs. Datum unverified; display only.", fill="#202020", font=fs)
canvas = Image.new("RGB", (im.width, im.height + 72), "white"); canvas.paste(hdr, (0, 0)); canvas.paste(im, (0, 72))
canvas.save(P / "Combined_Geology_Minerals_ALIGNED.png", optimize=True)

readme = """COMBINED MAP LAYERS - READ THIS FIRST

What each file is
  Geology_ALIGNED.tif    2011 geological sheet, rendered at 72 dpi, placed by its printed graticule.
  Minerals_ALIGNED.tif   2023 mineral sheet, placed by its embedded GeoPDF /Measure.
  Minerals_Symbol_Points_CORRECTED.geojson / .csv  1,323 printed mineral symbols, coordinates
                         rewritten from the printed graticule into the embedded frame (+18.5 to
                         +19.1 km east). Fields lon_printed / lat_printed keep the old values,
                         lon_was / lat_was the previously published ones.
  Nigeria_Natural_Earth_outline.geojson, Niger_Benue_Natural_Earth.geojson   reference geometry.

Which coordinates to trust
  The mineral sheet printed two coordinate definitions that disagree by 0.172 deg of longitude
  (about 19 km). Its own vector international boundary settles which one the artwork was drawn
  in: 1.06 km median offset from the Natural Earth Nigeria border in the embedded frame versus
  12.94 km in the printed frame. The stored mineral point coordinates had been computed from the
  printed graticule, so they were 19 km too far west; that is what this correction fixes.
  An earlier river-based shift of +0.0753 deg east / +0.0578 deg north is withdrawn (see report).

What this is NOT
  Not a datum transformation and not survey-accurate. Both sheets carry no established datum;
  EPSG:4326 is assigned only so GIS software will display the rasters on a world basemap.
  Do not use for licensing, exploration decisions, navigation or legal boundaries, and do not
  read geology or commodity classes from the blended raster - use the original PDFs.
"""
with zipfile.ZipFile(P / "Combined_Map_Layers.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=5) as z:
    z.writestr("README.txt", readme)
    for f in ["Combined_Geology_Minerals_ALIGNED.tif",
              "Minerals_Symbol_Points_CORRECTED.geojson", "Minerals_Symbol_Points_CORRECTED.csv",
              "Nigeria_Natural_Earth_outline.geojson", "Niger_Benue_Natural_Earth.geojson"]:
        z.write(P / f, f)
(P / "Geology_ALIGNED.tif").unlink()
print("wrote overlay png, composite tif, layer zip")
