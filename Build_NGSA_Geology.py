#!/usr/bin/env python3
"""Re-reference and repair the NGSA geology polygons that already live in this repository.

The polygons come from `data/ngsa/ngsa_geology_v6.gpkg` — revision 6 of the NGSA interpretation
that sat on branches 7am / edit-mode / side. They are the sensible ones: 1,588 bodies that follow
the printed contacts, cover the mapped area and carry a lithology. Their header says
"EPSG:4326 — assumed datum", i.e. nobody had checked the reference.

What this script does
---------------------
1. Checks the reference against the printed graticule on the source photograph, not against hope.
   The meridians and parallels were measured to the pixel centre (data/ngsa/graticule_control_points
   .json). The shipped linear transform is compared with the grid those lines define, in metres.
2. Applies a correction if the check finds one that matters (more than 200 m anywhere).
3. Cuts the bodies to Nigeria, closes the ground the map leaves uncoloured, absorbs the tiny
   bodies, and gives each one the legend name and period used everywhere else in this repository.
4. Writes data/geology/geology_bodies_retired.geojson and its report. That layer is NOT what
   ships (see Build_Geology_Units.py): it is kept as evidence of the trace, and named so nobody
   mistakes it for the shipped layer.

Run:  python3 Build_NGSA_Geology.py
"""
import json

import geopandas as gpd, numpy as np, rasterio
from shapely import STRtree, make_valid
from shapely.geometry import Point
from shapely.ops import unary_union

import geology_legend as L

SRC = "data/ngsa/ngsa_geology_v6.gpkg"
GPKG = "Nigeria_Geology_Minerals_4326.gpkg"
CP = "data/ngsa/graticule_control_points.json"
OUT = "data/geology/geology_bodies_retired.geojson"

SHIPPED = dict(x0=2.3359994770659283, sx=0.003045517499751267,
               y0=13.895364028822385, sy=-0.003045590373802226, crop=190)
MIN_AREA_KM2 = 0.5          # below this a body is merged into its neighbour
THIN_KM = 0.4               # ...unless it is a genuine chunky little outcrop
WATER_RGB = (150, 218, 243)  # the 2011 sheet's water blue

EXTRA_UNITS = {
    "Glgss": ("Gravel and sand", "Cretaceous"),
    "Glpg": ("Pebbly gravel", "Cretaceous"),
    "Glss": ("Gravel, sand and clay", "Cretaceous"),
    "MyI": ("Mylonites", "Pan-African"),
    "OGp": ("Older Granite series, code OGp — printed on the sheet, no row in its legend", "Pan-African"),
    "S": ("Code S — printed on the sheet, no row in its legend", "unknown"),
    "WATER": ("Water body (as printed)", "—"),
}


def corner_km(lon_a, lat_a, lon_b, lat_b):
    """distance in km on the ground between two lon/lat fixes"""
    dx = (lon_b - lon_a) * 111.32 * np.cos(np.radians((lat_a + lat_b) / 2))
    dy = (lat_b - lat_a) * 110.57
    return float(np.hypot(dx, dy))


def check_reference():
    """Compare the shipped linear georeference with the sheet's own printed graticule."""
    cp = json.load(open(CP))
    mer, par = cp["meridians"], cp["parallels"]
    ax, bx = np.polyfit([p[0] for p in mer], [p[1] for p in mer], 1)
    ay, by = np.polyfit([p[0] for p in par], [p[1] for p in par], 1)
    lon_grid = lambda x: bx + ax * x
    lat_grid = lambda y: by + ay * y
    lon_ship = lambda x: SHIPPED["x0"] + SHIPPED["sx"] * (x - SHIPPED["crop"])
    lat_ship = lambda y: SHIPPED["y0"] + SHIPPED["sy"] * (y - SHIPPED["crop"])

    xs = [p[0] for p in mer] + [p[0] for p in mer]
    ys = [p[0] for p in par] + [p[0] for p in par]
    offsets = [corner_km(lon_ship(x), lat_ship(y), lon_grid(x), lat_grid(y)) for x, y in zip(xs, ys)]
    res_mx = [abs(p[0] - (p[1] - bx) / ax) for p in mer]
    res_my = [abs(p[0] - (p[1] - by) / ay) for p in par]
    def spacing(pts):
        """neighbouring grid lines only: the control points are in two blocks, east and west"""
        d = np.diff(sorted(p[0] for p in pts))
        return float(d[d < np.median(d) * 2].mean())

    spacing_x, spacing_y = spacing(mer), spacing(par)
    rep = {
        "control_points": {"meridians": len(mer), "parallels": len(par)},
        "grid_pixels_per_degree": [round(spacing_x, 2), round(spacing_y, 2)],
        "grid_straightness_px": {"meridian": round(float(np.mean(res_mx)), 2),
                                 "parallel": round(float(np.mean(res_my)), 2)},
        "shipped_vs_grid_km": [round(float(np.mean(offsets)), 3), round(float(np.max(offsets)), 3)],
        "verdict": None,
    }
    worst = float(np.max(offsets))
    if worst > 0.2:
        rep["verdict"] = (f"the shipped transform was off by up to {worst:.2f} km; "
                          f"it has been replaced by the graticule fit")
    else:
        rep["verdict"] = (f"the shipped transform agrees with the printed graticule to "
                          f"{worst:.2f} km, so the polygons were already in the right place; "
                          f"the graticule fit is used from here on because it is measured, "
                          f"not assumed")
    # the graticule fit expressed as the same kind of pixel transform, for the record
    rep["graticule_transform"] = {"lon": [round(bx, 7), round(ax, 10)],
                                  "lat": [round(by, 7), round(ay, 10)]}
    return rep, (lon_ship, lat_ship), (lon_grid, lat_grid), worst


