#!/usr/bin/env python3
"""Splice regenerated content into expanded/026.md.

1. Trims the five refrain verses whose text was merged into the preceding verse
   (103, 121, 139, 174, 190) back to their own text.
2. Replaces the 36 empty sections with regenerated commentary.
3. Re-emits the file in the canonical 001.md structure.
"""
import os, re, sys, importlib.util

ROOT = "/home/user/new"
EXP = os.path.join(ROOT, "expanded")
INI = os.path.join(ROOT, "initial")
TARGET = os.path.join(EXP, "026.md")
NUM = 26
NAME = "al-Shuʿarāʾ"
EC = "**Expanded Commentary**"

VH = re.compile(r'^## Sūrah .+? \d+:(\d+)$')

# --- verses whose translation absorbed the next verse's text ---
MERGE_TRIM = {103, 121, 139, 174, 190}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def source_verses():
    """Ground-truth verse text from initial/026.md."""
    raw = open(os.path.join(INI, "026.md"), encoding="utf-8").read().replace("\r\n", "\n")
    out = {}
    cur = None
    for ln in raw.split("\n"):
        m = re.match(r'^> \*\*(\d+)\*\*\s*(.*)$', ln)
        if m:
            cur = int(m.group(1))
            out[cur] = [m.group(2).strip()] if m.group(2).strip() else []
        elif re.match(r'^\*\*\d+\*\*\s', ln) or ln.startswith(("***", "#")):
            cur = None
        elif cur and ln.strip() and not ln.startswith(">"):
            out[cur].append(ln.strip())
    return {k: " ".join(v).strip() for k, v in out.items()}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    secs = {}
    for fn in ("content_026_a.py", "content_026_b1.py", "content_026_b2.py", "content_026_cde.py"):
        mod = load_module(os.path.join(here, fn), fn[:-3])
        dup = set(secs) & set(mod.SECTIONS)
        if dup:
            print(f"ERROR: duplicate verses in {fn}: {sorted(dup)}")
            return 1
        secs.update(mod.SECTIONS)
    print(f"loaded {len(secs)} regenerated sections")

    src = source_verses()
    # every regenerated verse must have source text
    missing = [v for v in secs if v not in src]
    if missing:
        print(f"ERROR: no source text for verses {missing}")
        return 1

    lines = open(TARGET, encoding="utf-8").read().split("\n")
    idx = [(i, int(VH.match(l).group(1))) for i, l in enumerate(lines) if VH.match(l)]
    parsed = []
    for k, (i, v) in enumerate(idx):
        e = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
        parsed.append((v, lines[i + 1:e]))

    preamble = lines[:idx[0][0]]
    replaced = trimmed = 0
    out = [l for l in preamble]

    for v, body in parsed:
        nb = [b for b in body if b.strip()]
        # current translation line
        cur_tr = None
        if nb and nb[0].lstrip().startswith("> "):
            m = re.match(r'^> \*\*(.+?)\*\*\s*$', nb[0].strip())
            cur_tr = m.group(1) if m else nb[0][2:].strip()

        # 1. trim merged refrain verses back to their own source text
        if v in MERGE_TRIM and cur_tr:
            want = src[v].strip()
            if want and want not in cur_tr.replace("**", ""):
                pass  # leave alone if source text is not recognisably present
            elif cur_tr.replace("**", "").strip() != want:
                newbody = list(body)
                for j, b in enumerate(newbody):
                    if b.lstrip().startswith("> **"):
                        newbody[j] = f"> **{want}**"
                        trimmed += 1
                        print(f"  v{v}: trimmed merged translation -> {want[:70]!r}")
                        break
                body = newbody

        # 2. replace empty sections with regenerated content
        wordcount = len(" ".join(body).split())
        if v in secs and wordcount < 40:
            tr, blocks = secs[v]
            newbody = ["", f"> **{tr}**", "", EC, ""]
            for heading, paras in blocks:
                newbody.append(f"**{heading}**")
                newbody.append("")
                for p in paras:
                    newbody.append(p)
                    newbody.append("")
            body = newbody
            replaced += 1
        elif v in secs:
            print(f"  WARNING: v{v} was not empty ({wordcount} words); left untouched")

        out.append(f"## Sūrah {NAME} {NUM}:{v}")
        out.extend(body)

    res = "\n".join(out)
    # collapse 3+ blank lines
    res = re.sub(r"\n{3,}", "\n\n", res)
    # ensure '---' immediately precedes each verse heading, with a blank before it
    res = re.sub(r"\n+---\n+## Sūrah", "\n\n---\n## Sūrah", res)
    res = re.sub(r"(?<!\n---)\n(## Sūrah " + re.escape(NAME) + r" \d+:\d+)", r"\n\n---\n\1", res)
    res = re.sub(r"\n{3,}", "\n\n", res)
    res = res.rstrip("\n") + "\n"

    open(TARGET, "w", encoding="utf-8", newline="\n").write(res)
    print(f"\nreplaced {replaced} empty sections, trimmed {trimmed} merged translations")
    return 0


sys.exit(main())
