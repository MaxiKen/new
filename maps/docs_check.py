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
m = re.search(r"\*\*(\d+) vector layers, ([\d,]+) features\*\*", text)
if m:
    n_layers = len(found)
    n_feat = sum(v["features"] for v in audit.values())
    checks.append(dict(layer="(file)", check="header layer count",
                       doc=int(m.group(1)), measured=n_layers, ok=int(m.group(1)) == n_layers))
    checks.append(dict(layer="(file)", check="header feature count",
                       doc=int(m.group(2).replace(",", "")), measured=n_feat,
                       ok=int(m.group(2).replace(",", "")) == n_feat))
m = re.search(r"(\d+) layers in EPSG:4326 \(([\d,]+) features\), (\d+) in EPSG:32632 \(([\d,]+)\), "
              r"(\d+) in EPSG:6933 \(([\d,]+)\)", text)
if m:
    want = {4326: (int(m.group(1)), int(m.group(2).replace(",", ""))),
            32632: (int(m.group(3)), int(m.group(4).replace(",", ""))),
            6933: (int(m.group(5)), int(m.group(6).replace(",", "")))}
    got = {}
    for rec in audit.values():
        crs = int((rec["crs"] or "EPSG:0").split(":")[1])
        a, b = got.get(crs, (0, 0))
        got[crs] = (a + 1, b + rec["features"])
    for crs, (nl, nf) in want.items():
        checks.append(dict(layer="(file)", check=f"header EPSG:{crs} layers", doc=nl,
                           measured=got.get(crs, (0, 0))[0], ok=got.get(crs, (0, 0))[0] == nl))
        checks.append(dict(layer="(file)", check=f"header EPSG:{crs} features", doc=nf,
                           measured=got.get(crs, (0, 0))[1], ok=got.get(crs, (0, 0))[1] == nf))

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

bad = [c for c in checks if not c["ok"]]
json.dump({"checks": checks, "failures": bad}, open(OUT, "w"), indent=1)

print(f"{len(checks)} claims checked against the file, {len(bad)} wrong\n")
for c in bad:
    print(f"  ! {c['layer']:34s} {c['check']:32s} doc={c['doc']!r:>14}  measured={c['measured']!r}")
print(f"\nwrote {OUT.name}")
sys.exit(1 if bad else 0)
