#!/usr/bin/env python3
"""
check.py — the authoritative gate for the tafsir pipeline.

WHY THESE NUMBERS AND NOT OTHERS
Every threshold is measured on the healthy body of the reference chapter
(new/007.md verses 1-117) — the text the author actually approved — and every
one sits in an empty gap between that body and the drifted tail (7:118-206).
A rule the reference itself violates is not a rule, it is a contradiction, and
models resolve contradictions by dropping the numbers.

  metric                     healthy 1-117      drifted 118-206    gate
  bold mini-headings/verse   mean 6.6, max 12   mean 14.6, max 22  <4 or >12 FAIL, >9 WARN
  MEDIAN section words       min 99,  mean 186  max 92.5, mean 66  >=115 FAIL, <130 WARN
  reader-frame tic /verse    max 1              mean 3.7, max 15   <=2 FAIL
  plain cross-ref headings   max 2              max 2              <=2 FAIL
  words/verse                ~1298              ~1250              950-2300
  6-gram overlap vs initial  0.16%              13.0% (expanded)   <=2.5% FAIL
  longest verbatim run       0-11 words         128 words          <25 FAIL

Commands
  check.py chapter <chap>            gate the merged chapter
  check.py verse   <chap> <v>        gate one verse
  check.py files   <chap>            gate new/verse/<chap>_NNN.md one by one
  check.py plan    <chap>            write repair queue to /tmp/<chap>.worklist.json
  check.py merge   <chap> [--apply]  STRUCTURAL ONLY: merge fragmented sections by
                                     deleting mini-heading lines. Asserts that no
                                     prose word is altered. Never rewrites prose.
  check.py frames  <chap>            print every reader-frame to be rewritten
  check.py stats   <chap>            zone statistics, no verdict
  check.py split   <kind> <chap>   cut a chapter into per-verse source chunks
Exit 0 = no FAILs (warnings allowed), 1 = FAILs present.
"""
import re, sys, json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAX_HEADINGS, MIN_HEADINGS = 12, 4
WARN_HEADINGS = 9
MEDIAN_MIN_FAIL, MEDIAN_MIN_WARN = 115, 130
MAX_FRAMES_FAIL = 2
MAX_XREF = 2
MIN_WORDS, MAX_WORDS = 950, 2300
SHINGLE_N, MAX_OVERLAP, MAX_RUN = 6, 2.5, 25
MERGE_TARGET_MEDIAN, MERGE_MAX_H = 165, 9

BANNED = ["in conclusion", "it is important to note", "it is worth noting",
          "it's worth noting", "in today's world", "delve", "tapestry",
          "testament to", "let us explore", "we will explore", "this essay",
          "as an ai", "certainly!", "i hope this", "great question",
          "navigate the", "unpack the", "rich tapestry", "in the modern world",
          "let's dive", "it is worth noting", "it is worth noticing",
          "it is worth pausing", "it is worth comparing", "it is worth setting",
          "it is worth isolating", "it should be noted that", "worth dwelling on",
          "the source material says", "the source says", "according to the source",
          "the source notes", "as noted in the source", "source material",
          "as per the source", "the source indicates", "according to the sources"]
# matched only at sentence start, where they are dead giveaways
LEAD_IN = ["to summarize", "in summary", "furthermore, it", "additionally, it"]
DEBRIS = ["TODO", "FIXME", "XXX", "[insert", "lorem ipsum", "placeholder",
          "**Note to self", "TBD", "<<<<<<<", "...continued", "[[", "]]"]
FRAME = re.compile(
    r"(?:the sūrah's|the Book's|the Qur'an's|the passage's|the verse's) readers "
    r"(?:are|have|should|must|will|get|gain|receive|encounter|find themselves|are meant)"
    r"[^.!?]{0,240}?[.!?]"
    r"|readers (?:are|have been|have just been) (?:given|shown|told|reminded|left|held|meant|invited)"
    r"[^.!?]{0,240}?[.!?]", re.I)
XREF_HEAD = re.compile(r'^[A-Z“"][^*.>#|!`]{8,88}$')


