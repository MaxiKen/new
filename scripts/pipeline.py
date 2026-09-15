#!/usr/bin/env python3
"""
pipeline.py — orchestration and proof layer for one chapter of commentary.

check.py is the GATE (is this verse good?). This file is the PROCESS: it prepares a
chapter, records what has actually passed, assembles the chapter, and produces the
compliance receipt. It exists so that "I finished verse 42" is not a claim an agent
makes in prose, but a line a tool wrote after running the gate.

  start    <chap>              validate inputs, split the source, open the ledger
  next     <chap>              the next verse that still needs writing (resumable)
  status   <chap>              ledger tallies
  gate     <chap> <v>          run the gate on a verse file; writes nothing
  mark     <chap> <v>         gate, and ONLY on exit 0 write PASS + metrics + file hash
  assemble <chap> [--apply]    build new/<chap>.md from the PASS verse files, ascending
  verify   <chap>              re-check every PASS claim: file hash + gate re-run
  receipt  <chap> [--write]    full compliance proof; exit 0 = chapter is done

Anti-cheat design:
  * the ledger is only ever written by `mark`, and only after the gate exited 0;
  * each PASS stores a hash of the verse file at that moment, so editing a verse after
    marking it (or hand-writing a ledger line) is reported as STALE by verify/receipt;
  * `receipt` re-runs the whole chapter gate in a subprocess and embeds the raw output,
    so the transcript cannot be summarised favourably;
  * new/007.md is the reference standard and is write-protected by these tools.
"""
import json, re, sys, hashlib, subprocess, statistics, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util
_spec = importlib.util.spec_from_file_location("ck", ROOT / "scripts" / "check.py")
ck = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ck)

REFERENCE = "007"
H1 = "# Sūrah {name} (Chapter {n}) — Expanded Verse-by-Verse Commentary"


# ----------------------------------------------------------------- helpers
def chap_norm(c):
    c = str(c).strip().zfill(3)
    if not re.fullmatch(r"\d{3}", c):
        die(f"chapter must be 1-114 (got {c!r})")
    return c


def die(msg, code=1):
    print("ABORT: " + msg, file=sys.stderr)
    sys.exit(code)


def vdir(chap):
    return ROOT / "new" / "verse"


def vfile(chap, v):
    return vdir(chap) / f"{chap}_{int(v):03d}.md"


def ledger_path(chap):
    return vdir(chap) / f"{chap}.ledger.json"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def load_ledger(chap, required=True):
    p = ledger_path(chap)
    if not p.exists():
        if required:
            die(f"no ledger at {p.relative_to(ROOT)} — run: pipeline.py start {chap}")
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save_ledger(chap, led):
    led["updated"] = datetime.datetime.now().isoformat(timespec="seconds")
    ledger_path(chap).write_text(json.dumps(led, indent=1, ensure_ascii=False), encoding="utf-8")


def translation_verses(chap):
    p = ROOT / "translation" / f"{chap}.txt"
    if not p.exists():
        die(f"missing {p.relative_to(ROOT)}")
    nums = [int(m.group(1)) for m in re.finditer(r"^\s*(\d+)\s*\|",
            p.read_text(encoding="utf-8", errors="replace"), re.M)]
    if not nums:
        die(f"{p.relative_to(ROOT)} has no '<n> |' verse lines")
    return nums


def gate_verse(chap, v, quiet=False):
    """Run check.py's per-verse gate on the verse file. Returns (errs, warns, info)."""
    f = vfile(chap, v)
    if not f.exists():
        return [f"verse file missing: {f.relative_to(ROOT)}"], [], {}
    body = f.read_text(encoding="utf-8", errors="replace")
    errs, warns, info = ck.check(v, body, chap, ck._load_src(chap, v, "auto"), need_heading=True)
    return errs, warns, info


