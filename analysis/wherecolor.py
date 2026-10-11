#!/usr/bin/env python3
"""Where does a given color live? ASCII presence map for a target color."""
import sys
import numpy as np
from PIL import Image

target = np.array(list(map(int, sys.argv[1].split(','))))
tol = int(sys.argv[2]) if len(sys.argv) > 2 else 30
im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
d = np.abs(a - target).sum(axis=2)
m = d < tol * 3
H, W = m.shape
GW, GH = 120, 55
cw, ch = W // GW, H // GH
print('target rgb(%d,%d,%d) tol=%d : %d px (%.2f%%)' % (target[0], target[1], target[2], tol, m.sum(), 100*m.mean()))
print('   ' + ''.join(chr(65+i) for i in range(12)) + '| per-letter col = %dpx' % cw)
for gy in range(GH):
    row = ''
    for gx in range(GW):
        f = m[gy*ch:(gy+1)*ch, gx*cw:(gx+1)*cw].mean()
        row += ' ' if f < 0.02 else ('.' if f < 0.1 else ('+' if f < 0.3 else ('*' if f < 0.6 else '#')))
    print('%2d %s' % (gy, row))
