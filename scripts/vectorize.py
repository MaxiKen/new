"""Reproducible, source-limited reconstruction of the supplied NGSA image."""
from pathlib import Path
import json, hashlib, time, csv
import numpy as np
import pandas as pd
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import remove_small_holes, disk, binary_closing
import rasterio
from rasterio.features import shapes, rasterize
from affine import Affine
import shapely
from shapely.geometry import shape, LineString, box
from shapely.ops import unary_union, linemerge, polygonize
from shapely.affinity import affine_transform
import geopandas as gpd
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'gis_output'; OUT.mkdir(exist_ok=True)
def log(*s): print(time.strftime('%H:%M:%S'),*s,flush=True)
src=ROOT/'NGSA_map_geology_legend_isolated.png'
a=np.array(Image.open(src).convert('RGB'))
legend=pd.read_csv(ROOT/'scripts/legend.tsv',sep='\t',keep_default_na=False)
legend['group_name']=legend.group_name.str.replace('Pre-Alkaline young granite suite','Per Alkaline young Granite Series (as printed)',regex=False)
legend.insert(0,'legend_id',[f'L{i+1:03}' for i in range(len(legend))])
for i in legend.index:
 y=round(116.5+i*(3398.5-116.5)/91); patch=a[y-10:y+11,5471:5512]
 c,n=np.unique(patch.reshape(-1,3),axis=0,return_counts=True); rgb=c[n.argmax()]
 legend.loc[i,'row_y']=y
 for k,v in zip(['r','g','b'],rgb): legend.loc[i,k]=int(v)
 legend.loc[i,'age_label']=('Neogene (as printed)' if i<7 else 'Tertiary to Recent' if i<9 else 'Palaeogene (as printed)' if i<19 else 'Cretaceous' if i<48 else 'Jurassic' if i<58 else 'Pre-Cambrian to Cambrian')
legend[['row_y','r','g','b']]=legend[['row_y','r','g','b']].astype(int)
legend['note']='Transcribed from supplied legend; spelling lightly normalised; age labels not modernised.'
legend.loc[legend.legend_id=='L026','note']='Formation name appears as Bassage in source; transcription needs verification.'
legend.to_csv(OUT/'legend_lookup.csv',index=False)
# Preserve duplicate-colour alternatives rather than silently choosing a rock unit.
records=[dict(class_id=0,code='BACKGROUND',rgb=(255,255,255),legend_ids='',lithology='Background',formation='',group_name='',age_label='',status='excluded',kind='background')]
for rgb,subset in legend.groupby(['r','g','b'],sort=False):
 join=lambda col:' | '.join(dict.fromkeys(subset[col].tolist()))
 records.append(dict(class_id=len(records),code=join('code'),rgb=tuple(map(int,rgb)),legend_ids=join('legend_id'),lithology=join('lithology'),formation=join('formation'),group_name=join('group_name'),age_label=join('age_label'),status='ambiguous' if len(subset)>1 else 'colour_match',kind='geology'))
records.append(dict(class_id=len(records),code='WATER',rgb=(152,218,242),legend_ids='',lithology='Filled surface water',formation='Not applicable',group_name='Water',age_label='Not applicable',status='visual_water',kind='water'))
records.append(dict(class_id=len(records),code='UNRESOLVED',rgb=(255,121,127),legend_ids='',lithology='Unresolved pink-red source fill; rock unit not established',formation='Unresolved',group_name='Unresolved geology',age_label='Unresolved',status='unresolved',kind='geology'))
records.append(dict(class_id=len(records),code='UNRES_BLUE',rgb=(103,116,255),legend_ids='',lithology='Unresolved blue source fill; rock unit not established',formation='Unresolved',group_name='Unresolved geology',age_label='Unresolved',status='unresolved',kind='geology'))
classes=pd.DataFrame(records); classes.to_csv(OUT/'colour_classes.csv',index=False)
palette=np.array([r['rgb'] for r in records],dtype=np.uint8)
x0,y0,x1,y1=69,95,4155,3430
im=a[y0:y1,x0:x1]; h,w=im.shape[:2]; del a
log('Classifying',w,h,'pixels;',len(records)-1,'source classes')
tree=cKDTree(palette.astype(float)); labs=np.zeros((h,w),np.uint8); dist=np.empty((h,w),np.float32)
for y in range(0,h,100):
 d,ix=tree.query(im[y:y+100].reshape(-1,3),workers=2)
 labs[y:y+100]=ix.reshape(-1,w); dist[y:y+100]=d.reshape(-1,w)
