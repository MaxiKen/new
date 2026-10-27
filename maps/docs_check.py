#!/usr/bin/env python3
"""Test every number in `LAYERS.md` against the shipped GeoPackage.

A catalogue that drifts from the data is worse than no catalogue: it is read as
fact. The summary table and the section headings both quote a feature count, a
CRS, a geometry type, a length or area, and an in-Nigeria share. This script
parses those claims and checks each one against the file (with the measurements
`audit_layers.py` already made, in `layer_audit.json`).

It reports the claim, the measurement, and a verdict, and exits non-zero if any
claim is wrong, so the check can gate a release.

Run:  python docs_check.py          (after audit_layers.py)
"""
import json
import pathlib
import re
import sys

import pyogrio
import geopandas as gpd

HERE = pathlib.Path(__file__).parent
P = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
DOC = HERE / "LAYERS.md"
OUT = HERE / "docs_check.json"

audit = json.load(open(HERE / "layer_audit.json"))["layers"]
found = {n for n, _ in pyogrio.list_layers(P)}
text = DOC.read_text()

# ---- summary table ---------------------------------------------------------
# | # | `layer` | n | CRS | geometry | in Nigeria | purpose |
rows = re.findall(
    r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*([\d,]+)\s*\|\s*(\d+)\s*\|\s*([A-Za-z]+)\s*\|\s*"
    r"([^|]+)\|", text, re.M)
checks = []
for name, n, crs, geom, inside in rows:
    n = int(n.replace(",", ""))
    rec = audit.get(name)
    if rec is None:
        checks.append(dict(layer=name, check="present in file", doc="listed", measured=None,
                           ok=False))
        continue
    checks.append(dict(layer=name, check="feature count", doc=n,
                       measured=rec["features"], ok=rec["features"] == n))
    checks.append(dict(layer=name, check="CRS", doc=crs,
                       measured=(rec["crs"] or "").replace("EPSG:", ""), ok=rec["crs"] == f"EPSG:{crs}"))
    types = set(rec["geometry_types_present"])
    doc_type = geom.rstrip("s") if geom not in ("MultiPolygon",) else "MultiPolygon"
    ok_geom = (doc_type in types) or (geom == "MultiPolygon" and "MultiPolygon" in types)
    checks.append(dict(layer=name, check="geometry type", doc=geom,
                       measured="/".join(sorted(types)), ok=ok_geom))
    # in-Nigeria column: "100 %", "463/486", "same", "83.1 % of 41,194 km", "9.2 %*"
    inside = inside.strip().replace("*", "")
    m = re.match(r"([\d.]+)\s*%", inside)
    if m and rec.get("frac_inside") is not None:
        checks.append(dict(layer=name, check="in-Nigeria share", doc=float(m.group(1)),
                           measured=round(100 * rec["frac_inside"], 1),
                           ok=abs(100 * rec["frac_inside"] - float(m.group(1))) <= 0.15))
    m = re.match(r"(\d+)/(\d+)", inside)
    if m:
        checks.append(dict(layer=name, check="in-Nigeria count", doc=int(m.group(1)),
                           measured=rec.get("features_inside_nigeria"),
                           ok=rec.get("features_inside_nigeria") == int(m.group(1))))

# every layer in the file must be in the summary table
listed = {r[0] for r in rows}
for name in sorted(found - listed):
    checks.append(dict(layer=name, check="listed in the summary table", doc=None,
                       measured=None, ok=False))
for name in sorted(listed - found):
    checks.append(dict(layer=name, check="layer exists", doc="listed", measured=None, ok=False))

