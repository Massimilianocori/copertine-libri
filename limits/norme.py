"""Dati curati a mano per "Statute of Limitations by State": termini, citazioni testuali, regole di decorrenza e di sospensione.

Ogni citazione ("testo", lista di frammenti nell'ordine in cui compaiono nella legge) è copiata dal testo ufficiale salvato in
raccolta/_grezzi/ (fonte = id in dati/fonti.json). genera.py si ferma se un frammento non c'è più; verifica.py lo ricontrolla con un
estrattore suo e rilegge il termine ("frase") dal testo di legge, poi lo confronta con quello stampato nelle pagine.
Letti tutti il 13/11/2026. Regola: nessuna cella senza un articolo letto che dica il termine (per questo manca Washington ×
wrongful death: il capitolo 4.20 RCW non scrive un termine suo).
"""

VERIFICATO_IL = "2026-11-13"

CAUSE = {
    "personal-injury": {"nome": "Personal injury", "breve": "personal injury", "titolo": "Personal Injury",
                         "data": "Date of the injury", "esempi": "car accidents, slips and falls, dog bites and other injuries caused by someone else"},
    "medical-malpractice": {"nome": "Medical malpractice", "breve": "medical malpractice", "titolo": "Medical Malpractice",
                             "data": "Date of the treatment, act or omission", "esempi": "claims against doctors, hospitals and other health care providers"},
    "wrongful-death": {"nome": "Wrongful death", "breve": "wrongful death", "titolo": "Wrongful Death",
                        "data": "Date of death", "esempi": "claims brought after a death caused by someone else's wrongful act or negligence"},
    "debt": {"nome": "Debt collection", "breve": "debt collection", "titolo": "Debt Collection",
             "data": "Date of default (missed payment) or last payment", "esempi": "lawsuits to collect credit card balances, written contracts and open accounts"},
    "breach-of-contract": {"nome": "Breach of contract", "breve": "breach of contract", "titolo": "Breach of Contract",
                            "data": "Date of the breach", "esempi": "written and oral agreements"},
    "property-damage": {"nome": "Property damage", "breve": "property damage", "titolo": "Property Damage",
                         "data": "Date of the damage", "esempi": "damage to a car, a house or other property"},
}


def V(etichetta, anni, fonte, cit, testo, frase, **extra):
    """Una variante del termine: etichetta, anni, fonte, citazione, frammenti testuali, frase che contiene il termine."""
    d = {"etichetta": etichetta, "anni": anni, "fonte": fonte, "cit": cit, "testo": testo if isinstance(testo, list) else [testo], "frase": frase}
    d.update(extra)
    return d


def E(titolo, spiega, fonte, cit, testo):
    """Un'eccezione o regola collegata: titolo, spiegazione breve (nostra), fonte, citazione, frammenti testuali."""
    return {"titolo": titolo, "spiega": spiega, "fonte": fonte, "cit": cit, "testo": testo if isinstance(testo, list) else [testo]}


REG_F = E("Federal rule on time-barred consumer debt",
          "Under the federal Regulation F, a debt collector must not sue or threaten to sue a consumer over a debt once the applicable statute of limitations has expired.",
          "cfr_1006_26", "12 CFR 1006.26(b)",
          "A debt collector must not bring or threaten to bring a legal action against a consumer to collect a time-barred debt.")

STATI = {}
CELLE = {}

# =====================================================================================================================  TEXAS
STATI["TX"] = {
    "nome": "Texas", "slug": "texas", "codice": "Texas Civil Practice and Remedies Code (Chapter 16 and Chapter 74)",
    "regole": [
        E("Minors and people of unsound mind",
          "If the person who has the claim is under 18 or of unsound mind when the claim accrues, that time is not counted. A disability that starts later does not stop the clock.",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.001",
          ["(1) younger than 18 years of age, regardless of whether the person is married; or (2) of unsound mind.",
           "(b) If a person entitled to bring a personal action is under a legal disability when the cause of action accrues, the time of the disability is not included in a limitations period.",
           "(d) A disability that arises after a limitations period starts does not suspend the running of the period."]),
        E("Defendant out of state",
          "Time while the person being sued is absent from Texas is not counted.",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.063",
          "The absence from this state of a person against whom a cause of action may be maintained suspends the running of the applicable statute of limitations for the period of the person's absence."),
        E("Death of a party",
          "The death of either side pauses the deadline for up to 12 months (less if an executor or administrator qualifies sooner).",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.062",
          "(a) The death of a person against whom or in whose favor there may be a cause of action suspends the running of an applicable statute of limitations for 12 months after the death."),
        E("Case filed in the wrong court",
          "If a case is dismissed because the first court had no jurisdiction, the time it was pending is not counted, provided it is refiled in the right court within 60 days.",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.064",
          "(2) not later than the 60th day after the date the dismissal or other disposition becomes final, the action is commenced in a court of proper jurisdiction."),
    ],
    "governo": [
        E("Claims against a Texas governmental unit",
          "Under the Texas Tort Claims Act, the governmental unit is entitled to notice of the claim within six months of the incident, separately from the deadline to sue.",
          "tx_cprc101", "Tex. Civ. Prac. & Rem. Code § 101.101(a)",
          "A governmental unit is entitled to receive notice of a claim against it under this chapter not later than six months after the day that the incident giving rise to the claim occurred."),
    ],
    "cambi": [],
}
CELLE["TX/personal-injury"] = {
    "varianti": [V("Personal injury", 2, "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.003(a)",
                   "(a) Except as provided by Sections 16.010, 16.0031, and 16.0045, a person must bring suit for trespass for injury to the estate or to the property of another, conversion of personal property, taking or detaining the personal property of another, personal injury, forcible entry and detainer, and forcible detainer not later than two years after the day the cause of action accrues.",
                   "not later than two years after the day the cause of action accrues")],
    "inizio": "The two years run from “the day the cause of action accrues”. The section does not define that day for an ordinary injury claim; when it falls can depend on the facts, and the calculator counts from the date you enter.",
    "eccezioni": [
        E("Asbestos and silica injuries",
          "For injuries from asbestos or silica, the claim accrues at the earlier of the exposed person's death or the service of a qualifying medical report.",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.0031",
          "(1) the date of the exposed person's death; or (2) the date that the claimant serves on a defendant a report complying with Section 90.003 or 90.010(f)."),
    ],
    "nota": "Injuries caused by a doctor or hospital are health care liability claims with their own rules in Chapter 74: see the medical malpractice page.",
}
CELLE["TX/medical-malpractice"] = {
    "varianti": [V("Health care liability claim", 2, "tx_cprc74", "Tex. Civ. Prac. & Rem. Code § 74.251(a)",
                   "(a) Notwithstanding any other law and subject to Subsection (b), no health care liability claim may be commenced unless the action is filed within two years from the occurrence of the breach or tort or from the date the medical or health care treatment that is the subject of the claim or the hospitalization for which the claim is made is completed;",
                   "within two years from the occurrence of the breach or tort")],
    "inizio": "Two years from the breach or tort, or from the date the treatment or hospitalization that is the subject of the claim is completed.",
    "repose": V("Statute of repose", 10, "tx_cprc74", "Tex. Civ. Prac. & Rem. Code § 74.251(b)",
                "(b) A claimant must bring a health care liability claim not later than 10 years after the date of the act or omission that gives rise to the claim.",
                "not later than 10 years after the date of the act or omission"),
    "eccezioni": [
        E("Children under 12",
          "A child injured before age 12 has until the 14th birthday. Otherwise, the section applies to everyone regardless of age or other disability, so the general minors rule in § 16.001 does not extend it.",
          "tx_cprc74", "Tex. Civ. Prac. & Rem. Code § 74.251(a)",
          "provided that, minors under the age of 12 years shall have until their 14th birthday in which to file, or have filed on their behalf, the claim. Except as herein provided this section applies to all persons regardless of minority or other legal disability."),
        E("Pre-suit notice (60 days) pauses the deadline for 75 days",
          "Written notice must be sent at least 60 days before suing. Notice given as the chapter requires tolls the deadline for 75 days.",
          "tx_cprc74", "Tex. Civ. Prac. & Rem. Code § 74.051",
          ["at least 60 days before the filing of a suit in any court of this state based upon a health care liability claim.",
           "(c) Notice given as provided in this chapter shall toll the applicable statute of limitations to and including a period of 75 days following the giving of the notice, and this tolling shall apply to all parties and potential parties."]),
    ],
    "senza_regole_stato": True,
    "nota": "Because § 74.251 applies “notwithstanding any other law”, the general Texas tolling rules listed on the Texas page may not apply to these claims in the same way. Ask a Texas attorney.",
}
CELLE["TX/wrongful-death"] = {
    "varianti": [V("Action for injury resulting in death", 2, "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.003(b)",
                   "(b) A person must bring suit not later than two years after the day the cause of action accrues in an action for injury resulting in death. The cause of action accrues on the death of the injured person.",
                   "not later than two years after the day the cause of action accrues")],
    "inizio": "The statute says the claim accrues on the death of the injured person, so the two years run from the date of death.",
    "eccezioni": [],
    "nota": "If the death resulted from medical care, Chapter 74 (two years, 10-year repose) can apply instead: see the medical malpractice page.",
}
CELLE["TX/debt"] = {
    "varianti": [
        V("Debt", 4, "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.004(a)(3)",
          ["(a) A person must bring suit on the following actions not later than four years after the day the cause of action accrues:", "(3) debt;"],
          "not later than four years after the day the cause of action accrues"),
        V("Open or stated account", 4, "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.004(c)",
          "and must bring an action on an open or stated account, or on a mutual and current account concerning the trade of merchandise between merchants or their agents or factors, not later than four years after the day that the cause of action accrues.",
          "not later than four years after the day that the cause of action accrues"),
    ],
    "inizio": "Four years from the day the claim accrues. For accounts between partners or merchants, the section says it accrues when the dealings between the parties cease. For a missed payment, when the claim accrues can depend on the contract; the calculator counts from the date you enter.",
    "eccezioni": [
        E("Debt buyers cannot sue after the deadline, and a payment does not revive it",
          "A debt buyer may not sue or start arbitration on a consumer debt after the four-year period. Once barred, a payment or a reaffirmation does not revive the claim.",
          "tx_fin392", "Tex. Fin. Code § 392.307(c)-(d)",
          ["(c) A debt buyer may not, directly or indirectly, commence an action against or initiate arbitration with a consumer to collect a consumer debt after the expiration of the applicable limitations period provided by Section 16.004, Civil Practice and Remedies Code, or Section 3.118, Business & Commerce Code.",
           "(d) If an action to collect a consumer debt is barred under Subsection (c), the cause of action is not revived by a payment of the consumer debt, an oral or written reaffirmation of the consumer debt, or any other activity on the consumer debt."]),
        E("Acknowledging an old debt must be in writing",
          "An acknowledgment of a debt that looks time-barred counts against the deadline only if it is in writing and signed.",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.065",
          "An acknowledgment of the justness of a claim that appears to be barred by limitations is not admissible in evidence to defeat the law of limitations if made after the time that the claim is due unless the acknowledgment is in writing and is signed by the party to be charged."),
        REG_F,
    ],
}
CELLE["TX/breach-of-contract"] = {
    "varianti": [V("Written or oral contract", 4, "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.051",
                   "Every action for which there is no express limitations period, except an action for the recovery of real property, must be brought not later than four years after the day the cause of action accrues.",
                   "not later than four years after the day the cause of action accrues")],
    "inizio": "Texas does not set a separate period for written and oral contracts. A claim for money owed under a contract is a “debt” (four years, § 16.004(a)(3)); other contract claims fall under the four-year residual period of § 16.051.",
    "eccezioni": [
        E("Contract clauses that shorten the deadline below two years are void",
          "A contract cannot cut the time to sue to less than two years (with an exception for large business-sale agreements).",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.070(a)",
          "A stipulation, contract, or agreement that establishes a limitations period that is shorter than two years is void in this state."),
        E("Notice clauses shorter than 90 days are void",
          "A contract term that requires notice of a claim within less than 90 days as a condition of suing is void.",
          "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.071(a)",
          "A stipulation that requires notification within less than 90 days is void."),
    ],
}
CELLE["TX/property-damage"] = {
    "varianti": [V("Injury to property", 2, "tx_cprc16", "Tex. Civ. Prac. & Rem. Code § 16.003(a)",
                   "a person must bring suit for trespass for injury to the estate or to the property of another, conversion of personal property, taking or detaining the personal property of another, personal injury, forcible entry and detainer, and forcible detainer not later than two years after the day the cause of action accrues.",
                   "not later than two years after the day the cause of action accrues")],
    "inizio": "Two years from the day the claim accrues. The same two-year section covers damage to real property (“the estate”), conversion and taking or detaining personal property.",
    "eccezioni": [],
}

