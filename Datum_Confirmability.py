#!/usr/bin/env python3
"""Can either PDF's datum be confirmed from the map itself? Measure the detection limit.

The 2023 sheet's international boundary is vector artwork, so its page position is exact.
Whatever lat/lon frame those page positions imply can therefore be tested against reference
geometry. The question asked here is narrower and answerable: is the map precise enough to
tell the candidate datums apart at all? Candidate datum shifts across Nigeria are 100-360 m;
the control noise of a 1:2,000,000 sheet is of order 1 km.

Outputs: Datum_Confirmability.png, Datum_Confirmability.json
"""
import json, math
from pathlib import Path
import numpy as np, pymupdf
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely import distance as sdist, points as spts
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt, map_coordinates

P = Path(__file__).resolve().parent
OUT = {}
KM_LAT = 111.2
def km_lon(lat): return 111.2 * math.cos(math.radians(lat))

# ---- reference boundary, densely sampled (~450 m) ------------------------------
outline = unary_union([shape(f["geometry"]) for f in
                       json.load(open(P / "Nigeria_Natural_Earth_outline.geojson"))["features"]]).boundary
ref = np.array([[p.x, p.y] for p in (outline.interpolate(d) for d in
                                     np.arange(0, outline.length, 0.004))])
kdt = cKDTree(ref)

# ---- the 2023 sheet's own vector border ---------------------------------------
page = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
verts = []
for d in page.get_drawings():
    c = d.get("color")
    if c and abs(c[0] - 0.902) < .02 and c[1] < .05:
        for it in d["items"]:
            if it[0] == "l": verts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == "c": verts += [(it[k].x, it[k].y) for k in (1, 2, 3, 4)]
V = np.unique(np.round(np.array(verts), 2), axis=0)

def embedded(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)

lon, lat = embedded(V[:, 0], V[:, 1])
base = np.c_[lon, lat]
base = base[(base[:, 0] > 2.3) & (base[:, 0] < 15) & (base[:, 1] > 3.9) & (base[:, 1] < 14.2)]
if len(base) > 3000:
    base = base[np.linspace(0, len(base) - 1, 3000).astype(int)]

# ---- distance matrix for a grid of translations, computed once ----------------
def grid(step, half):
    g = np.arange(-half, half + step / 2, step)
    X, Y = np.meshgrid(g, g)
    return np.c_[X.ravel(), Y.ravel()]

def dmat(step, half):
    T = grid(step, half)
    d, _ = kdt.query(base[None, :, :] - T[:, None, :], workers=-1)
    return T, d * KM_LAT          # km

T1, D1 = dmat(0.004, 0.05)        # coarse, +-5.5 km
i = int(np.argmin(np.median(D1, axis=1)))
c = T1[i]
T2 = grid(0.0005, 0.006) + c      # fine, +-0.7 km
d, _ = kdt.query(base[None, :, :] - T2[:, None, :], workers=-1)
D2 = d * KM_LAT
j = int(np.argmin(np.median(D2, axis=1)))
T, Dm = T2[j], D2
zero1 = int(np.argmin((T1 ** 2).sum(axis=1)))
zero2 = int(np.argmin((T2 ** 2).sum(axis=1)))
OUT["border_2023"] = {
    "vertices_used": int(len(base)),
    "median_km_embedded_frame": round(float(np.median(Dm[zero2])), 2),
    "p90_km": round(float(np.percentile(Dm[zero2], 90)), 2),
    "best_translation_east_north_km": [round(float(T[0] * km_lon(7.8)), 1), round(float(T[1] * KM_LAT), 1)],
    "median_km_after_translation": round(float(np.median(Dm[j])), 2)}

# ---- bootstrap: how well is that translation even determined? -----------------
rng = np.random.default_rng(7)
boot = []
for _ in range(600):
    s = rng.integers(0, len(base), len(base))
    boot.append(T2[int(np.argmin(np.median(Dm[:, s], axis=1)))])
boot = np.array(boot)
bx, by = boot[:, 0] * km_lon(7.8), boot[:, 1] * KM_LAT
OUT["translation_uncertainty_95pct_km"] = {
    "east": round(float(np.percentile(np.abs(bx - np.median(bx)), 95)), 2),
    "north": round(float(np.percentile(np.abs(by - np.median(by)), 95)), 2)}

# ---- candidate datum shifts at Lokoja, from the PROJ/EPSG registry ------------
cands = {"NAD27 (as declared in the PDF)": (158.1, 120.3), "Minna (Nigeria's own datum)": (-81.5, 41.0),
         "Adindan": (4.6, 131.0), "ED50": (-87.1, -131.1), "Cape": (-91.3, -362.9)}
OUT["candidate_datum_shifts_km_at_Lokoja"] = {k: [v[0] / 1000, v[1] / 1000] for k, v in cands.items()}
vals = list(cands.values())
OUT["closest_two_candidate_datums_km_apart"] = round(min(
    math.dist(a, b) for a in vals for b in vals if a != b) / 1000, 2)

