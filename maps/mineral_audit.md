# Mineral-symbol audit — NGSA Mineral Resources Map of Nigeria, 2nd edition 2023

**Question asked:** are all the printed mineral symbols recorded, and is each point at the
centre of its printed symbol? The sheet carries *about 1,531* symbols.

**Answer: no, on both counts.** The symbol positions that were carried into
`Nigeria_Geology_Minerals_4326.gpkg` are wrong by about 10 km on average, so no derived
mineral layer (localities, icon-anchored localities, host-unit joins) can be used for
calculation. This file records the measurement and the rebuild.

---

## 1. How the sheet is built

The map body is **not vector**. It is seven embedded raster strips
(`xref 3/5/7/9/11/13/15`, 2060 px wide, 255 px tall), placed at x 74.24–2051.83 pt,
y 358.72–1968.66 pt. 1977.59 pt over 2060 px is exactly **75 dpi** (1.041667 px/pt).
Every symbol, every geology wash and every road casing lives in those pixels.

What *is* vector: the graticule, state boundaries, rivers, the place/feature labels,
the gazetteer numbers, and the letters drawn *inside* the symbols (`C`, `K`, `B`, `W`, …).
The symbol bodies themselves are raster, drawn in exact flat colours, with their internal
marks in a single ink colour **(31,26,23)** — distinct from the pure black (0,0,0) of text
and linework, which is what makes them separable.

### 1.1 The stored georeferencing is wrong

`minerals2023_mineral_symbols_raster` carries the transform

    lon = (x + 288.67) / 157.288        lat = (2575.87 - y) / 157.602

The printed graticule says otherwise. Fitting the detected graticule lines
(verticals x = 341.44, 656.64, 971.84, 1287.03, 1602.23, 1917.43 for lon 4…14;
horizontals y = 523.53, 838.73, 1153.93, 1469.14, 1784.34 for lat 13…5) gives
residual **0.000 pt** with

    lon = 0.006345 · x_pt + 1.8335          lat = -0.006345 · y_pt + 16.3218

i.e. **157.5987** and **157.6015** pt per degree, offsets −288.95 and 2572.35.
The stored longitude scale is 0.31 pt/° out (0.2 %) and the latitude offset is 3.5 pt out.

## 2. The measurement that matters

Converting the 1,514 real symbol rows through their own transform and asking how far each
lands from the nearest symbol ink on the sheet:

| statistic | value |
|---|---|
| median distance to nearest symbol ink | **14.09 px = 13.5 pt = 9.6 km** |
| mean / max | 17.88 px / 95 px |
| within 1 px (on the mark) | **5.9 %** |
| within 2 px | 9.1 % |
| within 4 px | 16.2 % |

Against the 1,323 symbols actually detected (§3): median distance **18.6 px**, and 1.9 %
are within 3 px. For two *independent* point sets of this density the expected median
nearest-neighbour distance is 22 px — the stored coordinates are statistically
indistinguishable from a random scatter.

**So the stored lon/lat carry no positional information.** They are not slightly off, and
they are not a shifted or rescaled copy of the true layout either. The two point clouds
have almost the same longitude extent (ratio 0.998), yet no translation reduces the
residual: a ±2 px tolerance around each stored point reaches only 30.3 % of the symbols,
and the best 26 px offset search over the whole sheet reached 29.9 %. Every claim in the
README about mineral positions being ±0.7 km is withdrawn.

## 3. Rebuild: 1,323 symbols, each centred on its glyph

`find_sites.py` detects a site as the union of, at the sheet's native resolution:

* compact flat-fill blobs (8–260 px, 4–22 × 3–18, fill ≥ 0.45) in the 14 fill colours that
  the whole-canvas colour scan shows form glyph bodies and nothing else
  (yellow, red, olive, magenta, grey-96, green, grey-130, grey-170, light green,
  blue-grey, dark, tan, bright green, orange);
* clusters of symbol-ink marks (31,26,23);
* enclosed white glyph bodies;
* black outline rings.

Parts within 5 px are merged into one site. The site's coordinate is the centroid of the
glyph body, so **the point is the centre of the symbol by construction** — not a label
position and not the centroid of a group.

| | |
|---|---|
| symbols detected | **1,323** |
| per 244-px band (N→S) | 78, 184, 208, 299, 316, 175, 63 |
| produced `lon` range | 2.457 – 14.400 |
| produced `lat` range | 3.843 – 14.038 |
| duplicate coordinates | 0 |
| invalid/null geometry | 0 |

Output: `mineral_symbols_detected.gpkg`, layer `mineral_symbols_detected`
(columns `canvas_x/y`, `x_pt/y_pt`, `lon/lat`, `glyph_class`, `class_dist`, `mineral`, `parts`).

### 3.1 Completeness check

Template matching against 37 map-native glyph templates (cluster means) returned 290 hits,
of which only **9** were more than 5 px from an already-detected site — the detector is
saturated, not under-sampled. Spot counts against the printed sheet agree: the dense
region x 1000–1200 / y 560–760 yields 34 detected for ~30 counted by eye; the hatching of
the pale-green units produces no detections, as it should.

### 3.2 The gap to ~1,531

Loosening the body threshold (min area 8 → 6 px, fill 0.45 → 0.40) raises the count to
1,505 — within 2 % of the quoted 1,531 — but the extra ~180 markers sit **along river
channels and the dashed state boundary**, not on symbols. They are the dotted ornament of
the drainage and boundary linework, at exactly the size and flatness of a small glyph.
At 75 dpi they cannot be separated from a 5-px symbol by colour, shape or context alone.

So the honest reading is: **1,323 confirmed symbols, and up to ~180 further marks that are
probably linework ornament.** The ~1,531 figure is consistent with the loose count, which
means it most likely includes that ornament, but that cannot be settled from the raster
without a higher-resolution source of the same sheet.

### 3.3 Attribution

886 of the 1,323 (67 %) are named, by matching each site to a clustered glyph exemplar and
reading the exemplar against the sheet's 67-entry EXPLANATIONS panel:

| mineral | n | | mineral | n |
|---|---|---|---|---|
| Clay / Pottery Clay | 189 | | Uranium | 34 |
| Kaolin / kaolinitic clay | 125 | | Coal | 34 |
| Gold | 122 | | Brine | 34 |
| Baryte | 63 | | Molybdenite | 24 |
| Iron Ore (Magnetite, Ilmenite) | 48 | | Lepidolite | 21 |
| Tourmaline | 46 | | Tantalite | 17 |
| Columbite | 45 | | Mica (m) | 7 |
| Fire Clay | 40 | | | |
| Lead-Zinc | 37 | | **named total** | **886** |

The remaining 437 are left `mineral = NULL` rather than guessed. They are the small
pictographic glyphs (dredger, leaf, cross-hatch, hexagon variants) whose 8–14 px bitmaps
do not separate confidently from the legend at this resolution.

## 4. What this means for the deliverable

* `mineral_symbols` (1,609 rows) and the whole `mineral_localities*` family (999 rows each)
  **must not be used for calculation** until rebuilt: their positions are ~10 km noise.
* `mineral_symbols_detected` replaces the printed-symbol layer with centres that are
  correct to ±0.5 px (±0.35 km) for position and to the sheet's own registration (~0.13 km).
* The locality layer is not yet rebuilt. It needs the gazetteer numbers re-associated to the
  new symbol sites; the numbers are vector text on the sheet and are still intact, so this
  is a tractable follow-up, but it is a separate job from the symbol geometry.
