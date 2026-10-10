"""Legge le Tabelle A e B dei treni garantiti Trenitalia (PDF ufficiali in questa cartella) e scrive treni-garantiti-2026.json.

Uso: python3 -I fonti/leggi_tabelle.py fonti/
Usa le tabelle del PDF (pdfplumber): righe con nomi di stazione su due righe e note "(n)" incluse.
"""
import json
import re
import sys
from pathlib import Path

import pdfplumber

cart = Path(sys.argv[1])
uscita = {}
for t in "AB":
    righe = []
    with pdfplumber.open(cart / f"trenitalia-tabella-{t}-treni-garantiti-2026.pdf") as pdf:
        for pag in pdf.pages:
            for tab in pag.extract_tables():
                for r in tab:
                    c = [re.sub(r"\s+", " ", (x or "")).strip() for x in r]
                    c = [x for x in c if x != ""]
                    if not c:
                        continue
                    m = re.match(r"^(\d{2,4})\s*(?:\((\d)\))?$", c[0])
                    if not m or len(c) < 6:
                        continue
                    nota = m.group(2)
                    resto = c[1:]
                    if len(resto) == 6 and re.fullmatch(r"\(\d\)", resto[0]):
                        nota, resto = resto[0][1], resto[1:]
                    cat, da, p, a, ar = resto[-5:]
                    righe.append(dict(n=m.group(1), nota=nota, cat=cat, da=da.title(), p=p.replace(".", ":"),
                                      a=a.title(), ar=ar.replace(".", ":")))
    uscita[t] = righe
    print(t, len(righe))
(cart / "treni-garantiti-2026.json").write_text(json.dumps(uscita, ensure_ascii=False, indent=0), encoding="utf-8")