# Accurate-colour seeds; lines, text and antialiases are not geological classes.
seeds=(dist<=8)&(labs>0)
# Low-saturation geological fills are retained alongside saturated colours.
sat=im.max(2).astype(int)-im.min(2).astype(int)
near_colour=ndi.maximum_filter((seeds&(sat>20)).astype(np.uint8),size=15)>0
# Low-saturation filled units (notably Lass) are legitimate: retain them.
# Printed grid is RGB 76,76,76 and outside the palette tolerance.
mask=binary_closing(seeds,footprint=disk(4))
mask=remove_small_holes(mask,area_threshold=512)
cc,n=ndi.label(mask); sizes=np.bincount(cc.ravel()); mask &= sizes[cc]>=8
# Repair narrow map-furniture gaps in the closed mask; never flood the exterior background.
_,nearest=ndi.distance_transform_edt(~seeds,return_indices=True)
labels=labs[tuple(nearest)]; labels[~mask]=0
repaired=int(np.count_nonzero(mask&~seeds)); del nearest,cc,im,dist,seeds,near_colour,sat
# Remove isolated 1-3 pixel colour specks. Larger disconnected components retained.
noise=np.zeros_like(mask)
for k in range(1,len(records)):
 cc,n=ndi.label(labels==k); sizes=np.bincount(cc.ravel()); noise|=(labels==k)&(sizes[cc]<4)
if noise.any():
 _,ii=ndi.distance_transform_edt(noise,return_indices=True);labels[noise]=labels[tuple(ii)][noise];del ii
labels[~mask]=0
# Exclude thin isolated water-colour linework: only filled areas with an interior core.
water_id=next(r['class_id'] for r in records if r['kind']=='water')
cc,n=ndi.label(labels==water_id)
width=ndi.distance_transform_edt(labels==water_id)
maxwidth=ndi.maximum(width,cc,index=np.arange(n+1))
water_lines=(labels==water_id)&(maxwidth[cc]<2.5)
labels[water_lines]=0
np.save(OUT/'classification.npy',labels)
log('Polygonising raster')
raw=[]; rawclass=[]
for geo,k in shapes(labels,connectivity=4,transform=Affine.identity()):
 raw.append(shape(geo));rawclass.append(int(k))
raw=np.array(raw,dtype=object);rawclass=np.array(rawclass)
log('Raw faces',len(raw),'valid coverage',shapely.coverage_is_valid(raw))
# Shared-edge simplification, then smooth the unique network ONCE, not each polygon.
simp=shapely.coverage_simplify(raw,0.65,simplify_boundary=False)
log('Building shared edge network')
network=linemerge(unary_union(shapely.boundary(simp).tolist()))
lines=list(network.geoms) if hasattr(network,'geoms') else [network]
def smooth(line):
 p=np.array(line.coords)
 # Densify long chords, so corner cutting is strictly sub-pixel.
 p=np.array(shapely.segmentize(line,2.0).coords)
 closed=np.array_equal(p[0],p[-1])
 for _ in range(2):
  q=.8*p[:-1]+.2*p[1:]; r=.2*p[:-1]+.8*p[1:]
  v=np.empty((2*len(q),2));v[0::2]=q;v[1::2]=r
  p=np.vstack([v,v[0]]) if closed else np.vstack([p[0],v,p[-1]])
 # Keep rectangular crop frame exact. Geological contacts are not squared off.
 if np.all(np.array(line.coords)[:,0]==0) or np.all(np.array(line.coords)[:,0]==w) or np.all(np.array(line.coords)[:,1]==0) or np.all(np.array(line.coords)[:,1]==h): return line
 return LineString(p)
log('Smoothing',len(lines),'shared edge chains')
smoothed=[smooth(l) for l in lines]
faces=list(polygonize(unary_union(smoothed)))
log('Assigning',len(faces),'smoothed faces by greatest overlap with raw source components')
rt=shapely.STRtree(raw); final=[]; ids=[]; refids=[]
for p in faces:
 candidates=rt.query(p,predicate='intersects')
 if not len(candidates):continue
 aa=shapely.area(shapely.intersection(raw[candidates],p)); j=candidates[np.argmax(aa)]
 if rawclass[j]==0:continue
 if p.area<.05:continue
 final.append(p);ids.append(rawclass[j]);refids.append(int(j))
# Georeference from visible one-degree grid, not an invented Nigerian boundary.
xpix=np.array([288,616,945,1273,1602,1930,2258,2587,2915,3244,3571,3900],float)
yPix=np.array([388,715,1045,1373,1702,2030,2358,2686,3015,3343],float)
ax,bx=np.polyfit(xpix,np.arange(3,15),1);ay,by=np.polyfit(yPix,np.arange(13,3,-1),1)
trans=Affine(ax,0,bx+ax*x0,0,ay,by+ay*y0)
grid={'method':'Independent linear fits to printed longitude and latitude graticule; coordinate reference assigned WGS84 for interoperability, original datum unknown. No external control used.','source_datum':'Unknown','output_crs':'EPSG:4326 (assumed datum)','affine':list(trans)[:6],'x_pixels':xpix.tolist(),'longitudes':list(range(3,15)),'y_pixels':yPix.tolist(),'latitudes':list(range(13,3,-1)),'grid_fit_rmse_pixels_x':float(np.sqrt(np.mean(((ax*xpix+bx-np.arange(3,15))/ax)**2))),'grid_fit_rmse_pixels_y':float(np.sqrt(np.mean(((ay*yPix+by-np.arange(13,3,-1))/ay)**2)))}
(OUT/'georeferencing.json').write_text(json.dumps(grid,indent=2))
with rasterio.open(OUT/'classified_reference.tif','w',driver='GTiff',height=h,width=w,count=1,dtype='uint8',crs='EPSG:4326',transform=trans,compress='DEFLATE',nodata=0) as dst:
 dst.write(labels,1); dst.write_colormap(1,{i:tuple(map(int,p))+((0 if i==0 else 255),) for i,p in enumerate(palette)})
