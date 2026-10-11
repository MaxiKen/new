import numpy as np, json, csv
from PIL import Image
from scipy import ndimage as ndi
d=json.load(open('work/units.json')); units=[tuple(u) for u in d['units']]; K=len(units)
Y0,Y1,X0,X1=d['box']; H,W=d['shape']
LF=np.load('work/LF.npy'); Lv1=np.load('work/Lv1.npy'); Lng=np.load('work/Lng.npy')
m=np.load('work/masks.npy'); MO=np.zeros((H,W),bool); MG=np.zeros((H,W),bool)
MO[Y0:Y1,X0:X1]=m[0]; MG[Y0:Y1,X0:X1]=m[1]
ND=K
NC,NR=12,7; CW,CH=W/NC,H/NR
COLS=[chr(ord('A')+i) for i in range(NC)]
def bx(c,r): return int(round(r*CH)),int(round((r+1)*CH)),int(round(c*CW)),int(round((c+1)*CW))

def halfmaj(L):
    Hh2,Ww2=L.shape[0]//2*2, L.shape[1]//2*2
    a=L[:Hh2,:Ww2].reshape(Hh2//2,2,Ww2//2,2)
    o=np.empty((Hh2//2,Ww2//2,4),dtype=L.dtype)
    for i in range(2):
        for j in range(2): o[...,i*2+j]=a[:,i,:,j]
    o.sort(axis=2); return o[...,1]
LFh,LNh=halfmaj(LF),halfmaj(Lng)

NB=[(dc,dr) for dc in (-1,0,1) for dr in (-1,0,1) if (dc,dr)!=(0,0)]
PS=16   # corner patch size for diagonal (corner-only) neighbours
def borderstrip(c,r,dc,dr):
    """the 1px strip of cell (c,r) facing neighbour (dc,dr)"""
    y0,y1,x0,x1=bx(c,r)
    if   (dc,dr)==(0,-1): return LF[y0, x0:x1]
    elif (dc,dr)==(0,1):  return LF[y1-1, x0:x1]
    elif (dc,dr)==(-1,0): return LF[y0:y1, x0]
    elif (dc,dr)==(1,0):  return LF[y0:y1, x1-1]
    return None
def cornerpatch(c,r,dc,dr):
    """PS x PS patch at the corner of cell (c,r) pointing at diagonal neighbour (dc,dr)"""
    y0,y1,x0,x1=bx(c,r)
    ys = slice(y0,y0+PS) if dr<0 else slice(y1-PS,y1)
    xs = slice(x0,x0+PS) if dc<0 else slice(x1-PS,x1)
    return LF[ys,xs]

rows=[]
for r in range(NR):
    for c in range(NC):
        y0,y1,x0,x1=bx(c,r)
        cell=LF[y0:y1,x0:x1]; v1=Lv1[y0:y1,x0:x1]
        n=cell.size
        cnt=np.bincount(cell.ravel(),minlength=K+1)
        geopx=n-int(cnt[ND])
        # polygons per unit
        polys={}
        for k in range(K):
            mk=(cell==k)
            if mk.sum()<50: continue
            lab,nc_=ndi.label(mk)
            sz=np.asarray(ndi.sum(mk,lab,range(1,nc_+1)))
            big=sz[sz>=200]
            polys[k]=(int(mk.sum()), int(len(big)), int(sz.max()) if len(sz) else 0)
        conn=[]
        for dc,dr in NB:
            nc_,nr_=c+dc,r+dr
            if not(0<=nc_<NC and 0<=nr_<NR): continue
            dirn={(-1,-1):'NW',(0,-1):'N',(1,-1):'NE',(-1,0):'W',(1,0):'E',(-1,1):'SW',(0,1):'S',(1,1):'SE'}[(dc,dr)]
            a=borderstrip(c,r,dc,dr); b=borderstrip(nc_,nr_,-dc,-dr)
            if a is None:
                # diagonal neighbour: corner contact only
                pa=cornerpatch(c,r,dc,dr).ravel(); pb=cornerpatch(nc_,nr_,-dc,-dr).ravel()
                sa={int(k) for k in np.unique(pa) if k<ND}; sb={int(k) for k in np.unique(pb) if k<ND}
                conn.append(dict(nb=f'{COLS[nc_]}{nr_+1}',dir=dirn,corner=True,
                                 aligned={}, offset=sorted(sa&sb), term=sorted(sa-sb)))
                continue
            a=a.ravel(); b=b.ravel(); mlen=min(len(a),len(b))
            a=a[:mlen]; b=b[:mlen]
            aligned={int(k):int(((a==k)&(b==k)).sum()) for k in range(K)}
            aligned={k:v for k,v in aligned.items() if v>=3}
            sa={int(k) for k in np.unique(a) if k<ND}; sb={int(k) for k in np.unique(b) if k<ND}
            offs=sorted((sa&sb)-set(aligned))
            term=sorted(sa-sb)
            conn.append(dict(nb=f'{COLS[nc_]}{nr_+1}',dir=dirn,corner=False,
                             aligned=aligned, offset=offs, term=term))
        ch=LFh[y0//2:y1//2,x0//2:x1//2]; nh=LNh[y0//2:y1//2,x0//2:x1//2]
        both=(ch<ND)&(nh<ND)
        rows.append(dict(cell=f'{COLS[c]}{r+1}',c=c,r=r,y0=y0,y1=y1,x0=x0,x1=x1,n=n,
            geopx=geopx,nodata=n-geopx,polys=polys,conn=conn,
            ov=int(MO[y0:y1,x0:x1].sum()), gp=int(MG[y0:y1,x0:x1].sum()),
            chg=int((cell!=v1).sum()),
            ag=int(((ch==nh)&both).sum()), tot=int(both.sum()),
            fp=int(((ch<ND)&(nh>=ND)).sum()), fn=int(((ch>=ND)&(nh<ND)).sum())))
    print('row',r+1,'done',flush=True)
json.dump(dict(rows=rows,units=units,grid=[NC,NR],cw=CW,ch=CH,shape=[H,W]),open('work/report.json','w'))
print('saved work/report.json')
