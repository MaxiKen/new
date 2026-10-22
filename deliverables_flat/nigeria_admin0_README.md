# Nigeria Admin 0 boundary (EPSG:4326)

This folder contains a single-feature ESRI Shapefile for Nigeria's national (Admin 0) boundary. The source Natural Earth attributes are retained; the feature identifies as `ADMIN = Nigeria` and `ISO_A3 = NGA`.

## Files

- `nigeria_admin0.shp` — polygon geometry
- `nigeria_admin0.shx` — geometry index
- `nigeria_admin0.dbf` — attributes
- `nigeria_admin0.prj` — WGS 84 / EPSG:4326 coordinate reference system
- `nigeria_admin0.cpg` — UTF-8 DBF character encoding

Keep the shapefile components together when opening `nigeria_admin0.shp` in GIS software.

## Source and terms

Derived by selecting Nigeria from Natural Earth's **Admin 0 – Countries, 1:10m** dataset, version **5.1.1**. The source dataset is in the [Natural Earth Vector repository](https://github.com/nvkelso/natural-earth-vector/tree/ca96624a56bd078437bca8184e78163e5039ad19/10m_cultural); the upstream project states that its data are public domain ([license](https://github.com/nvkelso/natural-earth-vector/blob/ca96624a56bd078437bca8184e78163e5039ad19/LICENSE.md)).

This is a generalized country-scale boundary, not a survey or a set of state/local-government boundaries.
