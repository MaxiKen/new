# Nigeria: geology and mineral resources atlas

One GeoPackage — `Nigeria_Geology_Minerals_4326.gpkg` (16.6 MB) — everything in **EPSG:4326**,
built by `Build_GeoPackage.py` and checked by `Validate_GeoPackage.py`
(**27 of 27 checks pass**, results in `GeoPackage_Validation.json`).

Open it in QGIS: drag the file in and tick layers. Rasters appear under "Add raster layer" →
the file → the named raster. Every raster carries tags recording how it was registered and
what it must not be used for.

The four map plates beside it are drawn **from this same file**, so a picture cannot disagree
with the data:

| plate | what it shows |
|---|---|
| `Map_1_Geology.png` | map units, faults, roads, drainage, state boundaries — with the full 45-code unit legend |
| `Map_2_Minerals.png` | the 2023 sheet with all 1,323 symbols re-plotted and classified |
| `Map_3_Combined.png` | muted geology + interpolated symbol density + every symbol + faults |
| `Map_4_Symbol_Centring.png` | six measured close-ups proving where each coordinate sits |

## Layers (13)

| layer | type | what it is |
|---|---|---|
| `minerals_symbols` | 1,323 points | every printed mineral symbol, at the **centre of its printed glyph**, with commodity name, class, confidence tier and value |
| `geology_units` | 1,142 polygons | the sheet's coloured map units, each with `unit_code`, `unit_name`, `period`, `sheet_colour`, `area_km2`, `in_nigeria` |
| `faults` | 13 traces | the sheet's "Major Fractures / Faults" symbol (246 km of trace) |
| `roads` | 954 strokes | the sheet's "Roads" symbol — the national road network |
| `rivers` | 1,055 lines | the sheet's blue drainage |
| `state_boundaries` | 83 lines | the sheet's internal administrative lines |
| `nigeria_boundary` | 1 polygon | Natural Earth 1:10m outline, for reference and clipping |
| `ref_geology_2011` | raster, 3-band uint8 | the 2011 sheet as drawn, registered on its printed graticule |
| `ref_minerals_2023` | raster, 3-band uint8 | the 2023 sheet as drawn, registered on its embedded frame |
| `combined_map` | raster, 3-band uint8 | the two sheets overlaid |
| `mineral_density_all` | raster, float32 | interpolated density of all printed symbols, σ = 0.15° |
| `mineral_density_metallic` | raster, float32 | same, metallic only (338 symbols) |
| `mineral_density_nonmetallic` | raster, float32 | same, industrial + gemstone + energy (967 symbols) |
| `dataset_notes` | table | 15 plain-language notes, including what the file must not be used for |

Reference rasters are 2,480 × 2,040 at 0.005° over 2.6–15.0°E, 3.9–14.1°N (0.005° ≈ 550 m).
Density rasters are 1,240 × 1,020 at 0.01°, in **symbols per 1000 km²**, −9999 outside Nigeria.

## Other features: what could and could not be extracted

The 2011 sheet is fully vector (45,435 paths, no images), and its legend gives the pen
meanings. That allowed every layer of information to be recovered — and one honest gap.

| feature | status |
|---|---|
| map units, with names and periods | **extracted** — 1,142 polygons, 45 named codes, 23 polygons that carry no printed label (kept, marked `unlabelled`, not guessed) |
| faults (major fractures) | **extracted** — the sheet's hachured symbol, 13 traces, 246 km |
| roads | **extracted** — thick black "Roads" symbol, 954 strokes |
| rivers | **extracted** — 1,055 blue lines |
| state boundaries | **extracted** — 83 grey banded lines |
| **folds** | **not present on this sheet.** Its structural symbols are *Geological Boundary (exact / approximate / inferred / transitional)*, *Major Fractures / Faults* and *Fractures / Fault (inferred)*. There is no fold symbol, no dip-and-strike symbol and no separate lineament group in the file, so no fold layer was invented. |
| graticule as a layer | not needed; the sheet's grid is a 10-minute subdivision drawn as thousands of short segments, and the coordinate transform is supplied instead |

