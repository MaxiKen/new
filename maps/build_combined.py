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
import argparse
import json
import pathlib
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import pyogrio

warnings.filterwarnings("ignore")

# The source extraction is NOT in this repository - see fetch_source.py and the
# provenance section of README.md.  Override with --source or the MAPS_SOURCE
# environment variable.
import os

_ap = argparse.ArgumentParser(description="Build the combined Nigeria map GeoPackage.")
_ap.add_argument("--source", default=os.environ.get(
    "MAPS_SOURCE", str(pathlib.Path(__file__).parent / "source_extraction" / "nigeria_maps.gpkg")),
    help="path to nigeria_maps.gpkg from MaxiKen/site (pinned commit)")
_args = _ap.parse_args()
SRC = pathlib.Path(_args.source)
if not SRC.exists():
    raise SystemExit(
        f"source extraction not found: {SRC}\n"
        f"Run  python fetch_source.py  first (it clones the pinned commit and verifies the checksum).")
OUT = pathlib.Path(__file__).parent
GPKG = OUT / "Nigeria_Geology_Minerals_4326.gpkg"
CRS = "EPSG:4326"

def _fix_mineral_graticule(g):
    """Subtract the constant +0.172 deg longitude offset from the QA graticule table."""
    import re
    from shapely import affinity
    offsets = []
    for _, r in g.iterrows():
        m = re.match(r"(\d+)", str(r.get("label", "")))
        if not m:
            continue
        b = r.geometry.bounds
        if (b[2] - b[0]) < 1e-9:                      # vertical = meridian
            offsets.append((b[0] + b[2]) / 2 - float(m.group(1)))
    if not offsets:
        return g
    shift = float(np.mean(offsets))
    out = g.copy()
    out["geometry"] = [affinity.translate(geom, xoff=-shift) for geom in out.geometry]
    out["label_offset_deg"] = shift
    print(f"  mineral graticule QA layer: removed +{shift:.4f} deg longitude label offset")
    return out


# ---------------------------------------------------------------- geology ----
units = pyogrio.read_dataframe(SRC, layer="geology2011_geology_units")
units["geometry"] = shapely.make_valid(units.geometry.values)
units = units[units.geometry.notna() & ~units.geometry.is_empty].copy()
units["geometry"] = shapely.normalize(units.geometry.values)          # stable ring order
# drop only *geometrically* identical polygons (the source really does carry duplicates)
units["_wkb"] = shapely.to_wkb(units.geometry.values)
units = units.drop_duplicates(subset="_wkb").drop(columns="_wkb").reset_index(drop=True)


def reconcile_legend(units, leg):
    """Resolve each polygon against the printed legend.

    The legend has 92 rows but only 87 distinct codes: `Esh`, `MS`, `MyP`, `Ncsh`
    and `Wss` are each printed twice, so each of those codes stands for two
    different units.  Dissolving by code alone merged them - and, because the
    first polygon of each group won, gave the merged unit one unit's name and
    colour (e.g. 8,739 km2 of "Blackshale, siltstone and sandstone" was being
    published as "Shale and limestone").

    Rules:
      * code printed once  -> that row defines the unit; every polygon of the
        code adopts it (a few polygons carry another unit's fill or an in-map
        label instead of a legend row);
      * code printed twice -> polygons are split by the legend row they carry;
        the lower row keeps the printed code, the other becomes CODE_<row>;
      * code not in the legend -> the unit is known only from its in-map label;
        kept and flagged attr_source = "in-map label".

    `fill` is the colour the sheet actually paints the unit: the dominant fill
    among the group's polygons (the MS swatches are swapped in the legend
    extraction, and the printed ink matches the polygons), falling back to the
    legend swatch.
    """
    attrs = ["formation", "strat_grp", "age_print", "series", "period_prt", "eon",
             "era", "period", "epoch", "age_ma_min", "age_ma_max", "rock_cls", "basins"]
    leg = leg.copy()
    leg["code"] = leg["code"].astype(str)
    rows_per_code = leg.groupby("code").size().to_dict()
    units["code"] = units["code"].astype(str).replace({"nan": np.nan})
    units["legend_row"] = pd.array(units["leg_row"], dtype="Float64")
    units["attr_source"] = "in-map label"

    def apply(mask, row):
        units.loc[mask, "unit"] = row["description"]
        units.loc[mask, "leg_code"] = row["code"]
        units.loc[mask, "leg_desc"] = row["description"]
        units.loc[mask, "leg_row"] = row["row"]
        units.loc[mask, "attr_source"] = "legend"
        for a in attrs:
            if a in leg.columns:
                units.loc[mask, a] = row[a]
        fills = units.loc[mask, "fill"].value_counts(dropna=True)
        fill = fills.index[0] if len(fills) and fills.iloc[0] >= 0.5 * mask.sum() else row["fill"]
        units.loc[mask, "fill"] = fill

    split = []
    for code, n in rows_per_code.items():
        rows = leg[leg["code"] == code].sort_values("row")
        carries = units["code"] == code
        if not carries.any():
            continue
        if n == 1:
            apply(carries, rows.iloc[0])
            continue
        for k, (_, row) in enumerate(rows.iterrows()):
            new_code = code if k == 0 else f"{code}_{int(row['row'])}"
            mask = carries & (units["legend_row"] == row["row"])
            if not mask.any():                       # no polygon claims this row
                continue
            units.loc[mask, "code"] = new_code
            apply(mask, row)
            split.append(new_code)
    # a polygon whose code is printed twice but whose row is missing: give it
    # the first row rather than dropping it silently
    for code, n in rows_per_code.items():
        if n < 2:
            continue
        rows = leg[leg["code"] == code].sort_values("row")
        stray = (units["code"] == code) & (units["legend_row"].isna()
                                           | ~units["legend_row"].isin(rows["row"]))
        if stray.any():
            apply(stray, rows.iloc[0])
    print(f"  legend reconciliation: {len(rows_per_code)} codes, "
          f"{int(sum(n - 1 for n in rows_per_code.values() if n > 1))} printed twice "
          f"-> split into {int(sum(rows_per_code.values()))} units ({', '.join(split)})")
    return units


# a polygon the extraction could not code still carries its in-map label; keep it
units.loc[units["code"].isna(), "code"] = units.loc[units["code"].isna(), "unit"].astype(str)

leg_table = pyogrio.read_dataframe(SRC, layer="geology2011_legend")
units = reconcile_legend(units, leg_table)

# Seven units are printed on the map but missing from the sheet's own legend
# (OGp, OGe, Gdss, Gmsh, LCM, Glls and a bare "S" in the Ilesha schist belt).
# They are kept - they are real, mapped ground - but the attribute is the
# printed label, not a legend description, and one of them is just a letter.
bare = units["attr_source"].eq("in-map label") & units["unit"].astype(str).str.len().le(3)
units.loc[bare, "unit"] = ("Unnamed unit printed '" + units.loc[bare, "unit"].astype(str)
                           + "' on the map (no legend row)")
units["attr_source"] = units["attr_source"].where(~bare, "printed label only")

keep = ["unit", "code", "leg_code", "leg_desc", "lbl_code", "code_src", "leg_row",
        "legend_row", "attr_source",
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
    # The source extraction labelled this QA layer with a bad af fine: its
    # "4 deg E" meridian is stored at 4.1718 E even though its latitude values
    # are right.  The feature layers are unaffected (the 2023 national boundary
    # sits 0.1 km from the 2011 coverage edge), so only this table is corrected.
    "graticule_minerals": _fix_mineral_graticule(
        pyogrio.read_dataframe(SRC, layer="minerals2023_graticule")),
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