# ---- section headings ------------------------------------------------------
# "### 29. `poly_soil_ph` — 111 polygons, 906,612 km², 5 classes"
heads = re.findall(r"^###\s+(\d+)\.\s*`([^`]+)`\s*—\s*(.+)$", text, re.M)
for num, name, claim in heads:
    rec = audit.get(name, {})
    m = re.match(r"([\d,]+)\s+(rows|polygons|points|lines)", claim)
    if m:
        want = int(m.group(1).replace(",", ""))
        checks.append(dict(layer=name, check="heading count", doc=want,
                           measured=rec.get("features"), ok=rec.get("features") == want))
    m = re.search(r"([\d,]+)\s*km²", claim)
    if m:
        want = float(m.group(1).replace(",", ""))
        got = rec.get("area_km2")
        checks.append(dict(layer=name, check="heading area km2", doc=want, measured=got,
                           ok=got is not None and abs(got - want) <= max(1.0, want * 0.002)))
    # "±0.35 km" is a positional tolerance, not a length of the layer
    m = None if "±" in claim else re.search(r"\b([\d,]+)\s*km\b", claim)
    if m and "km²" not in claim:
        want = float(m.group(1).replace(",", ""))
        got = rec.get("length_km")
        checks.append(dict(layer=name, check="heading length km", doc=want, measured=got,
                           ok=got is not None and abs(got - want) <= max(1.0, want * 0.002)))
    m = re.search(r"([\d.]+)\s*%\s*inside", claim)
    if m and rec.get("frac_inside") is not None:
        want = float(m.group(1))
        got = round(100 * rec["frac_inside"], 1)
        checks.append(dict(layer=name, check="heading inside share", doc=want, measured=got,
                           ok=abs(got - want) <= 0.15))
    m = re.search(r"(\d+)\s*inside", claim)
    if m and rec.get("features_inside_nigeria") is not None:
        checks.append(dict(layer=name, check="heading inside count", doc=int(m.group(1)),
                           measured=rec["features_inside_nigeria"],
                           ok=rec["features_inside_nigeria"] == int(m.group(1))))

# sections present: every layer needs one (the gazetteer points at its own file)
sectioned = {r[1] for r in heads}
for name in sorted(found - sectioned):
    checks.append(dict(layer=name, check="has its own section", doc=None, measured=None, ok=False))

# ---- header totals ---------------------------------------------------------
m = re.search(r"\*\*(\d+) vector layers,\s+([\d,]+) features[^*]*\*\*", text)
if not m and "vector layers" in text:
    checks.append(dict(layer="(file)", check="header totals are parseable",
                       doc="vector layers, ... features", measured="matched nothing", ok=False))
if m:
    n_layers = len(found)
    n_feat = sum(v["features"] for v in audit.values())
    checks.append(dict(layer="(file)", check="header layer count",
                       doc=int(m.group(1)), measured=n_layers, ok=int(m.group(1)) == n_layers))
    checks.append(dict(layer="(file)", check="header feature count",
                       doc=int(m.group(2).replace(",", "")), measured=n_feat,
                       ok=int(m.group(2).replace(",", "")) == n_feat))
# the deliverable must be one CRS. This used to check a three-CRS split sentence;
# the sentence is now a one-CRS claim, and the reprojections it used to describe
# are checked against the file they live in.
assert "every one in EPSG:4326" in text or "every layer in EPSG:4326" in text, \
    "LAYERS.md no longer states the single-CRS property"
_crs_bad = sorted({rec["crs"] for rec in audit.values()} - {"EPSG:4326"})
checks.append(dict(layer="(file)", check="every layer is EPSG:4326",
                   doc="every one in EPSG:4326", measured=sorted({rec["crs"] for rec in audit.values()}),
                   ok=not _crs_bad))

# the five reprojections: LAYERS.md's table against their own file
COPIES = HERE / "Nigeria_Geology_Minerals_projected_copies.gpkg"
_cop_layers = {n for n, _ in pyogrio.list_layers(COPIES)} if COPIES.exists() else set()
_cop_rows = re.findall(r"^\|\s*`([a-z0-9_]+)`\s*\|\s*EPSG:(\d+)\s*\|\s*`([a-z0-9_]+)`\s*\|\s*([\d,]+)\s*\|",
                       text, re.M)
