"""Scarica i file ufficiali del sito Codici ATECO 2025 e ne registra impronta, byte, HTTP e frasi controllate.

Uso (dalla radice del repository):
    python3 -I ateco/raccolta/fonti.py            # scarica solo i file che mancano in raccolta/_grezzi/
    python3 -I ateco/raccolta/fonti.py --rete     # riscarica tutto (aggiornamento: impronta cambiata = file nuovo)

Scrive ateco/dati/fonti.json: per ogni fonte indirizzo pubblico, HTTP, byte, SHA-256, data di lettura e l'esito di ogni
frase cercata (pagine ISTAT, note legali ISTAT con la licenza, nota congiunta Istat-Camere-Agenzia delle entrate,
risoluzione 24/E dell'Agenzia delle entrate, testi di legge su Normattiva per il regime forfetario).

Licenza dei contenuti ISTAT: Creative Commons Attribuzione 4.0 (frase controllata nella pagina «Note legali»).
robots.txt di istat.it e normattiva.it: i percorsi usati sono permessi (Normattiva vieta solo /ricerca/ e /mfr/ricerca/).
Nessun dato personale: si scaricano solo documenti pubblici. Pausa di 1 secondo tra le richieste.
"""
import hashlib
import html
import http.cookiejar
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (compatible; ateco-check/1.0)"
UP = "https://www.istat.it/wp-content/uploads/"
NORMATTIVA = "https://www.normattiva.it"

# File di dati e documenti (PDF: le frasi si cercano nel testo estratto con pdftotext).
FILE = {
    "struttura": {"url": UP + "2025/02/StrutturaATECO-2025-IT-EN-DE.xlsx", "nome": "struttura.xlsx",
                  "titolo": "Struttura ATECO 2025 italiano inglese tedesco (xlsx)", "chi": "Istat", "pagina": "istat_ateco"},
    "note": {"url": UP + "2025/03/Note-esplicative-ATECO-2025-italiano-inglese.xlsx", "nome": "note.xlsx",
             "titolo": "Note esplicative ATECO 2025 italiano inglese (xlsx)", "chi": "Istat", "pagina": "istat_ateco"},
    "raccordo": {"url": UP + "2026/07/Aggiornamento-2026-Tavola-raccordo-bidirezionale-ATECO-2025-ATECO-2022-italiano.xlsx",
                 "nome": "raccordo.xlsx", "titolo": "Tavola di raccordo bidirezionale ATECO 2025 – ATECO 2022 (aggiornamento 2026), italiano (xlsx)",
                 "chi": "Istat", "pagina": "istat_ateco"},
    "operativa": {"url": UP + "2026/07/Aggiornamento-2026-Tabella-operativa-riclassificazione-ATECO-2022-ATECO-2025.xlsx",
                  "nome": "operativa.xlsx", "titolo": "Tabella operativa di riclassificazione da ATECO 2022 a ATECO 2025 (aggiornamento 2026) (xlsx)",
                  "chi": "Istat con il sistema camerale", "pagina": "istat_ateco"},
    "nota_congiunta": {"url": UP + "2024/12/NotaInformativaCongiunta_Ateco.pdf", "nome": "nota_congiunta.pdf",
                       "titolo": "Nuova classificazione ATECO 2025: gli adempimenti statistici e amministrativi di imprese e liberi professionisti (nota informativa congiunta, 11 dicembre 2024)",
                       "chi": "Istat, sistema camerale e Agenzia delle entrate", "pagina": "istat_comunicato",
                       "cerca": ["entrerà in vigore a partire dal 1° gennaio 2025",
                                 "La nuova classificazione verrà adottata a partire dal 1° aprile 2025",
                                 "Il processo di riclassificazione sarà eseguito d’ufficio a partire dal 1° aprile 2025",
                                 "la visura camerale dell’impresa riporterà per un periodo transitorio sia i nuovi codici ATECO sia quelli precedenti",
                                 "tutti gli operatori IVA saranno tenuti ad utilizzare i codici attività indicati nella nuova classificazione ATECO 2025",
                                 "non comporta l’obbligo di presentare un’apposita dichiarazione di variazione dati",
                                 "la dichiarazione dovrà essere effettuata con la Comunicazione Unica (ComUnica)",
                                 "modello AA9/12 per imprese individuali, lavoratori autonomi, artisti e professionisti",
                                 "modello AA7/10 per società, enti, associazioni, eccetera",
                                 "modello AA5/6 per enti non commerciali, associazioni, eccetera",
                                 "modello ANR/3 per l’identificazione diretta ai fini IVA di soggetto non residente",
                                 "se il contribuente è iscritto nel Registro delle Imprese delle Camere di commercio",
                                 "A imprese e liberi professionisti non è richiesta alcuna azione prima del 1° aprile 2025"]},
    "risoluzione_24e": {"url": "https://www.agenziaentrate.gov.it/portale/documents/20143/8410900/RISOLUZIONE+ATECO+2025.pdf/05fdbeda-c727-bf26-ecab-a2e6c1080753",
                        "nome": "risoluzione_24e.pdf", "titolo": "Risoluzione n. 24/E dell'8 aprile 2025: Nuova classificazione delle attività economiche ATECO 2025",
                        "chi": "Agenzia delle entrate", "pagina": None,
                        "cerca": ["dal 1° gennaio 2025 è entrata in vigore la nuova classificazione delle attività economiche ATECO 2025",
                                  "che sostituisce la precedente versione ATECO 2007 (aggiornamento 2022)",
                                  "la nuova classificazione è attiva dal 1° aprile 2025",
                                  "Cassetto fiscale – Consultazioni – Anagrafica",
                                  "I contribuenti possono verificare i codici ATECO, prevalente e secondari, collegati alla propria posizione fiscale e registrati in Anagrafe Tributaria",
                                  "sono tenuti a utilizzare i nuovi codici negli atti e nelle dichiarazioni da presentare all’Agenzia delle entrate",
                                  "non comporta l’obbligo di presentare la dichiarazione di variazione dei dati"]},
    # Istruzioni dell'Agenzia al quadro LM: conferma della regola «coefficiente secondo ATECO 2007». L'indirizzo cambia ogni anno
    # (e a ogni aggiornamento delle istruzioni): se risponde 404, cercare il fascicolo 3 del modello Redditi PF dell'anno sul sito dell'Agenzia.
    "istruzioni_lm": {"url": "https://www.agenziaentrate.gov.it/portale/documents/d/guest/pf3_istruzioni_2026_agg-13-05-2026",
                      "nome": "istruzioni_lm.pdf", "titolo": "Modello Redditi Persone fisiche 2026, fascicolo 3, istruzioni per la compilazione (quadro LM, regime forfetario; aggiornamento del 13 maggio 2026)",
                      "chi": "Agenzia delle entrate", "pagina": None,
                      "cerca": ["Nel rigo LM21, colonna 4, (codice ATECO 2025) va indicato il codice dell’attività svolta in vigore dal 2025",
                                "all’approvazione dei nuovi coefficienti di redditività elaborati sulla base della classificazione delle attività economiche ATECO 2025",
                                "individuato sulla base del codice corrispondente all’attività esercitata secondo la classificazione ATECO 2007. (art. 1, decreto legislativo 12 giugno 2025, n. 81)"]},
}

