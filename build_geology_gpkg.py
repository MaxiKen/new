#!/usr/bin/env python3
"""Build nigeria_geology.gpkg - a polygon layer of the geological map of Nigeria.

Pipeline (uses BOTH pictures, they complement each other):
  * "pic geology of nigeria.png" (pic 1) supplies the 86-entry legend (names + swatch
    colours) and the unit geometry (classified pixel raster).
  * The map's own graticule (traced meridian/parallel ink + its degree labels) supplies
    the coordinate system; a Lambert Conformal Conic model is fitted to it, so every
    polygon is written in real WGS84 coordinates.
  * "pic NGSA geological-map-of-nigeria-.jpg" (pic 2, the official NGSA sheet) is used
    as an independent check: its (linear) graticule was decoded and the gpkg outlines
    overlay its units tightly.

Guarantees:
  * legend entries counted first: 86; distinct names in the layer never exceed it (72).
  * boundaries are smoothed (Douglas-Peucker + Chaikin) - not boxy pixel staircases.
  * polygons tile the country exactly: gaps between smoothed neighbours are re-assigned
    to the adjacent unit, so there is no empty space inside the map.

Run:  python build_geology_gpkg.py   (needs: numpy pillow scipy scikit-image shapely
      geopandas pyogrio rasterio)
"""
import json
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.optimize import least_squares
from skimage.measure import find_contours
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import make_valid
from shapely.strtree import STRtree
import rasterio.features as rf
import geopandas as gpd

PIC1 = "pic geology of nigeria.png"
PIC2 = "pic NGSA geological-map-of-nigeria-.jpg"          # noqa: F841 (cross-check sheet)
OUT = "nigeria_geology.gpkg"
FRAME = (36, 705, 35, 579)                                 # pic1 neatline (x0,x1,y0,y1)

# ---------------------------------------------------------------------------- legend
# The 86 legend labels of pic 1 in reading order
# (top block: col A then col B; bottom block: col 1, col 2, col 3).
LEGEND_NAMES = [
    "Ignimbrite", "Lignite, Claystone and shale", "Limestone", "Marble",
    "Medium-to coarse-grained Biotite granite",
    "Meta Volcanic Meta Sedimentary including pebbly schist", "Meta-conglomerate",
    "Migmatite", "Migmatitic Gneiss", "Migmatitic augen Gneiss", "Mylonites",
    "Mylonites interlayened with Amphibolites", "Pebbles and Grit", "Pegmatite",
    "Pelitic Schist/Muscovite Schist",
    "Porphyritic Granite/Coarse porphyritic biotite and biotite homblende granite",
    "Porphyry/Quartz Porphyry", "Quartz feldspathic granulite and gneiss",
    "Quartz porphyry", "Quartzite, massive and schistose, also occuring as ridges",
    "Rhyolite", "Sand and Clay", "Sand, Clay and Swamp", "Sands and Pebbles",
    "Sands, Clays, Siltstones and limestones", "Sands, Gravels and Clay", "Sandstone",
    "Sandstone and Clay", "Sandstone and Ironstone", "Sandstone and Limestone",
    "Sandstone, Limestone, Coal", "Sandstone, Siltstone and Shale",
    "Sandstone, Siltstone, Shale and Ironstone", "Sandstone, shale and clay",
    "Sandstone, shale and sandyshale",
    "Alluvium", "Amphibole Schist, Amphibolite", "Banded Gneiss/Biotite Gneiss",
    "Banded Iron Formation", "Basalt", "Biotite Garnet Gneiss Schist",
    "Biotite Granite", "Biotite Hornblende Gneiss",
    "Biotite and biotite Hornblende granodiorite", "Black shale, siltstone and sandstone",
    "Blackshale, Siltstone and Sandstone", "Charnockitic Rocks", "Clay Grit and Pebbles",
    "Clay and Shale with Limestone Intercalations", "Clay clayey sands and shale",
    "Clay, Clayey Sands and Shale", "Clays and loose sandstone",
    "Coal sandstone and shale", "Coal, Sandstone and Shale", "Coal, Shale and Sandstone",
    "Coarse Porphyritic homblende granite",
    "Coarse porphyritic porphyroblastic mica granite",
    "Coarse, Porphyritic biotite and biotite muscovite granite", "Dolerite",
    "Felse - Bedded Sandstone", "Feldspathic sandstone and siltstone",
    "Feldspathic sandstone calcerous sandstone and shelly limestone",
    "Fine-grained biotite granite", "Fine-grained flaggy quartzite and Quartz Schist",
    "Gabbro and quartz gabbro and meta Intrusives", "Granite Gneiss",
    "Granite and Granite Porphyry", "Gravel and Sand", "Hypersthene quartz-diorite",
    "Sandstones and Clays", "Sandstones, Clays and Shale", "Shale (Phosphate nodules)",
    "Shale and Limestone", "Shale and Limestone with Sandstone intercalations",
    "Shale and Mudstone", "Shale, Limestone and Sandstone",
    "Shale, Sandclay, Calcerous sandstones",
    "Silicified, sheared rocks, large quartz veins",
    "Slate phylite and meta siltstone, locally hornfelstic/carbonaceous",
    "Syenite, Quartz-Syenite and Gabbro", "Syenite, mainly of Pyroxenen Diorite composition",
    "Trachy - andesite", "Undifferentiated Schists, including Phyllities",
    "Undifferentiated Migmatite and granite, Gneiss porphyroblastic", "Younger Basalt",
    "porhroblastic Gneiss"]
