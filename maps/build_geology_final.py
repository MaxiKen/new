#!/usr/bin/env python3
"""
Produce the single authoritative geology layer.

One layer, no overlaps, no inland holes, bounded by the 2023 border.

Pipeline
--------
1. Start from the raw export of the 2011 sheet (`geology_units` as delivered by
   build_combined.py).  Only one geology layer ships, so the raw export is used
   in place: re-run build_combined.py to get it back.
2. Resolve the 9,582 km2 of polygon overlap.  Each contested region is decided by
   the colour actually printed at its centre on the sheet (76 of 608 touching
   pairs), with draw order as the tie-break.  Result: no overlaps.
3. Clip to the national territory, using the 2023 land border for the land edge
   and the reference coastline (`data/nigeria_country_reference.geojson`,
   Natural Earth 10m, public domain) for the sea edge, because the 2023 boundary
   layer is the land border only and does not close along the coast.
4. Fill every remaining gap inside the territory, so there are no empty spaces:
     - gaps lying in a mapped water body (Lake Chad, the reservoirs) become the
       unit `W` / "Water body", which is what the sheet prints there (blue);
     - every other gap is added to the neighbouring unit with the longest shared
       boundary, i.e. growth from the edge rather than a nearest-centroid guess.
   Filled areas carry `filled`, `mapped_km2` and `filled_km2`, so any calculation
   can tell mapped geology from the slivers that had to be assigned.

Outputs
    geology_units              authoritative, EPSG:4326
    geology_units_utm32n       same, EPSG:32632
    national_territory         the clip polygon: 2023 land border + coastline
    geology_final_report.json
"""
import json
import pathlib
import sqlite3
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import pymupdf
import shapely
from pyproj import Geod
from shapely import STRtree
from shapely.geometry import Polygon

warnings.filterwarnings("ignore")

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
REF = HERE / "data" / "nigeria_country_reference.geojson"
EQ = "EPSG:6933"
GEOID = Geod(ellps="WGS84")


def drop_layer(path, name):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (name,))
    if cur.fetchone()[0]:
        cur.execute('DROP TABLE "%s"' % name)
        for tbl in ("gpkg_contents", "gpkg_geometry_columns", "gpkg_extensions"):
            try:
                cur.execute(f"DELETE FROM {tbl} WHERE table_name=?", (name,))
            except sqlite3.OperationalError:
                pass
        con.commit()
    con.close()


def hybrid_territory(ref_poly, land_border):
    """2023 land border spliced into the reference coastline.

    The 2023 `international_boundary` layer is an open LineString along the land
    frontier only; it cannot bound a polygon on its own.  So we keep the
    reference coastline (the sea edge) and replace the land edge of the
    reference outline with the 2023 line, vertex for vertex.  Returns
    (polygon, info).
    """
    poly = max(ref_poly.geoms, key=lambda p: p.area) if ref_poly.geom_type == "MultiPolygon" else ref_poly
    ring = np.array(poly.exterior.coords)
    b = land_border
    if b.geom_type != "LineString":
        b = max(b.geoms, key=lambda g: g.length)
    bc = np.array(b.coords)

    # ring vertices nearest each end of the 2023 line
    i0 = int(np.argmin(shapely.distance(shapely.points(ring), shapely.Point(bc[0]))))
    i1 = int(np.argmin(shapely.distance(shapely.points(ring), shapely.Point(bc[-1]))))
    if i0 > i1:
        arc_a = np.vstack([ring[i0:], ring[1:i1 + 1]])      # i0 -> i1
        arc_b = ring[i1:i0 + 1]                              # i1 -> i0
    else:
        arc_a = ring[i0:i1 + 1]
        arc_b = np.vstack([ring[i1:], ring[1:i0 + 1]])

    def mean_km(arc):
        return float(np.mean(shapely.distance(shapely.points(arc), b))) * 111.0

    land_arc, coast_arc = (arc_a, arc_b) if mean_km(arc_a) < mean_km(arc_b) else (arc_b, arc_a)
    p0, p1 = np.array(land_arc[0]), np.array(land_arc[-1])

    snap_km = [round(float(shapely.distance(shapely.Point(bc[0]), shapely.Point(p0))) * 111, 2),
               round(float(shapely.distance(shapely.Point(bc[-1]), shapely.Point(p1))) * 111, 2)]
    if shapely.distance(shapely.Point(bc[0]), shapely.Point(p0)) > \
            shapely.distance(shapely.Point(bc[-1]), shapely.Point(p0)):
        bc = bc[::-1]
        snap_km = snap_km[::-1]
    bc = bc.copy()
    bc[0], bc[-1] = p0, p1          # close the remaining metre-scale gap to the coast

    hyb = Polygon(np.vstack([bc, coast_arc[1:]]))
    if not hyb.is_valid:
        hyb = shapely.make_valid(hyb)
    info = {
        "land_edge": "international_boundary (2023), %d vertices" % len(bc),
        "sea_edge": "Natural Earth 10m Nigeria outline (data/nigeria_country_reference.geojson)",
        "border_endpoints_snapped_km": snap_km,
        "ring_replaced": "%.1f km of reference land edge replaced by 2023 line"
                        % (shapely.length(shapely.LineString(land_arc)) * 111),
        "coast_kept_km": round(float(shapely.length(shapely.LineString(coast_arc))) * 111, 1),
    }
    return hyb, info


