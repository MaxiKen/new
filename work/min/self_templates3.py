import cv2, numpy as np, json, os, pickle, sys
import geopandas as gpd, pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl
from collections import defaultdict
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
old=gpd.read_file('shapefile_results/minerals/nigeria_mineral_symbols.shp')
cases=pickle.load(open('work/min/harvest_cases.pkl','rb'))
casebyleg=defaultdict(list)
for c in cases: casebyleg[c['leg']].append(c)
HALF=19; TS=29; OFF=HALF-TS//2
SCALES=[0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95]

def get_patch(cx,cy):
    x0,y0=int(round(cx))-HALF,int(round(cy))-HALF
    if x0<0 or y0<0 or x0+2*HALF+1>BW or y0+2*HALF+1>BH: return None
    return base[y0:y0+2*HALF+1,x0:x0+2*HALF+1].copy()
def load_legend(leg):
    t=cv2.imread(f'work/min/templates/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/templates/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    return t,m
LEG={leg:load_legend(leg) for leg in range(1,68)}
_cache={}
def legend_scaled(leg,s):
    if (leg,s) not in _cache: _cache[(leg,s)]=scale_tpl(*LEG[leg],s)
    return _cache[(leg,s)]

def fit_on_patch(leg,p,maxoff=8):
    bb=(-2,0.7,0.0,0.0)
    for s in SCALES:
        t,m=legend_scaled(leg,s)
        if t.shape[0]>p.shape[0] or t.shape[1]>p.shape[1]: continue
        ncc=masked_ncc(p,t,m)
        H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
        th,tw=t.shape[:2]
        ccx=xx+tw/2-HALF; ccy=yy+th/2-HALF
        ncc=np.where((np.abs(ccx)<=maxoff)&(np.abs(ccy)<=maxoff),ncc,-1)
        i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
        if v>bb[0]: bb=(v,s,float(x+tw/2-HALF),float(y+th/2-HALF))
    return bb  # ncc, scale, dx, dy (symbol centre rel to patch centre)

def make_mask(leg,s):
    _,m=legend_scaled(leg,s)
    canvas=np.zeros((TS,TS),np.float32)
    h,w=m.shape
    if h>TS-2 or w>TS-2:
        m=cv2.resize(m,(min(w,TS-2),min(h,TS-2)),interpolation=cv2.INTER_NEAREST); h,w=m.shape
    y=(TS-h)//2; x=(TS-w)//2
    canvas[y:y+h,x:x+w]=m
    return canvas

def ncc_shift(T,M,P,dx,dy,ys,xs):
    a=T[ys,xs]; b=P[ys+OFF+dy,xs+OFF+dx]
    a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    den=np.sqrt(float((a*a).sum())*float((b*b).sum()))
    return float((a*b).sum())/den if den>1e-6 else 0.0

def build(leg,centers):
    """centers: list of (x,y) approx symbol centres. Returns dict or None."""
    patches=[]; fits=[]
    for (x,y) in centers:
        p=get_patch(x,y)
        if p is None: continue
        patches.append(p); fits.append(fit_on_patch(leg,p))
    if not patches: return None
    ok=[f for f in fits if f[0]>=0.5]
    s=float(np.median([f[1] for f in ok])) if len(ok)>=1 else 0.7
    # recentre patches by per-patch fit offsets (only where fit decent)
    patches2=[]
    for (x,y),f in zip([c for c in centers if get_patch(*c) is not None],fits):
        if f[0]>=0.45: x,y=x+f[2],y+f[3]
        p=get_patch(x,y)
        if p is not None: patches2.append(p)
    if not patches2: return None
    patches=patches2
    M=make_mask(leg,s); ys,xs=np.where(M>0)
    if len(ys)<8: return None
    T=np.median(np.stack([p[OFF:OFF+TS,OFF:OFF+TS] for p in patches]),axis=0)
    shifted=None; scores=[0.0]*len(patches)
    for r in range(3):
        shifted=[]
        for i,p in enumerate(patches):
            bb=(-2,0,0)
            for dy in range(-4,5):
                for dx in range(-4,5):
                    v=ncc_shift(T,M,p,dx,dy,ys,xs)
                    if v>bb[0]: bb=(v,dx,dy)
            scores[i]=bb[0]
            shifted.append(p[OFF+bb[2]:OFF+bb[2]+TS,OFF+bb[1]:OFF+bb[1]+TS])
        T=np.median(np.stack(shifted),axis=0)
    keep=[i for i,v in enumerate(scores) if v>=0.55]
    if len(keep)>=2:
        T=np.median(np.stack([shifted[i] for i in keep]),axis=0)
        med=float(np.median([scores[i] for i in keep]))
    else:
        med=float(np.median(scores)); keep=list(range(len(patches)))
    # validation vs legend
    val=fit_on_patch(leg, np.pad(T,((5,5),(5,5),(0,0)),mode='edge'))[0]
    y0,y1=max(0,ys.min()-1),min(TS,ys.max()+2); x0,x1=max(0,xs.min()-1),min(TS,xs.max()+2)
    tpl=T[y0:y1,x0:x1]; mm=M[y0:y1,x0:x1]
    by,bx=np.where(mm>0)
    return {'tpl':tpl,'mask':mm,'cx':(bx.min()+bx.max())/2,'cy':(by.min()+by.max())/2,
            'scale':s,'n':len(patches),'nused':len(keep),'med':med,'val':float(val)}

def harvest_centers(leg,want=8,thr=0.62):
    out=[]
    for c in casebyleg.get(leg,[]):
        x0=int(max(0,c['px']-40)); y0=int(max(0,c['py']-40))
        x1=int(min(BW,c['px']+40)); y1=int(min(BH,c['py']+40))
        win=base[y0:y1,x0:x1]
        bb=(-2,None)
        for s in SCALES:
            t,m=legend_scaled(leg,s)
            if t.shape[0]>win.shape[0] or t.shape[1]>win.shape[1]: continue
            ncc=masked_ncc(win,t,m)
            H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
            th,tw=t.shape[:2]
            ccx=xx+x0+tw/2; ccy=yy+y0+th/2
            ncc=np.where(np.hypot(ccx-c['px'],ccy-c['py'])<=27,ncc,-1)
            i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
            if v>bb[0]: bb=(v,(x+x0+tw/2,y+y0+th/2))
        if bb[1] and bb[0]>=thr: out.append(bb[1])
        if len(out)>=want: break
    return out

def legend_fallback(leg,s):
    t,m=legend_scaled(leg,s)
    by,bx=np.where(m>0)
    return {'tpl':t,'mask':m,'cx':(bx.min()+bx.max())/2,'cy':(by.min()+by.max())/2,
            'scale':s,'n':0,'nused':0,'med':0,'val':1.0}

results={}
for leg in range(1,68):
    oc=[(float(r.px_x),float(r.px_y)) for _,r in old[old.leg_no==leg].iterrows()]
    if leg==16: oc=[]  # old leg16 seeds are Copper - do not use
    res=None; src=None
    # try old centres (limit 28 for speed, prefer... all)
    if len(oc)>=3:
        res=build(leg,oc[:28]); src='self'
        if res and res['val']<0.5 and res['med']<0.8:
            hc=harvest_centers(leg)
            res2=build(leg,hc) if len(hc)>=2 else None
            if res2 and (res2['val']>res['val'] or res2['med']>res['med']): res,src=res2,'self_harvest'
    if res is None:
        hc=harvest_centers(leg)
        allc=oc+hc
        if len(allc)>=2:
            res=build(leg,allc); src='self_harvest' if hc else 'self'
        elif len(allc)==1:
            res=build(leg,allc); src='self_single'
    if res is None or (res['val']<0.42 and res['med']<0.75):
        s=res['scale'] if res else 0.75
        res=legend_fallback(leg,s); src='legend_scaled'
    if leg==65 and src=='legend_scaled':
        # keep self (orange '=' glyph is real instance form)
        res=build(leg,oc[:28]); src='self'
    cv2.imwrite(f'work/min/selftpl/leg{leg:02d}.png',np.clip(res['tpl'],0,255).astype(np.uint8))
    cv2.imwrite(f'work/min/selftpl/leg{leg:02d}_mask.png',(res['mask']*255).astype(np.uint8))
    results[leg]={'src':src,'scale':res['scale'],'n_seeds':res['n'],'n_used':res['nused'],'med_ncc':res['med'],
                  'val_vs_legend':res['val'],'tpl_wh':[int(res['tpl'].shape[1]),int(res['tpl'].shape[0])],
                  'center_xy':[float(res['cx']),float(res['cy'])]}
    print(f"leg{leg:02d} {src:14s} s={res['scale']:.2f} used={res['nused']}/{res['n']} med={res['med']:.2f} val={res['val']:.2f} wh={results[leg]['tpl_wh']}")
json.dump(results,open('work/min/selftpl_meta.json','w'),indent=1)
mont=[]
for leg in range(1,68):
    im=cv2.imread(f'work/min/selftpl/leg{leg:02d}.png')
    if im is not None: mont.append((leg,cv2.resize(im,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)))
cols=8; cellw=max(m[1].shape[1] for m in mont)+8; cellh=max(m[1].shape[0] for m in mont)+16
rowsn=(len(mont)+cols-1)//cols
canvas=np.full((rowsn*cellh,cols*cellw,3),255,np.uint8)
for k,(no,big) in enumerate(mont):
    rr,cc=divmod(k,cols); y=rr*cellh; x=cc*cellw
    canvas[y+14:y+14+big.shape[0],x+4:x+4+big.shape[1]]=big
    cv2.putText(canvas,f"{no}",(x+4,y+11),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite('work/qa/selftpl_montage3.png',canvas)
print("done")
