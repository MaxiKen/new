"""Parse printed mineral index: per-column lines -> entries -> zone runs by number resets."""
import sys, re, csv
sys.path.insert(0,"scripts")
import numpy as np
from collections import Counter, defaultdict

rows=list(csv.DictReader(open("work/mineral_text_spans.csv")))
spans=[]
for r in rows:
    x0,y0,x1,y1=map(float,(r["x0"],r["y0"],r["x1"],r["y1"])); size=float(r["size"])
    if x0>=2280 and 8.5<=size<11 and ((x0<3350 and y0<2060) or (x0>=3350 and y0<1950)):
        spans.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,text=r["text"]))
# column starts from anchor x0 clustering (digit-start after lstrip)
starts_x=sorted(s["x0"] for s in spans if re.match(r"^\d{1,3}[.)]?\s", s["text"].lstrip()))
clusters=[]; cur=[starts_x[0]]
for v in starts_x[1:]:
    if v-cur[-1]>18: clusters.append(cur); cur=[v]
    else: cur.append(v)
clusters.append(cur)
COLS=[float(np.median(c)) for c in clusters]
merged=[COLS[0]]
for c in COLS[1:]:
    if c-merged[-1]<45: merged[-1]=(merged[-1]+c)/2
    else: merged.append(c)
COLS=merged
print("columns merged:", [round(c,1) for c in COLS])
def band_of(x0):
    b=-1
    for i,c in enumerate(COLS):
        if x0>=c-30: b=i
    return b

entries=[]
for b in range(len(COLS)):
    bs=[s for s in spans if band_of(s["x0"])==b]
    bs.sort(key=lambda s:(s["y0"], s["x0"]))
    lines=[]; cur=None
    for s in bs:
        if cur is None or s["y0"]-cur["y0"]>4.5:
            cur=dict(y0=s["y0"], spans=[s]); lines.append(cur)
        else: cur["spans"].append(s)
    band_entries=[]; pending_first=None
    for L in lines:
        sp=sorted(L["spans"], key=lambda s:s["x0"])
        txt=""
        for k,s in enumerate(sp):
            if k>0: txt+= "" if (s["x0"]-sp[k-1]["x1"])<1.2 else " "
            txt+=s["text"]
        txt=re.sub(r"\s+"," ",txt).strip()
        if not txt: continue
        _tok=txt.split(" ")[0]
        _norm=_tok.translate(str.maketrans({"l":"1","I":"1","|":"1","O":"0","o":"0"}))
        if re.search(r"\d", _tok) and re.fullmatch(r"\d{1,3}[.)]?", _norm): txt=_norm+txt[len(_tok):]
        m=re.match(r"^(\d{1,3})[.)]?\s*(.*)$", txt)
        if m and int(m.group(1))<=260:
            band_entries.append(dict(number=int(m.group(1)), raw=m.group(2).strip(), band=b, y0=round(L["y0"],1)))
        elif band_entries and len(txt)<95:
            band_entries[-1]["raw"]+=" "+txt
        elif not band_entries and pending_first is None and len(txt)<95:
            pending_first=(txt, round(L["y0"],1))
    if band_entries and band_entries[0]["number"]==2 and pending_first:
        raw1=re.sub(r"^[Il|]\s+","",pending_first[0])
        band_entries.insert(0, dict(number=1, raw=raw1, band=b, y0=pending_first[1]))
    print(f"band {b} x~{COLS[b]:.0f}: {len(band_entries)} entries, numbers head={[e['number'] for e in band_entries[:6]]} tail={[e['number'] for e in band_entries[-4:]]}")
    entries+=band_entries
print("total entries:", len(entries))
# zone runs by resets in concatenated reading order
segs=[]; cur=[entries[0]]
for e in entries[1:]:
    if e["number"]<=3 and cur[-1]["number"]>20:
        segs.append(cur); cur=[e]
    else: cur.append(e)
segs.append(cur)
print("segments:", [(len(s), s[0]["number"], max(x["number"] for x in s)) for s in segs])
ZONES="ABCDEFG"
allE=[]
for zi,seg in enumerate(segs):
    z=ZONES[zi] if zi<7 else "?"
    for e in seg: e["zone"]=z; allE.append(e)
entries=allE
# split embedded entries inside raw (pattern ' N. ' with N == expected-ish)
split_out=[]
for e in entries:
    raw=e["raw"]; cur=e
    while True:
        m=re.search(r"\s+(\d{1,3})[.)]\s+(?=[A-Z(])", raw)
        if m and 0 < int(m.group(1))-cur["number"] <= 8:
            head=raw[:m.start()].strip(); tail=raw[m.end():].strip()
            cur["raw"]=head; split_out.append(cur)
            cur=dict(number=int(m.group(1)), raw=tail, band=e["band"], y0=e["y0"], zone=e["zone"])
            raw=tail
        else:
            cur["raw"]=raw; split_out.append(cur); break
entries=split_out
per=defaultdict(list)
for e in entries: per[e["zone"]].append(e["number"])
for z in "ABCDEFG?":
    ns=per.get(z,[])
    if ns:
        miss=[k for k in range(1,max(ns)+1) if k not in set(ns)]
        dup=[k for k,c in Counter(ns).items() if c>1]
        print(f" zone {z}: {len(ns)} entries max={max(ns)} missing={miss} dup={dup}")

def split_code(raw):
    raw=re.sub(r"\s+"," ",raw).strip()
    if " - " in raw:
        loc,code=raw.rsplit(" - ",1); return loc.strip(), code.strip()
    toks=raw.split(" ")
    suf=[]
    while toks:
        t=toks[-1]
        if re.fullmatch(r"[A-Za-z]{1,2}[.]?", t) or re.fullmatch(r"[A-Z][a-z]?(\.[A-Z][a-z]?)+\.?", t) or t in (".",","):
            suf.insert(0,toks.pop())
        else: break
    if suf and toks:
        return " ".join(toks).strip(), " ".join(suf).strip()
    return raw, ""
codes=Counter()
for e in entries:
    loc,code=split_code(e["raw"]); e["locality"]=loc; e["code_raw"]=code; codes[code]+=1
print("code vocab:", len(codes))
for c,k in codes.most_common(100): print(f"   {k:4d}  {c!r}")
with open("work/mineral_index_raw.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["zone","number","locality","code_raw","raw","band","y0"])
    w.writeheader(); w.writerows(entries)
print("wrote work/mineral_index_raw.csv")
for e in entries[:5]: print(e)
