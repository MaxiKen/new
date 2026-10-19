"""Assign detections<->numbers<->index; write Minerals shapefiles + tables."""
import sys, re, csv, json
sys.path.insert(0,"scripts")
import numpy as np
import common as C
from scipy.spatial import cKDTree
from collections import Counter, defaultdict
import geopandas as gpd
from shapely.geometry import Point

# ---- load index, renumber dup heuristic, decode codes, clean localities
idx=list(csv.DictReader(open("work/mineral_index_raw.csv")))
for e in idx: e["number"]=int(e["number"])
by_zone=defaultdict(list)
for e in idx: by_zone[e["zone"]].append(e)
renum=0  # printed index numbers kept as-is (NGSA index itself contains duplicate numbers)
print("renumbered dups: 0 (disabled)")
CODEMAP={
 "Cl":"Clay","CI":"Clay","Ka":"Kaolin","Ls":"Limestone","Gy":"Gypsum","Cy":"Gypsum","Ta":"Tantalite",
 "Be":"Beryl","Mb":"Marble","Fe":"Iron Ore","Gs":"Glass Sand","Br":"Brine","Sn":"Tin (Cassiterite)",
 "Au":"Gold","Ba":"Baryte","Tc":"Talc","Fp":"Feldspar","C":"Coal","P":"Phosphate","Gm":"Gemstone (Beryl etc.)",
 "Tm":"Tourmaline","Qa":"Quartz","Qz":"Quartz","Nb":"Columbite","W":"Wolframite","Zr":"Zircon","Ky":"Kyanite",
 "Cr":"Chromite","Py":"Pyrite","Pb":"Lead","Zn":"Zinc","Dt":"Diatomite","Fr":"Fire Clay (?)","Gn":"Galena",
 "Ca":"Calcite","Bx":"Bauxitic Clay","Ds":"Dimension Stone","Aq":"Aquamarine (Beryl)","Bn":"Bentonite",
 "Bc":"Brick Clay","Fc":"Fire Clay","Na":"Salt / Trona","Tr":"Trona","Ts":"Tar Sand","Lg":"Lignite",
 "Mc":"Marcasite","Mz":"Monazite","Mo":"Molybdenite","Mn":"Manganese","Mg":"Magnesite","U":"Uranium",
 "Ag":"Silver","Cu":"Copper","Ni":"Nickel","Bi":"Bismuth","Li":"Lithium","Ab":"Asbestos","E":"Evaporite (?)",
 "Gr":"Granite","Lp":"Lepidolite","Tpz":"Topaz","Tp":"Topaz","Sl":"Sillimanite","Ss":"Silica Sand",
 "Mi":"Marl / Mica (?)","Ml":"Marl (?)","Mu":"Muscovite (Mica) (?)","Sd":"Sand (?)","M":"M (unspecified - see symbol)",
 "S":"Salt (?)","G":"Granite (?)","K":"Kaolin (?)","Dl":"Diatomite (?)","Ci":"? (Ci)","Us":"? (Us)","Ks":"? (Ks)","Ke":"? (Ke)",
 "Ru":"Ruby (Corundum)","F":"Fluorite","Rg":"River Gravel",
}
# legend symbol name -> plausible index tokens (for agreement scoring)
SYM_TOKENS={
 "Asbestos / Serpentine":{"Ab"},"Ball Clay":{"Cl"},"Baryte":{"Ba"},"Bauxitic Clay":{"Bx"},"Bentonite":{"Bn"},
 "Beryl, Aquamarine, Emerald":{"Be","Aq","Gm"},"Bismuth":{"Bi"},"Bitumen":{"Ts"},"Brick Clay":{"Bc"},"Brine":{"Br"},
 "Chromite":{"Cr"},"Clay / Pottery Clay":{"Cl","CI"},"Coal":{"C"},"Columbite":{"Nb","Sn"},
 "Copper minerals":{"Cu"},"Corundum, Sapphire & Ruby":{"Ru"},"Diatomite":{"Dt","Dl"},"Dimension Stone":{"Ds"},
 "Evaporite":{"E"},"Feldspar":{"Fp"},"Fire Clay":{"Fc","Fr"},"Fluorite":{"F"},"Garnet":{"Gm"},
 "Glass Sand":{"Gs"},"Graphite":{"Gr"},"River Gravel":{"Rg"},"Galena":{"Gn","Pb"},"Granite":{"Gr","G"},
 "Gypsum":{"Gy","Cy"},"Phosphate":{"P"},"Iron Ore (Magnetite, Ilmenite)":{"Fe"},
 "Kaolin / kaolinitic clay":{"Ka","K"},"Kyanite":{"Ky"},"Lead - Zinc":{"Pb","Zn"},"Lepidolite":{"Lp"},
 "Lignite":{"Lg"},"Limestone":{"Ls"},"Manganese":{"Mn"},"Marble":{"Mb","M"},"Marcasite (mc)":{"Mc"},
 "Marl (mi)":{"Mi","Ml"},"Mica (m)":{"M","Mi","Mu"},"Magnesite":{"Mg"},"Molybdenite (mo)":{"Mo"},
 "Monazite":{"Mz"},"Nickel (ni)":{"Ni"},"Phosphate Rock":{"P"},"Psammite":set(),
 "Pyrite / Pyroclore (py)":{"Py"},"Rose Quartz (r)":{"Qa","Qz"},"Saltlake / Potash":{"Na","S"},
 "Silica Sand (ss)":{"Ss","Sd"},"Sillimanite (sl)":{"Sl"},"Silver (ag)":{"Ag"},"Talc (tc)":{"Tc"},
 "Tantalite (ta)":{"Ta"},"Tar Sand (ts)":{"Ts"},"Topaz (tpz)":{"Tpz","Tp"},"Tourmaline (tm)":{"Tm"},
 "Trona (tr)":{"Tr","Na"},"Uranium (u)":{"U"},"Wolframite (w)":{"W"},"Zircon (zr)":{"Zr"},
 "Lithium (Amblygonite, Kunzite, Morganite, Spodumene, etc)":{"Li"},"Calcite":{"Ca"},"Gold":{"Au"},"Oil and Gas":set(),
}
def decode(code_raw):
    if not code_raw: return [], ""
    norm=code_raw.replace(" ","")
    toks=[t for t in re.split(r"[.,]", norm) if t]
    names=[CODEMAP.get(t, t) for t in toks]
    return toks, "; ".join(names)
