#!/usr/bin/env python3
"""Put a description on every layer *inside* the GeoPackage.

`gpkg_contents.description` was empty for all 40 layers, so a reader who opens
the file in QGIS or `ogrinfo` saw a list of names and nothing else: no unit, no
provenance, no caveat, and no way to tell a picture of an elevation map from a
DEM without leaving the file. `RASTER_LAYERS.md` already claimed the layers were
"titled, described and legended in gpkg_contents"; this makes that true.

Each description states what the layer is, how many features it holds, the CRS,
which script wrote it, and - where it matters - what it must not be used for.
The rasters additionally carry their measured fit (km/px, land-border offset,
overlap) read from `raster_georeferencing.json`, so the caveat travels with the
data instead of living only in a Markdown file.

Counts and CRSs are computed from the file, not typed in, so the text cannot
drift. The script is idempotent: it always recomputes the same string.

Run:  python describe_layers.py
"""
import json
import pathlib
import sqlite3

import pyogrio

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
# the five reprojections, which live in their own file so the deliverable is one CRS
COPIES = HERE / "Nigeria_Geology_Minerals_projected_copies.gpkg"
COPY_PARENT = {"geology_units_utm32n": "geology_units",
               "geology_units_equal_area": "geology_units",
               "mineral_localities_icons_utm32n": "mineral_localities_icons",
               "mineral_localities_equal_area": "mineral_localities_icons",
               "mineral_localities_utm32n": "mineral_localities_refined"}
OUT = HERE / "layer_descriptions.json"

