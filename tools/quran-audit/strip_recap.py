#!/usr/bin/env python3
"""Find and remove recapitulation blocks: mini-heading blocks that restate
their own section.

This is the defect class that 017.md carried and that Group H closed by block
removal (REMAINING_ISSUES.md H2/H5a). It is NOT the 007.md defect -- 007.md
carried machine-generated nominalisations that recurse within a sentence, which
repair_degen.py handles. A file can be checked for which defect it has: if
repair_degen.py --dry-run reports actions={'keep': N} with nothing stripped,
the duplication is structural, not sentential, and this is the tool to use.

A recap block is a mini-heading block whose content substantially restates
other blocks in the same section. It typically sits near the end, often
re-quoting blockquoted verses already quoted above it, and often under a
heading that paraphrases an earlier heading.

novel_sentences.py did this for 017.md by diffing against a pre-insertion
backup (/tmp/017.bak). No such backup exists for the other files, so this tool
identifies recap blocks by intra-section overlap instead, which needs no
history.

Removal is deliberately conservative and measured, not guessed. For each
flagged section the tool removes the smallest set of highest-overlap blocks
that (a) brings the section's 10-gram duprate under the gate and (b) leaves at
least MIN_WORDS words, so a duplication defect is never traded for a depth
defect. Before deleting a block it reports the block's novel sentences --
content found nowhere else in the section -- so anything worth keeping can be
folded into the heading it belongs under rather than lost.

Usage:
    strip_recap.py --sura 25 --dry-run          # report candidates
    strip_recap.py --sura 25 --dry-run 53       # one verse, full detail
    strip_recap.py --sura 25 --apply [verses]   # write
    strip_recap.py --sura 25 --classify         # overlap table, no removal plan
"""
import collections
import re
import sys

GATE = 0.030
MIN_WORDS = 400
NGRAM_DUP = 10          # matches census.py
NGRAM_OVL = 5           # content-word shingles for block-vs-block overlap
OVERLAP_MIN = 0.30      # a block this redundant is a recap candidate

MARKER = '**Expanded Commentary**'
WORDS = re.compile(r"[^\s]+")
CONTENT = re.compile(r"[a-zʾāīūṭṣḥḍẓʿğçş]+")
STOP = set("""the a an of and to in is that it for with as on be by not from
this these those are was were his her its their they he she we you your our
which who whom what when where how all any no nor only very also such than
then there here but or if so do does did done have has had being been one two
""".split())


def duprate(text, n=NGRAM_DUP):
    """Fraction of n-gram positions that duplicate an earlier position.

    Same metric as census.py and check_degeneracy.py, so a section reported
    clean here is clean under the gate.
    """
    toks = re.findall(r"\S+", text.lower())
    if len(toks) < n:
        return 0.0, len(toks)
    seen, dup = set(), 0
    for i in range(len(toks) - n + 1):
        g = tuple(toks[i:i + n])
        if g in seen:
            dup += 1
        seen.add(g)
    return dup / (len(toks) - n + 1), len(toks)


def shingles(text, n=NGRAM_OVL):
    w = [x for x in CONTENT.findall(text.lower()) if x not in STOP and len(x) > 2]
    return {tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}, len(w)


def sentences(text):
    # A period may be followed by up to two closing marks before the space.
    # Each lookbehind must be individually fixed-width, so the alternation is
    # placed outside them rather than inside one lookbehind.
    parts = re.split(
        r'(?:(?<=[.!?])|(?<=[.!?]["\'”’)\*])|(?<=[.!?]["\'”’)\*]{2}))\s+',
        text)
    return [p.strip() for p in parts if p.strip()]


def load_sections(path):
    """-> {verse: (line_start, [(heading, body, line_start), ...], raw_text)}"""
    raw = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    lines = raw.split('\n')
    out, cur, blocks, blines = {}, None, [], []
    surare = re.compile(r'^##\s+Sūrah\s+.+?(\d+):(\d+)\s*$')
    for i, ln in enumerate(lines):
        m = surare.match(ln)
        if m:
            if cur is not None:
                out[cur] = (start, blocks, '\n'.join(blines))
            cur = int(m.group(2))
            start, blocks, blines = i, [], [ln]
            continue
        if cur is None:
            continue
        blines.append(ln)
        h = re.match(r'^\*\*(.+?)\*\*\s*$', ln)
        if h and h.group(1).strip() != 'Expanded Commentary':
            blocks.append([h.group(1).strip(), '', i])
        elif blocks:
            blocks[-1][1] += ln + '\n'
    if cur is not None:
        out[cur] = (start, blocks, '\n'.join(blines))
    return out, lines


def analyse(blocks):
    """Overlap of each block against the union of the others."""
    sh = [shingles(b[1])[0] for b in blocks]
    res = []
    for i in range(len(blocks)):
        if not sh[i]:
            res.append(0.0)
            continue
        other = set()
        for j in range(len(blocks)):
            if j != i:
                other |= sh[j]
        res.append(len(sh[i] & other) / len(sh[i]))
    return res


def novel_report(body, others):
    """Sentences in body holding content words found nowhere else in section."""
    oc = set()
    for t in others:
        oc |= {w for w in CONTENT.findall(t.lower()) if w not in STOP and len(w) > 3}
    rows = []
    for s in sentences(body):
        cw = [w for w in CONTENT.findall(s.lower()) if w not in STOP and len(w) > 3]
        if not cw:
            continue
        novel = [w for w in cw if w not in oc]
        if novel:
            rows.append((len(novel) / len(cw), sorted(set(novel)), s))
    rows.sort(reverse=True)
    return rows


