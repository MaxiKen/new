#!/usr/bin/env python3
"""Put the provenance and the licences *inside* the GeoPackage.

The attribution currently travels next to the file, in `README.md`,
`metadata.json` and `raster_georeferencing.json`. A file that is copied on its
own - the normal fate of a `.gpkg` - arrives with none of it. GeoPackage 1.4 has
two optional tables for exactly this: `gpkg_metadata` (records, as ISO 19139
XML) and `gpkg_metadata_reference` (which part of the file each record is
about).

This writes four records:

  1. `geopackage` scope - the master record: what the file is, where every
     layer came from, the licence of each source, the bounding box, and the
     two standing warnings (the mineral positions are withdrawn; the towns
     gazetteer is GeoNames, CC BY 4.0).
  2. `table` scope `towns_geonames` - the CC BY 4.0 attribution GeoNames
     requires.
  3. `table` scope `national_territory` - the Natural Earth 10m outline and
     the 2023 sheet border it was replaced with.
  4. `table` scope, the six `mineral_localities*` layers and
     `mineral_symbols` - the withdrawal notice, attached to the layers that
     carry the withdrawn coordinates rather than only to the README.

All ids are fixed and every row is rewritten to the same bytes on a rerun, so
the script is idempotent; the timestamps are pinned to the date the records
were written, not the clock. No feature, tile, attribute or pixel is touched.

Run:  python add_gpkg_metadata.py
"""
import datetime as dt
import json
import pathlib
import sqlite3
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import geopandas as gpd

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
COPIES = HERE / "Nigeria_Geology_Minerals_projected_copies.gpkg"
OUT = HERE / "gpkg_metadata.json"

ISO19115 = "https://www.iso.org/standard/53798.html"

DDL = """
CREATE TABLE IF NOT EXISTS gpkg_metadata (
  id INTEGER CONSTRAINT m_pk PRIMARY KEY ASC NOT NULL,
  md_scope TEXT NOT NULL DEFAULT 'dataset',
  md_standard_uri TEXT NOT NULL,
  mime_type TEXT NOT NULL DEFAULT 'text/xml',
  metadata TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS gpkg_metadata_reference (
  reference_scope TEXT NOT NULL,
  table_name TEXT,
  column_name TEXT,
  row_id_value INTEGER,
  timestamp DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  md_file_id INTEGER NOT NULL,
  md_parent_id INTEGER,
  CONSTRAINT crmr_mfi_fk FOREIGN KEY (md_file_id) REFERENCES gpkg_metadata(id),
  CONSTRAINT crmr_mpi_fk FOREIGN KEY (md_parent_id) REFERENCES gpkg_metadata(id));
"""

WITHDRAWN = (
    "POSITIONS WITHDRAWN. The point coordinates in this layer were measured "
    "against the printed sheet and sit a median 14.1 px (about 10 km) from any "
    "printed symbol; their nearest-neighbour distribution is indistinguishable "
    "from a random scatter of the same size. Do not use them for calculation, "
    "interpolation or distance. mineral_symbols and minerals_named hold the "
    "positions that were measured against the sheet; mineral_localities* hold "
    "attributes only until they are rebuilt. See minerals_named.md."
)

LICENCES = [
    ("NGSA printed sheets (geology, minerals, soils, land cover, climate, "
     "population, ethnography, forest reserves)", "Nigeria Geological Survey "
     "Agency; digitised for this dataset, no separate licence granted by NGSA - "
     "cite the Agency and the sheet"),
    ("towns_geonames", "GeoNames, CC BY 4.0 (https://www.geonames.org/)"),
    ("national_territory / international_boundary",
     "Natural Earth 1:10m (public domain), edited onto the 2023 sheet border"),
    ("everything else", "derived from the NGSA sheets by the scripts in maps/"),
]