checks.append(dict(layer="(copies)", check="the reprojection table lists the file's layers",
                   doc=len(_cop_layers), measured=len(_cop_rows),
                   ok=len(_cop_rows) == len(_cop_layers) == 5))
for name, srs, parent, n in _cop_rows:
    ok = name in _cop_layers
    checks.append(dict(layer="(copies)", check=f"{name} is in the copies file",
                       doc="listed", measured=ok, ok=ok))
    if not ok:
        continue
    info = pyogrio.read_info(COPIES, layer=name)
    checks.append(dict(layer="(copies)", check=f"{name} CRS", doc=f"EPSG:{srs}",
                       measured=info["crs"], ok=info["crs"] == f"EPSG:{srs}"))
    checks.append(dict(layer="(copies)", check=f"{name} rows",
                       doc=int(n.replace(",", "")), measured=info["features"],
                       ok=info["features"] == int(n.replace(",", ""))))
    checks.append(dict(layer="(copies)", check=f"{name} parent is in the deliverable",
                       doc=parent, measured=parent in found, ok=parent in found))

# ---- the same claims, in the README's own layer table ------------------------
# Two documents quote the same figures. A number corrected in one and not the
# other is the most ordinary way for a package to start contradicting itself.
readme = HERE / "README.md"
if readme.exists():
    rtext = readme.read_text()
    rrows = re.findall(r"^\|\s*`([^`]+)`\s*\|\s*([\d,]+)\s*\|\s*(\d+)\s*\|\s*"
                       r"([A-Za-z]+)\s*\|([^|]*)\|([^|]*)\|", rtext, re.M)
    for name, n, crs, geom, purpose, inside in rrows:
        rec = audit.get(name)
        if rec is None:
            checks.append(dict(layer=name, check="README: present in file", doc="listed",
                               measured=None, ok=False))
            continue
        checks.append(dict(layer=name, check="README: feature count",
                           doc=int(n.replace(",", "")),
                           measured=rec["features"], ok=rec["features"] == int(n.replace(",", ""))))
        checks.append(dict(layer=name, check="README: CRS", doc=crs,
                           measured=rec["crs"], ok=rec["crs"] == f"EPSG:{crs}"))
        types = set(rec["geometry_types_present"])
        checks.append(dict(layer=name, check="README: geometry type", doc=geom,
                           measured="/".join(sorted(types)),
                           ok=geom in types or geom.rstrip("s") in types))
        cell = inside.strip().replace("*", "")
        m = re.match(r"([\d.]+)\s*%", cell)
        if m and rec.get("frac_inside") is not None:
            checks.append(dict(layer=name, check="README: in-Nigeria share", doc=float(m.group(1)),
                               measured=round(100 * rec["frac_inside"], 1),
                               ok=abs(100 * rec["frac_inside"] - float(m.group(1))) <= 0.15))
        m = re.search(r"(\d[\d,]*)/(\d[\d,]*)", cell)
        if m:
            want_in = int(m.group(1).replace(",", ""))
            checks.append(dict(layer=name, check="README: inside count", doc=want_in,
                               measured=rec.get("features_inside_nigeria"),
                               ok=rec.get("features_inside_nigeria") == want_in))
            checks.append(dict(layer=name, check="README: total count",
                               doc=int(m.group(2).replace(",", "")),
                               measured=rec["features"],
                               ok=rec["features"] == int(m.group(2).replace(",", ""))))
        # any length quoted in the row, in km, must be the measured length
        if rec.get("length_km") and "±" not in purpose + inside:
            for km in re.findall(r"(?<![\d.])(\d{1,3}(?:,\d{3})*)\s*km(?![²2])", purpose + " " + inside):
                val = int(km.replace(",", ""))
                if val < 100:
                    continue          # tolerances, not lengths
                checks.append(dict(layer=name, check="README: length km", doc=val,
                                   measured=rec["length_km"], ok=abs(rec["length_km"] - val) <= 1.5))

