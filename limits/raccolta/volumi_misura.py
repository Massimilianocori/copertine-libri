"""Domanda USA misurata il 13/11/2026 con api.seodata.dev /v1/keyword (conto con chiave, volume medio mensile Google Ads).

Uso (dalla radice del repository): python3 limits/raccolta/volumi_misura.py [--dry]  -> limits/dati/volumi-2026-11-13.json
La chiave sta in /root/.config/seodata/key e viene letta SOLO dentro la shell di curl ($(cat ...)): non passa da Python, non viene
stampata né scritta. Le frasi già nel file non si ripetono. 317 richieste il 13/11/2026 (181 con volume, 136 "errore": 404 = frase non
nel database). Per ogni frase il servizio restituisce anche dieci frasi simili con il loro volume (campo "simili").
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "dati" / "volumi-2026-11-13.json"
COPERTI = ["texas", "florida", "ohio", "washington", "virginia", "north carolina", "michigan", "arizona", "massachusetts", "minnesota"]
SCOPERTI = ["california", "new york", "georgia", "pennsylvania", "illinois", "new jersey"]
CAUSE = ["personal injury", "medical malpractice", "wrongful death", "debt", "breach of contract", "property damage"]


def frasi():
    q = []

    def add(x):
        if x not in q:
            q.append(x)
    for x in ["statute of limitations on debt", "personal injury statute of limitations", "medical malpractice statute of limitations",
              "wrongful death statute of limitations", "breach of contract statute of limitations", "property damage statute of limitations",
              "statute of limitations by state", "statute of limitations calculator", "statute of limitations on credit card debt",
              "car accident statute of limitations", "defamation statute of limitations", "fraud statute of limitations",
              "wrongful termination statute of limitations", "statute of limitations on debt by state", "statute of limitations civil cases"]:
        add(x)
    for s in COPERTI:
        for c in CAUSE:
            add(f"statute of limitations {c} {s}")
            add(f"{s} statute of limitations {c}")
            add(f"how long do you have to sue for {c} in {s}")
        add(f"{s} debt statute of limitations")
        add(f"{s} statute of limitations")
        add(f"lemon law {s}")
        add(f"statute of limitations credit card debt {s}")
        add(f"car accident statute of limitations {s}")
    for s in SCOPERTI:
        for c in CAUSE:
            add(f"statute of limitations {c} {s}")
        add(f"{s} debt statute of limitations")
        add(f"{s} statute of limitations")
        add(f"statute of limitations credit card debt {s}")
        add(f"car accident statute of limitations {s}")
    for s in ["texas", "florida", "california", "new york"]:
        for c in ["defamation", "fraud", "wrongful termination"]:
            add(f"statute of limitations {c} {s}")
    return q


def main():
    q = frasi()
    print(len(q), "frasi")
    if "--dry" in sys.argv:
        return
    dati = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {
        "fonte": "api.seodata.dev /v1/keyword (volume medio mensile Google Ads)", "misurato_il": "2026-11-13", "paese": "us", "frasi": {}}
    n = 0
    for x in q:
        if x in dati["frasi"]:
            continue
        url = "https://api.seodata.dev/v1/keyword?q=" + urllib.parse.quote(x) + "&country=us"
        r = subprocess.run(["bash", "-c", 'curl -s -w "\\n%{http_code}" "$U" -H "Authorization: Bearer $(cat /root/.config/seodata/key)"'],
                           env={**os.environ, "U": url}, capture_output=True, text=True, timeout=60)
        corpo, _, codice = r.stdout.rpartition("\n")
        n += 1
        try:
            d = json.loads(corpo)
        except ValueError:
            d = {}
        if codice == "200" and "volume" in d:
            dati["frasi"][x] = {"volume": d.get("volume"), "cpc": d.get("cpc"), "competition": d.get("competition"),
                                "simili": [[s["keyword"], s["volume"], s.get("cpc")] for s in d.get("similar", [])]}
        else:
            dati["frasi"][x] = {"errore": int(codice) if codice.isdigit() else codice}
        time.sleep(0.3)
    dati["richieste"] = dati.get("richieste", 0) + n
    OUT.write_text(json.dumps(dati, ensure_ascii=False, indent=1), encoding="utf-8")
    print("richieste fatte:", n)


if __name__ == "__main__":
    main()
