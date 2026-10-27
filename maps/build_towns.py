#!/usr/bin/env python3
"""Build `towns_geonames`: the GeoNames gazetteer of Nigerian places, as a layer.

Why a second towns layer
------------------------
`towns` in this GeoPackage is 486 labels read off the 2011 NGSA sheet, and 82 of
them were never named on the sheet.  That is what the map draws, not what exists:
Nigeria has tens of thousands of named settlements.  This layer is the gazetteer -
every populated place GeoNames records for Nigeria - and it is kept separate so
the surveyed-by-hand layer stays exactly as printed.  Use `towns` when you need to
match the paper map; use this one when you need coverage.

Source, pinned
--------------
GeoNames, CC BY 4.0.  The dump used is the split SQLite build of the GeoNames
`allCountries` export (2014-10-02) mirrored at

    github.com/albert-decatur/geonames2sqlite  @1515c016

Nine 50 MB zip chunks make one 432 MB zip, which holds a 1.46 GB SQLite file.
This script downloads the chunks, reassembles them, and keeps only the Nigerian
populated places (feature class `P`, 45,415 rows) plus the admin1/admin2 name
tables.  Nothing else is stored.

What is written
---------------
Layer `towns_geonames`, EPSG:4326 points, one row per GeoNames record:

  geonameid      GeoNames id (the stable key)
  name           the name as GeoNames prefers it
  ascii_name     ASCII-folded name
  alt_names      up to 300 chars of the recorded alternative spellings
  feature_code   PPL, PPLA (state capital), PPLA2, PPLC (national capital), ...
  feature_type   plain-language type: "populated place", "seat of ..."
  admin1_code    GeoNames state code, and `state` its name
  admin2_code    GeoNames LGA code, and `lga` its name (sparse: GeoNames NG has
                 almost no LGA coverage - 11 of 45,415 - so this is mostly NULL
                 and no LGA has been invented from anywhere else)
  population     0 where GeoNames records none; only 450 places carry a figure
  elevation_m    spot elevation where recorded, NULL otherwise
  dem_m          the SRTM value GeoNames stores for the point
  timezone
  moddate        when GeoNames last touched the record
  in_nigeria     point is inside `national_territory`
  ngsa_town_km   distance to the nearest NGSA `towns` label, km (NULL if none)
  dup_group      places sharing a name inside the same state, numbered; NULL
                 for the first occurrence - use `dup_group IS NULL` to drop the
                 duplicate spellings of one settlement

and `towns_report.json` with the counts and the two independent checks:
  * how many points fall inside the national territory, and
  * the distance from GeoNames to the 486 NGSA labels when the names match,
    which measures the gazetteer against an independent source instead of
    asserting that it is accurate.
"""
import json
import math
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

from gpkg_write import write_layer
from pyproj import Geod
from shapely.geometry import Point

HERE = pathlib.Path(__file__).parent
# distances are measured on a projection centred on Nigeria, so a km means a km
NG_AEQD = "+proj=aeqd +lat_0=9.08 +lon_0=8.68 +datum=WGS84 +units=m +no_defs"
GEOD = Geod(ellps="WGS84")
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
REPORT = HERE / "towns_report.json"
LAYER = "towns_geonames"

REPO = "albert-decatur/geonames2sqlite"
COMMIT = "1515c016027be9febacff4b272fcbde6a4d28dff"

# State polygons for the state column: Natural Earth admin-1, public domain, so
# the attribution can be shipped without a licence question.  (GeoNames itself
# leaves the state empty on 30 % of Nigeria's places.)
NE_REPO = "nvkelso/natural-earth-vector"
NE_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
NE_PATH = "geojson/ne_10m_admin_1_states_provinces.geojson"
NE_SHA = None   # resolved from the pinned tree, see fetch_states()

