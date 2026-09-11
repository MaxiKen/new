#!/usr/bin/env python3
"""Strip redundant inserted blocks from expanded/017.md.

Background. Every one of 017.md's 111 sections carries exactly one block whose
heading was malformed as "****Heading****" (normalised to "**Heading**" by
fix_headings.py). The blocks were inserted as a batch by a different generator
than the rest of the file. Measured against the rest of their own section:

  * removing the block takes 017.md from 34 sections at/above the 0.030
    duplication gate to 0 -- every flag in the file is caused by these blocks;
  * block-vs-section 10-gram overlap ranges 0.05-0.31 (median 0.19), so the
    blocks are NOT wholesale copies and cannot be deleted indiscriminately.

Each candidate must therefore be justified individually. This script only acts
on verses passed explicitly, and for each one asserts that the surviving section
text is byte-identical to what it was minus the block -- so no surrounding
prose can be disturbed.

Evidence for the verses handled so far (distinctive markers = scholar names,
Qur'an citations, hadith numbers; compared case-insensitively against the rest
of the same section):

    v42   9 markers, 0 unique   block restates both readings, 21:22, 23:91,
                                dalil al-tamanu', the Throne, the created/
                                uncreated dilemma and the modern application
    v43  18 markers, 0 unique   Malik, Ibn Taymiyyah, Bukhari 6682 / Muslim
                                2694 and "cognate accusative" all already
                                present outside the block
    v44   5 markers, 1 unique   the block is a light rephrasing of the
                                paragraph at the preceding heading, down to
                                "the bird in the tree"; the one unique item is
                                the citation "Muslim 1955", preserved by fixing
                                the surviving "Abu Dawud (2550)" instead
    v52  12 markers, 0 unique   the parallel estimates (10:45, 30:55, 46:35,
                                79:46), 23:115, 40:84-85 and even the closing
                                al-Asr sentence are all already in the section
    v56   7 markers, 0 unique   the block heading is a concatenation of two
                                headings the section already has

Usage:
    fix_017_blocks.py <pre_fix_copy> <verse> [<verse> ...]
    fix_017_blocks.py <pre_fix_copy> --dry-run <verse> ...
"""
import re
import subprocess
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from block017 import load, block_range  # noqa: E402

TARGET = 'expanded/017.md'


def duprate(text, n=10):
    w = re.findall(r"[\w'’\-]+", text.lower())
    if len(w) < 80:
        return 0.0
    g = [tuple(w[i:i + n]) for i in range(len(w) - n + 1)]
    if not g:
        return 0.0
    import collections
    c = collections.Counter(g)
    return sum(v - 1 for v in c.values() if v > 1) / len(g)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    pre = args[0]
    verses = [int(a) for a in args[1:]]

    old = load(pre)
    cur = load(TARGET)
    lines = open(TARGET, encoding='utf-8').read().split('\n')

    # Work from the highest line number down so earlier offsets stay valid.
    plan = []
    for v in verses:
        r = block_range(old[v][2])
        if not r:
            print(f'  v{v}: no formerly-malformed block found -- skipped')
            continue
        j, k = r
        i = cur[v][0]
        plan.append((v, i + j, i + k, j, k))
    plan.sort(key=lambda p: -p[1])

    for v, a, b, j, k in plan:
        blk = cur[v][2]
        before = '\n'.join(blk)
        before_dr = duprate('\n'.join(l for l in blk if l.strip() != '---'))
        head = blk[j].strip('*').strip()
        words = len(re.findall(r"[\w'’\-]+", ' '.join(blk[j:k])))

        rest = blk[:j] + blk[k:]
        after_dr = duprate('\n'.join(l for l in rest if l.strip() != '---'))

        # Guarantee 1: the surviving non-blank lines are exactly the section's
        # original non-blank lines minus the block's, in the original order.
        # Nothing surrounding the block may be altered, reordered or dropped.
        orig = [l for l in blk if l.strip()]
        gone = [l for l in blk[j:k] if l.strip()]
        surv = [l for l in rest if l.strip()]
        expect = [l for l in orig if l not in gone or orig.count(l) > gone.count(l)]
        # order-preserving subtraction, done properly with a multiset walk
        pending = list(gone)
        expect = []
        for l in orig:
            if l in pending:
                pending.remove(l)
                continue
            expect.append(l)
        assert surv == expect, f'v{v}: excision disturbed surrounding content'
        # Guarantee 2: the block was the duplication source.
        assert after_dr < before_dr, \
            f'v{v}: duprate did not fall ({before_dr:.3f} -> {after_dr:.3f})'

        lines[a:b] = []
        print(f'  v{v:<4} lines {a + 1}-{b}  ({words} w)  "{head[:52]}"  '
              f'duprate {before_dr:.3f} -> {after_dr:.3f}')

    res = '\n'.join(lines)
    res = re.sub(r'\n{3,}', '\n\n', res).rstrip('\n') + '\n'
    if not dry:
        open(TARGET, 'w', encoding='utf-8', newline='\n').write(res)
    print(f'\nblocks removed: {len(plan)}   '
          f'{"(dry run -- nothing written)" if dry else "(written)"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
