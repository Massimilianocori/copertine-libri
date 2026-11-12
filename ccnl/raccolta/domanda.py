"""Ricerche vere (autocompletamento Google, hl=it gl=it) per le domande frequenti del sito.

Uso (dalla radice del repository):
    python3 ccnl/raccolta/domanda.py      # rilegge tutte le radici e scrive ccnl/dati/domanda.json

Ogni FAQ in dati/faq.json cita la ricerca da cui nasce (campo "ricerca"): verifica.py controlla che quella ricerca
sia fra i suggerimenti salvati qui. Nessun dato personale: si mandano solo le parole di ricerca.
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "domanda.json"
URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl=it&gl=it&q="

RADICI = [
    "ccnl commercio", "ccnl commercio 4 livello", "ccnl commercio 4 livello 30 ore", "ccnl commercio 5 livello",
    "ccnl commercio 3 livello", "ccnl commercio 6 livello", "ccnl commercio 2 livello", "ccnl commercio 1 livello",
    "ccnl commercio quadro", "ccnl commercio 7 livello", "ccnl commercio paga oraria", "ccnl commercio part time",
    "ccnl commercio 2026", "ccnl commercio tabelle", "ccnl commercio aumenti", "ccnl commercio quattordicesima",
    "ccnl terziario", "ccnl terziario confcommercio", "paga oraria ccnl commercio", "stipendio 4 livello commercio",
    "stipendio 5 livello commercio", "ccnl commercio divisore",
    "ccnl metalmeccanici", "ccnl metalmeccanici 2026", "ccnl metalmeccanici livello", "ccnl metalmeccanici c3",
    "ccnl metalmeccanici d1", "ccnl metalmeccanici d2", "ccnl metalmeccanici c2", "ccnl metalmeccanici c1",
    "ccnl metalmeccanici b1", "ccnl metalmeccanici b2", "ccnl metalmeccanici b3", "ccnl metalmeccanici a1",
    "ccnl metalmeccanici paga oraria", "ccnl metalmeccanici minimi", "ccnl metalmeccanici aumenti",
    "stipendio metalmeccanico", "paga oraria metalmeccanico", "metalmeccanico c3",
    "ccnl multiservizi", "ccnl multiservizi 2026", "ccnl multiservizi 2 livello", "ccnl multiservizi 3 livello",
    "ccnl multiservizi livello", "ccnl multiservizi paga oraria", "ccnl pulizie", "ccnl pulizie paga oraria",
    "ccnl pulizie 2 livello", "paga oraria pulizie", "ccnl multiservizi aumenti", "stipendio addetto pulizie",
    "ccnl logistica", "ccnl logistica trasporto merci", "ccnl logistica livello", "ccnl logistica 5 livello",
    "ccnl logistica 6 livello", "ccnl logistica 4 livello", "ccnl logistica paga oraria", "ccnl logistica 2026",
    "ccnl trasporto merci", "ccnl trasporto merci livello", "stipendio autista c3", "ccnl logistica c3",
    "ccnl logistica 3 livello", "ccnl logistica aumenti", "stipendio magazziniere",
    "paga oraria colf", "paga oraria colf 2026", "stipendio colf", "stipendio badante", "stipendio badante convivente",
    "stipendio badante 2026", "badante convivente", "colf livello", "ccnl colf", "ccnl colf 2026",
    "ccnl lavoro domestico", "ccnl lavoro domestico 2026", "minimi colf 2026", "tabella colf 2026",
    "paga oraria badante", "badante livello cs", "badante livello ds", "colf livello b", "colf livello a",
    "tredicesima colf", "vitto e alloggio badante", "badante notturna",
    "paga oraria ccnl", "minimi tabellari", "minimi tabellari 2026", "tabelle retributive ccnl", "stipendio livello",
    "divisore orario", "divisore 168", "divisore 173", "come si calcola la paga oraria",
    "paga oraria lorda", "stipendio part time 20 ore", "stipendio part time 24 ore", "stipendio part time 30 ore",
    "ral", "ral 4 livello commercio", "ral metalmeccanico",
]


def leggi(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        dati = json.loads(r.read().decode("utf-8", errors="replace"))
    return dati[1] if isinstance(dati, list) and len(dati) > 1 else []


def main():
    out = {"fonte": URL + "<radice>", "letto_il": date.today().isoformat(), "note": "autocompletamento Google, hl=it gl=it",
           "radici": {}}
    for q in RADICI:
        try:
            out["radici"][q] = leggi(q)
        except Exception as e:  # noqa: BLE001
            out["radici"][q] = {"errore": str(e)[:120]}
        time.sleep(0.6)
    FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n = sum(len(v) for v in out["radici"].values() if isinstance(v, list))
    print(f"{len(RADICI)} radici, {n} suggerimenti -> {FILE}")


if __name__ == "__main__":
    main()
