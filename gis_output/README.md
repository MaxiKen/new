# Nigeria geology and filled water — raster-derived GIS reconstruction

**Source:** `NGSA_map_geology_legend_isolated.png`, 6,268 × 3,540 pixels.
**Status:** source-limited reconstruction; not an authoritative NGSA vector release and not a field-verified geological map.

## Open the shapefile

Extract the complete ZIP into one folder. Open **ngsa_units_water.shp** in QGIS, ArcGIS or another GIS. Keep its `.shx`, `.dbf`, `.prj` and `.cpg` files together. The matching `.qml` supplies source-colour fills with **no outline strokes** in QGIS. For other GIS software, colour by `rgb_hex` or categorise `class_id`; turn polygon outlines off.

There are **6,473 independent singlepart Polygon records**: **6,401 geology** and **72 filled-water** polygons. Spatially separate areas of the same colour are not dissolved or collected into multipart features. A connected polygon may legitimately contain holes occupied by other units. These are topologically distinct from multipart features.

## Attribute completeness and unavoidable ambiguity

The 92 legible legend rows are transcribed in **legend_lookup.csv**, including unit codes, lithological descriptions, formation/depositional descriptions, group/suite and broad printed age brackets. Repeated codes are retained; `legend_id` is the unique legend key. Typography and spacing have been lightly normalised, but unusual printed names and ages have not been silently replaced with modern equivalents. Detailed numerical ages, thicknesses, mineral contents and other information absent from the source have not been invented.

Feature attributes include `poly_id`, `class_id`, `src_part`, `unit_code`, `legend_ids`, `feat_type`, `lithology`, `formation`, `geo_group`, `age_label`, `attr_stat`, `review`, `edge_clip`, `area_km2`, `perim_km`, `src_px`, and `rgb_hex`. See **field_dictionary.csv** for definitions. Descriptive fields were checked after reopening the shapefile: no text truncation was detected. `polygon_attributes.csv` is a convenient non-GIS copy.

| Attribution status | Polygon count | Meaning |
|---|---:|---|
| colour_match | 5,962 | One legend swatch matches the classified source colour; geological identity still unverified |
| ambiguous | 220 | Multiple legend entries have exactly the same RGB colour |
| unresolved | 219 | Source fill has no sufficiently close legend swatch |
| visual_water | 72 | Filled water areas identified by their source colour |

The identical-colour pairs are **L019/L030** (Kalambaina / Dukamaje limestone), **L018/L034** (Dange shale / Rima siltstone and sandstone), **L035/L037** (Pindiga / Nupe) and **L050/L057** (granite and granite porphyry / biotite granite). All alternatives are recorded, separated by `|`; they are not falsely resolved from colour alone. The unmatched pink-red RGB 255,121,127 and blue RGB 103,116,255 fills remain explicitly unresolved. Some very small features may be residual cartographic artefacts rather than real outcrops.

**All features have `review = 1`.** A unique colour match is not a statement of ground-truth confidence. Formation attribution from such a small-scale image cannot be made complete and certain where the source itself is ambiguous.

## Boundaries and independence

1. Sample dominant RGB values from each legend swatch; group only truly identical colours into a candidate class.
2. Classify the full-resolution map panel, excluding the legend and most map furniture. Reliable colour seeds are within 8 RGB units of a candidate palette value.
3. Close narrow gaps from printed grid lines/text with a 4-pixel-radius morphological kernel and fill isolated mask holes smaller than 512 pixels. Reconstruct masked pixels from the nearest reliable colour seed.
4. Remove isolated mask fragments under 8 pixels and 1–3-pixel colour specks; retain larger connected areas. Filled-water fragments without an interior radius of at least 2.5 pixels are excluded as likely linework. This is not a river-centreline layer, nor are arbitrary river widths invented.
5. Polygonise using 4-neighbour connectivity. Simplify shared edges with a 0.65-pixel tolerance, densify chords to no more than 2 pixels, and smooth each unique shared edge twice with 20% corner cutting and fixed junction endpoints.
6. Re-polygonise the common edge network and attribute faces by greatest area overlap with their original cleaned component. Shared edges are constructed once, not smoothed independently on neighbouring polygons.

