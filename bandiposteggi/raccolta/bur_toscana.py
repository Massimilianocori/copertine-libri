"""Raccolta degli avvisi sui posteggi dal BURT (Bollettino Ufficiale della Regione Toscana), Parte III
(avvisi di Comuni ed enti).

Fonte (verificata il 9/10/2026):
  indice: https://www.regione.toscana.it/burt/consultazione  -> link /documents/d/guest/parte-iii-n-<n>-del-<gg-mm-aaaa>
  ogni link scarica il PDF dell'intera Parte III del numero.

Uso:
  python3 -I bur_toscana.py <cartella_download> <file_json_uscita> [anno]

Per ogni PDF: testo con pdfplumber, divisione in avvisi sulle intestazioni "COMUNE DI ..." /
"UNIONE ...", filtro per parole chiave sui posteggi, estrazione campi con comune.py.
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

INDICE = "https://www.regione.toscana.it/burt/consultazione"
BASE = "https://www.regione.toscana.it"
RX_FORTE = re.compile(r"posteggi|posteggio|commercio su aree? pubblic|ambulant|chiosc|edicol|spuntist", re.I)
RX_TESTATA = re.compile(r"\n(?=(?:COMUNE|UNIONE DEI COMUNI|UNIONE MONTANA|CITTÀ METROPOLITANA|PROVINCIA) D[IE'][^\n]{2,60}\n)")


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    anno = sys.argv[3] if len(sys.argv) > 3 else "2026"
    t0 = time.time()
    st, _, dati = C.scarica(INDICE)
    link = sorted(set(re.findall(r'href="(/documents/d/guest/parte-iii-n-[^"]*?-' + anno + r'[^"]*)"', dati.decode("utf-8", "replace"))))
    print("parti III", len(link), flush=True)
    risultati, log = [], []
    for l in link:
        nome = l.rsplit("/", 1)[1]
        loc = os.path.join(cartella, nome + ".pdf")
        st, ct, _ = C.scarica(BASE + l, loc) if not os.path.exists(loc) else (200, "cache", b"")
        testo = C.testo_pdf(loc, max_pagine=400) if st == 200 else ""
        m = re.search(r"n-(\d+(?:bis)?)-del-(\d{2})-(\d{2})-(\d{4})", nome)
        data = f"{m.group(4)}-{m.group(3)}-{m.group(2)}" if m else None
        trovati = 0
        for blocco in RX_TESTATA.split(testo):
            testa = blocco[:900]
            if not RX_FORTE.search(testa) or C.ESCLUDI.search(testa[:300]):
                continue
            righe = [r.strip() for r in blocco.strip().split("\n") if r.strip()]
            trovati += 1
            risultati.append({
                "parte_iii": m.group(1) if m else nome, "data_bu": data, "ente": righe[0] if righe else "",
                "oggetto": " ".join(righe[1:5])[:400], "pdf": BASE + l,
                "tipo_auto": C.estrai_tipo(blocco), "posteggi_auto": C.estrai_numero(blocco[:4000]),
                "scadenza_auto": C.estrai_scadenza(blocco[:6000]), "testo": C.normalizza(blocco[:3000]),
            })
        log.append({"parte_iii": nome, "url": BASE + l, "http": st, "caratteri": len(testo), "avvisi": trovati})
        print(nome, st, len(testo), trovati, flush=True)
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "BURT Toscana - Parte III", "anno": anno, "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "numeri": log, "avvisi": risultati}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
