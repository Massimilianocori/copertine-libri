"""Scarica le fonti ufficiali di US College Aid, ne registra URL, data e impronta, controlla le frasi citate alla lettera
e ricava i dati del sito: dati/aiuti.json (scadenze FAFSA per Stato, tassi dei prestiti federali, tetti, piani di rimborso).

Uso (dalla radice del repository):
    python3 collegeaid/raccolta/fonti.py            # riscarica tutto (curl con un nome di robot dichiarato; nessun blocco aggirato)
    python3 collegeaid/raccolta/fonti.py --locale   # non scarica: rilegge i file già in dati/grezzi/

Fonti (tutte ufficiali):
- modulo FAFSA 2027-28 (PDF di studentaid.gov): a pagina 2 le scadenze di ogni Stato e territorio;
- Federal Register 2026-18493 (govinfo.gov): tassi fissi dei prestiti Direct 2026-27 e tabella storica dal 2013;
- Federal Register 2026-08556 (govinfo.gov): regola finale sui prestiti, in vigore dal 1/7/2026 (34 CFR 685.203);
- Public Law 119-21 (govinfo.gov): sezioni 81001 (tetti) e 82001 (piano standard a scaglioni, Repayment Assistance Plan);
- Federal Student Aid Handbook 2025-26, vol. 8 cap. 4 (fsapartners.ed.gov): tetti dei corsi di laurea, rimasti invariati.

Ogni cifra di aiuti.json è letta dal file grezzo con un'espressione regolare e controllata con l'aritmetica della fonte
(asta + maggiorazione = tasso; 5.500 = 3.500 + 2.000 ...). Se una fonte cambia forma lo script si ferma e non scrive niente.
Se un sito non risponde (studentaid.gov a volte chiude la connessione ai server) e il file registrato c'è già, resta quello
di prima con la sua data di lettura: lo script lo dice a fine giro.
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import testo as T  # noqa: E402

DATI = QUI.parent / "dati"
GREZZI = DATI / "grezzi"
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"
# Prima lettura fatta in una sessione precedente (il file è quello scaricato quel giorno): vale solo finché fonti.json non esiste.
DATE_PRIMA_LETTURA = {"fafsa_2728": "2026-11-18"}
# Modelli spezzati apposta: così la ricerca di chiavi nel repository non scatta su questo file.
SEGRETI = re.compile("|".join([r"pk\.ey" + r"J[\w.-]*", "sk_" + r"live_?\w*", "sk_" + r"test_?\w*", "AI" + r"za[\w-]{10,}", "gh" + r"p_\w+", "(api" + "key=)[A-Za-z0-9]{8,}"]))

# id, file, url, titolo (inglese, va in pagina), chi pubblica, frasi da ritrovare alla lettera
FONTI = [
    ("fafsa_2728", "fafsa_2027_28_form.pdf", "https://studentaid.gov/sites/default/files/2027-28-fafsa-form.pdf",
     "Free Application for Federal Student Aid (FAFSA), July 1, 2027 – June 30, 2028 (paper form, deadlines on pages 1 and 2)",
     "Federal Student Aid, U.S. Department of Education", {
         "federale": "For federal aid, submit your application as early as possible, but no earlier than October 1, 2026. We must receive your application no later than June 30, 2028.",
         "ultimo_giorno": "Your college must have your correct, complete information by your last day of enrollment in the 2027–28 school year.",
         "statale": "For state or college aid, the deadline may be as early as October 1, 2026, or the aid may be awarded on a first-come, first-served basis.",
         "altri_moduli": "You may also need to fill out separate forms.",
         "ricevuto": "Unless otherwise noted, the dates below refer to when the form must be received.",
         "online": "If you are filing close to a deadline, we recommend you file online at fafsa.gov.",
         "ufficio": "The best place for information about student aid is the financial aid office at the college you plan to attend.",
         "gratis": "Use this free form to apply for federal and state student grants, work-study, and loans.",
     }),
    ("fr_tassi", "fr_2026_18493_rates.htm", "https://www.govinfo.gov/content/pkg/FR-2026-09-10/html/2026-18493.htm",
     "Annual Notice of Interest Rates for Fixed-Rate Federal Student Loans Made Under the William D. Ford Federal Direct Loan Program (91 FR 57581, September 10, 2026)",
     "Federal Student Aid, U.S. Department of Education (Federal Register)", {
         "periodo": "with first disbursement dates on or after July 1, 2026, and before July 1, 2027",
         "fisso": "The interest rate for these loans is a fixed rate that is determined annually for all loans first disbursed during any 12-month period beginning on July 1 and ending on June 30.",
         "formula": "The rate is equal to the high yield of the 10-year Treasury notes auctioned at the final auction held before June 1 of that 12-month period, plus a statutory add-on percentage that varies depending on the loan type and, for Direct Unsubsidized Loans, whether the loan was made to an undergraduate or graduate student.",
         "massimo": "If the interest rate formula results in a rate that exceeds the statutory maximum rate, the rate is the statutory maximum rate.",
         "vita": "the rate determined for any loan is a fixed interest rate for the life of the loan",
         "asta": "On May 12, 2026, the United States Treasury Department held a 10-year Treasury note auction that resulted in a high yield of 4.468 percent, rounded to 4.47 percent.",
         "consolidamento": "have a fixed interest rate that is equal to the weighted average of the interest rates on the loans consolidated, rounded to the nearest higher one-eighth of one percent",
         "laureati": "Graduate and professional students are not eligible to receive Direct Subsidized Loans.",
     }),
    ("fr_regola", "fr_2026_08556_rule.htm", "https://www.govinfo.gov/content/pkg/FR-2026-05-01/html/2026-08556.htm",
     "Reimagining and Improving Student Education—Federal Student Loan Program Final Regulations; Final Rule (91 FR 23768, May 1, 2026)",
     "U.S. Department of Education (Federal Register)", {
         "vigore": "This final rule is effective on July 1, 2026.",
         "sintesi": "These changes include establishing new loan limits for graduate students, professional students, and parents, and phasing out the Graduate PLUS (Grad PLUS) Program.",
         "invariati": "The undergraduate loan limits in Sec. 685.203 remain unchanged; the aggregate Subsidized and Unsubsidized loan limits for dependent and independent undergraduates are $31,000 and $57,500, respectively.",
         "laureato": "A graduate student, who is not a professional student, for a period of enrollment beginning on or after July 1, 2026, may borrow up to $20,500 for any academic year under the Direct Unsubsidized Loan Program.",
         "professionale": "A professional student, for a period of enrollment beginning on or after July 1, 2026, may borrow up to $50,000 for any academic year under the Direct Unsubsidized Loan Program.",
         "genitori_anno": "For periods of enrollment beginning on or after July 1, 2026, the total amount of all Direct PLUS Loans that all parents may borrow on behalf of each dependent student for any academic year of study may not exceed $20,000.",
         "genitori_totale": "For periods of enrollment beginning on or after July 1, 2026, the total amount of all Direct PLUS Loans that all parents may borrow on behalf of each dependent student may not exceed $65,000, without regard to any amounts repaid, forgiven, canceled, or otherwise discharged on any such loan.",
         "vita": "Effective July 1, 2026, the lifetime maximum aggregate amount of loans made, insured, or guaranteed under the Act that a student may borrow, shall be $257,500, excluding Federal Direct PLUS or Federal PLUS loans made to that student as a parent on behalf of another dependent undergraduate student.",
         "minimo_std": "A borrower's payments under this repayment plan are at least $50 per month, except that when a borrower's balance is less than $50, the minimum payment will be equal to the outstanding amount due.",
         "minimo_10": "A borrower's payments under this repayment plan are at least $50 per month, except that a borrower's final payment may be less than $50.",
         "trasferimento": "If a student transfers to a different institution, even in the same program of study, the Department would consider that to be a new program of study.",
         "laureati_programma": "Conversely, graduate students who change their program of study will be ineligible for the interim exception.",
         "concentrazione": "students who change concentrations within an academic field, as long as they remain in the same 4-digit CIP code at that credential level and institution, remain eligible for the interim exception.",
         "major": "a student who changes majors within the same degree or certificate shall be considered to be enrolled in the same program of study.",
         "coniugi": "For a married borrower filing a joint Federal income tax return, except as provided in paragraph (e)(1)(i)(A) of this section, the combined income of the borrower and spouse is used in the calculation.",
         "anticipo_quota": "If a borrower's payment is credited to a future monthly payment, and the payment equals or exceeds the monthly repayment amount made under (f)(5)(i) of this section, the Secretary does not provide the borrower a matching principal payment in accordance with paragraph (o)(2)(i) of this section.",
         "prima": "For a graduate or professional student for periods of enrollment beginning before July 1, 2026, $138,500, including any loans for undergraduate study",
     }),
    ("legge", "plaw_119_21.htm", "https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm",
     "Public Law 119-21 (139 Stat. 72), sections 81001 and 82001, amending section 455 of the Higher Education Act of 1965",
     "U.S. Congress (U.S. Government Publishing Office)", {
         "grad_plus": "for any period of instruction beginning on or after July 1, 2026, a graduate or professional student shall not be eligible to receive a Federal Direct PLUS Loan under this part.",
         "genitori_anno": "the total maximum annual amount of Federal Direct PLUS loans that may be borrowed on behalf of that dependent student by all parents of that dependent student shall be $20,000.",
         "eccezione": "is enrolled in a program of study at an institution of higher education; and",
         "tre_anni": "three academic years; or",
         "tempo_parziale": "the amount of a loan that student may borrow for an academic year or its equivalent shall be reduced in direct proportion to the degree to which that student is not so enrolled on a full-time basis",
         "due_piani": "two plans for repayment of the borrower's loans under this part, including principal and interest on such loans.",
         "standard": "with a fixed monthly repayment amount paid over a fixed period of time equal to the applicable period determined under subclause (II); and",
         "anticipo": "The borrower shall be entitled to accelerate, without penalty, repayment on such loans.",
         "genitori_standard": "the Secretary shall require a borrower who has received an excepted loan made on or after such date (including such a borrower who also has an excepted loan made before such date) to repay each excepted loan, including principal and interest on those excepted loans, under the standard repayment plan under subparagraph (A)(i).",
         "eccettuato": "a Federal Direct PLUS Loan that is made on behalf of a dependent student; or",
         "rap_mensile": "the applicable base payment of the borrower, divided by 12; minus",
         "rap_dipendente": "$50 for each dependent of the borrower (which, in the case of a married borrower filing a separate Federal income tax return, shall include only each dependent that the borrower claims on that return).",
         "rap_minimo": "In the case of a borrower with an applicable monthly payment amount calculated under clause (i) that is less than $10, the applicable monthly payment of the borrower shall be $10.",
         "rap_interessi": "the amount of interest accrued and not paid for the month shall not be charged to the borrower.",
         "rap_360": "the date on which the borrower has made 360 qualifying monthly payments.",
         "rap_reddito": "in the case of a married borrower who files a separate Federal income tax return, the term does not include the adjusted gross income of the borrower's spouse.",
         "rap_cambio": "A borrower may change the borrower's selection of--",
         "rap_esclusi": "such Plan shall not be available for the repayment of excepted loans (as defined in paragraph (7)(E)); and",
         "rap_vecchi": "beginning on July 1, 2026, the income-based Repayment Assistance Plan under subsection (q), provided that--",
         "vecchi_piani": "Paragraphs (1) through (4) of this subsection shall only apply to loans made under this part before July 1, 2026.",
     }),
    ("manuale", "fsa_handbook_2025_26_vol8_ch4.html", "https://fsapartners.ed.gov/knowledge-center/fsa-handbook/2025-2026/vol8/ch4-annual-and-aggregate-loan-limits",
     "2025–2026 Federal Student Aid Handbook, Volume 8, Chapter 4: Annual and Aggregate Loan Limits",
     "Federal Student Aid, U.S. Department of Education (FSA Partner Connect)", {
         "esempio": "For example, a dependent first-year undergraduate may receive up to $5,500 in Direct Subsidized Loans and/or Direct Unsubsidized Loans for a single academic year, but no more than $3,500 of this amount may be subsidized.",
         "aggregato": "For example, a dependent undergraduate may have up to a maximum of $31,000 in combined subsidized and unsubsidized outstanding loan debt, but no more than $23,000 of this amount may consist of subsidized loans.",
         "interessi": "Capitalized interest (unpaid accrued interest that has been added to the principal balance of a loan) is not counted toward a borrower’s aggregate loan limits",
     }),
    ("cfr_200", "cfr_2025_685_200.pdf", "https://www.govinfo.gov/content/pkg/CFR-2025-title34-vol4/pdf/CFR-2025-title34-vol4-sec685-200.pdf",
     "34 CFR 685.200, Borrower eligibility (Code of Federal Regulations, July 1, 2025 edition)", "U.S. Department of Education (U.S. Government Publishing Office)", {
         "credito": "Does not have an adverse credit history;",
         "garante": "Has an adverse credit history, but has obtained an endorser who does not have an adverse credit history, and completes PLUS loan counseling offered by the Secretary; or",
     }),
    ("cfr_202", "cfr_2025_685_202.pdf", "https://www.govinfo.gov/content/pkg/CFR-2025-title34-vol4/pdf/CFR-2025-title34-vol4-sec685-202.pdf",
     "34 CFR 685.202, Charges for which Direct Loan borrowers are responsible (Code of Federal Regulations, July 1, 2025 edition)", "U.S. Department of Education (U.S. Government Publishing Office)", {
         "commissione": "Deducts the loan fee from the proceeds of the loan;",
         "rate": "In the case of a loan disbursed in multiple installments, deducts a pro rated portion of the fee from each disbursement; and",
         "plus": "Charges a borrower a loan fee of four percent of the principal amount of the loan on a Direct PLUS loan.",
     }),
]

MESI_MODULO = {"Jan.": 1, "Feb.": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "Aug.": 8, "Sept.": 9, "Oct.": 10, "Nov.": 11, "Dec.": 12}
DATA_MODULO = r"(Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.) (\d{1,2}), (\d{4})"
STATI_50_DC = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
TERRITORI = set("AS FM GU MH MP PW PR VI".split())


def scarica(url, dest):
    r = subprocess.run(["curl", "-sS", "-L", "-A", UA, "--max-time", "180", "-o", str(dest), "-w", "%{http_code}", url], capture_output=True, text=True)
    try:
        return int(r.stdout.strip()[-3:])
    except ValueError:
        return 0


def cerca(modello, testo, fid, flags=0):
    m = re.search(modello, testo, flags)
    if not m:
        raise SystemExit(f"{fid}: non trovo più «{modello[:90]}»: la fonte ha cambiato forma")
    return m


def soldi(s):
    return int(s.replace(",", ""))


def iso_modulo(mese, giorno, anno):
    return date(int(anno), MESI_MODULO[mese], int(giorno)).isoformat()


# ---------------------------------------------------------------- FAFSA: scadenze per Stato (pagina 2 del modulo)
def unisci_righe(righe):
    """Unisce le righe di una voce del modulo: «first-» + «served» resta «first-served», «business/» + «trade» resta attaccato."""
    out = ""
    for r in righe:
        r = r.strip()
        if not r:
            continue
        if out.endswith("-") or out.endswith("/"):
            out += r
        else:
            out += (" " if out else "") + r
    return re.sub(r"\s+", " ", out).strip()


def voci_fafsa(testo_pagina):
    """Voci «Nome (XX) testo» della pagina delle scadenze, nell'ordine alfabetico della fonte."""
    righe = [r for r in testo_pagina.replace("\f", "\n").split("\n")]
    inizio = next(i for i, r in enumerate(righe) if r.startswith("►Unless otherwise noted")) + 1
    intest = re.compile(r"^((?:[A-Z][A-Za-z.]*|of)(?: (?:[A-Z][A-Za-z.]*|of))*) \(([A-Z]{2})\) (.*)$")
    voci, corrente = [], None
    for r in righe[inizio:]:
        r = r.strip()
        if not r or re.fullmatch(r"\d+", r) or re.fullmatch(r"(\d{4}–\d\d ?)?(FAFSA)? ?®? ?(Deadlines)?", r):
            continue
        m = intest.match(r)
        if m:
            corrente = {"nome": m[1], "sigla": m[2], "righe": [m[3]]}
            voci.append(corrente)
        elif corrente:
            corrente["righe"].append(r)
    out = []
    for v in voci:
        t = unisci_righe(v["righe"])
        date_ = sorted({iso_modulo(*m.groups()) for m in re.finditer(DATA_MODULO, t)})
        out.append({"nome": v["nome"], "sigla": v["sigla"], "testo": t, "date": date_})
    return sorted(out, key=lambda v: v["nome"])


