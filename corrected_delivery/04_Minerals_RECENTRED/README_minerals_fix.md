# Mineral occurrence points — re-detected and re-centred (what was done)

**Layer:** `nigeria_mineral_symbols_CORRECTED.shp` — 1,272 points, EPSG:4326, 60 of the 67 legend classes.
Style: `nigeria_mineral_symbols_CORRECTED.qml` (categorized by `LEG_NO`).
Counts per class (old vs new): `mineral_legend_with_counts.csv`.
Old-point audit trail: `reconciliation_old1486_to_new.csv` + `old_points_not_carried_forward.shp`.

## What was wrong before
The old file (1,486 points) placed points at bounding-box centres of rough detections and took many
class labels from the nearest printed deposit-table number. The result: points offset from symbol
centres, two points on some single symbols, missing symbols, and some points sitting on a different
mineral's glyph altogether.

## How the corrected layer was built
1. **Standard symbol marks taken from the printed EXPLANATIONS legend** of the Mineral Resources Map
   2023 — the glyph printed next to each of the 67 legend names (extracted from the PDF's own
   high-resolution legend images). Where the map-face symbol differs in size/colour from the legend
   patch (rectangular legend patches are stretched), each template was re-fitted to the symbol as
   actually printed on the map (map exemplars / colour-adapted fits, per class).
2. **Exhaustive template scan** of the whole map face for every class (masked colour correlation,
   template centre = footprint centre of the standard mark; sub-pixel peak refinement). A point's
   coordinates are the **calculated centre of its symbol**, converted to lon/lat with the map's
   publisher (PDF `/VP`) georeferencing and stored also as `PX_X/PX_Y` in the delivered
   `Mineral_Resources_Map_BASEONLY_symbols_georeferenced.tif` pixel grid so you can verify centring.
3. **Complete symbols first** (`DET_SRC = SCAN_COMPLETE`, 946 points): a detection must beat every
   other class's template at the same spot; **one point per symbol** is enforced (minimum point
   spacing 5.1 px map-wide — the old double-point problem is gone).
4. **Partial matches only inside clusters** (`SCAN_PARTIAL_CLUSTER`, 30 points): lower-threshold
   matches accepted only within 15 px of at least two accepted symbols; the point is still placed
   at the full standard-mark centre.
5. **Rescue/rejection of old points** (213 `RESCUE_RECENTRED` + 50 visually verified
   `WHITELIST_*`): symbols the scan missed (mostly overlapped glyphs in clusters) were re-centred
   by local template search at the old point; old points with no supporting glyph were **rejected**
   (99 dropped + 33 old duplicates of a single symbol + 29 contested — all listed with reasons in
   `reconciliation_old1486_to_new.csv` / `old_points_not_carried_forward.shp`).

Reconciliation of the old 1,486 points: **1,352 matched** (most moved to the true symbol centre),
33 were duplicate second points on one symbol, 99 had no glyph of their class at the old location,
2 unresolved. The corrected layer also contains **77 newly found symbols** with no old point, plus
classes restored from zero (Copper 5, Nickel 4, Fluorite 3, Calcite 2, Rose Quartz 1, Brick Clay 1, Asbestos 1*).

## Fields
`LEG_NO` legend number 1–67 · `MINERAL` name · `COMM_GRP` commodity group ·
`DET_SRC` how the centre was obtained (see above; `OLD_CENTRE_KEPT`/`WHITELIST_OLDCENTRE` =
 glyph below template-detection size, centre kept from old data — treat as lower positional confidence) ·
`LABEL_SRC` how the class label was decided · `SCORE` template correlation 0–1 (blank for kept/manual centres) ·
`MARGIN` score margin over the best competing class · `PX_X/PX_Y` symbol-centre pixel in the BASEONLY GeoTIFF ·
`OLD_FID` link to the previous file (-1 = new find).

## Confidence guidance and known limits (please read)
- The map picture's symbol raster is ~0.67 km/pixel; even perfect centring is ±~0.3 km. Filter on
  `DET_SRC`/`SCORE` if you need only the firmest points (`SCAN_COMPLETE` with `SCORE ≥ 0.8`).
- **Glyph-identical groups:** at print resolution some legend symbols are the same mark — white
  circle group (Baryte / Gypsum / Phosphate / Phosphate Rock / Bitumen / Trona / Bismuth),
  yellow-circle group (Brine / Salt-potash), purple triangles (Garnet / Iron Ore). Within these
  groups the label follows the old deposit-table linkage where an old point exists
  (`LABEL_SRC = old-table-within-glyphgroup`); new finds get the best-matching template's label —
  treat group-member labels as interchangeable pending field/table verification.
- **Sub-resolution glyphs:** Beryl (51), Granite, Zircon and a few single-occurrence classes are
  printed marks of only a few pixels that no template can separate from text/roads; their points
  are old locations re-centred where possible and flagged `RESCUE_RECENTRED`/`OLD_CENTRE_KEPT`.
  Beryl scan "detections" proved to be road fragments on visual check and were not used.
- **Classes with NO point (7):** Bitumen, Evaporite, Marcasite, Psammite, Silver, Tar Sand, Trona.
  For each, the legend glyph was searched exhaustively; the top candidates were inspected and are
  other minerals' glyphs (e.g. the single old Marcasite points sit on Brine/Clay symbols; the old
  Fluorite point sits on a Feldspar diamond while the 3 true Fluorite "F" glyphs were found
  elsewhere; old "Calcite" points sit on Copper triangles — they are now Copper points, and the 2
  true Calcite discs were found at another locality). Bitumen/Trona occurrences, if printed, are
  absorbed in the white-circle group above. Details per old point in the reconciliation file.
- *One AMBIGUOUS point:* at 5.324°E, 6.773°N (old fid 479, old label "Lithium") there is a
  magenta oval glyph matched by no template; it is delivered as **Asbestos-serpentine** with
  `DET_SRC = MANUAL_VISUAL` and an explanatory `LABEL_SRC`. Please verify it against the GeoTIFF.

## Verify it yourself
Load `../02_Georeferenced_map_pictures/Mineral_Resources_Map_BASEONLY_symbols_georeferenced.tif`
under this layer in QGIS and zoom in: every point should sit at the middle of its printed symbol.
Worked examples are in `../QA_maps_and_reports/QA_minerals_*ZOOM_final.png`.
