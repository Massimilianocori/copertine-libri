"""Scarica la previsione ufficiale della marea a Venezia (ICPSM, Comune di Venezia, open data CC BY) in dati/maree.json.

Fonte: https://dati.venezia.it/sites/default/files/dataset/opendata/previsione.json
(scheda: http://dati.venezia.it/?q=content/cpsm-dati-meteomarini-laguna-e-litorale-veneziano, "Licenza: CC-BY").
Attenzione: senza parametro anti-cache il server può restituire una copia vecchia di settimane: si aggiunge ?t=<ora>.
Se la fonte non risponde, o la previsione scaricata è più vecchia di quella salvata, il file non viene toccato.
Uso: python3 italystrikes/raccolta/maree.py (lo chiama anche raccogli.py, senza fermarsi se fallisce).
"""
import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RADICE = Path(__file__).resolve().parent.parent
FILE = RADICE / "dati" / "maree.json"
URL = "https://dati.venezia.it/sites/default/files/dataset/opendata/previsione.json"
ROMA = ZoneInfo("Europe/Rome")


def scarica():
    req = urllib.request.Request(f"{URL}?t={int(time.time())}", headers={"User-Agent": "Mozilla/5.0 (italy-strikes-today)"})
    with urllib.request.urlopen(req, timeout=40) as r:
        dati = json.loads(r.read().decode("utf-8"))
    estremali = []
    for x in dati:
        t = datetime.strptime(x["DATA_ESTREMALE"], "%Y-%m-%d %H:%M:%S")
        estremali.append({"t": t.strftime("%Y-%m-%d %H:%M"), "tipo": x["TIPO_ESTREMALE"], "cm": round(float(x["VALORE"]))})
    if not estremali:
        raise ValueError("previsione vuota")
    emessa = max(datetime.strptime(x["DATA_PREVISIONE"], "%Y-%m-%d %H:%M:%S") for x in dati).strftime("%Y-%m-%d %H:%M")
    estremali.sort(key=lambda e: e["t"])
    return {"letto_il": datetime.now(ROMA).strftime("%Y-%m-%d %H:%M"), "emessa": emessa, "fonte": URL, "estremali": estremali}


def main():
    nuovo = scarica()
    if FILE.exists():
        vecchio = json.loads(FILE.read_text(encoding="utf-8"))
        if vecchio.get("emessa", "") > nuovo["emessa"]:
            print(f"Maree: la fonte ha dato una previsione più vecchia ({nuovo['emessa']}) di quella salvata ({vecchio['emessa']}): non tocco nulla.")
            return
        if vecchio.get("emessa") == nuovo["emessa"] and vecchio.get("estremali") == nuovo["estremali"]:
            print(f"Maree: previsione invariata (emessa {nuovo['emessa']}).")
            return
    FILE.write_text(json.dumps(nuovo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Maree: previsione emessa {nuovo['emessa']}, {len(nuovo['estremali'])} estremali, massimo {max(e['cm'] for e in nuovo['estremali'] if e['tipo'] == 'max')} cm.")


if __name__ == "__main__":
    main()
