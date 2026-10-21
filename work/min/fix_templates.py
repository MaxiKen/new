import cv2, numpy as np, json, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl
from collections import defaultdict
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
zoned=pickle.load(open('work/min/map_numbers_zoned.pkl','rb'))
nlk=defaultdict(list)
for d in zoned: nlk[(d['zone'],int(d['value']))].append((d['cx'],d['cy']))
def to_px(x,y): return ((x-74.2397)/0.959996,(y-358.724)/0.959996)
def numpx(zone,num):
    pts=nlk.get((zone,num),[])
    return to_px(*pts[0]) if pts else None
HALF=19; TS=29; OFF=HALF-TS//2
SCALES=[0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95]
def get_patch(cx,cy):
    x0,y0=int(round(cx))-HALF,int(round(cy))-HALF
    if x0<0 or y0<0 or x0+2*HALF+1>BW or y0+2*HALF+1>BH: return None
    return base[y0:y0+2*HALF+1,x0:x0+2*HALF+1].copy()
def legend(leg):
    t=cv2.imread(f'work/min/templates/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/templates/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    return t,m
_cache={}
def lscaled(leg,s):
    if (leg,s) not in _cache: _cache[(leg,s)]=scale_tpl(*legend(leg),s)
    return _cache[(leg,s)]
def fit_patch(leg,p,maxoff=13):
    bb=(-2,0.7,0.0,0.0)
    for s in SCALES:
        t,m=lscaled(leg,s)
        if t.shape[0]>p.shape[0] or t.shape[1]>p.shape[1]: continue
        ncc=masked_ncc(p,t,m)
        H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
        th,tw=t.shape[:2]
        ccx=xx+tw/2-HALF; ccy=yy+th/2-HALF
        ncc=np.where((np.abs(ccx)<=maxoff)&(np.abs(ccy)<=maxoff),ncc,-1)
        i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
        if v>bb[0]: bb=(v,s,float(x+tw/2-HALF),float(y+th/2-HALF))
    return bb
def save(leg,tpl,mask,cx,cy,src,s,med=0.0):
    cv2.imwrite(f'work/min/selftpl/leg{leg:02d}.png',np.clip(tpl,0,255).astype(np.uint8))
    cv2.imwrite(f'work/min/selftpl/leg{leg:02d}_mask.png',(mask*255).astype(np.uint8))
    meta=json.load(open('work/min/selftpl_meta.json'))
    meta[str(leg)]={'src':src,'scale':s,'n_seeds':0,'n_used':0,'med_ncc':med,'val_vs_legend':1.0,
                    'tpl_wh':[int(tpl.shape[1]),int(tpl.shape[0])],'center_xy':[float(cx),float(cy)]}
    json.dump(meta,open('work/min/selftpl_meta.json','w'),indent=1)
    print(f"leg{leg:02d} saved {src} s={s} wh={(tpl.shape[1],tpl.shape[0])}")

def build_at(leg,centers):
    """centers: approx instance centres (px). Fit legend on each, recentre, median, mask from legend."""
    fits=[]; cents=[]
    for (x,y) in centers:
        p=get_patch(x,y)
        if p is None: continue
        f=fit_patch(leg,p)
        fits.append(f); cents.append((x+f[2],y+f[3]))
        print(f" leg{leg} center {(x,y)} fit ncc={f[0]:.2f} s={f[1]} off=({f[2]:.1f},{f[3]:.1f})")
    if not cents: return False
    ok=[f for f in fits if f[0]>=0.5]
    s=float(np.median([f[1] for f in ok])) if ok else 0.7
    patches=[get_patch(x,y) for x,y in cents]
    patches=[p for p in patches if p is not None]
    frames=np.stack([p[OFF:OFF+TS,OFF:OFF+TS] for p in patches])
    T=np.median(frames,axis=0) if len(patches)>1 else frames[0]
    _,m=lscaled(leg,s)
    canvas=np.zeros((TS,TS),np.float32)
    h,w=m.shape; yy=(TS-h)//2; xx=(TS-w)//2
    canvas[yy:yy+h,xx:xx+w]=m
    ys,xs=np.where(canvas>0)
    y0,y1=max(0,ys.min()-1),min(TS,ys.max()+2); x0,x1=max(0,xs.min()-1),min(TS,xs.max()+2)
    tpl=T[y0:y1,x0:x1]; mm=canvas[y0:y1,x0:x1]
    by,bx=np.where(mm>0)
    save(leg,tpl,mm,(bx.min()+bx.max())/2,(by.min()+by.max())/2,'manual_instance',s)
    return True

# Brick Clay (9): B121 & B154 instances (offsets from number px)
c=[]
p=numpx('B',121);  c.append((p[0]-10,p[1]+9))
p=numpx('B',154);  c.append((p[0]-4,p[1]+4))
build_at(9,c)
# Molybdenite (46): A78
p=numpx('A',78); build_at(46,[(p[0]+9,p[1]+3)])
# Corundum (16): F101
p=numpx('F',101); build_at(16,[(p[0]-4,p[1]+14)])
# Bismuth (7): B123 hat glyph
p=numpx('B',123); build_at(7,[(p[0]-7,p[1]-4)])
# Sillimanite (55) & Calcite (67): legend scaled
for leg,s in [(55,0.8),(67,0.75)]:
    t,m=lscaled(leg,s)
    by,bx=np.where(m>0)
    save(leg,t,m,(bx.min()+bx.max())/2,(by.min()+by.max())/2,'legend_scaled',s)
print("done")
