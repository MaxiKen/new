#!/usr/bin/env python3
"""Append a mini-heading block to existing verse sections.

Usage: append_block.py <sura_no> <module.py>

Module exposes:
    SURAH, NUM
    BLOCKS = {verse: (mini_heading, [para, ...])}

The block is inserted at the end of the section body, before the trailing
separator, leaving the existing content untouched.
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
    m = load(sys.argv[2], os.path.basename(sys.argv[2])[:-3])
    surah, blocks = m.SURAH, m.BLOCKS

    txt = open(target, encoding="utf-8").read()
    h1 = re.search(r'^# Sūrah (.+?) \(Chapter \d+\)', txt, re.M).group(1)
    assert h1 == surah, f"module SURAH {surah!r} != H1 {h1!r}"

    VH = re.compile(rf'^## Sūrah {re.escape(surah)} {num}:(\d+)$')
    lines = txt.split("\n")
    idx = [(i, int(VH.match(l).group(1))) for i, l in enumerate(lines) if VH.match(l)]

    done = 0
    for k in range(len(idx) - 1, -1, -1):
        i, v = idx[k]
        if v not in blocks:
            continue
        e = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
        heading, paras = blocks[v]
        add = [f"**{heading}**", ""]
        for p in paras:
            add += [p, ""]
        # find the last non-empty line of the body and insert after it
        j = e - 1
        while j > i and not lines[j].strip():
            j -= 1
        lines[j + 1:j + 1] = [""] + add
        done += 1

    res = "\n".join(lines)
    res = re.sub(r"\n{3,}", "\n\n", res)
    res = re.sub(r"\n+---\n+## Sūrah", "\n\n---\n## Sūrah", res)
    res = re.sub(r"(?<!\n---)\n(## Sūrah " + re.escape(surah) + r" "
                 + str(num) + r":\d+)", "\n\n---\n\\1", res)
    res = re.sub(r"\n{3,}", "\n\n", res)
    res = res.rstrip("\n") + "\n"
    open(target, "w", encoding="utf-8", newline="\n").write(res)
    print(f"{os.path.basename(target)}: appended 4th block to {done} sections")
    return 0


sys.exit(main())
