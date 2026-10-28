#!/usr/bin/env python3
"""Build Nigeria_Geology_Minerals_4326.gpkg - one GeoPackage, EPSG:4326, with everything.

Vector layers
  minerals_symbols   1,323 printed symbols, each at the centre of its printed glyph, with
                     commodity name, commodity class, confidence tier and confidence value
  nigeria_boundary   Natural Earth 1:10m national outline, used for reference and clipping
  alignment_checks   the summary numbers behind the registrations, as attributes

Raster layers (all EPSG:4326, deliberately downsized: these are reference images, not
measurement products)
  ref_geology_2011       the geological sheet as drawn, 0.01 deg per pixel
  ref_minerals_2023      the mineral sheet as drawn, 0.01 deg per pixel
  combined_map           the two sheets overlaid, 0.01 deg per pixel
  mineral_density_3band  interpolated occurrence density (all / metallic / non-metallic),
                         Gaussian kernel, sigma 0.15 deg, units: symbols per 1000 km^2

Every raster carries tags stating its registration, resolution and what it must not be used for.
"""
import json, math
from pathlib import Path
import numpy as np, pymupdf, rasterio, geopandas as gpd, pandas as pd
from shapely.geometry import shape, Point, box
from shapely.ops import unary_union
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from rasterio.features import geometry_mask

P = Path(__file__).resolve().parent
GPKG = P / "Nigeria_Geology_Minerals_4326.gpkg"
if GPKG.exists(): GPKG.unlink()

CRS = "EPSG:4326"
RES = 0.01                       # degrees per pixel for every raster in the package
L, B, R, T = 2.6, 3.9, 15.0, 14.1
W = int(round((R - L) / RES)); H = int(round((T - B) / RES))
transform = from_bounds(L, B, R, T, W, H)
print(f"raster grid {W} x {H} at {RES} deg")

# ---------------------------------------------------------------- vectors
pts = gpd.read_file(P / "Minerals_Symbol_Centres_4326.geojson")
pts["mineral_class"] = pts["mineral_class"].fillna("unknown").replace("", "unknown")
pts["tier"] = pts["tier"].fillna("unidentified")
keep = ["mineral", "mineral_class", "tier", "confidence", "colour_family",
        "family_accuracy_pct", "in_nigeria", "lon", "lat", "snap_px"]
pts_out = pts[keep + ["geometry"]].copy().set_crs(CRS, allow_override=True)
outline = gpd.read_file(P / "Nigeria_Natural_Earth_outline.geojson").to_crs(CRS)
nigeria = unary_union(outline.geometry)

checks = pd.DataFrame([
    {"check": "printed graticule vs artwork frame (2023 sheet)", "value": 0.1722, "unit": "deg",
     "meaning": "0.1718-0.1726 deg; the printed grid is this far west of the frame the sheet was drawn in"},
    {"check": "mineral sheet border vs Natural Earth, printed frame", "value": 12.94, "unit": "km",
     "meaning": "systematic west offset if the printed graticule is used"},
    {"check": "mineral sheet border vs Natural Earth, embedded frame", "value": 1.06, "unit": "km",
     "meaning": "why the embedded frame is used"},
    {"check": "mineral sheet border vs GADM, embedded frame", "value": 0.46, "unit": "km",
     "meaning": "second independent reference"},
    {"check": "geology state boundaries vs GADM", "value": 1.72, "unit": "km",
     "meaning": "median offset, no correction applied"},
    {"check": "geology rivers vs Natural Earth", "value": 2.73, "unit": "km",
     "meaning": "median offset, no correction applied"},
    {"check": "geology coastline vs Natural Earth", "value": 1.86, "unit": "km",
     "meaning": "median offset, no correction applied"},
    {"check": "geology sheet best-fit shift", "value": 0.92, "unit": "km",
     "meaning": "less than 1.5 map pixels; not applied because it is inside the drawing error"},
    {"check": "symbol centre residual (independent page render)", "value": 0.39, "unit": "km",
     "meaning": "median distance from each corrected point to the centre of its printed glyph"},
    {"check": "Minna datum to WGS 84 across Nigeria", "value": 0.112, "unit": "km",
     "meaning": "largest candidate datum shift; below what these sheets can resolve"},
], columns=["check", "value", "unit", "meaning"])
checks["geometry"] = [Point(8.0, 9.0)] * len(checks)

