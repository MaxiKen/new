#!/usr/bin/env python3
"""Measure spans of structural lines to identify panels/boxes."""
import numpy as np
from PIL import Image

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 110) & (sat < 75)

def segs(mask, min_gap=30, min_len=80):
    """Return contiguous runs of True with gaps merged if < min_gap."""
    idx = np.nonzero(mask)[0]
    if len(idx) == 0: return []
    out = []
    s = p = idx[0]
    for i in idx[1:]:
        if i - p <= min_gap: p = i
        else:
            if p - s >= min_len: out.append((s, p))
            s = p = i
    if p - s >= min_len: out.append((s, p))
    return out

print('=== horizontal lines: segments along x ===')
for y in [5, 19, 66, 91, 2686, 3015, 3343, 3484, 3534]:
    row = blackish[y]
    print('y=%4d:' % y, segs(row))

print()
print('=== vertical lines: segments along y ===')
for x in [5, 19, 67, 288, 616, 2258, 2587, 2915, 3244, 3571, 3900, 4155, 4194, 5282, 5462, 5521, 6263]:
    col = blackish[:, x]
    print('x=%4d:' % x, segs(col))
