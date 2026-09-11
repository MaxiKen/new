# -*- coding: utf-8 -*-
"""037.md batch L: realign 4 misaligned bodies (Group C, 5th batch).

  v143 heading "And had he not been among those who glorify" -> body had
       described the gourd plant (v146's content)
  v151 heading "Behold! It is of their own perversion that they say," -> body had
       described God not being unaware of what they do
  v162 heading "can tempt any against Him," -> body had described a claim that
       God sent down their punishment
  v166 heading "Truly we are those who glorify." -> body had described the angels
       not being arrogant in worship

These four are groundable via SHARED RANGE notes (143-44, 151-52, 161-63,
165-66), which the abbreviated-range parsing bug had previously hidden. The
commentary therefore speaks to the passage rather than to the individual verse,
since that is what the source provides.

Guards carried from batches C, I:
  - never re-quote the verse translation verbatim in the opening prose
  - never repeat a blockquote's wording verbatim in the prose above it
  - echo the verse's own distinctive vocabulary somewhere in the body
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

143: (None, [
 ("The Condition That Saved Him", [
  "The verse states a counterfactual about Jonah's deliverance. The commentators give its ground: had it not been for the life of devotion lived before these events, Jonah would have remained in the belly of the fish (IK, Ṭ).",
  "The commentators attribute the reading to IK and Ṭ. What saved him is located before the crisis rather than within it, and the deliverance is therefore read as the fruit of prior devotion."]),
 ("A Prophetic Saying", [
  "The commentators connect the verse to a saying of the Prophet Muhammad. Thus some relate this story to the saying: Seek to know God in times of ease, and He will know you in times of difficulty (IK).",
  "The attribution is to some, reported through IK. The saying is what generalises the narrative, and the commentators present the relation as one some have drawn rather than as a stated equivalence."]),
 ("The Cry in the Darkness", [
  "The commentators record a second reading of what the glorifying was. This verse can also be understood as a reference to Jonah's having cried out in the darkness: There is no god but Thee! Glory be to Thee! Truly I have been among the wrongdoers, citing 21:87, with Aj, IK, and Ṭ.",
  "The three commentators are cited for the identification, and the cross-reference supplies the wording. The commentators add that for the more extensive prayer and repentance of Jonah in the Bible, see Jonah 2:1–9."]),
 ("What Would Otherwise Have Happened", [
  "The commentators give two formulations of the alternative. If not for his praising God, he would have remained in the belly of the fish alive until the day on which human beings are resurrected (Aj), or the belly of the fish would have been his grave until the Day of Resurrection (Aj, Ṭ).",
  "The two differ in emphasis. The first stresses that he would have remained alive; the second that the belly would have become his grave. Both are attributed to Aj, with Ṭ joining the second, and the commentators preserve them together.",
  "> **Cross-Reference:** 21:87 — the cry in the darkness; Jonah 2:1–9 — the more extensive Biblical prayer; vv. 144–146 — the tarrying, the casting forth, and the gourd.",
  "> **Classical View (IK, Ṭ / Aj):** had it not been for the devotion lived before these events he would have remained in the fish's belly; some relate the story to the saying 'Seek to know God in times of ease, and He will know you in times of difficulty'; the glorifying is also read as his cry at 21:87, and without it he would have remained alive in the belly, or it would have been his grave, until the Day of Resurrection."]),
]),

151: (None, [
 ("Of Their Own Perversion", [
  "The verse attributes a saying to their perversion. The commentators gloss the word: perversion renders *ifk*, which is also understood to mean delusion, deception, or falsehood; see 29:61.",
  "The gloss supplies the range of the term. The commentators give three alternatives rather than a single equivalent, and they cite the cross-reference for the word's use elsewhere."]),
 ("What They Say", [
  "The verse does not state the saying here; it comes in the following verse, where the claim that God has begotten is reported and contradicted. The commentators connect the two.",
  "The perversion named here is therefore the ground of the claim made next, and the commentators treat the two verses as a single statement of the assertion and its character."]),
 ("The Connection to the Angels", [
  "The commentators explain how the claim arose. The idolaters' assertion that God has begotten is related to their saying that angels are females, as some of them conceived of God as having consorts with whom He begat other deities.",
  "The explanation supplies the reasoning behind the claim. The commentators do not present it as the verse's statement but as the relation between two assertions the idolaters made."]),
 ("The Answer at al-Anʿām", [
  "The commentators supply the Qur'an's reply. Thus 6:101 asks: How should He have a child when He has no consort, and He created all things?",
  "The quotation is what answers the claim. The commentators cite it rather than restating the argument, and the two halves of the question correspond to the two halves of the explanation — the absence of a consort, and the fact of creation.",
  "> **Cross-Reference:** 29:61 — the word ifk elsewhere; 6:101 — the question that answers the claim; v. 152 — the claim itself; vv. 149–153 — the surrounding questions.",
  "> **Classical View:** perversion renders ifk, also understood as delusion, deception, or falsehood (cf. 29:61); the assertion that God has begotten is related to their saying the angels are female, since some conceived of God as having consorts by whom He begat other deities, which 6:101 answers."]),
]),

162: (None, [
 ("No Power to Tempt", [
  "The verse completes a statement begun in the preceding one. The commentators give its sense: neither the disbelievers nor the jinn have any power to misguide or mislead, as God has already decreed each individual's final end.",
  "The commentators supply both the negation and its ground. The inability is not contingent but follows from a decree already made, and the commentators state the two together."]),
 ("The Scope of the Negation", [
  "The verse addresses both the worshippers and what they worship, and the commentators extend the negation to the jinn as well. The three are treated together as lacking the power to lead anyone astray.",
  "The commentators do not separate the cases, but the extension matters: the claim is not only that idols cannot tempt but that no created agent can."]),
 ("God's Words to Satan", [
  "The commentators relate the passage to a wider statement. This passage thus reflects another aspect of God's Words to Satan: As for My servants, truly thou hast no authority over them, citing 17:65.",
  "The cross-reference is what places the verse. The commentators describe it as another aspect of the same point, and the exception for God's servants matches the exception the sūrah makes at v160."]),
 ("Satan's Own Acknowledgement", [
  "The commentators add Satan's own words. Satan himself acknowledges this, saying: I shall cause them to err all together, save Thy sincere servants among them, citing 38:82–83, with a further reference at 15:39–40.",
  "The acknowledgement is what completes the argument. The commentators cite the verses rather than drawing the inference, and the exception Satan himself names corresponds to the sincere servants excepted here.",
  "> **Cross-Reference:** 17:65 — no authority over God's servants; 38:82–83 and 15:39–40 — Satan's acknowledgement and its exception; vv. 161, 163 — the statement this verse completes.",
  "> **Classical View:** neither the disbelievers nor the jinn have power to misguide or mislead, since God has decreed each individual's final end; this reflects God's words to Satan at 17:65, and Satan himself excepts God's sincere servants at 38:82–83."]),
]),

166: (None, [
 ("Those Who Glorify", [
  "The verse is a declaration of glorification. The commentators identify the speakers from the combination of what precedes and what is said here: the combination of the reference to their being ranged in ranks for prayer and worship (IK, R) and their glorifying God indicates that it is the angels who are meant.",
  "Two commentators are cited for the identification, and the reasoning is from the pairing rather than from either element alone. The commentators state that the combination is what indicates it."]),
 ("Ranged in Ranks", [
  "The commentators give a second reading of the phrase that precedes. Ranged in ranks can also be understood as a reference to the hierarchy in which the angels are arranged, which is part of the universal hierarchy of existence.",
  "The alternative widens the reference. On the first reading the ranks concern prayer and worship; on the second they concern a hierarchy that extends beyond the angels. The commentators preserve both."]),
 ("Glorification as the Angels' Speech", [
  "The verse's declaration belongs to the angels on the commentators' identification, and it follows their statement at v164 that each of them has a known station that is never left.",
  "The commentators connect the two by the identification of the speaker. The stations described earlier and the glorification declared here belong to the same beings, and the commentators' note supplies that link."]),
 ("Worship Without Weariness", [
  "The commentators' note about being ranged for prayer and worship places the glorification in the context of uninterrupted service. This corresponds to the detail recorded at v164 that some remain bowing without straightening their spines and others remain prostrating without lifting their heads (Z).",
  "The glorification is therefore continuous rather than occasional, and the commentators' two notes together supply both its constancy and its source.",
  "> **Cross-Reference:** v. 164 — the known stations of the angels; v. 165 — those ranged in ranks; 15:39–40 — the sincere servants excepted.",
  "> **Classical View (IK, R):** the combination of being ranged in ranks for prayer and worship with their glorifying God indicates that the angels are meant; ranged in ranks may also refer to the hierarchy in which the angels are arranged, part of the universal hierarchy of existence."]),
]),

}
