# Additional selected PDF layers

These are **new, separate outputs**. Existing `shapefile_results/geology/`, `shapefile_results/minerals/`, and `nigeria_shapefiles.zip` were not overwritten. All included vector layers use **EPSG:4326** and have `.prj` and UTF-8 `.cpg` sidecars.

## Geology PDF — G1–G5

The local geology PDF is raster-only. These five layers were reused from the matching 2011 vector edition in the public extraction repository `https://github.com/MaxiKen/site` at commit `138e9619fb8c1fad257f8cdefd3d03c51f6fb5c6`. Their coordinates already use the same graticule affine as the existing local geology rock-unit output; they were copied without changing geometries or attributes and were not clipped.

| Code | Layer | Features | Geometry |
|---|---|---:|---|
| G1 | `G1_geological_boundaries` | 2,819 | POLYLINE |
| G2 | `G2_faults` | 648 | POLYLINE |
| G3 | `G3_fold_axes` | 90 | POLYLINE |
| G4 | `G4_ridges` | 2 | POLYLINE |
| G5 | `G5_volcanic_plugs` | 68 | POINT |

The source attribute schemas are preserved; the only sidecar change is an explicit EPSG:4326 `.prj`. See `geology_2011/georeferencing.json` and `geology_2011/qa_report.json`. **G5 caveat:** the 68-feature `volcanic_plugs` output is a point-mark interpretation; the source map's legend sample is line-like, so do not treat these as verified volcanic-pipe linework or body polygons.

## Mineral PDF — M2

- `minerals_2023/M2_geology_areas.shp` contains the seven generalized area classes from the Mineral PDF legend. Six classes were matched to their raster swatch colors; the Gneiss–Migmatite–Granite Complex was derived as the residual white class. Its classification confidence is lower. Pattern gaps and map overprints were generalized at the native raster resolution.
- `minerals_2023/M2_pegmatite_marks.shp` contains 23 printed `P` marks as **points**. They are map marks, not body outlines or survey locations. The original source `/VP` coordinates are retained as `vp_lon` / `vp_lat`; `lon` / `lat` and point geometry use the same boundary-fit transform as the existing local Mineral outputs. The `adj_km` field records the per-point coordinate shift. Other source attributes are retained verbatim; `near_loc`, `near_km`, `near_mins`, and host-unit fields were not recalculated after the coordinate adjustment.
- `minerals_2023/M2_source_raster_75dpi.png` is the extracted image-only base used for polygonization; its coordinate mapping is documented in `minerals_2023/georeferencing.json`. Do not use the source repository's `.pgw` for this output.
- The Mineral PDF used here is byte-identical to the local input PDF (SHA-256 recorded in `georeferencing.json`). The PDF embedded `/VP` transform was not used.

The area classes are Alluvium, Quaternary Sediments, Tertiary Sediments, Cretaceous Sediments, Younger Granite Complex, Gneiss–Migmatite–Granite Complex, and Schists. The map legend also depicts Sand Bars as a line symbol; it is not one of the seven area classes and was not extracted as a separate line layer.

The polygon layer contains **572 features** (connected polygon parts): Alluvium 25, Quaternary Sediments 16, Tertiary Sediments 7, Cretaceous Sediments 14, Younger Granite Complex 29, Schists 36, and residual Gneiss–Migmatite–Granite Complex 445.

The native M2 raster sampling interval is roughly **0.68 km per pixel** near Nigeria; this is pixel spacing, **not a measured positional error**. The raster contains mineral symbols/text over the geology fills. The fixed Nigeria Admin-0 reference polygon was used to restrict M2 polygons to Nigeria; the G1–G5 source layers were not clipped. A follow-up comparison against the 2011 vector geology did not support replacing or snapping any M2 class boundaries, so no M2 geometry was changed. See `minerals_2023/M2_accuracy_assessment.md` for the crosswalk and georeferencing checks, and `minerals_2023/qa_report.json` for the extraction QA.

## Separate bundle

`shapefile_results/nigeria_pdf_selected_layers.zip` contains this folder only. The earlier `nigeria_shapefiles.zip` is unchanged.
