#!/usr/bin/env python3
"""Filler and depth gate for expanded/NNN.md.

Measures the things that make expanded prose read as padding rather than
scholarship, per verse section and per file:

  depth    words per section against a target band (default 1200-1600).
  tics     formulaic connective phrases per 1,000 words ("It is worth
           noting", "In other words", "The point is", ...).
  chains   self-referential sentence shapes per 1,000 words
           ("X is the Y that is Z", "the A of the B of the C",
            "the X is the Y of the Z").
  dup      repeated 10-grams within a section (degeneracy), as a fraction.
  repeats  sentences of 12+ words repeated verbatim elsewhere in the same
           file. Scripture and hadith quotations are excluded, so what is
           left is recycled commentary prose.

Nothing here edits files; it only reports. Exit status is 1 when any checked
section is outside the band or above a threshold, so it can be used as a gate.

usage: check_filler.py --sura 7 [--json out.json]
       check_filler.py --all
       check_filler.py --sura 7 --band 900-1100 --max-tics 4.0 --show 12
"""
import argparse
import collections
import json
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXP = os.path.join(ROOT, 'expanded')

HEAD = re.compile(r'^## S\u016brah .+? (\d+):(\d+)\s*$')

TICS = [
    'it is worth noting', 'worth noting', 'it is important to note',
    'important to note', 'it should be noted', 'it must be noted',
    'in other words', 'that is to say', 'the point is', 'the fact is',
    'as we have seen', 'as has been seen', 'as noted above',
    'it is no accident', 'not an accident', 'needless to say',
    'it goes without saying', 'to be sure', 'at the end of the day',
    'in a sense', 'in a way', 'so to speak', 'it is clear that',
    'it is obvious that', 'this is the reason why', 'the reason for this is',
]

CHAIN_RX = [
    (r'\bis the \w+ that is\b', 3),
    (r'\bof the \w+ of the\b', 2),
    (r'\bthe \w+ is the \w+ of the\b', 3),
]

QUOTE_SPAN = re.compile(r'[\u201c\u2018"\u00ab]([^\u201d\u2019"\u00bb]{12,})[\u201d\u2019"\u00bb]')
WORDS = re.compile(r"[\w\u02b9\u02bc\u02bf\u02c8\u02c9\u2019'-]+")


def sections(path):
    """Return [(verse, first_line_number, text)] for every verse section."""
    lines = open(path, encoding='utf-8').read().split('\n')
    idx = [(i, int(HEAD.match(l).group(2))) for i, l in enumerate(lines) if HEAD.match(l)]
    out = []
    for j, (i, v) in enumerate(idx):
        end = idx[j + 1][0] if j + 1 < len(idx) else len(lines)
        out.append((v, i + 1, '\n'.join(lines[i:end])))
    return out


def body_words(text):
    """Word count of the commentary body (translation blockquote excluded)."""
    return len(WORDS.findall('\n'.join(l for l in text.split('\n')
                                    if not l.startswith('>'))))


def tic_count(text):
    low = text.lower()
    return sum(low.count(t) for t in TICS)


def chain_count(text):
    return sum(w * len(re.findall(rx, text, re.I)) for rx, w in CHAIN_RX)


def dup_score(text, n=10):
    words = WORDS.findall(text.lower())
    grams = [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]
    if not grams:
        return 0.0, 0
    c = collections.Counter(grams)
    dupes = sum(v - 1 for v in c.values() if v > 1)
    return dupes / len(grams), dupes


def strip_quotes(text):
    """Remove quoted spans so scripture and hadith are not counted as prose."""
    return QUOTE_SPAN.sub(' ', text)


SENT = re.compile(r'(?<=[.!?])\s+(?=[\u0027\u2018\u201c*A-Z0-9])([^.!?\n]{60,400}[.!?])')


def prose_sentences(text):
    """Sentences of commentary prose: blockquoted verse translations and any
    quoted span (scripture, hadith, scholar) are removed first."""
    body = '\n'.join(l for l in text.split('\n') if not l.startswith('>'))
    out = []
    for s in SENT.findall(strip_quotes(body)):
        s = re.sub(r'\*+', '', s).strip()
        words = WORDS.findall(s)
        if len(words) >= 12:
            out.append(' '.join(words).lower())
    return out


