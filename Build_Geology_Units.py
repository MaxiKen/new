#!/usr/bin/env python3
"""Ship the 97-unit geology layer, not a thousand traced fragments.

The repository holds three readings of the same 2011 sheet:

  * ``Geology_Bodies.geojson``        1,552 bodies traced body by body (rejected: unusable
                                      as a map — every label becomes a hole, every road a seam)
  * ``Rebuild_Geology_Units.py``      5,539 regions read per pixel from the rendered sheet
                                      (rejected: same problem, one class per pixel)
  * ``data/geology/geology_units_main.gpkg``
                                      97 map units — one polygon set per legend entry, the way
                                      the sheet itself is drawn and the way the legend reads

This script takes the third and makes it the shipped layer. It does not re-trace anything: the
source is the dissolved vector reading of the sheet, already clipped to the national territory.
What it adds is the housekeeping a 97-unit layer needs to be usable:

  1. validate every geometry (GEOS-valid, polygonal only, no empty)
  2. merge each part smaller than MIN_PART_KM2 into the neighbour it shares the longest edge with,
     so a unit is a patchwork of real outcrops rather than of specks
  3. close pinhole gaps between units (ground inside Nigeria claimed by nobody)
  4. give every row the four fields the rest of the pipeline expects — unit_code, unit_name,
     period, sheet_colour — and say how each name was decided

Writes Geology_Units.geojson and Geology_Units_Report.json.

Run:  python3 Build_Geology_Units.py
"""
import json
from collections import defaultdict

import geopandas as gpd
import numpy as np
from shapely import STRtree
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

SRC = "data/geology/geology_units_main.gpkg"
BOUNDARY = "Nigeria_Natural_Earth_outline.geojson"
OUT = "Geology_Units.geojson"
REPORT = "Geology_Units_Report.json"

MIN_PART_KM2 = 0.25        # a part smaller than this is a speck, not an outcrop
HOLE_KM2 = 0.002           # a gap smaller than this is rounding
CRS_AEQD = "+proj=aea +lat_1=4 +lat_2=14 +lat_0=9 +lon_0=8 +datum=WGS84 +units=m +no_defs"

# the six codes the sheet prints but its legend never lists: keep them, mark them
LOW_CONFIDENCE = {"OGp", "W", "Gdss", "s", "Gmsh", "BCT"}


def polygonal(g):
    """any geometry -> polygons only (make_valid can hand back collections)"""
    if g is None or g.is_empty:
        return None
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    ps = parts(g)
    if not ps:
        return None
    return MultiPolygon(ps) if len(ps) > 1 else ps[0]


