# Remaining Issues — expanded/ Corpus Audit

**Date:** 2026-09-11
**Branch:** `arena/01a08c61-new`
**Scope:** 114 files, 6,229 sections, 6,292,058 words in `expanded/`
**Reference file:** `expanded/001.md` — confirmed correct by the user, never modified.

Every figure below was produced by running the named tool or script against the
working tree. Nothing is carried over from an earlier estimate. Where a number
could not be established, it is marked **unbounded** and the reason is given.

---

## Gate status (all green)

```
validate.py            PASSED 114/114, FAILED 0
check_translations.py  6,235 checked, 0 missing translation lines, 7 flagged
check_offtopic.py      114 files, 5,551 sections examined, 4 flagged
check_scaffolding.py   114 files, 0 genuine hits
```

Repro from the repo root:

```
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/check_translations.py [--sura N] [--verbose]
python3 tools/quran-audit/check_offtopic.py     [--sura N] [--verbose]
python3 tools/quran-audit/check_scaffolding.py  [--context N] [--sura N]
```

---

## Group A — Content depth

Six files sit below a 400-word median section. Measured ranges:

| File | Sections | Min | Median | Max | Words | <260 w | <400 w |
|---|---|---|---|---|---|---|---|
| `037.md` | 182 | 139 | 245 | 899 | 48,835 | 105 | 160 |
| `026.md` | 227 | 65 | 258 | 874 | 70,109 | 117 | 149 |
| `069.md` | 52 | 245 | 323 | 415 | 17,329 | 2 | 49 |
| `075.md` | 40 | 287 | 360 | 909 | 15,504 | 0 | 28 |
| `073.md` | 20 | 302 | 370 | 1,240 | 8,387 | 0 | 13 |
| `067.md` | 30 | 318 | 392 | 571 | 12,228 | 0 | 16 |

Corpus-wide: **226 sections under 260 w** and **507 under 400 w**, of 6,229 measured.

For comparison, the completed files sit far higher: `021.md` median 1,037 w,
`040.md` 937 w, `011.md` 914 w, `007.md` 730 w, `036.md` 516 w, `074.md` 436 w.

### A1 — Hard limit: sections that cannot be grounded

101 of the thin sections have **no commentary note in `initial/`** for their verse.
There is no source apparatus to build a rewrite from, so deepening them would mean
writing commentary with no source behind it.

| | Groundable | Ungroundable |
|---|---|---|
| Under 260 w | 143 | 81 |
| 260–400 w | 171 | 20 |
| **Total** | **314** | **101** |

`037.md` and `026.md` carry 81 of the 101 ungroudable sections between them.

**Decision needed:** leave the 101 thin, or write them without source support?

---

## Group B — Repetitive prose (303 sections, all inherited)

303 sections score >= 0.030 on the repeated-10-gram duplication measure.

Diffed against the pre-work baseline `48e6cbb`: baseline had **340**, there are
**303** now. Edits made during this project **fixed 37 and introduced 0**. Every
remaining case is inherited, not a regression.

Concentration by file:

| File | Count | Worst |
|---|---|---|
| `007.md` | 109 | 0.200 (v206) |
| `010.md` | 36 | 0.094 (v71) |
| `017.md` | 35 | 0.116 (v52) |
| `014.md` | 29 | 0.107 (v46) |
| `011.md` | 18 | 0.068 (v36) |
| `025.md` | 15 | 0.121 (v36) |
| `039.md` | 15 | 0.081 (v46) |
| `045.md` | 11 | 0.074 (v16) |
| `034.md` | 7 | 0.064 (v31) |
| `020.md`, `076.md` | 5 each | |
| `056.md` | 4 | |
| `026.md` | 3 | |
| `002, 004, 013, 030, 033, 041, 042, 062, 064` | 1–2 each | |

Worst single case, verified by printing the repeated n-gram: `007.md` v206, where
the 10-gram *"is the man who is in the one who is the object"* recurs 10 times in
a 1,111-word section.

Range across all 303: **0.030 – 0.200**.

---

## Group C — Misaligned bodies in `037.md` (correctness risk, NOW BOUNDED: 32 sections)

`037.md` had **61 verse headings** at the pre-work baseline and **182 now**. The
formatter `normalize.py` promoted roughly 21,326 words of unheaded prose into 121
new verse headings covering **vv 57–177**. The *translation lines* for those
sections were corrected (commit `a14dd59`, 119 swaps), but the **bodies were never
realigned** against their headings.

Consequence, with two verified examples: v62's body discussed *man ʿaṣaynā
al-rasūl* (content belonging to 33:66–67) under a heading about the tree of
Zaqqūm; v182's discussed "We have preferred some of them over others" (2:253)
under a heading about Jonah.

### Status: all 99 remaining sections have now been read

This group was previously recorded as unbounded. It is now bounded. Every one of
the 99 unread promoted-range sections was read against its own verse translation,
giving **32 misaligned sections**:

```
vv 58, 60, 70, 74, 75, 81, 82, 83, 90, 91, 92, 94, 99,
   107, 109, 124, 126, 127, 128, 137, 138, 143, 150, 151,
   154, 160, 162, 164, 166, 168, 172, 173
```

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
| Structural deviation from `001.md` | 114/114 pass |
| Cross-surah translation substitution | `011.md` vv 105–116+118, `007.md` v170, `040.md` v74, `037.md` 119 lines |
| Appended text in translation lines | `026.md` vv 124/132/146/181/185/208, `011.md` v117 |
| Template filler | 141 sections -> 0 |
| Whole-file leaked scaffolding | `036.md` (16,483 w), `074.md` (17,334 w) -> 0 |
| Residual scaffolding leaks | 5 locations, 10 hits -> 0, with `check_scaffolding.py` added and validated 10 -> 0 |

---

## Suggested order of follow-up

1. **Group C** — read the 99 unread promoted sections of `037.md`. Highest risk:
   it is a correctness defect, it is unbounded, and no tool catches it.
2. **Group A1 decision** — rule on the 101 ungroudable sections before any depth
   work, since it sets the ceiling on what can be done.
3. **Group A** — deepen the 314 groundable thin sections, largest files first
   (`037.md`, `026.md`).
4. **Group B** — rewrite the 303 inherited duplication cases, starting with
   `007.md` (109 sections) and the worst offenders by score.
5. **Groups D, E, F** — no action; recorded so they are not re-investigated.
