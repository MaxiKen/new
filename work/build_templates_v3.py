import numpy as np, pandas as pd, geopandas as gpd, cv2, pickle
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
import warnings; warnings.filterwarnings('ignore')
base=np.array(Image.open("work/mineral_base_2060x1677.png").convert("RGB")).astype(np.float32)
H,W=base.shape[:2]
legt=pickle.load(open("work/legend_tpl.pkl","rb"))["legend_tpl"]
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
pts=minr[['px_x','px_y']].values
order=np.argsort(minr.fid.values); taken=np.zeros(len(pts),bool); keep=[]; tt=cKDTree(pts)
for i in order:
    if taken[i]: continue
    keep.append(i)
    for j in tt.query_ball_point(pts[i],6): taken[j]=True
dedup=minr.iloc[keep].copy()
dpts=dedup[['px_x','px_y']].values; dt=cKDTree(dpts); dd,_=dt.query(dpts,k=2); dedup['nn']=dd[:,1]
BIG=20; OUT=13; SZ=27
def crop_at(cx,cy,half,img=base):
    icx,icy=int(round(cx)),int(round(cy))
    canv=np.full((2*half+1,2*half+1,3),255,np.float32)
    x0,x1=max(0,icx-half),min(W,icx+half+1); y0,y1=max(0,icy-half),min(H,icy+half+1)
    canv[y0-icy+half:y1-icy+half,x0-icx+half:x1-icx+half]=img[y0:y1,x0:x1]
    return canv
