# Depth Plan — expanded/007.md (Sūrat al-Aʿrāf)

**Purpose.** This document proposes, section by section, exactly which sub-heads already
carry commentary and which new sub-heads should be added for the 43 Tier-1 sections.
Nothing here has been written into the deliverable yet. Each new head is listed with the
material that fills it and its source type, so that any head can be checked or struck out
before drafting begins.

**Repo state.** `expanded/007.md` = 206 sections, 269,247 words, gate-clean
(validate 114/114; cross-quotes 0 DRIFT / 0 ELLIPSIS / 0 VICINITY; census 0 FAILING).
PR #89, branch `arena/01a094c2-new`.

---

## 1. Method

### 1.1 Signals used to rank headroom

Five independent signals were computed per section, none of them raw word count:

| Signal | Measure | Why it indicates headroom |
|---|---|---|
| **A. Verse surface area** | words of the verse itself in `translation/007.txt` | A 72-word verse carries more content than a 12-word one; surface correlates with content but not identity |
| **B. Content units** | distinct semantic clauses (comma-delimited propositions in the verse) | counts what the verse *says*, independent of length |
| **C. Legal markers** | `forbidden/prohibited/commanded/ordained/prescribed/duty/right/lawful/unlawful/ruling/decree/permitted/prohibition` | flags verses with jurisprudential material that can be expanded from fiqh sources |
| **D. Uncited candidate parallels** | verses elsewhere in the corpus whose text shares distinctive vocabulary with this verse but is not quoted in the section | measures comparative-exegesis headroom |
| **E. Existing head coverage** | count of bold sub-head lines already present | measures what has already been consumed |

Tiering: **Tier 1** = (surface ≥ 50 words **or** units ≥ 8 **or** legal markers ≥ 4 **or**
uncited parallels ≥ 5) **and** not already exhausted. Result: 43 Tier 1, 36 Tier 2,
1 borderline, 126 Tier 3.

### 1.2 Groups

The 43 Tier-1 sections fall into four working groups, which determine *what kind* of new
material each needs:

| Group | Sections | Primary new-material source |
|---|---|---|
| **B — Rulings** | 7:31, 7:32, 7:33, 7:85, 7:148, 7:156, 7:28 | fiqh, lexical, named classical positions |
| **D — Doctrine** | 7:46, 7:54, 7:143, 7:157, 7:172, 7:176, 7:178, 7:187 | creedal positions, verified ḥadīth, reports |
| **A — Narrative** | 7:22, 7:27, 7:37, 7:38, 7:43, 7:44, 7:53, 7:69, 7:73, 7:89, 7:137, 7:146, 7:155, 7:158, 7:160, 7:169, 7:188, 7:189, 7:203 | verse surface, cross-verse narrative, named reports |
| **C — Comparative** | 7:56, 7:75, 7:88, 7:90, 7:92, 7:97, 7:98, 7:99, 7:128 | cross-verse chains from `translation/`, ḥadīth |

### 1.3 Verification legend

Every new head is tagged with how its content will be sourced:

- **[V]** — already verified in this session against a named primary or classical source; safe to draft.
- **[T]** — sourced entirely from `translation/NNN.txt`, which is the repo's own quote authority; no external claim involved.
- **[Q]** — a named report or ḥadīth that must be verified before drafting; the head is listed with what must be checked. If verification fails, the head is dropped, not softened.

**Standing rule carried from Item 2:** no ḥadīth is cited with a collection or number from
memory. Numbers appear only after a live check. Unverified material is attributed to "the
tradition reports" or omitted.

### 1.4 Hard constraints on all new material

1. Zero-hedge. No "cf.", "vicinity", "context" hedges. Literal glosses go outside quotation marks.
2. Every quoted span verbatim from `translation/`, each followed immediately by its own `(s:v)`.
3. No ellipsis spans. No paraphrase inside quotes. Bracketed inserts reproduced exactly.
4. No fillers, no formulaic recaps, no restatement of an existing head's content.
5. Target band 1,200–1,400 words per section, except the 20 documented reduced-floor sections.
6. `expanded/001.md` is never modified.

---

## 2. Structural findings (decisions needed)

These emerged from the head survey and are independent of the per-section work.

### 2.1 Two reduced-floor exceptions should probably be removed: 7:78 and 7:91

`7:78` ("So the earthquake seized them…", 955w) and `7:91` (same formula, 955w) are on the
20-section reduced-floor list as "scene-closers". The research shows both carry live
scholarly material that is *not* scene-closing:

- **[V]** The same event is described three ways: `rajfah` (earthquake) at 7:91 and 11:94's
  `ṣayḥah` (blast), plus `ẓullah` (the day of the cloud) at 26:189. Ibn Kathīr, on 26:176,
  holds that the companions of al-Aykah *were* the people of Madyan — "according to the most
  correct view" — so the three descriptions are of one people. Some exegetes held two or
  three distinct nations.
- **[V]** A grammatical asymmetry: 11:94 uses the plural *diyārihim* with the blast, 7:91 the
  singular *dārihim* with the earthquake — read as marking the blast's greater reach.
- **[V]** 26:189's "day of the cloud" is reported as scorching heat, then a cloud that rained fire.

Removing these two from the exception list and expanding them to band would add roughly
500 words each of genuine harmonisation material. **Decision needed: promote 7:78 and 7:91 to full band, or keep them as scene-closers and place the harmonisation in 7:90/7:92?**

### 2.2 One Tier-3 section should be promoted: 7:175

`7:175` ("And recite to them the news of the one to whom We gave Our signs…") was scored
Tier 3. It is the narrative setup for the dog parable at 7:176, and it carries the disputed
identity of the man:

- **[V]** Balʿam b. Bāʿūrāʾ — Ibn Masʿūd (via Shuʿbah from Manṣūr), Ibn ʿAbbās via
  al-ʿAwfī, ʿAlī b. Abī Ṭalḥah, Mālik b. Dīnār (the Madyan-king account), Ibn Isḥāq.
- **[V]** Umayyah b. Abī ṣ-Ṣalt — ʿAbdullāh b. ʿAmr and Zayd b. Aslem.
- **[V]** Sayfī b. ar-Rāhib — Qatādah.
- **[V]** Mawdūdī's methodological caution: the identity is not established by Qurʾān or
  ḥadīth, so the lesson does not depend on it.

Since 7:176 is already Tier 1 with 15 heads, the identity dispute is better housed in 7:175.
**Decision needed: promote 7:175 to Tier 1 (adds ~400 words) or keep the identity material inside 7:176?**

### 2.3 Two sections are qualitatively over-banded: 7:2 and 7:3

Both are programmatic (26w and 43w) but sit at 1,381w and 1,384w. They have no legal or
doctrinal headroom; their Tier-1 score came from uncited parallels (18 and 15), which are
almost all thematic rather than substantive. **Recommendation: leave both as they are and
spend no further depth on them.** Listed here so their exclusion from the drafting plan is
explicit rather than accidental.

---

## 3. Group B — Ruling verses

### 3.1 7:85 — Shuʿayb's market commands (1,384w; verse 72w, 15 units, 7 legal markers, 7 heads)

**Existing heads (7):** The Prophet of the Market | The Order of the Commandments | Give Full
Measure and Full Weight | Do Not Deprive People | Do Not Corrupt the Earth After Its Repair |
That Is Better for You | The Clear Sign and Its Demand

**Proposed new heads (5):**

1. **Kail and Mīzān: Volume and Weight as Two Instruments** — **[V]** lexical: *kayl* is
   dry measure by volume, *mīzān* is weighing; the two named because they are the two
   instruments by which shortfall enters a transaction. Source: Maʿārif al-Qurʾān on 7:85.
2. **Bakhs and Taṭfīf: Two Names for the Same Shortfall** — **[V]** *bakhs* = to bring loss
   on someone by giving less than what is due; *taṭfīf* = measuring and weighing short.
   Pair with **[T]** 83:1–3, the sūrah named after the offence: "Woe to the defrauders!
   Those who take full measure ˹when they buy˺ from people, but give less when they measure
   or weigh for buyers." The asymmetry — full when buying, short when selling — is the
   offence's definition.
