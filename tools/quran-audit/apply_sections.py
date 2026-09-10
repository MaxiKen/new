#!/usr/bin/env python3
"""Splice regenerated commentary into an expanded/ file.

Usage: apply_sections.py <sura_no> <module.py> [<module2.py> ...]

Each module exposes:
    SURAH   = "al-Anbiyāʾ"           (must match the file's H1)
    NUM     = 21
    SECTIONS = {verse: (translation_or_None, [(mini_heading, [para, ...]), ...])}

translation_or_None  -> None keeps the existing translation line
                        str  replaces it (used to repair wrong verse text)
"""
import os, re, sys, importlib.util

ROOT = "/home/user/new"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    num = int(sys.argv[1])
    target = os.path.join(ROOT, "expanded", f"{num:03d}.md")
    mods = [load(p, os.path.basename(p)[:-3]) for p in sys.argv[2:]]

    secs, surah, fnum = {}, None, None
    for m in mods:
        assert m.NUM == num, f"{m.__name__}: NUM {m.NUM} != {num}"
        surah = m.SURAH
        fnum = m.NUM
        dup = set(secs) & set(m.SECTIONS)
        if dup:
            print(f"ERROR duplicate verses: {sorted(dup)}")
            return 1
        secs.update(m.SECTIONS)

    txt = open(target, encoding="utf-8").read()
    h1 = re.search(r'^# Sūrah (.+?) \(Chapter \d+\)', txt, re.M).group(1)
    assert h1 == surah, f"module SURAH {surah!r} != H1 {surah!r}"

    EC = "**Expanded Commentary**"
    VH = re.compile(rf'^## Sūrah {re.escape(surah)} {fnum}:(\d+)$')
    lines = txt.split("\n")
    idx = [(i, int(VH.match(l).group(1))) for i, l in enumerate(lines) if VH.match(l)]

    # rebuild from the end so line indices stay valid
    done_tr = done_body = 0
    for k in range(len(idx) - 1, -1, -1):
        i, v = idx[k]
        if v not in secs:
            continue
        e = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
        tr, blocks = secs[v]

        body = [""]
        if tr is None:
            nb = [b for b in lines[i + 1:e] if b.strip()]
            m = re.match(r'^> \*\*(.+?)\*\*\s*$', nb[0].strip())
            body.append(f"> **{m.group(1)}**")
        else:
            body.append(f"> **{tr}**")
            done_tr += 1
        body += ["", EC, ""]
        for heading, paras in blocks:
            body.append(f"**{heading}**")
            body.append("")
            for p in paras:
                body.append(p)
                body.append("")
        lines[i + 1:e] = body
        done_body += 1

    res = "\n".join(lines)
    res = re.sub(r"\n{3,}", "\n\n", res)
    # normalise existing separators, then re-insert any separator the splice consumed
    res = re.sub(r"\n+---\n+## Sūrah", "\n\n---\n## Sūrah", res)
    res = re.sub(r"(?<!\n---)\n(## Sūrah " + re.escape(surah) + r" "
                 + str(fnum) + r":\d+)", "\n\n---\n\\1", res)
    res = re.sub(r"\n{3,}", "\n\n", res)
    res = res.rstrip("\n") + "\n"
    open(target, "w", encoding="utf-8", newline="\n").write(res)
    print(f"{os.path.basename(target)}: {done_body} sections rewritten, "
          f"{done_tr} translations replaced")
    return 0


sys.exit(main())
