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
  nigeria_mineral_occurrences.shp  Mineral occurrence points (1,114 points,
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
This layer was rebuilt from scratch (second full rebuild, October 2026) by
the requested procedure: standard symbol first, complete matches first, then
partial matches in clusters, exactly one point per symbol at its calculated
centre - with every template and every centre re-verified after the previous
version was found to miss symbols and miss symbol centres.

Standard symbols and CENTRES: one template per legend symbol was built from
confirmed instances on the map at exact print scale, and the centre of each
symbol was MEASURED from the consensus ink outline of its confirmed instances
(not assumed from the template box). This removed systematic centre offsets
of up to ~2.5 map pixels (~1.7 km) that affected several symbols in earlier
extracts. Every template was also audited against its legend glyph; three
templates inherited from older work proved to be wrong symbols (Evaporite,
Fluorite, Mica) and were rebuilt from verified instances - the "E", "F" and
plain-disc glyphs now in the data were each confirmed letter-by-letter. All
points produced with the wrong templates were deleted, not patched.

COMPLETE matching (1,108 points, match_type = "complete"): the whole map
face was searched with the full templates (colour masked cross-correlation),
with acceptance thresholds calibrated per symbol from its own confirmed
instances: free-standing certain matches anywhere; strong matches near a
printed locality number; context-confirmed matches at a number whose table
row lists that mineral. Every table number then received a windowed search.
Look-alike symbols were arbitrated head-to-head at every candidate centre -
Brine "B" vs Evaporite "E" circles, Coal bar vs Kaolin box, Baryte / Gypsum /
Saltlake rings, Columbite vs Tantalite bowls, the clay / sand boxes - and
the tiny generic symbols (Beryl, Glass Sand, Gold, Coal) are protected by
blob-shape checks. Where a number's symbol was first claimed by the wrong
look-alike, arbitration relabelled it (e.g. 15 "Coal" points were really
Kaolin boxes).

PARTIAL matching (6 points, match_type = "partial"): for table occurrences
still unmatched after the complete pass, half-symbol templates (top / bottom
/ left / right) were searched at the locality number. A partial was accepted
only if the visible half beats every competing half-template at the same
centre; every accepted partial was visually audited (2 of 8 candidates were
rejected). "vis_part" records the visible fraction (0.5); the point is still
placed at the full symbol's calculated centre.

Coverage of the printed tables: the tables imply 1,096 (number, mineral)
occurrences. 747 are matched to a symbol at their own number (attributes
"locality" / "table_code" filled; link_type = "table row at its number");
for 52 more, the symbol is printed but shared with / attached to an adjacent
number, so the point exists but carries that neighbour's row. 351 further
printed symbols not itemised at a number carry their nearest number
(link_type = "nearest number (extra symbol)"), and 16 have no number within
48 map pixels. In total 1,114 points across 56 of the 67 legend categories.
One point per symbol is guaranteed: minimum separation between points is 5
map pixels (verified - no duplicates). "id_score" is the match confidence
(median 1.00; 5th percentile 0.79); "px_x / px_y" are symbol-centre
positions on the map image so any point can be checked against the
georeferenced TIFF in this zip.

Categories with NO points - verified at every relevant table number that the
printed map shows no distinct, usable symbol (no points were fabricated):
  Asbestos (1), Bismuth (7), Bitumen (8) - the Ondo belt occurrences are
  printed with the Tar-Sand symbol (59); Nickel (48), Phosphate Rock (49,
  shares code "P" and the Phosphate glyph), Psammite (50), Sillimanite (55),
  Trona (62), Calcite (67). Granite (30) and Rose Quartz (52): their legend
  marks are a tiny speckle / oval below reliable print resolution - searches
  at all their table numbers found no verifiable instance (earlier points
  for these two were false matches on map linework and were removed).
  Uranium (63): only 3 discs are printed on the whole map. Fluorite (22):
  only 3 orange "F" discs are printed (all captured). Mica (44): only 9
  pale-blue discs are printed (all captured); at the other mica numbers the
  map prints another commodity's symbol. Saltlake (53): 2 points where the
  distinct larger ring glyph could be confirmed against Gypsum.
Further unavoidable cases:
  * Phosphate (32) and Gypsum (31) are printed with the SAME glyph on this
    map (white circle with horizontal bar; the legend's "+" never appears at
    print scale - confirmed at every phosphate locality). Attribution
    therefore follows the locality table at each number: 7 Phosphate points.
  * Tin ("Sn") is drawn with the Columbite symbol; those points carry
    mineral = Columbite (14) with table_code preserving "Sn". At several
    north-western Sn/Nb localities only the white Tantalite (58) bowl is
    printed, so only that point exists; likewise some Fe-coded localities
    print no iron triangle. The (number, mineral) slots not matched above
    are cases where the map simply prints no separate symbol for that
    commodity at that number (checked window by window).
  * A handful of coastal / border symbols fall a short distance outside the
    generalised boundary polygon; they are exactly where the map prints them.
An audit against the superseded extract agrees with 72% of its points to
within 4 map pixels (80% within 8); where they disagree, the new point is
the one at the exact symbol centre - the old file had offset centres,
duplicated symbols, and points on the wrong glyphs (including points on
Kaolin boxes labelled as other minerals).

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
