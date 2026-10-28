# Niger and Benue reference check and provisional overlay

## Result and limits

The 2011 geology map's **printed-grid registration** matches the Natural Earth reference more closely for the Niger River than either uncorrected registration of the 2023 mineral map. For the Benue the geology grid and the mineral map's embedded registration are comparable at this coarse scale. This supports using the geology map's printed grid as a **working** baseline for an exploratory overlay, but does not establish its true datum or its accuracy for every town, geological boundary or mineral symbol.

An exploratory translation of the mineral map improves its apparent river alignment with the Natural Earth reference. **This is a test correction, not a proven datum transformation or a verified final map.** In particular, it conflicts with the earlier four-town comparison: applying the river-fit translation to the mineral points moves them approximately 10.7–10.8 km away from the previously extracted geology town points. The reason has not been resolved. Consequently, the supplied overlay must not be represented as correct coordinates, or used for exploration decisions, licensing, surveying, navigation or assigning mineral deposits to geological units.

## External reference

* Natural Earth, *Rivers + lake centerlines*, 1:10 million: https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-rivers-lake-centerlines/
* Source vector dataset, pinned: https://github.com/nvkelso/natural-earth-vector/blob/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_10m_rivers_lake_centerlines.geojson
* The rivers primarily derive from World Data Bank 2 and have been smoothed and manually adjusted; Natural Earth describes the data as intended for small-scale cartography. They are not survey-grade river boundaries. Their historical source may overlap the sources used by the two PDFs, so their errors cannot be assumed independent.
* `Niger_Benue_Natural_Earth.geojson` is a regional excerpt (3.3–12.8°E, 7.25–12.5°N); the Niger lake centreline is included in the map for context but omitted from the numerical test. It includes some neighbouring-country context. Natural Earth data are public domain.
* `Nigeria_Natural_Earth_outline.geojson` is the Natural Earth-based Nigeria outline recovered from this repository's earlier reference layer. `Nigeria_Rivers_Reference.png` is a map drawn from these external reference layers, not a downloaded survey map. The natural-earth confluence river endpoints near Lokoja are approximately (6.7673°E, 7.7857°N) and (6.7603°E, 7.7867°N); they do not meet exactly. A confluence can also extend over an area rather than one exact point.

The supplied map is a generalised regional vector reference, not an official NGSA cadastral or surveying map. See also https://www.fulokoja.edu.ng/about-us.php?i=lokoja-at-a-glance for independent context that Lokoja is close to the confluence; it gives a town coordinate, not an exact river meeting point.

## Numerical comparison

The two PDFs were rendered at 1 pixel per PDF point. A fixed RGB tolerance around the blue river-fill colour isolated candidate water pixels. Natural Earth Niger and Benue centrelines were sampled approximately every 0.025 degrees; for each sample, the algorithm measured the distance to the **nearest detected blue pixel anywhere on the page** under each candidate registration. One pixel is about 0.7 km at the map scale. The sample positions are highly spatially correlated and are not independent control points. Missing river segments, symbols printed over rivers, small tributaries, lake pixels, colour matching, different river widths, map generalisation and seasonality can bias the distances, including accidentally selecting the wrong blue feature.

| Registration | Niger median; 90th percentile | Benue median; 90th percentile |
|---|---:|---:|
| Geology, printed grid | 2.35 km; 5.85 km | 4.57 km; 14.62 km |
| Minerals, printed grid | 21.58 km; 26.60 km | 8.92 km; 17.27 km |
| Minerals, embedded geographic measure | 8.78 km; 12.97 km | 3.83 km; 10.85 km |

The full statistics and sample counts are in `River_Registration_Results.json`; `River_Registration_Comparison.png` shows the detected water in blue and Natural Earth centreline in orange. These are nearest-colour distances, not surveyed errors or rigorous confidence intervals.

### Exploratory river-fit shift

A two-parameter translation was fitted independently for each river on the mineral map with its embedded registration. The sign below is the proposed **addition to the mineral map's raw embedded longitude and latitude**:

| Fit on | Proposed shift east, north | Median residual on the other river |
|---|---:|---:|
| Niger | +0.07665°, +0.05427° | Benue: 2.17 km |
| Benue | +0.07402°, +0.06132° | Niger: 1.58 km |

For the visual overlay, the averages were rounded to **+0.0753° longitude, +0.0578° latitude**. This is an empirical image translation derived from two correlated, generalised drainage lines. It is **not** a NAD27-to-WGS84 conversion, and it is not validated against independent surveyed points. The cross-river test helps expose overfitting but the two river lines and map sources may share systematic errors. The nearest-colour method can match the wrong river or lake. Do not use this shift as an authoritative correction.

For the geology map, a translation fitted to Niger did not generalise well to Benue (6.83 km median) and vice versa (7.57 km median). This is a further reason not to declare a unique, globally correct transformation.

## Provisional combined files

* `Combined_Geology_Minerals_PRELIMINARY.png`: watermarked visual blend, 62% geology and 38% minerals. **The blended colours and mineral symbols do not preserve the source legends**; use the original PDFs for interpretation.
* `Combined_Geology_Minerals_PRELIMINARY.tif`: the same qualitative blend as a georeferenced RGB raster. There is no watermark in the raster itself; the warning is in its metadata and this report.
* `Provisional_GIS_Layers.zip`: two separate rendered GeoTIFFs and the reference rivers for use in GIS. In QGIS, load the geology TIFF, the mineral TIFF above it, and adjust opacity; this permits independent visibility and retains the original rendered map colours better than the composite. The source legends remain in the original PDFs, outside the cropped map areas.

The geology TIFF uses the printed-grid fit. The mineral TIFF uses the embedded GeoPDF measure followed by the exploratory river-fit translation. Both TIFFs are labelled EPSG:4326 **only as a working visualization assumption** so GIS software can overlay them. The original geology datum is unknown, and the mineral metadata calls its NAD27-based CRS “assumed.” No authoritative datum conversion was carried out. The TIFF labels must not be mistaken for verified original CRS metadata or demonstrated WGS 84 accuracy. The rasterized images do not contain digitized geology polygons or authoritative mineral point coordinates.

## Reproduction and checks

`River_Registration_Analysis.py` produces the comparison figure, reference map and JSON from the two PDFs and the supplied Natural Earth GeoJSON files. Install `pymupdf numpy scipy shapely matplotlib`. `Build_Provisional_Overlay.py` reproduces the TIFF, PNG and zipped layers; install `pymupdf numpy rasterio pillow`. Both scripts run from this directory. The Natural Earth reference excerpt has SHA-256 `712a625d9854b7835522c788f29c691501d03e78b83ff80e80c20a2a591d9093`.

The combined TIFF was checked for dimensions, CRS label and bounds, and the GIS-layer ZIP passed an archive integrity test. These are file-integrity checks, not geographic validation.

## What is needed for confidence

Obtain a geographically distributed set of **independently surveyed** control points with a documented datum, including points away from these two rivers. Independently locate actual symbol centres in both PDFs and resolve the disagreement with the four prior town comparisons. Fit the transformation on one set and evaluate separate withheld points, with uncertainty reported across Nigeria. If possible, obtain the original NGSA CRS, source layers and intended PDF georeferencing. Only then choose or revise the correction and publish a combined map as accurate.
