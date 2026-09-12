# Standardization Prompt — bring any chapter to the `expanded/007.md` standard

Copy everything below the line into a fresh session. Replace the two placeholders first:

- `{{N}}` — the chapter number as an integer, e.g. `11`
- `{{NNN}}` — the same number zero-padded to three digits, e.g. `011`

Everything a new session needs is in the prompt. It is written so that no question ever has to be
asked and no decision ever has to be escalated: every judgement call has a pre-decided answer in
§12. Do not edit the prompt down; the rules are what make the single-pass run possible.

---

## Mission

Bring `expanded/{{NNN}}.md` — the commentary on Sūrah number `{{N}}` — to the standard already
achieved in `expanded/007.md`, which is this repository's confirmed gold standard. Go verse by
verse, in ascending order, and do the whole chapter in one continuous run.

Work autonomously to completion. **Never ask a question, never request approval, never post a
progress update, never stop because the chapter is long, never pause between batches.** Report
once, at the very end. Everything you need to decide is decided below.

The benchmark you are aiming at, measured on `expanded/007.md`:

| Measure | 007 result |
|---|---|
| Sections | 206, one per verse, canonical skeleton |
| Body words | 277,675 (blockquoted verse text excluded) |
| Median section | 1,370 words |
| Shortest / longest | 824 (a documented reduced-floor fragment) / 2,100 |
| Qurʾānic quotations | 1,780, every one **EXACT** against `translation/` |
| Drift / ellipsis / vicinity / bad refs | 0 / 0 / 0 / 0 |
| Tics per 1,000 words | 0.19 |
| Chains per 1,000 words | 0.12 |
| Duplicate 10-gram fraction | 0.062 |
| Sentences repeated verbatim in-file | 0 |
| Sections failing any gate | **0** |

Match the ratios, not the absolute numbers — chapters differ in length. What must match is: every
verse inside its band, every quote exact, every gate at zero failures.

---

## 1. Hard constraints

1. Work **only** on chapter `{{N}}`. Do not modify any other `expanded/*.md`.
2. **Never modify** `expanded/001.md` (the confirmed structural reference), `translation/*.txt`,
   or `initial/*.txt`. They are inputs, not deliverables.
3. **Never cut, delete, reorder, summarise or rewrite existing commentary.** This work is
   additions only. If a section is too long, trim only material you added in this session.
4. Never delete, rename or move the repository root or its `.git` directory.
5. Commit to the session's branch and push only to that branch. **Never force-push.**
6. Keep generated artifacts out of Git. Anything a gate can regenerate stays untracked.
7. Do not run `normalize.py` on the chapter unless `validate.py` reports structural failures for
   it, and never run it on `expanded/001.md`.

## 2. Read once, then execute — no re-reading

Read these in one pass at the start. Do not return to them later except to look up a specific
line.

1. `system_instructions.md` — the house rules for depth, headings and continuous execution.
2. `expanded/001.md` — the canonical skeleton, first 40 lines and last 10 lines are enough.
3. `expanded/007.md` — the gold standard. **Do not read the whole file.** Read exactly four
   sections: the introduction, one long doctrinal section (7:143 or 7:46), one narrative section
   (7:73 or 7:91), and one short fragment (any verse in the `SHORT_VERSE` list). That is the
   register, the density and the mini-heading style you are reproducing.
4. `translation/{{NNN}}.txt` — the entire chapter, in one read. This is the quote authority.
5. `initial/{{NNN}}.md` — skim only. It is the old archaic source; it is background, and **nothing
   in it may be quoted**.
6. `tools/quran-audit/DEPTH_PLAN_007.md` §10 — read the *corrections* list only (§10.5 to §10.15).
   It is the accumulated record of mistakes made on 007. Every one of them is a trap you can avoid
   for free.
7. The docstrings of the seven scripts in `tools/quran-audit/`.

## 3. The canonical skeleton (`validate.py` enforces this byte-exactly)

