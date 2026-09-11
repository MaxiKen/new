# -*- coding: utf-8 -*-
"""011.md batch D: rewrite vv 7, 20, 29, 44 (template filler + fabricated Arabic).

These four carried the file's filler template ('The *second* *clause* states
the *word* that the *sūrah* gives with *particular* *weight*') with invented
Arabic transliteration that does not correspond to the verse. Their
translations were already correct, so only the commentary is replaced
(apply_sections.py is called with translation=None).

Rewritten from initial/011.md at the file's own depth (median 947 words).

Source apparatus: initial/011.md (R, Z, JJ, T, Ts, Kl; cross-refs 7:54c,
13:2, 2:171, 5:71, 6:52c, 46:23, 23:41, 8:59, 9:2-3, 24:57, 29:22, 35:44,
42:31, 46:32, 72:12, 7:38-39c, 17:75, 29:12-13, 33:66-68, 19:59)."""
SURAH = "Hūd"
NUM = 11

SECTIONS = {

7: (None, [
 ("Creation in Six Days — and the Throne Upon the Water", [
  "The verse opens with the act of creation: *wa-huwa lladhī khalaqa s-samāwāti wa-l-arḍa fī sittati ayyām* — \"He it is Who created the heavens and the earth in six days.\" The commentators direct the reader to 7:54c for the fuller treatment of the six days.",
  "The commentators note that the Qur'an's references to the six days of creation — 7:54, 10:3, 25:59, 32:4, 50:38, 57:4 — are often followed by the statement that God then mounted the Throne, as at 10:3, 25:59, and 32:4. The verse here is distinctive in placing the Throne before and during the creation rather than after it.",
  "The clause *wa-kāna ʿarshuhū ʿalā l-māʾ* — \"while His Throne was upon the water\" — has a biblical parallel at Genesis 1:2, and the commentators address its difficulty directly.",
  "Al-Rāzī's point is the crucial one: *upon* here cannot indicate physical space, since God's Throne could not be physically on the water if the heavens and the earth had not yet come into being. The water is not a surface beneath a situated object, because there is as yet no situated object.",
  "One reading the commentators offer is that the phrase indicates the manner in which the heavens came about without any physical support below them. The parallel is 13:2: *God it is Who raised the heavens without pillars that you see, then mounted the Throne.* On this reading the water signifies the absence of a supporting foundation rather than a foundation.",
 ]),
 ("\"That He May Try You\" — the Purpose Clause", [
  "The verse gives a purpose for the creation: *li-yabluwakum ayyukum aḥsanu ʿamalā* — \"that He may try you as to which of you is most virtuous in deed.\" The commentators note that the trial is the stated reason for the created order.",
  "The word *aḥsan* is the elative of *ḥasan* — good, beautiful. The verse does not ask which of you is obedient but which is *most* virtuous in deed, and the commentators read the elative as indicating that the trial concerns quality and not merely compliance.",
  "The object is *ʿamal* — deed, action. The commentators connect this to the sūrah's insistence, at v. 111, that payment will be for deeds. The trial announced here is settled by the same criterion.",
  "The placement is significant. The purpose clause attaches to the creation of the heavens and the earth, not to a later stage. The commentators read this as indicating that the cosmos is constituted as a testing ground from the outset rather than repurposed as one.",
 ]),
 ("\"If Thou Sayest You Shall Be Resurrected\"", [
  "The verse turns abruptly: *wa-laʾin qulta innakum mabʿūthūna min baʿdi l-mawt* — \"yet if thou sayest, 'Truly you shall be resurrected after death.'\" The commentators note the conditional form and the shift from cosmology to proclamation.",
  "The address is to the Prophet in the singular, and the commentators read this as placing him in the position of the one who announces what will not be accepted. The verse does not describe a hypothetical; it describes what happens when the announcement is made.",
  "The content of the announcement is resurrection — *mabʿūthūna min baʿdi l-mawt*. The commentators note that this is the specific claim the disbelievers reject, and that the sūrah returns to it throughout.",
  "The conditional *laʾin* anticipates the response, and the verse supplies it immediately. The structure makes the rejection feel automatic, as though the announcement and the refusal were a single event.",
 ]),
 ("\"This Is Naught but Manifest Sorcery\"", [
  "The disbelievers' answer is *in hādhā illā siḥrun mubīn* — \"this is naught but manifest sorcery.\" The commentators note the restriction in *in ... illā* — \"nothing but\" — which forecloses any other explanation.",
  "The word *siḥr* is significant. The commentators observe that the charge is not that the Prophet is lying but that he is practising deception by art. The distinction matters: a liar says what is false; a sorcerer makes the false appear compelling.",
  "The adjective *mubīn* — manifest, clear — is applied to the sorcery. The commentators read this as the disbelievers' way of saying that the deception is obvious, that anyone can see through it. The irony the verse leaves standing is that they have just demonstrated they cannot.",
  "This charge recurs throughout the Qur'an against the prophets, and the commentators connect it to the sūrah's other narratives. In each case the messenger is met not with argument but with a diagnosis of his person.",
 ]),
 ("The Verse as the Sūrah's Thesis in Miniature", [
  "Verse 7 contains the whole argument of the sūrah in a single sentence. The creation establishes God's power; the purpose clause establishes the trial; the announcement states the resurrection; the response records the refusal.",
  "The commentators read the sequence as programmatic. What follows across the next hundred verses is the working out of each element — communities tried, messengers announcing, notables refusing with charges against the messenger's person.",
  "The connection between the creation and the trial is what gives the sūrah its shape. The commentators note that the cosmos is not a backdrop to the trial but its instrument: the six days and the Throne are what make a testing ground possible.",
  "The verse also answers, in advance, the objection that resurrection is incredible. The one who made the heavens and the earth in six days, with the Throne upon the water before there was any support, is not short of power to raise the dead. The disbelievers' charge of sorcery is a refusal to make that connection.",
 ]),
])

,
20: (None, [
 ("\"They Cannot Thwart [Aught] on Earth\"", [
  "The verse opens with a statement of incapacity: *ulāʾika lam yakūnū muʿjizīna fī l-arḍ* — \"such as these cannot thwart [aught] on earth.\" The commentators explain that this means the disbelievers will not be able to prevent God's punishing them in this life if He wishes to do so.",
  "Al-Zamakhsharī's gloss is the operative one. The thwarting denied is not abstract resistance but the specific ability to escape punishment in this world. The commentators supply the parallels: 8:59, 9:2–3, 24:57, 29:22, 35:44, 42:31, 46:32, and 72:12.",
  "The phrase *fī l-arḍ* — \"on earth\" — is what the commentators emphasize. The incapacity is located in this world, not in the hereafter. The disbelievers cannot flee, cannot hide, cannot arrange their circumstances so that the punishment misses them.",
  "This connects to the sūrah's narratives. Every community that rejected its messenger was destroyed within the world, and the verse generalizes the pattern into a rule.",
 ]),
 ("\"No Protector Apart from God\"", [
  "The verse continues: *wa-mā kāna lahum min dūni Llāhi min awliyāʾ* — \"and they have no protector apart from God.\" The commentators note that God's being the only Protector for human beings is a common Qur'anic refrain.",
  "The parallels are extensive: 2:107, 2:120, 4:123, 4:173, 9:74, 9:116, 29:22, 33:18, 33:65, 42:31, and 48:22. The commentators read the recurrence as establishing a fixed theological claim rather than a contextual remark.",
  "The word *awlīyāʾ* is the plural of *walī* — protector, ally, one who stands near and acts on another's behalf. The commentators note that the negation is comprehensive: there are none besides God.",
  "The connection to the preceding clause is close. Those who cannot thwart punishment on earth also have no one to interpose. The two statements describe the same isolation from different angles — no escape and no advocate.",
  "The verse does not say the disbelievers have no protectors at all. It says they have none apart from God, which the commentators read as indicating that what they relied upon in place of God was never protection.",
 ]),
 ("\"The Punishment Will Be Multiplied\"", [
  "The verse states a doubling: *yuḍāʿafu lahumu l-ʿadhāb* — \"for them the punishment will be multiplied.\" The commentators explain the ground of the multiplication.",
  "Al-Jawzī's gloss is specific: they will be punished for their own misguided ways and also for misguiding others. The commentators supply the supporting passages: 7:38–39c, 17:75, 29:12–13, and 33:66–68.",
  "The principle is that leading others astray adds to the reckoning rather than distributing it. The commentators connect this to 29:12–13, where those who invite others to error bear their own burdens and burdens along with their own.",
  "The verse's context matters. It addresses the notables — those with standing who shaped their community's response. Their influence, which they treated as an asset, is what multiplies the punishment.",
  "The commentators note the contrast with the sūrah's treatment of the ordinary followers. In several narratives the leaders and the followers dispute in the Fire, and the leaders bear the greater share. The verse states the principle behind that pattern.",
 ]),
 ("\"They Were Not Able to Hear; Neither Did They See\"", [
  "The verse closes with a diagnosis: *mā kānū yastaṭīʿūna s-samʿa wa-mā kānū yubṣirūn* — \"they were not able to hear; neither did they see.\" The commentators note that the incapacity is stated as inability rather than refusal.",
  "Al-Rāzī's gloss is central: these words refer to a \"deafness of heart and blindness of soul.\" The commentators connect this to the Qur'an's consistent characterization of those insensible to the prophetic messages as blind and deaf.",
  "The supporting passages are numerous: 2:171, 5:71, 6:104, 7:64, 10:43, 11:28, 13:19, 27:4, 27:66, 27:81, 30:53, 41:17, 41:44, and 43:36–40. The commentators read the recurrence as establishing that the terms are technical rather than physical.",
  "The verb *yastaṭīʿūna* — \"were able\" — is worth noting. The commentators read the inability as acquired rather than innate. The disbelievers were not born deaf; they became unable to hear through the course of their refusal.",
  "This connects to the multiplication of punishment. The notables' influence shaped their community's sensibility, and the verse describes the result as a shared incapacity. The deafness is both the cause of the rejection and its consequence.",
 ]),
 ("The Verse in the Sūrah's Argument", [
  "Verse 20 concludes the description of those who desire the life of this world, begun at v. 15. The commentators read the sequence as moving from the desire, to its reward in this world, to its consequence in the next.",
  "The four clauses of the verse work together. No escape on earth; no protector; doubled punishment; and the incapacity that made the whole course possible. The commentators read the final clause as explaining the first three.",
  "The verse also prepares the transition that follows. Having described those who desired this world, the sūrah turns at v. 17 to those who stand upon a clear sign from their Lord. The contrast is between those who cannot hear and those who have something to hear.",
  "The pastoral edge is worth noting. The incapacity described is presented as a condition, and conditions can change. The commentators read the verse as a warning addressed to those who can still hear it.",
 ]),
])

,
29: (None, [
 ("\"I Ask Not of You Any Wealth\"", [
  "The verse records Noah's answer to his people: *wa-yā qawmi lā asʾalukum ʿalayhi mālan* — \"O my people! I ask not of you any wealth in return for it.\" The commentators explain that the *it* in *in return for it* refers to what Noah was calling his people to, namely faith in and sincere worship of the One God.",
  "Al-Ṭabarī's gloss fixes the referent. The refusal of payment is not a general statement about prophecy but a specific denial that the message is being sold. The commentators read this as answering an unspoken suspicion.",
  "The word *māl* — wealth, property — is concrete. The commentators note that Noah does not refuse an abstract reward but money, which is what the notables would have understood as the motive for a man gathering followers.",
  "The clause *in ajriya illā ʿalā Llāh* — \"my reward lies only with God\" — completes the statement. The commentators read the two halves together: no payment from the people, and a reward from God that does not depend on their acceptance.",
  "This is a recurring feature of the Qur'an's prophets. The commentators note the same formula in the mouths of Hūd, Ṣāliḥ, Shuʿayb, and the Prophet himself, and read the recurrence as establishing that the message is not a transaction.",
 ]),
 ("\"I Shall Not Drive Away Those Who Believe\"", [
  "The verse's central refusal is *wa-lā aṭṭaridu lladhīna āmanū* — \"and I shall not drive away those who believe.\" The commentators supply the occasion.",
  "Al-Ṭabarī records that the notables to whom Noah brought the message told him that if he wanted them to believe in him, he should shun those who were currently following him, because they were unworthy of being on equal footing with the notables. The commentators connect this to v. 27, where the notables describe the followers as the lowest among them.",
  "The request is a condition of belief, and Noah's refusal is unconditional. The commentators note that he does not negotiate the terms or propose a compromise; he states that he will not do it.",
  "The commentators observe that the Quraysh had the same issue with the Prophet's followers, and direct the reader to 6:52c. The parallel makes the verse a pattern rather than an isolated incident.",
  "The ground of the refusal follows: *innahum mulāqū rabbihim* — \"truly they shall meet their Lord.\" The commentators read this as the reason the followers cannot be dismissed. Their standing is not determined by social rank but by the meeting that awaits them.",
 ]),
 ("The Social Logic the Verse Refuses", [
  "The notables' request deserves examination, because it is not crude. They are not asking Noah to abandon his followers; they are asking him to separate them, so that the notables can associate with him without loss of status.",
  "The commentators read the request as an expression of a social order in which association is ranked. To sit with the lowly is to become lowly, and the notables are unwilling to accept that consequence.",
  "Noah's answer rejects the premise. The commentators note that he does not argue about the followers' worth or propose a separate gathering; he refuses the separation itself. The meeting with their Lord is what makes rank irrelevant.",
  "The verse thus addresses a recurring problem in religious communities. The commentators connect it to the sūrah's broader concern with the notables, who appear in nearly every narrative as the ones who refuse.",
  "The parallel at 6:52 is instructive, since there the Prophet is instructed not to drive away those who call upon their Lord morning and evening, seeking His face. The commentators read the two passages as making the same point from the prophet's side and God's.",
 ]),
 ("\"I See That You Are an Ignorant People\"", [
  "The verse closes with *wa-lākinnī arākum qawman tajhalūn* — \"but I see that you are an ignorant people.\" The commentators explain that this is in reference to the leaders' request that Noah should shun those who believed in God.",
  "The ignorance named is specific. The commentators read it as ignorance of what makes a person valuable — the notables do not know what they are asking Noah to dismiss.",
  "The verb *tajhalūn* is from the root *j-h-l*, which in Qur'anic usage carries the sense of acting without knowledge rather than merely lacking information. The commentators read it as describing a settled disposition.",
  "Al-Ṭabarī notes that the identical phrase is used by the prophet Hūd when addressing his people, at 46:23. The commentators read the repetition as indicating a standard prophetic response to this particular refusal.",
  "The verse ends on this note rather than on the refusal. The commentators read the placement as significant: Noah's final word to his people in this exchange is a diagnosis of their ignorance, not a restatement of his position.",
 ]),
 ("The Verse in the Noah Narrative", [
  "Verse 29 sits within the exchange between Noah and the notables that runs from v. 27 to v. 34. The commentators read the sequence as a negotiation that fails because the terms offered are unacceptable.",
  "The notables' position is stated at v. 27: we see you only as a human being like us, and we see only the lowest among us following you. Noah's answer at vv. 28–29 addresses both claims — he does not possess God's treasures, and he will not dismiss the followers.",
  "The verse's refusal is what makes the subsequent destruction intelligible. The commentators read the narrative as showing that the notables were not merely unconvinced but unwilling to accept the conditions on which belief was offered.",
  "The connection to the sūrah's opening is worth noting. Verse 7 described the trial as to which of you is most virtuous in deed. The notables' request would have made rank the criterion. Noah's refusal holds the verse's criterion in place.",
  "The pastoral application the commentators draw is direct. The verse addresses any community in which association is ranked and the lowly believer is treated as an embarrassment. Noah's answer is given as the standing response.",
 ]),
])

,
44: (None, [
 ("The Commands to the Earth and the Sky", [
  "The verse opens with two addresses: *wa-qīla yā arḍu blaʿī māʾaki wa-yā samāʾu aqliʿī* — \"and it was said, 'O earth! Swallow your water! And O sky! Hold back!'\" The commentators explain that God's commands to the earth and sky denote the end of the flood.",
  "The two commands are matched to the two sources of the water. The commentators note that the flood in the preceding verses came from the opened gates of the sky and the bursting springs of the earth, and that the reversal is addressed to each in turn.",
  "The verbs are precise. *Iblaʿī* — swallow — is used of the earth taking back what it released; *aqliʿī* — hold back, cease — is used of the sky's rain stopping. The commentators read the pairing as indicating a complete cessation rather than a reduction.",
  "The direct address to inanimate creation is characteristic of the Qur'an's flood narrative. The commentators note that the earth and sky are spoken to as addressees, which the tradition has read as indicating the immediacy of the command rather than a mediated process.",
  "The verse's abruptness is worth noting. After the extended narrative of the flood's onset, its end is given in a single sentence of two imperatives.",
 ]),
 ("\"The Water Was Made to Recede, and the Command Was Carried Out\"", [
  "The verse continues with two passive statements: *wa-ghīḍa l-māʾu wa-quḍiya l-amr* — \"and the water was made to recede, and the command was carried out.\" The commentators note that both are stated as accomplished facts.",
  "The verb *ghīḍa* denotes water diminishing or being absorbed. The commentators read it as describing the water's withdrawal rather than its evaporation or drainage — the earth has swallowed what it released.",
  "The phrase *quḍiya l-amr* — \"the command was carried out,\" or \"the matter was decided\" — is what the commentators emphasize. The commentators note that the same phrase appears elsewhere in the Qur'an for the settlement of a decisive matter.",
  "The dual statement is significant. The water's recession is the physical event; the carrying out of the command is its meaning. The commentators read the pairing as indicating that the flood was not a natural catastrophe but an executed judgment.",
  "The passive voice throughout removes any agent other than God. The commentators note that the verse does not describe the process by which the water receded, only that it did and that the command was fulfilled.",
 ]),
 ("\"It Settled on [Mount] Jūdī\"", [
  "The verse names the resting place: *wa-stawat ʿalā l-jūdī* — \"and it settled on [Mount] Jūdī.\" The commentators record the disagreement about the mountain's location and preserve it.",
  "Al-Jawzī and others report that in some traditional sources Jūdī, where the Ark settled, is a mountain near Mosul. The commentators note that other sources associate it with Mount Ararat in the eastern region of present-day Turkey.",
  "The disagreement is left open. The commentators do not resolve it, and the verse itself gives no geographical specification beyond the name.",
  "The verb *istawat* — settled, became level — is worth noting. The commentators read it as indicating that the Ark came to rest rather than landed, and that the water's recession left it grounded.",
  "The naming of a specific mountain is unusual in the Qur'an's flood narrative, which is otherwise sparing of geographical detail. The commentators have read this as anchoring the account in a place the hearers could locate.",
 ]),
 ("\"Away With the Wrongdoing People\"", [
  "The verse closes with *wa-qīla buʿdan li-l-qawmi ẓ-ẓālimīn* — \"and it was said, 'Away with the wrongdoing people!'\" The commentators note the form of the statement: *buʿdan* is a noun of distance used as an imprecation.",
  "Al-Rāzī records the belief that this was spoken by God. The commentators note the parallel at 23:41, where the identical phrase appears in the account of the destruction of Thamūd.",
  "The placement is striking. The imprecation comes after the Ark has settled — after the deliverance is complete. The commentators read the sequence as significant: the judgment is pronounced once the saved are safe.",
  "The word *ẓālimīn* — wrongdoers — is the sūrah's consistent term for the destroyed communities. The commentators note that it appears throughout the Noah narrative and that the verse uses it as the final word on the people.",
  "The imprecation is not addressed to the people but about them. The commentators read this as indicating that the address has ended; there is no further exchange between God and the destroyed community.",
 ]),
 ("The Verse as the Narrative's Resolution", [
  "Verse 44 concludes the flood narrative that begins at v. 36. The commentators read its compression as deliberate: after eight verses of warning, refusal, boarding, and rising water, the resolution is given in a single verse.",
  "The verse contains the whole reversal. The waters that rose are commanded down; the Ark that floated is settled; the people who refused are dismissed. The commentators read the sequence as a complete undoing of the flood's conditions.",
  "The connection to v. 43 is instructive. There the water rose and the Ark ran, and Noah's son refused to board. The verse here resolves both — the water recedes and the son is among those dismissed.",
  "The commentators note that the verse sets the pattern for the sūrah's remaining narratives. In each case the destruction is stated briefly after the warning is refused, and in each case the saved are distinguished from the destroyed.",
  "The final imprecation does pastoral work. The commentators read it as addressing the present audience: the distance pronounced on the wrongdoers is available to be avoided, and the sūrah's remaining narratives show how.",
 ]),
])

}
