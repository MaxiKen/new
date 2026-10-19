import numpy as np, pandas as pd, cv2, pickle, sys
sys.path.insert(0,"work")
src=open("work/build_templates_v3.py").read().split("final={}")[0]
exec(src)
cand3=pd.read_csv("work/scan_candidates3.csv")
pts3=pd.read_csv("work/points_v3.csv")
def near(df,x,y,r=7,label=""):
    sub=df[np.hypot(df.px_x-x,df.px_y-y)<=r].sort_values('score',ascending=False) if 'score' in df else df[np.hypot(df.px_x-x,df.px_y-y)<=r]
    print(f"--- {label} around ({x},{y}) r={r}")
    print(sub.head(10).to_string(index=False) if len(sub) else "  (none)")
f439=minr[minr.fid==439].iloc[0]; print("L4 f439 old Bauxitic pt:",f439.px_x,f439.px_y)
near(cand3,467,1192,7,"candidates @ pink glyph SW")
near(pts3,467,1192,10,"points_v3 @ pink glyph")
near(cand3,float(f439.px_x),float(f439.px_y),7,"candidates @ f439 F glyph")
for fid in (678,947):
    r=minr[minr.fid==fid].iloc[0]; print(f"fid{fid} {r.mineral} at {r.px_x},{r.px_y}")
    near(cand3,float(r.px_x),float(r.px_y),8,f"candidates @ fid{fid}")
    near(pts3,float(r.px_x),float(r.px_y),10,f"points_v3 @ fid{fid}")
r=minr[minr.fid==1396].iloc[0]
near(pts3,float(r.px_x),float(r.px_y),14,"points_v3 @ BrickClay fid1396")
near(cand3,float(r.px_x),float(r.px_y),10,"candidates @ BrickClay fid1396")
# unverified coverage
unv=pd.read_csv("work/unverified_old_v3.csv")
from scipy.spatial import cKDTree
t=cKDTree(pts3[['px_x','px_y']].values); d,_=t.query(unv[['px_x','px_y']].values)
print("unverified with new point within 8px:",int((d<=8).sum()),"of",len(unv)," | >12px:",int((d>12).sum()))
# hybrids
def hybrid_fit(no,seedpts,trim=0.45):
    tpl0,foot0=legt[no]; best=None
    for sxp in np.arange(0.60,1.05,0.04):
        for syp in np.arange(0.68,1.05,0.04):
            sx=sxp/(300/72); sy=syp/(300/72)
            nw=max(3,int(round(tpl0.shape[1]*sx))); nh=max(3,int(round(tpl0.shape[0]*sy)))
            t2=cv2.resize(tpl0,(nw,nh),interpolation=cv2.INTER_AREA)
            f=cv2.resize(foot0.astype(np.float32),(nw,nh),interpolation=cv2.INTER_AREA)>0.35
            rc=recentre(t2,f)
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
    if len(crops)>=1:
        med=np.median(np.array(crops),axis=0)
        newtpl=canvas.copy(); newtpl[cm]=med[cm]
        cand={"tpl":newtpl.astype(np.uint8),"mask":cm,"frac":cand["frac"]}
        ms=float(np.median(eval_at_points(cand,seedpts,search=4)))
    return ms,cand,f"sx={sxp:.2f} sy={syp:.2f} crops={len(crops)} precolour={best[0]:.3f}"
fin5=pickle.load(open("work/final_tpl_v5.pkl","rb"))["final"]
rg=[(r.px_x,r.px_y) for _,r in pts3[pts3.leg_no==28].iterrows()]+[(288.8,277.5)]
ms,c,tag=hybrid_fit(28,rg); print(f"28 RiverGravel hybrid {ms:.3f} {tag} size {c['tpl'].shape}")
fin5[28]={**fin5[28],**c,"source":f"v6-hybrid {tag}","self_med":round(ms,3)}
ms,c,tag=hybrid_fit(22,[(float(f439.px_x),float(f439.px_y))]); print(f"22 Fluorite hybrid {ms:.3f} {tag} size {c['tpl'].shape}")
fin5[22]={**fin5[22],**c,"source":f"v6-hybrid-f439seed {tag}","self_med":round(ms,3)}
pickle.dump({"final":fin5},open("work/final_tpl_v6.pkl","wb"))
# rescan 22,28
import geopandas as gpd
from transforms import min_lonlat_to_basepx
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
    for ch in range(3):
        I=img[:,:,ch]; mu=float((tpl[:,:,ch]*m).sum()/n)
        Tc=(tpl[:,:,ch]-mu)*m
        A=cv2.matchTemplate(I,Tc,cv2.TM_CCORR)
        Is=I-128.0
        B=cv2.matchTemplate(Is,m,cv2.TM_CCORR); C=cv2.matchTemplate(Is*Is,m,cv2.TM_CCORR)
        means.append(cv2.matchTemplate(I,m,cv2.TM_CCORR)/n)
        num=A if num is None else num+A
        d=C-B*B/n; denI=d if denI is None else denI+d
        denT+=float((Tc*Tc).sum())
    ok=denI>(25.0*n)
    return np.clip(np.where(ok,num/np.sqrt(np.maximum(denI,1e-6)*denT),-1.0),-1,1).astype(np.float32), means
def subpix(mp,x,y):
    if x<1 or y<1 or x>=mp.shape[1]-1 or y>=mp.shape[0]-1: return 0.0,0.0
    fx=(mp[y,x-1]-mp[y,x+1])/(2*(mp[y,x-1]-2*mp[y,x]+mp[y,x+1])+1e-9)
    fy=(mp[y-1,x]-mp[y+1,x])/(2*(mp[y-1,x]-2*mp[y,x]+mp[y+1,x])+1e-9)
    return float(np.clip(fx,-0.5,0.5)),float(np.clip(fy,-0.5,0.5))
rows=[]
for no in (22,28):
    f=fin5[no]; tpl=cv2.GaussianBlur(f['tpl'].astype(np.float32),(3,3),0.7); mask=f['mask']
    mp,means=ncc_and_means(baseb,tpl,mask)
    hx=(tpl.shape[1]-1)//2; hy=(tpl.shape[0]-1)//2
    vsub=valid[hy:hy+mp.shape[0],hx:hx+mp.shape[1]]
    mpv=np.where(vsub,mp,-1)
    dil=cv2.dilate(mpv,np.ones((5,5),np.float32))
    ys,xs=np.where((mpv>=0.45)&(mpv>=dil-1e-6))
    tmean=np.array([float((tpl[:,:,ch][mask]).mean()) for ch in range(3)])
    fx0,fy0=f['frac']
    for x,y in zip(xs,ys):
        sx,sy=subpix(mpv,x,y)
        dmean=max(abs(float(means[ch][y,x])-tmean[ch]) for ch in range(3))
        rows.append((no,x+hx+sx+fx0,y+hy+sy+fy0,float(mpv[y,x]),round(dmean,1)))
    print(no,"cand",len(ys),"max",round(float(mpv.max()),3),flush=True)
new=pd.DataFrame(rows,columns=["leg_no","px_x","px_y","score","dmean"])
out=pd.concat([cand3[~cand3.leg_no.isin([22,28])],new],ignore_index=True)
out.to_csv("work/scan_candidates4.csv",index=False)
for no in (22,28):
    cc=new[new.leg_no==no]
    for T in (0.6,0.65,0.7,0.75,0.8):
        print(no,"T",T,"gated40:",int(((cc.score>=T)&(cc.dmean<=40)).sum()))
print("saved scan_candidates4.csv")
