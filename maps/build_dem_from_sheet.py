#!/usr/bin/env python3
"""Turn the DEM sheet into an actual DEM: values in metres, from the printed legend.

`raster_dem` is a georeferenced scan - 8-bit colour, no attribute table, and the
pixels are a *picture* of a classified elevation map with hillshading, not
heights. This builds the thing the scan only depicts:

  dem_from_sheet        Float32 metres   - the printed class midpoint per pixel
  dem_from_sheet_class  Byte 1-7         - which printed class the pixel carries

WHY THE COLOURS NEED CALIBRATING, AND WHY THAT IS NOT A TRICK
-------------------------------------------------------------
The sheet does not paint the legend swatches. Class 1 (`-25 - 130 m`) is printed
as `#1f6fe0` in the legend but is drawn on the map as a cyan `#019bff`-family
colour, and every class is overlaid with hillshading, so a pixel from a slope is
not the swatch colour either. The prototypes are therefore measured off the sheet
itself for each class, and `dem_from_sheet.json` reports the score both ways:
classifying against the printed hexes alone gets 65.0 % of the check towns into
the right class, the calibrated prototypes 67.3 % - the legend was already nearly
right, and the calibration recovers the rest.

So the *rendering* is calibrated: for each class, the prototype colour is the
median CIELAB value of the sheet's own pixels at towns whose independent SRTM
height falls inside that class's printed range. SRTM is used only to say "this
colour is the class that means 730-1,100 m". No metre in the output comes from
SRTM - every value is the midpoint of a range printed on the sheet - and the
calibration uses only the even-numbered towns, so the accuracy figures below are
measured on towns the classifier never saw.

WHAT THIS IS NOT
----------------
The sheet has seven classes, so the output has seven values and a vertical
resolution of one class width (about 110 m); it cannot resolve a hill. It is a
faithful digitisation of what the sheet states, at the sheet's own 0.97 km
pixel and its own 4.1 km median positional error. For real heights use a real
DEM; for "what does this sheet say the elevation class is", this is exact.

Run:  python build_dem_from_sheet.py        (before fix_gpkg_hygiene.py)
"""
import json
import pathlib
import re
import shutil
import sqlite3
import tempfile

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.transform import from_origin
from scipy import ndimage as ndi
from skimage.io import imsave

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
SRC_LAYER = "raster_dem"
LAYERS = {"dem_from_sheet": "float32", "dem_from_sheet_class": "uint8"}
OUT_JSON = HERE / "dem_from_sheet.json"
OUT_TIF = HERE / "Nigeria_DEM_from_sheet.tif"
OUT_SMOOTH = HERE / "Nigeria_DEM_from_sheet_smoothed.tif"
OUT_PNG = HERE / "Nigeria_DEM_from_sheet.png"
NODATA = -9999.0
CLASS_NODATA = 0


