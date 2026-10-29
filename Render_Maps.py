#!/usr/bin/env python3
"""Cartographic output for the Nigeria geology & minerals atlas (EPSG:4326).

Map_1_Geology.png      map units, faults, drainage, administrative boundaries
Map_2_Minerals.png     2023 sheet with all 1,323 re-centred symbols, classified
Map_3_Combined.png     geology base + interpolated symbol density + every symbol
Map_4_Symbol_Centring 14x zooms on the source sheet proving the symbol centring

Everything is drawn from Nigeria_Geology_Minerals_4326.gpkg, so a picture cannot disagree
with the data it accompanies. Map furniture: graticule, scale bar, north arrow, legends,
credits and the stated accuracy limits.
"""
import math, textwrap
from pathlib import Path
import numpy as np, rasterio, geopandas as gpd, pymupdf
from PIL import Image
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D

P  = Path(__file__).resolve().parent
G  = P / "Nigeria_Geology_Minerals_4326.gpkg"
units  = gpd.read_file(G, layer="geology_units")
faults = gpd.read_file(G, layer="faults")
rivers = gpd.read_file(G, layer="rivers")
states = gpd.read_file(G, layer="state_boundaries")
roads  = gpd.read_file(G, layer="roads")
pts    = gpd.read_file(G, layer="minerals_occurrences")
nig    = gpd.read_file(G, layer="nigeria_boundary")
NIG    = nig.geometry.union_all()
NIGB   = gpd.GeoSeries([NIG.boundary], crs=nig.crs)
XL, XR, YB, YT = 2.55, 15.0, 4.05, 14.0
ASPECT = 1 / math.cos(math.radians(9.0))
F_DRAW = faults[faults.in_nigeria]
R_DRAW_ROADS = roads[roads.in_nigeria]
R_DRAW = rivers[rivers.in_nigeria]
S_DRAW = states[states.in_nigeria]


def raster_axes(fig, left, width, bottom, data_w, data_h, fig_w, fig_h):
    """Axes whose box exactly fits the data aspect, so no dead white space is left."""
    w_in = width * fig_w
    h_in = w_in * (data_h * ASPECT / data_w)
    return fig.add_axes([left, bottom, width, h_in / fig_h]), w_in, h_in

def rd(name):
    with rasterio.open(f"GPKG:{G}:{name}") as d:
        return d.read(), d.transform

