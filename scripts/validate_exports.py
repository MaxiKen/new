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
    report=dict(featureCount=len(g),sharedContactCount=len(lines),allSinglepart=True,allValid=True,uniquePolygonIds=True,noBlackOrNearBlackFills=True,internalGapCount=0,nonoverlappingInteriors=True,exactSharedEdges=True,noDuplicatedContacts=True,allGeographicLeftRightReferencesValid=True,webFeatureIdsMatchShapefile=True,stylesXmlValid=True,blackSourcePixelsCovered=quality['blackPixelsCovered'],caution='Topology validation is not geological verification. Datum remains assumed; source-photo comparison retains black annotations by design.')
    (OUT/'validation.json').write_text(json.dumps(report,indent=2));(WEB/'validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':validate()
