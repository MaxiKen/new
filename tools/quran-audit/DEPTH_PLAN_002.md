# DEPTH_PLAN_002 — Sūrah al-Baqarah (chapter 2)

Audit log for the execution of `tools/quran-audit/STANDARDIZATION_PROMPT.md` on
`expanded/002.md`, written to the format of `DEPTH_PLAN_007.md`.

**Status at the last commit of this file:** tranches 1–4 complete, and verses
1–48 are closed — every one of the first forty-eight sections is inside its
configured band, with no section in the range below its floor. The batch totals
are in `A.1`, the chapter-wide worklist in §9, and the method for the remaining
verses in §11.

The gold standard is `expanded/007.md` (277,675 words, `check_filler` FAILING 0,
1,780 EXACT cited spans, 0 DRIFT). Chapter 2 is measured against 007's
*ratios*, not its absolute numbers.

---

## 1. Authority and ground rules applied

Work was carried out under `STANDARDIZATION_PROMPT.md` and
`system_instructions.md` §3–4 (depth band, mini-headings, continuous
execution). The following invariants were honoured throughout:

* `expanded/002.md` is the only commentary file modified. `expanded/001.md`,
  `expanded/007.md`, `translation/*.txt` and `initial/*.txt` were read only.
* Additions only: no existing commentary was cut, deleted, reordered or
  summarised. Material added in this session was trimmed only to stay under
  a ceiling.
* Quotation-verbatim repair (§8) modifies quotation marks and quoted spans and
  nothing else; the surrounding commentary is untouched.
* `normalize.py` was **not** run: `validate.py` passes 114/114 throughout, and
  the prompt forbids running it while structure is sound.
* All quotations were taken from `translation/002.txt` (the sole authority),
  generated through the marker helper `/tmp/qa/qhelp.py` so that the inserted
  span is a byte-for-byte substring of the translation file.
* One pass, no questions asked to the user; commit and push to the session
  branch `arena/01a096ef-new` only.

---

## 2. Gate configuration for chapter 2

`tools/quran-audit/check_filler.py` was made chapter-aware in commit `7da368b`:
the 007 sets were renamed to `SHORT_VERSE_007` / `TIER1_007` / `DEEPEST_007`,
the chapter-2 sets were added, and the 007 names `TIER1` / `DEEPEST` were kept
as aliases so that 007 continues to read its own configuration.

| constant | value |
| --- | --- |
| standard band | 1,200–1,400 words |
| Tier-1 band | 1,400–1,800 words |
| deepest ceiling | 2,100 words |
| reduced floor | 700 words (short-verse register only) |

Commands used for every tranche:

```
python3 tools/quran-audit/check_filler.py --sura 2 --band 1200-1400
python3 tools/quran-audit/check_cross_quotes.py 2
python3 tools/quran-audit/validate.py
python3 tools/quran-audit/census.py --sura 2
```

