# Depth Plan — expanded/001.md (Sūrat al-Fātiḥah)

Written by the standardisation run of `STANDARDIZATION_PROMPT.md` with `{{N}}=1`, `{{NNN}}=001`.
Everything measured below was measured in the step that wrote it, from the repository, with the
gates' own counters — not recalled. Where a figure came from memory it is marked and corrected in
§9, which is the erratum list the next session should read first.

Baseline commit for all before/after figures: `88eea9a` (tip of `main` at branch creation).

---

## 1. Scope, and a collision in the prompt that had to be resolved

The prompt's Mission is to bring `expanded/001.md` to the standard of `expanded/007.md`. Its hard
constraint §1.2 says **"Never modify `expanded/001.md` (the confirmed structural reference) … They
are inputs, not deliverables."** With `{{N}}=1` the deliverable and the protected reference are the
same file. The two clauses cannot both be satisfied.

Resolved in favour of the Mission, on these grounds, and logged rather than silently applied:

1. §1.2's protection exists to stop collateral damage to a reference input while the session works
   on a *different* chapter. §2.2 asks the session to read `expanded/001.md` as "the canonical
   skeleton", which is a use, not an edit. For `{{N}}=1` there is no other chapter in scope.
2. §15's definition of done is stated for chapter `{{N}}` and is unreachable without editing
   `expanded/001.md`: at the baseline commit the file carried **61 DRIFT** and **4 VICINITY**
   quotations, and six of its seven own-verse blockquotes were **not** verbatim from
   `translation/001.txt`. §11 requires all of those at zero.
3. §12's tie-break — "Anything else ambiguous: choose the option that adds sourced scholarship and
   needs no user input, then move on" — and its stronger rule "A plan, summary or memory conflicts
   with `translation/`: `translation/` wins, always" both point the same way.

The edit was kept as narrow as the definition of done allows. **No commentary was cut, deleted,
reordered or summarised.** Three kinds of change were made, and only these:

- quoted Qurʾānic wording and its citation form, brought onto `translation/` (§4, §12);
- the seven own-verse blockquotes, brought onto `translation/001.txt` (§3, §15);
- two defects of text integrity repaired (§9.10, §9.11), and four style-gate items removed (§9.12).

`expanded/002.md`–`expanded/114.md`, `translation/*.txt` and `initial/*.txt` were not touched.
`normalize.py` was not run: `validate.py` reported no structural failure at any point (§1.7).

---

## 2. Method actually used

`expanded/001.md` was already at 11,508 body words across 7 sections at the baseline commit — a
median of 1,634 and a range of 1,453–2,040. **No section was below any floor.** The chapter's
deficit was not depth; it was quotation exactness. That inverted the usual shape of the run: there
was nothing to draft, and §10's insertion script (keyed by verse, inserted before the closing
`---`, applied highest-offset-first) was the wrong instrument. It was replaced by an anchored
find-and-replace script per batch, which is the correct instrument for in-place correction:

- every replacement is a `(old, new)` pair whose `old` must occur **exactly once** in the file;
- the script refuses to write at all if any anchor is non-unique, so a partial apply is impossible;
- it prints a dry-run projection of before/after body words, counted with `check_filler`'s own
  `WORDS` regex on non-`>` lines, before it will accept `--apply`;
- it was never re-run after an apply. The three post-apply fixes (§9.6, §9.10, §9.12) went directly
  into the file.

Scripts were written to `/tmp/q1/` by heredoc (`batch1.py`, `batch2.py`, `batch3.py`) and are not
tracked; the gate output they produce is reproducible.

Reading order followed §2: `system_instructions.md`, the head and tail of `expanded/001.md`, four
sections of `expanded/007.md` (introduction, 7:143 as the long doctrinal model, 7:1 as the
`SHORT_VERSE` fragment model), all of `translation/001.txt` in one read, `initial/001.md` skimmed
as background and quoted from nowhere, `DEPTH_PLAN_007.md` §10.3 and §10.5–§10.15 for the
corrections record, and the seven script docstrings.

