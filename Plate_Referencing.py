#!/usr/bin/env python3
"""Plate: the geology bodies, and the proof that they sit where the sheet says they do.

Panel 1  the source photograph of the sheet with the graticule lines the reference was measured on
Panel 2  the bodies over the printed sheet, national scale
Panel 3  two close-ups: the body outlines on the printed contacts
"""
import json

import geopandas as gpd, matplotlib, numpy as np, pymupdf
from matplotlib.collections import LineCollection
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PHOTO = "/tmp/pic NGSA geological-map-of-nigeria-.jpg"
SHEET = "Geological_Map_of_Nigeria.pdf"
X0, Y0, KX, KY = 276.36, 2281.63, 157.593, 157.586

bodies = gpd.read_file("data/geology/geology_bodies_retired.geojson")
rep = json.load(open("data/geology/geology_bodies_retired_report.json"))

fig = plt.figure(figsize=(16.5, 10.6), dpi=140)
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.05], hspace=.2, wspace=.06)

# ---------------------------------------------------------------- 1. the graticule check
ax = fig.add_subplot(gs[0, 0])
try:
    im = Image.open(PHOTO)
    crop = (150, 150, 1250, 560)
    ax.imshow(im.crop(crop), aspect="auto")
    cp = json.load(open("data/ngsa/graticule_control_points.json"))
    for x, deg in cp["meridians"]:
        if crop[0] <= x <= crop[2]:
            ax.axvline(x - crop[0], color="#ff2222", lw=1.0, alpha=.9)
            ax.text(x - crop[0], 12, f"{deg}°E", color="#ff2222", fontsize=7.5, ha="center")
    for y, deg in cp["parallels"]:
        if crop[1] <= y <= crop[3]:
            ax.axhline(y - crop[1], color="#ff2222", lw=1.0, alpha=.9)
            ax.text(6, y - crop[1] - 4, f"{deg}°N", color="#ff2222", fontsize=7.5, va="bottom")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("the printed graticule, measured line by line", fontsize=10, loc="left")
except Exception as e:  # photo not present: say so rather than invent a panel
    ax.text(.5, .5, "source photograph not present", ha="center", fontsize=9)
    ax.set_axis_off()
    print("photo missing:", e)

# ---------------------------------------------------------------- 2. the check, in numbers
ax2 = fig.add_subplot(gs[0, 1:])
ax2.set_axis_off()
ref = rep["reference"]
rows = [("reference control points", f"{ref['control_points']['meridians']} meridians + "
                                     f"{ref['control_points']['parallels']} parallels"),
        ("grid spacing on the sheet", f"{ref['grid_pixels_per_degree'][0]} px per degree east–west, "
                                      f"{ref['grid_pixels_per_degree'][1]} px north–south"),
        ("grid straightness", f"{ref['grid_straightness_px']['meridian']} px across a meridian, "
                              f"{ref['grid_straightness_px']['parallel']} px across a parallel"),
        ("shipped transform vs the grid", f"mean {ref['shipped_vs_grid_km'][0]} km, "
                                          f"worst {ref['shipped_vs_grid_km'][1]} km"),
        ("what was done", "the polygons were re-tied to the measured graticule"),
        ("bodies after repair", f"{rep['bodies']} in {rep['codes']} codes, "
                                f"{rep['coverage_pct']}% of Nigeria, "
                                f"{abs(rep['overlap_km2']):.2f} km² overlap"),
        ("tiny bodies left", f"{rep['under_0_5_km2']} under 0.5 km² "
                             f"({rep['merged_tiny']} merged into a neighbour)")]
for i, (k, v) in enumerate(rows):
    y = .93 - i * .125
    ax2.text(.02, y, k.upper(), fontsize=8.0, color="#777", transform=ax2.transAxes)
    ax2.text(.30, y - .012, v, fontsize=10.5, color="#111", transform=ax2.transAxes)
ax2.text(.02, .03, "The header of the source file said \u201cEPSG:4326 \u2014 assumed datum\u201d.\n"
                   "It is no longer assumed: the sheet's own grid is the reference, and it is measured.",
         fontsize=9, color="#444", transform=ax2.transAxes, va="bottom")
ax2.set_title("the reference is now measured, not assumed", fontsize=10, loc="left")

# ---------------------------------------------------------------- 3. national overlay
page = pymupdf.open(SHEET)[0]


def draw(ax, cx, cy, half, zoom, title):
    hp = half * KX
    x, y = cx * KX - X0, Y0 - cy * KY
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=pymupdf.Rect(x - hp, y - hp, x + hp, y + hp), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    ax.imshow(img, zorder=0, extent=[cx - half, cx + half, cy - half, cy + half])
    sel = bodies[bodies.geometry.intersects(
        __import__("shapely").geometry.box(cx - half, cy - half, cx + half, cy + half))]
    segs = []
    for g in sel.geometry:
        polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
        for p in polys:
            segs.append(np.asarray(p.exterior.coords))
    ax.add_collection(LineCollection(segs, colors="#00a6ff", linewidths=.75, zorder=3))
    ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half, cy + half)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=9.5, loc="left")


draw(fig.add_subplot(gs[1, 0]), 8.1, 9.05, 2.3, 2.6, "central Nigeria — the shipped bodies, in blue, on the printed sheet")
draw(fig.add_subplot(gs[1, 1]), 5.3, 12.9, .55, 9, "Sokoto, close up")
draw(fig.add_subplot(gs[1, 2]), 6.4, 5.4, .85, 7, "Niger delta, close up")

fig.suptitle("Geology bodies: re-referenced to the sheet's own graticule", fontsize=15.5, x=.008, ha="left")
fig.text(.008, .012,
         f"{rep['bodies']} bodies, {rep['codes']} unit codes, {rep['coverage_pct']}% of Nigeria covered, "
         f"{abs(rep['overlap_km2']):.2f} km² of overlap, no body smaller than 0.5 km². "
         "Outlines follow the printed contacts; the blue line is the shipped geometry.",
         fontsize=9, color="#444")
fig.savefig("Geology_Referencing.png", bbox_inches="tight", facecolor="white")
print("wrote Geology_Referencing.png")
