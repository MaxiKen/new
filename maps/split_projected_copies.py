#!/usr/bin/env python3
"""One CRS for the deliverable: move the measurement copies to their own file.

`Nigeria_Geology_Minerals_4326.gpkg` held 31 vector layers in three CRS: 26 in
EPSG:4326, three in EPSG:32632 and two in EPSG:6933. The five projected ones exist
only so that area and length can be measured in metres - in degrees you get square
degrees, and EPSG:3857 is 3.68 % wrong over Nigeria - and **each one has a 4326
twin in the same file holding identical attributes under the same key**.

Laying them together is the common case, and mixing CRS for that is a nuisance and
a source of silent error (a 6933 layer drawn on a 4326 canvas lands in the wrong
hemisphere). So the five copies move, unchanged, into

    Nigeria_Geology_Minerals_projected_copies.gpkg

leaving the deliverable with **26 vector layers and 9 raster layers, every one in
EPSG:4326** - which is also the only CRS the tiled rasters can carry.

Nothing is deleted: every copy is written to the new file first, read back, and
compared with its parent (all attributes, and the geometry after reprojection)
before it is removed from the main file. The comparison is strict enough to catch
a copy taken before a repair, which is the way this pair went wrong once. The
removal also clears the copy's own register rows (rtree index and its shadow
tables, `gpkg_extensions`, `gpkg_geometry_columns`, `gpkg_contents`,
`gpkg_ogr_contents`, and any `gpkg_metadata_reference` naming it).

Idempotent: a second run finds the five already gone and the five already in the
sibling file and changes nothing. Everything it did is recorded in
`projected_copies.json`.

Run:  python split_projected_copies.py
"""
import json
import pathlib
import sqlite3

import geopandas as gpd
import numpy as np
import pyogrio

from gpkg_write import write_layer

HERE = pathlib.Path(__file__).parent
MAIN = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
COPIES = HERE / "Nigeria_Geology_Minerals_projected_copies.gpkg"
OUT = HERE / "projected_copies.json"

# copy layer -> the 4326 layer it is a reprojection of. The last entry is the one
# that went wrong once: the UTM copy descends from _refined, not from the layer
# whose name it echoes.
PAIRS = {
    "geology_units_utm32n": "geology_units",
    "geology_units_equal_area": "geology_units",
    "mineral_localities_icons_utm32n": "mineral_localities_icons",
    "mineral_localities_equal_area": "mineral_localities_icons",
    "mineral_localities_utm32n": "mineral_localities_refined",
}


def layers_in(path):
    return [n for n, _ in pyogrio.list_layers(path)] if path.exists() else []


def key_of(g):
    for k in ("locality_id", "code"):
        if k in g.columns:
            return k
    raise SystemExit(f"no key column in {list(g.columns)}")


def compare(copy_path, copy_name, main_path, parent_name):
    """Every attribute equal, and the geometry equal to the parent reprojected."""
    c = gpd.read_file(copy_path, layer=copy_name)
    p = gpd.read_file(main_path, layer=parent_name)
    k = key_of(c)
    if len(c) != len(p) or set(c[k]) != set(p[k]):
        return dict(ok=False, reason=f"{len(c)} rows against {len(p)} in {parent_name}")
    c = c.sort_values(k).reset_index(drop=True)
    p = p.sort_values(k).reset_index(drop=True)
    shared = [x for x in c.columns if x in p.columns and x != "geometry"]
    differing = [x for x in shared if not c[x].equals(p[x])]
    # the copy's own geometry vs the parent's, reprojected into the copy's CRS
    expect = gpd.GeoSeries(p.geometry, crs=p.crs).to_crs(c.crs)
    d = np.array([a.distance(b) if c.crs.is_geographic else a.hausdorff_distance(b)
                  for a, b in zip(expect, c.geometry)])
    return dict(ok=not differing and float(d.max()) < 1e-6,
                rows=len(c), key=k, attributes_compared=len(shared),
                attributes_differing=differing,
                max_geometry_offset=float(d.max()),
                crs=c.crs.to_string(), parent=parent_name)


main_layers = layers_in(MAIN)
pending = [n for n in PAIRS if n in main_layers]
already = [n for n in PAIRS if n not in main_layers]
print(f"main file: {len(main_layers)} layers; {len(pending)} copy(ies) still in it")

