# -*- coding: utf-8 -*-
"""037.md batch P: rebuild bodies for vv 95, 130, 156.

These three translation lines were wrong-verse substitutions, corrected by
fix_translation.py. Their bodies had been written against the WRONG verse text,
so correcting the translation line alone created a new misalignment. This batch
rebuilds the bodies against the corrected verses.

  v95  was "Then do you worship, apart from God, that which possesses for you
       neither benefit nor harm" (21:66); is now "Do you worship that which you
       carve" -- body had discussed benefit and harm
  v130 was "And peace be upon him the day he was born..." (19:15); is now "Peace
       be upon Elias" -- body had discussed the day-of-birth blessing
  v156 was "And We have sent to you Moses with Our signs and a clear authority"
       (11:96); is now "Or have you a manifest authority?" -- body had discussed
       the sending of Moses

Guards: no verbatim re-quote of the verse in opening prose; no verbatim repeat
of blockquote wording in the prose above it; echo the verse's own vocabulary.
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

95: (None, [
 ("That Which You Carve", [
  "The verse puts a question about the object of worship. The commentators give its sense: the question in these verses is, Do you worship what you make rather than the One Who made you?",
  "The formulation is the commentators' own rather than a quotation. It reduces the challenge to a contrast between the maker and the made, and the carving named in the verse is what makes the contrast concrete."]),
 ("Carving as the Point", [
  "The verse specifies the object as something carved. The commentators do not gloss the word separately, but their formulation supplies its force: what is carved is made by the worshipper's own hand.",
  "The argument therefore does not depend on what the carved thing represents. It depends on the fact that the worshipper made it, which is what the commentators' question turns on."]),
 ("A Second Reading at v96", [
  "The commentators record an alternative that widens the claim. V. 96 can also be understood to mean that God creates human beings and all that they do (IK), since He is the only one who can create.",
  "The attribution is to IK, with the ground given: He is the only one who can create. On this reading the contrast extends from the carved object to the carving itself."]),
 ("The Connection to Omnipotence", [
  "The commentators relate the second reading to a wider theme. In this latter sense, it is related to the affirmation of God's Omnipotence in such verses as 3:128: Naught is thine in the matter; 3:154: The decision belongs entirely to God; and 12:21: And God prevails over His affair, but most of mankind know not.",
  "The three cross-references are what place the reading. The commentators supply them rather than arguing the connection, and each states the same point about the scope of divine decision.",
  "> **Cross-Reference:** 3:128; 3:154; 12:21 — affirmations of God's Omnipotence; v. 96 — the completion of the question and IK's alternative reading; vv. 91–94 — the preceding questions to the idols.",
  "> **Classical View (IK):** the question is whether they worship what they make rather than the One Who made them; v. 96 can also be read to mean that God creates human beings and all that they do, since He alone can create, which relates to the affirmations of Omnipotence at 3:128, 3:154, and 12:21."]),
]),

130: (None, [
 ("Peace Upon Elias", [
  "The verse pronounces the blessing. The commentators direct the reader to the commentary on 37:77–79, where the same formula appears for Noah, and they add a note specific to this verse about the form of the name.",
  "The cross-reference is therefore the apparatus for the blessing itself, and the note that follows concerns the name rather than the prayer."]),
 ("Ilyās or Ilyāsīn", [
  "The commentators record a variation. The Arabic for Elias in v. 123 (as well as 6:85) is *Ilyās*, but here it is *Ilyāsīn*, which many believe is another rendering of the same name (Q, Ṭ).",
  "The attribution is careful: many believe rather than established. The commentators give both forms and cite the other verse where the shorter form appears."]),
 ("A Plural Reading", [
  "The commentators record a second possibility. But it can also be read as a plural form, meaning the Ilyāses, or the family of Ilyās, which is then understood to mean Ilyās and those who followed his religion (Q, Ṭ, Z).",
  "Three commentators are cited for this reading. On it the blessing extends beyond the prophet to his followers, and the commentators give that interpretation explicitly."]),
 ("The Blessing in the Sūrah's Pattern", [
  "The commentators' cross-reference to the Noah parallel supplies the meaning of the prayer. There they record that the prayer for peace throughout the worlds means that all mankind, the jinn, and the angels are to wish him peace (R, Z), and that the blessed are remembered well by later generations in a manner befitting their status (IK).",
  "The same formula closes the accounts of Abraham at v109 and of Moses and Aaron at v120, and the commentators note the refrain that follows each at vv. 81, 111, 122, and 132.",
  "> **Cross-Reference:** vv. 77–79 — the Noah parallel and its gloss; 6:85 and v. 123 — the shorter form Ilyas; v. 132 — the closing refrain.",
  "> **Classical View (Q, Ṭ, Z):** the name here is Ilyasin, which many take as another rendering of Ilyas; it can also be read as a plural meaning the Ilyases or the family of Ilyas, understood as Ilyas and those who followed his religion."]),
]),

156: (None, [
 ("A Question About Authority", [
  "The verse asks whether they possess a manifest authority. The commentators gloss the term: manifest authority is understood as a reference to revelation, as when Moses is reported to have been sent with a manifest authority, citing 4:153, 11:96, 23:45, 40:23, 44:19, and 51:38.",
  "The gloss is what fixes the meaning. The commentators identify the authority as revelation rather than as argument or evidence generally, and they supply six references where the same phrase describes what Moses was sent with."]),
 ("A Different Kind of Reproach", [
  "The commentators distinguish this verse from the ones before it. Thus, while vv. 154–55 reproach the idolaters for having no intellectual proofs to substantiate their assertion that God has begotten offspring, these verses reproach them for having no revealed source to substantiate their claims.",
  "The distinction is between two kinds of support. The earlier verses concern reasoning; this one concerns revelation. The commentators state the contrast explicitly."]),
 ("The Parallel Question", [
  "The commentators supply a verse that asks the same thing. In the same vein, 35:40 asks rhetorically: Do they have a share in the heavens, or did We give them a book, such that they stand upon a clear proof from it? They add further references at 34:44, 46:4, 57:37–38, and 68:47, and direct the reader to the commentary on 35:40 and 46:4.",
  "The quotation makes the demand concrete: a share in the heavens, or a book. The commentators cite the verse rather than restating the argument, and the list shows the demand recurs."]),
 ("Why the Question Is Asked", [
  "The verse follows the challenges at vv. 149–155, in which the idolaters are asked about daughters and sons, about whether they witnessed the creation of the angels, and about how they judge.",
  "The commentators' note explains the progression: the earlier questions establish that the claims have no reasoning behind them, and this verse asks whether they have anything else. The commentators do not gloss the sequence, but their distinction between the two reproaches supplies it.",
  "> **Cross-Reference:** 4:153; 11:96; 23:45; 40:23; 44:19; 51:38 — Moses sent with a manifest authority; 35:40 — the parallel question, with 34:44; 46:4; 57:37–38; 68:47; vv. 154–155 — the reproach for having no intellectual proofs.",
  "> **Classical View:** manifest authority refers to revelation, as when Moses was sent with one; these verses reproach the idolaters for having no revealed source for their claims, where vv. 154–55 reproached them for having no intellectual proofs, as at 35:40."]),
]),

}
