#!/usr/bin/env python3
"""Clean legend swatch extraction: x 5464..5518, stable color runs."""
import numpy as np
from PIL import Image

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)

x0, x1 = 5466, 5516
col = a[60:3450, x0:x1]
med = np.median(col, axis=1).astype(int)   # per-row median rgb
sat = (col.max(axis=2) - col.min(axis=2)).mean(axis=1)

runs = []
cur = None
for i in range(len(med)):
    y = 60 + i
    m, s = med[i], sat[i]
    ok = s > 25                      # colored row (not black/white border)
    if cur is not None:
        cm = np.mean(cur['cols'], axis=0)
        sim = np.abs(m - cm).sum() < 60
    else:
        sim = False
    if ok and (cur is not None) and sim and y - cur['y1'] <= 3:
        cur['y1'] = y; cur['cols'].append(m)
    else:
        if cur is not None: runs.append(cur)
        cur = {'y0': y, 'y1': y, 'cols': [m]} if ok else None
if cur is not None: runs.append(cur)

# merge runs separated by tiny gaps with same color
merged = []
for r in runs:
    if merged and r['y0'] - merged[-1]['y1'] <= 4:
        cm1 = np.mean(merged[-1]['cols'], axis=0); cm2 = np.mean(r['cols'], axis=0)
        if np.abs(cm1 - cm2).sum() < 60:
            merged[-1]['y1'] = r['y1']; merged[-1]['cols'] += r['cols']; continue
    merged.append(r)

print('legend swatches (y0..y1 h medianRGB):')
out = []
for r in merged:
    if r['y1'] - r['y0'] < 10: continue
    c = np.mean(r['cols'], axis=0).astype(int)
    out.append((r['y0'], r['y1'], tuple(c)))
    print('  y %4d..%4d h=%3d  rgb(%3d,%3d,%3d)' % (r['y0'], r['y1'], r['y1']-r['y0']+1, c[0], c[1], c[2]))
print(len(out), 'swatches')
