import numpy as np, pandas as pd, geopandas as gpd, cv2, pickle, sys
from PIL import Image
sys.path.insert(0,"work")
from transforms import min_lonlat_to_basepx
base=np.array(Image.open("work/mineral_base_2060x1677.png").convert("RGB")).astype(np.float32)
H,W=base.shape[:2]
baseb=cv2.GaussianBlur(base,(3,3),0.7)
fin=pickle.load(open("work/final_tpl_v3.pkl","rb"))["final"]
# valid area: admin0 rasterised in base px, dilated
adm=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp")
valid=np.zeros((H,W),np.uint8)
def draw_poly(coords):
    px=np.array([min_lonlat_to_basepx(x,y) for x,y in coords],np.int32)
    cv2.fillPoly(valid,[px.reshape(-1,1,2)],1)
for geom in adm.geometry:
    polys=geom.geoms if geom.geom_type=='MultiPolygon' else [geom]
    for p in polys:
        draw_poly(p.exterior.coords)
        # holes ignored (none significant); fillPoly overwrite order fine
valid=cv2.dilate(valid,np.ones((21,21),np.uint8)).astype(bool)
print("valid px frac",valid.mean().round(3))
def masked_ncc_map(img, tpl, mask):
    m=mask.astype(np.float32); n=m.sum()
    num=0.0; denI=0.0; denT=0.0
    for c in range(3):
        I=img[:,:,c]; T=tpl[:,:,c]*m
        A=cv2.matchTemplate(I,T,cv2.TM_CCORR)
        B=cv2.matchTemplate(I,m,cv2.TM_CCORR)
        C=cv2.matchTemplate(I*I,m,cv2.TM_CCORR)
        sT=T.sum(); sT2=(T*T).sum()
        num=num+(A-B*sT/n); denI=denI+(C-B*B/n); denT=denT+(sT2-sT*sT/n)
    den=np.sqrt(np.maximum(denI,1e-6)*max(denT,1e-6))
    return (num/den).astype(np.float32)
def subpix(mp,x,y):
    if x<1 or y<1 or x>=mp.shape[1]-1 or y>=mp.shape[0]-1: return 0.0,0.0
    fx=(mp[y,x-1]-mp[y,x+1])/(2*(mp[y,x-1]-2*mp[y,x]+mp[y,x+1])+1e-9)
    fy=(mp[y-1,x]-mp[y+1,x])/(2*(mp[y-1,x]-2*mp[y,x]+mp[y+1,x])+1e-9)
    return float(np.clip(fx,-0.5,0.5)),float(np.clip(fy,-0.5,0.5))
LOW=0.42
allrows=[]
for no in range(1,68):
    f=fin[no]; tpl=f['tpl'].astype(np.float32); mask=f['mask']
    tplb=cv2.GaussianBlur(tpl,(3,3),0.7)
    mp=masked_ncc_map(baseb,tplb,mask)
    hx=(tpl.shape[1]-1)//2; hy=(tpl.shape[0]-1)//2
    vsub=valid[hy:hy+mp.shape[0],hx:hx+mp.shape[1]]
    mpv=np.where(vsub,mp,-1)
    dil=cv2.dilate(mpv,np.ones((5,5),np.float32))
    ys,xs=np.where((mpv>=LOW)&(mpv>=dil-1e-6))
    fx0,fy0=f['frac']
    for x,y in zip(xs,ys):
        sx,sy=subpix(mpv,x,y)
        allrows.append((no,x+hx+sx+fx0,y+hy+sy+fy0,float(mpv[y,x])))
    print(no,"cand",len(ys),"max",round(float(mpv.max()),3),flush=True)
df=pd.DataFrame(allrows,columns=["leg_no","px_x","px_y","score"])
df.to_csv("work/scan_candidates.csv",index=False)
print("TOTAL candidates",len(df))
