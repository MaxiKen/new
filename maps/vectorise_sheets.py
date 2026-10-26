#!/usr/bin/env python3
"""EXPLORATORY: vectorise all nine sheets and measure what survives.

Superseded as the shipping step by `build_vector_layers.py`, which writes only the
two sheets that pass.  This one stays as the evidence generator: it converts every
sheet so the comparison is empirical, and writes the candidates to a scratch
GeoPackage (/tmp/vectorisation_candidates.gpkg), never into the deliverable.

Note on the "holdout" idea in the earlier study: it compared the painted colours
with the legend hexes transcribed by eye into IMAGES, which turned out to be up to
dE 100 wrong.  That made every sheet look textured.  `read_legend_swatches.py` now
measures the printed swatches, and that measurement is what the shipped layers use.

Original note follows.

Vectorise the class maps whose classes are real areas, and measure the result.

A printed class map is flat fill with inked boundaries: its classes *are* polygons
and shipping them as polygons is strictly better - you can query, join, dissolve
and symbolise them, and the file is smaller.  A rendered surface (hillshading,
dithering) is not: there the class varies inside itself and polygonising turns
texture into slivers.

This script does the conversion for every sheet and lets the numbers decide:

  * the palette is measured from the sheet (k-means in CIELAB, k = number of
    printed classes), because the hexes previously transcribed into IMAGES were
    approximations - up to dE 30 away from the ink actually on the page
  * speckle is removed with a majority filter, which for a printed map is noise
    removal, not generalisation: JPEG artefacts and anti-aliased label text are
    not cartography
  * components below `min_km2` are dropped as slivers
  * the result is re-rendered and compared with the classified source

A sheet is written as a vector layer only if its round trip survives; otherwise
the raster stays the product and the numbers say why.
"""
import json
import pathlib
import sys

import numpy as np
import geopandas as gpd
import pyogrio
from PIL import Image
from scipy import ndimage
from shapely.geometry import shape
from skimage.color import rgb2lab, lab2rgb

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import georef_new_map as G  # noqa: E402

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
# candidates go to a scratch file: this script writes *all nine* sheets to see
# what survives, and only two of them are good enough to ship
OUT_GPKG = pathlib.Path("/tmp/vectorisation_candidates.gpkg")
REPORT = HERE / "vectorisation_report.json"

# per sheet: work resolution, smoothing, and the smallest polygon worth keeping
PLAN = {
    "raster_temperature":    dict(maxpx=2000, smooth=2, min_km2=2.0),
    "raster_forest_reserves": dict(maxpx=3000, smooth=1, min_km2=1.0),
    "raster_population":     dict(maxpx=2000, smooth=2, min_km2=2.0),
    "raster_landcover":      dict(maxpx=2000, smooth=2, min_km2=4.0),
    "raster_general_geology": dict(maxpx=2000, smooth=2, min_km2=2.0),
    "raster_ethnic_groups":  dict(maxpx=2000, smooth=2, min_km2=2.0),
    "raster_soil_ph":        dict(maxpx=2400, smooth=2, min_km2=2.0),
    "raster_dem":            dict(maxpx=2400, smooth=2, min_km2=2.0),
    "raster_dominant_soils": dict(maxpx=2400, smooth=2, min_km2=1.0),
}


