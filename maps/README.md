# Geology and Mineral Resources of Nigeria — combined, EPSG:4326

A single WGS 84 (longitude/latitude) dataset built from the two NGSA 1:2,000,000
sheets in this repository:

| Source | Sheet | Contribution |
|---|---|---|
| `Geological_Map_of_Nigeria.pdf` | NGSA Geological Map of Nigeria, 1:2,000,000, 2011 edition (DG Prof. Siyan Malomo) | 92 legend rows / 87 codes (1,518 polygons), boundaries, faults, fold axes, volcanic plugs, rivers, roads, railway, towns |
| `Mineral_Resources_Map_of_Nigeria_2023.pdf` | NGSA Mineral Resources Map of Nigeria, 1:2,000,000, 2nd edition 2023 (DG Dr Abdulrazaq Garba) | 999 mineral localities, 80 commodities in 8 groups, pegmatite marks, international boundary |

**Deliverables**

| File | What it is |
|---|---|
| `Nigeria_Geology_Minerals_4326.gpkg` | GeoPackage, 26 layers, 13,388 features, all EPSG:4326 — this is the deliverable |
| `Nigeria_Geology_Minerals_4326.png` / `.pdf` | rendered map |
| `build_combined.py` | rebuilds the GeoPackage |
| `render_combined.py` | rebuilds the image/PDF |
| `metadata.json` | provenance record |
| `accuracy_audit.md` | measured error budget: why ±10 km, what can and cannot be improved |
| `anchor_to_icons.py` | rebuilds the icon-anchored positions, the UTM layer and `icon_anchoring_report.json` |
| `refine_localities.py` | previous policy, kept for comparison |
| `fetch_source.py` | pulls the pinned source extraction (see provenance below) |
| `build_geology_final.py` | **builds the single geology layer**: resolves the overlaps from the printed ink, clips to the 2023 border, fills every inland gap; writes `geology_units`, `national_territory` and `geology_final_report.json` |
| `build_clean_geology.py` | superseded by `build_geology_final.py`; kept because it produced the `overlap_resolution.json` evidence for the ink test |
| `finalize_layers.py` | adds stable IDs, lon/lat, flags, the equal-area layers, **re-links every point to the shipped geology** and measures how much of each layer is inside Nigeria; writes `crs_qa_report.json` |
| `audit_layers.py` | **verifies all 26 layers** and writes `layer_audit.json`: geometry validity, CRS, duplicates, in-country share, area agreement, border flushness, point→unit joins |
| `locality_reassignments.csv` | the 49 locality moves, for review |

---

## Where the content comes from

Nothing in `maps/` was digitised by hand, and the geometry was **not** extracted in this
repository. The chain is:

| step | who / what | artefact |
|---|---|---|
| 1. source drawings | NGSA. `Geological_Map_of_Nigeria.pdf` (2011) and `Mineral_Resources_Map_of_Nigeria_2023.pdf` (2023) — layered vector exports from ArcMap with **no attribute tables** | the two PDFs in the repo root |
| 2. geometry extraction | done once in the sibling repo `MaxiKen/site` (pinned commit `138e961`): every vector path in the two PDFs sorted into layers, the affine fitted to each printed graticule, unit codes/ages rebuilt from layer names, the legend and in-polygon labels | `nigeria_maps.gpkg`, 40+ layers, 21 MB |
| 3. assembly (here) | `build_combined.py` selects/simplifies those layers, validates geometry, dedups polygons, re-joins localities to their host unit, corrects the mineral QA graticule | `Nigeria_Geology_Minerals_4326.gpkg`, 18 base layers |
| 4. point refinement (here) | `refine_localities.py`, then `anchor_to_icons.py` — move each locality onto the centre of its printed icon | +4 derived layers |
| 5. render (here) | `render_combined.py` | PNG + PDF |

**Step 2 is the one that matters, and it is external.** `fetch_source.py` pulls the exact
file used, pinned to a commit and verified by SHA-256, so the build is reproducible without
versioning a 21 MB intermediate:

```bash
python fetch_source.py          # clone MaxiKen/site @ 138e961, verify sha256, copy nigeria_maps.gpkg
python build_combined.py        # 18 base layers, with the raw geology (1,518 polygons)
python build_geology_final.py   # THE geology layer: no overlaps, no gaps, 2023 border
python refine_localities.py     # + refined + UTM layers
python anchor_to_icons.py       # + icon-anchored layers
python finalize_layers.py       # stable IDs, equal-area layers, crs_qa_report.json
python render_combined.py       # PNG/PDF
python audit_layers.py          # verify all 26 layers -> layer_audit.json
```

