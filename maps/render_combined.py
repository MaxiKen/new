#!/usr/bin/env python3
"""Render the combined geology + mineral resources map from the GeoPackage."""
import pathlib
import warnings

import geopandas as gpd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"

units = gpd.read_file(GPKG, layer="geology_units")
bnd = gpd.read_file(GPKG, layer="geology_boundaries")
fault = gpd.read_file(GPKG, layer="faults")
riv = gpd.read_file(GPKG, layer="rivers")
water = gpd.read_file(GPKG, layer="water_bodies")
state = gpd.read_file(GPKG, layer="state_boundaries")
natb = gpd.read_file(GPKG, layer="international_boundary")
loc = gpd.read_file(GPKG, layer="mineral_localities_refined")

GROUP_COLOURS = {
    "precious metals": "#d4a017",
    "base metals": "#6a3d9a",
    "ferrous metals": "#8c564b",
    "rare metals": "#e32636",
    "gemstones": "#c71585",
    "industrial minerals": "#2e86c1",
    "construction materials": "#7f8c8d",
    "energy": "#1b4f72",
    "no code printed": "#000000",
}

ERAS = [
    ("Cenozoic", "Cenozoic cover (Quaternary-Neogene)"),
    ("Mesozoic", "Mesozoic sediments (Cretaceous)"),
    ("Neoproterozoic (Pan-African deformed)", "Neoproterozoic, Pan-African deformed"),
    ("Neoproterozoic-Palaeozoic", "Neoproterozoic-Palaeozoic"),
    ("Archaean-Palaeoproterozoic", "Archaean / Palaeoproterozoic basement"),
]


def era_class(e):
    e = str(e)
    for key, _ in ERAS:
        if e.startswith(key):
            return key
    if "Archaean" in e and "reworked" in e:
        return "Archaean-Palaeoproterozoic"
    return None


units["era_class"] = units["era"].map(era_class)

X0, X1, Y0, Y1 = 2.40, 14.85, 3.95, 14.15
W, H = X1 - X0, Y1 - Y0
ASPECT = 1 / np.cos(np.radians((Y0 + Y1) / 2))

fig = plt.figure(figsize=(13.8, 11.6), dpi=200)
fig.patch.set_facecolor("white")
ax = fig.add_axes([0.045, 0.135, 0.94, 0.80])

# ---- geology base -----------------------------------------------------------
for fill, grp in units.groupby("fill"):
    grp.plot(ax=ax, color=fill, edgecolor="none", zorder=1)
water.plot(ax=ax, color="#bfe3f2", edgecolor="#7fb8d4", linewidth=0.4, zorder=2)
riv.plot(ax=ax, color="#5a9ac9", linewidth=0.45, zorder=3)
state.plot(ax=ax, color="none", edgecolor="#7a7a7a", linewidth=0.4, linestyle=(0, (4, 2)), zorder=4)
bnd.plot(ax=ax, color="#4d4d4d", linewidth=0.25, alpha=0.7, zorder=4)
fault.plot(ax=ax, color="#111111", linewidth=0.65, zorder=5)
natb.plot(ax=ax, color="#8b0000", linewidth=1.3, zorder=6)

# ---- mineral localities -----------------------------------------------------
for grp, g in loc.groupby("group_1"):
    ax.scatter(g.geometry.x, g.geometry.y,
               s=11 + 3.0 * g["n_minerals"].fillna(1),
               c=GROUP_COLOURS.get(grp, "#000000"),
               edgecolors="white", linewidths=0.3, alpha=0.93, zorder=8)

# ---- frame + graticule ------------------------------------------------------
ax.set_xlim(X0, X1)
ax.set_ylim(Y0, Y1)
ax.set_aspect(ASPECT)
for lon in range(3, 15):
    ax.axvline(lon, color="#444", lw=0.3, alpha=0.30, zorder=7)
    ax.text(lon, Y0 - 0.10, f"{lon}\u00b0E", ha="center", va="top", fontsize=7, color="#333")
for lat in range(4, 14):
    ax.axhline(lat, color="#444", lw=0.3, alpha=0.30, zorder=7)
    ax.text(X0 - 0.06, lat, f"{lat}\u00b0N", ha="right", va="center", fontsize=7, color="#333")

CITIES = {"Abuja": (7.4951, 9.0579), "Lagos": (3.3792, 6.5244), "Kano": (8.5167, 12.0022),
          "Port Harcourt": (7.0134, 4.8156), "Maiduguri": (13.1506, 11.8311),
          "Sokoto": (5.2476, 13.0609), "Enugu": (7.4985, 6.3350)}