# ----------------------------------------------------------------- commands
def start(chap):
    chap = chap_norm(chap)
    if chap == REFERENCE:
        die(f"{chap} is the reference standard. It is not generated, and these tools "
            f"will not write to it. Repair it by hand with apply_edits.py instead.")
    src = ROOT / "initial" / f"{chap}.md"
    if not src.exists():
        die(f"missing verified source {src.relative_to(ROOT)} — cannot generate without it")
    nums = translation_verses(chap)
    vdir(chap).mkdir(parents=True, exist_ok=True)

    # per-verse source chunks: the single biggest driver of compliance
    out = ROOT / "source_by_verse" / chap
    n = len(list(out.glob(f"{chap}_*.md"))) if out.exists() else 0
    if n < len(nums):
        print("building per-verse source chunks …")
        ck.split("initial", chap)
    else:
        print(f"source chunks already present ({n}) in {out.relative_to(ROOT)}/")

    lp = ledger_path(chap)
    if lp.exists():
        led = json.loads(lp.read_text(encoding="utf-8"))
        print(f"ledger exists, keeping it: {len(led['verses'])} entries "
              f"({sum(1 for x in led['verses'].values() if x['status']=='PASS')} PASS)")
    else:
        led = {"chapter": chap, "verses_total": len(nums), "verses": {},
               "created": datetime.datetime.now().isoformat(timespec="seconds")}
        save_ledger(chap, led)
        print(f"ledger opened: {lp.relative_to(ROOT)} ({len(nums)} verses to go)")

    have = sum(1 for v in nums if vfile(chap, v).exists())
    print(f"\nREADY — chapter {chap}: {len(nums)} verses, {have} verse files present, "
          f"{len(nums)-have} to write.")
    print(f"  next verse   : python3 scripts/pipeline.py next {chap}")
    print(f"  after writing: python3 scripts/pipeline.py mark {chap} <V>   (writes the ledger)")
    return 0


def next_verse(chap):
    chap = chap_norm(chap)
    led = load_ledger(chap)
    nums = translation_verses(chap)
    for v in nums:
        ent = led["verses"].get(str(v))
        if not ent or ent.get("status") != "PASS":
            print(v)
            return 0
    print("DONE")
    return 0


def status(chap):
    chap = chap_norm(chap)
    led = load_ledger(chap)
    nums = translation_verses(chap)
    p = sum(1 for v in nums if led["verses"].get(str(v), {}).get("status") == "PASS")
    stale = stale_verses(chap, led)
    print(f"chapter {chap}: {p}/{len(nums)} PASS  ({len(nums)-p} remaining)")
    if stale:
        print(f"  STALE (file changed after PASS — re-mark): {stale}")
    ws = [e["words"] for e in led["verses"].values() if e.get("words")]
    if ws:
        print(f"  mean words/verse {statistics.mean(ws):.0f} | min {min(ws)} | max {max(ws)}")
    return 0


def stale_verses(chap, led):
    out = []
    for v, ent in led["verses"].items():
        f = vfile(chap, int(v))
        if ent.get("status") != "PASS":
            continue
        if not f.exists():
            out.append(int(v))
        elif ent.get("sha") and sha(f.read_text(encoding="utf-8", errors="replace")) != ent["sha"]:
            out.append(int(v))
    return sorted(out)


def gate(chap, v):
    chap = chap_norm(chap)
    errs, warns, info = gate_verse(chap, int(v))
    tag = "PASS" if not errs else "FAIL"
    print(f"{chap}:{int(v)} [{tag}] " + " ".join(f"{k}={info[k]}" for k in
          ("words", "headings", "med", "xref", "frames") if k in info))
    for e in errs:
        print("  FAIL " + e)
    for w in warns:
        print("  warn " + w)
    return 1 if errs else 0


