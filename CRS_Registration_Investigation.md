# CRS and registration investigation: the two Nigeria maps

## Executive conclusion

The mineral PDF contains **two conflicting geographic registrations**. At its printed 4°E meridian, the PDF's embedded geographic measure gives approximately **4.1718°E**. The same near-constant discrepancy occurs at the printed 6°, 8°, 10°, 12° and 14°E lines. At Nigerian latitudes this is about **19 km east–west**.

This explains why the earlier comparison found an approximately 19 km map-to-map separation: it registered the mineral map against its printed graticule. If the same mineral dots are instead located using the PDF's embedded geographic measure, they are numerically much closer to the geology-map triangles: the median of four visually checked examples falls from **18.65 km to 0.55 km**. This is a comparison of raw geographic numbers, **not a verified datum transformation**.

This does **not** establish which mineral registration is geographically correct. In particular, neither close overlay between the maps nor an approximate match to GeoNames proves absolute accuracy. The earlier conclusion that the maps themselves are about 19 km apart was premature: the registration used is decisive.

## 1. What is actually declared

| Item | Geological map | Mineral resources map |
|---|---|---|
| PDF authoring software | Esri ArcMap 9.2 | Esri ArcMap 10.2.2 |
| Page | 3168 × 1764 PDF points, no rotation | 3960 × 2160 PDF points, no rotation |
| Machine-readable PDF geographic viewport | None found in page dictionary or object scan | One `/VP`, with `/Measure` of subtype `/GEO` |
| Embedded geographic CRS | Not found | `GCS_Assumed_Geographic_1`, datum `D_North_American_1927`, spheroid `Clarke_1866`, Greenwich, degree units |
| Actual source map datum | **Not established** by this PDF inspection | Its metadata declares the above, but the name explicitly says “Assumed”; it is not proof that the map's source was surveyed in NAD27 |
| Printed meridians/parallels | Present | Present |

The scan searched uncompressed PDF object dictionaries for `/Measure`, `/GCS`, `/GPTS`, `/LPTS`, `/WKT`, `/EPSG`, `/LGIDict`, `/Viewport` and `/VP`. Absence of a machine-readable CRS in the geology PDF does not prove that no paper documentation or original GIS project specifies one. A text search of the extracted PDF text did not find an explicit datum or projection declaration; non-text graphics and external documentation were not exhaustively established.

The PDFs' page-coordinate units are points (1/72 inch), **not metres**. Their different page sizes do not by themselves cause geographic misalignment.

### Mineral PDF embedded values

From the mineral page dictionary and its measure object, exactly as stored:

```
/VP [ << /Type /Viewport
  /BBox [74.23969 1801.2761 2051.1915 192.29888]
  /Measure 115 0 R >> ]
/Measure 115: /Subtype /GEO
  /Bounds [0 1 0 0 1 0 1 1]
  /GPTS [3.83671 2.47619 14.04668 2.47619
         14.04668 15.02138 3.83671 15.02138]
  /LPTS [0 1 0 0 1 0 1 1]
/GCS 114: GEOGCS["GCS_Assumed_Geographic_1",
  DATUM["D_North_American_1927",
    SPHEROID["Clarke_1866",6378206.4,294.9786982]],
  PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]
```

`GPTS` geographic pairs are latitude, longitude. The bounding box is written with the upper PDF y before the lower PDF y. For comparison, the calculations below convert to a top-left page origin (x rightward, y downward). Do not assume the individual numbers in the WKT alone establish a reliable NAD27-to-WGS84 operation in Nigeria.

## 2. Printed-graticule registration check

For reproducibility, the page-to-coordinate fits used in the earlier work are:

```
Geology:  longitude = (x + 276.36) / 157.593
          latitude  = (2281.63 - y) / 157.586
Minerals: longitude = (x + 288.95) / 157.5987
          latitude  = (2572.35 - y) / 157.6015
```

Here x and y are PDF points from the **top left**. The geology equations assign the geology printed graticule's numbers; they do not prove it is WGS 84. The mineral equations assign the **printed** graticule's numbers, not the embedded measure's.

The fits were checked against the actual printed grid lines, not only the text bounding boxes. The 12 geology meridians 3°–14°E and six mineral meridians 4°, 6°, 8°, 10°, 12°, 14°E were examined on rendered strips. Their observed x positions were within about **0.13 PDF point** of the predicted lines at 4× rendering resolution. The geology 4°–13°N and mineral 5°, 7°, 9°, 11°, 13°N horizontal lines were also checked; observed y positions were within about **0.4 point**. This is a rasterized control-line check, not an uncertainty estimate for where every town was drawn.

