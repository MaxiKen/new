"""Produce minerals_named.gpkg / .csv and the report on the 437 glyphs that the
committed mineral_symbols_detected.gpkg left unnamed."""
import json
import pickle
from collections import Counter

import geopandas as gpd
import numpy as np
import pyogrio
from shapely.geometry import Point

import name_glyphs as N

S = 75 / 72.0
X0, Y0 = 74.24, 358.72
LON_A, LON_B = 0.006345, 1.8335
LAT_A, LAT_B = -0.006345, 16.3218

# mineral -> (class, what it is / what it is used for)
DETAILS = {
    "Clay / Pottery Clay": ("industrial", "Brick, ceramic and pottery clay; cement and refractory raw material."),
    "Kaolin / kaolinitic clay": ("industrial", "China clay; paper coating, ceramics, paint filler, refractory."),
    "Gold": ("metallic", "Native gold; artisanal and industrial mining."),
    "Glass Sand": ("industrial", "Silica sand for glass, foundry sand, filtration, frac sand."),
    "Columbite": ("metallic", "Niobium-tantalum oxide; alloys, capacitors."),
    "Tantalite": ("metallic", "Tantalum ore; capacitors, superalloys, corrosion-resistant plant."),
    "Limestone": ("industrial", "Cement, lime, steel flux, aggregate."),
    "Brine": ("industrial", "Salt-bearing water; halite and industrial salt."),
    "Lead - Zinc": ("metallic", "Galena-sphalerite veins; Pb and Zn metal, batteries."),
    "Lepidolite": ("metallic", "Lithium mica; Li ore, pathfinder for tin-tantalum pegmatites."),
    "Beryl, Aquamarine, Emerald": ("gemstone", "Emerald and aquamarine gemstone plus beryllium ore."),
    "Lignite": ("energy", "Low-rank brown coal; fuel and lignite chemicals."),
    "Graphite": ("industrial", "Lubricant, refractories, batteries, pencils."),
    "Coal": ("energy", "Bituminous coal for power generation and metallurgy."),
    "Garnet": ("industrial", "Abrasive grit; semi-precious gemstone."),
    "Talc": ("industrial", "Cosmetics, ceramics, paint, paper."),
    "Tourmaline": ("gemstone", "Gemstone tourmaline in pegmatites."),
    "Chromite": ("metallic", "Chromium ore; stainless steel, refractories."),
    "Feldspar": ("industrial", "Flux in glass and ceramics; pottery body ingredient."),
    "Wolframite": ("metallic", "Tungsten ore; hard metals, cutting tools."),
    "Mica": ("industrial", "Sheet and ground mica; electrical and thermal insulation."),
    "Diatomite": ("industrial", "Diatomaceous earth; filtration, absorbents, insulation."),
    "Iron Ore (Magnetite, Ilmenite)": ("metallic", "Iron ore and titanium ore (ilmenite)."),
    "Kyanite": ("industrial", "High-alumina refractory mineral."),
    "Bentonite": ("industrial", "Swelling clay; drilling mud, foundry bonds."),
    "Marble": ("industrial", "Dimension stone and calcium carbonate filler."),
    "Magnesite": ("industrial", "Magnesium ore; refractories, magnesium compounds."),
    "Saltlake/ Potash": ("industrial", "Salt pans and brines; halite and potassium salts."),
    "Lithium (Ambligonite, Kunzite, Moganite, Spodumene, etc)": ("metallic", "Lithium pegmatite minerals; batteries."),
    "Baryte": ("industrial", "Barium sulphate; oil-well drilling mud weighting agent."),
    "Pyrite / Pyroclore": ("industrial", "Iron sulphide (sulphur/acid) and pyrochlore (Nb-Ta)."),
    "Bauxitic Clay": ("industrial", "Alumina and refractory raw material."),
    "Uranium": ("energy", "Uranium ore; nuclear fuel."),
    "Corundum, Sapphire & Ruby": ("gemstone", "Corundum: abrasive plus sapphire and ruby gemstone."),
    "Oil and Gas": ("energy", "Petroleum and natural gas."),
    "Flourite": ("industrial", "Fluorspar; metallurgical flux, HF and fluorine chemicals."),
    "Manganese": ("metallic", "Manganese ore; steel alloys, batteries."),
    "Copper minerals": ("metallic", "Copper oxide and sulphide minerals."),
    "Galena": ("metallic", "Lead sulphide ore, commonly with silver."),
    "Granite": ("industrial", "Dimension stone and crushed aggregate."),
    "Gypsum": ("industrial", "Plaster, wallboard, cement retarder."),
    "Phosphate": ("industrial", "Fertiliser phosphate."),
    "Phosphate Rock": ("industrial", "Fertiliser phosphate."),
    "Silica Sand": ("industrial", "Glass, foundry and frac sand."),
    "Sillimanite": ("industrial", "High-alumina refractory mineral."),
    "Silver": ("metallic", "Silver, commonly with lead-zinc ores."),
    "Trona": ("industrial", "Sodium carbonate; glass, detergents, chemicals."),
    "Tar Sand": ("energy", "Bitumen-impregnated sand; heavy oil."),
    "Topaz": ("gemstone", "Gemstone and abrasive."),
    "Zircon": ("industrial", "Zirconium silicate; ceramics, refractories, zirconia."),
    "Calcite": ("industrial", "Calcium carbonate; optical and filler uses."),
    "Bismuth": ("metallic", "Bismuth metal and compounds."),
    "Bitumen": ("energy", "Solid or viscous bitumen; road and industrial use."),
    "Brick Clay": ("industrial", "Clay for bricks and tiles."),
    "Ball Clay": ("industrial", "Plastic ceramic clay for whitewares and sanitaryware."),
    "Marcasite": ("industrial", "Iron sulphide; ornamental and sulphur source."),
    "Marl": ("industrial", "Lime-rich clay; cement raw material."),
    "Molybdenite": ("metallic", "Molybdenum ore; alloy steel."),
    "Monazite": ("metallic", "Rare-earth and thorium phosphate."),
    "Nickel": ("metallic", "Nickel ore; alloys and stainless steel."),
    "Psammite": ("industrial", "Metamorphosed sandstone; building and aggregate stone."),
    "River Gravel": ("industrial", "Sand and gravel aggregate."),
    "Asbestos / Serpentine": ("industrial", "Serpentine group; historically asbestos, now decorative stone."),
    "Evaporite": ("industrial", "Evaporite salts (gypsum, halite)."),
    "Fluorite": ("industrial", "Fluorspar."),
    "Dimension Stone": ("industrial", "Building and decorative stone."),
    "Bentonite ": ("industrial", "Drilling mud and foundry bonds."),
}


