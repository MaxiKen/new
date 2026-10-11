#!/usr/bin/env python3
"""Diff isolated vs original NGSA: find exactly what was changed/cleaned."""
import numpy as np
from PIL import Image

iso = np.asarray(Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')).astype(np.int16)
org = np.asarray(Image.open('pic NGSA geological-map-of-nigeria-.jpg').convert('RGB')).astype(np.int16)

OX, OY = 120, 96
h, w = iso.shape[:2]
# map interior in iso coords
X0, X1, Y0, Y1 = 69, 4153, 93, 3395
# corresponding org region
ox0, oy0 = X0+OX, Y0+OY
ox1, oy1 = X1+OX, Y1+OY
print('org region x %d..%d y %d..%d (org size %s)' % (ox0, ox1, oy0, oy1, org.shape[:2]))

iso_sub = iso[Y0:Y1, X0:X1]
org_sub = org[oy0:oy1, ox0:ox1]
print('shapes', iso_sub.shape, org_sub.shape)

d = np.abs(iso_sub.astype(int) - org_sub.astype(int)).sum(axis=2)
changed = d > 40
print('changed pixels: %d (%.2f%%)' % (changed.sum(), 100*changed.mean()))

# ASCII map of change density
H, W = changed.shape
GW, GH = 62, 30
cw, ch = W//GW, H//GH
print('change density map (map interior, iso coords):')
for gy in range(GH):
    row = ''
    for gx in range(GW):
        f = changed[gy*ch:(gy+1)*ch, gx*cw:(gx+1)*cw].mean()
        row += ' ' if f < 0.02 else ('.' if f < 0.1 else ('+' if f < 0.3 else ('*' if f < 0.6 else '#')))
    print('  |' + row + '|')

# what colors are now in iso where changed?
ch = changed
if ch.sum():
    cols = iso_sub[ch]
    q = (cols // 16 << 4) if False else (cols // 16 * 16)
    import collections
    c = collections.Counter(map(tuple, q))
    print('\niso colors at changed px (top):')
    for col, n in c.most_common(10):
        print('   ', col, n)
    ocols = org_sub[ch]
    qo = ocols // 16 * 16
    co = collections.Counter(map(tuple, qo))
    print('org colors at changed px (top):')
    for col, n in co.most_common(10):
        print('   ', col, n)
np.save('analysis/changed_mask.npy', changed)
