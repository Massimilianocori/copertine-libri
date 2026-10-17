"""Ricontrolla sulla fonte HUD, uno per uno, un campione di condomini dei nostri dati.

Uso (dalla radice del repository):
    python3 fhacondos/raccolta/ricontrolla.py                         # 20 condomini a caso da dati/condomini.json
    python3 fhacondos/raccolta/ricontrolla.py --n 20 --seme 7
    python3 fhacondos/raccolta/ricontrolla.py --edizione 2026-10-17 --stati VA,FL,CO   # dalla cache (test)

Per ogni condominio fa una ricerca NUOVA sul modulo HUD per Condo ID (tutti gli Stati, stato "All"), senza cache, e
confronta: nome, ID, indirizzo, città, contea, CAP, unità, stato, data dello stato e data di scadenza.
Due controlli indipendenti per ogni campo:
  1. valore letto dalla riga nuova con il parser (estrai.analizza_riga) == valore nei nostri dati;
  2. il valore dei nostri dati compare alla lettera nel testo della riga HUD (date nel formato MM/DD/YYYY della fonte),
     senza passare dal parser: così un errore del parser non si "conferma da solo".
Le unità si controllano sul testo grezzo: il numero deve comparire seguito da "unit".
Esce con codice 1 se c'è anche un solo errore. Ritmo: una richiesta ogni 1,2-2 secondi.
"""
import argparse
import html
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estrai import DATI, RE_RIGA, analizza_riga, leggi_edizione  # noqa: E402
from scarica import CACHE, MODULO, Sessione, campi_ricerca  # noqa: E402
from datetime import date  # noqa: E402

CAMPI = [("nome_raw", "nome"), ("id", "ID"), ("via_raw", "indirizzo"), ("citta_raw", "città"), ("contea_raw", "contea"),
         ("cap", "CAP"), ("unita", "unità"), ("stato", "stato"), ("data_stato", "data stato"), ("scadenza", "scadenza")]


def piatto(s):
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s).replace("\xa0", " ")).strip()


def usa(d):
    return f"{d[5:7]}/{d[8:10]}/{d[0:4]}" if d else ""


def ricerca_id(sess, condo_id):
    campi = campi_ricerca("", "X", date.today(), condo_id=condo_id)
    t = sess.post(campi, MODULO)
    righe = [r for r in RE_RIGA.findall(t) if condo_id in r]
    return righe


def controlla(nostro, riga_html):
    nuovo = analizza_riga(riga_html)
    grezzo = piatto('<td width="10%" align="left" valign="top">' + riga_html)
    errori = []
    for k, etichetta in CAMPI:
        a, b = nostro.get(k), nuovo.get(k)
        if a != b:
            errori.append(f"{etichetta}: nostro {a!r} / HUD {b!r}")
            continue
        # controllo 2: presenza letterale nel testo della riga
        if k in ("data_stato", "scadenza"):
            v = usa(a)
        elif k == "unita":
            if a is not None and not re.search(rf"(?<!\d)\(?{a}\)?\s*(?:-\s*)?(?:[A-Za-z.'/-]+\s+){{0,3}}units?\b", grezzo, re.I):
                errori.append(f"unità: {a} non trovato nel testo HUD")
            continue
        else:
            v = a or ""
        if v and v not in grezzo:
            errori.append(f"{etichetta}: {v!r} non compare nel testo HUD")
    return nuovo, errori


def esegui(condomini, n, seme, uscita_md=None):
    rnd = random.Random(seme)
    campione = rnd.sample(condomini, n)
    sess = Sessione()
    risultati, tot_err = [], 0
    for c in campione:
        righe = ricerca_id(sess, c["id"])
        if len(righe) != 1:
            errori = [f"la ricerca per ID ha dato {len(righe)} righe"]
            nuovo = {}
        else:
            nuovo, errori = controlla(c, righe[0])
        tot_err += len(errori)
        risultati.append((c, nuovo, errori))
        print(f"{c['id']} {c['st']} {c['nome_raw'][:40]:40} {'OK' if not errori else 'ERRORE: ' + '; '.join(errori)}",
              flush=True)
    righe_md = ["| # | Condo ID | Nome (HUD) | Città, Stato | CAP | Contea | Unità | Stato | Data stato | Scadenza | Esito |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, (c, nuovo, errori) in enumerate(risultati, 1):
        righe_md.append(f"| {i} | {c['id']} | {c['nome_raw']} | {c['citta_raw']}, {c['st']} | {c['cap'] or '–'} | "
                        f"{c['contea_raw'] or '–'} | {c['unita'] if c['unita'] is not None else '–'} | {c['stato']} | "
                        f"{usa(c['data_stato'])} | {usa(c['scadenza'])} | {'OK' if not errori else '; '.join(errori)} |")
    md = "\n".join(righe_md)
    if uscita_md:
        Path(uscita_md).write_text(md + "\n")
    print(f"\n{len(campione)} condomini ricontrollati, {tot_err} errori, {sess.richieste} richieste.")
    return tot_err, md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seme", type=int, default=None, help="vuoto = campione diverso a ogni esecuzione")
    ap.add_argument("--edizione", default="", help="legge dalla cache invece che da dati/condomini.json")
    ap.add_argument("--stati", default="")
    ap.add_argument("--solo-approvati", action="store_true", default=True)
    ap.add_argument("--md", default="", help="scrive anche la tabella in Markdown in questo file")
    a = ap.parse_args()
    if a.edizione:
        stati = [s.strip().upper() for s in a.stati.split(",") if s.strip()] or None
        condomini, _, _ = leggi_edizione(CACHE / a.edizione, tipi=("A",), stati=stati)
    else:
        condomini = json.loads((DATI / "condomini.json").read_text())
        if a.stati:
            stati = {s.strip().upper() for s in a.stati.split(",")}
            condomini = [c for c in condomini if c["st"] in stati]
    if a.solo_approvati:
        condomini = [c for c in condomini if c["tipo"] == "A"]
    err, _ = esegui(condomini, a.n, a.seme, a.md or None)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
