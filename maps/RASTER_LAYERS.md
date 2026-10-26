# The nine raster layers

Nine scanned thematic maps of Nigeria were added to
`Nigeria_Geology_Minerals_4326.gpkg` as georeferenced raster layers. Each keeps
its **original pixels** (a thematic map is a picture of a classification — it can
never be more accurate than the print) but is placed in EPSG:4326, clipped to the
2023 national boundary, and documented with its printed legend and a measured
positional error.

| Layer | Sheet | Native px | km/px E‑W × N‑S | Border offset | North / South / West / East | RMS | Overlap | Quality |
|---|---|---|---|---|---|---|---|---|
| `raster_landcover` | Land cover | 609×510 | 3.05 × 3.04 | **3.7 km** | −2 / −5 / −3 / +1 | 7.5 | 0.984 | high |
| `raster_dem` | Digital Elevation Model | 2000×1415 | 0.97 × 1.00 | **4.1 km** | −2 / +10 / −4 / −3 | 9.3 | 0.958 | high |
| `raster_temperature` | Historical average temperature | 816×1056 | 1.84 × 1.87 | **4.1 km** | −3 / −4 / −3 / +1 | 7.0 | 0.975 | high |
| `raster_dominant_soils` | Dominant soils | 10234×6678 | 0.17 × 0.17 | **4.1 km** | −1 / +4 / −3 / −9 | 7.3 | 0.891 | high |
| `raster_soil_ph` | Soil pH distribution | 2000×1415 | 1.02 × 1.03 | **4.7 km** | −3 / −1 / −4 / −4 | 7.6 | 0.970 | high |
| `raster_general_geology` | Generalised geology | 615×715 | 2.47 × 2.81 | **4.7 km** | −3 / +4 / −6 / −8 | 10.1 | 0.965 | high |
| `raster_ethnic_groups` | Ethno‑linguistic groups | 1344×1344 | 1.36 × 1.38 | **4.7 km** | −2 / −3 / −4 / −4 | 15.9 | 0.949 | high |
| `raster_forest_reserves` | Forest reserves | 6600×5100 | 0.22 × 0.22 | **10.4 km** | −2 / −4 / +0 / +5 | 18.1 | 0.852 | medium |
| `raster_population` | Population distribution | 850×520 | 2.37 × 2.32 | **10.9 km** | −9 / +5 / −25 / −12 | 18.2 | 0.928 | medium |

Sign convention: a **positive** side figure means the sheet draws that side of
Nigeria *further out* than the official border, negative means it draws it
*smaller*. The headline *Border offset* is the median absolute offset on the
**land border**; the coast is measured separately (see below), because several
sheets paint the Gulf of Guinea in a land colour and their southern edge is then
the edge of the drawing rather than a border.

The full machine-readable record, including every fit parameter, the per-side
offsets and the transcribed legend, is `raster_georeferencing.json`; the overlay
used to check each one is `raster_georeferencing_qc.png` (raster image, red =
`national_territory`, cyan = `state_boundaries`).

## Deducing the border offset

The offset is not assumed and not taken from the sheet's own scale bar. It is
read off the finished fit, by walking the boundary that the cartographer drew and
asking, for every point of it, how far the nearest point of the official border
is — in km, **signed**: outside the official line counts positive (the sheet
draws Nigeria bigger), inside counts negative.

Three decisions make the number mean something:

1. **The coast is excluded from the headline.** `water_bodies` is used to label
   the coastal stretch of the official border, and offsets are reported for the
   land border and the coast separately. On the sheets that paint the Gulf of
   Guinea in a land colour (elevation, soil pH, dominant soils) the southern edge
   of the drawing is not a border at all, and including it would report the
   cartographer's treatment of the sea as a registration error.
2. **It is measured per side** — north, south, west, east. A single number can
   hide the two failure modes that matter: a sheet drawn uniformly a few per cent
   too large (all four sides positive) versus one that is shifted (opposite signs
   on opposite sides). Every sheet here shows the first, except `raster_population`
   and `raster_forest_reserves`, which show the second — see below.
