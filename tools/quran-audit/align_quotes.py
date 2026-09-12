import re,os,glob,unicodedata,json
MANUAL={'7:21|7:68','7:23|4:111','7:24|37:148','7:56|26:151','7:61|46:9','7:62|6:66','7:65|26:124','7:68|38:70','7:71|7:71','7:87|26:118','7:93|11:95','7:101|28:3','7:103|30:56','7:102|46:17','7:94|7:94','7:20|7:20','7:23|7:16'}
def norm(s):
    s=unicodedata.normalize('NFKD',s).replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')
    s=re.sub(r"[^A-Za-z0-9' ]",' ',s); return re.sub(r'\s+',' ',s).lower().strip()
STOP=set('''the a an and of to in that is was were be been it its this these those he she they them his her their for with from as by on at not but so then than which who whom what when where how if or no nor do did does have has had will would shall should may might can could there here you your we our i me my us also all any more most other some such only own same very s t don now into over under about after before upon among between because while said say says saying one'''.split())
def toks(s): return set(w for w in norm(s).split() if w and w not in STOP and len(w)>2)
def load(t):
    d={}
    p='translation/%03d.txt'%t
    for ln in open(p,encoding='utf-8'):
        m=re.match(r'^\s*(\d+)\s*\|\s*(.*)$',ln)
        if m: d[int(m.group(1))]=m.group(2)
    return d
cache={}
def verse(t,v):
    if t not in cache: cache[t]=load(t)
    return cache[t].get(v)
pat=re.compile(r'“([^”]{20,700})”[^()]{0,60}\(([^()]{0,50}?)(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?[^()]{0,60}\)')
log=[]
for f in sorted(glob.glob('tools/quran-audit/out/rewrites/007/b*.md')):
    mm=re.search(r'b([0-9]+)[.]md$',os.path.basename(f))
    if not mm: continue
    v=int(mm.group(1))
    if v>104 or 25<=v<=54: continue
    body=open(f,encoding='utf-8').read()
    new=body; changed=0
    for m in list(pat.finditer(body)):
        q=m.group(1); s=int(m.group(3)); a=int(m.group(4)); b=int(m.group(5)) if m.group(5) else a
        key='%d|%d:%d'%(v,s,a)
        if key in MANUAL: continue
        parts=[verse(s,vv) for vv in range(a,min(b,a+15)+1)]
        parts=[p for p in parts if p]
        if not parts: continue
        cited=set()
        for p in parts: cited|=toks(p)
        rc=len(toks(q)&cited)/max(1,len(toks(q)))
        if rc>=0.55: continue
        disk=' … '.join(parts)
        disk=re.sub(r'\s+',' ',disk).strip()
        if len(disk)>250:
            cut=disk[:250]; cut=cut[:max(cut.rfind('. '),cut.rfind('; '),cut.rfind(', '),cut.rfind(' '))]
            disk=cut.rstrip(' ,;')+' …'
        if q not in new: continue
        new=new.replace('“%s”'%q,'“%s”'%disk,1)
        changed+=1
        log.append('7:%d %d:%d  OLD: %s\n         NEW: %s'%(v,s,b,q[:120],disk[:200]))
    if changed:
        open(f,'w',encoding='utf-8').write(new)
        log.append('== b%d.md: %d quote(s) aligned'%(v,changed))
open('/tmp/align_log.txt','w',encoding='utf-8').write('\n'.join(log))
print('\n'.join(log[-40:]))
print('total replacements:',len([l for l in log if l.startswith('7:')]))
