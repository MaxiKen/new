# Audit — `expanded/`

All 114 files checked against the confirmed reference **`expanded/001.md`**, and every
verse's translation cross-checked against its source in `initial/NNN.md`.

- **Formatting: 113 / 114 files now conform.** `001.md` is byte-identical to before
  (`cmp` passes) — it was used as the pattern only, never rewritten.
- **Content: 110 mis-anchored verse sections, 36 empty sections, and 123 sections of
  degenerate commentary still need regeneration.** These cannot be fixed by formatting.

Reproduce every number below with the scripts in `tools/quran-audit/` (see the end).

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

## Formatting defects found and fixed

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
`> **…**` line** — 037 (182, `> **Verse Translation:** …` label), 012 (111) and 040 (85)
(`> **N** *…*` numbered-italic), 043 (89) and 033 (73) (three-line
`> **Verse Translation**` / `>` / `> text` form), 084 (25, numbered), 082 (19, dropped
Arabic line), plus 142 quote-mark repairs; 61 bracketed headings `[37:N]` → `37:N`; 44
`Sūrat` → `Sūrah` in 070; 48 files given a trailing newline and 8 stripped of surplus ones.

**No commentary text was deleted.** This was verified by comparing the substantive prose
lines (headings, translation lines and structural lines excluded) of every file before and
after. Exactly **23 lines** differ, and each is accounted for:

| Lines | Files | What they were |
|---:|---|---|
| 7 | 003, 007, 026, 034, 052, 062, 107 | variant end-markers, replaced by the canonical `**[End of the commentary on Sūrah …]**` |
| 15 | 012 (2), 033 (8), 040 (1), 043 (4) | the four process-meta blocks itemised below |
| 1 | 018 | not a deletion: this paragraph simply had the welded duplicate `## Sūrah al-Kahf 18:103` stripped from its tail. Its text is intact — it ends `…verse 102 is the closing argument.` at line 4902 |

Translation lines are excluded from that comparison because every one of them was
re-wrapped (e.g. `> **Verse Translation**` / `>` / `> text` → `> **text**`); their words
are unchanged. Spot-checks confirm this — 033's closing paragraph "The final word is
neither confidence…" is still present at line 3498.

### The four process-meta blocks removed

These describe the *generation workflow*, not the Qur'an, and `001.md` contains none:

- **040** — an italic note under the H1: *"…in the style and at the depth of the expanded
  commentary on Sūrah al-Baqarah. Each verse is treated as its own section…"*
- **033** — the whole `## Editorial and Source Note` section, incl. *"Each section was
  completed and retained locally in numerical order before the next was written; the
  chapter file was assembled only after verse 73 was complete."*
- **012** — `**How This Commentary Reads the Source**`, citing `` `initial/012.md` ``
- **043** — `**Source, quotation, and interpretive conventions**`, citing `` `initial/043.md` ``

---

## Content defects — need regeneration

### 1. Mis-anchored verse text — 110 sections

The heading names verse *N*; the translation is some *other* verse.

| File | Sections | Verses | What is wrong |
|---|---:|---|---|
| **037.md** | 95 | 48–57, 59, 61–69, 71–75, 77–81, 83–88, 90, 92–94, 97–98, 100–103, 106, 108–112, 119–125, 127–129, 131–132, 134–135, 137, 139–145, 150–152, 154, 157–159, 161–163, 166, 168–171, 173, 176–182 | Verses 1–47 are correct. From v48 the sequence drifts — by v74 it is off by one (v74 carries 37:75 *"And indeed Noah cried out to Us"*, v75 carries 37:76, v77 carries 37:78), and elsewhere the text belongs to unrelated verses (v68 carries 37:44). v55's translation is the literal placeholder `> **(continued verse 55 — part of paradise/hell sequence)**`, and line 1050 still reads `Verse ${n} continues the description…`. |
| **011.md** | 10 | 13, 106–109, 111–112, 115–116, 118 | v13 carries **11:35's** text (*"If I fabricated it, then my guilt is upon me"* — a string-identical match to `initial/011.md` v35). v106–116/118 carry text from other sūrahs entirely: v106 is *"[He is] the Lord of the two Easts and the two Wests"* (55:17), v109 is *"So turn your face to the religion of God"* (30:30). |
| **040.md** | 4 | 31, 48, 50, 63 | Each carries the **next** verse's translation (v31↔40:32, v48↔40:49, v50↔40:51, v63↔40:64). The v31 shift is downstream of v30, whose translation has 40:31's text appended to it (*"…a day like the Day of the Allied Parties — the like of the people of Noah, ʿĀd, and Thamūd…"*), so v30 needs trimming as well. |
| **007.md** | 1 | 170 | Carries a continuation of 7:169 (*"So if other ephemeralities come to them…"*), not 7:170. |

