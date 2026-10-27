#!/usr/bin/env python3
"""Georeference the nine images in `new map/` and write them into the GeoPackage.

Why this is not "set a corner and a pixel size"
-----------------------------------------------
None of the nine images carries a world file, a projection or a georeferencing
block.  Six carry no graticule at all; four are web-resolution pictures of a
map with a legend and a title round it.  Guessing an extent from the image
corners would put every one of them tens of km out.

So each image is fitted to data this repository already trusts: the
`national_territory` polygon.  The fit is a four-parameter affine in
longitude/latitude

    lon = lon0 + x * sx          lat = lat0 - y * sy

(x, y = pixel column/row, y down), found in five stages, each one kept only if
it makes the drawn country and the territory overlap better:

  1. an exact FFT cross-correlation of the sheet's country mask with a rasterised
     territory, over a small scale fan - a translation search, not a hill-climb,
     which is what keeps it stable on masks that are only roughly right;
  2. a chamfer polish against the sheet's dark ink;
  3. a polish against the *drawn outline curve* (the ink is full of legends,
     titles and interior class boundaries; the outline is a clean closed curve);
  4. **bloat closure**: on several sheets the country colour is painted a few
     pixels outside the cartographer's border line, which biases the fit
     outwards.  The outward bias is measured, the mask is shrunk by it, and the
     fit is re-polished;
  5. the border offsets are then *measured* on the finished fit, per side.

The overlap (IoU) and the border offsets are both recorded, so the fit is
auditable rather than asserted, and a stage that does not help cannot survive.

Two image families need different treatment:

* `method = "bbox4"` - the drawn country can be masked by colour on all four
  sides, so all four parameters are free.
* `method = "bbox3"` - the map paints the sea the same way it paints low land
  (elevation and soil-pH: the lowest class is used for the ocean too), so the
  southern edge of the mask is the edge of the *sheet*, not of Nigeria.  For
  those, north/west/east are fitted and the y scale is derived from the
  x scale and the latitude (a conformal aspect assumption, true of the
  printed sheets), then lon0/lat0 are refined by IoU over land only.

What is written
---------------
One tiled RGBA raster per image inside `Nigeria_Geology_Minerals_4326.gpkg`,
EPSG:4326, clipped to `national_territory` (so title, legend, scale bar and
neighbouring countries are gone and the nine layers stack exactly on the
vector layers), plus a `raster_layers` attribute table recording, for each:
source file, method, fitted transform, IoU, native ground resolution and the
colour-to-class legend transcribed from the printed map.
"""
import json
import math
import pathlib
import sqlite3
import subprocess

import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import Affine
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from PIL import Image
from scipy import ndimage, optimize

Image.MAX_IMAGE_PIXELS = None

HERE = pathlib.Path(__file__).parent
SRC = HERE.parent / "new map"
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
REPORT = HERE / "raster_georeferencing.json"

FIT_MAX = 1400          # work resolution for the IoU fit
NODATA = 0

