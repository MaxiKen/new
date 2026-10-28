# How to confirm the datum (and why the PDFs alone cannot)

## 1. The verdict on the files we have

**Neither PDF can confirm its own datum.** Not "hard" — impossible with these files, because the
evidence that would identify a datum does not exist in them. Three independent reasons:

**(a) The declared CRS is a null value, not a datum.** The 2023 sheet's `/VP … /Measure /GEO`
carries

```
GEOGCS["GCS_Assumed_Geographic_1", DATUM["D_North_American_1927",
       SPHEROID["Clarke_1866", 6378206.4, 294.9786982]]
```

`GCS_Assumed_Geographic_1` is an **ESRI placeholder** that ArcMap wrote when a dataset had *no*
coordinate system: it means "the numbers look like degrees, so guess". ESRI's own documentation
states it "is not the data's correct coordinate system", that ArcGIS removed it in 9.2, and that
users must "take steps to identify the data's true coordinate system".
(https://desktop.arcgis.com/en/arcmap/latest/map/projections/gcs-assumed-geographic-1.htm,
https://desktop.arcgis.com/en/arcmap/latest/map/projections/identifying-an-unknown-coordinate-system.htm)

So `D_North_American_1927` is not a declaration by NGSA. It is the default ESRI attaches to its
"unknown" placeholder. Treating the sheet as NAD27 is an assumption inherited from software
behaviour, and NAD27 is anyway the wrong datum family for Nigeria.

This matters for copying: **do not** stamp `EPSG:4267` on these layers. Doing so would assert a
datum the file itself says is unknown, and would trigger a spurious 158 m east / 120 m north
"NAD27 → WGS 84" shift in any GIS.

**(b) The sheet's precision is coarser than the differences being asked about.** Measured in
`Datum_Confirmability.json`:

| test | result |
|---|---|
| 2023 vector international border vs Natural Earth Nigeria outline, embedded frame | median **1.08 km**, p90 3.16 km |
| best-fitting residual translation of that border | **+0.6 km east, −0.2 km north**, 95% bootstrap ±0.5 / ±0.6 km |
| same fit, one data band per 2° of longitude | east +0.4 to +1.3 km, north −0.9 to +0.4 km, **signs change** |
| 2011 coastline vs the same outline, printed grid | median 1.86 km; best fit −2.7 km E, −5.6 km N and still 1.47 km |

Candidate datum differences across Nigeria are **100–360 m** (largest pair separation 544 m;
NAD27 → Minna is 0.12° of nothing much: 240 m). The maps' own generalisation error is
~1–2 km and changes sign along the border. **The signal is 5–10× smaller than the noise**, so no
amount of clever fitting to this artwork can pick a datum. Fitting harder would just produce an
overfitted number, which is exactly the mistake the earlier river shift made.

**(c) The one datum hint present points to a *local* datum, not NAD27.** The 2023 sheet prints
`MINNA` in its marginal notes; it does **not** print the word "datum" or the names Clarke 1866 /
Clarke 1880 / WGS 84 anywhere. Nigeria's historical national datum is **Minna**, on the Clarke 1880
ellipsoid (EPSG:4263). A Nigerian national mapping sheet produced by the Geological Survey, with
MINNA printed on it and no datum statement, is more plausibly tied to Minna (or to arbitrary
WGS 84 degrees) than to a North American datum. This is a *lead*, not proof.

## 2. What "confirmed" would require

A datum is confirmed by one of two things: a **documentary statement** from the producer, or
**independent control points** accurate enough to separate the candidates. In order of cost:

### Route A — documentary (cheap, decisive, try this first)
Ask NGSA / the Geological Survey of Nigeria for:
1. the **coordinate system of the source geodatabase**, not the PDF export — the `.mxd`/`.aprx`, the
   original shapefiles, or the geodatabase's spatial reference;
2. the **datum and projection statement** on the map's production sheet or its metadata (a
   standard Nigerian 1:2,000,000 sheet normally carries one);
3. whether the exported GeoPDF was produced with a **coordinate system set at export** (the
   `GCS_Assumed_Geographic_1` strongly suggests it was not);
4. for the 2011 sheet: the same, from the then Geological Survey of Nigeria / NGSA.

One email can settle this. Everything below is only needed if the producer cannot answer.