# =====================================================================================================================  FLORIDA
STATI["FL"] = {
    "nome": "Florida", "slug": "florida", "codice": "Florida Statutes, chapter 95",
    "regole": [
        E("What pauses the deadline in Florida (closed list)",
          "Florida lists the reasons that toll a deadline, and says no other disability or reason does. They include the absence of the person to be sued, use of a false name, concealment, adjudicated incapacity, payments on a written obligation and pending arbitration.",
          "fl_95_051", "Fla. Stat. § 95.051",
          ["(1) The running of the time under any statute of limitations except ss. 95.281, 95.35, and 95.36 is tolled by:(a) Absence from the state of the person to be sued.",
           "(2) A disability or other reason does not toll the running of any statute of limitations except those specified in this section, s. 95.091, the Florida Probate Code, or the Florida Guardianship Law."]),
        E("Minors and incapacity: seven-year outer limit",
          "Minority tolls the deadline only while the child has no parent or guardian able to sue (or one with an adverse interest), and adjudicated incapacity before the claim tolls it; in both cases the action must be filed within 7 years of the event.",
          "fl_95_051", "Fla. Stat. § 95.051(1)(d), (i)",
          ["(d) The adjudicated incapacity, before the cause of action accrued, of the person entitled to sue. In any event, the action must be begun within 7 years after the act, event, or occurrence giving rise to the cause of action.",
           "(i) The minority or previously adjudicated incapacity of the person entitled to sue during any period of time in which a parent, guardian, or guardian ad litem does not exist, has an interest adverse to the minor or incapacitated person, or is adjudicated to be incapacitated to sue;"]),
    ],
    "governo": [
        E("Claims against the state, counties and cities",
          "Before suing the state or a local government in tort, the claim must be presented in writing within 3 years (2 years for wrongful death) and denied.",
          "fl_768_28", "Fla. Stat. § 768.28(6)(a)",
          ["(6)(a) An action may not be instituted on a claim against the state or one of its agencies or subdivisions unless the claimant presents the claim in writing to the appropriate agency",
           "within 3 years after such claim accrues",
           "2. Such action is for wrongful death, the claimant must present the claim in writing to the Department of Financial Services within 2 years after the claim accrues."]),
    ],
    "cambi": [
        {"data": "2023-03-24", "titolo": "Negligence: from four years to two (HB 837)",
         "spiega": "Chapter 2023-15, Laws of Florida, moved “an action founded on negligence” from the four-year list to the two-year list. It was approved by the Governor and took effect on March 24, 2023, and the change applies to causes of action accruing after that date. Negligence claims that accrued on or before March 24, 2023 kept the old four-year period.",
         "fonte": "fl_law_2023_15", "cit": "Laws of Florida ch. 2023-15, ss. 3, 28 and 31",
         "testo": ["Section 28. The amendments made by this act to s. 95.11, Florida Statutes, apply to causes of action accruing after the effective date of this act.",
                   "Section 31. This act shall take effect upon becoming a law.", "Approved by the Governor March 24, 2023."]},
    ],
}
_FL_NEG = V("Negligence (claims that accrued after March 24, 2023)", 2, "fl_95_11", "Fla. Stat. § 95.11(5)(a)",
            "(5) WITHIN TWO YEARS.—(a) An action founded on negligence.", "WITHIN TWO YEARS",
            prima={"fino_al": "2023-03-24", "anni": 4, "etichetta": "Negligence that accrued on or before March 24, 2023",
                   "cit": "Laws of Florida ch. 2023-15, s. 28 (old § 95.11(3)(a))", "fonte": "fl_law_2023_15",
                   "testo": ["(3) WITHIN FOUR YEARS.—", "(a) An action founded on negligence."], "frase": "WITHIN FOUR YEARS"})
CELLE["FL/personal-injury"] = {
    "varianti": [_FL_NEG,
                 V("Intentional tort (assault, battery and similar)", 4, "fl_95_11", "Fla. Stat. § 95.11(3)(n)",
                   ["(3) WITHIN FOUR YEARS.—", "(n) An action for assault, battery, false arrest, malicious prosecution, malicious interference, false imprisonment, or any other intentional tort,"],
                   "WITHIN FOUR YEARS")],
    "inizio": "Florida says a cause of action accrues “when the last element constituting the cause of action occurs” (§ 95.031(1)); for an injury caused by negligence that is usually the date of the injury, but it can depend on the facts.",
    "eccezioni": [],
    "nota": "Most injury claims (car accidents, falls) are founded on negligence. The two-year period applies to negligence claims that accrued after March 24, 2023; the calculator switches to four years for earlier dates.",
}
CELLE["FL/medical-malpractice"] = {
    "varianti": [V("Medical malpractice", 2, "fl_95_11", "Fla. Stat. § 95.11(5)(c)",
                   "(c) An action for medical malpractice shall be commenced within 2 years from the time the incident giving rise to the action occurred or within 2 years from the time the incident is discovered, or should have been discovered with the exercise of due diligence;",
                   "within 2 years from the time the incident giving rise to the action occurred")],
    "inizio": "Two years from the incident, or from when the incident was or should have been discovered with due diligence.",
    "repose": V("Outer limit", 4, "fl_95_11", "Fla. Stat. § 95.11(5)(c)",
                "however, in no event shall the action be commenced later than 4 years from the date of the incident or occurrence out of which the cause of action accrued,",
                "later than 4 years from the date of the incident"),
    "eccezioni": [
        E("Children up to their eighth birthday",
          "The four-year outer limit does not bar an action brought for a minor on or before the child's eighth birthday.",
          "fl_95_11", "Fla. Stat. § 95.11(5)(c)",
          "except that this 4-year period shall not bar an action brought on behalf of a minor on or before the child's eighth birthday."),
        E("Notice of intent pauses the deadline for 90 days",
          "Florida requires a pre-suit notice of intent; while the 90-day pre-suit period runs, the statute of limitations is tolled.",
          "fl_766_106", "Fla. Stat. § 766.106(4)",
          "(4) SERVICE OF PRESUIT NOTICE AND TOLLING.—The notice of intent to initiate litigation must be served within the time limits set forth in s. 95.11."),
    ],
}
CELLE["FL/wrongful-death"] = {
    "varianti": [V("Wrongful death", 2, "fl_95_11", "Fla. Stat. § 95.11(5)(e)",
                   ["(5) WITHIN TWO YEARS.—", "(e) An action for wrongful death."], "WITHIN TWO YEARS")],
    "inizio": "The section lists wrongful death among two-year actions but does not say when the claim accrues; the calculator counts from the date of death you enter. Ask a Florida attorney if the injury and the death happened on different dates.",
    "eccezioni": [
        E("Death from murder or manslaughter",
          "A wrongful death action against a natural person for an intentional tort resulting in death from acts described in ss. 782.04 or 782.07 may be brought at any time.",
          "fl_95_11", "Fla. Stat. § 95.11(11)",
          "an action for wrongful death seeking damages authorized under s. 768.21 brought against a natural person for an intentional tort resulting in death from acts described in s. 782.04 or s. 782.07 may be commenced at any time."),
    ],
}
CELLE["FL/debt"] = {
    "varianti": [
        V("Written contract or obligation", 5, "fl_95_11", "Fla. Stat. § 95.11(2)(b)",
          ["(2) WITHIN FIVE YEARS.—", "(b) A legal or equitable action on a contract, obligation, or liability founded on a written instrument,"], "WITHIN FIVE YEARS"),
        V("Not in writing, including store accounts", 4, "fl_95_11", "Fla. Stat. § 95.11(3)(j)",
          ["(3) WITHIN FOUR YEARS.—", "(j) A legal or equitable action on a contract, obligation, or liability not founded on a written instrument, including an action for the sale and delivery of goods, wares, and merchandise, and on store accounts."],
          "WITHIN FOUR YEARS"),
        V("Hospital medical debt (from referral to collection)", 3, "fl_95_11", "Fla. Stat. § 95.11(4)",
          "(4) WITHIN THREE YEARS.—An action to collect medical debt for services rendered by a facility licensed under chapter 395, provided that the period of limitations shall run from the date on which the facility refers the medical debt to a third party for collection.",
          "WITHIN THREE YEARS", nota_data="For this kind of debt the three years run from the date the hospital referred the debt to a collector, not from the missed payment."),
    ],
    "inizio": "From the day the claim accrues, except hospital medical debt, which runs from the referral to a third party for collection.",
    "eccezioni": [
        E("A payment on a written obligation pauses the clock",
          "Paying any part of the principal or interest of an obligation founded on a written instrument tolls the deadline.",
          "fl_95_051", "Fla. Stat. § 95.051(1)(f)",
          "(f) The payment of any part of the principal or interest of any obligation or liability founded on a written instrument."),
        E("Promise to pay a barred debt must be in writing",
          "An acknowledgment of, or promise to pay, a time-barred debt counts only if written and signed.",
          "fl_95_04", "Fla. Stat. § 95.04",
          "An acknowledgment of, or promise to pay, a debt barred by a statute of limitations must be in writing and signed by the person sought to be charged."),
        REG_F,
    ],
}
CELLE["FL/breach-of-contract"] = {
    "varianti": [
        V("Written contract", 5, "fl_95_11", "Fla. Stat. § 95.11(2)(b)",
          ["(2) WITHIN FIVE YEARS.—", "(b) A legal or equitable action on a contract, obligation, or liability founded on a written instrument,"], "WITHIN FIVE YEARS"),
        V("Oral contract (not founded on a written instrument)", 4, "fl_95_11", "Fla. Stat. § 95.11(3)(j)",
          ["(3) WITHIN FOUR YEARS.—", "(j) A legal or equitable action on a contract, obligation, or liability not founded on a written instrument,"], "WITHIN FOUR YEARS"),
    ],
    "inizio": "From the day the last element of the claim occurs (§ 95.031(1)), usually the breach.",
    "eccezioni": [
        E("Specific performance: one year",
          "An action asking the court to order performance of a contract (rather than money) must be brought within one year.",
          "fl_95_11", "Fla. Stat. § 95.11(6)(a)",
          "(6) WITHIN ONE YEAR.—(a) An action for specific performance of a contract."),
        E("Property insurance contracts",
          "A claim for breach of a property insurance contract has five years running from the date of loss.",
          "fl_95_11", "Fla. Stat. § 95.11(2)(e)",
          "(e) Notwithstanding paragraph (b), an action for breach of a property insurance contract, with the period running from the date of loss."),
    ],
}
CELLE["FL/property-damage"] = {
    "varianti": [
        dict(_FL_NEG, etichetta="Damage caused by negligence (accrued after March 24, 2023)"),
        V("Trespass on real property", 4, "fl_95_11", "Fla. Stat. § 95.11(3)(f)",
          ["(3) WITHIN FOUR YEARS.—", "(f) An action for trespass on real property."], "WITHIN FOUR YEARS"),
        V("Taking, detaining or injuring personal property", 4, "fl_95_11", "Fla. Stat. § 95.11(3)(g)",
          ["(3) WITHIN FOUR YEARS.—", "(g) An action for taking, detaining, or injuring personal property."], "WITHIN FOUR YEARS"),
    ],
    "inizio": "From the day the last element of the claim occurs (§ 95.031(1)), usually the damage.",
    "eccezioni": [],
    "nota": "Which period applies depends on how the claim is framed: damage caused by negligence (for example, a car crash) is in the two-year list since March 24, 2023, while trespass on land and injury to personal property are in the four-year list. Ask a Florida attorney which one fits your case.",
}