`build_geology_final.py` must run **after** `build_combined.py` and **before** `finalize_layers.py`:
it consumes the raw geology and rebuilds the derived layers. It refuses to run twice on its own
output, so start from `build_combined.py` when re-running it.

`build_combined.py` accepts `--source` (or `MAPS_SOURCE`) if the extraction lives elsewhere.

What is *this* repo's contribution to the coordinates: the verification that the extraction's
registration is right (graticule residual 130 m, area +0.1 %, national border 0.1 km from the
geology coverage edge), the correction of the one mislabelled QA table, and the point-accuracy
work (`accuracy_audit.md`) — not the original digitisation.


### One geology layer: no overlaps, no inland gaps, 2023 boundary

The file used to ship two geology layers — the raw 2011 export and a cleaned copy. It now ships
**one**: `geology_units`, produced by `build_geology_final.py`. The raw export is gone; it can be
regenerated with `build_combined.py` whenever the pipeline needs to be re-run from source.

**Overlaps are resolved by the sheet's own paint order.** A PDF draws its paths one after
another, each over what is already on the page, so an overlap is not ambiguous: the later path is
what you see. The extraction preserved that order for all 1,518 paths (`src_seq`), so the layer is
built by replaying it — each polygon loses exactly the part covered by any polygon drawn after it.
That is the faithful model of the drawing, and unlike a colour test it cannot be fooled by the
black label text printed on top of a unit.

Verified against the ink: sampling inside every surviving polygon and comparing with the colour the
sheet paints there, **1,426 of 1,462 polygons agree (97.5 %)**; the 36 that do not are small shapes
where the sample lands on a contact line or an adjacent unit's hatching. The result is exact —
residual overlap **0.002 km²** in the layer's own CRS, from round-off at shared edges.

**Gaps.** Inside the territory there were 7,250 km² of ground with no unit at all, in 1,577
pieces: Lake Chad (5,671 km², which the sheet prints blue) plus 1,576 slivers, none larger than
6.3 km². All of it is now assigned. A gap lying in a lake or reservoir drawn on the sheet becomes
`W` / "Water body"; every other gap joins the neighbour it shares the longest boundary with —
growth from the edge, not a nearest-centroid guess. Each row records `mapped_km2`, `filled_km2`
and a `filled` flag, so a calculation can drop the assigned slivers if it wants only directly
digitised ground.

**Result**

| | raw 2011 export | `geology_units` (shipped) |
|---|---|---|
| rows / units | 1,518 / 92 dissolved | **97** (96 rock units + water) |
| overlap between polygons | 9,582 km² | **0.002 km²** (round-off at shared edges) |
| uncovered ground inside the territory | 7,250 km² | **0.000 km²** |
| area drawn outside the territory | 3,764 km² past the 2023 border | **0** |
| summed `area_km2` | 912,520 km² | **907,157 km²** = the territory exactly |

Verified on the shipped file: 97 rows, 0 invalid or empty geometries, no duplicate geometries,
`geology_units`, `geology_units_equal_area` and the geodesic computation all give 907,157 km².

**The unit count went 92 → 96 because five codes are printed twice.** The legend has 92 rows but
only 87 distinct codes: `Esh`, `MS`, `MyP`, `Ncsh` and `Wss` each appear on two rows, and each row
is a different rock. Dissolving by code alone merged those pairs, and the surviving attributes came
from whichever polygon happened to come first — so 8,739 km² of *Blackshale, siltstone and
sandstone* was published as *Shale and limestone*, and 8,551 km² of *Sand, Clay and Mangrove
Swamps* as *Pelitic Schist*. Each polygon is now resolved against the legend row it carries; the
lower row keeps the printed code, the other becomes `CODE_<row>` (`Esh_43`, `MS_78`, `MyP_54`,
`Ncsh_23`, `Wss_31`). `attr_source` says whether a unit's attributes come from the legend or from
an in-map label.

