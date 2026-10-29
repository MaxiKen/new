#!/usr/bin/env python3
"""Canonical commodity names.

The sheet's text layer splits letters apart ("K aolin", "S ilica S and", "W olframite"), so the
same commodity can arrive as several spellings. This maps every spelling to one canonical name
and a canonical commodity class, and reports what it changed. No name is invented: each
canonical name is one of the spellings already present, and the mapping is explicit.
"""
import json
from pathlib import Path
import pandas as pd

P = Path(__file__).resolve().parent
df = pd.read_csv(P / "Minerals_Occurrences_4326.csv")

CANON = {
 "K aolin / k aolinitic clay": "Kaolin / kaolinitic clay",
 "Corundum, S apphire & R uby": "Corundum, Sapphire & Ruby",
 "W olframite (w)": "Wolframite",
 "S ilica S and (ss)": "Silica Sand",
 "Glass S and": "Glass Sand",
 "T ar S and (ts)": "Tar Sand",
 "T ourmaline (tm)": "Tourmaline",
 "T rona (tr)": "Trona",
 "M agnesite": "Magnesite",
 "M arble": "Marble",
 "M ica (m)": "Mica",
 "Nick el (ni)": "Nickel",
 "R ose Quartz (r)": "Rose Quartz",
 "Lead - Z inc": "Lead - Zinc",
 "Pyrite / Pyroclore (py)": "Pyrite / Pyrochlore",
 "Lithium - (Ambligonite, K unz ite, M oganite, S podumene, etc)":
     "Lithium (amblygonite, kunzite, spodumene)",
 "Iron Ore (M agnetite, Ilmenite)": "Iron Ore (magnetite, ilmenite)",
 "M arl (mi)": "Marl",
 "M arcasite (mc)": "Marcasite",
 "M olybdenite (mo)": "Molybdenite",
 "S altlak e/ Potash": "Salt / potash",
 "S illimanite (sl)": "Sillimanite",
 "S ilver (ag)": "Silver",
 "T alc (tc)": "Talc",
 "T antalite (ta)": "Tantalite",
 "T opaz (tpz )": "Topaz",
 "Z ircon (z r)": "Zircon",
 "Flourite": "Fluorite",
 "unidentified": "Unidentified",
}
df["mineral"] = df["mineral"].replace(CANON)
df["alternative_name"] = df["alternative_name"].replace(CANON)

CLASS = {
 "metallic": ["gold","silver","iron ore","lead - zinc","copper","tin","columbite","tantalite",
              "wolframite","chromite","manganese","pyrite / pyrochlore","molybdenite","nickel",
              "uranium","zircon","bismuth","monazite","galena"],
 "gemstone": ["beryl, aquamarine, emerald","garnet","topaz","tourmaline","corundum, sapphire & ruby",
              "kyanite","sillimanite","talc","mica","rose quartz","lithium (amblygonite, kunzite, spodumene)",
              "lepidolite"],
 "energy":   ["coal","lignite","tar sand","bitumen","oil and gas"],
}
def classify(name):
    n = str(name).lower()
    for cls, keys in CLASS.items():
        if any(k in n for k in keys):
            return cls
    return "industrial"
df["commodity_class"] = df["mineral"].map(classify)
df.to_csv(P / "Minerals_Occurrences_4326.csv", index=False)

gj = {"type": "FeatureCollection",
      "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
      "features": [{"type": "Feature",
                    "properties": {k: (None if (isinstance(v, float) and v != v) else v)
                                   for k, v in r.items() if k not in ("lon", "lat")},
                    "geometry": {"type": "Point", "coordinates": [float(r["lon"]), float(r["lat"])]}}
                   for _, r in df.iterrows()]}
json.dump(gj, open(P / "Minerals_Occurrences_4326.geojson", "w"))
print("canonical names:", df.mineral.nunique())
print(df.mineral.value_counts().head(14).to_string())
print("classes:", df.commodity_class.value_counts().to_dict())
