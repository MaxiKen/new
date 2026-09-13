# DEPTH_PLAN_003 — Sūrat Āl ʿImrān (chapter 3, 200 verses)

Working plan and corrections log for bringing `expanded/003.md` to the
`expanded/007.md` standard, per `tools/quran-audit/STANDARDIZATION_PROMPT.md`.

**Every figure in this document was measured in the step that writes it, against
the tree as it stood at that moment (§23.3). Nothing is recalled from memory.**
Where a figure is quoted it carries the command that produced it.

Baseline for all before/after measurements: commit `7c85d9a` (`Update print
statement from 'Hello' to 'Goodbye'`), the commit this session branched from.

---

## 1. Status of this chapter — read this first

**Correctness and depth are separate axes and are reported separately (§23.5).**

| Axis | State at the end of this run |
|---|---|
| Structure (§5, pass 1) | **complete.** `validate.py` 114/114, `normalize.py 3` idempotent, 0 stray rules, H2 inventory = intro + 200 verses |
| Translation re-sourcing (pass 3) | **complete.** 200 of 200 blockquotes byte-exact against `translation/003.txt`; 0 still matching `initial/003.md` |
| Citation integrity (pass 4) | **complete** for the classes that are mechanically decidable. 0 non-existent verse references, 0 unverified ḥadīth numbers left in the file, 0 drafting-debris hits |
| Quote register (passes 5–6) | **partly complete.** DRIFT 393 → 331, EXACT 4 → 126, VICINITY 20 → 0. 331 drifted spans remain |
| Duplication (pass 7) | **complete.** `census.py --dup 0.030` reports 0 sections at or above the gate on the 'whole' span |
| Depth (pass 8) | **not started.** 190 sections below their floor; median 756 words against a 1,200–1,400 band |

The chapter is **not finished**. Pass 8 — the expansion that carries 007's
277,675 words — is outstanding, and with it the residual 331 drifted quotations.
§9 below states the measured size of that gap and why it was not closed.

---

## 2. Pass 0 — the audit, measured before anything was touched

```
python3 tools/quran-audit/check_filler.py --sura 3 --band 1200-1400
python3 tools/quran-audit/check_cross_quotes.py 3
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/census.py --sura 3 --dup 0.030
python3 tools/quran-audit/check_translations.py --sura 3
```

At `7c85d9a`:

