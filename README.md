# Nigeria geology polygon layer

A polygon layer of the geology of Nigeria, one feature per legend label, built from the two pictures in this repository:

- `pic NGSA geological-map-of-nigeria-.jpg` (**picture 2**): NGSA geological map of Nigeria, 6600 × 3675 px. Its linework is the geometry source.
- `pic geology of nigeria.png` (**picture 1**): a second geology map of Nigeria with an 86-entry legend. Its colour groups are used as the second opinion for each polygon's name. Its source is not stated in the image and I could not identify its edition.

## Deliverables

| File | What it is |
|---|---|
| `nigeria_geology.gpkg` | GeoPackage, layer `nigeria_geology`, EPSG:4326 (WGS 84 lon/lat), 77 MultiPolygon features |
| `tables/nigeria_geology_attributes.csv` | The GPKG attributes without geometry |
| `tables/legend_p2_crosswalk.csv` | The 92 picture-2 legend rows, their picture-1 counterpart, and whether the label has a polygon |
| `tables/legend_p1_crosswalk.csv` | The 86 picture-1 legend entries, their colour group, and the mapped picture-2 rows |
| `qa/qa_predicted_vs_zoom.png` | The layer rendered in its legend colours: whole country (left) and a 3.5° × 3.3° zoom (right) |
| `scripts/` | Pipeline scripts and small parameter files (see *Reproducing*) |

GPKG fields:

- `name`: legend label, as printed in the picture-2 legend. One feature per label.
- `codes`: NGSA legend code(s) for the label.
- `legend_rows`: picture-2 legend row numbers that share this label.
- `p1_equivalent`: picture-1 legend entries mapped to this label by name.
- `colour_hex`: dominant map colour of the label's colour clusters.
- `colour_dE_median`: median CIE Lab distance (ΔE) between the map colour and the label's legend swatch.
- `p1_support`: area-weighted share (0–1) of picture-1 colour votes that fall in the picture-1 colour group(s) of this label. Blank if the label has no picture-1 counterpart.
- `confidence`: `high`, `medium` or `low` (rules below), decided by the largest share of the feature's area.
- `area_km2`: area in km², computed in the equal-area projection EPSG:6933.
- `n_colour_clusters`: number of picture-2 colour clusters merged into the feature.

## Legend counts (taken before building)

- Picture 1: **86 legend entries** (35 in the top-right panel, 51 in the bottom panel).
- Picture 2: **92 printed rows** (48 sedimentary/volcanic + 44 basement), which are **86 distinct label texts**. Six labels appear twice: Sandstone and Clay (rows 12/14), Shale and limestone (15/28), Limestone (19/30), Blackshale (41/43), Sandstone (42/45), Rhyolite (55/56).
- Output: **77 features**, which is within the 86-label limit. Nine labels have no polygon (see Limitations).

## Input checks and research

- **Source of picture 2.** NGSA lists its "Geological Maps of Nigeria 1:2,000,000" among its downloadable national products [1]. The 2004 national map is cited as "The Geological Map of Nigeria", Nigeria Geological Survey Agency, Abuja, 2004 [2]. Picture 2 carries the same title, so it matches this series.
- **Placement of picture 2.** Its plate-carrée graticule (meridians 3–14°E, parallels 10–13°N) is straight. A linear georeference fitted to it is x = −576.730 + 328.3601·lon and y = 4752.100 − 328.2750·lat, in pixels of the full-resolution JPEG. Its outline against the Natural Earth 1:10m Nigeria boundary (world-atlas 2.0.2) has a median offset of **2.3 km** (90th percentile 11.7 km).
- **Placement of picture 1.** A spherical Lambert conformal conic was fitted to its graticule (6°N to 14°N, 4°E to 12°E). The median gridline residual is **0.33 px**. The forward projection reproduces six measured gridline intersections, and the round-trip error is 0 px. Its colour field also covers slivers of Benin, Cameroon and Chad, so only pixels inside the Nigeria outline are used. Its outline against Natural Earth has a median offset of 10.7 km (90th percentile 30 km), and the larger tail comes from those slivers.

## Method

1. **Map colours.** Picture-2 pixels (3 × 3 median filter) were binned in CIE Lab. Well-populated bins (≥ 30 pixels) were average-linkage clustered into **651 colour clusters**. The remaining bins join the nearest cluster within ΔE 6.
2. **Legend swatches.** Every legend row's swatch was measured: 92 rows in picture 2 and 86 entries in picture 1. The picture-1 palette repeats: its swatches fall into **12 colour groups** (ΔE < 3), with 7–8 entries each. Picture 1 can therefore only say which group a unit belongs to, not which unit it is.
3. **Crosswalk.** Picture-2 rows are linked to picture-1 entries by name (`legend_tables.py`, `P2_TO_P1`). Entries marked `approx` are less certain. Five further name links were added after checking the unmatched picture-1 entries (`EXTRA_P1` in `label_clusters.py`): rows 41 and 43 to entry 45, row 11 to entry 51, row 25 to entry 53, and row 61 to entry 69.
4. **Cluster labelling.** Each colour cluster receives the one legend label that minimises
   `cost = min(ΔE, 8)/6 + 0.02·ΔE + w·(1 − P1 share of the label's colour group)`,
   with `w = 1 + 2·clip((ΔE − 4)/4, 0, 1)`, where ΔE is the distance to the label's nearest swatch. Picture 1 therefore gets more weight when the map colour is far from every swatch, and exact colour matches (ΔE ≤ 4) keep the legend colour in charge. Labels with no picture-1 counterpart get a neutral penalty of 0.9·w, so they cannot absorb unmatched areas by default.
