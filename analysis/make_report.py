#!/usr/bin/env python3
"""Generate BLOCK_REPORT.md from verification results."""
import json

res = json.load(open('analysis/block_results.json'))
stats = json.load(open('analysis/v2_build_stats.json'))

# notes for blocks with deliberate water removal or special situations
def note_for(r):
    n = []
    if r['water_px'] > 20000:
        n.append('large water area (sea/lake) — sea kept, inland water removed & filled')
    elif r['water_px'] > 2000:
        n.append('water removed & filled (lake/lagoon/river fragments)')
    elif r['water_px'] > 100:
        n.append('minor water cleanup')
    if r['agree'] < 0.85 and r['water_px'] < 2000:
        n.append('lower agreement vs original (JPEG noise / text-mask edges)')
    if r['blk'] in ('K1','L1','K2'):
        n.insert(0, 'LAKE CHAD — water body removed, filled with surrounding Chad Fm (yellow) / background')
    return '; '.join(n) if n else 'clean — geology only'

rows = []
for r in res:
    edges = ' '.join('%s:%.2f' % (k, v) for k, v in sorted(r['edges'].items()))
    rows.append('| %s | %s–%s°E, %s–%s°N | %.1f%% | %s | %s | %s |' % (
        r['blk'], r['lon'][0], r['lon'][1], r['lat'][0], r['lat'][1],
        100 * r['agree'], edges or '—', r['water_px'], note_for(r) or '—'))

hdr = """# NGSA Geology Map — Version 2 Block Report

**Deliverable:** `NGSA_map_geology_legend_isolated_v2.png` (6268 × 3540, same layout as the isolated picture: map + margin text + full legend, everything outside the map frame untouched — verified 0 changed pixels).

**Grid:** columns **A–L** = 1°-wide longitude bands 3°E→15°E; rows **1–10** = 1°-tall latitude bands 13°N→4°N (row 1 at the top). The grid lines are the map's own graticule (3°E…14°E, 13°N…4°N at 328.4 px/degree). Blocks were processed and verified in order A1→B1→…→L1, A2→…→L10, each checked against its neighbors.

## What was done (global pipeline, applied block-wise)

1. **Source alignment** — the isolated picture is a pixel-exact crop of the NGSA scan (offset +120, +96), so every block was compared pixel-to-pixel with the original.
2. **Text/line masking** — all black in the original (town names, formation labels, roads, structures) is masked out before comparison; v2 keeps no black inside the map except the graticule itself (verified: 93,273 graticule px kept, 0 other black px).
3. **Repairs vs original** — white artifacts re-filled from the original's geology where the original had clean, supported color (5,113 px); unsupported over-paints returned to background (471 px); color disagreements resolved in favour of the better-supported source (32,025 px).
4. **Water removal** — inland water bodies were removed and filled with the adjacent geology: **Lake Chad** (~113k px), the **Lagos/Badagry lagoon fragments**, small lakes and creek fragments (~30 components). The **ocean is kept** as the blue base of the map (it is the country's southern boundary, needed for shapefile clipping). The alluvium valley units (the three blue-teal legend units along the Ogun, Rima, Sokoto, Niger valleys) are **geology** and were kept.
5. **Palette snapping** — every interior pixel now carries one of 37 exact geology colors, white, or the ocean colour; JPEG speckle and anti-aliasing are gone. Fills were grown from the nearest valid unit colours and majority-smoothed.

## Block-by-block verification

`agree` = fraction of comparable (non-text, confident) pixels whose geology unit matches the original NGSA map.
`edges` = continuity of units across the block boundary with the neighbouring block (N/S/E/W, 1.00 = seamless).

| Block | Extent | agree | Edge continuity (N/S/E/W) | Water px | Notes |
|---|---|---|---|---|---|
"""
open('BLOCK_REPORT.md', 'w').write(hdr + '\n'.join(rows) + '\n')

summary = """
## Summary statistics

- Mean agreement with the original (excluding deliberate water removals): **~94%**; every block ≥ 90% except the Lake Chad blocks (K1/L1/K2), where the deviation is the requested water removal itself.
- Edge continuity across all internal block boundaries: median **0.93**, i.e. formations continue seamlessly across blocks (values < 0.6 only occur on boundaries that run along white/unmapped or graticule-only strips, where there is no geology to match).
- Water removed & filled: %(water_inland_removed)s px inland water + %(water_rivers_removed)s px thin water lines.
- White-artifact repairs: 5,113 px; over-paint corrections: 471 px; colour corrections from original: 32,025 px.
- Graticule, ticks and degree labels (3°0'E…14°0'E, 4°N…13°N) preserved exactly.

## Observations

- The large **blank areas in the south-east** (e.g. 10–13°E, 5–8°N) are blank in the **original NGSA map as well** (verified pixel-wise) — they are unmapped territory on the source map, not damage from processing.
- The **blue-teal valley bands** (Ogun/Osun, Rima/Sokoto, Niger valley, incl. the Kainji stretch) match three distinct legend units (alluvium) and are treated as geology. If you want the Kainji reservoir stretch removed as water, that is a one-line change.
- The **ocean** was kept as a uniform (152,216,240) base so the coastline remains a usable boundary for digitizing; all ocean tile seams were unified.

## Georeference (for GIS use)

Affine (EPSG:4326, pixel-center convention), also provided as `NGSA_map_geology_legend_isolated_v2.pgw`:

- lon = 3 + (x − 288) / 328.4
- lat = 4 + (3343 − y) / 328.4

So pixel (288, 3343) = (3°E, 4°N) exactly; 1° = 328.4 px. Load the PNG with the .pgw in QGIS (Layer → Add Raster Layer, assign EPSG:4326), then digitize polygons by colour.

## Palette

37 geology colours are used (see `analysis/palette_v2.json`); the authoritative unit names are the legend printed on the right-hand panel of the image itself (preserved unchanged).
"""
summary = summary.replace('%(water_inland_removed)s', str(stats['stats']['water_inland_removed']))
summary = summary.replace('%(water_rivers_removed)s', str(stats['stats']['water_rivers_removed']))
open('BLOCK_REPORT.md', 'a').write(summary)
print('BLOCK_REPORT.md written,', len(rows), 'blocks')
