# Standardization Prompt — bring any chapter to the `expanded/007.md` standard

Copy everything below the line into a fresh session. Replace the two placeholders first:

- `{{N}}` — the chapter number as an integer, e.g. `11`
- `{{NNN}}` — the same number zero-padded to three digits, e.g. `011`

This prompt is the complete specification of everything that was done to `expanded/007.md`. It is
deliberately long: it carries the rules, the measured norms, the gates, the defect classes that the
gates miss, and the pre-decided answer to every judgement call. Nothing here is optional background.
Do not shorten it before use.

**Those two substitutions and the instruction to run are the operator's entire contribution.** It is a
blueprint for a single uninterrupted run: the session it is pasted into must start and finish the
chapter without asking anything, reporting anything intermediate, or waiting for anything. See *The
one-shot mandate* below, which governs every section that follows.

---

## The one-shot mandate — read this first

This document is a **blueprint**. Its operator supplies exactly two things and nothing else: the
chapter number substituted into `{{N}}` and `{{NNN}}`, and the instruction to run. Every other decision
this work requires has already been taken and is written down below. **No further input from the
operator exists, is needed, or may be requested.**

Your job is to **start and finish chapter `{{N}}` in one continuous run** — from the first measurement
to the committed, gate-clean, logged deliverable — and to produce **exactly one** output to the
operator: the final report described in §24.

### What "finished" means

Not "started". Not "the first tranche is done". Not "here is the plan, shall I proceed?". Finished:

- all nine passes of §19 run, each with its measured figure recorded;
- every verse of the chapter inside its band, in the canonical skeleton, with 007's internal shape;
- every gate green at zero failures, plus the eight beyond-gate requirements of §25;
- the work committed, and pushed if the session has remote access;
- `tools/quran-audit/DEPTH_PLAN_{{NNN}}.md` written;
- one final report posted.

If any of those is missing, you have not finished, and you keep going.

**If more than one chapter is named**, the same mandate applies to each: complete them in ascending
chapter order, each one taken through all nine passes to the full standard before the next begins, and
produce a single combined report at the very end. Never pause between chapters, never report one and
wait to be told to start the next, and never treat a finished chapter as a reason to stop — the run
ends when the last named chapter is committed, logged and green.

### Never stop for any of these reasons

Each row is a point where an agent typically pauses. **Every one is pre-decided; act on it and
continue in the same run.**

| The moment | What you do instead of stopping |
|---|---|
| The chapter is long, or the run is taking many steps | Continue. Length is never a reason to pause, checkpoint with the operator, or split the work. 007 ran 206 sections across nine passes |
| You have finished a batch, a tranche or an instalment | Continue to the next one immediately. Batches exist to organise the work, not to create reporting points |
| You are unsure which phase the chapter needs | Run the §17 measurements and read the decision table. It decides. Do not ask which one applies |
| You must choose the Tier-1 list, a deepest-four set, or reduced-floor exceptions | §8 and §4 decide the criteria; §15 decides the ties. Choose, write the reason into the plan document, continue |
| Two readings of a rule seem to conflict | Take the one that adds sourced scholarship and needs no input (§15, final row), and record the choice |
| A gate keeps failing after several attempts | Keep fixing. A failing gate is work, not a question. Only §15's "gate examined zero sections" row changes the target — and that changes it to fixing the check, still without asking |
| `check_filler.py` still holds 007's lists and not this chapter's | Edit it per §14, re-verify 007 is unchanged, continue. This is expected work, not a blocker |
| `expanded/{{NNN}}.md` is missing, incomplete, or has fewer sections than the chapter has verses | Build the missing sections from the apparatus in `initial/{{NNN}}.md` in the canonical skeleton (§5) and continue. Do not report the gap and wait |
| `initial/{{NNN}}.md` is thin, or a verse has no source note at all | Match depth to what the source supports and document the lower floor (§21.5). 036.md was rebuilt at a median of 516 words deliberately below the corpus norm for exactly this reason. One verse corpus-wide had no note; it was written from the verse itself with cross-references from `translation/` |
| A quotation cannot be verified, or a ḥadīth number will not resolve | §15: attribute to a named exegete as tradition, or drop it and quote the Qurʾān. Never leave it pending |
| A ḥadīth number conflicts across the corpus | §22.3: correct only where the corpus is **unanimous**; otherwise record the variance in the plan document and move on. Harmonising to a plurality is forbidden |
| You find a defect class the gates do not cover | Fix it under §21–§23 and log it. Discovering an ungated defect is the normal case here — 007 needed four passes that no gate could see |
| Your context window is filling, or the run is very long | Do not summarise-and-hand-off, do not ask the operator to say "continue", do not end the turn early. Keep executing with tool calls until the chapter is finished |
| `git push` or a pull-request call fails, or the session has no remote access | Commit locally, say so in one line of the final report, and finish everything else. Losing the remote is never a reason to stop the work |
| You are tempted to check whether the operator wants scope widened to another chapter | They do not. Scope is **chapter `{{N}}` only**. Never touch another chapter's content; the single exception is §14's requirement to leave 007's gate lists intact |
| You have nothing left to do but report | Report once, per §24, and stop. That is the only permitted stop |

### Prohibited behaviours

These are the specific shapes an unfinished run takes. None is acceptable:

- **No progress reports.** No "batch 3 of 20 complete", no running commentary, no intermediate
  summaries. Silence until the final report.
- **No questions of any kind.** Not clarifying, not confirmatory, not rhetorical-with-a-pause. If a
  question forms, answer it from §15, §17, §21–§23, or `translation/` — in that order — and continue.
- **No "shall I continue?", "would you like me to…", "let me know if…"**. The answer is always yes and
  it is already given.
- **No partial delivery.** A plan without the chapter, a first tranche without the rest, a gate report
  without the fixes, or "the remaining sections will follow" are all failures. Deliver the chapter.
- **No deferral to a later session.** Do not write "this should be done next" into the deliverable as a
  substitute for doing it. The plan document may record genuine future work for *other* chapters;
  it may never record unfinished work for *this* one.
- **No stopping to be told the work looks right.** Verification is yours: run the gates, read the
  sections, measure the figures. §23.1 — a green gate is evidence only about what the gate measures,
  so check what it does not.

### The single report

One output, at the end, per §24: the nine-pass figures, the gate table, sections drafted and demoted,
words added **measured against the commit before you started and never recalled from memory**, anything
you could not do and why, and the path to `DEPTH_PLAN_{{NNN}}.md`. Nothing before it.

## Mission

Bring `expanded/{{NNN}}.md` — the commentary on Sūrah number `{{N}}` — to the standard achieved in
`expanded/007.md`, this repository's confirmed gold standard. Go verse by verse in ascending order
and complete the whole chapter in one continuous run.

Work autonomously to completion, in one run, under the one-shot mandate above. **Never ask a
question, never request approval, never post a progress update, never stop because the chapter is
long, never pause between batches, never end the turn with work outstanding.** Start at verse 1 and
finish at the last verse of the chapter, then commit, log and report — once, at the very end. §15
answers every judgement call in advance; §17 decides the phase; §19 gives the pass order.

**Read §17 before anything else.** It decides which of two phases your chapter needs. A chapter whose
prose is degenerate must be **regenerated** (§18) before it is expanded; a chapter that is merely thin
goes straight to expansion. 007 needed both, in that order: verses 5 to 206 — effectively the whole
chapter — were redrafted in the regeneration phase before a single depth heading was added, and the
expansion phase that followed contributed only 7,149 of the file's 277,675 words.

### The benchmark, measured on `expanded/007.md`

Depth and structure:

| Measure | 007 result |
|---|---|
| Verse sections | 206, one per verse, canonical skeleton |
| Body words | 277,675 (blockquoted verse text excluded) |
| Words per section | mean 1,348 · median 1,370 · min 824 · max 2,100 |
| Mini-headings per section | mean 10.1 · median 8 · min 3 · max 22 |
| Paragraphs per section | mean 16.6 · median 17 |
| Words per paragraph | mean 80 · median 79 · range 56–199 |
| Words per mini-heading block | mean 162 · median 169 · range 72–459 |
| Sūrah introduction | 982 words under 4 mini-headings |

Quotation and sourcing:

| Measure | 007 result |
|---|---|
| Qurʾānic quoted spans | 2,125 total; **1,780 carry a citation and every one is EXACT** |
| Drift / ellipsis / vicinity / bad refs | **0 / 0 / 0 / 0** |
| `(S:V)` citations in body prose | 2,990 — **14.5 per section** |
| Sections with ≥1 citation | **205 of 206 (100%)** |
| Sections containing a transliterated Arabic term in italics | **188 of 206 (91%)** |
| Sections naming a ḥadīth collection or imam | **70 of 206 (34%)** |
| Sections naming a classical exegete | **23 of 206 (11%)** |

Gate results:

| Gate | 007 result |
|---|---|
| `validate.py` | **114/114 PASSED, 0 FAILED** |
| `check_filler.py` | **FAILING 0** · below 0 · above 0 · tics 0.19/1k · chains 0.12/1k · dup 0.062 · repeated sentences 0 |
| `check_cross_quotes.py` | **1,780 EXACT · 0 DRIFT · 0 ELLIPSIS · 0 VICINITY · 0 NOVERSE** |
| `census.py` | 206 sections · 0 below 260 words · 0 below 400 words |

Match the **ratios and the zeros**, not the absolute numbers — chapters differ in length. What must
match: every verse inside its band, every quote exact, every gate at zero failures, citation density
in the same range, and Arabic glossing present in roughly nine sections out of ten.

---

## 1. Hard constraints

1. Work **only** on chapter `{{N}}`. Do not modify any other `expanded/*.md`.
2. **Never modify** `expanded/001.md` (the confirmed structural reference), `translation/*.txt`, or
   `initial/*.txt`. They are inputs, not deliverables.
3. **In Phase 2 (expansion) never cut, delete, reorder, summarise or rewrite existing commentary** —
   that phase is additions only, and if a section you have written exceeds its ceiling you trim only
   what you added in this session. **Phase 1 (regeneration, §17–§18) does replace prose**, but only
   where the diagnostics in §18.1 identify it as degenerate, and only under the guards in §18.2, which
   forbid deleting any sentence carrying a quotation, a verse citation or a scholar's name. If you are
   unsure which phase you are in, you are in Phase 2.
4. Never delete, rename or move the repository root or its `.git` directory.
5. Commit to the session's branch; push only to that branch. **Never force-push.**
6. Keep generated artifacts out of Git. Anything a gate can regenerate stays untracked. `git add -A`
   only after checking `git status` for generated output.
7. Do not run `normalize.py` unless `validate.py` reports structural failures — and if you do, apply
   the two post-normalize checks in §5.4, because `normalize.py` has historically *introduced* both
   of the defect classes that every gate reported green.
8. Never write the `[System Memory Check]` trailer from `system_instructions.md` §6.4 into any file.
   It belongs in chat responses only. Its presence in a deliverable is a defect (see §11.3).

## 2. Read once, then execute — no re-reading

Read these in one pass. Do not return to them except to look up a specific line.

1. `system_instructions.md` — house rules for depth, headings, and continuous execution.
2. `expanded/001.md` — the canonical skeleton. First 40 lines and last 10 lines are enough.
3. `expanded/007.md` — the gold standard. **Do not read the whole file.** Read exactly four
   sections: the introduction; one long doctrinal section (7:143 or 7:46); one narrative section
   (7:73 or 7:91); one short fragment (any verse in the `SHORT_VERSE` list of `check_filler.py`).
   That is the register, density and mini-heading style to reproduce.
4. `translation/{{NNN}}.txt` — the entire chapter, in one read. **This is the authority for both
   wording and vocabulary** (§3).
5. `initial/{{NNN}}.md` — the old archaic source. **Its translation wording may never be quoted and
   its vocabulary must never leak into the commentary** (§3). Its *commentary apparatus* is a different
   matter: the scholarly notes, reports and structural observations in it are legitimate material to
   regenerate from, and that is exactly how 007's worst sections were rebuilt (§18.7). Hold the
   distinction: **`initial/` supplies thought; `translation/` supplies every English word of
   scripture.**
6. `tools/quran-audit/DEPTH_PLAN_007.md` §10 — read the corrections list (§10.5 to §10.15). It is
   the accumulated record of every mistake made on 007. Each is a trap you can avoid for free.
7. The docstrings of the seven surviving scripts in `tools/quran-audit/`.
8. §16 below — the removed tools and the rules they leave behind. Three of them enforce defect
   classes no surviving gate detects; you must run those checks yourself.

## 3. `translation/` is the authority for wording **and** vocabulary

This is the single most important sourcing rule, and it has two halves. Most failures come from
obeying only the first.

### 3.1 The verse text and every quotation come from `translation/`

- The file format is one verse per line: `<verse number> | <text>`. Verse 47 is the line beginning
  `47 | `.
