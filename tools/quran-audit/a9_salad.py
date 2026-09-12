import re,os,glob,collections,sys,json
sys.path.insert(0,'/home/user/new/tools/quran-audit/')
from stop import STOP
ROOT='/home/user/new'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
VH=re.compile(r'^## Sūrah (.+?) (\d+):(\d+)\s*$')
def paragraphs(text):
    for para in re.split(r'\n\s*\n',text):
        yield para
def content_words(s):
    s=re.sub(r'[*_`>#]','',s); s=re.sub(r'[^\w\s]',' ',s,flags=re.U)
    return [w.lower() for w in s.split() if len(w)>=4 and w.lower() not in STOP and not re.search(r'[\u0600-\u06ff]',w)]
results=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    txt=open(p,encoding='utf-8').read().replace('\r\n','\n')
    lines=txt.split('\n')
    heads=[i for i,l in enumerate(lines) if VH.match(l.strip())]
    # per section
    for k,i in enumerate(heads):
        e=heads[k+1] if k+1<len(heads) else len(lines)
        v=VH.match(lines[i].strip()).group(3)
        body='\n'.join(lines[i+1:e])
        for para in paragraphs(body):
            if para.strip().startswith('>') or para.strip().startswith('#') or para.strip().startswith('---'): continue
            w=content_words(para)
            if len(w)<90: continue
            ttr=len(set(w))/len(w)
            # chain pattern: "is the form of", "the word that is the", "of the ... of the"
            chain=len(re.findall(r'\b(?:is|are|was|were)\s+the\s+\w+\s+(?:of|that)\b',para))
            oft=len(re.findall(r'\bof the \w+ of the\b',para))
            the=len(re.findall(r'\bthe\b',para))
            score=chain+oft
            if ttr<0.40 or score>=6:
                results.append(dict(f=n,v=int(v),ttr=round(ttr,2),chain=chain,oft=oft,the=the,words=len(w),
                                    snippet=para.strip()[:150].replace('\n',' ')))
results.sort(key=lambda r:(r['ttr'],-r['chain']))
json.dump(results,open('os.path.join(OUT,'salad.json','w'),ensure_ascii=False)
print('flagged paragraphs (low lexical diversity or chain-garble):',len(results))
print('by file:')
c=collections.Counter(r['f'] for r in results)
for f,n in sorted(c.items()): print('   %03d.md  %d paragraphs'%(f,n))
print('\n--- 25 worst ---')
for r in sorted(results,key=lambda r:r['ttr'])[:25]:
    print('%03d.md v%s ttr=%.2f chain=%d of-the=%d the=%d | %s'%(r['f'],r['v'],r['ttr'],r['chain'],r['oft'],r['the'],r['snippet']))
