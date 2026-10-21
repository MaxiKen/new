import numpy as np, pandas as pd, cv2, pickle, sys
sys.path.insert(0,"work")
from PIL import Image
src=open("work/build_templates_v3.py").read().split("final={}")[0]
exec(src)
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
            ms=float(np.median(eval_at_points(cand,seedpts,search=3)))
            if best is None or ms>best[0]: best=(ms,cand,sxp,syp)
    ms,cand,sxp,syp=best
    canvas=cand["tpl"].astype(np.float32); cm=cand["mask"]
    tf=cv2.GaussianBlur(canvas,(3,3),0.7)
    hx=(canvas.shape[1]-1)//2; hy=(canvas.shape[0]-1)//2
    crops=[]
    for (x,y) in seedpts:
        bb=-1; bw=None
        for dy in range(-3,4):
            for dx in range(-3,4):
                w=rectwin(x+dx,y+dy,hx,hy)
                s=masked_ncc(cv2.GaussianBlur(w,(3,3),0.7),tf,cm)
                if s>bb: bb=s; bw=w
        if bw is not None and bb>=trim: crops.append(bw)
    if crops:
        med=np.median(np.array(crops),axis=0)
        newtpl=canvas.copy(); newtpl[cm]=med[cm]
        cand={"tpl":newtpl.astype(np.uint8),"mask":cm,"frac":cand["frac"]}
        ms=float(np.median(eval_at_points(cand,seedpts,search=3)))
    return ms,cand,f"sx={sxp:.2f} sy={syp:.2f} crops={len(crops)} precolour_ms={best[0]:.3f}"
fin5=pickle.load(open("work/final_tpl_v5.pkl","rb"))["final"]
fin3=pickle.load(open("work/final_tpl_v3.pkl","rb"))["final"]
ms,cand,tag=hybrid_fit(67,[(1498.7,821.9),(1499.7,833.0)])
print(f"67 Calcite refit2 {ms:.3f} {tag} size {cand['tpl'].shape}")
fin5[67]={**fin3[67],**cand,"source":f"v5c-hybrid-purpledisc {tag}","self_med":round(ms,3)}
pickle.dump({"final":fin5},open("work/final_tpl_v5.pkl","wb"))
Image.fromarray(cand['tpl'].astype(np.uint8)).resize((120,120),Image.NEAREST).save("work/calcite_tpl.png")
# ---- rescan kept-patch classes with fin5 ----
import geopandas as gpd
from transforms import min_lonlat_to_basepx
CLASSES=[2,4,7,11,15,18,23,34,37,46,47,48,49,51,54,55,58,62,63,64,66,67]
baseb=cv2.GaussianBlur(base,(3,3),0.7)
adm=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp")
valid=np.zeros((H,W),np.uint8)
for geom in adm.geometry:
    polys=geom.geoms if geom.geom_type=='MultiPolygon' else [geom]
    for p in polys:
        px=np.array([min_lonlat_to_basepx(x,y) for x,y in p.exterior.coords],np.int32)
        cv2.fillPoly(valid,[px.reshape(-1,1,2)],1)
valid=cv2.dilate(valid,np.ones((21,21),np.uint8)).astype(bool)
def ncc_and_means(img,tpl,mask):
    m=mask.astype(np.float32); n=float(m.sum())
    num=None; denI=None; denT=0.0; means=[]
    for c in range(3):
        I=img[:,:,c]; mu=float((tpl[:,:,c]*m).sum()/n)
        Tc=(tpl[:,:,c]-mu)*m
        A=cv2.matchTemplate(I,Tc,cv2.TM_CCORR)
        Is=I-128.0
        B=cv2.matchTemplate(Is,m,cv2.TM_CCORR); C=cv2.matchTemplate(Is*Is,m,cv2.TM_CCORR)
        means.append(cv2.matchTemplate(I,m,cv2.TM_CCORR)/n)
        num=A if num is None else num+A
        d=C-B*B/n; denI=d if denI is None else denI+d
        denT+=float((Tc*Tc).sum())
    ok=denI>(25.0*n)
    sc=np.where(ok,num/np.sqrt(np.maximum(denI,1e-6)*denT),-1.0)
    return np.clip(sc,-1,1).astype(np.float32), means
def subpix(mp,x,y):
    if x<1 or y<1 or x>=mp.shape[1]-1 or y>=mp.shape[0]-1: return 0.0,0.0
    fx=(mp[y,x-1]-mp[y,x+1])/(2*(mp[y,x-1]-2*mp[y,x]+mp[y,x+1])+1e-9)
    fy=(mp[y-1,x]-mp[y+1,x])/(2*(mp[y-1,x]-2*mp[y,x]+mp[y+1,x])+1e-9)
    return float(np.clip(fx,-0.5,0.5)),float(np.clip(fy,-0.5,0.5))
rows=[]
for no in CLASSES:
    f=fin5[no]; tpl=cv2.GaussianBlur(f['tpl'].astype(np.float32),(3,3),0.7); mask=f['mask']
    mp,means=ncc_and_means(baseb,tpl,mask)
    hx=(tpl.shape[1]-1)//2; hy=(tpl.shape[0]-1)//2
    vsub=valid[hy:hy+mp.shape[0],hx:hx+mp.shape[1]]
    mpv=np.where(vsub,mp,-1)
    dil=cv2.dilate(mpv,np.ones((5,5),np.float32))
    ys,xs=np.where((mpv>=0.45)&(mpv>=dil-1e-6))
    tmean=np.array([float((tpl[:,:,c][mask]).mean()) for c in range(3)])
    fx0,fy0=f['frac']
    for x,y in zip(xs,ys):
        sx,sy=subpix(mpv,x,y)
        dmean=max(abs(float(means[c][y,x])-tmean[c]) for c in range(3))
        rows.append((no,x+hx+sx+fx0,y+hy+sy+fy0,float(mpv[y,x]),round(dmean,1)))
    sc=mpv[ys,xs]
    print(no,"cand",len(ys),"max",round(float(mpv.max()),3),{t:int((sc>=t).sum()) for t in (0.6,0.7,0.8)},flush=True)
new=pd.DataFrame(rows,columns=["leg_no","px_x","px_y","score","dmean"])
old=pd.read_csv("work/scan_candidates2.csv")
out=pd.concat([old[~old.leg_no.isin(CLASSES)],new],ignore_index=True)
out.to_csv("work/scan_candidates3.csv",index=False)
print("scan_candidates3 total",len(out))
