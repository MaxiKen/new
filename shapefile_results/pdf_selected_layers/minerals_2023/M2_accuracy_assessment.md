# M2 boundary accuracy assessment

**Assessment date:** 2026-10-18

**Decision:** No M2 polygon geometry was changed. The existing `M2_geology_areas.shp` remains the most defensible output from the available source data; no higher-resolution or vector replacement was validated.

## What 0.68 km per pixel means

The Mineral PDF's geology background is seven raster strips, assembled to **2060 × 1677 pixels** on a 3960 × 2160 pt (55 × 30 in) page. Under the established raster-to-page and boundary-fit transforms, a source pixel represents roughly **0.67 km east–west and 0.68 km north–south** near Nigeria.

That is the raster's **sampling interval**, not a measured positional error. A pixel-grid contour has about half-pixel (roughly 0.34 km) quantization at best, before accounting for printed line width, rasterization, hatching, overprinted symbols/text, generalized map linework, or georeferencing. The raster supplies no additional spatial detail below its native sampling scale. Upsampling or writing more decimal places would not add source detail.

The local PDF contains no higher-resolution embedded M2 map-base image. The official NGSA PDF candidate was also fetched as searchable text, but that response did not expose its embedded-image dimensions or binary for a resolution comparison; it therefore does not establish a higher-resolution source.

## Cross-check against the 2011 vector geology

The existing `shapefile_results/geology/nigeria_geology_units.shp` has 1,542 polygons. I built an explicit attribute crosswalk, unioned each group, clipped it to the fixed Nigeria Admin-0 reference, projected both datasets to EPSG:6933, and compared the result with each current M2 class. `IoU` is intersection-over-union; the two coverage columns show the fraction of the 2011 group and of the M2 class, respectively, that overlap.

| M2 class | 2011 features | 2011 area (km²) | M2 area (km²) | IoU | 2011 group covered by M2 | M2 covered by 2011 group |
|---|---:|---:|---:|---:|---:|---:|
| Alluvium | 35 | 58,738 | 11,981 | 0.140 | 0.147 | 0.723 |
| Quaternary Sediments | 21 | 152,569 | 154,156 | 0.725 | 0.845 | 0.836 |
| Tertiary Sediments | 68 | 80,907 | 78,993 | 0.453 | 0.616 | 0.631 |
| Cretaceous Sediments | 223 | 165,680 | 176,043 | 0.545 | 0.727 | 0.684 |
| Younger Granite Complex | 69 | 10,942 | 9,216 | 0.170 | 0.268 | 0.318 |
| Schists | 247 | 56,482 | 22,367 | 0.117 | 0.146 | 0.368 |
| Gneiss–Migmatite–Granite Complex | 789 | 358,312 | 445,910 | 0.662 | 0.894 | 0.719 |

Crosswalk rules (all string comparisons are against the original fields):

- **Alluvium:** `code == "Al"` and `unit == "Alluvium"`.
- **Quaternary:** `rock_cls == "sedimentary"`, `period` is `Quaternary` or `Neogene-Quaternary`, excluding code `Al`.
- **Tertiary:** `rock_cls == "sedimentary"`, `period` is `Paleogene`, `Paleogene-Neogene`, or `Paleogene-Quaternary (Tertiary-Recent)`.
- **Cretaceous:** `rock_cls == "sedimentary"` and `period == "Cretaceous"`.
- **Younger Granite:** `series == "Per Alkaline young Granite Series"`.
- **Schists:** `series == "Meta - Sedimentary / Meta - Volcanic Series"`.
- **Gneiss–Migmatite–Granite:** `series` is `Migmatite - Gneiss Complex`, `Pan - African Older Granite Series`, or `Cataclastic Rocks`.

Quaternary is the strongest match, but its boundary comparison is not close enough to justify snapping or replacing boundaries: sampled boundary-distance medians are **4.57 km (2011→M2)** and **5.84 km (M2→2011)**; only **20.8% / 18.2%** of those samples are within 1 km, and the 95th-percentile distances are **38.0 / 44.8 km**. The other class matches are weaker, and the Gneiss class in M2 is itself a residual. These differences are too large to treat the 2011 polygons as a sub-pixel correction for the 2023 raster map.

## Georeferencing checks

I extracted the PDF's red `International_Boundary` vector strokes and compared them with the fixed Nigeria reference outline. At 1.2 km sampling along the PDF border, the existing local boundary-fit transform gives a median distance of **0.88 km** and a 90th percentile of **2.74 km**. Applying the PDF `/VP` affine instead gives **1.12 km** and **3.11 km**. This is an outline consistency check, not an independent accuracy measurement for every geology boundary.

A separate affine fitted only to the printed graticule labels is internally inconsistent with that border control: it moves the red PDF border to a median **12.33 km** from the reference outline (90th percentile **15.95 km**). I did not use that alternate fit to shift the M2 polygons. The established boundary-fit coordinates were retained.

## Outcome and files

- No M2 shapefile, CRS, Pegmatite points, or existing ZIP was overwritten.
- The current layer remains `M2_geology_areas.shp` with 572 valid polygons and all seven legend classes.
- The existing ZIP was not rebuilt during this assessment; this standalone report was kept outside it. The archive's current on-disk SHA-256 is `47e57ef66e7b861ba205f0d0ad3a30b9d5337ad2606ba482650d88e700540c18`, and its integrity test passes.
- A defensible boundary improvement requires a better source—such as NGSA vector geology or a verified higher-resolution map base—not a resampled copy of this raster.
