"""Calendari regionali di fiere e sagre (dato diverso dagli avvisi: sono eventi con date, non bandi).

Fonti (verificate il 9/10/2026):
  - Piemonte: PDF "Calendario regionale 2026 delle manifestazioni fieristiche e delle sagre e fiere mercato"
    https://www.regione.piemonte.it/web/media/55082/download  (elenchi alfabetici: "Comune (PR) date")
  - Emilia-Romagna: banca dati "Fiere su aree pubbliche" (HTML)
    https://wwwservizi.regione.emilia-romagna.it/sagre/ris_ricerca_sagre.asp?dt_datada=01/01/2026&dt_dataa=31/12/2026
  - Lombardia: allegati del decreto calendario fieristico 2026 (3° aggiornamento, dec. 11496 del 4/9/2026)
  - Abruzzo: Allegato A calendario regionale fiere 2026 (BURA, 5/12/2025)

Uso:
  python3 -I calendari.py <cartella_download> <file_json_uscita>
"""
import html
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comune as C  # noqa: E402

PIEMONTE = "https://www.regione.piemonte.it/web/media/55082/download"
ER = "https://wwwservizi.regione.emilia-romagna.it/sagre/ris_ricerca_sagre.asp?dt_datada=01/01/2026&dt_dataa=31/12/2026"
LOMB = ("https://www.regione.lombardia.it/content/dam/rl/canali-tematici-servizi/11-attivita-produttive-imprese/02-fiere/"
        "sch-il-calendario-2026-delle-manifestazioni-fieristiche-in-lombardia/allegati/dec-11496-all-{x}-fiere-regionali-2026-3-aggiornamento.pdf")
ABRUZZO = "https://bura.regione.abruzzo.it/sites/bura.regione.abruzzo.it/files/bollettini/2025-12-05/calendario-regionale-fiere-2026.pdf"
MESE = "|".join(C.MESI)
RX_PIE = re.compile(r"^(.+?) \((AL|AT|BI|CN|NO|TO|VB|VC)\) (\d{1,2}(?:\s*-\s*\d{1,2})?(?: (?:" + MESE + r"))?(?:\s*-\s*\d{1,2})? (?:" + MESE + r")(?:\s*-\s*\d{1,2} (?:" + MESE + r"))?)\s*$", re.I)


def piemonte(cartella):
    import pdfplumber
    loc = os.path.join(cartella, "piemonte-calendario-2026.pdf")
    st, _, _ = C.scarica(PIEMONTE, loc) if not os.path.exists(loc) else (200, "", b"")
    out = []
    with pdfplumber.open(loc) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ""
            testata = t[:200]
            if "elenco" in testata.lower() and "cronologico" in t[:400].replace("\n", ""):
                continue
            sezione = "sagra/fiera mercato" if "SAGRE E FIERE MERCATO" in testata else "manifestazione fieristica"
            righe = t.split("\n")
            for j, r in enumerate(righe):
                m = RX_PIE.match(r.strip())
                if m:
                    nxt = righe[j + 1: j + 3]
                    titolo = nxt[1] if sezione == "manifestazione fieristica" and len(nxt) > 1 else (righe[j + 2] if j + 2 < len(righe) else "")
                    out.append({"regione": "Piemonte", "comune": m.group(1).strip(), "provincia": m.group(2), "date": m.group(3),
                                "anno": 2026, "categoria": sezione, "qualifica_o_merci": nxt[0] if nxt else "",
                                "denominazione": titolo.strip(), "fonte": PIEMONTE, "pagina_pdf": i + 1})
    return st, out


