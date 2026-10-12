from pathlib import Path
import json, zipfile, xml.etree.ElementTree as ET
import geopandas as gpd
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
R=Path(__file__).resolve().parents[1];O=R/'gis_output'
g=gpd.read_file(O/'ngsa_units_water.shp');qa=json.loads((O/'qa_report.json').read_text())
# Verify shapefile attribute round trip and full source-component independence.
a=pd.read_csv(O/'polygon_attributes.csv',keep_default_na=False)
for col in ['poly_id','class_id','src_part','unit_code','legend_ids','lithology','formation','geo_group','age_label','attr_stat']:
 actual=g[col].fillna('').astype(str).tolist();expected=a[col].astype(str).tolist()
 assert actual==expected, f'Attribute round-trip failed: {col}'
assert g.poly_id.is_unique and g.src_part.is_unique
assert (g.geom_type=='Polygon').all() and g.is_valid.all()
qa['attribute_roundtrip_verified']=True;qa['one_feature_per_retained_source_component']=True
(O/'qa_report.json').write_text(json.dumps(qa,indent=2))
# QGIS auto-loads the matching QML; colours match source, no polygon strokes.
root=ET.Element('qgis',version='3.40',styleCategories='Symbology')
renderer=ET.SubElement(root,'renderer-v2',type='categorizedSymbol',attr='class_id',symbollevels='0',forceraster='0')
cats=ET.SubElement(renderer,'categories'); syms=ET.SubElement(renderer,'symbols')
for ix,(cid,sub) in enumerate(g.groupby('class_id')):
 r=sub.iloc[0]; ET.SubElement(cats,'category',value=str(cid),label=f"{r.unit_code} — {r.lithology}",symbol=str(ix),render='true',type='long')
 symbol=ET.SubElement(syms,'symbol',name=str(ix),type='fill',alpha='1',clip_to_extent='1',force_rhr='0')
 layer=ET.SubElement(symbol,'layer',{'class':'SimpleFill','enabled':'1','locked':'0','pass':'0'})
 options=ET.SubElement(layer,'Option',type='Map')
 rgb=','.join(str(int(r.rgb_hex[j:j+2],16)) for j in [1,3,5])+',255'
 for name,value in [('color',rgb),('style','solid'),('outline_style','no'),('outline_width','0'),('joinstyle','round')]: ET.SubElement(options,'Option',name=name,value=value,type='QString')
ET.indent(root);ET.ElementTree(root).write(O/'ngsa_units_water.qml',encoding='utf-8',xml_declaration=True)
fig=plt.figure(figsize=(14,12),facecolor='#f5f3ee');ax=fig.add_axes([.055,.15,.89,.73]); ax.set_facecolor('white')
g.plot(ax=ax,color=g.rgb_hex,edgecolor='none',linewidth=0,antialiased=True)
ax.set_xlim(2.25,14.85);ax.set_ylim(3.6,14);ax.set_xlabel('Longitude · degrees east',fontsize=9,color='#555555');ax.set_ylabel('Latitude · degrees north',fontsize=9,color='#555555')
ax.tick_params(colors='#777777',labelsize=8)
for s in ax.spines.values():s.set_color('#cccccc')
ax.annotate('N',xy=(14.35,12.5),xytext=(14.35,11.7),ha='center',fontsize=11,arrowprops=dict(arrowstyle='-|>',color='#1f3939'))
fig.text(.055,.948,'NIGERIA  /  GEOLOGICAL POLYGONS',fontsize=22,weight='bold',color='#183d3b')
fig.text(.055,.922,'Raster-derived reconstruction • independent singlepart features • filled water areas',fontsize=11,color='#52625e')
fig.text(.055,.105,f"{len(g):,} independent polygons     |     92 source legend entries     |     Shared boundaries smoothed",fontsize=12,weight='bold',color='#183d3b')
fig.text(.055,.077,'439 polygons have ambiguous or unresolved unit attribution. Source colours are retained, not certainty-coded.',fontsize=10,color='#555555')
fig.text(.055,.053,'Georeferenced from the printed grid. WGS84 datum assumed; original datum unverified. Not an authoritative NGSA vector dataset.',fontsize=9,color='#555555')
fig.text(.055,.032,'Straight edges at the ocean/map extent are source clipping boundaries, not geological contacts. See README.md and qa_report.json.',fontsize=9,color='#555555')
fig.savefig(O/'vector_map_preview.png',dpi=170,facecolor=fig.get_facecolor());plt.close(fig)
fields={
'poly_id':'Unique polygon identifier. Each record is one spatially connected Polygon; no multipart records.',
'class_id':'Source colour class; joins colour_classes.csv. NOT a unique geological unit when colours are duplicated.',
'src_part':'Unique pre-smoothing connected component identifier. One exported feature per retained component.',
'unit_code':'Code transcribed from legend; alternatives separated by |. Codes in the source are not globally unique.',
'legend_ids':'Stable L001-L092 legend row identifiers. Alternatives separated by |; blank for water/unresolved.',
'feat_type':'geology or water.',
'lithology':'Full legible lithological description, or all same-colour alternatives. Unresolved classes explicitly identified.',
'formation':'Formation/group or depositional description as printed. Alternatives separated by |. Not stated where absent.',
'geo_group':'Legend group/suite where available; otherwise descriptive Sedimentary/Volcanic/Surficial deposits.',
'age_label':'Broad age bracket as printed, not corrected to modern stratigraphy. No inferred numerical ages.',
'attr_stat':'colour_match = unique palette match, NOT field-verified; ambiguous = duplicated swatch; unresolved = no close swatch; visual_water = filled water colour.',
'review':'1 for all features: manual verification recommended for this raster-derived dataset.',
'edge_clip':'1 if feature touches the cropped map frame; such edges must not be interpreted as natural boundaries.',
'area_km2':'Absolute ellipsoidal area on assumed WGS84, square kilometres; not survey accuracy.',
'perim_km':'Ellipsoidal exterior-ring perimeter, kilometres (hole perimeters excluded).',
'src_px':'Area of cleaned source component in full-resolution raster pixels, before smoothing.',
'rgb_hex':'Source/legend display colour in #RRGGBB notation.'}
(O/'field_dictionary.csv').write_text('field,description\n'+''.join(f'{k},"{v.replace(chr(34),chr(34)*2)}"\n' for k,v in fields.items()))
