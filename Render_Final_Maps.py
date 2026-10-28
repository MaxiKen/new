#!/usr/bin/env python3
"""Render the finished maps from the GeoPackage, so the pictures match the data exactly."""
import json
from pathlib import Path
import numpy as np, rasterio, geopandas as gpd
from shapely.geometry import box
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from rasterio.mask import mask as rmask
from rasterio.features import geometry_mask

P = Path(__file__).resolve().parent
GPKG = P / "Nigeria_Geology_Minerals_4326.gpkg"
pts = gpd.read_file(GPKG, layer="minerals_symbols")
nig = gpd.read_file(GPKG, layer="nigeria_boundary")
nigeria = nig.geometry.union_all()
NIG_B = gpd.GeoSeries([nigeria.boundary], crs=nig.crs)

def rd(name):
    with rasterio.open(f"GPKG:{GPKG}:{name}") as d:
        return d.read(), d.transform, d.crs

geo, tr, crs = rd("ref_geology_2011")
dens, _, _ = rd("mineral_density_all")
metal, _, _ = rd("mineral_density_metallic")
nonm, _, _ = rd("mineral_density_nonmetallic")
ext = (L, R, B, T) = (tr.c, tr.c + tr.a * geo.shape[2], tr.f + tr.e * geo.shape[1], tr.f)

fig, ax = plt.subplots(figsize=(13.2, 11.8), constrained_layout=True)
gshow = np.moveaxis(geo, 0, 2).astype(np.float32) / 255.0
gshow = np.clip((gshow - 0.5) * 0.82 + 0.5, 0, 1)      # slight desaturation of the base
ax.imshow(gshow, extent=ext, origin="upper", interpolation="lanczos")
d = dens[0].copy(); d[d < -9000] = np.nan
lev = [2, 4, 6, 8]
cs = ax.contourf(np.linspace(L, R, d.shape[1]), np.linspace(B, T, d.shape[0]), d,
                 levels=lev, colors=["#f7d9b0", "#f2b07a", "#e07b4f", "#c0432b"],
                 alpha=.42, extend="max")
ax.contour(np.linspace(L, R, d.shape[1]), np.linspace(B, T, d.shape[0]), d, levels=lev,
           colors="#8c2d15", linewidths=.55, alpha=.55, linestyles="--")
NIG_B.plot(ax=ax, color="#1b1b1b", lw=1.1)
CL = {"metallic": ("#8b1a1a", "o"), "industrial": ("#12457a", "s"),
      "gemstone": ("#5b2c83", "^"), "energy": ("#111111", "D"), "unknown": ("#666666", "x")}
for cls, (c, m) in CL.items():
    s = pts[pts["mineral_class"] == cls]
    if m == "x":
        ax.scatter(s.geometry.x, s.geometry.y, s=13, marker=m, c=c, linewidths=.7, alpha=.9, zorder=5)
    else:
        ax.scatter(s.geometry.x, s.geometry.y, s=13, marker=m, facecolors="none",
                   edgecolors=c, linewidths=.7, alpha=.9, zorder=5)
cb = fig.colorbar(cs, ax=ax, shrink=.52, pad=.015)
cb.set_label("symbols per 1000 km$^2$  (σ ≈ 17 km)", fontsize=9)
cb.ax.tick_params(labelsize=8)
for sp in ax.spines.values(): sp.set_linewidth(.6)
ax.set(xlim=(2.6, 15.0), ylim=(3.9, 14.1), xlabel="Longitude (°E)", ylabel="Latitude (°N)")
handles = [Line2D([], [], marker=m, ls="", markerfacecolor="none" if m != "x" else c,
                  markeredgecolor=c,
                  label=f"{cls} ({int((pts['mineral_class']==cls).sum())})")
           for cls, (c, m) in CL.items() if (pts["mineral_class"] == cls).any()]
handles.append(Patch(facecolor="#f0a860", alpha=.55, label="interpolated density"))
ax.legend(handles=handles, loc="lower left", fontsize=9, framealpha=.95,
          title="1,323 printed symbols", title_fontsize=9)
ax.set_title("Nigeria: geology (2011) with interpolated mineral-symbol density\n"
             "Everything EPSG:4326. Minerals placed at the centre of each printed symbol.\n"
             "Density counts printed symbols, not reserves or grade. Geology registration "
             "residual 1–2 km; datum not established.", fontsize=11)
fig.savefig(P / "Combined_Map_4326.png", dpi=155, facecolor="white")
plt.close(fig)

# --- per-class density comparison ---
fig, axs = plt.subplots(1, 3, figsize=(16.5, 6.2), constrained_layout=True)
for ax, band, title in zip(axs, [dens, metal, nonm],
                           ["all symbols", "metallic", "non-metallic"]):
    b = band[0].copy(); b[b < -9000] = np.nan
    im = ax.imshow(b, extent=ext, origin="upper", cmap="YlOrRd", vmin=0, vmax=np.nanpercentile(b, 99.5))
    NIG_B.plot(ax=ax, color="#333", lw=.7)
    ax.set(xlim=(2.6, 15), ylim=(3.9, 14.1), title=title, xlabel="Longitude (°E)")
    ax.set_ylabel("Latitude (°N)" if ax is axs[0] else "")
    fig.colorbar(im, ax=ax, shrink=.75, label="symbols per 1000 km$^2$")
fig.suptitle("Interpolated mineral-occurrence density, EPSG:4326 — the same field split by commodity class", fontsize=12)
fig.savefig(P / "Mineral_Density_By_Class.png", dpi=140)
print("rendered")
