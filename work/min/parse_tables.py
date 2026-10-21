import pymupdf, re, json
import pandas as pd
from collections import Counter, defaultdict

SRC='Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'
ON,OFF=0,2
def doc_only(onset):
    d=pymupdf.open(SRC)
    for c in d.layer_ui_configs():
        d.set_layer_ui_config(c['number'], ON if c['number'] in onset else OFF)
    return d

# --- chars from Other2 layer only ---
d=doc_only({0})
p=d[0]
td=p.get_text('rawdict')
chars=[]
for b in td['blocks']:
    if b['type']!=0: continue
    for l in b['lines']:
        for s in l['spans']:
            for c in s['chars']:
                chars.append({'c':c['c'],'x':c['bbox'][0],'y':c['bbox'][1],'x1':c['bbox'][2],'y1':c['bbox'][3],
                              'size':s['size'],'font':s['font'],'ox':c['origin'][0],'oy':c['origin'][1]})
print(f"Other2 chars: {len(chars)}")
print("fonts/sizes:", Counter((c['font'],round(c['size'],1)) for c in chars).most_common(10))

# headers: bold size ~19.8 single letters A-G
headers=[c for c in chars if c['c'] in 'ABCDEFG' and c['size']>15]
# group header chars (each header is 1 char)
print("\nHEADERS (size>15, A-G):")
for h in sorted(headers, key=lambda c:(round(c['y']),c['x'])):
    print(f"  {h['c']} x={h['x']:.1f} y={h['y']:.1f} size={h['size']:.1f}")

# table chars: ArialMT size ~9.9, x>2260
tab=[c for c in chars if 9.0<c['size']<11.0 and c['x']>2260 and c['c']!=' ']
print(f"\ntable chars: {len(tab)}")
# group into lines by oy (origin y) rounded: pitch ~9.04; cluster oy within 2pt
tab.sort(key=lambda c:(c['oy'], c['x']))
lines=[]
cur=[]; cury=None
for c in tab:
    if cury is None or abs(c['oy']-cury)<=2.0:
        cur.append(c); cury=c['oy'] if cury is None else cury
    else:
        lines.append(cur); cur=[c]; cury=c['oy']
if cur: lines.append(cur)
print(f"lines: {len(lines)}")
# split each line into segments by x gap > 18pt
segs=[]
for ln in lines:
    ln.sort(key=lambda c:c['x'])
    seg=[ln[0]]
    for c in ln[1:]:
        if c['x']-seg[-1]['x1']>18:
            segs.append(seg); seg=[c]
        else: seg.append(c)
    segs.append(seg)
print(f"segments: {len(segs)}")
# segment text with single spaces where gap>1.2pt
def seg_text(seg):
    out=[]
    for i,c in enumerate(seg):
        if i>0 and c['x']-seg[i-1]['x1']>1.2: out.append(' ')
        out.append(c['c'])
    return ''.join(out).strip()

rows=[]
for seg in segs:
    txt=seg_text(seg)
    x0=seg[0]['x']; y0=seg[0]['oy']
    # split codes: largest internal gap
    gaps=[(seg[i]['x']-seg[i-1]['x1'], i) for i in range(1,len(seg))]
    gi=max(gaps) if gaps else (0,0)
    if gi[0]>6:
        left=seg_text(seg[:gi[1]]); right=seg_text(seg[gi[1]:])
    else:
        left, right = txt, ''
    rows.append({'x':x0,'y':y0,'text':txt,'left':left,'codes_raw':right})
df=pd.DataFrame(rows)
# parse leading number from left (allow I/l as 1, O as 0 in leading token)
def lead_num(s):
    m=re.match(r'^([0-9IlO]+)\.?\s*(.*)$', s)
    if not m: return None, s
    num=m.group(1).replace('I','1').replace('l','1').replace('O','0')
    try: return int(num), m.group(2)
    except: return None, s
df['num']=[lead_num(s)[0] for s in df.left]
df['locality']=[lead_num(s)[1] for s in df.left]
print(f"\nsegments with leading number: {df.num.notna().sum()} / {len(df)}")
print("segments WITHOUT number (sample):")
print(df[df.num.isna()][['x','y','text']].head(30).to_string())
df.to_csv('work/min/table_segments_raw.csv', index=False)

# column clusters by x
dfn=df[df.num.notna()].copy()
print("\nnumber-segment x clusters:")
xc=Counter(round(v/5)*5 for v in dfn.x)
for k in sorted(xc): print(f"  x~{k}: {xc[k]}")
# per x-cluster (bin width 40 around modes) sequence check
modes=sorted(set(round(v/50)*50 for v in dfn.x))
for m in modes:
    sub=dfn[abs(dfn.x-m)<40].sort_values('y')
    if len(sub)<5: continue
    nums=sub.num.tolist()
    resets=[(i,nums[i-1],nums[i], round(sub.y.iloc[i])) for i in range(1,len(nums)) if nums[i]<=nums[i-1]]
    print(f"\nx~{m} n={len(sub)} y {sub.y.min():.0f}..{sub.y.max():.0f} num {nums[0]}..{nums[-1]} resets/jumps: {resets[:15]}")
