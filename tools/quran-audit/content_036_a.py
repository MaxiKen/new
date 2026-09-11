# -*- coding: utf-8 -*-
"""036.md batch A: rebuild vv 1, 2, 3, 4 at corpus depth (median ~900w).

036.md was reduced to median 223w by stripping 16,483 words of boilerplate that had
been repeated verbatim across all 83 sections. This rebuilds from initial/036.md.

Source apparatus:
  v1 -- the separated letters (al-muqatta'at) at the head of 29 surahs, meaning known
      only to God (2:1c). Readings: 'O human being' (Q) -- ya' vocative, sin = unsayn,
      diminutive of insan; a name given to the Prophet whose meaning is unknown (Q);
      a name of the Quran itself; al-Qushayri identifies it with the Day of the
      Covenant (yawm al-mithaq, 7:172c). 'Ali b. Abi Talib (IA, Q) reports the Prophet
      named by seven names in the Quran.
  v2 -- hakim = Wise; also 'determined / made firm' (muhkam) as at 11:1 (Q). Ibn Kathir:
      muhkam indicates falsehood comes not upon it from before or behind (41:42);
      hakim may mean 'making wise' (muhkim). Also wise at 10:1; 31:2; 43:3-4.
  v3-4 -- affirm the Prophet's mission, supporting readings that take Yasin as a
      reference to the Prophet himself. For straight path, see 1:6c (perseverance,
      being made firm (T, Ts); nearness, knowledge, love of God (Q)).
"""

SURAH = "Yā Sīn"
NUM = 36