geod=Geod(ellps='WGS84'); rows=[]; geometries=[]
for i,(p,k,ri) in enumerate(zip(final,ids,refids),1):
 rec=records[k];g=affine_transform(p,[ax,0,0,ay,bx+ax*x0,by+ay*y0]);area,perim=geod.geometry_area_perimeter(g)
 edge=int(p.bounds[0]<.01 or p.bounds[1]<.01 or p.bounds[2]>w-.01 or p.bounds[3]>h-.01)
 row={'poly_id':i,'class_id':int(k),'src_part':ri+1,'unit_code':rec['code'],'legend_ids':rec['legend_ids'],'feat_type':rec['kind'],'lithology':rec['lithology'],'formation':rec['formation'],'geo_group':rec['group_name'],'age_label':rec['age_label'],'attr_stat':rec['status'],'review':1,'edge_clip':edge,'area_km2':abs(area)/1e6,'perim_km':perim/1000,'src_px':float(raw[ri].area),'rgb_hex':'#'+''.join(f'{c:02X}' for c in rec['rgb'])}
 rows.append(row);geometries.append(g)
gdf=gpd.GeoDataFrame(rows,geometry=geometries,crs='EPSG:4326')
log('Exporting',len(gdf),'independent Polygon features')
gdf.to_file(OUT/'ngsa_units_water.shp',encoding='UTF-8',engine='pyogrio')
# Shapefile is the requested primary exchange format.
gdf.drop(columns='geometry').to_csv(OUT/'polygon_attributes.csv',index=False)
# Re-open the actual shapefile: validate deliverable, not only in-memory objects.
check=gpd.read_file(OUT/'ngsa_units_water.shp'); pix=np.array(final,dtype=object)
coverage=bool(shapely.coverage_is_valid(pix)); invalid=int((~check.is_valid).sum())
raw_fg=raw[rawclass>0]; raw_area=float(shapely.area(raw_fg).sum());new_area=float(shapely.area(pix).sum())
# Pairwise area overlap of exported features (degree units), via spatial index.
tr=shapely.STRtree(check.geometry.values); pairs=tr.query(check.geometry.values,predicate='intersects'); sel=pairs[0]<pairs[1]
ov=shapely.area(shapely.intersection(check.geometry.values[pairs[0][sel]],check.geometry.values[pairs[1][sel]]))
qa={'source_file':src.name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_size_pixels':[6268,3540],'crop_xyxy':[x0,y0,x1,y1],'legend_rows':len(legend),'source_colour_classes':len(records)-1,'polygon_count':len(check),'geology_polygons':int((check.feat_type=='geology').sum()),'water_polygons':int((check.feat_type=='water').sum()),'status_counts':check.attr_stat.value_counts().to_dict(),'invalid_geometry_count':invalid,'empty_geometry_count':int(check.is_empty.sum()),'multipart_count':int((check.geom_type!='Polygon').sum()),'unique_polygon_ids':bool(check.poly_id.is_unique),'valid_pixel_coverage':coverage,'positive_overlap_pairs_above_1e_15_degree2':int((ov>1e-15).sum()),'raw_foreground_components':len(raw_fg),'source_components_not_represented':int(len(set(np.where(rawclass>0)[0])-set(refids))),'repaired_pixels':repaired,'removed_colour_speck_pixels':int(noise.sum()),'excluded_thin_water_line_pixels':int(water_lines.sum()),'raw_pixel_area':raw_area,'smoothed_pixel_area':new_area,'smoothing_net_area_change_percent':100*(new_area/raw_area-1),'edge_clipped_features':int(check.edge_clip.sum()),'minimum_retained_colour_component_pixels':4,'small_mask_component_threshold_pixels':8,'review_required':'All polygons require source/field verification; identical legend colours and unmatched fill cannot be definitively attributed from this raster.'}
(OUT/'qa_report.json').write_text(json.dumps(qa,indent=2));log(json.dumps(qa,indent=2))
# Source colour preview for direct visual comparison.
preview=Image.fromarray(palette[labels]);preview.thumbnail((1600,1600));preview.save(OUT/'classification_preview.png')
# Retain only exchange formats, not the temporary classification array.
(OUT/'classification.npy').unlink()
