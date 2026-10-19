"""Finalize: rivers clipped to boundary; corrected mineral GCP table; geology QML from final shp."""
import sys, csv
sys.path.insert(0,"scripts")
import numpy as np
import common as C
import geopandas as gpd

# --- Rivers: clip ALL features (incl. smallest streams) to final boundary
riv=gpd.read_file("work/Rivers_raw.geojson")
bnd=gpd.read_file("output/02_Shapefiles/Nigeria_Boundary.shp")
clipped=gpd.clip(riv, bnd)
# explode multipart results to single lines, drop empties/tiny slivers <50 m (clip artefacts only)
clipped=clipped.explode(index_parts=False).reset_index(drop=True)
clipped=clipped[clipped.geometry.notna() & (~clipped.geometry.is_empty)]
eq=clipped.to_crs(6933)
clipped["LEN_KM"]= (eq.geometry.length/1000).round(3)
clipped=clipped[clipped["LEN_KM"]>=0.05].reset_index(drop=True)
clipped["RIV_ID"]=range(1,len(clipped)+1)
if "SOURCE" not in clipped: clipped["SOURCE"]="NGSA Mineral Resources Map 2023 (vector rivers layer)"
clipped=clipped[["RIV_ID","LEN_KM","SOURCE","geometry"]]
clipped.to_file("output/02_Shapefiles/Rivers.shp")
print(f"Rivers final: {len(clipped)} features, total {clipped['LEN_KM'].sum():,.0f} km, "
      f"min {clipped['LEN_KM'].min():.2f} km, median {clipped['LEN_KM'].median():.2f} km, max {clipped['LEN_KM'].max():.0f} km")
print(f" (input unclipped: {len(riv)} features)")

# --- Mineral GCP table (graticule intersections, both datums)
rows=[]
for lon in (4,6,8,10,12,14):
    for lat in (5,7,9,11,13):
        x,y=C.mineral_lonlat_to_pdf(lon,lat)
        col=(x-C.MIN_FRAME[0])*C.MIN_NATIVE_PXPT-0.5; row=(y-C.MIN_FRAME[1])*C.MIN_NATIVE_PXPT-0.5
        rows.append(dict(LON_PRINTED=lon, LAT_PRINTED=lat, LON_WGS84=lon+C.MIN_CORR_DX, LAT_WGS84=lat+C.MIN_CORR_DY,
                         PDF_X=round(float(x),2), PDF_Y=round(float(y),2), NATIVE_COL=round(float(col),1), NATIVE_ROW=round(float(row),1)))
with open("output/04_Tables/GCP_Mineral_Map_CORRECTED_WGS84.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("wrote GCP_Mineral_Map_CORRECTED_WGS84.csv", len(rows))

# --- Geology QML regenerated from final shapefile (unique CODE -> colour from R,G,B of first poly)
g=gpd.read_file("output/02_Shapefiles/Geology_Rocks.shp", columns=["UNIT_IDX","CODE","LITHOLOGY","R","G","B"] if False else None)
print("geology fields:", list(g.columns))
cats={}
for _,r in g.iterrows():
    key=(r["CODE"] or f"U{r['UNIT_IDX']}")
    if key not in cats:
        cats[key]=(int(r["R"]),int(r["G"]),int(r["B"]), str(r["LITHOLOGY"])[:80])
print("legend categories:", len(cats))
def xml_esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace('"',"&quot;")
syms=""; catsxml=""
for i,(code,(R,G,B,lith)) in enumerate(sorted(cats.items())):
    syms+=f'<symbol force_rhr="0" frame_rate="10" type="fill" is_animated="0" name="{i}" alpha="1" clip_to_extent="1"><data_defined_properties><Option type="Map"><Option value="" type="QString" name="name"/></Option></data_defined_properties><layer pass="0" class="SimpleFill" locked="0"><Option type="Map"><Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/><Option value="{R},{G},{B},255" type="QString" name="color"/><Option value="bevel" type="QString" name="joinstyle"/><Option value="0,0" type="QString" name="offset"/><Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/><Option value="MM" type="QString" name="offset_unit"/><Option value="90,90,90,255" type="QString" name="outline_color"/><Option value="solid" type="QString" name="outline_style"/><Option value="0.12" type="QString" name="outline_width"/><Option value="MM" type="QString" name="outline_width_unit"/><Option value="solid" type="QString" name="style"/></Option></layer></symbol>\n'
    catsxml+=f'<category value="{xml_esc(str(code))}" symbol="{i}" label="{xml_esc(str(code))} - {xml_esc(lith)}" render="true"/>\n'
qml=f'''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.28.0"><renderer-v2 symbollevels="0" enableorderby="0" forceraster="0" type="categorizedSymbol" attr="CODE">
<categories>{catsxml}</categories><symbols>{syms}</symbols></renderer-v2></qgis>
'''
open("output/02_Shapefiles/Geology_Rocks.qml","w").write(qml)
print("wrote Geology_Rocks.qml with", len(cats), "categories")
