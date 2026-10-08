import numpy as np, pickle, sys, json, math
sys.path.insert(0, '/home/user/work')
from PIL import Image
import cv2, shapely
from shapely.strtree import STRtree
from skimage.color import rgb2lab
import georef as G
from legend_tables import P2_ROWS, P1_LABELS, load_colors
Image.MAX_IMAGE_PIXELS = None
OUT = '/home/user/work/out/'
rng = np.random.default_rng(3)
p2c, p1c = load_colors()
labels = pickle.load(open('/home/user/work/labels.pkl', 'rb'))['labels']
gdf = __import__('geopandas').read_file(OUT + 'nigeria_geology.gpkg', layer='nigeria_geology')
name_to_L = {L['name']: L for L in labels}
polys = list(gdf.geometry); tree = STRtree(polys)
# random points inside Nigeria
NE = shapely.make_valid(G.load_nigeria()['Nigeria'])
minx, miny, maxx, maxy = NE.bounds
pts = []
while len(pts) < 150000:
    x = rng.uniform(minx, maxx, 300000); y = rng.uniform(miny, maxy, 300000)
    ok = shapely.contains_xy(NE, x, y)
    pts.extend(zip(x[ok], y[ok]))
pts = np.array(pts[:150000]); lon, lat = pts[:, 0], pts[:, 1]
ii, jj = tree.query(shapely.points(lon, lat), predicate='within')
lab_idx = -np.ones(len(lon), int); lab_idx[ii] = jj
keep = lab_idx >= 0
lon, lat, lab_idx = lon[keep], lat[keep], lab_idx[keep]
print('points labelled', len(lon))
# P2 colour at points
im2 = np.array(Image.open('/home/user/new/pic NGSA geological-map-of-nigeria-.jpg').convert('RGB'))
c2m = cv2.medianBlur(im2, 3); del im2
xp = np.clip(np.rint(G.P2_A + G.P2_B * lon).astype(int), 0, c2m.shape[1] - 1)
yp = np.clip(np.rint(G.P2_C + G.P2_D * lat).astype(int), 0, c2m.shape[0] - 1)
C2 = c2m[yp, xp].astype(float)
# P1 colour at points via LCC forward projection
P = json.load(open('/home/user/work/p1_lcc_params.json'))
phi0 = math.radians(P['phi0']); s = P['px_per_rad']; x0 = P['x0']; y0 = P['y0']; lam0 = math.radians(P['lam0'])
n = math.sin(phi0); t0 = math.tan(math.pi / 4 + phi0 / 2); F = math.cos(phi0) * t0 ** n / n; rho0 = F / t0 ** n
lam = np.radians(lon); ph = np.radians(lat)
t = np.tan(math.pi / 4 + ph / 2); rho = F / t ** n; th = n * (lam - lam0)
X1 = x0 + s * rho * np.sin(th); Y1 = y0 - s * (rho0 - rho * np.cos(th))
im1 = np.array(Image.open('/home/user/new/pic geology of nigeria.png').convert('RGB'))
m1 = cv2.medianBlur(im1, 3)
xi = np.rint(X1).astype(int); yi = np.rint(Y1).astype(int)
inb = (xi >= 0) & (xi < m1.shape[1]) & (yi >= 0) & (yi < m1.shape[0]) & (xi > 36) & (xi < 703) & (yi > 35) & (yi < 578)
C1 = m1[np.clip(yi, 0, m1.shape[0] - 1), np.clip(xi, 0, m1.shape[1] - 1)].astype(float)
# group of each P1 colour = nearest P1 swatch's group
A = np.load('/home/user/work/cluster_assign.npz'); gid1 = A['gid1']
L1s = rgb2lab(np.array(p1c, float)[None] / 255.0)[0]
L2s = rgb2lab(np.array(p2c, float)[None] / 255.0)[0]
Lc1 = rgb2lab(C1[None] / 255.0)[0]
d1 = np.sqrt(((Lc1[:, None, :] - L1s[None]) ** 2).sum(-1)); j1 = d1.argmin(1); dm1 = d1.min(1)
g1 = np.where(dm1 < 6, gid1[j1], -1)
Lc2 = rgb2lab(C2[None] / 255.0)[0]
d2 = np.sqrt(((Lc2[:, None, :] - L2s[None]) ** 2).sum(-1))
# agreement metrics per point
agree2 = np.zeros(len(lon), bool); agree1 = np.zeros(len(lon), bool); has1 = np.zeros(len(lon), bool)
conf = gdf.confidence.values
for q in range(len(lon)):
    L = name_to_L[gdf.name.values[lab_idx[q]]]
    rows = L['rows']
    agree2[q] = min(d2[q, r - 1] for r in rows) <= 4.0
    if L['groups'] is not None and inb[q] and g1[q] >= 0:
        has1[q] = True
        agree1[q] = g1[q] in L['groups']
print('share of sampled P2 colours within dE<=4 of the assigned label swatch: %.3f' % agree2.mean())
print('share of sampled P1 colours whose P1 colour-group is consistent with label: %.3f (on %d points with P1 evidence)' % (agree1[has1].mean(), has1.sum()))
for cname in ['high', 'medium', 'low']:
    sel = conf[lab_idx] == cname
    print('  confidence %-6s n=%6d  P2-agree %.3f  P1-agree %.3f' % (cname, sel.sum(), agree2[sel].mean() if sel.sum() else float('nan'), agree1[sel & has1].mean() if (sel & has1).sum() else float('nan')))
print('qa done')
