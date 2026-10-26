#!/usr/bin/env python3
"""Decide, per sheet, whether a class map should ship as polygons or as pixels.

The question is not taste.  A printed thematic map is either

  (a) **flat fills with hard edges** - a boundary the cartographer inked, which is
      a polygon and loses nothing when vectorised, or
  (b) **a rendered/continuous surface** - hillshading, dithering, gradients - where
      the "class" varies inside itself and vectorising turns texture into millions
      of slivers that mean nothing.

This script measures which, class by class, with four numbers that are hard to
argue with:

  purity        share of a class's area that survives a majority filter, i.e. how
                much of it is real area and not speckle
  big_share     share of the class area sitting in components >= 200 px: a flat
                fill is ~1.0, a dithered or shaded surface is ~0
  components    connected components per 1000 px of class area (fragmentation)
  roundtrip     re-render the vectorised result and compare with the classified
                source: the fraction of pixels whose class is preserved

A sheet passes only when the map object is mostly flat fill *and* the round trip
keeps the classes.
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

OUT = pathlib.Path(__file__).parent / "vectorisation_study.json"


def lab(hexes):
    rgb = np.array([[int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)] for h in hexes])
    return rgb2lab(rgb.reshape(1, -1, 3)).reshape(-1, 3)


def classify(img_lab, pal_lab, pal_hex, max_de=26.0, chunk=400_000):
    """Nearest palette entry in CIELAB, with a distance cut for ink/noise.

    Chunked: the full pixel-by-class distance matrix is several GB on the larger
    sheets and the sandbox OOM-kills it.
    """
    shp = img_lab.shape[:2]
    flat = img_lab.reshape(-1, 3)
    idx = np.empty(len(flat), np.int16)
    ok = np.empty(len(flat), bool)
    for a in range(0, len(flat), chunk):
        b = min(a + chunk, len(flat))
        d = np.linalg.norm(flat[a:b, None, :] - pal_lab[None, :, :], axis=2)
        idx[a:b] = d.argmin(1)
        ok[a:b] = d.min(1) <= max_de
    return idx.reshape(shp), ok.reshape(shp), pal_hex


def holdout_colours(img, mask, pal_lab, max_de=8.0, n=6):
    """Colours that carry a lot of area but match no legend swatch.

    If a sheet paints a class that its printed legend does not list, or paints a
    gradient between two classes, it shows up here - and it is exactly what would
    be lost by vectorising to the legend palette.
    """
    px = img[mask]
    if len(px) == 0:
        return []
    q = (px // 8 * 8).astype(np.uint8)
    vals, counts = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    order = np.argsort(-counts)[:400]
    lab = rgb2lab((vals[order] / 255).reshape(1, -1, 3)).reshape(-1, 3)
    d = np.linalg.norm(lab[:, None, :] - pal_lab[None, :, :], axis=2).min(1)  # only 400 rows
    far = d > max_de
    share = counts[order][far].sum() / counts.sum()
    top = [(tuple(int(v) for v in vals[order][i]), int(counts[order][i]))
           for i in np.argsort(-counts[order][far])[:n]]
    return share, top


def study(spec, fit):
    im = G.load_rgb(G.SRC / spec["file"])
    W, H = im.size
    f = min(1.0, 2200 / max(W, H))          # work at a resolution we can reason at
    small = np.asarray(im.resize((int(W * f), int(H * f)), Image.BILINEAR))

    # the country only, using the same plate mask the georeferencing used
    mask = G.plate_mask(small, **spec.get("mask", {}))
    mask = ndimage.binary_erosion(mask, np.ones((2, 2)))

    hexes = [c for c, _ in spec["legend"]]
    pal = lab(hexes)
    img_lab = rgb2lab(small / 255.0)
    cls, ok, _ = classify(img_lab, pal, hexes)
    cls = np.where(ok & mask, cls, -1)

    inside = mask.sum()
    unclassified = float((cls[mask] < 0).mean())
    hold = holdout_colours(small, mask & ok, pal)

    # per class: purity after a 3x3 majority filter, and fragmentation
    med = ndimage.median_filter(np.where(cls < 0, len(hexes), cls), size=3)
    per = []
    for i, (hx, label) in enumerate(spec["legend"]):
        m = cls == i
        n = int(m.sum())
        if n < 200:
            continue
        pure = float(((med == i) & m).sum() / n)
        lab_, nc = ndimage.label(m)
        if nc == 0:
            continue
        sizes = ndimage.sum(m, lab_, range(1, nc + 1))
        big = float(sizes[sizes >= 200].sum() / n)
        per.append(dict(i=i, hex=hx, label=str(label)[:44], px=n,
                        share=round(100 * n / inside, 1), purity=round(pure, 3),
                        big_share=round(big, 3),
                        components=int(nc),
                        comp_per_kpx=round(1000 * nc / n, 2)))
    area = sum(p["px"] for p in per) or 1
    w_pur = sum(p["purity"] * p["px"] for p in per) / area
    w_big = sum(p["big_share"] * p["px"] for p in per) / area
    w_frag = sum(p["comp_per_kpx"] * p["px"] for p in per) / area

    # round trip: keep components >= 60 px (a polygon worth having), re-render,
    # and see how much of the classified map survives
    keep = np.zeros_like(cls, bool)
    for i in range(len(hexes)):
        m = cls == i
        l_, nc = ndimage.label(m)
        if nc:
            sizes = ndimage.sum(m, l_, range(1, nc + 1))
            good = np.isin(l_, np.nonzero(sizes >= 60)[0] + 1)
            keep |= good
    rt = float((keep & ok & mask).sum() / max((ok & mask).sum(), 1))

    out = dict(layer=spec["layer"], px=[W, H], km_per_px=fit["km_per_px_ew"],
               classes=len(hexes),
               unclassified_pct=round(100 * unclassified, 1),
               holdout_share_pct=round(100 * hold[0], 1),
               holdout_top=hold[1],
               purity=round(w_pur, 3), big_share=round(w_big, 3),
               comp_per_kpx=round(w_frag, 2),
               roundtrip=round(rt, 3),
               per_class=per)
    # the verdict
    vector_ok = (w_pur >= 0.90 and w_big >= 0.80 and rt >= 0.80
                 and unclassified <= 0.25 and hold[0] <= 0.15)
    out["vector_ok"] = bool(vector_ok)
    return out


def main():
    fits = {r["layer"]: r for r in
            json.load(open(pathlib.Path(__file__).parent / "raster_georeferencing.json"))}
    res = []
    for spec in G.IMAGES:
        r = study(spec, fits[spec["layer"]])
        res.append(r)
        print(f"{r['layer']:24s} classes {r['classes']:3d}  "
              f"purity {r['purity']:.3f}  big {r['big_share']:.3f}  "
              f"frag {r['comp_per_kpx']:6.1f}/k  rt {r['roundtrip']:.3f}  "
              f"unclass {r['unclassified_pct']:5.1f}%  holdout {r['holdout_share_pct']:5.1f}%  "
              f"-> {'VECTOR' if r['vector_ok'] else 'raster'}")
    json.dump(res, open(OUT, "w"), indent=1)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
