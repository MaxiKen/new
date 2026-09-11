# Audit of `expanded/` — 114 files, 6,236 sections, 6,415,363 prose words

**Method.** `expanded/001.md` is the confirmed reference and has never been modified. Its
skeleton was encoded as `tools/quran-audit/validate.py`, which is now the structural gate for
the corpus. Content was verified against `initial/` (the ground-truth translation and
per-verse classical commentary) and `translation/*.txt` (a second translation used to
distinguish real substitutions from paraphrase). Every count in this report is the output of
a committed checker, not an estimate.

> **The title figures, and the three spans in this report.** Section count is `census.py`'s
> 6,236; `check_translations.py` reports 6,235 because one section has no source text to
> compare against. Prose words are word tokens matching `[\w'’-]+` summed over all of
> `expanded/` with lines that are exactly `---` excluded — **6,415,363**. An earlier revision
> of this title read 6,235 sections / 6,286,453 words, a figure reproducible by no span tried
> this pass; it is withdrawn. Depth and duplication are measured on different spans and must
> not be interchanged — see section 7.

---

## 1. Current gate status

```
$ python3 tools/quran-audit/validate.py
PASSED: 114/114      FAILED: 0

$ python3 tools/quran-audit/check_translations.py
checked: 6235 sections   (no translation line: 0)
flagged (<0.45 against BOTH initial/ and translation/): 7

$ python3 tools/quran-audit/check_offtopic.py
files: 114   sections examined: 5546   threshold: <15% echo
flagged: 4   (all four verified as false positives -- see section 6)

$ python3 tools/quran-audit/test_skeleton.py          # added this pass
18/18 checks PASS

$ python3 tools/quran-audit/normalize.py              # whole corpus
files written: 0                                      # idempotent

$ python3 tools/quran-audit/census.py --dup 0.030
duplication >= 0.03: 264 sections in 23 files          # was 269; see Group H

$ python3 tools/quran-audit/fix_orphan_connectors.py   # added this pass
orphan connectors: 0 in 0 files
```

The `validate.py` result above is now produced by a **hardened** gate. Before
this pass it reported the same PASSED 114/114 while 107 files carried 219
illegal horizontal rules and 10 files carried 11 non-canonical H2 headings; see
the correction to section 2 and `REMAINING_ISSUES.md` Group G.

> **Hardened again this pass, for the same reason.** `validate.py` still
> reported PASSED 114/114 while `017.md` carried **111 malformed bold
> mini-headings** (`****Heading****`) and three files carried **four orphan
> connector lines**. Neither class was checked. Both are now gated — `^\*{4,}`
> for malformed headings, and a bare short word alone between two blockquotes
> for orphan connectors — and each gate was regression tested in both
> directions. The lesson from Group G generalises: every "all green" in this
> report is evidence only about the classes the gate enumerates.
> `REMAINING_ISSUES.md` Groups H1 and I.

The 7 translation flags are register variants, each verified side-by-side against both
reference translations: `010.md` v91, `020.md` v1, `021.md` vv 73–76/78/97, `050.md` v25,
`068.md` vv 3/10/13/24/25, `094.md` v7, `102.md` v3, `108.md` v3. None is a wrong-verse
substitution and none was altered.

---

## 2. Repaired defect classes

| Defect class | Files affected | Status |
|---|---|---|
| Canonical-skeleton divergence | 114 files | **0 remaining** — *but see the correction below; this row was false when written* |
| Stray horizontal rules | 107 files, 219 rules | **0 remaining** — found and fixed this pass; gate hardened |
| Non-canonical H2 headings | 10 files, 11 headings | **0 remaining** — demoted to bold mini-headings |
| Degenerate prose, severe band | `007.md`, 10 sections | **0 remaining** — rebuilt from `initial/007.md` |
| Malformed bold mini-headings | `017.md`, 111 headings | **0 remaining** — `****H****` normalised to `**H**`; gate hardened |
| Redundant inserted blocks, severe band | `017.md`, 5 sections | **0 remaining** — excised on per-section evidence, depth rebuilt |
| Redundant inserted blocks, moderate band | `017.md`, 29 sections | **0 remaining** — all 111 blocks resolved; file off the duplication census, worst now 0.013 |
| Conflicting ḥadīth citation | `017.md` v44 | **resolved** — aligned to the corpus consensus (Muslim 1955) |
| Orphan connector lines | 3 files, 4 lines | **0 remaining** — bare `and` stranded between blockquotes; gate hardened |

