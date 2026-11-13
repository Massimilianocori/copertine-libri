"""Volumi di ricerca (Google Ads, USA) per scegliere cause e Stati: al massimo 15 richieste SENZA chiave a api.seodata.dev.

Uso (dalla radice del repository): python3 limits/raccolta/volumi.py   -> limits/dati/volumi.json
Non usa la chiave del conto (non va mai letta, stampata o scritta qui). Ogni risposta porta anche dieci frasi simili.
La prima frase ("medical malpractice statute of limitations") è stata letta a mano il 13/11/2026 con la stessa richiesta
senza chiave: è già nel file e non si ripete, così il totale resta 15.
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "dati" / "volumi.json"
URL = "https://api.seodata.dev/v1/keyword?country=us&q="
FRASI = [
    "statute of limitations personal injury texas", "statute of limitations florida personal injury",
    "statute of limitations on debt in texas", "statute of limitations on debt in florida",
    "statute of limitations breach of contract texas", "wrongful death statute of limitations texas",
    "statute of limitations property damage", "statute of limitations calculator",
    "statute of limitations ohio", "statute of limitations michigan", "statute of limitations virginia",
    "statute of limitations north carolina", "statute of limitations arizona", "statute of limitations minnesota",
]


def main():
    dati = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {"frasi": {}}
    fatte = 0
    for q in FRASI:
        if q in dati["frasi"] or fatte >= 14:
            continue
        req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0 (research script)"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode("utf-8"))
            dati["frasi"][q] = {"volume": d.get("volume"), "cpc": d.get("cpc"), "simili": [(s["keyword"], s["volume"], s["cpc"]) for s in d.get("similar", [])]}
        except Exception as e:  # noqa: BLE001
            dati["frasi"][q] = {"errore": str(e)[:100]}
        fatte += 1
        time.sleep(1.5)
    dati["letto_il"] = date.today().isoformat()
    dati["fonte"] = "api.seodata.dev senza chiave (volume medio mensile Google Ads, USA)"
    FILE.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{fatte} richieste; {len(dati['frasi'])} frasi in {FILE}")


if __name__ == "__main__":
    main()
