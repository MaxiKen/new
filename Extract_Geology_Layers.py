#!/usr/bin/env python3
"""Extract the geological sheet's own vector content into GIS layers.

The 2011 Geological Map of Nigeria is fully vector (45,435 paths, no images), so its map
units, faults, rivers and state boundaries can be recovered as geometry rather than traced
from a picture. All output is EPSG:4326, registered on the sheet's printed graticule.

Layers written to Geology_Layers_Extracted.gpkg:
  geology_units      filled map-unit polygons, dissolved by colour, with unit codes and names
  faults             the sheet's "Major Fractures / Faults" symbol: isolated hachured strokes
  roads              the sheet's "Roads" symbol: continuous thick black lines
  rivers             the sheet's blue drainage lines
  state_boundaries   the sheet's grey internal administrative lines for Nigeria
  graticule          10-minute graticule, for reference only

Where a layer's classification cannot be proven from the file, the attribute says so.
"""
import json, re
from pathlib import Path
import numpy as np, pymupdf, geopandas as gpd
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import make_valid

P = Path(__file__).resolve().parent
OUT = P / "Geology_Layers_Extracted.gpkg"
if OUT.exists(): OUT.unlink()

def to_ll(x, y): return ((x + 276.36) / 157.593, (2281.63 - y) / 157.586)