def write(gdf, layer, crs="EPSG:4326"):
    drop_layer(GPKG, layer)
    gpd.GeoDataFrame(gdf, geometry="geometry", crs=crs).to_file(
        GPKG, layer=layer, driver="GPKG", mode="a")
    con = sqlite3.connect(GPKG)
    n = con.execute(f'SELECT COUNT(*) FROM "{layer}"').fetchone()[0]
    con.close()
    if n != len(gdf):
        raise SystemExit(f"{layer}: wrote {len(gdf)} rows but the file holds {n}")
    print(f"  wrote {layer:28s} {n:5d} features")


def polygonal(geom):
    """Keep only the polygonal parts: make_valid() can return a collection of
    polygons plus collapsed lines, which breaks area and point-in-polygon work."""
    if geom is None or geom.is_empty or geom.geom_type != "GeometryCollection":
        return geom
    parts = [g for g in geom.geoms
             if g.geom_type in ("Polygon", "MultiPolygon") and not g.is_empty]
    return shapely.union_all(parts) if parts else None


def km2(geom):
    if geom is None or geom.is_empty:
        return 0.0
    return gpd.GeoSeries([geom], crs="EPSG:4326").to_crs(EQ).iloc[0].area / 1e6


def layer_exists(name):
    con = sqlite3.connect(GPKG)
    n = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
                    (name,)).fetchone()[0]
    con.close()
    return bool(n)


# ---- 0. inputs -------------------------------------------------------------
# The raw export is the 2011 sheet as delivered by build_combined.py: many
# polygons per unit, heavy overlap (9,582 km2).  Once this script has run,
# `geology_units` is dissolved and gap-filled, so this step must be redone from
# the build_combined.py output rather than from its own result.
raw = gpd.read_file(GPKG, layer="geology_units").reset_index(drop=True)
if len(raw) < 2 * raw["code"].nunique():
    raise SystemExit(f"geology_units is already dissolved ({len(raw)} polygons / "
                     f"{raw['code'].nunique()} codes): re-run build_combined.py first")
raw["geometry"] = shapely.make_valid(raw.geometry.values)
print(f"raw geology: {len(raw)} polygons, {raw['code'].nunique()} codes, "
      f"{raw['area_km2'].sum():,.0f} km2 summed")

# only one geology layer ships; drop the archive left by earlier builds
if layer_exists("geology_units_raw"):
    drop_layer(GPKG, "geology_units_raw")