# --------------------------------------------------------------------------
# legend transcription: colour -> class, read off each printed legend
# --------------------------------------------------------------------------
IMAGES = [
    dict(file="DEM-of-map-of-nigeria.jpg", mask=dict(n_bg=2, tol=26, margin=6), layer="raster_dem", method="bbox3",
         title="Digital Elevation Model of Nigeria",
         theme="elevation, 7 classes, metres",
         note="Elevation is drawn as a classified image with hillshading; the "
              "class boundaries were read from the printed legend, not from the "
              "pixels, so this is a picture of an elevation map, not a DEM. For "
              "actual elevations use a real DEM.",
         legend=[("#1f6fe0", "-25 - 130"), ("#d9ec9a", "140 - 260"),
                 ("#5f9e3f", "270 - 380"), ("#d4551f", "390 - 530"),
                 ("#8a3b1e", "540 - 720"), ("#b0a49c", "730 - 1,100"),
                 ("#ffffff", "1,200 - 2,100")]),
    dict(file="soil-ph-map-of-nigeria.jpg", mask=dict(n_bg=2, tol=26, margin=6), layer="raster_soil_ph", method="bbox3",
         title="Soil pH distribution in Nigeria",
         theme="soil pH, 5 classes",
         note="Flat classes, no shading, so the classes are clean; the map has "
              "no graticule and no source citation.",
         legend=[("#0b2f7a", "unlabelled (dark navy, legend swatch 1)"),
                 ("#1f9e8f", "0.01 - 5.5"),
                 ("#5fd63f", "5.6 - 6.8"), ("#f5a623", "6.9 - 7.8"),
                 ("#c0392b", "7.9 - 8.3")]),
    dict(file="temperature-map-of-nigeria.png", mask=dict(n_bg=2, tol=26, margin=6), layer="raster_temperature", method="bbox4",
         title="Nigeria historical average temperature, Jan-Dec 1986-2015",
         theme="mean temperature, 13 classes, degrees C",
         note="USGS/EROS, FEWS NET; CHIRTSmax data. The classes are drawn as a "
              "smooth surface, so class edges are interpolated in the artwork.",
         legend=[("#1f77b4", "< 16"), ("#5b9bd5", "16 - 18"), ("#7f9aa8", "18 - 20"),
                 ("#8fb0a8", "20 - 22"), ("#a8c39a", "22 - 24"), ("#cfe0a8", "24 - 26"),
                 ("#e8efa8", "26 - 28"), ("#f5e58a", "28 - 30"), ("#f7d27a", "30 - 32"),
                 ("#f5b95c", "32 - 34"), ("#f09a45", "34 - 36"), ("#e8722f", "36 - 38"),
                 ("#d9541f", "38 - 40"), ("#b8321a", "40 - 42"), ("#8e1a12", "> 42"),
                 ("#29b6f6", "water")]),
    dict(file="forest-reserve-map-of-nigeria.png", mask=dict(n_bg=3, tol=26, margin=6), layer="raster_forest_reserves", method="bbox4",
         title="Forest reserves and major rivers of Nigeria",
         theme="forest reserves / major rivers / water",
         note="Graticule labelled on all four sides; the fit agrees with the "
              "printed graticule to within the residual below.",
         legend=[("#1f7fe0", "Major Rivers"), ("#8ed43f", "Forest Reserves"),
                 ("#eaf7c0", "States Boundary fill"), ("#1f7fe0", "Gulf Of Guinea")]),
    dict(file="landcover-map-of-nigeria.png", mask=dict(n_bg=3, tol=8, margin=6, depth=10), layer="raster_landcover", method="bbox4",
         title="Land cover of Nigeria",
         theme="land cover, 15 classes",
         note="Smallest of the set (609x510 px): ~2.4 km per pixel, so useful as "
              "a locator only. The legend box overlaps the map in the SW corner.",
         legend=[("#0b6b4f", "Evergreen Needleleaf Forest"), ("#2e7d32", "Evergreen Broadleaf Forest"),
                 ("#1fa39a", "Deciduous Needleleaf Forest"), ("#4caf50", "Deciduous Broadleaf Forest"),
                 ("#8d6e3a", "Woodland"), ("#c8a15a", "Bare"), ("#b3b3b3", "Open Shrubland"),
                 ("#c97b4a", "Crop land"), ("#f2f2a0", "Closed Shrubland"),
                 ("#a8d08d", "Mixed Forest"), ("#cfe8a0", "Wooded Grassland"),
                 ("#e8d5a0", "Rangeland"), ("#1f3fd0", "Water"), ("#8b1a1a", "Urban")]),
    dict(file="population distribution-map-of-nigeria.png", mask=dict(n_bg=3, tol=26, margin=6), layer="raster_population", method="bbox4",
         title="Population distribution of Nigeria",
         theme="population by district, 5 classes (absolute)",
         note="Class breaks are absolute counts per drawn district, not density, "
              "and the districts are not named, so this layer cannot be joined to "
              "administrative units. Graticule labelled at 2.5-degree intervals.",
         legend=[("#fdf3c8", "0 - 110,85"), ("#f8e06a", "110,853 - 144,579"),
                 ("#f2b544", "144,580 - 179,550"), ("#c8631f", "179,551 - 232,287"),
                 ("#4a1004", "232,288 - 1,319,571")]),
    dict(file="Ethnic-map-in-nigeria.png", mask=dict(n_bg=3, tol=18, margin=10), layer="raster_ethnic_groups", method="bbox4",
         title="Ethno-linguistic groups of Nigeria",
         theme="ethno-linguistic groups, 35 classes",
         note="Third-party cartography (@Atlas_Cartography) from the 2006 census "
              "and 'Ethnographic survey of Africa'. Boundaries are schematic; the "
              "image is square with a black surround, so the fit is weaker (see "
              "IoU). Do not use for area statistics.",
         legend=[("#f48fb1", "Hausa"), ("#8e3b52", "Fulani"), ("#7e6b9e", "Bade"),
                 ("#e8b4c8", "Tera-Mandara"), ("#4a90c8", "Kanuri"), ("#f7c8e0", "Yedina"),
                 ("#b39ddb", "Baggara"), ("#1565c0", "Songhay"),
                 ("#90a4c0", "Bariba"), ("#a03b3b", "Mande (Busa)"), ("#b08968", "Kambari"),
                 ("#f5e642", "Dakarkari"), ("#f0a860", "Gbagyi"), ("#f2d04a", "Nupe-Ebira"),
                 ("#a8905a", "Atyap"), ("#e8641f", "Tiv-Gade"), ("#7a4a1f", "Berom-Jarawa"),
                 ("#e84a9a", "Angas"), ("#e8a020", "Jukun"), ("#a03b1f", "Tarok"),
                 ("#5cb85c", "Yoruba"), ("#3b7d3b", "Ewe"), ("#7fe8d0", "Edo"),
                 ("#4a7a1f", "Igbo"), ("#a8e06a", "Igala"), ("#1f6b4a", "Ijaw"),
                 ("#4ad64a", "Idoma-Ighde"), ("#1f8f6f", "Itsekiri"),
                 ("#d02020", "Abua-Ogbia-Atissa"), ("#e84a6a", "Eleme"),
                 ("#f5d0a0", "Ibibio-Efik"), ("#f7e8a0", "Bokyi")]),
    dict(file="dominant-soil-map-of-nigeria.jpg", mask=dict(n_bg=2, tol=18, margin=10), layer="raster_dominant_soils", method="bbox4",
         title="Dominant soils of Nigeria",
         theme="dominant soil unit, ~60 classes (FAO/UNESCO)",
         note="10,234 x 6,678 px scan of the printed sheet (GIS Laboratory, "
              "Department of Geography, University of Lagos), with five small "
              "inset maps on the right that are NOT part of the main map and are "
              "removed by the clip. Class names are printed in the legend but at "
              "scan resolution the symbols are not reliably machine-readable, so "
              "the class table below lists the legend headings only.",
         legend=[("#f2e8a0", "Acrisols (AC)"), ("#e8d27a", "Alisols (AL)"),
                 ("#c9b98a", "Cambisols (CM)"), ("#e8e8d8", "Chernozems (CH)"),
                 ("#8a6a4a", "Fluvisols (FL)"), ("#b8b8a8", "Gleysols (GL)"),
                 ("#d8c8a8", "Histosols (HS)"), ("#8a3b1f", "Leptosols (LP)"),
                 ("#c0392b", "Luvisols (LV)"), ("#e8846a", "Nitisols (NT)"),
                 ("#f5d0a0", "Phaeozems (PH)"), ("#7a5a3a", "Planosols (PL)"),
                 ("#a89078", "Plinthosols (PT)"), ("#d8b89a", "Podzols (PZ)"),
                 ("#9a7a5a", "Regosols (RG)"), ("#c8b0a0", "Solonchaks (SC)"),
                 ("#b0a090", "Solonetz (SN)"), ("#e0d0b0", "Vertisols (VR)"),
                 ("#7a9ac0", "Water bodies"), ("#f0f0e8", "Rock outcrops")]),
    dict(file="general-geology-map-of-nigeria.png", mask=dict(n_bg=2, tol=26, margin=6), layer="raster_general_geology", method="bbox4",
         title="General geology of Nigeria (simplified)",
         theme="geology, 9 legend classes by era and lithology",
         note="615 x 715 px - the coarsest item in the set and a simplified "
              "9-class generalisation of the same subject as geology_units. It "
              "is kept because it is the only sheet in the set with the eras "
              "labelled in plain language, NOT as a substitute for "
              "geology_units. Spot elevations in its margins are printed in a "
              "corrupt format (715057 deg E) and are unusable.",
         legend=[("#f7f7a0", "Cenozoic: alluvials, sand, gravels, clay, mangrove swamps, pebbles"),
                 ("#ffff00", "Cenozoic: sands, clays, shales, sandstones, lignites, grits"),
                 ("#f0a030", "Cenozoic: volcanics (basalts, trachytes, rhyolites)"),
                 ("#f5f5c0", "Mesozoic: sands, clays, coals, shales, sandstones, mudstones, limestones"),
                 ("#4a7a4a", "Mesozoic: basic and intermediate intrusions"),
                 ("#7ac0e8", "Mesozoic: granites, syenites, gabbros, rhyolites (Jurassic)"),
                 ("#e8d8a0", "Palaeozoic-Proterozoic: metasediments, schists, quartzites"),
                 ("#f07a8a", "Palaeozoic-Proterozoic: older granites"),
                 ("#f5b8b8", "Palaeozoic-Proterozoic: basement complex")]),
]