### Route B — independent control points (what surveyors use)
The map itself cannot supply this, because its own drawing error is 1–2 km. You need points whose
true coordinates are known to better than ~30 m, spread over the whole country, ideally 20–30 of
them. Cheap sources, in ascending order of quality:

| source | typical accuracy | note |
|---|---|---|
| GNSS **static** occupations on pillars/benchmarks of the Nigerian geodetic network (Surv. Gen./OSGoF) | 1–5 cm | the proper answer; a handful is enough to test a Helmert fit |
| OSGoF / NGSA published geodetic control lists and Continuously Operating Reference Station (CORS) coordinates | cm | ask for the station list and its datum, usually ITRF/WGS 84-realised |
| GNSS field capture at unambiguous features also printed on the sheet: bridge/road junctions, airfield runway ends, dam axes, church/mosque and school compounds in named towns | 3–10 m (handheld), <1 m (RTK) | must be *the same* feature, not the town name |
| High-resolution satellite imagery (0.3–0.5 m) co-registered to WGS 84 | 3–10 m | usable to check a *frame*, not to certify survey accuracy |
| OpenStreetMap / Natural Earth / GeoNames | 10–500 m | already tried; the current evidence base, and it is why the answer is "cannot confirm" |

**Design of the test.** With ~20 surveyed points spread across Nigeria:
1. Locate the same feature on the sheet (symbol/feature centre, by hand, at 75 dpi ≈ 0.7 km per
   pixel — so prefer large features, and record the pixel coordinates).
2. Convert page → lon/lat with the sheet's embedded measure (2023) or printed grid (2011).
3. Compare with surveyed WGS 84. Report residuals on the page scale, not just in degrees.
4. Fit a 2-parameter translation, then a 7-parameter Helmert, and test **candidate datums**
   (WGS 84, Minna EPSG:4263, Adindan EPSG:4201) against each other with a hold-out split.
5. Accept a datum only if its predicted pattern beats the alternatives by more than the residual
   scatter (a formal F-test / Akaike comparison), and state the achieved accuracy as a number.

**What would actually be learned.** Minna-to-WGS 84 in Nigeria is a few hundred metres at most and
is **not constant** — Nigeria's official transformation is a set of local shifts, not one
country-wide Helmert. So even a successful fit yields "the sheet behaves like *this* local shift",
plus a residual of the same order. Expect the honest answer to be *"datum indistinguishable from
WGS 84 within the map's 1–2 km accuracy; use WGS 84 and state 1–2 km"* — which is the practically
correct outcome for a 1:2,000,000 sheet, and is far better than a falsely precise claim.

### Route C — weak corroboration only (do not dress this up as confirmation)
* **Collected works of the Survey**: compare the sheet's printed graticule intersections with
  published Nigerian survey coordinates for the same trig pillars.
* **Comparisons of features**: run the border/coastline test already coded here against a second,
  independent national boundary (e.g. the OSGoF boundary or GADM) and against lakes Chad and Kainji
  shorelines. Agreement supports the *frame*, never the *datum*.
* **A residual field**: if a datum were wrong, the residual should be a smooth, low-order surface
  over the whole country. Here it is ~1 km, changes sign between longitude bands, and disappears
  under the embedded measure — the signature of cartographic generalisation, not a datum.

## 3. What is nevertheless settled now

Independent of the datum question, the sheet's **internal** inconsistency is fixed and reproducible:
the printed graticule is 0.172° (~19 km) west of the frame the artwork was actually drawn in,
established by the sheet's own vector international boundary (1.06 km vs 12.94 km). That is a
different problem from the datum, and correcting it is valid regardless of which datum turns out to
be right.

**Practical labelling rule until Route A or B succeeds:** keep the rasters labelled `EPSG:4326` as
a display assumption, add a `DATUM=basis unverified, candidate Minna/Clarke 1880 or unknown`
tag, and quote accuracy as "internal registration ~1 km; absolute datum not established". Do not
report, or round to, anything finer.

## 4. Files

* `Datum_Confirmability.py` / `.json` — the detection-limit test above (re-runnable).
* `Datum_Confirmability.png` — left: fitted correction with bootstrap scatter and candidate datum
  shifts drawn to the same scale; right: per-band fits whose signs change.
* `Niger_Benue_Alignment_Report.md` — the internal-registration correction and combined map.
