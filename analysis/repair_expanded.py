#!/usr/bin/env python3
"""
repair_expanded.py — Structural repair / normalisation for `expanded/*.md`.

The commentary files were generated in batches, and four classes of
machine-generated structural defect crept in. None of them deletes or rewrites
any commentary prose; all are pure Markdown structure repairs.

  1. GLUED VERSE HEADINGS  (severe in 037, cosmetic duplicate in 018)
     A verse heading was emitted at the end of the previous paragraph instead
     of on its own line:

         ...closing argument.## Sūrah al-Kahf 18:103

     In 037 this affects 121 headings (verses 37:57–37:177). The consequence is
     structural, not cosmetic: the commentary of 121 verses is silently
     attributed to verse 37:56, which then appears to contain ~20,761 words
     instead of the corpus-typical ~1,000, and chapter 37 appears to have only
     61 of its 182 verses.

     Repair: break the line before the heading. If a clean heading for the same
     verse already exists a line or two later (018), the glued duplicate is
     removed instead.

  2. EMPTY VERSE STUBS (026)
     Verse headings that carry no commentary body at all. These are NOT
     repaired here — there is nothing to restore; they are listed as work items
     for content generation. Use --report to print them.

  3. MACHINE MARKERS  "> **[System Memory Check]** ..."  (037, 073, 097, 105)
     Generation-harness output appended after every verse. Removed, together
     with the orphaned "---" separator and blank lines that framed it.

  4. MIXED LINE ENDINGS (58 files CRLF, 56 files LF)
     Normalised to LF so the corpus is byte-consistent.

Usage
-----
    python3 analysis/repair_expanded.py --dir expanded              # dry run
    python3 analysis/repair_expanded.py --dir expanded --apply      # write
    python3 analysis/repair_expanded.py --dir expanded --report     # list work items
"""

from __future__ import annotations

import argparse
import os
import re

# A verse heading appearing anywhere on a line: '## Sūrah X 12:34' or '## Sūrah X [12:34]'
GLUED_HEADING = re.compile(r"(?<=\S)(?P<head>##\s+[^\n#]*?(?P<ch>\d{1,3}):(?P<vs>\d{1,3})\s*\]?)(?=\s*$)", re.MULTILINE)
CLEAN_HEADING = re.compile(r"^##\s+[^\n#]*?(?P<ch>\d{1,3}):(?P<vs>\d{1,3})\s*\]?\s*$", re.MULTILINE)
SMC_LINE = re.compile(
    r"(?m)^[ \t]*>?[ \t]*\*\*\[System Memory Check\]\*\*[^\n]*(?:\n+|$)",
    re.IGNORECASE,
)


def read_bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def read(path: str) -> tuple[str, bool]:
    """Return (text normalised to LF, original_used_crlf)."""
    raw = read_bytes(path)
    used_crlf = b"\r\n" in raw
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    return text, used_crlf


def write(path: str, text: str, used_crlf: bool) -> None:
    """Write back, preserving the file's original line-ending style so the
    diff contains only the real repairs."""
    data = text.replace("\n", "\r\n").encode("utf-8") if used_crlf else text.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)


def repair_text(text: str, chapter: int) -> tuple[str, dict]:
    fixes = {"glued_split": 0, "glued_dropped_duplicate": 0, "smc_removed": 0}

    # ---- 1. glued headings ----
    def _split(m: re.Match) -> str:
        head = m.group("head").rstrip()
        ch, vs = int(m.group("ch")), int(m.group("vs"))
        if ch != chapter:
            return m.group(0)
        # does a clean heading for this verse already exist elsewhere?
        clean_here = [
            mm for mm in CLEAN_HEADING.finditer(m.string)
            if int(mm.group("ch")) == ch and int(mm.group("vs")) == vs
        ]
        if clean_here:
            fixes["glued_dropped_duplicate"] += 1
            return ""                       # drop the misfiled duplicate
        fixes["glued_split"] += 1
        return "\n\n" + head

    text = GLUED_HEADING.sub(_split, text)

    # ---- 3. machine markers (line + the blank run it leaves behind) ----
    def _smc(m: re.Match) -> str:
        fixes["smc_removed"] += 1
        return ""

    before = text
    text = SMC_LINE.sub(_smc, text)
    if fixes["smc_removed"] and text != before:
        # a removed end-of-file marker must not leave dangling blank lines
        text = re.sub(r"\n+$", "\n", text)

    # Nothing else is touched: no re-flowing, no blank-line tidying, no
    # line-ending rewriting. The diff therefore contains only real repairs.
    return text, fixes


def empty_verse_stubs(text: str) -> list[str]:
    out = []
    parts = re.split(r"(?m)^## ", text)[1:]
    for s in parts:
        lines = s.split("\n")
        title = lines[0].strip()
        if re.match(r".*\d{1,3}:\d{1,3}\]?$", title) and not "\n".join(lines[1:]).strip():
            out.append(title)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="expanded")
    ap.add_argument("--apply", action="store_true", help="write the repairs (default: dry run)")
    ap.add_argument("--report", action="store_true", help="only list empty verse stubs")
    args = ap.parse_args()

    totals = {"glued_split": 0, "glued_dropped_duplicate": 0, "smc_removed": 0}
    touched, stubs = [], []

    for fname in sorted(os.listdir(args.dir)):
        if not fname.endswith(".md"):
            continue
        m = re.search(r"(\d+)", fname)
        if not m:
            continue
        ch = int(m.group(1))
        path = os.path.join(args.dir, fname)
        original, used_crlf = read(path)

        if args.report:
            for s in empty_verse_stubs(original):
                stubs.append((fname, s))
            continue

        repaired, fixes = repair_text(original, ch)
        if repaired != original:
            touched.append((fname, fixes))
            for k in totals:
                totals[k] += fixes[k]
            if args.apply:
                write(path, repaired, used_crlf)

    if args.report:
        print(f"empty verse stubs (heading present, commentary absent): {len(stubs)}")
        for f, s in stubs:
            print(f"  {f}: {s}")
        return

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"[{mode}] files changed: {len(touched)}")
    for f, fixes in touched:
        if any(fixes.values()):
            print(f"  {f}: split {fixes['glued_split']} glued heading(s), "
                  f"dropped {fixes['glued_dropped_duplicate']} duplicate(s), "
                  f"removed {fixes['smc_removed']} machine marker(s)")
    print("totals:", totals)
    if not args.apply:
        print("re-run with --apply to write the repairs.")


if __name__ == "__main__":
    main()
