# -*- coding: utf-8 -*-
"""037.md batch R: rebuild bodies for vv 114, 118, 175.

Found by re-auditing 037.md's translation lines against BOTH initial/ and
translation/ by own-verse match, then reading every survivor. Four lines were
genuine defects (v114, v118, v146, v175) and were corrected by
fix_translation.py; all four now sit at own-match 1.00.

Three of the four bodies had been written against the wrong text, so the
translation fix alone would leave the body describing something else:

  v114 was "And We gave him Moses and Aaron as a gift" -- read as a gift
       bestowed ON someone, with a body about God's gift to Abraham's
       descendants. The verse says God was gracious UNTO Moses and Aaron; the
       favour is theirs, not given through them.
  v118 was "That you may be guided to the straight path" -- a purpose clause
       in the second person, with a body about the purpose of revelation and
       the believer's use of Scripture. The verse is a past-tense statement
       in the dual: God guided the two of them.
  v175 was "We have made for them a covenant, and they have a clear proof"
       -- an unrelated claim, with a body about evidence against rejection.
       The verse is the command to observe.

v146's body was already correct (it discussed the gourd tree), so only its
translation line was replaced; no body rewrite needed.

Division of labour with neighbouring sections already rebuilt in batch Q:
v117 covers the Torah as the Book that makes clear, so v118 takes the
guidance-upon-the-straight-path portion of the shared [117-118] note;
v179 covers the repetition of the command, so v175 takes what is observed.

Guards: no verbatim re-quote of the verse in the opening prose; no verbatim
repeat of blockquote wording in the prose above it; echo the verse's own
distinctive vocabulary; paragraphs distinct so duprate stays under 0.025.
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

114: (None, [
 ("A Favour Bestowed Upon Them", [
  "The verse states a favour and names its recipients. The graciousness described here is directed toward Moses and Aaron themselves, so what the verse reports is something conferred on the two brothers rather than something conveyed through them to another party.",
  "That direction matters for reading what follows. The sūrah goes on to list what the two received and what was done for them, and the whole sequence is held together by this opening statement of favour."]),
 ("Two Readings of the Favour", [
  "The commentators offer a general and a specific account of what the graciousness consisted in. It is a reference either to all of the worldly and religious blessings they were given (Ṭs), or specifically to the gift of prophethood (IJ).",
  "The first reading takes the favour as comprehensive, covering everything granted to the two in both registers of life. The second narrows it to the one gift that defines them, on the grounds that prophethood is what makes the rest intelligible."]),
 ("Why the Pair Is Named Together", [
  "The verse joins the two brothers in a single statement. Elsewhere the Quran narrates the mission with Moses in the foreground and Aaron as the one sent with him; here the favour is declared over both at once.",
  "The pairing is consistent with what the sūrah does throughout this passage. Help, victory, the book, and guidance are all given in the dual, so the graciousness named here is the first in a series of gifts made to the two together."]),
 ("The Wider Account", [
  "The commentators place this verse inside the full Quranic record of the mission. For the account of Moses, see 7:103–55, 10:75–93, 17:101–4, 18:60–82, 20:9–97, 26:10–66, 27:7–14, 28:3–46, 40:23–45, 43:46–56, and 44:17–31.",
  "Against that spread of narration, this verse's contribution is the summary judgement. The details of the confrontation and the deliverance are told at length elsewhere; what is stated here is that the two were recipients of divine favour."]),
 ("Favour as the Frame", [
  "The verse functions as a heading for the verses that follow. What comes next is an itemisation: deliverance, help, victory, the book, and guidance, each of which can be read as a particular instance of the graciousness named at the outset.",
  "This is why the verse is stated so briefly. It does not argue or describe; it announces the character of everything that follows, and the following verses supply the content.",
  "> **Cross-Reference:** vv. 115–120 — the deliverance, help, victory, book, and guidance itemised; 44:30–31 — the deliverance of the Children of Israel; Ṭs and IJ on the scope of the favour; 20:39 — favour conferred upon Moses.",
  "> **Classical View (Ṭs, IJ):** That God was gracious unto Moses and Aaron refers either to all of the worldly and religious blessings they were given (Ṭs), or specifically to the gift of prophethood (IJ)."]),
]),

118: (None, [
 ("Guided in the Dual", [
  "The verse reports an act already completed, and it reports it of two. The form is past tense and dual, so what is described is guidance given to Moses and Aaron rather than an aim proposed to an audience.",
  "The distinction changes who is being spoken about. The verse is not setting out a purpose for someone else's benefit but recording what was done for the two brothers named in the verses before it."]),
 ("The Straight Path", [
  "The commentators connect the phrase to the Quran's own central petition. Regarding their being guided upon the straight path, see 1:6c, where the same words are used of the path believers ask to be shown.",
  "That connection places this verse inside a wider usage. The path named here is not a private route given to two prophets alone but the same path the community asks for in every prayer, and the two are said to have been set upon it."]),
 ("Guidance Following the Book", [
  "The verse follows the grant of the book, and the sequence is significant. The Torah was given as that which makes clear, and what comes next is the guidance of the two upon the straight path.",
  "The commentators treat the two as belonging together. The book clarifies hidden matters of which people are ignorant, and the guidance named here is the direction that such clarification makes possible.",
  "So the disclosure and the direction are not separate gifts. One supplies what is known and the other supplies where to go with it, and both are given to the same two recipients."]),
 ("Guidance and the Straight Path in the Sūrah", [
  "This verse completes the account of what the two received. Favoured, delivered, helped, made victorious, given the book, and now guided, the sequence closes with the direction in which the earlier gifts are to be used.",
  "The sūrah then turns to the praise left upon them among later generations, which shows the guidance named here as something whose effects outlasted the two themselves."]),
 ("What the Guidance Consists In", [
  "The commentators do not gloss the guidance separately from the book, which suggests they read the two as one gift described twice. The book is guidance and a light, and the path is where that light leads.",
  "Read this way, the verse is not adding a new endowment but naming the effect of the one already given. What was clarified is also what directs, and the two brothers are described as having been set upon it.",
  "> **Cross-Reference:** 1:6c — the straight path as the object of the community's petition; v. 117 — the Book that makes clear, of which this guidance is the effect; 5:44 — the Torah as guidance and a light; vv. 119–120 — the praise left upon them.",
  "> **Classical View (Ṭb):** The Book that makes clear is the Torah, which clarifies hidden matters of which people are ignorant; regarding their being guided upon the straight path, see 1:6c."]),
]),

175: (None, [
 ("A Command to Watch", [
  "The verse addresses the Prophet and tells him to watch. The object is the disbelievers, and the watching is set against a second watching promised to them, so the verse describes an exchange of observation between two parties.",
  "The commentators relate the command to 3:179, where the same pairing appears. The parallel establishes that this is a familiar form of address rather than a remark specific to this sūrah."]),
 ("What the Prophet Will Observe", [
  "The commentators specify the content of the Prophet's watching. He is told to observe what befalls the disbelievers in this life and the next (R).",
  "The range covers both domains. What befalls them is not confined to the events of this world, and the verse that follows carries the same command forward, which is what allows the commentators to read the two together."]),
 ("What They Will Observe", [
  "The second half of the verse reverses the direction. The commentators explain that the disbelievers will observe the Divine Aid and Support that comes to the Prophet in this life, and the great reward that he will receive in the next (R).",
  "So the two watchings are not symmetrical. What the Prophet observes is what befalls them; what they observe is what is given to him. Each party is shown the outcome of the other."]),
 ("A Second Reading", [
  "The commentators record an alternative that shifts the time of their observation. It could also be understood to mean that they will soon observe the punishment of the Day of Resurrection (Q).",
  "On this reading the nearness in the verse refers to the certainty of the event rather than to its proximity in this world, and what they will observe is the punishment itself rather than the aid given to the Prophet."]),
 ("Why the Command Is Given", [
  "The verse stands after the sūrah's long argument with the disbelievers and after the assurances given to the messengers. The command to watch is what remains when argument has been exhausted.",
  "It also reassures the one addressed. What is promised is not that the disbelievers will be persuaded but that the outcome will be visible, to the Prophet in what befalls them and to them in what is given to him.",
  "> **Cross-Reference:** 3:179 — the parallel command and promise; vv. 174–75 — the preceding turn away and watch; v. 179 — the same command repeated; 15:3 — leave them, and they will soon come to know.",
  "> **Classical View (R, Q):** The Prophet is told to observe what befalls the disbelievers in this life and the next, for they will observe the Divine Aid and Support that comes to him in this life and the great reward he will receive in the next (R); or they will soon observe the punishment of the Day of Resurrection (Q)."]),
]),

}