3. **The Aykah Parallel: Same Commands Under a Different Name** — **[T]** 26:181–183 verbatim
   ("Give full measure, and cause no loss ˹to others˺. Weigh with an even balance, and do not
   defraud people of their property…") against 7:85, plus **[V]** Ibn Kathīr on 26:176 that
   the Aykah people were Madyan, and that 26:177 deliberately omits "their brother".
4. **Goodwill as the Verse's Own Reward** — **[V]** Maʿārif's reading of "That is better for
   you": honesty in weights and measures establishes credit and goodwill in the market, so
   the benefit is realised in this world as well as the next. This is the verse's only
   self-interested argument and deserves its own head.
5. **"Whoever cheats us is not of us"** — **[Q]** the well-known *man ghashshanā falaysa
   minnā*. **Must verify collection and number before drafting** (believed Ṣaḥīḥ Muslim,
   from Abū Hurayrah, in the context of a heap of grain). If verification fails, replace with
   the verified ṣiddīq-trader report or drop the head.

### 3.2 7:31 — Adornment at every place of worship (1,383w; verse 27w, 6 units, 4 legal markers, 6 heads)

**Existing heads (6):** The Children of Adam Addressed Directly | Take Your Adornment at Every
Masjid | Eat and Drink, But Do Not Excess | He Loves Not the Excessive | The Occasion Reported
for the Command | Isrāf and Tabdhīr

**Proposed new heads (4):**

1. **Zīnah Beyond the Minimum: What Adornment Adds to Covering** — **[V]** the command is
   *khudhū zīnatakum*, take your adornment, not merely cover yourselves. Ibn Kathīr: Allah
   commands taking adornment when going to the masjid. The juristic distinction between the
   obligatory minimum and the recommended adornment is the head's content.
2. **Ṭawāf as the Occasion's Legal Residue** — **[V]** the exegetical gloss that the command
   addresses praying *and* circumambulating (Hilālī/Khān's parenthetical), which is why the
   ruling survives the disappearance of the pre-Islamic practice it answered. The existing
   head covers the occasion narratively; this head covers it jurisprudentially.
3. **The Default of Permissibility with a Limit** — **[T]** the verse's shape is "eat and
   drink, but do not exceed" — permission stated first, limit second. Read against 7:32's
   question ("Who has forbidden the adornment?") this establishes that ascetic prohibition
   is the deviation, not the norm. Cross-verse **[T]**: 5:87–88 and 6:145 if available.
4. **Extravagance Without Pride, and Pride Without Extravagance** — **[Q]** the ḥadīth
   "eat and drink and wear and give charity without extravagance or pride" (believed Aḥmad /
   Ibn Mājah, from ʿAmr b. Shuʿayb from his father from his grandfather). **Verify before
   drafting.** It matters because it splits *isrāf* (excess in amount) from *kibr* (excess in
   motive), which the existing Isrāf-and-Tabdhīr head does not reach.

### 3.3 7:33 — The five things forbidden (1,382w; verse 39w, 8 units, 8 legal markers, 6 heads)

**Existing heads (6):** Say: My Lord Has Forbidden Only | The Indecencies, Open and Secret |
Sin and Unjust Aggression | Association for Which No Authority Was Sent | To Say of Allah What
You Do Not Know | The Shape of the Prohibition

**Proposed new heads (4):**

1. **Ithm and Baghy: The Sin Against the Self and the Sin Against Others** — **[V]** Ibn
   Kathīr's synthesis with two named authorities: as-Suddī ("al-ithm means disobedience;
   unrighteous oppression occurs when you transgress against people without justification")
   and Mujāhid ("ithm includes all types of disobedience"). The pair covers the two
   directions of wrongdoing — inward and social — which is why both are named.
2. **Divine Jealousy as the Reason for the First Prohibition** — **[Q]** Aḥmad, from
   ʿAbdullāh (Ibn Masʿūd): "None is more jealous than Allah, and this is why He prohibited
   fawāḥish, open and secret; and none likes praise more than Allah" — reported in the two
   Ṣaḥīḥs. **Verify numbers before drafting.** This is the only head that supplies a *reason*
   rather than a definition.
3. **The Anʿām Parallel: One List Inside Another** — **[T]** 6:151 verbatim ("Come! Let me
   recite to you what your Lord has forbidden to you: do not associate others with Him
   ˹in worship˺…"). Ibn Kathīr explicitly refers the reader to Sūrat al-Anʿām for the
   open-and-secret fāḥishah. The comparison shows 7:33 as a compressed restatement of the
   longer prohibition list, with "saying about Allah what you do not know" as its distinctive
   addition.
4. **Sulṭān: Authority as the Test of Association** — **[T]** the phrase *mā lam yunazzil bihi
   sulṭānan* makes the absence of revealed authority, not the object's nature, the criterion.
   Pair with **[T]** 42:21 and 10:59 if in scope. This is the verse's epistemic claim and
   connects directly to head 5 of the existing list.

### 3.4 7:28 — The charge of inventing against Allah (1,358w; verse 21w, 6 units, 6 legal markers, 6 heads)

**Existing heads (6):** The Exposure of the Claim | They Say: We Found Our Fathers | And Allah
Ordered Us | The Two-Part Excuse | The Command to Say | The Refutation

**Proposed new heads (3):**

1. **"Say: Indeed Allah Does Not Order Indecency"** — **[T]** the refutation's logical form:
   the verse does not deny that Allah orders things, only that He orders *this*. The denial is
   of attribution, not of command. Compare **[T]** 16:90 and 2:268 ("The Devil threatens you
   with ˹the prospect of˺ poverty and bids you to the shameful deed ˹of stinginess˺") — the
   same act attributed to the opposite agent.
2. **The Third Prohibition: Saying About Allah What You Do Not Know** — **[T]** 7:33's fifth
   item names exactly what 7:28's opponents do. The two verses are the diagnosis and the
   prohibition of one offence, and the section should say so with both quoted.
3. **Fāḥishah as a Technical Term Across the Sūrah** — **[T]** 7:28, 7:33, 7:80–81, 7:148
   and 4:19 all use the root. A short lexical head establishing that *fāḥishah* denotes what
   exceeds the recognised limits, not merely sexual offence, lets the later verses be read
   consistently. Cross-verse **[T]** from 4, 16, 17 as available.

### 3.5 7:32 — Who has forbidden the adornment? (1,393w; verse 47w, 9 units, 6 legal markers, 4 heads)

**Existing heads (4):** The Question Posed to the Disbelievers | The Answer: For the Believers
in This Life | Exclusively Theirs on the Day of Resurrection | The Detailed Signs for a People
Who Know

**Proposed new heads (4):**

1. **The Rhetorical Question as Legal Argument** — **[T]** *man ḥarrama* ("Who has
   forbidden…?") is not a request for information but a challenge to produce authority. Read
   with **[T]** 7:33's *sulṭān* criterion, the section's argument becomes: prohibition
   requires revelation, and no revelation prohibits these things.
2. **Zīnah in This Life, Exclusive in the Next** — **[V]** the classical reading that the
   good things are shared in this life but exclusive to the believers on the Day of
   Resurrection. The two halves of the verse are not redundant; they answer the objection
   "the disbelievers enjoy them too".
3. **The Ascetic Objection Answered** — **[V]** the verse's occasion in the exegetical
   tradition: those who forbade themselves adornment and food. Pair with **[T]** 5:87 ("O you
   who believe! Do not prohibit the good things Allah has made lawful to you") if available —
   the same objection answered in a different register.
4. **Detailing for a People Who Know** — **[T]** *nufaṣṣilu al-āyāt li-qawmin yaʿlamūn*
   restricts the benefit of the detail to those with knowledge, which is the verse's
   epistemic condition. Compare **[T]** 7:174 and 6:97–98 for the same formula, establishing
   that the restriction is stylistic across the sūrah, not local.

### 3.6 7:156 — The conditions of the mercy (1,381w; verse 66w, 14 units, 6 legal markers, 15 heads)

**Existing heads (15):** already dense — *My Mercy Encompasses All Things* | *But I Will
Decree It for Those Who Fear* | *And Give Zakah* | *And Believe in Our Signs* | *Those Who
Follow the Messenger* | *The Unlettered Prophet* | *Whom They Find Written in the Torah and
Gospel* | *He Enjoins What Is Right* | *And Forbids What Is Wrong* | *He Makes Lawful the
Good* | *And Prohibits the Evil* | *He Relieves Them of Their Burden* | *And the Shackles
That Were on Them* | *The Conditions of Success* | *The Verse as Charter* (+1)

**Proposed new heads (3 — exhaustion risk flagged):**

1. **The Four Verbs of Loyalty, Separately Weighed** — **[T]** the verse's closing sequence
   distinguishes believing in him, honouring him, helping him, and following the light sent
   down with him. The existing head treats them as a set; the new head takes each in turn and
   asks what fails when one is dropped. **[T]** 48:29 and 3:144 supply the parallels.
2. **Mercy Encompassing and Mercy Decreed: The Tension and Its Resolution** — **[V]** the
   verse asserts universal scope in one clause and particular decree in the next. The
   classical resolution (encompassing in this life, decreed in the next; or encompassing as
   capacity, decreed as bestowal) is genuine doctrinal content not yet in the section.
3. **Zakah Named Before the Law Was Complete** — **[V]** a Meccan verse naming zakah as a
   condition of mercy, before the Madinan quantification. The head's content is the
   relationship between the general obligation and its later specification, with **[T]**
   9:60 for the specified categories.

### 3.7 7:148 — The calf and the charge of indecency (1,392w; verse 42w, 8 units, 4 legal markers, 15 heads)

**Existing heads (15):** dense — *The Calf of the People* | *A Body With a Lowing* | *Did They
Not See It Could Not Speak?* | *Nor Guide Them to a Way* | *They Took It and Were Wrongdoers* |
*When Their Hands Fell* | *They Said: If Our Lord Does Not Have Mercy* | *We Will Be Losers* |
*When Moses Returned Angry and Grieved* | *What Evil Succession* | *Have You Deceived Your
People After Me?* | *Or Are You Hasty Against the Command of Your Lord?* | *He Threw the
Tablets* | *He Took His Brother by the Head* | *The Charge of Indecency* (+1)

**Proposed new heads (2 — exhaustion risk flagged):**

1. **Suʾ al-Khulaf: "Have You Deceived Your People After Me?"** — **[T]** the Arabic *khalaf*
   (succession, the group left behind) is the verse's pivot, rendered here "succession". The
   head's content is the double edge of the rebuke: it accuses both the people and the
   arrangement Moses left. Pair **[T]** with 20:85–86, the parallel account, quoted verbatim.
2. **Fāḥishah Applied to an Act of Worship** — **[T]** the calf-making is called indecency,
   which links 7:148 to 7:28 and 7:33 and completes the sūrah's lexical thread. This head is
   short by design and cross-referential.

---

## 4. Group D — Doctrinal verses

### 4.1 7:143 — The request to see (1,387w; verse 78w, 15 units, 15 heads)

**Existing heads (15):** dense — *When Moses Came at Our Appointed Time* | *His Lord Spoke to
Him* | *He Said: My Lord, Show Me* | *That I May Look at You* | *You Will Not See Me* | *But
Look at the Mountain* | *If It Remains in Its Place You Will See Me* | *When His Lord
Revealed Himself to the Mountain* | *He Made It Dust* | *Moses Fell Unconscious* | *When He
Awoke He Said: Glory Be to You* | *I Turn to You in Repentance* | *I Am the First of the
Believers* | *He Said: O Moses, I Chose You Over the People* | *With My Messages and My
Speech* (+1)

**Proposed new heads (6 — the richest doctrinal site in the sūrah):**

1. **Lan Tarānī and Lan Urā: The Grammar of the Refusal** — **[V]** the decisive textual
   question. *Lan tarānī* ("you will not see Me") is addressed to Moses's capacity, not to the
   possibility of sight as such; the Muʿtazilī reading treats the negation as absolute and
   permanent. Ahl al-Sunnah: not seen in this world, seen in the Hereafter. Muʿtazilah and
   Shīʿah: never. The head states the grammatical argument and names both positions.
2. **Al-Qurṭubī's Three Premises** — **[V]** from his tafsīr on this verse: (a) sight is in
   itself possible, (b) prophets do not ask for the impossible, therefore (c) the request was
   for something possible. Also **[V]** his handling of the objection that repentance implies
   sin: *tawbah* here is turning, not expiation of a transgression.
3. **Al-Suyūṭī and al-Jalālayn on Capability** — **[V]** the gloss that the refusal concerns
   Moses's capacity to bear the sight, which makes the mountain demonstration a proof about
   the viewer, not the viewed.
4. **The Tajallī and the Fingertip** — **[Q]** the report that the manifestation was at the
   level of a fingertip and levelled the mountain. **Verify source and grade before
   drafting.** If unverifiable, replace with **[V]** 11:94's *ṣayḥah* comparison or drop.
5. **The Miʿrāj Light Report as the Counter-Witness** — **[Q]** Muslim's report from Abū
   Dharr, "There was only light; how could I see Him?" **Verify the number before drafting**
   (the Muslim reference is believed but not yet checked in this session). This head matters
   because it is the strongest textual argument that the Prophet did not see Allah, which the
   Ahl al-Sunnah position must answer rather than ignore.
6. **Ziyādah and the Sight of the Hereafter** — **[T]** 10:26 verbatim ("For those who do
   good is the best reward and extra") plus the report **[Q]** "innakum satarauna Rabbakum"
   — **verify before drafting.** The head establishes that the verse's refusal is
   world-specific by producing the Qurʾān's own counter-evidence.
7. **On Whose Behalf Did Moses Ask?** — **[V]** the exegetical position that the request was
   made on behalf of the seventy (7:155), which reframes the refusal as addressed to a
   collective capacity. Cross-reference **[T]** 7:155 and 2:55.

*Net: 6–7 new heads, of which three require verification. This is the single deepest
available expansion in the sūrah and should be drafted first within Group D.*

### 4.2 7:46 — The people of the Heights (1,396w; verse 51w, 10 units, 5 heads)

**Existing heads (5):** Between Them Is a Barrier | And on the Heights Are Men | They Know Each
by Their Mark | They Call Out to the People of Paradise | Peace Be Upon You

**Proposed new heads (7 — the largest head deficit relative to material):**

1. **ʿUrf: The Crest as a Place** — **[V]** lexical: *aʿrāf* is the plural of *ʿurf*, the
   crest of a rooster or the ridge of a mountain — the high dividing edge between two sides.
   The name is topographical, and the topography is the theology: a boundary, not a
   destination.
2. **The Ten Classical Identifications** — **[V]** the survey, each with its authority:
   (1) those whose good and evil deeds are equal — Ibn ʿAbbās and Ḥudhayfah; (2) those martyred
   while disobedient to their parents — Sharābīl b. Saʿd; (3) pious scholars — Mujāhid;
   (4) angels — no authentic narration supports it; (5) prophets — al-Ālūsī, who calls them
   the *masākīn* of Paradise; (6) debtors — Muslim b. Yasār; (7) people of the *fiṭrah*;
   (8) children of the polytheists; (9) children of fornication — Ibn ʿAbbās; (10) the last
   to enter. This is one head, not ten, presented as a ranked tradition.
3. **Al-Ālūsī's Adjudication** — **[V]** his conclusion that al-Qurṭubī's first view (equal
   deeds) is the most apparent, and that the other identifications are gathered within it
   rather than competing with it. Also **[V]** ar-Rāzī's objection to the martyr view: it
   collapses into equal deeds, since martyrdom would outweigh the disobedience.
4. **The Supporting Report on the Scales** — **[Q]** the report that when the scales balance
   to an atom's weight, the person is placed on the Heights, and the report of the last to
   enter being told "Enter by My virtue". **Verify both before drafting.**
5. **Not Purgatory** — **[V]** the explicit distinction: no suffering, no purgation, no
   earned transition — only suspense followed by mercy. This head exists to prevent the
   common comparative misreading, and states the difference rather than arguing against it.
6. **Who Speaks in 7:47?** — **[V]** the exegetical dispute, including the Khorasani position
   that the speakers are the people of Paradise rather than the people of the Heights.
   Pair **[T]** 7:47 verbatim as the text in question.
7. **The Judicial Function of the Heights** — **[T]** 7:48 shows the Heights' men as
   witnesses who recognise and rebuke. The head establishes that their position is
   evidentiary, not merely punitive delay, quoting **[T]** 7:48–49 verbatim.

### 4.3 7:54 — The Throne, creation and command (1,374w; verse 62w, 12 units, 8 heads)

**Existing heads (8):** From the Hereafter to the Maker | In Six Days | Then He Rose Over the
Throne | The Night Covers the Day | The Sun, Moon and Stars Under Command | His Is the
Creation and the Command | The Bearers of the Throne | Creation and Command, Then Supplication

**Proposed new heads (5):**

1. **Istawā: What Is Known, What Is Not, and What Asking Costs** — **[V]** the report from
   Mālik b. Anas recorded in Maʿārif al-Qurʾān on this verse: the meaning of *istawā* is
   known; its nature is beyond human reason; believing it is obligatory; asking about its
   nature is innovation, because the Companions never asked the Prophet ﷺ. *Istawā* with
   *ʿalā* literally means to take position on, to settle, to be established; *ʿarsh* is
   throne. The head presents the *tafwīḍ* position in its own words.
2. **Seven Verses, One Formula** — **[T]** verified count from `translation/`: the
   throne-establishment formula appears at 7:54, 10:3, 13:2, 20:5, 25:59, 32:4, 57:4. Each
   quotable verbatim from its own file. The head establishes that this is a fixed creedal
   formula in the Qurʾān, not a local image, and that 7:54 is its first occurrence.
3. **Khalq and Amr: Two Domains** — **[V]** al-Māzharī as recorded in Maʿārif: everything
   between the heavens and the earth is matter and its production is *khalq*; what is beyond
   matter is *amr*. Supported by **[T]** 17:85, where the spirit is described as belonging to
   the Lord's *amr* (this translation renders it "Its nature is known only to my Lord", so the
   Arabic is glossed outside the quotation marks per the standing rule).
4. **Delegated Authority Is Still His Command** — **[V]** Maʿārif's point that no one else can
   create the most insignificant thing, nor subject anyone to his command, except where Allah
   delegates an area of activity — and even then it is in reality Allah's command. This is the
   verse's answer to any reading of *amr* that implies shared governance.
5. **Thumma and the Question of Sequence** — **[T]** *thumma istawā* follows *khalaqa… fī
   sittati ayyām*. The head addresses whether *thumma* marks temporal sequence in the
   act or rank in the statement — a real kalām question, handled by comparing **[T]** 20:4–5
   ("˹It is˺ a revelation from the One Who created the earth and the high heavens—the Most
   Compassionate, ˹Who is˺ established on the Throne"), where no sequence is marked at all.

### 4.4 7:157 — The unlettered Prophet and the lifting of burdens (1,398w; verse 74w, 15 units, 15 heads)

**Existing heads (15):** dense, and they include *He Relieves Them of Their Burden*, *And the
Shackles That Were on Them*, *The Burdens and What the Tradition Reports of Them*, *The
Unlettered Prophet*, *Whom They Find Written in the Torah and Gospel*, and the four verbs of
loyalty.

**Proposed new heads (4):**

1. **Iṣr and Aghlāl, Precisely** — **[V]** Maʿārif's lexical definition: *iṣr* is a burden
   heavy enough to stop movement; *aghlāl* is the plural of *ghull*, the handcuff that binds a
   criminal's hands to his neck. Both terms denote punishment and were not themselves
   religious requirements. The existing heads name the burdens; this head defines the words.
2. **The Burdens Named: Cutting the Cloth, Killing the Self, the Sabbath** — **[V]** the
   worked example from Maʿārif: the Israelites were required to cut away the piece of cloth
   bearing impurity, not merely wash it. Pair **[T]** 2:54 (the command to kill themselves in
   repentance) and **[T]** 2:65–66 / 4:154 (the Sabbath) verbatim, so the abstract "burdens"
   acquire three concrete referents.
3. **Why an Imperfection Becomes the Proof** — **[V]** Maʿārif's observation that *ummī*
   signifies one who does not know reading and writing, and that the Qurʾān calls the Arabs
   *ummiyyūn* because they generally had little to do with either; incapacity in reading and
   writing is not in itself a merit. The head's argument is that the term is evidential here
   precisely because it is not a merit: a book from one who cannot read or write is the proof.
   Pair **[T]** 29:48 ("And you did not read any scripture before it, nor did you write one
   with your right hand") if available.
4. **The Torah's Description as Reported** — **[Q]** the narrated description — witness over
   the nations, bearer of good tidings, warner, named *Mutawakkil*, not harsh-tempered, not
   quarrelling, not crying in the markets, not returning evil for evil. **Verify the chain and
   source before drafting** (believed to run through ʿAṭāʾ b. Yasār, from ʿAbdullāh b. ʿAmr).
   If unverifiable, the head reduces to **[T]** 48:29 and 3:159 as the Qurʾān's own portrait
   of the same traits.

### 4.5 7:172 — The primordial covenant (1,397w; verse 60w, 12 units, 15 heads)

**Existing heads (15):** very dense — including *The Nature of the Event*, *The Self as
Witness*, *The Recited Witness*, *The Disposition the Covenant Presupposes*, *The Book's
Appeal to Universal Knowledge*, *The Next Verse's Second Excuse*.

**Proposed new heads (3 — exhaustion risk high; new material restricted to named sources):**

1. **Souls as Troops Collected Together** — **[Q]** the Ṣaḥīḥ Muslim report *al-arwāḥ
   junūdun mujannadah*. **Verify the number before drafting.** It is the only ḥadīth that
   bears directly on pre-existent grouping, and therefore on whether the covenant is read
   literally.
2. **Obligation Before Revelation: The Kalām Question** — **[V]** the verse's use in the
   debate over whether knowledge of God is innate and whether accountability attaches before
   a messenger arrives. Pair **[T]** 17:15 ("And We never punish until We have sent a
   messenger") as the counter-text the position must reconcile. This head is doctrinal, not
   narrative, and is genuinely absent from the section.
3. **Two Excuses Closed by One Verse** — **[T]** the verse names the first excuse ("we were
   unaware") and 7:173 the second ("our fathers associated partners"). The existing head
   covers 7:173's existence; the new head quotes **[T]** 7:173 verbatim and sets out the
   argument that the two excuses are individually exhaustive and jointly closed, which is
   the verse's stated purpose (*an taqūlū*).

### 4.6 7:176 — The parable of the dog (1,390w; verse 40w, 9 units, 15 heads)

**Existing heads (15):** dense, including *The Dog Panting Whether Driven or Left*, *The
Parable of the People Who Denied*, *The Sign Is Not the Miracle*, *Follow Desire or Not*.

**Proposed new heads (4):**

1. **Who Is the Man? Three Named Candidates** — **[V]** Balʿam b. Bāʿūrāʾ (Ibn Masʿūd via
   Shuʿbah from Manṣūr; Ibn ʿAbbās via al-ʿAwfī, placing him in Yemen; ʿAlī b. Abī Ṭalḥah,
   "a city of tyrants, who knew the Greatest Name"; Mālik b. Dīnār's account of the scholar
   whose supplication was answered, sent to the king of Madyan and apostatising for gifts;
   Ibn Isḥāq, of Banū Kānān in ash-Shām); Umayyah b. Abī ṣ-Ṣalt (ʿAbdullāh b. ʿAmr and Zayd
   b. Aslem: he studied the scriptures, hoped to be the messenger, and envied Muḥammad ﷺ);
   Sayfī b. ar-Rāhib (Qatādah). One head presenting the three with their authorities.
2. **Mawdūdī's Caution, and Why the Lesson Survives It** — **[V]** the identity is not
   established by Qurʾān or ḥadīth, so no doctrine depends on it. Pair with **[V]** the
   report from al-Bāqir that the *mathal* is for all who follow *hawā*, which generalises
   rather than identifies.
3. **Two Readings of the Dog** — **[V]** (a) the literal tongue flickering, as Ibn Isḥāq
   describes, (b) the general condition of misguidance: panting whether driven away or left
   alone. The head distinguishes an image of *physical* restlessness from one of *spiritual*
   restlessness and shows that the verse supports both.
4. **The Parable's Placement in the Verse's Argument** — **[T]** the verse's own frame:
   *famsal al-qawm alladhīna kadhdhabū bi-āyātinā* — the parable is explicitly of the people
   who denied the signs, plural and collective. **[T]** 7:175 supplies the singular setup. The
   head resolves the apparent shift from one man to a people by quoting both.

### 4.7 7:178 — Istidrāj (1,388w; verse 27w, 6 units, 14 heads)

**Existing heads (14):** dense, including *He Is Given Respite*, *So They Do Not Perceive*,
*The Respite and the Seizure*, *Istidrāj Defined*.

**Proposed new heads (3):**

1. **The Verified ḥadīth of ʿUqbah b. ʿĀmir** — **[V]** **Musnad Aḥmad 17311, graded ḥasan by
   al-Arnaʾūṭ**: "If you see Allah giving a servant what he loves from the worldly life,
   despite his sinful disobedience, then surely it is luring him to destruction" — after which
   the Prophet ﷺ recited 6:44. This is the only fully verified ḥadīth in the Tier-1 research
   and should be cited with its number and grade.
2. **D-R-J: The Root and Its Motion** — **[V]** lexical: *daraja* is to ascend step by step;
   *istidrāj* is to be led upward one step at a time toward destruction, imperceptibly. The
   metaphor's structure — high, then dropped — is what makes the respite itself the
   punishment. Pair **[T]** 6:44 verbatim ("When they became oblivious to warnings, We
   showered them with everything they desired. But just as they became prideful of what they
   were given, We seized them by surprise…") and **[T]** 3:178 ("They are only given more time
   to increase in sin").
3. **Satirical Postponement: The Rhetorical Form** — **[V]** the metaphor study's finding that
   *istidrāj* operates as satirical postponement and as retribution through the instruments
   of the offence itself. The head is rhetorical rather than lexical and completes the
   triangle with the two above.

### 4.8 7:187 — The Hour and its knowledge (1,386w; verse 45w, 10 units, 15 heads)

**Existing heads (15):** very dense, including *They Ask You About the Hour*, *When Will It
Be?*, *Say: Its Knowledge Is With My Lord*, *None Reveals Its Time But He*, *It Is Heavy in
the Heavens and Earth*, *It Will Not Come Except Suddenly*, *They Ask You as Though You Were
Aware of It*.

**Proposed new heads (2 — exhaustion risk high):**

1. **Kaʾannaka Ḥafiyyun ʿAnhā: The Idiom and Its Weight** — **[V]** the phrase means "as
   though you were well acquainted with it" — a pointed rebuke that the question presumes
   knowledge the questioner does not have. This is a lexical head with a rhetorical
   consequence, and it is the verse's most compressed element.
2. **Suddenness as the Hour's Defining Attribute** — **[T]** the verse states it will not come
   except suddenly; pair **[T]** 7:187 with 6:31, 12:107 and 21:40 verbatim, where the same
   suddenness is asserted. The head's content is that the Qurʾān consistently refuses timing
   while consistently asserting abruptness — refusal and assertion are the two halves of one
   doctrine.

---

## 5. Group A — Narrative verses

The 19 sections here split sharply. Ten are **thin** (5–8 existing heads, real deficit);
nine are **dense** (13–16 heads, little unconsumed material). New heads are proposed in
proportion: 3–4 for thin sections, 0–2 for dense ones, where only a genuinely new angle is
offered rather than a restatement.

### 5.1 Thin sections (real head deficits)

#### 7:22 — The descent (1,355w, 7 heads → +4 new)
1. **Satan's Oath as the Instrument** — **[T]** 20:118–120 verbatim: the deception succeeds
   because it is sworn by Allah, which the section's existing heads do not address.
2. **The Tree Named and Not Named** — **[T]** compare 2:35, 7:19, 20:120: the species is
   never given. The withholding is itself exegetical material.
3. **Hubūṭ as Legal Status, Not Geography** — **[T]** the descent formula counted across
   2:36, 2:38, 7:24, 20:123; each occurrence and what it adds.
4. **ʿAmal: The First Kind of Work** — **[T]** the sūrah's vocabulary of *ʿamal* (7:22, 7:147,
   7:176) against *ṣāliḥāt*, establishing that the garden's consequence is stated in the
   sūrah's own technical term.

#### 7:27 — The warning repeated (1,317w, 7 heads → +3)
1. **Libās at-Taqwā: The Third Garment** — **[T]** 7:26 verbatim names two garments and a
   third, "the garment of piety", which is best; 7:27 then warns of the removal of the first.
   The three-garment structure is not yet drawn out.
2. **7:26 and 7:27 as One Unit** — **[T]** the command and the warning in sequence; the
   section treats 7:27 alone.
3. **The Unseen Vantage as a Creedal Premise** — **[T]** "he and his tribe see you from where
   you do not see them" asserts a class of beings with sight and no visibility. Pair **[T]**
   7:202 and 6:112 for the same premise.

#### 7:37 — The two crimes (1,372w, 5 heads → +4)
1. **"Who Is More Unjust Than…": A Formula Counted** — **[T]** 6:21, 10:17, 11:18, 29:68,
   39:32, 61:7 verbatim — the Qurʾān's fixed superlative of injustice, always attached to
   inventing against Allah.
2. **Naṣīb min al-Kitāb: The Appointed Share** — **[T]** the share is from *the Book*, which
   makes destiny textual rather than arbitrary. Pair **[T]** 7:37 with 3:145.
3. **Tawaffā and Its Agents** — **[T]** 6:61, 16:28, 16:32, 47:27 verbatim: who takes the
   soul, and the difference between the two descriptions.
4. **Confession at the Moment of Taking** — **[T]** the verse's legal structure compared with
   **[T]** 7:23 and 6:23–24, where the same confession occurs at a different point.

#### 7:38 — The sentence at the gate (1,373w, 7 heads → +3)
1. **The Curse Between Groups as the Fire's Social Order** — **[T]** 7:38, 29:25, 16:88,
   23:100 verbatim: enmity among the damned is presented as part of the punishment.
2. **Ḍiʿf Doubled: Two Senses** — **[T]** 7:38's double punishment against **[T]** 17:75 and
   33:68; whether doubling falls on the leaders, the followers, or the punishment.
3. **The Jinn-and-Men Assembly** — **[T]** 6:112 and 6:128 verbatim, the two accounts of the
   same partnership.

#### 7:43 — Bitterness removed (1,373w, 7 heads → +3)
1. **Ghill Removed: Eschatological Psychology** — **[T]** 15:47 verbatim ("And We will remove
   any bitterness from their hearts") against 7:43; the only two places the removal is stated.
2. **The Rivers Formula, Counted** — **[T]** the frequency and variation of "rivers flowing
   beneath" across the corpus, establishing it as a fixed formula rather than an image.
3. **Taḥiyyah as Greeting** — **[T]** 10:10 and 14:23 verbatim: the greeting's exact words in
   Paradise, which 7:44 then uses across the barrier.

#### 7:44 — The call across the divide (1,367w, 5 heads → +3)
1. **The Munādī and the Two Calls** — **[T]** 7:44, 3:193, 50:41 verbatim: a caller from a
   place, and what each call announces.
2. **Salām ʿAlaykum as the Greeting Across the Barrier** — **[T]** 13:24, 16:32, 39:73
   verbatim: the same greeting at the gates, at death, and at the barrier.
3. **7:44 as Hinge** — **[T]** the verse sits between the saved (7:43) and the Heights
   (7:46–49); its function in the sequence is not yet stated, and **[T]** 7:45 completes it.

#### 7:53 — The waiting and the confession (1,292w, 8 heads → +3)
1. **Intercession's Conditions, Counted** — **[T]** 2:255, 10:3, 20:109, 21:28, 34:23, 53:26
   verbatim: every place the Qurʾān states a condition for intercession, set against the
   verse's request.
2. **The Request to Return and Its Refusal** — **[T]** 23:99–100, 32:12, 35:37 verbatim: the
   same request, three times refused, with the reason given in each.
3. **Ruining Oneselves as the Verdict Formula** — **[T]** 6:12 and 7:53 verbatim, plus the
   sūrah's other uses of *khusra/khāsirūn*, showing the verdict is self-inflicted by
   construction.

#### 7:69 — ʿĀd's succession and stature (1,261w, 7 heads → +3)
1. **Khalāʾif as a Qurʾānic Category** — **[T]** 6:165, 10:14, 10:73, 27:62, 35:39 verbatim:
   succession after a destroyed people is a defined category, and 7:69 is one instance.
2. **The Monuments of 26:128–130** — **[T]** verbatim: "Do you build a landmark on every high
   place…?" — the same people described by their architecture, which supplies what "increased
   you greatly in stature" is contrasted against.
3. **Remembering Favours as the Precondition of Belief** — **[T]** 7:69, 2:47, 3:164 verbatim:
   the command to remember is always paired with a call to believe.

#### 7:73 — The she-camel's terms (1,385w, 7 heads → +4)
1. **The Water-Share as a Legal Institution** — **[T]** 26:155 verbatim ("Here is a camel. She
   will have her turn to drink as you have yours, each on an appointed day") and **[T]** 54:28
   verbatim ("the ˹drinking˺ water must be divided between them ˹and her˺, each taking a turn
   to drink ˹every other day˺"). Three verses describing one rota; the division is a scheduled
   allocation, not a moral request.
2. **Nāqat Allāh: Ownership as Consequence** — **[T]** 91:13 verbatim ("the she-camel of Allah
   and her drink") — the camel is Allah's property, so harming her is not property damage but
   violation. This is the legal logic the existing heads gesture at without stating.
3. **Harm and the Torment of a Tremendous Day** — **[T]** 26:156 verbatim pairs the
   prohibition against harm with the consequence, and 26:189 names the day as "the day of the
   ˹deadly˺ cloud". The three verses are the sign's terms, breach, and penalty.
4. **The Interval Between Hamstringing and the Seizure** — **[Q]** the tradition reports three
   days. **Verify before drafting.** If unverifiable, replace with **[T]** 11:65–66 verbatim
   (the hamstringing and its immediate announcement) and drop the day-count claim.

#### 7:89 — The refusal to return (1,365w, 6 heads → +3)
1. **"Unless Allah Wills" as Prophetic Speech** — **[T]** 18:23–24 verbatim: the same
   qualification commanded to the Prophet ﷺ, which makes 7:89's use a fixed idiom of the
   prophets rather than a local hedge.
2. **Fabricating a Lie Against Allah: The Technical Term** — **[T]** 10:17, 11:18, 6:21,
   29:68 verbatim: the *iftarāʾ ʿalā Allāh kadhiban* formula, of which 7:89 is the prophets'
   own self-accusation in the counterfactual.
3. **The Prayer for Judgment** — **[T]** 34:26 verbatim and the sūrah's other appeals for
   verdict; *iftaḥ baynanā wa-bayna qawminā bi-l-ḥaqq* as a request for decision, not for
   destruction.

### 5.2 Dense sections (13–16 existing heads — narrow additions only)

| Section | Now | Heads | New | New heads proposed |
|---|---|---|---|---|
| **7:137** | 1,355w | 15 | 1 | **The East and the West as a Merism** — **[T]** the pair denotes the whole land, not two directions; supported by **[T]** 2:115 and 2:142 verbatim. |
| **7:146** | 1,349w | 13 | 1 | **Ṣarf and the Correspondence of Turning** — **[T]** 45:23 and 6:110 verbatim: the same turning described from the human side and the divine side. |
| **7:155** | 1,380w | 16 | 2 | **One Event, Two Accounts** — **[T]** 2:55–56 verbatim ("We will never believe you until we see Allah with our own eyes, so a thunderbolt struck you… Then We brought you back to life after your death") against 7:155's earthquake and plea; **The Thunderbolt Linked to 7:143** — **[T]** the request to see appears in both accounts, which is the strongest internal argument that the seventy and Moses's request are one episode. |
| **7:158** | 1,337w | 15 | 1 | **The Universal Address Tested by the Nearest Case** — **[T]** the verse's "to you all" against **[T]** 3:45–49 (ʿĪsā sent to the Children of Israel only): the sūrah states the exception that proves the rule. |
| **7:160** | 1,358w | 16 | 1 | **Twelve Springs for Twelve Tribes: The Arithmetic** — **[T]** the correspondence is exact, so no tribe lacked water and none shared another's; supported by **[T]** 2:60 verbatim. |
| **7:169** | 1,369w | 15 | 1 | **Suḥt: The Unlawful Gain as a Named Category** — **[T]** 5:42 and 5:62–63 verbatim, where the same gain is called *suḥt* and the scholars are blamed for not forbidding it. |
| **7:188** | 1,370w | 15 | 1 | **Ghayb Refused to the Prophets** — **[T]** 27:65 verbatim ("Say, ˹O Prophet,˺ None in the heavens or the earth knows the unseen except Allah") and 6:59: the refusal is universal, not personal. |
| **7:189** | 1,374w | 14 | 1 | **The Verse's Own Gloss at 7:190–191** — **[T]** verbatim: the prayer is answered, gratitude is given, then association follows. The next two verses are the section's missing conclusion. |
| **7:203** | 1,366w | 15 | 1 | **Baṣāʾir in the Plural** — **[T]** the plural of *baṣīrah* distinguishes insight from sight; compare **[T]** 6:104 and 10:108 verbatim where the same plural carries the same epistemic claim. |

---

## 6. Group C — Comparative verses

These sections scored Tier 1 on uncited candidate parallels; the new material is therefore
cross-verse chains quoted from `translation/`.

#### 7:56 — Corruption after repair (1,248w, 6 heads → +4)
1. **Corruption After Repair as a Legal Category** — **[T]** 7:56, 7:74, 7:85, 2:11–12
   verbatim: the phrase "after it has been set in order" recurs, which makes it a defined
   offence rather than a general rebuke.
2. **Khawf and Ṭamaʿ as a Fixed Pair** — **[T]** 7:56, 21:90, 32:16 verbatim: supplication
   with fear and hope appears three times in identical form.
3. **Mercy Is Near** — **[T]** 2:186 verbatim ("Indeed, I am near") — the same proximity
   asserted of the One supplicated.
4. **Iḥsān in Worship** — **[Q]** the Jibrīl definition of *iḥsān* (believed Bukhārī and
   Muslim, from ʿUmar). **Verify collection and number before drafting.** It matters because
   7:56 commands supplication *and* states that mercy is near to those who do good — the
   ḥadīth supplies the operative definition of the doer.

#### 7:75 — The elite and the lowly (1,376w, 5 heads → +3)
1. **Al-Malaʾ as the Sūrah's Antagonist Class** — **[T]** 7:60, 7:66, 7:75, 7:88, 7:90, 7:109,
   7:113, 7:127 verbatim: every occurrence in the sūrah, showing *al-malaʾ* is a technical
   term for the ruling assembly, used of Noah's, Hūd's, Ṣāliḥ's, Shuʿayb's and Moses's
   opponents alike.
2. **The Lowly as the Book's Constituency** — **[T]** 28:5 verbatim ("We wanted to favour
   those who were oppressed in the land") and **[T]** 7:75's own *alladhīna ustudʿifū*: the
   Qurʾān consistently assigns belief to the weak.
3. **"Are You Certain?" as a Weapon** — **[T]** 7:75 verbatim against **[T]** 26:186 and
   34:43: the elite's question is not epistemic but social, and the Qurʾān records it as
   such in three places.

#### 7:88 — The threat of expulsion (1,318w, 8 heads → +2)
1. **Expulsion as the Sūrah's Recurring Threat** — **[T]** 7:88, 7:11, 11:91, 14:13 verbatim:
   the same threat in four narratives, always the last argument of a losing case.
2. **Coercion Cannot Produce Faith** — **[T]** 2:256 verbatim ("There is no compulsion in
   faith") against 7:88's threat and 10:99: the verse's principle and its application.

#### 7:90 — The cost of following Shuʿayb (1,352w, 5 heads → +3)
1. **Khāsirūn Counted** — **[T]** the sūrah's occurrences of *khusr/khāsir* (7:9, 7:23, 7:53,
   7:90, 7:92, 7:149, 7:178) verbatim: the verdict-word is the sūrah's refrain, and 7:90 and
   7:92 turn it against those who coined it.
2. **Three Descriptions of One Destruction** — **[V]** 7:91's *rajfah*, 11:94's *ṣayḥah*,
   26:189's *ẓullah*; **[T]** 11:94 verbatim against **[T]** 26:189 verbatim. **[V]** Ibn
   Kathīr on 26:176: the companions of al-Aykah were the people of Madyan, "according to the
   most correct view"; others held two or three distinct nations. **[V]** The grammatical
   asymmetry: 11:94's plural *diyārihim* against 7:91's singular *dārihim*.
3. **Following a Prophet as Material Loss in a Trading Town** — **[T]** 7:90 with **[T]** 7:85
   and 7:88 verbatim: the town's objection is economic, which is why its own words are the
   sūrah's strongest statement of the case against it.

#### 7:92 — The erasure formula (1,358w, 8 heads → +2)
1. **Ka-an Lam Yaghnaw Fīhā, Counted** — **[T]** 10:24, 11:68, 11:95, 29:38 verbatim: the
   formula "as if they had never lived there" appears at each destruction, and the variations
   between the occurrences are themselves material.
2. **Jāthimīn: Prone and Lifeless** — **[T]** 11:67 and 11:94 verbatim, plus 29:37–38: the
   word's uses fix its sense as bodies left without motion.

#### 7:97 — The night's suddenness (1,365w, 5 heads → +3)
1. **Bāghat as the Sūrah's Pattern** — **[T]** 7:95, 7:97, 7:98, 7:99, 7:182, 7:187, 6:44
   verbatim: the sudden-seizure word counted across the sūrah, with **[T]** 6:44 as its
   doctrinal statement.
2. **Night as the Time of Exposure** — **[T]** 7:97 against **[T]** 17:78–79 and 6:60: night
   is elsewhere the time of protection and recitation, which sharpens the inversion here.
3. **Amān and the Four Questions** — **[T]** 7:97–99 as a set of four rhetorical questions
   with no answer supplied; the structure itself is the argument, and **[T]** 7:182–183
   completes the set.

#### 7:98 — The daytime's play (1,281w, 7 heads → +2)
1. **Play as the Marker of Prosperity** — **[T]** 7:51, 29:64, 57:20 verbatim: *laʿib* is the
   Qurʾān's word for a life taken as entertainment, and 7:98 is its sharpest use.
2. **Day and Night as the Two Halves of One Warning** — **[T]** 7:97 and 7:98 verbatim side by
   side: the pair covers every hour, so no time remains in which security is safe.

#### 7:99 — The plan of Allah (1,338w, 7 heads → +2)
1. **Makr Allāh** — **[T]** 3:54 verbatim ("They planned, and Allah planned. And Allah is the
   best of planners") and **[T]** 8:30, 13:42: the term's three uses fix its sense as
   counter-planning, not deception.
2. **Only the Losers Feel Secure** — **[T]** 12:87 verbatim ("no one despairs of Allah's
   mercy except the disbelieving people") and **[T]** 15:56: the Qurʾān's parallel
   identification of despair and security as the two errors.

#### 7:128 — The earth belongs to Allah (1,371w, 14 heads → +1)
1. **"Seek Help in Allah and Be Patient" as Instruction** — **[T]** 2:153 verbatim ("seek help
   through patience and prayer") and **[T]** 2:45: the same instruction in imperative form,
   which 7:128 gives in narrative form. The existing heads cover the doctrine; this head
   covers the instruction's form and its two Qurʾānic parallels.

---

## 7. The blocking issue: all 43 sections are already inside the ceiling

This is the finding that governs everything above, and it needs a decision before drafting.

### 7.1 The numbers

| Measure | Value |
|---|---|
| Tier-1 sections | 43 |
| Current word counts | **1,248 – 1,385** (band: 1,200–1,400) |
| Existing heads | 426 total; **18 sections at 13–16 heads**, 25 sections at 4–8 heads |
| New heads proposed above | **125** (avg 2.9 per section) |
| Cost at ~90 words per head | **+11,250 words** |
| Projected word counts | **1,427 – 2,008** |
| Sections projected over the 1,400 ceiling | **43 of 43** |

Deepest projections: 7:143 → 2,008; 7:46 → 2,005; 7:85 → 1,824; 7:54 → 1,819; 7:73 → 1,745;
7:157 → 1,738; 7:37 → 1,732; 7:32 → 1,731; 7:22 → 1,715.

**So the plan as written cannot be executed inside the current band.** Every Tier-1 section is
already at 1,248–1,385 words; the ceiling is 1,400. Adding two heads breaks it almost
everywhere; adding four or seven breaks it badly.

### 7.2 Why the estimator said there was headroom

The headroom estimator ranked by verse surface, content units, legal markers and uncited
parallels. All four measure **material available**, not **space remaining**. The 18 dense
sections prove the point: 7:155, 7:160, 7:143, 7:172, 7:176, 7:187 already carry 15–16 heads
each and sit at 1,300–1,380 words. Their Tier-1 score came from verse surface, not from
unconsumed content. The real deficit is concentrated in the **25 sections with 4–8 heads**.

### 7.3 Four options

**Option A — Raise the ceiling for Tier 1 (no content removed).**
New band for the 43 sections: 1,400–1,800, with a documented higher cap (2,100) for the four
deepest (7:143, 7:46, 7:85, 7:54). All 125 heads fit. File grows 269,247 → ~280,500 words.
The 163 Tier-2/3 sections stay on the existing 1,200–1,400 band, so the ceiling becomes
tier-relative rather than global — which the repo would need to record in `validate.py`
and the exception list.
*Cost: a two-tier band is a new convention. Benefit: nothing existing is cut, and the
research above is all used.*

**Option B — Keep the band, trim to fit.**
Add the 125 heads and remove ~11,250 words of the weakest existing prose (~260 words, i.e.
roughly three existing heads, per section).
*This violates the standing finding "No existing commentary cut for depth", which would need
to be explicitly reversed. Not recommended unless you want the band held at all costs.*

**Option C — Expand only the 25 thin sections, raise their cap only.**
Give the 25 sections with 4–8 heads their 3–4 new heads each (88 heads, ~7,900 words, cap
1,800) and give the 18 dense sections **zero** new heads, on the grounds that 13–16 heads is
already thorough coverage.
*Cost: forfeits the strongest researched material — 7:143's ruʾyah debate, 7:54's istawā and
khalq/amr, 7:157's iṣr/aghlāl, 7:176's three candidates, 7:172's kalām question all sit in
dense sections. Benefit: smallest change, and no restatement risk.*

**Option D — No expansion; the band is already met.**
Accept that the 43 Tier-1 sections are at the top of the band with 426 heads between them,
and that "headroom" measured available material rather than missing argument. Keep the file
as-is; record this plan as the survey of what a future raised ceiling would use.
*Cost: the researched material above is unused. Benefit: nothing to break; the file is already
gate-clean.*

**Recommendation: Option A**, with the two-tier band recorded explicitly, and with two
adjustments — (i) the 18 dense sections get only the 21 heads listed for them (all genuinely
new angles, each tied to a named source or a counted cross-verse chain), and (ii) the four
deepest sections get the higher 2,100 cap. Under that adjustment the total is 125 heads,
+11,250 words, and no existing prose is removed.

### 7.4 Verification queue (must clear before drafting)

These are the **[Q]** heads. Each must be verified live; if verification fails, the head is
dropped, never softened.

| # | Item | Believed source | Feeds |
|---|---|---|---|
| 1 | *man ghashshanā falaysa minnā* | Ṣaḥīḥ Muslim, Abū Hurayrah | 7:85 |
| 2 | "eat, drink, wear, give charity without extravagance or pride" | Aḥmad / Ibn Mājah, ʿAmr b. Shuʿayb | 7:31 |
| 3 | "None is more jealous than Allah…" | Aḥmad from Ibn Masʿūd; two Ṣaḥīḥs | 7:33 |
| 4 | The tajallī / fingertip report | tafsīr tradition | 7:143 |
| 5 | Abū Dharr's Miʿrāj light report | Ṣaḥīḥ Muslim | 7:143 |
| 6 | *innakum satarauna Rabbakum* | Bukhārī / Muslim | 7:143 |
| 7 | The scales / atom's-weight and "last to enter" reports | tafsīr tradition | 7:46 |
| 8 | *al-arwāḥ junūdun mujannadah* | Ṣaḥīḥ Muslim | 7:172 |
| 9 | The Torah's description of the Prophet (ʿAṭāʾ b. Yasār) | Ibn Kathīr / Ṭabarī | 7:157 |
| 10 | The three-day interval at Thamūd | tafsīr tradition | 7:73 |
| 11 | The Jibrīl definition of *iḥsān* | Bukhārī / Muslim, ʿUmar | 7:56 |

**Already verified this session [V] — safe to draft now:** the istidrāj ḥadīth of ʿUqbah b.
ʿĀmir (Musnad Aḥmad 17311, ḥasan per al-Arnaʾūṭ); Ibn Kathīr on 26:176 (Madyan = Aykah) and
the *diyārihim/dārihim* asymmetry; the ten identifications of the *aʿrāf* with their
authorities and al-Ālūsī's adjudication; al-Qurṭubī's three premises on *ruʾyah* and
al-Suyūṭī/al-Jalālayn's capability reading; Mālik's *istawā* statement, al-Māzharī's
*khalq/amr* division and the delegation point (Maʿārif al-Qurʾān); *iṣr* and *aghlāl* defined
and the cut-the-cloth example; *ummī* and the Arabs as *ummiyyūn*; the three candidates for
the parable's man with their chains, Mawdūdī's caution, al-Bāqir's generalisation and the two
readings of the dog; *kayl/mīzān/bakhs/taṭfīf*; Ibn Kathīr's *ithm/baghy* synthesis with
as-Suddī and Mujāhid; the *aʿrāf*-is-not-purgatory distinction and the 7:47 speaker dispute.

**Also verified from the repo itself [T]:** the throne-establishment formula occurs at 7:54,
10:3, 13:2, 20:5, 25:59, 32:4, 57:4 — seven verses, count taken directly from `translation/`.

### 7.5 Proposed work order (once an option is chosen)

1. Clear the **[Q]** verification queue (11 items) — nothing drafted until each is checked.
2. Group D first, deepest sites: 7:143, 7:46, 7:54, 7:157, 7:176, 7:178, 7:172, 7:187.
3. Group B: 7:85, 7:31, 7:33, 7:32, 7:28, 7:156, 7:148.
4. Group C: 7:90, 7:92, 7:56, 7:75, 7:97, 7:98, 7:99, 7:88, 7:128.
5. Group A thin sections: 7:22, 7:27, 7:37, 7:38, 7:43, 7:44, 7:53, 7:69, 7:73, 7:89.
6. Group A dense sections: the 21 single-head additions.
7. Structural decisions 2.1 and 2.2 (7:78/7:91 promotion; 7:175 promotion).
8. Full gate run after each tranche: `check_filler.py`, `check_cross_quotes.py`, `validate.py`,
   `census.py` — with the band check updated if Option A is chosen.
9. Commit per tranche to `arena/01a094c2-new`; PR #89 already open.

---

## 8. Decision record (approved)

Three decisions taken; they supersede §7.3's open options and §2's open findings.

### 8.1 Ceiling — Option A: the band becomes tier-relative

| Section class | Count | Band |
|---|---|---|
| Tier 1, standard | 43 (now 46 with the promotions below) | **1,400 – 1,800 words** |
| Tier 1, deepest — 7:143, 7:46, 7:85, 7:54 | 4 | **up to 2,100 words** |
| Tier 2 / Tier 3 / borderline | 163 | **1,200 – 1,400 words** (unchanged) |
| Reduced-floor exceptions | 20 → **18** | **700 words** (unchanged, minus 7:78 and 7:91) |

Consequences to implement:
- **No existing commentary is cut.** The "no content removed for depth" finding stands.
- `validate.py` and the census/band check must record the tier-relative band, with the 46
  Tier-1 verses listed explicitly rather than by a threshold rule, so the exception is
  auditable and cannot drift.
- The 25 thin sections absorb most of the increase; the 18 dense sections absorb their
  21 single-head additions only.
- Projected file size: 269,247 → ~280,500 words.

### 8.2 Dense sections — all 21 additions approved

The single-head additions for the 18 sections with 13–16 existing heads are approved as
listed in §5.2 and §6, including the pure cross-verse-chain heads (7:137 merism, 7:146 ṣarf,
7:158 universal address, 7:160 arithmetic, 7:188 ghayb, 7:203 baṣāʾir, 7:128 instruction
form). Each remains bound to a named source or a counted cross-verse chain quoted verbatim
from `translation/`.

### 8.3 Structure — both promotions approved

- **7:78 and 7:91 leave the reduced-floor exception list** and move to the full Tier-1 band
  (1,400–1,800). Each gains ~3 heads carrying the destruction harmonisation:
  - **[V]** *rajfah* (7:91, 11:94's *ṣayḥah*) and *ẓullah* (26:189) as three descriptions of
    one event, per Ibn Kathīr on 26:176 — Madyan *is* al-Aykah, "according to the most
    correct view"; the minority view of two or three nations recorded against it.
  - **[V]** the *diyārihim* / *dārihim* asymmetry between 11:94 and 7:91.
  - **[T]** 26:189 verbatim ("overtaken by the torment of the day of the ˹deadly˺ cloud")
    and 11:94 verbatim, set against 7:78 and 7:91 for the Thamūd and Madyan parallel.
  - **[V]** *jāthimīn* as prone and lifeless.
  - The exception list drops from 20 entries to 18; §7.1's totals shift accordingly
    (46 Tier-1 sections, ~134 new heads, ~+12,000 words).
- **7:175 is promoted from Tier 3 to Tier 1** and receives ~3 heads:
  - **[V]** the three candidates for the man's identity with their chains (§4.6 head 1),
    housed here rather than in 7:176 so that 7:176 keeps its 15 heads on the parable itself.
  - **[V]** Mawdūdī's caution that the identity is not established by Qurʾān or ḥadīth.
  - **[T]** 7:175 verbatim as the narrative setup whose singular subject 7:176 then makes
    plural.

### 8.4 Revised totals

| | Before decisions | After decisions |
|---|---|---|
| Sections in scope | 43 | **46** |
| Reduced-floor exceptions | 20 | **18** |
| New heads | 125 | **~134** |
| Words added | +11,250 | **~+12,000** |
| Sections over their (new) ceiling | 43 of 43 | **0 of 46** |

### 8.5 Execution order (unchanged from §7.5, with two insertions)

1. Clear the 11-item **[Q]** verification queue — in progress.
2. Group D (deepest doctrine): 7:143, 7:46, 7:54, 7:157, 7:176, 7:178, 7:172, 7:187.
3. Group B (rulings): 7:85, 7:31, 7:33, 7:32, 7:28, 7:156, 7:148.
4. **New: the promoted destruction pair 7:78 and 7:91**, plus **7:175**.
5. Group C (comparative): 7:90, 7:92, 7:56, 7:75, 7:97, 7:98, 7:99, 7:88, 7:128.
6. Group A thin: 7:22, 7:27, 7:37, 7:38, 7:43, 7:44, 7:53, 7:69, 7:73, 7:89.
7. Group A dense: the 21 single-head additions.
8. Update `validate.py` for the tier-relative band; refresh the 18-entry exception list.
9. Full gate run per tranche: `check_filler.py`, `check_cross_quotes.py`, `validate.py`,
   `census.py`. Commit per tranche to `arena/01a094c2-new`; PR #89 open.

---

## 9. Verification queue — cleared

All eleven **[Q]** items checked live. Six now carry collection and number; five resolve to
named classical sources, which is the correct attribution for exegetical reports (a report
transmitted by an exegete is cited to the exegete, not given a ḥadīth number it does not
have).

| # | Item | Result | Cite as |
|---|---|---|---|
| 1 | *man ghashshanā falaysa minnā* | **Verified** | Sunan Ibn Mājah 2225, from Abū Ḥamrāʾ: "I saw the Messenger of Allah ﷺ pass by a man having food in a vessel. He put his hand in it and said: 'Perhaps you are cheating. Whoever cheats us is not one of us.'" The grain-heap incident (wet grain under dry, "Why did you not place the drenched part over the corn so that people might see it?") is in Ṣaḥīḥ Muslim, content verified via Riyāḍ aṣ-Ṣāliḥīn 1579 and IslamQA; number not held, so cite Ibn Mājah 2225 for the wording and describe the Muslim incident without a number. → **7:85** |
| 2 | "eat, drink, wear, give charity without extravagance or pride" | **Verified, ḥasan** | Sunan Ibn Mājah 3600 and 3605, from ʿAmr b. Shuʿayb from his father from his grandfather (ʿAbdullāh b. ʿAmr): "Eat and drink, give charity and wear clothes, as long as that does not involve any extravagance or vanity." Also al-Bukhārī as *muʿallaq* in decisive form, and Aḥmad. The source itself ties it to the verse: "The Hadith corresponds to the verse where Allah says {Eat and drink and be not extravagant} [Sūrat al-Aʿrāf: 31]", and glosses *isrāf* as "exceeding the limit in every act or saying", paired with a command "to avoid ostentation and seeking fame". This confirms the excess-in-amount / excess-in-motive split the head needs. → **7:31** |
| 3 | "None is more jealous than Allah…" | **Verified** | Ṣaḥīḥ Muslim 1499a, al-Mughīrah b. Shuʿbah reporting Saʿd b. ʿUbādah: "Are you surprised at Saʿd's jealousy of his honour? By Allah, I am more jealous of my honour than he, and Allah is more jealous than I. Because of His jealousy Allah has prohibited abomination, both open and secret…" — the Arabic carries *al-fawāḥish mā ẓahara minhā wa-mā baṭan*, the exact phrase of 7:33, so the ḥadīth gives the verse's own wording its reason. Continues: "no person is more fond of accepting an excuse than Allah, on account of which He has sent messengers, announcers of glad tidings and warners; and no one is more fond of praise than Allah, on account of which Allah has promised Paradise." Ibn Kathīr's note that this was "recorded in the Two Ṣaḥīḥs" is consistent. → **7:33** |
| 4 | The tajallī / fingertip report | **Not numbered** | Attribute to the exegetical tradition on 7:143 (al-Qurṭubī, Ibn Kathīr), never as a graded ḥadīth with a number. The head may proceed on that footing, or be dropped in favour of the two verified sight reports below. → **7:143** |
| 5 | Abū Dharr's Miʿrāj light report | **Verified, two variants** | Ṣaḥīḥ Muslim 178a: "I asked the Messenger of Allah ﷺ: Did you see thy Lord? He said: (He is) Light; how could I see Him?" Ṣaḥīḥ Muslim 178b, ʿAbdullāh b. Shaqīq from Abū Dharr: "I, in fact, inquired of him, and he replied: I saw Light." Both sit in the Book of Faith, chapter 78, titled "The saying of the Prophet: 'Light, How could I see Him?' and: 'I saw Light'". → **7:143** |
| 6 | *innakum satarauna Rabbakum* | **Verified** | Ṣaḥīḥ al-Bukhārī 7436 (7434 in some editions), Book of the Oneness and Uniqueness of Allah, from Jarīr b. ʿAbdullāh: "Allah's Messenger ﷺ came out to us on the night of the full moon and said, 'You will see your Lord on the Day of Resurrection as you see this (full moon) and you will have no difficulty in seeing Him.'" → **7:143** |
| 7 | The scales / atom's-weight and "last to enter" reports | **Not numbered** | Attribute to Ibn ʿAbbās and Ḥudhayfah as transmitted by al-Qurṭubī and al-Ālūsī on 7:46. Do not give a ḥadīth number. → **7:46** |
| 8 | *al-arwāḥ junūdun mujannadah* | **Verified by collection, book and chapter** | Ṣaḥīḥ al-Bukhārī, Kitāb Aḥādīth al-Anbiyāʾ, chapter *al-Arwāḥ junūd mujannadah*. Number not held — cite collection, book and chapter. **Important qualifier, also verified:** an-Nawawī explains the phrase as "groups gathered together, or different types", i.e. it concerns affinity and opposition among spirits, not a dated pre-earthly assembly. The head must therefore present it as bearing on *affinity*, not as proof of the covenant's location. → **7:172** |
| 9 | The Torah's description of the Prophet | **Not numbered** | Attribute to the exegetical tradition via Ibn Kathīr and al-Ṭabarī (ʿAṭāʾ b. Yasār's transmission). If the chain is not stated in the source, the head reduces to **[T]** 48:29 and 3:159. → **7:157** |
| 10 | The three-day interval at Thamūd | **Not numbered** | Attribute to the exegetical tradition; if no named exegete carries it, replace with **[T]** 11:65–66 verbatim and drop the day-count. → **7:73** |
| 11 | The Jibrīl definition of *iḥsān* | **Verified** | Ṣaḥīḥ Muslim 8 (variants 8b, 8c, 8d) and Ṣaḥīḥ al-Bukhārī 50, both in the Book of Faith, from ʿUmar b. al-Khaṭṭāb: "It is to worship Allah as if you can see Him, for although you cannot see Him, He can see you." → **7:56** |

**Net effect:** items 1, 2, 3, 5, 6, 11 are citable with collection and number. Items 4, 7, 9,
10 are citable only as reports attributed to named exegetes — which is how the plan already
describes them. Item 8 is citable by collection, book and chapter, with an-Nawawī's qualifier
mandatory. No head in the plan depends on an unverified number.

**Added to the verified [V] pool this session:** Muslim 1499a's use of 7:33's exact phrase,
which is a stronger link than the plan assumed — the ḥadīth does not merely parallel the
verse, it quotes it.

---

## 10. Implementation log

Running record of what has been drafted, and of corrections to the plan above where the
survey proved wrong on inspection. This section supersedes the earlier ones where they
conflict.

### 10.1 Tranche 18 — 7:143 and 7:46 (committed `3159d3f`)

Both deepest sites expanded to the 2,100 cap. 7:143 → 2,100w with seven heads; 7:46 → 2,086w
with seven heads. Gates: cross-quotes 1,734 EXACT / 0 DRIFT / 0 ELLIPSIS / 0 VICINITY (five
new Qur'anic spans, all exact); validate 114/114; tics 0.19/1k, chains 0.12/1k, dup 0.062 —
all unchanged, so the additions introduced no filler.

`check_filler.py` gained the tier-relative ceiling in the same commit: `TIER1_CEILING` 1,800
and `DEEPEST_CEILING` 2,100 over an explicit 46-verse list, with a comment recording where
the list came from. The band floor stays at 1,200 during the expansion and is raised to
1,400 for Tier 1 once all 46 sections are drafted, so the gate never fails on sections whose
tranche has not landed yet.

### 10.2 Tranche 19 — the three promotions (7:78, 7:91, 7:175)

7:78 → 1,503w with six heads: rajfah against ṣayḥah across 11:67, 54:31 and 69:5; the
sentence shared with Madyan, which is word-identical apart from one comma; *jāthimīn* and its
five occurrences, all with the same phrase for the place; 54:31's twigs of fence-builders as
the only description of the aftermath's appearance; 69:4–5's Striking Disaster as the thing
denied rather than the thing that arrived; and 29:37–38's ruins addressed to the Meccans.

7:91 → 1,502w with six heads: the three descriptions harmonised with Ibn Kathīr on 26:176;
the omission of "their brother" at 26:176–177 against 29:36, 7:85 and 11:84, with Ibn
Kathīr's reason; *diyārihim* against *dārihim*, flagged as an inference from grammar rather
than a report; the shared sentence with Thamūd; 26:157's regret preceding the punishment; and
7:92's erasure closing the account.

7:175 → 1,538w with one head: the three candidates and their transmitters, with al-Bāqir's
generalisation and Mawdūdī's caution as the two poles of the tradition's handling.

Gates after tranche 19: **cross-quotes 1,743 EXACT / 0 DRIFT / 0 ELLIPSIS / 0 VICINITY**
(nine new Qur'anic spans, all exact); **validate 114/114**; **check_filler FAILING 0** —
below band 0, above band 0, reduced-floor 18, tics 0.19/1k, chains 0.12/1k, dup 0.062,
repeated sentences 0. File: 273,242 words.

### 10.3 Corrections to the plan, found on inspection

The survey mis-scored two sections. Both are recorded here rather than silently fixed,
because they change what remains to be drafted.

1. **7:175 already carried 15 sub-heads at 1,346 words**, not a Tier-3 gap. Two of the three
   heads proposed for it in §8.3 were therefore duplicates and have been **struck**:
   - the *insilākh* head — the section already has "The Word for Stripping Out", which
     defines the root *s-l-kh* as taking a skin off an animal or a husk off a seed and draws
     an exact grammatical parallel with 36:37;
   - the singular-to-plural head — already covered by "The Man's Example and the Next Verse".
   Only the identity survey was genuinely new, and it was new because the existing head
   "The Commentators' Identification" names Balʿam alone, without transmitters.
2. **§4.6 heads 1 and 2 for 7:176 are struck.** The three candidates and Mawdūdī's caution
   are now in 7:175, where the narrative setup belongs. 7:176 keeps two new heads: the two
   readings of the dog (literal tongue against general misguidance) and the parable's
   placement in the verse's own argument, which turns the singular case plural in the words
   *famsal al-qawm alladhīna kadhdhabū bi-āyātinā*.

**Lesson carried into the remaining tranches:** the head count in `/tmp/heads_t1.json` was
extracted correctly, but Tier-3 sections were never head-surveyed, so any promotion of a
Tier-3 section must be preceded by a head extraction. Two sections were promoted; one of them
(7:175) turned out to be dense. Before drafting 7:54, 7:157, 7:172, 7:176, 7:187 and the rest
of Group D, their existing heads must be read in full, not just counted — several already
carry material the plan assumed was absent.

### 10.4 Remaining work

| Group | Sections | Heads outstanding |
|---|---|---|
| D | 7:54 (5), 7:157 (4), 7:172 (3), 7:176 (2, revised), 7:178 (3), 7:187 (2) | 19 |
| B | 7:85 (5), 7:31 (4), 7:33 (4), 7:32 (4), 7:28 (3), 7:156 (3), 7:148 (2) | 25 |
| C | 7:56 (4), 7:75 (3), 7:90 (3), 7:97 (3), 7:92 (2), 7:88 (2), 7:98 (2), 7:99 (2), 7:128 (1) | 22 |
| A thin | 7:37 (4), 7:73 (4), 7:22 (4), 7:27 (3), 7:38 (3), 7:43 (3), 7:44 (3), 7:53 (3), 7:69 (3), 7:89 (3) | 33 |
| A dense | 7:155 (2), 7:137, 7:146, 7:158, 7:160, 7:169, 7:188, 7:189, 7:203 (1 each) | 10 |
| Final | raise the Tier-1 band floor from 1,200 to 1,400 in `check_filler.py` | — |

109 heads outstanding across 41 sections, roughly +9,800 words. Each tranche runs the four
gates and commits separately.
