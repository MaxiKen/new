# Depth Plan — Sūrah Āl ʿImrān (Chapter 3)

Working plan and corrections log for bringing `expanded/003.md` to the `expanded/007.md`
standard, per `tools/quran-audit/STANDARDIZATION_PROMPT.md`.

**Status: IN PROGRESS.** The quotation and structure gates are largely closed; the depth gate
is not. §6 states exactly what remains and how much of it there is.

---

## 0. Baseline, measured at commit `0864ef9`

Figures below were produced by running the gates against the file as it stood before this
session, not recalled.

| Measure | Baseline | Note |
|---|---|---|
| Verse sections | 200 | one per verse, canonical skeleton |
| Body words (`check_filler.py` count) | 150,300 | blockquoted verse text excluded |
| min / median / max words | 515 / 756 / 1,481 | 007's median is 1,370 |
| Sections below the 1,200 floor | 199 of 200 | |
| Sections above the 1,400 ceiling | 1 | 3:133 at 1,481 |
| Reduced-floor entries | 0 | none had been configured |
| tics / chains / dup / repeats | 0.05 / 0.27 / 0.017 / 0 | all already inside threshold |
| `validate.py` | 114/114 PASSED | |
| `check_cross_quotes.py 3` | 1,767 spans · 417 cited · 1,350 uncited | **DRIFT 393 · VICINITY 20 · EXACT 4** |
| `census.py --sura 3` | 200 sections · 0 below 260 · 0 below 400 | |
| Blockquotes matching `translation/003.txt` | **0 of 200** | all were the `initial/` rendering |
| `(S:V)` citations in body prose | 326 (1.6 per section) | 007 carries 2,988 (14.5) |

Two structural facts dominated everything else: **not one of the 200 blockquotes was the
authoritative translation**, and **only four of 417 cited quotations were exact**.

---

## 1. Tier-1 list as chosen (§8)

Selected by the six density criteria applied to `translation/003.txt`. 40 of 200 verses = 20%,
inside the specified 15–25%. Now coded in `check_filler.py`.

### DEEPEST (5) — floor 1,400, ceiling 2,100

| Verse | Ground |
|---|---|
| 3:7 | *muḥkam* / *mutashābih*, *zaygh*, *umm al-kitāb*. The tradition disputes the extent of each class and records a dozen positions on who knows the *taʾwīl*. |
| 3:59 | The Adam likeness. The christological crux of the chapter and of the Najrān debate. |
| 3:97 | The ḥajj obligation at the first House, with its condition of ability — a ruling with conditions, exceptions and four schools' positions. |
| 3:103 | The rope of Allah and the prohibition of division. The chapter's ecclesiology in one verse. |
| 3:190 | The alternation of night and day and *ulū al-albāb*. The doxology the chapter closes on. |

### TIER1 (35 further) — floor 1,400, ceiling 1,800

3:2, 3:3, 3:18, 3:19, 3:26, 3:27, 3:31, 3:33, 3:37, 3:42, 3:45, 3:49, 3:55, 3:61, 3:64, 3:67,
3:79, 3:81, 3:85, 3:92, 3:96, 3:102, 3:104, 3:110, 3:130, 3:133, 3:136, 3:144, 3:145, 3:159,
3:169, 3:180, 3:185, 3:195, 3:200.

Grouped by the criterion that qualified each:

- **Divine name, attribute or act stated doctrinally** — 3:2, 3:3, 3:18, 3:26, 3:27, 3:145
- **Legal ruling, or a ruling's conditions** — 3:92, 3:96, 3:97, 3:102, 3:104, 3:110, 3:130, 3:180
- **Covenant, oath or eschatological scene** — 3:19, 3:81, 3:85, 3:133, 3:136, 3:169
- **Named prophetic episode with narrative consequences** — 3:33, 3:37, 3:42, 3:45, 3:49, 3:55,
  3:61, 3:67, 3:79
- **Formula repeated elsewhere, so it can be counted** — 3:31, 3:64, 3:144, 3:159, 3:185, 3:195, 3:200

### SHORT_VERSE (8) — reduced floor 700

Every entry is fourteen words or fewer in `translation/003.txt` **and** one of the three
fragment kinds. Reasons are written into the source alongside each key.

| Verse | Words | Kind |
|---|---|---|
| 3:1 | 1 | *muqattaʿāt* |
| 3:34 | 11 | scene-closer of the ʿImrān-family passage; takes its sense from 3:33 |
| 3:48 | 13 | single clause of the angels' address to Mary, completed in 3:49 |
| 3:63 | 13 | scene-closer of the Najrān debate; takes its sense from 3:61–62 |
| 3:82 | 10 | scene-closer of the prophets' covenant; takes its sense from 3:81 |
| 3:94 | 13 | scene-closer of the food-of-Israel passage; takes its sense from 3:93 |
| 3:138 | 14 | scene-closer of the Uḥud reflection; takes its sense from 3:137 |
| 3:141 | 9 | continuation clause of 3:140 |

