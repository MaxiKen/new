# In plain language: the four things you asked for

You asked for four things. Here is each one, what I did, and how you can check it yourself.

---

## 1. "The map pictures must be clearer"

**Done.** The old previews were drawn from a coarse raster. The new plates are drawn from the
**vector** content of the sheets, so the unit outlines, faults, roads and rivers are sharp at any
zoom, and each plate has proper map furniture: title block, north arrow, scale bar in kilometres,
graticule with degree labels, a full legend, and a footnote carrying the accuracy limits.

| plate | what you get |
|---|---|
| `Map_1_Geology.png` | the geological map, with the **whole 45-code unit legend** (grouped by period), faults, roads, rivers and state boundaries |
| `Map_2_Minerals.png` | the 2023 sheet with all 1,323 symbols re-plotted and colour-coded by commodity class |
| `Map_3_Combined.png` | geology (muted) + interpolated symbol density + every symbol + faults |
| `Map_4_Symbol_Centring.png` | six close-ups proving where each coordinate actually sits |

Every plate is drawn **from the GeoPackage itself**, so the picture and the data can never drift
apart.

## 2. "The mineral symbols are still not centred"

You were right, and this is what it took.

The points were landing *on* the symbols, but not at their centres — off by a median of about
3 px, roughly 2 km. Two things were checked before changing anything:

* **Was there a systematic shift?** No. Across 748 points the matching symbol sat at exactly
  **(0.0, 0.0)** pixel offset. So there was no bias to remove; the error was scatter.
* **What sets the floor?** One pixel of the artwork is **0.68 km**. Nothing measured from this
  sheet can be more precise than that.

Each point was then re-measured to the centre of its own printed glyph, and checked on the page
itself — by re-rendering the sheet and re-detecting the glyphs, without reusing any number from
the build:

| check | result |
|---|---|
| points landing on a detected symbol | **97.8%** |
| median distance from point to symbol centre | **0.35 km** |
| within 2 pt (1.4 km) | **95.4%** |

0.35 km is **half an artwork pixel** — finer than the drawing itself. `Map_4_Symbol_Centring.png`
shows six points at 14× and prints each one's own measured offset next to it, so you can see
rather than take my word.

## 3. "Extract the other useful features — fault, fold, etc."

The 2011 sheet is fully vector, so I read its legend and pulled out what is actually drawn:

| feature | what came out |
|---|---|
| map units | **1,142 polygons**, **45 named codes**, each with name and period |
| faults (major fractures) | **13 traces, 246 km** — the sheet's hachured symbol |
| roads | **954 strokes**, the national road network |
| rivers | **1,055 lines** |
| state boundaries | **83 lines** |
| **folds** | **not on this sheet at all** |

**About folds, straight:** this edition's structural key lists *Geological Boundary* (exact,
approximate, inferred, transitional), *Major Fractures / Faults* and *Fractures / Fault
(inferred)*. There is no fold symbol, no dip-and-strike symbol, and no separate structural line
group in the file. I could have drawn a "fold layer" from something else, but it would have been
invented, so I left it out.

**One trap worth knowing about.** Faults and roads are drawn with the *same* thick black pen.
My first attempt joined them together and produced a fake fault network running across the whole
country — wrong, and I threw it away. The honest separation is by connectivity: the roads form
one continuous connected network (954 touching strokes), while the fault dashes stand alone
(65 isolated strokes, chaining into 13 traces). All 13 lie in the Chad Basin margin in the
north-east, which is what this sheet actually shows.

## 4. "Map the geology and its associated layers"

**Done.** `Nigeria_Geology_Minerals_4326.gpkg` holds **13 layers**, all EPSG:4326, and passes
**27 of 27** validation checks:

* 7 vector layers: geology units, faults, roads, rivers, state boundaries, mineral symbols,
  national outline
* 6 raster layers: both sheets as drawn, the combined view, and three density surfaces

Open it in QGIS and every layer lines up, because they all come from the same two sheets placed
in the same frame.

## What the geology sheet needed: nothing

A different kind of file — 45,000 vector objects, no images — so it could be tested much harder
than the mineral sheet:

| what I checked | which way it wants to move |
|---|---|
| its state boundaries vs modern state boundaries | +0.2 km east, +0.9 km north |
| its Niger and Benue rivers vs Natural Earth | +0.2 km east, +0.8 km north |
| its coastline vs modern coastline | +0.3 km east, −2.1 km north |

Two checks agree to within 0.1 km, and the shift they want is **smaller than one and a half map
pixels**. The third disagrees. That pattern is drawing imprecision, not a fixable error — so **no
correction was applied**. Applying one would have been fitting noise.

The mineral sheet was different: it contradicted itself by **19 km**, which is why that one *was*
corrected.

## The remaining limits, in one place

| thing | status |
|---|---|
| datum | neither sheet states one. EPSG:4326 is the display frame. Minna → WGS 84 is ~0.09 km, far below what these sheets resolve |
| geology registration | 1–2 km, no correction applied |
| symbol centres | ~0.35 km median; 0.68 km is the artwork's floor |
| commodity names | ~81% correct per point — use the per-point `tier` and `confidence` columns |
| density surfaces | count **printed symbols**, not reserves, grade or production |
| not for | surveying, licensing, legal boundaries, navigation, or site-scale decisions |

## Files

| file | what it is |
|---|---|
| `Nigeria_Geology_Minerals_4326.gpkg` | **the product** — 13 layers, 16.6 MB, EPSG:4326 |
| `Map_1_Geology.png` … `Map_4_Symbol_Centring.png` | the four plates |
| `GEOPACKAGE_README.md` | layer-by-layer reference and method |
| `GeoPackage_Validation.json` | the 27 checks and their results |
| `Verify_Centres.json` | the centring verification numbers |
| `Geology_Extraction_Summary.json` | what was extracted, and how much of it is named |
