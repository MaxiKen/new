#!/usr/bin/env python3
"""Read the 2011 sheet's own legend: swatch colour, unit code, unit name and age.

Each legend row is: name (left column) | age text (middle) | swatch with the code printed in it.
The swatch rectangle comes from the vector drawing, its colour from the *rendered* page (what the
eye sees), the code from the text inside the swatch and the name from the text on the same row.

A few codes are printed twice with two tints, and four tints stand for two codes; both facts are
kept, because they decide whether a pixel can be named from its colour alone.

Writes Legend_Colours.json.
"""
import json
import numpy as np, pymupdf

doc = pymupdf.open("Geological_Map_of_Nigeria.pdf")
page = doc[0]
Z = 4.0
pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), alpha=False)
im = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
words = [(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")]

rows = []
for d in page.get_drawings():
    f = d.get("fill")
    if not f:
        continue
    r = d["rect"]
    if not (18 <= r.width <= 30 and 10 <= r.height <= 17) or r.x0 < 2200:
        continue                                     # legend swatches only
    ymid = (r.y0 + r.y1) / 2
    code = None
    for w in words:
        if w[0] - 2 <= (w[0] + w[2]) / 2 <= r.x1 + 2 and r.y0 - 2 <= (w[1] + w[3]) / 2 <= r.y1 + 2 \
                and w[0] > r.x0 - 2:
            code = w[4].strip().rstrip(",.")
            break
    if not code:
        continue
    # the unit name is printed to the right of the swatch, usually "lithology --- Formation"
    label = " ".join(w[4] for w in sorted(
        [w for w in words if abs((w[1] + w[3]) / 2 - ymid) < 5 and w[0] > r.x1 + 2],
        key=lambda w: w[0]))
    lith, sep, formation = label.partition("---")
    name = (formation or lith).strip(" -")
    lith = lith.strip(" -")
    age = " ".join(w[4] for w in sorted(
        [w for w in words if abs((w[1] + w[3]) / 2 - ymid) < 6 and 2548 <= w[0] < 2676],
        key=lambda w: w[0]))
    x0, x1 = int((r.x0 + 3) * Z), int((r.x1 - 1) * Z)
    y0, y1 = int((r.y0 + 3) * Z), int((r.y1 - 2) * Z)
    tile = im[y0:y1, x0:x1].reshape(-1, 3)
    q = (tile // 4 * 4).astype(np.int32)
    cc = q[:, 0] * 65536 + q[:, 1] * 256 + q[:, 2]
    u, c = np.unique(cc, return_counts=True)
    k = u[c.argmax()]
    rows.append({"code": code, "name": name, "lithology": lith, "age": age,
                 "rgb": [int((k // 65536) % 256), int((k // 256) % 256), int(k % 256)],
                 "flat_fraction": round(float(c.max() / len(tile)), 3),
                 "y": round(r.y0, 1)})

# an age written once covers the rows under it; carry it down the column
carry = ""
for r in sorted(rows, key=lambda r: r["y"]):
    if r["age"]:
        carry = r["age"]
    r["age_group"] = carry
rows.sort(key=lambda r: r["y"])

by_code, by_rgb = {}, {}
for r in rows:
    by_code.setdefault(r["code"], {"colours": set(), "names": set(), "ages": set()})
    by_code[r["code"]]["colours"].add(tuple(r["rgb"]))
    by_code[r["code"]]["names"].add(r["name"])
    by_code[r["code"]]["ages"].add(r["age_group"])
    by_rgb.setdefault(tuple(r["rgb"]), set()).add(r["code"])

out = {
    "swatches_read": len(rows),
    "codes": len(by_code),
    "colours": len(by_rgb),
    "units": {c: {"colours": sorted(map(list, v["colours"])),
                  "name": " / ".join(sorted(n for n in v["names"] if n)),
                  "lithology": " / ".join(sorted({r["lithology"] for r in rows
                                                  if r["code"] == c and r["lithology"]})),
                  "age": " / ".join(sorted(a for a in v["ages"] if a))}
              for c, v in by_code.items()},
    "colour_to_codes": {str(list(k)): sorted(v) for k, v in by_rgb.items()},
    "codes_with_two_tints": sorted([c for c, v in by_code.items() if len(v["colours"]) > 1]),
    "colours_shared_by_codes": {str(list(k)): sorted(v) for k, v in by_rgb.items() if len(v) > 1},
    "rows": rows,
}
json.dump(out, open("Legend_Colours.json", "w"), indent=1)
print(f"{out['swatches_read']} swatches -> {out['codes']} codes over {out['colours']} tints")
print("codes carrying two tints:", out["codes_with_two_tints"])
print("tints standing for two codes:")
for k, v in out["colours_shared_by_codes"].items():
    print("   ", k, v)
missing = [c for c, v in out["units"].items() if not v["name"]]
print("codes with no name read:", missing)
for c in ["b", "M", "Ts", "Wss", "Ncsh", "GIls", "bG-h"]:
    if c in out["units"]:
        print(f"   {c:>6}: {out['units'][c]['name'][:60]!r}  [{out['units'][c]['age'][:30]}]")