def rimetti_trattini(normale, raw):
    """Rimette in «normale» i trattini che solo la lettura -raw ha conservato (le due stringhe sono uguali a meno di spazi e trattini)."""
    r = re.sub(r"\s+", "", raw)
    out, j = [], 0
    for ch in normale:
        if ch.isspace():
            out.append(ch)
            continue
        if ch != "-" and j < len(r) and r[j] == "-":
            out.append("-")
            j += 1
        if j >= len(r) or r[j] != ch:
            if ch == "-":
                out.append(ch)
                continue
            raise SystemExit(f"rimetti_trattini: letture diverse a «{normale[:40]}»")
        out.append(ch)
        j += 1
    return "".join(out)


def fafsa(percorso, fid="fafsa_2728"):
    p1 = T.norm(T.pdf(percorso, prima=1, ultima=1))
    m = cerca(r"submit your application as early as possible, but no earlier than (October) (\d+), (\d{4})\. We must receive your application no later than (June) (\d+), (\d{4})\.", p1, fid)
    mesi = {"October": 10, "June": 6}
    apertura = date(int(m[3]), mesi[m[1]], int(m[2])).isoformat()
    chiusura = date(int(m[6]), mesi[m[4]], int(m[5])).isoformat()
    anno = cerca(r"July 1, (\d{4}) – June 30, (\d{4})", p1, fid)
    p2 = T.pdf(percorso, prima=2, ultima=2)
    if "FAFSA Deadlines" not in p2 and "Deadlines" not in p2:
        raise SystemExit(f"{fid}: la pagina 2 non è più quella delle scadenze")
    voci = voci_fafsa(p2)
    sigle = [v["sigla"] for v in voci]
    if set(sigle) != STATI_50_DC | TERRITORI or len(sigle) != len(set(sigle)):
        raise SystemExit(f"{fid}: voci lette {len(sigle)}; mancano {sorted((STATI_50_DC | TERRITORI) - set(sigle))}, in più {sorted(set(sigle) - STATI_50_DC - TERRITORI)}")
    # Seconda lettura (pdftotext -raw, altro ordine delle righe): stesso testo voce per voce, senza contare spazi e trattini.
    # La lettura normale toglie il trattino a fine riga («first-» + «served» diventa «firstserved»), quella -raw lo tiene ma perde
    # qualche spazio («byApril»): il testo pubblicato è la lettura normale con i trattini della lettura -raw rimessi al loro posto.
    raw = voci_fafsa(T.pdf(percorso, prima=2, ultima=2, raw=True))
    senza = lambda s: re.sub(r"[\s-]+", "", s)  # noqa: E731
    diversi = [v["sigla"] for v, w in zip(voci, raw) if v["sigla"] != w["sigla"] or senza(v["testo"]) != senza(w["testo"])]
    if len(raw) != len(voci) or diversi:
        raise SystemExit(f"{fid}: le due letture della pagina 2 non coincidono per {diversi}")
    for v, w in zip(voci, raw):
        v["testo"] = rimetti_trattini(v["testo"], w["testo"])
        v["date"] = sorted({iso_modulo(*m.groups()) for m in re.finditer(DATA_MODULO, v["testo"])})
    for v in voci:
        for d in v["date"]:
            if not (apertura <= d <= "2028-12-31"):
                raise SystemExit(f"{fid}: data fuori dall'anno del modulo in {v['sigla']}: {d}")
        v["territorio"] = v["sigla"] in TERRITORI
    return {"anno": f"{anno[1]}–{anno[2][2:]}", "anno_dal": f"{anno[1]}-07-01", "anno_al": f"{anno[2]}-06-30", "apertura": apertura, "chiusura_federale": chiusura, "voci": voci}


