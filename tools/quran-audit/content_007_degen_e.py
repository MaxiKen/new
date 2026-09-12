#!/usr/bin/env python3
"""Rebuild of four further degenerate sections of expanded/007.md.

Continues content_007_degen_a.py through _d.py. Measured before this rebuild:

    v193 0.091   v183 0.089   v202 0.089   v147 0.088

All four are the mixed case: substantial apparatus content buried inside
tautological frames. v183 in particular sits on one of the densest cross-
reference clusters in the sūrah (fourteen parallel verses on respite and
scheming) and was reduced almost to nothing by the loops. Rebuilt from
initial/007.md with the surviving material kept and the loops dropped.

Citations verified against extract_source.py before writing: 2:6, 36:10,
7:179, 7:195, 3:54, 86:15, 2:14, 18:105, 10:52, 27:90, 7:199, 7:201.
"""

SURAH = "al-Aʿrāf"
NUM = 7

SECTIONS = {

    # ------------------------------------------------------------------ 193
    193: (None, [
        ("Called to Guidance, or Called for Guidance", [
            "The verse's first clause is grammatically ambiguous in a way the commentators take seriously rather than resolve. Al-Jaṣṣāṣ, al-Ṭabarī and al-Ṭūsī read it as calling the idols *to* guidance: if you call them to guidance, they follow you not — they do not respond, they do not come along, nothing happens on their side.",
            "Al-Zamakhsharī records the other direction. The call is not *to* guidance but *for* it: when one calls upon the idols for guidance, they do not respond to the request. The preposition carries the difference, and the difference is between asking them to walk and asking them to lead.",
            "The two readings converge on the same fact, which is why the note holds both. An object that cannot be called to guidance cannot supply it either. The verse is not distinguishing between two failures but describing one failure from the two positions in which a worshipper can stand — the one who would follow and the one who would be led.",
        ]),
        ("Why They Cannot Answer", [
            "The apparatus grounds the non-response in physical terms, referring back to verse 195. They cannot respond in any way because they do not have ears with which they hear; nor do they have faculties of intellect and speech. The inventory in that verse — feet to walk on, hands to grasp with, eyes to perceive, ears to hear — is not decorative. Each absent organ corresponds to a function a supplicant needs from the one addressed.",
            "Feet would allow the god to come when called. Hands would allow it to act. Eyes would allow it to see the condition of the one calling. Ears would allow it to hear the call at all. Verse 195 removes the organs; verse 193 states the consequence, which is that the call goes nowhere.",
            "The addition of intellect and speech goes beyond the physical list and closes the last gap. Even an idol granted ears would need understanding to grasp a request and voice to answer it. The commentators supply both absences together, so that no intermediate case remains — nothing that hears but cannot understand, nothing that understands but cannot reply.",
        ]),
        ("The Third Reading: Calling the Idolaters", [
            "Al-Ṭūsī records a further possibility, in which the pronoun shifts referent. *If you call them to guidance* may refer not to the idols but to the attempt to call the idolaters — those who ascribe partners to God, described in verses 190 through 192 — to guidance. On this reading the verse is about people, and the second half of the verse makes better sense of them than of stone.",
            "The apparatus then draws the two cases together with a phrase that does the exegetical work: *in either case, because of their inability or unwillingness to respond to this call*. Al-Ṭabarī is credited with the observation that it does not matter whether you call them or remain silent, and the reason given covers both objects at once. The idols fail from inability. The people fail from unwillingness. The outcome for the caller is identical, which is what the verse is about.",
            "That the two readings can be held simultaneously is a mark of the verse's construction rather than of loose commentary. The Qur'an frequently addresses an object of worship and its worshipper in the same breath, because the description of one is a description of the other. A people who cannot be called to guidance have already become like the things they call upon.",
        ]),
        ("Call, or Remain Silent", [
            "The second half of the verse states the indifference plainly: *It is the same for you whether you call them or whether you remain silent.* The formula is one the Qur'an uses of a fixed condition rather than a passing mood, and its recurrence shows it is a technical statement about a category of people.",
            "At 2:6 the same construction opens the description of those for whom warning is futile: *\"Truly it is the same for the disbelievers whether thou warnest them or warnest them not; they do not believe.\"* At 36:10 it is repeated almost word for word: *\"It is the same for them whether thou warnest them or warnest them not; they do not believe.\"* In both the addressee is the Prophet ﷺ and in both the point is that his effort does not change the outcome.",
            "Verse 179 of this sūrah supplies the metaphor the note points to. Such people are likened to cattle — hearts with which they do not understand, eyes with which they do not see, ears with which they do not hear. The comparison is the same one verse 195 makes of the idols, and its application to human beings is what makes the third reading available at all.",
            "It should be said clearly what this verse is not. It is not a licence to stop calling. The command to warn is given repeatedly and is not withdrawn here. What the verse removes is the expectation that the calling produces the result, and it removes that expectation so that the one calling does not mistake a lack of effect for a defect in the message or in himself.",
        ]),
    ]),

    # ------------------------------------------------------------------ 183
    183: (None, [
        ("Respite as the Instrument", [
            "This verse is the second half of a pair and cannot be read without the first. Verse 182 describes God leading them on little by little — by degrees — and verse 183 names the mechanism: *And I will grant them respite; truly My scheme is firm.* The respite is not the absence of the scheme. It is the scheme.",
            "Al-Ṭabarī explains the connection. That God shall lead them on by degrees refers to the various ways in which God leads astray those who disbelieve or do wrong as punishment for their disbelief and wrongdoing, and granting them respite is named first among them. The punishment is not postponed by the delay; the delay is how the punishment is administered.",
            "The same pairing appears across the Qur'an and the commentators list the parallels: 13:32, where respite is granted so that a people may take their fill; 22:44 and 22:48, where the city is given respite and then seized; and 35:8. But the closest parallel is 68:44–45, the passage the note directs the reader to first, and it is closest by a wide margin — it repeats this pair almost word for word:",
            "> *\"So leave Me with those who deny this discourse. We shall lead them on little by little, whence they know not. And I shall grant them respite; truly My scheme is firm.\"* (68:44–45)",
            "Two sūrahs, one sentence. The second half is identical and the first differs by a single phrase, and the difference is instructive: 68:44 opens with *leave Me with those who deny this discourse*, which turns what is here a description into a command addressed to the Prophet ﷺ. The mechanism is stated in the same words in both places; what surrounds it is not. That the note points to this passage first, ahead of the looser parallels, is a recognition of how exact the agreement is.",

            "The word *respite* here carries that whole shape. It is not patience and it is not mercy. It is time given to a thing so that the thing may complete itself.",
        ]),
        ("Making Wrongdoing Seem Fair", [
            "The apparatus records a second mode alongside respite, and the two work together. God leads astray by granting respite *or* by making their wrongdoing seem fair to them — see 3:14, 6:108 and 10:12 — so that they falsely assume they enjoy Divine favour and thus continue along this path toward their own punishment.",
            "The two modes answer each other. Respite supplies the external evidence: things are going well, the crops came, the enemy was defeated, the wealth increased. Making wrongdoing seem fair supplies the internal evidence: what we are doing seems right to us. A person holding both will not question either.",
            "That is the precision of the mechanism al-Ṭabarī describes. The punishment does not have to be felt as punishment while it operates. It has to be misread as favour, and the misreading is itself part of the operation. The verse's first person — *I will grant them respite* — is what makes this legible: the respite is claimed by God as His own act, not described as something that happened to occur.",
            "The pastoral consequence is uncomfortable and unavoidable. Prosperity is not evidence of approval. The Qur'an says this often enough that it is a settled point rather than a local one, and this verse states it in its sharpest form: the longest respite is granted to the people whose punishment is most certain.",
        ]),
        ("My Scheme Is Firm", [
            "The second clause — *truly My scheme is firm* — uses the language of plotting, and the Qur'an applies that language to God repeatedly. The note collects the references. That God schemes against the disbelievers and that His scheming is superior to theirs is alluded to at 7:99, 10:21, 52:42 and 86:15–17; the last opens with the human side of the same contest, *\"Truly they are devising a scheme\"*, before turning to the divine.",
            "Two further formulations state the comparison outright. At 3:54: *\"And they plotted, and God plotted. And God is the best of plotters.\"* At 8:30 the same sentence is spoken of the Quraysh's plan against the Prophet ﷺ. And at 13:42 plotting is assigned to God altogether — *unto God belongs plotting altogether* — with 14:46 in parallel and 27:50 also cited.",
            "The word translated *firm* describes a scheme that is settled, executed in order, and not subject to interruption. That is what distinguishes it from human plotting, which the same verses describe as real but outrun. The people in 3:54 do plot, and their plot is not dismissed as nothing; it is simply placed beside a better one.",
            "Read with verse 182 the two clauses form a single statement about time. Human plotting operates inside a short horizon and must hurry. Divine plotting does not hurry, because it has arranged for the other party to spend the interval confirming himself in error. The firmness of the scheme is what makes the respite safe to grant.",
        ]),
        ("Why the Verse Says This in the First Person", [
            "Most of the surrounding passage speaks of God in the third person or addresses the Prophet ﷺ. This verse switches. *And I will grant them respite; truly My scheme is firm.* The first person is emphatic and it is doing specific work.",
            "The work is to remove the ambiguity that respite otherwise carries. If prosperity were merely permitted, or merely unremarked, a person receiving it could suppose that nothing was being decided about him. The first person forecloses that. The respite is not a gap in divine attention; it is a declared act with a stated intention behind it.",
            "It also relocates the danger. The threat in this verse is not addressed to the people being granted respite — they are not warned here, and by the logic of the passage they will not hear a warning in time. It is addressed to the reader, who is being told how to interpret the prosperity of others and, more uncomfortably, his own.",
            "The prohibition the verse implies is stated explicitly elsewhere in this sūrah, at 7:99: *Did they feel secure from God's plotting? None feels secure from God's plotting, save the people who are losers.* That verse and this one are the two halves of one warning. Verse 99 forbids the feeling of security; verse 183 explains why the feeling arises at all and why it is dangerous. The scheme is not visible in its operation. It looks exactly like success.",
        ]),
    ]),

    # ------------------------------------------------------------------ 202
    202: (None, [
        ("Their Brethren", [
            "The verse opens on a pronoun whose antecedent the commentators work through. *Their brethren* — that is, the brethren of Satan, or satans, since Satan can be a collective reference to satans as a group. Al-Ṭūsī records that these may be a reference to the ignorant mentioned in verse 199, or to the idolaters in general, and directs the reader to 2:14 for the same construction.",
            "That verse supplies the idiom. The hypocrites, when alone with their satans, say *\"We are with you. We were only mocking.\"* The possessive — *their* satans — is what matters. The relationship is not between a person and a general tempter but between a person and the particular company he keeps, and the Qur'an treats that company as an extension of him.",
            "The same possessive governs this verse and it is doing the same work. These people have brethren. The brethren are not strangers who accost them but associates whose company they have chosen and maintained, and verse 201 has just described the alternative — the reverent, who are touched by a visitation from Satan and then remember.",
            "The difference between the two verses is not that one group meets Satan and the other does not. Both meet him. The difference is what the meeting is called afterwards: a visitation in one case, brotherhood in the other.",
        ]),
        ("Drawn, Not Driven", [
            "The verb in the verse is one of movement, and al-Ṭabarī's gloss preserves its texture. Such people, in contrast to the reverent in verse 201, *allow themselves* to be drawn ever further into error; that is, they are literally helped along in their error by Satanic temptation.",
            "Two words in that gloss carry the argument. *Allow themselves* places the consent on their side. *Helped along* places the motion on the other side. Neither is sufficient alone, and the verse requires both — a pulling and a not-resisting.",
            "The phrase *ever further* describes direction rather than distance. Al-Ṭabarī explains that they err continuously, having no fear of God to give them pause. The absence of the pause is what converts a series of errors into a trajectory. Each step is small and each is taken in the direction of the last.",
            "This is the same structure verse 182 described at the level of divine action — leading on little by little. There the degrees are granted; here they are taken. The two verses describe one movement from opposite ends, and neither end is presented as coerced.",
        ]),
        ("And Then They Cease Not", [
            "The verse's final clause is grammatically unresolved, and the apparatus says so rather than choosing. Given the ambiguity of the pronouns in this verse, it may also mean that the satans do not cease in their attempts to lead such people further into error — al-Ṭabarī and al-Ṭūsī both record this reading.",
            "On the first reading the people do not cease: they continue in error without stopping. On the second the tempters do not cease: the attempts continue without stopping. The subject of the verb is not determined by the verse.",
            "The two readings are not in competition, because they describe a single continuous process from two sides. If the tempters never stop pulling and the tempted never stop yielding, there is no moment at which either clause could be false. The ambiguity is a feature of the description rather than a defect in it.",
            "What the clause adds in either case is duration. The earlier part of the verse describes a movement; this part says the movement has no internal stopping point. Nothing in the process generates its own interruption, which is why verse 201 had to supply one from outside.",
        ]),
        ("The Pair: Remembering, Then Seeing", [
            "Verse 202 is unintelligible without 201, and the two are best read as a single contrast. *Truly those who are reverent, when they are touched by a visitation from Satan, they remember; then behold, they see.*",
            "The reverent are described as *touched* — the same contact the brethren experience. The verse does not claim immunity for them. What it claims is a sequence: contact, remembrance, sight. The remembrance is the interruption, and the sight is what the interruption makes possible.",
            "Verse 202 has the same three positions and fails at the second. Contact occurs. Remembrance does not. And without remembrance there is no seeing, so the drawing continues — *ever further*, with no pause, because the pause was the thing remembrance would have supplied.",
            "The word translated *reverent* in 201 is the operative term. Al-Ṭabarī's gloss on 202 defines the brethren negatively by the same word: they err continuously, *having no fear of God to give them pause*. Reverence is not described here as a feeling of awe but as a mechanism — the thing that inserts a gap between a prompting and an action, and in that gap makes sight possible.",
            "Which is why verse 199's instruction fits where it does. *Take to pardoning, and enjoin right, and turn away from the ignorant.* The ignorant are those verse 202 calls brethren. The command is not to argue with them but to turn away, because the process described here has no point of entry from the outside — only from within, at the moment of remembrance, which another person cannot supply.",
        ]),
    ]),

    # ------------------------------------------------------------------ 147
    147: (None, [
        ("Two Denials Named", [
            "The verse identifies the people it concerns by two denials, and both are required. *As for those who deny Our signs and the meeting of the Hereafter.* The apparatus glosses the second: the meeting of the Hereafter refers to the Day of Resurrection and Judgment.",
            "The pairing is not redundant. Denial of the signs is a claim about evidence — that what has been shown does not establish what it was shown to establish. Denial of the meeting is a claim about accountability — that there is no occasion on which the matter will be reviewed. The first can be held by someone who still expects to answer for himself; the second removes that expectation entirely.",
            "The Qur'an treats the two together elsewhere and 18:105 is the closest parallel: *\"They are those who disbelieve in the signs of their Lord, and in the meeting with Him. Thus their deeds have come to naught, and on the Day of Resurrection We shall assign them no weight.\"* The same two denials, the same consequence, and the addition of a phrase — no weight — that explains what coming to naught means in the arithmetic of that Day.",
            "That the consequence follows both denials jointly is what makes the verse a statement about belief rather than about behaviour. It is not listing sins. It is naming the two convictions whose absence empties everything else of value.",
        ]),
        ("Their Deeds Have Come to Naught", [
            "The consequence is stated in a single clause: *their deeds have come to naught*. The apparatus unpacks it in three parts, and the three are distinct rather than interchangeable. They will not benefit from their deeds. They will not receive reward for them. Nor will their deeds, however seemingly good, be able to shield them from punishment for their denial and disbelief.",
            "The three answer three different hopes a person might place in a good deed — that it will advance him, that it will be credited to him, that it will protect him. The verse closes all three at once. What is left is a deed that happened and produced nothing.",
            "Elsewhere it is said that disbelievers, idolaters, hypocrites, and those who persecute the prophets and the righteous will have their deeds come to naught, and the note collects the references: 2:217, 3:22, 5:5 and 5:53, 9:17, and 18:105. The list is deliberately mixed. It includes the outright disbeliever and the hypocrite who professes belief, the idolater and the persecutor of the righteous — four different positions, one outcome.",
            "That mixture is the point of the recurrence. The nullification is not attached to a particular kind of wrong but to a particular kind of absence, and the absence is the one named in the first half of the verse. A hypocrite's deeds come to naught for the same reason an idolater's do.",
        ]),
        ("However Seemingly Good", [
            "The apparatus's phrase *however seemingly good* is doing careful work and deserves to be held onto. The verse does not say that the deeds of these people were bad deeds. It says their deeds have come to naught, and the gloss insists the nullification applies even where the deed appeared good and even where it was good in its outward form.",
            "This is the hardest implication of the verse and it is not softened anywhere in the note. A person may have fed the hungry, honoured a guest, freed a captive, kept a trust — and the verse says none of it will benefit him, be rewarded, or shield him. The deeds are not described as false; they are described as void.",
            "The distinction between false and void matters. A false deed was never done. A void deed was done and counted for nothing, and the voidness attaches to the person rather than to the act. That is why the verse opens with who these people are — those who deny the signs and the meeting — before saying what happens to their deeds. The condition of the doer determines the value of the doing.",
            "18:105 states the same conclusion in the language of weighing: *on the Day of Resurrection We shall assign them no weight*. The image is a scale, and the verse is not saying the deeds are light. It is saying they are not placed on it.",
        ]),
        ("Are They Recompensed for Aught Save What They Used to Do?", [
            "The verse closes with a rhetorical question, and its function is to deny injustice rather than to threaten. *Are they recompensed for aught save that which they used to do?* The expected answer is no, and the no is exculpatory of God.",
            "The formula is quoted elsewhere in the same words. At 10:52 it is put to the wrongdoers on the Day itself: *\"Then it shall be said unto the wrongdoers: Taste the punishment everlasting. Are you recompensed for aught save that which you used to earn?\"* At 27:90 the same question recurs. Its repetition across three sūrahs marks it as a settled formulation rather than a local turn of phrase.",
            "The question does two things at once. It asserts the exactness of the recompense — nothing is added to what they did, nothing arbitrary is inflicted. And it asserts the identity between the deed and its outcome, so that the punishment is not something imposed on their history but their history arriving at its term.",
            "Read against the first half of the verse the closing question completes an argument that could otherwise seem merely punitive. Their deeds have come to naught; they are recompensed only for what they used to do. The two clauses together say that the nullification is not a subtraction from what they earned but the shape of what they earned. Denial of the meeting with God is a deed like any other, and this verse reports its wage.",
        ]),
    ]),

}
