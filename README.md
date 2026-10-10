# Nigeria geological-map review

A reproducible **draft** interpretation of the supplied NGSA geological map, with a local interactive viewer and an ESRI shapefile package.

**Black is not a geological feature.** The derived map has no black/near-black fills or black outlines. Dotted/dashed black contacts that separate different units and small dark-outlined labeled intrusions are preserved as color boundaries; solid black overprints over uniform color (roads, railway, ridges, text) are filled from surrounding geology. The untouched photo is available only in clearly labelled comparison modes.

## View it

No runtime npm packages or external map services are needed:

```sh
python server.py --host 0.0.0.0 --port 3000
# or: npm run dev
```

Open the provided live preview (or `http://localhost:3000` when running on your own computer).

The viewer supports:
- Pan, wheel/touch zoom, keyboard zoom and fit; desktop and mobile layouts.
- Clean polygons, original photo, and an adjustable comparison divider.
- Click-to-inspect singlepart polygon attributes and review flags.
- Searchable legend; highlighting never removes polygons from the coverage.
- A continuity-review queue with previous IDs and an optional coral overlay of removed revision-5 cuts.
- Localized annotation-fill review and a source-photo check of two correctly separated bodies.
- A navigable anomaly queue, including restored connections, narrow bodies, annotation-heavy regions, similar colors and unresolved codes.
- One-copy shared-contact display in a non-black color.
- A direct shapefile ZIP download.

**The original-photo view still has black annotations by design. It is not the cleaned layer.**

## Contact & small-feature preservation (revision 8)

Revision 7 removed false splits caused by dark strokes, but it also erased legitimate printed features. Revision 8 adds three targeted safeguards while keeping the continuity-first policy (no global dissolve by color, no dark-stroke subdivision of connected bodies):

- **Two dotted/dashed lines enclosing a new color are preserved.** Thin elongated dark strokes (compact text blobs are filtered out by length/width ratio) whose two sides show different classified palette families become barriers that annotation-band repair cannot cross. Short gaps between adjacent dark dots are bridged so each dotted/dashed chain forms a complete boundary. After repair the classified regions are split at those barriers with watershed segmentation, turning the preserved ink into real polygon edges (rendered in non-black shared-contact color, not black).
- **A dotted/dashed line with a different color on each side is kept** by the same detector.
- **Small dark-outlined colored patches with a black label on them** (intrusions, enclaves, plugs, etc.) are detected before the EDT fill and added as explicit seeds. Their interior color is preserved instead of being dissolved into the surrounding large body.

Solid black overprints that do NOT separate different colors — railway lines, ridge hatchuring with ticks, thick roads, town/place-name text over uniform geology — are still removed and filled from neighboring colors.

The cumulative ancestry audit comparing to revision 5 is still available, and the visible-paint safeguard that prevents bridging two clearly separated OGp lenses is retained.

In the preview, choose **Inspect next restored connection**. Coral lines are the *previous removed cuts*, not current boundaries. **Compare current view with photo** keeps the location and zoom. Turn off the coral overlay for the clean result.

## GIS deliverable

Download **[`public/data/NGSA_geology_v8.zip`](public/data/NGSA_geology_v8.zip)**, or use the viewer's Download button. Keep the shapefile companion files together.

- `ngsa_geology`: individual polygon features, not a country-wide multipart dissolve by color.
- `shared_contacts`: each boundary once, with neighboring polygon IDs.
- `mapped_footprint`: auxiliary coverage union, not an official national border.
- QGIS styles, source reference crop/world file, legend and QA reports.

These are geometry/processing checks, **not geological verification**. Uncertain assignments remain flagged. The original datum is unconfirmed and WGS84 is assumed. Read **[method, attributes and limitations](docs/NOTES.md)** before using the output.

## Rebuild from the original image

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_map.py
.venv/bin/python scripts/audit_continuity.py
.venv/bin/python scripts/audit_repairs.py
.venv/bin/python scripts/validate_exports.py
.venv/bin/python scripts/package_map.py
```

The geometry pipeline uses the original JPG plus the transcribed legend, without external geology datasets. The historical ancestry-comparison step additionally reads revision 5 at commit `a62427bf26b3861fe58221a3f718626daa0455d8`; retain that Git history (or `.cache/baseline/map_v5.json`) when rerunning the audit. A shallow clone may need that commit fetched first. The published validation does not require the intermediate cache.

## Tests

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
.venv/bin/python scripts/validate_exports.py

# With the viewer running in another terminal:
npm ci
npm run test:browser
```

Browser tests use Playwright and an npm-bundled headless Chromium. On Linux x86-64, the test harness extracts the NSS libraries included in that package into ignored `.cache/`, avoiding an additional browser download or OS package install. `BASE_URL` can point tests at another running instance.

The server exposes **only `public/`**, never the repository, `.git` or credentials. Browser requests use relative same-origin URLs; the preview accepts its proxied host and binds to `0.0.0.0`. No source photographs were modified.
