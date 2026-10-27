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

CASES = [
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
        [("table", t, None, None) for t in
         ("mineral_symbols", "mineral_localities", "mineral_localities_refined",
          "mineral_localities_utm32n", "mineral_localities_icons",
          "mineral_localities_icons_utm32n", "mineral_localities_equal_area")]),
]

con.execute("DELETE FROM gpkg_metadata_reference")
con.execute("DELETE FROM gpkg_metadata")
refs = []
for mid, scope, xml, targets in CASES:
    ET.fromstring(xml)  # must be well-formed before it goes in the file
    con.execute("INSERT INTO gpkg_metadata (id, md_scope, md_standard_uri, mime_type, metadata)"
                " VALUES (?,?,?,?,?)",
                (mid, scope, ISO19115, "text/xml", xml))
    for scope, table, col, rowid in targets:
        con.execute("INSERT INTO gpkg_metadata_reference (reference_scope, table_name,"
                    " column_name, row_id_value, timestamp, md_file_id, md_parent_id)"
                    " VALUES (?,?,?,?,?,?,NULL)",
                    (scope, table, col, rowid, last, mid))
        refs.append(dict(scope=scope, table=table, md_file_id=mid))
con.commit()

# verify what was written, from the file
check = con.execute("SELECT count(*) FROM gpkg_metadata").fetchone()[0]
refs_in = con.execute("SELECT count(*) FROM gpkg_metadata_reference").fetchone()[0]
unknown = con.execute(
    "SELECT r.table_name FROM gpkg_metadata_reference r LEFT JOIN gpkg_contents c"
    " ON c.table_name = r.table_name WHERE r.reference_scope='table'"
    " AND c.table_name IS NULL").fetchall()
dangling = con.execute(
    "SELECT r.md_file_id FROM gpkg_metadata_reference r LEFT JOIN gpkg_metadata m"
    " ON m.id = r.md_file_id WHERE m.id IS NULL").fetchall()
integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
for (mid,) in con.execute("SELECT id FROM gpkg_metadata"):
    ET.fromstring(con.execute("SELECT metadata FROM gpkg_metadata WHERE id=?", (mid,)).fetchone()[0])
con.close()

assert not unknown, f"reference to a table that is not in gpkg_contents: {unknown}"
assert not dangling, f"reference to a missing metadata row: {dangling}"
assert integrity == "ok", integrity

report = dict(
    tables_added=["gpkg_metadata", "gpkg_metadata_reference"],
    records=check, references=refs_in, timestamp_used=last, integrity=integrity,
    records_detail=[{"id": m, "scope": scope, "chars": len(x),
                     "about": [r["table"] or "the whole file" for r in refs
                               if r["md_file_id"] == m]} for m, scope, x, _ in CASES],
    licences=[{"source": s, "terms": t} for s, t in LICENCES],
    note="ids and timestamps are pinned, so a rerun rewrites the same bytes",
)
json.dump(report, open(OUT, "w"), indent=1)
print(f"gpkg_metadata: {check} records, {refs_in} references -> {OUT.name}")
for r in report["records_detail"]:
    print(f"  id {r['id']}: {len(r['about'])} reference(s) - {', '.join(r['about'])[:90]}")
print(f"  timestamps = {last}; integrity_check: {integrity}")
