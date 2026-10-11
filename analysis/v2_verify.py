#!/usr/bin/env python3
"""
Block-by-block verification of v2 vs the original NGSA map.
Grid: columns A..L = 3-4E ... 14-15E; rows 1..10 = 13-14N (top) ... 4-5N (bottom).
For every block: agreement with the original's geology (text masked out),
edge-continuity with the 4 neighbors, and the actions taken.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import json

OX, OY = 120, 96
PARCH = 328.4
X0I, Y0I = 69, 93            # map interior bounds (incl. tick rows)
X1I, Y1I = 4153, 3394

pal = json.load(open('analysis/palette_v2.json'))
PAL_GEO = [tuple(c) for c in pal['geology']]
SPECIALS = [(k, tuple(v)) for k, v in pal['specials'].items()]
PALARR = np.array([list(c) for c in PAL_GEO] + [list(v) for _, v in SPECIALS], dtype=np.int32)
NG = len(PAL_GEO)
OCEAN_ID = NG + 1
WHITE_ID = NG

v2 = np.asarray(Image.open('NGSA_map_geology_legend_isolated_v2.png').convert('RGB')).astype(np.int16)
org = np.asarray(Image.open('pic NGSA geological-map-of-nigeria-.jpg').convert('RGB')).astype(np.int16)
iso = np.asarray(Image.open('NGSA_map_geology_legend_isolated.png').convert('RGB')).astype(np.int16)
d = np.load('analysis/v2_masks.npz')
wm, to_fill = d['wm'], d['to_fill']

h, w = wm.shape   # interior coords of the processed region (X0=73,Y0=96)
def in_proc(x, y):
    return 73 <= x < 73 + w and 96 <= y < 96 + h

def classify_sub(arr):
    hh, ww, _ = arr.shape
    best = np.full((hh, ww), 1e9, np.float64)
    idx = np.full((hh, ww), -1, np.int16)
    for cid in range(len(PALARR)):
        dd = np.abs(arr.astype(np.int32) - PALARR[cid]).sum(axis=2).astype(np.float64)
        upd = dd < best
        best[upd] = dd[upd]; idx[upd] = cid
    return idx, best

def blackish(a):
    mx = a.max(axis=2); mn = a.min(axis=2)
    return (mx < 110) & (mx - mn < 75)

MERX = [288 + i * PARCH for i in range(13)]
PARY = [3343 - i * PARCH for i in range(11)]

def tile_box(ci, ri):
    """ci 0..11 (A..L), ri 0..9 (row1=13-14N top ... row10=4-5N bottom).
    Returns x0, x1, ytop, ybot in full-image coords."""
    x0 = int(round(MERX[ci])) + 2
    x1 = int(round(MERX[ci + 1])) + 2
    ytop = int(round(PARY[10 - ri]))     # upper parallel (higher lat); ri=0 -> 14N
    ybot = int(round(PARY[9 - ri]))      # lower parallel; ri=0 -> 13N
    return x0, x1, ytop, ybot

results = []
print('BLOCK VERIFICATION  (v2 vs original NGSA, text masked)')
print('%-4s %-11s %8s %8s %8s %8s %8s %8s  %s' % (
    'blk', 'extent', 'agreeno', 'uncert', 'edgeN', 'edgeS', 'edgeE', 'edgeW', 'water_px'))

for ri in range(10):
    for ci in range(12):
        x0, x1, yt, yb = tile_box(ci, ri)
        blk = chr(65 + ci) + str(ri + 1)
        # org block (aligned) and v2 block
        ob = org[yt+OY:yb+OY, x0+OX:x1+OX]
        vb = v2[yt:yb, x0:x1]
        obm = ndimage.median_filter(ob, size=(5, 5, 1))
        oblk = blackish(ob)
        oblk_d = ndimage.binary_dilation(oblk, iterations=2)
        # classify
        cls_o, dist_o = classify_sub(obm)
        cls_v, dist_v = classify_sub(vb)
        # v2 colors are palette-exact -> confident
        comp = ~oblk_d & (dist_o <= 45)
        agree = (comp & (cls_o == cls_v)).sum()
        n_comp = comp.sum()
        uncertain = ((~oblk_d) & (dist_o > 45)).sum()
        agr = agree / max(1, n_comp)
        # water + fill actions inside this block (interior coords)
        wx0, wy0 = max(x0 - 73, 0), max(yt - 96, 0)
        wx1, wy1 = min(x1 - 73, w), min(yb - 96, h)
        water_px = int(wm[wy0:wy1, wx0:wx1].sum())
        fill_px = int(to_fill[wy0:wy1, wx0:wx1].sum())

        # edge continuity: compare class strips across each internal edge
        def edge_cont(e):
            (ax0, ay0, ax1, ay1, bx0, by0) = e
            sa = v2[ay0:ay1, ax0:ax1]
            sb = v2[by0:by0 + (ay1 - ay0), bx0:bx0 + (ax1 - ax0)]
            ca, _ = classify_sub(sa)
            cb, _ = classify_sub(sb)
            m = (ca >= 0) & (cb >= 0)      # ignore graticule/black on either side
            return float((ca[m] == cb[m]).mean()) if m.any() else 1.0
        cont = {}
        if ri > 0:      # north edge: block top row vs row above
            cont['N'] = edge_cont((x0, yt, x1, yt + 2, x0, yt - 2))
        if ri < 9:      # south
            cont['S'] = edge_cont((x0, yb - 2, x1, yb, x0, yb))
        if ci < 11:     # east
            cont['E'] = edge_cont((x1 - 2, yt, x1, yb, x1, yt))
        if ci > 0:      # west
            cont['W'] = edge_cont((x0, yt, x0 + 2, yb, x0 - 2, yt))
        results.append(dict(blk=blk, ci=ci, ri=ri,
                            lon=(3 + ci, 4 + ci), lat=(13 - ri, 14 - ri),
                            agree=round(agr, 4), n_comp=int(n_comp),
                            uncertain=int(uncertain),
                            edges={k: round(v, 3) for k, v in cont.items()},
                            water_px=water_px, fill_px=fill_px))
        print('%-4s %d-%dE %d-%dN %8.1f%% %7.1f%% %8s %8s %8s %8s  %d' % (
            blk, 3 + ci, 4 + ci, 13 - ri, 14 - ri, 100 * agr,
            100 * uncertain / max(1, uncertain + n_comp),
            ('%.2f' % cont['N']) if 'N' in cont else '-',
            ('%.2f' % cont['S']) if 'S' in cont else '-',
            ('%.2f' % cont['E']) if 'E' in cont else '-',
            ('%.2f' % cont['W']) if 'W' in cont else '-',
            water_px))

json.dump(results, open('analysis/block_results.json', 'w'), indent=1)
print('\nsaved analysis/block_results.json')