for n, (lo, la) in CITIES.items():
    ax.plot(lo, la, marker="*", ms=8.5, mfc="white", mec="black", mew=0.8, zorder=10)
    ax.annotate(n, (lo, la), xytext=(4, 2), textcoords="offset points", fontsize=7.4,
                fontweight="bold", color="#111", zorder=10,
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none", alpha=0.7))

# ---- legends ----------------------------------------------------------------
gh = [Line2D([], [], marker="o", ls="", mfc=c, mec="white", ms=6, label=g)
      for g, c in GROUP_COLOURS.items()]
leg = ax.legend(handles=gh, loc="upper left", fontsize=7.2, frameon=True, facecolor="white",
                framealpha=0.93, title="Mineral localities, 2023", title_fontsize=8,
                borderpad=0.7, labelspacing=0.42)
leg.set_zorder(20)

lh = [Line2D([], [], color="#8b0000", lw=1.4, label="International boundary"),
      Line2D([], [], color="#7a7a7a", lw=0.8, ls="--", label="State boundary"),
      Line2D([], [], color="#111111", lw=0.9, label="Fault"),
      Line2D([], [], color="#4d4d4d", lw=0.5, alpha=0.75, label="Geological boundary"),
      Line2D([], [], color="#5a9ac9", lw=0.9, label="River"),
      Line2D([], [], color="#7fb8d4", lw=3.2, label="Water body")]
leg2 = ax.legend(handles=lh, loc="lower left", fontsize=7.2, frameon=True, facecolor="white",
                 framealpha=0.93, title="Linework", title_fontsize=8,
                 borderpad=0.7, labelspacing=0.42)
leg2.set_zorder(20)
ax.add_artist(leg)

# scale bar: 200 km at 9 degN
dlon = 200 / (111.32 * np.cos(np.radians(9)))
ax.plot([X1 - 0.35 - dlon, X1 - 0.35], [Y0 + 0.30, Y0 + 0.30], color="black", lw=2.2, zorder=20)
ax.plot([X1 - 0.35 - dlon] * 2, [Y0 + 0.24, Y0 + 0.36], color="black", lw=1.2, zorder=20)
ax.plot([X1 - 0.35] * 2, [Y0 + 0.24, Y0 + 0.36], color="black", lw=1.2, zorder=20)
ax.text(X1 - 0.35 - dlon / 2, Y0 + 0.40, "200 km", ha="center", fontsize=7.4, zorder=20)
north = ax.annotate("N", xy=(X1 - 0.32, Y1 - 1.10), xytext=(X1 - 0.32, Y1 - 1.58),
                    ha="center", fontsize=9, fontweight="bold", zorder=20,
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1))

# ---- titles -----------------------------------------------------------------
fig.text(0.5, 0.965, "GEOLOGY AND MINERAL RESOURCES OF NIGERIA",
         ha="center", fontsize=18, fontweight="bold")
fig.text(0.5, 0.938,
         "Combined from the NGSA 1:2,000,000 Geological Map (2011) and Mineral Resources Map "
         "(2nd edition, 2023)  \u00b7  WGS 84 longitude / latitude (EPSG:4326)",
         ha="center", fontsize=9, color="#444")

# ---- bottom strip: geological units by era ---------------------------------
fig.text(0.045, 0.093, "GEOLOGICAL UNITS BY ERA", fontsize=9, fontweight="bold")
COLS, COLW = 3, 0.305
for i, (key, label) in enumerate(ERAS):
    sub = units[units["era_class"] == key]
    if sub.empty:
        continue
    col, row = i % COLS, i // COLS
    x = 0.045 + col * COLW
    y = 0.058 - row * 0.030
    top = sub.groupby("fill")["area_km2"].sum().sort_values(ascending=False).head(4)
    for c in top.index:
        fig.add_artist(Rectangle((x, y), 0.010, 0.0125, transform=fig.transFigure,
                                 facecolor=c, edgecolor="#666", lw=0.35))
        x += 0.0115
    fig.text(x + 0.005, y + 0.006,
             f"{label}  ({round(sub['area_km2'].sum() / 1000):,}k km\u00b2)",
             fontsize=7.5, va="center")

fig.text(0.5, 0.008,
         "Geology: 1,518 unit polygons in 92 units, 1,509 dated  \u00b7  Minerals: 999 localities, "
         "80 commodities in 8 groups, each joined to its host unit  \u00b7  "
         "median positional \u03c3 \u00b1 0.7 km (26 % of points are label-only, \u03c3 \u00b1 10 km)",
         ha="center", fontsize=7.6, color="#555")

ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
for sp in ax.spines.values():
    sp.set_linewidth(1.0)

for ext in ("png", "pdf"):
    out = HERE / f"Nigeria_Geology_Minerals_4326.{ext}"
    fig.savefig(out, facecolor="white", dpi=200 if ext == "png" else None)
    print("wrote", out, f"{out.stat().st_size / 1e6:.1f} MB")
