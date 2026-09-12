import re, os, glob, json, collections, unicodedata, math, sys
sys.path.insert(0,'/home/user/new/tools/quran-audit/')
from stop import STOP
ROOT='/home/user/new'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
def toks(s):
    s=unicodedata.normalize('NFKC',s)
    s=s.replace('\u2019',"'").replace('\u02be','').replace('\u02bf','').replace('\u02b9','')
    s=re.sub(r'[*_`~]','',s); s=re.sub(r'[^\w\s]',' ',s,flags=re.U)
    return [w.lower() for w in s.split() if len(w)>=4 and w.lower() not in STOP]
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
IDX=collections.defaultdict(set)
DF=collections.Counter()
for k,S in VSET.items():
    for t in S: IDX[t].add(k); DF[t]+=1
N=len(VSET)
IDF={t:math.log(N/(1+DF[t])) for t in DF}
def score(W,ch,v,span=1):
    U=set()
    for i in range(max(1,v-span),v+span+1): U|=VSET.get((ch,i),set())
    inter=[(IDF.get(t,0)) for t in W&U]
    tot=sum(IDF.get(t,0) for t in W)
    return sum(inter)/tot if tot else 0
def best_anywhere(W,k=4):
    c=collections.Counter()
    for t in W:
        for key in IDX.get(t,()): c[key]+=IDF.get(t,0)
    scored=sorted(((round(score(W,ch,v),3),ch,v) for (ch,v),_ in c.most_common(300)),reverse=True)
    return scored[:k]
CITE=re.compile(r'\(\s*(?:(?:Qur[\'\u2019]?an|Q|cf\.|see\s+also|see)\s*)?(\d{1,3})\s*:\s*(\d{1,3})\s*\)',re.I)
QUOTE=re.compile(r'[\u201c"]\s*([^\u201d"]{12,}?)\s*[\u201d"]')
SENT=re.compile(r'[.!?]\s+[A-Z"\u201c]')
recs=[]
nomat=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    raw=open(p,encoding='utf-8').read().replace('\r\n','\n')
    for cm in CITE.finditer(raw):
        ch,v=int(cm.group(1)),int(cm.group(2))
        if not 1<=ch<=114: continue
        win=raw[max(0,cm.start()-360):cm.start()]
        q=None
        for qm in reversed(list(QUOTE.finditer(win))):
            gap=win[qm.end():]
            if CITE.search(gap): continue
            if SENT.search(gap): continue   # must be same sentence
            q=qm.group(1); break
        if not q: continue
        W=set(toks(q))
        if len(W)<4: continue
        cov=round(score(W,ch,v),3)
        ba=best_anywhere(W)
        top=ba[0] if ba else (0.0,0,0)
        line=raw[:cm.start()].count('\n')+1
        r=dict(f=n,line=line,cite='%d:%d'%(ch,v),cov=cov,best=ba,quote=q[:240])
        recs.append(r)
        if not ba: nomat.append(r)
json.dump(recs,open('os.path.join(OUT,'idf.json','w'),ensure_ascii=False)
print('same-sentence quote/citation units:',len(recs))
print('quotes matching NO verse anywhere:',len(nomat))
for r in nomat[:15]: print('   %03d:%d cited %s | %s'%(r['f'],r['line'],r['cite'],r['quote'][:120].replace('\n',' ')))
sus=[r for r in recs if r['best'] and (r['best'][0][1]!=int(r['cite'].split(':')[0]) or r['best'][0][2]!=int(r['cite'].split(':')[1]))]
print('cited verse is not the top match:',len(sus))
strong=[r for r in sus if r['best'][0][0]>=0.85 and r['best'][0][0]-r['cov']>=0.4]
print('strong (top>=0.85 and +0.4 over cited):',len(strong))
for r in strong[:60]:
    b=r['best'][0]
    print('%03d:%d cited %-8s cov=%.2f  best %d:%d=%.2f | %s'%(r['f'],r['line'],r['cite'],r['cov'],b[1],b[2],b[0],r['quote'][:120].replace('\n',' ')))
