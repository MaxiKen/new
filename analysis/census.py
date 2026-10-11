#!/usr/bin/env python3
"""Color census of map interior + legend swatch extraction."""
import numpy as np
from PIL import Image
from collections import Counter

im = Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')
a = np.asarray(im)
H, W, _ = a.shape

# map interior (inside neatlines, excluding bottom label band y>=3395)
X0, X1, Y0, Y1 = 69, 4153, 93, 3395
sub = a[Y0:Y1, X0:X1]
h, w, _ = sub.shape
print('interior %dx%d' % (w, h))

flat = sub.reshape(-1, 3)
# quantize to 8 to fight jpg noise
q = flat // 8 << 3
cnt = Counter(map(tuple, q))
print('\n=== top 60 quantized colors (step 8) in map interior ===')
tot = len(flat)
for c, n in cnt.most_common(60):
    print('  %3d %3d %3d  %6.3f%%' % (c[0], c[1], c[2], 100.0*n/tot))
print('unique quantized:', len(cnt))
