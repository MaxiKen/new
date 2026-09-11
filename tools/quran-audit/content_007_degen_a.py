#!/usr/bin/env python3
"""Rebuild of the most degenerate sections of expanded/007.md (Sūrah al-Aʿrāf).

These sections were structurally valid and about the right verse, so no gate
flagged them; they failed on prose quality. Each carried the circular
"the X is the X that is the Y" construction repeated until the section became
word-salad. Measured 10-gram duprates before this rebuild:

    v206 0.200   v141 0.145   v204 0.143   v137 0.118

All four are rebuilt from the apparatus in initial/007.md.
"""

SURAH = "al-Aʿrāf"
NUM = 7

SECTIONS = {

    # ------------------------------------------------------------------ 137
    137: (None, [
        ("The Inheritance Given to the Oppressed", [
            "The verse closes the Exodus narrative in this sūrah by naming who ends up holding the land. *Mustaḍʿafūn* — \"those who were oppressed\" — comes from the root ḍ-ʿ-f, \"weakness.\" The form is not passive but reflexive-intensive: it describes people who were *held* in weakness, deliberately kept weak by someone stronger. Pharaoh's system did not merely happen to disadvantage the Israelites; it was engineered to keep them feeble, and the Qur'an elsewhere records his method in blunt terms: he \"slew their sons and spared their women\" (28:4). Weakness imposed from outside is what the word carries.",
            "That this same word describes the inheritors is the theological point of the verse. The land is not awarded to the militarily strongest, the most numerous, or the most politically accomplished. It is bequeathed to the people who were kept weak and who nevertheless held. God's bequest runs in the opposite direction from conventional power, and the verse says so by choosing the very term the oppressor used to define his victims.",
        ]),
        ("Patience as the Condition of the Promise", [
            "> *And the most beautiful Word of thy Lord was fulfilled for the Children of Israel because they were patient.*",
            "The causal particle matters. Fulfilment came *because they were patient* (ṣabarū). Al-Ṭabarī reads the verse as the direct realisation of what Moses told his people in verse 128 — \"Seek help in God and be patient\" — so the sūrah answers its own earlier command within nine verses. The promise was not a guarantee that patience would be unnecessary; patience was the mechanism by which the promise operated.",
            "This is worth stating plainly, because it is easily misheard. Ṣabr is not passivity. It is the refusal to abandon a position under pressure, which is an active discipline sustained over time. The Israelites did nothing to part the sea. What they did was continue to hold onto God's word through years of infanticide, forced labour, and ridicule — the period when holding on looked like nothing at all. The verse credits exactly that.",
            "Read generally, as many commentators do, the principle extends beyond one historical case: whoever meets adversity with patience and the expectation of Divine succour will be granted deliverance. The historical instance is the proof-of-concept, not the limit of the rule.",
        ]),
        ("Which Land Was Blessed", [
            "Commentators differ on the referent of *the land that We blessed*, and the disagreement is instructive rather than merely geographical. Al-Ṭabarī and al-Ṭabarsī take it to be Syria and Palestine (Shām), because that is the region the Qur'an elsewhere ordains for the Israelites: \"O my people! Enter the holy land which God has ordained for you\" (5:21). Al-Rāzī records others who take it to be Pharaoh's own domain in Egypt, and a third position holds that both are intended.",
            "The ground for calling it blessed is fertility and abundance — the land is blessed in the concrete sense of producing. But the Qur'an is careful not to make the blessing an exclusive ethnic property. Of the same region it says elsewhere that it is holy and blessed for all peoples (21:71). Inheritance here is tied to a moral condition, not to descent, which is why the verse attaches it to patience rather than to lineage.",
            "The phrase *the eastern and western parts of the land* is best read as an idiom for the whole of it — east and west together meaning every direction, the complete territory rather than a partition of it.",
        ]),
        ("What Was Demolished", [
            "> *And We demolished all that Pharaoh and his people had wrought and that which they used to build.*",
            "Al-Ṭabarī, al-Ṭabarsī and al-Zamakhsharī take this as the destruction of palaces, gardens, fields and orchards. The verse distinguishes two things: what they had *wrought* (yaṣnaʿūn) and what they used to *build* (yaʿrishūn). The pairing covers both the products of their craft and the structures they raised — manufacture and architecture, the movable and the fixed.",
            "The theological weight falls on the futility. Pharaoh's entire claim to authority rested on visible, durable achievement; the Qur'an quotes his boast elsewhere, \"Do I not possess the dominion of Egypt and these rivers flowing beneath me?\" (43:51). The verse answers by recording that all of it was demolished. Monumental building is precisely the kind of thing a regime uses to argue for its own permanence, and the demolition is the argument against that claim.",
            "The practical lesson is not that building is wrong but that building cannot bear the weight people place on it. Anything made the proof of one's own indispensability is being asked to do work it cannot do, and the verse records what happens when the test is applied.",
        ]),
    ]),

    # ------------------------------------------------------------------ 141
    141: (None, [
        ("Remembrance as the Ground of Obligation", [
            "Moses continues his address by turning from a claim to a memory. He does not argue that God deserves worship in the abstract; he reminds the people of something that happened to them. *And when We saved you from the House of Pharaoh* — the verb is najjaynākum, \"We delivered you,\" in the form that stresses rescue from something actively threatening.",
            "This is a characteristic Qur'anic method and it is worth noticing how deliberate it is. Rather than opening with doctrine, the address opens with experienced history. A people who have been freed can be reasoned with about what freedom obliges; a people who have merely been told about God's goodness cannot. Gratitude is being asked for on evidence the audience supplied themselves.",
            "The parallel passages al-Rāzī cites — \"And when Moses said unto his people: Remember God's favour upon you\" (14:6) and \"O Children of Israel! Remember My favour wherewith I favoured you\" (20:80) — show the same structure recurring. Remembrance of a specific favour is the consistent premise for the demand that follows.",
        ]),
        ("The House, Not Only the Man", [
            "The verse says *the House of Pharaoh* (Āl Firʿawn), not Pharaoh alone. The choice widens the referent from one tyrant to an entire ruling establishment — his court, his officials, his military, the administrative machinery through which the oppression was actually carried out. No single person could slay a generation of children; that required a system with personnel, orders, and compliance.",
            "Naming the house rather than the man is therefore more accurate historically and more useful morally. It records that atrocity at this scale is institutional, and it prevents the comfortable reading in which one monstrous individual bears all the guilt while everyone who executed the policy disappears from the account. The Qur'an consistently treats Pharaoh's *mlaʾ* — his chiefs and council — as co-responsible, and they are the ones who advise him throughout this sūrah.",
        ]),
        ("Slaying the Sons, Sparing the Women", [
            "> *...who inflicted terrible punishment upon you, slaying your sons and sparing your women.*",
            "The word rendered \"terrible punishment\" is sūm — from a root meaning to make someone endure, to drive livestock hard, to impose. It carries the sense of repeated, grinding imposition rather than a single blow. What is described is not an atrocity that occurred once but a policy sustained across years.",
            "The cross-reference at 7:127 records the same policy earlier in the sūrah, and 28:4 gives its rationale: Pharaoh feared a people who might multiply and threaten him, so he weakened them by destroying their male children. Sparing the women is not mercy. It is the other half of a demographic strategy — keeping the population labouring and unable to recover. The verse names both halves because both were instruments.",
            "The horror here is administrative. It is a policy with an objective, which is what makes it worse than indiscriminate violence rather than better. The Qur'an's insistence on naming it precisely — sons slain, women spared — refuses to let the reader soften it into general suffering.",
        ]),
        ("Trial in Both Directions", [
            "> *And in this was a great trial from your Lord.*",
            "The word is balāʾ, which in Qur'anic usage covers both affliction and testing, and the ambiguity is intended. The persecution was itself a great trial: endured over years, it tested whether the community would hold. Al-Rāzī connects it to the deliverance recorded in the same verse — the rescue was equally a trial, because salvation imposes the obligation of gratitude and the risk of squandering it.",
            "That double edge is the reason the sentence sits where it does. Having named the atrocity and the rescue together, the verse refuses to let either be taken as the end of the matter. Suffering tests endurance; deliverance tests character. The sūrah will go on to show the Israelites failing the second test almost immediately — asking Moses for an idol before their feet are dry (7:138) — which is the working demonstration of why rescue is also called a trial.",
            "For the reader the point generalises. Neither hardship nor relief is self-interpreting. Both are conditions under which something about a person is disclosed, and the disclosure is not the same in the two cases.",
        ]),
    ]),

    # ------------------------------------------------------------------ 204
    204: (None, [
        ("Two Verbs Where One Would Do", [
            "> *And when the Qur'an is recited, hearken unto it, and listen, that haply you may receive mercy.*",
            "The verse pairs two near-synonyms, *hearken* (istamiʿū) and *listen* (anṣitū). Al-Ālusī and al-Ṭabarī hold that the pairing is for emphasis, and the emphasis is on the *care* with which the recited Qur'an is to be received — full attention given both to understanding its meaning and to reflecting on its teachings, with al-Qurṭubī and al-Zamakhsharī adding that reflection is incomplete without acting on what the text prescribes.",
            "The two verbs are not simply redundant, and the difference between them is where the instruction lives. Anṣitū connotes listening *silently*; commentators note it was particularly important while the Prophet himself was reciting. Istamiʿū is the wider act of attending. So the verse asks for attention and for quiet, and the quiet is not incidental — it is the condition under which attention becomes possible.",
            "The threefold shape al-Ṭabarī and al-Qurṭubī give the command is worth holding onto: hear, understand, act. Each stage depends on the one before it. A person who has not genuinely heard cannot understand; one who has not understood cannot act on it; and acting is what makes the hearing count. The verse compresses all three into a single instruction about listening.",
        ]),
        ("Silence in the Congregation", [
            "The verse has a concrete legal application that al-Ālusī, al-Ṭabarī, al-Ṭabarsī and al-Zamakhsharī all record: it governs the etiquette of communal prayer. Those praying behind the imām are to be silent and attend to the Qur'anic passages he recites — neither conversing with fellow worshippers nor reciting along with him.",
            "This is a good example of a Qur'anic command settling a practical dispute by addressing the underlying disposition rather than the surface behaviour. The question of whether the congregation recites aloud behind the imām was contested among the early jurists, and the verse is one of the principal texts cited in that discussion. What it establishes beyond the technical ruling is that the congregation's role during recitation is receptive, not performative.",
            "Some commentators extend the command past the prayer entirely: al-Ālusī, al-Qurṭubī and al-Zamakhsharī hold that attentive listening applies in any context where one hears the Qur'an recited. On that reading the prayer ruling is the clearest instance of a general discipline rather than its limit.",
        ]),
        ("Listening as Servitude", [
            "Two further readings push inward. Some Sufi commentators take silent, purely receptive listening as a means of developing pure servitude toward God — a practice in which the listener stops supplying anything and simply receives. Al-Ālusī frames it as coming into the Presence of God, who is the ultimate Speaker behind the recited words.",
            "That framing changes what listening is for. If God is the real Speaker, then the recitation is not a performance being evaluated but an address being received, and the appropriate posture is the one a person takes when someone of consequence speaks directly to him. The silence the verse requires is the silence of that posture.",
        ]),
        ("Why Mercy Follows Listening", [
            "The closing clause — *that haply you may receive mercy* — connects back to verse 203, where the Qur'an is itself described as a mercy. The logic is straightforward: mercy is present in the recited words, so attending to them is how one receives it. Ibn ʿAjībah states it compactly: \"mercy is the closest thing to the one listening to the Qur'an.\"",
            "The particle *laʿalla* (\"haply\", \"that perhaps\") is characteristic of Qur'anic usage for Divine outcomes. It marks the result as genuinely attainable while making clear that it is not mechanically produced. Listening does not compel mercy; it places a person where mercy is being given. The distinction matters, because it rules out treating the practice as a transaction with a guaranteed return.",
            "Practically, this describes something most readers recognise. A text can be read past repeatedly without landing, and then at some point attended to properly and change a person. The difference between those two events is not in the text. The verse is legislating the difference.",
        ]),
    ]),

    # ------------------------------------------------------------------ 206
    206: (None, [
        ("Those Who Are with Thy Lord", [
            "> *Surely those who are with thy Lord are not too arrogant to worship Him. And they glorify Him, and prostrate unto Him.*",
            "*Those who are with thy Lord* are understood by al-Rāzī and al-Zamakhsharī to be the angels. Their being \"with\" God is not spatial — it is nearness to His Mercy and Bounty. The sūrah closes, as it opened, by locating the whole of creation in relation to God, and the highest creatures in that order are described first as worshippers.",
            "The verse is the last in the sūrah, and its placement is deliberate. Al-Aʿrāf has spent two hundred verses on human refusal: the chiefs who rejected their messengers, Pharaoh's establishment, the people who demanded an idol before their feet were dry. The final verse answers all of it with the angels, who are under no such temptation and worship anyway.",
        ]),
        ("The Argument from the Greater to the Lesser", [
            "Al-Rāzī draws out the implication explicitly: if the angels, with their spiritual purity and nearness to God, are not too arrogant to worship Him, how can human beings — marked by spiritual imperfection and distance from God — be reluctant to worship Him?",
            "This is an argument from the greater to the lesser, and its force depends on getting the direction right. Worship is not a burden that lesser creatures can be excused from because it exceeds their capacity. It is a good that the highest creatures pursue without needing to. The angels have nothing to gain from it and lose nothing by it, which is precisely why their worship establishes that worship is not about extraction.",
            "The vice named here is *kibr* — arrogance, the same word used for Iblīs's refusal earlier in this sūrah. The Qur'an's diagnosis of unbelief is consistently that it is not an intellectual failure but a posture. Iblīs did not lack evidence; he declined to submit. The angels are set at the opposite pole: capable of the same refusal, and not making it.",
            "Al-Rāzī points to 4:172 as the parallel text — \"the Messiah will never disdain to be a servant of God, nor the angels who are near Him\" — where disdain (an yastankif) plays exactly the role arrogance plays here. Both verses treat worship as something the exalted are not above, and both identify the refusal as a matter of self-regard.",
        ]),
        ("Glorification and Prostration", [
            "The verse names two acts. They *glorify* Him — yusabbiḥūn, from s-b-ḥ, declaring God free of every deficiency. Constant angelic praise is a recurring Qur'anic theme, and al-Rāzī cites 13:13, \"the angels hymn the praise of their Lord,\" 39:75, \"thou seest the angels hymning the praise of their Lord,\" and 42:5, \"the angels hymn the praise of their Lord and ask forgiveness for those on earth.\"",
            "Then they *prostrate*. Al-Rāzī notes 16:49: \"And unto God prostrateth whatsoever is in the heavens and whatsoever is on earth, of beast and angel, and they are not arrogant\" — which repeats this verse's denial of arrogance and extends the prostration to all creation.",
            "The pairing of glorification with prostration joins the inward declaration to the outward posture. Tasbīḥ is said; sujūd is done with the whole body. The angels are described as doing both, which is the pattern the sūrah asks of its reader.",
        ]),
        ("A Verse of Prostration", [
            "Because this verse mentions prostrating, it is one of the fifteen verses known as the *sajdah* verses. They are marked in official Arabic texts of the Qur'an, indicating that Muslims should physically prostrate upon reciting them or hearing them recited — though this is not required by Islamic Law. See the note at 19:58.",
            "The arrangement is striking and it is not accidental. The final word of the sūrah describes prostration, and the received practice of the community is to enact it at that point. The text does not merely report that the angels prostrate; it becomes the occasion for the reader to do the same. Reading the last verse aloud in the prescribed way ends the sūrah with the reader on the ground in the posture the verse describes.",
            "That is the sūrah's whole argument in a single gesture. Two hundred verses of human refusal close with an invitation to join the angels rather than Iblīs, and the physical act is the answer the reader gives. The distinction between the two is not settled by what one believes about God but by whether one bows.",
        ]),
    ]),
}
