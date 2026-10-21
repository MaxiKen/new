import pymupdf, numpy as np, pandas as pd, geopandas as gpd, json, re
from PIL import Image, ImageDraw
import warnings; warnings.filterwarnings('ignore')
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'); p=d[0]
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
print(leg[['legend_no','map_legend_category']].to_string())
# Legend label positions (x ~2111)
td=p.get_text("dict"); rows=[]
for bl in td["blocks"]:
    if bl["type"]!=0: continue
    for ln in bl["lines"]:
        s="".join(sp["text"] for sp in ln["spans"]).strip()
        x0,y0,x1,y1=ln["bbox"]
        if 2110<x0<2115 and s: rows.append((y0,y1,s))
rows.sort()
print(f"\nlegend label rows found: {len(rows)}")
for r in rows: print([round(r[0],1),round(r[1],1),r[2]])
# Render symbol column at 300dpi: clip x 2082..2114, y 325..1400
zoom=300/72
clip=pymupdf.Rect(2082,325,2114,1410)
pix=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom),clip=clip)
pix.save("work/legend_symbols_300dpi.png")
print("legend col render",pix.width,pix.height)
np.save("work/legend_rows.npy", np.array([(r[0],r[1]) for r in rows]))
with open("work/legend_rows.json","w") as f: json.dump(rows,f)