# ---- the raster catalogue's table -------------------------------------------
rdoc = HERE / "RASTER_LAYERS.md"
if rdoc.exists():
    fits = {f["layer"]: f for f in json.load(open(HERE / "raster_georeferencing.json"))}
    for row in re.findall(r"^\| `(raster_[a-z_]+)` \|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|"
                          r"([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|", rdoc.read_text(), re.M):
        layer = row[0]
        f = fits.get(layer)
        if f is None:
            checks.append(dict(layer=layer, check="raster: has a fit record", doc="listed",
                               measured=None, ok=False))
            continue
        px = row[2].strip().replace("×", "x")
        want_px = "x".join(str(v) for v in f["native_px"])
        checks.append(dict(layer=layer, check="raster: native px", doc=px, measured=want_px,
                           ok=px == want_px))
        km = row[3].strip().replace("×", "x")
        want_km = f"{f['km_per_px_ew']:.2f} x {f['km_per_px_ns']:.2f}"
        checks.append(dict(layer=layer, check="raster: km/px", doc=km, measured=want_km,
                           ok=km == want_km))
        m = re.search(r"([\d.]+)", row[4])
        if m:
            checks.append(dict(layer=layer, check="raster: border offset km",
                               doc=float(m.group(1)), measured=f["border_offset_km"],
                               ok=abs(f["border_offset_km"] - float(m.group(1))) <= 0.05))
        sides_doc = [x.strip().replace("\u2212", "-").replace("+", "") for x in row[5].split("/")]
        sides = f["border_sides_km"]
        sides_meas = [f"{sides[k]:+.0f}".replace("+", "") for k in ("north", "south", "west", "east")]
        checks.append(dict(layer=layer, check="raster: side offsets", doc=sides_doc,
                           measured=sides_meas, ok=sides_doc == sides_meas))
        m = re.search(r"([\d.]+)", row[7])
        if m:
            checks.append(dict(layer=layer, check="raster: overlap", doc=float(m.group(1)),
                               measured=round(f["iou"], 3),
                               ok=abs(f["iou"] - float(m.group(1))) <= 0.001))

# ---- field tables: every field the catalogue names must exist in that layer ---
# A field table is read as the layer's schema. This checks it against the schema.
import collections
cols_by_layer = {}
for name in found:
    info = pyogrio.read_info(P, layer=name)
    cols_by_layer[name] = set(info["fields"])
current = None
for line in text.splitlines():
    h = re.match(r"^###\s+\d+\.\s+`([^`]+)`", line)
    if h:
        current = h.group(1)
        continue
    if re.match(r"^#{2,3}\s", line):
        current = None
        continue
    if current is None or current not in cols_by_layer or not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not cells or not cells[0].startswith("`") or set(cells[0]) <= set("-: "):
        continue
    for tok in re.findall(r"`([^`]+)`", cells[0]):
        for piece in [x.strip() for x in tok.split(",")]:
            # `canvas_x/y` is shorthand for canvas_x and canvas_y
            parts = [piece]
            if "/" in piece:
                left, right = [x.strip() for x in piece.split("/", 1)]
                prefix = left.rsplit("_", 1)[0] + "_" if "_" in left else ""
                parts = [left, prefix + right]
            for part in parts:
                if not re.match(r"^[a-z][a-z0-9_]*$", part):
                    continue
                checks.append(dict(layer=current, check="field exists", doc=part,
                                   measured=None,
                                   ok=part in cols_by_layer[current]))


