# Expanded Commentary — Chapter Comparison & Declared Base Standard

*Corpus: `expanded/` — 114 chapters, 6,236 verse sections, 6,162,050 words. Analysis date: 2026-09-10.*

This document does two things. First it **compares every chapter** on the three requested metrics — average words per verse, average paragraphs per verse, average bold mini-headings per verse — computed from the verse-section *contents*. Second it **declares a base**: the floor every chapter should meet so that the corpus can be extended consistently rather than by guesswork.

## 1. Executive summary

| Measure | Corpus value |
| --- | --- |
| Verse sections analysed | 6,236 — every canonical verse, of which 36 are empty stubs (§3, §6.2) |
| Words in verse commentary | 6,162,050 |
| Paragraphs | 105,825 |
| Standalone bold mini-headings | 30,532 |
| Corpus-average words per verse | 994 |
| Corpus-average paragraphs per verse | 17.1 |
| Corpus-average bold mini-headings per verse | 4.92 |
| Median words per verse | 943 |

Two laws govern these numbers, and both are visible in the data:

1. **Depth per verse falls as chapters get longer.** Correlation between log(verses) and words per verse is **r = -0.64** (paragraphs r = -0.56, headings r = -0.46). A 3-verse sūrah averages ~1,933 words per verse; a 150+-verse sūrah averages ~803. This is why the base declared below is **tiered by chapter length** rather than flat.
2. **Chapter totals are not equal.** Total words per chapter range from 4,661 to 234,840 (median 37,404). Uniform per-verse depth across all 114 chapters would require an enormous, probably undesirable, rewrite of the short sūrahs; the base below specifies a **floor** that all chapters can reach, not a ceiling.

**Compliance at a glance:** 62 of 114 chapters currently meet their tier base; **52 chapters fall below it** (9 on all three metrics, 14 on two, 29 on one). Closing every gap would add roughly **374,210 words**, 3,520 paragraphs and 1,007 mini-headings.

## 2. What is counted, and how

| Quantity | Definition used |
| --- | --- |
| **Verse section** | The block beginning at a level-2 heading carrying a chapter:verse reference (`## Sūrah al-Baqarah 2:1` or `## Sūrah al-Ṣaffāt [37:1]`), up to the next heading. Front matter (`## Introduction to the Sūrah`) is measured separately and excluded from all verse averages. |
| **Word** | A whitespace-separated token containing at least one letter or digit after Markdown decoration (`# * _ ` `>` `|`, links, HTML) is stripped. Punctuation-only tokens are not words. |
| **Paragraph** | A maximal run of consecutive non-blank lines. Structural separators (`---`, the standalone `**Expanded Commentary**` label) break paragraphs and are not themselves paragraphs. A blockquote is one paragraph however many `>` lines it spans. |
| **Bold mini-heading** | A standalone line that is *entirely* bold — `**Heading**` with optional trailing `:` or `.`. Excluded: `**Expanded Commentary**`, `**Verse Translation**`, machine markers. Inline labels such as `**Modern Parallel:** In an age …` are **not** counted as headings; they are tallied separately (123 across the corpus). |
| **Verse translation** | The opening blockquote of each section (the English rendering of the verse, ~24 words, 2.4% of corpus words) **is included** in the primary numbers, because it is part of the section as it stands. The CSVs also carry a translation-excluded word count for anyone who wants the commentary prose alone. |
| **Content-bearing verse** | A verse section with a non-empty body. Empty stubs (heading present, text absent) are reported separately and excluded from the averages, so a missing verse does not silently depress a chapter's average. |

Every number in this report is regenerable with:

```bash
python3 analysis/verse_metrics.py --dir expanded --out analysis
python3 analysis/declare_base.py
```

## 3. Corpus integrity audit (read this before acting on any table)

The comparison was run twice: once on the corpus exactly as it stood, and once after a structural repair. Four defects were found. **None of them involved rewriting commentary prose** — the repairs move or remove Markdown structure only, in 5 files, and are visible in `git diff`.

| # | Defect | Where | Effect on the metrics | Action taken |
| --- | --- | --- | --- | --- |
| 1 | **Verse headings glued to the end of the previous paragraph** (`…closing argument.## Sūrah al-Kahf 18:103`) | `037.md` — 121 headings (verses 37:57–37:177); `018.md` — 1 duplicate | Severe. Chapter 37 counted only 61 of 182 verses, and the whole commentary of verses 57–177 was attributed to verse 37:56, which appeared to hold **20,761 words / 613 paragraphs** instead of ~1,000 / ~17. No other chapter was affected. | Line breaks restored (37), duplicated misfiled heading dropped (18). Chapter 37 now yields **182 contiguous verse sections** — and the repair revealed its real condition: its commentary is thin throughout (median 177 words per verse, no verse above 450), making it the largest single extension job in the corpus (§6). |
| 2 | **Empty verse stubs** — a verse heading with no commentary body | `026.md` — 36 sections (verses 26:104, 122, 125–127, 133–134, 140, 142–145, 147–148, 151–152, 161–164, 173, 175, 177–183, 186, 188, 191, 193, 199, 203, 207, 209, 211–212) | Chapter 26's raw average was dragged down by 36 zeros. Content is genuinely missing. | **Not repaired** — nothing to restore. Listed as a work item in §6.2. |
| 3 | **Generation-harness markers leaked into the files** (`> **[System Memory Check]**: …`) | `037.md` (22), `073.md`, `097.md`, `105.md` (1 each) | Cosmetic; each marker also injected ~25 non-commentary words into a verse. | Removed (25 lines), with the blank run they left behind. |
| 4 | **Mixed line endings** — 58 files CRLF, 56 files LF | Whole corpus | None on the metrics (the analyser normalises), but it makes every diff unreadable if normalised globally. | **Deliberately left alone.** The repair script preserves each file's original line endings so the diff contains only real repairs. |

