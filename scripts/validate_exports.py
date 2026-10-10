"""Validate persisted outputs independently of intermediate build geometry."""
from pathlib import Path
import json, sys, zipfile, xml.etree.ElementTree as ET
import numpy as np
import shapefile
import shapely as sh
from shapely.geometry import shape
from shapely.strtree import STRtree
from geometry import validate_coverage, no_black_palette
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/map';WEB=ROOT/'public/data'

def validate():
    reader=shapefile.Reader(str(OUT/'ngsa_geology'),encoding='utf-8');records=reader.records()
    g=np.array([shape(p.__geo_interface__) for p in reader.shapes()],dtype=object)
    union=validate_coverage(g)
    ids=[int(r['poly_id']) for r in records]
    assert len(g)==len(records)==len(set(ids))
    assert no_black_palette([r['hex_color'] for r in records])
    assert all(r['class_id']>0 for r in records)
    footprint=shape(shapefile.Reader(str(OUT/'mapped_footprint')).shape(0).__geo_interface__)
    assert union.symmetric_difference(footprint).area<1e-9
    edges=shapefile.Reader(str(OUT/'shared_contacts'));edge_records=edges.records()
    lines=np.array([shape(p.__geo_interface__) for p in edges.shapes()],dtype=object)
    assert sh.is_simple(lines).all()
    line_union=sh.union_all(lines);boundary_union=sh.union_all(sh.boundary(g))
    assert abs(float(sh.length(lines).sum())-line_union.length)<1e-7
    assert line_union.symmetric_difference(boundary_union).length<1e-7
    tree=STRtree(g);bad=[]
    for i,(line,row) in enumerate(zip(lines,edge_records)):
        assert row['left_id']!=row['right_id']
        m=line.length/2;eps=min(1e-5,line.length/10)
        p=np.array(line.interpolate(m).coords[0]);v=np.array(line.interpolate(m+eps).coords[0])-np.array(line.interpolate(m-eps).coords[0])
        n=np.array([-v[1],v[0]])/max(np.linalg.norm(v),1e-14)
        for sign,key in [(1,'left_id'),(-1,'right_id')]:
            hits=tree.query(sh.Point(p+sign*n*.00001),predicate='intersects')
            actual=ids[int(hits[0])] if len(hits) else 0
            if actual!=row[key]:bad.append((i+1,key,actual,row[key]))
    assert not bad,('Invalid adjacency references',bad[:10])
    # In this continuity-first product, equivalent-color adjacent interiors
    # must be a single connected feature, not two pieces cut by a dark stroke.
    by_id={int(r['poly_id']):r for r in records}
    same_family=[]
    for row in edge_records:
        if not row['left_id'] or not row['right_id']:continue
        left=by_id[row['left_id']];right=by_id[row['right_id']]
        candidates={int(x) for x in left['candidates'].split(',')}
        if int(right['class_id']) in candidates:same_family.append(row['edge_id'])
    assert not same_family,('Artificial same-family seams remain',same_family[:10])
    assert all(r['contact_qa']!='SPLIT_NEEDS_REVIEW' for r in records)
    method=json.loads((OUT/'continuity_method.json').read_text())
    assert method['blackStrokeSplittingEnabled'] is False
    assert method['waterPixelsUnchanged'] and method['reliableClassPixelsUnchanged']
    audit=json.loads((WEB/'continuity.json').read_text())
    assert audit['summary']['currentFeatureCount']==len(g)
    assert len(audit['changes'])==audit['summary']['restoredContinuousBodies']
    assert len(audit['removedContacts'])==audit['summary']['previousInternalSeamsRemoved']
    assert all(by_id[c['featureId']]['prior_n']==len(c['previousIds']) for c in audit['changes'])
    assert all(len(c['previousIds'])>=2 and min(c['retainedFractions'])>=.8 for c in audit['changes'])
    data=json.loads((WEB/'map.json').read_text())
    assert len(data['features'])==len(g)
    assert set(f['id'] for f in data['features'])==set(ids)
    assert no_black_palette([c['color'] for c in data['classes']])
    # Browser coordinates are only rounded for rendering. Match their bounds
    # and feature IDs, and do not treat the display JSON as the GIS source.
    for f in data['features']:
        assert len(f['rings'])>=1 and all(r[0]==r[-1] for r in f['rings'])
    for path in OUT.glob('*.qml'):ET.parse(path)
    quality=json.loads((OUT/'quality.json').read_text())
    assert quality['blackPixelsCovered']==quality['blackPixelsTested']
    assert quality['interiorGaps']==0 and not quality['overlaps']
    report=dict(noArtificialSameFamilySeams=True,darkStrokeSplitterDisabled=True,continuityAncestryMatchesGis=True,featureCount=len(g),sharedContactCount=len(lines),allSinglepart=True,allValid=True,uniquePolygonIds=True,noBlackOrNearBlackFills=True,internalGapCount=0,nonoverlappingInteriors=True,exactSharedEdges=True,noDuplicatedContacts=True,allGeographicLeftRightReferencesValid=True,webFeatureIdsMatchShapefile=True,stylesXmlValid=True,blackSourcePixelsCovered=quality['blackPixelsCovered'],caution='Topology validation is not geological verification. Datum remains assumed; source-photo comparison retains black annotations by design.')
    (OUT/'validation.json').write_text(json.dumps(report,indent=2));(WEB/'validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':validate()
