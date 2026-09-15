# Rewrite `new/{{NNN}}.md` — Verse-by-Verse Commentary, Gated

## TASK INPUT

```
SURAH = {{NNN}}        # zero-padded chapter number, e.g. 011
N     = {{N}}          # same chapter without padding, used in headings, e.g. 11
```

Nothing else is a variable. Set these two and every path below resolves.

---

## 0. THE GATE IS THE CONTRACT

Every requirement you must satisfy is machine-checkable. Compliance is not judged by
your own assessment, and not by mine — it is judged by `scripts/check.py`.

```bash
python3 scripts/check.py verse   {SURAH} <V>     # after each verse   → must exit 0
python3 scripts/check.py chapter {SURAH}         # after the merge   → must exit 0
```

**A verse is finished when its command exits 0.** Exit 1 means: rewrite that verse and
run it again. It does not mean explain, justify, negotiate, downgrade the requirement,
or report the failure to me. Do not move to the next verse with an exit 1 behind you.

If a gate is unreachable (no web access, missing source), you do not lower the gate —
you record the limit inside the verse file as `[UNVERIFIED: <what>]` and list it in the
final report. Silently skipping a requirement is the one failure mode that matters here.

Why this section exists: an instruction nobody measures is treated as advice. Every
number below was **computed from the reference chapter**, so the rules and the model
text cannot disagree. If they ever do, the reference wins and `new/STANDARD.md` must be
regenerated — see §8.

---

## 1. READ THESE THREE THINGS. NOTHING ELSE.

For verse `V` of chapter `{SURAH}`:

| # | file | what it is | size |
|---|---|---|---|
| 1 | `new/STANDARD.md` | the writing standard + the model verse | ~1,900 words |
| 2 | `source_by_verse/{SURAH}/{SURAH}_{V}.md` | the verified scholarly source **for this verse only** | ~270 words |
| 3 | line `V` of `translation/{SURAH}.txt` | the authoritative translation | ~40 words |

That is the entire reading list for a verse: roughly 350 tokens, not 80,000.

Before starting the chapter, prepare the source (administrative, allowed):

```bash
python3 scripts/check.py split initial {SURAH}
```

**Never read these, and never ask for them:**

- `new/007.md` — the full reference chapter. It is 280,000 words; nothing can hold it,
  and skimming it is what produced the drift this pipeline exists to prevent. Read
  `new/STANDARD.md` instead. If you need a longer example, read **one verse**:
  `sed -n '/## Sūrah .* 7:15$/,/^## Sūrah/p' new/007.md`.
- `expanded/` — the superseded drafts. Reading them is how a writer ends up
  paraphrasing them. They are not an input to anything.

---

## 2. THE LOOP

For each verse `V`, in order, one verse at a time:

1. Read the three files in §1.
2. Decide what this verse actually requires: what it says, what problem it answers,
   what is distinctive about it, where the exegetes disagree and on what grounds.
3. Write the commentary **from that understanding** — your own structure, your own
   sentences, in prose that asserts rather than gestures.
4. Save it as `new/verse/{SURAH}_{VVV}.md`.
5. Run `python3 scripts/check.py verse {SURAH} <V>`. Exit 1 → fix, re-run.
6. On exit 0, append `{"v":<V>,"status":"PASS"}` to `new/verse/{SURAH}.ledger.json`.
7. Next verse.

**Before writing anything at all, read `new/verse/{SURAH}.ledger.json` if it exists and
skip every verse it marks PASS.** Never regenerate a PASS verse — not to improve it, not
to re-verify it. This is what makes the job resumable after a context break instead of
restartable, and restarts are where chapters get shorter, thinner, and duplicated.

---

## 3. HARD REQUIREMENTS

These are the gates. All are measured by `scripts/check.py`.

**Structure.** One file per verse. Heading exactly `## Sūrah <Name> {N}:<V>`, then the
translation as a blockquote, then `**Expanded Commentary**`, then bold `**Mini-heading**`
lines each followed by a developed section. **No `###` headings anywhere** — the reference
uses bold mini-headings; a `###` is an instant fail.

**Translation.** The blockquote must equal line `V` of `translation/{SURAH}.txt`
character for character: same wording, same bracketed insertions, same punctuation. Copy
it; never quote it from memory, never paraphrase, modernise, shorten, or substitute
another translation.

**Depth.**
- 700–2,300 words per verse; aim for 1,000–1,500.
- 3–12 bold mini-headings; aim for 5–8.
- **median section ≥95 words, aim for 160–220.** A heading followed by two or three
  sentences is a defect. This single number is the one the reference chapter violated on
  its last 89 verses — 15 tiny sections instead of 7 real ones, the same content cut
  finer. If you are heading toward that, merge sections rather than writing less.

**Originality.** Your commentary must not be a transformation of `initial/`:
- ≤2.5% six-word overlap with the source (the reference sits at 0.16%);
- no run of 25 consecutive words copied from it.

Facts, reports, arguments and conclusions from the source are yours to use and develop;
their **expression and arrangement are not**. If your paragraph order matches the
source's, you are restructuring, not writing. `initial/` is what you studied before
writing the book, not the book.

**Cross-reference tier (optional, not required).** You may end a verse with 0–2 plain
(non-bold) Title-Case heading lines, each introducing a short paragraph on a parallel
passage. Maximum 2, no duplicates, and they never replace a real mini-heading section.

