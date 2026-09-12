#!/usr/bin/env python3
"""Propose replacements for inline quotations of a section's OWN verse that
still use the older `initial/` rendering rather than `translation/`.

For every matching block (>= MIN words) between the body and the old rendering
that is absent from the new rendering, the old verse and the new verse are
aligned word-by-word with difflib and the covering span of the new rendering is
proposed as the replacement. Output is a JSON list of candidates plus a
human-readable report with the carrying sentence, so each can be accepted,
edited or rejected before anything is written.

Usage:
    python3 align_own_verse.py report 7            # readable report
    python3 align_own_verse.py report 7 --json /tmp/c.json
"""
import re
import sys
import json
import difflib
import unicodedata

MIN = 4
VH = re.compile(r'^## S\u016brah .+? (\d+):(\d+)$')


def canon(s):
    s = unicodedata.normalize('NFKC', s)
    for a, b in [('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'),
                 ('\u201d', '"'), ('\u2014', ' '), ('\u2013', ' ')]:
        s = s.replace(a, b)
    s = re.sub(r'[*_`~]', ' ', s)
    s = re.sub(r'[^\w\s\']', ' ', s, flags=re.U)
    return re.sub(r'\s+', ' ', s).strip().lower()


def words(s):
    return canon(s).split()


def load_initial(n):
    d = {}
    for m in re.finditer(r'^> \*\*(\d+)\*\* (.*)$',
                         open('initial/%03d.md' % n, encoding='utf-8').read(), re.M):
        d[int(m.group(1))] = m.group(2).strip()
    return d


def load_translation(n):
    d = {}
    for line in open('translation/%03d.txt' % n, encoding='utf-8'):
        m = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', line)
        if m:
            d[int(m.group(1))] = m.group(2).strip()
    return d


def locate(span_words, raw):
    """Find the raw substring of `raw` whose canonical words start with
    span_words; returns (start, end) in raw indices or None."""
    if not span_words:
        return None
    # walk raw, tracking canonical word boundaries
    toks = [(m.start(), m.end(), canon(m.group(0))) for m in re.finditer(r"[\w'’]+", raw)]
    # canonicalise each token the same way canon() would (punctuation dropped)
    norm = []
    for s, e, t in toks:
        t2 = re.sub(r'[^\w\']', '', t).lower()
        if t2:
            norm.append((s, e, t2))
    cw = [re.sub(r'[^\w\']', '', w) for w in span_words]
    for i in range(len(norm) - len(cw) + 1):
        if [x[2] for x in norm[i:i + len(cw)]] == cw:
            return norm[i][0], norm[i + len(cw) - 1][1]
    return None


def propose(old_verse, new_verse, a, size):
    """Map old[a:a+size] onto the covering span of new_verse."""
    ow, nw = words(old_verse), words(new_verse)
    sm = difflib.SequenceMatcher(None, ow, nw, autojunk=False)
    start = end = None
    for b in sm.get_matching_blocks():
        if b.size == 0:
            continue
        o_from, o_to = b.a, b.a + b.size
        if o_to <= a or o_from >= a + size:
            continue
        n_from, n_to = b.b, b.b + b.size
        start = n_from if start is None else min(start, n_from)
        end = n_to if end is None else max(end, n_to)
    if start is None:
        return None
    # expand to raw spans in the new verse
    toks = [(m.start(), m.end()) for m in re.finditer(r"\S+", new_verse)]
    # count only word-ish tokens to index nw consistently
    wt = [(m.start(), m.end()) for m in re.finditer(r"[\w'’˹˺]+", new_verse)]
    if len(wt) < end:
        return None
    return new_verse[wt[start][0]:wt[end - 1][1]]


def main():
    cmd = sys.argv[1]
    n = int(sys.argv[2])
    out_json = None
    if '--json' in sys.argv:
        out_json = sys.argv[sys.argv.index('--json') + 1]
    ini, trn = load_initial(n), load_translation(n)
    lines = open('expanded/%03d.md' % n, encoding='utf-8').read().split('\n')
    idx = [i for i, l in enumerate(lines) if VH.match(l)]
    cands = []
    for k, i in enumerate(idx):
        v = int(VH.match(lines[i]).group(2))
        end = idx[k + 1] if k + 1 < len(idx) else len(lines)
        body = '\n'.join(lines[i + 5:end])
        old, new = ini.get(v, ''), trn[v]
        ow, bw, nw = words(old), words(body), words(new)
        nws = ' '.join(nw)
        sm = difflib.SequenceMatcher(None, ow, bw, autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size >= MIN]
        # words the older rendering has that the repository wording does not:
        # the archaic fingerprint (thee, unto, therein, raiment, haply ...). A
        # block is only a register drift if it carries one of them, otherwise it
        # is a phrase both renderings happen to share.
        nset = set(nw)
        merged = []
        for b in blocks:
            span = ' '.join(ow[b.a:b.a + b.size])
            if span in nws:
                continue
            if not any(w not in nset for w in ow[b.a:b.a + b.size]):
                continue
            # merge only when the blocks are contiguous in BOTH the old verse
            # and the body -- blocks that merely abut in the old verse can sit
            # in different paragraphs of the commentary and are separate quotes.
            if merged and b.a == merged[-1]['a'] + merged[-1]['size'] \
                    and b.b == merged[-1]['b'] + merged[-1]['size']:
                m = merged[-1]
                m['size'] += b.size
                m['span'] = ' '.join(ow[m['a']:m['a'] + m['size']])
            else:
                merged.append({'a': b.a, 'b': b.b, 'size': b.size, 'span': span})
        for m in merged:
            loc = locate(m['span'].split(), body)
            raw_old = body[loc[0]:loc[1]] if loc else m['span']
            prop = propose(old, new, m['a'], m['size'])
            ctx = sent = ''
            if loc:
                s = body.rfind('\n', 0, loc[0]) + 1
                e = body.find('\n', loc[1])
                ctx = body[s:e if e > 0 else len(body)].strip()
                para = body[s:e if e > 0 else len(body)]
                a, b = loc[0] - s, loc[1] - s
                st = max([para.rfind(t, 0, a) + 1 for t in ('. ', '? ', '! ', '\n')] or [0])
                en = min([x for x in (para.find(t, b) for t in ('. ', '? ', '! '))
                          if x != -1] or [len(para)])
                sent = para[st:en + 1].strip()
            cands.append({'verse': v, 'size': m['size'], 'span': m['span'],
                          'raw': raw_old, 'proposal': prop, 'context': ctx,
                          'sentence': sent,
                          'old_verse': old, 'new_verse': new})
    if out_json:
        json.dump(cands, open(out_json, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('wrote %d candidates to %s' % (len(cands), out_json))
    seen = set()
    for c in cands:
        if c['verse'] in seen:
            print()
        else:
            print('\n=== %d:%d' % (n, c['verse']))
            seen.add(c['verse'])
        print('  OLD (%dw): %s' % (c['size'], c['raw']))
        print('  NEW      : %s' % c['proposal'])
        print('  ctx      : %s' % (c['context'][:400] or '<whole-verse quote>'))
    print('\nsections: %d   candidates: %d' % (len(seen), len(cands)))


main()