# =====================================================================================================================  OHIO
STATI["OH"] = {
    "nome": "Ohio", "slug": "ohio", "codice": "Ohio Revised Code, chapter 2305",
    "regole": [
        E("Minors and people of unsound mind",
          "If the person with the claim is a minor or of unsound mind when it accrues, the period starts after the disability ends.",
          "oh_2305_16", "Ohio Rev. Code § 2305.16",
          "is, at the time the cause of action accrues, within the age of minority or of unsound mind, the person may bring it within the respective times limited by those sections, after the disability is removed."),
        E("Defendant out of state, absconding or hiding",
          "Time while the person being sued is out of Ohio, has absconded or is concealed is not counted (this does not apply to statutes of repose).",
          "oh_2305_15", "Ohio Rev. Code § 2305.15(A)",
          "After the cause of action accrues if the person departs from the state, absconds, or conceals self, the time of the person's absence or concealment shall not be computed as any part of a period within which the action must be brought."),
        E("Saving statute: one year to refile",
          "If a timely case fails otherwise than on the merits, a new action may be filed within one year or within the original period, whichever is later.",
          "oh_2305_19", "Ohio Rev. Code § 2305.19(A)",
          "may commence a new action within one year after the date of the reversal of the judgment or the plaintiff's failure otherwise than upon the merits or within the period of the original applicable statute of limitations, whichever occurs later."),
    ],
    "governo": [
        E("Claims against cities, counties and other political subdivisions",
          "An action against a political subdivision for injury, death or loss to person or property must be brought within two years, or any shorter period the Revised Code sets.",
          "oh_2744_04", "Ohio Rev. Code § 2744.04(A)",
          "shall be brought within two years after the cause of action accrues, or within any applicable shorter period of time for bringing the action provided by the Revised Code."),
    ],
    "cambi": [
        {"data": "2021-06-16", "titolo": "Contracts: written 8 → 6 years, oral 6 → 4 years (Senate Bill 13)",
         "spiega": "The version of § 2305.06 in force until June 16, 2021 gave eight years for written contracts; § 2305.07 gave six years for contracts not in writing. Senate Bill 13 (134th General Assembly) cut them to six and four years and added the six-year rule for consumer transactions. A transition rule in that bill covers claims that accrued before June 16, 2021: our calculator does not compute those dates.",
         "fonte": "oh_2305_06_2012", "cit": "Ohio Rev. Code § 2305.06 (version of September 28, 2012)",
         "testo": "an action upon a specialty or an agreement, contract, or promise in writing shall be brought within eight years after the cause of action accrued."},
        {"data": "2026-09-23", "titolo": "§ 2305.06 amended again (Senate Bill 219)",
         "spiega": "The official code shows § 2305.06 amended by Senate Bill 219 (136th General Assembly), effective September 23, 2026. The current text still says six years.",
         "fonte": "oh_2305_06", "cit": "Ohio Rev. Code § 2305.06",
         "testo": "September 23, 2026 – Amended by Senate Bill 219 - 136th General Assembly"},
    ],
}
_OH_TRANS = {"data": "2021-06-16", "messaggio": "This claim accrued before June 16, 2021, when Senate Bill 13 shortened Ohio's contract periods. A transition rule applies that this calculator does not compute: ask an Ohio attorney."}
CELLE["OH/personal-injury"] = {
    "varianti": [V("Bodily injury", 2, "oh_2305_10", "Ohio Rev. Code § 2305.10(A)",
                   "an action based on a product liability claim and an action for bodily injury or injuring personal property shall be brought within two years after the cause of action accrues.",
                   "shall be brought within two years after the cause of action accrues")],
    "inizio": "The section says the claim accrues “when the injury or loss to person or property occurs”, with later accrual dates for some exposure injuries.",
    "inizio_testo": {"fonte": "oh_2305_10", "cit": "Ohio Rev. Code § 2305.10(A)",
                     "testo": ["a cause of action accrues under this division when the injury or loss to person or property occurs."]},
    "eccezioni": [
        E("Exposure injuries: from the date you are told",
          "For injuries from exposure to toxic chemicals, drugs, medical devices, asbestos and some other agents, the claim accrues when a competent medical authority informs the person (or when the person should have known).",
          "oh_2305_10", "Ohio Rev. Code § 2305.10(B)",
          "accrues upon the date on which the plaintiff is informed by competent medical authority that the plaintiff has an injury that is related to the exposure,"),
    ],
}
CELLE["OH/medical-malpractice"] = {
    "varianti": [V("Medical claim", 1, "oh_2305_113", "Ohio Rev. Code § 2305.113(A)",
                   "(A) Except as otherwise provided in this section, an action upon a medical, dental, optometric, or chiropractic claim shall be commenced within one year after the cause of action accrued.",
                   "within one year after the cause of action accrued")],
    "inizio": "One year after the claim accrues. Ohio has one of the shortest medical malpractice periods in the country.",
    "repose": V("Statute of repose", 4, "oh_2305_113", "Ohio Rev. Code § 2305.113(C)(1)",
                "(1) No action upon a medical, dental, optometric, or chiropractic claim shall be commenced more than four years after the occurrence of the act or omission constituting the alleged basis of the medical, dental, optometric, or chiropractic claim.",
                "more than four years after the occurrence of the act or omission"),
    "eccezioni": [
        E("180-day letter",
          "A written notice sent before the year runs out, saying the claimant is considering a lawsuit, allows the action to be filed within 180 days after the notice.",
          "oh_2305_113", "Ohio Rev. Code § 2305.113(B)(1)",
          "gives to the person who is the subject of that claim written notice that the claimant is considering bringing an action upon that claim, that action may be commenced against the person notified at any time within one hundred eighty days after the notice is so given."),
        E("Late discovery and foreign objects",
          "If the injury could not reasonably have been discovered within three years but is discovered before the four-year limit, the person has one year from discovery; for a foreign object left in the body, one year from discovery.",
          "oh_2305_113", "Ohio Rev. Code § 2305.113(D)",
          "the person may commence an action upon the claim not later than one year after the person discovers the injury resulting from that act or omission."),
    ],
}
CELLE["OH/wrongful-death"] = {
    "varianti": [V("Wrongful death", 2, "oh_2125_02", "Ohio Rev. Code § 2125.02(F)(1)",
                   "a civil action for wrongful death shall be commenced within two years after the decedent's death.",
                   "within two years after the decedent's death")],
    "inizio": "Two years from the date of death.",
    "eccezioni": [
        E("Product claims: ten-year repose",
          "A wrongful death claim involving a product generally cannot accrue against the manufacturer or supplier more than ten years after the product was delivered to its first purchaser, with exceptions.",
          "oh_2125_02", "Ohio Rev. Code § 2125.02(F)(2)(a)",
          "no cause of action for wrongful death involving a product liability claim shall accrue against the manufacturer or supplier of a product later than ten years from the date that the product was delivered to its first purchaser or first lessee"),
    ],
}
CELLE["OH/debt"] = {
    "varianti": [
        V("Consumer debt (personal, family or household)", 6, "oh_2305_07", "Ohio Rev. Code § 2305.07(C)",
          "an action arising out of a consumer transaction incurred primarily for personal, family, or household purposes, based upon any contract, agreement, obligation, liability, or promise, express or implied, including an account stated, whether or not reduced to writing or signed by the party to be charged by that transaction, shall be commenced within six years after the cause of action accrued.",
          "shall be commenced within six years after the cause of action accrued", giorni_dopo=30, transizione=_OH_TRANS,
          nota_data="For consumer debt the statute says the claim accrues 30 days after the later of the last charge or the last payment; the calculator adds those 30 days to the date you enter."),
        V("Written contract (business debt)", 6, "oh_2305_06", "Ohio Rev. Code § 2305.06",
          "an action upon a specialty or an agreement, contract, or promise in writing shall be brought within six years after the cause of action accrued.",
          "shall be brought within six years after the cause of action accrued", transizione=_OH_TRANS),
        V("Contract not in writing (business debt)", 4, "oh_2305_07", "Ohio Rev. Code § 2305.07(A)",
          "an action upon a contract not in writing, express or implied, shall be brought within four years after the cause of action accrued.",
          "shall be brought within four years after the cause of action accrued", transizione=_OH_TRANS),
    ],
    "inizio": "For consumer debt, the statute fixes the start date itself: thirty days after the later of the last charge or the last payment made by or for the consumer. For business debts the period runs from when the claim accrues, usually the missed payment.",
    "inizio_testo": {"fonte": "oh_2305_07", "cit": "Ohio Rev. Code § 2305.07(C)",
                     "testo": ["For purposes of this division, a cause of action accrues thirty calendar days after the date of the last charge or payment by, or on behalf of, the consumer, whichever is later."]},
    "eccezioni": [REG_F],
}
CELLE["OH/breach-of-contract"] = {
    "varianti": [
        V("Written contract", 6, "oh_2305_06", "Ohio Rev. Code § 2305.06",
          "an action upon a specialty or an agreement, contract, or promise in writing shall be brought within six years after the cause of action accrued.",
          "shall be brought within six years after the cause of action accrued", transizione=_OH_TRANS),
        V("Oral contract", 4, "oh_2305_07", "Ohio Rev. Code § 2305.07(A)",
          "an action upon a contract not in writing, express or implied, shall be brought within four years after the cause of action accrued.",
          "shall be brought within four years after the cause of action accrued", transizione=_OH_TRANS),
    ],
    "inizio": "From the day the claim accrues, usually the breach. For claims that accrued before June 16, 2021 a transition rule applies (see recent changes).",
    "eccezioni": [
        E("Old rule: oral contracts had six years",
          "Before June 16, 2021, § 2305.07 gave six years for contracts not in writing. Some tables online still show six years.",
          "oh_2305_07_1993", "Ohio Rev. Code § 2305.07 (version of July 1, 1993)",
          "an action upon a contract not in writing, express or implied, or upon a liability created by statute other than a forfeiture or penalty, shall be brought within six years after the cause thereof accrued."),
    ],
}
CELLE["OH/property-damage"] = {
    "varianti": [
        V("Injury to personal property", 2, "oh_2305_10", "Ohio Rev. Code § 2305.10(A)",
          "an action based on a product liability claim and an action for bodily injury or injuring personal property shall be brought within two years after the cause of action accrues.",
          "shall be brought within two years after the cause of action accrues"),
        V("Trespass on real property", 4, "oh_2305_09", "Ohio Rev. Code § 2305.09(A)",
          ["an action for any of the following causes shall be brought within four years after the cause thereof accrued:", "(A) For trespassing upon real property;"],
          "shall be brought within four years after the cause thereof accrued"),
    ],
    "inizio": "For personal property, the claim accrues when the loss occurs (§ 2305.10(A)).",
    "eccezioni": [
        E("Hidden wrongdoer or underground damage",
          "For trespass under ground, injury to mines or wrongful taking of personal property, the claim does not accrue until the wrongdoer is discovered.",
          "oh_2305_09", "Ohio Rev. Code § 2305.09",
          "If the action is for trespassing under ground or injury to mines, or for the wrongful taking of personal property, the causes thereof shall not accrue until the wrongdoer is discovered;"),
    ],
}

