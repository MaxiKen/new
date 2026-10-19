import numpy as np, pandas as pd, geopandas as gpd
from PIL import Image, ImageDraw
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
new=pd.read_csv("work/points_v2.csv")
old=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
regions={"NW":(150,120,520,470),"Jos":(900,700,1270,1050),"SE":(1250,1150,1620,1500),"SW":(250,1050,620,1400)}
for tag,(x0,y0,x1,y1) in regions.items():
    cr=base.crop((x0,y0,x1,y1)).resize(((x1-x0)*2,(y1-y0)*2),Image.NEAREST)
    dr=ImageDraw.Draw(cr)
    sub=old[(old.px_x>=x0)&(old.px_x<x1)&(old.px_y>=y0)&(old.px_y<y1)]
    for _,r in sub.iterrows():
        X,Y=(r.px_x-x0)*2,(r.px_y-y0)*2; dr.ellipse((X-3,Y-3,X+3,Y+3),outline=(150,150,150))
    sn=new[(new.px_x>=x0)&(new.px_x<x1)&(new.px_y>=y0)&(new.px_y<y1)]
    for _,r in sn.iterrows():
        X,Y=(r.px_x-x0)*2,(r.px_y-y0)*2
        col=(255,0,0) if r.det_src=='SCAN_COMPLETE' else (255,140,0)
        dr.ellipse((X-5,Y-5,X+5,Y+5),outline=col,width=2)
        dr.text((X+6,Y-6),str(int(r.leg_no)),fill=(200,0,0))
    cr.save(f"work/qa_pilot_{tag}.png")
    print(tag,"new",len(sn),"old",len(sub))