The batches were smaller than §10's 8–12 verses because the chapter has seven:

| Batch | Sections | Anchors | Unique | Result |
|---|---|---|---|---|
| 1 | Introduction, 1:1, 1:2, 1:3 | 25 | 25 | DRIFT 61 → 46, EXACT 1 → 21 |
| 2 | 1:4, 1:5 | 23 | 23 | DRIFT 46 → 32, EXACT 21 → 38 |
| 3 | 1:6, 1:7 | 25 | 25 | DRIFT 32 → 1, VICINITY 2 → 0, EXACT 38 → 76 |
| 4 | 1:3 repair + style | 4 | 4 | DRIFT 1 → 0, tics 2 → 0, chains 2 → 0 |

---

## 3. What was actually wrong: the four defect classes

Reading the 61 DRIFT reports against `translation/` showed one root cause and three consequences.

**Root cause — the commentary was drafted against a different English translation.** Every drifting
span is a faithful rendering of the Arabic from another English version, not a sloppy quotation:
`"Blessed is He who sent down the Criterion upon His servant"` (25:1) where `translation/` reads
*"Blessed is the One Who sent down the Standard to His servant"*; `"God does not wrong people at
all"` (10:44) where `translation/` reads *"Allah does not wrong people in the least"*; `"Did He not
find you astray and guide you?"* (93:7) where `translation/` reads *"Did He not find you unguided
then guided you?"*. The file's own-verse blockquotes confirmed it: six of the seven matched
`initial/001.md`'s archaic rendering ("Thee we worship", "Thou hast blessed") modernised, and only
1:4 matched `translation/001.txt`. `check_translations.py` did not flag any of them, because it
accepts a match against **either** source above 0.45 — a register variant against `initial/` is
indistinguishable from a correct quotation as far as that gate is concerned.

**Consequence 1 — eight citations pointed at verses that do not contain the claim.** These are the
dangerous ones, because a correct-looking span hides a wrong reference. All eight were re-pointed
by reading the verse in `translation/`, never by guessing a neighbour:

| Was cited | Claim | Where the wording actually is |
|---|---|---|
| 25:67 | "Do not exaggerate in your religion" | 4:171, *"Do not go to extremes regarding your faith"* |
| 11:56 | "my Lord is on a straight path" | 11:56, *"Surely my Lord's Way is perfect justice"* |
| 26:20 | "and I was among the astray" | 26:20, *"I did it then, lacking guidance"* |
| 90:10 | "We have shown him the two ways" | 90:10, *"and shown them the two ways"* — second person, not first |
| 83:10–12 | "Then for those who disbelieved in the Day of Judgment" | 83:10–11, *"Woe on that Day to the deniers— those who deny Judgment Day!"* |
| 2:61 | "wrath upon wrath" | 2:90, *"They have earned wrath upon wrath"* — 2:61 carries the disgrace and misery, not the wrath |
| 39:53 | "transgressed against themselves … do not despair" | 39:53, *"who have exceeded the limits against their souls! Do not lose hope"* |
| 4:69 | "the witnesses (al-shuhadāʾ)" | 4:69, *"the martyrs"* — the Arabic term moved outside the quote as a gloss |

**Consequence 2 — one ellipsis inside a Qurʾānic quotation** (2:177, `"righteousness is... to
believe in God and the Last Day"`), forbidden outright by §4. Replaced by the contiguous span
*"the righteous are those who believe in Allah, the Last Day"* (2:177).

**Consequence 3 — four VICINITY failures**, all from `cf.` inside a citation parenthesis:
`(Qur'an 43:87; cf. 29:61, 63; 31:25; 39:38)`, `(cf. 83:10–12)`, `(Qur'an 47:17; cf. 19:76)`,
`(2:61; cf. 2:90; 3:112; 5:60)`. The gate reads a hedged parenthesis as a declaration that the
quote is not verbatim. Each was split: the quoted verse gets a bare `(S:V)` immediately after the
closing quote mark, and the parallel verses are either named in prose with no parenthesis or quoted
in their own right with their own parenthesis. 19:76 and 2:90 were promoted from hedges to real
quotations, because both say exactly what the sentence needed; 29:61, 29:63, 31:25, 39:38 and
3:112, 5:60 are named in prose.

