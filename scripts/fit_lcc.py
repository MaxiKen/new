import numpy as np, json
from scipy.optimize import least_squares
pts = json.load(open('/home/user/work/p1_grat_pts.json'))
MER = []   # (x, y, lon)
PAR = []   # (x, y, lat)
for k, v in pts['mer'].items():
    for c, y in v:
        MER.append((c, y, float(k)))
for k, v in pts['par'].items():
    if int(k) in (8, 12):
        continue
    for x, c in v:
        PAR.append((x, c, float(k)))
MER = np.array(MER); PAR = np.array(PAR)
D = np.deg2rad
LAM0 = D(8.0)

def lcc_inverse(x, y, p):
    phi0, s, x0, y0, lam0 = p
    n = np.sin(phi0)
    # F and rho0 for spherical LCC with unit radius; s = pixels per radian
    t0 = np.tan(np.pi / 4 + phi0 / 2)
    F = np.cos(phi0) * t0 ** n / n
    rho0 = F / t0 ** n
    dx = (x - x0) / s
    dy = (y0 - y) / s          # y up
    rho = np.sign(n) * np.hypot(dx, rho0 - dy)
    theta = np.arctan2(dx, rho0 - dy) if n > 0 else np.arctan2(dx, -(rho0 - dy))
    lam = lam0 + theta / n
    tt = (F / rho) ** (1.0 / n)
    phi = 2 * np.arctan(tt) - np.pi / 2
    return np.rad2deg(lam), np.rad2deg(phi)

def resid(p):
    lon_m, lat_m = lcc_inverse(MER[:, 0], MER[:, 1], p)
    lon_p, lat_p = lcc_inverse(PAR[:, 0], PAR[:, 1], p)
    # convert degree residuals to approximate pixel units
    s_deg = p[1] * np.pi / 180.0          # px per degree of arc
    r1 = (lon_m - MER[:, 2]) * s_deg * np.cos(np.deg2rad(lat_m))
    r2 = (lat_p - PAR[:, 2]) * s_deg
    return np.concatenate([r1, r2])

p0 = np.array([D(9.0), 3116.0, 345.5, 313.0, D(8.0)])
sol = least_squares(resid, p0, x_scale=[0.01, 100, 10, 10, 0.01], loss='soft_l1', f_scale=0.5)
p = sol.x
r = resid(sol.x)
print('phi0 deg %.4f ; px per deg %.4f ; x0 %.3f ; y0 %.3f ; lam0 %.4f' % (np.rad2deg(p[0]), p[1]*np.pi/180, p[2], p[3], np.rad2deg(p[4])))
print('residual px: median abs %.3f, 90pct %.3f, max %.3f (n=%d)' % (np.median(np.abs(r)), np.percentile(np.abs(r), 90), np.abs(r).max(), r.size))
lon_m, lat_m = lcc_inverse(MER[:, 0], MER[:, 1], p)
lon_p, lat_p = lcc_inverse(PAR[:, 0], PAR[:, 1], p)
print('meridian-lon errors deg: median %.5f max %.5f' % (np.median(np.abs(lon_m - MER[:, 2])), np.abs(lon_m - MER[:, 2]).max()))
print('parallel-lat errors deg: median %.5f max %.5f' % (np.median(np.abs(lat_p - PAR[:, 2])), np.abs(lat_p - PAR[:, 2]).max()))
# per-line summary
for lon in [4, 8, 12]:
    sel = MER[:, 2] == lon
    print('meridian', lon, 'median lon err %.5f  (n=%d)' % (np.median(lon_m[sel] - lon), sel.sum()))
for lat in [14, 10, 6]:
    sel = PAR[:, 2] == lat
    print('parallel', lat, 'median lat err %.5f  (n=%d)' % (np.median(lat_p[sel] - lat), sel.sum()))
json.dump({'phi0': float(np.rad2deg(p[0])), 'px_per_rad': float(p[1]), 'x0': float(p[2]), 'y0': float(p[3]), 'lam0': float(np.rad2deg(p[4]))}, open('/home/user/work/p1_lcc_params.json', 'w'), indent=1)