Post-repair verification: all 114 chapters now carry a contiguous verse sequence (1…N, no gaps, no duplicates) except chapter 26, whose gaps are the 36 empty stubs above; the corpus contains 6,236 verse sections, matching the canonical 6,236 − 36 stubs + 0.

## 4. The comparison

### 4.1 Distribution of the three metrics across the 114 chapters

**Average words per verse**

| min | p10 | p25 | median | p75 | p90 | max |
| --- | --- | --- | --- | --- | --- | --- |
| 209 | 549 | 886 | 1,158 | 1,579 | 1,915 | 3,279 |

**Average paragraphs per verse**

| min | p10 | p25 | median | p75 | p90 | max |
| --- | --- | --- | --- | --- | --- | --- |
| 5.6 | 10.2 | 13.7 | 19.3 | 28.5 | 37.1 | 68.0 |

**Average bold mini-headings per verse**

| min | p10 | p25 | median | p75 | p90 | max |
| --- | --- | --- | --- | --- | --- | --- |
| 1.00 | 3.45 | 4.17 | 5.47 | 6.44 | 8.15 | 11.20 |

The spread is wide — words per verse runs from 209 (Sūrah 37, Al-Ṣaffāt) to 3,279 (Sūrah 110, Al-Naṣr) — a factor of 16. That spread is not random: it tracks chapter length almost mechanically (§4.2), which is the single most important fact for setting a base.

### 4.2 Why the base must be tiered: depth vs chapter length

| Tier | Verses in chapter | Chapters | Verse sections | Median words/verse | Median paras/verse | Median headings/verse | IQR words/verse |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **T1** Very short | 3–10 | 19 | 112 | 1,933 | 34.0 | 7.67 | 482 |
| **T2** Short | 11–30 | 32 | 644 | 1,255 | 19.5 | 5.20 | 594 |
| **T3** Medium | 31–80 | 36 | 1,913 | 1,035 | 16.0 | 5.12 | 550 |
| **T4** Long | 81–150 | 20 | 2,125 | 909 | 13.9 | 4.74 | 632 |
| **T5** Very long | 151+ | 7 | 1,442 | 803 | 8.6 | 3.31 | 343 |

Read the two extreme rows together: the very short sūrahs receive roughly **2.4×** the per-verse word depth of the very long ones. A flat base of, say, 1,000 words per verse would mark every 150+-verse chapter as defective and every short chapter as excellent — it would measure chapter length, not quality. The tiered base in §5 corrects for this.

### 4.3 Every chapter, measured

Sorted by chapter number. `W/v`, `P/v`, `H/v` are the three requested metrics; `Tier` is the length tier; `Base` is compliance against the tier floor declared in §5 (✓ meets, ✗ falls below); `Gap (words)` is the per-verse word shortfall.

