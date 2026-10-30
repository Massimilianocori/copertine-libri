"""Legge i 16 XLSX BAMF "Prüfstellen für den Einbürgerungstest" e scrive grezzi/sedi_bamf.json.

Uso: python3 -I leggi_bamf.py <cartella_con_gli_xlsx>
Gli XLSX (16 file, uno per Land) si scaricano da
https://www.bamf.de/SharedDocs/Anlagen/DE/Integration/Einbuergerung/Pruefstellen-<LAND>.html
Non si salvano qui perché contengono email personali del personale delle sedi:
in sedi_bamf.json teniamo solo il dominio dell'email (serve a trovare il sito della sede).
"""
import sys
import json
import pathlib
import openpyxl

QUI = pathlib.Path(__file__).resolve().parent
LAENDER = "BW BY BE BB HB HH HE MV NI NW RP SL SN ST SH TH".split()

def pulisci(v):
    if v is None:
        return ""
    return " ".join(str(v).split())

sedi = []
for land in LAENDER:
    wb = openpyxl.load_workbook(pathlib.Path(sys.argv[1]) / f"{land}.xlsx", read_only=True)
    ws = wb.worksheets[0]
    intest = None
    for riga in ws.iter_rows(values_only=True):
        celle = [pulisci(c) for c in riga]
        if intest is None:
            if any(c.startswith("Name") and "Prüfstelle" in c for c in celle):
                celle = ["Name der Prüfstelle" if (c.startswith("Name") and "Prüfstelle" in c) else c for c in celle]
                intest = celle
            continue
        if not any(celle):
            continue
        d = dict(zip(intest, celle))
        nome = d.get("Name der Prüfstelle", "")
        if not nome:
            continue
        sedi.append({
            "land": land,
            "kreis": d.get("Kreis / kreisfreie Stadt", "") or d.get("Kreis", ""),
            "plz": d.get("PLZ", "").split(".")[0].strip(),
            "ort": d.get("Ort", ""),
            "nome": nome,
            "via": d.get("Straße", ""),
            "telefono": d.get("Telefon", ""),
            "dominio_email": d.get("E-Mail", "").split("@")[-1].strip().lower() if "@" in d.get("E-Mail", "") else "",
        })
    if intest is None:
        print("ATTENZIONE: intestazione non trovata in", land)

(QUI / "grezzi" / "sedi_bamf.json").write_text(json.dumps(sedi, ensure_ascii=False, indent=1))
from collections import Counter
print(len(sedi), "sedi")
print(Counter(s["land"] for s in sedi).most_common())
