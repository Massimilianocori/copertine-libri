"""Rilegge le fonti ufficiali della sezione "Australia visas: points calculator, official fees and requirements" (dal 18/11/2026)
e scrive visaincome/dati/australia_visti.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/australia_visti.py              # rilegge le fonti e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/australia_visti.py --domanda    # rimisura anche i volumi di ricerca (circa 5 minuti)

Fonti (lette il 18/11/2026 con richieste HTTP dirette, nessun browser; i file grezzi NON si salvano nel repository)
- Department of Home Affairs (immi.homeaffairs.gov.au): le tre tabelle dei punti (subclass 189, 190, 491) e le pagine dei visti
  189, 190, 491, 482 (Skills in Demand, Core Skills e Specialist Skills), 500, 417, 462, 600, 820/801, 309/100, la pagina
  "Who can help you with your application?" e la licenza (CC BY 3.0 AU). Il testo sta nell'HTML, dentro campi nascosti in JSON
  (sequenze \\uXXXX): lo script le scioglie e toglie i marcatori.
- Federal Register of Legislation (legislation.gov.au): Migration Regulations 1994, compilazione n. 291 del 3 novembre 2026
  (F2026C01194), volume 1 (regolamento 1.03 e 2.12C, Schedule 1 = visa application charge di ogni classe di visto) e volume 3
  (Schedule 6D = test a punti); Home Affairs Legislation Amendment (2026 Measures No. 1) Regulations 2026 (F2026L00874), che dal
  1° luglio 2026 ha riscritto gli importi della Schedule 1.
- NON usata: la tabella dei prezzi di Home Affairs (pagina "current visa pricing"). La pagina è leggibile, ma gli importi non sono
  nell'HTML: arrivano da un'interfaccia separata che qui non interroghiamo. Tutti gli importi vengono quindi dalla Schedule 1.
  Per lo stesso motivo le pagine dei visti di Home Affairs non mostrano il costo ("From" senza cifra).
- LETTURE: ogni frammento è stato letto A MANO il 18/11/2026. A ogni lancio si controlla che sia ancora nella fonte: se ne manca
  uno, o se la compilazione in vigore non è più la F2026C01194, il JSON NON si aggiorna (codice 1) finché qualcuno non rilegge.
- PUNTI: ogni riga ha le parole della tabella di Home Affairs (controllate nelle tre tabelle, con il punteggio subito dopo) e la
  voce della Schedule 6D con lo stesso punteggio.
- TARIFFE: gli importi NON sono scritti a mano: si leggono dal frammento della Schedule 1 ("$6 135" -> 6135).
- DOMANDA: volumi medi mensili (Google Ads) dello strumento dei volumi, per Paese. La chiave sta fuori dal repository e viene
  letta solo dentro la shell di curl: non passa da Python, non viene stampata né scritta.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "australia_visti.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
HA = "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/"
ED_HA = "Australian Government Department of Home Affairs"
ED_LEG = "Federal Register of Legislation (Australian Government)"
COMPILAZIONE = "F2026C01194"     # compilazione n. 291 delle Migration Regulations 1994, in vigore dal 3 novembre 2026
EPUB = "https://www.legislation.gov.au/F1996B03551/2026-11-03/2026-11-03/text/original/epub/OEBPS/"
PUBBLICO_REG = "https://www.legislation.gov.au/F1996B03551/latest/text"

FONTI = {
    "pts189": {"titolo": "Points table for Skilled Independent visa (subclass 189)", "url": HA + "skilled-independent-189/points-table"},
    "pts190": {"titolo": "Points table for Skilled Nominated visa (subclass 190)", "url": HA + "skilled-nominated-190/points-table"},
    "pts491": {"titolo": "Points table for Skilled Work Regional (Provisional) visa (subclass 491)", "url": HA + "skilled-work-regional-provisional-491/points-table"},
    "v189": {"titolo": "Skilled Independent visa (subclass 189), Points-tested stream", "url": HA + "skilled-independent-189/points-tested"},
    "v190": {"titolo": "Skilled Nominated visa (subclass 190)", "url": HA + "skilled-nominated-190"},
    "v491": {"titolo": "Skilled Work Regional (Provisional) visa (subclass 491), main applicant", "url": HA + "skilled-work-regional-provisional-491/application"},
    "v482": {"titolo": "Skills in Demand visa (subclass 482)", "url": HA + "skills-in-demand-visa-subclass-482"},
    "v482core": {"titolo": "Skills in Demand visa (subclass 482), Core Skills stream", "url": HA + "skills-in-demand-visa-subclass-482/core-skills-stream"},
    "v482spec": {"titolo": "Skills in Demand visa (subclass 482), Specialist Skills stream", "url": HA + "skills-in-demand-visa-subclass-482/specialist-skills-stream"},
    "v500": {"titolo": "Student visa (subclass 500)", "url": HA + "student-500"},
    "v417": {"titolo": "Working Holiday visa (subclass 417)", "url": HA + "work-holiday-417"},
    "v417first": {"titolo": "First Working Holiday visa (subclass 417)", "url": HA + "work-holiday-417/first-working-holiday-417"},
    "v462first": {"titolo": "First Work and Holiday visa (subclass 462)", "url": HA + "work-holiday-462/first-work-holiday-462"},
    "v600": {"titolo": "Visitor visa (subclass 600)", "url": HA + "visitor-600"},
    "v600tour": {"titolo": "Visitor visa (subclass 600), Tourist stream (apply outside Australia)", "url": HA + "visitor-600/tourist-stream-overseas"},
    "v820": {"titolo": "Partner visa (apply in Australia) (subclass 820 and 801)", "url": HA + "partner-onshore"},
    "v309": {"titolo": "Partner visa (apply overseas) (subclass 309 and 100)", "url": HA + "partner-offshore"},
    "prezzi": {"titolo": "Visa fees and charges: current visa pricing table",
               "url": "https://immi.homeaffairs.gov.au/visas/getting-a-visa/fees-and-charges/current-visa-pricing"},
    "aiuto": {"titolo": "Who can help you with your application?", "url": "https://immi.homeaffairs.gov.au/help-support/who-can-help-with-your-application/overview"},
    "licenza": {"titolo": "Copyright and disclaimer", "url": "https://www.homeaffairs.gov.au/access-and-accountability/using-our-website/copyright-and-disclaimer"},
    "mara": {"titolo": "Office of the Migration Agents Registration Authority (OMARA)", "editore": "Office of the Migration Agents Registration Authority", "url": "https://www.mara.gov.au/"},
    "migexp": {"titolo": "Migration Expert, home page (the company's own description; not an official source)", "editore": "Migration Expert",
               "url": "https://www.migrationexpert.com.au/", "partner": True},
    "reg_ultima": {"titolo": "Migration Regulations 1994, latest version (page of the register)", "editore": ED_LEG, "url": PUBBLICO_REG, "legge": True},
    "reg1": {"titolo": "Migration Regulations 1994, compilation No. 291 (3 November 2026), volume 1: regulations and Schedule 1", "editore": ED_LEG,
             "url": EPUB + "document_1/document_1.html", "pubblico": PUBBLICO_REG, "legge": True},
    "reg3": {"titolo": "Migration Regulations 1994, compilation No. 291 (3 November 2026), volume 3: Schedule 6D (general points test)", "editore": ED_LEG,
             "url": EPUB + "document_3/document_3.html", "pubblico": PUBBLICO_REG, "legge": True},
    "amd": {"titolo": "Home Affairs Legislation Amendment (2026 Measures No. 1) Regulations 2026 (F2026L00874), Schedule 3: fees for visa applications",
            "editore": ED_LEG, "url": "https://www.legislation.gov.au/F2026L00874/asmade/2026-06-30/text/original/epub/OEBPS/document_1/document_1.html",
            "pubblico": "https://www.legislation.gov.au/F2026L00874/asmade/text", "legge": True},
}

# ---------------------------------------------------------------- test a punti
# (id, categoria, parole della tabella di Home Affairs, punti, controllo nelle tabelle [None = parole + " " + punti], voce della Schedule 6D)
_OCC = "the applicant's nominated skilled occupation; or (b) a closely related skilled occupation; for a period totalling at least"
PUNTI = [
    ("eta_18", "eta", "at least 18 but less than 25 years", 25, None, "6D11 not less than 18 and under 25 25"),
    ("eta_25", "eta", "at least 25 but less than 33 years", 30, None, "6D12 not less than 25 and under 33 30"),
    ("eta_33", "eta", "at least 33 but less than 40 years", 25, None, "6D13 not less than 33 and under 40 25"),
    ("eta_40", "eta", "at least 40 but less than 45 years", 15, None, "6D14 not less than 40 and under 45 15"),
    ("ing_comp", "inglese", "Competent English", 0, None, None),
    ("ing_prof", "inglese", "Proficient English", 10, None, "6D22 proficient English 10"),
    ("ing_sup", "inglese", "Superior English", 20, None, "6D21 superior English 20"),
    ("est_0", "estero", "Less than 3 years", 0, None, None),
    ("est_3", "estero", "At least 3 but less than 5 years", 5, None, f"6D31 had been employed outside Australia in: (a) {_OCC} 36 months in the 10 years immediately before that time 5"),
    ("est_5", "estero", "At least 5 but less than 8 years", 10, None, f"6D32 had been employed outside Australia in: (a) {_OCC} 60 months in the 10 years immediately before that time 10"),
    ("est_8", "estero", "At least 8 years", 15, None, f"6D33 had been employed outside Australia in: (a) {_OCC} 96 months in the 10 years immediately before that time 15"),
    ("aus_0", "australia", "Less than 1 year", 0, None, None),
    ("aus_1", "australia", "At least 1 but less than 3 years", 5, None, f"6D41 had been employed in Australia in: (a) {_OCC} 12 months in the 10 years immediately before that time 5"),
    ("aus_3", "australia", "At least 3 but less than 5 years", 10, None, f"6D42 had been employed in Australia in: (a) {_OCC} 36 months in the 10 years immediately before that time 10"),
    ("aus_5", "australia", "At least 5 but less than 8 years", 15, None, f"6D43 had been employed in Australia in: (a) {_OCC} 60 months in the 10 years immediately before that time 15"),
    ("aus_8", "australia", "At least 8 years", 20, None, f"6D44 had been employed in Australia in: (a) {_OCC} 96 months in the 10 years immediately before that time 20"),
    ("tit_dott", "titolo", "A Doctorate from an Australian educational institution or a Doctorate from another educational institution, that is of a recognised standard.", 20, None,
     "6D71 met the requirements for: (a) the award of a doctorate by an Australian educational institution; or (b) the award of a doctorate, by another educational institution, that is of a recognised standard 20"),
    ("tit_laurea", "titolo", "At least a Bachelor degree from an Australian educational institution or at least a Bachelor qualification, from another educational institution, that is of a recognised standard.", 15, None,
     "6D72 met the requirements for: (a) the award of at least a bachelor degree by an Australian educational institution; or (b) the award of at least a bachelor qualification, by another educational institution, that is of a recognised standard 15"),
    ("tit_diploma", "titolo", "A diploma or trade qualification from an Australian educational institution.", 10, None,
     "6D73 met the requirements for the award of a diploma by an Australian educational institution 10 6D74 met the requirements for the award of a trade qualification by an Australian educational institution 10"),
    ("tit_ente", "titolo", "Attained a qualification or award recognised by the relevant assessing authority for your nominated skilled occupation as being suitable for that occupation", 10, None,
     "6D75 attained a qualification or award recognised by the relevant assessing authority for the applicant's nominated skilled occupation as being suitable for the occupation 10"),
    ("spec", "specialistico", "A Masters degree by research or a Doctorate degree from an Australian educational institution that included at least 2 academic years study in a relevant field.", 10, None,
     "6D7A1 the applicant met the requirements for the award of a specialist educational qualification 10"),
    ("studio_au", "studio", "Meet the Australian study requirement", 5, None, "6D81 the applicant met the Australian study requirement 5"),
    ("anno_prof", "anno", "Completion of a Professional Year in Australia", 5, None,
     "6D61 a professional year in Australia in: (a) the applicant's nominated skilled occupation; or (b) a closely related skilled occupation; for a period totalling at least 12 months in the 48 months immediately before that time 5"),
    ("lingua", "lingua", "Hold a recognised qualification in a credentialled community language", 5, None,
     "6D91 a qualification in a particular language: (a) awarded or accredited by a body specified by the Minister in an instrument in writing for this item; and (b) at a standard for the language specified in the instrument 5"),
    ("regionale", "regionale", "You must have at least 1 degree, diploma or trade qualification from an Australian educational institution that satisfies the Australian study requirement obtained while living and studying in an eligible area of regional Australia", 5, None,
     "6D101 each of the following applied: (a) the applicant met the Australian study requirement; (b) the location of the campus or campuses at which that study was undertaken is in a designated regional area; (c) while the applicant undertook the course of study the applicant lived in a designated regional area; (d) none of the study undertaken constituted distance education 5"),
    ("partner_skill", "partner", "Your spouse or de facto partner must also be an applicant for this visa and meet age, English and skill criteria", 10,
     "and the assessment wasn't for a Subclass 485 visa. 10", "at the time of invitation to apply for the visa, had competent English 10 6D112"),
    ("partner_solo", "partner", "You are single or your partner is an Australian citizen or permanent resident", 10,
     "You are single or your partner is an Australian citizen or permanent resident* 10",
     "6D112 Either: (a) the applicant does not have a spouse or de facto partner; or (b) the applicant has a spouse or de facto partner who is an Australian permanent resident or an Australian citizen 10"),
    ("partner_ing", "partner", "Your spouse or de facto partner must also be an applicant for this visa and has competent English", 5,
     "must not be an Australian permanent resident or an Australian citizen. 5",
     "6D113 The spouse or de facto partner of the applicant (the primary applicant): (a) is an applicant for the same subclass of visa as the primary applicant; and (b) is not an Australian permanent resident or an Australian citizen; and (c) at the time of invitation to apply for the visa, had competent English 5"),
]
# nomina: solo nella tabella del visto indicato
NOMINA = [
    ("nom_190", "190", "pts190", "You were invited to apply for a Subclass 190 (Skilled — Nominated) visa and the nominating State or Territory government agency has not withdrawn the nomination", 5,
     "6D121 The applicant has been invited to apply for a Subclass 190 (Skilled—Nominated) visa, and the nominating State or Territory government agency has not withdrawn the nomination 5"),
    ("nom_491", "491", "pts491", "You were invited to apply for a Skilled Work Regional (Provisional) visa (subclass 491) because you were nominated and the nominating State or Territory government agency has not withdrawn that nomination or You are being sponsored for a Skilled Work Regional (Provisional) visa (subclass 491) by a family member and the Minister has accepted that sponsorship", 15,
     "6D131 The applicant has been invited to apply for a Subclass 489 (Skilled—Regional) (Provisional) visa or a Subclass 491 (Skilled Work Regional (Provisional)) visa, and: (a) the nominating State or Territory government agency has not withdrawn the nomination; or (b) if the applicant is sponsored by a family member, the Minister has accepted the sponsorship 15"),
]

# ---------------------------------------------------------------- visa application charge (Schedule 1)
_T = "Item Component Amount 1 Base application charge ${} 2 Additional applicant charge for an applicant who is at least 18 ${} 3 Additional applicant charge for an applicant who is less than 18 ${}"
_TS = "Item Component Amount 1 Base application charge ${} 2 Additional applicant charge for any other applicant who is at least 18 ${} 3 Additional applicant charge for any other applicant who is less than 18 ${}"
_WH = "is not, and has not previously been, in Australia as the holder of a Subclass {} visa other than an offshore COVID-19 affected visa—${}; or ({}) for any other applicant—${}"
# visto -> voce della Schedule 1 (inizio della voce nel testo), righe: (id, chi paga [inglese, per la pagina], frammento, tipo)
# tipo "tab": base / adulto in più / minore in più; "uno": un solo importo; "due": due importi (primo visto, visti successivi)
TARIFFE = {
    "189": {"voce": "1137", "classe": "Skilled—Independent (Permanent) (Class SI)", "inizio": "1137 Skilled—Independent (Permanent) (Class SI) (1) Form", "finestra": 6000, "righe": [
        ("std", "Main applicant, Points-tested stream", "(b) for any other applicant: First instalment—Visas in the Points-tested stream etc. " + _T.format("6 135", "3 070", "1 540"), "tab"),
        ("pac", "Passport of a Pacific-regional country", "First instalment—Visas in the Points-tested stream etc. " + _T.format("5 030", "2 515", "1 260"), "tab"),
        ("seconda", "Second instalment: applicant aged 18 or over without functional English", "(b) is assessed as not having functional English; and (c) is an applicant to whom item 1A does not apply $4,885", "uno")]},
    "190": {"voce": "1138", "classe": "Skilled—Nominated (Permanent) (Class SN)", "inizio": "1138 Skilled—Nominated (Permanent) (Class SN) (1) Form", "finestra": 4500, "righe": [
        ("std", "Main applicant", "(ii) for any other applicant: First instalment " + _T.format("6 140", "3 070", "1 535"), "tab"),
        ("pac", "Passport of a Pacific-regional country", "First instalment " + _T.format("5 035", "2 515", "1 260"), "tab"),
        ("seconda", "Second instalment: applicant aged 18 or over without functional English", "(b) is assessed as not having functional English; and (c) is an applicant to whom item 1A does not apply $4 885", "uno")]},
    "491": {"voce": "1241", "classe": "Skilled Work Regional (Provisional) (Class PS)", "inizio": "1241 Skilled Work Regional (Provisional) (Class PS) (1) Form", "finestra": 6500, "righe": [
        ("std", "Main applicant", "(ii) for any other applicant: First instalment " + _T.format("6 140", "3 070", "1 535"), "tab"),
        ("pac", "Passport of a Pacific-regional country", "First instalment " + _T.format("5 035", "2 515", "1 260"), "tab"),
        ("seconda", "Second instalment: applicant aged 18 or over without functional English", "(b) is assessed as not having functional English $4,890", "uno")]},
    "482": {"voce": "1240", "classe": "Skills in Demand (Class GK)", "inizio": "1240 Skills in Demand (Class GK) (1) Form", "finestra": 5500, "righe": [
        ("std", "Main applicant", "(iii) for any other applicant: First instalment " + _T.format("4 015", "4 015", "1 005"), "tab"),
        ("pac", "Passport of a Pacific-regional country", "First instalment " + _T.format("3 290", "3 290", "825"), "tab")]},
    "500": {"voce": "1222", "classe": "Student (Temporary) (Class TU)", "inizio": "1222 Student (Temporary) (Class TU) (1) Form", "finestra": 12000, "righe": [
        ("std", "Main applicant", "(ii) for any other applicant: First instalment " + _TS.format("2 500", "1 530", "500"), "tab"),
        ("asean", "Passport of a country listed in subitem (5A), or enrolment in an ELICOS or non-award course", "First instalment " + _TS.format("2 050", "1 255", "410"), "tab"),
        ("pac", "Passport of a Pacific-regional country", "First instalment " + _T.format("745", "555", "185"), "tab")]},
    "417": {"voce": "1225", "classe": "Working Holiday (Temporary) (Class TZ)", "inizio": "1225 Working Holiday (Temporary) (Class TZ) (1) Form", "finestra": 5500, "righe": [
        ("std", "First Working Holiday visa; second or third visa", _WH.format("417 (Working Holiday)", "840", "iii", "1 000"), "due")]},
    "462": {"voce": "1224A", "classe": "Work and Holiday (Temporary) (Class US)", "inizio": "1224A Work and Holiday (Temporary) (Class US) (1) Form", "finestra": 7500, "righe": [
        ("std", "First Work and Holiday visa; second or third visa", _WH.format("462 (Work and Holiday)", "840", "iv", "1 000"), "due"),
        ("pac", "Passport of a Pacific-regional country", "who holds a valid passport issued by a Pacific-regional country—$690", "uno")]},
    "600": {"voce": "1236", "classe": "Visitor (Class FA)", "inizio": "1236 Visitor (Class FA) (1) Form", "finestra": 6000, "righe": [
        ("std", "Applying from outside Australia", "who is outside Australia at the time of application, the base application charge is $250", "uno"),
        ("dentro", "Applying in Australia", "for an applicant who does not hold a valid passport issued by a Pacific-regional country, to whom subparagraphs (i) and (ii) do not apply, and who is in Australia at the time of application, the base application charge is $630", "uno"),
        ("pac", "Passport of a Pacific-regional country, outside Australia", "who is outside Australia at the time of application, the base application charge is $205", "uno"),
        ("pac_dentro", "Passport of a Pacific-regional country, in Australia", "who is in Australia at the time of application, the base application charge is $515", "uno"),
        ("frequente", "Frequent Traveller stream", "for an applicant who does not hold a valid passport issued by a Pacific-regional country, the base application charge is $1 845", "uno")]},
    "820": {"voce": "1124B", "classe": "Partner (Residence) (Class BS)", "inizio": "1124B Partner (Residence) (Class BS) (1) Form", "finestra": 25000, "righe": [
        ("std", "Main applicant (most cases)", "(xvii) for any other applicant: First instalment " + _T.format("11 710", "5 860", "2 935"), "tab"),
        ("pac", "Passport of a Pacific-regional country", "(C) who holds a valid passport issued by a Pacific-regional country; or whose application is combined, or sought to be combined, with an application made by that person: First instalment " + _T.format("9 600", "4 805", "2 405"), "tab"),
        ("pmv", "Holder of a Prospective Marriage visa (subclass 300)", "(E) does not hold a valid passport issued by a Pacific-regional country; or whose application is combined, or sought to be combined, with an application made by that person: First instalment " + _T.format("1 955", "980", "485"), "tab")]},
    "309": {"voce": "1129", "classe": "Partner (Migrant) (Class BC)", "inizio": "1129 Partner (Migrant) (Class BC) (1) Form", "finestra": 3500, "righe": [
        ("std", "Main applicant", "(iii) for any other applicant: First instalment " + _T.format("11 710", "5 860", "2 935"), "tab"),
        ("pac", "Passport of a Pacific-regional country", "First instalment " + _T.format("9 600", "4 805", "2 405"), "tab")]},
}

# ---------------------------------------------------------------- letture (frammenti parola per parola)
LETTURE = {
    # test a punti: Home Affairs
    "pt_invito": ("pts189", "Under the SkillSelect model, the Department of Home Affairs invite skilled workers to apply for a Skilled Independent visa (subclass 189) based on the claims presented in their expression of interest (EOI) in SkillSelect."),
    "pt_deve": ("pts189", ["The applicant must:", "satisfy most criteria specified in the points test at the time of invitation", "provide documents to support all claims made in their EOI."]),
    "pt_soddisfa": ("pts189", "satisfy most criteria specified in the points test at the time of invitation"),
    "pt_documenti": ("pts189", "provide documents to support all claims made in their EOI."),
    "pt_lavoro_occ": ("pts189", "You can only claim points for employment if the employment was in your nominated skilled occupation or a closely related skilled occupation; and you were employed for the relevant periods set out in the table, in the 10 years before you are invited to apply.", {"valore": 10}),
    "pt_lavoro_20h": ("pts189", "Employed means engaged in an occupation for remuneration for at least 20 hours a week.", {"valore": 20}),
    "pt_tetto": ("pts189", "The maximum number of points that can be awarded is 20, this means that even if you score more than 20 combined points for your employment experience only 20 points will be awarded.", {"valore": 20}),
    "pt_titolo_piu_alto": ("pts189", "For points based migration you will receive points for your highest qualification only."),
    "pt_phd": ("pts189", "You can only be awarded points for a doctoral degree if you have completed a qualification at the relevant level, that is, a Doctor of Philosophy (PhD)."),
    "pt_studio": ("pts189", "You must have at least 1 degree, diploma or trade qualification from an Australian educational institution that meets the Australian study requirement."),
    "pt_anno": ("pts189", "To be eligible for the award of these points your Professional Year must have been in Accounting, ICT/Computing or Engineering"),
    "pt_lingua": ("pts189", "To be credentialled in a community language and eligible for the award of points you must have been accredited at the paraprofessional level or above, certified at the certified provisional level or above, or have a community language credential for interpreting or translating by the National Accreditation Authority for Translators and Interpreters"),
    "pt_regionale": ("pts189", "have been obtained while you lived in, and studied at a campus in, a designated regional area"),
    "pt_partner_stesso": ("pts189", "For you to be eligible for the award of these points your partner must be an applicant for the same visa subclass and must not be an Australian permanent resident or an Australian citizen."),
    "pt_partner_stato": ("pts189", "If your marital status changes during the processing of your visa, we may not award you points for this item."),
    "pt_nomina_190": ("pts190", "You must be nominated to be invited to apply for this visa. Provided your nomination remains in effect, you may be eligible for the award of these points."),
    "pt_nomina_491": ("pts491", "You must have been nominated or stated you would be sponsored by an eligible family member to be invited to apply for this visa."),
    # test a punti: Schedule 6D
    "l6d_titolo": ("reg3", "Schedule 6D—General points test for General Skilled Migration visas mentioned in subregulation 2.26AC(1)"),
    "l6d_tetto": ("reg3", "6D51 (1) If an applicant has a qualification mentioned in Part 6D.3 and a qualification mentioned in Part 6D.4, and the combined number of points that would be awarded under those Parts for the qualifications is more than 20 points: (a) the Minister must give the applicant 20 points under this Part for the qualifications; and (b) no points are given under Part 6D.3 or 6D.4.", {"valore": 20}),
    # 189
    "v189_devi": ("v189", ["have an occupation on the relevant skilled occupation list", "have a suitable skills assessment for the occupation", "be invited to apply for this visa", "satisfy the points test"]),
    "v189_puoi": ("v189", ["work and study anywhere in Australia", "sponsor eligible relatives for permanent residence", "if eligible, become an Australian citizen"]),
    "v189_eta": ("v189", "You must be aged under 45 when we invite you to apply for the visa. You can still apply for the visa if you turn 45 after we invite you to apply.", {"valore": 45}),
    "v189_65": ("v189", "If you do not obtain a score of 65 points you will not be invited to apply for this visa.", {"valore": 65}),
    "v189_65_piu": ("v189", "If we do invite you to apply for the visa, your invitation will state the number of points that you must score when we assess your application for grant of the visa (this score may be higher than 65 points, depending on your claims in the EOI).", {"valore": 65}),
    "v189_inglese": ("v189", "At the time of invitation, you must have at least competent English"),
    "v189_concessione": ("v189", "From 1 July 2026, a lower visa cost applies to eligible Pacific Island and Timor-Leste citizens who lodge a valid visa application."),
    "v189_stima": ("v189", "To work out what your visa will cost, use the Visa Pricing Estimator"),
    # 190
    "v190_devi": ("v190", ["have an occupation on the relevant skilled list", "have a suitable skills assessment for the occupation", "be invited to apply for this visa", "satisfy the points test"]),
    "v190_65": ("v190", "If you do not obtain a score of 65 points you will not be invited to apply for this visa.", {"valore": 65}),
    "v190_seconda": ("v190", "The second instalment charge for family members is AUD4,885.", {"valore": 4885}),
    # 491
    "v491_devi": ("v491", ["be nominated to apply by a state or territory government agency, or an eligible relative must sponsor you", "have an occupation on a relevant skilled occupation list", "have a suitable skills assessment for the occupation", "be invited to apply", "satisfy the points test."]),
    "v491_puoi": ("v491", ["stay in Australia for 5 years", "live, work and study in a designated regional area of Australia", "travel to and from Australia as many times as you want, while the visa is valid", "apply for permanent residence after 3 years from the time your visa is granted."], {"valore": 5}),
    "v491_eta": ("v491", "You must be aged under 45 to be invited to apply for the visa.", {"valore": 45}),
    "v491_3anni": ("v491", "You cannot apply for other permanent visas until you have held your subclass 491 visa for 3 years.", {"valore": 3}),
    # 482
    "v482_cosa": ("v482", "This temporary visa lets an employer sponsor a suitably skilled worker to fill a position they can't find a suitably skilled Australian to fill."),
    "v482_devi": ("v482", "Have an approved sponsor and be nominated for the visa"),
    "v482core_devi": ("v482core", ["be nominated to work in an occupation on the Core Skills Occupation List (CSOL)", "be paid the Annual Market Salary Rate (AMSR) for the occupation and no less than the Core Skills Income Threshold (CSIT)", "have at least 1 year relevant work experience in your nominated occupation or a related field", "have a relevant skills assessment if this is required for your occupation", "work only for your sponsor or associated entity, unless you are exempt", "meet minimum standards of English language proficiency unless you are exempt from needing to show this."]),
    "v482core_durata": ("v482core", "Up to 4 years. Hong Kong passport holders may stay up to 5 years.", {"valore": 4}),
    "v482spec_devi": ("v482spec", ["be nominated to work in an Australian and New Zealand Standard Classification of Occupations (ANZSCO) occupation listed in Major Groups 1,2,4,5 or 6. The salary must meet the Specialist Skills Income Threshold", "have at least 1 year relevant work experience in your nominated occupation or a related field"]),
    "reg_csit": ("reg1", "core skills income threshold means $73,150. Note: This amount is indexed under regulation 5.42A.", {"valore": 73150}),
    "reg_ssit": ("reg1", "specialist skills income threshold means $135,000. Note: This amount is indexed under regulation 5.42A.", {"valore": 135000}),
    "reg_indice": ("reg1", "indexation day means the first 1 July to occur after the commencement of this regulation and each later 1 July."),
    # 500
    "v500_devi": ("v500", ["be enrolled in a course of study in Australia and hold a valid Confirmation of Enrolment (CoE) when we decide your visa", "hold Overseas Student Health Cover (OSHC), or fall in one of the exemption categories", "be 6 years or older", "prove you have a welfare arrangement, if you are under 18"]),
    "v500_fuori": ("v500", "From 2 October 2026, most Student visa applications must be lodged outside Australia."),
    "v500_puoi": ("v500", ["participate in an eligible course of study in Australia", "travel in and out of Australia", "work up to 48 hours a fortnight when your course of study or training is in session."], {"valore": 48}),
    "v500_durata": ("v500", "Up to 6 years and in line with your enrolment.", {"valore": 6}),
    "v500_denaro": ("v500", "You must have enough money to pay for your stay in Australia."),
    "v500_costi": ("v500", ["12-month living costs are for:", "students - AUD29,710", "partners coming with you - AUD10,394", "a child coming with you - AUD4,449."], {"valore": 29710}),
    "v500_scuola": ("v500", "If you are including any school-age children in your application, add schooling costs of at least AUD13,502 per year for each child.", {"valore": 13502}),
    "v500_reddito": ("v500", "Alternatively, you can give evidence that your parents or your partner had a personal annual income of at least AUD87,856 in the 12 months before you apply. If you bring family members, your parents' or partner's income must be at least AUD102,500 in the 12 months before you apply.", {"valore": 87856}),
    "v500_genuino": ("v500", ["be a genuine student for entry", "be able to show an understanding that studying in Australia is the primary reason of your Student visa."]),
    "v500_concessione": ("v500", "A lower visa cost applies to eligible Pacific Island and Timor-Leste citizens, eligible ASEAN citizens and applicants in the ELICOS and Non-Award sector who lodge a valid Student visa application."),
    "reg_5a": ("reg1", "(5A) For the purposes of subparagraphs (2)(a)(ib) and (ic) and (3)(da)(i), the following countries are specified: (a) Brunei; (b) Cambodia; (c) Indonesia; (d) Laos; (e) Malaysia; (f) Myanmar; (g) Philippines; (h) Singapore; (i) Thailand; (j) Vietnam."),
    # 417 / 462
    "v417_devi": ("v417", ["Must be 18 to 30 years old (or 35 years old for some countries)", "Must have a passport from an eligible country or jurisdiction", "Must not be accompanied by dependent children"], {"valore": 30}),
    "v417_primo": ("v417first", ["hold a passport from an eligible country or jurisdiction", "be 18 to 30 years old (or 35 years old for some countries)", "apply online from outside Australia", "not be accompanied by dependent children", "apply on your own."], {"valore": 30}),
    "v417_denaro": ("v417first", "This is usually about AUD5,000 for your initial stay, plus the fare to where you are going after leaving Australia.", {"valore": 5000}),
    "v417_puoi": ("v417first", ["do short-term work in Australia to help pay for your holiday", "study for up to 4 months", "travel to and from Australia as many times as you want", "do 3 months of specified work to become eligible for a second Working Holiday visa"], {"valore": 4}),
    "v462_primo": ("v462first", ["have a passport from an eligible country", "be 18 to 30 years old (inclusive)", "apply from outside Australia", "not be accompanied by dependent children", "apply on your own."], {"valore": 30}),
    "v462_denaro": ("v462first", "This is usually about AUD5,000 for your initial stay, plus the fare to where you are going after leaving Australia.", {"valore": 5000}),
    "v462_concessione": ("v462first", "From 1 July 2026, a lower visa cost applies to eligible Papua New Guinea passport holders who lodge a valid first Work and Holiday (subclass 462) visa application."),
    "reg_417_eta": ("reg1", "(3AA) The applicant is aged at least 18 and no more than: (a) unless paragraph (b) applies—35; or (b) if the instrument mentioned in subitem (3) specifies a younger age for the foreign country that issued the passport the applicant holds (or, if paragraph (3BC)(b) applies, held)—that younger age.", {"valore": 35}),
    "reg_462_eta": ("reg1", "(aab) The applicant must be aged at least 18 and no more than: (i) unless subparagraph (ii) applies—35; or (ii) if the instrument mentioned in paragraph (a) specifies a younger age for the foreign country that issued the passport the applicant holds (or, if paragraph (aaa) applies, held)—that age.", {"valore": 35}),
    # 600
    "v600_cosa": ("v600", "For tourists, business visitors or to visit family for 3, 6 or 12 months"),
    "v600_devi": ("v600", ["be a genuine visitor", "have enough funds to support your stay and leave"]),
    "v600_tour": ("v600tour", ["intend to come to Australia to visit only", "have enough money for your stay in Australia", "not work in Australia", "you must be outside Australia when you apply and when we decide your visa"]),
    "v600_denaro": ("v600tour", "You must have, or have access to, enough money to support yourself while you are in Australia."),
    "v600_durata": ("v600tour", "Up to 12 months", {"valore": 12}),
    # partner
    "v820_cosa": ("v820", "Allows the partner or spouse of an Australian citizen, Australian permanent resident or eligible New Zealand citizen to live in Australia. You apply for the temporary and the permanent partner visas together."),
    "v820_devi": ("v820", "In most circumstances, you must be the spouse (married) or de facto partner of an: Australian citizen Australian permanent resident or eligible New Zealand citizen"),
    "v309_devi": ("v309", "You must be in a genuine relationship with your spouse or de facto partner who is: an Australian citizen Australian permanent resident eligible New Zealand citizen"),
    "reg_1214c": ("reg1", "1214C Partner (Temporary) (Class UK) (1) Form: The approved form specified by the Minister in a legislative instrument made for this item under subregulation 2.07(5). (2) Visa application charge: Nil. (3) Other: (a) Application must be made at the same time and place as an application for a Partner (Residence) (Class BS) visa."),
    "reg_1220a": ("reg1", "(2) Visa application charge: Nil. (3) Other: (a) An application must be made at the place, and in the manner, (if any) specified by the Minister in a legislative instrument made for this item under subregulation 2.07(5). (b) Applicant must be outside Australia. (c) Application must be made at the same time and place as an application for a Partner (Migrant) (Class BC) visa."),
    # tariffe: regole generali
    "reg_212c": ("reg1", "the visa application charge (if any) in relation to an application for a visa of a class to which an item of Schedule 1 relates is the sum of: (a) the first instalment (which is payable when the application is made), consisting of the following components: (i) the base application charge or the additional applicant charge; (ii) any subsequent temporary application charge; (iii) any non-Internet application charge; and (b) the second instalment (which is payable before the grant of the visa)."),
    "reg_alternativi": ("reg1", "Base application charge and additional applicant charge are alternatives. An applicant does not pay both components for the one application."),
    "reg_familiare": ("reg1", "Additional applicant charge is paid by an applicant who claims to be a member of the family unit of another applicant and seeks to combine the application with that applicant's application."),
    "reg_successiva": ("reg1", "(6) The amount of subsequent temporary application charge is $700.", {"valore": 700}),
    "reg_pacifico": ("reg1", "Pacific-regional country means each of the following: (a) Federated States of Micronesia; (b) Fiji; (c) Kiribati; (d) Nauru; (e) Palau; (f) Papua New Guinea; (g) Republic of the Marshall Islands; (h) Samoa; (i) Solomon Islands; (j) Timor-Leste; (k) Tonga; (l) Tuvalu; (m) Vanuatu."),
    "reg_compilazione": ("reg1", "Compilation No. 291 Compilation date: 3 November 2026"),
    "reg_testo": ("reg1", "This is a compilation of the Migration Regulations 1994 that shows the text of the law as amended and in force on 3 November 2026"),
    "amd_data": ("amd", "1. The whole of this instrument 1 July 2026."),
    "amd_titolo": ("amd", "Schedule 3—Fees for visa applications"),
    "pr_tabella": ("prezzi", "Use the Visa Prices table to help find the price of your visa. The table groups visas by what you plan to do in Australia."),
    "pr_concessione": ("prezzi", "For some visas, a lower visa cost may apply if you are an eligible citizen of a Pacific Island country, Timor-Leste or an ASEAN member country and you lodge a valid visa application."),
    "pr_stima": ("prezzi", "To work out your visa cost, use the Visa Pricing Estimator"),
    "pr_aggiornata": ("prezzi", "Last updated: 1/07/2026"),
    # chi può aiutare
    "ai_solo": ("aiuto", "Only certain people can help you with your visa application. This help is immigration assistance."),
    "ai_chi": ("aiuto", ["If you appoint someone to give you immigration assistance, they must be:", "a registered migration agent", "a legal practitioner, or", "an exempt person"]),
    "mara_nome": ("mara", "Welcome to the Office of the Migration Agents Registration Authority"),
    # partner (parole del suo sito: servono solo al riquadro, oggi spento)
    "me_agenti": ("migexp", "Registered Australian Migration Agents"),
    "me_consulto": ("migexp", "Book a consultation to discuss your visa options with our Registered Migration Agents in Australia."),
    "ai_prima": ("v189", "If you are getting help with your visa, before you pay someone, read information on Who can help with your visa application"),
    # licenza
    "lic_cc": ("licenza", "All material presented on this website is provided under a Creative Commons Attribution 3.0 Australia licence"),
    "lic_attr": ("licenza", "You should attribute material you get from this website as Australian Government Department of Home Affairs."),
}

# Frasi misurate (strumento dei volumi): Paese -> frasi
PAESI_DOMANDA = ["au", "in", "gb", "us"]
QUERY = ["pr points calculator", "australia pr points calculator", "australia points calculator", "australian immigration points calculator",
         "189 visa points calculator", "skilled migration points calculator", "points test australia", "australia pr points", "189 visa points",
         "190 visa points", "491 visa points", "australia visa points calculator", "immigration points calculator australia",
         "189 visa", "190 visa", "491 visa", "482 visa", "skills in demand visa", "500 visa", "student visa australia", "417 visa", "462 visa",
         "working holiday visa australia", "work and holiday visa australia", "600 visa", "visitor visa australia", "australia tourist visa",
         "partner visa australia", "820 visa", "309 visa", "801 visa", "spouse visa australia",
         "australia visa fees", "australian visa fees", "visa application charge", "australia visa cost", "189 visa cost", "189 visa fees", "190 visa cost",
         "190 visa fees", "491 visa cost", "491 visa fees", "482 visa cost", "482 visa fees", "student visa australia cost", "australian student visa fees",
         "student visa fees australia", "partner visa australia cost", "partner visa cost", "partner visa fees australia", "working holiday visa australia cost",
         "417 visa cost", "australia tourist visa fees", "australia visitor visa fees", "600 visa cost", "australia visa price",
         "189 visa requirements", "190 visa requirements", "491 visa requirements", "482 visa requirements", "student visa australia requirements",
         "partner visa australia requirements", "working holiday visa australia requirements", "visitor visa australia requirements",
         "australia tourist visa requirements", "working holiday visa australia age limit", "189 visa age limit", "491 visa to pr",
         "migration agent", "registered migration agent", "australia visa", "australian visa", "australia pr", "australia pr requirements",
         "how many points for australian pr", "australia immigration points", "australia skilled visa"]


def get(u, tentativi=4):
    for i in range(tentativi):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180)
            return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, b""
            time.sleep(5 + 10 * i)
    return 0, b""


def norm(t):
    t = (t or "").replace("​", "").replace("\xa0", " ").replace("‑", "-").replace("’", "'").replace("‘", "'")
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r" ([.,;:])", r"\1", t)


def testo(b, legge=False):
    """Testo normalizzato. Home Affairs: il contenuto è in campi nascosti in JSON (\\uXXXX, \\n, \\"): si sciolgono prima di togliere i marcatori.
    Legislazione: i trattini dentro i marcatori escono come ' - ' ('Pacific - regional'): si richiudono."""
    t = b.decode("utf-8", "replace")
    if not legge:
        t = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), t)
        t = t.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ").replace('\\"', '"').replace("\\/", "/")
        t = html.unescape(t)
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    t = norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))
    if legge:
        t = re.sub(r"(?<=\w) - (?=\w)", "-", t)
        t = t.replace(" — ", "—")
    return t.replace("( ", "(").replace(" )", ")")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def numeri(fr):
    """Importi in dollari scritti nel frammento: '$6 135' o '$4,885' -> 6135, 4885."""
    return [int(re.sub(r"[ ,]", "", x)) for x in re.findall(r"\$(\d{1,3}(?:[ ,]\d{3})*)", fr)]


def volume(q, paese):
    """Una frase, un Paese. La chiave è letta dalla shell dentro curl: non entra mai in Python."""
    url = "https://api.seodata.dev/v1/keyword?q=" + urllib.parse.quote(q) + "&country=" + paese
    r = subprocess.run(["bash", "-c", 'curl -s -m 60 -w "\\n%{http_code}" "$U" -H "Authorization: Bearer $(cat /root/.config/seodata/key)"'],
                       env={**os.environ, "U": url}, capture_output=True, text=True, timeout=90)
    corpo, _, codice = r.stdout.rpartition("\n")
    try:
        d = json.loads(corpo)
    except ValueError:
        d = {}
    if codice == "200" and "volume" in d:
        return {"volume": d.get("volume"), "cpc": d.get("cpc")}
    if codice == "404":
        return {"volume": None, "cpc": None}   # frase non nel database: nessun volume misurato
    raise SystemExit(f"strumento dei volumi: risposta {codice} per «{q}» ({paese}): domanda non aggiornata")


def nuova_domanda():
    out = {}
    for p in PAESI_DOMANDA:
        for q in QUERY:
            out[f"{p}|{q}"] = volume(q, p)
            time.sleep(0.2)
    return {"data": date.today().isoformat(), "metodo": "strumento dei volumi (api.seodata.dev /v1/keyword): volume medio mensile di Google Ads e costo per clic, per Paese; null = frase non nel database",
            "paesi": PAESI_DOMANDA, "query": out}


def main():
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    oggi = date.today().isoformat()
    fonti, testi, errori = {}, {}, []
    for k, f in FONTI.items():
        st, b = get(f["url"])
        legge = bool(f.get("legge"))
        fonti[k] = {"titolo": f["titolo"], "editore": f.get("editore", ED_HA), "url": f["url"], "http": st, "letto_il": oggi, "byte": len(b)}
        if f.get("partner"):
            fonti[k]["partner"] = True
        if f.get("pubblico"):
            fonti[k]["pubblico"] = f["pubblico"]
        testi[k] = testo(b, legge) if st == 200 and b else ""
        fonti[k]["sha256_testo"] = sha(testi[k].encode()) if testi[k] else None
        if st != 200:
            errori.append(f"{k}: HTTP {st} ({f['url']})")
        if not legge:
            m = re.search(r"Last updated: (\d{1,2}/\d{1,2}/\d{4})", testi[k])
            fonti[k]["aggiornata"] = m.group(1) if m else None
        time.sleep(1.5)
    if COMPILAZIONE not in testi.get("reg_ultima", ""):
        errori.append(f"la compilazione in vigore delle Migration Regulations non è più la {COMPILAZIONE}: rileggere Schedule 1 e Schedule 6D")
    # letture
    letture = {}
    for k, v in LETTURE.items():
        fonte, fr = v[0], v[1]
        opz = dict(v[2]) if len(v) > 2 else {}
        if isinstance(fr, list):   # elenco puntato della fonte: i pezzi, uno dopo l'altro, devono dare il testo della fonte
            opz["elenco"] = fr
            fr = " ".join(fr)
        if fr not in testi.get(fonte, ""):
            errori.append(f"{k}: frammento non trovato in {fonte}: {fr[:90]}…")
        letture[k] = {"fonte": fonte, "frammento": fr, **opz}
    # punti
    i6 = testi["reg3"].rfind("Schedule 6D—General points test")
    s6d = testi["reg3"][i6:i6 + 12000] if i6 >= 0 else ""
    punti = []
    for pid, cat, parole, n, controllo, legge in PUNTI:
        c = controllo or f"{parole} {n}"
        for t in ("pts189", "pts190", "pts491"):
            if c not in testi[t]:
                errori.append(f"punti {pid}: «{c[:70]}» non trovato nella tabella {t}")
        if legge and legge not in s6d:
            errori.append(f"punti {pid}: voce della Schedule 6D non trovata: {legge[:70]}…")
        if legge and not legge.endswith(f" {n}") and not f" {n} " in legge:
            errori.append(f"punti {pid}: la voce della Schedule 6D non ha il punteggio {n}")
        punti.append({"id": pid, "categoria": cat, "parole": parole, "punti": n, "fonte": "pts189", "legge": legge, "voce": legge.split(" ")[0] if legge and legge[:2] == "6D" else ("6D111" if pid == "partner_skill" else None)})
    nomina = []
    for pid, visto, fonte, parole, n, legge in NOMINA:
        if f"{parole} {n}" not in testi[fonte]:
            errori.append(f"nomina {pid}: riga non trovata in {fonte}")
        if legge not in s6d:
            errori.append(f"nomina {pid}: voce della Schedule 6D non trovata")
        nomina.append({"id": pid, "visto": visto, "parole": parole, "punti": n, "fonte": fonte, "legge": legge, "voce": legge.split(" ")[0]})
    # tariffe
    s1 = testi["reg1"].find("Schedule 1—Classes of visa (regulations 2.01 and 2.07) Note")
    sch1 = testi["reg1"][s1:] if s1 >= 0 else ""
    if not sch1:
        errori.append("Schedule 1 non trovata nel volume 1")
    tariffe = {}
    for visto, v in TARIFFE.items():
        i = sch1.find(v["inizio"])
        seg = sch1[i:i + v["finestra"]] if i >= 0 else ""
        if not seg:
            errori.append(f"tariffe {visto}: voce {v['voce']} non trovata")
        righe = []
        for rid, chi, fr, tipo in v["righe"]:
            if fr not in seg:
                errori.append(f"tariffe {visto}/{rid}: frammento non trovato nella voce {v['voce']}: {fr[:80]}…")
            nn = numeri(fr)
            attesi = {"tab": 3, "uno": 1, "due": 2}[tipo]
            if len(nn) != attesi:
                errori.append(f"tariffe {visto}/{rid}: attesi {attesi} importi, letti {nn}")
            # l'importo è stato fissato dal regolamento del 1° luglio 2026? (stessi importi nella stessa forma nel testo di modifica)
            pezzi = re.findall(r"\$\d{1,3}(?:[ ,]\d{3})*", fr)
            in_amd = all(p in testi["amd"] for p in pezzi) and (f"{v['voce']}(" in testi["amd"])
            righe.append({"id": rid, "chi": chi, "frammento": fr, "tipo": tipo, "importi": nn, "dal_1_luglio": in_amd})
        tariffe[visto] = {"voce": v["voce"], "classe": v["classe"], "righe": righe}
    if errori:
        print("NON aggiornato:\n  " + "\n  ".join(errori))
        sys.exit(1)
    domanda = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda", {})
    if not domanda:
        domanda = nuova_domanda()
    cont = {"url": {k: f["url"] for k, f in fonti.items()}, "letture": letture, "punti": punti, "nomina": nomina, "tariffe": tariffe, "domanda": domanda}
    out = {"_nota": "Generato da raccolta/australia_visti.py: non modificare a mano. Letture, punti e tariffe sono frammenti dei testi ufficiali, ricontrollati a ogni lancio; gli importi si leggono dai frammenti.",
           "letto_il": oggi, "compilazione": {"id": COMPILAZIONE, "numero": 291, "data": "2026-11-03"}, "modifica": {"id": "F2026L00874", "dal": "2026-07-01"},
           "fonti": fonti, "letture": letture, "punti": punti, "nomina": nomina, "tariffe": tariffe, "domanda": domanda}
    out["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(letture)} letture, {len(punti) + len(nomina)} righe di punti, {len(tariffe)} voci di tariffa, domanda del {domanda.get('data')}")


if __name__ == "__main__":
    main()
