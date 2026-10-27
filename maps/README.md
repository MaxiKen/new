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
| `Nigeria_Geology_Minerals_4326.gpkg` | GeoPackage, **31 vector layers, 60,555 features** plus **9 georeferenced raster layers** (30 MB of tiles), EPSG:4326 with five projected copies — this is the deliverable |
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
| `audit_layers.py` | **verifies all 31 feature layers, the 9 rasters and the file's own registers** and writes `layer_audit.json`: geometry validity, CRS, duplicates, in-country share, area agreement, border flushness, point→unit joins, dangling `gpkg_extensions`, orphan/undeclared spatial indexes, empty tile-matrix zoom levels, blank layer descriptions |
| `locality_reassignments.csv` | the 117 locality moves made by the (now superseded) icon-anchoring policy, for review |
| `find_sites.py` | detects every printed mineral glyph on the 2023 sheet at its native 75 dpi and writes `mineral_symbols_detected.gpkg` |
| `name_glyphs.py` / `name_the_437.py` | name those glyphs against the extraction's appearance reference; write `minerals_named.gpkg`, `minerals_named.csv` and `minerals_named.md` |
| `add_named_minerals.py` | folds `minerals_named` into the deliverable GeoPackage and refreshes `crs_qa_report.json` |
| `mineral_audit.md` | why the mineral positions were withdrawn, and the measurement of the rebuild |
| `minerals_named.md` | how each of the 1,323 glyphs was named, per-colour-family accuracy, and the totals that are *not* reliable |
| `REVIEW_2026-10-25.md` | an independent review of this dataset against the two source PDFs, and what it changed |
| `build_towns.py` | adds **`towns_geonames`** — the 45,415-place GeoNames gazetteer of Nigeria, with state, and the two accuracy checks against outside data |
| `towns_geonames.md` | that layer: provenance, licence, fields, the measured accuracy, and what it must not be used for |
| `towns_report.json` / `towns_geonames_qc.png` | its counts and checks, and the overlay it was checked against |
| `RASTER_VS_VECTOR.md` | **which of the nine scans should be polygons and which must stay rasters**, with the measurement behind each verdict |
| `read_legend_swatches.py` | reads the printed legend swatches off each sheet — the colour-to-class mapping was transcribed by eye and was up to dE 100 wrong |
| `build_vector_layers.py` | writes `poly_soil_ph`, `poly_population` (traced from the sheets, ink seams repaired on the soil sheet only) and `geology_era` (dissolved from `geology_units`) |
| `check_polygon_colour.py` | tests every class polygon against the sheet it was traced from; writes `polygon_colour_check.json` |
| `describe_layers.py` | writes the `gpkg_contents` description of all 40 layers — what each is, its counts, and what it must not be used for |
| `fix_gpkg_hygiene.py` | repairs the GeoPackage's registers (dangling extensions, orphan and undeclared indexes, empty zoom levels); idempotent, records every change |
| `make_vector_qc.py` | redraws `vector_layers_qc.png`, including the ground the sheets leave blank |
| `normalise_nulls.py` | makes missing values NULL again — a read/write round trip through a GeoDataFrame turns them into `''` |
| `repair_layers.py` | the per-layer defects found by the deep audit, each one idempotent and recorded (`layer_repairs.json`) |
| `docs_check.py` | **tests every number in `LAYERS.md` against the GeoPackage** — 176 claims, and it exits non-zero if one is wrong |
| `vectorisation_study.py` | the purity / fragmentation / round-trip test each sheet passes or fails |
| `georef_new_map.py` | **georeferences the nine scans in `new map/`** into the GeoPackage as clipped RGBA raster layers, with a measured border offset per layer |
| `RASTER_LAYERS.md` | the nine raster layers: format decisions, legend transcriptions, measured positional error and what each must not be used for |
| `raster_georeferencing.json` / `raster_georeferencing_qc.png` | the fit record for every raster layer, and the overlay it was checked against |

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
python add_named_minerals.py    # + minerals_named, refresh crs_qa_report.json
python render_combined.py       # PNG/PDF (draws minerals_named, not the localities)
python normalise_nulls.py       # restore NULL where a rewrite left ''
python repair_layers.py         # the per-layer repairs (idempotent)
python describe_layers.py       # a description for every layer, inside the file
python fix_gpkg_hygiene.py      # registers: dangling extensions, indexes, zoom levels
python audit_layers.py          # verify all 31 layers + 9 rasters + the file's registers -> layer_audit.json
python docs_check.py            # test every number in LAYERS.md against the file
python check_idempotency.py     # run the repairs twice: the second run must change no row
python georef_new_map.py        # + the 9 raster layers (merges tiles, never rebuilds the vectors)
python build_towns.py           # + towns_geonames, the gazetteer (downloads ~450 MB once, caches it)
```

`georef_new_map.py` and `build_towns.py` are the two steps that are safe to run
against the finished GeoPackage: the first writes each raster into a scratch file
and merges the tiles, the second replaces only its own layer. Neither touches the
27 layers the sheet-by-sheet build produced (`geology_era`, `poly_soil_ph` and
`poly_population` come from `build_vector_layers.py`, `towns_geonames` from
`build_towns.py`; `describe_layers.py` and `fix_gpkg_hygiene.py` only touch
metadata and are safe on the finished file). Re-running them replaces the nine
raster layers and `towns_geonames` in place. See `RASTER_LAYERS.md` and
`towns_geonames.md`.

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

Verified against the ink: one sample inside every surviving polygon, compared with the colour the
sheet paints there, gives **1,426 of 1,462 polygons agreeing (97.5 %)**; the 36 that do not are small
shapes where the sample lands on a contact line or an adjacent unit's hatching. The result is exact —
residual overlap **0.002 km²** in the layer's own CRS, from round-off at shared edges.

### How faithful is the geology layer? (area-weighted check)

The 97.5 % above is **one sample per source polygon**, so it says a polygon's centre is usually the
right colour — not that 97.5 % of the *area* is. Sampling 2,257 random points strictly inside the
shipped polygons gives the area view:

| what the sheet paints at a random interior point | share |
|---|---|
| the unit's own colour | **66.8 %** |
| another unit's legend colour | 8.6 % |
| other printed colours (grey hatching, overlay marks, rivers) | 21.4 % |
| dark linework or text | 3.2 % |

Half of the misses are within 0.7 km (1 px) of the unit's own boundary and 73 % within 2 km, i.e.
contact lines and round-off. About **16 % of all samples are more than 2 km inside a unit and still
not its colour** — hatch patterns and the sheet's own overlays. So treat the layer as a faithful
*outline* of the printed map, not as ground truth at the sub-kilometre level; the 97.5 % figure should
not be read as an area claim.

**Gaps.** Inside the territory there were 7,250 km² of ground with no unit at all, in 1,573
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
restores it. `Ts` is printed underneath `Qs`, and the sheet shows `Qs`: the replay leaves it
no area, so it is **dropped** from the layer and recorded in `geology_final_report.json` →
`units_dropped_no_area`, with the reason. The unlettered `BCT` is a neighbour's label but it
survives with **4.5 km²** of its own, mapped ground.

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

**Reaching the boundary.** The 2011 sheet only covers 899,916 km² of the 2023 territory, so
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
| the 26 EPSG:4326 layers | EPSG:4326 | 57,364 |
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

* `age_ma_min` / `age_ma_max` — **float64, numeric.** `min` is the younger bound, `max` the older,
  so a unit spans `age_ma_min`–`age_ma_max` Ma. They were shipped as text until this build, which
  made `age_ma_min < 100` a string comparison (and every value here is 0–4000, so it was wrong).

* `locality_id` — **unique key for all 999 rows.** Do not key on `zone`+`number`: 39 printed
  numbers are shared by two records (78 rows), flagged by `shared_number`.
* `lon` / `lat` — decimal degrees, identical to the geometry.
* `dist_to_coast_m` — 0 for the 995 localities inside the mapped landmass; 4 points lie
  0.9–5.7 km offshore (islands/creek settlements) and are flagged here rather than dropped.
* `host_code`, `host_boundary_dist_m` — host unit at the point, and its distance to that
  unit's boundary (useful to exclude points sitting on a contact).
* `n_icons`, `icon_tier`, `pos_method` — how the position was derived (see accuracy_audit.md).

### Three things to watch

1. **`geology_units` is already dissolved.** It has one row per unit (97 rows, up to 234 polygon
   parts each), with no overlaps and no gaps, so `sum(area_km2)` is a valid total and per-unit
   areas need no further dissolve. Analysing points against it needs no dedupe either — every
   point falls in exactly one unit.
2. **Not all of it is directly digitised.** 7,250 km² of the 907,157 km² (0.8 %) was assigned
   rather than drawn — 5,671 km² of that is Lake Chad, printed as water on the sheet. `filled`
   (boolean) is True for the 75 units that received such ground and False for the 22 that are
   entirely digitised; `filled_km2` is the amount, 0 for those 22. **`filled_km2 == 0` therefore
   selects the fully digitised units, not the filled ones** — to exclude assigned ground, use the
   boolean `filled` or subtract `filled_km2` from `area_km2`.
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
- **The measurements the file ships describe the geometry it ships.** Every stored length, area,
  perimeter and fraction is recomputed from the geometry in `audit_layers.py`. That check found
  `km_in_nigeria` measured on the equal-area grid while `len_km` was geodesic — so in-Nigeria
  length came out *longer than the line itself* in 3,174 rows across six layers, with
  `frac_in_nigeria` clamped to hide it.
- **The text is text.** No value ends mid-word, no name carries padding or a double space, and no
  numeric column holds a sentinel instead of NULL — the 42 × `-9999` in `dem_m` were SRTM voids
  being read as elevations of -9,999 m.

---

## What the layers contain

**31 layers, 60,555 features, all verified by `audit_layers.py`** (26 layers in EPSG:4326 with
57,364 features, three in 32632, two in 6933) (result in `layer_audit.json`).
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

> **Status: the mineral point layers are withdrawn for calculation.** A 2026-10 audit of the printed
> symbols (`mineral_audit.md`) found the stored coordinates sit a median 9.6 km from any symbol on
> the sheet and carry no positional signal. `minerals_named` is the replacement for the printed-symbol
> layer: **1,323 symbols, point = measured centre of each glyph, ±0.35 km** (94.9 % within 1 px of
> the symbol ink, against 8.5 % for a random point); 1,305 are named and 18 are withheld. The
> locality layers below are queued for rebuild on top of it.
>
> **The shipped PNG/PDF draws `minerals_named`, not the localities** — the published map shows the
> positions that are valid.

| layer | n | CRS | geometry | what it is | inside Nigeria |
|---|---|---|---|---|---|
| `mineral_localities_icons` | 999 | 4326 | Point | **POSITIONS INVALID — see `mineral_audit.md`; queued for rebuild.** Position was intended to be the centre of the printed mineral icon where one exists (842), otherwise the printed label, but the source symbol coordinates are ~9.6 km noise, so the anchoring does not hold. `locality_id` is the unique key; `n_icons`, `icon_tier`, `icon_spread_m`, `pos_method`, `moved_from_label_m`, `host_code`, `host_boundary_dist_m`, `group_centroid_lon/lat`, `shared_number` | 995/999 |
| `mineral_localities_icons_utm32n` | 999 | 32632 | Point | the same positions, metres | 995/999 |
| `mineral_localities_equal_area` | 999 | 6933 | Point | the same positions, equal-area | 995/999 |
| `mineral_localities` | 999 | 4326 | Point | the localities before icon anchoring, with the full source vocabulary (`symbol`, `sym_colour`, `min_conf`, `pos_src`, `label_lon/lat`, `groups`) | 991/999 |
| `mineral_localities_refined` | 999 | 4326 | Point | the previous positioning policy, kept for comparison | 992/999 |
| `mineral_localities_utm32n` | 999 | 32632 | Point | **the EPSG:32632 copy of `mineral_localities_refined` (layer 21), not of layer 20** — the name is historic; the coordinates match layer 21 exactly and differ from layer 20 by up to 11.9 km in 117 rows | 992/999 |
| `mineral_symbols` | 1,609 | 4326 | Point | **POSITIONS INVALID — see `mineral_audit.md` and `mineral_symbols_detected.gpkg`.** the extraction's symbol rows, with commodity, colour and how it was identified (`ident_mth`, `ident_scr`); the attributes are usable, the geometry is not (median 9.6 km from any symbol). **Filter on `is_symbol = 1` before counting:** that leaves the **1,489** rows that are one countable printed symbol. The 120 others are 56 raster slivers, 21 state-capital squares, 8 linework/label fragments, 5 bridge or water markings, 5 merged clusters, 15 fragments and 8 halves of a symbol already counted, and 2 merged touching pairs — unfiltered they show up as a phantom commodity with 56 members | 1,603/1,609 |
| `minerals_named` | 1,323 | 4326 | Point | **the printed symbols, correctly placed.** Every glyph re-detected on the sheet at its native 75 dpi, each point the centroid of its symbol (±0.35 km). Named with the accuracy stated per row: `mineral`, `tier` (probable ≥70 % / tentative 50–70 % / unidentified), `family_accuracy_pct`, `mineral_class`, `details`, `in_nigeria`. **Use this for position; use `mineral_symbols.mineral` for counts — with `is_symbol = 1`.** 144 symbols are printed outside the border because the sheet maps the whole region (Niger, Benin, Cameroon) — `in_nigeria=False`, not an error | 1,179/1,323 |

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
| uncovered ground inside the territory | **0.000 km²** in EPSG:4326 (0.006 km² if each polygon is reprojected on its own — same artefact as the overlap row) |
| geology drawn outside the territory | **0.000 km²** in EPSG:4326 (0.001 km² reprojected separately) |
| area: `area_km2` sum vs EPSG:6933 vs geodesic | 907,157.0 / 907,157.0 / 907,156.9 km² — **0.000 %** |
| 2023 border vertices on the geology edge | 3,500, worst **7.5 m** |
| codes in 4326 / 32632 / 6933 copies | identical sets |
| invalid / empty / null geometries | **0** in all 31 layers |
| duplicate geometries | only in point layers, and deliberate (see below) |
| point → unit joins | 0 mismatches in all 6 layers that carry one |
| numeric fields stored as text | **none** — `age_ma_min` / `age_ma_max` are float64 |
| dangling `gpkg_extensions` rows / orphan rtree tables | **0 / 0** (16 dead rows and 7 dead indexes removed, 17 undeclared indexes declared, 29 empty zoom levels dropped) |
| layers without a description inside the file | **0** of 40 |
| hairline slits / duplicate vertices in polygon rings | **0 / 0** (35 + 14 removed from `geology_units`, 95 from `geology_era`) |
| sentinel values in numeric columns (`-9999`, `-99999`, `-32768`) | **0** |
| text values with padding, double spaces or control characters | **0** |
| values cut off at a fixed width | **0** |
| stored lengths / areas / perimeters reproduced from the geometry | **all** — `len_km` and `km_in_nigeria` geodesic, `area_km2` in EPSG:6933, `frac_in_nigeria` = ratio |
| field names in `LAYERS.md` field tables that the layer does not have | **0** of 63 |
| rows changed by running the repairs a second time | **0** in all 40 tables |

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

Localities sit on a mapped unit 995/999 times; the other 4 are 0.9–5.7 km offshore or outside the
drawn polygon and are flagged by `host_boundary_dist_m > 0`. (The host-code agreement figure that
used to be quoted here — 93.5 % — is **withdrawn** with the rest of the mineral positioning: it was
measured with the discredited coordinates. The join itself is verified against the shipped
geology: 0 mismatches in all six layers that carry one, in `layer_audit.json`.)

---

## Caveats

1. **Attributes do not exist in the source PDFs.** Both sheets are drawing exports with no feature
   tables. Unit codes, stratigraphy, ages and mineral names were reconstructed from layer names,
   the printed legend, correlation chart and in-polygon labels. Spot-check before relying on any code.
2. **The mineral point layers are withdrawn — do not use them for calculation.** A 2026-10 audit
   measured the stored symbol coordinates against the sheet itself and found them to carry no
   positional information: median **14.1 px (9.6 km)** from the nearest symbol ink, only 5.9 %
   within 1 px, and a nearest-neighbour distance distribution statistically indistinguishable
   from a random scatter of the same size. The earlier claim that 84.3 % of localities "sit
   exactly on the centre of a printed icon" (±0.7 km) was computed on those coordinates and is
   **withdrawn**. The cause is upstream: the transform stored with the extraction is 0.2 % out in
   longitude scale and 3.5 pt out in latitude offset versus the sheet's own graticule, and the
   per-symbol positions were never on the glyphs in the first place. See `mineral_audit.md`.
   `mineral_symbols_detected.gpkg` replaces the printed-symbol layer with 1,323 symbols whose
   points are the measured centre of each glyph (±0.5 px = ±0.35 km). The `mineral_localities*`
   layers (999 rows each) still rest on the discredited coordinates and are queued for rebuild.
   **The extraction's `mineral` column is sound as a count, but only after filtering** — 120 of its
   1,609 rows are slivers, symbol halves, linework and state-capital squares. Use
   `is_symbol = 1` (1,489 rows) before any `value_counts()`; see the mineral table above.
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
   roads, state lines and towns for context: 16.9 % of the `rivers` length, 7.4 % of `roads`,
   7.7 % of `state_boundaries`, and 23 of 486 `towns` lie outside the border. They are kept (they
   are what the sheet shows) and flagged per feature — `frac_in_nigeria` on the lines, `in_nigeria` on the
   points. Filter on those rather than on your own clip.
8. **Five legend codes are printed twice** (`Esh`, `MS`, `MyP`, `Ncsh`, `Wss`), so the geology
   carries 92 rows for 87 codes: the five split units are published as `CODE` and `CODE_<row>`.
   If you join on a code list from somewhere else, expect those five to need mapping. Conversely
   **five printed units are absent from the sheet's legend** (`OGp`, `Gdss`, `Gmsh`, `LCM`, `S`),
   and two printed codes were normalised onto legend rows (`Glls`→`GIls`, `OGe`→`OGp`) — see the
   note above.
9. **One printed unit has no area and is dropped** (`Ts`, legend row 34): it is printed underneath
   `Qs`, so the paint-order replay leaves it nothing, and it is recorded in
   `geology_final_report.json` → `units_dropped_no_area` rather than shipped as an empty row.
   `BCT` (not in the legend at all) survives with 4.5 km²; `BIF`, which used to be in this list, is
   back: the paint order gives it its 26 km².
10. **Five units carry no stratigraphy** — `Gdss` (4,194 km²), `s` (671), `P` (312), `Gmsh` (115)
   and `BCT` (4.5): 5,296 km², 0.6 % of the layer. Four are printed labels with no legend row and
   `P`'s legend row leaves the era blank, so `era`, `period`, `eon`, `epoch` and the ages are
   **NULL** for them rather than guessed. They are listed in `geology_final_report.json` →
   `units_without_era` and are drawn as their own entry in the image's "by era" legend, so an
   era-based aggregation can see what it is leaving out (896,190 km² of rock is classified by era,
   5,671 km² is water, and 5,296 km² is unknown).
   Missing values are always NULL, never `""` — `P`'s era used to be an empty string, which is why
   "which units have no era?" answered four. The same holds for `note` and `fill_source` (NULL, not
   `""`, for ground that was digitised rather than filled).
11. **`graticule_geology` / `graticule_minerals` are QA layers**, not geography: they are the fitted
   graticule lines, which run past the map frame (33–36 % of their length is outside Nigeria).
    Do not include them in a country clip or an area total.
