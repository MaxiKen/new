#!/usr/bin/env python3
"""Unit code -> name and period, exactly as printed in the 2011 sheet's legend.

Extracted from the legend text once and kept here so every script (and the README) uses the
same wording.
"""

LEGEND = {
 "Al": ("Alluvium", "Recent"),
 "MWS": ("Meander belt, back swamps, fresh water swamps", "Recent"),
 "AB": ("Abandoned beach ridges", "Recent"),
 "MS": ("Mangrove swamps", "Recent"),
 "SDsm": ("Sombreiro-Warri deltaic formation, sand clay and swamp", "Recent"),
 "Cst": ("Chad Formation, sands clays siltstones and limestones", "Neogene"),
 "Bnst": ("Benin Formation, sands and clay", "Neogene"),
 "bb": ("Younger basalt", "Tertiary to Recent volcanics"),
 "bb2": ("Older basalt", "Tertiary to Recent volcanics"),
 "OAlgs": ("Ogwashi-Asaba Formation, lignite claystone and shale", "Palaeogene"),
 "Issh": ("Ilaro Formation, clayey sands and shale", "Palaeogene"),
 "Gwss": ("Gwandu Formation, sandstone and clay", "Palaeogene"),
 "Ast": ("Ameki Group", "Palaeogene"),
 "Esh": ("Ewekoro Formation, shale and limestone", "Palaeogene"),
 "Imsh": ("Imo Group, sandstone shale and clay", "Palaeogene"),
 "Kss": ("Kerri-Kerri Formation", "Cretaceous-Palaeogene"),
 "Dsh": ("Dange Formation, shale", "Palaeocene"),
 "Kls": ("Kalambaina Formation, limestone", "Palaeocene"),
 "Gss": ("Gombe Formation, sandstone siltstone shale and ironstone", "Cretaceous"),
 "Ajst": ("Ajali Formation, false-bedded sandstone", "Cretaceous"),
 "Mcs": ("Nsukka Formation, coal shale and sandstone", "Cretaceous"),
 "Asl": ("Abeokuta Formation, sandstone and limestone", "Cretaceous"),
 "Mcst": ("Mamu Formation, coal sandstone and shale", "Cretaceous"),
 "Nsh": ("Nkporo Formation, shale and mudstone", "Cretaceous"),
 "Bssf": ("Bassange Formation", "Cretaceous"),
 "Awst": ("Awgu Formation, shale and limestone", "Cretaceous"),
 "Psh": ("Pindiga Formation, sandstone siltstone and shale", "Cretaceous"),
 "Lass": ("Lafia Formation", "Cretaceous"),
 "NPst": ("Nupe Formation", "Cretaceous"),
 "Tst": ("Taloka Formation", "Cretaceous"),
 "Ess": ("Ezeaku Group", "Cretaceous"),
 "Eshl": ("Ezeaku Group, shale limestone and sandstone", "Cretaceous"),
 "Arlsh": ("Asu River Group, shale and limestone with sandstone", "Cretaceous"),
 "Ylsh": ("Yola Formation", "Cretaceous"),
 "Bst": ("Bima Formation, feldspathic sandstone", "Cretaceous"),
 "Fsh": ("Fika Formation, black shale siltstone and sandstone", "Cretaceous"),
 "Mlst": ("Limestone and siltstone", "Cretaceous"),
 "Yls": ("Yolde Formation, sandstone", "Cretaceous"),
 "Awst2": ("Awi-Mfamosing Formation", "Cretaceous"),
 "MyP": ("Quartz porphyry", "Jurassic"),
 "MyG": ("Granite and granite porphyry", "Jurassic"),
 "Mys": ("Syenite, quartz-syenite and gabbro", "Jurassic"),
 "MGp": ("Granites and granite porphyry", "Jurassic"),
 "r": ("Rhyolite", "Jurassic"),
 "Jyr": ("Rhyolite", "Jurassic"),
 "JyG": ("Biotite granite", "Jurassic"),
 "JyA": ("Trachy-andesite", "Jurassic"),
 "P": ("Pegmatite", "Pan-African"),
 "D": ("Dolerite", "Pan-African"),
 "ODh": ("Bauchite quartz-diorite", "Pan-African"),
 "OGd": ("Biotite and biotite-hornblende granodiorite", "Pan-African"),
 "OGS": ("Syenite, mainly pyroxene diorite composition", "Pan-African"),
 "OSq": ("Coarse biotite and biotite-muscovite granite", "Pan-African"),
 "OGh": ("Coarse hornblende granite", "Pan-African"),
 "OGf": ("Fine-grained biotite granite", "Pan-African"),
 "OGm": ("Medium to coarse biotite granite", "Pan-African"),
 "OGu": ("Undifferentiated granite, migmatite and granite gneiss", "Pan-African"),
 "OGCh": ("Charnockitic rocks", "Pan-African"),
 "OGr": ("Gabbro and quartz gabbro", "Pan-African"),
 "MV": ("Meta-volcanic / meta-sedimentary series", "Precambrian"),
 "Sa": ("Amphibole schist, amphibolite", "Precambrian"),
 "BIF": ("Banded iron formation", "Precambrian"),
 "Sp": ("Slate, phyllite and meta-siltstone", "Precambrian"),
 "m": ("Marble", "Precambrian"),
 "Sf": ("Fine-grained flaggy quartzite and quartz schist", "Precambrian"),
 "Qs": ("Quartzite, massive and schistose", "Precambrian"),
 "MSch": ("Pelitic schist / muscovite schist", "Precambrian"),
 "Su": ("Undifferentiated schists including phyllites", "Precambrian"),
 "Mc": ("Meta-conglomerate", "Precambrian"),
 "bS": ("Biotite garnet gneiss schist", "Precambrian"),
 "bG": ("Banded gneiss / biotite gneiss", "Precambrian"),
 "OPg": ("Porphyroblastic gneiss", "Precambrian"),
 "GG": ("Granite gneiss complex", "Precambrian"),
 "Ge": ("Granulite and gneiss", "Precambrian"),
 "MaG": ("Migmatitic augen gneiss", "Precambrian"),
 "MG": ("Migmatite", "Precambrian"),
 "qs": ("Silicified, sheared rocks, large quartz veins", "Precambrian"),
 "My": ("Mylonites", "Precambrian"),
 "aMy": ("Mylonites interlayered with amphibolites", "Precambrian"),
}

