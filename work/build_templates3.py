import numpy as np, pandas as pd, cv2, pickle
from PIL import Image, ImageDraw
leg=pd.read_csv("shapefile_results/minerals/mineral_legend.csv")
img=np.array(Image.open("work/legend_symbols_300dpi.png").convert("RGB")).astype(int)
ZOOM=300/72
ink=(np.max(np.abs(img-255),axis=2)>28)
n,lab,stats,cents=cv2.connectedComponentsWithStats(ink.astype(np.uint8),8)
comps=[]
for k in range(1,n):
    x,y,w,h,a=stats[k]
    if a<6 or cents[k][0]>119: continue
    comps.append((y,y+h,x,x+w,k))
comps.sort()
gap_px=2.2*ZOOM
clusters=[]; cur=[comps[0]]; curymax=comps[0][1]
for c in comps[1:]:
    if c[0]-curymax<=gap_px: cur.append(c); curymax=max(curymax,c[1])
    else: clusters.append(cur); cur=[c]; curymax=c[1]
clusters.append(cur)
assert len(clusters)==67
clusters=clusters[1:]  # drop EXPLANATIONS 'E' fragment -> 66 clusters for 67 legs (one merged pair)
# split the merged cluster (height >18pt) at largest internal vertical gap between comps sorted by y
out=[]
for cl in clusters:
    y0=min(c[0] for c in cl); y1=max(c[1] for c in cl)
    if (y1-y0)/ZOOM>18:
        cl_sorted=sorted(cl)
        gaps=[(cl_sorted[i+1][0]-max(c[1] for c in cl_sorted[:i+1]), i) for i in range(len(cl_sorted)-1)]
        gi=max(gaps)[1]
        print(f"splitting merged cluster h={(y1-y0)/ZOOM:.1f}pt at comp index {gi}, gaps={gaps}")
        out.append(cl_sorted[:gi+1]); out.append(cl_sorted[gi+1:])
    else:
        out.append(cl)
clusters=out
print(f"final clusters: {len(clusters)}")
assert len(clusters)==67
legend_tpl={}
for idx,cl in enumerate(clusters):
    legno=idx+1
    ks=[c[4] for c in cl]
    mask=np.isin(lab,ks)
    ys,xs=np.where(mask)
    pad=int(1.2*ZOOM)
    X0,X1=max(0,xs.min()-pad),min(img.shape[1],xs.max()+pad+1); Y0,Y1=max(0,ys.min()-pad),min(img.shape[0],ys.max()+pad+1)
    tpl=img[Y0:Y1,X0:X1].astype(np.uint8); m=mask[Y0:Y1,X0:X1]
    inv=(~m).astype(np.uint8); nn,ll=cv2.connectedComponents(inv,4)
    border=set(np.unique(np.concatenate([ll[0,:],ll[-1,:],ll[:,0],ll[:,-1]])))-{0}
    interior=np.isin(ll,[v for v in range(1,nn) if v not in border])
    foot=m|interior
    legend_tpl[legno]=(tpl,foot)
    print(f"leg{legno:2d} {leg[leg.legend_no==legno].point_attribute_name.values[0]:28s} size_pt {tpl.shape[1]/ZOOM:.1f}x{tpl.shape[0]/ZOOM:.1f}")
pickle.dump({"legend_tpl":legend_tpl},open("work/legend_tpl.pkl","wb"))
# sheet at 300dpi templates scaled to uniform cell (preserve aspect, enlarge NEAREST from downscaled 0.25 for preview of map-scale appearance)
cols=8; s=96; rowsn=int(np.ceil(67/cols))
sheet=Image.new("RGB",(cols*s,rowsn*s),(255,255,255)); dr=ImageDraw.Draw(sheet)
for idx,no in enumerate(sorted(legend_tpl)):
    tpl,foot=legend_tpl[no]
    small=cv2.resize(tpl,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)
    big=Image.fromarray(small).resize((small.shape[1]*3,small.shape[0]*3),Image.NEAREST)
    x=(idx%cols)*s; y=(idx//cols)*s
    sheet.paste(big,(x+4,y+16)); dr.text((x+4,y+3),f"{no} {leg[leg.legend_no==no].point_attribute_name.values[0][:15]}",fill=(200,0,0))
sheet.save("work/legend_templates_sheet.png")
print("sheet v2 saved")
