import numpy as np
# Mineral graticule label centers -> affine. Lon labels top: need label center x. Spans split; combine: use full label bbox approx from parts.
# Top lon labels: 4E center ~(328+357.4)/2=342.7 ; 6E: spans 643.2-672.6 center 657.9 ; 8E 958.4-987.8 c=973.1 ; 10E 1271.4-1305.3 c=1288.35 ; 12E 1586.6-1620.5 c=1603.55 ; 14E 1901.8-1935.7 c=1918.75
lon_lab=np.array([4,6,8,10,12,14]); x_lab=np.array([342.7,657.9,973.1,1288.35,1603.55,1918.75])
# Lat labels left (rotated): label bbox y spans: 13N: 505.6-539.5 c=522.55 ; 11N 821.1-854.4 c=837.75 ; 9N 1138.1-1167.5 c=1152.8 ; 7N 1453.3-1482.7 c=1468.0 ; 5N 1768.5-1797.9 c=1783.2
lat_lab=np.array([13,11,9,7,5]); y_lab=np.array([522.55,837.75,1152.8,1468.0,1783.2])  # pymupdf top-origin
for name,v,c in [("lon vs x",lon_lab,x_lab),("lat vs ytop",lat_lab,y_lab)]:
    A=np.vstack([c,np.ones_like(c)]).T
    sol,res,_,_=np.linalg.lstsq(A,v,rcond=None)
    pred=sol[0]*c+sol[1]
    print(name, f"deg = {sol[0]:.10f}*pt + {sol[1]:.6f}  pt/deg={1/sol[0]:.3f} resid_deg={np.round(v-pred,5)} resid_km={np.round((v-pred)*111,2)}")
# Compare transforms at raster corners & graticule intersections:
def grat(px,py): return ( (px-0)*0 + np.polyfit(x_lab,lon_lab,1)[0]*px+np.polyfit(x_lab,lon_lab,1)[1], np.polyfit(y_lab,lat_lab,1)[0]*py+np.polyfit(y_lab,lat_lab,1)[1])
def vp(px,py):
    u=(px-74.23969)/(2051.1915-74.23969); v=(py-358.7239)/(1967.7011-358.7239)
    return (2.47619+u*(15.02138-2.47619), 14.04668-v*(14.04668-3.83671))
def bf(px,py):
    yb=2160-py
    return (8.999624062683695+6.3408036208710055*(px-1104.0922160059586)/1000, 10.488502044741583+6.350936179071387*(yb-1241.0996111966826)/1000)
print("\npoint comparisons (lon,lat): GRAT vs VP vs BOUNDARYFIT, diffs in km (GRAT-VP, GRAT-BF, VP-BF)")
pts={"4E/13N":(342.7,522.55),"14E/5N":(1918.75,1783.2),"raster TL":(74.24,358.72),"raster BR":(2051.19,1967.70),"center":(1062,1163),"8E/9N":(973.1,1152.8)}
for k,(x,y) in pts.items():
    g,v,b=grat(x,y),vp(x,y),bf(x,y)
    f=lambda a: f"({a[0]:.4f},{a[1]:.4f})"
    d=lambda a,bb: f"({(a[0]-bb[0])*111*np.cos(np.radians(a[1])):+.1f},{(a[1]-bb[1])*111:+.1f})km"
    print(k,"GRAT",f(g),"VP",f(v),"BF",f(b)," G-V",d(g,v)," G-B",d(g,b)," V-B",d(v,b))
# Pink graticule line positions: x=777.0-777.6 vertical, x=1411.2-1411.8 vertical ; y=1306.6-1307.2 horiz, y~994-1002 horiz (slanted?)
# Convert those line positions under each transform: which deg do they correspond?
print("\npink lines: vertical x=777.3 ->", [round(f(777.3,1000)[0],3) for f in (grat,vp,bf)], " x=1411.5 ->",[round(f(1411.5,1000)[0],3) for f in (grat,vp,bf)])
print("horiz y=1306.9 -> lat", [round(f(1000,1306.9)[1],3) for f in (grat,vp,bf)], " y=998 ->",[round(f(1000,998)[1],3) for f in (grat,vp,bf)])
# Division lines A-G zones? pink lines likely division lines separating table zones A-G, NOT graticule! x=777 ~ lon? grat lon at 777 = ?
# Check frame rect: find thin black frame drawings large rect