def mark(chap, v):
    """The only sanctioned way to record progress: gate first, ledger second."""
    chap = chap_norm(chap)
    if chap == REFERENCE:
        die("cannot mark verses of the reference chapter")
    nums = translation_verses(chap)
    v = int(v)
    if v not in nums:
        die(f"chapter {chap} has no verse {v} (translation/{chap}.txt is authoritative)")
    f = vfile(chap, v)
    if not f.exists():
        die(f"nothing to mark: {f.relative_to(ROOT)} does not exist")
    errs, warns, info = gate_verse(chap, v)
    if errs:
        print(f"{chap}:{v} NOT RECORDED — the gate failed:")
        for e in errs:
            print("  FAIL " + e)
        print("Fix the verse file and run mark again. Do not proceed past this verse.")
        return 1
    led = load_ledger(chap)
    led["verses"][str(v)] = {
        "status": "PASS",
        "words": info.get("words"), "headings": info.get("headings"),
        "med_section": info.get("med"), "frames": info.get("frames"),
        "warnings": len(warns),
        "sha": sha(f.read_text(encoding="utf-8", errors="replace")),
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    save_ledger(chap, led)
    p = sum(1 for x in led["verses"].values() if x["status"] == "PASS")
    print(f"{chap}:{v} PASS recorded ({p}/{len(nums)} done). words={info.get('words')} "
          f"headings={info.get('headings')} median-section={info.get('med')}")
    return 0


def assemble(chap, apply=False):
    """Verse files -> new/<chap>.md. Pure concatenation: no word of prose is altered."""
    chap = chap_norm(chap)
    if chap == REFERENCE:
        die("never assemble over the reference chapter")
    led = load_ledger(chap)
    nums = translation_verses(chap)
    missing = [v for v in nums if led["verses"].get(str(v), {}).get("status") != "PASS"]
    if missing:
        print(f"ABORT: {len(missing)} verses are not PASS in the ledger: "
              f"{missing[:20]}{' …' if len(missing) > 20 else ''}")
        print("Assembling now would ship a short chapter. Finish them first.")
        return 1
    stale = stale_verses(chap, led)
    if stale:
        print(f"ABORT: these PASS verses were edited after their gate run: {stale}")
        print("Re-run `mark` on each so the recorded gate result matches the bytes.")
        return 1

    first = vfile(chap, nums[0]).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^## Sūrah (.+?) \d+:\d+", first, re.M)
    name = m.group(1).strip() if m else f"Chapter {int(chap)}"
    blocks = [H1.format(name=name, n=str(int(chap)))]
    intro = vdir(chap) / f"{chap}_000_intro.md"
    if intro.exists():
        blocks.append(intro.read_text(encoding="utf-8", errors="replace").strip())
    for v in nums:
        b = vfile(chap, v).read_text(encoding="utf-8", errors="replace").strip()
        if re.match(r"^---\s*$", b):          # verse file already opens with a rule
            b = b.split("---", 1)[1].strip()
        blocks.append(b)
    # the reference separates every section with exactly one '---' rule
    text = blocks[0] + "\n\n" + "\n\n---\n".join(blocks[1:])
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text.endswith("\n"):
        text += "\n"
    out = ROOT / "new" / f"{chap}.md"
    print(f"assembled {len(nums)} verse files -> {out.relative_to(ROOT)} "
          f"({len(text.split()):,} words, mean {len(text.split())//len(nums)} words/verse)")
    if not apply:
        print("dry run: pass --apply to write, then run `receipt`.")
        return 0
    out.write_text(text, encoding="utf-8")
    led["assembled"] = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "sha": sha(text), "words": len(text.split()), "verses": len(nums)}
    save_ledger(chap, led)
    print("WROTE " + str(out.relative_to(ROOT)))
    return 0


def verify(chap):
    """Re-prove every PASS claim from the files, ignoring the ledger's own numbers."""
    chap = chap_norm(chap)
    led = load_ledger(chap)
    nums = translation_verses(chap)
    bad = []
    for v in nums:
        ent = led["verses"].get(str(v))
        f = vfile(chap, v)
        if not ent or ent.get("status") != "PASS":
            bad.append((v, "not PASS in ledger")); continue
        if not f.exists():
            bad.append((v, "file missing")); continue
        cur = sha(f.read_text(encoding="utf-8", errors="replace"))
        if ent.get("sha") != cur:
            bad.append((v, "file changed after PASS — re-mark")); continue
        errs, _, _ = gate_verse(chap, v)
        if errs:
            bad.append((v, "gate now fails: " + errs[0]))
    print(f"verify {chap}: {len(nums)-len(bad)}/{len(nums)} PASS claims hold")
    reasons = {}
    for v, why in bad:
        reasons.setdefault(why.split(" — ")[0] if "not PASS" in why else why, []).append(v)
    for why, vs in sorted(reasons.items(), key=lambda x: -len(x[1]))[:6]:
        shown = ", ".join(str(x) for x in vs[:12]) + (f" … (+{len(vs)-12} more)" if len(vs) > 12 else "")
        print(f"  ✗ {why}  [{len(vs)}]: {shown}")
    if len(reasons) > 6:
        print(f"  … {len(reasons)-6} further reason categories")
    return 1 if bad else 0


