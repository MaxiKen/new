#!/usr/bin/env python3
"""
check_base.py — One-shot compliance check against the declared base.

Runs the measurement engine in-process, compares every chapter with its
length-tier floor from `analysis/base_standard.json`, and prints:

    * a per-chapter verdict (met / below base, and on which of the three metrics)
    * the extra words / paragraphs / headings needed to reach the floor
    * corpus-wide totals and the top priorities

Exit code 0 if every chapter meets the base, 1 otherwise — so it can be used
as a gate in a build or a pre-commit style check.

Usage:
    python3 analysis/check_base.py                    # summary + failures
    python3 analysis/check_base.py --all              # include passing chapters
    python3 analysis/check_base.py --chapter 26 37    # focus on chapters
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verse_metrics  # noqa: E402  (local module)

BASE_JSON = os.path.join(HERE, "base_standard.json")

TIER_ORDER = ["T1", "T2", "T3", "T4", "T5"]
METRIC_KEYS = [
    ("words_per_verse", "avg_words_per_verse_content", "W/v"),
    ("paragraphs_per_verse", "avg_paragraphs_per_verse_content", "P/v"),
    ("bold_headings_per_verse", "avg_bold_headings_per_verse_content", "H/v"),
]


def tier_for(spec: dict, verses: int) -> dict:
    for t in spec["tiers"]:
        lo, hi = t["verse_range"][0], t["verse_range"][1] or 10 ** 9
        if lo <= verses <= hi:
            return t
    return spec["tiers"][-1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="expanded")
    ap.add_argument("--all", action="store_true", help="list every chapter, not only failures")
    ap.add_argument("--chapter", nargs="*", type=int, help="only these chapter numbers")
    args = ap.parse_args()

    with open(BASE_JSON, encoding="utf-8") as fh:
        spec = json.load(fh)

    chapters, _ = verse_metrics.analyse(args.dir)

    failures, checked = [], 0
    rows = []
    for c in sorted(chapters, key=lambda c: c.chapter):
        if args.chapter and c.chapter not in args.chapter:
            continue
        checked += 1
        t = tier_for(spec, c.canonical_verses)
        fails, detail = [], []
        for key, attr, short in METRIC_KEYS:
            floor = t[key]["base_floor"]
            actual = getattr(c, attr)
            ok = actual + 1e-9 >= floor
            if not ok:
                fails.append(short)
            detail.append(f"{short} {actual:,.2f}/{floor:,.2f} {'ok' if ok else 'LOW'}")
        n = max(1, c.verses_with_content)
        need_w = int(round(max(0.0, t["words_per_verse"]["base_floor"] - c.avg_words_per_verse_content) * n))
        need_p = int(round(max(0.0, t["paragraphs_per_verse"]["base_floor"] - c.avg_paragraphs_per_verse_content) * n))
        need_h = int(round(max(0.0, t["bold_headings_per_verse"]["base_floor"] - c.avg_bold_headings_per_verse_content) * n))
        rows.append((c, t["tier"], fails, detail, need_w, need_p, need_h, c.empty_verse_stubs))
        if fails:
            failures.append(rows[-1])

    print(f"BASE CHECK — {checked} chapters in `{args.dir}/` against {os.path.relpath(BASE_JSON)}")
    print(f"declared {spec['declared']} | unit: {spec['unit']} | tiers: "
          + ", ".join(f"{t['tier']} {t['verse_range'][0]}–{t['verse_range'][1] or '+'}v" for t in spec["tiers"]))
    print()

    show = rows if args.all else failures
    if show:
        print(f"{'ch':>4} {'sūrah':<18} {'tier':>4}  {'words/verse':>13} {'paras/verse':>13} "
              f"{'heads/verse':>13}  {'needs words':>11} {'needs paras':>11} {'needs heads':>11}")
        for c, tier, fails, detail, nw, np_, nh, stubs in show:
            flag = "✗✗✗" if len(fails) == 3 else ("✗✗ " if len(fails) == 2 else ("✗  " if fails else "✓  "))
            print(f"{c.chapter:>4} {c.name[:18]:<18} {tier:>4}  {detail[0]:>13} {detail[1]:>13} "
                  f"{detail[2]:>13}  {nw:>11,} {np_:>11,} {nh:>11,}  {flag}"
                  + (f"  [{stubs} empty stubs]" if stubs else ""))
        print()

    total = len(rows)
    n_fail = len(failures)
    print(f"meets base : {total - n_fail:>4} / {total}")
    print(f"below base : {n_fail:>4} / {total}"
          + ("  (3 metrics: %d, 2 metrics: %d, 1 metric: %d)"
             % (sum(1 for r in failures if len(r[2]) == 3),
                sum(1 for r in failures if len(r[2]) == 2),
                sum(1 for r in failures if len(r[2]) == 1)) if failures else ""))
    print(f"to reach every floor: {sum(r[4] for r in failures):,} words, "
          f"{sum(r[5] for r in failures):,} paragraphs, {sum(r[6] for r in failures):,} mini-headings")
    stubs = sum(r[7] for r in rows)
    if stubs:
        print(f"empty verse stubs (no commentary at all): {stubs}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
