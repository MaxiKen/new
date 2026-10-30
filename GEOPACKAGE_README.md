# Nigeria: geology and mineral resources atlas

Two GeoPackages, both built by script and both checked by script:

| file | what it is |
|---|---|
| `Nigeria_Geology_Minerals_4326.gpkg` | **the reference frame.** 13 layers, EPSG:4326, 16.8 MB |
| `Nigeria_Geology_Minerals_projected.gpkg` | **the working frame.** The same layers with geometry genuinely reprojected to metres — Albers equal-area for areas, UTM 32N for positions and distances |

`Validate_GeoPackage.py` runs **30 checks on the 4326 package; all 30 pass**
(`GeoPackage_Validation.json`). `Projection_Report.json` proves the projected package's
coordinates really are metres by reporting their ranges and the measured scale error.

The four plates are drawn from the 4326 package, so a picture cannot disagree with the data:

| plate | what it shows |
|---|---|
| `Map_1_Geology.png` | map units, faults, roads, drainage, state boundaries, full 45-code legend |
| `Map_2_Minerals.png` | the 2023 sheet with every occurrence re-plotted once and classified |
| `Map_3_Combined.png` | muted geology + interpolated symbol density + every occurrence + faults |
| `Map_4_Symbol_Centring.png` | six measured close-ups proving where each coordinate sits |

## The unit layer is a partition of the country

It took three attempts. The first read the PDF's loose filled paths and included one page-sized
rectangle carrying the code `Qs`, the legend swatches and a neat-line strip: 1,142 polygons, 40.7% of
the country covered, 428,619 km² of overlap. The second read the printed colours pixel by pixel and
fixed the coverage, but fragmented every unit along the labels and lines printed over it (see
below). **This version ships the geology body set that already existed in this repository, taken
from branches `7am` / `edit-mode` / `side`, re-referenced against the sheet and repaired.**

| | value |
|---|---|
| bodies | **1,552** (78 unit codes) |
| Nigeria covered | **100.00%** |
| overlap | **0.000%** (0.00 km²) |
| unassigned holes | **1.1 km²** in total |
| bodies under 0.5 km² | **0** (41 merged into a neighbour) |
| largest body | 62,956 km² — the Chad basin sands |
| median body | 66 km² |
| carrying a full legend name | 1,402 of 1,552 |

### Where these polygons come from, and the reference check

The source, `data/ngsa/ngsa_geology_v6.gpkg`, is revision 6 of an interpretation made from a
6,600 × 3,675 photograph of the NGSA sheet: 1,588 singlepart polygons following the printed
contacts, one shared contact network, with a lithology per body. Its header said **“EPSG:4326 —
assumed datum”** — nobody had checked where it sat. That is the part that is now fixed, and the
check is measured, not asserted.

The photograph carries the sheet's own graticule. Every meridians and parallel was measured to the
pixel centre — 5 meridians (3°E to 14°E) and 9 parallels (5°N to 13°N, `data/ngsa/graticule_control
_points.json`):

| | measured |
|---|---|
| grid spacing | 328.5 px per degree east–west, 328.4 px north–south |
| straightness of the grid | 0.16 px across a meridian, 0.19 px across a parallel |
| shipped linear transform vs that grid | **mean 0.23 km, worst 0.27 km** |
| what was done | the polygons were re-tied to the measured graticule |

So the coordinates were already nearly right — but they were right by luck, and now they are right
by measurement. `Geology_Referencing.png` shows the graticule as measured, and the bodies drawn over
the printed sheet.

The geometry was then made fit to ship:

* **cut to the border** — 4,242 km² of the source lay outside Nigeria, mostly coast and border fringe;
* **bare ground closed** — 12,554 km² inside the border carried no body: 7 pieces were water on the
  printed sheet (Lake Chad and reservoirs) and became the class `WATER`; the rest, 8,575 km² of thin
  coastal and border strips, went to the neighbour sharing the longest edge with them;
* **tiny bodies merged** — 41 bodies under 0.5 km² and thinner than 0.4 km were absorbed, so there is
  not one speck left;
* **names and periods** from the sheet's legend, so the codes mean here what they mean on the sheet.

Two codes the sheet prints but its own legend omits stay unresolved on purpose: `OGp` (149 bodies,
79,251 km², the salmon Older Granite field) and `S` (1 body, 928 km²). They are named to series level,
given `name_confidence = low`, and counted out loud in the map legend rather than guessed.

### Why the pixel-by-pixel reading was retired

The second attempt read every flat colour on the sheet and rebuilt each region from it. It reached
100% coverage, but it split units in two in exactly the places the question was about, and its edges
were pixel staircases. Measured on that layer: **2,362 pairs of polygons sharing a unit code sat
within 2.5 km of each other, 462 within 1 km, 159 within 500 m.** Two causes, both found and both
worth recording because the body set does not have them:

