#!/usr/bin/env python3
"""Export the atlas into web assets for the live comparison viewer.

Everything here is derived from the shipped GeoPackage and the source PDFs, so the viewer
cannot show anything the package does not contain:

  data/minerals_sheet.jpg     the 2023 sheet's map area, rendered from the PDF at 3.4x
  data/geology_sheet.jpg      the 2011 sheet's map area, rendered from the PDF at 2.4x
  data/occurrences.json       1,091 occurrences with names, alternatives and confidence
  data/vectors.json           faults, roads, rivers, state lines, national boundary
  data/units.json             geology unit polygons with their sheet colours
  data/stats.json             the validation and verification numbers
"""
import json, math
from pathlib import Path
import pandas as pd, geopandas as gpd, pymupdf
from PIL import Image

P = Path(__file__).resolve().parent
D = P / "web" / "data"
D.mkdir(parents=True, exist_ok=True)
GPKG = P / "Nigeria_Geology_Minerals_4326.gpkg"


def render(pdf, rect, scale, out, quality=86):
    page = pymupdf.open(pdf)[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=rect, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    im.save(out, quality=quality, optimize=True)
    print(f"  {out.name}: {im.width}x{im.height} {out.stat().st_size/1e6:.1f} MB")


MX = pymupdf.Rect(74.23969, 358.7239, 2051.8313, 1968.6611)      # 2023 map area, page points
GX = pymupdf.Rect(130, 52, 2092, 1672)                            # 2011 map frame, page points
render(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf", MX, 3.4, D / "minerals_sheet.jpg", quality=82)
render(P / "Geological_Map_of_Nigeria.pdf", GX, 2.4, D / "geology_sheet.jpg", quality=84)


def ll_2023(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)


def ll_2011(x, y):
    return ((x + 276.36) / 157.593, (2281.63 - y) / 157.586)


bounds_minerals = ll_2023(MX.x0, MX.y1) + ll_2023(MX.x1, MX.y0)     # w, s, e, n
bounds_geology = ll_2011(GX.x0, GX.y1) + ll_2011(GX.x1, GX.y0)

# ---------------------------------------------------------------- occurrences
occ = pd.read_csv(P / "Minerals_Occurrences_4326.csv")

# inside / outside the national boundary, so the viewer can be honest about border picks
_boundary = gpd.read_file(GPKG, layer="nigeria_boundary").to_crs(4326).geometry.union_all()
_gpts = gpd.GeoDataFrame(occ, geometry=gpd.points_from_xy(occ.lon, occ.lat), crs=4326)
occ["outside_ng"] = ~_gpts.within(_boundary.buffer(0.03)).values
print(f"  {int(occ.outside_ng.sum())} points fall outside the national boundary")


def clean(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    return v


points = [{"lon": round(float(r.lon), 5), "lat": round(float(r.lat), 5),
           "n": clean(r.mineral), "a": clean(r.alternative_name), "c": clean(r.confidence),
           "k": clean(r.commodity_class), "s": clean(r.name_source),
           "ls": clean(r.legend_symbol), "m": float(r.margin) if pd.notna(r.margin) else 0.0,
           "src": int(r.n_source_points), "out": bool(r.outside_ng)} for r in occ.itertuples()]
json.dump(points, open(D / "occurrences.json", "w"), separators=(",", ":"))
print(f"  occurrences.json: {len(points)} points {(D/'occurrences.json').stat().st_size/1e6:.1f} MB")


# ---------------------------------------------------------------- vectors
def segs(gdf, tol=0.0025):
    out = []
    for g in gdf.geometry:
        if g is None or g.is_empty:
            continue
        gs = g.simplify(tol, preserve_topology=True)
        parts = list(gs.geoms) if gs.geom_type.startswith(("Multi", "GeometryCollection")) else [gs]
        for part in parts:
            if part.geom_type == "LineString":
                out.append([[round(x, 4), round(y, 4)] for x, y in part.coords])
            elif part.geom_type == "Polygon":
                out.append([[round(x, 4), round(y, 4)] for x, y in part.exterior.coords])
    return out


def load(name):
    g = gpd.read_file(GPKG, layer=name).to_crs(4326)
    return g[g["in_nigeria"]] if "in_nigeria" in g.columns else g


vec = {"faults": segs(load("faults")), "roads": segs(load("roads"), .004),
       "rivers": segs(load("rivers"), .004), "states": segs(load("state_boundaries"), .004)}
boundary = gpd.read_file(GPKG, layer="nigeria_boundary").to_crs(4326)
vec["boundary"] = segs(boundary, .002)
json.dump(vec, open(D / "vectors.json", "w"), separators=(",", ":"))
print(f"  vectors.json: {sum(len(v) for v in vec.values())} paths {(D/'vectors.json').stat().st_size/1e6:.1f} MB")

# ---------------------------------------------------------------- units, with sheet colours
u = gpd.read_file(GPKG, layer="geology_units").to_crs(4326)
units = []
for r in u.itertuples():
    g = r.geometry.simplify(.004, preserve_topology=True)
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    for poly in polys:
        units.append({"c": r.sheet_colour, "code": r.unit_code, "name": r.unit_name,
                      "in": bool(r.in_nigeria),
                      "p": [[round(x, 4), round(y, 4)] for x, y in poly.exterior.coords]})
json.dump(units, open(D / "units.json", "w"), separators=(",", ":"))
print(f"  units.json: {len(units)} polygons {(D/'units.json').stat().st_size/1e6:.1f} MB")

# ---------------------------------------------------------------- stats
rd = lambda f: json.load(open(P / f)) if (P / f).exists() else {}
stats = {"occurrences": len(occ),
         "names": int(occ.mineral.nunique()),
         "confidence": occ.confidence.value_counts().to_dict(),
         "class": occ.commodity_class.value_counts().to_dict(),
         "identical": int((occ.agreement == "both readings identical").sum()),
         "same_family": int((occ.family_agreement == "same commodity family").sum()),
         "merged": int((occ.n_source_points > 1).sum()),
         "outside": int(occ.outside_ng.sum()),
         "audit": rd("Centre_Audit.json"),
         "verify": rd("Verify_Centres.json"),
         "consolidation": rd("Symbol_Consolidation.json"),
         "validation": rd("GeoPackage_Validation.json"),
         "projection": rd("Projection_Report.json"),
         "bounds": {"minerals": [round(v, 4) for v in bounds_minerals],
                    "geology": [round(v, 4) for v in bounds_geology]},
         "counts": {"units": len(u), "faults": len(vec["faults"]), "roads": len(vec["roads"]),
                    "rivers": len(vec["rivers"]), "states": len(vec["states"])},
         "layers": 13, "checks": 30}
json.dump(stats, open(D / "stats.json", "w"), indent=1)
print("  stats.json written")
print("bounds minerals", [round(v, 2) for v in bounds_minerals])
print("bounds geology ", [round(v, 2) for v in bounds_geology])