def norm(s):
    for a, b in (("“", '"'), ("”", '"'), ("’", "'"), ("‘", "'")):
        s = s.replace(a, b)
    s = re.sub(r"[˹˺\[\]*]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def shingles(text, n=SHINGLE_N):
    w = re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def longest_run(a, b):
    A = re.sub(r"[^a-z0-9 ]", " ", a.lower()).split()
    B = re.sub(r"[^a-z0-9 ]", " ", b.lower()).split()
    pos = {}
    for i, w in enumerate(B):
        pos.setdefault(w, []).append(i)
    cur, best = [0] * (len(B) + 1), 0
    for i in range(len(A)):
        nxt = [0] * (len(B) + 1)
        for j in pos.get(A[i], []):
            nxt[j + 1] = cur[j] + 1
            best = max(best, nxt[j + 1])
        cur = nxt
    return best


def verses(text):
    ms = list(re.finditer(r"^## Sūrah .+?:(\d+)\s*$", text, re.M))
    return [(int(m.group(1)), text[m.end():(ms[i + 1].start() if i + 1 < len(ms) else len(text))])
            for i, m in enumerate(ms)]


def parse(body):
    """-> (bold_heads, section_texts, xref_heads, xref_tail_text, main_prose).

    Two tiers exist in the reference and both are legal:
      1. main argument : **bold** mini-headings, each carrying a developed section
      2. cross-ref tail: 0-2 PLAIN Title-Case heading lines after the last bold
         heading, each introducing a short cross-reference. Tier 2 is NOT counted
         as a mini-heading (counting it would force heading inflation) and is NOT
         a defect (it is the reference's own convention, used in 36 verses).
    """
    bold = [m for m in re.finditer(r"^\*\*(.+?)\*\*\s*$", body, re.M)
            if m.group(1).strip() != "Expanded Commentary"]
    if not bold:
        return [], [], [], "", ""
    heads = [m.group(1).strip() for m in bold]
    bounds = [m.end() for m in bold] + [len(body)]
    chunks = [body[bounds[i]:bounds[i + 1]] for i in range(len(bold))]

    def is_xref(ls):
        return (bool(XREF_HEAD.match(ls)) and not ls.startswith(("**", ">"))
                and not ls.endswith((".", "?", "!", ":", ",")))

    xref, tail = [], ""
    lines = chunks[-1].split("\n")
    cut = next((i for i, ln in enumerate(lines) if is_xref(ln.strip())), None)
    if cut is not None:
        tail = "\n".join(lines[cut:])
        chunks[-1] = "\n".join(lines[:cut])
        xref = [ln.strip() for ln in tail.split("\n") if is_xref(ln.strip())]
    cleaned = [clean(c) for c in chunks]
    return heads, cleaned, xref, clean(tail), " ".join(cleaned)


def clean(c):
    c = re.sub(r"^\s*>.*$", "", c, flags=re.M)
    c = re.sub(r"^\s*---\s*$", "", c, flags=re.M)
    return c.strip()


def sect_lens(chunks):
    return [len(c.split()) for c in chunks if len(c.split()) > 0]


def check(v, body, chap, src_text=None, need_heading=True):
    errs, warns = [], []
    heads, chunks, xref, tail, main_prose = parse(body)
    all_prose = (main_prose + " " + tail).strip()
    words = len(body.replace("---", "").split())
    lens = sect_lens(chunks)
    med = statistics.median(lens) if lens else 0
    n_h = len(heads)
    if need_heading and not re.search(r"^## Sūrah .+?:\d+\s*$", body, re.M):
        errs.append("no `## Sūrah <Name> C:V` heading line")
    trp = ROOT / "translation" / f"{chap}.txt"
    if trp.exists():
        tr = {}
        for line in trp.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^\s*(\d+)\s*\|\s*(.*)$", line)
            if m:
                tr[int(m.group(1))] = m.group(2).strip()
        if v not in tr:
            errs.append(f"verse {chap}:{v} not in translation/{chap}.txt")
        else:
            m = re.search(r"(?:^\s*>.*(?:\n|$))+", body, re.M)
            got = norm(re.sub(r"^\s*>\s?", "", m.group(0), flags=re.M)) if m else ""
            if got != norm(tr[v]):
                errs.append("TRANSLATION not verbatim")
                warns.append(f"got : {got[:80]}\n        want: {norm(tr[v])[:80]}")
    if re.search(r"^###\s", body, re.M):
        errs.append("H3 `###` present — standard uses bold mini-headings, not H3")
    if n_h < MIN_HEADINGS:
        errs.append(f"HEADINGS {n_h} < {MIN_HEADINGS}")
    if n_h > MAX_HEADINGS:
        errs.append(f"HEADINGS {n_h} > {MAX_HEADINGS} (fragmented)")
    elif n_h > WARN_HEADINGS:
        warns.append(f"{n_h} headings (> {WARN_HEADINGS})")
    if lens and med < MEDIAN_MIN_FAIL:
        errs.append(f"FRAGMENTED median section {med:.0f}w < {MEDIAN_MIN_FAIL}w — merge adjacent sections")
    elif lens and med < MEDIAN_MIN_WARN:
        warns.append(f"thin sections: median {med:.0f}w")
    if words < MIN_WORDS:
        errs.append(f"WORDS {words} < {MIN_WORDS}")
    if words > MAX_WORDS:
        errs.append(f"WORDS {words} > {MAX_WORDS}")
    if len(xref) > MAX_XREF:
        errs.append(f"XREF {len(xref)} plain cross-ref headings > {MAX_XREF}")
    fr = FRAME.findall(all_prose)
    if len(fr) > MAX_FRAMES_FAIL:
        errs.append(f"FRAME TIC {len(fr)} reader-frame sentences (limit {MAX_FRAMES_FAIL})")
    elif len(fr):
        warns.append(f"{len(fr)} reader-frame sentence")
    if len(set(heads)) != n_h:
        errs.append(f"duplicate mini-headings {sorted({h for h in heads if heads.count(h)>1})}")
    for i in range(n_h - 1):
        if heads[i] == heads[i + 1]:
            errs.append("ADJACENT duplicate headings")
    low = " " + re.sub(r"\s+", " ", all_prose.lower()) + " "
    hits = sorted({b for b in BANNED if b in low})
    for lead in LEAD_IN:
        if re.search(r"(?:[.!?:]\s+|^)" + re.escape(lead), low):
            hits.append(lead)
    if hits:
        errs.append("BOILERPLATE " + ", ".join(hits[:5]))
    dh = sorted({d for d in DEBRIS if d.lower() in low})
    if dh:
        errs.append("DEBRIS " + ", ".join(dh))
    # MONOTONY: the generalized drift signature. The collapse did not repeat a word, it
    # repeated a SYNTACTIC SLOT ("the sūrah's readers are shown that X"), which no banned-
    # word list can catch. So measure it: count how often a verse reuses the same opening
    # two words, and how often every section ends on the same rhythm. This also polices
    # repairs: replacing one tic with a single new opener would trip it immediately.
    OPENER_N = 4          # reference's worst is 3; a repeated tic reads 7-10
    opens = [" ".join(re.sub(r"\W+", " ", s).strip().lower().split()[:OPENER_N])
             for s in re.split(r"(?<=[.!?])\s+", all_prose) if len(s.split()) > 6]
    opens = [o for o in opens if len(o.split()) == OPENER_N]
    if opens:
        top = max(set(opens), key=opens.count)
        if opens.count(top) > 4:
            errs.append(f"MONOTONY {opens.count(top)} sentences open with “{top}” — vary the syntax")
        elif opens.count(top) > 3:
            warns.append(f"{opens.count(top)} sentences open with “{top}”")
    bopen = [h.split()[0].lower() for h in heads if h.split()]
    if bopen:
        tb = max(set(bopen), key=bopen.count)
        if bopen.count(tb) > 4:
            warns.append(f"{bopen.count(tb)} mini-headings start with “{tb}”")
    sents = [re.sub(r"\W+", " ", s).strip().lower()
             for s in re.split(r"(?<=[.!?])\s+", all_prose) if len(s.split()) > 8]
    dup = len(sents) - len(set(sents))
    if dup > 1:
        errs.append(f"PADDING {dup} duplicated sentences")
    # untagged Qur'anic quotation of THIS chapter (prompt §12 demands the tag)
    trp2 = ROOT / "translation" / f"{chap}.txt"
    if trp2.exists():
        own = {}
        for line in trp2.read_text(encoding="utf-8", errors="replace").splitlines():
            mm = re.match(r"^\s*(\d+)\s*\|\s*(.*)$", line)
            if mm:
                own[int(mm.group(1))] = norm(mm.group(2)).lower()
        body_src = " ".join(own.values())
        # the first blockquote IS the verse under commentary; a tag inside it would be
        # wrong, so it is excluded from the scan (appendix cross-ref quotes are still checked)
        scan_body = re.sub(r"(?:^\s*>.*(?:\n|$))+", lambda m: "\n" * m.group(0).count("\n"), body, count=1, flags=re.M)
        untagged = 0
        hspans = [(b.start(), b.end()) for b in re.finditer(r"^\*\*.*?\*\*\s*$", scan_body, re.M)]
        for qm in re.finditer(r"[“]([^”]{24,})[”]", scan_body):
            if any(a <= qm.start() < b for a, b in hspans):
                continue          # quoted-phrase mini-heading, not a cited quotation
            lw = norm(qm.group(1)).lower().rstrip(".;:,").split()
            if len(lw) < 6:
                continue
            if " ".join(lw) in body_src:
                win = scan_body[max(0, qm.start() - 260):qm.end() + 200]
                if not re.search(r"\(\s*\d{1,3}:\d{1,3}", win):
                    untagged += 1
        if untagged:
            errs.append(f"QUOTETAG {untagged} untagged Qur'anic quotation(s) — run fix_quotetags.py")
    if src_text:
        own = all_prose
        A, B = shingles(own), shingles(src_text)
        ov = 100 * len(A & B) / max(1, len(A))
        if ov > MAX_OVERLAP:
            errs.append(f"OVERLAP {ov:.2f}% > {MAX_OVERLAP}% vs initial/ — transformed, not rewritten")
        run = longest_run(own, src_text)
        if run >= MAX_RUN:
            errs.append(f"VERBATIM {run}-word run copied from initial/ (limit {MAX_RUN})")
    info = dict(verse=v, words=words, headings=n_h, med=round(med), xref=len(xref),
                frames=len(fr), lens=lens)
    return errs, warns, info


def _load_src(chap, v, mode):
    if mode == "off":
        return None
    p = ROOT / "source_by_verse" / chap / f"{chap}_{v:03d}.md"
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    p = ROOT / "initial" / f"{chap}.md"
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else None


def chapter(chap, src="auto"):
    path = ROOT / "new" / f"{chap}.md"
    if not path.exists():
        print(f"FAIL: {path.relative_to(ROOT)} missing")
        return 1
    text = path.read_text(encoding="utf-8", errors="replace")
    vs = verses(text)
    errs = []
    nums = [v for v, _ in vs]
    if nums != sorted(nums):
        errs.append("verse order broken")
    if len(set(nums)) != len(nums):
        errs.append(f"duplicate verses {sorted({n for n in nums if nums.count(n)>1})}")
    trp = ROOT / "translation" / f"{chap}.txt"
    if trp.exists():
        want = {int(m.group(1)) for m in re.finditer(r"^\s*(\d+)\s*\|",
                  trp.read_text(encoding="utf-8", errors="replace"), re.M)}
        miss = sorted(want - set(nums))
        if miss:
            errs.append(f"MISSING {len(miss)} verses {miss[:15]}")
    allwarns, failverses, infos = [], [], []
    for v, body in vs:
        e, w, info = check(v, body, chap, _load_src(chap, v, src), need_heading=False)
        infos.append(info)
        allwarns += [f"{chap}:{v}: {x}" for x in w]
        if e:
            failverses.append(v)
            errs += [f"[{chap}:{v}] " + x for x in e]
    hs = [i["headings"] for i in infos if i["headings"]]
    md = [i["med"] for i in infos if i["med"]]
    wd = [i["words"] for i in infos]
    print(f"=== chapter {chap} ===")
    print(f"verses {len(vs)} | words {sum(wd):,} | mean/verse {statistics.mean(wd):.0f} "
          f"| headings mean {statistics.mean(hs):.1f} max {max(hs)} | median-section mean "
          f"{statistics.mean(md):.0f} min {min(md)}")
    for v in failverses[:60]:
        pass
    for e in errs[:50]:
        print("  FAIL " + e)
    if len(errs) > 50:
        print(f"  ... {len(errs)-50} more FAILs")
    for w in allwarns[:12]:
        print("  warn " + w)
    if len(allwarns) > 12:
        print(f"  ... {len(allwarns)-12} more warnings")
    print(f"{'PASS' if not errs else 'FAIL'} — {len(failverses)} verses with FAILs: {failverses[:25]}")
    return 1 if errs else 0


def files(chap):
    d = ROOT / "new" / "verse"
    bad, n = [], 0
    if not d.exists():
        print(f"no {d.relative_to(ROOT)}/ directory — verse files are written there, one per verse")
        return 1
    for p in sorted(d.glob(f"{chap}_*.md")):
        v = int(p.stem.split("_")[1])
        body = p.read_text(encoding="utf-8", errors="replace")
        body = re.sub(r"^## .*", lambda m: m.group(0), body, count=0)
        e, w, info = check(v, body, chap, _load_src(chap, v, "auto"))
        n += 1
        if e:
            bad.append((p.name, e))
    for name, e in bad:
        print(f"FAIL {name}\n   " + "\n   ".join(e))
    if n == 0:
        print(f"no {chap}_NNN.md verse files in {d.relative_to(ROOT)}/ yet")
        return 1
    print(f"{'PASS' if not bad else 'FAIL'} — {n-len(bad)}/{n} verse files clean")
    return 1 if bad else 0


def plan(chap):
    path = ROOT / "new" / f"{chap}.md"
    if not path.exists():
        vf = ROOT / "new" / "verse"
        n = len(list(vf.glob(f"{chap}_*.md"))) if vf.exists() else 0
        print(f"no {path.relative_to(ROOT)} yet ({n} verse files present) — run `check.py files {chap}` "
              f"to gate the verses written so far")
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = []
    for v, body in verses(text):
        e, w, info = check(v, body, chap, None, need_heading=False)
        rows.append(dict(**info, fails=e, warns=w))
    Path(f"/tmp/{chap}.worklist.json").write_text(json.dumps(rows))
    bad = [r for r in rows if r["fails"]]
    cats = {}
    for r in bad:
        for f in r["fails"]:
            cats.setdefault(f.split()[0], []).append(r["verse"])
    print(f"{len(bad)}/{len(rows)} verses with FAILs")
    for c, vs in sorted(cats.items(), key=lambda x: -len(x[1])):
        print(f"  [{c:11s}] {len(vs):3d} verses: {vs[:16]}{' ...' if len(vs)>16 else ''}")
    print(f"worklist -> /tmp/{chap}.worklist.json")
    return 1 if bad else 0


def merge(chap, apply=False, target=None, maxh=None):
    """Raise fragmented sections to standard by deleting mini-heading lines only.

    Adjacent sections are merged along the argument order; the surviving heading is
    the first of each merged group. NO prose word is written, moved, or reworded —
    the function asserts byte-level prose identity before it will apply anything.
    """
    target = target or MERGE_TARGET_MEDIAN
    maxh = maxh or MERGE_MAX_H
    path = ROOT / "new" / f"{chap}.md"
    text = path.read_text(encoding="utf-8", errors="replace")
    ms = list(re.finditer(r"^## Sūrah .+?:(\d+)\s*$", text, re.M))
    pieces, plan_log = [], []
    prev = 0
    for i, m in enumerate(ms):
        end_ = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        gap, head_line, body = text[prev:m.start()], text[m.start():m.end()], text[m.end():end_]
        v = int(m.group(1))
        heads, chunks, xref, tail, main = parse(body)
        lens = [len(c.split()) for c in chunks]
        nz = [l for l in lens if l]
        med = statistics.median(nz) if nz else 0
        if len(heads) <= MAX_HEADINGS and med >= MEDIAN_MIN_FAIL:
            pieces.append(gap + head_line + body); prev = end_; continue
        groups = [[j] for j in range(len(heads))]
        while True:
            merged = [sum(lens[j] for j in g) for g in groups]
            mnz = [x for x in merged if x]
            if (statistics.median(mnz) if mnz else 0) >= target and len(groups) <= maxh:
                break
            if len(groups) <= MIN_HEADINGS:
                break
            best = None
            for k in range(len(groups) - 1):
                a, b = merged[k], merged[k + 1]
                key = (max(a, b), a + b)          # merge the two smallest neighbours
                if best is None or key < best[0]:
                    best = (key, k)
            if best is None:
                break
            k = best[1]
            groups[k] = groups[k] + groups[k + 1]
            del groups[k + 1]
        keep = {g[0] for g in groups}
        drop = [j for j in range(len(heads)) if j not in keep]
        if drop:
            bold = [mm for mm in re.finditer(r"^\*\*(.+?)\*\*\s*$", body, re.M)
                    if mm.group(1).strip() != "Expanded Commentary"]
            for j in sorted(drop, reverse=True):
                body = body[:bold[j].start()] + body[bold[j].end():]
            body = re.sub(r"\n{3,}", "\n\n", body)
            plan_log.append(dict(verse=v, before=len(heads), after=len(groups),
                                 dropped=[heads[j] for j in drop]))
        pieces.append(gap + head_line + body)
        prev = end_
    pieces.append(text[prev:])
    new = "".join(pieces)

    strip_bold = lambda s: re.sub(r"^\*\*(.+?)\*\*\s*$", "", s, flags=re.M)
    a = re.sub(r"\s+", " ", strip_bold(text)).strip()
    b = re.sub(r"\s+", " ", strip_bold(new)).strip()
    if a != b:
        print("ABORT: prose identity check FAILED — refusing to write")
        for i in range(min(len(a), len(b))):
            if a[i] != b[i]:
                print("  first diff at", i, repr(a[i-60:i+60]), "|||", repr(b[i-60:i+60]))
                break
        return 2
    Path(f"/tmp/{chap}.merge_plan.json").write_text(json.dumps(plan_log))
    tot = sum(len(x["dropped"]) for x in plan_log)
    print(f"structural merge: {len(plan_log)} verses re-sectioned, {tot} mini-heading lines removed")
    print("prose identity: PASS — every commentary word preserved in its original order")
    if apply:
        path.write_text(new, encoding="utf-8")
        print(f"APPLIED -> {path.relative_to(ROOT)}")
    else:
        print("dry run (add --apply)")
    return 0


def split(kind, chap):
    """Split <kind>/<chap>.md into per-verse chunks so the writer reads ~400 tokens
    per verse instead of ~80,000 for the whole chapter. Administrative only — it
    copies source text, it never rewrites commentary."""
    src = ROOT / kind / f"{chap}.md"
    text = src.read_text(encoding="utf-8", errors="replace")
    ms = list(re.finditer(r"^>\s*\*\*(\d+)\*\*", text, re.M))
    if not ms:
        print(f"ERROR: no verse anchors in {src}", file=sys.stderr)
        return 1
    out = ROOT / "source_by_verse" / chap
    out.mkdir(parents=True, exist_ok=True)
    intro = text[:ms[0].start()]
    if intro.strip():
        (out / f"{chap}_000_intro.md").write_text(intro.strip(), encoding="utf-8")
    for i, m in enumerate(ms):
        e = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        v = int(m.group(1))
        (out / f"{chap}_{v:03d}.md").write_text(text[m.start():e].strip(), encoding="utf-8")
    sizes = [len((out / f"{chap}_{int(m.group(1)):03d}.md").read_text(encoding="utf-8").split()) for m in ms]
    print(f"{kind}/{chap}.md -> {len(ms)} chunks in {out.relative_to(ROOT)}/")
    print(f"  mean chunk {statistics.mean(sizes):.0f} words (~{statistics.mean(sizes)*1.3:.0f} tok) "
          f"vs whole file {len(text.split()):,} words (~{len(text)//4:,} tok)")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "chapter"
    if cmd == "chapter":
        sys.exit(chapter(a[1] if len(a) > 1 else "007"))
    if cmd == "verse":
        ch, v = a[1], int(a[2])
        vf = ROOT / "new" / "verse" / f"{ch}_{v:03d}.md"
        if vf.exists():
            body = vf.read_text(encoding="utf-8", errors="replace")
            e, w, info = check(v, body, ch, _load_src(ch, v, "auto"), need_heading=True)
            print(f"{ch}:{v} [{vf.name}] " + " ".join(f"{k}={info[k]}" for k in ("words", "headings", "med", "xref", "frames")))
            for x in e: print("  FAIL " + x)
            for x in w: print("  warn " + x)
            sys.exit(1 if e else 0)
        text = (ROOT / "new" / f"{ch}.md").read_text(encoding="utf-8", errors="replace")
        for vv, body in verses(text):
            if vv == v:
                # body excludes the heading line (the parser consumed it), so the heading
                # check is not applicable in this mode
                e, w, info = check(vv, body, ch, _load_src(ch, vv, "auto"), need_heading=False)
                print(f"{ch}:{vv} " + " ".join(f"{k}={info[k]}" for k in ("words", "headings", "med", "xref", "frames")))
                for x in e: print("  FAIL " + x)
                for x in w: print("  warn " + x)
                sys.exit(1 if e else 0)
        sys.exit(2)
    if cmd == "files":
        sys.exit(files(a[1]))
    if cmd == "plan":
        sys.exit(plan(a[1]))
    if cmd == "merge":
        sys.exit(merge(a[1], "--apply" in a))
    if cmd == "split":
        sys.exit(split(a[1], a[2]))
    if cmd == "frames":
        ch = a[1] if len(a) > 1 else "007"
        text = (ROOT / "new" / f"{ch}.md").read_text(encoding="utf-8", errors="replace")
        todo = []
        for v, b in verses(text):
            fr = list(FRAME.finditer(b))
            if len(fr) > MAX_FRAMES_FAIL:
                todo.append((v, [(m.start(), m.group(0)) for m in fr]))
        print(f"{len(todo)} verses over the frame limit; "
              f"{sum(len(x[1]) for x in todo)} instances, "
              f"{sum(max(0,len(x[1])-MAX_FRAMES_FAIL) for x in todo)} must be rewritten")
        for v, fs in todo:
            print(f"\n<<<{ch}:{v}>>> ({len(fs)} frames, keep at most {MAX_FRAMES_FAIL})")
            for off, f in fs:
                print(f"  @{off} F|" + re.sub(r"\s+", " ", f).strip())
        sys.exit(1 if todo else 0)
    if cmd == "stats":
        text = (ROOT / "new" / f"{a[1] if len(a)>1 else '007'}.md").read_text(encoding="utf-8", errors="replace")
        for lo, hi in [(1, 117), (118, 999)]:
            sel = []
            for v, body in verses(text):
                if lo <= v <= hi:
                    e, w, info = check(v, body, "007", None, need_heading=False)
                    sel.append(info)
            if sel:
                print(f" {lo}-{hi}: n={len(sel)} headings mean={statistics.mean([s['headings'] for s in sel]):.1f} "
                      f"max={max(s['headings'] for s in sel)} | med-section mean={statistics.mean([s['med'] for s in sel]):.0f} "
                      f"min={min(s['med'] for s in sel)} max={max(s['med'] for s in sel)} "
                      f"| words mean={statistics.mean([s['words'] for s in sel]):.0f} | frames max={max(s['frames'] for s in sel)}")
        sys.exit(0)
    print(__doc__)
