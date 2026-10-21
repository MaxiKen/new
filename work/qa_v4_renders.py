import numpy as np, pandas as pd
from PIL import Image, ImageDraw
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
new=pd.read_csv("work/points_v4.csv")
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv").set_index('legend_no')
cell=92; cols=8
classes=[11,18,22,28,37]
im=Image.new("RGB",(cols*cell,len(classes)*(2*cell+16)),(255,255,255)); dr=ImageDraw.Draw(im)
for ri,no in enumerate(classes):
    y0=ri*(2*cell+16); sub=new[new.leg_no==no].copy()
    dr.text((4,y0+3),f"{no} {leg.loc[no,'point_attribute_name']} n={len(sub)} lowest first",fill=(200,0,0))
    sub['srt']=sub.score.fillna(-1); sub=sub.sort_values('srt').head(16)
    for i,(_,r) in enumerate(sub.iterrows()):
        x,y=int(r.px_x),int(r.px_y)
        cr=base.crop((x-12,y-12,x+13,y+13)).resize((cell-4,cell-4),Image.NEAREST)
        d2=ImageDraw.Draw(cr); d2.ellipse((cell//2-8,cell//2-8,cell//2+4,cell//2+4),outline=(255,0,0))
        X=(i%cols)*cell; Y=y0+16+(i//cols)*cell
        im.paste(cr,(X,Y)); dr.text((X+3,Y+3),(f"{r.score:.2f}" if pd.notna(r.score) else "old"),fill=(255,0,0))
im.save("work/qa4_changed_classes.png")
wl=new[new.det_src.str.contains('WHITELIST|MANUAL')].reset_index(drop=True)
rows=int(np.ceil(len(wl)/cols))
im=Image.new("RGB",(cols*cell,rows*cell+16),(255,255,255)); dr=ImageDraw.Draw(im)
dr.text((4,3),f"WHITELIST + MANUAL points n={len(wl)}",fill=(200,0,0))
for i,r in wl.iterrows():
    x,y=int(r.px_x),int(r.px_y)
    cr=base.crop((x-12,y-12,x+13,y+13)).resize((cell-4,cell-4),Image.NEAREST)
    d2=ImageDraw.Draw(cr); d2.ellipse((cell//2-8,cell//2-8,cell//2+4,cell//2+4),outline=(255,0,0))
    X=(i%cols)*cell; Y=16+(i//cols)*cell
    im.paste(cr,(X,Y)); dr.text((X+3,Y+3),f"L{int(r.leg_no)}",fill=(255,0,0))
im.save("work/qa4_whitelist.png"); print("saved", len(wl))