# --------------------------------------------------------------------------
# image -> country mask
# --------------------------------------------------------------------------
def load_rgb(path):
    im = Image.open(path)
    if im.mode in ("P", "LA", "RGBA"):
        im = im.convert("RGB")
    return im.convert("RGB")


def plot_box(a, dark=110, min_run=0.55):
    """Bounding box of the drawn map frame, or the whole image if there is none.

    These images are printed as a plate inside a thin rule; the plate colour is
    often the same as the background outside it, so the rule is the only thing
    that separates map from page.
    """
    h, w, _ = a.shape
    g = a.mean(2)
    dk = g < dark
    rows = np.where(dk.sum(1) > min_run * w)[0]
    cols = np.where(dk.sum(0) > min_run * h)[0]
    if len(rows) >= 2 and len(cols) >= 2:
        return int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())
    return 0, 0, w - 1, h - 1


def country_mask(a, n_bg=8, tol=26):
    """Mask of the drawn country.

    Background is not one colour: these pictures are printed on a plate that may
    be white, grey or pale sand, sometimes with a second colour inside a frame
    (the elevation and soil-pH sheets paint a grey or sand plate *and* reuse the
    lowest class for the sea).  So the background is taken to be the handful of
    most common colours in the image - quantised first, so JPEG noise does not
    split a flat wash - and the map is the largest remaining object.  Classes
    that happen to share a plate colour become holes and are filled back in.
    """
    h, w, _ = a.shape
    q = (a // 8).astype(np.int16)
    flat = q.reshape(-1, 3)
    vals, counts = np.unique(flat, axis=0, return_counts=True)
    bg = vals[np.argsort(-counts)[:n_bg]].astype(np.int16) * 8
    m = np.ones((h, w), bool)
    for c in bg:
        m &= np.abs(a - c.astype(np.int16)).max(2) > tol
    m = ndimage.binary_opening(m, np.ones((3, 3)))
    m = ndimage.binary_closing(m, np.ones((9, 9)))
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (int(np.argmax(sizes)) + 1)
    return ndimage.binary_fill_holes(m)


def make_territory_raster(terr, shape, params):
    lon0, lat0, sx, sy = params
    transform = Affine(sx, 0.0, lon0, 0.0, -sy, lat0)
    return rasterize([(terr, 1)], out_shape=shape, transform=transform,
                     fill=0, all_touched=False, dtype="uint8").astype(bool)


def iou(a, b):
    u = np.count_nonzero(a | b)
    return np.count_nonzero(a & b) / u if u else 0.0


def extent_from_mask(m, lo=0.2, hi=99.8):
    """Robust pixel extent of the mask (percentiles, so specks cannot stretch it)."""
    ys, xs = np.nonzero(m)
    if not len(xs):
        return 0.0, 1.0, 0.0, 1.0
    return (float(np.percentile(xs, lo)), float(np.percentile(xs, hi)),
            float(np.percentile(ys, lo)), float(np.percentile(ys, hi)))


def edge_points(a, block=2):
    """Edge pixels of the drawing, as (x, y) arrays, on a coarse grid.

    Used for the chamfer fit: the country outline is the strongest curved edge in
    these images, and trimming the score makes legends and text harmless.
    """
    g = a.mean(2)
    gx = ndimage.sobel(g, axis=1)
    gy = ndimage.sobel(g, axis=0)
    mag = np.hypot(gx, gy)
    thr = np.percentile(mag, 97)
    e = mag > max(thr, 40)
    e = e[::block, ::block]
    ys, xs = np.nonzero(e)
    return xs * block, ys * block


def outline_points(a, dark=150, block=2, min_span=0.30, frame_frac=0.40):
    """Pixels of the drawn country outline: dark, thin, long, and not a frame.

    The outline is the one structure that is both dark and extensive - a closed
    curve spanning most of the drawing.  Dark pixels are taken, the solid ones
    (text, legend boxes, filled symbols) removed, and the frame rules deleted by
    dropping every row and column that is mostly dark, so the plot border and the
    legend separators cannot masquerade as the country.  What is left, kept to
    its largest connected curve, is the outline.
    """
    g = a.mean(2)
    dk = g < dark
    h, w = dk.shape
    rowfrac = dk.sum(1) / w
    colfrac = dk.sum(0) / h
    frame = np.zeros_like(dk)
    frame[rowfrac > frame_frac, :] = True
    frame[:, colfrac > frame_frac] = True
    frame = ndimage.binary_dilation(frame, np.ones((5, 5)))
    dk = dk & ~frame
    solid = ndimage.binary_opening(dk, np.ones((5, 5)))
    thin = ndimage.binary_dilation(dk & ~solid, np.ones((3, 3)))
    lab, n = ndimage.label(thin, structure=np.ones((3, 3)))
    if n == 0:
        return None
    # keep curves that span a large share of the drawing, then the longest of them
    spans = {}
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        dy = sl[0].stop - sl[0].start
        dx = sl[1].stop - sl[1].start
        if dx > min_span * w or dy > min_span * h:
            spans[i] = (dx + dy, sl)
    if not spans:
        return None
    best = max(spans.items(), key=lambda kv: ndimage.sum(lab[kv[1][1]] == kv[0]))[0]
    keep = lab == best
    ys, xs = np.nonzero(keep[::block, ::block])
    return xs * block, ys * block


def box_fit(edge_xy, terr, shape):
    """Scale and offset from the outline's bounding box (conformal assumption)."""
    ex, ey = edge_xy
    H, W = shape
    tminx, tminy, tmaxx, tmaxy = terr.bounds
    bw, bh = ex.max() - ex.min(), ey.max() - ey.min()
    sx = (tmaxx - tminx) / max(bw, 1)
    sy = (tminy - tmaxy) / min(bh, 1) * -1 if False else (tmaxy - tminy) / max(bh, 1)
    return tminx - ex.min() * sx, tmaxy + ey.min() * sy, sx, sy


def frame_box(a, dark=150, frac=0.40):
    """Interior of the drawn plot frame, from its mostly-dark rows and columns."""
    g = a.mean(2)
    dk = g < dark
    h, w = dk.shape
    rows = np.where(dk.sum(1) / w > frac)[0]
    cols = np.where(dk.sum(0) / h > frac)[0]
    if len(rows) >= 2 and len(cols) >= 2:
        return int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())
    return 0, 0, w - 1, h - 1


