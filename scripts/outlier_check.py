import numpy as np, json, sys
sys.path.insert(0, '/home/user/work')
from shapely.geometry import Point
import georef as G
nig = G.load_nigeria()['Nigeria']
o = json.load(open('/home/user/work/outlines.json'))
def report(name, lon, lat, top=8):
    d = np.array([nig.boundary.distance(Point(a, b)) * 111.2 for a, b in zip(lon, lat)])
    idx = np.argsort(-d)[:top]
    print(name, 'top deviations (lon, lat, km):')
    for i in idx:
        print('   %.3f %.3f %.1f' % (lon[i], lat[i], d[i]))
    # cluster summary
    big = d > 20
    print('   points >20 km: %d of %d' % (big.sum(), d.size))
    if big.sum():
        print('   bbox of >20km points: lon %.2f-%.2f lat %.2f-%.2f' % (lon[big].min(), lon[big].max(), lat[big].min(), lat[big].max()))
report('P2', np.array(o['p2_outline'][0]), np.array(o['p2_outline'][1]))
report('P1', np.array(o['p1_outline'][0]), np.array(o['p1_outline'][1]))
