# Sūrah Āli ʿImrān (003) — verses 1–100 written, gated, recorded

Scope of this session: **100 verses, 2 runs of 50** (run 1 = vv. 1–50; run 2 = vv. 51–100).
Every verse was reasoned, written by hand, saved as its own file, passed
`check.py verse`, and then recorded in the ledger by `pipeline.py mark` (which writes
nothing unless the gate exits 0). No chapter merge was attempted: §7 of the standard
merges only when all 200 verses carry a PASS, and 100 remain.

## What exists

| item | value |
|---|---|
| verse files | `new/verse/003_001.md` … `new/verse/003_100.md` |
| ledger | `new/verse/003.ledger.json` — 100/200 PASS, each with a file hash |
| gate re-run | `check.py files 003` → **PASS — 100/100 verse files clean** |
| hash re-check | `pipeline.py verify 003` → **100/200 PASS claims hold** |

## Measured numbers (from the ledger, not from my impression)

| metric | vv. 1–50 | vv. 51–100 | reference band |
|---|---|---|---|
| words/verse | mean 1,021 — median 1,015 — min 954, max 1,203 | mean 1,028 — median 1,025 — min 951, max 1,169 | 950–2,300 (aim 1,000–1,500) |
| bold mini-headings | mean 6.34 — min 5, max 8 | mean 6.64 — min 6, max 7 | 4–12 (aim 5–8) |
| median section | mean 152 — min 128, max 212 | mean 147 — min 131, max 164 | ≥115 fail-line, aim 160–220 |
| total words written | 51,033 | 51,377 | — |

Chapter-wide: **102,410 words** for 100 verses, mean 1,024. Shortest verse in run 2 is
3:80 (951w), longest 3:72 (1,169w). The run-2 spread is tighter than run 1 because the
word-floor failures were fixed by developing an existing section rather than by adding
a new topic, which keeps every section above the fail-line.

## Evidence: everything cited was checked first

Quotations are copied from `translation/` only, each with its `({C}:{V})` tag. Ḥadīth
used in this batch were verified against the collections before use, and are cited with
number:

- Ṣaḥīḥ al-Bukhārī 13 / Ṣaḥīḥ Muslim 45 ("none of you believes until he loves for his brother what he loves for himself", agreed upon) — 3:92
- Ṣaḥīḥ al-Bukhārī 3366 (Abū Dharr: the first mosque on earth is al-Masjid al-Ḥarām, then al-Aqṣā, forty years apart) — 3:96
- Ṣaḥīḥ al-Bukhārī 1587 (Ibn ʿAbbās: on the day of the conquest the Prophet declared the town a sanctuary — no thorn cut, no game chased, nothing picked up except by one who announces it) — 3:97

Run 1's verified ḥadīth (Bukhārī 4547, Muslim 2654, Muslim 804, Tirmidhī 3478, Abū Dāwūd
1496, Ibn Mājah 3855, Muslim 1763, Abū Dāwūd 4344, Tirmidhī 2174, Bukhārī 3431, Bukhārī
3436, Bukhārī 5707, Tirmidhī 3878, Bukhārī 3411, and the Wathilah report in Musnad Aḥmad)
remain as listed in the earlier version of this report.

## UNVERIFIED limits recorded in the verse files

Run 1 (unchanged):

1. **3:12** — the report that the Prophet warned the Banū Qaynuqāʿ in their market-place after Badr, preserved in sīrah and tafsīr without a sound ḥadīth isnād.
2. **3:21** — the report of forty-three prophets killed in one day, on chains in the tafsīr works that are not reliable.

Run 2 (all marked in their verse files with a bracketed `[UNVERIFIED: …]` note):

3. **3:89** — the letter of the Companion who had left the community and the occasion of revelation reported for the verse; chains not examined.
4. **3:92** — the report of the Companion's prized tract of land and the occasion of revelation attached to the verse.
5. **3:96** — the reports tracing the Kaʿbah's foundations to Adam, related in the commentaries from earlier authorities.
6. **3:100** — the report of the man from among the Jews of Madinah who revived the old quarrel between Aws and Khazraj.

In every one of these cases the verse file presents the report as reported background
and states the limit of the claim; no collection or number is invented for it.

## Process notes from this run

- `fixverse_quote.py CHAP V` was used on every verse before gating, so each blockquote is
  byte-exact against `translation/003.txt` rather than re-typed.
- The most frequent gate failure remains the word floor (hit at 3:56, 57, 58, 60, 62, 63,
  65–69, 74, 78, 80, 82–84, 87, 89–94, 96, 97). The fix that worked: extend the argument
  of the thinnest genuine section, never repeat a point already made.
- Reader-frame warnings (the "the sūrah's readers are shown…" tic) appeared at 51, 60, 76,
  78, 88, 91; each was rewritten in the passive or with "the reader" singular, which the
  gate allows up to twice.
- One mistake was made and corrected in this run: files `003_007.md` … `003_013.md`
  (already finished in run 1) were accidentally overwritten and then restored from commit
  `bdc5eee` and re-marked, so the ledger hashes for those verses point at the original,
  run-1 content.

## Resume

```bash
python3 scripts/pipeline.py next 003      # → verse 101
python3 scripts/check.py verse 003 101    # gate (must exit 0)
python3 scripts/pipeline.py mark 003 101  # records PASS only on exit 0
```

Once 200/200 PASS: `pipeline.py assemble 003 --apply`, then `check.py chapter 003`.