5. **Smooth boundaries.** The grid is 0.002° (≈ 220 m). Each label's indicator is Gaussian-smoothed (σ = 1.6 cells ≈ 350 m) and normalised. The border between two labels is the zero contour of (own score − best competitor's score), so neighbouring polygons share exactly the same edge. The contours are polygonised. Specks under ≈ 1.2 km² are merged into the neighbour with the longest shared edge. The result is simplified with a coverage-preserving tolerance of 0.001° (≈ 110 m, well below the printed line width at 1:2,000,000). The file has 1.35 million vertices and is 24 MB.
6. **Clipping and masks.** Features are clipped to the Nigeria outline. Lake Chad (blue, lon 12.55–13.6°E, lat > 12.6°N) is masked. Unknown cells (3.6% of the grid before filling) are filled from their neighbours.

## Checks

- **Coverage** (equal-area projection): Nigeria 907,490.5 km²; layer 907,490.7 km². Uncovered area is 0.4 km² (0.00004%) and area outside Nigeria is 0.6 km². There are no overlaps, and all geometries are valid.
- **Agreement with both pictures**, sampled at 150,000 random points inside Nigeria:

  | Confidence | Points | Map colour within ΔE 4 of label swatch | Picture-1 group consistent with label |
  |---|---|---|---|
  | high | 32,071 | 81% | 65% |
  | medium | 48,178 | 37% | 58% |
  | low | 69,751 | 13% | 53% |
  | all | 150,000 | 35% | 57% (95,224 points with picture-1 evidence) |

  The picture-1 figure is partly circular, because picture-1 groups were used to choose labels. It measures consistency, not accuracy. No independent ground-truth map was available, so the names have not been validated against an authoritative dataset.
- **Confidence rule**, applied to the colour clusters that make up each feature:
  - `high`: map colour within ΔE 4 of the label's swatch, and at least 50% of picture-1 votes in the label's group.
  - `medium`: map colour within ΔE 4, or within ΔE 12 with at least 50% picture-1 agreement, or at least 80% picture-1 agreement.
  - `low`: everything else.

  The result is 10 high features (21.6% of area), 35 medium (31.9%) and 32 low (46.5%).

## Known limitations

1. **Colour shift is the main limitation.** Most map colours are more saturated than the legend swatches, and only 35% of sampled points match their label's swatch within ΔE 4. For the rest, the name rests on picture 1's 12 colour groups, which is a coarse guess. The largest low-confidence features are Sandstone (103,755 km²), Migmatitic gneiss (84,364 km²), Porphyroblastic Gneiss (82,690 km², colour ΔE 54) and Shale and mudstone (29,262 km², ΔE 37). Check these first.
2. **Identical or near-identical legend colours.** Rows 18 (Shale) and 34 (Siltstone and Sandstone) share one swatch. Rows 1 (Alluvium) and 77 differ by ΔE 1.5, and rows 31 and 43 by ΔE 2.7. Colour alone cannot separate the members of each pair.
3. **Nine legend labels have no polygon.** None of their swatches won a sizeable colour cluster, or their colour is shared with another label:
   - Sand,Clay and Swamp (row 5)
   - Limestone (rows 19, 30)
   - Siltstone and Sandstone (row 34)
   - Shale,limestone and sandstone (row 35)
   - Granites and granite porphyry (row 53)
   - Meta Volcanic Meta Sedimentary including pebbly schist (row 71)
   - Quartzite, massive and schistose, also occuring as ridges (row 77)
   - Banded gneiss / biotite gneiss (row 86)
   - Mylonites (row 91)

   Their absence reflects colour matching, not a finding that these units are missing from the map.
4. **Small units.** Specks under ≈ 1.2 km² were merged into neighbours, so the smallest outcrops are not separated. The layer has 8,120 interior rings, which are small units nested inside larger ones.
5. **Picture 1 is only a second opinion.** It is not clipped to Nigeria, and its palette repeats 12 colours. Its colours cannot validate picture-2 colours directly.
6. **Names are transcribed by hand** from the legend images. Check spelling against the source before publishing.
7. **Not an official product.** This is an inferred, colour-based layer. For authoritative use, obtain NGSA's own digital data.

## Reproducing

The scripts are in `scripts/`. Their paths point to a scratch folder (`/home/user/work`), and they were run as provided. Adjust the paths before rerunning them elsewhere. They need Python with numpy, pillow, scipy, scikit-image, shapely 2.x, pyogrio, pyproj, geopandas and opencv-python-headless.

Run order:

1. `swatch1b.py` (picture-1 swatches) and `swatch2c.py` (picture-2 swatches), then `legend_tables.py` (legend text and crosswalk).
2. `georef.py`, `fit_lcc.py` (writes `data/p1_lcc_params.json`), `p1grat.py`, `p1grat2.py`, `p2grat.py`, `p2grat2.py`, `check_fwd.py`, `validate_outline.py`.
3. `color_groups.py`, `label_clusters.py`, `build_layer.py`, `write_gpkg.py`, `make_tables.py`, `render_final.py`, `qa.py`.

The Natural Earth Nigeria boundary comes from the `world-atlas@2.0.2` npm package (countries-10m), converted with `topo2geo.js`.

## Sources

1. NGSA, "Geological Mapping" (lists the Geological Maps of Nigeria 1:2,000,000): https://ngsa.gov.ng/geological-mapping/
2. NGSA, "The Geological Map of Nigeria", Nigeria Geological Survey Agency, Abuja, 2004: https://www.scirp.org/reference/referencespapers?referenceid=876652