# ---- the gazetteer's own page -------------------------------------------------
# `towns_geonames.md` quotes 30-odd numbers about the same layer. They were checked
# by hand in the first pass and one of them was wrong (`elevation_m` was given as
# 45,393 non-null rows - the number of rows *without* a spot height). They are
# checked here instead.
_t = gpd.read_file(P, layer="towns_geonames")
_txt = (HERE / "towns_geonames.md").read_text()
_dp = _t["coord_dp"].value_counts()
_geo = _t.groupby("geometry").size()
_expect = [
    ("points", f"**{len(_t):,} points"),
    ("inside the territory", f"**{int(_t['in_nigeria'].sum()):,} of {len(_t):,} = "
                             f"{100 * _t['in_nigeria'].mean():.1f} %**"),
    ("state agreement", f"**{100 * _t['state_agree'].mean():.1f} %** of "
                        f"{int(_t['state_agree'].notna().sum()):,}"),
    ("agree / disagree", f"{int((_t['state_agree'] == 1).sum()):,} agree, "
                         f"{int((_t['state_agree'] == 0).sum()):,} do not"),
    ("population", f"only **{int((_t['population'] > 0).sum()):,}** places"),
    ("dem_m non-null", f"{int(_t['dem_m'].notna().sum()):,}"),
    ("elevation_m non-null", f"**{int(_t['elevation_m'].notna().sum())}** of the {len(_t):,} places"),
    ("dup_group", f"**{int(_t['dup_group'].notna().sum()):,} rows**"),
    ("coord_dp 0 and 5", f"| 0 | {_dp.get(0, 0):,} |"),
    ("coord_dp 5", f"| 5 | {_dp.get(5, 0):,} |"),
    ("2 dp or fewer", f"**{int((_t['coord_dp'] <= 2).sum()):,} entries"),
    ("3 dp or more", f"{int((_t['coord_dp'] >= 3).sum()):,} of {len(_t):,}"),
    ("PPL", f"`PPL` village/town ({int((_t['feature_code'] == 'PPL').sum()):,})"),
    ("PPLC", f"`PPLC` national capital ({int((_t['feature_code'] == 'PPLC').sum())}"),
    ("admin1_code 00", f"`admin1_code` is `00` for {int((_t['admin1_code'] == '00').sum()):,} rows"),
    ("lga", f"**{int(_t['lga'].notna().sum())} of {len(_t):,}**"),
    ("alt_names width", f"(the longest in the layer is "
                        f"{int(_t['alt_names'].dropna().str.len().max())})"),
    ("state present", f"{100 * _t['state'].notna().mean():.1f} % of rows"),
    ("shared coordinates", f"**{int(_geo[_geo > 1].sum() - len(_geo[_geo > 1])):,} rows "
                           f"repeat a coordinate already used**"),
]
for _label, _want in _expect:
    checks.append(dict(layer="towns_geonames.md", check=_label, doc=_want,
                       measured=_want, ok=_want in _txt))

# the same for the named-minerals page, where the counts live in two files
_mn = gpd.read_file(P, layer="minerals_named")
_ms = gpd.read_file(P, layer="mineral_symbols")
_mtxt = (HERE / "minerals_named.md").read_text()
_expect = [
    ("named rows", f"{len(_mn):,} points, EPSG:4326, one row per printed symbol"),
    ("previously named", f"named {int(_mn['previously_named'].sum()):,} of its {len(_mn):,}"),
    ("unidentified", f"{int((_mn['tier'] == 'unidentified').sum())}"),
    ("symbols in mineral_symbols", f"It holds {len(_ms):,} rows"),
    ("non-symbols", f"{int((_ms['is_symbol'] == 0).sum())} of them are not a"),
    ("countable symbols", f"On the {int((_ms['is_symbol'] == 1).sum()):,} rows that are symbols"),
    ("in Nigeria", f"{int(_mn['in_nigeria'].sum()):,} of them fall inside the"),
    ("outside the territory", f"The other {int((~_mn['in_nigeria']).sum())} are kept rather than dropped"),
]
for _label, _want in _expect:
    checks.append(dict(layer="minerals_named.md", check=_label, doc=_want,
                       measured=_want, ok=_want in _mtxt))