**Every printed unit now has area.** Three used to come out empty, and the cause was the overlap
rule, not the drawing: `BIF` (26 km² of banded iron formation) is painted *before* the blue `Sp`
schist that surrounds it, so an ink test at its centre reads blue and gave it away; the paint order
restores it. `Ts` and the unlettered `BCT` are printed underneath `Qs` and a neighbouring unit
respectively, and the sheet shows those; they stay empty and are listed in
`geology_final_report.json`.

**Two printed codes resolve to existing legend rows**, and both are recorded in
`build_combined.py`:

* `Glls` → `GIls`. The map prints **`GIls`** in two places and **`Glls`** in one — a capital I read
  as a lowercase l. Its colour `#63f287` is exactly the swatch of legend row 30, `GIls` "Limestone",
  whose bracket names the Dukamaje Formation: the Cretaceous limestone of the Sokoto basin, which is
  where the polygon sits. Row 30 previously had no polygon at all.
* `OGe` → `OGp`. Identical rock description, identical printed colour (`#ff7a7f`) and identical
  era: one unit whose label was read two ways. 84,000 km² of granite, merged back together.

**Five units are missing from the sheet's own legend.** The map prints `OGp`, `Gdss`, `Gmsh`, `LCM`
and a bare `S` inside its polygons but the legend has no row for them — an omission on the printed
sheet, not in the extraction. They are kept (they are real, mapped ground, 88,000 km² together) and
flagged `attr_source = "in-map label"` (4) or `"printed label only"` (the bare `S` and `BCT`, 675
km²), so a calculation can treat their attributes as printed labels rather than legend definitions.

**Reaching the boundary.** The 2011 sheet only covers 899,907 km² of the 2023 territory, so
clipping alone would have left a 7,250 km² margin along the border and around Lake Chad. All of it
is filled, and the layer is flush with the line: **every one of the 3,500 vertices of the 2023 land
border sits within 7.5 m of the geology**, and the build aborts if any vertex is more than 50 m
away. Along the coast the edge is the Natural Earth coastline, because the 2023 layer stops at the
shore and has no sea edge.

### Which border to publish

Three candidates exist in the data, and they are not equivalent:

| candidate | vertices | agreement with Natural Earth 10m (median / p90 / max) |
|---|---|---|
| `international_boundary` (2023 sheet) | 3,500 | **1.2 km / 3.1 km / 12.2 km** |
| 2011 coverage edge (union of geology polygons) | 7,258 | 1.4 km / 5.2 km / **53.1 km** |
| Natural Earth 10m admin-0 Nigeria | 1,772 | — (reference) |

**Retain the 2023 `international_boundary`.** Reasons, measured:

* it is a *dedicated boundary layer*, whereas the 2011 "edge" is a by-product of polygon union
  that carries **803 interior hole rings** and offshore excursions — 15 % of its outline sits
  more than 50 km from the 2023 border (65 % of those points are along the coast, worst case
  338 km), so it is not a national boundary at all;
* across **Lake Chad** — the only place the two sheets disagree seriously — the 2023 line tracks
  Natural Earth to a median 1.7 km, while the 2011 edge is 31–53 km away;
* it is the newer compilation and its shape agrees with the internationally used dataset to
  3.1 km at p90.

**What the file actually uses.** The 2023 layer is the **land border only** — an open line from
(2.70°E, 6.37°N) to (8.52°E, 4.74°N) that cannot close into a polygon on its own. So the territory
polygon is a splice, stored as `national_territory`: 3,906 km of reference land edge replaced,
vertex for vertex, by the 2023 line; 2,056 km of Natural Earth coastline kept; the two junctions
snapped by 0.5 km and 1.5 km. That polygon is 907,157 km² and `geology_units` is cut on it, so the
layer's edge *is* the 2023 border everywhere the border exists. The raw 2023 line remains in
`international_boundary`; the 2011 coverage edge is no longer used for anything.

Two caveats:

1. For a web country polygon, use **Natural Earth 10m** (public domain, no attribution burden — it
   is within 3.1 km at p90 of the 2023 line) or an OSM-derived boundary if you need delta detail
   (ODbL).
2. Neither NGSA line is authoritative for a legal or diplomatic purpose; the Nigeria–Cameroon
   boundary in the Lake Chad area in particular is treaty-defined and should be taken from an
   official gazette or the ICJ ruling, not from a 1:2,000,000 map.


---

## Using these layers for calculation

**Every layer is EPSG:4326 except the five explicitly projected copies.** All geometries are
valid, all have a CRS, no null or empty geometries, and `lon`/`lat` fields are asserted equal
to the geometry. Verified on the current build:

| layer | CRS | features |
|---|---|---|
| the 21 EPSG:4326 layers | EPSG:4326 | 10,205 |
| `mineral_localities_utm32n`, `mineral_localities_icons_utm32n`, `geology_units_utm32n` | EPSG:32632 | 999 / 999 / 97 |
| `mineral_localities_equal_area`, `geology_units_equal_area` | EPSG:6933 | 999 / 97 |

### Pick the CRS for what you are measuring

| task | use | why |
|---|---|---|
| storage, exchange, web maps | **EPSG:4326** | degrees; **never compute area in it** — the result is square degrees |
| area, coverage, density | **EPSG:6933** (`*_equal_area` layers) | exact: 0.000 % error against the geodesic area |
| length / nearest-neighbour, countrywide | geodesic metres (`pyproj.Geod` on the 4326 layer) | no projection error anywhere |
| length / nearest-neighbour, local | EPSG:32631 / 32632 / 32633 **by zone** | Nigeria spans zones 31N (2.7–6°E), 32N (6–12°E) and 33N (12–15°E); the provided UTM 32N layer is 0.19 % off in area and worse in length at the east/west edges |
| never | EPSG:3857 | +3.68 % area error over Nigeria (940,568 vs 907,157 km²) |

Measured on this build, for the mapped coverage:

| CRS | area | error |
|---|---|---|
| geodesic (truth) | 907,157 km² | — |
| EPSG:6933 | 907,157 km² | +0.000 % |
| ESRI:102022 (Africa Albers) | 907,157 km² | +0.000 % |
| EPSG:32632 | 908,907 km² | +0.193 % |
| EPSG:3857 | 940,568 km² | +3.683 % |

### Fields you can rely on

* `locality_id` — **unique key for all 999 rows.** Do not key on `zone`+`number`: 39 printed
  numbers are shared by two records (78 rows), flagged by `shared_number`.
* `lon` / `lat` — decimal degrees, identical to the geometry.
* `dist_to_coast_m` — 0 for the 996 localities inside the mapped landmass; 3 points lie
  1.7–8.6 km offshore (islands/creek settlements) and are flagged here rather than dropped.
* `host_code`, `host_boundary_dist_m` — host unit at the point, and its distance to that
  unit's boundary (useful to exclude points sitting on a contact).
* `n_icons`, `icon_tier`, `pos_method` — how the position was derived (see accuracy_audit.md).

### Three things to watch

1. **`geology_units` is already dissolved.** It has one row per unit (97 rows, up to 46 polygon
   parts each), with no overlaps and no gaps, so `sum(area_km2)` is a valid total and per-unit
   areas need no further dissolve. Analysing points against it needs no dedupe either — every
   point falls in exactly one unit.
2. **Not all of it is directly digitised.** `filled_km2` is 0 for 18 units and non-zero for 78;
   7,250 km² of the 907,157 km² is assigned rather than drawn (5,671 of that is Lake Chad, printed
   as water on the sheet). Filter on `filled_km2 == 0` if a statistic must exclude it.
3. **The border appears in three layers for three purposes.** `national_territory` is the polygon
   the geology is cut on, `international_boundary` is the raw 2023 land border line, and
   `geology_units`'s own outer edge coincides with the land border by construction. Use
   `national_territory` for a country polygon.


---

## How the coordinates were obtained

Neither PDF is usable as a georeferenced file out of the box, so **both sheets are registered the
same way: by fitting an affine transform to their printed 1° graticule.**

| | Geology sheet | Mineral sheet |
|---|---|---|
| Page | 3168 × 1764 pt | 3960 × 2160 pt |
| Map frame | 1981 × 1621 pt | 1977 × 1609 pt |
| pt per degree lon / lat | 157.593 / 157.586 | 157.288 / 157.602 |
| Grid squareness | 1.0000 | 0.998 |
| Implied scale | 1:2,002,000 | 1:2,006,000 |
| Graticule fit residual | 0.20 pt (≈140 m) | 0.24 pt (≈170 m) |
| Forward transform | `x = −276.36 + 157.593·lon`<br>`y = 2281.63 − 157.586·lat` | `x = −288.67 + 157.288·lon`<br>`y = 2575.87 − 157.602·lat` |