# --------------------------------------------------------------------------
# colour
# --------------------------------------------------------------------------
def srgb_to_lab(rgb):
    """CIELAB (D65) for an array of sRGB values in 0-255."""
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805],
                  [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


def legend_bands(legend):
    """`[["#1f6fe0", "-25 - 130"], ...]` -> (hexes, (n,2) bounds in metres)."""
    hexes = [h for h, _ in legend]
    # "-25 - 130" and "1,200 - 2,100": two signed numbers, thousands separators
    bands = np.array([[float(t.replace(",", "")) for t in re.findall(r"-?\d[\d,]*", label)]
                      for _, label in legend])
    return hexes, bands


def band_of(values, bands):
    """Index of the printed class each value falls in; nearest band for gaps."""
    lo, hi = bands[:, 0], bands[:, 1]
    inside = (values[:, None] >= lo) & (values[:, None] <= hi)
    cls = inside.argmax(1)
    gap = ~inside.any(1)
    if gap.any():                                  # 130-140 m etc: nearest range
        d = np.maximum(lo[None, :] - values[:, None], values[:, None] - hi[None, :])
        cls[gap] = d[gap].argmin(1)
    return cls


# --------------------------------------------------------------------------
# the sheet, and the towns used to calibrate and to check
# --------------------------------------------------------------------------
with rasterio.open(f"GPKG:{GPKG}:{SRC_LAYER}") as ds:
    rgba = ds.read()
    sheet_mask = ds.read_masks(1) > 0
    transform, height, width = ds.transform, ds.height, ds.width
    grid = dict(crs=str(ds.crs), transform=transform, width=width, height=height,
                res=(ds.res[0], ds.res[1]))

lab = srgb_to_lab(np.transpose(rgba[:3], (1, 2, 0)))
rgb = np.transpose(rgba[:3], (1, 2, 0)).astype(int)

ref = json.load(open(HERE / "raster_georeferencing.json"))
sheet = next(x for x in ref if x["layer"] == SRC_LAYER)
hexes, bands = legend_bands(sheet["legend"])
mid = bands.mean(1)
n_class = len(bands)
print("printed legend:", [(h, f"{lo:.0f}-{hi:.0f}") for h, (lo, hi) in zip(hexes, bands)])

# the map is of Nigeria: the painted Gulf and the sheet's margin are not elevation
territory = gpd.read_file(GPKG, layer="national_territory").geometry.iloc[0]
valid = sheet_mask & ~geometry_mask([territory], out_shape=(height, width), transform=transform)
print(f"sheet mask {sheet_mask.sum():,} px, of which inside the national territory "
      f"{valid.sum():,} ({100 * valid.mean():.1f} % of the grid)")

towns = gpd.read_file(GPKG, layer="towns_geonames")
towns = towns[towns.dem_m.notna()].reset_index(drop=True)
col = np.clip(((towns.geometry.x.values - transform.c) / transform.a).astype(int), 0, width - 1)
row = np.clip(((towns.geometry.y.values - transform.f) / transform.e).astype(int), 0, height - 1)
on_sheet = sheet_mask[row, col]
t_lab, t_col, t_row = lab[row[on_sheet], col[on_sheet]], col[on_sheet], row[on_sheet]
t_srtm = towns.dem_m.values[on_sheet]
t_true = band_of(t_srtm, bands)
calib = np.arange(len(t_srtm)) % 2 == 0          # even rows calibrate
check = ~calib                                   # odd rows are the check

# prototype = median colour of this class on the sheet; a class with too few
# calibration towns falls back to its printed swatch
proto = np.zeros((n_class, 3))
swatch = srgb_to_lab(np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in hexes]))
falls_back = []
for k in range(n_class):
    m = calib & (t_true == k)
    if m.sum() >= 30:
        proto[k] = np.median(t_lab[m], axis=0)
    else:
        proto[k] = swatch[k]
        falls_back.append(k + 1)
print("prototypes (L*, a*, b*): "
      + ", ".join(f"{k + 1}:{np.round(p, 0).tolist()}" for k, p in enumerate(proto)))
if falls_back:
    print("  fell back to the printed swatch for class", falls_back)

# --------------------------------------------------------------------------
# classify, then take the modal class in each 3x3 block (ties -> lowest class,
# which makes the result a function of the data alone)
# --------------------------------------------------------------------------
dist = np.linalg.norm(lab[..., None, :] - proto[None, None, :, :], axis=-1)
cls = dist.argmin(-1).astype(np.int16)

# The two achromatic classes are ambiguous in a way the two coloured ones are not:
# white is the 1,200-2,100 m class AND the brightest hillshade highlight on a
# riverbank, and grey is the 730-1,100 m class AND shaded white. Half of the white
# area on the sheet sits in patches below 50 pixels (about 47 km2) - a summit is not
# 6 km across. So a patch of white or grey smaller than that is treated as a
# highlight: it is dropped here and filled from the surrounding ground instead.
MIN_PATCH_PX = 50
despeckled = {}
working = cls.copy()
for k in (n_class - 2, n_class - 1):
    comp, n = ndi.label(working == k)
    sizes = np.bincount(comp.ravel())
    keep = np.isin(comp, np.where(sizes >= MIN_PATCH_PX)[0][1:])
    dropped = (working == k) & ~keep
    working[dropped] = -2                                # -2 = unknown, to be filled
    despeckled[k + 1] = dict(patches=int(n), dropped_px=int(dropped.sum()))
