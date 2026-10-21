import pickle, numpy as np, geopandas as gpd, pandas as pd
r=pickle.load(open('work/min/rivers_v2_nomame.pkl','rb'))
lab=pickle.load(open('work/min/river_labels_v2.pkl','rb'))
CUR={256:'River Benue',158:'Anambra',301:'Chanchaga',204:'Owena',85:'Shasha',233:'Warra',
     129:'Komadugu Gana',45:'Komadugu Gana',277:'K. Goma',269:'Katsina-Ala',282:'Cross River',
     32:'River Niger',53:'River Niger',322:'River Niger',190:'River Benue',225:"Jama'are",
     102:'Oyan',113:'Oramiri',0:'',306:'Gaya',243:'T. Gaba',317:'Anambra'}
def clean(s):
    s=s.strip()
    return s
names=[]
for _,row in lab.iterrows():
    cid=row['cid']
    if cid in CUR: names.append(CUR[cid])
    else:
        s=row['s_fwd']
        names.append(s[:1].upper()+s[1:] if s else '')
lab['river_name']=names
lab=lab[lab.river_name!=''].reset_index(drop=True)
print("usable labels:",len(lab))
# nearest reach within 0.08 deg
r['river_name']=''
seed={}  # reach idx -> name
for _,lr in lab.iterrows():
    d=r.geometry.distance(lr.geometry)
    i=int(d.idxmin())
    if d[i]<=0.08 and (i not in seed):
        seed[i]=lr['river_name']
print("seed reaches:",len(seed))
# endpoint graph
def ends(g):
    c=list(g.coords); return (round(c[0][0],6),round(c[0][1],6)),(round(c[-1][0],6),round(c[-1][1],6))
from collections import defaultdict
node2reach=defaultdict(list)
E={}
for i,g in enumerate(r.geometry):
    a,b=ends(g); E[i]=(a,b)
    node2reach[a].append(i); node2reach[b].append(i)
def dir_at(g,node):
    c=list(g.coords)
    a=(round(c[0][0],6),round(c[0][1],6))
    if a==node: v=np.array(c[min(3,len(c)-1)])-np.array(c[0])
    else: v=np.array(c[max(0,len(c)-4)])-np.array(c[-1])
    nv=np.linalg.norm(v)
    return v/nv if nv>0 else v
assigned=dict(seed)
# propagate: walk from each seed in both directions choosing straightest continuation
for si,name in list(seed.items()):
    for end_i in [0,1]:
        cur=si; node=E[cur][end_i]; budget=0
        prev_dir=-dir_at(r.geometry.iloc[cur],node)  # direction of travel into node
        while budget<450:
            cand=[j for j in node2reach[node] if j!=cur]
            if not cand: break
            best=None;bd=-2
            for j in cand:
                v=dir_at(r.geometry.iloc[j],node)
                dot=float(np.dot(prev_dir,v))
                if dot>bd: bd=dot;best=j
            if best is None or bd<0.25: break
            if best in assigned and assigned[best]!=name: break
            assigned[best]=name
            a,b=E[best]; nxt=b if a==node else a
            prev_dir=-dir_at(r.geometry.iloc[best],nxt)
            budget+=r.len_km.iloc[best]; cur=best; node=nxt
for i,nm in assigned.items(): r.at[r.index[i],'river_name']=nm
named=r[r.river_name!='']
print("named reaches:",len(named),"named km:",named.len_km.sum().round(0),"of",r.len_km.sum().round(0))
print(named.groupby('river_name').len_km.sum().sort_values(ascending=False).head(20).to_dict())
r=r.rename(columns={'class':'len_class'})
r.insert(0,'fid',range(1,len(r)+1))
r=r[['fid','river_name','len_class','len_km','geometry']]
r.to_file('work/min/rivers_final.shp')
lab[['river_name','geometry']].to_file('work/min/river_labels_final.shp')
pickle.dump(r,open('work/min/rivers_final.pkl','wb'))
print("saved rivers_final", len(r))
