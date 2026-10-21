================================================================================
NIGERIA - GEOLOGY, MINERAL OCCURRENCES AND RIVERS (GIS DATASET)
Extracted from the official Geological Map of Nigeria and the Mineral
Resources Map of Nigeria 2023 supplied by the client.
All files are in the root of this zip - no folders.
Coordinate system of every file: WGS 84 geographic (EPSG:4326).
================================================================================

CONTENTS
--------
Georeferenced map images (for visual comparison / backdrop in any GIS):
  Geological_Map_of_Nigeria_georeferenced_lowres.tif
  Mineral_Resources_Map_of_Nigeria_2023_georeferenced_lowres.tif

Vector layers (ESRI Shapefile; .shp/.shx/.dbf/.prj/.cpg per layer):
  nigeria_boundary.shp             Whole-Nigeria boundary (1 polygon).
  nigeria_states.shp               36 States + FCT (37 polygons).
  nigeria_geology_units.shp        Geological rock units (1,501 polygons,
                                     complete national coverage - see below).
  nigeria_mineral_occurrences.shp  Mineral occurrence points (1,236 points,
                                     one point at the centre of every symbol
                                     found on the mineral map).
  nigeria_rivers.shp               Rivers and streams (1,344 reaches,
                                     37,175 km - including small streams).
  nigeria_river_labels.shp         84 river-name label points taken from the
                                     printed map (for map labelling).
  nigeria_pegmatite_fields.shp     23 pegmatite-field markers (the "P" labels
                                     printed on the mineral map).

Tables:
  mineral_legend.csv               The map's 67-category mineral legend, with
                                     the number of occurrences found per
                                     category in this dataset.
  mineral_localities_table.csv     Transcription of the locality tables
                                     printed on the mineral map (1,170 rows:
                                     map zone/number, locality, commodity
                                     codes and decoded mineral names).

--------------------------------------------------------------------------------
1. GEOREFERENCED MAP IMAGES
--------------------------------------------------------------------------------
Both supplied PDF maps were registered to WGS 84 from ground-control
information on the maps themselves (the geology sheet against its graticule;
the mineral sheet was fitted to the state-capital positions and boundary
because its printed graticule is shifted by about 18 km and must not be used).
Residual mis-registration is below ~1 km (median 0.9 km on the mineral map),
which is at the limit of what these small-scale printed maps support. The
images in this zip are intentionally moderate-resolution copies so that you can
overlay the shapefiles and verify that every feature sits where the printed
map puts it.

--------------------------------------------------------------------------------
2. GEOLOGY  (nigeria_geology_units.shp)
--------------------------------------------------------------------------------
The earlier version of this layer contained holes (unfilled spaces) inside the
country and overlapping polygons. It was rebuilt as a clean planar coverage:
  * 41 duplicate / completely overdrawn polygons were removed
    (1,542 source polygons -> 1,501 final features).
  * ALL interior gaps (9,765 km2 in total) were closed by EXTENDING the
    surrounding existing polygons into the gap (shared-boundary growth into
    the empty face). No new "invented" geology polygons were created; units
    simply continue to meet each other, and large gaps were shared between
    the neighbouring units along a medial boundary.
  * The field qa_flag records what happened to each feature
    ("unchanged" = 1,027, "extended", "trimmed", "overlap_adj", ...).
Validation of the final file:
  * Union of all polygons == national boundary exactly
    (symmetric difference 0.0000 km2, no gaps, no overhang).
  * Zero overlaps between polygons; all 1,501 geometries valid.
Attributes retained per polygon: unit name, legend code/description,
formation, stratigraphic group, age (printed age, period/epoch/era/eon,
numeric age range in Ma), rock class, basin, area, centroid, QA flag.