> **Correction to the first row.** "Canonical-skeleton divergence: 0 remaining"
> was **not true** when it was written, and the gate cited as evidence was not
> capable of establishing it. 107 of 114 files carried **219 illegal horizontal
> rules** (134 duplicated boundary rules, 85 orphaned inside section bodies —
> 79 of them in `021.md`) and 10 files carried **11 non-canonical H2 headings**.
>
> `validate.py` PASSED 114/114 throughout, because for each heading it tested
> only `L[i-1] == '---'` and `L[i-2] == ''`. A duplicated rule satisfies both:
> the second rule sits at `L[i-1]` and the blank between them at `L[i-2]`, while
> the stray first rule occupies `L[i-3]`, which was never examined. It also
> never inventoried headings at all.
>
> All three root causes were in `normalize.py`: the preamble slice retains the
> first verse's boundary rule before `run()` re-emits one; the end-rule guard
> tested only `parts[-2]`, missing a rule at `parts[-3]`; and `clean()`'s
> `unglue` inserted `\n\n---\n\n` before welded headings that were later dropped
> as remnants, orphaning the rule. All are patched, the corpus is repaired with
> **zero content change** (126,667 fingerprinted content lines identical;
> 6,417,717 prose words unchanged), `validate.py` is hardened to reject both
> classes, and `test_skeleton.py` (18 checks) proves the pre-hardening gate
> would have accepted them. Full detail: `REMAINING_ISSUES.md` Group G.
>
> **General lesson.** A green gate is evidence only about what the gate
> measures. "PASSED 114/114" was reported as proof of skeleton conformance for
> an invariant the gate did not test.
| Leaked `[System Memory Check]` drafting scaffolding | `074.md` (54/56 sections, 61% of file) | **0 remaining** — 17,334 w stripped |
| Whole-file template boilerplate | `036.md` (83/83 sections, 13 sentences ×83) | **0 remaining** — 16,483 w stripped, all 83 sections rebuilt |
| Cross-sūrah verse substitution | `037.md` (117 sections), `011.md` (13), `007.md` (1), `040.md` (1) | **0 remaining** — 132 translations restored |
| Translation-line-only drift | `040.md` vv 31/48/50/63/73 | **0 remaining** |
| Appended text / run-on translation lines | `026.md` ×6, `011.md` v117 | **0 remaining** |
| Template-filler phrases (4 regex patterns) | 141 phrases across the corpus | **0 remaining** |
| Off-topic sections (<15% echo) | 25 flagged | **0 genuine remaining** (4 detector false positives) |
| Commentary body describing a *different* verse | `037.md` (7 verified) | **0 remaining** — realigned from `initial/037.md` |
| Leaked drafting scaffolding (self-correction, citation-hunting) | `037.md` v139, `032.md` ×4, `083.md` | **0 remaining** — 10 hits, all fixed |

A corpus-wide boilerplate scan confirmed the template class affected exactly two files:
`036.md` at 100% and `074.md` at 96%. Every other file scored 0%.

---

## 3. `036.md` — rebuilt in full

The file's 83 sections were entirely template-generated. The boilerplate was stripped first
(16,483 words), then every section was rebuilt verse by verse from the apparatus in
`initial/036.md`, in 21 batches of 4 (`content_036_a.py` … `content_036_u.py`).

| Metric | Value |
|---|---|
| Sections | 83 |
| Total words | 43,738 |
| Min / median / max | 419 / **516** / 721 |
| Sections with duprate ≥ 0.030 | **0** |
| Off-topic flags | **0** |
| Translation flags | **0** |

