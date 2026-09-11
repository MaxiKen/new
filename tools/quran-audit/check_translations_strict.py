#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strict translation-line audit for expanded/.

WHY THIS EXISTS
---------------
`check_translations.py` uses an overlap coefficient with `min(|A|,|B|)` as the
denominator. That denominator passes a DIFFERENT verse whenever the own-verse
text is short: `037.md` v156 scored 0.75 against text belonging to `11:96`, and
a whole-file "0 flagged" result was reported while three substitutions stood in
the file. This tool replaces that test.

TWO INDEPENDENT TESTS, because neither alone is sufficient:

  1. OWN-VERSE MATCH. Normalise, take tokens of length >= 2, Jaccard the line
     against BOTH `initial/` and `translation/` for that same verse. Anything
     below the threshold is printed for reading.

  2. FOREIGN EXACT MATCH. Build a normalised-string index of the whole corpus
     (`initial/` and `translation/`). A line that is verbatim some OTHER verse
     is a definite substitution and is reported as such.

A THIRD check classifies each survivor: the line is scored against every verse
in the corpus, and if its best match is a DIFFERENT verse well above its own
score, that is strong evidence of substitution rather than paraphrase.

CRITICAL: A SCORE ALONE NEVER DECIDES ANYTHING.
`001.md` is the user-confirmed correct reference, and it scores 0.67 and 0.76 at
v5 and v7, because it legitimately blends both sources ("You alone we worship,
and from You alone we seek help"). Legitimate hybrids exist. Every survivor this
tool prints must be READ against its sources before being called a defect.

TOKEN LENGTH MATTERS. Tokens must be length >= 2. A `len(w) > 3` filter empties
the token set on short verses such as "Ya. Sin." or "Say, He, God, is One", and
Jaccard then returns 0.00 on an EXACT match. That artifact once manufactured
about 64 false "fabricated" flags. The exact-normalised-string fallback below
covers the case where either token set is genuinely empty.

USAGE
    python3 tools/quran-audit/check_translations_strict.py [--sura N]
                                                           [--threshold 0.90]
                                                           [--verbose]
                                                           [--no-control]

Exit code is 0 when the self-test control passes and no FOREIGN EXACT match is
found. Own-verse misses below threshold are reported but do not fail the run,
because most are paraphrase register; they require a human reading.
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXPANDED = REPO / "expanded"
INITIAL = REPO / "initial"
TRANSLATION = REPO / "translation"

# Marks that must be removed before comparing: emphasis, tatweel-ish diacritics,
# and the small-high-seen style marks some editions carry.
STRIP = "*_`~\u0670\u0671\u0653\u0654\u0655\u0656\u0657\u0658"

PUNCT_MAP = [
    ("\u201c", '"'), ("\u201d", '"'), ("\u2018", "'"), ("\u2019", "'"),
    ("\u2013", "-"), ("\u2014", "-"),
]


def norm(s):
    """Normalise for comparison. NFKC, curly quotes/dashes to ASCII, strip
    emphasis and diacritic marks, drop non-word characters, collapse spaces."""
    s = unicodedata.normalize("NFKC", s)
    for a, b in PUNCT_MAP:
        s = s.replace(a, b)
    s = "".join(ch for ch in s if ch not in STRIP)
    s = re.sub(r"[^\w\s-]", " ", s)
    return " ".join(s.split()).lower()


def toks(s):
    """Tokens of length >= 2. Do NOT raise this to >3: see module docstring."""
    return set(w for w in norm(s).split() if len(w) >= 2)


def jac(a, b):
    """Jaccard over tokens, with an exact-normalised-string fallback when either
    token set is empty (very short verses)."""
    A, B = toks(a), toks(b)
    if not A or not B:
        return 1.0 if norm(a) == norm(b) else 0.0
    return len(A & B) / len(A | B)


def load_initial(n):
    """`initial/NNN.md`, format `> **N** text`."""
    d = {}
    p = INITIAL / f"{n:03d}.md"
    if not p.exists():
        return d
    for ln in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^>\s*\*\*(\d+)\*\*\s*(.*)$", ln.strip())
        if m:
            d[int(m.group(1))] = m.group(2).strip()
    return d


def load_translation(n):
    """`translation/NNN.txt`, format `N | text`. Note: .txt, not .md."""
    d = {}
    p = TRANSLATION / f"{n:03d}.txt"
    if not p.exists():
        return d
    for ln in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*(\d+)\s*\|\s*(.*)$", ln)
        if m:
            d[int(m.group(1))] = m.group(2).strip()
    return d


def expanded_lines(n):
    """Return {verse: translation_line} for expanded/NNN.md."""
    p = EXPANDED / f"{n:03d}.md"
    txt = p.read_text(encoding="utf-8")
    ms = list(re.finditer(r"^## Sūrah .+? (\d+):(\d+)$", txt, re.M))
    out = {}
    for idx, m in enumerate(ms):
        v = int(m.group(2))
        end = ms[idx + 1].start() if idx + 1 < len(ms) else len(txt)
        tm = re.search(r"^>\s*\*\*(.+?)\*\*\s*$", txt[m.end():end], re.M)
        out[v] = tm.group(1).strip() if tm else None
    return out


def suras():
    return sorted(int(p.stem) for p in EXPANDED.glob("*.md"))


def build_corpus_index(only=None):
    """normalised text -> sorted list of (sura, verse), over both sources."""
    idx = {}
    for n in (only if only else suras()):
        for d in (load_initial(n), load_translation(n)):
            for v, t in d.items():
                idx.setdefault(norm(t), []).append((n, v))
    for k in idx:
        idx[k].sort()
    return idx


def self_test():
    """Guard against the two failure modes that produced false results before.

    (a) an exact match must score 1.00 -- catches a token filter that empties
        the set on short verses;
    (b) a short verse with almost no long tokens must still compare correctly.
    """
    i1 = load_initial(1)
    if not i1:
        return False, "initial/001.md did not parse"
    v1 = i1[1]
    if abs(jac(v1, v1) - 1.0) > 1e-9:
        return False, f"exact match scored {jac(v1, v1):.2f}, expected 1.00"
    if not toks(v1):
        return False, f"token set empty for initial/001.md v1: {v1!r}"
    # A deliberately short string must fall back to exact comparison, not 0.0.
    if abs(jac("Ya Sin", "Ya Sin") - 1.0) > 1e-9:
        return False, "short-verse fallback broken"
    if abs(jac("Ya Sin", "Ha Mim")) != 0.0:
        return False, "short-verse fallback returns 1.0 for different text"
    return True, "control passed (exact match = 1.00, short-verse fallback OK)"


def build_corpus_texts(only=None):
    """List of (sura, verse, text) for every verse in both sources.

    Used by best_foreign, which needs the raw text of every verse, not just the
    normalised-string buckets that build_corpus_index produces.
    """
    out = []
    for n in (only if only else suras()):
        ini = load_initial(n)
        trl = load_translation(n)
        for v in sorted(set(ini) | set(trl)):
            if v in ini:
                out.append((n, v, ini[v]))
            if v in trl:
                out.append((n, v, trl[v]))
    return out


def best_foreign(line, sura, verse, corpus_texts):
    """Best match for `line` anywhere in the corpus, excluding this verse.

    Returns (score, (sura, verse)) or (0.0, None). Comparing this against the
    own-verse score is what separates a substitution from a paraphrase: if a
    DIFFERENT verse matches better than the verse's own text, the line was
    probably taken from that other verse.
    """
    best_s, best_w = 0.0, None
    for s, v, t in corpus_texts:
        if s == sura and v == verse:
            continue
        sc = jac(line, t)
        if sc > best_s:
            best_s, best_w = sc, (s, v)
    return best_s, best_w


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sura", type=int, help="audit a single sura")
    ap.add_argument("--threshold", type=float, default=0.90,
                    help="own-verse match below this is printed (default 0.90)")
    ap.add_argument("--verbose", action="store_true",
                    help="show source and expanded wording for each miss")
    ap.add_argument("--no-control", action="store_true",
                    help="skip the self-test (not recommended)")
    args = ap.parse_args()

    ok, msg = self_test()
    print(f"self-test: {msg}")
    if not ok and not args.no_control:
        print("ABORTING: the metric is not behaving; do not trust any count "
              "from this run.", file=sys.stderr)
        return 2
    if not ok:
        print("WARNING: self-test failed but --no-control given.", file=sys.stderr)

    targets = [args.sura] if args.sura else suras()
    corpus = build_corpus_index(targets)
    corpus_texts = build_corpus_texts(targets)

    checked = 0
    missing_line = 0
    no_source = 0
    foreign = []      # definite substitutions
    misses = []       # below threshold, need reading

    for n in targets:
        ini = load_initial(n)
        trl = load_translation(n)
        lines = expanded_lines(n)
        for v in sorted(lines):
            e = lines[v]
            if e is None:
                missing_line += 1
                continue
            if v not in ini and v not in trl:
                no_source += 1
                continue
            checked += 1
            si = jac(e, ini[v]) if v in ini else 0.0
            st = jac(e, trl[v]) if v in trl else 0.0
            best = max(si, st)

            # Test 2: verbatim some other verse?
            locs = corpus.get(norm(e), [])
            foreign_locs = [(s, vv) for s, vv in locs if not (s == n and vv == v)]
            own_loc = any(s == n and vv == v for s, vv in locs)
            if foreign_locs and not own_loc:
                foreign.append((n, v, foreign_locs, e, ini.get(v, trl.get(v, ""))))

            if best < args.threshold:
                # Test 3: is some DIFFERENT verse a clearly better match than
                # the verse's own text? If so, substitution is likely. If the
                # own verse is still the best match available, it is paraphrase.
                alt_score, alt_where = best_foreign(e, n, v, corpus_texts)
                misses.append((n, v, best, si, st, e,
                               ini.get(v, ""), trl.get(v, ""),
                               alt_score, alt_where))

    print(f"checked: {checked}   no translation line: {missing_line}   "
          f"no source text: {no_source}")
    print(f"own-verse match < {args.threshold:.2f}: {len(misses)}  "
          f"(must be READ; most are paraphrase register)")
    print(f"FOREIGN EXACT MATCH (definite substitution): {len(foreign)}")

    if foreign:
        print("\n=== definite substitutions ===")
        for n, v, locs, e, own in foreign:
            where = ", ".join(f"{s}:{vv}" for s, vv in locs[:4])
            print(f"  {n:03d}:{v}  is verbatim {where}")
            print(f"      line: {e[:110]}")
            print(f"      own : {own[:110]}")

    # Of the misses, how many have a DIFFERENT verse as their best corpus match?
    # Those are the ones worth reading first: the own verse is not even the
    # closest text in the corpus, which is what a substitution looks like.
    suspect = [m for m in misses if m[9] and m[8] > m[2] + 0.05]
    print(f"of those, best corpus match is a DIFFERENT verse: {len(suspect)}  "
          f"(read these first)")

    if args.verbose and misses:
        print(f"\n=== own-verse misses < {args.threshold:.2f} ===")
        for n, v, best, si, st, e, iv, tv, ascore, awhere in sorted(
                misses, key=lambda x: x[2]):
            print(f"\n  {n:03d}:{v}  best {best:.2f}  (initial {si:.2f} / "
                  f"translation {st:.2f})")
            if awhere:
                mark = "  <-- OTHER VERSE WINS" if ascore > best + 0.05 else ""
                print(f"    best corpus : {ascore:.2f} -> "
                      f"{awhere[0]}:{awhere[1]}{mark}")
            print(f"    initial/    : {iv[:150]}")
            print(f"    translation/: {tv[:150]}")
            print(f"    expanded/   : {e[:150]}")
    elif misses:
        from collections import Counter
        c = Counter(n for n, *_ in misses)
        print("\nmisses per file: " +
              ", ".join(f"{k:03d}:{v}" for k, v in sorted(c.items())))
        if suspect:
            print("suspect (other verse is a better match): " +
                  ", ".join(f"{m[0]:03d}:{m[1]}" for m in sorted(suspect)))

    print("\nA miss is NOT a defect. Read it against both sources first: "
          "001.md v5/v7 score 0.67/0.76 and are correct.")
    return 1 if foreign else 0


if __name__ == "__main__":
    sys.exit(main())
