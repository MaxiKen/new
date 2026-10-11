"""Assemble the map from its 121 blocks, with the sheet's legend, and audit the seams.

Each block was drawn on its own during the survey (``blocks.py``). This puts the
blocks back together into one sheet - the map area is pasted block by block, A1
first, K11 last, each block carrying only what its own survey mapped - and then
checks the joints: along every printed meridian and parallel of the block grid, a
formation must meet the same formation on the far side of the line. The count is
reported for version 1 (as published) and for the assembled result, so the effect
of the cross-boundary work is measurable rather than asserted.

Outputs
    NGSA_map_geology_v2_blocks.png           blocks reassembled, legend intact
    NGSA_map_geology_v2_blocks_photo.jpg     high-quality photographic render of it
    data/clean/blocks/seams.json             the seam audit
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blocks as bl
import clean_map as cm
import render_map as rm
import sheetgrid

ROOT = cm.ROOT
OUT_PNG = ROOT / 'NGSA_map_geology_v2_blocks.png'
OUT_PHOTO = ROOT / 'NGSA_map_geology_v2_blocks_photo.jpg'
X0, Y0, X1, Y1 = cm.map_area()


def to_sheet_x(src_x):
    return int(round(src_x - cm.SHEET_OFFSET[0]))


def to_sheet_y(src_y):
    return int(round(src_y - cm.SHEET_OFFSET[1]))


def lut_of(units):
    pal = cm.palette_of(units)
    lut = np.zeros((cm.PAPER_ID + 1, 3), np.uint8)
    lut[1:len(pal) + 1] = pal
    lut[cm.PAPER_ID] = (255, 255, 255)
    return lut


def mosaic(sheet, ids, lut):
    """Paste every block's own drawing into the sheet, in survey order."""
    out = sheet.copy()
    covered = np.zeros(ids.shape, bool)
    for name, letter, number, *_ in sheetgrid.cells():
        x0, y0, x1, y1 = bl.cell_box(letter, number)
        if x1 <= x0 or y1 <= y0:
            continue
        tile = lut[ids[y0:y1, x0:x1].clip(0, cm.PAPER_ID)]
        out[Y0 + y0:Y0 + y1, X0 + x0:X0 + x1] = tile
        covered[y0:y1, x0:x1] = True
    return out, covered


def seam_audit(ids, zone, painted):
    """Crossings of unit boundaries with the block grid, before and after.

    A seam is *continuous* where the formation touching the line on one side is the
    same formation on the far side. Anything else is a cut block boundary - a
    formation that stops at the grid line instead of running through it.
    """
    res = {}
    for tag, arr in (('version1', ids['before']), ('assembled', ids['after'])):
        cut = kept = 0
        for x in sheetgrid.MERIDIAN_X:
            sx = to_sheet_x(x) - X0
            if not (1 <= sx < arr.shape[1]):
                continue
            left = arr[:, sx - 1]
            right = arr[:, sx]
            ok = zone[:, sx - 1] & zone[:, sx] & painted[:, sx - 1] & painted[:, sx]
            same = (left == right) | (left == cm.PAPER_ID) | (right == cm.PAPER_ID)
            kept += int((ok & same).sum())
            cut += int((ok & ~same).sum())
        for y in sheetgrid.PARALLEL_Y:
            sy = to_sheet_y(y) - Y0
            if not (1 <= sy < arr.shape[0]):
                continue
            up, dn = arr[sy - 1, :], arr[sy, :]
            ok = zone[sy - 1, :] & zone[sy, :] & painted[sy - 1, :] & painted[sy, :]
            same = (up == dn) | (up == cm.PAPER_ID) | (dn == cm.PAPER_ID)
            kept += int((ok & same).sum())
            cut += int((ok & ~same).sum())
        res[tag] = dict(continuousPx=kept, cutPx=cut,
                        cutShare=round(100 * cut / max(kept + cut, 1), 3))
    return res


def main():
    units = cm.read_legend()
    lut = lut_of(units)
    d = np.load(cm.WORK / 'r9.npz')
    b = np.load(cm.WORK / 'r9_blocks.npz')
    ids = np.where(b['changed'], b['repairs'], d['after']).astype(np.int16)
    sheet = np.array(Image.open(rm.SHEET_V2).convert('RGB'))
    out, covered = mosaic(sheet, ids, lut)
    Image.fromarray(out).save(OUT_PNG, optimize=True)
    rm.photo_render(out, OUT_PHOTO, bend=0.026)
    np.savez_compressed(cm.WORK / 'r9_assembled.npz', ids=ids, covered=covered)
    audit = seam_audit({'before': d['before'], 'after': ids}, d['zone'], d['mask'])
    audit['mosaic'] = dict(blocks=121, mapAreaPixels=int(d['zone'].sum()),
                           coveredByBlocks=int(covered.sum()),
                           coverageOfMapArea=round(100 * float(covered.sum()) / d['zone'].sum(), 2),
                           outsideBlocksKept=int((d['zone'] & ~covered).sum()))
    audit['files'] = [OUT_PNG.name, OUT_PHOTO.name]
    (ROOT / 'data/clean/blocks/seams.json').write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
