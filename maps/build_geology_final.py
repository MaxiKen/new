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

# ---- 2. resolve overlaps using the printed ink ----------------------------
units = raw.copy()
units["draw_order"] = units.groupby("code").ngroup()      # stable tie-break
dissolved = units.dissolve(by="code", as_index=False,
                           aggfunc={c: "first" for c in units.columns
                                    if c not in ("code", "geometry")})
dissolved["geometry"] = shapely.make_valid(dissolved.geometry.values)

fill_of = dict(zip(dissolved["code"], dissolved["fill"]))
prio = dict(zip(dissolved["code"], dissolved["draw_order"]))

DPI = 200
S = DPI / 72
page = pymupdf.open(HERE.parent / "Geological_Map_of_Nigeria.pdf")[0]
pix = page.get_pixmap(dpi=DPI)
raster = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def ink_at(lon, lat):
    x = (-276.36 + 157.593 * lon) * S
    y = (2281.63 - 157.586 * lat) * S
    xi, yi = int(round(x)), int(round(y))
    if not (2 <= yi < raster.shape[0] - 2 and 2 <= xi < raster.shape[1] - 2):
        return None
    return raster[yi - 2:yi + 3, xi - 2:xi + 3].reshape(-1, 3).mean(0)


def hex2rgb(h):
    try:
        return np.array([int(h[k:k + 2], 16) for k in (1, 3, 5)], float)
    except Exception:
        return None


geoms = {r["code"]: shapely.make_valid(r.geometry) for _, r in dissolved.iterrows()}
ink_decided = 0
for _round in range(4):
    codes = list(geoms)
    proj = {c: shapely.make_valid(gpd.GeoSeries([geoms[c]], crs="EPSG:4326").to_crs(EQ).iloc[0])
            for c in codes}
    tree = STRtree([proj[c] for c in codes])
    pairs = [(i, j) for i, j in zip(*tree.query([proj[c] for c in codes],
                                                predicate="intersects")) if i < j]
    changed = False
    decided = 0
    for i, j in pairs:
        a, b = codes[i], codes[j]
        inter = proj[a].intersection(proj[b])
        if inter.is_empty or inter.area / 1e6 < 0.01:
            continue
        pt = gpd.GeoSeries([inter.representative_point()], crs=EQ).to_crs("EPSG:4326").iloc[0]
        ink = ink_at(pt.x, pt.y)
        winner = None
        if ink is not None:
            ra, rb = hex2rgb(fill_of.get(a, "")), hex2rgb(fill_of.get(b, ""))
            ma = ra is not None and np.abs(ink - ra).max() < 30
            mb = rb is not None and np.abs(ink - rb).max() < 30
            if ma and not mb:
                winner = a
            elif mb and not ma:
                winner = b
        if winner is None:
            winner = a if prio[a] >= prio[b] else b
        else:
            decided += 1
        loser = b if winner == a else a
        reg = shapely.make_valid(gpd.GeoSeries([inter], crs=EQ).to_crs("EPSG:4326").iloc[0])
        try:
            geoms[loser] = shapely.make_valid(shapely.make_valid(geoms[loser]).difference(reg))
            changed = True
        except Exception:
            continue
    ink_decided += decided
    print(f"  overlap pass {_round + 1}: {len(pairs)} touching pairs, {decided} decided by ink")
    if not changed:
        break

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

geoms = {c: shapely.make_valid(g.intersection(country)) for c, g in geoms.items()}
geoms = {c: g for c, g in geoms.items() if not g.is_empty}
print(f"  clipped to {km2(country):,.0f} km2 territory -> {len(geoms)} units")

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
wb["area_in_nigeria_km2"] = [round(km2(shapely.make_valid(g.intersection(country))), 1)
                             for g in wb.geometry]
wb["frac_in_nigeria"] = [round(a / km2(g), 3) if km2(g) else 0.0
                         for a, g in zip(wb["area_in_nigeria_km2"], wb.geometry)]
wb["geometry"] = [polygonal(shapely.make_valid(g)) for g in wb.geometry]
wb = wb[wb.geometry.notna()].reset_index(drop=True)
wb["note"] = ""
wb.loc[wb["kind"] == "river", "note"] = (
    "corridor enclosing the Niger and Benue channels, not a printed water polygon")
wb.loc[wb["kind"] == "sea", "note"] = "sea area of the sheet; clipped by the coastline only"
write(wb, "water_bodies")

codes = list(geoms)
tree = STRtree([geoms[c] for c in codes])
grow = {c: [geoms[c]] for c in codes}
water_parts = []
for g in sorted(gap_parts, key=lambda p: -p.area):
    if g.intersection(water).area / max(g.area, 1e-12) > 0.5:
        water_parts.append(g)
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

