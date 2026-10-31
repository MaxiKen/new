# Depth Plan — expanded/002.md (Sūrah al-Baqarah) to the 007 standard

Executed under `STANDARDIZATION_PROMPT.md` with `{{N}}=2`, `{{NNN}}=002`.
Baseline measured at session start: 286 sections, 215,252 body words, mean 753 /
median 731 / min 342 / max 1,321; heads mean 3.3; gate `--band 1200-1400`:
283 below band, FAILING 284; cross-quotes 378 cited → 342 DRIFT, 29 VICINITY, 7 EXACT;
validate 114/114. `check_filler.py` extended for chapter 2 (§14): SHORT_VERSE_2 (5),
TIER1_2 (45 incl. 5 deepest); 007 re-verified unchanged (277,675w, FAILING 0,
reduced-floor 18; 1,780 EXACT).

## Tier-1 list as chosen (§8)

Deepest (ceiling 2,100): **2:62** (faiths outside the covenant — the most disputed
exclusivity verse), **2:255** (Āyat al-Kursī — the divine attributes), **2:256**
(no compulsion — the most disputed legal principle), **2:282** (the longest verse —
the debt-and-witnessing code), **2:286** (capacity, forgetting, the closing prayer).

TIER1 (floor 1,400, ceiling 1,800): 2:30 (vicegerency), 2:34 (the prostration command
and Iblīs's refusal), 2:37 (the words of repentance), 2:40 (the first covenant
formula), 2:47 (the favours formula), 2:80 (the Fire only numbered days), 2:102
(Hārūt and Mārūt), 2:106 (abrogation), 2:124 (Abraham tested; the imamate covenant),
2:143 (the middle community), 2:154 (the martyrs), 2:155 (the tests), 2:158 (Ṣafā and
Marwah), 2:178 (retaliation), 2:183 (fasting prescribed), 2:184 (the disputed
exemptions), 2:185 (Ramaḍān and the Night), 2:186 (I am near), 2:187 (the night of
the fast), 2:190 (the fighting limits), 2:191 (persecution worse than killing),
2:197 (ḥajj conduct), 2:216 (fighting made obligatory), 2:217 (the sacred months),
2:221 (marriage to polytheists), 2:228 (waiting period; the degree), 2:229 (divorce
twice; khulʿ), 2:230 (the threefold divorce), 2:233 (two years of suckling), 2:249
(Tālūt's river test), 2:257 (the Guardian of light), 2:258 (the king who argued),
2:259 (the sleeper of the ruined city), 2:260 (the four birds), 2:261 (the grain of
seven ears), 2:268 (Satan threatens poverty), 2:275 (trade and ribā), 2:279 (the war
clause), 2:284 (what is in the heavens), 2:285 (no distinction between messengers).

## Vocabulary authority (§3)

`translation/002.txt` wording throughout: *malaʾ* not present as "chiefs" — check each
verse; taqwā → "mindful"; khashyah → "stand in awe"; *khibr* → "certainty"/"sure faith";
āmāna → "feel secure"; ṣibghah → 2:138 "the natural Way"; the middle ummah → "an
upright community"; *adh-dhann* → "wishfully speculate"; "role model" (2:124 imām),
"proclaim the greatness" (2:185), "dumbstruck" (2:258), "blessed with knowledge and
stature" (2:247), "honour this trust" (2:283).

## Short verses (REDUCED_FLOOR 700), with reasons

2:1 muqattaʿāt; 2:12 one-clause rebuttal completing the hypocrites' dialogue of 2:11;
2:52 one-clause divine reply of forgiveness continuing the calf scene of 2:51; 2:192
one-clause divine reply closing the fight scene of 2:190–191; 2:227 continuation
clause of 2:226's four-month ruling. Not admitted: 2:42, 2:43, 2:152, 2:244, 2:278 —
complete commands, full band.

## Batch log (§13) — measured, never recalled

(to be appended per batch)

## Sections demoted / heads struck, with reasons

(none yet — run per verse before drafting, §9)

## Corrections list (§17.3)

(to be appended)

## Batch log (prologue + verses, ascending)

**Batch 1 — prologue + 2:1–2:8** (commit 23858c4). Sections 9 of 9 to band
(1,392/1,393/1,369/1,355/1,382/1,370/1,380/1,394 + prologue); +14 heads; blockquote
remediation for the range. Ḥadīth used: Jibrīl hadith cited as Ṣaḥīḥ Muslim 8 +
al-Bukhārī 50 (ʿUmar) — **verified** (Bukhārī 50 = Book of Belief, the asking of
Jibrīl; Muslim 8 is the canonical parallel); Bukhārī 33 three-signs of the
hypocrite (Abū Hurayrah) — **verified** (three signs: lying, breaking promises,
betraying trusts); the "fourth completes it" sentence is unnumbered in the file and
was left unnumbered (Bukhārī 34 carries the four-sign version).

**Batch 2 — 2:9–2:16** (commit 2b07465). All eight sections to band
(1,400/1,400/1,399/1,373/1,398/1,387/1,397/1,400); +20 heads. Defects fixed in
batch: 63:4 span pair demoted to italics; own-verse citations added at 2:14, 2:15,
2:16; "trades"→"trade" (2:86 agreement). Ḥadīth: Muslim 102 (grain-cheating, Abū
Hurayrah) — **verified** (Book of Faith, "he who deceives is not of me");
Bukhārī 52 + Muslim 1599 (the heart governs the body, an-Nuʿmān ibn Bashīr) —
**verified** (both collections, same report).

**Batch 3 — 2:17–2:24** (commit 1f020ab). Sections to 1,337–1,412; +18 heads incl.
the 2:22 chain fix. Post-pass: 17:97 wording aligned, own-verse citations added
(2:19, 2:20×2, 2:21), *O humanity!* italicised, two scaffolding leaks removed,
al-Walīd paragraph rewritten (fabricated fragment deleted), 21:98 and 3:133
rendered as wording. 2:17 left over ceiling in this commit; trimmed to 1,399 in
batch 5's pass.

**Batch 4 — 2:25–2:34** (commit 2fdbc4d). All ten sections past their floors
(Tier-1 2:30/2:34 at ≥1,400; 2:32 raised 1,138→1,211); +30 heads; body +5,332
words. Own-verse citations added at 2:25×2, 2:26×2, 2:28, 2:29×2, 2:30, 2:31,
2:33×2, 2:34; 66:6 span corrected to verbatim; pre-existing 18:50 span aligned.
Ḥadīth: Muslim 2824 (no eye has seen; Abū Hurayrah) — **verified**; Bukhārī 2067 +
Muslim **2557** (kinship ties, Anas) — **verified; file's "Muslim 2556" corrected
to 2557**; Muslim 486 — **verified with narrator correction: ʿĀʾishah (the night
prostration duʿāʾ), not Ibn ʿAbbās; the tahajjud frame was replaced with the
ʿĀʾishah scene and the duʿāʾ wording**.

**Batch 5 — 2:35–2:42** (this commit). All eight sections to band, including
Tier-1 2:37 (1,411) and 2:40 (1,408); 2:17 ceiling trim landed (1,399); +15 heads;
nine blocks. Verse work: 7:19 + 20:120 (tree), 2:36 residence clause + 20:123,
7:23 repentance prayer + Muslim 2759 (**verified**: "Allah spreads out His Hand…
until the sun rises from the west"), tawwāb name-count, 10:62 immunity formula,
3:131, 3:187 covenant-taken, 2:122/2:152 remembrance formula, 2:97 confirmation,
16:95 trade, 2:41 trade wording, 3:71 twin verse, 2:43 worship-pair with 19:31,
19:55, 20:14. Old-prose quotes aligned in the range: 2:2, 6:104, 7:157, 2:37
(inspired words), 2:37 names, 2:40 covenant clause, 2:152, 2:41 trade, 3:77, 2:146,
19:31, 19:55, 20:14, 7:180, 2:29, 2:33 secrets, 2:30 knowledge, 7:20, 7:21, 29:2.
Defect class closed in range: ASCII-wrapper-around-curly nesting removed at 2:25,
2:26 (29:2), 2:30, 2:35, 2:36; one stray "(2:25)" restored out of the 2:25
blockquote. Remaining cited DRIFTs in 2:25–2:42 (14) are pre-session old-prose
quotes — list verified this batch: 2:26 (22:73, 9:124–125), 2:27 (7:172, 4:1,
47:22), 2:28 (76:1×2, 36:78–79), 2:29 (11:61 — verbatim but ˹˺-bracketed), 2:31
(7:180 fixed; remainder), 2:34 (48:29×2), 2:35 (4:1 ellipsis form). Gate snapshot
at this commit: filler below 243 / above 0 / FAILING 244 (all outside 2:17–42),
tics 0.04/1k, chains 0.32/1k, dup 0.039, 0 repeated; cross-quotes EXACT 151,
DRIFT 318, VICINITY 28, FAILED 0; validate 114/114; check_translations 286
checked / 0 flagged; 007 unchanged (277,675w, FAILING 0).

**Next:** batch 6 ascending from 2:43 (≈243 sections below floor; next Tier-1s at
2:47, 2:80).

**Batch 6 — 2:43–2:50** (this commit). All eight sections to band (2:47 Tier-1 at
1,431); +17 heads; nine blocks (11:114 hours; 3:43 Mary's parallel; afalā
taʿqilūn count; ʿĀʾishah's "His character was the Qur'an" — **unnumbered by
design: the report is verified as hers but no collection-number was verified, so
none is printed**; 2:153 pair; Muslim 223 — **verified** ("prayer is a light…
patience is illumination," Abū Mālik al-Ashʿarī); 23:2 humility tag; 18:110
meeting-hope; 2:156 return-formula; 2:122 doubled address; 14:7
gratitude-increase; 2:143 witness-community; 2:123 twin formula; 3:30 account;
7:136 drowning; 10:92 preserved corpse; 26:63 strike). Old-prose alignments in
range: 2:43 gloss → "Establish prayer, pay alms-tax"; two chain-shapes in 2:44
reworded. Remaining cited DRIFTs in 2:43–2:50 (18) are pre-session old-prose
quotes (22:54, 2:4, 5:20, 43:32, 31:33, 2:255/20:109, 79:24, 21:35, 10:90–91,
42:45, 26:61–62, 4:1-ellipsis at 2:35's list, 3:91/5:36 vicinity) — documented.
Gate snapshot: filler below 235 / above 0 / FAILING 236 (none in 2:17–50);
cross-quotes EXACT 165, DRIFT 317, VICINITY 28, FAILED 0; validate 114/114;
007 unchanged.

**Batch 7 — 2:51–2:58** (this commit). All eight sections to band (1,204–1,265);
+17 heads; 19 blocks (20:80 Ṭûr appointment; forty as formation; 2:52 pardon
grammar + thanks purpose; 5:12 covenant terms; 7:148 lowing idol; 20:85 Sâmiri;
2:54 severity weighed; 4:153 demand lineage; 2:56 witnesses + taught
resurrection; 20:80 manna/quails; 2:57 cloud-shade; 7:161 gate-echo; 2:58
increase to the virtuous). New-quote defects: zero (all 18 cited DRIFTs in range
are pre-session old-prose: 20:88/20:90, 31:13, 2:55/2:2, 7:155, 6:103, 7:143,
41:13, 22:46, 7:155, 10:44, 31:12, 14:8 — documented). Chain-shapes reworded:
2:51 (Bukhārī 3667 clause — number is pre-existing old prose, unverified this
session), 2:58. Gate snapshot: filler below 228 / above 0 / FAILING 231 (none in
2:17–58); validate 114/114; manual checks examined: 8, no issues.

**Batch 8 — 2:59–2:66** (this commit). All eight sections to band; the deepest
2:62 raised 1,018→1,634 (ceiling 2,100) with three new heads (twin verse 2:112;
the 2:111 demand; al-Ghazālī's reach + 3:85 boundary). Other heads: 7:162
substitution told twice; taḥrīf doctrine; 7:160 twelve springs; 3:112 disgrace
exception; 2:61 craving-as-catechism; 4:154 mount retold; 7:163/7:166/5:60
Sabbath-triad; 2:66 example-method; sacred time. New-quote defects fixed before
commit: four ASCII+curly nestings de-nested (2:60/61/62/63), one drafting
artifact removed ("— no;" residue at 2:62), 2:63 my own quotes aligned to the
translation's wording ("Hold firmly…", "observe its teachings"), 2:61 chain
reworded, 2:64 own-span cited (2:63). Remaining cited DRIFTs in 2:59–2:66 (10)
are pre-session old-prose artifacts (incl. two unpaired-quote artifacts at 2:62
and Archer "haply/reverent" wording) — documented. Gate snapshot: filler below
220 / above 0 / FAILING 221 (none in 2:17–66); cross-quotes EXACT 181, DRIFT
318, VICINITY 28, FAILED 0; validate 114/114; manual checks examined: 8.

**Batch 9 — 2:67–2:74** (this commit). The cow episode + the hardened hearts:
all eight sections to band (1,212–1,345); +20 heads, 26 blocks (2 heads/section
plus addenda). Quote set: 2:67 mock-question; 2:68 age-specification; 2:69
bright-yellow; 2:70 sameness-confession + Allah-willing; 2:71 unworked cow +
"now you have come with the truth" + "hesitantly!"; 2:72 the murder + disclosure;
2:73 strike + purpose-clause; 2:74 hardness + yielding rocks + never unaware —
all verified EXACT (new-quote defects: none; every own-verse span cited (2:NN)).
Chain-shapes reworded: 2:68/2:72 (three "of the X of the" shapes). Gate
snapshot: filler below 212 / above 0 / FAILING 213 (none in 2:17–74);
cross-quotes EXACT 197, DRIFT 318, VICINITY 28, FAILED 0; validate 114/114;
manual checks examined: 8, none flagged. Remaining cited DRIFTs in 2:67–2:74
are pre-session old-prose quotes (not re-listed individually — the standing
in-prose remediation pass will align them chapter-wide).
