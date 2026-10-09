"""
Digitise the Nigeria geology map ("pic geology of nigeria.png") into a GeoPackage
polygon layer whose `name` attribute carries the legend label(s).

Pipeline
  1. Read the map frame (inside the black border) and the graticule.
  2. Classify every frame pixel to the nearest legend swatch colour.
     The legend's 86 labels use only 12 distinct swatch colours, so the
     map can only separate 12 colour groups; each group keeps the list of
     legend labels that share its colour.
  3. Fill "empty" pixels (white background, graticule lines, text, north arrow,
     scale bar) from their nearest classified neighbour, so the map has no gaps.
  4. Smooth each colour group with a Gaussian and extract sub-pixel iso-contours,
     so boundaries are curved rather than pixel-stepped.
  5. Make the polygons exactly tile the frame (no gaps, no overlaps), simplify,
     and georeference them to WGS84 lon/lat with the printed graticule.
  6. Write the GeoPackage: layer `geology_polygons` (12 features) and
     `legend_lookup` (all 86 legend entries and the polygon each belongs to).

Usage:  python build_geology_gpkg.py <input.png> <output.gpkg>
"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
import shapely
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely.validation import make_valid
import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legend_table import LEGEND

SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/user/new/pic geology of nigeria.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/home/user/new/nigeria_geology_polygons.gpkg'

SIGMA = 2.0          # Gaussian smoothing (native pixels) controlling boundary roundness
MATCH_T = 22.0       # max RGB distance to accept a swatch colour (else "empty")
MIN_SPECK = 15       # connected components smaller than this (px) are re-filled
PAD = 8              # zero padding so polygons close at the frame edge
SIMPLIFY = 0.25      # vertex tolerance in native pixels

# ---- 1. frame and graticule ------------------------------------------------
# Frame interior in pixel-index coordinates (black border at x=34/35, 705; y=33, 580).
X0, X1 = 36, 704     # inclusive interior columns
Y0, Y1 = 34, 579     # inclusive interior rows
# Graticule centre-lines measured from the image (pixel-index coordinates):
#   longitude: x=126 -> 4E, x=345 -> 8E, x=560 -> 12E
#   latitude : y=33.2 -> 14N (frame top), y=252.6 -> 10N, y=471.5 -> 6N, y=580 -> 4N (frame bottom)
LON_PTS = np.array([(126.0, 4.0), (345.0, 8.0), (560.0, 12.0)])
LAT_PTS = np.array([(33.2, 14.0), (252.6, 10.0), (471.5, 6.0), (580.0, 4.0)])
a_lon, b_lon = np.polyfit(LON_PTS[:, 0], LON_PTS[:, 1], 1)  # lon = a*x + b
a_lat, b_lat = np.polyfit(LAT_PTS[:, 0], LAT_PTS[:, 1], 1)  # lat = a*y + b

im = np.asarray(Image.open(SRC).convert('RGB')).astype(float)
crop = im[Y0:Y1 + 1, X0:X1 + 1]
H, W = crop.shape[:2]

# ---- 2. colour groups -------------------------------------------------------
swatch = np.array([c for _, _, c in LEGEND], float)
groups = []
for i, c in enumerate(swatch):
    for g in groups:
        if np.linalg.norm(swatch[g[0]] - c) < 8:
            g.append(i)
            break
    else:
        groups.append([i])
K = len(groups)
centres = np.array([swatch[g].mean(axis=0) for g in groups])
group_names = ['; '.join(LEGEND[i][1] for i in g) for g in groups]
group_legend_n = [len(g) for g in groups]
group_hex = ['#%02x%02x%02x' % tuple(int(round(v)) for v in centres[k]) for k in range(K)]

d = np.sqrt(((crop.reshape(-1, 3)[:, None, :] - centres[None]) ** 2).sum(-1))
lab = d.argmin(1).reshape(H, W)
lab[d.min(1).reshape(H, W) > MATCH_T] = -1

# ---- 3. remove specks and fill empty pixels --------------------------------
for k in range(K):
    cc, n = ndi.label(lab == k)
    if n:
        sizes = ndi.sum(np.ones_like(cc), cc, index=np.arange(1, n + 1))
        small = np.isin(cc, 1 + np.where(sizes < MIN_SPECK)[0])
        lab[small] = -1
idx = ndi.distance_transform_edt(lab < 0, return_distances=False, return_indices=True)
lab = lab[idx[0], idx[1]]
assert (lab >= 0).all()

# ---- 4. smooth + iso-contours ----------------------------------------------
P = np.zeros((K, H + 2 * PAD, W + 2 * PAD), np.float32)
for k in range(K):
    P[k, PAD:-PAD, PAD:-PAD] = (lab == k)
    P[k] = ndi.gaussian_filter(P[k], SIGMA, mode='constant', cval=0.0)

def rings_to_polygons(rings):
    """Even-odd nesting of contour rings -> shapely polygons with holes."""
    polys = []
    for r in rings:
        if len(r) < 4:
            continue
        # contour (row,col) in padded field -> interior pixel index (x,y)
        xy = np.column_stack([r[:, 1] - PAD + X0, r[:, 0] - PAD + Y0])
        p = Polygon(xy)
        if not p.is_valid:
            p = make_valid(p)
        if p.area > 0:
            polys.append(p)
    if not polys:
        return None
    depth = []
    for i, p in enumerate(polys):
        depth.append(sum(1 for j, q in enumerate(polys) if j != i and q.buffer(0).contains(p.representative_point())))
    shells = [i for i in range(len(polys)) if depth[i] % 2 == 0]
    holes = [i for i in range(len(polys)) if depth[i] % 2 == 1]
    shell_geoms = [polys[i] for i in shells]
    hole_map = {j: [] for j in range(len(shells))}
    for h in holes:
        cands = [(polys[s].area, j) for j, s in enumerate(shells) if polys[s].buffer(0).contains(polys[h].representative_point())]
        if cands:
            hole_map[min(cands)[1]].append(polys[h].exterior)
    out = []
    for j, s in enumerate(shell_geoms):
        out.append(Polygon(s.exterior, holes=hole_map[j]).buffer(0))
    return unary_union(out)

frame = box(X0 - 0.5, Y0 - 0.5, X1 + 0.5, Y1 + 0.5)
class_polys = []
for k in range(K):
    rings = measure.find_contours(P[k], 0.5)
    g = rings_to_polygons(rings)
    if g is None:
        class_polys.append(Polygon())
        continue
    g = g.intersection(frame).simplify(SIMPLIFY, preserve_topology=True)
    g = make_valid(g).buffer(0)
    class_polys.append(g)

# ---- 5. make a clean tiling of the frame -----------------------------------
# 5a. remove overlaps: earlier classes (larger area first) keep their area
order = sorted(range(K), key=lambda k: -class_polys[k].area)
assigned = Polygon()
for k in order:
    p = class_polys[k].difference(assigned)
    class_polys[k] = p
    assigned = unary_union([assigned, p])
# 5b. gaps: give each gap piece to the neighbouring class it shares the longest border with
gaps = frame.difference(unary_union(class_polys))
if not gaps.is_empty:
    pieces = list(gaps.geoms) if hasattr(gaps, 'geoms') else [gaps]
    for piece in pieces:
        if piece.area <= 0:
            continue
        best, bl = None, -1
        for k in range(K):
            if class_polys[k].is_empty:
                continue
            L = piece.buffer(0.6).intersection(class_polys[k].boundary).length
            if L > bl:
                best, bl = k, L
        if best is not None:
            class_polys[best] = unary_union([class_polys[best], piece]).buffer(0)
# final coverage check
cover = unary_union(class_polys)
print(f'frame area {frame.area:.1f}  covered {cover.area:.1f}  sum of parts {sum(p.area for p in class_polys):.1f}')

# ---- 6. georeference and write --------------------------------------------
def to_lonlat(g):
    # shapely affine: x' = a*x + b, y' = d*y + e  with x=pixel-col, y=pixel-row
    return shapely.affinity.affine_transform(g, [a_lon, 0, 0, a_lat, b_lon, b_lat])

records = []
for k in range(K):
    g = class_polys[k]
    if g.is_empty:
        continue
    g = to_lonlat(g)
    g = make_valid(g)
    # keep only polygonal parts
    if g.geom_type == 'GeometryCollection':
        g = unary_union([p for p in g.geoms if p.geom_type in ('Polygon', 'MultiPolygon')])
    if g.geom_type == 'Polygon':
        g = MultiPolygon([g])
    records.append({
        'name': group_names[k],
        'legend_items': group_legend_n[k],
        'colour_hex': group_hex[k],
        'colour_group': k + 1,
        'geometry': g,
    })
gdf = gpd.GeoDataFrame(records, geometry='geometry', crs='EPSG:4326')
gdf['area_km2'] = (gdf.to_crs('EPSG:32632').area / 1e6).round(1)
if os.path.exists(OUT):
    os.remove(OUT)
gdf.to_file(OUT, layer='geology_polygons', driver='GPKG')

lookup = []
for n, (block, name, rgb) in enumerate(LEGEND, 1):
    k = next(gi for gi, g in enumerate(groups) if (n - 1) in g)
    lookup.append({
        'legend_no': n,
        'legend_block': block,
        'name': name,
        'swatch_hex': '#%02x%02x%02x' % rgb,
        'colour_group': k + 1,
        'polygon_name': group_names[k],
    })
gpd.GeoDataFrame(pd.DataFrame(lookup), geometry=None).to_file(OUT, layer='legend_lookup', driver='GPKG')

print('legend entries:', len(LEGEND), ' colour groups (polygon features):', K)
print('bounds lon/lat:', gdf.total_bounds.round(4).tolist())
print('written', OUT)
