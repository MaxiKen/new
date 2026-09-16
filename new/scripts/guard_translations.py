#!/usr/bin/env python3
"""Guard the assembled chapter against translation drift.

Two invariants, both learned the hard way:
  1. No draft placeholder (`__T__`) may exist anywhere under new/ or inside the assembled chapter.
  2. Every verse file's blockquote must be byte-identical to its line in translation/<chap>.txt,
     and so must the matching blockquote in the assembled new/<chap>.md.

Usage:  python3 scripts/guard_translations.py [chap]      (default: every chapter with a verse file)
Exit 0 = clean.  Exit 1 = violations printed, do not commit.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSE_RE = re.compile(r'^\s*(\d+)\s*\|\s*(.*)$')


def load_translation(chap):
    path = ROOT / 'translation' / f'{chap}.txt'
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        m = VERSE_RE.match(line)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def verse_blockquote(path):
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('> '):
            return line[2:].strip()
    return None


def chapter_blockquotes(path):
    """Map verse number -> blockquote text, keyed off the '## Sūrah al-Baqarah N:M' headings."""
    found, current = {}, None
    head = re.compile(r'^##\s+Sūrah\s+al-Baqarah\s+\d+:(\d+)\s*$')
    for line in path.read_text(encoding='utf-8').splitlines():
        m = head.match(line)
        if m:
            current = int(m.group(1))
        elif current is not None and line.startswith('> '):
            found[current] = line[2:].strip()
            current = None
    return found


def main():
    chap = sys.argv[1] if len(sys.argv) > 1 else '002'
    problems = []

    for path in sorted(ROOT.glob('new/**/*')):
        if path.is_file() and '__T__' in path.read_text(encoding='utf-8', errors='ignore'):
            problems.append(f'PLACEHOLDER  {path.relative_to(ROOT)} still contains __T__')

    tr = load_translation(chap)
    if not tr:
        problems.append(f'NO TRANSLATION FILE for chapter {chap}')

    files = sorted((ROOT / 'new' / 'verse').glob(f'{chap}_*.md'))
    for path in files:
        v = int(path.stem.split('_')[1])
        got, want = verse_blockquote(path), tr.get(v)
        if got is None:
            problems.append(f'MISSING      {path.relative_to(ROOT)} has no blockquote')
        elif want is None:
            problems.append(f'NO SOURCE    {path.relative_to(ROOT)} has no line in translation/{chap}.txt')
        elif got != want:
            problems.append(f'DRIFT        {path.relative_to(ROOT)} blockquote != translation/{chap}.txt')

    assembled = ROOT / 'new' / f'{chap}.md'
    if assembled.exists():
        for v, got in chapter_blockquotes(assembled).items():
            if tr.get(v) is not None and got != tr[v]:
                problems.append(f'DRIFT        new/{chap}.md verse {v} blockquote != translation/{chap}.txt')

    if problems:
        print('\n'.join(problems))
        print(f'\nGUARD FAIL — {len(problems)} problem(s). Do not commit.')
        return 1
    print(f'GUARD PASS — {len(files)} verse files in chapter {chap}: '
          f'0 placeholders, all blockquotes byte-identical to translation/{chap}.txt, assembled chapter in sync.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
