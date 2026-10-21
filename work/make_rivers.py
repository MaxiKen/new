import pymupdf, numpy as np, geopandas as gpd, json, os, shutil
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union, linemerge
import sys; sys.path.insert(0,'work')
from transforms import min_page_to_lonlat
import warnings; warnings.filterwarnings('ignore')
AEA="+proj=aea +lat_1=4 +lat_2=12 +lat_0=0 +lon_0=9 +datum=WGS84 +units=m +no_defs +type=crs"
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'); p=d[0]
dr=p.get_drawings()
def paths_to_lines(sel):
    lines=[]
    for x in sel:
        cur=[]
        def flush():
            nonlocal cur
            if len(cur)>=2:
                # dedupe consecutive
                cc=[cur[0]]
                for q in cur[1:]:
                    if q!=cc[-1]: cc.append(q)
                if len(cc)>=2: lines.append(LineString(cc))
            cur=[]
        for it in x['items']:
            if it[0]=='l':
                a=(it[1].x,it[1].y); b=(it[2].x,it[2].y)
                if cur and cur[-1]==a: cur.append(b)
                else: flush(); cur=[a,b]
            elif it[0]=='c':
                p0=np.array([it[1].x,it[1].y]); p1=np.array([it[2].x,it[2].y]); p2=np.array([it[3].x,it[3].y]); p3=np.array([it[4].x,it[4].y])
                ts=np.linspace(0,1,9)
                pts=[tuple(((1-t)**3)*p0+3*((1-t)**2)*t*p1+3*(1-t)*(t**2)*p2+(t**3)*p3) for t in ts]
                if cur and cur[-1]==pts[0]: cur.extend(pts[1:])
                else: flush(); cur=pts[:]
            elif it[0]=='re':
                flush()
            else:
                flush()
        flush()
    return lines

blue=[x for x in dr if x.get('color')==(0.450980007648468,0.8745099902153015,1.0)]
page_lines=paths_to_lines(blue)
print(f"river page lines: {len(page_lines)}")
# to lonlat (VP transform)
ll_lines=[]
for ln in page_lines:
    coords=[min_page_to_lonlat(x,y) for x,y in ln.coords]
    if len(coords)>=2: ll_lines.append(LineString(coords))
riv=gpd.GeoDataFrame({"seg_id":range(1,len(ll_lines)+1)},geometry=ll_lines,crs=4326)
# merge connected lines into longer features where endpoints touch (tolerance via linemerge on union)
merged=linemerge(unary_union(ll_lines))
mparts=list(merged.geoms) if isinstance(merged,MultiLineString) else [merged]
print(f"after linemerge connected features: {len(mparts)}")
riv2=gpd.GeoDataFrame({"seg_id":range(1,len(mparts)+1)},geometry=mparts,crs=4326)
riv2m=riv2.to_crs(AEA); riv2['len_km']=(riv2m.geometry.length.values/1000).round(2)
print(f"total river length (frame): {riv2['len_km'].sum():.0f} km; features >=5km: {(riv2.len_km>=5).sum()}, 1-5km: {((riv2.len_km>=1)&(riv2.len_km<5)).sum()}, <1km: {(riv2.len_km<1).sum()}")
# Name attribution by proximity to Natural Earth major rivers (within 1.2 km for majority of segment length sampled)
ne=gpd.read_file("shapefiles/nigeria_online_layers/river_lines/river_lines.shp")
# dissolve NE by name (Benue/Benoue merge label)
ne['nm']=ne['RIVER_NAME'].replace({'Bénoué':'Benue'})
nem=ne.to_crs(AEA)
names=[]; conf=[]
from shapely.strtree import STRtree
netree=STRtree(list(nem.geometry.values)); negeoms=list(nem.geometry.values); nenames=list(ne['nm'].values)
for g in riv2m.geometry:
    # sample points every ~2km
    L=g.length; ns=max(3,int(L/2000)+1)
    pts=[g.interpolate(t) for t in np.linspace(0,L,ns)]
    votes={}
    for pt in pts:
        j=int(netree.nearest(pt))
        if pt.distance(negeoms[j])<=1200: votes[nenames[j]]=votes.get(nenames[j],0)+1
    if votes:
        best=max(votes,key=votes.get); frac=votes[best]/len(pts)
        names.append(best); conf.append(f"NE-match {frac:.0%} within 1.2km")
    else:
        names.append(""); conf.append("as printed; not a Natural-Earth major river")