# Pagine web: frasi controllate. "atto" + "voce": testo di un articolo o allegato su Normattiva (si apre prima l'atto,
# poi la voce dell'indice con la stessa sessione, come fa il browser).
PAGINE = {
    "istat_ateco": {"url": "https://www.istat.it/classificazione/ateco-2025/", "titolo": "ATECO 2025 e aggiornamenti", "chi": "Istat",
                    "cerca": ["Dall’1 gennaio 2025 è entrata in vigore ATECO 2025, la nuova classificazione delle attività economiche",
                              "La classificazione è stata adottata operativamente a partire dall’1 aprile 2025",
                              "L’aggiornamento 2026 della classificazione ATECO 2025 non ha modificato la struttura, i livelli o le descrizioni della classificazione, ma ha aggiornato esclusivamente le relazioni di corrispondenza",
                              "è coerente con NACE Rev. 2.1",
                              "sezioni (lettera maiuscola), divisioni (2 cifre numeriche), gruppi (3 cifre numeriche), classi (4 cifre numeriche), categorie (5 cifre numeriche) e sottocategorie (6 cifre numeriche)",
                              "note di inclusione e di inclusione aggiuntiva : rappresentano esempi di attività economiche comprese in un determinato codice ma non possono essere considerate esaustive",
                              "note di esclusione : intendono evidenziare quelle attività economiche che non appartengono ad un determinato codice",
                              "Questa semplificazione implica inevitabilmente una perdita di informazioni"],
                    "data": r"Data aggiornamento: (\d{1,2} \w+ \d{4})"},
    "istat_comunicato": {"url": "https://www.istat.it/comunicato-stampa/nuova-classificazione-ateco-2025/",
                         "titolo": "Nuova classificazione Ateco 2025: gli adempimenti statistici e amministrativi di imprese e liberi professionisti", "chi": "Istat",
                         "cerca": ["La nuova classificazione dovrà essere utilizzata per tutti gli adempimenti non solo di natura statistica ma anche di natura amministrativa"]},
    "istat_note_legali": {"url": "https://www.istat.it/note-legali/", "titolo": "Note legali: responsabilità e licenza", "chi": "Istat",
                          "cerca": ["Salvo diversa indicazione, tutti i contenuti pubblicati su questo sito sono soggetti alla licenza Creative Commons – Attribuzione – versione 4.0",
                                    "per qualsiasi fine, anche commerciale",
                                    "Devi riconoscere una menzione di paternità adeguata , fornire un link alla licenza e indicare se sono state effettuate delle modifiche"]},
    "l190_all4": {"url": NORMATTIVA + "/uri-res/N2Ls?urn:nir:stato:legge:2014-12-23;190", "voce": "Allegato 4",
                  "titolo": "Legge 23 dicembre 2014, n. 190, allegato 4 (regime forfetario, coefficienti di redditività)", "chi": "Normattiva",
                  "cerca": ["Codici attività ATECO 2007", "Coefficiente di redditività"]},
    "dlgs81_art1": {"url": NORMATTIVA + "/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2025-06-12;81~art1!vig=2026-01-01",
                    "titolo": "Decreto legislativo 12 giugno 2025, n. 81, art. 1 (coefficienti per i contribuenti forfetari)", "chi": "Normattiva",
                    "cerca": ["Fino alla approvazione dei nuovi coefficienti di redditività elaborati sulla base della classificazione delle attività economiche ATECO 2025",
                              "continuano a determinare il reddito imponibile applicando all'ammontare dei ricavi o dei compensi percepiti il coefficiente di redditività previsto nell'allegato 4 alla citata legge n. 190 del 2014 , individuato sulla base del codice corrispondente all'attività esercitata secondo la classificazione ATECO 2007"]},
    "tuir_art235": {"url": NORMATTIVA + "/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2026-06-19;117", "voce": "art. 235",
                    "titolo": "Decreto legislativo 19 giugno 2026, n. 117 (testo unico imposte sui redditi), art. 235", "chi": "Normattiva",
                    "cerca": ["commi da 64 a 68, legge 23 dicembre 2014, n. 190",
                              "determinano il reddito imponibile applicando all'ammontare dei ricavi o dei compensi percepiti il coefficiente di redditività nella misura indicata nell'allegato D del presente testo unico, diversificata a seconda del codice ATECO che contraddistingue l'attività esercitata",
                              "Sul reddito imponibile si applica un'imposta sostitutiva dell'imposta sui redditi, delle addizionali regionali e comunali e dell'imposta regionale sulle attività produttive",
                              "Fino alla approvazione dei nuovi coefficienti di redditività elaborati sulla base della classificazione delle attività economiche ATECO 2025",
                              "individuato sulla base del codice corrispondente all'attività esercitata secondo la classificazione ATECO 2007"]},
    "tuir_allD": {"url": NORMATTIVA + "/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2026-06-19;117", "voce": "Allegato D",
                  "titolo": "Decreto legislativo 19 giugno 2026, n. 117 (testo unico imposte sui redditi), allegato D", "chi": "Normattiva",
                  "cerca": ["Regime forfetario dei contribuenti minimi", "Codici attività ATECO 2007"]},
    "tuir_art377": {"url": NORMATTIVA + "/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2026-06-19;117", "voce": "art. 377",
                    "titolo": "Decreto legislativo 19 giugno 2026, n. 117 (testo unico imposte sui redditi), art. 377", "chi": "Normattiva",
                    "cerca": ["Le disposizioni del presente testo unico si applicano a decorrere dal 1° gennaio 2027"]},
}

