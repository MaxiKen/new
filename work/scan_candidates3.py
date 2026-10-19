import numpy as np, pandas as pd, geopandas as gpd, cv2, pickle, sys
from PIL import Image
sys.path.insert(0,"work")
from transforms import min_lonlat_to_basepx
base=np.array(Image.open("work/mineral_base_2060x1677.png").convert("RGB")).astype(np.float32)
H,W=base.shape[:2]
baseb=cv2.GaussianBlur(base,(3,3),0.7)
fin=pickle.load(open("work/final_tpl_v3.pkl","rb"))["final"]
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
    for c in range(3):
        I=img[:,:,c]; mu=float((tpl[:,:,c]*m).sum()/n)
        Tc=(tpl[:,:,c]-mu)*m
        A=cv2.matchTemplate(I,Tc,cv2.TM_CCORR)
        Is=I-128.0
        B=cv2.matchTemplate(Is,m,cv2.TM_CCORR); C=cv2.matchTemplate(Is*Is,m,cv2.TM_CCORR)
        Braw=cv2.matchTemplate(I,m,cv2.TM_CCORR)
        means.append(Braw/n)
        num=A if num is None else num+A
        d=C-B*B/n; denI=d if denI is None else denI+d
        denT+=float((Tc*Tc).sum())
    ok=denI>(25.0*n)
    sc=np.where(ok,num/np.sqrt(np.maximum(denI,1e-6)*denT),-1.0)
    return np.clip(sc,-1,1).astype(np.float32), means
def subpix(mp,x,y):
    if x<1 or y<1 or x>=mp.shape[1]-1 or y>=mp.shape[0]-1: return 0.0,0.0
    fx=(mp[y,x-1]-mp[y,x+1])/(2*(mp[y,x-1]-2*mp[y,x]+mp[y,x+1])+1e-9)
    fy=(mp[y-1,x]-mp[y+1,x])/(2*(mp[y-1,x]-2*mp[y,x]+mp[y+1,x])+1e-9)
    return float(np.clip(fx,-0.5,0.5)),float(np.clip(fy,-0.5,0.5))
LOW=0.45; rows=[]
for no in range(1,68):
    f=fin[no]; tpl=cv2.GaussianBlur(f['tpl'].astype(np.float32),(3,3),0.7); mask=f['mask']
    mp,means=ncc_and_means(baseb,tpl,mask)
    hx=(tpl.shape[1]-1)//2; hy=(tpl.shape[0]-1)//2
    vsub=valid[hy:hy+mp.shape[0],hx:hx+mp.shape[1]]
    mpv=np.where(vsub,mp,-1)
    dil=cv2.dilate(mpv,np.ones((5,5),np.float32))
    ys,xs=np.where((mpv>=LOW)&(mpv>=dil-1e-6))
    tmean=np.array([float((tpl[:,:,c][mask]).mean()) for c in range(3)])
    fx0,fy0=f['frac']
    for x,y in zip(xs,ys):
        sx,sy=subpix(mpv,x,y)
        dmean=max(abs(float(means[c][y,x])-tmean[c]) for c in range(3))
        rows.append((no,x+hx+sx+fx0,y+hy+sy+fy0,float(mpv[y,x]),round(dmean,1)))
    print(no,len(ys),flush=True)
pd.DataFrame(rows,columns=["leg_no","px_x","px_y","score","dmean"]).to_csv("work/scan_candidates2.csv",index=False)
print("TOTAL",len(rows))