The rebuild runs at a median of 516 words, deliberately below the 976-word corpus healthy
figure because this sūrah's apparatus in `initial/` is thinner than that of `011.md`,
`021.md`, or `040.md`. Depth was matched to what the source material can support rather than
padded to a number.

Eight sections initially tripped the duplication gate (vv 18, 28, 36, 45, 47, 65, 66, 78) for
the same reason each time: quoting the verse translation verbatim in the opening prose. The
10-grams of the quoted verse alone trip the detector. Each was fixed by paraphrasing the
opening and leaving the quotation to the `> **…**` line.

---

## 4. Translation-defect history, all resolved

**Whole section substituted** — the commentary belonged to a different verse:
`011.md` vv 105–116 and 118 (each mapped to 81:1, 55:17, 25:61, 10:5, 30:30, 80:1, 37:179,
37:126, 109:1, 81:28, 69:39, 48:7, 37:179); `007.md` v170; `040.md` v74.

**Translation line only:** `040.md` vv 31, 48, 50, 63, 73.

**Appended text / run-on:** `026.md` vv 124, 132, 146, 181, 185, 208; `011.md` v117.

`037.md`'s defect was the largest: of 182 sections, 63 matched `initial/`, 2 matched
`translation/`, and **117 matched neither**. The cause was that vv 57–177 were 21,326 words
of unheaded content which `normalize.py` had promoted into 121 new verse headings; 97 of the
121 quoted other sūrahs. All 119 substitute translations were replaced, and the file now
scores 0 of 182 mismatch.

---

## 5. Complete files

| File | Sections | Median words | Notes |
|---|---|---|---|
| `001.md` | 112 | — | confirmed reference, never modified |
| `011.md` | 123 | 914 | 0 translation defects, 0 filler |
| `021.md` | 112 | 1,037 | 121,660 w; vv 73–76/78/97 are legitimate variants |
| `026.md` | 227 | 258 | 0 translation defects; depth outstanding |
| `036.md` | 83 | 516 | rebuilt in full this pass |
| `040.md` | 85 | 937 | 0 translation defects |
| `007.md` | 206 | 730 | |
| `037.md` | 182 | 231 | correctness complete; depth outstanding |

---

## 6. Outstanding

**Depth.** Six files sit below a 400-word median section:

| File | Sections | Min | Median | Max | Words |
|---|---|---|---|---|---|
| `026.md` | 227 | 61 | 247 | 849 | 68,686 |
| `037.md` | 182 | 144 | 290 | 903 | 56,466 |
| `069.md` | 52 | 243 | 320 | 410 | 17,185 |
| `075.md` | 40 | 285 | 358 | 910 | 15,467 |
| `073.md` | 20 | 301 | 367 | 1,239 | 8,347 |
| `067.md` | 30 | 317 | 391 | 569 | 12,177 |

> **Correction.** The table above previously carried **pre-Group-C** figures —
> `037.md` at min 139 / median 231 / 43,186 words and `026.md` at min 65 /
> median 258 / 70,109 words — and so contradicted section 3 and
> `REMAINING_ISSUES.md`'s own Group C result. It is replaced with the current
> measurement, taken on the same span as `REMAINING_ISSUES.md` Group A (section
> body, H2 heading line and rules excluded, word tokens `[\w'’-]+`). On that
> span the corpus stands at **198 sections under 260 w and 524 under 400 w** of
> 6,236. `026.md`, not `037.md`, is now the thinnest file by median.
>
> `017.md` is **not** a depth problem and is deliberately absent from this
> table: 111 sections, min 759 w, median 1,055 w, max 1,975 w, 119,274 words.
> It was 724 w minimum before this pass removed five redundant blocks, and
> three sections that fell below that floor were rebuilt (Group H3). No section
> of `017.md` is under 400 w.

**Off-topic flags — 4, all verified false positives.**

> **Correction.** This report previously stated the `037.md` hits were "depth artifacts —
> bodies of 88–161 words under-echo by construction — not subject drift." That was wrong.
> Reading them showed they were genuine: `037.md` v62's body discussed *man ʿaṣaynā
> al-rasūl* (33:66–67 content) under a heading about the tree of Zaqqūm, and v182's discussed
> "We have preferred some of them over others" (2:253 content). All 7 were realigned from
> `initial/037.md`'s apparatus and now score 0 flags.

