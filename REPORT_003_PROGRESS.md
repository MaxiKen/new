# Sūrah Āli ʿImrān (003) — final report: 200/200 PASS, chapter assembled and gated

Scope: the whole chapter, written by hand in four runs of fifty (1–50, 51–100, 101–150,
151–200). Every verse was reasoned from its own source chunk and translation line, saved as
its own file, fixed for its blockquote with `fixverse_quote.py`, passed `check.py verse`
(exit 0), and then recorded by `pipeline.py mark`, which writes nothing unless the gate
exits 0. No gate was relaxed and no verse was marked before it passed.

## What exists

| item | value |
|---|---|
| verse files | `new/verse/003_001.md` … `new/verse/003_200.md` (200 files) |
| ledger | `new/verse/003.ledger.json` — 200/200 PASS, each with a file hash |
| assembled chapter | `new/003.md` (single H1 title line, verses ascending) |
| verse gate | `check.py files 003` → **PASS — 200/200 verse files clean** |
| chapter gate | `check.py chapter 003` → **PASS — 0 verses with FAILs** |
| hash re-check | `pipeline.py verify 003` → **200/200 PASS claims hold** |

## Measured numbers

| metric | final chapter | `initial/003.md` | §3 band |
|---|---|---|---|
| total words | 202,922 | 44,514 | — |
| expansion | **4.56× the initial file** (+158,408 words, ≈ +356%) | — | — |
| verses | 200 | 200 | 200 |
| words/verse | mean 1,015 — median 1,004 — min 955, max 1,203 | mean ≈223 | 950–2,300 |
| bold mini-headings/verse | mean 7.0 — min 5, max 9 | — | 4–12 |
| median section | mean 136 — min 115, max 212 | — | ≥115 fail-line |

Chapter-gate line as printed: `verses 200 | words 201,998 | mean/verse 1,010 |
headings mean 7.0 max 9 | median-section mean 136 min 115` (the gate counts verse bodies
without their heading lines, which is why its mean is slightly below the ledger's).

**Unusually short verses.** 3:15 and 3:158 (955 words each), 3:3 and 3:169 (959), 3:160
(960). Each is a single declaration or petition rather than a narrative: 3:15 lists the
reward of the mindful, 3:158 returns to the theme of death and return, 3:3 names the books
revealed before the Qur'an, and 3:169 states the station of those slain in God's way. Their
sections are developed to the fail-line and no further, because the material does not carry
more without repetition.

**Unusually long verses.** 3:49 (1,203), 3:77 (1,169), 3:85 (1,139), 3:55 (1,134), 3:36
(1,119). These carry several distinct items — 3:49 the signs given to Jesus through the
Gospel narrative, 3:77 the trade of the covenant for a paltry price and its fourfold
judgment, 3:85 the question of the religion accepted by God, 3:55 the dialogue and the
raising of Jesus, 3:36 the vow of Mary's mother and the naming. The length follows the
number of separate subjects the verse holds, not padding.

## Evidence

- Every Qur'anic quotation is copied from `translation/003.txt` and carries its `(C:V)`
  tag; every blockquote was set by `fixverse_quote.py`, so it is byte-exact against line V
  of the translation file.
- Ḥadīth were cited only from collections checked while writing, with numbers. The
  principal ones: Bukhārī 13 / Muslim 45 (3:92); Bukhārī 3366 (3:96); Bukhārī 1587 (3:97);
  Bukhārī 4547 (3:7); Muslim 2654 (3:8); Bukhārī 3431 (3:36); Bukhārī 3436 (3:46);
  Bukhārī 3411 and Tirmidhī 3878 (3:42); Abū Dāwūd 1496 / Tirmidhī 3478 (3:1–2);
  Bukhārī 5707 (3:49); Muslim 1763 (3:13, 3:123); Bukhārī 3039 (3:121);
  Bukhārī 4051 / Muslim 2505 (3:122); Muslim 49a (3:104); Bukhārī 6114 / Muslim 2609
  (3:134); Muslim 1017 (3:137); Bukhārī 6464 / Muslim 2818 (3:136); Muslim 2956 (3:196);
  Bukhārī 2892 / Riyāḍ al-Ṣāliḥīn 1290 (3:200); the Negus's funeral prayer, Bukhārī and
  Muslim (3:199); Bukhārī 1241–42 and Muslim 1905a (3:144–145).

## UNVERIFIED limits recorded in the verse files (11)

Each is marked in its file with a bracketed `[UNVERIFIED: …]` note and presented as
reported background, without inventing a collection or number:

1. **3:12** — the Banū Qaynuqāʿ market-place warning, reported in sīrah/tafsīr without a sound isnād.
2. **3:21** — the report of forty-three prophets killed in one day.
3. **3:89** — the letter of the Companion who left the community and the reported occasion of the verse.
4. **3:92** — the Companion's prized tract of land and the occasion of revelation attached to the verse.
5. **3:96** — the reports tracing the Kaʿbah's foundations to Adam.
6. **3:100** — the man from the Jews of Madinah who revived the quarrel between Aws and Khazraj.
7. **3:113** — the several occasions of revelation recorded for the verse.
8. **3:121** — the report that ʿAbdullāh ibn Ubayy withdrew from Uḥud with about three hundred men.
9. **3:128** — the wounding of the Prophet's face, the damaged tooth, and the words attributed to him.
10. **3:133** — the Byzantine emperor's emissary and the question put to the Prophet about the garden's width.
11. **3:167** — the same withdrawal figure of three hundred men, repeated with the verse's own point.

## Process notes

- The four runs were written as four batches of fifty, as instructed; batching changed the
  amount processed per turn, never what had to exist. Each verse still had to pass its own
  gate before it counted.
- The two recurring gate failures were the 950-word floor and the 115-word median section.
  The fix in every case was to develop an existing section's argument, never to repeat a
  point already made and never to pad.
- The chapter gate caught ten verses (4, 24, 64, 130, 131, 133, 138, 166, 182, 188) whose
  word counts included their heading line and so sat just under the floor once the heading
  was excluded. Each was strengthened with one genuine sentence and re-gated and re-marked
  before the chapter was re-assembled.
- Reader-frame warnings, thin-section warnings and repeated-initial-word warnings remain in
  the gate output by design; they are warnings, not failures, and the chapter passed with 0
  FAILs.