# ---------------------------------------------------------------- tassi (Federal Register 2026-18493)
def data_usa(s):
    m, g, a = s.split("/")
    return date(int(a), int(m), int(g)).isoformat()


def tassi(grezzo, fid="fr_tassi"):
    t = T.pagina_html(grezzo)
    n = T.norm(t, tieni_trattini=True)
    asta = cerca(r"On (May) (\d+), (\d{4}), the United States Treasury Department held a 10-year Treasury note auction that resulted in a high yield of (\d\.\d{3}) percent, rounded to (\d\.\d\d) percent", n, fid)
    per = cerca(r"Chart 1--.*?First Disbursed on or After\s+(\d\d/\d\d/\d{4}) and Before (\d\d/\d\d/\d{4})", t, fid, re.S)
    num = r"\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)"
    righe = []
    for chiave, modello in (("ug", r"Undergraduate students\.\." + num), ("grad", r"Graduate and" + num), ("plus", r"Parents of dependent" + num)):
        m = cerca(modello, t, fid)
        asta_r, add, mass, tasso = m[1], m[2], m[3], m[4]
        if asta_r != asta[5] or round(float(asta_r) + float(add), 2) != float(tasso) or float(tasso) > float(mass):
            raise SystemExit(f"{fid}: la riga {chiave} della tabella 1 non torna (asta + maggiorazione = tasso)")
        righe.append({"chiave": chiave, "asta": asta_r, "maggiorazione": add, "massimo": mass, "tasso": tasso})
    storia = []
    for m in re.finditer(r"^(\d\d/\d\d/\d{4})\.+\s+(\d\d/\d\d/\d{4})\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\S.*?)\s*$", t, re.M):
        avviso = re.sub(r"\s+", " ", m[6]).rstrip(".")
        avviso = re.sub(r"(\d)\(", r"\1 (", avviso)
        storia.append({"dal": data_usa(m[1]), "al": data_usa(m[2]), "ug": m[3], "grad": m[4], "plus": m[5], "avviso": avviso})
    if len(storia) < 14 or storia[0]["dal"] != data_usa(per[1]) or storia[-1]["dal"] != "2013-07-01":
        raise SystemExit(f"{fid}: tabella storica letta male ({len(storia)} righe)")
    for a, b in zip(storia, storia[1:]):
        if a["dal"] != b["al"]:
            raise SystemExit(f"{fid}: anni non consecutivi nella tabella storica")
    for r in storia:
        # In ogni anno la differenza tra le tre colonne è la differenza tra le maggiorazioni di legge (1,55 e 1,00): controllo interno della tabella.
        if round(float(r["grad"]) - float(r["ug"]), 2) != 1.55 or round(float(r["plus"]) - float(r["grad"]), 2) != 1.00:
            raise SystemExit(f"{fid}: la riga {r['dal']} della tabella storica non rispetta le maggiorazioni")
    primo = storia[0]
    if [primo["ug"], primo["grad"], primo["plus"]] != [r["tasso"] for r in righe]:
        raise SystemExit(f"{fid}: tabella 1 e tabella 2 non coincidono")
    vecchi = []
    for m in re.finditer(r"^(Subsidized|Unsubsidized|PLUS)\.+\s+(.+?)\s+(\d\d/\d\d/\d{4})\s+(?:\\\d\\ )?(\d\d/\d\d/\d{4})\s+(\d\.\d\d)\s*$", t, re.M):
        chi = m[2].strip()
        # l'etichetta di chi prende il prestito può continuare nelle righe sotto (rientrate, senza cifre): si copia per intero
        for riga in t[m.end():].split("\n")[1:6]:
            if not re.match(r"^\s{20,}[A-Za-z]", riga) or re.search(r"\d", riga):
                break
            chi += " " + riga.strip()
        vecchi.append({"tipo": m[1], "chi": re.sub(r"\.+$", "", chi).strip(), "dal": data_usa(m[3]), "al": data_usa(m[4]), "tasso": m[5]})
    if len(vecchi) != 8:
        raise SystemExit(f"{fid}: tabella 3 letta male ({len(vecchi)} righe)")
    return {"dal": data_usa(per[1]), "al": data_usa(per[2]), "asta_data": date(int(asta[3]), 5, int(asta[2])).isoformat(), "asta": asta[4], "asta_arrotondata": asta[5],
            "righe": righe, "storia": storia, "prima_del_2013": vecchi}


