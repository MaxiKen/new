import numpy as np, pandas as pd, geopandas as gpd, cv2, pickle
from PIL import Image
base=np.array(Image.open("work/mineral_base_2060x1677.png").convert("RGB")).astype(np.float32)
H,W=base.shape[:2]
baseb=cv2.GaussianBlur(base,(3,3),0.7)
fin=pickle.load(open("work/final_tpl_v3.pkl","rb"))["final"]
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
def ncc_map(img,tpl,mask):
    m=mask.astype(np.float32); n=float(m.sum())
    num=None; denI=None; denT=0.0
    for c in range(3):
        I=img[:,:,c]; mu=float((tpl[:,:,c]*m).sum()/n)
        Tc=(tpl[:,:,c]-mu)*m
        A=cv2.matchTemplate(I,Tc,cv2.TM_CCORR)
        Is=I-128.0
        B=cv2.matchTemplate(Is,m,cv2.TM_CCORR); C=cv2.matchTemplate(Is*Is,m,cv2.TM_CCORR)
        num=A if num is None else num+A
        d=C-B*B/n; denI=d if denI is None else denI+d
        denT+=float((Tc*Tc).sum())
    ok=denI>(25.0*n)
    sc=np.where(ok, num/np.sqrt(np.maximum(denI,1e-6)*denT), -1.0)
    return np.clip(sc,-1,1).astype(np.float32)
def direct(cx,cy,tpl,mask):
    hx=(tpl.shape[1]-1)//2; hy=(tpl.shape[0]-1)//2
    icx,icy=int(round(cx)),int(round(cy))
    win=np.full(tpl.shape,255,np.float32)
    x0,x1=max(0,icx-hx),min(W,icx+hx+1); y0,y1=max(0,icy-hy),min(H,icy+hy+1)
    win[y0-icy+hy:y1-icy+hy,x0-icx+hx:x1-icx+hx]=baseb[y0:y1,x0:x1]
    a=win[mask]; b=tpl[mask]; a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    return float((a*b).sum()/np.sqrt((a*a).sum()*(b*b).sum()))
for no in [12,31,33,27]:
    f=fin[no]; tpl=cv2.GaussianBlur(f['tpl'].astype(np.float32),(3,3),0.7); mask=f['mask']
    mp=ncc_map(baseb,tpl,mask)
    hx=(tpl.shape[1]-1)//2; hy=(tpl.shape[0]-1)//2
    sub=minr[minr.leg_no==no].sort_values('fid').head(6)
    print(f"class {no} mapmax {mp.max():.3f}")
    for _,r in sub.iterrows():
        x,y=int(round(r.px_x)),int(round(r.px_y))
        ms=mp[max(0,y-hy-2):y-hy+3, max(0,x-hx-2):x-hx+3].max()
        ds=max(direct(r.px_x+dx,r.px_y+dy,tpl,mask) for dx in(-2,-1,0,1,2) for dy in(-2,-1,0,1,2))
        print(f"  fid{int(r.fid)} map {ms:.3f} direct {ds:.3f}")