| Measure | Value |
|---|---|
| Verse sections | 200, one per verse, contiguous 1 → 200 |
| Body words (gate's own count) | 150,300 |
| Words per section | min 515 · **median 755** · max 1,481 |
| Sections below the 1,200–1,400 band | 190 (199 below before the §14 lists existed) |
| Sections above the band | 1 (3:1 at 1,481 words) |
| tics / 1,000 words | 0.05 (007: 0.19; ceiling 4.0) |
| chains / 1,000 words | 0.27 (007: 0.12; ceiling 1.5) |
| duplicate 10-gram fraction | 0.017 (007: 0.062; ceiling 0.10) |
| sentences of 12+ words repeated verbatim | 0 |
| quoted spans | 1,767 — 417 carrying a Qurʾānic citation, 1,350 uncited |
| **DRIFT / VICINITY / EXACT / NOVERSE / ELLIPSIS** | **393 / 20 / 4 / 0 / 0** |
| blockquotes byte-exact against `translation/003.txt` | **0 of 200** |
| blockquotes matching `initial/003.md` | 200 of 200 |
| `validate.py` | PASSED 114/114, FAILED 0 |
| `census.py` sections < 260 w / < 400 w | 0 / 0 |
| `census.py` sections at duprate ≥ 0.030 ('whole' span) | 0 |
| `check_translations.py --sura 3` flagged | 0 |

**Phase decision (§17).** Median 755 words is far below 1,200, but dup 0.017 is
under the 0.030 gate, chains 0.27/1k is under 1.5, no section reaches 5 chains
per 1,000 words, census reports zero flagged sections, and no blockquote matches
neither source. The table's last row decides: **Phase 2 — "prose clean but
median far below 1,200 words", expecting to author most of the band rather than
add to it.** No regeneration was warranted, so no section was rebuilt and no
retention figure applies (§19, pass 2).

What the audit *did* show is a defect 007 did not have at this stage: the whole
file is written in the `initial/` register, quotations included. That makes
passes 3, 5 and 6 larger here than they were on 007, and it is the reason the
run spent itself on sourcing before reaching depth.

---

## 3. Pass 1 — structural normalisation

`validate.py` already reported 114/114 at baseline, so `normalize.py` was **not**
needed as a repair (§1.7). It was run once, scoped to this chapter only, purely
to test idempotence:

```
python3 tools/quran-audit/normalize.py 3     -> files written: 0
diff /tmp/003_pre_norm.md expanded/003.md    -> byte-identical
```

- stray horizontal rules: **0**
- H2 inventory: `## Introduction to the Sūrah` + 200 verse headings, **0 others**
- malformed bold (`^****`): **0** · orphan connector lines: **0** · carriage
  returns: **0** · trailing newlines: exactly **1**

**§5.4 was applied even though `normalize.py` wrote nothing**, because §5.3
records that both defect classes it was designed to remove were introduced by
`normalize.py` itself while every gate stayed green.

**Tool hazard found (§23.4 class).** `normalize.py`'s `main()` filters
`sys.argv` with `if not a.startswith('--')`, so **any flag-only invocation is
read as "no chapters named" and rewrites all 113 editable files.** A
`normalize.py --help` in this session deleted 377 lines from `expanded/007.md`
before it was caught. `expanded/007.md` was restored with
`git checkout -- expanded/007.md` and re-verified in the same step:
`check_cross_quotes.py 7` → 2,125 spans / 1,780 EXACT / 345 UNCITED, and
`check_filler.py --sura 7` → 277,675 words / FAILING 0 / reduced-floor 18, both
exactly the benchmark figures. `last_fixlog.json` was removed as generated
output. **Never invoke `normalize.py` with flags only; always name the chapter.**

---

## 4. Pass 3 — translation re-sourcing (complete)

```
blockquotes byte-exact against translation/003.txt :   0 -> 200 of 200
blockquotes still matching initial/003.md          : 200 ->   0
file size                                          : 1,046,727 -> 1,023,185 bytes
```

Each section's `> **…**` line was replaced from `translation/003.txt` and the
commentary left untouched (§18.5: swap the line, never the section). Applied
highest-line-index-first so earlier offsets did not shift (§13.5). Verified
afterwards by re-parsing all 200 sections and comparing byte-for-byte.

`check_translations.py --sura 3` → checked 200 sections, flagged 0 both before
and after, so no section was carrying a wrong verse; this was a register
problem, not a substitution problem (§18.5 / group E).

---

## 5. Passes 4–6 — citation integrity and the quote register

### 5.1 Pass 4: verse numbers against chapter lengths (§22.1)

```
references scanned in expanded/003.md : 1,098 across 4,960 lines
verse number exceeding its sura length : 1
```

The single hit is `(Philippians 1:23)` at L3934 in section 3:158 — a New
Testament citation, not a Qurʾānic one. **Read and judged a detector false
positive (§21.2, group D); left unchanged.** It is prefixed by the book name
inside its own parenthesis and `check_cross_quotes.py` reports NOVERSE 0, so no
span is mis-resolved by it. Recorded here rather than "fixed".

No fabricated "in some counts" hedge of the §22.1 kind exists in this file.

### 5.2 Pass 4 / §21.4: drafting debris and unverified numbers

Nine patterns scanned over all 4,960 lines. Result after repair: **0 hits in
every class** — the system-memory-check ritual trailer of
`system_instructions.md` §6.4 (the string is deliberately not reproduced here:
§1.8 forbids it in any file), citation-hunting
(`we need a source for` / `verify before` / TBD / TODO / FIXME / XXX), planning
artifacts, narrator guess-chains, digit-followed-by-`?`, U+FFFD, undefined
letter codes `(Q)/(JJ)/(Z)/(IK)/(R)`, camel-case corruption, stray `$`.

Five genuine hits were found and fixed:

| Site | Class (§21.4) | Repair |
|---|---|---|
| L54 `unmatcHed` | corrupted token | → `unmatched` |
| L4012 `al-Bukhārī 3107?` | unverified number in the deliverable | one search; unresolved → number dropped. The same parenthesis already carried al-Bukhārī 6939, 3079, 6979 and Muslim 1830–1832, which stand |
| L4442 `al-Bukhārī 1333?` | unverified number | one search confirmed the report (the Prophet's funeral prayer over ʿAbdullāh b. Ubayy, Ibn ʿUmar and ʿUmar, on 9:84) but not the number → collection and book named instead of a number |
| L4488 `the heir of 4:53? No — the specific report:` | narrator guess-chain, the exact `083.md` class | guess-chain deleted; the report is stated as transmitted through Ibn Kathīr's tafsīr on 3:181 |
| L4589 `Muslim 1881?` | unverified number | one search; wording confirmed at **al-Bukhārī 2796** (Anas, Book of Jihād, verified live) and that citation added; the unverified Muslim number dropped |

§6 was applied literally: a number is carried only if verified, and where one
search does not verify it the report is attributed to a named exegete or carried
by collection-and-book. **No number was invented and none was harmonised to a
plurality (§22.3).**

### 5.3 Pass 4 / §22.4: a count claim measured before it was written

`expanded/003.md` §3:136 asserted the river phrase occurs "over forty times,
from 2:25 onward". Measured against `translation/`:

```
"rivers flow" in translation/ : 37 occurrences across 25 chapters
earliest                     : 2:25
```

The claim was **wrong** and is corrected in the file to *thirty-seven
occurrences, beginning at 2:25*. This is the §22.4 class — a count stated from
memory — and §7:103's "roughly one hundred and thirty times" is the recorded
precedent.

### 5.4 Pass 5: the drifted quotations

393 spans were DRIFT because the whole commentary quotes scripture in the
`initial/` register. A span is only repairable automatically when the alignment
between the two renderings is unambiguous, so each candidate was scored on six
independent conditions and **every accepted proposal was read before it was
written**:

1. both the quote's first and last *content* word anchored in the verse;
2. forward coverage — matched share of the quote's content words ≥ 0.60;
3. reverse coverage — matched share of the span's content words ≥ 0.62, which is
   what stops the span over-running into verse the quotation never covered;
4. growth (span words ÷ quote words) ≤ 1.60;
5. no nested quote characters, and no span ending on a comma, semicolon, colon
   or dash or starting on a dangling connective;
6. not a schematic placeholder — one candidate read `God does not guide X,`
   where `X` is the author's own variable, and rewriting it would have destroyed
   the device.

The aligner is Needleman–Wunsch over loose word keys with a register-variant
synonymy (`allah↔god`, `torment↔punishment`, `criterion↔standard`,
`humankind↔mankind`, …). difflib's exact-block LCS was tried first and rejected:
it drops every substituted word, so `your wealth and your children are but a
trial` aligned to `your wealth and your children are only a` and lost `test`.

```
49 spans re-worded to verbatim translation/ spans, all read individually
6 further candidates REJECTED on reading although the filter passed them:
    "as they knew their sons"        -> "they are not all alike: there are some"
    "let not grieve you those ..."   -> "not grieve for those ... —surely"
    "nor would he command you ..."   -> drops the connective "nor"
    "why do you disbelieve?"         -> "Why do you deny"  (loses the object)
    "God wrongs them not ..."        -> "...but they wronged" (truncated)
    "had we known ... fighting"      -> duplicate of a fuller span in 3:167
```

### 5.5 Pass 5: the zero-hedge rule (§6)

22 spans were VICINITY. Every one was an own-verse gloss in the `initial/`
register whose *nearest* parenthesis was a `cf.` cross-reference list — the
§6.4 "nearest citation wins" hazard. Each was repaired by re-wording the
quotation to `translation/` **and** giving it its own `(S:V)` immediately after
the closing quote, so the hedge parenthesis is no longer the nearest one. Two
that were paraphrase rather than scripture had the quotation marks removed
instead, since §6 forbids paraphrase inside them:

- 3:95 — `Joseph's *"this is what my Lord made true; He has spoken truth"* (the
  sense of 6:151 and 18:98…)` was not scripture at all. Measured: 6:151 does not
  carry the claim, 18:98 does. Rewritten around the verbatim span
  `"promise is ever true" (18:98)`.
- 3:175 — one quote carried `...` inside it. §6.2 forbids ellipsis in a
  quotation absolutely; it is now a single contiguous span.

```
VICINITY : 20 -> 0
```

### 5.6 Pass 6: own-verse alignment

`align_own_verse.py report 3` proposes **515 candidates**. §12.4 says the tool
proposes and does not apply, and that every candidate is reviewed. Read as a
set, its difflib covering spans are **not safe to install wholesale**:

| Candidate | Proposal |
|---|---|
| `and He sent down the Criterion` (3:4) | `and` |
| `Truly naught is hidden from God on earth or in Heaven` (3:5) | `on earth or in` |
| `Confirming What Was Before It` | matched **inside a bold mini-heading**, `**"In Truth, Confirming What Was Before It"**` — a heading is never a quotation |

The candidates were therefore re-derived with the pass-5 aligner and filter,
heading lines excluded, and 1,829 own-verse spans were examined:

```
own-verse spans examined : 1,829
accepted                 :    51 rewordings, 44 also given a (3:V) citation
rejected                 : 1,778   (580 no alignment; the rest on the six
                                   conditions above)
```

Three consequences were handled rather than left:

- **Duplicate citations suppressed.** Where two spans in one section resolve to
  the same or a containing span, only the first is cited (§6: never quote one
  span twice in a section).
- **Terminal punctuation preserved inside the quote.** Where the old span ended
  `?` and the verbatim replacement does not, the mark is kept inside the closing
  quote. `norm()` strips punctuation, so the gate still sees a verbatim span, and
  the sentence keeps its question.
- **Citation adjacency creates new DRIFT.** Inserting `(3:V)` makes that
  parenthesis the nearest one for any *earlier* quote on the same line (§6.4),
  which turned eight previously-uncited archaic glosses into freshly-cited
  DRIFT. Six were re-worded with their own citation. Two were not scripture and
  were de-quoted: an Arabic transliteration sitting in quotation marks beside a
  verse reference, and a ḥadīth whose parenthesis carried a bare `3:190` that the
  gate read as a Qurʾānic citation because **"Musnad Aḥmad" is not in
  `check_cross_quotes.py`'s HADITH name list** — a detector gap worth closing
  (§12 of the corrections list).

### 5.7 Measured result of passes 4–6

```
python3 tools/quran-audit/check_cross_quotes.py 3
                     baseline 7c85d9a -> HEAD
  quoted spans              1,767 -> 1,763
  with a Qur'anic citation    417 ->   457
  DRIFT                       393 ->   331
  VICINITY                     20 ->     0
  EXACT                         4 ->   126
  NOVERSE                       0 ->     0
  ELLIPSIS                      0 ->     0
  UNCITED                   1,350 -> 1,306
```

---

## 6. Pass 7 — duplication clearing

Nothing to clear. `census.py --sura 3 --dup 0.030` reports **0 sections at or
above the gate on the 'whole' span**, before and after every other pass. The
§18.1 diagnostic was run first, as §18.1 requires: with duprate 0.017 and zero
flagged sections there is neither sentential degeneration nor structural
recapitulation, so neither §18.2 nor §18.3 was applied and **no prose was
deleted anywhere in this run**.

One movement is worth recording because §21.5 predicts it exactly:

```
check_filler.py duplicate 10-gram fraction : 0.017 -> 0.028
```

Re-sourcing the blockquotes and re-wording the own-verse glosses necessarily puts
the verse's own wording into the body, which is the §18.4 mechanism. It remains
under the 0.030 census gate and well under `check_filler.py`'s 0.10 `--max-dup`,
and `census.py` still reports zero flagged sections. §21.5's eight 036.md
sections tripped the gate for this reason alone; chapter 3 does not.

The §11.2 recap scan, run with §18.3's own constants (`NGRAM_OVL = 5`,
`OVERLAP_MIN = 0.30`) over mini-heading blocks:

```
sections examined : 200     (examined: 0 is a failure, per 3.3)
recap candidates  :   0
```

---

## 7. §14 — `check_filler.py` configured for chapter 3

Keys in this gate are already chapter-qualified (`'7:143'`), so chapter 3's
entries were added alongside 007's and 007's sets were not touched.
`TIER1_FLOOR 1400`, `TIER1_CEILING 1800`, `DEEPEST_CEILING 2100` and
`REDUCED_FLOOR 700` are unchanged, and `depth_floor` / `depth_ceiling` are
unchanged.

**Verified after the edit, as §14 requires:**

```
check_filler.py --sura 7 --band 1200-1400
  007.md  206 sections  277675 words  min 824 / med 1370 / max 2100
  below 0  above 0  reduced-floor 18  tics 0.19/1k  chains 0.12/1k
  dup 0.062  repeated sentences 0  FAILING 0
check_cross_quotes.py 7
  2125 spans  EXACT 1780  UNCITED 345
```

Both are byte-for-byte the benchmark figures in the prompt. The `reduced-floor`
counter still reports 18 for 007, so the "raising a floor must not inflate it"
bug was not reintroduced.

### 7.1 DEEPEST (5) — the chapter's theological and legal cruxes

| Verse | Why it is deepest |
|---|---|
| **3:7** | *muḥkam* and *mutashābih*, and the *waqf* on *illā Allāh*. The hermeneutical crux of the whole corpus; al-Ṭabarī, al-Rāzī, Ibn Kathīr and al-Qurṭubī divide on whether the well-grounded in knowledge share the meaning |
| **3:18** | The tawḥīd verse: Allāh Himself, the angels and the people of knowledge bear witness; *al-Qāʾim bi-l-qisṭ* |
| **3:59** | The likeness of Jesus is the likeness of Adam — the Christological crux of the Madinan debate with Najrān |
| **3:64** | The common word — the covenant formula addressed to the People of the Book, repeated across the corpus and therefore countable |
| **3:97** | The first House and the obligation of pilgrimage, with its condition (*man istaṭāʿa ilayhi sabīlā*) and the schools' positions on it |

### 7.2 TIER1 (46 of 200 = 23%, inside §8's 15–25%)

DEEPEST plus: 3:19, 3:27, 3:31, 3:35, 3:42, 3:45, 3:49, 3:50, 3:55, 3:61, 3:67,
3:75, 3:77, 3:81, 3:85, 3:92, 3:93, 3:96, 3:102, 3:103, 3:104, 3:110, 3:130,
3:134, 3:139, 3:144, 3:145, 3:152, 3:159, 3:161, 3:169, 3:179, 3:180, 3:181,
3:185, 3:187, 3:190, 3:191, 3:195, 3:199, 3:200.

Selected on §8's criteria: the legal rulings (usury 3:130, pilgrimage 3:96–97,
the commanding group 3:104, *ghulūl* 3:161, the spending of what one loves
3:92, the food law 3:93); the divine attributes and acts stated doctrinally
(3:18, 3:26–27, 3:150, 3:179–181); the covenants and eschatological scenes
(3:64, 3:77, 3:81, 3:169, 3:185); the named prophetic episodes with narrative
consequences (the house of ʿImrān 3:33–51, Najrān 3:59–63, Uḥud 3:121–175); the
countable repeated formulae (the river phrase at 3:136, "every soul will taste
death" at 3:185, the no-fear/no-grief seal at 3:170); and the disputed terms
(3:7, 3:55, 3:67).

**§9's warning is recorded here so it is not repeated.** On 007 the Tier-1 list
was wrong about half the time — 22 of 46 listed sections were already saturated.
This list has **not** been through §9's per-verse deduplication test, because
that test is run immediately before drafting each verse and no verse of chapter 3
has been drafted yet. Every one of these 46 must be re-tested at the moment it is
drafted, and demotions logged with their reasons.

### 7.3 SHORT_VERSE (10, reduced floor 700) — each with its written reason

Fifteen verses of chapter 3 are fourteen words or fewer in
`translation/003.txt`. Qualification is conjunctive (§4), so ten were admitted
and **five were refused**:

| Admitted | Reason |
|---|---|
| 3:1 (1w) | muqattaʿāt: *Alif-Lām-Mīm* |
| 3:34 (11w) | scene-closer: the chosen lines are descendants of one another |
| 3:48 (13w) | single clause within the annunciation speech begun at 3:45 |
| 3:63 (13w) | scene-closer to the Jesus narrative: if they turn away |
| 3:82 (10w) | scene-closer to the covenant of the prophets: whoever turns back |
| 3:94 (13w) | scene-closer to the challenge over the food law |
| 3:131 (9w) | scene-closer to the usury prohibition: guard yourselves |
| 3:138 (14w) | scene-closer to vv. 136–137: this is an insight to humanity |
| 3:141 (9w) | continuation clause of 3:140, begins on "and" |
| 3:150 (12w) | scene-closer to 3:149: Allāh is your Guardian |

| Refused — stays in the full band | Why |
|---|---|
| 3:2 (13w) | *al-Ḥayy al-Qayyūm*: a doctrinal declaration, not a fragment |
| 3:5 (12w) | divine omniscience stated as a complete proposition |
| 3:132 (11w) | obedience to the Messenger — real scholarship to fill it with |
| 3:158 (13w) | death, martyrdom and the gathering: eschatological, complete |
| 3:196 (13w) | the prosperity of the disbelievers: a complete prohibition |

`check_filler.py --sura 3` now reports **reduced-floor 10** and, with the Tier-1
floors in place, **below 190 / above 0**.

---

## 8. §12.3 — the three manual checks

All three were run as throwaway inline scripts, not committed, and all three
print how many sections they examined (§3.3: `examined: 0` is a failure).

| Check | Examined | Result |
|---|---|---|
| Echo test (§3.3) | **199** sections | **1 below 15%** — 3:76 at 12.5% |
| Recap scan (§11.2) | **200** sections | **0 candidates** |
| Scaffolding scan (§11.3) | **4,960** lines | **0 genuine hits** after the five repairs of §5.2 |

The echo test skips sections with fewer than three distinctive tokens or no prose
body; 199 of 200 were examined, and the one skipped is 3:1, whose blockquote is
the single word *Alif-Lãm-Mĩm*.

**3:76 is a detector artifact (§21.2, group D) and was not "fixed".** Read
against its own verse, the section is unmistakably about 3:76: it opens on *balā*
and works through *man awfā bi-ʿahdihi wa-ttaqā*. It scores 12.5% because the
detector is lemma-blind and cannot see that the body's *Yea!*, *God*, *reverent*,
*pact* and *fulfills* are the same things as the translation's *Absolutely!*,
*Allah*, *mindful*, *trusts* and *honour*. That is the `067.md` v10 and `026.md`
v176 class precisely. **The four recorded detector bugs were not repeated:** no
stemming patch was tried, and mini-heading lines were excluded from the body
exactly as §3.3 specifies (non-blockquote, non-heading prose).

What the flag *does* point at is real and is logged rather than patched: the
divergence is one of **vocabulary**, and §3.2 requires the commentary's own
English to use the translation's words. In this file that divergence is
systematic — the whole commentary was authored in the `initial/` register — so it
is a property of pass 8's drafting work, not of 3:76. It is item 3 of the
outstanding work in §9.

---

## 9. What is outstanding, and the measured size of it

Recorded as genuine future work, which §"no deferral" permits for work not done;
it is stated here because it is **not** done and must not be read as done.

### 9.1 Pass 8 — depth (the dominant gap)

```
python3 tools/quran-audit/check_filler.py --sura 3 --band 1200-1400
  200 sections   150,438 words   min 515 / med 756 / max 1481
  below 190   above 0   reduced-floor 10   FAILING 190
```

007's comparable figures are 206 sections, 277,675 words, min 824 / med 1,370 /
max 2,100, below 0, FAILING 0. To reach the band, chapter 3 needs roughly
**110,000 additional body words** — 190 sections lifted by a mean of about 580
words each, 46 of them to a 1,400-word Tier-1 floor and 5 to as much as 2,100 —
authored to §7's content list (Arabic root and morphology, quoted
cross-references at 007's density of 14.5 citations per section against this
chapter's present 2.3, verified ḥadīth, named exegetes with their positions
counted, *asbāb al-nuzūl* with chains, *ʿaqīdah*, *fiqh* with the schools,
practical implication, and the reason the command makes sense), at 007's internal
shape of 8–10 mini-headings, ~160 words under each and ~80 per paragraph.

