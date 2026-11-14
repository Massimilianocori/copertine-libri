"""Riunisce le risposte di seodata.dev (una per file JSON, scaricate con curl) in dati/domanda.json.

Le ricerche si fanno con curl, mai da Python, e la chiave non va mai scritta né stampata:
    curl -s -G "https://api.seodata.dev/v1/keyword" --data-urlencode "q=<frase>" --data-urlencode "country=us" \
         -H "Authorization: Bearer $(cat /root/.config/seodata/key)" -o <cartella>/<frase_con_trattini>.json
Poi: python3 realestate/raccolta/domanda.py <cartella>              # riscrive domanda.json con le sole risposte della cartella
      python3 realestate/raccolta/domanda.py <cartella> --aggiungi   # aggiunge (o aggiorna) le frasi della cartella a quelle già in domanda.json
"""
import json
import sys
from datetime import date
from pathlib import Path

DATI = Path(__file__).resolve().parent.parent / "dati"


def main():
    cartella = Path(sys.argv[1])
    ricerche = []
    for f in sorted(cartella.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if "keyword" not in d or d.get("volume") is None:
            raise SystemExit(f"{f.name}: risposta senza volume")
        ricerche.append({"frase": d["keyword"], "volume_mese": d["volume"], "cpc_usd": d.get("cpc") or 0,
                         "simili": [{"frase": s["keyword"], "volume_mese": s["volume"]} for s in d.get("similar", []) if s.get("volume")]})
    if "--aggiungi" in sys.argv and (DATI / "domanda.json").exists():
        nuove = {r["frase"] for r in ricerche}
        ricerche += [r for r in json.loads((DATI / "domanda.json").read_text(encoding="utf-8"))["ricerche"] if r["frase"] not in nuove]
    ricerche.sort(key=lambda r: (-r["volume_mese"], r["frase"]))
    testo = json.dumps({"_nota": f"Volumi medi mensili Google Ads (USA) letti con seodata.dev: {len(ricerche)} ricerche. Servono a scegliere i titoli e le FAQ: "
                                 "ogni FAQ cita una di queste frasi. Le frasi con l'anno risultano quasi sempre a 0 nello strumento.",
                        "letto_il": date.today().isoformat(), "paese": "us", "ricerche": ricerche}, ensure_ascii=False, indent=1) + "\n"
    if ("sd_" + "live") in testo:
        raise SystemExit("chiave nel testo: non scrivo")
    (DATI / "domanda.json").write_text(testo, encoding="utf-8")
    print(f"{len(ricerche)} ricerche in dati/domanda.json")


if __name__ == "__main__":
    main()
