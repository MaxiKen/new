# Sūrah Āli ʿImrān (003) — verses 1–50 written, gated, recorded

Scope of this session: **50 verses, 4 runs** (13 + 12 + 13 + 12). Every verse was
reasoned, written by hand, saved as its own file, passed `check.py verse`, and then
recorded in the ledger by `pipeline.py mark` (which writes nothing unless the gate
exits 0). No chapter merge was attempted: §7 of the standard merges only when all 200
verses carry a PASS, and 150 remain.

## What exists

| item | value |
|---|---|
| verse files | `new/verse/003_001.md` … `new/verse/003_050.md` |
| ledger | `new/verse/003.ledger.json` — 50/200 PASS, each with a file hash |
| gate re-run | `check.py files 003` → **PASS — 50/50 verse files clean** |
| hash re-check | `pipeline.py verify 003` → **50/200 PASS claims hold** |

## Measured numbers (from the ledger, not from my impression)

| metric | this batch (vv. 1–50) | reference band |
|---|---|---|
| words/verse | mean 1,021 — median 1,014 — min 954, max 1,203 | 950–2,300 (aim 1,000–1,500) |
| bold mini-headings | mean 6.34 — min 5, max 8 | 4–12 (aim 5–8) |
| median section | mean 152 — min 128, max 212 | ≥115 fail-line, aim 160–220 |
| total words written | 51,033 | — |
| source words for the same verses | 11,294 (`source_by_verse/003/`) | — |
| expansion vs. `initial/003.md` | 4.52× | — |

Shortest verses: 3:4 (954w) and 3:24 (954w) — both short, single-claim verses, kept
above the floor by merging thin sections rather than padding. Longest: 3:49 (1,203w),
a verse with four listed miracles; 3:36 (1,119w) and 3:29 (1,109w) follow.

## Evidence: everything cited was checked first

Quotations are copied from `translation/` only, each with its `({C}:{V})` tag. Ḥadīth
used in this batch were verified against the collections before use, and are cited with
number:

- Ṣaḥīḥ al-Bukhārī 4547 (ʿĀʾishah — "beware of them", the followers of the ambiguous verses) — 3:7
- Ṣaḥīḥ Muslim 2654 (hearts between two fingers of the Merciful) — 3:8
- Ṣaḥīḥ Muslim 804 (the two bright ones, al-Baqarah and Āli ʿImrān) and Sunan al-Tirmidhī 3478 / Abū Dāwūd 1496 / Ibn Mājah 3855 (the Greatest Name in 2:163 and the opening of Āli ʿImrān) — 3:1–2
- Ṣaḥīḥ Muslim 1763 (the Prophet's supplication at Badr) — 3:13
- Sunan Abī Dāwūd 4344 and Sunan al-Tirmidhī 2174 ("a word of justice before a tyrannical ruler"; graded ḥasan by virtue of corroborating narrations) — 3:21
- Ṣaḥīḥ al-Bukhārī 3431 (Satan touches every child of Adam except Mary and her son, with Abū Hurayrah reciting 3:36) — 3:36
- Ṣaḥīḥ al-Bukhārī 3436 ("none spoke in the cradle but three") — 3:46
- Ṣaḥīḥ al-Bukhārī 5707 (no contagion; keep away from the leper as from a lion) — 3:49
- Sunan al-Tirmidhī 3878 and Ṣaḥīḥ al-Bukhārī 3411 (the four women; perfection among women) — 3:42
- Musnad Aḥmad, from Wathilah ibn al-Asqaʿ (the descents of the scriptures in Ramaḍān; no number verified, so none is given) — 3:3

## UNVERIFIED limits recorded in the verse files

1. **3:12** — the report that the Prophet warned the Banū Qaynuqāʿ in their market-place
   after Badr is preserved in sīrah and tafsīr literature without a sound ḥadīth isnād;
   it is presented as reported background, with no collection or number cited.
2. **3:21** — the report of forty-three prophets killed in one day, with those who
   protested being killed with them, appears in tafsīr works (Ibn Abī Ḥātim, al-Qurṭubī,
   Ibn Kathīr) on chains that are not reliable; no ḥadīth collection or number is cited.

Both are marked in their verse files with a bracketed `[UNVERIFIED: …]` note.

## Tools added

- `scripts/q.py` — prints the authoritative translation line(s) for given references, so
  every quotation is copied rather than recalled.
- `scripts/fixverse_quote.py CHAP V` — writes line V of `translation/CHAP.txt` into a verse
  file's blockquote exactly (copying, never re-typing, the translation).

## Resume

```bash
python3 scripts/pipeline.py next 003      # → verse 51
python3 scripts/check.py verse 003 51     # gate (must exit 0)
python3 scripts/pipeline.py mark 003 51   # records PASS only on exit 0
```

Once 200/200 PASS: `pipeline.py assemble 003 --apply`, then `check.py chapter 003`.
