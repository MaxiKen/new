"""Fold the named-mineral layer into the shipped GeoPackage.

`Nigeria_Geology_Minerals_4326.gpkg` is written by build_combined.py /
build_geology_final.py, which know nothing about the mineral-glyph work.  This step
appends `minerals_named` (from minerals_named.gpkg) so the deliverable is one complete
file, and stamps the layer's provenance into metadata.json.

Run it after the build chain, before audit_layers.py:

    python build_combined.py
    python build_geology_final.py
    ...
    python add_named_minerals.py
    python audit_layers.py
"""
import json
import sqlite3

import geopandas as gpd
import pyogrio

GPKG = "Nigeria_Geology_Minerals_4326.gpkg"
LAYER = "minerals_named"
SRC = "minerals_named.gpkg"

METADATA = {
    "key": LAYER,
    "value": (
        "1,323 printed mineral symbols re-detected on the sheet at its native 75 dpi, "
        "each point the centroid of its glyph; named against the source extraction's "
        "appearance reference with 80.8% leave-one-out accuracy, per-row tier "
        "probable/tentative/unidentified. Positions are valid; per-mineral totals are "
        "not (Limestone 30 vs 136) - use mineral_symbols.mineral for counts and this "
        "layer for position. 144 symbols sit outside the border because the sheet maps "
        "the whole region; in_nigeria flags them. See mineral_audit.md and "
        "minerals_named.md"
    ),
}


def main():
    g = gpd.read_file(SRC, layer=LAYER)
    terr = gpd.read_file(GPKG, layer="national_territory").geometry.union_all().buffer(0)
    g["in_nigeria"] = g.within(terr)

    con = sqlite3.connect(GPKG)
    cur = con.cursor()
    cur.execute("DELETE FROM gpkg_geometry_columns WHERE table_name=?", (LAYER,))
    cur.execute("DELETE FROM gpkg_contents WHERE table_name=?", (LAYER,))
    cur.execute(f'DROP TABLE IF EXISTS "{LAYER}"')
    con.commit()
    con.close()

    g.to_file(GPKG, layer=LAYER, driver="GPKG", mode="a")
    print(f"{LAYER}: {len(g)} features, {int(g.in_nigeria.sum())} inside Nigeria")

    m = json.load(open("metadata.json"))
    m = [r for r in m if r["key"] != LAYER]
    m.insert(len(m) - 1, METADATA)
    json.dump(m, open("metadata.json", "w"), indent=1)
    print("metadata entries:", len(m))

    total = sum(pyogrio.read_info(GPKG, layer=n)["features"]
                for n, _ in pyogrio.list_layers(GPKG))
    print("gpkg:", len(pyogrio.list_layers(GPKG)), "layers,", total, "features")


if __name__ == "__main__":
    main()
