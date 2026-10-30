#!/usr/bin/env python3
"""Rebuild the 2011 geology units as a true partition of the mapped area.

The first attempt walked the PDF's vector paths. That captured loose filled shapes: one page-sized
rectangle labelled as a unit, legend swatches, shapes that overlap each other, and only 41% of the
country. The sheet is in fact a flat-colour map, so the reliable reading is per pixel:

  1. render the map frame from the PDF,
  2. give every pixel the legend tint it is closest to (the legend table is read from the sheet),
  3. fill text, rules and line work from the neighbouring tint, so no pixel is left unassigned,
  4. name each connected region from the unit code printed inside it,
  5. turn the regions into polygons and clip them to the national boundary.

Because each pixel has exactly one class, the result is a planar partition by construction: no
overlaps, no gaps, one unit at every location. Regions with no printed code are kept and marked
`unresolved` rather than guessed.

Writes Geology_Units_Partition.geojson and Geology_Partition_Report.json.
"""
import json, math
import numpy as np, pandas as pd, pymupdf, geopandas as gpd
import rasterio.features
from rasterio.transform import Affine
from scipy import ndimage
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

from geology_legend import UNIT, unit_name

LEGEND = UNIT

Z = 2.0                                            # render zoom; 0.34 km per pixel
KM_PER_PX = 0.68 / Z
FRAME = pymupdf.Rect(114, 60, 2100, 1680)          # the sheet's map area in page points
TOL = 60                                           # RGB distance accepted as "this tint"
MIN_KM2 = 1.5                                      # smaller regions are absorbed
SIMPLIFY = 0.0002                                  # ~22 m, well below one printed pixel
SMOOTH = 7                                         # median window: removes hatch dots and text


TINT_NAME = {                                     # same code, two printed meanings
    ("MS", (240, 244, 0)): ("Pelitic schist / muscovite schist", "Precambrian"),
    ("MS", (148, 168, 252)): ("Sand, clay and mangrove swamps", "Recent"),
}


def ll(x, y):
    return ((x + 276.36) / 157.593, (2281.63 - y) / 157.586)


# ---------------------------------------------------------------- 1. the sheet's legend
leg = json.load(open("Legend_Colours.json"))
tints = [tuple(r["rgb"]) for r in leg["rows"]]
hex_by_tint = {}
for r in leg["rows"]:
    hex_by_tint.setdefault(tuple(r["rgb"]), set()).add(r["code"])

# a code may be printed in two tints; a tint may carry two codes
tint_codes = {t: sorted(c) for t, c in hex_by_tint.items()}
TINT_LIST = list(tint_codes)                      # the exact order the classifier indexes
unknown_tints = [t for t, c in tint_codes.items() if len(c) > 1]
print(f"legend: {len(tints)} swatches, {len(tint_codes)} tints, "
      f"{sum(len(c) for c in tint_codes.values())} code slots")
print(f"tints that stand for two codes: {unknown_tints}")

# ---------------------------------------------------------------- 2. read the map
page = pymupdf.open("Geological_Map_of_Nigeria.pdf")[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=FRAME, alpha=False)
im = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.int16)
H, W = im.shape[:2]
print(f"map render {W}x{H}  ({KM_PER_PX:.2f} km per pixel)")
# the sheet hatches some fills and prints codes inside them; a median keeps the fill, drops the ink
im = np.stack([ndimage.median_filter(im[:, :, c], size=SMOOTH) for c in range(3)], axis=2)

