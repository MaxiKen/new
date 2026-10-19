import numpy as np, pandas as pd, geopandas as gpd
from PIL import Image, ImageDraw
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
new=pd.read_csv("work/points_v3.csv"); unv=pd.read_csv("work/unverified_old_v3.csv")
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv").set_index('legend_no')
# A: zoom audits
regions={"JosZOOM":(980,780,1200,1000),"NWZOOM":(200,180,420,400),"SWZOOM":(350,1150,570,1370)}
for tag,(x0,y0,x1,y1) in regions.items():
    S=4
    cr=base.crop((x0,y0,x1,y1)).resize(((x1-x0)*S,(y1-y0)*S),Image.NEAREST)
    dr=ImageDraw.Draw(cr); dr.text((6,6),tag,fill=(255,0,0))
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
    cr.save(f"work/qa3_{tag}.png"); print(tag,"new",len(sn),"unv",len(su))
# B: per-class lowest-score accepted sheets, 5 combined images
cell=88; cols=8; per=16
classes=list(range(1,68))
for part in range(5):
    subset=classes[part*14:(part+1)*14]
    im=Image.new("RGB",(cols*cell,len(subset)*(2*cell+16)),(255,255,255)); dr=ImageDraw.Draw(im)
    for ri,no in enumerate(subset):
        y0=ri*(2*cell+16)
        sub=new[new.leg_no==no].copy()
        dr.text((4,y0+3),f"{no} {leg.loc[no,'point_attribute_name']} n={len(sub)} (lowest scores first)",fill=(200,0,0))
        sub['srt']=sub.score.fillna(-1)
        sub=sub.sort_values('srt').head(per)
        for i,(_,r) in enumerate(sub.iterrows()):
            x,y=int(r.px_x),int(r.px_y)
            cr=base.crop((x-12,y-12,x+13,y+13)).resize((cell-4,cell-4),Image.NEAREST)
            d2=ImageDraw.Draw(cr); d2.ellipse((cell//2-8,cell//2-8,cell//2+4,cell//2+4),outline=(255,0,0))
            X=(i%cols)*cell; Y=y0+16+(i//cols)*cell
            im.paste(cr,(X,Y)); dr.text((X+3,Y+3),(f"{r.score:.2f}" if pd.notna(r.score) else "old"),fill=(255,0,0))
    im.save(f"work/qa3_classes_part{part}.png"); print("part",part,"saved")
# C: unverified crops sample
sel=unv.sort_values(['leg_no','fid']).groupby('leg_no').head(4).head(48)
cell=110; cols=8; rows=int(np.ceil(len(sel)/cols))
im=Image.new("RGB",(cols*cell,rows*cell),(255,255,255)); dr=ImageDraw.Draw(im)
for i,(_,r) in enumerate(sel.iterrows()):
    x,y=int(r.px_x),int(r.px_y)
    cr=base.crop((x-13,y-13,x+14,y+14)).resize((cell-4,cell-4),Image.NEAREST)
    d2=ImageDraw.Draw(cr); d2.ellipse((cell//2-9,cell//2-9,cell//2+5,cell//2+5),outline=(255,0,0))
    X=(i%cols)*cell; Y=(i//cols)*cell
    im.paste(cr,(X,Y)); dr.text((X+3,Y+3),f"L{int(r.leg_no)} f{int(r.fid)}",fill=(255,0,0))
im.save("work/qa3_unverified_sample.png"); print("unv sheet",len(sel))
