"""Legge le pagine ufficiali su OPT e STEM OPT (USCIS, ICE/SEVP, Federal Register, eCFR) e scrive
visaincome/dati/opt.json (sezione "US OPT and STEM OPT" del sito, dal 30/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/opt.py              # rilegge le pagine e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/opt.py --domanda    # rifà anche l'autocompletamento di Google (circa 1 minuto)

Come funziona
- uscis.gov, ice.gov e studyinthestates.dhs.gov rispondono 403 a urllib (protezione Akamai): si leggono con Chromium
  tramite raccolta/browser.js (Playwright; serve node). Il testo è il textContent della pagina, spazi normalizzati.
  La tariffa del modulo I-765 e quella del servizio "premium processing" (I-907) si leggono dal selettore della pagina
  G-1055 (Fee Schedule), che mostra la tabella del modulo scelto.
- Federal Register: API JSON (titolo, tipo, citazione, data, data di efficacia, fine dei commenti, sommario). Il testo
  completo su federalregister.gov chiede una verifica: per i frammenti si legge il PDF ufficiale su govinfo.gov (pdftotext).
- eCFR (8 CFR 214.2): elenco delle versioni e testo di oggi, per sapere che cosa dice il testo codificato sulla scadenza
  della domanda di OPT (60 o 30 giorni dopo la fine del programma).
- LETTURE (sotto) contiene ogni valore letto A MANO il 30/10/2026 con il FRAMMENTO DI TESTO della pagina ufficiale da cui viene.
  A ogni lancio lo script riscarica le pagine e controlla che ogni frammento ci sia ancora: se un frammento manca,
  la pagina è cambiata e il JSON NON viene aggiornato (esce con codice 1) finché qualcuno non rilegge la pagina e aggiorna LETTURE.
- ASSENZE: frasi che NON devono comparire (es. "(c)(3)" tra le categorie I-765 con la tariffa aggiuntiva della legge H.R. 1).
- Domanda: autocompletamento di Google (client=firefox, hl=en, gl=us/in), salvata in "domanda".
Nessun testo copiato per intero: si pubblicano fatti brevi (importi, scadenze) con il link alla pagina ufficiale.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "opt.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

# ---------------------------------------------------------------- pagine ufficiali lette con il browser
PAGINE = {
    "i765": ("https://www.uscis.gov/i-765", "U.S. Citizenship and Immigration Services (USCIS)", "I-765, Application for Employment Authorization"),
    "g1055": ("https://www.uscis.gov/g-1055", "USCIS", "G-1055, Fee Schedule"),
    "g1055_i765": ("https://www.uscis.gov/g-1055#fee=97312", "USCIS", "G-1055, Fee Schedule: Form I-765"),
    "g1055_i907": ("https://www.uscis.gov/g-1055#fee=97333", "USCIS", "G-1055, Fee Schedule: Form I-907, Request for Premium Processing Service"),
    "opt": ("https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/optional-practical-training-opt-for-f-1-students",
            "USCIS", "Optional Practical Training (OPT) for F-1 Students"),
    "stem": ("https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/optional-practical-training-extension-for-stem-students-stem-opt",
             "USCIS", "Optional Practical Training Extension for STEM Students (STEM OPT)"),
    "premium": ("https://www.uscis.gov/forms/all-forms/how-do-i-request-premium-processing", "USCIS", "How Do I Request Premium Processing?"),
    "online": ("https://www.uscis.gov/file-online/forms-available-to-file-online", "USCIS", "Forms Available to File Online"),
    "ice": ("https://www.ice.gov/sevis/practical-training", "U.S. Immigration and Customs Enforcement (ICE), SEVP", "Practical Training"),
    "sevp_disoccupazione": ("https://studyinthestates.dhs.gov/sevis-help-hub/student-records/fm-student-employment/unemployment-counter",
                            "Study in the States (DHS, SEVP)", "SEVIS Help Hub: Unemployment Counter"),
    "sevp_opt": ("https://studyinthestates.dhs.gov/sevis-help-hub/student-records/fm-student-employment/f-1-optional-practical-training-opt",
                 "Study in the States (DHS, SEVP)", "SEVIS Help Hub: F-1 Optional Practical Training (OPT)"),
}

# ---------------------------------------------------------------- Federal Register (API JSON + PDF su govinfo)
DOCUMENTI_FR = {
    "tasse_opt": "2026-20660",       # proposta: Optional Practical Training Fees (8/10/2026)
    "durata_fissa": "2026-14439",    # regola finale: Fixed Time Period of Admission (17/7/2026), efficacia rinviata dal tribunale
    "premium": "2026-00321",         # regola finale: Adjustment to Premium Processing Fees (12/1/2026, in vigore dall'1/3/2026)
    "hr1_2027": "2026-20187",        # avviso: FY 2027 Inflation Adjustment to H.R. 1 Immigration Fees (1/10/2026)
}
ECFR_VERSIONI = "https://www.ecfr.gov/api/versioner/v1/versions/title-8.json?section=214.2"
ECFR_TESTO = "https://www.ecfr.gov/api/versioner/v1/full/{d}/title-8.xml?section=214.2"
ECFR_PAGINA = "https://www.ecfr.gov/current/title-8/chapter-I/subchapter-B/part-214/section-214.2"
ECFR_PRIMA = "2026-09-14"   # ultimo giorno del testo precedente alla regola del 17/7/2026 (60 giorni)
FRASE_GRAZIA_60 = ("An F-1 student who has completed a course of study and any authorized practical training following completion of studies "
                   "will be allowed an additional 60-day period to prepare for departure from the United States")

# ---------------------------------------------------------------- letture a mano (30/10/2026)
# fonte: chiave di PAGINE ("pagina") o di DOCUMENTI_FR ("fr:<chiave>" = sommario dell'API, "pdf:<chiave>" = testo del PDF).
LETTURE = {
    "tassa_carta": {"valore": 520, "fonte": "g1055_i765",
                    "frammento": "General Filing for initial, replacement, or renewal Employment Authorization Document (EAD), unless noted below. "
                                 "Review all options below to confirm if you are eligible for a reduced fee or fee exemption. $520 $470"},
    "tassa_online": {"valore": 470, "fonte": "g1055_i765",
                     "frammento": "General Filing for initial, replacement, or renewal Employment Authorization Document (EAD), unless noted below. "
                                  "Review all options below to confirm if you are eligible for a reduced fee or fee exemption. $520 $470"},
    "premium": {"valore": 1780, "fonte": "g1055_i907",
                "frammento": "Form I-907 with Form I-765, Application for Employment Authorization I-765 (OPT and STEM-OPT classifications). $1,780* $1,780*"},
    "premium_prima": {"valore": 1685, "fonte": "pdf:premium", "frammento": "set the fee for the premium processing of Form I–765 at $1,685"},
    "premium_dal": {"valore": "2026-03-01", "fonte": "pdf:premium", "frammento": "A request for premium processing postmarked on or after March 1, 2026, must include the new fee"},
    "premium_giorni": {"valore": 30, "fonte": "premium", "frammento": "30 business days for Form I-765"},
    "online_opt": {"valore": True, "fonte": "online", "frammento": "(c)(3)(B) – F-1 student, post-completion OPT"},
    "online_stem": {"valore": True, "fonte": "online",
                    "frammento": "(c)(3)(C) – F-1 student, 24-month extension of OPT for science, technology, engineering and mathematics (STEM) students"},
    "finestra": {"valore": {"prima": 90, "dopo": 60, "dso": 30}, "fonte": "i765",
                 "frammento": "File Form I-765 up to 90 days before, but no later than 60 days after, your program end date. "
                              "You must file your Form I-765 within 30 days of the date that your DSO enters the recommendation for OPT into your SEVIS record."},
    "finestra_opt": {"valore": {"prima": 90, "dopo": 60, "dso": 30}, "fonte": "opt",
                     "frammento": "Must apply within 30 days after your DSO enters the recommendation for OPT into your SEVIS record, andMay apply up to 90 days "
                                  "before you complete your degree, but no later than 60 days after you complete your degree."},
    "inizio_max": {"valore": 60, "fonte": "sevp_opt",
                   "frammento": "Post-Completion OPT: Start Date must be on or after the Program End Date. It cannot be more than 60 days after the Program End Date."},
    "finestra_stem": {"valore": {"prima": 90, "dso": 60}, "fonte": "stem",
                      "frammento": "Submit the Form I-765, Application for Employment Authorization, up to 90 days before your current OPT employment authorization expires, "
                                   "and within 60 days of the date your designated school official (DSO) enters the recommendation for OPT into your "
                                   "Student and Exchange Visitor Information System (SEVIS) record."},
    "finestra_stem_i765": {"valore": 90, "fonte": "i765",
                           "frammento": "File Form I-765 up to 90 days before the expiration of your current OPT, if you are requesting a 24-month STEM extension."},
    "mesi_opt": {"valore": 12, "fonte": "ice", "frammento": "You can apply for 12 months of OPT at each education level"},
    "mesi_opt_uscis": {"valore": 12, "fonte": "opt",
                       "frammento": "Eligible students can apply to receive up to 12 months of OPT employment authorization before completing their academic studies "
                                    "(pre-completion) and/or after completing their academic studies (post-completion)."},
    "mesi_stem": {"valore": 24, "fonte": "stem", "frammento": "may apply for a 24-month extension of their post-completion optional practical training (OPT)"},
    "proroga_stem": {"valore": 180, "fonte": "stem",
                     "frammento": "If you file your STEM OPT extension application on time and your OPT period expires while your extension application is pending, "
                                  "we will automatically extend your employment authorization for 180 days."},
    "dopo_ead": {"valore": True, "fonte": "opt",
                 "frammento": "You may not begin your pre- or post-completion OPT until after we approve your Form I-765 and you receive your Employment Authorization Document (EAD)."},
    "disoccupazione": {"valore": 90, "fonte": "sevp_disoccupazione", "frammento": "Post-completion OPT: 90 days."},
    "disoccupazione_stem": {"valore": 150, "fonte": "sevp_disoccupazione", "frammento": "STEM OPT: 150 days, which includes any days accrued while on post-completion OPT."},
    "disoccupazione_uscis": {"valore": {"opt": 90, "stem": 150}, "fonte": "stem",
                             "frammento": "Initial post-completion OPT onlyUp to 90 days90 days24-month extensionAn additional 60 days150 days"},
    "conteggio_inizio": {"valore": True, "fonte": "sevp_disoccupazione", "frammento": "Look back to the Actual OPT Start Date for that period of OPT."},
    "conteggio_giorni": {"valore": True, "fonte": "sevp_disoccupazione", "frammento": "Count each day without employer information."},
    "rinvio_regola": {"valore": "2026-09-14", "fonte": "i765",
                      "frammento": "issued an order postponing the effective date of the final rule entitled “Establishing a Fixed Time Period of Admission and an "
                                   "Extension of Stay Procedure for Nonimmigrant Academic Students, Exchange Visitors, and Representatives of Foreign Information Media,” "
                                   "published at 91 Fed. Reg. 44976 (July 17, 2026)"},
    "regole_precedenti": {"valore": True, "fonte": "i765", "frammento": "Until such time, USCIS will proceed under the previous regulatory provisions."},
    "hr1_altre": {"valore": True, "fonte": "g1055", "frammento": "Certain forms have an additional fee required along with any filing fee."},
    "proposta_importi": {"valore": {"iniziale": 70000, "successiva": 30000}, "fonte": "fr:tasse_opt",
                         "frammento": "$70,000 for initial OPT; and $30,000 for any subsequent OPT."},
    "proposta_scuole": {"valore": True, "fonte": "pdf:tasse_opt",
                        "frammento": "fee that an SEVP-certified educational institution must pay for each F–1 nonimmigrant student prior to a DSO’s initial"},
    "proposta_stem": {"valore": True, "fonte": "pdf:tasse_opt",
                      "frammento": "(regardless of whether it is another pre-completion OPT, postcompletion OPT, or STEM OPT extension)"},
    "proposta_docket": {"valore": "ICEB-2026-0100", "fonte": "pdf:tasse_opt", "frammento": "DHS Docket No. ICEB–2026–0100"},
    "proposta_da_quando": {"valore": True, "fonte": "pdf:tasse_opt",
                           "frammento": "The OPT fee of $70,000 would start to apply for F–1 nonimmigrant students who will receive a DSO recommendation for any type of OPT that is dated on or after the effective date of the final rule."},
    "proposta_60_giorni": {"valore": 60, "fonte": "pdf:tasse_opt",
                           "frammento": "DHS is proposing that the final rule take effect 60 days after the date of publication of the final rule in the Federal Register"},
    "regola_30": {"valore": 30, "fonte": "pdf:durata_fissa",
                  "frammento": "In paragraph (f)(11)(i)(B)(2), removing the number ‘‘60’’ and adding, in its place, the number ‘‘30’’"},
    "regola_grazia_30": {"valore": 30, "fonte": "pdf:durata_fissa",
                         "frammento": "since students will now have 30 days, rather than 60 days, to depart the country or seek to maintain lawful status"},
}
# Frasi che NON devono esserci: se compaiono, una regola è cambiata (es. tariffa H.R. 1 estesa all'OPT).
ASSENZE = [("g1055_i765", "(c)(3)")]
# Regole del Federal Register: tipo e date attese (se cambiano, lo script si ferma).
ATTESI_FR = {
    "tasse_opt": {"type": "Proposed Rule", "publication_date": "2026-10-08", "comments_close_on": "2026-11-09"},
    "durata_fissa": {"type": "Rule", "publication_date": "2026-07-17", "effective_on": "2026-09-15"},
    "premium": {"type": "Rule", "publication_date": "2026-01-12", "effective_on": "2026-03-01"},
    "hr1_2027": {"type": "Notice", "publication_date": "2026-10-01", "effective_on": "2026-10-16"},
}

QUERY = {"us": ["opt application", "opt application deadline", "opt deadline", "opt unemployment", "opt unemployment days", "opt fee", "opt fee 2026",
                "stem opt", "stem opt extension", "stem opt extension fee", "stem opt unemployment", "opt calculator", "opt 70000 fee", "opt proposed fee",
                "opt 60 days", "opt 90 days", "when to apply for opt", "i-765 fee", "i-765 fee opt", "opt grace period", "opt 30 days"],
         "in": ["opt fee", "opt unemployment days", "stem opt extension fee", "opt application deadline", "opt 70000"]}


def get(u, tentativi=3, comprimi=False):
    for i in range(tentativi):
        try:
            h = dict(UA, **({"Accept-Encoding": "gzip"} if comprimi else {}))
            r = urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=60)
            b = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                import gzip
                b = gzip.decompress(b)
            return r.status, b
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, b""
            time.sleep(2 + 2 * i)
    return 0, b""


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def leggi_browser():
    js = Path(__file__).resolve().parent / "browser.js"
    urls = [v[0] for v in PAGINE.values()]
    r = subprocess.run(["node", str(js)] + urls, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit(f"ERRORE: lettura con il browser non riuscita ({r.stderr[-400:]})")
    return json.loads(r.stdout)


def leggi_fr(num):
    st, b = get(f"https://www.federalregister.gov/api/v1/documents/{num}.json")
    if st != 200:
        return None, ""
    d = json.loads(b)
    testo = ""
    st2, pdf = get(d["pdf_url"])
    if st2 == 200 and pdf[:4] == b"%PDF":
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.pdf"
            f.write_bytes(pdf)
            out = subprocess.run(["pdftotext", str(f), "-"], capture_output=True, text=True, timeout=120).stdout
            testo = norm(out)
    meta = {k: d.get(k) for k in ("title", "type", "citation", "publication_date", "effective_on", "comments_close_on", "html_url", "pdf_url", "abstract", "document_number")}
    meta["sha256_pdf"] = hashlib.sha256(pdf).hexdigest() if st2 == 200 else None
    return meta, testo


def leggi_ecfr():
    st, b = get(ECFR_VERSIONI, comprimi=True)
    if st != 200:
        return None
    versioni = json.loads(b)["content_versions"]
    ultima = versioni[-1]["date"]
    st, x = get(ECFR_TESTO.format(d=ultima), comprimi=True)
    if st != 200:
        return None
    t = norm(re.sub(r"<[^>]+>", " ", x.decode("utf-8", "replace")))
    m = re.search(r"up to 90 days prior to his or her program end date and no later than (\d+) days after his or her program end date", t)
    # testo precedente alla regola del 17/7/2026 (efficace sulla carta dal 15/9/2026, rinviata dal tribunale): versione del giorno prima
    st, x0 = get(ECFR_TESTO.format(d=ECFR_PRIMA), comprimi=True)
    t0 = norm(re.sub(r"<[^>]+>", " ", x0.decode("utf-8", "replace"))) if st == 200 else ""
    m0 = re.search(r"up to 90 days prior to his or her program end date and no later than (\d+) days after his or her program end date", t0)
    return {"ultima_versione": ultima, "versioni_2026": [v["date"] for v in versioni if v["date"].startswith("2026")],
            "giorni_dopo_fine_programma": int(m.group(1)) if m else None, "pagina": ECFR_PAGINA,
            "frammento": m.group(0) if m else None,
            "precedente": {"data": ECFR_PRIMA, "giorni_dopo_fine_programma": int(m0.group(1)) if m0 else None,
                           "grazia_60": FRASE_GRAZIA_60 in t0, "frammento_grazia": FRASE_GRAZIA_60,
                           "url": f"https://www.ecfr.gov/on/{ECFR_PRIMA}/title-8/section-214.2"}}


def autocompleta(q, gl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": "en", "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda():
    out = {}
    for gl, qs in QUERY.items():
        for q in qs:
            out[f"{gl}|{q}"] = autocompleta(q, gl)
            time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<us|in>&hl=en&q=…", "query": out}


def main():
    oggi = date.today().isoformat()
    errori = []
    pagine = leggi_browser()
    testi = {}
    fonti = {}
    for k, (u, editore, titolo) in PAGINE.items():
        p = pagine.get(u, {})
        if p.get("http") != 200 or len(p.get("testo", "")) < 500:
            errori.append(f"pagina non leggibile (HTTP {p.get('http')}): {u}")
        testi[k] = p.get("testo", "")
        fonti[k] = {"url": u.split("#")[0], "titolo": titolo, "editore": editore, "http": p.get("http"), "letto_il": oggi,
                    "aggiornata": p.get("aggiornata", ""), "sha256": hashlib.sha256(testi[k].encode("utf-8")).hexdigest()}
    fr = {}
    for k, num in DOCUMENTI_FR.items():
        meta, testo = leggi_fr(num)
        if not meta:
            errori.append(f"Federal Register: documento {num} non leggibile")
            continue
        for campo, atteso in ATTESI_FR[k].items():
            if meta.get(campo) != atteso:
                errori.append(f"Federal Register {num}: {campo} = {meta.get(campo)!r}, atteso {atteso!r}")
        meta["letto_il"] = oggi
        fr[k] = meta
        testi[f"fr:{k}"] = norm(meta.get("abstract") or "")
        testi[f"pdf:{k}"] = testo
    for k, v in LETTURE.items():
        if v["frammento"] not in testi.get(v["fonte"], ""):
            errori.append(f"{k}: frammento non trovato in {v['fonte']}: {v['frammento'][:120]!r}")
    for fonte, frase in ASSENZE:
        if frase in testi.get(fonte, ""):
            errori.append(f"{fonte}: compare {frase!r} (regola cambiata: rileggere la pagina)")
    ecfr = leggi_ecfr()
    if not ecfr or ecfr["giorni_dopo_fine_programma"] not in (30, 60):
        errori.append("eCFR: testo di 8 CFR 214.2(f)(11)(i)(B)(2) non leggibile o cambiato")
    elif ecfr["precedente"]["giorni_dopo_fine_programma"] != 60 or not ecfr["precedente"]["grazia_60"]:
        errori.append(f"eCFR {ECFR_PRIMA}: testo precedente (60 giorni) non trovato")
    # la regola rinviata e il testo codificato devono restare coerenti con quello che dicono le pagine
    if ecfr and ecfr["giorni_dopo_fine_programma"] == 60 and LETTURE["rinvio_regola"]["frammento"] in testi.get("i765", ""):
        errori.append("eCFR torna a 60 giorni mentre USCIS parla ancora del rinvio: rileggere e aggiornare le pagine")
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom:
        errori.append("domanda: nessun dato di autocompletamento (lanciare con --domanda)")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    letture = {k: {"valore": v["valore"], "fonte": v["fonte"], "frammento": v["frammento"]} for k, v in LETTURE.items()}
    contenuto = {"letture": letture, "fonti": fonti, "federal_register": fr, "ecfr": ecfr}
    uscita = {"_nota": "Generato da raccolta/opt.py: non modificare a mano (i valori letti a mano stanno in LETTURE dentro lo script). "
                       "Fonti: USCIS, ICE/SEVP, Federal Register, eCFR, lette il giorno indicato.",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} pagine ufficiali, {len(fr)} documenti del Federal Register, {len(letture)} valori controllati; "
          f"I-765 ${letture['tassa_online']['valore']} online / ${letture['tassa_carta']['valore']} su carta, premium ${letture['premium']['valore']}; "
          f"eCFR {ecfr['ultima_versione']} ({ecfr['giorni_dopo_fine_programma']} giorni); impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
