import cv2, numpy as np, json
base=cv2.imread('work/min/mineral_base.png')  # BGR
meta=json.load(open('work/min/templates_meta.json'))
def to_px(x,y): return ((x-74.2397)/0.959996,(y-358.724)/0.959996)
# Jos window page x1030-1400 y980-1280
x0,y0=to_px(1030,980); x1,y1=to_px(1400,1280)
win=base[int(y0):int(y1),int(x0):int(x1)].copy()
print("window",win.shape)
def score_sqdiff(res,tpl,mask):
    # SQDIFF with mask: lower better; convert to pseudo-NCC: 1 - res/sum(tpl^2 over mask)
    denom=float(((tpl.astype(np.float64)**2)*mask[:,:,None]).sum())
    return 1-res/denom
for legno in [14,34,26,58,31,36]:
    tpl=cv2.imread(f'work/min/templates/leg{legno:02d}.png')
    m=cv2.imread(f'work/min/templates/leg{legno:02d}_mask.png',0)
    print(f"--- leg{legno} {meta[str(legno)]['name']} tpl{tpl.shape}")
    for s in [0.8,0.9,1.0,1.1,1.25,1.4]:
        t2=cv2.resize(tpl,None,fx=s,fy=s,interpolation=cv2.INTER_LINEAR if s>1 else cv2.INTER_AREA)
        m2=cv2.resize(m,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
        if t2.shape[0]>=win.shape[0] or t2.shape[1]>=win.shape[1]: continue
        res=cv2.matchTemplate(win,t2,cv2.TM_SQDIFF,mask=m2)
        sc=score_sqdiff(res,t2,(m2>0).astype(np.float64))
        flat=np.sort(sc.ravel())[::-1]
        print(f"  s={s}: top1={flat[0]:.3f} top10={flat[9]:.3f} count>0.80={int((sc>0.80).sum())} count>0.85={int((sc>0.85).sum())}")