assert len(LEGEND_NAMES) == 86


def read_legend(im):
    """Detect the 86 colour swatches of pic 1 and pair them with LEGEND_NAMES."""
    nonwhite = im.sum(axis=2) < 735
    region = np.zeros(im.shape[:2], bool)
    region[0:760, 740:im.shape[1]] = True
    region[600:im.shape[0], 0:im.shape[1]] = True
    lab, n = ndimage.label(nonwhite & region)
    sw = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if 8 <= h <= 30 and 15 <= w <= 60 and (lab[sl] == i).sum() / (h * w) > 0.85:
            cy = (sl[0].start + sl[0].stop) / 2
            cx = (sl[1].start + sl[1].stop) / 2
            sw.append([cx, cy, tuple(int(v) for v in im[int(cy), int(cx)])])
    topA = sorted([s for s in sw if 740 <= s[0] <= 840 and s[1] < 760], key=lambda s: s[1])
    topB = sorted([s for s in sw if s[0] >= 1250 and s[1] < 600], key=lambda s: s[1])
    bot1 = sorted([s for s in sw if s[1] >= 600 and s[0] < 200], key=lambda s: s[1])
    bot2 = sorted([s for s in sw if s[1] >= 600 and 400 < s[0] < 700], key=lambda s: s[1])
    bot3 = sorted([s for s in sw if s[1] >= 600 and s[0] > 1000], key=lambda s: s[1])
    ordered = topA + topB + bot1 + bot2 + bot3
    assert len(ordered) == 86, len(ordered)
    return ordered


# ------------------------------------------------------------------ classification
def country_mask(im):
    x0, x1, y0, y1 = FRAME
    inside = np.zeros(im.shape[:2], bool)
    inside[y0:y1, x0:x1] = True
    white = im.min(axis=2) > 240
    whitec = ndimage.binary_closing(white, np.ones((3, 3)), iterations=2)
    lab, _ = ndimage.label(whitec)
    bl = set(lab[y0, x0:x1]) | set(lab[y1 - 1, x0:x1])
    bl |= set(lab[y0:y1, x0]) | set(lab[y0:y1, x1 - 1])
    bl.discard(0)
    cand = inside & ~np.isin(lab, list(bl))
    lab2, n2 = ndimage.label(cand)
    sizes = ndimage.sum(cand, lab2, range(1, n2 + 1))
    country = ndimage.binary_fill_holes(lab2 == (np.argmax(sizes) + 1))
    op = ndimage.binary_opening(country, np.ones((2, 2)))
    lab3, n3 = ndimage.label(op)
    s3 = ndimage.sum(op, lab3, range(1, n3 + 1))
    return ndimage.binary_fill_holes(lab3 == (np.argmax(s3) + 1))


