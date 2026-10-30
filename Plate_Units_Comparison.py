#!/usr/bin/env python3
"""The plate that answers "why 97 and not 1,500".

Same window of the Sokoto basin, drawn three ways from data already in this repository:

  1. the printed 2011 sheet, cropped from the georeferenced raster
  2. the shipped layer: 97 map units (Build_Geology_Units.py)
  3. the traced-body layer: 1,552 bodies (Build_NGSA_Geology.py), kept on disk, not shipped

The point of the plate is not that one is prettier. It is that panel 3 draws the same rock as
panel 2, cut into pieces wherever a name, a road or a shear zone crosses it, so a reader cannot
tell a contact from a label and a "unit" no longer means what the sheet's legend says it means.

Writes Geology_Units_Comparison.png.

Run:  python3 Plate_Units_Comparison.py
"""
import json

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import box
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPoly

WIN = (4.6, 12.0, 6.4, 13.4)          # lon0, lat0, lon1, lat1 — Sokoto / Kebbi / Zamfara
SHEET = "web/data/geology_sheet.jpg"


def patches(gdf, lonlat=WIN):
    out, cols = [], []
    for r in gdf.itertuples():
        c = getattr(r, "sheet_colour", None) or getattr(r, "fill", None) or "#cccccc"
        g = r.geometry
        parts = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
        for p in parts:
            out.append(MplPoly(np.asarray(p.exterior.coords), closed=True))
            cols.append(c)
    return out, cols


def main():
    units = gpd.read_file("Geology_Units.geojson", engine="pyogrio")
    bodies = gpd.read_file("Geology_Bodies.geojson", engine="pyogrio")
    stats = json.load(open("web/data/stats.json"))
    b = stats["bounds"]["geology"]

    fig = plt.figure(figsize=(15.6, 8.6), facecolor="white")
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.30], hspace=0.10, wspace=0.05,
                          left=0.014, right=0.986, top=0.86, bottom=0.03)

    titles = ["1 · the printed sheet", f"2 · shipped: {len(units)} map units",
              f"3 · not shipped: {len(bodies):,} traced bodies"]
    for i, (title, gdf) in enumerate(zip(titles, [None, units, bodies])):
        ax = fig.add_subplot(gs[0, i])
        ax.set_xlim(WIN[0], WIN[2]); ax.set_ylim(WIN[1], WIN[3])
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=11.5, fontweight="600", color="#22303d", pad=9)
        for sp in ax.spines.values():
            sp.set_color("#c9d2db")
        if gdf is None:
            ax.imshow(plt.imread(SHEET), extent=[b[0], b[2], b[1], b[3]], aspect="auto")
            continue
        clip = gdf[gdf.geometry.intersects(box(*WIN))]
        pats, cols = patches(clip)
        ax.add_collection(PatchCollection(pats, facecolor=cols, edgecolor="#3b3b3b",
                                          linewidth=0.35))

    # ---------------------------------------------------------------- the numbers
    ax = fig.add_subplot(gs[1, :]); ax.axis("off")
    cols = [("", 0.0), ("2 · shipped", 0.40), ("3 · traced bodies", 0.58)]
    rows = [
        ("polygons in Nigeria", f"{len(units)}", f"{len(bodies):,}"),
        ("polygons in this window",
         f"{len(units[units.geometry.intersects(box(*WIN))])}",
         f"{len(bodies[bodies.geometry.intersects(box(*WIN))]):,}"),
        ("distinct unit codes", f"{units.unit_code.nunique()}", f"{bodies.unit_code.nunique()}"),
        ("area covered", f"{units.area_km2.sum():,.0f} km²", f"{bodies.area_km2.sum():,.0f} km²"),
        ("median polygon", f"{units.area_km2.median():,.0f} km²", f"{bodies.area_km2.median():,.1f} km²"),
        ("legend rows it can fill", "97 of 97", "78 of 97"),
        ("names read from the legend", "91 (94%)", "1,402 of 1,552"),
    ]
    for j, (txt, x) in enumerate(cols):
        ax.text(x, 1.0, txt, fontsize=10, fontweight="600", color="#22303d",
                transform=ax.transAxes, va="top")
    for i, row in enumerate(rows):
        y = 0.855 - i * 0.135
        for j, (txt, x) in enumerate(zip(row, [c[1] for c in cols])):
            ax.text(x, y, txt, fontsize=10,
                    color="#26303a" if j == 0 else ("#0f5f7a" if j == 1 else "#8a5410"),
                    transform=ax.transAxes, va="top")
    ax.plot([0.0, 0.97], [0.925, 0.925], color="#c9d2db", lw=1, transform=ax.transAxes,
            clip_on=False)
    ax.text(0.755, 1.0,
            "Both layers are read from the same sheet, so the\n"
            "difference is not in the rock. A traced body stops\n"
            "wherever printed type, a road or a shear zone crosses\n"
            "it, so one legend row becomes hundreds of shapes and\n"
            "a contact can no longer be told from a label. The\n"
            "shipped layer keeps one shape per unit and the\n"
            "legend's own 97 codes.",
            fontsize=9.3, color="#4a5563", va="top", transform=ax.transAxes, linespacing=1.6)

    fig.text(0.014, 0.955, "Why the geology layer is 97 units and not 1,500",
             fontsize=15.5, fontweight="600", color="#101720")
    fig.text(0.014, 0.912,
             "Same ground — Sokoto, Kebbi and Zamfara, 4.6–6.4°E by 12.0–13.4°N — drawn three ways. "
             "Colours are the sheet's own tints, measured per unit.",
             fontsize=10, color="#4a5563")
    fig.savefig("Geology_Units_Comparison.png", dpi=150, facecolor="white")
    print("wrote Geology_Units_Comparison.png")


if __name__ == "__main__":
    main()