--------------------------------------------------------------------------------
3. MINERAL OCCURRENCES  (nigeria_mineral_occurrences.shp)
--------------------------------------------------------------------------------
Method (as requested - standard symbol first, point at the calculated centre):
  * A standard template was built for every one of the 67 legend symbols
    (from clear instances on the map, at the map's exact print scale).
  * The whole map face was searched exhaustively. Complete template matches
    were taken first; in dense clusters where symbols overlap, half-symbol
    (partial) matching was used so that partly-hidden symbols are still
    captured. In every case the point was placed at the centre computed from
    the standard symbol.
  * Each found symbol was linked to the numbered locality tables printed on
    the map (1,170 table rows, zones A-G). Field "stage" records how a point
    was obtained:
      1        complete match at its table number
      2/2core/2partial/2na
               matched at its table number, including partly-obscured
               symbols inside clusters
      3        extra symbol found by the full-map sweep (occurrence printed
               on the map but not itemised at a number)
      4audit   recovered in a final audit against the previous extract and
               re-verified against the symbol template
  * One point per symbol: duplicates within 5 map pixels were removed.
  * "id_score" is the template-match confidence (1.00 = pixel-perfect);
    "px_x/px_y" are the symbol-centre positions on the map image so you can
    cross-check any point against the georeferenced TIFF supplied.

Result: 1,236 points covering 60 of the 67 legend categories.
An audit against the earlier extract shows 80% of its points agree with the
new ones to within 8 map pixels; where they disagreed, the new point is the
one sitting at the exact symbol centre (the old file had offset, doubled and
mislabelled points, which is why this rebuild was necessary).

Important notes - symbols that the printed map does NOT actually show:
Visual inspection of the map face at every relevant table number confirmed
that for the following categories the locality is listed in the tables but NO
symbol is printed at the number. They therefore have few or no points, because
points were only placed where a real symbol exists:
  Asbestos (1): 0 found      Bitumen (8): 0 found (the Ondo belt occurrences
  Nickel (48): 0 found       are printed with the Tar-Sand symbol, no. 59)
  Trona (62): 0 found        Calcite (67): 0 found
  Psammite (50): 0 found     Saltlake (53): only 2 printed
  Uranium (63): only 4 printed (of 10 table entries)
Also:
  * Legend nos. 32 (Phosphate) and 49 (Phosphate Rock) use the identical
    symbol and the same table code "P"; all such symbols are recorded as 32.
  * Tin ("Sn" in the tables) is drawn with the Columbite symbol; those points
    carry mineral = "Columbite .." (no. 14) with table_code preserving "Sn".
    In the north-west several "Sn/Nb" localities print only the Tantalite
    (58) bowl, so only that point exists for them.
  * Of the 1,096 (number, mineral) occurrences implied by the tables at
    printed map numbers, 855 are matched to a symbol at that number; the rest
    have no corresponding symbol printed (see above) or are hidden under
    neighbouring symbols in the densest clusters.
  * Five points (creek/island and border symbols: Ikorodu, Port Harcourt,
    Akatafie Id, Jibiya, Ndigan) fall a short distance outside the generalised
    boundary polygon; they are exactly where the map prints those symbols.

--------------------------------------------------------------------------------
4. RIVERS  (nigeria_rivers.shp, nigeria_river_labels.shp)
--------------------------------------------------------------------------------
The rivers were taken from the vector "Rivers" layer stored inside the
official mineral-map PDF itself (892 drawn sections), georeferenced with the
same transform as the mineral points, merged into connected reaches and
clipped to the national boundary. This replaces the earlier 35-line river
file, which only carried the largest rivers.
  * 1,344 reaches, 37,175 km total - small streams and tributaries included
    exactly as drawn on the map.
  * "len_class" groups reaches by length (major >= 120 km, medium >= 35 km,
    minor < 35 km) - the PDF draws all rivers with one line weight, so this
    is a length class, not a Strahler order.
  * 84 river names printed on the map were transcribed; 217 reaches (9,703 km)
    carry a name in "river_name" (Niger, Benue, Kaduna, Gongola, Hadejia,
    Jama'are, Sokoto, Cross, Anambra, ...). nigeria_river_labels.shp holds
    the label positions for cartography.

--------------------------------------------------------------------------------
5. BOUNDARIES
--------------------------------------------------------------------------------
nigeria_boundary.shp (whole country, 1 polygon) and nigeria_states.shp
(36 states + FCT) are included so the dataset is complete on its own.
Areas were computed in an equal-area projection (EPSG:6933).

--------------------------------------------------------------------------------
ACCURACY STATEMENT
--------------------------------------------------------------------------------
Everything is tied to the two printed maps. Their scale limits absolute
accuracy to roughly 0.5-1 km; within that limit, mineral points sit at the
exact centres of the printed symbols, geology polygons form a watertight
national coverage, and rivers reproduce the map's own hydrography. Overlay
any layer on the two georeferenced TIFFs in this zip to verify.
================================================================================