- Each section's blockquote must be that line's text **verbatim**.
- Every Qurʾānic quotation anywhere in the commentary must be a **verbatim contiguous span** of
  `translation/SSS.txt`. Copy-paste it; **never retype from memory.** Retyping produces near-misses
  the gate rejects as DRIFT.
- `initial/` is never quoted. If a section's existing prose quotes the old rendering, replacing that
  quotation with the `translation/` wording is part of the work — `align_own_verse.py` exists for the
  own-verse case (§12.6).

### 3.2 The commentary's own English must use the translation's words

When the commentary refers to anything the translation names, it uses **the translation's English
word**, not a synonym from another rendering, not the writer's preferred term, and not a term
imported from `initial/`. A reader must be able to move between the blockquote at the top of the
section and the prose below it without meeting a second vocabulary for the same thing.

The pattern is: italicised transliteration, an em dash, then the translation's own English.

> *qāla al-malaʾu alladhīna istakbarū* — the arrogant chiefs of his people said

Concrete pairs established on 007. Where your chapter contains these terms, these are the words:

| Arabic | The word `translation/` uses | Not |
|---|---|---|
| *malaʾ* | **chiefs** | nobles, notables, elite assembly |
| *mustakbir* | **arrogant** | haughty, prideful |
| *mustaḍʿaf* | **lowly / weak** | oppressed masses, the poor |
| *khāsir* | **losers** | ruined, undone |
| *rajfah* | **˹overwhelming˺ earthquake** | temblor, quake |
| *ṣayḥah* | **˹mighty˺ blast** | shout, cry, clamour |
| *ẓullah* | **˹deadly˺ cloud** | shadow, canopy |
| *jāthimīn* | **lifeless** ("they fell lifeless in their homes") | prostrate, crouching |
| *aʿrāf* | **the heights** | the wall, the partition |
| *muḥsin* | **good-doers** | virtuous, excellent |
| *āmana / amn* | **feel secure** | feel safe, be at ease |
| *istidrāj* | **gradually draw them to destruction in ways they cannot comprehend** | gradual punishment, entrapment |
| *fāḥishah* | the translation's own word at each occurrence — check each one | indecency, lewdness |

Where the translation inserts an editorial gloss in brackets, that gloss is part of its wording:
`˹overwhelming˺ earthquake`, `˹deadly˺ cloud`, `˹only˺ delay their end`. Reproduce the bracketed
word when quoting, and prefer the bracketed adjective when describing.

**For terms not in this table, derive the word the same way**: read the verse in `translation/`, take
the English noun or verb it actually uses, and use that throughout the section — in headings, in
glosses, and in analysis. If two verses render the same Arabic differently, note the difference
rather than picking a third word.

### 3.3 The echo test — the quantitative form of §3.2

This was enforced by a gate that has since been removed (`check_offtopic.py`). The rule survives and
you must run it yourself with a throwaway inline script (do not commit it):

> Take the **distinctive tokens** from the section's own `> **…**` translation line — words longer
> than three letters, minus a stop list of high-frequency function words (`that, this, they, them,
> their, there, these, those, then, than, what, when, which, while, with, from, have, been, were,
> will, shall, unto, upon, your, ours, thee, thou, thy, and, for, not, but, all, any, who, whom,
> his, her, its, our, you, she, him, was, are, did, does, into, over, only, surely, truly, behold,
> indeed`). Count how many of them appear in the commentary body — non-blockquote, non-heading prose.
> **A section echoes fewer than 15% of its own distinctive vocabulary when its prose has drifted onto
> a different subject.** Skip sections with fewer than three distinctive tokens or with no prose body.

Target for a standardized chapter: **zero sections below 15%.**

Two warnings that come from that tool's own history:

- **Always print how many sections the sweep examined.** An earlier version silently scanned zero
  sections because a regex was missing the `re.M` flag and still printed a clean "0 found" report.
  **Treat `examined: 0` as a failure, not a pass.** This applies to every check you write in this
  session: a gate that examined nothing has proved nothing.
- The test catches drift, not depth. A section can pass it and still be thin; §7 covers length.

## 4. Length rules — the depth band

Body words are tokens matching `[\wʹʼʿʾ’'-]+` counted on lines that do **not** start with `>`. That
is exactly how `check_filler.py` counts, so your estimate and the gate agree.

