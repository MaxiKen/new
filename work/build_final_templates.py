import numpy as np, pandas as pd, geopandas as gpd, cv2, pickle
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
import warnings; warnings.filterwarnings('ignore')
base=np.array(Image.open("work/mineral_base_2060x1677.png").convert("RGB")).astype(np.float32)
H,W=base.shape[:2]
legt=pickle.load(open("work/legend_tpl.pkl","rb"))["legend_tpl"]
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
# dedupe old points for exemplar picking: cluster within 6px (greedy by fid)
pts=minr[['px_x','px_y']].values
order=np.argsort(minr.fid.values); taken=np.zeros(len(pts),bool); keep_idx=[]
tree_all=cKDTree(pts)
for i in order:
    if taken[i]: continue
    keep_idx.append(i)
    for j in tree_all.query_ball_point(pts[i],6): taken[j]=True
dedup=minr.iloc[keep_idx].copy()
dpts=dedup[['px_x','px_y']].values
dtree=cKDTree(dpts); dd,_=dtree.query(dpts,k=2); dedup['nn']=dd[:,1]
print(f"deduped exemplar pool: {len(dedup)} (from {len(minr)})")

def recentre(tpl, foot):
    ys,xs=np.where(foot)
    if len(xs)==0: return None
    cx=(xs.min()+xs.max())/2; cy=(ys.min()+ys.max())/2
    hx=int(np.ceil(max(cx-xs.min(),xs.max()-cx)))+1; hy=int(np.ceil(max(cy-ys.min(),ys.max()-cy)))+1
    icx,icy=int(round(cx)),int(round(cy))
    canvas=np.full((2*hy+1,2*hx+1,3),255,np.uint8); cm=np.zeros((2*hy+1,2*hx+1),bool)
    x0,x1=max(0,icx-hx),min(tpl.shape[1],icx+hx+1); y0,y1=max(0,icy-hy),min(tpl.shape[0],icy+hy+1)
    canvas[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=tpl[y0:y1,x0:x1]
    cm[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=foot[y0:y1,x0:x1]
    return canvas,cm,(cx-icx,cy-icy)

def downscale(no, s):
    tpl,foot=legt[no]
    nw=max(3,int(round(tpl.shape[1]*s))); nh=max(3,int(round(tpl.shape[0]*s)))
    t=cv2.resize(tpl,(nw,nh),interpolation=cv2.INTER_AREA)
    f=cv2.resize(foot.astype(np.float32),(nw,nh),interpolation=cv2.INTER_AREA)>0.35
    # ensure footprint not empty / not full
    if f.sum()<8: f=cv2.resize(foot.astype(np.float32),(nw,nh),interpolation=cv2.INTER_AREA)>0.15
    return recentre(t,f)

def masked_ncc(win, tpl, mask):
    # win,tpl float HxWx3; mask bool
    if win.shape!=tpl.shape: return -1
    m=mask
    if m.sum()<8: return -1
    a=win[m]; b=tpl[m]
    a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    den=np.sqrt((a*a).sum()*(b*b).sum())
    return float((a*b).sum()/den) if den>0 else -1

def window_at(cx,cy,hx,hy):
    # centre (cx,cy) continuous base coords (pixel centres at integers); extract (2hy+1)x(2hx+1) with white pad
    icx,icy=int(round(cx)),int(round(cy))
    canv=np.full((2*hy+1,2*hx+1,3),255,np.float32)
    x0,x1=max(0,icx-hx),min(W,icx+hx+1); y0,y1=max(0,icy-hy),min(H,icy+hy+1)
    canv[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=base[y0:y1,x0:x1]
    return canv

SCALES=[0.20,0.215,0.2273,0.24,0.255]
final={}; report=[]
for _,lr in leg.iterrows():
    no=int(lr.legend_no)
    variants={s:downscale(no,s) for s in SCALES}
    candidates=[]
    sub=dedup[dedup.leg_no==no]
    pref=sub[sub.nn>15].sort_values('fid').head(25)
    if len(pref)<8: pref=sub.sort_values('fid').head(25)
    verified=[]  # (score, cx, cy, scale)
    for _,r in pref.iterrows():
        best=(-1,None,None,None)
        for s,(t,m,frac) in variants.items():
            if t is None: continue
            hy=(t.shape[0]-1)//2; hx=(t.shape[1]-1)//2
            tf=t.astype(np.float32)
            for dy in range(-4,5):
                for dx in range(-4,5):
                    win=window_at(r.px_x+dx, r.px_y+dy, hx,hy)
                    sc=masked_ncc(win,tf,m)
                    if sc>best[0]: best=(sc, r.px_x+dx+frac[0], r.px_y+dy+frac[1], s)
        if best[0]>=0.72: verified.append(best)
    if len(verified)>=3:
        scales=np.array([v[3] for v in verified]); bs=float(np.median(scales))
        # nearest in SCALES
        bs=min(SCALES,key=lambda s:abs(s-bs))
        t,m,frac=variants[bs]
        hy=(t.shape[0]-1)//2; hx=(t.shape[1]-1)//2
        stack=[]
        for sc,cx,cy,s in verified:
            if abs(s-bs)<1e-9 or True:
                # re-extract at bs template size centred at (cx-frac) integer centre approx: use cx,cy as centre (frac already added; window_at rounds)
                stack.append(window_at(cx-frac[0],cy-frac[1],hx,hy))
        med=np.median(np.array(stack),axis=0)
        newt=t.copy()
        newt[m]=med[m].astype(np.uint8)
        final[no]={"tpl":newt,"mask":m,"frac":frac,"source":f"legend-shape+map-colours (n={len(verified)})","scale":bs,"med_score":round(float(np.median([v[0] for v in verified])),3),"verified":verified}
    else:
        t,m,frac=variants[0.2273]
        final[no]={"tpl":t,"mask":m,"frac":frac,"source":f"legend-only (verified={len(verified)})","scale":0.2273,"med_score":None,"verified":verified}
    report.append((no,lr.point_attribute_name,len(sub),len(verified),final[no]["source"],final[no]["scale"],final[no]["med_score"],(final[no]["tpl"].shape[1],final[no]["tpl"].shape[0]),int(final[no]["mask"].sum())))
    print(report[-1])
pickle.dump({"final":final},open("work/final_tpl.pkl","wb"))
cols=8; s=100; rowsn=int(np.ceil(67/cols))
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255)); dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(range(1,68)):
    x=(idx%cols)*s; y=(idx//cols)*s
    dr.text((x+4,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:14]}",fill=(200,0,0))
    t=final[no]['tpl']; big=Image.fromarray(t).resize((t.shape[1]*3,t.shape[0]*3),Image.NEAREST)
    sheet.paste(big,(x+4,y+15))
    dr.text((x+4,y+84),final[no]["source"][:22],fill=(0,0,160))
sheet.save("work/final_templates_sheet.png")
print("final sheet saved")
