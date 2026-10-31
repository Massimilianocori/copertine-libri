"""Legge le pagine GOV.UK sul Graduate visa (guida, Immigration Rules Appendix Graduate, Statement of Changes HC 1333 e
nota esplicativa, guida all'Immigration Health Surcharge, tabella delle tariffe del Home Office) e scrive
visaincome/dati/graduate.json (sezione "UK Graduate visa" del sito, dal 30/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/graduate.py              # rilegge le pagine e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/graduate.py --domanda    # rifà anche l'autocompletamento di Google (circa 1 minuto)

Come funziona
- GOV.UK: Content API (https://www.gov.uk/api/content/<percorso>), testo HTML ripulito (tag tolti, spazi normalizzati).
  Per ogni pagina si salvano la data di aggiornamento pubblica (public_updated_at) e l'impronta SHA-256 del testo.
- Tariffe: la pagina "UK visa fees" elenca le tabelle ODS del Home Office; si legge la più recente e la riga
  "Graduate Route – main applicant and dependants" (colonna della tariffa in vigore dalla data della tabella).
- LETTURE (sotto): ogni valore letto A MANO il 30/10/2026 con il FRAMMENTO DI TESTO della pagina ufficiale da cui viene.
  Se un frammento manca, la pagina è cambiata: il JSON NON viene aggiornato (esce con codice 1) finché qualcuno non
  rilegge la pagina e aggiorna LETTURE.
- Domanda: autocompletamento di Google (client=firefox, hl=en, gl=uk/in/ng/pk), salvata in "domanda".
Contiene informazioni del settore pubblico rilasciate con la Open Government Licence v3.0.
"""
import hashlib
import html as H
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "graduate.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
API = "https://www.gov.uk/api/content"

# chiave: (percorso GOV.UK, titolo, parti della guida da leggere o None per il corpo intero)
PAGINE = {
    "guida": ("/graduate-visa", "Graduate visa (GOV.UK guide)", None),
    "appendice": ("/guidance/immigration-rules/immigration-rules-appendix-graduate", "Immigration Rules: Appendix Graduate", None),
    "hc1333": ("/government/publications/statement-of-changes-to-the-immigration-rules-hc-1333-14-october-2025/"
               "statement-of-changes-to-the-immigration-rules-hc-1333-14-october-2025-accessible-version",
               "Statement of changes to the Immigration Rules: HC 1333, 14 October 2025", None),
    "memorandum": ("/government/publications/statement-of-changes-to-the-immigration-rules-hc-1333-14-october-2025/"
                   "explanatory-memorandum-to-the-statement-of-changes-to-the-immigration-rules-hc-1333-14-october-2025-accessible",
                   "Explanatory memorandum to the Statement of changes HC 1333", None),
    "ihs": ("/healthcare-immigration-application", "Pay for UK healthcare as part of your immigration application", None),
    "tariffe": ("/government/publications/visa-regulations-revised-table", "UK visa fees (Home Office)", None),
}

LETTURE = {
    "durata_2_anni": {"valore": {"mesi": 24, "fino_al": "2026-12-31"}, "fonte": "guida", "frammento": "2 years if you apply on or before 31 December 2026"},
    "durata_18_mesi": {"valore": {"mesi": 18, "dal": "2027-01-01"}, "fonte": "guida", "frammento": "18 months if you apply on or after 1 January 2027"},
    "durata_phd": {"valore": {"mesi": 36}, "fonte": "guida", "frammento": "If you have a PhD or other doctoral qualification, it will last for 3 years."},
    "inizio": {"valore": "decisione", "fonte": "guida", "frammento": "Your visa will start from the day your application is approved."},
    "non_estendibile": {"valore": True, "fonte": "guida", "frammento": "You cannot extend your Graduate visa."},
    "prima_scadenza": {"valore": True, "fonte": "guida", "frammento": "You must apply before your Student visa or Tier 4 (General) student visa expires."},
    "decisione_settimane": {"valore": 8, "fonte": "guida", "frammento": "you’ll usually get a decision on your visa within 8 weeks"},
    "in_uk": {"valore": True, "fonte": "guida", "frammento": "You must be in the UK when you apply."},
    "tassa": {"valore": 937, "fonte": "guida", "frammento": "pay the £937 application fee"},
    "ihs_anno": {"valore": 1035, "fonte": "guida", "frammento": "this is usually £1,035 for each year you’ll be in the UK"},
    "ihs_18": {"valore": 1552.5, "fonte": "guida", "frammento": "18 months - it will cost £1,552.50"},
    "ihs_24": {"valore": 2070, "fonte": "guida", "frammento": "2 years - it will cost £2,070"},
    "ihs_36": {"valore": 3105, "fonte": "guida", "frammento": "3 years - it will cost £3,105"},
    "familiari_stessa_fine": {"valore": True, "fonte": "guida", "frammento": "If their application is successful, their visa will end on the same date as yours."},
    "regola_gr81": {"valore": True, "fonte": "appendice", "frammento": "Period granted from date of decision PhD or other doctoral qualification 3 years"},
    "regola_18": {"valore": True, "fonte": "appendice",
                  "frammento": "All other qualifications 18 months if the applicant has successfully completed a course at UK bachelor’s degree or master’s degree level, "
                               "or another relevant qualification that meets the requirement of ST8.1/2/3 of the Rules, and the application is made on or after 1 January 2027."},
    "hc1333_18": {"valore": True, "fonte": "hc1333",
                  "frammento": "All other qualifications 18 months if the applicant has successfully completed a course at UK bachelor’s degree or master’s degree level, "
                               "or another relevant qualification that meets the requirement of ST8.1/2/3 of the Rules, and the application is made on or after 1 January 2027."},
    "memorandum_526": {"valore": True, "fonte": "memorandum",
                       "frammento": "The change to 18 months will apply to applications submitted on or after 1 January 2027, with PhD graduates continuing to receive three years of leave."},
    "memorandum_motivo": {"valore": True, "fonte": "memorandum",
                          "frammento": "The Immigration White Paper published on 12 May announced the Government’s intention to reduce the duration of stay under the Graduate route to 18 months."},
    "ihs_adulti": {"valore": 1035, "fonte": "ihs", "frammento": "£1,035 per year for all other visa and immigration applications"},
    "ihs_minori": {"valore": 776, "fonte": "ihs", "frammento": "£776 per year for visa and immigration applicants who are under the age of 18 at time of application"},
    "ihs_mezzo_anno": {"valore": True, "fonte": "ihs", "frammento": "the yearly cost plus half the yearly cost, if it’s for 18 months or less"},
    "ihs_familiari": {"valore": True, "fonte": "ihs", "frammento": "Dependants aged 18 or over usually need to pay the same amount as you."},
}

