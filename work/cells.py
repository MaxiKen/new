import numpy as np, json, time
from PIL import Image
from scipy import ndimage as ndi
t0=time.time()
d=json.load(open('work/units.json')); units=[tuple(u) for u in d['units']]
Y0,Y1,X0,X1=d['box']; H,W=d['shape']; K=len(units)
U=np.load('work/U3.npy'); h,w=U.shape
masks=np.load('work/masks.npy'); overlay,gap,nodata=masks
ISO='NGSA_map_geology_legend_isolated.png'; NGS='pic NGSA geological-map-of-nigeria-.jpg'
DY,DX=96,120
ND=K                                        # canonical no-data label

LF=np.full((H,W),ND,dtype=np.int16); LF[Y0:Y1,X0:X1]=np.where(U>=0,U,ND)
np.save('work/LF.npy',LF)
MO=np.zeros((H,W),bool); MO[Y0:Y1,X0:X1]=overlay
MG=np.zeros((H,W),bool); MG[Y0:Y1,X0:X1]=gap

pal=np.array(units,dtype=np.int32)
def nearest(img, median=0, wt=246):
    img=img.astype(np.uint8)
    if median:
        img=np.stack([ndi.median_filter(img[...,c],size=median) for c in range(3)],axis=2)
    f=img.astype(np.int32)
    Hh,Ww,_=f.shape; out=np.empty((Hh,Ww),dtype=np.int16)
    for rs in range(0,Hh,180):
        re=min(Hh,rs+180); blk=f[rs:re].reshape(-1,3)
        best=np.full(len(blk),1<<30,dtype=np.int32); lab=np.zeros(len(blk),dtype=np.int16)
        for k in range(K):
            dd=blk-pal[k]; dd=(dd*dd).sum(axis=1)
            m=dd<best; best[m]=dd[m]; lab[m]=k
        out[rs:re]=lab.reshape(re-rs,Ww)
    out[img.min(axis=2)>=wt]=ND
    return out

A=np.asarray(Image.open(ISO).convert('RGB'))
B=np.asarray(Image.open(NGS).convert('RGB').crop((DX,DY,DX+W,DY+H)))
Lv1=nearest(A);                    print(f'[{time.time()-t0:.0f}s] v1 labelled',flush=True)
Lng=nearest(B, median=3);          print(f'[{time.time()-t0:.0f}s] ngsa labelled (denoised)',flush=True)
np.save('work/Lv1.npy',Lv1); np.save('work/Lng.npy',Lng)

# half-resolution majority maps -> fair structural comparison
def halfmaj(L):
    Hh,Ww=L.shape; Hh2,Ww2=Hh//2*2, Ww//2*2
    a=L[:Hh2,:Ww2].reshape(Hh2//2,2,Ww2//2,2)
    out=np.empty((Hh2//2,Ww2//2,4),dtype=L.dtype)
    for i in range(2):
        for j in range(2): out[...,i*2+j]=a[:,i,:,j]
    out.sort(axis=2)
    return out[...,1]                                   # conservative: 2nd smallest of 4
LFh,L1h,LNh=halfmaj(LF),halfmaj(Lv1),halfmaj(Lng)

NC,NR=12,7; CW=W/NC; CH=H/NR
cols=[chr(ord('A')+i) for i in range(NC)]
def bx(c,r):
    return int(round(r*CH)),int(round((r+1)*CH)),int(round(c*CW)),int(round((c+1)*CW))

rowsout=[]; conns=[]
for r in range(NR):
    for c in range(NC):
        y0,y1,x0,x1=bx(c,r)
        cell=LF[y0:y1,x0:x1]; v1=Lv1[y0:y1,x0:x1]; ng=Lng[y0:y1,x0:x1]
        n=cell.size
        cnt=np.bincount(cell.ravel(),minlength=K+1)
        geopx=n-int(cnt[K])
        tops=sorted([(int(cnt[k]),k) for k in range(K) if cnt[k]>0],reverse=True)
        chg=int((cell!=v1).sum())
        ov=int(MO[y0:y1,x0:x1].sum()); gp=int(MG[y0:y1,x0:x1].sum())
        ch=LFh[y0//2:y1//2, x0//2:x1//2]; nh=LNh[y0//2:y1//2, x0//2:x1//2]; vh=L1h[y0//2:y1//2, x0//2:x1//2]
        b2=(ch<K); bn=(nh<K)
        both=b2&bn
        ag=int(((ch==nh)&both).sum()); tot=int(both.sum())
        fp=int((b2&(~bn)).sum()); fn=int(((~b2)&bn).sum())
        ag1=int((((vh==nh)&(vh<K)&(nh<K))).sum()); tot1=int(((vh<K)&(nh<K)).sum())
        rowsout.append(dict(cell=f'{cols[c]}{r+1}',c=c,r=r,n=n,geo=geopx,nodata=n-geopx,
                            nuni=len(tops),tops=tops[:6],chg=chg,ov=ov,gp=gp,
                            ag=ag,tot=tot,fp=fp,fn=fn,ag1=ag1,tot1=tot1))
        for dn,(dc,dr) in {'E':(1,0),'S':(0,1)}.items():
            if not(0<=c+dc<NC and 0<=r+dr<NR): continue
            ny0,ny1,nx0,nx1=bx(c+dc,r+dr); nb=LF[ny0:ny1,nx0:nx1]
            if dn=='E': a=cell[:,-1]; b=nb[:,0]
            else:       a=cell[-1,:];  b=nb[0,:]
            a=np.asarray(a).ravel(); b=np.asarray(b).ravel()
            shared={int(k):int(((a==k)&(b==k)).sum()) for k in range(K)}
            shared={k:v for k,v in shared.items() if v>=3}
            au=sorted({int(k) for k in np.unique(a) if k<K}); bu=sorted({int(k) for k in np.unique(b) if k<K})
            dang=sorted(set(au)&set(bu)-set(shared))
            conns.append(dict(a=f'{cols[c]}{r+1}',b=f'{cols[c+dc]}{r+1+dr}',dir=dn,
                              shared=shared,dangling=dang,au=au,bu=bu))
        print(f'  [{time.time()-t0:.0f}s] {cols[c]}{r+1}',flush=True)
json.dump(dict(rows=rowsout,conns=conns,units=units,grid=[NC,NR],cw=CW,ch=CH),open('work/cells.json','w'))
print(f'[{time.time()-t0:.0f}s] ALL CELLS DONE',flush=True)