# Published coordinates for a spot check of the gazetteer, independent of
# anything in this repository: city -> (lat, lon).
KNOWN = {
    "Lagos": (6.455, 3.384), "Kano": (12.002, 8.517), "Ibadan": (7.378, 3.947),
    "Abuja": (9.058, 7.495), "Port Harcourt": (4.777, 7.013),
    "Benin City": (6.338, 5.626), "Kaduna": (10.523, 7.441),
    "Maiduguri": (11.831, 13.151), "Enugu": (6.441, 7.499), "Jos": (9.896, 8.858),
    "Ilorin": (8.497, 4.542), "Aba": (5.107, 7.367), "Sokoto": (13.062, 5.244),
    "Calabar": (4.976, 8.338), "Uyo": (5.038, 7.913),
}
CHUNKS = [
    "0635e491c79af498ace637b0aedf186e20930ceb",
    "ca2d8bc7770ca5cdde66fb9313bf1084197daff2",
    "70d9c9de93c2160ab349e3aacf14ce400c3c0049",
    "33bd389f74a1fa5c25f4b5700041417b85deee0e",
    "d076e50ee69cbed1e02376652975e253a83b2d8b",
    "c334d399f4f3cf2096e8b79fc6bf95706ba6285b",
    "8c60cc596bb9fb45a26faefc6a6cb079d183a082",
    "879a92282a5d1735302bf3ac99a26677b9e5acfa",
    "74b1cda24f643925cb1b4f25a3659bc11d8e1b36",
]


def fetch_dump(cache):
    """Download and reassemble the pinned GeoNames SQLite build."""
    cache = pathlib.Path(cache)
    db = cache / "geonames.sqlite"
    if db.exists():
        print(f"  using cached {db}")
        return db
    cache.mkdir(parents=True, exist_ok=True)
    blob = f"https://api.github.com/repos/{REPO}/git/blobs/{{sha}}"
    parts = []
    for i, sha in enumerate(CHUNKS, 1):
        f = cache / f"{sha}.zip"
        if not f.exists():
            print(f"  chunk {i}/{len(CHUNKS)} ...", end="", flush=True)
            req = urllib.request.Request(blob.format(sha=sha),
                                         headers={"Accept": "application/vnd.github.raw"})
            with urllib.request.urlopen(req, timeout=180) as r:
                f.write_bytes(r.read())
            print(f" {f.stat().st_size / 1e6:.0f} MB")
        parts.append(f)
    # each downloaded zip holds one 50 MB slice of a single larger zip, so the
    # slices (not the zips) are what concatenate back into an archive
    combined = cache / "geonames.zip"
    with open(combined, "wb") as out:
        for f in parts:
            out.write(subprocess.run(["unzip", "-p", str(f)], check=True,
                                     capture_output=True).stdout)
    print("  reassembling ...")
    subprocess.run(["unzip", "-o", "-q", str(combined), "-d", str(cache)], check=True)
    got = list(cache.glob("*.sqlite"))
    if not got:
        sys.exit("unzip produced no .sqlite")
    got[0].rename(db)
    combined.unlink()
    for f in parts:
        f.unlink()
    return db


def fetch_states(cache):
    """Nigeria's 37 first-level units, from Natural Earth (public domain)."""
    cache = pathlib.Path(cache)
    f = cache / "ne_adm1.geojson"
    if f.exists():
        return gpd.read_file(f).query("admin == 'Nigeria'").reset_index(drop=True)
    cache.mkdir(parents=True, exist_ok=True)
    tree = json.load(urllib.request.urlopen(
        f"https://api.github.com/repos/{NE_REPO}/git/trees/{NE_COMMIT}", timeout=180))
    gdir = next(t["sha"] for t in tree["tree"] if t["path"] == "geojson")
    tree = json.load(urllib.request.urlopen(
        f"https://api.github.com/repos/{NE_REPO}/git/trees/{gdir}", timeout=180))
    sha = next(t["sha"] for t in tree["tree"]
               if t["path"] == NE_PATH.split("/")[-1])
    req = urllib.request.Request(
        f"https://api.github.com/repos/{NE_REPO}/git/blobs/{sha}",
        headers={"Accept": "application/vnd.github.raw"})
    print("  natural earth admin-1 ...", end="", flush=True)
    with urllib.request.urlopen(req, timeout=300) as r:
        f.write_bytes(r.read())
    print(f" {f.stat().st_size / 1e6:.0f} MB")
    return gpd.read_file(f).query("admin == 'Nigeria'").reset_index(drop=True)


