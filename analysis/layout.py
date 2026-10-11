#!/usr/bin/env python3
"""Layout analysis of the isolated map picture."""
import numpy as np
from PIL import Image

IM = 'NGSA_map_geology_legend_isolated.png'
im = Image.open(IM).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.int16)
print('size', W, H)

r, g, b = a[..., 0], a[..., 1], a[..., 2]
mx = a.max(axis=2); mn = a.min(axis=2)
sat = mx - mn
blackish = (mx < 90) & (sat < 60)          # dark, low-saturation -> text/lines
whiteish = (mn > 225) & (sat < 25)         # near-white background
grayish  = (sat < 25) & (mx >= 90) & (mn <= 225)  # mid gray

print('black frac %.3f  white frac %.3f  gray frac %.3f' %
      (blackish.mean(), whiteish.mean(), grayish.mean()))

# Coarse grid map: for each cell, fraction of black / white / colored
gw, gh = 48, 27
cw, ch = W / gw, H / gh
print('\ncell size %.0f x %.0f' % (cw, ch))
print('cols are %.1f px wide; rows %.1f px tall' % (cw, ch))

# Row/col profiles of blackness to find text bands and map frame
black_rows = blackish.mean(axis=1)
black_cols = blackish.mean(axis=0)
white_rows = whiteish.mean(axis=1)

def runs(mask, minlen=1):
    out = []; s = None
    for i, v in enumerate(mask):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s >= minlen: out.append((s, i - 1))
            s = None
    if s is not None: out.append((s, len(mask) - 1))
    return out

# Find large white horizontal bands (margins between map and legend)
print('\nrows with >60% white:', runs(white_rows > 0.6, 5))
print('rows with >90% white:', runs(white_rows > 0.9, 5))
print('rows with >40% black:', runs(black_rows > 0.40, 3))
print('cols with >40% black:', runs(black_cols > 0.40, 3))
