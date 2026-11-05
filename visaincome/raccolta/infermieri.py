"""Infermieri formati all'estero nel Regno Unito e in Irlanda, per Paese di formazione (sezione "Nurses abroad" del sito, dal 5/11/2026).
Scrive visaincome/dati/infermieri.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/infermieri.py              # scarica (o riusa i file in raccolta/_grezzi/) e scrive il JSON
    python3 visaincome/raccolta/infermieri.py --nuovo      # riscarica sempre i file ufficiali
    python3 visaincome/raccolta/infermieri.py --domanda    # rifà anche l'autocompletamento di Google (circa 1 minuto)

Fonti (tutte lette il 5/11/2026, HTTP 200):
1. NMC (Nursing and Midwifery Council), "Registration data reports": la pagina elenca i file; si prende il più recente
   "nmc-register-<mese>-<anno>-uk-data-tables.xlsx" (marzo 2026, pubblicato a luglio 2026). Fogli "Training Country ALL"
   (persone sul registro per Paese di formazione, ogni 6 mesi dal 30/9/2020) e "Training Country Joiners" (persone entrate per la
   prima volta nei 6 mesi). Il registro comprende infermieri, ostetriche e (in Inghilterra) nursing associates.
   Controlli: per ogni data, somma dei Paesi di ogni area = sub-totale del file; UK + estero = totale; nuovi iscritti: il
   "6 Year Total" = somma dei 12 semestri. Licenza: le condizioni NMC (sez. 6) non danno una licenza di riuso dei dati;
   le pagine citano pochi numeri come fatti, con il link al file.
2. NMC, pagina "How much is it going to cost?" (guida per chi si è formato fuori dal Regno Unito): costi dal 1/10/2026.
   Controllo: le quattro voci (valutazione, CBT, OSCE, iscrizione) sommano al totale scritto (£1.226). La pagina
   "Information for internationally trained applicants" scrive ancora "£1,170" con voci che sommano a £1.226: NON usata
   (vedi "scartati" nel JSON).
3. Irlanda, Department of Health, "JQ06 – Stock of nurses by country of first qualification" (data.gov.ie, CC BY 4.0;
   dati delle iscrizioni annuali al NMBI). CSV in cp1252, anni 2021-2025; valori sotto 25 soppressi ("." con segno S).
   Controlli: totale = formati in Irlanda + all'estero + sconosciuti; somma dei Paesi pubblicati <= formati all'estero e
   differenza < 25 × Paesi soppressi.
4. GOV.UK, "Code of practice for the international recruitment of health and social care personnel in England" (Content API,
   OGL v3): frasi sulla lista rossa e allegato A (rossi e ambra) e B (verdi con accordo).
5. OMS: pagina domande e risposte sulla "WHO health workforce support and safeguards list" (5/8/2026, descrive la lista 2026
   ancora da pubblicare) e pubblicazione "WHO health workforce support and safeguards list 2023" (pagina + PDF, 55 Paesi).
   Controllo: i 54 Paesi rossi del codice britannico + Nepal (ambra) sono tutti scritti nel PDF del 2023, che ne conta 55;
   il Kenya (ambra) non c'è. La lista 2026 provvisoria (lettera circolare C.L.25.2026, solo su siti specchio) NON si usa.
6. Home Office, file "Entry clearance visa applications and outcomes detailed datasets" già in raccolta/_grezzi/ (lo stesso
   SHA-256 di dati/rifiuti.json), foglio Data_Vis_D02, sottotipo "Health and Care Worker" (colonna "Visa type subgroup"):
   per nazionalità × anno × tipo di richiedente (principale o familiare) × esito. Controllo: per ogni nazionalità e trimestre
   degli ultimi 8 i concessi e i rifiutati non superano il gruppo Work di dati/rifiuti.json.
LETTURE (sotto): ogni frase o cifra letta A MANO il 5/11/2026 con il FRAMMENTO del testo ufficiale. Se un frammento manca,
il JSON NON viene aggiornato (codice 1) finché qualcuno non rilegge la pagina.
"""
import csv
import hashlib
import html as H
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rifiuti import GREZZI, RADICE, UA, scarica  # noqa: E402

USCITA = RADICE / "dati" / "infermieri.json"
FILE_HO = GREZZI / "uk-entry-clearance-outcomes.xlsx"
NMC = "https://www.nmc.org.uk"
PAGINE = {
    "nmc_pagina": NMC + "/about-us/reports-and-accounts/registration-statistics/",
    "nmc_costi": NMC + "/registration/joining-the-register/register-nurse-midwife/trained-outside-uk/how-to-guide/check-ready/costs/",
    "nmc_intl": NMC + "/registration/information-for-internationally-trained-applicants/",
    "oms_qa": "https://www.who.int/news-room/questions-and-answers/item/who-health-workforce-support-and-safeguards-list",
    "oms_ssl2023": "https://www.who.int/publications/i/item/9789240069787",
}
API_GOVUK = "https://www.gov.uk/api/content"
CODICE = ("/government/publications/code-of-practice-for-the-international-recruitment-of-health-and-social-care-personnel/"
          "code-of-practice-for-the-international-recruitment-of-health-and-social-care-personnel-in-england")
