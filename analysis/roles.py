#!/usr/bin/env python3
"""Presence maps for key palette colors (compact)."""
import numpy as np
from PIL import Image

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
X0, X1, Y0, Y1 = 69, 4153, 93, 3395
sub = a[Y0:Y1, X0:X1]
H, W, _ = sub.shape
GW, GH = 62, 30
cw, ch = W // GW, H // GH

targets = [
    ('OCEAN? (152,216,248)', (152,216,248)),
    ('STEELBLUE (120,200,216)', (120,200,216)),
    ('GRAY (216,216,216)', (216,216,216)),
    ('PERIWINKLE (152,168,248)', (152,168,248)),
    ('BLUEVIOLET (136,120,248)', (136,120,248)),
    ('SKYBLUE (120,184,248)', (120,184,248)),
    ('PALEPINK (248,200,232)', (248,200,232)),
    ('PALEYELLOW (248,248,184)', (248,248,184)),
    ('PALEGREEN (200,248,168)', (200,248,168)),
    ('PALEKHAKI (232,232,152)', (232,232,152)),
]
for name, t in targets:
    t = np.array(t)
    d = np.abs(sub - t).sum(axis=2)
    m = d < 45
    print('=== %s : %.2f%% ===' % (name, 100*m.mean()))
    for gy in range(GH):
        row = ''
        for gx in range(GW):
            f = m[gy*ch:(gy+1)*ch, gx*cw:(gx+1)*cw].mean()
            row += ' ' if f < 0.03 else ('.' if f < 0.15 else ('+' if f < 0.4 else ('*' if f < 0.7 else '#')))
        print('  |' + row + '|')
    print()
