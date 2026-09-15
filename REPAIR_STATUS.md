# Reference repair status — `new/007.md`

Snapshot date: 2026-09-15. Produced by `scripts/check.py chapter 007`.

## Why the reference had to be repaired at all

The pipeline told every model to "study `new/007.md`" as the standard. That file is
280,000 words (~407k tokens). Nothing can hold it, so each model guessed at the standard,
and the guesses drifted. Worse, the prompt's stated numbers contradicted the file they
were derived from, so a model could satisfy the rules or imitate the reference but never
both.

Measured before any changes (bold mini-headings per verse / median section length):

| zone | headings/verse | median section | words/verse |
|---|---|---|---|
| 7:1–117 (approved) | 6.6 (max 12) | 191 (min 102) | 1,369 |
| 7:118–206 (drifted) | **14.6 (max 22)** | **67 (min 53)** | 1,250 |

Words per verse is flat across both zones — the tail lost no content. It cut the same
material into 15 pieces instead of 7. That is why the repair could be structural rather
than a rewrite.

## What was fixed

| # | defect | count | method |
|---|---|---|---|
| 1 | fragmented sections (7:118–206) | 89 verses, 654 heading lines | `check.py merge` — deletes heading lines only; **prose identity asserted byte-for-byte** before writing |
| 2 | untagged Qur'anic quotations | 85 | `fix_quotetags.py` — resolves each quote against an 8-word index of **all 114** `translation/*.txt`; insertions-only proof |
| 3 | `It is worth noting / pausing / noticing …` | 9 | authored, `apply_edits.py` |
| 4 | duplicated + adjacent duplicate mini-headings | 7:35 (2) | authored rename |
| 5 | whole verse re-quoted where a reference sufficed | 7:182 (6:44 twice) | authored |
| 6 | reader-frame tic (`the sūrah's readers are shown that X`) | 342 → **162** | 53 de-framed (`fix_frames.py`), 130 re-cast by hand (`replace_frames.py`) |
| 7 | typo: "the angers who serve" | 7:195 | → "the angels who serve" |
| 8 | duplicate citation tags from tool bug | 22 | collapsed |

Repaired tail now matches the approved zone: **7.3 headings / median 175 words**, against
6.6 / 191 in the healthy zone.

## Remaining (21 verses, all in 7:158–193)

Only two checks still fail, and they are the same defect — the reader-frame tic:

```
FRAME TIC   20 verses   (158,160,161,163,165,173,176,177,179,181,182,184,185,187,188,189,190,191,192,193)
MONOTONY     2 verses   (174,191)
```

104 frame sentences remain; each verse may keep 2, so ~64 must be re-cast. **These are not
deletable:** a triage measured each frame's overlap with its neighbouring sentences and
found that **0 of 104** are restatements — every one carries content, so the fix must be
authored, not scripted or trimmed. Many are mid-sentence (e.g. `…which is a detail the
sūrah's readers are meant to notice:`), so a wrapper-stripping script would corrupt them.

To resume:

```bash
python3 scripts/check.py frames 007 > new/007.frame_worklist.txt   # every sentence, with offsets
# author {verse: [replacement per frame, in order]} then:
python3 scripts/replace_frames.py 007 /tmp/f.json --apply          # exact-count + isolated-span proof
python3 scripts/check.py chapter 007                               # want: PASS, exit 0
python3 scripts/make_standard.py 007                               # regenerate the loadable standard
```

`replace_frames.py` refuses to write unless (a) a verse supplies exactly as many
replacements as it has frames, (b) no replacement still contains a frame, and (c) the
edited spans can be reversed to reproduce the original bytes.

## Everything else passes

`check.py chapter 007` reports no failures for: translation verbatim (206/206), verse
completeness and order, heading counts, section depth, word bands, cross-ref tier,
boilerplate, debris, padding, untagged quotations, and originality (**0.16%** overlap
with `initial/007.md`, longest verbatim run 11 words against a 25-word limit).

## Deliverables for the whole project

- `new/STANDARD.md` — **1,870 words (~2,770 tokens), 147× smaller than the chapter.**
  Generated from the reference by `scripts/make_standard.py`, so the rules and the model
  text cannot drift apart again. Contains one complete model verse (7:15), the
  cross-reference tier (7:23), the measured bands, and a before/after for the tic.
- `standardization_prompt.md` — rewritten around machine-checkable gates, one verse per
  write, ≤5 per turn, a ledger for resumption, and a graded policy for unverifiable
  evidence. Points at `STANDARD.md`, never at the full chapter, and bans reading
  `expanded/`.
- `source_by_verse/{chap}/` — per-verse source chunks (mean 266 words vs 55,412 for the
  whole chapter, a 208× reduction in what must be read):
  `python3 scripts/check.py split initial {CHAP}`.

## Two rules worth keeping in mind

1. **A gate that the reference fails is a broken gate, not a broken reference.** My first
   checker false-failed the gold file 17 times (`not only`, `min_headings=4`). Every
   threshold in `check.py` was then calibrated so the approved zone passes, which is what
   makes the drift zone's failures trustworthy.
2. **Never relax a threshold to make legacy work pass.** `MAX_OVERLAP = 2.5%` rejects 55
   of the 114 existing `expanded/` chapters and 0 reference verses. That is the number to
   enforce going forward — the debt it implies for old chapters is real and is the point.