# =====================================================================================================================  WASHINGTON
STATI["WA"] = {
    "nome": "Washington", "slug": "washington", "codice": "Revised Code of Washington, chapter 4.16 RCW",
    "regole": [
        E("Minors, incompetence and imprisonment before sentencing",
          "If the person with the claim is under 18, legally incompetent, or imprisoned on a criminal charge before sentencing when the claim accrues, that time is not counted.",
          "wa_4_16", "RCW 4.16.190",
          "the time of such disability shall not be a part of the time limited for the commencement of action."),
        E("Defendant out of state or concealed",
          "Time while the person being sued is out of the state or concealed is not counted.",
          "wa_4_16", "RCW 4.16.180",
          "the time of his or her absence or concealment shall not be deemed or taken as any part of the time limit for the commencement of such action."),
        E("Filing versus service: 90 days",
          "An action counts as commenced when the complaint is filed or the summons is served, but the other step must follow within 90 days or the filing does not stop the clock.",
          "wa_4_16", "RCW 4.16.170",
          "For the purpose of tolling any statute of limitations an action shall be deemed commenced when the complaint is filed or summons is served whichever occurs first."),
    ],
    "governo": [
        E("Claims against local governments: 60-day waiting period",
          "A tort claim against a local government must first be presented; suit cannot start until 60 days later, and the deadline is tolled during those 60 days.",
          "wa_4_96_020", "RCW 4.96.020(4)",
          "The applicable period of limitations within which an action must be commenced shall be tolled during the sixty calendar day period."),
    ],
    "cambi": [],
    "assente": {"wrongful-death": "Washington's wrongful death chapter (chapter 4.20 RCW) does not state its own deadline, so we have not published a Washington wrongful death page. Ask a Washington attorney."},
}
CELLE["WA/personal-injury"] = {
    "varianti": [V("Injury to the person", 3, "wa_4_16", "RCW 4.16.080(2)",
                   ["The following actions shall be commenced within three years:",
                    "(2) An action for taking, detaining, or injuring personal property, including an action for the specific recovery thereof, or for any other injury to the person or rights of another not hereinafter enumerated;"],
                   "shall be commenced within three years")],
    "inizio": "The section does not define when an injury claim accrues; the calculator counts from the date you enter.",
    "eccezioni": [
        E("Libel, slander, assault and battery: two years",
          "Some intentional torts have a shorter two-year period.",
          "wa_4_16", "RCW 4.16.100(1)",
          "(1) An action for libel, slander, assault, assault and battery, or false imprisonment."),
    ],
}
CELLE["WA/medical-malpractice"] = {
    "varianti": [V("Health care negligence", 3, "wa_4_16", "RCW 4.16.350",
                   "based upon alleged professional negligence shall be commenced within three years of the act or omission alleged to have caused the injury or condition, or one year of the time the patient or his or her representative discovered or reasonably should have discovered that the injury or condition was caused by said act or omission, whichever period expires later,",
                   "within three years of the act or omission")],
    "inizio": "Three years from the act or omission, or one year from when the patient discovered (or should have discovered) that it caused the injury, whichever expires later.",
    "repose": V("Statute of repose", 8, "wa_4_16", "RCW 4.16.350",
                "except that in no event shall an action be commenced more than eight years after said act or omission:",
                "more than eight years after said act or omission"),
    "eccezioni": [
        E("Fraud, concealment or a foreign body",
          "The time is tolled upon proof of fraud, intentional concealment, or a foreign body with no therapeutic or diagnostic purpose.",
          "wa_4_16", "RCW 4.16.350",
          "PROVIDED, That the time for commencement of an action is tolled upon proof of fraud, intentional concealment, or the presence of a foreign body not intended to have a therapeutic or diagnostic purpose or effect,"),
        E("Minors: parents' knowledge counts",
          "For this section, the knowledge of a custodial parent or guardian is imputed to a child, so the general minors rule in RCW 4.16.190 does not simply pause the clock.",
          "wa_4_16", "RCW 4.16.350",
          "For purposes of this section, notwithstanding RCW 4.16.190, the knowledge of a custodial parent or guardian shall be imputed to a person under the age of eighteen years,"),
    ],
    "nota": "Washington courts have ruled on parts of this section (the legislature's own note cites DeYoung v. Providence Medical Center). Ask a Washington attorney how it applies today.",
}
CELLE["WA/debt"] = {
    "varianti": [
        V("Written contract", 6, "wa_4_16", "RCW 4.16.040(1)",
          ["The following actions shall be commenced within six years:", "(1) An action upon a contract in writing, or liability express or implied arising out of a written agreement,"],
          "shall be commenced within six years"),
        V("Account receivable", 6, "wa_4_16", "RCW 4.16.040(2)",
          ["The following actions shall be commenced within six years:", "(2) An action upon an account receivable."], "shall be commenced within six years"),
        V("Contract not in writing", 3, "wa_4_16", "RCW 4.16.080(3)",
          ["The following actions shall be commenced within three years:", "(3) Except as provided in RCW 4.16.040(2), an action upon a contract or liability, express or implied, which is not in writing, and does not arise out of any written instrument;"],
          "shall be commenced within three years"),
    ],
    "inizio": "From the day the claim accrues. For a mutual open and current account, the section says it accrues at the last item proved on either side.",
    "eccezioni": [
        E("What counts as an account receivable",
          "An account receivable is any obligation for payment incurred in the ordinary course of the creditor's business or profession.",
          "wa_4_16", "RCW 4.16.040(2)",
          "For purposes of this section, an account receivable is any obligation for payment incurred in the ordinary course of the claimant's business or profession, whether arising from one or more transactions and whether or not earned by performance."),
        E("Mutual open accounts",
          "For a mutual open and current account, the clock starts at the last item on either side, unless more than a year passed between items.",
          "wa_4_16", "RCW 4.16.150",
          "the cause of action shall be deemed to have accrued from the time of the last item proved in the account on either side,"),
        REG_F,
    ],
}
CELLE["WA/breach-of-contract"] = {
    "varianti": [
        V("Written contract", 6, "wa_4_16", "RCW 4.16.040(1)",
          ["The following actions shall be commenced within six years:", "(1) An action upon a contract in writing, or liability express or implied arising out of a written agreement,"],
          "shall be commenced within six years"),
        V("Oral contract", 3, "wa_4_16", "RCW 4.16.080(3)",
          ["The following actions shall be commenced within three years:", "(3) Except as provided in RCW 4.16.040(2), an action upon a contract or liability, express or implied, which is not in writing, and does not arise out of any written instrument;"],
          "shall be commenced within three years"),
    ],
    "inizio": "From the day the claim accrues, usually the breach; the section does not define it.",
    "eccezioni": [],
}
CELLE["WA/property-damage"] = {
    "varianti": [
        V("Waste or trespass on real property", 3, "wa_4_16", "RCW 4.16.080(1)",
          ["The following actions shall be commenced within three years:", "(1) An action for waste or trespass upon real property;"], "shall be commenced within three years"),
        V("Taking, detaining or injuring personal property", 3, "wa_4_16", "RCW 4.16.080(2)",
          ["The following actions shall be commenced within three years:", "(2) An action for taking, detaining, or injuring personal property,"], "shall be commenced within three years"),
    ],
    "inizio": "From the day the claim accrues; the section does not define it.",
    "eccezioni": [],
}

