import numpy as np, json, time
from PIL import Image
from scipy import ndimage as ndi
t0=time.time()
d=json.load(open('work/units.json')); units=[tuple(u) for u in d['units']]
Y0,Y1,X0,X1=d['box']; H,W=d['shape']; K=len(units)
U=np.load('work/U3.npy'); h,w=U.shape
A=np.asarray(Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB'))
NODATA=(232,229,223)
pal=np.array([[0,0,0]]+units+[NODATA],dtype=np.uint8)
geo=(U>=0)
print('U3',U.shape,'geology',100*geo.mean(),'nodata',100*(~geo).mean(), flush=True)

def compose(keep_outside, flood=False):
    Uu=U.copy()
    if flood:
        idx=ndi.distance_transform_edt(~geo, return_distances=False, return_indices=True)
        Uu=Uu[tuple(idx)]
    out=np.empty((H,W,3),dtype=np.uint8); out[:,:]=NODATA
    if keep_outside:
        out[:]=A
        out[A.min(axis=2)>=246]=NODATA
    out[Y0:Y1, X0:X1]=pal[Uu+1]
    return out

Image.fromarray(compose(True)).save('NGSA_geology_isolated_v2.png', optimize=True)
print(f'[{time.time()-t0:.0f}s] v2 (legend kept, no-data tone)', flush=True)
Image.fromarray(compose(False)).save('NGSA_geology_isolated_v2_maponly.png', optimize=True)
Image.fromarray(compose(False, flood=True)).save('NGSA_geology_isolated_v2_fullyfilled.png', optimize=True)
print(f'[{time.time()-t0:.0f}s] maponly + fullyfilled', flush=True)
Image.fromarray(pal[U+1]).save('work/v2_mapcrop.png')
print(f'[{time.time()-t0:.0f}s] done', flush=True)
