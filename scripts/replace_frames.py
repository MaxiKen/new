#!/usr/bin/env python3
"""
replace_frames.py — apply writer-authored replacements for reader-frame sentences.

The frame tic in the reference is a SYNTACTIC habit ("the sūrah's readers are shown
that X"), and the only honest repair is to re-cast each sentence individually. This
tool exists to make that safe at volume:

  * replacements are addressed by position (the k-th frame in verse V), so a sentence
    that occurs more than once in the chapter can never be edited in the wrong place;
  * every verse must supply exactly as many replacements as it has frames — no silent
    partial pass, and no new tic smuggled in by leaving one of three in place;
  * the tool verifies that bytes outside the replaced spans are untouched, and aborts
    otherwise;
  * it rejects any replacement that still contains the frame, or that merely swaps the
    frame for a different fixed opener (the MONOTONY gate in check.py catches that later).

Input JSON:  { "<verse>": ["replacement 1", "replacement 2", ...], ... }

  replace_frames.py 007 /tmp/f.json            dry run
  replace_frames.py 007 /tmp/f.json --apply     write
"""
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util
_spec = importlib.util.spec_from_file_location("ck", ROOT / "scripts" / "check.py")
ck = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ck)


def main(chap, jf, do=False):
    path = ROOT / "new" / f"{chap}.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    want = json.loads(Path(jf).read_text(encoding="utf-8"))
    ms = list(re.finditer(r"^## Sūrah .+?:(\d+)\s*$", text, re.M))
    spans = {}
    for i, m in enumerate(ms):
        e = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        spans[int(m.group(1))] = (m.end(), e)

    edits = []
    for verse_s, repls in want.items():
        v = int(verse_s)
        if v not in spans:
            print(f"ABORT: verse {chap}:{v} not found"); return 1
        s, e = spans[v]
        found = list(ck.FRAME.finditer(text, s, e))
        if len(found) != len(repls):
            print(f"ABORT 7:{v}: file has {len(found)} frames, you supplied {len(repls)} "
                  f"— every frame in a verse must be handled")
            return 1
        for m, new in zip(found, repls):
            old = text[m.start():m.end()]
            if re.search(r"readers (?:are|have|should|must|will)", new, re.I):
                print(f"ABORT 7:{v}: replacement still contains a reader-frame: {new[:70]}")
                return 1
            if not new.strip():
                print(f"ABORT 7:{v}: empty replacement — deletions must be authored in apply_edits.py")
                return 1
            edits.append((m.start(), m.end(), old, new.strip(), v))

    new_text = text
    for st, en, old, new, v in sorted(edits, key=lambda x: -x[0]):
        new_text = new_text[:st] + new + new_text[en:]

    # prove only the addressed spans moved: rebuild the original from the new text
    # Undo in ASCENDING order: edits left of the current one are still applied and have
    # shifted nothing to their left, so after each undo the following edit sits again at
    # its original offset. Descending here would double-count the length changes.
    check = new_text
    for st, en, old, new, v in sorted(edits, key=lambda x: x[0]):
        check = check[:st] + old + check[st + len(new):]
    if check != text:
        print("ABORT: reconstruction mismatch — edits were not isolated to their spans")
        return 2

    aw, bw = len(text.split()), len(new_text.split())
    print(f"{len(edits)} frame sentences re-cast across {len(want)} verses | words {aw:,} → {bw:,}")
    for st, en, old, new, v in edits[:40]:
        print(f"\n  7:{v} − {re.sub(chr(92)+'s+',' ',old).strip()[:150]}")
        print(f"  7:{v} + {re.sub(chr(92)+'s+',' ',new)[:150]}")
    if do:
        path.write_text(new_text, encoding="utf-8")
        print("\nAPPLIED")
    else:
        print("\ndry run (--apply to write)")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(a[0], a[1], "--apply" in a))
