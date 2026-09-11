# -*- coding: utf-8 -*-
"""037.md batch Q: rebuild bodies for vv 117, 165, 167, 179.

Found by a stricter re-audit of the translation lines. Three of these carried
wrong text (v117 own-match 0.29, v167 own-match 0.23, v165 a paraphrase that
dropped "truly we are"), corrected by fix_translation.py and now at 1.00.
The fourth (v179) had a correct translation line but a body written about
Isaac and Jacob -- a different verse entirely. All four bodies are rebuilt
against the corrected verses.

  v117 "And We gave him the Scripture and the Criterion" -> "And We gave the
       two of them the Book that makes clear". The body had glossed al-kitab
       and al-furqan, which belong to 2:53, not to this verse.
  v165 "among them are those who are ranged in ranks" -> "truly we are those
       who are ranged [in ranks]". The body had treated the angels as spoken
       ABOUT in the third person; the verse has them speaking of themselves.
  v167 "Rather, they say, Indeed you are one of those possessed" (cf. 26:153)
       -> "Indeed, they used to say". The body had discussed an accusation of
       madness, which is not in this verse at all.
  v179 translation was already correct; the body had discussed the guidance of
       Isaac and Jacob and their descendants, which belongs much earlier.

Guards: no verbatim re-quote of the verse in the opening prose; no verbatim
repeat of blockquote wording in the prose above it; echo the verse's own
distinctive vocabulary; each paragraph distinct so duprate stays under 0.025.
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

117: (None, [
 ("The Two of Them", [
  "The verse records a gift made to a pair. The two are Moses and Aaron, the brothers whose mission the sūrah has just narrated, and what is given to them is a single book rather than two separate endowments.",
  "The dual form matters for how the gift is read. The preceding verses described the two as helped and made victorious together; here the same togetherness carries over into revelation, so the book is given to the mission and not to one brother apart from the other."]),
 ("A Book That Makes Things Clear", [
  "The commentators identify the book directly. The Book that makes clear is the Torah, and they add a general principle about what makes any revealed book such a book: it clarifies hidden matters of which people are ignorant (Ṭb).",
  "The emphasis therefore falls on clarification rather than on legislation. A book of this kind is defined by what it discloses, and the ignorance it addresses is the ignorance people carry before the book arrives."]),
 ("Guidance and a Light", [
  "The commentators then set the Torah inside the wider Quranic description of it. It is also described as a book wherein there is guidance and a light, and by it the prophets who submitted judged for the Jews.",
  "That judgement was not theirs alone. The sages and the rabbis judged by the same book, and they did so in accordance with such of God's Book as they were bidden to preserve and to which they were witnesses (5:44).",
  "Two conditions are built into that sentence. The judges act on the portion they were charged to preserve, and they stand as witnesses to it, which places responsibility for the book's transmission alongside the authority to judge by it."]),
 ("Why the Torah Is Named Here", [
  "The mention of the book belongs to a larger arc. The commentators point to the full Quranic account of Moses elsewhere: 7:103–55, 10:75–93, 17:101–4, 18:60–82, 20:9–97, 26:10–66, 27:7–14, 28:3–46, 40:23–45, 43:46–56, 44:17–31.",
  "Against that spread of accounts, this verse contributes one thing the others do not always foreground: the book itself, named as the thing given. The confrontation with Pharaoh and the deliverance of the people are told at length elsewhere; here the gift is the disclosure."]),
 ("The Shape of the Gift", [
  "Read with what precedes it, the verse completes a sequence. Help and victory came first, then the book. Deliverance is not the end of the mission but its condition, and what follows deliverance is a clarification given to a people.",
  "The verse that follows takes up the purpose of that clarification, which is why this verse stops at the naming of the book and leaves its aim to be stated next.",
  "> **Cross-Reference:** 5:44 — the Torah as guidance and light, by which the prophets, sages and rabbis judged; 2:53 — the parallel grant of Scripture and Criterion to Moses; 28:43 — the book given to Moses as a mercy; vv. 118–120 — the purpose and outcome of the gift.",
  "> **Classical View (Ṭb):** The Book that makes clear is the Torah, which, like all revealed books, clarifies hidden matters of which people are ignorant."]),
]),

165: (None, [
 ("Who Is Speaking", [
  "The verse is spoken in the first person plural, and the commentators use that fact to identify the speakers. Taken together with the glorification in the verse that follows, the combination indicates that it is the angels who are meant (IK, R).",
  "The identification is therefore inferential rather than stated. Nothing in the verse names angels outright; what settles it is the pairing of being ranged with glorifying, since that pairing describes a worshipping company rather than a human one."]),
 ("Ranged for Prayer and Worship", [
  "The commentators attach a purpose to the ranging. Being ranged [in ranks] is understood with reference to prayer and worship (IK, R), so the ranks are not military or administrative but liturgical.",
  "This is what distinguishes the verse from a mere description of order. The ranks exist for the sake of what is done inside them, and the glorification named in the next verse is that action."]),
 ("A Second Sense of Ranging", [
  "The commentators record a further reading of the same phrase. Ranged [in ranks] can also be taken as a reference to the hierarchy in which the angels are arranged, and that hierarchy is described as part of the universal hierarchy of existence.",
  "On this reading the verse is not only about worship but about place. Each angel holds a position in an ordering that extends beyond the angels themselves, which connects this verse to the known station mentioned in the verse before it."]),
 ("Against the Worship of Angels", [
  "Both readings bear on the sūrah's larger argument. Earlier verses accused the Quraysh of assigning daughters to God and of making the angels into objects of reverence; here the angels describe themselves.",
  "What they say about themselves is that they stand in ranks and glorify. A company arranged for worship and occupying assigned stations is a company of worshippers, and the verse supplies that self-description in their own words rather than in God's report about them."]),
 ("Order as the Point", [
  "The verse sits between the claim to a known station and the claim to glorification, and it is the middle term that joins them. The station fixes where each angel stands; the glorification is what is done from that station.",
  "The ranging is what makes the two coherent. Without ranks, stations would be isolated positions and glorification would be uncoordinated; with ranks, the company acts together and in order.",
  "> **Cross-Reference:** v. 164 — each angel has a known station; v. 166 — the glorification that the ranging supports; 66:6 — angels who do not disobey God's command; vv. 1–3 — the opening oath by those ranged in ranks.",
  "> **Classical View (IK, R):** The combination of their being ranged in ranks for prayer and worship and their glorifying God indicates that it is the angels who are meant; ranging can also denote the hierarchy in which the angels are arranged, part of the universal hierarchy of existence."]),
]),

167: (None, [
 ("A Habitual Claim", [
  "The verse opens a quotation rather than completing one. The form used is the habitual past, so what is introduced is something said repeatedly and over time, not a single remark made on one occasion.",
  "That framing matters for the verses that follow. What comes next is the content of the repeated claim, and this verse exists to mark it as a settled position these people held and returned to."]),
 ("What They Claimed", [
  "The commentators supply the substance. Before the revelation of the Quran, the idolaters claimed that were a reminder to come to them — meaning a revealed Book like the Torah or the Gospel — they would devote themselves to worshipping God.",
  "The claim is conditional and flattering to the speaker. It places the obstacle outside them, in the absence of a book, and promises wholehearted devotion once that absence is remedied."]),
 ("When the Reminder Came", [
  "The commentators then record what actually happened. When the Quran came, they denied it (R), and the same pattern is pointed to at 6:155–57.",
  "The denial is what exposes the earlier claim. The condition they had named was met, and the promised devotion did not follow, which indicates that the absence of a book was never the real obstacle.",
  "The commentators draw the parallel explicitly. This is similar to their denial of the Prophet in 35:42–3, where an oath to follow a warner is likewise followed by an increase in aversion when the warner arrives."]),
 ("A Reminder Like the Books of Old", [
  "The reference to a reminder identifies the kind of thing they said they wanted. A reminder in this sense is a revealed Book, and the two named as examples are the Torah and the Gospel.",
  "So the claim appeals to the same category of revelation that the sūrah has already discussed in its account of Moses. What they profess to be waiting for is of the same kind as what was given to earlier communities."]),
 ("What They Will Come to Know", [
  "The commentators close the passage with its outcome. On the Day of Judgment they will know the truth of what they rejected, and the commentators gather the parallels at 15:3 and 15:96, 29:66, 40:70, and 43:89.",
  "The knowledge is placed at the end rather than the beginning. It is not a knowledge they acquire by argument in this world but one that arrives with the events they are shown, which is the point the following verses press."]),
 ("The Function of the Verse", [
  "This verse and the ones after it answer an objection. If the idolaters had genuinely wanted a book, the coming of the Quran should have settled the matter; the passage explains why it did not.",
  "The answer is that the claim was never tested until the condition was met, and the denial that followed shows the claim to have been a way of postponing rather than a statement of readiness.",
  "> **Cross-Reference:** 6:155–57 — the same claim and the same denial; 35:42–3 — the oath to follow a warner, followed by aversion; 15:3, 15:96; 29:66; 40:70; 43:89 — knowing the truth of what was rejected; v. 168 — the content of the claim.",
  "> **Classical View (R):** Before the revelation of the Quran the idolaters claimed that were a reminder — a revealed Book like the Torah or the Gospel — to come to them, they would devote themselves to worshipping God; then when the Quran came, they denied it."]),
]),

179: (None, [
 ("A Repeated Instruction", [
  "The verse repeats what was said at verses 174–75, and the commentators treat the repetition itself as the thing to be explained rather than as a stylistic doubling.",
  "The instruction is to observe, and the object of observation is left general in the wording. What the commentators supply is the significance of hearing the same command twice within a few verses."]),
 ("Reaffirmation of the Lesson", [
  "One reading takes the repetition at face value. It can be seen as a reaffirmation of this essential lesson (IK), so the second occurrence does not add new content but presses home what has already been given.",
  "On this reading the two occurrences are identical in meaning and differ only in force. The lesson is repeated because it is the lesson the sūrah has been building toward, and repetition is how its weight is marked."]),
 ("Two Kinds of Observing", [
  "The commentators record a second reading that distinguishes the two occurrences. The first instance can be understood as a reference to observing things in this world, and this second instance as a reference to observing the events of the Hereafter (R).",
  "This reading gives each occurrence its own domain. The turn away and the watching that preceded it belong to what can be seen in the present, while the watching here belongs to what will be seen when the promised events arrive.",
  "The division is not arbitrary. It matches the sūrah's own movement, which has shifted from the arguments of this world to the descriptions of the Garden and the Fire that occupy its middle verses."]),
 ("The Nearness in the Warning", [
  "The verse pairs the command with a prediction. They are told to observe, and they are told that they will observe soon, so the same act is required of the Prophet and promised to his opponents.",
  "The nearness is what gives the warning its force. What is coming is not deferred indefinitely; it is presented as imminent, and the repetition of the verb makes the two observings the same event seen from two sides."]),
 ("Closing the Argument", [
  "This verse stands at the end of the sūrah's argumentative section. The refutations, the narratives of the messengers, and the descriptions of reward and punishment have been set out, and the sūrah now turns to its closing doxology.",
  "The repeated command is therefore the last thing said before the praise. What remains to be done is not further argument but observation, and the verse assigns that task to both parties at once.",
  "> **Cross-Reference:** vv. 174–75 — the first occurrence of the same instruction; vv. 171–73 — the word that went ahead for the messengers; v. 180 — the closing doxology; 15:3 — leave them and they will soon come to know.",
  "> **Classical View (IK, R):** The repetition of these verses is either a reaffirmation of this essential lesson (IK), or the first instance refers to observing things in this world and this second instance to observing the events of the Hereafter (R)."]),
]),

}
