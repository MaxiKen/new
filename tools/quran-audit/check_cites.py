import re,sys,os,unicodedata
def load(t):
    d={}
    p='translation/%03d.txt'%t
    if not os.path.exists(p): return d
    for ln in open(p,encoding='utf-8'):
        m=re.match(r'^\s*(\d+)\s*\|\s*(.*)$',ln)
        if m: d[int(m.group(1))]=m.group(2)
    return d
cache={}
def verse(t,v):
    if t not in cache: cache[t]=load(t)
    return cache[t].get(v)
def norm(s):
    s=unicodedata.normalize('NFKD',s).replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')
    s=re.sub(r"[^A-Za-z0-9' ]",' ',s)
    return re.sub(r'\s+',' ',s).lower().strip()
STOP=set('''the a an and of to in that is was were be been it its this these those he she they them his her their for with from as by on at not but so then than which who whom what when where how if or no nor do did does have has had will would shall should may might can could there here you your we our i me my us also all any more most other some such only own same very s t don now into over under about after before upon among between because while said say says saying one who's'''.split())
def toks(s): return [w for w in norm(s).split() if w and w not in STOP and len(w)>2]
lines=open('expanded/007.md',encoding='utf-8').read().replace('\r\n','\n').split('\n')
H=re.compile(r'^## Sūrah .+? (\d+):(\d+)\s*$')
idx=[(i,int(H.match(l.strip()).group(2))) for i,l in enumerate(lines) if H.match(l.strip())]
secs={}
for k,(i,v) in enumerate(idx):
    if v>104: break
    nxt=idx[k+1][0] if k+1<len(idx) else len(lines)
    chunk=lines[i:nxt]; body=[];q=False
    for l in chunk[1:]:
        if l.startswith('>'): q=True; continue
        if q and l.strip()=='': q=False; continue
        if not q: body.append(l)
    secs[v]='\n'.join(body)
R=re.compile(r'(?<![\d:])(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?')
missing=[];low=[];nrefs=0;nquote=0
for v in sorted(secs):
    if v<19 or 25<=v<=54: continue
    text=secs[v]
    # sentence-ish units
    units=re.split(r'(?<=[.!?])\s+|\n\n',text)
    pos=0
    for m in R.finditer(text):
        t,a=int(m.group(1)),int(m.group(2)); b=int(m.group(3)) if m.group(3) else a
        if t==7 and 19<=a<=104: continue
        nrefs+=1
        if t>114 or a==0: missing.append((v,m.group(0),'SYNTAX')); continue
        got={}
        for vv in range(a,min(b,a+15)+1):
            tx=verse(t,vv)
            if tx: got[vv]=tx
        if not got: missing.append((v,m.group(0),'NO-VERSE')); continue
        unit=next((u for u in units if m.group(0) in u),'')
        qs=re.findall(r'“([^”]{20,600})”',unit)
        # widen: also quotes in the immediately surrounding text ±600 chars
        if not qs:
            win=text[max(0,m.start()-700):m.end()+700]
            qs=re.findall(r'“([^”]{20,600})”',win)
        if not qs: continue
        nquote+=1
        vt=set()
        for vv,tx in got.items(): vt|=set(toks(tx))
        best=max((len(set(toks(q))&vt)/max(1,len(set(toks(q))))) for q in qs)
        if best<0.30: low.append((v,m.group(0),round(best,2),qs[0][:70]))
print('refs checked:',nrefs,' with nearby quote:',nquote,' missing:',len(missing),' low-overlap:',len(low))
for r in missing: print('MISSING',r)
for r in low: print('LOW 7:%d %s %.2f | %s'%r)
