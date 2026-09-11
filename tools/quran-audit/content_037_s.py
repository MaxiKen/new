# -*- coding: utf-8 -*-
"""037.md batch S: rebuild bodies for vv 49 and 149.

v149's translation line was a mistranslation -- "Are your daughters for them,
and for you are the sons?" drops the reference to the Lord, which is the whole
force of the challenge. Corrected by fix_translation.py to "So ask them, does
your Lord have daughters while they have sons?" (own-match 1.00). Its body
opened by quoting the OLD line verbatim, so the fix left the body misaligned.

v49's translation line is left as it stands: "as if they were pearls well
protected" is a blend of initial/ ("hidden eggs") and translation/ ("pristine
pearls"), the same kind of hybrid the confirmed-correct 001.md uses at v5 and
v7, and the pearl reading is itself supported by the apparatus (IJ, IK, T).
Its BODY, however, was built on an invented transliteration: it glossed the
phrase as "ka-annahunna al-yaqut wa-l-marjan" and then explained yaqut as
rubies and marjan as coral. That is the imagery of 55:58, not of 37:49. The
apparatus for 37:49 is about bayd (eggs) and its relation to whiteness.

Guards: no verbatim re-quote of the verse in the opening prose; no verbatim
repeat of blockquote wording in the prose above it; echo the verse's own
distinctive vocabulary; paragraphs distinct so duprate stays under 0.025.
"""

SURAH = "al-Ṣaffāt"
NUM = 37

SECTIONS = {

49: (None, [
 ("What Is Compared", [
  "The verse finishes the portrait of the companions begun in the verse before it, and it does so with a single image drawn from something concealed and untouched.",
  "The commentators take up the image at the level of the word itself. The word for egg, bayḍ, is closely related to the word for white, bayyāḍ or abyaḍ, and in the context of the maidens of Paradise that relation is taken as an allusion to purity (Iṣ)."]),
 ("Egg and White", [
  "The connection between the two words is not accidental in either language. As the commentators note, the link holds in English as well, where the same object carries the same suggestion of an unmarked surface.",
  "What the comparison therefore conveys is not hardness or value in the first instance but an absence of blemish. The image is chosen for what it says about purity rather than for what it says about price."]),
 ("The White of the Cup", [
  "The commentators tie the image back to the description of the drink earlier in the passage. The mention of eggs can be connected to the use of white in v. 46, where the cup is described by that colour.",
  "So the whiteness runs through the whole scene. What is drunk and what is beheld are described in the same terms, and the commentators add the wider parallel at 3:106–7, where those who enter Paradise are spoken of as those whose faces whiten."]),
 ("The Pearl Reading", [
  "The commentators record an alternative identification. Some say that what is intended by eggs is pearls (IJ, IK, Ṭ), and the parallel given is 56:22–23: wide-eyed maidens, the likeness of concealed pearls (Q).",
  "On this reading the image shifts from the shell to the jewel, but the point of concealment is carried across unchanged. What is prized is what has been kept out of sight, and both readings turn on that."]),
 ("What Hidden Means", [
  "The commentators give two senses for the concealment in the phrase. Hidden refers to the inside of the egg, or of the pearl, or it means that the egg or pearl itself is never touched (IK, Ṭ).",
  "The first sense locates the purity within; the second preserves it from without. Either way the quality described is one that depends on not having been handled, which is what the image contributes to the description of the companions."]),
 ("The Function of the Image", [
  "The verse is the last in a short sequence describing the Garden's cup and its attendants, and it closes the sequence on the note of preservation rather than possession.",
  "What is stressed is not that the companions belong to the inhabitants of the Garden but that they are kept as they are. The image of something enclosed and untouched does that work, and the commentators' glosses all point the same way.",
  "> **Cross-Reference:** v. 46 — the white cup, to which the whiteness here is tied; v. 48 — the maidens of modest gaze; 56:22–23 — the likeness of concealed pearls; 3:106–7 — the faces that whiten; 55:58 — a separate image of rubies and coral, not the one used here.",
  "> **Classical View (Iṣ, IK, Ṭ):** Bayḍ is closely related to the word for white, which in this context is taken as an allusion to purity; some say pearls are intended (IJ, IK, Ṭ), and hidden refers either to the inside of the egg or pearl or to its never being touched."]),
]),

149: (None, [
 ("A Question Put to Them", [
  "The verse opens a new movement in the sūrah by putting a question to the idolaters rather than answering one. The commentators mark the turn: these verses now move to criticism of the belief that God has sons or daughters.",
  "The form of the address matters. What is asked for is not a defence but an account of a preference, and the question is framed so that any honest answer concedes the point being made."]),
 ("The Preference Being Exposed", [
  "The commentators state the inconsistency directly. The idolaters are asked how they can attribute daughters to God when they themselves prefer sons and are distressed by daughters.",
  "The two halves of the question are what give it its force. The same people who assign female offspring to the divine realm reserve male offspring for themselves, and the verse holds the two assignments side by side."]),
 ("The Distress at a Daughter", [
  "The commentators supply the parallel that makes the preference concrete. At 16:57–58 they assign unto God daughters, glory be to Him, while they have that which they desire; and when one of them receives tidings of a female child, his face darkens and he is choked with anguish.",
  "The physical description is what the commentators lean on. The reaction is not a settled opinion but a visible distress, and it is that reaction which the question in this verse asks them to account for. The same scene appears at 43:17."]),
 ("An Argument About Logic", [
  "The commentators identify the target of the criticism precisely. It is aimed not only at the belief itself but also at its lack of internal logic.",
  "That distinction shapes the verse. The charge is not simply that the belief is false but that it cannot be held consistently by someone who feels about daughters what these people feel. The question is designed to surface the contradiction rather than to refute the claim from outside."]),
 ("The Wider Argument", [
  "The commentators place the passage among the Quran's repeated returns to this theme, citing 43:16 and 52:39 as the closest parallels and 53:21–22 among the others.",
  "The list is long because the claim appears in several forms across the Quran: daughters assigned to God at 16:57, offspring attributed to Him at 6:100 and 10:68, and the denial of any such thing at 112:3. This verse is one instance of a sustained argument rather than an isolated remark."]),
 ("What Follows", [
  "The verses that follow press the question from a second direction. Having asked about the preference, the sūrah asks how they came to know anything about the angels' creation at all.",
  "So this verse establishes the contradiction in their preference, and the next removes the ground on which the preference could be defended. The two questions are complementary, and the commentators read them together.",
  "> **Cross-Reference:** 16:57–58 — assigning daughters to God while desiring sons, and the darkened face; 43:16–17 and 43:19 — the same criticism, and the angels made females; 52:39 and 53:21–22 — the parallel questions; v. 150 — the question about witnessing the angels' creation.",
  "> **Classical View (the commentators on vv. 149–153):** The idolaters are asked how they can attribute daughters to God when they themselves prefer sons and are distressed by daughters; the criticism is aimed not only at the belief itself but at its lack of internal logic."]),
]),

}
