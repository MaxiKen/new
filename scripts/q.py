#!/usr/bin/env python3
"""q.py C:V [C:V ...] — print the authoritative translation line(s), for copying verbatim."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
cache = {}
for ref in sys.argv[1:]:
    c, v = ref.split(':')
    c, v = int(c), int(v)
    if c not in cache:
        d = {}
        for line in (ROOT / 'translation' / f'{c:03d}.txt').read_text(encoding='utf-8').splitlines():
            m = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', line)
            if m:
                d[int(m.group(1))] = m.group(2).strip()
        cache[c] = d
    print(f'({c}:{v}) {cache[c].get(v, "?? MISSING")}')
