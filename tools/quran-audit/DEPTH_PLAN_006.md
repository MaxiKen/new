# Depth Plan — expanded/006.md (Sūrat al-Anʿām)

Post-repair baseline (band 1200–1400): 165 sections, 196,573 words,
min 928 / median 1177 / max 1578. Below band: 92 sections. Above band:
11 sections (70:1403, 108:1406, 14:1416, 76:1417, 93:1428, 38:1431,
12:1449, 165:1474, 25:1484, 91:1552, 99:1578). Quote gate at baseline:
810 EXACT, 0 everything; all remaining filler fails depth-only.

## 1. Method

New commentary is added as bold mini-heads appended at the end of each
section (before its closing `---`), one to three heads per section depending
on the word deficit. Every head must satisfy, in order:

1. **Novelty (§7).** The head's material must be absent from the section,
   checked by grep over the section text — never by memory. Existing heads
   are extracted first; candidate parallels are grepped; struck candidates
   are recorded in the batch log below.
2. **Exact quotation (§9).** Every Qur'anic span quoted is fetched from
   `translation/` before drafting and verified byte-identical by the
   insertion script prior to `--apply`. Blockquote form is preferred (it
   carries no body words, so the head's prose alone must clear the floor).
3. **No new fails.** Insertion scripts check head uniqueness across the
   chapter, the full TICS list, and the three chain regexes on the new
   prose. All four gates are re-run after every batch.
4. **No padding.** Heads carry named sources, counted formulae, or genuine
   parallels. A section that cannot support a head is demoted out of Tier-1
   rather than padded (no case arose: every below-band section supported
   at least one head).

Hadith numbers cited in new heads are verified by web search at draft
time; no collection number is written from memory.

## 2. Tier-1 and reduced-floor decisions

**SHORT_6: none.** The six verses of fourteen words or fewer in
translation/006.txt — 6:4, 6:11, 6:18, 6:23, 6:49, 6:85 — are all
self-contained statements (a doctrinal sentence, a complete imperative, an
attribute pair, an eschatological declaration, a threat, a prophet list),
none a muqatta'at, a dialogue clause, or a scene-closing fragment. All
stay in the full band. (6:49 at 957w and 6:85 at 1087w carry full heads
below like any other section.)

**TIER1_6 (24 sections, 14.5%).** The eleven above-band sections take the
raised ceiling (their density is surveyed, not assumed: mercy-and-gathering
at 6:12, the guardian at 6:14, the veils at 6:25, animal communities at
6:38, play-and-ransom at 6:70, Abraham and the star at 6:76, reverence and
Moses at 6:91, fabrication and death at 6:93, rain and plants at 6:99,
insulting the idols at 6:108, succession at 6:165). Thirteen dense
sections are promoted after §7 screens of their existing heads against
candidate new heads:

| verse | base words | screen result |
|---|---|---|
| 6:1 | 1395 | khalaqa/jaʿala distinction already covered (2+2 hits) — struck; corpus-count of the ḥamd formula absent — kept |
| 6:19 | 1387 | 25:1, 48:8, 33:45 all absent — kept |
| 6:44 | 1273 | ʿUqbah istidrāj ḥadīth present (17311), 7:182 present, Qārūn/68:44 present — kept provisionally, 10:24 checked at draft |
| 6:54 | 1389 | 4:17 present; 39:53 absent — kept |
| 6:59 | 1381 | Bukhārī 4778 (five keys) absent; 31:34 present — kept, deepest |
| 6:82 | 1131 | 106:4, 24:55 absent; Khārijite dispute present — kept |
| 6:103 | 1308 | Muslim 179 (veil of light) absent; 75:23, 7:143 present — kept, deepest |
| 6:122 | 1209 | 24:35, 57:12 absent; 57:28 present — kept |
| 6:125 | 1106 | Night-Journey opening (349/163), 10:100 absent — kept |
| 6:141 | 1177 | tenth ḥadīth present (1483); 2:267, 17:26–27 absent — kept |
| 6:145 | 1237 | liver/spleen (3314), fangs/talons (1934) present; "perfected" (5:3's seal) absent — kept as Tier-1, not deepest |
| 6:151 | 1374 | Ibn Masʿūd testament ḥadīth (3070) absent from section; 17:23 present — kept, deepest |
| 6:160 | 1054 | intentions ḥadīth (6491), 2:261 present; fasting exception (1904/1151), 11:114 absent — kept |

**DEEPEST_6 (3): 6:59, 6:103, 6:151** — the keys of the unseen, the vision
verse, the first commandments; each disputed at length by named
authorities. 6:145 was a deepest candidate and is Tier-1 instead (one
genuine head: 5:3's seal).

## 3. Batch log

### Batch 1 (vv. 1–12): 101 → 96 failing

| verse | head added | +words | lands |
|---|---|---|---|
| 6:1 | Twelve Times: The Formula Across the Qur'an (12× "All praise is for Allah" counted in translation/, 9× "Praise be to Allah", 6:45 blockquote) | 165 | 1560 ✓ Tier-1 |
| 6:2 | From It, Into It, From It Again: 20:55 (three-clause biography; 20:55 blockquote) | 90 | 1272 ✓ |
| 6:7 | A Personal Letter for Each: 74:52 (*ṣuḥufan munashsharah*; 4:153 paraphrase) | 121 | 1255 ✓ |
| 6:8 | Why Do You Not Bring Us the Angels: 15:7–8 (15:8 blockquote; *bi'l-ḥaqq* as judgment) | 160 | 1237 ✓ |
| 6:10 | Respite Before the Seizing: 13:32 (*imlā'* between mockery and seizure) | 79 | 1227 ✓ |

Struck: none (all first-choice candidates absent by grep). Gates: skeleton
0, translations 0, quotes 817 EXACT / 0 bad, filler −5.

### Batch 2 (vv. 13–24): 96 → 93 failing

| verse | head added | +words | lands |
|---|---|---|---|
| 6:19 | A Warner to the Whole World: 25:1 (*nadhran lil-ʿālamīn*; 25:1 blockquote, 34:28 inline) | 132 | 1520 ✓ Tier-1 |
| 6:22 | The Sūrah Answers Itself: 6:94 (*ayna* answered; 6:94 span sliced programmatically) | 101 | 1237 ✓ |
| 6:24 | Thighs, Flesh, and Bones: Muslim 2968 (verified via search; 4:42 blockquote) | 225 | 1244 ✓ |

Struck: §24 first choice (36:65/24:24 sealed-mouths head) — both verses
already blockquoted in §23, the neighboring section; cross-section
duplication. Replaced with the ḥadīth-narrative version (Muslim 2968),
distinct material. Gates: quotes 820 EXACT / 0 bad, filler −3.
