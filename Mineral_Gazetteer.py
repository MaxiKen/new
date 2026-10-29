#!/usr/bin/env python3
"""Read the 2023 sheet's own occurrence gazetteer and resolve every printed number.

The sheet indexes occurrences by gridded zone A-G: each symbol on the map carries a printed
index number that is only unique INSIDE its zone, and the right-hand panel lists, for each
(zone, index), a locality plus one or more mineral codes. That table is the sheet's own
statement of what is where, so it, not a guess, is what names each occurrence.

Outputs: Mineral_Gazetteer.json  (zone -> index -> {locality, codes, minerals})
         Mineral_Codes.json      (legend code -> mineral name)
"""
import json, re
from pathlib import Path
import pymupdf

P = Path(__file__).resolve().parent
PDF = P / "Mineral_Resources_Map_of_Nigeria_2023.pdf"
page = pymupdf.open(PDF)[0]

# ---------------------------------------------------------------- legend: code -> mineral
LEGEND_ROWS = json.load(open(P / "Legend_Rows.json")) if (P / "Legend_Rows.json").exists() else None

def read_legend():
    ws = [w for w in page.get_text("words") if 2095 < w[0] < 2290 and 325 < w[1] < 1400]
    rows = {}
    for w in ws:
        rows.setdefault(round(w[1] / 3), []).append(w)
    merged = []
    for k in sorted(rows):
        if merged and k - merged[-1][0] <= 2:
            merged[-1][1].extend(rows[k])
        else:
            merged.append([k, list(rows[k])])
    out = []
    for k, items in merged:
        items.sort(key=lambda w: w[0])
        txt = " ".join(w[4] for w in items)
        if re.match(r"^\d", txt) or not txt.strip():
            continue
        out.append({"y0": min(w[1] for w in items), "text": txt})
    # repair the sheet's own kerning: a capital followed by a space inside a word
    def fix(t):
        t = re.sub(r"\bS (?=[a-z])", "S", t)
        t = re.sub(r"\bR (?=[a-z])", "R", t)
        t = re.sub(r"\bM (?=[a-z])", "M", t)
        t = re.sub(r"\bK (?=[a-z])", "K", t)
        t = re.sub(r"\bT (?=[a-z])", "T", t)
        t = re.sub(r"\bZ (?=[a-z])", "Z", t)
        t = re.sub(r"\bN (?=[a-z])", "N", t)
        t = re.sub(r"\bA (?=[a-z])", "A", t)
        t = re.sub(r"\bB (?=[a-z])", "B", t)
        t = re.sub(r"\bP (?=[a-z])", "P", t)
        t = re.sub(r"\bG (?=[a-z])", "G", t)
        t = re.sub(r"\bF (?=[a-z])", "F", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t
    ent = []
    for e in out:
        if e["text"].startswith("M oganite") or e["text"].startswith("Moganite"):
            ent[-1]["text"] += " " + e["text"]
        else:
            ent.append({"y0": e["y0"], "text": fix(e["text"])})
    return ent

legend = read_legend()
# code in brackets at the end of a legend name, e.g. "Talc (tc)"; otherwise the sheet's
# two-letter label printed inside the swatch, which we record separately.
codes = {}
for e in legend:
    m = re.search(r"\(([a-z]{1,3})\)\s*$", e["text"].lower())
    name = re.sub(r"\s*\([a-z]{1,3}\)\s*$", "", e["text"], flags=re.I).strip()
    codes[name] = {"name": name, "code": m.group(1) if m else None}
print("legend minerals:", len(codes))

# ---------------------------------------------------------------- gazetteer columns
ZONE = {"A": 0, "B": 1, "D": 2, "E": 3, "F": 4, "G": 5}     # C has no numbered list
COL_X = [(2296, 2404), (2444, 2530), (2634, 2735), (2787, 2883), (2963, 3067),
         (3143, 3243), (3298, 3409), (3455, 3556)]
def col_of(x):
    for i, (a, b) in enumerate(COL_X):
        if a - 6 <= x <= b:
            return i
    return None

ws = [w for w in page.get_text("words") if w[0] > 2250 and 330 < w[1] < 1900]
rows = {}
for w in ws:
    rows.setdefault((col_of(w[0]), round(w[1] / 4)), []).append(w)
entries = []
for (c, r), items in rows.items():
    if c is None:
        continue
    items.sort(key=lambda w: w[0])
    entries.append({"col": c, "row": r, "text": " ".join(w[4] for w in items),
                    "x": items[0][0], "y": min(w[1] for w in items)})

# a row can hold up to three flow columns; each starts with "n." or "n "
def split_segments(items_line):
    """split one text line into (number, rest) segments by looking for number starts"""
    return items_line

by_col = {}
for e in entries:
    by_col.setdefault(e["col"], []).append(e)
for c in by_col:
    by_col[c].sort(key=lambda e: (e["row"], e["x"]))

def parse_entry(txt):
    m = re.match(r"^(\d{1,3})\s*[.,]?\s*(.*)$", txt)
    if not m:
        return None
    return int(m.group(1)), m.group(2).strip()

parsed = {}
for c, lst in by_col.items():
    for e in lst:
        g = parse_entry(e["text"])
        if g:
            parsed.setdefault(c, []).append({"num": g[0], "rest": g[1], "y": e["y"], "x": e["x"]})

print("zones parsed:", {c: len(v) for c, v in parsed.items()})
for c, lst in parsed.items():
    nums = [p["num"] for p in lst]
    print(f"  col {c}: {len(nums)} entries, numbers {min(nums)}-{max(nums)}")

json.dump({"zones": parsed, "legend": codes}, open(P / "Mineral_Gazetteer_raw.json", "w"), indent=1)