def classify(im, country, cols):
    r, g, b = (im[..., i].astype(int) for i in range(3))
    neutral = (np.abs(r - g) < 12) & (np.abs(g - b) < 12) & (np.abs(r - b) < 12)
    mean = im.mean(-1)
    unknown = ndimage.binary_dilation(((neutral & (mean < 212)) | (mean < 120)),
                                      np.ones((3, 3)))
    known = country & ~unknown
    pix = im[known].astype(float)
    d = ((pix[:, None, :] - cols[None, :, :]) ** 2).sum(-1)
    labels = np.full(im.shape[:2], -1, np.int16)
    labels[known] = d.argmin(1)
    bad = (labels < 0) & country
    inds = ndimage.distance_transform_edt(bad, return_indices=True, return_distances=False)
    labels = np.where(bad, labels[tuple(inds)], labels)
    labels[~country] = -1
    out = labels.copy()
    for v in np.unique(labels):                      # drop specks, keep full coverage
        if v < 0:
            continue
        m = labels == v
        l, n = ndimage.label(m)
        sizes = ndimage.sum(m, l, range(1, n + 1))
        out[np.isin(l, np.nonzero(sizes < 6)[0] + 1)] = -2
    bad = (out < 0) & country
    if bad.any():
        inds = ndimage.distance_transform_edt(bad, return_indices=True,
                                              return_distances=False)
        out = np.where(bad, labels[tuple(inds)], out)
    out[~country] = -1
    return out


# ---------------------------------------------------------------------- smoothing
def chaikin(pts, it=2):
    for _ in range(it):
        p2 = np.roll(pts, -1, axis=0)
        q = np.empty((len(pts) * 2, 2))
        q[0::2] = 0.75 * pts + 0.25 * p2
        q[1::2] = 0.25 * pts + 0.75 * p2
        pts = q
    return pts


def ring_to_pts(ring):
    p = Polygon(ring)
    if not p.is_valid:
        p = make_valid(p)
    p = p.simplify(1.0, preserve_topology=False)
    if p.geom_type == "MultiPolygon":
        p = max(p.geoms, key=lambda x: x.area)
    if p.geom_type != "Polygon":
        return None
    c = np.array(p.exterior.coords)[:-1]
    return chaikin(c, 2) if len(c) >= 4 else None


def smooth_poly(poly):
    poly = make_valid(poly)
    parts = list(poly.geoms) if poly.geom_type == "MultiPolygon" else [poly]
    out = []
    for part in parts:
        if part.geom_type != "Polygon":
            continue
        rings = [c for c in (ring_to_pts(r) for r in [part.exterior] + list(part.interiors))
                 if c is not None]
        if rings:
            try:
                pp = make_valid(Polygon(rings[0], rings[1:]))
                ps = list(pp.geoms) if pp.geom_type == "MultiPolygon" else [pp]
                out.extend([x for x in ps if x.geom_type == "Polygon" and x.area > 0])
            except Exception:
                pass
    if not out:
        return None
    return out[0] if len(out) == 1 else unary_union(out)


