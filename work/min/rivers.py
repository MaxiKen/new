import pickle, numpy as np, geopandas as gpd, pandas as pd
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import unary_union
from collections import Counter
L=pickle.load(open('work/min/mineral_layers.pkl','rb'))
def tf(x,y): return (0.0063408528*x+1.999778, -0.0063497677*y+16.326633)
drawings=L[16]['drawings']
print("drawings:",len(drawings))
print("types:",Counter(d.get('type') for d in drawings))
print("widths:",Counter(round(d.get('width') or 0,2) for d in drawings))
print("colors:",Counter(d.get('color') for d in drawings).most_common(5))
print("fills:",Counter(d.get('fill') for d in drawings).most_common(5))
itemtypes=Counter()
for d in drawings:
    for it in d['items']: itemtypes[it[0]]+=1
print("item types:",itemtypes)

def bezier(p0,p1,p2,p3,n=8):
    t=np.linspace(0,1,n+1)[:,None]
    P=np.array([[p.x,p.y] for p in (p0,p1,p2,p3)])
    B=((1-t)**3)*P[0]+3*((1-t)**2)*t*P[1]+3*(1-t)*t**2*P[2]+(t**3)*P[3]
    return [tuple(r) for r in B[1:]]
lines=[]; polys=[]
for d in drawings:
    paths=[]; cur=[]
    last=None
    for it in d['items']:
        if it[0]=='l':
            p1,p2=it[1],it[2]
            if last is None or (abs(p1.x-last[0])>0.01 or abs(p1.y-last[1])>0.01):
                if len(cur)>=2: paths.append(cur)
                cur=[(p1.x,p1.y)]
            cur.append((p2.x,p2.y)); last=(p2.x,p2.y)
        elif it[0]=='c':
            seg=bezier(it[1],it[2],it[3],it[4])
            if last is None: cur=[(it[1].x,it[1].y)]
            cur+=seg; last=seg[-1]
        elif it[0]=='re':
            r=it[1]; paths.append([(r.x0,r.y0),(r.x1,r.y0),(r.x1,r.y1),(r.x0,r.y1),(r.x0,r.y0)])
    if len(cur)>=2: paths.append(cur)
    for p in paths:
        ll=[tf(x,y) for x,y in p]
        closed = len(ll)>3 and abs(ll[0][0]-ll[-1][0])<1e-6 and abs(ll[0][1]-ll[-1][1])<1e-6
        if closed and d.get('fill') is not None:
            try: polys.append(Polygon(ll))
            except Exception: pass
        else:
            lines.append({'geometry':LineString(ll),'width_pt':round(float(d.get('width') or 0),3)})
rivers=gpd.GeoDataFrame(lines,crs='EPSG:4326')
print("line features:",len(rivers)," bound:",rivers.total_bounds)
print("lake polys:",len(polys))
# clip to Nigeria boundary
admin=gpd.read_file('shapefiles/nigeria_admin0/nigeria_admin0.shp')
nigeria=admin.geometry.unary_union
rivers['geometry']=rivers.geometry.intersection(nigeria)
rivers=rivers[~rivers.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
rivers=rivers[rivers.geometry.geom_type.isin(['LineString','MultiLineString'])]
print("after clip:",len(rivers))
rivers['len_km']=rivers.geometry.to_crs('EPSG:3857').length/1000
rivers=rivers[rivers.len_km>0.05].reset_index(drop=True)

# labels: merge fragments by block + proximity
words=L[9]['words']
labels=[]
used=[False]*len(words)
ws=sorted(range(len(words)),key=lambda i:(words[i][5],words[i][0]))
for i in ws:
    if used[i]: continue
    w=words[i]; used[i]=True
    txt=w[4]; x0,y0,x1,y1=w[0],w[1],w[2],w[3]
    # chain following fragments close to current end
    changed=True
    while changed:
        changed=False
        for j in ws:
            if used[j]: continue
            u=words[j]
            gapx=max(u[0]-x1, x0-u[2], 0); gapy=max(u[1]-y1, y0-u[3], 0)
            if gapx<26 and gapy<14:
                if u[0]>=x1-2: txt=txt+(' ' if gapx>7 else '')+u[4]
                else: txt=u[4]+(' ' if gapx>7 else '')+txt
                x0,y0=min(x0,u[0]),min(y0,u[1]); x1,y1=max(x1,u[2]),max(y1,u[3])
                used[j]=True; changed=True
    cx,cy=tf((x0+x1)/2,(y0+y1)/2)
    labels.append({'name':txt.strip(),'x':cx,'y':cy})
lab=gpd.GeoDataFrame(labels,geometry=[Point(d['x'],d['y']) for d in labels],crs='EPSG:4326')
print("labels merged:",len(lab))
print(sorted(lab.name.unique())[:40])
# assign nearest label within 0.06 deg (~6km)
from scipy.spatial import cKDTree
# distance point-to-line via geopandas sindex if available; fallback: line representative points sampled
names=['']*len(rivers)
if hasattr(rivers,'sindex') and rivers.sindex is not None:
    for _,lr in lab.iterrows():
        buf=lr.geometry.buffer(0.06)
        cand=list(rivers.sindex.intersection(buf.bounds))
        best=None;bd=1e9
        for ci in cand:
            dd=rivers.geometry.iloc[ci].distance(lr.geometry)
            if dd<bd: bd=dd;best=ci
        if best is not None and bd<=0.06 and names[best]=='':
            names[best]=lr['name']
rivers['river_name']=names
print("named segments:",sum(1 for n in names if n))
wc=rivers.width_pt.quantile([0.5,0.9,0.99])
print("width quantiles:",wc.to_dict())
def cls(w):
    return 'major' if w>=0.9 else ('medium' if w>=0.45 else 'minor')
rivers['class']=rivers.width_pt.map(cls)
rivers.insert(0,'fid',range(1,len(rivers)+1))
rivers=rivers[['fid','river_name','class','len_km','width_pt','geometry']]
rivers['len_km']=rivers.len_km.round(2)
print(rivers['class'].value_counts().to_dict(),"total km:",rivers.len_km.sum().round(0))
rivers.to_file('work/min/rivers_v1.shp')
lab.to_file('work/min/river_labels.shp')
if polys:
    lakes=gpd.GeoDataFrame(geometry=polys,crs='EPSG:4326')
    lakes['geometry']=lakes.geometry.intersection(nigeria)
    lakes=lakes[~lakes.geometry.is_empty]
    print("lakes after clip:",len(lakes), lakes.area.sum())
    lakes.to_file('work/min/lakes_v1.shp')
pickle.dump(rivers,open('work/min/rivers_v1.pkl','wb'))
print("done")
