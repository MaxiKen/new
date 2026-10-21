import numpy as np, pandas as pd
from PIL import Image, ImageDraw
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
new=pd.read_csv("work/points_v2.csv"); cand=pd.read_csv("work/scan_candidates2.csv")
def sheet_pts(df,tag,n=24):
    df=df.head(n)
    cols=8; rows=max(1,int(np.ceil(len(df)/cols)))
    im=Image.new("RGB",(cols*110,rows*110),(255,255,255)); dr=ImageDraw.Draw(im)
    for i,(_,r) in enumerate(df.iterrows()):
        x,y=int(r.px_x),int(r.px_y)
        cr=base.crop((x-13,y-13,x+14,y+14)).resize((108,108),Image.NEAREST)
        d2=ImageDraw.Draw(cr); d2.ellipse((48,48,60,60),outline=(255,0,0))
        im.paste(cr,((i%cols)*110,(i//cols)*110))
        s=f"{r.score:.2f}" if pd.notna(r.score) else "old"
        dr.text(((i%cols)*110+3,(i//cols)*110+3),s,fill=(255,0,0))
    im.save(f"work/qa_sheet_{tag}.png")
# accepted points for suspicious classes
for no,tag in [(3,'baryte_acc'),(4,'bauxitic_acc'),(11,'chromite_acc'),(16,'corundum_acc'),(52,'roseq_acc'),(30,'granite_acc'),(59,'tarsand_acc'),(47,'monazite_acc')]:
    sub=new[new.leg_no==no].sort_values('score')
    sheet_pts(sub,tag)
# top candidates for missing classes (NMS 8px by score)
for no,tag in [(9,'brickclay_cand'),(15,'copper_cand'),(19,'evaporite_cand'),(22,'fluorite_cand'),(50,'psammite_cand'),(8,'bitumen_cand'),(48,'nickel_cand'),(56,'silver_cand'),(1,'asbestos_cand'),(62,'Trona_cand')]:
    cc=cand[cand.leg_no==no].sort_values('score',ascending=False)
    acc=[]
    for _,r in cc.iterrows():
        if all((r.px_x-a.px_x)**2+(r.px_y-a.px_y)**2>64 for a in acc): acc.append(r)
        if len(acc)>=24: break
    sheet_pts(pd.DataFrame(acc),tag)
print("sheets done")
