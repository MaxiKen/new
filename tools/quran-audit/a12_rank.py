#!/usr/bin/env python3
"""Rank the sections of one file by degeneracy, so rewrites can go worst-first."""
import re, sys, os, statistics
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEAD = re.compile(r'^## Sūrah .+? (\d+):(\d+)\s*$')
C1 = re.compile(r'\bis the \w+ that is\b', re.I)
C2 = re.compile(r'\bthe \w+ is the \w+ of the\b', re.I)
C3 = re.compile(r'\bof the \w+ of the\b', re.I)
C4 = re.compile(r'\bis in the form of the\b', re.I)
ch = int(sys.argv[1]); path = os.path.join(ROOT, 'expanded', '%03d.md' % ch)
lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
idx = [i for i, l in enumerate(lines) if HEAD.match(l.strip())]
rows = []
for k, i in enumerate(idx):
    e = idx[k + 1] if k + 1 < len(idx) else len(lines)
    body = '\n'.join(lines[i + 1:e]); v = int(HEAD.match(lines[i].strip()).group(2))
    w = len(body.split())
    hits = len(C1.findall(body)) + len(C2.findall(body)) + len(C3.findall(body)) + len(C4.findall(body))
    rows.append((v, w, hits, round(1000 * hits / max(1, w), 1)))
rows.sort(key=lambda r: -r[3])
print('%5s %6s %6s %8s' % ('verse', 'words', 'chains', 'per 1k'))
for r in rows[:int(sys.argv[2]) if len(sys.argv) > 2 else 25]:
    print('%5d %6d %6d %8.1f' % r)
worst = [r for r in rows if r[3] >= 5]
print('sections at >=5 chains/1k words: %d of %d' % (len(worst), len(rows)))