def kmeans_palette(lab_px, k, iters=25, seed=0):
    """k dominant colours, in LAB, weighted by area."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(lab_px), size=min(len(lab_px), 200_000), replace=False)
    x = lab_px[idx]
    # k-means++ style seeding
    cen = [x[rng.integers(len(x))]]
    for _ in range(k - 1):
        d = np.min(np.linalg.norm(x[:, None, :] - np.array(cen)[None, :, :], axis=2), 1)
        p = d ** 2
        if not np.isfinite(p).all() or p.sum() <= 0:      # duplicate seeds
            cen.append(x[rng.integers(len(x))])
            continue
        cen.append(x[rng.choice(len(x), p=p / p.sum())])
    cen = np.array(cen)
    for _ in range(iters):
        d = np.linalg.norm(x[:, None, :] - cen[None, :, :], axis=2)
        a = d.argmin(1)
        for j in range(k):
            m = a == j
            if m.any():
                cen[j] = x[m].mean(0)
    # order by area, so class order is stable and readable (chunked: the full
    # matrix is 1.4 GB on the 10,000-px soils scan)
    cnt = np.zeros(k, int)
    for a0 in range(0, len(lab_px), 500_000):
        b0 = min(a0 + 500_000, len(lab_px))
        d = np.linalg.norm(lab_px[a0:b0, None, :] - cen[None, :, :], axis=2)
        cnt += np.bincount(d.argmin(1), minlength=k)
    order = np.argsort(-cnt)
    return cen[order], cnt[order] / len(lab_px)


def vectorise(spec, fit, plan):
    im = G.load_rgb(G.SRC / spec["file"])
    W, H = im.size
    f = min(1.0, plan["maxpx"] / max(W, H))
    small = np.asarray(im.resize((max(1, int(W * f)), max(1, int(H * f))), Image.BILINEAR))
    mask = ndimage.binary_erosion(G.plate_mask(small, **spec.get("mask", {})), np.ones((2, 2)))
    h, w = mask.shape

    km_px = fit["km_per_px_ew"] / f
    lat0, lon0 = fit["lat0"], fit["lon0"]
    sy = fit["deg_per_px_lat"] / f
    sx = fit["deg_per_px_lon"] / f

    img_lab = rgb2lab(small / 255.0)
    k = len(spec["legend"])
    cen, share = kmeans_palette(img_lab[mask], k, seed=k)

    # assign, then clean: a printed class boundary is hundreds of pixels long,
    # so a 1-pixel speckle is print noise, not a class
    # chunked: the full pixel-by-class matrix is ~1 GB on the larger sheets
    flat = img_lab.reshape(-1, 3)
    cls = np.empty(len(flat), np.int16)
    far = np.empty(len(flat), bool)
    for a in range(0, len(flat), 500_000):
        b = min(a + 500_000, len(flat))
        d = np.linalg.norm(flat[a:b, None, :] - cen[None, :, :], axis=2)
        cls[a:b] = d.argmin(1)
        far[a:b] = d.min(1) > 30.0               # ink, text, paper edge
    cls = cls.reshape(h, w)
    far = far.reshape(h, w)
    cls = np.where(mask & ~far, cls, -1)
    for _ in range(plan["smooth"]):
        med = ndimage.median_filter(np.where(cls < 0, k, cls), size=3)
        cls = np.where(med < k, med, -1)
        cls = np.where(mask, cls, -1)

    # sliver removal, per class, in km²
    px_km2 = km_px ** 2
    # a polygon smaller than ~5 px a side is print noise, not a class area; without
    # this floor the hillshaded sheets polygonise into millions of slivers
    min_px = max(24, plan["min_km2"] / px_km2)
    for i in range(k):
        m = cls == i
        l_, nc = ndimage.label(m)
        if not nc:
            continue
        sizes = ndimage.sum(m, l_, range(1, nc + 1))
        drop = np.isin(l_, np.nonzero(sizes < min_px)[0] + 1)
        cls[drop] = -1

    # round trip
    rt = float((cls >= 0).sum() / max(mask.sum(), 1))

    from rasterio.features import shapes
    from rasterio.transform import Affine
    tr = Affine(sx, 0, lon0, 0, -sy, lat0)
    # match each measured cluster to a printed legend label **by colour**, never
    # by order: the biggest area is not the first row of the legend
    legend_lab = rgb2lab(np.array([[
        [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)] for h, _ in spec["legend"]]]))
    legend_lab = legend_lab.reshape(-1, 3)
    pairs = sorted(((float(np.linalg.norm(cen[i] - legend_lab[j])), i, j)
                    for i in range(k) for j in range(len(legend_lab))))
    lab_of, used = {}, set()
    for dE, i, j in pairs:                       # greedy, one label per cluster
        if i in lab_of or j in used:
            continue
        lab_of[i] = (j, dE)
        used.add(j)

    recs = []
    for geom, val in shapes(cls.astype(np.int32), mask=(cls >= 0), transform=tr):
        i = int(val)
        recs.append((i, shape(geom)))
    # clip to the country: the plate mask includes painted sea and paper margins,
    # so the raw polygons overrun the border (a 930,000 km2 "Nigeria")
    terr = gpd.read_file(GPKG, layer="national_territory").geometry.union_all()
    polys, keep = [], []
    for i, g in recs:
        c = g.intersection(terr)
        if not c.is_empty and c.area > 1e-9:
            polys.append(c)
            keep.append(i)
    rows = []
    for i in keep:
        j, dE = lab_of.get(i, (None, None))
        rows.append(dict(
            cls=i,
            class_name=str(spec["legend"][j][1]) if j is not None else "",
            legend_hex=spec["legend"][j][0] if j is not None else "",
            colour_dE=None if dE is None else round(dE, 1)))
    gdf = gpd.GeoDataFrame(rows, geometry=polys, crs="EPSG:4326")
    gdf["area_km2"] = (gdf.to_crs("EPSG:6933").area / 1e6).round(4)
    hexes = ["#%02x%02x%02x" % tuple(
        int(round(v * 255)) for v in lab2rgb(c.reshape(1, 1, 3)).reshape(3)) for c in cen]
    dEs = [v[1] for v in lab_of.values()]
    return gdf, dict(k=k, km_px=round(km_px, 3), roundtrip=round(rt, 3),
                     polygons=int(len(gdf)),
                     palette_hex=hexes,
                     labels_matched=len(lab_of),
                     label_dE_median=round(float(np.median(dEs)), 1) if dEs else None,
                     label_dE_max=round(float(np.max(dEs)), 1) if dEs else None,
                     colour_to_label={hexes[i]: (spec["legend"][j][1], round(d, 1))
                                      for i, (j, d) in lab_of.items()})


def main():
    fits = {r["layer"]: r for r in json.load(open(HERE / "raster_georeferencing.json"))}
    out = []
    for spec in G.IMAGES:
        name = spec["layer"]
        plan = PLAN[name]
        gdf, met = vectorise(spec, fits[name], plan)
        verts = int(sum(len(g.exterior.coords) for g in gdf.geometry if g.geom_type == "Polygon")
                    + sum(len(p.exterior.coords) for g in gdf.geometry if g.geom_type == "MultiPolygon"
                          for p in g.geoms))
        met.update(layer=name.replace("raster_", "poly_"),
                   source_layer=name, vertices=verts,
                   area_km2=round(float(gdf.area_km2.sum()), 1))
        out.append(met)
        print(f"{name:24s} k={met['k']:2d} {met['km_px']:5.2f} km/px  "
              f"{met['polygons']:6d} polygons {met['vertices']:7d} vertices  "
              f"area {met['area_km2']:6.0f} km2  rt {met['roundtrip']:.3f}", flush=True)
        gdf.to_file(OUT_GPKG, layer=met["layer"], driver="GPKG")
        del gdf
        import gc; gc.collect()
    json.dump(out, open(REPORT, "w"), indent=1)
    print(f"\nwrote {len(out)} candidate vector layers into {OUT_GPKG.name} "
          f"for inspection -> {REPORT.name}")
    print("  the shipped layers are written by build_vector_layers.py")


if __name__ == "__main__":
    main()
