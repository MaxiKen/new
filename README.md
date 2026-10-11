# NGSA geological map — v1 → v2

Three pictures, all on the same pixel frame so that grid cell **A1** means the same pixels in each:

| file | what it is |
|---|---|
| `NGSA_map_geology_legend_isolated.png` | **v1** — the "Isolated" picture (input) |
| `pic NGSA geological-map-of-nigeria-.jpg` | **NGSA** — the reference picture (input) |
| `NGSA_geology_isolated_v2.png` | **v2** — cleaned, geology-only rendering (main deliverable) |
| `NGSA_geology_isolated_v2_maponly.png` | v2, map area only, legend area filled with the no-data tone |
| `NGSA_geology_isolated_v2_fullyfilled.png` | v2, with the unmapped (no-data) area also flood-filled from the nearest geology |
| `NGSA_geology_isolated_v2_grid.png` | v2 with the A–L / 1–7 coordinate grid and cell IDs |
| `NGSA_isolated_v1_grid.png` | v1 with the same grid, for direct comparison |
| `pic_NGSA_grid.png` | NGSA **cropped to the identical frame** (dx +120, dy +96) with the same grid |
| `CELL_BY_CELL_REPORT.md` | cell-by-cell feature inventory + 8-neighbour connection log (84 cells) |
| `cell_inventory.csv` | the same inventory as a flat table |
| `work/` | the pipeline scripts |

## Key geometric finding

`NGSA_map_geology_legend_isolated.png` is **exactly** `pic NGSA geological-map-of-nigeria-.jpg`
cropped at **dx = +120, dy = +96** (scale 1:1). The map neatline is identical in both
(cols 19–4194, rows 91–3485). v1 is a lossless flat-colour rendering; the NGSA file is a
JPEG of the same rendering and carries the compression noise (549,571 distinct colours vs
v1's 176,798 and v2's 65 inside the map).

## What v2 does

1. **Exact colour census.** v1 is flat-shaded, so its true unit colours are recoverable
   exactly. 64 areal units were isolated from the line work, labels, graticule and
   anti-aliasing by a 7×7 uniformity ("core") test.
2. **Overlay removed, space filled.** 1,014,171 px (4.57 %) of non-geology overlay —
   graticule `rgb(76,76,76)`, label/road line work `rgb(224,224,150)`, black neatline and
   text — were removed and the space filled from the surrounding geology.
3. **Gaps closed.** 97,777 px of small interior white gaps were filled; 12,273 px of
   speckle (<300 px) removed.
4. **Nothing left blank.** Every remaining non-geology pixel gets the single no-data tone
   `rgb(232,229,223)` → **0.00 % pure white** in v2 (v1: 52.13 %).
5. **Boundaries smoothed** with two passes of a 3×3 categorical median on boundary pixels
   only — removes the pixel staircase on contacts without moving any interior pixel.

**Faithfulness check:** of the 8,525,635 px that were already flat unit colours in v1,
**99.985 % are preserved byte-identical** in v2. v2 changes 6.87 % of the canvas and virtually
all of that is overlay removal and gap filling. Structural agreement with the NGSA reference,
compared at ½ resolution to suppress JPEG noise, is **78.33 %**.

## Reading the cell atlas

Grid: **12 columns (A–L) × 7 rows (1–7)** = 84 cells of 522.3 × 505.7 px over the
6268 × 3540 canvas. For each cell the report lists the units present (colour, area, number of
discrete polygons, largest polygon) and then checks **all eight neighbours**:

* **aligned** — the unit is on both sides of the shared edge at the same place, with the
  length of the shared segment. That is the documented connection across the cell border.
* **offset** — the unit exists on both sides of the border but displaced; follow it into the
  named neighbour.
* **ends** — the unit reaches this cell's border but is absent from the neighbour, so the
  feature terminates there.
* **corner contact** — diagonal neighbours share no edge, so only the 16×16 px corner patch is
  compared.
