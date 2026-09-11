#!/usr/bin/env python3
"""Remove orphaned bare-word connector lines between two blockquotes.

Defect class (Group I, previously undetected). Four places in the corpus carry a
single short word -- in every case "and" -- sitting on its own line between two
blockquoted sources:

    > *"And never would We punish until We sent a messenger."* (Qur'an 17:15)

    and

    > *"...so that mankind would have no argument against God..."* (Qur'an 4:165)

The word is a remnant of a lead-in that was reduced to nothing but its
conjunction, leaving an orphan that renders as a stray paragraph.

Repair: drop the orphan line and the blank that follows it, so the two
quotations sit adjacent. That is the corpus norm -- 2,761 adjacent blockquote
pairs across 86 files, against 4 of these orphans. The pairing itself already
carries the corroboration; no words are lost that the surrounding prose depends
on.

Scope is deliberately narrow. Short lines ending in a colon ("and:", "God
says:", "Of belief:") are valid lead-ins and are left alone, as is any connector
of more than three words.

Usage:
    fix_orphan_connectors.py            # scan and report
    fix_orphan_connectors.py --apply    # scan, repair, report
"""
import glob
import os
import re
import sys

WORD = re.compile(r'^[A-Za-zʿ’\-\']{1,3}$')


def find(lines):
    """Return indices of orphan connector lines: quote / blank / WORD / blank / quote."""
    out = []
    for i in range(2, len(lines) - 2):
        s = lines[i].strip()
        if not WORD.match(s):
            continue
        if lines[i - 1].strip() or lines[i + 1].strip():
            continue
        if not lines[i - 2].startswith('> ') or not lines[i + 2].startswith('> '):
            continue
        out.append(i)
    return out


def main():
    apply_fix = '--apply' in sys.argv
    total = 0
    files = 0
    for path in sorted(glob.glob('expanded/*.md')):
        lines = open(path, encoding='utf-8').read().split('\n')
        bad = find(lines)
        if not bad:
            continue
        files += 1
        total += len(bad)
        for i in bad:
            print(f'  {os.path.basename(path):<10} L{i + 1:<6} {lines[i].strip()!r}')
        if apply_fix:
            for i in sorted(bad, reverse=True):
                del lines[i:i + 2]          # orphan + following blank
            txt = '\n'.join(lines)
            txt = re.sub(r'\n{3,}', '\n\n', txt).rstrip('\n') + '\n'
            open(path, 'w', encoding='utf-8', newline='\n').write(txt)
    print(f'\norphan connectors: {total} in {files} files   '
          f'{"(repaired)" if apply_fix else "(scan only -- pass --apply to repair)"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