# Tabella dei coefficienti come la stampano allegato 4 e allegato D: si controlla riga per riga in entrambi i testi
# (estrai.py la trasforma in regole sui codici; verifica.py la rilegge dai file salvati).
COEFFICIENTI = [
    (1, "Industrie alimentari e delle bevande", "(10-11)", "40%"),
    (2, "Commercio all'ingrosso e al dettaglio", "45 - (da 46.2 a 46.9) -(da 47.1 a 47.7) - 47.9", "40%"),
    (3, "Commercio ambulante di prodotti alimentari e bevande", "47.81", "40%"),
    (4, "Commercio ambulante di altri prodotti", "47.82 - 47.89", "54%"),
    (5, "Costruzioni e attività immobiliari", "(41-42-43) - (68)", "86%"),
    (6, "Intermediari del commercio", "46.1", "62%"),
    (7, "Attività dei servizi di alloggio e di ristorazione", "(55-56)", "40%"),
    (8, "Attività professionali, scientifiche, tecniche, sanitarie, di istruzione, servizi finanziari e assicurativi",
     "(64-65-66) - (69-70-71-72-73-74-75) - (85) - (86-87-88)", "78%"),
    (9, "Altre attività economiche", "(01-02-03) - (05-06-07-08-09) - (12-13-14-15-16-17-18-19-20-21-22-23-24-25-26-27-28-29-30-31-32-33) - (35) - "
     "(36-37-38-39) - (49-50-51-52-53) - (58-59-60-61-62-63) - (77-78-79-80-81-82) - (84) - (90-91-92-93) - (94-95-96) - (97-98) - (99)", "67%"),
]