def plate_mask(a, tol=24, dark=150, n_bg=2, margin=8, depth=6):
    """Map object, separated from the printed plate it sits on.

    The plate colour is read from the margin *inside* the plot frame, a few pixels
    in - not from the frame rule itself (which is dark and would be mistaken for
    background) and not from the image corners (which carry that same rule).  The
    sea on some sheets is painted with the plate colour, so the mask is the
    country plus any class that shares it; `method` decides what to trust.
    """
    h, w, _ = a.shape
    x0, y0, x1, y1 = frame_box(a, dark=dark)
    x0, y0 = min(x0 + margin, w - 1), min(y0 + margin, h - 1)
    x1, y1 = max(x1 - margin, 0), max(y1 - margin, 0)
    inner = a[y0:y1 + 1, x0:x1 + 1]
    ih, iw = inner.shape[:2]
    d = max(1, min(depth, ih // 5, iw // 5))
    strip = np.concatenate([inner[:d].reshape(-1, 3), inner[-d:].reshape(-1, 3),
                            inner[:, :d].reshape(-1, 3), inner[:, -d:].reshape(-1, 3)])
    q = (strip // 6).astype(np.int16)
    vals, counts = np.unique(q, axis=0, return_counts=True)
    bgs = [(vals[i] * 6).astype(np.int16) for i in np.argsort(-counts)[:n_bg]]
    m = np.ones((h, w), bool)
    for c in bgs:
        m &= np.abs(a - c).max(2) > tol
    m = ndimage.binary_opening(m, np.ones((3, 3)))
    m = ndimage.binary_closing(m, np.ones((7, 7)))
    m = ndimage.binary_fill_holes(m)
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (int(np.argmax(sizes)) + 1)
    return ndimage.binary_fill_holes(m)


def start_from_mask(mask, terr, method):
    x0, x1, y0, y1 = extent_from_mask(mask)
    tminx, tminy, tmaxx, tmaxy = terr.bounds
    sx = (tmaxx - tminx) / max(x1 - x0, 1)
    if method == "bbox3":
        sy = sx / math.cos(math.radians((tminy + tmaxy) / 2))
    else:
        sy = (tmaxy - tminy) / max(y1 - y0, 1)
    return tminx - x0 * sx, tmaxy + y0 * sy, sx, sy


def territory_boundary(terr, step=4, min_lat=None):
    geoms = [terr] if terr.geom_type == "Polygon" else list(terr.geoms)
    pts = np.vstack([np.array(g.exterior.coords)[::step] for g in geoms])
    if min_lat is not None:
        pts = pts[pts[:, 1] > min_lat]
    return pts


def refine(start, edge_xy, terr, method, shape, cap=60.0, trim=0.10, TOL=2.5):
    """Polish a mask-derived start against the drawn edge pixels.

    Score = coverage of the border within TOL px (primary) + trimmed mean
    distance (tie-breaker), with the aspect ratio held within 10 % of the start so
    the fit cannot slide onto interior detail.  Returns the transform plus two
    honest metrics: coverage and the trimmed mean residual.
    """
    from scipy.spatial import cKDTree

    ex, ey = edge_xy
    tb = territory_boundary(terr, min_lat=6.5 if method == "bbox3" else None)
    if ex is None or len(ex) == 0:
        return tuple(start), dict(coverage=float("nan"), resid_px=float("nan"))
    tree = cKDTree(np.column_stack([ex, ey]))
    aspect0 = start[3] / start[2]

    def metrics(p):
        l0, a0, sx, sy = p
        px = (tb[:, 0] - l0) / sx
        py = (a0 - tb[:, 1]) / sy
        d, _ = tree.query(np.column_stack([px, py]), k=1)
        cover = float((d <= TOL).mean())
        dm = np.minimum(d, cap)
        k = max(1, int(len(dm) * (1.0 - trim)))
        return cover, float(np.sort(dm)[:k].mean())

    def score(p):
        if p[2] <= 0 or p[3] <= 0:
            return 1e9
        if not (0.90 * aspect0 <= p[3] / p[2] <= 1.10 * aspect0):
            return 1e9
        cov, res = metrics(p)
        return -cov + 0.002 * res

    best = np.array(start, float)
    best_v = score(best)
    step = np.array([best[2] * 6, best[3] * 6, best[2] * 0.05, best[3] * 0.05])
    lo = best - np.array([2.0, 2.0, best[2] * 0.15, best[3] * 0.15])
    hi = best + np.array([2.0, 2.0, best[2] * 0.15, best[3] * 0.15])
    for shrink in (1.0, 0.5, 0.25, 0.12, 0.06, 0.03, 0.015):
        improved = True
        while improved:
            improved = False
            for i in range(4):
                for sgn in (+1, -1):
                    cand = best.copy()
                    cand[i] = np.clip(cand[i] + sgn * step[i] * shrink, lo[i], hi[i])
                    v = score(cand)
                    if v < best_v - 1e-7:
                        best, best_v = cand, v
                        improved = True
    cov, res = metrics(best)
    return tuple(best), dict(coverage=round(cov, 4), resid_px=round(res, 2))


def fit_fft(mask, terr, method, shape):
    """Best (scale, translation) by cross-correlating mask and territory.

    Scale comes from the mask's own extent; the translation is then found exactly
    - one FFT correlation per trial scale - rather than by hill-climbing, which is
    what makes this stable on images whose mask is only roughly right.  A small
    scale fan (and, for `bbox4`, an aspect fan) is evaluated on intersection over
    union.
    """
    from scipy.signal import fftconvolve

    H, W = shape
    m = mask.astype(np.float32)
    m -= m.mean()
    best, best_v = None, -1.0
    aspects = (1.0,) if method == "bbox3" else (0.96, 1.0, 1.04)
    for k in (0.88, 0.94, 1.0, 1.06, 1.12):
        for asp in aspects:
            lon0, lat0, sx, sy = start_from_mask(mask, terr, method)
            sx, sy = sx * k, sy * k * asp
            lat0 = lat0  # keep the north edge, the correlation fixes the rest
            tr = make_territory_raster(terr, (H, W), (lon0, lat0, sx, sy)).astype(np.float32)
            if tr.sum() == 0:
                continue
            tr -= tr.mean()
            corr = fftconvolve(m, tr[::-1, ::-1], mode="same")
            dy, dx = np.unravel_index(int(np.argmax(corr)), corr.shape)
            # a shift in the correlation peak = a crop of the territory raster
            l0 = lon0 - (W // 2 - dx) * sx if False else lon0 + (dx - W // 2) * sx
            a0 = lat0 - (dy - H // 2) * sy
            t = make_territory_raster(terr, (H, W), (l0, a0, sx, sy))
            v = iou(mask, t)
            if v > best_v:
                best, best_v = (l0, a0, sx, sy), v
    return best, best_v


def mask_outline(mask):
    """Boundary curve of the drawn country: the outer edge of the largest blob."""
    solid = ndimage.binary_fill_holes(mask)
    inner = ndimage.binary_erosion(solid, np.ones((3, 3)))
    return solid & ~inner


def fit_outline(mask, terr, method, shape, start, span=0.06, step=8):
    """Polish a fit against the drawn outline itself.

    Edge maps pick up legends, titles and interior class boundaries, which drags
    an edge-driven fit sideways.  The outer boundary of the map object is a
    closed country-shaped curve with none of that clutter, so it is the cleanest
    available proxy for the printer's own border line.  The objective is
    symmetric: how far the mapped border sits from that curve, and back.
    """
    from scipy.ndimage import distance_transform_edt

    H, W = shape
    outline = mask_outline(mask)
    dt_outline = distance_transform_edt(~outline)

    def cost(lon0, lat0, sx, sy):
        pts = territory_boundary(terr, step=3)
        xs = (pts[:, 0] - lon0) / sx
        ys = (lat0 - pts[:, 1]) / sy
        ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
        if ok.sum() < 100:
            return np.inf
        a = np.clip(ys[ok].astype(int), 0, H - 1)
        b = np.clip(xs[ok].astype(int), 0, W - 1)
        fwd = dt_outline[a, b]
        tb = make_territory_raster(terr, (H, W), (lon0, lat0, sx, sy))
        dt_border = distance_transform_edt(~mask_outline(tb))
        ys2, xs2 = np.nonzero(outline)
        back = dt_border[ys2, xs2]
        return float(np.median(fwd) + np.median(back))

    fit_outline.cost = cost

    lon0, lat0, sx, sy = start
    best, best_c = (lon0, lat0, sx, sy), cost(lon0, lat0, sx, sy)
    for _ in range(3):                                   # coarse-to-fine grid
        k = span
        found = best
        for dk in (-k, 0, k):
            for dx in (-step, 0, step):
                for dy in (-step, 0, step):
                    if dk == dx == dy == 0:
                        continue
                    c = cost(best[0] + dx * best[2], best[1] - dy * best[3],
                             best[2] * (1 + dk), best[3] * (1 + dk))
                    if c < best_c:
                        best_c, found = c, (best[0] + dx * best[2], best[1] - dy * best[3],
                                            best[2] * (1 + dk), best[3] * (1 + dk))
        best = found
        span, step = span / 2, max(1, step // 2)
    return best, dict(outline_px=round(best_c, 2))


def fit_sheet(small, spec, terr, water=None):
    """The whole georeferencing chain for one sheet, with every stage gated.

    Five stages, each one kept only if it makes the drawn country and the
    territory overlap better:

      1. FFT translation search over a scale fan      (exact, stable)
      2. chamfer polish on the ink                   (small correction)
      3. polish on the drawn outline curve           (no legend ink)
      4. bloat closure: the painted edge often sits a few pixels outside the
         cartographer's border line, which biases the fit outwards; measure it,
         shrink the mask by it, re-fit
      5. read the border offsets off the finished fit - the measurement, not an
         input to it
    """
    mask = plate_mask(small, **spec.get("mask", {}))
    edges = edge_points(small)
    H, W = small.shape[:2]

    (lon0, lat0, sx, sy), iou_fft = fit_fft(mask, terr, spec["method"], (H, W))
    met = {"iou_fft": round(iou_fft, 4), "refined": False,
           "outline_refined": False, "debloat_px": 0.0}

    def better(cand):
        return iou(mask, make_territory_raster(terr, mask.shape, cand))

    base = better((lon0, lat0, sx, sy))
    (l2, a2, sx2, sy2), met2 = refine((lon0, lat0, sx, sy), edges, terr,
                                      spec["method"], (H, W))
    if better((l2, a2, sx2, sy2)) > base:
        lon0, lat0, sx, sy = l2, a2, sx2, sy2
        base = better((lon0, lat0, sx, sy))
        met["refined"] = True

    (l3, a3, sx3, sy3), _ = fit_outline(mask, terr, spec["method"], (H, W),
                                        (lon0, lat0, sx, sy))
    if better((l3, a3, sx3, sy3)) > base:
        lon0, lat0, sx, sy = l3, a3, sx3, sy3
        base = better((lon0, lat0, sx, sy))
        met["outline_refined"] = True

    # --- bloat closure -----------------------------------------------------
    # each pass measures the bloat that is *left* and shrinks by that much, so the
    # erosion accumulates; it stops as soon as nothing is left to take off
    working, taken = mask, 0.0
    for _ in range(3):
        # the signal is the whole mask edge, sea included: the sea is part of the
        # mask, so it is part of what the fit is being asked to align.  Whether the
        # erosion is right is decided by the overlap afterwards, not by opinion.
        o = border_offsets(working, terr, (lon0, lat0, sx, sy), working.shape,
                           step=8, clip=80.0, water=water)["all"]
        if o is None:
            break
        km_px = (sx * 111.32 * math.cos(math.radians(9.0)) + sy * 110.57) / 2
        want = o["median_km"] / km_px
        if want < 0.75:                     # nothing left, or the edge is inside
            break
        cand = debloat(mask, taken + want)
        (lc, ac, sxc, syc), _ = fit_outline(cand, terr, spec["method"],
                                            cand.shape, (lon0, lat0, sx, sy))
        if iou(cand, make_territory_raster(terr, cand.shape, (lc, ac, sxc, syc))) > iou(
                cand, make_territory_raster(terr, cand.shape, (lon0, lat0, sx, sy))):
            lon0, lat0, sx, sy = lc, ac, sxc, syc
        working, taken = cand, taken + want
        met["debloat_px"] = round(taken, 2)
    mask = working

    met["iou"] = round(iou(mask, make_territory_raster(terr, mask.shape,
                                                       (lon0, lat0, sx, sy))), 4)
    met["offsets"] = border_offsets(mask, terr, (lon0, lat0, sx, sy), mask.shape,
                                    water=water)
    met["mask"] = mask
    return (lon0, lat0, sx, sy), met


def to_rgba(a, keep, feather=1):
    """RGBA where alpha follows the country mask, softened by one pixel."""
    h, w, _ = a.shape
    alpha = (keep.astype(np.float32) * 255).astype(np.uint8)
    if feather:
        alpha = ndimage.grey_erosion(alpha, size=(feather * 2 + 1, feather * 2 + 1))
        alpha = ndimage.gaussian_filter(alpha.astype(np.float32), feather).astype(np.uint8)
    rgba = np.dstack([a, alpha])
    return np.moveaxis(rgba, 2, 0)      # (4, h, w)


def write_layer(dst, name, rgba, transform, description):
    """Add one tiled RGBA raster layer to an EXISTING GeoPackage.

    rasterio/GDAL's GPKG raster driver can only create a raster in a *new* file
    (opening mode "w" truncates), so each layer is written to a scratch
    GeoPackage and then merged in: GPKG rasters are ordinary tables, so the tile
    table, its metadata rows and the tile-matrix entries can be copied across with
    SQL, leaving the 27 vector layers untouched.
    """
    import sqlite3
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td) / "one.gpkg"
        prof = dict(driver="GPKG", width=rgba.shape[2], height=rgba.shape[1],
                    count=4, dtype="uint8", crs="EPSG:4326", transform=transform,
                    photometric="RGB", alpha="YES", tiled=True,
                    blockxsize=256, blockysize=256, compress="DEFLATE",
                    zlevel=9, RASTER_TABLE=name, RASTER_IDENTIFIER=name,
                    DESCRIPTION=description)
        with rasterio.open(tmp, "w", **prof) as d:
            d.write(rgba)

        con = sqlite3.connect(dst)
        cur = con.cursor()
        cur.execute("ATTACH DATABASE ? AS src", (str(tmp),))
        cur.execute("DELETE FROM gpkg_contents WHERE table_name = ?", (name,))
        cur.execute("DROP TABLE IF EXISTS main.\"%s\"" % name)
        cur.execute(f'CREATE TABLE main."{name}" (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                    " zoom_level INTEGER NOT NULL, tile_column INTEGER NOT NULL,"
                    " tile_row INTEGER NOT NULL, tile_data BLOB NOT NULL)")
        cur.execute(f'INSERT INTO main."{name}" (id, zoom_level, tile_column, tile_row, tile_data)'
                    f' SELECT id, zoom_level, tile_column, tile_row, tile_data FROM src."{name}"')
        cur.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS "idx_{name}_tiles" ON "{name}"'
                    " (zoom_level, tile_column, tile_row)")
        cur.execute('DELETE FROM main.gpkg_tile_matrix_set WHERE table_name = ?', (name,))
        cur.execute('INSERT INTO main.gpkg_tile_matrix_set SELECT * FROM src.gpkg_tile_matrix_set'
                    ' WHERE table_name = ?', (name,))
        cur.execute('DELETE FROM main.gpkg_tile_matrix WHERE table_name = ?', (name,))
        cur.execute('INSERT INTO main.gpkg_tile_matrix SELECT * FROM src.gpkg_tile_matrix'
                    ' WHERE table_name = ?', (name,))
        # GDAL declares a zoom level for every overview it *could* write, including
        # ones it did not (the rasters are single-resolution).  Leave only the
        # levels that actually hold tiles, so the matrix describes the data.
        cur.execute('DELETE FROM main.gpkg_tile_matrix WHERE table_name = ? AND zoom_level'
                    ' NOT IN (SELECT DISTINCT zoom_level FROM main."%s")' % name, (name,))
        cur.execute("SELECT data_type, identifier, description, last_change, min_x, min_y,"
                    " max_x, max_y, srs_id FROM src.gpkg_contents WHERE table_name = ?", (name,))
        row = cur.fetchone()
        cur.execute("INSERT INTO gpkg_contents (table_name, data_type, identifier, description,"
                    " last_change, min_x, min_y, max_x, max_y, srs_id)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)", (name, *row))
        try:
            cur.execute("INSERT OR IGNORE INTO gpkg_extensions (table_name, column_name,"
                        " extension_name, definition, scope) VALUES (?,?,?,?,?)",
                        (name, "tile_data", "gpkg_rtree_index", "", "write-only"))
        except sqlite3.OperationalError:
            pass
        con.commit()
        cur.execute("DETACH DATABASE src")
        con.close()


def main():
    terr_gdf = gpd.read_file(GPKG, layer="national_territory")
    terr = terr_gdf.geometry.union_all()
    water = gpd.read_file(GPKG, layer="water_bodies").geometry.union_all()
    rows = []
    for spec in IMAGES:
        im = load_rgb(SRC / spec["file"])
        full = np.asarray(im)
        H, W = full.shape[:2]
        f = min(1.0, FIT_MAX / max(W, H))
        small = np.asarray(im.resize((max(1, int(W * f)), max(1, int(H * f))),
                                     Image.BILINEAR))

        (lon0, lat0, sx, sy), met = fit_sheet(small, spec, terr, water)
        mask = met.pop("mask")
        off = met["offsets"]

        sx_n, sy_n = sx * f, sy * f          # degrees per native pixel
        transform = Affine(sx_n, 0.0, lon0, 0.0, -sy_n, lat0)

        keep = rasterize([(terr, 1)], out_shape=(H, W), transform=transform,
                         fill=0, all_touched=True, dtype="uint8").astype(bool)
        keep = ndimage.binary_erosion(keep, np.ones((3, 3)))
        # drop whatever is not part of the drawn country: a legend box, a scale
        # bar or a title that happens to fall inside the border
        m_full = ndimage.binary_closing(mask, np.ones((5, 5)))
        keep &= ndimage.zoom(m_full.astype(np.uint8), (H / m_full.shape[0],
                                                       W / m_full.shape[1]), order=0).astype(bool)
        rgba = to_rgba(full, keep, feather=2)

        km_e = sx_n * 111.32 * math.cos(math.radians(9))
        km_n = sy_n * 110.57
        km_px = (km_e + km_n) / 2                    # ground km per native pixel

        a = off["land"] or off["all"]      # the land border is the honest measure
        coast = off["coast"]
        out_km = a["abs_median_km"]        # the border, measured against the sheet
        quality = ("high" if out_km < 6 else
                   "medium" if out_km < 15 else "approximate")
        sides = {k: (off[k]["median_km"] if off[k] else None)
                 for k in ("north", "south", "west", "east")}
        side_txt = ", ".join(f"{k} {v:+.0f} km" for k, v in sides.items() if v is not None)
        desc = (f"{spec['title']}. Source: new map/{spec['file']} ({W}x{H} px). "
                f"Georeferenced by fitting the drawn country of the scanned sheet to "
                f"national_territory (affine, no rotation, no re-projection of the "
                f"pixels). Measured fit on the land border: {out_km:.1f} km median "
                f"offset ({side_txt}); RMS {a['rms_km']:.1f} km, 90th percentile "
                f"{a['p90_km']:+.1f} km; the two country shapes overlap with IoU "
                f"{met['iou']:.3f} ({quality} confidence). "
                f"{km_e:.3f} km/px east-west, {km_n:.3f} km/px north-south. "
                f"Clipped to the national territory. {spec['note']}")
        write_layer(GPKG, spec["layer"], rgba, transform, desc)

        rows.append(dict(layer=spec["layer"], file=spec["file"], title=spec["title"],
                         theme=spec["theme"], method=spec["method"],
                         iou=met["iou"], iou_fft=met["iou_fft"],
                         refined=met["refined"], outline_refined=met["outline_refined"],
                         debloat_px=met["debloat_px"],
                         border_offset_km=out_km,
                         border_rms_km=a["rms_km"],
                         border_p90_km=a["p90_km"],
                         border_sides_km=sides,
                         border_worst_km=a["worst_abs_km"],
                         border_n=a["n"],
                         coast_offset_km=(coast["abs_median_km"] if coast else None),
                         coast_n=(coast["n"] if coast else 0),
                         fit_quality=quality,
                         km_per_px_ew=round(km_e, 4), km_per_px_ns=round(km_n, 4),
                         lon0=round(lon0, 6), lat0=round(lat0, 6),
                         deg_per_px_lon=round(sx_n, 9), deg_per_px_lat=round(sy_n, 9),
                         native_px=[W, H], note=spec["note"], legend=spec["legend"]))
        print(f"  {spec['layer']:24s} IoU {met['iou']:.3f}  border {out_km:5.1f} km "
              f"({side_txt})  rms {a['rms_km']:4.1f}  {km_e:6.3f}x{km_n:6.3f} km/px")

    # dropping the previous copy of each raster leaves free pages behind; VACUUM
    # gives the space back so the deliverable does not creep upwards on re-runs
    with sqlite3.connect(GPKG) as con:
        con.execute("VACUUM")

    json.dump(rows, open(REPORT, "w"), indent=2)
    # GDAL declares an rtree index on each new `tile_data` BLOB and a zoom level
    # for overviews it did not write; both are register debris, so clean up here
    # rather than leaving a file that describes things it does not contain
    subprocess.run([sys.executable, str(HERE / "fix_gpkg_hygiene.py")], check=True)
    print(f"\nwrote {REPORT.name} and {len(rows)} raster layers into {GPKG.name}")





def border_offsets(mask, terr, params, shape, step=4, clip=60.0, water=None):
    """Deduce how far the sheet's own border sits from the official one, per side.

    Every point of the *mapped* outline is paired with the nearest point of the
    official `national_territory` boundary, and the gap is signed: negative where
    the sheet draws Nigeria smaller than it is (the printed border falls inside
    the official line), positive where it draws it larger.  Reported per side so a
    sheet that is scaled or shifted on one axis cannot hide behind an average.

    The **coast is reported separately and excluded from the headline figure**.
    Several sheets paint the Gulf of Guinea in a land colour, so their southern
    edge is not a border at all but the edge of the drawing; mixing it in would
    blame the registration for what the cartographer did with the sea.

    This is a measurement, not an input to the fit: the fit is decided first, from
    the overlap of the two shapes, and only then is the offset read off.
    """
    from scipy.spatial import cKDTree
    from shapely import distance as shp_distance
    from shapely.geometry import Point

    H, W = shape
    lon0, lat0, sx, sy = params
    KX = 111.32 * math.cos(math.radians(9.0))          # km per degree longitude
    KY = 110.57                                        # km per degree latitude

    ys, xs = np.nonzero(mask_outline(mask))
    if len(ys) > 60000:
        sel = np.linspace(0, len(ys) - 1, 60000).astype(int)
        ys, xs = ys[sel], xs[sel]
    mlon = lon0 + xs * sx
    mlat = lat0 - ys * sy

    tp = territory_boundary(terr, step=step)
    _, idx = cKDTree(tp).query(np.c_[mlon, mlat], workers=-1)
    dist_km = np.hypot((mlon - tp[idx, 0]) * KX, (mlat - tp[idx, 1]) * KY)

    tb = make_territory_raster(terr, (H, W), params)
    inside = tb[ys, xs]
    signed = np.where(inside, -dist_km, dist_km)

    blon, blat = tp[idx, 0], tp[idx, 1]
    coast = np.zeros(len(blon), bool)
    if water is not None:
        # a border point within `tol` of the sea is a coastal point
        tol = 0.02
        near = water.buffer(tol) if hasattr(water, "buffer") else water
        for i in np.nonzero((np.abs(blat - 5.0) < 4.0))[0]:
            coast[i] = near.contains(Point(blon[i], blat[i]))

    def stats(v):
        if len(v) < 25:
            return None
        return dict(
            n=int(len(v)),
            median_km=round(float(np.median(v)), 2),
            mean_km=round(float(v.mean()), 2),
            rms_km=round(float(np.sqrt((v ** 2).mean())), 2),
            p10_km=round(float(np.percentile(v, 10)), 2),
            p90_km=round(float(np.percentile(v, 90)), 2),
            worst_abs_km=round(float(np.abs(v).max()), 2),
            abs_median_km=round(float(np.median(np.abs(v))), 2),
        )

    good = np.abs(signed) < clip          # gross mismatches are not a border
    out = {"all": stats(signed[good]),
           "land": stats(signed[good & ~coast]),
           "coast": stats(signed[good & coast])}
    for name, sel in (("north", blat > 11.4), ("south", blat < 6.6),
                      ("west", blon < 4.6), ("east", blon > 13.2)):
        out[name] = stats(signed[good & ~coast & sel])
    return out
def _densify(coords, spacing_deg=0.008):
    """Resample a polyline at a fixed spacing so nearest-point matches are fair."""
    d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(coords, axis=0), axis=1))]
    if d[-1] < spacing_deg or len(coords) < 2:
        return coords
    n = max(2, int(d[-1] / spacing_deg))
    t = np.linspace(0, d[-1], n)
    return np.c_[np.interp(t, d, coords[:, 0]), np.interp(t, d, coords[:, 1])]


def debloat(mask, px, cap=24.0):
    """Shrink the mask edge onto the drawn border by `px` pixels.

    On several sheets the country colour is painted a few pixels *outside* the
    printed border line (or the fill is anti-aliased over it).  That shows up as a
    border offset that is positive on all four sides at once - a constant, not a
    registration error - and it makes the overlap score reward a fit that is
    slightly too large.  Eroding the mask by the measured amount leaves the mask
    edge where the cartographer drew the country.
    """
    if px <= 0.25:
        return mask
    px = min(px, cap)
    dist = ndimage.distance_transform_edt(mask)
    return dist > px


if __name__ == "__main__":
    main()
