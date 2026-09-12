#!/usr/bin/env python3
"""Replace only the translation line of named verse sections.

Use when a section's commentary is correct but its translation line quotes a
different verse, or when a whole file's verse translations have to be brought
onto one of the repository's two reference renderings. Rewriting the whole
section would destroy good prose; this swaps the single line and leaves the
commentary untouched.

Two sources are available:

    --source initial      (default) `initial/NNN.md`, lines `> **N** text`
    --source translation  `translation/NNN.txt`, lines `N | text`

`--all` selects every verse the source carries, so a whole chapter can be put
on one rendering in a single pass.

Usage:
    python3 tools/quran-audit/fix_translation.py 40 31 48 50 63
    python3 tools/quran-audit/fix_translation.py 40 31 --dry-run
    python3 tools/quran-audit/fix_translation.py 7 --all --source translation
    python3 tools/quran-audit/fix_translation.py 7 --all --source translation --dry-run
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
    if not os.path.exists(path):
        return out
    text = open(path, encoding='utf-8').read()
    for m in re.finditer(r'^> \*\*(\d+)\*\* (.*)$', text, re.M):
        out[int(m.group(1))] = m.group(2).strip()
    return out


def load_translation(n):
    path = os.path.join(ROOT, 'translation', '%03d.txt' % n)
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', line)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


LOADERS = {'initial': load_initial, 'translation': load_translation}


def parse_args(argv):
    source, dry, take_all, positional = 'initial', False, False, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--dry-run':
            dry = True
        elif a == '--all':
            take_all = True
        elif a == '--source':
            i += 1
            source = argv[i]
        elif a.startswith('--source='):
            source = a.split('=', 1)[1]
        elif not a.startswith('--'):
            positional.append(a)
        i += 1
    if source not in LOADERS:
        raise SystemExit('unknown --source %r (use: %s)'
                         % (source, ', '.join(sorted(LOADERS))))
    if not positional:
        raise SystemExit(__doc__)
    return source, dry, take_all, positional


def main():
    source, dry, take_all, positional = parse_args(sys.argv[1:])
    n = int(positional[0])
    src = LOADERS[source](n)
    if not src:
        raise SystemExit('no source text found for sura %d (%s)' % (n, source))
    verses = sorted(src) if take_all else [int(v) for v in positional[1:]]

    path = os.path.join(ROOT, 'expanded', '%03d.md' % n)
    lines = open(path, encoding='utf-8').read().split('\n')

    # map verse -> line index of its translation line
    heads = [(i, int(m.group(2))) for i, m in
             ((i, VERSE_HEAD.match(l)) for i, l in enumerate(lines)) if m]
    changed = same = 0
    for k, (hi, verse) in enumerate(heads):
        if verse not in verses:
            continue
        if verse not in src:
            print('  v%d: NOT IN %s/%03d - skipped' % (verse, source, n))
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
        new = '> **%s**' % src[verse]
        if old == new:
            same += 1
            continue
        print('  v%d:\n    - %s\n    + %s' % (verse, old[:110], new[:110]))
        if not dry:
            lines[target] = new
        changed += 1

    if not dry and changed:
        open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print('%s %d translation line(s) in %03d.md from %s/ (%d already correct)'
          % ('would replace' if dry else 'replaced', changed, n, source, same))


if __name__ == '__main__':
    main()