def clean_loc(s):
    toks=s.split(" "); out=[]
    for t in toks:
        if out and len(out[-1])==1 and out[-1].isupper() and t[:1].islower():
            out[-1]=out[-1]+t
        elif out and len(t)==1 and t.islower():
            out[-1]=out[-1]+t
        else: out.append(t)
    return " ".join(out)
index={}
for e in idx:
    toks,decoded=decode(e["code_raw"])
    e["code_tokens"]=toks; e["mineral_decoded"]=decoded
    e["locality_clean"]=clean_loc(e["locality"])
    key=(e["zone"],int(e["number"]))
    if key not in index: index[key]=e
print("index entries usable:", len(index))
with open("output/04_Tables/Mineral_Index_transcribed.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["ZONE","NUMBER","LOCALITY","CODE_RAW","MINERAL_DECODED","RAW_TEXT"])
    w.writeheader()
    for e in sorted(idx, key=lambda e:(e["zone"], int(e["number"]))):
        w.writerow(dict(ZONE=e["zone"],NUMBER=e["number"],LOCALITY=e["locality_clean"],CODE_RAW=e["code_raw"],
                        MINERAL_DECODED=e["mineral_decoded"],RAW_TEXT=e["raw"]))

# ---- load points + numbers
pts=list(csv.DictReader(open("work/mineral_points_v1.csv")))
for p in pts:
    p["cx"]=float(p["cx"]); p["cy"]=float(p["cy"]); p["score1"]=float(p["score1"]) if p["score1"] not in ("","None") else 0.0
    px,py=C.mineral_native_to_pdf(p["cx"],p["cy"]); p["zone"]=C.mineral_zone_of(px,py)
nums=list(csv.DictReader(open("work/mineral_numbers.csv")))
for n in nums:
    n["nat_x"]=float(n["nat_x"]); n["nat_y"]=float(n["nat_y"]); n["number"]=int(n["number"])

# ---- assignment (same zone, <=62px, agreement bonus)
def agrees(p, n):
    e=index.get((n["zone"],n["number"]))
    if not e or not p["sym1"]: return False
    return len(SYM_TOKENS.get(p["sym1"],set()) & set(e["code_tokens"]))>0
pairs=[]
for ni,n in enumerate(nums):
    for pi_,p in enumerate(pts):
        d=float(np.hypot(p["cx"]-n["nat_x"], p["cy"]-n["nat_y"]))
        if d<=62:
            eff=d-(9 if agrees(p,n) else 0)+(0 if p["zone"]==n["zone"] else 12)+(25 if p["cls"]=="number_only" else 0)
            pairs.append((eff, d, ni, pi_))
pairs.sort()
num_to_pt={}; pt_to_num={}
for eff,d,ni,pi_ in pairs:
    if ni not in num_to_pt and pi_ not in pt_to_num:
        num_to_pt[ni]=pi_; pt_to_num[pi_]=ni
# shared second number for still-unassigned numbers near an assigned point
alt_num={}
for ni,n in enumerate(nums):
    if ni in num_to_pt: continue
    best=None
    for pi_,p in enumerate(pts):
        if p["zone"]!=n["zone"]: continue
        d=float(np.hypot(p["cx"]-n["nat_x"], p["cy"]-n["nat_y"]))
        if d<=26 and (best is None or d<best[0]): best=(d,pi_)
    if best: alt_num[ni]=best[1]
assigned_nums=set(num_to_pt)|set(alt_num)
print(f"numbers assigned 1:1={len(num_to_pt)} shared={len(alt_num)} unassigned={len(nums)-len(assigned_nums)}")

drop_pi=set()
for pi_,p in enumerate(pts):
    if p["cls"]=="number_only" and pi_ not in pt_to_num:
        drop_pi.add(pi_)  # blob took this number; placeholder redundant
print("redundant NUMBER_ONLY dropped:", len(drop_pi))
records=[]
for pi_,p in enumerate(pts):
    if pi_ in drop_pi: continue
    ni=pt_to_num.get(pi_)
    zone=p["zone"]; number=-1; alt=-1; loc=""; code=""; mineral=""; 
    if ni is not None:
        n=nums[ni]; number=n["number"]; zone=n["zone"]
        e=index.get((zone,number))
        if e: loc=e["locality_clean"]; code=e["code_raw"]; mineral=e["mineral_decoded"]
    alts=[nums[k]["number"] for k,v in alt_num.items() if v==pi_]
    if alts: alt=alts[0]
    if not mineral: mineral=p["sym1"] or ""
    if p["cls"]=="number_only": match="NumberOnly"
    elif p["src"]=="pattern": match="Partial"
    elif p["src"] in ("cluster","rescue"): match="Partial"
    else: match="Complete"
    lon,lat=C.mineral_native_to_lonlat_corr(p["cx"],p["cy"])
    records.append(dict(MIN_ID="", ZONE=zone, NUMBER=number, ALT_NUM=alt, LOCALITY=loc[:120],
        MIN_CODE=code[:40], MINERAL=mineral[:160], SYMBOL=(p["sym1"] or "")[:60], MATCH=match,
        SCORE=round(p["score1"],3), SRC=p["src"], REVIEW=p.get("review","") or "",
        LON=round(float(lon),6), LAT=round(float(lat),6), geometry=Point(float(lon),float(lat))))
# guarantee: every printed number gets a point (placeholder at number if nothing assigned)
have_num={(r["ZONE"],r["NUMBER"]) for r in records if r["NUMBER"]>0} | {(r["ZONE"],r["ALT_NUM"]) for r in records if r["ALT_NUM"]>0}
added_ph=0
for n in nums:
    if (n["zone"],n["number"]) not in have_num:
        e=index.get((n["zone"],n["number"]))
        lon,lat=C.mineral_native_to_lonlat_corr(n["nat_x"],n["nat_y"])
        records.append(dict(MIN_ID="",ZONE=n["zone"],NUMBER=n["number"],ALT_NUM=-1,
            LOCALITY=(e["locality_clean"][:120] if e else ""),MIN_CODE=(e["code_raw"][:40] if e else ""),
            MINERAL=(e["mineral_decoded"][:160] if e else ""),SYMBOL="",MATCH="NumberOnly",SCORE=0.0,
            SRC="number_only",REVIEW="NUMBER_ONLY",LON=round(float(lon),6),LAT=round(float(lat),6),
            geometry=Point(float(lon),float(lat))))
        added_ph+=1
print("placeholder points added for unassigned numbers:", added_ph)
# spatial sanity: main points must fall inside Nigeria boundary (+0.06 deg)
bnd=gpd.read_file("output/02_Shapefiles/Nigeria_Boundary.shp")
poly=bnd.geometry.iloc[0].buffer(0.06)
nout=0
for r in records:
    if not r["REVIEW"] and not poly.contains(r["geometry"]):
        r["REVIEW"]="OUTSIDE_NGA"; nout+=1
print("main points moved to review (outside boundary):", nout)
main=[r for r in records if not r["REVIEW"]]
rev=[r for r in records if r["REVIEW"]]
for i,r in enumerate(main,1): r["MIN_ID"]=f"MIN{i:04d}"
for i,r in enumerate(rev,1): r["MIN_ID"]=f"REV{i:04d}"
print("main points:", len(main), " review:", len(rev))
print("main with number:", sum(1 for r in main if r["NUMBER"]>0), " unnumbered:", sum(1 for r in main if r["NUMBER"]<0))
print("MATCH:", Counter(r["MATCH"] for r in main))
for name,recs in [("Minerals",main),("Minerals_NEEDS_REVIEW",rev)]:
    g=gpd.GeoDataFrame(recs, crs="EPSG:4326")
    g.to_file(f"output/02_Shapefiles/{name}.shp")
    print("wrote", name, len(g))
with open("output/04_Tables/Mineral_Points_all.csv","w",newline="") as f:
    fields=["MIN_ID","ZONE","NUMBER","ALT_NUM","LOCALITY","MIN_CODE","MINERAL","SYMBOL","MATCH","SCORE","SRC","REVIEW","LON","LAT"]
    w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
    for r in main+rev: w.writerow({k:r[k] for k in fields})
# stats for QA/README
stats=dict(numbers_on_map=len(nums), numbers_assigned_11=len(num_to_pt), numbers_shared=len(alt_num),
           numbers_unassigned=len(nums)-len(assigned_nums), main_points=len(main), review_points=len(rev),
           index_entries=len(idx),
           assigned_with_locality=sum(1 for r in main if r["NUMBER"]>0 and r["LOCALITY"]),
           assigned_no_locality=sum(1 for r in main if r["NUMBER"]>0 and not r["LOCALITY"]))
json.dump(stats, open("work/mineral_stats.json","w"), indent=1)
print(stats)
