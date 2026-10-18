# Nigeria online GIS layers

This bundle contains the requested Nigeria GIS layers as ESRI Shapefiles, plus a source crosswalk and QA report. The fixed reference at `shapefiles/nigeria_admin0/` was **not modified**. All output coordinates are WGS 84 / EPSG:4326. No PDFs or PDF-derived features were used.

## Contents

| Layer | Features | Source and vintage | License | Notes |
|---|---:|---|---|---|
| `state_boundaries/` | 37 polygons | Natural Earth 10m Admin-1, v5.1.1 | Public domain | 36 states + FCT; matches the fixed Natural Earth reference very closely. |
| `senatorial_districts/` | 109 polygons | OCHA Nigeria COD-AB, v01; valid 2019-04-17 | CC BY-IGO | Official COD-AB senatorial-district layer; source geometry retained. |
| `lga_boundaries/` | 774 polygons | geoBoundaries / GRID3, representative year 2022 | CC BY 4.0 | Current LGA geometry source used here; its attributes include name and level. |
| `river_lines/` | 35 lines | Natural Earth 10m rivers, v5.1.1 | Public domain | Generalized major-river centerlines, clipped to the fixed reference; not a complete river network. |
| `road_lines/` | 4,708 lines | HDX Nigeria Road Network; data period 2023-10-27 | CC BY (HDX) | GitHub mirror whose schema and bounds match HDX metadata; exact file hash could not be compared to HDX. |
| `rail_lines/` | 1,429 lines | OpenStreetMap/OEX Nigeria snapshot, 2026-09-06 | ODbL 1.0 | Line geometries only; station points and railway polygons are not included. |
| `state_capitals/` | 37 points | GeoNames coordinates; state/capital names from a state list | CC BY 4.0 for coordinates; MIT for names | One matched capital per state/FCT; all points fall within the fixed reference. |
| `towns/` | 927 points | GeoNames `cities.json` v1.1.65, published 2026-10-01 | CC BY 4.0 | Smaller GeoNames subset retained for comparison; not exhaustive; 11 points outside the fixed reference are flagged. |
| `populated_places/` | 22,004 points | SafeSignal-Geo v0.2.0; OSM-derived records categorized as `settlement` | ODbL 1.0 | Dense layer, about 23.7× the GeoNames comparison layer; 21,352 inside and 652 outside the fixed reference (`IN_REF`). |
| `grid3_settlement_names_source/` | — | GRID3 NGA Settlement Names public ArcGIS Feature Service; source reports 292,438 points | CC BY 4.0 | **Source pointer and downloader only; no GRID3 point files are bundled yet.** The existing `populated_places/` layer is preserved. |
| `codab_lga_senatorial_crosswalk.csv` | 774 rows | OCHA Nigeria COD-AB ADM2 attributes | CC BY-IGO | Links OCHA LGA names/p-codes to the OCHA senatorial district name/p-code. It is not a direct join table for the GRID3 LGA geometries. |

See `sources.json` for detailed source URLs, licenses, versions, and mirror notes. See `validation.json` for per-layer counts, CRS checks, geometry checks, bounds, and reference overlays. `SHA256SUMS.txt` lists the deliverable file checksums (excluding itself).

The `grid3_settlement_names_source/` directory records GRID3's separate 292,438-point Settlement Names source and includes a downloader for an environment with access to its public ArcGIS host. **It currently contains no GRID3 geometry or Shapefile.** This sandbox can inspect the service metadata but cannot retrieve its data payload; the older `towns/` and `populated_places/` layers remain intact. See that directory's README for the service URL, license, and retrieval instructions.

## Reference alignment and QA

The comparison reference is `shapefiles/nigeria_admin0/nigeria_admin0.shp` (one valid WGS 84 polygon; approximately 907,499.58 km² in the local equal-area comparison projection). Polygon overlay areas below use a Nigeria-centered Albers equal-area projection; source files themselves remain in EPSG:4326.

