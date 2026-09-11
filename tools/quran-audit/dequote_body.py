#!/usr/bin/env python3
"""Remove the body's re-quotation of the section's own verse, keeping the Arabic.

THE DEFECT. In much of the corpus a section displays its verse in the
`> **translation**` line and then, in the body, quotes that same English
translation again inside the construct

    <lead-in>: *"<English from the verse>"* (*<Arabic transliteration>*).

The English half duplicates the line immediately above it and is the single
largest cause of the remaining Group B duplication flags: 1,302 sections
corpus-wide contain such a re-quote, and 135 of the 172 sections currently
over the 0.030 gate are over it because of this construct. Removing the
translation line from the measured span drops 010.md from 30 flagged sections
to 0, 034.md from 8 to 0 and 039.md from 16 to 1, which is what identifies it
as the cause rather than a correlate.

The reference skeleton expanded/001.md -- user-confirmed, never to be modified
-- does not do this. Its longest verbatim overlap between a section's verse
and its own body is 30-40 characters of incidental phrase, against 60+ here
systematically. So the construct is a deviation from the reference, not a house
convention.

THE FIX. The Arabic transliteration duplicates nothing and appears nowhere else
in the section; deleting it would trade a duplication defect for a loss of real
scholarship. So only the English is removed, and the colon that introduced it
is left to introduce the Arabic instead:

    before:  ...rejected the truth: *"As for the disbelievers, theirs shall be
              a drink of boiling liquid..."* (*wa'lladhīna kafarū lahum
              sharābun min ḥamīmin...*). The Arabic term *ḥamīm* refers to...
    after:   ...rejected the truth: *wa'lladhīna kafarū lahum sharābun min
              ḥamīmin...*. The Arabic term *ḥamīm* refers to...

A second, mirrored form occurs in most other files and is handled the same
way -- keep the Arabic, drop the duplicated English gloss that follows it:

    before:  *Quli Allāhumma fāṭira ... yakhtalifūn* — "Say: O God!
              Originator of the heavens and the earth, ... they differ."
              *Fāṭir* is from *faṭara*, to split...
    after:   *Quli Allāhumma fāṭira ... yakhtalifūn*. *Fāṭir* is from
              *faṭara*, to split...

Nothing else in the section is touched. Only constructs whose English overlaps
the section's own translation by at least MIN_OVERLAP characters are
candidates, so a genuine cross-reference quotation (which quotes some *other*
verse, and whose parenthetical is `(Qur'an 27:30)` rather than italic Arabic)
can never be matched. Blockquote lines are excluded outright.

Every edit is re-measured with census.duprate on the census 'whole' span before
it is accepted; an edit that does not lower the duprate is reported and
skipped rather than applied.

Usage:
    dequote_body.py --sura 10 --dry-run
    dequote_body.py --sura 10 --dry-run 93      # one verse, full context
    dequote_body.py --sura 10 --apply [verses]
    dequote_body.py --survey                    # corpus-wide census of the defect
"""
import collections
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402

GATE = 0.030
MIN_OVERLAP = 60        # chars of the verse re-quoted before it counts
MIN_WORDS = 400

# *"<English>"* (*<Arabic>*)  -- the construct to dismantle
CONSTRUCT = re.compile(r'\*["“](.+?)["”]\*\s*\(\*(.+?)\*\)', re.S)
# *<Arabic>* — "<English>"  -- the mirror form (039.md, 014.md, 011.md ...)
ARABIC_FIRST = re.compile(r'\*([^*"“”]+)\*\s*[\u2014\u2013-]\s*["“](.+?)["”]', re.S)
# a quote with no Arabic after it
LONE_QUOTE = re.compile(r'\*["“](.+?)["”]\*', re.S)
WS = re.compile(r'\s+')


def squash(t):
    return WS.sub(' ', t).strip().lower()


def longest_common_run(a, b, cap=260):
    """Length of the longest substring of `a` occurring in `b`, probed downward.

    Probing long lengths first keeps this cheap: the construct quotes whole
    clauses, so the run is long when it exists at all.
    """
    for L in range(min(cap, len(a)), MIN_OVERLAP - 1, -5):
        for s in range(0, len(a) - L + 1, 5):
            if a[s:s + L] in b:
                return L
    return 0


def transform(body, translation, verbose=False):
    """-> (new_body, n_edits, samples). Only verified re-quotes are altered.

    Replacement is done by explicit slicing rather than re.sub with a function:
    a sub() callback must return only the text replacing the match, and
    returning a rebuilt line silently duplicates the surrounding text.
    """
    tr = squash(translation)
    if not tr:
        return body, 0, []
    edits = 0
    samples = []
    out = []
    for ln in body.split('\n'):
        if ln.lstrip().startswith('>'):
            out.append(ln)          # the translation line is never touched
            continue
        # Both forms are matched in one pass over the line by position, so a
        # line carrying each is handled correctly.
        cands = []
        for m in CONSTRUCT.finditer(ln):
            eng, ar = m.group(1), m.group(2)
            if longest_common_run(squash(eng), tr) >= MIN_OVERLAP:
                cands.append((m.start(), m.end(), ar, eng, 'eng-first'))
        for m in ARABIC_FIRST.finditer(ln):
            ar, eng = m.group(1), m.group(2)
            if longest_common_run(squash(eng), tr) >= MIN_OVERLAP:
                cands.append((m.start(), m.end(), ar, eng, 'ar-first'))
        cands.sort()
        res, pos = '', 0
        for st, en, ar, eng, kind in cands:
            if st < pos:
                continue            # overlapping match; already consumed
            lead = ln[pos:st]
            if kind == 'ar-first':
                # keep the Arabic, drop the duplicated English gloss after it
                rep = f'*{ar.strip()}*'
            else:
                before = (res + lead).rstrip()
                nxt = ln[en:en + 1]
                if before.endswith((':', ';', ',', '\u2014', '-')):
                    # the colon that introduced the English now introduces the Arabic
                    rep = f'*{ar}*'
                else:
                    rep = f' The Arabic reads *{ar}*' + ('' if nxt == '.' else '.')
            res += lead + rep
            pos = en
            edits += 1
            if verbose:
                samples.append((lead[-70:], eng[:70], ar[:70]))
        out.append(res + ln[pos:])
    return '\n'.join(out), edits, samples


