"""Scarica le fonti ufficiali (commissioni immobiliari di Texas, Alabama, Nebraska e Hawaii), ne registra URL, data e impronta
SHA-256, controlla le frasi citate alla lettera e ricava i dati del sito: dati/tassi.json (esami e promossi per scuola,
requisiti e tariffe della licenza).

Uso (dalla radice del repository):
    python3 realestate/raccolta/fonti.py            # riscarica tutto (curl con un nome di robot dichiarato; nessun blocco aggirato)
    python3 realestate/raccolta/fonti.py --locale   # non scarica: rilegge i file già in dati/grezzi/

Uscite: dati/fonti.json (una voce per fonte: url, file, sha256, letto_il, http, frasi trovate) e dati/tassi.json.
Ogni cifra di tassi.json viene dal file grezzo: dal JSON del Texas, dalle schede HTML dell'Alabama, dalle tabelle del PDF delle Hawaii,
da espressioni regolari sui testi (ore, età, tariffe). Solo il Nebraska è una trascrizione a mano (dati/manuali/ne_q1_2026.json: il PDF
è una scansione), legata all'impronta del PDF e controllata con l'aritmetica delle sue righe. Se una fonte cambia forma lo script si
ferma e dati/grezzi resta com'era («tutto o niente»).

Nessun dato su persone: solo scuole (aziende ed enti) e numeri aggregati di esami.
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import testo as T  # noqa: E402

DATI = QUI.parent / "dati"
GREZZI = DATI / "grezzi"
MANUALI = DATI / "manuali"
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"
SOGLIA_CAMPIONE = 30   # sotto questo numero di esami la percentuale è segnata «small sample» in pagina

# id, file, url, titolo (inglese, va in pagina), chi pubblica, frasi da ritrovare alla lettera
FONTI = [
    # ------------------------------------------------------------ Texas
    ("tx_tassi", "tx_passrates_rei.json", "https://www.trec.texas.gov/sites/default/files/json/PassRatesRei.json",
     "Education provider exam passage rates, sales agents and brokers (data file loaded by the official page)", "Texas Real Estate Commission", {}),
    ("tx_pagina", "tx_passrates_pagina.html", "https://www.trec.texas.gov/education/education-provider-exam-passage-rates-sales-agents-and-brokers",
     "Provider Exam Passage Rates for Sales Agents and Brokers", "Texas Real Estate Commission", {
         "sales": "The percentage of students who passed the Sales Agent licensing exam on their first attempt, within the past two years.",
         "affiliazione": "If a student took the majority of his or her qualifying courses from the same provider in the two years prior to taking the licensing exam for the first time, the student's exam results are attributed to that provider.",
         "totale": "The Overall Provider Statistics row at the top of the table contains the combined data for all students included in the table, no matter their provider affiliation.",
         "mpr": "Minimum Pass Rate (MPR) is equal to 80% of the Overall Pass Rate.",
         "standing": "A provider whose Overall Pass Rate is greater than or equal to the Minimum Pass Rate (MPR) benchmark is considered in good standing.",
     }),
    ("tx_licenza", "tx_sales_agent.html", "https://www.trec.texas.gov/become-licensed/sales-agent",
     "Become a Real Estate Sales Agent", "Texas Real Estate Commission", {
         "sponsor": "A sales agent must be sponsored by a licensed Broker in order to perform any act of real estate services.",
         "realm": "If you do not have a TREC license number, register for a REALM Portal account to receive a pre-license education application number by email.",
         "tasse": "Application fees are non-refundable and non-transferable.",
         "eta": "18 years of age or older",
         "ore": "A sales agent applicant must complete 180 classroom hours of the following qualifying real estate courses:",
         "prima": "Do not submit your license application until you have completed all required pre-licensing education.",
         "anno": "Your application expires one year from the date it is filed. You must complete all license requirements within that one-year period.",
         "impronte": "You are required by law to have fingerprints on file with the Texas Department of Public Safety (DPS) so a background check can be performed.",
         "pearson": "License exams are administered by Pearson, a testing service company.",
         "tre": "If you fail either exam three times, you will be required to complete additional education before you can test again.",
         "inattiva": "After meeting the above requirements, you will be issued an inactive license. You must be sponsored by a broker to move to active status and be able to practice brokerage activity.",
     }),
    ("tx_tariffe", "tx_fee_schedule.html", "https://www.trec.texas.gov/agency-information/fee-schedule",
     "Fee Schedule Effective September 1, 2026", "Texas Real Estate Commission", {
         "titolo": "Fee Schedule Effective September 1, 2026",
         "esame": "Real Estate Sales Examination Fee, paid to exam provider",
         "impronte": "Fingerprint Fee – paid to IDEMIA if the applicant has not previously been fingerprinted for TREC.",
     }),
    # ------------------------------------------------------------ Alabama
    ("al_tassi", "al_school_stats.html", "https://arec.alabama.gov/apps/SchoolStatsWF/",
     "Exam Pass Rates by School", "Alabama Real Estate Commission", {
         "periodo": "Data reflects the previous 12 months and is updated the 10th of every month.",
         "definizione": "The displayed school statistics represent the number of students who have taken and passed the license examination on their first attempt (1st) and the total number of students who have taken and passed the license examination, including retakes (All).",
     }),
    ("al_licenza", "al_become.html", "https://arec.alabama.gov/pages/consumer/tools/becomerep.aspx",
     "Become a Licensed Real Estate Professional", "Alabama Real Estate Commission", {
         "eta": "Be at least 19 years old;",
         "diploma": "Show proof of high school graduation or the equivalent;",
         "residenza": "Show proof of bona fide residency in any state in the U.S.;",
         "ore": "Prior to taking the state exam, successfully complete an approved 60 clock hour prelicense course. Applicants have 6 months to pass the state exam after completing the course. If these deadlines are not met, the course must be retaken.",
         "post": "Must complete a 30 hour post license training course within the first twelve months of licensure in order to be issued an original (permanent) license.",
     }),
    ("al_domanda", "al_app_instructions.html", "https://arec.alabama.gov/pages/professionals/licensing/app_instructions.aspx",
     "License Application Instructions", "Alabama Real Estate Commission", {
         "novanta": "The completed applications, all additional materials and fees MUST be complete and submitted to the Alabama Real Estate Commission within 90 days of your examination date.",
         "nullo": "Failure to meet this deadline will mean your exam score is null and void.",
         "tariffe": "Fees vary depending upon the license-type you are seeking. Refer to the license application for an accurate accounting of the fees owed.",
         "impronte": "Applicants must submit to a fingerprint-based federal and state criminal background check",
     }),
    ("al_esame", "al_exam_locations.html", "https://arec.alabama.gov/pages/professionals/edu/exam_locations.aspx",
     "Exam Scheduling", "Alabama Real Estate Commission", {
         "pearson": "To find license examination locations and schedule the license examination, please visit Pearson at home.pearsonvue.com/al/realestate or call 888-926-9488.",
     }),
    # ------------------------------------------------------------ Nebraska
    ("ne_indice", "ne_exam_performance_index.pdf", "https://nrec.nebraska.gov/sites/default/files/doc/Education/examperformancebyschool.pdf",
     "License Examination Performance by School", "Nebraska Real Estate Commission", {
         "cosa": "This report shows the performance on the Nebraska real estate license examination by school for candidates taking the examination for the first time during the reporting period.",
         "soglie": "The number of correct questions necessary to pass the National exam is 60/80. The number of correct questions necessary to pass the State exam is 38/50.",
         "cautela": "The Commission would caution readers to be aware of the total number of students that are being tested from any school.",
         "piccoli": "percentages have less to tell when the number of students is quite small.",
     }),
    # Regola (revisione del 14/11/2026): del Nebraska si usa SOLO un rapporto collegato dall'indice ufficiale qui sopra (ne_indice), mai un file
    # raggiunto indovinando l'indirizzo. Il giro si ferma se questo indirizzo non è tra i collegamenti dell'indice. Trimestre nuovo = quando l'indice lo collega.
    ("ne_tassi", "ne_school_pass_report_2026_q1.pdf",
     "https://nrec.nebraska.gov/sites/default/files/doc/Education/School%20Reports/School%20Pass%20Report%20firstquarter2026.pdf",
     "Exam Performance Summary by School, 1st Quarter 2026 (report posted by the commission)", "Nebraska Real Estate Commission", {
         "intervallo": "Date Range: 01-Jan-2026 to 31-Mar-2026",
     }),
    ("ne_licenza", "ne_salesperson_information.pdf", "https://nrec.nebraska.gov/sites/default/files/doc/Application/salesperson%20information.pdf",
     "Resident Real Estate Salesperson Information", "Nebraska Real Estate Commission", {
         "ore": "CURRENT REQUIREMENT- 96 HOURS TOTAL",
         "eta": "At least 19 years old",
         "tempi": "The typical application process takes approximately 4-8 weeks.",
         "trenta": "Your license must be issued within 30 days from passing the exam.",
         "valida": "Your application and background report is only valid for 1 year from the date the application is received.",
         "eo": "Purchase an E&O Insurance policy that meets the Nebraska requirements.",
         "voto": "Exam score of 75%",
     }),
    ("ne_tariffe", "ne_fees.pdf", "https://nrec.nebraska.gov/sites/default/files/doc/Commission/fees.pdf",
     "Fee Schedule", "Nebraska Real Estate Commission", {
         "domanda": "License Application Fee - Salespersons & Brokers",
         "esame": "License Examination Fee - Salespersons & Brokers - per exam",
         "licenza": "Salesperson Original License Fee (current year only)",
         "data": "Updated January 2026",
     }),
    ("ne_esame", "ne_examination_process.pdf", "https://nrec.nebraska.gov/sites/default/files/doc/Application/examinationprocess.pdf",
     "Real Estate Examination Information", "Nebraska Real Estate Commission", {
         "pearson": "Schedule the exam online through Pearson or by phone at 800-819-3966.",
         "ripetere": "Applicants may retake the examination multiple times during their eligibility period.",
         "tassa": "Examination appointments and fees are required for each retake.",
     }),
    # ------------------------------------------------------------ Hawaii
    ("hi_tassi", "hi_school_files_2610.pdf", "https://cca.hawaii.gov/wp-content/uploads/2026/10/sf2610.pdf",
     "School Files, October 2026 (pass-fail rates, July to September 2026 and one year rolling)", "Hawaii Real Estate Commission", {
         "titolo": "JULY – SEPTEMBER 2026 STATS AND ONE YEAR ROLLING",
     }),
    ("hi_licenza", "hi_salesperson_flowchart.pdf", "https://cca.hawaii.gov/wp-content/uploads/2026/01/190605.salesflowchart.pdf",
     "General Steps on Becoming a Hawaii Licensed Real Estate Salesperson on Active Status", "Hawaii Real Estate Commission", {
         "ore": "Successfully complete a 60 hour Hawaii salesperson prelicensing course.",
         "certificato": "School Completion Certificates are valid two (2) years from the date of issuance",
         "domanda": "Within two (2) years of passing the Hawaii salesperson’s examination, submit a complete application for a Hawaii real estate salesperson’s license.",
         "attivo": "To be licensed on active status, the applicant must be employed or associated with a current and active Hawaii licensed real estate brokerage firm or sole proprietor.",
     }),
    ("hi_requisiti", "hi_exam_prerequisites.html", "https://cca.hawaii.gov/reb/real_ed-exam_lic-exam_info-exam_prereq/",
     "Examination Prerequisites", "Hawaii Real Estate Commission", {
         "eta": "You must be at least 18 years of age as of the date of the examination.",
         "diploma": "You must have earned a high school diploma or equivalent",
         "cittadinanza": "You must be a United States citizen, a United States national, or an alien authorized to work in the United States.",
     }),
    ("hi_prelicenza", "hi_prelicensing.html", "https://cca.hawaii.gov/reb/general-prelicensing-information-and-prelicense-school-resources/",
     "General Prelicensing Information", "Hawaii Real Estate Commission", {
         "psi": "PSI administers the Hawaii real estate licensing examination.",
     }),
    ("hi_tariffe", "hi_fees.html", "https://cca.hawaii.gov/reb/application-registration-fees/",
     "Application / Registration Fees", "Hawaii Real Estate Commission", {
         "licenza": "Odd numbered year – $382 Even numbered year – $282 Renewal – $268",
     }),
    ("hi_faq", "hi_faq.html", "https://cca.hawaii.gov/reb/faqs-re_faqs/",
     "Real Estate Licensing, Renewals, and Education FAQs", "Hawaii Real Estate Commission", {
         "attesa": "You must wait 24 hours before rescheduling an examination.",
         "residente": "Do I have to be a resident of Hawaii to secure a real estate license? No.",
     }),
    # ------------------------------------------------------------ partner (non è una fonte ufficiale: serve solo al riquadro, oggi spento)
    ("aceable", "aceable_affiliate.html", "https://partnerships.aceable.com/affiliate",
     "Affiliate Program", "Aceable", {
         "compenso": "15–25% commission per sale, tiered by volume. 30-day attribution.",
     }),
]
FILE_DATI = {"tx_tassi", "al_tassi", "ne_tassi", "hi_tassi"}    # fonti dei numeri: fa sempre fede l'impronta del file intero


def scarica(url, dest, barattolo):
    # Il barattolo dei cookie serve al sito dell'Alabama (ASP.NET controlla che il client accetti i cookie e altrimenti reindirizza all'infinito).
    r = subprocess.run(["curl", "-sL", "-m", "120", "-A", UA, "-b", barattolo, "-c", barattolo, "-o", str(dest), "-w", "%{http_code}", url], capture_output=True, text=True)
    return int(r.stdout.strip()[-3:] or 0)


def _testo_tmp(tmp, dest):
    """Testo di un file scaricato come .tmp: gli si dà per un attimo il nome vero, perché l'estrazione guarda l'estensione."""
    copia = tmp.with_name("leggi_" + dest.name)
    copia.write_bytes(tmp.read_bytes())
    try:
        return T.testo(copia)
    finally:
        copia.unlink()


def cerca(pattern, t, fid):
    m = re.search(pattern, t)
    if not m:
        raise SystemExit(f"{fid}: non trovo «{pattern}» nel file grezzo")
    return m


def _iso(mgy):
    return datetime.strptime(mgy, "%m/%d/%Y").date().isoformat()


def _voce(n, p, pc):
    """Una misura: esami, promossi, percentuale come la stampa la fonte (None se nessun esame)."""
    return {"n": n, "p": p, "pc": pc if n else None}


def _controlla_pc(dove, n, p, pc, modo):
    """La percentuale stampata deve tornare con esami e promossi. modo: 'c2' (2 decimali), 'c1' (1 decimale), 't1' (troncata a 1 decimale), 'c0' (intero)."""
    if p > n or n < 0 or p < 0:
        raise SystemExit(f"{dove}: promossi {p} su {n} esami")
    if not n:
        return
    vera, letta = 100 * p / n, float(pc.rstrip("%"))
    ok = {"c2": abs(vera - letta) <= 0.0051, "c1": abs(vera - letta) <= 0.051, "t1": -1e-9 <= vera - letta < 0.1 + 1e-9, "c0": abs(vera - letta) <= 0.5 + 1e-9}[modo]
    if not ok:
        raise SystemExit(f"{dove}: {p}/{n} = {vera:.3f}% ma la fonte stampa {pc}")


# ---------------------------------------------------------------- Texas
def texas(percorso):
    d = json.loads(Path(percorso).read_text(encoding="utf-8"))
    if len(d["dates"]) != 1 or len(d["passrates0"]) != 1:
        raise SystemExit("tx_tassi: forma del file cambiata (dates / passrates0)")
    tot = d["passrates0"][0]
    scuole = []
    # Come fa la pagina ufficiale: tutte le righe dei gruppi passrates1, 2, 3…, tranne i nomi con un asterisco.
    for k in sorted(k for k in d if re.fullmatch(r"passrates[1-9]\d*", k)):
        for x in d[k]:
            nome_uff = x["SchlNm"]
            if not nome_uff or "*" in nome_uff:
                continue
            n, p, pc = int(x["SALEExmCnt"]), int(x["SALEExmPssdCnt"]), x["SALEPC"]
            _controlla_pc(f"tx_tassi/{nome_uff}", n, p, pc if n else "0%", "c2")
            # Alcune scuole si registrano con punti esclamativi attorno al nome («! ! ! AYPORealEstate.com ! ! !»): in pagina si tolgono, il nome ufficiale resta qui.
            nome = re.sub(r"^[!\s]+|[!\s]+$", "", nome_uff)
            scuole.append({"nome": nome, "nome_ufficiale": nome_uff, "first": _voce(n, p, pc)})
    if len(scuole) < 20 or len({s["nome"] for s in scuole}) != len(scuole):
        raise SystemExit(f"tx_tassi: {len(scuole)} scuole, o nomi doppi")
    n, p, pc = int(tot["SALEExmCnt"]), int(tot["SALEExmPssdCnt"]), tot["SALEPC"]
    _controlla_pc("tx_tassi/totale", n, p, pc, "c2")
    somma_n, somma_p = sum(s["first"]["n"] for s in scuole), sum(s["first"]["p"] for s in scuole)
    if somma_n > n or somma_p > p:
        raise SystemExit("tx_tassi: la somma delle scuole supera il totale dello Stato")
    scuole.sort(key=lambda s: (-s["first"]["n"], s["nome"].lower()))
    return {"periodo": {"dal": _iso(d["dates"][0]["BgnDt"]), "al": _iso(d["dates"][0]["EndDt"])},
            "totale": {"origine": "ufficiale", "first": _voce(n, p, pc)},
            "somma_scuole": {"n": somma_n, "p": somma_p},
            "complessivo_pc": tot["SbjctMttrPC"], "mpr": tot["MPR"], "scuole": scuole}


# ---------------------------------------------------------------- Alabama
def alabama(percorso):
    s = Path(percorso).read_text(encoding="utf-8", errors="replace")
    pezzi = re.split(r'href="/apps/SchoolStatsWF/Home/SchoolDetail/(\d+)"', s)
    scuole = []
    for i in range(1, len(pezzi), 2):
        cod, blocco = pezzi[i], pezzi[i + 1]
        nome = T.norm(html.unescape(re.sub(r"<[^>]+>", " ", blocco.split("</a>", 1)[0].lstrip(">"))))
        nome = nome.lstrip("> ").strip()
        m = re.search(r'<span class="m-0">(.*?)</span>', blocco, re.S)
        citta = T.norm(html.unescape(m.group(1))) if m else ""
        formati = [T.norm(x) for x in re.findall(r'<span class="badge[^"]*">(.*?)</span>', blocco, re.S)]
        t = T.norm(html.unescape(re.sub(r"<[^>]+>", " ", blocco)))
        num = r"Total (\d+) (\d+) Passed (\d+) (\d+) % Passed (\S+) (\S+)"
        m = re.search(r"Salesperson Examination 1st All " + num + r" Broker Examination 1st All " + num, t)
        if not m or not nome:
            raise SystemExit(f"al_tassi: scheda {cod} non letta")
        n1, na, p1, pa, pc1, pca = int(m[1]), int(m[2]), int(m[3]), int(m[4]), m[5], m[6]
        _controlla_pc(f"al_tassi/{nome}/1st", n1, p1, pc1 if n1 else "0%", "c1")
        _controlla_pc(f"al_tassi/{nome}/all", na, pa, pca if na else "0%", "c1")
        if set(formati) - {"Classroom", "Online"}:
            raise SystemExit(f"al_tassi: formato sconosciuto {formati}")
        scuole.append({"nome": nome, "nome_ufficiale": nome, "codice": cod, "citta": citta, "formati": formati,
                       "first": _voce(n1, p1, pc1), "all": _voce(na, pa, pca)})
    if len(scuole) < 50 or len({s["codice"] for s in scuole}) != len(scuole):
        raise SystemExit(f"al_tassi: {len(scuole)} scuole, o codici doppi")
    scuole.sort(key=lambda x: (-x["first"]["n"], x["nome"].lower()))
    tot = {"origine": "somma"}
    for k in ("first", "all"):
        tot[k] = {"n": sum(x[k]["n"] for x in scuole), "p": sum(x[k]["p"] for x in scuole), "pc": None}
    return {"periodo": None, "totale": tot, "scuole": scuole}


# ---------------------------------------------------------------- Hawaii
HI_NON_SCUOLE = {"0": "Unknown", "5555": "Uniform Equivalency Only", "7777": "Pre-License Equivalency Only", "8888": "Pre-License and Uniform Equivalency", "9999": "Restoration"}


def hawaii(percorso):
    t = T.pdf(percorso, layout=True)
    sezioni = {}
    attuale = None
    intervallo = None
    for riga in t.splitlines():
        m = re.search(r"From:\s*(\d+/\d+/\d+)\s+To:\s*(\d+/\d+/\d+)", riga)
        if m:
            intervallo, attuale = (_iso(m[1]), _iso(m[2])), None
            continue
        m = re.match(r"\s*Portion: HI Real Estate (Broker|Salesperson) - (National|State)\s*$", riga)
        if m:
            attuale = (intervallo, m[1].lower(), m[2].lower())
            if attuale in sezioni:
                raise SystemExit(f"hi_tassi: sezione doppia {attuale}")
            sezioni[attuale] = {"righe": [], "totale": None}
            continue
        if attuale is None:
            continue
        m = re.match(r"\s*(\d+)\s+(\S.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d)%", riga)
        if m:
            cod, nome, n, p, f, pc = m[1], T.norm(m[2]), int(m[3]), int(m[4]), int(m[5]), m[6] + "%"
            if p + f != n:
                raise SystemExit(f"hi_tassi: {nome}: {p} + {f} ≠ {n}")
            _controlla_pc(f"hi_tassi/{nome}", n, p, pc, "t1")
            sezioni[attuale]["righe"].append((cod, nome, n, p, pc))
            continue
        m = re.match(r"\s*Total\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d)%", riga)
        if m:
            n, p, f, pc = int(m[1]), int(m[2]), int(m[3]), m[4] + "%"
            righe = sezioni[attuale]["righe"]
            if p + f != n or sum(r[2] for r in righe) != n or sum(r[3] for r in righe) != p:
                raise SystemExit(f"hi_tassi: il totale di {attuale} non è la somma delle righe")
            _controlla_pc(f"hi_tassi/totale {attuale}", n, p, pc, "t1")
            sezioni[attuale]["totale"] = (n, p, pc)
            attuale = None
    intervalli = sorted({k[0] for k in sezioni})
    if len(sezioni) != 8 or len(intervalli) != 2 or any(v["totale"] is None for v in sezioni.values()):
        raise SystemExit(f"hi_tassi: attese 8 tabelle su 2 periodi, trovate {len(sezioni)} su {len(intervalli)}")
    anno = max(intervalli, key=lambda iv: date.fromisoformat(iv[1]) - date.fromisoformat(iv[0]))
    trimestre = min(intervalli, key=lambda iv: date.fromisoformat(iv[1]) - date.fromisoformat(iv[0]))
    naz, sta = sezioni[(anno, "salesperson", "national")], sezioni[(anno, "salesperson", "state")]
    scuole, altri = {}, {}
    for chiave, sez in (("national", naz), ("state", sta)):
        for cod, nome, n, p, pc in sez["righe"]:
            dove = altri if cod in HI_NON_SCUOLE else scuole
            if cod in HI_NON_SCUOLE and HI_NON_SCUOLE[cod] != nome:
                raise SystemExit(f"hi_tassi: codice {cod} ora è «{nome}»")
            v = dove.setdefault(cod, {"nome": nome, "nome_ufficiale": nome, "codice": cod, "national": _voce(0, 0, None), "state": _voce(0, 0, None)})
            if v["nome"] != nome:
                raise SystemExit(f"hi_tassi: codice {cod} con due nomi")
            v[chiave] = _voce(n, p, pc)
    for v in scuole.values():
        m = re.search(r"\((Classroom|Online)\)\s*$", v["nome"])
        v["formati"] = [m[1]] if m else []
    elenco = sorted(scuole.values(), key=lambda x: (-x["national"]["n"], x["nome"].lower(), x["codice"]))
    if len(elenco) < 10:
        raise SystemExit("hi_tassi: meno di 10 scuole")
    return {"periodo": {"dal": anno[0], "al": anno[1]}, "trimestre": {"dal": trimestre[0], "al": trimestre[1]},
            "totale": {"origine": "ufficiale", "national": _voce(*naz["totale"]), "state": _voce(*sta["totale"])},
            "non_scuole": sorted(altri.values(), key=lambda x: int(x["codice"])), "scuole": elenco}


# ---------------------------------------------------------------- Nebraska (trascrizione a mano, controllata)
def nebraska(percorso_pdf):
    m = json.loads((MANUALI / "ne_q1_2026.json").read_text(encoding="utf-8"))
    sha = hashlib.sha256(Path(percorso_pdf).read_bytes()).hexdigest()
    if m["sha256_pdf"] != sha:
        raise SystemExit(f"ne_tassi: il PDF non è quello trascritto in dati/manuali/ne_q1_2026.json (impronta {sha}): rileggere le pagine e aggiornare la trascrizione")
    scuole = []
    for s in m["scuole"]:
        somma = {g: [0, 0, 0] for g in ("first", "repeat", "all")}
        for nome_riga, riga in s["righe"].items():
            for g in ("first", "repeat", "all"):
                n, p, pc, f, fc = riga[g]
                dove = f"ne_tassi/{s['nome']}/{nome_riga}/{g}"
                if p + f != n:
                    raise SystemExit(f"{dove}: {p} + {f} ≠ {n}")
                _controlla_pc(dove, n, p, f"{pc}%", "c0")
                _controlla_pc(dove + " (fail)", n, f, f"{fc}%", "c0")
                if not n and (pc or fc):
                    raise SystemExit(f"{dove}: percentuale senza esami")
                if nome_riga != "total":
                    somma[g] = [a + b for a, b in zip(somma[g], (n, p, f))]
            if [a + b for a, b in zip(riga["first"][:2], riga["repeat"][:2])] != riga["all"][:2]:
                raise SystemExit(f"ne_tassi/{s['nome']}/{nome_riga}: first + repeat ≠ all")
        for g in ("first", "repeat", "all"):
            t = s["righe"]["total"][g]
            if somma[g] != [t[0], t[1], t[3]]:
                raise SystemExit(f"ne_tassi/{s['nome']}: la riga Total ({g}) non è la somma delle righe")
        v = {"nome": s["nome"], "nome_ufficiale": s["nome"], "codice": s["codice"]}
        for chiave, riga in (("national", "sales_national"), ("state", "sales_state")):
            r = s["righe"].get(riga)
            v[chiave + "_first"] = _voce(r["first"][0], r["first"][1], f"{r['first'][2]}%") if r else _voce(0, 0, None)
            v[chiave + "_all"] = _voce(r["all"][0], r["all"][1], f"{r['all'][2]}%") if r else _voce(0, 0, None)
        v["solo_broker"] = "sales_national" not in s["righe"] and "sales_state" not in s["righe"]
        scuole.append(v)
    if len(scuole) != 12 or len({s["codice"] for s in scuole}) != 12:
        raise SystemExit("ne_tassi: attese 12 scuole")
    scuole.sort(key=lambda x: (-x["national_first"]["n"], x["nome"].lower()))
    tot = {"origine": "somma"}
    for k in ("national_first", "state_first", "national_all", "state_all"):
        tot[k] = {"n": sum(x[k]["n"] for x in scuole), "p": sum(x[k]["p"] for x in scuole), "pc": None}
    return {"periodo": m["periodo"], "totale": tot, "scuole": scuole}


# ---------------------------------------------------------------- licenza: ore, età, tariffe (dai testi)
def soldi(s):
    return int(round(float(s.replace(",", "")) * 100))


def licenza(testi):
    L = {}
    t = testi["tx_tariffe"]
    m = cerca(r"Fee Schedule Effective (\w+ \d+, \d{4}) Sales Agent: Fee Late Fee < 90 days Late Fee > 90 days Texas Online Fee Texas A&M Research Center Real Estate Recovery Fee Total Fee "
              r"Original Application (\d+\.\d\d) (\d+\.\d\d) (\d+\.\d\d) (\d+\.\d\d) (\d+\.\d\d) Renewal", t, "tx_tariffe")
    dom = {"tassa": soldi(m[2]), "texas_online": soldi(m[3]), "centro_ricerca": soldi(m[4]), "fondo": soldi(m[5]), "totale": soldi(m[6])}
    if dom["tassa"] + dom["texas_online"] + dom["centro_ricerca"] + dom["fondo"] != dom["totale"]:
        raise SystemExit("tx_tariffe: le voci della domanda non danno il totale")
    es = cerca(r"Real Estate Sales Examination Fee, paid to exam provider (\d+\.\d\d) (\d+\.\d\d) ", t, "tx_tariffe")
    imp = cerca(r"Fingerprint Fee – paid to IDEMIA if the applicant has not previously been fingerprinted for TREC\. (\d+\.\d\d) (\d+\.\d\d) ", t, "tx_tariffe")
    if es[1] != es[2] or imp[1] != imp[2]:
        raise SystemExit("tx_tariffe: tassa d'esame o impronte con totale diverso")
    tl = testi["tx_licenza"]
    corsi = re.findall(r"(Principles of Real Estate I|Principles of Real Estate II|Law of Agency|Law of Contracts|Promulgated Contract Forms|Real Estate Finance) \((\d+) hours\)", tl)
    ore = int(cerca(r"must complete (\d+) classroom hours", tl, "tx_licenza")[1])
    if len(corsi) != 6 or sum(int(o) for _, o in corsi) != ore:
        raise SystemExit("tx_licenza: i sei corsi non sommano alle ore richieste")
    L["TX"] = {"ore": ore, "corsi": [{"nome": n, "ore": int(o)} for n, o in corsi], "eta": int(cerca(r"(\d+) years of age or older", tl, "tx_licenza")[1]),
               "in_vigore": m[1], "domanda": dom, "esame": soldi(es[1]), "impronte": soldi(imp[1])}

    t = testi["al_licenza"]
    L["AL"] = {"ore": int(cerca(r"complete an approved (\d+) clock hour prelicense course\. Applicants have", t, "al_licenza")[1]),
               "mesi_esame": int(cerca(r"Applicants have (\d+) months to pass the state exam", t, "al_licenza")[1]),
               "ore_post": int(cerca(r"Must complete a (\d+) hour post license training course", t, "al_licenza")[1]),
               "eta": int(cerca(r"Be at least (\d+) years old;", t, "al_licenza")[1]),
               "giorni_domanda": int(cerca(r"within (\d+) days of your examination date", testi["al_domanda"], "al_domanda")[1])}

    t = testi["ne_licenza"]
    tot = int(cerca(r"CURRENT REQUIREMENT- (\d+) HOURS TOTAL", t, "ne_licenza")[1])
    pps = int(cerca(r"(\d+) hour Professional Practice Standards", t, "ne_licenza")[1])
    pre = int(cerca(r"(\d+) Clock hours \(3 courses\) in Approved Pre-License Education", t, "ne_licenza")[1])
    if pps + pre != tot:
        raise SystemExit("ne_licenza: le ore non sommano")
    tf = testi["ne_tariffe"]
    ti = testi["ne_indice"]
    sog = cerca(r"pass the National exam is (\d+)/(\d+)\. The number of correct questions necessary to pass the State exam is (\d+)/(\d+)\.", ti, "ne_indice")
    L["NE"] = {"ore": tot, "ore_standard": pps, "ore_corsi": pre, "eta": int(cerca(r"At least (\d+) years old", t, "ne_licenza")[1]),
               "domanda": soldi(cerca(r"License Application Fee - Salespersons & Brokers \$ ?([\d.]+)", tf, "ne_tariffe")[1]),
               "esame": soldi(cerca(r"License Examination Fee - Salespersons & Brokers - per exam \$ ?([\d.]+)", tf, "ne_tariffe")[1]),
               "ripetizione": soldi(cerca(r"Examination Retake Fee - Salespersons & Brokers - within one year of application \$ ?([\d.]+)", tf, "ne_tariffe")[1]),
               "licenza": soldi(cerca(r"Salesperson Original License Fee \(current year only\) \$ ?([\d.]+)", tf, "ne_tariffe")[1]),
               "rinnovo": soldi(cerca(r"Salesperson Renewal Fee - 2 Year \$ ?([\d.]+)", tf, "ne_tariffe")[1]),
               "soglia_nazionale": [int(sog[1]), int(sog[2])], "soglia_statale": [int(sog[3]), int(sog[4])]}

    t = testi["hi_tariffe"]
    m = cerca(r"Salesperson, ?Broker-Salesperson, PB, BIC: Odd numbered year – \$(\d+) Even numbered year – \$(\d+) Renewal – \$(\d+)", t, "hi_tariffe")
    L["HI"] = {"ore": int(cerca(r"Successfully complete a (\d+) hour Hawaii salesperson prelicensing course", testi["hi_licenza"], "hi_licenza")[1]),
               "eta": int(cerca(r"at least (\d+) years of age as of the date of the examination", testi["hi_requisiti"], "hi_requisiti")[1]),
               "licenza_dispari": soldi(m[1]), "licenza_pari": soldi(m[2]), "rinnovo": soldi(m[3]),
               "ore_attesa": int(cerca(r"You must wait (\d+) hours before rescheduling an examination", testi["hi_faq"], "hi_faq")[1]),
               "ore_formazione_continua": int(cerca(r"complete (\d+) hours of Commission approved continuing education every licensing biennium", testi["hi_licenza"], "hi_licenza")[1])}
    return L


STATI = {
    "TX": {"nome": "Texas", "slug": "texas", "ente": "Texas Real Estate Commission", "sigla": "TREC", "titolo_licenza": "sales agent", "fonte": "tx_tassi", "fonte_def": "tx_pagina"},
    "AL": {"nome": "Alabama", "slug": "alabama", "ente": "Alabama Real Estate Commission", "sigla": "AREC", "titolo_licenza": "salesperson", "fonte": "al_tassi", "fonte_def": "al_tassi"},
    "NE": {"nome": "Nebraska", "slug": "nebraska", "ente": "Nebraska Real Estate Commission", "sigla": "NREC", "titolo_licenza": "salesperson", "fonte": "ne_tassi", "fonte_def": "ne_indice"},
    "HI": {"nome": "Hawaii", "slug": "hawaii", "ente": "Hawaii Real Estate Commission", "sigla": "REC", "titolo_licenza": "salesperson", "fonte": "hi_tassi", "fonte_def": "hi_tassi"},
}


def dati(testi, fonti):
    lettori = {"TX": texas, "AL": alabama, "NE": nebraska, "HI": hawaii}
    stati = {}
    for s, info in STATI.items():
        v = dict(info)
        v.update(lettori[s](DATI.parent / fonti[info["fonte"]]["file"]))
        v["letto_il"] = fonti[info["fonte"]]["letto_il"]
        stati[s] = v
    return {"_nota": "Generato da raccolta/fonti.py dai file in dati/grezzi/ (Nebraska: da dati/manuali/ne_q1_2026.json, controllato). n = esami, p = promossi, "
                     "pc = percentuale come la stampa la fonte (null se nessun esame). Texas: solo primo tentativo. Alabama: first = primo tentativo, all = tutti i tentativi. "
                     "Nebraska: parte nazionale e parte statale, first = First Time Takers, all = Total. Hawaii: parte nazionale e parte statale, tutti gli esami sostenuti. "
                     "totale.origine: «ufficiale» se la riga è della fonte, «somma» se è la nostra somma delle scuole.",
            "soglia_campione": SOGLIA_CAMPIONE, "stati": stati, "licenza": licenza(testi)}


def main():
    locale = "--locale" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    vecchie = {}
    if (DATI / "fonti.json").exists():
        vecchie = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["fonti"]
    oggi = date.today().isoformat()
    fonti, testi, errori, nuovi = {}, {}, [], []
    link_indice_ne = set()
    with tempfile.TemporaryDirectory() as tmpdir:
        barattolo = str(Path(tmpdir) / "cookie.txt")
        for fid, nome, url, titolo, chi, frasi in FONTI:
            dest = GREZZI / nome
            leggi = dest          # file da cui leggere: quello nuovo (.tmp) finché non si sa che tutto il giro è buono
            if locale:
                http, letto = vecchie.get(fid, {}).get("http", 200), vecchie.get(fid, {}).get("letto_il", oggi)
                if not dest.exists():
                    raise SystemExit(f"{fid}: manca {dest}")
            else:
                tmp = dest.with_name(dest.name + ".tmp")
                http, letto = scarica(url, tmp, barattolo), oggi
                if http != 200 or not tmp.exists() or tmp.stat().st_size < 1000:
                    tmp.unlink(missing_ok=True)
                    errori.append(f"{fid}: HTTP {http} da {url} (file precedente conservato)")
                    continue
                leggi = tmp
                nuovi.append((tmp, dest))
            grezzo = leggi.read_bytes()
            testi[fid] = T.norm(T.testo(leggi) if leggi == dest else _testo_tmp(leggi, dest))
            trovate = {k: (T.norm(f) in testi[fid]) for k, f in frasi.items()}
            for k, ok in trovate.items():
                if not ok:
                    errori.append(f"{fid}: frase «{k}» non trovata alla lettera")
            if fid == "ne_indice":
                link_indice_ne = T.link_pdf(leggi)
            if fid == "ne_tassi" and url not in link_indice_ne:
                errori.append(f"{fid}: {url} non è tra i collegamenti dell'indice ufficiale del Nebraska (ne_indice): si usa solo un rapporto collegato dalla Commissione")
            # Le pagine HTML cambiano byte a ogni scarico (parti dinamiche): per loro fa fede l'impronta delle frasi citate. Per i file dei numeri fa sempre fede il file intero.
            fonti[fid] = {"url": url, "file": f"dati/grezzi/{nome}", "titolo": titolo, "chi": chi, "sha256": hashlib.sha256(grezzo).hexdigest(), "byte": len(grezzo),
                          "impronta": "frasi" if nome.endswith(".html") and fid not in FILE_DATI else "file", "sha256_frasi": T.impronta_frasi(testi[fid], frasi),
                          "http": http, "letto_il": letto, "frasi": frasi, "trovate": trovate}
    if errori:
        # Giro non buono: i file scaricati si buttano, così dati/grezzi resta uguale a ciò che fonti.json descrive.
        for tmp, _ in nuovi:
            tmp.unlink(missing_ok=True)
        print("\n".join(errori))
        raise SystemExit(f"{len(errori)} errori: fonti.json, tassi.json e dati/grezzi NON aggiornati")
    precedenti = []
    for tmp, dest in nuovi:
        if dest.exists():
            prec = dest.with_name(dest.name + ".prec")
            dest.replace(prec)
            precedenti.append((prec, dest))
        tmp.replace(dest)
    try:
        tassi = dati(testi, fonti)
    except SystemExit:
        # Una tabella o una cifra non si legge più: si torna ai file di prima (dati/grezzi = fonti.json) e i nuovi vanno in cache/ per guardarli.
        scarto = DATI.parent / "cache" / "fonti_non_lette"
        scarto.mkdir(parents=True, exist_ok=True)
        for _, dest in nuovi:
            dest.replace(scarto / dest.name)
        for prec, dest in precedenti:
            prec.replace(dest)
        print(f"Un dato non si legge più nei file nuovi: dati/grezzi è rimasto com'era, i file nuovi sono in {scarto}.")
        raise
    for prec, _ in precedenti:
        prec.unlink()
    for fid, f in fonti.items():
        v = vecchie.get(fid)
        if v and v.get("sha256") != f["sha256"]:
            stesso = f["impronta"] == "frasi" and v.get("sha256_frasi") == f["sha256_frasi"]
            print(f"{fid}: file cambiato dall'ultima lettura" + (" (solo parti dinamiche della pagina: le frasi citate sono le stesse)" if stesso else " (rileggere le cifre)"))
    tassi["letto_il"] = max(f["letto_il"] for f in fonti.values())
    (DATI / "fonti.json").write_text(json.dumps({"_nota": "Generato da raccolta/fonti.py. File grezzi in dati/grezzi/. PDF, JSON e pagine dei numeri: fa fede sha256 (file intero). Altre pagine HTML (impronta = frasi): i byte cambiano a ogni scarico, fa fede sha256_frasi (le frasi citate alla lettera, ritrovate nel file).",
                                                 "fonti": fonti}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (DATI / "tassi.json").write_text(json.dumps(tassi, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_scuole = {s: len(v["scuole"]) for s, v in tassi["stati"].items()}
    print(f"{len(fonti)} fonti, {sum(len(f['frasi']) for f in fonti.values())} frasi trovate alla lettera; tassi.json scritto: {n_scuole}.")


if __name__ == "__main__":
    main()