# =====================================================================================================================  VIRGINIA
STATI["VA"] = {
    "nome": "Virginia", "slug": "virginia", "codice": "Code of Virginia, Title 8.01, chapter 4",
    "regole": [
        E("When the clock starts",
          "Virginia's general rule: injury claims accrue when the injury is sustained, and contract claims when the breach occurs, not when the damage is discovered (with listed exceptions).",
          "va_8_01_230", "Va. Code § 8.01-230",
          "the right of action shall be deemed to accrue and the prescribed limitation period shall begin to run from the date the injury is sustained in the case of injury to the person or damage to property, when the breach of contract occurs in actions ex contractu and not when the resulting damage is discovered,"),
        E("Minors and incapacitated people",
          "A person who is a minor or incapacitated when the claim accrues may sue within the period after the disability is removed.",
          "va_8_01_229", "Va. Code § 8.01-229(A)(1)",
          "1. If a person entitled to bring any action is at the time the cause of action accrues an infant, except if such infant has been emancipated pursuant to Article 15 (§ 16.1-331 et seq.) of Chapter 11 of Title 16.1, or incapacitated, such person may bring it within the prescribed limitation period after such disability is removed; or"),
        E("Voluntary nonsuit: six months to refile",
          "After a voluntary nonsuit, the case may be refiled within six months of the court's order or within the original period, whichever is longer.",
          "va_8_01_229", "Va. Code § 8.01-229(E)(3)",
          "the plaintiff may recommence his action within six months from the date of the order entered by the court, or within the original period of limitation, or within the limitation period as provided by subdivision B 1, whichever period is longer."),
    ],
    "governo": [
        E("Claims against counties, cities and towns: six months",
          "A negligence claim against a locality is barred unless written notice is filed within six months of accrual (or the locality had actual knowledge).",
          "va_15_2_209", "Va. Code § 15.2-209(A)",
          "Every claim cognizable against any county, city, or town for negligence shall be forever barred unless the claimant or his agent, attorney, or representative has filed a written statement of the nature of the claim, which includes the time and place at which the injury is alleged to have occurred, within six months after such cause of action accrued."),
        E("Claims against the Commonwealth: one-year notice",
          "A claim under the Virginia Tort Claims Act requires a notice of claim within one year of accrual.",
          "va_8_01_195_7", "Va. Code § 8.01-195.7",
          "Every claim cognizable against the Commonwealth or a transportation district under this article shall be forever barred, unless within one year after the cause of action accrues to the claimant the notice of claim required by § 8.01-195.6 is properly filed."),
    ],
    "cambi": [],
}
CELLE["VA/personal-injury"] = {
    "varianti": [V("Personal injury", 2, "va_8_01_243", "Va. Code § 8.01-243(A)",
                   "A. Unless otherwise provided in this section or by other statute, every action for personal injuries, whatever the theory of recovery, and every action for damages resulting from fraud, shall be brought within two years after the cause of action accrues.",
                   "shall be brought within two years after the cause of action accrues")],
    "inizio": "Virginia's general rule (§ 8.01-230) is that an injury claim accrues on the date the injury is sustained.",
    "eccezioni": [
        E("Parents' claim for a child's medical expenses: five years",
          "A parent's own claim against the wrongdoer for the expenses of treating an injured child falls under the five-year property period.",
          "va_8_01_243", "Va. Code § 8.01-243(B)",
          "B. Every action for injury to property, including actions by a parent or guardian of an infant against a tort-feasor for expenses of curing or attempting to cure such infant from the result of a personal injury or loss of services of such infant, shall be brought within five years after the cause of action accrues."),
    ],
}
CELLE["VA/medical-malpractice"] = {
    "varianti": [V("Malpractice (personal injury)", 2, "va_8_01_243", "Va. Code § 8.01-243(A)",
                   "every action for personal injuries, whatever the theory of recovery, and every action for damages resulting from fraud, shall be brought within two years after the cause of action accrues.",
                   "shall be brought within two years after the cause of action accrues")],
    "inizio": "Two years from the injury (§ 8.01-230), with the extensions below.",
    "eccezioni": [
        E("Foreign object, concealment, missed cancer diagnosis: one more year",
          "The two years are extended to one year from discovery for a foreign object left in the body or when fraud or concealment prevented discovery, and to one year from when a diagnosis is communicated for a negligent failure to diagnose cancer or certain tumors.",
          "va_8_01_243", "Va. Code § 8.01-243(C)",
          ["C. The two-year limitations period specified in subsection A shall be extended in actions for malpractice against a health care provider as follows:",
           "1. In cases arising out of a foreign object having no therapeutic or diagnostic effect being left in a patient's body, for a period of one year from the date the object is discovered or reasonably should have been discovered;"]),
        E("Ten-year cap on those extensions",
          "The extensions cannot go beyond 10 years from accrual (minors' tolling aside).",
          "va_8_01_243", "Va. Code § 8.01-243(C)",
          "However, the provisions of this subsection shall not apply to extend the limitations period beyond 10 years from the date the cause of action accrues,"),
        E("Children: until the 10th birthday",
          "For a minor, two years from the last act or omission; a child injured before age 8 has until the 10th birthday.",
          "va_8_01_243_1", "Va. Code § 8.01-243.1",
          "shall be commenced within two years of the date of the last act or omission giving rise to the cause of action except that if the minor was less than eight years of age at the time of the occurrence of the malpractice, he shall have until his tenth birthday to commence an action."),
    ],
}
CELLE["VA/wrongful-death"] = {
    "varianti": [V("Wrongful death", 2, "va_8_01_244", "Va. Code § 8.01-244(B)",
                   "B. Every action under § 8.01-50 shall be brought by the personal representative of the decedent within two years after the death of the injured person.",
                   "within two years after the death of the injured person")],
    "inizio": "Two years after the death; the action is brought by the personal representative.",
    "eccezioni": [
        E("A dismissed case does not use up the time",
          "If a timely wrongful death action abates or is dismissed without a decision on the merits, the time it was pending is not counted.",
          "va_8_01_244", "Va. Code § 8.01-244(B)",
          "the time such action is pending shall not be counted as any part of such period of two years and another action may be brought within the remaining period of such two years as if such former action had not been instituted."),
    ],
}
CELLE["VA/debt"] = {
    "varianti": [
        V("Written and signed contract", 5, "va_8_01_246", "Va. Code § 8.01-246(A)(2)",
          "2. In actions on any contract that is not otherwise specified and that is in writing and signed by the party to be charged thereby, or by his agent, within five years whether such writing be under seal or not;",
          "within five years"),
        V("Unwritten or unsigned contract", 3, "va_8_01_246", "Va. Code § 8.01-246(A)(4)",
          "4. In actions upon (i) any contract that is not otherwise specified and that is in writing and not signed by the party to be charged, or by his agent, or (ii) any unwritten contract, express or implied, within three years.",
          "within three years"),
        V("Medical debt (from the final invoice due date)", 3, "va_8_01_246", "Va. Code § 8.01-246(B)",
          "such an action is barred if not commenced within three years from the due date applicable to the final invoice for a health care service",
          "within three years from the due date", nota_data="For medical debt the three years run from the due date of the final invoice (or the breach of a payment plan)."),
    ],
    "inizio": "Contract claims accrue when the breach occurs, not when the damage is discovered (§ 8.01-230).",
    "eccezioni": [
        E("A new written promise restarts the period",
          "A signed written promise to pay (or a written acknowledgment from which a promise can be implied) gives a new period from the promise.",
          "va_8_01_229", "Va. Code § 8.01-229(G)(1)",
          "An acknowledgment in writing, from which a promise of payment may be implied, shall be deemed to be such promise within the meaning of this subsection."),
        REG_F,
    ],
}
CELLE["VA/breach-of-contract"] = {
    "varianti": [
        V("Written and signed contract", 5, "va_8_01_246", "Va. Code § 8.01-246(A)(2)",
          "2. In actions on any contract that is not otherwise specified and that is in writing and signed by the party to be charged thereby, or by his agent, within five years whether such writing be under seal or not;",
          "within five years"),
        V("Oral contract (or written but unsigned)", 3, "va_8_01_246", "Va. Code § 8.01-246(A)(4)",
          "4. In actions upon (i) any contract that is not otherwise specified and that is in writing and not signed by the party to be charged, or by his agent, or (ii) any unwritten contract, express or implied, within three years.",
          "within three years"),
    ],
    "inizio": "When the breach occurs, not when the resulting damage is discovered (§ 8.01-230).",
    "eccezioni": [
        E("Sale of goods",
          "For contracts covered by § 8.2-725 of the Uniform Commercial Code (sale of goods), that section controls instead.",
          "va_8_01_246", "Va. Code § 8.01-246(C)",
          "C. In the case of any action to which § 8.2-725 of the Uniform Commercial Code is applicable, that section shall be controlling"),
    ],
}
CELLE["VA/property-damage"] = {
    "varianti": [V("Injury to property", 5, "va_8_01_243", "Va. Code § 8.01-243(B)",
                   "B. Every action for injury to property, including actions by a parent or guardian of an infant against a tort-feasor for expenses of curing or attempting to cure such infant from the result of a personal injury or loss of services of such infant, shall be brought within five years after the cause of action accrues.",
                   "shall be brought within five years after the cause of action accrues")],
    "inizio": "From the date the damage to property is sustained (§ 8.01-230).",
    "eccezioni": [],
    "nota": "Virginia gives five years for property damage but only two years for personal injury, even when both come from the same accident.",
}

# =====================================================================================================================  NORTH CAROLINA
STATI["NC"] = {
    "nome": "North Carolina", "slug": "north-carolina", "codice": "North Carolina General Statutes, chapter 1, article 5",
    "regole": [
        E("Minors and people who are insane or incompetent",
          "A person under 18, insane or incompetent when the claim accrues may sue within the period after the disability is removed.",
          "nc_1_17", "N.C. Gen. Stat. § 1-17(a)",
          "(a) A person entitled to commence an action who is under a disability at the time the cause of action accrued may bring his or her action within the time limited in this Subchapter, after the disability is removed,"),
    ],
    "governo": [
        E("Claims against State agencies: Industrial Commission",
          "Tort claims against State departments and agencies go to the Industrial Commission within three years (two years after a death).",
          "nc_143_299", "N.C. Gen. Stat. § 143-299",
          "All claims against any and all State departments, institutions, and agencies shall henceforth be forever barred unless a claim be filed with the Industrial Commission within three years after the accrual of such claim,"),
    ],
    "cambi": [],
}
CELLE["NC/personal-injury"] = {
    "varianti": [V("Personal injury", 3, "nc_1_52", "N.C. Gen. Stat. § 1-52(16)",
                   ["Within three years an action -",
                    "(16) Unless otherwise provided by law, for personal injury or physical damage to claimant's property, the cause of action, except in causes of actions referred to in G.S. 1-15(c), shall not accrue until bodily harm to the claimant or physical damage to his property becomes apparent or ought reasonably to have become apparent to the claimant, whichever event first occurs."],
                   "Within three years")],
    "inizio": "The claim does not accrue until bodily harm becomes apparent, or ought reasonably to have become apparent.",
    "repose": V("Outer limit", 10, "nc_1_52", "N.C. Gen. Stat. § 1-52(16)",
                "no cause of action shall accrue more than 10 years from the last act or omission of the defendant giving rise to the cause of action.",
                "more than 10 years from the last act or omission"),
    "eccezioni": [],
}
CELLE["NC/medical-malpractice"] = {
    "varianti": [V("Professional malpractice", 3, "nc_1_15", "N.C. Gen. Stat. § 1-15(c)",
                   "Provided nothing herein shall be construed to reduce the statute of limitation in any such case below three years.",
                   "below three years")],
    "inizio": "The claim accrues at the last act of the defendant giving rise to it. If the injury is not readily apparent and is discovered two or more years later, suit must be brought within one year of discovery, but never in less than three years overall.",
    "inizio_testo": {"fonte": "nc_1_15", "cit": "N.C. Gen. Stat. § 1-15(c)",
                     "testo": ["a cause of action for malpractice arising out of the performance of or failure to perform professional services shall be deemed to accrue at the time of the occurrence of the last act of the defendant giving rise to the cause of action:"]},
    "repose": V("Outer limit", 4, "nc_1_15", "N.C. Gen. Stat. § 1-15(c)",
                "Provided further, that in no event shall an action be commenced more than four years from the last act of the defendant giving rise to the cause of action:",
                "more than four years from the last act of the defendant"),
    "eccezioni": [
        E("Foreign object: up to 10 years",
          "For a foreign object left in the body, one year from discovery, but no more than 10 years from the last act.",
          "nc_1_15", "N.C. Gen. Stat. § 1-15(c)",
          "but in no event may the action be commenced more than 10 years from the last act of the defendant giving rise to the cause of action."),
        E("Children: until age 10 (or 19)",
          "If the normal time runs out before the child turns 10, the action may be brought until the 10th birthday (with further rules for abused or neglected children and children in State custody).",
          "nc_1_17", "N.C. Gen. Stat. § 1-17(c)(1)",
          "(1) If the time limitations specified in G.S. 1-15(c) expire before the minor attains the full age of 10 years, the action may be brought any time before the minor attains the full age of 10 years."),
    ],
}
CELLE["NC/wrongful-death"] = {
    "varianti": [V("Wrongful death", 2, "nc_1_53", "N.C. Gen. Stat. § 1-53(4)",
                   ["Within two years -", "(4) Actions for damages on account of the death of a person caused by the wrongful act, neglect or fault of another under G.S. 28A-18-2; the cause of action shall not accrue until the date of death."],
                   "Within two years")],
    "inizio": "The statute says the claim does not accrue until the date of death.",
    "eccezioni": [
        E("No death claim if the injury claim was already barred",
          "If the person would have been barred from suing for the injury by the medical malpractice or ten-year rules, no wrongful death action can be brought.",
          "nc_1_53", "N.C. Gen. Stat. § 1-53(4)",
          "Provided that, whenever the decedent would have been barred, had he lived, from bringing an action for bodily harm because of the provisions of G.S. 1-15(c) or 1-52(16), no action for his death may be brought."),
    ],
}
CELLE["NC/debt"] = {
    "varianti": [
        V("Contract or account", 3, "nc_1_52", "N.C. Gen. Stat. § 1-52(1)",
          ["Within three years an action -", "(1) Upon a contract, obligation or liability arising out of a contract, express or implied, except those mentioned in the preceding sections or in G.S. 1-53(1)."],
          "Within three years"),
        V("Sealed instrument", 10, "nc_1_47", "N.C. Gen. Stat. § 1-47(2)",
          ["Within ten years an action -", "(2) Upon a sealed instrument or an instrument of conveyance of an interest in real property, against the principal thereto."],
          "Within ten years"),
    ],
    "inizio": "From the day the claim accrues, usually the missed payment.",
    "eccezioni": [
        E("New promise must be in writing; payments are different",
          "An acknowledgment or promise restarts the period only if in a signed writing; the section does not change the effect of a payment of principal or interest.",
          "nc_1_26", "N.C. Gen. Stat. § 1-26",
          "No acknowledgment or promise is evidence of a new or continuing contract, from which the statutes of limitations run, unless it is contained in some writing signed by the party to be charged thereby; but this section does not alter the effect of any payment of principal or interest."),
        REG_F,
    ],
}
CELLE["NC/breach-of-contract"] = {
    "varianti": [
        V("Written or oral contract", 3, "nc_1_52", "N.C. Gen. Stat. § 1-52(1)",
          ["Within three years an action -", "(1) Upon a contract, obligation or liability arising out of a contract, express or implied, except those mentioned in the preceding sections or in G.S. 1-53(1)."],
          "Within three years"),
        V("Sealed instrument", 10, "nc_1_47", "N.C. Gen. Stat. § 1-47(2)",
          ["Within ten years an action -", "(2) Upon a sealed instrument or an instrument of conveyance of an interest in real property, against the principal thereto."],
          "Within ten years"),
    ],
    "inizio": "North Carolina uses the same three years for written and oral contracts; a contract under seal has ten.",
    "eccezioni": [
        E("Contracts with local governments: two years",
          "An action against a local unit of government on a contract must be brought within two years.",
          "nc_1_53", "N.C. Gen. Stat. § 1-53(1)",
          "(1) An action against a local unit of government upon a contract, obligation or liability arising out of a contract, express or implied."),
    ],
}
CELLE["NC/property-damage"] = {
    "varianti": [
        V("Trespass on real property", 3, "nc_1_52", "N.C. Gen. Stat. § 1-52(3)",
          ["Within three years an action -", "(3) For trespass upon real property. When the trespass is a continuing one, the action shall be commenced within three years from the original trespass, and not thereafter."],
          "Within three years"),
        V("Taking or injuring goods", 3, "nc_1_52", "N.C. Gen. Stat. § 1-52(4)",
          ["Within three years an action -", "(4) For taking, detaining, converting or injuring any goods or chattels, including action for their specific recovery."],
          "Within three years"),
    ],
    "inizio": "For physical damage to property, the claim does not accrue until the damage becomes apparent or ought reasonably to have become apparent (§ 1-52(16)).",
    "repose": V("Outer limit", 10, "nc_1_52", "N.C. Gen. Stat. § 1-52(16)",
                "no cause of action shall accrue more than 10 years from the last act or omission of the defendant giving rise to the cause of action.",
                "more than 10 years from the last act or omission"),
    "eccezioni": [
        E("Continuing trespass",
          "For a continuing trespass, the three years run from the original trespass.",
          "nc_1_52", "N.C. Gen. Stat. § 1-52(3)",
          "When the trespass is a continuing one, the action shall be commenced within three years from the original trespass, and not thereafter."),
    ],
}

