#!/usr/bin/env python3
"""Tile census: 12 (A-L, 3-14E) x 10 (1-10, 13N-4N) degree tiles.
Compare isolated vs original NGSA per tile."""
import numpy as np
from PIL import Image

iso = np.asarray(Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')).astype(int)
org = np.asarray(Image.open('pic NGSA geological-map-of-nigeria-.jpg').convert('RGB')).astype(int)
OX, OY = 120, 96

# graticule pixel anchors in iso coords
MERX = [288 + i*328.4 for i in range(13)]        # 3E..15E edges (last = beyond right frame)
PARY = [3343 - i*328.4 for i in range(11)]       # 4N..14N edges

def tile_box(ci, ri):
    """col ci: 0=A (3-4E) ... 11=L (14-15E); row ri: 0=row1 (13-14N) top ... 9=row10 (4-5N) bottom"""
    x0 = int(round(MERX[ci])) + 2
    x1 = int(round(MERX[ci+1])) + 2
    y1 = int(round(PARY[ri])) - 1     # top (higher lat -> smaller y)
    y0 = int(round(PARY[ri+1])) - 1   # bottom
    return x0, y0, x1, y1   # y0 bottom, y1 top

def classify(arr):
    mx = arr.max(axis=2); mn = arr.min(axis=2); sat = mx - mn
    white = (mn > 215) & (sat < 30)
    blue = (arr[...,2] > arr[...,0] + 40) & (arr[...,2] > 190) & (arr[...,1] > 170) & ~white
    black = (mx < 110) & (sat < 75)
    colored = ~white & ~blue & ~black
    return white, blue, black, colored

print('TILE CENSUS (iso | org)  fractions of tile area')
print('col  row  lon    lat     iso_white iso_blue iso_col | org_white org_blue org_col org_black | verdict')
rows = []
for ri in range(10):
    for ci in range(12):
        x0, y0, x1, y1 = tile_box(ci, ri)
        t_iso = iso[y0:y1, x0:x1]
        t_org = org[y0+OY:y1+OY, x0+OX:x1+OX]
        wI, bI, kI, cI = classify(t_iso)
        wO, bO, kO, cO = classify(t_org)
        n = t_iso.shape[0]*t_iso.shape[1]
        lat_hi = 13 - ri
        verdict = 'OK'
        if cI.mean() < 0.10 and cO.mean() > 0.25: verdict = 'MISSING(white)'
        elif cI.mean() + 0.25 < cO.mean(): verdict = 'PARTIAL'
        elif bI.mean() > 0.5 and cO.mean() > 0.3: verdict = 'WRONG(blue)'
        print('%s%-2d %d-%dE %d-%dN   %8.2f %8.2f %7.2f | %8.2f %8.2f %7.2f %7.2f  %s' % (
            chr(65+ci), ri+1, 3+ci, 4+ci, lat_hi-1, lat_hi,
            wI.mean(), bI.mean(), cI.mean(),
            wO.mean(), bO.mean(), cO.mean(), kO.mean(), verdict))
        rows.append((chr(65+ci), ri+1, verdict))
print()
from collections import Counter
print(Counter(v for _,_,v in rows))