def read_nigeria(db):
    """Nigeria's populated places, with GeoNames' own state and LGA names."""
    con = sqlite3.connect(db)
    a1 = {(r[0], r[1]): r[2] for r in con.execute(
        "select adm0_code, adm1_code, adm1_name from admin1codesascii")}
    a2 = {(r[0], r[1], r[2]): r[3] for r in con.execute(
        "select adm0_code, adm1_code, adm2_code, adm2_name from admin2codes")}
    fc = {r[0]: (r[1], r[2]) for r in con.execute(
        "select code, name, description from featurecodes_en")}
    rows = con.execute("""
        select geonameid, name, asciiname, alternatenames, latitude, longitude,
               featurecode, admin1code, admin2code, population, elevation, dem,
               timezone, modificationdate
        from allCountries
        where countrycode = 'NG' and featureclass = 'P'""").fetchall()
    con.close()
    df = pd.DataFrame(rows, columns=[
        "geonameid", "name", "ascii_name", "alt_names", "lat", "lon",
        "feature_code", "admin1_code", "admin2_code", "population",
        "elevation_m", "dem_m", "timezone", "moddate"])
    df["feature_type"] = df.feature_code.map(lambda c: fc.get(c, ("", ""))[0])
    df["state"] = [a1.get(("NG", c)) for c in df.admin1_code]
    df["lga"] = [a2.get(("NG", a, b)) for a, b in zip(df.admin1_code, df.admin2_code)]
    # a place with no recorded alternative names has none: NULL, not '' - the
    # file's convention, and the difference between "absent" and "empty" that a
    # text query can see
    df["alt_names"] = df.alt_names.str.slice(0, 120)
    df["alt_names"] = df.alt_names.replace("", None)
    df["population"] = df.population.fillna(0).astype("int64")
    return df


def norm(s):
    """Fold a name for matching: no accents, no punctuation, no 'town' suffix."""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().replace("-", " ").replace("'", "")
    for tail in (" town", " township", " village"):
        if s.endswith(tail):
            s = s[: -len(tail)]
    return " ".join(s.split())


def spot_check(g):
    """Distance from published coordinates to the nearest gazetteer place of that
    name - an accuracy statement that does not depend on this repository."""
    geo = g.to_crs(NG_AEQD)
    out = {}
    for city, (lat, lon) in KNOWN.items():
        sub = g[(g["name"].str.lower() == city.lower())
                | (g["ascii_name"].str.lower() == city.lower())]
        if not sub.empty:
            x, y = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(NG_AEQD).iloc[0].coords[0]
            d = geo.geometry.loc[sub.index].distance(Point(x, y)).min() / 1000
            out[city] = round(float(d), 2)
    vals = list(out.values())
    return dict(cities=out, n=len(vals),
                median_km=round(float(np.median(vals)), 2) if vals else None,
                worst_km=round(float(np.max(vals)), 2) if vals else None)


