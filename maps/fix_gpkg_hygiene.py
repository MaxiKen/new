#!/usr/bin/env python3
"""Make the GeoPackage describe exactly what it contains.

A GeoPackage carries registers *about* its contents: `gpkg_contents` (the
layers), `gpkg_geometry_columns`, `gpkg_extensions` (spatial indexes, tiling
schemes), the `rtree_<layer>_<column>` index tables, and `gpkg_tile_matrix`
(the zoom levels of each tile pyramid).  Building layers with GDAL's `to_file`
leaves entries behind in those registers, and the data itself still reads
perfectly - which is why `PRAGMA integrity_check` says "ok" for a file that
still advertises a layer, an index or a zoom level that is not there.

This script repairs the registers. No feature, tile, attribute or pixel is
touched; every change is recorded in `gpkg_hygiene.json`. All repairs are
idempotent - a second run changes nothing.

  1. `gpkg_extensions` rows whose subject does not exist
       * a feature table that is gone, and
       * a `gpkg_rtree_index` on a raster's `tile_data` column, which is a
         raster BLOB and cannot be indexed by an rtree
  2. `rtree_*` index tables whose layer is gone (and their shadow tables)
  3. spatial indexes that exist but are not declared -> *declare* them. An
     undeclared index is invisible to every conforming client, and the layer
     has no spatial query plan. This is the one repair that adds to the file.
  4. `gpkg_tile_matrix` zoom levels that hold no tiles (GDAL declares an
     overview for every level it could write, including levels it did not;
     a client that trusts the matrix asks for a tile that was never written)
  5. `gpkg_geometry_columns` rows whose table is gone
  6. VACUUM

Run:  python fix_gpkg_hygiene.py
"""
import json
import pathlib
import sqlite3

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "gpkg_hygiene.json"
SHADOW = ("_node", "_rowid", "_parent", "_data")

con = sqlite3.connect(GPKG)
con.execute("PRAGMA foreign_keys = ON")
cur = con.cursor()

