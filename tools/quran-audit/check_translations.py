#!/usr/bin/env python3
"""Content check v2: gather full blockquote block after each verse heading."""
import os, re, json, sys, unicodedata

ROOT="/home/user/new"; EXP=os.path.join(ROOT,"expanded"); INI=os.path.join(ROOT,"initial")
ARABIC = re.compile(r'[\u0600-\u06FF\u0750-\u077F]')

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    for a,b in [('’',"'"),('‘',"'"),('“','"'),('”','"'),('—',' '),('–',' '),('ـ',''),('،',','),('؛',';'),('˹','' ),('˺','')]:
        s = s.replace(a,b)
    s = re.sub(r'[*_`~]','',s)
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.U)
    return re.sub(r'\s+',' ',s).strip().lower()

def wordset(s): return [w for w in norm(s).split() if len(w)>2]
def jac(a,b):
    A,B=set(a),set(b)
    return len(A&B)/len(A|B) if A and B else 0.0
def ov(a,b):
    A,B=set(a),set(b)
    return len(A&B)/min(len(A),len(B)) if A and B else 0.0

def parse_initial(path):
    raw=open(path,encoding='utf-8').read().replace('\r\n','\n')
    verses={}; cur=None
    for ln in raw.split('\n'):
        m=re.match(r'^> \*\*(\d+)\*\*\s*(.*)$', ln)
        if m:
            cur=int(m.group(1)); verses[cur]=[m.group(2).strip()] if m.group(2).strip() else []
        elif re.match(r'^\*\*\d+\*\*\s', ln) or ln.startswith('***') or ln.startswith('#'):
            cur=None
    return {k:' '.join(v).strip() for k,v in verses.items()}

VH = re.compile(r'^##\s+(?:Sūra?t?\s+)?(.*?)\s*\[?(\d+):(\d+)\]?\s*$')
def parse_expanded(path):
    raw=open(path,encoding='utf-8').read().replace('\r\n','\n')
    lines=raw.split('\n')
    idx=[(i,int(VH.match(ln.rstrip()).group(2)),int(VH.match(ln.rstrip()).group(3)))
         for i,ln in enumerate(lines) if ln.startswith('## ') and VH.match(ln.rstrip())]
    out={}
    for j,(i,ch,v) in enumerate(idx):
        end = idx[j+1][0] if j+1<len(idx) else len(lines)
        body=lines[i+1:end]
        nb=[b for b in body if b.strip()]
        # collect leading blockquote block
        bq=[]
        for b in nb:
            if b.startswith('>'):
                bq.append(re.sub(r'^>\s?','',b).strip())
            else: break
        out[v]=(bq, '\n'.join(body))
    return out

def clean_bq(bq):
    """return (english_text, has_label, has_arabic)"""
    parts=[]
    label=False; arab=False
    for line in bq:
        t=line.strip()
        if not t: continue
        if ARABIC.search(t): arab=True; continue
        t2=re.sub(r'^\*\*(Verse Translation|Translation|Text and Translation|Verse \d+|The Verse)\*\*:?\s*','',t,flags=re.I)
        if t2!=t: label=True
        t2=re.sub(r'^\*\*(\d+)\*\*\s*','',t2)
        parts.append(t2.replace('*',''))
    return ' '.join(parts).strip(), label, arab

def main():
    nums=[int(a) for a in sys.argv[1:]] if len(sys.argv)>1 else range(1,115)
    res={}
    for num in nums:
        fn=f"{num:03d}.md"
        ini=parse_initial(os.path.join(INI,fn)); exp=parse_expanded(os.path.join(EXP,fn))
        rows=[]
        for v in sorted(exp):
            bq, body = exp[v]
            et,label,arab = clean_bq(bq)
            it = ini.get(v,'')
            if not et:
                rows.append({'v':v,'flag':'EMPTY_OR_NO_TRANSLATION','et':bq[:2],'it':it[:80],'j':0}); continue
            j=jac(wordset(et),wordset(it)); o=ov(wordset(et),wordset(it))
            best_v, best_j = v, j
            for sv,st in ini.items():
                jj=jac(wordset(et),wordset(st))
                if jj>best_j: best_j,best_v=jj,sv
            flag='ok'
            if o < 0.55 and len(wordset(it))>=6: flag='MISMATCH'
            elif best_v!=v and best_j>j+0.20: flag=f'ANCHOR_{best_v}'
            rows.append({'v':v,'flag':flag,'j':round(j,3),'o':round(o,3),'best':best_v,
                         'bj':round(best_j,3),'et':et[:95],'it':it[:95],'label':label,'arab':arab,
                         'words':len(body.split())})
        res[fn]=rows
    print(json.dumps(res,ensure_ascii=False))
main()
