"""Match v2 palette (86) to NGSA legend rows (92 transcribed) by swatch colours sampled from iso sheet."""
import sys, csv, json
sys.path.insert(0,"scripts")
import numpy as np, cv2
from PIL import Image
import geopandas as gpd
Image.MAX_IMAGE_PIXELS=None

# Transcribed top->bottom from NGSA explanations (code, lithology, formation/group or "")
LEGEND = [
("Al","Alluvium","Sediments"),
("MWS","Sands, Gravels and Clay","Meander belt, back swamps, fresh water swamps"),
("AB","Sands and Pebbles","Abandoned Beach Ridges"),
("MS","Sand, Clay and Mangrove Swamps","Mangrove swamps"),
("SDsm","Sand, Clay and Swamp","Sombreiro Deltaic Formation"),
("Cst","Sands, Clays, siltstones and limestones","Chad Formation"),
("Bnst","Sand and Clay","Benin Formation"),
("b","Younger Basalt","Newer Basalt"),
("bb","Basalt","Older Basalt"),
("OAlgs","Lignite, Claystone and shale","Ogwashi-Asaba Formation"),
("Issh","Clay clayey sands and shale","Ilaro Formation"),
("Gwss","Sandstone and Clay",""),
("Glcl","Sandstones and Clays","Gwandu Formation"),
("Wss","Sandstone and Clay",""),
("Esh","Shale and limestone",""),
("Imsh","Clay and Shale with Limestone Intercalations","Imo Group"),
("Kss","Sandstone, shale and Clay","Kerri-Kerri Formation"),
("Dsh","Shale","Dange Formation (Sokoto Group)"),
("Kls","Limestone","Kalambaina Formation (Sokoto Group)"),
("Gss","Sandstone, Siltstone, Shale and ironstone","Gombe Formation"),
("Ajst","False-bedded sandstone","Ajali Formation"),
("Ncsh","Coal, shale and sandstone","Nsukka Formation"),
("Ncsh","Sandstone, limestone, Coal","Nsukka Formation"),
("Asl","Sandstone and Limestone","Abeokuta Formation"),
("Mcst","Coal, Sandstone and Shale","Mamu Formation"),
("Bssf","Sandstone and Ironstone","Bassange Formation"),
("Nsh","Shale and mudstone","Nkporo Formation"),
("ANsh","Shale and Limestone","Awgu Formation"),
("Tst","Sandstone, siltstone and shale","Taloka Formation"),
("Glls","Limestone","Dukamaje Formation"),
("Wss","Sandstone, clays and shale","Dukamaje and Wurno Formation, Rima Group"),
("Wcs","Clays and loose sandstone","Dukamaje and Wurno Formation, Rima Group"),
("Wsh","Shale (Phosphate nodules)","Dukamaje and Wurno Formation, Rima Group"),
("Ts","Siltstone and Sandstone","Dukamaje and Wurno Formation, Rima Group"),
("Psh","Shale, limestone and sandstone","Pindiga Formation"),
("Lass","Sandstone, shale and sandy shale","Lafia-Wukari Formation"),
("NPss","Feldspathic sandstone and siltstone","Nupe Formation"),
("Glpg","Pebbles and grit","Gundumi-Illo Formation"),
("Glss","Clay grit and pebbles","Gundumi-Illo Formation"),
("Glgss","Gravel and sand","Gundumi-Illo Formation"),
("Fsh","Black shale, siltstone and sandstone","Fika Formation"),
("Ess","Sandstone","Eze-Aku Group"),
("Esh","Black shale, siltstone and sandstone","Eze-Aku Group"),
("Mlst","Limestone and Siltstone","Awi-Mfamosing Formation"),
("Awst","Sandstone","Awi-Mfamosing Formation"),
("Yls","Shale, sandy clay, calcareous sandstones","Yola-Bima-Yolde Formation"),
("Bss","Feldspathic sandstone, calcareous sandstone and shelly limestone","Bima Formation"),
("Arlsh","Shale and limestone with sandstone intercalations","Asu River Group"),
("MyP","Quartz porphyry","Younger Granite Series (Jurassic)"),
("MyG","Granite and granite porphyry","Younger Granite Series (Jurassic)"),
("MyI","Ignimbrite","Younger Granite Series (Jurassic)"),
("Mys","Syenite, quartz-syenite and gabbro","Younger Granite Series (Jurassic)"),
("MGp","Granites and granite porphyry","Younger Granite Series (Jurassic)"),
("MyP","Porphyry / quartz porphyry","Younger Granite Series (Jurassic)"),
("r","Rhyolite","Younger Granite Series (Jurassic)"),
("Jyr","Rhyolite","Younger Granite Series (Jurassic)"),
("JyG","Biotite granite","Younger Granite Series (Jurassic)"),
("JyA","Trachy-andesine","Younger Granite Series (Jurassic)"),
("P","Pegmatite","Pan-African Older Granite Series"),
("D","Dolerite","Pan-African Older Granite Series"),
("ODh","Bauchite quartz-diorite","Pan-African Older Granite Series"),
("OGd","Biotite and biotite hornblende granodiorite","Pan-African Older Granite Series"),
("OGS","Syenite, mainly of pyroxene diorite composition","Pan-African Older Granite Series"),
("OSq","Coarse biotite and biotite muscovite granite","Pan-African Older Granite Series"),
("OGh","Coarse hornblende granite","Pan-African Older Granite Series"),
("OGf","Fine-grained biotite granite","Pan-African Older Granite Series"),
("OGm","Medium- to coarse-grained biotite granite","Pan-African Older Granite Series"),
("OGu","Undifferentiated granite, migmatite and granite Gneiss","Pan-African Older Granite Series"),
("OGCh","Charnockitic rocks","Pan-African Older Granite Series"),
("OGr","Gabbro and quartz gabbro","Pan-African Older Granite Series"),
("MV","Meta Volcanic Meta Sedimentary including pebbly schist","Meta-Sedimentary / Meta-Volcanic Series"),
("Sa","Amphibole Schist, Amphibolite","Meta-Sedimentary / Meta-Volcanic Series"),
("BIF","Banded Iron Formation","Meta-Sedimentary / Meta-Volcanic Series"),
("Sp","Slate phyllite and meta siltstone, locally hornfelsic / carbonaceous","Meta-Sedimentary / Meta-Volcanic Series"),
("m","Marble","Meta-Sedimentary / Meta-Volcanic Series"),
("Sf","Fine-grained flaggy quartzite and Quartz Schist","Meta-Sedimentary / Meta-Volcanic Series"),
("Qs","Quartzite, massive and schistose, also occurring as ridges","Meta-Sedimentary / Meta-Volcanic Series"),
("MS","Pelitic Schist / Muscovite Schist","Meta-Sedimentary / Meta-Volcanic Series"),
("Su","Undifferentiated schists, including phyllites","Meta-Sedimentary / Meta-Volcanic Series"),
("Mc","Meta-conglomerate","Meta-Sedimentary / Meta-Volcanic Series"),
("bS","Biotite Garnet Gneiss Schist","Migmatite-Gneiss Complex"),
("bG-h","Biotite hornblende gneiss","Migmatite-Gneiss Complex"),
("OPg","Porphroblastic Gneiss","Migmatite-Gneiss Complex"),
("GG","Granite Gneiss","Migmatite-Gneiss Complex"),
("Ge","Granulite and gneiss","Migmatite-Gneiss Complex"),
("bG","Banded gneiss / biotite gneiss","Migmatite-Gneiss Complex"),
("MaG","Migmatitic augen gneiss","Migmatite-Gneiss Complex"),
("MG","Migmatitic gneiss","Migmatite-Gneiss Complex"),
("M","Migmatite","Migmatite-Gneiss Complex"),
("qs","Silicified, sheared rocks, large quartz veins","Cataclastic Rocks"),
("My","Mylonites","Cataclastic Rocks"),
("aMy","Mylonites interlayered with amphibolites","Cataclastic Rocks"),
]
print(f"legend rows transcribed: {len(LEGEND)}")