# ---- 1. write the copies out, unless they are already there and correct -------
if pending:
    existing = layers_in(COPIES)
    if not set(pending) <= set(existing):
        # build the sibling file from scratch: the five layers, their descriptions,
        # and nothing else. Writing them one at a time keeps the layer names.
        if COPIES.exists():
            COPIES.unlink()
        con = sqlite3.connect(MAIN)
        desc = {t: d for t, d in con.execute(
            "SELECT table_name, description FROM gpkg_contents")}
        con.close()
        for name in PAIRS:
            g = gpd.read_file(MAIN, layer=name)
            pyogrio.write_dataframe(g, COPIES, layer=name, driver="GPKG",
                                    layer_options={"SPATIAL_INDEX": "YES"})
            print(f"  wrote {name:32s} {len(g):5d} rows  {g.crs.to_string()}")
        con = sqlite3.connect(COPIES)
        for name in PAIRS:
            con.execute("UPDATE gpkg_contents SET description = ? WHERE table_name = ?",
                        (desc.get(name), name))
        con.commit()
        con.close()

    # ---- 2. prove, from the file, that each copy is its parent reprojected ---
    verdicts = {}
    for name, parent in PAIRS.items():
        v = compare(COPIES, name, MAIN, parent)
        verdicts[name] = v
        print(f"  verify {name:32s} ok={v['ok']}  {v.get('rows', '')} rows, "
              f"{v.get('attributes_compared', '')} attributes, "
              f"max offset {v.get('max_geometry_offset', float('nan')):.2e}")
        if not v["ok"]:
            raise SystemExit(f"refusing to remove {name} from the main file: {v}")
else:
    verdicts = {}
    print("  all five copies are already in the sibling file")

# ---- 3. remove them from the main file, registers included -------------------
dropped = []
if pending:
    con = sqlite3.connect(MAIN)
    for name in pending:
        # drop the rtree *virtual* table, not its shadow tables: DROP on a shadow
        # (`..._node`) is refused by the rtree module, and the shadows go with the
        # virtual table. The index name comes from the register, not from a guess.
        rtree_tables = [f"rtree_{t}_{c}" for t, c in con.execute(
            "SELECT table_name, column_name FROM gpkg_extensions"
            " WHERE extension_name = 'gpkg_rtree_index' AND table_name = ?", (name,))]
        for t in rtree_tables:
            con.execute(f'DROP TABLE IF EXISTS "{t}"')
        for reg in ("gpkg_extensions", "gpkg_geometry_columns", "gpkg_ogr_contents",
                    "gpkg_contents"):
            con.execute(f'DELETE FROM "{reg}" WHERE table_name = ?', (name,))
        con.execute("DELETE FROM gpkg_metadata_reference WHERE table_name = ?", (name,))
        con.execute(f'DROP TABLE "{name}"')
        dropped.append(dict(layer=name, rtree_tables_removed=len(rtree_tables)))
    con.commit()
    con.execute("VACUUM")
    con.close()
    print(f"  removed from the main file: {', '.join(pending)}")

# ---- 4. what the two files hold now ------------------------------------------
con = sqlite3.connect(MAIN)
main_now = con.execute(
    "SELECT table_name, data_type, srs_id FROM gpkg_contents ORDER BY data_type, table_name"
).fetchall()
integrity_main = con.execute("PRAGMA integrity_check").fetchone()[0]
con.close()
con = sqlite3.connect(COPIES)
copies_now = con.execute(
    "SELECT table_name, srs_id FROM gpkg_contents ORDER BY table_name").fetchall()
integrity_copies = con.execute("PRAGMA integrity_check").fetchone()[0]
con.close()

non_4326 = [t for t, d, s in main_now if d == "features" and s != 4326]
assert not non_4326, f"the main file still holds {non_4326}"
assert integrity_main == "ok" and integrity_copies == "ok"

report = dict(
    main_file=MAIN.name,
    copies_file=COPIES.name,
    why="the deliverable must be one CRS so layers can be laid on each other; the "
        "five reprojections exist only for measuring, and each has a 4326 twin in "
        "the main file holding identical attributes under the same key",
    moved=[dict(layer=n, parent=PAIRS[n], **{k: v for k, v in verdicts.get(n, {}).items()
                                             if k in ("rows", "crs", "max_geometry_offset",
                                                      "attributes_compared")})
           for n in PAIRS],
    removed_this_run=dropped,
    main_layers=dict(total=len(main_now),
                     features=sum(1 for t, d, s in main_now if d == "features")),
    main_srs=sorted({s for t, d, s in main_now}),
    copies_srs=sorted({s for t, s in copies_now}),
    integrity=dict(main=integrity_main, copies=integrity_copies),
    note="nothing was deleted: every copy was written, read back and compared with "
         "its parent before it left the main file; a second run is a no-op",
)
json.dump(report, open(OUT, "w"), indent=1)

n_feat = sum(gpd.read_file(MAIN, layer=t, rows=1).shape[0] or 0 for t, d, s in main_now
             if d == "features")
print(f"\nmain: {len([1 for t, d, s in main_now if d == 'features'])} vector + "
      f"{len([1 for t, d, s in main_now if d == 'tiles'])} raster layers, "
      f"CRS {sorted({s for t, d, s in main_now})}, integrity {integrity_main}")
print(f"copies: {len(copies_now)} layers, CRS {sorted({s for t, s in copies_now})}, "
      f"integrity {integrity_copies} -> {OUT.name}")
