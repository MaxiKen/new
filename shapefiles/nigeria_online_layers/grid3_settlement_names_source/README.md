# GRID3 Nigeria Settlement Names — source pointer and downloader

**This directory does not yet contain the GRID3 point data or a shapefile.** It preserves the official source metadata and provides a downloader for an environment that can retrieve the public ArcGIS Feature Service. The pre-existing `towns/` and OSM-derived `populated_places/` layers remain separate and unchanged.

## Official source

- Dataset: GRID3 NGA — Settlement Names (292,438 named settlement points reported by the source portal).
- Source page: <https://data.grid3.org/datasets/GRID3::grid3-nga-settlement-names/about>
- Public ArcGIS Feature Service: <https://services3.arcgis.com/BU6Aadhn6tbBEdyk/arcgis/rest/services/Settlements_in_Nigeria/FeatureServer/0>
- Service item ID: `73d8522d1c4d4c75be6c10fa790c685c`
- License: Creative Commons Attribution 4.0 International (CC BY 4.0): <https://creativecommons.org/licenses/by/4.0/>
- Attribution supplied by the service: eHealth Africa, Proxy Logics, and Oak Ridge National Laboratory (ORNL). 2020. *Settlement Points in Nigeria*. Geo-Referenced Infrastructure and Demographic Data for Development (GRID3). <https://grid3.gov.ng/>.
- Geometry / CRS: point / EPSG:4326.
- Extent reported by the service: 2.69902546–14.67432000° E, 4.27695000–13.87818171° N.
- The portal reports the source/data record updated 2025-09-04; the ArcGIS layer metadata reports its last data edit as 2024-04-30. The dataset is described as released in March 2021.

The feature service supports query/export formats including Shapefile, GeoPackage, GeoJSON, CSV, and File Geodatabase. The sandbox can inspect the service metadata but cannot download the full data payload from the ArcGIS host under its outbound-host restrictions, so no GRID3 geometries are represented as locally downloaded or validated here. A time-limited Azure CSV export link was supplied and tested with the available fetch tool; it returned HTTP 500. Its signed query token is intentionally not stored in this repository.

## Convert the CSV export to a point Shapefile

If the CSV is downloaded to a local file, run this from the repository root:

```bash
python -m pip install pyshp
python shapefiles/nigeria_online_layers/grid3_settlement_names_source/convert_grid3_csv_to_point_shapefile.py /path/to/Settlements_in_Nigeria.csv
```

The converter writes a **new sibling folder** at `shapefiles/nigeria_online_layers/grid3_settlement_names/` with point geometry in EPSG:4326 and only the requested attributes: `FID`, `LGA_NAME`, `STATE_NAME`, and `SET_NAME`. It detects common ArcGIS CSV coordinate columns (or point geometry columns), retains all valid records, and refuses to overwrite a non-empty output folder. It does not modify or replace `towns/` or `populated_places/`.

## Download directly from the Feature Service

In an environment with access to the ArcGIS host, the paged downloader can create the same compact schema directly from the public Feature Service:

```bash
python -m pip install pyshp
python shapefiles/nigeria_online_layers/grid3_settlement_names_source/download_grid3_settlement_names.py
```

Both paths write only the requested fields and keep coordinates as point geometry. They do not clip rows or add extra attributes. After conversion, refresh the parent bundle's `sources.json`, `validation.json`, `SHA256SUMS.txt`, ZIP, and ZIP checksum before distributing the complete bundle.
