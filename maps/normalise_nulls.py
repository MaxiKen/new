#!/usr/bin/env python3
"""Empty strings are not values: replace `''` with NULL in every text column.

`LAYERS.md` states the file's convention - **missing values are NULL, never `""`**
- because the two are not interchangeable in practice:

  * `WHERE period IS NULL` and `WHERE period = ''` return different rows, so a
    query written against one convention silently misses data under the other;
  * `''` is a value to a text function: `length('')` is 0 and `'' || name` is not
    `name`;
  * a join on `''` matches every missing value at once;
  * in the projected copies it made the copies disagree with the layer they copy:
    `geology_units` had 24 NULL periods, `geology_units_utm32n` had 5 NULL and 19
    empty - so `WHERE period IS NULL` gave two different answers depending on
    which copy you asked.

Two places broke the convention: `build_towns.py` filled absent alternate names
with `''`, and every layer that was read into a GeoDataFrame and written out again
turned its NULLs into `''` - pandas stores NULL in an object column as `NaN`, and
GDAL writes `NaN` to a text field as an empty string. 131,755 cells across nine
layers were affected, all invisible to `PRAGMA integrity_check`.

The repair goes through GDAL rather than SQL: an `UPDATE` on a layer with a
spatial index fires the GeoPackage rtree triggers, which call SpatiaLite
functions (`ST_IsEmpty`, `ST_MinX`) that plain SQLite does not have. Rewriting the
layer lets GDAL keep the index and the registers consistent.

Idempotent: a second run finds nothing. Records what it changed in
`null_normalisation.json`, with a checksum of the geometry before and after so the
claim "only empty strings changed" is testable.

Run:  python normalise_nulls.py
"""
import hashlib
import json
import pathlib
import sqlite3

import geopandas as gpd
import pandas as pd
import pyogrio

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "null_normalisation.json"


def geometry_digest(g):
    h = hashlib.sha256()
    for w in g.geometry.to_wkb():
        h.update(w if w else b"")
    return h.hexdigest()[:16]


def main(gpkg=GPKG, out=OUT):
    con = sqlite3.connect(gpkg)
    layers = [r[0] for r in con.execute(
        "SELECT table_name FROM gpkg_contents WHERE data_type = 'features' ORDER BY 1")]
    findings = {}
    for t in layers:
        for col, typ in [(r[1], r[2]) for r in con.execute(f'PRAGMA table_info("{t}")')]:
            if typ != "TEXT":
                continue
            n = con.execute(f'SELECT count(*) FROM "{t}" WHERE "{col}" = \'\'').fetchone()[0]
            if n:
                findings.setdefault(t, {})[col] = n
    con.close()

    report = {"file": gpkg.name, "layers": {}, "cells_normalised": sum(
        v for cols in findings.values() for v in cols.values())}
    for t, cols in findings.items():
        g = gpd.read_file(gpkg, layer=t)
        before_rows, before_hash = len(g), geometry_digest(g)
        for col in cols:
            if col in g.columns:
                g[col] = g[col].astype(object).where(pd.notna(g[col]), None).replace("", None)
        pyogrio.write_dataframe(g, gpkg, layer=t, driver="GPKG", append=False)
        back = gpd.read_file(gpkg, layer=t)
        assert len(back) == before_rows, (t, len(back), before_rows)
        assert geometry_digest(back) == before_hash, f"{t}: geometry changed"
        assert not any((back[c].astype(str) == "").any() for c in cols if c in back.columns)
        report["layers"][t] = dict(rows=before_rows, cells=sum(cols.values()),
                                   columns=cols, geometry_unchanged=True)
        print(f"  {t:34s} {sum(cols.values()):7,d} cells -> NULL  ({before_rows:,} rows, "
              f"geometry unchanged)")

    # verify the promise on the finished file
    con = sqlite3.connect(gpkg)
    left = {}
    for t in [r[0] for r in con.execute(
            "SELECT table_name FROM gpkg_contents WHERE data_type = 'features'")]:
        for col, typ in [(r[1], r[2]) for r in con.execute(f'PRAGMA table_info("{t}")')]:
            if typ != "TEXT":
                continue
            n = con.execute(f'SELECT count(*) FROM "{t}" WHERE "{col}" = \'\'').fetchone()[0]
            if n:
                left[f"{t}.{col}"] = n
    con.close()
    report["remaining_empty_strings"] = left
    # keep the first run's record: a later run finds nothing to do and would
    # otherwise overwrite the evidence with zeros
    if out.exists():
        prev = json.load(open(out))
        if prev.get("cells_normalised") and not report["cells_normalised"]:
            report["history"] = {"cells_normalised": prev["cells_normalised"],
                                 "layers": prev.get("layers", {})}
            report["note"] = ("nothing to do on this run; the counts in `history` are the "
                              "empty strings this sweep removed when it was first run")
    json.dump(report, open(out, "w"), indent=1)

    if not findings:
        print("no empty strings found - nothing to do")
    print(f"\n{report['cells_normalised']:,} cells normalised in {len(findings)} layers; "
          f"empty strings left: {sum(left.values())}")
    print(f"wrote {out.name}")
    return report


if __name__ == "__main__":
    main()