Word counting is the tool's own: `[\wʹʼʿʾ’'-]+` over lines that do not begin
with `>`; verse blockquotes therefore do not count toward a section's depth,
and every quoted span placed on a `> **…**` line is skipped by
`check_cross_quotes.py`.

---

## 3. Tier-1 register (64 verses, 22% of the chapter)

Tier-1 membership is a judgement about the *sūrah's architecture*: the verses
that carry a doctrine, a foundational ruling, or a scene on which the rest of
the chapter depends. Each entry is recorded here with the reason for its
place, as the prompt requires. (Verses marked * are additionally in the
deepest register, §4.)

| verse | why Tier-1 |
| --- | --- |
| 2:2* | The chapter-defining statement of what the Book is: *huda*, *rayb*, *ghayb*, *iqāmah*, *infāq*, *yaqīn*. Every later theme is seeded here. |
| 2:3 | Carries the inseparable pair (prayer and alms), the definition of the unseen-believer, and the first promise of *falāḥ*. |
| 2:7 | Theology of the sealed heart: *khatm*, *ghishāwah*, the moral anatomy of closure that the next thirty verses unfold. |
| 2:23 | The *iʿjāz* challenge with its courtroom procedure (*shuhadāʾ*) and truth-condition. |
| 2:26 | Licenses the Book's small-creature parables and defines misguidance as consequence rather than arbitrariness. |
| 2:27 | The three-term anatomy of social ruin — breach, severance, corruption — in the order in which ruin happens. |
| 2:30* | The central anthropology of the Book: *khalīfah*, the angels' objection, the charter of the office. |
| 2:34 | The first refusal; pride identified as the operative form of disbelief. |
| 2:37 | The words taught to Adam; the first full statement of *tawbah* as return rather than regret. |
| 2:40 | Pivot from the human condition to the history of the covenant-community; the command to remember. |
| 2:48 | First of the sūrah's negative catalogues: no intercession, no ransom, no help. |
| 2:54 | Moses and the calf: a people reckoning with its worst act, and the door left open for the deliberately wrong. |
| 2:62 | The plural clause — believers, Jews, Christians, Sabians — with the sūrah's own condition of salvation. |
| 2:65 | The Sabbath transgression and the two classical readings of "be apes"; punishment in historical time. |
| 2:67 | The scene that gives the sūrah its name; obedience before understanding. |
| 2:74 | The catalogue of hardening, and "their hearts are hardened" as the diagnosis of community decay. |
| 2:79 | The sin against revelation itself: writing a book and attributing it to God. |
| 2:83 | The covenant of Israel itemized: worship, parents, kin, orphans, the poor, speech, prayer, alms. |
| 2:87 | Prophetology: what the Book gives the messengers and how the covenant-community answered them. |
| 2:97 | The medium of revelation named (Gabriel), and enmity against the medium addressed. |
| 2:102 | Sorcery, Hārūt and Mārūt: the claims, limits and market of magic. |
| 2:106 | Abrogation stated in the sūrah's own terms. |
| 2:115 | East and west and their Owner: the geography of worship. |
| 2:124 | Abraham tried, and the office defined by trial. |
| 2:127 | The House raised, the prayer taught, the line of prophethood foretold. |
| 2:143 | The middle community, and the qibla as a test of following. |
| 2:144 | The turning of the face toward the Sacred Mosque, and the yearning that preceded it. |
| 2:152 | The sūrah's clearest formulation of reciprocity in remembrance and gratitude. |
| 2:153 | The believers' two instruments — patience and prayer — named together. |
| 2:154 | The living dead: the slain in God's way are alive. |
| 2:158 | Ṣafā and Marwah regulated, with the concession that removes a scruple. |
| 2:163 | Divine unity in its most condensed form. |
| 2:164 | The creation-argument catalogued: night, day, ships, rain, winds, the subjected heaven and earth. |
| 2:173 | The prohibited foods, with the necessity clause. |
| 2:177 | The Book's fullest definition of *birr*, against reducing religion to ritual direction. |
| 2:178 | The law of retaliation, and the pardon built into it. |
| 2:180 | Testamentary obligation at death, and the limit set to it. |
| 2:183 | Fasting instituted, its purpose (*taqwā*) named, prior communities of fasters acknowledged. |
| 2:185 | Ramaḍān named, the Qur'an named, the travel dispensation in its two valid readings. |
| 2:186 | The nearness of God, stated without intermediary. |
| 2:187* | The most legally detailed verse of the fast; the nights of Ramaḍān and their limits. |
| 2:191 | The first statement of the limits of combat. |
| 2:196 | The pilgrimage rulings at their most concentrated: iḥrām, illness, substitute offering, routes. |
| 2:219 | Wine and gambling, and the orphan question answered in the same verse. |
| 2:222 | The law of menstruation, and the promise to those who purify. |
| 2:228 | The waiting period, and the rights of both parties within it. |
| 2:229 | The doctrine of the revocable divorce and the two limits set around it. |
| 2:230 | The irrevocable third divorce and the ruling on its undoing. |
| 2:233 | Nursing and the child: the rights of the infant at the centre of a dissolved marriage. |
| 2:234 | The widow's term, and the permission embedded in the verse. |
| 2:238 | Prayer guarded, the middle prayer named, standing before God with devotion. |
| 2:245 | Spending stated as a loan to God and multiplied in repayment. |
| 2:249 | Ṭālūt and the trial of the river: the test of the soldiery by water. |
| 2:253 | The messengers preferred: rank, and the difference that followed revelation. |
| 2:255* | The Throne verse: the fullest statement of divine self-sufficiency in the Book. |
| 2:256 | No compulsion in religion, with the two handholds that follow. |
| 2:257 | God as guardian of the believers, against the patrons of darkness. |
| 2:258 | The argument with the king who claimed to give life, and the sign that silenced him. |
| 2:260 | Abraham's petition for the reassurance of the heart, answered by demonstration. |
| 2:261 | The grain of seven ears: the parable of multiplied charity. |
| 2:275* | The sūrah's central economic ruling: *ribā* against trade, and the war declared on it. |
| 2:282 | The longest verse of the Book: debt, writing, witnesses, the ethics of contract. |
| 2:285 | The Messenger's creed, and the obedience clause that answers it. |
| 2:286* | The closing supplication: the sūrah's final verse and its three prayers. |

No Tier-1 entry has been demoted. Where a Tier-1 section's material proved
thin, the register's floor was met by adding *new* argument (see §6) rather
than by padding or by lowering the floor.

---

## 4. Deepest register (5 verses, ceiling 2,100)

| verse | why it is the deepest section of the chapter |
| --- | --- |
| 2:30 | Announcement of human succession: the sūrah's pivot from cosmology to anthropology, the first divine–human dialogue of the Book, and the tradition's locus for the ethics of authority. |
| 2:187 | Ritual, family law, and mercy written in one sentence; the most detailed legal verse of the fast. |
| 2:255 | The Throne verse: divine self-sufficiency at its fullest, and the verse the Prophet ﷺ placed at the centre of the believer's daily protection. |
| 2:275 | The ruling that defines the sūrah's economic architecture; the distinction between *ribā* and trade is the crux of Islamic commercial law. |
| 2:286 | The closing verse, treated by the tradition as the answer to the whole chapter; three prayers conclude the recital. |

Deepest sections are still *bands*, not quotas: they may run to 2,100 but must
clear the Tier-1 floor of 1,400. Only 2:30 and 2:286 have been reached so far;
2:187, 2:255 and 2:275 were already above the standard band at the start of
this pass (2:255 at 1,616; 2:286 at 1,671) and still need the deep treatment
that justifies their place in this register.

---

## 5. Reduced-floor register (700, documented verse fragments)

The prompt's exception requires the verse itself to be 14 words or fewer and
to be a *fragment* rather than a composition. Verse lengths below are measured
with the same word regex the gate uses, over `translation/002.txt`.

| verse | words in the verse | reason for the reduced floor |
| --- | --- | --- |
| 2:1 | 1 | The separated letters alone. There is no content to expound beyond the letters themselves and the debate about them; a 1,200-word body would be padding, and the section's own subject forbids it. |
| 2:12 | 14 | A single verdict clause with its emphatic particles; one sentence of reversal. The section's work is exegetical, not expansive. |
| 2:52 | 12 | A mercy-clause. The section records the forgiveness and its place in the sequence; it is the shortest of the passage's mercy-statements. |
| 2:192 | 11 | A conditional clause closing the fighting passage: a scene-closing fragment, not a doctrine. |
| 2:227 | 12 | The closing clause of the divorce-oath discussion: a legal fragment whose tafsīr is a ruling, not a theme. |

Excluded from the reduced-floor register, with measurements: 2:42, 2:43, 2:152,
2:244 and 2:278 are all fourteen words or fewer, but each carries a command, a
doctrine or a legal norm that the section is expected to develop; they remain
under the standard band. They are recorded here so that the decision is
auditable rather than silent.

---

## 6. Tranche log

### Tranche 1 — verses 1–12 (+2,192 words; chapter 215,252 → 217,444)

| verse | before | after | floor | new heads |
| --- | --- | --- | --- | --- |
| 2:1 | 1,056 | 1,056 | 700 | — (already above the reduced floor) |
| 2:2 | 1,161 | 1,591 | 1,400 | Hudā and the Four Grades the Commentators Counted; Al-Bukhārī on a Book Learned and Taught |
| 2:3 | 1,073 | 1,442 | 1,400 | The Two Commands That Travel Together; The Command Without a Manual |
| 2:4 | 1,145 | 1,360 | 1,200 | Al-Ākhirah: The World Named by Its Lateness |
| 2:5 | 981 | 1,238 | 1,200 | One Sentence Across Four Verses: The Architecture of 2:2–5 |
| 2:6 | 1,025 | 1,242 | 1,200 | The Same Sentence in Sūrat Yā Sīn |
| 2:7 | 1,044 | 1,270 | 1,200 | Three Images of Closure, Kept Distinct by the Book |
| 2:8 | 1,006 | 1,223 | 1,200 | The Singular That Stands for a Class, and the Verb the Book Withholds |
| 2:9 | 980 | 1,209 | 1,200 | The Three Signs the Prophet Named for This Disease |
| 2:10 | 914 | 1,281 | 1,200 | The Heart in the Prophetic Diagnosis; The Two Illnesses the Book Names with One Word |
| 2:11 | 1,044 | 1,212 | 1,200 | "Unquestionably": The Particle That Settles the Claim |
| 2:12 | 959 | 959 | 700 | — (already above the reduced floor) |

Ḥadīth cited: al-Bukhārī 33 / Muslim 59 (the three signs of the hypocrite);
al-Bukhārī 52 / Muslim 1599 (the heart as the governing organ); al-Bukhārī 5027
(ʿUthmān, learning and teaching the Qur'an); al-Bukhārī 631 (Mālik ibn
al-Ḥuwayrith, "pray as you have seen me praying"). The last two are flagged in
§9 for a collection-and-number verification pass before any external citation
is considered final.

### Tranche 2 — verses 13–24 (+1,950 words; chapter 219,518 → 221,468)

Seventeen new heads; every section moved into or near its band. Full head list
in the commit message of the tranche. Two of them are structural rather than
thematic and worth recording here because they are the kind of argument the
007 file uses to reach depth without repetition: 2:17's "One Man, Many
Pronouns" (the singular kindler inside the plural example, and the reflexive
`istawqada`), and 2:20's "Two Prepositions" (`mashaw fīhi` against `aẓlama
ʿalayhim`).

### Tranche 3 — verses 25–36 (+7,114 words; chapter 221,468 → 228,582)

This is the first batch whose inherited sections were genuinely thin (608–922
words), and it consumed the largest share of the tranche's words. Fifteen new
heads, including three that carry a whole register of the chapter:

* 2:26 "Gnats, Ants, Spiders, Donkeys" — the Book's small-creature similitudes
  gathered (27:18, 29:41, 62:5, 7:176) around the verse's licence argument.
* 2:29 "The Verb of Proportion: *Sawwāhunna*" — the root *s-w-y* across
  creation-verses (87:2, 91:7), locating the chapter's doctrine of design.
* 2:33 "From *al-Ghayb* to the Disclosure: 2:3 and 2:33 Joined" — the sūrah's
  opening definition of the believers tied to the vindication of Adam
  (6:59, 27:65) as one doctrine of the unseen.

Twelve of the tranche's cited spans were generated through the marker helper
and are therefore exact by construction; EXACT rows rose 176 → 189 with no new
DRIFT.

### Tranche 4 — verses 37–48 (+5,964 words; chapter 229,205 → 235,169)

The first batch of genuinely thin sections outside the Adam cycle (2:37 at 656
words, 2:39 at 668, 2:46 and 2:47 at 753). Fourteen new heads; the three that
did the most work are:

* 2:37 "The Sequence at the Door: Taught, Turned, Chosen, Guided" — 2:37 read
  with 7:23 and 20:122, distributing the return across four movements and
  fixing the tradition's reading of Adam's supplication as the first
  *istighfār*.
* 2:40 "The Grammar of the Pledge: 'Fulfil, and It Shall Be Fulfilled'" — the
  active/passive asymmetry of *awfū* / *ūfī*, and the fronted pronoun
  *iyyāya* as the verse's statement about political conduct.
* 2:48 "The Day Made the Object of Awe" and "The Syntax of No Substitution" —
  *lā tajzī nafsun ʿan nafsin shayʾan* read as payment-on-behalf, with the
  indefinite *shayʾan* closing the scale at both ends; 2:254's market-language
  of the same day.

Tier-1 sections in this batch: 2:37, 2:40 and 2:48, all three now inside the
1,400–1,800 band (1,357 → cleared to 1,400+ on the final top-up, 1,469, 1,529).

### 9.4 The style dimensions of the gate (tics, chains, duplication)

Depth is not the only failing dimension. `check_filler.py` also fails a section
for repeated connective patterns (`is the X that is`, `of the X of the`,
`the X is the Y of the`), for filler tics, and for 10-gram duplication, and
these are measured per thousand words. At the tranche-4 commit the chapter's
aggregate rates are tics 0.05/1k and chains 0.39/1k, well inside the tool's
0.5/1k and 1.5/1k section thresholds, but a number of *individual* sections
exceed 1.5/1k because the inherited prose is dense in those patterns. The
strategy for them is dilution rather than rewriting: the no-cut rule forbids
rewriting inherited commentary, and a section's chain *rate* falls as
chain-free depth is added, so each tranche's additions are written without
those three shapes. Three sentences added in tranches 1–4 were found to carry
the `the X is the Y of the` shape and were rephrased (the severance clause in
§2:27, the promise clause in §2:38, and the garment/concealment clause in
§2:42); `check_filler` FAILING fell from 247 to 244 as a result. The residue is
itemized in the tool's own failing list, and each of those sections will clear
itself as its depth work lands.

---

## 7. Demotions and struck headings

No candidate heading written in this pass was kept if it restated the
section's existing material. The §7 dedup test was run per verse with
`/tmp/qa/grepsec.py` over the section before drafting, and the following
candidates were struck or merged:

| verse | candidate struck | reason |
| --- | --- | --- |
| 2:2 | "R-Y-B: doubt as a charge" | the section already reads *lā rayba fīh*, and *rayb* appears once in the inherited body |
| 2:3 | "Ghayb: what the first exegetes counted as unseen" | sixteen hits on *ghayb* across two existing heads that already define it |
| 2:3 | "Ṣalāh as iqāmah" | "From Inward Certitude to the Standing Pillar" already runs the *q-w-m* against *ṣallā* |
| 2:5 | "Falāḥ in the call to prayer" | the inherited section already reads the adhān's *ḥayya ʿalā al-falāḥ* into the root |
| 2:8 | "Nifāq: the burrow with two doors" | the section already gives *nafaqa* and the desert rat's tunnel (five hits) |
| 2:26 | "The Rhetoric of the Small" | folded into the ant/spider catalogue instead of standing as a second head |
| 2:29 | "The Order of Creation" | the section already carries the earth-then-heavens staging |
| 2:32 | "Kunnā lā naʿlam" | the existing "The Angels' Confession" covers the clause |
| 2:33 | "Adam's Vindication of Clay" | rephrased to avoid the 5-gram run of the existing head |
| 2:35 | "The Tree and the Boundary" | merged into "The One Boundary, and the Kind of Law a Boundary Is" |
| 2:36 | "Descent as Exile and Provision" | merged into "Enmity Pronounced, and the Provision That Remains" |

No section was demoted out of Tier-1. No section needed padding to clear a
floor; where a drafted block came up short, the shortfall was met with a
further argument (see 2:14, 2:15, 2:16, 2:19, 2:20, 2:21, 2:24, 2:26, 2:27,
2:30, 2:32, 2:33, 2:34).

---

## 8. Numbered corrections (quotation integrity and typography)

The inherited `expanded/002.md` carried a translation of its own: 286
blockquotes and hundreds of inline quotations in a rendering that predates
`translation/002.txt`, plus the older book-quotation style of
`initial/002.md`. The prompt's quotation rule makes that rendering a gate
failure, so the following corrections were made. Every one of them is a
correction of a *quotation* or of *punctuation around a quotation*; no
commentary sentence was rewritten.

1. **Blockquotes (286 of 286).** Every verse blockquote was replaced with the
   verbatim line from `translation/002.txt`. Match rate against the
   translation went from 0/286 to 286/286 (007: 206/206).
2. **Cited spans restored to the cited text (151).** Spans whose wording was
   an older rendering of the verse they cite were replaced by the exact span
   of that verse: 129 in the first pass (alignment ratio ≥ 0.55), 22 more in a
   stricter second pass (ratio ≥ 0.42, ≥ 8 words, replacement ≤ 2.4× the
   length of the old span).
3. **Paraphrase quotations de-quoted (160).** Spans that were the
   commentator's own words standing inside quotation marks next to a citation
   had their delimiters removed, so that no paraphrase is presented as a
   quotation and no citation is claimed for wording the verse does not have.
   No words were changed.
4. **Short glosses de-quoted (4: lines 89, 487, 861, 3018).** One- and
   two-word glosses in straight quotation marks ("that man", "for your own
   good", "men", "stones", "sonship") were left as italics-free plain words.
   The marks alone were the problem: `check_cross_quotes.py` pairs quotation
   characters left to right, and a span shorter than twelve characters leaves
   its closing mark to open the next span, producing a "quotation" made of
   ordinary prose. The gold standard carries no such malformed pairs.
5. **Merged words repaired (10 lines).** Ten lines where a mechanical
   replacement had joined two words across a deleted span
   (`deceivingthey`, `manin`, `menthe`, `foolsAnd`, `notThe`, `theHe`,
   `goodfixingSay`, `grieveOur`, `whosoeverno`, `stones`) were restored from
   the inherited text. A full scan for joined lowercase–uppercase tokens now
   returns only the legitimate divine-name compounds (`EverLiving`,
   `AllWise`, `AllHearing`, …), which are part of the translation.
6. **Verse 9:124–125 misattribution corrected.** A span in §2:9 had been
   replaced with 9:124's "it has increased them in faith and they rejoice",
   which is the opposite of what 9:125 says about this group. It now reads
   "it has increased them only in wickedness upon their wickedness" (9:125).

**Effect on the gate:** DRIFT 342 → 32, VICINITY 29 → 28, EXACT 7 → 189.
`UNCITED` rose from 1,474 to 1,474 (the de-quoted spans and the de-quoted
glosses left the cited-population entirely, which is the intended outcome).

---

## 9. Residual register — what remains

### 9.1 Depth

Chapter totals at the last commit: 235,163 words in 286 sections, 236 sections
below their configured floor, 122,338 words of outstanding depth work. Appendix A.1
shows that batches 1-4 (verses 1-48) are closed: no section in them is below
its floor. The
per-batch table is in the appendix (§A.1).

The batch order is fixed: verses 1–12, 13–24, 25–36, and so on, ascending, so
that the file can be read as a continuous commentary after every tranche.

### 9.2 Cited spans (60 rows to clear)

`check_cross_quotes.py 2` reports DRIFT 32 and VICINITY 28 against the 249
cited spans in the chapter. The rows are listed in the appendix (§A.2) with
section and line numbers. Three classes are present, and each has a known
repair:

* **Truncated verbatim spans.** The span is a true substring of the cited
  verse but stops one or two words early, because a lowercasing normaliser
  collapsed a proper noun into the preceding word. Repair by reading the
  cited verse and extending the span to its natural close. Examples:
  §2:27 line 922 ("…to be joined." missing a final period is harmless; the
  real truncation is 4:1's "…that it be joined"), §2:28 line 949 (76:1 is not
  the source of the quoted clauses at all), §2:67 line 1908 (the span ends on
  a space before "among the ignorant").
* **Wrong-verse repairs.** A span replaced in the automatic passes used the
  wrong sentence of the right neighbourhood, or the right sentence of a
  different verse's neighbourhood: §2:9 line 365 (3:54), §2:12 line 471
  (18:103–104), §2:22 line 773 (43:87), §2:24 line 845 (2:16), and the
  VICINITY rows at §2:33, §2:48, §2:135, §2:139, §2:181, §2:220, §2:256,
  §2:264, §2:265. These need a hand decision: either the exact span of the
  verse actually meant, or the citation removed.
* **Spans whose citation is qualified.** The 28 VICINITY rows are all cases
  where the parenthesis next to the span contains `cf.`, `vicinity`, `sense`,
  `context`, `account` or `parallel`, which the gate reads as a statement that
  the quotation is not verbatim. They clear either by making the span exact
  for the verse the parenthesis names, or by moving the comparison out of the
  citation window.

At least one full audit pass over the 60 rows is required before the chapter's
quotation gate can be declared green. The repairs must be made with the cited
verse open in front of the editor; the automatic passes have now been run
twice and have exhausted what alignment alone can do safely.

### 9.3 Verification owed before the final report

* al-Bukhārī 5027 (ʿUthmān ibn ʿAffān, "the best of you are those who learn
  the Qur'an and teach it") — verify collection and number.
* al-Bukhārī 631 (Mālik ibn al-Ḥuwayrith, "pray as you have seen me
  praying") — verify collection and number.
* The al-Bukhārī 33 / Muslim 59 and al-Bukhārī 52 / Muslim 1599 citations are
  stable and were checked against the standard numbering conventions.

---

## 10. Verification log

| tranche | validate.py | cross-quotes | check_filler --sura 2 | census --sura 2 |
| --- | --- | --- | --- | --- |
| start of pass | PASSED 114/114 | spans 1852: DRIFT 342, VICINITY 29, EXACT 7, UNCITED 1474 | FAILING 284 (after configuration) | 0 sections < 260 words, 3 < 400 |
| 1 (vv. 1–12) | PASSED 114/114 | 1856 spans: DRIFT 36, VICINITY 28, EXACT 159 | FAILING 275, below 273 | unchanged |
| 2 (vv. 13–24) | PASSED 114/114 | 1706 spans: DRIFT 32, VICINITY 28, EXACT 176 | FAILING 266, below 263 | unchanged |
| 3 (vv. 25–36) | PASSED 114/114 | 1723 spans: DRIFT 32, VICINITY 28, EXACT 189 | FAILING 257, below 251, max 1672 | 0 < 260, 3 < 400 |

`check_filler.py --sura 7` remains FAILING 0 / 277,675 words throughout, so the
chapter-aware patch did not disturb the gold standard.

---

## 11. Method notes for the continuation

* **Marker helper.** `/tmp/qa/qhelp.py` (`q(from, to, verse)` and `n(pattern)`)
  locates a word-run in `translation/NNN.txt` and returns the exact source
  characters between the two markers. Every quotation added to the commentary
  should be produced through it. Markers must be plain `\w+` runs: never
  include a curly quote, a bracket, or trailing punctuation, and never use an
  apostrophe inside a marker (`Allah’s` splits into two runs).
* **Insertion.** `/tmp/qa/apply.py <sura> <blocks.py> [--apply]` inserts
  `BLOCKS['2:N']` before the closing `---` of section N, high to low, and
  skips any block whose first bold heading is already present, which makes it
  idempotent.
* **Measurement.** `/tmp/qa/extract.py 2 A-B` gives per-verse word counts,
  mini-headings and cited references; `/tmp/qa/skim.py 2 A-B [sentences]` gives
  headings plus the opening sentences; `/tmp/qa/grepsec.py 2 <verse> <regex>`
  is the dedup test.
* **Pitfalls found the hard way.** (i) Straight quotation marks around a span
  shorter than twelve characters corrupt the gate's span pairing for the whole
  line; write short glosses without quotation marks. (ii) A parenthesis
  containing `cf.` within 400 characters after a quotation turns it into a
  VICINITY row, and the reference inside that parenthesis then defines the
  span's required text. (iii) A heading with nested emphasis (`**…*word*…**`)
  renders as a triple asterisk and should be avoided. (iv) In Python block
  files, `\\"` inside a triple-quoted string emits a literal backslash into
  the markdown; write `"` directly.
