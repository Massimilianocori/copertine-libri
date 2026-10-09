"""Legge l'elenco "Avvisi" dei siti comunali costruiti con Municipium e tiene quelli sui posteggi.

Struttura verificata il 9/10/2026 (es. https://www.comune.ragusa.it/it/news?type=3):
  - /it/news?type=3&page=<n> = elenco degli avvisi, 9-12 schede per pagina, dalla più recente;
  - ogni scheda: <span class="h5 card-pretitle"> <data> </span> <a href="..." class="link-detail"> <h3 ...> <titolo>
  - l'API <comune>-api.municipiumapp.it/api/... risponde 401 senza credenziali: si usa solo l'HTML pubblico;
  - i PDF allegati stanno su <comune>-api.municipiumapp.it/s3/... e sono serviti agli script (24 su 25 nel test).

Non esiste un elenco pubblico dei Comuni che usano Municipium: i domini vanno raccolti a parte
(file di testo, un dominio per riga, es. "www.comune.ragusa.it").

Uso:
  python3 -I municipium.py <domini.txt> <file_json_uscita> [pagine_max]

Per ogni dominio legge le pagine dell'elenco finché trova avvisi del 2026 (al massimo pagine_max)
e salva: HTTP status, pagine lette, avvisi 2026 totali, avvisi 2026 con parole chiave sui posteggi.
"""
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

RX_SCHEDA = re.compile(r'card-pretitle">\s*(\d{1,2} \w+ \d{4})\s*</span>\s*<a href="([^"]+)" class="link-detail">\s*<h3[^>]*>(.*?)</h3>', re.S)
RX_POSTEGGI = re.compile(r"posteggi|posteggio|aree pubbliche|area pubblica|ambulant|chiosc|edicol|spunta|spuntist|"
                         r"\bfiera\b|\bfiere\b|sagra|mercatin|mercato settimanale|food truck|street food|postazion", re.I)


def data_iso(d):
    g, m, a = d.split()
    return f"{a}-{C.MESI.get(m.lower(), 0):02d}-{int(g):02d}"


def main():
    domini = [r.strip() for r in open(sys.argv[1], encoding="utf-8") if r.strip() and not r.startswith("#")]
    uscita = sys.argv[2]
    pagine_max = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    t0 = time.time()
    out = []
    for dom in domini:
        avvisi, st_primo, pagine = [], None, 0
        for p in range(1, pagine_max + 1):
            st, ct, dati = C.scarica(f"https://{dom}/it/news?type=3&page={p}")
            st_primo = st_primo or st
            if st != 200:
                break
            pagine += 1
            schede = RX_SCHEDA.findall(dati.decode("utf-8", "replace"))
            if not schede:
                break
            for d, u, t in schede:
                avvisi.append({"data": data_iso(d), "url": u, "titolo": re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()})
            if min(data_iso(d) for d, _, _ in schede) < "2026-01-01":
                break
        anno = [a for a in avvisi if a["data"].startswith("2026")]
        pert = [a for a in anno if RX_POSTEGGI.search(a["titolo"])]
        out.append({"dominio": dom, "http": st_primo, "pagine_lette": pagine, "avvisi_2026": len(anno),
                    "avvisi_posteggi_2026": len(pert), "pertinenti": pert})
        print(dom, st_primo, pagine, len(anno), len(pert), flush=True)
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({"fonte": "Elenco 'Avvisi' dei siti Municipium", "verificato_il": time.strftime("%Y-%m-%d"),
                   "secondi": round(time.time() - t0), "domini": out}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
