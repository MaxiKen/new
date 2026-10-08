import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
im = np.asarray(Image.open('/home/user/new/pic NGSA geological-map-of-nigeria-.jpg').convert('RGB')).astype(int)
g = im.mean(axis=2)
sat = im.max(axis=2) - im.min(axis=2)
def peaks_1d(vals, thr):
    idx = np.where(vals > thr)[0]
    out = []
    if idx.size:
        s = p = idx[0]
        for v in idx[1:]:
            if v != p + 1:
                out.append((int(s), int(p))); s = v
            p = v
        out.append((int(s), int(p)))
    return out
# Top margin ticks: rows 170..184, columns across the whole width
band = (g[170:185, :] < 200) & (sat[170:185, :] < 40)
frac = band.mean(axis=0)
xs = peaks_1d(frac, 0.6)
print('top-margin vertical tick columns:', [((a + b) / 2, b - a + 1) for a, b in xs][:60])
# Left margin ticks: columns 150..184 (between outer frame and inner frame)
band2 = (g[:, 150:184] < 200) & (sat[:, 150:184] < 40)
frac2 = band2.mean(axis=1)
ys = peaks_1d(frac2, 0.6)
print('left-margin horizontal tick rows:', [((a + b) / 2, b - a + 1) for a, b in ys][:80])
# Bottom margin: find frame rows near bottom of map (inner frame) - search rows 3400..3520 for long dark lines
rowdark = (g < 90).mean(axis=1)
print('rows with long dark runs (>30%):', [(a, b) for a, b in peaks_1d(rowdark, 0.3)])
coldark = (g < 90).mean(axis=0)
print('cols with long dark runs (>15%):', [(a, b) for a, b in peaks_1d(coldark, 0.15)])
