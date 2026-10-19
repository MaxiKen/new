# Nigeria Geology & Mineral Resources GIS Deliverable (REBUILT)

Rebuilt from the four supplied sources only:
- `pic NGSA geological-map-of-nigeria-.jpg` (NGSA geological map scan)
- `NGSA_map_geology_legend_isolated.png` / `_v2.png` (isolated geology + legend)
- `Mineral_Resources_Map_of_Nigeria_2023 (2).pdf` (NGSA Mineral Resources Map 2023, ArcMap PDF)

All vector data are **WGS84 (EPSG:4326)**, latitude/longitude degrees.

## Contents
```
01_Georeferenced_Rasters/   GeoTIFFs of both map pictures (see Georeferencing note)
02_Shapefiles/              Nigeria_Boundary, Geology_Rocks (+ .qml), Minerals,
                            Minerals_NEEDS_REVIEW, Rivers, Nigeria_LandBorder_NGSA2023
03_QA_Check_Plots/          visual check plots (geology whole country + 2 details; minerals per zone A-G)
04_Tables/                  GCP tables, geology colour/legend tables, transcribed mineral index,
                            full mineral point table
```

## Point-by-point against your review
1. **Geology map picture** – included: `Geology_Map_of_Nigeria_NGSA_map_only.tif`
   (and the full sheet). Georeferenced on its printed 1° graticule (RMS ≈ 0.3 px);
   independent checks against Natural Earth towns/boundary showed **no shift** for this map.
2. **Mineral map picture** – included and properly georeferenced:
   `Mineral_Resources_Map_of_Nigeria_2023_map_only.tif` (+ full sheet, + the native
   symbols-layer raster at its original resolution). See SHIFT note below — the files
   *without* `_AS_PRINTED_GRATICULE` in the name are the true-WGS84 versions to use.
3. **Whole-Nigeria boundary** – included: `Nigeria_Boundary.shp` (913,009 km²; NGSA 2023
   land border + coastline/river closure, validated against Natural Earth admin-0).
   The land-border line exactly as printed on the mineral map is `Nigeria_LandBorder_NGSA2023.shp`.
4. **Geology gaps/holes** – fixed the way you instructed: **no new polygons were invented.**
   Coverage inside the boundary is now **100.00000 % (35,288 polygons, 86 rock units,
   913,009 km², gap 0.00000 km²)**, achieved only by *extending the existing neighbouring
   polygons* into the artefacts (the supplied isolated-geology picture is itself complete;
   the earlier holes came from the old conversion, and the picture's missing far-west strip
   was regularized westward from its own edge polygons and the Lake Chad basin fill was
   extended from surrounding units — see `SRC` field). Rock names/codes were matched by
   colour (CIELAB) to the transcribed 92-row printed legend: 71 units High confidence,
   14 Medium, and the large coral Older-Granite unit follows the map-face label **OGp**
   (it has no entry in the printed legend list; closest legend row is OGh — flagged Medium).
   Full audit trail: `04_Tables/Geology_legend_match.csv`, `Geology_legend_transcribed.csv`.
5. **Minerals** – completely redone from the map's own symbol layer at native resolution:
   - 67 legend symbol templates were extracted from the PDF legend itself. Note: the PDF
     stores the legend strip images **upside-down** — this was detected and corrected.
   - Every symbol on the map was searched: template matching (complete match first),
     ink-blob segmentation, cluster splitting (partial matches, still centred), green
     pattern-patch detection (Limestone/Marl), and a number-guided rescue pass.
   - **One point per symbol**: duplicates suppressed (no two points within 8.5 px on the
     native raster ≈ half a symbol width); each point is at the **calculated centre of the
     symbol's ink bounding box** (for pattern patches, the patch centre).
   - All 987 printed occurrence numbers were extracted from the PDF text and assigned to
     points; the printed index (1,141 entries) was transcribed, so numbered points carry
     ZONE / NUMBER / LOCALITY / MINERAL. 911 numbers sit on a detected symbol, 59 share a
     symbol (recorded as ALT_NUM — still one point), 17 could not be paired (area-type
     occurrences with no point symbol: the point is placed at the printed number, in
     NEEDS_REVIEW, MATCH=NumberOnly).
   - Result: `Minerals.shp` **1,227 points** (772 numbered, 455 un-numbered symbols that
     are printed on the map but not in the index), plus `Minerals_NEEDS_REVIEW.shp`
     (370 uncertain items) kept separate so the main file stays clean.
   - `MATCH` field: Complete (825, full symbol match) / Partial (402, cluster/pattern/
     rescued matches). Random-sample visual audit of un-numbered points: real symbols.
6. **Rivers** – confirmed OK and finalised: extracted from the PDF's own vector river
   layer (not traced from raster), **all streams kept incl. the smallest** (shortest kept
   segment 0.07 km; only <50 m clip slivers dropped). Final: `Rivers.shp`, 910 features,
   37,792 km inside Nigeria (clipped to `Nigeria_Boundary.shp`).

## IMPORTANT georeferencing note (the "shift")
The mineral map's printed graticule is **internally shifted** with respect to its own
drawn geography. Independent control (Natural Earth boundary Chamfer fit + 68 towns)
gives: **true WGS84 = printed graticule + (0.162°, −0.002°)** for the mineral map only.
All delivered mineral-map products (rasters without `_AS_PRINTED_GRATICULE`, Minerals,
Rivers, LandBorder) already have this correction applied, so they align with the geology
map, the national boundary and real-world WGS84 data. `_AS_PRINTED_GRATICULE` copies are
kept for reference — do not mix the two. (The geology JPG needed no correction. Note the
mineral map's own town dots have a separate small mis-registration in the source artwork;
the correction follows the national border/coastline, the most reliable frame.)

## How to visually verify placement (QGIS)
1. Add `Mineral_Resources_Map_of_Nigeria_2023_map_only.tif`, then `Minerals.shp`:
   every green point in `03_QA_Check_Plots/QA_Minerals_Zone*.png` sits at a symbol centre.
2. Add `Geology_Map_of_Nigeria_NGSA_map_only.tif`, then `Geology_Rocks.shp`
   (load `Geology_Rocks.qml` for the original colours) and `Nigeria_Boundary.shp`.
3. Rivers/border overlay the mineral GeoTIFF exactly (same source PDF vector layers).

## Known limitations (please read)
- SYMBOL names for un-numbered mineral points are machine classifications (template
  scores in `SCORE`); similar symbols (e.g. coloured triangles) can be confused. For
  numbered points the MINERAL comes from the printed index and is authoritative.
- The printed index itself contains duplicate numbers and a few illegible entries;
  ~5 % of entries could not be transcribed (their points have blank LOCALITY).
  Locality spellings follow the PDF text layer (occasional split-letter artefacts
  were repaired where unambiguous; `Mineral_Index_transcribed.csv` keeps RAW_TEXT).
- Geology legend rows with identical fills on the printed map (e.g. Dsh≈Ts, NPss≈Psh,
  Kls≈Glls) cannot be separated by colour; the likeliest row was used and is flagged
  in `Geology_legend_match.csv` (small margin). Thin grey dyke units (D, ODh, OGS) are
  not present as separate colours in the supplied isolated-geology picture.
- Estimated positional accuracy: geology ≈ 400 m; minerals ≈ 250 m + source-map
  generalisation. Suitable for regional (1:2,000,000-class) use, not cadastral work.

*Methods/provenance: every processing step is scripted in `scripts/` (01–08, 06a–06l).*