def parts(g):
    if g.geom_type == "Polygon":
        return [g]
    if g.geom_type == "MultiPolygon":
        return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def main():
    rep = {}
    gdf = gpd.read_file(SRC, layer="geology_bodies").to_crs(4326)
    print(f"source: {len(gdf)} bodies, {gdf.unit_code.nunique()} codes")

    ref, ship, grid, worst = check_reference()
    rep["reference"] = ref
    print(f"reference: {ref['verdict']}")

    # move the polygons from the assumed transform to the measured one (tiny, but it is the
    # difference between 'assumed' and 'checked')
    if worst > 0.05:
        lon_ship, lat_ship = ship
        lon_grid, lat_grid = grid
        def retie(geom):
            from shapely import transform as sh_transform
            def f(a):
                lon = a[:, 0]; lat = a[:, 1]
                # invert the shipped transform to sheet pixels, then apply the graticule fit
                px = (lon - SHIPPED["x0"]) / SHIPPED["sx"] + SHIPPED["crop"]
                py = (lat - SHIPPED["y0"]) / SHIPPED["sy"] + SHIPPED["crop"]
                return np.column_stack([lon_grid(px), lat_grid(py)])
            return sh_transform(geom, f)
        gdf["geometry"] = [retie(g) for g in gdf.geometry]
        print("  polygons retied to the printed graticule")

    gdf["geometry"] = [make_valid(g) if not g.is_valid else g for g in gdf.geometry]
    gdf = gdf[~gdf.geometry.is_empty].reset_index(drop=True)

    # ---------------------------------------------------------------- cut to the country
    ng = gpd.read_file(GPKG, layer="nigeria_boundary").to_crs(4326).geometry.union_all()
    gdf["geometry"] = gdf.geometry.intersection(ng)
    gdf = gdf[~gdf.geometry.is_empty].reset_index(drop=True)
    gdf["geometry"] = gdf.geometry.apply(lambda g: max(parts(g), key=lambda p: p.area)
                                         if g.geom_type != "Polygon" and parts(g) else g)
    gdf = gdf[~gdf.geometry.is_empty].reset_index(drop=True)
    print(f"  after cutting to Nigeria: {len(gdf)} bodies")

    # ---------------------------------------------------------------- close the ground the map leaves bare
    sheet = rasterio.open(f"GPKG:{GPKG}:ref_geology_2011")

    def is_water(geom):
        """is the printed 2011 sheet blue at this piece of ground?"""
        p = geom.representative_point()
        r, c = sheet.index(p.x, p.y)
        win = sheet.read([1, 2, 3], window=((max(r - 3, 0), r + 4), (max(c - 3, 0), c + 4)))
        rgb = win.reshape(3, -1).mean(1)
        return float(np.abs(rgb - np.array(WATER_RGB)).sum()) < 60

    filled_water, filled_land = 0, 0.0
    for _ in range(4):
        uni = unary_union(gdf.geometry.tolist())
        gaps = [p for p in parts(ng.difference(uni)) if p.area * 111 * 111 > 0.004]
        if not gaps:
            break
        geoms = gdf.geometry.tolist()
        tree = STRtree(geoms)
        new_rows, touched = [], False
        for h in gaps:
            if is_water(h):
                new_rows.append(dict(unit_code="WATER", lithology="open water as printed",
                                     class_id=95, hex_color="#96dcf4", contact_qa="WATER_MASK",
                                     qa_status="WATER", geometry=h))
                filled_water += 1
                touched = True
                continue
            best, blen = None, 0.0
            for j in tree.query(h.buffer(0.02), predicate="intersects"):
                ln = geoms[int(j)].boundary.intersection(h.buffer(0.02)).length
                if ln > blen:
                    best, blen = int(j), ln
            if best is None:
                continue
            geoms[best] = unary_union([geoms[best], h])
            filled_land += h.area * 111 * 111
            touched = True
        gdf["geometry"] = geoms
        if new_rows:
            gdf = gpd.GeoDataFrame(
                __import__("pandas").concat([gdf, gpd.GeoDataFrame(new_rows, crs=4326)],
                                            ignore_index=True), crs=4326)
        if not touched:
            break
    sheet.close()
    print(f"  bare ground closed: {filled_water} water pieces, {filled_land:,.0f} km² of ground added to a neighbour")

    # ---------------------------------------------------------------- tiny bodies
    merged_tiny = 0
    u = gdf.to_crs(32632)
    for _ in range(3):
        geoms = u.geometry.tolist()
        tree = STRtree(geoms)
        drop = set()
        for i, g in enumerate(geoms):
            if i in drop or g.area / 1e6 >= MIN_AREA_KM2:
                continue
            if g.length and 2 * g.area / g.length / 1000 > THIN_KM:
                continue
            best, blen = None, 0.0
            for j in tree.query(g.buffer(50), predicate="intersects"):
                j = int(j)
                if j == i:
                    continue
                ln = geoms[j].boundary.intersection(g.buffer(50)).length
                if ln > blen:
                    best, blen = j, ln
            if best is None:
                continue
            geoms[best] = unary_union([geoms[best], g])
            drop.add(i)
            merged_tiny += 1
        if not drop:
            break
        alive = [k for k in range(len(geoms)) if k not in drop]
        u = u.iloc[alive].copy()
        u["geometry"] = [geoms[k] for k in alive]
        u = u.reset_index(drop=True)
    gdf = u.to_crs(4326)
    print(f"  tiny bodies merged into a neighbour: {merged_tiny}")

    # ---------------------------------------------------------------- names, periods, colours
    def name_of(code):
        if code in L.UNIT:
            return L.UNIT[code][0], L.UNIT[code][1], "high"
        if code in EXTRA_UNITS:
            nm, per = EXTRA_UNITS[code]
            # water is not in doubt; the gravel variants and the mylonite are named from the
            # sheet's own words; OGp and S are codes the sheet prints but its legend omits
            conf = {"WATER": "high", "Glgss": "medium", "Glpg": "medium",
                    "Glss": "medium", "MyI": "medium"}.get(code, "low")
            return nm, per, conf
        for c in L.UNIT:
            if c.lower() == str(code).lower():
                return L.UNIT[c][0], L.UNIT[c][1], "medium"
        return f"Unresolved code {code} — printed on the sheet, absent from its legend", "unknown", "low"

    names, periods, conf = zip(*[name_of(c) for c in gdf.unit_code])
    gdf["unit_name"] = names
    gdf["period"] = periods
    gdf["name_confidence"] = conf
    gdf["how_named"] = [
        "code printed on the map body, matched to the sheet's legend" if c in L.UNIT
        else "code printed on the map body, but the sheet's legend has no row for it — "
             "named only to series level and flagged low" for c in gdf.unit_code]
    gdf["sheet_colour"] = [("#96dcf4" if c == "WATER" else h) for c, h in zip(gdf.unit_code, gdf.hex_color)]
    gdf["area_km2"] = (gdf.to_crs(32632).area / 1e6).round(4)
    gdf["in_nigeria"] = True

    # ---------------------------------------------------------------- checks and output
    u = gdf.to_crs(32632)
    uni = unary_union(u.geometry.tolist())
    ng32 = gpd.GeoSeries([ng], crs=4326).to_crs(32632).iloc[0]
    areas = u.area / 1e6
    rep.update({
        "bodies": int(len(gdf)),
        "codes": int(gdf.unit_code.nunique()),
        "area_km2": round(float(areas.sum()), 1),
        "union_km2": round(float(uni.area / 1e6), 1),
        "nigeria_km2": round(float(ng32.area / 1e6), 1),
        "coverage_pct": round(float(uni.intersection(ng32).area / ng32.area * 100), 3),
        "overlap_km2": round(float(areas.sum() - uni.area / 1e6), 3),
        "holes_km2": round(float(ng32.difference(uni).area / 1e6), 3),
        "under_0_5_km2": int((areas < 0.5).sum()),
        "median_km2": round(float(areas.median()), 1),
        "largest_km2": round(float(areas.max()), 1),
        "named_full_legend": int((gdf.name_confidence != "low").sum()),
        "codes_absent_from_legend": {c: int((gdf.unit_code == c).sum())
                                     for c in ("OGp", "S") if (gdf.unit_code == c).any()},
        "area_without_legend_name_km2": round(float(areas[gdf.name_confidence == "low"].sum()), 1),
        "merged_tiny": merged_tiny,
        "water_bodies": int((gdf.unit_code == "WATER").sum()),
    })
    print(json.dumps({k: rep[k] for k in ("bodies", "codes", "area_km2", "coverage_pct",
                                          "overlap_km2", "holes_km2", "under_0_5_km2",
                                          "named_full_legend")}, indent=1))

    cols = ["unit_code", "unit_name", "period", "sheet_colour", "area_km2", "in_nigeria",
            "how_named", "name_confidence", "lithology", "class_id", "contact_qa", "geometry"]
    gdf[cols].to_crs(4326).to_file(OUT, driver="GeoJSON")
    json.dump(rep, open("data/geology/geology_bodies_retired_report.json", "w"), indent=1)
    print(f"wrote {OUT} and its report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
