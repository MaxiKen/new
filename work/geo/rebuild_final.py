import geopandas as gpd, numpy as np, shapely, json, warnings, pickle, time
import pandas as pd
from shapely import STRtree
from shapely.ops import unary_union
from PIL import Image
warnings.filterwarnings('ignore')
t0=time.time()
KM2=12266.0

geo=gpd.read_file('shapefile_results/geology/nigeria_geology_units.shp')
geo['fid']=np.arange(len(geo))
d=pickle.load(open('work/geo/faces.pkl','rb')); faces=d['faces']; in_ref=d['in_ref']
face_cands=pickle.load(open('work/geo/face_cands.pkl','rb'))
areas=np.array([f.area for f in faces])
src_seq=geo.src_seq.values

tr=json.load(open('work/geo/geology_transform.json'))
A,B=tr['lon_coef']; C,D=tr['lat_coef']
img=np.asarray(Image.open('work/geo/geology_native.png').convert('RGB')).astype(int)
H,W=img.shape[:2]
def sample_color(poly, nmax=100):
    pts=[poly.representative_point()]
    minx,miny,maxx,maxy=poly.bounds
    n=9
    for i in range(1,n):
        for j in range(1,n):
            p=shapely.Point(minx+(maxx-minx)*i/n, miny+(maxy-miny)*j/n)
            if poly.contains(p): pts.append(p)
    cols=[]
    for p in pts[:nmax]:
        px=int((p.x-B)/A); py=int((p.y-D)/C)
        if 1<=px<W-1 and 1<=py<H-1: cols.append(img[py,px])
    return np.median(np.array(cols),axis=0) if cols else None

def hexrgb(h):
    try: return np.array([int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)],dtype=float)
    except: return None
fills={j:hexrgb(h) for j,h in enumerate(geo['fill']) if isinstance(h,str)}

def color_decision(face, cand_fids):
    """Return chosen fid by color or None. Group by fill; clear-match criteria."""
    col=sample_color(face)
    if col is None: return None, 999, None
    byfill={}
    for j in cand_fids:
        if j in fills: byfill.setdefault(geo.fill.iloc[j], []).append(j)
    if not byfill: return None, 999, col
    dists={fl: float(np.linalg.norm(col-fills[js[0]])) for fl,js in byfill.items()}
    order=sorted(dists.items(), key=lambda kv: kv[1])
    best_fl, best_d = order[0]
    second_d = order[1][1] if len(order)>1 else 999
    if best_d<=38 and (second_d-best_d)>=12:
        # within fill group choose max src_seq
        win=max(byfill[best_fl], key=lambda j: src_seq[j])
        return win, best_d, col
    return None, best_d, col

assign=np.full(len(faces),-1,dtype=int)
method=np.array(['']*len(faces), dtype=object)
log=[]

# --- pass 1: source-overlap faces ---
for i,ovs in face_cands.items():
    if not ovs: continue
    f=faces[i]; akm=areas[i]*KM2
    full=[j for j,c in ovs if c>=0.99]
    if len(full)==1:
        assign[i]=full[0]; method[i]='source'
    elif len(full)>=2:
        win=None
        if akm>=2:
            win,bd,col=color_decision(f, full)
            if win is not None: method[i]='overlap_color'
        if win is None:
            win=max(full, key=lambda j: src_seq[j]); method[i]='overlap_draworder'
        assign[i]=win
        if akm>=1:
            log.append({'face':i,'area_km2':round(float(akm),2),'kind':'overlap','chosen_fid':int(win),
                        'chosen_unit':geo.unit.iloc[win],'method':method[i],
                        'candidates':';'.join(f"{j}:{geo.unit.iloc[j][:24]}" for j in full)})
    else:
        j,c=max(ovs, key=lambda t:t[1])
        assign[i]=j; method[i]='partial_majority'
        if akm>=1:
            log.append({'face':i,'area_km2':round(float(akm),2),'kind':'partial','chosen_fid':int(j),
                        'chosen_unit':geo.unit.iloc[j],'method':method[i],
                        'candidates':';'.join(f"{jj}:{geo.unit.iloc[jj][:24]}({cc:.2f})" for jj,cc in ovs)})
print(f"pass1 assigned {(assign>=0).sum()}  [{time.time()-t0:.0f}s]")