* **Line work taken for rock.** Roads, rivers, shear zones and dashes are printed in flat colours
  like units; the reader carved them out of the unit they crossed. Their thickness gives them away:
  measured as twice the largest inscribed radius, line work is 2–6 px and fills are 11 px or more.
* **A name cut into the unit under it.** Every letter was a hole, and the filler gave each letter
  pixel to its nearest neighbour, so a name straddling a contact took half its letters from each
  side and dismembered the unit it was printed on.

Repairing those two rules took the fragmentation from 2,362 pairs to 1,151, and it is documented in
`Geology_Partition_Before_After.png` — but the result still had staircase edges and still cut units
where a line was thinner than the cut-off. It is kept on disk (`Geology_Units_Repaired.geojson`) for
comparison and is **not** what ships.

## The life saver

`Geology_LifeSaver.py` is the safety net around the unit layer. Run it after any change:

```
python3 Geology_LifeSaver.py            # audit, repair, write Geology_Units_Repaired.geojson
python3 Geology_LifeSaver.py --check    # audit only, exit code 1 if anything is wrong
```

It measures the layer, fixes what it finds, and writes both `LifeSaver_Report.json` and the repaired
layer back into `Geology_Layers_Extracted.gpkg` as `geology_units`, which is what every downstream
build reads.

| step | what it does | result on the current build |
|---|---|---|
| overlaps | trims the smaller polygon where two claim the same ground | nothing to do on the shipped layer |
| cuts | bridges two parts of one unit when only empty ground lies between them, never across another unit | 6 pairs found, none narrow enough to be a cut |
| slivers | merges strands thinner than 0.45 km into their neighbour; leaves small chunky outcrops alone | 0 |
| holes | gives unassigned ground to the neighbour sharing the longest edge with it | 1.1 km² left, below its threshold |
| fragments | counts the pieces each unit comes in, so the real structure is visible | reported, not forced together |
| read-back | reads the written file again and checks the sum of areas against the union | 909,249.3 = 909,249.3 km², nothing double-counted |

Two rules keep it honest. It never invents a unit — a bridge joins only two polygons that already
carry the same code — and it checks every geometry it writes: a repair that changes a polygon's area
by more than 1% is rejected, because an over-helpful `make_valid` once turned one weak ring into a
36,000 km² polygon spanning half the country. That failure is why the read-back step exists.

## Live comparison viewer

`serve_atlas.py` runs a small web app for checking the result against the pictures it came from:

```
python3 serve_atlas.py            # then open http://localhost:8080
```

It needs only `pymupdf` and `pillow` beyond the pipeline's own environment. No CDN, no build step,
no external tiles. `web/data/` is generated by `Build_Web_Data.py`, so the viewer cannot show
anything the package does not contain.

| part | what it does |
|---|---|
| **Explore** | either sheet as a base picture with every re-plotted occurrence, fault, river, road, state line and boundary on top |
| **Compare** | a draggable divider: the **printed geology sheet on the left, the unit polygons on the right**, locked to one shared view — drag it either way and the side you widen takes over the screen |
| **Verify** | a live crop rendered straight from the PDF at the cursor, with a crosshair on the digitised coordinate |
| Inspector | the printed symbol at 9×, its name, the other reading, confidence, class, name source, matcher margin |
| Filters | name confidence, commodity class, six vector layers, picks outside Nigeria, and a searchable list of all 1,091 records |

**Mobile.** Below 900 px the layout becomes a single full-screen map: the layer panel is a drawer
behind the hamburger, the inspector slides up from the bottom when a point is tapped, the toolbar
becomes one row with a zoom slider, and one finger pans while two fingers pinch.

**Deep zoom.** The zoom slider runs from level 100 (the whole country) to **1500**, which is about
25 km across a phone screen — far past the resolution of the exported sheet. Two things make that
usable rather than merely pixelated:

* above level 320 the server renders the visible window **from the PDF on demand** (`/api/view`),
  so the picture stays sharp instead of showing the scan's pixels;
* the unit polygons are drawn as **vectors** above level 200, with fills laid down big-to-small and
  each boundary stroked in its own colour, so no white seams appear between neighbours.

## What changed in this revision

### 1. One point per printed symbol — duplicates removed

The sheet draws a cluster of occurrences as several distinct symbols side by side. The previous
file placed **1,323** points; measuring them showed that **232 of those points sat on a symbol
that already had a point** — the same printed symbol had been recorded twice.

Consolidation is geometric, not a choice: a symbol is a connected patch of the sheet's symbol
palette, so two points that land on the same patch are the same symbol and become one point,
placed at that patch's centre. Two points on *different* patches stay separate however close —
a cluster of adjacent symbols is a real cluster.

