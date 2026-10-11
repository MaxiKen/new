"""Block-by-block survey of the cleaned map, A1 -> K11, with cross-boundary work.

The sheet is divided by its own printed block grid (``sheetgrid``): eleven columns
A-K and eleven rows 1-11, one degree of longitude and latitude to a block. Blocks
are taken in reading order - A1, B1, C1 ... K1, then A2 - and for each one the
script

1. maps the features in the block: which formations are present, how much of the
   block each covers, and whether each is a body, a ribbon or a speck;
2. draws it, i.e. writes the block on its own so the mapping can be checked
   without the rest of the sheet around it;
3. examines the eight neighbouring blocks and *establishes* the connections: a
   formation that reaches a boundary must reach it at the same place on the far
   side, so a crossing that exists on one side only is drawn across, and the four
   blocks meeting at each corner are checked for a joint they all agree on.

The labels are corrected in place as the survey proceeds, so block D4 is surveyed
on the map left by C2..E3, and the accumulated repair layer is saved for the
renderer. Outputs: one JSON report per block in ``data/clean/blocks/``, a PNG per
block under ``.cache/build/blocks/``, and ``data/clean/blocks/report.json``.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clean_map as cm
import sheetgrid

ROOT = cm.ROOT
WORK = cm.WORK
OUT = ROOT / 'data/clean/blocks'
DEBUG = ROOT / '.cache/build/blocks'
CROP_ORIGIN = (cm.CROP[0], cm.CROP[1])     # the block grid is in source pixels
STRIP = 3                                  # px compared on each side of a boundary
MIN_RUN = 6                                # px of disagreement worth repairing
BODY, RIBBON, SPECK = 'body', 'ribbon', 'speck'


def cell_box(letter, number):
    """Block box in cleaned-array (map-area crop) pixels."""
    x0, y0, x1, y1 = sheetgrid.bbox_of(f'{letter}{number}')
    ax0, ay0 = CROP_ORIGIN
    return (max(int(round(x0)) - ax0, 0), max(int(round(y0)) - ay0, 0),
            min(int(round(x1)) - ax0, cm.CROP[2] - ax0),
            min(int(round(y1)) - ay0, cm.CROP[3] - ay0))


def classify(mask_2d):
    """Split one formation in one block into bodies, ribbons and specks."""
    if not mask_2d.any():
        return dict(bodies=0, ribbons=0, specks=0, features=[])
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask_2d.astype(np.uint8), 8)
    edt = ndi.distance_transform_edt(mask_2d)
    feats = []
    for i in range(1, int(n)):
        comp = lab == i
        area = int(stats[i, 4])
        width = float(2 * edt[comp].max() + 1)
        length = float(max(stats[i, 2], stats[i, 3]))
        kind = SPECK if area < 20 else (RIBBON if width <= 8.0 and length > 3.5 * width else BODY)
        feats.append(dict(area=area, width=round(width, 2), length=round(length, 1),
                          top_left=[int(stats[i, 0]), int(stats[i, 1])], kind=kind))
    feats.sort(key=lambda f: -f['area'])
    return dict(bodies=sum(1 for f in feats if f['kind'] == BODY),
                ribbons=sum(1 for f in feats if f['kind'] == RIBBON),
                specks=sum(1 for f in feats if f['kind'] == SPECK),
                features=feats[:12])


def block_features(ids, valid, units):
    """Per-formation census of one block."""
    total = int(valid.sum())
    rows = []
    for u in units:
        m = (ids == u['id']) & valid
        px = int(m.sum())
        if px == 0:
            continue
        c = classify(m)
        rows.append(dict(id=int(u['id']), code=u['code'], name=u['name'], color=u['color'],
                         pixels=px, shareOfBlock=round(100 * px / max(total, 1), 2),
                         bodies=c['bodies'], ribbons=c['ribbons'], specks=c['specks'],
                         largest=c['features'][0] if c['features'] else None))
    rows.sort(key=lambda r: -r['pixels'])
    return rows, total


def boundary_runs(side_a, side_b, vertical, ids_a, ids_b, valid_a, valid_b):
    """Where each formation arrives at a boundary, from both sides.

    ``matched`` counts boundary positions at which the same formation arrives from
    both blocks - a connection already established. Each run in ``runs`` is a
    stretch where it arrives from one side only: the connection is broken there and
    has to be drawn across.
    """
    a, b = (side_a, side_b) if vertical else (side_a.T, side_b.T)
    va, vb = (valid_a, valid_b) if vertical else (valid_a.T, valid_b.T)
    matched, runs = {}, []
    uids = {int(v) for v in np.unique(ids_a[valid_a]) if v > 0}
    uids |= {int(v) for v in np.unique(ids_b[valid_b]) if v > 0}
    for uid in sorted(uids):
        ta = (a == uid).any(1) & va.any(1)
        tb = (b == uid).any(1) & vb.any(1)
        if not (ta | tb).any():
            continue
        matched[uid] = dict(both=int((ta & tb).sum()), aOnly=int((ta & ~tb).sum()),
                            bOnly=int((tb & ~ta).sum()))
        disagree, i, n = ta ^ tb, 0, len(ta)
        while i < n:
            if not disagree[i]:
                i += 1
                continue
            j = i
            while j + 1 < n and disagree[j + 1]:
                j += 1
            if j - i + 1 >= MIN_RUN:
                has = 'a' if ta[i] else 'b'
                onto = 'b' if has == 'a' else 'a'
                far = (a if onto == 'a' else b)[i:j + 1].ravel()
                runs.append(dict(uid=uid, start=int(i), stop=int(j), length=int(j - i + 1),
                                 has=has, onto=onto,
                                 displaced=sorted(set(int(v) for v in far if v > 0))))
            i = j + 1
    return matched, runs


def edge_strips(box, shape):
    """The boundary-adjacent strips of a block, keyed by compass side."""
    x0, y0, x1, y1 = box
    h, w = shape
    out = {}
    if x1 < w:
        out['E'] = ((slice(y0, y1), slice(x1 - STRIP, x1)), (slice(y0, y1), slice(x1, x1 + STRIP)), True)
    if x0 > 0:
        out['W'] = ((slice(y0, y1), slice(x0, x0 + STRIP)), (slice(y0, y1), slice(x0 - STRIP, x0)), True)
    if y1 < h:
        out['S'] = ((slice(y1 - STRIP, y1), slice(x0, x1)), (slice(y1, y1 + STRIP), slice(x0, x1)), False)
    if y0 > 0:
        out['N'] = ((slice(y0, y0 + STRIP), slice(x0, x1)), (slice(y0 - STRIP, y0), slice(x0, x1)), False)
    return out


def neighbour_name(letter, number, side):
    di = {'E': 1, 'W': -1}.get(side, 0)
    dj = {'S': 1, 'N': -1}.get(side, 0)
    i, j = sheetgrid.LETTERS.index(letter) + di, number - 1 + dj
    if 0 <= i < 11 and 0 <= j < 11:
        return f'{sheetgrid.LETTERS[i]}{j + 1}'
    return None


def main():
    DEBUG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    units = cm.read_legend()
    pal = cm.palette_of(units)
    lut = np.zeros((cm.PAPER_ID + 1, 3), np.uint8)
    lut[1:len(pal) + 1] = pal
    lut[cm.PAPER_ID] = (255, 255, 255)
    d = np.load(WORK / 'r9.npz')
    ids = d['after'].astype(np.int16).copy()
    zone, painted = d['zone'], d['mask']
    shape = ids.shape
    repairs = np.zeros(shape, np.int16)
    tally = dict(cells=0, boundaries=0, matchedCrossings=0, brokenRuns=0,
                 repairedRuns=0, repairedPixels=0, skippedAtPaper=0, cornerJoints=0)

    for name, letter, number, _x, _y, _x1, _y1 in sheetgrid.cells():
        x0, y0, x1, y1 = cell_box(letter, number)
        if x1 <= x0 or y1 <= y0:
            continue
        feats, total = block_features(ids[y0:y1, x0:x1], zone[y0:y1, x0:x1], units)
        geology = int((zone[y0:y1, x0:x1] & painted[y0:y1, x0:x1] & (ids[y0:y1, x0:x1] > 0)
                       & ~np.isin(ids[y0:y1, x0:x1], [cm.PAPER_ID, cm.WATER_ID])).sum())
        checks = {}
        for side, (box_a, box_b, vertical) in edge_strips((x0, y0, x1, y1), shape).items():
            nbr = neighbour_name(letter, number, side)
            if nbr is None:
                continue
            A, B = ids[box_a], ids[box_b]
            va = zone[box_a] & painted[box_a]
            vb = zone[box_b] & painted[box_b]
            tally['boundaries'] += 1
            if not (va.any() and vb.any()):
                checks[side] = dict(neighbour=nbr, skipped='one side is unmapped ground')
                continue
            matched, runs = boundary_runs(A, B, vertical, A, B, va, vb)
            applied = 0
            for r in runs:
                tgt_box = box_a if r['onto'] == 'a' else box_b
                # a vertical boundary runs down the strip, so the crossing index is
                # a row of the strip; a horizontal one runs across, so it is a column
                along = A.shape[0] if vertical else A.shape[1]
                assert 0 <= r['start'] <= r['stop'] < along, (name, side, r)
                m = np.zeros(A.shape, bool)
                if vertical:
                    m[r['start']:r['stop'] + 1, :] = True
                else:
                    m[:, r['start']:r['stop'] + 1] = True
                assert m.any()
                view = ids[tgt_box[0], tgt_box[1]]
                bad = np.isin(view, [cm.PAPER_ID, cm.WATER_ID]) & m
                if bad.any():
                    tally['skippedAtPaper'] += 1
                    r['heldBack'] = int(bad.sum())
                    m &= ~bad
                    if not m.any():
                        r['applied'] = False
                        r['skipped'] = 'blank sheet or open water on the far side'
                        continue
                view = ids[tgt_box[0], tgt_box[1]]
                view[m] = np.int16(r['uid'])
                ids[tgt_box[0], tgt_box[1]] = view
                rview = repairs[tgt_box[0], tgt_box[1]]
                rview[m] = np.int16(r['uid'])
                repairs[tgt_box[0], tgt_box[1]] = rview
                r['applied'] = True
                applied += int(m.sum())
                tally['repairedRuns'] += 1
            tally['brokenRuns'] += len(runs)
            tally['repairedPixels'] += applied
            tally['matchedCrossings'] += sum(v['both'] for v in matched.values())
            checks[side] = dict(neighbour=nbr, unitsMatched={k: v for k, v in matched.items()},
                                brokenRuns=len(runs), repairedPixels=applied, runs=runs[:10])

        # the four blocks meeting at each corner of this one
        corners = []
        for ci, (dx, dy) in (('SE', (1, 1)), ('SW', (-1, 1)), ('NE', (1, -1)), ('NW', (-1, -1))):
            px, py = (x1 if dx > 0 else x0), (y1 if dy > 0 else y0)
            quads = {}
            for qi, (ox, oy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
                xa, xb = ((px, px + STRIP) if ox == 0 else (px - STRIP, px))
                ya, yb = ((py, py + STRIP) if oy == 0 else (py - STRIP, py))
                if not (0 <= xa < shape[1] and 0 <= ya < shape[0] and xb <= shape[1] and yb <= shape[0]):
                    continue
                w = ids[ya:yb, xa:xb][zone[ya:yb, xa:xb] & painted[ya:yb, xa:xb]]
                quads[qi] = sorted(set(int(v) for v in np.unique(w) if v > 0))
            joint = None
            for v in quads.get(0, []):
                if all(v in q for q in quads.values()) and len(quads) == 4:
                    joint = v if joint is None else joint
                    tally['cornerJoints'] += 1
            corners.append(dict(corner=ci, blocks=sheetgrid.neighbours(letter, number),
                                quadrants={str(k): v for k, v in quads.items()},
                                jointUnit=joint))

        entry = dict(cell=name, box=[int(x0), int(y0), int(x1), int(y1)],
                     zonePixels=total, geologyPixels=geology,
                     mappedFraction=round(100 * geology / max(total, 1), 1), formations=feats, neighbours=sheetgrid.neighbours(letter, number),
                     edges=checks, corners=corners)
        (OUT / f'{name}.json').write_text(json.dumps(entry, indent=1))
        crop = lut[ids[y0:y1, x0:x1].clip(0, cm.PAPER_ID)]
        Image.fromarray(crop).resize((crop.shape[1] * 2, crop.shape[0] * 2),
                                     Image.NEAREST).save(DEBUG / f'{name}.png')
        tally['cells'] += 1
        print('%-4s formations %-3d geology %7d px (%4.1f%%)  dominant %-5s  broken crossings %-3d  drawn across %d px'
              % (name, len(feats), geology, 100 * geology / max(total, 1), (feats[0]['code'] if feats else '-'),
                 sum(c.get('brokenRuns', 0) for c in checks.values()),
                 sum(c.get('repairedPixels', 0) for c in checks.values())), flush=True)

    np.savez_compressed(WORK / 'r9_blocks.npz', repairs=np.where(repairs > 0, repairs, 0).astype(np.int16),
                        changed=repairs > 0, ids=ids)
    (OUT / 'report.json').write_text(json.dumps(tally, indent=2))
    print(json.dumps(tally, indent=2))


if __name__ == '__main__':
    main()
