#!/usr/bin/env python3
"""Cluster map interior colors into a palette; save palette + presence maps."""
import numpy as np
from PIL import Image
import json

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
X0, X1, Y0, Y1 = 69, 4153, 93, 3395
sub = a[Y0:Y1, X0:X1].reshape(-1, 3)

# sample every 3rd pixel
s = sub[::3].astype(np.float32)
# quantize to 16 first
q = (np.floor(s / 16) * 16)
colors, counts = np.unique(q, axis=0, return_counts=True)
order = np.argsort(-counts)
cands = colors[order]

# greedy clustering: take colors in freq order, absorb others within dist 48
palette = []
pal_count = []
for c, n in zip(cands, counts[order]):
    c = c.astype(np.float32)
    hit = False
    for i, p in enumerate(palette):
        if abs(c[0]-p[0]) + abs(c[1]-p[1]) + abs(c[2]-p[2]) < 48:
            pal_count[i] += n
            hit = True
            break
    if not hit:
        palette.append(c); pal_count.append(n)

print('clusters:', len(palette))
GW, GH = 78, 40
mask_all = np.zeros((Y1-Y0, X1-X0), bool)
H, W = mask_all.shape
cw, ch = W // GW, H // GH
res = []
for i, (p, n) in enumerate(zip(palette, pal_count)):
    if n / len(s) < 0.0008: continue
    res.append((int(p[0])+8, int(p[1])+8, int(p[2])+8, int(n)))
json.dump(res, open('analysis/palette.json', 'w'))
for r in res:
    print('  rgb(%3d,%3d,%3d)  %5.2f%%' % (r[0], r[1], r[2], 100.0*r[3]/len(s)))
