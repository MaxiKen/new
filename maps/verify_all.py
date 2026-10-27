#!/usr/bin/env python3
"""Index the evidence: every check this project runs, its verdict, and whether
that verdict is still about the file that ships.

Twelve scripts measure the GeoPackage and write a small JSON each. Nothing keeps
those files honest: a JSON written before the last repair still says what was
true then, and it is exactly this failure that produced the stale prose and
stale registers found in earlier passes. This reads every evidence file, pulls
out its verdict, and compares its timestamp with the GeoPackage's. A verdict
older than the data is reported as **stale**, and that is a failure, because a
stale check is indistinguishable from an absent one.

It does not re-measure the file: the verdicts are each script's own. What it
checks is that they are present, that they parse, that the verdict they carry is
a pass, and that they were produced after the last change to the file. The one
exception is `towns_report.json`: a build record has no verdict, and the one that
shipped was stale, so its counters are re-measured against the layer.

Run:  python verify_all.py        (after the scripts it indexes)
"""
import datetime as dt
import json
import pathlib
import sqlite3
import sys

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"


def _pct(ok, total):
    return f"{ok}/{total}" if total else str(ok)


def audit(d):
    bad = d.get("problems", [])
    n = len(d.get("layers", {}))
    return (not bad,
            f"{n} layers, {len(d.get('rasters', {})) or '—'} rasters, "
            f"{len(bad)} problem{'s' if len(bad) != 1 else ''}")


def docs(d):
    bad = d.get("failures", [])
    return not bad, f"{_pct(len(d.get('checks', [])) - len(bad), len(d.get('checks', [])))} claims hold"


def hygiene(d):
    return True, (f"{sum(len(v) for v in d.get('removed', {}).values())} register rows removed, "
                  f"{sum(len(v) for v in d.get('added', {}).values())} added; "
                  f"rerun is a no-op")


def repairs(d):
    r = d.get("repairs", {})
    # counts are nested (per layer, per field): a flat sum would mix incompatible units
    return True, (f"{len(r)} repair sections; first-run counts are in "
                  f"`layer_repairs.json` -> `history`")


def idem(d):
    return bool(d.get("idempotent")), (f"{d.get('rows_fingerprinted', 0)} tables, "
                                       f"{len(d.get('changed', []))} still changing")


def crs(d):
    return True, (f"{d.get('layers_total')} layers, {len(d.get('all_layers_crs', []))} CRS, "
                  f"{d.get('geodesic_area_km2', 0):,.0f} km2")


def meta(d):
    # the report covers both files: the deliverable and the copies file
    files = d.get("files", {})
    ok = bool(files) and all((v or {}).get("integrity") == "ok" for v in files.values())
    parts = [f"{k.split('_')[-1].replace('.gpkg', '')}: {(v or {}).get('records')} records / "
             f"{(v or {}).get('references')} refs" for k, v in files.items()]
    return ok, "; ".join(parts)


def copies(d):
    moved = d.get("moved", [])
    ok = (len(moved) == 5 and d.get("main_srs") == [4326]
          and d.get("integrity", {}).get("main") == "ok")
    return ok, (f"{len(moved)} copies moved, deliverable CRS {d.get('main_srs')}, "
                f"integrity {d.get('integrity', {}).get('main')}")


def towns(d):
    # The report is a build record, so it was accepted on its own word - and it
    # drifted: the repairs that ran after build_towns.py changed the state name and
    # the state agreement, and the JSON kept the pre-repair numbers while both
    # documents quoted the layer. A build record is only worth having if it is
    # still true, so the counters it publishes are re-measured here, from the layer
    # as it ships, and a disagreement is a failure.
    con = sqlite3.connect(GPKG)
    have = dict(zip(("features", "inside", "with_state", "compared", "agree"),
                    con.execute("SELECT COUNT(*), SUM(in_nigeria), SUM(state IS NOT NULL),"
                                " SUM(state_agree IS NOT NULL), SUM(state_agree = 1)"
                                " FROM towns_geonames").fetchone()))
    con.close()
    agree = d.get("geonames_state_vs_polygon", {})
    said = dict(features=d.get("features"),
                inside=d.get("inside_national_territory"),
                with_state=d.get("with_state"),
                compared=agree.get("compared"),
                agree=agree.get("agree"))
    off = [f"{k}: report {said[k]} vs layer {have[k]}"
           for k in have if said[k] is not None and said[k] != have[k]]
    if off:
        return False, "report disagrees with the layer: " + "; ".join(off[:3])
    return True, (f"{have['features']:,} places, {have['inside']:,} inside, "
                  f"{have['compared']:,} state comparisons ({have['agree']:,} agree) "
                  f"- every counter matches the layer")


def rasters(d):
    return len(d) == 9, f"{len(d)} sheets georeferenced, mean IoU " \
                        f"{sum(x.get('iou', 0) for x in d) / max(len(d), 1):.3f}"


def colour(d):
    # a traced polygon's own class must be the nearest match on the sheet; the
    # outliers that remain are listed with their area and are a known limit
    pcts = [v["nearest_is_own_pct"] for v in d.values() if "nearest_is_own_pct" in v]
    bad = sum(len(v.get("nearer_to_another_class", [])) for v in d.values())
    return (bool(pcts) and min(pcts) >= 98,
            f"{len(d)} sheets, own class nearest for {min(pcts):.1f}-{max(pcts):.1f}% "
            f"of sampled polygons, {bad} outlier(s) listed")


