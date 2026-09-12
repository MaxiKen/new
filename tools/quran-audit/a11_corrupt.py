import re,os,glob,collections,json
ROOT='/home/user/new'
VH=re.compile(r'^## Sūrah (.+?) (\d+):(\d+)\s*$')
PATS={
 'glitch_?$':re.compile(r'[A-Za-zʿʾāīū\u02be\u02bf]\?[\$\?]?'),
 'dollar':re.compile(r'\$'),
 'stray_caret':re.compile(r'\^'),
 'unbalanced_bold':None,
 'placeholder':re.compile(r'\b(TODO|TBD|FIXME|XX+|placeholder|\[insert|Lorem)\b',re.I),
 'double_space':re.compile(r'\S  \S'),
 'orphan_asterisk':re.compile(r'(?<!\*)\*(?!\*)[^*\n]{0,3}(?<!\*)\*(?!\*)'),
 'note_style':re.compile(r'\b(First clause|Second clause|Third clause|Qur\'an responds|Hadith:)\b'),
 'meta_leak':re.compile(r'\b(the source commentary|the source notes|the source lists|our source|the source records)\b',re.I),
 'as_we_will_see':re.compile(r'\b(as we (?:will|shall) (?:see|discuss)|we will (?:see|come to))\b',re.I),
}
counts=collections.Counter(); byfile=collections.Counter(); ex=collections.defaultdict(list)
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    txt=open(p,encoding='utf-8').read()
    for k,rx in PATS.items():
        if rx is None: continue
        hits=rx.findall(txt)
        if hits:
            counts[k]+=len(hits); byfile[(k,n)]+=len(hits)
            if len(ex[k])<4: ex[k].append((n,hits[:4]))
print('--- corruption / artifact markers corpus-wide ---')
for k,v in counts.most_common(): print('  %-16s %6d   e.g. %s'%(k,v,str(ex[k][:3])[:150]))
print('\n--- files with glitch markers (top) ---')
gl=sorted([(v,k) for k,v in byfile.items() if k[0]=='glitch_?$'],reverse=True)[:12]
for v,k in gl: print('   %03d.md  %d'%(k[1],v))
print('\n--- meta-leak ("the source commentary/notes...") per file top 12 ---')
ml=sorted([(v,k) for k,v in byfile.items() if k[0]=='meta_leak'],reverse=True)[:12]
for v,k in ml: print('   %03d.md  %d'%(k[1],v))
# unbalanced bold per section
print('\n--- markdown integrity ---')
bad=0; badq=0; badec=0
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    lines=open(p,encoding='utf-8').read().replace('\r\n','\n').split('\n')
    heads=[i for i,l in enumerate(lines) if VH.match(l.strip())]
    for k,i in enumerate(heads):
        e=heads[k+1] if k+1<len(heads) else len(lines)
        b='\n'.join(lines[i+1:e])
        if b.count('**')%2: bad+=1
        if b.count('"')%2: badq+=1
        if '**Expanded Commentary**' not in b: badec+=1
print('  sections with odd number of ** :',bad)
print('  sections with odd number of straight quotes:',badq)
print('  sections missing "**Expanded Commentary**":',badec)