def record_xml(title, abstract, bbox, scope_note):
    west, south, east, north = bbox
    lic = "".join(
        f"<gmd:otherConstraints><gco:CharacterString>{escape(f'{src}: {txt}')}"
        f"</gco:CharacterString></gmd:otherConstraints>"
        for src, txt in LICENCES)
    return f"""<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" \
xmlns:gco="http://www.isotc211.org/2005/gco">
  <gmd:fileIdentifier><gco:CharacterString>maxiken/new:nigeria-geology-minerals:4326</gco:CharacterString></gmd:fileIdentifier>
  <gmd:language><gco:CharacterString>eng</gco:CharacterString></gmd:language>
  <gmd:hierarchyLevel><gmd:MD_ScopeCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_ScopeCode" codeListValue="dataset">dataset</gmd:MD_ScopeCode></gmd:hierarchyLevel>
  <gmd:contact><gmd:CI_ResponsibleParty>
    <gmd:organisationName><gco:CharacterString>MaxiKen/new (this repository)</gco:CharacterString></gmd:organisationName>
    <gmd:role><gmd:CI_RoleCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#CI_RoleCode" codeListValue="pointOfContact">pointOfContact</gmd:CI_RoleCode></gmd:role>
  </gmd:CI_ResponsibleParty></gmd:contact>
  <gmd:dateStamp><gco:Date>{STAMP}</gco:Date></gmd:dateStamp>
  <gmd:referenceSystemInfo><gmd:MD_ReferenceSystem><gmd:referenceSystemIdentifier>
    <gmd:RS_Identifier><gmd:code><gco:CharacterString>EPSG:4326 (layers in 6933 and 32632 are declared per layer)</gco:CharacterString></gmd:code></gmd:RS_Identifier>
  </gmd:referenceSystemIdentifier></gmd:MD_ReferenceSystem></gmd:referenceSystemInfo>
  <gmd:identificationInfo><gmd:MD_DataIdentification>
    <gmd:citation><gmd:CI_Citation>
      <gmd:title><gco:CharacterString>{escape(title)}</gco:CharacterString></gmd:title>
      <gmd:date><gmd:CI_Date><gmd:date><gco:Date>{STAMP}</gco:Date></gmd:date>
        <gmd:dateType><gmd:CI_DateTypeCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#CI_DateTypeCode" codeListValue="publication">publication</gmd:CI_DateTypeCode></gmd:dateType>
      </gmd:CI_Date></gmd:date>
    </gmd:CI_Citation></gmd:citation>
    <gmd:abstract><gco:CharacterString>{escape(abstract)}</gco:CharacterString></gmd:abstract>
    <gmd:status><gmd:MD_ProgressCode codeList="http://standards.iso.org/iso/19139/resources/gmxCodelists.xml#MD_ProgressCode" codeListValue="completed">completed</gmd:MD_ProgressCode></gmd:status>
    <gmd:resourceConstraints><gmd:MD_LegalConstraints>
      <gmd:useLimitation><gco:CharacterString>{escape(scope_note)}</gco:CharacterString></gmd:useLimitation>
      {lic}
    </gmd:MD_LegalConstraints></gmd:resourceConstraints>
    <gmd:extent><gmd:EX_Extent><gmd:geographicElement><gmd:EX_GeographicBoundingBox>
      <gmd:westBoundLongitude><gco:Decimal>{west:.6f}</gco:Decimal></gmd:westBoundLongitude>
      <gmd:eastBoundLongitude><gco:Decimal>{east:.6f}</gco:Decimal></gmd:eastBoundLongitude>
      <gmd:southBoundLatitude><gco:Decimal>{south:.6f}</gco:Decimal></gmd:southBoundLatitude>
      <gmd:northBoundLatitude><gco:Decimal>{north:.6f}</gco:Decimal></gmd:northBoundLatitude>
    </gmd:EX_GeographicBoundingBox></gmd:geographicElement></gmd:EX_Extent></gmd:extent>
  </gmd:MD_DataIdentification></gmd:identificationInfo>
  <gmd:dataQualityInfo><gmd:DQ_DataQuality><gmd:lineage><gmd:LI_Lineage>
    <gmd:statement><gco:CharacterString>{escape(LINEAGE)}</gco:CharacterString></gmd:statement>
  </gmd:LI_Lineage></gmd:lineage></gmd:DQ_DataQuality></gmd:dataQualityInfo>
</gmd:MD_Metadata>"""


