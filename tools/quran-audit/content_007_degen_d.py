#!/usr/bin/env python3
"""Rebuild of four more degenerate sections of expanded/007.md.

Continues content_007_degen_a.py, _b.py and _c.py. Measured before this rebuild:

    v149 0.094   v188 0.091   v190 0.092   v197 0.092

These four are the mixed case rather than the pure one. Each carries genuine
apparatus content -- v188 and v190 are among the richer notes in the sūrah --
interleaved with tautological loops, so the loss is not of scholarship but of
readability. Rebuilt from initial/007.md with the surviving material kept and
the loops dropped. Every citation below was checked against extract_source.py
before writing.
"""

SURAH = "al-Aʿrāf"
NUM = 7

SECTIONS = {

    # ------------------------------------------------------------------ 149
    149: (None, [
        ("Remorse Fell Into Their Hands", [
            "The verse's opening phrase is an idiom rather than a description, and the commentators read it three ways. Literally it says that remorse *fell into their hands* — and al-Rāzī explains that the falling is an inward event: remorse settling into the heart, which the hand is made to stand for because the hand is where a person feels what he cannot otherwise express.",
            "Al-Rāzī and al-Zamakhsharī both record a second reading, more physical. The remorseful bite their hands, as though attacking the site of the feeling. On this account the idiom is not a metaphor for interiority at all but a compressed report of a gesture — the same gesture the Qur'an describes elsewhere for the Day of Judgment, when the wrongdoer bites his hands.",
            "The third reading turns the hand from an image of feeling into an instrument of repair. Remorse fell into their hands in the sense that the responsibility now lay in their own hands: it was for them to make amends and set matters right, and no one else could do it.",
            "The three are not competing so much as cumulative. Remorse arrives as a feeling, expresses itself as a gesture, and — if it is genuine — becomes an acknowledgement that the fixing belongs to the one who broke it. The verse needs all three, because what follows is not a feeling but a sentence spoken.",
        ]),
        ("Seeing Before Speaking", [
            "Between the remorse and the prayer the verse places an act of sight: *and they saw that they had gone astray*. The sequence is deliberate and it is the whole psychology of the verse. Remorse came first and was not sufficient; what produced the prayer was the seeing.",
            "That distinction matters. The people had not stopped wanting the calf. They had seen what they were. Al-Rāzī's first reading — remorse settling into the heart — describes the arrival of the feeling, and this clause describes the moment the feeling became knowledge, which is the only point at which it can issue in speech.",
            "The Qur'an marks the same order elsewhere when it describes the disbeliever on the Day of Judgment seeing his record and wishing he had not been given it. Sight precedes the wish as it precedes the prayer here. What a person says about himself after seeing is different in kind from what he says before.",
        ]),
        ("Contrition Without an Excuse", [
            "What they say is short, and its shortness is the point. *If our Lord does not have mercy upon us and forgive us, we shall surely be among the losers.* There is no explanation, no mitigating circumstance, no reference to the samirī or to Moses's absence or to the calf's apparent power. The sentence contains a condition and a consequence and nothing between them.",
            "The source note describes it as immediate and utter contrition, a casting of themselves upon the mercy of God rather than an offering of excuses, and identifies two exact parallels. The first is in this sūrah, at verse 23, where Adam and his spouse say:",
            "> *\"Our Lord! We have wronged ourselves. If Thou dost not forgive us and have Mercy upon us, we shall surely be among the losers.\"* (7:23)",
            "The second is Noah's, at 11:47: *\"My Lord! Truly I seek refuge in Thee from questioning Thee concerning that whereof I have no knowledge. If Thou dost not forgive me and have Mercy upon me, I shall surely be among the losers.\"*",
            "Three speakers, three different failures, one formula — and the formula is identical down to its closing words. That is not coincidence but instruction. The Qur'an is showing what repentance sounds like when it is real, and it sounds the same whether it is spoken by the first human beings, by a prophet who asked a question he should not have asked, or by a people who built a calf. The structure is: we did this, we have no defence, everything now depends on you.",
        ]),
        ("Among the Losers", [
            "The word translated *losers* is *khāsirūn*, from *kh-s-r*, to lose, to suffer diminution, to come out of a transaction worse than one went in. It is commercial language applied to a spiritual state, and this sūrah uses it repeatedly — at verse 90 of those who disbelieved and turned others from the path, at verse 92 of the people of Shuʿayb, whose own trading idiom is turned back on them, and at verse 99 of those who feel secure from God's plan.",
            "The recurrence is not mere repetition. Each use names the same thing from a different direction: the disbeliever loses, the fraudulent trader loses, the secure lose. What makes verse 149's use different is who is speaking. In the earlier instances the word is God's description of them; here it is their description of themselves.",
            "That is the last step the verse records, and it is the one that matters. A person who can say *we shall be among the losers* about himself, without qualification and without an excuse attached, has already taken the position that mercy requires of him. The calf-worshippers are not saved by their remorse; they are saved by having arrived, through it, at an accurate sentence about themselves.",
        ]),
    ]),

    # ------------------------------------------------------------------ 188
    188: (None, [
        ("No Power Over Benefit or Harm", [
            "The verse opens with a command to disclaim, and the disclaimer is as complete as language allows. *Say: I have no power over what benefit or harm may come to me, save as God wills.* The Prophet ﷺ is instructed to state that he cannot secure a good for himself or deflect an evil from himself, except as God wills it.",
            "The restriction to himself is what gives the statement its force. He is not denying the ability to help others while retaining some private power; he is denying it in the case where every person would most expect to have it. If a man cannot guarantee his own benefit or ward off his own harm, the question of his doing so for anyone else does not arise.",
            "The same disclaimer is put in the Prophet's ﷺ mouth twice more. 10:49: *\"Say: I have no power over what harm or benefit may come to me, save as God wills. For every community there is a term.\"* And 72:21–22, where the denial is extended to what he can do for others: *\"Say: I have no power over what harm or guidance may come to you.\"* The three together close the matter from both sides — nothing for himself, nothing for them.",
            "The theological purpose is plain and it is protective. A prophet who could benefit or harm independently would be an object of petition, and petition directed to him would be indistinguishable from worship. The disclaimer removes the ground on which such a practice could be built, and it removes it in the prophet's own reported words rather than in a third-person statement about him.",
        ]),
        ("Had I Knowledge of the Unseen", [
            "The second clause argues the same point from the other direction, as a counterfactual. *Had I knowledge of the unseen, I would have acquired much good, and no evil would have touched me.* The reasoning is an open syllogism whose conclusion is visibly false, which is what makes it persuasive: he has not acquired unlimited good and evil has touched him, therefore the premise fails.",
            "The unseen — *al-ghayb* — is defined broadly by the commentators. It covers every realm of reality beyond ordinary human reach: the celestial realm, the inner intentions and thoughts and spiritual destiny of other people, the Hour which verse 187 has just been asked about, and all future events. Al-Ṭabarī notes that the argument here turns particularly on the future, which is the part of the unseen that would have been commercially and practically useful.",
            "The counterfactual's two halves answer the two things a person would want foreknowledge for. *I would have acquired much good* is the offensive use — knowing where advantage lies. *No evil would have touched me* is the defensive use — knowing where danger lies. The verse claims neither, and by claiming neither it makes the same disclaimer as the first clause, but now grounded in an argument rather than an assertion.",
        ]),
        ("What \"Much Good\" Means", [
            "The commentators differ on the phrase *much good*, and both readings are recorded. Al-Rāzī and al-Ṭabarī take it primarily as the accumulation of good works — a religious gain, measured in the register that survives death. The same authorities note that in theory it could also mean the acquisition of worldly benefits, and al-Zamakhsharī allows that reading as well.",
            "The ambiguity is not carelessness. The counterfactual works on either reading, and the report attached to the verse shows why the worldly one was live for the original audience. Al-Rāzī records that some of the Quraysh asked the Prophet ﷺ whether God had informed him of the times of rising and falling prices, so that they might profit from the information in their trading.",
            "That request is the verse's real occasion, and it explains the choice of example. They were not asking for prophecy about the Hour or for knowledge of the heart. They were asking for a market forecast, on the assumption that a man in contact with God would have an advantage in commerce. The answer given is that he has no such advantage and could not have one, because he does not know the future at all.",
            "It is worth noting what the verse does not do with this. It does not rebuke the question as impious. It answers it as a factual claim that happens to be false, and in answering it separates prophethood from advantage in the world so completely that a man who wanted a stock tip has been told, in the same breath, that the prophet cannot protect himself from harm.",
        ]),
        ("Naught but a Warner and a Bearer of Glad Tidings", [
            "The verse closes by stating what remains once power and foreknowledge have been disclaimed. *I am naught save a warner and a bearer of glad tidings unto a people who believe.* Two functions, and both are functions of speech.",
            "The pairing is one of the Qur'an's most repeated descriptions of the prophetic office — at 2:119 and 2:213, 4:165, 5:19, 6:48, 11:2, 17:105, 18:56, 25:56, 33:45, 34:28 and 48:8. Its recurrence across Madinan and Makkan sūrahs alike indicates that it is not a local answer to the Quraysh but the settled definition of the role.",
            "The definition is limiting in both directions. A warner cannot compel; a bearer of glad tidings cannot confer. Neither office includes the power to benefit or harm, which is what the first clause denied, nor the knowledge of outcomes, which is what the second denied. What is left is transmission, and the verse is content to leave exactly that.",
            "The final qualification — *unto a people who believe* — attaches to the glad tidings rather than to the warning, and the asymmetry is real. The warning is general; the good news has an addressee. The one who believes receives the tidings as tidings, and the one who does not hears the same words as a threat. The verse does not soften this. It says that the message is one thing and its reception is another, and that the second is not in the messenger's hands either.",
        ]),
    ]),

    # ------------------------------------------------------------------ 190
    190: (None, [
        ("From a Single Soul", [
            "The verse is the second half of a pair, and the first half supplies its premise. Verse 189 describes the creation of humanity from a single soul and the making of its mate so that he might find rest in her, and the commentators commonly identify the soul as Adam and the mate as Eve — al-Jaṣṣāṣ, al-Rāzī, al-Ṭabarī and al-Zamakhsharī all record that reading — while noting that the same terms can describe the generation of human beings from male and female spouses generally.",
            "The purpose of the pairing is stated in a word: *li-yaskuna ilayhā*, that he might find rest in her. The Qur'an says the same thing of marriage as one of God's signs at 30:21, *\"And among His signs is that He created mates for you from among yourselves, that you might find rest in them, and He established affection and mercy between you\"*, and see also 2:187. What is being described is emotional and physical comfort, and the source note is explicit that this is among the most important benefits of marriage — not merely the opportunity for procreation, which is named separately at 16:72.",
            "Al-Zamakhsharī draws the connection that makes verse 190 possible. To find rest in one's spouse means to enjoy love, peace and intimacy together, and this is natural in a specific sense: the spouses were made from a single soul. He maintains that love for a spouse is therefore similar to love for a child, insofar as both derive from the sense that the beloved is part of one's own being.",
            "That observation is the hinge of the pair. Verse 189 establishes a love grounded in shared substance; verse 190 records what happened when that love was given what it asked for.",
        ]),
        ("A Difficulty in the Reading", [
            "Taken as a story about Adam and Eve, verse 190 presents a problem the commentators face directly. Adam is a prophet in the Islamic tradition, and the verse says that when the healthy child was given, *they ascribed partners unto Him with regard to that which He had given them*. Ascribing partners is shirk. It is difficult to see how this narrative can concern Adam.",
            "Two solutions are recorded. Some commentators hold that when the verse turns to the ascription of partners it is no longer speaking of Adam and Eve but of their offspring — human beings generally — and that the shift is marked only by context. The difficulty with this is grammatical and the note records it: the verb tenses continue in the dual. The sentence does not change number where the reading requires it to.",
            "The second solution accepts the dual and changes the genre. On this reading the pair is not two named individuals but a type: a husband and a wife, any husband and any wife, and the narrative is a parable about what married people do when a prayer is answered.",
            "Given the considerations on both sides, this seems the most reasonable reading, and it costs nothing exegetically. The parable loses no force by being general; if anything it gains, because a story about one couple in the distant past can be set aside while a story about every couple cannot.",
        ]),
        ("The Parable of the Answered Prayer", [
            "What the parable describes is a specific and common failure, and it has a precise sequence. The couple, having been given a light burden and then grown heavy with it, call upon God that the child be healthy and sound. They are helpless and afraid, and in that state they address God alone. The prayer is answered. The child is born healthy. And then — in the verse's own transition, *fa-lammā ātāhumā ṣāliḥan*, then when He gave them a healthy child — they ascribe partners to Him with regard to the very thing He gave.",
            "The ascription need not be a statue. It is the attribution of an answered prayer to some other cause: the physician, the timing, the family's merit, the remedy, one's own management of the pregnancy. The blessing arrives and the account of how it arrived quietly stops ending with God.",
            "The Qur'an describes this movement often enough that the commentators treat it as a pattern rather than an incident. See 6:63–64, where God is called upon in distress and then forgotten when the distress is lifted; 10:22–23, the same sequence at sea; 17:67, harm at sea and turning away on reaching land; 29:65, sincerity in the crisis and shirk in the safety; 30:33 and 31:32, both turning to God under pressure and then associating once delivered.",
            "The last two are worth reading alongside this verse because they name the mechanism. In 31:32 the wave passes over them and they call upon God sincerely; when He brings them to shore, some of them take a middle course. Sincerity under threat is easy and is not credited as virtue. The test is what the same person says when the threat has gone and the good has arrived.",
        ]),
        ("Exalted Above What They Ascribe", [
            "The verse ends by stepping out of the narrative and saying something about God directly. *Exalted is God above the partners they ascribe.* The formula is a declaration of transcendence — *taʿālā* — and it does not argue with the ascription. It states that God is above it.",
            "The same closing formula recurs at 9:31, where it answers the taking of rabbis and monks as lords beside God; at 10:18, where it answers the intercessors the idolaters claim; and at 16:1 and 16:3. In each case it follows a description of a specific ascription and refuses to engage with it on its own terms.",
            "That refusal is the verse's final word on the parable. The couple's error is not answered by a proof that no partner exists, or by a listing of what God did and the causes did not. It is answered by a statement about God's height, which makes the ascription not false so much as beneath the subject. The partners are not rivals who lost; they are not in the same order of being as the thing they were set beside.",
            "Read with verse 189 the pair forms a complete arc. Love grounded in a shared soul asks God for a child; God gives the child; the receiving of the gift becomes the occasion for misdescribing its source; and the verse closes by placing God above the misdescription. Nothing in the arc is unusual, which is why it is told of everyone.",
        ]),
    ]),

    # ------------------------------------------------------------------ 197
    197: (None, [
        ("The Second Statement of the Same Fact", [
            "This verse says what verses 191 and 192 have already said, and the saying again is the point. Those verses put the matter as two questions — *Do they ascribe as partners those who created naught and are themselves created? Those who can neither help them, nor help themselves?* — and this verse puts it as a statement, in the indicative, addressed directly.",
            "The shift from question to declaration is a shift in what is being asked of the hearer. A rhetorical question invites agreement; a statement requires only that it be heard. By the third telling the argument is no longer being made but registered, which is what a passage does when it considers a point closed.",
            "It is also worth noting what the reiteration adds. The questions were about *them* — the partners the idolaters ascribe. This verse is about *you*: those whom *you* call upon. The general proposition has been turned into a second-person address, and the person being described as helpless is no longer a hypothetical but the hearer's own god.",
        ]),
        ("Neither You Nor Themselves", [
            "The two negations are ordered, and the order is the argument. *Can neither help you, nor help themselves.* The first is what the worshipper needs and does not have. The second is what removes any remaining excuse for supplying it.",
            "A being unable to help its worshipper might still be worth petitioning if it were powerful in itself and merely constrained — a friend at court, an intermediary with access. The second negation closes that possibility. These objects cannot help themselves. Whatever is happening to them, they cannot alter; whatever is done to them, they cannot prevent.",
            "The comparison the verse forces is therefore not between the idols and God but between the idols and the people worshipping them, and it comes out against the idols. The worshipper can act on his own behalf. The thing he worships cannot. Verse 195 makes the same point physically — no feet to walk on, no hands to grasp, no eyes to see, no ears to hear — and this verse makes it in terms of agency.",
            "Ibn Kathīr and al-Māwardī treat the sequence as the sūrah's central argument against shirk precisely because it does not require the hearer to grant anything about God. It requires only that he look at what he is looking at.",
        ]),
        ("The Irony at 21:68", [
            "The Qur'an illustrates the reversal with a scene rather than an argument. When Abraham broke the idols and his people came to burn him for it, their cry is recorded at 21:68:",
            "> *\"They said: Burn him, and help your gods, if you would take action!\"* (21:68)",
            "The irony is complete and the verse states it in their own grammar. They are being asked to *help their gods* — the same gods they call upon for help. The direction of the relationship has been reversed by the arrival of one man with an axe, and the reversal exposes what the relationship always was.",
            "This is what verse 197 means by *nor help themselves*, and the story in Sūrah al-Anbiyāʾ is its narrative proof. A god that must be defended by its worshippers is not a god that can defend them. The people in that scene are not confused about the facts — they can see that the idols cannot act — and their cry shows that seeing the fact does not by itself end the worship.",
            "Which is why the passage returns to the point three times. The repetition is not for those who have not understood it but for those who have understood it and gone on anyway.",
        ]),
    ]),

}