Equal spacing in both axes at 157.6 pt/degree is exactly what an **unprojected** WGS 84 data
frame at 1:2,000,000 produces, so the drawn geometry is already in lon/lat — no reprojection
from a projected CRS is needed. The datum is taken as WGS 84; on the Minna datum the shift is
100–200 m, well below drawing resolution.

**Do not use the mineral sheet's embedded GeoPDF `/Measure` dictionary.** It is internally
inconsistent: it maps the 1977 pt frame to 10.21° of longitude (193.6 pt/°) and 1609 pt to 12.55°
of latitude (128.3 pt/°). That would stretch the sheet 1.23× horizontally and squash it 0.81×
vertically — Lagos would move ~370 km west of where the sheet's own graticule puts it. The
graticule fit above supersedes it.

### Verification

- **Area:** geology polygons total 924,900 km² against Nigeria's official 923,768 km² (+0.1 %).
  Their union covers 97.8 % of the country, the remainder being the narrow coastal/border fringe.
- **Internal consistency:** independent graticule-line extraction (12 meridians / 10 parallels)
  reproduces the label fit to <0.01 pt.
- **Town positions** (only 3 names are unique enough to check against modern coordinates) agree
  to ~10 km; the same offset appears in both sheets, so it is the source drawing's generalization,
  not a registration error.

---

## What the layers contain

**26 layers, 13,400 features, all verified by `audit_layers.py`** (result in `layer_audit.json`).
The table gives the count, CRS and geometry, what the layer is, and how much of it is inside
Nigeria. "inside" matters: the 2011 sheet draws neighbouring-country context, so the base layers
are not all Nigerian — that is now measured per feature, not assumed.

### Geology

| layer | n | CRS | geometry | what it is | inside Nigeria |
|---|---|---|---|---|---|
| `geology_units` | 97 | 4326 | MultiPolygon | **the only geology layer.** 96 rock units + `W` water. Valid, non-overlapping, no inland gap, cut on `national_territory`. Attributes: `code`, `unit`, `leg_desc`, `legend_row`, `attr_source`, `eon`/`era`/`period`/`epoch`, `age_ma_min`/`age_ma_max`, `rock_cls`, `formation`, `draw_order`, `area_km2`, `mapped_km2`, `filled_km2`, `filled`, `fill_source`, `fill`, `note` | 100 % |
| `geology_units_utm32n` | 97 | 32632 | MultiPolygon | same, on UTM 32N. Areas here are **+0.19 %** — use it for local distance, not for area | 100 % |
| `geology_units_equal_area` | 97 | 6933 | MultiPolygon | same, on EPSG:6933. `area_km2_equal_area` is exact (0.000 % vs geodesic) — **use this for area statistics** | 100 % |
| `geology_boundaries` | 2,819 | 4326 | LineString | contacts between units: exact / approximate / inferred / transitional in `class` | 99.9 % of 82,407 km |
| `faults` | 648 | 4326 | LineString | major and inferred fractures (`class`) | 99.8 % of 17,820 km |
| `fold_axes` | 90 | 4326 | LineString | anticlinal and synclinal axes | 94.4 % |
| `volcanic_plugs` | 68 | 4326 | Point | plugs and necks, with the host unit attached | 68/68 |
| `younger_granite_outlines` | 59 | 4326 | LineString | Jos Plateau ring-complex outlines. **Outlines, not closed rings** — 18 of 59 return to their start point, the rest do not, so do not treat them as polygons | 100 % |

### Water

| layer | n | CRS | geometry | what it is | inside Nigeria |
|---|---|---|---|---|---|
| `water_bodies` | 4 | 4326 | MultiPolygon | `kind` = `sea`, `lake` (Chad), `river`, `lake / reservoir`. **Read `note` and `printed_polygon` before using it**: `river` is a corridor enclosing the Niger–Benue channels, not water printed as a polygon; `sea` is the sheet's sea area. Only `lake` and `lake / reservoir` are water drawn as polygons, and only those were used to fill gaps in the geology | 9.2 % — by design, this is sea plus cross-border water |
| `rivers` | 1,054 | 4326 | LineString | river centrelines | 83.1 % of 40,482 km |
| `national_territory` | 1 | 4326 | Polygon | the clip polygon: 2023 land border + Natural Earth 10m coastline, 907,157 km². `land_edge`, `sea_edge`, `border_layer`, `area_km2` record the construction | 100 % |
| `international_boundary` | 1 | 4326 | LineString | the 2023 boundary as printed: 4,166 km, 3,500 vertices, **open** (2.70°E 6.37°N → 8.52°E 4.74°N). Land border only | 100 % |