*Not* defects: `068.md` v24, `102.md` v3 and `108.md` v3 were flagged by the similarity
check and cleared on inspection — each renders its own verse in different words
(102:3 and 102:4 are near-identical in the source, which is what tripped the check).
A further 52 sections are looser paraphrases of the **correct** verse; `001.md` itself
sets that precedent (its v5 scores 0.83 against the source wording), so they were left alone.

### 2. Empty sections — 36 (026.md)

Heading only: no translation, no commentary.

`026.md` verses 104, 122, 125–127, 133–134, 140, 142–145, 147–148, 151–152, 161–164,
173, 175, 177–180, 182–183, 186, 191, 204, 206–207, 209, 211–212.

Six further sections in 026 (141, 150, 160, 172, 176, 185) carry the sūrah's repeated
refrain *"Truly in that is a sign, but most of them are not believers"* — correct, since
the sūrah repeats it verbatim.

### 3. Degenerate commentary — 123 sections

Translations are right; the commentary is circular filler that repeats its own clauses,
plus transliterations that do not correspond to the Arabic. Measured as the rate of
repeated 10-word sequences inside a section: **corpus median 0.00, `001.md`'s worst
0.0031**, versus 0.43–0.48 for the worst offenders.

| File | Sections | Verses |
|---|---:|---|
| **021.md** | 91 | 20–21, 24–112 |
| **011.md** | 11 | 106–107, 110–113, 116, 118–119, 122–123 |
| **007.md** | 10 | 15, 137, 141, 164, 185, 189, 195, 200, 204, 206 |
| **025.md** | 5 | 31, 50, 57, 60, 77 |
| **017.md** | 4 | 35, 40, 42, 52 |
| **026.md** | 1 | 103 |
| **029.md** | 1 | 18 |

Example, `021.md` v20: *"the continuity is the sūrah's way of telling the reader that the
praise is not a tiring"*, with the verse glossed as *`Wa-hum yaṣḥabūna bil-aylī
wa-al-nahār`* — the actual text is *yusabbiḥūna al-layla wa-l-nahār*.

### 4. Style outlier — 045.md

328 runs of single-word emphasis (`*human* *cannot* *tame*`) against 53,191 words —
**6.17 per 1,000 words**, where `001.md` and the corpus median are both 0.00 (076.md is
0.50). Its verse translations are all exact. The text is coherent, so this is an
emphasis-style deviation, not corruption; left in place because stripping it risks
removing legitimate italics.

---

## Regeneration scope

| Task | Sections |
|---|---:|
| 037.md verses 48–182 (mis-anchored) + a missing `## Introduction to the Sūrah` body | ~135 |
| 021.md verses 20–112 (degenerate commentary) | 91 |
| 026.md (36 empty + v103) | 37 |
| 011.md v13 + 105–118 | 14 |
| 007.md (1 mis-anchored + 10 degenerate) | 11 |
| 025.md, 017.md, 029.md | 10 |
| **Total** | **~298** |

---

## Reproducing this audit

Run from the repository root:

```bash
python3 tools/quran-audit/validate.py            # structural conformance vs 001.md
python3 tools/quran-audit/check_translations.py  # verse text vs initial/NNN.md
python3 tools/quran-audit/check_degeneracy.py    # repetitive-filler detector
python3 tools/quran-audit/dump_section.py expanded/037.md 55   # print one section
```

`tools/quran-audit/normalize.py` is the idempotent normaliser that produced the
formatting fixes; it never writes `001.md`. `last_fixlog.json`,
`last_classification.json` and `last_degeneracy.json` are its most recent outputs.
