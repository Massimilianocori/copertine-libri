"""Scarica e legge i numeri PPS (PPSN) assegnati in Irlanda per nazionalità e scrive visaincome/dati/ppsn.json
(pagine "How many [nazionalità] moved to Ireland" della sezione "Who moved where", dal 30/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/ppsn.py            # scarica (o riusa i file già in raccolta/_grezzi/) e scrive il JSON
    python3 visaincome/raccolta/ppsn.py --nuovo    # riscarica sempre i file ufficiali

Fonte: Department of Social Protection (Irlanda), raccolta "Annual Allocations: PPS Numbers" su gov.ie
(https://www.gov.ie/en/department-of-social-protection/collections/annual-allocations-pps-numbers/), scheda su data.gov.ie
"Personal Public Service Number (PPSN) Allocations" (licenza CC BY 4.0). Due file CSV, trovati ogni volta sulla pagina gov.ie
(il nome cambia a ogni aggiornamento, es. 20261019_PPSN_registrations_by_year_month_and_country.csv):
1. "PPSN registrations by year, month and country" (dal gennaio 2023, mensile): Paese = nazionalità della persona; " " = valore
   non pubblicato (piccolo); la riga "All" è il totale di tutte le nazionalità.
2. "PPSN registrations by year and country" (dal 2001, annuale, con la regione del mondo).
Controlli: intestazioni attese; per ogni nazionalità coperta i 12 (o meno, nell'anno in corso) mesi sono tutti pubblicati e la loro
somma è uguale al totale annuo del secondo file; somma annua di tutte le nazionalità = somma dei mesi della riga "All" (2023 →);
mesi consecutivi senza buchi; le 12 nazionalità della sezione ci sono tutte. Se un controllo fallisce il JSON NON viene toccato.

Domanda (autocompletamento Google, gl=ie e gl=in, 30/10/2026): salvata in DOMANDA qui sotto e nel JSON.
"""
import csv
import hashlib
import html
import io
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rifiuti import GREZZI, RADICE, scarica  # noqa: E402

USCITA = RADICE / "dati" / "ppsn.json"
PAGINA = "https://www.gov.ie/en/department-of-social-protection/collections/annual-allocations-pps-numbers/"
SCHEDA = "https://data.gov.ie/dataset/personal-public-service-number-ppsn-allocations"
API_SCHEDA = "https://data.gov.ie/api/3/action/package_show?id=personal-public-service-number-ppsn-allocations"
SERVIZIO = "https://www.gov.ie/en/department-of-social-protection/services/get-a-personal-public-service-pps-number/"
LICENZA, LICENZA_URL = "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
# codice Eurostat della sezione "Who moved where" -> nome nel file del Dipartimento
NAZIONALITA = {
    "US": "United States of America (the)", "UK": "United Kingdom of Great Britain and Northern Ireland", "CA": "Canada",
    "AU": "Australia", "IN": "India", "PK": "Pakistan", "NG": "Nigeria", "PH": "Philippines (the)", "CN": "China",
    "BR": "Brazil", "ZA": "South Africa", "NZ": "New Zealand",
}
# frasi della pagina del servizio PPS su gov.ie su cui si basano le pagine (controllate a ogni lancio)
FRASI_SERVIZIO = ["helps you access social welfare benefits, public services and information in Ireland",
                  "customers resident on the island of Ireland and customers resident abroad"]
