# The 437 unnamed mineral symbols — names and details

`mineral_symbols_detected.gpkg` named 886 of its 1,323 printed-symbol points and left
**437 unnamed**, because those glyphs are too small or too plain to read one at a time.
This file names them, says how much to trust each name, and describes the commodities.

Layer: **`minerals_named.gpkg`** (layer `minerals_named`, plus `minerals_named.csv`).
1,323 points, EPSG:4326, one row per printed symbol.

---

## 1. How the names were obtained

The coordinates in the old extraction were noise, but its **attributes were never in
doubt** — its reader labelled all 1,514 symbols with a colour and a printed size on this
same sheet at this same 75 dpi. Those labels are used as reference appearance samples.
Each of our glyphs is reduced to the same kind of signature:

| feature | how it is measured | why |
|---|---|---|
| body colour | the dominant saturated palette colour inside the glyph's own box | the sheet uses a fixed flat palette, so this is discrete and reliable. Sampling the box (not a fixed window) is what lets Limestone's hatched green grid read as **green** rather than as an outline |
| printed size | union bounding box of the glyph's own parts, in px | the legend glyphs are drawn ~1.25× larger, so only map-scale size is comparable |

Naming is a box kernel over the reference: count the reference symbols of each mineral
that share the colour family and fall within ±1 px in both dimensions, and take the most
common. A single median size is not enough — Limestone's glyph is a 10×10 green grid and
Marl's is also 10×10, so only the **count** of matching symbols separates 136 Limestones
from 5 Marls.

## 2. How much to trust a name

Leave-one-out over the 1,482 usable reference symbols:

**80.8 % of names are correct (1,197/1,482).** Broken down by colour family, because that
is what governs an individual name:

| colour family | accuracy | | colour family | accuracy |
|---|---|---|---|---|
| violet (Calcite) | 100 % | | blue grey (Mica, Uranium) | 78.9 % |
| khaki (Kaolin) | 99.1 % | | yellow (Clay, Gold, Glass Sand, Brine…) | 77.8 % |
| dark grey (Columbite) | 97.9 % | | outline (Beryl, Graphite, Gypsum, Baryte…) | 66.4 % |
| brown (Granite) | 97.2 % | | bright green (Lithium) | 66.7 % |
| light green (Wolframite) | 95.8 % | | tan (Zircon, Saltlake) | 50.0 % |
| purple (Talc, Garnet, Iron Ore) | 91.1 % | | orange (Fluorite) | 0 % |
| red (Marble, Feldspar, Lead-Zinc) | 90.3 % | | grey | 16.7 % |
| green (Limestone, Magnesite, Kyanite) | 87.7 % | | | |

That table is applied per glyph: `tier = probable` when its family scores ≥ 70 %,
`tentative` between 50–70 %, and **no name at all** below 50 % — a name is withheld
rather than guessed. The `family_accuracy_pct` column carries the number for each row.

## 3. The 437, named

**267 probable, 160 tentative, 10 left unidentified.**

| n | mineral | tier | family accuracy | class |
|---|---|---|---|---|
| 69 | Beryl, Aquamarine, Emerald | tentative | 66.4 % | gemstone |
| 43 | Gold | probable | 77.8 % | metallic |
| 39 | Lead-Zinc | probable | 90.3 % | metallic |
| 33 | Kaolin / kaolinitic clay | probable | 99.1 % | industrial |
| 28 | Lepidolite | probable | 90.3 % | metallic |
| 21 | Limestone | probable | 87.7 % | industrial |
| 20 | Clay / Pottery Clay | probable | 77.8 % | industrial |
| 20 | Chromite | tentative | 66.4 % | metallic |
| 19 | Glass Sand | probable | 77.8 % | industrial |
| 18 | Graphite | tentative | 66.4 % | industrial |
| 12 | Pyrite / Pyroclore | probable | 77.8 % | industrial |
| 12 | Magnesite | probable | 87.7 % | industrial |
| 11 | Talc | probable | 91.1 % | industrial |
| 10 | Marble | probable | 90.3 % | industrial |
| 8 | Kyanite | probable | 87.7 % | industrial |
| 6 | Bentonite | probable | 77.8 % | industrial |
| 6 | Coal | tentative | 66.4 % | energy |
| 5 | Brine | probable | 77.8 % | industrial |
| 5 | Tantalite | tentative | 66.4 % | metallic |
| 4 | Diatomite | probable | 87.7 % | industrial |
| 4 | Feldspar | probable | 90.3 % | industrial |
| 4 | Mica | probable | 78.9 % | industrial |
| 4 | Granite | probable | 99.1 % | industrial |
| 4 | Gypsum | tentative | 66.4 % | industrial |
| 4 | Psammite | tentative | 66.4 % | industrial |
| 3 | Wolframite | probable | 95.8 % | metallic |
| 2 | Garnet | probable | 91.1 % | gemstone |
| 2 | Columbite | probable | 97.9 % | metallic |
| 2 | Tourmaline | probable | 90.3 % | gemstone |
| 2 | River Gravel | probable | 91.1 % | industrial |
| 1 each | Zircon, Iron Ore (Magnetite, Ilmenite), Manganese | probable | ≥ 87.7 % | — |
| 1 each | Lignite, Corundum/Sapphire/Ruby, Oil and Gas, Silica Sand | tentative | 50–66 % | — |
| 10 | *unidentified* | — | < 50 % | 7 bright green, 1 orange, 1 tan, 1 green |

