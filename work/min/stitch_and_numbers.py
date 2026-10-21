import pymupdf, numpy as np, pickle, json
from PIL import Image
import io
Image.MAX_IMAGE_PIXELS=None

# ---------- 1) Correct stitch ----------
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf')
p=d[0]
infos=[i for i in p.get_image_info(xrefs=True) if i['width']==2060]
infos.sort(key=lambda i: i['bbox'][1])
x0=infos[0]['bbox'][0]; x1=infos[0]['bbox'][2]; ytop=infos[0]['bbox'][1]; ybot=infos[-1]['bbox'][3]
PTPX=(x1-x0)/2060.0
print(f"frame x {x0:.4f}..{x1:.4f} y {ytop:.4f}..{ybot:.4f} pt/px={PTPX:.6f}")
rows_total=int(round((ybot-ytop)/PTPX))
print("canvas rows:", rows_total)
canvas=np.full((rows_total,2060,3),255,dtype=np.uint8)
for i in infos:
    pix=pymupdf.Pixmap(d,i['xref'])
    img=np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB'))[::-1]  # flip vertical
    r0=int(round((i['bbox'][1]-ytop)/PTPX))
    r1=r0+img.shape[0]
    # check overlap consistency with existing canvas where overlapping
    if r0>0:
        ov=min(r1,rows_total)-r0
        # overlap region is first row(s) vs previous strip bottom rows already pasted
        prev_end=r0  # previous strip may extend 1 row into this
    canvas[r0:r1]=img[:rows_total-r0] if r1>rows_total else img
    print(f" xref{i['xref']} bbox_y0={i['bbox'][1]:.2f} -> row {r0}..{r1}")
Image.fromarray(canvas).save('work/min/mineral_base.png')
print("saved work/min/mineral_base.png", canvas.shape)
# seam check: recompute each strip's first row vs previous strip row at same canvas position from raw strips
strips=[]
for i in infos:
    pix=pymupdf.Pixmap(d,i['xref'])
    strips.append(np.asarray(Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB'))[::-1])
for k in range(len(strips)-1):
    a=strips[k][-1].astype(int); b=strips[k+1][0].astype(int)
    print(f" seam {k}: last row of strip{k} vs first row strip{k+1}: mean|diff|={np.abs(a-b).mean():.2f} max={np.abs(a-b).max()}")
meta={'frame_pt':[float(x0),float(ytop),float(x1),float(ybot)],'pt_per_px':float(PTPX),'size_px':[2060,int(rows_total)]}
json.dump(meta, open('work/min/base_meta.json','w'), indent=1)

# ---------- 2) Map numbers from layer 6 chars ----------
ON,OFF=0,2
d2=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf')
for c in d2.layer_ui_configs():
    d2.set_layer_ui_config(c['number'], ON if c['number'] in (1,4,6) else OFF)
p2=d2[0]
td=p2.get_text('rawdict')
chars=[]
for b in td['blocks']:
    if b['type']!=0: continue
    for l in b['lines']:
        for s in l['spans']:
            for c in s['chars']:
                chars.append({'c':c['c'],'x':c['bbox'][0],'y':c['bbox'][1],'x1':c['bbox'][2],'y1':c['bbox'][3],
                              'size':round(s['size'],1),'font':s['font'],'ox':c['origin'][0],'oy':c['origin'][1]})
print(f"\nlayer6 chars: {len(chars)} fonts: {set((c['font'],c['size']) for c in chars)}")
print("distinct char values:", sorted(set(c['c'] for c in chars)))
# group into numbers: cluster by proximity (x gap<4, oy within 2.5)
chars=[c for c in chars if c['c']!=' ']
chars.sort(key=lambda c:(round(c['oy']/3), c['x']))
# union-find clustering
parent=list(range(len(chars)))
def find(a):
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: parent[rb]=ra
# spatial hash by oy bands
from collections import defaultdict
bands=defaultdict(list)
for idx,c in enumerate(chars): bands[int(c['oy']//5)].append(idx)
for band,idxs in bands.items():
    for cand_band in (band-1,band,band+1):
        for i in idxs:
            for j in bands.get(cand_band,[]):
                if j<=i: continue
                a,b=chars[i],chars[j]
                if abs(a['oy']-b['oy'])<2.5 and -2 < (b['x']-a['x1']) < 4.5:
                    union(i,j)
groups=defaultdict(list)
for idx in range(len(chars)): groups[find(idx)].append(idx)
numbers=[]
DIGMAP={'I':'1','l':'1','O':'0','o':'0','S':'5','B':'8','Z':'2','•':''}
for g in groups.values():
    cs=sorted([chars[i] for i in g], key=lambda c:c['x'])
    txt=''.join(c['c'] for c in cs)
    dig=''.join(DIGMAP.get(ch,ch) for ch in txt)
    cx=float(np.mean([(c['x']+c['x1'])/2 for c in cs])); cy=float(np.mean([(c['y']+c['y1'])/2 for c in cs]))
    numbers.append({'txt':txt,'dig':dig,'cx':cx,'cy':cy,'x0':min(c['x'] for c in cs),'y0':min(c['y'] for c in cs),
                    'x1':max(c['x1'] for c in cs),'y1':max(c['y1'] for c in cs),'nchar':len(cs)})
print(f"number groups: {len(numbers)}")
bad=[n for n in numbers if not n['dig'].isdigit()]
print(f"non-digit groups: {len(bad)} sample: {[(n['txt'],round(n['cx']),round(n['cy'])) for n in bad[:20]]}")
good=[n for n in numbers if n['dig'].isdigit()]
for n in good: n['value']=int(n['dig'])
print(f"digit numbers: {len(good)} value range {min(n['value'] for n in good)}..{max(n['value'] for n in good)}")
print("value counts>1 sample:", {v:c for v,c in sorted(__import__('collections').Counter(n['value'] for n in good).items()) if c>6})
pickle.dump(numbers, open('work/min/map_numbers_raw.pkl','wb'))
# inside frame?
inside=[n for n in good if x0-5<=n['cx']<=x1+5 and ytop-5<=n['cy']<=ybot+5]
print(f"numbers inside map frame: {len(inside)}")
