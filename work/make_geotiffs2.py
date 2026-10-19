import pymupdf, numpy as np, rasterio, json, hashlib
from rasterio.transform import Affine
from rasterio.enums import Resampling
from PIL import Image
import sys; sys.path.insert(0,'work')
from transforms import *
OUT="corrected_delivery/02_Georeferenced_map_pictures"
import os; os.makedirs(OUT, exist_ok=True)

def write_tif(path, arr, west, north, dlon, dlat, desc):
    tr=Affine(dlon,0,west,0,dlat,north)
    prof=dict(driver='GTiff',height=arr.shape[0],width=arr.shape[1],count=3,dtype='uint8',crs='EPSG:4326',
              transform=tr,compress='JPEG',jpeg_quality=88,tiled=True,blockxsize=256,blockysize=256,photometric='YCBCR')
    with rasterio.open(path,'w',**prof) as ds:
        for i in range(3): ds.write(arr[:,:,i],i+1)
        ds.update_tags(DESCRIPTION=desc, GEOREF_NOTE="EPSG:4326, north-up, no rotation. See georeferencing reports in QA_maps_and_reports.")
        ds.build_overviews([2,4,8,16],Resampling.average)
    with rasterio.open(path) as ds:
        b=[round(float(v),6) for v in ds.bounds]
        print(path, ds.width, ds.height, "bounds", b, "res", ds.res)
    print(" size MB", round(os.path.getsize(path)/1e6,1))
    return {"file":path,"width":arr.shape[1],"height":arr.shape[0],"bounds":b,"dlon_px":dlon,"dlat_px":dlat}

meta={}
# ===== GEOLOGY full sheet (native image) =====
geo=np.array(Image.open("work/geology_native_full.jpg").convert("RGB"))
H,W=geo.shape[:2]
# page pt per px
ptx=3168/W; pty=1764/H
dlon=GEO_DLDX*ptx; dlat=GEO_DLADY*pty
meta['geology_full']=write_tif(f"{OUT}/Geological_Map_of_Nigeria_FULLSHEET_georeferenced.tif", geo, GEO_LON0, GEO_LAT_TOP, dlon, dlat,
  "Geological Map of Nigeria (NGSA) full sheet, native 6600x3675 image from PDF, georeferenced by printed 1-degree graticule affine (verified). CRS EPSG:4326. Legend panels east of map frame project beyond Nigeria lon; use MAPFRAME version for overlay.")
# ===== GEOLOGY map frame interior: cols 188..4274, rows 188..3523 (inside innermost neatline at 187/4275/187/3524) =====
x0,y0,x1,y1=188,188,4275,3524  # PIL crop exclusive end => last included 4274/3523
frame=geo[y0:y1, x0:x1]
west=GEO_LON0+dlon*x0; north=GEO_LAT_TOP+dlat*y0
meta['geology_frame']=write_tif(f"{OUT}/Geological_Map_of_Nigeria_MAPFRAME_georeferenced.tif", frame, west, north, dlon, dlat,
  "Geological Map of Nigeria (NGSA) map-frame interior only (inside neatline), georeferenced EPSG:4326 by printed graticule affine. Use this for overlay comparison with geology shapefiles (same transform).")

# ===== MINERAL full sheet render at 150 dpi =====
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'); p=d[0]
zoom=150/72
pix=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom))
print("mineral full render", pix.width, pix.height)
full=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3].copy()
# page pt per px = 1/zoom
dlon_m=MIN_DLDX/zoom; dlat_m=MIN_DLADY/zoom
west_m=MIN_LON0; north_m=MIN_LAT0  # lat at ytop=0: MIN_LAT0 = lat at 0? MIN_LAT0 defined as MIN_LAT[0]-DLADY*FRAME_y0 => lat at ytop=0 yes
meta['mineral_full']=write_tif(f"{OUT}/Mineral_Resources_Map_of_Nigeria_2023_FULLSHEET_georeferenced.tif", full, west_m, north_m, dlon_m, dlat_m,
  "Mineral Resources Map of Nigeria 2023 (NGSA) full sheet rendered 150dpi, georeferenced EPSG:4326 by publisher extent (/VP) transform (=graticule +0.172deg lon). WARNING: printed longitude graticule on this sheet is displaced ~19km; do not georeference by it. Legend/table panels east of frame project beyond Nigeria; use MAPFRAME version for overlay.")
# ===== MINERAL map frame render at 150dpi, clip=neatline interior =====
# Render clip exactly frame; get_pixmap with clip: pixel (0,0) corresponds clip top-left. Width = ceil(frame_w*zoom) etc. To keep transform exact, compute from clip origin.
clip=pymupdf.Rect(MIN_FRAME[0],MIN_FRAME[1],MIN_FRAME[2],MIN_FRAME[3])
pix2=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom), clip=clip)
print("mineral frame render", pix2.width, pix2.height, "expected", (MIN_FRAME[2]-MIN_FRAME[0])*zoom, (MIN_FRAME[3]-MIN_FRAME[1])*zoom)
fr=np.frombuffer(pix2.samples,dtype=np.uint8).reshape(pix2.height,pix2.width,pix2.n)[:,:,:3].copy()
# Exact: use nominal dlon/dlat; west/north at frame edges (subpixel <1px alignment uncertainty from renderer rounding; adjust by using pix dims vs nominal span ratio? Renderer maps clip edge to image edge, so span = frame lon/lat span over pix dims.)
dlon_f=(MIN_LON[1]-MIN_LON[0])/pix2.width; dlat_f=(MIN_LAT[1]-MIN_LAT[0])/pix2.height
meta['mineral_frame']=write_tif(f"{OUT}/Mineral_Resources_Map_of_Nigeria_2023_MAPFRAME_georeferenced.tif", fr, MIN_LON[0], MIN_LAT[0], dlon_f, dlat_f,
  "Mineral Resources Map of Nigeria 2023 (NGSA) map-frame (neatline) rendered 150dpi including vector overprints, EPSG:4326 publisher-extent transform. Use for overlay comparison with mineral points/rivers (same transform).")
# ===== MINERAL base raster only (symbols+geology tints, NO vector overprint) 2060x1677 =====
base=np.array(Image.open("work/mineral_base_2060x1677.png").convert("RGB"))
# extent edges in page pts: x 74.23969..2051.83130, ytop 358.72388..1968.66113
west_b,_=min_page_to_lonlat(74.23969,358.72388); east_b,south_b=min_page_to_lonlat(2051.83130,1968.66113); _,north_b=min_page_to_lonlat(74.23969,358.72388)
dlon_b=(east_b-west_b)/base.shape[1]; dlat_b=(south_b-north_b)/base.shape[0]
meta['mineral_base']=write_tif(f"{OUT}/Mineral_Resources_Map_BASEONLY_symbols_georeferenced.tif", base, west_b, north_b, dlon_b, dlat_b,
  "Mineral map embedded base raster ONLY (2060x1677: geology tints + mineral symbols, without vector roads/labels/boundaries overprint), EPSG:4326 publisher-extent transform. Best picture for checking mineral point centring: symbols are not obscured by labels.")
json.dump(meta, open(f"{OUT}/geotiff_index.json","w"), indent=2)
print(json.dumps(meta,indent=2))
