#!/usr/bin/env python3
"""
V2 build (rev2): clean geology-only map from isolated PNG + NGSA original.
- hardcoded clean palette (from color census)
- fixes restricted to geology classes only
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import json, collections

ISO = 'NGSA_map_geology_legend_isolated.png'
ORG = 'pic NGSA geological-map-of-nigeria-.jpg'
OUT = 'NGSA_map_geology_legend_isolated_v2.png'

OX, OY = 120, 96
PARCH = 328.4
X0, X1, Y0, Y1 = 73, 4149, 96, 3394
MERX = [288 + i * PARCH for i in range(12)]
PARY = [3343 - i * PARCH for i in range(10)]
BOTTOM_ROW = Y1 - Y0 - 5

# ---- clean palette (hand-checked from census of the isolated map) ----
PAL_GEO = [
    (248,248,88), (216,216,120), (248,120,120), (248,184,72), (120,216,184),
    (248,248,184), (248,136,184), (216,168,8), (168,248,104), (152,232,88),
    (136,168,88), (88,168,56), (200,248,168), (184,232,120), (120,200,56),
    (248,248,8), (152,168,248), (216,136,232), (248,200,232), (136,120,248),
    (216,184,56), (248,248,136), (216,248,72), (232,232,152), (168,248,200),
    (184,120,72), (232,184,200), (232,200,104), (216,232,248),
    (248,112,80), (240,240,0), (240,208,208), (224,224,160), (224,192,192),
]
PAL_GEO += [(123,192,215), (122,184,252), (152,184,224)]   # alluvium valley blues (legend units)
SPECIALS = [('WHITE',(250,250,250)), ('OCEAN',(152,216,240))]
PALARR = np.array([list(c) for c in PAL_GEO] + [list(v) for _, v in SPECIALS], dtype=np.int32)
PALNAME = ['G%02d' % i for i in range(len(PAL_GEO))] + [k for k, _ in SPECIALS]
WATER_IDS = np.array([len(PAL_GEO)+i for i,(k,_) in enumerate(SPECIALS) if k != 'WHITE'])
WHITE_ID = len(PAL_GEO)
NG = len(PAL_GEO)
NP = len(PALARR)
json.dump({'geology': [list(c) for c in PAL_GEO], 'specials': {k: list(v) for k,v in SPECIALS}},
          open('analysis/palette_v2.json','w'), indent=1)

iso = np.asarray(Image.open(ISO).convert('RGB')).astype(np.int16)
org = np.asarray(Image.open(ORG).convert('RGB')).astype(np.int16)
iso_i = iso[Y0:Y1, X0:X1]
org_i = org[Y0+OY:Y1+OY, X0+OX:X1+OX]
h, w, _ = iso_i.shape
print('interior %dx%d, palette %d geo + %d special' % (w, h, NG, len(SPECIALS)), flush=True)

def blackish(a):
    mx = a.max(axis=2); mn = a.min(axis=2)
    return (mx < 110) & (mx - mn < 75)

def classify(arr):
    best = np.full((h, w), 1e9, np.float64)
    idx = np.full((h, w), -1, np.int16)
    for cid in range(NP):
        d = np.abs(arr.astype(np.int32) - PALARR[cid]).sum(axis=2).astype(np.float64)
        upd = d < best
        best[upd] = d[upd]; idx[upd] = cid
    idx[best > 70] = -1
    return idx

gy, gx = np.mgrid[0:h, 0:w]
near = np.zeros((h, w), bool)
for mx_ in MERX: near |= np.abs(gx + X0 - mx_) <= 4
for my_ in PARY: near |= np.abs(gy + Y0 - my_) <= 4
blk = blackish(iso_i)
grat_keep = blk & near
print('graticule keep px:', int(grat_keep.sum()), ' other black:', int((blk & ~near).sum()), flush=True)

print('classify...', flush=True)
iso_med = ndimage.median_filter(iso_i, size=(3,3,1))
cls_iso = classify(iso_med)
del iso_med
org_med = ndimage.median_filter(org_i, size=(5,5,1))
cls_org = classify(org_med)
org_blk = blackish(org_i)
org_blk_d = ndimage.binary_dilation(org_blk, iterations=3)
print('org text fraction: %.3f' % org_blk.mean(), flush=True)

def local_support(cls):
    sup = np.full_like(cls, -1); frac = np.zeros(cls.shape, np.float32)
    for cid in range(NP):
        cnt = ndimage.uniform_filter((cls == cid).astype(np.float32), size=9, mode='nearest')
        upd = cnt > frac
        sup[upd] = cid; frac[upd] = cnt[upd]
    return sup, frac

sup_iso, frac_iso = local_support(cls_iso)
sup_org, frac_org = local_support(cls_org)
del sup_iso, sup_org
print('support done', flush=True)

v2 = iso_i.copy()
cls_v2 = cls_iso.copy()
stats = collections.Counter()

org_geo = (cls_org >= 0) & (cls_org < NG)
iso_geo = (cls_iso >= 0) & (cls_iso < NG)

# Fix A: iso white, org has clean supported geology -> take org color
fixA = (cls_iso == WHITE_ID) & org_geo & (~org_blk_d) & (frac_org >= 0.5) & (~near)
stats['fixA_white_artifact'] = int(fixA.sum())
v2[fixA] = PALARR[cls_org[fixA]]; cls_v2[fixA] = cls_org[fixA]

# Fix B: iso colored (unsupported) where org is white -> back to white
fixB = iso_geo & (cls_org == WHITE_ID) & (frac_iso < 0.45) & (~near)
stats['fixB_overpaint_to_white'] = int(fixB.sum())
v2[fixB] = PALARR[WHITE_ID]; cls_v2[fixB] = WHITE_ID

# Fix C: both GEOLOGY but different; org wins only with clearly better support
diff = iso_geo & org_geo & (cls_iso != cls_org) & (~org_blk_d) & (~near)
fixC = diff & (frac_org > frac_iso + 0.15) & (frac_org >= 0.55)
stats['fixC_org_wins'] = int(fixC.sum())
stats['fixC_kept_iso'] = int((diff & ~fixC).sum())
v2[fixC] = PALARR[cls_org[fixC]]; cls_v2[fixC] = cls_org[fixC]

stray = (cls_v2 == -1) & ~grat_keep
stats['stray'] = int(stray.sum())
print('repairs:', dict(stats), flush=True)

# ---------- water ----------
r, g, b = v2[...,0].astype(np.int32), v2[...,1].astype(np.int32), v2[...,2].astype(np.int32)
wm = ((b-g) >= 12) & (b >= 220) & (g >= 195) & (r >= 105) & (r <= 175)
wm &= ~grat_keep
print('water px: %d (%.2f%%)' % (wm.sum(), 100*wm.mean()), flush=True)

rg_ = v2[...,0].astype(np.int32); gg_ = v2[...,1].astype(np.int32); bg_ = v2[...,2].astype(np.int32)
glueblue = ((bg_-gg_) >= 10) & (bg_ >= 195) & (gg_ >= 165) & (rg_ <= 175)
glue = near & (blk | wm | (glueblue & ndimage.binary_dilation(wm, iterations=4)))
er = ndimage.binary_erosion(wm, structure=np.ones((11,11)), border_value=0)
bigwater = ndimage.binary_dilation(er, structure=np.ones((11,11))) & wm
rivers = wm & ~bigwater
lab, n = ndimage.label(bigwater | glue)
bottom_ids = set(np.unique(lab[BOTTOM_ROW]).tolist()); bottom_ids.discard(0)
ocean = wm & np.isin(lab, list(bottom_ids))
inland = wm & ~ocean
print('rivers %d | bigwater %d | ocean %d | inland %d' %
      (rivers.sum(), bigwater.sum(), ocean.sum(), inland.sum()), flush=True)

lab2, n2 = ndimage.label(inland)
sizes = ndimage.sum(inland, lab2, range(1, n2+1))
objs = ndimage.find_objects(lab2)
comps = []
for i in np.argsort(-sizes)[:30]:
    if sizes[i] < 150: break
    sl = objs[i]
    comps.append((int(sizes[i]), sl[1].start+X0, sl[1].stop+X0, sl[0].start+Y0, sl[0].stop+Y0))
print('inland water components (to be filled):')
for c in comps:
    print('   %7d px  x %d..%d y %d..%d (lon %.2f..%.2f lat %.2f..%.2f)' % (
        c[0], c[1], c[2], c[3], c[4],
        3+(c[1]-288)/PARCH, 3+(c[2]-288)/PARCH, 4+(3343-c[4])/PARCH, 4+(3343-c[3])/PARCH), flush=True)
stats['water_rivers_removed'] = int(rivers.sum())
stats['water_inland_removed'] = int(inland.sum())

# ---------- fill ----------
to_fill = (rivers | inland | stray) & ~grat_keep
# eat the anti-aliasing ring around removed water so fills source clean unit colors
to_fill = ndimage.binary_dilation(to_fill, iterations=2) & ~grat_keep
print('to fill: %d' % to_fill.sum(), flush=True)
OCEAN_ID = NG + 1
# fills must never source from (or become) ocean-class pixels
src_invalid = to_fill | (cls_v2 == OCEAN_ID)
ind = ndimage.distance_transform_edt(src_invalid, return_distances=False, return_indices=True)
ys, xs = ind
cur_cls = cls_v2[ys, xs].copy()
cur_cls[cur_cls < 0] = WHITE_ID
cur_rgb = PALARR[cur_cls].astype(np.int16)   # fills only ever contain clean palette colors

for it in range(3):
    bestfrac = np.full((h, w), -1.0, np.float32)
    bestcls = cur_cls.copy()
    for cid in range(NP):
        if cid == OCEAN_ID: continue          # never spread ocean into fills
        cnt = ndimage.uniform_filter((cur_cls == cid).astype(np.float32), size=7, mode='nearest')
        upd = (cnt > bestfrac) & (cnt > 0.34)
        bestfrac[upd] = cnt[upd]; bestcls[upd] = cid
    upd = to_fill & (bestcls != cur_cls)
    print('  smooth pass %d: %d updates' % (it, int(upd.sum())), flush=True)
    cur_cls[upd] = bestcls[upd]; cur_rgb[upd] = PALARR[bestcls[upd]]

np.savez_compressed('analysis/v2_masks.npz', wm=wm, ocean=ocean, inland=inland,
                    to_fill=to_fill, rivers=rivers, grat=grat_keep)
v2[to_fill] = cur_rgb[to_fill]
cls_v2[to_fill] = cur_cls[to_fill]

# ---------- finalize ----------
out = v2
# fresh classification of the filled output, then snap
cls_out = classify(out)
geo = (cls_out >= 0) & (cls_out < NG) & ~grat_keep
out[geo] = PALARR[cls_out[geo]]
out[ocean] = np.array(SPECIALS[1][1])
out[(cls_out == WHITE_ID) & ~grat_keep] = np.array(SPECIALS[0][1])
# anything still unmatched -> nearest palette entry
left = ((cls_out == -1) | ((cls_out == OCEAN_ID) & ~ocean)) & ~grat_keep
if left.sum():
    bestd = np.full((h, w), 1e9, np.float64); bestc = np.zeros((h, w), np.int16)
    for cid in range(NP):
        if cid == OCEAN_ID: continue      # leftover land pixels must not snap to ocean
        d = np.abs(out.astype(np.int32) - PALARR[cid]).sum(axis=2).astype(np.float64)
        u = (d < bestd) & left
        bestd[u] = d[u]; bestc[u] = cid
    out[left] = PALARR[bestc[left]]
    print('leftover snapped:', int(left.sum()), flush=True)

final = iso.copy()
final[Y0:Y1, X0:X1] = out
final[Y0:Y1, X0:X1][grat_keep] = iso_i[grat_keep]
Image.fromarray(final.astype(np.uint8)).save(OUT)
print('saved', OUT, flush=True)

json.dump({'stats': {k: int(v) for k, v in stats.items()},
           'inland_water_components': comps,
           'palette_names': PALNAME},
          open('analysis/v2_build_stats.json', 'w'), indent=1)
print('DONE', flush=True)
