"""Map number labels -> native px + zone. No merging: every pure-digit span is one label
(verified: close pairs are distinct cluster labels, no split digits)."""
import sys, re, csv
sys.path.insert(0,"scripts")
import common as C
from collections import Counter
rows=list(csv.DictReader(open("work/mineral_text_spans.csv")))
out=[]
for r in rows:
    t=r["text"].strip()
    if re.fullmatch(r"\d{1,3}\.?", t) and int(t.rstrip("."))>=1:
        x0,y0,x1,y1=map(float,(r["x0"],r["y0"],r["x1"],r["y1"]))
        if C.MIN_FRAME[0]<=x0<=C.MIN_FRAME[2] and C.MIN_FRAME[1]<=y0<=C.MIN_FRAME[3]:
            cx,cy=(x0+x1)/2,(y0+y1)/2
            out.append(dict(number=int(t.rstrip(".")), pdf_x=round(cx,2), pdf_y=round(cy,2),
                nat_x=round(float((cx-C.MIN_FRAME[0])*C.MIN_NATIVE_PXPT-0.5),2),
                nat_y=round(float((cy-C.MIN_FRAME[1])*C.MIN_NATIVE_PXPT-0.5),2),
                zone=C.mineral_zone_of(cx,cy), w_pt=round(x1-x0,1), h_pt=round(y1-y0,1)))
with open("work/mineral_numbers.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print("labels:", len(out), Counter(o["zone"] for o in out))