def plan(blocks, threshold=GATE, min_words=MIN_WORDS):
    """Smallest set of highest-overlap blocks whose removal clears the gate."""
    full = '\n'.join(b[1] for b in blocks)
    base, _ = duprate(full)
    if base < threshold:
        return base, base, [], len(WORDS.findall(full))
    ov = analyse(blocks)
    order = sorted(range(len(blocks)), key=lambda i: -ov[i])
    drop, cur = [], base
    for i in order:
        if ov[i] < OVERLAP_MIN:
            break
        trial = drop + [i]
        txt = '\n'.join(b[1] for j, b in enumerate(blocks) if j not in trial)
        d, _ = duprate(txt)
        w = len(WORDS.findall(txt))
        if w < min_words:
            continue
        drop = trial
        cur = d
        if d < threshold:
            break
    drop.sort()
    return base, cur, drop, len(WORDS.findall(full))


def rebuild(lines, blocks, drop, verse):
    """Delete the dropped blocks' heading + body lines."""
    kill = set()
    for i in drop:
        s = blocks[i][2]
        e = blocks[i + 1][2] if i + 1 < len(blocks) else None
        kill.add(s)
        if e is None:
            # last block: run to the section's trailing separator
            j = s + 1
            while j < len(lines) and not lines[j].startswith('## Sūrah'):
                if lines[j].strip() == '---':
                    break
                kill.add(j)
                j += 1
        else:
            for j in range(s, e):
                kill.add(j)
    out = [ln for i, ln in enumerate(lines) if i not in kill]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)) + '\n'


def main():
    a = sys.argv[1:]
    sura = 7
    if '--sura' in a:
        i = a.index('--sura')
        sura = int(a[i + 1])
        # the sura number must not be mistaken for a verse number
        del a[i:i + 2]
    path = f'expanded/{sura:03d}.md'
    verses = [int(x) for x in a if x.isdigit()]
    secs, lines = load_sections(path)

    if '--classify' in a:
        print(f'{path}  --classify')
        for v in verses or sorted(secs):
            if v not in secs:
                continue
            _, blocks, _ = secs[v]
            if len(blocks) < 2:
                continue
            d, _ = duprate('\n'.join(b[1] for b in blocks))
            if d < GATE and not verses:
                continue
            ov = analyse(blocks)
            print(f'  v{v}  duprate {d:.3f}  {len(blocks)} blocks')
            for i, (h, b, _) in enumerate(blocks):
                mark = ' RECAP?' if ov[i] >= OVERLAP_MIN else ''
                print(f'      blk{i} {ov[i]:5.0%} {len(WORDS.findall(b)):5d}w  {h[:56]}{mark}')
        return 0

    apply_ = '--apply' in a
    tot_drop = tot_before = tot_after = 0
    cleared = still = thin = 0
    for v in verses or sorted(secs):
        if v not in secs:
            continue
        _, blocks, _ = secs[v]
        if len(blocks) < 2:
            continue
        before, after, drop, wc = plan(blocks)
        if before < GATE:
            continue
        tot_before += 1
        if not drop:
            still += 1
            print(f'v{v}: NO SAFE REMOVAL (duprate {before:.3f}, {wc}w) -- needs authoring')
            continue
        if after >= GATE:
            still += 1
            tag = f'best {after:.3f}'
        else:
            cleared += 1
            tag = f'{before:.3f} -> {after:.3f}  CLEARS'
        kept = wc - sum(len(WORDS.findall(blocks[i][1])) for i in drop)
        if kept < MIN_WORDS:
            thin += 1
        print(f'v{v}: {tag}  drop {len(drop)} blk, {wc}w -> {kept}w')
        for i in drop:
            h, b, _ = blocks[i]
            others = [blocks[j][1] for j in range(len(blocks)) if j != i]
            print(f'    - blk{i} "{h}" ({len(WORDS.findall(b))}w)')
            for frac, novel, s in novel_report(b, others)[:3]:
                print(f'        novel {frac:.0%} {novel[:7]}')
                print(f'          {s[:190]}')
        tot_drop += len(drop)
    print(f'\nsections over gate : {tot_before}')
    print(f'cleared            : {cleared}')
    print(f'not cleared        : {still}')
    print(f'would go under {MIN_WORDS}w : {thin}')
    print(f'blocks to remove   : {tot_drop}')

    if apply_:
        allines = lines
        for v in verses or sorted(secs):
            if v not in secs:
                continue
            _, blocks, _ = secs[v]
            _, _, drop, _ = plan(blocks)
            if drop:
                # re-locate each time: line numbers shift after an edit
                secs2, allines2 = load_sections_from('\n'.join(allines))
                if v in secs2:
                    _, b2, _ = secs2[v]
                    _, _, d2, _ = plan(b2)
                    if d2:
                        allines = rebuild(allines2, b2, d2, v).split('\n')
        open(path, 'w', encoding='utf-8', newline='\n').write(
            re.sub(r'\n{3,}', '\n\n', '\n'.join(allines)).rstrip('\n') + '\n')
        print(f'WROTE {path}')
    else:
        print('(dry run -- nothing written)')
    return 0


def load_sections_from(raw):
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix='.md')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(raw)
    try:
        return load_sections(tmp)
    finally:
        os.unlink(tmp)


if __name__ == '__main__':
    sys.exit(main())
