import pymupdf, numpy as np, cv2, json, os
import pandas as pd
os.makedirs('work/min/templates', exist_ok=True)
HARD=[340.8,356.5,367.7,385.8,402.9,418.6,430.8,448.9,465.0,475.9,494.0,511.4,527.0,539.0,557.1,573.4,589.1,602.2,619.8,635.5,647.2,665.3,681.9,697.6,713.0,724.6,743.2,759.7,771.2,789.8,806.1,817.8,836.0,852.5,868.2,881.1,899.1,914.6,926.1,944.2,961.0,976.3,993.3,1007.3,1024.0,1039.7,1052.4,1070.4,1086.1,1097.4,1115.5,1132.8,1148.2,1161.0,1179.0,1193.1,1210.2,1221.0,1239.7,1256.6,1267.7,1286.4,1303.4,1314.4,1332.9,1358.0,1384.3]
leg=pd.read_csv('work/min/mineral_legend.csv')
PDF='Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'
doc=pymupdf.open(PDF); page=doc[0]
X0,X1,Y0,Y1=2078,2112.0,326,1404
CLIP=pymupdf.Rect(X0,Y0,X1,Y1)
SC=300/72; TARGET=1.0416667
pix=page.get_pixmap(matrix=pymupdf.Matrix(SC,SC), clip=CLIP)
img=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3).copy()
print("render300:",img.shape)
gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
mx=img.max(axis=2).astype(int); mn=img.min(axis=2).astype(int)
ink=((gray<243)|((mx-mn)>14)).astype(np.uint8)
n,lab,stats,cent=cv2.connectedComponentsWithStats(ink,8)
print("components:",n)
comps=[]
for i in range(1,n):
    x,y,w,h,a=stats[i]
    if a<6: continue
    comps.append({'x':x,'y':y,'w':w,'h':h,'a':a,'cx':cent[i][0],'cy':cent[i][1],'lab':i})
# symbol bands from ink-density profile peaks (exactly 67, in legend order)
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
sub=img[:,:131]
prof=gaussian_filter1d(ink[:,:131].sum(axis=1).astype(float),5)
pk,_=find_peaks(prof,distance=42,prominence=3)
pk=[p for p in pk if Y0+p/SC>335]
assert len(pk)==67, f"peaks={len(pk)}"
bounds=[0]
for a,b in zip(pk[:-1],pk[1:]):
    bounds.append(a+int(np.argmin(prof[a:b])))
bounds.append(img.shape[0])
rows={i:[] for i in range(67)}
for c in comps:
    if c['x']>130 or c['a']<20: continue
    j=int(np.searchsorted(bounds,c['cy']))-1
    if 0<=j<67 and abs(c['cy']-pk[j])<=36: rows[j].append(c)
print("band assignment done; comps per symbol:", [len(rows[i]) for i in range(67)])
def body_mask_300(patch):
    g=cv2.cvtColor(patch,cv2.COLOR_RGB2GRAY)
    white=(g>240).astype(np.uint8)*255
    h,w=white.shape
    im=white.copy(); mask=np.zeros((h+2,w+2),np.uint8)
    for sx,sy in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(w//2,h-1),(0,h//2),(w-1,h//2)]:
        if im[sy,sx]==255: cv2.floodFill(im,mask,(sx,sy),128,loDiff=0,upDiff=0)
    return (im!=128).astype(np.uint8)
meta={}; montage=[]
for i in range(67):
    cs=rows[i]; no=int(leg.loc[i,'legend_no']); name=leg.loc[i,'point_attribute_name']
    if not cs: print("NO COMP",no,name); continue
    x0=max(0,min(c['x'] for c in cs)-4); x1=min(img.shape[1],max(c['x']+c['w'] for c in cs)+4)
    y0=max(0,min(c['y'] for c in cs)-4); y1=min(img.shape[0],max(c['y']+c['h'] for c in cs)+4)
    patch=img[y0:y1,x0:x1]
    bm=body_mask_300(patch)
    # drop body parts not belonging to this symbol's comps (safety): keep CC of bm overlapping assigned comps
    fac=TARGET/SC
    tpl=cv2.resize(patch,None,fx=fac,fy=fac,interpolation=cv2.INTER_AREA)
    mres=cv2.resize(bm.astype(np.float32),None,fx=fac,fy=fac,interpolation=cv2.INTER_AREA)
    m=(mres>0.18).astype(np.uint8)
    by,bx=np.where(m>0)
    if len(bx)==0: print("EMPTY AFTER DS",no); continue
    xx0,xx1=max(0,bx.min()-1),min(m.shape[1],bx.max()+2)
    yy0,yy1=max(0,by.min()-1),min(m.shape[0],by.max()+2)
    tpl=tpl[yy0:yy1,xx0:xx1]; m=m[yy0:yy1,xx0:xx1]
    by,bx=np.where(m>0)
    cx=(bx.min()+bx.max())/2.0; cy=(by.min()+by.max())/2.0
    meta[no]={'name':name,'tpl_wh':[int(tpl.shape[1]),int(tpl.shape[0])],'center_xy':[float(cx),float(cy)],'body_px':int(m.sum()),'ncomp':len(cs)}
    cv2.imwrite(f"work/min/templates/leg{no:02d}.png", cv2.cvtColor(tpl,cv2.COLOR_RGB2BGR))
    cv2.imwrite(f"work/min/templates/leg{no:02d}_mask.png", m*255)
    montage.append((no,cv2.resize(tpl,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)))
json.dump(meta,open('work/min/templates_meta.json','w'),indent=1)
print("templates:",len(meta))
cols=8; cellw=max(m[1].shape[1] for m in montage)+8; cellh=max(m[1].shape[0] for m in montage)+16
rowsn=(len(montage)+cols-1)//cols
canvas=np.full((rowsn*cellh,cols*cellw,3),255,np.uint8)
for k,(no,big) in enumerate(montage):
    rr,cc=divmod(k,cols); y=rr*cellh; x=cc*cellw
    canvas[y+14:y+14+big.shape[0],x+4:x+4+big.shape[1]]=big
    cv2.putText(canvas,f"{no}",(x+4,y+11),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,0,0),1)
cv2.imwrite('work/qa/templates_montage.png',cv2.cvtColor(canvas,cv2.COLOR_RGB2BGR))
print("montage ok")
