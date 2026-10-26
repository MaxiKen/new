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
| `alt_names` | up to 300 characters of recorded alternative spellings |
| `feature_code`, `feature_type` | `PPL` village/town (45,141), `PPLA` state capital (36), `PPLA2` (82), `PPLC` national capital (1 — Abuja), `PPLX` section of a place (44), `PPLQ` abandoned (40), `PPLL` locality (41), `PPLS` (25), `PPLF` farm (4), `PPLR` religious (1), with the plain-language type beside each |
| `state` | state name, from the state polygon the point falls in |
| `state_gn` | the state GeoNames itself records (70 % of places have none) |
| `state_agree` | TRUE/FALSE where both exist — they agree on **93.6 %** of 31,486 comparisons; disagreeing rows are worth a look before trusting either |
| `admin1_code`, `admin2_code`, `lga` | GeoNames' own codes; `lga` is nearly always NULL because GeoNames has almost no Nigerian LGA coverage (11 of 45,415) and no LGA has been invented from elsewhere |
| `population` | 0 where GeoNames records none; only **450** places carry a figure |
| `elevation_m`, `dem_m`, `timezone`, `moddate` | as recorded by GeoNames |
| `in_nigeria` | point falls inside `national_territory` |
| `ngsa_town_km` | distance to the nearest NGSA `towns` label, km |
| `dup_group` | places with the same name in the same state within 5 km, numbered — **642 rows** are a second spelling of a settlement already in the layer. `dup_group IS NULL` drops them; nothing was deleted |

## Accuracy — measured, not asserted

| check | result |
|---|---|
| inside the national territory | **44,915 of 45,415 = 98.9 %** |
| the 500 outside | median **0.8 km** beyond the border (generalisation), worst 292 km (a place GeoNames locates in a neighbouring country) |
| against published coordinates for 15 major cities (independent of this repository) | median **0.55 km**, worst 5.7 km (Ibadan) |
| against the NGSA map labels — for each of the 404 named labels, the nearest same-name gazetteer place | **257 within 15 km**, median 10.8 km, 90th percentile 98 km |
| state agreement, GeoNames' own field vs. the polygon | **93.6 %** of 31,486 |
| state present | 99.8 % of rows (from the polygon) |

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