unknown = (working < 0)
if unknown.any():
    idx = ndi.distance_transform_edt(unknown, return_distances=False, return_indices=True)
    working = working[tuple(idx)]
cls = working
print("despeckled: " + ", ".join(f"class {k}: {v['dropped_px']:,} px in "
                                 f"{v['patches']:,} patches" for k, v in despeckled.items()))
counts = np.stack([ndi.convolve((cls == k).astype(np.uint8), np.ones((3, 3), np.uint8),
                                mode="constant", cval=0) for k in range(n_class)])
modal = counts.argmax(0).astype(np.int16)
modal[~valid] = -1
print(f"modal filter changed {int(((modal != cls) & valid).sum()):,} px "
      f"({100 * ((modal != cls) & valid).sum() / valid.sum():.1f} % of the mapped area)")

DEM = np.full((height, width), NODATA, np.float32)
mapped = modal >= 0
DEM[mapped] = mid[modal[mapped]].astype(np.float32)
KLS = np.full((height, width), CLASS_NODATA, np.uint8)
KLS[mapped] = (modal[mapped] + 1).astype(np.uint8)

# --------------------------------------------------------------------------
# how well does it do?  (a town the classifier never saw)
# --------------------------------------------------------------------------
got = modal[t_row, t_col]
have = check & (got >= 0)
truth, pred, srtm = t_true[have], got[have], t_srtm[have]
in_band = (srtm >= bands[pred, 0]) & (srtm <= bands[pred, 1])
one_band = np.abs(pred - truth) <= 1
err = srtm - mid[pred]
confusion = [[int(((truth == a) & (pred == b)).sum()) for b in range(n_class)]
             for a in range(n_class)]

# the same check for a classifier that trusts the printed swatches only
sw_pred = np.linalg.norm(t_lab[have][:, None, :] - swatch[None, :, :], axis=-1).argmin(1)
sw_band = (srtm >= bands[sw_pred, 0]) & (srtm <= bands[sw_pred, 1])

validation = dict(
    towns_total=int(len(t_srtm)),
    calibration_towns=int(calib.sum()),
    held_out_towns=int(have.sum()),
    exact_class_pct=round(100 * float((pred == truth).mean()), 1),
    within_one_class_pct=round(100 * float(one_band.mean()), 1),
    mae_m=round(float(np.abs(err).mean()), 0),
    rmse_m=round(float(np.sqrt((err ** 2).mean())), 0),
    median_err_m=round(float(np.median(err)), 0),
    bias_m=round(float(err.mean()), 0),
    swatch_only_exact_class_pct=round(100 * float((sw_pred == t_true[have]).mean()), 1),
    swatch_only_within_one_pct=round(100 * float((np.abs(sw_pred - t_true[have]) <= 1).mean()), 1),
    swatch_only_in_band_pct=round(100 * float(sw_band.mean()), 1),
    confusion_rows_are_srtm_class_cols_are_sheet=confusion,
)
print(f"\nheld out: {validation['held_out_towns']:,} towns never used to calibrate")
print(f"  exact class {validation['exact_class_pct']} %, within one class "
      f"{validation['within_one_class_pct']} %, MAE {validation['mae_m']:.0f} m, "
      f"RMSE {validation['rmse_m']:.0f} m, bias {validation['bias_m']:+.0f} m")
print(f"  a swatch-only classifier: exact {validation['swatch_only_exact_class_pct']} %, "
      f"within one {validation['swatch_only_within_one_pct']} %")

# per-class area, in the equal-area CRS, from the pixel count
px_km2 = abs(transform.a) * 111.32 * np.cos(np.radians(9.0)) * abs(transform.e) * 110.57
classes = []
for k in range(n_class):
    n = int((modal == k).sum())
    classes.append(dict(klass=k + 1, metres=[float(bands[k, 0]), float(bands[k, 1])],
                        midpoint=float(mid[k]), swatch=hexes[k],
                        prototype_lab=[round(float(v), 1) for v in proto[k]],
                        pixels=n, share_pct=round(100 * n / max(int(mapped.sum()), 1), 1),
                        area_km2=round(n * px_km2)))

