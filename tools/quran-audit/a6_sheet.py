import json,re,sys
ROOT='/home/user/new'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
TR={}
for n in range(1,115):
    d={}
    for line in open(ROOT+'/translation/%03d.txt'%n,encoding='utf-8'):
        m=re.match(r'^(\d+) \| (.*)$',line.rstrip('\n'))
        if m: d[int(m.group(1))]=m.group(2)
    TR[n]=d
recs=json.load(open('os.path.join(OUT,'final'))
sus=[r for r in recs if not r['ok'] and r['best'] and r['best'][0][0]>=0.75 and r['cov']<0.4]
print('candidates:',len(sus))
files={}
for r in sus:
    files.setdefault(r['f'],open(ROOT+'/expanded/%03d.md'%r['f'],encoding='utf-8').read().replace('\r\n','\n').split('\n'))
for r in sus[:40]:
    ch,v=[int(x) for x in r['cite'].split(':')]
    b=r['best'][0]
    L=files[r['f']]
    ctx=' '.join(L[max(0,r['line']-4):r['line']+1])[-520:]
    print('='*100)
    print('%03d.md line %d   cited %s (cov %.2f)   best %d:%d (%.2f)'%(r['f'],r['line'],r['cite'],r['cov'],b[1],b[2],b[0]))
    print('  QUOTED : %s'%r['quote'][:190].replace('\n',' '))
    print('  CITED  : %s'%TR.get(ch,{}).get(v,'<no such verse in reference>')[:230])
    print('  BEST   : %s'%TR.get(b[1],{}).get(b[2],'')[:230])
    print('  CONTEXT: ...%s'%ctx.replace('\n',' '))