| | before | now |
|---|---|---|
| points | 1,323 | **1,091** |
| points sharing a symbol with another point | 232 | **0** |
| merged points kept as an attribute | — | 141 rows carry `n_source_points > 1` |
| median distance to the symbol's printed centre | 0.35 km | **0.09 km** |
| within 1 pt (0.71 km) | 74% | **96%** |

Fitting each point to the centre of its glyph then moved 836 of them a median of 0.8 pt. No
point was moved onto a neighbouring symbol: 54 points had no glyph within reach and were left
where the consolidation put them.

`Map_4_Symbol_Centring.png` shows six occurrences at 14×, each labelled with its own measured
offset — four of the six are exactly 0.00.

### 2. More minerals, and names clearly marked as readings

The sheet's legend carries **67 mineral symbols**, and its gazetteer lists some localities with
three or four minerals each (`87 Rjishi Hills Sn. W. Nb. Ta`, `11 MARNONA Gy`). Reading it took
three passes:

1. **The gazetteer** (`Parse_Gazetteer.py` → `Gazetteer_Localities.json`) parses the occurrence
   table at character level and recovers the locality and the mineral codes for each numbered
   entry, with the code → mineral expansions. It is the survey's own statement of what is where.
2. **The legend symbols** (`Detect_Symbols.py`) are extracted as 67 templates and matched
   against each occurring symbol on the sheet, giving a second, independent name and a score.
3. **The commodity code printed inside each symbol** — the original reading, 81% correct per
   point in leave-one-out testing.

Where those two readings agree, the name is safe. Where they only agree on a family
(Clay vs Brick Clay; Beryl vs Emerald) the name is published with `confidence = medium`. Where
they conflict the row keeps **both names** — `mineral` and `alternative_name` — and is marked
`low`. That is deliberate: I will not overwrite a good reading with a guess, and I will not hide
a conflict behind a single confident-looking column.

