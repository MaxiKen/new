# -*- coding: utf-8 -*-
"""037.md batch O: realign the final 2 misaligned bodies (Group C complete).

  v172 heading "that they will surely be helped," -> body had described being
       made an example between them (33:21 material)
  v173 heading "and that Our host will surely be victorious." -> body had
       described God's covenant with the Prophet's people (v175's content)

Both share the [171-173] note, so each is written on its own half of it:
  v172 -> the help promised to the messengers, and the quotation of 40:51-52
  v173 -> the victory of the host, and the decree at 58:21
This split avoids the verbatim-repetition duprate failures of batch C.

Guards: no verbatim re-quote of the verse in opening prose; no verbatim repeat
of blockquote wording in the prose above it; echo the verse's own vocabulary.
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

172: (None, [
 ("The Help Already Promised", [
  "The verse states the first half of what has been decreed. The commentators supply its ground: God has already informed His messengers that they will prevail over the disbelievers, in both this world and the next (IK).",
  "The attribution is to IK. The informing is prior to the events, and the commentators specify the two spheres in which the prevailing occurs."]),
 ("The Parallel at Ghāfir", [
  "The commentators supply a verse that states the same promise. As at 40:51–52: Truly We shall help Our messengers and those who believe during the life of this world and on the Day when the witnesses arise, the Day when the excuses of the wrongdoers will not benefit them and theirs will be the curse, and theirs will be the evil abode.",
  "The quotation is what confirms the two spheres. The commentators cite the verse in full rather than paraphrasing it, and its second half describes the Day on which the excuses fail."]),
 ("Help for the Messengers and the Believers", [
  "The verse quoted extends the help beyond the messengers to those who believe. The commentators cite it without comment on that extension, but it widens the promise this verse records.",
  "The commentators do not gloss the addition, and the verse they quote supplies it as part of the same statement."]),
 ("A Promise, Not a Prediction", [
  "The commentators' word for what God has done is informed, and the verse quoted says We shall help. The help is therefore presented as something already settled rather than as a future contingency.",
  "This connects to the verse that precedes it, where the commentators note that God's Word has already gone forth unto His messengers. The going forth and the informing are the same act, and the commentators treat them as such.",
  "> **Cross-Reference:** 40:51–52 — the help promised to the messengers and the believers, and the Day when excuses fail; v. 171 — the Word already gone forth; v. 173 — the victory that completes the promise.",
  "> **Classical View (IK):** the messengers were told beforehand of their prevailing against those who disbelieve — in this life and in the life to come — as 40:51–52 states."]),
]),

173: (None, [
 ("The Host Victorious", [
  "The verse completes the promise begun in the two before it. The commentators state the general principle behind it: from a Qur'anic perspective, all prophetic missions are ultimately victorious.",
  "The claim is about all missions rather than any single one, and the commentators present it as a perspective the Qur'an gives rather than as an observation about history."]),
 ("The Decree", [
  "The commentators supply the ground of that principle. Because God has decreed: I shall surely prevail, I and My messengers, citing 58:21.",
  "The quotation is what makes the victory certain. The commentators cite the decree rather than arguing from outcomes, and the decree includes the messengers alongside God."]),
 ("Why the Two Verses Are Paired", [
  "The commentators treat vv. 171–173 as a single statement. The Word that has gone forth, the help promised, and the victory of the host are three parts of one decree, and the commentators' note covers all three.",
  "The help at v172 and the victory here are therefore not two separate promises but the same promise stated twice, and the commentators do not distinguish them."]),
 ("The Scope of the Victory", [
  "The commentators' earlier gloss specifies the spheres: the messengers will prevail over the disbelievers in both this world and the next (IK). The victory of the host therefore extends across both, as the quotation from 40:51–52 confirms.",
  "The commentators do not limit the claim to either sphere, and the two cross-references they supply — 40:51–52 for the help and 58:21 for the decree — together cover both.",
  "> **Cross-Reference:** 58:21 — the decree that God and His messengers shall prevail; 40:51–52 — the help in this world and on the Day the witnesses arise; vv. 171–172 — the Word gone forth and the help promised.",
  "> **Classical View (IK):** all prophetic missions are ultimately victorious, because God has decreed 'I shall surely prevail, I and My messengers' (58:21); the messengers will prevail over the disbelievers in both this world and the next."]),
]),

}