# --- adjacency (shared border length per neighboring face) ---
ftree=STRtree(faces)
adj={}   # i -> {j: shared_len}
for i,f in enumerate(faces):
    if not in_ref[i]: continue
    for j in ftree.query(f):
        if j<=i or not in_ref[j]: continue
        inter=f.boundary.intersection(faces[j].boundary)
        L=inter.length
        if L>1e-12:
            adj.setdefault(i,{})[int(j)]=L
            adj.setdefault(int(j),{})[i]=L
print(f"adjacency built: {sum(len(v) for v in adj.values())//2} edges  [{time.time()-t0:.0f}s]")

# --- pass 2: gap faces BFS ---
remaining=set(int(i) for i in np.where((assign<0)&in_ref)[0])
print(f"gap faces to fill: {len(remaining)}")
rounds=0
while remaining:
    progressed=False; rounds+=1
    for i in sorted(remaining, key=lambda i:-areas[i]):
        neigh=adj.get(i,{})
        # border length per assigned feature
        per={}
        for j,L in neigh.items():
            if assign[j]>=0: per[assign[j]]=per.get(assign[j],0)+L
        if not per: continue
        akm=areas[i]*KM2; f=faces[i]
        win=None
        if akm>=5:
            win,bd,col=color_decision(f, list(per.keys()))
            if win is not None: method[i]='gap_color'
        if win is None:
            win=max(per, key=per.get); method[i]='gap_border'
        assign[i]=win; progressed=True
        if akm>=1:
            log.append({'face':i,'area_km2':round(float(akm),2),'kind':'gap','chosen_fid':int(win),
                        'chosen_unit':geo.unit.iloc[win],'method':method[i],
                        'candidates':';'.join(f"{j}:{geo.unit.iloc[j][:24]}" for j in per)})
    remaining={i for i in remaining if assign[i]<0}
    print(f" round {rounds}: remaining {len(remaining)}")
    if not progressed: break
print(f"unassigned (islands): {sorted(remaining)} areas km2: {[round(float(areas[i]*KM2),1) for i in remaining]}")

# --- pass 3: island faces -> NEW features via color vs delta-vicinity units ---
new_rows=[]
MAXFID=len(geo)
for i in sorted(remaining):
    f=faces[i]; col=sample_color(f)
    cen=f.representative_point()
    # candidate features within 1.2 deg
    cand=[j for j in range(len(geo)) if abs(geo.cen_lon.iloc[j]-cen.x)<1.2 and abs(geo.cen_lat.iloc[j]-cen.y)<1.2 and j in fills]
    dists={j: float(np.linalg.norm(col-fills[j])) for j in cand}
    win=min(dists, key=dists.get)
    print(f" island face {i} area {areas[i]*KM2:.1f} km2 sampled {col} -> unit fid {win} {geo.unit.iloc[win]!r} fill {geo.fill.iloc[win]} dist {dists[win]:.1f}")
    assign[i]=MAXFID; method[i]='new_island'
    row=geo.iloc[win].copy()
    row['fid']=MAXFID; row['src_seq']=int(geo.src_seq.max())+1+ (MAXFID-len(geo)); row['n_lbl']=0
    new_rows.append(row)
    log.append({'face':i,'area_km2':round(float(areas[i]*KM2),2),'kind':'island_new','chosen_fid':int(MAXFID),
                'chosen_unit':geo.unit.iloc[win],'method':'new_island_color',
                'candidates':f"source fid {win}"})
    MAXFID+=1

pd.DataFrame(log).sort_values('area_km2',ascending=False).to_csv('work/geo/gap_assignment_log.csv',index=False)
pickle.dump({'assign':assign,'method':method,'new_rows':new_rows}, open('work/geo/assign_final.pkl','wb'))
from collections import Counter
print("\nmethods (faces):", Counter(method[in_ref]))
print("methods (km2):")
for m in sorted(set(method[in_ref])):
    sel=in_ref&(method==m)
    print(f"  {m:20s} faces={sel.sum():5d} area={areas[sel].sum()*KM2:10.1f} km2")
print(f"total inside-ref face area: {areas[in_ref].sum()*KM2:.1f} km2  [{time.time()-t0:.0f}s]")