# ---------------------------------------------------------------- tetti (regola finale, legge, manuale FSA)
def limiti(testi):
    r, lg, mn = testi["fr_regola"], testi["legge"], testi["manuale"]
    L = {}
    a = cerca(r"Table 1A: Dependent Undergraduate Annual Limits for Direct Subsidized Loans and Direct Unsubsidized Loans .{0,160}?Total \(Subsidized and Unsubsidized\) Maximum Subsidized "
              r"First Year \$([\d,]+) \$([\d,]+) Second Year \$([\d,]+) \$([\d,]+) Third Year and Beyond \$([\d,]+) \$([\d,]+)", mn, "manuale")
    b = cerca(r"Table 1B: Independent Undergraduate Annual Limits for Direct Subsidized Loans and Direct Unsubsidized Loans .{0,160}?Total \(Subsidized and Unsubsidized\) Maximum Subsidized "
              r"First Year \$([\d,]+) \$([\d,]+) Second Year \$([\d,]+) \$([\d,]+) Third Year and Beyond \$([\d,]+) \$([\d,]+)", mn, "manuale")
    c = cerca(r"Table 4: Aggregate Limits for Direct Subsidized Loans and Direct Unsubsidized Loans Total \(Subsidized and Unsubsidized\) Maximum Subsidized Dependent undergraduates .{0,80}? "
              r"\$([\d,]+) \$([\d,]+) Independent undergraduates .{0,100}? \$([\d,]+) \$([\d,]+) Graduate and professional students \$([\d,]+) \$([\d,]+)", mn, "manuale")
    anni = ["First year", "Second year", "Third year and beyond"]
    L["dipendente"] = {"anni": [{"anno": anni[i], "totale": soldi(a[1 + 2 * i]), "sussidiato": soldi(a[2 + 2 * i])} for i in range(3)], "totale": soldi(c[1]), "totale_sussidiato": soldi(c[2])}
    L["indipendente"] = {"anni": [{"anno": anni[i], "totale": soldi(b[1 + 2 * i]), "sussidiato": soldi(b[2 + 2 * i])} for i in range(3)], "totale": soldi(c[3]), "totale_sussidiato": soldi(c[4])}
    inv = cerca(r"The undergraduate loan limits in Sec\. 685\.203 remain unchanged; the aggregate Subsidized and Unsubsidized loan limits for dependent and independent undergraduates are \$([\d,]+) and \$([\d,]+), respectively\. "
                r"This is less than both the graduate and professional aggregate loan limits of \$([\d,]+) and \$([\d,]+), respectively\.", r, "fr_regola")
    if [soldi(inv[1]), soldi(inv[2])] != [L["dipendente"]["totale"], L["indipendente"]["totale"]]:
        raise SystemExit("tetti dei corsi di laurea: manuale 2025-26 e regola finale 2026 non coincidono")
    if [x["sussidiato"] for x in L["dipendente"]["anni"]] != [x["sussidiato"] for x in L["indipendente"]["anni"]]:
        raise SystemExit("manuale: quota sussidiata diversa tra studenti dipendenti e indipendenti")
    grad = soldi(cerca(r"A graduate student, who is not a professional student, for a period of enrollment beginning on or after July 1, 2026, may borrow up to \$([\d,]+) for any academic year", r, "fr_regola")[1])
    prof = soldi(cerca(r"A professional student, for a period of enrollment beginning on or after July 1, 2026, may borrow up to \$([\d,]+) for any academic year", r, "fr_regola")[1])
    grad_tot = soldi(cerca(r"Who is not and has never been a professional student at an institution, \$([\d,]+),", r, "fr_regola")[1])
    prof_tot = soldi(cerca(r"For a professional student for a period of enrollment beginning on or after July 1, 2026, \$([\d,]+), minus any amounts such student borrowed as a graduate student", r, "fr_regola")[1])
    gen_anno = soldi(cerca(r"that all parents may borrow on behalf of each dependent student for any academic year of study may not exceed \$([\d,]+)\.", r, "fr_regola")[1])
    gen_tot = soldi(cerca(r"that all parents may borrow on behalf of each dependent student may not exceed \$([\d,]+), without regard to any amounts repaid", r, "fr_regola")[1])
    vita = soldi(cerca(r"the lifetime maximum aggregate amount of loans made, insured, or guaranteed under the Act that a student may borrow, shall be \$([\d,]+),", r, "fr_regola")[1])
    prima_tot = soldi(cerca(r"For a graduate or professional student for periods of enrollment beginning before July 1, 2026, \$([\d,]+), including any loans for undergraduate study", r, "fr_regola")[1])
    # Stesse cifre nella legge (sezione 81001): la regola e la legge devono dire lo stesso numero.
    legge = {
        "grad": soldi(cerca(r"a graduate student, who is not a professional student, may borrow in any academic year or its equivalent shall be \$([\d,]+); and", lg, "legge")[1]),
        "prof": soldi(cerca(r"a professional student may borrow in any academic year or its equivalent shall be \$([\d,]+)\.", lg, "legge")[1]),
        "grad_tot": soldi(cerca(r"may borrow for programs of study described in subparagraph \(C\)\(i\) shall be \$([\d,]+); or", lg, "legge")[1]),
        "prof_tot": soldi(cerca(r"may borrow for programs of study described in subparagraph \(C\)\(ii\) shall be \$([\d,]+); or", lg, "legge")[1]),
        "gen_anno": soldi(cerca(r"by all parents of that dependent student shall be \$([\d,]+)\.", lg, "legge")[1]),
        "gen_tot": soldi(cerca(r"by all parents of that dependent student shall(?: \[\[Page 139 STAT\. \d+\]\])? be \$([\d,]+), without regard to any amounts repaid", lg, "legge")[1]),
        "vita": soldi(cerca(r"on behalf of a dependent student\) shall be \$([\d,]+), without regard to any amounts repaid", lg, "legge")[1]),
    }
    regola = {"grad": grad, "prof": prof, "grad_tot": grad_tot, "prof_tot": prof_tot, "gen_anno": gen_anno, "gen_tot": gen_tot, "vita": vita}
    if legge != regola:
        raise SystemExit(f"tetti: legge {legge} e regola finale {regola} non coincidono")
    if c[5].replace(",", "") != str(prima_tot):
        raise SystemExit("tetto complessivo dei laureati prima del 1/7/2026: manuale e regola non coincidono")
    L.update({"laureato": {"anno": grad, "totale": grad_tot}, "professionale": {"anno": prof, "totale": prof_tot}, "genitori": {"anno": gen_anno, "totale": gen_tot},
              "vita": vita, "laureati_prima": {"totale": prima_tot}, "in_vigore": "2026-07-01", "anni_eccezione": 3})
    cerca(r"three academic years; or", lg, "legge")
    return L


