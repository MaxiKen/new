import numpy as np, pickle, sys
sys.path.insert(0, '/home/user/work')
import pyproj, shapely
import geopandas as gpd
from skimage.color import rgb2lab
from legend_tables import P2_ROWS, P1_LABELS, load_colors
p2c, p1c = load_colors()
OUT = '/home/user/work/out/'
A = np.load('/home/user/work/cluster_assign.npz')
labels = pickle.load(open('/home/user/work/labels.pkl', 'rb'))['labels']
Lk, Rk, n_k, best, frac_kg, nvalid = A['Lk'], A['Rk'], A['n_k'], A['best'], A['frac_kg'], A['nvalid']
polys = pickle.load(open(OUT + 'polys.pkl', 'rb'))['polys']
import shapely as _sh
_keys = sorted(polys)
_simp = _sh.coverage_simplify([polys[k] for k in _keys], 0.001, simplify_boundary=True)
polys = {k: (_g if _g is not None and not _g.is_empty else polys[k]) for k, _g in zip(_keys, _simp)}
L2all = rgb2lab(np.array(p2c, float)[None] / 255.0)[0]
geod = pyproj.Geod(ellps='WGS84')
from pyproj import Transformer
_tr = Transformer.from_crs('EPSG:4326', 'EPSG:6933', always_xy=True)  # equal-area
def cluster_class(c, li):
    L = labels[li]
    dE2 = min(float(np.sqrt(((Lk[c] - L2all[r - 1]) ** 2).sum())) for r in L['rows'])
    f = None
    if L['groups'] is not None and nvalid[c] >= 30:
        f = float(sum(frac_kg[c, g] for g in L['groups']))
    colour_ok = dE2 <= 4.0                       # exact or near-exact legend colour
    colour_near = dE2 <= 12.0                    # map colour shifted but same colour family
    p1_ok = (f is not None) and f >= 0.5         # picture 1 colour group agrees
    p1_strong = (f is not None) and f >= 0.8
    if colour_ok and p1_ok:
        cls = 'high'
    elif colour_ok or (colour_near and p1_ok) or p1_strong:
        cls = 'medium'
    else:
        cls = 'low'
    return cls, dE2, f
recs = []
for k in sorted(polys):
    L = labels[k]
    idx = np.where(best == k)[0]
    info = [cluster_class(c, k) for c in idx]
    area_by = {'high': 0.0, 'medium': 0.0, 'low': 0.0}
    for c, (cls, dE2, f) in zip(idx, info):
        area_by[cls] += float(n_k[c])
    conf = max(area_by, key=lambda s: area_by[s]) if idx.size else 'low'
    dEs = [d for (_, d, _) in info]
    fs = [(f, n_k[c]) for c, (_, _, f) in zip(idx, info) if f is not None]
    sup = float(sum(f * n for f, n in fs) / sum(n for _, n in fs)) if fs else None
    hexc = None
    if idx.size:
        top = idx[np.argmax(n_k[idx])]
        hexc = '#%02x%02x%02x' % tuple(int(round(v)) for v in Rk[top])
    area = float(shapely.transform(polys[k], lambda c: np.column_stack(_tr.transform(c[:, 0], c[:, 1]))).area) / 1e6
    recs.append({
        'name': L['name'],
        'codes': '; '.join(sorted(set(P2_ROWS[r - 1][1] for r in L['rows']))),
        'legend_rows': ', '.join(str(r) for r in L['rows']),
        'p1_equivalent': '; '.join(P1_LABELS[j] for j in sorted(L['p1'])) if L['p1'] else None,
        'colour_hex': hexc,
        'colour_dE_median': round(float(np.median(dEs)), 1) if dEs else None,
        'p1_support': None if sup is None else round(sup, 3),
        'confidence': conf,
        'area_km2': round(area, 2),
        'n_colour_clusters': int(idx.size),
        'geometry': polys[k],
    })
gdf = gpd.GeoDataFrame(recs, geometry='geometry', crs='EPSG:4326')
gdf.to_file(OUT + 'nigeria_geology.gpkg', layer='nigeria_geology', driver='GPKG')
gdf.drop(columns='geometry').to_csv(OUT + 'attributes.csv', index=False)
print('features', len(gdf), 'area km2', round(gdf.area_km2.sum(), 1))
print('confidence', gdf.confidence.value_counts().to_dict())
print('legend labels with no polygon:')
have = set(gdf.name)
for k, L in enumerate(labels):
    if L['name'] not in have:
        print('   ', L['name'], '| rows', L['rows'])
