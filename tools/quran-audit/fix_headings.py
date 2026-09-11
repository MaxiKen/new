#!/usr/bin/env python3
"""Normalise heading forms in expanded/*.md to the canonical skeleton.

Two classes are repaired:

  non-canonical H2  -> demoted to a bold mini-heading
  "****Heading****"  -> "**Heading**"   (malformed bold mini-heading)

Exactly three leading asterisks ("***Term*: the rest**") is LEFT ALONE: it is
valid bold opening with a nested italic, and occurs legitimately in 026.md and
040.md.

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

# A bold mini-heading is **Text**. Four or more leading asterisks is malformed:
# "****Text****" does not reliably render as bold and diverges from the
# canonical form. Exactly three leading asterisks is legitimate -- "***Term*:
# the rest**" is bold opening with a nested italic, as in 026.md and 040.md --
# so it must not be rewritten.
MALFORMED = re.compile(r'^\*{4,}([^*].*?[^*])\*{4,}$')


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
    files_scanned = len(files)
    for f in files:
        name = os.path.basename(f)
        raw = open(f, 'rb').read()
        lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')

        targets = [i for i, l in enumerate(lines)
                   if l.startswith('## ') and not canonical(l)]
        malformed = [(i, MALFORMED.match(l.rstrip('\n')))
                     for i, l in enumerate(lines)]
        malformed = [(i, m) for i, m in malformed if m]

        if not targets and not malformed:
            continue

        before = [l for l in lines if l.strip()]
        for i in targets:
            text = lines[i][3:].strip()
            # a heading already carrying bold markers would nest them
            text = text.replace('**', '').strip()
            lines[i] = f'**{text}**'
            print(f'  {name}:{i + 1}  "## {text}"  ->  "**{text}**"')
        for i, m in malformed:
            text = m.group(1).strip()
            lines[i] = f'**{text}**'
            print(f'  {name}:{i + 1}  "****{text[:48]}****"  ->  "**{text[:50]}**"')
        after = [l for l in lines if l.strip()]

        # Guarantee: same line count, and every line identical except the
        # demoted/normalised headings, which differ only by their markers.
        assert len(before) == len(after), f'{name}: line count changed'
        for b, a in zip(before, after):
            if b == a:
                continue
            if b.startswith('## '):
                assert a == f'**{b[3:].strip().replace("**", "").strip()}**', \
                    f'{name}: unexpected edit {b[:40]!r} -> {a[:40]!r}'
            else:
                mm = MALFORMED.match(b)
                assert mm and a == f'**{mm.group(1).strip()}**', \
                    f'{name}: unexpected edit {b[:40]!r} -> {a[:40]!r}'

        total += len(targets) + len(malformed)
        if not args.dry_run:
            res = '\n'.join(lines)
            if not res.endswith('\n'):
                res += '\n'
            open(f, 'w', encoding='utf-8', newline='\n').write(res)

    print(f'\nheadings normalised: {total}  ({files_scanned} files scanned)')
    print('(dry run -- nothing written)' if args.dry_run else '(written)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