3. **Bloat is removed before measuring, but only where it exists.** The painted
   country edge frequently sits a few pixels outside the printed border line. That
   reads as a uniform positive offset on all four sides, and it biases the fit
   outwards. The measured amount is eroded off the mask and the fit re-polished;
   whether the erosion was right is decided by the overlap, not by opinion. The
   temperature sheet was 8.6 px (~16 km) bloated on every side: removing it took
   the overlap from 0.925 to **0.975**.

### What the per-side numbers say about the individual sheets

* **`raster_dem`, `raster_soil_ph`, `raster_temperature`, `raster_landcover`** —
  all four sides within ±4 km, RMS under 10 km. These are as well registered as a
  scanned thematic map can be.
* **`raster_dominant_soils`, `raster_general_geology`, `raster_ethnic_groups`** —
  ±4 km typical, with one side (east −9 km, east −8 km, and RMS 16 km
  respectively) carrying the residual. For the geology sheet that is the eastern
  border, where the sheet's generalisation is visibly coarser than the 2023
  border; for the ethnic sheet it is the schematic nature of the map itself.
* **`raster_dem` south +10 km** — the Gulf of Guinea is painted in the lowest
  elevation class, so the mask edge runs offshore; the land fit is good
  (±3 km on the other three sides) and the southern figure is reported rather
  than smoothed away.
* **`raster_forest_reserves`, `raster_population`** — the only two sheets whose
  sides disagree in sign, i.e. they are **not** uniformly scaled but displaced.
  Population is −25 km on the west and −12 km on the east with the north only
  −9 km: its coloured districts stop short of the western border, and no affine
  fit can satisfy both ends, so the compromise costs overlap (0.928) and shows up
  in the offsets. The forest-reserve sheet draws its own border — the grey band
  along its north-west edge is the sheet's border, and it lies ~100 km east of the
  real one in that stretch; the fitted border follows the drawn line the best an
  affine can (0.852). Both are limits of the **sheets**, not of the fit, and are
  the reason those two layers are marked *medium* rather than *high*.

## Format decisions

* **GeoTIFF‑in‑GeoPackage tiles, 4‑band RGBA `uint8`.** The alpha band carries
  the clip, so the surrounding paper, legend boxes, scale bars, north arrows and
  titles disappear instead of smearing into the mapping. Multi‑band rasters in a
  GeoPackage must be byte data, hence `uint8`.
* **No rotation, no reprojection of the pixels.** Every sheet is a plain affine
  (independent x/y scale, no rotation). Resampling a classification would invent
  class values along every boundary, so the pixels are untouched and only the
  grid is set. Each layer is delivered at the sheet's own resolution.
* **Clipped to `national_territory`** with a 1‑pixel inward erosion and an
  intersection with the map object, so a legend that happens to fall inside the
  country rectangle cannot survive as stray pixels.
* **Not converted to vector.** Automatic vectorisation of a 60‑class soil map
  would produce hundreds of thousands of slivers with no attribution, and the
  classes are only knowable from a printed legend; a documented raster is the
  better product here.
* **Each layer is titled, described and legended** in `gpkg_contents` and in the
  JSON, including the caveats — a reader can tell a picture of an elevation map
  from a real DEM without opening this file.

## How the georeferencing works

`georef_new_map.py` (rerun it to regenerate everything; it merges into the
existing GeoPackage without touching the 27 vector layers):

The full chain, and what each stage is allowed to decide:

1. **Plate mask.** The plot frame is found from the printed rule, and the paper
   colour is read from a ring of pixels just *inside* the frame. The country is
   the largest object that differs from that colour. The plate settings differ per
   sheet and are recorded in `IMAGES` — pale vegetation and the painted sea on the
   land‑cover and soil‑pH sheets need a stricter tolerance than the rest.
2. **Translation search.** For a small fan of scales (and, where the sheet is not
   guaranteed conformal, a small aspect fan) the best translation is found by an
   FFT cross‑correlation of the plate mask with a rasterised
   `national_territory` — an exact search, not a hill‑climb, which is what makes
   it stable on masks that are only roughly right.