# =====================================================================================================================  MICHIGAN
STATI["MI"] = {
    "nome": "Michigan", "slug": "michigan", "codice": "Michigan Compiled Laws, chapter 600 (Revised Judicature Act)",
    "regole": [
        E("Minors and insanity: one year after it ends",
          "If the person with the claim is under 18 or insane when it accrues, they have one year after the disability ends, even if the period has run.",
          "mi_5851", "MCL 600.5851(1)",
          "shall have 1 year after the disability is removed through death or otherwise, to make the entry or bring the action although the period of limitations has run."),
        E("Fraudulent concealment: two years from discovery",
          "If the person liable hides the claim or their identity, the action may be brought within two years of discovery.",
          "mi_5855", "MCL 600.5855",
          "the action may be commenced at any time within 2 years after the person who is entitled to bring the action discovers, or should have discovered, the existence of the claim or the identity of the person who is liable for the claim,"),
        E("Defendant outside Michigan",
          "Absences of more than two months at a time are not counted, unless the defendant could be served anyway.",
          "mi_5853", "MCL 600.5853",
          "any and all periods of absence in excess of 2 months at a time shall not be counted as any part of the time limited for the commencement of the action"),
    ],
    "governo": [
        E("Claims against the State of Michigan",
          "A notice or claim must be filed with the court of claims within one year, and within six months for property damage or personal injuries.",
          "mi_6431", "MCL 600.6431(4)",
          "(4) For a claim against this state for property damage or personal injuries, the claimant shall file the claim or notice under subsection (1) with the clerk of the court of claims within 6 months after the event that gives rise to the claim."),
    ],
    "cambi": [],
}
CELLE["MI/personal-injury"] = {
    "varianti": [V("Injury to a person", 3, "mi_5805", "MCL 600.5805(2)",
                   "(2) Except as otherwise provided in this section, the period of limitations is 3 years after the time of the death or injury for all actions to recover damages for the death of a person or for injury to a person or property.",
                   "the period of limitations is 3 years after the time of the death or injury")],
    "inizio": "Three years after the time of the injury.",
    "eccezioni": [
        E("Assault, battery, false imprisonment: two years",
          "These intentional torts have two years (five years in domestic or dating violence cases).",
          "mi_5805", "MCL 600.5805(3)",
          "(3) Subject to subsections (4) to (6), the period of limitations is 2 years for an action charging assault, battery, or false imprisonment."),
        E("Products liability: three years",
          "A products liability action also has three years.",
          "mi_5805", "MCL 600.5805(12)",
          "(12) The period of limitations is 3 years for a products liability action."),
    ],
}
CELLE["MI/medical-malpractice"] = {
    "varianti": [V("Malpractice", 2, "mi_5805", "MCL 600.5805(8)",
                   "(8) Except as otherwise provided in this chapter, the period of limitations is 2 years for an action charging malpractice.",
                   "the period of limitations is 2 years for an action charging malpractice")],
    "inizio": "A medical malpractice claim accrues at the time of the act or omission, regardless of when it is discovered.",
    "inizio_testo": {"fonte": "mi_5838a", "cit": "MCL 600.5838a(1)",
                     "testo": ["accrues at the time of the act or omission that is the basis for the claim of medical malpractice, regardless of the time the plaintiff discovers or otherwise has knowledge of the claim."]},
    "repose": V("Statute of repose", 6, "mi_5838a", "MCL 600.5838a(2)",
                "the claim shall not be commenced later than 6 years after the date of the act or omission that is the basis for the claim.",
                "later than 6 years after the date of the act or omission"),
    "eccezioni": [
        E("Six months from discovery",
          "The action may also be brought within six months after the patient discovers or should have discovered the claim, if that is later.",
          "mi_5838a", "MCL 600.5838a(2)",
          "or within 6 months after the plaintiff discovers or should have discovered the existence of the claim, whichever is later."),
        E("182-day notice of intent",
          "A notice of intent must be given at least 182 days before suing; the deadline is tolled during the notice period if the claim would otherwise be barred.",
          "mi_2912b", "MCL 600.2912b(1)",
          "a person shall not commence an action alleging medical malpractice against a health professional or health facility unless the person has given the health professional or health facility written notice under this section not less than 182 days before the action is commenced."),
        E("Children under 8",
          "A child injured before age 8 has until the 10th birthday or the normal period, whichever is later.",
          "mi_5851", "MCL 600.5851(7)",
          "a person shall not bring an action based on the claim unless the action is commenced on or before the person's tenth birthday or within the period of limitations set forth in section 5838a, whichever is later."),
    ],
}
CELLE["MI/wrongful-death"] = {
    "varianti": [V("Death of a person", 3, "mi_5805", "MCL 600.5805(2)",
                   "the period of limitations is 3 years after the time of the death or injury for all actions to recover damages for the death of a person or for injury to a person or property.",
                   "the period of limitations is 3 years after the time of the death or injury")],
    "inizio": "The statute counts from “the time of the death or injury”. The calculator counts from the date of death you enter; if the injury happened earlier, ask a Michigan attorney which date applies.",
    "eccezioni": [
        E("Personal representative: two years after letters of authority",
          "If the person dies before the period runs out (or within 30 days after), the personal representative may sue within 2 years after letters of authority are issued, but never later than 3 years after the period has run.",
          "mi_5852", "MCL 600.5852",
          ["may be commenced by the personal representative of the deceased person at any time within 2 years after letters of authority are issued although the period of limitations has run.",
           "(4) Notwithstanding subsections (1) to (3), an action shall not be commenced under this section later than 3 years after the period of limitations has run."]),
    ],
}
CELLE["MI/debt"] = {
    "varianti": [V("Breach of contract (debt)", 6, "mi_5807", "MCL 600.5807(9)",
                   "(9) The period of limitations is 6 years for an action to recover damages or money due for breach of contract that is not described in subsections (2) to (8).",
                   "The period of limitations is 6 years")],
    "inizio": "From when the claim first accrued, usually the missed payment.",
    "eccezioni": [REG_F],
}
CELLE["MI/breach-of-contract"] = {
    "varianti": [V("Written or oral contract", 6, "mi_5807", "MCL 600.5807(9)",
                   "(9) The period of limitations is 6 years for an action to recover damages or money due for breach of contract that is not described in subsections (2) to (8).",
                   "The period of limitations is 6 years")],
    "inizio": "Michigan's six years apply to breach of contract whether written or oral, unless a more specific period applies.",
    "eccezioni": [
        E("Covenants in deeds and mortgages: ten years",
          "An action founded on a covenant in a deed or mortgage of real estate has ten years.",
          "mi_5807", "MCL 600.5807(5)",
          "(5) The period of limitations is 10 years for an action founded on a covenant in a deed or mortgage of real estate."),
    ],
}
CELLE["MI/property-damage"] = {
    "varianti": [V("Injury to property", 3, "mi_5805", "MCL 600.5805(2)",
                   "the period of limitations is 3 years after the time of the death or injury for all actions to recover damages for the death of a person or for injury to a person or property.",
                   "the period of limitations is 3 years after the time of the death or injury")],
    "inizio": "Three years after the time of the injury to the property.",
    "eccezioni": [],
}

