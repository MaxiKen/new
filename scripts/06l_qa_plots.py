"""Per-zone QA plots: native raster + final points + printed number positions."""
import sys, csv
sys.path.insert(0,"scripts")
import numpy as np, cv2
import common as C
img=cv2.imread("work/mineral_native_map.png")
def pdf2nat(x,y):
    return (x-C.MIN_FRAME[0])*C.MIN_NATIVE_PXPT-0.5, (y-C.MIN_FRAME[1])*C.MIN_NATIVE_PXPT-0.5
F=C.MIN_FRAME
zones={
 "A":(F[0],F[1],C.ZONE_V1,C.ZONE_H_A), "B":(C.ZONE_V1,F[1],C.ZONE_V2,C.ZONE_H_E),
 "C":(C.ZONE_V2,F[1],F[2],C.ZONE_H_E), "D":(F[0],C.ZONE_H_A,C.ZONE_V1,C.ZONE_H_F),
 "E":(C.ZONE_V1,C.ZONE_H_E,F[2],C.ZONE_H_F), "F":(F[0],C.ZONE_H_F,C.ZONE_V1,F[3]),
 "G":(C.ZONE_V1,C.ZONE_H_F,F[2],F[3]),
}
recs=list(csv.DictReader(open("output/04_Tables/Mineral_Points_all.csv")))
def to_native(r):
    x,y=C.mineral_lonlat_to_pdf(float(r["LON"])-C.MIN_CORR_DX, float(r["LAT"])-C.MIN_CORR_DY)
    return pdf2nat(x,y)
for r in recs: r["nx"],r["ny"]=to_native(r)
nums=list(csv.DictReader(open("work/mineral_numbers.csv")))
import os
os.makedirs("output/03_QA_Check_Plots", exist_ok=True)
for z,(x0,y0,x1,y1) in zones.items():
    nx0,ny0=pdf2nat(x0,y0); nx1,ny1=pdf2nat(x1,y1)
    ix0,iy0,ix1,iy1=max(0,int(nx0)),max(0,int(ny0)),min(img.shape[1],int(nx1)+1),min(img.shape[0],int(ny1)+1)
    c=img[iy0:iy1,ix0:ix1].copy()
    for n in nums:
        if n["zone"]==z:
            cv2.circle(c,(int(float(n["nat_x"])-ix0),int(float(n["nat_y"])-iy0)),3,(255,120,0),1)
    for r in recs:
        if ix0<=r["nx"]<ix1 and iy0<=r["ny"]<iy1:
            col=(0,180,0) if not r["REVIEW"] else (0,140,255)
            cv2.circle(c,(int(r["nx"]-ix0),int(r["ny"]-iy0)),3,col,1)
            cv2.circle(c,(int(r["nx"]-ix0),int(r["ny"]-iy0)),0,(0,0,255),-1)
    fn=f"output/03_QA_Check_Plots/QA_Minerals_Zone{z}.png"
    cv2.imwrite(fn,c)
    print(fn, c.shape)
print("done")