---

## 4. Two typographic rules adopted, and why

**(a) Qurʾānic quotations now use curly double quotes.** `check_cross_quotes.py` detects an
ascii-double span with `"([^"“”‘’]{12,700})"`, whose content class excludes the curly apostrophe.
`translation/` is full of them — *Allah's mercy*, *atom's weight*, *my Lord's Way* — so an
ascii-quoted span containing one is not detected at all, and silently leaves the gate's field of
view. That is worse than a DRIFT: it is an unchecked quotation. The curly-double class
`“([^“”]{12,700})”` admits apostrophes, brackets and dashes, which is why `expanded/007.md` uses
it. All 76 cited spans in the chapter now use it, matching the gold standard.

**(b) Nested double quotation marks inside a quoted span are levelled to singles.** Five verses
embed a quotation of their own — 43:87 (*“Allah!”*), 40:16 (*“Who does all authority belong to this
Day?”*), 10:10 and 39:75 (*“All praise is for Allah—Lord of all worlds!”*), 27:30 (*‘In the Name of
Allah…*). A curly-double span cannot contain a curly double, so either the span is shortened and
loses the words the argument needs, or the inner marks are levelled — `‘Allah!’` inside
`“…they will certainly say, ‘Allah!’”`. Levelling is ordinary English typographic practice for
nesting, and the gate compares **words**: `norm()` strips quote characters, editorial brackets and
dashes before the substring test, so wording and the `˹ ˺` brackets stay byte-exact. Rule (b) was
used five times; where a sub-span without inner quotes served the argument just as well — 19:65,
17:110, 39:53, 26:20, 25:60, 8:9, 5:77 — the sub-span was preferred and no levelling was done.

**Editorial brackets were reproduced exactly in every span** — `˹O Prophet˺`, `˹alone˺`,
`˹of right and wrong˺`, `˹with good deeds˺`, `˹to Paradise˺`, `˹you˺`, `˹in His attributes˺`,
`˹indeed˺`, `˹most˺`, `˹even˺`, `˹their˺`, `˹rightly˺`, `˹believers˺`, `˹all˺`, `˹necessary˺`,
`˹for the journey˺`, `˹He will ask,˺`, `˹simply˺`, `˹before you˺` — because §4 makes a dropped
bracket a failure.

**Capitalisation was left as the translation has it**, per §4. Two spans open lowercase — *"and
shown them the two ways ˹of right and wrong˺?"* (90:10) and *"when you cried out to your Lord for
help, He answered"* (8:9) — and the lead-in sentences were arranged so a lowercase opening reads
correctly ("which God has already given universally:", "had shown the pattern answered directly:").

---

## 5. Tier-1 list as chosen, and the §7 dedup test result

Chosen: **all seven verses are Tier-1**; **1:1, 1:5 and 1:7 are deepest**. No section was demoted,
because none needed demoting — §12's demotion rule fires only for a section that is saturated *and
below 1,400 words*, and the lowest section in the chapter was already at 1,453.

The 15–25% heuristic of §6 is calibrated on a 206-verse chapter, where it selects 31–52 verses. On
seven verses it selects one or two, and applying it literally would leave five sections that were
already drafted above the standard band failing `check_filler.py`'s ceiling with no permissible
remedy: §5 says sections above the band are left alone and that "the ceiling exists to stop padding,
not to force cuts", and §1.3 forbids cutting existing commentary. The governing rule is therefore
§5's, and the Tier-1 marker test was applied verse by verse to the text as read from
`translation/001.txt`, not to a summary of it:

