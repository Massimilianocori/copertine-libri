"""Ricerche vere (autocompletamento Google, gl=gb, hl=en) per le domande frequenti del sito Heat Pump Grants UK.

Uso (dalla radice del repository):
    python3 heatpumps/raccolta/domanda.py      # rilegge tutte le radici e scrive heatpumps/dati/domanda.json

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
URL = "https://suggestqueries.google.com/complete/search?client=firefox&gl=gb&hl=en&q="

RADICI = [
    "boiler upgrade scheme", "boiler upgrade scheme eligibility", "boiler upgrade scheme 9000", "boiler upgrade scheme end date",
    "boiler upgrade scheme air to air", "boiler upgrade scheme how to apply", "boiler upgrade scheme epc",
    "boiler upgrade scheme second home", "boiler upgrade scheme landlord", "boiler upgrade scheme new build",
    "boiler upgrade scheme wales", "boiler upgrade scheme scotland", "boiler upgrade scheme statistics",
    "heat pump grant", "heat pump grant 9000", "heat pump grant 7500", "heat pump grant uk", "heat pump grant eligibility",
    "air source heat pump grant", "air to air heat pump grant", "ground source heat pump grant", "government grants for heat pumps",
    "is the 7500 heat pump grant", "can i get a heat pump grant", "do i qualify for", "how much is the heat pump grant",
    "heat pump cost", "heat pump cost after grant", "air source heat pump cost", "average cost of heat pump installation uk",
    "ground source heat pump cost", "how much does a heat pump cost", "heat pump cost uk",
    "heat pump installers", "mcs certified installer", "how many heat pumps installed in",
    "heat pump grant cornwall", "heat pump grant devon", "heat pump grant kent", "heat pump cost london",
    "solar panels cost", "cost of solar panels uk", "solar panel cost per kw uk", "how much do solar panels cost uk",
    "solar panels grant", "solar panels leeds", "solar panels bristol", "solar panels manchester", "solar panels scotland",
    "vat on heat pumps", "vat on solar panels",
]


def leggi(q):
    req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        dati = json.loads(r.read().decode("utf-8", errors="replace"))
    return dati[1] if isinstance(dati, list) and len(dati) > 1 else []


def main():
    out = {"fonte": URL + "<radice>", "letto_il": date.today().isoformat(), "note": "autocompletamento Google, gl=gb hl=en", "radici": {}}
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
