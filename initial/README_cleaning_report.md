# Cleaning report — 114 sūrah commentary files

**Input:** `uploads/001.md … 114.md` (≈1.06 million words, raw text extraction of a printed Quran commentary)  
**Output:** `cleaned/001.md … 114.md` — same names, same format (Markdown), one file per sūrah.

## What was wrong with the source files

| Problem | Scale | Fix |
|---|---|---|
| Windows line endings (`\r\n`) on every line | 95,558 lines | normalised to `\n` |
| Text hard-wrapped at the printed page's line width (every line of the book became a line of text), so paragraphs were lost | ~95,000 line breaks | lines re-flowed into paragraphs; real paragraph boundaries recovered with a typeset-width model (see below) |
| Words hyphenated across a line break (`pre-` / `Islamic`) | 309 | joined; the hyphen kept only where it belongs in the word (`pre-Islamic`, `al-Rāzī`) |
| Verse numbers printed as ornamental numerals came through as garbage characters (`*`, `+`, `J`, `Z`, `Ċ`, `Ě`, `Ȋ`, `!`, `"`, `Ð`, `@`, `ɵ` …) | 6,236 verses | decoded (the extraction had read each number as a hex code point) and replaced with the real verse number; all 6,236 verified against the canonical verse count of every sūrah |
| Commentary headers (verse numbers on their own line) indistinguishable from text | 5,049 headers | rendered as bold run-in headers **1**, **3–4**, … |
| Clusters where the extraction emitted one word per line (`their` / `mothers,` / `including` / `grandmothers;`) | 14 clusters | re-joined |
| Verses attached to the wrong commentary section (extractor split the page in the wrong place) | 24 verses in 9 files | re-attached to the section whose header covers them |
| Verse text that ended up *inside* a commentary paragraph | 2 (6:131, 7:104) | restored to the verse text |
| Commentary header lost entirely (38:5) or itself turned into an ornament glyph (85:12) | 2 | restored |
| Missing basmalah line (105) | 1 | restored |
| Stray/garbage symbols (`√111:5c`), doubled punctuation (`..`), a `0` for `o` (`s0`) | 3 | fixed |
| Genuine typos (`peoplle`, `pilgram`, `permissable`, `fortelling`, `whosever`, `prayeru`, `existiation`, `there be will`) | 9 | fixed |
| Inconsistent transliteration/abbreviations (`aḥādith`, `al-ṭabrisī`, `Ḥūd`, `al-kisāʾi`, `(AJ,`) | 8 | harmonised with the form used everywhere else in the text |

## Output structure (identical for all 114 files)

```
# 106. Quraysh                     ← sūrah number + name (as spelled in its own introduction)

## Introduction                    ← the introductory essay, in paragraphs

## Text and Commentary

*In the Name of God, …*            ← basmalah (absent in 9 as in the original; is verse 1 in sūrah 1)

> **1** For the secure passage …   ← verse text, as block quotes with real verse numbers
>
> **2** their secure passage …

**1–2** Reading this verse as …    ← commentary, header in bold, paragraphs preserved

***                                ← the book's own section divider
```

## How paragraph breaks were recovered

