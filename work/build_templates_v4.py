import numpy as np, pandas as pd, cv2, pickle, sys
sys.path.insert(0,"work")
from PIL import Image, ImageDraw
src=open("work/build_templates_v3.py").read().split("final={}")[0]
exec(src)  # defines base,H,W,legt,leg,minr,dedup, helpers, build_exemplar, eval_at_points, legend_scaled
from transforms import min_lonlat_to_basepx
import geopandas as gpd
fin3=pickle.load(open("work/final_tpl_v3.pkl","rb"))["final"]
extra=minr[~minr.leg_no.isin(dedup.leg_no.unique())]
pool=pd.concat([dedup,extra],ignore_index=True)
def pts_of(no): 
    s=pool[pool.leg_no==no].sort_values('fid')
    return [(float(r.px_x),float(r.px_y)) for _,r in s.iterrows()]
def med_score(cand,pts):
    if not pts: return -1
    return float(np.median(eval_at_points(cand,pts)))
patched={}
# A: trimmed exemplar rebuild
for no in [4,11,23,28,29,30,34,37,47,51,58,63,64,65,66]:
    sub=pool[pool.leg_no==no].sort_values('fid')
    if len(sub)<4: continue
    pref=sub[sub.nn>15] if 'nn' in sub else sub
    use=pref.head(40) if len(pref)>=5 else sub.head(40)
    ex=build_exemplar([r for _,r in use.iterrows()])
    if ex is None: print(no,"exemplar build failed"); continue
    allpts=pts_of(no)
    scs=eval_at_points(ex,allpts)
    kept=[p for p,s in zip(allpts,scs) if s>=0.62]
    candtpl=ex; tag="exemplar"
    if len(kept)>=4:
        rows=[]
        for (x,y) in kept:
            rows.append(pd.Series(dict(px_x=x,px_y=y)))
        ex2=build_exemplar(rows)
        if ex2 is not None: candtpl=ex2; tag="exemplar-trimmed"
    evalset=kept if len(kept)>=3 else allpts
    ms_new=med_score(candtpl,evalset); ms_old=med_score({"tpl":fin3[no]["tpl"],"mask":fin3[no]["mask"]},evalset)
    print(f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:14]} kept {len(kept)}/{len(allpts)} new {ms_new:.3f} old {ms_old:.3f} ({tag}) size {candtpl['tpl'].shape}")
    if ms_new>=ms_old-0.02:
        patched[no]={**candtpl,"source":f"v4-{tag}","self_med":round(ms_new,3)}
# B: hybrid legend-shape + fitted scale + map colours from 1-3 old points
def hybrid_fit(no,seedpts):
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
            scs=eval_at_points(cand,seedpts,search=4)
            ms=float(np.median(scs))
            if best is None or ms>best[0]: best=(ms,cand,sxp,syp)
    if best is None: return None
    ms,cand,sxp,syp=best
    # colour-adapt: median of aligned crops within footprint
    canvas=cand["tpl"].astype(np.float32); cm=cand["mask"]
    tf=cv2.GaussianBlur(canvas,(3,3),0.7)
    hx=(canvas.shape[1]-1)//2; hy=(canvas.shape[0]-1)//2
    crops=[]
    for (x,y) in seedpts:
        bb=-1; bw=None
        for dy in range(-4,5):
            for dx in range(-4,5):
                w=rectwin(x+dx,y+dy,hx,hy)
                s=masked_ncc(cv2.GaussianBlur(w,(3,3),0.7),tf,cm)
                if s>bb: bb=s; bw=w
        if bw is not None and bb>=0.45: crops.append(bw)
    if crops:
        med=np.median(np.array(crops),axis=0)
        newtpl=canvas.copy(); newtpl[cm]=med[cm]
        cand={"tpl":newtpl.astype(np.uint8),"mask":cm,"frac":cand["frac"]}
        ms=float(np.median(eval_at_points(cand,seedpts,search=4)))
    return ms,cand,f"sx={sxp:.2f} sy={syp:.2f} colour-adapted={bool(crops)}"
for no in [2,7,9,16,18,19,21,22,42,46,49,54,55,59,60,62,67]:
    sp=pts_of(no)[:3]
    if not sp: print(no,"no seed points"); continue
    out=hybrid_fit(no,sp)
    if out is None: continue
    ms,cand,tag=out
    ms_old=float(np.median(eval_at_points({"tpl":fin3[no]["tpl"],"mask":fin3[no]["mask"]},sp,search=4)))
    print(f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:14]} hybrid {ms:.3f} old {ms_old:.3f} {tag} size {cand['tpl'].shape}")
    if ms>=ms_old-0.02: patched[no]={**cand,"source":f"v4-hybrid {tag}","self_med":round(ms,3)}
# Nickel seeded
out=hybrid_fit(48,[(925.7,1550.3),(935.5,1550.3),(935.4,1442.7)])
if out:
    ms,cand,tag=out; print(f"48 Nickel hybrid {ms:.3f} {tag} size {cand['tpl'].shape}")
    patched[48]={**cand,"source":f"v4-hybrid-nickelseed {tag}","self_med":round(ms,3)}
fin4=dict(fin3)
for k,v in patched.items(): fin4[k]={**fin3[k],**v}
pickle.dump({"final":fin4},open("work/final_tpl_v4.pkl","wb"))
# sheet of patched templates
keys=sorted(patched); cols=6; s=130; rowsn=int(np.ceil(len(keys)/cols)) or 1
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255)); dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(keys):
    x=(idx%cols)*s; y=(idx//cols)*s; f=patched[no]
    dr.text((x+4,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:15]}",fill=(200,0,0))
    t=f['tpl']; sheet.paste(Image.fromarray(t.astype(np.uint8)).resize((t.shape[1]*4,t.shape[0]*4),Image.NEAREST),(x+4,y+16))
    dr.text((x+4,y+s-14),f"med={f.get('self_med')}",fill=(0,120,0))
sheet.save("work/patched_templates_sheet.png")
print("patched classes:",keys)
# asbestos zoom sheet top8
cand=pd.read_csv("work/scan_candidates2.csv")
cc=cand[(cand.leg_no==1)&(cand.dmean<=42)].sort_values('score',ascending=False).head(8)
baseim=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
im=Image.new("RGB",(4*170,2*170),(255,255,255)); dr=ImageDraw.Draw(im)
for i,(_,r) in enumerate(cc.iterrows()):
    x,y=int(r.px_x),int(r.px_y)
    cr=baseim.crop((x-16,y-16,x+17,y+17)).resize((165,165),Image.NEAREST)
    d2=ImageDraw.Draw(cr); d2.ellipse((74,74,90,90),outline=(255,0,0))
    im.paste(cr,((i%4)*170,(i//4)*170)); dr.text(((i%4)*170+4,(i//4)*170+4),f"#{i} {r.score:.2f} ({x},{y})",fill=(255,0,0))
im.save("work/asbestos_top8.png"); print("asbestos sheet saved")