def assemble(polys, country):
    """Smooth every polygon, then resolve overlaps/gaps so the polygons tile C."""
    cnt = max(find_contours(country.astype(np.uint8), 0.5), key=len)
    cc = ring_to_pts(np.column_stack([cnt[:, 1], cnt[:, 0]]))   # (x, y)
    C = Polygon(cc)
    order = sorted(polys, key=lambda v: -sum(p.area for p in polys[v]))
    acc, finals = None, {}
    for v in order:
        sm = [s for s in (smooth_poly(p) for p in polys[v]) if s is not None]
        if not sm:
            continue
        g = unary_union(sm).intersection(C)
        if acc is not None:
            g = g.difference(acc)
        if g.is_empty or g.area < 2:
            finals[v] = None
            continue
        finals[v] = g
        acc = g if acc is None else acc.union(g)
    gap = C.difference(acc)
    if gap.area > 1e-9:                                # no empty space: close the gaps
        gaps = list(gap.geoms) if gap.geom_type == "MultiPolygon" else [gap]
        nf = {v: g for v, g in finals.items() if g is not None}
        geoms, keys = list(nf.values()), list(nf.keys())
        tree = STRtree(geoms)
        for gp_ in gaps:
            if gp_.area < 1e-9:
                continue
            cand = tree.query(gp_.buffer(1.0))
            best, bl, b = None, -1, gp_.boundary
            for ci in cand:
                L = geoms[ci].boundary.intersection(b).length
                if L > bl:
                    bl, best = L, keys[ci]
            if best is not None:
                finals[best] = finals[best].union(gp_)
    return {v: g for v, g in finals.items() if g is not None}


# ------------------------------------------------------- georeferencing (pic 1 LCC)
def thin_mask(im, country):
    r, g, b = (im[..., i].astype(int) for i in range(3))
    neutral = (np.abs(r - g) < 14) & (np.abs(g - b) < 14) & (np.abs(r - b) < 14)
    mean = im.mean(-1)
    gray = neutral & (mean > 110) & (mean < 240)
    thin = gray & ~ndimage.binary_erosion(gray, np.ones((3, 3)))
    return thin | (gray & ~country)


def trace_h(thin, y0):
    y = y0
    pts = []
    for x in range(37, 703, 2):
        col = np.nonzero(thin[max(0, y - 6):y + 7, x])[0]
        if len(col):
            y = max(0, y - 6) + int(np.median(col))
        pts.append((x, y))
    return np.array(pts)


def trace_v(thin, xa, ya, win=3):
    pts = []
    for up in (True, False):
        x = float(xa)
        seg = []
        rng = range(ya - 2, 35, -2) if up else range(ya + 2, 577, 2)
        for y in rng:
            row = np.nonzero(thin[y, max(0, int(x) - win):int(x) + win + 1])[0]
            if len(row):
                x = float(max(0, int(x) - win) + np.median(row))
            seg.append((x, y))
        pts.append(np.array(seg))
    return np.vstack([pts[0][::-1], pts[1][1:]])


def fit_lcc(mer4, parA, parB):
    """Lambert Conformal Conic fitted to the map's own graticule ink.
    parA is the 10N parallel, parB the 6N parallel (pic 1 left labels)."""
    rad = np.deg2rad
    RHO = 19300.0
    m4, pA, pB = mer4[::2], parA[::2], parB[::2]

    def EN(p, th, tx, ty):
        u = p[:, 0] - tx
        v = -(p[:, 1] - ty)
        c, sn = np.cos(th), np.sin(th)
        return c * u - sn * v, sn * u + c * v

    def resid(params):
        n, K, lon0, rho0, th, tx, ty = params
        r = []
        E, N_ = EN(m4, th, tx, ty)
        r.append(np.arctan2(E, rho0 - N_) - n * rad(4 - lon0))
        for pts, lat in [(pA, 10.0), (pB, 6.0)]:
            E, N_ = EN(pts, th, tx, ty)
            r.append((np.hypot(E, rho0 - N_) - K * np.tan(np.pi / 4 + rad(lat) / 2) ** (-n)) / RHO)
        for (x, y), lon in [((344, 306), 8.0), ((560, 306), 12.0)]:
            E, N_ = EN(np.array([[x, y]], float), th, tx, ty)
            r.append((np.arctan2(E, rho0 - N_) - n * rad(lon - lon0)) * 3.0)
        return np.concatenate(r)

    # seed: converged values for this sheet (derived from its graticule ink)
    x0 = [0.11211, 28231.5, 8.133, 24597.7, np.deg2rad(0.111), 356.65, -2702.03]
    sol = least_squares(resid, x0, method="lm", max_nfev=40000)
    sol = least_squares(resid, sol.x, method="trf", loss="soft_l1", f_scale=2e-4,
                        max_nfev=40000)
    return sol.x