def main(cache="/tmp/geonames_cache"):
    terr = gpd.read_file(GPKG, layer="national_territory").geometry.union_all()
    ngsa = gpd.read_file(GPKG, layer="towns")[["name", "geometry"]].rename(
        columns={"name": "ngsa_name"})
    ngsa["ngsa_name"] = ngsa["ngsa_name"].astype(str)

    states = fetch_states(cache)
    db = fetch_dump(cache)
    df = read_nigeria(db)
    print(f"  {len(df):,} Nigerian populated places in the gazetteer")

    g = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df.lon, df.lat)],
                         crs="EPSG:4326")
    g = g.drop(columns=["lat", "lon"])

    # --- state, from the polygon the point actually falls in ---------------
    st = states[["name_en", "geometry"]].rename(columns={"name_en": "state_ne"})
    j = gpd.sjoin(g, st, how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")]
    g["state_polygon"] = j["state_ne"].to_numpy()
    g["state_gn"] = g["state"]
    g["state_agree"] = pd.array([
        None if (pd.isna(a) or pd.isna(b) or not str(a).strip() or not str(b).strip())
        else norm(str(a)).replace(" state", "") == norm(str(b)).replace(" state", "")
        for a, b in zip(g.state_gn, g.state_polygon)], dtype="boolean")
    g["state"] = g["state_polygon"].fillna(g["state_gn"])

    # --- the checks that make the layer auditable --------------------------
    g["in_nigeria"] = g.geometry.within(terr).to_numpy()
    # WAT is WAT either side of the border, but a Nigerian gazetteer should not
    # label a place inside Nigeria with the neighbouring country's zone
    g.loc[(g["timezone"] == "Africa/Douala") & g["in_nigeria"], "timezone"] = "Africa/Lagos"
    gm = g.to_crs(NG_AEQD)                       # metres, for every distance
    ngsa_m = ngsa.to_crs(NG_AEQD)

    near = gpd.sjoin_nearest(gm, ngsa_m, how="left", distance_col="ngsa_m")
    near = near[~near.index.duplicated()]
    g["ngsa_town_km"] = (near["ngsa_m"] / 1000).round(3).to_numpy()

    # how far outside the border the ones that fall outside actually are
    outsiders = gm[~g.in_nigeria]
    terr_m = gpd.GeoSeries([terr], crs=4326).to_crs(NG_AEQD).iloc[0]
    out_km = (outsiders.geometry.distance(terr_m) / 1000).round(2) if len(outsiders) else None

    # the same settlement recorded twice under two spellings: same name, same
    # state, within 5 km.  Numbered, not deleted - the record is real, the
    # duplicate is a fact about the gazetteer, and dropping rows is not this
    # script's job.
    g["dup_group"] = pd.Series(pd.NA, index=g.index, dtype="Int64")
    key = g["ascii_name"].map(norm) + "|" + g["state"].fillna("").str.lower()
    for _, idx in g.groupby(key).groups.items():
        idx = list(idx)
        if len(idx) < 2:
            continue
        pts = gm.geometry.loc[idx]
        for n, i in enumerate(idx):
            if n and any(pts.loc[i].distance(pts.loc[j]) < 5000 for j in idx[:n]):
                g.at[i, "dup_group"] = n

    # --- name-matched cross-check against the NGSA labels ------------------
    # asked the other way round, which is the honest question: for each label the
    # paper map prints, how close is the nearest gazetteer place with that name?
    # (asking it per gazetteer row instead would be swamped by the many hamlets
    # that share a common name)
    ngsa_named = ngsa[ngsa.names_ok].copy() if "names_ok" in ngsa else ngsa.copy()
    ngsa_named = ngsa[~ngsa.ngsa_name.isin(["nan", "None", ""])].copy()
    ngsa_named["k"] = ngsa_named.ngsa_name.map(norm)
    ngsa_named = ngsa_named[ngsa_named.k != ""].to_crs(NG_AEQD)
    g["k"] = g.ascii_name.map(norm)
    gx = np.array([p.x for p in gm.geometry])
    gy = np.array([p.y for p in gm.geometry])
    lab = gpd.GeoDataFrame(
        {"k": g["k"].to_numpy(), "x": gx, "y": gy},
        geometry=gpd.points_from_xy(gx, gy), crs=NG_AEQD)
    pairs = ngsa_named.reset_index()[["index", "k", "geometry"]].merge(
        lab[["k", "geometry"]], on="k", suffixes=("_label", "_gaz"))
    pairs["d_km"] = pairs.geometry_label.distance(pairs.geometry_gaz) / 1000
    per_label = pairs.groupby("index").d_km.min()
    n_matched = int((per_label < 15).sum())
    matched = float(per_label.median()) if len(per_label) else float("nan")

    report = dict(
        source="GeoNames allCountries dump, 2014-10-02 build, CC BY 4.0",
        source_repo=f"https://github.com/{REPO}@{COMMIT[:7]}",
        layer=LAYER,
        features=int(len(g)),
        feature_codes=g.feature_code.value_counts().to_dict(),
        inside_national_territory=int(g.in_nigeria.sum()),
        inside_pct=round(100 * g.in_nigeria.mean(), 2),
        with_state=int(g.state.notna().sum()),
        with_state_pct=round(100 * g.state.notna().mean(), 1),
        with_population=int((g.population > 0).sum()),
        state_seats=int(g.feature_code.isin(["PPLA", "PPLA2", "PPLC"]).sum()),
        duplicate_spellings=int(g.dup_group.notna().sum()),
        check_against_ngsa=dict(
            ngsa_named_labels=int(len(ngsa_named)),
            labels_with_a_same_name_place_under_15km=n_matched,
            median_distance_km=round(float(matched), 2) if not math.isnan(matched) else None,
            p90_distance_km=(round(float(per_label.quantile(0.9)), 2)
                             if len(per_label) else None),
        ),
        nearest_ngsa_km_median=round(float(np.nanmedian(g.ngsa_town_km)), 2),
        state_from_polygon=int(g.state_polygon.notna().sum()),
        state_from_polygon_pct=round(100 * g.state_polygon.notna().mean(), 1),
        geonames_state_vs_polygon=dict(
            compared=int(g.state_agree.notna().sum()),
            agree=int((g.state_agree == True).sum()),
            agree_pct=round(float(100 * (g.state_agree == True).sum()
                                  / max(g.state_agree.notna().sum(), 1)), 1),
        ),
        spot_check=spot_check(g),
        outside_territory=int((~g.in_nigeria).sum()),
        outside_territory_max_km=(round(float(out_km.max()), 2)
                                  if out_km is not None and len(out_km) else None),
        outside_territory_median_km=(round(float(out_km.median()), 2)
                                     if out_km is not None and len(out_km) else None),
    )
    json.dump(report, open(REPORT, "w"), indent=1)

    # --- write -------------------------------------------------------------
    # numeric fields must be numbers: `elevation_m > 500` on TEXT compares strings
    out = g.copy()
    out["elevation_m"] = pd.to_numeric(out["elevation_m"], errors="coerce").astype("Int64")
    # -9999 is the SRTM void, and it must not be read as an elevation of -9,999 m
    out["dem_m"] = pd.to_numeric(out["dem_m"], errors="coerce")
    out.loc[(out["dem_m"] == -9999) | (out["dem_m"] < 0), "dem_m"] = pd.NA
    for code_col in ("admin1_code", "admin2_code"):
        out[code_col] = out[code_col].replace("", None)
    # how precisely GeoNames records the position, in decimal places: 7,372 of
    # the entries carry 2 or fewer, which is a position good to 1 km at best
    def _dp(v):
        t = f"{v:.6f}".rstrip("0").rstrip(".")
        return len(t.split(".")[1]) if "." in t else 0

    out["coord_dp"] = [min(_dp(x), _dp(y))
                       for x, y in zip(out.geometry.x, out.geometry.y)]
    out = out.drop(columns=[c for c in ("k", "ngsa_name") if c in out.columns])
    out = out[["geonameid", "name", "ascii_name", "alt_names", "feature_code",
               "feature_type", "state", "state_gn", "state_agree",
               "admin1_code", "admin2_code", "lga",
               "population", "elevation_m", "dem_m", "timezone", "moddate",
               "in_nigeria", "coord_dp", "ngsa_town_km", "dup_group", "geometry"]]
    write_layer(out, GPKG, LAYER)
    print(f"  wrote layer {LAYER}: {len(out):,} points")
    for k in ("inside_pct", "with_state_pct", "with_population", "state_seats",
              "duplicate_spellings", "nearest_ngsa_km_median", "check_against_ngsa"):
        print(f"  {k:24s} {report[k]}")
    # a rewritten layer loses its gpkg_contents description and can pick up
    # register debris: finish the job so the shipped layer is self-describing
    here = pathlib.Path(__file__).parent
    subprocess.run([sys.executable, str(here / "fix_gpkg_hygiene.py")], check=True)
    subprocess.run([sys.executable, str(here / "describe_layers.py")], check=True)
    print(f"  wrote {REPORT.name}")
    return report


if __name__ == "__main__":
    main(*sys.argv[1:])
