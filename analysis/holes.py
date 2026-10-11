#!/usr/bin/env python3
"""Find white holes inside the colored (geology) region + water body inventory."""
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(int)
X0, X1, Y0, Y1 = 69, 4153, 93, 3395
sub = a[Y0:Y1, X0:X1]
h, w, _ = sub.shape

mx = sub.max(axis=2); mn = sub.min(axis=2); sat = mx - mn
white = (mn > 215) & (sat < 30)
# ocean/lake blue family: pale blue, B>R, G between, not too dark
blue = (sub[...,2] > sub[...,0] + 40) & (sub[...,2] > 190) & (sub[...,1] > 170)
mxs = sub.max(axis=2); mns = sub.min(axis=2)

lab, n = ndimage.label(white)
print('white components:', n)
# which touch the border of the interior?
border_ids = set(lab[0,:]) | set(lab[-1,:]) | set(lab[:,0]) | set(lab[:,-1])
sizes = ndimage.sum(white, lab, range(1, n+1))
holes = []
for i in range(1, n+1):
    if i in border_ids: continue
    if sizes[i-1] < 12: continue
    ys, xs = np.nonzero(lab == i)
    holes.append((int(sizes[i-1]), xs.min(), xs.max(), ys.min(), ys.max()))
holes.sort(reverse=True)
print('white holes (not connected to border): %d, top 30:' % len(holes))
for s, x0, x1, y0, y1 in holes[:30]:
    print('  %6d px  x %d..%d y %d..%d  (%dx%d)  geo %.2fE %.2fN' % (
        s, x0+X0, x1+X0, y0+Y0, y1+Y0, x1-x0+1, y1-y0+1,
        3+(x0+X0-288)/328.4, 4+(3343-(y0+Y0))/328.4))

# water bodies: blue components not connected to the ocean (south edge / big)
lab2, n2 = ndimage.label(blue)
sizes2 = ndimage.sum(blue, lab2, range(1, n2+1))
print('\nblue components:', n2)
big = np.argsort(-sizes2)
for i in big[:15]:
    if sizes2[i] < 200: break
    ys, xs = np.nonzero(lab2 == i+1)
    print('  %7d px  x %d..%d y %d..%d  geo %.2fE %.2fN' % (
        sizes2[i], xs.min()+X0, xs.max()+X0, ys.min()+Y0, ys.max()+Y0,
        3+(xs.min()+X0-288)/328.4, 4+(3343-(ys.min()+Y0))/328.4))