File layout, top to bottom:

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

Then, for every verse in order:

```
<blank>
---
<blank>
## Sūrah <Name> {{N}}:<verse>
<blank>
> **<the verse text, verbatim from translation/{{NNN}}.txt>**
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

And the file ends:

```
<blank>
---
**[End of the commentary on Sūrah <Name>]**
```

Rules the validator checks, all of which must hold:

- The `<Name>` in the H1, in every verse heading, and in the end marker must be **identical**.
- The chapter number in the H1 must equal `{{N}}`.
- Every verse heading is preceded by a blank line and then `---`. Exactly one rule per boundary,
  nowhere else. A stray or duplicated `---` fails.
- Verse numbers are contiguous from 1 to the last verse, in ascending order, no duplicates.
- The line after each verse heading is blank, then the blockquote `> **…**`, then blank, then
  `**Expanded Commentary**`, then blank, then the first mini-heading.
- **No `###` or deeper headings anywhere.** Everything below H2 is a bold mini-heading.
- A bold mini-heading is `**Text**` — never four or more leading asterisks.
- Exactly one trailing newline at end of file; never two; no carriage returns anywhere.
- No bare one-to-three-letter word alone on a line between two blockquotes.

## 4. Where every quotation comes from

**Qurʾānic quotations come only from `translation/SSS.txt`, and only as verbatim contiguous spans.**

- The file format is one verse per line: `<verse number> | <text>`. Verse 47 is the line beginning
  `47 | `.
- **Copy-paste the span. Never retype it from memory.** Retyping produces near-misses that the gate
  rejects as DRIFT.
- Reproduce editorial brackets `˹ ˺` and their contents **exactly**. The gate strips the bracket
  characters but keeps the bracketed *words*, so a dropped `˹O Prophet˺` is a failure.
- **No ellipses inside a quotation, ever.** Do not join two parts of a verse with `…`. Quote one
  contiguous span, or write two separate quotations.
- **No paraphrase inside quotation marks.** A literal gloss goes outside the quotes, in italics:
  *dallāhumā bi-ghurūr* — so he brought about their fall through deception.
- Quoted spans begin with the translation's own capitalisation. If the span starts mid-sentence,
  restructure your sentence so a lowercase opening reads correctly; do not capitalise the quote.
- **Apostrophe hazard:** a curly `’` inside a quoted span closes the gate's span detection early.
  Prefer a sub-span with no apostrophe in it. Where a verse reads `Allah’s mercy is always close`,
  quote `mercy is always close to the good-doers`, not the whole clause.
- **Citation placement:** put `(S:V)` immediately after the closing quotation mark. The gate scans
  roughly 400 characters *after* a quote for the nearest citation, and the **first** parenthesis
  wins. When two quotations share a sentence, each needs its own parenthesis directly after it, or
  the first will be checked against the second's reference and fail.
- **Zero-hedge rule:** none of these words may appear in the window after a quotation —
  `vicinity`, `cf.`, `sense`, `context`, `sequel`, `account`, `clause`, `onward`, `paraphrase`,
  `and parallels`, `in its own s`. They mark the quote as non-verbatim and are reported as
  VICINITY failures. Write around them.
- Quoting the section's **own** verse inside its own body still needs its own `(S:V)` immediately
  after the quote.

**Ḥadīth and scholarly reports:**

- Give the actual wording, and the collection and number **only if verified**. Web search is
  permitted and expected for this — use it to verify, never to generate.
- If a number cannot be verified after one search, either attribute the report to a named exegete
  as exegetical tradition (al-Ṭabarī, Ibn Kathīr, al-Qurṭubī, al-Rāzī, al-Ālūsī, al-Suyūṭī), or
  drop the citation and support the point from the Qurʾān instead. **Never invent a number.**
