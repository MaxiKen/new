#!/usr/bin/env python3
"""Rebuild of four further degenerate sections of expanded/007.md.

Continues content_007_degen_a.py through _e.py. Measured before this rebuild:

    v196 0.086   v182 0.085   v201 0.085   v154 0.080

v182 shares a joint apparatus note with v183, which was rebuilt in
content_007_degen_e.py. The two rebuilds are deliberately differentiated to
avoid creating fresh inter-section duplication: v183 carries the agency
(respite, the firm scheme, the plotting cluster, 68:44-45) and v182 carries
the manner (gradualness, unknowing, the 'seem fair' mode).

v201 is likewise differentiated from v202, rebuilt in _e.py: v202 treats the
brethren and the unceasing drawing, v201 treats the visitation, the
remembrance and the restored sight.

Citations verified against extract_source.py before writing: 6:154, 7:52,
7:150, 7:195, 10:71, 11:55, 35:44, 77:39, 85:22, 114:4.
"""

SURAH = "al-Aʿrāf"
NUM = 7

SECTIONS = {

    # ------------------------------------------------------------------ 154
    154: (None, [
        ("When the Anger Abated", [
            "The verse begins with a subsiding rather than an action, and the order matters. *And when the anger abated from Moses, he took up the Tablets.* The anger came first and it went away on its own terms; what Moses did followed the abatement and not the anger.",
            "The anger itself is described at verse 150, where Moses returns to his people angry and aggrieved, casts down the Tablets and seizes his brother by the head. The commentators note there that his anger was at his people but perhaps also at himself for having left them, and that his grief was both for their grave error and for having to cut short the intimate discourse with God. That is a compound state, and this verse reports its end.",
            "It is worth attending to what the verse does not say. It does not say Moses mastered his anger, or repented of it, or was rebuked for it. It says the anger abated — a verb of weather, describing something that passes. The Prophetic anger at idolatry is not treated here as a fault requiring correction but as a condition with a duration.",
            "What the verse does establish is that nothing is done inside that duration. The Tablets lie where they were cast. Moses waits, or rather the narrative waits, until the state has passed; and the first act recorded after it is an act of retrieval.",
        ]),
        ("He Took Up the Tablets", [
            "The retrieval is stated in a few words and the verse draws no attention to it, which is itself significant. Moses had cast the Tablets down in front of his people, in anger, at the moment of their worst failure. The gesture was public and it was destructive in appearance. Nothing in the intervening verses reports what became of them.",
            "And now he takes them up. The verse does not say they were broken, does not say they were intact, does not say he gathered fragments. It says he took up the Tablets, using the same object as before, and then immediately speaks of what is in them — *in their inscription lay a guidance and a mercy* — which requires that the inscription still be legible.",
            "The silence is best read as deliberate. The narrative has no interest in the physical fate of the Tablets because its interest is in what they contain, and the content is stated in the same sentence as the retrieval. Whatever happened when they fell, what is picked up is a text.",
            "There is also a correction implied in the gesture, though the verse does not name it. The Tablets were cast down at the people. They are taken up for the people — for *those who are in awe of their Lord*, as the second half of the verse specifies. The same object moves from being an expression of anger to being an instrument of mercy, and the movement is marked only by the verb.",
        ]),
        ("In Their Inscription", [
            "The word translated *inscription* is *nuskhah*, and the apparatus treats it at length because it is not a simple term. It generally denotes a written copy of something, but its root meaning relates to substituting one thing for another, particularly as regards a text. Both senses are live here and the commentators pursue both.",
            "Al-Qushayrī and al-Rāzī record the first consequence of the root meaning. On their reading *nuskhah* refers to new Tablets given to Moses, which contained a copy of what had been inscribed on the originals. The substitution is then literal: the first Tablets were replaced by second ones, and the second carry the same text.",
            "Al-Qushayrī records a second and broader reading, in which *nuskhah* refers to the notion that guidance and mercy were inscribed upon — or copied onto — the Torah Tablets from the heavenly Preserved Tablet, from which all Divine Revelation derives. See 85:22, where the Qur'an itself is described as *upon a Preserved Tablet*.",
            "On this reading the substitution runs the other way. The Tablets in Moses's hands are the copy, and the original is in heaven. Every revelation is a *nuskhah* in that sense, and the word does the same work here that it does in the technical vocabulary of the commentators when they speak of one text superseding another.",
            "The two readings are not mutually exclusive and the verse does not require a choice between them. What both preserve is that the Tablets are not self-originating. Their authority is derived — from an earlier set, on the first reading, or from a heavenly original, on the second.",
        ]),
        ("A Guidance and a Mercy", [
            "What the inscription contains is named in two words, and the pairing is a formula rather than a description. *A guidance and a mercy* — the same two nouns, in the same order, are used of the Torah and of the Qur'an alike, and the apparatus collects the instances: 6:154, 7:52, 16:64, 28:43, and 31:2–3.",
            "Two of these are close enough to quote. 6:154 speaks of the Book given to Moses: *\"Then We gave unto Moses the Book, complete for those who would be virtuous, as an exposition of all things, and as a guidance and a mercy.\"* And 7:52, earlier in this same sūrah, speaks of the Qur'an: *\"We have indeed brought them a Book, which We have expounded with knowledge, as a guidance and a mercy for a people who believe.\"*",
            "The agreement of the two descriptions is the exegetical point. Al-Ṭabarī and al-Zamakhsharī take the phrase simply as indicating that the contents of the Tablets — the Torah — contained guidance and mercy, and the fact that the Qur'an describes itself in the identical terms means the verse is making a claim about revelation generally, not about one book.",
            "The two nouns are not synonyms and their order is not arbitrary. Guidance directs; mercy receives. A text that guided without mercy would be a demand, and a text that showed mercy without guidance would be a comfort with no direction in it. The pairing describes what a revelation must be to be of use.",
            "The verse then restricts the benefit. Guidance and mercy lie in the inscription *for those who are in awe of their Lord* — the same qualification 7:52 makes in the words *for a people who believe*. The restriction is not a withholding. It is a statement about reception: the Tablets contain what they contain for everyone, and it reaches only the one who is in a condition to receive it.",
            "That condition is named here as awe, and it connects this verse to the one that follows in the narrative and to the sūrah's larger argument. Verse 157 will describe those who follow the unlettered Prophet they find written in the Torah and the Gospel. The Tablets are not a closed document; they are a guidance and a mercy that point onward, and the awe required to read them is the same awe required to follow what they point to.",
        ]),
    ]),

    # ------------------------------------------------------------------ 182
    182: (None, [
        ("Little by Little", [
            "The verse describes a manner rather than an event. *And as for those who deny Our signs, We shall lead them on little by little, whence they know not.* The phrase translated *little by little* is rendered by the commentators as *by degrees*, and the leading is gradual by definition — a thing done all at once could not be done by degrees.",
            "The graduality is not incidental to the mechanism but constitutive of it. Al-Ṭabarī explains that the leading on by degrees refers to the various ways in which God leads astray those who disbelieve or do wrong, as punishment for their disbelief and wrongdoing. The punishment is thus administered in instalments, and the instalments are what make it a punishment rather than a catastrophe.",
            "A catastrophe is survived or not. A series of small advantages is absorbed, and each one adjusts the person's estimate of his position slightly upward. The verse describes the second, and the reason it is worse is that the person undergoing it experiences improvement throughout.",
            "The same phrase appears in Sūrah al-Qalam at 68:44, in a sentence otherwise identical to this one, which is the parallel the apparatus directs the reader to first. Its recurrence indicates that this is a named way of acting rather than a figure chosen for the occasion.",
        ]),
        ("Whence They Know Not", [
            "The second clause is the verse's real subject. *Whence they know not* — the process is invisible to the people undergoing it, and the invisibility is stated as a fact about them rather than a limitation of the description.",
            "This is what distinguishes the verse from an ordinary account of divine punishment. Elsewhere the Qur'an describes a people seized and knowing they are seized — the cry at the moment of the drowning, the recognition when the punishment arrives. Here the knowledge is absent throughout. There is no point in the sequence at which the person being led can look at his situation and identify it.",
            "The clause also explains why the leading must be gradual. A sudden reversal would be visible; a slow one is not, because each step is measured against the step before it rather than against the beginning. The unknowing is produced by the little-by-littleness, and the two halves of the verse are therefore one mechanism described twice.",
            "It follows that no amount of reflection on the part of the person being led would disclose the situation to him, since the disclosure would have to come from outside the sequence. This is why verse 99 of this sūrah poses its question in the third person — *Did they feel secure from God's plotting?* — rather than the second. The people concerned are not being addressed. They could not hear it.",
        ]),
        ("Making Wrongdoing Seem Fair", [
            "The apparatus names two modes by which the leading is accomplished, and this verse is chiefly concerned with the second. The first is the granting of respite, which verse 183 states explicitly and which is treated there. The second is making their wrongdoing seem fair to them — see 3:14, 6:108 and 10:12 — so that they falsely assume they enjoy Divine favour and thus continue along this path toward their own punishment.",
            "The two modes operate on different surfaces. Respite changes the world around the person: his affairs prosper, his enemies are delayed, his wealth increases. Making wrongdoing seem fair changes the person: what he is doing begins to look right to him. The first supplies evidence from outside, the second removes the capacity to read that evidence correctly.",
            "Together they close the escape. A person whose circumstances are improving and whose conduct seems to him sound has no internal signal telling him that anything is wrong, and the verse's final clause says he has no external one either. *Whence they know not* is the summary of both.",
            "It should be said plainly that the verse attributes the making-seem-fair to God rather than to the person's own reasoning. This is not a description of self-deception in the ordinary sense, where a person might be argued out of it by a better argument. It is a description of a condition imposed as punishment, and the punishment is precisely that the condition cannot be argued with from inside.",
        ]),
        ("A Punishment That Does Not Feel Like One", [
            "Al-Ṭabarī's framing — leading astray *as punishment* for disbelief and wrongdoing — is the key to the verse, and it is easy to miss because the verse nowhere uses the word punishment. What it describes looks like favour from every available vantage point, including the vantage point of the person receiving it.",
            "The Qur'an elsewhere names the specific error of inference this makes possible, at 23:55–56: *\"Do they reckon that, [on account of] the wealth and the children that We have provided them, We hasten unto good for them? Nay, but they are unaware!\"* The question is put as a reckoning — a calculation the people have performed and got wrong. The answer denies not the provision but the inference drawn from it, and closes by saying they are unaware. The prosperity is real and the reasoning is false, and the falseness is not corrigible by the person holding it, which is what verse 182's *whence they know not* states as a condition.",
            "This is why the verse is addressed to the Prophet ﷺ and to the reader rather than to those it describes. Its function is not to warn the people being led — the mechanism excludes that — but to instruct the one watching. A community prospering is not thereby vindicated. A person succeeding is not thereby right.",
            "The instruction cuts both ways and the verse does not soften the second direction. The reader is being told how to interpret his own prosperity as well as anyone else's, and the interpretive difficulty is identical: from inside a sequence of small advantages, nothing is visible. The only vantage the verse offers is the one it occupies, which is outside.",
            "Verse 183 then supplies what this verse withholds — the first-person claim to the respite and the statement that God's scheme is firm. Read together the pair says that the invisibility of the process is not an accident of its gradualness but the design of it, and that the design has an author who announces Himself in the next verse.",
        ]),
    ]),

    # ------------------------------------------------------------------ 196
    196: (None, [
        ("The Answer to the Challenge", [
            "This verse cannot be read apart from the one before it, because it is the answer to a challenge the Prophet ﷺ has just been told to issue. Verse 195 ends with the command *Say: Call upon your partners* — and then, in the same verse, with the invitation *scheme against me, and grant me no respite*.",
            "The apparatus explains the challenge. It is that they try their best to thwart God and the mission of His Prophet. The invitation is issued to people who have just been shown that their gods have no feet to walk on, no hands to grasp, no eyes to perceive, no ears to hear — and who are then told to bring those gods and do their worst, immediately and without delay.",
            "Verse 196 is what the Prophet ﷺ says after issuing it, and its position is the point. He has invited the combined hostility of the city and its gods. The next sentence is not a calculation of the odds but a statement of who is on his side.",
            "The same challenge is put in the mouths of two earlier prophets, and the apparatus cites both. Noah at 10:71, addressing a people to whom his presence and his reminding have become grievous. And Hūd at 11:55, in words nearly identical to this verse's: *\"So scheme against me then, all together, and grant me no respite.\"* Three prophets, three peoples, one formula — and in each case the formula is followed by a statement of trust rather than by a withdrawal.",
        ]),
        ("My Protector Is God", [
            "The answer opens in the first person and names a single relationship. *Truly my Protector is God.* The word translated *Protector* is *waliyy*, carrying the senses of guardian, patron, ally and one who is close — the same root that governs the Qur'anic language of alliance and of God's nearness to the believer.",
            "The emphatic particle *truly* at the head of the sentence is doing work against an implied objection. The challenge of verse 195 invited the idolaters to act; the natural human response to having issued such an invitation is to look around for support. The verse begins by saying where the support is, and by saying it with emphasis.",
            "What the claim excludes is as important as what it asserts. It does not say *God is my Protector and so are my tribe, my companions, my followers*. The protection is named in the singular and attributed to one source, immediately after a challenge that would have made any human ally's contribution decisive.",
            "That the Prophet ﷺ is instructed to say this in his own voice, rather than having it said about him, is characteristic of the passage. Verses 194 to 196 are built as a series of things he is to say — call upon them, ask them whether they have ears, scheme against me, my Protector is God — and the sequence makes the final statement part of the challenge rather than a retreat from it.",
        ]),
        ("Who Sent Down the Book", [
            "The verse does not leave the claim bare. It qualifies the Protector with a relative clause: *God, Who sent down the Book.* The qualification identifies God by an act, and the act chosen is revelation.",
            "This is not the only act by which God could have been identified here. The surrounding passage has available to it creation, sovereignty, the sending of prophets, the destruction of prior peoples. The verse selects the sending down of the Book, and the selection is an argument.",
            "The argument is that the protection claimed is of a piece with the mission that provoked the challenge. The Prophet ﷺ has been threatened because of what he brought. He answers by naming as his Protector the one who sent him with it, so that the threat and the protection are referred to the same source. To scheme against him is to scheme against the sender, and verse 195 has already said what the idols can do about that.",
            "The Qur'an makes the same point directly at 35:44, cited by the apparatus in this connection: *naught in the heavens or upon the earth can thwart God*. The verse there follows a description of God's respite to a people who would have been seized for their deeds, and the conclusion drawn is that no scheme succeeds against Him. The protection claimed in verse 196 rests on that impossibility.",
            "It also answers 77:39, where God Himself issues the same challenge on the Day of Judgment — *\"So if you have a scheme, then scheme against Me!\"* — to those who have been given every provision and denied it. The invitation the Prophet ﷺ extends in verse 195 is an extension of one God will extend finally, and verse 196 states why both can be extended safely.",
        ]),
        ("He Protects the Righteous", [
            "The verse's last clause moves from the singular to the general. *And He protects the righteous.* Having named his own Protector, the Prophet ﷺ states a rule that includes him rather than a privilege that sets him apart.",
            "The shift is deliberate and it changes the character of the claim. A statement that God protects this prophet would be a report about one man's situation, which his opponents could accept while continuing to oppose him. A statement that God protects the righteous makes the protection conditional on a quality available to anyone, and places the Prophet ﷺ among those who have it rather than above them.",
            "It also relocates the ground of the contest. The idolaters' scheme is aimed at a person; the verse answers that the person is an instance of a class, and that what protects him protects the class. To prevail against him would require prevailing against the rule, and the rule is God's.",
            "The apparatus draws the contrast with verses 182 and 183, where God grants respite to those who deny His signs and His scheme is firm. The two passages describe the same divine acting from opposite sides. There, the disbelievers are given time and led on whence they know not. Here, the righteous are protected and know it, and say so. The difference is not in God's power but in who is being described and what they are aware of.",
            "That awareness is the verse's last word on the challenge. The idolaters are invited to scheme and to grant no respite; the Prophet ﷺ states that his Protector is the one who sent down the Book and who protects the righteous. He is not claiming to be untouchable. He is claiming to be on the side of a rule that does not depend on his being untouchable, and the claim is offered in the same breath as the invitation, which is what makes it a challenge rather than a comfort.",
        ]),
    ]),

    # ------------------------------------------------------------------ 201
    201: (None, [
        ("A Visitation", [
            "The verse's first term is technical and the commentators gloss it carefully. To be touched by a *visitation* from Satan — *ṭāʾif* — means to be tempted by him, and al-Zamakhsharī gives the lexical meaning as perhaps occurring in a dream or an apparition. The word denotes something that comes around a person, circles him, touches him from outside.",
            "The image is of a passing thing rather than a dwelling one. A *ṭāʾif* arrives; it does not take up residence. That is the first thing the verse establishes about the reverent — not that they are free of Satanic contact but that the contact has the character of a visit, with a beginning and an end.",
            "Al-Ṭabarī records two narrower identifications. Some consider the visitation here to refer to the impulse toward anger. Others take it as any Satanic insinuation — the *whispering* described at 114:4, *the evil of the stealthy whisperer* — that tempts one toward a moral or intellectual lapse.",
            "The second is the broader and it covers the first. What matters for the verse is that the temptation is specified as reaching the person from outside his own settled character. It is a whisper, an impulse, an apparition — something that comes to him, not something he is.",
            "This is why the verse can promise what it promises. If the temptation were the person's own disposition, remembering would be of no use. Because it is a visitation, there is a moment at which it can be met.",
        ]),
        ("They Remember", [
            "The response is a single verb and the apparatus expands it. The reverent *remember* — that is, they remember God, and in particular they remember the commands of God and the threat of His punishment — and so return to obedience. Al-Ṭabarī is credited with the gloss.",
            "The content of the remembering is specified rather than left general, and the two things named are complementary. The commands tell the person what he was about to do wrongly. The threat of punishment tells him what it costs. Neither alone produces the return; the verse requires both.",
            "The word itself — *tadhakkarū* — carries more than recollection. The note records that it can also mean to reflect or to take heed. The three senses describe one movement: something known before is made present again, and being made present it changes what the person does.",
            "That the remembering is of something *already known* is the verse's central claim about the reverent. They are not given new information at the moment of temptation. They recall what they had. The visitation works by making the known temporarily unavailable, and the remembrance works by making it available again.",
            "Al-Zamakhsharī adds the observation that turns a single event into a character. Remembering God in this way whenever one is tempted is, he says, the *regular habit* of the reverent. The verse is not describing a lucky recovery but a practiced one — a response so established that it fires before deliberation.",
        ]),
        ("Then Behold, They See", [
            "The verse's second stage is introduced with a particle of suddenness. *Then behold, they see.* Al-Ṭūsī explains that after remembering, the reverent are restored to sound judgment and guidance; al-Ṭabarī that they return to what is right and what God has commanded.",
            "The sight is therefore not new perception but recovered perception. Nothing is disclosed to them at this moment that they did not know before the visitation. What is restored is the ability to see what they know, which the temptation had removed.",
            "The sequence is the argument of the verse and it is not reversible. Remembrance first, then sight — not sight leading to remembrance. A person waiting to see clearly before he remembers will not see clearly, because the impairment is in the seeing. The verse places the recoverable act at the point where it can still be performed.",
            "The particle *behold* marks how quickly the second follows the first. There is no described interval of struggle, no negotiation, no gradual clarification. The remembrance happens and the sight is there. That immediacy is what al-Zamakhsharī's *regular habit* explains: a response this fast has been made fast by repetition.",
            "It also identifies what the temptation actually did. If sight returns at once upon remembrance, then sight was not destroyed but obscured — covered by something that could be removed by an act of recall. The *ṭāʾif* is a passing thing, and the verse treats it as one throughout.",
        ]),
        ("Those Who Are Reverent", [
            "The subject of the verse is *alladhīna ittaqaw*, those who are reverent, and the term deserves attention because the verse defines it operationally rather than by feeling. Reverence here is not described as awe, or as piety of temperament, or as the absence of temptation. It is described as what a person does when touched.",
            "The definition is given in three movements — contact, remembrance, sight — and the middle one is the whole of it. The reverent are not those who escape the visitation; verse 201 says plainly that they are touched. They are those in whom the touch produces a specific response.",
            "This makes the quality available rather than exceptional. The apparatus's two glosses on the visitation — the impulse toward anger, the whispering toward a moral or intellectual lapse — describe experiences nobody is without. What the verse claims for the reverent is not immunity from these but an established answer to them.",
            "Al-Ṭabarī's specification of what is remembered is the practical content of that answer. The commands of God and the threat of His punishment are not abstractions requiring scholarly access; they are what a person has already been taught, held ready for the moment a whisper arrives.",
            "The verse closes on the restored sight, and it is worth noting that nothing further is said. The reverent are not praised, not rewarded in the sentence, not distinguished by title. They see, and the seeing is the end of the matter — the return to what is right and what God has commanded, which is where the verse leaves them.",
        ]),
    ]),

}