| Printed mineral meridian | Approx. page x, points | Embedded measure's longitude at that x |
|---:|---:|---:|
| 4°E | 341.445 | 4.171800°E |
| 6°E | 656.642 | 6.171955°E |
| 8°E | 971.840 | 8.172111°E |
| 10°E | 1287.037 | 10.172267°E |
| 12°E | 1602.234 | 12.172422°E |
| 14°E | 1917.432 | 14.172578°E |

The slight change in the offset indicates a small scale difference as well as a translation. Do not universally subtract exactly 0.172° and call that an authoritative datum correction.

## 3. Town-symbol test with both mineral registrations

The geology symbols in these cases are small triangles; the minerals symbols are dots. Four pairs were visually checked. Their centres are approximate: the mineral centre was estimated from the adjacent label anchor after checking the displayed symbol, not surveyed or independently digitized to subpixel precision. The geology positions come from the repository's previous extraction of the geology symbols. Geographic distances below are spherical approximations computed from coordinate numbers, without a validated datum transformation.

| Town | Geology vs minerals, printed-grid registration | Geology vs minerals, embedded registration | Geology vs GeoNames | Minerals embedded vs GeoNames |
|---|---:|---:|---:|---:|
| Argungu | 18.63 km | 0.52 km | 7.73 km | 7.36 km |
| Bungudu | 18.56 km | 0.45 km | 7.92 km | 7.49 km |
| Baure | 18.67 km | 0.58 km | 8.96 km | 8.58 km |
| Ogbomosho / Ogbomoso | 19.11 km | 0.73 km | 11.79 km | 11.53 km |
| Median, four examples | **18.65 km** | **0.55 km** | **8.44 km** | **8.04 km** |

These four were chosen to check recognizable names and symbols, not as a random sample. GeoNames represents a settlement by a point which can differ from a cartographer's chosen town symbol. The remaining discrepancies need separate investigation; the available evidence does not isolate map error, historical gazetteer accuracy, match identity, symbol placement, datum or extraction error.

The companion CSV contains **78 automatically matched candidates**. Only these four have been visually checked. Three outliers are specially flagged; all remaining candidates have unverified marker and name associations. For transparency, the CSV also has the alternative raw embedded-coordinate columns. The candidate matching required a GeoNames point within 20 km of the geology point and filtered on recorded coordinate digits; this selection biases any GeoNames-versus-geology summary. Coordinate decimal places are not a demonstrated accuracy. Do not interpret the 78 candidate median as an independent, unbiased accuracy assessment.

## 4. Can CRS/datum alone explain this?

* A GIS can legitimately draw different CRSs together after a **known, valid** transformation. Conversely, assigning the wrong CRS, confusing axis order, or using an inappropriate datum transformation can produce misalignment.
* Here, before any datum transformation, the **same mineral PDF itself** assigns different longitudes to the same printed 4°E line. That is a directly measured page-registration inconsistency, not proof of a particular datum shift.
* The mineral WKT names NAD27/Clarke 1866 as an **assumed** geographic system. The available PROJ 9.5.1 operation search for this exact WKT with a Nigeria-area query returned only a **ballpark** operation to WGS 84, accuracy unknown, with unchanged numerical coordinates. A ballpark/no-op is not evidence that NAD27 and WGS 84 truly coincide in Nigeria. No authoritative Nigeria-specific NAD27 transformation is established by this inspection.
* The geology PDF does not establish its datum. It would be improper to assign EPSG:4326 or Minna merely because those are plausible choices. An illustrative PROJ query for a *hypothetical* Minna-to-WGS84 transformation near 4.5°E, 12.7°N yields changes on the order of 0.0007–0.0008° longitude (roughly 0.08 km); this is **not** evidence that either PDF uses Minna and cannot determine the real error.
* A correct datum transformation cannot be selected confidently until the original CRS/datum and transformation parameters are independently documented. Raster georeferencing, page export, wrong viewport, layer displacement, axis order, cartographic generalization, and name/symbol matching all remain possible contributors.

## 5. Practical GIS guidance

1. Preserve the original PDFs and distinguish two versions of the mineral registration: **printed-grid** and **embedded-measure**. Do not silently replace one with the other or edit the original file.
2. Do not represent either as a verified EPSG:4326 dataset until its datum is established. A temporary WGS 84 assumption may be useful for visualization, but must be clearly labelled as an assumption.
3. Compare both registrations against a distributed set of independently surveyed control points or authoritative town, road and border coordinates. Record source, datum, epoch, and uncertainty for each; avoid choosing matches by proximity to just one map. Digitize the actual symbols, not label positions, and independently review repeated place names.
4. Request NGSA's original GIS project/layers, the published CRS and datum, and the intended geographic registration of the mineral PDF. An authoritative source is needed to decide whether the printed grid or the embedded measure is the error.
5. If a correction is eventually supported by independent controls, document the transformation and residuals on withheld check points. Merely changing an EPSG label is not a coordinate transformation.