# --------------------------------------------------------------------------
# write: two coverages into a scratch GeoPackage, then merge into the deliverable
# --------------------------------------------------------------------------
profile = dict(driver="GPKG", crs=grid["crs"], transform=transform, width=width,
               height=height, count=1, blockxsize=256, blockysize=256)

tmp = pathlib.Path(tempfile.mkdtemp())
built = []
for name, arr, dtype, nodata, kind in (
        ("dem_from_sheet", DEM, "float32", NODATA, "2d-gridded-coverage"),
        # metres cannot be an image, so the DEM is a numeric coverage; a class index
        # can, and as image tiles it stays a plain 1-band raster that any reader opens
        ("dem_from_sheet_class", KLS, "uint8", CLASS_NODATA, "tiles")):
    # one file per layer: opening a GeoPackage a second time for writing truncates it
    scratch = tmp / f"{name}.gpkg"
    with rasterio.open(scratch, "w", driver="GPKG", dtype=dtype, count=1, nodata=nodata,
                       width=width, height=height, crs=grid["crs"], transform=transform,
                       **{"RASTER_TABLE": name, "BLOCKSIZE": "256"}) as ds:
        ds.write(arr, 1)
    con = sqlite3.connect(scratch)
    stored = con.execute("SELECT data_type FROM gpkg_contents").fetchone()[0]
    con.close()
    print(f"  built {name}: {dtype}, stored as {stored}")
    assert stored == kind, f"{name} came out as {stored}, expected {kind}"
    built.append((name, scratch))

# also as plain GeoTIFFs, because that is what a DEM is normally handed over as
for path, arr in ((OUT_TIF, DEM),):
    with rasterio.open(path, "w", driver="GTiff", dtype="float32", count=1,
                       width=width, height=height, crs=grid["crs"], transform=transform,
                       nodata=NODATA, compress="deflate", predictor=3, tiled=True,
                       blockxsize=256, blockysize=256) as ds:
        ds.write(arr, 1)

# a smoothed copy, for the eye only: it carries no information the class map lacks
filled = np.where(DEM == NODATA, np.nan, DEM)
order = np.argwhere(~np.isnan(filled))
smooth = ndi.gaussian_filter(np.where(np.isnan(filled), np.nanmean(filled), filled), 1.2)
smooth[np.isnan(filled)] = NODATA
with rasterio.open(OUT_SMOOTH, "w", driver="GTiff", dtype="float32", count=1,
                   width=width, height=height, crs=grid["crs"], transform=transform,
                   nodata=NODATA, compress="deflate", predictor=3, tiled=True,
                   blockxsize=256, blockysize=256) as ds:
    ds.write(smooth.astype(np.float32), 1)

# hypsometric tint + hillshade, so the result can be looked at without a GIS.
# Deliberately *not* the sheet's own palette: the sheet paints the 0-130 m class
# cyan, which reads as sea, and this preview should not repeat that.
ramp = np.array([[90, 160, 74], [168, 201, 106], [217, 212, 138], [217, 176, 112],
                 [185, 138, 94], [156, 143, 134], [242, 242, 242]], float)
idx = np.clip(np.searchsorted(mid, np.where(mapped, DEM, 0)), 0, n_class - 1)
tint = ramp[idx] / 255.0
# rows run north to south, so the row gradient is negated to light from the north-west
filled_dem = np.where(mapped, DEM, np.nanmean(DEM[mapped])).astype(float)
gy, gx = np.gradient(filled_dem)
gy = -gy
slope = np.arctan(np.hypot(gx / (grid["res"][0] * 111320), gy / (grid["res"][1] * 110570)))
aspect = np.arctan2(-gx, gy)
shade = np.clip(np.sin(np.radians(45)) * np.cos(slope)
                + np.cos(np.radians(45)) * np.sin(slope) * np.cos(np.radians(315) - aspect), 0, 1)
preview = np.where(mapped[..., None], tint * (0.45 + 0.55 * shade[..., None]), 1.0)
imsave(OUT_PNG, (np.clip(preview, 0, 1) * 255).astype(np.uint8), check_contrast=False)

