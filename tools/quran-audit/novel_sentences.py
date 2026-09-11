#!/usr/bin/env python3
"""Score each sentence of a 017.md inserted block for novelty against its own section.

The 29 sections still over the 0.030 duplication gate are not degenerate prose;
each carries an inserted block that restates part of its section while also
adding material. Block-vs-section overlap runs 0.05-0.31 and the blocks hold
11,577 words with 1,129 content words found nowhere else in their section, so
bulk deletion would destroy real scholarship. The correct treatment is to remove
the block and fold its genuinely novel sentences into the heading they belong
under.

This script finds those sentences. For every sentence in a block it reports the
fraction of the sentence's content words that appear nowhere else in the same
section, plus the words themselves, so the handful worth keeping can be read
directly instead of inferred from a citation count.

Usage:
    novel_sentences.py 45            # one verse
    novel_sentences.py --all         # every section still over the gate
    novel_sentences.py --all --min 0.45
"""
import collections
import re
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from block017 import load, block_range  # noqa: E402

PRE = '/tmp/017.bak'
CUR = 'expanded/017.md'
GATE = 0.030

STOP = set("""the and that this with from they their them there which when what would
could should shall about into upon over under after before because therefore however
thus hence also both each every other others more most such only own same than then
these those been being were was are is not but for his her its he she it we you i of
in to a an as at by on or if no so up out one two may might must can cannot does did
have has had will just very much many any all some who whom whose where while""".split())


def duprate(text, n=10):
    w = re.findall(r"[\w'’\-]+", text.lower())
    if len(w) < 80:
        return 0.0
    g = [tuple(w[i:i + n]) for i in range(len(w) - n + 1)]
    c = collections.Counter(g)
    return sum(v - 1 for v in c.values() if v > 1) / len(g)


def content_words(text):
    return [w for w in re.findall(r"[a-zʿāūīṭḍṣẓḥʾ’'\-]{4,}", text.lower())
            if w not in STOP and not w.isdigit()]


def sentences(text):
    """Split on sentence boundaries, keeping Qur'an/hadith quotations intact."""
    text = re.sub(r'\s+', ' ', text.replace('> ', '')).strip()
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z*“"\'(])', text)
    return [p for p in parts if len(p.split()) >= 6]


def flagged(cur):
    out = []
    for v in sorted(cur):
        blk = cur[v][2]
        if duprate(' '.join(blk)) >= GATE:
            out.append(v)
    return out


def analyse(v, old, cur, threshold):
    j, k = block_range(old[v][2])
    blk = cur[v][2]
    ins = ' '.join(blk[j:k])
    out_vocab = set(content_words(' '.join(blk[:j] + blk[k:])))
    rows = []
    for s in sentences(ins):
        cw = content_words(s)
        if not cw:
            continue
        novel = [w for w in cw if w not in out_vocab]
        rows.append((len(novel) / len(cw), len(cw), novel, s))
    rows.sort(key=lambda r: -r[0])
    return rows, len(re.findall(r'\w+', ins))


def main():
    args = sys.argv[1:]
    threshold = 0.35
    if '--min' in args:
        i = args.index('--min')
        threshold = float(args[i + 1])
        args = args[:i] + args[i + 2:]
    old, cur = load(PRE), load(CUR)
    verses = flagged(cur) if '--all' in args else \
        [int(a) for a in args if not a.startswith('--')]
    for v in verses:
        rows, wc = analyse(v, old, cur, threshold)
        keep = [r for r in rows if r[0] >= threshold]
        print(f'\n{"=" * 100}\nv{v}  block {wc} w  sentences {len(rows)}  '
              f'at/above {threshold:.2f} novelty: {len(keep)}')
        for frac, n, novel, s in keep:
            print(f'  [{frac:.2f} {n:>2}cw] {s[:250]}')
            print(f'          novel: {", ".join(novel[:12])}')
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
