import numpy as np, json
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

# ---------- Picture 2 (NGSA, plate carree graticule) ----------
P2_MER_X = {3: 408.16, 4: 736.54, 5: 1065.17, 6: 1393.55, 7: 1722.17, 8: 2050.05,
            9: 2378.37, 10: 2706.83, 11: 3035.43, 12: 3363.83, 13: 3691.64, 14: 4020.23}
P2_PAR_Y = {13: 484.75, 12: 812.50, 11: 1141.00, 10: 1469.50}

def fit_p2():
    lons = np.array(list(P2_MER_X.keys()), float); xs = np.array(list(P2_MER_X.values()))
    b, a = np.polyfit(lons, xs, 1)            # x = a + b*lon  (b px/deg)
    lats = np.array(list(P2_PAR_Y.keys()), float); ys = np.array(list(P2_PAR_Y.values()))
    d, c = np.polyfit(lats, ys, 1)            # y = c + d*lat  (d px/deg, negative)
    return a, b, c, d

P2_A, P2_B, P2_C, P2_D = fit_p2()

def p2_to_lonlat(x, y):
    lon = (np.asarray(x, float) - P2_A) / P2_B
    lat = (np.asarray(y, float) - P2_C) / P2_D
    return lon, lat

def lonlat_to_p2(lon, lat):
    x = P2_A + P2_B * np.asarray(lon, float)
    y = P2_C + P2_D * np.asarray(lat, float)
    return x, y

# ---------- Picture 1 (conic graticule; 2nd-order polynomial fit to gridline points) ----------
def _poly2_design(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return np.vstack([np.ones_like(x), x, y, x * x, x * y, y * y]).T

def fit_p1():
    pts = json.load(open('/home/user/work/p1_grat_pts.json'))
    # lon model from meridian points (value = lon)
    X, Y, L = [], [], []
    for k, v in pts['mer'].items():
        for xm, ym in v:
            X.append(xm); Y.append(ym); L.append(float(k))
    X, Y, L = map(np.array, (X, Y, L))
    A = _poly2_design(X, Y)
    cl = np.linalg.lstsq(A, L, rcond=None)[0]
    # lat model from parallel points
    X2, Y2, P = [], [], []
    for k, v in pts['par'].items():
        if int(k) in (8, 12):   # noisier lines, down-weighted by exclusion
            continue
        for xp, yp in v:
            X2.append(xp); Y2.append(yp); P.append(float(k))
    X2, Y2, P = map(np.array, (X2, Y2, P))
    A2 = _poly2_design(X2, Y2)
    cp = np.linalg.lstsq(A2, P, rcond=None)[0]
    return cl, cp

P1_CL, P1_CP = fit_p1()

def p1_to_lonlat(x, y):
    A = _poly2_design(np.asarray(x, float), np.asarray(y, float))
    return A @ P1_CL, A @ P1_CP

def lonlat_to_p1_residual_check():
    # residuals of fit on the gridline points
    pts = json.load(open('/home/user/work/p1_grat_pts.json'))
    out = {}
    for k, v in pts['mer'].items():
        arr = np.array(v)
        lon, lat = p1_to_lonlat(arr[:, 0], arr[:, 1])
        out['mer%s' % k] = (float(np.abs(lon - float(k)).mean() * 111.32 * 0.99 * 1000), float(np.abs(lon - float(k)).max()))
    for k, v in pts['par'].items():
        arr = np.array(v)
        lon, lat = p1_to_lonlat(arr[:, 0], arr[:, 1])
        out['par%s' % k] = (float(np.abs(lat - float(k)).mean() * 111.0 * 1000), float(np.abs(lat - float(k)).max()))
    return out

def load_nigeria():
    d = json.load(open('/home/user/work/npm/countries_sel.geojson'))
    geoms = {f['properties']['name']: shape(f['geometry']) for f in d['features']}
    return geoms

if __name__ == '__main__':
    print('P2 fit: x = %.3f + %.4f*lon ; y = %.3f + %.4f*lat' % (P2_A, P2_B, P2_C, P2_D))
    print('P1 lon coef', np.round(P1_CL, 6))
    print('P1 lat coef', np.round(P1_CP, 6))
    print('P1 check (mean km, max deg) per gridline:')
    for k, v in lonlat_to_p1_residual_check().items():
        print('  ', k, np.round(v, 4))
    # P1 corners of picture frame
    for (x, y) in [(34.5, 33.5), (705, 33.5), (34.5, 579.5), (705, 579.5), (370, 306)]:
        lon, lat = p1_to_lonlat([x], [y])
        print('P1 pixel', (x, y), '-> lon %.4f lat %.4f' % (lon[0], lat[0]))
    g = load_nigeria()
    nig = g['Nigeria']
    print('Nigeria bounds (NE 10m):', np.round(nig.bounds, 4), 'area km2 approx', round(nig.area * 111.32**2 * 0.97, 0))
