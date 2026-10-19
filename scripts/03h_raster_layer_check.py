"""Which shift does the mineral RASTER (symbols) layer follow? Outline chamfer vs NE."""
import sys; sys.path.insert(0,"scripts")
import numpy as np, cv2, geopandas as gpd
from scipy import ndimage
from common import mineral_native_to_lonlat

img = cv2.imread("work/mineral_native_map.png")  # BGR, 2060x1677
print("native", img.shape)
# samples: sea in Gulf (x~250,y~1450), outside white (x~100,y~100), interior pale (x~1500,y~400)
for (x,y,lab) in [(250,1450,"gulf"),(100,100,"outsideNW"),(1500,400,"interiorNE"),(1000,800,"centre"),(1900,200,"chad?")]:
    print(lab, img[y,x])
sea = np.median(img[1350:1550, 80:500].reshape(-1,3), axis=0).astype(float)
print("sea median BGR", sea)
f = img.astype(float)
dist_sea = np.sqrt(((f-sea)**2).sum(axis=2))
whiteish = (img[:,:,0]>240)&(img[:,:,1]>240)&(img[:,:,2]>240)
land = ((~whiteish)&(dist_sea>45)).astype(np.uint8)
land = cv2.morphologyEx(land, cv2.MORPH_CLOSE, np.ones((5,5),np.uint8))
n,lab,stats,_ = cv2.connectedComponentsWithStats(land,8)
big = 1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
mask=(lab==big).astype(np.uint8)
cnts,_=cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# fill
filled=np.zeros_like(mask); cv2.drawContours(filled,cnts,-1,1,-1); mask=filled
cnts,_=cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cnt=max(cnts,key=cv2.contourArea).reshape(-1,2).astype(float)  # (col,row)
print(f"raster land contour pts={len(cnt)} bbox col[{cnt[:,0].min():.0f},{cnt[:,0].max():.0f}] row[{cnt[:,1].min():.0f},{cnt[:,1].max():.0f}] area_frac={mask.mean():.3f}")
cv2.imwrite("work/mineral_raster_landmask.png", mask*255)
# resample contour ~3500 pts
d=np.r_[0,np.cumsum(np.hypot(np.diff(cnt[:,0]),np.diff(cnt[:,1])))]
t=np.linspace(0,d[-1],3500)
P=np.column_stack([np.interp(t,d,cnt[:,0]), np.interp(t,d,cnt[:,1])])
lon,lat = mineral_native_to_lonlat(P[:,0], P[:,1])
pts_map=np.column_stack([lon,lat])
print("raster outline map-lonlat bounds:", pts_map.min(axis=0), pts_map.max(axis=0))
# NE EDT chamfer search
ne = gpd.read_file("work/NE_Nigeria.geojson").geometry.iloc[0]
parts=[ne.boundary] if ne.boundary.geom_type=="LineString" else list(ne.boundary.geoms)
def densify(line, step=0.01):
    n=max(100,int(line.length/step)); return np.array([(p.x,p.y) for p in [line.interpolate(dd) for dd in np.linspace(0,line.length,n)]])
NEpts=np.vstack([densify(p) for p in parts if p.length>1.0])
res=0.002; x0,x1,y0,y1=2.0,15.2,3.8,14.4
W=int((x1-x0)/res)+1; H=int((y1-y0)/res)+1
grid=np.ones((H,W),bool)
ix=np.round((NEpts[:,0]-x0)/res).astype(int); iy=np.round((NEpts[:,1]-y0)/res).astype(int)
ok=(ix>=0)&(ix<W)&(iy>=0)&(iy<H); grid[iy[ok],ix[ok]]=False
edt=ndimage.distance_transform_edt(grid)*res
def chamfer(dx,dy,pts):
    X=pts[:,0]+dx; Y=pts[:,1]+dy
    ix=np.round((X-x0)/res).astype(int); iy=np.round((Y-y0)/res).astype(int)
    v=(ix>=0)&(ix<W)&(iy>=0)&(iy<H); d=edt[iy[v],ix[v]]
    return float(np.median(d)), float(np.mean(np.sort(d)[:int(0.9*len(d))]))
for lab_,(dx,dy) in [("uncorrected",(0,0)),("border shift",(0.162,-0.002)),("town shift",(0.224,0.065))]:
    print(f"raster outline {lab_:14s} ({dx:+.3f},{dy:+.3f}): median/mean90={chamfer(dx,dy,pts_map)}")
best=None
for dx in np.arange(0.0,0.301,0.01):
    for dy in np.arange(-0.08,0.121,0.01):
        med,m90=chamfer(dx,dy,pts_map)
        if best is None or m90<best[0]: best=(m90,dx,dy,med)
print(f"RASTER coarse optimum dx={best[1]:+.3f} dy={best[2]:+.3f} mean90={best[0]:.5f} median={best[3]:.5f}")
bx,by=best[1],best[2]
for dx in np.arange(bx-0.012,bx+0.013,0.002):
    for dy in np.arange(by-0.012,by+0.013,0.002):
        med,m90=chamfer(dx,dy,pts_map)
        if m90<best[0]: best=(m90,dx,dy,med)
print(f"RASTER FINE optimum dx={best[1]:+.4f} dy={best[2]:+.4f} mean90={best[0]:.5f} (~{best[0]*111:.2f}km) median={best[3]:.5f}")
import json
json.dump(dict(raster_dx=float(best[1]), raster_dy=float(best[2]), raster_mean90=float(best[0]), raster_median=float(best[3])),
          open("work/correction_raster.json","w"), indent=1)
