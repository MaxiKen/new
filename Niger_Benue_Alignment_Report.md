# Which coordinate frame is right, and the corrected combined map

## 1. Short answer

**The mineral sheet is the one that was misplaced, and it was misplaced by its own coordinate definition, not by a datum shift.**

The 2023 sheet defines coordinates twice, and the two definitions disagree by **0.172° of longitude — about 19 km**:

| definition | longitude of the printed 4°E meridian |
|---|---|
| printed graticule (drawn meridians/parallels) | 4.0000°E |
| embedded GeoPDF `/Measure /GEO` | 4.1718°E |

The **mineral symbol point coordinates in the earlier files were computed from the printed graticule**, so they inherit the western biasing. They are now rewritten onto the embedded frame (`Minerals_Symbol_Points_CORRECTED.csv` / `.geojson`), a move of **+18.5 to +19.1 km east (median +18.9 km)** and **+0.02 to +0.11 km north**. No other transformation is applied.

The geology sheet has only one coordinate definition (its printed graticule, no embedded measure), so nothing about it needed rewriting.

**This is a correction of an internal inconsistency in one sheet. It is not a datum transformation and it does not make either map survey-accurate.**

## 2. What decided it: the sheet's own vector border

The mineral map body is raster, but its **international boundary is vector** (a pure-red stroke, ~7,000 vertices). The Natural Earth Nigeria outline was projected through each of the two definitions and compared with that drawn border:

| frame used to place the reference border | median offset from the sheet's drawn border | 90th percentile |
|---|---:|---:|
| printed graticule | **12.94 km** | 18.06 km |
| embedded GeoPDF measure | **1.06 km** | 3.15 km |

Under the printed graticule the reference border sits systematically ~19 km west of the red border actually drawn on the sheet; under the embedded measure it lands on it. The artwork was therefore laid out in the embedded frame. The best-fit residual translation for the embedded frame is −0.007°/−0.000°, i.e. already centred.

This is stronger evidence than the river test that preceded it, because it uses a line drawn by the map's own author at known national geometry, over its full length, rather than colour-segmented river pixels.

Note the same test is **not** usable on the geology sheet to prove that printed grid correct: a trial fit there wandered to a nonsensical +0.40° shift, which is a warning that the coastline control on that sheet is not a clean independent check. The geology printed graticule remains the only definition that sheet carries, so it is used, but its accuracy is not thereby proven.

## 3. The withdrawn river shift

The first draft applied an empirical **+0.0753°E / +0.0578°N** translation to the mineral sheet, fitted only to colour-segmented river pixels. Two things now argue against it:

1. After correcting the frame, the mineral sheet's river alignment in the embedded frame is **Niger median 6.43 km, Benue 1.87 km**, and a two-river fit lands at −0.082°/−0.035° (Niger) and −0.097°/−0.059° (Benue) in the *opposite* direction, scattered between the two rivers. River linework cannot pin it down better than that.
2. The withdrawn shift was previously shown to move the extracted town points ~10.7–10.8 km away from the geology comparison points. It is therefore discarded, and the corrected files carry no empirical displacement.

The vector border, not the rivers, is the control used.

## 4. Do the town points agree now?

The four previously hand-checked towns in `Town_comparison_three_sources.csv` are **not independent evidence**: earlier work confirmed those mineral markers were placed at fixed label-relative offsets rather than measured symbol centres, so they contain their own positional error. They also disagree with the corrected frame by roughly 10.7–10.8 km, in the same direction as the withdrawn shift. That disagreement is unresolved and is recorded rather than smoothed over. Symbol centres in the corrected dataset come from the glyph centroids, which is the more defensible measurement; the four town rows should not be used to re-litigate the frame.

## 5. Accuracy that must still be reported

* **EPSG:4326 is assigned as a display assumption.** Neither PDF states an established datum; the mineral metadata says `GCS_Assumed_Geographic_1` with a NAD27-family name, and no verified NAD27→WGS 84 transformation was performed. The internal 19 km inconsistency is fixed; the shared datum offset, if any, is not.
* Even in the correct frame the sheet's own border residual is ~1 km, and any georeferencing inherits that.
* Coordinates are for the **printed symbol glyphs**, whose centres are accurate to a few pixels (~0.5–1 km) at 75 dpi artwork. Commodity **names** are classification estimates (80.8% leave-one-out); per-mineral totals are unreliable and per-point names should be treated per the `tier`/`confidence` columns.
* The rivers are Natural Earth 1:10m generalised centrelines (World Data Bank 2 lineage), not surveyed channels; the two lines do not meet exactly at Lokoja and the confluence shifts over time.
* **Not for** licensing, exploration decisions, legal boundaries, navigation or surveying.

## 6. Files

| file | what it is |
|---|---|
| `Combined_Geology_Minerals_ALIGNED.png` | combined preview, minerals on the embedded frame |
| `Combined_Geology_Minerals_ALIGNED.tif` | the same as a georeferenced RGB raster |
| `Combined_Map_Layers.zip` | composite TIFF, corrected points, reference vectors, README |
| `Minerals_Symbol_Points_CORRECTED.csv/.geojson` | 1,323 symbols; new `lon/lat`, plus `lon_printed`, `lat_printed`, `lon_was`, `lat_was`, and per-point km shift |
| `Minerals_Symbol_Points_source.csv` | the original 1,323-point table recovered from the previous build |
| `Mineral_Registration_QC.png` | before/after control figure |
| `Correct_Mineral_Registration.py` | reproducible point rewrite |
| `Build_Aligned_Overlay.py` | reproducible combined layer |
| `Mineral_Registration_QC.py` | reproducible control figure |
| `Nigeria_Natural_Earth_outline.geojson`, `Niger_Benue_Natural_Earth.geojson`, `Nigeria_Rivers_Reference.png` | reference geometry (Natural Earth, public domain) |
| `CRS_Registration_Investigation.md`, `CRS_check.py` | earlier metadata/graticule investigation |

## 7. To make it authoritative

Obtain from NGSA the intended CRS and the source layers used to lay out the sheet, and a set of independently surveyed survey-grade control points distributed across the country. Then fit and hold-out-test a datum transformation and state a measured accuracy figure. Until then the combined map is a well-controlled internal alignment, not a certified georeference.