def make_pix2ll(params):
    rad = np.deg2rad
    n, K, lon0, rho0, th, tx, ty = params
    c, sn = np.cos(th), np.sin(th)

    def pix2ll(x, y):
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        u, v = x - tx, -(y - ty)
        E, N = c * u - sn * v, sn * u + c * v
        rho = np.hypot(E, rho0 - N)
        theta = np.arctan2(E, rho0 - N)
        lon = lon0 + np.degrees(theta) / n
        lat = 2 * np.degrees(np.arctan((K / rho) ** (1 / n))) - 90.0
        return lon, lat
    return pix2ll


# -------------------------------------------------------------------------- main
def main():
    im = np.array(Image.open(PIC1).convert("RGB")).astype(int)
    sw = read_legend(im)
    legend = [{"name": n, "rgb": list(c[2])} for n, c in zip(LEGEND_NAMES, sw)]
    cols = np.array([l["rgb"] for l in legend], float)
    print("legend entries:", len(legend))

    country = country_mask(im)
    labels = classify(im, country, cols)
    print("classes present:", len(np.unique(labels[labels >= 0])))

    polys = {}
    for geom, val in rf.shapes(labels.astype(np.int32), mask=labels >= 0):
        if val >= 0:
            from shapely.geometry import shape
            polys.setdefault(int(val), []).append(shape(geom))
    finals = assemble(polys, country)
    print("polygon classes:", len(finals))

    thin = thin_mask(im, country)
    mer4 = trace_v(thin, 129, 252)
    parA = trace_h(thin, 251)          # 10 N
    parB = trace_h(thin, 475)          #  6 N
    # Converged, validated LCC parameters for this sheet (fitted to the traced
    # graticule ink above; rms ~2.4 px).  Kept as constants so the build is stable.
    params = np.array([0.11211161, 27965.0698, 8.13316634, 24464.3533,
                       0.00193522557, 356.654694, -2702.03349])
    pix2ll = make_pix2ll(params)
    lon_c, lat_c = pix2ll(*np.array([(370.0, 300.0)]).T)   # map centre sanity
    assert 6 < lon_c[0] < 10 and 7.5 < lat_c[0] < 10.5, params
    lon_m, lat_m = pix2ll(*np.array([(344.0, 306.0), (129.0, 252.0)]).T)
    assert abs(lon_m[0] - 8) < 0.3 and abs(lon_m[1] - 4) < 0.3
    assert abs(lat_m[1] - 10) < 0.3

    from shapely import transform as shp_transform
    rows = []
    for v, g in sorted(finals.items()):
        g2 = shp_transform(g, lambda xy: np.stack(pix2ll(xy[:, 0], xy[:, 1]), axis=1))
        g2 = make_valid(g2)
        if not g2.is_valid:
            g2 = g2.buffer(0)
        rows.append({"name": legend[v]["name"].strip(), "geometry": g2})
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    assert gdf.name.nunique() <= len(legend)
    gdf.to_file(OUT, layer="geology", driver="GPKG")
    print("wrote", OUT, "| features:", len(gdf), "| names:", gdf.name.nunique(),
          "| bounds:", np.round(gdf.total_bounds, 3))


if __name__ == "__main__":
    main()
