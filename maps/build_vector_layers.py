#!/usr/bin/env python3
"""Build the vector products, with the decision for each sheet recorded.

Which sheets become polygons is decided by measurement, not taste
(`vectorisation_study.py` and the round trip in `vectorise_sheets.py`):

  * a **flat class map** whose legend can be read off the page -> polygons. The
    classes are real areas; polygons can be queried, dissolved and measured, and
    the round trip loses < 5 % of the classification.
  * a **rendered surface** (hillshade, interpolation between classes) -> the
    raster stays the product. Polygonising it converts relief or a gradient into
    slivers that carry less information than the picture.
  * a sheet whose **classes are map features we already hold as vector** -> do not
    duplicate the picture; the vector source is better. `general_geology` is this
    case: `geology_units` already has 97 attributed units, so the 9 era classes are
    dissolved from those instead of traced from a 2.5 km/px screenshot.

Layers written:
  poly_soil_ph       5 classes, 1 km/px, palette measured from the printed swatches
  poly_population    5 classes, 2.4 km/px, same
  geology_era        9 era classes dissolved from `geology_units` (no raster input)
"""
import json
import pathlib
import sqlite3
import subprocess
import sys

import geopandas as gpd
import numpy as np
import pyogrio
from PIL import Image
from scipy import ndimage
from shapely.geometry import shape
from skimage.color import rgb2lab
from rasterio.features import shapes
from rasterio.transform import Affine

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import georef_new_map as G  # noqa: E402

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
REPORT = HERE / "vector_layers_report.json"

# sheets that become polygons, with the work settings
VECTORISE = {
    # fill_gaps_px: repair unclassified pixels within N px of a class (ink seams)
    "raster_soil_ph":   dict(maxpx=2400, smooth=2, min_km2=3.0, fill_gaps_px=3),
    "raster_population": dict(maxpx=2000, smooth=2, min_km2=4.0),
}


def hex_lab(h):
    return rgb2lab(np.array([[[int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]]])).reshape(3)


def build(spec, fit, swatches, plan, terr):
    im = G.load_rgb(G.SRC / spec["file"])
    W, H = im.size
    f = min(1.0, plan["maxpx"] / max(W, H))
    small = np.asarray(im.resize((max(1, int(W * f)), max(1, int(H * f))),
                                 Image.BILINEAR))
    mask = ndimage.binary_erosion(G.plate_mask(small, **spec.get("mask", {})),
                                  np.ones((2, 2)))
    h, w = mask.shape

    # the palette is the printed legend, measured - not a k-means guess and not
    # the hand-transcribed hexes, which were up to dE 30 out
    names = [str(l) for _, l in spec["legend"]]
    pal = np.array([hex_lab(s["hex"]) for s in swatches])
    assert len(pal) == len(names), (len(pal), len(names))

    img_lab = rgb2lab(small / 255.0)
    flat = img_lab.reshape(-1, 3)
    cls = np.empty(len(flat), np.int16)
    far = np.empty(len(flat), bool)
    for a in range(0, len(flat), 500_000):
        b = min(a + 500_000, len(flat))
        d = np.linalg.norm(flat[a:b, None, :] - pal[None, :, :], axis=2)
        cls[a:b] = d.argmin(1)
        far[a:b] = d.min(1) > 24.0            # ink, text, shading
    cls = cls.reshape(h, w)
    far = far.reshape(h, w)
    cls = np.where(mask & ~far, cls, -1)

    for _ in range(plan["smooth"]):
        med = ndimage.median_filter(np.where(cls < 0, len(pal), cls), size=3)
        cls = np.where(mask & (med < len(pal)), med, -1)

    # A printed class map has no holes *inside* a class fill: what looks like a
    # hole is the ink line drawn between two colours, or a letter.  Holes within
    # `fill_gaps_px` of a class are therefore repaired by claiming the nearest
    # class.  This is applied to soil pH only, and deliberately not to the
    # population sheet, where large blank areas are places the sheet genuinely
    # leaves uncoloured - inventing values there would be fabrication.
    r = plan.get("fill_gaps_px")
    if r:
        # The unreadable dark-navy swatch must not act as a *source*: the ink
        # line drawn between two class fills is itself dark, and dark navy is
        # the nearest legend colour to it, so it would swallow every seam and
        # quietly grow the one class whose meaning is unknown.
        src_cls = np.ones(len(pal), bool)
        for i, nm in enumerate(names):
            if nm.lower().startswith("unlabelled"):
                src_cls[i] = False
        src = (cls >= 0) & src_cls[np.maximum(cls, 0)]
        dist, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
        seam = mask & (cls < 0) & (dist <= r)
        cls = np.where(seam, cls[iy, ix], cls)
        print(f"    seam repair: filled {int(seam.sum())} px within {r} px of a "
              f"labelled class")

    km_px = fit["km_per_px_ew"] / f
    min_px = max(24, plan["min_km2"] / km_px ** 2)
    for i in range(len(pal)):
        m = cls == i
        l_, nc = ndimage.label(m)
        if nc:
            sizes = ndimage.sum(m, l_, range(1, nc + 1))
            cls[np.isin(l_, np.nonzero(sizes < min_px)[0] + 1)] = -1

    tr = Affine(fit["deg_per_px_lon"] / f, 0, fit["lon0"],
                0, -fit["deg_per_px_lat"] / f, fit["lat0"])
    recs = [(int(v), shape(gm)) for gm, v in
            shapes(cls.astype(np.int32), mask=(cls >= 0), transform=tr)]
    polys = [(i, g.intersection(terr)) for i, g in recs]
    polys = [(i, g) for i, g in polys if not g.is_empty and g.area > 1e-9]
    gdf = gpd.GeoDataFrame(
        {"class_id": [i + 1 for i, _ in polys],
         "class_name": [names[i] for i, _ in polys],
         "legend_hex": [swatches[i]["hex"] for i, _ in polys]},
        geometry=[g for _, g in polys], crs="EPSG:4326")
    gdf["area_km2"] = (gdf.to_crs("EPSG:6933").area / 1e6).round(4)
    kept = float((cls >= 0).sum() / max(mask.sum(), 1))
    return gdf, dict(km_px=round(km_px, 3), classes=len(pal),
                     classified_pct=round(100 * kept, 1),
                     polygons=int(len(gdf)),
                     area_km2=round(float(gdf.area_km2.sum()), 1),
                     palette=[s["hex"] for s in swatches])


