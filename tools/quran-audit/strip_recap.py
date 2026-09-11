#!/usr/bin/env python3
"""Find and remove recapitulation blocks: mini-heading blocks that restate
their own section.

This is the defect class 017.md carried and that Group H closed by block
removal (REMAINING_ISSUES.md H2/H5a). It is NOT the 007.md defect -- 007.md
carried machine-generated nominalisations recursing within a sentence, which
repair_degen.py handles. Check which defect a file has before choosing a tool:
if repair_degen.py --dry-run reports actions={'keep': N} with nothing
stripped, the duplication is structural rather than sentential.

A recap block is a mini-heading block whose content substantially restates
other blocks in the same section. It typically sits near the end, often
re-quoting blockquoted verses or hadith already quoted above it, often under a
heading that paraphrases an earlier heading.

novel_sentences.py did this for 017.md by diffing against a pre-insertion
backup (/tmp/017.bak). No such backup exists for the other files, so this tool
identifies recap blocks by intra-section overlap instead, which needs no
history.

SCORING. All duprates here are computed by census.duprate on the census
'whole' span (section heading through body, trailing rule dropped). That is
non-negotiable: census.py carries an explicit warning that a body-only span
gives materially different counts (151 vs 269 at the 0.030 gate) and must not
be substituted silently. An earlier version of this tool scored joined block
bodies only, which excluded the verse-translation line, and consequently found
zero flagged sections in files census reported 30 in. Do not reintroduce that.

Removal is measured, not guessed. For each flagged section the tool removes the
smallest set of highest-overlap blocks that (a) brings the census duprate under
the gate and (b) leaves at least MIN_WORDS words, so a duplication defect is
never traded for a depth defect. Before deleting a block it reports the block's
novel sentences -- content found nowhere else in the section -- so anything
worth keeping can be folded into a surviving heading rather than lost.

Usage:
    strip_recap.py --sura 25 --dry-run          # report candidates + salvage
    strip_recap.py --sura 25 --classify 53      # per-block overlap table
    strip_recap.py --sura 25 --apply [verses]   # write
"""
import collections
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402

GATE = 0.030
MIN_WORDS = 400
NGRAM_OVL = 5           # content-word shingles for block-vs-block overlap
OVERLAP_MIN = 0.30      # a block this redundant is a recap candidate

CONTENT = re.compile(r"[a-zʾāīūṭṣḥḍẓʿğçş]+")
STOP = set("""the a an of and to in is that it for with as on be by not from
this these those are was were his her its their they he she we you your our
which who whom what when where how all any no nor only very also such than
then there here but or if so do does did done have has had being been one two
""".split())
HEADING = re.compile(r'^\*\*(.+?)\*\*\s*$')
# Hoisted: Python 3.11 f-strings cannot contain backslashes, and this
# pattern is needed inside f-string expressions below.
WCOUNT = re.compile(r"[\w'\u2019\-]+")


def duprate(text):
    """census's metric on census's span. Returns (rate, word_count)."""
    r, _, _ = census.duprate(text)
    return r, len(WCOUNT.findall(text))


