"""Domanda USA delle pagine «LLC by State», misurata con api.seodata.dev /v1/keyword (volume medio mensile Google Ads).

Uso (dalla radice del repository): python3 -I naics/raccolta/volumi_llc.py [--dry]  -> naics/dati/volumi-llc-2026-11-14.json
La chiave sta in /root/.config/seodata/key e viene letta SOLO dentro la shell di curl ($(cat ...)): non passa da Python, non viene
stampata né scritta. Le frasi già nel file non si ripetono. volume null = frase non nel database dello strumento (404).
Per rifare la misura: file nuovo con la data (cambiare OUT qui e FILE_VOLUMI_LLC in genera.py e verifica.py).
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "dati" / "volumi-llc-2026-11-14.json"
STATI = ["texas", "florida", "california", "new york", "north carolina", "michigan", "colorado", "arizona"]
MODELLI = ["{s} llc", "how to start an llc in {s}", "{s} llc cost", "how much does an llc cost in {s}", "{s} llc filing fee",
           "{s} registered agent", "{s} annual report", "{s} llc annual fee", "how long does it take to get an llc in {s}"]
TESTE = ["llc cost by state", "llc fees by state", "llc filing fees by state", "llc annual fees by state", "llc by state",
         "naics code for llc", "do i need a naics code for my llc", "what is a registered agent",
         "texas franchise tax", "texas llc franchise tax", "california llc fee", "california llc tax", "california statement of information",
         "florida llc annual report", "new york llc publication requirement", "new york biennial statement", "nc llc annual report",
         "michigan llc annual statement", "colorado periodic report", "arizona llc publication requirement", "arizona statutory agent"]


def frasi():
    q = []
    for s in STATI:
        for m in MODELLI:
            q.append(m.format(s=s))
    return q + [t for t in TESTE if t not in q]


def main():
    q = frasi()
    print(len(q), "frasi")
    if "--dry" in sys.argv:
        return
    dati = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {
        "_nota": "Volumi medi mensili di ricerca su Google negli Stati Uniti (Google Ads) letti con api.seodata.dev per le pagine "
                 "«LLC by State». volume null = la frase non è nel database dello strumento (risposta 404). «simili» = frasi vicine "
                 "restituite dallo strumento con il loro volume (misurate anch'esse: valgono per titoli e FAQ).",
        "misurato_il": "2026-11-14", "strumento": "api.seodata.dev, country=us", "ricerche_usate": 0, "frasi": {}}
    for x in q:
        if x in dati["frasi"]:
            continue
        url = "https://api.seodata.dev/v1/keyword?q=" + urllib.parse.quote(x) + "&country=us"
        r = subprocess.run(["bash", "-c", 'curl -s -m 50 -w "\\n%{http_code}" "$U" -H "Authorization: Bearer $(cat /root/.config/seodata/key)"'],
                           env={**os.environ, "U": url}, capture_output=True, text=True, timeout=70)
        corpo, _, codice = r.stdout.rpartition("\n")
        try:
            d = json.loads(corpo)
        except ValueError:
            d = {}
        if codice == "200" and "volume" in d:
            dati["frasi"][x] = {"volume": d.get("volume"), "cpc_usd": d.get("cpc"), "dato_del": (d.get("cached_at") or "2026-11-14")[:10],
                                "simili": {s["keyword"]: s["volume"] for s in d.get("similar", []) if s.get("volume") is not None}}
        elif codice == "404":
            dati["frasi"][x] = {"volume": None, "cpc_usd": None, "dato_del": "", "simili": {}}
        else:
            print("fermo:", x, codice, sorted(d.keys())[:6])
            break
        dati["ricerche_usate"] += 1
        OUT.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        time.sleep(0.4)
    print("ricerche usate in tutto:", dati["ricerche_usate"], "· frasi con volume:", sum(1 for v in dati["frasi"].values() if v["volume"]))


if __name__ == "__main__":
    main()