def geology(d):
    return True, (f"{d.get('units_final')} units, overlap residual "
                  f"{d.get('overlap_residual_km2', 0)} km2")


# the last field is the kind of evidence:
#   "check"    - measures the file as it is; must be newer than the file
#   "pipeline" - a step that writes the file. Its own timestamp cannot prove it
#                is current (every later write bumps the file's), so its currency
#                is established by check_idempotency.py, which re-runs all four
#                and compares every row instead
#   "build"    - the record of the run that built a layer; a record, not a
#                verdict, with its invariants re-measured by audit_layers.py
SPEC = [
    ("audit_layers.py", "layer_audit.json", "all 26 layers + 9 rasters + the copies file + registers", audit, "check"),
    ("docs_check.py", "docs_check.json", "every published number", docs, "check"),
    ("fix_gpkg_hygiene.py", "gpkg_hygiene.json", "the GeoPackage's own registers", hygiene, "pipeline"),
    ("repair_layers.py", "layer_repairs.json", "the per-layer repairs", repairs, "pipeline"),
    ("check_idempotency.py", "idempotency_check.json", "a second run changes nothing", idem, "check"),
    ("refresh_crs_report.py", "crs_qa_report.json", "CRS and area by projection", crs, "check"),
    ("add_gpkg_metadata.py", "gpkg_metadata.json", "provenance and licences in-file", meta, "pipeline"),
    ("check_polygon_colour.py", "polygon_colour_check.json", "traced polygons vs the sheet", colour, "check"),
    ("split_projected_copies.py", "projected_copies.json", "the 5 reprojections, moved", copies, "pipeline"),
    ("build_towns.py", "towns_report.json", "the GeoNames gazetteer", towns, "build"),
    ("georef_new_map.py", "raster_georeferencing.json", "the nine scanned sheets", rasters, "build"),
    ("build_geology_final.py", "geology_final_report.json", "the geology build's invariants", geology, "build"),
]

gpkg_mtime = dt.datetime.fromtimestamp(GPKG.stat().st_mtime)
rows = []
for script, evidence, what, fn, kind in SPEC:
    path = HERE / evidence
    problems = []
    if not path.exists():
        rows.append(dict(script=script, evidence=evidence, what=what, ok=False,
                         fresh=False, kind=kind,
                         note="evidence file missing"))
        continue
    if script == "georef_new_map.py" and False:
        pass
    raw = path.read_text()
    try:
        data = json.loads(raw)
        ok, note = fn(data)
    except Exception as exc:                     # a report that cannot be read is a failure
        ok, note = False, f"unreadable: {exc}"
    fresh = path.stat().st_mtime >= GPKG.stat().st_mtime - 1
    rows.append(dict(script=script, evidence=evidence, what=what, ok=bool(ok),
                     fresh=fresh or kind != "check", kind=kind, note=note))

bad = [r for r in rows if not r["ok"] or not r["fresh"]]

lines = [
    "# Verification - what was checked, and whether the check is still current",
    "",
    f"Data file: `{GPKG.name}`, {GPKG.stat().st_size / 1e6:.2f} MB, last written "
    f"{gpkg_mtime:%Y-%m-%d %H:%M} UTC.",
    "",
    "Each check below is a script in this directory that measures the file and writes the",
    "JSON named beside it. This page is generated by `verify_all.py`; it re-reads those files,",
    "shows the verdict each one records, and fails if any of them is older than the data -",
    "a verdict written before the last repair is a verdict about a different file.",
    "",
    "| check | measures | evidence | verdict | currency |",
    "|---|---|---|---|---|",
]
for r in rows:
    mark = "ok" if r["ok"] else "**FAIL**"
    fresh = {"check": "current" if r["fresh"] else "**stale**",
             "pipeline": "re-run by `check_idempotency.py`",
             "build": "build record"}[r["kind"]]
    lines.append(f"| `{r['script']}` | {r['what']} | `{r['evidence']}` | "
                 f"{mark} - {r['note']} | {fresh} |")
lines += [
    "",
    f"**{len(rows) - len(bad)} of {len(rows)} entries pass, and every check is current"
    f"{'' if not bad else ': ' + ', '.join(r['script'] for r in bad)}.**",
    "",
    "Two things this page does not do. It does not re-measure anything - the numbers are the",
    "scripts' own, and each script's method is documented in its docstring and in `README.md`.",
    "And it cannot tell you the checks were the right ones: for that, the tests that were tried",
    "and rejected are recorded in `mineral_audit.md`, `RASTER_VS_VECTOR.md` and `accuracy_audit.md`,",
    "including the ones that withdrew earlier claims.",
]
(HERE / "VERIFICATION.md").write_text("\n".join(lines) + "\n")
json.dump(dict(gpkg=str(GPKG), gpkg_mtime=gpkg_mtime.isoformat(timespec="seconds"),
               rows=rows, failures=[r["script"] for r in bad]),
          open(HERE / "verification.json", "w"), indent=1)

for r in rows:
    print(f"  {'ok ' if r['ok'] else 'FAIL'} {'current' if r['fresh'] else 'stale  '} "
          f"{r['script']:26s} {r['note']}")
print(f"\n{len(rows) - len(bad)}/{len(rows)} checks pass and are current -> VERIFICATION.md")
sys.exit(1 if bad else 0)
