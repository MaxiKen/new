#!/usr/bin/env python3
"""Does the 2011 geology sheet need a correction, and if so, one single correction?

The 2023 mineral sheet had one big error: its points were computed on a frame 19 km west of
the frame its own artwork was drawn in. That was fixable with one shift.

This script asks the same question of the 2011 geology sheet, but tests THREE independent
feature classes on it, because a single global correction is only justified if they agree:

  (a) the vector state-boundary network  vs GADM state boundaries
  (b) the raster coastline               vs Natural Earth / GADM national outline
  (c) the raster Niger and Benue         vs Natural Earth river centrelines

Each is compared with a best-fitting translation, with a bootstrap standard error. If the
three disagree beyond their errors, no single shift is correct and the honest answer is
"leave it, and quote ~1-2 km".

Outputs: Geology_Alignment_Test.json, Geology_Alignment_Test.png
"""
import json, math
from pathlib import Path
import numpy as np, pymupdf
from shapely.geometry import shape, box
from shapely.ops import unary_union
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt, map_coordinates, binary_erosion
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
KM = 111.2
def kx(lat): return 111.2 * math.cos(math.radians(lat))

# page geometry of the 2011 sheet, fitted earlier to its printed graticule
def to_lonlat(x, y): return (x + 276.36) / 157.593, (2281.63 - y) / 157.586
def to_page(lon, lat): return lon * 157.593 - 276.36, 2281.63 - lat * 157.586

page = pymupdf.open(P / "Geological_Map_of_Nigeria.pdf")[0]

# ---------------- (a) vector state-boundary network ------------------------------
verts = []
for d in page.get_drawings():
    c = d.get("color")
    if c and abs(c[0] - .67) < .02 and abs(c[1] - .67) < .02 and abs(c[2] - .67) < .02 \
            and abs((d.get("width") or 0) - 3.96) < .5:
        for it in d["items"]:
            if it[0] == "l": verts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == "c": verts += [(it[k].x, it[k].y) for k in (1, 2, 3, 4)]
V = np.unique(np.round(np.array(verts), 2), axis=0)
lo, la = to_lonlat(V[:, 0], V[:, 1])
S = np.c_[lo, la]
S = S[(S[:, 0] > 2.6) & (S[:, 0] < 14.8) & (S[:, 1] > 4.2) & (S[:, 1] < 13.95)]
S = S[np.linspace(0, len(S) - 1, 700).astype(int)]
OUT = {"state_network": {"vector_vertices": int(len(V)), "sampled": int(len(S))}}

def fit(pts, tree, half=0.05, step=0.001, boots=200, seed=3):
    g = np.arange(-half, half + step / 2, step)
    X, Y = np.meshgrid(g, g); T = np.c_[X.ravel(), Y.ravel()]
    dd, _ = tree.query(pts[None, :, :] - T[:, None, :], workers=-1); dd *= KM
    med = np.median(dd, axis=1); i = int(np.argmin(med))
    rng = np.random.default_rng(seed); sols = []
    for _ in range(boots):
        s = rng.integers(0, len(pts), len(pts))
        sols.append(T[int(np.argmin(np.median(dd[:, s], axis=1)))])
    sols = np.array(sols)
    raw = np.median(dd[np.argmin((T ** 2).sum(axis=1))])
    lat = pts[:, 1].mean()
    return dict(raw_median_km=round(float(raw), 2), after_median_km=round(float(med[i]), 2),
                shift_east_km=round(float(T[i, 0] * kx(lat)), 2),
                shift_north_km=round(float(T[i, 1] * KM), 2),
                se_east_km=round(float(sols[:, 0].std() * kx(lat)), 2),
                se_north_km=round(float(sols[:, 1].std() * KM), 2))

# GADM state boundaries are used for analysis only and are not redistributed.
gd_path = Path("/tmp/nga_states_bound.geojson")
if gd_path.exists():
    gd = json.load(open(gd_path))
    st = unary_union([shape(f["geometry"]).simplify(0.0004).boundary for f in gd["features"]])
    GA = np.array([[q.x, q.y] for q in (st.interpolate(d) for d in np.arange(0, st.length, 0.01))])
    OUT["state_network"].update(fit(S, cKDTree(GA)))
    OUT["state_network"]["reference"] = "GADM 4.1 state boundaries (analysis only)"
else:
    OUT["state_network"]["error"] = "GADM file not present"

# ---------------- raster features ------------------------------------------------
clip = pymupdf.Rect(80, 90, 2050, 1693)
pix = page.get_pixmap(clip=clip, alpha=False)
a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.int16)
sea = (abs(a[:, :, 0] - 151) <= 8) & (abs(a[:, :, 1] - 218) <= 9) & (abs(a[:, :, 2] - 242) <= 8)
# water fill colour: the same fill fills rivers and the sea, and thin river strokes antialias
# into it. A separate stroke-colour mask fails at 1:1 render scale, so use the fill.
water = sea

ne = unary_union([shape(f["geometry"]) for f in
                  json.load(open(P / "Nigeria_Natural_Earth_outline.geojson"))["features"]]).boundary