def shingles(text, n=NGRAM_OVL):
    w = [x for x in CONTENT.findall(text.lower()) if x not in STOP and len(x) > 2]
    return {tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def sentences(text):
    # Each lookbehind alternative must be individually fixed-width, so the
    # alternation sits outside them rather than inside one lookbehind.
    parts = re.split(
        r'(?:(?<=[.!?])|(?<=[.!?]["\'”’)\*])|(?<=[.!?]["\'”’)\*]{2}))\s+',
        text)
    return [p.strip() for p in parts if p.strip()]


def block_ranges(lines, i, e):
    """Mini-heading blocks inside section lines [i, e) -> [(heading, s, en)].

    s is the heading's own line; en is the line before the next heading (or e).
    The pre-heading region (translation, marker) is excluded: it is not a
    candidate for removal.
    """
    idx = [j for j in range(i, e)
           if HEADING.match(lines[j])
           and HEADING.match(lines[j]).group(1).strip() != 'Expanded Commentary']
    out = []
    for k, j in enumerate(idx):
        en = idx[k + 1] if k + 1 < len(idx) else e
        out.append((HEADING.match(lines[j]).group(1).strip(), j, en))
    return out


def body_of(lines, s, en):
    return '\n'.join(lines[s + 1:en])


def whole_minus(lines, i, e, drop):
    """The census 'whole' span with the dropped block ranges removed."""
    kill = set()
    for _, s, en in drop:
        kill.update(range(s, en))
    return '\n'.join(l for j, l in enumerate(lines)
                     if i <= j < e and j not in kill and l.strip() != '---')


def overlap_table(lines, i, e, blocks):
    sh = [shingles(body_of(lines, s, en)) for _, s, en in blocks]
    res = []
    for k in range(len(blocks)):
        if not sh[k]:
            res.append(0.0)
            continue
        other = set()
        for m in range(len(blocks)):
            if m != k:
                other |= sh[m]
        res.append(len(sh[k] & other) / len(sh[k]))
    return res


def novel_report(lines, blocks, k):
    """Sentences in block k holding content words found nowhere else."""
    body = body_of(lines, blocks[k][1], blocks[k][2])
    oc = set()
    for m, (_, s, en) in enumerate(blocks):
        if m != k:
            oc |= {w for w in CONTENT.findall(body_of(lines, s, en).lower())
                   if w not in STOP and len(w) > 3}
    rows = []
    for sent in sentences(body):
        cw = [w for w in CONTENT.findall(sent.lower()) if w not in STOP and len(w) > 3]
        if not cw:
            continue
        novel = [w for w in cw if w not in oc]
        if novel:
            rows.append((len(novel) / len(cw), sorted(set(novel)), sent))
    rows.sort(reverse=True)
    return rows


def plan(lines, i, e, blocks, threshold=GATE, min_words=MIN_WORDS):
    """Smallest set of highest-overlap blocks whose removal clears the gate."""
    base, wc = duprate(whole_minus(lines, i, e, []))
    if base < threshold:
        return base, base, [], wc
    ov = overlap_table(lines, i, e, blocks)
    order = sorted(range(len(blocks)), key=lambda k: -ov[k])
    drop, cur = [], base
    for k in order:
        if ov[k] < OVERLAP_MIN:
            break
        trial = drop + [k]
        tdrop = [blocks[x] for x in trial]
        txt = whole_minus(lines, i, e, tdrop)
        d, w = duprate(txt)
        if w < min_words:
            continue
        drop, cur = trial, d
        if d < threshold:
            break
    drop.sort()
    return base, cur, [blocks[x] for x in drop], wc


def main():
    a = sys.argv[1:]
    sura = 7
    if '--sura' in a:
        k = a.index('--sura')
        sura = int(a[k + 1])
        # the sura number must not be mistaken for a verse number
        del a[k:k + 2]
    path = f'expanded/{sura:03d}.md'
    verses = [int(x) for x in a if x.isdigit()]

    raw = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    lines = raw.split('\n')
    secs = census.sections_of(path)
    heads = sorted((v, d['line'] - 1) for v, d in secs.items())
    ranges = {}
    for k, (v, i) in enumerate(heads):
        ranges[v] = (i, heads[k + 1][1] if k + 1 < len(heads) else len(lines))

    if '--classify' in a:
        print(f'{path}  --classify  (duprate = census metric on census span)')
        for v in verses or sorted(secs):
            if v not in ranges:
                continue
            i, e = ranges[v]
            blocks = block_ranges(lines, i, e)
            if len(blocks) < 2:
                continue
            d, _ = duprate(whole_minus(lines, i, e, []))
            if d < GATE and not verses:
                continue
            ov = overlap_table(lines, i, e, blocks)
            print(f'  v{v}  duprate {d:.3f}  {len(blocks)} blocks')
            for k, (h, s, en) in enumerate(blocks):
                mark = ' RECAP?' if ov[k] >= OVERLAP_MIN else ''
                print(f'      blk{k} {ov[k]:5.0%} {len(re.findall(r"[a-z]+", body_of(lines, s, en))):5d}w'
                      f'  {h[:56]}{mark}')
        return 0

    apply_ = '--apply' in a
    over = cleared = still = thin = 0
    edits = []
    for v in verses or sorted(secs):
        if v not in ranges:
            continue
        i, e = ranges[v]
        blocks = block_ranges(lines, i, e)
        if len(blocks) < 2:
            continue
        before, after, drop, wc = plan(lines, i, e, blocks)
        if before < GATE:
            continue
        over += 1
        if not drop:
            still += 1
            print(f'v{v}: NO SAFE REMOVAL (duprate {before:.3f}, {wc}w) -- needs authoring')
            continue
        kept = wc - sum(len(WCOUNT.findall(body_of(lines, s, en)))
                        for _, s, en in drop)
        if after >= GATE:
            still += 1
            tag = f'{before:.3f} -> {after:.3f} still over'
        else:
            cleared += 1
            tag = f'{before:.3f} -> {after:.3f}  CLEARS'
        if kept < MIN_WORDS:
            thin += 1
            tag += '  THIN!'
        print(f'v{v}: {tag}  drop {len(drop)} blk, {wc}w -> {kept}w')
        for h, s, en in drop:
            nw = len(WCOUNT.findall(body_of(lines, s, en)))
            print(f'    - "{h}" (lines {s + 1}-{en}, {nw}w)')
            k = blocks.index((h, s, en))
            for frac, novel, sent in novel_report(lines, blocks, k)[:3]:
                print(f'        novel {frac:.0%} {novel[:7]}')
                print(f'          {sent[:180]}')
        edits.append((v, drop))

    print(f'\nsections over gate : {over}')
    print(f'cleared            : {cleared}')
    print(f'not cleared        : {still}')
    print(f'would go under {MIN_WORDS}w : {thin}')
    print(f'blocks to remove   : {sum(len(d) for _, d in edits)}')

    if apply_:
        # delete from the bottom up so earlier line numbers stay valid
        kill = set()
        for v, drop in edits:
            for _, s, en in drop:
                kill.update(range(s, en))
        out = [l for j, l in enumerate(lines) if j not in kill]
        txt = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).rstrip('\n') + '\n'
        open(path, 'w', encoding='utf-8', newline='\n').write(txt)
        print(f'WROTE {path}')
        print('re-run: normalize.py %d, then validate.py and census.py' % sura)
    else:
        print('(dry run -- nothing written)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