### Minerals

| layer | n | CRS | geometry | what it is | inside Nigeria |
|---|---|---|---|---|---|
| `mineral_localities_icons` | 999 | 4326 | Point | **use this one for the 999 localities.** Position = centre of the printed mineral icon where one exists (842), otherwise the printed label. `locality_id` is the unique key; `n_icons`, `icon_tier`, `icon_spread_m`, `pos_method`, `moved_from_label_m`, `host_code`, `host_boundary_dist_m`, `group_centroid_lon/lat`, `shared_number` | 995/999 |
| `mineral_localities_icons_utm32n` | 999 | 32632 | Point | the same positions, metres | 995/999 |
| `mineral_localities_equal_area` | 999 | 6933 | Point | the same positions, equal-area | 995/999 |
| `mineral_localities` | 999 | 4326 | Point | the localities before icon anchoring, with the full source vocabulary (`symbol`, `sym_colour`, `min_conf`, `pos_src`, `label_lon/lat`, `groups`) | 991/999 |
| `mineral_localities_refined` | 999 | 4326 | Point | the previous positioning policy, kept for comparison | 992/999 |
| `mineral_localities_utm32n` | 999 | 32632 | Point | the same | 991/999 |
| `mineral_symbols` | 1,609 | 4326 | Point | every printed mineral symbol, with commodity, colour and how it was identified (`ident_mth`, `ident_scr`) | 1,603/1,609 |

### Settlements, transport, QA

| layer | n | CRS | geometry | what it is | inside Nigeria |
|---|---|---|---|---|---|
| `towns` | 486 | 4326 | Point | towns; 82 unnamed, 23 are in neighbouring countries (`in_nigeria = False`, unit fields null) | 463/486 |
| `state_capitals` | 32 | 4326 | Point | label-centre approximations, ±15 km | 32/32 |
| `state_boundaries` | 83 | 4326 | LineString | state lines; `km_in_nigeria`, `frac_in_nigeria` per feature | 92.3 % of 36,043 km |
| `roads` | 122 | 4326 | LineString | trunk roads | 92.6 % |
| `railway` | 6 | 4326 | LineString | | 100 % |
| `graticule_geology` | 22 | 4326 | LineString | the graticule fitted to the 2011 sheet — QA only | 66.5 % (it runs past the corners; that is the point) |
| `graticule_minerals` | 11 | 4326 | LineString | the graticule fitted to the 2023 sheet, with the +0.172° longitude label offset removed — QA only | 63.6 % |

**`ocg_id` is not a unique key.** It identifies the object on the source sheet, and one printed line
can be exported as several fragments (1,054 river fragments from a single source layer, 2,819
boundary fragments from 4). Use `locality_id` for the localities, `code` for the geology, and the row order
otherwise. `layer_audit.json` records the fragment count per layer.

### Cross-layer checks (all passing)

| check | result |
|---|---|
| overlap between geology polygons | **0.002 km²**, measured in EPSG:4326 |
| uncovered ground inside the territory | **0.000 km²** |
| geology drawn outside the territory | **0.000 km²** |
| area: `area_km2` sum vs EPSG:6933 vs geodesic | 907,157.0 / 907,157.0 / 907,156.9 km² — **0.000 %** |
| 2023 border vertices on the geology edge | 3,500, worst **7.5 m** |
| codes in 4326 / 32632 / 6933 copies | identical sets |
| invalid / empty / null geometries | **0** in all 26 layers |
| duplicate geometries | only in point layers, and deliberate (see below) |
| point → unit joins | 0 mismatches in all 6 layers that carry one |

**The overlap number is measured in the layer's own CRS, deliberately.** Reprojecting each polygon
*separately* to EPSG:6933 moves shared edges by a few millimetres, so a 6933-only measurement
invents slivers that are not in the data and overstates the overlap by four orders of magnitude
(0.002 km² → 2 km²). Pairs that genuinely overlap in EPSG:4326 are what is counted; their area is
then reported in km². Rebuilding also taught the same lesson the hard way: a "cut the slivers
first" pass removed **1,877 km² of coverage** while reporting 0.0016 km² of overlap, because it
deleted the reprojection artefacts instead of the data.