That is authoring, not editing: §4 forbids reaching the number by restatement,
recap or summary, and §15 forbids padding a saturated section. It was not
attempted in this run. **The correct answer where the source is thin is a
documented lower floor (§21.5, 036.md's deliberate median of 516), not invented
scholarship** — but `initial/003.md` is not thin: it carries 257,419 bytes of
apparatus for 200 verses, so 036.md's precedent does not apply here and the band
is the target.

### 9.2 Passes 5–6 residual — 331 drifted spans

The remaining DRIFT population is not mechanically repairable, and the reason is
measured rather than assumed. Under the aligner's six conditions the pass
accepted 51 spans and withheld the rest; the dominant causes are 579 spans with
no usable alignment at all and 325 failing forward *and* reverse coverage
together, which is what genuine vocabulary divergence looks like —
`Criterion`/`Standard`, `glad tidings`/`good news`, `reverence`/`mindfulness`.
Each needs a person to read the carrying sentence,
choose the verbatim span, and restructure the sentence around it so the lowercase
or bracketed opening still reads (§6). §22.2 says this explicitly: *"Read them;
do not 'fix' them."*

Three sub-populations inside it, each with its own treatment:

| Sub-population | Count at HEAD | Treatment |
|---|---|---|
| Spans with `…` or `...` inside the quotation | 58 own-verse, plus cross-verse spans inside the 331 | §6.2 forbids ellipsis absolutely: split into two quotations each with its own citation, or quote one contiguous span |
| Spans whose target carries inner curly quotes | 58 own-verse | §6: quote only contiguous **inner** spans; the verse's own `“…”` cannot be nested inside an existing quotation |
| Spans with no usable alignment at all | 579 own-verse | Not quotations of the own verse — cross-sūrah references, ḥadīth, and Arabic glosses. No treatment; they are correctly uncited or cited elsewhere |
| Spans failing the edge, coverage or tail conditions together | 325 own-verse | Genuine vocabulary divergence; read the carrying sentence and choose the span by hand |

Measured by re-running the pass-6 applier against the finished tree, which also
proves it **idempotent** — `accepted for rewrite: 0`, and `already-exact` rose
from 40 to 98, confirming the 51 rewrites landed and are now verbatim:

```
noalign 579 · edges/conf/cov/rcov 325 · tailstop 225 · edgepunct 140
already-exact 98 · ellipsis 58 · nestedquote 58 · growth 27
```

### 9.3 §3.2 — the commentary's own vocabulary

The file's prose uses `initial/`'s words throughout: *God* for *Allah*,
*criterion* for *Standard*, *reverence* for *mindfulness*, *hosts* for
*armies*, *seizure* for *grip*. §3.2 requires the translation's own English word
everywhere the translation names a thing, in headings, glosses and analysis. This
is a whole-file editorial pass coupled to 9.1 — it should be done verse by verse
as each section is drafted to the band, not as a separate sweep, because a
vocabulary change and a depth change to the same section are one edit.

### 9.4 Citation density

007 carries 2,990 `(S:V)` citations in body prose, 14.5 per section, and 205 of
206 sections have at least one. Chapter 3 carries 457 cited spans across 200
sections — **2.3 per section**. §7 treats fewer than about five as under-sourced.
Cross-references must be added *with their quoted text from `translation/`*,
never as bare pointers, which makes this part of pass 8 rather than separate
from it.

---

## 10. Corrections — every error found in this plan and in this run

Numbered, per §24.3, because this list is what stops the next session repeating
the mistakes. Items 1–4 are errors in the **tooling and the source file**; items
5–9 are errors in **this run's own method**, caught before they were written.

1. **`normalize.py` rewrites the whole corpus when invoked with flags only.**
   `main()` strips every argument beginning `--`, so `normalize.py --help` is
   read as "no chapters named" and runs 2–114. It deleted 377 lines from
   `expanded/007.md` in this session. Caught by `git status` in the same step,
   restored by `git checkout -- expanded/007.md`, and re-verified against both
   benchmark figures before any further work. `last_fixlog.json` deleted as
   generated output. **This is a live hazard for the next session, not a
   historical note.**

2. **`check_cross_quotes.py`'s HADITH name list omits `Musnad Aḥmad`.** The list
   is `al-Bukhārī|Bukhari|Muslim|al-Tirmidhī|Tirmidhi|Abū Dāwūd|al-Dārimī|Ibn
   Mājah|al-Nasāʾī|Luke|Matthew|John \d`. A ḥadīth attributed to Musnad Aḥmad
   whose parenthesis also mentioned a verse was therefore checked *as a Qurʾānic
   quotation* against that verse and reported DRIFT. Found at 3:190. The file was
   repaired by removing the bare verse number from that parenthesis; **the gate
   still has the gap** and will repeat it for any Musnad Aḥmad, Muwaṭṭaʾ Mālik,
   Ṣaḥīḥ Ibn Ḥibbān or Sunan al-Dāraquṭnī citation. Adding those names is a
   one-line change to a surviving gate and belongs in a separate, reviewed edit.

3. **`expanded/003.md` asserted a count from memory and the count was wrong.**
   "over forty occurrences, from 2:25 onward" for the river phrase. Measured
   against `translation/`: **37 occurrences across 25 chapters**, earliest 2:25.
   Corrected in the file. §22.4's rule — any claim of the form "N times" is
   measured before it is written — applies to every count in this document too,
   which is why each carries its command.

4. **Four unverified ḥadīth numbers were sitting in the deliverable marked with
   a literal `?`**, plus a full narrator guess-chain (`the heir of 4:53? No — the
   specific report:`) of exactly the `083.md` class, where all three guesses in
   that precedent were wrong. None was left pending (§15): one search each, then
   the number dropped or replaced by collection-and-book, and the guess-chain
   deleted. One number *was* verified live and added — al-Bukhārī 2796 for the
   whip-width of Paradise.

5. **difflib is the wrong aligner for register-shifted translations, and this run
   started with it.** Its exact-block LCS drops every substituted word, so
   `your wealth and your children are but a trial` aligned to
   `your wealth and your children are only a` — verbatim, contiguous, and missing
   the one word that mattered. Replaced by Needleman–Wunsch with substitution
   scoring. **Do not reuse `align_own_verse.py`'s difflib proposals without this.**

6. **`align_own_verse.py` matches inside bold mini-headings.** One candidate was
   `Confirming What Was Before It` → `in truth, confirming what came before it`,
   taken from `**"In Truth, Confirming What Was Before It"**`. Installing it
   would have destroyed a heading. Any own-verse pass must exclude lines matching
   `^\*{2,3}[^*].*\*\*$` before it looks at quotations.

7. **The first acceptance filter was too loose and the second too strict, and
   both were wrong in instructive ways.** With both word-edges anchored at
   position 0 and *n−1*, only 6 spans passed. With content-word edges only, 10
   passed and **6 of the 10 were bad** — each had dropped a content word at an
   edge and truncated the sense (`"Whosoever obeys the Messenger has obeyed God"`
   → `"obeys the Messenger has truly obeyed Allah"`). The setting that survived
   review anchors the first and last *content* word, adds reverse coverage to
   catch over-run, and rejects spans ending on a comma or starting on a dangling
   connective. Reverse coverage was the single most valuable addition: without it
   a three-word quote could pull a forty-word span.

8. **Adding a citation creates new failures elsewhere on the same line.** This was
   not anticipated. Inserting `(3:V)` after an own-verse quotation made that
   parenthesis the *nearest* one for an earlier quotation on the line (§6.4),
   converting eight uncited spans into cited DRIFT and moving the DRIFT count
   **up** by three on a pass that was supposed to reduce it. Caught only because
   the gate was re-run after the pass rather than assumed. **Any citation-insertion
   pass must be followed by a full gate re-run and a diff of the DRIFT set, not a
   count.**

9. **A word count taken with the wrong counter.** A first delta was computed with
   an ad-hoc `[\wʹʼʿʾ’'-]+` count over non-blockquote lines and gave 151,957 →
   152,095. The gate's own count over the same two trees gives **150,300 →
   150,438**. §24.5 requires the gate's own count; the ad-hoc figure is withdrawn
   and is not quoted anywhere in this document as a result. The two differ by
   ~1,650 words because the gate also excludes heading lines. **State which
   counter produced a number (§23.2).**

10. **`expanded/003.md` describes 3:151 as "3:151's sister text" while quoting
    3:151 itself.** The section *is* 3:151. Corrected to "in this very verse"
    when the quotation was re-sourced. This is the §21.1 group C class in
    miniature — a body misdescribing its own heading — and it was found only by
    reading the carrying sentence, which is the point §21.1 makes about group C:
    **no tool finds it.**

---

## 11. Working notes for the next session

- The baseline for any further before/after figure is now `c124b2f`, not
  `7c85d9a`. Both are in this repository's history, so either can be
  re-measured with `git show <sha>:expanded/003.md` (§23.4: never assume a
  `/tmp` copy survives).
- Draft in batches of 8–12 verses (§13), running §9's deduplication test
  **immediately before each verse**, never in bulk and never from the Tier-1 list
  in §7.2 above. Expect to demote roughly half of that list, as 007 did.
- Do §3.2's vocabulary pass **inside** each batch, not separately (§9.3).
- After any batch: all four gates, then the three §12.3 checks, then commit with
  the word counts before and after in the message (§13.7).
- Keep every scratch script in `/tmp`. The four used here —
  `pass3_blockquotes.py`, `requote2.py`, `pass6_own.py`, `pass6b.py` — are
  single-use instruments whose rules are now written down in §5 of this document,
  which is the principle §16 states for the 133 scripts that were deleted. None is
  committed.
- `expanded/003.md` must never be edited by a script that has already been
  applied (§13.5): every applier here is insert-by-offset and re-running one
  duplicates its work.
