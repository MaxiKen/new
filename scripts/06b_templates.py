"""FINAL mineral legend templates (67): flipped strips, Granite fragments merged, Calcite from render."""
import sys, json
sys.path.insert(0,"scripts")
import numpy as np, cv2, fitz
doc=fitz.open("Mineral_Resources_Map_of_Nigeria_2023 (2).pdf"); page=doc[0]

NAMES = [
 "Asbestos / Serpentine","Ball Clay","Baryte","Bauxitic Clay","Bentonite","Beryl, Aquamarine, Emerald",
 "Bismuth","Bitumen","Brick Clay","Brine","Chromite","Clay / Pottery Clay","Coal","Columbite",
 "Copper minerals","Corundum, Sapphire & Ruby","Diatomite","Dimension Stone","Evaporite","Feldspar",
 "Fire Clay","Fluorite","Garnet","Oil and Gas","Glass Sand","Gold","Graphite","River Gravel","Galena",
 "Granite","Gypsum","Phosphate","Iron Ore (Magnetite, Ilmenite)","Kaolin / kaolinitic clay","Kyanite",
 "Lead - Zinc","Lepidolite","Lignite","Limestone","Manganese","Marble","Marcasite (mc)","Marl (mi)",
 "Mica (m)","Magnesite","Molybdenite (mo)","Monazite","Nickel (ni)","Phosphate Rock","Psammite",
 "Pyrite / Pyroclore (py)","Rose Quartz (r)","Saltlake / Potash","Silica Sand (ss)","Sillimanite (sl)",
 "Silver (ag)","Talc (tc)","Tantalite (ta)","Tar Sand (ts)","Topaz (tpz)","Tourmaline (tm)","Trona (tr)",
 "Uranium (u)","Wolframite (w)","Zircon (zr)",
 "Lithium (Amblygonite, Kunzite, Morganite, Spodumene, etc)","Calcite",
]
PATTERN = {"River Gravel","Granite","Limestone","Marl (mi)"}  # area-pattern fills, not point markers

def ink_mask(arr):
    a=arr.astype(int); mn=a.min(axis=2); mx=a.max(axis=2)
    return (mn<198)|((mx-mn)>55)

def segments(ink, gap=3):
    row=ink.any(axis=1); r=row.copy(); i=0
    while i<len(r):
        if not r[i]:
            j=i
            while j<len(r) and not r[j]: j+=1
            if j-i<=gap and i>0 and j<len(r): r[i:j]=True
            i=j
        else: i+=1
    segs=[]; i=0
    while i<len(r):
        if r[i]:
            j=i
            while j<len(r) and r[j]: j+=1
            segs.append((i,j-1)); i=j
        else: i+=1
    return segs

infos={i["xref"]:i for i in page.get_image_info(xrefs=True)}
raw=[]  # (tpl, pxpt, strip)
for xref in (19,21):
    inf=infos[xref]; bb=inf["bbox"]
    pix=fitz.Pixmap(doc,xref)
    arr=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.h,pix.w,pix.n)[:,:,:3]
    arr=np.ascontiguousarray(arr[::-1])
    pxpt=pix.h/(bb[3]-bb[1]); ink=ink_mask(arr)
    for (a,b) in segments(ink):
        sub=ink[a:b+1]; cols=np.where(sub.any(axis=0))[0]
        x0,x1=max(0,cols.min()-2),min(arr.shape[1],cols.max()+3)
        y0,y1=max(0,a-2),min(arr.shape[0],b+3)
        raw.append((arr[y0:y1,x0:x1], float(pxpt), xref))
print("raw segments:", len(raw))
# merge segments 29+30 (Granite speckle fragments, same strip, stack vertically w/ actual gap preserved approx)
g1,g2=raw[29][0],raw[30][0]
W=max(g1.shape[1],g2.shape[1])
def pad(t,W):
    out=np.full((t.shape[0],W,3),255,np.uint8); out[:,:t.shape[1]]=t; return out
granite=np.vstack([pad(g1,W), np.full((4,W,3),255,np.uint8), pad(g2,W)])
raw=raw[:29]+[(granite,raw[29][1],raw[29][2])]+raw[31:]
print("after Granite merge:", len(raw))
# Calcite from page render (ESRI marker glyph, purple dot)
clip=fitz.Rect(2090,1376,2110,1400)
pix=page.get_pixmap(clip=clip, matrix=fitz.Matrix(3.125,3.125))
carr=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.h,pix.w,pix.n)[:,:,:3]
ink=ink_mask(carr); yy,xx=np.where(ink)
ctpl=carr[max(0,yy.min()-2):yy.max()+3, max(0,xx.min()-2):xx.max()+3]
raw.append((np.ascontiguousarray(ctpl),3.125,0))
print("total templates:", len(raw), "names:", len(NAMES))
assert len(raw)==len(NAMES)

templates=[]
for (tpl,pxpt,xref),name in zip(raw,NAMES):
    subink=ink_mask(tpl); yy,xx=np.where(subink)
    templates.append(dict(name=name, tpl=tpl, pxpt=pxpt, strip=int(xref), pattern=bool(name in PATTERN),
        ink_bbox=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],
        ink_centroid=[float(xx.mean()),float(yy.mean())]))
    print(f" {name:52s} strip{xref} {tpl.shape[1]}x{tpl.shape[0]}px ({tpl.shape[1]/pxpt:.1f}x{tpl.shape[0]/pxpt:.1f}pt){' PATTERN' if name in PATTERN else ''}")

cols=9; rows=int(np.ceil(len(templates)/cols))
sheet=np.full((rows*84, cols*84,3),255,np.uint8)
for i,t in enumerate(templates):
    r,c=divmod(i,cols); tpl=t["tpl"]
    sc=min(68/tpl.shape[1],68/tpl.shape[0])
    small=cv2.resize(cv2.cvtColor(tpl,cv2.COLOR_RGB2BGR),(max(1,int(tpl.shape[1]*sc)),max(1,int(tpl.shape[0]*sc))),interpolation=cv2.INTER_AREA)
    y,x=r*84+3,c*84+3
    sheet[y:y+small.shape[0],x:x+small.shape[1]]=small
    cv2.putText(sheet,str(i+1),(x,y+76),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1)
cv2.imwrite("work/mineral_templates_sheet.png",sheet)
np.savez("work/mineral_templates.npz", **{f"t{i}":t["tpl"] for i,t in enumerate(templates)})
json.dump([{k:v for k,v in t.items() if k!="tpl"} for t in templates], open("work/mineral_templates_meta.json","w"), indent=1)
print("saved final templates")