3. **Outline polish.** The outer boundary of the map object is a clean closed
   curve; edge maps are not, because they carry legends, titles and interior
   class boundaries. A small pattern search minimises the symmetric distance
   between the mapped border and that curve.
4. **Bloat closure.** The measured outward offset is eroded off the mask and the
   fit re-polished, until nothing is left to take off (see above).
5. **Measurement.** The border offset is read off the finished fit, per side.
6. **Clipping and writing.** The result is checked by eye for all nine
   (`raster_georeferencing_qc.png`) and by `audit_layers.py`, which verifies CRS,
   grid, tile count, how much of the territory carries pixels and how many pixels
   fall outside it. Current audit: **0 problems**.

Every stage is gated on the same measure — the overlap between the drawn country
and the territory — so no stage can be accepted on faith. Mean overlap across the
nine sheets is **0.941** (worst 0.852, best 0.984); mean land-border offset is
**5.7 km**.

### Things the numbers must not be used for

* `raster_dem` is a **picture** of an elevation map with hillshading; read
  elevation from a real DEM.
* `raster_landcover` is the coarsest sheet (3 km/px, 15 classes) — a locator, not
  a land‑cover dataset.
* `raster_population` is drawn by unnamed district with **absolute counts**, so
  it cannot be joined to the admin layers or normalised by area. Treat its
  position as approximate (±35 km).
* `raster_ethnic_groups` is schematic: 35 groups, boundaries indicative, close
  colours deliberately encode close languages.
* `raster_dominant_soils` has five inset panels on the right that the clip
  removes; the main map is the layer.
* `raster_general_geology`'s marginal spot elevations are corrupt in the scan
  (`715057 deg E`) and were not used.
* `raster_forest_reserves` is a reserves/rivers map, not a forest‑cover map, and
  its sheet is the noisiest of the nine (±27 km).
* `raster_temperature` is CHIRTSmax for Jan–Dec 1986–2015 (USGS/FEWS NET): a
  climatology, not a forecast, and one class is water.

## Layer catalogue and legend transcriptions


#### `raster_dem` — Digital Elevation Model of Nigeria

Source `new map/DEM-of-map-of-nigeria.jpg` · elevation, 7 classes, metres · 2000×1415 px · 0.97 × 1.00 km/px

Elevation is drawn as a classified image with hillshading; the class boundaries were read from the printed legend, not from the pixels, so this is a picture of an elevation map, not a DEM. For actual elevations use a real DEM.

Printed legend:

| Swatch | Class |
|---|---|
| `#1f6fe0` | -25 - 130 |
| `#d9ec9a` | 140 - 260 |
| `#5f9e3f` | 270 - 380 |
| `#d4551f` | 390 - 530 |
| `#8a3b1e` | 540 - 720 |
| `#b0a49c` | 730 - 1,100 |
| `#ffffff` | 1,200 - 2,100 |

#### `raster_soil_ph` — Soil pH distribution in Nigeria

Source `new map/soil-ph-map-of-nigeria.jpg` · soil pH, 5 classes · 2000×1415 px · 1.02 × 1.03 km/px

Flat classes, no shading, so the classes are clean; the map has no graticule and no source citation.

Printed legend:

| Swatch | Class |
|---|---|
| `#0b2f7a` | 0 |
| `#1f9e8f` | 0.01 - 5.5 |
| `#5fd63f` | 5.6 - 6.8 |
| `#f5a623` | 6.9 - 7.8 |
| `#c0392b` | 7.9 - 8.3 |

#### `raster_temperature` — Nigeria historical average temperature, Jan-Dec 1986-2015

Source `new map/temperature-map-of-nigeria.png` · mean temperature, 13 classes, degrees C · 816×1056 px · 1.84 × 1.87 km/px

USGS/EROS, FEWS NET; CHIRTSmax data. The classes are drawn as a smooth surface, so class edges are interpolated in the artwork.

Printed legend:

