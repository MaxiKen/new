# Geology and Mineral Resources of Nigeria — combined, EPSG:4326

A single WGS 84 (longitude/latitude) dataset built from the two NGSA 1:2,000,000
sheets in this repository:

| Source | Sheet | Contribution |
|---|---|---|
| `Geological_Map_of_Nigeria.pdf` | NGSA Geological Map of Nigeria, 1:2,000,000, 2011 edition (DG Prof. Siyan Malomo) | ~92 rock units (1,518 polygons), boundaries, faults, fold axes, volcanic plugs, rivers, roads, railway, towns |
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
| `finalize_layers.py` | adds stable IDs, lon/lat, flags and the equal-area layers; writes `crs_qa_report.json` |
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

**Overlaps.** The raw export carries 676 touching pairs sharing 9,582 km² (1.05 % of the summed
area), a third of it a unit overlapping *itself* (`Bss` under `Bss`, `Asl` under `Asl`) — an
extraction artefact from overlapping ring groups, not something the sheet draws. Every contested
region is now decided by the ink printed at its centre (78 of 608 touching pairs), with draw order
as the tie-break. Validated at the 18 largest different-unit overlaps: **16/18 carry the unit the
sheet prints** (draw order alone got 10/18).

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
| rows / units | 1,518 / 92 | **93** (92 units + water) |
| overlap between polygons | 9,582 km² | **0** (7 × 10⁻¹¹ deg², shared-edge round-off) |
| uncovered ground inside the territory | 9,773 km² | **0.000 km²** |
| area outside the territory | 3,764 km² drawn past the 2023 border | **0** |
| summed `area_km2` | 912,520 km² | **907,157 km²** = the territory exactly |

Verified on the shipped file: 93 rows, 0 invalid or empty geometries, no duplicate geometries,
`geology_units`, `geology_units_equal_area` and the geodesic computation all give 907,157 km².

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
| `mineral_localities_utm32n`, `mineral_localities_icons_utm32n`, `geology_units_utm32n` | EPSG:32632 | 999 / 999 / 93 |
| `mineral_localities_equal_area`, `geology_units_equal_area` | EPSG:6933 | 999 / 93 |

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

1. **`geology_units` is already dissolved.** It has one row per unit (93 rows, up to 46 polygon
   parts each), with no overlaps and no gaps, so `sum(area_km2)` is a valid total and per-unit
   areas need no further dissolve. Analysing points against it needs no dedupe either — every
   point falls in exactly one unit.
2. **Not all of it is directly digitised.** `filled_km2` is 0 for 33 units and non-zero for 60;
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

| Layer | Features | Notes |
|---|---|---|
| `geology_units` | 93 polygons | **the only geology layer.** 92 codes / 97 lithologies + `W` water. Attributes: `unit`, `code`, `leg_desc`, `formation`, `strat_grp`, `age_print`, `eon`/`era`/`period`/`epoch`, `age_ma_min`/`age_ma_max`, `rock_cls`, `draw_order`, `area_km2`, `mapped_km2`, `filled_km2`, `filled`, `fill_source`, `fill` |
| `geology_units_utm32n` / `geology_units_equal_area` | 93 each | the same layer on EPSG:32632 / EPSG:6933 |
| `national_territory` | 1 polygon | the clip: 2023 land border + Natural Earth coastline, 907,157 km². Attributes record which edge came from where |
| `mineral_localities` | 999 points | `locality`, `zone`, `number`, `mineral_1`, `group_1`, `minerals`, `n_minerals`, `symbol`, plus the **host rock re-joined from the geology polygons**: `host_unit`, `host_code`, `host_era`, `host_period`, `host_age_ma`, `host_dist_m` |
| `mineral_localities_icons` | 999 points | **use this one.** Every point is the centre of a printed mineral icon wherever one exists (842 points). Attributes: `n_icons`, `icon_tier`, `icon_spread_m`, `pos_method`, `moved_from_label_m`, `host_code`, `host_boundary_dist_m`, and `group_centroid_lon/lat` recording where the geometric centroid of a multi-icon group would fall |
| `mineral_localities_icons_utm32n` | 999 points | the same on EPSG:32632 |
| `mineral_localities_refined` | 999 points | previous policy (symbol where available, otherwise label) — kept for comparison |
| `mineral_localities_utm32n` | 999 points | the same points on WGS 84 / UTM zone 32N (EPSG:32632) for measuring in metres — reprojection is exact, so this changes nothing about accuracy |
| `mineral_symbols` | 1,609 points | every printed mineral symbol with its identified commodity and colour |
| `faults` | 648 | major + inferred fractures |
| `geology_boundaries` | 2,819 | exact / approximate / inferred / transitional |
| `fold_axes` | 90 | anticlinal + synclinal |
| `volcanic_plugs` | 68 | |
| `younger_granite_outlines` | 59 | Jos Plateau ring complexes |
| `rivers` / `water_bodies` | 1,054 / 4 | |
| `state_boundaries` / `international_boundary` | 83 / 1 | |
| `roads` / `railway` | 122 / 6 | |
| `towns` / `state_capitals` | 486 / 32 | capitals are label-centre approximations, ±15 km |
| `graticule_geology` / `graticule_minerals` | 22 / 11 | the fitted graticules, kept for QA |

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
   because the sheet prints nothing to anchor them to — 58 are commodities with no legend symbol
   (cassiterite, quartz) and 121 have one but not within the validated radius. Pointing those at a
   distant icon would be right only 4 % of the time, so they are left on their labels.
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