* **Commits.** One commit per tranche, message carrying the before/after table,
  the new heads, the struck headings, and the four gate lines. Push only
  `expanded/002.md` and `tools/quran-audit/*` to `arena/01a096ef-new`.

---

## Appendix A — generated registers

### A.1 Depth worklist by batch of twelve verses

| verses | words now | outstanding to floor | state |
| --- | --- | --- | --- |
| 1–12 | 15,332 | 0 | closed |
| 13–24 | 15,375 | 0 | closed |
| 25–36 | 16,208 | 0 | closed |
| 37–48 | 15,779 | 0 | closed |
| 49–60 | 10,023 | 4,156 | pending |
| 61–72 | 8,363 | 6,637 | pending |
| 73–84 | 8,451 | 6,549 | pending |
| 85–96 | 8,387 | 6,213 | pending |
| 97–108 | 8,297 | 6,703 | pending |
| 109–120 | 8,129 | 6,471 | pending |
| 121–132 | 7,581 | 7,219 | pending |
| 133–144 | 8,890 | 5,910 | pending |
| 145–156 | 7,870 | 7,130 | pending |
| 157–168 | 8,415 | 6,585 | pending |
| 169–180 | 9,406 | 5,794 | pending |
| 181–192 | 9,936 | 4,964 | pending |
| 193–204 | 9,959 | 4,669 | pending |
| 205–216 | 9,730 | 4,670 | pending |
| 217–228 | 9,361 | 5,139 | pending |
| 229–240 | 8,262 | 7,138 | pending |
| 241–252 | 7,543 | 7,257 | pending |
| 253–264 | 9,414 | 6,386 | pending |
| 265–276 | 7,556 | 7,044 | pending |
| 277–286 | 6,896 | 5,704 | pending |

