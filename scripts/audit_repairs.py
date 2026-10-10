"""Publish localized, inspectable annotation repairs and source safeguards."""
from pathlib import Path
import json,numpy as np,shapely as sh
from skimage.measure import label
from scipy import ndimage as ndi
from shapely.geometry import Polygon
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/map';WEB=ROOT/'public/data'
q=np.load(ROOT/'.cache/build/raster_qa.npz');data=json.loads((WEB/'map.json').read_text())
changed=q['repair_mask'];old=q['original_classes'];new=q['revised_classes'];ids=q['ids']
assert not np.any(changed & (~q['annotation_band']|q['water']|q['reliable_mask']|(q['observed']>0)))
assert np.array_equal(old[q['water']],new[q['water']])
assert np.array_equal(old[q['observed']>0],new[q['observed']>0])
patches=label(np.where(changed,ids,0),connectivity=1)
lookup={f['body']:f['id'] for f in data['features']};areas=[]
for i,sl in enumerate(ndi.find_objects(patches),1):
    if sl is None:continue
    local=patches[sl]==i;y,x=np.nonzero(local);y+=sl[0].start;x+=sl[1].start
    body=int(ids[y[0],x[0]])
    areas.append(dict(featureId=lookup[body],pixels=len(x),bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],
                      previousClassIds=list(map(int,np.unique(old[y,x]))),classIds=list(map(int,np.unique(new[y,x])))))
areas.sort(key=lambda a:(-a['pixels'],a['featureId'],a['bbox']))
# Native-photo spot check: two clearly enclosed OGp lenses separated by visible
# GG/Ch paint must NOT be bridged merely because both are pink and close.
polys=np.array([Polygon(f['rings'][0],f['rings'][1:]) for f in data['features']],object);tree=STRtree(polys)
selected=[]
for x,y in [(2410,2610),(2442,2610)]:
    hits=tree.query(sh.Point(x-190+.5,y-190+.5),predicate='intersects')
    assert len(hits)==1
    f=data['features'][int(hits[0])];assert f['classId']==93;selected.append(f['id'])
assert len(set(selected))==2,'Distinct original-photo OGp lenses wrongly joined'
report=dict(summary=dict(repairedSourcePixels=int(changed.sum()),localizedRepairAreas=len(areas),affectedBodies=len(set(a['featureId'] for a in areas)),
        originalVisiblePaintPreserved=True,waterPreserved=True,repairsRestrictedToAnnotationBands=True,
        caution='Source-supported interpolation, not independent geological certification. Some annotation artifacts and omitted thin units remain.'),
        areas=areas,sourceChecks=[dict(name='Separate pink OGp lenses: real intervening units preserved',sourcePixelSamples=[[2410,2610],[2442,2610]],
        featureIds=selected,bbox=[2160,2330,2320,2490],passed=True)])
for path in [OUT/'annotation_repairs.json',WEB/'repairs.json']:path.write_text(json.dumps(report,separators=(',',':')))
print(json.dumps(report['summary'],indent=2));print('Protected source example:',selected)
