"""Soglia 4: controllo di verità tra le determine dei Comuni e i dati ANAC.

Passo 1 (estrai): da ciascun file prodotto da atti_maggioli.py sceglie a caso
(seme fisso) N determine di affidamento pubblicate nel periodo con un CIG
nell'oggetto (escluse liquidazioni, rettifiche, revoche, impegni senza
affidamento), apre la pagina di dettaglio sulla piattaforma del Comune, scarica
il primo allegato PDF in una cartella di lavoro FUORI dal repository e ne
estrae il testo (pdftotext), poi cerca il CIG nell'indice TSV prodotto da
analizza_mese.py (campi ANAC: ente, oggetto, importo, aggiudicatari,
aggiudicazione, primo file delta in cui compare).

Uso:
    python3 -I verita.py estrai --atti A1.json A2.json ... --indice indice.tsv \
        --lavoro CARTELLA --uscita verita-bozza.json [--per-ente 4] [--seme 20261010]

Il confronto (importo, aggiudicatario, oggetto) si fa leggendo il testo della
determina salvato in CARTELLA/<cig>.txt: l'esito è registrato a mano nel file
finale con una nota per ogni caso (nessuna correzione dei dati ANAC).
"""
import argparse
import base64
import html
import json
import os
import random
import re
import subprocess
import time

UA = "Mozilla/5.0 (compatible; ChiLavoraColComune-test/0.1)"
RE_SI = re.compile(r"AFFIDAMENT|AGGIUDICA|CONTRARRE|ORDINE DIRETTO|ODA|TRATTATIVA DIRETTA", re.I)
RE_NO = re.compile(r"LIQUIDAZ|RETTIFIC|REVOC|ANNULLAMENT|ACCERTAMENT|RIMBORS|PRESA D'ATTO|PROROGA", re.I)


def curl(url, out=None):
    cmd = ["curl", "-sSL", "--max-time", "90", "-A", UA]
    if out:
        cmd += ["-o", out]
    r = subprocess.run(cmd + [url], capture_output=True)
    time.sleep(1.5)
    return r.stdout.decode("utf-8", "replace") if not out else None


def leggi_indice(path, cigs):
    trovati = {}
    with open(path, encoding="utf-8") as f:
        intest = f.readline().rstrip("\n").split("\t")
        for line in f:
            c = line[:10]
            if c in cigs:
                trovati[c] = dict(zip(intest, line.rstrip("\n").split("\t")))
    return trovati


def estrai(a):
    rnd = random.Random(a.seme)
    scelti = []
    for p in a.atti:
        d = json.load(open(p, encoding="utf-8"))
        cand = [x for x in d["atti"] if x["cig"] and RE_SI.search(x["oggetto"]) and not RE_NO.search(x["oggetto"])]
        cand.sort(key=lambda x: (x["data_pubblicazione"], x["numero"]))
        for x in rnd.sample(cand, min(a.per_ente, len(cand))):
            x = dict(x, ente_host=d["host"], candidati_ente=len(cand), atti_periodo_ente=d["atti_nel_periodo"])
            scelti.append(x)
    idx = leggi_indice(a.indice, {x["cig"][0] for x in scelti})
    os.makedirs(a.lavoro, exist_ok=True)
    for x in scelti:
        c = x["cig"][0]
        x["anac"] = idx.get(c)
        x["allegati"] = []
        if x["url"]:
            pag = curl(x["url"])
            links = [html.unescape(h) for h in re.findall(r'href="([^"]+)"', pag)
                     if re.search(r"download|\.pdf|/documents/|allegat", h, re.I) and "javascript" not in h]
            # piattaforma Maggioli: link agli allegati codificati come window.open(atob('...'))
            links = [base64.b64decode(b).decode("utf-8", "replace") for b in re.findall(r"atob\('([A-Za-z0-9+/=]+)'\)", pag)] + links
            x["allegati"] = links[:5]
            for i, l in enumerate(links[:3]):
                dest = os.path.join(a.lavoro, f"{c}_{i}.pdf")
                curl(l, dest)
                if os.path.exists(dest) and open(dest, "rb").read(4) == b"%PDF":
                    subprocess.run(["pdftotext", "-layout", dest, os.path.join(a.lavoro, f"{c}.txt")])
                    x["pdf_letto"] = l
                    break
        print(c, x["ente_host"].split(".")[0], "ANAC:", "SI" if x["anac"] else "NO", "PDF:", "SI" if x.get("pdf_letto") else "NO", flush=True)
    with open(a.uscita, "w", encoding="utf-8") as f:
        json.dump(scelti, f, ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("azione", choices=["estrai"])
    ap.add_argument("--atti", nargs="+", required=True)
    ap.add_argument("--indice", required=True)
    ap.add_argument("--lavoro", required=True)
    ap.add_argument("--uscita", required=True)
    ap.add_argument("--per-ente", type=int, default=4)
    ap.add_argument("--seme", type=int, default=20261010)
    estrai(ap.parse_args())


if __name__ == "__main__":
    main()