rows = []
for _, r in dissolved.iterrows():
    c = r["code"]
    if c not in grow:
        continue
    rows.append({**{k: r[k] for k in dissolved.columns if k not in ("geometry", "draw_order")},
                 "draw_order": prio[c], "filled": False, "fill_source": "", "geometry": None})
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

# ---- 4c. polish: exact zero overlap, exact zero gap -----------------------
def polish(gdf, territory):
    """Remove the last sliver crumbs left by floating-point geometry ops."""
    gs = [shapely.make_valid(g) for g in gdf.geometry.values]
    order = gdf["draw_order"].tolist()
    cut_km2 = 0.0
    for _ in range(4):
        t = STRtree(gs)
        pairs = [(i, j) for i, j in zip(*t.query(gs, predicate="intersects")) if i < j]
        touched = False
        for i, j in pairs:
            inter = gs[i].intersection(gs[j])
            if inter.is_empty or km2(inter) <= 0:
                continue
            loser = j if order[i] <= order[j] else i        # the later draw loses
            gs[loser] = shapely.make_valid(gs[loser].difference(inter))
            cut_km2 += km2(inter)
            touched = True
        if not touched:
            break
    absorbed_km2 = 0.0
    for _ in range(4):
        left = shapely.make_valid(territory.difference(shapely.union_all(gs)))
        crumbs = [p for p in (left.geoms if hasattr(left, "geoms") else [left])
                  if not p.is_empty and km2(p) > 0]
        if not crumbs:
            break
        t = STRtree(gs)
        for p in crumbs:
            i = int(t.nearest(p))
            gs[i] = shapely.make_valid(shapely.union_all([gs[i], p]))
            absorbed_km2 += km2(p)
    return gs, cut_km2, absorbed_km2


polished, cut_km2, absorbed_km2 = polish(final, country)
final["geometry"] = [polygonal(shapely.make_valid(g)) for g in polished]
final = final[final.geometry.notna()]
final = gpd.GeoDataFrame(final, geometry="geometry", crs="EPSG:4326")
print(f"  polish: {cut_km2:.4f} km2 residual overlap cut, "
      f"{absorbed_km2:.4f} km2 of crumbs absorbed")

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
final["note"] = ""
final.loc[final["code"] == "W", "note"] = "filled from the water body printed on the sheet"
no_area = final.loc[final["area_km2"] < 0.001, ["code", "unit"]].to_dict("records")
final = final[final["area_km2"] >= 0.001].reset_index(drop=True)
if no_area:
    print(f"  dropped {len(no_area)} legend unit(s) with no mapped area: "
          + ", ".join(f"{r['code']} ({r['unit']})" for r in no_area))

# how much of each unit is fill rather than mapped geology
final["filled"] = final["filled_km2"] > 0.0
final["fill_source"] = np.where(~final["filled"], "",
                                np.where(final["code"] == "W", "water body",
                                         "grown from neighbouring unit"))

cov = shapely.union_all(final.geometry.values)
resid_overlap = 0.0
gg = shapely.make_valid(proj.geometry.values)
t2 = STRtree(gg)
for i, j in [(i, j) for i, j in zip(*t2.query(gg, predicate="intersects")) if i < j]:
    a = gg[i].intersection(gg[j])
    if not a.is_empty:
        resid_overlap += a.area / 1e6
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

report = {
    "raw_polygons": int(len(raw)),
    "raw_overlap_km2": 9582.2,
    "units_final": int(final["code"].nunique()),
    "units_dropped_no_area": no_area,
    "polygons_final": int(len(final)),
    "overlap_residual_km2": round(resid_overlap, 3),
    "ink_decided_pairs": int(ink_decided),
    "gaps_filled_pieces": int(len(gap_parts)),
    "gaps_filled_km2": round(km2(gaps), 1),
    "polish_overlap_cut_km2": round(cut_km2, 4),
    "polish_crumbs_absorbed_km2": round(absorbed_km2, 4),
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
}
json.dump(report, open(HERE / "geology_final_report.json", "w"), indent=2, default=str)

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
write(out, "geology_units")

# reprojection to UTM creates self-intersections, so repair and re-clean here
utm = out.to_crs("EPSG:32632")
utm["geometry"] = [polygonal(shapely.make_valid(g)) for g in utm.geometry]
utm = utm[utm.geometry.notna()]
write(utm, "geology_units_utm32n", "EPSG:32632")
for old in ("geology_units_clean", "geology_units_clean_utm32n", "geology_units_equal_area"):
    drop_layer(GPKG, old)
print("  removed superseded geology_units_clean* / equal_area (rebuilt later)")
