import numpy as np, pickle, json, time
from PIL import Image
from scipy import ndimage as ndi
t0=time.time()
ISO='NGSA_map_geology_legend_isolated.png'
A=np.asarray(Image.open(ISO).convert('RGB'))
H,W,_=A.shape
Y0,Y1,X0,X1=93,3483,20,4193                 # neatline interior
M=A[Y0:Y1, X0:X1]; h,w,_=M.shape
print('map interior', M.shape, flush=True)

# ---- 1. exact-colour census + 7x7 core test ----
f=M.reshape(-1,3)
vals,cts=np.unique(f,axis=0,return_counts=True)
o=np.argsort(-cts)[:260]; top=vals[o]; topc=cts[o]
key=f[:,0].astype(np.int64)*65536+f[:,1].astype(np.int32)*256+f[:,2]
tk =top[:,0].astype(np.int64)*65536+top[:,1].astype(np.int32)*256+top[:,2]
sorter=np.argsort(tk); Ls=np.full(f.shape[0],-1,dtype=np.int32)
pos=np.clip(np.searchsorted(tk[sorter],key),0,len(tk)-1)
hit=tk[sorter][pos]==key; Ls[hit]=sorter[pos][hit]
L=Ls.reshape(h,w)
core=np.ones((h,w),bool)
for dy in range(-3,4):
    for dx in range(-3,4):
        if dy==0 and dx==0: continue
        ys0,ys1=max(0,-dy),min(h,h-dy); xs0,xs1=max(0,-dx),min(w,w-dx)
        s=np.zeros((h,w),bool)
        s[ys0:ys1,xs0:xs1]=(L[ys0:ys1,xs0:xs1]==L[ys0+dy:ys1+dy,xs0+dx:xs1+dx])&(L[ys0:ys1,xs0:xs1]>=0)
        core&=s
core&=(L>=0)
cc=np.bincount(L[core].ravel()+1,minlength=len(top)+1)[1:]

# ---- 2. units ----
units=[]
for i in range(len(top)):
    n=int(topc[i]); c=int(cc[i]); rgb=tuple(int(v) for v in top[i])
    if n<4000 or min(rgb)>=248 or c/max(n,1)<0.35: continue
    units.append(dict(rgb=rgb,n=n,core=c/n))
units.sort(key=lambda u:-u['n'])
print(f'[{time.time()-t0:.0f}s] {len(units)} units', flush=True)

ucol=np.array([u['rgb'] for u in units],dtype=np.int16)
uk=ucol[:,0].astype(np.int64)*65536+ucol[:,1].astype(np.int32)*256+ucol[:,2]
order=np.argsort(uk); uks=uk[order]
pos=np.clip(np.searchsorted(uks,key),0,len(uks)-1); hit=uks[pos]==key
U=np.full(f.shape[0],-1,dtype=np.int16); U[hit]=order[pos][hit]
U=U.reshape(h,w)

whiteish=(M.min(axis=2)>=248)
overlay=(~whiteish)&(U<0)                     # graticule / text / roads / AA
print(f'[{time.time()-t0:.0f}s] unit {100*(U>=0).mean():.2f}%  white {100*whiteish.mean():.2f}%  overlay {100*overlay.mean():.2f}%', flush=True)

# ---- 3. white components: small=>gap(to fill), large=>no-data ----
lab,nc=ndi.label(whiteish)
sizes=np.asarray(ndi.sum(whiteish,lab,range(1,nc+1)))
small=np.isin(lab,np.nonzero(sizes<6000)[0]+1)
gap=whiteish&small; nodata=whiteish&(~small)
print(f'[{time.time()-t0:.0f}s] white comps={nc} gap={int(gap.sum())} nodata={int(nodata.sum())}', flush=True)

# ---- 4. fill overlay+gap from nearest known unit ----
#     only where the mark actually sits on/next to mapped geology; marks out in the
#     unmapped sheet area (e.g. graticule running across blank ground) become no-data,
#     otherwise the flood fill paints spurious coloured streaks there.
DMAX=10
dist=ndi.distance_transform_edt(U<0)
fillable=overlay&(dist<=DMAX)
stranded=overlay&(dist>DMAX)
nodata=nodata|stranded
print(f'[{time.time()-t0:.0f}s] overlay: {int(fillable.sum())} on geology (fill), {int(stranded.sum())} stranded (-> no data)', flush=True)
del dist
Uf=U.copy()
todo=fillable|gap
idx=ndi.distance_transform_edt(~(Uf>=0), return_distances=False, return_indices=True)
Uf=Uf[tuple(idx)]
del idx
# ---- 5. de-speckle (only inside geology) ----
geo=~nodata
lab2,n2=ndi.label(geo)
sz2=np.asarray(ndi.sum(np.ones_like(lab2),lab2,range(1,n2+1)))
tiny=np.isin(lab2,np.nonzero(sz2<300)[0]+1)&geo
print(f'[{time.time()-t0:.0f}s] speckle<300px: {int(tiny.sum())}', flush=True)
Uf2=Uf.copy(); Uf2[tiny]=-1
if (Uf2<0).any():
    idx=ndi.distance_transform_edt(~(Uf2>=0), return_distances=False, return_indices=True)
    Uf2=Uf2[tuple(idx)]

# ---- 6. categorical 3x3 median on boundaries, 2 passes ----
def boundary(Lm):
    b=np.zeros(Lm.shape,bool)
    for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
        ys0,ys1=max(0,-dy),min(h,h-dy); xs0,xs1=max(0,-dx),min(w,w-dx)
        b[ys0:ys1,xs0:xs1]|=(Lm[ys0:ys1,xs0:xs1]!=Lm[ys0+dy:ys1+dy,xs0+dx:xs1+dx])
    return b
Us=Uf2.copy()
for it in range(2):
    b=boundary(Us)&geo
    ys,xs=np.nonzero(b)
    m=(ys>=1)&(ys<h-1)&(xs>=1)&(xs<w-1)
    ys=ys[m]; xs=xs[m]
    patch=np.stack([Us[ys+dy,xs+dx] for dy in (-1,0,1) for dx in (-1,0,1)],axis=1)
    patch.sort(axis=1); Us[ys,xs]=patch[:,4]
    print(f'[{time.time()-t0:.0f}s] smooth {it+1}: {len(ys)} px', flush=True)

Us[nodata]=-2                      # -2 = no data
np.save('work/U3.npy',Us.astype(np.int16))
np.save('work/masks.npy', np.stack([overlay,gap,nodata]).astype(np.bool_))
json.dump(dict(units=[u['rgb'] for u in units], box=[Y0,Y1,X0,X1], shape=[H,W],
               stats=dict(units=[u['n'] for u in units])), open('work/units.json','w'), indent=1)
print(f'[{time.time()-t0:.0f}s] DONE. units={len(units)}', flush=True)
