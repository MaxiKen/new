# DEPTH_PLAN_001 — Standardization of `expanded/001.md` (Sūrah al-Fātiḥah)

Working plan for bringing `expanded/001.md` to the `expanded/007.md` standard per
`STANDARDIZATION_PROMPT.md` ({{N}} = 1, {{NNN}} = 001). Section 10 is the running
corrections log; it supersedes earlier sections where they conflict.

## 1. Baseline state (measured before any edit, commit `0864ef9`)

| Gate | Result |
|---|---|
| `validate.py` | 114/114 PASSED, 0 FAILED |
| `check_filler.py --sura 1 --band 1200-1400` | 7 sections, 11,508 body words; min 1,453 / med 1,634 / max 2,040; **FAILING 7** (all `depth>1400` — no Tier-1 list existed for chapter 1); tics 0.00/1k, chains 0.00/1k, dup 0.003, repeated sentences 0 |
| `check_cross_quotes.py 1` | 120 spans; 66 cited: **DRIFT 61, VICINITY 4, EXACT 1**, UNCITED 54 |
| `census.py --sura 1` | 7 sections, 0 below 260, 0 below 400 |
| `check_translations.py --sura 1` | 7 checked, 0 flagged |

Diagnosis: the seven sections are already at or above the gold-standard depth
(007 mean 1,348; here 1,453–2,040), with 6–8 mini-headings and 15–19 paragraphs
per section (007: mean 10.1 / median 8 headings; 16.6 / 17 paragraphs), and a
1,327-word introduction under 4 mini-headings (007: 982 under 4). The file's
deficit is entirely one: **every Qur'anic quotation — the seven blockquotes and
every inline cross-reference — was sourced from the old rendering** (the
`initial/` wording), while `translation/001.txt` and the other `translation/`
files now carry different wording. The work is therefore a re-sourcing pass,
not an expansion pass:

1. the seven blockquotes are replaced by the verbatim `translation/001.txt` lines;
2. the 61 DRIFT spans are rewritten as verbatim contiguous spans of the cited
   verses in `translation/`, each with its `(S:V)` citation immediately after;
3. the 4 VICINITY citations (qualifying words inside the citation parenthesis,
   `cf. …`) are de-qualified and their parallel references handled per 007
   practice (one or two of the parallels quoted with their own citation, the
   rest named without quotation marks);
4. the old-rendering verse wording embedded in the Muslim 395 ḥadīth qudsī and
   in a few prose glosses is aligned to the translation's wording (§3.1/§3.2).

## 2. Tier-1 list (chosen before drafting, §8)