def rectwin(cx,cy,hx,hy):
    icx,icy=int(round(cx)),int(round(cy))
    canv=np.full((2*hy+1,2*hx+1,3),255,np.float32)
    x0,x1=max(0,icx-hx),min(W,icx+hx+1); y0,y1=max(0,icy-hy),min(H,icy+hy+1)
    canv[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=base[y0:y1,x0:x1]
    return canv
def masked_ncc(win,tpl,mask):
    if win.shape!=tpl.shape or mask.sum()<8: return -1
    a=win[mask]; b=tpl[mask]; a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    den=np.sqrt((a*a).sum()*(b*b).sum())
    return float((a*b).sum()/den) if den>0 else -1
def footprint_from_median(M):
    border=np.concatenate([M[:2].reshape(-1,3),M[-2:].reshape(-1,3),M[:,:2].reshape(-1,3),M[:,-2:].reshape(-1,3)])
    B=np.median(border,axis=0)
    D=np.max(np.abs(M-B),axis=2)
    foot=(D>30).astype(np.uint8)
    foot=cv2.morphologyEx(foot,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,lab,stats,cents=cv2.connectedComponentsWithStats(foot,8)
    keepm=np.zeros(foot.shape,bool); c0=SZ//2
    for k in range(1,n):
        x,y,w,h,a=stats[k]
        if (a>=8 or ((x-3<=c0<=x+w+3) and (y-3<=c0<=y+h+3))): keepm|=(lab==k)
    inv=(~keepm).astype(np.uint8); nn,ll=cv2.connectedComponents(inv,4)
    borderl=set(np.unique(np.concatenate([ll[0,:],ll[-1,:],ll[:,0],ll[:,-1]])))-{0}
    interior=np.isin(ll,[v for v in range(1,nn) if v not in borderl])
    foot2=(keepm|interior)
    foot2=cv2.dilate(foot2.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
    return foot2
def recentre(tpl,foot):
    ys,xs=np.where(foot)
    if len(xs)<8: return None
    cx=(xs.min()+xs.max())/2; cy=(ys.min()+ys.max())/2
    hx=int(np.ceil(max(cx-xs.min(),xs.max()-cx)))+1; hy=int(np.ceil(max(cy-ys.min(),ys.max()-cy)))+1
    icx,icy=int(round(cx)),int(round(cy))
    canvas=np.full((2*hy+1,2*hx+1,3),255,np.uint8); cm=np.zeros((2*hy+1,2*hx+1),bool)
    x0,x1=max(0,icx-hx),min(tpl.shape[1],icx+hx+1); y0,y1=max(0,icy-hy),min(tpl.shape[0],icy+hy+1)
    canvas[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=tpl[y0:y1,x0:x1].astype(np.uint8)
    cm[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=foot[y0:y1,x0:x1]
    return canvas,cm,(cx-icx,cy-icy)
def sane(cm):
    ys,xs=np.where(cm); w=xs.max()-xs.min()+1; h=ys.max()-ys.min()+1
    return w<=23 and h<=21 and cm.sum()<=240 and cm.sum()>=12
def build_exemplar(rows):
    orig=[(float(r.px_x),float(r.px_y)) for r in rows]
    bigs=[crop_at(x,y,BIG) for x,y in orig]
    aligned=np.array([c[BIG-OUT:BIG+OUT+1,BIG-OUT:BIG+OUT+1] for c in bigs])
    tpl=np.median(aligned,axis=0); centres=list(orig)
    for it in range(3):
        newal=[]; newcen=[]
        for cb,(ox,oy) in zip(bigs,orig):
            res=cv2.matchTemplate(cb.astype(np.uint8),tpl.astype(np.uint8),cv2.TM_CCOEFF_NORMED)
            _,_,_,loc=cv2.minMaxLoc(res)
            ccx,ccy=loc[0]+OUT,loc[1]+OUT
            newcen.append((ox+(ccx-BIG), oy+(ccy-BIG)))  # FIXED: relative to ORIGINAL crop centre
            canv=np.full((SZ,SZ,3),255,np.float32)
            x0,x1=max(0,ccx-OUT),min(2*BIG+1,ccx+OUT+1); y0,y1=max(0,ccy-OUT),min(2*BIG+1,ccy+OUT+1)
            canv[y0-ccy+OUT:y1-ccy+OUT,x0-ccx+OUT:x1-ccx+OUT]=cb[y0:y1,x0:x1]
            newal.append(canv)
        aligned=np.array(newal); centres=newcen; tpl=np.median(aligned,axis=0)
    foot=footprint_from_median(tpl)
    rc=recentre(tpl,foot)
    if rc is None: return None
    canvas,cm,frac=rc
    if not sane(cm): return None
    return {"tpl":canvas,"mask":cm,"frac":frac,"n":len(rows)}
def eval_at_points(cand, rows_pts, search=3):
    canvas=cand["tpl"]; cm=cand["mask"]
    tf=cv2.GaussianBlur(canvas.astype(np.float32),(3,3),0.7)
    hx=(canvas.shape[1]-1)//2; hy=(canvas.shape[0]-1)//2
    scs=[]
    for (x,y) in rows_pts:
        b=-1
        for dy in range(-search,search+1):
            for dx in range(-search,search+1):
                wb=cv2.GaussianBlur(rectwin(x+dx,y+dy,hx,hy),(3,3),0.7)
                b=max(b,masked_ncc(wb,tf,cm))
        scs.append(b)
    return scs
def legend_scaled(no,sx_pt,sy_pt):
    tpl0,foot0=legt[no]
    sx=sx_pt/(300/72); sy=sy_pt/(300/72)
    nw=max(3,int(round(tpl0.shape[1]*sx))); nh=max(3,int(round(tpl0.shape[0]*sy)))
    t=cv2.resize(tpl0,(nw,nh),interpolation=cv2.INTER_AREA)
    f=cv2.resize(foot0.astype(np.float32),(nw,nh),interpolation=cv2.INTER_AREA)>0.35
    rc=recentre(t,f)
    if rc is None: return None
    canvas,cm,frac=rc
    if not sane(cm): return None
    return {"tpl":canvas,"mask":cm,"frac":frac}
final={}; rows_rep=[]
for _,lr in leg.iterrows():
    no=int(lr.legend_no); name=lr.point_attribute_name
    sub=dedup[dedup.leg_no==no].sort_values('fid')
    eval_pts=[(float(r.px_x),float(r.px_y)) for _,r in sub.head(25).iterrows()]
    cands=[]
    if len(sub)>=3:
        pref=sub[sub.nn>15]
        use=pref.head(40) if len(pref)>=5 else sub.head(40)
        ex=build_exemplar([r for _,r in use.iterrows()])
        if ex: cands.append(("map-exemplar",ex))
    if len(sub)>=1:
        small=[(float(r.px_x),float(r.px_y)) for _,r in sub.head(10).iterrows()]
        best=None
        for sxp in [0.68,0.76,0.84,0.92,1.0]:
            for syp in [0.76,0.84,0.92,1.0]:
                c=legend_scaled(no,sxp,syp)
                if c is None: continue
                med=float(np.median(eval_at_points(c,small)))
                if best is None or med>best[0]: best=(med,c,f"legend-scaled sx={sxp} sy={syp}")
        if best: cands.append((best[2],best[1]))
    if cands:
        scored=[]
        for tag,c in cands:
            scs=eval_at_points(c,eval_pts)
            scored.append((float(np.median(scs)),tag,c,scs))
        scored.sort(key=lambda z:-z[0])
        med,tag,c,scs=scored[0]
        final[no]={**c,"source":tag,"self_med":round(med,3),"self_p25":round(float(np.quantile(scs,0.25)),3),"n_eval":len(eval_pts)}
    else:
        c=legend_scaled(no,0.88,0.88) or legend_scaled(no,0.8,0.88)
        final[no]={**c,"source":"legend-only default (no old pts)","self_med":None,"n_eval":0}
    f=final[no]
    rows_rep.append((no,name,len(sub),f["source"],f.get("self_med"),(f["tpl"].shape[1],f["tpl"].shape[0]),int(f["mask"].sum())))
    print(rows_rep[-1],flush=True)
pickle.dump({"final":final},open("work/final_tpl_v3.pkl","wb"))
cols=6; s=130; rowsn=int(np.ceil(67/cols))
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255)); dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(range(1,68)):
    x=(idx%cols)*s; y=(idx//cols)*s; f=final[no]
    dr.text((x+4,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:16]}",fill=(200,0,0))
    t=f['tpl']; big=Image.fromarray(t).resize((t.shape[1]*4,t.shape[0]*4),Image.NEAREST)
    sheet.paste(big,(x+4,y+16))
    dr.text((x+4,y+s-26),f["source"][:24],fill=(0,0,160)); dr.text((x+4,y+s-14),f"med={f.get('self_med')}",fill=(0,120,0))
sheet.save("work/final_templates_sheet_v3.png")
pd.DataFrame(rows_rep,columns=["leg_no","name","n_old_dedup","source","self_med","size","mask_px"]).to_csv("work/final_templates_v3.csv",index=False)
print("v3 done")
