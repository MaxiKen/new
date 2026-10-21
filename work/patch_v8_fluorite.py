import numpy as np, pandas as pd, cv2, pickle, sys
sys.path.insert(0,"work")
from PIL import Image, ImageDraw
src=open("work/build_templates_v3.py").read().split("final={}")[0]
exec(src)
cx,cy=1579.5,944.5
x0,y0=int(cx)-25,int(cy)-25; win=base[y0:y0+51,x0:x0+51]
R,G,B=win[:,:,0],win[:,:,1],win[:,:,2]
orange=((R>170)&(G>70)&(G<200)&(B<130)&(R-B>90)).astype(np.uint8)
n,lab,stats,cents=cv2.connectedComponentsWithStats(orange,8)
blobs=[(x0+cents[k][0],y0+cents[k][1],int(stats[k,4])) for k in range(1,n) if stats[k,4]>=8]
print("orange blobs near fid339:",blobs)
Image.fromarray(win.astype(np.uint8)).resize((306,306),Image.NEAREST).save("work/fluorite_seed_zoom2.png")
seed=[(blobs[0][0],blobs[0][1])] if blobs else [(cx,cy)]
def hybrid_fit(no,seedpts,trim=0.45,search=3):
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
            ms=float(np.median(eval_at_points(cand,seedpts,search=search)))
            if best is None or ms>best[0]: best=(ms,cand,sxp,syp)
    ms,cand,sxp,syp=best
    canvas=cand["tpl"].astype(np.float32); cm=cand["mask"]
    tf=cv2.GaussianBlur(canvas,(3,3),0.7)
    hx=(canvas.shape[1]-1)//2; hy=(canvas.shape[0]-1)//2
    crops=[]
    for (x,y) in seedpts:
        bb=-1; bw=None
        for dy in range(-search,search+1):
            for dx in range(-search,search+1):
                w=rectwin(x+dx,y+dy,hx,hy)
                s=masked_ncc(cv2.GaussianBlur(w,(3,3),0.7),tf,cm)
                if s>bb: bb=s; bw=w
        if bw is not None and bb>=trim: crops.append(bw)
    if crops:
        med=np.median(np.array(crops),axis=0)
        newtpl=canvas.copy(); newtpl[cm]=med[cm]
        cand={"tpl":newtpl.astype(np.uint8),"mask":cm,"frac":cand["frac"]}
        ms=float(np.median(eval_at_points(cand,seedpts,search=search)))
    return ms,cand,f"sx={sxp:.2f} sy={syp:.2f} precolour={best[0]:.3f}"
fin6=pickle.load(open("work/final_tpl_v6.pkl","rb"))["final"]
ms,c,tag=hybrid_fit(22,seed)
print(f"22 Fluorite refit2 {ms:.3f} {tag} size {c['tpl'].shape} seed {seed}")
fin6[22]={**fin6[22],**c,"source":f"v8-hybrid-Fseed339 {tag}","self_med":round(ms,3)}
pickle.dump({"final":fin6},open("work/final_tpl_v6.pkl","wb"))
Image.fromarray(c['tpl'].astype(np.uint8)).resize((130,130),Image.NEAREST).save("work/fluorite_tpl2.png")
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
f=fin6[22]; tpl=cv2.GaussianBlur(f['tpl'].astype(np.float32),(3,3),0.7); mask=f['mask']
m=mask.astype(np.float32); nn=float(m.sum()); num=None; denI=None; denT=0.0; means=[]
for ch in range(3):
    I=baseb[:,:,ch]; mu=float((tpl[:,:,ch]*m).sum()/nn); Tc=(tpl[:,:,ch]-mu)*m
    A=cv2.matchTemplate(I,Tc,cv2.TM_CCORR); Is=I-128.0
    Bm=cv2.matchTemplate(Is,m,cv2.TM_CCORR); C=cv2.matchTemplate(Is*Is,m,cv2.TM_CCORR)
    means.append(cv2.matchTemplate(I,m,cv2.TM_CCORR)/nn)
    num=A if num is None else num+A
    d=C-Bm*Bm/nn; denI=d if denI is None else denI+d; denT+=float((Tc*Tc).sum())
ok=denI>(25.0*nn)
mp=np.clip(np.where(ok,num/np.sqrt(np.maximum(denI,1e-6)*denT),-1.0),-1,1).astype(np.float32)
hx=(tpl.shape[1]-1)//2; hy=(tpl.shape[0]-1)//2
mpv=np.where(valid[hy:hy+mp.shape[0],hx:hx+mp.shape[1]],mp,-1)
dil=cv2.dilate(mpv,np.ones((5,5),np.float32))
ys,xs=np.where((mpv>=0.45)&(mpv>=dil-1e-6))
tmean=np.array([float((tpl[:,:,ch][mask]).mean()) for ch in range(3)])
fx0,fy0=f['frac']; rows=[]
def subpix(mp,x,y):
    if x<1 or y<1 or x>=mp.shape[1]-1 or y>=mp.shape[0]-1: return 0.0,0.0
    fx=(mp[y,x-1]-mp[y,x+1])/(2*(mp[y,x-1]-2*mp[y,x]+mp[y,x+1])+1e-9)
    fy=(mp[y-1,x]-mp[y+1,x])/(2*(mp[y-1,x]-2*mp[y,x]+mp[y+1,x])+1e-9)
    return float(np.clip(fx,-0.5,0.5)),float(np.clip(fy,-0.5,0.5))
for x,y in zip(xs,ys):
    sx,sy=subpix(mpv,x,y)
    dmean=max(abs(float(means[ch][y,x])-tmean[ch]) for ch in range(3))
    rows.append((22,x+hx+sx+fx0,y+hy+sy+fy0,float(mpv[y,x]),round(dmean,1)))
new=pd.DataFrame(rows,columns=["leg_no","px_x","px_y","score","dmean"])
old=pd.read_csv("work/scan_candidates4.csv")
pd.concat([old[old.leg_no!=22],new],ignore_index=True).to_csv("work/scan_candidates5.csv",index=False)
for T in (0.6,0.7,0.8,0.85,0.9):
    print("22 T",T,"gated42:",int(((new.score>=T)&(new.dmean<=42)).sum()))
baseim=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
cc=new[new.dmean<=42].sort_values('score',ascending=False)
acc=[]
for _,r in cc.iterrows():
    if all((r.px_x-a.px_x)**2+(r.px_y-a.px_y)**2>64 for a in acc): acc.append(r)
    if len(acc)>=24: break
cell=96; cols=8; rowsn=int(np.ceil(len(acc)/cols)) or 1
im=Image.new("RGB",(cols*cell,rowsn*cell+16),(255,255,255)); dr=ImageDraw.Draw(im)
dr.text((4,3),"22 Fluorite REFIT2 (seed fid339 F) top gated",fill=(200,0,0))
for i,r in enumerate(acc):
    x,y=int(r.px_x),int(r.px_y)
    cr=baseim.crop((x-12,y-12,x+13,y+13)).resize((cell-4,cell-4),Image.NEAREST)
    d2=ImageDraw.Draw(cr); d2.ellipse((cell//2-8,cell//2-8,cell//2+4,cell//2+4),outline=(255,0,0))
    X=(i%cols)*cell; Y=16+(i//cols)*cell
    im.paste(cr,(X,Y)); dr.text((X+3,Y+3),f"{r.score:.2f}",fill=(255,0,0))
im.save("work/qa_patch_22c.png"); print("saved")
