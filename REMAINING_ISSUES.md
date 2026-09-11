# Remaining Issues — expanded/ Corpus Audit

**Date:** 2026-09-11 (revised this pass)
**Branch:** `arena/01a0917f-new`
**Scope:** 114 files, 6,236 sections, 6,415,363 prose words in `expanded/`
**Reference file:** `expanded/001.md` — confirmed correct by the user, never modified.

Every figure below was produced by running the named tool or script against the
working tree. Nothing is carried over from an earlier estimate. Where a number
could not be established, it is marked **unbounded** and the reason is given.

> **Revision note (this pass).** Two earlier figures in this file were not
> reproducible and have been corrected: the Group B count of **303** and the
> corpus scope of **6,229 sections / 6,292,058 words**. The measured values are
> **279 sections at/above the 0.030 duplication gate** and **6,236 sections**.
> The method is stated under Group B so the number can be checked. A third
> inconsistency is recorded under Group A: the `037.md` row of the depth table
> was taken **before** the Group C rebuild and contradicts this file's own
> Group C result line.
>
> A previously undetected defect class — **219 stray horizontal rules and 11
> non-canonical H2 headings in 107 files** — was found and closed. It is
> recorded as **Group G**. All four gates reported green while 107 of 114 files
> carried it, because `validate.py` did not check for either class.
>
> Two further classes were found and closed this pass. **Group H**: every one of
> `017.md`'s 111 sections carries a block inserted by a different generator, all
> 111 with malformed `****Heading****` mini-headings (now normalised), and five
> of them near-verbatim restatements of their own section (now removed, with the
> lost depth rebuilt). **Group I**: four orphaned bare-word connector lines
> stranded between two blockquotes. `validate.py` gates both classes now.
>
> **The prose-word figure changes with these fixes** and is reproducible as:
> word tokens matching `[\w'’-]+`, summed over all of `expanded/`, excluding
> lines that are exactly `---`. That measure gives **6,415,363** on the current
> tree; the earlier 6,416,381 reconciles as 6,416,381 − 2,158 (five blocks
> removed from `017.md`) + 1,143 (depth rebuilt into three of them) − 3
> (orphan connectors).

---

## Gate status (all green)

```
validate.py            PASSED 114/114, FAILED 0   (HARDENED this pass -- Groups G, H, I)
check_translations.py  6,235 checked, 0 missing translation lines, 7 flagged
check_offtopic.py      114 files, 5,546 sections examined, 4 flagged
check_scaffolding.py   114 files, 0 genuine hits
test_skeleton.py       18/18 checks passed (NEW this pass)
normalize.py           files written: 0 on the whole corpus (idempotent)
fix_orphan_connectors.py  0 orphan connectors remaining (NEW this pass)
```

Repro from the repo root:

```
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/check_translations.py [--sura N] [--verbose]
python3 tools/quran-audit/check_offtopic.py     [--sura N] [--verbose]
python3 tools/quran-audit/check_scaffolding.py  [--context N] [--sura N]
python3 tools/quran-audit/test_skeleton.py       # regression test for Group G
python3 tools/quran-audit/census.py              # depth + duplication census
python3 tools/quran-audit/fix_separators.py --dry-run
python3 tools/quran-audit/fix_headings.py     --dry-run
python3 tools/quran-audit/fix_orphan_connectors.py        # Group I scan
python3 tools/quran-audit/block017.py /tmp/017.bak --list # Group H block locator
python3 tools/quran-audit/novel_sentences.py --all        # Group H novelty report
```

> **Caution on "all green".** `validate.py` PASSED 114/114 before this pass
> while 107 files carried structural artifacts. The gate checked `L[i-1]` and
> `L[i-2]` relative to each heading, which a duplicated rule satisfies, and it
> never inventoried headings. A green gate is evidence only about what the gate
> measures. The hardened version and its regression test are in Group G.

---

## Group A — Content depth

Six files sit below a 400-word median section. Measured ranges:

| File | Sections | Min | Median | Max | Words | <260 w | <400 w |
|---|---|---|---|---|---|---|---|
| `037.md` | 182 | **144** | 290 | 903 | 56,466 | 72 | 150 |
| `026.md` | 227 | 61 | 247 | 849 | 68,686 | 122 | 157 |
| `069.md` | 52 | 243 | 320 | 410 | 17,185 | 2 | 50 |
| `075.md` | 40 | 285 | 358 | 910 | 15,467 | 0 | 28 |
| `073.md` | 20 | 301 | 367 | 1,239 | 8,347 | 0 | 13 |
| `067.md` | 30 | 317 | 391 | 569 | 12,177 | 0 | 16 |

Corpus-wide (whole-section words, **H2 heading line and rules excluded**):
**198 sections under 260 w** and **524 under 400 w**, of 6,236 measured.

> **The measure must be stated exactly or the figures do not reproduce.**
> Counting from the `## Sūrah …` heading line through the section, excluding
> lines that are exactly `---`, gives **198 / 524** — this file's figures.
> Including the heading line adds its four tokens to every section and gives
> 190 / 505, which looks like progress but is only a different span. `census.py`
> reports a third, body-only span (215 / 601). All three are correct for their
> own span; only the first is comparable to the numbers below.

