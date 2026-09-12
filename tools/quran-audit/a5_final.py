import re, os, glob, json, collections, unicodedata, math, sys
sys.path.insert(0,'/home/user/new/tools/quran-audit/')
from stop import STOP
ROOT='/home/user/new'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
def toks(s):
    s=unicodedata.normalize('NFKC',s)
    s=s.replace('\u2019',"'").replace('\u02be','').replace('\u02bf','').replace('\u02b9','')
    s=re.sub(r'[*_`~]','',s)
    s=re.sub(r'[^\w\s]',' ',s,flags=re.U)
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
IDX=collections.defaultdict(list)
for k,S in VSET.items():
    for t in S: IDX[t].append(k)
CITE=re.compile(r'\(\s*(?:Qur[\'\u2019]?an\s*)?(\d{1,3})\s*:\s*(\d{1,3})\s*\)')
QUOTE=re.compile(r'[\u201c"]([^\u201d"]{12,})[\u201d"]')
def score(W,ch,v,span=2):
    U=set()
    for i in range(max(1,v-span),v+span+1):
        U|=VSET.get((ch,i),set())
    return len(W&U)/max(1,len(W))
def best_anywhere(W,k=5):
    c=collections.Counter()
    for t in W:
        for key in IDX.get(t,()): c[key]+=1
    scored=[]
    for key,_n in c.most_common(500):
        s=score(W,key[0],key[1])
        if s>0: scored.append((round(s,3),key[0],key[1]))
    scored.sort(reverse=True)
    return scored[:k]
out=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    raw=open(p,encoding='utf-8').read().replace('\r\n','\n')
    for cm in CITE.finditer(raw):
        ch,v=int(cm.group(1)),int(cm.group(2))
        if not 1<=ch<=114: continue
        win=raw[max(0,cm.start()-500):cm.start()]
        q=None
        for qm in reversed(list(QUOTE.finditer(win))):
            if CITE.search(win[qm.end():]): continue
            q=qm.group(1); break
        if not q: continue
        W=set(toks(q))
        if len(W)<4: continue
        cov=round(score(W,ch,v),3)
        ba=best_anywhere(W)
        top=ba[0] if ba else (0.0,0,0)
        ok = bool(ba) and top[1]==ch and abs(top[2]-v)<=2 and cov>=0.5
        out.append(dict(f=n,line=raw[:cm.start()].count('\n')+1,cite='%d:%d'%(ch,v),cov=cov,best=ba,quote=q[:220],ok=ok))
json.dump(out,open('os.path.join(OUT,'final.json','w'),ensure_ascii=False)
print('units:',len(out),'| cited-passage-match:',sum(1 for r in out if r['ok']),'| no match anywhere:',sum(1 for r in out if not r['best']))
sus=[r for r in out if not r['ok'] and r['best'] and r['best'][0][0]>=0.75 and r['cov']<0.4]
print('STRONG candidates:',len(sus))
for r in sus[:50]:
    b=r['best'][0]
    print('%03d:%d cited %-8s cov=%.2f  best %d:%d=%.2f | %s'%(r['f'],r['line'],r['cite'],r['cov'],b[1],b[2],b[0],r['quote'][:130].replace('\n',' ')))
