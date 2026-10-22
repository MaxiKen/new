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
  nigeria_mineral_occurrences.shp  Mineral occurrence points (1,090 points,
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
This layer was rebuilt from zero by the requested procedure: standard symbol
first, complete matches first, then partial matches, every point placed at
the calculated centre of its symbol.

Standard symbols: one template was built for each legend symbol from clear
instances on the map at the exact print scale. A point's position is the
centre computed from the standard symbol (its mask bounding-box centre),
never an eyeballed click.

COMPLETE matching (1,079 points, match_type = "complete"): the whole map
face was searched with the full templates (colour masked cross-correlation).
Acceptance is tiered by match strength: certain matches (score >= 0.95)
anywhere on the map; strong matches (>= 0.90) near a printed locality
number; context-confirmed matches (>= 0.82) at a number whose table row lists
that mineral. In addition, every table number received a windowed search
with full-template and ink-only masks, which recovers symbols printed over
different geology tints. The few tiny or generic symbols (Beryl diamond,
Glass-Sand pentagon, Gold square, Coal bar) were protected by blob-shape
checks against look-alike map detail, and doubtful centres were cross-checked
against all competing templates.

PARTIAL matching (11 points, match_type = "partial"): for table occurrences
still unmatched after the complete pass - typically symbols half-buried in
dense clusters - half-symbol templates (top / bottom / left / right halves)
were searched at the locality number. Only partial matches whose visible half
is strong and which survived full-template cross-checks plus a visual audit
of every candidate were kept; "vis_part" records which half is visible. The
point is still placed at the full symbol's computed centre.

Linkage: 758 points are attached to the exact table row of their printed
number (locality and commodity codes in the attributes); 320 further printed
symbols that are not itemised at a number carry their nearest number for
reference; 12 have no number within 48 map pixels. "id_score" is the match
confidence (1.00 = pixel-perfect) and "px_x / px_y" are the symbol-centre
positions on the map image, so any point can be cross-checked against the
georeferenced TIFF in this zip. One point per symbol is guaranteed: the
minimum separation between points is 5 map pixels (verified - no duplicates).

Result: 1,090 points covering 58 of the 67 legend categories.

Symbols the printed map does NOT actually show (verified visually at every
relevant table number; no points were fabricated for them):
  Asbestos (1) 0, Bismuth (7) 0, Bitumen (8) 0 - the Ondo belt occurrences are
  printed with the Tar-Sand symbol (59); Nickel (48) 0, Psammite (50) 0,
  Saltlake/Potash (53) 0, Sillimanite (55) 0, Trona (62) 0, Calcite (67) 0.
  Uranium (63): only 3 discs are printed on the whole map.
Further unavoidable cases:
  * Phosphate (32) and Gypsum (31) are printed with the SAME glyph on this
    map (white circle with horizontal bar; the legend's "+" never appears at
    print scale - confirmed at every phosphate locality). Attribution
    therefore follows the locality table at each number: 7 Phosphate points.
    Legend no. 49 (Phosphate Rock) shares code "P" and the same glyph.
  * Tin ("Sn") is drawn with the Columbite symbol; those points carry
    mineral = Columbite (14) with table_code preserving "Sn". At several
    north-western Sn/Nb localities only the white Tantalite (58) bowl is
    printed, so only that point exists; likewise some Fe-coded localities
    print no iron triangle. Of the 1,096 (number, mineral) occurrences
    implied by the tables, 758 are matched to a symbol at their number;
    the remainder are not printed as separate symbols.
  * A handful of coastal / border symbols fall a short distance outside the
    generalised boundary polygon; they are exactly where the map prints them.
An audit against the superseded extract agrees with 76% of its points to
within 8 map pixels; where they disagreed, the new point is the one at the
exact symbol centre (the old file had offset, doubled and mislabelled points).

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
