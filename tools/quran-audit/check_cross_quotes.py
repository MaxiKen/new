#!/usr/bin/env python3
"""Cross-quote verifier for expanded/NNN.md.

Every quoted span in the commentary body that carries a Qur'anic citation
(S:V, S:V-V, or a list of them) is checked against translation/SSS.txt.

Classes:
  EXACT      quote is a verbatim substring of the cited verse(s)
  ELLIPSIS   quote is verbatim apart from explicit ellipsis gaps
  PARTIAL    quote is shorter than the verse but every word kept is verbatim
             (a contiguous substring) -> same as EXACT, kept for clarity
  DRIFT      some word(s) of the quote are not in the cited verse text
  NOVERSE    citation resolves to nothing in translation/ (bad ref)
  VICINITY   citation is explicitly qualified (vicinity / cf. / sense / context)
             -> not presented as verbatim, reported separately

Hadith quotations (al-Bukhari/Muslim/...) and quotes with no Qur'anic
citation are skipped.

usage: python3 check_cross_quotes.py <sura> [--json out.json] [--show-drift]
       python3 check_cross_quotes.py --sura 7
"""
import re, os, sys, json, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TR = os.path.join(ROOT, 'translation')

_cache = {}
def load(sura):
    if sura not in _cache:
        d = {}
        p = os.path.join(TR, '%03d.txt' % sura)
        if os.path.exists(p):
            for ln in open(p, encoding='utf-8'):
                m = re.match(r'^\s*(\d+)\s*\|\s*(.*)$', ln.rstrip('\n'))
                if m:
                    d[int(m.group(1))] = m.group(2).strip()
        _cache[sura] = d
    return _cache[sura]

QUOTE_CHARS = '\u2018\u2019\u201c\u201d\u0022\u0027\u00ab\u00bb\u2039\u203a'
BRACKETS = '\u02f9\u02fa\u02b9\u02ba'

def norm(s):
    # comparison form: words only. Quote nesting, editorial brackets, dashes and
    # punctuation are all ignored so that only real wording differences count.
    s = unicodedata.normalize('NFKD', s)
    s = re.sub('[' + QUOTE_CHARS + BRACKETS + ']', ' ', s)
    s = s.replace('\u2014', ' ').replace('\u2013', ' ').replace('\u2011', ' ')
    s = re.sub(r'[^A-Za-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).lower().strip()

HADITH = re.compile(r'(al-Bukh\u0101r\u012b|Bukhari|Muslim|al-Tirmidh\u012b|Tirmidhi|Ab\u016b D\u0101w\u016bd|al-D\u0101rim\u012b|Ibn M\u0101jah|al-Nas\u0101\u02be\u012b|Luke|Matthew|John \d)')
REF = re.compile(r'(\d{1,3})\s*:\s*(\d{1,3})(?:\s*[\u2013\-]\s*(\d{1,3}))?')
QUAL = re.compile(r'(vicinity|cf\.|sense|context|sequel|account|clause|onward|paraphras|and parallels|in its own s)')

def refs_in(text):
    out = []
    for m in REF.finditer(text):
        s, v1, v2 = int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))
        if 1 <= s <= 114 and v2 >= v1:
            out.append((s, v1, v2))
    return out

