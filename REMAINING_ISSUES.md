# Remaining Issues — expanded/ Corpus Audit

**Date:** 2026-09-11
**Branch:** `arena/01a08c61-new`
**Scope:** 114 files, 6,236 sections, 6,316,569 words in `expanded/`
**Reference file:** `expanded/001.md` — confirmed correct by the user, never modified.

Every figure below was produced by running the named tool or script against the
working tree. Nothing is carried over from an earlier estimate. Where a number
could not be established, it is marked **unbounded** and the reason is given.

---

## Gate status (all green)

```
validate.py            PASSED 114/114, FAILED 0
check_translations.py  6,235 checked, 0 missing translation lines, 7 flagged
check_offtopic.py      114 files, 5,544 sections examined, 4 flagged
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
| `037.md` | 182 | 166 | 309 | 899 | 59,527 | 61 | 143 |
| `026.md` | 227 | 65 | 258 | 874 | 70,034 | 117 | 149 |
| `069.md` | 52 | 245 | 323 | 415 | 17,329 | 2 | 49 |
| `075.md` | 40 | 287 | 360 | 909 | 15,504 | 0 | 28 |
| `073.md` | 20 | 302 | 370 | 1,240 | 8,387 | 0 | 13 |
| `067.md` | 30 | 318 | 392 | 571 | 12,228 | 0 | 16 |

Corpus-wide: **182 sections under 260 w** and **490 under 400 w**, of 6,236 measured.

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

## Group E — Translation lines: 16 real defects found and fixed

This group was previously recorded as **7 benign flags, no action required**. That
conclusion was **wrong** and is retracted. It rested on `check_translations.py`,
whose overlap coefficient uses `min(|A|,|B|)` as the denominator — which lets a
*different* verse pass whenever the own-verse text is short. `037.md` v156 scored
0.75 against text belonging to `11:96`.

### E1 — The method that works

A low score is not evidence of a defect, and a high score is not evidence of
correctness. Two separate tests are needed:

1. **Own-verse match** — normalise, take tokens of length ≥2, Jaccard against
   *both* `initial/` and `translation/` for that verse. Below 0.90 → read it.
   (Tokens ≥2, not >3: a `len(w)>3` filter empties the token set on short verses
   like `Yā. Sīn.` and scores 0.00 on an exact match. That artifact manufactured
   ~64 false flags and was rejected.)
2. **Exact-match to a different verse** — build a normalised-string index of the
   whole corpus; a line that is verbatim another verse is a definite substitution.

Neither threshold alone is sufficient. The control that exposed this:
**`001.md`, the user-confirmed reference, itself scores 0.67 and 0.76 at v5 and
v7**, because it blends both sources ("You alone we worship, and from You alone
we seek help"). Legitimate hybrids exist, so every survivor must be *read*.

### E2 — Corpus-wide result

| Test | Result |
|---|---|
| Exact match to a different verse | **0 genuine** (2 hits, both benign) |
| Lines below 0.90 against both own-verse sources | 609, of which the great majority are paraphrase register |
| Files whose *median* is below 0.90 | 12 — see E4 |

The 2 exact-match hits are not defects: `026:67` differs from its own verse only
by *but*/*though* (and matches the sūrah's repeated refrain at 26:8/103/121), and
`055:63` differs only by a trailing em-dash.

### E3 — The 16 lines corrected

All replaced from `initial/` via `fix_translation.py` (dry-run first) and verified
at own-verse match **1.00**. Re-verified intact after five branch resets.

| Section | Was carrying | Should read |
|---|---|---|
| `011.md` v13 | `11:35` | own verse |
| `037.md` v95 | `21:66` | own verse |
| `037.md` v130 | `19:15` | own verse |
| `037.md` v156 | `11:96` | own verse |
| `037.md` v117 | `2:53` ("Scripture and the Criterion") | "the Book that makes clear" |
| `037.md` v167 | cf. `26:153` ("one of those possessed") | "Indeed, they used to say" |
| `037.md` v114 | favour given *through* them to another | "We were gracious unto Moses and Aaron" |
| `037.md` v118 | purpose clause, 2nd person | past tense, dual: "guided the two of them" |
| `037.md` v175 | "a covenant… a clear proof" (unrelated) | "and observe them; for they will soon observe" |
| `037.md` v149 | dropped "your Lord" — the point of the challenge | "does your Lord have daughters" |
| `037.md` v165 | third person ("among them are those") | first person ("truly we are those") |
| `037.md` v146 | run-on with v145's text glued on | "We caused a gourd tree to grow over him" |
| `026.md` v150, v172, v205, v210 | following verses glued on | own verse only |

### E4 — Bodies had to be rebuilt, not just the lines

**Correcting a translation line without rebuilding its body creates a fresh
misalignment**, because the body had been written to describe the wrong verse.
`check_offtopic.py` does **not** catch this class. Twelve bodies were rebuilt from
the source apparatus: `037.md` vv 95, 130, 156, 117, 165, 167, 114, 118, 175, 149,
49, plus v179 (whose line was correct but whose body described Isaac and Jacob).

`037.md` v49 is a distinct sub-class: its body glossed the verse as
*ka-annahunna al-yāqūt wa-l-marjān* and explained *yāqūt* as rubies and *marjān*
as coral. That is the imagery of **55:58**, not `37:49`, whose apparatus concerns
*bayḍ* (eggs) and its relation to whiteness. The invented transliteration is gone;
no `yāqūt`/`marjān` remains in the file.

### E5 — The 12 paraphrase-register files

These sit below a 0.90 median **file-wide**, so the deviation is a consistent
editorial register rather than corruption. Sampling confirmed each says the right
thing for the right verse (`108:3` "it is your hater who is cut off" for "thine
enemy shall be the one without posterity"; `004:128` "fears from her husband
ill-treatment or aversion" for "fears animosity or desertion").

`108.md` `094.md` `087.md` `068.md` `040.md` `048.md` `073.md` `102.md` `010.md`
`071.md` `050.md` `016.md`

**Left in place.** Normalising them to `initial/` would be a stylistic
unification across ~1,100 sections, not a correctness fix, and it would move them
away from the register `001.md` itself uses.

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