JQ06_API = "https://data.gov.ie/api/3/action/package_show?id=jq06-stock-of-nurses-by-country-of-first-qualification"
JQ06_SCHEDA = "https://data.gov.ie/dataset/jq06-stock-of-nurses-by-country-of-first-qualification"
SOTTOTIPO = "Health and Care Worker"
ESITI = ("Issued", "Refused", "Withdrawn", "Lapsed")

LETTURE = {
    # NMC, pagina dei costi (guida per chi si è formato fuori dal Regno Unito)
    "costo_totale": {"valore": 1226, "fonte": "nmc_costi", "frammento": "The total cost of fees and tests is £1,226"},
    "costo_valutazione": {"valore": 167, "fonte": "nmc_costi", "frammento": "Qualification evaluation fee Paid to NMC on submission of eligibility and qualification application. This fee is non-refundable. £167"},
    "costo_cbt": {"valore": 83, "fonte": "nmc_costi", "frammento": "Computer based test (CBT) cost Paid to test provider before test. £83 first sitting"},
    "costo_cbt_resit": {"valore": 83, "fonte": "nmc_costi", "frammento": "For both Clinical and Numeracy £83 full resit"},
    "costo_cbt_clinical": {"valore": 70, "fonte": "nmc_costi", "frammento": "For Clinical only £70 partial resit"},
    "costo_cbt_numeracy": {"valore": 50, "fonte": "nmc_costi", "frammento": "For Numeracy only £50 partial resit"},
    "costo_osce": {"valore": 794, "fonte": "nmc_costi", "frammento": "Objective structured clinical examination (OSCE) cost Paid to test provider before exam. £794 first sitting"},
    "costo_osce_resit": {"valore": 794, "fonte": "nmc_costi", "frammento": "Payable if candidate fails in eight or more stations. £794 full resit"},
    "costo_osce_parziale": {"valore": 397, "fonte": "nmc_costi", "frammento": "Payable if candidate fails in up to seven stations. £397 partial resit"},
    "costo_iscrizione": {"valore": 182, "fonte": "nmc_costi", "frammento": "Registration fee Paid to NMC on submission of registration application. This fee is refundable in certain circumstances. £182"},
    "costo_aumento": {"valore": "2026-10-01", "fonte": "nmc_costi", "frammento": "Please note our fees increased on 1 October 2026."},
    "costo_escluso": {"valore": True, "fonte": "nmc_costi", "frammento": "This doesn't include the cost of your visa, flights to the UK and any accommodation and travel while in the UK."},
    "costo_resit": {"valore": True, "fonte": "nmc_costi", "frammento": "These costs could be higher if you need to resit tests."},
    # GOV.UK, codice di condotta
    "codice_da_oms": {"valore": "2023", "fonte": "codice", "frammento": "The red list is drawn from the WHO Health Workforce Support and Safeguards List 2023"},
    "codice_no_attivo": {"valore": True, "fonte": "codice", "frammento": "No active recruitment of health and care staff will be undertaken from countries on the red list."},
    "codice_rosso": {"valore": True, "fonte": "codice", "frammento": "Countries on the WHO health workforce support and safeguards list are graded red, which means no active recruitment is permitted from these countries."},
    "codice_ambra": {"valore": True, "fonte": "codice", "frammento": "The country will be added to the amber list and recruitment can happen only on the terms of the agreement."},
    "codice_verde": {"valore": True, "fonte": "codice", "frammento": "Active recruitment is permitted from green graded countries."},
    "codice_diretta": {"valore": True, "fonte": "codice", "frammento": "Individual health and social care employers may consider direct applications from individuals who are resident in countries on the code red and amber list"},
    "codice_diretta_def": {"valore": True, "fonte": "codice", "frammento": "A direct application can only be made in response to a specific advertised vacancy that is hosted by, and recruited to, the same sponsoring organisation."},
    "codice_residenza": {"valore": True, "fonte": "codice", "frammento": "The rules on active recruitment and direct applications are based on the country where an individual is residing when they apply for a health or social care job, rather than the nationality of the individual or their original country of training."},
    "codice_3anni": {"valore": 3, "fonte": "codice", "frammento": "The WHO health workforce support and safeguards list is updated by WHO every 3 years, or more frequently if required."},
    # OMS
    "oms_data_qa": {"valore": "2026-08-05", "fonte": "oms_qa", "frammento": "5 August 2026 | Questions and answers"},
    "oms_flessibilita": {"valore": True, "fonte": "oms_qa", "frammento": "The update of the SSL from 2026 onwards includes the flexibility option in its application"},
    "oms_finale": {"valore": True, "fonte": "oms_qa", "frammento": "After incorporating Member State responses, WHO publishes the final list of countries and shares them with Member States and the public."},
    "oms_3anni": {"valore": 3, "fonte": "oms_qa", "frammento": "The SSL is scheduled to be updated every 3 years or earlier if necessary"},
    "oms_volontario": {"valore": True, "fonte": "oms_qa", "frammento": "are voluntary instruments adopted under article 23 of the WHO Constitution, and as such they are not legally binding"},
    "oms_2023_55": {"valore": 55, "fonte": "oms_ssl2023", "frammento": "The WHO health workforce support and safeguards list 2023 comprises 55 countries."},
    "oms_2023_data": {"valore": "2023-03-08", "fonte": "oms_ssl2023", "frammento": "WHO health workforce support and safeguards list 2023 8 March 2023 | Technical document"},
    "oms_2023_prossime": {"valore": [2026, 2029], "fonte": "oms_pdf", "frammento": "with the next updates scheduled for publication in 2026 and 2029"},
    # Irlanda, metadati JQ06
    "jq06_soppressi": {"valore": 25, "fonte": "jq06_metadati", "frammento": "Any Country with a value smaller than 25 was suppressed for confidentiality purposes."},
    "jq06_ostetriche": {"valore": True, "fonte": "jq06_metadati", "frammento": "Note that figures also include midwives"},
    "jq06_copertura": {"valore": True, "fonte": "jq06_metadati", "frammento": "have self-reported to be practicing in Ireland"},
    "jq06_fine_anno": {"valore": True, "fonte": "jq06_metadati", "frammento": "Year (also referred to as data reference year) is taken as at the end of the calendar year of reference."},
}
# Frasi della pagina NMC per chi si è formato all'estero che NON si usano (totale che non torna con le voci): solo registrate
SCARTATI = {"nmc_intl_totale": {"fonte": "nmc_intl", "frammento": "The total cost for application and registration is £1,170.",
                                "voci": ["Qualification evaluation fee - £167", "Computer-based test (CBT) - £83",
                                         "Objective Structured Clinical Examination (OSCE) - £794", "Registration fee for entry onto our register - £182"],
                                "motivo": "£167 + £83 + £794 + £182 = £1.226, non £1.170 (importo precedente all'aumento del 1/10/2026?): usata la pagina dei costi"}}
