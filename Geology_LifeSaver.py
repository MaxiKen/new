#!/usr/bin/env python3
"""Life saver — a safety net for the geology unit layer.

Run it after any change to the units, or whenever the layer looks wrong:

    python3 Geology_LifeSaver.py            # audit, repair, report
    python3 Geology_LifeSaver.py --check    # audit only; exit code 1 if anything is wrong

It answers five questions about the layer and fixes what it finds:

  1. overlaps      two polygons claiming the same ground      -> the smaller gives way
  2. holes         ground inside Nigeria with no unit          -> given to the longest-edge neighbour
  3. slivers       hair-thin fragments left by the tracing     -> merged into the neighbour they touch
  4. cuts          one unit split in two by a line or a label  -> bridged, if the gap is narrow
  5. fragments     the same unit in many disconnected pieces   -> counted, not forced together

It never invents a unit: a bridge only joins two polygons that already carry the same code, and it
refuses to join them across another unit. Everything it changes is written to the report.

Writes Geology_Units_Repaired.geojson and LifeSaver_Report.json.
"""
import json, sys
from collections import defaultdict

import numpy as np, geopandas as gpd
from shapely import STRtree
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

import os
SRC = ("Geology_Bodies.geojson" if os.path.exists("Geology_Bodies.geojson")
       else "Geology_Units_Partition.geojson")     # guard whatever layer actually ships
OUT = "Geology_Units_Repaired.geojson"
GPKG = "Nigeria_Geology_Minerals_4326.gpkg"

MIN_AREA_KM2 = 0.35       # smaller than this is a sliver
THIN_KM = 0.45            # ...and thin: 2*area/length under this means a strand, not a patch
BRIDGE_M = 400            # a gap narrower than this between two parts of one unit is a cut
HOLE_KM2 = 0.002          # smaller holes are rounding, not ground

CHECK_ONLY = "--check" in sys.argv


def parts(g):
    if g.geom_type == "Polygon":
        return [g]
    if g.geom_type == "MultiPolygon":
        return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def audit(gdf, boundary):
    g = gdf.geometry
    uni = unary_union(g.tolist())
    ng = boundary
    area = uni.area / 1e6
    overlap = (g.area.sum() - uni.area) / 1e6
    gap = ng.difference(uni).area / 1e6
    return {
        "polygons": int(len(gdf)),
        "codes": int(gdf.unit_code.nunique()),
        "covered_pct": round(uni.intersection(ng).area / ng.area * 100, 3),
        "overlap_km2": round(float(overlap), 3),
        "gap_km2": round(float(gap), 3),
        "slivers": int(sum(1 for p in g if p.area / 1e6 < MIN_AREA_KM2)),
    }


def find_cuts(gdf, geoms, codes, tree, tol_m=2500):
    """Pairs of same-code polygons with nothing but empty ground between them."""
    cuts = []
    for i, g in enumerate(geoms):
        try:
            near = tree.query(g, predicate="dwithin", distance=tol_m)
        except Exception:                       # older shapely without dwithin
            near = tree.query(g.buffer(tol_m), predicate="intersects")
        for j in near:
            j = int(j)
            if j <= i or codes[i] != codes[j]:
                continue
            d = g.distance(geoms[j])
            if not (0 < d <= tol_m):
                continue
            corridor = g.buffer(d / 2 + 60).intersection(geoms[j].buffer(d / 2 + 60))
            blocked = any(geoms[k].intersection(corridor).area > corridor.area * 0.02
                          for k in tree.query(corridor, predicate="intersects")
                          if k not in (i, j))
            if not blocked:
                cuts.append((i, j, d))
    return cuts


def health(geoms, label):
    """sum vs union: if these drift apart, some step has duplicated ground."""
    tot = sum(g.area for g in geoms) / 1e6
    uni = unary_union([g for g in geoms if not g.is_empty]).area / 1e6
    print(f"  [{label}] sum {tot:,.0f} km²  union {uni:,.0f} km²  double-counted {tot - uni:,.1f} km²")
    return tot - uni