# ---- the DEM built from the sheet -------------------------------------------
# The DEM's numbers are the ones a reader will act on (a class means a height), so
# every one of them in RASTER_LAYERS.md is checked against dem_from_sheet.json - the
# per-class table and the accuracy table - rather than trusted.
dem_path = HERE / "dem_from_sheet.json"
if dem_path.exists() and rdoc.exists():
    dem = json.load(open(dem_path))
    for row in re.findall(r"^\| (\d) \| ([\d,]+) – ([\d,]+) \| ([\d.]+) \| ([\d.]+) % \| "
                          r"([\d,]+) \|", rdoc.read_text(), re.M):
        k = int(row[0])
        c = dem["classes"][k - 1]
        for label, doc, measured in (
                ("dem: class lo m", float(row[1].replace(",", "")), c["metres"][0]),
                ("dem: class hi m", float(row[2].replace(",", "")), c["metres"][1]),
                ("dem: class value m", float(row[3]), c["midpoint"]),
                ("dem: class share pct", float(row[4]), c["share_pct"]),
                ("dem: class area km2", float(row[5].replace(",", "")), c["area_km2"])):
            checks.append(dict(layer=f"dem_from_sheet (class {k})", check=label, doc=doc,
                               measured=measured, ok=abs(float(doc) - float(measured)) < 1e-6))
    acc = re.findall(r"\| \*\*this build\*\* \| ([\d.]+) % \| ([\d.]+) % \| (\d+) m \|",
                     rdoc.read_text())
    if acc:
        a = acc[0]
        for label, doc, measured in (
                ("dem: exact class pct", float(a[0]), dem["validation"]["exact_class_pct"]),
                ("dem: within one class pct", float(a[1]),
                 dem["validation"]["within_one_class_pct"]),
                ("dem: mae m", float(a[2]), dem["validation"]["mae_m"])):
            checks.append(dict(layer="dem_from_sheet", check=label, doc=doc, measured=measured,
                               ok=abs(float(doc) - float(measured)) < 1e-6))
    else:
        checks.append(dict(layer="dem_from_sheet", check="dem: accuracy table present",
                           doc="missing", measured=None, ok=False))
    sw = re.findall(r"\| printed swatches alone \| ([\d.]+) % \| ([\d.]+) % \|", rdoc.read_text())
    if sw:
        for label, doc, measured in (
                ("dem: swatch exact pct", float(sw[0][0]),
                 dem["validation"]["swatch_only_exact_class_pct"]),
                ("dem: swatch within pct", float(sw[0][1]),
                 dem["validation"]["swatch_only_within_one_pct"])):
            checks.append(dict(layer="dem_from_sheet", check=label, doc=doc, measured=measured,
                               ok=abs(float(doc) - float(measured)) < 1e-6))

# ---- the README's own claim count -------------------------------------------
# README says "(408 claims in all)". That sentence is a claim too, so it is
# checked against this run's total; a new block that changes the count without
# updating the sentence fails here.
_readme = (HERE / "README.md").read_text()
_m = re.search(r"\((\d[\d,]*) claims in all\)", _readme)
if _m:
    _stated = int(_m.group(1).replace(",", ""))
    _total = len(checks) + 1  # this count is itself one of the claims
    checks.append(dict(layer="README.md", check="stated claim count", doc=str(_stated),
                       measured=_total, ok=_stated == _total))

bad = [c for c in checks if not c["ok"]]
json.dump({"checks": checks, "failures": bad}, open(OUT, "w"), indent=1)

print(f"{len(checks)} claims checked against the file, {len(bad)} wrong\n")
for c in bad:
    print(f"  ! {c['layer']:34s} {c['check']:32s} doc={c['doc']!r:>14}  measured={c['measured']!r}")
print(f"\nwrote {OUT.name}")
sys.exit(1 if bad else 0)
