#!/usr/bin/env python3
"""Print verse text + source commentary for a verse range.

Usage: extract_source.py <sura_no> <lo> <hi>
Reads initial/<sura>.md, which holds the ground-truth translation lines
(> **N** text) and the per-verse commentary blocks (**N** ... / **N-M** ...).
"""
import re, sys

num = int(sys.argv[1])
lo, hi = int(sys.argv[2]), int(sys.argv[3])
raw = open(f"initial/{num:03d}.md", encoding="utf-8").read().replace("\r\n", "\n")
lines = raw.split("\n")

# verse translations
vt, cur = {}, None
for ln in lines:
    m = re.match(r'^> \*\*(\d+)\*\*\s*(.*)$', ln)
    if m:
        cur = int(m.group(1))
        vt[cur] = [m.group(2).strip()] if m.group(2).strip() else []
    elif re.match(r'^\*\*\d', ln) or ln.startswith(("***", "#")):
        cur = None
    elif cur and ln.strip() and not ln.startswith(">"):
        vt[cur].append(ln.strip())
vt = {k: " ".join(v).strip() for k, v in vt.items()}

# commentary blocks keyed by (start, end) verse
cm, i = {}, 0
while i < len(lines):
    m = re.match(r'^\*\*(\d+)(?:[–-](\d+))?\*\*\s*(.*)$', lines[i])
    if m:
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        buf = [m.group(3).strip()]
        i += 1
        while (i < len(lines) and lines[i].strip()
               and not re.match(r'^\*\*\d', lines[i])
               and not lines[i].startswith((">", "***", "#"))):
            buf.append(lines[i].strip())
            i += 1
        cm[(a, b)] = " ".join(buf)
    else:
        i += 1

for v in range(lo, hi + 1):
    print(f"### v{v}: {vt.get(v, '(no translation line)')}")
    for (a, b), t in sorted(cm.items()):
        if a <= v <= b:
            tag = f"{a}–{b}" if b > a else str(a)
            print(f"   [{tag}] {t}")
    print()
