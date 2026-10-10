"""Scarica i cambi di riferimento della BCE e li salva in visaincome/dati/cambi.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/cambi.py              # scarica dalla BCE
    python3 visaincome/raccolta/cambi.py FILE.xml     # legge un file XML già scaricato (prove)

Fonte: European Central Bank, euro foreign exchange reference rates (eurofxref-daily.xml),
pubblicati ogni giorno lavorativo verso le 16:00 ora dell'Europa centrale.
Le pagine del sito leggono dati/cambi.json da raw.githubusercontent.com; se il file non arriva
usano i cambi scritti dentro la pagina al momento della generazione.

Se il download o il controllo falliscono, il file esistente NON viene toccato (esce con codice 1).
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

URL_BCE = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
import os
# CAMBI_FILE permette di scrivere altrove: il workflow automatico (che salva solo italystrikes/dati) lo usa
# per tenere aggiornata la copia italystrikes/dati/cambi-bce.json letta dalle pagine.
FILE = Path(os.environ["CAMBI_FILE"]) if os.environ.get("CAMBI_FILE") else Path(__file__).resolve().parent.parent / "dati" / "cambi.json"
NS = "{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}"
OBBLIGATORIE = ("USD", "GBP", "CAD", "AUD", "PHP", "INR")  # senza queste il file non si aggiorna


def scarica():
    req = urllib.request.Request(URL_BCE, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def leggi(xml_bytes):
    radice = ET.fromstring(xml_bytes)
    giorno = None
    tassi = {}
    for cubo in radice.iter(NS + "Cube"):
        if cubo.get("time"):
            giorno = cubo.get("time")
        if cubo.get("currency") and cubo.get("rate"):
            tassi[cubo.get("currency")] = float(cubo.get("rate"))
    if not giorno or len(giorno) != 10:
        raise ValueError("data dei cambi mancante")
    mancanti = [v for v in OBBLIGATORIE if not tassi.get(v)]
    if mancanti:
        raise ValueError("valute mancanti: " + ", ".join(mancanti))
    if any(not (0 < t < 1e7) for t in tassi.values()):
        raise ValueError("cambio fuori scala")
    return giorno, tassi


def main():
    try:
        dati = Path(sys.argv[1]).read_bytes() if len(sys.argv) > 1 else scarica()
        giorno, tassi = leggi(dati)
    except Exception as e:  # noqa: BLE001 - qualsiasi errore: non toccare il file
        print(f"Cambi BCE non aggiornati: {e}")
        sys.exit(1)
    vecchio = {}
    if FILE.exists():
        try:
            vecchio = json.loads(FILE.read_text(encoding="utf-8"))
        except ValueError:
            vecchio = {}
    if vecchio.get("data") == giorno and vecchio.get("tassi") == tassi:
        print(f"Cambi BCE già aggiornati al {giorno}")
        return
    out = {
        "fonte": "European Central Bank, euro foreign exchange reference rates",
        "url": URL_BCE,
        "data": giorno,
        "scaricato_il": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "base": "EUR",
        "tassi": dict(sorted(tassi.items())),
    }
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Cambi BCE del {giorno}: {len(tassi)} valute salvate in {FILE}")


if __name__ == "__main__":
    main()