def scan(path, band, max_tics, max_chain, max_dup, max_repeat):
    secs = sections(path)
    rows = []
    allsent = collections.Counter()
    for v, ln, text in secs:
        w = body_words(text)
        tics = tic_count(text)
        chains = chain_count(text)
        dup, dupes = dup_score(text)
        sents = prose_sentences(text)
        allsent.update(sents)
        rows.append(dict(verse=v, line=ln, words=w,
                         tics=tics, tics_1k=round(1000 * tics / w, 2) if w else 0,
                         chains=chains, chains_1k=round(1000 * chains / w, 2) if w else 0,
                         dup=round(dup, 4), dup_grams=dupes, sentences=len(sents)))
    lo, hi = band
    repeated = {s: c for s, c in allsent.items() if c > 1}
    for r in rows:
        r['fails'] = sorted(
            ([ 'depth<%d' % lo] if r['words'] < lo else []) +
            (['depth>%d' % hi] if r['words'] > hi else []) +
            (['tics>%.1f' % max_tics] if r['tics_1k'] > max_tics else []) +
            (['chains>%.1f' % max_chain] if r['chains_1k'] > max_chain else []) +
            (['dup>%.2f' % max_dup] if r['dup'] > max_dup else []))
    words = [r['words'] for r in rows]
    return dict(
        file=os.path.basename(path), sections=len(rows),
        words_total=sum(words),
        words_min=min(words) if words else 0,
        words_median=int(statistics.median(words)) if words else 0,
        words_max=max(words) if words else 0,
        below_band=sum(1 for r in rows if r['words'] < lo),
        above_band=sum(1 for r in rows if r['words'] > hi),
        tics_total=sum(r['tics'] for r in rows),
        tics_1k=round(1000 * sum(r['tics'] for r in rows) / max(sum(words), 1), 2),
        chains_1k=round(1000 * sum(r['chains'] for r in rows) / max(sum(words), 1), 2),
        worst_dup=max((r['dup'] for r in rows), default=0),
        repeated_sentences=len(repeated),
        repeated_examples=sorted(repeated.items(), key=lambda kv: -kv[1])[:8],
        failing_sections=[dict(verse=r['verse'], line=r['line'], words=r['words'],
                               fails=r['fails']) for r in rows if r['fails']],
        rows=rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sura', nargs='?', type=int)
    ap.add_argument('--sura', dest='sura_opt', type=int)
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--band', default='1200-1600')
    ap.add_argument('--max-tics', type=float, default=4.0, help='per 1,000 words')
    ap.add_argument('--max-chain', type=float, default=1.5, help='per 1,000 words')
    ap.add_argument('--max-dup', type=float, default=0.10, help='10-gram duplicate fraction')
    ap.add_argument('--max-repeat', type=int, default=0)
    ap.add_argument('--show', type=int, default=10, help='worst sections to list')
    ap.add_argument('--json')
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.band.split('-'))

    suras = list(range(1, 115)) if a.all else [a.sura or a.sura_opt]
    if not suras or suras == [None]:
        ap.error('give a sura number, --sura N, or --all')

    out = []
    bad = 0
    for n in suras:
        p = os.path.join(EXP, '%03d.md' % n)
        if not os.path.exists(p):
            continue
        r = scan(p, (lo, hi), a.max_tics, a.max_chain, a.max_dup, a.max_repeat)
        out.append(r)
        fails = len(r['failing_sections'])
        bad += fails
        print('%s  %4d sections  %8d words  band %s  min %d / med %d / max %d  '
              'below %d above %d  tics %.2f/1k  chains %.2f/1k  dup %.3f  '
              'repeated sentences %d  FAILING %d'
              % (r['file'], r['sections'], r['words_total'], a.band, r['words_min'],
                 r['words_median'], r['words_max'], r['below_band'], r['above_band'],
                 r['tics_1k'], r['chains_1k'], r['worst_dup'],
                 r['repeated_sentences'], fails))
        for s, c in r['repeated_examples'][:4]:
            print('    %dx  %s' % (c, s[:100]))
        worst = sorted(r['failing_sections'],
                       key=lambda x: (x['words'], len(x['fails'])))[:a.show]
        for f in worst:
            print('    %d:%-4d L%-6d %5dw  %s' % (n, f['verse'], f['line'], f['words'],
                                                  ','.join(f['fails'])))
    if a.json:
        json.dump(out, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('wrote', a.json)
    print('\nsections failing the gate: %d' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
