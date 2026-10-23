# Accuracy audit — can another EPSG layer + adjusted coordinates get below ±10 km?

Short answer: **for the transform, no — it is already at its floor and provably cannot
improve. For the point positions, partly yes, and that part is now implemented.**

The ±10 km is not a georeferencing error. It is the distance between the ink that
represents a locality (its printed symbol) and the ink that was used to place it (its
number label). No reprojection or resampling can move a point closer to a symbol.

All figures below are measured from the two PDFs and from the delivered GeoPackage.

---

## 1. The transform is already optimal

| Test | Result | What it means |
|---|---|---|
| Affine fit to the geology graticule (12 meridians, 10 parallels) | max residual **0.185 pt = 130 m**, rms 0.11 pt | registration is 77× finer than the 10 km figure |
| 2nd-order polynomial instead of affine | **0.197 pt** (no improvement) | the sheet is a clean affine; there is no paper distortion left to model |
| Mineral sheet, affine / 2nd-order | 2.94 pt / 2.72 pt (2.1 / 1.9 km) | also affine; the 2.9 pt is label-centring noise, not distortion |
| Anisotropy (pt per degree lon ÷ lat) | 1.0000 (geology), 1.0005 (mineral) | the frames are square; nothing to un-skew |
| EPSG:4326 → EPSG:32632 → EPSG:4326 round trip, all 999 points | max **0.000 mm** | reprojection is exact; a new EPSG layer changes the numbers, not the accuracy |
| Area check, geology polygons | 924,900 km² vs 923,768 official (**+0.1 %**) | the geometry is not stretched anywhere |

A higher-order warp would only be fitting the 0.1-pt noise of where the printer put the
graticule lines. There is no residual signal at any wavelength worth removing.

## 2. Where the ±10 km actually comes from

On the 2023 sheet each locality is printed as a **number label** plus, sometimes, a
**mineral symbol**. Measuring the distance between a label and the symbol that was
accepted for it:

| label → accepted symbol displacement (n = 686) | value |
|---|---|
| median | **9.0 km** |
| p75 | 10.8 km |
| p90 | 12.8 km |
| max | 17.3 km |
| within 2 km | 10 points |

The cartographer moved the numbers off the symbols to keep the sheet legible. So the
same sheet supports two very different accuracies depending on which ink you anchor to:

| Anchoring | Points | σ | Why |
|---|---|---|---|
| Printed symbol centre | **686** (68.7 %) | **±0.7 km** | the symbol *is* the feature; 1 pt of ink = 0.71 km |
| Symbol recovered by mineral identity + geometry | **49** (4.9 %) | **±1.2 km** | unambiguous match to a same-mineral symbol |
| Label position only | **264** (26.4 %) | **±10 km** | label displaced from the feature by the margin above |

Result: **median positional σ is now ±0.7 km**, not ±10 km. The ±10 km applies only to
the quarter of points whose symbol cannot be located.

## 3. The adjustment you proposed — implemented, and here is what it yields

For each label-only locality the script searches for a symbol of *the same mineral*
(identity, not just colour) and accepts the match only if it is unambiguous — the best
candidate at least twice as close as the next, within 15 km.

| Outcome | Points | Consequence |
|---|---|---|
| Accepted | **49** | moved median **6.9 km** (max 14.6 km); host rock changed for 12 |
| Ambiguous (several same-mineral symbols nearby) | 41 | left at label position — a wrong 7 km snap is worse than an honest label |
| No same-mineral symbol within 30 km | 223 | their symbols are either not printed or were exported as merged clusters (95 of 1,609 symbols are unidentified blobs) |

So geometric adjustment converts about 5 % of the sheet from ±10 km to ±1 km. It cannot
do more, because **for 223 points the information is not on the sheet** — there is no
symbol within 30 km to snap to.

Every point now carries `pos_method` and `pos_sigma_m`, and the 49 moves are listed in
`locality_reassignments.csv` so they can be reviewed or rejected individually.

## 4. Why warping one sheet onto the other does not help either

The two sheets share coast, borders and rivers, so they can be cross-registered. Doing
that on the drawn coastline:

| | median | p90 |
|---|---|---|
| Offset as registered | 5.4 km | 17.9 km |
| After the best possible global shift (−0.03°, −0.02°) | 4.9 km | 24.0 km |

The optimum shift is only 3 km and it barely changes the median. The disagreement is not
a displaced frame — it is two different generalisations of the same coast, compiled 12
years apart. The same is true of a thin-plate-spline warp: it would fit the ocean and
distort everything else.

## 5. Error budget

| Source | Magnitude | Reducible from these PDFs? |
|---|---|---|
| Graticule fit / registration | 0.13 km | already at floor |
| Reprojection (4326 ↔ UTM / Albers) | 0.000 mm | n/a — exact |
| Printed symbol size (1 pt ink) | 0.7 km | no |
| Label placement, symbol-anchored points | covered by symbol centre | no |
| Label placement, label-only points | 9–13 km | **only for 49/313** |
| Source compilation & generalisation at 1:2 M | ~1–2 km | no |
| Sheet-to-sheet base disagreement | 5 km median, 18 km p90 | no — content, not geometry |
| **Best achievable for a symbol-anchored point** | **~0.7–1.2 km** | — |
| **Best achievable for a label-only point** | **~10 km** | — |

## 6. If you need better than ±1 km

Not from these two files. What would actually do it, in order of cost:

1. **NGSA 1:100,000 sheet maps** — 132 sheets published 2004–2023, free from ngsa.gov.ng;
   four times the linear scale, so 1 pt of ink is 0.18 km and the compilation error falls
   with it.
2. **NGSA state mineral resources maps at 1:250,000** — the 2023 national sheet is compiled
   from these, so the locality symbols are placed at 8× the resolution before generalisation.
3. **Field or GPS coordinates** for the specific deposits you care about, joined by name.
4. **Authoritative vectors for the base** (OSM, Natural Earth, GADM) instead of the 2011
   generalised coastline — this fixes the 5 km base disagreement but not the 9 km label
   displacement, which is a property of the mineral sheet itself.
