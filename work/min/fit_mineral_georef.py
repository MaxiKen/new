import pickle, numpy as np, json, geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import cKDTree
from pyproj import Transformer
import warnings; warnings.filterwarnings('ignore')

layers=pickle.load(open('work/min/mineral_layers.pkl','rb'))
# densify boundary segments in page coords
def densify(drawings, step=2.0):
    pts=[]
    for x in drawings:
        for it in x['items']:
            if it[0]=='l':
                p1,p2=it[1],it[2]
                n=max(2,int(np.hypot(p2.x-p1.x,p2.y-p1.y)/step))
                for t in np.linspace(0,1,n): pts.append((p1.x+t*(p2.x-p1.x), p1.y+t*(p2.y-p1.y)))
            elif it[0]=='c':
                p0,p1,p2,p3=it[1],it[2],it[3],it[4]
                for t in np.linspace(0,1,12):
                    mt=1-t
                    pts.append((mt**3*p0.x+3*mt*mt*t*p1.x+3*mt*t*t*p2.x+t**3*p3.x,
                                mt**3*p0.y+3*mt*mt*t*p1.y+3*mt*t*t*p2.y+t**3*p3.y))
            elif it[0]=='re':
                r=it[1]; pts += [(r.x0,r.y0),(r.x1,r.y0),(r.x1,r.y1),(r.x0,r.y1)]
    return np.array(pts)

bnd=densify(layers[12]['drawings'], step=2.0)
print(f"boundary densified pts: {len(bnd)}")
# Separate red thick drawings? They are in same layer; check: 4 red w2.88 - likely frame/division? keep, robust fit handles.

ref=gpd.read_file('shapefiles/nigeria_admin0/nigeria_admin0.shp')
refline=ref.geometry.iloc[0].boundary
# densify ref boundary in metric, build KDTree in degrees-scaled space (lon*cos, lat)
refm=gpd.GeoSeries([refline],crs='EPSG:4326').to_crs('EPSG:32632').iloc[0]
nseg=int(refm.length/400)
ref_pts_m=np.array([(p.x,p.y) for p in [refm.interpolate(d) for d in np.linspace(0,refm.length,nseg)]])
tr_inv=Transformer.from_crs('EPSG:32632','EPSG:4326',always_xy=True)
ref_lon,ref_lat=tr_inv.transform(ref_pts_m[:,0],ref_pts_m[:,1])
coslat=np.cos(np.radians(9.5))
tree=cKDTree(np.column_stack([ref_lon*coslat, ref_lat]))
ref_ll=np.column_stack([ref_lon,ref_lat])
print(f"ref densified pts: {len(ref_ll)}")

def vp(x,y):
    return (2.47619+(x-74.23969)/(2051.1915-74.23969)*(15.02138-2.47619),
            14.04668-(y-358.72388)/(1967.70117-358.72388)*(14.04668-3.83671))

def evaluate(fn, label):
    lon=np.empty(len(bnd)); lat=np.empty(len(bnd))
    lon[:],lat[:]=fn(bnd[:,0],bnd[:,1])
    d,idx=tree.query(np.column_stack([lon*coslat,lat]))
    dkm=d*111.0
    print(f"{label:28s} median={np.median(dkm):.3f}km mean={dkm.mean():.3f} p90={np.percentile(dkm,90):.3f} p95={np.percentile(dkm,95):.3f} frac<2km={(dkm<2).mean():.3f}")
    return dkm, idx, lon, lat

evaluate(lambda x,y: vp(x,y), 'VP embedded')
def prev(x,y):
    py=2160-y
    return (8.999624062683695+6.3408036208710055*(x-1104.0922160059586)/1000,
            10.488502044741583+6.350936179071387*(py-1241.0996111966826)/1000)
evaluate(prev, 'PREV boundary-fit')

