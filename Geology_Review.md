# Geology layer review

*Nigeria geology and minerals atlas — review of every polygon layer in the repository, 30 October 2026.*

You said three things: the preview was still not okay, the layer should not be near a thousand
polygons, and I should keep checking the repository for the best layer. This is the answer to all
three, in the order you asked.

---

## 1. The preview, before anything else

The preview was wrong for two reasons, and neither of them was the data.

| what you saw | why | now |
|---|---|---|
| no polygons at all on the right-hand side of Compare | the unit layer shipped with its checkbox **off** (`state.layers.units.on = false`), and the page opened on the *minerals* sheet | the viewer opens on the 2011 geology sheet with the 97 units drawn |
| in Compare, a pale ghost instead of coloured rock | the replot was painted at **55% opacity** — correct over a printed sheet, wrong on the Compare side, which has no sheet under it | Compare paints the replot at full strength; that side is a colour comparison, so it shows the measured colour |
| the two Compare labels overprinted each other when the divider was dragged left | both labels were drawn on the same row | the second label steps down a row when there is no room |

**How this was checked.** All four modes (Explore, Compare, Compare dragged wide, deep zoom) were
rendered at 1280 × 800 and at 390 × 844, and each render was checked twice: by eye, and by counting
non-background pixels in each half of the canvas. Counting is what makes the check honest — a blank
pane cannot pass it. The Compare pane now carries 16,873 coloured samples at desktop size and 2,993
at phone size, against 0 before the fix.

**One limit, stated plainly.** The map itself was rendered headlessly and inspected. The HTML
controls around it (toolbar, drawer, inspector) were checked by reading the layout and measuring it
at 390 px wide — the toolbar's minimum width is 240 px against 390 px available, the comparison
label is capped at `100% − 24px` with ellipsis — but they could not be screenshotted in this
environment: the headless browser needs `libnss3` / `libnspr4`, which are not installed and cannot be
installed without root. Treat the phone layout as reviewed by measurement, not by photograph.

---

## 2. Every geology polygon layer in the repository

All of them were opened and counted, not just the one that ships.

| layer | file | polygons | verdict |
|---|---|---|---|
| **map units — shipped** | `Geology_Units.geojson` | **97** | **ships** |
| guard output | `Geology_Units_Repaired.geojson` | 97 | identical to the shipped layer after `--apply` |
| inside the package | `Nigeria_Geology_Minerals_4326.gpkg` → `geology_units` | 97 | same rows, equal-area areas |
| traced bodies | `data/geology/geology_bodies_retired.geojson` | 1,552 | **retired** — kept as evidence |
| upstream source | `data/ngsa/ngsa_geology_v6.gpkg` → `geology_bodies` | 1,588 | upstream, not shipped |
| pixel reading (repaired) | `Geology_Units_Repaired.geojson` (from the pixel build) | 5,539 → 97 | **retired** |
| early PDF-path reading | — | 1,142 | **retired** (had a page-sized `Qs` rectangle) |
| national outline | `Nigeria_Natural_Earth_outline.geojson` | 1 | not a geology layer |
| sheet rasters | `ref_geology_2011`, `combined_map` | 2480 × 2040 px | pictures, not polygons |

You were right that a layer should not be near a thousand. The traced set is 1,552, the pixel
reading 5,539, and neither is a geology layer — they are tracings of one. **The 97-unit layer is the
only one that matches the sheet's own legend, which has 97 rows.**

The body set and its report have been moved out of the repository root into
`data/geology/` and renamed `…_retired`, so that nothing at the top of the tree can be mistaken for
the layer that ships.

---

## 3. The shipped layer, measured

| | value |
|---|---|
| map units | **97** — 97 distinct codes |
| parts (an outcrop of a unit is a part) | **1,572** — 15 units are one piece, median 5, `OGp` 232 |
| area | **907,157 km²** |
| coverage of Nigeria (909,250 km²) | **99.65%**; the 3,205 km² not covered is the Cameroon border strip and a sliver of coast the sheet never colours |
| overlap | **0.03 km²** |
| enclosed ground unassigned | **0.02 km²** |
| median unit / median part | **3,078 km²** / **73 km²** |
| largest / smallest unit | `M` Migmatite 99,972 km² / `BCT` 4.5 km² |
| named from a legend row | **91 of 97** (94%) |
| flagged `name_confidence = low` | 6 — `OGp`, `W`, `Gdss`, `s`, `Gmsh`, `BCT`, 94,433 km² |

