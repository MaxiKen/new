#!/usr/bin/env python3
"""
fix_quotetags.py — insert the (C:V) citation the style requires after every
Qur'anic quotation that currently lacks one.

How it works: every run of quoted text (>=6 words) is matched against an index
of 8-word phrases built from ALL of translation/*.txt. A quotation that matches
exactly is a Qur'anic quotation, so its reference is not a judgement call — it
is whichever verse contains those words. The tag is inserted after the closing
quote mark (and after the italic marker, if present), matching the house style
`*“…”* (7:19)`.

Verification: the edit is applied to a copy first and the script asserts that
old and new differ ONLY by the inserted tag strings. If any other byte changed,
it refuses to write.

  fix_quotetags.py <chap>            dry run
  fix_quotetags.py <chap> --apply    write new/<chap>.md
"""
import re, sys, glob, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_WORDS = 6


def norm(s):
    for a, b in (("“", '"'), ("”", '"'), ("’", "'"), ("‘", "'")):
        s = s.replace(a, b)
    s = re.sub(r"[˹˺\[\]*]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def build_index():
    idx = {}
    for path in sorted((ROOT / "translation").glob("*.txt")):
        c = int(path.stem)
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^\s*(\d+)\s*\|\s*(.*)$", line)
            if not m:
                continue
            w = norm(m.group(2)).lower().split()
            for i in range(max(1, len(w) - MIN_WORDS + 1)):
                idx.setdefault(" ".join(w[i:i + MIN_WORDS]), set()).add((c, int(m.group(1))))
    return idx


TAG = re.compile(r"\(\s*\d{1,3}:\d{1,3}")


def translation_lines(chap):
    out = {}
    pth = ROOT / "translation" / f"{chap}.txt"
    for line in pth.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\d+)\s*\|\s*(.*)$", line)
        if m:
            out[int(m.group(1))] = norm(m.group(2)).lower()
    return out


def find_edits(text, idx, chap):
    tr_line = translation_lines(chap)
    edits, ambiguous = [], []
    ms = list(re.finditer(r"^## Sūrah .+?:(\d+)\s*$", text, re.M))
    for i, m in enumerate(ms):
        e = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        v = int(m.group(1))
        body_raw = text[m.end():e]
        bq = re.match(r"\s*((?:\s*>.*(?:\n|$))+)\n?", body_raw)
        blocked = list(range(m.end(), m.end() + (bq.end() if bq else 0)))   # translation quote: off limits
        body = body_raw
        bold_spans = [(b.start(), b.end()) for b in re.finditer(r"^\*\*.*?\*\*\s*$", body, re.M)]
        for q in re.finditer(r"[“]([^”]{24,})[”]", body):
            st = m.end() + q.start()
            if st in blocked:
                continue                      # inside the translation blockquote
            if any(a <= q.start() < b for a, b in bold_spans):
                continue                      # mini-heading, not a quotation in prose
            raw = q.group(1)
            w = norm(raw).lower().rstrip('.;:,').strip().split()
            local = " ".join(w)
            if len(w) < MIN_WORDS:
                continue
            hits = set()
            for j in range(max(1, len(w) - MIN_WORDS + 1)):
                hits |= idx.get(" ".join(w[j:j + MIN_WORDS]), set())
            if not hits:
                continue
            if TAG.search(body[max(0, st - 260):q.end() + 200]):
                continue                      # already cited nearby
            cov = {c: sum(1 for j in range(max(1, len(w) - MIN_WORDS + 1))
                          if c in idx.get(" ".join(w[j:j + MIN_WORDS]), set())) for c in hits}
            # A tie is resolved deterministically, not by guesswork: if the exact phrase
            # occurs in the verse currently under commentary, it is a self-quotation and
            # its reference is that verse. Only true ties with no local match are skipped.
            if len(hits) > 1 and (int(chap), v) in hits and local in tr_line.get(v, ""):
                cov = {(int(chap), v): 10**6}
            ranked = sorted(cov.items(), key=lambda x: (-x[1], x[0]))
            if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
                ambiguous.append((v, raw[:60], sorted(cov)))
                continue
            (c, vv), _ = ranked[0]
            pos = body.find(raw, st)
            k = pos + len(raw)
            if body[k:k + 1] != "”":
                ambiguous.append((v, raw[:60], "closing quote not adjacent"))
                continue
            k += 1
            if body[k:k + 1] == "*":
                k += 1
            edits.append((m.end() + k, f" ({c}:{vv})", v, raw[:50], (c, vv)))
    return edits, ambiguous


def apply_chap(chap, do_apply=False):
    path = ROOT / "new" / f"{chap}.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    idx = build_index()
    edits, amb = find_edits(text, idx, chap)
    new = text
    for at, tag, *_ in sorted(edits, key=lambda x: -x[0]):
        new = new[:at] + tag + new[at:]
    # Exact verification: remove each tag again. Undoing in ascending order means every
    # tag still sits at its ORIGINAL offset (earlier ones are gone, later ones don't
    # shift it), so this proves the file changed by these insertions and nothing else.
    undo = new
    for at, tag, *_ in sorted(edits, key=lambda x: x[0]):
        if not re.fullmatch(r" \(\d{1,3}:\d{1,3}\)", tag):
            print(f"ABORT: malformed tag {tag!r}")
            return 2
        if undo[at:at + len(tag)] != tag:
            print(f"ABORT: insertion at {at} not where expected")
            return 2
        undo = undo[:at] + undo[at + len(tag):]
    if undo != text:
        print("ABORT: undo did not restore the original file — refusing to write")
        return 2
    print(f"{chap}: {len(edits)} citation tags inserted; verified insertions-only")
    print(f"{chap}: {len(amb)} ambiguous left for manual review")
    for a_ in amb:
        print("   manual:", a_)
    if do_apply:
        path.write_text(new, encoding="utf-8")
        print(f"APPLIED -> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(apply_chap(a[0], "--apply" in a))
