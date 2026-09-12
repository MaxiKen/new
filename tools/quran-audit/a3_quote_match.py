import re, os, glob, json, unicodedata, collections, sys
ROOT='/home/user/new'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

def norm(s):
    s=unicodedata.normalize('NFKC',s)
    for a,b in [('\u2019',"'"),('\u2018',"'"),('\u201c','"'),('\u201d','"'),('\u2014',' '),('\u2013',' ')]:
        s=s.replace(a,b)
    s=re.sub(r'[\u0670\u0653\u02f9\u02ba\u02be\u02bf\u02b9]','',s)
    return re.sub(r'\s+',' ',s).strip().lower()

def toks(s):
    s=re.sub(r'[*_`~]','',s)
    s=re.sub(r'[^\w\s]',' ',s,flags=re.U)
    return [w for w in s.split() if len(w)>2]

TR={}
for n in range(1,115):
    d={}
    for line in open(ROOT+'/translation/%03d.txt'%n,encoding='utf-8'):
        m=re.match(r'^(\d+) \| (.*)$',line.rstrip('\n'))
        if m: d[int(m.group(1))]=m.group(2)
    TR[n]=d

# inverted index: token -> list of (ch,v)  (tokens len>=5, not too common)
df=collections.Counter()
vset={}
for ch,d in TR.items():
    for v,txt in d.items():
        S=set(t for t in toks(txt) if len(t)>=5)
        vset[(ch,v)]=S
        for t in S: df[t]+=1
N=len(vset)
IDX=collections.defaultdict(list)
for (ch,v),S in vset.items():
    for t in S:
        if df[t]<=250: IDX[t].append((ch,v))

def best_matches(qwordset, topk=4):
    cand=collections.Counter()
    for t in qwordset:
        for key in IDX.get(t,()): cand[key]+=1
    out=[]
    for key,c in cand.most_common(60):
        S=vset[key]
        ov=len(qwordset&S)/max(1,min(len(qwordset),len(S)))
        out.append((round(ov,3),key[0],key[1]))
    out.sort(reverse=True)
    return out[:topk]

CITE=re.compile(r'\((?:\s*(?:Qur[\'\u2019]?an|Q\.?|cf\.|see)?\s*)(\d{1,3})\s*:\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*\)')
QUOTE=re.compile(r'\*\s*[\u201c"]([^\u201d"]{12,})[\u201d"]\s*\*|\*[\u201c"]([^\u201d"]{12,})[\u201d"]\*|[\u201c"]([^\u201d"]{12,})[\u201d"]')

records=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    raw=open(p,encoding='utf-8').read()
    text=raw.replace('\r\n','\n')
    for cm in CITE.finditer(text):
        ch,v=int(cm.group(1)),int(cm.group(2))
        if not (1<=ch<=114): continue
        # nearest quote before the citation within 400 chars (not crossing another citation)
        window=text[max(0,cm.start()-420):cm.start()]
        quotes=[m for m in QUOTE.finditer(window)]
        if not quotes: continue
        # ignore quotes that are actually inside an earlier citation's area
        qm=quotes[-1]
        q=qm.group(1) or qm.group(2) or qm.group(3)
        if not q: continue
        # a citation closer than the quote's end? skip if another CITE between qm.end and cm.start
        between=window[qm.end():]
        if CITE.search(between): continue
        W=set(t for t in toks(q) if len(t)>=5)
        if len(W)<3: continue
        bm=best_matches(W)
        if not bm: continue
        cited=None
        for ov,c,vv in bm:
            if c==ch and vv==v: cited=(ov,vv); break
        ref_ov=None
        key=(ch,v)
        if key in vset:
            ref_ov=round(len(W&vset[key])/max(1,min(len(W),len(vset[key]))),3)
        line=text[:cm.start()].count('\n')+1
        records.append(dict(file=n,line=line,cite='%d:%d'%(ch,v),cited_ov=ref_ov,
                            best=bm,quote=q[:160]))
json.dump(records,open('os.path.join(OUT,'qmatch.json','w'),ensure_ascii=False)
print('quotation units matched to a citation:',len(records))
good=[r for r in records if r['cited_ov'] is not None and r['cited_ov']>=0.5]
weak=[r for r in records if r['cited_ov'] is not None and r['cited_ov']<0.3]
print('well-attested (>=0.50 overlap with cited verse):',len(good))
print('weak (<0.30):',len(weak))

sus=[]
for r in weak:
    top=r['best'][0]
    if top[1:]!=(int(r['cite'].split(':')[0]),int(r['cite'].split(':')[1])) and top[0]>=0.6 and top[0]-r['cited_ov']>=0.3:
        sus.append(r)
print('CANDIDATE MISATTRIBUTIONS (best match elsewhere & much stronger):',len(sus))
for r in sus:
    print('%03d:%d  cited %-8s ov=%.2f  best %d:%d ov=%.2f | %s'%(r['file'],r['line'],r['cite'],r['cited_ov'],r['best'][0][1],r['best'][0][2],r['best'][0][0],r['quote'][:110]))
