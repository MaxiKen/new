import numpy as np, cv2, geopandas as gpd
from PIL import Image
OUT = '/home/user/work/out/'
gdf = gpd.read_file(OUT + 'nigeria_geology.gpkg', layer='nigeria_geology')
def render(bbox, W, H):
    lon0, lon1, lat0, lat1 = bbox
    sx = W / (lon1 - lon0); sy = H / (lat1 - lat0)
    idx = -np.ones((H, W), np.int32)
    for li, row in enumerate(gdf.itertuples()):
        geoms = row.geometry.geoms if hasattr(row.geometry, 'geoms') else [row.geometry]
        for g in geoms:
            m = np.zeros((H, W), np.uint8)
            ext = np.array(g.exterior.coords)
            cv2.fillPoly(m, [np.round(np.column_stack([(ext[:, 0]-lon0)*sx, (lat1-ext[:, 1])*sy])).astype(np.int32)], 1)
            for hole in g.interiors:
                hc = np.array(hole.coords)
                cv2.fillPoly(m, [np.round(np.column_stack([(hc[:, 0]-lon0)*sx, (lat1-hc[:, 1])*sy])).astype(np.int32)], 0)
            idx[m == 1] = li
    rgb = np.full((H, W, 3), 255, np.uint8)
    for li, row in enumerate(gdf.itertuples()):
        hx = row.colour_hex
        col = (128, 128, 128) if not hx else tuple(int(hx[k:k+2], 16) for k in (1, 3, 5))
        rgb[idx == li] = col
    return rgb
full = render((2.6, 14.8, 4.2, 14.0), 1012, 826)
zoom = render((6.5, 10.0, 8.6, 11.9), 1000, 760)
h = max(full.shape[0], zoom.shape[0])
pad = lambda a: np.pad(a, ((0, h - a.shape[0]), (0, 8), (0, 0)), constant_values=255)
Image.fromarray(np.concatenate([pad(full), pad(zoom)], axis=1)).save(OUT + 'qa_render_pair.png')
print('final QA render written')