Package: `Nigeria_Geology_Minerals_4326.gpkg`, 16.5 MB, 13 layers, **35 of 35 validation checks
pass**. Projected package rebuilt. Maps 1–3 regenerated from the package.

### Why the 97-unit layer is the best one in the repository

It is not a matter of taste, and it is not a matter of count alone:

* **it is a partition** — 99.65% coverage, 0.03 km² of overlap, no unit drawn over another;
* **it is the legend** — one row per legend entry, so a code on the map means one thing, and 91 of
  97 names come from the sheet rather than from a guess;
* **it keeps real structure** — `OGp` is 232 separate outcrops because the Older Granite field
  really is scattered; the layer is 97 rows and 1,572 polygons, and welding those outcrops together
  would be a lie about the geology;
* **the traced alternatives fail on a property, not on style** — a traced body ends where a printed
  name, a road or a shear zone crosses it. Median body 69 km² against a median unit of 3,078 km²;
  78 of 97 codes instead of 97; 1,402 of 1,552 bodies can be named at all. A contact and a label
  look alike, so nothing downstream can use the edge of a "body" as a boundary.

---

## 4. What the audit found and fixed this round

These were real defects, each of them measured:

1. **Three units vanished on reprojection.** `Al`, `Bnst` and `Ajst` are valid in lon/lat but turn
   invalid when rotated into the equal-area frame; `make_valid` on the projected shape returned a
   collection with no polygons in it, silently dropping ~94,000 km². Every geometry is now repaired
   with `buffer(0)` first, which fixes exactly this case with no measurable change in area.
2. **Coordinate rounding re-broke rings on write.** GeoJSON rounds coordinates on the way out, and
   thin rings that were valid in memory came back self-intersecting. Both scripts now read the
   written file back and repair what actually landed on disk: **0 invalid rings** in the shipped
   layer, measured after a round trip through the file.
3. **Hole-filling invented ground.** Filling "holes" against the national outline had added
   **97,000 km² of rock** in places the sheet never colours (offshore, the north-east corner).
   Only ground the units already enclose counts as a hole — now 0.02 km².
4. **Validation was pinned to a 1,000-row layer.** Two checks (`> 1000` named bodies, 100% coverage
   against the national outline) could only pass on the traced set; they were passing a layer, not
   testing a property. They now test what matters — every row named, coverage of the area the sheet
   actually maps — and the package passes 35 of 35.
5. **The layer under the build was not in the repository.** The 97-unit source lived only on a
   branch that is not checked out (`maps/Nigeria_Geology_Minerals_4326.gpkg` on `addition`). It is
   now vendored at `data/geology/geology_units_main.gpkg`, so the build no longer depends on which
   branch happens to be present.

---

## 5. What is still weak, said out loud

* **6 codes have no legend row** (`OGp`, `W`, `Gdss`, `s`, `Gmsh`, `BCT`, 94,433 km² — 10% of the
  area). `OGp` is the salmon Older Granite field and is named to series level; the others are named
  as printed. They are flagged `low` rather than guessed, and the map legend says so.
* **The sheet does not colour the whole country.** 3,205 km² of the Cameroon border strip and a
  sliver of coast have no unit because the printed sheet has none. The layer says so instead of
  inventing rock to fill it.
* **41 parts are under 0.5 km².** They are genuine specks in the source reading, not tracing debris,
  and are left in place rather than merged away.
* **The phone layout is measured, not photographed** — see the limit in section 1.

---

## 6. Files

| file | what it is |
|---|---|
| `Geology_Units.geojson` | the shipped layer, 97 rows |
| `data/geology/geology_units_main.gpkg` | the vendored source the build reads |
| `Build_Geology_Units.py` | builds the shipped layer from it; `Geology_Units_Report.json` is its output |
| `Geology_LifeSaver.py` | the audit and repair guard: `--check`, default, `--apply` |
| `Geology_Units_Comparison.png` | the same Sokoto window drawn three ways, with the numbers |
| `Plate_Units_Comparison.py` | draws that plate |
| `GEOPACKAGE_README.md` | the full method, layer by layer |
| `web/` | the viewer, served by `python3 serve_atlas.py` |