# ---------------------------------------------------------------- rasters
def render(path, x0, y0, x1, y1, px_per_pt=1):
    pg = pymupdf.open(path)[0]
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(px_per_pt, px_per_pt),
                        clip=pymupdf.Rect(x0, y0, x1, y1), alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)

GEO_CROP = (80, 90, 2050, 1693)
MIN_CROP = (80, 359, 2050, 1968)
def geo_ll(x, y): return (x + 276.36) / 157.593, (2281.63 - y) / 157.586
def min_ll(x, y):
    return (2.47619 + (x - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (y - 358.7239) * 10.20997 / 1608.9773)
def bounds(c, fn):
    l, t = fn(c[0], c[1]); r, b = fn(c[2], c[3]); return l, b, r, t

g_img = render(P / "Geological_Map_of_Nigeria.pdf", *GEO_CROP)
m_img = render(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf", *MIN_CROP)
gb, mb = bounds(GEO_CROP, geo_ll), bounds(MIN_CROP, min_ll)

def warp_to_grid(img, bnds, band=3):
    out = np.zeros((band, H, W), np.uint8)
    src_tr = from_bounds(*bnds, img.shape[1], img.shape[0])
    for k in range(band):
        reproject(img[:, :, k], out[k], src_transform=src_tr, src_crs=CRS,
                  dst_transform=transform, dst_crs=CRS, resampling=Resampling.bilinear)
    return out

geo_r = warp_to_grid(g_img, gb)
min_r = warp_to_grid(m_img, mb)
comb = (geo_r.astype(np.float32) * .62 + min_r.astype(np.float32) * .38).astype(np.uint8)

# ---------------------------------------------------------------- density
PTS = pts_out[pts_out["in_nigeria"].astype(str).str.lower() == "true"]
def kde(sel, sigma_deg=0.15):
    xs = ((sel.geometry.x.values - L) / RES)
    ys = ((sel.geometry.y.values - B) / RES)
    gx, gy = np.meshgrid(np.arange(W), np.arange(H))
    acc = np.zeros((H, W), np.float32)
    r = int(4 * sigma_deg / RES)
    for x, y in zip(xs, ys):
        ix, iy = int(x), int(y)
        x0, x1 = max(0, ix - r), min(W, ix + r + 1)
        y0, y1 = max(0, iy - r), min(H, iy + r + 1)
        if x0 >= x1 or y0 >= y1: continue
        dx = (np.arange(x0, x1) - x) * RES
        dy = (np.arange(y0, y1) - y) * RES
        acc[y0:y1, x0:x1] += np.exp(-(dy[:, None] ** 2 + dx[None, :] ** 2) / (2 * sigma_deg ** 2))
    # normalise gaussian to per-symbol contribution, then convert to symbols per 1000 km2
    # gaussian integrates to 1 over deg^2; convert that to symbols per km^2 per symbol
    km2_per_deg2 = 111.2 * (111.2 * math.cos(math.radians(9)))
    norm = 1.0 / (2 * math.pi * sigma_deg ** 2) / km2_per_deg2 * 1000
    acc = acc * norm
    mask = geometry_mask([nigeria], out_shape=(H, W), transform=transform, invert=False)
    acc[mask] = -9999.0
    return acc.astype(np.float32)

metal = PTS[PTS["mineral_class"] == "metallic"]
nonmetal = PTS[PTS["mineral_class"] != "metallic"]
dens = np.stack([kde(PTS), kde(metal), kde(nonmetal)])
print("density bands built", dens.shape)

# ---------------------------------------------------------------- write
def write_raster(name, arr, tags, band_names=None):
    pr = dict(driver="GPKG", height=arr.shape[1], width=arr.shape[2], count=arr.shape[0],
              dtype=str(arr.dtype), crs=CRS, transform=transform, RASTER_TABLE=name,
              compress="deflate", predictor=2)
    if (GPKG).exists():
        pr["APPEND_SUBDATASET"] = "YES"
    with rasterio.open(GPKG, "w", **pr) as d:
        d.write(arr)
        d.update_tags(**tags)
        if band_names:
            for i, n in enumerate(band_names, 1):
                d.set_band_description(i, n)
        if arr.shape[0] == 3:
            d.colorinterp = [rasterio.enums.ColorInterp.red,
                             rasterio.enums.ColorInterp.green,
                             rasterio.enums.ColorInterp.blue]
    print("raster", name, arr.shape, arr.dtype)

comm = dict(CRS_NOTE="EPSG:4326 assigned as the display frame. Neither source sheet states a "
                      "datum; Minna->WGS 84 is about 0.09 km and is not resolvable here.",
            USE="visual reference and regional context at 1:2,000,000",
            NOT_FOR="surveying, licensing, legal boundaries, navigation, site-scale decisions")
write_raster("ref_geology_2011", geo_r, dict(TITLE="Geological Map of Nigeria 2011 - reference image",
            REGISTRATION="printed graticule; no correction applied (residual 1-2 km)",
            RESOLUTION="0.01 deg/px, deliberately downsized", **comm))
write_raster("ref_minerals_2023", min_r, dict(TITLE="Mineral Resources Map of Nigeria 2023 - reference image",
            REGISTRATION="embedded GeoPDF measure (printed graticule is 0.172 deg west)",
            RESOLUTION="0.01 deg/px, deliberately downsized", **comm))
write_raster("combined_map", comb, dict(TITLE="Geology and minerals overlaid - reference image",
            REGISTRATION="geology printed graticule; minerals embedded frame",
            LEGEND="colours and symbols are not decodable from this composite; use the source PDFs", **comm))
band_tags = dict(
    TITLE="Interpolated mineral occurrence density",
    METHOD="Gaussian kernel, sigma 0.15 deg (about 17 km), one contribution per printed symbol",
    UNITS="symbols per 1000 km2; nodata -9999 outside Nigeria",
    WARNING="density of printed SYMBOLS, not of reserves, grade, production or economic "
            "viability. Clustering reflects both geology and where the survey looked. "
            "Commodity names are about 81% correct.",
    **comm)
for name, arr, sub in [("mineral_density_all", dens[0], "all %d symbols" % len(PTS)),
                       ("mineral_density_metallic", dens[1], "metallic: %d symbols" % len(metal)),
                       ("mineral_density_nonmetallic", dens[2],
                        "non-metallic (industrial, gemstone, energy): %d symbols" % len(nonmetal))]:
    write_raster(name, arr[None, :, :], dict(band_tags, SUBSET=sub))

# ---------------------------------------------------------------- vectors (append)
pts_out.to_file(GPKG, layer="minerals_symbols", driver="GPKG", mode="a")
outline.assign(name="Nigeria").to_file(GPKG, layer="nigeria_boundary", driver="GPKG", mode="a")
gpd.GeoDataFrame(checks, geometry="geometry", crs=CRS).to_file(
    GPKG, layer="alignment_checks", driver="GPKG", mode="a")

# metadata row
import sqlite3
con = sqlite3.connect(GPKG)
con.execute("""CREATE TABLE IF NOT EXISTS dataset_notes(
    topic TEXT, note TEXT)""")
notes = [
    ("title", "Nigeria geology and mineral symbols, EPSG:4326"),
    ("mineral_positions", "Centre of each printed symbol on the 2023 NGSA sheet. Snapped from the "
                          "native 75 dpi artwork; independent page check: median 0.39 km from the "
                          "glyph centre, 96.5% land on a glyph."),
    ("mineral_frame", "The 2023 sheet prints a graticule 0.172 deg (about 19 km) west of the frame "
                      "its artwork was drawn in. Coordinates here use the embedded frame, proven by "
                      "the sheet's own vector border (0.5-1.1 km vs 12.9 km)."),
    ("geology", "No correction applied. The sheet's state boundaries, rivers and coastline all sit "
                "within 1-3 km of independent reference data and the best-fit shift (0.9 km) is "
                "below one and a half map pixels."),
    ("datum", "Not established for either sheet. Treat as WGS 84 and quote 1-2 km."),
    ("commodity_names", "Classified from symbol colour and size; 80.8% correct leave-one-out. Use the "
                        "tier and confidence columns per point; per-mineral totals are unreliable."),
    ("density", "Kernel density of symbols, not of mineral wealth. See the raster band notes."),
    ("not_for", "Surveying, licensing, legal boundaries, navigation, or site-scale decisions."),
]
con.executemany("INSERT INTO dataset_notes VALUES (?,?)", notes)
con.commit(); con.close()

# ---------------------------------------------------------------- report
from pyogrio import list_layers
print("\nlayers:")
for n, g in list_layers(GPKG):
    print("  ", n, g or "raster")
print("size MB", round(GPKG.stat().st_size / 1024 / 1024, 1))
