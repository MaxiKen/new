import cv2, numpy as np, json, os, pickle
import geopandas as gpd, pandas as pd
os.makedirs('work/min/selftpl',exist_ok=True)
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)  # BGR
BH,BW=base.shape[:2]
old=gpd.read_file('shapefile_results/minerals/nigeria_mineral_symbols.shp')
legmeta=json.load(open('work/min/templates_meta.json'))
HALF=19; TS=29; OFF=HALF-TS//2  # template frame offset inside patch

def get_patch(cx,cy):
    x0,y0=int(round(cx))-HALF,int(round(cy))-HALF
    if x0<0 or y0<0 or x0+2*HALF+1>BW or y0+2*HALF+1>BH: return None
    return base[y0:y0+2*HALF+1,x0:x0+2*HALF+1].copy()

def legend_mask_centered(leg,s=0.7):
    m=cv2.imread(f'work/min/templates/leg{leg:02d}_mask.png',0).astype(np.float32)/255
    m2=cv2.resize(m,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    m2=(m2>0.35).astype(np.float32)
    canvas=np.zeros((TS,TS),np.float32)
    h,w=m2.shape; y=(TS-h)//2; x=(TS-w)//2
    if h>TS or w>TS:
        m2=cv2.resize(m2,(min(w,TS),min(h,TS)),interpolation=cv2.INTER_NEAREST); h,w=m2.shape; y=(TS-h)//2; x=(TS-w)//2
    canvas[y:y+h,x:x+w]=m2
    return canvas

def masked_ncc_shift(T,M,P,dx,dy):
    ys,xs=np.where(M>0)
    a=T[ys,xs]                      # (n,3)
    b=P[ys+OFF+dy,xs+OFF+dx]
    a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    num=float((a*b).sum()); den=np.sqrt(float((a*a).sum())*float((b*b).sum()))
    return num/den if den>1e-6 else 0.0

def align_patches(patches,M,rounds=3):
    # template frame = central TSxTS of patches
    frames=np.stack([p[OFF:OFF+TS,OFF:OFF+TS] for p in patches])
    T=np.median(frames,axis=0)
    shifts=[(0,0)]*len(patches); scores=[0.0]*len(patches)
    for r in range(rounds):
        shifted=[]
        for i,p in enumerate(patches):
            best=(-2,0,0)
            for dy in range(-5,6):
                for dx in range(-5,6):
                    v=masked_ncc_shift(T,M,p,dx,dy)
                    if v>best[0]: best=(v,dx,dy)
            scores[i]=best[0]; shifts[i]=(best[1],best[2])
            shifted.append(p[OFF+best[2]:OFF+best[2]+TS,OFF+best[1]:OFF+best[1]+TS])
        T=np.median(np.stack(shifted),axis=0)
    return T,shifts,scores,shifted

def agreement_mask(shifted,Mleg):
    inks=[]
    for f in shifted:
        border=np.concatenate([f[:2].reshape(-1,3),f[-2:].reshape(-1,3),f[:,:2].reshape(-1,3),f[:,-2:].reshape(-1,3)])
        med=np.median(border,axis=0)
        d=np.abs(f-med).max(axis=2)
        inks.append((d>26).astype(np.float32))
    A=np.mean(np.stack(inks),axis=0)
    M=((A>0.45)|((Mleg>0)&(A>0.22))).astype(np.uint8)
    # fill holes
    ff=M.copy(); h,w=M.shape
    mask=np.zeros((h+2,w+2),np.uint8)
    inv=(1-ff)*255
    cv2.floodFill(inv,mask,(0,0),128)
    holes=(inv==255).astype(np.uint8)
    M=np.maximum(M,holes)
    # keep CCs that touch legend mask or are large
    n,lab,stats,_=cv2.connectedComponentsWithStats(M,8)
    if n>1:
        areas=stats[1:,cv2.CC_STAT_AREA]; mx=areas.max()
        keep=np.zeros_like(M)
        for i in range(1,n):
            touch=bool(((lab==i)&(Mleg>0)).any())
            if areas[i-1]>=max(6,0.06*mx) or touch: keep[lab==i]=1
        M=keep
    return M.astype(np.float32)

results={}
montage=[]
for leg in range(1,68):
    seeds=old[old.leg_no==leg]
    patches=[]; used=0
    for _,r in seeds.iterrows():
        p=get_patch(r.px_x,r.px_y)
        if p is not None: patches.append(p)
    if len(patches)>=3:
        Mleg=legend_mask_centered(leg,0.7)
        Mp=Mleg.copy()
        T,shifts,scores,shifted=align_patches(patches,Mp,rounds=2)
        # refine mask then one more round
        Mnew=agreement_mask(shifted,Mleg)
        if Mnew.sum()>=20:
            T,shifts,scores,shifted=align_patches(patches,Mnew,rounds=2)
            Mnew=agreement_mask(shifted,Mleg)
        else:
            Mnew=Mleg
        keep=[i for i,s in enumerate(scores) if s>=0.55]
        if len(keep)>=3:
            shifted=[shifted[i] for i in keep]
            T=np.median(np.stack(shifted),axis=0)
            Mnew=agreement_mask(shifted,Mleg)
            scores=[scores[i] for i in keep]
        M=Mnew
        if M.sum()<10: M=Mleg
        ys,xs=np.where(M>0)
        y0,y1=max(0,ys.min()-1),min(TS,ys.max()+2); x0,x1=max(0,xs.min()-1),min(TS,xs.max()+2)
        tpl=T[y0:y1,x0:x1]; mm=M[y0:y1,x0:x1]
        by,bx=np.where(mm>0)
        cx=(bx.min()+bx.max())/2; cy=(by.min()+by.max())/2
        cv2.imwrite(f'work/min/selftpl/leg{leg:02d}.png',np.clip(tpl,0,255).astype(np.uint8))
        cv2.imwrite(f'work/min/selftpl/leg{leg:02d}_mask.png',(mm*255).astype(np.uint8))
        results[leg]={'src':'self','n_seeds':len(patches),'n_used':len(keep) if len(patches)>=3 else len(patches),
                      'med_ncc':float(np.median(scores)) if scores else 0,'tpl_wh':[int(tpl.shape[1]),int(tpl.shape[0])],
                      'center_xy':[float(cx),float(cy)],'body_px':int(mm.sum())}
        montage.append((leg,cv2.resize(np.clip(tpl,0,255).astype(np.uint8),None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)))
        print(f"leg{leg:02d} self n={len(patches)} used={results[leg]['n_used']} medNCC={results[leg]['med_ncc']:.2f} wh={results[leg]['tpl_wh']}")
    else:
        results[leg]={'src':'pending','n_seeds':len(patches)}
        print(f"leg{leg:02d} pending seeds={len(patches)}")
json.dump(results,open('work/min/selftpl_meta.json','w'),indent=1)
pickle.dump(results,open('work/min/selftpl_meta.pkl','wb'))
if montage:
    cols=8; cellw=max(m[1].shape[1] for m in montage)+8; cellh=max(m[1].shape[0] for m in montage)+16
    rowsn=(len(montage)+cols-1)//cols
    canvas=np.full((rowsn*cellh,cols*cellw,3),255,np.uint8)
    for k,(no,big) in enumerate(montage):
        rr,cc=divmod(k,cols); y=rr*cellh; x=cc*cellw
        canvas[y+14:y+14+big.shape[0],x+4:x+4+big.shape[1]]=big
        cv2.putText(canvas,f"{no}",(x+4,y+11),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    cv2.imwrite('work/qa/selftpl_montage.png',canvas)
print("done")
