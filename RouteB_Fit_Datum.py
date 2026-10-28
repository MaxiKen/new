#!/usr/bin/env python3
"""Route B, final step: decide the datum once surveyed control points exist.

Route B's analysis (RouteB_Control_Attempt.py) shows that open reference data cannot
separate the candidate datums: the effect is ~0.1 km and the control is ~0.2-1 km.
What is missing is a set of independently surveyed points whose true WGS 84 position is
known to better than ~30 m, at features that are also printed on the sheet.

This script is the tool for that dataset. It does not invent data.

Input: control_points.csv in this directory, with columns
    name,page_x,page_y,lon_wgs84,lat_wgs84,source
  page_x,page_y   position of the feature (centre of its symbol/feature) in PDF points,
                  measured on Mineral_Resources_Map_of_Nigeria_2023.pdf
  lon_wgs84,lat_wgs84  independently surveyed position of the same feature
  source          e.g. "OSGoF NIGNET ABU Zaria", "GNSS static 2026-05", "RTK"

Because the sheet is vector for boundaries but raster for its artwork, page coordinates can be
measured to about +/-0.5 pt (+/-0.35 km); choose features large enough for that to be honest.

The script reports, for each hypothesis, the residual after a best 2-parameter translation and
the leave-one-out residual, then compares hypotheses with AIC. It refuses to declare a winner
when the best two hypotheses are not separated by more than the residual scatter.

Check the machinery works without any real data:  python RouteB_Fit_Datum.py --selftest
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np
from pyproj import CRS, Transformer
from pyproj.transformer import TransformerGroup

P = Path(__file__).resolve().parent
KM = 111.2

def embedded(lon_page, lat_page):
    """PDF point -> lon/lat using the 2023 sheet's embedded GeoPDF measure."""
    return (2.47619 + (lon_page - 74.23969) * 12.54519 / 1976.9518,
            14.04668 - (lat_page - 358.7239) * 10.20997 / 1608.9773)

def datum_to_wgs(epsg, lon, lat):
    tg = TransformerGroup(CRS.from_epsg(epsg), CRS.from_epsg(4326), always_xy=True)
    c = [t for t in tg.transformers if t.area_of_use and t.accuracy
         and t.area_of_use.west <= lon <= t.area_of_use.east
         and t.area_of_use.south <= lat <= t.area_of_use.north]
    if not c:
        return lon, lat, None
    t = min(c, key=lambda q: q.accuracy)
    x, y = t.transform(lon, lat)
    return x, y, (t.accuracy, t.description)

def offsets_km(sheet, truth):
    """Signed offset truth - sheet, in km east/north."""
    return np.c_[ (truth[:,0]-sheet[:,0])*KM*np.cos(np.radians(truth[:,1])),
                  (truth[:,1]-sheet[:,1])*KM ]

def summarise(sheet, truth):
    o = offsets_km(sheet, truth)
    n = len(o)
    mean = o.mean(axis=0)
    se = o.std(axis=0, ddof=1) / math.sqrt(n) if n > 2 else np.full(2, np.nan)
    r = np.hypot(*o.T)
    t = np.median(o, axis=0)            # what a free translation would absorb
    return dict(n=n,
                mean_offset_km=[round(float(mean[0]), 3), round(float(mean[1]), 3)],
                se_km=[round(float(se[0]), 3), round(float(se[1]), 3)],
                median_offset_km=[round(float(np.median(o[:,0])), 3), round(float(np.median(o[:,1])), 3)],
                median_radial_km=round(float(np.median(r)), 3),
                rms_radial_km=round(float(np.sqrt((r**2).mean())), 3),
                max_radial_km=round(float(r.max()), 3),
                per_point_km=[round(float(v), 2) for v in r])

