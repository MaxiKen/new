import geopandas as gpd, pandas as pd, numpy as np, sys, shutil, os
sys.path.insert(0,"work")
import transforms as T
from shapely.ops import transform as shp_transform
# ---- M2 remap BF->VP ----
def bf_to_vp_array(xs,ys):
    x_pt=1104.0922160059586+(xs-8.999624062683695)*1000.0/6.3408036208710055
    yb=1241.0996111966826+(ys-10.488502044741583)*1000.0/6.350936179071387
    return (T.MIN_LON0+T.MIN_DLDX*x_pt, T.MIN_LAT0+T.MIN_DLADY*(2160-yb))
os.makedirs("corrected_delivery/06_Other_PDF_layers/minerals_2023_VP_corrected",exist_ok=True)
m2=gpd.read_file("shapefile_results/pdf_selected_layers/minerals_2023/M2_geology_areas.shp")
m2['geometry']=m2.geometry.apply(lambda g: shp_transform(bf_to_vp_array,g))
eq=m2.to_crs(6933)
m2['area_km2']=(eq.geometry.area/1e6).round(2); m2['perim_km']=(eq.geometry.length/1e3).round(2)
m2.to_file("corrected_delivery/06_Other_PDF_layers/minerals_2023_VP_corrected/M2_geology_areas_VP.shp")
peg=gpd.read_file("shapefile_results/pdf_selected_layers/minerals_2023/M2_pegmatite_marks.shp")
peg['geometry']=peg.geometry.apply(lambda g: shp_transform(bf_to_vp_array,g))
peg['lon']=peg.geometry.x.round(6); peg['lat']=peg.geometry.y.round(6)
peg.to_file("corrected_delivery/06_Other_PDF_layers/minerals_2023_VP_corrected/M2_pegmatite_marks_VP.shp")
shutil.copy("shapefile_results/pdf_selected_layers/minerals_2023/M2_accuracy_assessment.md","corrected_delivery/06_Other_PDF_layers/minerals_2023_VP_corrected/")
print("M2 remapped:",len(m2),len(peg),[round(v,2) for v in m2.total_bounds])
# ---- G layers copy ----
dst="corrected_delivery/06_Other_PDF_layers/geology_2011_vectors"
os.makedirs(dst,exist_ok=True)
for f in os.listdir("shapefile_results/pdf_selected_layers/geology_2011"):
    shutil.copy(f"shapefile_results/pdf_selected_layers/geology_2011/{f}",f"{dst}/{f}")
print("G copied:",os.listdir(dst))
# ---- reference layers ----
for name in ["state_boundaries","lga_boundaries"]:
    src=f"shapefiles/nigeria_online_layers/{name}"; d2=f"corrected_delivery/07_Reference_layers/{name}"
    os.makedirs(d2,exist_ok=True)
    for f in os.listdir(src): shutil.copy(f"{src}/{f}",f"{d2}/{f}")
print("refs copied")
# ---- geology QML ----
g=gpd.read_file("corrected_delivery/03_Geology_rock_units_FILLED/nigeria_geology_units_FILLED.shp")
modefill=g.groupby(g.code.astype(str)).fill.agg(lambda s:s.mode().iloc[0])
desc=g.groupby(g.code.astype(str)).leg_desc.first()
def hex2rgb(h):
    h=h.lstrip('#'); return int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
cats=[]; syms=[]
for i,code in enumerate(sorted(modefill.index)):
    r,gg,b=hex2rgb(str(modefill[code]))
    lab=f"{code} - {str(desc.get(code,''))[:60]}".replace('&','&amp;').replace('<','').replace('>','').replace('"','')
    cats.append(f'<category value="{code}" label="{lab}" symbol="{i}" render="true"/>')
    syms.append(f'<symbol name="{i}" type="fill" alpha="1" clip_to_extent="1" is_animated="0" force_rhr="0"><data_defined_properties><Option type="Map"><Option name="name" type="QString" value=""/></Option></data_defined_properties><layer class="SimpleFill" enabled="1" pass="0"><prop k="color" v="{r},{gg},{b},255"/><prop k="outline_color" v="70,70,70,255"/><prop k="outline_style" v="solid"/><prop k="outline_width" v="0.06"/><prop k="outline_width_unit" v="MM"/><prop k="style" v="solid"/></layer></symbol>')
qml=f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0-Firenze" styleCategories="Symbology">
  <renderer-v2 type="categorizedSymbol" attr="code" symbollevels="0" enableorderby="0">
    <categories>{''.join(cats)}</categories>
    <symbols>{''.join(syms)}</symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
</qgis>'''
open("corrected_delivery/03_Geology_rock_units_FILLED/nigeria_geology_units_FILLED.qml","w").write(qml)
print("geology QML categories:",len(cats))
# ---- minerals QML categorized by LEG_NO ----
import matplotlib.cm as cm
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
pal=[]
for cmap in ('tab20','tab20b','tab20c','Dark2'):
    pal+= [tuple(int(round(v*255)) for v in c[:3]) for c in cm.get_cmap(cmap).colors]
cats=[]; syms=[]
for i,(_,row) in enumerate(leg.iterrows()):
    r,gg,b=pal[i%len(pal)]
    lab=f"{int(row.legend_no)} {row.point_attribute_name}".replace('&','&amp;').replace('"','')
    cats.append(f'<category value="{int(row.legend_no)}" label="{lab}" symbol="{i}" render="true"/>')
    syms.append(f'<symbol name="{i}" type="marker" alpha="1" clip_to_extent="1" is_animated="0" force_rhr="0"><data_defined_properties><Option type="Map"><Option name="name" type="QString" value=""/></Option></data_defined_properties><layer class="SimpleMarker" enabled="1" pass="0"><prop k="color" v="{r},{gg},{b},255"/><prop k="name" v="circle"/><prop k="outline_color" v="255,255,255,255"/><prop k="outline_width" v="0.25"/><prop k="outline_width_unit" v="MM"/><prop k="size" v="2.6"/><prop k="size_unit" v="MM"/></layer></symbol>')
qml=f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0-Firenze" styleCategories="Symbology">
  <renderer-v2 type="categorizedSymbol" attr="LEG_NO" symbollevels="0" enableorderby="0">
    <categories>{''.join(cats)}</categories>
    <symbols>{''.join(syms)}</symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
</qgis>'''
open("corrected_delivery/04_Minerals_RECENTRED/nigeria_mineral_symbols_CORRECTED.qml","w").write(qml)
print("minerals QML categories:",len(cats))
