# Nigeria geology polygon layer

## Deliverables

- **`nigeria_geology.gpkg`** — polygon GeoPackage in **EPSG:4326**.
  - Main layer: `nigeria_geology`
  - Geometry: `MultiPolygon`
  - Feature count: **86**
  - Unique `name` values: **86**
  - A default QGIS categorized style is embedded in the GeoPackage.
- **`nigeria_geology.qml`** — companion QGIS style, in case a GIS does not automatically load the embedded style.
- **`nigeria_geology_preview.png`** — visual quality-control preview.
- **`data/legend.csv`** — the 86 transcribed legend entries and source colours.

## Legend count

The source image contains **86 legend entries**. They occur in five layout blocks containing 17, 17, 20, 15, and 17 entries:

`17 + 17 + 20 + 15 + 17 = 86`

No names outside those 86 entries are used. The `name` attribute preserves the spelling and capitalization visible in the source legend, including apparent source typos.

## Layer fields

| Field | Description |
|---|---|
| `legend_id` | Alphabetical source-legend position, 1–86 |
| `name` | Legend text transcribed from the supplied image |
| `color_hex` | Source legend swatch colour |
| `area_km2` | Equal-area measurement in EPSG:6933 |
| `source` | Provenance note |

Each legend category is stored once as a multipart polygon. This keeps the attribute table to exactly 86 rows while preserving all disconnected occurrences.

## Construction and quality controls

1. The map was calibrated from its printed graticule: 4°, 8°, and 12° E and 6°, 10°, and 14° N.
2. The 12 printed swatch colours were sampled and used to classify the map pixels.
3. Graticule and cartographic ink were suppressed and filled from surrounding geology.
4. Categorical contacts were bicubically interpolated at 3× source resolution, lightly smoothed, and simplified as a **shared polygon coverage**. Shared-edge simplification avoids independent outlines that could create cracks or overlaps.
5. The coverage was clipped to the Natural Earth 1:10m Nigeria boundary, giving a clean national outline instead of a pixel-stepped edge.
6. Every part of the national polygon was assigned to a geology polygon. Validation found:
   - uncovered area: **0**
   - area outside Nigeria: **0**
   - overlap from duplicated polygon area: below `3 × 10⁻13` square degrees (floating-point noise)
   - invalid geometries: **0**
7. The final bounds are `2.671082° E, 4.272162° N, 14.669936° E, 13.880291° N`.

## Interpretation note

The image cycles only **12 colours across 86 legend names**, so colour alone does not uniquely identify a name. Exact recovery of every original category is mathematically impossible from this raster without its source GIS dataset. Names sharing a colour were therefore allocated using polygon position, size, shape, and the known broad geology of Nigeria: the Sokoto, Chad, Bida/Nupe, Benue, Anambra, and coastal basins; the southwest and north-central basement; and the Jos volcanic/ring-complex region. This is a carefully placed raster interpretation, not a substitute for an authoritative NGSA vector dataset or field-scale mapping.

The appropriate working scale is the source map's national scale (approximately 1:2,000,000), not parcel or site investigation scale.

## Sources

- Supplied raster: `pic geology of nigeria.png`
- Nigeria boundary: Natural Earth, `ne_10m_admin_0_countries` (public domain), downloaded from the [Natural Earth vector repository](https://github.com/nvkelso/natural-earth-vector)
- Geological placement references: [Nigerian Geological Survey Agency — Geological Mapping](https://ngsa.gov.ng/geological-mapping/) and [Litho-structural Map of Nigeria](https://ngsa.gov.ng/litho-structural-map-of-nigeria/)

## Rebuild

With the Python dependencies installed:

```bash
python scripts/explore_segmentation.py
python scripts/create_geology_gpkg.py
```
