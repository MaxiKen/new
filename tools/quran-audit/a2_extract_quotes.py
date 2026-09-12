import re, os, glob, json, unicodedata
ROOT='/home/user/new'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

def norm(s):
    s=unicodedata.normalize('NFKC',s)
    for a,b in [('\u2019',"'"),('\u2018',"'"),('\u201c','"'),('\u201d','"'),('\u2014',' '),('\u2013',' ')]:
        s=s.replace(a,b)
    s=re.sub(r'[\u0670\u0653\u02f9\u02ba\u02be\u02bf\u02b9\u02ba]','',s)
    s=re.sub(r'[*_`~]','',s)
    s=re.sub(r'[^\w\s]',' ',s,flags=re.U)
    return re.sub(r'\s+',' ',s).strip().lower()

def words(s):
    return [w for w in norm(s).split() if len(w)>2]

# load translations
TR={}
for n in range(1,115):
    d={}
    for line in open(ROOT+'/translation/%03d.txt'%n,encoding='utf-8'):
        m=re.match(r'^(\d+) \| (.*)$',line.rstrip('\n'))
        if m: d[int(m.group(1))]=m.group(2)
    TR[n]=d

Q=re.compile(r'\(\s*(?:Qur[\'\u2019]?an|Q\.?)?\s*(\d{1,3})\s*:\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*\)')
hits=[]
seen=set()
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    lines=open(p,encoding='utf-8').read().split('\n')
    for i,l in enumerate(lines):
        for m in Q.finditer(l):
            ch,v=int(m.group(1)),int(m.group(2))
            if ch<1 or ch>114: continue
            key=(n,i,m.start())
            if key in seen: continue
            seen.add(key)
            # find the nearest preceding/following quoted text
            # simplistic: take text between previous citation end and this citation
            ctx=l
            hits.append(dict(file=n,line=i+1,ch=ch,v=v,end=int(m.group(3) or v),ctx=ctx))
print('total citation occurrences:',len(hits))

# evaluate overlap for citations that carry a quoted string on the same line
def quoted_segments(s):
    out=[]
    for m in re.finditer(r'[*_]*["\u201c]([^"\u201d]{15,})["\u201d][*_]*',s):
        out.append(m.group(1))
    return out

results=[]
for h in hits:
    qs=quoted_segments(h['ctx'])
    if not qs: continue
    q=max(qs,key=len)
    W=set(words(q))
    if len(W)<4: continue
    best=None
    tr=TR.get(h['ch'],{})
    if h['v'] in tr:
        ref=set(words(tr[h['v']]))
        best=(len(W&ref)/max(1,min(len(W),len(ref))),h['v'])
    # search all verses of cited chapter for a better match
    cand=[]
    for vv,txt in tr.items():
        ref=set(words(txt))
        if not ref: continue
        ov=len(W&ref)/max(1,min(len(W),len(ref)))
        cand.append((ov,vv))
    cand.sort(reverse=True)
    results.append(dict(file=h['file'],line=h['line'],cite='%d:%d'%(h['ch'],h['v']),
                        cited_ov=round(best[0],3) if best else None,
                        top=[(round(c[0],3),c[1]) for c in cand[:3]], quote=q[:120]))
json.dump(results,open('os.path.join(OUT,'quotes.json','w'),ensure_ascii=False,indent=1)
R=[r for r in results if r['cited_ov'] is not None]
print('citations with a quoted verse on the same line:',len(R))
R.sort(key=lambda r:r['cited_ov'])
print('\n--- 40 LOWEST overlap with cited verse ---')
for r in R[:40]:
    print('%03d:%d cite %-8s cited_ov=%.2f top=%s | %s'%(r['file'],r['line'],r['cite'],r['cited_ov'],r['top'],r['quote']))