| Class | Band |
|---|---|
| Standard verse (narrative, legal, doctrinal) | **1,200 – 1,400** |
| Tier-1 verse (the chapter's densest and most consequential) | **1,400 – 1,800** |
| Deepest verses (the 3–5 theological or legal cruxes) | up to **2,100** |
| Reduced-floor exceptions (documented fragments only) | **700** minimum |

Reduced-floor qualification is conjunctive — a verse qualifies **only** if it is fourteen words or
fewer in `translation/{{NNN}}.txt` **and** it is one of: the *muqattaʿāt*; a single dialogue clause;
a scene-closing fragment that takes its sense from the verse before it. A short verse that is not a
fragment stays in the full band, because there is real scholarship to fill it with. On 007 the
qualifying examples were the four disjointed letters, Iblīs's one-clause appeal, the one-clause
divine reply granting respite, a one-clause oath, a one-clause rejection, a one-clause rebuke inside
a longer speech, three scene-closers, and pairs of continuation clauses of six to eight words.

Exceptions are added **one at a time, each with a written reason.** Never in bulk.

### 4.1 Shape inside the band

Length alone is not the standard. Match 007's internal shape (§ benchmark tables):

- **8–10 mini-headings** per standard section; more only where the verse genuinely carries more
  distinct arguments. Never fewer than three.
- **~160 words under each mini-heading** — one developed argument, not a list of gestures.
- **~80 words per paragraph.** Paragraphs run 56–199; a paragraph over 200 words should be split,
  and a paragraph under 50 is usually a fragment that belongs to its neighbour.
- **~15 paragraphs** per standard section.
- The **sūrah introduction** is its own section: on 007 it runs ~980 words under 4 mini-headings,
  covering the sūrah's name, its period and occasion, its structure, and its central argument. Scale
  to the chapter.
- No closing recap paragraph. A section ends on its last argument, not on a summary of itself.

## 5. The canonical skeleton — and the two defect classes the gates miss

### 5.1 File layout

```
# Sūrah <Name> (Chapter {{N}}) — Expanded Verse-by-Verse Commentary
<blank>
## Introduction to the Sūrah
<blank>
**Expanded Commentary**
<blank>
**<bold mini-heading>**
<blank>
<introduction prose, under as many mini-headings as it needs>
```

Then for every verse, in order:

```
<blank>
---
<blank>
## Sūrah <Name> {{N}}:<verse>
<blank>
> **<verse text verbatim from translation/{{NNN}}.txt>**
<blank>
**Expanded Commentary**
<blank>
**<bold mini-heading>**
<blank>
<prose paragraph>
<blank>
**<next bold mini-heading>**
<blank>
<prose paragraph>
```

The file ends:

```
<blank>
---
**[End of the commentary on Sūrah <Name>]**
```

### 5.2 Rules `validate.py` enforces byte-exactly

- `<Name>` is **identical** in the H1, every verse heading, and the end marker.
- The chapter number in the H1 equals `{{N}}`; the number in every verse heading equals `{{N}}`.
- Verse numbers contiguous 1 → last, ascending, no duplicates.
- Every verse heading is preceded by a blank line then `---`, and the line before that is blank.
- **Exactly one rule per boundary, nowhere else.** A rule is legal only as the line immediately
  preceding a verse heading or the end marker.
- After each verse heading: blank, blockquote matching `^> \*\*.+\*\*$`, blank, `**Expanded
  Commentary**`, blank, then the first mini-heading.
- **No `###` or deeper headings anywhere.** Everything below H2 is a bold mini-heading.
- The only H2s are `## Introduction to the Sūrah` and the verse headings. No other H2 of any kind.
- A bold mini-heading is `**Text**`. **Never four or more leading asterisks.** Exactly three is
  legitimate only as `***Term*: the rest**` (bold opening with a nested italic).
- No bare one-to-three-letter word alone on a line between two blockquotes (an orphaned connector —
  the remnant of a lead-in reduced to nothing but its conjunction). Lines ending in a colon
  (`and:`, `God says:`) are valid lead-ins.
- Exactly one trailing newline; never two; **no carriage returns anywhere**.

### 5.3 The two defect classes that every gate reported green

These were found by a regression test, not by a gate: **107 of 114 files carried them while all
gates passed.** After any structural edit — and especially after any `normalize.py` run — check both
explicitly:

1. **Stray horizontal rules.** 219 across the corpus: 134 duplicated boundary rules and 85 orphaned
   inside a section body. The gap existed because the validator tested `L[i-1]` and `L[i-2]` relative
   to a heading, so the sequence `--- blank --- heading` satisfied both tests. Current `validate.py`
   closes this by computing the set of legal rule positions and flagging everything else — confirm
   it still does before trusting a green run.
2. **Non-canonical H2 headings.** 11 across 10 files: introduction subdivisions and concluding
   reflections. These read as legitimate structure and are not verse headings, so they must be
   converted to bold mini-headings.

The recorded root causes, all in `normalize.py`: it kept the rule at the end of the preamble slice
and then re-emitted `['', '---']` before the first section (duplicated intro→verse-1 boundary); it
tested only `parts[-2]` before inserting the closing rule, missing one at `parts[-3]` (duplicated
end boundary); and its `clean()` unglue inserted `\n\n---\n\n` before a welded heading that was later
dropped as a remnant, orphaning the rule inside the body.

### 5.4 Post-normalize checklist

If you run `normalize.py` on the chapter, immediately after:

- Count `---` occurrences and confirm each is immediately followed (after one blank line) by a verse
  heading or the end marker. Zero exceptions.
- List every `^## ` line and confirm each is either `## Introduction to the Sūrah` or a verse
  heading. Zero exceptions.
- Run `validate.py` and confirm 114/114.

## 6. Where every quotation comes from

**Qurʾānic quotations: `translation/SSS.txt` only, verbatim contiguous spans.** The hazards below
are the four that actually cause gate failures; all four were hit repeatedly on 007.

1. **Editorial brackets are words.** The gate strips the bracket *characters* `˹ ˺` but keeps the
   bracketed *words*. Dropping `˹O Prophet˺` from a span is a DRIFT failure. Reproduce brackets
   exactly as they appear.
2. **No ellipses inside a quotation, ever.** Do not join two parts of a verse with `…`. Quote one
   contiguous span, or write two separate quotations with their own citations. Ellipsis spans are
   reported as a distinct failure class.
3. **The curly apostrophe closes a span early.** Span detection ends at the first `’`. Where a verse
   reads `Allah’s mercy is always close to the good-doers`, quote
   `mercy is always close to the good-doers` — not the whole clause. Prefer apostrophe-free
   sub-spans; where impossible, split into two quotations.
4. **The nearest citation wins.** The gate scans roughly 400 characters *after* a closing quote for a
   reference, and the **first** parenthesis it finds is the one the quote is checked against. So:
   put `(S:V)` immediately after every closing quote. When two quotations share a sentence, each
   needs its own parenthesis directly after it, or the first quote will be checked against the
   second's reference and fail. This applies to a section quoting **its own** verse too.

Further quotation rules:

- **No paraphrase inside quotation marks.** A literal gloss goes outside them, in italics:
  *dallāhumā bi-ghurūr* — so he brought about their fall through deception.
- Quoted spans begin with the translation's own capitalisation. If a span starts mid-sentence,
  restructure your sentence so the lowercase opening reads correctly; never capitalise the quote.
- **Zero-hedge rule.** None of these words may appear in the window after a quotation: `vicinity`,
  `cf.`, `sense`, `context`, `sequel`, `account`, `clause`, `onward`, `paraphrase`, `and parallels`,
  `in its own s`. Each marks the citation as non-verbatim and is reported as a VICINITY failure.
  Write around them — this constrains ordinary prose near quotes, so check the sentence after each
  quotation, not just the quotation.
- **Do not quote the same span twice in one section.** Reference it the second time.
- Nested quotations: quote only contiguous **inner** spans, or split multi-verse quotes into
  separate quotations.

**Ḥadīth and scholarly reports:**

- Give the actual wording, and a collection and number **only if verified**. Web search is permitted
  and expected — use it to verify, never to generate.
- If a number cannot be verified after one search: attribute the report to a named exegete as
  exegetical tradition (al-Ṭabarī, Ibn Kathīr, al-Qurṭubī, al-Rāzī, al-Ālūsī, al-Suyūṭī,
  al-Jalālayn), **or** drop the citation and support the point from the Qurʾān instead.
  **Never invent a number.** Never present an unverified report as numbered.
- Where a report is qualified or contested by a commentator, carry the qualifier. Model: an-Nawawī's
  gloss on the *al-arwāḥ junūd mujannadah* chapter of Ṣaḥīḥ al-Bukhārī — affinity and grouping, not
  a pre-earthly assembly. The qualifier is mandatory whenever that report is used.
- Citation forms verified on 007, usable as models of the right specificity: Sunan Ibn Mājah 2225;
  Ibn Mājah 3600/3605 (ʿAmr b. Shuʿayb ← ʿAbdullāh b. ʿAmr, graded ḥasan); Ṣaḥīḥ Muslim 1499a
  (al-Mughīrah ← Saʿd b. ʿUbādah); Muslim 178a and 178b (Abū Dharr, with the variant via ʿAbdullāh
  b. Shaqīq); Ṣaḥīḥ al-Bukhārī 7436 (Jarīr b. ʿAbdullāh); Muslim 8 and Ṣaḥīḥ al-Bukhārī 50 (Book of
  Faith, ʿUmar); Musnad Aḥmad 17311 (ʿUqbah b. ʿĀmir, ḥasan per al-Arnaʾūṭ). Where a report is
  numbered in one collection but reached through another, cite both paths.

## 7. What each verse section must contain

Per `system_instructions.md` §3, and visible in every section of 007:

- **Arabic vocabulary, root and morphology**, transliterated and explained in simple English. Present
  in ~91% of 007's sections; treat it as expected, and its absence from a section as something to
  justify.
- **Qurʾānic cross-references with the actual quoted text** from `translation/` — never bare
  pointers. 007 averages **14.5 citations per section**; a section with fewer than about five is
  under-sourced.
- **Authentic ḥadīth** with real wording and verified collection and number — present in ~34% of
  sections, and expected wherever the verse states a ruling, a reward, or an eschatological scene.
- **Classical scholars' views** — al-Ṭabarī, Ibn Kathīr, al-Qurṭubī, al-Rāzī, al-Ālūsī, Ibn ʿAbbās,
  Ibn Taymiyyah, Mālik, an-Nawawī, al-Suyūṭī, al-Jalālayn, al-Māzharī — named in ~11% of sections,
  and expected wherever the tradition genuinely differs. Where it differs, **give the positions and
  count them** ("ten opinions are recorded on who the people of the heights are"), and where an
  exegete adjudicates, give the adjudication and its ground.
- **Asbāb al-nuzūl** and historical context where applicable, with the chain or source named. Where
  the identity of a figure is not established by Qurʾān or ḥadīth, say so and list the candidate
  identifications with their chains rather than asserting one.
- **ʿAqīdah**: divine attributes, justice, human responsibility, free will, the Hereafter.
- **Fiqh**: where a verse carries a ruling, give the ruling's conditions, its evidences, and the
  schools' positions. Web research is authorised and expected for this.
- **Psychological, social, ethical and practical implications**, including modern application and
  relatable analogy.
- **The logical reason** the command or principle makes sense — not merely what it says.

Length must come from these. Never from restatement, recap, or a summary paragraph.

## 8. Choosing the Tier-1 list

Read every verse from `translation/{{NNN}}.txt` — already done in §2 — and score each for density. A
verse is a Tier-1 candidate if it carries any of:

- a legal ruling, or a ruling's conditions and exceptions
- a divine attribute, name, or act of God stated doctrinally
- a covenant, oath, or eschatological scene
- a named prophetic episode with narrative consequences
- a formula the Qurʾān repeats elsewhere, so that it can be counted across chapters
- a term the exegetical tradition disputes, with identifiable positions

Select roughly **15–25% of the chapter's verses** as Tier-1, and the **3–5 densest** of those as
"deepest". Write the list into your working plan before drafting anything.

Then apply §9 to every one of them, because on 007 this list was **wrong about half the time**: 22 of
the 46 sections listed as having headroom were already saturated.

## 9. The deduplication test — the rule that governs all drafting

Run **per verse, immediately before drafting that verse.** Never in bulk, never from memory, never
from a cached list of headings.

1. **Read the verse text** from `translation/{{NNN}}.txt`.
2. **Extract every existing bold mini-heading** for that verse from `expanded/{{NNN}}.md`.
3. For each candidate new heading, **grep the section body for every citation that heading depends
   on** — each `S:V` reference and each key term.
4. **If the sources are already quoted in the section, the heading is a citation upgrade to an
   existing head, not new depth. Drop it.**
5. If *every* candidate heading is already carried, the section is saturated: **remove it from the
   Tier-1 list, leave it in the standard band, and log the removal with the reason.**
6. Never propose a heading for content the verse does not contain. Verify the word or phrase the
   heading is about actually appears in that verse.

Two corollaries that saved the most time on 007:

- **Count concordances from `translation/`, never from a summary or a cached list.** Grep the actual
  files. On 007 a plan claimed a verdict-word occurred seven times including a verse that did not
  contain it; the true count was six. Another claimed an expulsion threat at a verse that was
  actually about Iblīs's respite. A third claimed a root ran through three verses when one of them
  was an unrelated simile. A fourth listed a verse that was not an instance and omitted one that was.
- **A heading already drafted in another section is cross-section duplication, not depth.** Where a
  harmonisation belongs naturally at two verses, draft it once, at the verse where it does the most
  work, and let the other verse cite it.

The payoff for running this test honestly is that it also *finds* material: on 007 it surfaced the
sūrah's fourth verse announcing the whole destruction pattern in one clause, the fact that only one
verse in the entire Qurʾān records Satan swearing, and that the tree of the fall is never identified
anywhere except in the tempter's own advertisement.

## 10. Style prohibitions the gates measure

- **Tics ≤ 4.0 per 1,000 words; target near zero** (007 achieves 0.19). Banned: `it is worth noting`,
  `worth noting`, `it is important to note`, `important to note`, `it should be noted`,
  `it must be noted`, `in other words`, `that is to say`, `the point is`, `the fact is`,
  `as we have seen`, `as has been seen`, `as noted above`, `it is no accident`, `not an accident`,
  `needless to say`, `it goes without saying`, `to be sure`, `at the end of the day`, `in a sense`,
  `in a way`, `so to speak`, `it is clear that`, `it is obvious that`, `this is the reason why`,
  `the reason for this is`.
- **Chains ≤ 1.5 per 1,000 words; target near zero** (007 achieves 0.12). Banned shapes:
  `is the X that is`, `of the X of the`, `the X is the Y of the`. These are scored on prose with
  quotations stripped, so quoting scripture does not mask them and cannot excuse them.
- **Duplicate 10-gram fraction ≤ 0.10** within a section; target ~0.06.
- **Zero sentences of 12+ words repeated verbatim** anywhere else in the file. Scripture and ḥadīth
  quotations are excluded from this check, so anything it flags is recycled commentary prose.
- Short readable paragraphs. Every mini-heading unique and specific to the argument that follows it —
  never a template reused across verses, never decorative, never a heading that could sit on any
  section.
- Scholarly but plain. No sensationalism, no fictional dramatisation, no novelistic writing, no
  exaggeration.

## 11. Three defect classes no surviving gate detects

These were enforced by tools that have been removed (§16). The rules survive and you must run them
yourself, with throwaway inline scripts that you do not commit.

### 11.1 Off-topic drift

The echo test in §3.3. Zero sections below 15% echo of their own translation's distinctive
vocabulary.

### 11.2 Recapitulation blocks

A mini-heading block whose content restates its own section is a recap, however well written.
Detected by reading, and by checking whether a block's claims appear in the blocks around it. The
repair is removal of the block — but under §1.3 you may only remove material you added in this
session, so for pre-existing recaps, note them in the plan document and leave them.

### 11.3 Leaked drafting scaffolding

The author's own deliberation left in delivered prose. **No other checker flags this, because the
text is well-formed Markdown about the right verse** — it was found on 007 only by direct reading.
Scan the whole file for:

- self-correction left in place ("actually", "on reflection", "I said above that", "to restate")
- citation-hunting ("we need a source for", "verify before", "TBD", "TODO", "FIXME", "XXX")
- planning artifacts ("this section will", "the next head covers", "draft:")
- the `[System Memory Check]` trailer from `system_instructions.md` §6.4

Distinguish **GENUINE** defects from **QUOTED** occurrences of the same surface forms inside
scripture or a character's speech — `Let me kill Moses` is Pharaoh's words at 40:26, and
`Say: 'Wait — we too are waiting'` is 6:158. Those are not defects. Print each hit with surrounding
context and judge it; do not count hits automatically.

Target: **zero genuine hits.**

## 12. The gates — commands, thresholds, pass criteria

### 12.1 The four mandatory gates, run after every batch

```
python3 tools/quran-audit/check_filler.py --sura {{N}} --band 1200-1400
python3 tools/quran-audit/check_cross_quotes.py {{N}}
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/census.py --sura {{N}}
```

| Gate | Measures | Pass criteria |
|---|---|---|
| `check_filler.py` | depth band per section; tics/1k; chains/1k; duplicate 10-gram fraction; sentences of 12+ words repeated verbatim in-file | **FAILING 0**, below 0, above 0; tics ≤4.0, chains ≤1.5, dup ≤0.10, repeated sentences 0 |
| `check_cross_quotes.py` | every quoted span carrying an `S:V` citation, checked against `translation/SSS.txt` | **DRIFT 0, ELLIPSIS 0, VICINITY 0, NOVERSE 0**; every cited span EXACT |
| `validate.py` | canonical skeleton, all 114 files | **PASSED 114/114, FAILED 0** |
| `census.py` | corpus depth distribution and duplication ground truth | 0 sections below 260 words, 0 below 400 |

`check_filler.py` flags: `--band LO-HI`, `--max-tics` (default 4.0), `--max-chain` (default 1.5),
`--max-dup` (default 0.10), `--max-repeat` (default 0), `--sura N`, `--all`, `--json OUT`, `--show N`.
It reports and never edits; exit status 1 when any checked section is outside the band or above a
threshold, so it works as a gate.

`check_cross_quotes.py` classes: **EXACT** (verbatim substring of the cited verses), **PARTIAL**
(shorter than the verse but every kept word verbatim — treated as EXACT), **ELLIPSIS** (verbatim
apart from explicit ellipsis gaps), **DRIFT** (some word is not in the cited text), **NOVERSE** (the
citation resolves to nothing — a bad reference), **VICINITY** (the citation is explicitly qualified,
so it is not presented as verbatim). Ḥadīth quotations and quotes with no Qurʾānic citation are
skipped and reported as UNCITED; on 007 that is 345 spans, which is normal.

### 12.2 The optional fifth gate

```
python3 tools/quran-audit/check_translations.py --sura {{N}}
```

Reports sections whose blockquoted translation matches **neither** `initial/` nor `translation/`
above its threshold — which indicates a cross-sūrah substitution rather than a register variant.
There are **7 pre-existing flags corpus-wide that are known and ignored**; investigate only new ones
for your chapter. If a section is flagged, `diagnose_sections.py` used to find the best-matching
verse anywhere in `initial/` + `translation/` to confirm whether it was a substitution — that tool is
gone, so do the lookup directly.

### 12.3 The three manual checks from §11

Run these once before the final commit, and again after any large batch:

- echo test (§3.3) — zero sections below 15%
- recap scan (§11.2)
- scaffolding scan (§11.3) — zero genuine hits

Write each as an inline script through a bash heredoc. **Print the number of sections examined and
treat `examined: 0` as a failure.**

### 12.4 Utility for own-verse quotations

```
python3 tools/quran-audit/align_own_verse.py report {{N}}
python3 tools/quran-audit/align_own_verse.py report {{N}} --json /tmp/c.json
```

Proposes replacements for inline quotations of a section's **own** verse that still use the older
`initial/` rendering. For every matching block above its minimum word count that is absent from the
new rendering, it aligns old and new word-by-word with `difflib` and proposes the covering span of
the new rendering, outputting a JSON candidate list plus a readable report showing the carrying
sentence — so each candidate can be accepted, edited or rejected before anything is written. It
proposes; it does not apply. Review every candidate: on 007 the alignment pass covered 68 drifted
sections, and the user's decision was to align **all** of them, not a subset.

### 12.5 What the gates do not cover

No gate checks factual accuracy, correct attribution of a ḥadīth, whether a scholar's position is
represented correctly, or whether an argument is sound. Those are your responsibility and the reason
web verification is authorised. The gates check form, sourcing and padding — nothing else. A file can
pass all four and still be wrong.

### 12.6 Git recovery, without force-pushing

If a push is rejected because the remote has moved, or if the local history has been truncated:

1. `git fetch origin <branch>`
2. Inspect `FETCH_HEAD` before touching anything — confirm it is the commit you expect.
3. `git reset --mixed FETCH_HEAD` — this **preserves the working tree** and re-points the branch.
4. Check `git status`; re-commit only the files you intended.
5. Push; it will fast-forward.

Never `git reset --hard`, never `git clean`, never force-push. Local history truncation has happened
once on this repository already, and the recovery above lost nothing.

## 13. The execution loop

Work in batches of **8–12 verses**. Per batch:

1. Read the batch's verses from `translation/{{NNN}}.txt`.
2. Extract each section's existing mini-headings and body word count from `expanded/{{NNN}}.md`.
3. Run the §9 dedup test on each. Decide: add heads, or demote the section out of Tier-1.
4. Fetch **every** quotation you intend to use, verbatim, from `translation/` — all of them, in one
   step, before writing any prose.
5. Write the additions with a Python script run through a bash heredoc. The script must:
   - key insertions by **string** verse numbers (`'44'`), not integers;
   - insert each block immediately **before the section's closing `---`**;
   - apply insertions from **highest file offset to lowest**, so earlier positions do not shift;
   - print a dry-run projection of before/after word counts against the ceiling first;
   - write the file only under an explicit `--apply` flag;
   - open files with an explicit `'w'` mode.
   **Never re-run a script that has already been applied** — it duplicates every block. Fixes after
   an apply go directly into the file.
6. Run the four gates (§12.1). Fix every failure. Re-run until all four are clean.
7. Commit with a message stating: sections touched; word counts before and after; heads added; heads
   struck as duplicates with the reason; sections demoted; and the four gate results.
8. Push to the session branch. Go to the next batch.

Scratch scripts go in `/tmp/` via bash heredoc; the file-writing tool is workspace-scoped and cannot
reach `/tmp/`.

## 14. Configuring `check_filler.py` for this chapter

The Tier-1 machinery currently holds 007's lists. Extend it for chapter `{{N}}` without breaking 007:

- Keep `TIER1_FLOOR = 1400`, `TIER1_CEILING = 1800`, `DEEPEST_CEILING = 2100`, `REDUCED_FLOOR = 700`.
- Add this chapter's `DEEPEST` and `TIER1` verse keys, and its `SHORT_VERSE` entries with a written
  reason each. Key them so 007's entries are untouched — either generalise `depth_floor` and
  `depth_ceiling` to consider the chapter, or add parallel sets.
- **After editing, confirm 007 is unchanged**: `check_filler.py --sura 7 --band 1200-1400` must still
  report 277,675 words, FAILING 0, reduced-floor 18; and `check_cross_quotes.py 7` must still report
  1,780 EXACT.
- The summary line's `reduced-floor` figure counts floors **below** the band floor. Raising a floor
  must not silently inflate it — that bug existed and was fixed; do not reintroduce it.
- `depth_floor(key, lo)` returns `REDUCED_FLOOR` for `SHORT_VERSE` members, `TIER1_FLOOR` for `TIER1`
  members, and the band floor otherwise. `depth_ceiling(key, hi)` returns `DEEPEST_CEILING` for
  `DEEPEST`, `TIER1_CEILING` for `TIER1`, and the band ceiling otherwise.

## 15. Pre-decided answers — never ask, just apply these

| Situation | Decision |
|---|---|
| Unsure whether a heading is genuinely new | If its citations are already in the section, drop it |
| Unsure whether a verse is Tier-1 | If it carries a ruling, a divine attribute, or a repeated formula, yes |
| Section saturated but below 1,400 words | Demote it out of Tier-1; **never pad it** |
| Ḥadīth number unverifiable after one search | Attribute to a named exegete as tradition, or drop it and quote the Qurʾān |
| Over the ceiling | Trim the newest head; never an existing one |
| Two candidate heads make the same point | Keep the stronger, drop the other |
| A harmonisation fits two verses equally | Draft it once where it does most work; the other verse cites it |
| Verse is 14 words or fewer | Check whether it is a fragment; only then consider the reduced floor, with a written reason |
| Two English words compete for one Arabic term | Use the one `translation/` uses (§3.2) |
| `translation/` and `initial/` disagree | `translation/` wins, always, for both text and vocabulary |
| A plan, summary or memory conflicts with `translation/` | `translation/` wins, always |
| A gate reports zero failures but examined zero sections | Treat as failure; fix the check |
| `normalize.py` was run | Apply the §5.4 checklist before trusting any green gate |
| An existing section has a recap or scaffolding leak | Log it in the plan document; do not delete pre-existing prose |
| The chapter is long or the run is taking many steps | Continue. Never checkpoint with the operator, never split the work, never end the turn with verses outstanding |
| `expanded/{{NNN}}.md` is missing or has fewer sections than the chapter has verses | Build the missing sections from `initial/{{NNN}}.md` in the canonical skeleton (§5). Do not report the gap and wait |
| A verse has no source note in `initial/` | Write it from the verse itself with cross-references quoted from `translation/`, document the lower floor, and continue (§21.5) |
| `initial/{{NNN}}.md` is thin for this chapter | Match depth to what the source supports and document it; never pad to a number (§21.5) |
| A ḥadīth number conflicts across the corpus | Correct only where the corpus is unanimous; otherwise record the variance and move on (§22.3) |
| You find a defect no gate covers | Fix it under §21–§23 and log it. Ungated defects are the normal case, not an escalation |
| `git push` or a pull-request call fails | Commit locally, note it in one line of the final report, and finish everything else |
| You are tempted to post progress or ask whether to continue | Do neither. One report, at the end (§24) |
| You wonder whether scope extends to another chapter | It does not. Chapter `{{N}}` only; the sole exception is leaving 007's gate lists intact (§14) |
| Anything else ambiguous | Choose the option that adds sourced scholarship and needs no user input, then move on |

## 16. The removed tools, and the rules they leave behind

The repository once carried **133 audit and one-off scripts** in `tools/quran-audit/`, plus 4 stale JSON
run outputs and 218 generated rewrite artifacts. All but seven scripts were deleted, on the principle
that **only the gates that measure the standard belong in the repository**; everything else
was a single-use instrument whose rule is now written down instead of coded. This matters to you for
one reason: three of them enforced defect classes that no surviving gate detects (§11). Know what is
gone so you do not assume it is being checked.

**Surviving (7):** `validate.py`, `check_filler.py`, `check_cross_quotes.py`, `check_translations.py`,
`census.py`, `align_own_verse.py`, `normalize.py`.

### 16.1 The staged audit suite `a1`–`a12` (12 scripts, removed)

A corpus-wide audit pipeline, run in order, writing intermediates to `out/`. All twelve hard-coded
`ROOT='/home/user/new'`, which is itself the lesson — the surviving tools derive `ROOT` from
`__file__`, so they work from any checkout.

| Script | What it did |
|---|---|
| `a1_structure.py` | per-section structure scan: headings, verse numbers, ordering |
| `a2_extract_quotes.py` | extracted every quoted span in the corpus into `out/` |
| `a3_quote_match.py` | matched extracted quotes against `translation/` |
| `a4_window.py` | analysed the citation window following each quote |
| `a5_final.py` | assembled the final audit report from the intermediates |
| `a6_sheet.py` | emitted the audit as a spreadsheet |
| `a7_idf.py` | inverse-document-frequency scoring of section vocabulary — distinctiveness |
| `a8_range.py` | chapter length table against a hard-coded reference |
| `a9_salad.py` | "word salad" detection — prose with high word count and low topical signal |
| `a10_chain.py` | self-referential chain shapes, e.g. `is the X that is` |
| `a11_corrupt.py` | corruption and mojibake pattern scan |
| `a12_rank.py` | ranked sections by degeneracy so rewrites could go worst-first |

**Surviving coverage:** `a3`/`a4` → `check_cross_quotes.py`; `a10` → `check_filler.py`'s chain
metric; `a12` and the degeneracy half of `a9` → `check_filler.py`'s dup and repeated-sentence
metrics. **Not covered by anything now:** `a7` distinctiveness, `a9` word-salad, `a11` corruption.
Spot-check for mojibake and for sections whose vocabulary is generic rather than verse-specific —
the echo test in §3.3 catches most of the latter.

### 16.2 Superseded quote and citation checkers (removed)

| Script | What it did | Superseded by |
|---|---|---|
| `check_quotes.py` | first-generation quote verification against `translation/` | `check_cross_quotes.py` |
| `check_quotes2.py` | second generation, with normalisation of quotes and diacritics | `check_cross_quotes.py` |
| `classify_quotes.py` | classified quoted spans by type | `check_cross_quotes.py`'s six classes |
| `check_cites.py` | checked citation resolvability | `check_cross_quotes.py`'s NOVERSE class |
| `align_quotes.py` | aligned quotes to `translation/`, carrying a hand-maintained `MANUAL` set of **17 exception pairs** such as `7:21|7:68`, `7:23|4:111`
   and `7:103|30:56` | `align_own_verse.py`, which proposes from `difflib` alignment instead of a hand-maintained list |

The hard-coded exception list is why `align_quotes.py` was replaced: a manual list silently stops
covering new cases.

### 16.3 Degeneracy tooling (removed)

| Script | What it did |
|---|---|
| `check_degeneracy.py` | detected degenerate/repetitive generated prose and non-matching verse text |
| `repair_degen.py` | repaired 007's degenerate prose by stripping formulaic frames **without deleting content** |
| `novel_sentences.py` | scored each sentence of an inserted block for novelty against its own section |
| `strip_recap.py` | found and removed recapitulation blocks — mini-heading blocks restating their own section |
| `dupscan.json`, `last_degeneracy.json`, `last_classification.json`, `last_fixlog.json` | stale run outputs |

**Surviving coverage:** detection → `check_filler.py`'s dup and repeated-sentence metrics.
**Not covered:** the recap block (§11.2) and per-sentence novelty. The `repair_degen.py` principle is
worth keeping: repair degeneracy by stripping formulaic frames, never by deleting substance.

### 16.4 The three whose rules no gate enforces (removed) — see §11

| Script | What it did | Rule that survives |
|---|---|---|
| `check_offtopic.py` | corpus-wide sweep for sections whose body does not echo the distinctive vocabulary of their own translation; flagged below 15% echo | §3.3 — run it yourself |
| `check_scaffolding.py` | scanned for leaked drafting scaffolding, distinguishing genuine leaks from the same surface forms inside quoted scripture | §11.3 — run it yourself |
| `test_skeleton.py` | regression test for the two canonical-skeleton defect classes that every gate reported green while 107 of 114 files carried them | §5.3 and §5.4 — check both explicitly |

### 16.5 Structural fixers, one-pass (removed — the corpus is already clean)

| Script | What it did |
|---|---|
| `fix_headings.py` | normalised heading forms to the canonical skeleton, two defect classes |
| `fix_separators.py` | normalised horizontal rules to the canonical form taken from `expanded/001.md` |
| `fix_orphan_connectors.py` | removed bare-word connector lines stranded between two blockquotes (4 places corpus-wide) |
| `fix_translation.py` | replaced only the translation line of named sections, for cases where the commentary was correct but the translation line quoted the wrong rendering |
| `dequote_body.py` | removed a body's re-quotation of its own verse while keeping the Arabic |

If your chapter needs any of these, reimplement narrowly for that chapter, run it, verify with
`validate.py`, and do not commit the script.

### 16.6 Editing utilities and per-chapter one-offs (removed)

`section.py` (extract/replace a single verse section without touching the rest), `dump_section.py`
(print one section), `extract_source.py` (print verse text plus source commentary for a verse range),
`diagnose_sections.py` (for sections flagged by `check_translations.py`, find the best-matching verse
anywhere in `initial/` + `translation/` and test whether the section was a cross-sūrah substitution),
`apply_sections.py` (splice regenerated commentary into an `expanded/` file), `append_block.py`
(append a mini-heading block to existing sections), `block017.py` and `apply_026.py` (chapter
one-offs), `stop.py` (the shared stop-word list, reproduced in §3.3), and **94**
`content_NNN_*.py` per-chapter content modules for chapters 007, 011, 021, 026, 036, 037 and 040.

These are the pattern your §13 batch script follows: a module carrying the new content, and an
applier that splices it in. Write one per batch, keep it in `/tmp/`, do not commit it.

### 16.7 Generated artifacts and superseded documents (removed)

- `out/rewrites/007/` — **218** generated per-section rewrite drafts and batch artifacts, reproducible
  from the gates. `tools/quran-audit/.gitignore` now excludes `out/`; keep it that way.
- `AUDIT_EXPANDED.md`, `EXPANDED_FOLDER_AUDIT.md`, `REMAINING_ISSUES.md` — superseded audit
  narratives. **Their findings are now carried in this prompt**: the defect taxonomy in §21, citation
  and factual integrity in §22, measurement discipline in §23, and the pass sequence they imply in
  §19. Do not recreate corpus-wide audit narratives; write a per-chapter plan document instead (§24).

## 17. The two phases — measure first, then decide

Everything in §8 to §16 assumes a chapter that is structurally sound and merely needs depth. That was
007's state when its expansion began: 206 sections, a median of about 1,370 words each, duplication
and chain scores inside the gates. **Most chapters are not in that state, and 007 itself was not in it
when the work started.** verses 5 to 206 were redrafted first; the expansion that followed added only
7,149 of the file's 277,675 words.

Measure before choosing. Run, against the chapter exactly as it stands:

```
python3 tools/quran-audit/check_filler.py --sura {{N}} --band 1200-1400
python3 tools/quran-audit/check_cross_quotes.py {{N}}
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/census.py --sura {{N}} --dup 0.030
python3 tools/quran-audit/check_translations.py --sura {{N}}
```

Then decide:

| Finding | Phase |
|---|---|
| Median section ≥1,200 words, dup <0.030, chains <1.5/1k, zero DRIFT | **Phase 2 only** — go to §8 |
| Any section at duprate ≥0.030 on the census 'whole' span | **Phase 1** — §18.3 |
| Any section at ≥5 chain shapes per 1,000 words | **Phase 1** — §18.2 |
| Bodies that re-quote their own verse in English | **Phase 1** — §18.4 |
| Blockquote is the wrong verse, or matches neither source | **Phase 1** — §18.5 |
| Prose clean but median far below 1,200 words | **Phase 2**, expecting to author most of the band rather than add to it |

Chain shapes are counted per section as hits per 1,000 body words, sections ranked worst-first so
rewrites go in order of need. The four patterns:

```
C1  is the X that is
C2  the X is the Y of the
C3  of the X of the
C4  is in the form of the
```

On 007 the threshold for "this section must be rebuilt" was **≥5 chains per 1,000 words**.

**Phase 1 ends when all four gates are green and the three manual checks (§12.3) pass. Only then does
Phase 2 begin. Never interleave them** — regenerating a section after depth headings have been added
to it destroys that work.

These two phases sit inside a longer **nine-pass sequence** (§19). Regeneration is pass 2 of 9, not the
whole of Phase 1: structural normalisation comes before it, and re-sourcing, citation integrity,
gold-standard quoting, own-verse alignment and duplication clearing come after it and before
expansion. 007 needed all nine.

## 18. The regeneration pipeline

007's rebuild is the reference implementation. The module that rebuilt its four worst sections
described them as *"structurally valid and about the right verse, so no gate flagged them; they failed
on prose quality."* That is the situation this section exists for: a file that passes every structural
gate and is still unreadable.

### 18.1 Diagnose the defect class before choosing a repair

There are two, and they need opposite treatments.

- **Sentential degeneration** — machine-generated nominalisations recursing *within* a sentence. This
  was 007's defect, and it accounted for **39% of the words in its 100 flagged sections**. Repair by
  stripping frames (§18.2).
- **Structural recapitulation** — inserted blocks restating material elsewhere in the same section.
  This was 017's defect; block-vs-section overlap ran **0.05–0.31**. Repair by measured block removal
  (§18.3).

**The diagnostic that separates them:** run the sentential repair in dry-run. If it reports
`actions={'keep': N}` with nothing stripped, the duplication is **structural**, not sentential —
switch to §18.3. Choosing wrong wastes a pass and risks deleting good prose.

Degeneracy is scored as the **fraction of 10-gram tokens duplicated within the section**. Sections
under 80 words score 0.0 and are skipped, because there is not enough text to measure.

### 18.2 Sentential repair — strip frames, never scholarship

Three patterns, three repairs.

**(a) Framed kernels.** *"The logic of the vow is the logic that is worth stating: Iblis knows that the
straight path is the means of the salvation, and he attacks the means, not the end."* The clause after
the colon is real commentary. **Drop the frame, keep the kernel — recursively:** the kernel can itself
be a loop, in which case it goes too.

**(b) Pure loops.** *"...are the people who are in the state of the one who are the ones who are the
objects of the punishment of God the torment from the heaven."* No information content at any point.
**Delete — but guarded.** A sentence is deleted only if it matches a loop template **and** contains no
quotation mark, no verse citation (`\d{1,3}:\d{1,3}`), and no scholar's name (al-Ṭabarī, al-Rāzī,
al-Qurṭubī, Ibn Kathīr, al-Zamakhsharī and the rest of the list). The guard is what makes it
impossible for the repair to lose anything informative.

