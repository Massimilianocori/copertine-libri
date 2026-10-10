"""Prepara i dati del calcolatore di codice fiscale (satellite di Italy Strikes Today).

Fonti ufficiali:
- Stati esteri con codice catastale (CODAT, "Z..."): tabella 2 ANPR, Ministero dell'Interno
  https://www.anagrafenazionale.interno.it/wp-content/uploads/tabella_2_statiesteri.xlsx (copia in fonti/)
- Comuni italiani con codice catastale: ISTAT https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv
Uso: python3 italystrikes/satelliti/prepara_cf.py   -> scrive satelliti/cf-esteri.json e cf-comuni.json
"""
import csv
import io
import json
import urllib.request
from datetime import date
from pathlib import Path

import openpyxl

QUI = Path(__file__).resolve().parent
URL_ISTAT = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"
URL_ANPR = "https://www.anagrafenazionale.interno.it/wp-content/uploads/tabella_2_statiesteri.xlsx"


def esteri():
    wb = openpyxl.load_workbook(QUI / "fonti" / "anpr-tabella_2_statiesteri.xlsx", read_only=True)
    ws = wb.worksheets[0]
    righe = list(ws.iter_rows(values_only=True))
    t = righe[0]
    i = {k: t.index(k) for k in ("DENOMINAZIONEISTAT", "DENOMINAZIONEISTAT_EN", "CODAT", "DATAFINEVALIDITA", "NASCITA")}
    out = []
    for r in righe[1:]:
        cod = (r[i["CODAT"]] or "").strip()
        if not cod.startswith("Z") or len(cod) != 4:
            continue
        if not str(r[i["DATAFINEVALIDITA"]] or "").startswith("31/12/9999"):
            continue
        out.append({"en": (r[i["DENOMINAZIONEISTAT_EN"]] or "").strip(), "it": (r[i["DENOMINAZIONEISTAT"]] or "").strip(), "c": cod})
    out.sort(key=lambda x: x["en"])
    return out


def comuni():
    req = urllib.request.Request(URL_ISTAT, headers={"User-Agent": "Mozilla/5.0"})
    testo = urllib.request.urlopen(req, timeout=60).read().decode("latin-1")
    r = csv.reader(io.StringIO(testo), delimiter=";")
    t = next(r)
    norm = [c.replace("\n", " ").strip() for c in t]
    ic = next(k for k, c in enumerate(norm) if c.lower().startswith("codice catastale"))
    inome = norm.index("Denominazione in italiano")
    isig = norm.index("Sigla automobilistica")
    out = []
    for riga in r:
        if len(riga) <= max(ic, inome, isig) or not riga[ic].strip():
            continue
        out.append([riga[inome].strip(), riga[isig].strip(), riga[ic].strip()])
    out.sort()
    return out


def main():
    e, c = esteri(), comuni()
    if len(e) < 180 or len(c) < 7500:
        raise SystemExit(f"ERRORE: dati incompleti (esteri {len(e)}, comuni {len(c)})")
    meta = {"letto_il": date.today().isoformat(), "fonte_esteri": URL_ANPR, "fonte_comuni": URL_ISTAT}
    (QUI / "cf-esteri.json").write_text(json.dumps({"meta": meta, "paesi": e}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (QUI / "cf-comuni.json").write_text(json.dumps({"meta": meta, "comuni": c}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Paesi esteri: {len(e)}; comuni: {len(c)}.")


if __name__ == "__main__":
    main()
