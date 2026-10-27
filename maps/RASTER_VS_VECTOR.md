# Raster or vector? — the decision, sheet by sheet

The nine scans were first shipped all as rasters. That was a decision made once, in
advance, and it was not tested per sheet. This document records the test, the
measurement behind each verdict, and what changed.

## What the test asks

A printed class map is one of three things, and each wants a different format:

| if the sheet is… | the right product is… | why |
|---|---|---|
| **flat fills with inked boundaries** | **polygons** | the classes *are* areas: they can be queried, dissolved, joined to the geology and measured in km². The round trip loses < 5 % of the classification. |
| **a rendered surface** — hillshade, interpolation between classes | **the raster** | the "class" varies inside itself; polygonising turns relief or a gradient into thousands of slivers that mean less than the picture |
| **a picture of something we already hold as vector** | **neither — use that vector** | tracing a screenshot of a class map we already have as attributed polygons would add error, not data |

The measurements (`vectorisation_study.py`, `vectorise_sheets.py`,
`legend_swatches.json`): the share of each class that survives a majority filter
(**purity**), the share sitting in components ≥ 200 px (**big_share**), fragmentation
per 1000 px, and the **round trip** — re-render the vectorised result and compare it
with the classified source.

## The verdicts

| sheet | 90 % of the area is… | round trip | verdict | why |
|---|---|---|---|---|
| `raster_soil_ph` | 5 flat classes | 0.986 | **polygons** → `poly_soil_ph` | 111 polygons, 906,612 km², 5 classes, 99.94 % of the territory covered; colour agreement at polygon interior points **100 %** within dE 24 (median 1.8) |
| `raster_population` | 5 flat classes | 0.958 | **polygons** → `poly_population` | 299 polygons, 839,255 km², 92.51 % of the territory covered; agreement **99.3 %** within dE 24 (median 1.7) |
| `raster_general_geology` | 9 flat classes | 0.907 | **neither** → `geology_era` | it is a simplified picture of `geology_units`, which we already hold as 97 attributed polygons. The era classes are **dissolved from that vector**, not traced from a 2.5 km/px screenshot. (The dissolved layer has **7** classes; the sheet's legend draws 9, but they are era *plus lithology* — so this is a coarser generalisation of that sheet, not a reproduction of it.) |
| `raster_temperature` | **4 colours** | 0.992 | raster | the cleanest flat map in the set by colour, but it is a *smooth field*: the class boundary is an isotherm drawn through a continuous surface, and the printed classes are 16 bands whose swatches cannot even be read off the page (6 detected of 16). Polygons would invent hard edges the climate does not have |
| `raster_ethnic_groups` | 32 classes, 88 % flat edges | 0.985 | raster | schematic, 32 classes and a 2-px-thick black surround; its legend swatches could not be read (8 of 32 detected), so a polygon layer would carry unverified class labels |
| `raster_landcover` | 14 classes | **0.858** | raster | the coarsest sheet (3.05 km/px) — polygonising it turns texture into slivers, and 14 % of the classification is lost to the minimum-area rule |
| `raster_dominant_soils` | 20 classes, 0.17 km/px | 0.953 | raster | 10,234 px wide with five inset panels; a vector copy would be ~300,000 vertices of a scan *of* a soil map, at 0.7 km/px, to no benefit |
| `raster_dem` | 7 classes + hillshade | 0.980 | raster | it is a *picture of an elevation model*: the shading varies inside every class, and the class boundaries are contours. Polygons of contours are the wrong product entirely |
| `raster_forest_reserves` | 2-colour fill | 0.980 | raster | it is a reserve/river map with dotted patterns and 0.48 km/px at working resolution; the reserves are already available as better data elsewhere, and its own border is ~100 km out in the north-west (see `RASTER_LAYERS.md`) |

Rasters are kept for **all nine**. The two that became polygons keep their raster
too, so nothing was taken away.

## What the test caught

1. **The transcribed legend colours were wrong.** `IMAGES` listed colours up to
   **dE 100** from the ink actually on the page (median 15–27). The new
   `read_legend_swatches.py` measures the printed swatches instead — solid
   rectangles, found by shape, grouped into stacks, sorted — and those measured
   colours are what `poly_soil_ph` and `poly_population` carry in `legend_hex`.
   For soil pH the measured swatch is `#7df901`; the transcription said `#5fd63f`.
   The polygon layers are right *because* of this correction, not despite it.
2. **A first attempt attached labels by area order** — the biggest class got the
   first legend row. That is arbitrary and was discarded; labels now come from the
   measured swatch order. `check_polygon_colour.py` now tests the claim on every
   polygon, at an interior point (a centroid can fall outside a crescent and read
   the wrong class): for soil pH **106 of 111** polygons sample a sheet pixel
   within dE 24 of their own swatch — the other five have their interior point
   outside the sheet's pixel footprint, where the printed plate stops short of the
   border (see the per-side offsets in `RASTER_LAYERS.md`) — and for population
   **297 of 299**. Three population polygons read a pixel nearer a *neighbouring*
   swatch than their own (310 km², 434 km² and 2,346 km²); that is the row
   classification at 2.4 km/px disagreeing with the traced fill by one class, and
   it is reported rather than hidden. `polygon_colour_check.json` holds every
   sample.
3. **Polygonising without clipping to the country produced a "Nigeria" of
   930,000 km²** — the plate mask includes painted sea and paper margins. Every
   polygon is now intersected with `national_territory`.

## What the two traced layers cover, and what they leave blank

A traced class map is only complete where the sheet is. Measured against
`national_territory` (`audit_layers.py` → `layer_checks.class_polygons`,
`vector_layers_report.json`):

| layer | polygons | km² | share of the territory covered | left blank | largest blank | what the blank is |
|---|---|---|---|---|---|---|
| `poly_soil_ph` | 111 | 906,612 | **99.94 %** | 545 km² in 143 pieces | 177 km² | seams and ink between fills |
| `poly_population` | 299 | 839,255 | **92.51 %** | **67,902 km²** in 1,786 pieces | **26,116 km²** (north-east corner) | the sheet prints no class there |

**Seam repair, applied to soil pH and deliberately not to population.** Before
the repair the soil-pH layer left 33,575 km² unclassified in 974 pieces, and
measurement of those holes against the classified raster showed **96.2 % of them
within 3 px of a fill**: they are the ink line between two colours and the
letters of place names, not missing data. So unclassified pixels within 3 px of
a class are now claimed by the nearest class (`fill_gaps_px` in
`build_vector_layers.py`), which is what took the blank from 33,575 km² to
545 km². The same test on the population sheet says the opposite — only 26.8 %
of its blank pixels are within 3 px of a fill and **66.9 % are more than 12 px
away** — so nothing is filled there: a district the sheet does not colour stays
uncoloured rather than acquiring an invented population class.

The repair has one exemption: the dark-navy swatch whose label cannot be read
(below) is not used as a *source* for filling. Ink lines are dark, dark navy is
the nearest legend colour to them, and filling from it would quietly grow the one
class whose meaning is unknown — it did, by 624 km², in the first version of this
repair, which is how the exemption was found.

## The legend swatch that cannot be read

Class 1 of the soil-pH sheet is printed in dark navy (`#00227b` measured) with no
readable value beside it; the hand transcription had recorded the label as `0`,
which reads as a pH of exactly zero and is not something the sheet says. The
swatch itself is real — 2,422 raster pixels lie within dE 30 of it, against 15
near-black pixels, so it is a printed fill and not a scanning artefact — so it is
kept, named `unlabelled (dark navy, legend swatch 1)`, and measured: 3,209 km² in
4 polygons. Naming it `0` would have been an invented value; dropping it would
have deleted a real class. The name now says what is known and no more.

## What the file itself claims

A GeoPackage can read perfectly and still misdescribe itself. Two checks were
added because the earlier audit's "0 problems" did not cover them:

* **Registers** (`fix_gpkg_hygiene.py`, `gpkg_hygiene_before.json` →
  `gpkg_hygiene.json`). The shipped file carried **16 `gpkg_extensions` rows for
  things that do not exist** — 7 for exploratory layers dropped long before
  (`poly_dem`, `poly_landcover`, …) and 9 declaring an rtree index on the
  `tile_data` BLOB of each raster, which cannot be indexed — plus **7 orphan
  `rtree_*` index tables** for the dropped layers and **17 spatial indexes that
  existed but were never declared**, so no conforming client could use them. All
  17 are now declared, the 23 dead rows and 7 dead indexes are gone, and every
  feature layer has exactly one declared, present index.
* **Tile pyramids.** GDAL declares a `gpkg_tile_matrix` zoom level for every
  overview it *could* write; these rasters are single-resolution, so 29 of the 38
  declared levels held no tiles at all. A client that trusts the matrix asks for
  a tile that was never written and draws nothing when zoomed out. The matrix now
  declares exactly the one level per raster that holds tiles (38 → 9 rows).
* **Descriptions.** `gpkg_contents.description` was empty for **all 40 layers** —
  nothing inside the file said what a layer was, where it came from, or what it
  must not be used for. `describe_layers.py` now writes a description for every
  layer, caveats included, and `audit_layers.py` fails if one is blank.

None of this removes data: 31 feature layers, 9 raster layers, 60,555 features and
every tile are still there, and `gpkg_hygiene.json` records each register entry
that was corrected.

## Where the numbers live

| file | what it holds |
|---|---|
| `vectorisation_study.json` | per-sheet purity, big-share, fragmentation, round trip, per-class detail |
| `vectorise_sheets.py` | the conversion itself (k-means palette, majority filter, sliver floor, clip, measure) |
| `legend_swatches.json` | the measured swatch colours and positions, per sheet |
| `vector_layers_report.json` | what `build_vector_layers.py` wrote |
| `polygon_colour_check.json` | `check_polygon_colour.py`: every polygon's sheet pixel against its own swatch |
| `vector_layers_qc.png` | the three layers drawn, with the ground the sheets leave blank in grey (`make_vector_qc.py`) |
| `layer_descriptions.json` | the description now stored for each of the 40 layers |
| `gpkg_hygiene.json` / `gpkg_hygiene_before.json` | the register entries corrected, and the state they were found in |
| `layer_audit.json` | `audit_layers.py`, including the GeoPackage-conformance checks |

Reproduce: `python read_legend_swatches.py && python build_vector_layers.py &&
python describe_layers.py && python make_vector_qc.py && python check_polygon_colour.py
&& python audit_layers.py`.
