#!/usr/bin/env python3
"""Full structural scan of the right panel + margin label detection."""
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im).astype(np.int16)
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 110) & (sat < 75)

# --- all vertical lines in right panel x 4194..6268, threshold 0.15 ---
print('=== vertical lines, right panel ===')
sub = blackish[:, 4196:6268]
frac = sub.mean(axis=0)
xs = np.nonzero(frac > 0.15)[0] + 4196
groups = []
for x in xs:
    if groups and x - groups[-1][-1] <= 3: groups[-1].append(x)
    else: groups.append([x])
for gr in groups:
    x = int(np.mean(gr))
    ys = np.nonzero(blackish[:, x])[0]
    # contiguous span
    print('  x=%d frac=%.2f  yspan %d..%d' % (x, frac[x-4196], ys.min(), ys.max()))

print('=== horizontal lines, right panel ===')
sub = blackish[66:3534, 4196:6268]
frac = sub.mean(axis=0) if False else sub.mean(axis=1)
ys = np.nonzero(frac > 0.15)[0] + 66
groups = []
for y in ys:
    if groups and y - groups[-1][-1] <= 3: groups[-1].append(y)
    else: groups.append([y])
for gr in groups:
    y = int(np.mean(gr))
    xs = np.nonzero(blackish[y, 4196:6268])[0] + 4196
    print('  y=%d frac=%.2f  xspan %d..%d' % (y, frac[y-66], xs.min(), xs.max()))

# --- margin label blobs ---
def blobs(mask):
    lab, n = ndimage.label(mask)
    if n == 0: return []
    out = []
    for i in range(1, n+1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 30: continue
        out.append((xs.min(), xs.max(), ys.min(), ys.max(), len(ys)))
    return out

print('\n=== top margin band y 6..64 (text blobs, map x range) ===')
band = blackish[8:63, 20:4190]
for b in blobs(band):
    print('  x %d..%d y %d..%d n=%d  cx=%d' % (b[0]+20, b[1]+20, b[2]+8, b[3]+8, b[4], (b[0]+b[1])//2+20))

print('\n=== top band y 68..89 (between frames) ===')
band = blackish[69:89, 70:4150]
for b in blobs(band):
    print('  x %d..%d y %d..%d n=%d  cx=%d' % (b[0]+70, b[1]+70, b[2]+69, b[3]+69, b[4], (b[0]+b[1])//2+70))

print('\n=== left band x 21..64 (text blobs) ===')
band = blackish[92:3480, 21:64]
for b in blobs(band):
    print('  x %d..%d y %d..%d n=%d  cy=%d' % (b[0]+21, b[1]+21, b[2]+92, b[3]+92, b[4], (b[2]+b[3])//2+92))

print('\n=== bottom band y 3486..3532 ===')
band = blackish[3486:3532, 20:4190]
for b in blobs(band):
    print('  x %d..%d y %d..%d n=%d  cx=%d' % (b[0]+20, b[1]+20, b[2]+3486, b[3]+3486, b[4], (b[0]+b[1])//2+20))

print('\n=== right band x 4196..5280 (text blobs) ===')
band = blackish[92:3480, 4196:5280]
for b in blobs(band):
    print('  x %d..%d y %d..%d n=%d  cy=%d' % (b[0]+4196, b[1]+4196, b[2]+92, b[3]+92, b[4], (b[2]+b[3])//2+92))
