#!/usr/bin/env python3
"""Filler and depth gate for expanded/NNN.md.

Measures the things that make expanded prose read as padding rather than
scholarship, per verse section and per file:

  depth    words per section against a target band (default 1200-1600), with
           an explicit, reason-carrying reduced floor for the minority of
           verses that are muqatta'at, a single dialogue clause or a
           scene-closing fragment (see SHORT_VERSE below).
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

# --- auditable depth exception -------------------------------------------
# The band assumes a verse has enough surface to sustain it. A minority of
# verses do not: the muqatta'at, a single dialogue clause, or a sentence that
# closes a scene and takes its sense from the verse before it. Writing those
# to the full band is padding, which is precisely what this gate exists to
# stop, so they carry a reduced floor (REDUCED_FLOOR) and the same ceiling.
#
# Membership is objective and auditable: every entry is a verse of fourteen
# words or fewer in translation/NNN.txt *and* a fragment of one of the kinds
# named above. Short verses that are not fragments -- 7:55 on the manners of
# supplication, 7:166 on the metamorphosis, 7:183 on istidraj, 7:199 on
# forbearance and turning away, 7:5 on the cry of the destroyed cities --
# stay in the full band, because there is real scholarship to fill them with.
# Entries are added one at a time with a reason; never in bulk.
REDUCED_FLOOR = 700
SHORT_VERSE = {
    '7:1':   "muqatta'at: the four disjointed letters, one word in translation",
    '7:14':  "Iblis's one-clause appeal for respite",
    '7:15':  "one-clause divine reply granting the respite",
    '7:21':  "one-clause oath by which Iblis swore to them",
    '7:76':  "one-clause rejection by the arrogant party",
    '7:78':  "scene-closer: the earthquake and the prone bodies",
    '7:81':  "one-clause rebuke within Lut's speech",
    '7:91':  "scene-closer: the earthquake and the prone bodies",
    '7:107': "scene: the staff thrown down and becoming a snake",
    '7:109': "one-clause accusation by the chiefs of Pharaoh's people",
    '7:111': "one-clause reply deferring Moses and his brother",
    '7:112': "purpose clause continuing 7:111, six words in translation",
    '7:114': "one-clause reply granting the magicians their wage",
    '7:118': "scene-closer: the truth prevailed and the illusion failed",
    '7:119': "scene-closer: Pharaoh's people defeated and humiliated",
    '7:120': "scene: the magicians falling down prostrate, six words",
    '7:121': "opening clause of the magicians' declaration, completed in 7:122",
    '7:122': "continuation clause of 7:121, six words in translation",
    '7:125': "one-clause reply of the magicians on returning to their Lord",
    '7:192': "continuation clause of 7:191, eight words in translation",
}


def depth_floor(key, lo):
    """Floor for section `key` ('7:25'); the band floor unless excepted."""
    return REDUCED_FLOOR if key in SHORT_VERSE else lo



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


def prose_only(text):
    """Commentary prose alone: blockquoted lines out, then quoted spans out.

    Tics and chains are properties of the commentary, not of scripture. A shape
    like 'the A of the B of the C' inside a quotation belongs to the translation
    being quoted -- scoring it as a chain would penalise the very exactness that
    check_cross_quotes.py demands, and would make verbatim quotation cost more
    than paraphrase.
    """
    body = '\n'.join(l for l in text.split('\n') if not l.startswith('>'))
    return strip_quotes(body)


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


def scan(path, band, max_tics, max_chain, max_dup, max_repeat, sura=None):
    lo, hi = band
    secs = sections(path)
    rows = []
    allsent = collections.Counter()
    for v, ln, text in secs:
        w = body_words(text)
        prose = prose_only(text)
        tics = tic_count(prose)
        chains = chain_count(prose)
        dup, dupes = dup_score(text)
        sents = prose_sentences(text)
        allsent.update(sents)
        rows.append(dict(verse=v, line=ln, words=w,
                         floor=depth_floor('%d:%d' % (sura, v), lo) if sura else lo,
                         tics=tics, tics_1k=round(1000 * tics / w, 2) if w else 0,
                         chains=chains, chains_1k=round(1000 * chains / w, 2) if w else 0,
                         dup=round(dup, 4), dup_grams=dupes, sentences=len(sents)))
    repeated = {s: c for s, c in allsent.items() if c > 1}
    for r in rows:
        r['fails'] = sorted(
            ([ 'depth<%d' % r['floor']] if r['words'] < r['floor'] else []) +
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
        below_band=sum(1 for r in rows if r['words'] < r['floor']),
        reduced_floor=sum(1 for r in rows if r['floor'] != lo),
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
        r = scan(p, (lo, hi), a.max_tics, a.max_chain, a.max_dup, a.max_repeat, sura=n)
        out.append(r)
        fails = len(r['failing_sections'])
        bad += fails
        print('%s  %4d sections  %8d words  band %s  min %d / med %d / max %d  '
              'below %d above %d  reduced-floor %d  tics %.2f/1k  chains %.2f/1k  '
              'dup %.3f  repeated sentences %d  FAILING %d'
              % (r['file'], r['sections'], r['words_total'], a.band, r['words_min'],
                 r['words_median'], r['words_max'], r['below_band'], r['above_band'],
                 r['reduced_floor'], r['tics_1k'], r['chains_1k'], r['worst_dup'],
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