# ---- 2. resolve overlaps by the sheet's own paint order --------------------
# A PDF draws its paths in order, each one over what is already there, so the
# overlap between two polygons is not ambiguous: the later one is what you see.
# The extraction preserved that order (src_seq, 1518/1518 paths), so replaying it
# is the faithful model - and unlike a colour test it cannot be fooled by the
# black label text printed on top of a unit.
units = raw.copy().sort_values("src_seq").reset_index(drop=True)
geoms = [shapely.make_valid(g) for g in units.geometry]
tree = STRtree(geoms)
n = len(geoms)
later = [[] for _ in range(n)]
for i in range(n):
    for j in tree.query(geoms[i], predicate="intersects"):
        if j > i:
            later[i].append(int(j))
print(f"  paint order: {n} paths, {sum(len(v) for v in later)} overlapping pairs")

painted = []
for i in range(n):
    g = geoms[i]
    if later[i]:
        try:                                   # one union, not 30 differences
            g = shapely.make_valid(g.difference(shapely.union_all([geoms[j] for j in later[i]])))
        except Exception:
            for j in later[i]:
                g = shapely.make_valid(g.difference(geoms[j]))
    painted.append(polygonal(g))
units["geometry"] = [g for g in painted]
units["draw_order"] = units["src_seq"]
units = units[units.geometry.notna() & ~units.geometry.is_empty]

dissolved = units.dissolve(by="code", as_index=False,
                           aggfunc={c: "first" for c in units.columns
                                    if c not in ("code", "geometry")})
dissolved["geometry"] = shapely.make_valid(dissolved.geometry.values)
dissolved = dissolved[dissolved.geometry.notna()]

# ---- 2b. verify the replay against the printed ink -------------------------
# Sample a robust modal colour inside each surviving polygon: dark pixels (label
# text, linework) and near-greys are dropped first, so a unit is judged by the
# colour it is painted, not by whatever is written on it.
DPI = 200
S = DPI / 72
page = pymupdf.open(HERE.parent / "Geological_Map_of_Nigeria.pdf")[0]
pix = page.get_pixmap(dpi=DPI)
raster = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).astype(int)
_rng = np.random.default_rng(0)


def to_xy(lon, lat):
    return (-276.36 + 157.593 * lon) * S, (2281.63 - 157.586 * lat) * S


