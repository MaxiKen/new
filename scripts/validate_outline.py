import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union
from skimage import measure
import shapely
import sys
sys.path.insert(0, '/home/user/work')
import georef as G
Image.MAX_IMAGE_PIXELS = None
nig = G.load_nigeria()['Nigeria']
nig_b = nig.boundary
L = json.load(open('/home/user/work/p1_lcc_params.json'))

def lcc_forward_lonlat(x, y):
    # inverse of fit (pixel -> lon/lat) using fitted params
    phi0 = np.deg2rad(L['phi0']); s = L['px_per_rad']; x0 = L['x0']; y0 = L['y0']; lam0 = np.deg2rad(L['lam0'])
    n = np.sin(phi0); t0 = np.tan(np.pi/4 + phi0/2); F = np.cos(phi0) * t0**n / n; rho0 = F / t0**n
    x = np.asarray(x, float); y = np.asarray(y, float)
    dx = (x - x0) / s; dy = (y0 - y) / s
    rho = np.hypot(dx, rho0 - dy)
    theta = np.arctan2(dx, rho0 - dy)
    lam = lam0 + theta / n
    phi = 2*np.arctan((F / rho)**(1.0/n)) - np.pi/2
    return np.rad2deg(lam), np.rad2deg(phi)

def km_dist(lons, lats):
    pts = [Point(a, b) for a, b in zip(lons, lats)]
    d = np.array([nig_b.distance(p) for p in pts])
    return d * 111.2  # km (approx, degrees ~ 111 km)

def largest_mask_outline(mask, min_area=2000):
    lab, nlab = ndi.label(mask)
    sizes = ndi.sum(mask, lab, range(1, nlab+1))
    k = int(np.argmax(sizes)) + 1
    m = lab == k
    m = ndi.binary_fill_holes(m)
    return m, sizes[k-1]

# ---- Picture 1 outline ----
im1 = np.asarray(Image.open('/home/user/new/pic geology of nigeria.png').convert('RGB')).astype(int)
mn = im1.min(axis=2)
mask1 = mn < 236
mask1[:, :37] = False; mask1[:, 703:] = False; mask1[:36, :] = False; mask1[578:, :] = False
mask1 = ndi.binary_opening(mask1, structure=np.ones((3, 3)))
m1, a1 = largest_mask_outline(mask1)
m1 = ndi.binary_opening(m1, structure=np.ones((5, 5)))
m1, a1 = largest_mask_outline(m1)
cont = measure.find_contours(m1.astype(float), 0.5)
cont = max(cont, key=len)
ys, xs = cont[:, 0], cont[:, 1]
lon1, lat1 = lcc_forward_lonlat(xs, ys)
d1 = km_dist(lon1[::3], lat1[::3])
print('P1 mask px area', int(a1), 'outline pts', len(cont))
print('P1 outline distance to NE Nigeria boundary (km): median %.2f  p90 %.2f  p99 %.2f  max %.2f' % (np.median(d1), np.percentile(d1, 90), np.percentile(d1, 99), d1.max()))
print('P1 outline lon range %.3f-%.3f lat range %.3f-%.3f' % (lon1.min(), lon1.max(), lat1.min(), lat1.max()))
# area comparison
p1poly = Polygon(np.c_[lon1, lat1]).buffer(0)
print('P1 polygon area (deg^2) %.3f vs NE %.3f' % (p1poly.area, nig.area))

# ---- Picture 2 outline ----
im2 = Image.open('/home/user/new/pic NGSA geological-map-of-nigeria-.jpg').convert('RGB')
sm = im2.resize((1650, 919), Image.BILINEAR)
a2 = np.asarray(sm).astype(int)
mn2 = a2.min(axis=2)
sat2 = a2.max(axis=2) - a2.min(axis=2)
mask2 = (mn2 < 225) & ~((a2[..., 2] > a2[..., 0] + 40))   # not white, not blue water
# restrict to map area inside the inner frame (x 47..1100, y 47..880 in 1/4 scale) and exclude legend (x>1080)
mask2[:, 1060:] = False
mask2[:47, :] = False; mask2[880:, :] = False; mask2[:, :46] = False
mask2 = ndi.binary_opening(mask2, structure=np.ones((3, 3)))
m2, a2s = largest_mask_outline(mask2)
m2 = ndi.binary_opening(m2, structure=np.ones((5, 5)))
m2, a2s = largest_mask_outline(m2)
cont2 = max(measure.find_contours(m2.astype(float), 0.5), key=len)
ys2, xs2 = cont2[:, 0] * 4.0, cont2[:, 1] * 4.0   # back to full-res pixel coords
lon2, lat2 = G.p2_to_lonlat(xs2, ys2)
d2 = km_dist(lon2[::3], lat2[::3])
print('P2 mask area (1/4 px)', int(a2s))
print('P2 outline distance to NE Nigeria boundary (km): median %.2f  p90 %.2f  p99 %.2f  max %.2f' % (np.median(d2), np.percentile(d2, 90), np.percentile(d2, 99), d2.max()))
print('P2 outline lon range %.3f-%.3f lat range %.3f-%.3f' % (lon2.min(), lon2.max(), lat2.min(), lat2.max()))
p2poly = Polygon(np.c_[lon2, lat2]).buffer(0)
print('P2 polygon area (deg^2) %.3f vs NE %.3f' % (p2poly.area, nig.area))
np.save('/home/user/work/mask1.npy', m1); np.save('/home/user/work/mask2_q.npy', m2)
json.dump({'p1_outline': [list(map(float, lon1[::4])), list(map(float, lat1[::4]))],
           'p2_outline': [list(map(float, lon2[::12])), list(map(float, lat2[::12]))]}, open('/home/user/work/outlines.json', 'w'))
