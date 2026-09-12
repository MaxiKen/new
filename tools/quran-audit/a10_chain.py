import re,os,glob,collections
ROOT='/home/user/new'
VH=re.compile(r'^## Sūrah (.+?) (\d+):(\d+)\s*$')
RX1=re.compile(r'\bis the \w+ that is\b',re.I)
RX2=re.compile(r'\bof the \w+ of the\b',re.I)
RX3=re.compile(r'\bthe \w+ is the \w+ of the\b',re.I)
rows=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    txt=open(p,encoding='utf-8').read()
    w=len(txt.split())
    a,b,c=len(RX1.findall(txt)),len(RX2.findall(txt)),len(RX3.findall(txt))
    rows.append((n,w,a,b,c,(a*3+b*2+c*3)/(w/1000)))
rows.sort(key=lambda r:-r[5])
print('%-8s %8s %6s %6s %6s %10s'%('file','words','is-the','of-the','the-X-is','score/1k'))
for r in rows[:18]: print('%03d.md  %8d %6d %6d %6d %10.1f'%r)
print('...')
for r in rows[-5:]: print('%03d.md  %8d %6d %6d %6d %10.1f'%r)
tot=sum(r[2] for r in rows)
print('\ncorpus totals: "is the X that is" =',tot,'; "of the X of the" =',sum(r[3] for r in rows),'; "the X is the Y of the" =',sum(r[4] for r in rows))
# how many sections of 007 are affected
txt=open(ROOT+'/expanded/007.md',encoding='utf-8').read().replace('\r\n','\n')
lines=txt.split('\n'); heads=[i for i,l in enumerate(lines) if VH.match(l.strip())]
aff=[];tot_w=0;aff_w=0
for k,i in enumerate(heads):
    e=heads[k+1] if k+1<len(heads) else len(lines)
    body='\n'.join(lines[i+1:e]); 
    v=VH.match(lines[i].strip()).group(3)
    hits=len(RX1.findall(body))+len(RX3.findall(body))
    tot_w+=len(body.split())
    if hits>=5: aff.append((int(v),hits,len(body.split())))
    if hits>=5: aff_w+=len(body.split())
print('\n007.md: sections with >=5 chain-patterns: %d of %d; affected words %d of %d (%.0f%%)'%(len(aff),len(heads),aff_w,tot_w,100*aff_w/tot_w))
print('first affected verse:',aff[0][0],'last:',aff[-1][0])
print('verses affected (first 60):',[a[0] for a in aff][:60])
