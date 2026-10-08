import numpy as np, json
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
im = np.asarray(Image.open('/home/user/new/pic NGSA geological-map-of-nigeria-.jpg').convert('RGB')).astype(int)
def runs_of(mask):
    idx = np.where(mask)[0]
    out = []
    if idx.size == 0:
        return out
    s = p = idx[0]
    for v in idx[1:]:
        if v != p + 1:
            out.append((int(s), int(p))); s = v
        p = v
    out.append((int(s), int(p)))
    return out
x0, x1 = 5590, 5634
y0, y1 = 120, 3520
sub = im[y0:y1, x0:x1]
nonwhite = sub.min(axis=2) < 232
frac = nonwhite.mean(axis=1)
rows = frac > 0.6
res = []
for a, b in runs_of(rows):
    if b - a + 1 >= 14:
        block = sub[a:b + 1]
        m = block.min(axis=2) >= 110   # exclude dark text
        # use the median over the non-text pixels
        px = block[m] if m.sum() > 50 else block.reshape(-1, 3)
        c = np.median(px, axis=0)
        res.append({'y0': a + y0, 'y1': b + y0, 'h': b - a + 1, 'rgb': [int(v) for v in c]})
print('n swatches', len(res))
for i, r in enumerate(res):
    print(i + 1, r['y0'], r['y1'], r['h'], r['rgb'])
json.dump(res, open('/home/user/work/p2_swatches_raw.json', 'w'), indent=1)
