#!/usr/bin/env python3
"""Locate and print the block that fix_headings.py normalised in expanded/017.md.

The 111 blocks are identified by the malformed "****Heading****" form they had
before normalisation. fix_headings.py rewrote those lines in place without
changing the line count, so positions recorded from a pre-fix copy remain valid.

Usage:
    block017.py <pre_fix_copy> <verse> [<verse> ...]   # print block + section
    block017.py <pre_fix_copy> --list                  # all blocks, one line each
"""
import re
import sys

VH = re.compile(r'^## Sūrah (.+?) (\d+):(\d+)$')
BH = re.compile(r'^\*\*')


def load(path):
    L = open(path, encoding='utf-8').read().split('\n')
    idx = [i for i, l in enumerate(L) if VH.match(l)]
    out = {}
    for k, i in enumerate(idx):
        v = int(VH.match(L[i]).group(3))
        e = idx[k + 1] if k + 1 < len(idx) else len(L)
        out[v] = (i, e, L[i:e])
    return out


def block_range(blk):
    """(start, end) offsets of the formerly-malformed block within the section."""
    m = [j for j, l in enumerate(blk) if l.startswith('****')]
    if not m:
        return None
    j = m[0]
    k = j + 1
    while k < len(blk) and not BH.match(blk[k]) and not blk[k].startswith('## '):
        k += 1
    return j, k


if __name__ == '__main__':
    pre = sys.argv[1]
    old = load(pre)
    cur = load('expanded/017.md')
    if '--list' in sys.argv:
        for v in sorted(old):
            r = block_range(old[v][2])
            if not r:
                continue
            j, k = r
            head = cur[v][2][j].strip('*').strip()
            words = len(re.findall(r"[\w'’\-]+", ' '.join(cur[v][2][j:k])))
            print(f'v{v:<4} offset {j:>3}-{k:<3} file line {cur[v][0] + j + 1:>5}  '
                  f'{words:>4} w  {head[:70]}')
    else:
        for a in sys.argv[2:]:
            v = int(a)
            r = block_range(old[v][2])
            i, e, blk = cur[v]
            j, k = r
            print(f'########## 017.md v{v}  (section file lines {i + 1}-{e}) ##########')
            print(f'--- BLOCK: offsets {j}-{k}, file lines {i + j + 1}-{i + k} ---')
            for l in blk[j:k]:
                if l.strip():
                    print(l)
            print(f'\n--- REST OF SECTION (block removed) ---')
            for l in blk[:j] + blk[k:]:
                if l.strip() and l.strip() != '---':
                    print(l)
            print()