# =====================================================================================================================  ARIZONA
STATI["AZ"] = {
    "nome": "Arizona", "slug": "arizona", "codice": "Arizona Revised Statutes, title 12, chapter 5",
    "regole": [
        E("Minors and people of unsound mind",
          "Time while the person with the claim is under 18 or of unsound mind (at accrual) is not counted.",
          "az_12_502", "Ariz. Rev. Stat. § 12-502",
          "is at the time the cause of action accrues either under eighteen years of age or of unsound mind, the period of such disability shall not be deemed a portion of the period limited for commencement of the action."),
        E("Defendant out of state",
          "Time while the person being sued is outside Arizona is not counted.",
          "az_12_501", "Ariz. Rev. Stat. § 12-501",
          "The time of such person's absence shall not be counted or taken as a part of the time limited by the provisions of this chapter."),
        E("Saving statute: six months",
          "If a timely case ends other than on the merits (and not by abatement, voluntary dismissal or dismissal for lack of prosecution), a new action may be filed within six months.",
          "az_12_504", "Ariz. Rev. Stat. § 12-504(A)",
          "may commence a new action for the same cause after the expiration of the time so limited and within six months after such termination."),
    ],
    "governo": [
        E("Claims against public entities: 180-day notice, one year to sue",
          "A notice of claim must be filed within 180 days, and the lawsuit within one year.",
          "az_12_821_01", "Ariz. Rev. Stat. §§ 12-821.01(A), 12-821",
          "Any claim that is not filed within one hundred eighty days after the cause of action accrues is barred and no action may be maintained thereon."),
    ],
    "cambi": [],
}
CELLE["AZ/personal-injury"] = {
    "varianti": [V("Injury to the person", 2, "az_12_542", "Ariz. Rev. Stat. § 12-542(1)",
                   ["there shall be commenced and prosecuted within two years after the cause of action accrues, and not afterward, the following actions:",
                    "1. For injuries done to the person of another including causes of action for medical malpractice as defined in section 12-561."],
                   "within two years after the cause of action accrues")],
    "inizio": "From the day the claim accrues; the section does not define it for injuries.",
    "eccezioni": [
    ],
}
CELLE["AZ/medical-malpractice"] = {
    "varianti": [V("Medical malpractice", 2, "az_12_542", "Ariz. Rev. Stat. § 12-542(1)",
                   ["there shall be commenced and prosecuted within two years after the cause of action accrues, and not afterward, the following actions:",
                    "1. For injuries done to the person of another including causes of action for medical malpractice as defined in section 12-561."],
                   "within two years after the cause of action accrues")],
    "inizio": "From the day the claim accrues; the section does not define it.",
    "eccezioni": [],
}
CELLE["AZ/wrongful-death"] = {
    "varianti": [V("Injury when death ensues", 2, "az_12_542", "Ariz. Rev. Stat. § 12-542(2)",
                   ["there shall be commenced and prosecuted within two years after the cause of action accrues, and not afterward, the following actions:",
                    "2. For injuries done to the person of another when death ensues from such injuries, which action shall be considered as accruing at the death of the party injured."],
                   "within two years after the cause of action accrues")],
    "inizio": "The statute says the action accrues at the death of the injured person.",
    "eccezioni": [],
}
CELLE["AZ/debt"] = {
    "varianti": [
        V("Written contract signed in Arizona", 6, "az_12_548", "Ariz. Rev. Stat. § 12-548(A)(1)",
          ["A. An action for debt shall be commenced and prosecuted within six years after the cause of action accrues, and not afterward, if the indebtedness is evidenced by or founded on either of the following:",
           "1. A contract in writing that is executed in this state."], "within six years after the cause of action accrues"),
        V("Credit card", 6, "az_12_548", "Ariz. Rev. Stat. § 12-548(A)(2)",
          ["A. An action for debt shall be commenced and prosecuted within six years after the cause of action accrues, and not afterward, if the indebtedness is evidenced by or founded on either of the following:",
           "2. A credit card as defined in section 13-2101, paragraph 3, subdivision (a)."], "within six years after the cause of action accrues"),
        V("Debt not in writing, or open account", 3, "az_12_543", "Ariz. Rev. Stat. § 12-543(1)-(2)",
          ["There shall be commenced and prosecuted within three years after the cause of action accrues, and not afterward, the following actions:",
           "1. For debt where the indebtedness is not evidenced by a contract in writing."], "within three years after the cause of action accrues"),
        V("Written instrument signed outside Arizona", 4, "az_12_544", "Ariz. Rev. Stat. § 12-544(3)",
          ["There shall be commenced and prosecuted within four years after the cause of action accrues, and not afterward, the following actions:",
           "3. Upon a judgment or decree of a court rendered without the state, or upon an instrument in writing executed without the state."],
          "within four years after the cause of action accrues"),
    ],
    "inizio": "From the day the claim accrues, usually the missed payment.",
    "eccezioni": [
        E("Arizona's period wins conflicts with other states",
          "For written-contract and credit card debts, if another state's deadline conflicts with Arizona's, the Arizona section applies.",
          "az_12_548", "Ariz. Rev. Stat. § 12-548(B)",
          "B. If there is a conflict between another jurisdiction and this state relating to the statute of limitations for a debt action as described in subsection A of this section, this section applies."),
        E("Open accounts: recent items keep the account alive",
          "No item of an open account is barred while any item was incurred within the three years before suit.",
          "az_12_543", "Ariz. Rev. Stat. § 12-543(2)",
          "but no item of a stated or open account shall be barred so long as any item thereof has been incurred within three years immediately prior to the bringing of an action thereon."),
        E("Acknowledging a barred debt must be in writing",
          "A later acknowledgment counts against the deadline only if written and signed.",
          "az_12_508", "Ariz. Rev. Stat. § 12-508",
          "unless the acknowledgment is in writing and signed by the party to be charged thereby."),
        REG_F,
    ],
}
CELLE["AZ/breach-of-contract"] = {
    "varianti": [
        V("Written contract signed in Arizona", 6, "az_12_548", "Ariz. Rev. Stat. § 12-548(A)(1)",
          ["A. An action for debt shall be commenced and prosecuted within six years after the cause of action accrues, and not afterward, if the indebtedness is evidenced by or founded on either of the following:",
           "1. A contract in writing that is executed in this state."], "within six years after the cause of action accrues"),
        V("Oral agreement (debt not in writing)", 3, "az_12_543", "Ariz. Rev. Stat. § 12-543(1)",
          ["There shall be commenced and prosecuted within three years after the cause of action accrues, and not afterward, the following actions:",
           "1. For debt where the indebtedness is not evidenced by a contract in writing."], "within three years after the cause of action accrues"),
    ],
    "inizio": "From the day the claim accrues, usually the breach.",
    "eccezioni": [
        E("Employment contracts: one year",
          "Breach of an oral or written employment contract (including handbooks that set no time limit) has one year.",
          "az_12_541", "Ariz. Rev. Stat. § 12-541(3)",
          "3. For breach of an oral or written employment contract including contract actions based on employee handbooks or policy manuals that do not specify a time period in which to bring an action."),
    ],
    "nota": "Arizona's contract sections are written in terms of “debt”. Whether they cover a breach that is not a claim for money owed is a question for an Arizona attorney.",
}
CELLE["AZ/property-damage"] = {
    "varianti": [
        V("Injury to the estate or property", 2, "az_12_542", "Ariz. Rev. Stat. § 12-542(3)",
          ["there shall be commenced and prosecuted within two years after the cause of action accrues, and not afterward, the following actions:",
           "3. For trespass for injury done to the estate or the property of another."], "within two years after the cause of action accrues"),
        V("Taking, detaining or converting goods", 2, "az_12_542", "Ariz. Rev. Stat. § 12-542(4)-(5)",
          ["there shall be commenced and prosecuted within two years after the cause of action accrues, and not afterward, the following actions:",
           "4. For taking or carrying away the goods and chattels of another."], "within two years after the cause of action accrues"),
    ],
    "inizio": "From the day the claim accrues; the section does not define it.",
    "eccezioni": [],
}

