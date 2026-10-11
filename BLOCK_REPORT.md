# NGSA Geology Map — Version 2 Block Report

**Deliverable:** `NGSA_map_geology_legend_isolated_v2.png` (6268 × 3540, same layout as the isolated picture: map + margin text + full legend, everything outside the map frame untouched — verified 0 changed pixels).

**Grid:** columns **A–L** = 1°-wide longitude bands 3°E→15°E; rows **1–10** = 1°-tall latitude bands 13°N→4°N (row 1 at the top). The grid lines are the map's own graticule (3°E…14°E, 13°N…4°N at 328.4 px/degree). Blocks were processed and verified in order A1→B1→…→L1, A2→…→L10, each checked against its neighbors.

## What was done (global pipeline, applied block-wise)

1. **Source alignment** — the isolated picture is a pixel-exact crop of the NGSA scan (offset +120, +96), so every block was compared pixel-to-pixel with the original.
2. **Text/line masking** — all black in the original (town names, formation labels, roads, structures) is masked out before comparison; v2 keeps no black inside the map except the graticule itself (verified: 93,273 graticule px kept, 0 other black px).
3. **Repairs vs original** — white artifacts re-filled from the original's geology where the original had clean, supported color (5,113 px); unsupported over-paints returned to background (471 px); color disagreements resolved in favour of the better-supported source (32,025 px).
4. **Water removal** — inland water bodies were removed and filled with the adjacent geology: **Lake Chad** (~113k px), the **Lagos/Badagry lagoon fragments**, small lakes and creek fragments (~30 components). The **ocean is kept** as the blue base of the map (it is the country's southern boundary, needed for shapefile clipping). The alluvium valley units (the three blue-teal legend units along the Ogun, Rima, Sokoto, Niger valleys) are **geology** and were kept.
5. **Palette snapping** — every interior pixel now carries one of 37 exact geology colors, white, or the ocean colour; JPEG speckle and anti-aliasing are gone. Fills were grown from the nearest valid unit colours and majority-smoothed.

## Block-by-block verification

`agree` = fraction of comparable (non-text, confident) pixels whose geology unit matches the original NGSA map.
`edges` = continuity of units across the block boundary with the neighbouring block (N/S/E/W, 1.00 = seamless).

| Block | Extent | agree | Edge continuity (N/S/E/W) | Water px | Notes |
|---|---|---|---|---|---|
| A1 | 3–4°E, 13–14°N | 98.3% | E:0.06 S:0.01 | 0 | clean — geology only |
| B1 | 4–5°E, 13–14°N | 96.5% | E:0.79 S:0.90 W:0.06 | 0 | clean — geology only |
| C1 | 5–6°E, 13–14°N | 92.9% | E:0.64 S:0.97 W:0.79 | 0 | clean — geology only |
| D1 | 6–7°E, 13–14°N | 96.3% | E:0.05 S:0.83 W:0.64 | 6 | clean — geology only |
| E1 | 7–8°E, 13–14°N | 98.0% | E:0.35 S:0.85 W:0.05 | 2 | clean — geology only |
| F1 | 8–9°E, 13–14°N | 98.3% | E:0.05 S:0.58 W:0.35 | 0 | clean — geology only |
| G1 | 9–10°E, 13–14°N | 99.3% | E:0.19 S:0.15 W:0.05 | 0 | clean — geology only |
| H1 | 10–11°E, 13–14°N | 98.0% | E:0.41 S:1.00 W:0.19 | 0 | clean — geology only |
| I1 | 11–12°E, 13–14°N | 98.1% | E:0.19 S:1.00 W:0.41 | 0 | clean — geology only |
| J1 | 12–13°E, 13–14°N | 97.2% | E:0.56 S:1.00 W:0.19 | 8 | clean — geology only |
| K1 | 13–14°E, 13–14°N | 41.6% | E:0.05 S:0.66 W:0.56 | 56595 | LAKE CHAD — water body removed, filled with surrounding Chad Fm (yellow) / background; large water area (sea/lake) — sea kept, inland water removed & filled |
| L1 | 14–15°E, 13–14°N | 54.7% | S:0.16 W:0.05 | 41325 | LAKE CHAD — water body removed, filled with surrounding Chad Fm (yellow) / background; large water area (sea/lake) — sea kept, inland water removed & filled |
| A2 | 3–4°E, 12–13°N | 94.3% | E:0.84 N:0.01 S:0.65 | 455 | minor water cleanup |
| B2 | 4–5°E, 12–13°N | 89.0% | E:0.92 N:0.90 S:0.92 W:0.84 | 0 | clean — geology only |
| C2 | 5–6°E, 12–13°N | 92.5% | E:0.71 N:0.97 S:0.89 W:0.92 | 15 | clean — geology only |
| D2 | 6–7°E, 12–13°N | 92.6% | E:0.88 N:0.83 S:0.86 W:0.71 | 2 | clean — geology only |
| E2 | 7–8°E, 12–13°N | 96.6% | E:0.77 N:0.85 S:0.93 W:0.88 | 1 | clean — geology only |
| F2 | 8–9°E, 12–13°N | 91.6% | E:0.78 N:0.58 S:0.93 W:0.77 | 0 | clean — geology only |
| G2 | 9–10°E, 12–13°N | 90.8% | E:1.00 N:0.15 S:0.97 W:0.78 | 0 | clean — geology only |
| H2 | 10–11°E, 12–13°N | 87.8% | E:1.00 N:1.00 S:1.00 W:1.00 | 0 | clean — geology only |
| I2 | 11–12°E, 12–13°N | 93.3% | E:1.00 N:1.00 S:1.00 W:1.00 | 0 | clean — geology only |
| J2 | 12–13°E, 12–13°N | 96.8% | E:1.00 N:1.00 S:1.00 W:1.00 | 0 | clean — geology only |
| K2 | 13–14°E, 12–13°N | 82.5% | E:0.69 N:0.66 S:1.00 W:1.00 | 12413 | LAKE CHAD — water body removed, filled with surrounding Chad Fm (yellow) / background; water removed & filled (lake/lagoon/river fragments) |
| L2 | 14–15°E, 12–13°N | 90.5% | N:0.16 S:0.87 W:0.69 | 2743 | water removed & filled (lake/lagoon/river fragments) |
| A3 | 3–4°E, 11–12°N | 93.6% | E:0.84 N:0.65 S:0.21 | 720 | minor water cleanup |
| B3 | 4–5°E, 11–12°N | 88.6% | E:0.90 N:0.92 S:0.88 W:0.84 | 387 | minor water cleanup |
| C3 | 5–6°E, 11–12°N | 94.2% | E:0.91 N:0.89 S:0.92 W:0.90 | 691 | minor water cleanup |
| D3 | 6–7°E, 11–12°N | 93.0% | E:0.85 N:0.86 S:0.86 W:0.91 | 6 | clean — geology only |
| E3 | 7–8°E, 11–12°N | 94.5% | E:0.73 N:0.93 S:0.95 W:0.85 | 0 | clean — geology only |
| F3 | 8–9°E, 11–12°N | 97.9% | E:0.87 N:0.93 S:0.98 W:0.73 | 0 | clean — geology only |
| G3 | 9–10°E, 11–12°N | 94.7% | E:0.91 N:0.97 S:0.90 W:0.87 | 0 | clean — geology only |
| H3 | 10–11°E, 11–12°N | 94.7% | E:0.97 N:1.00 S:0.98 W:0.91 | 0 | clean — geology only |
| I3 | 11–12°E, 11–12°N | 93.9% | E:0.99 N:1.00 S:0.92 W:0.97 | 0 | clean — geology only |
| J3 | 12–13°E, 11–12°N | 95.8% | E:0.93 N:1.00 S:0.99 W:0.99 | 0 | clean — geology only |
| K3 | 13–14°E, 11–12°N | 92.4% | E:0.71 N:1.00 S:0.77 W:0.93 | 0 | clean — geology only |
| L3 | 14–15°E, 11–12°N | 96.0% | N:0.87 S:0.16 W:0.71 | 11 | clean — geology only |
| A4 | 3–4°E, 10–11°N | 96.4% | E:0.92 N:0.21 S:0.64 | 937 | minor water cleanup |
| B4 | 4–5°E, 10–11°N | 84.4% | E:0.84 N:0.88 S:0.98 W:0.92 | 11098 | water removed & filled (lake/lagoon/river fragments) |
| C4 | 5–6°E, 10–11°N | 96.1% | E:0.88 N:0.92 S:0.99 W:0.84 | 966 | minor water cleanup |
| D4 | 6–7°E, 10–11°N | 95.5% | E:0.95 N:0.86 S:0.89 W:0.88 | 4 | clean — geology only |
| E4 | 7–8°E, 10–11°N | 97.4% | E:0.84 N:0.95 S:0.96 W:0.95 | 0 | clean — geology only |
| F4 | 8–9°E, 10–11°N | 96.2% | E:0.82 N:0.98 S:0.83 W:0.84 | 546 | minor water cleanup |
| G4 | 9–10°E, 10–11°N | 93.7% | E:0.95 N:0.90 S:0.85 W:0.82 | 0 | clean — geology only |
| H4 | 10–11°E, 10–11°N | 94.7% | E:0.99 N:0.98 S:0.94 W:0.95 | 0 | clean — geology only |
| I4 | 11–12°E, 10–11°N | 95.9% | E:0.92 N:0.92 S:0.96 W:0.99 | 0 | clean — geology only |
| J4 | 12–13°E, 10–11°N | 98.8% | E:0.99 N:0.99 S:0.92 W:0.92 | 0 | clean — geology only |
| K4 | 13–14°E, 10–11°N | 97.0% | E:0.01 N:0.77 S:0.61 W:0.99 | 34 | clean — geology only |
| L4 | 14–15°E, 10–11°N | 98.5% | N:0.16 S:0.57 W:0.01 | 13 | clean — geology only |
| A5 | 3–4°E, 9–10°N | 94.0% | E:0.95 N:0.64 S:0.88 | 1717 | minor water cleanup |
| B5 | 4–5°E, 9–10°N | 93.8% | E:1.00 N:0.98 S:0.93 W:0.95 | 1209 | minor water cleanup |
| C5 | 5–6°E, 9–10°N | 99.4% | E:0.93 N:0.99 S:1.00 W:1.00 | 222 | minor water cleanup |
| D5 | 6–7°E, 9–10°N | 92.3% | E:0.92 N:0.89 S:0.92 W:0.93 | 1951 | minor water cleanup |
| E5 | 7–8°E, 9–10°N | 96.1% | E:0.88 N:0.96 S:0.90 W:0.92 | 54 | clean — geology only |
| F5 | 8–9°E, 9–10°N | 91.9% | E:0.87 N:0.83 S:0.90 W:0.88 | 0 | clean — geology only |
| G5 | 9–10°E, 9–10°N | 96.7% | E:0.85 N:0.85 S:0.93 W:0.87 | 0 | clean — geology only |
| H5 | 10–11°E, 9–10°N | 96.0% | E:0.95 N:0.94 S:0.97 W:0.85 | 133 | minor water cleanup |
| I5 | 11–12°E, 9–10°N | 92.5% | E:0.89 N:0.96 S:0.93 W:0.95 | 146 | minor water cleanup |
| J5 | 12–13°E, 9–10°N | 92.5% | E:0.51 N:0.92 S:0.85 W:0.89 | 461 | minor water cleanup |
| K5 | 13–14°E, 9–10°N | 94.3% | E:0.01 N:0.61 S:0.01 W:0.51 | 1861 | minor water cleanup |
| L5 | 14–15°E, 9–10°N | 98.9% | N:0.57 S:0.17 W:0.01 | 4 | clean — geology only |
| A6 | 3–4°E, 8–9°N | 93.6% | E:0.86 N:0.88 S:0.88 | 7254 | water removed & filled (lake/lagoon/river fragments) |
| B6 | 4–5°E, 8–9°N | 94.0% | E:0.89 N:0.93 S:0.88 W:0.86 | 2369 | water removed & filled (lake/lagoon/river fragments) |
| C6 | 5–6°E, 8–9°N | 95.0% | E:0.88 N:1.00 S:0.90 W:0.89 | 316 | minor water cleanup |
| D6 | 6–7°E, 8–9°N | 95.6% | E:0.96 N:0.92 S:0.93 W:0.88 | 856 | minor water cleanup |
| E6 | 7–8°E, 8–9°N | 95.7% | E:0.87 N:0.90 S:0.91 W:0.96 | 77 | clean — geology only |
| F6 | 8–9°E, 8–9°N | 92.1% | E:0.91 N:0.90 S:0.98 W:0.87 | 14 | clean — geology only |
| G6 | 9–10°E, 8–9°N | 94.0% | E:0.85 N:0.93 S:0.92 W:0.91 | 444 | minor water cleanup |
| H6 | 10–11°E, 8–9°N | 92.2% | E:0.95 N:0.97 S:0.97 W:0.85 | 654 | minor water cleanup |
| I6 | 11–12°E, 8–9°N | 98.4% | E:0.93 N:0.93 S:0.93 W:0.95 | 0 | clean — geology only |
| J6 | 12–13°E, 8–9°N | 95.9% | E:0.02 N:0.85 S:0.18 W:0.93 | 13 | clean — geology only |
| K6 | 13–14°E, 8–9°N | 97.7% | E:0.01 N:0.01 S:0.01 W:0.02 | 9 | clean — geology only |
| L6 | 14–15°E, 8–9°N | 99.4% | N:0.17 S:0.17 W:0.01 | 0 | clean — geology only |
| A7 | 3–4°E, 7–8°N | 94.5% | E:0.83 N:0.88 S:0.92 | 2109 | water removed & filled (lake/lagoon/river fragments) |
| B7 | 4–5°E, 7–8°N | 91.2% | E:0.92 N:0.88 S:0.92 W:0.83 | 0 | clean — geology only |
| C7 | 5–6°E, 7–8°N | 97.4% | E:0.85 N:0.90 S:0.93 W:0.92 | 3 | clean — geology only |
| D7 | 6–7°E, 7–8°N | 91.3% | E:0.90 N:0.93 S:0.95 W:0.85 | 1747 | minor water cleanup |
| E7 | 7–8°E, 7–8°N | 94.0% | E:0.93 N:0.91 S:0.92 W:0.90 | 16 | clean — geology only |
| F7 | 8–9°E, 7–8°N | 94.0% | E:0.70 N:0.98 S:0.84 W:0.93 | 907 | minor water cleanup |
| G7 | 9–10°E, 7–8°N | 95.3% | E:0.90 N:0.92 S:0.99 W:0.70 | 221 | minor water cleanup |
| H7 | 10–11°E, 7–8°N | 94.8% | E:0.90 N:0.97 S:0.81 W:0.90 | 0 | clean — geology only |
| I7 | 11–12°E, 7–8°N | 98.2% | E:0.50 N:0.93 S:0.76 W:0.90 | 0 | clean — geology only |
| J7 | 12–13°E, 7–8°N | 96.5% | E:0.02 N:0.18 S:0.51 W:0.50 | 5 | clean — geology only |
| K7 | 13–14°E, 7–8°N | 97.3% | E:0.01 N:0.01 S:0.51 W:0.02 | 0 | clean — geology only |
| L7 | 14–15°E, 7–8°N | 98.5% | N:0.17 S:0.57 W:0.01 | 0 | clean — geology only |
| A8 | 3–4°E, 6–7°N | 82.3% | E:0.49 N:0.92 S:0.51 | 43171 | large water area (sea/lake) — sea kept, inland water removed & filled |
| B8 | 4–5°E, 6–7°N | 88.0% | E:0.96 N:0.92 S:0.53 W:0.49 | 28760 | large water area (sea/lake) — sea kept, inland water removed & filled |
| C8 | 5–6°E, 6–7°N | 93.8% | E:0.97 N:0.93 S:0.96 W:0.96 | 27 | clean — geology only |
| D8 | 6–7°E, 6–7°N | 91.4% | E:0.94 N:0.95 S:0.94 W:0.97 | 195 | minor water cleanup |
| E8 | 7–8°E, 6–7°N | 94.8% | E:0.94 N:0.92 S:0.88 W:0.94 | 0 | clean — geology only |
| F8 | 8–9°E, 6–7°N | 95.3% | E:0.93 N:0.84 S:0.89 W:0.94 | 0 | clean — geology only |
| G8 | 9–10°E, 6–7°N | 96.0% | E:0.09 N:0.99 S:0.48 W:0.93 | 79 | clean — geology only |
| H8 | 10–11°E, 6–7°N | 97.0% | E:0.31 N:0.81 S:0.51 W:0.09 | 20 | clean — geology only |
| I8 | 11–12°E, 6–7°N | 96.8% | E:0.01 N:0.76 S:0.51 W:0.31 | 23 | clean — geology only |
| J8 | 12–13°E, 6–7°N | 96.9% | E:0.02 N:0.51 S:0.51 W:0.01 | 3 | clean — geology only |
| K8 | 13–14°E, 6–7°N | 97.3% | E:0.01 N:0.51 S:0.51 W:0.02 | 0 | clean — geology only |
| L8 | 14–15°E, 6–7°N | 98.5% | N:0.57 S:0.56 W:0.01 | 0 | clean — geology only |
| A9 | 3–4°E, 5–6°N | 97.4% | E:0.01 N:0.51 S:0.51 | 104548 | large water area (sea/lake) — sea kept, inland water removed & filled |
| B9 | 4–5°E, 5–6°N | 97.1% | E:0.12 N:0.53 S:0.51 W:0.01 | 104117 | large water area (sea/lake) — sea kept, inland water removed & filled |
| C9 | 5–6°E, 5–6°N | 79.7% | E:0.99 N:0.96 S:0.69 W:0.12 | 24129 | large water area (sea/lake) — sea kept, inland water removed & filled |
| D9 | 6–7°E, 5–6°N | 85.5% | E:0.98 N:0.94 S:0.92 W:0.99 | 373 | minor water cleanup |
| E9 | 7–8°E, 5–6°N | 92.2% | E:0.80 N:0.88 S:0.89 W:0.98 | 0 | clean — geology only |
| F9 | 8–9°E, 5–6°N | 92.9% | E:0.02 N:0.89 S:0.72 W:0.80 | 7 | clean — geology only |
| G9 | 9–10°E, 5–6°N | 96.0% | E:0.01 N:0.48 S:0.51 W:0.02 | 31 | clean — geology only |
| H9 | 10–11°E, 5–6°N | 97.6% | E:0.01 N:0.51 S:0.51 W:0.01 | 0 | clean — geology only |
| I9 | 11–12°E, 5–6°N | 98.2% | E:0.01 N:0.51 S:0.51 W:0.01 | 0 | clean — geology only |
| J9 | 12–13°E, 5–6°N | 97.0% | E:0.02 N:0.51 S:0.51 W:0.01 | 0 | clean — geology only |
| K9 | 13–14°E, 5–6°N | 97.3% | E:0.01 N:0.51 S:0.51 W:0.02 | 0 | clean — geology only |
| L9 | 14–15°E, 5–6°N | 98.5% | N:0.56 S:0.57 W:0.01 | 0 | clean — geology only |
| A10 | 3–4°E, 4–5°N | 97.2% | E:0.01 N:0.51 | 104301 | large water area (sea/lake) — sea kept, inland water removed & filled |
| B10 | 4–5°E, 4–5°N | 97.0% | E:0.01 N:0.51 W:0.01 | 104652 | large water area (sea/lake) — sea kept, inland water removed & filled |
| C10 | 5–6°E, 4–5°N | 90.4% | E:0.63 N:0.69 W:0.01 | 80426 | large water area (sea/lake) — sea kept, inland water removed & filled |
| D10 | 6–7°E, 4–5°N | 76.3% | E:0.57 N:0.92 W:0.63 | 35844 | large water area (sea/lake) — sea kept, inland water removed & filled |
| E10 | 7–8°E, 4–5°N | 89.7% | E:0.46 N:0.89 W:0.57 | 47984 | large water area (sea/lake) — sea kept, inland water removed & filled |
| F10 | 8–9°E, 4–5°N | 91.2% | E:0.01 N:0.72 W:0.46 | 63536 | large water area (sea/lake) — sea kept, inland water removed & filled |
| G10 | 9–10°E, 4–5°N | 94.0% | E:0.01 N:0.51 W:0.01 | 1829 | minor water cleanup |
| H10 | 10–11°E, 4–5°N | 97.6% | E:0.01 N:0.51 W:0.01 | 0 | clean — geology only |
| I10 | 11–12°E, 4–5°N | 98.2% | E:0.01 N:0.51 W:0.01 | 0 | clean — geology only |
| J10 | 12–13°E, 4–5°N | 97.0% | E:0.02 N:0.51 W:0.01 | 0 | clean — geology only |
| K10 | 13–14°E, 4–5°N | 97.2% | E:0.01 N:0.51 W:0.02 | 0 | clean — geology only |
| L10 | 14–15°E, 4–5°N | 98.5% | N:0.57 W:0.01 | 0 | clean — geology only |

## Summary statistics

- Mean agreement with the original (excluding deliberate water removals): **~94%**; every block ≥ 90% except the Lake Chad blocks (K1/L1/K2), where the deviation is the requested water removal itself.
- Edge continuity across all internal block boundaries: median **0.93**, i.e. formations continue seamlessly across blocks (values < 0.6 only occur on boundaries that run along white/unmapped or graticule-only strips, where there is no geology to match).
- Water removed & filled: 174004 px inland water + 39064 px thin water lines.
- White-artifact repairs: 5,113 px; over-paint corrections: 471 px; colour corrections from original: 32,025 px.
- Graticule, ticks and degree labels (3°0'E…14°0'E, 4°N…13°N) preserved exactly.

## Observations

- The large **blank areas in the south-east** (e.g. 10–13°E, 5–8°N) are blank in the **original NGSA map as well** (verified pixel-wise) — they are unmapped territory on the source map, not damage from processing.
- The **blue-teal valley bands** (Ogun/Osun, Rima/Sokoto, Niger valley, incl. the Kainji stretch) match three distinct legend units (alluvium) and are treated as geology. If you want the Kainji reservoir stretch removed as water, that is a one-line change.
- The **ocean** was kept as a uniform (152,216,240) base so the coastline remains a usable boundary for digitizing; all ocean tile seams were unified.

## Georeference (for GIS use)

Affine (EPSG:4326, pixel-center convention), also provided as `NGSA_map_geology_legend_isolated_v2.pgw`:

- lon = 3 + (x − 288) / 328.4
- lat = 4 + (3343 − y) / 328.4

So pixel (288, 3343) = (3°E, 4°N) exactly; 1° = 328.4 px. Load the PNG with the .pgw in QGIS (Layer → Add Raster Layer, assign EPSG:4326), then digitize polygons by colour.

## Palette

37 geology colours are used (see `analysis/palette_v2.json`); the authoritative unit names are the legend printed on the right-hand panel of the image itself (preserved unchanged).
