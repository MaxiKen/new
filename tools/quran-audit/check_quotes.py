import re,os,unicodedata,sys
def load(t):
    d={}; p='translation/%03d.txt'%t
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
    s=re.sub(r"[^A-Za-z0-9' ]",' ',s); return re.sub(r'\s+',' ',s).lower().strip()
STOP=set('''the a an and of to in that is was were be been it its this these those he she they them his her their for with from as by on at not but so then than which who whom what when where how if or no nor do did does have has had will would shall should may might can could there here you your we our i me my us also all any more most other some such only own same very s t don now into over under about after before upon among between because while said say says saying one'''.split())
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
# quote followed by a ref paren within 220 chars
pat=re.compile(r'“([^”]{20,700})”[^()]{0,60}\(([^()]{0,50}?)(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?[^()]{0,60}\)')
bad=[];n=0
for v in sorted(secs):
    if v<19 or 25<=v<=54: continue
    t=secs[v]
    for m in pat.finditer(t):
        q=m.group(1); s=int(m.group(3)); a=int(m.group(4)); b=int(m.group(5)) if m.group(5) else a
        vt=set()
        for vv in range(a,min(b,a+15)+1):
            tx=verse(s,vv)
            if tx: vt|=set(toks(tx))
        if not vt: bad.append((v,'%d:%d'%(s,a),'NO-VERSE',q[:60])); continue
        n+=1
        r=len(set(toks(q))&vt)/max(1,len(set(toks(q))))
        if r<0.40: bad.append((v,'%d:%d-%d'%(s,a,b),round(r,2),q[:60]))
print('quotes with ref after:',n,'flagged:',len(bad))
for x in bad: print('FLAG 7:%d -> %s (%s) | %s'%(x[0],x[1],x[2],x[3]))
