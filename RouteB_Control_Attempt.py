#!/usr/bin/env python3
"""Route B, executed as far as the open data allows.

Question: can the datum of either sheet be confirmed from freely available online data?

We bring in two independent national references and one independent test line set:

  * Natural Earth 1:10m Nigeria outline (repo copy).
  * GADM state boundaries for Nigeria (external, used for analysis only - GADM licence is
    academic/non-commercial and the data are NOT redistributed in this repository; see
    RouteB_Report.md for the source and licence).
  * The 2023 sheet's own vector international boundary, whose page coordinates are exact
    because it is vector, not raster.

If the two references already disagree with each other by more than a datum shift, then no
amount of fitting can identify a datum from them. That is what is measured here.

Requires a GADM file at /tmp/nga_states_bound.geojson (see RouteB_Report.md, do not commit it).
Outputs: RouteB_Control_Attempt.json, RouteB_Control_Attempt.png
"""
import json, math, os
from pathlib import Path
import numpy as np, pymupdf
from shapely.geometry import shape
from shapely.ops import unary_union
from scipy.spatial import cKDTree
from pyproj import CRS
from pyproj.transformer import TransformerGroup
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
OUT = {}
KM = 111.2
def kx(lat): return 111.2 * math.cos(math.radians(lat))

def sample(geom, step):
    return np.array([[q.x, q.y] for q in (geom.interpolate(d) for d in np.arange(0, geom.length, step))])

# ---------- references ---------------------------------------------------------
ne = unary_union([shape(f["geometry"]) for f in
                  json.load(open(P / "Nigeria_Natural_Earth_outline.geojson"))["features"]]).boundary
NE = sample(ne, 0.01)
gadm_path = Path("/tmp/nga_states_bound.geojson")
GADM = None
if gadm_path.exists():
    gd = json.load(open(gadm_path))
    gadm = unary_union([shape(f["geometry"]).simplify(0.0005) for f in gd["features"]]).boundary
    GADM = sample(gadm, 0.01)

# reference vs reference
d,_ = cKDTree(GADM).query(NE); d1 = d * KM
d,_ = cKDTree(NE).query(GADM); d2 = d * KM
OUT["reference_disagreement"] = {
    "natural_earth_vs_gadm_km": {"median": round(float(np.median(d1)), 2),
                                 "p90": round(float(np.percentile(d1, 90)), 2),
                                 "other_direction_median": round(float(np.median(d2)), 2),
                                 "other_direction_p90": round(float(np.percentile(d2, 90)), 2)},
    "note": "two independent national outlines disagree by ~1 km: that is the floor any fit inherits"}

# ---------- the sheet's exact vector border ------------------------------------
page = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
def embedded(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)
verts = []
for d in page.get_drawings():
    c = d.get("color")
    if c and abs(c[0] - 0.902) < .02 and c[1] < .05:
        for it in d["items"]:
            if it[0] == "l": verts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == "c": verts += [(it[k].x, it[k].y) for k in (1, 2, 3, 4)]
V = np.unique(np.round(np.array(verts), 2), axis=0)
lon, lat = embedded(V[:, 0], V[:, 1])
B = np.c_[lon, lat]
B = B[(B[:, 0] > 2.3) & (B[:, 0] < 15) & (B[:, 1] > 3.9) & (B[:, 1] < 14.2)]
if len(B) > 1200:
    B = B[np.linspace(0, len(B) - 1, 1200).astype(int)]

def fit_translation(pts, tree, step=0.001, half=0.02, boots=300, seed=1):
    g = np.arange(-half, half + step / 2, step)
    X, Y = np.meshgrid(g, g); T = np.c_[X.ravel(), Y.ravel()]
    dd, _ = cKDTree(tree).query(pts[None, :, :] - T[:, None, :], workers=-1)
    dd = dd * KM
    i = int(np.argmin(np.median(dd, axis=1)))
    rng = np.random.default_rng(seed)
    sols = []
    for _ in range(boots):
        s = rng.integers(0, len(pts), len(pts))
        sols.append(T[int(np.argmin(np.median(dd[:, s], axis=1)))])
    sols = np.array(sols)
    se = sols.std(axis=0)
    return T[i], np.median(dd[i]), se

for label, ref, tree in [("natural earth", NE, NE), ("gadm", GADM, GADM)]:
    if tree is None: continue
    d,_ = cKDTree(tree).query(B); d = d * KM
    t, med, se = fit_translation(B, tree)
    OUT.setdefault("sheet_border_2023_vs", {})[label] = {
        "median_km": round(float(np.median(d)), 2),
        "p90_km": round(float(np.percentile(d, 90)), 2),
        "best_translation_km": [round(float(t[0] * kx(7.8)), 2), round(float(t[1] * KM), 2)],
        "median_after_km": round(float(med), 2),
        "bootstrap_se_km": [round(float(se[0] * kx(7.8)), 2), round(float(se[1] * KM), 2)],
        "minimum_detectable_shift_km": round(float(2 * max(se[0] * kx(7.8), se[1] * KM)), 2)}