def main():
    gdf = gpd.read_file(SRC).to_crs(32632)
    gdf["geometry"] = gdf.geometry.apply(lambda g: make_valid(g) if not g.is_valid else g)
    gdf = gdf[~gdf.geometry.is_empty].reset_index(drop=True)
    ng = gpd.read_file(GPKG, layer="nigeria_boundary").to_crs(32632).geometry.union_all()

    before = audit(gdf, ng)
    log = {"before": before, "repairs": {}}
    print("BEFORE", json.dumps(before))

    geoms = gdf.geometry.tolist()
    codes = gdf.unit_code.tolist()
    tree = STRtree(geoms)
    cuts_before = find_cuts(gdf, geoms, codes, tree)
    log["before"]["cuts_empty_space"] = len(cuts_before)
    log["before"]["cuts_narrow"] = sum(1 for _, _, d in cuts_before if d <= BRIDGE_M)
    print(f"  one unit split in two by nothing but empty ground: {len(cuts_before)} "
          f"({log['before']['cuts_narrow']} of them by less than {BRIDGE_M} m)")

    if CHECK_ONLY:
        bad = (before["overlap_km2"] > 1 or before["gap_km2"] > 50 or before["slivers"] > 0
               or log["before"]["cuts_narrow"] > 0)
        json.dump(log, open("LifeSaver_Report.json", "w"), indent=1)
        print("\nCHECK:", "problems found" if bad else "layer is clean")
        return 1 if bad else 0

    # ---------------------------------------------------------------- 1. overlaps
    # Greedy in area order, but only touching polygons that actually overlap: rebuilding one
    # huge union over and over is what made this pass slow.
    tree = STRtree(geoms)
    processed = set()
    for i in np.argsort([-g.area for g in geoms]):
        i = int(i)
        for j in tree.query(geoms[i], predicate="intersects"):
            j = int(j)
            if j == i or j in processed:
                continue
            inter = geoms[i].intersection(geoms[j])
            if inter.area > 1e-6:
                geoms[j] = geoms[j].difference(geoms[i])
        processed.add(i)
    keep = [k for k, g in enumerate(geoms) if not g.is_empty]
    if len(keep) != len(geoms):
        gdf = gdf.iloc[keep].copy()
        gdf["geometry"] = [geoms[k] for k in keep]
        gdf = gdf.reset_index(drop=True)
        geoms = gdf.geometry.tolist()
        codes = gdf.unit_code.tolist()
    else:
        gdf = gdf.copy()
        gdf["geometry"] = geoms
    log["repairs"]["overlaps_removed_km2"] = round(before["overlap_km2"], 3)
    print(f"  overlaps removed: {before['overlap_km2']:.2f} km²")

    health(geoms, "after step 1")

    # ---------------------------------------------------------------- 2. bridge cuts
    tree = STRtree(geoms)
    cuts = find_cuts(gdf, geoms, codes, tree)
    bridged = 0
    for i, j, d in sorted(cuts, key=lambda c: c[2]):
        if d > BRIDGE_M:
            continue
        a, b = geoms[i], geoms[j]
        if a is None or b is None:
            continue
        r = d / 2 + 1
        merged = unary_union([a.buffer(r), b.buffer(r)]).buffer(-r)
        if merged.is_empty:
            continue
        geoms[i] = merged
        geoms[j] = None
        bridged += 1
    if bridged:
        alive = [k for k, g in enumerate(geoms) if g is not None]
        gdf = gdf.iloc[alive].copy()
        gdf["geometry"] = [geoms[k] for k in alive]
        gdf = gdf.reset_index(drop=True)
        geoms = gdf.geometry.tolist()
        codes = gdf.unit_code.tolist()
    log["repairs"]["cuts_bridged"] = bridged
    print(f"  cuts bridged: {bridged}")

    health(geoms, "after step 2")

    # ---------------------------------------------------------------- 3. slivers
    merged_slivers = 0
    for _ in range(4):
        tree = STRtree(geoms)
        drop = set()
        for i, g in enumerate(geoms):
            if i in drop:
                continue
            if g.area / 1e6 >= MIN_AREA_KM2:
                continue
            if g.length and 2 * g.area / g.length / 1000 > THIN_KM:
                continue                       # a small but chunky patch: a real outcrop
            best, blen = None, 0.0
            for j in tree.query(g.buffer(30), predicate="intersects"):
                if j == i:
                    continue
                ln = geoms[j].boundary.intersection(g.buffer(30)).length
                if ln > blen:
                    best, blen = j, ln
            if best is None:
                continue
            geoms[best] = unary_union([geoms[best], g])
            drop.add(i)
            merged_slivers += 1
        if not drop:
            break
        alive = [k for k in range(len(geoms)) if k not in drop]
        gdf = gdf.iloc[alive].copy()
        gdf["geometry"] = [geoms[k] for k in alive]
        gdf = gdf.reset_index(drop=True)
        geoms = gdf.geometry.tolist()
        codes = gdf.unit_code.tolist()
    log["repairs"]["slivers_merged"] = merged_slivers
    print(f"  slivers merged into a neighbour: {merged_slivers}")

    health(geoms, "after step 3")

    # ---------------------------------------------------------------- 4. holes
    filled, filled_area = 0, 0.0
    for _ in range(3):
        uni = unary_union(geoms)
        holes = [p for p in parts(ng.difference(uni)) if p.area / 1e6 >= HOLE_KM2]
        if not holes:
            break
        tree = STRtree(geoms)
        touched = False
        for h in holes:
            best, blen = None, 0.0
            for j in tree.query(h.buffer(30), predicate="intersects"):
                ln = geoms[j].boundary.intersection(h.buffer(30)).length
                if ln > blen:
                    best, blen = j, ln
            if best is None:
                continue
            geoms[best] = unary_union([geoms[best], h])
            filled += 1
            filled_area += h.area / 1e6
            touched = True
        if not touched:
            break
    gdf["geometry"] = geoms
    log["repairs"]["holes_filled"] = filled
    log["repairs"]["holes_filled_km2"] = round(filled_area, 3)
    print(f"  holes filled from the adjoining unit: {filled} ({filled_area:.2f} km²)")

    health(geoms, "after step 4")

    # ---------------------------------------------------------------- 5. fragments left
    tree = STRtree(gdf.geometry.tolist())
    cuts_after = find_cuts(gdf, gdf.geometry.tolist(), gdf.unit_code.tolist(), tree)
    after = audit(gdf, ng)
    after["cuts_empty_space"] = len(cuts_after)
    after["same_code_pairs_2_5km"] = None
    log["after"] = after
    print("AFTER ", json.dumps(after))

    # fragments per unit, so the user can see where single units really are several patches
    per = defaultdict(int)
    for c in gdf.unit_code:
        per[c] += 1
    log["fragments_per_unit"] = dict(sorted(per.items(), key=lambda kv: -kv[1])[:15])

    def clean(g, guard=True):
        """Repair a broken ring without inventing ground.

        make_valid can turn a nearly-degenerate ring into a shape that spans half the country if
        the ring is self-intersecting in an unlucky place, so buffer(0) is tried first and any
        candidate that changes the area by more than 1% is rejected.
        """
        if g.is_valid or g.is_empty:
            return g
        a0 = g.area
        for cand in (g.buffer(0), make_valid(g)):
            polys = parts(cand)
            if not polys:
                continue
            m = polys[0] if len(polys) == 1 else unary_union(polys)
            if m.is_empty:
                continue
            if not guard or a0 == 0 or abs(m.area - a0) <= max(1e-9, 0.01 * a0):
                return m
        return g

    gdf = gdf.copy()
    gdf["geometry"] = [clean(g) for g in gdf.geometry]

    gdf["area_km2"] = (gdf.area / 1e6).round(4)
    out4326 = gdf.to_crs(4326).copy()
    # reprojection and writing can re-break a thin ring, so repair what is actually written
    n_bad = int((~out4326.geometry.is_valid).sum())
    out4326["geometry"] = [clean(g) for g in out4326.geometry]
    n_bad2 = int((~out4326.geometry.is_valid).sum())
    if n_bad:
        print(f"  thin rings repaired for the 4326 write: {n_bad} -> {n_bad2} still broken")
        log["repairs"]["invalid_rings_repaired"] = n_bad - n_bad2
    out4326 = out4326[~out4326.geometry.is_empty].reset_index(drop=True)
    out4326.to_file(OUT, driver="GeoJSON")
    import pyogrio
    pyogrio.write_dataframe(out4326, "Geology_Layers_Extracted.gpkg", layer="geology_units",
                            driver="GPKG")
    print("repaired layer written into Geology_Layers_Extracted.gpkg as geology_units")

    # ---------------------------------------------------------------- 6. check what was written
    back = gpd.read_file(OUT).to_crs(32632)
    # reprojecting a thin ring back to metres can re-break it; buffer(0) repairs without moving ground
    gs = [g.buffer(0) if not g.is_valid else g for g in back.geometry]
    gs = [g for g in gs if not g.is_empty]
    tot = back.area.sum() / 1e6
    uni = unary_union(gs).area / 1e6
    drift = tot - uni
    log["written"] = {"polygons": int(len(back)), "sum_km2": round(float(tot), 1),
                      "union_km2": round(float(uni), 1), "double_counted_km2": round(float(drift), 1),
                      "invalid": int((~back.is_valid).sum())}
    print(f"  read back: {len(back)} polygons, sum {tot:,.0f} km², union {uni:,.0f} km², "
          f"double-counted {drift:,.1f} km², invalid {int((~back.is_valid).sum())}")
    if drift > 1.0 or abs(drift) > 0.01 * uni:
        print("  WARNING: the written layer claims more ground than it covers — "
              "the repair duplicated something")
    json.dump(log, open("LifeSaver_Report.json", "w"), indent=1)
    print(f"\nwritten {OUT} ({len(gdf)} polygons) and LifeSaver_Report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