# Nomi del codice britannico -> nomi del PDF OMS 2023 (dove sono diversi)
NOMI_OMS = {"Congo, Democratic Republic of": "Democratic Republic of the Congo", "Côte d’Ivoire": "Côte d'Ivoire", "Gambia, The": "Gambia",
            "Lao People’s Democratic Republic": "Lao People's Democratic Republic", "Micronesia, Federated States of": "Micronesia (Federated States of)",
            "Tanzania, United Republic of": "United Republic of Tanzania", "Yemen, Republic of": "Yemen"}
# Nomi del codice britannico -> nazionalità nel file del Home Office (dove sono diverse)
NOMI_HO = {"Congo, Democratic Republic of": "Congo (Democratic Republic)", "Côte d’Ivoire": "Ivory Coast", "Lao People’s Democratic Republic": "Laos",
           "Micronesia, Federated States of": "Micronesia", "Tanzania, United Republic of": "Tanzania", "Yemen, Republic of": "Yemen",
           "Timor-Leste": "East Timor"}
REGIONI_OMS = {"African Region": 37, "Eastern Mediterranean Region": 6, "South-East Asia Region": 3, "Western Pacific Region": 8, "Region of the Americas": 1}

QUERY = [
    "in|how many indian nurses in uk", "in|indian nurses in ireland", "in|can indian nurse work in uk",
    "ph|how many filipino nurses in uk", "ph|filipino nurses in ireland",
    "ng|how many nigerian nurses in uk", "ng|nigerian nurses in ireland", "gh|ghanaian nurses in uk", "zw|zimbabwean nurses in uk",
    "np|nepali nurses in uk", "za|south african nurses in uk", "ke|kenyan nurses in uk", "pk|pakistani nurses in uk",
    "zm|zambian nurses in uk", "lk|sri lankan nurses in uk", "jm|jamaican nurses in uk", "au|australian nurses in uk",
    "gb|foreign nurses in uk", "gb|international nurses in uk", "ie|nurses in ireland from", "ie|how many nurses in ireland",
    "ng|is nigeria on the red list", "gh|is ghana on the red list", "zw|is zimbabwe on the red list", "ke|is kenya on the red list",
    "np|is nepal on the red list", "pk|is pakistan on the red list", "zm|is zambia on the red list",
    "ng|red list countries for nurses", "gb|red list countries", "gb|who red list", "gb|nhs red list countries",
    "gh|nmc registration fee", "ng|nmc application fee", "ng|nmc osce fee", "ng|nmc cbt fee", "ph|nmc uk fee", "gb|nmc osce resit fee",
    "in|nmc registration fee",
]