Short verses **rejected** for the reduced floor, with the reason (§4 requires the test to be
conjunctive, and these are short but not fragments):

- **3:2** (13 w) — two divine names; the most densely commented verse in the opening. Tier-1.
- **3:5** (12 w) — a complete statement of omniscience with a five-verse concordance.
- **3:131** (9 w), **3:132** (11 w) — standalone commands with live *fiqh* and *ʿaqīdah* material.
- **3:150** (12 w), **3:158** (13 w), **3:196** (13 w) — each carries a complete argument of its own.

---

## 2. Batch log

Word counts are `check_filler.py` body words, before → after, measured on the file.

### Batch 1 — verses 3:2 to 3:6

| Verse | Before | Added | After | Floor | Result |
|---|---|---|---|---|---|
| 3:2 | 634 | 835 | 1,469 | 1,400 | clears, Tier-1 band |
| 3:3 | 653 | 868 | 1,521 | 1,400 | clears, Tier-1 band |
| 3:4 | 837 | 437 | 1,274 | 1,200 | clears |
| 3:5 | 919 | 312 | 1,231 | 1,200 | clears |
| 3:6 | 688 | 542 | 1,230 | 1,200 | clears |

Heads added: 21. Heads struck as duplicates: none dropped, but two candidate heads on 3:5 —
the pastoral reading and the "concealment has no location" argument — were merged into one,
because both rest on the same preposition and would have restated each other.

Corpus totals moved 150,300 → 154,031 body words (**+3,731**); below-floor 199 → 194.

---

## 3. Sections demoted out of Tier-1

**None.** No Tier-1 section was found saturated, because the §9 dedup test could not yet be
run to completion: on 007 the test demoted 22 of 46 listed sections, and that verdict depends
on reading each section's existing heads against the material the verse actually carries. It
has been run for 3:2–3:6 only. Demotions for the remaining 35 Tier-1 verses are still open and
must not be assumed.

---

## 4. Corrections — errors found in this plan and in the file

Numbered, per §17.3. Items 1–8 are errors found in the source file; items 9–13 are errors in
this session's own working assumptions.

1. **All 200 blockquotes were the wrong rendering.** Not one matched `translation/003.txt`;
   all were the `initial/` register ("God", "Thou", "the Living, the Self-Subsisting").
   `check_translations.py` reported **0 flagged**, because the threshold test is against
   *either* source and every line matched `initial/`. A green run of that gate is therefore
   **not** evidence that the blockquotes are correct. Replaced all 200 verbatim.

2. **Seven lines carried stray or missing quotation marks** (1249, 2042, 2585, 2785, 3133,
   3292, 4654). This was not cosmetic. Unbalanced marks desynchronise quote pairing, so the
   cross-quote gate paired the *closing* mark of one quotation with the *opening* mark of the
   next and extracted the prose between them as though it were scripture. That alone accounted
   for 155 of the 393 reported DRIFT spans. Fixed before any quotation work was attempted.

3. **12:3 was misquoted in the commentary.** The file said the Qurʾān calls Joseph's narrative
   "the best of accounts". 12:3 says "the best of stories".

4. **18:98 was attributed to Joseph.** The file wrote "Joseph's *'this is what my Lord made
   true; He has spoken truth'* (the sense of … 18:98 …)". 18:98 is Dhū al-Qarnayn speaking.

5. **Matthew 15:24 was cited as Qurʾān 15:24.** The span "I was sent only to the lost sheep of
   the house of Israel" carries the citation `(15:24)`. Sūrah 15:24 has nothing to do with it.
   **Still open** — see §6.

6. **A ḥadīth was cited as a Qurʾānic verse.** The span *waylun li-man qaraʾahā wa lam
   yatafakkar fīhā* is transliterated ḥadīth, cited to `(3:190)`. **Still open.**

7. **`translation/003.txt` contains unbalanced curly quotes** — 78 U+201C against 76 U+201D.
   This is a property of the input file, not of the commentary, and it sits on `> ` blockquote
   lines that the cross-quote gate skips. Body prose is balanced 2,101 / 2,101. Recorded so a
   later session does not chase it as a defect in `expanded/003.md`.

8. **3:76 fails the echo test at 12.5%.** The only section of 200 below 15%. Its prose uses the
   old register for the verse's own key words, which is the §3.2 vocabulary rule failing in a
   measurable way. **Still open.**

9. **First assumption: DRIFT meant 393 misquotations.** Wrong. After the quote-mark repair the
   honest count was 402 real spans, of which 155 earlier "DRIFT" rows had been extraction
   artifacts. Corrected before drafting.

10. **Second assumption: a global quote toggle would mis-pair.** Tested three conversion
    strategies and measured each with the gate rather than trusting the first. Context-aware
    smart-quoting produced 2,817 opens against 1,799 closes; per-block reset produced DRIFT
    400. The naive global toggle, applied *after* the seven stray marks were fixed, balanced at
    2,308 / 2,308. The measurement chose the method.