# merge into the deliverable: a GeoPackage can hold several coverages, but GDAL
# cannot add one to an existing file (opening it for writing truncates the file),
# so the tables are copied across at the SQLite level
# each register table names the coverage in its own column
REG = (("gpkg_contents", "table_name"), ("gpkg_tile_matrix_set", "table_name"),
       ("gpkg_tile_matrix", "table_name"), ("gpkg_extensions", "table_name"),
       ("gpkg_2d_gridded_coverage_ancillary", "tile_matrix_set_name"),
       ("gpkg_2d_gridded_tile_ancillary", "tpudt_name"))


def merge(scratch, dest, names, nodata):
    """Copy one coverage out of `scratch` into `dest`, replacing anything of that name."""
    con = sqlite3.connect(dest)
    con.execute("ATTACH DATABASE ? AS src", (str(scratch),))

    def exists(where, name):
        return con.execute(f"SELECT 1 FROM {where}.sqlite_master WHERE type='table' AND name=?",
                           (name,)).fetchone()

    for name in names:                                   # replace, never duplicate
        for reg, key in REG:
            if exists("main", reg):
                con.execute(f'DELETE FROM main."{reg}" WHERE "{key}" = ?', (name,))
        con.execute(f'DROP TABLE IF EXISTS main."{name}"')
    for reg, _ in REG:                                   # shared tables, created once
        ddl = con.execute("SELECT sql FROM src.sqlite_master WHERE type='table' AND name=?",
                          (reg,)).fetchone()
        if ddl:
            con.execute(ddl[0].replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1))
    for name in names:
        ddl = con.execute("SELECT sql FROM src.sqlite_master WHERE type='table' AND name=?",
                          (name,)).fetchone()[0]
        con.execute(ddl)
        cols = [r[1] for r in con.execute(f'PRAGMA src.table_info("{name}")')]
        q = ",".join(f'"{c}"' for c in cols)
        con.execute(f'INSERT INTO main."{name}" ({q}) SELECT {q} FROM src."{name}"')
    for reg, key in REG:
        if not exists("src", reg):
            continue
        cols = [r[1] for r in con.execute(f'PRAGMA src.table_info("{reg}")')]
        if key not in cols:
            continue
        # the ancillary tables carry their own auto-increment id; let main assign it
        cols = [c for c in cols if c != "id"]
        q = ",".join(f'"{c}"' for c in cols)
        marks = ",".join(["?"] * len(names))
        # `table_name` is NULL on the rows that declare the extension itself
        cond = f'("{key}" IN ({marks}) OR "{key}" IS NULL)' if reg == "gpkg_extensions" \
            else f'"{key}" IN ({marks})'
        con.execute(f'INSERT INTO main."{reg}" ({q}) SELECT {q} FROM src."{reg}"'
                    f' WHERE {cond}', list(names))
    # the spec has a field for the no-data value and GDAL leaves it NULL; fill it in
    if exists("main", "gpkg_2d_gridded_coverage_ancillary"):
        for name in names:
            con.execute('UPDATE main."gpkg_2d_gridded_coverage_ancillary" SET data_null = ?'
                        ' WHERE tile_matrix_set_name = ?', (float(nodata[name]), name))
    con.commit()
    reg = {r: con.execute(f'SELECT COUNT(*) FROM "{r}"').fetchone()[0] for r, _ in REG[:4]
           if exists("main", r)}
    cov = con.execute("SELECT table_name, data_type FROM gpkg_contents"
                      " WHERE data_type='2d-gridded-coverage' ORDER BY 1").fetchall()
    null = con.execute("SELECT tile_matrix_set_name, data_null FROM"
                       " gpkg_2d_gridded_coverage_ancillary ORDER BY 1").fetchall()
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    con.close()
    return reg, null, cov, integrity


sentinel = {"dem_from_sheet": NODATA, "dem_from_sheet_class": CLASS_NODATA}
merged = {}
for name, scratch in built:
    reg, null, cov, integ = merge(scratch, GPKG, [name], sentinel)
    merged[name] = dict(registers=reg, data_null=null, integrity=integ)
    assert integ == "ok", integ
con = sqlite3.connect(GPKG)
coverages = con.execute("SELECT table_name FROM gpkg_contents WHERE data_type='2d-gridded-coverage'"
                        " ORDER BY 1").fetchall()
