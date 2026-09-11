#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan expanded/ for leaked drafting scaffolding -- the author's own
deliberation left in the delivered prose.

This is a distinct defect class from the structural, translation, and
off-topic gates. It was found only by direct reading: no other checker
flags it, because the text is well-formed Markdown about the right verse.

Two patterns matter:
  * GENUINE  -- self-correction, citation-hunting, TODO markers, and the
    leaked [System Memory Check] trailer.
  * QUOTED   -- the same surface forms occurring inside quoted scripture
    or a character's speech. "Let me kill Moses" is Pharaoh's words
    (40:26); "Say: 'Wait -- we too are waiting'" is 6:158. These are NOT
    defects, so each hit is printed with context for a human to judge
    rather than being counted automatically.

Usage:
    python3 tools/quran-audit/check_scaffolding.py [--context N]
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GENUINE = [
    (r"\bWait\s*[—–-]\s*actually", "self-correction"),
    (r"\bLet me (?:correct|be careful|state it|write)", "self-correction"),
    (r"\?\s*—\s*(?:no|actually|wait)\b", "citation-hunting"),
    (r"\bSystem Memory Check\b", "leaked directive"),
    (r"\bTODO\b|\bFIXME\b|\bTBD\b|\bXXX\b", "marker"),
    (r"\bplaceholder\b|\[insert", "marker"),
    (r"\bI should be about\b|\bI need to write\b", "drafting"),
    (r"\bNote to self\b", "drafting"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", type=int, default=110,
                    help="characters of surrounding text to print")
    ap.add_argument("--sura", type=int, default=None)
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(ROOT, "expanded", "*.md")))
    if a.sura:
        files = [f for f in files if os.path.basename(f) == f"{a.sura:03d}.md"]

    files_examined = 0
    total = 0
    for path in files:
        text = open(path, encoding="utf-8").read()
        files_examined += 1
        hits = []
        for rx, kind in GENUINE:
            for m in re.finditer(rx, text):
                ln = text[: m.start()].count("\n") + 1
                lo = max(0, m.start() - a.context)
                hits.append((ln, kind, text[lo:m.end() + a.context].replace("\n", " ")))
        if hits:
            print(f"{os.path.basename(path)}: {len(hits)} hit(s)")
            for ln, kind, ctx in sorted(hits):
                print(f"  L{ln} [{kind}] …{ctx}…")
            total += len(hits)

    print(f"\nfiles examined: {files_examined}   candidate hits: {total}")
    if total:
        print("NOTE: each hit needs reading. Quoted scripture and a character's")
        print("speech produce the same surface forms and are not defects.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