LINEAGE = (
    "Geometry and attributes extracted from the two NGSA printed sheets (2003 "
    "solid geology, 2023 geology and minerals) as vector paths, with the affine "
    "fitted to each printed graticule; unit codes, ages, legend rows and "
    "in-polygon labels rebuilt from the sheet's own layer names. The nine raster "
    "layers are the printed sheets in 'new map/', georeferenced per sheet with a "
    "measured border offset. The state outline is Natural Earth 1:10m, replaced "
    "on the 2023 sheet border. The towns gazetteer is GeoNames."
)

con = sqlite3.connect(GPKG)
con.execute("PRAGMA foreign_keys=ON")
con.executescript(DDL)

# A pinned stamp. The file's own `last_change` was tried first, but it moves
# whenever *any* later step writes to the file, which makes a rerun differ; the
# records were written on this date and saying so is both true and stable.
STAMP = "2026-10-27"
last = f"{STAMP}T00:00:00.000Z"

terr = gpd.read_file(GPKG, layer="national_territory")
west, south, east, north = terr.total_bounds
n_feat = con.execute("SELECT sum(1) FROM gpkg_contents WHERE data_type='features'").fetchone()[0]
layers = con.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features' ORDER BY table_name").fetchall()
tiles = con.execute("SELECT table_name FROM gpkg_contents WHERE data_type='tiles' ORDER BY table_name").fetchall()
n_attr = sum(gpd.read_file(GPKG, layer=t).shape[0] for (t,) in layers)

MASTER = record_xml(
    "Nigeria - geology, minerals, soils, land cover, climate and places (GeoPackage)",
    f"{len(layers)} feature layers ({n_attr:,} features) and {len(tiles)} raster "
    f"layers ({len(tiles)} of the nine printed sheets in 'new map/'), EPSG:4326 with "
    f"per-layer projected copies. Layers: " + ", ".join(t for (t,) in layers) + ".",
    (west, south, east, north),
    "Read README.md and LAYERS.md before use: the mineral stand-in layers carry "
    "withdrawn coordinates, the geology is a 1:2,000,000 generalisation, and the "
    "rasters keep the sheets' own positional error. Attribution must stay with "
    "the file.")

# a record may only reference a table that the file it is written into holds, so
# each file gets its own case list, filtered against its own gpkg_contents
MINERAL_LAYERS = ("mineral_symbols", "mineral_localities", "mineral_localities_refined",
                  "mineral_localities_icons", "mineral_localities_utm32n",
                  "mineral_localities_icons_utm32n", "mineral_localities_equal_area")


def write_records(path, cases, stamp):
    """Replace the metadata tables of one file with `cases`; return what was written."""
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(DDL)
    contents = {r[0] for r in con.execute("SELECT table_name FROM gpkg_contents")}
    con.execute("DELETE FROM gpkg_metadata_reference")
    con.execute("DELETE FROM gpkg_metadata")
    written = []
    for mid, scope, xml, targets in cases:
        ET.fromstring(xml)                      # well-formed before it goes in
        missing = [t for _, t, *_ in targets if t and t not in contents]
        assert not missing, f"{path.name}: records reference absent table(s) {missing}"
        con.execute("INSERT INTO gpkg_metadata (id, md_scope, md_standard_uri, mime_type,"
                    " metadata) VALUES (?,?,?,?,?)", (mid, scope, ISO19115, "text/xml", xml))
        for rscope, table, col, rowid in targets:
            con.execute("INSERT INTO gpkg_metadata_reference (reference_scope, table_name,"
                        " column_name, row_id_value, timestamp, md_file_id, md_parent_id)"
                        " VALUES (?,?,?,?,?,?,NULL)", (rscope, table, col, rowid, stamp, mid))
            written.append(dict(scope=rscope, table=table, md_file_id=mid))
    con.commit()
    n_rec, n_ref = (con.execute("SELECT count(*) FROM gpkg_metadata").fetchone()[0],
                    con.execute("SELECT count(*) FROM gpkg_metadata_reference").fetchone()[0])
    unknown = con.execute(
        "SELECT r.table_name FROM gpkg_metadata_reference r LEFT JOIN gpkg_contents c"
        " ON c.table_name = r.table_name WHERE r.reference_scope='table'"
        " AND c.table_name IS NULL").fetchall()
    dangling = con.execute(
        "SELECT r.md_file_id FROM gpkg_metadata_reference r LEFT JOIN gpkg_metadata m"
        " ON m.id = r.md_file_id WHERE m.id IS NULL").fetchall()
    for (mid,) in con.execute("SELECT id FROM gpkg_metadata"):
        ET.fromstring(con.execute("SELECT metadata FROM gpkg_metadata WHERE id=?",
                                  (mid,)).fetchone()[0])
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    con.close()
    assert not unknown and not dangling and integrity == "ok", (unknown, dangling, integrity)
    return dict(records=n_rec, references=n_ref, integrity=integrity, detail=written)


