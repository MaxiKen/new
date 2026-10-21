import numpy as np, pandas as pd, geopandas as gpd, cv2, pickle
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
import warnings; warnings.filterwarnings('ignore')
base=np.array(Image.open("work/mineral_base_2060x1677.png").convert("RGB")).astype(np.float32)
H,W=base.shape[:2]
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
pts=minr[['px_x','px_y']].values
tree=cKDTree(pts); dd,_=tree.query(pts,k=2); nn=dd[:,1]
minr['nn']=nn
BIG=20; OUT=13; SZ=2*OUT+1  # aligned crop 27
def get_crop(cx,cy,half):
    cx,cy=int(round(cx)),int(round(cy))
    canvas=np.full((2*half+1,2*half+1,3),255,np.float32)
    x0,x1=max(0,cx-half),min(W,cx+half+1); y0,y1=max(0,cy-half),min(H,cy+half+1)
    canvas[y0-cy+half:y1-cy+half, x0-cx+half:x1-cx+half]=base[y0:y1,x0:x1]
    return canvas

def build_class(rows):
    crops_big=[get_crop(r.px_x,r.px_y,BIG) for r in rows]
    # init template: median of central 27 crops (unaligned)
    cents=np.array([c[BIG-OUT:BIG+OUT+1,BIG-OUT:BIG+OUT+1] for c in crops_big])
    tpl=np.median(cents,axis=0)
    aligned=cents.copy()
    for it in range(3):
        newal=[]
        tpl_bgr=tpl.astype(np.uint8)
        for cb in crops_big:
            res=cv2.matchTemplate(cb.astype(np.uint8), tpl_bgr, cv2.TM_CCOEFF_NORMED)
            _,_,_,loc=cv2.minMaxLoc(res)
            # loc is top-left in 41 canvas; aligned centre should be at BIG => extract 27 around loc centre
            ccx=loc[0]+OUT; ccy=loc[1]+OUT
            # clip cc to allow extraction with padding
            canv=np.full((SZ,SZ,3),255,np.float32)
            x0,x1=max(0,ccx-OUT),min(2*BIG+1,ccx+OUT+1); y0,y1=max(0,ccy-OUT),min(2*BIG+1,ccy+OUT+1)
            canv[y0-ccy+OUT:y1-ccy+OUT, x0-ccx+OUT:x1-ccx+OUT]=cb[y0:y1,x0:x1]
            newal.append(canv)
        aligned=np.array(newal); tpl=np.median(aligned,axis=0)
    # backgrounds + footprint
    bgfrac=np.zeros((SZ,SZ)); 
    for c in aligned:
        border=np.concatenate([c[0,:],c[-1,:],c[:,0],c[:,-1]])
        bg=np.median(border,axis=0)
        isbg=np.max(np.abs(c-bg),axis=2)<22
        bgfrac+=isbg
    bgfrac/=len(aligned)
    foot=bgfrac<0.35
    # clean: keep comps area>=3, fill enclosed holes
    n,lab,stats,_=cv2.connectedComponentsWithStats(foot.astype(np.uint8),8)
    keep=np.zeros_like(foot)
    for k in range(1,n):
        if stats[k,cv2.CC_STAT_AREA]>=3: keep|= (lab==k)
    inv=(~keep).astype(np.uint8); nn,ll=cv2.connectedComponents(inv,4)
    borderl=set(np.unique(np.concatenate([ll[0,:],ll[-1,:],ll[:,0],ll[:,-1]])))-{0}
    interior=np.isin(ll,[v for v in range(1,nn) if v not in borderl])
    foot=keep|interior
    # template colour: median over non-bg instances per pixel
    tplcol=np.zeros((SZ,SZ,3),np.float32)
    for yy in range(SZ):
        for xx in range(SZ):
            vals=[]
            for ci,c in enumerate(aligned):
                border=np.concatenate([c[0,:],c[-1,:],c[:,0],c[:,-1]]); bg=np.median(border,axis=0)
                if np.max(np.abs(c[yy,xx]-bg))>=22: vals.append(c[yy,xx])
            tplcol[yy,xx]=np.median(vals,axis=0) if vals else np.median(aligned[:,yy,xx],axis=0)
    # centred canvas on footprint bbox centre
    ys,xs=np.where(foot)
    if len(xs)==0: return None
    cx=(xs.min()+xs.max())/2; cy=(ys.min()+ys.max())/2
    hx=int(np.ceil(max(cx-xs.min(), xs.max()-cx)))+1; hy=int(np.ceil(max(cy-ys.min(), ys.max()-cy)))+1
    icx,icy=int(round(cx)),int(round(cy))
    canvas=np.full((2*hy+1,2*hx+1,3),255,np.uint8); cmask=np.zeros((2*hy+1,2*hx+1),bool)
    x0,x1=max(0,icx-hx),min(SZ,icx+hx+1); y0,y1=max(0,icy-hy),min(SZ,icy+hy+1)
    canvas[y0-icy+hy:y1-icy+hy, x0-icx+hx:x1-icx+hx]=tplcol[y0:y1,x0:x1].astype(np.uint8)
    cmask[y0-icy+hy:y1-icy+hy, x0-icx+hx:x1-icx+hx]=foot[y0:y1,x0:x1]
    return {"tpl":canvas,"mask":cmask,"frac":(cx-icx,cy-icy),"n":len(rows),"foot_wh":(int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1))}