# ---------- how big is a datum shift here? ------------------------------------
def shift(epsg, lo, la):
    tg = TransformerGroup(CRS.from_epsg(epsg), CRS.from_epsg(4326), always_xy=True)
    c = [t for t in tg.transformers if t.area_of_use and t.accuracy
         and t.area_of_use.west <= lo <= t.area_of_use.east
         and t.area_of_use.south <= la <= t.area_of_use.north]
    if not c: return None
    t = min(c, key=lambda q: q.accuracy)
    x, y = t.transform(lo, la)
    return (x - lo) * kx(la) * 1000, (y - la) * KM * 1000, t.accuracy

fields = {}
for name, epsg in [("Minna (EPSG:4263)", 4263), ("NAD27 (EPSG:4267)", 4267)]:
    rows = []
    for la in np.arange(4, 14.01, 1.0):
        for lo in np.arange(3, 15.01, 1.0):
            s = shift(epsg, lo, la)
            if s: rows.append((lo, la, s[0], s[1], s[2]))
    F = np.array(rows); fields[name] = F
    mag = np.hypot(F[:, 2], F[:, 3]) if len(F) else np.array([np.nan])
    OUT.setdefault("datum_shift_field", {})[name] = {
        "grid_points_with_operation": int(len(F)),
        "median_m": round(float(np.nanmedian(mag)), 0) if len(F) else None,
        "max_m": round(float(np.nanmax(mag)), 0) if len(F) else None,
        "median_operation_accuracy_m": round(float(np.median(F[:, 4])), 1) if len(F) else None}

datum_max = max((v["max_m"] or 0) for v in OUT["datum_shift_field"].values()) / 1000
det = min(v["minimum_detectable_shift_km"] for v in OUT["sheet_border_2023_vs"].values())
OUT["verdict"] = {
    "largest_candidate_datum_shift_km": round(datum_max, 3),
    "best_detectable_shift_km": det,
    "reference_self_disagreement_km": (OUT["reference_disagreement"]["natural_earth_vs_gadm_km"]["median"]
                                       if GADM is not None else None),
    "ratio_detection_to_signal": round(det / datum_max, 1) if datum_max else None,
    "result": "NOT SEPARABLE. The largest candidate datum shift in Nigeria (0.11 km) is smaller "
              "than the smallest offset this border can resolve (0.16 km, against GADM), and "
              "the two independent references disagree with each other by 0.85 km. Any datum "
              "identified by fitting these data would be an artefact of the reference choice."}

# ---------- figure -------------------------------------------------------------
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14.5, 6.2), constrained_layout=True)
bars = []
if GADM is not None:
    bars.append(("Natural Earth vs GADM\n(references disagree)", OUT["reference_disagreement"]["natural_earth_vs_gadm_km"]["median"]))
bars += [("2023 sheet border vs\nNatural Earth", OUT["sheet_border_2023_vs"]["natural earth"]["median_km"])]
if GADM is not None:
    bars.append(("2023 sheet border vs\nGADM", OUT["sheet_border_2023_vs"]["gadm"]["median_km"]))
bars += [
        ("Minna->WGS 84\n(largest datum shift)", OUT["datum_shift_field"]["Minna (EPSG:4263)"]["max_m"] / 1000),
        ("best shift this fit\ncould detect", det)]
ax.barh([b[0] for b in bars], [b[1] for b in bars], color=["#6b7280", "#0b6fb8", "#0b6fb8", "#b3261e", "#111"])
for i, (_, v) in enumerate(bars): ax.text(v + .02, i, f"{v:.2f} km", va="center", fontsize=9)
ax.set(xlabel="median / max offset (km)", title="Every other error source is larger than the datum effect\nthe sheet's residual is 4-10x, the reference disagreement 8x")
ax.grid(alpha=.25, axis="x"); ax.invert_yaxis()

F = fields["Minna (EPSG:4263)"]
if len(F):
    mag = np.hypot(F[:, 2], F[:, 3])
    K = 30.0                      # arrows drawn 30x true length, for visibility
    u = F[:, 2] / 1000 / (KM * np.cos(np.radians(F[:, 1]))) * K
    v = F[:, 3] / 1000 / KM * K
    ax2.set_aspect(1 / math.cos(math.radians(9)))
    q = ax2.quiver(F[:, 0], F[:, 1], u, v, mag, cmap="viridis", width=.005)
    cb = fig.colorbar(q, ax=ax2, label="displacement (m)")
    cb.set_ticks([60, 80, 100, 110])
ax2.set(xlabel="Longitude (deg E)", ylabel="Latitude (deg N)",
        title="Minna -> WGS 84 across Nigeria (EPSG operation via PROJ)\n"
              "arrows drawn 30x true length; the whole country moves 60-112 m")
ax2.grid(alpha=.25)
fig.savefig(P / "RouteB_Control_Attempt.png", dpi=130)
json.dump(OUT, open(P / "RouteB_Control_Attempt.json", "w"), indent=2)
print(json.dumps(OUT, indent=2))
