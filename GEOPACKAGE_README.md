# What is in `Nigeria_Geology_Minerals_4326.gpkg`

One GeoPackage, everything EPSG:4326, built by `Build_GeoPackage.py` and checked by
`Validate_GeoPackage.py` (**18 of 18 checks pass** — see `GeoPackage_Validation.json`).

Open it in QGIS: drag the file in, and pick layers from the list. Rasters appear when you
select them in the "Select raster layers" dialog.

## Layers

| layer | type | what it is | resolution |
|---|---|---|---|
| `minerals_symbols` | points | 1,323 printed mineral symbols, each at the centre of its printed glyph, with commodity **name**, **class**, confidence **tier** and confidence value | point |
| `ref_geology_2011` | raster | the 2011 geological sheet as drawn, registered on its printed graticule | 0.01° ≈ 1.1 km |
| `ref_minerals_2023` | raster | the 2023 mineral sheet as drawn, registered on its embedded frame | 0.01° ≈ 1.1 km |
| `combined_map` | raster | the two sheets overlaid | 0.01° ≈ 1.1 km |
| `mineral_density_all` | raster | interpolated density of all printed symbols | 0.01°, σ = 0.15° ≈ 17 km |
| `mineral_density_metallic` | raster | same, metallic only (338 symbols) | " |
| `mineral_density_nonmetallic` | raster | same, industrial + gemstone + energy (967 symbols) | " |
| `nigeria_boundary` | polygon | Natural Earth 1:10m outline, for reference and clipping | — |
| `alignment_checks` | points | the ten measurements behind every registration decision, as numbers with meanings | — |
| `dataset_notes` | table | eight plain-language notes, including what the file must not be used for | — |

Every raster carries tags giving its registration, its resolution, the reason it was placed
that way, and an explicit "not for" line. Those travel with the data, so a future user cannot
silently inherit a wrong assumption.

## The mineral points are as accurate as this sheet allows

Three separate errors were found and fixed, and the fixes are independently verified:

1. **The art strips are stored vertically flipped.** The seven 75 dpi strips holding all the
   symbol artwork are drawn flipped on the page. Reading them naively mirrored every recorded
   latitude about its strip axis — tens of kilometres, in both directions, with no pattern.
   Verified fix: symbols detected on the page now land on the same symbols in the artwork
   **100%** of the time, against **1%** for random positions (`/tmp` check in the build log;
   reproducible with `Rebuild_Symbol_Centres.py`).
2. **The printed graticule is 19 km west of the frame the artwork uses.** Proven by the sheet's
   own vector international border: it matches modern boundary data to **0.5–1.1 km** using the
   embedded GeoPDF measure, but is **12.9 km** out using the printed grid.
3. **Points sat inside glyphs but not at their centres.** Each point is now snapped to the
   centre of the printed glyph it belongs to, using the native artwork with hole-filling so
   ring and outlined symbols are measured whole.

**Independent verification** (`Verify_Centres.py`, which does not reuse any of the build's
coordinates — it re-renders the page at 4 px/pt and re-detects the glyphs):

| check | result |
|---|---|
| points landing on a detected glyph | **97.8%** |
| median distance from point to glyph centre | **0.44 km** (0.62 pt) |
| within 1 pt (0.7 km) | 73.9% |
| within 2 pt (1.4 km) | 94.3% |

A visual proof sheet of eight random points, drawn on the real page, is in
`Symbol_Centre_Proof.png`. The crosshair is the point; the symbol under it is the mineral.

## The density surface

Gaussian kernel, σ = 0.15° (≈17 km), one unit contribution per symbol, converted to
**symbols per 1000 km²**, masked to Nigeria with −9999 outside. It integrates back to ~1,029
symbols against 1,179 inside the border — the shortfall is coastline clipping, and this is
asserted as a test rather than assumed.

**Read it as**: how densely the *printed symbols* cluster. Not reserves, not grade, not
production, not economic viability. Clustering partly reflects real geology and partly
reflects where the survey looked. Commodity names are ~81% correct per point, so the class
split is indicative only.

## Deliberately downsampled

The reference rasters are 0.01° (about 1.1 km) per pixel — coarse on purpose, as you asked,
because they are for confirming the work, not for measuring from. The full-resolution geology
raster remains available as `Geology_Georeferenced.tif` if you need it.

## The honest limits, stated once more

* **Datum not established** for either sheet. EPSG:4326 is the display frame. Minna → WGS 84
  moves Nigeria about 0.09 km, which is below what these sheets can resolve.
* **Geology needs no correction**: its state boundaries, rivers and coastline all sit within
  1–3 km of independent reference data, and the best-fit shift (0.9 km) is below one and a half
  map pixels. Applying it would be fitting noise.
* **Commodity names** are 80.8% correct overall (leave-one-out). Use the `tier` and
  `confidence` columns per point; per-mineral counts are unreliable.
* **Not for** surveying, licensing, legal boundaries, navigation, or site-scale decisions.

## Reproducing it

```
Rebuild_Symbol_Centres.py    # re-measures symbol centres from the native artwork
Verify_Centres.py            # independent page-render check + proof sheet
Build_GeoPackage.py          # builds the .gpkg
Validate_GeoPackage.py       # 18 assertions on the finished file
Render_Final_Maps.py         # draws the two preview maps from the .gpkg itself
```
