import re, sys
VH = re.compile(r'^##\s+(?:Sūra?t?\s+)?(.*?)\s*\[?(\d+):(\d+)\]?\s*$')
def sections(path):
    lines=open(path,encoding='utf-8').read().replace('\r\n','\n').split('\n')
    idx=[(i,int(VH.match(l.rstrip()).group(2)),int(VH.match(l.rstrip()).group(3)))
         for i,l in enumerate(lines) if l.startswith('## ') and VH.match(l.rstrip())]
    out={}
    for j,(i,ch,v) in enumerate(idx):
        out[v]=(i+1, lines[i: (idx[j+1][0] if j+1<len(idx) else len(lines))])
    return out
if __name__=='__main__':
    secs=sections(sys.argv[1])
    for v in [int(x) for x in sys.argv[2:]]:
        ln, body = secs.get(v, (None,['MISSING']))
        print(f"########## {sys.argv[1]} v{v}  (starts line {ln}) ##########")
        for b in body[:12]: print(b[:300])
        print(f"... ({len(body)} lines total)")
        print()
