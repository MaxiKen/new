"""Revision 7: continuity-first, native-image interpretation, single shared edges, review artifacts.

No previous generated package is required. All output follows from the original
JPG and the transcribed legend. Color-based interpretation remains a DRAFT.
"""
from pathlib import Path
import csv, json, hashlib, zipfile, shutil
from collections import Counter
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching
from skimage.measure import label
from skimage.morphology import skeletonize
import rasterio
from rasterio.features import shapes, sieve, rasterize
from rasterio.transform import Affine
import shapely as sh
from shapely.geometry import shape, mapping, LineString
from shapely.affinity import affine_transform
from shapely.strtree import STRtree
from shapely.ops import polygonize
import shapefile
from pyproj import CRS, Geod
from xml.sax.saxutils import escape
from geometry import fill_labels, no_black_palette, smooth_samples, validate_coverage
from continuity import repair_annotation_bands, connected_bodies

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/map'
WEB = ROOT / 'public/data'
WORK = ROOT / '.cache/build'
for folder in (OUT, WEB, WORK): folder.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'pic NGSA geological-map-of-nigeria-.jpg'
CROP = (190, 190, 4274, 3526)


def log(message): print(message, flush=True)

def lab(rgb): return cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def classify():
    image = np.array(Image.open(SOURCE).convert('RGB'))
    rgb = image[CROP[1]:CROP[3], CROP[0]:CROP[2]].copy()
    units = []
    for i, row in enumerate((ROOT/'scripts/legend.txt').read_text().splitlines()):
        code, name = row.split('|')
        y = round(213.5 + i * (3495 - 213.5) / 91)
        color = np.median(image[y-8:y+8, 5589:5597].reshape(-1,3), axis=0).astype('uint8')
        units.append(dict(id=i+1, code=code, name=name, color='#'+''.join(f'{n:02x}' for n in color), legend_y=y))
    units += [dict(id=93, code='OGp', name='Unresolved map code OGp; no matching legend code', color='#ff797f', legend_y=0),
              dict(id=94, code='S', name='Unresolved map code S; no matching legend code', color='#6774ff', legend_y=0),
              dict(id=95, code='WATER', name='Mapped water / water-color interpretation; not geology', color='#99d8eb', legend_y=0)]
    palette = np.array([[int(u['color'][j:j+2],16) for j in (1,3,5)] for u in units],np.uint8)
    assert no_black_palette([u['color'] for u in units])
    smooth = cv2.medianBlur(rgb,3); colors = lab(smooth); plab = lab(palette[None])[0]
    allpal = np.vstack([plab, lab(np.array([[[255,255,255]]],np.uint8))[0]])
    distance, nearest = cKDTree(allpal).query(colors.reshape(-1,3),k=2)
    distance = distance.reshape(*rgb.shape[:2],2); nearest = nearest.reshape(*rgb.shape[:2],2)
    choice = nearest[:,:,0]; chroma=np.linalg.norm(colors[:,:,1:],axis=2)
    # Land footprint is based on substantial colored regions, never gridlines.
    land=((choice<94)&(chroma>22)&(smooth.max(2)>150)).astype('uint8')
    land=cv2.morphologyEx(land,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    land=cv2.morphologyEx(land,cv2.MORPH_CLOSE,np.ones((17,17),np.uint8))
    land=cv2.morphologyEx(land,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    contours,_=cv2.findContours(land,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    mask=np.zeros(choice.shape,np.uint8)
    cv2.drawContours(mask,[max(contours,key=cv2.contourArea)],-1,1,-1)
    mask=ndi.binary_fill_holes(mask)
    # Water is explicitly classified, never cut out to create blank holes.
    wm=((choice==94)&(distance[:,:,0]<12)&mask).astype('uint8')
    wm=cv2.morphologyEx(wm,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,cc,stats,_=cv2.connectedComponentsWithStats(wm,8)
    large=np.flatnonzero(stats[:,cv2.CC_STAT_AREA]>=60); large=large[large!=0]
    water=np.isin(cc,large)&mask
    # Neutral cartographic strokes are suppressed; broad true gray geological
    # regions are allowed. Pale lavender basalt is NOT neutral gray.
    neutral=(chroma<8)&(smooth.max(2)<225)
    graycore=cv2.erode(neutral.astype('uint8'),np.ones((17,17),np.uint8))>0
    neutral_stroke=neutral&~cv2.dilate(graycore.astype('uint8'),np.ones((5,5),np.uint8)).astype(bool)
    dark=rgb.max(2)<130
    annotations=dark|neutral_stroke
    annotations=cv2.dilate(annotations.astype('uint8'),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))>0
    valid=(choice<94)&(distance[:,:,0]<12)&(smooth.max(2)>120)&mask&~annotations
    cores=np.zeros(mask.shape,bool)
    for k in range(94):
        size=17 if np.linalg.norm(plab[k,1:])<8 else 5
        region=((choice==k)&valid).astype('uint8')
        cores |= cv2.erode(region,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(size,size)))>0
    seeds=np.where(cores,choice+1,0).astype('uint8')
    classes=fill_labels(seeds,mask)
    classes=sieve(classes,size=12,connectivity=4,mask=mask)
    classes[water]=95;classes[~mask]=0
    # Equivalent palette choices must not form artificial checkerboard contacts.
    groups=fcluster(linkage(plab[:94],method='complete'),t=3,criterion='distance')
    canonical=np.arange(96,dtype=np.uint8)
    alternatives={95:[95]}
    for group in np.unique(groups):
        members=np.flatnonzero(groups==group)+1;canonical[members]=members[0]
        for member in members:alternatives[int(member)]=[int(x) for x in members]
    # Remove the former "thin dark barrier" splitter. A black crossing is not
    # evidence that an already-connected lithological color body is separate.
    # Additional repairs require matching reliable ORIGINAL colors across a
    # short annotation-only band; water and known other geology are protected.
    band=cv2.dilate(annotations.astype('uint8'),np.ones((5,5),np.uint8)).astype(bool)&mask&~water
    reliable=np.where(valid&~band,choice+1,0).astype('uint8')
    reliable[cores]=(choice[cores]+1).astype('uint8')
    # Native visible color can be genuine thin geology even when erosion and
    # annotation dilation left no reliable core there. Do not bridge over it.
    source_lab=lab(rgb)
    raw_distance,raw_choice=cKDTree(allpal).query(source_lab.reshape(-1,3))
    raw_distance=raw_distance.reshape(mask.shape);raw_choice=raw_choice.reshape(mask.shape)
    observed=np.where((raw_choice<94)&(raw_distance<4)&(rgb.max(2)>150)
        &(np.linalg.norm(source_lab[:,:,1:],axis=2)>15)&mask&~dark,raw_choice+1,0).astype('uint8')
    before_classes=classes.copy()
    before_ids,_=connected_bodies(classes,canonical)
    classes,repair_mask,conflicts=repair_annotation_bands(
        classes,reliable,band,mask,water,canonical,max_gap=24,observed=observed)
    ids,table=connected_bodies(classes,canonical)
    assert np.array_equal(classes[observed>0],before_classes[observed>0])
    assert np.all(ids[mask]>0) and not np.any(ids[~mask])
    assert np.array_equal(classes[water],before_classes[water])
    assert np.array_equal(classes[reliable>0],before_classes[reliable>0])
    continuity=dict(blackStrokeSplittingEnabled=False,maxGapPixels=24,
        scanAxes=["horizontal","vertical","diagonal-down","diagonal-up"],
        distanceUnit="Euclidean source pixels",
        trustedBodiesProtected=True,
        supportedBandPixels=int(repair_mask.sum()),
        rejectedOrConflictingBandPixels=int(conflicts.sum()),
        connectedBodiesBeforeBandRepair=int(before_ids.max()),
        connectedBodiesAfterBandRepair=int(ids.max()),
        waterPixelsUnchanged=True,reliableClassPixelsUnchanged=True,visibleSourcePaintUnchanged=True,
        rationale='Dark strokes never subdivide an existing color component. Four-axis gap repair requires matching original-color endpoints, no water or reliable other unit; trusted bodies cannot be split. Only fully masked, wholly untrusted annotation fragments may be consumed.')
    (OUT/'continuity_method.json').write_text(json.dumps(continuity,indent=2))
    ambiguity=(nearest[:,:,1]<94)&((distance[:,:,1]-distance[:,:,0])<3)
    np.savez_compressed(WORK/'raster_qa.npz',ids=ids,mask=mask,dark=dark,annotations=annotations,ambiguity=ambiguity,table=table,repair_mask=repair_mask,canonical=canonical,original_classes=before_classes,revised_classes=classes,water=water,reliable_mask=reliable>0,observed=observed,annotation_band=band)
    log(f'Classification: {len(table)-1} body seeds, no unassigned interior pixels')
    return rgb,ids,table,units,alternatives,mask,dark,annotations,ambiguity


def refine(ids,rgb):
    polys=[];body=[]
    for geo,value in shapes(ids,mask=ids>0,transform=Affine.identity(),connectivity=4):
        g=shape(geo)
        if not g.is_valid:g=sh.make_valid(g)
        parts=[g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon']
        for part in parts:polys.append(part);body.append(int(value))
    polys=sh.coverage_clean(np.array(polys,dtype=object),snapping_distance=0)
    validate_coverage(polys)
    initial=sh.coverage_simplify(polys,tolerance=1,simplify_boundary=True)
    net=sh.line_merge(sh.union_all(sh.boundary(initial)))
    lines=np.array(list(net.geoms),dtype=object)
    dark=rgb.max(2)<130;dd=ndi.distance_transform_edt(~skeletonize(dark)).astype('float32')
    heavy=ndi.distance_transform_edt(dark)>1.8
    heavy=cv2.dilate(heavy.astype('uint8'),np.ones((7,7),np.uint8)).astype('float32')
    colors=lab(rgb)
    def sample(field,xy):return ndi.map_coordinates(field,[xy[:,1]-.5,xy[:,0]-.5],order=1,mode='nearest')
    bases=[];proposals=[];supports=[]
    for j,line in enumerate(lines):
        n=max(3,int(np.ceil(line.length))+1);step=line.length/(n-1)
        a=sh.get_coordinates(sh.line_interpolate_point(line,np.linspace(0,line.length,n)))
        closed=np.allclose(a[0],a[-1],atol=1e-8)
        if line.length<5:
            bases.append(a);proposals.append(a);supports.append(0);continue
        b=smooth_samples(a,2.2/max(step,.1),closed)
        tangent=np.gradient(b,axis=0);normal=np.c_[-tangent[:,1],tangent[:,0]]
        normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
        shifts=np.arange(-4,4.001,.5)
        trials=b[:,None,:]+normal[:,None,:]*shifts[None,:,None]
        flat=trials.reshape(-1,2);normals=np.repeat(normal,len(shifts),axis=0)
        distances=sample(dd,flat).reshape(n,-1)
        left=np.stack([sample(colors[:,:,k],flat+normals*5) for k in range(3)],1)
        right=np.stack([sample(colors[:,:,k],flat-normals*5) for k in range(3)],1)
        contrast=np.linalg.norm(left-right,axis=1).reshape(n,-1)
        eligible=(distances<=1.25)&(contrast>=9)&(sample(heavy,flat).reshape(n,-1)<.25)
        cost=1.5*distances**2+.22*shifts[None,:]**2;cost[~eligible]=1e6
        pick=cost.argmin(1);ok=eligible[np.arange(n),pick]
        mode='wrap' if closed else 'nearest'
        supported=ndi.gaussian_filter1d(ok.astype(float),4/max(step,.1),mode=mode)>.55
        weight=ok&supported;offset=shifts[pick]*weight
        numerator=ndi.gaussian_filter1d(offset,1.5/max(step,.1),mode=mode)
        denominator=ndi.gaussian_filter1d(weight.astype(float),1.5/max(step,.1),mode=mode)
        shift=np.divide(numerator,denominator,out=np.zeros_like(numerator),where=denominator>.2)*np.clip(denominator,0,1)
        if not closed:shift*=np.clip(np.minimum(np.arange(n),np.arange(n)[::-1])/5,0,1)
        b=smooth_samples(b+normal*shift[:,None],.7/max(step,.1),closed)
        delta=b-a;norm=np.linalg.norm(delta,axis=1)
        b=a+delta*np.minimum(1,4.5/np.maximum(norm,1e-10))[:,None]
        if closed:b[-1]=b[0]
        else:b[0]=a[0];b[-1]=a[-1]
        bases.append(a);proposals.append(b);supports.append(float(weight.mean()))
        if j%2000==0:log(f'Refining shared photo-guided arc {j}/{len(lines)}')
    strengths=np.ones(len(lines))
    def curves():return np.array([LineString(a+s*(b-a)) for a,b,s in zip(bases,proposals,strengths)],dtype=object)
    for iteration in range(12):
        network=curves();pairs=STRtree(network).query(network,predicate='crosses')
        bad=np.unique(np.r_[pairs.ravel(),np.flatnonzero(~sh.is_simple(network))]).astype(int)
        if not len(bad):break
        strengths[bad]*=.45
        if iteration>=8:strengths[bad]=0
    else:raise RuntimeError('Contact crossing safeguards failed')
    # Same face count is not sufficient: require a complete one-to-one
    # overlap assignment too. Back off if a tiny body otherwise loses identity.
    for attempt in range(10):
        network=curves()
        faces=np.array(list(polygonize(sh.union_all(network))),dtype=object)
        try:
            if len(faces)!=len(initial):raise ValueError('Face count changed')
            pairs=STRtree(initial).query(faces,predicate='intersects')
            overlap=sh.area(sh.intersection(faces[pairs[0]],initial[pairs[1]]))
            score=2*overlap/(sh.area(faces[pairs[0]])+sh.area(initial[pairs[1]]))
            good=score>0
            costs=coo_matrix((1.00001-score[good],(pairs[0,good],pairs[1,good])),shape=(len(faces),len(initial))).tocsr()
            rr,cc=min_weight_full_bipartite_matching(costs)
            order=np.empty(len(initial),int);order[cc]=rr
            final=faces[order];validate_coverage(final)
            break
        except (ValueError,AssertionError):
            strengths*=.5
            if attempt>=8:strengths[:]=0
    else:raise RuntimeError('Cannot preserve one-to-one contact topology')
    # Remove redundant vertices with a shared coverage operation (both sides).
    final=sh.coverage_simplify(final,tolerance=.13,simplify_boundary=True)
    footprint=validate_coverage(final)
    contacts=sh.line_merge(sh.union_all(sh.boundary(final)))
    contacts=np.array(list(contacts.geoms),dtype=object)
    log(f'Geometry: {len(final)} singlepart polygons, {len(contacts)} unique shared arcs')
    np.save(WORK/'polygons_wkb.npy',np.array([p.wkb for p in final],dtype=object),allow_pickle=True)
    return final,np.array(body),contacts,footprint,dict(photo_evidence_arcs=sum(v>0 for v in supports),arcs_reduced=int((strengths<1).sum()),smoothing_sigma_pixels=2.2,max_proposed_shift_pixels=4.5)


def georeference():
    xs=[408.5,736.5,1065.5,1393.5,1722.5,2050,2378.5,2707,3035.5,3364,3691.5,4020.5]
    ys=[484.5,1141,1469.5,1798,2126.5,2454.5,2782.5,3111.5,3439.5]
    a,b=np.polyfit(xs,np.arange(3,15),1);c,d=np.polyfit(ys,[13,11,10,9,8,7,6,5,4],1)
    return Affine(a,0,a*CROP[0]+b,0,c,c*CROP[1]+d)


def write_styles(units):
    parts=['<qgis version="3.34" styleCategories="Symbology"><renderer-v2 type="categorizedSymbol" attr="class_id"><categories>']
    for i,u in enumerate(units):
        text=escape(u['code']+' — '+u['name'],{'"':'&quot;'})
        parts.append(f'<category type="long" value="{i+1}" symbol="{i}" label="{text}" render="true"/>')
    parts.append('</categories><symbols>')
    for i,u in enumerate(units):
        color=','.join(str(int(u['color'][k:k+2],16)) for k in (1,3,5))+',255'
        parts.append(f'<symbol type="fill" name="{i}"><layer class="SimpleFill"><Option type="Map"><Option name="color" value="{color}" type="QString"/><Option name="outline_style" value="no" type="QString"/></Option></layer></symbol>')
    parts.append('</symbols></renderer-v2></qgis>')
    (OUT/'ngsa_geology.qml').write_text('\n'.join(parts))
    (OUT/'shared_contacts.qml').write_text('<qgis version="3.34" styleCategories="Symbology"><renderer-v2 type="singleSymbol"><symbols><symbol type="line" name="0"><layer class="SimpleLine"><Option type="Map"><Option name="line_color" value="103,145,129,255" type="QString"/><Option name="line_width" value="0.08" type="QString"/><Option name="joinstyle" value="round" type="QString"/></Option></layer></symbol></symbols></renderer-v2></qgis>')


def export(rgb,ids,table,units,alternatives,mask,dark,annotations,ambiguity,polygons,bodies,contacts,footprint,refinement):
    T=georeference();trans=[T.a,T.b,T.d,T.e,T.c,T.f]
    geod=Geod(ellps='WGS84');prj=CRS.from_epsg(4326).to_wkt(version='WKT1_ESRI')
    # Statistics summarize source pixels by reconstructed body, not confidence.
    counts=np.bincount(ids.ravel(),minlength=len(table))
    ann=np.bincount(ids.ravel(),weights=annotations.ravel(),minlength=len(table))/np.maximum(counts,1)*100
    amb=np.bincount(ids.ravel(),weights=ambiguity.ravel(),minlength=len(table))/np.maximum(counts,1)*100
    writer=shapefile.Writer(str(OUT/'ngsa_geology'),shapeType=shapefile.POLYGON,encoding='utf-8')
    for f in [('poly_id','N',10,0),('body_id','N',10,0),('class_id','N',3,0),('unit_code','C',12,0),('lithology','C',130,0),('hex_color','C',7,0),('area_km2','F',16,3),('ann_pct','F',6,1),('ambig_pct','F',6,1),('candidates','C',60,0),('contact_qa','C',24,0),('qa_status','C',24,0)]:writer.field(*f)
    features=[];class_counts=Counter();issue_counts=Counter()
    repair_mask=np.load(WORK/'raster_qa.npz')['repair_mask']
    repaired=np.bincount(ids[repair_mask],minlength=len(table))
    for i,(poly,body) in enumerate(zip(polygons,bodies),1):
        cls,original,split=map(int,table[body]);u=units[cls-1]
        wp=sh.orient_polygons(affine_transform(poly,trans));area=abs(geod.geometry_area_perimeter(wp)[0])/1e6
        problems=[]
        if cls==95:problems.append('water')
        elif cls>92:problems.append('unresolved-code')
        if len(alternatives[cls])>1:problems.append('similar-colors')
        if repaired[body]:problems.append('band-repaired')
        if ann[body]>35:problems.append('annotation-heavy')
        if poly.area/poly.length<2.5:problems.append('narrow-body')
        # Preserve narrow candidates and flag them; automatically deleting them
        # could erase real geological bodies rather than just printed artifacts.
        qa='WATER_NOT_GEOLOGY' if cls==95 else ('MAP_CODE_UNRESOLVED' if cls>92 else 'DRAFT_REVIEW')
        writer.shape(mapping(wp));writer.record(i,int(body),cls,u['code'],u['name'],u['color'],area,float(ann[body]),float(amb[body]),','.join(map(str,alternatives[cls])),'ANNOTATION_BAND_REPAIR' if repaired[body] else 'COLOR_CONTACT_DRAFT',qa)
        rings=[np.round(np.array(r.coords),3).tolist() for r in [poly.exterior]+list(poly.interiors)]
        features.append(dict(id=i,body=int(body),classId=cls,area=round(area,3),annotation=round(float(ann[body]),1),ambiguity=round(float(amb[body]),1),issues=problems,bbox=[round(v,3) for v in poly.bounds],rings=rings))
        class_counts[cls]+=1;issue_counts.update(problems)
    writer.close()
    e=shapefile.Writer(str(OUT/'shared_contacts'),shapeType=shapefile.POLYLINE)
    for f in [('edge_id','N',10),('left_id','N',10),('right_id','N',10)]:e.field(*f)
    tree=STRtree(polygons);adjacencies=[]
    def side(point):
        hit=tree.query(point,predicate='intersects');return int(hit[0])+1 if len(hit) else 0
    for i,line in enumerate(contacts,1):
        m=line.length/2;eps=min(.1,line.length/10)
        p=np.array(line.interpolate(m).coords[0]);v=np.array(line.interpolate(m+eps).coords[0])-np.array(line.interpolate(m-eps).coords[0])
        n=np.array([-v[1],v[0]])/max(np.linalg.norm(v),1e-10)
        # Reverse pixel left/right because geographic y increases northward.
        left=side(sh.Point(p-n*.008));right=side(sh.Point(p+n*.008))
        assert left!=right,(i,left,right)
        e.shape(mapping(affine_transform(line,trans)));e.record(i,left,right);adjacencies.append([left,right])
    e.close()
    f=shapefile.Writer(str(OUT/'mapped_footprint'),shapeType=shapefile.POLYGON);f.field('name','C',60)
    f.shape(mapping(affine_transform(footprint,trans)));f.record('Covered source-map footprint, not official country boundary');f.close()
    for name in ['ngsa_geology','shared_contacts','mapped_footprint']:
        (OUT/f'{name}.prj').write_text(prj);(OUT/f'{name}.cpg').write_text('UTF-8')
    for u in units:u.update(count=class_counts[u['id']],candidates=alternatives[u['id']])
    with open(OUT/'legend.csv','w') as file:
        w=csv.DictWriter(file,fieldnames=units[0].keys(),lineterminator='\n');w.writeheader();w.writerows(units)
    Image.fromarray(rgb).save(WEB/'source.jpg',quality=92)
    (OUT/'source_reference.jgw').write_text('\n'.join(map(str,[T.a,T.d,T.b,T.e,T.c+T.a/2,T.f+T.e/2])))
    (OUT/'source_reference.prj').write_text(prj)
    # The output geometry, NOT just the seed raster, is checked for gaps.
    output_raster=rasterize([(p,i+1) for i,p in enumerate(polygons)],out_shape=mask.shape,transform=Affine.identity(),dtype='int32')
    interior=ndi.distance_transform_edt(np.pad(mask,1))[1:-1,1:-1]>5
    assert not np.any(interior&(output_raster==0))
    black_inside=dark&interior
    assert np.all(output_raster[black_inside]>0)
    stats=dict(revision=7,built='2026-10-10',featureCount=len(features),contactCount=len(contacts),classCount=len(class_counts),blackFillClasses=0,interiorGaps=0,blackPixelsCovered=int(black_inside.sum()),blackPixelsTested=int(black_inside.sum()),overlaps=False,singlepart=True,crs='EPSG:4326 — assumed datum',sourceSize=[6600,3675],crop=list(CROP),width=rgb.shape[1],height=rgb.shape[0],sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),issueCounts=dict(issue_counts),refinement=refinement,continuity=json.loads((OUT/'continuity_method.json').read_text()),limitations=['Automated geological draft, not exhaustive manual verification.','Map-only codes, similar colors, narrow bodies and inferred contacts need review.','Gap-free within the mapped footprint, not the page or an official country boundary.','Original source photo intentionally retains black annotations in comparison mode.'])
    data=dict(stats=stats,classes=units,features=features,contacts=[np.round(np.array(line.coords),3).tolist() for line in contacts],transform=[T.a,T.b,T.c,T.d,T.e,T.f],extent=list(footprint.bounds),regions=[dict(name='Whole map',box=list(footprint.bounds)),dict(name='Jos Plateau',box=[1900,1050,2600,1780]),dict(name='Southwest',box=[430,1810,1340,2490]),dict(name='Katsina',box=[1430,220,2220,920]),dict(name='Delta',box=[1000,2520,2200,3250])])
    (WEB/'map.json').write_text(json.dumps(data,separators=(',',':')))
    (OUT/'quality.json').write_text(json.dumps(stats,indent=2));(WEB/'quality.json').write_text(json.dumps(stats,indent=2))
    write_styles(units)
    log(json.dumps(stats,indent=2))


def main():
    classified=classify();rgb,ids,*_=classified
    result=refine(ids,rgb)
    export(*classified,*result)

if __name__=='__main__':main()