| Ch | Sūrah | Verses | Tier | W/v | P/v | H/v | Base | Gap (words) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | :-: | ---: |
| 1 | Al-Fātiḥah | 7 | T1 | 1,933 | 33.4 | 6.43 | ✓ | — |
| 2 | Al-Baqarah | 286 | T5 | 821 | 9.1 | 3.31 | ✓ | — |
| 3 | Āl ʿImrān | 200 | T5 | 796 | 9.6 | 3.67 | ✓ | — |
| 4 | Al-Nisāʾ | 176 | T5 | 931 | 8.6 | 3.44 | ✓ | — |
| 5 | Al-Māʾidah | 120 | T4 | 1,497 | 20.4 | 7.54 | ✓ | — |
| 6 | Al-Anʿām | 165 | T5 | 1,291 | 26.9 | 8.25 | ✓ | — |
| 7 | Al-Aʿrāf | 206 | T5 | 803 | 8.1 | 2.59 | ◐ | — |
| 8 | Al-Anfāl | 75 | T3 | 1,015 | 9.8 | 4.01 | ◐ | — |
| 9 | Al-Tawbah | 129 | T4 | 800 | 10.2 | 3.99 | ◐ | — |
| 10 | Yūnus | 109 | T4 | 627 | 11.8 | 4.27 | ◐ | −73 |
| 11 | Hūd | 123 | T4 | 887 | 8.4 | 3.65 | ◐ | — |
| 12 | Yūsuf | 111 | T4 | 1,131 | 13.8 | 4.32 | ✓ | — |
| 13 | Al-Raʿd | 43 | T3 | 1,095 | 19.4 | 6.44 | ✓ | — |
| 14 | Ibrāhīm | 52 | T3 | 1,016 | 12.9 | 4.88 | ◐ | — |
| 15 | Al-Ḥijr | 99 | T4 | 966 | 9.1 | 3.94 | ◐ | — |
| 16 | Al-Naḥl | 128 | T4 | 1,550 | 29.6 | 8.24 | ✓ | — |
| 17 | Al-Isrāʾ | 111 | T4 | 1,069 | 15.3 | 5.93 | ✓ | — |
| 18 | Al-Kahf | 110 | T4 | 859 | 21.2 | 5.55 | ✓ | — |
| 19 | Maryam | 98 | T4 | 722 | 8.3 | 2.94 | ◐ | — |
| 20 | Ṭā Hā | 135 | T4 | 476 | 7.5 | 3.25 | ✗ | −224 |
| 21 | Al-Anbiyāʾ | 112 | T4 | 1,275 | 13.7 | 3.25 | ◐ | — |
| 22 | Al-Ḥajj | 78 | T3 | 1,004 | 25.2 | 7.04 | ✓ | — |
| 23 | Al-Muʾminūn | 118 | T4 | 1,505 | 23.2 | 8.38 | ✓ | — |
| 24 | Al-Nūr | 64 | T3 | 1,529 | 24.9 | 8.33 | ✓ | — |
| 25 | Al-Furqān | 77 | T3 | 1,136 | 23.2 | 5.94 | ✓ | — |
| 26 | Al-Shuʿarāʾ | 227 **(+36 empty)** | T5 | 271 | 7.1 | 2.92 | ◐ | −259 |
| 27 | Al-Naml | 93 | T4 | 1,754 | 44.1 | 7.02 | ✓ | — |
| 28 | Al-Qaṣaṣ | 88 | T4 | 1,663 | 55.3 | 7.77 | ✓ | — |
| 29 | Al-ʿAnkabūt | 69 | T3 | 1,583 | 16.4 | 6.62 | ✓ | — |
| 30 | Al-Rūm | 60 | T3 | 775 | 10.3 | 4.02 | ◐ | −45 |
| 31 | Luqmān | 34 | T3 | 1,654 | 18.6 | 5.47 | ✓ | — |
| 32 | Al-Sajdah | 30 | T2 | 1,567 | 11.4 | 4.70 | ◐ | — |
| 33 | Al-Aḥzāb | 73 | T3 | 588 | 20.2 | 4.74 | ◐ | −232 |
| 34 | Sabaʾ | 54 | T3 | 410 | 12.8 | 3.02 | ✗ | −410 |
| 35 | Fāṭir | 45 | T3 | 1,524 | 40.7 | 7.11 | ✓ | — |
| 36 | Yā Sīn | 83 | T4 | 419 | 14.0 | 6.00 | ◐ | −281 |
| 37 | Al-Ṣaffāt | 182 | T5 | 209 | 5.6 | 1.00 | ✗ | −321 |
| 38 | Ṣād | 88 | T4 | 533 | 13.9 | 4.82 | ◐ | −167 |
| 39 | Al-Zumar | 75 | T3 | 462 | 11.0 | 3.48 | ✗ | −358 |
| 40 | Ghāfir | 85 | T4 | 932 | 11.4 | 4.65 | ✓ | — |
| 41 | Fuṣṣilat | 54 | T3 | 886 | 10.6 | 4.06 | ◐ | — |
| 42 | Al-Shūrā | 53 | T3 | 1,000 | 14.1 | 4.13 | ✓ | — |
| 43 | Al-Zukhruf | 89 | T4 | 501 | 17.5 | 4.43 | ◐ | −199 |
| 44 | Al-Dukhān | 59 | T3 | 1,036 | 10.7 | 4.71 | ◐ | — |
| 45 | Al-Jāthiyah | 37 | T3 | 1,358 | 15.3 | 5.51 | ✓ | — |
| 46 | Al-Aḥqāf | 35 | T3 | 812 | 14.6 | 4.03 | ◐ | −8 |
| 47 | Muḥammad | 38 | T3 | 2,236 | 40.5 | 6.50 | ✓ | — |
| 48 | Al-Fatḥ | 29 | T2 | 718 | 19.7 | 4.45 | ◐ | −252 |
| 49 | Al-Ḥujurāt | 18 | T2 | 2,054 | 45.6 | 8.22 | ✓ | — |
| 50 | Qāf | 45 | T3 | 1,420 | 18.6 | 5.64 | ✓ | — |
| 51 | Al-Dhāriyāt | 60 | T3 | 927 | 16.4 | 5.45 | ✓ | — |
| 52 | Al-Ṭūr | 49 | T3 | 1,034 | 23.8 | 5.65 | ✓ | — |
| 53 | Al-Najm | 62 | T3 | 1,124 | 13.7 | 5.47 | ✓ | — |
| 54 | Al-Qamar | 55 | T3 | 1,522 | 37.1 | 5.73 | ✓ | — |
| 55 | Al-Raḥmān | 78 | T3 | 962 | 15.6 | 5.79 | ✓ | — |
| 56 | Al-Wāqiʿah | 96 | T4 | 727 | 20.4 | 8.79 | ✓ | — |
| 57 | Al-Ḥadīd | 29 | T2 | 1,304 | 12.8 | 4.34 | ◐ | — |
| 58 | Al-Mujādilah | 22 | T2 | 899 | 19.1 | 4.32 | ◐ | −71 |
| 59 | Al-Ḥashr | 24 | T2 | 1,233 | 19.3 | 5.67 | ✓ | — |
| 60 | Al-Mumtaḥanah | 13 | T2 | 1,743 | 33.3 | 7.54 | ✓ | — |
| 61 | Al-Ṣaff | 14 | T2 | 1,556 | 19.5 | 6.36 | ✓ | — |
| 62 | Al-Jumuʿah | 11 | T2 | 988 | 17.2 | 4.00 | ◐ | — |
| 63 | Al-Munāfiqūn | 11 | T2 | 1,480 | 30.1 | 6.18 | ✓ | — |
| 64 | Al-Taghābun | 18 | T2 | 1,872 | 20.2 | 6.06 | ✓ | — |
| 65 | Al-Ṭalāq | 12 | T2 | 1,560 | 26.0 | 5.83 | ✓ | — |
| 66 | Al-Taḥrīm | 12 | T2 | 1,658 | 22.3 | 5.83 | ✓ | — |
| 67 | Al-Mulk | 30 | T2 | 403 | 12.6 | 3.03 | ✗ | −567 |
| 68 | Al-Qalam | 52 | T3 | 818 | 20.5 | 5.23 | ◐ | −2 |
| 69 | Al-Ḥāqqah | 52 | T3 | 329 | 13.2 | 3.98 | ◐ | −491 |
| 70 | Al-Maʿārij | 44 | T3 | 762 | 11.5 | 3.16 | ✗ | −58 |
| 71 | Nūḥ | 28 | T2 | 1,281 | 21.2 | 5.21 | ✓ | — |
| 72 | Al-Jinn | 28 | T2 | 932 | 31.6 | 5.89 | ◐ | −38 |
| 73 | Al-Muzzammil | 20 | T2 | 404 | 13.8 | 3.80 | ✗ | −566 |
| 74 | Al-Muddaththir | 56 | T3 | 736 | 25.0 | 6.02 | ◐ | −84 |
| 75 | Al-Qiyāmah | 40 | T3 | 376 | 14.8 | 3.52 | ◐ | −444 |
| 76 | Al-Insān | 31 | T3 | 1,068 | 19.1 | 4.06 | ✓ | — |
| 77 | Al-Mursalāt | 50 | T3 | 1,315 | 10.7 | 4.74 | ◐ | — |
| 78 | Al-Nabaʾ | 40 | T3 | 1,622 | 17.4 | 4.72 | ✓ | — |
| 79 | Al-Nāziʿāt | 46 | T3 | 1,390 | 38.6 | 5.98 | ✓ | — |
| 80 | ʿAbasa | 42 | T3 | 1,178 | 15.4 | 5.02 | ✓ | — |
| 81 | Al-Takwīr | 29 | T2 | 973 | 17.1 | 4.00 | ◐ | — |
| 82 | Al-Infiṭār | 19 | T2 | 1,487 | 32.6 | 6.05 | ✓ | — |
| 83 | Al-Muṭaffifīn | 36 | T3 | 1,138 | 15.6 | 4.42 | ✓ | — |
| 84 | Al-Inshiqāq | 25 | T2 | 1,223 | 17.2 | 5.76 | ✓ | — |
| 85 | Al-Burūj | 22 | T2 | 1,004 | 16.6 | 3.14 | ◐ | — |
| 86 | Al-Ṭāriq | 17 | T2 | 1,675 | 33.4 | 9.88 | ✓ | — |
| 87 | Al-Aʿlā | 19 | T2 | 1,278 | 15.7 | 3.47 | ◐ | — |
| 88 | Al-Ghāshiyah | 26 | T2 | 877 | 19.5 | 4.96 | ◐ | −93 |
| 89 | Al-Fajr | 30 | T2 | 949 | 15.7 | 5.10 | ◐ | −21 |
| 90 | Al-Balad | 20 | T2 | 1,205 | 13.3 | 5.05 | ◐ | — |
| 91 | Al-Shams | 15 | T2 | 1,229 | 21.1 | 5.87 | ✓ | — |
| 92 | Al-Layl | 21 | T2 | 1,060 | 12.1 | 5.52 | ◐ | — |
| 93 | Al-Ḍuḥā | 11 | T2 | 951 | 19.3 | 5.00 | ◐ | −19 |
| 94 | Al-Sharḥ | 8 | T1 | 2,347 | 34.0 | 7.50 | ✓ | — |
| 95 | Al-Tīn | 8 | T1 | 2,016 | 23.9 | 6.38 | ◐ | — |
| 96 | Al-ʿAlaq | 19 | T2 | 1,640 | 48.4 | 8.74 | ✓ | — |
| 97 | Al-Qadr | 5 | T1 | 932 | 25.6 | 6.00 | ✗ | −868 |
| 98 | Al-Bayyinah | 8 | T1 | 2,434 | 68.0 | 9.75 | ✓ | — |
| 99 | Al-Zalzalah | 8 | T1 | 1,804 | 37.1 | 5.00 | ◐ | — |
| 100 | Al-ʿĀdiyāt | 11 | T2 | 1,404 | 24.0 | 5.18 | ✓ | — |
| 101 | Al-Qāriʿah | 11 | T2 | 1,608 | 25.1 | 5.09 | ✓ | — |
| 102 | Al-Takāthur | 8 | T1 | 1,661 | 37.1 | 7.88 | ◐ | −139 |
| 103 | Al-ʿAṣr | 3 | T1 | 1,827 | 59.7 | 7.67 | ✓ | — |
| 104 | Al-Humazah | 9 | T1 | 2,484 | 29.3 | 5.89 | ◐ | — |
| 105 | Al-Fīl | 5 | T1 | 2,003 | 33.2 | 7.80 | ✓ | — |
| 106 | Quraysh | 4 | T1 | 2,558 | 38.8 | 7.75 | ✓ | — |
| 107 | Al-Māʿūn | 7 | T1 | 1,282 | 25.1 | 4.29 | ✗ | −518 |
| 108 | Al-Kawthar | 3 | T1 | 2,224 | 47.3 | 8.00 | ✓ | — |
| 109 | Al-Kāfirūn | 6 | T1 | 1,803 | 34.7 | 7.00 | ✓ | — |
| 110 | Al-Naṣr | 3 | T1 | 3,279 | 35.3 | 9.67 | ✓ | — |
| 111 | Al-Masad | 5 | T1 | 1,343 | 36.0 | 8.60 | ◐ | −457 |
| 112 | Al-Ikhlāṣ | 4 | T1 | 2,222 | 29.0 | 7.75 | ✓ | — |
| 113 | Al-Falaq | 5 | T1 | 1,829 | 31.2 | 11.20 | ✓ | — |
| 114 | Al-Nās | 6 | T1 | 1,866 | 24.0 | 6.00 | ◐ | — |