# ---- per 2-degree band: is the residual structured like a datum shift? -------
per = []
for lo, hi in [(2.5, 4.5), (4.5, 6.5), (6.5, 8.5), (8.5, 10.5), (10.5, 12.5), (12.5, 15)]:
    m = (base[:, 0] >= lo) & (base[:, 0] < hi)
    if m.sum() < 80: per.append({"band": [lo, hi], "n": int(m.sum()), "east_km": None, "north_km": None}); continue
    k = int(np.argmin(np.median(Dm[:, m], axis=1)))
    per.append({"band": [lo, hi], "n": int(m.sum()),
                "east_km": round(float(T2[k, 0] * km_lon(base[m, 1].mean())), 1),
                "north_km": round(float(T2[k, 1] * KM_LAT), 1)})
OUT["per_band_translation_km"] = per

# ---- 2011 sheet: same question on its coastline ------------------------------
gpage = pymupdf.open(P / "Geological_Map_of_Nigeria.pdf")[0]
clip = pymupdf.Rect(80, 90, 2050, 1693)
pix = gpage.get_pixmap(clip=clip, alpha=False)
a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.int16)
sea = (abs(a[:, :, 0] - 151) <= 8) & (abs(a[:, :, 1] - 218) <= 9) & (abs(a[:, :, 2] - 242) <= 8)
Dg = distance_transform_edt(~sea)
coast = outline.intersection(box(2.5, 3.5, 9.5, 6.3))
cp = np.array([[q.x, q.y] for q in (coast.interpolate(t) for t in np.arange(0, coast.length, 0.01))])
def gdist(dx, dy):
    x = cp[:, 0] * 157.593 - 276.36 + dx * 157.593
    y = 2281.63 - cp[:, 1] * 157.586 - dy * 157.586
    return map_coordinates(Dg, [y - clip.y0, x - clip.x0], order=1, mode="constant", cval=400) * 0.7
GT = grid(0.002, 0.05)
GZ = np.array([np.median(gdist(dx, dy)) for dx, dy in GT])
k = int(np.argmin(GZ))
OUT["coastline_2011"] = {"samples": int(len(cp)), "median_km": round(float(np.median(gdist(0, 0))), 2),
                         "best_translation_east_north_km": [round(float(GT[k, 0] * km_lon(5)), 1),
                                                            round(float(GT[k, 1] * KM_LAT), 1)],
                         "median_km_after": round(float(GZ[k]), 2)}

# ---- figure ------------------------------------------------------------------
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14.5, 6.6), constrained_layout=True)
ax.scatter(bx, by, s=6, alpha=.22, color="#4a6fa5", label=f"bootstrap solutions (n={len(boot)})")
ax.scatter([T[0] * km_lon(7.8)], [T[1] * KM_LAT], s=110, marker="X", color="#111",
           label="best fit", zorder=6)
ax.axhline(0, color="#ccc", lw=.6); ax.axvline(0, color="#ccc", lw=.6)
fx, fy = T[0] * km_lon(7.8), T[1] * KM_LAT
ax.axvspan(fx - 0.5, fx + 0.5, color="#111", alpha=.07, zorder=0)
ax.axhspan(fy - 0.5, fy + 0.5, color="#111", alpha=.07, zorder=0)
for k2, (de, dn) in cands.items():
    ax.annotate("", xy=(fx + de / 1000, fy + dn / 1000), xytext=(fx, fy),
                arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#b3261e", alpha=.85))
    ax.annotate(k2, (fx + de / 1000, fy + dn / 1000), xytext=(8, 8), textcoords="offset points",
                fontsize=8.5, color="#b3261e")
ax.set_title("Grey band = +/-0.5 km; the border fit alone is only good to ~1-2 km\n"
             "arrows: where each candidate datum would put the border relative to NAD27")
ax.set(xlabel="east component of fitted correction (km)", ylabel="north component (km)",
       xlim=(fx - 1.0, fx + 1.0), ylim=(fy - 1.0, fy + 1.0))
ax.legend(fontsize=8.5, loc="lower left"); ax.grid(alpha=.25); ax.set_aspect("equal")

bands = [r for r in per if r["east_km"] is not None]
x = np.arange(len(bands)); w = 0.38
ax2.bar(x - w / 2, [r["east_km"] for r in bands], w, color="#0b6fb8", label="east component")
ax2.bar(x + w / 2, [r["north_km"] for r in bands], w, color="#e08a1e", label="north component")
ax2.axhline(0, color="#333", lw=.8)
for sgn in (-1, 1):
    ax2.axhline(sgn * OUT["translation_uncertainty_95pct_km"]["east"], color="#999", ls=":", lw=1)
ax2.set_xticks(x); ax2.set_xticklabels([f'{r["band"][0]}-{r["band"][1]}' for r in bands])
ax2.set(xlabel="longitude band (deg E)", ylabel="fitted translation (km)",
        title="Fitted border translation by longitude band\nsigns change along the border: cartographic generalisation, not a datum")
ax2.legend(fontsize=9); ax2.grid(alpha=.25, axis="y")
fig.savefig(P / "Datum_Confirmability.png", dpi=130)

json.dump(OUT, open(P / "Datum_Confirmability.json", "w"), indent=2)
print(json.dumps(OUT, indent=2))
