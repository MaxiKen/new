# Tafsir Natural-Length Edit — Progress Ledger

Goal (user instruction, 2026-09-20): remove the fixed word-count regime from `expanded/NNN.md`.
Each verse's commentary must simply make sense and be well explained in simple English:
no unnecessary repetition, headings merged/removed where they only fragment, texts rearranged,
underdeveloped verses may grow if genuinely needed. Do NOT cut hadith, cross-references,
stories, or historical accounts (rephrasing allowed). Edits are hand-made verse by verse —
no scripted/pattern-based rewriting. Markdown only; do not regenerate JSON.

Order: sequential from Sūrah 001. Resume exactly where the ledger says.

| chapter | status | edited through | notes |
|---|---|---|---|
| 001 | DONE | all (intro + 1:1–1:7) | 15,321 → 12,303 words. Qudsī Muslim 395 now quoted in full once (intro) instead of 5×; faʿlān/faʿīl grammar only at 1:3; fixed garbled "Erra and beledig" in 1:7. All hadith/citations preserved. |
| 002 | IN PROGRESS | intro + 2:1–2:13 | 2:14 onward untouched (original generated text). Resume at `## Sūrah al-Baqarah 2:14`. Work in batches of ~5 verses: read range, hand-write edited batch to `.edit_batch.md`, splice between verse headers, delete scratch. |

Method (per batch, chapter 002 onward):
1. `grep -n "^## Sūrah al-Baqarah 2:N$"` to find batch boundaries.
2. Read the range with `sed -n 'X,Yp'`.
3. Hand-write the edited verses (quote lines `> **...**` copied verbatim) to `.edit_batch.md`.
4. Splice: `S=<start line> E=<next header line>; head -n $((S-1)) file > /tmp/new; cat .edit_batch.md >> /tmp/new; tail -n +$E file >> /tmp/new; mv /tmp/new file; rm .edit_batch.md`
5. Update this ledger.