iso = cv2.imread("NGSA_map_geology_legend_isolated.png")  # BGR
H,W = iso.shape[:2]
iso_rgb = cv2.cvtColor(iso, cv2.COLOR_BGR2RGB)
# Find swatch column: search x in [0.80W,0.92W] for vertical band with many saturated pixels
hsv = cv2.cvtColor(iso, cv2.COLOR_BGR2HSV)
sat = hsv[:,:,1]
x_lo, x_hi = int(W*0.80), int(W*0.93)
colscore = (sat[:, x_lo:x_hi]>60).sum(axis=0)
# swatches are ~50px wide blocks; find contiguous high-score run
print("colscore top xs:", [(int(x_lo+i), int(colscore[i])) for i in np.argsort(-colscore)[:8]])
# choose band around max
cx = x_lo+int(np.argmax(colscore))
band = iso_rgb[:, max(0,cx-35):cx+35]
band_sat = sat[:, max(0,cx-35):cx+35]
print(f"swatch centre x~{cx} band width {band.shape[1]}")
# Row profile: fraction saturated in band per row; swatch rows high, gaps (white+code text) lower. Code text inside swatch reduces centre; use edges of band? Use median colour per detected segment.
rowfrac = (band_sat>50).mean(axis=1)
# segments where rowfrac>0.35
segs=[]; in_seg=False; start=0
for y in range(H):
    if rowfrac[y]>0.35 and not in_seg: in_seg=True; start=y
    if (rowfrac[y]<=0.35 or y==H-1) and in_seg:
        in_seg=False
        if y-start>=10: segs.append((start,y-1))