QUERY = {"uk": ["graduate visa", "graduate visa 18 months", "graduate visa cost", "graduate visa cost 2026", "graduate visa fee", "graduate route",
                "graduate visa 2027", "graduate visa ihs", "graduate visa length", "graduate visa phd", "graduate visa when to apply",
                "graduate visa duration", "graduate visa changes", "graduate visa calculator", "psw visa uk"],
         "in": ["graduate visa uk", "uk graduate visa 18 months", "uk psw visa", "uk graduate visa cost", "uk graduate visa fee"],
         "ng": ["uk graduate visa", "graduate visa uk cost"],
         "pk": ["uk graduate visa", "uk psw visa 18 months"]}


def get(u, tentativi=3):
    for i in range(tentativi):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60)
            return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, b""
            time.sleep(2 + 2 * i)
    return 0, b""


def testo_html(h):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", h or ""))).strip()


def leggi_pagina(percorso):
    st, b = get(API + percorso)
    if st != 200:
        return {"http": st}, ""
    d = json.loads(b)
    det = d.get("details", {})
    if det.get("parts"):
        t = " ".join(f'{p["title"]}. {testo_html(p["body"])}' for p in det["parts"])
    else:
        t = testo_html(det.get("body", ""))
    meta = {"url": "https://www.gov.uk" + percorso, "titolo": d.get("title"), "http": st, "aggiornata": (d.get("public_updated_at") or "")[:10],
            "sha256": hashlib.sha256(t.encode("utf-8")).hexdigest()}
    return meta, t, d


def leggi_tariffa(d):
    """Tabella ODS più recente della pagina 'UK visa fees' e riga del Graduate Route."""
    allegati = [a for a in d["details"].get("attachments", []) if (a.get("url") or "").endswith(".ods")]
    if not allegati:
        return None
    a = allegati[0]   # la pagina elenca prima la tabella più recente
    st, b = get(a["url"])
    if st != 200:
        return None
    x = zipfile.ZipFile(io.BytesIO(b)).read("content.xml").decode("utf-8")
    righe = re.findall(r"<table:table-row[^>]*>(.*?)</table:table-row>", x, re.S)
    def celle(r):
        return [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", c[1] or ""))).strip()
                for c in re.findall(r"<table:table-cell([^>]*)(?:/>|>(.*?)</table:table-cell>)", r, re.S)]
    intest = next((celle(r) for r in righe if "Fees category" in " ".join(celle(r))), None)
    riga = next((celle(r) for r in righe if celle(r) and celle(r)[0].startswith("Graduate Route")), None)
    if not intest or not riga:
        return None
    return {"titolo": a.get("title"), "url": a["url"], "sha256": hashlib.sha256(b).hexdigest(), "intestazione": intest[:5], "riga": riga[:5]}


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
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<uk|in|ng|pk>&hl=en&q=…", "query": out}


def main():
    oggi = date.today().isoformat()
    errori = []
    fonti, testi, grezzi = {}, {}, {}
    for k, (percorso, titolo, _) in PAGINE.items():
        r = leggi_pagina(percorso)
        if len(r) < 3 or r[0].get("http") != 200:
            errori.append(f"pagina GOV.UK non leggibile: {percorso}")
            continue
        meta, t, d = r
        meta["letto_il"] = oggi
        meta["titolo_nostro"] = titolo
        fonti[k], testi[k], grezzi[k] = meta, t, d
    for k, v in LETTURE.items():
        if v["frammento"] not in testi.get(v["fonte"], ""):
            errori.append(f"{k}: frammento non trovato in {v['fonte']}: {v['frammento'][:120]!r}")
    tariffa = leggi_tariffa(grezzi["tariffe"]) if "tariffe" in grezzi else None
    if not tariffa:
        errori.append("tabella delle tariffe del Home Office non leggibile o senza la riga del Graduate Route")
    else:
        valori = [c for c in tariffa["riga"][1:3] if c.startswith("£")]
        if not valori or any(v != f"£{LETTURE['tassa']['valore']:,}" for v in valori):
            errori.append(f"tariffa del Graduate Route nella tabella ODS diversa da £{LETTURE['tassa']['valore']}: {tariffa['riga']}")
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
    contenuto = {"letture": letture, "fonti": fonti, "tariffa_ods": tariffa}
    uscita = {"_nota": "Generato da raccolta/graduate.py: non modificare a mano (i valori letti a mano stanno in LETTURE dentro lo script). "
                       "Fonti: GOV.UK (Open Government Licence v3.0), lette il giorno indicato.",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} pagine GOV.UK, {len(letture)} valori controllati; tariffa £{letture['tassa']['valore']} "
          f"({tariffa['titolo']}); IHS £{letture['ihs_anno']['valore']} l'anno; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
