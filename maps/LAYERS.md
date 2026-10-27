# Layer catalogue — `Nigeria_Geology_Minerals_4326.gpkg`

**26 vector layers, 57,364 features — every one in EPSG:4326** — plus **ten tiled raster
layers** (the nine georeferenced sheets and the DEM class map; also EPSG:4326, the only CRS a
degree-tiled raster can carry), documented separately in
[`RASTER_LAYERS.md`](RASTER_LAYERS.md), **one numeric raster** — the DEM built from the DEM
sheet, `dem_from_sheet` — and **one** added gazetteer layer,
[`towns_geonames`](towns_geonames.md) (45,415 points), documented in
[`towns_geonames.md`](towns_geonames.md).

**One CRS, on purpose.** All 26 vector layers, the ten tiled rasters and the DEM are EPSG:4326, so they can be
laid on each other, joined and drawn without a reprojection. The five reprojections that used to
sit in this file — three in EPSG:32632, two in EPSG:6933 — exist only so that area and length can
be *measured* in metres, and each had a 4326 twin here; they now live, unchanged, in
**`Nigeria_Geology_Minerals_projected_copies.gpkg`** (see
[The five reprojections](#the-five-reprojections)). Nothing was deleted: the geometry and every
attribute of each copy are the same, and `audit_layers.py` proves the copy is its parent
reprojected on every run. Layer numbers 5, 6, 23, 24 and 25 are therefore absent from the summary
table below — the numbering is deliberately left alone so every cross-reference in these files
still resolves.

Every layer has a CRS, 0 invalid / empty / null geometries, and is verified by `audit_layers.py`
(result: `layer_audit.json`, 0 problems).

The file also carries its own provenance: `gpkg_metadata` holds five ISO 19139 records — the
whole file (title, lineage, bounding box, the licence of every source), the GeoNames CC BY 4.0
attribution for `towns_geonames`, the Natural Earth terms for the outline, the notice attached to
its four mineral layers whose positions are withdrawn, and the statement of what the DEM is and
is not — with
`gpkg_metadata_reference` saying which part of the file each one is about. `add_gpkg_metadata.py`
writes them and `audit_layers.py` checks that they are well-formed and still complete, so the
attribution survives the file being copied on its own.

### The DEM built from the sheet

`raster_dem` is a scan; `dem_from_sheet` is the elevation those pixels state. Every pixel
carries the **midpoint of the printed legend class** it falls in, as float32 metres, in an OGC
**2D gridded coverage** — the GeoPackage container for a numeric raster, unlike the image tiles
of the nine scans. `dem_from_sheet_class` is the same map as an integer 1–7 in legend order, as
one band of image tiles.

| class | printed range (m) | value (m) | share | area (km²) |
|---|---|---|---|---|
| 1 | -25 – 130 | 52.5 | 14.5 % | 130,735 |
| 2 | 140 – 260 | 200.0 | 22.2 % | 200,395 |
| 3 | 270 – 380 | 325.0 | 31.3 % | 283,099 |
| 4 | 390 – 530 | 460.0 | 17.2 % | 155,127 |
| 5 | 540 – 720 | 630.0 | 11.3 % | 101,986 |
| 6 | 730 – 1,100 | 915.0 | 2.6 % | 23,206 |
| 7 | 1200 – 2,100 | 1650.0 | 1.0 % | 8,599 |

Each class's prototype colour was calibrated on the sheet itself — the legend swatch is not the
colour the map is painted in, and hillshading changes every slope's colour — and checked against
SRTM heights at towns the calibration never saw: **68.4 % exact class,
96.1 % within one class, MAE 73 m** on
22,379 towns. No metre comes from SRTM; every value is a printed legend value.
With seven classes the vertical resolution is about 158 m, so this
says what the sheet states and cannot resolve a hill — for real heights use a real DEM. Full
account in [`RASTER_LAYERS.md`](RASTER_LAYERS.md); the GeoTIFFs are
`Nigeria_DEM_from_sheet.tif` and `_smoothed.tif`.

Two sheets feed it, and it matters which one for what:

* **2011 Geological Map** → all base geography, geology, faults, folds, water, settlements, transport.
* **2023 Mineral Resources Map** → the mineral symbols, the 999 numbered localities, the
  international boundary.

Navigation: [Boundary & water](#1-boundary-and-water) · [Geology](#2-geology) ·
[Base geography](#3-base-geography) · [Minerals](#4-minerals) ·
[The gazetteer](#6-the-gazetteer) · [QA](#5-qa-layers) ·
[Class polygons](#7-the-class-polygons-2931) ·
[How to choose](#8-which-layer-do-i-want) · [Read this before you compute](#9-read-this-before-you-compute) ·
[The five reprojections](#the-five-reprojections)

---

## Summary table

| # | layer | n | CRS | geometry | in Nigeria | one-line purpose |
|---|---|---|---|---|---|---|
| 1 | `national_territory` | 1 | 4326 | Polygon | 100 % | the country polygon everything is clipped to |
| 2 | `international_boundary` | 1 | 4326 | LineString | 100 % | the 2023 land border as printed |
| 3 | `water_bodies` | 4 | 4326 | MultiPolygon | 9.2 %* | sea, Lake Chad, the Niger–Benue corridor |
| 4 | `geology_units` | 97 | 4326 | MultiPolygon | 100 % | **the geology**: 96 rock units + water |
| 7 | `geology_boundaries` | 2,819 | 4326 | LineString | 99.9 % of 84,001 km | contacts, by confidence |
| 8 | `faults` | 648 | 4326 | LineString | 99.8 % of 18,669 km | major and inferred faults |
| 9 | `fold_axes` | 90 | 4326 | LineString | 94.6 % | anticlines and synclines |
| 10 | `younger_granite_outlines` | 59 | 4326 | LineString | 100 % | Jos Plateau ring complexes, as outlines |
| 11 | `rivers` | 1,054 | 4326 | LineString | 83.1 % of 41,194 km | drainage centrelines |
| 12 | `roads` | 122 | 4326 | LineString | 92.6 % of 19,842 km | trunk roads |
| 13 | `railway` | 6 | 4326 | LineString | 100 % of 3,131 km | rail lines |
| 14 | `state_boundaries` | 83 | 4326 | LineString | 92.3 % of 36,044 km | 36 states + FCT |
| 15 | `towns` | 486 | 4326 | Point | 463/486 | settlements **as printed on the 2011 sheet**, with host unit. For coverage use `towns_geonames` (28) |
| 16 | `state_capitals` | 32 | 4326 | Point | 32/32 | capitals, label centres ±15 km |
| 17 | `volcanic_plugs` | 68 | 4326 | Point | 68/68 | plugs and necks |
| 18 | `mineral_symbols` | 1,609 | 4326 | Point | 1,603/1,609 | **positions withdrawn**; attributes usable |
| 19 | `minerals_named` | 1,323 | 4326 | Point | 1,179/1,323 | **the valid printed symbols** (±0.35 km) |
| 20 | `mineral_localities` | 999 | 4326 | Point | 991/999 | **positions withdrawn**; raw extraction |
| 21 | `mineral_localities_refined` | 999 | 4326 | Point | 992/999 | **positions withdrawn**; older policy |
| 22 | `mineral_localities_icons` | 999 | 4326 | Point | 995/999 | **positions withdrawn**; icon-anchored |
| 26 | `graticule_geology` | 22 | 4326 | LineString | 66.5 %* | QA: the 2011 graticule fit |
| 27 | `graticule_minerals` | 11 | 4326 | LineString | 63.8 %* | QA: the 2023 graticule fit |
| 28 | `towns_geonames` | 45,415 | 4326 | Point | 98.9 % | **the gazetteer** — every populated place GeoNames records for Nigeria; state, population where known. See [`towns_geonames.md`](towns_geonames.md) |
| 29 | `poly_soil_ph` | 111 | 4326 | MultiPolygon | 100 % | **the soil-pH sheet as polygons**: 5 pH classes, palette measured from the printed swatches, clipped to the border; covers 99.94 % of the territory |
| 30 | `poly_population` | 299 | 4326 | MultiPolygon | 100 % | **the population sheet as polygons**: 5 absolute-count classes by unnamed district; covers 92.51 % of the territory, the rest is blank on the sheet |
| 31 | `geology_era` | 7 | 4326 | MultiPolygon | 100 % | 7 era classes dissolved from the attributed `geology_units` (era only, no lithology), keyed by `class_id` — the vector answer to the general-geology sheet |

\* low "in Nigeria" share is by design for these three — they are sea, cross-border water and
graticule lines that run past the map frame. Do not clip them, do not add them to an area total.

---

*Not in this file:* 5, 6, 23, 24, 25 — the five reprojections, now in
`Nigeria_Geology_Minerals_projected_copies.gpkg`. See [The five reprojections](#the-five-reprojections).

## 1. Boundary and water

### 1. `national_territory` — 1 polygon, 907,157 km²

The country polygon. Every other layer is either clipped to it or measured against it, and
`geology_units` is cut on it, so the geology's outer edge **is** this line.

It is not a supplied boundary: it is a **splice**. The 2023 sheet's border is a land border
only — an open line from (2.70°E, 6.37°N) to (8.52°E, 4.74°N) that cannot close into a
polygon. So 3,906 km of the Natural Earth 10m Nigeria outline's land edge was replaced,
vertex for vertex, by the 2023 line; the 2,056 km of coastline was kept; the two junctions
were snapped by 0.5 km and 1.5 km. Build-time assertion: **all 3,500 border vertices lie
within 7.5 m** of the geology edge, or the build aborts.

| field | meaning |
|---|---|
| `source` | "2023 land border + Natural Earth 10m coastline" |
| `land_edge`, `sea_edge` | which source supplied each part |
| `border_layer` | `international_boundary (2023)` |
| `area_km2` | 907,157.0 |

**Read it as:** the clip polygon. Not a legal boundary. The Nigeria–Cameroon line across
Lake Chad is treaty-defined; take that from a gazette or the ICJ ruling, not from a
1:2,000,000 map. Official land area is 923,768 km² — 1.7 % larger, because the official
figure treats Lake Chad and the creeks differently. That is not an error in this polygon.

### 2. `international_boundary` — 1 line, 4,093 km, 3,500 vertices

The 2023 sheet's boundary exactly as printed: a single open LineString, land border only,
no sea edge, `closed = 0`. It is the raw input to layer 1.

Fields: `class`, `name`, `n_frag`, `len_km`, `km_in_nigeria`, `frac_in_nigeria`, `n_vert`,
`mid_lon/lat`, `zone`, `start_lon/lat`, `end_lon/lat`, `closed`. `len_km` is the geodesic
length, the same call and the same name as on the seven other measured line layers — it used
to be called `length_km` here alone, and there was no in-Nigeria field at all.

**Use it for:** drawing a border, or checking your own line against NGSA's.
**Do not use it for:** a polygon (it is open) or a legal claim.

### 3. `water_bodies` — 4 polygons, 152,863 km² drawn, 9.2 % inside Nigeria

Four rows, four different meanings. **Read `kind` and `printed_polygon` first** — this is
the most easily misread layer in the file.

| `name` | `kind` | area km² | in Nigeria | `printed_polygon` | what it actually is |
|---|---|---|---|---|---|
| Gulf of Guinea (Atlantic Ocean) | `sea` | 133,395 | 3,085 | False | the sheet's sea area; clipped by the coastline only |
| Lake Chad | `lake` | 13,373 | 5,670 | **True** | real water polygon, printed blue |
| River Niger / River Benue | `river` | 5,869 | 5,084 | False | a **corridor envelope** around the two channels, *not* water drawn as a polygon |
| *(NULL)* — unnamed reservoir | `lake / reservoir` | 226 | 226 | **True** | real water polygon; `name` is NULL and `name_src` records `no water name on the map` (it sits at 6.90–7.07 E, 9.73–10.03 N) |

Only `printed_polygon = True` (Lake Chad + the reservoir) was allowed to absorb geology
gaps — that is where the `W` / "Water body" unit's 5,671 km² comes from. The `river` row has
15 rings and must not be treated as a lake; using it as water would flood the Niger valley
with false "water" geology.

Other fields: `area_km2` (whole drawn polygon, EPSG:6933 like every other area in the file),
`area_in_nigeria_km2`, `frac_in_nigeria`, `n_rings`, `fill`, `perim_km` (geodesic, interior
rings included), `cen_lon/lat`, bounds, `src_seq`, `note`. All of them are now computed from
the stored geometry; before this pass the areas were up to 10 km² away from it (Lake Chad),
which made them reproducible only by trust, and the unnamed reservoir's in-Nigeria area
(225.7) was larger than its own total (225.56), with `frac_in_nigeria` 1.0006.

---

## 2. Geology

### 4. `geology_units` — 97 rows, 907,157 km², the deliverable layer

**There is one geology layer, and this is it.** 96 rock units + one `W` water unit. Valid,
non-overlapping (residual 0.002 km² = round-off at shared edges), no inland gap (0.006 km²,
same cause), cut on `national_territory`, and `sum(area_km2)` equals the country exactly — so
per-unit areas need no further dissolve, and every point falls in exactly one unit.

Rings are simple: the paint-order replay left 35 hairline slits — a ring running out along a
contact and back along the same line, up to 7.1 km long and zero area wide — and 14 duplicate
vertices. Neither is visible in an area or an overlap test, which is why they survived three
audits; both break simplification and rendering. Removed on 19 units by snapping to a 1e-9°
grid (0.05 mm) and re-validating: the ring set, the point set and the area are unchanged
(1.6 m² of degenerate sliver parts collapsed), and there are no slits or duplicate vertices
left anywhere in the file. `geology_era` had 95 slits of up to 13.8 km and is clean for the
same reason; its copies were rebuilt from the cleaned geometry.

It is built from the 1,518 printed polygons of the 2011 sheet by **replaying the PDF's paint
order**: each path loses exactly the part covered by any path drawn after it. That is a
faithful model of the drawing and cannot be fooled by black label text on top of a unit
(an ink test can). Checked against the printed ink at 1,426/1,462 polygons; the honest
area-weighted version of that check is in the README — 66.8 % of random interior points show
the unit's own colour, and half of the misses are within 1 px of a contact.

Unit mix: 47 sedimentary, 21 metamorphic, 15 plutonic, 6 volcanic, 3 "fault rock", 2 minor
intrusive, 1 water. Ages span 0–4,000 Ma.

| field | meaning |
|---|---|
| `code` | the printed unit code. **Unique, but not case-safe**: `M`/`m` and `Qs`/`qs` are different units |
| `unit` | rock description, from the legend row or the in-map label |
| `leg_desc`, `legend_row` | the legend row this unit resolved to (NULL when the sheet has no row for it) |
| `attr_source` | `legend` (90) / `in-map label` (4) / `printed label only` (2) / NULL (1 = water) — how much to trust the attributes |
| `era`, `period`, `eon`, `epoch` | stratigraphy. **NULL for 5 units** (Gdss, s, P, Gmsh, BCT: 5,296 km²) — see below |
| `age_ma_min` / `age_ma_max` | numeric (float64), younger and older bound |
| `rock_cls` | sedimentary / metamorphic / plutonic / volcanic / minor intrusive / fault rock / water |
| `formation` | formation name where the legend gives one |
| `draw_order` | the paint order this polygon was replayed at (`src_seq`) |
| `filled` | **bool**: did this unit receive assigned (not drawn) ground? True for 75 units, False for 22 |
| `fill_source` | `water body` / `grown from neighbouring unit` / NULL |
| `mapped_km2` | area that was directly digitised (`0` only for `W`: the water unit's ground comes entirely from the printed water polygons, see `fill_source`) |
| `filled_km2` | area assigned: `area_km2 - mapped_km2`. **0 means fully digitised** |
| `area_km2` | total, computed in EPSG:6933 |
| `fill`, `note` | printed colour; provenance note |

Watch-outs:

* **Five codes are printed twice** on the legend (`Esh`, `MS`, `MyP`, `Ncsh`, `Wss`), each row
  a different rock, so those five come in pairs `CODE` and `CODE_<row>`. If you join on an
  external code list, expect to map them.
* **Five printed units are absent from the sheet's own legend** (`OGp`, `Gdss`, `Gmsh`, `LCM`, `S`)
  — real mapped ground, flagged `attr_source`. Two printed codes were normalised onto legend
  rows (`Glls`→`GIls`, `OGe`→`OGp`).
* **Five units have no era at all** (`Gdss` 4,194 km², `s` 671, `P` 312, `Gmsh` 115, `BCT` 4.5):
  896,190 km² is era-classified, 5,671 km² is water, 5,296 km² is unknown. `era IS NULL`
  finds them; the PNG's legend lists them explicitly.
* `Ts` is **not** in this layer: the sheet prints it under `Qs`, the replay leaves it no area,
  and it is recorded in `geology_final_report.json` → `units_dropped_no_area`.
* 7,250 km² (0.8 %) was **assigned rather than drawn**. If a statistic must exclude it,
  subtract `filled_km2` or filter `filled == False` — **not** `filled_km2 == 0`, which selects
  the opposite group.

### 7. `geology_boundaries` — 2,819 lines, 81,849 km, 99.9 % inside Nigeria

The contacts between units, as printed, with the confidence the cartographer gave them:

| `class` | n |
|---|---|
| approximate | 1,481 |
| inferred | 718 |
| exact | 587 |
| transitional | 33 |

These are the source lines, so they are **not** guaranteed to coincide with the edges of
`geology_units` after the paint-order replay — a contact under a later-drawn unit is still
printed here. 39 fragments run past the border (the worst keeps 69 % of its length inside;
99.85 % of the layer's total length is inside).

Fields: `ocg_id`, `layer`, `class`, `stroke`, `width_pt`, `n_frag`, `len_km`, `src_seq`,
`km_in_nigeria`, `frac_in_nigeria`.

### 8. `faults` — 648 lines, 17,704 km, 99.8 % inside Nigeria

Fractures in two classes: **major fracture / fault** (243) and **fracture / fault (inferred)**
(405). Split across two source layers, hence 646 fragments in 2 `ocg_id` groups.

Fields as layer 7. Straight-line drawing, so these are structure traces at 1:2,000,000, not
surveyed fault geometry — do not buffer them into "fault zones" and believe the width.

### 9. `fold_axes` — 90 lines, 1,962 km, 94.6 % inside Nigeria

Anticlinal (8) and synclinal (82) axes. Same field set. 5.6 % of their length runs outside
the border because the sheet draws the neighbouring countries' structure too.

### 10. `younger_granite_outlines` — 59 lines, 2,466 km

The Jurassic Younger Granite ring complexes of the Jos Plateau, as printed. **These are
outlines, not closed rings**: 18 of the 59 return to their start point, the rest do not.
Drawing them as polygons will produce open shapes. The granite *area* is in
`geology_units` (unit `JyG`/`Jyr` etc.); this layer is the ring linework.

---

## 3. Base geography

All seven are **2011 sheet**, so they are 12 years older than the mineral data and
generalised at 1:2,000,000 (1 pt ≈ 0.7 km). The five line layers carry
`km_in_nigeria` / `frac_in_nigeria`; the point layers carry `in_nigeria`, because the sheet
prints neighbouring-country context and it is flagged rather than deleted.

### 11. `rivers` — 1,054 lines, 40,206 km, 83.1 % inside Nigeria

Drainage centrelines. The largest single-source layer in the file: 1,054 fragments from **one**
source `ocg_id`, because a PDF path gets exported per segment. 16.9 % of the length is in
Niger, Benin, Cameroon and Chad — that is the sheet's context, not an error. Fields include
`class`, `stroke`, `width_pt`, `len_km`, `src_seq`.

### 12. `roads` — 122 lines, 19,630 km, 92.5 % inside Nigeria

Trunk roads only; this is not a road network and it is not navigable — no junctions, no
classes beyond `road`, no names. 7.4 % runs outside the border.

### 13. `railway` — 6 lines, 3,084 km, 100 % inside Nigeria

Six long lines, entirely within the country. The only transport layer with no cross-border
content.

### 14. `state_boundaries` — 83 lines, 35,588 km, 92.2 % inside Nigeria

The country's internal boundaries, drawn as 83 fragments: the 36 state boundaries plus the
FCT, but also the neighbouring countries' internal lines, which is why 7.7 % of the length is
foreign. There is **no state attribute** — no names, no codes, no state polygons — so you
cannot group these by state without polygonising them or joining an external boundary set. To get states you would have to
polygonise these lines or join an external boundary set.

### 15. `towns` — 486 points, 463 inside Nigeria

Settlements, with the name taken from the printed label: `name` (82 are NULL — the label was
too far or unreadable), `name_kind`, `name_dist` (how far the label sat from the point),
`src_seq`. Each point is joined to the shipped geology: `unit_code`, `unit`, `unit_era`,
`unit_per` (NULL for the 23 outside Nigeria).

The 23 outside are real (Maradi, Zinder, Aguié… Niger; Cameroonian and Beninese towns) and
flagged `in_nigeria = False`. Positions come from a 1:2,000,000 print, so expect a few km of
label-placement error; this is a gazetteer, not a coordinates table.

### 16. `state_capitals` — 32 points

**32 of the 37 capitals** (36 states plus the FCT), named as the sheet names them (`ILORIN`,
`UYO`, `ABAKILIKI`, `BENIN - CITY`, …), with the same host-unit fields as towns. The five the
sheet's label layer does not carry are **Abuja, Owerri, Yenagoa, Abeokuta and Osogbo** — they
are not in `towns` either, so this layer cannot supply them; take them from `towns_geonames`
(`PPLC`/`PPLA` rows). **These are label centres, not surveyed points — ±15 km.** Good enough to
label a map; not good enough to measure distance to a capital city.

### 17. `volcanic_plugs` — 68 points, all inside Nigeria

Volcanic plugs and necks as point symbols on the sheet, each joined to its host unit. 68 of
68 inside the border. The plugs' *outlines* are not in the file — only the symbol position.

`name` is **NULL for all 68 rows**, by design: the sheet gives the plugs no names, and
`name_kind` says so (`no name on map`). The column is kept because the sibling point layers
have it, not because it holds anything.

---

## 4. Minerals

Eight layers, and the first thing to understand is that **six of them carry positions that
have been withdrawn**. Read this section in full before using any of them.

The audit (`mineral_audit.md`): the extraction stored a transform for the 2023 sheet that is
0.2 % out in longitude scale and 3.5 pt out in latitude offset, and the per-symbol positions
were never on the glyphs anyway. Measured against the sheet, they sit a median **14.1 px =
9.6 km** from any symbol ink, only 5.9 % within 1 px, and the nearest-neighbour distribution
is statistically indistinguishable from a random scatter. I re-measured this independently:
stored points 12.1 km median, shuffled x/y 13.9–14.2 km, uniform-in-territory 15.4 km.

So: **valid positions → `minerals_named`. Usable commodity attributes → `mineral_symbols`,
filtered on `is_symbol = 1`.** Everything else in the family is kept for provenance and
comparison, and `mineral_localities*` is queued for rebuild.

Which copy comes from which matters here, because the names do not say:

| layer | CRS | parent | what it adds |
|---|---|---|---|
| 20 `mineral_localities` | 4326 | — | the extraction as it stands |
| 21 `mineral_localities_refined` | 4326 | 20 | `pos_method`, `pos_sigma_m`, `pos_confidence`, `reassigned_from` |
| 22 `mineral_localities_icons` | 4326 | 21 | icon anchoring: `locality_id`, `n_icons`, `icon_tier`, `moved_from_label_m` |
| 23 `mineral_localities_icons_utm32n` | 32632 | 22 | the projection only — *copies file* |
| 24 `mineral_localities_equal_area` | 6933 | 22 | the projection only — *copies file* |
| 25 `mineral_localities_utm32n` | 32632 | **21** | the projection only, *not* layer 20 in metres — *copies file* |

### 18. `mineral_symbols` — 1,609 rows, **POSITIONS WITHDRAWN**

The extraction's reading of the printed symbols: one row per mark it thought was a symbol.

| field | meaning |
|---|---|
| `mineral` | the commodity it read. Usable — **after filtering** |
| `is_symbol` | **1 = countable printed symbol (1,489 rows); 0 = not a symbol (120)** |
| `colour`, `fill` | printed colour |
| `ident_mth`, `ident_scr` | how the identification was made and its score |
| `link`, `near_num` | link to a locality / nearest printed number |
| `in_nigeria` | 1,603 of 1,609 |

The 120 non-symbols, which is why `value_counts()` on this column is a trap:

| what | n |
|---|---|
| raster slivers (linework, dashes) | 56 |
| state-capital squares | 21 |
| fragments of a symbol already counted | 15 |
| halves of a symbol already counted | 8 |
| linework / label fragments | 8 |
| merged clusters of touching symbols | 5 |
| bridge / water markings | 5 |
| merged touching pairs | 2 |

Unfiltered, they show up as a phantom commodity called `not a mineral symbol: raster sliver`
with 56 members. On the 1,489 real symbols: 66 distinct commodities, Limestone 136, Clay 174,
Gold 112, Kaolin 109.

### 19. `minerals_named` — 1,323 rows, **the valid printed symbols** (±0.35 km)

Every printed mineral glyph re-detected on the sheet at its native 75 dpi; the point is the
**measured centroid of the glyph body**, so it is on the symbol by construction. Verified:
94.9 % within 1 px of symbol ink (a random point in the same area: 8.5 %).

| field | meaning |
|---|---|
| `canvas_x/y`, `lon`, `lat` | pixel and geographic position |
| `colour_family`, `w_px`, `h_px` | the signature the naming used |
| `mineral` | commodity name, or NULL (1,305 named, 18 withheld) |
| `tier` | `probable` ≥70 % family accuracy (973) / `tentative` 50–70 % (332) / `unidentified` (18) |
| `confidence`, `family_accuracy_pct` | per-row score and the accuracy of its colour family |
| `mineral_class` | metallic (338) / industrial (777) / gemstone (144) / energy (46) / NULL (18) |
| `previously_named`, `prior_name` | whether the old extraction named it, and what it said |
| `details` | what the commodity is |
| `in_nigeria` | 1,179 of 1,323 (144 are printed outside the border by design — the sheet maps the whole region) |

**This is what the shipped PNG/PDF draws.** Limits: per-symbol names are ~81 % accurate, but
**per-mineral totals are not reliable here** (Limestone reads 30 against the extraction's 136;
Baryte is never detected). Use this layer for *where*, `mineral_symbols.is_symbol = 1` for
*how many*. The detector also finds 1,323 of ~1,531 marks, the shortfall being small plain
glyphs — see `minerals_named.md` §5.

### 20. `mineral_localities` — 999 rows, **POSITIONS WITHDRAWN**

The 2023 sheet's numbered localities, straight from the extraction, with the richest
commodity vocabulary: `zone` (A–G), `number`, `locality` (name), `minerals` (all commodities at
that locality), `mineral_1`, `group_1` (9 groups: industrial 307, construction 283, rare metals
135, gemstones 75, precious metals 72, ferrous 47, energy 45, base metals 34, no code 1),
`n_minerals`, `n_unknown`, `symbol`, `sym_colour`, `pos_src`, `label_lon/lat`, `min_conf`,
plus the host-unit join (`host_unit`, `host_code`, `host_era`, `host_period`, `host_age_ma`,
`host_dist_m`) and `in_nigeria` (991/999).

**80 commodities.** One locality lists as many as 4; 874 list one. `zone`+`number` is *not*
unique — 39 printed numbers are shared by two records — so key on nothing here; the key is
`locality_id` in layer 22.

`min_conf` is **dirty free text** from the extraction: `certain` (595), `legend` (114),
`probable` (93), but also concatenations like `certain certain` (54), `certain legend` (18),
`uncertain uncertain` (3) and 20-odd other spellings. Do not use it as a clean category.

### 21. `mineral_localities_refined` — 999 rows, **POSITIONS WITHDRAWN**

The earlier positioning policy, kept only for comparison: same localities, plus
`pos_method`, `pos_sigma_m`, `pos_confidence`, `reassigned_from`. It is **the only layer with
`pos_sigma_m` / `pos_confidence`** — which is why older documentation that says "every point
carries a sigma" was describing this layer, not the shipped one. Superseded twice over.

### 22. `mineral_localities_icons` — 999 rows, **POSITIONS WITHDRAWN**

The most developed of the locality layers — intended to be the best of them — and still
invalid, because it rests on the same discredited symbol coordinates. It adds
`locality_id` (the unique key: zone+number, e.g. `A5`), `n_icons`, `icon_spread_m`,
`icon_tier` (mineral identity 702 / recorded colour 111 / inferred colour 7 / none 179),
`pos_method` (single icon centre 681, number label only 179, medoid of 2–4 icons 139),
`moved_from_label_m`, `dist_to_coast_m`, `shared_number`, `host_code`,
`host_boundary_dist_m`, `group_centroid_lon/lat`.

Its construction is still worth knowing, because it is the right method on the wrong input:
where a locality owns several printed icons, the point is a **medoid** — a real icon nearest
the group centre — never the centroid, which would fall on blank paper between two deposits.
`group_centroid_lon/lat` records where that rejected centroid was.

Caveats even after the rebuild: 15 geometries are deliberate duplicates (two records at one
position: 29 rows in 14 positions), and `dist_to_coast_m > 0` for 4 points 0.9–5.7 km offshore.

---

## 5. QA layers

Both are **instruments, not geography**: they are the graticule fitted to each sheet, used to
derive and verify the affine transforms. 33–36 % of their length runs past the map frame, which
is the point — they are what the fit was measured on.

### 26. `graticule_geology` — 22 lines, 24,041 km

The 1° graticule fitted to the 2011 sheet: 12 meridians and 10 parallels, `axis`, `value`,
`label` (`3°E`…), `page_pt` (where the line sits on the page), `length_km`, `n_lines`. This is
the evidence for the geology affine `lon = (x + 276.36)/157.593, lat = (2281.63 - y)/157.586`,
residual 0.20 pt = 130 m.

### 27. `graticule_minerals` — 11 lines, 13,664 km

The graticule fitted to the 2023 sheet, plus the field that documents a source defect:
`vp_value` is what the extraction's table said (4.172 for the 4°E line), `printed` is what the
sheet says (4), `offset_deg` = 0.172 and `label_offset_deg` = 0.17217 record the **+0.172°
(19 km) mislabelling** that was removed. Only that QA table was wrong — the 2023 feature
layers check out against the 2011 ones (boundary 0.1 km, towns 0.5 km).

---

## 6. The gazetteer

### 28. `towns_geonames` — 45,415 points

Every populated place GeoNames records for Nigeria, from the `allCountries` dump
(snapshot 2014-10-02, CC BY 4.0, "GeoNames, geonames.org"). It answers the question
the printed sheet cannot: the 2011 map labels 486 towns, GeoNames has 45,415, and
only one of the 32 state capitals appears in both layers.

| field | what it is |
|---|---|
| `geonameid` | the GeoNames id — the stable key |
| `coord_dp` | decimal places GeoNames recorded for the position: **7,372 of 45,415 entries have 2 or fewer**, i.e. a position good to about 1 km at best and 50 km at worst. Filter on it before measuring distances |
| `state`, `state_gn`, `state_agree` | state from the polygon the point falls in; GeoNames' own state; and `state_agree` as a real BOOLEAN where both exist (93.7 % of 31,913 agree; 427 of those have no polygon state, so they agree by construction) |
| `population` | 0 where GeoNames records none — only **450** places carry a figure |
| `elevation_m`, `dem_m` | spot elevation and digital model height, as recorded, NULL where absent. GeoNames records a spot elevation for only 22 rows, so use `dem_m`: it holds 45,371 values, with 44 NULLs where GeoNames gave the SRTM void `-9999` or a small negative over water |
| `dup_group` | 642 rows are a second spelling of a place already in the layer; 2,638 rows share an exact coordinate with another row |

Full provenance, the licence, and the two independent accuracy checks are in
[`towns_geonames.md`](towns_geonames.md). In short: 98.9 % fall inside the
territory, and against published coordinates for 15 major cities the median error
is 0.55 km.

## 7. The class polygons (29–31)

These three are not traced from a scan for its own sake: the raster-or-vector
question was decided per sheet by measurement, and only the sheets whose classes
are flat fills with a readable legend became polygons (`RASTER_VS_VECTOR.md`).
Every one keeps its source raster beside it.

### 29. `poly_soil_ph` — 111 polygons, 906,612 km², 5 classes

The soil-pH sheet, traced: 1.02 km/px print, class colours measured from the
printed swatches (not transcribed by eye), clipped to `national_territory`,
33,030 km² of seam holes no wider than 3 px repaired by claiming the nearest
labelled class (the blank went from 33,575 km² in 974 pieces to 545 km² in 143).

| class | km² | polygons | swatch |
|---|---|---|---|
| 0.01 - 5.5 | 358,348 | 26 | `#10ad7a` |
| 5.6 - 6.8 | 364,326 | 38 | `#7df901` |
| 6.9 - 7.8 | 88,084 | 20 | `#fcba04` |
| 7.9 - 8.3 | 92,644 | 23 | `#c94d35` |
| *unlabelled (dark navy, legend swatch 1)* | 3,209 | 4 | `#00227b` |

* **The fifth class has no printed value.** Its swatch is a real printed fill
  (2,422 sheet pixels within ΔE 30 of it) with no legible label. It is named for
  what is known — the colour and its position in the legend — rather than `0`,
  which is what an earlier transcription guessed and what the sheet does not say.
* **Class edges are good to about 1 km, plus the sheet's own registration error**
  (per-side offsets −3.2 / −0.9 / −4.1 / −3.7 km).
* Verified: 106 of 111 polygons sample a sheet pixel within ΔE 24 of their own
  swatch at an interior point (`polygon_colour_check.json`); the other five have
  their interior point beyond the edge of the printed plate.

### 30. `poly_population` — 299 polygons, 839,255 km², 5 classes

The population sheet, traced: 2.37 km/px, classes of **absolute** population by
**unnamed** district.

| class | km² | polygons | swatch |
|---|---|---|---|
| 0 - 110,85 | 137,172 | 60 | `#f7f5a3` |
| 110,853 - 144,579 | 138,857 | 64 | `#f5db70` |
| 144,580 - 179,550 | 155,355 | 70 | `#f1b944` |
| 179,551 - 232,287 | 203,122 | 57 | `#c16018` |
| 232,288 - 1,319,571 | 204,750 | 48 | `#600a14` |

* **7.5 % of the territory is not covered, and that is correct**: 67,902 km² in
  1,786 pieces, the largest 26,116 km² in the north-east corner, are places the
  sheet leaves uncoloured. Only 26.8 % of that blank lies within 3 px of a fill,
  against 96.2 % for the soil-pH sheet, so nothing is filled in.
* **The class labels are as printed, and the first one is a truncated reading**:
  `0 - 110,85` — almost certainly 110,85x on the sheet, cut off in the scan. The
  labels also contain commas, so join on `class_id` (1–5) and keep `class_name`
  for display.
* **The districts are unnamed**, so this cannot be joined to any admin layer, and
  as an absolute count it cannot be normalised by area. It is a picture of a
  population sheet, in polygons.
* Three polygons (3,090 km² in total) read a sheet pixel one class away from
  their traced class at their interior point — row-classification noise at
  2.4 km/px, reported in `polygon_colour_check.json`.

### 31. `geology_era` — 7 polygons, 907,157 km²

**Seven era classes, dissolved from the attributed `geology_units` vector** rather
than traced from the 2.5 km/px screenshot — exact in area, no tracing error, keyed
by `class_id` like the other two class layers.

It is **not** a reproduction of the general-geology sheet's legend. That legend
draws **nine** classes, and they are era *plus lithology* (three Cenozoic: alluvials;
sands and clays; volcanics — and so on for Mesozoic and Palaeozoic-Proterozoic),
with no water and no unclassified class. Dissolving our 97 attributed units by era
gives seven, because the vector geology carries one era per unit and no lithological
subdivision at that level. The layer is therefore the vector generalisation of that
sheet, not a transcription of it: it is coarser, and it says so.

| `class_id` | era | km² |
|---|---|---|
| 1 | Cenozoic | 303,554 |
| 2 | Archaean-Palaeoproterozoic, reworked in the Neoproterozoic | 222,935 |
| 3 | Mesozoic | 177,131 |
| 4 | Neoproterozoic-Palaeozoic | 136,202 |
| 5 | Neoproterozoic (Pan-African deformed) | 56,369 |
| 6 | Water | 5,671 |
| 7 | unclassified | 5,296 |

`unclassified` is the five units the source map gives no stratigraphy for (`Gdss`,
`s`, `P`, `Gmsh`, `BCT`) — see §9, item 5. It is not a gap in coverage: the layer
covers all 907,157 km².

## The five reprojections

These are the same features as their 4326 parents — same rows, same attributes, same key,
geometry reprojected — and they live in a second file so that the deliverable is one CRS:

    Nigeria_Geology_Minerals_projected_copies.gpkg   (51 MB is the main file; this one is ~8 MB)

| layer | CRS | parent | rows | use it for |
|---|---|---|---|---|
| `geology_units_utm32n` | EPSG:32632 | `geology_units` | 97 | local metric work inside 6–12° E; **not** area |
| `geology_units_equal_area` | EPSG:6933 | `geology_units` | 97 | area, coverage, density (exact) |
| `mineral_localities_icons_utm32n` | EPSG:32632 | `mineral_localities_icons` | 999 | local distance (positions withdrawn) |
| `mineral_localities_equal_area` | EPSG:6933 | `mineral_localities_icons` | 999 | equal-area work (positions withdrawn) |
| `mineral_localities_utm32n` | EPSG:32632 | `mineral_localities_refined` | 999 | local distance (positions withdrawn) |

You do not need them to work in metres: `pyproj.Geod` gives geodesic area and length from the
4326 layers directly, and `gdf.to_crs(6933)` costs nothing on these row counts. They are kept
because a stored measurement is reproducible and a recomputed one can drift with the library.

`split_projected_copies.py` did the move and `audit_layers.py` re-proves it every run: the copy's
every attribute is compared with its parent and its geometry with the parent reprojected (max
offset 0.00 m), and the deliverable is asserted to hold nothing but EPSG:4326.

#### 5. `geology_units_utm32n` — 97 rows, EPSG:32632

The same 97 units in UTM 32N, with the same attributes. Areas here read **+0.19 %** high, and
lengths are worse at the eastern and western edges, because Nigeria spans zones 31N, 32N and
33N and this is one zone. **Use for local metric work inside 6–12°E; do not use for area.**

#### 6. `geology_units_equal_area` — 97 rows, EPSG:6933

The same, on the equal-area projection, plus `area_km2_equal_area`. This is the layer to
compute area, coverage, density or share-of-country from: it matches the geodesic figure to
0.000 %. `geology_units` and this layer give identical totals — pick by CRS convenience, not
by accuracy.

#### 23. `mineral_localities_icons_utm32n` — 999 rows, EPSG:32632

Layer 22 in metres, same attributes. Same withdrawal applies.

#### 24. `mineral_localities_equal_area` — 999 rows, EPSG:6933

Layer 22 on the equal-area projection. Note 17 duplicate geometries here against 15 in 4326 —
reprojection rounds two more pairs onto the same coordinate. Same withdrawal applies.

#### 25. `mineral_localities_utm32n` — 999 rows, EPSG:32632

**This is the EPSG:32632 copy of layer 21, `mineral_localities_refined` — not of layer 20.**
The name is historic: the layer was written by `refine_localities.py` alongside the refined
positions, and its coordinates match layer 21 in 999 of 999 rows while differing from layer 20
by up to **11.9 km** in 117 rows. Its columns are layer 21's (`pos_sigma_m`,
`pos_confidence`, `reassigned_from`, `host_boundary_dist_m`), not layer 20's. Read the
coordinates as refined. If you need the raw extraction in metres, project layer 20 yourself —
both carry withdrawn positions, so the difference is historical, not usable data.

---

## 8. Which layer do I want?

| if you want to… | use |
|---|---|
| draw Nigeria | `national_territory` |
| map or quantify geology | `geology_units`; areas and shares from `geology_units_equal_area` |
| put a point on a unit | spatial-join against `geology_units` (no dedupe needed — one unit per point) |
| study structure | `faults`, `fold_axes`, `geology_boundaries`, `younger_granite_outlines` |
| map mineral **deposits** | `minerals_named` |
| count mineral **symbols per commodity** | `mineral_symbols` where `is_symbol = 1` |
| work with the 999 numbered localities and their commodity lists | `mineral_localities` (attributes), `mineral_localities_icons` (`locality_id`), **positions not yet rebuilt** |
| plot towns / capitals / roads / rivers | layers 11–17, filtered on `in_nigeria` / `frac_in_nigeria` if you need only Nigeria |
| check the georeferencing | `graticule_geology`, `graticule_minerals` |

## Provenance inside the file

`gpkg_metadata` holds four ISO 19139 records and `gpkg_metadata_reference` says what each
one is about: the whole file (`geopackage` scope — title, abstract, lineage, bounding box
and the licence of every source), `towns_geonames` (the GeoNames **CC BY 4.0** attribution),
`national_territory` and `international_boundary` (Natural Earth 1:10m, public domain,
edited onto the 2023 sheet border), and the mineral layers (the positions-withdrawn
notice, so a reader who opens `mineral_symbols` in any GIS finds it). `add_gpkg_metadata.py`
writes them with pinned ids and dates, so a rerun is byte-identical; `audit_layers.py`
re-parses the XML on every run and fails if a record is malformed, a reference is dangling,
the CC BY 4.0 text is missing, or the withdrawal notice is gone.

## 9. Read this before you compute

1. **Storage CRS is EPSG:4326 — never compute area in it** (you get square degrees). Area →
   EPSG:6933. Countrywide length/distance → geodesic (`pyproj.Geod`). Local length → UTM by
   zone (31N / 32N / 33N; the 32N copies are wrong at the edges). Never EPSG:3857 (+3.68 %
   over Nigeria).
2. **Do not use any `mineral_localities*` position for calculation.** Valid positions are
   `minerals_named`; valid counts are `mineral_symbols[is_symbol == 1]`.
3. **`ocg_id` is not a key.** It identifies the object on the sheet and one printed line can
   be many fragments (1,054 river fragments from one object). Keys: `locality_id` (all six
   locality layers carry it, and it is unique), `code` (geology), `class_id` (the three class
   layers), `geonameid` (the gazetteer), `src_seq` (the base layers, unique within each).
4. **`code` is case-sensitive**: `M` ≠ `m`, `Qs` ≠ `qs`. Lowercasing it merges two different
   units.
5. **Missing values are NULL, never `""`.** This is enforced, not hoped for:
   `normalise_nulls.py` rewrites any empty string to NULL and `audit_layers.py` fails
   if one reappears. Where `era` is NULL, the sheet gives no stratigraphy — it was
   not guessed. Before the 2026-10-27 pass the file held **131,755 empty strings**
   across nine layers, and the projected copies of `geology_units` disagreed with
   it: 24 NULL periods in the base layer, 5 NULL and 19 empty in each copy.
6. **`filled_km2 == 0` selects fully digitised units**, not filled ones. Use `filled == False`.
7. **Duplicate point geometries are deliberate** in the locality layers (46 in layers 20
   and 21, 15 in layer 22, 17 in the equal-area copy — reprojection rounds two more pairs
   onto one coordinate); they are distinct records, not rows to drop.
8. **The low "in Nigeria" percentages on `water_bodies`, `graticule_geology` and
   `graticule_minerals` are by design** — sea, cross-border water, and fit lines. Do not clip
   them and do not add them to a total.

9. **`mineral_localities_utm32n` (25) is not layer 20 in metres.** It holds layer 21's
   refined positions, and the two differ by up to 11.9 km in 117 rows. See §Minerals, layer 25.
10. **`legend_row` is not unique and not a key.** It is the printed legend row, and two codes
   can sit on one row: `LCM` and `Mcst` both carry row 25. It is a pointer back to the paper,
   nothing more.
11. **`coord_dp` in `towns_geonames` is the precision of the position**, in decimal places.
   7,372 entries are at 2 or fewer — up to 1 km, and at 0–1 up to tens of km. A nearest-city
   query that ignores it will return places that are not where they say.
12. **`lon`/`lat` and the geometry are the same point** in `towns`, `state_capitals` and
   `volcanic_plugs` (6 decimal places, about 0.1 m); in the projection copies the coordinates
   round-trip to within a millimetre. A query cannot get two answers for one point — that was
   not true before 2026-10-27, when the two copies disagreed by up to 0.1 m in 584 rows.
13. **Every row's length is one measure.** `len_km` and `km_in_nigeria` are both geodesic, and
   `frac_in_nigeria` is their ratio, so `km_in_nigeria <= len_km` always. Before the 2026-10-27
   pass the two were measured differently — `len_km` on the ellipsoid, `km_in_nigeria` on the
   EPSG:6933 grid, which stretches a north-south line in this latitude range — and the
   in-Nigeria figure came out *longer than the whole line* in 26 state-boundary, 71 road, 580
   river, 486 fault, 39 fold-axis and 1,972 geology-boundary rows. `frac_in_nigeria` was
   clamped to hide it. `audit_layers.py` now re-measures every line geodesically and fails if
   the attributes disagree.
14. **`water_bodies.perim_km` includes the interior rings** (Lake Chad has 38 holes, 640 km of
   shoreline): it is 1,570 km, of which 930 km is the outer shore. `area_in_nigeria_km2` is
   never larger than `area_km2`, and `frac_in_nigeria` is their ratio.
15. **A missing value is never a sentinel.** `towns_geonames.dem_m` held 42 × `-9999` (the SRTM
   void, all coastal or riverine) and two small negatives before this pass — an elevation of
   -9,999 m that any `MIN()` or `< 500` test would have counted as data. It is NULL now, and
   the audit fails on any `-9999` / `-99999` / `-32768` in any numeric column.
16. **No value is cut off at a fixed width.** Two were: `mineral_symbols.link` stopped at
   "colour not consi" in 448 rows, and `towns_geonames.alt_names` could stop mid-name in the
   middle of its list. Both are whole now, and the audit checks that the strings that were
   truncated are complete.
17. **Text carries no padding, no double spaces and no control characters.** One town name had
   a double space and `Gabu(Ogaja)` was the one locality of 999 written without a space before
   its parenthetical; both are join keys, so both are fixed.
18. **`geology_units.formation` is a name, not a note.** Twelve rows carried the provenance tag
   "(chart key)" inside the name, one read "Awgu - Formation" with a dash before the word
   Formation, and three held a lithology ("Sediments", "Mangroves swamps", "Meader belt …")
   because the sheet's legend row gave no formation — those three are NULL now, with a `note`,
   and `unit` still holds the printed description. 37 names, all clean.