riv2['river_nm']=names; riv2['name_src']=conf
riv2['source']="Mineral Resources Map of Nigeria 2023 (NGSA) PDF vector Rivers layer, VP georeferencing"
print(riv2[riv2.river_nm!=""].groupby('river_nm')['len_km'].agg(['count','sum']).to_string())
print(f"unnamed (small/tributary) features: {(riv2.river_nm=='').sum()} length {riv2.loc[riv2.river_nm=='','len_km'].sum():.0f} km")
OUT="corrected_delivery/05_Rivers"; os.makedirs(OUT,exist_ok=True)
riv2.to_file(f"{OUT}/rivers_as_printed_mineralmap2023.shp",encoding="utf-8")
# Nigeria-only clipped
admin=gpd.read_file("shapefiles/nigeria_admin0/nigeria_admin0.shp").geometry.iloc[0]
clip=[]
for _,r in riv2.iterrows():
    c=r.geometry.intersection(admin)
    if c.is_empty: continue
    parts=list(c.geoms) if isinstance(c,MultiLineString) else [c]
    for part in parts:
        if part.length>1e-9: clip.append({"seg_id":int(r.seg_id),"river_nm":r.river_nm,"name_src":r.name_src,"source":r.source,"geometry":part})
cl=gpd.GeoDataFrame(clip,crs=4326)
clm=cl.to_crs(AEA); cl['len_km']=(clm.geometry.length.values/1000).round(2)
cl=cl[cl.len_km>=0.05].copy(); cl['seg_id']=range(1,len(cl)+1)
print(f"clipped Nigeria-only: {len(cl)} features, {cl.len_km.sum():.0f} km")
cl.to_file(f"{OUT}/rivers_nigeria_only_from_mineralmap.shp",encoding="utf-8")
# Keep NE majors clearly renamed copy
os.makedirs(f"{OUT}/previous_major_rivers_only",exist_ok=True)
for ext in ['shp','shx','dbf','prj','cpg']:
    s=f"shapefiles/nigeria_online_layers/river_lines/river_lines.{ext}"
    if os.path.exists(s): shutil.copy(s,f"{OUT}/previous_major_rivers_only/rivers_MAJORONLY_NaturalEarth.{ext}")
qa={"as_printed_features":int(len(riv2)),"as_printed_total_km":round(float(riv2.len_km.sum()),1),
 "nigeria_only_features":int(len(cl)),"nigeria_only_total_km":round(float(cl.len_km.sum()),1),
 "named_major_features":int((riv2.river_nm!="").sum()),"small_tributary_features":int((riv2.river_nm=="").sum()),
 "previous_NE_features":35,"previous_NE_total_km_approx":5233,
 "note":"Previous river_lines (Natural Earth 10m) contains ONLY 12 major rivers (35 segments) and is NOT a complete river network. New layers extract every blue river line printed/vectorised on the Mineral Resources Map 2023, including small tributaries shown at 1:2,000,000. Names assigned only where coincident with a Natural Earth major river; blank river_nm = smaller river/tributary as printed (map does not name most small rivers). Very small streams below 1:2M printing scale cannot be recovered from this map."}
json.dump(qa,open(f"{OUT}/rivers_QA_report.json","w"),indent=2)
print(json.dumps(qa,indent=2))
# QA map
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(16,8),sharex=True,sharey=True)
ne.plot(ax=axes[0],color='blue',linewidth=0.7); gpd.GeoSeries([admin],crs=4326).boundary.plot(ax=axes[0],color='black',linewidth=0.8)
axes[0].set_title(f"PREVIOUS river_lines: {len(ne)} major-river segments only\n(12 named rivers, Natural Earth 10m)")
cl.plot(ax=axes[1],color='blue',linewidth=0.35); gpd.GeoSeries([admin],crs=4326).boundary.plot(ax=axes[1],color='black',linewidth=0.8)
axes[1].set_title(f"NEW rivers_nigeria_only_from_mineralmap: {len(cl)} features, {cl.len_km.sum():.0f} km\n(every river line printed on Mineral Map 2023, incl. small tributaries)")
plt.tight_layout(); plt.savefig("corrected_delivery/QA_maps_and_reports/QA_rivers_before_after.png",dpi=160)
print("river QA map done")