> **Correction to this table.** The `037.md` row previously read min 139 /
> median **245** / max 899 / **48,835** words, with 105 sections under 260 w and
> 160 under 400 w. That row was measured **before** the Group C rebuild and
> contradicted this file's own Group C result line (median 282, 55,576 words).
> It has been replaced with the post-rebuild measurement. `037.md` is still the
> second-thinnest file in the corpus, but it is no longer the thinnest —
> `026.md` is.
>
> **A second correction to the same row, this pass.** The replacement wrote
> **245** into the *min* column. 245 was the row's old *median*; the measured
> minimum is **144**, shared by v117 and v167 (v165 is 145, v179 is 147). Every
> other cell in the row — median 290, max 903, 56,466 words, 72 and 150 — was
> re-measured this pass and is correct. The rest of the table reproduces exactly.
> v117 is a two-clause verse ("And We gave him the Scripture and the
> Criterion") whose section runs to two headings and 144 words; it is a genuine
> Group A target, not a measurement artifact.

Two further files sit just above the 400-word line and should be watched rather
than treated as complete: **`034.md`** (54 sections, median 401 w) and
**`039.md`** (75 sections, median 411 w). Neither was listed in earlier
revisions of this file.

For comparison, the completed files sit far higher: `021.md` median 1,037 w,
`040.md` 937 w, `011.md` 914 w, `007.md` 730 w, `036.md` 516 w, `074.md` 436 w.

### A1 — Nearly every thin section can be grounded

An earlier revision of this file reported **101 ungroudable sections**. That
figure was **wrong**, and the error is worth recording because it nearly caused
a real omission.

`initial/` abbreviates the end of a verse range in its markers: `**124-28**`
means verses 124–128, and `**108-9**` means 108–109. The parsing code computed
`range(124, 29)`, which is empty, so every abbreviated range marker was silently
dropped and its verses counted as having no source note.

With the abbreviation rule applied, the groundability census becomes:

| | Groundable | Ungroundable |
|---|---|---|
| Under 260 w | 205 | **1** |
| 260–400 w | 204 | 0 |
| **Total** | **409** | **1** |

The single exception is `026.md` v110 (71 w), which has no note in
`initial/026.md` — that file covers 226 of its 227 verses.

The same fix was applied to `tools/quran-audit/extract_source.py`, which had the
same bug and returned "(no commentary)" for verses that do have a shared range
note. Verified: `v109` and `v124`, which previously printed nothing, now return
their `[108–109]` and `[124–128]` notes, while `v107`'s per-verse note is
unchanged.

**Consequence:** the depth work in Group A is not blocked. 409 of the 410 thin
sections have source apparatus to build from.

---

## Group B — Repetitive prose (264 sections; 15 fixed across two passes)

**Method, stated so the number is checkable.** Per section, tokenise the whole
section (heading through body, lowercased), form 10-grams, and take the fraction
of 10-gram *positions* that are duplicates of an earlier position within the same
section. Sections under 80 tokens score 0. This is the measure in
`check_degeneracy.py`, whose reporting threshold is 0.10; the 0.030 threshold
used here is stricter.

```
python3 tools/quran-audit/census.py --dup 0.030
```

> **Correction.** An earlier revision reported **303** sections. That figure is
> **not reproducible** by any variant tried: whole-section vs body-only span,
> with and without Markdown markers stripped, n=10 and n=8, minimum length 80
> and 0. The measured value on the pre-pass tree was **279**. The per-file
> breakdown also disagreed with the old table in ways not explained by any
> recorded edit — `014.md` was listed at 29 but measures 16, `010.md` at 36 but
> measures 30, `011.md` at 18 but measures 12. The old 303 is withdrawn.
> The baseline `48e6cbb` it was diffed against is not in this repository's
> history (the tree is squashed to a single merge commit), so it cannot be
> re-checked.

### Work completed this pass

The ten worst sections in `007.md` — the whole of the **>= 0.100 severe band** —
were rebuilt from the apparatus in `initial/007.md`:

| Verse | Before | After | Words |
|---|---|---|---|
| v206 | 0.200 | **0.017** | 772 |
| v141 | 0.145 | **0.008** | 736 |
| v204 | 0.143 | **0.006** | 689 |
| v185 | 0.120 | **0.000** | 675 |
| v137 | 0.118 | **0.023** | 838 |
| v189 | 0.116 | **0.025** | 875 |
| v195 | 0.113 | **0.009** | 585 |
| v200 | 0.108 | **0.012** | 667 |
| v164 | 0.107 | **0.000** | 706 |
| v15  | 0.105 | **0.000** | 524 |

**10 fixed, 0 introduced.** On the census span `007.md` moved from
10 / 52 / 110 sections at >= 0.100 / >= 0.060 / >= 0.030 to **0 / 42 / 100**.
Corpus-wide: **269** (was 279). Five further sections were cleared this pass in
`017.md` (Group H2), bringing the corpus to **264**; `007.md` itself is
unchanged at 0 / 42 / 100 and is now the file holding the worst cases.

The rebuilds are in `content_007_degen_a.py` (vv 137, 141, 204, 206) and
`content_007_degen_b.py` (vv 15, 164, 185, 189, 195, 200).

**This is not a stylistic complaint.** `007.md` v206 previously read, in full:

> *"the people who are the objects of the contrast of the verse are the people
> who are in the state of the one who are the ones who worship God with the
> spiritual purity and the nearness to God, and the people who worship God with
> the spiritual purity and the nearness to God are the people who are in the
> state of the one who are the ones who are the examples of the worship of God…"*

The 10-gram *"is the man who is in the one who is the object"* recurred 10 times
in 1,118 words. Sections in this band were **degenerate output**, not prose with
a repetitive style, and Group B should be treated as a correctness class rather
than a polish class. No gate caught it: the Markdown was well-formed, the text
was about the right verse, the translations were exact, and the vocabulary
echoed the verse strongly enough to pass `check_offtopic.py`.

### Remaining, by file (measured this pass)

| File | Count | Worst |
|---|---|---|
| `007.md` | 100 | 0.099 (v162) |
| `010.md` | 30 | 0.082 (v93) |
| `017.md` | **12** | **0.088 (v38)** — was 34 / 0.114, see Group H |
| `014.md` | 16 | 0.078 (v46) |
| `039.md` | 16 | 0.080 (v46) |
| `025.md` | 15 | 0.092 (v32) |
| `011.md` | 12 | 0.055 (v91) |
| `034.md` | 8 | 0.064 (v31) |
| `045.md` | 7 | 0.070 (v16) |
| `020.md` | 6 | 0.039 (v97) |
| `026.md`, `056.md`, `076.md` | 4 each | 0.055 / 0.045 / 0.087 |
| `004.md` | 3 | 0.040 (v173) |
| `013.md` | 2 | 0.039 (v40) |
| `002, 030, 033, 037, 041, 042, 062, 064` | 1 each | 0.032–0.048 |

Severity bands across the remaining **264** (was 269): **0 >= 0.150**,
**0** in 0.100–0.149, **89** in 0.060–0.099, **175** in 0.030–0.059.
**No section anywhere in the corpus is now at or above 0.100.**

Next targets by severity: `007.md` v162 (0.099), `007.md` v25 (0.098),
`007.md` v194 (0.098), `007.md` v205 (0.097), `007.md` v149 (0.094),
`025.md` v32 (0.093). `007.md` holds seven of the eight worst sections and is
now the file to work on; `017.md`'s severe band is closed (Group H).

> **What the remaining 264 are, and are not.** The ten `007.md` sections
> cleared earlier were *degenerate output* — a 10-gram recurring ten times in
> 1,118 words. The 264 that remain are a different thing: prose with a
> repetitive register, or (in `017.md`'s case) an inserted block that restates
> part of its own section while also adding material. Treating them as
> degenerate and rebuilding from scratch would destroy recoverable scholarship.
> `017.md` is measured for exactly this in Group H; the same caution applies to
> `007.md`.

---

## Group C — Misaligned bodies in `037.md` — **CLOSED (32/32 fixed)**

`037.md` had **61 verse headings** at the pre-work baseline and **182 now**. The
formatter `normalize.py` promoted roughly 21,326 words of unheaded prose into 121
new verse headings covering **vv 57–177**. The *translation lines* for those
sections were corrected (commit `a14dd59`, 119 swaps), but the **bodies were never
realigned** against their headings.

Consequence, with two verified examples: v62's body discussed *man ʿaṣaynā
al-rasūl* (content belonging to 33:66–67) under a heading about the tree of
Zaqqūm; v182's discussed "We have preferred some of them over others" (2:253)
under a heading about Jonah.

### Status: CLOSED — all 32 fixed and verified

This group was previously recorded as unbounded. Reading every one of the 99
unread promoted-range sections against its own verse translation bounded it at
**32 misaligned sections**, and **all 32 have now been rebuilt from source**:

```
ALL 32, fixed in batches G–O:
  vv 58, 60, 70, 74, 75, 81, 82, 83, 90, 91, 92, 94, 99,
     107, 109, 124, 126, 127, 128, 137, 138, 143, 150, 151,
     154, 160, 162, 164, 166, 168, 172, 173

  G  58, 60, 70, 74          J   99, 107, 150, 154      M  109, 124, 126, 127
  H  75, 81, 82, 83          K  160, 164                N  128, 137, 138, 168
  I  90, 91, 92, 94          L  143, 151, 162, 166      O  172, 173
```

Every fix was verified after application by re-reading the section's opening
prose against its own verse translation, confirming it now describes the verse
it is headed by. All 32 score under the 0.030 duplication gate.

Where several sections share one source note (vv 124–128, 137–138, 161–163,
171–173), each was written on a different portion of that note rather than
repeating it — the verbatim-repetition failure that broke the duplication gate
twice in batch C.

Result for `037.md`: **182 sections, min 139 / median 282 / max 899, 55,576
words total** (median was 238 w when this pass began).

### C2 — The 14 remaining misaligned sections ARE groundable (earlier claim retracted)

An earlier revision of this file claimed these 14 had no source note and
presented a decision between writing them unsourced or leaving them misaligned.
**That claim was false** and the decision it framed was unnecessary.

The cause was the abbreviated-range bug described in A1: `initial/037.md` covers
these verses inside shared range markers, and the parser dropped every such
marker. With the rule applied, coverage is:

| Verses | Covered by marker | Per-verse note |
|---|---|---|
| 109 | `108-9` | no — range only |
| 124, 126, 127, 128 | `124-28` | no — range only |
| 137, 138 | `137-38` | no — range only |
| 143 | `143-44` | no — range only |
| 151 | `149-53`, `151-52` | no — range only |
| 162 | `161-63` | no — range only |
| 166 | `165-66` | no — range only |
| 168 | `167-70` | no — range only |
| 172, 173 | `171-73` | no — range only |

All 14 have apparatus; none has a note naming its own verse alone. The notes are
substantive, not stubs — `124-28` runs 87 words on Baal and the arraignment,
`143-44` runs 165 words including a Prophetic saying, `167-70` runs 114 words on
the pre-Qur'anic promise, `171-73` runs 107 words with a quotation of 40:51–52.

A shared range note is in fact the likely *cause* of the misalignment: when
`normalize.py` promoted unheaded prose into per-verse headings, verses covered
only by a collective note had no verse-specific source to align against. But it
is ample material to rebuild from.

**No decision is needed, and none was taken.** All 14 were rebuilt from these
shared range notes in batches L, M, N, and O. The only caveat is that the
resulting commentary speaks to the passage rather than to the individual verse,
since that is what the source provides — which is the correct treatment, not a
compromise.

Three were re-read in full to confirm the classification is not a headline
artifact:

| Section | Heading's verse | Body actually describes |
|---|---|---|
| `037.md` v58 | "Are we then not to die," | "He who spends his wealth to be purified" (92:18) |
| `037.md` v154 | "What ails you? How do you judge?" | "We are the Descenders" and Qur'anic preservation (15:9) |
| `037.md` v172 | "that they will surely be helped," | "We have made for you an example" (33:21 cross-ref) |

The common shape is an **offset**: the body describes an adjacent or nearby verse,
as though the unheaded prose was sliced against the wrong heading boundaries when
`normalize.py` promoted it. v74 describes v75, v75 describes v76, v83 describes
v84, v107 describes v105, v109 describes v107, v127 describes v130, v143 describes
v146.

Already fixed earlier this session: vv 50, 61, 62, 66, 85, 87, 182 (7 sections).
Rebuilt in total from source apparatus: 25 sections (22 inside the promoted range).

### Why no tool detects this class

Five automated metrics were built against this defect and **all five failed
validation**:

1. 4-gram exact match — 0.0% everywhere, no signal.
2. Paired "own note vs best other note" — claimed 67% of `037.md`; a control run
   flagged 46% of `011.md` and 62% of `040.md`, both verified clean.
3. Transliteration-absent — matched `**Expanded Commentary**` in all 182 sections.
4. Stemming patch to `check_offtopic.py` — raised flags 11 to 45, introducing
   false positives into previously-clean files.
5. Quote-owner lookup by token overlap — degenerate: verse `37:58` ("Are we then
   not to die,") has a single token longer than three characters, so it scored
   1.00 against any quote containing "then", producing four impossible matches.

`check_offtopic.py` remains useful but only catches bodies that under-echo their
own translation; a body can describe the wrong verse while echoing enough
vocabulary to pass. It found 7 of these 39.

**Reading is the only reliable method, and it has now been applied.** The list of
32 above is the complete set within the promoted range as read.

---

## Group D — Detector false positives (4, no action required)

All four were read in full and confirmed to be limitations of the checker, not
content defects:

| Section | Echo | Cause |
|---|---|---|
| `018.md` v75 | 0.0% | Body quotes the verse in Arabic transliteration rather than the English wording |
| `026.md` v132 | 0.0% | Body covers vv 132–134 collectively; `initial/026.md` has no note for them at all |
| `026.md` v176 | 14.3% | One point under the 15% threshold; echoes *inhabitants*/*thicket*, misses *messengers* only because the body says *message* |
| `067.md` v10 | 0.0% | Pure inflection: verse "had we listened… understood", body "listening and understanding" |

A stemming patch was trialled on `check_offtopic.py` and **rejected** — it raised
flags from 11 to 45 and created false positives in previously-clean files
(`040.md`, `007.md`).

---

## Group E — Verified benign (7, no action required)

Translation-line flags from `check_translations.py`. Each was compared side by side
against both `initial/` and `translation/` and confirmed to be a register variant,
not a wrong-verse substitution:

| Section | Score vs `initial/` | Expanded wording | Source wording |
|---|---|---|---|
| `010.md` v91 | 0.36 | "Now? When thou didst disobey before…" | "Now, though previously you disobeyed…" |
| `050.md` v25 | 0.40 | "Hindering the good, a transgressor, full of doubt" | "every hinderer of good, every transgressor, every doubter" |
| `068.md` v3 | 0.20 | "a reward never cut off" | "a reward unceasing" |
| `068.md` v10 | 0.33 | "habitual swearer, contemptible in character" | (variant phrasing) |
| `068.md` v13, v25 | — | register variants | |
| `094.md` v7 | — | register variant | |

---

## Group F — Stylistic outlier (`045.md`)

Emphasis-run density (bold and italic spans per 1,000 words):

| File | Runs / 1,000 w |
|---|---|
| `045.md` | **246.26** (13,099 runs / 53,191 w) |
| `011.md` | 99.27 |
| `076.md` | 84.65 |
| `015.md` | 58.15 |
| `008.md` | 55.24 |
| `040.md` | 49.84 |
| **corpus median** | **25.08** |

`045.md` ranks 1 of 114, roughly 10x the median. Its translations are exact. Most
runs are italics wrapping Arabic transliteration, which is a stylistic choice
consistent within the file. **Left in place by decision** — flagged here only so
the deviation is on record.

---

## Group G — Structural artifacts — **CLOSED (this pass)**

Two defect classes were found in 107 of 114 files. **Every gate reported green
while they were present**, including `validate.py`, whose entire purpose is
enforcing conformance to `001.md`'s skeleton, and which `AUDIT_EXPANDED.md`
section 2 credits with reducing "canonical-skeleton divergence" to
"**0 remaining**". That claim was false.

### G1 — Stray horizontal rules (219)

`001.md` contains exactly 8 rules for 7 verses plus 1 end marker, and **none
anywhere else**. The canonical form is one rule immediately before each verse
heading and one immediately before the end marker, with a blank line before the
rule and none after it:

```
<content line>
<blank>
---
## Sūrah <name> N:<v>
```

Measured against that, the corpus carried **219 illegal rules**:

| Class | Count | Shape |
|---|---|---|
| duplicate | 134 | `---` blank `---` heading (108 at intro→v1, 25 at the end marker, 1 triple in `043.md`) |
| internal | 85 | `---` blank `**Mini-Heading**` — 79 in `021.md`, 6 elsewhere |

**Why `validate.py` missed it.** For each heading it tested `L[i-1] == '---'`
and `L[i-2] == ''`. A duplicated rule satisfies both, because the *second* rule
is at `L[i-1]` and the blank between them is at `L[i-2]`; the stray first rule
sits at `L[i-3]`, which was never examined. The end-marker check tested only
`L[-2]`.

### G2 — Non-canonical H2 headings (11, in 10 files)

`001.md` has 9 ATX headings total: 1 H1, the introduction H2, and 7 verse H2s.
Subdivisions are **bold mini-headings**, as `system_instructions.md` section 4
requires. Ten files carried extra H2s:

| File | Heading |
|---|---|
| `004.md` | `## The Occasions of Its Revelation`, `## Distinguished Contents`, `## Structure of the Commentary` |
| `050.md` | `## Conclusion: The Shape of the Whole` |
| `053.md` | `## Concluding Note to the Commentary` |
| `071.md` | `## Closing: The Sūrah Sealed` |
| `072.md` | `## Concluding Reflection on Sūrah al-Jinn` |
| `073.md` | `## Concluding Reflection` |
| `075.md` | `## Concluding Synthesis` |
| `094.md` | `## Closing Remarks on the Sūrah` |
| `103.md` | `## Closing Reflection: Why Three Verses Suffice` |

`validate.py` never inventoried headings, so all ten passed.

### G3 — Root causes, all in `normalize.py`

1. **`run()`** kept the rule at the end of the preamble slice — `parse()` slices
   the preamble as everything before the first verse heading, so it ends with
   that heading's boundary rule — and then the section loop re-emitted
   `['', '---']`. Result: `---` blank `---` `## Sūrah N:1`. **108 files.**
2. **`run()`** tested only `parts[-2] != '---'` before inserting the closing
   rule, missing one already present at `parts[-3]` after blank collapsing.
   **25 files.**
3. **`clean()`**'s `unglue` inserted `'\n\n---\n\n'` before a heading welded
   mid-line. `fix_section()` later dropped that heading as a remnant, orphaning
   the rule inside the body. **79 internal rules in `021.md`.**

### G4 — Fixes applied

| Fix | Where |
|---|---|
| All three root causes patched | `normalize.py` — preamble strips every trailing rule/blank; end-rule guard looks back past blanks; `unglue` inserts a blank only; `fix_section()` drops orphaned rules and demotes in-section H2s; `fix_preamble()` demotes preamble H2s |
| 219 stray rules removed | `fix_separators.py` (new) — 134 duplicate + 85 internal, across 107 files |
| 11 H2s demoted to bold mini-headings | `fix_headings.py` (new) — content preserved, no words deleted |
| Gate hardened | `validate.py` — new checks: every rule must be immediately followed by a verse heading or the end marker; H2 inventory must equal intro + verses; H3+ rejected |
| Regression test | `test_skeleton.py` (new) — 18 checks, all passing |

### G5 — Verification

```
prose words before all Group G repairs : 6,417,717
prose words after  (007.md rebuilds aside): 6,417,717    delta 0
content lines fingerprinted            : 126,667 -- identical before/after
git diff, classified line by line      : 228 removed (217 blanks, 11 H2s),
                                         11 added (bold forms), 0 unexplained
validate.py                            : PASSED 114/114
normalize.py on the whole corpus       : files written: 0  (idempotent)
test_skeleton.py                       : 18/18 PASS
```

The word-count delta of **−219** reported by a naive `wc -w` style count is
markup, not prose: `---` tokenises as a word under the `[\w'’\-]+` pattern used
throughout this audit. Excluding rule lines, the count is unchanged.

**Proof the gate gap was real.** Against a file carrying all four artifact
classes, the pre-hardening `validate.py` (taken from `git show HEAD:`) reported
only two incidental symptoms and **neither** defect class; the hardened version
reports `stray horizontal rule x5 (4 duplicate, 1 internal)` and
`non-canonical H2 x1`, and `normalize.py` then repairs the file to canonical
form while preserving the injected content as a demoted bold mini-heading.
This is assertion 3 of `test_skeleton.py`.

### G6 — Latent tooling hazard found while testing

`normalize.py`, `apply_sections.py`, `append_block.py` and `apply_026.py` all
hard-coded `ROOT = "/home/user/new"`. Run from a copy — such as a test sandbox —
they silently read and wrote the **real** corpus instead of the copy. All four
now derive `ROOT` from `__file__`. Without this fix, `test_skeleton.py` would
have mutated the shipped corpus during its own run.

---

## Group H — Inserted blocks in `017.md` (111; headings CLOSED, severe band CLOSED)

`017.md` is not like the other files. Every one of its 111 sections carries
exactly one block that a **different generator** spliced in after the rest of
the section was written. Two defects follow from that batch, and they need
different treatments.

All four gates reported green while `017.md` carried 34 sections over the
duplication gate and 111 malformed mini-headings, because `validate.py` checked
neither class.

### H1 — Malformed mini-headings (111) — **CLOSED**

Every block heading was emitted as `****Heading****` instead of the canonical
`**Heading**`. Four leading asterisks do not reliably render as bold; in most
renderers the run opens italic and the heading text comes out mangled.

```
python3 tools/quran-audit/fix_headings.py --dry-run
```

All 111 normalised to `**Heading**`, with heading text preserved character for
character and line counts unchanged (verified by diff). **0 malformed remain
corpus-wide.** `validate.py` now gates `^\*{4,}`.

> **Scope is deliberately narrow.** A broad "line starts with asterisks" scan
> catches 7,000+ legitimate italic prose lines. Only four-or-more leading
> asterisks identifies this class. `***Term*: the rest**` — three leading — is
> valid bold opening with a nested italic and must **not** be "fixed".

### H2 — Redundant blocks, severe band (5) — **CLOSED**

Dropping a block takes `017.md` from 34 sections over the gate to 29, so the
blocks are the cause of the file's flags. But block-vs-section 10-gram overlap
across all 111 ranges 0.05–0.31 (median 0.02 overall, 0.19 among the 34
flagged), which means the blocks are **not** wholesale copies and cannot be
deleted indiscriminately — 97 of the 111 have overlap under 0.20 and carry
original scholarship.

Each of the five worst was therefore justified individually. Method: extract
the block's *distinctive markers* — scholar names, Qur'an citations, ḥadīth
numbers — and test them case-insensitively against the rest of the same
section. A marker absent from the rest is content the section would lose.

| Verse | Duprate | Markers | Unique | Verdict |
|---|---|---|---|---|
| v52 | 0.114 | 12 | **0** | remove — parallel estimates (10:45, 30:55, 46:35, 79:46), 23:115, 40:84–85 *and* the closing al-ʿAṣr sentence are all already in the section |
| v42 | 0.108 | 9 | **0** | remove — restates both readings, 21:22, 23:91, *dalīl al-tamānuʿ*, the Throne, and the modern application |
| v44 | 0.097 | 5 | 1 | remove — a light rephrasing of the paragraph at the preceding heading, down to "the bird in the tree"; the one unique item is the citation *Muslim 1955*, preserved separately (H4) |
| v43 | 0.096 | 18 | **0** | remove — Mālik, Ibn Taymiyyah, al-Bukhārī 6682 / Muslim 2694 and "cognate accusative" all already present outside the block |
| v56 | 0.091 | 7 | **0** | remove — the block heading is a concatenation of two headings the section already has |

```
python3 tools/quran-audit/fix_017_blocks.py /tmp/017.bak --dry-run 42 43 44 52 56
```

`fix_017_blocks.py` locates each block from the pre-fix copy and asserts, per
section, that the surviving non-blank lines are **exactly** the original minus
the block, in order — so no surrounding prose can be disturbed. It also asserts
the duprate falls. 2,160 words removed; the five sections measure **0.000,
0.000, 0.000, 0.008, 0.000**.

`017.md`'s severe band is empty: worst section is now **0.089** (v45), against
0.114 before.

### H3 — Depth consequence, and repair — **CLOSED**

Removing redundancy removes length. Three of the five sections fell below
`017.md`'s former floor of 724 words, and **v43 fell to 369** — the only
section in the entire corpus under 400 words. Redundancy removed is not depth
added, so each was rebuilt from material the section did not already contain:

| Verse | After removal | Rebuilt | New material |
|---|---|---|---|
| v43 | 369 | **1,030** | *ʿuluwwan kabīrā* occurs exactly twice in the sūrah and the two face each other: at 17:4 it is the Children of Israel's blameworthy "great rising", at 17:43 God's praiseworthy elevation. Plus *ʿammā yaqūlūn* picking up 17:42's *ka-mā yaqūlūn*, and the *ʿaẓīm* thread from 17:40's *qawlan ʿaẓīmā* to the bowing formula |
| v42 | 612 | **835** | 17:42 supposes gods *with* Him (*maʿahu*) where 21:22 supposes gods *other than* God (*illā Allāh*); the emphatic apodosis *idhan la-btaghaw*; the apparatus's ontological conclusion that granting the rivals' existence ends the refutation |
| v56 | 631 | **890** | The verse's test run at the end: 28:64 (the same command issued on the Day of Judgment, and they do not answer) and the repudiation cluster at 10:28 and 16:86, closing on 6:17 |

At this point in the pass `017.md` measured 111 sections, min 759 w, median
1,055 w, max 1,975 w, 119,274 w total, with no section under 400 w. All five
rebuilt sections measure 0.000–0.008 duplication.

> **Superseded by H5c.** The 759 w minimum was an artifact of the blocks
> themselves and is withdrawn as a target. Later removals in H5b lowered it.
> `017.md` currently measures **min 584 w, median 1,009 w, 114,244 w total, 0
> sections under 400 w**. The rebuilds recorded in the table above stand — each
> was justified by unused apparatus, not by a word count.

### H4 — Conflicting ḥadīth citation found while removing v44 — **CLOSED**

v44 cited the *iḥsān* ḥadīth as "Abū Dāwūd (2550)" in its own prose while the
block cited "Abū Dāwūd (2877) … (Muslim 1955)" — two different Abū Dāwūd
numbers for one ḥadīth, in one section. The corpus's four other occurrences
(`005.md`, `006.md`, `016.md` ×2) all give **Muslim 1955**, and `005.md` names
the narrator, Shaddād ibn Aws. The surviving citation is aligned to that
consensus, so removing the block loses no attribution.

> `initial/017.md` does **not** record this ḥadīth for v44; it enters from
> general Islamic knowledge, which `system_instructions.md` permits. There is
> no internal source to arbitrate the numbering, so the corpus's own consistent
> attribution is the available evidence.

### H5 — The remaining 29 blocks: **do not bulk-delete**

The 29 sections still over the gate are **not** degenerate prose. Measured:

```
29 blocks, 11,577 words, 1,129 novel content words
```

A *novel content word* is a word of four or more letters, stopwords excluded,
that appears in the block and **nowhere else in its own section**. `v75`'s block
has 10 of its 11 sentences above a 0.25 novelty threshold and 67% novel
vocabulary; `v48` 44%; `v25` 46%; `v21` 45%. Deleting these blocks would
destroy recoverable scholarship and drop several sections below the depth
floor.

The correct treatment is **remove, fold, and rebuild**: excise the block, carry
its genuinely novel content into the heading it belongs under, and author
replacement depth from `initial/017.md`'s apparatus. v45 is worked end to end as
the template.

```
python3 tools/quran-audit/novel_sentences.py --all --min 0.25
python3 tools/quran-audit/novel_sentences.py 45 --min 0.0   # one section, all sentences
python3 tools/quran-audit/fix_017_blocks.py /tmp/017.bak --dry-run <verse>
```

`novel_sentences.py` scores every sentence of a block by the fraction of its
content words absent from the rest of the section, and prints the novel words,
so the handful worth keeping can be read rather than guessed.

> **Why sentence-level scoring is necessary.** A citation count is not enough.
> v45's block scores 0 unique markers, and its two highest-scoring sentences
> (0.57, 0.40) are framing fluff — "The verse's pastoral function is what has
> made it important across the tradition." The one sentence carrying real
> content scores 0.26, because a novel clause is embedded in a long sentence
> that also restates the section: 41:5 is "an **acknowledgment** rather than a
> **complaint**: they know they are not receiving, and they **prefer** it that
> way." Only sentence-level inspection surfaces it.

### H5a — Automated sentence-trimming was tried and **REJECTED**

Because the blocks mix restatement with original material, the obvious
automation is to score each sentence and delete the redundant ones in place,
keeping the novel ones. It was built and measured. **It clears the gate and
destroys the prose.**

Measured first, and the numbers looked good: sentence-level excision clears the
0.030 gate for **26 of the 28** sections, and holds the median section at
**854 w** against 743 w for wholesale block removal, with 6 sections below the
floor instead of 17. Applied to 12 sections, all 12 cleared.

Then the results were read. Three examples:

| Verse | Surviving text after the trim | Defect |
|---|---|---|
| v53 | "The second half of the verse identifies the adversary's method with precision." | Announces content that was deleted; the sentence now points at nothing |
| v33 | "The two together convert vengeance into law…" | "The two" has no antecedent — the sentence naming them was deleted. The heading still promises "Three Options", which the text no longer enumerates |
| v24 | "The word *dhull* is chosen with **equal care**…" | "equal" compares against a deleted sentence; the paragraph then jumps to a ḥadīth about death with no transition |

A back-reference detector caught three such breaks (`This…`, `Its…`, `Both…`)
but **missed all three of the examples above**, because their dangling
references are mid-sentence, not sentence-initial. No cheap heuristic finds
them: the reference is grammatical, and only a reader who knows what was deleted
can see the gap.

The structural reason is decisive. **81 of the 111 blocks are a single
paragraph** (29 have two, one has three), so there is no safe granularity
between "sentence" and "whole block". Paragraph-level trimming collapses into
block removal for most of the file, and sentence-level trimming leaves fragments
that no longer cohere.

The 12 sections that were trimmed have been **reverted byte-for-byte** and the
tool deleted. `novel_sentences.py` is kept — its scoring is what identifies the
content worth preserving — but nothing applies that scoring mechanically.

> **Do not rebuild this.** The gate measures 10-gram repetition and cannot see
> a missing antecedent. Passing it is necessary and nowhere near sufficient.

### H5b — Worklist

Removal is safe and coherent by construction, since a block is a heading plus a
self-contained paragraph: excising it leaves the original section intact. What
varies is how much depth must be rebuilt afterwards, and how much novel content
must be folded in first.

| Section | Now | After removal | Treatment |
|---|---|---|---|
| v37 | 1,180 | 790 | remove; **0** novel sentences, nothing to fold |
| v32, v36, v40 | 1,131 / 1,341 / 1,080 | 785 / 918 / 742 | remove; fold at most a clause or two |
| v28, v38, v49 | 1,136 / 860 / 957 | 754 / 517 / 538 | remove, fold, **rebuild depth** |
| v25, v34, v46, v48, v51 | — | 632 / 819 / 674 / 435 / 779 | remove, fold, rebuild where under ~600 |
| v41, v50, v53, v55 | — | 702 / 476 / 744 / 589 | remove, fold, **rebuild depth** |
| v19, v21, v24, v26, v29, v30, v31, v33, v35, v39, v54, v75 | — | 742 / 752 / 978 / 765 / 722 / 630 / 759 / 896 / 808 / 784 / 524 / 450 | remove, fold; rebuild v54, v75 |

No section falls under the corpus's 400-word Group A floor after removal
(minimum would be 435), so none of this is a Group A violation.

### H5c — The 759-word floor is an artifact, and is **withdrawn**

Earlier in this Group the rebuilds after the severe-band removals were justified
as keeping `017.md` "internally even", because no section of the file sat below
759 w. That reasoning does not survive measurement. The 759 w floor was produced
**by the blocks themselves**: with all 111 blocks removed, `017.md` measures
min 326 w, median 669 w. The floor was not a property of the file's original
composition but of a later insertion inflating every section at once.

The corpus standard is Group A's **400 words**, not a per-file minimum. So the
rule going forward is:

> Rebuild depth only where a section is thin **for its verse** — where the
> apparatus in `initial/017.md` supplies material the section has not used. Do
> not rebuild to reach a number. `system_instructions.md` forbids filler, and
> padding a complete section to hit an artifact floor is exactly that.

Applied, and the two cases that prompted the rule:

| Verse | Words | Verdict |
|---|---|---|
| v43 | 369 → **1,030** | genuinely thin, and the apparatus plus the sūrah's own text supplied real material (H3) — rebuild correct |
| v48 | 430 → **975** | same: two forms of the sorcery charge, the recurrences at 26:153/185 and 17:101, 4:114 (H3) — rebuild correct |
| v49 | 533 → **1,013** | same: 6:94, 18:48 and the ram ḥadīth were unused apparatus — rebuild correct |
| v50 | **596** | **no rebuild.** The verse is the single clause *"Say: Be you of stone, or of iron,"* and the section already works through the hypothetical, the *a fortiori*, 36:79, 30:27's *wa huwa ahwanu ʿalayhi*, the fragment's rhetorical form, the 52:35–36 trilemma, and origination against rearrangement. The apparatus for vv 49–51 is exhausted. More would be filler |
| v55 | **584** | **no rebuild.** Four headings already cover the frame of universal knowledge, the hierarchy with 2:253 and 2:285, the *Zabūr* with 34:10 and the mountains and birds, and the placement after the false deities. `initial/017.md` carries no further note on this verse |

`017.md` now measures **min 584 w, median 1,009 w**, with **0 sections under
400 w** and 10 under the withdrawn 759 w figure. Those 10 are recorded here so
the variance is visible and deliberate rather than overlooked — they are not
defects and are not queued for work.

**Status: OPEN.** Severe band closed; 17 sections cleared (v45, v37, v40, v28,
v30, v31, v32, v34, v36, v41, v46, v48, v49, v50, v53, v55, v29); **12 remain**
— v19, v21, v24, v25, v26, v33, v35, v38, v39, v51, v54, v75 — worst 0.088
(v38). Each still needs its substance tested by direct search before removal,
since the marker comparison produces false positives (H5b).

### H6 — Block identification is position-based, and why that matters

Blocks cannot be found by "the Nth heading in the section" — that heuristic
picks the wrong block. They are identified by the `****` markers in a pre-fix
copy (`/tmp/017.bak`), and `fix_headings.py` preserves line counts, so the
backup's relative offsets stay valid against the current file.
`block017.py /tmp/017.bak <verse>` prints a block with the rest of its section
for comparison; `--list` prints all positions. `fix_017_blocks.py` and
`novel_sentences.py` both verify alignment before acting (106 of 106 blocks
aligned on the current tree, 0 skipped).

---

## Group I — Orphan connector lines (4) — **CLOSED**

Four places carried a bare short word — in every case `and` — alone on a line
between two blockquoted sources:

```markdown
> *"And never would We punish until We sent a messenger."* (Qur'an 17:15)

and

> *"…so that mankind would have no argument against God after the messengers."* (Qur'an 4:165)
```

The word is the remnant of a lead-in reduced to nothing but its conjunction,
and it renders as a stray one-word paragraph.

| File | Lines |
|---|---|
| `076.md` | 167, 222 |
| `094.md` | 175 |
| `109.md` | 98 |

Repair: drop the orphan and the blank following it, so the two quotations sit
adjacent. That is the corpus norm — **2,761 adjacent blockquote pairs across 86
files** against these 4 orphans. The pairing itself carries the corroboration,
so no words the surrounding prose depends on are lost.

```
python3 tools/quran-audit/fix_orphan_connectors.py          # scan
python3 tools/quran-audit/fix_orphan_connectors.py --apply  # repair
```

Scope is narrow. Short lines **ending in a colon** — `and:`, `God says:`,
`Of belief:`, `And ablution:` — are valid lead-ins and are left alone (160 such
lines across 41 files were examined and correctly not flagged). Any connector
over three words is left alone. `validate.py` gates the class; regression tested
both ways (fails on an injected orphan, passes on the clean corpus).

---

## What is already complete

| File | Status |
|---|---|
| `001.md` | Untouched reference (user-confirmed correct) |
| `036.md` | COMPLETE — all 83 sections rebuilt from source apparatus; median 516 w, 43,738 w total; 0 duplication >= 0.030, 0 off-topic |
| `021.md` | COMPLETE — 112 sections, median 1,037 w |
| `011.md` | COMPLETE — 123 sections, 0 translation defects |
| `040.md` | COMPLETE — 85 sections, 0 translation defects |
| `026.md` | Correctness complete (0 defects); depth outstanding — see Group A |

### Defect classes already closed

| Class | Resolution |
|---|---|
| Structural deviation from `001.md` | 114/114 pass **and** genuinely canonical — see Group G; the earlier "0 remaining" claim was false |
| Stray horizontal rules / extra H2s | 219 rules + 11 H2s -> 0; `validate.py` hardened; `test_skeleton.py` added |
| Cross-surah translation substitution | `011.md` vv 105–116+118, `007.md` v170, `040.md` v74, `037.md` 119 lines |
| Appended text in translation lines | `026.md` vv 124/132/146/181/185/208, `011.md` v117 |
| Template filler | 141 sections -> 0 |
| Whole-file leaked scaffolding | `036.md` (16,483 w), `074.md` (17,334 w) -> 0 |
| Residual scaffolding leaks | 5 locations, 10 hits -> 0, with `check_scaffolding.py` added and validated 10 -> 0 |
| Degenerate prose, severe band | `007.md` 10 sections >= 0.100 duprate -> 0, rebuilt from `initial/007.md` |
| Malformed bold mini-headings | `017.md` 111 `****Heading****` -> **0**; `validate.py` gates `^\*{4,}` — see Group H1 |
| Redundant inserted blocks, severe band | `017.md` 5 sections >= 0.09 duprate -> **0**; depth rebuilt where the apparatus supported it — see Group H2/H3 |
| Redundant inserted blocks, moderate band | `017.md` 29 -> **12** sections over the gate (17 cleared, worst 0.114 -> 0.088); 759 w floor withdrawn as an artifact — see Group H5b/H5c |
| Automated sentence-trimming | **tried and rejected** — cleared the gate for 26/28 sections but stranded mid-sentence antecedents; reverted and deleted — see Group H5a |
| Mis-citation in a removed block | `017.md` v34's block attributed 4:10's text to 4:2; the section itself was correct and the error was not carried into the fold |
| Conflicting ḥadīth citation | `017.md` v44 cited Abū Dāwūd 2550 and 2877 for one ḥadīth -> aligned to the corpus consensus, Muslim 1955 — see Group H4 |
| Orphan connector lines | 4 bare `and` lines stranded between blockquotes in 3 files -> **0**; `validate.py` gates the class — see Group I |

---

## Suggested order of follow-up

> **Superseded.** The list below was written when Group C was open and
> unbounded, and when 101 sections were believed ungroudable. Both premises are
> gone: Group C is **CLOSED** (32/32 rebuilt) and the A1 census establishes
> **409 of 410** thin sections are groundable. It is replaced by the list that
> follows.

1. ~~**Group C** — read the 99 unread promoted sections of `037.md`.~~ **DONE.**
2. ~~**Group A1 decision** — rule on the 101 ungroudable sections.~~ **RETRACTED**
   — the figure was an artifact of the abbreviated-range parsing bug; 409 of 410
   are groundable and no ruling is needed.
3. ~~**Group B** — rewrite the 303 inherited duplication cases.~~ **COUNT
   CORRECTED to 279**, of which the 10 worst are now fixed; 269 remain.
4. ~~**Groups D, E, F** — no action.~~ Still no action.

### Current order of follow-up

1. ~~**Group B, severe band in `017.md`**~~ **DONE this pass** — see Group H2
   and H3. All five sections at or above 0.09 are cleared and the depth lost by
   clearing them is rebuilt; `017.md`'s worst section is now 0.089 and no
   section anywhere in the corpus is at or above 0.100.

   > **The prescribed treatment was wrong and should not be reused.** This item
   > said "Same treatment as `007.md`: rebuild from `initial/017.md`." That
   > assumes degenerate output. `017.md`'s duplication was not degenerate prose
   > but **inserted blocks restating their own sections**, and rebuilding the
   > file from scratch would have destroyed the 97 of 111 blocks that carry
   > original scholarship (overlap under 0.20). Diagnose the mechanism before
   > choosing the treatment: `007.md`'s severe band was a 10-gram recurring ten
   > times in 1,118 words, which only a rewrite fixes; `017.md`'s was a
   > duplicated block, which an excision fixes.

2. **Group H5 — the 12 remaining blocks in `017.md`.** Worst is v38 (0.088);
   the rest are v19, v21, v24, v25, v26, v33, v35, v39, v51, v54, v75. 17
   sections were cleared this pass, taking the file from 34 over the gate to 12
   and its worst from 0.114 to 0.088.

   Treatment is **remove, fold, and rebuild only where the apparatus supports
   it** — never automated sentence-trimming (H5a, tried and rejected) and never
   padding to a word count (H5c, the 759 w floor withdrawn as an artifact).
   Before removing any block, test its substance by **direct search for the
   term in the section**, not by marker comparison alone: the marker test
   reported unique content in v32, v53 and v55 that the section already had,
   from citation-format variance and diacritic stripping (H5b). v45 is worked
   end to end as the template.

3. **Group B — remainder of `007.md`.** 100 sections still >= 0.030, 42 >=
   0.060, and `007.md` now holds **seven of the eight worst sections in the
   corpus** (v162 0.099, v25 0.098, v194 0.098, v205 0.097, v149 0.094, v197
   0.092, v190 0.092). The severe band is clear; what remains is moderate.
   **Apply the lesson from item 1**: check whether each is degenerate output or
   prose with a repetitive register before rebuilding, and measure what a
   rewrite would cost in depth.

4. **Group A, depth** — 524 sections under 400 w, 198 under 260 w (figures
   unchanged this pass; the measure is stated above the Group A table and must
   be matched or they will not reproduce). Largest groundable pools first:
   `026.md` (157 under 400 w, median 247) and `037.md` (150 under 400 w, median
   290). 409 of the 410 thin sections have source apparatus; the single
   exception is `026.md` v110. `037.md`'s thinnest are v117 and v167 at **144 w**
   each — corrected this pass from a table cell that wrongly read 245.

5. **Group A, borderline files** — `034.md` (54 sections, median 401 w, min 315)
   and `039.md` (75 sections, median 411 w, min 284) sit just above the
   400-word line. Re-measured this pass, both figures hold. Monitor rather than
   treat as complete.

6. **Groups D, E, F** — no action; recorded so they are not re-investigated.
   **Groups G, H1–H4, I** — closed this pass.