def main():
    canvas = np.load("/tmp/canvas75.npy")
    g, ref = N.run(canvas)
    acc = json.load(open("/tmp/acc.json"))
    fa = acc["family"]

    old = pyogrio.read_dataframe("mineral_symbols_detected.gpkg")
    prev = {(round(r.canvas_x, 2), round(r.canvas_y, 2)):
            (r.mineral if isinstance(r.mineral, str) else None)
            for r in old.itertuples()}

    rows = []
    for s in g:
        k = (round(s["x"], 2), round(s["y"], 2))
        was = prev.get(k)
        x_pt, y_pt = X0 + s["x"] / S, Y0 + s["y"] / S
        lon = LON_B + LON_A * x_pt
        lat = LAT_B + LAT_A * y_pt
        cls, desc = DETAILS.get(s["mineral"], ("", ""))
        rows.append(dict(canvas_x=k[0], canvas_y=k[1],
                         lon=round(lon, 6), lat=round(lat, 6),
                         colour_family=s["colour"], mineral=s["mineral"],
                         confidence=round(s["conf"], 2),
                         family_accuracy_pct=fa.get(s["colour"]),
                         mineral_class=cls, details=desc,
                         previously_named=bool(was), prior_name=was,
                         w_px=s["w"], h_px=s["h"]))
    gdf = gpd.GeoDataFrame(rows, geometry=[Point(r["lon"], r["lat"]) for r in rows],
                           crs="EPSG:4326")
    gdf.to_file("minerals_named.gpkg", layer="minerals_named", driver="GPKG")
    gdf.drop(columns="geometry").to_csv("minerals_named.csv", index=False)
    pickle.dump(dict(rows=rows, acc=acc), open("/tmp/report_data.pkl", "wb"))

    print("rows:", len(gdf), " previously named:", gdf.previously_named.sum(),
          " previously NULL:", (~gdf.previously_named).sum())
    new = gdf[~gdf.previously_named]
    print("\nTHE %d PREVIOUSLY UNNAMED, NOW NAMED:" % len(new))
    for m, n in Counter(new.mineral).most_common():
        sub = new[new.mineral == m]
        print(f"  {n:4d}  {m:44s} fam {sub.colour_family.iloc[0]:12s} "
              f"acc {sub.family_accuracy_pct.iloc[0]}%")
    print("\nconfidence:", Counter("high" if r >= .8 else "medium" if r >= .5 else "low"
                                   for r in new.confidence).most_common())
    print("\nagreement with the earlier names, where both named: %d/%d" % (
        (gdf[gdf.previously_named].mineral == gdf[gdf.previously_named].prior_name).sum(),
        gdf.previously_named.sum()))
    return gdf


if __name__ == "__main__":
    main()
