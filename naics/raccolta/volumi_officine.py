"""Domanda USA della sezione «Auto repair shop rules by state», misurata con api.seodata.dev /v1/keyword (volume medio mensile Google Ads).

Uso (dalla radice del repository): python3 -I naics/raccolta/volumi_officine.py [--dry]  -> naics/dati/volumi-officine-2026-11-19.json
La chiave sta in /root/.config/seodata/key e viene letta SOLO dentro la shell di curl ($(cat ...)): non passa da Python, non viene
stampata né scritta. Le frasi già nel file non si ripetono. volume null = frase non nel database dello strumento (404).
Per rifare la misura: file nuovo con la data (cambiare OUT qui e FILE_VOLUMI_OFFICINE in genera.py e verifica.py).
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "dati" / "volumi-officine-2026-11-19.json"
STATI = ["florida", "washington state", "minnesota", "california", "michigan", "new york"]
MODELLI = ["{s} auto repair laws", "auto repair laws in {s}", "{s} mechanic laws", "{s} auto repair estimate law", "{s} car repair laws",
           "{s} auto repair shop license", "{s} auto repair license", "how to open an auto repair shop in {s}",
           "{s} auto repair consumer rights", "{s} auto repair regulations"]
TESTE = ["auto repair laws by state", "auto repair laws", "auto repair estimate laws", "mechanic laws", "car repair laws",
         "can a mechanic charge more than the estimate", "can a mechanic charge more than quoted", "can a mechanic keep your car if you don't pay",
         "do mechanics have to give you a written estimate", "written estimate auto repair", "auto repair invoice requirements",
         "can i ask for my old parts back from mechanic", "do mechanics have to give old parts back", "do mechanics have to return old parts",
         "auto repair estimate template", "auto repair invoice template", "auto repair shop invoices", "auto repair invoices", "mechanic invoice",
         "mechanic receipt template", "repair order template", "auto repair work order template", "auto repair authorization form",
         "auto repair waiver form", "do you need a license to be a mechanic", "do i need a license to open an auto repair shop",
         "auto repair shop license", "auto repair license", "mechanic shop license", "how to start a mechanic shop", "how to open an auto repair shop",
         "auto repair shop requirements", "naics code for auto repair shop", "auto repair naics code",
         "florida motor vehicle repair act", "motor vehicle repair act", "fdacs motor vehicle repair", "florida motor vehicle repair license",
         "motor vehicle repair shop registration florida", "florida statute 559.905", "florida auto repair estimate law 10",
         "bureau of automotive repair", "bureau of automotive repair license", "write it right", "bar write it right", "california automotive repair act",
         "automotive repair dealer license", "ard license", "california auto repair estimate requirements", "california auto repair invoice requirements",
         "rcw 46.71", "washington auto repair act", "washington state auto repair act", "minnesota truth in repairs act", "truth in repairs act",
         "minnesota statute 325f.60", "michigan motor vehicle service and repair act", "motor vehicle service and repair act",
         "michigan repair facility license", "michigan repair facility registration", "michigan mechanic license", "michigan mechanic certification",
         "ny dmv repair shop", "nys dmv repair shop registration", "new york repair shop registration act", "nys repair shop regulations",
         "ny dmv repair shop complaint", "repair shop registration", "auto repair laws in washington state"]


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
                 "«Auto repair shop rules by state». volume null = la frase non è nel database dello strumento (risposta 404). «simili» = frasi vicine "
                 "restituite dallo strumento con il loro volume (misurate anch'esse: valgono per titoli e FAQ).",
        "misurato_il": "2026-11-19", "strumento": "api.seodata.dev, country=us", "ricerche_usate": 0, "frasi": {}}
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
            dati["frasi"][x] = {"volume": d.get("volume"), "cpc_usd": d.get("cpc"), "dato_del": (d.get("cached_at") or "2026-11-19")[:10],
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
