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
order=np.argsort(minr.fid.values); taken=np.zeros(len(pts),bool); keep=[]
tt=cKDTree(pts)
for i in order:
    if taken[i]: continue
    keep.append(i)
    for j in tt.query_ball_point(pts[i],6): taken[j]=True
dedup=minr.iloc[keep].copy()
dpts=dedup[['px_x','px_y']].values; dt=cKDTree(dpts); dd,_=dt.query(dpts,k=2); dedup['nn']=dd[:,1]
print("dedup pool",len(dedup))
BIG=20; OUT=13; SZ=27
def crop_at(cx,cy,half,img=base):
    icx,icy=int(round(cx)),int(round(cy))
    canv=np.full((2*half+1,2*half+1,3),255,np.float32)
    x0,x1=max(0,icx-half),min(W,icx+half+1); y0,y1=max(0,icy-half),min(H,icy+half+1)
    canv[y0-icy+half:y1-icy+half,x0-icx+half:x1-icx+half]=img[y0:y1,x0:x1]
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
    foot=(D>22).astype(np.uint8)
    foot=cv2.morphologyEx(foot,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,lab,stats,cents=cv2.connectedComponentsWithStats(foot,8)
    keepm=np.zeros(foot.shape,bool); cy0,cx0=SZ//2,SZ//2
    for k in range(1,n):
        x,y,w,h,a=stats[k]
        central=(x-3<=cx0<=x+w+3) and (y-3<=cy0<=y+h+3)
        if a>=8 or central: keepm|=(lab==k)
    inv=(~keepm).astype(np.uint8); nn,ll=cv2.connectedComponents(inv,4)
    borderl=set(np.unique(np.concatenate([ll[0,:],ll[-1,:],ll[:,0],ll[:,-1]])))-{0}
    interior=np.isin(ll,[v for v in range(1,nn) if v not in borderl])
    return keepm|interior
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
def build_exemplar(rows):
    bigs=[crop_at(r.px_x,r.px_y,BIG) for r in rows]
    aligned=np.array([c[BIG-OUT:BIG+OUT+1,BIG-OUT:BIG+OUT+1] for c in bigs])
    tpl=np.median(aligned,axis=0)
    centres=[(float(r.px_x),float(r.px_y)) for r in rows]
    for it in range(3):
        newal=[]; newcen=[]
        for cb,(ox,oy) in zip(bigs,centres):
            res=cv2.matchTemplate(cb.astype(np.uint8),tpl.astype(np.uint8),cv2.TM_CCOEFF_NORMED)
            _,_,_,loc=cv2.minMaxLoc(res)
            ccx,ccy=loc[0]+OUT,loc[1]+OUT
            # refined centre in base coords: original centre + (cc-BIG)
            newcen.append((ox+(ccx-BIG), oy+(ccy-BIG)))
            canv=np.full((SZ,SZ,3),255,np.float32)
            x0,x1=max(0,ccx-OUT),min(2*BIG+1,ccx+OUT+1); y0,y1=max(0,ccy-OUT),min(2*BIG+1,ccy+OUT+1)
            canv[y0-ccy+OUT:y1-ccy+OUT,x0-ccx+OUT:x1-ccx+OUT]=cb[y0:y1,x0:x1]
            newal.append(canv)
        aligned=np.array(newal); centres=newcen; tpl=np.median(aligned,axis=0)
    foot=footprint_from_median(tpl)
    if foot.sum()<15 or foot.sum()>0.65*SZ*SZ: return None,centres,foot
    rc=recentre(tpl,foot)
    if rc is None: return None,centres,foot
    canvas,cm,frac=rc
    # self scores (blurred)
    scores=[]
    tf=cv2.GaussianBlur(canvas.astype(np.float32),(3,3),0.7)
    for (cx,cy) in centres:
        win=crop_at(cx,cy,(canvas.shape[1]-1)//2) if canvas.shape[1]==canvas.shape[0] else None
        # general rect window
        hx=(canvas.shape[1]-1)//2; hy=(canvas.shape[0]-1)//2
        icx,icy=int(round(cx)),int(round(cy))
        canv=np.full((2*hy+1,2*hx+1,3),255,np.float32)
        x0,x1=max(0,icx-hx),min(W,icx+hx+1); y0,y1=max(0,icy-hy),min(H,icy+hy+1)
        canv[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=base[y0:y1,x0:x1]
        wb=cv2.GaussianBlur(canv,(3,3),0.7)
        scores.append(masked_ncc(wb,tf,cm))
    return {"tpl":canvas,"mask":cm,"frac":frac,"self_med":round(float(np.median(scores)),3),"self_scores":scores,"centres":centres,"n":len(rows)},centres,foot

final={}; rep=[]
# legend fallback helper with anisotropic scale search at known points
def legend_fallback(no, rows):
    tpl0,foot0=legt[no]
    best=None
    for sx_pt in [0.68,0.76,0.84,0.92,1.0]:  # px per pt x
        for sy_pt in [0.76,0.84,0.92,1.0]:
            sx=sx_pt/(300/72); sy=sy_pt/(300/72)
            nw=max(3,int(round(tpl0.shape[1]*sx))); nh=max(3,int(round(tpl0.shape[0]*sy)))
            t=cv2.resize(tpl0,(nw,nh),interpolation=cv2.INTER_AREA)
            f=cv2.resize(foot0.astype(np.float32),(nw,nh),interpolation=cv2.INTER_AREA)>0.35
            rc=recentre(t,f)
            if rc is None: continue
            canvas,cm,frac=rc
            tf=cv2.GaussianBlur(canvas.astype(np.float32),(3,3),0.7)
            hx=(canvas.shape[1]-1)//2; hy=(canvas.shape[0]-1)//2
            scs=[]
            for r in rows:
                b=-1
                for dy in range(-3,4):
                    for dx in range(-3,4):
                        icx,icy=int(round(r.px_x+dx)),int(round(r.px_y+dy))
                        canv=np.full((2*hy+1,2*hx+1,3),255,np.float32)
                        x0,x1=max(0,icx-hx),min(W,icx+hx+1); y0,y1=max(0,icy-hy),min(H,icy+hy+1)
                        canv[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=base[y0:y1,x0:x1]
                        b=max(b,masked_ncc(cv2.GaussianBlur(canv,(3,3),0.7),tf,cm))
                scs.append(b)
            med=float(np.median(scs)) if scs else -1
            if best is None or med>best[0]: best=(med,canvas,cm,frac,sx_pt,sy_pt,scs)
    return best

for _,lr in leg.iterrows():
    no=int(lr.legend_no); name=lr.point_attribute_name
    sub=dedup[dedup.leg_no==no]
    pref=sub[sub.nn>15].sort_values('fid')
    use=pref.head(40) if len(pref)>=5 else sub.sort_values('fid').head(40)
    out=None
    if len(use)>=3:
        out,_,_=build_exemplar([r for _,r in use.iterrows()])
    if out is not None and out["self_med"]>=0.60:
        final[no]={**out,"source":f"map-exemplar median (n={out['n']})"}
    else:
        rows=[r for _,r in sub.sort_values('fid').head(12).iterrows()]
        if rows:
            best=legend_fallback(no,rows)
            med,canvas,cm,frac,sxp,syp,scs=best
            # colour-adapt from best-aligned crops if med decent: skip (keep legend colours) for simplicity unless exemplar out exists with lower score
            if out is not None and out["self_med"]>med:
                final[no]={**out,"source":f"map-exemplar median LOWSCORE (n={out['n']})"}
            else:
                final[no]={"tpl":canvas,"mask":cm,"frac":frac,"self_med":round(med,3),"source":f"legend scaled sx={sxp} sy={syp} (npts={len(rows)})","n":len(rows)}
        elif out is not None:
            final[no]={**out,"source":f"map-exemplar median (n={out['n']})"}
        else:
            # no old points at all: legend at default scale (0.947 px/pt; rect classes use 0.76 x-scale guess? use isotropic 0.88 compromise, flag)
            tpl0,foot0=legt[no]; s=0.88/(300/72)
            nw=max(3,int(round(tpl0.shape[1]*s))); nh=max(3,int(round(tpl0.shape[0]*s)))
            t=cv2.resize(tpl0,(nw,nh),interpolation=cv2.INTER_AREA); f=cv2.resize(foot0.astype(np.float32),(nw,nh),interpolation=cv2.INTER_AREA)>0.35
            canvas,cm,frac=recentre(t,f)
            final[no]={"tpl":canvas,"mask":cm,"frac":frac,"self_med":None,"source":"legend-only default scale (no old points)","n":0}
    rep.append((no,name,len(sub),final[no]["source"],final[no].get("self_med"),(final[no]["tpl"].shape[1],final[no]["tpl"].shape[0]),int(final[no]["mask"].sum())))
    print(rep[-1])
pickle.dump({"final":final},open("work/final_tpl_v2.pkl","wb"))
cols=8; s=100; rowsn=int(np.ceil(67/cols))
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255)); dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(range(1,68)):
    x=(idx%cols)*s; y=(idx//cols)*s
    dr.text((x+4,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:14]}",fill=(200,0,0))
    t=final[no]['tpl']; big=Image.fromarray(t).resize((t.shape[1]*3,t.shape[0]*3),Image.NEAREST)
    sheet.paste(big,(x+4,y+15)); dr.text((x+4,y+84),f"s={final[no].get('self_med')}",fill=(0,0,160))
sheet.save("work/final_templates_sheet_v2.png")
print("v2 sheet saved")