Legend: ✓ meets base on all three metrics · ◐ below base on one or two · ✗ below base on all three.

### 4.4 Rankings

**Average words per verse**

| Highest | value | Lowest | value |
| --- | --- | --- | --- |
| 110. Al-Naṣr | 3,279 | 37. Al-Ṣaffāt | 209 |
| 106. Quraysh | 2,558 | 26. Al-Shuʿarāʾ | 271 |
| 104. Al-Humazah | 2,484 | 69. Al-Ḥāqqah | 329 |
| 98. Al-Bayyinah | 2,434 | 75. Al-Qiyāmah | 376 |
| 94. Al-Sharḥ | 2,347 | 67. Al-Mulk | 403 |
| 47. Muḥammad | 2,236 | 73. Al-Muzzammil | 404 |
| 108. Al-Kawthar | 2,224 | 34. Sabaʾ | 410 |
| 112. Al-Ikhlāṣ | 2,222 | 36. Yā Sīn | 419 |

**Average paragraphs per verse**

| Highest | value | Lowest | value |
| --- | --- | --- | --- |
| 98. Al-Bayyinah | 68.0 | 37. Al-Ṣaffāt | 5.6 |
| 103. Al-ʿAṣr | 59.7 | 26. Al-Shuʿarāʾ | 7.1 |
| 28. Al-Qaṣaṣ | 55.3 | 20. Ṭā Hā | 7.5 |
| 96. Al-ʿAlaq | 48.4 | 7. Al-Aʿrāf | 8.1 |
| 108. Al-Kawthar | 47.3 | 19. Maryam | 8.3 |
| 49. Al-Ḥujurāt | 45.6 | 11. Hūd | 8.4 |
| 27. Al-Naml | 44.1 | 4. Al-Nisāʾ | 8.6 |
| 35. Fāṭir | 40.7 | 2. Al-Baqarah | 9.1 |

