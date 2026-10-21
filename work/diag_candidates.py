import numpy as np, pandas as pd
from PIL import Image, ImageDraw
cand=pd.read_csv("work/scan_candidates.csv")
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
def sheet(no,n=16,title=""):
    sub=cand[cand.leg_no==no].sort_values('score',ascending=False)
    # simple NMS 8px
    acc=[]
    for _,r in sub.iterrows():
        if all((r.px_x-a[0])**2+(r.px_y-a[1])**2>64 for a in acc): acc.append((r.px_x,r.px_y,r.score))
        if len(acc)>=n: break
    im=Image.new("RGB",(8*110,((n+7)//8)*110),(255,255,255)); dr=ImageDraw.Draw(im)
    for i,(x,y,s) in enumerate(acc):
        cr=base.crop((int(x)-13,int(y)-13,int(x)+14,int(y)+14)).resize((108,108),Image.NEAREST)
        d2=ImageDraw.Draw(cr); d2.ellipse((48,48,60,60),outline=(255,0,0))
        im.paste(cr,((i%8)*110,(i//8)*110)); dr.text(((i%8)*110+3,(i//8)*110+3),f"{title} {s:.2f}",fill=(255,0,0))
    im.save(f"work/diag_top_{no}.png")
for no,t in [(17,"Diatomite"),(45,"Magnesite"),(6,"Beryl"),(3,"Baryte"),(59,"TarSand"),(34,"Kaolin")]:
    sheet(no,title=t)
print("done")