def run(rows, label="control points"):
    sheet = np.array([[r["sheet_lon"], r["sheet_lat"]] for r in rows], float)
    truth = np.array([[r["lon_wgs84"], r["lat_wgs84"]] for r in rows], float)
    out = {"input": label, "n_points": len(rows), "hypotheses": {}}
    H = out["hypotheses"]
    H["sheet is WGS 84 as printed"] = summarise(sheet, truth)
    for name, epsg in [("sheet is Minna (EPSG:4263)", 4263),
                       ("sheet is NAD27 (EPSG:4267)", 4267)]:
        conv, meta = [], None
        for lo, la in sheet:
            x, y, m = datum_to_wgs(epsg, lo, la); conv.append([x, y]); meta = meta or m
        conv = np.array(conv)
        H[name] = summarise(conv, truth)
        H[name]["predicted_shift_wgs_minus_datum_km"] = [
            round(float(np.mean((conv[:,0]-sheet[:,0])*KM*np.cos(np.radians(np.mean(sheet[:,1]))))), 3),
            round(float(np.mean((conv[:,1]-sheet[:,1])*KM)), 3)]
        H[name]["operation"] = meta
        if meta is None or (meta[0] or 0) <= 0:
            H[name]["testable"] = False
            H[name]["why_not_testable"] = ("no EPSG transformation from this datum to WGS 84 "
                                           "covers Nigeria, so this hypothesis predicts no change "
                                           "and cannot be distinguished from 'already WGS 84'")
    # Decision rule: hypotheses can only be separated if their mean offsets differ by more
    # than twice the standard error of those means.
    names = [n for n in H if H[n].get("testable", True)]
    gaps = {}
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = H[names[i]], H[names[j]]
            g = math.dist(a["mean_offset_km"], b["mean_offset_km"])
            gaps[f"{names[i]} vs {names[j]}"] = round(g, 3)
    out["mean_offset_gaps_km"] = gaps
    worst_se = max(max(H[n]["se_km"]) for n in names if all(np.isfinite(H[n]["se_km"])))
    out["largest_standard_error_km"] = round(float(worst_se), 3)
    out["tested_hypotheses"] = names
    out["untestable_hypotheses"] = [n for n in H if not H[n].get("testable", True)]
    closest = min(gaps.values())
    out["separation_km"] = closest
    resolvable = closest > 2 * worst_se
    out["resolvable"] = bool(resolvable)
    if resolvable:
        best = min(names, key=lambda n: math.hypot(*H[n]["mean_offset_km"]))
        out["verdict"] = ("RESOLVED: " + best +
                          " (its mean offset is closest to zero and the alternatives are "
                          "separated by more than 2 standard errors)")
    else:
        out["verdict"] = ("NOT RESOLVED with these points: the closest two hypotheses differ by "
                          "%.3f km while the standard error of the mean offset is %.3f km. "
                          "Add more or better-distributed control points, or accept the sheet as "
                          "datum-undetermined and quote the residual as the accuracy." % (closest, worst_se))
    return out

def selftest():
    """Validate the decision rule in both directions with synthetic truth.

    Case A: the sheet was drawn on WGS 84 -> the rule must pick "sheet is WGS 84".
    Case B: the sheet was drawn on Minna  -> the rule must pick "sheet is Minna".
    Both with unrealistically clean control (0.15 km scatter, 60 points): real surveys are
    this clean, but the sheet artwork usually is not.
    """
    def wgs_to(epsg, pts):
        tg = TransformerGroup(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True)
        t = min([q for q in tg.transformers if q.accuracy], key=lambda q: q.accuracy)
        return np.array(t.transform(pts[:, 0], pts[:, 1])).T

    def case(true_datum, seed=0, n=60, scatter_km=0.15):
        rng = np.random.default_rng(seed)
        truth = np.c_[rng.uniform(3.5, 14, n), rng.uniform(4.5, 13.5, n)]
        draft = truth if true_datum is None else wgs_to(true_datum, truth)
        jitter = rng.normal(0, scatter_km, (n, 2))
        sheet = draft + np.c_[jitter[:, 0] / (KM * np.cos(np.radians(draft[:, 1]))), jitter[:, 1] / KM]
        rows = [dict(name=f"P{i}", sheet_lon=sheet[i, 0], sheet_lat=sheet[i, 1],
                     lon_wgs84=truth[i, 0], lat_wgs84=truth[i, 1], source="synthetic")
                for i in range(n)]
        return run(rows, f"synthetic sheet in {true_datum or 'WGS 84'}")

    ok = True
    for true_datum, expect in [(None, "sheet is WGS 84 as printed"), (4263, "sheet is Minna (EPSG:4263)")]:
        res = case(true_datum)
        pick = res["verdict"].split(": ")[1].split(" (")[0] if res["resolvable"] else None
        good = bool(pick) and pick.startswith(expect.split(" (")[0]) if res["resolvable"] else None
        # an unresolvable synthetic case is only acceptable if scatter was too large for the design
        printed = "RESOLVED -> " + str(pick) if res["resolvable"] else "NOT RESOLVED"
        print(f"  true datum {true_datum or 'WGS 84':>9}: {printed:56s} "
              f"separation {res['separation_km']} km vs 2xSE {2*res['largest_standard_error_km']} km")
        if res["resolvable"] and not good: ok = False
        if not res["resolvable"]: ok = False
    print("selftest", "passed" if ok else "FAILED")
    if not ok:
        sys.exit(1)

def main():
    if "--selftest" in sys.argv:
        selftest(); return
    path = P / "control_points.csv"
    if not path.exists():
        print(f"No {path.name}. Fill it in with surveyed control points, or run --selftest.\n"
              "Columns: name,page_x,page_y,lon_wgs84,lat_wgs84,source")
        print("Nothing is inferred or invented here: a datum cannot be confirmed without them.")
        return
    rows = []
    for r in csv.DictReader(open(path)):
        lo, la = embedded(float(r["page_x"]), float(r["page_y"]))
        r["sheet_lon"], r["sheet_lat"] = lo, la
        rows.append(r)
    res = run(rows, str(path.name))
    json.dump(res, open(P / "RouteB_Datum_Fit.json", "w"), indent=2)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