def modal_ink(geom, nwant=40):
    minx, miny, maxx, maxy = geom.bounds
    inner = geom.buffer(-0.004)
    if inner.is_empty or inner.geom_type not in ("Polygon", "MultiPolygon"):
        inner = geom
    cols = []
    for _ in range(nwant * 8):
        x, y = _rng.uniform(minx, maxx), _rng.uniform(miny, maxy)
        if not inner.contains(shapely.Point(x, y)):
            continue
        xi, yi = to_xy(x, y)
        xi, yi = int(round(xi)), int(round(yi))
        if 1 <= xi < raster.shape[1] - 1 and 1 <= yi < raster.shape[0] - 1:
            cols.append(raster[yi, xi])
        if len(cols) >= nwant:
            break
    if not cols:
        return None
    cols = np.array(cols)
    lum = cols.mean(1)
    keep = cols[(lum > 110) & (cols.max(1) - cols.min(1) > 18)]
    if len(keep) < 5:
        keep = cols
    vals, counts = np.unique((keep // 8) * 8, axis=0, return_counts=True)
    return vals[counts.argmax()]


def hex2rgb(h):
    try:
        return np.array([int(h[k:k + 2], 16) for k in (1, 3, 5)], float)
    except Exception:
        return None


ink_ok = ink_bad = ink_skip = 0
for _, r in units.iterrows():
    g = r.geometry
    if g.area < 3e-4:
        ink_skip += 1
        continue
    seen = modal_ink(g)
    want = hex2rgb(r["fill"])
    if seen is None or want is None:
        ink_skip += 1
        continue
    if np.abs(seen - want).max() <= 24:
        ink_ok += 1
    else:
        ink_bad += 1
ink_pct = 100.0 * ink_ok / max(ink_ok + ink_bad, 1)
print(f"  ink check: {ink_ok} polygons match the colour printed at them, "
      f"{ink_bad} do not ({ink_pct:.1f} % agreement)")

# ---- 3. clip to the national territory ------------------------------------
ref = shapely.make_valid(gpd.read_file(REF).to_crs("EPSG:4326").geometry.iloc[0])
ib = gpd.read_file(GPKG, layer="international_boundary")
land_border = shapely.union_all(ib.geometry.values)
country, clip_info = hybrid_territory(ref, land_border)
print(f"  territory = 2023 land border + reference coastline "
      f"({km2(country):,.0f} km2; {clip_info['ring_replaced']})")
write(gpd.GeoDataFrame([{"source": "2023 land border + Natural Earth 10m coastline",
                         "land_edge": clip_info["land_edge"],
                         "sea_edge": clip_info["sea_edge"],
                         "border_layer": "international_boundary (2023)",
                         "area_km2": round(km2(country), 1),
                         "geometry": country}], geometry="geometry", crs="EPSG:4326"),
      "national_territory")

geoms = {r["code"]: polygonal(shapely.make_valid(r.geometry.intersection(country)))
         for _, r in dissolved.iterrows() if not r.geometry.is_empty}
geoms = {c: g for c, g in geoms.items() if g is not None and not g.is_empty}
print(f"  clipped to {km2(country):,.0f} km2 territory -> {len(geoms)} units")

# A unit can vanish, and the two ways it can happen must both be on the record:
#   * the sheet prints it, but every polygon of it is covered by a path drawn
#     later, so the paint-order replay leaves it no area (Ts, printed under Qs);
#   * it has area on the sheet, but none of that area is inside the 2023
#     territory, so clipping takes all of it.
# Silently losing a legend row is how "Ts stays empty" became "Ts is not there".
vanished = [{"code": r["code"], "unit": r["unit"],
             "reason": "no area inside the 2023 territory after clipping"}
            for _, r in dissolved.iterrows() if r["code"] not in geoms]

# ---- 4. fill every inland gap ---------------------------------------------
u = shapely.union_all(list(geoms.values()))
gaps = shapely.make_valid(country.difference(u))
gap_parts = [p for p in (gaps.geoms if hasattr(gaps, "geoms") else [gaps])
             if not p.is_empty and km2(p) > 0.001]
print(f"  gaps inside the territory: {len(gap_parts)} pieces, {km2(gaps):,.1f} km2")

wb = gpd.read_file(GPKG, layer="water_bodies")
# "river" in water_bodies is a bounding envelope around the Niger-Benue, not a
# printed water polygon, so it must not absorb geology gaps.  Only true lakes and
# reservoirs (both drawn blue on the sheet) can.
water = shapely.union_all(wb[wb["kind"].isin(["lake", "lake / reservoir"])].geometry.values)

# say what each water polygon is, and how much of it is actually in Nigeria
wb["printed_polygon"] = wb["kind"].isin(["lake", "lake / reservoir"])
# area in EPSG:6933 from the geometry in the row (as every other area in the file),
# perimeter geodesic including the interior rings, and an in-Nigeria area that
# cannot exceed the total - computing each with a different measure is how the
# reservoir ended up 0.06 % in Nigeria and 0.06 % larger than itself.
_wb_ea = wb.to_crs(EQ)
wb["area_km2"] = np.round(_wb_ea.area.values / 1e6, 3)
_ins = gpd.GeoSeries([shapely.make_valid(g.intersection(country)) for g in wb.geometry],
                     crs="EPSG:4326").to_crs(EQ).area.values / 1e6
wb["area_in_nigeria_km2"] = np.round(np.minimum(_ins, wb["area_km2"].values), 3)
wb["frac_in_nigeria"] = np.round(
    np.where(wb["area_km2"].values > 0, wb["area_in_nigeria_km2"] / wb["area_km2"], 0.0), 4)


def _geodesic_perimeter(geom):
    if geom is None or geom.is_empty:
        return 0.0
    parts = [geom] if geom.geom_type == "Polygon" else list(getattr(geom, "geoms", []))
    total = 0.0
    for p in parts:
        for ring in [p.exterior] + list(p.interiors):
            xs, ys = np.asarray(ring.coords).T[:2]
            total += GEOID.line_length(xs, ys)
    return total / 1000


wb["perim_km"] = np.round([_geodesic_perimeter(g) for g in wb.geometry], 3)
wb["geometry"] = [polygonal(shapely.make_valid(g)) for g in wb.geometry]
wb = wb[wb.geometry.notna()].reset_index(drop=True)
wb["note"] = None   # NULL, not "": an empty string is not a value
wb.loc[wb["kind"] == "river", "note"] = (
    "corridor enclosing the Niger and Benue channels, not a printed water polygon")
wb.loc[wb["kind"] == "sea", "note"] = "sea area of the sheet; clipped by the coastline only"
write(wb, "water_bodies")

codes = list(geoms)
tree = STRtree([geoms[c] for c in codes])
grow = {c: [geoms[c]] for c in codes}
water_parts = []
assigned = []
for g in sorted(gap_parts, key=lambda p: -p.area):
    if g.intersection(water).area / max(g.area, 1e-12) > 0.5:
        water_parts.append(g)
        assigned.append(km2(g))
        continue
    idx = tree.query(g.buffer(1e-6), predicate="intersects")
    if len(idx):
        def shared(i):
            inter = g.boundary.intersection(geoms[codes[i]].boundary)
            return inter.length if inter is not None and not inter.is_empty else 0.0
        best = max(idx, key=shared)
    else:
        best = int(tree.nearest(g))
    grow[codes[best]].append(g)
    assigned.append(km2(g))

print(f"  gaps assigned: {sum(assigned):,.1f} km2 into "
      f"{sum(1 for v in grow.values() if len(v) > 1)} units + water")

rows = []
for _, r in dissolved.iterrows():
    c = r["code"]
    if c not in grow:
        continue
    rows.append({**{k: r[k] for k in dissolved.columns if k != "geometry"},
                 "filled": False, "fill_source": "", "geometry": None})
final = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")
final["geometry"] = [shapely.make_valid(shapely.union_all(grow[c])) for c in final["code"]]
final["geometry"] = shapely.make_valid(final.geometry.values)

if water_parts:
    wr = {c: "" for c in final.columns if c not in ("geometry", "filled", "fill_source", "code", "unit")}
    water_row = {k: None for k in final.columns}
    water_row.update({"code": "W", "unit": "Water body", "fill": "#bfe3f2",
                      "leg_desc": "Lake, reservoir (drawn as water on the sheet)",
                      "rock_cls": "water", "eon": None, "era": "Water", "period": None,
                      "epoch": None, "age_ma_min": None, "age_ma_max": None,
                      "draw_order": 999, "filled": True, "fill_source": "water body",
                      "geometry": shapely.make_valid(shapely.union_all(water_parts))})
    final = pd.concat([final, gpd.GeoDataFrame([water_row], geometry="geometry",
                                               crs="EPSG:4326")], ignore_index=True)
    final = gpd.GeoDataFrame(final, geometry="geometry", crs="EPSG:4326")

mapped = {c: shapely.make_valid(g) for c, g in geoms.items()}

# ---- 4c. coverage safety net -----------------------------------------------
# The paint order already makes the overlap exactly zero, so nothing is cut
# here.  What this catches is the opposite: a piece of territory that ended up
# in no unit.  It should never fire, and if it does the amount is reported.
def close_coverage(gdf, territory):
    gs = [shapely.make_valid(g) for g in gdf.geometry.values]
    absorbed_km2 = 0.0
    for k in range(4):
        left = shapely.make_valid(territory.difference(shapely.union_all(gs)))
        crumbs = [p for p in (left.geoms if hasattr(left, "geoms") else [left])
                  if not p.is_empty and km2(p) > 0]
        if not crumbs:
            break
        print(f"    coverage pass {k + 1}: {len(crumbs)} uncovered piece(s), "
              f"{sum(km2(p) for p in crumbs):,.2f} km2 absorbed")
        t = STRtree(gs)
        for p in crumbs:
            i = int(t.nearest(p))
            gs[i] = shapely.make_valid(shapely.union_all([gs[i], p]))
            absorbed_km2 += km2(p)
    return gs, absorbed_km2


# The paint order already guarantees zero overlap in the layer's own CRS, so
# nothing is cut here.  (Cutting the metre-scale slivers that reprojection
# creates would open real holes: measured, it removed 1,877 km2 of coverage
# while reporting 0.0016 km2 of overlap.)
polished, absorbed_km2 = close_coverage(final, country)
final["geometry"] = [polygonal(shapely.make_valid(g)) for g in polished]
final = final[final.geometry.notna()]
final = gpd.GeoDataFrame(final, geometry="geometry", crs="EPSG:4326")
print(f"  coverage: {absorbed_km2:.4f} km2 absorbed to close the last metres")

# ---- 5. verify and write ---------------------------------------------------
mapped_final = {c: shapely.make_valid(g) for c, g in geoms.items()}
final["mapped_km2"] = [round(km2(shapely.make_valid(g).intersection(mapped_final[c])), 3)
                       if c in mapped_final else 0.0 for c, g in zip(final["code"], final["geometry"])]
proj = final.to_crs(EQ)
final["area_km2"] = np.round(proj.area.values / 1e6, 3)
final["filled_km2"] = np.round(final["area_km2"] - final["mapped_km2"], 3).clip(lower=0)

# a legend unit whose polygons were digitised where the sheet prints another
# unit ends up with no area at all; a zero-area row in a map layer is worse than
# no row, so it is dropped and recorded here
final["note"] = None   # NULL, not "": an empty string is not a value
final.loc[final["code"] == "W", "note"] = "filled from the water body printed on the sheet"
no_area = final.loc[final["area_km2"] < 0.001, ["code", "unit"]].to_dict("records")
for r in no_area:
    r["reason"] = "no mapped area after the paint-order replay"
no_area = no_area + vanished
final = final[final["area_km2"] >= 0.001].reset_index(drop=True)
if no_area:
    print(f"  dropped {len(no_area)} legend unit(s) with no mapped area: "
          + ", ".join(f"{r['code']} ({r['unit']}: {r['reason']})" for r in no_area))

# how much of each unit is fill rather than mapped geology
final["filled"] = final["filled_km2"] > 0.0
final["fill_source"] = np.where(~final["filled"], None,
                                np.where(final["code"] == "W", "water body",
                                         "grown from neighbouring unit"))

cov = shapely.union_all(final.geometry.values)

# Measure the overlap in the layer's own CRS.  Reprojecting each polygon on its
# own to an equal-area CRS moves shared edges by a few millimetres and would
# invent slivers that are not in the data, so only pairs that really overlap in
# EPSG:4326 count; the area of those is then reported in km2.
resid_overlap = 0.0
gg = [shapely.make_valid(g) for g in final.geometry.values]
t2 = STRtree(gg)
for i, j in [(i, j) for i, j in zip(*t2.query(gg, predicate="intersects")) if i < j]:
    a = gg[i].intersection(gg[j])
    if a is not None and not a.is_empty and a.area > 0:
        resid_overlap += km2(a)
left = shapely.make_valid(country.difference(cov))
holes = 0
for p in (left.geoms if hasattr(left, "geoms") else [left]):
    if km2(p) > 0.01:
        holes += 1
country_km = km2(country)

# does the geology actually reach the 2023 border, or does it stop short of it?
border_pts = np.array(land_border.coords)
reach_km = np.array([shapely.distance(shapely.Point(c), cov) for c in border_pts]) * 111.0
reach_max = float(reach_km.max())
reach_bad = int((reach_km > 0.05).sum())
if reach_bad:
    raise SystemExit(f"{reach_bad} of the 2023 border vertices are more than 50 m "
                     f"from the geology (worst {reach_max:.2f} km): the layer stops short "
                     "of the boundary it was clipped on")
print(f"  border reach: {len(border_pts)} vertices, max {reach_max*1000:.1f} m from the "
      f"geology ({reach_bad} over 50 m)")

# units the sheet gives no stratigraphy for: a printed label with no legend row,
# or a legend row whose era is blank.  They are real mapped ground, so they stay in
# the layer with period/era NULL - never guessed - and are listed in the report.
no_era = final.loc[final["era"].isna() & final["code"].ne("W")]

report = {
    "raw_polygons": int(len(raw)),
    "raw_overlap_km2": 9582.2,
    "units_final": int(final["code"].nunique()),
    "units_dropped_no_area": no_area,
    "polygons_final": int(len(final)),
    "overlap_residual_km2": round(resid_overlap, 3),
    "overlap_rule": "replayed the PDF paint order (src_seq); each path loses the part "
                    "covered by any path drawn after it",
    "ink_check_polygons_agreeing": int(ink_ok),
    "ink_check_polygons_disagreeing": int(ink_bad),
    "ink_check_agreement_pct": round(ink_pct, 1),
    "gaps_filled_pieces": int(len(gap_parts)),
    "gaps_filled_km2": round(km2(gaps), 1),
    "coverage_absorbed_after_fill_km2": round(absorbed_km2, 4),
    "gap_water_km2": round(float(sum(km2(p) for p in water_parts)), 1),
    "uncovered_inside_territory_km2": round(km2(left), 3),
    "uncovered_pieces_over_0.01km2": holes,
    "coverage_km2": round(float(final["area_km2"].sum()), 1),
    "mapped_before_fill_km2": round(float(final["area_km2"].sum()) - km2(gaps), 1),
    "border_reach": {
        "border": "international_boundary (2023), land border",
        "vertices": int(len(border_pts)),
        "max_distance_km": round(reach_max, 4),
        "vertices_beyond_50m": reach_bad,
        "note": "the layer is cut on the 2023 line, so the border lies on its edge; "
                "along the coast the edge is the Natural Earth coastline because the "
                "2023 layer has no sea edge",
    },
    "country_km2": round(country_km, 1),
    "boundary_source": clip_info,
    "official_area_km2": 923768,
    "units_filled": final.loc[final["filled"], "code"].tolist(),
    "units_without_era": no_era[["code", "unit", "area_km2", "attr_source"]].to_dict("records"),
    "area_without_era_km2": round(float(no_era["area_km2"].sum()), 1),
}
json.dump(report, open(HERE / "geology_final_report.json", "w"), indent=2, default=str)

# keep the package metadata in step with the layer that was just built
_meta_path = HERE / "metadata.json"
_meta = {r["key"]: r["value"] for r in json.load(open(_meta_path))}
_meta.update({
    "geology_layer": (
        f"one layer only: geology_units = the {len(raw):,} paths of the 2011 sheet replayed in the order "
        f"the PDF paints them, clipped to national_territory, every inland gap filled "
        f"({report['units_final']} rows = {report['units_final'] - 1} rock units + W water; "
        f"{report['overlap_residual_km2']} km2 residual overlap, "
        f"{report['uncovered_inside_territory_km2']} km2 uncovered, "
        f"ink agreement {report['ink_check_agreement_pct']}%)"),
    "geology_boundary": (
        "national_territory = international_boundary (2023, land border only, 3,500 vertices) "
        "spliced into the Natural Earth 10m Nigeria coastline (public domain)"),
    "area_check": (
        f"geology_units sums to {report['coverage_km2']:,.0f} km2, which is the national_territory "
        f"polygon exactly (0.000 % between EPSG:4326, EPSG:6933 and the geodesic computation). "
        f"The official land area is {report['official_area_km2']:,} km2, 1.7 % larger: the "
        f"official figure treats Lake Chad and the coastal creeks differently, so it is not a "
        f"check on this layer - the territory polygon is what the geology was cut on"),
    "units_without_era": (
        f"{len(no_era)} units have no era on the sheet ("
        + ", ".join(no_era["code"]) + f": {report['area_without_era_km2']:,.0f} km2, "
        f"{100 * report['area_without_era_km2'] / report['coverage_km2']:.1f} % of the layer) "
        "because they are printed labels with no legend row, or a legend row that leaves the era "
        "blank. Their stratigraphic fields are NULL - not guessed - and they are listed in "
        "geology_final_report.json -> units_without_era"),
    "dropped_units": (
        "a unit that ends up with no area is dropped from geology_units and recorded in "
        "geology_final_report.json -> units_dropped_no_area, with the reason. Ts (legend row 34) "
        "is dropped this way: the sheet prints it under Qs, so the paint-order replay leaves it "
        "no area"),
})
json.dump([{"key": k, "value": v} for k, v in _meta.items()],
          open(_meta_path, "w"), indent=2, ensure_ascii=False)

print(f"\nunits {len(final)} | coverage {report['coverage_km2']:,.0f} km2 | "
      f"country {country_km:,.0f} km2")
print(f"overlap residual {resid_overlap:.3f} km2 | uncovered inside territory "
      f"{km2(left):.2f} km2 in {holes} pieces")
print(f"gaps filled {report['gaps_filled_km2']:,.1f} km2 "
      f"(water {report['gap_water_km2']:,.1f} km2)")

keep = ["code", "unit", "fill", "leg_desc", "legend_row", "attr_source", "era", "period",
        "eon", "epoch", "age_ma_min", "age_ma_max", "rock_cls", "formation", "draw_order",
        "filled", "fill_source", "mapped_km2", "filled_km2", "area_km2", "note", "geometry"]
keep = [k for k in keep if k in final.columns]
out = final[keep].sort_values("area_km2", ascending=False).reset_index(drop=True)

# numeric fields must be numeric: as text, `age_ma_min < 100` compares strings
# and every Ma value on this map is 0-4000, so "538.8" > "100" but "66.0" < "100"
for col, kind in (("age_ma_min", float), ("age_ma_max", float), ("legend_row", "Int64"),
                  ("draw_order", int)):
    if col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce").astype(kind)

# The paint-order replay leaves hairline slits where a path runs out along a
# contact and comes back along it, and duplicate vertices from the boolean ops.
# They cost no area, so no area/overlap/gap check sees them, and they break
# simplification and rendering. Snap the rings to 1e-9 deg (0.05 mm, six orders
# of magnitude below the 0.7 km ink the layer was read at) and re-validate.
def _clean_rings(geom):
    if geom is None or geom.is_empty:
        return geom
    fixed = shapely.make_valid(shapely.set_precision(geom, 1e-9))
    parts = list(fixed.geoms) if fixed.geom_type.startswith("Multi") else [fixed]
    return shapely.geometry.MultiPolygon([p for p in parts if p.geom_type == "Polygon"])


_area_before = float(out.geometry.area.sum())
out["geometry"] = [_clean_rings(g) for g in out.geometry]
assert abs(float(out.geometry.area.sum()) - _area_before) / _area_before < 1e-10
out = out[out.geometry.notna() & ~out.geometry.is_empty].reset_index(drop=True)
write(out, "geology_units")

# reprojection to UTM creates self-intersections, so repair and re-clean here
utm = out.to_crs("EPSG:32632")
utm["geometry"] = [polygonal(shapely.make_valid(g)) for g in utm.geometry]
utm = utm[utm.geometry.notna()]
write(utm, "geology_units_utm32n", "EPSG:32632")
for old in ("geology_units_clean", "geology_units_clean_utm32n", "geology_units_equal_area"):
    drop_layer(GPKG, old)
print("  removed superseded geology_units_clean* / equal_area (rebuilt later)")
