# Accuracy audit — is the symbol centre the true point, and does snapping help?

> ## ⚠ WITHDRAWN IN PART — read this first
>
> **Every number in §1 and §3b that describes where a locality sits is retracted.** Those
> figures were computed from the coordinates the source extraction stored for the 2023
> symbols, and a later audit measured those coordinates against the sheet itself: they sit
> a median **14.1 px (9.6 km)** from any printed symbol, and their nearest-neighbour
> distribution is statistically indistinguishable from a random scatter of the same size.
> The stored lon/lat carry **no positional information**, so "842 (84.3 %) on a printed
> symbol", "686 anchored", "σ ± 0.7 km", "97.4 % land on the correct icon" and
> "93.5 % host-rock agreement" are all withdrawn. See `mineral_audit.md` and README
> caveat 2.
>
> What survives: the *method* (§1's finding that a symbol centre is a better anchor than
> the printed number, §2's rejection of cluster centroids, §3's measurement that snapping
> beyond ~16 km is worse than not snapping, §5's transform residuals, §6's mislabelled QA
> graticule). Those are properties of the printed sheet and of the registration, and they
> are re-measured on the rebuilt, correctly placed layer:
> `minerals_named` — 1,323 symbols, point = measured glyph centre, ±0.35 km.
>
> **The rebuild has not been done.** The `mineral_localities*` layers (999 rows each) still
> rest on the discredited coordinates and are queued for rebuild on top of
> `minerals_named`; until that happens the figures below describe a layer that must not be
> used for calculation. §4's field list is also stale: see the note at the end of §4.

You asked whether the centre of each symbol should be taken as the actual location, and
whether that improves things. **Yes for a single symbol — that was the anchor for 686
localities (withdrawn, see above). No for a cluster of symbols, and only partly for the
ones whose symbol has to be guessed.** All three claims are measured below.

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

> Measured on the printed sheet's own symbol geometry — one of the findings that survives
> the withdrawal. It is also what `anchor_to_icons.py` does: where a locality owns several
> printed icons it takes the medoid — the real icon nearest the group centre — and never the
> centroid, which can land on blank paper between two deposits.

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

## 3b. Anchoring every point on its icon (the brief) — implemented, with one correction

> **Withdrawn.** The "842 / 999 (84.3 %)" row is the headline number of the retracted
> result: it was measured with the stored symbol coordinates. Re-measured on the printed
> sheet, those coordinates are 9.6 km noise (`mineral_audit.md`), so neither the 84.3 % nor
> the before/after comparison below is a statement about the shipped data. `minerals_named`
> replaces it: 1,323 glyphs, each point the measured centre, 94.9 % of them within 1 px of
> the symbol ink (a random point in the same area: 8.5 %).

You asked that the mineral points be the calculated centre of the symbol icons. Implemented
in `anchor_to_icons.py`, with one correction that the measurement forced:

| variant | points sitting on an icon | verdict |
|---|---|---|
| centroid of all icons owned by a locality | **693 / 999** | rejected — where a locality prints several icons they are a cluster with a median spread of 11.2 km, and their centroid falls **5.9 km** from the nearest icon, i.e. on blank paper |
| medoid — the real icon nearest the group centre | **842 / 999** | used |

So the rule is: one icon -> that icon's exact centre; several icons -> the printed icon nearest
their centre. Either way the point always lands on ink, never between symbols. Both coordinates
are kept (`group_centroid_lon/lat` records where the geometric centroid would have been).

Icon assignment uses commodity identity (<=20 km), then recorded colour (<=15 km), then colour
inferred from the commodity (<=12 km). Back-tested on the 686 localities whose icon is known:
**97.4 % land on the correct icon** (685 of 686 resolved).

| | before (numbers used) | refined | icon-anchored |
|---|---|---|---|
| points within 0.4 km of an icon | 686 (68.7 %) | 803 (80.4 %) | **842 (84.3 %)** |
| p90 stray to nearest icon | 11.1 km | 11.0 km | **10.7 km** |

**Does it reduce the stray? Yes, but modestly — not to zero.** 179 points still sit on their
printed number, with a median 11.1 km stray, because for them the sheet prints nothing to anchor
to. Re-measured against the shipped layers:

| why the 179 stayed | points |
|---|---|
| the commodity has no legend symbol at all (cassiterite, quartz, clay…) | 58 |
| a same-commodity symbol is printed, but a median **56 km** away | 102 |
| no same-commodity symbol anywhere on the sheet | 19 |

In the 15 cases where a same-commodity symbol *is* within 10 km, that symbol is **already claimed
by another locality**, so snapping would steal it rather than place this one. Pointing these at a
distant icon would be the 4 %-accurate case from §3, i.e. it would add stray. This is a limit of
the printed sheet, not of the processing.

## 4. Policy adopted

> **Withdrawn.** This table describes the superseded positions. The shipped
> `mineral_localities_icons` layer carries `pos_method`, `n_icons`, `icon_tier`,
> `icon_spread_m` and `moved_from_label_m` — it does **not** carry `pos_sigma_m` or
> `pos_confidence`; those exist only in `mineral_localities_refined`, which is kept for
> comparison. And the positions they describe are ~10 km noise (see the banner), so the
> whole policy is queued for rebuild on `minerals_named`.

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

## 6b. What the deep audit of the locality layers changed

The ±10 km in this document is the *locating* error, and it is unchanged. A later
layer-by-layer audit of the GeoPackage found defects of a different kind — record-level
inconsistencies that no accuracy figure would have revealed — and fixed them. They matter here
because two of them could have been mistaken for accuracy:

| defect | how it showed up | what was wrong | now |
|---|---|---|---|
| stale host stratigraphy | one locality (number **70**, host code `GIgss`) carried `Cenozoic / Quaternary` while its host unit is `Mesozoic / Cretaceous` | the host join had been made before the unit table was final; 999 rows were checked and only this one had drifted | re-joined; the audit's `denormalised_unit_attribute_drift` check guards it |
| "projected copy" that was not one | `mineral_localities_utm32n` disagreed with `mineral_localities` by up to 11.9 km in 117 rows | it is the EPSG:32632 copy of `mineral_localities_**refined**` (the de-duplicated positions), not of the raw digitised layer — the name and the catalogue both implied otherwise | documented as the copy of `_refined`; attribute-identical to it, 0 m round-trip |
| position stored twice | `towns`, `state_capitals`, `volcanic_plugs` keep `lon`/`lat` **and** geometry | the pair had been rounded to 6 dp and the geometry had not, so the two disagreed by up to 0.1 m — harmless, but a file should not hold two answers to one question | geometry snapped to `lon`/`lat` (residual < 1 nm); the audit re-checks it at 1 cm, the EPSG:6933 round-trip figure of 1.4 mm |

Neither of the first two changes any coordinate. The third moves points by at most 0.1 m. The
±10 km stands, and the audit's job from here is to keep such record-level errors from being
read as measurement error.

## 7. What would actually reduce the ±10 km

Nothing in these two files. In order of cost:

1. **NGSA 1:100,000 sheets** (132 published 2004–2023, free) — 4× linear scale, so ink
   resolution falls from 0.7 km to 0.18 km and the 9 km label placement problem disappears.
2. **NGSA state mineral maps at 1:250,000** — the national sheet is compiled from these.
3. GPS coordinates for specific deposits, joined by name.
4. Authoritative base vectors (OSM/OSM-derived) to replace the 2011 generalised coastline —
   fixes the 5 km base disagreement, not the label displacement.