All seven verses qualify under the §8 criteria (each carries a divine name or
attribute, a repeated formula, a disputed term, or the sūrah's covenantal core):

| Verse | Tier | Ground |
|---|---|---|
| 1:1 | Tier-1 | the basmalah: three divine Names, the legal dispute over its verse-status, the consecration formula of every rakʿah |
| 1:2 | **Deepest** | the opening doctrinal statement: al-ḥamd, Rabb, al-ʿālamīn — rubūbiyyah stated as the root of the 1:5 argument |
| 1:3 | Tier-1 | the two Names of mercy: the Raḥmān/Raḥīm distinction the tradition disputes, the Name no creature may bear |
| 1:4 | Tier-1 | Mālik/Malik, *dīn*, and the Day of Reckoning as the eschatological pivot of the sūrah |
| 1:5 | **Deepest** | the covenant of worship and help — the exact center of the sūrah; the ḥadīth qudsī's hinge verse |
| 1:6 | **Deepest** | the *ihdinā* petition: the layers of hidāyah, the anatomy of al-ṣirāṭ, the bridge |
| 1:7 | **Deepest** | the three destinies: blessed / displeased-with / astray — the sūrah's closing argument |

No `SHORT_VERSE` entries: no verse of al-Fātiḥah is a fragment of the qualifying
kinds (no *muqattaʿāt*, no bare dialogue clause, no scene-closer) — 1:1 at ten
words and 1:4 at five words are complete doctrinal statements with consumed
scholarly surface (1,725 and 1,480 words respectively in the baseline).

## 3. §9 deduplication test, run per verse before drafting

The seven sections were read in full with their existing mini-headings extracted,
and every candidate new heading was tested against the section's existing
citations:

- **1:1** — heads: *The Phrase That Stands Above Every Page; Is the Basmalah a
  Verse?; Why Begin with a Name at All?; The Word Allāh; Two Names of Mercy at
  the First Threshold; Beginning Like the Book Itself.* Every candidate
  (the basmalah's occurrences, its legal status, the Name's exclusivity, the
  mercy root) is already carried with its sources (27:30, 96:1, 43:87, 19:65,
  the Anas/Abū Hurayrah/Ibn ʿAbbās reports). **Saturated as to heads; re-sourced only.**
- **1:2** — heads: *Why the Book's First Statement Is Praise; Ḥamd Is Not Mere
  Thanks; Rabb: The Lord Who Cultivates; What Are "the Worlds"?; Gratitude as a
  Law of Increase; Ending Where This Verse Ends.* Candidates (the ḥamd/shukr/
  madḥ distinction, the lām of entitlement, the ʿālamīn readings, the
  eschatological closing formulae 10:10 / 39:75 / 37:182) all present. **Saturated; re-sourced only.**
- **1:3** — heads: *A Deliberate Repetition; Two Names from One Root; A Name No
  Creature May Bear; The Psychology of a Mercy-First Creed; Mercy that Demands
  to Become Social; Two Registers of One Light.* Candidates (the faʿlān/faʿīl
  anatomy, the Ibn ʿAbbās report, 25:60's Meccan question, the 100 portions,
  the dog/cat reports) all present. **Saturated; re-sourced only.**
- **1:4** — heads: *Two Readings, One Unshakable Certainty; Why Single Out a
  Day; Dīn: The Day the Debt Comes Due; Justice Deferred Is Not Justice
  Denied; A Doctrine That Edits a Life; Standing Before the Sentence, Daily.*
  Candidates (Mālik/Malik, the 40:16 scene, the dayn/dīn etymology, the
  99:7–8 / 7:8–9 scales, ʿUmar's muḥāsabah) all present. **Saturated; re-sourced only.**
- **1:5** — heads: *The Turn at the Exact Center; Grammar as Creed; Worship
  Defined; Why "We" When One Prays Alone; The Second Clause; Reliance Without
  Passivity; The Covenant Repeated.* Candidates (the iltifāt, the ḥar
  fronting, 19:93 / 51:56 / 39:2, the camel-tethering report) all present.
  **Saturated; re-sourced only.**
- **1:6** — heads: *The Greatest Thing Ever Asked; The Layers of Hidāyah; The
  Ṣirā: Anatomy of a Road; The Middle Road Between Every Two Extremes; Map,
  Guide, Companions, Provisions; Why the Ask Must Be Daily; The Other Ṣirāṭ.*
  Candidates (90:10 / 41:17 / 28:56 / 47:17, the Al-Nawwās parable, 2:143,
  17:9 / 42:52–53 / 11:56 / 9:119 / 2:197, the bridge) all present.
  **Saturated; re-sourced only.**
- **1:7** — heads: *A Path Known by Its Travelers; Who Are the Blessed?; Those
  Who Incur Wrath; Those Astray; Three Trajectories and One Daily Crossing;
  Hard Grammar, Open Door; Āmīn: The Seal of the Whole.* Candidates (4:69,
  the ʿAdī report, the 2:61 / 3:90 / 2:108 / 4:136 / 5:77 / 28:50 / 26:20 /
  93:7 / 16:125 map, 39:53 / 13:27, the āmīn report) all present.
  **Saturated; re-sourced only.**

Result: **no new mini-headings drafted for any section; no demotions either**,
because every section's depth already sits at or above 1,400 words and only the
Tier-1/Deepest ceilings can hold it. The sections stay Tier-1 by depth, not by
padding. New words enter only as (a) verbatim quotation spans (the translation's
wording is slightly longer in places), (b) one parallel-verse quote at 1:6
(19:76) replacing the `cf.` in a VICINITY citation, and (c) one sentence at 1:1
naming the 29:61–63 / 31:25 / 39:38 parallels that the old `cf.` list carried.

## 4. Quotation conventions adopted (from the gold standard)

- Qur'anic spans are set in **curly double quotes** `“…”`, the 007 style —
  007 quotes spans containing curly apostrophes (`Allah’s`) inside curly
  doubles, which the gate's span detector reads correctly; the file's existing
  straight-quote prose is left untouched except where a quotation itself is
  being re-sourced.
- Each re-sourced span is a **verbatim contiguous substring** of the cited
  verse(s) in `translation/` (verified by substring assertion in the applying
  script, never retyped from memory).
- Citation forms: `(S:V)` or `(S:V–S2)`, immediately after the closing quote.
- Spans begin with the translation's own capitalisation; lowercase openings are
  placed after a colon or dash so they read correctly.
- Verse text embedded in the Muslim 395 ḥadīth qudsī and in the al-Bukhārī 5006
  report is aligned to the translation's wording (a Qur'anic quotation inside a
  ḥadīth quotation is still a Qur'anic quotation, §3.1).

## 5. Batch log

| Batch | Sections | Before (body words) | After (body words) | Heads added | Heads struck | Gate results |
|---|---|---|---|---|---|---|
| A | Introduction, 1:1, 1:2 | 1,725 / 1,453 | — | 0 | 0 | — |
| B | 1:3, 1:4 | 1,517 / 1,480 | — | 0 | 0 | — |
| C | 1:5, 1:6 | 1,659 / 1,634 | — | 0 | 0 | — |
| D | 1:7 | 2,040 | — | 0 | 0 | — |

(Filled in as each batch lands.)

## 6. Vocabulary decisions

- General commentary word for God remains **God** — the confirmed gold standard
  `expanded/007.md` uses "God" 697 times against a translation that says
  "Allah" 81 times and "God" zero times, so the house standard tolerates it.
- Where the translation names a specific term, the translation's word is used
  in the new and re-sourced text: *the Most Compassionate, Most Merciful; Lord
  of all worlds; Master of the Day of Judgment; the Straight Path; the Path of
  those You have blessed; displeased; astray; we worship; we ask for help;
  the great Quran; the seven often-repeated verses.*

## 10. Corrections log

(Running record of errors found in this plan or in the baseline as the work
proceeds; see §10.1 onward. Nothing recorded yet.)

### 10.1

(placeholder — see below as entries are added)
