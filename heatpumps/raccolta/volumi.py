"""Volumi di ricerca mensili (Google Ads, Regno Unito) per Heat Pump Grants UK, letti con api.seodata.dev (country=gb).

Uso (dalla radice del repository):
    python3 -I heatpumps/raccolta/volumi.py elenco.txt [--max N]   # una frase per riga; salta quelle già misurate

Scrive in heatpumps/dati/volumi-AAAA-MM-GG.json (data del giorno): per ogni frase volume, cpc (£), data del dato e le «simili»
restituite dallo strumento con il loro volume. volume null = risposta 404 (frase non nel database dello strumento).
Le richieste passano da curl (da Python con urllib lo strumento risponde 403). La chiave del conto si legge dal file di
configurazione locale e arriva a curl solo dallo standard input (-K -): non compare negli argomenti del processo, non viene
mai stampata, scritta in un file o messa in un messaggio d'errore. Pausa di 0,35 secondi tra le richieste.
Si mandano solo parole di ricerca (schemi, contributi, luoghi), nessun dato personale.
"""
import json
import subprocess
import sys
import time
import urllib.parse
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
URL = "https://api.seodata.dev/v1/keyword?country=gb&q="
FILE_CHIAVE = Path("/root/.config/seodata/key")


def file_del_giorno():
    return RADICE / "dati" / f"volumi-{date.today().isoformat()}.json"


def chiedi(q, chiave):
    """(codice HTTP, corpo) con curl; la chiave passa solo dallo standard input come file di configurazione."""
    conf = f'header = "Authorization: Bearer {chiave}"\n'
    r = subprocess.run(["curl", "-s", "-K", "-", "-w", "\n%{http_code}", "--max-time", "40", URL + urllib.parse.quote(q)],
                       input=conf, capture_output=True, text=True)
    corpo, _, codice = r.stdout.rpartition("\n")
    return (int(codice) if codice.isdigit() else 0), corpo


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    frasi = [x.strip().lower() for x in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    massimo = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 350
    f = file_del_giorno()
    dati = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {
        "_nota": ("Volumi medi mensili di ricerca su Google nel Regno Unito (Google Ads) letti con api.seodata.dev (country=gb). volume null = "
                  "la frase non è nel database dello strumento (risposta 404). «dato_del» = data del dato nello strumento. «simili» = frasi "
                  "vicine restituite dallo strumento con il loro volume (misurate anch'esse). Usati da genera.py per titoli, descrizioni e FAQ."),
        "misurato_il": date.today().isoformat(), "strumento": "api.seodata.dev, country=gb", "ricerche_usate": 0, "frasi": {}}
    chiave = FILE_CHIAVE.read_text(encoding="utf-8").strip()
    fatte = 0
    for q in frasi:
        if q in dati["frasi"]:
            continue
        if fatte >= massimo:
            break
        codice, corpo = chiedi(q, chiave)
        if codice == 200:
            d = json.loads(corpo)
            dati["frasi"][q] = {"volume": d.get("volume"), "cpc_gbp": d.get("cpc"), "dato_del": (d.get("cached_at") or "")[:10] or None,
                                "simili": {s["keyword"]: s["volume"] for s in d.get("similar", [])}}
        elif codice == 404:
            dati["frasi"][q] = {"volume": None}
        else:
            print(f"HTTP {codice} su «{q}»: mi fermo", file=sys.stderr)
            break
        fatte += 1
        dati["ricerche_usate"] += 1
        f.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")  # dopo ogni risposta: niente richieste perse
        time.sleep(0.35)
    del chiave
    f.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{fatte} richieste ora, {dati['ricerche_usate']} in tutto oggi; {len(dati['frasi'])} frasi in {f.relative_to(RADICE.parent)}")


if __name__ == "__main__":
    main()
