"""Prezzo dell'elettricità per le famiglie (Eurostat, nrg_pc_204) per Italia, Spagna e Francia. Scrive dati/prezzi.json.

Uso (dalla radice del repository):
    python3 solarebalcone/raccolta/prezzi.py

Serie: "Electricity prices for household consumers - bi-annual data (from 2007 onwards)", fascia di consumo DC
(2.500-4.999 kWh l'anno, la fascia di riferimento di Eurostat per le famiglie), tutte le tasse e le imposte comprese
(tax=I_TAX), euro per kWh. Si prende l'ultimo semestre pubblicato. Riuso: "authorised provided the source is
acknowledged" (avviso sul copyright di Eurostat, letto l'8/11/2026). Solo libreria standard.
Germania (DE) già letta per quando la versione tedesca sarà accesa.
"""
import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
PAESI = ["IT", "ES", "FR", "DE"]
URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204?format=JSON&lang=EN"
       + "".join(f"&geo={p}" for p in PAESI) + "&nrg_cons=KWH2500-4999&tax=I_TAX&currency=EUR&unit=KWH&lastTimePeriod=3")
PAGINA = "https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204/default/table"


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "solarebalcone/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        stato, corpo = r.status, r.read()
    d = json.loads(corpo)
    geo = d["dimension"]["geo"]["category"]["index"]
    tempi = d["dimension"]["time"]["category"]["index"]
    n_t = d["size"][-1]
    valori = {}
    for g, gi in geo.items():
        serie = {t: d["value"].get(str(gi * n_t + ti)) for t, ti in tempi.items()}
        validi = {t: v for t, v in serie.items() if v is not None}
        ultimo = max(validi)
        valori[g] = {"eur_kwh": validi[ultimo], "periodo": ultimo, "serie": serie}
    out = {"_nota": ("Eurostat nrg_pc_204: prezzo dell'elettricità per le famiglie, fascia DC 2.500-4.999 kWh/anno, tutte le tasse "
                     "comprese, EUR/kWh, ultimo semestre pubblicato. Media nazionale: la bolletta di ciascuno può essere diversa."),
           "url": URL, "pagina": PAGINA, "http": stato, "sha256": hashlib.sha256(corpo).hexdigest(),
           "aggiornato_eurostat": d.get("updated"), "letto_il": date.today().isoformat(), "paesi": valori}
    dest = RADICE / "dati" / "prezzi.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for g, v in valori.items():
        print(f"{g}: {v['eur_kwh']} €/kWh ({v['periodo']})")
    print(f"Scritto {dest}.")


if __name__ == "__main__":
    main()
