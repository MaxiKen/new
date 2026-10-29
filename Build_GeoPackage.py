#!/usr/bin/env python3
"""Build Nigeria_Geology_Minerals_4326.gpkg — a complete, documented EPSG:4326 dataset.

Vector layers
  geology_units       1,142 filled map-unit polygons from the 2011 sheet, with unit code,
                      rock name, period and the sheet colour; named from the unit labels
                      printed inside each polygon
  faults              115 structural fault lines drawn on the 2011 sheet
  rivers              1,055 drainage lines from the 2011 sheet
  state_boundaries    83 internal administrative lines from the 2011 sheet
  minerals_symbols    1,323 mineral symbols from the 2023 sheet, each at the centre of its
                      printed glyph, with commodity, class, confidence and tier
  nigeria_boundary    Natural Earth 1:10m outline, for reference and clipping
  alignment_checks    the measurements behind every registration decision

Rasters (EPSG:4326)
  ref_geology_2011 / ref_minerals_2023 / combined_map    0.005 deg per pixel reference images
  mineral_density_all / _metallic / _nonmetallic         kernel density, 0.01 deg, sigma 0.15 deg
"""
import json, math
from pathlib import Path
import numpy as np, pymupdf, rasterio, geopandas as gpd, pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from rasterio.features import geometry_mask

P = Path(__file__).resolve().parent
GPKG = P / "Nigeria_Geology_Minerals_4326.gpkg"
if GPKG.exists(): GPKG.unlink()
CRS = "EPSG:4326"
DREF, DDENS = 0.005, 0.01
L, B, R, T = 2.6, 3.9, 15.0, 14.1
W = int(round((R - L) / DREF)); H = int(round((T - B) / DREF))
DW = int(round((R - L) / DDENS)); DH = int(round((T - B) / DDENS))
tref = from_bounds(L, B, R, T, W, H)
tdens = from_bounds(L, B, R, T, DW, DH)
print(f"reference grid {W}x{H} at {DREF} deg; density grid {DW}x{DH} at {DDENS} deg")

# ------------------------------------------------------------------ rasters
def render(path, clip, scale=2):
    pg = pymupdf.open(path)[0]
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(scale, scale),
                        clip=pymupdf.Rect(*clip), alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)

def geo_ll(x, y): return (x + 276.36) / 157.593, (2281.63 - y) / 157.586
def min_ll(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)
def bnds(c, fn):
    l, t = fn(c[0], c[1]); r, b = fn(c[2], c[3]); return l, b, r, t