The extraction destroyed the distinction between a *line* break and a *paragraph* break. Fortunately the source is a justified typeset text: a line that ends a paragraph is short, while a line inside a paragraph is filled to the measure. I fitted a per-character width model to the 55,000 unambiguous lines, then for each line ending in a full stop asked whether the first word of the next line *would have fitted* on it. If it would have, a paragraph break must have occurred; if not, the text simply wrapped. ~93% of the 5,000+ candidate breaks were clear-cut; the remaining ~170 borderline cases were decided by additionally looking at the shape of the following line (a paragraph's first line is indented, so it is measurably shorter). Rules on top: a paragraph never begins with a lower-case word or a closing punctuation mark, never after an abbreviation such as *v.* / *vv.* / *cf.*, and dialogue exchanges (“Yes.” / “No.”) are one utterance per paragraph, as in the book.

## What I did *not* change

* No rewriting, re-punctuating or modernising — wording, spelling conventions (e.g. *Makkah*, *sūrah*), transliteration and the author's commentator abbreviations *(IK, Q, R, Ṭ …)* are untouched.
* Spaced ellipses `. . .` (the book's house style) are kept.
* Two passages are cut off in the source itself and cannot be reconstructed: the last sentence of the introduction to **sūrah 1** (“…so too does it mark the beginning of creation”, no full stop) and the introduction to **sūrah 105**, which stops mid-sentence (“…so let those who are”). Both are left exactly as they were.
* The last sentence of **sūrah 7** carries an added clause (“although this is not required by Islamic Law”) that is not part of the original typesetting; it was kept, I only capitalised *Islamic Law* to match the rest of the text and added the missing full stop.

## Totals

* Files: 114  
* Verses decoded and validated: 6,236  
* Commentary sections: 5,049  
* Paragraphs reconstructed: 6,875  
* Verses re-attached to the correct section: 24  

## Per-file notes

Files not listed needed only the standard treatment (line endings, glyph decoding, reflow, hyphenation).

**001.md** — introduction ends without a full stop in source ("…the beginning of creation"); left as is  
**002.md** — typo: (prayeru) → (prayer); typo: al-ṭabrisī → al-Ṭabrisī  
**003.md** — typo: fortelling → foretelling  
**004.md** — typo: (Q, R).. → (Q, R).  
**005.md** — typo: whosever → whosoever  
**006.md** — verse 131 was embedded inside the commentary of 130; restored to the verse text  
**007.md** — verse 104 was embedded inside the commentary of 103; restored to the verse text; final sentence lacked a full stop; added; last sentence contains a hand-added clause ("although this is not required by Islamic Law") not in the printed book; kept, capitalisation fixed; typo: pilgram → pilgrim; typo: "the islamic law" → "Islamic Law"  
**012.md** — typo: (AJ, → (Aj,  [commentator abbreviation]  
**015.md** — typo: al-ṭabrisī → al-Ṭabrisī  
**016.md** — typo: permissable → permissible  
**020.md** — typo: (AJ, → (Aj,  [commentator abbreviation] (×2)  
**026.md** — verse 112 re-attached to the commentary section that discusses it (rule a); verse 113 re-attached to the commentary section that discusses it (rule a); verse 114 re-attached to the commentary section that discusses it (rule a); verse 115 re-attached to the commentary section that discusses it (rule a); verse 116 re-attached to the commentary section that discusses it (rule a); verse 117 re-attached to the commentary section that discusses it (rule a); verse 118 re-attached to the commentary section that discusses it (rule a); verse 119 re-attached to the commentary section that discusses it (rule a); verse 121 re-attached to the commentary section that discusses it (rule a); verse 123 re-attached to the commentary section that discusses it (rule a); verse 145 re-attached to the commentary section that discusses it (rule b)  
**029.md** — typo: Ḥūd → Hūd  
**036.md** — typo: s0 → so  
**037.md** — typo: (AJ, → (Aj,  [commentator abbreviation]  
**038.md** — block 4: commentary header missing in source; inserted header for its verse(s)  
**055.md** — verse 17 re-attached to the commentary section that discusses it (rule a)  
**067.md** — typo: al-kisāʾi → al-Kisāʾī  
**068.md** — typo: existiation → existentiation  
**072.md** — typo: peoplle → people; typo: aḥādith → aḥādīth  
**085.md** — commentary header 12 was rendered as an ornament glyph in source; restored; verse 5 re-attached to the commentary section that discusses it (rule b); verse 12 re-attached to the commentary section that discusses it (rule a)  
**087.md** — verse 11 re-attached to the commentary section that discusses it (rule b)  
**088.md** — verse 11 re-attached to the commentary section that discusses it (rule a); verse 12 re-attached to the commentary section that discusses it (rule a); verse 13 re-attached to the commentary section that discusses it (rule a); verse 14 re-attached to the commentary section that discusses it (rule a); verse 19 re-attached to the commentary section that discusses it (rule a); verse 20 re-attached to the commentary section that discusses it (rule b); typo: "there be will no" → "there will be no"  
**092.md** — verse 16 re-attached to the commentary section that discusses it (rule b); verse 17 re-attached to the commentary section that discusses it (rule b)  
**093.md** — typo: whosever → whosoever  
**098.md** — verse 7 re-attached to the commentary section that discusses it (rule b)  
**105.md** — basmalah line was missing in source (introduction is cut off mid-sentence); basmalah restored; introduction is truncated in source ("…so let those who are"); text lost before extraction, left as is  
**111.md** — typo: √111:5c → 111:5c  [stray symbol]  
