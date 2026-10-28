#!/usr/bin/env python3
"""Build a visual-only GIS overlay; datum and accuracy are unverified.
Requires pymupdf numpy rasterio pillow. Not suitable for survey, exploration or navigation.
"""
from pathlib import Path
import json,zipfile
import numpy as np
import pymupdf
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
geo=pymupdf.open(P/'Geological_Map_of_Nigeria.pdf')[0]
mineral=pymupdf.open(P/'Mineral_Resources_Map_of_Nigeria_2023.pdf')[0]
gbox=pymupdf.Rect(80,90,2050,1693);mbox=pymupdf.Rect(80,359,2050,1968)
# Mineral paper coordinates use embedded GeoPDF measure and an exploratory
# +0.0753 E / +0.0578 N translation, fitted only from Natural Earth rivers.
# EPSG:4326 is a working assumption for this visualization, not a verified CRS.
def getpix(page,box):
 p=page.get_pixmap(matrix=pymupdf.Matrix(1,1),clip=box,alpha=False)
 return np.frombuffer(p.samples,np.uint8).reshape(p.height,p.width,3).copy()
g=getpix(geo,gbox);m=getpix(mineral,mbox)
gbounds=((gbox.x0+276.36)/157.593,(2281.63-gbox.y1)/157.586,(gbox.x1+276.36)/157.593,(2281.63-gbox.y0)/157.586)
def embedded(x,y):
 return (2.47619+(x-74.23969)*12.54519/(2051.1915-74.23969),14.04668-(y-(2160-1801.2761))*10.20997/((2160-192.29888)-(2160-1801.2761)))
l,t=embedded(mbox.x0,mbox.y0);r,b=embedded(mbox.x1,mbox.y1);mbounds=(l+.0753,b+.0578,r+.0753,t+.0578)
gtrans=from_bounds(*gbounds,g.shape[1],g.shape[0]);mtrans=from_bounds(*mbounds,m.shape[1],m.shape[0]);crs='EPSG:4326'
out=np.zeros_like(g);coverage=np.zeros(g.shape[:2],dtype=np.uint8)
for b in range(3):reproject(m[:,:,b],out[:,:,b],src_transform=mtrans,src_crs=crs,dst_transform=gtrans,dst_crs=crs,resampling=Resampling.nearest)
reproject(np.ones(m.shape[:2],dtype=np.uint8),coverage,src_transform=mtrans,src_crs=crs,dst_transform=gtrans,dst_crs=crs,resampling=Resampling.nearest)
# An alpha blend is a qualitative visualization only. Symbols/colours cannot be
# reliably classified from it. The unblended layers are supplied separately.
blend=g.copy();valid=coverage!=0;blend[valid]=(g[valid].astype(np.float32)*.62+out[valid].astype(np.float32)*.38).astype(np.uint8)
def write_tif(path,a,transform,description):
 profile=dict(driver='GTiff',height=a.shape[0],width=a.shape[1],count=3,dtype='uint8',crs=crs,transform=transform,compress='deflate',predictor=2,tiled=True)
 with rasterio.open(path,'w',**profile) as d:
  d.write(np.moveaxis(a,2,0));d.update_tags(DESCRIPTION=description,STATUS='PRELIMINARY; unknown original datum; EPSG:4326 assigned solely as display assumption; not survey-accurate',REFERENCE='Natural Earth 1:10m Niger and Benue, exploratory raster colour match')
write_tif(P/'Combined_Geology_Minerals_PRELIMINARY.tif',blend,gtrans,'62% geology plus 38% mineral colour blend; legend and symbols cannot be reliably decoded from this composite')
write_tif(P/'Geology_PRELIMINARY.tif',g,gtrans,'2011 PDF printed-grid fit; source datum unknown')
write_tif(P/'Minerals_PRELIMINARY.tif',m,mtrans,'2023 embedded measure plus provisional +0.0753 degrees longitude and +0.0578 degrees latitude')
# Clearly watermark the preview without changing the georeferenced raster.
im=Image.fromarray(blend); header=Image.new('RGB',(im.width,70),'white');d=ImageDraw.Draw(header)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',21);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except OSError:font=small=ImageFont.load_default()
d.text((12,5),'PRELIMINARY OVERLAY — NOT VERIFIED COORDINATES',fill='#9a1e15',font=font)
d.text((12,36),'Geology 62% + minerals 38%; use original PDFs for legends. River-fitted mineral shift is experimental.',fill='#202020',font=small)
canvas=Image.new('RGB',(im.width,im.height+70),'white');canvas.paste(header,(0,0));canvas.paste(im,(0,70));canvas.save(P/'Combined_Geology_Minerals_PRELIMINARY.png',optimize=True)
notes='''PROVISIONAL GIS LAYERS — NOT SURVEY ACCURATE\n\nGeology_PRELIMINARY.tif: 2011 PDF rendered at 72 dpi and registered from its printed grid.\nMinerals_PRELIMINARY.tif: 2023 PDF rendered at 72 dpi; embedded measure plus +0.0753 degrees east and +0.0578 degrees north, an exploratory fit to Natural Earth river centrelines.\nBoth TIFFs carry EPSG:4326 only as a working visualization assumption; neither original datum is established. No verified datum transformation was performed. Overlay is not for exploration, licensing, navigation, surveying or exact location. Read the River Alignment report and original PDF legends.\n'''
with zipfile.ZipFile(P/'Provisional_GIS_Layers.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 z.writestr('README.txt',notes)
 for f in ['Geology_PRELIMINARY.tif','Minerals_PRELIMINARY.tif','Niger_Benue_Natural_Earth.geojson']:z.write(P/f,f)
for f in ['Geology_PRELIMINARY.tif','Minerals_PRELIMINARY.tif']:(P/f).unlink()
print('Saved preview, provisional composite GeoTIFF, and zip of separate GIS layers.')