# Autocompletamento Google (client=firefox, gl=ie, hl=en), letto il 30/10/2026 (risultati uguali con gl=in): "how many <nazionalità> in ireland"
DOMANDA = {
    "data": "2026-10-30",
    "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=ie&hl=en&q=…",
    "query": {
        "ie|how many indians in ireland": ["how many indians in ireland", "how many indians in ireland 2026", "how many indians in ireland percentage", "how many indians in ireland 2025", "how many indians in ireland 2025 statistics", "how many indians in ireland today", "how many hindus in ireland", "how many hindus in ireland 2016", "how many hindus in ireland 2025", "how many indians live in ireland 2025"],
        "ie|how many brazilians in ireland": ["how many brazilians in ireland", "how many brazilians in ireland 2026", "how many brazilians in ireland 2025", "how are there so many brazilians in ireland", "how many brazilians live in northern ireland", "how many brazilian live in ireland"],
        "ie|how many pakistanis in ireland": ["how many pakistanis in ireland", "how many pakistani in ireland 2025", "how many pakistani in ireland 2026", "how many pakistan in ireland", "how many pakistanis in northern ireland", "how many pakistani doctors in ireland", "how many indians and pakistanis in ireland", "pakistani population in ireland", "which country has most pakistani immigrants", "how many nationalities can a pakistani have"],
        "ie|how many nigerians in ireland": ["how many nigerians in ireland", "how many nigerians in ireland 2026", "how many nigerians in ireland 2025", "how many nigerians in northern ireland", "how many nigerian refugees in ireland", "how many nigerians live in northern ireland", "how many population has nigeria"],
        "ie|how many filipinos in ireland": ["how many filipinos in ireland", "how many filipinos in ireland 2026", "how many filipinos in ireland 2025", "how many filipino in ireland 2024", "how many filipinos working in ireland", "how many filipino nurses in ireland", "how many filipino workers in ireland", "how many filipinos in northern ireland"],
        "ie|how many chinese in ireland": ["how many chinese in ireland", "how many chinese in ireland 2025", "how many chinese restaurants in ireland", "how many chinese takeaways in ireland", "how many chinese in northern ireland", "how many chinese students in ireland", "how many chinese takeaways in northern ireland"],
        "ie|how many americans in ireland": ["how many americans in ireland", "how many us citizens in ireland", "how many americans live in ireland", "how many americans live in ireland 2025", "how many south americans in ireland", "how many african americans in ireland", "how many americans work in ireland", "how many latin americans in ireland", "how many american companies in ireland", "how many american expats in ireland"],
        "ie|how many british in ireland": ["how many british in ireland", "how many brits in ireland", "how many english in ireland", "how many british live in ireland", "how many british people in ireland", "how many british died in ireland", "how many british in northern ireland", "how many british immigrants in ireland", "how many british citizens in ireland", "how many british soldiers died in ireland"],
        "ie|how many south africans in ireland": ["how many south africans in ireland", "how many south africans live in ireland", "how many south africans were deported in ireland", "irish population in south africa", "can a south african move to ireland"],
        "ie|how many canadians in ireland": ["how many canadians in ireland", "how many canadians live in northern ireland", "how many canadians claim irish ancestry", "how many canadians claim irish heritage", "how many canadians have irish ancestry", "how many canadians have irish heritage", "how many canadians are irish", "how many canadians of irish descent", "how many irelands fit in canada", "can canadian citizens live in ireland"],
        "ie|how many australians in ireland": ["how many australians in ireland", "how many aussies in ireland", "how many australians live in ireland", "how many aussies live in ireland", "how many australians have irish heritage", "how many australians are irish", "how many australians claim irish ancestry", "how many australians have irish descent", "how many irish in australia", "how many irelands fit in australia"],
        "ie|indians in ireland": ["indians in ireland", "indians in ireland reddit", "indians in ireland population", "indians in ireland facebook", "indians in ireland whatsapp group", "indians in ireland 2026", "indians in ireland racism", "indians in ireland percentage", "indians in ireland forum", "indians in ireland number"],
    },
}


def leggi_csv(b):
    return list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))


def numero(x):
    x = (x or "").strip().replace(",", "")
    return int(x) if x.isdigit() else None


def chiave_mese(s):
    a, m = s.split(" ", 1)
    return f"{a}-{MESI.index(m) + 1:02d}"


