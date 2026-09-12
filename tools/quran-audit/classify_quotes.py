import re,os,glob,unicodedata,json
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
pat=re.compile(r'“([^”]{20,700})”[^()]{0,60}\(([^()]{0,50}?)(\d{1,3}):(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?[^()]{0,60}\)')
res={'match':[],'refix':[],'ambig':[]}
for f in sorted(glob.glob('tools/quran-audit/out/rewrites/007/b*.md')):
    mm=re.search(r'b([0-9]+)[.]md$',os.path.basename(f))
    if not mm: continue
    v=int(mm.group(1))
    if v>104 or 25<=v<=54: continue
    body=open(f,encoding='utf-8').read()
    for m in pat.finditer(body):
        q=m.group(1); s=int(m.group(3)); a=int(m.group(4)); b=int(m.group(5)) if m.group(5) else a
        cited=set()
        for vv in range(a,min(b,a+15)+1):
            if (s,vv) in ctok: cited|=ctok[(s,vv)]
        if not cited: continue
        qt=toks(q); rc=len(qt&cited)/max(1,len(qt))
        if rc>=0.55: continue
        bs,br=0,None
        for k,vt in ctok.items():
            if not vt: continue
            r=len(qt&vt)/len(qt)
            if r>bs: bs,br=r,k
        item={'sec':v,'ref':'%d:%d-%d'%(s,a,b),'rc':round(rc,2),'best':('%d:%d'%br if br else '','%.2f'%bs),'q':q}
        if rc>=0.30: res['match'].append(item)
        elif bs>=0.75 and br and (br[0]!=s): res['refix'].append(dict(item,newref='%d:%d'%br))
        else: res['ambig'].append(item)
for k in res: print(k,len(res[k]))
json.dump(res,open('/tmp/qclass.json','w'),ensure_ascii=False,indent=1)
print('--- refix candidates ---')
for it in res['refix']: print('7:%d cited %s -> %s (%.2f) | %s'%(it['sec'],it['ref'],it['newref'],float(it['best'][1]),it['q'][:80]))
print('--- ambiguous ---')
for it in res['ambig']: print('7:%d cited %s rc=%s best=%s | %s'%(it['sec'],it['ref'],it['rc'],it['best'],it['q'][:80]))