| | count |
|---|---|
| occurrences | **1,091** |
| distinct commodity names | **47** (spellings merged from the sheet's split kerning) |
| both readings identical | 194 |
| readings agree on a commodity family | 199 |
| readings conflict (`confidence = low`) | 892 |
| `confidence` high / medium / low | 86 / 113 / 892 |

The columns to sort by when you check: `confidence`, then `family_agreement`, then `margin`
(how far the winning legend symbol beat the runner-up). `legend_symbol`, `second_symbol` and
`legend_score` let you see exactly what the matcher saw.

`Parse_Gazetteer.py` is honest about its own limit: the panel's index numbers **restart in each
gridded zone**, so a number alone is ambiguous. The local names are not, which is why the table
is keyed by locality and matched to the map by name.

### 3. Layers that are actually projected

EPSG:4326 is a frame of degrees. Distances and areas measured in it are wrong by up to 1% in
latitude scaling — the very error that made a length look 1% short. So a second package now
carries real projected geometry:

| layer | CRS | coordinates | why |
|---|---|---|---|
| `geology_units`, `nigeria_boundary` | ESRI:102022 Africa Albers Equal Area Conic | −2,386,313 to −395,217 m E | areas are comparable everywhere |
| `minerals_occurrences`, `faults`, `roads`, `rivers`, `state_boundaries` | EPSG:32632 WGS 84 / UTM 32N | −196,828 to 1,103,938 m E | positions and distances are metric |

Measured, not asserted: the UTM 32N distance scale error over short baselines is
**0.035% median** (−0.02% to 0.45%) — worst case about 1 m in 220 m. Nigeria's area in the
equal-area frame is **907,498 km²**.

The 4326 package remains the authoritative reference frame; the projected one is for measuring.

## Layers (13, in the 4326 package)

| layer | type | what it is |
|---|---|---|
| `minerals_occurrences` | 1,091 points | one row per printed symbol, at its centre, with name, alternative name, confidence, source and classifier evidence |
| `geology_units` | 1,552 bodies | the sheet's map units as a complete partition of the country, with `unit_code`, `unit_name`, `period`, `sheet_colour`, `area_km2`, `name_confidence`, `how_named` |
| `faults` | 13 traces | the sheet's "Major Fractures / Faults" symbol (246 km) |
| `roads` | 954 strokes | the sheet's "Roads" symbol — the national road network |
| `rivers` | 1,055 lines | the sheet's blue drainage |
| `state_boundaries` | 83 lines | the sheet's internal administrative lines |
| `nigeria_boundary` | 1 polygon | Natural Earth 1:10m outline |
| `ref_geology_2011` | 3-band uint8 | the 2011 sheet as drawn, on its printed graticule |
| `ref_minerals_2023` | 3-band uint8 | the 2023 sheet as drawn, on its embedded frame |
| `combined_map` | 3-band uint8 | the two sheets overlaid |
| `mineral_density_all` | float32 | interpolated symbol density, σ = 0.15° |
| `mineral_density_metallic` | float32 | same, metallic only |
| `mineral_density_nonmetallic` | float32 | same, industrial + gemstone + energy |
| `dataset_notes` | table | 15 plain-language notes, including what the file must not be used for |

Reference rasters: 2,480 × 2,040 at 0.005° over 2.6–15.0°E, 3.9–14.1°N. Density rasters:
1,240 × 1,020 at 0.01°, in symbols per 1000 km², −9999 outside Nigeria.

## Other features: what could and could not be extracted

| feature | status |
|---|---|
| map units with names and periods | **extracted** — 1,552 bodies, one unit at every point of the country, 1,402 with a legend name and 150 flagged low |
| faults (major fractures) | **extracted** — 13 traces, 246 km |
| roads | **extracted** — 954 strokes |
| rivers | **extracted** — 1,055 lines |
| state boundaries | **extracted** — 83 lines |
| **folds** | **not present on this sheet.** Its structural key has *Geological Boundary* (exact/approximate/inferred/transitional), *Major Fractures / Faults* and *Fractures / Fault (inferred)* only. No fold symbol, no dip-and-strike symbol, no separate structural group. None was invented. |

**Faults vs roads.** Both use the same thick black pen. They are separated by connectivity: the
road network is one continuous connected network (954 touching strokes); fault dashes stand
alone (65 isolated strokes chaining into 13 traces, all on the Chad Basin margin). That is what
this edition actually shows.

## Method and provenance

```
Extract_Geology_Layers.py     units, faults, roads, rivers, state lines from the vector geology sheet
Parse_Gazetteer.py            the 2023 sheet's own occurrence table: locality -> mineral codes
Rebuild_Symbol_Centres.py     per-symbol art-strip reconstruction (fixes the flipped strips)
Consolidate_Symbols.py        one point per printed symbol; merges duplicates by symbol patch
Classify_Symbols.py           matches each symbol against the 67 legend symbols
Finalise_Occurrences.py       publishes a name, an alternative, a source and a confidence
Normalise_Names.py            one canonical spelling and commodity class per mineral
Snap_Final.py                 moves each point onto its glyph centre
Verify_Centres.py             independent page-render check (does not reuse build coordinates)
Build_GeoPackage.py           the 4326 package
Build_Projected_Layers.py     the projected package, with measured scale error
Validate_GeoPackage.py        30 assertions on the finished file
Render_Maps.py                the four plates, drawn from the package itself
```

Three source errors are fixed in this lineage and are worth knowing about, because they are
invisible in the output:

1. **The seven 75 dpi art strips are stored vertically flipped.** Reading them naively mirrored
   every latitude about its strip axis. Fix verified: symbols land on the same symbol in the
   artwork 100% of the time, against 1% for random positions.
2. **The printed graticule is 19 km west of the frame the artwork uses.** Proven by the sheet's
   own vector border: 0.5–1.1 km error on the embedded measure, 12.9 km on the printed grid.
3. **Points sat inside glyphs but not at their centres.** No global bias existed (748 points
   matched at exactly (0.0, 0.0) px offset), so the residual was pure source resolution; each
   point is now fitted to its own glyph.

## Limits, stated once

* **Datum not established** for either sheet. EPSG:4326 is the display frame. Minna → WGS 84
  moves Nigeria about 0.09 km, below what these sheets resolve.
* **Geology needs no correction**: state boundaries, rivers and coastline all sit within 1–3 km
  of independent reference data; the best-fit shift (0.9 km) is under one and a half map pixels.
* **Symbol centres**: an independent audit (`Measure_Centres.py`, `Centre_Audit.json`) renders a
  30 pt window around each of the 1,091 points and measures the distance to the centre of the
  printed mark it sits on: **median 0.49 pt ≈ 0.33 km**, 70% within 2 pt, and only 3.3% of windows
  match a mark too small to be a symbol. The tail is where a symbol touches its index number, a
  road or a leader line — one ink blob, so the *measurement* drifts, not the point. One artwork
  pixel is 0.68 km, so the drawing, not the method, is the floor.
* **Commodity names**: 18% of rows are carried by both independent readings, 27% more agree on a
  family, and 82% are marked `low`. Use `confidence`; do not quote per-mineral totals as fact.
  The columns `mineral` (published), `alternative_name` (the other reading), `legend_symbol`,
  `second_symbol` and `margin` show exactly what each reading was and how close the call was.
* **Faults** are the sheet's printed symbol at 1:2,000,000; the hachures show the downthrown side,
  but the sheet does not label certainty.
* **Not for** surveying, licensing, legal boundaries, navigation, or site-scale decisions.
