import numpy as np, pandas as pd
from PIL import Image, ImageDraw
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
cand=pd.read_csv("work/scan_candidates2.csv")
classes=[(48,'48 Nickel'),(1,'1 Asbestos'),(56,'56 Silver'),(8,'8 Bitumen'),(62,'62 Trona'),(22,'22 Fluorite')]
cell=96; cols=8; per=16
im=Image.new("RGB",(cols*cell, len(classes)*(2*cell+16)),(255,255,255)); dr=ImageDraw.Draw(im)
for ri,(no,title) in enumerate(classes):
    y0=ri*(2*cell+16)
    dr.text((4,y0+3),title+"  (top gated dmean<=42, by score)",fill=(200,0,0))
    cc=cand[(cand.leg_no==no)&(cand.dmean<=42)].sort_values('score',ascending=False)
    acc=[]
    for _,r in cc.iterrows():
        if all((r.px_x-a.px_x)**2+(r.px_y-a.px_y)**2>64 for a in acc): acc.append(r)
        if len(acc)>=per: break
    for i,r in enumerate(acc):
        x,y=int(r.px_x),int(r.px_y)
        cr=base.crop((x-12,y-12,x+13,y+13)).resize((cell-4,cell-4),Image.NEAREST)
        d2=ImageDraw.Draw(cr); d2.ellipse((cell//2-8,cell//2-8,cell//2+4,cell//2+4),outline=(255,0,0))
        X=(i%cols)*cell; Y=y0+16+(i//cols)*cell
        im.paste(cr,(X,Y)); dr.text((X+3,Y+3),f"{r.score:.2f}",fill=(255,0,0))
im.save("work/qa_missing2.png"); print("saved")
# identify long black bars: context crop around a Tar Sand top candidate
cc=cand[cand.leg_no==59].sort_values('score',ascending=False).iloc[0]
x,y=int(cc.px_x),int(cc.px_y)
base.crop((x-60,y-30,x+61,y+31)).resize((484,244),Image.NEAREST).save("work/blackbar_context.png")
print("bar at",x,y)