**(c) Framed openers.** *"The verse states the act of the people who did wrong, and the act is the act
that is the substitution of the word: <quote>."* The quotation must survive and the section must still
open. **Replace the frame with a plain lead-in, preserving the quote.**

**Governing principle: none of this rewrites scholarship. A section left too thin to stand is reported
for authoring, not padded.** Automated trimming that damages coherence was already tried on 017 and
rejected; the repair is deliberately narrower and touches only sentences that are already incoherent.

Measured duprates on 007 immediately before its worst four sections were rebuilt: **v206 0.200,
v141 0.145, v204 0.143, v137 0.118.** Record the before-and-after figures for every section you
rebuild.

### 18.3 Structural repair — measured block removal

The constants the tool used:

| Constant | Value | Meaning |
|---|---|---|
| `GATE` | **0.030** | census duprate at or above which a section is flagged |
| `MIN_WORDS` | **400** | a section is never left below this by a removal |
| `NGRAM_OVL` | **5** | content-word shingle size for block-vs-block overlap |
| `OVERLAP_MIN` | **0.30** | a block this redundant is a recap candidate |

A recap block is a mini-heading block whose content substantially restates other blocks in the same
section. It typically sits near the end, often re-quotes verses or ḥadīth already quoted above it, and
often sits under a heading that paraphrases an earlier heading.