def testo_html(t):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def compatto(t):
    """Testo senza spazi, parentesi doppie di Normattiva e trattini: serve a confrontare la tabella dei coefficienti."""
    return re.sub(r"[\s()\-–]+", "", t.replace("((", "").replace("))", "")).lower()


def apri(opener, url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with opener.open(req, timeout=60) as r:
        return r.status, r.read()


def testo_pdf(p):
    out = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, check=True).stdout
    return re.sub(r"\s+", " ", out)


def main():
    rete = "--rete" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    oggi = date.today().isoformat()
    vecchio = json.loads((DATI / "fonti.json").read_text(encoding="utf-8")) if (DATI / "fonti.json").exists() else {"file": {}, "pagine": {}}
    out = {"_nota": "Scritto da raccolta/fonti.py. I file grezzi stanno in raccolta/_grezzi/ (fuori da git): verifica.py ne ricalcola l'impronta.",
           "licenza": {"nome": "Creative Commons Attribuzione 4.0 Internazionale (CC BY 4.0)", "url": "https://creativecommons.org/licenses/by/4.0/deed.it",
                       "pagina": "istat_note_legali"},
           "file": {}, "pagine": {}, "coefficienti": [list(x) for x in COEFFICIENTI]}
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    for fid, f in FILE.items():
        dest = GREZZI / f["nome"]
        prima = vecchio["file"].get(fid, {})
        if rete or not dest.exists():
            st, b = apri(opener, f["url"])
            dest.write_bytes(b)
            letto = oggi
            time.sleep(1)
        else:
            st, b, letto = prima.get("http", 200), dest.read_bytes(), prima.get("letto_il", oggi)
        rec = {"url": f["url"], "titolo": f["titolo"], "chi": f["chi"], "pagina": f["pagina"], "file": f["nome"], "http": st,
               "byte": len(b), "sha256": hashlib.sha256(b).hexdigest(), "letto_il": letto}
        if f.get("cerca"):
            t = testo_pdf(dest)
            rec["trovate"] = {c: (re.sub(r"\s+", " ", c) in t) for c in f["cerca"]}
        out["file"][fid] = rec
        print(f"{fid}: HTTP {st}, {len(b)} byte, {rec['sha256'][:12]}")
    for pid, p in PAGINE.items():
        nome = f"pagina_{pid}.html"
        dest = GREZZI / nome
        prima = vecchio["pagine"].get(pid, {})
        if rete or not dest.exists():
            st, b = apri(opener, p["url"])
            time.sleep(1)
            if p.get("voce"):
                pag = b.decode("utf-8", errors="replace")
                voci = re.findall(r"showArticle\('([^']+)'[^>]*>([^<]*)<", pag)
                link = [html.unescape(u) for u, n in voci if n.strip() == p["voce"]]
                if not link:
                    raise SystemExit(f"{pid}: voce «{p['voce']}» non trovata nell'indice dell'atto")
                st, b = apri(opener, NORMATTIVA + link[0])
                time.sleep(1)
            dest.write_bytes(b)
            letto = oggi
        else:
            st, b, letto = prima.get("http", 200), dest.read_bytes(), prima.get("letto_il", oggi)
        t = testo_html(b.decode("utf-8", errors="replace"))
        rec = {"url": p["url"], "titolo": p["titolo"], "chi": p["chi"], "file": nome, "http": st, "byte": len(b),
               "sha256": hashlib.sha256(b).hexdigest(), "letto_il": letto, "trovate": {c: (c in t) for c in p["cerca"]}}
        if p.get("voce"):
            rec["voce"] = p["voce"]
        if p.get("data"):
            m = re.search(p["data"], t)
            rec["data_pagina"] = m.group(1) if m else None
        if pid in ("l190_all4", "tuir_allD"):
            tc = compatto(t)
            rec["coefficienti_trovati"] = {str(n): all(compatto(x) in tc for x in (g, c, k)) for n, g, c, k in COEFFICIENTI}
        out["pagine"][pid] = rec
        manca = [c[:50] for c, ok in rec["trovate"].items() if not ok]
        print(f"{pid}: HTTP {st}, frasi mancanti: {manca or 'nessuna'}" + (f", tabella: {rec['coefficienti_trovati']}" if "coefficienti_trovati" in rec else ""))
    (DATI / "fonti.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
