"""Rebuild the mineral-symbol point layer from glyphs detected on the sheet.

The point of each feature is the centre of the printed symbol, measured on the map
raster at its native 75 dpi and projected with the transform fitted to the printed
graticule:

    lon = 0.006345 * x_pt + 1.8335
    lat = -0.006345 * y_pt + 16.3218

(x_pt, y_pt are PDF points, origin top-left of the page.)
"""
import json
import pickle

import numpy as np
import pyogrio

import find_sites as F

S = 75 / 72.0
X0, Y0 = 74.24, 358.72
LON_A, LON_B = 0.006345, 1.8335
LAT_A, LAT_B = -0.006345, 16.3218

# cluster -> legend mineral, read off the exemplar contact sheets against the
# sheet's EXPLANATIONS panel.  Only clusters examined and identified are listed;
# everything else stays "unidentified" rather than being guessed.
CLUSTER_MINERAL = {
    0: "Gold", 1: "Uranium", 3: "Fire Clay", 7: "Molybdenite",
    8: "Columbite", 9: "Kaolin / kaolinitic clay", 10: "Iron Ore (Magnetite, Ilmenite)",
    13: "Tourmaline", 16: "Clay / Pottery Clay", 22: "Gold", 25: "Baryte",
    27: "Gold", 32: "Brine", 33: "Mica (m)", 34: "Tantalite", 38: "Lepidolite",
    39: "Kaolin / kaolinitic clay", 41: "Iron Ore (Magnetite, Ilmenite)",
    43: "Coal", 45: "Clay / Pottery Clay", 46: "Kaolin / kaolinitic clay",
    47: "Gold", 51: "Baryte", 53: "Lepidolite", 55: "Lead - Zinc",
}


def to_page(x, y):
    return X0 + x / S, Y0 + y / S


def to_lonlat(x_pt, y_pt):
    return LON_B + LON_A * x_pt, LAT_B + LAT_A * y_pt


def build():
    canvas = np.load("/tmp/canvas75.npy")
    sites = F.detect(canvas)
    D = pickle.load(open("/tmp/clust2.pkl", "rb"))
    ctr = D["ctr"].reshape(-1, 16, 20, 3).astype(np.float32)
    lbl = D["lbl"]

    rows = []
    for s in sites:
        x, y = s["x"], s["y"]
        xi, yi = int(round(x)), int(round(y))
        k, dist = -1, 1e9
        if 8 <= yi < 1669 and 10 <= xi < 2050:
            patch = canvas[yi - 8:yi + 8, xi - 10:xi + 10].astype(np.float32)
            d = np.abs(ctr - patch).mean(axis=(1, 2, 3))
            k = int(d.argmin())
            dist = float(d[k])
        x_pt, y_pt = to_page(x, y)
        lon, lat = to_lonlat(x_pt, y_pt)
        rows.append(dict(canvas_x=round(x, 2), canvas_y=round(y, 2),
                         x_pt=round(x_pt, 3), y_pt=round(y_pt, 3),
                         lon=round(lon, 6), lat=round(lat, 6),
                         glyph_class=k, class_dist=round(dist, 2),
                         mineral=CLUSTER_MINERAL.get(k, ""),
                         parts=s["n"], kind=s["kind"]))
    return rows


def write(rows, path="/home/user/new/maps/mineral_symbols_detected.gpkg"):
    import geopandas as gpd
    from shapely.geometry import Point
    gdf = gpd.GeoDataFrame(rows, geometry=[Point(r["lon"], r["lat"]) for r in rows],
                           crs="EPSG:4326")
    gdf["mineral"] = gdf["mineral"].replace("", None)
    gdf.to_file(path, layer="mineral_symbols_detected", driver="GPKG")
    return gdf


if __name__ == "__main__":
    rows = build()
    print("symbols:", len(rows))
    gdf = write(rows)
    named = gdf[gdf.mineral.notna()]
    print("named:", len(named), f"({100*len(named)/len(gdf):.1f}%)")
    print(named.mineral.value_counts().to_string())
    with open("/tmp/symbols_summary.json", "w") as f:
        json.dump(dict(total=len(rows), named=int(len(named)),
                       per_mineral=named.mineral.value_counts().to_dict()),
                  f, indent=1)