**Average bold mini-headings per verse**

| Highest | value | Lowest | value |
| --- | --- | --- | --- |
| 113. Al-Falaq | 11.20 | 37. Al-Ṣaffāt | 1.00 |
| 86. Al-Ṭāriq | 9.88 | 7. Al-Aʿrāf | 2.59 |
| 98. Al-Bayyinah | 9.75 | 26. Al-Shuʿarāʾ | 2.92 |
| 110. Al-Naṣr | 9.67 | 19. Maryam | 2.94 |
| 56. Al-Wāqiʿah | 8.79 | 34. Sabaʾ | 3.02 |
| 96. Al-ʿAlaq | 8.74 | 67. Al-Mulk | 3.03 |
| 111. Al-Masad | 8.60 | 85. Al-Burūj | 3.14 |
| 23. Al-Muʾminūn | 8.38 | 70. Al-Maʿārij | 3.16 |

## 5. The declared base

The base is **derived from the corpus's own distribution**, per length tier, with three levels:

- **Base floor** — the 25th percentile of the tier. *This is the standard to declare and enforce.* A chapter below its floor must be extended.
- **Standard** — the tier median. The typical, healthy expectation; new or reworked content should aim here.
- **Extended** — the tier 75th percentile. Achievable excellence; nothing needs to reach it, but it shows what the same authorial voice already produces.

### 5.1 The base spec

| Tier | Verses | Ch | W/verse **floor** | standard | extended | P/verse **floor** | standard | extended | H/verse **floor** | standard | extended |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **T1** Very short | 3–10 | 19 | **1,800** | 1,930 | 2,290 | **29.0** | 34.0 | 37.0 | **6.25** | 7.75 | 8.00 |
| **T2** Short | 11–30 | 32 | **970** | 1,260 | 1,560 | **16.5** | 19.5 | 25.5 | **4.50** | 5.25 | 6.00 |
| **T3** Medium | 31–80 | 36 | **820** | 1,040 | 1,370 | **13.0** | 16.0 | 21.0 | **4.00** | 5.00 | 5.75 |
| **T4** Long | 81–150 | 20 | **700** | 910 | 1,330 | **11.0** | 14.0 | 20.5 | **4.00** | 4.75 | 7.25 |
| **T5** Very long | 151+ | 7 | **530** | 800 | 880 | **7.5** | 8.5 | 9.5 | **2.75** | 3.25 | 3.50 |

A chapter **meets the base** when all three of its averages are at or above its tier floor. A verse section, individually, is *thin* when it falls below the per-verse floor in §5.3.

### 5.2 Plain-language statement of the base