def main():
    fits = {r["layer"]: r for r in json.load(open(HERE / "raster_georeferencing.json"))}
    sw = json.load(open(HERE / "legend_swatches.json"))
    terr = gpd.read_file(GPKG, layer="national_territory").geometry.union_all()

    # Drop every layer this script is about to write, *with its registers*.
    # GDAL's `to_file` appends a layer to an existing GeoPackage and refuses a
    # table name that `gpkg_contents` already advertises, and a half-finished
    # drop leaves `gpkg_contents` pointing at a table that is gone.  Dropping
    # table + rtree + register rows together makes a rerun deterministic.
    targets = {"geology_era"} | {n.replace("raster_", "poly_")
                                for n in VECTORISE}
    con = sqlite3.connect(GPKG, isolation_level=None)   # explicit commits
    have = {n for n, _ in pyogrio.list_layers(GPKG)}
    stale = sorted(n for n in have if n.startswith("poly_") or n in targets)
    for n in stale:
        for t in [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
                " AND name LIKE 'rtree_%'")]:
            if t.startswith(f"rtree_{n}_") and not any(
                    t.endswith(x) for x in ("_node", "_rowid", "_parent", "_data")):
                con.execute(f'DROP TABLE IF EXISTS "{t}"')
        con.execute(f'DROP TABLE IF EXISTS "{n}"')
        for t in ("gpkg_contents", "gpkg_geometry_columns", "gpkg_extensions"):
            con.execute(f"DELETE FROM {t} WHERE table_name = ?", (n,))
    con.close()
    if stale:
        print(f"  rebuilt in place: {', '.join(stale)}")

    out = []
    for spec in G.IMAGES:
        name = spec["layer"]
        if name not in VECTORISE:
            continue
        plan = VECTORISE[name]
        gdf, met = build(spec, fits[name], sw[name]["swatches"], plan, terr)
        layer = name.replace("raster_", "poly_")
        gdf.to_file(GPKG, layer=layer, driver="GPKG")
        met.update(layer=layer, source=name, geometry="Polygon (MultiPolygon)")
        out.append(met)
        print(f"  {layer:20s} {met['classes']} classes  {met['polygons']:5d} polygons  "
              f"{met['area_km2']:8.1f} km2  {met['km_px']} km/px  "
              f"classified {met['classified_pct']}%")

    # --- geology_era: the vector answer to 'can that one be vector?' --------
    gu = gpd.read_file(GPKG, layer="geology_units")
    gu["era_class"] = gu["era"].fillna("unclassified")
    era = gu.dissolve(by="era_class", as_index=False)[["era_class", "geometry"]]
    era = era.rename(columns={"era_class": "class_name"})
    era["area_km2"] = (era.to_crs("EPSG:6933").area / 1e6).round(2)
    era = era.sort_values("area_km2", ascending=False).reset_index(drop=True)
    era.to_file(GPKG, layer="geology_era", driver="GPKG")
    out.append(dict(layer="geology_era", source="geology_units (vector, no raster)",
                    classes=int(len(era)), polygons=int(len(era)),
                    area_km2=round(float(era.area_km2.sum()), 1),
                    note="dissolved by era; the same 9 classes the general "
                         "geology sheet shows, but from attributed vector geology"))
    print(f"  {'geology_era':20s} {len(era)} era classes dissolved from geology_units  "
          f"{era.area_km2.sum():.0f} km2")

    json.dump(out, open(REPORT, "w"), indent=1)
    # a rebuild leaves register debris; clean it in the same run so the shipped
    # file never advertises a layer, index or zoom level it does not contain
    subprocess.run([sys.executable, str(HERE / "fix_gpkg_hygiene.py")], check=True)
    print(f"\nwrote {REPORT.name}")


if __name__ == "__main__":
    main()