- **State polygons:** 37/37 valid. Their union differs from the fixed reference by about **0.0057 km²** (about 5,652 m²), effectively aligned at this scale.
- **GRID3 LGA polygons:** 774/774 valid. Union symmetric difference is about **8,517.93 km²**: about 6,765.52 km² outside the reference and 1,752.42 km² of reference area uncovered. The source boundaries were not clipped, snapped, or repaired.
- **OCHA senatorial polygons:** 109/109 valid and 109 unique district names/codes. Union symmetric difference is about **8,307.73 km²**: about 5,278.85 km² outside the reference and 3,028.88 km² of reference area uncovered. The 109 polygons agree with the union of the source OCHA COD-AB ADM2 polygons to within about 143 m², but do not exactly match the fixed Natural Earth reference.
- **Roads:** all 4,708 source lines are valid; about **0.280%** of total line length lies outside the fixed reference.
- **Railways:** all 1,429 source lines are valid; 1,427 intersect the reference and about **0.118%** of total line length lies outside it.
- **Rivers:** the 35 Natural Earth features are clipped to the fixed reference. They are generalized 1:10m centerlines and omit many smaller watercourses; use a more detailed, properly licensed network for hydrologic analysis.
- **State capitals:** 37 valid points, all inside the reference.
- **GeoNames comparison towns:** 927 valid points across all 37 state/FCT codes; 916 lie inside the reference and 11 do not. The existing `towns/` layer is unchanged and retains/flags all source records.
- **Dense populated places:** 22,004 valid OSM-derived settlement points from the SafeSignal-Geo v0.2.0 bundled gazetteer. 21,352 lie inside the fixed reference and 652 do not; all are retained and the `IN_REF` field marks coverage. All selected rows have unique OSM source IDs (`osm:node/<id>` or `osm:way/<id>`); 367 records share a coordinate with another source feature, and 688 have source `STATE=Unknown`. Treat the state/LGA attributes as source labels, not authoritative boundary joins. OpenStreetMap completeness is variable; this is not a census or exhaustive inventory.

For `populated_places.shp`, `SOURCE` preserves each OSM object ID, `LICENSE` records its row-level license, and `ALIASES` carries the package's semicolon-separated alternate names. `POP_SCORE` is the package's popularity/tie-break score, **not a population count**; `LAT`/`LON` mirror the point geometry, and `IN_REF` is `Y` or `N`.

No source boundary was snapped to the fixed reference. The area differences are documented rather than hidden. In particular, do **not** assume that the GRID3 LGA layer and OCHA senatorial layer share identical boundary vintages.

## Senatorial district provenance