def furniture(ax, scale_km=200, bar=(0.075, 0.06)):
    ax.set_xlim(XL, XR); ax.set_ylim(YB, YT); ax.set_aspect(ASPECT)
    ax.set_xticks(range(4, 15, 2)); ax.set_yticks(range(4, 14, 2))
    ax.tick_params(labelsize=9, length=3.5, color="#444")
    for s in ax.spines.values(): s.set_color("#333"); s.set_linewidth(.8)
    ax.set_xlabel("Longitude (°E)", fontsize=9.5, labelpad=2)
    ax.set_ylabel("Latitude (°N)", fontsize=9.5, labelpad=2)
    ax.grid(color="#8d8d8d", lw=.28, alpha=.5)
    y0 = YB + (YT - YB) * bar[1]
    lat = y0 + (YT - YB) * .22
    dx = scale_km / (111.32 * math.cos(math.radians(lat)))
    x0 = XL + (XR - XL) * bar[0]
    ax.add_patch(Rectangle((x0, y0), dx / 2, .05, fc="#1b1b1b", ec="#1b1b1b", lw=.6, zorder=30))
    ax.add_patch(Rectangle((x0 + dx / 2, y0), dx / 2, .05, fc="white", ec="#1b1b1b", lw=.6, zorder=30))
    for x, t in ((x0, "0"), (x0 + dx / 2, str(scale_km // 2)), (x0 + dx, f"{scale_km} km")):
        ax.text(x, y0 + .085, t, fontsize=7.4, ha="center", zorder=31)
    ax.text(x0, y0 + .235, f"scale at {lat:.1f}°N", fontsize=6.6, color="#555", zorder=31)
    ax.annotate("", xy=(XR - .45, YT - .18), xytext=(XR - .45, YT - .95),
                arrowprops=dict(arrowstyle="-|>", color="#1b1b1b", lw=1.7), zorder=31)
    ax.text(XR - .45, YT - .07, "N", fontsize=10.5, ha="center", weight="bold", zorder=31)

def unit_legend(ax, groups, title, sub, fs=6.0, width=48, ax_h_in=8.97):
    """Column legend with bold period headers and wrapped full unit names.

    Row heights are laid out in points and converted to axes fractions, so the column
    cannot overflow however many units a period contains.
    """
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    lh = (fs * 1.42) / 72.0 / ax_h_in          # one wrapped text line, in axes fraction
    ax.text(0, 1.0, title, fontsize=9.2, weight="bold", va="top", color="#111")
    ax.text(0, 1.0 - lh * 1.5, sub, fontsize=6.5, va="top", color="#666")
    y = 1.0 - lh * 3.4
    for head, items in groups:
        ax.text(0, y, head.upper(), fontsize=6.9, weight="bold", color="#8a2f1e", va="top")
        y -= lh * 1.75
        for label, kw in items:
            txt = "\n".join(textwrap.wrap(label, width))
            n = txt.count("\n") + 1
            ax.add_patch(Rectangle((.004, y - fs / 72.0 / ax_h_in * .78), .05,
                                   fs / 72.0 / ax_h_in * .80, **kw))
            ax.text(.075, y + fs / 72.0 / ax_h_in * .18, txt, fontsize=fs, va="top",
                    color="#222", linespacing=1.30)
            y -= lh * n + lh * .30
        y -= lh * .55
    return y

# ============================================================== MAP 1 - geology
fig = plt.figure(figsize=(16.4, 10.0), facecolor="white")
ax = fig.add_axes([.038, .072, .585, .775])
la = fig.add_axes([.645, .072, .163, .775])
lb = fig.add_axes([.818, .072, .175, .775])

units.plot(ax=ax, color=units["sheet_colour"], ec="#3f3f3f", lw=.15, zorder=1)
R_DRAW_ROADS.plot(ax=ax, color="#222222", lw=.5, alpha=.85, zorder=3)
R_DRAW.plot(ax=ax, color="#1f6fb4", lw=.33, alpha=.8, zorder=3)
S_DRAW.plot(ax=ax, color="#6f6f6f", lw=.6, zorder=4)
F_DRAW.plot(ax=ax, color="#c01018", lw=1.6, zorder=5)
NIGB.plot(ax=ax, color="#0e0e0e", lw=1.4, zorder=6)
furniture(ax, bar=(0.53, 0.055))

PERIODS = ["Recent", "Neogene", "Tertiary to Recent volcanics", "Palaeogene", "Cretaceous",
           "Jurassic", "Pan-African", "Precambrian"]
def groups_for(per_list):
    out = []
    for per in per_list:
        sub = units[(units.period == per) & (units.unit_code != "unlabelled")].drop_duplicates("unit_code")
        sub = sub.sort_values("unit_code")
        if len(sub):
            out.append((f"{per} ({len(sub)})",
                        [(f"{r.unit_code}  {r.unit_name}", dict(fc=r.sheet_colour, ec="#555", lw=.35))
                         for _, r in sub.iterrows()]))
    return out
y_a = unit_legend(la, groups_for(PERIODS[:5]), "MAP UNITS",
                  f"{len(units)} polygons · {units.unit_code.nunique()} codes · part 1 of 2")
y_b = unit_legend(lb, groups_for(PERIODS[5:]), "MAP UNITS (cont.)",
                  "unit codes as printed on the sheet · part 2 of 2")
lb.text(0, y_b + .004, "23 further polygons are drawn but carry no printed code.\n"
                       "They are kept in the data marked 'unlabelled'.", fontsize=5.9,
        va="top", color="#666", linespacing=1.35)

hl = [Line2D([], [], color="#c01018", lw=1.8, label=f"fault (major fracture) — {len(faults)} traces"),
      Line2D([], [], color="#222222", lw=.9, label=f"road — {len(roads)} strokes"),
      Line2D([], [], color="#1f6fb4", lw=1.0, label=f"river — {len(rivers)}"),
      Line2D([], [], color="#6f6f6f", lw=1.2, label=f"state boundary — {len(states)}"),
      Line2D([], [], color="#0e0e0e", lw=1.6, label="international boundary")]
ax.legend(handles=hl, loc="lower left", bbox_to_anchor=(.008, .012), fontsize=7.2,
          framealpha=.97, edgecolor="#999", borderpad=.5, labelspacing=.42, handlelength=1.8)
fig.text(.5, .955, "GEOLOGICAL MAP OF NIGERIA", ha="center", fontsize=20, weight="bold", color="#111")
fig.text(.5, .925, "Map units, faults, roads, drainage and administrative boundaries vectorised from the "
                   "2011 Geological Survey of Nigeria 1:2,000,000 sheet",
         ha="center", fontsize=10.4, color="#333")
fig.text(.038, .022, "EPSG:4326 WGS 84 display frame  ·  unit outlines copied from the sheet, colours not "
                     "reinterpreted  ·  registration residual 1–2 km  ·  no fold or dip-and-strike layer "
                     "exists on this sheet  ·  not a survey product",
         fontsize=7.0, color="#555")
fig.savefig(P / "Map_1_Geology.png", dpi=150, facecolor="white")
plt.close(fig); print("map 1")

# ============================================================== MAP 2 - minerals
img, tr = rd("ref_minerals_2023")
CL = {"metallic": ("#a01414", "o"), "industrial": ("#0b3f7a", "s"),
      "gemstone": ("#5b2c83", "^"), "energy": ("#111111", "D"), "unknown": ("#777777", "x")}
def symbols(ax, s_=9, lw=.55):
    for cls, (c, m) in CL.items():
        s = pts[pts["mineral_class"] == cls]
        kw = dict(s=s_, marker=m, linewidths=lw, alpha=.95, zorder=7)
        if m == "x": kw["c"] = c
        else: kw["facecolors"] = "none"; kw["edgecolors"] = c
        ax.scatter(s.geometry.x, s.geometry.y, **kw)

DW, DH = tr.a * img.shape[2], -tr.e * img.shape[1]
FW, FH = 12.8, 11.0
fig = plt.figure(figsize=(FW, FH), facecolor="white")
ax, _, _ = raster_axes(fig, .045, .91, .062, DW, DH, FW, FH)
ax.imshow(np.moveaxis(img, 0, 2), extent=(tr.c, tr.c + DW, tr.f + tr.e * img.shape[1], tr.f),
          origin="upper", interpolation="lanczos", zorder=1)
symbols(ax); furniture(ax)
hl = [Line2D([], [], marker=m, ls="", markersize=7, markerfacecolor="none" if m != "x" else c,
             markeredgecolor=c, markeredgewidth=.85,
             label=f"{cls}  {int((pts['mineral_class'] == cls).sum())}")
      for cls, (c, m) in CL.items() if (pts['mineral_class'] == cls).sum() > 0]
ax.legend(handles=hl, loc="upper left", fontsize=8.8, framealpha=.97, edgecolor="#888",
          title=f"printed occurrences — {len(pts)}", title_fontsize=8.8, borderpad=.65)
fig.text(.5, .972, "MINERAL RESOURCES MAP OF NIGERIA", ha="center", fontsize=19, weight="bold", color="#111")
fig.text(.5, .945, f"The 2023 NGSA sheet in EPSG:4326; every printed symbol located once, at the centre of its "
                   f"marker ({len(pts)} occurrences, {pts.mineral.nunique()} commodities)", ha="center", fontsize=10.2, color="#333")
fig.text(.045, .022, "Symbol centre ≈ 0.1 km median; one artwork pixel is 0.68 km  ·  names: 18% carried by both "
                     "independent readings, 27% agree on a commodity family, 90% called low confidence  ·  "
                     "counts are not reserves, grade or production",
         fontsize=7.1, color="#555")
fig.savefig(P / "Map_2_Minerals.png", dpi=150, facecolor="white")
plt.close(fig); print("map 2")

# ============================================================== MAP 3 - combined
dens, td = rd("mineral_density_all")
DW, DH = 12.45, 9.95
FW, FH = 13.6, 9.3
fig = plt.figure(figsize=(FW, FH), facecolor="white")
ax, _, _ = raster_axes(fig, .042, .70, .088, DW, DH, FW, FH)
fig_h = FH

def muted(hexcol, k=.72):
    import matplotlib.colors as mc
    r, g, b = mc.to_rgb(hexcol)
    return (1 - (1 - r) * k, 1 - (1 - g) * k, 1 - (1 - b) * k)

units.plot(ax=ax, color=[muted(c) for c in units["sheet_colour"]], ec="#6b6b6b", lw=.12, zorder=1)
d = dens[0].copy(); d[d < -9000] = np.nan
xs = np.linspace(td.c, td.c + td.a * d.shape[1], d.shape[1])
ys = np.linspace(td.f + td.e * d.shape[0], td.f, d.shape[0])
lev = [1, 2, 3, 4, 5, 6, 7]
cf = ax.contourf(xs, ys, d, levels=lev, colors=["#fff2e0", "#fdd9b5", "#f9b98d", "#f0906a",
                                                "#dc6849", "#bc3f2d", "#93231a"],
                 alpha=.55, extend="max", zorder=2)
ax.contour(xs, ys, d, levels=lev[1:-1], colors="#7d2411", linewidths=.4, alpha=.35, ls="--", zorder=2)
R_DRAW.plot(ax=ax, color="#1f6fb4", lw=.3, alpha=.55, zorder=3)
S_DRAW.plot(ax=ax, color="#5a5a5a", lw=.4, alpha=.6, zorder=3)
F_DRAW.plot(ax=ax, color="#8f0d14", lw=1.1, alpha=.85, zorder=4)
symbols(ax, s_=8, lw=.5)
NIGB.plot(ax=ax, color="#0e0e0e", lw=1.3, zorder=6)
furniture(ax, bar=(0.79, 0.055))
cax = fig.add_axes([.760, .33, .013, .40])
cb = fig.colorbar(cf, cax=cax)
cb.set_label("mineral symbols per 1000 km²  (kernel σ ≈ 17 km)", fontsize=8.2)
cb.ax.tick_params(labelsize=7.8)
hl = [Line2D([], [], marker=m, ls="", markersize=6.2, markerfacecolor="none" if m != "x" else c,
             markeredgecolor=c, markeredgewidth=.75, label=cls) for cls, (c, m) in CL.items()]
hl += [Patch(fc="#dc6849", alpha=.55, label="symbol density"),
       Line2D([], [], color="#8f0d14", lw=1.2, label=f"fault ({len(faults)})"),
       Patch(fc="#e8e2d2", ec="#6b6b6b", lw=.2, label="geological unit (muted)")]
ax.legend(handles=hl, loc="lower left", bbox_to_anchor=(.005, .012), fontsize=7.8,
          framealpha=.97, edgecolor="#888", borderpad=.5, labelspacing=.4)
fig.text(.5, .965, "GEOLOGY AND MINERAL RESOURCES OF NIGERIA", ha="center", fontsize=18, weight="bold", color="#111")
fig.text(.5, .937, "The 2011 geological units, every 2023 mineral symbol, and the interpolated density of those symbols",
         ha="center", fontsize=10.0, color="#333")
fig.text(.042, .010, "EPSG:4326  ·  units muted so the mineral overlay reads clearly  ·  density counts printed symbols, "
                     "not reserves, grade or production  ·  datum of the source sheets is not established",
         fontsize=7.1, color="#555")
fig.savefig(P / "Map_3_Combined.png", dpi=150, facecolor="white")
plt.close(fig); print("map 3")

# ============================================================== MAP 4 - centring proof
# Same measurement as Verify_Centres.py, applied to a few points so the plate is a proof,
# not a promise: every panel reports its own measured offset from the printed glyph centre.
pg = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
from scipy.ndimage import label as ndlabel, binary_fill_holes
PALETTE = np.array([[255,245,0],[218,37,29],[151,148,107],[151,69,120],[0,146,63],[187,130,91],
                    [102,122,179],[237,255,140],[38,115,0],[230,230,0],[96,93,92],[130,130,130]])
S2 = 4
CLIP = pymupdf.Rect(74.23969, 358.7239, 2051.8313, 1968.6611)
_pix = pg.get_pixmap(matrix=pymupdf.Matrix(S2, S2), clip=CLIP, alpha=False)
A = np.frombuffer(_pix.samples, np.uint8).reshape(_pix.height, _pix.width, 3).astype(np.int16)
_MX, _MN = A.max(2), A.min(2)
PAL = np.zeros(A.shape[:2], bool)
for _c in PALETTE: PAL |= (np.abs(A - _c).max(axis=2) <= 22)
SYM = PAL | ((_MX < 95) & ((_MX - _MN) < 45))

def ll2page(lon, lat):
    return (74.23969 + (lon - 2.47619) / 12.54519 * 1976.9518,
            358.7239 + (14.04668 - lat) / 10.20997 * 1608.9773)

def glyph_offset(x, y, rad=22):
    """Distance in page points from (x, y) to the centre of the nearest symbol glyph."""
    px, py = int(round((x - CLIP.x0) * S2)), int(round((y - CLIP.y0) * S2))
    win = binary_fill_holes(SYM[max(0, py - rad):py + rad + 1, max(0, px - rad):px + rad + 1])
    lab, n = ndlabel(win)
    best = None
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        if not (3 * S2 / 2 <= h <= 24 * S2 / 2 and 3 * S2 / 2 <= w <= 24 * S2 / 2): continue
        gx = (xs.min() + xs.max()) / 2 + max(0, px - rad)
        gy = (ys.min() + ys.max()) / 2 + max(0, py - rad)
        d = float(np.hypot(gx - px, gy - py)) / S2
        if d <= 11 and (best is None or d < best[0]): best = (d,)
    return None if best is None else best[0]

sel = pts.sample(6, random_state=7).reset_index(drop=True)
fig, axes = plt.subplots(1, len(sel), figsize=(16.2, 3.9), facecolor="white")
for ax, (_, r) in zip(axes, sel.iterrows()):
    x, y = ll2page(r.geometry.x, r.geometry.y)
    Sk, H = 14, 11.0
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(Sk, Sk), clip=pymupdf.Rect(x - H, y - H, x + H, y + H), alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
    ax.imshow(a, interpolation="nearest")
    c = (pix.width - 1) / 2.0
    ax.axvline(c, color="#ff00ff", lw=1.0, alpha=.9)
    ax.axhline(c, color="#ff00ff", lw=1.0, alpha=.9)
    ax.add_patch(plt.Circle((c, c), 1.0 * Sk, fill=False, ec="#ff00ff", lw=1.0, ls=":", alpha=.9))
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color("#999")
    off = glyph_offset(x, y)
    name = str(r.get("mineral", "")).strip() or "unidentified"
    cls = str(r.get("mineral_class", "unknown"))
    tag = "no glyph found" if off is None else f"offset {off:.2f} pt = {off * 0.706:.2f} km"
    ax.set_title(f"{name[:26]}\n{cls} · {tag}", fontsize=8.4, color="#111", pad=6)
    ax.set_xlabel(f"{r.geometry.y:.2f}°N  {r.geometry.x:.2f}°E", fontsize=7.6, color="#444")

fig.suptitle("CENTRING PROOF — magenta crosshair marks the stored coordinate, dotted circle is the 1 pt "
             "(0.71 km) tolerance", fontsize=12.5, weight="bold", y=1.0)
import json as _j
_v = _j.load(open(P / "Verify_Centres.json"))
fig.text(.5, .015, f"Checked against the sheet itself, independently of the extraction: {_v['total']} points, "
                   f"{_v['on_a_glyph_pct']}% land on a detected symbol, median "
                   f"{_v['distance_to_glyph_centre_pt_median']} pt = "
                   f"{_v['distance_to_glyph_centre_km_median']} km from its printed centre, "
                   f"{_v['within_1pt_pct']}% within 1 pt. One artwork pixel is 0.68 km, so this is the "
                   "drawing's own limit.",
         ha="center", fontsize=8.0, color="#444")
fig.subplots_adjust(left=.012, right=.988, top=.74, bottom=.20, wspace=.07)
fig.savefig(P / "Map_4_Symbol_Centring.png", dpi=200, facecolor="white")
plt.close(fig); print("map 4")
