import numpy as np, json, math, sys
sys.path.insert(0, '/home/user/work')
import georef as G
exec(open('/home/user/work/cooccur.py').read().split("nig = G.load_nigeria()")[0].split("import georef as G")[1]) if False else None
P = json.load(open('/home/user/work/p1_lcc_params.json'))
def lcc_fwd(lon, lat):
    phi0 = math.radians(P['phi0']); s = P['px_per_rad']; x0 = P['x0']; y0 = P['y0']; lam0 = math.radians(P['lam0'])
    n = math.sin(phi0); t0 = math.tan(math.pi/4 + phi0/2); F = math.cos(phi0) * t0**n / n; rho0 = F / t0**n
    lam = np.radians(lon); phi = np.radians(lat)
    rho = F / np.tan(np.pi/4 + phi/2)**n
    th = n * (lam - lam0)
    x = x0 + s * rho * np.sin(th)
    y = y0 - s * (rho0 - rho * np.cos(th))
    return x, y
def lcc_inv(x, y):
    phi0 = math.radians(P['phi0']); s = P['px_per_rad']; x0 = P['x0']; y0 = P['y0']; lam0 = math.radians(P['lam0'])
    n = math.sin(phi0); t0 = math.tan(math.pi/4 + phi0/2); F = math.cos(phi0) * t0**n / n; rho0 = F / t0**n
    dx = (x - x0)/s; dy = (y0 - y)/s
    rho = np.hypot(dx, rho0 - dy); th = np.arctan2(dx, rho0 - dy)
    lam = lam0 + th/n
    phi = 2*np.arctan((F/rho)**(1.0/n)) - np.pi/2
    return np.degrees(lam), np.degrees(phi)
for lon, lat in [(8,10),(4,6),(12,14),(8,6),(4,10),(12,6)]:
    x, y = lcc_fwd(np.array([lon], float), np.array([lat], float))
    print('lon %d lat %d -> pixel x=%.1f y=%.1f' % (lon, lat, x[0], y[0]))
xs = np.array([100., 345., 600.]); ys = np.array([50., 300., 550.])
lo, la = lcc_inv(xs, ys)
x2, y2 = lcc_fwd(lo, la)
print('roundtrip err', np.round(x2 - xs, 4), np.round(y2 - ys, 4))
