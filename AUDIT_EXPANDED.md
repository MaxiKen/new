# Audit — `expanded/`

All 114 files checked against the confirmed reference **`expanded/001.md`**, and every
verse's translation cross-checked against its source in `initial/NNN.md` and
`translation/NNN.txt`.

## Current status

| Gate | Result |
|---|---|
| Structural conformance vs `001.md` | **114 / 114 PASS**, 0 FAILED |
| Verse sections | **6,236** across 114 files, 6,487,229 words |
| Translation text vs source | **7 flagged of 6,235** — all 7 verified register variants, not defects |
| Missing translation lines | **0** |
| Off-topic commentary | **25 flagged of 5,551** examined |
| `001.md` | never modified |

Every number below is reproducible with the scripts in `tools/quran-audit/` (see the end).
Where a figure is a historical record of work already done rather than a current
measurement, it is labelled as such.

---

## The canonical shape (taken from `001.md`)

```
# Sūrah al-Fātiḥah (Chapter 1) — Expanded Verse-by-Verse Commentary
                                      <- blank
## Introduction to the Sūrah
                                      <- blank
**Expanded Commentary**
                                      <- blank
**Unique mini-heading**  … body …
                                      <- blank
---
## Sūrah al-Fātiḥah 1:1
                                      <- blank
> **In the Name of God, the Compassionate, the Merciful.**
                                      <- blank
**Expanded Commentary**
                                      <- blank
**Unique mini-heading**  … body …
…
                                      <- blank
---
**[End of the commentary on Sūrah al-Fātiḥah]**
```

LF endings, no trailing whitespace, no consecutive blank lines, one trailing newline.

---

## Formatting defects found and fixed (historical record)

Applied to 113 files (everything except `001.md`). Totals from
`tools/quran-audit/last_fixlog.json`:

| # | Defect | Fixed | Where |
|---:|---|---:|---|
| 195 | Italic wrapper inside the translation line (`***text***`) | 195 | 012 (111), 040 (84) |
| 166 | Unclosed quotation mark in a translation | 166 | 35 files |
| 122 | Heading welded to the end of the previous line | 122 | 037 (121), 018 (1) |
| 91 | Missing `---` before the end marker | 91 | 91 files |
| 73 | Consecutive blank lines | 73 | 32 files |
| 69 | Non-canonical / absent end marker | 69 | 69 files |
| 57 | CRLF line endings → LF | 57 | 57 files |
| 25 | Leaked `> **[System Memory Check]**: system_instructions.md loaded…` | 25 | 037 (22), 073, 097, 105 |
| 19 | Arabic-script translation line above the English | 19 | 082 |
| 8 | Intro heading not followed by `**Expanded Commentary**` | 8 | 028, 033, 037, 040, 043, 068, 073, 113 |
| 6 | Wrong intro heading text | 6 | 004, 017, 033, 037, 068, 073 |
| 5 | Wrong H1 | 5 | 017, 037, 040, 068, 070 |
| 4 | Leaked generation-process meta prose | 4 | 012, 033, 040, 043 |
| 1 | Duplicate verse heading | 1 | 018 (a second `18:103`) |
| 1 | Verse-translation blockquote buried under the first mini-heading | 1 | 040 v76 |
| 1 | Stray `---` above the intro heading | 1 | 040 |

Also normalised, counted inside the rows above: 511 missing `---` separators before verse
headings; **726 verse-translation blocks rewritten to the single canonical
`> **…**` line** — 037 (182), 012 (111) and 040 (85), 043 (89) and 033 (73), 084 (25),
082 (19, dropped Arabic line), plus 142 quote-mark repairs; 61 bracketed headings
`[37:N]` → `37:N`; 44 `Sūrat` → `Sūrah` in 070; 48 files given a trailing newline and 8
stripped of surplus ones.

**No commentary text was deleted.** Verified by comparing the substantive prose lines of
every file before and after; exactly **23 lines** differ and each is accounted for (7
variant end-markers; 15 process-meta block lines; 1 welded duplicate heading in 018 whose
paragraph text is intact).

### The four process-meta blocks removed

