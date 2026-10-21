import pymupdf, re, json
import pandas as pd, numpy as np
from collections import Counter

SRC='Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'
ON,OFF=0,2
d=pymupdf.open(SRC)
for c in d.layer_ui_configs():
    d.set_layer_ui_config(c['number'], ON if c['number']==0 else OFF)
p=d[0]
td=p.get_text('rawdict')
chars=[]
for b in td['blocks']:
    if b['type']!=0: continue
    for l in b['lines']:
        for s in l['spans']:
            for c in s['chars']:
                chars.append({'c':c['c'],'x':c['bbox'][0],'y':c['bbox'][1],'x1':c['bbox'][2],'y1':c['bbox'][3],
                              'size':round(s['size'],1),'font':s['font'],'oy':c['origin'][1]})
# table blocks definition: (x_lo,x_hi,code_x)
BLOCKS=[(2280,2440,2408.9),(2440,2620,2535.1),(2620,2790,2739.0),(2790,2960,2886.6),
        (2960,3130,3071.0),(3130,3290,3247.4),(3290,3460,3412.9),(3460,3660,3559.0)]
def block_of(x):
    for i,(lo,hi,cx) in enumerate(BLOCKS):
        if lo<=x<hi: return i
    return -1

tab=[c for c in chars if 9.0<c['size']<11.0 and c['x']>2260 and c['c']!=' ']
for c in tab: c['blk']=block_of(c['x'])
tab=[c for c in tab if c['blk']>=0]

def join_chars(cs, space_gap=1.6):
    cs=sorted(cs,key=lambda c:c['x'])
    out=[]
    for i,c in enumerate(cs):
        if i>0 and c['x']-cs[i-1]['x1']>space_gap: out.append(' ')
        out.append(c['c'])
    return ''.join(out).strip()

rows=[]
for bi,(lo,hi,cx) in enumerate(BLOCKS):
    bc=[c for c in tab if c['blk']==bi]
    bc.sort(key=lambda c:(c['oy'],c['x']))
    # group by oy within 2pt
    lines=[]; cur=[]; cury=None
    for c in bc:
        if cury is None or abs(c['oy']-cury)<=2.0: cur.append(c); cury=c['oy'] if cury is None else cury
        else: lines.append(cur); cur=[c]; cury=c['oy']
    if cur: lines.append(cur)
    for ln in lines:
        left=[c for c in ln if c['x']<cx-3]
        right=[c for c in ln if c['x']>=cx-3]
        if not left: continue
        rows.append({'blk':bi,'y':float(np.median([c['oy'] for c in ln])),
                     'left':join_chars(left),'codes_raw':join_chars(right) if right else ''})
df=pd.DataFrame(rows)
print(f"raw lines in blocks: {len(df)}")
def lead_num(s):
    m=re.match(r'^([0-9IlO]+)\.?\s*(.*)$', s)
    if not m: return None,s
    num=m.group(1).replace('I','1').replace('l','1').replace('O','0')
    try: return int(num), m.group(2).strip()
    except: return None,s
df['num']=[lead_num(s)[0] for s in df.left]
df['locality_raw']=[lead_num(s)[1] for s in df.left]
print(f"with number: {df.num.notna().sum()}, without: {df.num.isna().sum()}")
print("sample no-number lines:")
print(df[df.num.isna()][['blk','y','left','codes_raw']].head(25).to_string())

# zone segmentation by (blk, y-cut)
# from headers: B1: A y<1295, B y>=1295 ; B2: B y<1025, C y>=1025 ; B5: E y<1235, F y>=1235 ; others single
def zone_of(blk,y):
    if blk==0: return 'A' if y<1295 else 'B'
    if blk==1: return 'B' if y<1025 else 'C'
    if blk==2: return 'D'
    if blk==3: return 'E'
    if blk==4: return 'E' if y<1235 else 'F'
    if blk==5: return 'F'
    if blk in (6,7): return 'G'
df['zone']=[zone_of(b,y) for b,y in zip(df.blk,df.y)]
dfn=df[df.num.notna()].copy()
print("\nper zone sequences:")
for z in 'ABCDEFG':
    sub=dfn[dfn.zone==z].sort_values(['blk','y'])
    nums=sub.num.astype(int).tolist()
    missing=[n for n in range(1,max(nums)+1) if n not in set(nums)] if nums else []
    dups=[n for n,c in Counter(nums).items() if c>1]
    print(f" zone {z}: rows={len(sub)} num range {min(nums)}..{max(nums)} missing={missing[:20]}{'...' if len(missing)>20 else ''} dups={sorted(dups)[:15]}")
    # order check within block flow: blk order then y - B zone spans blk0-bottom then blk1-top: sort key above puts blk0 B(1-85) before blk1 B(86+) correct by blk
df.to_csv('work/min/tables_raw2.csv',index=False)
print("\nsaved work/min/tables_raw2.csv")
print(dfn[dfn.zone=='C'].sort_values(['blk','y']).tail(12)[['blk','y','num','locality_raw','codes_raw']].to_string())
print(dfn[dfn.zone=='F'].sort_values(['blk','y']).head(6)[['blk','y','num','locality_raw','codes_raw']].to_string())
print(dfn[dfn.zone=='F'].sort_values(['blk','y']).iloc[78:90][['blk','y','num','locality_raw','codes_raw']].to_string())