print(f"detected swatch segments: {len(segs)}")
for i,s in enumerate(segs[:5]): print(i,s)
print("...")
for i,s in enumerate(segs[-3:], start=len(segs)-3): print(i,s)
# Sample median saturated colour per segment (exclude black text: value dark; exclude white)
seg_rgb=[]
for (y0,y1) in segs:
    sub = band[y0:y1+1].reshape(-1,3).astype(float)
    ss = band_sat[y0:y1+1].ravel()
    vv = hsv[y0:y1+1, max(0,cx-35):cx+35, 2].ravel()
    keep = (ss>40)&(vv>70)
    if keep.sum()<20: keep = ss>25
    seg_rgb.append(np.median(sub[keep],axis=0) if keep.any() else np.median(sub,axis=0))
seg_rgb=np.array(seg_rgb)
print("segment RGBs sample:\n", seg_rgb[:5].round(0))
if len(segs)!=len(LEGEND):
    print(f"WARNING segment count {len(segs)} != legend {len(LEGEND)} - will align by order with offset search / manual check needed")
# v2 palette
v2pil=Image.open("NGSA_map_geology_legend_isolated_v2.png"); pal=v2pil.getpalette()
idx=np.array(v2pil)
units=sorted([int(u) for u in np.unique(idx) if u!=0])
v2rgb=np.array([[pal[u*3],pal[u*3+1],pal[u*3+2]] for u in units],float)
def rgb2lab(rgb):
    # use cv2 on uint8 image blocks
    im = rgb.clip(0,255).astype(np.uint8).reshape(1,-1,3)
    lab = cv2.cvtColor(im, cv2.COLOR_RGB2Lab).reshape(-1,3).astype(float)
    lab[:,0]=lab[:,0]*100/255; lab[:,1]-=128; lab[:,2]-=128
    return lab
lab_leg = rgb2lab(seg_rgb); lab_v2 = rgb2lab(v2rgb)
# distance matrix v2 x legend-segments
D = np.sqrt(((lab_v2[:,None,:]-lab_leg[None,:,:])**2).sum(axis=2))
best = np.argmin(D,axis=1); bestd = D[np.arange(len(units)),best]
second = np.sort(D,axis=1)[:,1] if D.shape[1]>1 else bestd
rows=[]
print("\nUNIT -> LEGEND matches (Lab dist; margin to 2nd):")
for k,u in enumerate(units):
    li=int(best[k])
    code,lith,form = LEGEND[li] if li < len(LEGEND) else ("?","?","?")
    conf = "High" if bestd[k]<10 and (second[k]-bestd[k])>4 else ("Medium" if bestd[k]<16 else "LOW-CHECK")
    rows.append(dict(UNIT_IDX=u, CODE=code, LITHOLOGY=lith, FORMATION=form, LEG_ROW=li+1,
                     DIST=float(bestd[k]), MARGIN=float(second[k]-bestd[k]), CONF=conf,
                     V2_RGB=tuple(int(v) for v in v2rgb[k]), LEG_RGB=tuple(int(v) for v in seg_rgb[li])))
    print(f" U{u:3d} RGB{tuple(int(v) for v in v2rgb[k])} -> row{li+1:2d} {code:6s} d={bestd[k]:5.1f} margin={second[k]-bestd[k]:5.1f} {conf:9s} {lith[:52]}")
