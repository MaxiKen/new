# In plain language: what you asked for this time

Four things: more minerals, better names, one point per symbol, and layers that are really
projected. Here is each one and how you can check it.

---

## 1. "There are actually much more numbers of minerals"

You were right, and the reason is on the sheet itself.

The 2023 sheet does not just draw symbols — it **numbers every occurrence** and prints an
**occurrence table** down the right-hand side. That table gives, for each number, a locality and
the mineral codes found there, and many localities list **several minerals at once**:

```
87  Rjishi Hills   Sn. W. Nb. Ta      (four minerals at one place)
11  MARNONA        Gy
30  Kwali          Ka
```

So the sheet's own legend carries **67 mineral symbols**, and I now read that table with
`Parse_Gazetteer.py`, giving the locality and codes for each numbered entry. The output is
`Gazetteer_Localities.json`.

The number of **distinct commodity names** in the file went from 40 to **47**, and each row now
also records what the other reading thought it was, so a multi-mineral locality is visible
rather than flattened to one guess.

## 2. "If labelling requires prediction, put what it is most likely to be"

Done, with the prediction labelled as a prediction rather than hidden.

Each symbol now has **two independent readings**:

* the **commodity code printed inside the symbol** (the original reading — 81% correct in
  leave-one-out testing), and
* the **legend symbol** that best matches the printed glyph out of the sheet's 67, with a score
  and the runner-up.

| what happened | rows |
|---|---|
| both readings give the same name | 194 |
| readings agree on a family (Clay vs Brick Clay; Beryl vs Emerald) | 199 |
| readings disagree | 892 |

Where they agree, the row says `confidence = high` or `medium`. Where they disagree, the row
keeps **both names** — `mineral` and `alternative_name` — and is marked `low`. I did not
overwrite a good reading with a guess, and I did not hide a conflict behind one confident-looking
column. `legend_symbol`, `second_symbol` and `margin` show exactly what the matcher saw, so your
verification is a column sort, not a re-do.

## 3. "Don't put two points on one mineral"

I measured this properly instead of assuming: **232 of the old 1,323 points sat on a symbol that
already had a point**. The sheet draws a cluster as several separate symbols, and the old
extraction sometimes recorded one printed symbol twice.

The rule now is geometric: a symbol is a connected patch of the sheet's symbol colours, so two
points on the *same* patch are the same symbol and become one point at that patch's centre. Two
points on *different* patches stay separate however close together they are — a cluster of
adjacent symbols is a real cluster and must not be collapsed.

| | before | now |
|---|---|---|
| points | 1,323 | **1,091** |
| points sharing a symbol with another point | 232 | **0** |
| median distance to the symbol's printed centre | 0.35 km | **0.09 km** |
| within 0.71 km of the centre | 74% | **96%** |

141 of the new points are merges of two or more old ones, and each says so in
`n_source_points` — nothing was discarded silently.

`Map_4_Symbol_Centring.png` shows six occurrences at 14× with their measured offsets printed
under them. Four are exactly 0.00; the others are under half a millimetre on the paper.

## 4. "I don't want the layers to only be displayed in EPSG 4326"

Correct — and worth being blunt about: a layer whose coordinates are still degrees is **not**
projected, whatever its metadata says. So there is now a second package where the geometry is
genuinely reprojected into metres:

| layer | CRS | coordinates |
|---|---|---|
| geology units, national outline | ESRI:102022 Africa Albers **Equal Area** | −2,386,313 … −395,217 m |
| occurrences, faults, roads, rivers, state lines | EPSG:32632 **UTM zone 32N** | −196,828 … 1,103,938 m |

Areas go to the equal-area frame so unit sizes are comparable everywhere; points and lines go to
UTM so distances are in metres. Measured, not claimed:

* UTM 32N distance error over short baselines: **0.035% median** (worst 0.45% — about 1 m in 220 m).
* Nigeria's area in the equal-area frame: **907,498 km²**.

The 4326 package stays as the reference frame for interchange; the projected one is for
measuring.

## What is still not known

* **The sheet restarts its index numbers in each zone.** A number alone is ambiguous; only the
  printed locality names are unique. So the occurrence table is keyed by locality and matched to
  the map by name.
* **Commodity names are not settled.** 82% of rows are marked low. The evidence is in the row;
  your check should start with `confidence`.
* **Folds are still not extractable** — that structural key does not exist on this sheet. No fold
  layer was invented.
* **Symbol centres** are 0.09 km median from the glyph centre; one artwork pixel is 0.68 km, so
  the drawing is the floor, not the method.

## The files

| file | what it is |
|---|---|
| `Nigeria_Geology_Minerals_4326.gpkg` | **the reference package**, 13 layers, EPSG:4326 |
| `Nigeria_Geology_Minerals_projected.gpkg` | **the measuring package**, real projected geometry |
| `Minerals_Occurrences_4326.csv` / `.geojson` | 1,091 occurrences with names, alternatives and confidence |
| `Gazetteer_Localities.json` | the sheet's own occurrence table, parsed |
| `Map_1_Geology.png` … `Map_4_Symbol_Centring.png` | the four plates |
| `GeoPackage_Validation.json`, `Verify_Centres.json`, `Occurrence_Report.json`, `Projection_Report.json` | the numbers behind every claim above |