**How faults were separated from roads.** Both are drawn with the same thick black pen — this
was the trap. They are separated by connectivity, not by guessing: the road network is one
continuous connected network (954 mutually touching strokes), while fault dashes stand alone
(65 isolated strokes, which chain into 13 traces, all in the Chad Basin margin of the
north-east). That is what the sheet actually shows; the rest of Nigeria carries no fault symbol
on this edition.

## The mineral points are as accurate as this sheet allows

Three separate errors were found and fixed, and every fix is independently verified:

1. **The art strips are stored vertically flipped.** The seven 75 dpi strips holding the symbol
   artwork are drawn flipped on the page; reading them naively mirrored every latitude about
   its strip axis. Fix verified: symbols detected on the page land on the same symbols in the
   artwork **100%** of the time, against **1%** for random positions.
2. **The printed graticule is 19 km west of the frame the artwork uses.** Proven by the sheet's
   own vector border: it matches modern boundary data to **0.5–1.1 km** on the embedded GeoPDF
   measure, but is **12.9 km** out on the printed grid.
3. **Points sat inside glyphs but not at their centres.** There was no global bias — 748 of
   1,323 points had a matching glyph at exactly (0.0, 0.0) px offset — so the residual was
   pure source resolution. Each point was then re-measured to the centre of its own glyph.

**Independent verification** (`Verify_Centres.py`, which re-renders the page at 4 px/pt and
re-detects the glyphs without reusing any build coordinate):

| check | result |
|---|---|
| points landing on a detected glyph | **97.8%** |
| median distance from point to glyph centre | **0.35 km** (0.50 pt) |
| within 1 pt (0.71 km) | 75.0% |
| within 2 pt (1.41 km) | **95.4%** |

One artwork pixel is **0.68 km**, so a 0.35 km median is finer than the drawing itself. That is
the floor: claiming better would be false. `Map_4_Symbol_Centring.png` shows six points at 14×,
each labelled with its own measured offset.

## Reading the geology layer

Colours are the sheet's own; nothing was reinterpreted. A unit's name comes from the unit label
printed *inside* its polygons, voted across all polygons of that colour (92 of 105 colours
resolved). Where that failed the polygon is marked `unit_code = 'unlabelled'`. Periods follow
the sheet's legend, which mixes era names and system names (e.g. "Pan-African" alongside
"Jurassic"); the file keeps the sheet's wording.

## The density surface

Gaussian kernel, σ = 0.15° (≈17 km), one unit per symbol, converted to symbols per 1000 km²,
masked to Nigeria. It integrates to about 1,087 symbols against 1,179 inside the border — the
shortfall is coastline clipping, asserted as a test rather than assumed.

**Read it as**: how densely the *printed symbols* cluster. Not reserves, not grade, not
production, not economic viability. Clustering partly reflects real geology and partly
reflects where the survey looked. Commodity names are ~81% correct per point, so the class
split is indicative only.

## Limits, stated once

* **Datum not established** for either sheet. EPSG:4326 is the display frame. Minna → WGS 84
  moves Nigeria about 0.09 km, below what these sheets can resolve.
* **Geology needs no correction**: state boundaries, rivers and coastline all sit within 1–3 km
  of independent reference data; the best-fit shift (0.9 km) is below one and a half map pixels.
* **Commodity names** are 80.8% correct overall (leave-one-out). Use the `tier` and
  `confidence` columns per point; per-mineral totals are unreliable.
* **Faults** are the sheet's printed symbol, generalised at 1:2,000,000; the hachures show the
  downthrown side but the sheet does not label certainty.
* **Not for** surveying, licensing, legal boundaries, navigation, or site-scale decisions.

## Reproducing it

```
Extract_Geology_Layers.py   # pulls units, faults, roads, rivers, state lines from the vector sheet
Rebuild_Symbol_Centres.py   # re-measures symbol centres from the native artwork
Snap_To_Symbols.py          # snaps each point to its own glyph centre
Verify_Centres.py           # independent page-render check
Build_GeoPackage.py         # builds the .gpkg (13 layers)
Validate_GeoPackage.py      # 27 assertions on the finished file
Render_Maps.py              # draws the four plates from the .gpkg itself
```
