#!/usr/bin/env python3
"""Replace only the translation line of named verse sections, from initial/.

Use when a section's commentary is correct but its translation line quotes a
different verse. Rewriting the whole section would destroy good prose; this
swaps the single line and leaves the commentary untouched.

Usage:
    python3 tools/quran-audit/fix_translation.py 40 31 48 50 63
    python3 tools/quran-audit/fix_translation.py 40 31 --dry-run
"""
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERSE_HEAD = re.compile(r'^## S\u016brah .+? (\d+):(\d+)$', re.M)
TRANS_LINE = re.compile(r'^> \*\*(.+?)\*\*\s*$')


def load_initial(n):
    path = os.path.join(ROOT, 'initial', '%03d.md' % n)
    out = {}
    text = open(path, encoding='utf-8').read()
    for m in re.finditer(r'^> \*\*(\d+)\*\* (.*)$', text, re.M):
        out[int(m.group(1))] = m.group(2).strip()
    return out


def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    args = [a for a in args if not a.startswith('--')]
    n = int(args[0])
    verses = [int(v) for v in args[1:]]

    ini = load_initial(n)
    path = os.path.join(ROOT, 'expanded', '%03d.md' % n)
    lines = open(path, encoding='utf-8').read().split('\n')

    # map verse -> line index of its translation line
    heads = [(i, int(m.group(2))) for i, m in
             ((i, VERSE_HEAD.match(l)) for i, l in enumerate(lines)) if m]
    changed = 0
    for k, (hi, verse) in enumerate(heads):
        if verse not in verses:
            continue
        if verse not in ini:
            print('  v%d: NOT IN initial/%03d.md - skipped' % (verse, n))
            continue
        stop = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        target = None
        for j in range(hi + 1, stop):
            if not lines[j].strip():
                continue
            if TRANS_LINE.match(lines[j].strip()):
                target = j
            break
        if target is None:
            print('  v%d: no translation line found - skipped' % verse)
            continue
        old = lines[target]
        new = '> **%s**' % ini[verse]
        if old == new:
            print('  v%d: already correct' % verse)
            continue
        print('  v%d:\n    - %s\n    + %s' % (verse, old[:110], new[:110]))
        if not dry:
            lines[target] = new
        changed += 1

    if not dry:
        open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print('%s %d translation line(s) in %03d.md'
          % ('would replace' if dry else 'replaced', changed, n))


if __name__ == '__main__':
    main()
