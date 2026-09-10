#!/usr/bin/env python3
"""Detect degenerate/repetitive generated commentary and non-matching verse text."""
import re, sys, os, json, collections
VH = re.compile(r'^##\s+(?:Sūra?t?\s+)?(.*?)\s*\[?(\d+):(\d+)\]?\s*$')

def sections(path):
    lines=open(path,encoding='utf-8').read().replace('\r\n','\n').split('\n')
    idx=[(i,int(VH.match(l.rstrip()).group(2)),int(VH.match(l.rstrip()).group(3)))
         for i,l in enumerate(lines) if l.startswith('## ') and VH.match(l.rstrip())]
    out={}
    for j,(i,ch,v) in enumerate(idx):
        out[v]=(i+1, '\n'.join(lines[i: (idx[j+1][0] if j+1<len(idx) else len(lines))]))
    return out

def degen_score(text):
    """fraction of 10-gram tokens that are duplicated within the section"""
    words=re.findall(r"[\w'’\-]+", text.lower())
    if len(words)<80: return 0.0, 0
    n=10
    grams=[tuple(words[i:i+n]) for i in range(len(words)-n+1)]
    if not grams: return 0.0,0
    c=collections.Counter(grams)
    dupes=sum(v-1 for v in c.values() if v>1)
    return dupes/len(grams), dupes

if __name__=='__main__':
    res={}
    for f in sorted(os.listdir('expanded')):
        if not f.endswith('.md'): continue
        secs=sections('expanded/'+f)
        bad=[]
        for v in sorted(secs):
            ln, body = secs[v]
            sc, dupes = degen_score(body)
            if sc>0.10:
                bad.append((v, ln, round(sc,3), dupes))
        if bad: res[f]=bad
    print(json.dumps(res, ensure_ascii=False, indent=1))
