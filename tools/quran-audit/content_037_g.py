# -*- coding: utf-8 -*-
"""037.md batch G: realign 4 misaligned bodies (Group C, first batch).

Each of these sections' bodies described a DIFFERENT verse than its heading:
  v58  heading "Are we then not to die," -> body discussed 92:18 spending wealth
  v60  heading "This indeed is the great triumph!" -> body discussed 92:20 the Face
  v70  heading "yet they hasten in their footsteps" -> body discussed 7:188 the unseen
  v74  heading "Not so for God's sincere servants" -> body opened the Noah narrative

Root cause: normalize.py promoted unheaded prose into verse headings, slicing it
against the wrong boundaries. Translations were fixed in a14dd59; bodies were not.

Guards carried from batch C's two duprate failures:
  - never re-quote the verse translation verbatim in the opening prose
  - never repeat a blockquote's wording verbatim in the prose above it
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

58: (None, [
 ("The Question That Follows the Rescue", [
  "The verse is the first of three in which the speaker asks whether death has been left behind. The commentators read these verses as a continuation of the words of the believer from the previous verses, or as the words of all of the believers in Paradise.",
  "Both readings are preserved. On the first, one speaker carries on from the preceding exchange; on the second, the voice widens to include everyone in the Garden. The commentators do not choose between them."]),
 ("Joy at What Has Been Avoided", [
  "The commentators state what the speech expresses: joy at realizing that they will not suffer death again and that they have avoided Divine Punishment.",
  "Two things are being rejoiced in, and the commentators keep them distinct. The first is the end of dying; the second is the escape from punishment. The question in this verse concerns the former, and the following verse takes up the latter."]),
 ("Death Once, and Not Again", [
  "The verse asks whether death will come only once. The commentators' gloss supplies the contrast that makes the question meaningful: in the Garden there is no second death, and the death already passed through was the one that led here.",
  "The question is therefore not a doubt but a confirmation. It is asked by those for whom the answer is already settled, and the commentators read it as an expression of relief rather than of enquiry."]),
 ("The Speech in Its Setting", [
  "These verses sit inside the dialogue at vv. 50–57, in which one of the speakers in Paradise recalls a companion who disputed the resurrection. The commentators at v56 record that the believer's words there are addressed to that companion.",
  "The question at this verse continues that address. The commentators do not gloss the transition, but the setting explains why the speech turns to death and punishment: both were the substance of the earlier dispute.",
  "> **Cross-Reference:** vv. 50–57 — the dialogue this speech continues; vv. 59–60 — the completion of the question; 5:119 and 44:51–57 — the blessings of the Garden.",
  "> **Classical View:** these verses continue the words of the believer from the preceding verses, or are the words of all the believers in Paradise, expressing joy at the realization that they will not die again and that they have escaped Divine Punishment."]),
]),

60: (None, [
 ("The Great Triumph", [
  "The verse names what has been attained. The commentators explain that attaining to the Garden is referred to as the great triumph in over a dozen verses.",
  "The recurrence is what the commentators establish. The phrase is not local to this passage but a settled designation, appearing more than a dozen times across the Qur'an, and the commentators cite the blessings of the Garden at 5:119 and 44:51–57."]),
 ("What Makes It Great", [
  "The commentators connect the description to the two things the preceding verses rejoice in: that death will not come again, and that Divine Punishment has been avoided.",
  "The triumph is therefore defined by absence as much as by possession. What has been escaped is part of what is being named, and the commentators read the three verses as a single movement from question to declaration."]),
 ("One Speech or Many", [
  "The commentators record the same alternative reading here as at v58: these verses continue the words of the believer, or are the words of all of the believers in Paradise.",
  "The choice affects who is speaking but not what is said. On either reading the declaration closes the speech, and the commentators preserve both without preferring one."]),
 ("The Contrast With the Dialogue", [
  "The speech began as a reply to a companion who denied the resurrection. The commentators at v53 record that the companion asked whether the dead would be brought back for reckoning, and this verse answers him by describing what the believers have reached.",
  "The declaration is therefore polemical as well as joyful. It closes an argument that was still open when the companion spoke, and the commentators note the answer by placing these verses within the same exchange.",
  "> **Cross-Reference:** vv. 58–59 — the question this verse answers; vv. 50–57 — the dialogue with the companion; 5:119 and 44:51–57 — the blessings of the Garden.",
  "> **Classical View:** attaining the Garden is called the great triumph in more than a dozen verses; these words continue the believer's speech from the preceding verses, or belong to all the believers in Paradise rejoicing that they will not die again and have avoided Divine Punishment."]),
]),

70: (None, [
 ("Hastening in Their Footsteps", [
  "The verse completes a pair. The commentators explain that because their fathers had followed a different set of beliefs, the disbelievers waxed arrogant when told to bear witness that there is no god but God (Ṭ), preferring the way of their forefathers to the one to which the Prophet called them (R).",
  "Two commentators are cited and their readings differ in emphasis. Ṭ locates the cause in the fathers' beliefs; R locates it in the preference for the fathers' way over the Prophet's call. The commentators preserve both."]),
 ("The Parallel at al-Baqarah", [
  "The commentators supply the Qur'an's own statement of the pattern, as at 2:170: When it is said unto them, Follow what God has sent down, they say, Nay, we follow that which we found our fathers doing. What! Even though their fathers understood nothing, and were not rightly guided?",
  "The quotation is what identifies the behaviour. The commentators cite it rather than describing the pattern in their own words, and the rebuke at the end of the verse is part of what they quote."]),
 ("The Wider References", [
  "The commentators add further parallels: 5:104, 7:28, 11:109, and 43:22–23.",
  "The list is what allows the sūrah's treatment to be brief. The appeal to the fathers is a recurring feature of the Qur'an's account of the prophetic disputes, and the commentators supply the references rather than arguing the point."]),
 ("Hastening and Inheriting", [
  "The verse's verb describes speed. The disbelievers do not merely follow their fathers but hasten in their footsteps, and the commentators read that haste as the mark of an unexamined inheritance.",
  "This connects to the rebuke quoted from 2:170 — the fathers understood nothing and were not rightly guided. The haste is toward a way that the commentators' source already describes as lacking understanding.",
  "> **Cross-Reference:** 2:170 — the refusal to follow what God sent down, preferring the fathers' way; 5:104; 7:28; 11:109; 43:22–23 — further parallels; vv. 69–71 — the passage this verse completes.",
  "> **Classical View (Ṭ / R):** because their fathers had held different beliefs, the disbelievers grew arrogant when told to bear witness that there is no god but God, preferring their forefathers' way to the one the Prophet called them to, as at 2:170."]),
]),

74: (None, [
 ("Not So for the Sincere", [
  "The verse makes an exception. The commentators record two readings of what it is excepted from. This verse follows upon v. 71, meaning that those who are sincere have not gone astray, or upon v. 73, meaning that the end of those who are sincere is not the same as that of the disbelievers (R).",
  "The two readings attach the verse to different antecedents. The first answers the statement that most of those of old had gone astray; the second answers the invitation to behold how those who were warned fared. The commentators attribute the account to R."]),
 ("Which Reading the Sequence Supports", [
  "The commentators state a preference. The latter interpretation is borne out by the following accounts, in which prophets such as Noah and Lot are saved along with small groups of their followers.",
  "The evidence is structural rather than lexical. What follows in the sūrah are narratives of deliverance, and the commentators read those as confirming that the verse concerns differing ends rather than differing paths."]),
 ("The Exception in the Sūrah's Pattern", [
  "The verses before this one describe a general going astray despite the sending of warners, and end by directing attention to the fate of those who were warned. The exception interrupts that pattern before the narratives begin.",
  "The commentators do not gloss the interruption, but the placement is what their preferred reading depends on: the verse stands immediately before the accounts of Noah and Lot, and those accounts supply the exception it announces."]),
 ("Small Groups Saved", [
  "The commentators' note specifies the shape of the deliverance: prophets such as Noah and Lot are saved along with small groups of their followers.",
  "The smallness is what recurs in the narratives that follow. At v81 the commentators note that among Noah's people only a few believed, and at v134 the deliverance of Lot and his family is recorded with a single exception. The verse anticipates that pattern.",
  "> **Cross-Reference:** vv. 71–73 — the going astray and the fate of those warned; vv. 75–82 — Noah's account; vv. 133–138 — Lot's account; v. 81 — the few who believed.",
  "> **Classical View (R):** the verse follows either v. 71, meaning the sincere did not go astray, or v. 73, meaning their end differs from that of the disbelievers; the latter is borne out by the accounts that follow, in which Noah and Lot are saved with small groups of followers."]),
]),

}
