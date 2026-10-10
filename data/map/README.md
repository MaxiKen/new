# NGSA geological-map interpretation · revision 5

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

Dark strokes can recover additional divisions inside similar-colored regions, but roads and faults can imitate such contacts. Substantial internal color components are required, and these divisions are explicitly flagged. Hidden and dashed same-color contacts may still be merged; artificial splits can remain.

After noding the shared network, contacts are sampled at uniform distances and smoothed over approximately 2.2 native pixels. Nearby dark-stroke centers guide the line only where sustained photo evidence and differing colors on opposite sides support a contact. Proposed movement is limited to 4.5 pixels. Adjustments that would cross another contact are reduced. Every face must survive one-to-one; junctions and adjacent edges remain common.

This removes the raster-step pattern rather than merely rounding every step. Some angularity is retained at junctions, sharp original contacts and narrow bodies to avoid destroying features. The geometry is not claimed to be a perfect manual tracing of every printed boundary.

## Other anomalies found and exposed in the viewer

- **Unmatched map codes:** OGp and S occur in readable map labels without corresponding legend codes. Their lithology remains unresolved; it is not guessed from a similar color.
- **Similar legend colors:** several entries have effectively indistinguishable fills. `candidates` lists alternatives. Body-level majority color is not geological verification.
- **Narrow bodies:** some may be genuine geology; others may be residual road or label halos. They are retained and flagged rather than deleted indiscriminately.
- **Annotation-heavy reconstruction:** heavily covered regions depend on inferred neighbors. Annotation percentages include a buffer around strokes, so they are not literally the percentage of printed black ink and are not accuracy scores.
- **Inferred same-color contacts:** possible road/fault/contact confusion is preserved as `SPLIT_NEEDS_REVIEW`.
- **Water interpretation:** separated from geology, but its classification still needs checking against the photo.

The viewer's anomaly queue jumps to individual flagged polygons. Flags overlap and are **not confirmed errors**. Not every legend row is recovered; absence from the output is not evidence that a unit is absent from the source. None of the polygons is certified as fully geologically verified. This revision was rebuilt because earlier generated packages were absent from the checkout; its IDs/counts are new and not asserted to match revisions 1–4.

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
| contact_qa | Inferred split needs review or color-derived contact draft |
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
.venv/bin/python scripts/validate_exports.py
.venv/bin/python scripts/package_map.py
```

Native arrays and temporary files go in ignored `.cache/`. `data/map/` contains GIS components and reports. `public/data/` contains viewer data and the portable ZIP. All UI assets run locally without map tiles, third-party fonts or external services.
