#!/usr/bin/env python3
"""Independent validation of the GeoPackage. Prints a pass/fail table and writes JSON."""
import json, sqlite3
from pathlib import Path
import numpy as np, rasterio, geopandas as gpd
from shapely.geometry import Point

P = Path(__file__).resolve().parent
GPKG = P / "Nigeria_Geology_Minerals_4326.gpkg"
R = []
def chk(name, ok, detail):
    R.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + f"{name}: {detail}")


# ---- vector layers: geometry, CRS and attribute integrity
for name, must in [("geology_units", ["unit_code", "unit_name", "period", "sheet_colour",
                                      "area_km2", "in_nigeria"]),
                   ("faults", ["feature", "certainty", "evidence", "length_km", "in_nigeria"]),
                   ("roads", ["feature", "evidence", "in_nigeria"]),
                   ("rivers", ["feature", "length_km", "in_nigeria"]),
                   ("state_boundaries", ["feature", "in_nigeria"])]:
    g = gpd.read_file(GPKG, layer=name)
    ok = (g.crs.to_epsg() == 4326 and len(g) > 0 and all(m in g.columns for m in must)
          and g.geometry.notna().all() and not g.geometry.is_empty.any())
    chk(f"vector {name}", ok, f"{len(g)} features, fields {list(g.columns)[:6]}")

u = gpd.read_file(GPKG, layer="geology_units")
chk("units carry names, not just colours", (u.unit_code != "unlabelled").sum() > 1000,
    f"{u.unit_code.nunique()} codes, {(u.unit_code=='unlabelled').sum()} unlabelled")
chk("units are inside or on Nigeria", u.in_nigeria.mean() > .8,
    f"{u.in_nigeria.sum()} of {len(u)} polygons flagged in_nigeria")
fa = gpd.read_file(GPKG, layer="faults")
chk("fault layer is sparse and plausible", 5 <= len(fa) <= 200,
    f"{len(fa)} traces, {fa.length_km.sum():.0f} km, {fa.in_nigeria.sum()} in Nigeria")
ro = gpd.read_file(GPKG, layer="roads")
chk("road network present", len(ro) > 500, f"{len(ro)} strokes, {ro.in_nigeria.sum()} in Nigeria")

con = sqlite3.connect(GPKG)
rows = con.execute("select table_name,data_type,srs_id from gpkg_contents").fetchall()
names = {r[0] for r in rows}
need = {"ref_geology_2011", "ref_minerals_2023", "combined_map", "mineral_density_all",
        "mineral_density_metallic", "mineral_density_nonmetallic", "minerals_symbols",
        "nigeria_boundary", "geology_units", "faults", "roads", "rivers", "state_boundaries"}
chk("all 13 layers present", need <= names, f"{len(need & names)} of {len(need)}: {sorted(names)}")
chk("every layer is EPSG:4326", all(r[2] == 4326 for r in rows), {r[0]: r[2] for r in rows})
ints = con.execute("pragma integrity_check").fetchone()[0]
chk("sqlite integrity", ints == "ok", ints)
notes = dict(con.execute("select topic,note from dataset_notes").fetchall())
chk("dataset notes present", len(notes) >= 6, list(notes))

pts = gpd.read_file(GPKG, layer="minerals_symbols")
chk("point count", len(pts) == 1323, len(pts))
chk("points have CRS", pts.crs.to_epsg() == 4326, str(pts.crs))
chk("all classes populated",
    pts["mineral_class"].isin(["metallic", "industrial", "gemstone", "energy", "unknown"]).all(),
    pts["mineral_class"].value_counts().to_dict())
chk("all tiers populated",
    pts["tier"].isin(["probable", "tentative", "unidentified"]).all(),
    pts["tier"].value_counts().to_dict())
nig = gpd.read_file(GPKG, layer="nigeria_boundary")
inside = pts.within(nig.geometry.union_all()).sum()
chk("most points inside Nigeria", inside > 1100, f"{inside} of {len(pts)} inside")
chk("coordinates in plausible range",
    pts.geometry.x.between(2.3, 15).all() and pts.geometry.y.between(3.8, 14.2).all(),
    f"x {pts.geometry.x.min():.2f}-{pts.geometry.x.max():.2f}, y {pts.geometry.y.min():.2f}-{pts.geometry.y.max():.2f}")

for name in ["ref_geology_2011", "ref_minerals_2023", "combined_map",
             "mineral_density_all", "mineral_density_metallic", "mineral_density_nonmetallic"]:
    with rasterio.open(f"GPKG:{GPKG}:{name}") as d:
        a = d.read(1)
        want = (1240, 1020) if "density" in name else (2480, 2040)
        ok = (d.crs.to_epsg() == 4326 and (d.width, d.height) == want
              and np.isfinite(np.nanmax(a.astype(float))))
        chk(f"raster {name}", ok,
            f"{d.width}x{d.height} {d.dtypes[0]} {d.crs.to_string()} bounds "
            f"{tuple(round(v, 2) for v in d.bounds)}")

# density sanity: integral should approximate the number of symbols
with rasterio.open(f"GPKG:{GPKG}:mineral_density_all") as d:
    a = d.read(1); a[a < -9000] = np.nan
    cell = (0.01 * 111.2) * (0.01 * 111.2 * np.cos(np.radians(9)))
    total = np.nansum(a) * cell / 1000
chk("density integrates to the point count", 0.85 * 1179 < total < 1.15 * 1179,
    f"integral {total:.0f} vs 1179 symbols inside Nigeria "
    f"(edge clipping outside the border accounts for the difference)")

# the two reference rasters must line up with each other and with the points
with rasterio.open(f"GPKG:{GPKG}:ref_geology_2011") as dg, \
     rasterio.open(f"GPKG:{GPKG}:ref_minerals_2023") as dm:
    same = dg.transform == dm.transform and dg.shape == dm.shape
chk("reference rasters share one grid", same, "identical transform and shape")

out = {"generated_from": str(GPKG.name), "checks": R,
       "passed": sum(r["pass"] for r in R), "total": len(R)}
json.dump(out, open(P / "GeoPackage_Validation.json", "w"), indent=2)
print(f"\n{out['passed']}/{out['total']} checks passed")