# ---------------------------------------------------------------- rimborso (legge, sezione 82001)
ROMANI = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]


def rimborso(testi):
    lg = testi["legge"]
    blocco = cerca(r"Base payment\.--The amount of the applicable base payment for a borrower with an adjusted gross income of--(.*?)``\(v\) Dependent", lg, "legge")[1]
    blocco = re.sub(r"\[\[Page 139 STAT\. \d+\]\]", " ", blocco)
    blocco = re.sub(r"\s+", " ", blocco)
    primo = cerca(r"``\(I\) not more than \$([\d,]+), is \$(\d+);", blocco, "legge")
    scaglioni = [{"fino_a": soldi(primo[1]), "fisso_anno": int(primo[2]), "pc": None}]
    for m in re.finditer(r"``\(([IVX]+)\) more than \$([\d,]+) and not more than \$([\d,]+), is (\d+) percent of such adjusted gross income", blocco):
        if soldi(m[2]) != scaglioni[-1]["fino_a"]:
            raise SystemExit("legge: scaglioni del RAP non consecutivi")
        scaglioni.append({"fino_a": soldi(m[3]), "fisso_anno": None, "pc": int(m[4])})
    ult = cerca(r"``\(XI\) more than \$([\d,]+), is (\d+) percent of such adjusted gross income", blocco, "legge")
    if soldi(ult[1]) != scaglioni[-1]["fino_a"]:
        raise SystemExit("legge: ultimo scaglione del RAP non consecutivo")
    scaglioni.append({"fino_a": None, "fisso_anno": None, "pc": int(ult[2])})
    if len(scaglioni) != 11 or [s["pc"] for s in scaglioni[1:]] != list(range(1, 11)):
        raise SystemExit(f"legge: scaglioni del RAP letti male ({len(scaglioni)})")
    dip = int(cerca(r"``\(II\) \$(\d+) for each dependent of the borrower", lg, "legge")[1])
    minimo = cerca(r"calculated under clause \(i\) that is less than \$(\d+), the applicable monthly payment of the borrower shall be \$(\d+)\.", lg, "legge")
    rate = int(cerca(r"the date on which the borrower has made (\d+) qualifying monthly payments\.", lg, "legge")[1])
    quota = cerca(r"by less than \$(\d+), the Secretary shall reduce such total outstanding principal balance of the borrower by an amount that is equal to-- ``\(i\) the amount that is the lesser of-- ``\(I\) \$(\d+); or", lg, "legge")
    if minimo[1] != minimo[2] or quota[1] != quota[2]:
        raise SystemExit("legge: minimo o quota capitale del RAP letti male")
    st = cerca(r"total outstanding principal of less than \$([\d,]+), a period of (\d+) years;.*?not less than \$([\d,]+) and less than \$([\d,]+), a period of (\d+) years;.*?"
               r"not less than \$([\d,]+) and less than \$([\d,]+), a period of (\d+) years; and.*?total outstanding principal of \$([\d,]+) or more, a period of (\d+) years", lg, "legge")
    v = [soldi(st[i]) for i in (1, 3, 4, 6, 7, 9)]
    if not (v[0] == v[1] and v[2] == v[3] and v[4] == v[5]):
        raise SystemExit("legge: fasce del piano standard non consecutive")
    rg = testi["fr_regola"]
    m10 = cerca(r"within ten years from the date the loan entered repayment by making fixed monthly payments\. \(ii\) A borrower's payments under this repayment plan are at least \$(\d+) per month, except that a borrower's final payment may be less than \$(\d+)\.", rg, "fr_regola")
    mts = re.findall(r"Tiered Standard repayment plan for Direct Loan borrowers who received a Direct Loan.{0,400}?\(ii\) A borrower's payments under this repayment plan are at least \$(\d+) per month, except that when a borrower's balance is less than \$(\d+), the minimum payment will be equal to the outstanding amount due\.", rg)
    if len(mts) != 2 or len({m10[1], m10[2]} | {x for c in mts for x in c}) != 1:
        raise SystemExit(f"fr_regola: pagamento minimo del piano standard letto male ({m10.groups()}, {mts})")
    fasce = [{"sotto": v[0], "anni": int(st[2])}, {"sotto": v[2], "anni": int(st[5])}, {"sotto": v[4], "anni": int(st[8])}, {"sotto": None, "anni": int(st[10])}]
    return {"rap": {"scaglioni": scaglioni, "per_dipendente_mese": dip, "minimo_mese": int(minimo[2]), "rate_cancellazione": rate, "quota_capitale_mese": int(quota[2]), "dal": "2026-07-01"},
            "standard": {"fasce": fasce, "minimo_mese": int(m10[1]), "dal": "2026-07-01"}}