11. **Concordance counts were verified by grep, not recalled.** *All-Sustaining* occurs in
    **three** verses (2:255, 3:2, 20:111) and *Ever-Living* in **four** (those two plus 25:58
    and 40:65). An earlier draft sentence claimed the pair occurred "three times" without
    distinguishing pair-membership from single occurrence; the grep showed the claim happened
    to be right for the pair but the reasoning was wrong. The furqān phrase *standard ˹to
    distinguish between right and wrong˺* occurs in **five** verses (2:53, 2:185, 3:4, 8:29,
    21:48), not the six an initial count suggested — 25:1 renders the same noun as "the
    Standard" and 8:41 does not carry the phrase at all.

12. **`cov` from difflib alignment is not a correctness score.** The substitution for 3:142's
    neighbour 2:276 ("God blights ribā and causes charity to grow" → "Allah has made interest
    fruitless and charity fruitful") scored 0.29 and was exactly right, while a 0.67-scoring
    window at 2:170 ran past the end of its sentence and produced a broken span ending mid
    `˹` bracket. Guard rails were added instead of trusting the score: balanced `˹ ˺` pairs,
    no nested double quote, length within 0.5×–2.5× of the original.

13. **The applier failed twice before it was correct.** First on duplicate positions — two
    DRIFT rows on one line resolving to the same offset. Then on overlapping spans, where a
    nested quotation sat inside an outer one and applying the inner invalidated the outer's
    offset. Both were caught by an assertion inside the apply loop, so no partial write
    reached the file.

---

## 5. Gate results at the last commit

| Gate | Result |
|---|---|
| `validate.py` | **114/114 PASSED, 0 FAILED** |
| `check_filler.py --sura 3 --band 1200-1400` | 154,031 words · below 186 · above 0 · reduced-floor 8 · tics 0.07/1k · chains 0.32/1k · dup 0.032 · repeated sentences 0 · **FAILING 186** |
| `check_cross_quotes.py 3` | 1,765 spans · 447 cited · **EXACT 238 · DRIFT 209 · VICINITY 0 · NOVERSE 0 · ELLIPSIS 0** · uncited 1,318 |
| `census.py --sura 3` | 200 sections · 0 below 260 · 0 below 400 |

Movement on the quotation gate since baseline: EXACT 4 → 238, DRIFT 393 → 209,
VICINITY 20 → 0. `validate.py` was 114/114 before and is 114/114 after every edit.

007 regression check (§14 requirement): `check_filler.py --sura 7` still reports **277,675
words, FAILING 0, reduced-floor 18**, and `check_cross_quotes.py 7` still reports **1,780
EXACT**. Unchanged.

Manual checks (§12.3), each printing the number of sections examined — `examined: 0` treated
as failure:

| Check | Examined | Result |
|---|---|---|
| Echo test (§3.3) | 200 sections (1 skipped, <3 distinctive tokens) | 1 below 15% (3:76 at 12.5%); median 60% |
| Recap scan (§11.2) | 200 sections | 0 blocks above the 90% content-word overlap threshold |
| Scaffolding scan (§11.3) | 4,960 lines | 10 raw hits, all the ordinary adverb "actually"; **0 genuine leaks**; no `[System Memory Check]` trailer anywhere |

---

## 6. What remains, measured

This is the honest statement of the gap, so the next session does not have to rediscover it.

1. **Depth is the open gate.** 186 of 200 sections are below their floor. Closing them means
   roughly **+110,000 body words** at 007's shape (8–10 unique mini-headings, ~160 words per
   head, ~80-word paragraphs). Batch 1 added 3,731 words across five sections. At that rate
   the chapter needs around thirty more batches.

2. **209 DRIFT spans remain.** These are quotations still in the `initial/` rendering. The
   tooling that fixed the first 191 is a difflib aligner plus guard rails; the residue needs
   per-item judgment, because a large share are cases where **the citation itself is wrong**
   (3:123's section cites 8:9 for 8:44's content) or where **the "quotation" is not Qurʾān at
   all** (corrections 5 and 6 above). For those the fix is a corrected reference, a
   re-attribution to the ḥadīth or to the Gospel, or removing the quotation marks so a
   paraphrase is no longer presented as scripture.

3. **Citation density is 2.2 per section against 007's 14.5.** 1,318 quoted spans carry no
   citation. Most are genuine Qurʾānic quotations in the old wording; each needs to be found in
   `translation/` and cited immediately after it, or de-quoted.

4. **Vocabulary is still the `initial/` register in the body.** The blockquotes now say
   *Allah*; the prose beneath them largely says *God*. §3.2 requires the translation's word
   throughout, and 3:76's echo failure is that rule showing up as a number. Harmonising it
   across 154,000 words is part of the depth work, not separate from it.

5. **The §9 dedup test has been run for five verses.** Until it is run for the other 35 Tier-1
   verses, no demotion verdict is available and §3 of this document stays empty by default
   rather than by finding.
