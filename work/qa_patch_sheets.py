import numpy as np, pandas as pd
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
cand=pd.read_csv("work/scan_candidates4.csv"); pts=pd.read_csv("work/points_v3.csv"); unv=pd.read_csv("work/unverified_old_v3.csv")
cell=96; cols=8
def sheet(df,title,fn,per=24):
    rows=int(np.ceil(min(per,len(df))/cols)) or 1
    im=Image.new("RGB",(cols*cell,rows*cell+16),(255,255,255)); dr=ImageDraw.Draw(im)
    dr.text((4,3),title,fill=(200,0,0))
    for i,(_,r) in enumerate(df.head(per).iterrows()):
        x,y=int(r.px_x),int(r.px_y)
        cr=base.crop((x-12,y-12,x+13,y+13)).resize((cell-4,cell-4),Image.NEAREST)
        d2=ImageDraw.Draw(cr); d2.ellipse((cell//2-8,cell//2-8,cell//2+4,cell//2+4),outline=(255,0,0))
        X=(i%cols)*cell; Y=16+(i//cols)*cell
        im.paste(cr,(X,Y)); dr.text((X+3,Y+3),r['tag'],fill=(255,0,0))
    im.save(fn); print(fn)
for no,ttl in [(22,'22 Fluorite NEW hybrid top gated dmean<=40'),(28,'28 RiverGravel NEW hybrid top gated dmean<=40')]:
    cc=cand[(cand.leg_no==no)&(cand.dmean<=40)].sort_values('score',ascending=False)
    acc=[]
    for _,r in cc.iterrows():
        if all((r.px_x-a.px_x)**2+(r.px_y-a.px_y)**2>64 for a in acc): acc.append(r)
        if len(acc)>=24: break
    df=pd.DataFrame(acc); df['tag']=[f"{s:.2f}" for s in df.score]
    sheet(df,ttl,f"work/qa_patch_{no}.png")
t=cKDTree(pts[['px_x','px_y']].values); d,_=t.query(unv[['px_x','px_y']].values)
far=unv[d>12].copy()
print("far unverified:",len(far))
print(far.groupby(['leg_no','mineral']).size().to_string())
sel=far.sort_values(['leg_no','fid']).groupby('leg_no').head(3).head(24)
sel=sel.copy(); sel['tag']=[f"L{int(a)} f{int(b)}" for a,b in zip(sel.leg_no,sel.fid)]
sheet(sel,'Unverified old points with NO new point within 12px (sample)','work/qa_patch_farmiss.png')
far.to_csv("work/unverified_far_v3.csv",index=False)