> **Base standard.** Every chapter of the expanded commentary is expected to average, per verse section, at least the following — any chapter below its row is marked for extension: **3–10 verses**: 1,800 words / 29.0 paragraphs / 6.25 mini-headings; **11–30 verses**: 970 words / 16.5 paragraphs / 4.50 mini-headings; **31–80 verses**: 820 words / 13.0 paragraphs / 4.00 mini-headings; **81–150 verses**: 700 words / 11.0 paragraphs / 4.00 mini-headings; **151 or more verses**: 530 words / 7.5 paragraphs / 2.75 mini-headings. Averages at the tier median mark a chapter as sound; averages at the 75th percentile mark it as extended.

### 5.3 Annex — the per-verse floor (for spot repairs)

Chapter averages can hide individual thin verses, so a second, verse-level floor is declared. No verse section in the corpus should fall below **420 words, 6 paragraphs and 3 mini-headings** (≈ the 10th percentile of the 6,200 content-bearing sections). Within the current corpus, 646 sections are below the word floor, 356 below the paragraph floor and 493 below the heading floor; they are itemised in `analysis/verse_level_shortfall.csv`.

## 6. Extension worklist

### 6.1 Chapters below the base, in priority order

Priority is by number of failed metrics, then by total words needed to reach the floor.

