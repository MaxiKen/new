import cv2, numpy as np, json, sys
import geopandas as gpd
sys.path.insert(0,'work/min')
from ncc import masked_ncc
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
g=gpd.read_file('deliverables_flat/nigeria_mineral_occurrences.shp')
def score_peak(t,m,bcx,bcy,cx,cy,R=2.5):
    WR=int(max(t.shape[:2])/2+R+4)
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    return float(np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=R,ncc,-1).max())
out={}
for L in range(1,68):
    if L==49: continue
    v4t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png')
    if v4t is None: continue
    v4t=v4t.astype(np.float32)
    v4m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
    th,tw=v4t.shape[:2]
    ys,xs=np.where(v4m>0); bcx4=(xs.min()+xs.max())/2; bcy4=(ys.min()+ys.max())/2
    seeds=g[(g.leg_no==L)&(g.id_score>=0.85)]
    patches=[]; centres=[]
    for _,r in seeds.iterrows():
        cx,cy=float(r.px_x),float(r.px_y)
        x0,y0=int(round(cx-bcx4)),int(round(cy-bcy4))
        if x0<0 or y0<0 or x0+tw>BW or y0+th>BH: continue
        patches.append(base[y0:y0+th,x0:x0+tw].copy()); centres.append((cx,cy))
    if len(patches)>=3:
        diffs=[]
        for p in patches:
            outside=p[v4m==0]
            bg=np.median(outside,axis=0) if len(outside)>=10 else np.median(np.concatenate([p[0],p[-1],p[:,0],p[:,-1]]),axis=0)
            diffs.append(np.abs(p-bg).max(axis=2))
        med=np.median(np.stack(diffs),axis=0)
        ink=(med>40).astype(np.uint8)
        n,lab,st,cent=cv2.connectedComponentsWithStats(ink,8)
        for i in range(1,n):
            if st[i][4]<3: ink[lab==i]=0
        if ink.sum()>=5:
            ys,xs=np.where(ink>0)
            bcx=(xs.min()+xs.max())/2; bcy=(ys.min()+ys.max())/2
            src='consensus'
        else:
            bcx,bcy=bcx4,bcy4; src='v4fallback'
    else:
        outside=v4t[v4m==0]
        bg=np.median(outside,axis=0) if len(outside)>=10 else np.median(np.concatenate([v4t[0],v4t[-1]]),axis=0)
        ink=(np.abs(v4t-bg).max(axis=2)>40)&(v4m>0)
        if ink.sum()>=5:
            ys,xs=np.where(ink)
            bcx=(xs.min()+xs.max())/2; bcy=(ys.min()+ys.max())/2
        else: bcx,bcy=bcx4,bcy4
        src='tpl_ink'
        centres=[(float(r.px_x),float(r.px_y)) for _,r in g[g.leg_no==L].iterrows()]
    bias=(bcx-bcx4,bcy-bcy4)
    if centres:
        sc=[score_peak(v4t,v4m,bcx,bcy,cx+bias[0],cy+bias[1]) for cx,cy in centres]
        p5,p10,p50=[float(np.percentile(sc,q)) for q in (5,10,50)]
    else:
        sc=[]; p5=p10=p50=None
    out[str(L)]={'center_xy':[float(bcx),float(bcy)],'bias':[float(bias[0]),float(bias[1])],
                 'n':len(centres),'self_p5':p5,'self_p10':p10,'self_p50':p50,'src':src}
    print(f"leg{L:02d} n={len(centres):3d} bias=({bias[0]:+.1f},{bias[1]:+.1f}) self p5={p5} p50={p50} {src}",flush=True)
json.dump(out,open('work/min/centres6.json','w'),indent=1)
# strip-scale check: self scores by row band for big legs
print("\nstrip check (median self-score by 240-row band):")
for L in [12,26,34,31]:
    if str(L) not in out: continue
    v4t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
    v4m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
    bcx,bcy=out[str(L)]['center_xy']; bias=out[str(L)]['bias']
    bands={}
    for _,r in g[(g.leg_no==L)&(g.id_score>=0.85)].iterrows():
        b=int(r.px_y//240)
        bands.setdefault(b,[]).append(score_peak(v4t,v4m,bcx,bcy,r.px_x+bias[0],r.px_y+bias[1]))
    print(f" leg{L}:",{b:(len(v),round(float(np.median(v)),3)) for b,v in sorted(bands.items())})
# montage: v4 templates, blue=v4 centre, red=corrected centre
cells=[]
for L in range(1,68):
    if str(L) not in out: continue
    t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png')
    v4m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0)
    ys,xs=np.where(v4m>0); bcx4=(xs.min()+xs.max())/2; bcy4=(ys.min()+ys.max())/2
    bcx,bcy=out[str(L)]['center_xy']
    cell=np.full((36,36,3),255,np.uint8)
    oy,ox=18-int(round(bcy4)),18-int(round(bcx4))
    y0,y1=max(0,oy),min(36,oy+t.shape[0]); x0,x1=max(0,ox),min(36,ox+t.shape[1])
    if y1>y0 and x1>x0: cell[y0:y1,x0:x1]=t[y0-oy:y1-oy,x0-ox:x1-ox]
    cv2.drawMarker(cell,(18,18),(255,0,0),cv2.MARKER_TILTED_CROSS,9,1)   # blue X = old
    cv2.drawMarker(cell,(18+int(round(bcx-bcx4)),18+int(round(bcy-bcy4))),(0,0,255),cv2.MARKER_CROSS,7,1)  # red + = new
    cv2.putText(cell,str(L),(1,10),cv2.FONT_HERSHEY_SIMPLEX,0.36,(0,0,255),1)
    cells.append(cv2.resize(cell,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST))
cols=11; H=cells[0].shape[0]; W=cells[0].shape[1]
rows=(len(cells)+cols-1)//cols
canvas=np.full((H*rows,W*cols,3),255,np.uint8)
for i,c in enumerate(cells):
    r,cc=divmod(i,cols); canvas[r*H:(r+1)*H,cc*W:(cc+1)*W]=c
cv2.imwrite('work/qa/centres6_montage.png',canvas)
print("montage saved")
