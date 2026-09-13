# Standardize `expanded/{{NNN}}.md` to the `expanded/007.md` standard

Replace `{{N}}` with the chapter number and `{{NNN}}` with it zero-padded (e.g. `11` / `011`).

Work in one continuous run, verse by verse in ascending order. Ask nothing, report nothing until the
end, and finish the whole chapter. `expanded/001.md`, `translation/*.txt` and `initial/*.md` are
inputs — never modify them.

---

## The standard — what 007 has that the other chapters do not

Audit against these twelve. Each row is the quality, how to produce it, and how to check it.

| # | Quality | How to achieve it | Audit check |
|---|---|---|---|
| 1 | **One section per verse, canonical shape** | `## Sūrah <Name> {{N}}:<verse>` → blank → `> **<verse text>**` → blank → `**Expanded Commentary**` → blank → bold mini-headings with prose → blank → `---`. Nothing else. | Verse numbers run 1→last with no gaps or duplicates. No `###` or deeper. The only H2s are the introduction and the verses. Exactly one `---` per boundary, never inside a body, never doubled. No `****` bold. No lone one-to-three-letter line between two blockquotes |
| 2 | **Blockquote is the repository translation, word for word** | Copy the line `<verse> \| <text>` from `translation/{{NNN}}.txt`. Never use `initial/`'s archaic wording, never retype. | Compare each blockquote to its line in `translation/{{NNN}}.txt`. Any difference is a defect |
| 3 | **The commentary speaks the translation's vocabulary** | When the prose names anything the verse names, use the translation's own English word — not a synonym, not a term from `initial/`. Pattern: *transliteration* — the translation's word. | Read a section against its blockquote. Any second vocabulary for the same thing is a defect |
| 4 | **Each section is about its own verse** | Write from the verse's own content. Where prose drifts to a neighbouring verse, rewrite it on the right verse. | Count the verse's distinctive words (over three letters, minus `that, this, they, them, their, there, these, those, then, than, what, when, which, while, with, from, have, been, were, will, shall, your, and, for, not, but, all, any, who, whom, his, her, its, our, you, was, are, did, does, into, over, only, surely, truly, behold, indeed`) that appear in the body. **Under 15% = drifted** |
| 5 | **Every quotation verbatim, cited on the spot** | Copy contiguous spans from `translation/SSS.txt`. Put `(S:V)` immediately after each closing quote. Keep editorial brackets like `˹O Prophet˺` — they are words. One span, one citation; never join two parts with `…`. Where a span contains a curly apostrophe, quote only the part after it. | Find every quoted span with a citation. Each must be an exact substring of the cited verses. No ellipses. No paraphrase inside quote marks — a literal gloss goes outside them in italics |
| 6 | **Zero hedging near a quotation** | State the citation as exact or drop it. | None of these within a sentence of a quote: `cf.`, `vicinity`, `context`, `sense`, `sequel`, `account`, `clause`, `onward`, `paraphrase`, `and parallels` |
| 7 | **Citations that exist and claims that are measured** | Check every verse number against that sūrah's length in `translation/`. Verify a ḥadīth collection and number by search before writing it; if it will not verify, attribute the report to a named exegete as tradition, or support the point from the Qurʾān instead. Never invent a number, an Arabic root, or a textual variant. | Any verse number above its sūrah's length. Any ḥadīth number that cannot be verified. Any "the only", "the first", "the shortest", "N times", "in the Xth juzʾ" that has not been counted |
| 8 | **Depth inside a band, from real scholarship** | Body words (excluding the blockquote): standard verse **1,200–1,400**; the chapter's densest 15–25% **1,400–1,800**; its 3–5 theological or legal cruxes up to **2,100**; a genuine fragment (fourteen words or fewer, and the disjointed letters, a single dialogue clause, or a scene-closer) **700** minimum with a written reason. Depth comes from vocabulary and roots, cross-references quoted in full, verified ḥadīth, named exegetes and their differences, occasion of revelation, doctrine, ruling and its conditions, and practical implication — never from restatement. | Word count per section. Where the source apparatus in `initial/{{NNN}}.md` is thin, write shorter and record why; **never pad to a number** |
| 9 | **Internal shape** | 8–10 mini-headings per standard section, each naming the argument that follows it, each carrying about 160 words of one developed point, in paragraphs of about 80 words. Headings vary verse to verse. No closing recap — a section ends on its last argument. | Headings per section; words per heading; paragraph lengths; any heading that could sit on a different section; any summary paragraph at the end |
| 10 | **Sound prose** | No self-referential chains — `is the X that is`, `of the X of the`, `the X is the Y of the`, `is in the form of the`. No nominalisation loops. No mini-heading block that restates its own section. **Do not re-quote the section's own verse in English under the blockquote** — if the Arabic transliteration is wanted, keep that alone and drop the English. | Search for the four chain shapes. Look for any block whose claims already appear in the blocks around it. Look for the verse's English text repeated in the body |
| 11 | **No drafting debris** | Deliver prose only. | No `[System Memory Check]`. No `wait`, `actually`, `let me correct`, `TODO`, `TBD`, `FIXME`. No undefined letter codes such as `(Q)`, `(IK)`, `(JJ)`, `(Z)`, `(R)`. No truncated words, stray `?` or `$`, or replacement characters. No sentence repeated verbatim across sections. No boilerplate sentence appearing in every section |
| 12 | **No formulaic tics** | Cut them outright; do not substitute synonyms. | `it is worth noting`, `worth noting`, `it is important to note`, `it should be noted`, `in other words`, `that is to say`, `the point is`, `the fact is`, `as we have seen`, `as noted above`, `it is no accident`, `needless to say`, `to be sure`, `in a sense`, `so to speak`, `it is clear that`, `this is the reason why` |

