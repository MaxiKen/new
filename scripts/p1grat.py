import numpy as np, json
from PIL import Image
im = np.asarray(Image.open('/home/user/new/pic geology of nigeria.png').convert('RGB')).astype(float)
g = im.mean(axis=2)
sat = im.max(axis=2) - im.min(axis=2)
H, W = g.shape
mer_guess = {4: (133, 125.5), 8: (345.5, 344), 12: (558.5, 563)}  # top, bottom expected x
par_guess = {10: 252.5, 6: 471.0}
def centroid_line(vals, idx, halfw):
    lo, hi = idx - halfw, idx + halfw + 1
    seg = vals[lo:hi]
    base = np.median(seg)
    d = base - seg
    d = np.clip(d, 0, None)
    if d.max() < 12:
        return None, 0
    c = np.average(np.arange(lo, hi), weights=d)
    return c, d.max()
# Meridians: scan rows, expected x linearly interpolated between top and bottom guesses
res_mer = {}
for lon, (xt, xb) in mer_guess.items():
    pts = []
    for y in range(40, 572, 3):
        xe = xt + (xb - xt) * (y - 40) / (572 - 40)
        xi = int(round(xe))
        # use row segment; reject rows where colored polygons are present (saturation high)
        row_sat = sat[y, xi - 6: xi + 7]
        if row_sat.max() > 60:
            continue
        c, dep = centroid_line(g[y], xi, 4)
        if c is None:
            continue
        pts.append((c, y, dep))
    res_mer[lon] = pts
    print('meridian', lon, 'n points', len(pts))
# Parallels: scan columns in right part (white background region x 600..700), and left/other where possible
res_par = {}
for lat, yg in par_guess.items():
    pts = []
    for x in range(560, 700, 2):
        yi = int(round(yg))
        col_sat = sat[yi - 6: yi + 7, x]
        if col_sat.max() > 60:
            continue
        c, dep = centroid_line(g[:, x], yi, 4)
        if c is None:
            continue
        pts.append((x, c, dep))
    res_par[lat] = pts
    print('parallel', lat, 'n points', len(pts), 'mean y', np.mean([p[1] for p in pts]) if pts else None)
json.dump({'mer': {k: [(float(a), int(b)) for a, b, _ in v] for k, v in res_mer.items()},
           'par': {k: [(int(a), float(b)) for a, b, _ in v] for k, v in res_par.items()}},
          open('/home/user/work/p1_grat_raw.json', 'w'))
for lon, pts in res_mer.items():
    ys = np.array([p[1] for p in pts]); xs = np.array([p[0] for p in pts])
    A = np.vstack([ys, np.ones_like(ys)]).T
    m, b = np.linalg.lstsq(A, xs, rcond=None)[0]
    r = xs - (m * ys + b)
    print('meridian %d: x = %.3f*y + %.2f ; x at y=40: %.2f, at y=572: %.2f ; resid std %.2f' % (lon, m, b, m*40+b, m*572+b, r.std()))
for lat, pts in res_par.items():
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    A = np.vstack([xs, np.ones_like(xs)]).T
    m, b = np.linalg.lstsq(A, ys, rcond=None)[0]
    r = ys - (m * xs + b)
    print('parallel %d: y = %.5f*x + %.2f ; y at x=560: %.2f, x=700: %.2f ; resid std %.2f' % (lat, m, b, m*560+b, m*700+b, r.std()))
