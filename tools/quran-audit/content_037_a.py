# -*- coding: utf-8 -*-
"""037.md batch A: rebuild the 7 sections whose bodies described a DIFFERENT verse.

Verified defect (read directly, not inferred from a metric):
  v62  body was about 'man ʿaṣaynā al-rasūl'  = 33:66-67 content, not Zaqqūm
  v182 body was about 'We have preferred some of them over others' = 2:253 content
  v50 / v61 / v66 / v85 / v87 bodies likewise quoted other verses' Arabic.

Cause: vv 57-177 were 21,326 words of unheaded content that normalize.py promoted
into verse headings. 119 translations were later corrected, but the bodies were
never realigned, leaving section text describing the wrong verse.

Rebuilt from initial/037.md's apparatus, in 037.md's own template shape.
The Cross-Reference / Classical View lines are PARAGRAPHS inside the final
mini-heading block (apply_sections.py wraps a tuple's first element in **...**),
so they render as `> **...**` blockquote lines.
No hadith is asserted unless the apparatus supplies one.
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

50: (None, [
 ("Turning to One Another, Questioning", [
  "The scene shifts to the Garden, where its inhabitants converse. The commentators explain that the inhabitants of the Garden ask one another about their state in the world (IJ). The questioning is therefore retrospective: it looks back at the life that has ended rather than forward.",
  "The commentators record two readings of who the companion is. A companion refers to the satan assigned to each person, directing the reader to 43:36 (IJ, Ṭ). Or it refers to a believer's companion who denied the Resurrection and would ask the believer in astonishment, \"Are you among those who confirm the Resurrection?\" (IJ, IK, Ṭ). The two readings differ on whether the questioner is an assigned satan or a human acquaintance."]),
 ("The Question and the Mockery", [
  "The commentators note that the first part of v. 53 reflects a question posed in several Qur'anic verses, listing 13:5, 17:49 and 17:98, 23:35 and 23:82–83, 27:67, 36:78–79, 37:16–17, 50:3, 56:47–48, and 79:11, while the second part of v. 53 mocks the belief in a final reckoning.",
  "The recurrence matters. The objection to bodily resurrection is not a local feature of this passage but a standing objection across the Qur'an, and the commentators' list shows how often it returns. The mocking tone in the second half is what distinguishes the question from sincere inquiry."]),
 ("Seeing Across the Divide", [
  "The commentators describe the mechanism: when they have died, and the believer goes to the Garden and the idolater goes to the Fire, the believer sees the state of the disbeliever (Ṭ), and according to 7:46–50, the disbelievers in Hell can see the believers in Paradise.",
  "The visibility runs in both directions, and the commentators cite 7:46–50 for the second direction. What makes the conversation possible is not proximity but the removal of the barrier that separated them in the world."]),
 ("The Two Companions of al-Kahf", [
  "The commentators offer an identification: thus some say this passage refers to the two companions discussed in 18:32–43 (IJ). The attribution is to some rather than to all, and the commentators preserve it without endorsing it.",
  "The reading connects this passage to the parable of the two gardens, where one companion boasted of wealth and the other warned him. The identification is offered because the pattern of two companions with opposite ends fits, not because the text names them.",
  "> **Cross-Reference:** 43:36 — the satan assigned to each person; 7:46–50 — the two groups seeing one another across the barrier.",
  "> **Classical View (IJ, IK, Ṭ):** the companion is either the satan appointed to a person or a human acquaintance who denied the Resurrection and now asks in astonishment whether the believer was among those who affirmed it."]),
]),

61: (None, [
 ("For the Like of This Let the Laborers Labor", [
  "The verse is an invitation rather than a description. The commentators state its message: it is to let those in this world perform righteous deeds, so that they too may attain the honor that God has bestowed upon these believers in the Hereafter (Ṭ).",
  "The reading makes the verse hortatory. What has been described in the preceding verses is not merely reported but held up as something worth working toward, and the commentators identify the labor as righteous deeds performed in this world."]),
 ("Whose Words Are These", [
  "The commentators record a disagreement about the speaker. This verse can be understood as the words of God (Z) or as the words of the believers in the Garden.",
  "The two readings change the register. As God's words the verse is a command addressed to the living; as the believers' words it is an exclamation of delight addressed to one another. The commentators preserve both without preferring either, and the verse's wording does not mark a speaker."]),
 ("Labor and Its Object", [
  "The word laborers is what carries the exhortation. The commentators do not gloss the term, but their reading supplies its content: the labor is the performance of righteous deeds, and its object is the honor bestowed upon the believers described in the surrounding verses.",
  "The connection between labor and honor is what makes the verse an argument rather than a slogan. The honor is shown first, in the description of the Garden, and the invitation follows from it. The commentators' note that the labor is to be performed in this world fixes the time in which the invitation can be accepted."]),
 ("The Verse in the Sequence", [
  "The verse closes the description of the Garden's rewards and turns toward the disbelievers' provision at vv. 62–68. The commentators do not gloss the transition, but the structure supplies it: the invitation is followed by its opposite.",
  "The commentators note at vv. 62–63 that in contrast to the fruits bestowed upon the believers as a known provision in the Garden (vv. 41–42), the disbelievers are given the tree of Zaqqūm. The labor invited here is therefore set against the outcome avoided there.",
  "> **Cross-Reference:** vv. 41–42 — the known provision of the Garden, against which the invitation is framed.",
  "> **Classical View (Ṭ / Z):** the verse exhorts those in this world to righteous deeds so that they may attain the same honor; it may be read either as the speech of God or as that of the believers in the Garden."]),
]),

62: (None, [
 ("The Better Welcome, and Zaqqūm", [
  "The verse poses a comparison. The commentators explain that in contrast to the fruits bestowed upon the believers as a known provision in the Garden (vv. 41–42), the disbelievers are given the tree of Zaqqūm, which is said to bear pain and sorrow (Z).",
  "The commentators identify what the tree bears: pain and sorrow. The description is not of a fruit but of an affliction, and the commentators attribute the reading to Z."]),
 ("Why a Question", [
  "The commentators explain the rhetorical form. As it is known that there is no good in Zaqqūm, the rhetorical question is posed here as a rebuke to the disbelievers for the course they have chosen (Z).",
  "The question is therefore not genuinely open. Its answer is already settled, and its function is to make the disbelievers' choice visible to them. The commentators read it as a rebuke rather than as an inquiry, and they ground that reading in the absence of any good in the tree."]),
 ("Its Effects", [
  "The commentators supply the description from elsewhere in the Qur'an. Its effects are best described in 44:43–46: Truly the tree of Zaqqūm is the food of the sinner, like molten lead boiling in their bellies, like the boiling of boiling liquid. They add 56:51–53 as a further parallel.",
  "The cross-reference is offered as the fullest account, and the commentators direct the reader to the commentary on 44:43–46. What this verse supplies is the comparison; what 44:43–46 supplies is the sensation."]),
 ("A Trial", [
  "The commentators explain the term used at v. 63: that Zaqqūm is a trial (*fitnah*) means that eating from it is a punishment in the Hereafter (IJ, Z).",
  "The gloss fixes the sense of trial. It is not a test whose outcome is unknown but a punishment already determined, and the commentators attribute the reading to both IJ and Z. The word therefore names the character of the eating rather than its uncertainty.",
  "> **Cross-Reference:** 44:43–46 — the fullest description of Zaqqūm's effects; 56:51–53; vv. 41–42 — the believers' known provision, set in contrast.",
  "> **Classical View (Z / IJ):** Zaqqūm bears pain and sorrow; the question is a rebuke, since no good is in it; and its being a *fitnah* means the eating of it is itself the punishment."]),
]),

66: (None, [
 ("Eating and Filling the Belly", [
  "The verse describes the eating. The commentators explain that the disbelievers eat thereof because they are commanded to do so, citing 56:53, and that they fill their bellies either because of severe hunger or because they are forced to eat it even though they despise it (Z).",
  "The two readings differ on the motive. One makes the eating a consequence of hunger, the other of compulsion despite revulsion. The commentators preserve both and note what they share."]),
 ("What Both Readings Imply", [
  "The commentators draw a common implication: both interpretations allude to the fact that their own avaricious natures have forced them to continue to eat from Zaqqūm.",
  "The reading makes the compulsion internal rather than external. Whether the cause is hunger or force, the commentators locate the driver in the eaters' own nature. The eating is therefore continuous, and the commentators' phrase continue to eat is what marks it."]),
 ("Satiety and Thirst", [
  "The commentators describe what follows. But if they are satiated, then thirst overwhelms them, and they are given a drink that burns their faces and tears apart their intestines (Z).",
  "The sequence closes the possibility of relief. The filling of the belly named in the verse does not end the affliction but produces the next one, and the commentators attribute the account to Z."]),
 ("The Boiling Liquid and Its Contrast", [
  "The commentators set the drink against the Garden's provision. The brew of a boiling liquid — citing 6:70, 10:4, 18:29, 38:57, 44:46, 47:15, 78:24–25, and 88:5 — that the disbelievers are made to drink stands in sharp contrast to the cool and pleasing drinks presented to the believers in the Garden, citing 37:45–47, 76:5–6, 76:17–18, 76:21, and 83:25–28, and to the rivers of water, milk, honey, and wine described in 47:15.",
  "The contrast is drawn within the sūrah as well as across it. Verses 45–47 of this sūrah describe the believers' drink, and the commentators place the boiling liquid directly against it.",
  "> **Cross-Reference:** 56:53 — the command to eat; 37:45–47 — the believers' drink in this same sūrah; 47:15 — the rivers of the Garden.",
  "> **Classical View (Z):** they eat because they are commanded, filling their bellies from severe hunger or under compulsion despite despising it; both readings show their own avarice driving them on, and satiety brings a thirst answered by a drink that burns the face and tears the intestines."]),
]),

85: (None, [
 ("Abraham's Question to His People", [
  "The verse opens Abraham's dispute. The commentators place it in a wider pattern: this is one of several passages in which Abraham argues with his people regarding the inanity of their idolatry, citing 2:258, 6:83, and 21:51–67.",
  "The question asked is not rhetorical in the ordinary sense. It asks what they worship, and the commentators treat the passage as an argument rather than as a narrative interlude."]),
 ("Why Abraham Here", [
  "The commentators record an observation about the passage's placement. As al-Rāzī observes, the Qur'an invokes the story of Abraham in the context of the Prophet Muhammad's disputations with the idolaters, because even the idolatrous Arabs had great respect for Abraham as one of their most prominent forefathers.",
  "The observation explains the choice of exemplar. The argument is addressed to an audience that already honors Abraham, and the commentators direct the reader to 43:26–27 for the same point. The appeal to a shared forefather is what gives the disputation its force."]),
 ("The Form of the Question", [
  "The verse reports the question without reporting the answer, which follows at vv. 86–87. The commentators note at v. 86 that the subtle grammatical structure of that verse allows several readings, all of which express rebuke and amazement.",
  "The sequence is therefore a progression from inquiry to rebuke. Abraham asks what they worship, and the reply he draws out is met with amazement. The commentators do not gloss v. 85's question beyond placing it in the pattern of Abraham's disputations."]),
 ("The Disputation and Its Aim", [
  "The commentators describe the subject of the argument as the inanity of idolatry. The word is theirs, and it characterizes what Abraham is demonstrating rather than what he is asserting.",
  "The cross-references at 2:258, 6:83, and 21:51–67 show the same argument conducted elsewhere, and the commentators cite them as parallels rather than as sources. The passage here is one instance of a recurring form.",
  "> **Cross-Reference:** 2:258, 6:83, 21:51–67 — Abraham's disputations elsewhere; 43:26–27 — the idolaters' respect for their forefathers.",
  "> **Classical View (al-Rāzī):** the Qur'an sets Abraham's argument in the context of the Prophet's own disputations because the idolatrous Arabs held Abraham in great respect as one of their most prominent forefathers."]),
]),

87: (None, [
 ("What Do You Think of the Lord of the Worlds", [
  "The verse is the second question in Abraham's exchange. The commentators record two readings of what it asks, and the difference between them is substantial.",
  "The first reading takes it as a challenge about God's nature: this verse may mean, \"Do you think that God would permit inanimate objects to share in the worship that is His due alone, or do you think that He is of their same genus, such that you should make them equal in worship?\" (R)."]),
 ("The Second Reading", [
  "The commentators give an alternative: it could also be understood to mean, \"What, then, do you think God will do with you when you meet Him, while you have been worshipping other gods?\" (IK, Ṭ).",
  "The two readings differ in direction. The first concerns what God is and whether inanimate objects can be His equals; the second concerns what God will do to those who have worshipped them. The commentators preserve both, attributing the first to R and the second to IK and Ṭ."]),
 ("The Question as Argument", [
  "The commentators place the verse in the same pattern as v. 85: this is one of several passages in which Abraham argues with his people regarding the inanity of their idolatry, citing 2:258, 6:83, and 21:51–67.",
  "The question form is what makes it an argument rather than an assertion. Abraham does not state a conclusion but asks what his people think, and the commentators' two readings both leave the answer to be supplied by those addressed."]),
 ("The Shared Forefather", [
  "The commentators note again why Abraham is the one arguing. As al-Rāzī observes, the Qur'an invokes the story of Abraham in the context of the Prophet Muhammad's disputations with the idolaters, because even the idolatrous Arabs had great respect for Abraham as one of their most prominent forefathers.",
  "The point applies to this verse as much as to v. 85. The question is put by a figure the audience already honors, and the commentators direct the reader to 43:26–27 for the same observation.",
  "> **Cross-Reference:** 2:258, 6:83, 21:51–67 — Abraham's disputations; 43:26–27 — the idolaters' respect for their forefathers.",
  "> **Classical View (R / IK, Ṭ):** either \"Do you think God would permit inanimate objects to share His worship, or that He is of their genus?\" or \"What do you think God will do with you when you meet Him, having worshipped other gods?\""]),
]),

182: (None, [
 ("Praise Be to God, Lord of the Worlds", [
  "The sūrah closes with praise. The commentators treat vv. 181–82 together, and their note concerns the greeting of peace that precedes it and the practice attached to both.",
  "The closing follows the declaration of transcendence at v. 180, where the commentators explained that above that which they ascribe refers on one level to the partners the idolaters ascribe to God (IJ) and on another to God's complete transcendence beyond all that is other than Him (Q). The praise here is what follows that declaration."]),
 ("Peace Upon the Messengers", [
  "The commentators supply a report about the preceding verse. Regarding the messengers, the Prophet is reported to have said, \"If you send peace upon me, send peace upon the messengers, for I am a messenger among the messengers\" (IK, Q, Ṭ), and they direct the reader to 33:56 for greetings of peace upon the Prophet.",
  "The report explains the plural. The peace is sent upon the message bearers collectively, and the Prophet's saying places himself among them rather than above them."]),
 ("A Practice at the End of Prayer", [
  "The commentators record a further report: it is reported that the Prophet would often recite vv. 180–82 at the end of his prayers (Q).",
  "The report connects the three verses as a unit. What closes the sūrah also closed the Prophet's prayers, and the commentators attribute the report to Q."]),
 ("The Counsel of ʿAlī", [
  "The commentators add a third report: ʿAlī ibn Abī Ṭālib, in a saying sometimes attributed to the Prophet (IK), counseled, \"Whosoever desires that the greatest measure of reward be measured for him on the Day of Resurrection, let his last words at any gathering be Glory be to thy Lord, the Lord of Might, above that which they ascribe. Peace be upon the message bearers. And praise be to God, Lord of the worlds\" (Bg).",
  "The commentators are careful about the attribution, noting that the saying is sometimes attributed to the Prophet. The counsel quotes all three closing verses, and the commentators attribute it to Bg.",
  "> **Cross-Reference:** vv. 180–81 — the declaration of transcendence and the peace upon the messengers, recited with this verse; 33:56 — greetings of peace upon the Prophet.",
  "> **Classical View (IK, Q, Ṭ / Bg):** the Prophet said, \"If you send peace upon me, send peace upon the messengers, for I am a messenger among the messengers\"; he often recited vv. 180–82 at the end of his prayers; and ʿAlī counseled making these three verses one's last words at any gathering."]),
]),

}
