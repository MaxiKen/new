#!/usr/bin/env python3
"""Zoom tool: render a crop as fine ASCII with dominant colors.
Usage: python3 zoom.py IMG X0 Y0 X1 Y1 [GW [GH]]
Chars: #=mostly black, .=mostly white, letters=colored (by hue), +=mixed
Also prints the 12 most common quantized colors in the crop.
"""
import sys
import numpy as np
from PIL import Image

img = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2:6])
GW = int(sys.argv[6]) if len(sys.argv) > 6 else 100
GH = int(sys.argv[7]) if len(sys.argv) > 7 else None

im = Image.open(img).convert('RGB')
W, H = im.size
x0, y0 = max(0, x0), max(0, y0)
x1, y1 = min(W, x1), min(H, y1)
a = np.asarray(im).astype(np.int16)[y0:y1, x0:x1]
h, w, _ = a.shape
if GH is None:
    GH = max(1, round(GW * h / w / 2.2))   # chars ~2.2:1 tall
cw, ch = max(1, w // GW), max(1, h // GH)

r, g, b = a[...,0], a[...,1], a[...,2]
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 100) & (sat < 70)
whiteish = (mn > 215) & (sat < 30)

def cell_char(yi, xi):
    ys, xs = yi*ch, xi*cw
    blk = blackish[ys:ys+ch, xs:xs+cw]
    wht = whiteish[ys:ys+ch, xs:xs+cw]
    n = blk.size
    bf, wf = blk.mean(), wht.mean()
    if bf > 0.5: return '#'
    if bf > 0.2: return '+'
    if wf > 0.7: return '.'
    # dominant color among all pixels
    rr, gg, bb = r[ys:ys+ch, xs:xs+cw], g[ys:ys+ch, xs:xs+cw], b[ys:ys+ch, xs:xs+cw]
    R, G, B = int(rr.mean()), int(gg.mean()), int(bb.mean())
    if R > 200 and G > 200 and B > 200: return '.'
    if max(R,G,B) < 100 and max(R,G,B)-min(R,G,B) < 70: return '#'
    s = max(R,G,B) - min(R,G,B)
    if s < 40: return 'w'  # light gray/gray
    if R >= G >= B and R - B > 40: return 'Y' if G - B > 40 else 'O'
    if G > R and G > B: return 'G'
    if B > R and B > G: return 'B'
    if R > G and R > B and B > G: return 'M'
    if R > G and R > B: return 'R'
    return '?'

print('crop x[%d:%d] y[%d:%d] (%dx%d) grid %dx%d cells (%dx%d px)' % (x0,x1,y0,y1,w,h,GW,GH,cw,ch))
hdr = '     ' + ''.join(str((i//10)%10) if i%10==0 else ' ' for i in range(GW))
hdr2 = '     ' + ''.join(str(i%10) for i in range(GW))
for yi in range(GH):
    row = ''.join(cell_char(yi, xi) for xi in range(GW))
    print('%4d %s' % (y0 + yi*ch, row))
print(hdr); print(hdr2)

# top quantized colors
q = (a[::3, ::3] // 32 * 32).reshape(-1, 3)
colors, counts = np.unique(q, axis=0, return_counts=True)
order = np.argsort(-counts)
print('\ntop colors (quantized to 32):')
for i in order[:12]:
    print('  rgb(%3d,%3d,%3d) %5.2f%%' % (colors[i][0], colors[i][1], colors[i][2], 100*counts[i]/counts.sum()))