**The scoring rule is non-negotiable:** every duprate is computed on the census **'whole'** span —
section heading through body, trailing rule dropped. `census.py` carries an explicit warning that a
body-only span gives materially different counts, **151 versus 269 sections at the 0.030 gate**, and
must not be substituted silently. An earlier version of the tool scored joined block bodies only,
which excluded the verse-translation line, and consequently found **zero** flagged sections in files
census reported **30** in. If your sweep reports zero where census reports some, your span is wrong —
fix the span, do not accept the zero.

**Removal is measured, never guessed.** For each flagged section, remove the smallest set of
highest-overlap blocks that (a) brings the census duprate under the gate **and** (b) leaves at least
`MIN_WORDS` words — so a duplication defect is never traded for a depth defect. Before deleting any
block, report its **novel sentences**: content found nowhere else in the section. Anything worth
keeping must be visible before it goes.

Why that discipline matters, measured on 017: the 29 sections still over the gate were **not**
degenerate prose. Each carried an inserted block that restated part of its section *while also adding
material* — the blocks held **11,577 words, of which 1,129 content words appeared nowhere else in
their section**. Bulk deletion would have destroyed real scholarship. The correct treatment: **remove
the block and fold its genuinely novel sentences into the mini-heading they belong under.**

### 18.4 The own-verse re-quote — the largest single cause of duplication flags

The defect construct, appearing in the body directly below the section's own blockquote:

```
<lead-in>: *"<English text of the verse>"* (*<Arabic transliteration>*).
```

The English half duplicates the `> **translation**` line immediately above it. Measured corpus-wide:
**1,302 sections contain such a re-quote, and 135 of the 172 sections over the 0.030 gate were over
it because of this construct alone.** The test that proved cause rather than correlation: removing the
translation line from the measured span dropped 010.md from **30 flagged sections to 0**, 034.md from
**8 to 0**, and 039.md from **16 to 1**.

`expanded/001.md` — the user-confirmed reference, never to be modified — **does not do this**. Its
longest verbatim overlap between a section's verse and its own body is 30–40 characters of incidental
phrase, against 60+ characters systematically elsewhere. So the construct is a **deviation from the
reference, not a house convention**, and removing it moves the corpus toward 001 rather than away
from it.

**The fix removes only the English and keeps the Arabic transliteration**, because the transliteration
duplicates nothing and appears nowhere else in the section — deleting it would trade a duplication
defect for a loss of real scholarship. The colon that introduced the quotation is cleaned up with it.

### 18.5 A wrong translation line — swap the line, never the section

Where a section's commentary is correct but its blockquote is a different verse, **rewriting the whole
section would destroy good prose**. Replace the single `> **…**` line from `translation/{{NNN}}.txt`
and leave the commentary untouched. `check_translations.py --sura {{N}}` finds these: it reports
sections whose blockquote matches **neither** `initial/` nor `translation/` above its threshold, which
indicates a cross-sūrah substitution rather than a register variant. For each hit, find the
best-matching verse anywhere in `initial/` + `translation/` to confirm what happened before swapping.

### 18.6 The module-and-applier pattern

Regeneration is never done by editing the file by hand. The new prose is written as **data in a Python
module** and spliced in by an applier. Two appliers, two contracts.

**Full-section replacement** — `apply_sections.py <sura_no> <module.py> [<module2.py> …]`:

```python
SURAH   = "al-Aʿrāf"        # must match the file's H1 name exactly
NUM     = 7
SECTIONS = {
    verse: (translation_or_None, [(mini_heading, [para, ...]), ...]),
}
```

`translation_or_None`: **`None` keeps the existing translation line**; a **string replaces it** — that
is how a wrong verse text is repaired in the same pass (§18.5).

**Additions only** — `append_block.py <sura_no> <module.py>`:

```python
SURAH, NUM
BLOCKS = {verse: (mini_heading, [para, ...])}
```

Inserted at the end of the section body, before the trailing separator, existing content untouched.
**This is the contract Phase 2 uses** (§13).

Both appliers must derive the repository root from `__file__`. A hard-coded absolute root silently
retargets the real corpus when the tool is run from a copy — every script in the deleted `a1`–`a12`
suite hard-coded it, which is one reason none of that suite survived.

Keep modules and appliers in `/tmp/`; do not commit them. 007's rebuild and the work on six other
chapters used roughly 94 such content modules.

### 18.7 Rebuild from the source apparatus, in the target register

A regenerated section is rebuilt **from the apparatus in `initial/{{NNN}}.md`** — its scholarly notes,
reports and observations — with every word of scripture taken from `translation/{{NNN}}.txt` and every
term rendered in the translation's own vocabulary (§3.2). Record in the module's docstring the
measured duprates that justified each rebuild, so the decision stays auditable.

The target register is what 007's redrafted sections read like. Each carries, in roughly this order:
the mini-heading naming the argument; the Arabic clause transliterated, with its root and its
grammatical construction identified — *"Mā kāna … illā is a restrictive construction: the whole of
their speech was nothing but that one clause"*; the lexical range of the key word, including its
pre-Qurʾānic usage — *"daʿwā meant a claim in the market and the courtroom of the Arabs, the assertion
a man entered on his own behalf"*; the theological point that follows **from** the grammar rather than
being asserted beside it; cross-references quoted verbatim with their citations; and a closing
sentence stating what the verse does, not summarising what was just said. No recaps, no framing
sentences, no hedges.

### 18.8 Artifacts

Draft each section as its own markdown file and assemble batch files before splicing. 007 used
`out/rewrites/007/`: per-section drafts `b05.md` through `b206.md`, plus nine batch files covering
verses 5–9, 10–13, 14–18, 19–35, 36–54, 55–79, 80–104, 105–154 and 155–206 — the whole chapter. Keep
them under `out/`, which `.gitignore` excludes: they are working drafts, not deliverable, and the
merged repository deliberately carries none of them.

### 18.9 End of Phase 1

Phase 1 is complete when all of the following hold: the four gates are green (§12.1); census reports
zero sections at or above the 0.030 duprate on the 'whole' span; no section exceeds 5 chains per 1,000
words; the echo test (§3.3) finds nothing below 15%; the scaffolding scan (§11.3) finds nothing
genuine; the recap scan (§11.2) finds nothing; and every blockquote is verbatim from
`translation/{{NNN}}.txt`.

Log in `DEPTH_PLAN_{{NNN}}.md` every section rebuilt, its before-and-after duprate, what was removed
and under which guard, and every novel sentence folded back in. Then start Phase 2 at §8.

## 19. The full pass sequence — everything that was done to 007

007 did not go from source file to deliverable in one step. It went through **nine ordered passes**,
and each one fixed a class of defect the previous pass could not see. A new chapter needs the same
sequence. Do not skip passes because the chapter looks clean — 007 looked structurally clean at every
stage and still needed all nine.

| # | Pass | What it fixes | 007's measured effect |
|---|---|---|---|
| **0** | **Audit** | Establishes what is actually wrong, by measurement | Found 007 was *"the single largest quality failure in the folder"*: ≈120,000 of ~160,000 words (**≈75%**) carried ≥5 template chains; a stricter paragraph test put **48.8%** of the file as degenerate filler; **168 of 206 sections** had no ḥadīth or book citation of any kind; median section **730 words** |
| **1** | **Structural normalisation** | Stray rules, non-canonical headings, malformed bold, orphan connectors | Corpus-wide: **219 illegal horizontal rules** in 107 files (134 duplicate, 85 internal) and **11 non-canonical H2s** in 10 files → 0, with **zero content change** (126,667 fingerprinted content lines identical before and after) |
| **2** | **Regeneration** (§18, §20) | Degenerate, looped, templated prose | **All 206 sections rewritten** in ten instalments; 7:5–7:206 came to **200,150 words** inside a 900–1,100 band; chains to **0 per 1,000 words** |
| **3** | **Translation re-sourcing** | Blockquotes carrying the wrong or archaic wording | **205 of 207 blockquotes replaced** so that every one is byte-exact against `translation/007.txt`; **zero** left matching `initial/` wording |
| **4** | **Citation integrity** (§22) | Non-existent verse numbers, wrong ḥadīth numbers, drifted quotation wording, unverified counts | `(21:119)` — a verse that does not exist — removed from two places; **129 quotations across 33 drafts** re-worded to the repository translation; a five-gram matcher then reported **0 non-existent references and 0 wording divergences across 286 checked citations** |
| **5** | **Gold-standard quote pass** (§6) | Hedges, ellipsis spans, paraphrase inside quotes | The regeneration drafts contained **66 `cf.` and 68 `vicinity`** instances; the deliverable contains **zero**. Final state **1,780 EXACT spans, 0 DRIFT, 0 ELLIPSIS, 0 VICINITY** |
| **6** | **Own-verse alignment** | Inline quotations of a section's own verse drifting from the blockquote | **68 sections** re-aligned to `translation/007.txt`; **2,125 spans** checked |
| **7** | **Duplication clearing** (§18.2–18.4) | The three distinct duplication classes | **100 sections over the gate** → 0 at ≥0.030; 007 had held **seven of the eight worst sections in the corpus**, and 52 were still flagged after mechanical clearing |
| **8** | **Expansion** (§8–§16) | Depth below the band | **+7,149 body words** over ten tranches; 25 Tier-1 sections drafted, 22 demoted, 1 promoted in |

