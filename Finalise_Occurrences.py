#!/usr/bin/env python3
"""Final occurrence table: one row per printed symbol, with the best available name and an
explicit statement of where that name came from.

Two independent readings of each symbol are kept:
  mineral_code_reading - the commodity code printed inside the symbol, read from the native
                         artwork (the earlier pipeline; 81% correct in leave-one-out testing)
  legend_symbol        - the sheet's own legend symbol that best matches the printed glyph
They do not always agree. Sometimes they name the same commodity family (Clay vs Brick Clay,
Beryl vs Emerald); sometimes they genuinely conflict. Nothing is silently discarded: the row
carries both readings, the family verdict, a confidence and a conflict flag, so a later human
check is a column sort rather than rework.
"""
import json
from pathlib import Path
import pandas as pd, numpy as np

P = Path(__file__).resolve().parent
df = pd.read_csv(P / "Minerals_Occurrences_4326.csv")
df = df.rename(columns={"mineral": "mineral_code_reading",
                        "mineral_class": "class_from_code_reading",
                        "tier": "classifier_tier"})

# ---------------------------------------------------------------- commodity families
FAMILY = {
    "kaolin": "clay", "clay": "clay", "brick": "clay", "ball clay": "clay", "fire clay": "clay",
    "beryl": "beryl", "emerald": "beryl", "aquamarine": "beryl",
    "lepidolite": "lithium", "lithium": "lithium", "ambligonite": "lithium", "spodumene": "lithium",
    "columbite": "columbite-tantalite", "tantalite": "columbite-tantalite",
    "lead": "lead-zinc", "zinc": "lead-zinc", "galena": "lead-zinc",
    "pyrite": "sulphide", "marcasite": "sulphide", "pyroclore": "sulphide",
    "silica": "silica sand", "glass": "silica sand",
    "limestone": "carbonate", "marble": "carbonate", "calcite": "carbonate", "marl": "carbonate",
    "gypsum": "evaporite", "evaporite": "evaporite", "trona": "evaporite", "saltlake": "evaporite",
    "salt": "evaporite", "potash": "evaporite",
    "iron": "iron", "magnetite": "iron", "ilmenite": "iron",
    "quartz": "quartz", "rose quartz": "quartz",
    "granite": "granite", "pegmatite": "granite", "psammite": "psammite",
    "coal": "coal", "lignite": "coal", "tar sand": "bitumen", "bitumen": "bitumen",
    "oil": "oil and gas", "gas": "oil and gas",
    "gold": "gold", "silver": "silver", "copper": "copper", "tin": "tin",
    "wolframite": "tungsten", "baryte": "baryte", "feldspar": "feldspar", "mica": "mica",
    "talc": "talc", "garnet": "garnet", "topaz": "topaz", "tourmaline": "tourmaline",
    "kyanite": "kyanite", "sillimanite": "sillimanite", "chromite": "chromium",
    "manganese": "manganese", "uranium": "uranium", "zircon": "zircon", "bismuth": "bismuth",
    "molybdenite": "molybdenum", "nickel": "nickel", "diatomite": "diatomite",
    "dimension": "dimension stone", "phosphate": "phosphate", "bentonite": "bentonite",
    "brine": "brine", "asbestos": "asbestos", "graphite": "graphite", "monazite": "monazite",
    "magnesite": "magnesite", "sapphire": "corundum", "corundum": "corundum", "ruby": "corundum",
    "fluorite": "fluorite", "flourite": "fluorite", "river gravel": "gravel",
    "lithium -": "lithium",
}
def fam(name):
    n = str(name).lower()
    for k in sorted(FAMILY, key=len, reverse=True):
        if k in n:
            return FAMILY[k]
    return n.strip()

def key(s):
    return "".join(ch for ch in str(s).lower() if ch.isalpha())

df["family_from_code"] = df["mineral_code_reading"].map(fam)
df["family_from_legend"] = df["legend_symbol"].map(fam)
df["agreement"] = np.where(df.apply(lambda r: key(r["mineral_code_reading"]) == key(r["legend_symbol"]), axis=1),
                           "both readings identical", "readings differ")