The 10 withheld are glyphs whose colour family cannot be resolved at this resolution;
they keep their measured colour and no mineral name.

## 4. Details of each commodity

Class, and what the commodity is, are in the `mineral_class` and `details` columns of the
layer. Summary of what the 437 turned out to be:

* **Metallic (164):** Gold 43, Lead-Zinc 39, Lepidolite 28, Chromite 20, Tantalite 5,
  Wolframite 3, Columbite 2, plus Iron Ore, Manganese.
* **Industrial (188):** Kaolin 33, Limestone 21, Clay 20, Glass Sand 19, Graphite 18,
  Pyrite 12, Magnesite 12, Talc 11, Marble 10, Kyanite 8, Bentonite 6, Brine 5,
  Diatomite 4, Feldspar 4, Mica 4, Granite 4, Gypsum 4, Psammite 4, River Gravel 2,
  Zircon, Silica Sand.
* **Energy (7):** Coal 6, Lignite 1.
* **Gemstone (75):** Beryl/Aquamarine/Emerald 69, Garnet 2, Tourmaline 2,
  Corundum/Sapphire/Ruby 1.

## 5. What this does *not* fix — read before computing

Naming a glyph is not the same as counting its commodity. The two methods' per-mineral
totals diverge, and the divergence is diagnostic:

| mineral | extraction total | this layer | reading |
|---|---|---|---|
| Clay / Pottery Clay | 178 | 178 | agrees exactly |
| Kaolin | 109 | 235 | **over-called** — khaki glyphs are over-detected, or some are being misread as khaki |
| Gold | 114 | 148 | over-called by ~30 % |
| Limestone | 136 | 30 | **under-detected** — the hatched green grid glyph is the one my detector most often misses |
| Marble | 53 | 11 | under-detected |
| Gypsum | 38 | 7 | under-detected |
| Granite | 38 | 6 | under-detected |
| Baryte | 31 | 0 | not detected at all |

So: **per-symbol names are ~81 % accurate, but per-mineral totals are not reliable yet.**
The shortfall is the same one already recorded — this detector finds 1,323 of the ~1,531
symbols, and the missing ~200 are concentrated in exactly the small, plain glyphs
(Limestone, Marble, Gypsum, Granite, Baryte) that fail both detection and naming.

If you need commodity totals for calculation, take them from the extraction's `mineral`
column — which is sound — and use this layer only for **where** each symbol is. **Filter
that column on `is_symbol = 1` first.** It holds 1,609 rows, and 120 of them are not a
countable symbol: 56 raster slivers, 21 state-capital squares, 8 linework/label fragments,
5 bridge or water markings, 5 merged clusters, 15 fragments and 8 halves of a symbol that is
already counted as its own row, and 2 merged touching pairs. Unfiltered, `value_counts()` reports
a phantom commodity called `not a mineral symbol: raster sliver` with 56 members and
inflates the real ones. On the 1,489 rows that are symbols the totals are, for example,
Limestone 136, Clay 174, Gold 112, Kaolin 109.
