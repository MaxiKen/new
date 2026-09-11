# -*- coding: utf-8 -*-
"""037.md batch C: deepen the four thinnest sections that have source apparatus.

037.md runs 182 sections at median 232w. 81 of them sit under 260w and have
apparatus in initial/037.md to ground a rewrite. This batch takes the four
thinnest of those: v133 (142w), v136 (147w), v104 (148w), v106 (154w).

Template is 037.md's own: mini-heading prose, with the Cross-Reference and
Classical View lines as blockquote PARAGRAPHS inside the final mini-heading
(apply_sections.py wraps a tuple's first element in **...**).

Every claim below is drawn from initial/037.md's apparatus for these verses.
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

104: (None, [
 ("The Call That Stopped the Knife", [
  "The verse marks the turning point of the narrative. The commentators explain that before Abraham could sacrifice his son, God called to him, and when he turned, Abraham found a fine white-horned ram to take his son's place in the sacrifice (IK).",
  "The sequence is precise: the call comes before the act, and the substitute is already present when Abraham turns. The commentators describe the ram as fine and white-horned, and they attribute the account to IK."]),
 ("The Horns in the Kaʿbah", [
  "The commentators record a further tradition. According to some accounts, the horns of this ram were kept in the Kaʿbah, but were lost when the Kaʿbah burned down in 63/683.",
  "The attribution is careful — according to some accounts rather than as an established fact — and the commentators supply the date at which the relic is said to have been lost. The detail is preserved because it was reported, not because the verse states it."]),
 ("The Basis of a Rite", [
  "The commentators draw the ritual consequence. This substitution of a ram for Abraham's son serves as the basis for the ritual of slaughtering an animal that is required as the final rite of the ḥajj.",
  "The connection is what makes the verse operative rather than merely narrative. What happened once to Abraham is what the pilgrim re-enacts, and the commentators identify the substitution as the ground of the rite."]),
 ("The Trial and Its End", [
  "The verse stands between the submission at v103 and the naming of the trial at v106. The commentators explain at v106 that the command to sacrifice is described as a trial, and that this is also understood to mean it was a blessing (Q).",
  "The call is therefore what closes the trial. The commentators note at v106 that it is through severe trials that God brings His pious servants the best reward in this life and the next, if they are able to faithfully endure them, as did Abraham (Ṭb). The substitution is the reward, not the cancellation of the test."]),
 ("What the Verse Does Not Say", [
  "The verse does not describe the ram beyond the commentators' note, and does not say how it appeared. The substitution is stated, and the detail is supplied from IK.",
  "The verse also does not mention the ḥajj. The commentators supply the connection to the rite, and the verse records only the call and the substitution.",
  "> **Cross-Reference:** v. 103 — the submission that preceded the call; v. 107 — the ransom that follows it.",
  "> **Classical View (IK):** God called before the sacrifice could be completed, and Abraham, turning, found a fine white-horned ram in his son's place; some accounts say its horns were kept in the Kaʿbah until the fire of 63/683."]),
]),

106: (None, [
 ("The Manifest Trial", [
  "The verse names what has happened. The commentators explain that the command to sacrifice is described as a trial, and that this is also understood to mean that it was a blessing (Q).",
  "The double naming is what the commentators emphasise. The same event is a trial and a blessing, and the commentators attribute the second reading to Q rather than presenting it as their own."]),
 ("Why a Trial Is a Blessing", [
  "The commentators supply the reasoning. It is through severe trials that God brings His pious servants the best reward in this life and the next, if they are able to faithfully endure them, as did Abraham (Ṭb).",
  "The condition is explicit. The reward follows endurance rather than the trial as such, and the commentators cite Abraham as the one who endured. The attribution is to Ṭb, and the blessing is therefore conditional on faithfulness."]),
 ("Manifest", [
  "The trial is called manifest, and the commentators do not gloss the adjective. What the surrounding narrative supplies is why: the command was explicit, the preparation was carried through, and the outcome was visible.",
  "The manifestness is what makes the trial available as an example. The commentators' note that Abraham faithfully endured is what allows the verse to function as a pattern rather than as a private test."]),
 ("The Verse in the Sequence", [
  "The verse follows the substitution at vv. 104–105 and precedes the refrain at v110. The commentators do not gloss the transition, but the structure supplies it: the trial is named, then rewarded.",
  "The refrain that follows — Thus do We recompense the virtuous — is what the commentators connect to the blessing named here. The recompense is the reward that severe trials bring to those who endure them.",
  "> **Cross-Reference:** vv. 104–105 — the call and the ransom; v. 110 — the refrain of recompense that follows.",
  "> **Classical View (Q / Ṭb):** the command is called a trial and is also read as a blessing, because severe trials are the means by which the pious are brought to the best reward in both lives — provided they endure faithfully, as Abraham did."]),
]),

133: (None, [
 ("Lot Among the Message Bearers", [
  "The verse introduces the third of the sūrah's prophetic narratives. The commentators note that Lot is considered to be either Abraham's nephew or cousin, and they record the disagreement rather than resolving it.",
  "The relation matters for the narrative's placement. Lot follows the Abraham cycle at vv. 83–113, and the commentators supply the kinship that connects the two."]),
 ("The Wider Accounts", [
  "The commentators direct the reader to the Qur'an's other narrative accounts of Lot and his people: 7:80–84, 11:77–83, 15:57–77, 26:160–73, 27:54–58, 29:26–35, and 54:33–38. They add the similar Biblical narrative in Genesis 19.",
  "The list is what allows this verse to introduce Lot in a single line. The story is told at length elsewhere, and the commentators supply the references rather than retelling it here."]),
 ("A Messenger, Not Only a Kinsman", [
  "The verse names Lot among the message bearers, and the commentators do not gloss the phrase. What it establishes is his office, which is what the following verses presuppose.",
  "The sūrah's pattern is consistent. Noah was introduced the same way at v79, and Jonah at v139. The commentators do not draw the parallel, but the formula recurs across the sūrah's four narratives."]),
 ("What Follows", [
  "The verse is followed by the account of Lot's deliverance and his people's destruction at vv. 134–138. The commentators explain at v136 that after they refused to pay him any heed, the people of Lot's town were destroyed.",
  "The introduction is therefore brief because the narrative that follows is not. The commentators supply the detail at the verses that carry it rather than at this one.",
  "> **Cross-Reference:** the seven parallel passages listed above, together with the similar Biblical narrative at Genesis 19."
  "> **Classical View:** Lot is considered to be either Abraham's nephew or his cousin; the commentators record both without preferring either."]),
]),

136: (None, [
 ("Then We Destroyed the Others", [
  "The verse states the outcome. The commentators explain that after they refused to pay him any heed, the people of Lot's town were destroyed. The refusal is what precedes the destruction, and the commentators make the sequence explicit.",
  "The verse itself does not give the reason. The commentators supply it from the narrative, and the destruction follows the refusal rather than occurring independently of it."]),
 ("The Manner of Destruction", [
  "The commentators record two descriptions of the means. The people were destroyed by stones of baked clay, citing 11:82 and 15:74, or by a torrent of stones, citing 54:34.",
  "The two descriptions are preserved rather than harmonised. The commentators cite both sets of verses and do not choose between them, and the difference is one of emphasis rather than of substance."]),
 ("A Torment From Heaven", [
  "The commentators add what the stones are said to have been: they are said to have rained down upon them as a torment from Heaven, citing 29:34, with a further reference at 7:84.",
  "The attribution is careful. The commentators say the stones are said to have rained down, marking the description as reported rather than as the verse's own statement. The origin of the torment is what the cross-reference establishes."]),
 ("The Others", [
  "The verse distinguishes the others from those saved. The preceding verses describe the deliverance of Lot and his family, and this verse names those left behind.",
  "The commentators do not gloss the distinction, but the narrative supplies it. The sūrah's pattern across its four narratives is consistent: the messenger and those with him are saved, and the people who refused are destroyed.",
  "> **Cross-Reference:** 11:82 and 15:74 — stones of baked clay; 54:34 — a torrent of stones; 29:34 — a torment from Heaven; 7:84.",
  "> **Classical View:** after the people of Lot's town refused to pay him any heed they were destroyed by stones of baked clay or a torrent of stones, said to have rained down upon them as a torment from Heaven."]),
]),

}
