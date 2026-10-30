#!/usr/bin/env python3
"""Plate: what the label/line splitting looked like, and what the repair did about it."""
import geopandas as gpd, matplotlib
import numpy as np, pymupdf
from matplotlib.collections import LineCollection
from PIL import Image
from shapely import STRtree
from shapely.geometry import box

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SHEET = "Geological_Map_of_Nigeria.pdf"
X0, Y0 = 276.36, 2281.63
KX, KY = 157.593, 157.586


def gaps(gdf, tol=2500):
    u = gdf.to_crs(32632)
    geoms, codes = u.geometry.tolist(), u.unit_code.tolist()
    tree = STRtree(geoms)
    out = []
    for i, g in enumerate(geoms):
        for j in tree.query(g, predicate="dwithin", distance=tol):
            j = int(j)
            if j <= i or codes[i] != codes[j]:
                continue
            d = g.distance(geoms[j])
            if 0 < d <= tol:
                out.append(d)
    return np.array(out)


def rings(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    return [np.asarray(p.exterior.coords) for p in polys]


before = gpd.read_file("/tmp/prev.gpkg", layer="geology_units")
after = gpd.read_file("Geology_Units_Repaired.geojson")
gb, ga = gaps(before), gaps(after)
print("before", len(gb), "after", len(ga))

# the worst surviving cuts in the OLD layer, one per unit code
u = before.to_crs(32632)
geoms, codes = u.geometry.tolist(), u.unit_code.tolist()
tree = STRtree(geoms)
cuts = []
for i, g in enumerate(geoms):
    for j in tree.query(g, predicate="dwithin", distance=200):
        j = int(j)
        if j <= i or codes[i] != codes[j]:
            continue
        d = g.distance(geoms[j])
        if 0 < d <= 200:
            cuts.append((d, codes[i], g.centroid.x, g.centroid.y))
cuts.sort()
picked, seen = [], set()
for d, code, x, y in cuts:
    if code in seen:
        continue
    seen.add(code)
    picked.append((code, *u.to_crs(4326).geometry.iloc[0].centroid.coords[0][:0]))
    picked[-1] = (code, gpd.GeoSeries([__import__("shapely").Point(x, y)], crs=32632).to_crs(4326).iloc[0].x,
                  gpd.GeoSeries([__import__("shapely").Point(x, y)], crs=32632).to_crs(4326).iloc[0].y, d)
    if len(picked) == 3:
        break
print("cases:", [(c, round(d)) for c, _, _, d in picked])

fig = plt.figure(figsize=(17, 11.2), dpi=140)
gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1], hspace=.28, wspace=.07)

ax = fig.add_subplot(gs[0, :])
bins = np.linspace(0, 2500, 51)
ax.hist(gb, bins=bins, color="#c0504d", alpha=.62, label=f"before the repair — {len(gb):,} pairs")
ax.hist(ga, bins=bins, color="#2f6f4f", alpha=.75, label=f"after the repair — {len(ga):,} pairs")
ax.set_xlabel("distance between two polygons that carry the same unit code (metres)")
ax.set_ylabel("number of pairs")
ax.set_title("One unit split into several polygons: how far apart the pieces sit", fontsize=13, loc="left")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(.0, .88))
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, ax.get_ylim()[1] * 1.12)
for lim, lab, xf in [(500, "<500 m", .26), (1000, "<1 km", .46)]:
    n_b, n_a = int((gb < lim).sum()), int((ga < lim).sum())
    ax.axvline(lim, color="#555", lw=.8, ls=":")
    ax.text(xf, .80, f"{lab}:  {n_b} → {n_a}", transform=ax.transAxes, fontsize=10.5, color="#222")
ax.text(.99, .96, "pairs further than 2.5 km apart are not counted: at that distance a unit really is\n"
        "in two places, not split by a printed name or a line crossing it",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#555")

page = pymupdf.open(SHEET)[0]
for k, (code, cx, cy, d) in enumerate(picked):
    axx = fig.add_subplot(gs[1, k])
    half = .045
    hp = half * 157.59
    x, y = cx * KX - X0, Y0 - cy * KY
    pix = page.get_pixmap(matrix=pymupdf.Matrix(9, 9),
                          clip=pymupdf.Rect(x - hp, y - hp, x + hp, y + hp), alpha=False)
    axx.imshow(Image.frombytes("RGB", (pix.width, pix.height), pix.samples), zorder=0)
    box_ = box(cx - half, cy - half, cx + half, cy + half)
    def to_px(gdf, colour, width, dash):
        segs = []
        for g in gdf.geometry[gdf.geometry.intersects(box_)]:
            for r in rings(g):
                segs.append(np.column_stack([(r[:, 0] - cx) / (2 * half) * pix.width,
                                             (cy - r[:, 1]) / (2 * half) * pix.height]))
        return LineCollection(segs, colors=colour, linewidths=width, zorder=3,
                              linestyles=dash)

    axx.add_collection(to_px(before, "#ff2b2b", 1.1, "--"))
    axx.add_collection(to_px(after, "#00c2ff", 1.5, "solid"))
    axx.set_xlim(0, pix.width); axx.set_ylim(pix.height, 0)
    axx.set_xticks([]); axx.set_yticks([])
    for s in axx.spines.values():
        s.set_color("#999")
    axx.set_title(f"{code} — old boundary red, repaired boundary blue", fontsize=10)

fig.suptitle("Geology units: a printed name or a line no longer cuts a unit in two",
             fontsize=15.5, x=.008, ha="left")
fig.text(.008, .015, "Top: every pair of polygons sharing a unit code, by the gap between them.  "
         "Bottom: the same three places over the printed sheet.  Red dashed is the old "
         "boundary, which detoured around every letter; blue is the repaired boundary, which runs "
         "straight through the name because the name is printed on the rock, not between two rocks.",
         fontsize=9, color="#444")
fig.savefig("Geology_Partition_Before_After.png", bbox_inches="tight", facecolor="white")
print("wrote Geology_Partition_Before_After.png")
