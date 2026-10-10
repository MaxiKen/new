# Nigeria geological-map review

A reproducible **draft** interpretation of the supplied NGSA geological map, with a local interactive viewer and an ESRI shapefile package.

**Black is not a geological feature.** The derived map has no black/near-black fills or black outlines. Labels and cartographic strokes are filled from surrounding geological colors. The untouched photo is available only in clearly labelled comparison modes.

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
- A navigable anomaly queue, including uncertain contacts, narrow bodies, annotation-heavy regions, similar colors and unresolved codes.
- One-copy shared-contact display in a non-black color.
- A direct shapefile ZIP download.

**The original-photo view still has black annotations by design. It is not the cleaned layer.**

## GIS deliverable

Download **[`public/data/NGSA_geology_v5.zip`](public/data/NGSA_geology_v5.zip)**, or use the viewer's Download button. Keep the shapefile companion files together.

- `ngsa_geology`: individual polygon features, not a country-wide multipart dissolve by color.
- `shared_contacts`: each boundary once, with neighboring polygon IDs.
- `mapped_footprint`: auxiliary coverage union, not an official national border.
- QGIS styles, source reference crop/world file, legend and QA reports.

The current build has **2,443 singlepart polygons** and **6,635 shared contact arcs**. Independent checks find **no internal gaps, no overlapping interiors, no black/near-black fill classes**, and coverage of all **422,325 tested black interior source pixels**.

These are geometry/processing checks, **not geological verification**. Uncertain assignments remain flagged. The original datum is unconfirmed and WGS84 is assumed. Read **[method, attributes and limitations](docs/NOTES.md)** before using the output.

## Rebuild from the original image

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_map.py
.venv/bin/python scripts/validate_exports.py
.venv/bin/python scripts/package_map.py
```

The pipeline uses the original JPG plus the transcribed legend. No earlier generated package or external geology dataset is needed. Earlier generated revisions were absent from the checkout; revision 5 is a fresh reproducible build, not a claim to preserve their feature IDs.

Only broad neutral regions may qualify as actual gray geological fills. Pale colored units are handled separately from gray annotations. Contacts are built as one shared network, smoothed by arclength, locally guided by the photo, and checked for crossings and face preservation. Water remains explicit rather than blank. See the method notes for inference limits.

## Tests

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
.venv/bin/python scripts/validate_exports.py

# With the viewer running in another terminal:
npm ci
npm run test:browser
```

Browser tests use Playwright and an npm-bundled headless Chromium. On Linux x86-64, the test harness extracts the NSS libraries included in that package into ignored `.cache/`, avoiding an additional browser download or OS package install. `BASE_URL` can point tests at another running instance.

Real-browser tests cover clean-map black-pixel exclusion, intentional black pixels in the source-photo view, selection, anomaly navigation, legend search/highlight, comparison, zoom, contact visibility, download, and responsive grid sizing. Screenshots are saved under ignored `.cache/browser/`.

## Repository layout

```
scripts/       native-image interpretation, geometry checks and packaging
public/        standalone viewer, source crop, display data and download ZIP
data/map/      geographic shapefiles, style files, provenance and QA reports
tests/         geometric regression tests and real-browser interaction tests
docs/          method and limitations
```

The server exposes **only `public/`**, never the repository, `.git` or credentials. Browser requests use relative same-origin URLs; the preview accepts its proxied host and binds to `0.0.0.0`. No source photographs were modified.
