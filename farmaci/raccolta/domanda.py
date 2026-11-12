"""Ricerche vere (autocompletamento Google, hl=it gl=it): decidono quali pagine si indicizzano e da dove nascono le FAQ.

Uso (dalla radice del repository):
    python3 -I farmaci/raccolta/domanda.py          # legge le radici e i nomi che mancano, riprende da dove si era fermato
    python3 -I farmaci/raccolta/domanda.py --tutto  # rilegge tutto (ogni 3 mesi)

Per ogni principio attivo della lista di trasparenza e per ogni nome commerciale di fantasia (prima parola del nome)
si manda una sola richiesta, «<nome> », e si salvano i suggerimenti. Le radici generali servono per le FAQ.
Nessun dato personale: si mandano solo nomi di farmaci e parole di ricerca. Pausa di 0,5 secondi tra le richieste;
alla prima risposta diversa da 200 lo script si ferma e salva (niente tentativi di aggirare i limiti).
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "domanda.json"
URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl=it&gl=it&q="

RADICI = [
    "farmaco equivalente", "farmaco equivalente di", "farmaci equivalenti", "farmaco generico", "generico del",
    "farmaco equivalente cosa significa", "farmaco equivalente differenza", "farmaci equivalenti differenza prezzo",
    "differenza tra farmaco generico e originale", "differenza prezzo farmaco", "differenza di prezzo farmaco equivalente",
    "prezzo di riferimento farmaci", "prezzo di riferimento", "lista di trasparenza", "lista di trasparenza aifa",
    "farmaci carenti", "farmaci carenti aifa", "elenco farmaci carenti", "farmaci mancanti", "farmaci mancanti in farmacia",
    "farmaco carente", "farmaco carente cosa fare", "farmaco non si trova", "non si trova in farmacia", "farmaco introvabile",
    "farmaco mancante", "farmaco esaurito", "carenza farmaci", "carenza farmaci 2026", "farmaco sostitutivo",
    "farmaco di marca", "farmaco di marca o generico", "pagare la differenza farmaco", "differenza a carico del paziente",
    "il farmacista può sostituire", "sostituzione farmaco farmacista", "non sostituibile ricetta", "ticket farmaci",
    "farmaco originale", "farmaci generici sono uguali", "farmaco equivalente è uguale", "equivalente di",
]

INTERESSE = re.compile(r"generic|equivalent|alternativ|sostitut|prezz|cost[oa]|mutuabil|non si trova|carenz|carent|mancant|introvabil|"
                       r"esaurit|ritirat|differenza|simile|uguale|al posto", re.I)


def leggi(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status}")
        dati = json.loads(r.read().decode("utf-8", errors="replace"))
    return dati[1] if isinstance(dati, list) and len(dati) > 1 else []


def nomi_da_cercare():
    T = json.loads((RADICE / "dati" / "trasparenza.json").read_text(encoding="utf-8"))["righe"]
    import importlib.util
    spec = importlib.util.spec_from_file_location("nomi", RADICE / "nomi.py")
    nomi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nomi)
    pa = sorted({nomi.pa_ricerca(r["pa"]) for r in T})
    fant = sorted({nomi.marchio(r["farmaco"]) for r in T if nomi.di_fantasia(r["farmaco"], r["pa"])})
    return pa, fant


def main():
    tutto = "--tutto" in sys.argv
    old = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() and not tutto else {}
    out = {"fonte": URL + "<radice>", "note": "autocompletamento Google, hl=it gl=it; per i nomi si cerca «<nome> »",
           "letto_il": old.get("letto_il", date.today().isoformat()), "radici": old.get("radici", {}), "nomi": old.get("nomi", {})}
    pa, fant = nomi_da_cercare()
    coda = [("radici", q, q) for q in RADICI] + [("nomi", n, n + " ") for n in pa + fant]
    fatte = 0
    try:
        for sez, chiave, q in coda:
            if chiave in out[sez]:
                continue
            out[sez][chiave] = leggi(q)
            fatte += 1
            time.sleep(0.5)
            if fatte % 100 == 0:
                print(f"  {fatte} richieste", flush=True)
                FILE.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"FERMATO dopo {fatte} richieste: {e}", file=sys.stderr)
    if fatte:
        out["letto_il"] = date.today().isoformat()
    FILE.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    con = sum(1 for k, v in out["nomi"].items() if any(INTERESSE.search(s) for s in v))
    print(f"richieste nuove {fatte}; nomi letti {len(out['nomi'])} su {len(pa) + len(fant)}; con ricerche su equivalenti/prezzo/carenza: {con}")


if __name__ == "__main__":
    main()