SECTIONS = {

1: (None, [
 ("The Separated Letters", [
  "The sūrah opens with two letters of the Arabic alphabet recited by name: *yāʾ* and *sīn*. They belong to the class known as the separated letters — *al-muqaṭṭaʿāt* — which stand at the beginning of twenty-nine of the Qur'an's one hundred and fourteen sūrahs. The commentators at 2:1 note that in recitation the names of the letters are used rather than their sounds, which is why they are transliterated here as they are recited.",
  "The majority position on their meaning is that it is known only to God. That is not a confession of ignorance about the text but a claim about it: these letters are not words, and no reading of them as words is compelled. The commentators record the readings that follow without requiring any of them, and the sūrah itself does not gloss them."]),
 ("The Reading 'O Human Being'", [
  "Some allow that *yāʾ sīn* could be an abbreviation meaning O human being (Q). On this interpretation the *yāʾ* is the vocative particle O, used in many Qur'anic verses, and the *sīn* abbreviates *unsayn*, the diminutive of *insān* — human being. The commentators note that in this context the diminutive O little human being functions as a term of endearment, and is read as God's address to the Prophet Muhammad.",
  "The reading has a consequence for what follows. If the opening is an address to the Prophet, then the oath at v2 and the affirmation at v3 attach to a person already named, and the sequence is vocative, oath, declaration. The commentators at vv 3–4 note exactly this: those verses affirm the Prophet's mission and thus support the interpretations that see Yā Sīn as a reference to the Prophet himself."]),
 ("A Name Given to the Prophet", [
  "Others say that Yā Sīn is a name given to the Prophet by God whose exact meaning is unknown (Q). For this reason it is sometimes used in the Islamic world as a name for a male. The commentators cite the report from ʿAlī ibn Abī Ṭālib (IA, Q): I heard the Messenger of God say, Verily God has named me by seven names in the Quran — Muhammad, Aḥmad, Ṭā Hā, Yā Sīn, thou enwrapped, thou who art covered, and servant of God — with the cross-references 3:144, 33:40, 47:2 and 48:29 for Muhammad; 61:6 for Aḥmad; 20:1 for Ṭā Hā; 73:1 and 74:1 for the two enwrapped addresses; and 72:19 for servant of God.",
  "The list places Yā Sīn among names the Qur'an itself supplies, which is what allows it to be used as a personal name. The report is preserved as a report; the commentators do not present it as settling the meaning of the letters, only as one account of how the sequence came to be understood as a name."]),
 ("The Other Readings", [
  "Two further interpretations are recorded. Other commentators take Yā Sīn to be a name of the Qur'an itself. Al-Qushayrī identifies it with the Day of the Covenant — *yawm al-mīthāq* — when God made a covenant with all the children of Adam, as at 7:172.",
  "The four readings are not competing claims about a single fact so much as different accounts of what kind of thing the opening is: an address, a name of the Prophet, a name of the Book, or an allusion to a primordial event. The commentators set them side by side. What they share is the assumption that the letters carry significance; what divides them is the direction of that significance, and the verse does not decide."]),
 ("What the Verse Does Not Say", [
  "The verse does not explain the letters, and does not indicate which of the recorded readings is intended. It does not connect them to the oath that follows, and does not say whether they are an address, a title, or something else.",
  "The verse also does not distinguish Yā Sīn from the separated letters at the head of the other twenty-eight sūrahs. The commentators treat it within that class, and the majority position — that the meaning is known only to God — applies to all of them equally. The particular readings offered here are offered for this sequence because the sūrah's own content, at vv 3–4, appears to support one of them."]),
]),

2: (None, [
 ("An Oath by the Book", [
  "By the Wise Quran. The sūrah swears by the Qur'an before making its declaration, and the thing sworn by is characterised by a single adjective. The oath form is familiar from the Makkan sūrahs, where God swears by created things and by revelation alike, and the effect is to establish the ground on which what follows will rest.",
  "What follows is the affirmation of the Prophet's mission at v3. The oath by the Qur'an and the declaration about the messenger are therefore joined: the Book is the warrant for the claim about the man. The commentators note at vv 3–4 that those verses affirm the Prophet's mission, and the oath here is what the affirmation is sworn upon."]),
 ("Ḥakīm as Determined", [
  "*Ḥakīm*, here translated Wise, can also mean determined or made firm — *muḥkam* — as at 11:1, where the Qur'an is described as a Book whose signs have been determined, *uḥkimat* (Q). The commentators cite Ibn Kathīr for the consequence: that the Qur'an is *muḥkam* indicates that falsehood comes not upon it from before it or from behind it, as at 41:42.",
  "On this reading the adjective describes the Book's resistance to alteration. Its signs have been fixed, and nothing can be inserted into it or removed from it. The commentators do not treat this as the only sense of *ḥakīm*, but as one of its established senses, and the cross-reference to 11:1 supplies the same root used of the same Book."]),
 ("Ḥakīm as Making Wise", [
  "*Ḥakīm* could also mean something that makes wise — *muḥkim* — indicating that the Qur'an teaches the truth. The commentators note that Ibn Kathīr takes the use of *ḥakīm* here as an allusion to the Qur'an as a revealed book, and that the Qur'an is described as wise elsewhere, at 10:1, 31:2, and 43:3–4.",
  "The two readings differ in direction. On the first the adjective describes what the Book is: settled, unalterable. On the second it describes what the Book does: it makes the one who follows it wise. The commentators preserve both, and the word's range admits both without strain, since a book whose signs are fixed can also be a book that instructs."]),
 ("The Adjective and the Sūrah's Argument", [
  "The choice of *ḥakīm* is not incidental to what the sūrah will do. Yā Sīn's central movement is an argument about resurrection, conducted with the disbelievers of Makkah, and the argument proceeds by reasoning from what is already known to what is being denied. A book described as wise is a book that argues.",
  "The commentators do not draw this connection explicitly at v2, and the verse does not claim it. What the verse establishes is the character of the authority being invoked. The sūrah then uses that authority in the way the adjective suggests — not by assertion alone but by putting cases, drawing analogies, and asking questions that the hearer must answer."]),
 ("What the Verse Does Not Say", [
  "The verse does not say what is being sworn to. It supplies the oath and stops, leaving the declaration to the next verse. It does not explain in what respect the Qur'an is wise, and does not choose between the readings of *ḥakīm* recorded by the commentators.",
  "The verse also does not say who swears. The oath form is unattributed in the Arabic, and the commentators do not supply an attribution here. The sūrah's later verses make clear that the speaker is God, but this verse leaves the oath standing on its own, which is characteristic of the form."]),
]),

3: (None, [
 ("The Affirmation of the Mission", [
  "Truly thou art among the message bearers. The declaration that the oath at v2 was sworn upon is now made. The emphatic construction leaves no room for qualification: the Prophet is among those who bear a message, and the sūrah states it as settled.",
  "The commentators note that these verses affirm the Prophet's mission, and that the affirmation supports the interpretations which see Yā Sīn as a reference to the Prophet himself. The connection is what gives the opening its shape: if the letters address the Prophet, then the oath and the declaration are addressed to him too, and the three verses form a single movement of naming, swearing, and confirming."]),
 ("Among, Not Alone", [
  "The verse says among the message bearers, not that he is the message bearer. The preposition places him within a company, and the company is one the Qur'an describes at length elsewhere. Noah, Hūd, Ṣāliḥ, Lot, Shuʿayb, and Moses have all been named in the preceding sūrahs as bearers of the same kind of message to the same kind of resistance.",
  "The placement matters for the argument the sūrah will make. A messenger among messengers is not an innovation, and the opposition he faces is not unprecedented. The sūrah's account of the people of the town at vv 13–29 depends on this: what happens there has happened before, and the outcome is known."]),
 ("The Sequence of the Opening", [
  "Read in order, the three verses move from an address to a warrant to a claim. Yā Sīn — if it is an address — names the one being spoken to. By the Wise Quran supplies the authority. Truly thou art among the message bearers states what that authority establishes.",
  "The commentators do not gloss the sequence as such, and the verses do not announce their structure. What they achieve is that the Prophet's mission is not asserted at the opening of the sūrah but sworn to, and sworn to by the Book that constitutes the mission. The affirmation is therefore self-supporting in a way a bare declaration would not be."]),
 ("The Address and Its Recipient", [
  "The declaration is in the second person singular and is addressed to the Prophet. The sūrah's opening is therefore not a general statement about prophethood but a particular statement to one man, and the commentators' note that these verses affirm his mission takes it that way.",
  "This is consistent with the Makkan context the commentators describe for the sūrah. It was revealed in the early part of the middle Makkan period, when the opposition was intensifying and the Prophet's standing was being contested. An affirmation of the mission is a response to a contest, and the verse's emphatic form is what a response to a contest looks like."]),
 ("What the Verse Does Not Say", [
  "The verse does not say what the message is, and does not summarise it. It affirms that the Prophet bears one and leaves the content to the sūrah that follows. It does not name the other message bearers, and does not say how many there were.",
  "The verse also does not say that the mission will succeed in the sense of being accepted. It states the fact of the mission rather than its outcome, and the sūrah's own narrative at vv 13–29 shows a community that rejected its messengers. The affirmation concerns the sending, not the reception."]),
]),

4: (None, [
 ("Upon a Straight Path", [
  "The mission affirmed at v3 is now qualified: it is upon a straight path. The commentators direct the reader to 1:6 for the phrase, where guide us upon the straight path is understood as a prayer for perseverance in following that path and thus for continued aid (Ṭ), and for being made firm in following the way of truth (Ṭs).",
  "The glosses at 1:6 add that the request for guidance implies seeking to be led to God Himself, and thus a desire for intimacy with Him, nearness to Him (Q), knowledge of Him, and love for Him. The path is therefore not merely a route but a relationship, and the commentators read it that way in the sūrah where the phrase is prayed rather than described."]),
 ("The Path and the Message", [
  "The attachment of the path to the mission is what the verse contributes. The Prophet is among the message bearers, and his is upon a straight path. The commentators do not gloss the connection, but the phrase does two things at once: it characterises the message and distinguishes it from other claims.",
  "A straight path is one without deviation, and the Qur'an uses the phrase to contrast the way of the messengers with the ways of those who opposed them. The sūrah's later verses will show the alternative in practice — a town that killed its messengers, and a people who said our auguring ill is upon yourselves. The path named here is what those alternatives are measured against."]),
 ("Straightness in the Qur'an", [
  "The phrase recurs throughout the Qur'an and is not local to this sūrah. The commentators' cross-reference to 1:6 places it in the daily prayer, where it is asked for rather than asserted. The difference between the two uses is significant: in al-Fātiḥah the believer asks to be guided upon it, and here the Prophet is declared to be upon it.",
  "The commentators note at 1:6 that for those who believe and perform righteous deeds, their Lord guides them by their faith, citing 10:9 (Ṭs). The guidance is therefore continuous rather than a single bestowal, and the path is something one remains upon rather than something one enters once. The Prophet's being upon a straight path is a standing condition, not an achievement."]),
 ("What the Verse Does Not Say", [
  "The verse does not define the straight path, and does not enumerate what it consists in. It attaches the phrase to the mission and leaves the content to the Qur'an's wider use of it, which the commentators supply by cross-reference rather than by explanation.",
  "The verse also does not say that others are not upon it. It describes the Prophet's mission and does not exclude anyone else. The sūrah's later verses distinguish those who follow the messengers from those who reject them, but this verse makes no such division; it states where the mission lies and moves on."]),
]),

}