**Every one of the 6,473 retained source components has exactly one exported feature.** None was lost during smoothing. Pixel stair-steps are reduced and smooth geological contacts replace the boxy raster edge traces. This is deliberately conservative smoothing, not invented sub-pixel geological detail.

There are **6 edge-clipped features**. Straight lines at the source/map extent—particularly the ocean extent—are legitimate clipping edges and are flagged with `edge_clip = 1`. They are not represented as natural geological contacts. It would be misleading to draw a fictional coast beyond the image solely to eliminate those straight edges.

## Georeferencing and accuracy

The printed one-degree graticule is fitted independently in longitude and latitude using 12 longitude lines (3–14° E) and 10 latitude lines (13–4° N). The fit and measured pixel locations are supplied in **georeferencing.json**.

- Output coordinate system: **EPSG:4326, WGS84 assumed for interoperability**.
- Original horizontal datum: **not established from the supplied image**. This is NOT a verified datum transformation.
- Raster sampling: approximately **0.003045° per pixel**, or roughly **330–340 metres** in this latitude range.
- Internal grid-fit residual: **0.370 pixels in longitude; 0.497 pixels in latitude**. These residuals measure the fit to the printed grid only, **not real-world positional accuracy**.
- Colour cleanup, printed line widths, source compilation and georeferencing introduce additional uncertainty. The 4-pixel closing radius corresponds to roughly 1.3 km; narrow gaps/units can be affected. Small outcrops below the cleanup thresholds are not guaranteed to survive.
- Areas and exterior perimeters are computed on the assumed WGS84 ellipsoid. Their stored decimal precision does not imply survey accuracy.

No external boundary dataset was substituted. Coverage follows the source colours, including filled water shown outside Nigeria. This layer is not an administrative-boundary product. Fine rivers, fault traces, geological line symbols and grid lines are not separately digitised.

## Quality checks on the exported shapefile

- Invalid geometries: **0**
- Empty geometries: **0**
- Multipart/non-Polygon geometries: **0**
- Duplicate polygon IDs: **0**
- Duplicate retained source-component IDs: **0**
- Overlapping feature pairs above 1e-15 square degrees: **0**
- Smoothed shared-edge coverage test: **passed**
- Retained components lost during smoothing: **0**
- Net area change from boundary smoothing: **−0.000300%**
- Attribute round-trip: **passed**

These are computational geometry checks, not a geological accuracy certification. A valid coverage test does not establish that every original colour was interpreted correctly or that every uncoloured hole is meaningful. Small residual raster/annotation artefacts and source omissions need manual review. See **qa_report.json** for cleanup counts and the input SHA-256 fingerprint.

## Package contents

- `ngsa_units_water.shp/.shx/.dbf/.prj/.cpg` — primary shapefile dataset
- `ngsa_units_water.qml` — QGIS source-colour, no-outline style
- `legend_lookup.csv` — all 92 source legend rows
- `colour_classes.csv` — source-colour classes, including ambiguous and unresolved classes
- `polygon_attributes.csv` and `field_dictionary.csv` — attributes and definitions
- `classified_reference.tif` — georeferenced classified raster used for vectorisation; 0 = background
- `vector_map_preview.png` — preview rendered from the exported shapefile
- `classification_preview.png` — classified raster preview
- `georeferencing.json`, `qa_report.json`, `README.md` — provenance, QA and limitations

Reproducible code is retained in the repository under `scripts/`: install `requirements-lock.txt`, run `vectorize.py`, then `package.py`. The original source image is unchanged. Generation used only the supplied PNG; the other repository image was inspected for context but was not substituted as the extraction source.
