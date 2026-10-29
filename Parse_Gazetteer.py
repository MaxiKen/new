#!/usr/bin/env python3
"""Read the 2023 sheet's occurrence gazetteer: locality -> mineral codes.

The sheet prints an index number next to every symbol and, in the right-hand EXPLANATIONS
panel, lists for each number the locality and one or more mineral codes ("11. MARNONA Gy",
"87 Rjishi Hills Sn. W. Nb. Ta"). That table is the survey's own statement of which minerals
occur at which place, and several localities list three or four minerals.

The panel's index numbers restart in each gridded zone, but the LOCALITY names do not, so the
table is keyed by locality here and matched to the map by name.

Writes Gazetteer_Localities.json: {spaceless_key: {locality, codes[], numbers[]}}
"""
import json, re
from pathlib import Path
import pymupdf

P = Path(__file__).resolve().parent
page = pymupdf.open(P / "Mineral_Resources_Map_of_Nigeria_2023.pdf")[0]
raw = page.get_text("rawdict")

# ---- lines in the explanation panel
lines = []
for b in raw["blocks"]:
    for l in b.get("lines", []):
        cs = [c for s in l["spans"] for c in s["chars"]]
        if not cs:
            continue
        x0 = min(c["bbox"][0] for c in cs); y0 = min(c["bbox"][1] for c in cs)
        if x0 > 2270 and 330 < y0 < 1900:
            txt = re.sub(r"\s+", " ", "".join(c["c"] for c in cs)).strip()
            if txt:
                lines.append({"x": x0, "y": y0, "t": txt})
# drop the copyright/credits paragraph at the bottom right
lines = [l for l in lines if not (l["x"] > 3400 and l["y"] > 1900)]
print("panel lines:", len(lines))

# ---- mineral codes, as printed. Element symbols are unambiguous; the rest are the legend's
#      own abbreviations, expanded where the legend gives them explicitly.
CODE = {
 # elements
 "Au":"Gold","Ag":"Silver","Cu":"Copper","Pb":"Lead","Zn":"Zinc","Sn":"Tin","W":"Wolframite (tungsten)",
 "Nb":"Niobium (columbite)","Ta":"Tantalite","Fe":"Iron","Mn":"Manganese","U":"Uranium","Zr":"Zircon",
 "Ni":"Nickel","Mo":"Molybdenite","Cr":"Chromite","Al":"Aluminium ore (bauxite)","Bi":"Bismuth",
 "Hg":"Mercury","Sb":"Antimony","Li":"Lithium","Be":"Beryl","V":"Vanadium","Co":"Cobalt","Ti":"Titanium (ilmenite)",
 # the legend's own abbreviations
 "Gy":"Gypsum","Ls":"Limestone","Cl":"Clay / pottery clay","Cy":"Clay","Ka":"Kaolin","K":"Kaolin",
 "Bn":"Bentonite","Br":"Brine","Ba":"Baryte","Gr":"Granite","Gran":"Granite","Ky":"Kyanite","Gm":"Granite / migmatite",
 "Tm":"Tourmaline","Tpz":"Topaz","Tr":"Trona","Ts":"Tar sand","Ta_":"Tantalite","Sl":"Sillimanite","Ss":"Silica sand",
 "Tc":"Talc","R":"Rose quartz","Py":"Pyrite","Mo_":"Molybdenite","Ni_":"Nickel","Mi":"Marl","Mc":"Marcasite",
 "M":"Mica","Sd":"Sand","Qa":"Quartz","Qz":"Quartz","Gs":"Glass sand","Gvl":"River gravel","Ru":"Ruby",
 "D":"Diatomite","Ds":"Dimension stone","E":"Evaporite","F":"Feldspar","Fp":"Feldspar","P":"Phosphate",
 "Lg":"Lignite","Mb":"Marble","S":"Salt","Si":"Silica sand","Sr":"Salt / potash","Na":"Salt / potash",
 "Aq":"Aquamarine","Pt":"Platinum","Bx":"Bauxite","Fr":"Feldspar","Bcl":"Ball clay","T":"Talc",
 "Us":"Unspecified","U_":"Uranium","Oil":"Oil and gas","Gas":"Gas","C":"Coal","Co_":"Coal","Ca":"Calcite",
 "Dm":"Diamond","Dia":"Diamond","Fl":"Fluorite","Fc":"Fluorite","Ag_":"Silver","Am":"Amphibolite",
 "Ar":"Asbestos","As":"Asbestos","ab":"Asbestos","At":"Asbestos","Bit":"Bitumen","Cor":"Corundum",
 "Sap":"Sapphire","Gt":"Garnet","Ga":"Garnet","Il":"Ilmenite","Mag":"Magnetite","Mt":"Magnetite",
}
def expand(code):
    if code in CODE: return CODE[code]
    base = code.rstrip(".")
    if base in CODE: return CODE[base]
    cap = base[:1].upper() + base[1:].lower()
    if cap in CODE: return CODE[cap]
    return None

# a code token: 1-3 letters, optional trailing dot, capitalised like the sheet prints them
TOKEN = re.compile(r"^[A-Z][a-z]{0,2}\.?$|^[A-Z]{1,3}\.?$")

def split_codes(rest):
    """Locality then codes. Codes are the trailing short tokens; the sheet separates them
    with dots or spaces, e.g. 'Sn. Nb. Ta' or 'Cu Pb. Zn'."""
    toks = rest.split()
    codes, i = [], len(toks)
    while i > 0:
        t = toks[i-1]
        if TOKEN.match(t) and len(t) <= 4:
            codes.append(t.rstrip(".")); i -= 1
        else:
            break
    loc = " ".join(toks[:i]).strip()
    return loc, codes

def key(s):
    return re.sub(r"[^a-z]", "", s.lower())

gaz = {}
n_num = 0
for l in lines:
    m = re.match(r"^(\d{1,3})\s*[.,]?\s+(.+)$", l["t"])
    if not m:
        continue
    num, rest = int(m.group(1)), m.group(2)
    loc, codes = split_codes(rest)
    # repair the sheet's broken kerning: "K wadoma" -> "Kwadoma", "S ok oto" -> "Sokoto"
    loc = re.sub(r"\b([A-Z])\s+([a-z])", r"\1\2", loc)
    loc = re.sub(r"\b([a-z]{1,2})\s+([a-z]{2,})", r"\1\2", loc)
    if not loc or not codes:
        continue
    k = key(loc)
    if len(k) < 3:
        continue
    n_num += 1
    e = gaz.setdefault(k, {"locality": loc, "codes": [], "numbers": []})
    for c in codes:
        if c not in e["codes"]:
            e["codes"].append(c)
    e["numbers"].append(num)

print("numbered entries parsed:", n_num)
print("distinct localities:", len(gaz))
multi = sum(1 for v in gaz.values() if len(v["codes"]) > 1)
print("localities with more than one mineral:", multi)
import collections
cc = collections.Counter(c for v in gaz.values() for c in v["codes"])
print("code vocabulary:", len(cc))
print("top codes:", cc.most_common(20))
unk = [c for c in cc if expand(c) is None]
print("codes not expanded:", sorted(unk)[:40], "count", len(unk))
out = {k: {"locality": v["locality"], "codes": v["codes"], "numbers": v["numbers"],
           "minerals": [expand(c) or c for c in v["codes"]]} for k, v in gaz.items()}
json.dump(out, open(P / "Gazetteer_Localities.json", "w"), indent=1)
print("written Gazetteer_Localities.json")
for k in list(gaz)[:6]:
    print("  ", gaz[k]["locality"], gaz[k]["codes"])