Measured end to end, pass 2 through pass 8 took the file from **204,702 words to 282,755** (raw), and
retention analysis shows a **median of 91.2% of the original prose sentences surviving** into the
deliverable, with no section below 65.7%. That is the shape of a correct job: the regeneration
replaced what was broken, and everything after it preserved what was sound. If your retention figure
is near zero, you have destroyed scholarship; if it is near 100% and the gates were failing, you have
done nothing.

**Passes 0 and 1 come before regeneration for a reason.** A degenerate file also carries structural
artifacts, and rebuilding prose on top of stray rules and duplicated headings just re-buries them.
`normalize.py` is idempotent — running it over the whole corpus wrote **0 files** at the end — so it is
safe to run first and again at the end.

**The order of 3 before 5 matters.** Re-source the blockquote from `translation/` *first*, then enforce
verbatim quoting. Doing it the other way means re-checking every quote twice, because the authority
changed underneath it.

## 20. The 007 regeneration record

This is what actually happened in pass 2, instalment by instalment, because the sequence of problems is
the sequence a new chapter will hit.

| Instalment | Verses | Sections | What the record shows |
|---|---|---|---|
| 1 | 7:5–7:9 | 5 | 655–709 words each, 0 chains/1k. An **invented etymology** — root *ʿajāh* given for *daʿwā* — was caught and removed. Ḥadīth numbers supplied: Muslim 2747; al-Bukhārī 1413 / Muslim 1016; al-Tirmidhī 2417 + al-Dārimī 554; al-Tirmidhī 2639 |
| 2 | 7:10–7:13 | 4 | 837–993 words. Four **wrong citations in the old text** corrected (16:35, 35:27, 43:7, 28:78); 26 verified cross-references added |
| 3 | 7:14–7:18 | 5 | 754 → 986 words **after a top-up**. The invalid `(21:119)` in 7:18 fixed to 7:156. Two **garbled Arabic roots** — *ḍ--ḍ* and *ṭ-rḍ* — corrected to *madhʾūman* (dh-ʾ-m) and *madḥūran* (d-ḥ-r) |
| 4 | 7:19–7:35 | 16 | 827–1,054 words. Installed with `section.py putbody`. **7:25 was verified clean and left untouched.** A draft artifact — the literal string `(2:139? no)` — was **intercepted in the 7:29 draft before install** |
| 5 | 7:36–7:54 | 19 | 876–1,350 words. The **last** invalid `(21:119)`, in 7:49, removed and confirmed by grep. Ten ḥadīth numbers verified live; two corrected (al-Bukhārī 7145 → **7257**; 6556 → **3245**); a loose paraphrase replaced with verbatim 16:25; a misattributed gloss replaced with verbatim 75:20–21 |
| 6 | 7:55–7:79 | 25 | 923–1,091 words. The sūrah's second narrative cycle — Noah, Hūd, Ṣāliḥ, Lot, Shuʿayb — supplied with the repository translation's wording for every quotation |
| 7 | 7:80–7:104 | 25 | **7:90–7:94 had to be re-anchored**: the first drafts were built on 23:33–38 / 11:88 material, i.e. the *wrong verses*, and were replaced. Twelve reference corrections. Then the **fidelity sweep**: 129 quotations across 33 drafts re-worded to `translation/` |
| 8 | 7:105–7:154 | 50 | Batches K–T. All 50 inside 900–1,100 words, and the whole repaired range 7:5–7:154 brought inside the band in the same pass |
| 9 | 7:155–7:206 | 52 | Batches U–AB. Sūrah complete: 200,150 words across 7:5–7:206. A dedicated five-gram verbatim matcher checked every citation against `translation/` and corrected 16 drifted quotations plus one reference (5:63 → 5:62–63). A **counting claim** — §7:103's "roughly one hundred and thirty times" — was corrected to the measured figure: Moses appears **178** times in `translation/` |

### 20.1 The four failure modes this record exposes

1. **Invented scholarship.** A root that does not exist (*ʿajāh* for *daʿwā*), garbled consonantal
   skeletons (*ḍ--ḍ*), a citation to a verse number the sūrah does not have (21:119 — Sūrah 21 has 112
   verses). **Aggravating:** 007 is the commentary *on al-Aʿrāf itself*, and it misattributed that
   sūrah's own most famous verse (7:156) to a non-existent 21:119 **twice**, while six other files
   cited 7:156 correctly for the same words.
2. **Drafts built on the wrong verse.** 7:90–7:94 were structurally perfect and about different
   verses. Nothing in the file could reveal it; only reading the body against its own heading did.
3. **Drafter's wording instead of the repository's.** 129 quotations across 33 drafts. The drafter
   paraphrased scripture from memory in a plausible register. This is the single most common defect and
   it is invisible to any gate that checks structure.
4. **Drafting debris left in the file.** `(2:139? no)`, `(46:17 hedge dropped)`, self-correction
   monologue. Caught by reading drafts *before* install, not after.

### 20.2 The applier that was actually used: `section.py`

§18.6 describes the two content-module appliers. The 007 regeneration used a third, simpler tool,
because it was replacing existing sections rather than splicing in generated data:

```
section.py get 007:18                  # print the section
section.py get 007:18 out/18.md        # write it to a file
section.py put 007:18 out/18.md        # replace the WHOLE section from a file
section.py putbody 007:18 out/18.md    # replace only the BODY, keeping heading + blockquote + marker
section.py put 007:18 out/18.md --dry  # show what would change
```

A section runs from its `## Sūrah … C:V` heading up to (not including) the next `## Sūrah` heading.
`put` preserves the original heading and surrounding `---` separators; the replacement file's own
heading is ignored. `putbody` splits the section at the `**Expanded Commentary**` marker, keeps
everything up to and including that marker, strips `---` lines and trailing blanks from the new body,
and keeps the trailing separator.

**Use `putbody`, never `put`, for a body-only draft — and the incident that proves it.** Two
full-section drafts (`07_07.md`, `07_13.md`, which carry their own `## Sūrah` heading and blockquote)
were installed through `putbody`. The result duplicated the heading and blockquote *inside* the
section body. The duplicate header blocks had to be excised, both sections reinstalled from body-only
drafts, and the file re-verified at exactly 206 sections with no missing verse. **This is why two
artifact series exist in `out/rewrites/007/`:** `07_NN.md` files are full-section drafts (verses 5–18)
and `bNN.md` files are body-only drafts (verses 5–206). The body-only series is the one that was
installed. Match the draft format to the applier.

### 20.3 The band during regeneration was 900–1,100 words, not the depth band

Every instalment was brought inside **900–1,100 words**. The 1,200–1,400 / 1,400–1,800 / 2,100 bands
of §4 are the *expansion* target and were set later. Do not try to hit the expansion band during
regeneration: the job of pass 2 is to make the prose sound, and a section that is 950 words of real
scholarship is a success at that stage. Passes 3–7 add words incidentally; pass 8 adds them
deliberately.

### 20.4 Sections that were verified clean were left untouched

7:25 was inspected, found clean, and **not rewritten**. Do not regenerate a section because it is in
the range being regenerated. Inspect each one; a clean section that gets rebuilt loses whatever was
right about it. The same discipline appears in the duplication work: `dequote_body.py` was applied
**only to sections already over the gate** — 1,167 sections containing the same construct but passing
were deliberately left alone, because normalising them was a larger stylistic change nobody asked for.

## 21. The defect taxonomy — the ten groups

The corpus audit classified every defect it found into groups A–J. A new chapter should be checked
against all ten, because each needs a different treatment and two of them need *no* treatment at all.

| Group | Defect | Treatment |
|---|---|---|
| **A** | **Content depth.** 007's median was 730 words. Corpus-wide, 198 sections under 260 words and 524 under 400 of 6,236 | Expand from the apparatus in `initial/`. **Groundability first:** 409 of 410 thin sections had source material; only `026.md` v110 had none |
| **B** | **Repetitive prose.** Three separate classes, each needing a different tool — see §18.1 | Diagnose, then §18.2 / §18.3 / §18.4 |
| **C** | **Misaligned bodies** — the commentary describes a different verse than its heading | **Read it. No tool works.** See §21.1 |
| **D** | **Detector false positives** | Document, do not "fix". See §21.2 |
| **E** | **Verified benign** (register variants) | No action. 007's contribution: 7 translation flags corpus-wide, all register variants, none a wrong-verse substitution, none altered |
| **F** | **Stylistic outlier** | Leave by decision. `045.md` runs 6.17 emphasis runs per 1,000 words against a corpus norm near 1; translations exact; left alone as the file's own style |
| **G** | **Structural artifacts** — stray rules, extra H2s | `fix_separators.py`, `fix_headings.py`, hardened `validate.py`, `test_skeleton.py` |
| **H** | **Inserted blocks** restating their own section | `strip_recap.py` + remove-and-test. **Never bulk-delete** |
| **I** | **Orphan connector lines** — a bare `and` stranded between two blockquotes | `fix_orphan_connectors.py`; `validate.py` now gates the class |
| **J** | **Inconsistent ḥadīth citation across files** | See §22.3 — recorded, not harmonised |

### 21.1 Group C is the class no tool can find

`037.md` had 61 verse headings at baseline and 182 after `normalize.py` promoted **21,326 words of
unheaded prose into 121 new verse headings**. The translation lines were corrected, but the bodies
were never realigned against their headings. Result: v62's body discussed *man ʿaṣaynā al-rasūl*
(33:66–67 content) under a heading about the tree of Zaqqūm; v182's discussed "We have preferred some
of them over others" (2:253) under a heading about Jonah.

The common shape is an **offset** — the body describes an adjacent verse, as though the unheaded prose
had been sliced against the wrong heading boundaries. v74 describes v75, v75 describes v76, v83
describes v84, v107 describes v105, v109 describes v107, v127 describes v130, v143 describes v146.

**Five automated metrics were built against this defect and all five failed validation:**

1. 4-gram exact match — 0.0% everywhere, no signal.
2. Paired "own note vs best other note" — claimed 67% of `037.md`, but a **control run flagged 46% of
   `011.md` and 62% of `040.md`, both verified clean**. A metric that fires on clean files is not a
   metric.
3. Transliteration-absent — matched the literal string `**Expanded Commentary**` in all 182 sections.
4. A stemming patch to `check_offtopic.py` — raised corpus flags from 11 to 45 and introduced false
   positives into previously-clean files.
5. Quote-owner lookup by token overlap — degenerate: verse 37:58 ("Are we then not to die,") has a
   single token longer than three characters, so it scored 1.00 against any quote containing "then",
   producing four impossible matches.

`check_offtopic.py` catches only bodies that *under-echo* their own translation; a body can describe
the wrong verse while echoing enough vocabulary to pass. It found 7 of these 39. **Reading every
section's opening prose against its own verse translation is the only method that worked**, and it
bounded an "unbounded" problem at 32 sections, all rebuilt.

Where several sections share one source note (a range marker covering verses 124–128, say), write each
on a **different portion** of that note. Repeating it is the verbatim-repetition failure that broke the
duplication gate twice in one batch. The resulting commentary then speaks to the passage rather than
the individual verse — which is the correct treatment when that is what the source provides, not a
compromise.

### 21.2 Groups D and F: what not to fix

