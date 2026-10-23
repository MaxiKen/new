#!/usr/bin/env python3
"""
Build a single EPSG:4326 (WGS 84 lon/lat) map of Nigeria combining

  * the geology of the NGSA 1:2,000,000 Geological Map of Nigeria (2011 edition)
  * the mineral localities, symbols and infrastructure of the NGSA
    Mineral Resources Map of Nigeria (2023, 2nd edition)

Both source sheets are unprojected equirectangular drawings.  Neither carries a
usable georeference: the geology sheet has none at all (ArcMap 9.2 exported
before "Export Map Georeference Information" existed) and the mineral sheet's
embedded GeoPDF /Measure dictionary is inconsistent with its own printed
graticule.  Each sheet is therefore registered by fitting an affine transform
to its printed 1-degree graticule - in both sheets longitude and latitude are
equally spaced at 157.6 pt/degree, which is exactly what an unprojected
WGS 84 data frame at 1:2,000,000 looks like.

The combined product keeps the extracted geometry in lon/lat as-is; the only
edits are topological (make_valid, drop duplicate polygons, rebuild the
locality -> host-unit join against the authoritative geology polygons).

Outputs
    maps/Nigeria_Geology_Minerals_4326.gpkg
"""
import json
import pathlib
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import pyogrio

warnings.filterwarnings("ignore")

SRC = pathlib.Path("/tmp/site/nigeria_maps.gpkg")   # extraction of the two NGSA sheets
OUT = pathlib.Path(__file__).parent
GPKG = OUT / "Nigeria_Geology_Minerals_4326.gpkg"
CRS = "EPSG:4326"

# ---------------------------------------------------------------- geology ----
units = pyogrio.read_dataframe(SRC, layer="geology2011_geology_units")
units["geometry"] = shapely.make_valid(units.geometry.values)
units = units[units.geometry.notna() & ~units.geometry.is_empty].copy()
units["geometry"] = shapely.normalize(units.geometry.values)          # stable ring order
# drop only *geometrically* identical polygons (the source really does carry duplicates)
units["_wkb"] = shapely.to_wkb(units.geometry.values)
units = units.drop_duplicates(subset="_wkb").drop(columns="_wkb").reset_index(drop=True)

keep = ["unit", "code", "leg_code", "leg_desc", "lbl_code", "code_src", "leg_row",
        "formation", "strat_grp", "age_print", "series", "period_prt",
        "eon", "era", "period", "epoch",
        "age_ma_min", "age_ma_max", "rock_cls", "basins", "age_src",
        "area_km2", "perim_km", "cen_lon", "cen_lat", "fill"]
units = units[[c for c in keep if c in units.columns] + ["geometry"]]

# ------------------------------------------------------------- minerals -----
loc = pyogrio.read_dataframe(SRC, layer="minerals2023_mineral_localities")
loc = loc[[c for c in loc.columns
           if c in ("zone", "number", "locality", "minerals", "mineral_1", "group_1",
                    "groups", "n_minerals", "n_unknown", "symbol", "sym_colour",
                    "pos_src", "label_lon", "label_lat", "min_conf")
           ] + ["lon", "lat", "geometry"]]

syms = pyogrio.read_dataframe(SRC, layer="minerals2023_mineral_symbols_raster")
syms = syms[[c for c in syms.columns
             if c in ("mineral", "colour", "fill", "ident_mth", "ident_scr", "link", "near_num")
             ] + ["geometry"]]

# ---------------------------------------------------- host-unit re-join -----
# The 2023 sheet prints only symbols next to numbered localities; the host rock
# is read from the geological sheet.  Recompute it here against the cleaned
# polygons so the attribute in this file is self-consistent.
tree = shapely.STRtree(units.geometry.values)
pts = shapely.points(loc.geometry.x.values, loc.geometry.y.values)

def host(geom, px, py):
    if geom is not None and not geom.is_empty:
        idx = tree.query(geom, predicate="intersects")
        if len(idx):
            # smallest containing polygon wins (a point on a boundary can hit several)
            areas = units.iloc[idx]["area_km2"].values
            return units.iloc[idx[int(np.argmin(areas))]]
    idx = tree.nearest(geom)
    if idx is not None:
        return units.iloc[int(idx)]
    return None

