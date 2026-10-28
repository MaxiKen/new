# In plain language: what was wrong, what I fixed, and what I did to the geology map

## 1. The one real error, in a sentence

The 2023 mineral sheet draws its own longitude grid in the wrong place — it is **19 km too far west** — so every mineral point read off that grid came out 19 km west of where it belongs. **I moved all 1,323 mineral points 19 km east to fix it.**

That is the whole correction. Nothing else needed moving.

## 2. How I know it's 19 km and not something else

The sheet contradicts itself. It says "4°E" is in two different places at once:

* where the **printed grid line** is drawn on the paper,
* where the **computer-readable georeferencing** inside the PDF says it is.

Those two are 19 km apart. Only one can be right. To decide which, I used something the mapmaker drew that I can check against the real world: **the country's own border**, which is drawn as clean vector linework on that sheet, not as pixel artwork.

I laid a modern Nigeria border on top of the sheet, twice — once using the printed grid, once using the embedded georeferencing:

| which definition I used | how far the modern border missed the sheet's drawn border |
|---|---|
| printed grid | **12.9 km** (and always to the west — a systematic error) |
| embedded georeferencing | **1.1 km** against Natural Earth, **0.5 km** against GADM |

The border lands on top under the embedded version. So the sheet was *drawn* in the embedded frame, and the printed grid is the mistake. The mineral points had been read off the printed grid — hence 19 km west.

This is not a guess or an optimisation. It's one of the two options the sheet itself offers, and the sheet's own linework picks one.

## 3. What I did to the geology map — you were right that I hadn't touched it

The geology sheet is a completely different kind of file: **45,000 vector objects, no images at all**. That let me run a much stronger test on it than on the mineral sheet. I ran three independent checks:

| what I checked | which way it wants to move | how sure (1σ) |
|---|---|---|
| its **state boundaries** vs modern state boundaries | +0.2 km east, **+0.9 km north** | ±0.3, ±0.2 |
| its **Niger and Benue rivers** vs Natural Earth | +0.2 km east, **+0.8 km north** | ±0.8, ±0.9 |
| its **coastline** vs modern coastline | +0.3 km east, **−2.1 km north** | ±1.1, ±0.4 |

**Result: the geology sheet needs no correction.** Two of the three agree with each other almost exactly (they want the same +0.2 km east, +0.9 km north), and that shift is **smaller than one and a half pixels of the map**. The third — the coastline — disagrees, which tells me the small offsets are just drawing imprecision, not a fixable error.

That matters. For the mineral sheet there was a **19 km** contradiction: obvious, systematic, and provable. Here there is a **1 km** wobble that points in different directions depending on what you measure — which is exactly what a hand-drawn 1:2,000,000 map looks like. Applying a "correction" here would be fitting noise and would make the map *worse*, not better.

So what I did with the geology map instead:

1. **Turned it into a proper GIS layer** — `Geology_Georeferenced.tif`, the entire sheet at double resolution, correctly placed in longitude/latitude, with its accuracy and caveats written into the file's own metadata.
2. **Rebuilt the combined map properly.** The earlier version blended the two sheets at 62%/38%, which turned the geology into mud and made both legends useless. The new `Combined_Map_v2.png` keeps the geology in full, unmodified colour and draws the 1,323 corrected mineral symbols on top as clean vector markers, colour-coded by commodity class.

## 4. Why the previous answer was impossible to read

I was answering a narrower question than you asked. You asked "how do we confirm the datum?" and I answered with a statistical argument about *why the datum cannot be confirmed* — 0.11 km signal against 0.85 km noise, chi-squared reasoning, bootstrap standard errors. All of that is true and all of it was in the report, but it answered "can we?" when you wanted "then what's the number?"

Plain version of that answer:

> A "datum" is the assumed shape and position of the earth that a map's coordinates are measured against. Nigeria's official one is called **Minna**, and converting from Minna to the modern standard (WGS 84, what GPS uses) moves everything by about **90 metres**. These sheets are accurate to about **1,000–2,000 metres**. So the datum question is asking me to detect a 90 m effect with a ruler that only reads to 1,500 m — from map artwork alone. It can't be done, and no amount of analysis changes that. It's not a failure of effort; it's a property of the data.
>
> The practical consequence is small: **treat the coordinates as WGS 84 and quote ±1–2 km.** That is exactly what the file metadata now says.

If you need better than that, the only routes are the two in `Datum_Confirmation_Plan.md`: ask NGSA which coordinate system their source geodatabase uses (one email, decisive), or survey ~20 map features with RTK GPS. The tool for the second is built and tested.

## 5. Honest list of what is and isn't known

**Known and fixed**
* Mineral points: 19 km eastward error → corrected, old values kept in the file.
* Geology map: registered from its printed grid; no correction needed.
* Both sheets: the printed grid is the correct frame *for the geology sheet*, and the wrong one *for the minerals sheet* — that asymmetry is the actual finding.

**Known and cannot be fixed from these files**
* Neither sheet states a datum. EPSG:4326 is written on the TIFFs so GIS software will display them, **not** because it was verified.
* The geology sheet's residual accuracy is 1–2 km.
* Mineral commodity names are ~81% correct per point (a text/colour classification); counts per mineral are unreliable.

**Not suitable for**
Exploration decisions, licensing, legal boundaries, navigation, or anything at site scale. These are 1:2,000,000 regional maps.

## 6. Files

| file | what it is |
|---|---|
| `Combined_Map_v2.png` | **the combined map to look at** — geology in full colour, corrected mineral symbols on top |
| `Geology_Georeferenced.tif` | the geology sheet as a GIS layer, with caveats in its metadata |
| `Geology_Layers.zip` | the TIFF, the corrected points, and the alignment test figure, with a README |
| `Geology_Alignment_Test.png` / `.json` | the three-check evidence that the geology map needs no shift |
| `Minerals_Symbol_Points_CORRECTED.csv` / `.geojson` | 1,323 points, corrected, with old and new coordinates side by side |
| `Mineral_Registration_QC.png` | the before/after proof of the 19 km fix |
| `Niger_Benue_Alignment_Report.md` | full technical detail on the mineral correction |
| `RouteB_Report.md`, `Datum_Confirmation_Plan.md` | the datum question, and exactly how to settle it |
