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
| `raster_soil_ph` | 5 flat classes | 0.986 | **polygons** → `poly_soil_ph` | 115 polygons, 873,582 km², 5 classes; colour agreement at polygon centres **98.3 %** |
| `raster_population` | 5 flat classes | 0.958 | **polygons** → `poly_population` | 299 polygons, 839,255 km²; agreement **99.3 %** |
| `raster_general_geology` | 9 flat classes | 0.907 | **neither** → `geology_era` | it is a simplified picture of `geology_units`, which we already hold as 97 attributed polygons. The era classes are **dissolved from that vector**, not traced from a 2.5 km/px screenshot |
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
   measured swatch order, and the two shipped layers were verified against the
   raster at polygon centres (98.3 % and 99.3 % colour agreement).
3. **Polygonising without clipping to the country produced a "Nigeria" of
   930,000 km²** — the plate mask includes painted sea and paper margins. Every
   polygon is now intersected with `national_territory`.

## Where the numbers live

| file | what it holds |
|---|---|
| `vectorisation_study.json` | per-sheet purity, big-share, fragmentation, round trip, per-class detail |
| `vectorise_sheets.py` | the conversion itself (k-means palette, majority filter, sliver floor, clip, measure) |
| `legend_swatches.json` | the measured swatch colours and positions, per sheet |
| `vector_layers_report.json` | what `build_vector_layers.py` wrote |
| `vector_layers_qc.png` | the three new layers drawn |

Reproduce: `python read_legend_swatches.py && python build_vector_layers.py`.