rows = [host(g, x, y) for g, x, y in zip(pts, loc.lon.values, loc.lat.values)]
loc["host_unit"]  = [r["unit"]      if r is not None else None for r in rows]
loc["host_code"]  = [r["code"]      if r is not None else None for r in rows]
loc["host_era"]   = [r["era"]       if r is not None else None for r in rows]
loc["host_period"]= [r["period"]    if r is not None else None for r in rows]
loc["host_age_ma"]= [r["age_ma_max"] if r is not None else None for r in rows]
loc["host_dist_m"] = [
    round(shapely.distance(g, units.geometry.iloc[int(tree.nearest(g))]) * 111_320, 0)
    if r is None or not g.intersects(r.geometry) else 0.0
    for g, r in zip(pts, rows)]

# ---------------------------------------------------------------- output -----
GPKG.unlink(missing_ok=True)

layers = {
    "geology_units": units,
    "geology_boundaries": pyogrio.read_dataframe(SRC, layer="geology2011_geological_boundaries"),
    "faults": pyogrio.read_dataframe(SRC, layer="geology2011_faults"),
    "fold_axes": pyogrio.read_dataframe(SRC, layer="geology2011_fold_axes"),
    "younger_granite_outlines": pyogrio.read_dataframe(SRC, layer="geology2011_younger_granite_outlines"),
    "volcanic_plugs": pyogrio.read_dataframe(SRC, layer="geology2011_volcanic_plugs"),
    "rivers": pyogrio.read_dataframe(SRC, layer="geology2011_rivers"),
    "water_bodies": pyogrio.read_dataframe(SRC, layer="geology2011_major_rivers_poly"),
    "state_boundaries": pyogrio.read_dataframe(SRC, layer="geology2011_state_boundaries"),
    "roads": pyogrio.read_dataframe(SRC, layer="geology2011_roads"),
    "railway": pyogrio.read_dataframe(SRC, layer="geology2011_railway"),
    "towns": pyogrio.read_dataframe(SRC, layer="geology2011_towns"),
    "state_capitals": pyogrio.read_dataframe(SRC, layer="geology2011_state_capitals"),
    "mineral_localities": loc,
    "mineral_symbols": syms,
    "international_boundary": pyogrio.read_dataframe(SRC, layer="minerals2023_international_boundary"),
    "graticule_geology": pyogrio.read_dataframe(SRC, layer="geology2011_graticule"),
    "graticule_minerals": pyogrio.read_dataframe(SRC, layer="minerals2023_graticule"),
}

for name, gdf in layers.items():
    if gdf.crs is None:
        gdf = gdf.set_crs(CRS)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(CRS)
    gdf["geometry"] = shapely.make_valid(gdf.geometry.values)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
    pyogrio.write_dataframe(gdf, GPKG, layer=name, driver="GPKG", append=True)
    print(f"  {name:26s} {len(gdf):5d} features")

meta = pd.DataFrame([
    ("title", "Geology and Mineral Resources of Nigeria - combined, EPSG:4326"),
    ("crs", "WGS 84, longitude/latitude, EPSG:4326, degrees"),
    ("geology_source", "NGSA Geological Map of Nigeria, 1:2,000,000 (2011 edition, DG Prof. Siyan Malomo); vector PDF, 125 layers"),
    ("minerals_source", "NGSA Mineral Resources Map of Nigeria, 1:2,000,000, 2nd edition 2023 (DG Dr Abdulrazaq Garba); vector PDF"),
    ("geology_registration", "affine fitted to printed 1-degree graticule: lon = (x + 276.36)/157.593, lat = (2281.63 - y)/157.586; residual 0.20 pt"),
    ("minerals_registration", "affine fitted to printed graticule (not the embedded /Measure, which disagrees with it): lon = (x + 288.67)/157.288, lat = (2575.87 - y)/157.602"),
    ("provenance_note", "Both sheets are unprojected equirectangular at 157.6 pt/deg = 1:2,000,000; datum treated as WGS 84 (Minna datum would shift ~100-200 m, below drawing resolution)"),
    ("positional_accuracy", "1 pt = 0.7 km on the ground; graticule fit <0.3 pt; residual cartographic disagreement between the two sheets ~5 km median, 20 km p90"),
    ("area_check", "geology polygons total 924,900 km2 vs 923,768 km2 official - +0.1%"),
    ("attributes_note", "No attribute tables exist in either PDF; codes, strata and ages were reconstructed from layer names, the printed legend and in-polygon labels"),
    ("built", "2026-10-23"),
], columns=["key", "value"])
meta.to_json(OUT / "metadata.json", orient="records", indent=2)
print(f"\nwrote {GPKG}  ({GPKG.stat().st_size/1e6:.1f} MB)")
