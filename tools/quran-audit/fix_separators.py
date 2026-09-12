#!/usr/bin/env python3
"""Normalise horizontal rules in expanded/*.md to the canonical skeleton.

Canonical form, taken from expanded/001.md (the confirmed reference, which has
8 rules for 7 verses + 1 end marker and ZERO rules anywhere else):

    <content line>
    <blank>
    ---
    ## Sūrah <name> <n>:<v>          <- or **[End of the commentary ...]**

A ``---`` is legal in exactly one place: immediately before a verse heading or
immediately before the end marker. Every other rule is an artifact.

Two artifact classes are repaired here:

  duplicate   ``---`` blank ``---`` heading      -- normalize.py's run()
              prepends ['', '---'] to each section without checking whether the
              section body already opened with a rule.

  internal    ``---`` blank ``**Mini-Heading**`` -- normalize.py's clean()
              unglues a welded heading by inserting '\\n\\n---\\n\\n'; the heading
              is later dropped as a remnant, orphaning the rule inside the body.

Neither was caught by validate.py, which checks L[i-1] and L[i-2] relative to a
heading but never looks further back, so a duplicated rule satisfies both.

Usage:
    fix_separators.py --dry-run      # report only
    fix_separators.py                # repair in place
    fix_separators.py --sura 21      # one file
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VH = re.compile(r'^## Sūrah .+ \d+:\d+$')
ENDM = re.compile(r'^\*\*\[End of the commentary on Sūrah .+\]\*\*$')


def is_boundary(line):
    s = line.strip()
    return bool(VH.match(s) or ENDM.match(s))


def repair(lines):
    """Return (new_lines, removed_count)."""
    # Pass 1: drop every rule that is not immediately followed by a boundary.
    kept, removed = [], 0
    for i, l in enumerate(lines):
        if l.strip() in ('---', '***'):
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if not is_boundary(nxt):
                removed += 1
                continue
        kept.append(l)

    # Pass 2: collapse blank runs created by the removals (001.md has no 2+ runs).
    out = []
    for l in kept:
        if l.strip() == '' and out and out[-1].strip() == '':
            continue
        out.append(l)

    # Pass 3: guarantee exactly one blank line before each surviving rule, and
    # insert a rule if a boundary lost one.
    final = []
    for i, l in enumerate(out):
        if is_boundary(l):
            # walk back over the rule we expect to see
            if final and final[-1].strip() in ('---', '***'):
                if len(final) >= 2 and final[-2].strip() != '':
                    final.insert(-1, '')
            else:
                if final and final[-1].strip() != '':
                    final.append('')
                final.append('---')
        final.append(l)

    # Pass 4: dedupe any adjacent rules the insertion may have produced.
    ded = []
    for l in final:
        if l.strip() in ('---', '***') and ded and ded[-1].strip() in ('---', '***'):
            continue
        ded.append(l)
    return ded, removed


def audit(lines):
    """Classify every rule in a file by what follows it (blanks skipped)."""
    dup = internal = ok = 0
    for i, l in enumerate(lines):
        if l.strip() not in ('---', '***'):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        if is_boundary(nxt):
            ok += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        following = lines[j].strip() if j < len(lines) else '<EOF>'
        if following in ('---', '***'):
            dup += 1          # a second rule follows: this one is redundant
        else:
            internal += 1     # orphaned inside a section body
    return ok, dup, internal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--sura', type=int)
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(ROOT, 'expanded', '*.md')))
    if args.sura:
        files = [f for f in files if os.path.basename(f) == f'{args.sura:03d}.md']

    tot_dup = tot_int = changed = 0
    for f in files:
        name = os.path.basename(f)
        raw = open(f, 'rb').read()
        text = raw.decode('utf-8').replace('\r\n', '\n')
        lines = text.split('\n')
        trailing = lines and lines[-1] == ''
        body = lines[:-1] if trailing else lines

        ok, dup, internal = audit(body)
        if dup == 0 and internal == 0:
            continue
        tot_dup += dup
        tot_int += internal
        changed += 1

        new, removed = repair(body)
        nok, ndup, nint = audit(new)

        # Guarantee 1: no artifacts survive.
        assert ndup == 0 and nint == 0, f'{name}: repair left {ndup} dup / {nint} internal'
        # Guarantee 2: every boundary rule that existed still exists.
        assert nok == ok, f'{name}: boundary rules changed {ok} -> {nok}'
        # Guarantee 3: not one word of content is touched. Comparing only the
        # non-blank, non-rule lines makes this independent of blank collapsing.
        def content(ls):
            return [l for l in ls if l.strip() and l.strip() not in ('---', '***')]
        assert content(body) == content(new), f'{name}: CONTENT CHANGED'

        res = '\n'.join(new + ([''] if trailing else []))
        if not res.endswith('\n'):
            res += '\n'
        print(f'{name}: removed {removed} stray rules '
              f'({dup} duplicate, {internal} internal); '
              f'{len(body)} -> {len(new)} lines; {ok} boundary rules intact')
        if not args.dry_run:
            open(f, 'w', encoding='utf-8', newline='\n').write(res)

    print(f'\nfiles affected: {changed}/{len(files)}   '
          f'duplicate rules: {tot_dup}   internal rules: {tot_int}   '
          f'total removed: {tot_dup + tot_int}')
    print('(dry run -- nothing written)' if args.dry_run else '(written)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
