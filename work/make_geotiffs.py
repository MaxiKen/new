import pymupdf, numpy as np, rasterio
from rasterio.transform import Affine
from rasterio.enums import Resampling
from PIL import Image
import sys; sys.path.insert(0,'work')
from transforms import *

def write_tif(path, arr, lon_west_edge, lat_north_edge, dlon_px, dlat_px, description):
    """arr: (H,W,3) uint8. dlat_px negative."""
    tr = Affine(dlon_px, 0, lon_west_edge, 0, dlat_px, lat_north_edge)
    profile = dict(driver='GTiff', height=arr.shape[0], width=arr.shape[1], count=3, dtype='uint8',
                   crs='EPSG:4326', transform=tr, compress='JPEG', jpeg_quality=88, tiled=True,
                   blockxsize=256, blockysize=256, photometric='YCBCR', predictor=1)
    with rasterio.open(path,'w',**profile) as ds:
        for i in range(3): ds.write(arr[:,:,i], i+1)
        ds.update_tags(DESCRIPTION=description)
        ds.build_overviews([2,4,8,16], Resampling.average)
        ds.update_tags(ns='rio_overview', resampling='average')
    with rasterio.open(path) as ds:
        print(path, ds.width, ds.height, "bounds", [round(v,5) for v in ds.bounds], "res deg/px", ds.res)
    return tr

# ---------- GEOLOGY: native embedded image 6600x3675 over full page 3168x1764 pt ----------
d2=pymupdf.open('Geological_Map_of_Nigeria.pdf')
pix=pymupdf.Pixmap(d2,4)
print("geology pix", pix.width, pix.height, pix.n, pix.alpha)
geo_img=Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
geo_img.save("work/geology_native_full.jpg", quality=92)
print("saved geology_native_full.jpg")
# Detect neatline: grayscale dark pixel projections. Use downscaled for speed then refine.
g=np.array(geo_img.convert("L"))
dark=(g<80)
# Sum over central band rows to find vertical frame lines (long verticals)
colsum=dark.sum(axis=0); rowsum=dark.sum(axis=1)
H,W=g.shape
# print top candidate columns with >2500 dark px
cand=np.where(colsum>2400)[0]
print("vertical line candidate cols (runs):")
runs=[]
if len(cand):
    s=cand[0]; prev=cand[0]
    for c in cand[1:]:
        if c>prev+1: runs.append((s,prev)); s=c
        prev=c
    runs.append((s,prev))
for a,b in runs: print(f" col {a}-{b} centre {(a+b)/2:.1f} maxsum {colsum[a:b+1].max()}")
cand2=np.where(rowsum>3500)[0]
runs2=[]
if len(cand2):
    s=cand2[0]; prev=cand2[0]
    for c in cand2[1:]:
        if c>prev+1: runs2.append((s,prev)); s=c
        prev=c
    runs2.append((s,prev))
print("horizontal line candidate rows:")
for a,b in runs2: print(f" row {a}-{b} centre {(a+b)/2:.1f} maxsum {rowsum[a:b+1].max()}")
np.save("work/geo_colsum.npy", colsum); np.save("work/geo_rowsum.npy", rowsum)
