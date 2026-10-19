import pandas as pd, numpy as np
from PIL import Image, ImageDraw
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
new=pd.read_csv("work/points_v5.csv"); unv=pd.read_csv("work/unverified_old_v5.csv")
regions={"JosZOOM":(980,780,1200,1000),"NWZOOM":(200,180,420,400),"SWZOOM":(350,1150,570,1370)}
for tag,(x0,y0,x1,y1) in regions.items():
    S=4
    cr=base.crop((x0,y0,x1,y1)).resize(((x1-x0)*S,(y1-y0)*S),Image.NEAREST)
    dr=ImageDraw.Draw(cr); dr.text((6,6),tag+" FINAL v5",fill=(255,0,0))
    su=unv[(unv.px_x>=x0)&(unv.px_x<x1)&(unv.px_y>=y0)&(unv.px_y<y1)]
    for _,r in su.iterrows():
        X,Y=(r.px_x-x0)*S,(r.px_y-y0)*S
        dr.line((X-6,Y-6,X+6,Y+6),fill=(120,120,120),width=2); dr.line((X-6,Y+6,X+6,Y-6),fill=(120,120,120),width=2)
    sn=new[(new.px_x>=x0)&(new.px_x<x1)&(new.px_y>=y0)&(new.px_y<y1)]
    for _,r in sn.iterrows():
        X,Y=(r.px_x-x0)*S,(r.px_y-y0)*S
        col=(255,0,0) if r.det_src=='SCAN_COMPLETE' else ((255,140,0) if 'RESCUE' in r.det_src else (200,0,200))
        dr.ellipse((X-9,Y-9,X+9,Y+9),outline=col,width=2)
        dr.text((X+10,Y-6),str(int(r.leg_no)),fill=(200,0,0))
    cr.save(f"corrected_delivery/QA_maps_and_reports/QA_minerals_{tag}_final.png")
    print(tag,len(sn))
