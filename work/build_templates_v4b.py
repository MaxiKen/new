import numpy as np, pandas as pd, cv2, pickle, sys
sys.path.insert(0,"work")
from PIL import Image, ImageDraw
src=open("work/build_templates_v3.py").read().split("final={}")[0]
exec(src)
fin4=pickle.load(open("work/final_tpl_v4.pkl","rb"))["final"]
extra=minr[~minr.leg_no.isin(dedup.leg_no.unique())]
pool=pd.concat([dedup,extra],ignore_index=True)
def pts_of(no,n=12):
    s=pool[pool.leg_no==no].sort_values('fid').head(n)
    return [(float(r.px_x),float(r.px_y)) for _,r in s.iterrows()]
def hybrid_fit(no,seedpts,trim=0.60):
    tpl0,foot0=legt[no]; best=None
    for sxp in np.arange(0.60,1.05,0.04):
        for syp in np.arange(0.68,1.05,0.04):
            sx=sxp/(300/72); sy=syp/(300/72)
            nw=max(3,int(round(tpl0.shape[1]*sx))); nh=max(3,int(round(tpl0.shape[0]*sy)))
            t=cv2.resize(tpl0,(nw,nh),interpolation=cv2.INTER_AREA)
            f=cv2.resize(foot0.astype(np.float32),(nw,nh),interpolation=cv2.INTER_AREA)>0.35
            rc=recentre(t,f)
            if rc is None: continue
            canvas,cm,frac=rc
            if not sane(cm): continue
            cand={"tpl":canvas,"mask":cm,"frac":frac}
            ms=float(np.median(eval_at_points(cand,seedpts,search=4)))
            if best is None or ms>best[0]: best=(ms,cand,sxp,syp)
    if best is None: return None
    ms,cand,sxp,syp=best
    canvas=cand["tpl"].astype(np.float32); cm=cand["mask"]
    tf=cv2.GaussianBlur(canvas,(3,3),0.7)
    hx=(canvas.shape[1]-1)//2; hy=(canvas.shape[0]-1)//2
    crops=[]; 
    for (x,y) in seedpts:
        bb=-1; bw=None
        for dy in range(-4,5):
            for dx in range(-4,5):
                w=rectwin(x+dx,y+dy,hx,hy)
                s=masked_ncc(cv2.GaussianBlur(w,(3,3),0.7),tf,cm)
                if s>bb: bb=s; bw=w
        if bw is not None and bb>=trim: crops.append(bw)
    if len(crops)>=2:
        med=np.median(np.array(crops),axis=0)
        newtpl=canvas.copy(); newtpl[cm]=med[cm]
        cand={"tpl":newtpl.astype(np.uint8),"mask":cm,"frac":cand["frac"]}
    scs=eval_at_points(cand,seedpts,search=4)
    hi=[s for s in scs if s>=trim]
    return cand, (float(np.median(hi)) if hi else float(np.median(scs))), len(crops), f"sx={sxp:.2f} sy={syp:.2f}"
patched=[]
for no in [4,11,23,28,37,51,63,64,66]:
    sp=pts_of(no)
    out=hybrid_fit(no,sp)
    if out is None: print(no,"hybrid failed"); continue
    cand,ms,nc,tag=out
    scs_old=eval_at_points({"tpl":fin4[no]["tpl"],"mask":fin4[no]["mask"]},sp,search=4)
    scs_new=eval_at_points(cand,sp,search=4)
    # compare on subset where EITHER scores >=0.6 (likely-true points)
    idx=[i for i in range(len(sp)) if scs_new[i]>=0.6 or scs_old[i]>=0.6]
    mnew=float(np.median([scs_new[i] for i in idx])) if idx else -1
    mold=float(np.median([scs_old[i] for i in idx])) if idx else -1
    print(f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:14]} hybrid on trueish({len(idx)}) {mnew:.3f} vs old {mold:.3f} colourcrops={nc} {tag} size {cand['tpl'].shape}")
    if idx and mnew>=mold-0.02:
        fin4[no]={**fin4[no],**cand,"source":f"v4b-hybrid {tag}","self_med":round(mnew,3)}
        patched.append(no)
pickle.dump({"final":fin4},open("work/final_tpl_v4.pkl","wb"))
print("v4b patched:",patched)
# sheet for v4b
cols=5; s=140; rowsn=int(np.ceil(len(patched)/cols)) or 1
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255)); dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(patched):
    x=(idx%cols)*s; y=(idx//cols)*s; f=fin4[no]
    dr.text((x+4,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:15]}",fill=(200,0,0))
    t=f['tpl']; sheet.paste(Image.fromarray(t.astype(np.uint8)).resize((t.shape[1]*4,t.shape[0]*4),Image.NEAREST),(x+4,y+16))
    dr.text((x+4,y+s-14),f"med={f.get('self_med')}",fill=(0,120,0))
sheet.save("work/patched_templates_sheet_v4b.png"); print("sheet saved")
