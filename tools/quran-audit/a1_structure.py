import re, os, glob, collections
ROOT='/home/user/new'
VH=re.compile(r'^## Sūrah (.+?) (\d+):(\d+)\s*$')
rows=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    txt=open(p,encoding='utf-8').read()
    lines=txt.split('\n')
    heads=[(i,m.group(1),int(m.group(2)),int(m.group(3))) for i,l in enumerate(lines) for m in [VH.match(l.strip())] if m]
    # reference count
    ref=sum(1 for _ in open(ROOT+'/translation/%03d.txt'%n,encoding='utf-8'))
    verses=[h[3] for h in heads]
    surahs=set(h[2] for h in heads)
    names=collections.Counter(h[1] for h in heads)
    issues=[]
    if surahs!={n}: issues.append('heading chapter numbers %s != file %d'%(sorted(surahs),n))
    if len(names)>1: issues.append('multiple surah names: %s'%names.most_common())
    if verses!=list(range(1,len(verses)+1)):
        miss=[v for v in range(1,max(verses)+1) if v not in set(verses)]
        dups=[v for v,c in collections.Counter(verses).items() if c>1]
        ooo = verses!=sorted(verses)
        issues.append('verse seq bad: missing=%s dups=%s out_of_order=%s last=%s'%(miss[:20],dups[:20],ooo,max(verses)))
    if len(verses)!=ref: issues.append('verse count %d vs reference %d'%(len(verses),ref))
    # marker checks
    ec=txt.count('**Expanded Commentary**')
    tq=len(re.findall(r'^> \*\*.+\*\*\s*$',txt,re.M))
    # the sūrah introduction legitimately carries one extra **Expanded Commentary** marker
    if ec not in (len(heads), len(heads)+1): issues.append('Expanded Commentary markers %d vs sections %d'%(ec,len(heads)))
    if tq<len(heads): issues.append('blockquote translation lines %d vs sections %d'%(tq,len(heads)))
    if 'Sūrah' not in names: pass
    rows.append((n,len(heads),ref,names.most_common(1)[0][0],issues))
print('file sec ref name issues')
bad=0
for n,s,r,name,iss in rows:
    if iss:
        bad+=1
        print('%03d %4d %4d %-28s %s'%(n,s,r,name,'; '.join(iss)))
print('files with structural issues:',bad,'of',len(rows))