The 4 that remain were each read and are detector artifacts, not subject drift:

| Section | Echo | Why it fails |
|---|---|---|
| `018.md` v75 | 0.0% | Body quotes the verse in Arabic transliteration (*qāla a-lam aqul laka…*) rather than the English wording; it engages Khiḍr, Moses, patience and the repetition of v72 throughout |
| `026.md` v132 | 0.0% | Body covers vv 132–134 collectively; `initial/026.md` carries **no** commentary note for these verses, so there is no source vocabulary to echo |
| `026.md` v176 | 14.3% | One point under threshold; echoes *inhabitants* and *thicket*, misses *messengers* only because the body says *message* |
| `067.md` v10 | 0.0% | Pure inflection: verse says "had we **listened**… **understood**", body says "**listening** and **understanding**" |

The detector is lemma-blind and does not read transliteration. A stemming patch was tried and
**rejected**: it raised corpus flags from 11 to 45 and introduced false positives in `040.md`
and `007.md` where there had been none. The four are documented rather than "fixed."

A real bug *was* found and fixed: `body_lines()` dropped entirely-bold lines as headings, so
mini-headings carrying the verse's own vocabulary were excluded from the body. `040.md` v3's
headings are literally "Forgiver of Sin", "Accepter of Repentance", "Severe in Retribution",
"Possessor of Bounty" — the exact words of the verse — yet it scored 12.5% echo, and 100% once
headings were retained.

**`074.md`.** Structurally valid and correct after the scaffolding strip, but now thin.
Measured this pass on the standard span: 56 sections, **min 378 / median 418 / max 790**
across **24,771** words. It needs depth rebuilt from `initial/074.md`.

> **Correction.** This entry previously read min 392 / median 436 / max 793 across 25,610
> words. Those figures are not reproducible on the current tree under either span (including
> the H2 heading line gives min 382 / median 422, still not 392 / 436), so they were taken
> against an earlier state of the file. The numbers above are what `074.md` measures now.

**`017.md` — CLOSED: 0 sections over the duplication gate.** The file no longer appears in
the census; its worst section is now 0.013 (v100), against 0.114 when the pass began. All
29 remaining blocks were resolved by remove-and-test, with 9 folds, 2 rebuilds on apparatus
the sections had never used (v54, v75) and the rest needing nothing. The diagnosis below is
retained because it is what made the treatment correct: these were **not** degenerate prose
and must not be rebuilt from scratch — each carried an
inserted block that restated part of its own section while also adding material, and the 29
blocks together held 11,577 words including 1,129 content words found nowhere else in their
sections. Treatment is trim and fold. Full method, evidence and bucketed worklist:
`REMAINING_ISSUES.md` Group H5.

**`007.md` — 100 sections still over the gate, 42 at or above 0.060.** The severe band is
clear, but `007.md` now holds seven of the eight worst sections in the corpus. Before
rebuilding any of them, establish whether it is degenerate output (a 10-gram recurring many
times, which only a rewrite fixes) or prose with a repetitive register (which a rewrite would
fix at the cost of depth). `017.md` was misdiagnosed as the former and the correct treatment
turned out to be an excision.

**`045.md`.** 6.17 emphasis runs per 1,000 words against a corpus norm near 1. Translations
are exact. Left in place by decision — the pattern is the file's own style.

---

## 8. Defect class found by reading, not by any checker

**Leaked drafting scaffolding.** Five locations contained the author's own deliberation
rather than commentary. None was caught by `validate.py`, `check_translations.py`, or
`check_offtopic.py`, because in every case the Markdown was well-formed and the text was
about the right verse. It surfaced only from reading section bodies directly.