def rebuild_lines(path, verse, new_body):
    """Replace a section's body in the file's lines."""
    lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    secs = census.sections_of(path)
    heads = sorted((v, d['line'] - 1) for v, d in secs.items())
    k = [n for n, (v, _) in enumerate(heads) if v == verse][0]
    i = heads[k][1]
    e = heads[k + 1][1] if k + 1 < len(heads) else len(lines)
    blk = lines[i + 1:e]
    # body starts after the Expanded Commentary marker, ends before '---'
    try:
        j = blk.index('**Expanded Commentary**') + 1
    except ValueError:
        j = 0
    pre, post = blk[:j], blk[j:]
    cut = len(post)
    for n, ln in enumerate(post):
        if ln.strip() == '---':
            cut = n
            break
    return lines[:i + 1] + pre + new_body.split('\n') + post[cut:] + lines[e:]


def main():
    a = sys.argv[1:]
    sura = None
    if '--sura' in a:
        k = a.index('--sura')
        sura = int(a[k + 1])
        del a[k:k + 2]
    verses = [int(x) for x in a if x.isdigit()]
    apply_ = '--apply' in a
    verbose = '--dry-run' in a and verses

    if '--survey' in a:
        tot = collections.Counter()
        per = []
        import glob
        for p in sorted(glob.glob('expanded/*.md')):
            secs = census.sections_of(p)
            n = nf = ne = 0
            for v, d in secs.items():
                tr = squash(d['translation'])
                if len(tr) < MIN_OVERLAP:
                    continue
                _, e, _ = transform(d['body'], d['translation'])
                if e:
                    n += 1
                    ne += e
                    r, _, _ = census.duprate(d['whole'])
                    if r >= GATE:
                        nf += 1
            if n:
                per.append((p, n, nf, ne))
            tot['sec'] += n
            tot['flagged'] += nf
            tot['constructs'] += ne
        for p, n, nf, ne in sorted(per, key=lambda x: -x[2])[:18]:
            print(f'  {p}  {n:4d} sections  {nf:3d} flagged  {ne:4d} constructs')
        print(f'\ncorpus: {tot["sec"]} sections, {tot["flagged"]} flagged, '
              f'{tot["constructs"]} constructs')
        return 0

    path = f'expanded/{sura:03d}.md'
    secs = census.sections_of(path)
    over = fixed = cleared = nohelp = thin = 0
    pending = []
    for v in verses or sorted(secs):
        d = secs[v]
        before, wbefore = census.duprate(d['whole'])[0], len(re.findall(r"[\w'’\-]+", d['body']))
        if before < GATE and not verses:
            continue
        new_body, n, samples = transform(d['body'], d['translation'], verbose)
        if not n:
            continue
        over += 1
        # Re-measure by transforming the census 'whole' span in place rather
        # than rebuilding a section from parts: a rebuilt probe does not match
        # the original span token-for-token, so its duprate is not comparable
        # to `before` and can read as an improvement that is really an artifact.
        new_whole, nw, _ = transform(d['whole'], d['translation'])
        after = census.duprate(new_whole)[0]
        wafter = len(re.findall(r"[\w'’\-]+", new_body))
        # The floor is a guard against pushing a healthy section into a depth
        # defect, not a reason to leave verbatim duplication in an already-thin
        # one. 039.md's sections average 387w (42 of 75 already under 400)
        # against 001.md's 1942w, so an absolute floor would refuse to fix
        # precisely the file that most needs it. Removing the English gloss of
        # an Arabic line that stays costs words but no information: the reader
        # still has the > **translation** line above and the Arabic in place.
        if wbefore >= MIN_WORDS > wafter:
            thin += 1
        if after >= before:
            nohelp += 1
            print(f'v{v}: {n} construct(s) but no improvement ({before:.3f} -> {after:.3f}) -- skipped')
            continue
        fixed += 1
        if after < GATE:
            cleared += 1
        print(f'v{v}: {before:.3f} -> {after:.3f}  {n} construct(s), '
              f'{wbefore}w -> {wafter}w' + ('  CLEARS' if after < GATE else ''))
        for lead, eng, ar in samples:
            print(f'    lead: ...{lead.strip()[-64:]}')
            print(f'    drop: *"{eng}..."*')
            print(f'    keep: *{ar}...*')
        pending.append((v, new_body))

    print(f'\nsections with the construct : {over}')
    print(f'edited                      : {fixed}')
    print(f'cleared the gate            : {cleared}')
    print(f'no improvement, skipped     : {nohelp}')
    print(f'pushed under {MIN_WORDS}w by the edit : {thin}')

    if apply_:
        lines = open(path, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
        # apply bottom-up so line numbers stay valid
        for v, nb in sorted(pending, reverse=True):
            lines = rebuild_lines(path, v, nb)
            open(path, 'w', encoding='utf-8', newline='\n').write(
                re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).rstrip('\n') + '\n')
        print(f'WROTE {path}')
        print(f're-run: normalize.py {sura}, validate.py, test_skeleton.py, census.py')
    else:
        print('(dry run -- nothing written)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
