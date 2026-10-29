#!/usr/bin/env python3
"""Audit every occurrence against the printed symbol it sits on, one point at a time.

For each point we render a 30 pt window around it from the 2023 PDF, take the local map
background colour, find the printed ink blob the point belongs to (or the nearest one within
6 pt) and measure how far the point is from that blob's bounding-box centre.

Writes Centre_Audit.json + a contact sheet of the worst offenders so the number can be checked
by eye as well as by arithmetic.
"""
import json
import numpy as np, pandas as pd, pymupdf
from PIL import Image, ImageDraw
from scipy import ndimage

Z = 6.0              # render zoom for the audit windows
HALF_PT = 15.0       # window half-size in page points
MX = pymupdf.Rect(74.23969, 358.7239, 2051.8313, 1968.6611)
page = pymupdf.open("Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]

pts = pd.read_csv("Minerals_Occurrences_4326.csv")
px = MX.x0 + (pts.lon.values - 2.47619) / 12.54519 * 1976.9518
py = MX.y0 + (14.04668 - pts.lat.values) / 10.20997 * 1608.9773

R = int(HALF_PT * Z)
rows, worst = [], []
for i, (x, y) in enumerate(zip(px, py)):
    clip = pymupdf.Rect(x - HALF_PT, y - HALF_PT, x + HALF_PT, y + HALF_PT)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=clip, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(np.int16)
    if a.shape[0] < 20 or a.shape[1] < 20:
        continue
    # local background = the most common colour (map fill)
    q = (a // 12).astype(np.int32)
    flat = q.reshape(-1, 3)
    codes = flat[:, 0] * 10000 + flat[:, 1] * 100 + flat[:, 2]
    bg = np.bincount(codes - codes.min()).argmax() + codes.min()
    bgc = np.array([bg // 10000, (bg // 100) % 100, bg % 100]) * 12 + 6
    mask = (np.abs(a - bgc).sum(2) > 70)
    lab, n = ndimage.label(mask)
    if n == 0:
        rows.append((i, np.nan, 0, 0, "no ink"))
        continue
    cy, cx = a.shape[0] // 2, a.shape[1] // 2
    here = lab[cy, cx]
    if here == 0:                                  # point is on background: take the nearest blob
        sl = ndimage.find_objects(lab)
        dist = np.full(n + 1, 1e9)
        for k, s in enumerate(sl, 1):
            if s is None or (s[0].stop - s[0].start) < 3 or (s[1].stop - s[1].start) < 3:
                continue
            by = (s[0].start + s[0].stop - 1) / 2
            bx = (s[1].start + s[1].stop - 1) / 2
            dist[k] = np.hypot(bx - cx, by - cy) / Z
        k = dist.argmin()
        if dist[k] > 6:
            rows.append((i, np.nan, 0, 0, "no symbol within 6 pt"))
            continue
    else:
        k = here
    sl = ndimage.find_objects(lab, max_label=n)[k - 1]
    by = (sl[0].start + sl[0].stop - 1) / 2
    bx = (sl[1].start + sl[1].stop - 1) / 2
    w = (sl[1].stop - sl[1].start) / Z
    h = (sl[0].stop - sl[0].start) / Z
    off = np.hypot(bx - cx, by - cy) / Z
    kind = "glyph" if min(w, h) >= 3.0 else "small mark"
    rows.append((i, off, w, h, kind))
    if off > 2.0 and len(worst) < 60:
        worst.append((i, off, clip))

aud = pd.DataFrame(rows, columns=["row", "offset_pt", "w_pt", "h_pt", "kind"])
ok = aud.dropna(subset=["offset_pt"])
res = {
    "points_checked": int(len(aud)),
    "matched_to_printed_ink": int(len(ok)),
    "median_offset_pt": round(float(ok.offset_pt.median()), 3),
    "median_offset_km": round(float(ok.offset_pt.median() * 0.68), 3),
    "p90_offset_pt": round(float(ok.offset_pt.quantile(.9)), 2),
    "within_0_5pt_pct": round(float((ok.offset_pt <= .5).mean() * 100), 1),
    "within_1pt_pct": round(float((ok.offset_pt <= 1).mean() * 100), 1),
    "within_2pt_pct": round(float((ok.offset_pt <= 2).mean() * 100), 1),
    "matched_to_a_small_mark_pct": round(float((ok.kind == "small mark").mean() * 100), 1),
    "unmatched": int(len(aud) - len(ok)),
    "worst": [{"row": int(i), "offset_pt": round(float(o), 2)} for i, o, _ in worst[:20]],
}
print(json.dumps(res, indent=1))
json.dump(res, open("Centre_Audit.json", "w"), indent=1)

# contact sheet of the worst offenders, each with the digitised coordinate marked
if worst:
    crop = int(R * 2)
    cols = 6
    rows_n = (len(worst) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * crop, rows_n * crop), "white")
    for n, (i, off, clip) in enumerate(worst):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(Z, Z), clip=clip, alpha=False)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        d = ImageDraw.Draw(im)
        c = im.width / 2
        d.line([(c - 26, c), (c - 5, c)], fill=(255, 0, 220), width=2)
        d.line([(c + 5, c), (c + 26, c)], fill=(255, 0, 220), width=2)
        d.line([(c, c - 26), (c, c - 5)], fill=(255, 0, 220), width=2)
        d.line([(c, c + 5), (c, c + 26)], fill=(255, 0, 220), width=2)
        d.ellipse([c - 3, c - 3, c + 3, c + 3], fill=(255, 0, 220))
        d.text((4, 4), f"#{i} {off:.1f}pt", fill=(180, 0, 90))
        sheet.paste(im, ((n % cols) * crop, (n // cols) * crop))
    sheet.save("Centre_Audit_worst.png")
    print(f"  contact sheet: Centre_Audit_worst.png ({len(worst)} crops)")
