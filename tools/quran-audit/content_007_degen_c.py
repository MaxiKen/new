#!/usr/bin/env python3
"""Rebuild of the worst remaining degenerate sections of expanded/007.md.

Follows content_007_degen_a.py and _b.py, which cleared the four sections at
0.118-0.200. These three are the next band and are not repairable by stripping
formulaic frames, because the frames are not wrapping kernels -- the whole body
is the loop. Measured before this rebuild:

    v25  0.098   v162 0.099   v194 0.098

v25's surviving sentences are themselves degenerate ("the three stages are the
three stages of the same drama, and the drama is the drama that is in the form
of the state of the man"), which is why repair_degen.py classed them as content
and left them. v194 retained two informative sentences out of a whole section.
All three are rebuilt from the apparatus in initial/007.md.
"""

SURAH = "al-Aʿrāf"
NUM = 7

SECTIONS = {

    # ------------------------------------------------------------------ 25
    25: (None, [
        ("Three Clauses, One Place", [
            "The verse is built on a single repeated pronoun. *Fīhā* — \"therein\", \"in it\" — governs all three clauses, and the antecedent is the earth named in the command to descend that precedes it. Life is in it, death is in it, and the coming forth is from it. Nothing in the sequence happens anywhere else.",
            "That is the whole force of the construction, and it is easy to read past. The verse does not say that man will live, die and be raised; it says that all three will happen *in relation to one place*, and that the place is the same. The earth is not a corridor the human being passes through on the way to somewhere more important. It is the location of the beginning, the location of the end, and the location of the return.",
            "> *\"He said: Therein you shall live, and therein you shall die, and from there shall you be brought forth.\"*",
            "The third clause changes its preposition deliberately. The first two use *fīhā*, in it; the third uses *minhā*, from it. Life and death are contained by the earth; the rising is an emergence out of it. The same ground that closes over a body is the ground that gives it back.",
        ]),
        ("Who Is Being Addressed", [
            "The command to descend in verse 24 is plural — *ihbiṭū*, get down, all of you — and al-Ṭabarī reads it as addressed to Adam and Eve, to their future progeny, and to Iblīs together. The enmity named in the same breath, *each of you an enemy to the other*, is therefore not only a statement about the human being and the tempter but about human beings among themselves.",
            "The scope matters for what follows. Verse 13 had banished Iblīs from the Garden specifically: *Get down from it.* This command is wider — a descent from the celestial realm altogether — and it carries the whole human race with it. Verse 25 is what the descent leads to, and it is addressed to everyone who descended.",
            "The verse is also a statement of the terms. Nothing is negotiated; nothing is offered back. The three clauses are declarative, and the human being is told where his life will run and where it will end before he has taken a step.",
        ]),
        ("A Fall Read as Mercy", [
            "Some Sufi commentators read the whole sequence providentially, and even mercifully. Al-Jīlī and those who follow him note that the act of disobedience led to Adam's assumption of the vicegerency on earth, and that it opened a way of drawing near to God which is only available after distance has been experienced. Proximity that has never been lost is not the same thing as proximity recovered.",
            "Ibn ʿAṭāʾ Allāh, the eighth-/fourteenth-century Shādhilī master, put the principle in a single line of his *Ḥikam*:",
            "> *\"An act of disobedience that bequeaths humility and need is better than an act of obedience that bequeaths might and pride.\"* (Ibn ʿAṭāʾ Allāh, al-Ḥikam 96)",
            "The comparison is not between disobedience and obedience but between two outcomes. What is being weighed is what the act leaves in the soul. An obedience that produces self-sufficiency has lost the thing worship exists for; a fall that produces need has found it. On this reading the descent is not only a punishment but the condition of a perfection that was not reachable otherwise — because it requires repentance, and repentance requires something to return from.",
            "The same reading gives the fall a second consequence, on God's side rather than man's. It occasions the manifestation of an attribute that innocence would never have disclosed. Forgiveness is only manifest where there is something to forgive.",
        ]),
        ("The Second Account", [
            "This verse closes the second telling of the Adam narrative in the order of the muṣḥaf. The first is at 2:30–39; later accounts run at 17:61–65 and 20:115–24, and at 15:28–43 and 38:71–85 the same story is told of the first human being without naming him.",
            "The repetition is not redundancy, and the differences are where the meaning lies. Each account closes differently, and this one closes on the earth: on where the story's descendants will actually live, die and rise. The telling in Sūrah Ṭā Hā closes on the warning not to forget; this one closes on a geography.",
            "That is why the three clauses are worth taking as a unit rather than as a summary. The verse is the Qur'an's most compressed statement of the human condition — one place, three events, no exit from the sequence and no alternative venue for any of them.",
        ]),
        ("What the Sequence Forecloses", [
            "The order is fixed and no stage can be skipped. The man who hopes to arrive at the being-brought-forth without passing through the dying has misunderstood the verse; the one who hopes to live somewhere other than the earth has misunderstood it too.",
            "The practical weight of that is not morbid. A life lived on the assumption that it will end in the same ground it began in is a life in which the ground has a claim. The verse makes the earth a witness to the whole of a human career — present at the living, present at the dying, and the thing that hands the person back. It is not scenery.",
        ]),
    ]),

    # ------------------------------------------------------------------ 162
    162: (None, [
        ("What Was Commanded and What Was Said", [
            "The verse follows directly on the instruction at 7:161, which is unusually generous in what it gives and unusually precise in what it asks. The people are told to settle in the town, to eat of it wherever they wish, to say one word, and to enter the gate prostrating — and the forgiveness of their iniquities and an increase for the virtuous are attached to the doing of it.",
            "The word they were to say is *ḥiṭṭah*, rendered here as *remove the burden*. It is a single term and the command is to utter it. What the wrongdoers among them did was substitute another word for it, and the verse records the substitution without yet naming the substitute.",
            "The act is named in the commentary tradition *tabdīl* — substitution, replacement — and it is treated as a distinct offence rather than as a degree of ordinary disobedience. Refusing to do a commanded thing is *maʿṣiyah*: the command stands and the person fails it. Substituting is different in kind, because it asserts that something else will serve. The word is not declined; it is exchanged.",
        ]),
        ("Ḥiṭṭah into Ḥinṭah", [
            "Al-Zamakhsharī supplies the substitute. Rather than saying *ḥiṭṭah* and prostrating, he reports, they said *ḥinṭah* — wheat — and entered the gate on their backsides, in mockery. The two words differ by a single letter, and the change converts a plea for the removal of a burden into the name of a grain.",
            "The reading is famous and it is worth stating the objection the source note itself raises, because the objection is better than the wordplay. These words would not have been spoken in Arabic. The exchange depends on a phonetic near-identity that belongs to Arabic and not to the language the Israelites were speaking, so as an account of what was actually said it does not convince.",
            "What survives the objection is the shape of the act rather than the syllables. The report is doing exegetical work on the kind of substitution intended: a change small enough to be passed off as compliance, and derisive enough to undo it. Entering the gate on their backsides is the same gesture performed with the body instead of the tongue — the form of the command kept and its direction reversed.",
        ]),
        ("Why Substitution Is the Graver Thing", [
            "The commentators read the gate episode alongside the accusations of *taḥrīf*, distortion, levelled later in Sūrah al-Baqarah (2:75–79), and the connection is not incidental. If a received word may be exchanged for another, the exchange does not stop at that word. Ibn ʿĀshūr's formulation in the later tradition puts the stakes plainly: the sin of *tabdīl* is the declaration that the revelation's precise wording does not bind the hearer.",
            "That is why the punishment in this verse is not delayed to a later generation or generalised into a warning. It falls on the substitution itself. The verse is the first recorded instance in the Qur'an's Israel narrative of a received word exchanged for a substitute, and it is also the first instance of that exchange answered directly from heaven.",
            "The moral generalises without strain. Most departures from a command are not refusals. They are substitutions — a thing done in place of the thing asked for, close enough to be described as obedience by the person doing it. The verse treats that as the more serious case, not the more excusable one.",
        ]),
        ("Rijz: The Torment From Heaven", [
            "The word for what is sent down is *rijz*. In classical Arabic it denotes foulness, defilement, loathsome filth, and the Qur'an uses it of idolatry itself — 22:30: *\"So shun the filth of idols, and shun false speech\"* — and of wine, gambling, idols and the divining arrows together at 5:90, *\"a means of defilement, of Satan's doing\"*. In the account of Badr at 8:11 it names what the water sent from the sky removes: the defilement of Satan from the believers' hearts.",
            "The word is therefore doing double work here. Al-Ṭabarī and the commentators understand it in this verse as a punishment or an act of wrath, and the same term recurs in this sūrah at 7:134–35 for the plagues sent on Pharaoh's people and lifted again — and see also 29:34 and 34:5. But a punishment called *filth* is not merely a penalty. It is described as what it is: a defilement falling on people who had just defiled a command.",
            "> *\"So We sent down upon them a torment from heaven for the wrong they used to do.\"*",
            "Two features of the clause are worth marking. The torment comes *from heaven*, which answers the direction of the offence — the word was changed on the ground and the reply descends. And the reason given is *bi-mā kānū yaẓlimūn*, on account of the wrong they *used to* do: the imperfect with *kānū* describes a settled habit rather than a single lapse. The substitution was not an incident. It was their way of dealing with commands.",
        ]),
    ]),

    # ------------------------------------------------------------------ 194
    194: (None, [
        ("Servants Like You", [
            "The verse opens by reclassifying the objects of worship. They are not rivals to God, nor independent powers, nor intermediaries holding a share of the divine authority. They are *ʿibād* — servants, owned beings — and the qualification that follows is the one that stings: *like you*. *Amthālukum*. The worshipper and the thing worshipped belong to the same category.",
            "The point is not that the idols are evil or false in some dramatic sense but that they are junior. They belong to God and stand under His sovereignty, in the same standing as the people bowing to them. A servant who petitions another servant, over the head of the master who owns them both, has misdescribed the situation he is in.",
            "This is the sūrah's sustained argument against shirk reduced to a single word. Elsewhere the Qur'an disputes the *power* of the false deities; here it disputes their *status*, and the dispute over status is the more damaging of the two, because a being with no power might still be pitied or honoured while a being with the same rank as its worshipper cannot be addressed at all.",
        ]),
        ("The Challenge to Call", [
            "The verse then does something unusual: it grants the request. *So call upon them.* There is no prohibition issued and no argument offered. The idolaters are told to do exactly what they were doing, and to see what happens.",
            "> *\"Let them answer you, if you are truthful.\"*",
            "The conditional *in kuntum ṣādiqīn* — if you are truthful — is the hinge. Truthfulness here is not sincerity but accuracy: the claim that these beings can hear and respond. The verse proposes an empirical test of a metaphysical claim, and it proposes it in the imperative, which removes the excuse of not having tried.",
            "The challenge is structurally identical to the one the Qur'an puts to those who deny the resurrection — produce your proof, if you are truthful — and it works the same way. A claim that cannot survive being acted on was never a claim about the world. The verse does not need to refute the idolater; it needs him to make one phone call.",
        ]),
        ("Less Capable Than the Worshipper", [
            "Verse 195 presses the same advantage with a sequence of rhetorical questions that Ibn Kathīr and al-Māwardī treat as the core of the argument. Do the idols have feet to walk on? Hands to grasp with? Eyes to see by? Ears to hear with?",
            "The list is deliberately physical and deliberately descending. Feet, hands, eyes, ears — the equipment of an agent. The idols are not described as weak gods but as insensate objects, and the comparison being forced is not between them and God but between them and the person addressing them.",
            "That is the argument's real edge. How is it that a being with feet and hands and eyes and ears worships a thing with none? The worshipper outranks his god in every capacity the questions name. The verse is not asking the idolater to think more highly of God; it is asking him to notice that he is already, by a wide margin, the more capable of the two.",
        ]),
        ("Scheme Against Me, and Grant Me No Respite", [
            "The passage closes by turning the challenge from the idols to their worshippers, and the turn is addressed to the Prophet ﷺ himself. He is told to invite the full conspiracy: let them scheme against him together, and let them not give him a moment's respite.",
            "The formula is not new to this sūrah. Noah issues it at 10:71 and Hūd at 11:55, in both cases to a people who have the numbers and the intention to kill him, and in both cases the invitation is genuine rather than rhetorical bravado. At 77:39 the same challenge is put to the deniers on the Day of Judgment itself: *So if you have a scheme, then scheme against Me.*",
            "The reason a prophet can issue it is given elsewhere and does not depend on his own strength. Nothing in the heavens or the earth can thwart God — 35:44 — while God's own scheme holds even where He grants respite, which is the subject of verses 182 and 183 of this sūrah. The respite the disbeliever is enjoying is not evidence that the scheme against him has failed; it is the mechanism by which it is being completed.",
            "Read in sequence the two challenges are one argument. The idols cannot answer when they are called, and their worshippers cannot harm the one who calls them. The verse removes both the object of worship and the threat that protected it, and leaves the idolater with nothing to do and nothing to fear from.",
        ]),
    ]),

}