def ref_text(s, v1, v2):
    d = load(s)
    parts = [d.get(v) for v in range(v1, v2 + 1)]
    if any(p is None for p in parts):
        return None
    return ' '.join(parts)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--json' in sys.argv:
        args = [a for a in args if a != sys.argv[sys.argv.index('--json') + 1]]
    if not args or not args[0].isdigit():
        sys.exit('usage: check_cross_quotes.py <sura> [--json out.json] [--show-drift]')
    sura = int(args[0])
    as_json = None
    if '--json' in sys.argv:
        as_json = sys.argv[sys.argv.index('--json') + 1]
    path = os.path.join(ROOT, 'expanded', '%03d.md' % sura)
    lines = open(path, encoding='utf-8').read().split('\n')
    H = re.compile(r'^## S\u016brah .+? (\d+):(\d+)\s*$')
    secof = []
    cur = 0
    for l in lines:
        m = H.match(l.strip())
        if m:
            cur = int(m.group(2))
        secof.append(cur)

    # quoted spans per line: curly double, ascii double, curly single
    span_res = [
        re.compile(r'\u201c([^\u201c\u201d]{12,700})\u201d'),
        re.compile(r'"([^"“”‘’]{12,700})"'),
        re.compile(r'\u2018([^\u2018\u2019]{12,700})\u2019'),
    ]
    rows = []
    for i, l in enumerate(lines):
        if l.startswith('> **'):          # own-verse translation blockquote
            continue
        taken = []
        for rx in span_res:
            for m in rx.finditer(l):
                a, b = m.span(1)
                if any(a >= ta and b <= tb for ta, tb in taken):
                    continue
                taken.append((a, b))
                q = m.group(1)
                if len(norm(q).split()) < 3:
                    continue
                # citation window: after the quote, else before.  The window is
                # wide and the parenthesis may be long, because a citation often
                # carries an explanatory clause; a narrow window silently skipped
                # such spans, which is the one failure mode this gate must not
                # have.  Spans with no citation at all are reported as UNCITED
                # rather than dropped.
                after = l[b:b + 400]
                before = l[max(0, a - 400):a]
                cite = None
                # a reference in the few words immediately before the span wins:
                # "(20:117, where Adam is told, "...")" cites the inner quote by
                # the reference that introduces it, not by whatever parenthesis
                # happens to follow.
                mb = re.search(r'(\d{1,3}:\d{1,3}(?:\s*[–-]\s*\d{1,3})?)[^()\d]{0,60}$', before)
                mm = re.search(r'\*{0,2}[\s,;]*\(([^()]{0,300})\)', after)
                if mb and (not mm or mm.start() > 6):
                    cite = mb.group(1)
                if mm:
                    cite = mm.group(1)
                else:
                    mm2 = re.search(r'\(([^()]{0,300})\)\s*[:\u2014\-]?\s*\*{0,2}\s*$', before)
                    if mm2:
                        cite = mm2.group(1)
                if cite is not None and (HADITH.search(cite) or
                                         HADITH.search(l[max(0, a - 60):b + 60])):
                    continue
                rr = refs_in(cite) if cite else []
                rows.append(dict(line=i + 1, section=secof[i], quote=q,
                                 cite=(cite or '').strip(), refs=rr,
                                 qualified=bool(cite and QUAL.search(cite))))
    # dedupe identical (line, quote)
    seen = set(); uniq = []
    for r in rows:
        k = (r['line'], r['quote'][:80], r['cite'])
        if k in seen: continue
        seen.add(k); uniq.append(r)

    for r in uniq:
        if not r['refs']:
            r['cls'] = 'UNCITED'; r['miss'] = []
            continue
        nq = norm(r['quote'])
        words = nq.split()
        # candidate reference texts: each ref alone, and all refs joined in order
        cands = []
        missing = False
        for (s, v1, v2) in r['refs']:
            t = ref_text(s, v1, v2)
            if t is None:
                missing = True
            else:
                cands.append(norm(t))
        joined = norm(' '.join(ref_text(s, v1, v2) or '' for (s, v1, v2) in r['refs']))
        if joined:
            cands.append(joined)
        if missing and not cands:
            r['cls'] = 'NOVERSE'; r['miss'] = []; continue
        if r['qualified']:
            r['cls'] = 'VICINITY'; r['miss'] = []
            continue
        # fragment-wise check (handles ellipsis inside the quote)
        frags = [f for f in re.split(r'\u2026|\[\.\.\.\]|\.\.\.', r['quote']) if norm(f)]
        best = None
        for c in cands:
            if nq and nq in c:
                best = ('EXACT', []); break
            ok = True; miss = []
            for f in frags:
                nf = norm(f)
                if nf not in c:
                    ok = False
                    miss += [w for w in nf.split() if len(w) > 2 and w not in c.split()]
            if ok:
                best = ('ELLIPSIS' if len(frags) > 1 else 'EXACT', [])
                break
            if best is None or len(miss) < len(best[1]):
                best = ('DRIFT', miss)
        r['cls'], r['miss'] = best
    order = {'DRIFT': 0, 'NOVERSE': 1, 'ELLIPSIS': 2, 'VICINITY': 3, 'UNCITED': 4, 'EXACT': 5}
    uniq.sort(key=lambda r: (order.get(r['cls'], 9), r['section'], r['line']))
    counts = {}
    for r in uniq:
        counts[r['cls']] = counts.get(r['cls'], 0) + 1
    cited = sum(v for k, v in counts.items() if k != 'UNCITED')
    print('quoted spans: %d  (with a Quranic citation: %d, uncited: %d)'
          % (len(uniq), cited, counts.get('UNCITED', 0)))
    for k in ('DRIFT', 'NOVERSE', 'ELLIPSIS', 'VICINITY', 'EXACT', 'UNCITED'):
        if counts.get(k):
            print('  %-9s %d' % (k, counts[k]))
    if '--show-uncited' in sys.argv:
        for r in uniq:
            if r['cls'] == 'UNCITED':
                print('  UNCITED L%-6d \u00a7%s  %s' % (r['line'], r['section'], r['quote'][:110]))
    if as_json:
        json.dump(uniq, open(as_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('wrote', as_json)
    if '--show-drift' in sys.argv:
        for r in uniq:
            if r['cls'] != 'DRIFT':
                continue
            print('\n\u00a7%d:%d line %d  cites (%s)' % (sura, r['section'], r['line'], r['cite']))
            print('  QUOTE: %s' % r['quote'][:300])
            for (s, v1, v2) in r['refs']:
                t = ref_text(s, v1, v2)
                print('  REF %d:%d%s: %s' % (s, v1, '' if v1 == v2 else '-' + str(v2), (t or 'MISSING')[:300]))
            print('  MISSING WORDS: %s' % ', '.join(r['miss'][:14]))
    return 0

if __name__ == '__main__':
    sys.exit(main())