# Corrections and additions read directly from the sheet's legend image. The code letters on this
# sheet are kerned and a few are printed in two places, so these were transcribed by eye from the
# legend rather than by text search.
FIXED = {
    "MG": ("Migmatitic gneiss", "Precambrian"),
    "MS": ("Pelitic schist / muscovite schist", "Precambrian"),
}
EXTRA = {
    "M": ("Migmatite", "Precambrian"),
    "Myl": ("Ignimbrite", "Jurassic"),
    "b": ("Younger basalt (Newer Basalt)", "Tertiary to Recent volcanics"),
    "bG-h": ("Biotite hornblende gneiss", "Precambrian"),
    "Glcl": ("Sandstones and clays, Gwandu Formation", "Palaeogene"),
    "Wss": ("Sandstone, clays and shale, Dukamaje and Wurno Formation", "Cretaceous"),
    "Wcs": ("Clays and loose sandstone, Dukamaje and Wurno Formation", "Cretaceous"),
    "Wsh": ("Shale with phosphate nodules, Rima Group", "Cretaceous"),
    "Ts": ("Siltstone and sandstone, Rima Group", "Cretaceous"),
    "Ncsh": ("Coal, shale and sandstone, Nsukka Formation", "Cretaceous"),
    "ANsh": ("Shale and limestone, Awgu Formation", "Cretaceous"),
    "GIls": ("Limestone, Dukamaje Formation", "Cretaceous"),
    "GIpg": ("Pebbles and grit, Gundumi-Illo Formation", "Cretaceous"),
    "GIss": ("Clay grit and pebbles, Gundumi-Illo Formation", "Cretaceous"),
    "GIgss": ("Gravel and sand, Gundumi-Illo Formation", "Cretaceous"),
    "Bss": ("Feldspathic sandstone, calcareous sandstone and shelly limestone, Bima Formation", "Cretaceous"),
    "NPss": ("Feldspathic sandstone and siltstone, Nupe Formation", "Cretaceous"),
}

UNIT = {**LEGEND, **EXTRA, **FIXED}


def unit_name(code):
    """Name and age for a printed code; never guesses beyond what the legend says."""
    return UNIT.get(code, ("Not named in the legend", "unknown"))


PERIOD_ORDER = ["Recent", "Neogene", "Tertiary to Recent volcanics", "Palaeogene",
                "Cretaceous-Palaeogene", "Palaeocene", "Cretaceous", "Jurassic",
                "Precambrian"]
