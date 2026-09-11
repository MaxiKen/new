#!/usr/bin/env python3
"""Demote non-canonical H2 headings in expanded/*.md to bold mini-headings.

Canonical skeleton, from expanded/001.md (9 ATX headings total: 1 H1 + 8 H2):

    # Sūrah <name> (Chapter N) — Expanded Verse-by-Verse Commentary
    ## Introduction to the Sūrah
    ## Sūrah <name> N:1   ...   ## Sūrah <name> N:<last>

No other H2 exists in the reference. Subdivisions inside the introduction and
inside a verse section are **bold mini-headings**, per system_instructions.md
section 4: "Every major change in thought or section gets its own unique,
context-specific bold mini-heading."

Ten files carry extra H2s -- three introduction subdivisions in 004.md and eight
concluding reflections (050, 053, 071, 072, 073, 075, 094, 103). validate.py
never checked for unexpected H2s, so all ten passed the gate while diverging
from the reference skeleton.

Demotion preserves every word: only the ATX marker becomes a bold span. Content
is asserted identical before and after, modulo the heading line itself.

Usage:
    fix_headings.py --dry-run
    fix_headings.py
    fix_headings.py --sura 4
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VH = re.compile(r'^## Sūrah .+ \d+:\d+$')
INTRO = '## Introduction to the Sūrah'


def canonical(line):
    s = line.rstrip()
    return s == INTRO or bool(VH.match(s)) or s.startswith('# ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--sura', type=int)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(ROOT, 'expanded', '*.md')))
    if args.sura:
        files = [f for f in files if os.path.basename(f) == f'{args.sura:03d}.md']

    total = 0
    for f in files:
        name = os.path.basename(f)
        raw = open(f, 'rb').read()
        lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')

        targets = [i for i, l in enumerate(lines)
                   if l.startswith('## ') and not canonical(l)]
        if not targets:
            continue

        before = [l for l in lines if l.strip()]
        for i in targets:
            text = lines[i][3:].strip()
            # a heading already carrying bold markers would nest them
            text = text.replace('**', '').strip()
            lines[i] = f'**{text}**'
            print(f'  {name}:{i + 1}  "## {text}"  ->  "**{text}**"')
        after = [l for l in lines if l.strip()]

        # Guarantee: same line count, and every line identical except the
        # demoted headings, which differ only by the marker/bold wrapper.
        assert len(before) == len(after), f'{name}: line count changed'
        for b, a in zip(before, after):
            if b == a:
                continue
            assert b.startswith('## ') and a == f'**{b[3:].strip().replace("**", "").strip()}**', \
                f'{name}: unexpected edit {b[:40]!r} -> {a[:40]!r}'

        total += len(targets)
        if not args.dry_run:
            res = '\n'.join(lines)
            if not res.endswith('\n'):
                res += '\n'
            open(f, 'w', encoding='utf-8', newline='\n').write(res)

    print(f'\nnon-canonical H2 headings demoted: {total} '
          f'across {len([1 for f in files])} files scanned')
    print('(dry run -- nothing written)' if args.dry_run else '(written)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
