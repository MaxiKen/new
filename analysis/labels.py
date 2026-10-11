#!/usr/bin/env python3
"""Find coordinate labels inside map frame edges + graticule geometry."""
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 110) & (sat < 75)

# Map interior
X0, X1, Y0, Y1 = 69, 4153, 93, 3482

def blobs(mask, ox, oy, min_n=25):
    lab, n = ndimage.label(mask)
    out = []
    for i in range(1, n+1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < min_n: continue
        out.append((xs.min()+ox, xs.max()+ox, ys.min()+oy, ys.max()+oy, len(ys)))
    return out

# strips just inside each edge (where labels usually sit)
strips = {
 'top    (y 93..135)': blackish[93:135, X0:X1],
 'bottom (y 3430..3482)': blackish[3430:3482, X0:X1],
 'left   (x 69..115)': blackish[Y0:Y1, 69:115],
 'right  (x 4110..4153)': blackish[Y0:Y1, 4110:4153],
}
for name, mask in strips.items():
    ox, oy = (X0, 93) if name.startswith(('top','bottom')) else (69, Y0)
    if name.startswith('bottom'): oy = 3430
    if name.startswith('right'): ox = 4110
    bl = blobs(mask, ox, oy)
    print('=== %s : %d blobs ===' % (name, len(bl)))
    for b in bl[:40]:
        print('   x %d..%d y %d..%d n=%d' % b)
