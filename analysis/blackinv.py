#!/usr/bin/env python3
"""Inventory black components inside the map: sizes, shapes -> text vs lines."""
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 110) & (sat < 75)
H, W = blackish.shape

# map interior
X0, X1, Y0, Y1 = 69, 4153, 93, 3395
mask = np.zeros_like(blackish)
mask[Y0:Y1, X0:X1] = blackish[Y0:Y1, X0:X1]
# remove graticule lines & neatline zone (they are at known positions)
mer = [288,616,945,1273,1602,1929,2258,2587,2915,3244,3571,3900]
par = [388,716,1045,1373,1702,2030,2358,2686,3015,3343]
for x in mer:
    mask[:, x-4:x+5] = False
for y in par:
    mask[y-4:y+5, :] = False

lab, n = ndimage.label(mask)
print('components:', n)
sizes = ndimage.sum(mask, lab, range(1, n+1))
objs = ndimage.find_objects(lab)
big = np.argsort(-sizes)
print('\nbiggest 40 black components (excl. graticule):')
for i in big[:40]:
    sl = objs[i]
    y0, y1 = sl[0].start, sl[0].stop
    x0, x1 = sl[1].start, sl[1].stop
    w, h = x1-x0, y1-y0
    print('  n=%6d  bbox x %4d..%4d y %4d..%4d  (w=%d h=%d)  geo(%.2fE %.2fN)' % (
        sizes[i], x0, x1, y0, y1, w, h,
        3+(x0-288)/328.4, 4+(3343-y0)/328.4))

# shape classes
linelike = 0; textlike = 0; other = []
for i in range(n):
    sl = objs[i]; s = sizes[i]
    if s < 10: continue
    w = sl[1].stop - sl[1].start; h = sl[0].stop - sl[0].start
    if (w > 200 or h > 200) and s / (w*h) < 0.35:
        linelike += 1; other.append((int(s), sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, 'LINE'))
    elif s < 4000 and max(w, h) < 250:
        textlike += 1
print('\nlinelike:', linelike, ' textlike(chars):', textlike)
