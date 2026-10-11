#!/usr/bin/env python3
"""Extract legend swatch colors from the legend swatch column x 5464..5519."""
import numpy as np
from PIL import Image

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)

# find colored runs in the swatch column
col = a[:, 5466:5518]
mean = col.mean(axis=1)  # per-row mean rgb
mx = col.max(axis=2); mn = col.min(axis=2); sat = (mx - mn).mean(axis=1)
# a row is "swatch" if saturated color (not black border, not white gap)
rows = []
for y in range(60, 3450):
    m = mean[y]
    s = sat[y]
    rows.append((y, tuple(m), s))

# group consecutive rows with similar color
runs = []
cur = None
for y, c, s in rows:
    if s > 30 and max(c) < 250:  # colored
        if cur and y - cur['y1'] <= 2 and abs(c[0]-cur['c'][-1][0]) < 30 and abs(c[1]-cur['c'][-1][1]) < 30 and abs(c[2]-cur['c'][-1][2]) < 30:
            cur['y1'] = y; cur['c'].append(c)
        else:
            if cur: runs.append(cur)
            cur = {'y0': y, 'y1': y, 'c': [c]}
    else:
        if cur: runs.append(cur); cur = None
if cur: runs.append(cur)

print('swatch runs (y0..y1, height, mean color):')
for r in runs:
    if r['y1'] - r['y0'] < 12: continue  # too small
    cs = np.array(r['c'])
    m = cs.mean(axis=0).astype(int)
    print('  y %4d..%4d  h=%3d  rgb(%3d,%3d,%3d)  std(%d,%d,%d)' % (
        r['y0'], r['y1'], r['y1']-r['y0']+1, m[0], m[1], m[2],
        cs[:,0].std(), cs[:,1].std(), cs[:,2].std()))
