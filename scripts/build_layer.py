import numpy as np, json, pickle, sys, math, time
sys.path.insert(0, '/home/user/work')
from PIL import Image
import cv2
from scipy import ndimage as ndi
from skimage import measure
from skimage.color import rgb2lab
import shapely
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
import shapely.ops
import geopandas as gpd
import pyproj
from legend_tables import P2_ROWS, P1_LABELS, load_colors
import georef as G
t0 = time.time()
Image.MAX_IMAGE_PIXELS = None
OUT = '/home/user/work/out/'
P2PATH = '/home/user/new/pic NGSA geological-map-of-nigeria-.jpg'
P1PATH = '/home/user/new/pic geology of nigeria.png'
SIG = 1.6          # smoothing sigma in grid cells (~0.36 km)
DX = 0.002         # grid step in degrees (~0.22 km)
LON0, LAT1 = 2.60, 13.95
NCOL = int(math.ceil((14.75 - LON0) / DX)); NROW = int(math.ceil((LAT1 - 4.20) / DX))
A = np.load('/home/user/work/cluster_assign.npz')
labels = pickle.load(open('/home/user/work/labels.pkl', 'rb'))['labels']
Lk, Rk, n_k, best, bestc, frac_kg = A['Lk'], A['Rk'], A['n_k'], A['best'], A['bestc'], A['frac_kg']
NE = G.load_nigeria()['Nigeria']
NE = shapely.make_valid(NE)
im2 = np.array(Image.open(P2PATH).convert('RGB'))
H2, W2 = im2.shape[:2]
c2m = cv2.medianBlur(im2, 3); del im2
print('P2 loaded', c2m.shape, round(time.time() - t0, 1), flush=True)

# ---- colour -> label lookup on a 4-level RGB grid (nearest accepted cluster within dE 6)
accept = np.where(best >= 0)[0]
cent = Lk[accept]
qs = np.arange(64)
Q = np.stack(np.meshgrid(qs, qs, qs, indexing='ij'), -1).reshape(-1, 3)
Lq = rgb2lab((Q * 4 + 2)[None].astype(float) / 255.0)[0]
lut = np.full(Lq.shape[0], -1, np.int32)
for s in range(0, Lq.shape[0], 4000):
    d = np.sqrt(((Lq[s:s + 4000, None, :] - cent[None, :, :]) ** 2).sum(-1))
    j = d.argmin(1); dm = d[np.arange(d.shape[0]), j]
    lut[s:s + 4000] = np.where(dm < 6.0, best[accept[j]], -1)
lut = lut.reshape(64, 64, 64)

