#!/usr/bin/env python3
"""Draw the three class layers, and the ground they do not cover.

`vector_layers_qc.png` was made by hand and went stale the moment the layers
were rebuilt (it still said 115 polygons). This regenerates it from the shipped
GeoPackage, and shows one thing a class map of polygons hides: where the sheet
had nothing to trace. The gap is drawn as a light grey fill inside the
territory, so a class layer with a hole at the border cannot look complete.

Run:  python make_vector_qc.py
"""
import pathlib
import warnings

import geopandas as gpd
import matplotlib
import shapely

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "vector_layers_qc.png"

LAYERS = [("poly_soil_ph", "5 pH classes, traced from the sheet"),
          ("poly_population", "5 population classes, traced from the sheet"),
          ("geology_era", "eras, dissolved from attributed geology")]

terr = gpd.read_file(GPKG, layer="national_territory")
fig, axes = plt.subplots(1, 3, figsize=(18, 6.2))
for ax, (name, sub) in zip(axes, LAYERS):
    g = gpd.read_file(GPKG, layer=name)
    terr.boundary.plot(ax=ax, color="black", linewidth=0.8, zorder=3)
    # what the layer does not cover, inside the territory
    terra = shapely.make_valid(terr.geometry.iloc[0])
    cover = shapely.make_valid(shapely.union_all(list(g.geometry)))
    gap = shapely.make_valid(terra.difference(cover))
    if not gap.is_empty:
        gpd.GeoSeries([gap], crs="EPSG:4326").plot(
            ax=ax, color="#9e9e9e", edgecolor="none", zorder=1)
    if "legend_hex" in g.columns:
        colours = g["legend_hex"]
    else:
        colours = [plt.cm.tab10(i) for i in range(len(g))]
    g.plot(ax=ax, color=colours, edgecolor="none", zorder=2)
    gap_pct = 100 * gap.area / terra.area if not gap.is_empty else 0.0
    ax.set_title(f"{name} — {len(g)} polygons, {sub}\n"
                 f"{g['area_km2'].sum():,.0f} km² · sheet has no data on "
                 f"{gap_pct:.1f} % of the territory (grey)", fontsize=10)
    ax.set_xlabel("Geodetic longitude [degree]")
    ax.set_ylabel("Geodetic latitude [degree]")
    ax.set_xlim(2.3, 15.1)
    ax.set_ylim(3.9, 14.2)
    ax.set_aspect("equal")
    ax.grid(alpha=0.2, linewidth=0.4)
    if name == "geology_era":
        for (_, r), c in zip(g.iterrows(), [plt.cm.tab10(i) for i in range(len(g))]):
            ax.plot([], [], marker="s", linestyle="", color=c, markersize=7,
                    label=f"{r['class_name']} — {r['area_km2']:,.0f} km²")
        ax.legend(loc="lower left", fontsize=6.5, framealpha=0.85)

fig.suptitle("The three class-polygon layers, and the ground the printed sheets "
             "leave blank", fontsize=12)
fig.tight_layout()
fig.savefig(OUT, dpi=110)
print(f"wrote {OUT.name}")