tables = {r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table'")}
features = {r[0] for r in cur.execute(
    "SELECT table_name FROM gpkg_contents WHERE data_type = 'features'")}
tiles = {r[0] for r in cur.execute(
    "SELECT table_name FROM gpkg_contents WHERE data_type = 'tiles'")}
contents = features | tiles
geom_col = {r[0]: r[1] for r in cur.execute(
    "SELECT table_name, column_name FROM gpkg_geometry_columns")}
report = {"file": GPKG.name, "removed": {}, "added": {}, "kept": {}}

rtree_tables = {t for t in tables if t.startswith("rtree_") and not t.endswith(SHADOW)}
valid_rtree = {f"rtree_{t}_{c}" for t, c in geom_col.items() if t in features}

# 1. extension rows whose subject does not exist -----------------------------
dead = [(t, c, e) for t, c, e in cur.execute(
    "SELECT table_name, column_name, extension_name FROM gpkg_extensions")
    if t not in contents
    or (e == "gpkg_rtree_index" and t in tiles)]
cur.executemany("DELETE FROM gpkg_extensions WHERE table_name = ? AND column_name IS ?"
                " AND extension_name = ?", dead)
report["removed"]["extension_rows"] = [
    dict(table_name=t, column_name=c, extension_name=e) for t, c, e in dead]

# 2. rtree index tables for layers that are gone ------------------------------
orphan_rtree = sorted(rtree_tables - valid_rtree)
for t in orphan_rtree:
    cur.execute(f'DROP TABLE IF EXISTS "{t}"')
report["removed"]["orphan_rtree_tables"] = orphan_rtree

# 3. indexes that exist but are not declared ---------------------------------
declared = {(t, c) for t, c, e in cur.execute(
    "SELECT table_name, column_name, extension_name FROM gpkg_extensions"
    " WHERE extension_name = 'gpkg_rtree_index'")}
undeclared = sorted((t, c) for t, c in geom_col.items()
                    if t in features and f"rtree_{t}_{c}" in valid_rtree
                    and (t, c) not in declared)
cur.executemany(
    "INSERT INTO gpkg_extensions (table_name, column_name, extension_name,"
    " definition, scope) VALUES (?, ?, 'gpkg_rtree_index',"
    " 'http://www.geopackage.org/spec/#extension_rtree', 'write-only')",
    undeclared)
report["added"]["undeclared_indexes_declared"] = [f"{t}.{c}" for t, c in undeclared]
report["kept"]["rtree_indexes"] = sorted(valid_rtree & rtree_tables)
report["kept"]["declared_but_missing"] = sorted(
    f"{t}.{c}" for t, c in declared if f"rtree_{t}_{c}" not in rtree_tables)

# 4. tile-matrix zoom levels with no tiles -----------------------------------
stale_zoom = []
for t in sorted(tiles):
    have = {r[0] for r in cur.execute('SELECT DISTINCT zoom_level FROM "%s"' % t)}
    for (z,) in cur.execute("SELECT zoom_level FROM gpkg_tile_matrix"
                            " WHERE table_name = ?", (t,)):
        if z not in have:
            stale_zoom.append({"table": t, "zoom_level": z})
cur.executemany("DELETE FROM gpkg_tile_matrix WHERE table_name = ? AND zoom_level = ?",
                [(d["table"], d["zoom_level"]) for d in stale_zoom])
report["removed"]["tile_matrix_levels_without_tiles"] = stale_zoom

# 5. geometry-column rows for tables that do not exist -----------------------
gc_orphan = [t for t in geom_col if t not in contents]
cur.executemany("DELETE FROM gpkg_geometry_columns WHERE table_name = ?",
                [(t,) for t in gc_orphan])
report["removed"]["orphan_geometry_columns"] = gc_orphan

con.commit()
# 6. reclaim the pages the dropped index tables leave behind
cur.execute("VACUUM")
con.commit()

# ---- what the registers say now --------------------------------------------
report["after"] = {
    "features": len(features), "tiles": len(tiles),
    "extension_rows": cur.execute("SELECT count(*) FROM gpkg_extensions").fetchone()[0],
    "spatial_indexes": len({r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'rtree_%'")
        if not r[0].endswith(SHADOW)}),
    "tile_matrix_rows": cur.execute("SELECT count(*) FROM gpkg_tile_matrix").fetchone()[0],
    "integrity_check": cur.execute("PRAGMA integrity_check").fetchone()[0],
    "foreign_key_check": len(cur.execute("PRAGMA foreign_key_check").fetchall()),
    "size_mb": round(GPKG.stat().st_size / 1e6, 2),
}
con.close()

# the repairs are idempotent, so a rerun finds nothing to do; carry the record of
# the *first* repair forward rather than overwriting it with an empty one
if OUT.exists():
    previous = json.load(open(OUT))
    for key in ("history", "note"):
        if key in previous:
            report.setdefault(key, previous[key])
report.setdefault("history", dict(
    dangling_extension_rows=len(report["removed"]["extension_rows"]),
    orphan_rtree_indexes=len(report["removed"]["orphan_rtree_tables"]),
    undeclared_live_indexes=len(report["added"]["undeclared_indexes_declared"]),
    stale_tile_matrix_levels=len(report["removed"]["tile_matrix_levels_without_tiles"])))
report.setdefault("note", "the repairs are idempotent, so a rerun reports 0 removed / "
                          "0 added; gpkg_hygiene_before.json holds the state as found")
json.dump(report, open(OUT, "w"), indent=1)
removed = sum(len(v) for v in report["removed"].values())
added = sum(len(v) for v in report["added"].values())
print(f"registers repaired: {removed} removed, {added} added -> {OUT.name}")
for k, v in report["removed"].items():
    print(f"  removed {k}: {len(v)}")
for k, v in report["added"].items():
    print(f"  added   {k}: {len(v)}")
print(f"  after: {report['after']}")
