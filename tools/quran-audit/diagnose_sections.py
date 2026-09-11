#!/usr/bin/env python3
"""For each verse section flagged by check_translations.py, find the best-matching
verse anywhere in initial/ + translation/, and test whether the section's own
commentary prose matches the correct verse or the substituted one.

This distinguishes:
  (a) wrong translation line only  -> commentary matches the correct verse
  (b) whole section substituted    -> commentary matches the wrong text too

Usage:
    python3 tools/quran-audit/diagnose_sections.py 11 105 106 107
    python3 tools/quran-audit/diagnose_sections.py --flagged   # all flagged
"""
import re
import os
import sys
import glob
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VERSE_HEAD = re.compile(r'^## S\u016brah .+? (\d+):(\d+)$', re.M)
TRANS_LINE = re.compile(r'^> \*\*(.+?)\*\*\s*$')


def norm(s):
    s = unicodedata.normalize('NFKC', s)
    for a, b in [('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'),
                 ('\u201d', '"'), ('\u2014', ' '), ('\u2013', ' ')]:
        s = s.replace(a, b)
    s = re.sub(r'[*_`~\u02b9\u02ba\u02f9\u02fa]', '', s)
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.U)
    return re.sub(r'\s+', ' ', s).strip().lower()


def wordset(s, minlen=3):
    return set(w for w in norm(s).split() if len(w) > minlen)


def overlap(a, b, minlen=3):
    A, B = wordset(a, minlen), wordset(b, minlen)
    if not A or not B:
        return None
    return len(A & B) / min(len(A), len(B))


def all_sources():
    """Every verse text in initial/*.md and translation/*.txt, keyed (sura, verse)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'initial', '*.md'))):
        n = int(os.path.basename(path)[:3])
        for m in re.finditer(r'^> \*\*(\d+)\*\* (.*)$',
                             open(path, encoding='utf-8').read(), re.M):
            out.setdefault((n, int(m.group(1))), []).append(
                ('initial', m.group(2)))
    for path in sorted(glob.glob(os.path.join(ROOT, 'translation', '*.txt'))):
        n = int(os.path.basename(path)[:3])
        for line in open(path, encoding='utf-8'):
            m = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', line)
            if m:
                out.setdefault((n, int(m.group(1))), []).append(
                    ('translation', m.group(2)))
    return out


def get_section(path, verse):
    """Return (translation, prose_body) for one verse section."""
    text = open(path, encoding='utf-8').read()
    heads = [(m.start(), m.end(), int(m.group(2)))
             for m in VERSE_HEAD.finditer(text)]
    for i, (_s, end, v) in enumerate(heads):
        if v != verse:
            continue
        stop = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        block = text[end:stop]
        lines = block.split('\n')
        trans = None
        for line in lines:
            if not line.strip():
                continue
            m = TRANS_LINE.match(line.strip())
            if m:
                trans = m.group(1)
            break
        prose = [l for l in lines
                 if l.strip() and not l.startswith('>')
                 and not l.strip().startswith('**')]
        return trans, ' '.join(prose)
    return None, None


def main():
    args = sys.argv[1:]
    src = all_sources()

    if '--flagged' in args:
        import subprocess
        out = subprocess.run(
            [sys.executable,
             os.path.join(ROOT, 'tools', 'quran-audit', 'check_translations.py')],
            capture_output=True, text=True).stdout
        targets = []
        for line in out.split('\n'):
            m = re.match(r'^\s+(\d{3})\.md: \d+ -> \[(.*)\]$', line)
            if m:
                n = int(m.group(1))
                for v in re.findall(r'\d+', m.group(2)):
                    targets.append((n, int(v)))
    else:
        n = int(args[0])
        targets = [(n, int(v)) for v in args[1:]]

    for n, v in targets:
        path = os.path.join(ROOT, 'expanded', '%03d.md' % n)
        trans, prose = get_section(path, v)
        if trans is None:
            print('=== %03d:%d  NO SECTION' % (n, v))
            continue

        # best match for the translation line, corpus-wide
        scored = []
        for (sn, sv), variants in src.items():
            best = max((overlap(trans, t) or 0) for _k, t in variants)
            if best:
                scored.append((best, sn, sv))
        scored.sort(reverse=True)
        top = scored[0] if scored else (0, 0, 0)

        # does the prose match the correct verse, or the substituted text?
        own_ini = dict((sv, t) for (sn, sv), vs in src.items() if sn == n
                       for k, t in vs if k == 'initial').get(v)
        prose_vs_own = overlap(prose, own_ini) if own_ini else None
        sub_text = None
        if top[0] >= 0.45 and (top[1], top[2]) != (n, v):
            sub_text = dict(src[(top[1], top[2])]).get('initial')
        prose_vs_sub = overlap(prose, sub_text) if sub_text else None

        print('=== %03d:%d' % (n, v))
        print('    exp trans : %s' % trans[:100])
        print('    best match: %03d:%d @%.2f  %s'
              % (top[1], top[2], top[0],
                 'SAME VERSE' if (top[1], top[2]) == (n, v) else '<-- SUBSTITUTED'))
        print('    prose vs own %03d:%d  : %s'
              % (n, v, 'n/a' if prose_vs_own is None else '%.2f' % prose_vs_own))
        if sub_text:
            print('    prose vs sub %03d:%d : %s'
                  % (top[1], top[2],
                     'n/a' if prose_vs_sub is None else '%.2f' % prose_vs_sub))
        verdict = 'REGISTER VARIANT' if (top[1], top[2]) == (n, v) else (
            'TRANSLATION-ONLY' if (prose_vs_own or 0) > (prose_vs_sub or 0)
            else 'WHOLE SECTION SUBSTITUTED')
        print('    verdict: %s' % verdict)


if __name__ == '__main__':
    main()