main_layers = [t for (t,) in layers]
MAIN_CASES = [
    (1, "dataset", MASTER, [("geopackage", None, None, None)]),
    (2, "featureType", record_xml(
        "towns_geonames - GeoNames populated places, Nigeria",
        "45,415 populated places from the GeoNames allCountries dump, with the "
        "state polygon each point falls in and SRTM elevation sampled at the point.",
        (west, south, east, north),
        "GeoNames data is licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. "
        "Attribution to GeoNames (https://www.geonames.org/) is required wherever "
        "this layer is published, in a map or in a data product. The dump is from "
        "2014-10-02; populations and boundaries in it are that old."),
        [("table", "towns_geonames", None, None)]),
    (3, "featureType", record_xml(
        "national_territory - Nigeria outline used to clip every layer",
        "The state outline in EPSG:4326: Natural Earth 1:10m, edited onto the "
        "2023 sheet border.",
        (west, south, east, north),
        "Natural Earth 1:10m is public domain. Editing it onto the NGSA 2023 "
        "border does not make the result authoritative for legal boundaries."),
        [("table", "national_territory", None, None),
         ("table", "international_boundary", None, None)]),
    (4, "featureType", record_xml(
        "Mineral positions - withdrawn",
        "The layers that carry the extraction's mineral-symbol coordinates, and "
        "the notice that those coordinates carry no positional information.",
        (west, south, east, north), WITHDRAWN),
        [("table", t, None, None) for t in MINERAL_LAYERS if t in main_layers]),
]

con_m = sqlite3.connect(GPKG)
main_report = write_records(GPKG, MAIN_CASES, last)

copies_report = None
if COPIES.exists():
    con_c = sqlite3.connect(COPIES)
    copy_layers = [r[0] for r in con_c.execute(
        "SELECT table_name FROM gpkg_contents WHERE data_type='features' ORDER BY 1")]
    parent = {"geology_units_utm32n": "geology_units",
              "geology_units_equal_area": "geology_units",
              "mineral_localities_icons_utm32n": "mineral_localities_icons",
              "mineral_localities_equal_area": "mineral_localities_icons",
              "mineral_localities_utm32n": "mineral_localities_refined"}
    srs = sorted({r[0] for r in con_c.execute("SELECT DISTINCT srs_id FROM gpkg_contents")})
    con_c.close()
    COPY_CASES = [
        (1, "dataset", record_xml(
            "Nigeria - measurement copies of the projected layers (GeoPackage)",
            f"{len(copy_layers)} reprojections of layers in "
            f"Nigeria_Geology_Minerals_4326.gpkg, for calculating area and length in "
            f"metres. Layers: " + ", ".join(f"{c} (from {parent[c]})" for c in copy_layers)
            + f". CRS: {', '.join('EPSG:%d' % s for s in srs)}.",
            (west, south, east, north),
            "These layers are the same features as the EPSG:4326 originals, "
            "reprojected: same rows, same attributes, same key. They live here "
            "rather than in the deliverable because that file is a single CRS "
            "(EPSG:4326, the only one its tiled rasters can carry) so that its "
            "layers can be laid on each other without a reprojection. Use them to "
            "measure, the originals to draw. Same source and terms as the "
            "originals: NGSA sheets, digitised for this dataset."),
            [("geopackage", None, None, None)]
            + [("table", c, None, None) for c in copy_layers]),
        (2, "featureType", record_xml(
            "Mineral positions - withdrawn (projected copies)",
            "The reprojected copies of the mineral-locality layers, and the notice "
            "that the coordinates in them carry no positional information.",
            (west, south, east, north), WITHDRAWN),
            [("table", t, None, None) for t in
             ("mineral_localities_utm32n", "mineral_localities_icons_utm32n",
              "mineral_localities_equal_area") if t in copy_layers]),
    ]
    copies_report = write_records(COPIES, COPY_CASES, last)