exemplars={}
report=[]
for _,lr in leg.iterrows():
    no=int(lr.legend_no)
    sub=minr[minr.leg_no==no]
    iso=sub[sub.nn>28].sort_values('fid')
    # prefer signature/table methods first
    use=iso.head(40)
    if len(use)<4:
        # relax isolation to 18
        use=sub[sub.nn>18].sort_values('fid').head(40)
    if len(use)>=3:
        rows=[r for _,r in use.iterrows()]
        out=build_class(rows)
        if out: exemplars[no]=out
        report.append((no,lr.point_attribute_name,len(sub),len(use), out['foot_wh'] if out else None, (out['tpl'].shape[1],out['tpl'].shape[0]) if out else None))
    else:
        report.append((no,lr.point_attribute_name,len(sub),len(use),None,None))
    print(report[-1])
pickle.dump({"exemplars":exemplars},open("work/exemplar_tpl.pkl","wb"))
# sheet
cols=8; s=96; rowsn=int(np.ceil(67/cols))
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255)); dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(range(1,68)):
    x=(idx%cols)*s; y=(idx//cols)*s
    dr.text((x+4,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:15]}",fill=(200,0,0))
    if no in exemplars:
        t=exemplars[no]['tpl']; big=Image.fromarray(t).resize((t.shape[1]*3,t.shape[0]*3),Image.NEAREST)
        sheet.paste(big,(x+4,y+16)); dr.text((x+4,y+80),f"n={exemplars[no]['n']}",fill=(0,0,200))
    else:
        dr.text((x+4,y+30),"NO EXEMPLAR\n(legend only)",fill=(200,0,0))
sheet.save("work/exemplar_templates_sheet.png")
print("sheet saved")
# scale calibration legend(pt) -> exemplar(px)
legt=pickle.load(open("work/legend_tpl.pkl","rb"))["legend_tpl"]
ratios=[]
for no in exemplars:
    lt,lf=legt[no]; lys,lxs=np.where(lf)
    lw=(lxs.max()-lxs.min()+1)/(300/72); lh=(lys.max()-lys.min()+1)/(300/72)
    ew,eh=exemplars[no]['foot_wh']
    ratios.append((no,ew/lw,eh/lh))
    print(f"leg{no} ratio x {ew/lw:.3f} y {eh/lh:.3f} (ex {ew}x{eh}px vs legend {lw:.1f}x{lh:.1f}pt)")
r=np.array([(a+b)/2 for _,a,b in ratios])
print(f"median px/pt ratio map/legend = {np.median(r):.4f} (base px/pt if same size = {2060/1977.59:.4f}); downscale from 300dpi legend render = {np.median(r)/(300/72):.4f}")
