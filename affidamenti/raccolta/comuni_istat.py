"""Anagrafica dei Comuni italiani con popolazione, dai file ISTAT.

Fonti (scaricate a mano fuori dal repository, verificate il 10/10/2026):
  - https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv
    (codici, denominazione, regione, provincia, flag capoluogo; latin-1, ';')
  - https://demo.istat.it/data/posas/POSAS_2026_it_Comuni.zip
    (popolazione residente per età al 1/1/2026, stima; la riga Età=999 è il totale)

Uso:
    python3 -I comuni_istat.py ELENCO.csv POSAS.zip USCITA.tsv

Scrive un TSV: istat, comune, provincia_sigla, regione, capoluogo(0/1), popolazione.
Funzioni riusabili: carica(path_tsv) -> lista di dict; estrai_medi(...) per il
campione casuale di Comuni "medi" (soglie di popolazione come argomenti).
"""
import csv
import io
import random
import sys
import zipfile


def leggi_elenco(path):
    with open(path, encoding="latin-1", newline="") as f:
        r = csv.reader(f, delimiter=";")
        intest = next(r)
        out = {}
        for row in r:
            d = dict(zip(intest, row))
            cod = d["Codice Comune formato alfanumerico"].strip()
            out[cod] = {
                "istat": cod,
                "comune": d["Denominazione in italiano"].strip(),
                "provincia_sigla": d["Sigla automobilistica"].strip(),
                "regione": d["Denominazione Regione"].strip(),
                "capoluogo": int(d[[k for k in intest if k.startswith("Flag Comune capoluogo")][0]].strip() or 0),
            }
    return out


def leggi_popolazione(path_zip):
    z = zipfile.ZipFile(path_zip)
    testo = z.read(z.namelist()[0]).decode("utf-8-sig", "replace")
    righe = testo.splitlines()[1:]  # la prima riga è il titolo
    pop = {}
    for d in csv.DictReader(io.StringIO("\n".join(righe)), delimiter=";"):
        if (d.get("Età") or "").strip() == "999" and d.get("Totale"):
            pop[d["Codice comune"].strip()] = int(d["Totale"])
    return pop


def carica(path_tsv):
    with open(path_tsv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        r["popolazione"] = int(r["popolazione"] or 0)
        r["capoluogo"] = int(r["capoluogo"])
    return rows


def estrai_medi(rows, n, seme, pop_min=15000, pop_max=60000, escludi_capoluoghi=True):
    """Estrazione casuale riproducibile di n Comuni 'medi'."""
    cand = [r for r in rows if pop_min <= r["popolazione"] <= pop_max
            and not (escludi_capoluoghi and r["capoluogo"])]
    cand.sort(key=lambda r: r["istat"])
    return random.Random(seme).sample(cand, n)


def main():
    elenco, posas, uscita = sys.argv[1:4]
    el = leggi_elenco(elenco)
    pop = leggi_popolazione(posas)
    with open(uscita, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["istat", "comune", "provincia_sigla", "regione", "capoluogo", "popolazione"])
        for cod in sorted(el):
            e = el[cod]
            w.writerow([cod, e["comune"], e["provincia_sigla"], e["regione"], e["capoluogo"], pop.get(cod, "")])
    print(f"{len(el)} comuni, popolazione trovata per {sum(1 for c in el if c in pop)}")


if __name__ == "__main__":
    main()