# The same reasoning applies to the rest of the file's own bookkeeping, which is
# what stood between this dataset and a build you can re-run. Three things drifted
# on every run and none of them is data:
#   * `gpkg_contents.last_change` is the wall clock of whoever ran the pipeline,
#     because the repair and describing passes rewrite tables and bump it;
#   * the rows of the register tables are re-inserted by those passes in whatever
#     order they happened to run, so the row ids - and with them every page of the
#     file - move;
#   * SQLite's header counts writes (change counter, schema cookie).
# Left alone, a rerun rewrote all 49 MB of a byte-identical dataset. This is the
# last writer, so it normalises all three: the stamp is pinned, the registers are
# rewritten in sorted order, VACUUM rebuilds the file from its contents alone, and
# the header counters are set to a fixed value. Nothing here describes a layer, and
# the sort is total, so the same data gives the same bytes.
STAMPED_TABLES = ("gpkg_contents",)


def normalise(path, stamp):
    """Pin the timestamps, fix the register row order, VACUUM, pin the header."""
    con = sqlite3.connect(path, isolation_level=None)
    n = con.execute("SELECT COUNT(*) FROM gpkg_contents").fetchone()[0]
    con.execute("UPDATE gpkg_contents SET last_change = ?", (stamp,))
    con.execute("BEGIN")
    for t in ("gpkg_contents", "gpkg_geometry_columns", "gpkg_extensions",
              "gpkg_ogr_contents", "gpkg_tile_matrix", "gpkg_tile_matrix_set",
              "gpkg_spatial_ref_sys", "gpkg_metadata", "gpkg_metadata_reference"):
        if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                           (t,)).fetchone():
            continue
        cols = [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]
        quoted = ",".join(f'"{c}"' for c in cols)
        rows = con.execute(f'SELECT {quoted} FROM "{t}"').fetchall()
        rows.sort(key=lambda r: [(v is not None, str(v)) for v in r])
        con.execute(f'DELETE FROM "{t}"')
        con.executemany(f'INSERT INTO "{t}" ({quoted}) VALUES ({",".join("?" * len(cols))})',
                        rows)
    con.execute("COMMIT")
    con.execute("VACUUM")
    con.close()
    # the counter and its mirror at offset 92 are written together, which is what
    # keeps the header self-consistent; the schema cookie counts DDL, not data
    raw = bytearray(path.read_bytes())
    for off in (24, 92):
        raw[off:off + 4] = (1).to_bytes(4, "big")
    raw[40:44] = (1).to_bytes(4, "big")
    path.write_bytes(raw)
    return n


report = dict(
    tables_added=["gpkg_metadata", "gpkg_metadata_reference"],
    last_change_pinned=dict(main=normalise(GPKG, last),
                            copies=normalise(COPIES, last) if copies_report else 0),
    files={
        GPKG.name: dict(records=main_report["records"],
                        references=main_report["references"],
                        integrity=main_report["integrity"],
                        about=[r["table"] or "the whole file" for r in main_report["detail"]]),
        COPIES.name: dict(records=copies_report["records"],
                          references=copies_report["references"],
                          integrity=copies_report["integrity"],
                          about=[r["table"] or "the whole file"
                                 for r in copies_report["detail"]]) if copies_report else None,
    },
    timestamp_used=last,
    licences=[{"source": s_, "terms": t} for s_, t in LICENCES],
    note="ids and timestamps are pinned, so a rerun rewrites the same bytes",
)
json.dump(report, open(OUT, "w"), indent=1)

for name, d in report["files"].items():
    if not d:
        continue
    print(f"{name}: {d['records']} record(s), {d['references']} reference(s), "
          f"integrity {d['integrity']}")
    for r in d["about"]:
        print(f"   - {r}")
print(f"timestamps = {last} -> {OUT.name}")