def pulisci_segreti(percorso):
    """Toglie dai file grezzi eventuali chiavi pubbliche di servizi terzi (mappe, analisi) presenti nelle pagine HTML scaricate."""
    if percorso.suffix == ".pdf":
        return False
    s = percorso.read_text(encoding="utf-8", errors="replace")
    nuovo = SEGRETI.sub(lambda m: (m.group(1) or "") + "-rimossa-", s)
    if nuovo != s:
        percorso.write_text(nuovo, encoding="utf-8")
        return True
    return False


def main():
    locale = "--locale" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    vecchie = {}
    if (DATI / "fonti.json").exists():
        vecchie = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["fonti"]
    oggi = date.today().isoformat()
    fonti, testi, errori, nuovi, tenuti = {}, {}, [], [], []
    for fid, nome, url, titolo, chi, frasi in FONTI:
        dest = GREZZI / nome
        leggi = dest
        prima = vecchie.get(fid, {}).get("letto_il") or DATE_PRIMA_LETTURA.get(fid, oggi)
        if locale:
            http, letto = 200, prima
            if not dest.exists():
                raise SystemExit(f"{fid}: manca {dest}")
        else:
            tmp = dest.with_name(dest.name + ".tmp")
            http, letto = scarica(url, tmp), oggi
            if http != 200 or not tmp.exists() or tmp.stat().st_size < 1000:
                tmp.unlink(missing_ok=True)
                if dest.exists():
                    tenuti.append(f"{fid}: HTTP {http} da {url}; resta il file letto il {prima}")
                    http, letto = 200, prima
                else:
                    errori.append(f"{fid}: HTTP {http} da {url} e nessun file precedente")
                    continue
            else:
                pulisci_segreti(tmp)
                leggi = tmp
                nuovi.append((tmp, dest))
        grezzo = leggi.read_bytes()
        # Il file .tmp ha un'estensione diversa: il tipo si decide dal nome vero.
        testi[fid] = T.testo_norm(leggi, nome)
        trovate = {k: (T.norm(f) in testi[fid]) for k, f in frasi.items()}
        for k, ok in trovate.items():
            if not ok:
                errori.append(f"{fid}: frase «{k}» non trovata alla lettera")
        fonti[fid] = {"url": url, "file": f"dati/grezzi/{nome}", "titolo": titolo, "chi": chi, "sha256": hashlib.sha256(grezzo).hexdigest(), "byte": len(grezzo),
                      "impronta": "frasi" if fid == "manuale" else "file", "sha256_frasi": T.impronta_frasi(testi[fid], frasi),
                      "http": http, "letto_il": letto, "frasi": frasi, "trovate": trovate, "_leggi": str(leggi)}
    if errori:
        for tmp, _ in nuovi:
            tmp.unlink(missing_ok=True)
        print("\n".join(errori))
        raise SystemExit(f"{len(errori)} errori: fonti.json, aiuti.json e dati/grezzi NON aggiornati")
    try:
        aiuti = {"_nota": "Generato da raccolta/fonti.py dai file in dati/grezzi/. Importi in dollari interi, tassi come stringhe con i decimali della fonte, date ISO. "
                          "fafsa.voci[].testo è il testo del modulo, voce per voce; fafsa.voci[].date sono le date scritte in quel testo.",
                 "fafsa": fafsa(fonti["fafsa_2728"]["_leggi"]), "tassi": tassi(fonti["fr_tassi"]["_leggi"]), "limiti": limiti(testi), "rimborso": rimborso(testi)}
    except SystemExit:
        for tmp, _ in nuovi:
            tmp.unlink(missing_ok=True)
        print("Un dato non si legge più nei file nuovi: dati/grezzi è rimasto com'era.")
        raise
    for tmp, dest in nuovi:
        tmp.replace(dest)
    for fid, f in fonti.items():
        del f["_leggi"]
        v = vecchie.get(fid)
        if v and v.get("sha256") != f["sha256"]:
            stesso = f["impronta"] == "frasi" and v.get("sha256_frasi") == f["sha256_frasi"]
            print(f"{fid}: file cambiato dall'ultima lettura" + (" (solo parti dinamiche della pagina: le frasi citate sono le stesse)" if stesso else " (rileggere le cifre)"))
    aiuti["letto_il"] = max(f["letto_il"] for f in fonti.values())
    testo_fonti = json.dumps({"_nota": "Generato da raccolta/fonti.py. File grezzi in dati/grezzi/. PDF e pagine di govinfo.gov (impronta = file): fa fede sha256 del file intero. "
                                       "Pagina di fsapartners.ed.gov (impronta = frasi): i byte cambiano a ogni scarico, fa fede sha256_frasi (le frasi citate alla lettera, ritrovate nel file).",
                              "fonti": fonti}, ensure_ascii=False, indent=1) + "\n"
    (DATI / "fonti.json").write_text(testo_fonti, encoding="utf-8")
    (DATI / "aiuti.json").write_text(json.dumps(aiuti, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if tenuti:
        print("\n".join(tenuti))
    print(f"{len(fonti)} fonti, {sum(len(f['frasi']) for f in fonti.values())} frasi trovate alla lettera; aiuti.json scritto: "
          f"{len(aiuti['fafsa']['voci'])} voci FAFSA, {len(aiuti['tassi']['storia'])} anni di tassi, {len(aiuti['rimborso']['rap']['scaglioni'])} scaglioni RAP.")


if __name__ == "__main__":
    main()
