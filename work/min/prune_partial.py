import cv2, numpy as np, pickle, sys
sys.path.insert(0,'work/min')
from ncc import masked_ncc
from collections import Counter
base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
BH,BW=base.shape[:2]
P=pickle.load(open('work/min/partial_v2.pkl','rb'))
acc=P['accepted']
KEEP={3,5,6,20,21,25,29,37,62,63,64,65,66,67}
print("visual-keep candidates:")
for i in sorted(KEEP):
    c=acc[i]
    print(f" #{i} leg{c['leg']} score={c['score']} full={c['full']} vis={c['vis']} occ={c['occ']} at ({c['cx']:.0f},{c['cy']:.0f})")
TPL={}
def tpl(L):
    if L==32: L=31
    if L not in TPL:
        t=cv2.imread(f'work/min/selftpl4/leg{L:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/selftpl4/leg{L:02d}_mask.png',0).astype(np.float32)/255
        ys,xs=np.where(m>0)
        TPL[L]=(t,m,(xs.min()+xs.max())/2,(ys.min()+ys.max())/2)
    return TPL[L]
def score_at(L,cx,cy):
    t,m,bcx,bcy=tpl(L); WR=20
    x0=int(max(0,cx-WR)); y0=int(max(0,cy-WR)); x1=int(min(BW,cx+WR)); y1=int(min(BH,cy+WR))
    win=base[y0:y1,x0:x1]
    if win.shape[0]<t.shape[0]+2 or win.shape[1]<t.shape[1]+2: return 0.0
    ncc=masked_ncc(win,t,m)
    H,W=ncc.shape; yy,xx=np.mgrid[0:H,0:W]
    return float(np.where(np.hypot(xx+x0+bcx-cx,yy+y0+bcy-cy)<=1.6,ncc,-1).max())
LEGS=[L for L in range(1,68) if L!=49]
kept=[]
for i in sorted(KEEP):
    c=acc[i]
    own=score_at(c['leg'],c['cx'],c['cy'])
    bl,bv=max(((K,score_at(K,c['cx'],c['cy'])) for K in LEGS if K!=c['leg']),key=lambda kv:kv[1])
    verdict = 'DROP(competitor)' if bv>own+0.10 else 'KEEP'
    print(f" #{i} leg{c['leg']}: own_full={own:.3f} best_other=leg{bl} {bv:.3f} -> {verdict}")
    if verdict=='KEEP': kept.append(c)
# merge with complete
S=pickle.load(open('work/min/complete_v6.pkl','rb'))
pts,num_state=S['pts'],S['num_state']
for c in kept:
    pts.append({'leg':c['leg'],'cx':c['cx'],'cy':c['cy'],'score':c['score'],'tier':'partial',
                'match_type':'partial','vis_part':c['vis'],'num_idx':c['ni']})
    num_state[c['ni']]['filled'][c['leg']]+=1
for p in pts:
    p.setdefault('vis_part','')
tot=sum(sum(ns['expected'].values()) for ns in num_state)
fil=sum(sum(ns['filled'].values()) for ns in num_state)
print(f"FINAL pts={len(pts)} (partial kept {len(kept)}) filled={fil}/{tot}")
print("per-leg:",dict(sorted(Counter(p['leg'] for p in pts).items())))
print("match types:",Counter(p['match_type'] for p in pts))
# dedup audit
from scipy.spatial import cKDTree
xy=np.array([[p['cx'],p['cy']] for p in pts])
d,_=cKDTree(xy).query(xy,k=2)
print("pairs <5px:",int((d[:,1]<5).sum())," min nn dist:",round(float(d[:,1].min()),2))
pickle.dump({'pts':pts,'num_state':num_state},open('work/min/final_v2_pts.pkl','wb'))