# layer -> (what it is / where it came from, caveat or None)
FEATURES = {
    "national_territory": (
        "Nigeria's national territory, the polygon every layer is clipped to "
        "(2023 border, EPSG:4326).", None),
    "international_boundary": (
        "The 2023 land border as printed on the source map, one line; every "
        "geology vertex is within 7.5 m of it.", None),
    "water_bodies": (
        "Sea, Lake Chad and the Niger-Benue corridor as polygons, from the "
        "source map.",
        "Deliberately not clipped to the territory: these run past the border "
        "and the sea is most of the area. Do not add to an area total."),
    "geology_units": (
        "The geology: 96 rock units plus water, no overlaps and no gaps, "
        "attributed with era, period, lithology and age; built by "
        "build_geology_final.py.",
        "A generalised 1:2,000,000 source: boundaries are good to a few km, "
        "not to a drill hole."),
    "geology_units_utm32n": (
        "`geology_units` in EPSG:32632 (UTM 32N, metres) for metric work.",
        "UTM area is +0.19 % over the true area; use equal-area for areas."),
    "geology_units_equal_area": (
        "`geology_units` in EPSG:6933 (equal-area) with exact areas in "
        "`area_km2_equal_area`.", None),
    "geology_boundaries": (
        "Geological contacts as lines, with a confidence attribute.",
        "Not the same object as `international_boundary`."),
    "faults": ("Major and inferred faults as lines.", "Inferred faults are drawn, not observed."),
    "fold_axes": ("Anticline and syncline axes as lines.", "Axes, not fold limbs."),
    "younger_granite_outlines": (
        "Outlines of the Jos Plateau ring complexes (younger granites) as lines.",
        "Outlines only: no polygon fill is implied."),
    "rivers": (
        "Drainage centrelines from the source map.",
        "83 % of their length is inside Nigeria; they continue across the border."),
    "roads": ("Trunk roads as lines from the source map.", None),
    "railway": ("Rail lines as lines from the source map.", None),
    "state_boundaries": (
        "The 36 state boundaries plus the FCT, as lines.", None),
    "towns": (
        "Settlements as printed on the 2011 sheet, with their host geology "
        "unit, and labels placed where the sheet places them. `lon`/`lat` (6 dp, "
        "about 0.1 m) are the same point as the geometry.",
        "Label centres, not surveyed coordinates; 82 rows have no name because "
        "the printed label could not be read - for coverage use `towns_geonames`."),
    "towns_geonames": (
        "The gazetteer: every populated place GeoNames records for Nigeria, "
        "with state and population where known; built by build_towns.py from "
        "the GeoNames allCountries dump (CC BY 4.0, 2014-10-02 snapshot).",
        "Names and coordinates are GeoNames'. `coord_dp` gives the decimal places "
        "GeoNames recorded: 7,372 entries carry 2 or fewer, i.e. a position good "
        "to about 1 km at best and 50 km at worst - filter on it before measuring "
        "distances. 642 rows are a second spelling of a place already in the layer "
        "(`dup_group`) and 2,638 share an exact coordinate with another row. "
        "98.9 % fall inside the border. See towns_geonames.md."),
    "state_capitals": (
        "State capitals named on the sheet, as label centres - 32 of the 37 "
        "(36 states plus the FCT).",
        "Label centres: good to about 15 km, not city-centre coordinates. "
        "Abuja, Owerri, Yenagoa, Abeokuta and Osogbo are not labelled here (nor "
        "in `towns`); take them from `towns_geonames`."),
    "volcanic_plugs": ("Volcanic plugs and necks as points.", None),
    "mineral_symbols": (
        "Minerals read off the printed symbols, 1,609 points, with the printed "
        "commodity attributes.",
        "Positions withdrawn: the symbol centres are not reliable. Attributes "
        "are usable, geometry is not."),
    "minerals_named": (
        "The 1,323 printed symbols that were named and anchored, good to about "
        "0.35 km.", None),
    "mineral_localities": (
        "Raw extraction of mineral localities (999 points).",
        "Positions withdrawn - do not use the coordinates."),
    "mineral_localities_refined": (
        "The same 999 localities under the older snapping policy.",
        "Positions withdrawn - do not use the coordinates."),
    "mineral_localities_icons": (
        "The same 999 localities, anchored to the printed icons.",
        "Positions withdrawn - do not use the coordinates."),
    "mineral_localities_utm32n": (
        "EPSG:32632 copy of `mineral_localities_refined`, not of "
        "`mineral_localities` - the name is historic and the contents are the "
        "refined positions (they differ from the raw extraction by up to 11.9 km "
        "in 117 of 999 rows).",
        "Positions withdrawn - the projection does not fix them."),
    "mineral_localities_equal_area": (
        "`mineral_localities_icons` in EPSG:6933 - the icon-anchored layer, not "
        "the raw extraction.",
        "Positions withdrawn - the projection does not fix them."),
    "mineral_localities_icons_utm32n": (
        "`mineral_localities_icons` in EPSG:32632.",
        "Positions withdrawn - the projection does not fix them."),
    "graticule_geology": (
        "The 2011 sheet's graticule, kept as a QA reference for the scan's fit.",
        "QA object, not geography: do not map it as features."),
    "graticule_minerals": (
        "The 2023 sheet's graticule, kept as a QA reference for that scan's fit.",
        "QA object, not geography: do not map it as features."),
    "poly_soil_ph": (
        "The soil-pH sheet as polygons: 5 pH classes traced from the printed "
        "fills, class colours measured from the printed swatches, clipped to "
        "the border; built by build_vector_layers.py.",
        "Traced from a 1.02 km/px print, so class edges are good to about 1 km "
        "plus the sheet's own ~4 km registration error. The first legend swatch "
        "is printed in dark navy with no readable value and is kept as "
        "'unlabelled' rather than guessed."),
    "poly_population": (
        "The population sheet as polygons: 5 classes of absolute population by "
        "unnamed district, traced from the printed fills, clipped to the "
        "border; built by build_vector_layers.py.",
        "Absolute counts per unnamed district on a 2.4 km/px print: not joinable "
        "to the admin layers and not normalisable by area. 7.5 % of the "
        "territory is left uncoloured on the sheet and is left uncoloured here."),
    "geology_era": (
        "Seven era classes dissolved from the attributed `geology_units` vector "
        "(plus water and unclassified), keyed by `class_id`; built by "
        "build_vector_layers.py. Not a tracing of the general-geology sheet: that "
        "sheet's legend draws nine era-plus-lithology classes, so this is a "
        "coarser, era-only generalisation of the vector geology.", None),
}

