# Standardization Prompt — bring any chapter to the `expanded/007.md` standard

Copy everything below the line into a fresh session. Replace the two placeholders first:

- `{{N}}` — the chapter number as an integer, e.g. `11`
- `{{NNN}}` — the same number zero-padded to three digits, e.g. `011`

This prompt is the complete specification of everything that was done to `expanded/007.md`. It is
deliberately long: it carries the rules, the measured norms, the gates, the defect classes that the
gates miss, and the pre-decided answer to every judgement call. Nothing here is optional background.
Do not shorten it before use.

---

## Mission

Bring `expanded/{{NNN}}.md` — the commentary on Sūrah number `{{N}}` — to the standard achieved in
`expanded/007.md`, this repository's confirmed gold standard. Go verse by verse in ascending order
and complete the whole chapter in one continuous run.

Work autonomously to completion. **Never ask a question, never request approval, never post a
progress update, never stop because the chapter is long, never pause between batches.** Report once,
at the very end. §15 answers every judgement call in advance.

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
3. **Never cut, delete, reorder, summarise or rewrite existing commentary.** This work is additions
   only. If a section you have written exceeds its ceiling, trim only what you added in this session.
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
5. `initial/{{NNN}}.md` — skim only. Old archaic source; background only. **Nothing in it may be
   quoted, and its vocabulary must not leak into the commentary.**
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
  narratives. Their findings live in the gates and in `DEPTH_PLAN_007.md`. Do not recreate
  corpus-wide audit narratives; write a per-chapter plan document instead (§17).

## 17. Finish

1. Confirm every Tier-1 section clears 1,400 words and every other section clears its own floor.
2. Run the three manual checks (§12.3) one final time, plus all four gates.
3. Write `tools/quran-audit/DEPTH_PLAN_{{NNN}}.md`: the Tier-1 list as chosen; the batch log with
   word counts; every section demoted with its reason; and a **numbered list of corrections** — every
   factual error you found in your own plan along the way, including wrong concordance counts and
   mis-assigned material. On 007 this ran to fifteen subsections and was the most reused artifact in
   the repository, because it is what stops the next session repeating the same mistakes.
4. Commit, push, and post one summary comment to the pull request with the final gate table.
5. Report **once**. Include: sections drafted; sections demoted; words added, measured with the
   gate's own count against the commit before you started (**never recalled from memory** — two
   figures written from memory on 007 were both wrong and needed a published erratum); and the four
   gate results.

## 18. Definition of done

Every verse of chapter `{{N}}` has: its own section in the canonical skeleton; its blockquoted
translation verbatim from `translation/{{NNN}}.txt`; commentary that uses the translation's own
vocabulary and echoes at least 15% of its distinctive words; body prose inside its band with 007's
internal shape; unique context-specific mini-headings; every Qurʾānic quotation EXACT against
`translation/` with its citation immediately after it; no leaked scaffolding; no recap blocks; and
all four gates green at zero failures. Then it is committed, pushed, logged in
`DEPTH_PLAN_{{NNN}}.md`, and reported once.
