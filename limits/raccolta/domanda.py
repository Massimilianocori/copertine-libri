"""Ricerche vere (autocompletamento Google, gl=us, hl=en) per le domande frequenti del sito Statute of Limitations by State.

Uso (dalla radice del repository):
    python3 limits/raccolta/domanda.py      # rilegge tutte le radici e scrive limits/dati/domanda.json

Ogni FAQ in dati/faq.json cita la ricerca da cui nasce (campo "ricerca"): verifica.py controlla che quella ricerca sia
tra i suggerimenti salvati qui (o sia una radice). Nessun dato personale: si mandano solo le parole di ricerca.
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "domanda.json"
URL = "https://suggestqueries.google.com/complete/search?client=firefox&gl=us&hl=en&q="

RADICI = [
    "statute of limitations", "statute of limitations calculator", "statute of limitations by state",
    "statute of limitations personal injury", "statute of limitations car accident", "how long do you have to sue",
    "how long do you have to sue after a car accident", "how long do i have to file a lawsuit",
    "statute of limitations medical malpractice", "medical malpractice statute of limitations discovery rule",
    "wrongful death statute of limitations", "statute of limitations on debt", "can a debt collector sue after",
    "does a payment restart the statute of limitations", "time barred debt", "statute of limitations credit card debt",
    "statute of limitations breach of contract", "statute of limitations oral contract", "statute of limitations written contract",
    "statute of limitations property damage", "statute of limitations for minors", "tolling statute of limitations",
    "statute of repose", "statute of limitations texas", "statute of limitations florida", "statute of limitations ohio",
    "statute of limitations washington state", "statute of limitations virginia", "statute of limitations north carolina",
    "statute of limitations michigan", "statute of limitations arizona", "statute of limitations massachusetts",
    "statute of limitations minnesota", "florida statute of limitations negligence", "ohio statute of limitations medical malpractice",
    "texas statute of limitations debt", "minnesota statute of limitations personal injury", "ohio statute of limitations breach of contract",
]


def leggi(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        dati = json.loads(r.read().decode("utf-8", errors="replace"))
    return dati[1] if isinstance(dati, list) and len(dati) > 1 else []


def main():
    out = {"fonte": URL + "<radice>", "letto_il": date.today().isoformat(), "note": "autocompletamento Google, gl=us hl=en", "radici": {}}
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
