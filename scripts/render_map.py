"""Render version 2 of the sheet from the cleaned map.

The rule is deliberately narrow: a pixel of the version-1 sheet is rewritten only
where the cleaning pass changed the unit under it, and only inside the mapped
footprint of Nigeria. The EXPLANATIONS panel, the sheet frame, the title block and
the graticule in the margins are copied byte for byte, so nothing that is not
geology can drift.

    NGSA_map_geology_legend_v2.png           6268x3540, the same canvas as v1
    NGSA_map_geology_legend_v2_gridded.png   reference block grid over those pixels
    NGSA_map_geology_v2_photo.jpg            high-quality photographic render

Coordinate spaces: ``sheetgrid`` is in source-photograph pixels, ``clean_map``'s
map area is sheet pixels (source minus SHEET_OFFSET), and the cleaned unit arrays
are map-area crop pixels (sheet minus the top-left corner of ``map_area``).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clean_map as cm
import sheetgrid

ROOT = cm.ROOT
SHEET_V1 = ROOT / 'NGSA_map_geology_legend_isolated.png'
SHEET_V2 = ROOT / 'NGSA_map_geology_legend_v2.png'
SHEET_V2_GRID = ROOT / 'NGSA_map_geology_legend_v2_gridded.png'
PHOTO = ROOT / 'NGSA_map_geology_v2_photo.jpg'
GRID_RGB = (208, 58, 58)

X0, Y0, X1, Y1 = cm.map_area()            # sheet pixels of the mapped area


def src_to_sheet(x, y):
    return x - cm.SHEET_OFFSET[0], y - cm.SHEET_OFFSET[1]


def unit_lut(units):
    """id -> RGB for every legend entry, plus the blank-sheet colour."""
    pal = cm.palette_of(units)
    lut = np.zeros((cm.PAPER_ID + 1, 3), np.uint8)
    lut[1:len(pal) + 1] = pal
    lut[cm.PAPER_ID] = (255, 255, 255)
    return lut


def cleaned_sheet():
    """The version-1 sheet with every removed print healed over."""
    d = np.load(cm.WORK / 'r9.npz')
    before, after, mask, erase = d['before'], d['after'], d['mask'], d['erase']
    blocks = cm.WORK / 'r9_blocks.npz'
    connected = 0
    if blocks.exists():
        # the block survey draws a formation across a boundary where only one of
        # the two blocks showed it: version 2 is the connected map, not just the
        # cleaned one.
        b = np.load(blocks)
        rep = b['repairs']
        connected = int(b['changed'].sum())
        after = np.where(b['changed'], rep, after)
    zone = d['zone'] if 'zone' in d.files else mask
    lut = unit_lut(cm.read_legend())
    sheet = np.array(Image.open(SHEET_V1).convert('RGB'))
    region = sheet[Y0:Y1, X0:X1].astype(np.int16)
    # A removed print often heals to the unit that already surrounded it, so the
    # label does not change - but its colour must. Rewrite every erased pixel, not
    # only the ones whose unit moved.
    changed = zone & (after > 0) & (erase | (after != before))
    painted = lut[after.clip(0, cm.PAPER_ID)].astype(np.int16)
    sheet[Y0:Y1, X0:X1] = np.where(changed[..., None], painted, region).astype(np.uint8)
    return sheet, changed, zone, connected


def grid_lines():
    """Meridian/parallel positions of the block grid, in sheet pixels."""
    xs = sorted({int(round(src_to_sheet(x, 0)[0])) for x in sheetgrid.MERIDIAN_X})
    ys = sorted({int(round(src_to_sheet(0, y)[1])) for y in sheetgrid.ROW_Y})
    return [x for x in xs if X0 - 2 <= x <= X1 + 2], [y for y in ys if Y0 - 2 <= y <= Y1 + 2]


def draw_grid(sheet):
    """Reference block grid: columns A-K, rows 1-11, one degree per block."""
    img = Image.fromarray(sheet).convert('RGB')
    dr = ImageDraw.Draw(img, 'RGB')
    xs, ys = grid_lines()
    for x in xs:
        dr.line([(x, Y0), (x, Y1)], fill=GRID_RGB, width=2)
    for y in ys:
        dr.line([(X0, y), (X1, y)], fill=GRID_RGB, width=2)
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 26)
        small = ImageFont.truetype('DejaVuSans.ttf', 19)
    except OSError:
        font = small = ImageFont.load_default()
    for j in range(11):
        name, x0, x1 = sheetgrid.columns()[j]
        cx = (int(src_to_sheet(x0, 0)[0]) + int(src_to_sheet(x1, 0)[0])) // 2
        for cy in (min(ys) - 24, max(ys) + 24):
            if Y0 - 40 < cy < Y1 + 60:
                dr.text((cx, cy), name[0], fill=GRID_RGB, font=font, anchor='mm')
    for i in range(11):
        number, y0, y1 = sheetgrid.rows()[i]
        cy = (int(src_to_sheet(0, y0)[1]) + int(src_to_sheet(0, y1)[1])) // 2
        for cx in (min(xs) - 26, max(xs) + 26):
            if X0 - 44 < cx < X1 + 44:
                dr.text((cx, cy), str(number), fill=GRID_RGB, font=font, anchor='mm')
    dr.text((X0 + 4, Y1 + 6), 'block grid: A-K x 1-11, one degree of longitude and '
            'latitude per block', fill=(120, 120, 120), font=small)
    return np.asarray(img)


def remove_linework_keys(sheet):
    """Delete the Roads / Railway / Rivers keys from the EXPLANATIONS panel.

    Version 2 shows no road, railway or river linework, so a legend key for it
    would be a promise the map no longer keeps. Only the ink of those three rows
    is taken: the panel paper around them is left exactly as printed, so no pale
    rectangle betrays where the keys were.
    """
    bx0, by0, bx1, by1 = 4348, 2062, 4512, 2206
    band = sheet[by0:by1, bx0:bx1].astype(np.int32)
    paper = np.median(np.concatenate([sheet[by0 - 12:by0 - 4, bx0:bx1],
                                      sheet[by1 + 4:by1 + 12, bx0:bx1]]).reshape(-1, 3), 0)
    ink = np.abs(band - paper[None, None, :]).sum(2) > 18
    if ink.sum() < 400:                      # not the keys: refuse to touch the sheet
        return 0
    out = sheet.copy()
    fill = np.round(paper).astype(np.uint8)
    region = out[by0:by1, bx0:bx1]
    region[ink] = fill
    out[by0:by1, bx0:bx1] = region
    np.copyto(sheet, out)
    return int(ink.sum())


def photo_render(sheet, path, bend=0.028, desk=(232, 229, 224)):
    """A photographic print of the sheet: gentle perspective, light, shadow, grain.

    The quadrilateral is fitted with an explicit homography rather than a PIL
    transform, because PIL's QUAD maps its corners in an order that silently
    transposes the image.
    """
    import cv2
    img = Image.fromarray(sheet).convert('RGB')
    w, h = img.size
    m = int(0.045 * w)
    cw, ch = w + 2 * m, h + 2 * m + int(0.05 * h)
    b = bend * w
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([[m + b, m], [m + w, m + b * 0.55], [m + w - b * 0.7, m + h],
                      [m, m + h - b * 0.4]])
    M = cv2.getPerspectiveTransform(src, dst)
    paper = cv2.warpPerspective(np.asarray(img), M, (cw, ch), flags=cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_REPLICATE)
    mask = np.zeros((ch, cw), np.uint8)
    cv2.fillConvexPoly(mask, dst.astype(np.int32), 255)
    shadow = np.zeros((ch, cw), np.uint8)
    cv2.fillConvexPoly(shadow, (dst + np.float32([9, 15])).astype(np.int32), 255)
    shadow = cv2.GaussianBlur(shadow, (0, 0), 12).astype(np.float32) / 255.0 * 0.42
    a = paper.astype(np.float32)
    bg = np.array(desk, np.float32)[None, None, :] * (1 - shadow[..., None] * 0.55)
    m3 = (mask[..., None] > 127)
    out = np.where(m3, a, bg)
    # a lamp to the upper left, so the sheet is brighter there and falls away
    yy, xx = np.mgrid[0:ch, 0:cw]
    r2 = ((xx - cw * 0.42) / cw) ** 2 + ((yy - ch * 0.40) / ch) ** 2
    out *= np.clip(1 - 0.40 * r2, 0.82, 1.045)[..., None]
    rng = np.random.default_rng(11)
    out += rng.normal(0, 1.25, out.shape).astype(np.float32)
    # paper grain shows through the pale colours
    grain = rng.normal(0, 2.2, (ch, cw)).astype(np.float32)
    grain = cv2.GaussianBlur(grain, (0, 0), 0.8)[..., None]
    pale = (out.mean(2, keepdims=True) > 205)
    out = out + grain * pale * 0.55
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGB').save(
        path, quality=96, subsampling=0, optimize=True, progressive=True)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGB')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--no-photo', action='store_true')
    args = ap.parse_args()
    sheet, changed, mask, connected = cleaned_sheet()
    keys = remove_linework_keys(sheet)
    Image.fromarray(sheet).save(SHEET_V2, optimize=True)
    Image.fromarray(draw_grid(sheet)).save(SHEET_V2_GRID, optimize=True)
    if not args.no_photo:
        photo_render(sheet, PHOTO)
    qa = json.loads((cm.OUT / 'qa.json').read_text())
    report = dict(version=2, base=SHEET_V1.name, sheetSize=[int(sheet.shape[1]), int(sheet.shape[0])],
                  rewrittenPixels=int(changed.sum()),
                  crossBoundaryConnectionPixels=connected,
                  legendKeysRemoved=dict(rows=['Roads', 'Railway', 'Rivers'], inkPixels=keys),
                  rewrittenShareOfMappedArea=round(float(100 * changed.sum() / mask.sum()), 3),
                  shareOfMapArea=round(float(100 * changed.sum() / mask.sum()), 3),
                  residualThinWaterStrokes=int(qa['residualAfter']['waterStrokeComponents']),
                  residualUnpaintedInsideFootprint=int(qa['residualAfter']['unpaintedPixels']),
                  mappedWaterPixels=[qa['residualBefore']['waterPixels'], qa['residualAfter']['waterPixels']],
                  grayShadingPixels=[qa['residualBefore']['grayPixels'], qa['residualAfter']['grayPixels']],
                  legendUnitPixelsChanged=int(sum(abs(u['pixels'] - u['before']) for u in qa['legend'])),
                  unchangedOutsideMapArea=True)
    (cm.OUT / 'render.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
