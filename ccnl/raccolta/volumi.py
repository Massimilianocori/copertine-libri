"""Volumi di ricerca mensili (Google Ads, Italia) per le pagine di Paga CCNL, letti con api.seodata.dev (country=it).

Uso (dalla radice del repository):
    python3 -I ccnl/raccolta/volumi.py elenco.txt [--max N]   # una frase per riga; salta quelle già misurate

Scrive in ccnl/dati/volumi-AAAA-MM-GG.json (data del giorno): per ogni frase volume, cpc, data del dato e le «simili»
restituite dallo strumento con il loro volume. volume null = risposta 404 (frase non nel database dello strumento).
La chiave del conto si legge dal file di configurazione locale e si usa solo nell'intestazione della richiesta:
non va mai stampata, scritta in un file o messa in un messaggio d'errore. Pausa di 0,35 secondi tra le richieste.
Si mandano solo parole di ricerca (contratti, livelli, «stipendio», «paga oraria»...), nessun dato personale.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
URL = "https://api.seodata.dev/v1/keyword?country=it&q="
FILE_CHIAVE = Path("/root/.config/seodata/key")


def file_del_giorno():
    return RADICE / "dati" / f"volumi-{date.today().isoformat()}.json"


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    frasi = [x.strip().lower() for x in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if x.strip()]
    massimo = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 400
    f = file_del_giorno()
    dati = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {
        "_nota": ("Volumi medi mensili di ricerca su Google in Italia (Google Ads) letti con api.seodata.dev (country=it). volume null = la frase "
                  "non è nel database dello strumento (risposta 404). «dato_del» = data del dato nello strumento. «simili» = frasi vicine "
                  "restituite dallo strumento con il loro volume (misurate anch'esse). Usati da genera.py per titoli, descrizioni e FAQ."),
        "misurato_il": date.today().isoformat(), "strumento": "api.seodata.dev, country=it", "ricerche_usate": 0, "frasi": {}}
    chiave = FILE_CHIAVE.read_text(encoding="utf-8").strip()
    fatte = 0
    for q in frasi:
        if q in dati["frasi"]:
            continue
        if fatte >= massimo:
            break
        req = urllib.request.Request(URL + urllib.parse.quote(q), headers={"Authorization": "Bearer " + chiave, "User-Agent": "ricerca-volumi/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode("utf-8"))
            dati["frasi"][q] = {"volume": d.get("volume"), "cpc_eur": d.get("cpc"), "dato_del": (d.get("cached_at") or "")[:10] or None,
                                "simili": {s["keyword"]: s["volume"] for s in d.get("similar", [])}}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                dati["frasi"][q] = {"volume": None}
            else:
                print(f"HTTP {e.code} su «{q}»: mi fermo", file=sys.stderr)
                break
        except (urllib.error.URLError, OSError) as e:
            print(f"errore di rete su «{q}» ({type(e).__name__}): mi fermo", file=sys.stderr)
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