| Ch | Sūrah | Tier | W/v actual / floor | P/v actual / floor | H/v actual / floor | Below on | Words to add | Paras to add | Headings to add |
| ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 37 | Al-Ṣaffāt | T5 | 209 / 530 | 5.6 / 7.5 | 1.00 / 2.75 | W/v, P/v, H/v | 58,422 | 339 | 318 |
| 20 | Ṭā Hā | T4 | 476 / 700 | 7.5 / 11.0 | 3.25 / 4.00 | W/v, P/v, H/v | 30,267 | 472 | 101 |
| 39 | Al-Zumar | T3 | 462 / 820 | 11.0 / 13.0 | 3.48 / 4.00 | W/v, P/v, H/v | 26,872 | 149 | 39 |
| 34 | Sabaʾ | T3 | 410 / 820 | 12.8 / 13.0 | 3.02 / 4.00 | W/v, P/v, H/v | 22,118 | 8 | 53 |
| 67 | Al-Mulk | T2 | 403 / 970 | 12.6 / 16.5 | 3.03 / 4.50 | W/v, P/v, H/v | 17,004 | 116 | 44 |
| 73 | Al-Muzzammil | T2 | 404 / 970 | 13.8 / 16.5 | 3.80 / 4.50 | W/v, P/v, H/v | 11,324 | 54 | 14 |
| 97 | Al-Qadr | T1 | 932 / 1,800 | 25.6 / 29.0 | 6.00 / 6.25 | W/v, P/v, H/v | 4,339 | 17 | 1 |
| 107 | Al-Māʿūn | T1 | 1,282 / 1,800 | 25.1 / 29.0 | 4.29 / 6.25 | W/v, P/v, H/v | 3,627 | 27 | 14 |
| 70 | Al-Maʿārij | T3 | 762 / 820 | 11.5 / 13.0 | 3.16 / 4.00 | W/v, P/v, H/v | 2,530 | 66 | 37 |
| 26 | Al-Shuʿarāʾ | T5 | 271 / 530 | 7.1 / 7.5 | 2.92 / 2.75 | W/v, P/v | 49,450 | 76 | 0 |
| 69 | Al-Ḥāqqah | T3 | 329 / 820 | 13.2 / 13.0 | 3.98 / 4.00 | W/v, H/v | 25,532 | 0 | 1 |
| 75 | Al-Qiyāmah | T3 | 376 / 820 | 14.8 / 13.0 | 3.52 / 4.00 | W/v, H/v | 17,756 | 0 | 19 |
| 48 | Al-Fatḥ | T2 | 718 / 970 | 19.7 / 16.5 | 4.45 / 4.50 | W/v, H/v | 7,302 | 0 | 1 |
| 30 | Al-Rūm | T3 | 775 / 820 | 10.3 / 13.0 | 4.02 / 4.00 | W/v, P/v | 2,718 | 160 | 0 |
| 58 | Al-Mujādilah | T2 | 899 / 970 | 19.1 / 16.5 | 4.32 / 4.50 | W/v, H/v | 1,555 | 0 | 4 |
| 89 | Al-Fajr | T2 | 949 / 970 | 15.7 / 16.5 | 5.10 / 4.50 | W/v, P/v | 618 | 25 | 0 |
| 9 | Al-Tawbah | T4 | 800 / 700 | 10.2 / 11.0 | 3.99 / 4.00 | P/v, H/v | 0 | 104 | 1 |
| 11 | Hūd | T4 | 887 / 700 | 8.4 / 11.0 | 3.65 / 4.00 | P/v, H/v | 0 | 320 | 43 |
| 15 | Al-Ḥijr | T4 | 966 / 700 | 9.1 / 11.0 | 3.94 / 4.00 | P/v, H/v | 0 | 188 | 6 |
| 19 | Maryam | T4 | 722 / 700 | 8.3 / 11.0 | 2.94 / 4.00 | P/v, H/v | 0 | 260 | 104 |
| 57 | Al-Ḥadīd | T2 | 1,304 / 970 | 12.8 / 16.5 | 4.34 / 4.50 | P/v, H/v | 0 | 108 | 5 |
| 87 | Al-Aʿlā | T2 | 1,278 / 970 | 15.7 / 16.5 | 3.47 / 4.50 | P/v, H/v | 0 | 16 | 20 |
| 114 | Al-Nās | T1 | 1,866 / 1,800 | 24.0 / 29.0 | 6.00 / 6.25 | P/v, H/v | 0 | 30 | 2 |
| 36 | Yā Sīn | T4 | 419 / 700 | 14.0 / 11.0 | 6.00 / 4.00 | W/v | 23,298 | 0 | 0 |
| 43 | Al-Zukhruf | T4 | 501 / 700 | 17.5 / 11.0 | 4.43 / 4.00 | W/v | 17,675 | 0 | 0 |
| 33 | Al-Aḥzāb | T3 | 588 / 820 | 20.2 / 13.0 | 4.74 / 4.00 | W/v | 16,900 | 0 | 0 |
| 38 | Ṣād | T4 | 533 / 700 | 13.9 / 11.0 | 4.82 / 4.00 | W/v | 14,731 | 0 | 0 |
| 10 | Yūnus | T4 | 627 / 700 | 11.8 / 11.0 | 4.27 / 4.00 | W/v | 7,957 | 0 | 0 |
| 74 | Al-Muddaththir | T3 | 736 / 820 | 25.0 / 13.0 | 6.02 / 4.00 | W/v | 4,726 | 0 | 0 |
| 88 | Al-Ghāshiyah | T2 | 877 / 970 | 19.5 / 16.5 | 4.96 / 4.50 | W/v | 2,428 | 0 | 0 |
| 111 | Al-Masad | T1 | 1,343 / 1,800 | 36.0 / 29.0 | 8.60 / 6.25 | W/v | 2,283 | 0 | 0 |
| 102 | Al-Takāthur | T1 | 1,661 / 1,800 | 37.1 / 29.0 | 7.88 / 6.25 | W/v | 1,110 | 0 | 0 |
| 72 | Al-Jinn | T2 | 932 / 970 | 31.6 / 16.5 | 5.89 / 4.50 | W/v | 1,072 | 0 | 0 |
| 46 | Al-Aḥqāf | T3 | 812 / 820 | 14.6 / 13.0 | 4.03 / 4.00 | W/v | 280 | 0 | 0 |
| 93 | Al-Ḍuḥā | T2 | 951 / 970 | 19.3 / 16.5 | 5.00 / 4.50 | W/v | 212 | 0 | 0 |
| 68 | Al-Qalam | T3 | 818 / 820 | 20.5 / 13.0 | 5.23 / 4.00 | W/v | 104 | 0 | 0 |
| 7 | Al-Aʿrāf | T5 | 803 / 530 | 8.1 / 7.5 | 2.59 / 2.75 | H/v | 0 | 0 | 33 |
| 8 | Al-Anfāl | T3 | 1,015 / 820 | 9.8 / 13.0 | 4.01 / 4.00 | P/v | 0 | 244 | 0 |
| 14 | Ibrāhīm | T3 | 1,016 / 820 | 12.9 / 13.0 | 4.88 / 4.00 | P/v | 0 | 5 | 0 |
| 21 | Al-Anbiyāʾ | T4 | 1,275 / 700 | 13.7 / 11.0 | 3.25 / 4.00 | H/v | 0 | 0 | 84 |
| 32 | Al-Sajdah | T2 | 1,567 / 970 | 11.4 / 16.5 | 4.70 / 4.50 | P/v | 0 | 154 | 0 |
| 41 | Fuṣṣilat | T3 | 886 / 820 | 10.6 / 13.0 | 4.06 / 4.00 | P/v | 0 | 131 | 0 |
| 44 | Al-Dukhān | T3 | 1,036 / 820 | 10.7 / 13.0 | 4.71 / 4.00 | P/v | 0 | 138 | 0 |
| 62 | Al-Jumuʿah | T2 | 988 / 970 | 17.2 / 16.5 | 4.00 / 4.50 | H/v | 0 | 0 | 6 |
| 77 | Al-Mursalāt | T3 | 1,315 / 820 | 10.7 / 13.0 | 4.74 / 4.00 | P/v | 0 | 116 | 0 |
| 81 | Al-Takwīr | T2 | 973 / 970 | 17.1 / 16.5 | 4.00 / 4.50 | H/v | 0 | 0 | 14 |
| 85 | Al-Burūj | T2 | 1,004 / 970 | 16.6 / 16.5 | 3.14 / 4.50 | H/v | 0 | 0 | 30 |
| 90 | Al-Balad | T2 | 1,205 / 970 | 13.3 / 16.5 | 5.05 / 4.50 | P/v | 0 | 64 | 0 |
| 92 | Al-Layl | T2 | 1,060 / 970 | 12.1 / 16.5 | 5.52 / 4.50 | P/v | 0 | 92 | 0 |
| 95 | Al-Tīn | T1 | 2,016 / 1,800 | 23.9 / 29.0 | 6.38 / 6.25 | P/v | 0 | 41 | 0 |
| 99 | Al-Zalzalah | T1 | 1,804 / 1,800 | 37.1 / 29.0 | 5.00 / 6.25 | H/v | 0 | 0 | 10 |
| 104 | Al-Humazah | T1 | 2,484 / 1,800 | 29.3 / 29.0 | 5.89 / 6.25 | H/v | 0 | 0 | 3 |

