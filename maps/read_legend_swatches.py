#!/usr/bin/env python3
"""Read each sheet's printed legend swatches: measure the colours, not the guess.

The colour-to-class mapping in `IMAGES` was transcribed by eye, and the
vectorisation run showed how far off it was - median dE 15-27 and worst over 100,
which is enough to put a class label on the wrong polygon.  The swatches printed
on the sheet are solid rectangles, so their colours can simply be measured.

Method: inside a legend crop, find solid rectangular blobs (bounding-box fill
ratio close to 1 - that is what separates a swatch from a letter), keep the ones
that share a column, sort them top to bottom, and take the median colour of each.
The measured colours replace the transcription wherever a swatch is found.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.color import rgb2lab

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import georef_new_map as G  # noqa: E402

HERE = pathlib.Path(__file__).parent
OUT = HERE / "legend_swatches.json"

# generous legend crops, as fractions of the sheet (x0, y0, x1, y1)
CROP = {
    "raster_dem":              (0.60, 0.30, 1.00, 0.65),
    "raster_soil_ph":          (0.70, 0.50, 1.00, 0.90),
    "raster_temperature":      (0.00, 0.80, 1.00, 1.00),
    "raster_forest_reserves":  (0.60, 0.70, 1.00, 1.00),
    "raster_landcover":        (0.00, 0.65, 0.60, 1.00),
    "raster_population":       (0.58, 0.52, 1.00, 0.90),
    "raster_ethnic_groups":    (0.00, 0.05, 0.34, 0.65),
    "raster_dominant_soils":   (0.68, 0.00, 1.00, 0.80),
    "raster_general_geology":  (0.00, 0.70, 1.00, 1.00),
}


def find_swatches(img, maxpx=2200):
    """Solid coloured rectangles anywhere on the page, grouped into legend stacks.

    No cropping: a swatch is a filled rectangle, so it can be found by shape
    (bounding-box fill ratio close to 1) and colour (not black, not paper).  That
    also survives the sheets whose legend is in two columns or sits in a corner.
    Groups that share a column and are stacked with regular gaps are a legend.
    """
    W, H = img.size
    f = min(1.0, maxpx / max(W, H))
    a = np.asarray(img.resize((int(W * f), int(H * f)), Image.LANCZOS)).astype(np.int16)
    h, w = a.shape[:2]
    q = (a // 4 * 4).astype(np.uint8)
    vals, counts = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    bg = vals[counts.argmax()]
    chroma = a.max(2) - a.min(2)
    # a swatch is coloured, or a deliberate dark block - but never near-paper and
    # never a thin black rule
    fg = (np.abs(a - bg).max(2) > 26) & (a.max(2) > 40)
    fg &= (chroma > 22) | (a.max(2) < 120)
    fg = ndimage.binary_closing(fg, np.ones((3, 3)))
    fg = ndimage.binary_opening(fg, np.ones((3, 3)))

    lab, n = ndimage.label(fg)
    if not n:
        return []
    boxes = []
    min_w = max(8, int(w * 0.010))
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        ys, xs = sl
        bh, bw = ys.stop - ys.start, xs.stop - xs.start
        if bw < min_w or bh < 4 or bw > w * 0.5 or bh > h * 0.12:
            continue
        if not (0.15 <= bw / bh <= 12):
            continue
        m = lab[sl] == i
        if m.mean() < 0.88:                       # solid fill, not a glyph
            continue
        px = a[sl][m]
        med = np.median(px, axis=0)
        if (med.max() - med.min()) < 20 and med.max() > 140:
            continue                              # grey area, not a swatch
        boxes.append(dict(x=int(xs.start), y=int(ys.start), w=int(bw), h=int(bh),
                          rgb=[int(v) for v in med],
                          hex="#%02x%02x%02x" % tuple(int(v) for v in med)))
    if not boxes:
        return []

    # group into stacks: same column (x within half a swatch), regular vertical gaps
    boxes.sort(key=lambda b: (b["x"], b["y"]))
    used, groups = set(), []
    for i, b in enumerate(boxes):
        if i in used:
            continue
        grp = [i]
        used.add(i)
        grew = True
        while grew:
            grew = False
            for j, o in enumerate(boxes):
                if j in used:
                    continue
                if any(abs(o["x"] - boxes[k]["x"]) <= max(3, boxes[k]["w"] * 0.35)
                       and abs(o["w"] - boxes[k]["w"]) <= max(3, boxes[k]["w"] * 0.35)
                       and abs(o["h"] - boxes[k]["h"]) <= max(3, boxes[k]["h"] * 0.6)
                       and 0 < (o["y"] - boxes[k]["y"]) <= 4 * max(boxes[k]["h"], o["h"])
                       for k in grp):
                    grp.append(j)
                    used.add(j)
                    grew = True
        groups.append(sorted(grp, key=lambda j: boxes[j]["y"]))
    out = []
    for g in groups:
        if len(g) < 2:
            continue
        stack = [boxes[j] for j in g]
        # de-duplicate rows that are the same swatch split in two
        clean = []
        for b in stack:
            if clean and abs(b["y"] - clean[-1]["y"]) < max(2, b["h"] * 0.5):
                continue
            clean.append(b)
        out.append(dict(n=len(clean), x=clean[0]["x"], swatches=clean))
    out.sort(key=lambda s: -s["n"])
    return out


def main():
    res = {}
    for spec in G.IMAGES:
        name = spec["layer"]
        im = G.load_rgb(G.SRC / spec["file"])
        W, H = im.size
        want = len(spec["legend"])
        # the whole page first, then quadrant crops at higher resolution: on the
        # 10,000-px soils scan the swatches are sub-pixel at page scale
        groups = find_swatches(im)
        for (cx0, cy0, cx1, cy1) in ((0.62, 0.0, 1.0, 0.55), (0.62, 0.45, 1.0, 1.0),
                                     (0.0, 0.05, 0.4, 0.7), (0.0, 0.6, 0.6, 1.0),
                                     (0.55, 0.0, 1.0, 0.5), (0.55, 0.45, 1.0, 1.0),
                                     (0.0, 0.0, 1.0, 0.35), (0.0, 0.62, 1.0, 1.0)):
            crop = im.crop((int(W * cx0), int(H * cy0), int(W * cx1), int(H * cy1)))
            groups += find_swatches(crop, maxpx=1500)
        groups.sort(key=lambda g: -g["n"])
        best = None
        for g in groups:
            if abs(g["n"] - want) <= max(1, want * 0.15):
                best = g
                break
        if best is None and groups:
            best = min(groups, key=lambda g: abs(g["n"] - want))
        got = best["swatches"] if best else []
        res[name] = dict(expected=want, n=len(got),
                         stacks=[g["n"] for g in groups],
                         swatches=got)
        print(f"{name:24s} legend lists {want:3d}  stacks found {[g['n'] for g in groups][:8]}"
              f"  chose {len(got):3d}")
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
