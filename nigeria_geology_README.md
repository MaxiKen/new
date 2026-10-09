# Nigeria geology polygon layer

## Deliverable

- **GeoPackage:** `nigeria_geology.gpkg`
- **Layer:** `nigeria_geology`
- **Geometry:** MultiPolygon
- **CRS:** WGS 84 geographic coordinates, **EPSG:4326**

The layer has 12 features. Its `name` field contains the map-legend labels separated by ` | `; `palette_id` identifies the repeated color class, `map_color` stores the source swatch color as a hex value, and `legend_n` gives the number of legend entries represented by that feature.

## Legend count and limitation of the source image

I counted **86 legend entries** in the supplied image before digitizing. The legend repeats only **12 visible fill colors** across those 86 entries. Since labels that share a color cannot be distinguished from the pixels in this image, the output groups those labels by swatch color rather than inventing separate, unsupported unit boundaries. The 12 polygon features are therefore below the 86-entry limit, and the sum of `legend_n` is 86.

## Geometry and placement

The image was georeferenced from the printed graticule (4°, 8°, and 12° E; 6°, 10°, and 14° N) and clipped to the Nigeria country outline. The supplied color map was classified, supersampled 4×, and smoothed before polygonization; shared boundaries were simplified as a valid polygon coverage. Coverage was checked against the country mask: there are no interior gaps or overlaps in the output polygons.

The country outline uses Natural Earth country boundaries from the [geo-countries dataset](https://github.com/datasets/geo-countries); Natural Earth data is public domain. The geological colors and internal boundaries come from the supplied PNG. Because the source is a raster image and reuses colors, this layer is a careful digitization of the visible map—not a substitute for an original 86-unit geological GIS dataset.

## Rebuild

`build_nigeria_geology.py` regenerates the GeoPackage from the supplied PNG and downloads the public-domain Natural Earth boundary at runtime. Python dependencies: `Pillow`, `numpy`, `opencv-python-headless`, `rasterio`, `shapely`, `fiona`, and `affine`.