The three heaviest single jobs are **37. Al-Ṣaffāt** (T5, 58,422 words, currently 209 w/v against a floor of 530), **26. Al-Shuʿarāʾ** (T5, 49,450 words, currently 271 w/v against a floor of 530), **20. Ṭā Hā** (T4, 30,267 words, currently 476 w/v against a floor of 700). They alone account for 138,139 of the 374,210 total words, so a staged rollout should start there.

Totals: **374,210 words**, 3,520 paragraphs, 1,007 mini-headings to bring every chapter to its floor. Reaching the tier **standard** instead of merely the floor would require more; the floors are the minimum defensible target.

### 6.2 Content that is missing outright (higher priority than any average)

| Where | What is missing | Suggested action |
| --- | --- | --- |
| `expanded/026.md` | 36 verse sections exist as headings with no commentary: 26:104, 122, 125–127, 133–134, 140, 142–145, 147–148, 151–152, 161–164, 173, 175, 177–183, 186, 188, 191, 193, 199, 203, 207, 209, 211–212 | Write each as a full section at the **T5 floor** (535+ words, 7.5+ paragraphs, 3+ headings) → ≈ 19,000 words. Averages cannot be trusted for this chapter until they are filled. |
| `expanded/037.md` | Nothing *missing*, but structurally it was the worst file in the corpus and, once repaired, it is also the thinnest: 182 sections averaging 209 words / 4 paragraphs / 3 headings against a T5 floor of 530 / 7.5 / 2.75. | Extend verse-by-verse to the T5 floor — the single largest job (≈58,000 words). The 121 heading breaks restored in this pass must not be lost again; re-verify with `python3 analysis/check_base.py`. |

### 6.3 Cheapest wins

| Ch | Sūrah | Tier | Below on | Words to add | Paras to add | Headings to add | Effort score |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |
| 68 | Al-Qalam | T3 | W/v | 104 | 0 | 0 | 104 |
| 93 | Al-Ḍuḥā | T2 | W/v | 212 | 0 | 0 | 212 |
| 104 | Al-Humazah | T1 | H/v | 0 | 0 | 3 | 240 |
| 46 | Al-Aḥqāf | T3 | W/v | 280 | 0 | 0 | 280 |
| 14 | Ibrāhīm | T3 | P/v | 0 | 5 | 0 | 300 |
| 62 | Al-Jumuʿah | T2 | H/v | 0 | 0 | 6 | 480 |
| 99 | Al-Zalzalah | T1 | H/v | 0 | 0 | 10 | 800 |
| 72 | Al-Jinn | T2 | W/v | 1,072 | 0 | 0 | 1,072 |
| 102 | Al-Takāthur | T1 | W/v | 1,110 | 0 | 0 | 1,110 |
| 81 | Al-Takwīr | T2 | H/v | 0 | 0 | 14 | 1,120 |
| 58 | Al-Mujādilah | T2 | W/v, H/v | 1,555 | 0 | 4 | 1,875 |
| 114 | Al-Nās | T1 | P/v, H/v | 0 | 30 | 2 | 1,960 |

Effort score = words needed + 60 × paragraphs needed + 80 × headings needed. These twelve chapters can all be brought to base with comparatively small additions, and several fail on a single structural metric (too few paragraph breaks, or too few mini-headings for the word count) rather than on missing substance — the cheapest work available.

## 7. How to extend against the base

1. **Pick a chapter** from §6.1 or §6.2 (missing content first, then three-metric failures).
2. **Extend by verse, not by chapter.** Add depth where a section is under the tier floor: new material that carries argument (vocabulary, cross-references, hadith with collections named, classical positions, reasoning, application), not padding.
3. **Keep the three ratios in view.** Roughly one mini-heading per 224 words and one paragraph per 62 words is the corpus norm; a chapter that hits the word floor with too few paragraphs or headings simply reads as walls of text and will fail the other two metrics.
4. **Re-measure after each chapter** — the loop is cheap:

```bash
python3 analysis/verse_metrics.py --dir expanded --out analysis   # recompute the three metrics
python3 analysis/check_base.py                                    # what passes, what still fails
python3 analysis/declare_base.py                                  # refresh this report
```

5. **Re-baseline deliberately.** The floors in §5.1 are calibrated to the corpus as it stands today. If the corpus is extended substantially, re-run `declare_base.py` — a new base will be derived from the improved distribution, and the bar rises with the work. Change `TIERS` in `declare_base.py` if you want different length bands.

## 8. Files produced by this analysis

| File | Contents |
| --- | --- |
| `analysis/expanded_base_standard.md` | This report. |
| `analysis/expanded_chapter_metrics.csv` | The 114-chapter comparison table — one row per chapter, the three requested metrics plus totals, spreads, and integrity columns. |
| `analysis/expanded_verse_metrics.csv` | The same measurements for all 6,236 verse sections — the raw data behind every chapter average. |
| `analysis/base_standard.json` | The declared base spec (tiers, floors, standards, extended levels) in machine-readable form. |
| `analysis/extension_worklist.csv` | Per chapter: compliance, failed metrics, and the words / paragraphs / headings needed to reach the floor. |
| `analysis/verse_level_shortfall.csv` | Verse sections below the per-verse floor. |
| `analysis/verse_metrics.py` | The measurement engine. |
| `analysis/declare_base.py` | Base derivation, compliance, and this report. |
| `analysis/repair_expanded.py` | The structural repair tool (dry-run by default). |
| `analysis/check_base.py` | One-shot compliance check. |

---

*Measured from the verse-section contents of `expanded/*.md` only; `initial/` and `translation/` were not used as inputs.*