Four off-topic flags survived corpus-wide and all four were read and confirmed as **detector
artifacts**: `018.md` v75 quotes its verse in Arabic transliteration rather than English; `026.md`
v132's verses have **no commentary note in `initial/` at all**, so there is no source vocabulary to
echo; `026.md` v176 misses only because the body says *message* where the verse says *messengers*;
`067.md` v10 is pure inflection ("had we **listened**… **understood**" against "**listening** and
**understanding**"). The detector is lemma-blind and cannot read transliteration.

Two real bugs were found in the *detector*, not the corpus, and both are worth knowing:

- A stemming patch was tried and **rejected** — it raised flags from 11 to 45.
- `body_lines()` dropped entirely-bold lines as headings, so **mini-headings carrying the verse's own
  vocabulary were excluded from the body**. `040.md` v3's headings are literally "Forgiver of Sin",
  "Accepter of Repentance", "Severe in Retribution", "Possessor of Bounty" — the exact words of the
  verse — yet it scored 12.5% echo, and 100% once headings were retained.

**Rule: when a gate flags a section, read the section before changing it.** Document detector
limitations rather than "fixing" clean prose to satisfy them.

### 21.3 What was tried and rejected — do not retry

- **Automated sentence-trimming** (Group H5a): cleared the duplication gate for 26 of 28 sections but
  **stranded mid-sentence antecedents** — removing a sentence left a pronoun or a "this" pointing at
  nothing. Reverted and deleted.
- **Bulk deletion of inserted blocks**: would have destroyed 97 of 017's 111 blocks, which carry
  original scholarship (overlap under 0.20). 017 was **misdiagnosed** as degenerate prose, and the
  prescribed treatment "same as 007.md, rebuild from `initial/`" was wrong and is explicitly marked
  *should not be reused*.
- **A 759-word floor** (Group H5c): withdrawn as a measurement artifact.
- **Harmonising ḥadīth numbers to a corpus plurality**: a guess dressed as a correction (§22.3).
- **An absolute 400-word floor on duplication repairs**: it would refuse to fix precisely the files
  that most need it. `039.md` and `034.md` are genuinely thin (42 of 75 and 37 of 54 sections already
  under 400 words before any edit), so the guard was made **relative**: block an edit only where it
  would push a section that *started* above the floor below it.
- **Stripping all of `014.md`'s flagged sections**: cleared 15 of 16 but cut the file from 16,087 to
  8,435 words and pushed five sections to 270–380 words in a file whose minimum was 760. The strip was
  applied only to the 10 sections that clear *and* keep their depth; **v38, v43, v44, v45, v46, v51
  were left at their original 831–978 words for authored rebuilds**. v44 was excluded because it does
  not clear either way (0.043), so stripping it would only have cost words.

### 21.4 Defects that leaked from the drafting process itself

These are not prose-quality problems; they are the author's own process left in the deliverable. None
was caught by any structural gate, because the Markdown was well-formed and the text was about the
right verse.

| Class | Instance | Size |
|---|---|---|
| **`[System Memory Check]` ritual leaked** | `074.md`, 54 of 56 sections — 61% of the file | **17,334 words stripped** |
| **Whole-file template boilerplate** | `036.md`, 83 of 83 sections, the same 13 sentences ×83 | **16,483 words stripped**, all 83 rebuilt |
| **Drafting monologue** | `037.md` v139's body *was* the deliberation: "…**Wait — actually** v139 starts with Jonah… **Let me correct** the content." | rebuilt from `initial/` |
| **Citation-hunting left in prose** | `032.md` ×4: `40:47? — actually … Let me be careful`, `41:32? — actually`, `35:26? — actually`, `15:82? — … — wait` | 4 hits fixed |
| **Narrator guess-chain** | `083.md`: "Ibn ʿUmar? — no; it is narrated from Abū Hurayrah? — the wording is: Najdī ibn ʿUmar? Let me state it as transmitted" | all three guesses **wrong**; the narrator is al-Nuʿmān ibn Bashīr (Bukhārī 52), verified externally because `initial/` does not record the ḥadīth |
| **Corrupted tokens** | Truncated words with a stray `?` mid-prose (`004.md` ×4, plus `002`, `006`, `028`, `029`, `030`, `077`, `083`); a U+FFFD replacement character in `002.md`; stray `$`; a stray `Max` inside a citation ("cf. the hadith **Max** the celebrated Muslim 1017"); word-salad sentences in `004.md` and `008.md` | all fixed |
| **Undefined shorthand citations** | Two incompatible systems coexisted: numbered references in some files, bare letter codes `(Q)`, `(JJ)`, `(Z)`, `(IK)`, `(R)` in **19 files** (up to 82 occurrences in one), never defined for the reader | standardised |

`check_scaffolding.py` now covers the class and was validated by running it against the pre-fix files:
**10 hits before, 0 after.** Its patterns also match quoted scripture — "Let me kill Moses" is Pharaoh
at 40:26, and "Say: 'Wait — we too are waiting'" is 6:158 — so it **prints context for human judgement
rather than asserting a count**. Never let a scaffolding checker auto-delete.

Note that `system_instructions.md` at the repository root *requires* the `[System Memory Check]`
append ritual as part of its memory protocol. That is an instruction to the agent about its own
responses; it must never reach the deliverable. 074.md is what happens when it does.

### 21.5 A full-file rebuild, and how deep to go

`036.md` is the reference case for rebuilding an entire file: all 83 sections were template-generated,
so the boilerplate was stripped first (16,483 words) and every section rebuilt verse by verse from the
apparatus in `initial/036.md`, in **21 batches of 4** (`content_036_a.py` … `content_036_u.py`). Final
state: 43,738 words, min 419 / **median 516** / max 721, zero sections over the duplication gate,
zero off-topic flags, zero translation flags.

**The median of 516 was deliberately below the corpus healthy figure of 976**, because this sūrah's
apparatus in `initial/` is thinner than that of `011.md`, `021.md` or `040.md`. The recorded principle:
*"Depth was matched to what the source material can support rather than padded to a number."* That is
the correct answer when a chapter's source is thin, and it is why §15 pre-decides that a structurally
short verse gets a documented lower floor instead of invented scholarship.

One trap from that rebuild, which will recur: **eight sections (vv 18, 28, 36, 45, 47, 65, 66, 78)
tripped the duplication gate for the same reason each time — quoting the verse translation verbatim in
the opening prose.** The 10-grams of the quoted verse alone trip the detector. Each was fixed by
paraphrasing the opening and leaving the quotation to the `> **…**` line. This is the same mechanism as
§18.4; do not let the opening prose of a regenerated section restate its own blockquote.

## 22. Citation and factual integrity

Pass 4 in §19. This is the pass that catches things no structural gate can see, and 007 needed it
badly.

### 22.1 Verse numbers must be checked against chapter lengths

A citation is invalid if the verse number exceeds the sūrah's length. `translation/NNN.txt` gives every
chapter's length, so this is mechanically checkable. Instances found:

| Location | Cited | Problem | Correct |
|---|---|---|---|
| `007.md` ×2 | `(21:119)` | Sūrah 21 has **112** verses | **7:156** |
| `011.md:137` | `(93:27)` | Sūrah 93 has **11** verses | 53:42 / 94:8 |
| `011.md:137` | `(59:62)` | Sūrah 59 has **24** verses | — |
| `029.md:1579` | `(41:99–100)` | Sūrah 41 has **54** verses | 16:99 |
| `037.md` ×2 | `57:37–38` | Sūrah 57 has **29** verses | — |
| `050.md:756` | `(24:65)` | Sūrah 24 has **64** verses | 24:24 |
| `008.md:913` | "8:80's sūrah-kin" | Sūrah 8 has **75** verses | — |
| `034.md:455` | "(Qur'an 14:78 in some counts; 4:78)" | Sūrah 14 has **52** verses, and **there is no counting variant — the "in some counts" hedge is invented** | 4:78 |

The last row is its own class: a fabricated textual-critical hedge invented to cover a bad number.
Delete the hedge; do not preserve it.

Also check ḥadīth-number plausibility against the collection's size: Muslim 3849 and Muslim 4261 were
both flagged as **outside the standard 3,033-numbering of Ṣaḥīḥ Muslim**.

### 22.2 Every quotation's wording must be matched, not remembered

The fidelity sweep that fixed 129 quotations across 33 drafts is the pass to copy. Method: a **five-gram
verbatim matcher** comparing each quoted span against `translation/NNN.txt`. Corrections it produced in
007's final instalment alone: 5:13 ("commanded to uphold"), 5:60, 2:79 ("what they have earned"),
2:134 ("what they have done"), 34:46 ("Your fellow man is not insane"), 6:38 ("nothing out of the
Record"), 15:49–50, 34:13, 49:10 ("but one brotherhood"), 28:16, 40:7, 17:34, 20:86, 20:94, 61:5
("Allah caused their hearts to deviate"), 7:22 — plus one reference corrected (5:63 → 5:62–63).

**Two matcher artifacts to expect, so you do not chase them:**

- A strict five-gram test over the whole repaired file flagged **992 quoted spans**; the majority are
  quotations that **span two adjacent verses**, which the matcher cannot resolve. Read them; do not
  "fix" them.
- **Translation-register differences** produce false positives. A quote-to-citation matcher flagged
  **205 "strong" candidates** for misattribution and hand-checking showed the large majority were
  false, caused by the file's own archaic register against the reference translation, and by quotes
  spanning two verses. A separate translation-fidelity sweep flagged 7 sections; **all 7 proved to be
  faithful paraphrases**. Translation content was therefore concluded to be *not* a defect area.

**A high-precision variant does work:** hunt for a quote that shares **zero** distinctive vocabulary
with the verse it is cited against but **≥75%** with another verse. That returned **0 false positives
corpus-wide** and is the right shape of test.

### 22.3 ḥadīth numbers: the corpus-unanimity rule

One report — *"I and the Hour have been sent like these two"*, the Prophet ﷺ joining his index and
middle fingers — is cited **thirteen different ways across thirteen files**, with six distinct
al-Bukhārī numbers (4936, 6036, 6500, 6503, 6504, 6505), four distinct Muslim numbers (867, 2683,
2950, 2951) and one al-Tirmidhī (2338).

**Not every variance is an error.** al-Bukhārī 4936 (Book of Afflictions) and 6504 (Book of *Riqāq*)
are two genuine placements of the same report, and Muslim 2950 and 2951 are two genuine narrations
from Sahl ibn Saʿd. Two files citing different numbers can both be right.

The governing rule, which resolves the whole class:

> **Where the corpus is unanimous, it settles the question. Where it is merely varied, it does not.**

Applied: `017.md` v35's al-Bukhārī 2079 was **corrected to al-Tirmidhī 1209**, because seven files
cite it consistently as al-Tirmidhī 1209 and two others show 2079 to be a different report entirely
(the option to revoke a transaction). v51's Muslim 2940 was **corrected to 2951** — no corpus support,
and it duplicated the role of 2950 cited eleven lines earlier; a typo. v44's Abū Dāwūd 2550 and 2877
for one ḥadīth were **aligned to the corpus consensus, Muslim 1955**. But the thirteen-way report was
**left alone**, because `initial/017.md` attributes it to al-Ṭabarī with no collection number at all,
so the ground-truth sources do not settle it. Harmonising thirteen files to the plurality (al-Bukhārī
6504 with Muslim 2950/2951 and Sahl ibn Saʿd) **would be a guess dressed as a correction.**

Also fixed where externally decidable: `001.md`'s al-Bukhārī **714 → 756** for "There is no prayer for
the one who does not recite the Opening of the Book" (Muslim 394 was already correct); `015.md`'s
"Tie **her** and rely" → the actual narration is "Tie **it** and rely (on God)" (al-Tirmidhī 2517, Ibn
Mājah 4168), cited with no number and altered wording.

**No gate covers this class.** A checker that flags identical quotation text appearing under different
collection numbers would find it mechanically, and is worth writing before any ḥadīth-heavy work.

### 22.4 Factual and superlative claims

Three classes were found, all by reading:

- **Wrong metadata.** `026.md`: "sits in the **fifteenth** juzʾ" — al-Shuʿarāʾ lies in the **19th**.
  `021.md`: "marks the opening of the **fifteenth** of the thirty juzʾ" — al-Anbiyāʾ opens the **17th**
  (21:1 is the start of juzʾ 17).
- **False superlatives, sometimes self-contradicted inside the same file.** `005.md`: "It is the **only
  sūrah** to mention the call to prayer (v. 58)" — contradicted **2,800 lines later in the same file**,
  which quotes 62:9 ("when the call to prayer is made on Friday…"). `002.md`: "the **shortest verse**
  in the Madinan address" applied to 2:42 (13 words), when the shortest are the opening letters (2:1).
- **Counts stated from memory.** §7:103's "roughly **one hundred and thirty** times" was corrected to
  the measured figure: Moses appears **178** times in `translation/`.

**Rule: any claim of the form "the only", "the first", "the shortest", "N times", or "in the Xth juzʾ"
must be measured against the corpus or an external source before it is written.** Grep for it. If it
cannot be measured, delete the claim rather than soften it.

### 22.5 The apparatus the chapter must actually carry

Measured against the project's own brief, the corpus failed badly before this work, and 007 was among
the worst:

| Requirement | Measured, pre-work |
|---|---|
| Ḥadīth with collection identified | **3,715 of 6,236 sections (59.6%)** had no *numbered* ḥadīth citation; **2,674 (42.9%)** had no ḥadīth or book citation of any kind. Worst: `026.md` 215/227 (95%), `037.md` 174/182, **`007.md` 168/206**, `011.md` 118/123 |
| Qurʾānic cross-reference | **3,340 sections (53.6%)** contained no verse reference |
| Any quoted text or attributed report | **225 sections (3.6%)** had no quotation, no blockquote and no attribution verb |
| Self-description vs delivery | `026.md:33` promises "authenticated Prophetic reports with their collections identified" and "Nothing is compressed because of the chapter's length" — yet 215 of its 227 sections carry no ḥadīth or book citation at all, none carries a numbered reference, and the file holds the corpus's 20 thinnest sections |

**A chapter's introduction must not promise what its sections do not deliver.** Check the file's own
claims about itself against its measurements before finishing.

## 23. Measurement discipline, and the green-gate fallacy

More errors in this work came from unmeasured figures than from bad prose. These rules are not
bureaucracy; each one exists because a specific number was wrong and nearly caused a specific mistake.

### 23.1 The green-gate fallacy

> **A green gate is evidence only about what the gate measures.**

`validate.py` reported **PASSED 114/114** while **107 of 114 files** carried 219 illegal horizontal
rules and 10 files carried 11 non-canonical H2 headings — and an audit report had already credited it
with reducing "canonical-skeleton divergence" to "**0 remaining**". That claim was false. The gate
tested `L[i-1] == '---'` and `L[i-2] == ''` for each heading; a duplicated rule satisfies both, because
the second rule sits at `L[i-1]` and the blank between them at `L[i-2]`, while the stray first rule
occupies `L[i-3]`, which was never examined. It also **never inventoried headings at all**.

It was then hardened **twice more for the same reason**: it still reported 114/114 while `017.md`
carried 111 malformed `****Heading****` mini-headings and three files carried four orphan connector
lines. Neither class was checked. Both are now gated (`^\*{4,}` for malformed headings; a bare short
word alone between two blockquotes for orphans), and each gate was regression-tested **in both
directions**. `test_skeleton.py` (18 checks) proves the pre-hardening gate would have accepted them:
against a file carrying all four artifact classes, the old gate reported neither class, while the new
one reports `stray horizontal rule x5 (4 duplicate, 1 internal)` and `non-canonical H2 x1`.

**Consequence for you:** when a gate passes, ask what it does not test, and inventory that separately.
Do not report a gate pass as proof of a property the gate does not check.

### 23.2 Three spans exist — state which one you used

Word counts and duplication rates differ materially by span, and mixing them produces figures that look
like progress and are not.

| Span | Used by | 007-era corpus result |
|---|---|---|
| **Whole section** — heading through body, trailing rule dropped | `census.py` duplication, and the audit's depth tables | **198 sections under 260 w, 524 under 400 w** of 6,236; **269** sections at ≥0.030 duprate |
| **Body only** | `census.py` depth; `check_degeneracy.py`; `repair_degen.py` | 215 / 601 on the same tree; **151** sections at ≥0.030 |
| **Heading-inclusive** | nothing — do not use | 190 / 505 — adds four tokens per section and "looks like progress but is only a different span" |

`census.py`'s own comment warns that a body-only span gives materially different counts (**151 vs
269** at the 0.030 gate) and **must not be substituted silently**. An early `strip_recap.py` made
exactly that substitution and consequently found **zero** flagged sections in files `census` reported
**30** in. Its depth figures are body-only and so run ~12–25 words below the whole-section medians.

Prose words corpus-wide are defined as **word tokens matching `[\w'’-]+`, summed over all of
`expanded/`, excluding lines that are exactly `---`** — 6,415,363 on that tree. Note the trap: `---`
tokenises as a word under that pattern, so a naive count reported a delta of −219 when Group G's
repairs removed 219 rule lines with **zero prose change**.

Also: `check_translations.py` reports **6,235** sections where `census.py` reports **6,236**, because
one section has no source text to compare against. Both are right.

### 23.3 Every figure quoted in a log must be measured in the step that writes it

Figures written from memory were wrong often enough to become a standing rule, and three separate
errata record it:

- The expansion was reported as adding **12,318 words**; measured with the gate's own body-word count
  at the commit immediately before tranche 18 against HEAD, it added **7,149** (270,526 → 277,675).
- The Tier-1 list was reported as holding **47 verses**; it held **46** when introduced, and now holds
  **25** — 46 − 22 demoted + 1 promoted in.
- A duplication count of **303** sections was reported and is **not reproducible by any variant tried**
  (whole-section vs body-only, with and without Markdown stripped, n=10 and n=8, minimum length 80 and
  0). The measured value was **279**. The old figure is withdrawn. Its per-file breakdown also
  disagreed in ways no recorded edit explains — `014.md` listed at 29 but measuring 16, `010.md` at 36
  but 30, `011.md` at 18 but 12.
- A "groundability census" reported **101 ungroudable sections**. The real figure was **1 of 410**. The
  cause was a parsing bug: `initial/` abbreviates verse ranges in its markers — `**124-28**` means
  124–128 — and the code computed `range(124, 29)`, which is empty, so **every abbreviated range marker
  was silently dropped** and its verses counted as having no source note. The same bug was in
  `extract_source.py`, which returned "(no commentary)" for verses that do have a shared range note.
  This error **nearly caused a real omission**: a decision was framed around writing 101 sections
  unsourced.
- A depth table row for `037.md` was carried **pre-rebuild** and contradicted the same document's own
  result line. It was corrected twice — the second correction because the fix wrote the old *median*
  (245) into the *min* column, when the measured minimum is **144**, shared by v117 and v167.
- `074.md`'s figures (min 392 / median 436 / 25,610 words) were **not reproducible on the current tree
  under either span**; they had been taken against an earlier state of the file.

**Where a figure cannot be reproduced, withdraw it in writing and say so.** Never silently replace it —
a later reader cannot tell a correction from an estimate. Where a wrong figure has already been pushed
in a commit message and history cannot be rewritten, the erratum stands as the correction and says
exactly that.

**Also record what a number was measured against.** The pre-work baseline `48e6cbb` referenced in one
report is **not in this repository's history** — the tree was squashed — so figures diffed against it
can never be re-checked. That is a permanent loss of auditability, and it is why §19 keeps its own
before-and-after measurements.

### 23.4 Tooling hazards

- **Hard-coded roots.** `normalize.py`, `apply_sections.py`, `append_block.py` and `apply_026.py` all
  hard-coded `ROOT = "/home/user/new"`. Run from a copy — such as a test sandbox — they **silently read
  and wrote the real corpus instead of the copy**. All four were changed to derive `ROOT` from
  `__file__`. Without that fix, the regression test would have mutated the shipped corpus during its
  own run.
- **Working copies in `/tmp` do not survive a sandbox reset.** The 017 block analysis depended on a
  pre-fix copy at `/tmp/017.bak`; it was **lost and regenerated mid-pass**. Anything a later step needs
  must be regenerable from a committed ref (`git show <sha>:expanded/NNN.md > /tmp/NNN.bak`), never
  assumed to persist.
- **Position-based identification is the only reliable method** for locating an inserted block. Finding
  one by "the Nth heading in the section" **picks the wrong one**.
- **Test whether a marker-preserving tool keeps offsets valid.** `fix_headings.py` preserves line
  counts, which is exactly why a pre-fix copy's relative offsets stayed valid against the current file.
  That property was relied on, not assumed.

### 23.5 What "complete" means for a chapter

The files recorded as complete, with the figures that earned it:

| File | Sections | Median words | Note |
|---|---|---|---|
| `001.md` | 112 | 1,942 | **confirmed reference, never modified** |
| `011.md` | 123 | 914 | 0 translation defects, 0 filler |
| `021.md` | 112 | 1,037 | 121,660 words; vv 73–76/78/97 are legitimate variants |
| `026.md` | 227 | 247 | correctness complete; **depth outstanding** |
| `036.md` | 83 | 516 | rebuilt in full |
| `037.md` | 182 | 290 | correctness complete; depth outstanding |
| `040.md` | 85 | 937 | 0 translation defects |
| `007.md` | 206 | **730 at audit** → 1,357 after expansion | the file this prompt is derived from |
| `017.md` | 111 | 1,055 | **not** a depth problem; no section under 400 words |

**Correctness and depth are separate axes and are reported separately.** `026.md` and `037.md` are
"correctness complete, depth outstanding" — every citation verified, every translation right, and still
the two thinnest files in the corpus. Say which axis you have finished.

## 24. Finish

1. Confirm every Tier-1 section clears 1,400 words and every other section clears its own floor.
2. Run the three manual checks (§12.3) one final time, plus all four gates.
3. Walk the nine-pass table in §19 and confirm each pass has been run or was measured as unnecessary.
   A pass skipped because the chapter "looked clean" is not a pass run — 007 looked structurally clean
   at every stage and still needed all nine. For each, record the measured figure:
   - pass 0 audit — the chapter's defect counts before you touched anything;
   - pass 1 — `normalize.py` idempotent (0 files written), no stray rules, H2 inventory = intro + verses;
   - pass 2 — chains per 1,000 words, and the retention figure if you regenerated anything;
   - pass 3 — blockquotes byte-exact against `translation/{{NNN}}.txt`, count matching `initial/` = 0;
   - pass 4 — 0 non-existent verse references, 0 wording divergences, N citations checked;
   - pass 5 — 0 `cf.`, 0 `vicinity`, 0 ELLIPSIS, 0 DRIFT, and the EXACT count;
   - pass 6 — own-verse spans checked;
   - pass 7 — census sections at ≥0.030 on the 'whole' span = 0;
   - pass 8 — words added, measured against the commit before you started.
3. Write `tools/quran-audit/DEPTH_PLAN_{{NNN}}.md`: the Tier-1 list as chosen; the batch log with
   word counts; every section demoted with its reason; and a **numbered list of corrections** — every
   factual error you found in your own plan along the way, including wrong concordance counts and
   mis-assigned material. On 007 this ran to fifteen subsections and was the most reused artifact in
   the repository, because it is what stops the next session repeating the same mistakes.
4. Commit, push, and post one summary comment to the pull request with the final gate table.
5. Report **once**, and only after the chapter is finished. This is the sole output the operator
   receives — there is no earlier message and no later one. Include: confirmation that the whole
   chapter was completed in this single run with no input sought; the nine-pass figures from step 3;
   sections drafted; sections demoted; words added, measured with the gate's own count against the
   commit before you started (**never recalled from memory** — two figures written from memory on 007
   were both wrong and needed a published erratum); the four gate results; anything that could not be
   done and why; and the path to `DEPTH_PLAN_{{NNN}}.md`.

## 25. Definition of done

Every verse of chapter `{{N}}` has: its own section in the canonical skeleton; its blockquoted
translation verbatim from `translation/{{NNN}}.txt`; commentary that uses the translation's own
vocabulary and echoes at least 15% of its distinctive words; body prose inside its band with 007's
internal shape; unique context-specific mini-headings; every Qurʾānic quotation EXACT against
`translation/` with its citation immediately after it; no leaked scaffolding; no recap blocks; and
all four gates green at zero failures.

**And, beyond the gates (§23.1 — a green gate is evidence only about what the gate measures):**

- **Structurally canonical** — no stray horizontal rules, no H2 outside the intro and the verses, no
  `****` malformed bold, no orphan connector lines, `normalize.py` idempotent on the file.
- **Citation-integral (§22)** — every verse number valid against its sūrah's length in
  `translation/`; no fabricated "in some counts" hedges; every quotation's wording five-gram matched
  against `translation/{{NNN}}.txt`; no ḥadīth number written from memory; and where the corpus
  disagrees on a number, corrected only where the corpus is **unanimous**, never harmonised to a
  plurality.
- **Factually integral (§22.4)** — every "only", "first", "shortest", "N times" and juzʾ claim measured
  before it was written.
- **Free of drafting debris (§21.4)** — no `[System Memory Check]`, no template boilerplate, no
  self-correction monologue, no citation-hunting, no guess-chains, no corrupted tokens or stray
  characters, no undefined letter-code citations.
- **Describing the right verse (§21.1)** — every section's opening prose read against its own verse
  translation. No tool can do this for you.
- **Not over-fixed (§21.2, §21.3)** — detector false positives documented rather than "corrected"; no
  automated sentence-trimming; no bulk block deletion; no scholarship traded away to clear a gate.
- **Depth matched to the source (§21.5)** — where the apparatus in `initial/{{NNN}}.md` is thin, the
  section is shorter and the lower floor is documented, not padded to a number.
- **Retention sane (§19)** — if anything was regenerated, the share of sound original prose that
  survived is recorded and defensible.

Then it is committed, pushed if the session has remote access, logged in `DEPTH_PLAN_{{NNN}}.md`,
and reported once.

**And it was all done in one run.** The chapter is finished — not begun, not partly finished, not
planned — and the operator was asked for nothing between the instruction to start and the final
report. A deliverable that leaves any verse, any pass or any gate outstanding is not done, whatever
else it contains.
