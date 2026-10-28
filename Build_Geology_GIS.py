#!/usr/bin/env python3
"""Turn the 2011 geology sheet into a usable, documented GIS layer and rebuild the combined map.

Two deliverables, both explicit about what is and is not known:

  Geology_Georeferenced.tif   the whole sheet at 2 px/pt, placed by its printed graticule.
                              EPSG:4326 is a DISPLAY ASSUMPTION: the sheet states no datum.
  Combined_Map_v2.png         geology raster as the base map (full colour, unblended), with the
                              1,323 corrected mineral symbols drawn on top as vector markers
                              coloured by commodity class. This replaces the 62/38 colour blend,
                              which destroyed the geology colours it was supposed to show.

Alignment: the sheet needs no correction. Geology_Alignment_Test.py shows its three independent
feature classes land within ~1 km of modern reference data, and two of them agree with each
other at +0.2 km east, +0.9 km north - under 1.5 map pixels. Applying that would be fitting noise.
"""
import csv, json, zipfile
from pathlib import Path
import numpy as np, pymupdf, rasterio
from rasterio.transform import from_bounds
from PIL import Image, ImageDraw, ImageFont
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

P = Path(__file__).resolve().parent
CROP = pymupdf.Rect(80, 90, 2050, 1693)
def ll(x, y): return (x + 276.36) / 157.593, (2281.63 - y) / 157.586
L, T = ll(CROP.x0, CROP.y0); R, B = ll(CROP.x1, CROP.y1)

page = pymupdf.open(P / "Geological_Map_of_Nigeria.pdf")[0]
SCALE = 2
pix = page.get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), clip=CROP, alpha=False)
img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)

# ---------- 1. standalone georeferenced geology ----------
prof = dict(driver="GTiff", height=img.shape[0], width=img.shape[1], count=3, dtype="uint8",
            crs="EPSG:4326", transform=from_bounds(L, B, R, T, img.shape[1], img.shape[0]),
            compress="deflate", predictor=2, tiled=True, blockxsize=512, blockysize=512)
with rasterio.open(P / "Geology_Georeferenced.tif", "w", **prof) as d:
    d.write(np.moveaxis(img, 2, 0))
    d.update_tags(
        TITLE="Geological Map of Nigeria, 2011 (NGSA)",
        REGISTRATION="printed graticule, reference meridians/parallels fitted to <0.4 pt",
        RESIDUAL_ACCURACY_KM="1-2 (state boundaries 1.7, rivers 2.7, coastline 1.9 km median "
                             "against independent reference data)",
        CORRECTION_APPLIED="none - no single translation is justified by the evidence",
        DATUM="NOT STATED ON THE SHEET. EPSG:4326 assigned only so GIS can display it.",
        ATTRIBUTION="Geological Survey of Nigeria / NGSA. Check terms before redistribution.",
        SUITABLE_FOR="visual reference and regional context at 1:2,000,000",
        NOT_SUITABLE_FOR="surveying, licensing, legal boundaries, navigation, or site-scale decisions")

# ---------- 2. combined map: geology base + mineral symbols as vectors ----------
rows = [r for r in csv.DictReader(open(P / "Minerals_Symbol_Points_CORRECTED.csv"))
        if r["in_nigeria"] == "True"]
CLASS = {"metallic": ("#c0392b", "o", "metallic"),
         "industrial": ("#1f6fb4", "s", "industrial"),
         "gemstone": ("#7d3c98", "^", "gemstone"),
         "energy": ("#1b1b1b", "D", "energy")}
fig, ax = plt.subplots(figsize=(13, 11.5), constrained_layout=True)
ax.imshow(img, extent=(L, R, B, T), origin="upper", interpolation="lanczos")
for cls, (col, mk, lab) in CLASS.items():
    sel = [r for r in rows if r["mineral_class"] == cls and r["tier"] in ("probable", "tentative")]
    ax.scatter([float(r["lon"]) for r in sel], [float(r["lat"]) for r in sel],
               s=17, marker=mk, facecolors="none", edgecolors=col, linewidths=.8, alpha=.85, label=lab)
hid = [r for r in rows if r["tier"] == "unidentified"]
ax.scatter([float(r["lon"]) for r in hid], [float(r["lat"]) for r in hid], s=16, marker="x",
           c="#555", linewidths=.8, label="unidentified")
ax.set(xlim=(L, R), ylim=(B, T), xlabel="Longitude (deg E)", ylabel="Latitude (deg N)")
leg = ax.legend(loc="lower right", fontsize=9, framealpha=.95, title="2023 mineral symbols",
                title_fontsize=9, markerscale=1.6)
for h in leg.legend_handles: h.set_alpha(1)
ax.set_title("Geological map of Nigeria, 2011 — with the 2023 mineral symbols re-registered onto it\n"
             "Geology base is unmodified and unblended. Symbols are the printed glyph centres, "
             "moved +18.9 km east out of the 2023 sheet's incorrect printed-graticule frame.\n"
             "Symbol positions ~1 km; commodity names are classification estimates; "
             "datum not established — use the original sheets for interpretation.",
             fontsize=11)
fig.savefig(P / "Combined_Map_v2.png", dpi=160)
plt.close(fig)

# ---------- 3. bundle ----------
readme = """NIGERIA GEOLOGY + MINERALS - LAYER NOTES

Geology_Georeferenced.tif
  The whole 2011 NGSA geological sheet, 2 px per PDF point, placed by its own printed
  graticule. No correction was applied, because none is justified: the sheet's state
  boundaries, rivers and coastline all land within ~1-2 km of modern reference data, and
  the two best-controlled classes agree with each other at +0.2 km east / +0.9 km north,
  which is less than 1.5 map pixels. See Geology_Alignment_Test.png.

Minerals_Symbol_Points_CORRECTED.geojson / .csv
  1,323 printed mineral symbols with their commodity name, class and confidence tier.
  Coordinates were computed by the original extraction on the 2023 sheet's PRINTED
  graticule, which sits 0.172 degrees (~19 km) west of the frame that sheet was actually
  drawn in. They are corrected here (+18.5 to +19.1 km east). The sheet's own vector
  international boundary proves which frame is right: it matches modern data to 0.5-1.1 km
  in the embedded frame but is 12.9 km out in the printed frame.

HONEST LIMITS
  * No datum is established for either sheet. EPSG:4326 is assigned so GIS software will
    display the rasters; it is not a claim about the source data. Minna -> WGS 84 would
    move Nigeria about 0.09 km, which is below what these sheets can resolve.
  * Ancient and slow-moving: do not use for exploration decisions, licensing, legal
    boundaries, navigation or site-scale work.
  * Commodity names are 80.8% correct overall (leave-one-out). Per-mineral totals are not
    reliable; use the tier and confidence columns per point.
"""
with zipfile.ZipFile(P / "Geology_Layers.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("README.txt", readme)
    for f in ["Geology_Georeferenced.tif", "Minerals_Symbol_Points_CORRECTED.geojson",
              "Minerals_Symbol_Points_CORRECTED.csv", "Geology_Alignment_Test.png"]:
        z.write(P / f, f)
print("tif", (P / "Geology_Georeferenced.tif").stat().st_size // 1024 // 1024, "MB")
print("done")
