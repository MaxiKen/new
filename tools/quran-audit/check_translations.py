#!/usr/bin/env python3
"""Check every verse section's translation in expanded/ against initial/ and translation/.

Reports sections whose translation matches NEITHER source above a threshold,
which indicates a cross-surah substitution rather than a register variant.

Usage:
    python3 tools/quran-audit/check_translations.py            # summary
    python3 tools/quran-audit/check_translations.py --verbose  # every flagged section
    python3 tools/quran-audit/check_translations.py --sura 11  # one sura
"""
import re
import os
import sys
import glob
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THRESHOLD = 0.45

VERSE_HEAD = re.compile(r'^## S\u016brah .+? (\d+):(\d+)$', re.M)
TRANS_LINE = re.compile(r'^> \*\*(.+?)\*\*\s*$')


def norm(s):
    s = unicodedata.normalize('NFKC', s)
    for a, b in [('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'),
                 ('\u201d', '"'), ('\u2014', ' '), ('\u2013', ' ')]:
        s = s.replace(a, b)
    s = re.sub(r'[*_`~\u02b9\u02ba]', '', s)
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.U)
    return re.sub(r'\s+', ' ', s).strip().lower()


def wordset(s):
    return set(w for w in norm(s).split() if len(w) > 2)


def overlap(a, b):
    """Overlap coefficient. Returns None when either side is empty."""
    A, B = wordset(a), wordset(b)
    if not A or not B:
        return None
    return len(A & B) / min(len(A), len(B))


def load_initial(n):
    path = os.path.join(ROOT, 'initial', '%03d.md' % n)
    out = {}
    if not os.path.exists(path):
        return out
    text = open(path, encoding='utf-8').read()
    for m in re.finditer(r'^> \*\*(\d+)\*\* (.*)$', text, re.M):
        out[int(m.group(1))] = m.group(2)
    return out


def load_translation(n):
    path = os.path.join(ROOT, 'translation', '%03d.txt' % n)
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', line)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def sections(path):
    """Yield (verse, translation_or_None) for each verse section."""
    text = open(path, encoding='utf-8').read()
    heads = [(m.start(), m.end(), int(m.group(2)))
             for m in VERSE_HEAD.finditer(text)]
    for i, (_start, end, verse) in enumerate(heads):
        stop = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        found = None
        for line in text[end:stop].split('\n'):
            if not line.strip():
                continue
            m = TRANS_LINE.match(line.strip())
            if m:
                found = m.group(1)
            break  # only the first non-blank line can be the translation
        yield verse, found


def main():
    verbose = '--verbose' in sys.argv
    only = None
    if '--sura' in sys.argv:
        only = int(sys.argv[sys.argv.index('--sura') + 1])

    flagged = []
    checked = no_trans = no_source = 0

    for path in sorted(glob.glob(os.path.join(ROOT, 'expanded', '*.md'))):
        name = os.path.basename(path)
        n = int(name[:3])
        if only is not None and n != only:
            continue
        ini = load_initial(n)
        trn = load_translation(n)
        for verse, got in sections(path):
            if got is None:
                no_trans += 1
                continue
            a = overlap(got, ini[verse]) if verse in ini else None
            b = overlap(got, trn[verse]) if verse in trn else None
            if a is None and b is None:
                no_source += 1
                continue
            checked += 1
            best = max(x for x in (a, b) if x is not None)
            if best < THRESHOLD:
                flagged.append((name, verse, a, b, got,
                                ini.get(verse), trn.get(verse)))

    print('checked: %d sections (no translation line: %d, no source text: %d)'
          % (checked, no_trans, no_source))
    print('flagged (<%.2f against BOTH initial/ and translation/): %d'
          % (THRESHOLD, len(flagged)))

    by_file = {}
    for name, verse, a, b, got, i, t in flagged:
        by_file.setdefault(name, []).append(verse)
    for name in sorted(by_file):
        print('  %s: %d -> %s' % (name, len(by_file[name]), by_file[name]))

    if verbose:
        print()
        for name, verse, a, b, got, i, t in flagged:
            print('=== %s v%d  initial=%s translation=%s'
                  % (name, verse,
                     'n/a' if a is None else '%.2f' % a,
                     'n/a' if b is None else '%.2f' % b))
            print('    exp: %s' % (got[:130] if got else None))
            print('    ini: %s' % (i[:130] if i else None))
            print('    trn: %s' % (t[:130] if t else None))


if __name__ == '__main__':
    main()