- Where a report is contested or a commentator qualifies it, carry the qualifier. An-Nawawī's
  gloss on the *al-arwāḥ junūd mujannadah* chapter — affinity and grouping, not a pre-earthly
  assembly — is the model of how to do this.

## 5. Length rules — the depth band

Word counts are **body words**: tokens matching `[\wʹʼʿʾ’'-]+`, counted on lines that do not start
with `>`. This is exactly how `check_filler.py` counts, so the gate and your estimate agree.

| Class | Band |
|---|---|
| Standard verse (narrative, legal, doctrinal) | **1,200 – 1,400** |
| Tier-1 verse (the chapter's densest and most consequential) | **1,400 – 1,800** |
| Deepest verses (the 3–5 theological or legal cruxes of the chapter) | up to **2,100** |
| Reduced-floor exceptions (documented fragments only) | **700** minimum |

- A verse qualifies for the reduced floor **only** if it is fourteen words or fewer in
  `translation/{{NNN}}.txt` **and** it is one of: the *muqattaʿāt*, a single dialogue clause, or a
  scene-closing fragment that takes its sense from the verse before it.
- A short verse that is **not** a fragment stays in the full band — there is real scholarship to
  fill it with. (On 007: the manners of supplication, the metamorphosis, *istidrāj*, forbearance.)
- Exceptions are added **one at a time, each with a written reason.** Never in bulk.
- Sections already above the band are left alone. The ceiling exists to stop padding, not to force
  cuts.

## 6. Choosing the Tier-1 list

Read every verse of the chapter from `translation/{{NNN}}.txt` — you already did this in §2 — and
score each for density. A verse is a Tier-1 candidate if it carries any of:

- a legal ruling or a ruling's conditions
- a divine attribute, name, or act of God stated doctrinally
- a covenant, oath, or eschatological scene
- a named prophetic episode with narrative consequences
- a formula the Qurʾān repeats elsewhere, which can be counted across chapters
- a term the exegetical tradition disputes, with identifiable positions

Select roughly **15–25% of the chapter's verses** as Tier-1, and the **3–5 densest** of those as
"deepest". Write the list down in your working plan before drafting anything.

Then apply §7 to every one of them, because on 007 this list was **wrong about half the time**.

## 7. The deduplication test — the single most important rule

This is the lesson that governs everything. On 007, 22 of the 46 sections listed as having
headroom turned out to be already saturated, and the plan's own concordance lists were factually
wrong six times. The test that caught both problems is run **per verse, immediately before
drafting that verse**, never in bulk and never from memory:

1. **Read the verse text** from `translation/{{NNN}}.txt`. Do not rely on a summary of it.
2. **Extract every existing bold mini-heading** for that verse from `expanded/{{NNN}}.md`.
3. For each candidate new heading, **grep the section body for every citation that heading depends
   on** — each `S:V` reference, and each key term.
4. **If the sources are already quoted in the section, the heading is a citation upgrade to an
   existing head, not new depth. Drop it.**
5. If *every* candidate heading is already carried, the section is saturated: **remove it from the
   Tier-1 list, leave it in the standard band, and log the removal with the reason.**
6. Never propose a heading for content the verse does not contain. Verify that the word or phrase
   the heading is about actually appears in that verse.

Two corollaries that saved the most time on 007:

- **Count concordances from `translation/`, never from a summary or a cached list.** Grep the
  actual files. On 007 a plan claimed a word occurred seven times including a verse that did not
  contain it; the true count was six. Another claimed an expulsion threat at a verse that was
  actually about Iblīs's respite.
- **A heading already drafted in another section is cross-section duplication, not depth.** If the
  same harmonisation belongs naturally at two verses, draft it once, at the verse where it does the
  most work, and let the other verse cite it.

## 8. What each verse section must contain

Per `system_instructions.md` §3, and visible in every section of 007:

- **Arabic vocabulary, root and morphology**, transliterated and explained in simple English.
- **Qurʾānic cross-references with the actual quoted text** from `translation/`, not bare pointers.
- **Authentic ḥadīth** with real wording and a verified collection and number.
- **Classical scholars' views** — al-Ṭabarī, Ibn Kathīr, al-Qurṭubī, al-Rāzī, al-Ālūsī, Ibn ʿAbbās,
  Ibn Taymiyyah, Mālik, an-Nawawī — where they genuinely differ or genuinely illuminate. Where the
  tradition records multiple positions, give the positions and, where an exegete adjudicates, the
  adjudication.
- **Asbāb al-nuzūl** and historical context where applicable, with the chain or source named.
- **ʿAqīdah**: divine attributes, justice, human responsibility, free will, the Hereafter.
- **Psychological, social, ethical and practical implications**, including modern application and
  relatable analogy.
- **The logical reason** the command or principle makes sense — not just what it says.

Length must come from these. Never from restatement, recap, or a summary paragraph at the end of a
section.

## 9. Style prohibitions the gates measure

- **Tics ≤ 4.0 per 1,000 words; target near zero.** Banned: `it is worth noting`, `worth noting`,
  `it is important to note`, `it should be noted`, `in other words`, `that is to say`,
  `the point is`, `the fact is`, `as we have seen`, `as noted above`, `it is no accident`,
  `needless to say`, `it goes without saying`, `to be sure`, `at the end of the day`, `in a sense`,
  `in a way`, `so to speak`, `it is clear that`, `it is obvious that`, `this is the reason why`,
  `the reason for this is`.
- **Chains ≤ 1.5 per 1,000 words; target near zero.** Banned shapes: `is the X that is`,
  `of the X of the`, `the X is the Y of the`.
- **Duplicate 10-gram fraction ≤ 0.10** within a section; target ~0.06.
- **Zero sentences of 12+ words repeated verbatim** anywhere else in the file. Scripture and
  ḥadīth quotations are excluded from this check, so anything it flags is recycled commentary.
- **Do not quote the same verse span twice in one section.** Reference it the second time instead.
- Short, readable paragraphs. Every mini-heading unique and specific to the argument that follows
  it — never a template reused across verses, never decorative.
- Scholarly but plain. No sensationalism, no fictional dramatisation, no novelistic writing, no
  exaggeration.

## 10. The execution loop

Work in batches of **8–12 verses**. Per batch:

1. Read the batch's verses from `translation/{{NNN}}.txt`.
2. Extract each section's existing mini-headings and body word count from `expanded/{{NNN}}.md`.
3. Run the §7 dedup test on each. Decide: add heads, or demote the section out of Tier-1.
4. Fetch every quotation you intend to use, verbatim, from `translation/` — all of them, in one
   step, before writing.
5. Write the additions with a Python script run through a bash heredoc. The script must:
   - key its insertions by **string** verse numbers, not integers;
   - insert each block immediately **before the section's closing `---`**;
   - apply insertions from **highest file offset to lowest**, so earlier positions do not shift;
   - print a dry-run projection of before/after word counts against the ceiling first;
   - only write the file when run with an explicit `--apply` flag.
   **Never re-run a script that has already been applied** — it duplicates every block. Fixes after
   an apply go directly into the file.
6. Run all four gates (§11). Fix every failure. Re-run until all four are clean.
7. Commit with a message stating: sections touched, word counts before and after, heads added,
   heads struck as duplicates with the reason, sections demoted, and the gate results.
8. Push to the session branch. Go to the next batch.

Write scripts to `/tmp/` with a bash heredoc; the file-writing tool is workspace-scoped and cannot
reach `/tmp/`. Open files with an explicit `'w'` mode.

## 11. The gates — all four, after every batch

```
python3 tools/quran-audit/check_filler.py --sura {{N}} --band 1200-1400
python3 tools/quran-audit/check_cross_quotes.py {{N}}
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/census.py --sura {{N}}
```

Pass criteria, all of which must hold before you commit:

- `check_filler.py` → **FAILING 0**, below 0, above 0
- `check_cross_quotes.py` → **DRIFT 0, ELLIPSIS 0, VICINITY 0, NOVERSE 0**; every cited span EXACT
- `validate.py` → **PASSED 114/114, FAILED 0**
- `census.py` → 0 sections below 260 words, 0 below 400

Optional: `python3 tools/quran-audit/check_translations.py --sura {{N}}`. There are 7 pre-existing
flags corpus-wide that are known and ignored; investigate only new ones for your chapter.

If a push is ever rejected because the remote has moved: fetch the branch, `git reset --mixed` to
the fetched tip (this preserves your working tree), then re-commit only the files you intended.
Never force-push, and never `git add -A` without first checking `git status` for generated output.

## 12. Pre-decided answers — never ask, just apply these

| Situation | Decision |
|---|---|
| Unsure whether a heading is genuinely new | If its citations are already in the section, drop it |
| Unsure whether a verse is Tier-1 | If it carries a ruling, a divine attribute, or a repeated formula, yes |
| Section saturated but below 1,400 words | Demote it out of Tier-1; **never pad it** |
| Ḥadīth number unverifiable after one search | Attribute to a named exegete as tradition, or drop it and quote the Qurʾān |
| Over the ceiling | Trim the newest head; never an existing one |
| Two candidate heads make the same point | Keep the stronger, drop the other |
| A harmonisation fits two verses equally | Draft it once, where it does most work; the other verse cites it |
| The verse is 14 words or fewer | Check whether it is a fragment; only then consider the reduced floor, with a written reason |
| A plan, summary or memory conflicts with `translation/` | `translation/` wins, always |
| Anything else ambiguous | Choose the option that adds sourced scholarship and needs no user input, then move on |

## 13. Configuring `check_filler.py` for this chapter

The Tier-1 machinery in `tools/quran-audit/check_filler.py` currently holds 007's lists. Extend it
for chapter `{{N}}` without breaking 007:

- Keep `TIER1_FLOOR = 1400`, `TIER1_CEILING = 1800`, `DEEPEST_CEILING = 2100`, `REDUCED_FLOOR = 700`.
- Add this chapter's `DEEPEST` and `TIER1` verse keys, and this chapter's `SHORT_VERSE` entries
  with a written reason each. Key them so 007's entries are untouched — either generalise
  `depth_floor` and `depth_ceiling` to look at the chapter, or add parallel sets.
- **After editing, confirm 007 is unchanged**: `check_filler.py --sura 7 --band 1200-1400` must
  still report 277,675 words, FAILING 0, reduced-floor 18, and `check_cross_quotes.py 7` must
  still report 1,780 EXACT.
- Note that the summary line's `reduced-floor` figure counts floors *below* the band floor. If you
  raise a floor for a chapter, that counter must not silently absorb it.

## 14. Finish

1. Confirm every Tier-1 section for the chapter clears 1,400 words and every other section clears
   its own floor.
2. Write `tools/quran-audit/DEPTH_PLAN_{{NNN}}.md`: the Tier-1 list as chosen, the batch log with
   word counts, every section demoted with its reason, and a numbered list of corrections — every
   factual error you found in your own plan along the way. This document is how the next session
   avoids your mistakes; on 007 it ran to fifteen subsections and was the most reused artifact in
   the repository.
3. Commit, push, and post one summary comment to the open pull request with the final gate table.
4. Report **once**. Include: sections drafted, sections demoted, words added (measured with the
   gate's own count against the commit before you started — not recalled), and the four gate
   results.

## 15. Definition of done

Every verse of chapter `{{N}}` has its own section in the canonical skeleton; its blockquoted
translation verbatim from `translation/{{NNN}}.txt`; body prose inside its band; unique
context-specific mini-headings; every Qurʾānic quotation EXACT against `translation/`; and all four
gates green at zero failures. Then it is committed, pushed, logged, and reported once.
