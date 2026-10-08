import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
im = np.asarray(Image.open('/home/user/new/pic NGSA geological-map-of-nigeria-.jpg').convert('RGB')).astype(float)
g = im.mean(axis=2)
# horizontal graticule rows: use white area x in [200, 600] (outside Nigeria, top-left white region and left region)
seg = g[:, 200:600]
rowmean = seg.mean(axis=1)
# background white ~ 255; line pixels darker. find local minima below 245 sustained
cand = np.where(rowmean < 246)[0]
groups = []
if cand.size:
    s = p = cand[0]
    for v in cand[1:]:
        if v != p + 1:
            groups.append((s, p)); s = v
        p = v
    groups.append((s, p))
print('rows with mean<246 in x[200,600]:')
for a, b in groups:
    if a > 150 and b < 3600:
        c = np.average(np.arange(a, b + 1), weights=(255 - rowmean[a:b + 1]))
        print('  rows %d-%d centroid %.2f depth %.1f' % (a, b, c, (255 - rowmean[a:b+1]).max()))
# vertical graticule columns in top margin rows 170..184 (sub-pixel)
for xc in [408, 736, 1065, 1393, 1722, 2050, 2378, 2706, 3035, 3363, 3691, 4020]:
    sub = g[170:185, xc - 6:xc + 7].mean(axis=0)
    dark = 255 - sub
    cx = np.average(np.arange(xc - 6, xc + 7), weights=np.clip(dark, 0, None) + 1e-9)
    print('meridian near %d -> centroid %.2f depth %.1f' % (xc, cx, dark.max()))