def parts(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    if g.geom_type == "MultiPolygon":
        return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def clean(g):
    """Repair without inventing ground.

    A geometry that is valid in lon/lat can turn invalid when it is rotated into an equal-area
    projection (thin rings meet at a point). buffer(0) fixes exactly that -- measured area change
    is under 0.0001% -- whereas make_valid on the projected shape can return a collection with no
    polygons left at all, which is how three units once disappeared from this layer.
    """
    if g is None or g.is_empty:
        return None
    if g.is_valid:
        return polygonal(g)
    a0 = g.area
    for cand in (g.buffer(0), make_valid(g)):
        c = polygonal(cand)
        if c is None or c.is_empty:
            continue
        if a0 == 0 or abs(c.area - a0) <= max(1e-9, 0.01 * a0):
            return c
    return None


def safe_union(*geoms):
    """union that repairs its inputs first: reprojection and buffer(0) leave thin rings that make
    GEOS throw a side-location conflict"""
    fixed = []
    for g in geoms:
        if g is None or g.is_empty:
            continue
        g = clean(g)
        if g is None or g.is_empty or not g.is_valid:
            continue
        fixed.append(g)
    if not fixed:
        return None
    if len(fixed) == 1:
        return fixed[0]
    try:
        return unary_union(fixed)
    except Exception:
        return unary_union([g.buffer(0) for g in fixed])


def as_multi(g):
    ps = parts(g)
    return MultiPolygon(ps) if len(ps) > 1 else (ps[0] if ps else None)


def main():
    rep = {}
    src = gpd.read_file(SRC, engine="pyogrio").to_crs(4326)
    rep["source"] = {"file": SRC, "rows": len(src), "crs": "EPSG:4326"}

    # ---------------------------------------------------------------- 1. valid polygons only
    src["geometry"] = [clean(g) for g in src.geometry]
    src = src[src.geometry.notna()].reset_index(drop=True)   # rows and geoms stay in step
    before_parts = sum(len(parts(g)) for g in src.geometry)

    # ---------------------------------------------------------------- 2. merge specks
    aea = src.to_crs(CRS_AEQD)
    geoms = [clean(g) for g in aea.geometry]
    tree = STRtree(geoms)
    merged = 0
    small = []
    for i, g in enumerate(geoms):
        for p in parts(g):
            if p.area / 1e6 < MIN_PART_KM2:
                small.append((i, p))
    for i, p in small:
        # the neighbour that shares the longest edge with this speck; never across another unit
        # that is not already touching it, and never into itself
        best, best_len = None, 0.0
        for j in tree.query(p.buffer(1.0)):
            j = int(j)
            if j == i:
                continue
            for q in parts(geoms[j]):
                if q.buffer(1.0).contains(p):
                    shared = p.buffer(1.0).intersection(q).area
                    if shared > best_len:
                        best, best_len = j, shared
        if best is None:
            continue
        geoms[best] = as_multi(safe_union(geoms[best], p))
        geoms[i] = as_multi(safe_union(*[x for x in parts(geoms[i]) if not x.equals(p)]))
        merged += 1
    after_parts = sum(len(parts(g)) for g in geoms)

    # ---------------------------------------------------------------- 3. close pinholes
    boundary = gpd.read_file(BOUNDARY, engine="pyogrio").to_crs(CRS_AEQD)
    nigeria = safe_union(*[clean(g) for g in boundary.geometry])
    country = safe_union(*geoms)
    # Only ground the sheet has already surrounded counts as a gap. The sheet does not colour the
    # whole of Nigeria (offshore, the far north-east corner), and calling that "a hole" would mean
    # inventing 97,000 km2 of rock -- which a previous pass of this script did.
    holes = [Polygon(r) for p in parts(country) for r in p.interiors
             if p.area and Polygon(r).area / 1e6 >= HOLE_KM2]
    filled, filled_km2 = 0, 0.0
    if holes:
        gtree = STRtree(geoms)
        for h in holes:
            best, best_len = None, 0.0
            for j in gtree.query(h):
                j = int(j)
                touch = h.boundary.intersection(geoms[j].boundary).length
                if touch > best_len:
                    best, best_len = j, touch
            if best is None:
                continue
            geoms[best] = as_multi(safe_union(geoms[best], h))
            filled += 1
            filled_km2 += h.area / 1e6
    aea["geometry"] = [as_multi(g) for g in geoms]
    aea = aea[aea.geometry.notna() & ~aea.geometry.is_empty].reset_index(drop=True)
    geoms = [g for g in geoms if g is not None]

    # ---------------------------------------------------------------- 4. the shipped schema
    out = aea.copy()
    out["unit_code"] = out["code"]
    out["unit_name"] = out["unit"].fillna("").str.strip()
    out["period"] = out["period"].fillna("").str.strip()
    out["sheet_colour"] = out["fill"]
    out["area_km2"] = (out.area / 1e6).round(2)
    out["in_nigeria"] = [bool(g.representative_point().within(nigeria)) for g in out.geometry]
    out["name_confidence"] = ["low" if c in LOW_CONFIDENCE else "high" for c in out.unit_code]
    out["how_named"] = [
        "printed code, legend row" if c not in LOW_CONFIDENCE else "printed code, no legend row"
        for c in out.unit_code
    ]
    out = out[["unit_code", "unit_name", "period", "sheet_colour", "area_km2", "in_nigeria",
               "how_named", "name_confidence", "geometry"]].to_crs(4326)
    out = out.sort_values("area_km2", ascending=False).reset_index(drop=True)
    out.to_file(OUT, driver="GeoJSON", engine="pyogrio",
                layer_options={"COORDINATE_PRECISION": 12})

    # ---------------------------------------------------------------- report
    part_sizes = np.array([p.area / 1e6 for g in aea.geometry for p in parts(g)])
    rep.update({
        "shipped_layer": OUT,
        "rows": len(out),
        "codes": int(out.unit_code.nunique()),
        "parts_before_merge": int(before_parts),
        "parts_after_merge": int(after_parts),
        "specks_merged": int(merged),
        "specks_threshold_km2": MIN_PART_KM2,
        "holes_filled": filled,
        "holes_filled_km2": round(filled_km2, 3),
        "coverage_pct_nigeria": round(100 * country.intersection(nigeria).area / nigeria.area, 2),
        "unmapped_km2": round(country.symmetric_difference(nigeria).area / 1e6, 1),
        "area_outside_nigeria_km2": round(country.difference(nigeria).area / 1e6, 1),
        "overlap_km2": round(
            sum(g.area for g in aea.geometry) - safe_union(*aea.geometry).area, 3) / 1e6,
        "area_km2": round(float(aea.area.sum()) / 1e6, 1),
        "part_km2": {"min": round(float(part_sizes.min()), 3),
                     "median": round(float(np.median(part_sizes)), 1),
                     "max": round(float(part_sizes.max()), 1)},
        "small_parts_under_half_km2": int((part_sizes < 0.5).sum()),
        "named_from_legend": int((out.name_confidence == "high").sum()),
        "low_confidence": sorted(out[out.name_confidence == "low"].unit_code.tolist()),
        "low_confidence_area_km2": round(
            float(out[out.name_confidence == "low"].area_km2.sum()), 0),
        "replaced": {"Geology_Bodies.geojson": 1552, "Rebuild_Geology_Units.py": 5539},
    })
    json.dump(rep, open(REPORT, "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