| Verse | Words in `translation/` | Body words before → after | Heads | Tier-1 marker on the verse text |
|---|---|---|---|---|
| 1:1 | 10 | 1,725 → 1,776 | 6 | three divine names stated doctrinally; a repeated formula (§6); a term disputed with identifiable positions — the basmalah's verse-status |
| 1:2 | 9 | 1,453 → 1,453 | 6 | divine attribute and act (*rubūbiyyah*); the ḥamd closing formula repeated at 10:10, 39:75, 37:182 |
| 1:3 | 5 | 1,517 → 1,557 | 6 | two divine names; a distinction the tradition disputes with named positions |
| 1:4 | 6 | 1,480 → 1,485 | 6 | divine attribute in two canonical readings (*Mālik* / *Malik*); an eschatological scene |
| 1:5 | 11 | 1,659 → 1,662 | 7 | covenant (the ḥadīth qudsī's "between Myself and My servant"); a ruling's condition; a disputed term (*ʿibādah*) |
| 1:6 | 6 | 1,634 → 1,679 | 7 | the chapter's most repeated formula (§6); the layers of *hidāyah* disputed as four kinds |
| 1:7 | 18 | 2,040 → 2,081 | 7 | eschatological categories; a named report with a live grading dispute; an identification the commentators argue |

Deepest three, each on its own written ground:

- **1:1** — the only verse of the chapter whose canonical *status* is itself litigated, across four
  legal schools, and the section carries the whole dispute (Anas through Muslim 399; Abū Hurayrah
  through Ibn Khuzaymah and al-Ḥākim; Ibn ʿAbbās through Abū Dāwūd 788; the Shāfiʿī and Jaʿfarī
  position; the Ḥanafī and Mālikī position; Ibn Taymiyyah's adjudication that the dispute is about
  liturgical numbering only) alongside the morphology of both mercy names and the derivation debate
  over *Allāh*.
- **1:5** — the structural pivot and the covenant itself: the *ḥaṣr* grammar of the fronted object,
  the definition of worship, the four-motive classification of worshippers, and the effort/*tawakkul*
  synthesis that later jurisprudence and ethics both build on.
- **1:7** — the three-category doctrine of mankind, the passive-participle theology of *maghḍūb*
  and why the agent of wrath is left unnamed, the semantic range of *ḍalāl*, and the ʿAdī b. Ḥātim
  report together with the note that its chain is not of the strongest while its meaning is
  corroborated. At 2,081 words it is the only section that could not sit under the Tier-1 ceiling.

**§7 dedup test, run per verse before drafting.** The test asks whether a candidate heading's
citations are already in the section. No candidate heading was ever proposed, because no section
was below its floor and §5 forbids padding an above-band section; so the test's output is that all
seven sections are saturated and none is demoted. Two corollaries of §7 were still applied, and
both paid:

- **Every concordance below was counted from `translation/` by grep, never from memory or from a
  cached list.** That is what exposed §9.4 and §9.5.
- **No heading drafted in one section was duplicated in another.** The one place a harmonisation
  could have gone twice — the *raḥim*/womb derivation from the Name *al-Raḥmān* — is drafted at
  1:1 under "Two Names of Mercy at the First Threshold" and only cross-referenced at 1:3 ("recall
  the linguistic foundation laid in the commentary on 1:1"). It stays that way.

**Reduced floor: no chapter-1 entry.** Five verses are fourteen words or fewer in
`translation/001.txt` (1:1 ten, 1:2 nine, 1:3 five, 1:4 six, 1:6 six), so the first half of §5's
test is met — but the second half is not, for any of them. None is a *muqattaʿah*; none is a single
dialogue clause; none is a scene-closer taking its sense from the verse before it. 1:3 and 1:6 look
like continuations and are not: 1:3 is a full statement of two divine names with a disputed
distinction behind it, and 1:6 is an independent petition carrying the chapter's most repeated
formula. §5's own rule decides it — "a short verse that is not a fragment stays in the full band —
there is real scholarship to fill it with" — and each of the five is in fact filled, from 1,453 to
1,776 words. `SHORT_VERSE` therefore gains nothing, and the summary line's `reduced-floor` counter
(which counts floors *below* the band floor, per the note in §13) correctly reads 0 for this
chapter and still reads 18 for 007.

---

## 6. Concordances counted from `translation/` for this run

Measured by grep over all 114 files, counting verse lines only. These are the numbers the Tier-1
marker "a formula the Qurʾān repeats elsewhere, which can be counted across chapters" rests on.

| Formula | Occurrences | Sūras | Note |
|---|---|---|---|
| "Straight Path" (any case) | 30 | 20 | densest at 43 (3); 2, 3, 4, 6, 16 at 2 each |
| "Straight Way" | 6 | 6 | 6:39, 16:9, 30:30, 41:6, 46:30, 81:28 — a distinct phrase, not a variant spelling |
| "Lord of all worlds" | 42 | 21 | densest at 26 (11), then 7 (5) |
| "praise be to Allah" (any case) | 10 | 8 | the ḥamd closing formula, 39:75 among them |
| "All praise is for Allah" | 14 | 12 | 1:2's exact opening, recurring at 6, 27, 10, 14, 17 … |
| full basmalah, "In the Name of Allah—the Most Compassionate, Most Merciful" | **2** | 2 | 1:1 and 27:30 only — the section's claim that it occurs "once inside the body of the text" is correct as measured |
| "Most Compassionate, Most Merciful" | 6 | 5 | 1:1, 1:3, 2:163, 27:30, 41:2, 59:22 |
| "Day of Judgment" | 64 | 34 | densest at 3 and 28 (5 each) |
| "astray" | 56 | 35 | densest at 20 (4) |

Two traps avoided by counting rather than remembering: "In the Name of Allah" alone returns **four**
hits, because 11:41 has Noah's *"In the Name of Allah it will sail and cast anchor"* — the *full*
basmalah is what occurs twice, and the phrase had to be grepped in full before the count could be
used. And "Most Compassionate, Most Merciful" returns **seven** hits by raw grep; the seventh is
not a verse (§9.5). A third trap was *not* avoided on the first pass of this very document, and is
recorded as §9.14 — read it before trusting any list of verse numbers written here.

---

## 7. Gate results, measured at the end of the run

```
python3 tools/quran-audit/check_filler.py --sura 1 --band 1200-1400
001.md   7 sections  11693 words  band 1200-1400  min 1453 / med 1662 / max 2081
         below 0 above 0  reduced-floor 0  tics 0.00/1k  chains 0.00/1k
         dup 0.003  repeated sentences 0  FAILING 0

python3 tools/quran-audit/check_cross_quotes.py 1
quoted spans: 115  (with a Quranic citation: 76, uncited: 39)
  EXACT     76
  UNCITED   39
DRIFT 0   ELLIPSIS 0   VICINITY 0   NOVERSE 0

python3 tools/quran-audit/validate.py
PASSED: 114/114
FAILED: 0

python3 tools/quran-audit/census.py --sura 1
files: 1   sections: 7   words: 13,786
corpus-wide: 0 sections < 260 w, 0 sections < 400 w
001.md    7  1662  1954  2327    13,786     0     0

python3 tools/quran-audit/check_translations.py --sura 1
checked: 7 sections (no translation line: 0, no source text: 0)
flagged (<0.45 against BOTH initial/ and translation/): 0
```

Corpus-wide `check_translations.py` still reports exactly the **7 pre-existing flags** — 010.md:91,
050.md:25, 068.md:3/10/13/25, 094.md:7 — and none of them is in chapter 1, so nothing new was
introduced.

`census.py` and `check_filler.py` disagree by design: census keeps fully-bold mini-heading lines
and counts the introduction, so its 13,786 is not comparable to the gate's 11,693. The gate's
figure is the one §11 uses, and it is the one quoted everywhere in this document.

**007 regression check, required by §13, run after the `check_filler.py` edit:**

```
python3 tools/quran-audit/check_filler.py --sura 7 --band 1200-1400
007.md  206 sections  277675 words  band 1200-1400  min 824 / med 1370 / max 2100
        below 0 above 0  reduced-floor 18  tics 0.19/1k  chains 0.12/1k
        dup 0.062  repeated sentences 0  FAILING 0

python3 tools/quran-audit/check_cross_quotes.py 7
quoted spans: 2125  (with a Quranic citation: 1780, uncited: 345)
  EXACT     1780
  UNCITED   345
```

277,675 words, FAILING 0, reduced-floor 18, 1,780 EXACT — all four figures identical to the values
§13 requires. The edit widened `DEEPEST` and `TIER1` by union with `'1:x'` keys and left every 007
literal byte-identical, so `depth_floor` and `depth_ceiling` needed no change: their keys already
carry the sūrah number.

---

## 8. Comparison against the 007 benchmark

The prompt says to match ratios, not absolutes. Chapter 1 has seven verses; 007 has 206.

| Measure | 007 gold standard | 001 after this run |
|---|---|---|
| Sections, one per verse, canonical skeleton | 206 | 7 |
| Body words (blockquoted verse text excluded) | 277,675 | 11,693 |
| Median section | 1,370 | 1,662 |
| Shortest / longest | 824 / 2,100 | 1,453 / 2,081 |
| Qurʾānic quotations, every one EXACT | 1,780 | 76 |
| DRIFT / ELLIPSIS / VICINITY / bad refs | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Tics per 1,000 words | 0.19 | **0.00** |
| Chains per 1,000 words | 0.12 | **0.00** |
| Duplicate 10-gram fraction (worst section) | 0.062 | **0.003** |
| Sentences of 12+ words repeated verbatim in-file | 0 | 0 |
| Sections failing any gate | 0 | 0 |
| Own-verse blockquotes verbatim from `translation/` | 206 / 206 | 7 / 7 |

Every verse is inside its band, every citation is exact, every gate is at zero failures. The
median is above 007's because the Fātiḥah's verses are short and dense and were drafted long, and
the duplication and tic ratios are better because the file is small enough that nothing had to be
recycled to reach length.

---

## 9. Corrections — errors found along the way, numbered

Read this section before touching chapter 1 again, and read items 1–5 before trusting any
concordance anywhere. §10.15 of `DEPTH_PLAN_007.md` established the rule that a figure written in a
log must be measured in the step that writes it; items 1–5 are the same rule applied to quotations.

1. **The prompt's own §1.2 collides with its Mission at `{{N}}=1`.** Recorded in §1 rather than
   resolved silently. Any future run on a chapter that the prompt also names as a reference input
   will hit the same wall; the resolution there should be the one here.

2. **A plan that assumed chapter 1 needed depth would have been wrong.** The intuitive reading of
   "bring to the 007 standard" is that a 94 KB file next to a 1.7 MB gold standard is thin. Measured,
   chapter 1 was already above the Tier-1 floor in all seven sections before a single edit. Its
   defect was exactness, not length. Measure before proposing heads — the same error §10.3 of
   `DEPTH_PLAN_007.md` records for 7:175.

3. **`check_translations.py` cannot see the defect this chapter had.** It passes a section that
   matches *either* `initial/` or `translation/` above 0.45, and all seven of 001.md's blockquotes
   matched `initial/001.md`. The only gate that catches an own-verse blockquote which is not
   verbatim from `translation/` is a direct string comparison, which is not in any of the four
   gates. It was done by hand here and is recorded as a script for the next session (§10).

4. **A citation re-pointed from memory is a citation re-pointed wrongly.** 2:61 was cited for
   "wrath upon wrath"; that phrase is in **2:90**. 25:67 was cited for "do not exaggerate in your
   religion"; 25:67 is about spending, and the phrase is **4:171**. 26:20 was cited for "I was
   among the astray"; the verse says **"I did it then, lacking guidance"**. 90:10 was cited in the
   first person plural-adjacent ("We have shown him"); the verse is second person plural, **"shown
   them"**. All four were found by reading the verse, and each would have survived a memory check.

5. **A raw grep over-counts when a file carries non-verse text.** "Most Compassionate, Most
   Merciful" returns seven hits across six files. The seventh is in `translation/048.txt` line 1,
   which does not contain verse 48:1's text at the start of the line at all — it carries the sūrah's
   editorial introduction (~1,600 characters of asbāb narrative about the Treaty of Ḥudaybiyah)
   with the verse appended after it: *"…In the Name of Allah—the Most Compassionate, Most Merciful
   Treaty of Ḥudaibiyah 1. Indeed, We have granted you a clear triumph ˹O Prophet˺"*. The true
   count in verse text is **six across five files**. This is an input-data defect in a file §1.2
   forbids this session to modify; it is logged for whoever owns `translation/`, and any future
   chapter-48 run must know that `check_cross_quotes.py 48` tests quotations of 48:1 against that
   whole blob, and that a *correct* quotation of the verse's opening words will pass only because
   the test is a substring test.

6. **Two anchors in the batch scripts were written from memory and failed the uniqueness assert.**
   `ʿabd` was typed as `ʿd`, and `ḍalāl` as `ḑalāl` (d-cedilla U+1E11 for d-dot-below U+1E0D). The
   script's rule — refuse to write if any anchor is non-unique — turned both into a no-op instead of
   a corruption. Diacritics must be copied from the file, not typed; where they must be typed, the
   codepoint has to be checked.

7. **A post-apply fix was needed because the fix itself moved the gate's citation window.** Making
   the 33:43 quotation at 1:3 exact required putting `(33:43)` inside the parenthesis that
   attributes the Ibn ʿAbbās report. The gate then took `33:43` as the citation for the *outer*
   span — the Ibn ʿAbbās report — and reported it as DRIFT against 33:43. Fixed by moving the
   Ibn Kathīr sentence and its quotation out of the attribution parenthesis into prose of their
   own, on a new line. Lesson: never nest a second parenthesis inside a citation parenthesis, and
   never let a Qurʾānic reference sit in the trailing parenthesis of a *scholar's* quotation.

8. **`check_cross_quotes.py` has a blind spot that hides quotations, and this chapter had one.**
   The gate skips any span whose ±60-character neighbourhood matches its `HADITH` regex — which
   includes the bare token `Muslim`. The word **"Muslims"** therefore suppresses a Qurʾānic
   quotation. At 1:1 the span *"And what is al-Raḥmān?"* (25:60) was followed 26 characters later by
   "the early Muslims later heard", so the gate classified the whole span as a hadith report and
   never read it. It was invisible, and it was still wrong. It
   was found by a private scanner that lists every span with an `S:V` reference nearby regardless of
   the hadith skip, and corrected to *"What is 'the Most Compassionate'?"* (25:60). That scanner
   found exactly **one** such span in this chapter; a longer chapter will have more, and no gate
   will report them.

9. **Unbalanced scare quotes make the gate read prose as scripture.** Straight `"…"` used for
   scare quotes pairs up across a whole line, and at 1:4 it swallowed the real 2:282 quotation into
   a 300-character span of commentary about *dīn* and *dayn*. Converting the scare quotes on the
   affected lines to curly quotes (1:1, 1:2, 1:4, 1:5, 1:7 — five lines) restored correct pairing
   and let the real span be cited and verified. Straight double quotes should not be used for scare
   quotes anywhere in `expanded/`; the gold standard does not use them.

10. **A corrupted sentence was repaired.** 1:7 read *"Erra and beledig categories exist to identify
    roads, not to nail souls in place"* — two non-words where "These" belongs, evidently a
    transliteration fragment pasted over an English word. Repaired to *"These categories exist to
    identify roads…"*. This is a text-integrity repair, not a rewrite of commentary; the sentence's
    argument is unchanged.

11. **Two claims in the existing prose were checked against `translation/` and left standing, one
    corrected.** The claim that the basmalah "occurs once inside the body of the text as well" was
    verified by grep and is **correct** (§6). The claim at 1:7 that 5:77 describes "the Meccan
    generations of Christians" was **not** correct — al-Māʾidah is Medinan and 5:77 addresses the
    People of the Book generally — and was minimally corrected to "the people of scripture warned
    against following…". Left standing and flagged for a future pass, because §1.3 forbids
    rewriting existing commentary and neither is a quotation: at 1:4 the phrase *"ʿAbdullāh ibn
    Ubayy's peer al-ʿĀṣ ibn Wāʾil"*, which pairs a Medinan hypocrite with a Meccan aristocrat as
    though they were contemporaries in the same city. The 75:3–4 quotation next to it is now exact;
    the appositive is a historical claim this session had no mandate to adjudicate.

12. **The style gates went up before they went down, and that was the correct order.** Correcting
    the quotations exposed 2 tics and 1 chain that had been hidden inside quoted spans the gate
    strips before scoring prose (`in a sense` twice at 1:7, `of the vermin of the` at 1:3). Both
    were well inside the thresholds — 0.17/1k against limits of 4.0 and 1.5 — but §9 of the prompt
    targets near zero, so all three were removed: the two hedges deleted, and *"to eat of the
    vermin of the earth"* reduced to *"to eat the vermin of the earth"*. Final: tics 0.00/1k,
    chains 0.00/1k. The lesson is that `prose_only()` scores only what survives quote-stripping, so
    a change of quotation marks moves the style score even when no prose is touched.

13. **`expanded/001.md` and `expanded/007.md` use different English translations of the Qurʾān in
    their prose apparatus.** After this run every *quotation* in 001.md comes from `translation/`,
    but the file's running prose still says "God" where the translation says "Allah", "the
    Compassionate" where it says "the Most Compassionate", and "Criterion" where it says
    "Standard". That is a register choice in unquoted commentary, which §1.3 protects, and it is not
    a gate failure. A future session that wants full terminological consistency should treat it as
    a separate, explicitly-authorised pass, not as standardisation.

14. **This document’s own first draft contained a recalled list, and it was wrong in five of six
    entries.** §6 tabulates the six occurrences of "Straight Way". Written from memory they were
    6:157, 16:121, 30:43, 41:52, 46:22, 81:28. Grepped for their verse numbers they are
    **6:39, 16:9, 30:30, 41:6, 46:30, 81:28** — one of six correct. The counts in the table were
    measured and were right; the verse numbers were recalled and were not. This is exactly the
    failure `DEPTH_PLAN_007.md` §10.15 records for two word totals, and §10.9 records for the
    *khusr* and suddenness concordances: a count taken from `translation/` is trustworthy, a list
    of *where* it occurs is not, unless the same grep printed the locations. Every location cited
    anywhere in this document has now been printed by a grep in this session.

---

## 10. What the next session should reuse

1. **A blockquote-verbatim check is missing from the four gates.** `validate.py` tests the *form*
   `^> \*\*.+\*\*$`; nothing tests that the content equals `translation/NNN.txt`. The eleven lines
   used here are enough, and the check found six of seven blockquotes wrong in this chapter while
   `check_translations.py` found none:

   ```python
   tr = dict((int(m.group(1)), m.group(2).strip()) for m in
             (re.match(r'^\s*(\d+)\s*\|\s*(.*)$', l.rstrip('\n'))
              for l in open('translation/%03d.txt' % n, encoding='utf-8')) if m)
   # for each '## Sūrah … N:V' heading at line i: lines[i+2][4:-2] must equal tr[V]
   ```

2. **A citation-blind-spot scanner is missing too.** List every span with an `S:V` reference in its
   neighbourhood *regardless* of the `HADITH` skip, and diff that against the gate's own rows. The
   difference is the set of Qurʾānic quotations no gate is reading. Item 8.

3. **The batch script's shape is worth keeping for correction runs**: `(old, new)` pairs, each
   asserted unique, all-or-nothing write, dry-run word projection printed before `--apply`, never
   re-run after an apply. §10.5's insertion script is right for additions and wrong for corrections.

4. **Chapter 1 is finished.** All four gates are green at zero failures, all seven blockquotes are
   verbatim, all 76 cited spans are EXACT, tics and chains are at zero, and no section is below its
   floor or above its ceiling. The remaining work on this file, if anyone wants it, is item 13 — a
   terminological harmonisation of unquoted prose — and item 11's flagged appositive. Neither is a
   gate matter.
