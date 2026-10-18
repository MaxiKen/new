# Nigeria mineral and geology shapefiles

All deliverables are in this folder, separate from the fixed reference polygon directory (`../shapefiles/nigeria_admin0/`). The reference outline is used for georeferencing QA only; it is not included in these layers and was not used to clip them.

## Layers

### Mineral symbols — points

`minerals/nigeria_mineral_symbols.shp` contains **1,486 point features**. Each point is an estimated center of a mapped mineral symbol. Attributes include the single mineral/category name, legend number, commodity group, identification method/score, source blob IDs, center-estimation method, locality/table context, and final coordinates. Every feature has one non-list `mineral` value; grouped symbols are labelled as groups rather than emitting ambiguous comma- or slash-separated alternatives. `minerals/mineral_legend.csv` maps those values to the original legend wording.

The symbol review consolidated 15 same-colour fragments, estimated all 8 half-symbol cases, and split 2 touching pairs. A separate template scan found 345 matches; its two unmatched peaks were reviewed as linework/overprint rather than added as mineral symbols. Six candidates without a corresponding single legend mineral and eight Psammite area-tint matches were withheld. QA counts and the per-name breakdown are in `minerals/qa_report.json`.

### Geology units — polygons

`geology/nigeria_geology_units.shp` contains **1,542 valid polygon/multipolygon features** representing mapped rock units only. It retains 32 attributes, including unit/code, legend description, formation/stratigraphic labels, printed age, normalized era/period/epoch, age range, rock class, and basin. `geology/geology_legend.csv` is included as a lookup.

## CRS and positional QA

Both shapefiles are **EPSG:4326** and include `.shp`, `.shx`, `.dbf`, `.prj`, and UTF-8 `.cpg` files. Neither PDF's embedded CRS/geospatial transform was used.

- **Minerals:** the map's vector international-boundary linework was parsed in page coordinates and independently registered to the fixed Nigeria polygon. The robust boundary-fit residual is about **0.90 km median / 2.77 km at the 90th percentile**. A separate check against 33 named capital positions is less consistent (**12.4 km RMS**); capital labels/markers are approximate and this check was not allowed to override the stronger boundary fit. The source symbol raster is about **0.68 km per pixel** (75 dpi at roughly 1:2,000,000), so symbol centers are estimates, not survey coordinates.
- **Geology:** an affine was fitted from the printed 1-degree graticule (12 meridians and 10 parallels), with maximum fit residual about **0.001054° (~117 m)**. The corresponding vector edition was used because the local PDF is image-based; its 72-dpi render aligns with the local map at zero shift with RGB mean absolute error about `[5.03, 4.76, 4.59]` on a 0–255 scale, and the unit records/attributes match the vector-edition candidate. Capital-label QA is about **8.1 km RMS**; the graticule is the stronger control.

These checks do not imply survey-grade accuracy: the maps are generalized and the fixed Natural Earth outline is generalized. Features were **not clipped** to that outline. Eight mineral points fall outside it (maximum distance about **7.0 km**) and are retained because they are mapped occurrences.

See each layer folder's `georeferencing.json` and `qa_report.json` for the transform, detailed checks, bounds, and counts. `nigeria_shapefiles.zip` is a convenience bundle of both result folders.
