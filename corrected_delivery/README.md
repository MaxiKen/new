# Nigeria geology & minerals — CORRECTED delivery (2026-10-19)

This package fixes the previous delivery complaint-by-complaint. All layers are EPSG:4326.

## Your complaints → what was done

| # | Complaint | Fix |
|---|-----------|-----|
| 1 | Geology PDF picture missing from the zip; mineral picture poorly/not georeferenced | **Both map pictures are now georeferenced GeoTIFFs in the zip** (`02_Georeferenced_map_pictures/`): full-sheet + map-frame versions of each map, plus a symbols-only mineral base. Geology picture uses its printed graticule (verified against the national boundary, median offset ~1.2 km). The mineral map's *printed longitude graticule labels are displaced by 0.172° on the sheet itself*, so its picture and all mineral-map layers use the publisher's embedded map-frame georeferencing (PDF `/VP`), which matches the printed coastline/boundary to ~1 km. Overlay any shapefile on its picture to verify placement. Original PDFs are in `02.../source_PDFs/`. |
| 2 | Whole-Nigeria shapefile missing | Included: `01_Nigeria_boundary/nigeria_admin0.shp` (whole country, one MultiPolygon). States/LGAs in `07_Reference_layers/`. |
| 3 | Geology polygons have inland spaces/gaps | Rebuilt: `03_Geology_rock_units_FILLED/`. Started from the original polygons **with holes** and filled all 950 gaps (9,765.7 km²) by **extending the surrounding existing polygons** (nearest-extension split where several neighbours meet). No new polygons were created except one unavoidable case: Lake Chad open water. The layer now tiles Nigeria exactly — **0.0 km² gap and 0.0 km² overflow** within numeric tolerance (was 5,945.8 km² outside the border). Per-gap log + QGIS style (`.qml`) included. |
| 4 | Minerals poorly referenced — missing symbols, two points on one symbol, points not at symbol centres | Completely re-detected: `04_Minerals_RECENTRED/`. Every point (1,272) was placed at the **calculated centre of a printed symbol** by scanning the whole map with the **standard symbol mark taken from the printed legend** (complete-symbol matches first; partial matches only inside tight clusters, still centred on the full mark). One point per symbol is enforced. 77 previously missing symbols added; 33 old duplicate points removed; 99 old points that sit on no (or another mineral's) glyph are listed with reasons instead of being carried forward. Classes restored from zero include Copper, Nickel, Fluorite, Calcite. Full method, confidence fields and limits: `04.../README_minerals_fix.md`. |
| 5 | Confirm rivers; even small rivers must be included | The old river file was **not** okay — it held only 12 major rivers (35 segments). Replaced in `05_Rivers/` with **every river printed on the Mineral Resources Map 2023, including the small tributaries**: 1,447 features / 43,245 km as printed; 1,348 / 36,587 km inside Nigeria. Blank name = smaller printed tributary (the map doesn't name them). |

## Folders
- `01_Nigeria_boundary/` — whole-country boundary (the clip frame used throughout).
- `02_Georeferenced_map_pictures/` — 5 GeoTIFFs + index + source PDFs. Best for checking mineral centres: `Mineral_Resources_Map_BASEONLY_symbols_georeferenced.tif`; for geology overlay: `Geological_Map_of_Nigeria_MAPFRAME_georeferenced.tif`.
- `03_Geology_rock_units_FILLED/` — gap-filled rock units + original-with-gaps copy + logs + QML + legend.
- `04_Minerals_RECENTRED/` — corrected mineral points + QML + legend with counts + old→new reconciliation (all 1,486 old points accounted for) + shapefile of old points not carried forward, with reasons.
- `05_Rivers/` — complete printed river network (as-printed and Nigeria-only) + previous majors-only file for comparison.
- `06_Other_PDF_layers/` — 2011 geology vector layers (boundaries, faults, fold axes, ridges, volcanic plugs) unchanged; 2023 M2 geology areas + pegmatite marks **re-projected** to the same publisher frame as everything else.
- `07_Reference_layers/` — state and LGA boundaries.
- `QA_maps_and_reports/` — QA maps: geology filled + border zooms, mineral centre-check zooms (Jos, NW, SW), rivers before/after, symbol-template sheet.

## How to verify (2 minutes in QGIS)
1. Minerals: load `02.../Mineral_Resources_Map_BASEONLY_symbols_georeferenced.tif`, then
   `04.../nigeria_mineral_symbols_CORRECTED.shp` (style `.qml` loads automatically). Zoom anywhere —
   each point sits in the middle of its printed symbol; `PX_X/PX_Y` give the exact picture pixel.
2. Geology: load `02.../Geological_Map_of_Nigeria_MAPFRAME_georeferenced.tif` under
   `03.../nigeria_geology_units_FILLED.shp` — unit boundaries follow the printed map and no inland
   spaces remain.

## Accuracy notes
- Source pictures: geology ~335 m/px, mineral symbols ~670 m/px — point centres are good to about
  ±0.3 km; the mineral map is 1:2,000,000, so do not use these points for site-scale work.
- A few legend symbols are printed identically (white-circle and yellow-circle groups) and a few
  glyphs are only a few pixels wide (e.g. Beryl). Those points carry explicit confidence fields
  (`DET_SRC`, `LABEL_SRC`, `SCORE`) — see the minerals README before filtering.
- 7 of the 67 legend classes have no verified occurrence on the map face (Bitumen, Evaporite,
  Marcasite, Psammite, Silver, Tar Sand, Trona) — evidence is documented per class/point in `04.../`.