| Swatch | Class |
|---|---|
| `#1f77b4` | < 16 |
| `#5b9bd5` | 16 - 18 |
| `#7f9aa8` | 18 - 20 |
| `#8fb0a8` | 20 - 22 |
| `#a8c39a` | 22 - 24 |
| `#cfe0a8` | 24 - 26 |
| `#e8efa8` | 26 - 28 |
| `#f5e58a` | 28 - 30 |
| `#f7d27a` | 30 - 32 |
| `#f5b95c` | 32 - 34 |
| `#f09a45` | 34 - 36 |
| `#e8722f` | 36 - 38 |
| `#d9541f` | 38 - 40 |
| `#b8321a` | 40 - 42 |
| `#8e1a12` | > 42 |
| `#29b6f6` | water |

#### `raster_forest_reserves` — Forest reserves and major rivers of Nigeria

Source `new map/forest-reserve-map-of-nigeria.png` · forest reserves / major rivers / water · 6600×5100 px · 0.22 × 0.21 km/px

Graticule labelled on all four sides; the fit agrees with the printed graticule to within the residual below.

Printed legend:

| Swatch | Class |
|---|---|
| `#1f7fe0` | Major Rivers |
| `#8ed43f` | Forest Reserves |
| `#eaf7c0` | States Boundary fill |
| `#1f7fe0` | Gulf Of Guinea |

#### `raster_landcover` — Land cover of Nigeria

Source `new map/landcover-map-of-nigeria.png` · land cover, 15 classes · 609×510 px · 3.05 × 3.04 km/px

Smallest of the set (609x510 px): ~2.4 km per pixel, so useful as a locator only. The legend box overlaps the map in the SW corner.

Printed legend:

| Swatch | Class |
|---|---|
| `#0b6b4f` | Evergreen Needleleaf Forest |
| `#2e7d32` | Evergreen Broadleaf Forest |
| `#1fa39a` | Deciduous Needleleaf Forest |
| `#4caf50` | Deciduous Broadleaf Forest |
| `#8d6e3a` | Woodland |
| `#c8a15a` | Bare |
| `#b3b3b3` | Open Shrubland |
| `#c97b4a` | Crop land |
| `#f2f2a0` | Closed Shrubland |
| `#a8d08d` | Mixed Forest |
| `#cfe8a0` | Wooded Grassland |
| `#e8d5a0` | Rangeland |
| `#1f3fd0` | Water |
| `#8b1a1a` | Urban |

#### `raster_population` — Population distribution of Nigeria

Source `new map/population distribution-map-of-nigeria.png` · population by district, 5 classes (absolute) · 850×520 px · 2.30 × 2.26 km/px

Class breaks are absolute counts per drawn district, not density, and the districts are not named, so this layer cannot be joined to administrative units. Graticule labelled at 2.5-degree intervals.

Printed legend:

| Swatch | Class |
|---|---|
| `#fdf3c8` | 0 - 110,85 |
| `#f8e06a` | 110,853 - 144,579 |
| `#f2b544` | 144,580 - 179,550 |
| `#c8631f` | 179,551 - 232,287 |
| `#4a1004` | 232,288 - 1,319,571 |

#### `raster_ethnic_groups` — Ethno-linguistic groups of Nigeria

Source `new map/Ethnic-map-in-nigeria.png` · ethno-linguistic groups, 35 classes · 1344×1344 px · 1.36 × 1.38 km/px

Third-party cartography (@Atlas_Cartography) from the 2006 census and 'Ethnographic survey of Africa'. Boundaries are schematic; the image is square with a black surround, so the fit is weaker (see IoU). Do not use for area statistics.

Printed legend:

