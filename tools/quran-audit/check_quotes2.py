import re,os,glob,unicodedata
from collections import defaultdict
def norm(s):
    s=unicodedata.normalize('NFKD',s).replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')
    s=re.sub(r"[^A-Za-z0-9' ]",' ',s); return re.sub(r'\s+',' ',s).lower().strip()
STOP=set('''the a an and of to in that is was were be been it its this these those he she they them his her their for with from as by on at not but so then than which who whom what when where how if or no nor do did does have has had will would shall should may might can could there here you your we our i me my us also all any more most other some such only own same very s t don now into over under about after before upon among between because while said say says saying one'''.split())
def toks(s): return set(w for w in norm(s).split() if w and w not in STOP and len(w)>2)
corpus={}
for p in sorted(glob.glob('translation/*.txt')):
    t=int(os.path.basename(p)[:3])
    for ln in open(p,encoding='utf-8'):
        m=re.match(r'^\s*(\d+)\s*\|\s*(.*)$',ln)
        if m: corpus[(t,int(m.group(1)))]=m.group(2)
ctok={k:toks(v) for k,v in corpus.items()}
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
def best(q):
    qt=toks(q)
    if not qt: return None,0
    bs,br=0,None
    for k,vt in ctok.items():
        if not vt: continue
        r=len(qt&vt)/len(qt)
        if r>bs: bs,br=r,k
    return br,bs
pat=re.compile(r'“([^”]{20,700})”[^()]{0,60}\(([^()]{0,50}?)(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?[^()]{0,60}\)')
rows=[]
for v in sorted(secs):
    if v<19 or 25<=v<=54: continue
    for m in pat.finditer(secs[v]):
        q=m.group(1); s=int(m.group(3)); a=int(m.group(4)); b=int(m.group(5)) if m.group(5) else a
        cited=set()
        byref=False
        for vv in range(a,min(b,a+15)+1):
            if (s,vv) in ctok: cited|=ctok[(s,vv)]
        if not cited: rows.append((v,'%d:%d'%(s,a),'NO-VERSE',q[:70],'')); continue
        r_cited=len(toks(q)&cited)/max(1,len(toks(q)))
        if r_cited>=0.55: continue     # wording close enough to cited ref
        br,bs=best(q)
        rows.append((v,'%d:%d-%d'%(s,a,b),'cited %.2f'%r_cited,q[:75], '%s %s %.2f'%(br[0] if br else '-',br[1] if br else '',bs)))
print('items needing manual review:',len(rows))
for x in rows: print('7:%d  cited %s (%s)\n    "%s"\n    best: %s'%x)
