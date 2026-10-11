#!/usr/bin/env python3
"""Find precise map bbox and structural lines."""
import numpy as np
from PIL import Image

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.int16)
r, g, b = a[...,0], a[...,1], a[...,2]
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 100) & (sat < 70)
whiteish = (mn > 215) & (sat < 30)
colored = ~blackish & ~whiteish & (sat > 40)

colfrac = colored.mean(axis=0)
rowfrac = colored.mean(axis=1)
nz = np.nonzero(colfrac > 0.005)[0]
print('colored columns: %d..%d' % (nz.min(), nz.max()))
nzy = np.nonzero(rowfrac > 0.005)[0]
print('colored rows: %d..%d' % (nzy.min(), nzy.max()))

# black column profile -> long vertical lines
bcol = blackish.mean(axis=0)
cand = np.nonzero(bcol > 0.25)[0]
print('\nvertical black lines (>25% of height):')
groups = []
for x in cand:
    if groups and x - groups[-1][-1] <= 2: groups[-1].append(x)
    else: groups.append([x])
for gr in groups:
    x = int(np.mean(gr))
    seg = blackish[:, x]
    ys = np.nonzero(seg)[0]
    print('  x=%d..%d frac=%.2f span y %d..%d' % (gr[0], gr[-1], bcol[x], ys.min(), ys.max()))

brow = blackish.mean(axis=1)
cand = np.nonzero(brow > 0.25)[0]
print('\nhorizontal black lines (>25% of width):')
groups = []
for y in cand:
    if groups and y - groups[-1][-1] <= 2: groups[-1].append(y)
    else: groups.append([y])
for gr in groups:
    y = int(np.mean(gr))
    seg = blackish[y, :]
    xs = np.nonzero(seg)[0]
    print('  y=%d..%d frac=%.2f span x %d..%d' % (gr[0], gr[-1], brow[y], xs.min(), xs.max()))

# where does blackness live overall? quadrant density
print('\nblack pixel count:', blackish.sum(), ' colored:', colored.sum(), ' white:', whiteish.sum())
# black density in horizontal bands of 200px
for y0 in range(0, H, 200):
    band = blackish[y0:y0+200]
    print('  y %4d-%4d: black %.4f colored %.4f' % (y0, y0+200, band.mean(), colored[y0:y0+200].mean()))