# =====================================================================================================================  MASSACHUSETTS
STATI["MA"] = {
    "nome": "Massachusetts", "slug": "massachusetts", "codice": "Massachusetts General Laws, chapter 260",
    "regole": [
        E("Minors and mental illness",
          "If the person with the claim is a minor or incapacitated by mental illness when it accrues, the period runs after the disability is removed.",
          "ma_260_7", "Mass. Gen. Laws c. 260, § 7",
          "If the person entitled thereto is a minor, or is incapacitated by reason of mental illness when a right to bring an action first accrues, the action may be commenced within the time hereinbefore limited after the disability is removed."),
        E("Defendant living outside Massachusetts",
          "Time while the person being sued resides out of the Commonwealth is excluded.",
          "ma_260_9", "Mass. Gen. Laws c. 260, § 9",
          "if, after a cause of action has accrued, the person against whom it has accrued resides out of the commonwealth, the time of such residence shall be excluded in determining the time limited for the commencement of the action;"),
        E("Fraudulent concealment",
          "If the person liable fraudulently conceals the claim, the period before discovery is excluded.",
          "ma_260_12", "Mass. Gen. Laws c. 260, § 12",
          "If a person liable to a personal action fraudulently conceals the cause of such action from the knowledge of the person entitled to bring it, the period prior to the discovery of his cause of action by the person so entitled shall be excluded in determining the time limited for the commencement of the action."),
    ],
    "governo": [
        E("Claims against public employers: written presentment within two years",
          "Under the Massachusetts Tort Claims Act, the claim must first be presented in writing to the public employer within two years, and suit can follow only after a denial (or six months without one).",
          "ma_258_4", "Mass. Gen. Laws c. 258, § 4",
          "unless the claimant shall have first presented his claim in writing to the executive officer of such public employer within two years after the date upon which the cause of action arose,"),
    ],
    "cambi": [],
}
CELLE["MA/personal-injury"] = {
    "varianti": [V("Tort (including personal injury)", 3, "ma_260_2a", "Mass. Gen. Laws c. 260, § 2A",
                   "Section 2A. Except as otherwise provided, actions of tort, actions of contract to recover for personal injuries, and actions of replevin, shall be commenced only within three years next after the cause of action accrues.",
                   "shall be commenced only within three years next after the cause of action accrues")],
    "inizio": "From the day the claim accrues; the section does not define it.",
    "eccezioni": [
    ],
}
CELLE["MA/medical-malpractice"] = {
    "varianti": [V("Malpractice against physicians and hospitals", 3, "ma_260_4", "Mass. Gen. Laws c. 260, § 4",
                   "Actions of contract or tort for malpractice, error or mistake against physicians, surgeons, dentists, optometrists, hospitals and sanitoria shall be commenced only within three years after the cause of action accrues,",
                   "shall be commenced only within three years after the cause of action accrues")],
    "inizio": "Three years after the claim accrues.",
    "repose": V("Statute of repose", 7, "ma_260_4", "Mass. Gen. Laws c. 260, § 4",
                "but in no event shall any such action be commenced more than seven years after occurrence of the act or omission which is the alleged cause of the injury upon which such action is based except where the action is based upon the leaving of a foreign object in the body.",
                "more than seven years after occurrence of the act or omission"),
    "eccezioni": [
        E("Foreign object left in the body",
          "The seven-year outer limit does not apply when the claim is based on a foreign object left in the body.",
          "ma_260_4", "Mass. Gen. Laws c. 260, § 4",
          "except where the action is based upon the leaving of a foreign object in the body."),
    ],
}
CELLE["MA/wrongful-death"] = {
    "varianti": [V("Wrongful death", 3, "ma_229_2", "Mass. Gen. Laws c. 229, § 2",
                   "An action to recover damages under this section shall be commenced within three years from the date of death, or within three years from the date when the deceased's executor or administrator knew, or in the exercise of reasonable diligence, should have known of the factual basis for a cause of action,",
                   "shall be commenced within three years from the date of death")],
    "inizio": "Three years from the date of death, or from when the executor or administrator knew or should have known the facts.",
    "eccezioni": [
        E("Other chapter 260 rules can extend it",
          "The section allows the extra time provided by sections 4, 4B, 9 or 10 of chapter 260.",
          "ma_229_2", "Mass. Gen. Laws c. 229, § 2",
          "or within such time thereafter as is provided by section four, four B, nine or ten of chapter two hundred and sixty."),
    ],
}
CELLE["MA/debt"] = {
    "varianti": [V("Contract (written or oral)", 6, "ma_260_2", "Mass. Gen. Laws c. 260, § 2",
                   "Section 2. Actions of contract, other than those to recover for personal injuries, founded upon contracts or liabilities, express or implied, except actions limited by section one or actions upon judgments or decrees of courts of record of the United States or of this or of any other state of the United States, shall, except as otherwise provided, be commenced only within six years next after the cause of action accrues.",
                   "be commenced only within six years next after the cause of action accrues")],
    "inizio": "From the day the claim accrues, usually the missed payment.",
    "eccezioni": [
        E("A new promise must be in writing",
          "An acknowledgment or promise takes a contract claim out of the deadline only if it is in a writing signed by the person charged.",
          "ma_260_13", "Mass. Gen. Laws c. 260, § 13",
          "unless such acknowledgment or promise has been made by, or is contained in, a writing signed by the party chargeable thereby."),
        REG_F,
    ],
    "nota": "This page covers chapter 260. Other Massachusetts laws and regulations on debt collection practices can also affect old consumer debts; ask a Massachusetts attorney.",
}
CELLE["MA/breach-of-contract"] = {
    "varianti": [V("Written or oral contract", 6, "ma_260_2", "Mass. Gen. Laws c. 260, § 2",
                   "Section 2. Actions of contract, other than those to recover for personal injuries, founded upon contracts or liabilities, express or implied, except actions limited by section one or actions upon judgments or decrees of courts of record of the United States or of this or of any other state of the United States, shall, except as otherwise provided, be commenced only within six years next after the cause of action accrues.",
                   "be commenced only within six years next after the cause of action accrues")],
    "inizio": "Six years for written and oral contracts alike, from the day the claim accrues.",
    "eccezioni": [
        E("Contract claims for personal injuries: three years",
          "A contract action to recover for personal injuries falls under the three-year section instead.",
          "ma_260_2a", "Mass. Gen. Laws c. 260, § 2A",
          "actions of contract to recover for personal injuries,"),
    ],
}
CELLE["MA/property-damage"] = {
    "varianti": [V("Tort (including damage to property)", 3, "ma_260_2a", "Mass. Gen. Laws c. 260, § 2A",
                   "Section 2A. Except as otherwise provided, actions of tort, actions of contract to recover for personal injuries, and actions of replevin, shall be commenced only within three years next after the cause of action accrues.",
                   "shall be commenced only within three years next after the cause of action accrues")],
    "inizio": "From the day the claim accrues; the section does not define it.",
    "eccezioni": [],
}

# =====================================================================================================================  MINNESOTA
STATI["MN"] = {
    "nome": "Minnesota", "slug": "minnesota", "codice": "Minnesota Statutes, chapter 541",
    "regole": [
        E("Minors and insanity (with limits)",
          "Being under 18 or insane suspends the period until the disability is removed; except for infancy, the extension cannot exceed five years, and never more than one year after the disability ends.",
          "mn_541_15", "Minn. Stat. § 541.15(a)",
          "provided that such period, except in the case of infancy, shall not be extended for more than five years, nor in any case for more than one year after the disability ceases:"),
        E("Defendant out of state",
          "Time while the person being sued is out of state and cannot be served is not counted.",
          "mn_541_13", "Minn. Stat. § 541.13",
          "the time of the person's absence is not part of the time limited for the commencement of the action."),
    ],
    "governo": [
        E("Claims against cities and other municipalities: 180-day notice",
          "Notice must be presented to the municipality within 180 days after the loss or injury is discovered (one year for a wrongful death claim).",
          "mn_466_05", "Minn. Stat. § 466.05",
          "shall cause to be presented to the governing body of the municipality within 180 days after the alleged loss or injury is discovered a notice stating the time, place and circumstances thereof,"),
    ],
    "cambi": [],
}
CELLE["MN/personal-injury"] = {
    "varianti": [
        V("Negligence and other injury to the person", 6, "mn_541_05", "Minn. Stat. § 541.05, subd. 1(5)",
          ["Except where the Uniform Commercial Code otherwise prescribes, the following actions shall be commenced within six years:",
           "(5) for criminal conversation, or for any other injury to the person or rights of another, not arising on contract, and not hereinafter enumerated;"],
          "shall be commenced within six years"),
        V("Assault, battery and other intentional torts", 2, "mn_541_07", "Minn. Stat. § 541.07(1)",
          ["the following actions shall be commenced within two years:",
           "(1) for libel, slander, assault, battery, false imprisonment, or other tort resulting in personal injury,"],
          "shall be commenced within two years"),
    ],
    "inizio": "From the day the claim accrues; the sections do not define it.",
    "eccezioni": [],
    "nota": "Minnesota has two possible periods for injuries. Section 541.07(1) gives two years for libel, slander, assault, battery, false imprisonment “or other tort resulting in personal injury”, while § 541.05 gives six years for “any other injury to the person”. Negligence claims are generally treated under the six-year period; some tables online show two years for all injuries. Ask a Minnesota attorney which applies to your claim.",
}
CELLE["MN/medical-malpractice"] = {
    "varianti": [V("Health care provider actions", 4, "mn_541_076", "Minn. Stat. § 541.076(b)",
                   "(b) An action by a patient or former patient against a health care provider alleging malpractice, error, mistake, or failure to cure, whether based on a contract or tort, must be commenced within four years from the date the cause of action accrued.",
                   "must be commenced within four years from the date the cause of action accrued")],
    "inizio": "Four years from the date the claim accrued.",
    "eccezioni": [
        E("Children: up to seven years",
          "For a minor, the period is suspended until the disability is removed, but for no more than seven years, or more than one year after the child turns 18.",
          "mn_541_15", "Minn. Stat. § 541.15(b)",
          "The suspension may not be extended for more than seven years, or for more than one year after the disability ceases."),
    ],
}
CELLE["MN/wrongful-death"] = {
    "varianti": [V("Wrongful death", 3, "mn_573_02", "Minn. Stat. § 573.02, subd. 1",
                   "Any other action under this section may be commenced within three years after the date of death provided that the action must be commenced within six years after the act or omission.",
                   "within three years after the date of death")],
    "inizio": "Three years after the date of death.",
    "repose": V("Outer limit", 6, "mn_573_02", "Minn. Stat. § 573.02, subd. 1",
                "Any other action under this section may be commenced within three years after the date of death provided that the action must be commenced within six years after the act or omission.",
                "within six years after the act or omission", nota_data="Six years from the act or omission that caused the death, which can be earlier than the date of death; the calculator uses the date you enter."),
    "eccezioni": [
        E("Deaths caused by medical negligence",
          "For a death caused by the professional negligence of a physician, hospital or similar provider: three years from death, but no later than the medical malpractice period of § 541.076.",
          "mn_573_02", "Minn. Stat. § 573.02, subd. 1",
          "shall be commenced within three years of the date of death, but in no event shall be commenced beyond the time set forth in section 541.076."),
        E("Murder: no deadline",
          "An action for a death caused by an intentional act constituting murder may be brought at any time.",
          "mn_573_02", "Minn. Stat. § 573.02, subd. 1",
          "An action to recover damages for a death caused by an intentional act constituting murder may be commenced at any time after the death of the decedent."),
    ],
}
CELLE["MN/debt"] = {
    "varianti": [
        V("Consumer debt", 6, "mn_541_053", "Minn. Stat. § 541.053",
          "actions upon an obligation arising out of a consumer debt primarily for personal, family, or household purposes shall be commenced within six years.",
          "shall be commenced within six years"),
        V("Other contract debt", 6, "mn_541_05", "Minn. Stat. § 541.05, subd. 1(1)",
          ["Except where the Uniform Commercial Code otherwise prescribes, the following actions shall be commenced within six years:",
           "(1) upon a contract or other obligation, express or implied, as to which no other limitation is expressly prescribed;"],
          "shall be commenced within six years"),
    ],
    "inizio": "From the day the claim accrues, usually the missed payment.",
    "eccezioni": [
        E("A payment does not revive an expired consumer debt",
          "Once the six years have run, collecting a payment, a bankruptcy discharge or a reaffirmation does not revive the deadline.",
          "mn_541_053", "Minn. Stat. § 541.053",
          "After its expiration, the statute of limitations is not revived by the collection of a payment on an account, a discharge in a bankruptcy proceeding, or an oral or written reaffirmation of the debt."),
        REG_F,
    ],
}
CELLE["MN/breach-of-contract"] = {
    "varianti": [V("Written or oral contract", 6, "mn_541_05", "Minn. Stat. § 541.05, subd. 1(1)",
                   ["Except where the Uniform Commercial Code otherwise prescribes, the following actions shall be commenced within six years:",
                    "(1) upon a contract or other obligation, express or implied, as to which no other limitation is expressly prescribed;"],
                   "shall be commenced within six years")],
    "inizio": "Six years for written and oral contracts alike, unless another period is expressly prescribed or the Uniform Commercial Code applies.",
    "eccezioni": [],
}
CELLE["MN/property-damage"] = {
    "varianti": [
        V("Trespass on real estate", 6, "mn_541_05", "Minn. Stat. § 541.05, subd. 1(3)",
          ["Except where the Uniform Commercial Code otherwise prescribes, the following actions shall be commenced within six years:", "(3) for a trespass upon real estate;"],
          "shall be commenced within six years"),
        V("Taking, detaining or injuring personal property", 6, "mn_541_05", "Minn. Stat. § 541.05, subd. 1(4)",
          ["Except where the Uniform Commercial Code otherwise prescribes, the following actions shall be commenced within six years:", "(4) for taking, detaining, or injuring personal property, including actions for the specific recovery thereof;"],
          "shall be commenced within six years"),
    ],
    "inizio": "From the day the claim accrues; the section does not define it.",
    "eccezioni": [
        E("Pesticide application: two years",
          "Damage to property from the application of a pesticide has two years.",
          "mn_541_07", "Minn. Stat. § 541.07(7)",
          "(7) against the person who applies the pesticide for injury or damage to property resulting from the application, but not the manufacture or sale, of a pesticide."),
    ],
}

ORDINE_STATI = ["TX", "FL", "OH", "WA", "VA", "NC", "MI", "AZ", "MA", "MN"]
ORDINE_CAUSE = list(CAUSE)