The OCHA source is the [Nigeria COD-AB page](https://data.humdata.org/dataset/cod-ab-nga), which lists 37 ADM1 states, 774 ADM2 LGAs, the OCHA data period and review dates, and a CC BY-IGO license. The layer has 109 senator districts and carries OCHA fields corresponding to `sendist_en` and `sendistpcode` (shortened in Shapefile field names). Its source record dates are 2019-03-11 / valid-on 2019-04-17, version `v01`; the COD-AB page reports review on 2025-10-30.

The binary download hosts were not accessible in this environment. The senatorial shapefile components were therefore acquired from the `Fathia-Sadiq/ReportNigeria` GitHub mirror pinned at commit `aaed493911f55d2099b007d6a39ea01d877b428c`. The repository has no declared license. Its layer name, WGS 84 CRS, 109 features, fields, version, and valid-on date match the official COD-AB source metadata, but byte-for-byte identity with the official HDX archive could not be verified. Attribution is to OCHA Nigeria / OSGOF, Ehealth Africa, and the United Nations Cartographic Section under the official COD-AB CC BY-IGO terms.

The companion CSV comes from the same OCHA ADM2 source. Avoid joining it to the GRID3 polygons by LGA name alone: the two releases use different geometry/name versions, and not every GRID3 name has an exact normalized match in the OCHA table. Use OCHA p-codes where working with the corresponding OCHA COD-AB geometry.

## Source and license notes

- **Natural Earth states and rivers:** pinned Natural Earth Vector commit `ca96624a56bd078437bca8184e78163e5039ad19`; [Admin-1 source](https://github.com/nvkelso/natural-earth-vector/tree/ca96624a56bd078437bca8184e78163e5039ad19/10m_cultural), [river centerlines source](https://github.com/nvkelso/natural-earth-vector/tree/ca96624a56bd078437bca8184e78163e5039ad19/10m_physical), public domain.
- **LGAs:** geoBoundaries source archive [NGA_ADM2.zip](https://github.com/wmgeolab/geoBoundaries/blob/90c1f0d6cd6db5b58e2e24a1c57fcb2a2c9483b3/sourceData/gbOpen/NGA_ADM2.zip); metadata identifies GRID3, representative year 2022, CC BY 4.0.
- **Roads:** official [HDX Nigeria: Road Network](https://data.humdata.org/dataset/nigeria-road-network) lists OpenStreetMap contributors and other partners, CC BY, and a 2023-10-27 data period. The local mirror was taken from `mojojompe/Safe-Route-Ai` at commit `d821608b48246c1ca1835c82a636ef75c5a55baa`; schema and bounds match the HDX resource, but the exact archive bytes were not hash-verified.
- **Railways:** `onyekereolachi1-a11y/Nigeria-airport-and-railway-routes`, pinned at commit `1ea87c7506e95fcde72ada8dde4bf1b7f23b1912`; its embedded OEX README identifies OpenStreetMap contributors, snapshot 2026-09-06, WGS 84, and ODbL 1.0. The line layer is extracted without station points/polygons.
- **Capitals:** GeoNames-based `cities.json` v1.1.65 supplies coordinates under CC BY 4.0. Capital names/state codes come from [`devcenter-square/states-cities`](https://github.com/devcenter-square/states-cities/blob/ef40cceb5078f5249d80b67fbea8ca68fab3f2e2/app/data/states.json) (MIT); capital coordinates are from GeoNames, not that repository.
- **GeoNames comparison towns:** `cities.json` v1.1.65 is a population/administrative-seat-filtered GeoNames subset; it has no population or feature-code field in this package and is not an exhaustive inventory.
- **Dense populated-place points:** Downloaded from the [SafeSignal-Geo 0.2.0 PyPI package](https://pypi.org/project/safesignal-geo/) (wheel SHA-256 and extracted CSV SHA-256 are recorded in `sources.json`). The package contains 42,315 national gazetteer rows; this layer selects only the 22,004 rows with `type=settlement`. All selected rows carry a row-level ODbL license and an OSM source identifier (`osm:node/<id>` or `osm:way/<id>`); no Wikipedia/LAMATA rows or non-settlement POIs are included. Package code is Apache-2.0, while the selected OSM-derived data are distributed under ODbL 1.0 with OpenStreetMap attribution/share-alike requirements. Package documentation's broader data-license statement is not substituted for the selected rows' per-row ODbL values. The package was uploaded 2026-05-20, but the underlying OSM extract date is not specified. PyPI metadata advertises a GitHub repository that returned 404 when checked on 2026-10-18; the published wheel and embedded CSV are therefore pinned by SHA-256, and row-level OSM IDs/licenses are preserved. The output is WGS 84 / EPSG:4326; it is OSM-derived, incomplete, and not an official settlement census. `IN_REF` flags all points outside the fixed reference; none are silently dropped.
- **Rivers:** HydroSHEDS HydroRIVERS was not packaged. Its official product/license terms restrict standalone redistribution; the included public-domain Natural Earth extract is deliberately marked as generalized and incomplete. See the [HydroRIVERS product page](https://www.hydrosheds.org/products/hydrorivers) for the official detailed network and terms.

Licenses differ by layer; there is no single license for the whole bundle. Retain each source’s attribution and comply with its license when redistributing or using the layers.

## Opening the data

Keep each layer’s `.shp`, `.shx`, `.dbf`, `.prj`, and `.cpg` files together. The convenience archive is `shapefiles/nigeria_online_layers.zip`; the same files are also available unpacked in this folder. The original `shapefiles/nigeria_admin0/` reference shapefile remains unchanged.
