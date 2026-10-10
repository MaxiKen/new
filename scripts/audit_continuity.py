"""Trace revision-5 fragments to current continuous bodies for visual review.

This is an overlap/ancestry audit, not proof of geological identity. The
original photo remains available to inspect every restored candidate.
"""
from pathlib import Path
import subprocess,json,hashlib,csv,shapefile
from collections import defaultdict, Counter
import numpy as np,shapely as sh
from shapely.geometry import Polygon,LineString
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1];WEB=ROOT/'public/data';OUT=ROOT/'data/map'
BASE='a62427bf26b3861fe58221a3f718626daa0455d8'
path=ROOT/'.cache/baseline/map_v5.json'
if path.exists():blob=path.read_bytes()
else:blob=subprocess.check_output(['git','show',f'{BASE}:public/data/map.json'],cwd=ROOT)
if hashlib.sha256(blob).hexdigest()!='fae56e173aa23c96b73f74821fc106488215de73fed75e30029012ae0ae598e2':
    raise ValueError('Baseline cache does not match the named revision-5 commit')
old=json.loads(blob);new=json.loads((WEB/'map.json').read_text())
# Idempotent: ancestry tags are regenerated; direct band-repair flags are
# independent and survive. Never accumulate stale previous IDs on reruns.
for f in new['features']:
    f['issues']=[v for v in f['issues'] if v!='continuity-restored']
    f.pop('previousIds',None)
def polygons(data):
    return np.array([sh.make_valid(Polygon(f['rings'][0],f['rings'][1:])) for f in data['features']],object)
a=polygons(old);b=polygons(new);tree=STRtree(b);otree=STRtree(a)
pairs=tree.query(a,predicate='intersects')
areas=sh.area(sh.intersection(a[pairs[0]],b[pairs[1]]))
best={}
for oi,ni,area in zip(pairs[0],pairs[1],areas):
    fraction=area/a[oi].area
    of=old['features'][oi];nf=new['features'][ni]
    family=new['classes'][nf['classId']-1]['candidates']
    if fraction>=.8 and of['classId'] in family and fraction>best.get(int(oi),(-1,0))[1]:
        best[int(oi)]=(int(ni),float(fraction))
parents=defaultdict(list)
for oi,(ni,fraction) in best.items():parents[ni].append((oi,fraction))
restored={ni:entries for ni,entries in parents.items() if len(entries)>=2}
old_owner={oi:ni for ni,entries in restored.items() for oi,_ in entries}
seams=[];seam_counts=defaultdict(int)
for xy in old['contacts']:
    line=LineString(xy)
    if line.length<1:continue
    m=line.length/2;eps=min(.15,line.length/10)
    p=np.array(line.interpolate(m).coords[0]);v=np.array(line.interpolate(m+eps).coords[0])-np.array(line.interpolate(m-eps).coords[0])
    normal=np.array([-v[1],v[0]])/max(np.linalg.norm(v),1e-10)
    h1=otree.query(sh.Point(p+normal*.03),predicate='intersects');h2=otree.query(sh.Point(p-normal*.03),predicate='intersects')
    if len(h1)!=1 or len(h2)!=1 or h1[0]==h2[0]:continue
    oi,oj=int(h1[0]),int(h2[0]);ni=old_owner.get(oi)
    if ni is None or old_owner.get(oj)!=ni:continue
    # Require a real removed interior seam, not just a contact moved sideways.
    inset=b[ni].buffer(-.25)
    if inset.is_empty or line.intersection(inset).length/line.length<.6:continue
    seams.append(dict(featureId=new['features'][ni]['id'],previousIds=[old['features'][oi]['id'],old['features'][oj]['id']],points=xy))
    seam_counts[ni]+=1
changes=[]
for ni,entries in restored.items():
    if not seam_counts[ni]:continue
    f=new['features'][ni]
    f['previousIds']=[old['features'][oi]['id'] for oi,_ in entries]
    if 'continuity-restored' not in f['issues']:f['issues'].append('continuity-restored')
    changes.append(dict(featureId=f['id'],previousIds=f['previousIds'],retainedFractions=[round(fr,4) for _,fr in entries],removedContacts=seam_counts[ni],bbox=f['bbox'],classId=f['classId']))
changes.sort(key=lambda c:(-c['removedContacts'],c['featureId']))
method=json.loads((OUT/'continuity_method.json').read_text())
summary=dict(baselineRevision=5,baselineCommit=BASE,baselineSha256=hashlib.sha256(blob).hexdigest(),previousFeatureCount=len(a),currentFeatureCount=len(b),restoredContinuousBodies=len(changes),previousInternalSeamsRemoved=len(seams),sourceSupportedBandPixels=method['supportedBandPixels'],policy='Connected colors are not split by dark overprints; no proximity-only or global same-color dissolve.',caution='Ancestry/overlap evidence, not exhaustive geological verification. IDs changed: use previousIds for tracing reviewed merges.')
audit=dict(summary=summary,changes=changes,removedContacts=seams)
(WEB/'continuity.json').write_text(json.dumps(audit,separators=(',',':')))
(OUT/'continuity_review.json').write_text(json.dumps(dict(summary=summary,changes=changes),indent=2))
# Carry the restoration status into the GIS DBF, not just the browser.
r=shapefile.Reader(str(OUT/'ngsa_geology'),encoding='utf-8')
fields=r.fields[1:];rows=r.records();geometries=r.shapes();r.close()
names=[f[0] for f in fields]
if 'prior_n' not in names:fields.append(['prior_n','N',6,0])
lookup={c['featureId']:len(c['previousIds']) for c in changes}
w=shapefile.Writer(str(ROOT/'.cache/build/audited'),shapeType=shapefile.POLYGON,encoding='utf-8')
for field in fields:w.field(*field)
for g,row in zip(geometries,rows):
    values=list(row)
    if len(values)<len(fields):values.append(0)
    n=lookup.get(int(row['poly_id']),0);values[[f[0] for f in fields].index('prior_n')]=n
    direct='band-repaired' in new['features'][int(row['poly_id'])-1]['issues']
    values[names.index('contact_qa')]='CONTINUITY_RESTORED' if n else ('ANNOTATION_BAND_REPAIR' if direct else 'COLOR_CONTACT_DRAFT')
    w.shape(g);w.record(*values)
w.close()
for ext in ['shp','shx','dbf']:(ROOT/f'.cache/build/audited.{ext}').replace(OUT/f'ngsa_geology.{ext}')
with open(OUT/'continuity_crosswalk.csv','w') as f:
    writer=csv.writer(f,lineterminator='\n');writer.writerow(['previous_revision','previous_poly_id','current_poly_id','retained_area_fraction','same_palette_family'])
    for oi,(ni,fraction) in sorted(best.items()):writer.writerow([5,old['features'][oi]['id'],new['features'][ni]['id'],round(fraction,6),True])
new['stats']['continuityReview']=summary
new['stats']['issueCounts']=dict(Counter(issue for f in new['features'] for issue in f['issues']))
(WEB/'map.json').write_text(json.dumps(new,separators=(',',':')))
for folder in [OUT,WEB]:(folder/'quality.json').write_text(json.dumps(new['stats'],indent=2))
print(json.dumps(summary,indent=2))
