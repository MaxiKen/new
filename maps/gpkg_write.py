#!/usr/bin/env python3
"""Replace a layer inside a GeoPackage without depending on the writer's version.

`pyogrio.write_dataframe(..., append=False)` used to mean "overwrite the layer".
pyogrio 0.13 refuses instead ("Layer already exists, CreateLayer failed"), and
its `OVERWRITE=YES` layer option truncates the rows but leaves the table, so the
write then dies on `CREATE TABLE ... already exists`. A pipeline that silently
depends on the installed writer's semantics is a pipeline that breaks in a fresh
environment - this one did.

So the layer is dropped here, deliberately, with the GeoPackage's own registers
kept consistent - the rtree index virtual table (not its shadow tables), the
`gpkg_extensions` declaration, `gpkg_geometry_columns`, `gpkg_ogr_contents` and
`gpkg_contents` - and only then written. The layer's description is carried
across, because `audit_layers.py` fails on a layer with no description and a
repair that drops one would otherwise look like a documentation defect.

Nothing else in the file is touched: other layers, their attributes, the rasters
and the metadata records are the same bytes afterwards.
"""
import sqlite3

import pyogrio


def _drop_layer(path, layer):
    """Remove one layer and every register row that names it; return its description."""
    con = sqlite3.connect(path)
    has = con.execute("SELECT count(*) FROM sqlite_master WHERE type='table'"
                      " AND name=?", (layer,)).fetchone()[0]
    desc = None
    if has:
        row = con.execute("SELECT description FROM gpkg_contents WHERE table_name=?",
                          (layer,)).fetchone()
        desc = row[0] if row else None
        # the rtree index is a virtual table: drop it, not its shadow tables
        for (col,) in con.execute(
                "SELECT column_name FROM gpkg_extensions WHERE table_name=?"
                " AND extension_name='gpkg_rtree_index'", (layer,)).fetchall():
            con.execute(f'DROP TABLE IF EXISTS "rtree_{layer}_{col}"')
        for reg in ("gpkg_extensions", "gpkg_geometry_columns", "gpkg_ogr_contents",
                    "gpkg_contents"):
            con.execute(f'DELETE FROM "{reg}" WHERE table_name = ?', (layer,))
        con.execute(f'DROP TABLE IF EXISTS "{layer}"')
        con.commit()
    con.close()
    return desc


def write_layer(gdf, path, layer, spatial_index=True):
    """Write `gdf` as `layer` in `path`, replacing it and keeping its description."""
    desc = _drop_layer(path, layer)
    pyogrio.write_dataframe(gdf, path, layer=layer, driver="GPKG", append=False,
                            layer_options={"SPATIAL_INDEX": "YES" if spatial_index else "NO"})
    if desc:
        con = sqlite3.connect(path)
        con.execute("UPDATE gpkg_contents SET description = ? WHERE table_name = ?",
                    (desc, layer))
        con.commit()
        con.close()
    return layer
