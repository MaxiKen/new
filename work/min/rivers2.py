import pickle, numpy as np, geopandas as gpd, pandas as pd
from shapely.geometry import Point, MultiLineString
from shapely.ops import linemerge, unary_union
rivers=pickle.load(open('work/min/rivers_v1.pkl','rb'))
merged=linemerge(unary_union(list(rivers.geometry)))
if merged.geom_type=='LineString': parts=[merged]
else: parts=list(merged.geoms)
r=gpd.GeoDataFrame(geometry=parts,crs='EPSG:4326')
r['len_km']=(r.geometry.to_crs('EPSG:3857').length/1000).round(2)
r=r[r.len_km>0.05].reset_index(drop=True)
print("merged reaches:",len(r),"total km:",r.len_km.sum().round(0))
def cls(L): return 'major' if L>=120 else ('medium' if L>=35 else 'minor')
r['class']=r.len_km.map(cls)
print(r['class'].value_counts().to_dict())
# label clusters via proximity graph (page pt space)
L=pickle.load(open('work/min/mineral_layers.pkl','rb'))
def tf(x,y): return (0.0063408528*x+1.999778, -0.0063497677*y+16.326633)
words=L[9]['words']
F=[{'cx':(w[0]+w[2])/2,'cy':(w[1]+w[3])/2,'t':w[4],'x0':w[0],'x1':w[2]} for w in words]
n=len(F); parent=list(range(n))
def find(a):
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
for i in range(n):
    for j in range(i+1,n):
        if abs(F[i]['cx']-F[j]['cx'])<34 and abs(F[i]['cy']-F[j]['cy'])<20:
            parent[find(i)]=find(j)
clusters={}
for i in range(n): clusters.setdefault(find(i),[]).append(i)
print("clusters:",len(clusters))
labels=[]
with open('work/min/river_label_clusters.txt','w') as fh:
    for k,idxs in sorted(clusters.items(), key=lambda kv:-len(kv[1])):
        fr=[F[i] for i in idxs]
        C=np.array([[f['cx'],f['cy']] for f in fr])
        # PCA axis
        Cc=C-C.mean(axis=0)
        if len(fr)>1:
            _,_,Vt=np.linalg.svd(Cc,full_matrices=False); ax=Vt[0]
        else: ax=np.array([1.0,0.0])
        order=np.argsort(Cc@ax)
        s1=''.join(fr[i]['t'] for i in order)
        s2=''.join(fr[i]['t'] for i in order[::-1])
        cx,cy=tf(C[:,0].mean(),C[:,1].mean())
        labels.append({'cid':k,'n':len(fr),'s_fwd':s1,'s_rev':s2,'lon':cx,'lat':cy,'geometry':Point(cx,cy)})
        fh.write(f"cid={k} n={len(fr)} lon={cx:.3f} lat={cy:.3f} fwd='{s1}' rev='{s2}'\n")
lab=gpd.GeoDataFrame(labels,crs='EPSG:4326')
lab.to_pickle('work/min/river_labels_v2.pkl')
pickle.dump(r,open('work/min/rivers_v2_nomame.pkl','wb'))
print(open('work/min/river_label_clusters.txt').read())
