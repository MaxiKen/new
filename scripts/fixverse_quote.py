#!/usr/bin/env python3
"""fixverse_quote.py CHAP V — replace the first blockquote block of new/verse/CHAP_VVV.md
with the authoritative line V of translation/CHAP.txt, copied exactly."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
chap, v = sys.argv[1], int(sys.argv[2])
line = None
for ln in (ROOT / 'translation' / f'{chap}.txt').read_text(encoding='utf-8').splitlines():
    m = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', ln)
    if m and int(m.group(1)) == v:
        line = m.group(2).strip()
assert line, f'verse {v} not found'
p = ROOT / 'new' / 'verse' / f'{chap}_{v:03d}.md'
t = p.read_text(encoding='utf-8')
m = re.search(r'(?m)^(?:>.*(?:\n|$))+', t)
assert m, 'no blockquote found'
t = t[:m.start()] + '> ' + line + '\n' + t[m.end():]
p.write_text(t, encoding='utf-8')
print(f'{p.name}: blockquote set from translation/{chap}.txt line {v}')
