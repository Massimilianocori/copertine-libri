"""Ricerche vere (autocompletamento Google, gl=au, hl=en) per le domande frequenti del sito.

Uso (dalla radice del repository):
    python3 paytax/raccolta/domanda.py      # rilegge tutte le radici e scrive paytax/dati/domanda.json

Ogni FAQ del sito cita in dati/faq.json la ricerca da cui nasce (campo "ricerca"): verifica.py controlla che quella
ricerca sia nel file salvato qui. Nessun dato personale: si mandano solo le parole di ricerca.
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "domanda.json"
URL = "https://suggestqueries.google.com/complete/search?client=firefox&gl=au&hl=en&q="

RADICI = [
    "payroll tax", "payroll tax calculator", "payroll tax threshold", "payroll tax rates", "payroll tax rate",
    "how is payroll tax calculated", "payroll tax grouping", "payroll tax interstate", "payroll tax multiple states",
    "payroll tax due dates", "payroll tax annual reconciliation", "payroll tax registration", "payroll tax regional",
    "payroll tax exemption", "payroll tax contractors", "payroll tax 2026", "payroll tax 2027", "what is payroll tax",
    "do i have to pay payroll tax", "when do you pay payroll tax", "payroll tax threshold 2026",
    "payroll tax nsw", "payroll tax vic", "payroll tax victoria", "payroll tax qld", "payroll tax queensland",
    "payroll tax wa", "payroll tax sa", "payroll tax south australia", "payroll tax tasmania", "payroll tax tas",
    "payroll tax act", "payroll tax canberra", "payroll tax nt", "payroll tax northern territory",
    "payroll tax threshold nsw", "payroll tax threshold vic", "payroll tax threshold qld", "payroll tax threshold wa",
    "payroll tax threshold sa", "payroll tax threshold tas", "payroll tax threshold act", "payroll tax threshold nt",
    "payroll tax rate nsw", "payroll tax rate vic", "payroll tax rate qld", "payroll tax rate wa", "payroll tax rate act",
    "mental health levy qld", "mental health and wellbeing surcharge", "payroll tax surcharge victoria",
    "payday super", "payday super rules", "payday super due date", "payday super penalties", "payday super clearing house",
    "payroll tax threshold history", "payroll tax monthly threshold", "payroll tax registration nsw",
    "payroll tax registration qld", "payroll tax registration vic", "payroll tax registration wa",
    "is payroll tax", "does payroll tax", "can payroll tax", "which state has the lowest payroll tax",
]


def leggi(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        dati = json.loads(r.read().decode("utf-8", errors="replace"))
    return dati[1] if isinstance(dati, list) and len(dati) > 1 else []


def main():
    out = {"fonte": URL + "<radice>", "letto_il": date.today().isoformat(), "note": "autocompletamento Google, gl=au hl=en", "radici": {}}
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