df["family_agreement"] = np.where(df.family_from_code == df.family_from_legend,
                                  "same commodity family", "different family")

# ---------------------------------------------------------------- what we publish
def publish(r):
    if r["family_agreement"] == "same commodity family":
        return r["mineral_code_reading"]          # the code reading is the more specific one
    if r["name_confidence"] == "high":
        return r["legend_symbol"]
    return r["mineral_code_reading"]

df["mineral_published"] = df.apply(publish, axis=1)
df["alternative_name"] = df.apply(
    lambda r: (r["legend_symbol"] if key(r["mineral_published"]) == key(r["mineral_code_reading"])
               else r["mineral_code_reading"]), axis=1)
df["name_source"] = np.where(
    df.apply(lambda r: key(r["mineral_published"]) == key(r["mineral_code_reading"]), axis=1),
    "printed commodity code read from the artwork", "legend symbol match on the printed glyph")
df["confidence"] = np.select(
    [df["family_agreement"].eq("same commodity family") & df["name_confidence"].eq("high"),
     df["family_agreement"].eq("same commodity family"),
     df["name_confidence"].eq("high")],
    ["high", "medium", "low"], default="low")

# ---------------------------------------------------------------- commodity class
def cls(name):
    n = str(name).lower()
    if any(k in n for k in ("gold", "silver", "iron", "lead", "zinc", "copper", "tin", "columbite",
                            "tantalite", "wolframite", "chromite", "manganese", "galena", "pyrite",
                            "molybden", "nickel", "uranium", "zircon", "bismuth", "magnetite",
                            "monazite", "ilmenite", "tungsten")):
        return "metallic"
    if any(k in n for k in ("beryl", "aquamarine", "emerald", "garnet", "topaz", "tourmaline",
                            "sapphire", "ruby", "kyanite", "sillimanite", "talc", "mica", "quartz",
                            "corundum", "lithium", "lepidolite")):
        return "gemstone"
    if any(k in n for k in ("coal", "lignite", "tar sand", "bitumen", "oil", "gas")):
        return "energy"
    return "industrial"

df["commodity_class"] = df["mineral_published"].map(cls)

out = df.rename(columns={"mineral_published": "mineral"})
out = out[["lon", "lat", "mineral", "alternative_name", "name_source", "confidence",
           "agreement", "family_agreement", "commodity_class", "legend_symbol", "legend_score",
           "second_symbol", "margin", "mineral_code_reading", "class_from_code_reading",
           "classifier_tier", "n_source_points", "symbol_patch", "cx", "cy"]]
out.to_csv(P / "Minerals_Occurrences_4326.csv", index=False)

gj = {"type": "FeatureCollection",
      "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
      "features": [{"type": "Feature",
                    "properties": {k: (None if pd.isna(v) else v) for k, v in r.items()
                                   if k not in ("lon", "lat")},
                    "geometry": {"type": "Point", "coordinates": [float(r["lon"]), float(r["lat"])]}}
                   for _, r in out.iterrows()]}
json.dump(gj, open(P / "Minerals_Occurrences_4326.geojson", "w"))

rep = {"occurrences": int(len(out)),
       "distinct_mineral_names": int(out.mineral.nunique()),
       "both_readings_identical": int((out.agreement == "both readings identical").sum()),
       "same_commodity_family": int((out.family_agreement == "same commodity family").sum()),
       "different_family": int((out.family_agreement == "different family").sum()),
       "confidence": out.confidence.value_counts().to_dict(),
       "classes": out.commodity_class.value_counts().to_dict(),
       "symbols_merged_from_more_than_one_source_point": int((out.n_source_points > 1).sum())}
json.dump(rep, open(P / "Occurrence_Report.json", "w"), indent=2)
print(json.dumps(rep, indent=2))
print("\ntop names:\n", out.mineral.value_counts().head(12).to_string())