# ---- sample the P2 map on the working grid
lab = np.full((NROW, NCOL), -1, np.int16)
dom = np.zeros((NROW, NCOL), bool)
cc = np.arange(NCOL); LON = LON0 + (cc + 0.5) * DX
for r0 in range(0, NROW, 200):
    r1 = min(NROW, r0 + 200); nb = r1 - r0
    LAT = LAT1 - (np.arange(r0, r1) + 0.5) * DX
    LONb = np.broadcast_to(LON[None, :], (nb, NCOL)); LATb = np.broadcast_to(LAT[:, None], (nb, NCOL))
    ins = shapely.contains_xy(NE, LONb.ravel(), LATb.ravel()).reshape(nb, NCOL)
    x2 = G.P2_A + G.P2_B * LONb; y2 = G.P2_C + G.P2_D * LATb
    ci = np.clip(np.rint(x2).astype(np.int32), 0, W2 - 1); ri = np.clip(np.rint(y2).astype(np.int32), 0, H2 - 1)
    col = c2m[ri, ci].astype(np.int32)
    lb = lut[col[..., 0] // 4, col[..., 1] // 4, col[..., 2] // 4]
    blue = (col[..., 2] > 200) & (col[..., 0] < 190) & ((col[..., 2] - col[..., 0]) > 50)
    lakebox = (LONb > 12.55) & (LONb < 13.6) & (LATb > 12.6)
    lab[r0:r1] = np.where(ins & ~(blue & lakebox), lb, -1)
    dom[r0:r1] = ins
del c2m
print('domain cells', int(dom.sum()), 'unknown inside', round(float((dom & (lab < 0)).sum() / dom.sum()), 4), round(time.time() - t0, 1), flush=True)

# ---- fill unknown cells inside the domain from the nearest known neighbour
for it in range(2000):
    todo = dom & (lab < 0)
    if not todo.any():
        break
    p = np.pad(lab, 1, constant_values=-1)
    neigh = [p[0:-2, 1:-1], p[2:, 1:-1], p[1:-1, 0:-2], p[1:-1, 2:]]
    newlab = np.full(lab.shape, -1, np.int16)
    for nbv in neigh[::-1]:
        newlab = np.where(nbv >= 0, nbv, newlab)
    upd = todo & (newlab >= 0)
    if not upd.any():
        break
    lab[upd] = newlab[upd]
print('fill done after', it, 'iterations; unknown left', int((dom & (lab < 0)).sum()), round(time.time() - t0, 1), flush=True)
lab = np.where(dom, lab, -1).astype(np.int16)
np.save(OUT + 'lab_grid.npy', lab)

# ---- smooth indicator fields -> exact partition via zero contours of (S_k - best competitor)
from shapely.ops import polygonize, unary_union as _uu
Dblur = ndi.gaussian_filter(dom.astype(np.float32), SIG, mode='constant', truncate=4.0)
PAD = int(4 * SIG) + 4
present = [int(k) for k in np.unique(lab) if k >= 0]
A_MIN_RING = 2.0e-5   # closed contour loops enclosing less than ~0.25 km2 are noise

print('labels present on grid', len(present), flush=True)
def window_of(k):
    m = lab == k
    rr = np.where(m.any(1))[0]; cc_ = np.where(m.any(0))[0]
    return (max(0, rr[0] - PAD), min(NROW, rr[-1] + 1 + PAD), max(0, cc_[0] - PAD), min(NCOL, cc_[-1] + 1 + PAD))
def smooth_S(k, W):
    r0, r1, c0, c1 = W
    I = (lab[r0:r1, c0:c1] == k).astype(np.float32)
    B = ndi.gaussian_filter(I, SIG, mode='constant', truncate=4.0)
    Dw = Dblur[r0:r1, c0:c1]
    return np.where(Dw > 1e-3, B / np.maximum(Dw, 1e-6), 0).astype(np.float32)
max1 = np.full((NROW, NCOL), -1, np.float32); max2 = np.full((NROW, NCOL), -1, np.float32)
lab1 = np.full((NROW, NCOL), -1, np.int16)
WIN = {}
for k in present:
    W = window_of(k); WIN[k] = W
    S = smooth_S(k, W)
    r0, r1, c0, c1 = W
    m1 = max1[r0:r1, c0:c1]; m2 = max2[r0:r1, c0:c1]; l1 = lab1[r0:r1, c0:c1]
    top = S > m1
    max2[r0:r1, c0:c1] = np.where(top, m1, np.maximum(m2, S))
    max1[r0:r1, c0:c1] = np.where(top, S, m1)
    lab1[r0:r1, c0:c1] = np.where(top, k, l1)
print('pass1 done', round(time.time() - t0, 1), flush=True)
lines = []
for k in present:
    W = WIN[k]; r0, r1, c0, c1 = W
    S = smooth_S(k, W)
    comp = np.where(lab1[r0:r1, c0:c1] == k, max2[r0:r1, c0:c1], max1[r0:r1, c0:c1])
    F = S - comp
    F = np.where(lab1[r0:r1, c0:c1] < 0, -1.0, F).astype(np.float32)
    F = np.pad(F, 1, constant_values=-1.0)
    for cnt in measure.find_contours(F, 0.0):
        if len(cnt) < 3:
            continue
        gr = r0 + cnt[:, 0] - 1; gc = c0 + cnt[:, 1] - 1
        xy = np.column_stack([LON0 + (gc + 0.5) * DX, LAT1 - (gr + 0.5) * DX])
        if shapely.Polygon(xy).area >= A_MIN_RING:
            lines.append(shapely.LineString(xy))
del max2
print('contour lines', len(lines), round(time.time() - t0, 1), flush=True)
lines.extend(list(NE.boundary.geoms) if hasattr(NE.boundary, 'geoms') else [NE.boundary])
noded = shapely.union_all(lines)
print('noded lines', len(noded.geoms) if hasattr(noded, 'geoms') else 1, round(time.time() - t0, 1), flush=True)
faces = list(polygonize(noded.geoms if hasattr(noded, 'geoms') else [noded]))
print('faces', len(faces), round(time.time() - t0, 1), flush=True)
# assign each face to the argmax label at its interior point, keep faces inside Nigeria
MIN_PART = 1.0e-4    # deg^2 (about 1.2 km^2)
keep_geom, keep_lab = [], []
for f in faces:
    if f.area <= 0:
        continue
    rp = shapely.point_on_surface(f)
    if not NE.contains(rp):
        continue
    c = int((rp.x - LON0) / DX); r = int((LAT1 - rp.y) / DX)
    c = min(max(c, 0), NCOL - 1); r = min(max(r, 0), NROW - 1)
    lb = int(lab1[r, c])
    if lb < 0:
        continue
    keep_geom.append(f); keep_lab.append(lb)
print('inside faces', len(keep_geom), 'area sum/NE', round(sum(g.area for g in keep_geom) / NE.area, 5), flush=True)
# merge specks into the neighbour with the longest shared boundary
tree = shapely.STRtree(keep_geom)
for i in np.argsort([g.area for g in keep_geom]):
    if keep_geom[i].area >= MIN_PART:
        continue
    cand = [j for j in tree.query(keep_geom[i], predicate='intersects') if j != i and keep_lab[j] != keep_lab[i]]
    if not cand:
        continue
    j = max(cand, key=lambda j: keep_geom[i].boundary.intersection(keep_geom[j].boundary).length)
    keep_lab[i] = keep_lab[j]
# coverage-preserving simplification of the partition, then dissolve per label
if hasattr(shapely, 'coverage_simplify'):
    simp = shapely.coverage_simplify(keep_geom, 0.0003, simplify_boundary=True)
    keep_geom = [g if g is not None else keep_geom[i] for i, g in enumerate(simp)]
polys = {}
for g, lb in zip(keep_geom, keep_lab):
    polys.setdefault(lb, []).append(g)
polys = {k: shapely.make_valid(_uu(v)) for k, v in polys.items()}
tot = sum(v.area for v in polys.values()); uni = _uu(list(polys.values())).area
print('partition: sum area/NE %.6f ; union/NE %.6f ; overlap/NE %.6f' % (tot / NE.area, uni / NE.area, (tot - uni) / NE.area), flush=True)
print('total time so far', round(time.time() - t0, 1), flush=True)
pickle.dump({'polys': polys}, open(OUT + 'polys.pkl', 'wb'))

print('build stage complete; attributes are written by write_gpkg.py', flush=True)
