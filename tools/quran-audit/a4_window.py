import re, os, glob, json, collections, unicodedata
ROOT='/home/user/new'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
def toks(s):
    s=unicodedata.normalize('NFKC',s)
    s=re.sub(r'[*_`~]','',s)
    s=re.sub(r'[^\w\s]',' ',s,flags=re.U)
    return [w.lower() for w in s.split() if len(w)>4]
TR={}
for n in range(1,115):
    d={}
    for line in open(ROOT+'/translation/%03d.txt'%n,encoding='utf-8'):
        m=re.match(r'^(\d+) \| (.*)$',line.rstrip('\n'))
        if m: d[int(m.group(1))]=m.group(2)
    TR[n]=d
VSET={}
for _ch,_d in TR.items():
    for _v,_t in _d.items(): VSET[(_ch,_v)]=set(toks(_t))
# index token -> verses
IDX=collections.defaultdict(list)
for k,S in VSET.items():
    for t in S: IDX[t].append(k)

CITE=re.compile(r'\(\s*(?:Qur[\'\u2019]?an\s*)?(\d{1,3})\s*:\s*(\d{1,3})\s*\)')
QUOTE=re.compile(r'[\u201c"]([^\u201d"]{12,})[\u201d"]')

def window_cov(W,ch,v,span=3):
    U=set()
    for i in range(max(1,v-span),min(len(TR.get(ch,{})),v+span)+1): U|=VSET.get((ch,i),set())
    return len(W&U)/max(1,len(W))

def best_anywhere(W,k=6):
    c=collections.Counter()
    for t in W:
        for key in IDX.get(t,()): c[key]+=1
    scored=[]
    for (ch,v),_ in c.most_common(400):
        U=set()
        for i in range(max(1,v-2),v+3): U|=VSET.get((ch,i),set())
        scored.append((round(len(W&U)/max(1,len(W)),3),ch,v))
    scored.sort(reverse=True)
    return scored[:k]

out=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    raw=open(p,encoding='utf-8').read().replace('\r\n','\n')
    lines=raw.split('\n')
    for cm in CITE.finditer(raw):
        ch,v=int(cm.group(1)),int(cm.group(2))
        if not 1<=ch<=114: continue
        win=raw[max(0,cm.start()-500):cm.start()]
        # take the LAST quote that is not separated from the citation by another citation
        q=None
        for qm in reversed(list(QUOTE.finditer(win))):
            if CITE.search(win[qm.end():]): continue
            q=qm.group(1); break
        if not q: continue
        W=set(toks(q))
        if len(W)<4: continue
        cov_cited=window_cov(W,ch,v)
        ba=best_anywhere(W)
        top=ba[0] if ba else (0.0,0,0)
        same = bool(ba) and top[1]==ch and abs(top[2]-v)<=2
        out.append(dict(f=n,line=raw[:cm.start()].count('\n')+1,cite='%d:%d'%(ch,v),cov=round(cov_cited,3),
                        best=ba,quote=q[:200],ok=same))
json.dump(out,open('os.path.join(OUT,'win.json','w'),ensure_ascii=False)
print('quote/citation units:',len(out))
print('cited passage is the best match:',sum(1 for r in out if r['ok']))
sus=[r for r in out if not r['ok']]
print('NOT best match:',len(sus))
strong=[r for r in sus if r['best'][0][0]>=0.6 and r['cov']<0.4]
print('STRONG misattribution candidates:',len(strong))
for r in strong[:45]:
    print('%03d:%d cited %-8s cov=%.2f best=%s | %s'%(r['f'],r['line'],r['cite'],r['cov'],r['best'][:3],r['quote'][:150].replace('\n',' ')))
