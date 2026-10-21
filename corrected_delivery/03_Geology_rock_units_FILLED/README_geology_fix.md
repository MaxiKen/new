# Geology rock units — gap-filled (what was done)

**Layer:** `nigeria_geology_units_FILLED.shp` (1,502 polygons, EPSG:4326) + QGIS style `nigeria_geology_units_FILLED.qml` (categorized by `code`, printed-legend fill colours).

## Problem in the previous delivery
The original `nigeria_geology_units.shp` (kept here as `nigeria_geology_units_ORIGINAL_with_gaps.shp`) left **9,764.6 km² of inland gaps** inside Nigeria and **overflowed the national boundary by 5,945.8 km²**, and its polygons overlapped each other by 8,835 km².

## Fix (extension method — as instructed)
1. Started from the original polygons **with their holes**.
2. Overlaps were resolved by print order: where polygons overlap, the unit printed **on top in the PDF (later draw order)** wins. This rule was verified by sampling the printed colour at overlap locations on the georeferenced picture.
3. Everything was clipped exactly to the Nigeria boundary (`../01_Nigeria_boundary/`).
4. **950 gaps (9,765.67 km²) were filled by EXTENDING the surrounding existing polygons** into the empty space:
   - 817 gaps with several neighbours: split between neighbours along nearest-distance (Voronoi) lines, so each neighbour grows into the part of the gap closest to it;
   - 122 gaps with a single neighbour: given entirely to that neighbour;
   - 10 gaps: extended from the neighbour sharing the longest border.
5. **New polygons were NOT created — with one necessary exception:** Lake Chad open water (5,443.2 km²), where the printed map shows lake, not rock. It is one polygon with `code = WATER`.
6. 41 original features disappeared completely because they were entirely covered by later-printed units on top of them (logged in `dropped_features_log.csv`; the codes OGe and Ts vanish for this reason).

Per-gap audit trail: `gap_fill_log.csv` (950 rows: gap area, method, receiving unit). Area change per legend code: `area_by_code_before_after.csv`. Field `fix_flag` marks every polygon: UNCHANGED 815 / EXTENDED 597 / TRIMMED 89 / NEW_WATER 1.

## Validation
Final layer tiles Nigeria **exactly**: union area = 907,499.0 km² vs boundary 907,499.6 km²; remaining gap and overflow = 0.0 km² at computation precision (an independent re-computation in an equal-area projection reproduces the tiling to within 0.2 km² of border sliver tolerance); all geometries valid. See `geology_filled_QA_report.json` and the maps in `../QA_maps_and_reports/` (full map, extension-areas map, 5 border zooms). You can also overlay this layer on `../02_Georeferenced_map_pictures/Geological_Map_of_Nigeria_MAPFRAME_georeferenced.tif` to compare every boundary with the printed map.
