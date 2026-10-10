"""Decide se rigenerare e ripubblicare il sito (ogni pubblicazione Netlify costa 15 crediti su 300 al mese,
condivisi da tutti i siti dell'account: se finiscono, TUTTI i siti vanno offline fino al mese dopo).

Regole: al massimo MAX_MESE pubblicazioni nel mese solare; una a settimana per tenere fresche le pagine;
una in più (dopo almeno 2 giorni dall'ultima) se cambia uno sciopero importante: nazionale o in una delle
città/aeroporti del sito, per il trasporto passeggeri, nei prossimi 21 giorni. Tra una pubblicazione e l'altra le
pagine si aggiornano nel browser da dati/vista.json (pubblicato su GitHub, non su Netlify).

Stampa "deploy=si" o "deploy=no" (formato $GITHUB_OUTPUT) e, se si, registra la data in dati/deploy.json.
Uso: python3 italystrikes/raccolta/decidi_deploy.py [--forza]
"""
import hashlib
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

DATI = Path(__file__).resolve().parent.parent / "dati"
MAX_MESE = 6
PASSEGGERI = {"trains", "flights", "local-transport", "ferries", "taxis"}


def impronta_importante(oggi):
    vista = json.loads((DATI / "vista.json").read_text(encoding="utf-8"))
    limite = (oggi + timedelta(days=21)).isoformat()
    righe = sorted(
        (v["id"], v["inizio"], v["fine"], v["stato"])
        for v in vista["scioperi"]
        if v["fine"] >= oggi.isoformat() and v["inizio"] <= limite and PASSEGGERI & set(v["settori"])
        and (v["ambito"] == "national" or v["citta"] or v["aeroporti"]))
    return hashlib.sha256(json.dumps(righe).encode()).hexdigest()[:16]


def main():
    oggi = datetime.now(ZoneInfo("Europe/Rome")).date()
    f = DATI / "deploy.json"
    stato = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"pubblicazioni": [], "impronta": ""}
    nel_mese = [x for x in stato["pubblicazioni"] if x[:7] == oggi.isoformat()[:7]]
    ultima = date.fromisoformat(stato["pubblicazioni"][-1]) if stato["pubblicazioni"] else None
    giorni = (oggi - ultima).days if ultima else 999
    imp = impronta_importante(oggi)
    motivo = ""
    if "--forza" in sys.argv:
        motivo = "forzata"
    elif len(nel_mese) >= MAX_MESE:
        motivo = ""
    elif giorni >= 7:
        motivo = "settimanale"
    elif giorni >= 2 and imp != stato.get("impronta"):
        motivo = "sciopero importante cambiato"
    if motivo and (ultima != oggi or motivo == "forzata"):
        stato["pubblicazioni"].append(oggi.isoformat())
        stato["pubblicazioni"] = stato["pubblicazioni"][-60:]
        stato["impronta"] = imp
        f.write_text(json.dumps(stato, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("deploy=si")
        print(f"motivo={motivo}", file=sys.stderr)
    else:
        print("deploy=no")
        print(f"nessuna pubblicazione (questo mese {len(nel_mese)}/{MAX_MESE}, ultima {ultima})", file=sys.stderr)


if __name__ == "__main__":
    main()
