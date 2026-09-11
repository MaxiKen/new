# -*- coding: utf-8 -*-
"""Corpus-wide off-topic sweep.

Flags sections whose commentary body does not echo the distinctive vocabulary of
their own translation -- i.e. prose that has drifted onto a different subject.

Test: take distinctive tokens from the section's `> **...**` translation line
(len > 3, minus a STOP list). Count how many appear in the commentary body
(non-blockquote, non-bold prose). Flag when < 15% are echoed.

Skips sections with < 3 distinctive tokens or with no prose body.

IMPORTANT: this tool always prints how many sections it examined. A previous
version of this sweep silently scanned 0 sections because a regex was missing
re.M, and still printed a clean "0 found" report. Treat `examined: 0` as failure.

Usage:
    python3 tools/quran-audit/check_offtopic.py            # whole corpus
    python3 tools/quran-audit/check_offtopic.py --sura 11  # one file
    python3 tools/quran-audit/check_offtopic.py --verbose
"""

import argparse
import glob
import os
import re
import sys
import unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ~30 high-frequency words that carry no topical signal.
STOP = {
    "that", "this", "they", "them", "their", "there", "these", "those", "then",
    "than", "what", "when", "which", "while", "with", "from", "have", "been",
    "were", "will", "shall", "unto", "upon", "your", "ours", "thee", "thou",
    "thy", "and", "for", "not", "but", "all", "any", "who", "whom", "his",
    "her", "its", "our", "you", "she", "him", "was", "are", "did", "does",
    "into", "over", "only", "surely", "truly", "behold", "indeed",
}

HEAD_RE = re.compile(r"^## S\u016brah (.+?) (\d+):(\d+)$", re.M)


def norm(s):
    """NFKC, fold punctuation, drop markup, lowercase."""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    # strip markdown emphasis and the Quranic transliTeration marks
    s = re.sub(r"[*_`~\u0670\u0653\u02f9\u02ba\u02be\u02bf]", " ", s)
    s = re.sub(r"[^\w\s-]", " ", s)
    return s.lower()


def toks(s, minlen=4):
    return [t for t in norm(s).split() if len(t) >= minlen and t not in STOP]


def body_lines(block):
    """Prose lines only: drop blockquotes (translations, cross-refs) and bold
    mini-heading lines."""
    out = []
    for ln in block.split("\n"):
        st = ln.strip()
        if not st:
            continue
        if st.startswith(">"):          # blockquote = translation / cross-ref
            continue
        if st.startswith("**") and st.endswith("**"):
            # Mini-heading: strip the bold markers but KEEP the words. Headings
            # carry the verse's own vocabulary (e.g. 040.md v3's headings are
            # "Forgiver of Sin", "Accepter of Repentance", ...), so dropping them
            # produced false positives at 0% echo for on-topic sections.
            out.append(st.strip("*").strip())
            continue
        if st == "---":
            continue
        out.append(st)
    return "\n".join(out)


def echo_rate(translation, body):
    """Fraction of the translation's distinctive tokens echoed in the body."""
    t = set(toks(translation, 4))
    if len(t) < 3:
        return None, 0
    b = set(norm(body).split())
    if not b:
        return None, 0
    hit = t & b
    return len(hit) / len(t), len(t)


def scan_file(path):
    txt = open(path, encoding="utf-8").read()
    heads = list(HEAD_RE.finditer(txt))
    rows = []
    for i, m in enumerate(heads):
        start = m.end()
        stop = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
        block = txt[start:stop]

        tm = re.search(r"^> \*\*(.+?)\*\*\s*$", block, re.M)
        if not tm:
            continue
        translation = tm.group(1)

        # body = everything after the translation line
        body = body_lines(block[tm.end():])
        if not body.strip():
            continue

        rate, nt = echo_rate(translation, body)
        if rate is None:
            continue
        rows.append((int(m.group(3)), rate, nt, len(body.split())))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sura", type=int, default=None)
    ap.add_argument("--threshold", type=float, default=0.15)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    if a.sura:
        paths = [os.path.join(ROOT, "expanded", f"{a.sura:03d}.md")]
    else:
        paths = sorted(glob.glob(os.path.join(ROOT, "expanded", "*.md")))

    examined = 0
    flagged = []
    per_file = []

    for p in paths:
        if not os.path.exists(p):
            print(f"ERROR: no such file {p}", file=sys.stderr)
            return 1
        rows = scan_file(p)
        examined += len(rows)
        bad = [r for r in rows if r[1] < a.threshold]
        name = os.path.basename(p)
        per_file.append((name, len(bad), len(rows)))
        for v, rate, nt, wc in bad:
            flagged.append((name, v, rate, nt, wc))

    # --- the count is the whole point; print it first ---
    print(f"files: {len(paths)}   sections examined: {examined}   "
          f"threshold: <{a.threshold:.0%} echo")
    if examined == 0:
        print("FAILURE: examined 0 sections -- sweep is a no-op, result is meaningless")
        return 1
    print()

    if a.verbose or a.sura:
        for name, nb, n in sorted(per_file, key=lambda r: -r[1]):
            if nb:
                print(f"  {name}: {nb} flagged of {n}")
        print()

    if flagged:
        print(f"flagged: {len(flagged)}")
        for name, v, rate, nt, wc in sorted(flagged):
            print(f"  {name} v{v}: echo {rate:.1%}  ({nt} distinctive tokens, {wc}w body)")
    else:
        print("flagged: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