---

## Audit

1. Read `translation/{{NNN}}.txt` in full. It is the authority for every word of scripture and for
   vocabulary.
2. Read `initial/{{NNN}}.md`. Use its scholarly notes, reports and observations as material. Never
   quote its translation wording; never let its vocabulary into the prose.
3. Read three sections of `expanded/007.md` for register: one long doctrinal section, one narrative
   section, one short fragment. Do not read the whole file.
4. Go through `expanded/{{NNN}}.md` verse by verse and score each section against the twelve.
   **Write the defect list down** — per verse, which numbers fail and what the failure is.
5. Classify every section: **CLEAN** (meets all twelve), **FIX** (fails on items that are local
   edits — 2, 5, 6, 7, 10, 11, 12), or **REWRITE** (fails on 3, 4, 8 or 9, which are properties of
   the whole section).

The list is the work order. Do not start cleaning before it is written.

---

## Clean

Work the list in ascending verse order, in batches of eight to twelve verses.

- **Write each section once, to all twelve.** Do not draft it and come back to fix its quotes or its
  depth afterwards.
- **CLEAN sections are left alone.** Add only what a specific item is missing.
- **FIX sections** get the local edit and nothing else. Where a blockquote is wrong, replace that one
  line; do not touch the commentary.
- **REWRITE sections** are written again from the apparatus in `initial/{{NNN}}.md`, in the register
  of 007: mini-heading naming the argument; the Arabic clause transliterated with its root and its
  grammatical construction; the lexical range of the key word; the theological point following *from*
  the grammar; cross-references quoted verbatim with their citations; a closing sentence stating what
  the verse does rather than summarising what was said.
- **When you rewrite, never lose substance.** Any sentence carrying a quotation, a verse citation or a
  scholar's name survives into the new prose. Where a block restates its section but also adds
  material, remove the block and fold the new material under the heading it belongs to.
- **Fetch every quotation before writing the prose** — all of them, verbatim from `translation/`, in
  one step.
- After each batch, re-check the twelve for those verses and correct what fails.
- Commit per batch. Keep scratch scripts out of the repository.

---

## Finished when

- every verse section meets all twelve, and the audit list is empty;
- every blockquote is identical to its line in `translation/{{NNN}}.txt`;
- every quotation is exact with its citation immediately after it, and there is no hedging, ellipsis
  or paraphrase inside quotes;
- no verse number is invalid, no ḥadīth number is unverified, and no superlative or count is
  unmeasured;
- every section is inside its band for a stated reason, and nothing was padded to reach it;
- the file is written to a plan document listing what was audited, what was fixed, what was rewritten,
  and any section left below its band with the reason.

Then report once: sections cleaned, sections rewritten, final word counts, and anything that could not
be completed and why.
