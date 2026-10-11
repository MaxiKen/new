#!/usr/bin/env python3
"""ASCII visualization of the isolated map: my 'eyes' for layout."""
import numpy as np
from PIL import Image

IM = 'NGSA_map_geology_legend_isolated.png'
im = Image.open(IM).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.int16)
r, g, b = a[...,0], a[...,1], a[...,2]
mx = a.max(axis=2); mn = a.min(axis=2); sat = mx - mn
blackish = (mx < 100) & (sat < 70)
whiteish = (mn > 215) & (sat < 30)

# hue-ish classification for colored pixels
colored = ~blackish & ~whiteish

def dominant_char(bs, ws, cs, rs, gs, bls):
    n = bs.size
    bf, wf, cf = bs.mean(), ws.mean(), cs.mean()
    if bf > 0.25: return '#'
    if wf > 0.55: return '.'
    if cf < 0.08: return ','   # sparse mixed
    # dominant hue among colored
    rr, gg, bb = rs.mean(), gs.mean(), bls.mean()
    if rr > gg + 25 and rr > bb + 25: return 'R'
    if gg > rr + 15 and gg > bb + 15: return 'G'
    if bb > rr + 25 and bb > gg + 15: return 'B'
    if rr > bb + 25 and gg > bb + 25 and abs(rr-gg) < 40: return 'Y'
    if rr > gg + 25 and bb > gg + 25: return 'M'
    if gg > rr + 15 and bb > rr + 15: return 'C'
    if rr > 200 and gg > 150 and bls.mean() < 120: return 'O'
    return 'o'

GW, GH = 120, 60
cw, chh = W // GW, H // GH
lines = []
for gy in range(GH):
    line = []
    for gx in range(GW):
        y0, y1 = gy*chh, (gy+1)*chh
        x0, x1 = gx*cw, (gx+1)*cw
        blk = blackish[y0:y1, x0:x1]; wht = whiteish[y0:y1, x0:x1]
        col = colored[y0:y1, x0:x1]
        rs, gs, bls = r[y0:y1,x0:x1][col], g[y0:y1,x0:x1][col], b[y0:y1,x0:x1][col]
        line.append(dominant_char(blk, wht, col, rs, gs, bls))
    lines.append(''.join(line))
print('ASCII map (each char = %dx%d px): #=black,.=white, hue letters' % (cw, chh))
for i, l in enumerate(lines):
    print('%2d %s' % (i, l))
print('    ' + ''.join(str((i//10)%10) if i%10==0 else ' ' for i in range(GW)))
print('    ' + ''.join(str(i%10) for i in range(GW)))