# The map's own inks, not the legend swatches. The sheet is printed with a colour-management
# shift, so a fill on the map can sit 40-90 RGB units from the swatch that represents it, and
# matching to swatches blurs neighbouring units together. So: find the flat inks the map itself
# uses, and classify against those.
flat = (im >> 3).astype(np.int32)
code5 = (flat[:, :, 0] * 1024 + flat[:, :, 1] * 32 + flat[:, :, 2]).ravel()
vals, counts = np.unique(code5, return_counts=True)
order = np.argsort(-counts)
MAP_TINTS = []
for i in order:
    if counts[i] < 0.0004 * code5.size:          # under ~0.04% of the map is not a fill
        break
    k = int(vals[i])
    rgb = ((k // 1024) * 8 + 4, ((k // 32) % 32) * 8 + 4, (k % 32) * 8 + 4)
    if rgb == (4, 4, 4) or sum(rgb) < 90:        # ink, not fill
        continue
    MAP_TINTS.append(rgb)
print(f"{len(MAP_TINTS)} flat inks found on the map itself, "
      f"covering {counts[order[:len(MAP_TINTS)]].sum() / code5.size * 100:.0f}% of it")

LEG_TINTS = list(tint_codes)
INK_CODES = {}
INK_SWATCH = {}
for i, ink in enumerate(MAP_TINTS):
    ds = sorted((sum(abs(a - b) for a, b in zip(ink, t)), j) for j, t in enumerate(LEG_TINTS))
    d, j = ds[0]
    INK_SWATCH[i] = (LEG_TINTS[j], d)
    INK_CODES[i] = tint_codes[LEG_TINTS[j]] if d <= 90 else []
print("map inks close enough to a legend swatch:",
      sum(1 for i in INK_CODES if INK_CODES[i]), "of", len(MAP_TINTS))

lut_n = 32
lut_rgb = np.array(MAP_TINTS, np.float32)
q = (im >> 3).astype(np.int32)
keys = (q[:, :, 0] * lut_n + q[:, :, 1]) * lut_n + q[:, :, 2]
lut_cls = np.full(lut_n ** 3, -1, np.int16)
lut_dist = np.zeros(lut_n ** 3, np.float32)
for k in range(lut_n ** 3):
    r, g, b = (k // (lut_n * lut_n)) * 8 + 4, ((k // lut_n) % lut_n) * 8 + 4, (k % lut_n) * 8 + 4
    d = np.abs(lut_rgb - np.array([r, g, b], np.float32)).sum(1)
    i = int(d.argmin())
    lut_dist[k] = d[i]
    lut_cls[k] = i if d[i] <= TOL else -1
cls = lut_cls[keys]
print(f"pixels on one of the map's own inks: {(cls >= 0).mean() * 100:.1f}%")

# ---------------------------------------------------------------- 3. no pixel left behind
hole = cls < 0
if hole.any():
    idx = ndimage.distance_transform_edt(hole, return_distances=False, return_indices=True)
    cls = cls[tuple(idx)]
print("every pixel now carries a tint")

# clean the class raster as well: text and rules that survived the median are absorbed by
# whichever tint dominates their neighbourhood
best = np.zeros((H, W), np.float32)
cls_c = np.zeros((H, W), np.int16)
for t in range(len(MAP_TINTS)):
    f = ndimage.uniform_filter((cls == t).astype(np.float32), 5)
    take = f > best
    best[take] = f[take]
    cls_c[take] = t
    del f, take
cls = cls_c
del best
print("class raster cleaned")

# connected regions of one tint
ids = np.zeros((H, W), np.int32)
nxt = 1
regions = []
for t_i, tint in enumerate(MAP_TINTS):
    m = cls == t_i
    if not m.any():
        continue
    lab, n = ndimage.label(m)
    if n == 0:
        continue
    sl = ndimage.find_objects(lab)
    for k in range(1, n + 1):
        s = sl[k - 1]
        h = s[0].stop - s[0].start
        w = s[1].stop - s[1].start
        area_km2 = (lab[s] == k).sum() * (KM_PER_PX ** 2)
        if area_km2 < MIN_KM2:
            continue
        ids[s][lab[s] == k] = nxt
        regions.append({"id": nxt, "tint": tint, "tint_i": t_i, "codes": INK_CODES[t_i],
                        "area_km2": area_km2, "slice": s})
        nxt += 1
print(f"{len(regions)} regions kept")

# ---------------------------------------------------------------- 4. name them from the printed codes
# Every ink on the sheet is a fill printed once in the legend and labelled wherever it appears.
# So: count which unit codes are printed on which ink, and pair each ink with the code that is
# printed on it more than on any other ink, and that appears on no other ink as often (a mutual
# best). One ink, at most one code: a code can never spread to the wrong colour.
raw = [(w[0], w[1], w[2], w[3], w[4].strip().rstrip(",.")) for w in page.get_text("words")]
known = set(LEGEND) | {c for cs in tint_codes.values() for c in cs}
words = list(raw)
for i, a in enumerate(raw):                       # join kerned pairs such as "Q"+"s" or "b"+"G"
    for b_ in raw[i + 1:i + 4]:
        if abs((a[1] + a[3]) / 2 - (b_[1] + b_[3]) / 2) > 2.5:
            continue
        if not (0 <= b_[0] - a[2] <= 4):
            continue
        j = a[4] + b_[4]
        if j in known:
            words.append((a[0], min(a[1], b_[1]), b_[2], max(a[3], b_[3]), j))
            break

votes, ink_tokens = {}, {}
for x0, y0, x1, y1, txt in words:
    if txt not in known:
        continue
    px = int(((x0 + x1) / 2 - FRAME.x0) * Z)
    py = int(((y0 + y1) / 2 - FRAME.y0) * Z)
    if not (0 <= px < W and 0 <= py < H):
        continue
    rid = int(ids[py, px])
    t = int(cls[py, px])
    if rid:
        votes.setdefault(rid, {})
        votes[rid][txt] = votes[rid].get(txt, 0) + 1
        ink_tokens.setdefault(t, {})
        ink_tokens[t][txt] = ink_tokens[t].get(txt, 0) + 1

# mutual-best pairing of ink <-> code
code_total = {}
for t, d in ink_tokens.items():
    for c, n in d.items():
        code_total.setdefault(c, {})[t] = n
best_code = {t: max(d, key=d.get) for t, d in ink_tokens.items() if d}
INK_CODE, INK_HOW = {}, {}
for t, c in best_code.items():
    top_ink_of_code = max(code_total[c], key=code_total[c].get)
    if top_ink_of_code != t:
        continue                                  # that code belongs to another ink more strongly
    INK_CODE[t] = c
    INK_HOW[t] = f"{ink_tokens[t][c]} printed labels of {c} on this ink"
print(f"{len(INK_CODE)} of {len(MAP_TINTS)} inks paired with their printed code")

# inks with no mutual best may still be named from the legend, if the legend gives them one code
for t, tint in enumerate(MAP_TINTS):
    if t in INK_CODE:
        continue
    swatch, d = INK_SWATCH[t]
    codes = tint_codes.get(swatch, [])
    if d <= 60 and len(codes) == 1:
        INK_CODE[t] = codes[0]
        INK_HOW[t] = f"ink matches the legend swatch for {codes[0]} (RGB distance {d:.0f}); no label printed on it"

rows = []
for r in regions:
    own = votes.get(r["id"], {})
    code = INK_CODE.get(r["tint_i"])
    how = INK_HOW.get(r["tint_i"], "this ink is not labelled on the sheet")
    n = own.get(code, 0) if code else 0
    second = ""
    if own:
        order = sorted(own.items(), key=lambda kv: -kv[1])
        if order[0][0] != code:
            second = order[0][0]          # a different code printed inside: say so
    if code is None:
        conf = "low"
    elif n > 0:
        conf = "high"
    elif "printed labels" in how:
        conf = "medium"
    else:
        conf = "low"
    if code and code != "unresolved":
        name, period = LEGEND.get(code, ("Not named in the legend", "unknown"))
        if code in {c for (c, _t) in TINT_NAME}:      # same code, two printed meanings
            swatch = INK_SWATCH[r["tint_i"]][0]
            cands = [(tt, v) for (c, tt), v in TINT_NAME.items() if c == code]
            tt, v = min(cands, key=lambda p: sum(abs(a - b) for a, b in zip(swatch, p[0])))
            name, period = v
    else:
        code, name, period = "unresolved", "Not labelled on the sheet", "unknown"
    if second:
        how += f"; a different code ({second}) is printed inside this region"
    r.update(code=code, votes=n, second=second, how=how, name=name, period=period, conf=conf)
    rows.append(r)

named = sum(1 for r in rows if r["code"] != "unresolved")
print(f"regions named: {named} of {len(rows)}; "
      f"codes used: {len({r['code'] for r in rows})}")

# ---------------------------------------------------------------- 5. polygons
src = ids.astype(np.int32)
transform = Affine(1 / Z, 0, FRAME.x0, 0, 1 / Z, FRAME.y0)
shapes = []
for geom, val in rasterio.features.shapes(src, mask=src > 0, transform=transform, connectivity=4):
    shapes.append((int(val), geom))
print(f"{len(shapes)} polygons from the label raster")

meta = {r["id"]: r for r in rows}
out = []
for rid, geom in shapes:
    m = meta[rid]
    g = Polygon(geom["coordinates"][0], geom["coordinates"][1:]) if geom["type"] == "Polygon" \
        else make_valid(shape(geom))
    if not g.is_valid:
        g = make_valid(g)
    if g.is_empty:
        continue
    if g.geom_type == "MultiPolygon":
        g = max(g.geoms, key=lambda p: p.area)
    pts = [ll(x, y) for x, y in g.exterior.coords]
    poly = Polygon(pts, [[ll(x, y) for x, y in r.coords] for r in g.interiors])
    poly = poly.simplify(SIMPLIFY, preserve_topology=True)
    if poly.is_empty or not poly.is_valid:
        poly = make_valid(poly)
    if poly.is_empty:
        continue
    out.append({"unit_code": m["code"], "unit_name": m["name"], "period": m["period"],
                "sheet_colour": "#%02x%02x%02x" % m["tint"],
                "how_named": m["how"], "name_confidence": m["conf"],
                "label_votes": int(m["votes"]),
                "label_second": m["second"],
                "same_tint_as": ",".join(c for c in m["codes"] if c != m["code"]),
                "geometry": poly})

units = gpd.GeoDataFrame(out, crs=4326)
print(f"{len(units)} polygons before clipping")

# ---------------------------------------------------------------- 6. clip to the country
b = gpd.read_file("Nigeria_Geology_Minerals_4326.gpkg", layer="nigeria_boundary").to_crs(4326)
ng = unary_union(b.geometry.tolist())
units["geometry"] = units.geometry.intersection(ng)
units = units[~units.geometry.is_empty]
units = units.explode(index_parts=False).reset_index(drop=True)
units["area_km2"] = units.to_crs(32632).area / 1e6
units = units[units.area_km2 >= MIN_KM2].reset_index(drop=True)
print(f"{len(units)} polygons after clipping to the boundary")

# ---------------------------------------------------------------- 6b. close what is left
# simplification and the minimum-area filter leave thin holes; each is given to the unit it
# shares the longest edge with, so the layer tiles the country exactly
from shapely import STRtree
rest = ng.difference(unary_union(units.geometry.tolist()))
holes = [p for p in (rest.geoms if hasattr(rest, "geoms") else [rest]) if p.area > 0]
geoms = units.geometry.tolist()
tree = STRtree(geoms)
absorb = {}
for h in holes:
    best, blen = None, 0.0
    for i in tree.query(h, predicate="intersects"):
        ln = geoms[i].boundary.intersection(h.boundary).length
        if ln > blen:
            best, blen = i, ln
    if best is not None:
        absorb.setdefault(best, []).append(h)
if absorb:
    newg = list(units.geometry)
    for i, hs in absorb.items():
        newg[i] = unary_union([newg[i]] + hs)
    units["geometry"] = newg
    units = units[~units.geometry.is_empty].reset_index(drop=True)
    print(f"{sum(len(v) for v in absorb.values())} slivers absorbed into {len(absorb)} neighbours")

# ---------------------------------------------------------------- 7. prove it is a partition
units["area_km2"] = units.to_crs(32632).area / 1e6
u32 = units.to_crs(32632)
union = unary_union(u32.geometry.tolist())
ng32 = b.to_crs(32632).geometry.union_all()
area_sum = u32.area.sum() / 1e6
area_union = union.area / 1e6
gap = ng32.difference(union).area / 1e6
outside = union.difference(ng32).area / 1e6
rep = {
    "method": "per-pixel reading of the printed fills, named by the code printed inside each region",
    "pixels": int(H * W),
    "regions": len(units),
    "codes": int(units.unit_code.nunique()),
    "named_from_printed_code": int((units.unit_code != "unresolved").sum()),
    "unresolved_polygons": int((units.unit_code == "unresolved").sum()),
    "unresolved_km2": round(float(units.loc[units.unit_code == "unresolved", "area_km2"].sum()), 1),
    "nigeria_km2": round(float(ng32.area / 1e6), 1),
    "sum_of_polygons_km2": round(float(area_sum), 1),
    "union_km2": round(float(area_union), 1),
    "overlap_km2": round(float(area_sum - area_union), 2),
    "gap_km2": round(float(gap), 2),
    "outside_country_km2": round(float(outside), 2),
    "coverage_pct": round(float(area_union / (ng32.area / 1e6) * 100), 2),
    "gap_pct": round(float(gap / (ng32.area / 1e6) * 100), 3),
}
print(json.dumps(rep, indent=1))

units.drop(columns=[]).to_file("Geology_Units_Partition.geojson", driver="GeoJSON")
json.dump(rep, open("Geology_Partition_Report.json", "w"), indent=1)
print("written Geology_Units_Partition.geojson")