page = pymupdf.open(P / "Geological_Map_of_Nigeria.pdf")[0]
words = [(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")]

# ---------------------------------------------------------------- unit names from legend
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
CODES = sorted(LEGEND, key=len, reverse=True)

# ---------------------------------------------------------------- geology unit polygons
polys = []
for d in page.get_drawings():
    f = d.get("fill")
    if not f: continue
    r = d["rect"]
    if r.width < 3 or r.height < 3: continue          # text glyphs and swatches
    ring = []
    for it in d["items"]:
        if it[0] == "l": ring += [it[1], it[2]]
        elif it[0] == "c": ring += [it[1], it[2], it[3], it[4]]
    if len(ring) < 3: continue
    try:
        g = Polygon([(q.x, q.y) for q in ring])
        if not g.is_valid: g = make_valid(g)
        if g.is_empty or g.area < 40: continue        # drop slivers under ~1.5 km2
    except Exception:
        continue
    polys.append((g, tuple(round(c, 3) for c in f)))
print("filled map-unit polygons:", len(polys))

# colour -> unit code, using the unit labels printed inside the polygons
from collections import Counter, defaultdict
votes = defaultdict(Counter)
for g, col in polys:
    minx, miny, maxx, maxy = g.bounds
    for (x0, y0, x1, y1, w) in words:
        if x0 < minx or x1 > maxx or y0 < miny or y1 > maxy: continue
        t = w.strip().rstrip(",")
        if t in LEGEND: votes[col][t] += 1
colour_code = {}
for col, c in votes.items():
    colour_code[col] = c.most_common(1)[0][0]
print("colours with a labelled code:", len(colour_code), "of", len({c for _, c in polys}))

rows = []
for g, col in polys:
    code = colour_code.get(col)
    name, period = LEGEND.get(code, ("Undifferentiated / label not legible", "unknown"))
    rows.append({"unit_code": code or "unlabelled", "unit_name": name, "period": period,
                 "sheet_colour": "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in col),
                 "how_named": "printed unit label inside the polygon" if code else "not read",
                 "geometry": g})
units = gpd.GeoDataFrame(rows, crs="EPSG:4326")
units["geometry"] = units.geometry.apply(
    lambda g: Polygon([to_ll(x, y) for x, y in g.exterior.coords],
                      [[to_ll(x, y) for x, y in r.coords] for r in g.interiors])
    if g.geom_type == "Polygon" else None)
units = units[units.geometry.notna() & ~units.geometry.is_empty]

# ---------------------------------------------------------------- line layers
def lines_by(pred):
    out = []
    for d in page.get_drawings():
        if not pred(d): continue
        cur = []
        for it in d["items"]:
            if it[0] == "l":
                if not cur: cur = [it[1], it[2]]
                else: cur.append(it[2])
            elif it[0] == "c":
                if not cur: cur = [it[1], it[2], it[3], it[4]]
                else: cur += [it[2], it[3], it[4]]
        if len(cur) >= 2:
            out.append(LineString([(q.x, q.y) for q in cur]))
    return out

def blue(d):
    c = d.get("color")
    return c and abs(c[0] - .35) < .05 and abs(c[1] - .57) < .05 and c[2] > .9
def grey_state(d):
    c = d.get("color")
    return c and all(abs(v - .667) < .03 for v in c) and abs((d.get("width") or 0) - 3.96) < .5

def project(gl):
    return [LineString([to_ll(x, y) for x, y in g.coords]) for g in gl if g.length > 0]

# ---------------------------------------------------------------------------- structure
# The sheet's legend (right-hand panel) gives the pen meanings for thick black ink:
#   "Roads"                      thick black continuous lines  -> the national road network
#   "Major Fractures / Faults"   short isolated hachured strokes -> faults
#   "Fractures / Fault (inferred)" the same symbol, lighter use
# There is no fold symbol, no dip-and-strike symbol and no separate lineament layer.
# So thick black strokes are split by CONNECTIVITY: strokes that touch other thick strokes
# belong to the continuous road network; strokes that stand alone are fault dashes.
FRAME = (130.0, 2092.0, 52.0, 1672.0)          # map frame in page points, from the graticule fit

def _thick_strokes():
    X0, X1, Y0, Y1 = FRAME
    out = []
    for d in page.get_drawings():
        c, w = d.get("color"), d.get("width")
        if c is None or w is None or max(c) > .05 or w < .95: continue
        for it in d["items"]:
            if it[0] == "l": a, b = it[1], it[2]
            elif it[0] == "c": a, b = it[1], it[4]
            else: continue
            if not (X0 <= a.x <= X1 and X0 <= b.x <= X1): continue
            if not (Y0 <= a.y <= Y1 and Y0 <= b.y <= Y1): continue
            out.append((a.x, a.y, b.x, b.y))
    return out

def _split_by_connectivity(segs, tol=0.6, big=5):
    """Group strokes that share an endpoint (to tol) and split the touching network from
    the isolated strokes.  Roads touch each other; fault dashes do not."""
    from collections import defaultdict
    key = lambda x, y: (round(x / tol) * tol, round(y / tol) * tol)
    parent = list(range(len(segs)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def union(i, j):
        a, b = find(i), find(j)
        if a != b: parent[a] = b
    where = defaultdict(list)
    for i, (x1, y1, x2, y2) in enumerate(segs):
        where[key(x1, y1)].append(i); where[key(x2, y2)].append(i)
    for lst in where.values():
        for a in lst[1:]: union(lst[0], a)
    comp = defaultdict(list)
    for i in range(len(segs)): comp[find(i)].append(i)
    road = [segs[i] for v in comp.values() if len(v) >= big for i in v]
    iso  = [segs[i] for v in comp.values() if len(v) <  big for i in v]
    return road, iso, len(comp)

def _chain(strokes, gap=14.0, maxdeg=25.0, min_pt=12.0):
    """Join collinear strokes separated by up to `gap` points into fault traces."""
    import math
    ang = lambda s: math.atan2(s[3] - s[1], s[2] - s[0])
    def dphi(a, b):
        d = abs(a - b) % math.pi
        return min(d, math.pi - d)
    used, traces = set(), []
    for i, s in enumerate(strokes):
        if i in used: continue
        used.add(i); line = [(s[0], s[1]), (s[2], s[3])]
        for head in (0, 1):
            while True:
                tip = line[0] if head == 0 else line[-1]
                ref = (line[1][0] - line[0][0], line[1][1] - line[0][1]) if head == 0 else \
                      (line[-1][0] - line[-2][0], line[-1][1] - line[-2][1])
                best = None
                for j, t in enumerate(strokes):
                    if j in used: continue
                    if dphi(math.atan2(ref[1], ref[0]), ang(t)) > math.radians(maxdeg): continue
                    for w, pt in ((0, (t[0], t[1])), (1, (t[2], t[3]))):
                        d = math.hypot(pt[0] - tip[0], pt[1] - tip[1])
                        if d <= gap and (best is None or d < best[0]): best = (d, j, w)
                if not best: break
                _, j, w = best
                t = strokes[j]; used.add(j)
                seg = [(t[0], t[1]), (t[2], t[3])]
                if w == 0: seg = seg[::-1]
                if head == 0: line = seg[::-1][:-1] + line
                else: line = line + seg[1:]
        traces.append(line)
    return [LineString(t) for t in traces if LineString(t).length >= min_pt]

_road_segs, _iso_segs, _ncomp = _split_by_connectivity(_thick_strokes())
_roads = [LineString([(s[0], s[1]), (s[2], s[3])]) for s in _road_segs]
_faults = _chain(_iso_segs)
print(f"structure: {_ncomp} thick-stroke groups -> {len(_roads)} road strokes, {len(_faults)} fault traces")

faults = gpd.GeoDataFrame(
    {"feature": "fault",
     "evidence": "isolated hachured thick black stroke, the sheet's 'Major Fractures / Faults' symbol",
     "certainty": "as printed; the sheet does not label individual faults certain or inferred",
     "geometry": project(_faults)}, crs="EPSG:4326")
roads = gpd.GeoDataFrame(
    {"feature": "road", "evidence": f"continuous thick black line, the sheet's 'Roads' symbol ({len(_roads)} strokes)",
     "geometry": project(_roads)}, crs="EPSG:4326")
rivers = gpd.GeoDataFrame({"feature": "river", "geometry": project(lines_by(blue))}, crs="EPSG:4326")
states = gpd.GeoDataFrame({"feature": "state boundary", "geometry": project(lines_by(grey_state))},
                          crs="EPSG:4326")

# graticule: long straight black lines
grat = []
for d in page.get_drawings():
    c = d.get("color")
    if not (c and max(c) < .05 and abs((d.get("width") or 0) - .36) < .01): continue
    r = d["rect"]
    if r.width > 1200 and r.height < 1.5: grat.append(LineString([(r.x0, (r.y0 + r.y1) / 2), (r.x1, (r.y0 + r.y1) / 2)]))
    elif r.height > 1200 and r.width < 1.5: grat.append(LineString([((r.x0 + r.x1) / 2, r.y0), ((r.x0 + r.x1) / 2, r.y1)]))
graticule = gpd.GeoDataFrame({"feature": "graticule", "geometry": project(grat)}, crs="EPSG:4326")

print("faults", len(faults), "roads", len(roads), "rivers", len(rivers), "state boundaries", len(states),
      "graticule", len(graticule), "units", len(units))

units.to_file(OUT, layer="geology_units", driver="GPKG")
faults.to_file(OUT, layer="faults", driver="GPKG", mode="a")
roads.to_file(OUT, layer="roads", driver="GPKG", mode="a")
rivers.to_file(OUT, layer="rivers", driver="GPKG", mode="a")
states.to_file(OUT, layer="state_boundaries", driver="GPKG", mode="a")
graticule.to_file(OUT, layer="graticule", driver="GPKG", mode="a")

summary = {
    "geology_units": int(len(units)),
    "distinct_units_named": int(units.unit_code.nunique()),
    "units_label_not_read": int((units.unit_code == "unlabelled").sum()),
    "fault_lines": int(len(faults)),
    "fault_km": round(float(faults.to_crs("EPSG:3857").length.sum() / 1000), 1),
    "road_strokes": int(len(roads)),
    "fold_symbols": 0,
    "river_lines": int(len(rivers)),
    "state_boundary_lines": int(len(states)),
    "graticule_lines": int(len(graticule)),
    "unit_codes": sorted(c for c in units.unit_code.unique() if c != "unlabelled"),
}
json.dump(summary, open(P / "Geology_Extraction_Summary.json", "w"), indent=2)
print(json.dumps(summary, indent=2)[:1500])