GC, MC = (80, 90, 2050, 1693), (80, 359, 2050, 1968)
gimg, mimg = render(P / "Geological_Map_of_Nigeria.pdf", GC), \
             render(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf", MC)
gb, mb = bnds(GC, geo_ll), bnds(MC, min_ll)

def warp(img, b, scale=1.0):
    h = int(round(H * scale)); w = int(round(W * scale))
    tr = from_bounds(L, B, R, T, w, h)
    out = np.zeros((3, h, w), np.uint8)
    src = from_bounds(*b, img.shape[1], img.shape[0])
    for k in range(3):
        reproject(img[:, :, k], out[k], src_transform=src, src_crs=CRS,
                  dst_transform=tr, dst_crs=CRS, resampling=Resampling.cubic)
    return out

geo_r = warp(gimg, gb)
min_r = warp(mimg, mb)
comb = (geo_r.astype(np.float32) * .62 + min_r.astype(np.float32) * .38).astype(np.uint8)
print("reference rasters warped")

# ------------------------------------------------------------------ vectors
units = gpd.read_file(P / "Geology_Layers_Extracted.gpkg", layer="geology_units")
faults = gpd.read_file(P / "Geology_Layers_Extracted.gpkg", layer="faults")
roads  = gpd.read_file(P / "Geology_Layers_Extracted.gpkg", layer="roads")
rivers = gpd.read_file(P / "Geology_Layers_Extracted.gpkg", layer="rivers")
states = gpd.read_file(P / "Geology_Layers_Extracted.gpkg", layer="state_boundaries")
pts = gpd.read_file(P / "Minerals_Symbol_Centres_4326.geojson")
outline = gpd.read_file(P / "Nigeria_Natural_Earth_outline.geojson").to_crs(CRS)
nigeria = unary_union(outline.geometry)
for g in (units, faults, roads, rivers, states, pts):
    g.set_crs(CRS, allow_override=True, inplace=True)

units["area_km2"] = (units.to_crs("EPSG:3857").area / 1e6).round(1)
units["in_nigeria"] = units.geometry.representative_point().within(nigeria)
units = units[["unit_code", "unit_name", "period", "sheet_colour", "area_km2",
               "in_nigeria", "how_named", "geometry"]]
faults["length_km"] = (faults.to_crs("EPSG:3857").length / 1000).round(1)
rivers["length_km"] = (rivers.to_crs("EPSG:3857").length / 1000).round(1)
# The 2011 sheet also draws structure and drainage in neighbouring countries and its marginal
# panels. Flag rather than delete: the geometry is real, it is just not Nigerian territory.
faults["in_nigeria"] = faults.geometry.intersects(nigeria.buffer(0.02))
roads["in_nigeria"] = roads.geometry.intersects(nigeria.buffer(0.02))
rivers["in_nigeria"] = rivers.geometry.intersects(nigeria.buffer(0.02))
states["in_nigeria"] = states.geometry.intersects(nigeria.buffer(0.02))
faults = faults[["feature", "certainty", "evidence", "length_km", "in_nigeria", "geometry"]]
roads = roads[["feature", "evidence", "in_nigeria", "geometry"]]
rivers = rivers[["feature", "length_km", "in_nigeria", "geometry"]]
states = states[["feature", "in_nigeria", "geometry"]]

pts["mineral_class"] = pts["mineral_class"].fillna("unknown").replace("", "unknown")
pts["tier"] = pts["tier"].fillna("unidentified")
pts["mineral"] = pts["mineral"].fillna("unidentified")
pts["confidence"] = pd.to_numeric(pts["confidence"], errors="coerce")
pts["in_nigeria"] = pts.geometry.within(nigeria)
cols = ["mineral", "mineral_class", "tier", "confidence", "colour_family",
        "family_accuracy_pct", "in_nigeria", "snap_px", "canvas_x_centre",
        "canvas_y_centre", "geometry"]
pts = pts[[c for c in cols if c in pts.columns]]

# ------------------------------------------------------------------ density
PTS = pts[pts["in_nigeria"]]
def kde(sel, sigma=0.15):
    xs = (sel.geometry.x.values - L) / DDENS
    ys = (sel.geometry.y.values - B) / DDENS
    acc = np.zeros((DH, DW), np.float32)
    r = int(4 * sigma / DDENS)
    for x, y in zip(xs, ys):
        ix, iy = int(x), int(y)
        x0, x1 = max(0, ix - r), min(DW, ix + r + 1)
        y0, y1 = max(0, iy - r), min(DH, iy + r + 1)
        if x0 >= x1 or y0 >= y1: continue
        dx = (np.arange(x0, x1) - x) * DDENS
        dy = (np.arange(y0, y1) - y) * DDENS
        acc[y0:y1, x0:x1] += np.exp(-(dy[:, None] ** 2 + dx[None, :] ** 2) / (2 * sigma ** 2))
    km2_per_deg2 = 111.2 * (111.2 * math.cos(math.radians(9)))
    acc *= 1.0 / (2 * math.pi * sigma ** 2) / km2_per_deg2 * 1000
    acc[geometry_mask([nigeria], out_shape=(DH, DW), transform=tdens, invert=False)] = -9999
    return acc.astype(np.float32)

metal = PTS[PTS["mineral_class"] == "metallic"]
nonm = PTS[PTS["mineral_class"] != "metallic"]
D = [kde(PTS), kde(metal), kde(nonm)]
print("density built")

# ------------------------------------------------------------------ write
COMMON = dict(
    CRS_NOTE="EPSG:4326 is the display frame. Neither source sheet states a datum; a Minna to "
             "WGS 84 shift is about 0.09 km and is below what these sheets can resolve.",
    ACCURACY="geology registration residual 1-2 km; mineral symbol centres to about 0.6 km",
    USE="regional reference at 1:2,000,000",
    NOT_FOR="surveying, licensing, legal boundaries, navigation, site-scale decisions")

def raster(name, arr, tr, tags):
    pr = dict(driver="GPKG", height=arr.shape[1], width=arr.shape[2], count=arr.shape[0],
              dtype=str(arr.dtype), crs=CRS, transform=tr, RASTER_TABLE=name,
              compress="deflate", predictor=2, tiled=True,
              blockxsize=512, blockysize=512)
    if GPKG.exists(): pr["APPEND_SUBDATASET"] = "YES"
    with rasterio.open(GPKG, "w", **pr) as d:
        d.write(arr); d.update_tags(**tags)
        if arr.shape[0] == 3:
            d.colorinterp = [rasterio.enums.ColorInterp.red,
                             rasterio.enums.ColorInterp.green,
                             rasterio.enums.ColorInterp.blue]
    print("  raster", name, arr.shape, arr.dtype)

raster("ref_geology_2011", geo_r, tref,
       dict(TITLE="Geological Map of Nigeria, 2011 - reference image",
            REGISTRATION="printed graticule, no correction applied", RESOLUTION="0.005 deg/px",
            **COMMON))
raster("ref_minerals_2023", min_r, tref,
       dict(TITLE="Mineral Resources Map of Nigeria, 2023 - reference image",
            REGISTRATION="embedded GeoPDF measure (printed graticule is 0.172 deg west)",
            RESOLUTION="0.005 deg/px", **COMMON))
raster("combined_map", comb, tref,
       dict(TITLE="Geology and minerals overlaid - reference image",
            LEGEND="colours and symbols are not decodable from a blend; use the source sheets",
            **COMMON))
BANDS = [("mineral_density_all", D[0], f"all {len(PTS)} symbols"),
         ("mineral_density_metallic", D[1], f"metallic ({len(metal)} symbols)"),
         ("mineral_density_nonmetallic", D[2], f"non-metallic ({len(nonm)} symbols)")]
for name, arr, sub in BANDS:
    raster(name, arr[None], tdens,
           dict(TITLE="Interpolated mineral-symbol density", SUBSET=sub,
                METHOD="Gaussian kernel, sigma 0.15 deg (about 17 km), one per printed symbol",
                UNITS="symbols per 1000 km2; nodata -9999 outside Nigeria",
                WARNING="counts printed symbols, not reserves, grade, production or economic "
                        "viability; clustering reflects both geology and survey coverage; "
                        "commodity names are about 81% correct", **COMMON))

for layer, gdf in [("geology_units", units), ("faults", faults), ("roads", roads), ("rivers", rivers),
                   ("state_boundaries", states), ("minerals_symbols", pts),
                   ("nigeria_boundary", outline.assign(name="Nigeria"))]:
    gdf.to_file(GPKG, layer=layer, driver="GPKG", mode="a")
    print("  vector", layer, len(gdf))

# ------------------------------------------------------------------ notes
import sqlite3
con = sqlite3.connect(GPKG)
con.execute("CREATE TABLE IF NOT EXISTS dataset_notes(topic TEXT, note TEXT)")
notes = [
 ("title", "Nigeria geology, structure and mineral symbols, EPSG:4326"),
 ("geology_units", f"{len(units)} filled polygons from the 2011 NGSA sheet, {units.unit_code.nunique()} distinct "
                   "unit codes. Named from the unit labels printed inside each polygon; a unit whose label "
                   "could not be read is marked 'unlabelled' rather than guessed."),
 ("faults", f"{len(faults)} fault traces ({int(faults.in_nigeria.sum())} inside Nigeria, "
            f"{faults.length_km.sum():.0f} km of trace in total) rebuilt from the sheet's thick black "
            "hachured structural symbol by chaining its vector segments end to end. The hachures show "
            "the downthrown side; the sheet does not label certainty, so no certainty is claimed. "
            "Treat as mapped structure, not a surveyed trace."),
 ("roads", f"{len(roads)} strokes of the sheet's thick black 'Roads' symbol, forming the national road "
            f"network ({int(roads.in_nigeria.sum())} inside Nigeria). Identified from the legend after the "
            "roads were found to be drawn with the same pen as the fault symbol; connectivity separates them."),
 ("faults_method", "Faults are the sheet's 'Major Fractures / Faults' symbol: short isolated hachured strokes. "
                    "They are separated from the continuous road network by connectivity, not by guessing: a "
                    "thick black stroke that touches another belongs to the road network, one that stands alone "
                    "is a fault dash. The hachures show the downthrown side."),
 ("rivers", f"{len(rivers)} drainage lines from the 2011 sheet ({int(rivers.in_nigeria.sum())} inside Nigeria)."),
 ("state_boundaries", f"{len(states)} internal administrative lines from the 2011 sheet "
                      f"({int(states.in_nigeria.sum())} inside Nigeria); neighbouring countries' internal "
                      "boundaries are also drawn on the sheet and are kept but flagged."),
 ("features_not_available", "The 2011 sheet carries faults only as a structural line layer. It has no fold "
                            "symbol layer, no dip-and-strike layer and no separate mineral-occurrence "
                            "polygons, so none of those could be extracted; nothing has been invented. "
                            "Graticule: the sheet's grid is a 10-minute subdivision drawn as thousands of "
                            "short segments, so the coordinate transform is supplied instead of a grid layer."),
 ("mineral_positions", "Centre of each printed symbol on the 2023 sheet, measured from its native 75 dpi "
                       "artwork and re-verified on an independent page render: 97.8% of points land on a "
                       "detected glyph, median 0.6 pt (about 0.45 km) from its centre. One artwork pixel is "
                       "0.68 km, which is the limit of the source."),
 ("mineral_frame", "The 2023 sheet prints a graticule 0.172 deg (about 19 km) west of the frame its artwork "
                   "was drawn in. Coordinates here use the embedded frame, proven by the sheet's own vector "
                   "border (0.5-1.1 km against modern data) versus the printed frame (12.9 km)."),
 ("geology_registration", "No correction applied. State boundaries, rivers and coastline on the sheet all "
                          "fall within 1-3 km of independent reference data, and the best-fit shift (0.9 km) "
                          "is less than 1.5 map pixels."),
 ("datum", "Not established for either sheet. Treat as WGS 84 and quote 1-2 km."),
 ("commodity_names", "Classified from symbol colour and size; 80.8% correct leave-one-out. Use the tier and "
                     "confidence columns per point; per-mineral totals are not reliable."),
 ("density", "Kernel density of printed symbols, not of mineral wealth. See the raster band notes."),
 ("not_for", "Surveying, licensing, legal boundaries, navigation, or site-scale decisions."),
]
con.executemany("INSERT INTO dataset_notes VALUES (?,?)", notes)
con.commit(); con.close()
print("size MB", round(GPKG.stat().st_size / 1e6, 1))
