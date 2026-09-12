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
#
# 7:78 and 7:91 were on this list as scene-closers and have been removed.
# Both carry live scholarly material that is not scene-closing: the same
# destruction is described as rajfah here, as sayhah at 11:94 and as the
# zullah of 26:189, and Ibn Kathir holds on 26:176 that the companions of
# al-Aykah were the people of Madyan. They are listed in TIER1 below.
REDUCED_FLOOR = 700
SHORT_VERSE_007 = {
    '7:1':   "muqatta'at: the four disjointed letters, one word in translation",
    '7:14':  "Iblis's one-clause appeal for respite",
    '7:15':  "one-clause divine reply granting the respite",
    '7:21':  "one-clause oath by which Iblis swore to them",
    '7:76':  "one-clause rejection by the arrogant party",
    '7:81':  "one-clause rebuke within Lut's speech",
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

# --- chapter 2 (al-Baqarah) -------------------------------------------------
# Same objective test as 007: fourteen words or fewer in translation/002.txt
# *and* a fragment of one of the three named kinds. Ten verses of al-Baqarah
# fall under fourteen words; five of those ten are fragments and five are not.
# The five that are not -- listed here so the exclusion is auditable rather
# than silent -- stay in the full band because their material is real:
#   2:42  an imperative (do not mix truth with falsehood) with the whole
#         tahrif polemic behind it;
#   2:43  an imperative naming prayer, alms-tax and bowing with the
#         congregation;
#   2:152 an imperative pair (remember Me / thank Me) that is one of the
#         sūrah's memorised formulas;
#   2:244 an imperative (fight in the cause of Allah) carrying two divine
#         names;
#   2:278 an imperative on outstanding interest, the legal crux of 275-281.
SHORT_VERSE_002 = {
    '2:1':   "muqatta'at: Alif-Lam-Mim, one word in translation",
    '2:12':  "scene-closing verdict on the hypocrites' claim in 2:11; takes "
             "its sense from the exchange it closes",
    '2:52':  "scene-closer: forgiveness after the calf, taking its sense from "
             "the forty nights and the calf of 2:51",
    '2:192': "scene-closer: the cease-fire clause of the fighting passage, "
             "eleven words in translation",
    '2:227': "continuation clause closing the ila' ruling of 2:226, twelve "
             "words in translation",
}

SHORT_VERSE_BY_SURA = {2: SHORT_VERSE_002, 7: SHORT_VERSE_007}


def depth_floor(key, lo):
    """Floor for section `key` ('7:25'); the band floor unless excepted.

    Tier-1 sections carry their own floor (TIER1_FLOOR), raised from the
    band floor once every listed section had been drafted to it. Sections
    demoted out of TIER1 return to the band floor; no commentary is cut.
    """
    sura = int(key.split(':')[0])
    if key in SHORT_VERSE_BY_SURA.get(sura, {}):
        return REDUCED_FLOOR
    if key in TIER1_BY_SURA.get(sura, set()):
        return TIER1_FLOOR
    return lo


# --- tier-relative ceiling ------------------------------------------------
# The band ceiling assumes no single verse carries more argument than the
# ceiling can hold. A surveyed minority of Sūrat al-Aʿrāf does: the sections
# in TIER1 are those whose verse surface, content units, legal markers and
# uncited candidate parallels all indicate material the section had not
# consumed. The survey, the approvals and the verification of every external
# source cited are recorded in tools/quran-audit/DEPTH_PLAN_007.md, which
# lists the sub-heads each section already carried and the sub-heads added.
# They carry TIER1_CEILING. The four deepest -- the request to see God, the
# people of the heights, the market commands and the throne verse -- carry
# DEEPEST_CEILING, because their material is disputed at length by named
# authorities and compresses below that ceiling only by losing the dispute.
#
# Membership is an explicit verse list, not a threshold rule, so the
# exception stays auditable and cannot drift. Entries are added one at a
# time with the head that justifies them, and removed when reading the
# section shows its heads already consume the material; never in bulk.
# Twenty-two sections were listed and then removed on that ground:
# 7:178, 7:187, 7:32, 7:148, 7:92, 7:98, 7:128, 7:73, and the
# fourteen demoted together at tranche 27 (7:38, 7:43, 7:53, 7:69,
# 7:89, 7:137, 7:146, 7:155, 7:158, 7:160, 7:169, 7:188, 7:189,
# 7:203). See DEPTH_PLAN_007.md section 10.
TIER1_FLOOR = 1400
TIER1_CEILING = 1800
DEEPEST_CEILING = 2100
DEEPEST_007 = {'7:143', '7:46', '7:85', '7:54'}
TIER1_007 = DEEPEST_007 | {
    '7:22', '7:27', '7:28', '7:31', '7:33', '7:37',
    '7:44', '7:54', '7:56', '7:75', '7:78', '7:85',
    '7:88', '7:90', '7:91', '7:97', '7:99', '7:156',
    '7:157', '7:172', '7:175', '7:176', '7:182',
}

# --- chapter 2 (al-Baqarah) -----------------------------------------------
# Sixty-four of the chapter's 286 verses (22%) are listed. The selection rule
# is section 6 of tools/quran-audit/STANDARDIZATION_PROMPT.md: a verse is a
# Tier-1 candidate if it carries a legal ruling or a ruling's conditions, a
# divine attribute stated doctrinally, a covenant or oath or eschatological
# scene, a named prophetic episode with narrative consequences, a formula the
# Qur'an repeats elsewhere, or a term the tradition disputes with identifiable
# positions. Every entry below carries at least one of the six; the head that
# justifies each is recorded in tools/quran-audit/DEPTH_PLAN_002.md, and a
# section found on reading to have already consumed the material is removed
# from this set and logged there as demoted, exactly as on 007.
#
# The five deepest are the sūrah's own cruxes, the verses whose material is
# disputed at length by named authorities: the khilafah dialogue with the
# angels (30), the nights of the fast and the limits of i'tikaf (187), the
# Pedestal Verse (255), the prohibition of interest with its war-verse (275),
# and the closing petition (286).
DEEPEST_002 = {'2:30', '2:187', '2:255', '2:275', '2:286'}
TIER1_002 = DEEPEST_002 | {
    '2:2', '2:3', '2:7', '2:23', '2:26', '2:27', '2:34',
    '2:37', '2:40', '2:48', '2:54', '2:62', '2:65', '2:67',
    '2:74', '2:79', '2:83', '2:87', '2:97', '2:102', '2:106',
    '2:115', '2:124', '2:127', '2:143', '2:144', '2:152',
    '2:153', '2:154', '2:158', '2:163', '2:164', '2:173',
    '2:177', '2:178', '2:180', '2:183', '2:185', '2:186',
    '2:191', '2:196', '2:219', '2:222', '2:228', '2:229',
    '2:230', '2:233', '2:234', '2:238', '2:245', '2:249',
    '2:253', '2:256', '2:257', '2:258', '2:260', '2:261',
    '2:282', '2:285',
}

TIER1_BY_SURA = {2: TIER1_002, 7: TIER1_007}
DEEPEST_BY_SURA = {2: DEEPEST_002, 7: DEEPEST_007}

# Both names retained so nothing that imported the 007 sets can break.
DEEPEST = DEEPEST_007
TIER1 = TIER1_007


def depth_ceiling(key, hi):
    """Ceiling for section `key`; the band ceiling unless raised."""
    sura = int(key.split(':')[0])
    if key in DEEPEST_BY_SURA.get(sura, set()):
        return DEEPEST_CEILING
    if key in TIER1_BY_SURA.get(sura, set()):
        return TIER1_CEILING
    return hi



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
                         ceiling=depth_ceiling('%d:%d' % (sura, v), hi) if sura else hi,
                         tics=tics, tics_1k=round(1000 * tics / w, 2) if w else 0,
                         chains=chains, chains_1k=round(1000 * chains / w, 2) if w else 0,
                         dup=round(dup, 4), dup_grams=dupes, sentences=len(sents)))
    repeated = {s: c for s, c in allsent.items() if c > 1}
    for r in rows:
        r['fails'] = sorted(
            ([ 'depth<%d' % r['floor']] if r['words'] < r['floor'] else []) +
            (['depth>%d' % r['ceiling']] if r['words'] > r['ceiling'] else []) +
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
        reduced_floor=sum(1 for r in rows if r['floor'] < lo),
        above_band=sum(1 for r in rows if r['words'] > r['ceiling']),
        raised_ceiling=sum(1 for r in rows if r['ceiling'] != hi),
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
