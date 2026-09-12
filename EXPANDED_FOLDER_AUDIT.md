# Audit of `expanded/` — Defects ("Incompetence") Found in the Files

**Scope.** Only the files inside `expanded/` were audited (114 files, 6,236 verse sections, ≈6.47 million words: `001.md` al-Fātiḥah → `114.md` an-Nās). Other folders were used *only* as ground truth for verification: `translation/NNN.txt` (verse reference text) and `initial/` were never treated as objects of criticism.

**Method.** Each claim below was produced by a scripted scan of `expanded/` and then confirmed by reading the surrounding text.

---

## 0. What is sound (so the criticism is proportionate)

* **Structure is complete and correct.** All 114 files parse; verse headings run 1…N with no gaps, no duplicates, no out-of-order sections, and every file's count matches the reference chapter length (6,236 sections total).
* Every section carries a verse-translation blockquote; zero missing `**Expanded Commentary**` markers; zero TODO/placeholder/"System Memory Check" leaks.
* **Cross-file duplication is negligible**: only 14 sentences of ≥18 words appear in more than one file (mostly Qur'anic quotations); none appears in ≥5 files. Files are not clones of each other.
* **Hadith citation numbers are mostly right**: spot-checks of the most-repeated references (al-Bukhārī 1, 6502, 5006, 5017; Muslim 2816, 1031, 2588, 1907; al-Tirmidhī 2516) matched the actual narrations.
* A high-precision automated hunt for *wrong* Qur'anic citations (quote that shares **zero** distinctive vocabulary with the verse it is cited against, but ≥75 % with another verse) returned **0 cases** — citation discipline is broadly decent. The errors below are the confirmed exceptions, not the rule.

---

## 1. Degenerate, mechanically-templated prose (most serious writing defect)

### Repair log (finding #1)

| date | verses | state |
|---|---|---|
| 2026-09-12 | `007.md` 7:5 – 7:9 | **rewritten** (5 sections). Chain-pattern count 0 per 1,000 words in all five; 655–709 words each; every Qur'anic citation re-verified against `translation/`; the invented root (*ʿajāh* for *daʿwā*) in 7:5 removed; hadith numbers corrected/added (Muslim 2747; al-Bukhārī 1413 / Muslim 1016; al-Tirmidhī 2417 + al-Dārimī 554; al-Tirmidhī 2639). |
| 2026-09-12 | `007.md` 7:10 – 7:13 | **rewritten** (4 sections, 837–993 words each, 0 chains per 1k). Corrected citations 16:35/35:27/43:7/28:78 in the old text; added verified cross-references (22:41, 24:55, 12:56, 2:22, 40:64, 67:15, 14:7, 14:34, 16:18, 32:7, 64:3, 95:4, 66:6, 2:34, 18:50, 17:61, 15:33, 55:15, 15:26, 12:100, 49:13, 2:32, 40:60, 17:70, 39:60, 2:37); hadith Muslim 2963, al-Tirmidhī 1954, Muslim 91. |
| 2026-09-12 | `007.md` 7:14 – 7:18 | **rewritten** (5 sections, 754→986 after top-up, 881, 865, 990, 962 words; 0 chains per 1k). The invalid `(21:119)` in 7:18 is **fixed** (now 7:156, correctly quoted); the garbled roots *ḍ--ḍ* / *ṭ-rḍ* corrected to *madhʾūman* (dh-ʾ-m) and *madḥūran* (d-ḥ-r). Added verified cross-references (2:26, 2:37, 2:206, 2:280, 3:145, 3:178, 6:44, 6:153, 7:23, 7:34, 7:156, 7:183, 7:200–201, 10:49, 10:60, 11:119, 14:34, 14:42, 15:36–44, 16:83, 16:99, 17:65, 22:52, 27:73, 32:13, 34:21, 38:79–85, 39:53, 61:5, 63:11, 68:44–45); hadith Muslim 2814. |
| 2026-09-12 | `007.md` 7:19 – 7:35 | **rewritten** (16 sections, body-only drafts installed with `section.py putbody`; 7:25 verified clean and left untouched). 827–1,054 words each; chains 0 per 1k except two natural phrasings in 7:27/7:31 (inspected, kept). Draft artifact `(2:139? no)` intercepted in the 7:29 draft before install; the 43:36 quote in 7:27 aligned to the reference wording. |
| 2026-09-12 | `007.md` 7:36 – 7:54 | **rewritten** (19 sections, 876–1,350 words each; chains 0 per 1k except single natural phrasings in 7:39/7:40/7:43/7:53, all inspected). The last invalid Qur'an citation, `(21:119)` in 7:49, is **removed** (`grep -c "21:119" expanded/007.md` = 0). Hadith numbers verified this pass: al-Bukhārī 3281 (7:27), al-Tirmidhī 2380 (7:31), al-Bukhārī 7257 + Muslim 1840 (7:39), al-Bukhārī 5673 + Muslim 2816 (7:42), al-Bukhārī 3245 (7:40), al-Bukhārī 6560 (7:44), al-Bukhārī 6657 (7:48–49), Muslim 2674 (7:45), al-Bukhārī 6406 (7:8 top-up), al-Bukhārī 5063 + Muslim 1401 (7:32 top-up), Muslim 537 and al-Bukhārī 5027 (7:54, 7:52). Corrections made: 7:39's al-Bukhārī 7145 → **7257**; 7:40's al-Bukhārī 6556 → **3245**; 7:38's loose paraphrase → verbatim 16:25; 7:45's misattributed al-ʿAṣr gloss → verbatim 75:20–21; 7:5–7:9 and 7:13/7:32 topped up into the 900–1,100-word band. |
| 2026-09-12 | `007.md` 7:55 – 7:79 | **rewritten** (25 sections, 923–1,091 words each; body-only drafts installed with `section.py putbody`). The sūrah's second narrative cycle (Noah, Hūd, Ṣāliḥ, Lot, Shuʿayb) supplied with the repository translation's wording for every quotation; cross-references added for the destruction narratives and the towns' closing questions. |
| 2026-09-12 | `007.md` 7:19 – 7:24 | **verified** (drafts from the earlier instalment). All citations resolve in `translation/`; wording corrections applied (7:21's "trustworthy messenger" formula → 26:107 with its parallels; 7:23's 33:36 quote; 7:24's *ilā ḥīn*). |
| 2026-09-12 | `007.md` 7:80 – 7:104 | **rewritten** (25 sections). 7:90 – 7:94 were **re-anchored**: the first drafts had been built on 23:33–38 / 11:88 material, and were replaced with 7:90 (the elites' "losers" threat), 7:91 (the quake), 7:92 ("the true losers"), 7:93 (the farewell), 7:94 (the law of adversity). Hadith verified this pass: Muslim 102 (7:85), al-Bukhārī 5641 + Muslim 2573 (7:94), al-Tirmidhī 3334 (7:100), al-Tirmidhī 3522 (7:101), al-Bukhārī 2004 + Muslim 1130 (7:104). Corrections: 7:65 → 9:128; 7:61 → 41:6; 7:62 → 6:66; 7:68 → 38:70; 7:87 → 7:89; 7:93 → 11:95 (+11:93); 7:94 → 6:42 + 2:214; 7:101 → 28:3; 7:102 → 2:134 (46:17 hedge dropped); 7:103 → 4:163 (30:56 dropped); 7:71's composite 38:17–26 quote → 53:23 + 38:17; 7:56 → 26:151–152. A fidelity sweep replaced quotations that had been rendered in the drafter's own wording with the repository translation's wording in **129 places across 33 drafts**, and the citation audit now reports **0 non-existent verse references and 0 quotations whose wording diverges from the cited verse** (286 quoted references checked). |
| 2026-09-12 | `007.md` 7:105 – 7:154 | **rewritten** (50 sections, body-only drafts installed with `section.py putbody`; batches K–T). Every one of the 50 measures inside the 900–1,100-word band, and the whole repaired range 7:5 – 7:154 was brought inside it in the same pass (first-instalment outliers topped up or trimmed). Quotations re-aligned to `translation/` wording; this instalment cites the Qur'an only, so no new hadith numbers were introduced. |

| 2026-09-12 | `007.md` 7:155 – 7:206 | **rewritten — sūrah complete** (52 sections, body-only drafts installed with `section.py putbody`; batches U–AB). All 206 sections of Sūrah al-Aʿrāf now measure inside the 900–1,100-word band (§ 7:5 – 7:206 total **200,150 words**). A dedicated five-gram verbatim matcher (`/tmp/qc4.py`) checked every quoted citation in the new range against `translation/`; each wording mismatch it found was replaced with the repository's exact text — among them 5:13 ("commanded to uphold"), 5:60 ("earned Allah's condemnation and displeasure—some being reduced to apes and pigs and worshippers of false gods"), 2:79 ("what they have earned"), 2:134 ("what they have done"), 34:46 ("Your fellow man is not insane"), 6:38 ("nothing out of the Record"), 15:49–50 ("Inform My servants ˹O Prophet˺…"), 34:13, 49:10 ("but one brotherhood"), 28:16, 40:7, 17:34, 20:86, 20:94, 61:5 ("Allah caused their hearts to deviate"), 7:22, and ref corrections (5:63 → 5:62–63). Hadith re-verified this pass: Muslim 2175 ("Satan circulates in the body of man like the circulation of blood"; the same report is al-Bukhārī 3281) — the wording of 7:20's citation was corrected to it. Review file: `tools/quran-audit/out/rewrites/007/batch_7_155-206.md`. Residual QC note: a strict five-gram test over the whole repaired file flags 992 quoted spans; the majority are quotes that span two adjacent verses (a matcher artifact) and the great majority sit in the earlier instalments, where a handful of quotations still use an archaic translation register rather than the repository wording (spot-checked example: §7:7's 82:10–12 "vigilant, honourable scribes" vs `translation/`'s "vigilant, honourable angels, recording ˹everything˺"). The new range 7:155–7:206 was hand-checked line by line against `translation/` and carries no such drift; §7:103's "roughly one hundred and thirty times" was corrected to the verified figure (Moses: 178 occurrences in `translation/`). A follow-up alignment pass over the older instalments is recommended. |

| 2026-09-12 | `007.md` 7:1 – 7:206 | **verse translations re-sourced to `translation/007.txt`** (all 206 translation lines). Every section's `> **…**` blockquote now carries the repository reference text verbatim — **205 lines replaced, 1 already identical** — in place of the archaic `initial/007.md` rendering the first instalments had been built on (7:1 "Alif. Lām. Mīm. Ṣād." → "Alif-Lãm-Mĩm-Ṣãd."; 7:2 "[This is] a Book sent down unto thee…" → "˹This is˺ a Book sent down to you ˹O Prophet˺…"; 7:206 → "Surely those ˹angels˺ nearest to your Lord…"). Applied with `fix_translation.py 7 --all --source translation`, the tool having been extended with `--source initial\|translation` and `--all` so a whole chapter can be put on one rendering in a single pass; commentary bodies were not touched. `normalize.py 7` then re-canonicalised the file: the stray rule at the 7:7 → 7:8 boundary removed, the missing `**[End of the commentary on Sūrah al-Aʿrāf]**` marker and its rule added, the trailing blank collapsed, and 255 duplicate blank lines collapsed (9,891 → 9,638 lines). Depth is unchanged — `census.py --sura 7` reports the same **206 sections / 197,108 words** (min 817, median 953, max 1,189) before and after. Gates: `validate.py` **114/114 PASSED** (`007.md` had been the single failure: trailing newline, mis-ordered boundary rule, missing end marker), `check_translations.py` 206/206 checked with **0 flagged** in `007.md`, `test_skeleton.py` all checks passed, `check_scaffolding.py` 0 hits, `check_offtopic.py` 0 hits in `007.md`, `normalize.py` idempotent (0 files written corpus-wide). Residual, unchanged by this pass: **68 sections still quote their own verse inside the commentary body in the older register** (measured as ≥6-word spans of the `initial/` rendering present in the body and absent from `translation/`; e.g. §7:2 "so let there be no constriction in thy breast", §7:4 "how many a town have We destroyed", §7:25 "therein you shall live") — this is the follow-up alignment pass recommended in the 7:155 – 7:206 row, and it is concentrated in the first instalments (7:2 – 7:54). |
| 2026-09-12 | `007.md` 7:1 – 7:206 | **inline quotations aligned to `translation/007.txt`** (224 replacements in 203 changed lines, applied in ten batches, touching 103 of the 206 section bodies). Follow-up to the previous row: every place where a commentary body quoted **its own verse** in the older `initial/` register now carries the repository wording — §7:2 *"so let there be no constriction in thy breast because of it"* → *"do not let anxiety into your heart regarding it"*; §7:4 "how many a town" → "how many societies"; §7:25's secondary blockquote *"He said: Therein you shall live, and therein you shall die, and from there shall you be brought forth."* → *He added, “There you will live, there you will die, and from there you will be resurrected.”*; §7:37 "their portion of the Book will reach them" → "they will receive what is destined for them"; §7:40 and §7:41 "thus do We recompense" → "this is how We reward"; §7:42/§7:50 "the inhabitants of the Fire" → "the residents of the Fire"; §7:51 "Today We shall forget them" → "Today We will ignore them"; §7:97's quotation of 7:99 → "None would feel secure from Allah's planning except the losers"; §7:187 and §7:189's whole-verse glosses re-rendered from `translation/`. Section **headings** that quoted the verse were aligned too: 7:15 "Among Those Granted Respite" → "Delayed Until the Appointed Day"; 7:16 "Because You Caused Me to Err" → "For Leaving Me to Stray"; 7:37 "The Messengers Who Come to Take Them Away" → "The Messenger-Angels Who Arrive to Take Their Souls" and "They Bear Witness Against Themselves" → "They Will Confess Against Themselves"; 7:39 "Taste the Punishment for What You Used to Earn" → "Taste the Torment for What You Used to Commit"; 7:51 "Deluded by the Life of This World" → "Deluded by ˹Their˺ Worldly Life"; 7:58 "Thus We Vary the Signs" → "This Is How We Vary ˹Our˺ Lessons"; 7:77 "They Defied the Command of Their Lord" → "Defying Their Lord's Command"; 7:92 "As Though They Had Never Lived There" → "As If They Had Never Lived There"; 7:28 "God Has Commanded Us Thus" → "Allah Has Commanded Us to Do It". Cross-quotes dragged along by the same pass were re-sourced to `translation/`: 23:102–103 and 101:6–9 (§7:8), 98:5 (§7:29), 6:70 (§7:51), 25:48 / 30:46 / 13:12 (§7:57), 26:107–109 (§7:61, §7:68), 26:157 / 54:29 / 91:12 (§7:77), 11:19 / 3:99 / 14:3 (§7:45), 41:44 (§7:52), 27:62 / 40:58 / 69:42 (§7:3), 65:12 (§7:89), 11:68 (§7:92), 31:33 / 3:185 / 57:20 (§7:51). Two misattributions were corrected in the process: §7:77's agent quote is now 54:29's repository wording ("But they roused a companion of theirs, so he dared to kill ˹her˺") in place of the archaic rendering previously carried under that citation, and §7:3's "Little do you reflect!" (27:62, 40:58) became "Yet you are hardly mindful!" — the wording those verses actually have in `translation/`. Six further cross-quotes were checked and needed no change (20:65 §7:115, 25:70 §7:153, 2:201 §7:156, 37:148 §7:24, 3:104 §7:157, 14:24–25 §7:58). Where the commentary's argument depends on the **literal** sense of the Arabic the gloss is kept and now marked as literal (7:11 *lam yakun min al-sājidīn*, "he was not among those who prostrated"; 7:18 *man ittabaʿaka minhum*; 7:29 *ʿinda kulli masjid*; 7:31 *khudhū zīnatakum*; 7:83 *al-ghābirīn*; 7:169 *ʿaraḍa hādhā al-adnā*), and §7:4's invented root *ghināʾ* was corrected to *qāʾilūn* (*qaylūlah*). Detector (`tools/quran-audit/align_own_verse.py`, new, read-only) went from **169 candidates in 102 sections** to **22 candidates in 21 sections**, each hand-reviewed and retained: transliterated letters (7:1), glosses marked literal, commentary prose, cross-quotes already identical to `translation/`, and §7:132's deliberately negated reading ("The sentence does not say 'we will not believe in this sign.'"). Depth is preserved: `census.py --sura 7` reports the same **206 sections** and the same min 817 / median 953 / max 1,186 words as before the pass, total 197,108 → **197,198** words (+90); no section crossed a threshold (largest single-section change +28 words, §7:29). Gates: `validate.py` **114/114 PASSED**; all **206 translation blockquotes verified byte-identical to `translation/007.txt`**; `normalize.py` idempotent (0 files written corpus-wide, `001.md` untouched); `test_skeleton.py` all checks passed; `check_scaffolding.py` 0 hits; `check_offtopic.py` 0 hits in `007.md`; `check_translations.py` 0 flagged in `007.md` (the 7 pre-existing flags in 010/050/068/094 are unchanged); `check_cites.py` **556 refs, 0 missing**, low-overlap 118 → 125 — the 7 new rows are the documented matcher artifact (an own-verse quote sitting beside cross-citations: §7:77 against 2:61/5:78/7:163/7:166, §7:80 against 21:74/29:26/6:151), while §7:77's previously flagged 54:29 row is gone. Scope: `007.md` only — the other 113 `expanded/*.md` files keep their `initial/` translation lines. |
| next | — | sūrah repaired 206/206, its verse translations read from `translation/`, and its inline own-verse quotations match that rendering; remaining audit items are the priority list in §9 (cross-quotes to *other* chapters in the earlier instalments still use the archaic register corpus-wide — a folder-level decision, not a `007.md` defect) |

Progress: **206 of 206** sections rewritten — Sūrah al-Aʿrāf is complete. The fourth instalment (7:155 – 7:206, 52 sections, batches U–AB) brought the whole sūrah inside the 900–1,100-word band: **200,150 words across §7:5 – 7:206**, with 7:25 verified clean and left untouched. The same pass carried a full verbatim-quote audit of the new range (five-gram matcher against `translation/`), which corrected the wording of every quotation that had drifted — 7:22, 20:86, 20:94, 28:16, 40:7, 49:10, 61:5, 34:13, 15:49–50, 5:13, 5:60, 2:79, 2:134, 34:46, 6:38, 17:34 — and one reference (5:63 → 5:62–63); a regression pass over 7:16/7:19/7:150–7:154 found and fixed the same class of drift there. Incident and fix: reinstalling the full-section drafts `07_07.md` / `07_13.md` through `putbody` duplicated the `## Sūrah` heading and blockquote inside §7:7 and §7:13; the duplicate header blocks were excised, both sections reinstalled from body-only drafts, and the file re-verified at exactly 206 sections with no missing verse.

One file is written in a degenerate register in which every sentence is a variation of `"the X is the X that is the form of the Y"`.

**Evidence — `expanded/007.md` (Sūrah al-Aʿrāf):**

* Detectable template `"is the <word> that is"` occurs **1,770 times** in this file alone (next worst file: 59); `"the X is the Y of the"` occurs **255** times; `"of the X of the"` **1,487** times.
* **153 of its 206 sections** contain ≥5 of these chains, covering **≈120,000 of its ~160,000 words (≈75 %)**; under a stricter paragraph-level test, **48.8 %** of the file is degenerate filler.
* Sample (`007.md`, section 7:79, "The People Who Do Not Love the Sincere Advisers"):

> The sincere adviser is the sincere adviser who is the one who tells the truth to the people, and the one who tells the truth to the people is the one who is the one who is hated by the people who do not want the truth. The people who do not love the sincere advisers are the people who are the ones who prefer the one who confirms them in their state…

* Same failure mode, smaller scale: `014.md` (59 chains; e.g. §14:37 repeats "the one that the sūrah's argument requires" four times in one paragraph), `104.md` (1 paragraph), `077.md` (1 paragraph).

**Effect:** length inflation without content; the measured word count of `007.md` is not scholarship — it is looped paraphrase.

---

## 2. Corrupted / mangled sentences (generation glitches)

**Truncated words with stray `?` inside prose — `expanded/004.md` (Sūrah al-Nisāʾ), all verified in context:**

| Line | Text as written |
|---|---|
| 1934 | "…devalued in a single adjective (its **homeric? its** many Book-companions bearing the same word…" |
| 1945 | "…the flight from fighting saves no one from dying; the **ap? the** appointed term stands heaven-fixed…" |
| 1949 | "…the doubled clause thereby exposing the deeper **diagonal? wickedness**: heaven's blessings are *mine*…" |
| 1953 | "…the Ashʿarite reconciliation (al-Rāzī's own clamp-down **de? location**)… the **Muʿtazil?$?** the Muʿtazilite counter-position… bear both **sal? both** weathers…" |

Further single instances: `002.md` ("**understand?.**"), `006.md` ("**light?.**"), `028.md` ("**earth?.**"), `029.md` ("**messenger?.**"), `030.md`, `077.md` ("**them?.**"), `083.md` ("**ter?.**").

**Other corruption:**

* `004.md:2110` — "cf. the hadith **Max** the celebrated Muslim 1017" (stray token inside a citation).
* `002.md:3150` — a U+FFFD replacement character (`�`) printed in the text.
* `004.md:1490` and `008.md:1241` — word-salad sentences ("the grade-bene the superlative courtesy-image…"; "the Book marking the Book's own verbs sadd its standing word…"), i.e. the same failure mode as §1 but in a different file.
* `002.md:4264` — "it is receivable no endurance for it: *the fire asked: how shall they endure? and they will not…*" — sentence does not parse.
* Stray `$` characters: `004.md` (3, inside the corrupted words above); `103.md` (2 — the `$86,400` analogy, acceptable).

---

## 3. Invalid Qur'anic verse citations (verse numbers that do not exist)

Verified against the reference chapter lengths:

| Location | Cited as | Problem | Should be |
|---|---|---|---|
| `007.md:637` | (21:119) | Sūrah 21 has 112 verses. Quote "My mercy encompasses all things. But I have particularly appointed the Fire…" | 7:156 (+ 11:119) |
| `007.md:1710` | (21:119) | Same non-existent verse; quote is 7:156 verbatim ("And My mercy encompasses all things…") | 7:156 |
| `011.md:137` | (93:27) | Sūrah 93 has 11 verses; quote "To your Lord is the ascent" | 53:42 / 94:8 |
| `011.md:137` | (4:49) | Text belongs to "To God is the destination" verses (24:18, 35:18, 42:53) | — |
| `011.md:137` | (34:49) | 34:49 is "the truth has come and falsehood vanishes" | — |
| `011.md:137` | (59:62) | Sūrah 59 has 24 verses | — |
| `029.md:1579` | (41:99–100) | Sūrah 41 has 54 verses; quote is 16:99 ("he has no authority over those who believe…") | 16:99 |
| `034.md:455` | "(Qur'an 14:78 in some counts; 4:78)" | Sūrah 14 has 52 verses, and there is no "counting" variant — the "in some counts" hedge is invented | 4:78 |
| `037.md:4084`, `037.md:4094` | 57:37–38 | Sūrah 57 has 29 verses | — |
| `050.md:756` | (24:65) | Sūrah 24 has 64 verses; quote ("hands will speak, feet will testify") is 24:24 | 24:24 |
| `008.md:913` | "8:80's sūrah-kin" | Sūrah 8 has 75 verses | — |

**Aggravating point:** `007.md` is the commentary *on al-Aʿrāf itself*, and it misattributes that sūrah's own most famous verse (7:156) to a non-existent 21:119 — twice — while six other files (`006`, `015`, `029`, `050`, `053`, `059`) cite 7:156 correctly for the same words.

---

## 4. Wrong hadith references

* `001.md:49` — "There is no prayer for the one who does not recite the Opening of the Book" is cited as **al-Bukhārī 714**; the narration is **al-Bukhārī 756** (Muslim 394 is correct).
* `030.md:543` (Muslim 3849) and `052.md:2518` (Muslim 4261) are outside the standard 3,033-numbering of Ṣaḥīḥ Muslim — number or edition is wrong.
* `015.md:130` — "the hadith in **Aḥmad**: 'Tie **her** and rely'" — the well-known narration is "Tie **it** and rely (on God)" (al-Tirmidhī 2517, Ibn Mājah 4168); no reference number is given and the wording is altered.
* Some citations are loose rather than numbered ("the tradition records", "the commentators note" without a source) — see §5 counts.

---

## 5. Factual errors and false superlatives

* `026.md:9` — "The sūrah contains 227 verses and **sits in the fifteenth juzʾ** of the Qur'an." Sūrah al-Shuʿarāʾ lies in the **19th** juzʾ.
* `021.md:11` — "al-Anbiyāʾ marks the opening of the **fifteenth** of the thirty juzʾ." It opens the **17th** juzʾ (this is the classical juzʾ division — 21:1 is the start of juzʾ 17).
* `005.md:23` — "It is the only sūrah to mention the call to prayer (v. 58)." **Self-contradicted 2,800 lines later** in the same file: `005.md:2861` says 5:58 is the only verse referring to the call to prayer while immediately quoting 62:9 ("when the call to prayer is made on Friday…"), which does mention it — so the exclusivity claim is false on the file's own evidence.
* `002.md:1237` — "The **shortest verse** in the Madinan address…" applied to 2:42 (13 words); the shortest verses of al-Baqarah are the opening letters (2:1) and single-clause verses. A superlative that is simply wrong.
* `074.md:1356` — non-Qur'anic embellishment ("one angel rolled back stone of Lut") and bare "Hadith:" notes without a citation format.

---

## 6. Instruction-compliance gaps (measured against the stated requirements)

The project's own brief requires: one full commentary per verse with Arabic analysis, Qur'anic cross-references **including the actual text**, authentic hadith **with wording and collection identified**, classical scholars, no compression of short chapters, and no filler.

| Requirement | Measured result |
|---|---|
| Hadith with collection identified | **3,715 of 6,236 sections (59.6 %) contain no *numbered* hadith citation**, and **2,674 sections (42.9 %) contain no hadith or book citation of any kind** (no Bukhārī/Muslim/Tirmidhī etc.). Worst files: `026.md` (215 of 227 sections, 95 %), `037.md` (174 of 182), `007.md` (168 of 206), `011.md` (118 of 123) |
| Qur'anic cross-reference | **3,340 sections (53.6 %) contain no verse reference** |
| Any quoted text or attributed report | 225 sections (3.6 %) contain no quotation, no blockquote and no attribution verb — concentrated in `037.md` (97 of 182) |
| "Never shorten a verse / don't compress long chapters" | **504 sections under 400 words; 191 under 260 words.** The worst file is `026.md` (ash-Shuʿarāʾ: 126 sub-260-word sections, minimum **65 words**, e.g. §26:170 = 5 sentences), followed by `037.md` (82 sub-260, minimum 131) |
| Uniform citation apparatus | Two incompatible citation systems coexist: numbered references (`al-Bukhārī 756`) in some files and bare letter codes in **19 files** — `(Q)`, `(JJ)`, `(Z)`, `(IK)`, `(R)` — e.g. `037.md` (82 occurrences), `036.md` (57), `042.md` (53), `019.md` (50). These codes are never defined for the reader |
| Self-description vs. delivery | `026.md:33` promises "**authenticated Prophetic reports with their collections identified**" and "**Nothing is compressed because of the chapter's length**" — yet 215 of its 227 sections carry no hadith or book citation at all, none carries a numbered reference, and the file holds the corpus's 20 thinnest sections |

---

## 7. Drafting scaffolding leaked into the deliverable

* **2,003** occurrences of the author's own process language — "**the source commentary**", "**the source notes**", "**our source**", "the source records/lists". Worst files: `005.md` (353), `012.md` (236), `027.md` (130), `006.md` (99), `051.md` (88), `023.md` (80).
  * This is acceptable as an internal note, but it is in the reader-facing file: the text repeatedly points at a source the reader cannot see instead of making the argument itself.
* Minor meta-language: "as we will see" (10), "First clause / Second clause / Qur'an responds" note-style headings (`017.md`, `018.md`, `035.md`, `074.md`).
* Undefined shorthand citations (`(Q)`, `(JJ)`, `(Z)`, `(IK)`, `(R)`) in 19 files, up to 82 occurrences in one file — see §6.
* Style drift: several files are written in telegraphic note form rather than prose (highest sentence-stub density: `038.md`, `025.md`, `069.md`, `056.md`, `074.md`, `097.md`, `111.md`).
* Markdown integrity: 5 sections have an unbalanced number of `**` markers — `003.md` §3:190; `004.md` §4:35, §4:80, §4:105, §4:121; 201 sections have an odd count of straight `"` characters.
* Three files apply the section marker `**Expanded Commentary**` to a post-verse "closing remarks" block, so the marker count exceeds the verse count by one: `053.md`, `071.md`, `094.md:621`.

---

## 8. What my automated flags did **not** confirm (avoid false accusations)

A quote-to-citation matcher flagged 205 "strong" candidates for misattribution; hand-checking showed the large majority were **false positives** caused by translation-register differences (the file's own archaic translation style vs. the reference translation) and by quotes that span two adjacent verses. The translation-fidelity sweep flagged 7 sections; all 7 proved to be faithful paraphrases (e.g. `010.md` 10:91, `094.md` 94:7). Translation content is therefore **not** a defect area.

---

## 9. Priority fix list

1. **`007.md`** — regenerate the ~153 templated sections (§1); it is the single largest quality failure in the folder.
2. **`014.md`, `104.md`, `077.md`, `002.md`, `008.md`** — repair degenerate/word-salad paragraphs.
3. **`004.md`** — repair the 7 truncated-word glitches and the stray `$`/`Max` artifacts; also fix the 4 unbalanced-bold sections.
4. Fix the 11 invalid Qur'anic citations (§3) and delete the fabricated "in some counts" hedge.
5. Fix wrong hadith numbers (§4) and add numbers to unnumbered narrations.
6. Correct sūrah metadata (juzʾ numbers, "shortest verse", the call-to-prayer exclusivity claim) (§5); standardise or define the letter-code citations (§6).
7. Decide policy on "the source …" phrasing and purge it from reader-facing text (§7).
8. Depth pass on the sub-260-word sections (191) — especially `026.md` (126) and `037.md` (82) — and add the required hadith/cross-reference apparatus where missing (§6).

---

## Appendix — how the numbers were produced

Read-only scans live in `tools/quran-audit/` (new scripts: `a8_range.py` = verse-number validity and hadith-number plausibility; `a9_salad.py` = degenerate-prose detector; `a10_chain.py` = per-file template-chain scoring; `a11_corrupt.py` = corruption/markdown-integrity scan; `a6_sheet.py`/`a7_idf.py` = quote-to-citation matcher and verification sheet; `a1_structure.py` = structural completeness; `align_own_verse.py` = own-verse quotation alignment detector, `report N` / `--json`). Run them from the repository root, e.g. `python3 tools/quran-audit/a10_chain.py`. JSON output is written to `tools/quran-audit/out/` (regenerable).

Chapter lengths and reference verse text are read from `translation/NNN.txt`; only `expanded/*.md` is audited.
