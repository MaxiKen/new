import numpy as np, pandas as pd, cv2, pickle, sys
sys.path.insert(0,"work")
from PIL import Image
src=open("work/build_templates_v3.py").read().split("final={}")[0]
exec(src)
bc=minr[minr.fid==1474].iloc[0]
print("fid1474 at",bc.px_x,bc.px_y)
x0,y0=int(bc.px_x)-30,int(bc.px_y)-30
win=base[y0:y0+61,x0:x0+61]
R,G,B=win[:,:,0],win[:,:,1],win[:,:,2]
purple=((R>120)&(B>120)&(G<110)&(R-G>40)).astype(np.uint8)
n,lab,stats,cents=cv2.connectedComponentsWithStats(purple,8)
seeds=[]
for k in range(1,n):
    if stats[k,4]>=12:
        seeds.append((x0+cents[k][0],y0+cents[k][1],int(stats[k,4])))
print("purple blobs:",seeds)
# zoom check image
im=Image.fromarray(win.astype(np.uint8)).resize((61*6,61*6),Image.NEAREST)
im.save("work/calcite_seed_zoom.png")
seedpts=[(s[0],s[1]) for s in seeds[:3]]
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
fin5=pickle.load(open("work/final_tpl_v5.pkl","rb"))["final"]
fin3=pickle.load(open("work/final_tpl_v3.pkl","rb"))["final"]
if len(seedpts)>=2:
    ms,cand,tag=hybrid_fit(67,seedpts)
    print(f"67 Calcite refit {ms:.3f} {tag} size {cand['tpl'].shape} seeds {seedpts}")
    fin5[67]={**fin3[67],**cand,"source":f"v5b-hybrid-purpledisc {tag}","self_med":round(ms,3)}
    pickle.dump({"final":fin5},open("work/final_tpl_v5.pkl","wb"))
    print("saved")