These describe the *generation workflow*, not the Qur'an, and `001.md` contains none:
**040** (italic note under the H1), **033** (`## Editorial and Source Note`),
**012** (`**How This Commentary Reads the Source**`), **043**
(`**Source, quotation, and interpretive conventions**`).

---

## Content defects repaired (historical record)

### 1. Mis-anchored / substituted verse text

The heading names verse *N*; the translation carried some *other* verse.

| File | Sections | What was wrong | Status |
|---|---:|---|---|
| **037.md** | 119 | Cross-sūrah content substitution: of 182 sections, 63 matched `initial/`, 2 matched `translation/`, **117 matched neither**. The original had 61 headings; vv 57–177 were 21,326 words of unheaded content that `normalize.py` promoted into verse headings. 97 of 121 quote other sūrahs. | **0 of 182 mismatch** |
| **011.md** | 13 | vv 105–116, 118 carried text from other sūrahs entirely (v105→81:1, v106→55:17, v107→25:61, v108→10:5, v109→30:30, v110→80:1, v111→37:179, v112→37:126, v113→109:1, v114→81:28, v115→69:39, v116→48:7, v118→37:179) | **0 of 123 flagged** |
| **040.md** | 5 | vv 31, 48, 50, 63 each carried the **next** verse's translation; v73 had fused 40:73+74+75 into one line | **0 defects** |
| **040.md v74** | 1 | Whole section carried 40:75's text *and* Arabic | rewritten |
| **007.md v170** | 1 | Carried a continuation of 7:169 | rewritten |
| **026.md** | 6 | vv 124, 132, 146, 181, 185, 208 — translation line carried its own verse **plus the text of the verses that follow** (v124 ran through vv 125–127). Verified each following section exists separately with correct text before trimming, so no content was lost. | trimmed |
| **011.md v117** | 1 | Translation line carried an appended sentence (*"But if they reform, He will never destroy them."*) absent from both sources | stripped |

### 2. Empty sections — 36 (026.md)

Heading only, no translation or commentary: vv 104, 122, 125–127, 133–134, 140,
142–145, 147–148, 151–152, 161–164, 173, 175, 177–180, 182–183, 186, 191, 204,
206–207, 209, 211–212. **All 36 filled. `026.md` now has 227 sections, 0 defects.**

### 3. Degenerate / template-filler commentary

