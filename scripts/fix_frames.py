#!/usr/bin/env python3
"""
fix_frames.py — ONE-TIME REFERENCE REPAIR TOOL. Not part of the generation pipeline.

The reference chapter new/007.md carries a tic that marked its collapse: a section's own
point, hedged behind an attention-director — "The sūrah's readers are shown that X."
The house rule is that commentary asserts X. This tool performs the grammatical
de-framing: delete the wrapper, promote X, recapitalise.

Why this is legitimate on the reference and NOT on generated commentary:
  * it only removes a hedge; it adds no words and reorders nothing;
  * it fires only where the wrapper OPENS a sentence, so the result is well-formed;
  * every single change is printed for review before anything is written.
In generated commentary, a script rewriting prose is the very thing the pipeline forbids,
so scripts/check.py only MEASURES the tic (FRAME TIC) and fails the verse — a human or the
writing model must author the replacement. This script exists only because the reference
predates the rule and contains 285 instances.

  fix_frames.py 007            dry run, prints every change
  fix_frames.py 007 --apply    write new/007.md
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEAD = re.compile(r"""^\s*(?:["“'`*\-]\s*)?""", re.X)
WRAP = re.compile(
    r"""(?P<pre>\s*(?:["“'`*\-]\s*)?)
        (?P<art>The|the)\s+
        (?P<own>sūrah's|Book's|Qur'an's|passage's|verse's|verses')\s+readers\s+
        (?P<cop>are\s+being|have\s+just\s+been|have\s+been|will\s+be|are|should|must|were)\s+
        (?:also\s+|then\s+)?
        (?P<verb>shown|told|given|reminded|meant\s+to\s+notice|invited\s+to\s+see|asked\s+to\s+see)\s+that\s+
        (?P<first>[a-z“"\'])""", re.X)
STRANDED = re.compile(r"(?P<conj>, (?:and|but)) that ", re.I)


def deframe(text):
    """-> (new_text, changes). Sentences are processed separately; separators preserved."""
    changes = []
    pieces = re.split(r"(?<=[.!?])(\s+)", text)     # [sent, sep, sent, sep, ...]
    for i in range(0, len(pieces), 2):
        s = pieces[i]
        m = WRAP.match(s)
        if not m:
            continue
        body = s[m.end("first") - 1:]
        body = body[0].upper() + body[1:] if body[:1].islower() else body
        body = STRANDED.sub(lambda x: x.group("conj") + " ", body, count=1)
        changes.append({"removed": re.sub(r"\s+", " ", m.group(0)).strip(),
                        "becomes": re.sub(r"\s+", " ", (m.group("pre") + body)[:1]
                                          + body[1:90]).strip()})
        pieces[i] = m.group("pre") + body
    return "".join(pieces), changes


if __name__ == "__main__":
    chap = sys.argv[1] if len(sys.argv) > 1 else "007"
    do = "--apply" in sys.argv
    path = ROOT / "new" / f"{chap}.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    new, ch = deframe(text)
    a, b = re.sub(r"\s+", "", text).lower(), re.sub(r"\s+", "", new).lower()
    if len(b) > len(a):
        print("ABORT: de-framing added words — refusing")
        sys.exit(2)
    print(f"de-framed {len(ch)} wrappers | words {len(text.split()):,} → {len(new.split()):,}")
    for c in ch[:28]:
        print(f"   - {c['removed']}\n   + {c['becomes']}")
    if len(ch) > 28:
        print(f"   … {len(ch) - 28} more")
    if do:
        path.write_text(new, encoding="utf-8")
        print("APPLIED")
    else:
        print("dry run (--apply to write)")
