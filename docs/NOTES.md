# NGSA geological-map interpretation · revision 7

Prepared 10 October 2026 from the supplied **pic NGSA geological-map-of-nigeria-.jpg** (6600 × 3675 pixels). This is a reproducible automated draft, not an official NGSA vector dataset or an exhaustively hand-traced geological map. The source image is unchanged.

## What “black removed” means

**No black or near-black geological fills are exported. No black outlines are used in the derived viewer or bundled styles.** Dark labels, symbols, and cartographic strokes are excluded as geological seeds; obscured cells are filled from nearby reliable geological colors. Black is not an “unknown unit.” The word *black* in a legitimate lithology such as “black shale” describes the rock, not its map fill and is retained.

The original photo deliberately retains its black annotations for comparison. The viewer opens on **Clean map**; **Original photo** and **Compare** display a warning. Source pixels are never confused with cleaned polygons.

All tested black source pixels strictly inside the mapped footprint are covered by the derived geometry. The exact count and checks are in `quality.json` and `validation.json`. No black-colored geological class or internal empty space is used as a placeholder for text.

## Coverage and water

Output polygons form an edge-matched coverage: no internal gaps or overlapping interiors. “No gaps” applies to the mapped footprint, not the rectangular page, open ocean, or an authoritative country boundary. Smoothing can move its exterior slightly; the raster check excludes a five-source-pixel band at that exterior and explicitly accounts for image-frame edges. The complete vector union separately has no unassigned internal rings.

Water is an explicit review class, not an empty hole and not invented geology. Thin rivers printed over geology are commonly treated as cartographic linework. The water mask and outer footprint are color-derived approximations and require review along coasts, lagoons and borders.

## Single bodies and shared, non-boxy contacts

Each output record is a singlepart polygon. Different bodies are **not dissolved country-wide by color**. Each contact is constructed once and inherited identically by its neighboring polygons. The `shared_contacts` layer contains one copy of each edge, with its geographic left/right polygon IDs (0 = outside).

The native 4084 × 3336 map crop is classified by sampled legend colors in CIELAB space. Nearly identical palette choices are grouped locally to prevent JPEG speckle becoming checkerboard boundaries, with alternatives retained in attributes. Thin neutral linework and dark annotations are masked. Broad genuine gray units are permitted; pale lavender geology is not treated as gray annotation. A 12-source-pixel speckle sieve generalizes very small bodies.

**Continuity correction:** the previous build explicitly inserted thin-dark-stroke barriers inside connected color regions. That was a direct cause of artificial fragmentation. Revision 6 removes that subdivision rule entirely. A connected palette-family component gets one body seed; black crossings cannot cut it. Disconnected bodies remain separate—there is no country-wide color dissolve.

A second pass examines narrow annotation bands in four directions: horizontal, vertical, and both diagonals. It requires matching reliable original-image palette families at the ends of a run, within **24 Euclidean native pixels**, no water or visible intervening geology, and agreement where directional evidence competes. Diagonal distances are not treated as if each step were one pixel.

**Visible-paint safeguard:** an expanded annotation buffer can cover genuine thin geology whose eroded color core disappeared. Native source pixels with a close palette match (CIELAB distance below 4), sufficient brightness/chroma and no dark ink are therefore additional protected evidence, even inside that buffer. Those pixels cannot be recolored or crossed by a repair. This is still a color-based safeguard, not an authoritative lithological determination.

Matching source evidence can reconnect separate interiors or remove a wholly untrusted annotation halo inside a body already connected around the overprint. A patch that cuts a body containing reliable, visibly colored, unmasked or water evidence is rejected whole. Only a completely masked and unsupported annotation component may be consumed or broken up. No generic morphological closing, proximity buffer, or unsupported long-distance joining is used.

This pass changed **11,283 native pixels**, localized to **2,134 repair areas affecting 371 bodies**. These counts are interpolation changes, not independent geological verification. Water, reliable class pixels and protected visible paint were unchanged. Competing or unsafe evidence was rejected. The net body count is not a correctness target.

**Source counterexample checked:** the two OGp lenses sampled at original-photo pixels (2410, 2610) and (2442, 2610) have another visible unit between them. They remain separate in the exported GIS layer. An earlier small-band proposal would have joined them. The viewer's **Check two bodies kept separate** button exposes this location. Other uncertain contacts still require review.

The revision-5 ancestry audit finds 316 reconstructed continuous regions containing 730 old internal seams. At least 80% of each listed previous polygon's area must lie in its new same-palette-family parent. Each displayed old seam must separate two such former fragments and now predominantly lie inside the restored region. These are measurable overlap/ancestry criteria—not an assertion that all geological identity has been manually verified.

**Trade-off:** the continuity-first policy can merge genuinely different units that share an indistinguishable color and are separated only by a black contact. The source labels and stratigraphy must resolve those cases. Color equivalence alone is not proof of geological identity. Overprints can still cause false color halos or omitted narrow units; these remain exposed for review.

After noding the shared network, contacts are sampled at uniform distances and smoothed over approximately 2.2 native pixels. Nearby dark-stroke centers guide the line only where sustained photo evidence and differing colors on opposite sides support a contact. Proposed movement is limited to 4.5 pixels. Adjustments that would cross another contact are reduced. Every face must survive one-to-one; junctions and adjacent edges remain common.

