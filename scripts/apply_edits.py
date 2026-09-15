#!/usr/bin/env python3
"""
apply_edits.py — apply AUTHOR-EDITED sentence replacements to a chapter file.

This exists so that hand-written fixes are safe at scale. The AI (or the human)
authors a list of {"old": ..., "new": ...} pairs; this tool refuses to write unless
every `old` string occurs EXACTLY ONCE in the file, so nothing can be applied to the
wrong verse and no prose can be silently reworded twice.

It is a repair tool for the reference standard, NOT a generation tool: it only ever
applies edits that a writer authored. Generated commentary must be written verse by
verse by the model; scripts/check.py measures it. This tool never invents text.

  apply_edits.py <chap> <edits.json>          dry run (validate only)
  apply_edits.py <chap> <edits.json> --apply  write new/<chap>.md

edits.json  =  [{"old": "...", "new": "...", "note": "optional"}, ...]
"""
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(chap, jf, do=False):
    path = ROOT / "new" / f"{chap}.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    edits = json.loads(Path(jf).read_text(encoding="utf-8"))
    bad = []
    for k, e in enumerate(edits):
        old = e["old"]
        n = text.count(old)
        if n != 1:
            bad.append((k, n, old[:90]))
    if bad:
        for k, n, o in bad:
            print(f"  REJECT edit #{k}: {n} occurrences of {o!r}")
        print(f"ABORT: {len(bad)}/{len(edits)} edits are not unique — refusing to write")
        return 1
    new = text
    for e in edits:
        new = new.replace(e["old"], e["new"], 1)
    # structural invariants that no prose edit may break
    for pat, name in [(r"^## Sūrah .+?:\d+\s*$", "verse headings"),
                      (r"^\*\*.+?\*\*\s*$", "mini-headings")]:
        a = len(re.findall(pat, text, re.M))
        b = len(re.findall(pat, new, re.M))
        tol = e.get("headings", 0) if False else 0
        if name == "verse headings" and a != b:
            print(f"ABORT: verse heading count changed {a} -> {b}")
            return 2
    aw, bw = len(text.split()), len(new.split())
    print(f"{len(edits)} edits applied | words {aw:,} → {bw:,} ({bw-aw:+d})")
    for e in edits[:12]:
        print("   -", re.sub(r"\s+", " ", e["old"])[:88])
        print("   +", re.sub(r"\s+", " ", e["new"])[:88])
    if len(edits) > 12:
        print(f"   … {len(edits)-12} more")
    if do:
        path.write_text(new, encoding="utf-8")
        print("APPLIED")
    else:
        print("dry run (--apply to write)")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(a[0], a[1], "--apply" in a))