**The duplicate point geometries are real.** 15 localities share a position with another locality,
29 rows in 14 positions — two printed symbols side by side can be close enough that the icon
centres coincide, and a few localities print one number over several icons. They are distinct
records (`locality_id` unique), not duplicates to be dropped; the 46 duplicates in
`mineral_localities` are the same effect at the un-anchored positions.

Localities sit on a mapped unit 995/999 times; the other 4 are 1.7–4.7 km offshore or outside the
drawn polygon and are flagged by `host_dist_m > 0`. Host codes agree with the 2023 sheet's own
reading for 93.5 % of localities — the remaining 6.5 % are points that fall in a different
polygon after the duplicates/overlaps were cleaned, and the geometry here is the authority.

---

## Caveats

1. **Attributes do not exist in the source PDFs.** Both sheets are drawing exports with no feature
   tables. Unit codes, stratigraphy, ages and mineral names were reconstructed from layer names,
   the printed legend, correlation chart and in-polygon labels. Spot-check before relying on any code.
2. **Positional accuracy is not uniform** — see `accuracy_audit.md`. Registration is 0.13 km and
   reprojection is exact, so all the error is in the sheet's own ink. **842 of 999 localities
   (84.3 %) now sit exactly on the centre of a printed mineral icon**, assigned by commodity
   identity, recorded colour or inferred colour and back-tested at 97.4 % correct: those carry
   **±0.7 km**. The remaining 179 are located by their printed number only and carry **±10 km**,
   because the sheet prints nothing to anchor them to. Measured: 58 are commodities with no legend
   symbol at all (cassiterite, quartz, clay), 102 have a same-commodity symbol printed somewhere
   but at a median distance of **56 km**, and in the 15 cases where such a symbol is within 10 km,
   **it is already claimed by another locality** — so there is nothing left to anchor to. Pointing
   away from the label to a distant icon would be right only 4 % of the time; they stay on their
   printed numbers, and this is a limit of the sheet rather than of the processing.
3. **The two sheets disagree at the several-km level** on shared features (coastline median offset
   ~5 km, 90th percentile ~18 km; worst on the western Niger delta flank). They were compiled
   12 years apart and generalised independently. This dataset uses the **2011 sheet for all base
   geography** and the 2023 sheet only for mineral information, so no feature is duplicated from
   two vintages.
4. **Datum unrecorded.** WGS 84 assumed.
5. **`state_capitals` are label centres**, not surveyed points (±15 km).
6. **The geology is seamless, but 7,250 km² of it was assigned rather than drawn** — see
   "Three things to watch". Slivers of a few hundred metres were grown into the neighbouring unit;
   near a contact, a point that falls in such a sliver may belong to the unit on the other side.
7. **The base layers are not all Nigerian.** The 2011 sheet draws neighbouring-country rivers,
   roads, state lines and towns for context: 16.9 % of `rivers`, 7.6 % of `roads`, 7.7 % of
   `state_boundaries`, and 23 of 486 `towns` lie outside the border. They are kept (they are what
   the sheet shows) and flagged per feature — `frac_in_nigeria` on the lines, `in_nigeria` on the
   points. Filter on those rather than on your own clip.
8. **Five legend codes are printed twice** (`Esh`, `MS`, `MyP`, `Ncsh`, `Wss`), so the geology
   carries 92 rows for 87 codes: the five split units are published as `CODE` and `CODE_<row>`.
   If you join on a code list from somewhere else, expect those five to need mapping. Conversely
   **five printed units are absent from the sheet's legend** (`OGp`, `Gdss`, `Gmsh`, `LCM`, `S`),
   and two printed codes were normalised onto legend rows (`Glls`→`GIls`, `OGe`→`OGp`) — see the
   note above.
9. **Two printed units have no area** in the shipped geometry (`BCT`, `Ts`) — they are printed
   underneath `Qs` and a neighbouring unit, and the sheet shows that neighbour. `BCT` is not in the
   legend at all; `Ts` is (row 34). `BIF`, which used to be in this list, is back: the paint order
   gives it its 26 km².
10. **`graticule_geology` / `graticule_minerals` are QA layers**, not geography: they are the fitted
   graticule lines, which run past the map frame (33–36 % of their length is outside Nigeria).
    Do not include them in a country clip or an area total.