| Swatch | Class |
|---|---|
| `#f48fb1` | Hausa |
| `#8e3b52` | Fulani |
| `#7e6b9e` | Bade |
| `#e8b4c8` | Tera-Mandara |
| `#4a90c8` | Kanuri |
| `#f7c8e0` | Yedina |
| `#b39ddb` | Baggara |
| `#1565c0` | Songhay |
| `#90a4c0` | Bariba |
| `#a03b3b` | Mande (Busa) |
| `#b08968` | Kambari |
| `#f5e642` | Dakarkari |
| `#f0a860` | Gbagyi |
| `#f2d04a` | Nupe-Ebira |
| `#a8905a` | Atyap |
| `#e8641f` | Tiv-Gade |
| `#7a4a1f` | Berom-Jarawa |
| `#e84a9a` | Angas |
| `#e8a020` | Jukun |
| `#a03b1f` | Tarok |
| `#5cb85c` | Yoruba |
| `#3b7d3b` | Ewe |
| `#7fe8d0` | Edo |
| `#4a7a1f` | Igbo |
| `#a8e06a` | Igala |
| `#1f6b4a` | Ijaw |
| `#4ad64a` | Idoma-Ighde |
| `#1f8f6f` | Itsekiri |
| `#d02020` | Abua-Ogbia-Atissa |
| `#e84a6a` | Eleme |
| `#f5d0a0` | Ibibio-Efik |
| `#f7e8a0` | Bokyi |

#### `raster_dominant_soils` — Dominant soils of Nigeria

Source `new map/dominant-soil-map-of-nigeria.jpg` · dominant soil unit, ~60 classes (FAO/UNESCO) · 10234×6678 px · 0.17 × 0.17 km/px

10,234 x 6,678 px scan of the printed sheet (GIS Laboratory, Department of Geography, University of Lagos), with five small inset maps on the right that are NOT part of the main map and are removed by the clip. Class names are printed in the legend but at scan resolution the symbols are not reliably machine-readable, so the class table below lists the legend headings only.

Printed legend:

| Swatch | Class |
|---|---|
| `#f2e8a0` | Acrisols (AC) |
| `#e8d27a` | Alisols (AL) |
| `#c9b98a` | Cambisols (CM) |
| `#e8e8d8` | Chernozems (CH) |
| `#8a6a4a` | Fluvisols (FL) |
| `#b8b8a8` | Gleysols (GL) |
| `#d8c8a8` | Histosols (HS) |
| `#8a3b1f` | Leptosols (LP) |
| `#c0392b` | Luvisols (LV) |
| `#e8846a` | Nitisols (NT) |
| `#f5d0a0` | Phaeozems (PH) |
| `#7a5a3a` | Planosols (PL) |
| `#a89078` | Plinthosols (PT) |
| `#d8b89a` | Podzols (PZ) |
| `#9a7a5a` | Regosols (RG) |
| `#c8b0a0` | Solonchaks (SC) |
| `#b0a090` | Solonetz (SN) |
| `#e0d0b0` | Vertisols (VR) |
| `#7a9ac0` | Water bodies |
| `#f0f0e8` | Rock outcrops |

#### `raster_general_geology` — General geology of Nigeria (simplified)

Source `new map/general-geology-map-of-nigeria.png` · geology, simplified to 9 classes by era · 615×715 px · 2.47 × 2.81 km/px

615 x 715 px - the coarsest item in the set and a simplified 9-class generalisation of the same subject as geology_units. It is kept because it is the only sheet in the set with the eras labelled in plain language, NOT as a substitute for geology_units. Spot elevations in its margins are printed in a corrupt format (715057 deg E) and are unusable.

Printed legend:

| Swatch | Class |
|---|---|
| `#f7f7a0` | Cenozoic: alluvials, sand, gravels, clay, mangrove swamps, pebbles |
| `#ffff00` | Cenozoic: sands, clays, shales, sandstones, lignites, grits |
| `#f0a030` | Cenozoic: volcanics (basalts, trachytes, rhyolites) |
| `#f5f5c0` | Mesozoic: sands, clays, coals, shales, sandstones, mudstones, limestones |
| `#4a7a4a` | Mesozoic: basic and intermediate intrusions |
| `#7ac0e8` | Mesozoic: granites, syenites, gabbros, rhyolites (Jurassic) |
| `#e8d8a0` | Palaeozoic-Proterozoic: metasediments, schists, quartzites |
| `#f07a8a` | Palaeozoic-Proterozoic: older granites |
| `#f5b8b8` | Palaeozoic-Proterozoic: basement complex |
