# `towns_geonames` — the gazetteer of Nigerian places

**45,415 points, EPSG:4326**, built by `build_towns.py`. One row per populated
place GeoNames records for Nigeria: towns, villages, hamlets and the seats of
government.

It is a **new layer beside `towns`, not a replacement.** `towns` is the 486
labels the 2011 NGSA sheet printed (82 of them unnamed) — that is what the paper
map shows. `towns_geonames` is the gazetteer — that is what exists. Use `towns` to
match the map; use this one to have coverage.

## Provenance (pinned, so this is reproducible)

| what | source | licence |
|---|---|---|
| 45,415 populated places | GeoNames `allCountries` dump, 2014-10-02 build, via `github.com/albert-decatur/geonames2sqlite@1515c01` | **CC BY 4.0** — attribution: *"GeoNames, geonames.org"* |
| the `state` fallback | Natural Earth admin-1 states/provinces (`nvkelso/natural-earth-vector@ca96624`) | public domain |

`build_towns.py` downloads the nine 50 MB zip chunks, reassembles the 1.46 GB
SQLite dump, keeps only the Nigerian `featureclass = P` rows and the admin name
tables, and throws the rest away. Nothing is stored in this repository except the
resulting layer and `towns_report.json`.

## Fields

| field | what it is |
|---|---|
| `geonameid` | the GeoNames id — the stable key, use this to join back |
| `name`, `ascii_name` | the name as GeoNames prefers it, and ASCII-folded |
| `alt_names` | the alternative spellings GeoNames records, comma-separated and cut at 120 characters (the longest in the layer is 116) |
| `feature_code`, `feature_type` | `PPL` village/town (45,141), `PPLA` state capital (36), `PPLA2` (82), `PPLC` national capital (1 — Abuja), `PPLX` section of a place (44), `PPLQ` abandoned (40), `PPLL` locality (41), `PPLS` (25), `PPLF` farm (4), `PPLR` religious (1), with the plain-language type beside each |
| `state` | state name, from the state polygon the point falls in |
| `state_gn` | the state GeoNames itself records (70 % of places have none) |
| `state_agree` | a real BOOLEAN (1/0, NULL where either side is unknown) — they agree on **93.7 %** of 31,913 comparisons (29,903 agree, 2,010 do not); disagreeing rows are worth a look before trusting either. 427 of the 31,913 fall outside every state polygon on the sheet, so their `state` *is* GeoNames' own and they agree by construction |
| `admin1_code`, `admin2_code` | GeoNames' own codes, as printed — `admin1_code` is `00` for 13,501 rows, which is GeoNames saying it does not know the state, so use `state` (from the polygon) rather than this code; `admin2_code` is populated for 12 rows |
| `lga` | the local government area, resolved from GeoNames' own `admin2` names: **11 of 45,415**. GeoNames has almost no Nigerian LGA coverage and no LGA was invented from another source |
| `population` | 0 where GeoNames records none; only **450** places carry a figure |
| `elevation_m`, `dem_m` | spot elevation and digital elevation model, in metres, as recorded — `elevation_m` is `INTEGER`, `dem_m` `REAL`, both NULL where GeoNames has none. GeoNames records a spot elevation for only **22** of the 45,415 places, so `elevation_m` is almost always NULL and `dem_m` is the field to use; `dem_m` is populated for 45,371, the other 44 being the SRTM void `-9999` and two small negatives over water, which are NULL rather than elevations |
| `timezone`, `moddate` | as recorded by GeoNames |
| `coord_dp` | **the precision of the position**, in decimal places (0–5). GeoNames does not record an accuracy, but it does record the number of digits: see below |
| `in_nigeria` | point falls inside `national_territory` |
| `ngsa_town_km` | distance to the nearest NGSA `towns` label, km |
| `dup_group` | places with the same name in the same state within 5 km, numbered — **642 rows** are a second spelling of a settlement already in the layer. `dup_group IS NULL` drops them; nothing was deleted |
| `ngsa_town_km` | distance to the nearest NGSA `towns` label, km |

### Coordinate precision, which nothing else in the layer admits to

GeoNames rounds a position to as many decimal places as it holds: 5 is about a
metre, 1 is about 10 km, 0 is the whole degree. The distribution in this layer:

| `coord_dp` | rows | worst-case positional error |
|---|---|---|
| 0 | 320 | ~55 km |
| 1 | 3,631 | ~5.5 km |
| 2 | 3,421 | ~550 m |
| 3 | 971 | ~55 m |
| 4 | 7,262 | ~5.5 m |
| 5 | 29,810 | ~0.5 m |

**7,372 entries (16 %) are at 2 decimal places or fewer.** They are real places,
correctly named and correctly inside the right district, but their position is
good to a kilometre at best and tens of kilometres at worst — the coordinate was
recorded as a coarse locality, not surveyed. The two accuracy figures quoted below
are unaffected (the 15 major cities are all at 4–5 dp; the NGSA comparison is a
nearest-name distance, not a true error). For any distance calculation, filter:
`WHERE coord_dp >= 3`.

### Duplicate coordinates

**2,638 rows repeat a coordinate already used** — 4,373 rows in all sit on a coordinate that
at least one other row also has — more than the 642 that
`dup_group` marks, because GeoNames also gives neighbouring hamlets and two
different spellings the same rounded position, and because at `coord_dp` 0–2 the
rounding itself coincides. A spatial join therefore returns several places for one
point; that is the source's behaviour, not a defect in the layer, and nothing was
merged or dropped to hide it.

## Accuracy — measured, not asserted

| check | result |
|---|---|
| inside the national territory | **44,915 of 45,415 = 98.9 %** |
| the 500 outside | median **0.8 km** beyond the border (generalisation), worst 292 km (a place GeoNames locates in a neighbouring country) |
| against published coordinates for 15 major cities (independent of this repository) | median **0.55 km**, worst 5.7 km (Ibadan) |
| against the NGSA map labels — for each of the 404 named labels, the nearest same-name gazetteer place | **257 within 15 km**, median 10.8 km, 90th percentile 98 km |
| state agreement, GeoNames' own field vs. the polygon | **93.7 %** of 31,913 (427 of them have no polygon state, so they agree by construction) |
| state present | 99.8 % of rows (from the polygon) |
| positions with `coord_dp >= 3` | 38,043 of 45,415 = **83.8 %** (7,372 at 2 or fewer) |

Read the NGSA comparison correctly: a blanket "the gazetteer is 10 km from the
sheet" would be the wrong conclusion. Nigerian place names repeat — there are 14
records called *Aba* — so a label on the paper map can legitimately be 10 km from
the nearest *same-name* hamlet as well as 100 m from one. The 15 major cities,
where a single correct location exists, agree to 0.55 km median. That is the
accuracy figure to quote.

## What it is not

* **Not every settlement.** GeoNames is dense in the south-east and south-west and
  sparse in the north, because that is where contributors mapped. A blank area is
  not an empty area.
* **Not population data.** 450 of 45,415 carry a population, and those are
  round-number estimates from various dates. Do not sum them.
* **Uses the 2014 dump.** Newer GeoNames builds exist; the mirror this script can
  reach from a sandboxed environment is that one. The date is recorded per row in
  `moddate` so a reader can see how old a coordinate is.
* **Mixed positional quality.** GeoNames coordinates come from a century of
  different sources — survey, gazetteer digitisation, GPS. For a hamlet, expect
  hundreds of metres to a few km; for a city, the sub-km figures above.

Full machine-readable counts: `towns_report.json`. Overlay used to check it:
`towns_geonames_qc.png`.