def main():
    nuovo = "--nuovo" in sys.argv
    oggi = date.today().isoformat()
    errori = []
    pag, _ = scarica(PAGINA, nuovo=True)
    pag = pag.decode("utf-8", "replace")
    agg = re.search(r"Last updated on:\s*(\d{1,2} \w+ \d{4})", re.sub(r"<[^>]+>", " ", pag))
    link = {k: html.unescape(m.group(0)) for k, pat in (("mensile", r"https://assets\.gov\.ie/[^\"' ]*PPSN_registrations_by_year_month_and_country\.csv"),
                                                         ("annuale", r"https://assets\.gov\.ie/[^\"' ]*PPSN_registrations_by_year_and_country\.csv"))
            for m in [re.search(pat, pag)] if m}
    if set(link) != {"mensile", "annuale"}:
        sys.exit(f"ERRORE: link ai CSV non trovati sulla pagina {PAGINA}")
    fonti = {}
    righe = {}
    for k, url in link.items():
        dati, meta = scarica(url, GREZZI / f"ppsn-{k}.csv", nuovo=nuovo)
        if meta.get("url") not in (None, url):
            dati, meta = scarica(url, GREZZI / f"ppsn-{k}.csv", nuovo=True)
        righe[k] = leggi_csv(dati)
        fonti[k] = {"url": url, "file": url.rsplit("/", 1)[1], "byte": len(dati), "sha256": hashlib.sha256(dati).hexdigest(),
                    "scaricato_il": meta.get("scaricato_il", oggi), "http": meta.get("http", 200), "last_modified": meta.get("last_modified", "")}
    att_m = ["ppsn_registration_year", "ppsn_registration_year_month", "country_label_stat", "unit", "value"]
    att_a = ["ppsn_registration_year", "region_label_stat", "country_label_stat", "unit", "value"]
    if list(righe["mensile"][0].keys()) != att_m:
        errori.append(f"intestazione del file mensile cambiata: {list(righe['mensile'][0].keys())}")
    if list(righe["annuale"][0].keys()) != att_a:
        errori.append(f"intestazione del file annuale cambiata: {list(righe['annuale'][0].keys())}")
    if errori:
        print("ERRORI:", *errori, sep="\n - ")
        sys.exit(1)
    # mensile
    mens = defaultdict(dict)
    for r in righe["mensile"]:
        mens[r["country_label_stat"]][chiave_mese(r["ppsn_registration_year_month"])] = numero(r["value"])
    mesi = sorted({m for v in mens.values() for m in v})
    a0, m0 = int(mesi[0][:4]), int(mesi[0][5:])
    attesi = []
    a, m = a0, m0
    while f"{a}-{m:02d}" <= mesi[-1]:
        attesi.append(f"{a}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    if mesi != attesi:
        errori.append("mesi non consecutivi nel file mensile")
    # annuale
    divise = []
    ann = defaultdict(dict)        # nazionalità -> anno -> numero (una sola riga per nazionalità e anno, tranne "Other")
    regione = defaultdict(set)
    totale_anni = defaultdict(int)   # somma di tutte le righe (anche le "Other" di ogni regione del mondo)
    for r in righe["annuale"]:
        v = numero(r["value"])
        if v is None:
            errori.append(f"valore annuo non numerico: {r}")
            continue
        totale_anni[r["ppsn_registration_year"]] += v
        # una nazionalità può stare in due regioni nello stesso anno (Regno Unito nel 2020, anno della Brexit: "European Union" e
        # "Europe excluding EU"): si sommano le righe e si annota la divisione
        if r["ppsn_registration_year"] in ann[r["country_label_stat"]] and r["country_label_stat"] in NAZIONALITA.values():
            divise.append(f"{r['country_label_stat']} {r['ppsn_registration_year']}")
        ann[r["country_label_stat"]][r["ppsn_registration_year"]] = ann[r["country_label_stat"]].get(r["ppsn_registration_year"], 0) + v
        regione[r["country_label_stat"]].add(r["region_label_stat"])
    anni = sorted(totale_anni)
    totale_anni = dict(totale_anni)
    # controlli
    for a in sorted({m[:4] for m in mesi}):
        s = sum(v for m, v in mens["All"].items() if m.startswith(a) and v is not None)
        if s != totale_anni.get(a):
            errori.append(f"{a}: somma dei mesi della riga All ({s}) diversa dalla somma annua di tutte le nazionalità ({totale_anni.get(a)})")
    naz = {}
    for c, nome in NAZIONALITA.items():
        if nome not in mens or nome not in ann:
            errori.append(f"nazionalità {nome} assente da uno dei due file")
            continue
        mm = {m: mens[nome].get(m) for m in mesi}
        if any(v is None for v in mm.values()):
            errori.append(f"{nome}: mesi non pubblicati {[m for m, v in mm.items() if v is None]}")
        for a in sorted({m[:4] for m in mesi}):
            s = sum(v or 0 for m, v in mm.items() if m.startswith(a))
            if s != ann[nome].get(a):
                errori.append(f"{nome} {a}: somma dei mesi {s} diversa dal totale annuo {ann[nome].get(a)}")
        naz[c] = {"nome": nome, "regione": sorted(regione.get(nome, []))[0] if regione.get(nome) else None, "anni": {a: ann[nome].get(a) for a in anni}, "mesi": mm}
    # pagina del servizio PPS (definizione usata nelle pagine)
    srv, srv_meta = scarica(SERVIZIO, nuovo=True)
    srv_t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", srv.decode("utf-8", "replace"))))
    for f in FRASI_SERVIZIO:
        if f not in srv_t:
            errori.append(f"frase non più presente nella pagina del servizio PPS: {f!r}")
    srv_agg = re.search(r"Last updated on:\s*(\d{1,2} \w+ \d{4})", srv_t)
    # scheda data.gov.ie: licenza
    sch, _ = scarica(API_SCHEDA, nuovo=True)
    sch = json.loads(sch)["result"]
    if sch.get("license_id") != "CC-BY-4.0":
        errori.append(f"licenza della scheda data.gov.ie cambiata: {sch.get('license_id')}")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:60]:
            print(" -", x)
        sys.exit(1)
    from datetime import datetime
    def iso(s):
        return datetime.strptime(s, "%d %B %Y").date().isoformat() if s else None
    contenuto = {"anni": anni, "mesi": mesi, "nazionalita": naz,
                 "tutte": {"anni": totale_anni, "mesi": {m: mens["All"].get(m) for m in mesi}}, "righe_sommate": divise}
    uscita = {"_nota": "Generato da raccolta/ppsn.py: non modificare a mano. Numeri PPS (PPSN) assegnati per nazionalità, per anno (dal 2001) "
                       "e per mese (dal gennaio 2023). Fonte: Department of Social Protection, gov.ie / data.gov.ie (CC BY 4.0).",
              "generato_il": oggi, "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "fonti": {"pagina": {"url": PAGINA, "titolo": "Annual Allocations: PPS Numbers", "aggiornata": iso(agg.group(1)) if agg else None, "letta_il": oggi},
                        "scheda": {"url": SCHEDA, "titolo": sch.get("title"), "licenza": LICENZA, "licenza_url": LICENZA_URL,
                                   "editore": (sch.get("organization") or {}).get("title"), "modificata": (sch.get("metadata_modified") or "")[:10]},
                        "servizio": {"url": SERVIZIO, "titolo": "Get a Personal Public Service (PPS) Number", "aggiornata": iso(srv_agg.group(1)) if srv_agg else None,
                                     "letta_il": oggi, "http": srv_meta.get("http"), "frasi": FRASI_SERVIZIO},
                        **fonti},
              "domanda": DOMANDA, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(naz)} nazionalità, anni {anni[0]}-{anni[-1]}, mesi {mesi[0]} → {mesi[-1]}; pagina gov.ie aggiornata il "
          f"{uscita['fonti']['pagina']['aggiornata']}; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