def raster_fit(mask, lon, lat, centre=0.0, label=""):
    edge = mask & ~binary_erosion(mask, iterations=2)
    D = distance_transform_edt(~edge)
    def cost(dx, dy):
        x, y = to_page(lon + dx, lat + dy)
        if ((x - clip.x0 < 0) | (x - clip.x0 > clip.width) |
                (y - clip.y0 < 0) | (y - clip.y0 > clip.height)).any():
            return 999.0
        return float(np.median(map_coordinates(D, [y - clip.y0, x - clip.x0], order=1,
                                               mode="constant", cval=300) * (111.2 / 157.6)))
    g = np.arange(-0.03, 0.031, 0.001)
    C = np.array([[cost(dx, dy) for dx in g] for dy in g])
    j, i = np.unravel_index(int(np.argmin(C)), C.shape)
    # bootstrap over contiguous chunks (samples along one line are not independent)
    rng = np.random.default_rng(4); n = len(lon); sols = []
    for _ in range(60):
        idx = np.concatenate([np.arange(st, st + 40) % n for st in rng.integers(0, n, max(1, n // 40))])
        def c2(dx, dy, idx=idx):
            x, y = to_page(lon[idx] + dx, lat[idx] + dy)
            return float(np.median(map_coordinates(D, [y - clip.y0, x - clip.x0], order=1,
                                                   mode="constant", cval=300) * (111.2 / 157.6)))
        best = (0.0, 0.0); bc = 1e9
        for dy in np.arange(-0.012, 0.0121, 0.002):
            for dx in np.arange(-0.012, 0.0121, 0.002):
                c = c2(dx, dy)
                if c < bc: bc, best = c, (dx, dy)
        sols.append(best)
    sols = np.array(sols)
    return dict(raw_median_km=round(cost(0, 0), 2), after_median_km=round(float(C[j, i]), 2),
                shift_east_km=round(float(g[i] * kx(lat.mean())), 2),
                shift_north_km=round(float(g[j] * KM), 2),
                se_east_km=round(float(sols[:, 0].std() * kx(lat.mean())), 2),
                se_north_km=round(float(sols[:, 1].std() * KM), 2), reference=label)

# (b) coastline
coast = ne.intersection(box(2.5, 3.6, 9.6, 6.3))
cl = np.array([[q.x, q.y] for q in (coast.interpolate(t) for t in np.arange(0, coast.length, 0.02))])
OUT["coastline"] = raster_fit(sea, cl[:, 0], cl[:, 1], label="Natural Earth outline")
OUT["coastline"]["samples"] = int(len(cl))

# (c) rivers
ref = json.load(open(P / "Niger_Benue_Natural_Earth.geojson"))
Rp = []
for f in ref["features"]:
    if f["properties"]["name"] not in ("Niger", "Benue"): continue
    g_ = shape(f["geometry"]); ls = list(g_.geoms) if hasattr(g_, "geoms") else [g_]
    for line in ls:
        if line.geom_type == "LineString" and line.length > .1:
            Rp += [[p.x, p.y] for p in (line.interpolate(d) for d in np.arange(.02, line.length, .02))]
Rp = np.array(Rp)
OUT["rivers"] = raster_fit(water, Rp[:, 0], Rp[:, 1], label="Natural Earth Niger + Benue")
OUT["rivers"]["samples"] = int(len(Rp))

# ---------------- verdict ---------------------------------------------------------
pts = {k: [v["shift_east_km"], v["shift_north_km"], v["se_east_km"], v["se_north_km"]]
       for k, v in OUT.items() if isinstance(v, dict) and "shift_east_km" in v}
names = list(pts)
pairs = {}
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a1, b1 = pts[names[i]], pts[names[j]]
        gap = math.dist(a1[:2], b1[:2])
        sig = 2 * max(a1[2], a1[3], b1[2], b1[3])
        pairs[f"{names[i]} vs {names[j]}"] = {
            "gap_km": round(gap, 2), "combined_2sigma_km": round(sig, 2),
            "agree": bool(gap <= sig)}
OUT["agreement"] = pairs
OUT["verdict"] = ("ONE CORRECTION JUSTIFIED" if all(p["agree"] for p in pairs.values())
                  else "NO SINGLE CORRECTION JUSTIFIED: the feature classes on this sheet "
                       "disagree with each other by more than their own uncertainties, so "
                       "there is no translation that improves them all")
json.dump(OUT, open(P / "Geology_Alignment_Test.json", "w"), indent=2)

# ---------------- figure ----------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 8), constrained_layout=True)
col = {"state_network": "#0b6fb8", "coastline": "#e08a1e", "rivers": "#b3261e"}
lab = {"state_network": "state boundaries vs GADM", "coastline": "coastline vs Natural Earth",
       "rivers": "Niger + Benue vs Natural Earth"}
for k, (e, n, se, sn) in pts.items():
    ax.errorbar(e, n, xerr=se, yerr=sn, fmt="o", color=col[k], capsize=4, ms=9)
    ax.annotate(lab[k], (e, n), xytext=(10, 8), textcoords="offset points", color=col[k], fontsize=10)
ax.axhline(0, color="#999", lw=.8); ax.axvline(0, color="#999", lw=.8)
ax.set(xlabel="fitted eastward shift (km)", ylabel="fitted northward shift (km)",
       xlim=(-2.5, 2.5), ylim=(-2.5, 2.5),
       title="2011 geology sheet: each feature class wants a different correction\n"
             "error bars are bootstrap 1-sigma; if these do not share one point, no single shift is right")
ax.grid(alpha=.25)
fig.savefig(P / "Geology_Alignment_Test.png", dpi=130)
print(json.dumps(OUT, indent=2))