Translations correct; commentary was circular filler that repeated its own clauses, plus
fabricated Arabic transliteration. Measured as the rate of repeated 10-word sequences
inside a section (corpus median 0.00; `001.md`'s worst 0.0031).

| File | Sections | Status |
|---|---:|---|
| **021.md** | 91 | **COMPLETE** — 112/112 sections ≥976 words, 121,660 words |
| **011.md** | 53 | **COMPLETE** — 0 filler sections of 123; median 914 words |
| **007.md** | 10 | repaired |
| **025.md** | 5 | repaired by deletion (sound prose with duplicated blocks) |
| **017.md** | 4 | repaired by deletion |
| **026.md**, **029.md** | 2 | repaired |

A separate template-filler phrase scan found **141 phrases corpus-wide**, concentrated in
`011.md` (132 phrases across 53 sections). `011.md` is now at **0**.

### 4. Style outlier — 045.md (left in place by decision)

328 runs of single-word emphasis (`*human* *cannot* *tame*`) against 53,191 words —
**6.17 per 1,000 words**, where `001.md` and the corpus median are both 0.00. Its verse
translations are all exact and the text is coherent, so this is an emphasis-style
deviation, not corruption; stripping it risks removing legitimate italics.

### 5. Register variants — NOT defects (do not "fix")

**7 sections** score <0.45 against both sources but render their own verse in different
words. Each was verified side-by-side:

`010.md` v91 · `050.md` v25 · `068.md` vv 3, 10, 13, 25 · `094.md` v7

Previously retracted on the same grounds: `068.md` v9, `094.md` v3, `073.md` v2,
`108.md` v2, `087.md`/`010.md`/`050.md` 1 each. Other known legitimate variants:
`068.md` v24, `102.md` v3, `108.md` v3, `020.md` v1, `021.md` vv 73–76/78/97.
`001.md` itself sets the precedent — its v5 scores 0.83 against the source wording.

---

## Content defects still outstanding

### A. `074.md` — leaked drafting notes, 54 of 56 sections

The file's two closing blocks are **generation scaffolding, not commentary**. 54 of 56
sections carry a `**Cross-Referential Web for Verse N**` block and a
`**Practical Tarbiyyah Exercise for Verse N**` block whose text is **byte-identical across
all 54 sections** — including the verse number in the heading only.

The blocks contain visible drafting artifacts:

> *"For responsibility verses, link to Sūrah al-Muddaththir's sister Sūrah
> al-Muddaththir? **Actually link to** 52:21 — …"*

That is the author hesitating mid-note, and the self-reference is nonsense (the sūrah's
sister is itself).

Measured: of `074.md`'s 42,944 words, **25,988 (61%) are the repeated boilerplate tail**.
Median section is 756 words, of which **481 are boilerplate** — leaving **276 words of
genuine per-verse content** against a corpus median near 900.

### B. `036.md` — whole-file template, all 83 sections

Every one of the 83 sections reuses the same three mini-headings —
*A Word Carried by the Arabic*, *The Qur'an Explains the Qur'an*,
*The Verse Brought into Daily Life* — and repeats **8 sentences verbatim 83 times each**,
e.g. *"Arabic wording matters because translation necessarily selects one edge of a word's
range."* **100% of sections** contain at least one shared sentence.

Sections are also thin: median **422 words** (min 390, max 488) against a corpus median
near 900. The prose is on-topic — this is not the off-topic class — but it is boilerplate.

### C. Off-topic sweep — 25 of 5,551 examined

First valid run of this sweep. (`check_offtopic.py` flags a section when <15% of its
translation's distinctive tokens are echoed in its commentary body.)

| File | Flagged | Note |
|---|---:|---|
| 036.md | 13 | the template defect above; short bodies under-echo by construction |
| 037.md | 7 | vv 50, 61, 62, 66, 85, 87, 182 — all under 161 words |
| 026.md | 2 | vv 132, 176 |
| 018.md, 040.md, 067.md | 1 each | v75, v3, v10 |

The 036.md and 037.md hits are depth/template artifacts rather than subject drift; they
should be re-measured after A and B are fixed. The 018/040/067 hits are unreviewed.

### D. Depth — files still well under the corpus median

| File | Sections | Median words | Min |
|---|---:|---:|---:|
| 037.md | 182 | 231 | 139 |
| 026.md | 227 | 258 | 65 |
| 069.md | 52 | 323 | 245 |
| 075.md | 40 | 360 | 287 |
| 073.md | 20 | 370 | 302 |
| 067.md | 30 | 392 | 318 |
| 034.md | 54 | 411 | 321 |
| 039.md | 75 | 415 | 288 |

`037.md` and `026.md` are **correctness-complete** — every translation matches its source
and there are 0 structural or content defects. What remains is depth only.

---

## Reproducing this audit

Run from the repository root:

```bash
python3 tools/quran-audit/validate.py            # structural conformance vs 001.md
python3 tools/quran-audit/check_translations.py  # verse text vs initial/ + translation/
python3 tools/quran-audit/check_offtopic.py      # commentary drift (prints sections examined)
python3 tools/quran-audit/check_degeneracy.py    # repetitive-filler detector
python3 tools/quran-audit/extract_source.py 11 94 98   # dump source + covering commentary
```

Regeneration pipeline: `extract_source.py <sura> <lo> <hi>` → write
`content_<sura>_<batch>.py` with a `SECTIONS` dict → `apply_sections.py <sura> <module.py>`
→ **`validate.py` immediately** → `check_translations.py --sura N` → measure words /
duprate / filler → commit.

`tools/quran-audit/normalize.py` is the idempotent normaliser that produced the formatting
fixes; it never writes `001.md`. **Caveat: on `037.md` it promoted 121 unheaded blocks into
verse headings**, which is how that file came to have 182 sections from an original 61.
`last_fixlog.json`, `last_classification.json` and `last_degeneracy.json` are its most
recent outputs.