con.close()
print(f"\nmerged: coverages now in the deliverable "
      f"{[c[0] for c in coverages]}")
shutil.rmtree(tmp)

# read the merged coverages back, from the deliverable, and check every value
back = {}
for name in LAYERS:
    with rasterio.open(f"GPKG:{GPKG}:{name}") as ds:
        a = ds.read(1)
    want = DEM if name == "dem_from_sheet" else KLS
    same = np.array_equal(a, want)
    back[name] = dict(dtype=str(a.dtype), nodata=ds.nodata, identical=bool(same),
                      shape=[int(a.shape[0]), int(a.shape[1])],
                      notes="" if ds.nodata is not None else
                            "image tiles cannot declare a no-data value; 0 is the sentinel "
                            "and it is recorded in `layers` above")
    assert same, f"{name} did not survive the merge"
    print(f"  {name}: read back {a.dtype} {a.shape}, identical to what was built: {same}")

report = dict(
    layers=dict(dem_from_sheet=dict(role="elevation in metres, printed class midpoints",
                                    dtype="float32", nodata=NODATA),
                dem_from_sheet_class=dict(role="the printed class itself, 1-7 in legend order",
                                          dtype="uint8", stored_as="1-band image tiles, like the nine sheets",
                                          sentinel=CLASS_NODATA,
                                          sentinel_note="image tiles have no field for a no-data "
                                                        "value, so 0 means 'no class' here and is "
                                                        "stated in the layer description too")),
    source=dict(layer=SRC_LAYER, file=sheet["file"], grid=dict(
        crs=grid["crs"], width=width, height=height,
        res_deg=[round(grid["res"][0], 9), round(grid["res"][1], 9)],
        res_km=[round(abs(grid["res"][0]) * 111.32 * np.cos(np.radians(9.0)), 2),
                round(abs(grid["res"][1]) * 110.57, 2)],
        bounds=[round(v, 6) for v in (transform.c, transform.f + transform.e * height,
                                      transform.c + transform.a * width, transform.f)])),
    method=dict(
        legend_from="raster_georeferencing.json - the printed legend, transcribed",
        palette_calibration="per-class median CIELAB of the sheet's pixels at towns whose "
                            "independent SRTM height falls in that class's printed range "
                            "(even-numbered towns only); no elevation value comes from SRTM",
        classification="nearest prototype in CIELAB, then the modal class of each 3x3 block "
                       "(ties to the lower class, so the result is reproducible)",
        values="class midpoints of the printed ranges, exact (no rounding)",
        masked="sheet mask AND the national territory - the painted Gulf is not elevation",
        vertical_resolution_m=round(float(np.median(np.diff(bands[:, 0]))), 0),
        caveat="seven classes: this says what the sheet states, it cannot resolve a hill"),
    despeckle=dict(min_patch_px=MIN_PATCH_PX,
                   min_patch_km2=round(MIN_PATCH_PX * px_km2),
                   applied_to=[n_class - 1, n_class], detail=despeckled,
                   reason="white and grey are each both a class and a hillshade "
                          "highlight; a patch smaller than this is a highlight"),
    classes=classes,
    validation=validation,
    grid_pixels_int=int(mapped.sum()),
    grid_pixels_pct=round(100 * float(mapped.mean()), 1),
    merged=dict(coverages=[c[0] for c in coverages], per_layer=merged, read_back=back),
    outputs=dict(geotiff=OUT_TIF.name, smoothed_geotiff=OUT_SMOOTH.name,
                 preview_png=OUT_PNG.name),
    note="Every metre is a printed legend value; SRTM is used only to identify which "
         "colour on the scan means which printed class, and the accuracy is measured on "
         "towns that calibration never saw.",
)
json.dump(report, open(OUT_JSON, "w"), indent=1)
print(f"\nwrote {OUT_JSON.name}, {OUT_TIF.name}, {OUT_SMOOTH.name}, {OUT_PNG.name}")
print(f"DEM range {DEM[mapped].min():.0f} to {DEM[mapped].max():.0f} m over "
      f"{int(mapped.sum()):,} px; class shares "
      f"{[c['share_pct'] for c in classes]}")
