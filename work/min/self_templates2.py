import cv2, numpy as np, json, os, pickle, sys
import geopandas as gpd, pandas as pd
sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl
os.makedirs('work/min/selftpl',exist_ok=True)
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
old=gpd.read_file('shapefile_results/minerals/nigeria_mineral_symbols.shp')
cases=pickle.load(open('work/min/harvest_cases.pkl','rb'))
from collections import defaultdict
casebyleg=defaultdict(list)
for c in cases: casebyleg[c['leg']].append(c)
HALF=19; TS=29; OFF=HALF-TS//2
SCALES=[0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9]

def get_patch(cx,cy):
    x0,y0=int(round(cx))-HALF,int(round(cy))-HALF
    if x0<0 or y0<0 or x0+2*HALF+1>BW or y0+2*HALF+1>BH: return None
    return base[y0:y0+2*HALF+1,x0:x0+2*HALF+1].copy()
def load_legend(leg):
    t=cv2.imread(f'work/min/templates/leg{leg:02d}.png').astype(np.float32)
    m=cv2.imread(f'work/min/templates/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    return t,m
LEG={leg:load_legend(leg) for leg in range(1,68)}
LSCALE={}
def legend_scaled(leg,s):
    if (leg,s) not in LSCALE: LSCALE[(leg,s)]=scale_tpl(*LEG[leg],s)
    return LSCALE[(leg,s)]

def fit_scale_on_patches(leg,patches):
    best=[]
    for p in patches:
        bb=(-2,0.7,0,0)
        for s in SCALES:
            t,m=legend_scaled(leg,s)
            if t.shape[0]>p.shape[0] or t.shape[1]>p.shape[1]: continue
            ncc=masked_ncc(p,t,m)
            # peak must lie so template centre within +-7 of patch centre
            H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
            th,tw=t.shape[:2]
            ccx=xx+tw/2-HALF; ccy=yy+th/2-HALF
            ncc=np.where((np.abs(ccx)<=7)&(np.abs(ccy)<=7),ncc,-1)
            i=np.argmax(ncc); v=float(ncc.ravel()[i]); y,x=np.unravel_index(i,ncc.shape)
            if v>bb[0]: bb=(v,s,x+tw/2-HALF,y+th/2-HALF)
        best.append(bb)
    ok=[b for b in best if b[0]>=0.5]
    if len(ok)>=2:
        return float(np.median([b[1] for b in ok])), ok
    return 0.7, ok

def make_mask(leg,s):
    _,m=legend_scaled(leg,s)
    canvas=np.zeros((TS,TS),np.float32)
    h,w=m.shape
    if h>TS or w>TS:
        m=cv2.resize(m,(min(w,TS-2),min(h,TS-2)),interpolation=cv2.INTER_NEAREST); h,w=m.shape
    y=(TS-h)//2; x=(TS-w)//2
    canvas[y:y+h,x:x+w]=m
    return canvas

def ncc_shift(T,M,P,dx,dy):
    ys,xs=np.where(M>0)
    a=T[ys,xs]; b=P[ys+OFF+dy,xs+OFF+dx]
    a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    den=np.sqrt(float((a*a).sum())*float((b*b).sum()))
    return float((a*b).sum())/den if den>1e-6 else 0.0

def build_from_patches(leg,patches,s):
    M=make_mask(leg,s)
    frames=np.stack([p[OFF:OFF+TS,OFF:OFF+TS] for p in patches])
    T=np.median(frames,axis=0)
    shifted=None; scores=[0]*len(patches)
    for r in range(3):
        shifted=[]; 
        for i,p in enumerate(patches):
            bb=(-2,0,0)
            for dy in range(-5,6):
                for dx in range(-5,6):
                    v=ncc_shift(T,M,p,dx,dy)
                    if v>bb[0]: bb=(v,dx,dy)
            scores[i]=bb[0]
            shifted.append(p[OFF+bb[2]:OFF+bb[2]+TS,OFF+bb[1]:OFF+bb[1]+TS])
        T=np.median(np.stack(shifted),axis=0)
    keep=[i for i,v in enumerate(scores) if v>=0.55]
    if len(keep)>=2:
        T=np.median(np.stack([shifted[i] for i in keep]),axis=0)
    ys,xs=np.where(M>0)
    y0,y1=max(0,ys.min()-1),min(TS,ys.max()+2); x0,x1=max(0,xs.min()-1),min(TS,xs.max()+2)
    tpl=T[y0:y1,x0:x1]; mm=M[y0:y1,x0:x1]
    by,bx=np.where(mm>0)
    cx=(bx.min()+bx.max())/2; cy=(by.min()+by.max())/2
    return tpl,mm,cx,cy,len(keep),float(np.median([scores[i] for i in keep])) if keep else 0.0

def harvest_seeds(leg,want=8):
    seeds=[]
    for c in casebyleg.get(leg,[]):
        p=get_patch(c['px'],c['py'])
        if p is None: continue
        # search around number: bigger window
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
            if v>bb[0]: bb=(v,(x+x0+tw/2,y+y0+th/2,s))
        if bb[1] and bb[0]>=0.62:
            seeds.append((bb[1][0],bb[1][1]))
        if len(seeds)>=want: break
    return seeds

results={}; scales_found=[]
order=list(range(1,68))
# pass 1: legs with >=3 old seeds
for leg in order:
    seeds=old[old.leg_no==leg]
    patches=[]
    for _,r in seeds.iterrows():
        p=get_patch(r.px_x,r.px_y)
        if p is not None: patches.append(p)
    if len(patches)>=3:
        s,ok=fit_scale_on_patches(leg,patches[:25])
        scales_found.append(s)
        tpl,mm,cx,cy,nused,med=build_from_patches(leg,patches,s)
        cv2.imwrite(f'work/min/selftpl/leg{leg:02d}.png',np.clip(tpl,0,255).astype(np.uint8))
        cv2.imwrite(f'work/min/selftpl/leg{leg:02d}_mask.png',(mm*255).astype(np.uint8))
        results[leg]={'src':'self','scale':s,'n_seeds':len(patches),'n_used':nused,'med_ncc':med,
                      'tpl_wh':[int(tpl.shape[1]),int(tpl.shape[0])],'center_xy':[float(cx),float(cy)]}
        print(f"leg{leg:02d} self s={s} used={nused}/{len(patches)} med={med:.2f} wh={results[leg]['tpl_wh']}")
global_s=float(np.median(scales_found)) if scales_found else 0.7
print("global scale median:",global_s)
# pass 2: remaining legs via harvest
for leg in order:
    if leg in results: continue
    seeds=old[old.leg_no==leg]
    patches=[]
    for _,r in seeds.iterrows():
        p=get_patch(r.px_x,r.px_y)
        if p is not None: patches.append(p)
    hs=harvest_seeds(leg,want=8-len(patches))
    for (x,y) in hs:
        p=get_patch(x,y)
        if p is not None: patches.append(p)
    if len(patches)>=2:
        s,ok=fit_scale_on_patches(leg,patches)
        tpl,mm,cx,cy,nused,med=build_from_patches(leg,patches,s)
        src='self_harvest'
    elif len(patches)==1:
        s,ok=fit_scale_on_patches(leg,patches)
        tpl,mm,cx,cy,nused,med=build_from_patches(leg,patches,s)
        src='self_single'
    else:
        s=global_s
        t,m=legend_scaled(leg,s)
        tpl,mm=t,m
        by,bx=np.where(mm>0); cx=(bx.min()+bx.max())/2; cy=(by.min()+by.max())/2
        nused=0; med=0; src='legend_scaled'
    cv2.imwrite(f'work/min/selftpl/leg{leg:02d}.png',np.clip(tpl,0,255).astype(np.uint8))
    cv2.imwrite(f'work/min/selftpl/leg{leg:02d}_mask.png',(mm*255).astype(np.uint8))
    results[leg]={'src':src,'scale':s,'n_seeds':len(patches),'n_used':nused,'med_ncc':med,
                  'tpl_wh':[int(tpl.shape[1]),int(tpl.shape[0])],'center_xy':[float(cx),float(cy)]}
    print(f"leg{leg:02d} {src} s={s} patches={len(patches)} used={nused} med={med:.2f} wh={results[leg]['tpl_wh']}")
json.dump(results,open('work/min/selftpl_meta.json','w'),indent=1)
# montage
mont=[]
for leg in order:
    im=cv2.imread(f'work/min/selftpl/leg{leg:02d}.png')
    if im is not None: mont.append((leg,cv2.resize(im,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)))
cols=8; cellw=max(m[1].shape[1] for m in mont)+8; cellh=max(m[1].shape[0] for m in mont)+16
rowsn=(len(mont)+cols-1)//cols
canvas=np.full((rowsn*cellh,cols*cellw,3),255,np.uint8)
for k,(no,big) in enumerate(mont):
    rr,cc=divmod(k,cols); y=rr*cellh; x=cc*cellw
    canvas[y+14:y+14+big.shape[0],x+4:x+4+big.shape[1]]=big
    cv2.putText(canvas,f"{no}",(x+4,y+11),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite('work/qa/selftpl_montage2.png',canvas)
print("done")
