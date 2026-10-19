# Rivers — complete as printed (including small rivers)

**Answer to "is the river shapefile okay?": No — it was replaced.** The previously shipped `river_lines` came from Natural Earth and contains **only the largest rivers** (12 named rivers, 35 segments, ~5,233 km). It is kept for comparison in `previous_major_rivers_only/`.

**New layers (EPSG:4326):**
- `rivers_as_printed_mineralmap2023.shp` — **every blue river line printed on the Mineral Resources Map of Nigeria 2023**, extracted from the PDF's own river vectors: 1,447 features, 43,245 km (includes short reaches across the border exactly as printed).
- `rivers_nigeria_only_from_mineralmap.shp` — same network clipped to Nigeria: 1,348 features, 36,587 km.

**Small rivers are included** down to the smallest tributaries drawn at the map's 1:2,000,000 scale (1,299 of the as-printed features are small tributaries). Streams smaller than what the map prints cannot be recovered from this source.

148 features carry a `river_nm` name where they coincide (±1.2 km) with a named Natural Earth major river. **A blank `river_nm` means a smaller printed river/tributary** — the map does not name most small rivers, so no name was invented. See `rivers_QA_report.json` and `../QA_maps_and_reports/QA_rivers_before_after.png`.
