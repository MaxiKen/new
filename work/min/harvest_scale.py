import cv2, numpy as np, json, pickle
import pandas as pd
import sys; sys.path.insert(0,'work/min')
from ncc import masked_ncc, scale_tpl

base=cv2.imread('work/min/mineral_base.png').astype(np.float32)
meta=json.load(open('work/min/templates_meta.json'))
tab=pd.read_pickle('work/min/tables_final.pkl')
zoned=pickle.load(open('work/min/map_numbers_zoned.pkl','rb'))
# zoned: list of dicts? normalize
nums=[]
if isinstance(zoned,list):
    for d in zoned: nums.append(d)
print("zoned sample:", nums[:2])
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Be':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cor':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Gy':31,'Ka':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'M':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Ru':16,'Sl':55,'Sn':14,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zn':36,'Zr':65,'Il':33,'Ilm':33}
# number lookup (zone,value)->list of (cx_pt,cy_pt)
from collections import defaultdict
nlk=defaultdict(list)
for d in nums:
    nlk[(d['zone'],int(d['value']))].append((d['cx'],d['cy']))
def to_px(x,y): return ((x-74.2397)/0.959996,(y-358.724)/0.959996)
# harvest cases: single-code rows with map number present
cases=[]
for _,r in tab.iterrows():
    cl=[c for c in r.codes_list if not c.startswith('?')]
    if len(cl)!=1: continue
    leg=CODE2LEG.get(cl[0])
    if leg is None: continue
    key=(r.zone,int(r.link_num))
    if key not in nlk: continue
    for (cx,cy) in nlk[key][:1]:
        px,py=to_px(cx,cy)
        cases.append({'zone':r.zone,'num':int(r.link_num),'leg':leg,'px':px,'py':py,'code':cl[0]})
print(f"harvest cases: {len(cases)}")
from collections import Counter
print(Counter(c['leg'] for c in cases).most_common(10))
pickle.dump(cases,open('work/min/harvest_cases.pkl','wb'))

tpls={}
def get_tpl(leg,s):
    if (leg,s) not in tpls:
        t=cv2.imread(f'work/min/templates/leg{leg:02d}.png').astype(np.float32)
        m=cv2.imread(f'work/min/templates/leg{leg:02d}_mask.png',0).astype(np.float32)/255.0
        tpls[(leg,s)]=scale_tpl(t,m,s)
    return tpls[(leg,s)]
# sample up to 6 cases per leg for speed
sample=[]
byleg=defaultdict(list)
for c in cases: byleg[c['leg']].append(c)
for leg,cs in byleg.items(): sample+=cs[:6]
print("sample cases:",len(sample),"legs:",len(byleg))
R=34
for s in [0.7,0.75,0.8,0.85,0.9,0.95,1.0]:
    peaks=[]
    for c in sample:
        t,m=get_tpl(c['leg'],s)
        x0=int(max(0,c['px']-R)); y0=int(max(0,c['py']-R))
        x1=int(min(base.shape[1],c['px']+R)); y1=int(min(base.shape[0],c['py']+R))
        win=base[y0:y1,x0:x1]
        if win.shape[0]<t.shape[0] or win.shape[1]<t.shape[1]: continue
        ncc=masked_ncc(win,t,m)
        peaks.append(float(ncc.max()))
    peaks=np.array(peaks)
    print(f"s={s}: median={np.median(peaks):.3f} mean={peaks.mean():.3f} frac>0.75={(peaks>0.75).mean():.2f} frac>0.85={(peaks>0.85).mean():.2f} n={len(peaks)}")