used=set(int(b) for b in best)
print(f"\nLegend rows matched: {len(used)}/{len(LEGEND)}; unmatched rows:")
for i,(code,lith,form) in enumerate(LEGEND):
    if i not in used: print(f" row{i+1} {code} {lith}")
# duplicates: legend rows matched by >1 unit
import collections
dup={k:v for k,v in collections.Counter(int(b) for b in best).items() if v>1}
print("legend rows with multiple v2 units:", {LEGEND[k][0]+f"(row{k+1})":v for k,v in dup.items()})
with open("output/04_Tables/Geology_legend_match.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["UNIT_IDX","CODE","LITHOLOGY","FORMATION","LEG_ROW","Lab_dist","margin","CONFIDENCE","V2_RGB","LEGEND_RGB"])
    for r in rows: w.writerow([r["UNIT_IDX"],r["CODE"],r["LITHOLOGY"],r["FORMATION"],r["LEG_ROW"],round(r["DIST"],2),round(r["MARGIN"],2),r["CONF"],r["V2_RGB"],r["LEG_RGB"]])
with open("output/04_Tables/Geology_legend_transcribed.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["LEG_ROW","CODE","LITHOLOGY","FORMATION","SWATCH_RGB"])
    for i,(code,lith,form) in enumerate(LEGEND):
        sr = tuple(int(v) for v in seg_rgb[i]) if i < len(seg_rgb) else ""
        w.writerow([i+1,code,lith,form,sr])
json.dump(rows, open("work/geology_legend_rows.json","w"), indent=1, default=str)
# Join to polygons + write final shapefile (truncate field names for shapefile handled by driver; rename explicitly)
gdf=gpd.read_file("work/Geology_Rocks_complete_no_names.geojson")
lookup={r["UNIT_IDX"]:r for r in rows}
gdf["CODE"]=[lookup[int(u)]["CODE"] for u in gdf["UNIT_IDX"]]
gdf["LITHOLOGY"]=[lookup[int(u)]["LITHOLOGY"] for u in gdf["UNIT_IDX"]]
gdf["FORMATION"]=[lookup[int(u)]["FORMATION"] for u in gdf["UNIT_IDX"]]
gdf["LEG_CONF"]=[lookup[int(u)]["CONF"] for u in gdf["UNIT_IDX"]]
cols=["POLY_ID","UNIT_IDX","CODE","LITHOLOGY","FORMATION","LEG_CONF","SRC","R","G","B","HEX","AREA_KM2","geometry"]
gdf=gdf[cols]
gdf.to_file("output/02_Shapefiles/Geology_Rocks.shp")
gdf.to_file("work/Geology_Rocks_FINAL.geojson", driver="GeoJSON")
print(f"\nWrote Geology_Rocks.shp ({len(gdf)} polys). Confidence counts: {gdf['LEG_CONF'].value_counts().to_dict()}")
# QML style categorized by UNIT_IDX with HEX fills
def qml():
    cats=""
    for r in rows:
        hx=f"#{r['V2_RGB'][0]:02x}{r['V2_RGB'][1]:02x}{r['V2_RGB'][2]:02x}"
        label=f"{r['CODE']} - {r['LITHOLOGY']}".replace("&","and").replace("<","").replace('"',"'")
        cats+=f'<category symbol="{r["UNIT_IDX"]}" value="{r["UNIT_IDX"]}" label="{label}"/>\n'
    syms=""
    for r in rows:
        R,G,B=r["V2_RGB"]
        syms+=f'<symbol type="fill" name="{r["UNIT_IDX"]}"><layer class="SimpleFill"><prop k="color" v="{R},{G},{B},255"/><prop k="outline_color" v="60,60,60,255"/><prop k="outline_width" v="0.1"/></layer></symbol>\n'
    return f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34"><renderer-v2 type="categorizedSymbol" attr="UNIT_IDX">
<categories>{cats}</categories><symbols>{syms}</symbols></renderer-v2></qgis>"""
open("output/02_Shapefiles/Geology_Rocks.qml","w").write(qml())
print("wrote QML")
