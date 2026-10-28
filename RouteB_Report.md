# Route B, carried out with open data: the datum cannot be confirmed this way

I ran Route B myself rather than leaving it as advice. Result in one line: **with freely
available online data the datum is not identifiable — the test is 1.4× too coarse for the
0.11 km effect, and the references disagree with themselves by 0.85 km.** Two of the three
plausible datums are indistinguishable from WGS 84 *by any test with this artwork*.

All numbers below are reproducible: `RouteB_Control_Attempt.py` → `RouteB_Control_Attempt.json`.

## 1. What I brought in

| source | how obtained | what it contributes |
|---|---|---|
| Natural Earth 1:10m Nigeria outline | already in repo (`Nigeria_Natural_Earth_outline.geojson`) | independent national boundary, generalised |
| GADM 4.1 state boundaries, Nigeria (38 features) | `Das4joe/Nigeria-shapefile` mirror of GADM on GitHub; **used for analysis only, not redistributed here** because GADM's licence is academic/non-commercial | second, independent, much more detailed national boundary (124° of line vs Natural Earth's 55°) |
| EPSG datum operations via PROJ | `pyproj` against the EPSG registry (`TransformerGroup`) | the actual size of each candidate datum shift over Nigeria |
| The 2023 sheet's vector international boundary | PyMuPDF `get_drawings()`, pure-red stroke, 3,500 unique vertices | the *only* part of either sheet with exact, non-rasterised page geometry |

The state-boundary file is downloaded to `/tmp/nga_states_bound.geojson`; the script skips it
gracefully if absent, and nothing GADM-derived is committed.

## 2. Three measurements

**(a) The references disagree with each other by ~0.85 km.**
Natural Earth → GADM: median **0.85 km**, p90 3.03 km. GADM → Natural Earth: median 1.61 km,
p90 9.21 km. So the two "truths" differ by more than 7× the largest datum effect in Nigeria.
Any fit picks up this disagreement before it can see a datum.

**(b) The sheet's own border resolves a shift to about 0.16 km — against one reference only.**
Fitting a translation of the 2023 vector border to each reference (block-bootstrap standard
errors over 1,200 sampled vertices):

| reference | median offset before fit | best translation (E, N) | median after | 95% bootstrap SE | smallest detectable shift |
|---|---:|---:|---:|---:|---:|
| Natural Earth | 1.11 km | +0.66, −0.22 km | 0.97 km | ±0.23, ±0.32 km | 0.63 km |
| GADM | 0.46 km | +0.11, 0.00 km | 0.45 km | ±0.05, ±0.08 km | **0.16 km** |

The sheet is much closer to GADM than to Natural Earth, which is expected: neither the 2011 nor
the 2023 sheet is sourced from Natural Earth, and Natural Earth is the coarser dataset. Note
also that the *shape* of the sheet's border matters here, not just its position — this is a much
stronger control than the coastline or river tests.

**(c) The datum effect is 0.06–0.11 km.** Computed on a 1° grid over Nigeria from EPSG operations:

| datum | operations covering Nigeria | median shift | max shift | median operation accuracy |
|---|---:|---:|---:|---:|
| **Minna → WGS 84** (EPSG:4263, Clarke 1880 — Nigeria's own datum) | 15 | 87 m | **112 m** | ±15 m |
| **NAD 27 → WGS 84** (EPSG:4267 — the datum named in the PDF's placeholder) | 31 | 0 m (only a ballpark op covers Nigeria) | 0 m | n/a |

Two things follow. First, **NAD 27 is not testable in Nigeria at all**: PROJ has no Nigeria-area
NAD 27 → WGS 84 operation, only a "ballpark" one, so "the sheet is NAD 27" predicts literally no
change and is numerically identical to "the sheet is already WGS 84." That hypothesis is
unfalsifiable with these data, which is itself an argument for not claiming it.

Second, Minna moves Nigeria **60–112 m west/north-west**, i.e. about **0.1 km** — less than the
2023 sheet's 0.16 km detection floor and 8× less than the reference disagreement.

## 3. The verdict, stated honestly

* **Not separable.** Signal 0.11 km; nearest competing explanation (reference disagreement)
  0.85 km; sheet residual 0.46–1.11 km. A datum "found" by fitting these layers would be an
  artefact of which reference I happened to use. I am not going to publish that.
* **What is nevertheless true and useful:** the sheet behaves like a WGS 84 / GDA-style frame to
  within **0.5 km** (its offset from GADM), and its internal frame is consistent to ~1 km. That is
  a *practical* answer for a 1:2,000,000 map, and it is the honest ceiling of what this artwork
  supports.
* **The internal 19 km error remains fixed and is independent of this question.** The printed
  graticule vs embedded measure discrepancy is 0.172°, a hundred times the effect being tested
  here, and the vector-border evidence for it (1.11 vs 12.94 km) is not marginal.

## 4. What would actually settle it

I built the tool for the final step, `RouteB_Fit_Datum.py`, and validated it both ways. It takes
`control_points.csv` (`name,page_x,page_y,lon_wgs84,lat_wgs84,source`), converts each point through
the sheet's embedded measure, and reports each hypothesis' mean offset with standard error.
It declares a datum only when the closest two hypotheses are separated by more than 2 standard
errors; otherwise it reports "not resolved".

`python RouteB_Fit_Datum.py --selftest` proves it works in both directions on synthetic data:

```
true datum    WGS 84: RESOLVED -> sheet is WGS 84 as printed     separation 0.079 km vs 2xSE 0.042 km
true datum      4263: RESOLVED -> sheet is Minna                 separation 0.079 km vs 2xSE 0.042 km
selftest passed
```

With real control points the requirements are concrete. The Minna–WGS 84 difference is ~0.11 km;
to resolve it at 2σ you need the standard error of the mean offset below ~0.05 km, which needs
roughly:

* ~20 points with 0.25 km residuals, or
* ~10 points with 0.15 km residuals, or
* 5 points with 0.1 km residuals,

spread across the country (the shift varies by latitude, so do not cluster them). Since the sheet's
own artwork is only good to ~0.5 km per point, the realistic route is **large features with exact
surveyed positions** — dam axes, runway ends, major bridge ends, trig pillars that also appear on
the sheet — surveyed by **RTK/static GNSS (≤0.05 m)**, not by handheld. Twenty such points would do
it. Without them, "datum undetermined, behaviour consistent with WGS 84 to 0.5 km" is the correct
and final answer.

Where to get those points, concretely:
* **OSGoF (Office of the Surveyor General of the Federation)** — NIGNET CORS station coordinates
  (11–16 stations: Abuja/OSGoF, Lagos/UNILAG, Zaria/ABU, Enugu/UNEC, Calabar/UNICAL, Maiduguri,
  Toro, Yola, Port Harcourt, Kebbi, Gembu). Ask for the published ITRF/IGS coordinates; several are
  in the open literature.
* **NGSA / Geological Survey of Nigeria** — the source geodatabase, which is still the cheapest
  possible answer (Route A).
* **Published geodesy papers** (e.g. the NIGNET stability and ITRF2014 velocity studies) contain
  station coordinates at the cm level; those are legitimate independent control for the
  *frame*, though only for the few stations that coincide with sheet features.

## 5. Files

* `RouteB_Control_Attempt.py`, `RouteB_Control_Attempt.json`, `RouteB_Control_Attempt.png` — the three
  measurements above and the figure.
* `RouteB_Fit_Datum.py` — the hypothesis test for when control points exist; `--selftest` validated.
* `Datum_Confirmation_Plan.md` — the general plan this implements.
* `Niger_Benue_Alignment_Report.md` — the internal 19 km correction, unaffected by all of this.