def emilia(cartella):
    st, _, dati = C.scarica(ER, os.path.join(cartella, "er-fiere-2026.htm"))
    s = dati.decode("latin-1", "replace")
    out = []
    for d, titolo, luogo, prov, merci in re.findall(r"<dt>(\d\d/\d\d/\d{4}) - <a[^>]*>(.*?)</a> - (.*?) \((\w\w)\)</dt><dd>(.*?)</dd>", s, re.S):
        out.append({"regione": "Emilia-Romagna", "comune": html.unescape(luogo).strip().title(), "provincia": prov,
                    "date": d, "anno": 2026, "categoria": "fiera su area pubblica",
                    "denominazione": html.unescape(titolo).strip(),
                    "qualifica_o_merci": html.unescape(re.sub(r"<[^>]+>", " ", merci)).replace("Merci:", "").strip(), "fonte": ER})
    return st, out


def lombardia(cartella):
    out, stati = [], []
    for x in ("a", "b", "c"):
        url = LOMB.format(x=x)
        loc = os.path.join(cartella, f"lombardia-2026-all-{x}.pdf")
        st, _, _ = C.scarica(url, loc)
        stati.append(st)
        if st != 200:
            continue
        testo = C.testo_pdf(loc, max_pagine=60)
        for r in testo.split("\n"):
            # righe con una data gg/mm/aaaa del 2026: una per manifestazione
            if re.search(r"\b\d{1,2}/\d{1,2}/2026\b", r):
                # niente recapiti (telefoni, email) degli organizzatori
                r = re.sub(r"(?i)\b(?:tel|fax|cell)\.?\s*[\d /.+-]{6,}|\S+@\S+|-\s*$", " ", r)
                out.append({"regione": "Lombardia", "riga": re.sub(r"\s+", " ", r).strip()[:200], "anno": 2026,
                            "categoria": "manifestazione fieristica (allegato " + x.upper() + ")", "fonte": url})
    return stati, out


def abruzzo(cartella):
    loc = os.path.join(cartella, "abruzzo-2026.pdf")
    st, _, _ = C.scarica(ABRUZZO, loc)
    out = []
    if st == 200:
        for r in C.testo_pdf(loc, max_pagine=40).split("\n"):
            if re.match(r"^\d{1,3} ", r) and re.search(r"2026|\d{1,2}[-/]\d{1,2}", r):
                out.append({"regione": "Abruzzo", "riga": r.strip()[:200], "anno": 2026,
                            "categoria": "manifestazione fieristica", "fonte": ABRUZZO})
    return st, out


NOTE = [
    "Piemonte ed Emilia-Romagna elencano fiere e sagre su area pubblica (con posteggi per ambulanti): pertinenti per BandiPosteggi.",
    "Lombardia e Abruzzo elencano manifestazioni fieristiche in quartieri fieristici (fiere di settore): poco pertinenti per gli ambulanti;"
    " per la Lombardia le righe sono testo grezzo dell'allegato, non ancora divise in campi.",
    "Il PDF del calendario lombardo 2027 citato nello studio (Dec. 9712 del 17/07/2026, URL regione.lombardia.it/content/dam/rl/Dec.%209712...)"
    " risponde 404 il 9/10/2026.",
    "Gli eventi non sono avvisi di assegnazione: indicano dove e quando si terrà una fiera, non le scadenze delle domande.",
]


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    os.makedirs(cartella, exist_ok=True)
    t0 = time.time()
    fonti, eventi = [], []
    for nome, f, url in (("Piemonte", piemonte, PIEMONTE), ("Emilia-Romagna", emilia, ER),
                         ("Lombardia", lombardia, LOMB.format(x="[a|b|c]")), ("Abruzzo", abruzzo, ABRUZZO)):
        st, ev = f(cartella)
        fonti.append({"regione": nome, "url": url, "http": st, "eventi": len(ev)})
        eventi += ev
        print(nome, st, len(ev), flush=True)
    with open(uscita, "w", encoding="utf-8") as fo:
        json.dump({"descrizione": "Calendari regionali 2026 di fiere e sagre (eventi, non avvisi di assegnazione)",
                   "verificato_il": time.strftime("%Y-%m-%d"), "secondi": round(time.time() - t0),
                   "fonti": fonti, "note": NOTE, "eventi": eventi}, fo, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
