#!/usr/bin/env python3
"""Before/after control figure: which frame was the 2023 mineral sheet drawn in?

Left/right panels show the same rendered sheet area with the Natural Earth Nigeria
boundary (dashed) drawn through the printed-graticule definition and the embedded
GeoPDF /Measure definition. Median offsets: 12.94 km and 1.06 km respectively.
Third panel: the 1,323 symbol points before and after the coordinate rewrite.
"""
import json
from pathlib import Path
import numpy as np, pymupdf
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import shape
from shapely.ops import unary_union

P = Path(__file__).resolve().parent
page = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
def printed(x, y): return (x + 288.95) / 157.5987, (2572.35 - y) / 157.6015
def embedded(x, y): return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
                            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)
def to_page(lon, lat, fn):
    # invert the affine by fitting two points
    (l0, b0), (l1, t1) = fn(0, 0), fn(1000, 1000)
    sx = 1000 / (l1 - l0); sy = -1000 / (t1 - b0)
    return (lon - l0) * sx, (lat - b0) * sy
outline = unary_union([shape(f["geometry"]) for f in json.load(open(P / "Nigeria_Natural_Earth_outline.geojson"))["features"]]).boundary
clip = pymupdf.Rect(150, 640, 700, 1200)
pix = page.get_pixmap(matrix=pymupdf.Matrix(1, 1), clip=clip, alpha=False)
img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)

fig, axes = plt.subplots(1, 3, figsize=(18, 6.4), constrained_layout=True)
for ax, fn, title in [(axes[0], printed, "Printed graticule: Natural Earth border (cyan) is ~19 km off\nthe sheet's own red border — median 12.94 km"),
                      (axes[1], embedded, "Embedded GeoPDF measure: cyan border tracks the red one\n— median 1.06 km")]:
    ax.imshow(img, extent=[clip.x0, clip.x1, clip.y1, clip.y0])
    for geom in getattr(outline, "geoms", [outline]):
        xy = np.array(geom.coords) if geom.geom_type == "LineString" else None
        if xy is None: continue
        x, y = to_page(xy[:, 0], xy[:, 1], fn)
        ax.plot(x, y, ls=(0, (6, 3)), lw=2.0, color="#00d1ff")
    ax.set(xlim=(clip.x0, clip.x1), ylim=(clip.y1, clip.y0), title=title, xlabel="PDF x (pt)", ylabel="PDF y (pt)")
    ax.tick_params(labelsize=8)

ax = axes[2]
import csv
rows = list(csv.DictReader(open(P / "Minerals_Symbol_Points_CORRECTED.csv")))
old = np.array([[float(r["lon_printed"]), float(r["lat_printed"])] for r in rows])
new = np.array([[float(r["lon"]), float(r["lat"])] for r in rows])
ax.scatter(old[:, 0], old[:, 1], s=1.5, c="#9aa0a6", label="old (printed graticule)")
ax.scatter(new[:, 0], new[:, 1], s=1.5, c="#0b6fb8", label="corrected (embedded frame)")
for geom in getattr(outline, "geoms", [outline]):
    xy = np.array(geom.coords)
    ax.plot(xy[:, 0], xy[:, 1], color="#333", lw=.8)
ax.set(xlim=(2.5, 14.8), ylim=(3.8, 14.1), xlabel="Longitude (deg E)", ylabel="Latitude (deg N)",
       title="1,323 mineral symbols: +18.9 km east")
ax.legend(markerscale=6, fontsize=8, loc="lower left"); ax.grid(alpha=.25)
fig.suptitle("The 2023 sheet's vector international boundary decides which coordinate frame the artwork uses", fontsize=13)
fig.savefig(P / "Mineral_Registration_QC.png", dpi=130)
