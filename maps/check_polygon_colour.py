#!/usr/bin/env python3
"""Check the class-polygon layers against the printed sheets, and write
`polygon_colour_check.json`.

The vector layers claim that each polygon's class is the colour printed at that
place on the sheet.  This tests the claim where it is weakest - and cheapest to
test: at each polygon's interior point (a point guaranteed to be inside it),
read the corresponding pixel of the georeferenced sheet and compare it with the
measured legend swatch for the polygon's class.

Two numbers per layer:
  * `within_24` - share of polygons whose sheet pixel is within dE 24 of *their
    own* class swatch.  dE 24 is the same threshold the builder uses to decide a
    pixel is a class fill rather than ink or text.
  * `nearest_is_own` - share whose sheet pixel is nearer their own swatch than
    any other class swatch.  A polygon can pass the first test and fail the
    second only where the swatches are close together, so both are reported.

A `representative_point` is used, not a centroid: a centroid can fall outside a
crescent-shaped polygon and sample a different class.

Run:  python check_polygon_colour.py
"""
import json
import pathlib

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import rowcol
from skimage.color import rgb2lab

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
SWATCHES = json.load(open(HERE / "legend_swatches.json"))
OUT = HERE / "polygon_colour_check.json"

# class layer -> the sheet it was traced from
PAIRS = {
    "poly_soil_ph": "raster_soil_ph",
    "poly_population": "raster_population",
}


def lab(hex_):
    rgb = np.array([[[int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]]])
    return rgb2lab(rgb).reshape(3)


out = {}
for layer, sheet in PAIRS.items():
    hexes = [s["hex"] for s in SWATCHES[sheet]["swatches"]]
    pal = np.array([lab(h) for h in hexes])
    g = gpd.read_file(GPKG, layer=layer)
    own = {h: int(np.argmin(np.linalg.norm(lab(h)[None, :] - pal, axis=1)))
           for h in g["legend_hex"].unique()}
    recs = []
    with rasterio.open(f"GPKG:{GPKG}:{sheet}") as ds:
        img, tr, n = ds.read(), ds.transform, ds.count
        for _, r in g.iterrows():
            p = r.geometry.representative_point()
            row, col = rowcol(tr, p.x, p.y)
            if not (0 <= row < img.shape[1] and 0 <= col < img.shape[2]):
                continue
            if n == 4 and img[3, row, col] == 0:      # outside the plate mask
                continue
            px = img[:3, row, col].reshape(1, 1, 3) / 255.0
            d = np.linalg.norm(rgb2lab(px).reshape(3)[None, :] - pal, axis=1)
            recs.append(dict(class_name=r["class_name"], own_de=round(float(d[own[r["legend_hex"]]]), 1),
                             nearest=int(np.argmin(d)), nearest_de=round(float(d.min()), 1),
                             area_km2=float(r["area_km2"])))
    own_de = np.array([x["own_de"] for x in recs])
    wrong = [x for x in recs if x["nearest"] != own[x["class_name"]]] if False else \
            [x for x in recs if x["nearest_de"] < x["own_de"]]
    out[layer] = dict(
        sheet=sheet, polygons=int(len(g)), sampled=int(len(recs)),
        median_own_de=round(float(np.median(own_de)), 1),
        p90_own_de=round(float(np.percentile(own_de, 90)), 1),
        within_24_pct=round(100 * float((own_de <= 24).mean()), 1),
        within_40_pct=round(100 * float((own_de <= 40).mean()), 1),
        nearest_is_own_pct=round(100 * float((own_de <= np.array(
            [x["nearest_de"] for x in recs])).mean()), 1),
        nearer_to_another_class=[
            dict(class_name=x["class_name"], own_de=x["own_de"],
                 nearest_de=x["nearest_de"], area_km2=x["area_km2"]) for x in wrong],
    )
    print(f"{layer:16s} {len(recs):4d} samples  median dE {out[layer]['median_own_de']:4.1f}  "
          f"within 24: {out[layer]['within_24_pct']:5.1f}%  "
          f"nearer another swatch: {len(wrong)}")

json.dump(out, open(OUT, "w"), indent=1)
print(f"\nwrote {OUT.name}")