# ICP: axis-aligned affine lon=a x + b ; lat = c y + d ; init VP coefficients
a=(15.02138-2.47619)/(2051.1915-74.23969); b=2.47619-a*74.23969
c=-(14.04668-3.83671)/(1967.70117-358.72388); d=14.04668-c*358.72388
print(f"\ninit a={a:.10f} b={b:.6f} c={c:.10f} d={d:.6f} (pt/deg x={1/a:.4f} y={-1/c:.4f})")
for it in range(8):
    lon=a*bnd[:,0]+b; lat=c*bnd[:,1]+d
    dist,idx=tree.query(np.column_stack([lon*coslat,lat]))
    tgt=ref_ll[idx]
    resid=np.hypot((lon-tgt[:,0])*coslat, lat-tgt[:,1])*111
    # robust weights: huber-ish + trim worst 5%
    w=np.ones(len(bnd))
    mad=np.median(resid)*1.4826+1e-9
    w=np.minimum(1.0, (3*mad)/np.maximum(resid,1e-9))
    keep=resid<np.percentile(resid,92)
    # weighted LS per axis
    X=np.column_stack([bnd[keep,0], np.ones(keep.sum())])
    W=np.diag(w[keep])
    solx=np.linalg.lstsq(X*np.sqrt(w[keep])[:,None], tgt[keep,0]*np.sqrt(w[keep]), rcond=None)[0]
    Y=np.column_stack([bnd[keep,1], np.ones(keep.sum())])
    soly=np.linalg.lstsq(Y*np.sqrt(w[keep])[:,None], tgt[keep,1]*np.sqrt(w[keep]), rcond=None)[0]
    a,b,c,d=solx[0],solx[1],soly[0],soly[1]
    print(f" iter{it}: a={a:.10f} b={b:.6f} c={c:.10f} d={d:.6f} median_resid={np.median(resid):.3f}km keep={keep.sum()}")
def icp(x,y): return a*x+b, c*y+d
evaluate(icp,'ICP axis-aligned (new)')
print(f" pt/deg x={1/a:.4f} y={-1/c:.4f}")
# full affine variant for comparison (one-shot from ICP correspondences, trimmed)
lon=a*bnd[:,0]+b; lat=c*bnd[:,1]+d
dist,idx=tree.query(np.column_stack([lon*coslat,lat])); tgt=ref_ll[idx]
resid=np.hypot((lon-tgt[:,0])*coslat, lat-tgt[:,1])*111
keep=resid<np.percentile(resid,92)
X=np.column_stack([bnd[keep,0],bnd[keep,1],np.ones(keep.sum())])
clon=np.linalg.lstsq(X,tgt[keep,0],rcond=None)[0]; clat=np.linalg.lstsq(X,tgt[keep,1],rcond=None)[0]
print(" full affine lon:",clon," lat:",clat)
evaluate(lambda x,y:(clon[0]*x+clon[1]*y+clon[2], clat[0]*x+clat[1]*y+clat[2]),'ICP full-affine (comparison)')

# Towns validation: town squares vs towns ref
towns=gpd.read_file('shapefiles/nigeria_online_layers/towns/towns.shp')
ttree=cKDTree(np.column_stack([towns.geometry.x.values*coslat, towns.geometry.y.values]))
tc=np.load('work/min/town_centers_page.npy')
for label,fn in [('VP',lambda x,y:vp(x,y)),('PREV',prev),('ICP-new',icp)]:
    lo=np.empty(len(tc)); la=np.empty(len(tc)); lo[:],la[:]=fn(tc[:,0],tc[:,1])
    dd,_=ttree.query(np.column_stack([lo*coslat,la])); dd=dd*111
    print(f"TOWNS {label:8s} median nearest-ref-town={np.median(dd):.2f}km frac<3km={(dd<3).mean():.2f} frac<5km={(dd<5).mean():.2f} frac<10km={(dd<10).mean():.2f}")

out={'model':'lon=a*page_x+b; lat=c*page_y+d (page pts, PyMuPDF top-down origin, page 3960x2160)',
     'a':float(a),'b':float(b),'c':float(c),'d':float(d),
     'pt_per_deg':[float(1/a),float(-1/c)],
     'init':'embedded /VP GPTS','method':'robust ICP of International_Boundary vector layer to Natural Earth admin0 boundary (densified 400 m), axis-aligned affine, trimmed+Huber weights',
     'frame_page':[74.23969,358.72388,2051.1915,1967.70117],
     'graticule_note':'printed graticule lines/labels are shifted +0.165 deg lon vs map content; NOT used. Graticule scale 157.60 pt/deg agrees with fitted scale.'}
json.dump(out, open('work/min/mineral_transform.json','w'), indent=1)
print("\nsaved work/min/mineral_transform.json")
# delta vs VP & PREV across frame
for (x,y) in [(74.24,358.72),(2051.19,358.72),(74.24,1967.7),(2051.19,1967.7),(1063,1163)]:
    n=icp(x,y); v=vp(x,y); p=prev(x,y)
    print(f" ({x:.0f},{y:.0f}) new=({n[0]:.4f},{n[1]:.4f}) minusVP=({(n[0]-v[0])*111:+.2f},{(n[1]-v[1])*111:+.2f})km minusPREV=({(n[0]-p[0])*111:+.2f},{(n[1]-p[1])*111:+.2f})km")