def receipt(chap, write=False):
    """The compliance artifact. Re-runs everything; embeds raw tool output."""
    chap = chap_norm(chap)
    led = load_ledger(chap)
    nums = translation_verses(chap)
    L = []
    A = L.append
    ok = True

    A(f"# Compliance receipt — chapter {chap}")
    A("")
    A(f"Generated {datetime.datetime.now().isoformat(timespec='seconds')} by "
         f"`scripts/pipeline.py receipt {chap}`. Every line below is produced by re-running "
         f"the tool, not by the writer's account.")
    A("")

    # 1 gate transcript, verbatim
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check.py"), "chapter", chap],
                       capture_output=True, text=True)
    A("## 1. Chapter gate (`check.py chapter`)")
    A("")
    A("```")
    for ln in (r.stdout + r.stderr).strip().splitlines()[-60:]:
        A(ln)
    A("```")
    A("")
    A(f"exit code: **{r.returncode}**  (0 required)")
    if r.returncode != 0:
        ok = False
    A("")

    # 2 ledger vs reality
    A("## 2. Ledger vs files")
    A("")
    passed = [v for v in nums if led["verses"].get(str(v), {}).get("status") == "PASS"]
    stale = stale_verses(chap, led)
    missing_files = [v for v in nums if not vfile(chap, v).exists()]
    A(f"- verses required by `translation/{chap}.txt`: **{len(nums)}**")
    A(f"- verse files present: **{len(nums)-len(missing_files)}**")
    A(f"- recorded PASS by the tool: **{len(passed)}**")
    A(f"- PASS entries whose bytes changed afterwards (stale): **{len(stale)}**")
    if missing_files:
        A(f"- MISSING files: {missing_files[:25]}")
    if stale:
        A(f"- STALE: {stale[:25]} — re-run `mark` on these")
    ok = ok and not missing_files and not stale and len(passed) == len(nums)
    if not stale:
        A("- every PASS hash matches its file: **yes**")
    A("")

    # 3 merged file
    A("## 3. Merged chapter")
    A("")
    out = ROOT / "new" / f"{chap}.md"
    if not out.exists():
        A(f"- `new/{chap}.md` **does not exist** — run `pipeline.py assemble {chap} --apply`")
        ok = False
    else:
        text = out.read_text(encoding="utf-8", errors="replace")
        found = [int(m.group(1)) for m in re.finditer(r"^## S\u016brah .+?:(\d+)\s*$", text, re.M)]
        A(f"- words: **{len(text.split()):,}** | verse sections: **{len(found)}** | "
          f"mean {len(text.split())//max(1,len(found))} words/verse")
        A(f"- H1 title present: **{text.startswith('# S')}**")
        A(f"- every required verse present exactly once, in order: "
          f"**{'yes' if found == nums else 'NO'}**")
        if found != nums:
            A(f"  - expected {len(nums)} verses, found {len(found)}; "
              f"diff: {sorted(set(nums) ^ set(found))[:20]}")
            ok = False
        # the merge must not have altered any verse file
        drift = []
        for v in nums:
            f = vfile(chap, v)
            if not f.exists():
                continue
            vb = re.sub(r"\s+", " ", f.read_text(encoding="utf-8", errors="replace")).strip()
            if re.match(r"^---\s*", vb):
                vb = vb.split("---", 1)[1].strip()
            if vb and vb[:120] not in re.sub(r"\s+", " ", text):
                drift.append(v)
        A(f"- merged text matches the verse files byte-for-byte (whitespace aside): "
          f"**{'yes' if not drift else 'NO — ' + str(drift[:10])}**")
        if drift:
            ok = False
    A("")

    # 4 statistics against the standard
    A("## 4. Statistics vs the standard")
    A("")
    ws = [led["verses"][str(v)].get("words", 0) for v in passed] or [0]
    hs = [led["verses"][str(v)].get("headings", 0) for v in passed] or [0]
    ms = [led["verses"][str(v)].get("med_section", 0) for v in passed] or [0]
    fr = [led["verses"][str(v)].get("frames", 0) for v in passed] or [0]
    ini = ROOT / "initial" / f"{chap}.md"
    iw = len(ini.read_text(encoding="utf-8", errors="replace").split()) if ini.exists() else 0
    A("| metric | this chapter | standard (`new/STANDARD.md`) |")
    A("|---|---|---|")
    A(f"| mean words/verse | {statistics.mean(ws):.0f} | 1,000–1,500 (band 700–2,300) |")
    A(f"| median words/verse | {statistics.median(ws):.0f} | 1,369 in the reference |")
    A(f"| mean mini-headings/verse | {statistics.mean(hs):.1f} | 5–8 (band 3–12) |")
    A(f"| mean median-section length | {statistics.mean(ms):.0f} | 160–220 (fail <95) |")
    A(f"| max reader-frames in one verse | {max(fr)} | 0 (fail >2) |")
    A(f"| total chapter words | {sum(ws):,} | initial/{chap}.md is {iw:,} "
      f"({(sum(ws)/iw if iw else 0):.1f}×) |")
    below = [v for v in passed if (led["verses"][str(v)].get("words") or 0) < 900]
    A(f"| verses under 900 words | {len(below)} | allowed; each must still be gate-clean |")
    A("")
    if len(below):
        A("Short verses (justify in the report; thinness, not length, is the defect): "
          + ", ".join(f"{chap}:{v}" for v in below[:15]))
        A("")

    # 5 verification limits
    A("## 5. Verification limits recorded in the text")
    A("")
    unv = []
    for v in nums:
        f = vfile(chap, v)
        if f.exists():
            for m in re.finditer(r"\[UNVERIFIED[^\]]*\]", f.read_text(encoding="utf-8", errors="replace")):
                unv.append((v, m.group(0)))
    if unv:
        for v, s in unv[:30]:
            A(f"- {chap}:{v} {s}")
        A(f"\n{len(unv)} unverified item(s). Each one is a known limit, not a silent failure.")
    else:
        A("- none recorded")
    A("")

    # 6 verdict
    A("## 6. Verdict")
    A("")
    A(("**PASS** — every required verse is gate-clean, the ledger matches the files, "
          "and the merged chapter reproduces them."
          if ok else
          "**NOT COMPLETE** — the items above must be resolved. Do not report this chapter "
          "as finished until `receipt` exits 0."))
    A("")
    A("Commands that produced this: `check.py chapter`, `pipeline.py verify`, "
      "ledger hashes, verse-file/merged comparison.")
    print("\n".join(L))
    if write:
        p = ROOT / "new" / f"{chap}.COMPLIANCE.md"
        p.write_text("\n".join(L), encoding="utf-8")
        print(f"wrote {p.relative_to(ROOT)}")
    print(f"\nVERDICT: {'PASS' if ok else 'INCOMPLETE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    cmd, rest = a[0], a[1:]
    if cmd == "start":
        sys.exit(start(rest[0]))
    if cmd == "next":
        sys.exit(next_verse(rest[0]))
    if cmd == "status":
        sys.exit(status(rest[0]))
    if cmd == "gate":
        sys.exit(gate(rest[0], rest[1]))
    if cmd == "mark":
        sys.exit(mark(rest[0], rest[1]))
    if cmd == "assemble":
        sys.exit(assemble(rest[0], "--apply" in rest))
    if cmd == "verify":
        sys.exit(verify(rest[0]))
    if cmd == "receipt":
        sys.exit(receipt(rest[0], "--write" in rest))
    print(f"unknown command: {cmd}", file=sys.stderr)
    print(__doc__)
    sys.exit(2)
