# Nigeria mineral and geology shapefiles

All deliverables are in this folder, separate from the fixed reference polygon directory (`../shapefiles/nigeria_admin0/`). The reference outline is used for georeferencing QA only; it is not included in these layers and was not used to clip them.

## Layers

### Mineral symbols — points

`minerals/nigeria_mineral_symbols.shp` contains **793 point features**, one per mineral symbol printed on the map. Symbols were located on the 96 dpi map raster as saturated point-marker bodies (colour + body bounding box), with touching symbols split before measuring. Attributes: `type_id` / `n_type` (symbol type and how many points share it), `colour` / `colour_hex` / `rgb` (measured fill), `w`, `h`, `area` (body size in raster pixels), `mineral`, `conf`, `basis` and `in_nga`.

**436 of the 793 symbols (55%) are resolved to a mineral**, by comparing each symbol *type* with the printed legend markers (fill colour + body size + the code letter drawn inside the marker, e.g. `C` = Clay, `K` = Kaolin, `di` = Diatomite, `Ds` = Dimension Stone, `t` = Talc). Resolved names: Gold 124, Clay/Pottery Clay 107, Diatomite 60, Kaolin 59, Columbite 36, Talc 19, Dimension Stone 14, Mica 7, Limestone 5, Granite 5. The remaining 357 features keep their measured colour and body size and are left unnamed rather than guessed, because colour alone does not identify a mineral (the yellow family alone covers Gold, Clay, Pyrite, Glass Sand, Brine and Dimension Stone). `minerals/symbol_typology.csv` and `minerals/symbol_typology.png` list every type with a 6x example crop, so the unresolved types can be matched against the printed legend.

`minerals/nigeria_mineral_labels.shp` contains **985 point features**: the numbered occurrence labels printed on the map (vector text in the PDF, exact positions, values 0–256). These numbers refer to the seven zone tables printed in the map's explanation panel (zones A–G, each numbered separately); the tables give the locality and the commodity code for each number, so this layer can be joined to that table by `num` once the zone is identified.

`minerals/mineral_legend.csv` reproduces the 66 legend entries in printed order.

### Geology units — polygons

`geology/nigeria_geology_units.shp` contains **1,542 valid polygon/multipolygon features** representing mapped rock units only. It retains 32 attributes, including unit/code, legend description, formation/stratigraphic labels, printed age, normalized era/period/epoch, age range, rock class, and basin. `geology/geology_legend.csv` is included as a lookup.

## CRS and positional QA

All shapefiles are **EPSG:4326** and include `.shp`, `.shx`, `.dbf`, `.prj`, and UTF-8 `.cpg` files. Neither PDF's embedded CRS/geospatial transform was used.

- **Minerals:** the georeference is a least-squares fit of the map's printed 2-degree graticule (6 meridians, 5 parallels, 315.20 pt per 2 degrees): `lon = 4.0 + (x - 341.44)/157.62`, `lat = 13.0 + (y_up - 1636.47)/157.62`. It was validated against 478 printed town squares compared with GeoNames (median 0.152 deg / 16.9 km, driven by ambiguous town names); in the 129 best-matching pairs there is no detectable bias (median dx +0.0004 deg, dy -0.0075 deg). The printed international boundary agrees with the Natural Earth outline to **5.7 km median / 7.5 km p90**, which is the generalisation difference between the two sources. Symbol centres additionally carry about +/-0.7 km of source-raster resolution, so they are map-reading positions, not survey coordinates.
- **Geology:** an affine was fitted from the printed 1-degree graticule (12 meridians and 10 parallels), with maximum fit residual about **0.001054° (~117 m)**. The corresponding vector edition was used because the local PDF is image-based; its 72-dpi render aligns with the local map at zero shift with RGB mean absolute error about `[5.03, 4.76, 4.59]` on a 0–255 scale, and the unit records/attributes match the vector-edition candidate. Capital-label QA is about **8.1 km RMS**; the graticule is the stronger control.

These checks do not imply survey-grade accuracy: the maps are generalized and the fixed Natural Earth outline is generalized. Features were **not clipped** to that outline. 71 of the 793 symbols and 154 of the 985 occurrence labels fall outside the reference outline; they are retained because they are mapped occurrences (offshore oil and gas, border-zone deposits) and because the two outlines disagree by up to ~7 km near the border.

See each layer folder's `georeferencing.json` and `qa_report.json` for the transform, detailed checks, bounds, and counts. `nigeria_shapefiles.zip` is a convenience bundle of both result folders.

## Additional selected PDF layers (separate outputs)

The requested G1–G5 geology line/point layers and M2 mineral-map generalized geology polygons are in `pdf_selected_layers/`. This is a new folder; the existing geology/mineral layers and `nigeria_shapefiles.zip` were not overwritten. The separate archive is `nigeria_pdf_selected_layers.zip`. See `pdf_selected_layers/README.md` for layer counts, attribute notes, M2 raster-polygonization limitations, and coordinate adjustments. All new vectors are EPSG:4326.
