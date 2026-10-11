#!/usr/bin/env python3
"""Measure parallel line segments + find all label text near map edges."""
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 110) & (sat < 75)

def segs(mask, min_gap=25, min_len=60):
    idx = np.nonzero(mask)[0]
    if len(idx) == 0: return []
    out = []; s = p = idx[0]
    for i in idx[1:]:
        if i - p <= min_gap: p = i
        else:
            if p - s >= min_len: out.append((int(s), int(p)))
            s = p = i
    if p - s >= min_len: out.append((int(s), int(p)))
    return out

print('=== parallel line segments (x spans) ===')
for lat, y in [(4,3343),(5,3015),(6,2686),(7,2358),(8,2030),(9,1702),(10,1373),(11,1045),(12,716),(13,388)]:
    row = blackish[y-1:y+2, :].any(axis=0)
    print('  %dN y=%d:' % (lat, y), segs(row))

print()
print('=== meridian line segments (y spans) ===')
for lon, x in [(3,288),(4,616),(5,945),(6,1273),(7,1602),(8,1929),(9,2258),(10,2587),(11,2915),(12,3244),(13,3571),(14,3900)]:
    col = blackish[:, x-1:x+2].any(axis=1)
    print('  %dE x=%d:' % (lon, x), segs(col))

# Find text blobs near edges inside map: big-ish clusters that are not lines
def text_blobs(x0, x1, y0, y1, tag):
    band = blackish[y0:y1, x0:x1]
    # remove long horizontal/vertical runs: erode-ish approach: label blobs, filter size
    lab, n = ndimage.label(band)
    out = []
    for i in range(1, n+1):
        ys, xs = np.nonzero(lab == i)
        w = xs.max()-xs.min()+1; h = ys.max()-ys.min()+1
        if len(ys) < 40: continue
        if w > 300 or h > 300: continue  # lines
        if w < 4 and h > 100: continue   # vertical line pieces
        if h < 4 and w > 100: continue   # horizontal line pieces
        out.append((int(xs.min()+x0), int(xs.max()+x0), int(ys.min()+y0), int(ys.max()+y0), len(ys)))
    print('=== %s: %d text-ish blobs ===' % (tag, len(out)))
    for b in out[:60]: print('   x %d..%d y %d..%d n=%d' % b)

text_blobs(70, 4150, 136, 230, 'top inside map (below ticks)')
text_blobs(70, 300, 395, 3480, 'left inside map')
text_blobs(3850, 4150, 395, 3480, 'right inside map')
text_blobs(70, 4150, 3400, 3480, 'bottom above neatline')