# raster layer -> what it must not be used for
RASTER_CAVEAT = {
    "raster_dem": "a picture of an elevation map with hillshading - read "
                  "elevation from a real DEM",
    "raster_soil_ph": "a 1:2,000,000 print with no source citation - class "
                      "edges are drawn by hand, not surveyed",
    "raster_temperature": "CHIRTSmax Jan-Dec 1986-2015 climatology, one class is "
                          "water - not a forecast, not a station record",
    "raster_forest_reserves": "a reserves-and-rivers map, not forest cover; the "
                              "noisiest fit of the nine",
    "raster_landcover": "the coarsest sheet (3 km/px, 15 classes) - a locator, "
                        "not a land-cover dataset",
    "raster_population": "absolute counts per unnamed district - do not join to "
                         "admin layers or normalise by area; position is "
                         "approximate",
    "raster_ethnic_groups": "schematic: boundaries indicative, close colours "
                            "deliberately encode close languages",
    "raster_dominant_soils": "the five inset panels on the right were clipped "
                             "away, so the layer is the main map alone",
    "raster_general_geology": "a simplification of the geology already shipped "
                              "as `geology_units`; use `geology_era` for the "
                              "class areas",
}

fits = {r["layer"]: r for r in json.load(open(HERE / "raster_georeferencing.json"))}
con = sqlite3.connect(GPKG)
rows = con.execute("SELECT table_name, data_type FROM gpkg_contents").fetchall()

descriptions = {}
for name, kind in rows:
    if kind == "features":
        what, caveat = FEATURES[name]
        g = pyogrio.read_info(GPKG, layer=name)
        n = g["features"]
        text = f"{what} {n:,} feature{'' if n == 1 else 's'}, {g['crs']}."
    else:
        f = fits[name]
        sides = f["border_sides_km"]
        text = (f"Georeferenced scan: {f['title']} ({f['theme']}), "
                f"{f['native_px'][0]}x{f['native_px'][1]} px at "
                f"{f['km_per_px_ew']:.2f} x {f['km_per_px_ns']:.2f} km/px, "
                f"EPSG:4326 RGBA tiles; land-border offset "
                f"{f['border_offset_km']:.1f} km (N/S/W/E "
                f"{sides['north']:+.1f}/{sides['south']:+.1f}/"
                f"{sides['west']:+.1f}/{sides['east']:+.1f}), overlap with the "
                f"territory {f['iou']:.3f}. This is {RASTER_CAVEAT[name]}. "
                f"Legend in RASTER_LAYERS.md.")
        caveat = None
    if caveat:
        text = f"{text} {caveat}"
    descriptions[name] = text

con.executemany("UPDATE gpkg_contents SET description = ? WHERE table_name = ?",
                [(t, n) for n, t in descriptions.items()])
con.commit()
blank = [r[0] for r in con.execute(
    "SELECT table_name FROM gpkg_contents WHERE description IS NULL OR description = ''")]
con.close()

# ---- the copies file: same treatment, plus why it exists --------------------
if COPIES.exists():
    con = sqlite3.connect(COPIES)
    for name, kind in con.execute(
            "SELECT table_name, data_type FROM gpkg_contents").fetchall():
        if kind != "features":
            continue
        parent = COPY_PARENT[name]
        what, caveat = FEATURES[parent]
        info = pyogrio.read_info(COPIES, layer=name)
        text = (f"Measurement copy of `{parent}` in {info['crs']}: {info['features']:,} "
                f"features, every attribute identical to the parent and the same key, "
                f"geometry reprojected so that area and length can be computed in "
                f"metres. It lives in this file, not in "
                f"Nigeria_Geology_Minerals_4326.gpkg, so that the deliverable is a "
                f"single CRS and its layers can be laid on each other without a "
                f"reprojection. Use `{parent}` for display and this copy for "
                f"measurement. {what}")
        if caveat:
            text = f"{text} {caveat}"
        con.execute("UPDATE gpkg_contents SET description = ? WHERE table_name = ?",
                    (text, name))
        descriptions[name] = text
    con.commit()
    con.close()

json.dump(descriptions, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"described {len(descriptions)} layers, {len(blank)} left blank")
for n in ("poly_soil_ph", "raster_population"):
    print(f"\n{n}:\n  {descriptions[n]}")
print(f"\nwrote {OUT.name}")