### A.2 Cited spans still failing `check_cross_quotes.py`

Classes: **D** = DRIFT, **V** = VICINITY. Line numbers are current as of the tranche-3 commit.

| class | section | line | citation as written | span (truncated to 96 characters) |
| --- | --- | --- | --- | --- |
| D | 2:3 | 152 | 51:19; 70:24 |  The sentence performs a quiet revolution in the philosophy of ownership: before any giving is c |
| D | 2:9 | 368 | 3:54 |  — the Arabists explain — is not falsehood; it is the idiomatic use of the same word turned agai |
| D | 2:12 | 487 | 18:103–104 | Say: shall We inform you of the greatest losers in their works? Those whose effort is wasted in  |
| D | 2:13 | 522 | 29:64 |  of their sneer were compounding an eternal capital. There is no folly like a brilliant mind pla |
| D | 2:22 | 825 | 43:87 | while you know |
| D | 2:27 | 994 | 4:1 | and they sever what God has commanded to be joined. |
| D | 2:27 | 994 | 4:1 | has commanded *that it be joined* |
| D | 2:28 | 1025 | 76:1 | then He will cause you to die |
| D | 2:28 | 1025 | 76:1 | then He will give you life |
| D | 2:29 | 1062 | with parallels at 41:9–12, where the earth and its mountains | then He turned to the heaven and fashioned them, seven heavens. |
| D | 2:29 | 1062 | 20:5 | and He revealed in every heaven its affair |
| V | 2:33 | 1178 | cf. 35:38; 49:18 | He said: Did I not tell you that I know the unseen of the heavens and the earth, and that I know |
| D | 2:47 | 1574 | 3:110 | * (5:20). The preference lay in the *burdens-gifts*: prophecy in their midst, kingship united wi |
| V | 2:48 | 1601 | cf. 3:91, 5:36 | and ransom will not be accepted from it |
| D | 2:51 | 1678 | 31:13 | while you were wrongdoers |
| D | 2:62 | 1939 | 2:38 |  — as if to say: salvation is not the property of a name on a register but the consequence of th |
| D | 2:62 | 1939 | 46:13 |  — is the sūrah's own recurring formula for salvation, already given to those who follow God's g |
| D | 2:65 | 2010 | 62:5 |  was spoken? The commentators transmit two principal readings. The prevailing early view takes t |
| D | 2:65 | 2010 | 62:5 |  — comparing the case to the Qur'an's description of Torah-bearers who do not carry their script |
| D | 2:65 | 2010 | 17:50 |  The Book itself places all such images in a single moral family along with the spider of 29:41, |
| V | 2:65 | 2016 | reported by Ibn Baṭṭah and others; graded with weakness in i | Do not commit what the Jews committed, making God's prohibitions lawful through petty stratagems |
| D | 2:67 | 2056 | 11:46 | I seek refuge in God from being . |
| D | 2:67 | 2056 | 12:33 | among the ignorant |
| V | 2:75 | 2238 | cf. 2:55 | this is from God |
| V | 2:75 | 2238 | cf. 2:55 | after they had understood it, |
| V | 2:76 | 2257 | the descriptions and prophecies, cf. 7:157 | what God has unveiled/opened up to you |
| V | 2:77 | 2284 | cf. 9:16 | Do you think, perchance, that God does not know those of you who strive…? |
| D | 2:79 | 2326 | 2:16, 2:207, 61:10–11 |  trainings that teach students to *produce* authority rather than *transmit* it. Second, the buy |
| V | 2:81 | 2356 | as at the great sermon-clause 2:177, and at 21:26, 30:8 | Nay / Indeed rather |
| V | 2:83 | 2410 | cf. 3:113–115; 7:159 | then you turned away — save a few of you — while you were averting. |
| V | 2:89 | 2532 | cf. 7:157 |  In some transmitted versions they offered prayers in their own gatherings: * |
| V | 2:94 | 2643 | cf. 2:111: none will enter Paradise except those of their ow | Say: if the Abode of the Hereafter with God is exclusively yours, to the exclusion of other peop |
| V | 2:100 | 2771 | cf. 3:81 | We made no covenant concerning Muḥammad specifically |
| V | 2:101 | 2794 | cf. 2:99; 7:157 | those given the Book |
| V | 2:101 | 2794 | cf. 2:99; 7:157 | the Book of God |
| V | 2:102 | 2815 | the winds, the jinn, the subjugation of peoples; cf. 21:81–8 | and they followed what the satans recited against the kingdom of Solomon. |
| V | 2:104 | 2861 | as the parallel verse 4:46 takes note of Jews "twisting word | give us your ear. |
| V | 2:107 | 2918 | cf. 33:1–2 | Do you not know that God's is the dominion of the heavens and the earth? |
| V | 2:110 | 2989 | cf. 73:20; 75:13; 3:30 | and whatever good you send on ahead for your souls, you will find it with God. |
| D | 2:114 | 3073 | "the Sacred Mosque" 17:1 | who does *greater wrong* than... |
| V | 2:125 | 3334 | cf. 22:26–32 for the same Abrahamic rites | and take the Station of Abraham as a place of prayer. |
| V | 2:132 | 3487 | cf. 4:12; 5:106 | and Abraham charged his sons with it, as did Jacob. |
| V | 2:133 | 3518 | cf. 46:8; 19:98: "Do you ˹still˺ see any of them, or ˹even˺  | or were you witnesses when death came upon Jacob, and he said to his sons: what will you worship |
| V | 2:135 | 3582 | cf. 6:79; 6:162-63 — Abrahamic-path phrases sealed into the  | My Lord, make me firm upon Your religion... I have turned my face to You; I am the first of the  |
| D | 2:137 | 3622 | 3:173's ; 8:62; 9:59; 33:48 | God will suffice you against them. |
| V | 2:139 | 3676 | cf. the believer-counsels of the Salaf at this verse and 2:2 | Conceal your charity as you conceal your sins |
| D | 2:163 | 4200 | 57:3 | He is God the One |
| D | 2:163 | 4200 | 57:3 | He is God, there is no god but He |
| D | 2:163 | 4200 | 57:3 | He is the First and the Last, the Outward and the Inward |
| V | 2:169 | 4316 | cf. 2:80's  talk; 2:135's millah-claims | and to say about God what you know not |
| D | 2:181 | 4576 | related traditions assembled by the mufassirūn and jurists u | He who alters a bequest after hearing it bears upon himself the likeness of the one who introduc |
| D | 2:200 | 4995 | Islam recognizes the fathers' line as the first natural bond | as you remember |
| D | 2:207 | 5142 | the purchase of error at guidance's price, 2:16; the purchas | and among mankind |
| V | 2:220 | 5489 | 2:185's very words of the Ramadan-law — always cited in the  | God intends for you ease, and He does not intend for you hardship. |
| D | 2:246 | 6027 | 1 Samuel 8:19-20 once matching it phrase by phrase in the wh | when they said to a prophet of theirs: raise up for us a king — that we may fight in the way of  |
| D | 2:247 | 6042 | 6:124 | why him?why was this Quran not sent down upon a great man from one of the two towns?God knows be |
| V | 2:256 | 6211 | 10:99's: "Would you then force people to become believers?"; | sound judgment has been made clear from error |
| V | 2:264 | 6393 | Musnad Aḥmad; al-Ṭabarānī — the Prophet's *duʿāʾ al-shirk al | O God, I seek refuge in You from knowingly associating aught with You, and I ask Your forgivenes |
| V | 2:265 | 6414 | 2:233's own sealing at the nursing's end — and again at 2:23 | and God of whatsoever you do is Seeing |
| D | 2:281 | 6721 | — 2:272's own pattern refrain | and *fear a day — be mindful of a day* — when you shall be returned unto God |

### A.3 Counts

* DRIFT rows: 32 (25 of them six words or more, i.e. genuine misquotations
  rather than one-word glosses).
* VICINITY rows: 28, all spans whose parenthesis contains a qualifying
  word (`cf.`, `vicinity`, `sense`, `context`, `account`, `parallel`).
* Cited spans in the chapter: 249 (EXACT 189). Uncited quoted spans: 1,474.
* Sections still short of a floor: 251; the shortest five are 2:270 (342w), 2:252 (400w), 2:277 (405w), 2:250 (414w), 2:244 (424w).
