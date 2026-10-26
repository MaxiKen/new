# Layer catalogue — `Nigeria_Geology_Minerals_4326.gpkg`

**27 vector layers, 14,723 features** — plus **9 georeferenced raster layers**, documented
separately in [`RASTER_LAYERS.md`](RASTER_LAYERS.md). 22 layers in EPSG:4326 (11,532 features), 3 in EPSG:32632
(2,095), 2 in EPSG:6933 (1,096). Every layer has a CRS, 0 invalid / empty / null geometries,
and is verified by `audit_layers.py` (result: `layer_audit.json`, 0 problems).

Two sheets feed it, and it matters which one for what:

* **2011 Geological Map** → all base geography, geology, faults, folds, water, settlements, transport.
* **2023 Mineral Resources Map** → the mineral symbols, the 999 numbered localities, the
  international boundary.

Navigation: [Boundary & water](#1-boundary-and-water) · [Geology](#2-geology) ·
[Base geography](#3-base-geography) · [Minerals](#4-minerals) · [QA](#5-qa-layers) ·
[How to choose](#6-which-layer-do-i-want) · [Read this before you compute](#7-read-this-before-you-compute)

---

## Summary table

| # | layer | n | CRS | geometry | in Nigeria | one-line purpose |
|---|---|---|---|---|---|---|
| 1 | `national_territory` | 1 | 4326 | Polygon | 100 % | the country polygon everything is clipped to |
| 2 | `international_boundary` | 1 | 4326 | LineString | 100 % | the 2023 land border as printed |
| 3 | `water_bodies` | 4 | 4326 | MultiPolygon | 9.2 %* | sea, Lake Chad, the Niger–Benue corridor |
| 4 | `geology_units` | 97 | 4326 | MultiPolygon | 100 % | **the geology**: 96 rock units + water |
| 5 | `geology_units_utm32n` | 97 | 32632 | MultiPolygon | 100 % | the same, metres |
| 6 | `geology_units_equal_area` | 97 | 6933 | MultiPolygon | 100 % | the same, exact areas |
| 7 | `geology_boundaries` | 2,819 | 4326 | LineString | 99.9 % of 84,001 km | contacts, by confidence |
| 8 | `faults` | 648 | 4326 | LineString | 99.8 % of 18,669 km | major and inferred faults |
| 9 | `fold_axes` | 90 | 4326 | LineString | 94.4 % | anticlines and synclines |
| 10 | `younger_granite_outlines` | 59 | 4326 | LineString | 100 % | Jos Plateau ring complexes, as outlines |
| 11 | `rivers` | 1,054 | 4326 | LineString | 83.1 % of 41,194 km | drainage centrelines |
| 12 | `roads` | 122 | 4326 | LineString | 92.6 % of 19,842 km | trunk roads |
| 13 | `railway` | 6 | 4326 | LineString | 100 % of 3,131 km | rail lines |
| 14 | `state_boundaries` | 83 | 4326 | LineString | 92.3 % of 36,044 km | 36 states + FCT |
| 15 | `towns` | 486 | 4326 | Point | 463/486 | settlements, with host unit |
| 16 | `state_capitals` | 32 | 4326 | Point | 32/32 | capitals, label centres ±15 km |
| 17 | `volcanic_plugs` | 68 | 4326 | Point | 68/68 | plugs and necks |
| 18 | `mineral_symbols` | 1,609 | 4326 | Point | 1,603/1,609 | **positions withdrawn**; attributes usable |
| 19 | `minerals_named` | 1,323 | 4326 | Point | 1,179/1,323 | **the valid printed symbols** (±0.35 km) |
| 20 | `mineral_localities` | 999 | 4326 | Point | 991/999 | **positions withdrawn**; raw extraction |
| 21 | `mineral_localities_refined` | 999 | 4326 | Point | 992/999 | **positions withdrawn**; older policy |
| 22 | `mineral_localities_icons` | 999 | 4326 | Point | 995/999 | **positions withdrawn**; icon-anchored |
| 23 | `mineral_localities_icons_utm32n` | 999 | 32632 | Point | same | the same, metres |
| 24 | `mineral_localities_equal_area` | 999 | 6933 | Point | same | the same, equal-area |
| 25 | `mineral_localities_utm32n` | 999 | 32632 | Point | 991/999 | (20) in metres |
| 26 | `graticule_geology` | 22 | 4326 | LineString | 66.5 %* | QA: the 2011 graticule fit |
| 27 | `graticule_minerals` | 11 | 4326 | LineString | 63.6 %* | QA: the 2023 graticule fit |

\* low "in Nigeria" share is by design for these three — they are sea, cross-border water and
graticule lines that run past the map frame. Do not clip them, do not add them to an area total.

---

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

### 2. `international_boundary` — 1 line, 4,166 km, 3,500 vertices

The 2023 sheet's boundary exactly as printed: a single open LineString, land border only,
no sea edge, `closed = 0`. It is the raw input to layer 1.

Fields: `class`, `name`, `n_frag`, `length_km`, `n_vert`, `mid_lon/lat`, `zone`,
`start_lon/lat`, `end_lon/lat`, `closed`.

**Use it for:** drawing a border, or checking your own line against NGSA's.
**Do not use it for:** a polygon (it is open) or a legal claim.

### 3. `water_bodies` — 4 polygons, 152,863 km² drawn, 9.2 % inside Nigeria

Four rows, four different meanings. **Read `kind` and `printed_polygon` first** — this is
the most easily misread layer in the file.

| `name` | `kind` | area km² | in Nigeria | `printed_polygon` | what it actually is |
|---|---|---|---|---|---|
| Gulf of Guinea (Atlantic Ocean) | `sea` | 133,390 | 3,085 | False | the sheet's sea area; clipped by the coastline only |
| Lake Chad | `lake` | 13,363 | 5,670 | **True** | real water polygon, printed blue |
| River Niger / River Benue | `river` | 5,870 | 5,084 | False | a **corridor envelope** around the two channels, *not* water drawn as a polygon |
| (unnamed reservoir) | `lake / reservoir` | 226 | 226 | **True** | real water polygon |

Only `printed_polygon = True` (Lake Chad + the reservoir) was allowed to absorb geology
gaps — that is where the `W` / "Water body" unit's 5,671 km² comes from. The `river` row has
15 rings and must not be treated as a lake; using it as water would flood the Niger valley
with false "water" geology.

Other fields: `area_km2` (whole drawn polygon), `area_in_nigeria_km2`, `frac_in_nigeria`,
`n_rings`, `fill`, `perim_km`, `cen_lon/lat`, bounds, `src_seq`, `note`.

---

## 2. Geology

### 4. `geology_units` — 97 rows, 907,157 km², the deliverable layer

**There is one geology layer, and this is it.** 96 rock units + one `W` water unit. Valid,
non-overlapping (residual 0.002 km² = round-off at shared edges), no inland gap, cut on
`national_territory`, and `sum(area_km2)` equals the country exactly — so per-unit areas
need no further dissolve, and every point falls in exactly one unit.

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
| `mapped_km2` | area that was directly digitised |
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

### 5. `geology_units_utm32n` — 97 rows, EPSG:32632

The same 97 units in UTM 32N, with the same attributes. Areas here read **+0.19 %** high, and
lengths are worse at the eastern and western edges, because Nigeria spans zones 31N, 32N and
33N and this is one zone. **Use for local metric work inside 6–12°E; do not use for area.**

### 6. `geology_units_equal_area` — 97 rows, EPSG:6933

The same, on the equal-area projection, plus `area_km2_equal_area`. This is the layer to
compute area, coverage, density or share-of-country from: it matches the geodesic figure to
0.000 %. `geology_units` and this layer give identical totals — pick by CRS convenience, not
by accuracy.

### 7. `geology_boundaries` — 2,819 lines, 84,001 km, 99.9 % inside Nigeria

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

### 8. `faults` — 648 lines, 18,669 km, 99.8 % inside Nigeria

Fractures in two classes: **major fracture / fault** (243) and **fracture / fault (inferred)**
(405). Split across two source layers, hence 646 fragments in 2 `ocg_id` groups.

Fields as layer 7. Straight-line drawing, so these are structure traces at 1:2,000,000, not
surveyed fault geometry — do not buffer them into "fault zones" and believe the width.

### 9. `fold_axes` — 90 lines, 1,983 km, 94.4 % inside Nigeria

Anticlinal (8) and synclinal (82) axes. Same field set. 5.6 % of their length runs outside
the border because the sheet draws the neighbouring countries' structure too.

### 10. `younger_granite_outlines` — 59 lines, 2,519 km

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

### 11. `rivers` — 1,054 lines, 41,194 km, 83.1 % inside Nigeria

Drainage centrelines. The largest single-source layer in the file: 1,054 fragments from **one**
source `ocg_id`, because a PDF path gets exported per segment. 16.9 % of the length is in
Niger, Benin, Cameroon and Chad — that is the sheet's context, not an error. Fields include
`class`, `stroke`, `width_pt`, `len_km`, `src_seq`.

### 12. `roads` — 122 lines, 19,842 km, 92.6 % inside Nigeria

Trunk roads only; this is not a road network and it is not navigable — no junctions, no
classes beyond `road`, no names. 7.4 % runs outside the border.

### 13. `railway` — 6 lines, 3,131 km, 100 % inside Nigeria

Six long lines, entirely within the country. The only transport layer with no cross-border
content.

### 14. `state_boundaries` — 83 lines, 36,044 km, 92.3 % inside Nigeria

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

One point per state capital plus Abuja, named (`ILORIN`, `UYO`, `ABAKILIKI`, …), with the
same host-unit fields as towns. **These are label centres, not surveyed points — ±15 km.**
Good enough to label a map; not good enough to measure distance to a capital city.

### 17. `volcanic_plugs` — 68 points, all inside Nigeria

Volcanic plugs and necks as point symbols on the sheet, each joined to its host unit. 68 of
68 inside the border. The plugs' *outlines* are not in the file — only the symbol position.

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

### 23. `mineral_localities_icons_utm32n` — 999 rows, EPSG:32632

Layer 22 in metres, same attributes. Same withdrawal applies.

### 24. `mineral_localities_equal_area` — 999 rows, EPSG:6933

Layer 22 on the equal-area projection. Note 17 duplicate geometries here against 15 in 4326 —
reprojection rounds two more pairs onto the same coordinate. Same withdrawal applies.

### 25. `mineral_localities_utm32n` — 999 rows, EPSG:32632

Layer 20 in metres (the raw extraction, with `pos_sigma_m`/`pos_confidence`). Same withdrawal
applies.

---

## 5. QA layers

Both are **instruments, not geography**: they are the graticule fitted to each sheet, used to
derive and verify the affine transforms. 33–36 % of their length runs past the map frame, which
is the point — they are what the fit was measured on.

### 26. `graticule_geology` — 22 lines, 24,230 km

The 1° graticule fitted to the 2011 sheet: 12 meridians and 10 parallels, `axis`, `value`,
`label` (`3°E`…), `page_pt` (where the line sits on the page), `length_km`, `n_lines`. This is
the evidence for the geology affine `lon = (x + 276.36)/157.593, lat = (2281.63 - y)/157.586`,
residual 0.20 pt = 130 m.

### 27. `graticule_minerals` — 11 lines, 13,765 km

The graticule fitted to the 2023 sheet, plus the field that documents a source defect:
`vp_value` is what the extraction's table said (4.172 for the 4°E line), `printed` is what the
sheet says (4), `offset_deg` = 0.172 and `label_offset_deg` = 0.17217 record the **+0.172°
(19 km) mislabelling** that was removed. Only that QA table was wrong — the 2023 feature
layers check out against the 2011 ones (boundary 0.1 km, towns 0.5 km).

---

## 6. Which layer do I want?

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

## 7. Read this before you compute

1. **Storage CRS is EPSG:4326 — never compute area in it** (you get square degrees). Area →
   EPSG:6933. Countrywide length/distance → geodesic (`pyproj.Geod`). Local length → UTM by
   zone (31N / 32N / 33N; the 32N copies are wrong at the edges). Never EPSG:3857 (+3.68 %
   over Nigeria).
2. **Do not use any `mineral_localities*` position for calculation.** Valid positions are
   `minerals_named`; valid counts are `mineral_symbols[is_symbol == 1]`.
3. **`ocg_id` is not a key.** It identifies the object on the sheet and one printed line can
   be many fragments (1,054 river fragments from one object). Keys: `locality_id`
   (localities), `code` (geology), row order otherwise.
4. **`code` is case-sensitive**: `M` ≠ `m`, `Qs` ≠ `qs`. Lowercasing it merges two different
   units.
5. **Missing values are NULL, never `""`** (except `fill_source`/`note` on the 22 fully
   digitised units, which are NULL too). Where `era` is NULL, the sheet gives no
   stratigraphy — it was not guessed.
6. **`filled_km2 == 0` selects fully digitised units**, not filled ones. Use `filled == False`.
7. **Duplicate point geometries are deliberate** in the locality layers (15 in layer 22);
   they are distinct records, not rows to drop.
8. **The low "in Nigeria" percentages on `water_bodies`, `graticule_geology` and
   `graticule_minerals` are by design** — sea, cross-border water, and fit lines. Do not clip
   them and do not add them to a total.