def testo_html(b):
    t = b.decode("utf-8", "replace") if isinstance(b, bytes) else b
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")).strip()


def get(u, tentativi=3):
    for i in range(tentativi):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90)
            return r.status, r.read(), dict(r.headers)
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, b"", {}
            time.sleep(2 + 2 * i)
    return 0, b"", {}


def autocompleta(q, gl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": "en", "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda(query):
    out = {}
    for k in query:
        gl, q = k.split("|", 1)
        out[k] = autocompleta(q, gl)
        time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<Paese>&hl=en&q=…", "query": out}


# ---------------------------------------------------------------- Home Office: sottotipi del foglio Data_Vis_D02 (usato anche da ancestry.py)
def leggi_sottotipi(percorso, sottotipi):
    """{sottotipo: {nazionalità: {trimestre: {"M"|"D": [concessi, rifiutati, ritirati, decaduti]}}}}, gruppo del sottotipo, nazionalità del file."""
    import openpyxl
    wb = openpyxl.load_workbook(percorso, read_only=True)
    ws = wb["Data_Vis_D02"]
    intest = None
    out = {s: defaultdict(lambda: defaultdict(lambda: {"M": [0, 0, 0, 0], "D": [0, 0, 0, 0]})) for s in sottotipi}
    gruppi = {s: set() for s in sottotipi}
    tutte = set()
    for r in ws.iter_rows(values_only=True):
        if intest is None:
            if r and r[0] == "Year" and r[1] == "Quarter":
                intest = list(r)
                if intest[2:10] != ["Nationality", "Region", "Visa type group", "Visa type", "Visa type subgroup", "Applicant type", "Case outcome", "Decisions"]:
                    raise SystemExit(f"Home Office: intestazioni inattese {intest}")
            continue
        if not r[1]:
            continue
        tutte.add(r[2])
        if r[6] not in out:
            continue
        if r[8] not in ESITI or r[7] not in ("Main Applicant", "Dependant"):
            raise SystemExit(f"Home Office: esito o tipo di richiedente inattesi {r}")
        gruppi[r[6]].add((r[4], r[5]))
        out[r[6]][r[2]][r[1]]["M" if r[7] == "Main Applicant" else "D"][ESITI.index(r[8])] += int(r[9] or 0)
    return {s: {n: dict(v) for n, v in d.items()} for s, d in out.items()}, {s: sorted(g) for s, g in gruppi.items()}, tutte


def controllo_ho(rif, d, nome):
    """Il sottotipo non può superare il gruppo Work di dati/rifiuti.json (ultimi 8 trimestri), nazionalità per nazionalità."""
    errori, n = [], 0
    for naz, per_q in d.items():
        for q, v in per_q.items():
            w = rif["uk"]["naz"].get(naz, {}).get("Work", {}).get(q)
            if q not in rif["uk"]["trimestri"]:
                continue
            if w is None:
                errori.append(f"{nome}: {naz} {q} senza il gruppo Work in rifiuti.json")
                continue
            n += 1
            for i in (0, 1):
                if v["M"][i] + v["D"][i] > w[i]:
                    errori.append(f"{nome}: {naz} {q} {ESITI[i]} {v['M'][i] + v['D'][i]} oltre il gruppo Work {w[i]}")
    return errori, n


def per_anno(per_q):
    """{anno: {"M": [...], "D": [...], "trimestri": n}} da {trimestre: {...}}."""
    out = {}
    for q, v in sorted(per_q.items()):
        a = q[:4]
        x = out.setdefault(a, {"M": [0, 0, 0, 0], "D": [0, 0, 0, 0], "trimestri": []})
        for t in ("M", "D"):
            x[t] = [p + s for p, s in zip(x[t], v[t])]
        x["trimestri"].append(q[-2:])
    return out


def fonte_ho(rif, b_ho):
    sha = hashlib.sha256(b_ho).hexdigest()
    f = dict(rif["fonti"]["uk"])
    if sha != f["sha256"]:
        raise SystemExit("Home Office: il file in raccolta/_grezzi/ non è quello di dati/rifiuti.json: rilanciare prima rifiuti.py")
    return f


# ---------------------------------------------------------------- NMC
def leggi_nmc(b):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
    errori = []

    def foglio(nome, joiners):
        righe = list(wb[nome].iter_rows(values_only=True))
        intest = next(r for r in righe if r[2] == "Country of Training")
        i0 = righe.index(intest)
        col = [c for c in intest[3:] if c is not None]
        if joiners:
            if col[-1] != "6 Year Total":
                errori.append(f"NMC {nome}: ultima colonna {col[-1]!r}")
            col = col[:-1]
        n = len(col)
        area, sub, paesi, ordine = None, {}, {}, []
        totale = None
        for r in righe[i0 + 1:]:
            if r[2] is None and r[0] is None and r[1] is None:
                break
            if r[0]:
                area = "UK" if r[0] == "UK" else None
            if r[1]:
                area = "EU/EEA" if r[1] == "EU/EEA" else "Rest of the World"
            nome_r = str(r[2]).strip()
            if nome_r == "EU/EEA sub-total":   # nel foglio dei nuovi iscritti l'etichetta "Rest of the World" manca: viene dopo il sub-totale UE/SEE
                area_dopo = "Rest of the World"
            else:
                area_dopo = None
            v = [int(x or 0) for x in r[3:3 + n]]
            if joiners and int(r[3 + n] or 0) != sum(v):
                errori.append(f"NMC {nome}: {nome_r} 6 Year Total {r[3 + n]} diverso dalla somma {sum(v)}")
            if nome_r == "Total":
                totale = v
            elif nome_r.endswith("sub-total"):
                sub[nome_r] = v
            else:
                paesi[nome_r] = {"area": area, "v": v}
                ordine.append(nome_r)
            if area_dopo:
                area = area_dopo
        for a, s in (("UK", "UK sub-total"), ("EU/EEA", "EU/EEA sub-total"), ("Rest of the World", "Rest of the World sub-total")):
            somma = [sum(p["v"][i] for p in paesi.values() if p["area"] == a) for i in range(n)]
            if somma != sub.get(s):
                errori.append(f"NMC {nome}: somma {a} {somma} diversa dal sub-totale {sub.get(s)}")
        if [a + b for a, b in zip(sub["EU/EEA sub-total"], sub["Rest of the World sub-total"])] != sub["International sub-total"]:
            errori.append(f"NMC {nome}: EU/EEA + resto del mondo diverso dal sub-totale internazionale")
        if [a + b for a, b in zip(sub["UK sub-total"], sub["International sub-total"])] != totale:
            errori.append(f"NMC {nome}: UK + estero diverso dal totale")
        return col, paesi, sub, totale

    c_all, p_all, s_all, t_all = foglio("Training Country ALL", False)
    c_new, p_new, s_new, t_new = foglio("Training Country Joiners", True)
    date_ = [c.date().isoformat() for c in c_all]
    semestri = []
    for c in c_new:
        m = re.fullmatch(r"6 mths to (\d\d)/(\d\d)/(\d{4})", c)
        if not m:
            errori.append(f"NMC: intestazione dei nuovi iscritti inattesa {c!r}")
            continue
        semestri.append(f"{m.group(3)}-{m.group(2)}-{m.group(1)}")
    if semestri != date_:
        errori.append(f"NMC: semestri dei nuovi iscritti {semestri} diversi dalle date del registro {date_}")
    paesi = {}
    for k, v in p_all.items():
        paesi[k] = {"area": v["area"], "registro": v["v"], "nuovi": p_new.get(k, {}).get("v")}
    return {"date": date_, "paesi": paesi, "subtotali": s_all, "totale": t_all, "subtotali_nuovi": s_new, "totale_nuovi": t_new}, errori


def link_nmc(pagina):
    xs = re.findall(r'href="(/globalassets/sitedocuments/data-reports/[^"]*?nmc-register-([a-z]+)-(\d{4})-uk-data-tables\.xlsx)"', pagina)
    mesi = {"march": 3, "september": 9}
    xs = [(int(a), mesi.get(m, 0), u) for u, m, a in xs]
    return NMC + max(xs)[2] if xs else None


# ---------------------------------------------------------------- Irlanda (JQ06)
def leggi_jq06(b):
    righe = list(csv.DictReader(io.StringIO(b.decode("cp1252"))))
    att = ["STATISTIC", "Statistic Label", "YEAR", "Year", "TRNGTYPE", "Type of training", "QUALCOU", "Foreign country of first qualification", "UNIT", "VALUE", "FLAG", "Flag"]
    errori = []
    if list(righe[0].keys()) != att:
        return None, [f"JQ06: intestazione cambiata {list(righe[0].keys())}"]
    anni = sorted({r["YEAR"] for r in righe})
    tipi = defaultdict(dict)
    paesi = {}
    for r in righe:
        v = r["VALUE"].strip()
        n = int(v) if v.isdigit() else None
        if r["TRNGTYPE"] != "FOREIGN":
            tipi[r["TRNGTYPE"]][r["YEAR"]] = n
            continue
        c = r["QUALCOU"].strip()
        if c == "-":   # riga dei formati all'estero (tutti i Paesi)
            tipi["FOREIGN"][r["YEAR"]] = n
            continue
        p = paesi.setdefault(c, {"nome": r["Foreign country of first qualification"].strip(), "v": {}})
        if n is None and r["FLAG"].strip() != "S":
            errori.append(f"JQ06: {c} {r['YEAR']} vuoto senza il segno S")
        p["v"][r["YEAR"]] = n
    for a in anni:
        tot, dom, unk = tipi["TOTAL"][a], tipi["DOMESTIC"][a], tipi["UNKNWN"][a]
        est = tot - dom - unk
        if tipi["FOREIGN"].get(a) != est:
            errori.append(f"JQ06 {a}: formati all'estero {tipi['FOREIGN'].get(a)} diverso da totale - Irlanda - sconosciuti ({est})")
        pubb = sum(p["v"].get(a) or 0 for p in paesi.values())
        sopp = sum(1 for p in paesi.values() if p["v"].get(a) is None)
        if not 0 <= est - pubb < 25 * max(sopp, 1):
            errori.append(f"JQ06 {a}: formati all'estero {est}, Paesi pubblicati {pubb}, soppressi {sopp}: i conti non tornano")
    return {"anni": anni, "totale": tipi["TOTAL"], "irlanda": tipi["DOMESTIC"], "sconosciuto": tipi["UNKNWN"],
            "estero": {a: tipi["TOTAL"][a] - tipi["DOMESTIC"][a] - tipi["UNKNWN"][a] for a in anni}, "paesi": paesi}, errori


# ---------------------------------------------------------------- codice di condotta (allegati A e B)
def liste_codice(body):
    def lista(id_):
        m = re.search(r'<h[234] id="' + id_ + r'"[^>]*>.*?</h[234]>\s*(?:<p>.*?</p>\s*)*<ul>(.*?)</ul>', body, re.S)
        return [H.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<li>(.*?)</li>", m.group(1), re.S)] if m else []
    return {"rosso": lista("red-countries---active-recruitment-is-not-permitted"),
            "ambra": lista("amber-countries---international-recruitment-is-only-permitted-in-compliance-with-the-terms-of-the-government-to-government-agreement"),
            "verde": lista("annex-b-green-countries-with-government-to-government-agreement-in-place-with-the-uk")}


def main():
    nuovo = "--nuovo" in sys.argv
    oggi = date.today().isoformat()
    errori = []
    fonti, testi, grezzi = {}, {}, {}
    for k, u in PAGINE.items():
        st, b, h = get(u)
        if st != 200:
            errori.append(f"{k}: HTTP {st} ({u})")
            continue
        testi[k], grezzi[k] = testo_html(b), b.decode("utf-8", "replace")
        fonti[k] = {"url": u, "http": st, "sha256": hashlib.sha256(testi[k].encode()).hexdigest(), "letto_il": oggi}
        m = re.search(r"Last updated:\s*(\d\d)/(\d\d)/(\d{4})", testi[k])
        if m:
            fonti[k]["aggiornata"] = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    fonti.get("nmc_pagina", {})["titolo"] = "NMC registration data reports"
    fonti.get("nmc_costi", {})["titolo"] = "NMC: How much is it going to cost? (trained outside the UK)"
    fonti.get("nmc_intl", {})["titolo"] = "NMC: Information for internationally trained applicants"
    fonti.get("oms_qa", {})["titolo"] = "WHO: WHO health workforce support and safeguards list (questions and answers)"
    fonti.get("oms_ssl2023", {})["titolo"] = "WHO health workforce support and safeguards list 2023"
    # GOV.UK codice
    st, b, _ = get(API_GOVUK + CODICE)
    liste = {}
    if st != 200:
        errori.append(f"codice GOV.UK: HTTP {st}")
    else:
        d = json.loads(b)
        body = d["details"]["body"]
        testi["codice"] = testo_html(body)
        fonti["codice"] = {"url": "https://www.gov.uk" + CODICE, "api": API_GOVUK + CODICE, "http": st, "titolo": d["title"],
                           "aggiornata": d["public_updated_at"][:10], "sha256": hashlib.sha256(testi["codice"].encode()).hexdigest(), "letto_il": oggi,
                           "licenza": "Open Government Licence v3.0"}
        liste = liste_codice(body)
        if len(liste["rosso"]) != 54 or liste["ambra"] != ["Kenya", "Nepal"] or len(liste["verde"]) < 1:
            errori.append(f"codice: allegati A/B cambiati: {len(liste['rosso'])} rossi, ambra {liste['ambra']}, verdi {liste['verde']}")
    # OMS: PDF della lista 2023
    m = re.search(r'(https://iris\.who\.int/server/api/core/bitstreams/[0-9a-f-]+/content)[^>]*>\s*Download', grezzi.get("oms_ssl2023", ""))
    oms_paesi = []
    if not m:
        errori.append("OMS: link al PDF della lista 2023 non trovato")
    else:
        st, b, _ = get(m.group(1))
        if st != 200 or not b.startswith(b"%PDF"):
            errori.append(f"OMS: PDF della lista 2023 non leggibile (HTTP {st})")
        else:
            import subprocess
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                f.write(b)
                f.flush()
                t = subprocess.run(["pdftotext", f.name, "-"], capture_output=True, text=True).stdout
            testi["oms_pdf"] = re.sub(r"\s+", " ", t)
            fonti["oms_pdf"] = {"url": m.group(1), "http": st, "sha256": hashlib.sha256(b).hexdigest(), "byte": len(b), "letto_il": oggi,
                                "titolo": "WHO health workforce support and safeguards list 2023 (PDF)", "licenza": "CC BY-NC-SA 3.0 IGO"}
            for reg, n in REGIONI_OMS.items():
                if f"{reg} ({n})" not in testi["oms_pdf"]:
                    errori.append(f"OMS 2023: '{reg} ({n})' non trovato nel PDF")
            oms_paesi = [NOMI_OMS.get(p, p) for p in liste.get("rosso", [])] + ["Nepal"]
            for p in oms_paesi:
                if p not in testi["oms_pdf"]:
                    errori.append(f"OMS 2023: {p} non trovato nel PDF")
            if "Kenya" in testi["oms_pdf"] or len(oms_paesi) != 55:
                errori.append("OMS 2023: Kenya nel PDF o Paesi diversi da 55")
    stato_2026 = "non pubblicata"
    pubblicazioni = re.findall(r'<a[^>]*href="(/publications/[^"]+)"[^>]*>([^<]*[Ss]afeguards list[^<]*)', grezzi.get("oms_qa", ""))
    fonti.get("oms_qa", {})["pubblicazioni_collegate"] = [t.strip() for _, t in pubblicazioni]
    if not pubblicazioni or any("2026" in t or "2026" in u for u, t in pubblicazioni):
        stato_2026 = "DA CONTROLLARE: la pagina dell'OMS sembra collegare una pubblicazione 2026"
        errori.append("OMS: la pagina sembra collegare una lista 2026 pubblicata: rileggere e aggiornare le pagine")
    # NMC: file del registro
    url_nmc = link_nmc(grezzi.get("nmc_pagina", ""))
    if not url_nmc:
        errori.append("NMC: link al file del registro non trovato")
        nmc = {}
    else:
        nome_f = url_nmc.rsplit("/", 1)[1]
        b, meta = scarica(url_nmc, GREZZI / "infermieri" / nome_f, nuovo=nuovo)
        nmc, e = leggi_nmc(b)
        errori += e
        fonti["nmc_xlsx"] = {"url": url_nmc, "file": nome_f, "byte": len(b), "sha256": hashlib.sha256(b).hexdigest(), "http": meta.get("http", 200),
                             "last_modified": meta.get("last_modified", ""), "scaricato_il": meta.get("scaricato_il", oggi),
                             "titolo": "NMC register data tables (UK)", "licenza": "NMC terms and conditions (section 6): figures cited as facts with a link"}
    # Irlanda
    st, b, _ = get(JQ06_API)
    jq = {}
    if st != 200:
        errori.append(f"JQ06: API data.gov.ie HTTP {st}")
    else:
        pk = json.loads(b)["result"]
        if pk.get("license_id") != "CC-BY-4.0":
            errori.append(f"JQ06: licenza cambiata {pk.get('license_id')}")
        csvs = [r for r in pk["resources"] if (r.get("format") or "").upper() == "CSV"]
        pdfs = [r for r in pk["resources"] if (r.get("format") or "").upper() == "PDF"]
        if len(csvs) != 1 or len(pdfs) != 1:
            errori.append("JQ06: risorse CSV/PDF cambiate")
        else:
            bc, meta = scarica(csvs[0]["url"], GREZZI / "infermieri" / "jq06.csv", nuovo=True)
            jq, e = leggi_jq06(bc)
            errori += e
            st2, bp, _ = get(pdfs[0]["url"])
            if st2 == 200:
                import subprocess
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                    f.write(bp)
                    f.flush()
                    testi["jq06_metadati"] = re.sub(r"\s+", " ", subprocess.run(["pdftotext", f.name, "-"], capture_output=True, text=True).stdout).replace("’", "'")
            else:
                errori.append(f"JQ06: metadati HTTP {st2}")
            fonti["jq06_scheda"] = {"url": JQ06_SCHEDA, "api": JQ06_API, "http": st, "titolo": pk["title"], "editore": pk["organization"]["title"],
                                    "licenza": pk["license_title"], "licenza_url": "https://creativecommons.org/licenses/by/4.0/",
                                    "aggiornata": pk["metadata_modified"][:10], "letto_il": oggi}
            fonti["jq06_csv"] = {"url": csvs[0]["url"], "byte": len(bc), "sha256": hashlib.sha256(bc).hexdigest(), "codifica": "cp1252",
                                 "last_modified": meta.get("last_modified", ""), "scaricato_il": meta.get("scaricato_il", oggi), "http": meta.get("http", 200)}
            fonti["jq06_metadati"] = {"url": pdfs[0]["url"], "http": st2, "sha256": hashlib.sha256(bp).hexdigest(), "letto_il": oggi}
    # frammenti
    for k, v in LETTURE.items():
        if v["frammento"] not in testi.get(v["fonte"], ""):
            errori.append(f"{k}: frammento non trovato in {v['fonte']}: {v['frammento'][:110]!r}")
    if sum(LETTURE[k]["valore"] for k in ("costo_valutazione", "costo_cbt", "costo_osce", "costo_iscrizione")) != LETTURE["costo_totale"]["valore"]:
        errori.append("NMC: le voci dei costi non sommano al totale scritto")
    scartati = {}
    for k, v in SCARTATI.items():
        t = testi.get(v["fonte"], "")
        scartati[k] = dict(v, presente=v["frammento"] in t and all(x in t for x in v["voci"]))
    # Home Office
    rif = json.loads((RADICE / "dati" / "rifiuti.json").read_text(encoding="utf-8"))
    f_ho = fonte_ho(rif, FILE_HO.read_bytes())
    sott, gruppi, tutte = leggi_sottotipi(FILE_HO, [SOTTOTIPO])
    if gruppi[SOTTOTIPO] != [("Work", "Worker")]:
        errori.append(f"Home Office: {SOTTOTIPO} in gruppi inattesi {gruppi[SOTTOTIPO]}")
    e, n_ho = controllo_ho(rif, sott[SOTTOTIPO], SOTTOTIPO)
    errori += e
    hcw = {naz: per_anno(q) for naz, q in sott[SOTTOTIPO].items()}
    trimestri = sorted({q for v in sott[SOTTOTIPO].values() for q in v})
    mancanti = [NOMI_HO.get(p, p) for p in liste.get("rosso", []) + liste.get("ambra", []) if NOMI_HO.get(p, p) not in tutte]
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda(QUERY) if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom or any(k not in dom["query"] for k in QUERY):
        errori.append("domanda: autocompletamento mancante o incompleto (lanciare con --domanda)")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    letture = {k: {"valore": v["valore"], "fonte": v["fonte"], "frammento": v["frammento"]} for k, v in LETTURE.items()}
    contenuto = {"letture": letture, "fonti": fonti, "nmc": nmc, "irlanda": jq,
                 "codice": {**liste, "nomi_oms": NOMI_OMS, "nomi_ho": NOMI_HO, "assenti_dal_file_ho": mancanti},
                 "oms": {"lista_2023": oms_paesi, "regioni_2023": REGIONI_OMS, "lista_2026": stato_2026},
                 "hcw": {"fonte": f_ho, "trimestri": trimestri, "controlli_work": n_ho, "naz": hcw}, "scartati": scartati}
    uscita = {"_nota": "Generato da raccolta/infermieri.py: non modificare a mano (i valori letti a mano stanno in LETTURE dentro lo script). "
                       "NMC: registro e nuovi iscritti per Paese di formazione (citati come fatti); Irlanda: JQ06, CC BY 4.0; GOV.UK e Home Office: OGL v3.0; "
                       "OMS: lista 2023 (la 2026 non è pubblicata). hcw.naz: nazionalità -> anno -> M (richiedenti principali) / D (familiari) = "
                       "[concessi, rifiutati, ritirati, decaduti].",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: NMC al {nmc['date'][-1]} ({nmc['totale'][-1]:,} sul registro, {len(nmc['paesi'])} Paesi); "
          f"Irlanda {jq['anni'][-1]} ({jq['totale'][jq['anni'][-1]]:,}); codice: {len(liste['rosso'])} rossi, ambra {liste['ambra']}, verdi {liste['verde']}; "
          f"OMS 2023: {len(oms_paesi)} Paesi, 2026 {stato_2026}; Health and Care Worker {trimestri[0]}–{trimestri[-1]}, {len(hcw)} nazionalità, "
          f"{n_ho} confronti con il gruppo Work; assenti dal file HO: {mancanti}; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
