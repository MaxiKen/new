import numpy as np, json
from PIL import Image
im = np.asarray(Image.open('/home/user/new/pic geology of nigeria.png').convert('RGB')).astype(float)
g = im.mean(axis=2)
sat = im.max(axis=2) - im.min(axis=2)
def local_centroid(profile, idx, halfw=4, minDepth=10):
    lo, hi = idx - halfw, idx + halfw + 1
    seg = profile[lo:hi]
    base = np.median(profile[max(0, idx - 15): idx + 16])
    d = np.clip(base - seg, 0, None)
    if d.max() < minDepth:
        return None
    return float(np.average(np.arange(lo, hi), weights=d))
# expected line positions (from fitted lines)
mer_fit = {4: (-0.014, 133.39), 8: (-0.003, 345.77), 12: (0.008, 558.35)}   # x = m*y + b
par_fit = {10: (-0.01775, 264.48), 6: (-0.00822, 476.43)}                  # y = m*x + b
# extrapolated parallels 4,8,12,14 using spacing ~ 54.5 px/deg with slight slope similar to neighbours
pars = {14: (-0.0118, 38.0 - 0.0118*600*0 ), 12: None, 8: None, 4: None}
# simple linear extrapolation of the intercept in y for each x using parallel spacing
def y_of(lat, x):
    # interpolate between known parallel lines (linear in lat)
    y10 = par_fit[10][0]*x + par_fit[10][1]
    y6 = par_fit[6][0]*x + par_fit[6][1]
    spacing = (y6 - y10) / 4.0
    return y10 + (10 - lat) * spacing
mer_pts = {}
for lon, (m, b) in mer_fit.items():
    pts = []
    for y in range(36, 576, 2):
        xe = m * y + b
        xi = int(round(xe))
        if sat[y, xi-5:xi+6].max() > 90:
            continue
        c = local_centroid(g[y], xi, 4, 10)
        if c is None:
            continue
        pts.append((c, float(y)))
    mer_pts[lon] = pts
par_pts = {}
for lat in [14, 12, 10, 8, 6, 4]:
    pts = []
    for x in range(40, 705, 2):
        ye = y_of(lat, x)
        yi = int(round(ye))
        if yi < 36 or yi > 576:
            continue
        if sat[yi-5:yi+6, x].max() > 90:
            continue
        c = local_centroid(g[:, x], yi, 4, 10)
        if c is None:
            continue
        pts.append((float(x), c))
    par_pts[lat] = pts
    print('parallel', lat, 'points', len(pts))
for lon, pts in mer_pts.items():
    print('meridian', lon, 'points', len(pts))
json.dump({'mer': {str(k): v for k, v in mer_pts.items()}, 'par': {str(k): v for k, v in par_pts.items()}}, open('/home/user/work/p1_grat_pts.json', 'w'))
# Fit line models to report consistency
for lat, pts in par_pts.items():
    if len(pts) < 10:
        continue
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    # robust: iterate removing outliers
    keep = np.ones_like(xs, bool)
    for _ in range(3):
        A = np.vstack([xs[keep], xs[keep]**2, np.ones(keep.sum())]).T
        coef = np.linalg.lstsq(A, ys[keep], rcond=None)[0]
        r = ys - (coef[0]*xs + coef[1]*xs**2 + coef[2])
        keep = np.abs(r) < max(0.6, 3*np.std(r[keep]))
    print('parallel %d quadratic fit: y(560)=%.2f y(640)=%.2f y(700)=%.2f resid std %.3f kept %d/%d' % (lat, np.polyval([coef[1],coef[0],coef[2]],560), np.polyval([coef[1],coef[0],coef[2]],640), np.polyval([coef[1],coef[0],coef[2]],700), r[keep].std(), keep.sum(), len(xs)))
for lon, pts in mer_pts.items():
    ys = np.array([p[1] for p in pts]); xs = np.array([p[0] for p in pts])
    keep = np.ones_like(xs, bool)
    for _ in range(3):
        A = np.vstack([ys[keep], np.ones(keep.sum())]).T
        m, b = np.linalg.lstsq(A, xs[keep], rcond=None)[0]
        r = xs - (m*ys + b)
        keep = np.abs(r) < max(0.6, 3*np.std(r[keep]))
    print('meridian %d linear: x(40)=%.2f x(572)=%.2f resid std %.3f kept %d/%d' % (lon, m*40+b, m*572+b, r[keep].std(), keep.sum(), len(xs)))
