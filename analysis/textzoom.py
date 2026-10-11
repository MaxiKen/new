#!/usr/bin/env python3
"""Render text regions as 1:1 ASCII art so I can read them."""
import sys
import numpy as np
from PIL import Image

im = Image.open(sys.argv[1] if len(sys.argv) > 1 else 'NGSA_map_geology_legend_isolated.png').convert('RGB')
x0, y0, x1, y1 = map(int, sys.argv[2:6])
step = int(sys.argv[6]) if len(sys.argv) > 6 else 1
a = np.asarray(im).astype(np.int16)[y0:y1, x0:x1]
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 130) & (sat < 90)
print('region x %d..%d y %d..%d (1 char = %d px)' % (x0, x1, y0, y1, step))
h, w = blackish.shape
for yy in range(0, h, step):
    row = ''
    for xx in range(0, w, step):
        blk = blackish[yy:yy+step, xx:xx+step]
        row += '#' if blk.mean() > 0.4 else ('+' if blk.mean() > 0.15 else '.')
    print(row)
