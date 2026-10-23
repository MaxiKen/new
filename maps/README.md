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
| `Nigeria_Geology_Minerals_4326.gpkg` | GeoPackage, 20 layers, all EPSG:4326 — this is the deliverable |
| `Nigeria_Geology_Minerals_4326.png` / `.pdf` | rendered map |
| `build_combined.py` | rebuilds the GeoPackage |
| `render_combined.py` | rebuilds the image/PDF |
| `metadata.json` | provenance record |
| `accuracy_audit.md` | measured error budget: why ±10 km, what can and cannot be improved |
| `anchor_to_icons.py` | rebuilds the icon-anchored positions, the UTM layer and `icon_anchoring_report.json` |
| `refine_localities.py` | previous policy, kept for comparison |
| `locality_reassignments.csv` | the 49 locality moves, for review |

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
| `geology_units` | 1,518 polygons | 92 codes / 97 lithologies. Attributes: `unit`, `code`, `leg_desc`, `formation`, `strat_grp`, `age_print`, `eon`/`era`/`period`/`epoch`, `age_ma_min`/`age_ma_max`, `rock_cls`, `basins`, `area_km2`, `fill` |
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
6. Small slivers and overlaps from the source remain (≈8,800 km² of overlap between adjacent units,
   mostly Alluvium and Bida-basin units); the polygons are valid but not topologically clean.