This removes the raster-step pattern rather than merely rounding every step. Some angularity is retained at junctions, sharp original contacts and narrow bodies to avoid destroying features. The geometry is not claimed to be a perfect manual tracing of every printed boundary.

## Other anomalies found and exposed in the viewer

- **Unmatched map codes:** OGp and S occur in readable map labels without corresponding legend codes. Their lithology remains unresolved; it is not guessed from a similar color.
- **Similar legend colors:** several entries have effectively indistinguishable fills. `candidates` lists alternatives. Body-level majority color is not geological verification.
- **Narrow bodies:** some may be genuine geology; others may be residual road or label halos. They are retained and flagged rather than deleted indiscriminately.
- **Annotation-heavy reconstruction:** heavily covered regions depend on inferred neighbors. Annotation percentages include a buffer around strokes, so they are not literally the percentage of printed black ink and are not accuracy scores.
- **Restored continuous regions:** marked `CONTINUITY_RESTORED` where revision-5 ancestry supports a reconnection. Direct annotation-band interpolation is separately marked `ANNOTATION_BAND_REPAIR`, with localized areas available in the viewer. This is an inference flag, not a verification grade. No new `SPLIT_NEEDS_REVIEW` dark-line subdivisions are generated.
- **Water interpretation:** separated from geology, but its classification still needs checking against the photo.

The viewer's **Inspect next restored connection** control zooms to an old seam inside a reconnected region. The optional coral overlay is revision-5 history, not current geometry. Photo comparison preserves that location. The general anomaly queue jumps to individual flagged polygons. Flags overlap and are **not confirmed errors**. Not every legend row is recovered; absence from the output is not evidence that a unit is absent from the source. None of the polygons is certified as fully geologically verified. IDs changed in revision 6 as artificial fragments were recombined. Use `continuity_crosswalk.csv` and `continuity_review.json` for supported revision-5 ancestry; unmatched or highly altered fragments are not forced into a crosswalk.

## GIS use

Unzip the download and keep all companion files together. Add `ngsa_geology.shp`; apply its QML for colored fills without outlines. Add `shared_contacts.shp` above it for fine **non-black** green contacts. This draws a boundary once rather than twice. The main polygon geometry also shares those exact edges. `mapped_footprint` is an auxiliary union, not the individual geological layer.

The download includes the original review crop as `source_reference.jpg` with `.jgw`/`.prj` georeferencing. The crop is a JPEG re-encoding for viewing; classification uses the original supplied JPG. Color styles have been XML-checked, not opened in a desktop QGIS session here.

### Fields

| Field | Interpretation |
|---|---|
| poly_id | Unique singlepart polygon ID |
| body_id | Reconstructed seed-body ID; separate final parts can share this while retaining unique poly_id values |
| class_id | Legend 1–92; unresolved map codes 93–94; water 95 |
| unit_code / lithology | Tentative legend/map code and color-derived description |
| hex_color | Non-black display fill |
| area_km2 | Approximate geodesic area under assumed WGS84 |
| ann_pct | Body-wide source annotation-buffer percentage, not confidence |
| ambig_pct | Body-wide close first/second color matches, not confidence |
| candidates | Similar palette class IDs, including the selected class |
| contact_qa | CONTINUITY_RESTORED, ANNOTATION_BAND_REPAIR or COLOR_CONTACT_DRAFT; none means verified |
| prior_n | Number of supported revision-5 parent fragments for an audited merge; 0 when not established |
| qa_status | Draft, unresolved code, or water—not a verification grade |

## Coordinates and limitations

Assigned CRS **WGS 84 / EPSG:4326**; x = longitude, y = latitude. The printed regular degree grid provides the fit. The original datum is **unconfirmed**; assigning WGS84 is not a verified datum transformation. A native pixel is approximately 335 m on the ground. The map is generalized, and real positional error can exceed pixel-level fit residuals.

The browser uses rounded pixel-space geometry for display and selection; the shapefiles retain full geographic geometry. Topology validation is not geological validation. Do not use this draft for site-scale, engineering, regulatory, resource or publication decisions without authoritative positional and geological checks.

## Provenance and reproduction

The supplied NGSA image remains the source; no external geology datasets or generated images were substituted. The source SHA-256 is recorded in `quality.json`. Rights in the original map remain with their holders; this repository does not claim official endorsement.

From the repository:

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_map.py
.venv/bin/python scripts/audit_continuity.py
.venv/bin/python scripts/audit_repairs.py
.venv/bin/python scripts/validate_exports.py
.venv/bin/python scripts/package_map.py
```

Native arrays and temporary files go in ignored `.cache/`. `data/map/` contains GIS components and reports. `public/data/` contains viewer data and the portable ZIP. All UI assets run locally without map tiles, third-party fonts or external services.

The audit uses the published revision-5 map at Git commit `a62427bf26b3861fe58221a3f718626daa0455d8` or its cached JSON in `.cache/baseline/map_v5.json`. Keep that history when rebuilding (a shallow clone may need the commit fetched). The baseline SHA-256 is recorded in the audit. Final exported-data validation works without the cache. Revision-5 and revision-6 ZIPs are retained for comparison; the current download is `NGSA_geology_v7.zip`.

`annotation_repairs.json` records localized fills, preserved evidence checks and the separate-lens counterexample. The ancestry audit is idempotent: rerunning it replaces its tags rather than accumulating stale previous IDs. Ancestry and direct-band counts intentionally represent different evidence.
