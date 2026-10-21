import numpy as np, pandas as pd, cv2, pickle, sys
sys.path.insert(0,"work")
src=open("work/build_templates_v3.py").read().split("final={}")[0]
exec(src)
fin3=pickle.load(open("work/final_tpl_v3.pkl","rb"))["final"]
fin4=pickle.load(open("work/final_tpl_v4.pkl","rb"))["final"]
extra=minr[~minr.leg_no.isin(dedup.leg_no.unique())]
pool=pd.concat([dedup,extra],ignore_index=True)
def hybrid_fit(no,seedpts,trim=0.45):
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
    ms,cand,sxp,syp=best
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
        if bw is not None and bb>=trim: crops.append(bw)
    if crops:
        med=np.median(np.array(crops),axis=0)
        newtpl=canvas.copy(); newtpl[cm]=med[cm]
        cand={"tpl":newtpl.astype(np.uint8),"mask":cm,"frac":cand["frac"]}
        ms=float(np.median(eval_at_points(cand,seedpts,search=4)))
    return ms,cand,f"sx={sxp:.2f} sy={syp:.2f} crops={len(crops)} precolour_ms={best[0]:.3f}"
fin5=dict(fin4)
# reverts to v3 templates
for no in [9,16,19,21,22,42,59,60]:
    fin5[no]=fin3[no]
print("reverted to v3:",[9,16,19,21,22,42,59,60])
# Copper seeded at old Calcite points (blue triangles)
seeds=[(float(r.px_x),float(r.px_y)) for _,r in minr[minr.leg_no==67].iterrows()]
ms,cand,tag=hybrid_fit(15,seeds)
print(f"15 Copper hybrid {ms:.3f} {tag} size {cand['tpl'].shape}")
fin5[15]={**fin3[15],**cand,"source":f"v5-hybrid-copperseed {tag}","self_med":round(ms,3)}
# Calcite seeds: v3-template candidates (candidates2) near Brick Clay fid1474
cand2=pd.read_csv("work/scan_candidates2.csv")
bc=minr[minr.fid==1474].iloc[0]
near=cand2[(cand2.leg_no==67)&(np.hypot(cand2.px_x-bc.px_x,cand2.px_y-bc.px_y)<=20)].sort_values('score',ascending=False)
print("calcite seed cands near fid1474:\n",near.head(6).to_string(index=False))
seeds67=[(float(r.px_x),float(r.px_y)) for _,r in near.head(3).iterrows()]
if seeds67:
    ms,cand,tag=hybrid_fit(67,seeds67)
    print(f"67 Calcite hybrid {ms:.3f} {tag} size {cand['tpl'].shape}")
    fin5[67]={**fin3[67],**cand,"source":f"v5-hybrid-discseed {tag}","self_med":round(ms,3)}
# Monazite hybrid attempt
seeds47=[(float(r.px_x),float(r.px_y)) for _,r in pool[pool.leg_no==47].sort_values('fid').iterrows()]
ms,cand,tag=hybrid_fit(47,seeds47)
ms_old=float(np.median(eval_at_points({"tpl":fin3[47]["tpl"],"mask":fin3[47]["mask"]},seeds47,search=4)))
print(f"47 Monazite hybrid {ms:.3f} vs v3 {ms_old:.3f} {tag}")
if ms>=ms_old: fin5[47]={**fin3[47],**cand,"source":f"v5-hybrid {tag}","self_med":round(ms,3)}
pickle.dump({"final":fin5},open("work/final_tpl_v5.pkl","wb"))
print("fin5 saved")