---

## 4. STYLE — WHAT MAKES IT READ LIKE THE STANDARD

1. **Assert the point; do not announce that something is worth noticing.** The reference's
   collapse looked like this: `The sūrah's readers are shown that the pattern of judgment
   extends to those inside the covenant.` Repetition of that *syntax*, not that word, is
   the drift signature.

   Write the second form, always: `The pattern of judgment extends to those inside the
   covenant, not outside it.` Gate: ≤2 such sentences per verse; 0 is the standard.
2. **Vary your openings.** No 4-word sentence opening may appear more than 3 times in a
   verse (4 is tolerated; more fails `MONOTONY`). Fixing one tic by replacing it with a different fixed opener is still a tic,
   and `MONOTONY` fails it.
3. **A heading states a claim.** `**Delayed Until the Appointed Day**`, not
   `**Language**`, not `**Notes**`. Never manufacture a heading to reach a count, and
   never reuse one verse's heading pattern in the next.
4. **No padding.** Nothing here exists to be filled out. Do not restate the translation,
   repeat a conclusion, re-say a point in other words, or add generic moral advice. If
   more words do not add understanding, the verse is finished — being short and right
   beats being long and redundant, and `PADDING` fails duplicate sentences.
5. **Report disagreement with its grounds.** When the exegetes differ, give each side's
   *reason*, then say which is stronger and why. A list of names who differed is not
   scholarship.
6. **Explain difficult terms in the sentence that uses them** — transliteration, then
   plain sense, then what turns on it.
7. Natural scholarly English. No `delve`, `tapestry`, `testament to`, `it is worth
   noting`, `in conclusion` (the full list is `BANNED` in `scripts/check.py`).

---

## 5. EVIDENCE

- **Qur'anic quotations.** Take wording from `translation/` only; never from memory.
  Every exact quotation carries `({C}:{V})` immediately after it — no exceptions, since
  `QUOTETAG` fails the verse otherwise. `python3 scripts/fix_quotetags.py {SURAH}` audits
  a finished chapter for this.
- **Hadith and reports.** Verify before including: existence, collection, number,
  wording, attribution, grade. Never invent a number, chain, collection, grade or
  attribution.
  - Web tool available → verify, then cite (`Musnad Aḥmad 17311, graded ḥasan by
    al-Arnāʾūṭ`), and include only what you actually checked.
  - No web access → do **not** fabricate a reference and do **not** drop the requirement.
    Attribute cautiously (`it is reported that…`, no number), or omit the report, and
    record `UNVERIFIED` in the verse file plus the final report.
- Do not add evidence to look scholarly. Relevant and verified, or nothing.

---

## 6. BATCHING — FIXED, NOT NEGOTIATED

Do not assess your own capacity; that judgement is where chapters get quietly shortened.

- **One verse per file write. Maximum 5 verses per turn. These are constants.**
- Continue from the last PASS in the ledger without asking for approval, and without
  progress reports (a one-line `011: 42/206` only if a session is about to end).
- Never combine two verses into one writing unit, ever. If a turn ends mid-chapter, the
  ledger tells you where to resume.
- A later batch is held to exactly the same standard as the first. Depth, originality,
  verbatim translation and per-verse files are not workload currency.
- Batching changes how much you process at once. It never changes what must exist.

Priority: **gate compliance > completion speed > batch size.**

---

## 7. FINISHING THE CHAPTER

Only after every verse has its own PASS file:

1. Merge in ascending order into `new/{SURAH}.md` (assembly, with a single H1 title line
   at the top: `# Sūrah <Name> (Chapter {N}) — Expanded Verse-by-Verse Commentary`; the
   verse files themselves carry no H1).
2. `python3 scripts/check.py chapter {SURAH}` → must exit 0. Fix the offending verse
   file and re-merge; never patch the merged file alone, or the two diverge.
3. Statistics, new versus `initial/{SURAH}.md`: total words, verses, mean and median
   words/verse, mean mini-headings/verse, expansion ratio, and where your numbers fall
   against §3. `python3 scripts/check.py stats {SURAH}` prints the reference's own bands.
4. Report once, briefly: verses completed, files created, final and initial word counts,
   expansion %, mean words and mini-headings per verse, unusually short/long verses with
   the reason, and every `UNVERIFIED` limit you hit.

Judging the numbers: a verse shorter than its neighbours is fine if the verse is simple;
a verse at the word limit that says nothing is a failure. Deviation from an average is not
the defect — thinness is.

---

## 8. IF A RULE CANNOT BE MET

If you find that a gate and the reference genuinely conflict (the gold text violates what
§3 demands), **stop and say so** rather than picking one. That conflict is a defect in the
standard, not a licence to relax the writing. The fix is to repair the reference or
regenerate the standard:

```bash
python3 scripts/make_standard.py 007
```

Never edit a number in this prompt by hand to make a file pass.

---

## FINAL

Set `SURAH`. Read `new/STANDARD.md`, the one source chunk, the one translation line.
For each verse: reason, write independently, save as its own file, run the gate, update
the ledger. One verse per write, five per turn. No `###`, no untagged quotation, no
translation drift, no paraphrase of `initial/`, no reader-frames, no padding. Never open
`expanded/`, never write `new/007.md`. A verse is done at exit 0. Complete the whole
chapter, then merge → gate → statistics → report.

Start immediately.