## 6. Data, provenance and reproducibility

* `Nigeria_GeoNames_towns.geojson`: 45,415 populated-place records extracted from the repository's previously assembled GeoNames layer. The original data are a **2014-10-02** GeoNames dump mirrored through `albert-decatur/geonames2sqlite` at commit `1515c016027be9febacff4b272fcbde6a4d28dff`; it was not newly downloaded for this check. GeoNames is attributed to geonames.org (CC BY 4.0). The `state` field was derived in that earlier build using Natural Earth boundaries, not always directly from GeoNames; `state_gn` is the original GeoNames state where populated. Alternative names may be truncated in the prior extraction.
* `Town_comparison_three_sources.csv`: coordinates, distances, matching identifiers, alternative embedded registration, and per-row review status. It is a candidate-review table, not a fully validated town inventory.
* `CRS_check.py`: inspect the PDF geographic metadata and recompute the meridian discrepancy and four checked numerical comparisons. Requires PyMuPDF: `python -m pip install pymupdf`, then `python CRS_check.py`. The optional illustrative datum-operation test used pyproj 3.7.2 / PROJ 9.5.1; available operations can differ by installation and grid availability.
* PDF SHA-256: geology `9a92e22bbb2536981db033748cacd8aa5a5096cecda74c0109a1dddd95f629c8`; minerals `d7a74aa425fb5950a39edd1d73ab9a0a7ecd19effb985b25af5e4fd3f0ec46d9`.

No original PDF was modified.

## 7. Additional online reference and algorithmic cross-check

A further check used Natural Earth's public-domain 1:10m populated-places data, downloaded from the pinned GitHub revision `nvkelso/natural-earth-vector@ca96624a56bd078437bca8184e78163e5039ad19`. There are 68 Nigerian records in `Nigeria_Natural_Earth_places.geojson`. Natural Earth and GeoNames are distinct published datasets, but their underlying sources may overlap; they must not be assumed statistically independent or survey-grade.

The workflow matched settlement names from Natural Earth to the prior geology extraction and to text in the mineral PDF, with proximity screens of 35 km and 60 km respectively. This yielded 11 candidates. Seven pairs (Bama, Biu, Idah, Iseyin, Nguru, Ogbomosho and Orlu) were retained after visually inspecting the PDF crops. Their marker positions are still approximate, and the name identities are not independently proven. Aba was excluded because the map label may identify a different Aba; Jalingo because the estimated mineral marker is ambiguous; and Ife and Iwo because their mineral symbols or names are obscured/ambiguous. All 11 candidates and exclusions are in `Natural_Earth_town_comparison.csv`.

| Numerical comparison with Natural Earth, seven candidates | Median |
|---|---:|
| Geology, printed grid | 9.35 km |
| Minerals, printed grid | 25.88 km |
| Minerals, embedded measure (raw declared coordinates) | 8.97 km |
| Geology vs minerals embedded measure | 0.61 km |

For an exploratory held-out test, each of the seven points was held out in turn. A two-parameter **median longitude/latitude translation**, fitted to the other six relative to Natural Earth, was applied to the held-out point. Median held-out residuals were 3.53 km for geology, 3.45 km for minerals printed grid, and 3.51 km for minerals embedded registration; worst held-out residuals were approximately 5.7–5.8 km. `python Natural_Earth_validation.py` recomputes these figures from the candidate CSV.

This is an exploratory fit, **not a new CRS identification or a recommended correction**. The same six-point translation can absorb a registration shift under either mineral registration, which is precisely why these data cannot establish the correct CRS by optimization alone. The points were name- and distance-screened, the sample is small, the source reference points and map symbol centres have unknown uncertainty, and the CRS/datum of the geology map is unknown. The observed additional offset from Natural Earth could involve cartographic generalization, source georeferencing, datum, symbol placement, name matching, or reference error; these effects cannot be isolated by this test.

The new evidence strengthens the practical preference for the mineral **embedded** registration when comparing the two maps, and exposes a remaining several-kilometre disagreement with Natural Earth. It does not make either registration authoritative. A defensible absolute correction needs independently surveyed control points of known datum and uncertainty, or the original NGSA GIS metadata, followed by an out-of-sample validation across Nigeria.