| Location | What was there |
|---|---|
| `037.md` v139 | The body *was* the drafting monologue: "The verse begins the Jonah narrative: 'And Lot, when he said…' **Wait — actually** v139 starts with Jonah… **Let me correct** the content." Rebuilt from `initial/037.md` [139]/[142] |
| `032.md` ×4 | Citation-hunting left in the prose: `40:47? — actually … Let me be careful`, `41:32? — actually`, `35:26? — actually`, `15:82? — … — wait` |
| `083.md` | A guess-chain over a ḥadīth narrator: "Ibn ʿUmar? — no; it is narrated from Abū Hurayrah? — the wording is: Najdī ibn ʿUmar? Let me state it as transmitted" |

Every citation was verified against `initial/` **before** the deliberation was stripped —
67:8, 41:31–32, 43:25 / 30:47 / 7:136, and 15:82 / 26:149 / 89:9 all check out. The `083.md`
narrator guesses were all three wrong; the narrator is **al-Nuʿmān ibn Bashīr** (Bukhārī 52),
verified externally, since `initial/` does not record this ḥadīth.

This class is now covered by `check_scaffolding.py`. The tool was validated by running it
against the pre-fix files: **10 hits detected before the fix, 0 after.** Its patterns also
match quoted scripture ("Let me kill Moses" is Pharaoh at 40:26; "Say: 'Wait — we too are
waiting'" is 6:158), so it prints context for human judgement rather than asserting a count.

---

## 7. Reproducing the gates

```
python3 tools/quran-audit/validate.py                       # hardened: rules + heading inventory
python3 tools/quran-audit/check_translations.py [--sura N] [--verbose]
python3 tools/quran-audit/check_offtopic.py     [--sura N] [--verbose]
python3 tools/quran-audit/check_scaffolding.py  [--context N] [--sura N]
python3 tools/quran-audit/census.py [--thin N] [--dup N] [--sura N] [--json F]
python3 tools/quran-audit/test_skeleton.py                  # Group G regression test
python3 tools/quran-audit/extract_source.py <sura> <lo> <hi>
python3 tools/quran-audit/fix_translation.py <sura> <verse...> --dry-run
python3 tools/quran-audit/fix_separators.py [--dry-run] [--sura N]
python3 tools/quran-audit/fix_headings.py     [--dry-run] [--sura N]
python3 tools/quran-audit/apply_sections.py <sura> <module.py>...

# added this pass -- Group H (017.md inserted blocks) and Group I (orphans)
python3 tools/quran-audit/fix_orphan_connectors.py [--apply]
python3 tools/quran-audit/block017.py /tmp/017.bak <verse>   # or --list
python3 tools/quran-audit/novel_sentences.py <verse...> | --all [--min F]
python3 tools/quran-audit/fix_017_blocks.py /tmp/017.bak [--dry-run] <verse...>
```

`block017.py`, `novel_sentences.py` and `fix_017_blocks.py` all locate the
`017.md` blocks from a **pre-fix copy** (`/tmp/017.bak`), because the blocks were
identified by their malformed `****` markers and `fix_headings.py` preserves line
counts, so the copy's relative offsets stay valid against the current file. That
copy is a working artifact, not committed — `/tmp` does not survive a sandbox reset, and
this one was lost and regenerated mid-pass. Regenerate it with
`git show 6eb8b1f:expanded/017.md > /tmp/017.bak` — the base commit, which still
carries the `****` markers. Position-based identification is the only reliable
method — locating a block by "the Nth heading in the section" picks the wrong
one.

`census.py` reports depth and duplication together. Its duplication measure uses
the **whole-section span** (heading through body, trailing rule dropped) to match
`check_degeneracy.py`; a body-only span gives materially different counts (151 vs
269 at the 0.030 gate), so the two must not be interchanged. Its depth figures
are body-only and therefore run ~12–25 words below the whole-section medians
quoted in section 6 of this report and in `REMAINING_ISSUES.md` Group A.

Restore any file from history with `git checkout <sha> -- expanded/`. Note that
the working tree is squashed to a single merge commit (`6eb8b1f`), so the
pre-work baseline `48e6cbb` referenced in `REMAINING_ISSUES.md` Group B is not
recoverable from this repository and figures diffed against it cannot be
re-checked.
