# Accuracy audit — is the symbol centre the true point, and does snapping help?

You asked whether the centre of each symbol should be taken as the actual location, and
whether that improves things. **Yes for a single symbol — that is now the anchor for 686
localities. No for a cluster of symbols, and only partly for the ones whose symbol has to
be guessed.** All three claims are measured below.

---

## 1. The symbol centre is the right anchor (and is already used)

On the 2023 sheet a locality appears as a **mineral symbol**, which depicts the feature,
plus a **printed number**, which is only a pointer. The symbol centre is authoritative; the
number is wherever the cartographer could fit it.

| | measured |
|---|---|
| Distance from a locality's printed number to the symbol that represents it (n = 686) | median **9.0 km**, p90 12.8 km, max 17.3 km |
| Locality anchored on its symbol centre | **686 (68.7 %)**, σ **±0.7 km** |
| Host-rock agreement with the sheet's own reading, for those points | **95.7 %** |

One point of ink at 1:2,000,000 is 0.71 km, so a symbol centre is as good as this sheet allows.

## 2. But the centre of a *group* of symbols is worse

The obvious extension — average the nearby symbols and use the centre of that cluster —
was rejected on measurement:

| rule | error against the true symbol centre |
|---|---|
| nearest compatible symbol | **0.0 km** median (83–97 % hit it exactly) |
| centroid of same-colour symbols within 20 km | **2.9 km** median |

A cluster mixes symbols belonging to neighbouring localities, so its centre sits between
two deposits rather than on either.

## 3. Snapping helps only while the candidate is close — and hurts beyond that

The hard question is the 313 localities whose symbol is *not* printed near their number.
I simulated exactly that situation on the 686 known points: hide every symbol within 8.8 km
of the printed number (the search radius the original extraction used), then apply the rule
and see whether it finds the right symbol.

| distance from number to the chosen symbol | n | lands on the right symbol | lands >5 km wrong | 
|---|---|---|---|
| 8.8 – 12 km | 190 | **83.2 %** | 14.7 % |
| 12 – 16 km | 78 | 66.7 % | 33.3 % |
| 16 – 25 km | 90 | **4.4 %** | 95.6 % |
| all | 358 | 59.8 % | 39.1 % |

**A blanket snap is worse than no snap:** rms error 11.8 km after snapping versus 9.4 km
leaving the points on their printed numbers. Beyond 16 km the rule is almost never right,
so it is not a matter of tuning a radius.

The earlier easy-case backtest (95.5 % correct) was misleading because it could only test
the cases where the symbol was already close — i.e. exactly the ones the original
extraction had already solved.

## 4. Policy adopted

| method | points | σ | grounds |
|---|---|---|---|
| Printed symbol centre | **686** | ±0.7 km | the symbol is the feature |
| Symbol recovered by mineral identity / colour, unambiguous, ≤12 km | **117** | ±3 km | back-test: 83 % correct, 15 % wrong, rms ≈3 km |
| Printed number only (no unambiguous symbol within 12 km) | **196** | ±10 km | snapping would make these worse |

Median positional σ across the layer: **±0.7 km**. Every point carries `pos_method`,
`pos_sigma_m` and `pos_confidence` (`high` / `probable` / `low`), and the 117 moves are listed
in `locality_reassignments.csv` so any of them can be rejected individually.

## 5. The transform cannot be improved (unchanged result)

| test | result |
|---|---|
| affine fit to the geology graticule (12 meridians, 10 parallels) | 0.185 pt = **130 m** |
| 2nd-order fit instead of affine | 0.197 pt — no gain, so no paper distortion to model |
| anisotropy (pt per ° lon ÷ pt per ° lat) | 1.0000 |
| EPSG:4326 → 32632 → 4326, all points | **0.000 mm** |
| geology polygon area vs official Nigeria | +0.1 % |

A second EPSG layer re-expresses the same points; it does not re-measure them. `mineral_localities_utm32n`
(EPSG:32632) is included for metric work.

## 6. A defect found in the source extraction, and its scope

While checking this, the `minerals2023_graticule` table in the reference extraction turned out
to place the printed **4°E** meridian at **4.1718°** — a +0.172° (19 km) offset in longitude.
That looked alarming, so the feature layers were tested independently:

| test | result |
|---|---|
| 2023 national boundary → 2011 sheet's coverage edge (the national border) | **0.1 km** median |
| 2023 towns → 2011 towns | 0.5 km |
| 2023 railway / roads → 2011 | 1–2 km |
| 2023 graticule table labels | 0.172° off |

So only the QA graticule table was mislabelled; the feature layers are correctly georeferenced.
That table is corrected in the GeoPackage (`label_offset_deg` records the adjustment). Had the
offset been real, the boundary would have missed the border by 19 km — it misses by 100 m.

## 7. What would actually reduce the ±10 km

Nothing in these two files. In order of cost:

1. **NGSA 1:100,000 sheets** (132 published 2004–2023, free) — 4× linear scale, so ink
   resolution falls from 0.7 km to 0.18 km and the 9 km label placement problem disappears.
2. **NGSA state mineral maps at 1:250,000** — the national sheet is compiled from these.
3. GPS coordinates for specific deposits, joined by name.
4. Authoritative base vectors (OSM/OSM-derived) to replace the 2011 generalised coastline —
   fixes the 5 km base disagreement, not the label displacement.
