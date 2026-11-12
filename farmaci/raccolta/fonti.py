"""Scarica i file ufficiali AIFA del sito Farmaco Equivalente e ne registra impronta, data di pubblicazione e frasi controllate.

Uso (dalla radice del repository):
    python3 farmaci/raccolta/fonti.py            # scarica solo i file che mancano in raccolta/_grezzi/
    python3 farmaci/raccolta/fonti.py --rete     # riscarica tutto (aggiornamento: impronta cambiata = lista nuova)

Scrive farmaci/dati/fonti.json: per ogni fonte indirizzo pubblico, HTTP, byte, SHA-256, data di lettura, data di
pubblicazione dichiarata da AIFA nella pagina che elenca il file, e l'esito di ogni frase cercata.

Fonte: Agenzia Italiana del Farmaco (aifa.gov.it). Licenza dei dati aperti AIFA: Creative Commons Attribuzione 4.0
(CC BY 4.0), dichiarata nella pagina «Open Data» (frase controllata qui sotto). robots.txt di aifa.gov.it: i percorsi
/documents/ e le pagine lette sono permessi. Nessun dato personale: si scaricano solo documenti pubblici.
"""
import hashlib
import html
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (compatible; farmaci-check/1.0)"
AIFA = "https://www.aifa.gov.it"

# Pagine ufficiali: si leggono per la licenza, le date di pubblicazione dei file e le frasi di legge citate nel sito.
PAGINE = {
    "open_data": {"url": AIFA + "/open-data", "titolo": "Open Data", "chi": "AIFA",
                  "cerca": ["La licenza di distribuzione dei dati utilizzata da AIFA la CC-BY (attribuzione) nella versione 4.0",
                            "anche commercialmente, con l'obbligo di citare la fonte"]},
    "pagina_trasparenza": {"url": AIFA + "/liste-di-trasparenza", "titolo": "Liste di trasparenza", "chi": "AIFA",
                           "cerca": ["AIFA rende disponibile mensilmente le liste di trasparenza dei medicinali ai sensi dell’art. 7 del D.L. 18.9.2001, n. 347 (convertito in Legge 16.11.2001, n. 405)"],
                           "data_file": r"Elenco in formato \.csv del (\d{2}/\d{2}/\d{4})"},
    "pagina_carenti": {"url": AIFA + "/farmaci-carenti", "titolo": "Farmaci carenti", "chi": "AIFA",
                       "cerca": ["si intende un medicinale temporaneamente non reperibile sul territorio nazionale in quanto il titolare AIC",
                                 "non può assicurarne una fornitura continua, rispetto al bisogno terapeutico del paziente",
                                 "potrebbe trattarsi di una indisponibilità temporanea, ovvero una discontinuità locale nella distribuzione",
                                 "il farmacista può segnalare tale mancanza alla Regione di riferimento"],
                       "data_file": r"Elenco farmaci carenti - (\d{2}/\d{2}/\d{4}) \[[\d.]+ Mb\] \[CSV\]",
                       "data_equivalenti": r"Elenco dei farmaci carenti per i quali sono disponibili equivalenti - (\d{2}/\d{2}/\d{4})",
                       "data_alternativo": r"Elenco dei farmaci carenti per i quali è disponibile trattamento alternativo - (\d{2}/\d{2}/\d{4})"},
    "pagina_classi": {"url": AIFA + "/liste-farmaci-a-h", "titolo": "Elenchi farmaci di classe A e H", "chi": "AIFA",
                      "cerca": [], "data_file": r"Liste A e H - Aggiornamento del (\d{2}/\d{2}/\d{4})"},
    "pagina_equivalenti": {"url": AIFA + "/farmaci-equivalenti1", "titolo": "Farmaci equivalenti", "chi": "AIFA",
                           "cerca": ["Il farmaco equivalente è un farmaco che ha principio attivo, forma farmaceutica, via di somministrazione, modalità di rilascio, dosaggio, numero di unità posologiche e dosi unitarie uguali a un farmaco di riferimento (“di marca”) a cui è scaduta la copertura brevettuale",
                                     "Il farmaco equivalente è riconoscibile dalla dicitura “Medicinale Equivalente” sul foglio illustrativo e sulla confezione esterna",
                                     "I medicinali inseriti in lista di trasparenza, nello stesso gruppo, sono considerati automaticamente sostituibili, salvo che l’AIFA decida diversamente, sulla base di motivazioni tecnico-scientifiche",
                                     "la differenza fra il prezzo più basso e il prezzo del farmaco prescritto è a carico del paziente",
                                     "il possesso del requisito della stessa efficacia terapeutica"]},
    "pagina_mancante": {"url": AIFA + "/cosa-fare-quando-un-farmaco-%C3%A8-mancante", "titolo": "Cosa fare quando un farmaco è mancante", "chi": "AIFA",
                        "cerca": ["Un medicinale può essere “mancante” a causa di due fenomeni distinti, che richiedono interventi diversi a supporto del paziente da parte del farmacista: carenza e indisponibilità",
                                  "che viene aggiornato almeno due volte alla settimana",
                                  "il farmacista dovrà provvedere a contattare almeno tre grossisti tra quelli a disposizione nel suo territorio",
                                  "è obbligato a fornire entro le quarantotto ore, su richiesta delle farmacie",
                                  "le confezioni importate, seppur destinate alla terapia domiciliare, non potranno essere dispensate dalle farmacie convenzionali ma esclusivamente da ASL e/o strutture competenti per territorio"]},
    # Testo vigente dell'articolo citato nel sito (Normattiva, banca dati ufficiale della normativa statale)
    "legge_art7": {"url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legge:2001-09-18;347~art7",
                   "titolo": "Decreto-legge 18 settembre 2001, n. 347, art. 7 (testo vigente)", "chi": "Normattiva, Istituto Poligrafico e Zecca dello Stato",
                   "cerca": ["Prezzo di rimborso dei farmaci di uguale composizione",
                             "sono rimborsati al farmacista dal Servizio sanitario nazionale fino alla concorrenza del prezzo più basso del corrispondente prodotto disponibile nel normale ciclo distributivo regionale",
                             "dopo aver informato l'assistito, consegna allo stesso il farmaco avente il prezzo più basso",
                             "può apporre sulla ricetta adeguata indicazione secondo la quale il farmacista",
                             "la differenza fra il prezzo più basso ed il prezzo del farmaco prescritto è a carico dell'assistito con l'eccezione dei pensionati di guerra titolari di pensioni vitalizie"]},
}

# File di dati. "pagina" e "chiave_data": dove AIFA dichiara la data del file.
FILE = {
    "trasparenza": {"url": AIFA + "/documents/20142/825643/Lista_farmaci_equivalenti.csv", "nome": "trasparenza.csv",
                    "titolo": "Lista di trasparenza (farmaci equivalenti e prezzi di riferimento), formato CSV", "chi": "AIFA",
                    "pagina": "pagina_trasparenza", "chiave_data": "data_file"},
    "carenti": {"url": AIFA + "/documents/20142/847339/elenco_medicinali_carenti.csv", "nome": "carenti.csv",
                "titolo": "Elenco completo dei farmaci carenti, formato CSV", "chi": "AIFA",
                "pagina": "pagina_carenti", "chiave_data": "data_file"},
    "carenti_equivalenti": {"url": AIFA + "/documents/20142/2171819/1_Elenco_farmaci_carenti_con_equivalenti.ods", "nome": "carenti_equivalenti.ods",
                            "titolo": "Elenco dei farmaci carenti per i quali sono disponibili equivalenti, formato ODS", "chi": "AIFA",
                            "pagina": "pagina_carenti", "chiave_data": "data_equivalenti"},
    "carenti_alternativo": {"url": AIFA + "/documents/20142/2171819/2_Elenco_farmaci_carenti_con_trattamento_alternativo.ods", "nome": "carenti_alternativo.ods",
                            "titolo": "Elenco dei farmaci carenti per i quali è disponibile un trattamento alternativo, formato ODS", "chi": "AIFA",
                            "pagina": "pagina_carenti", "chiave_data": "data_alternativo"},
    "classe_a": {"url": AIFA + "/documents/20142/3815901/Classe-A_per_principio-attivo_30-6-2026.csv", "nome": "classe_a.csv",
                 "titolo": "Elenco dei farmaci di fascia A per principio attivo, formato CSV", "chi": "AIFA",
                 "pagina": "pagina_classi", "chiave_data": "data_file"},
}


def norm(t):
    t = t.replace(" ", " ").replace("’", "’")
    return re.sub(r"\s+", " ", t).strip()


def testo_html(b):
    t = b.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))


def scarica(url, tentativi=3):
    for k in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            if k == tentativi - 1:
                raise
            print(f"  nuovo tentativo ({e})", file=sys.stderr)
            time.sleep(5)


def data_iso(gg):
    g, m, a = gg.split("/")
    return f"{a}-{m}-{g}"


def main():
    rete = "--rete" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    vecchio = {}
    if (DATI / "fonti.json").exists():
        vecchio = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))
    oggi = date.today().isoformat()
    out = {"licenza": {"nome": "Creative Commons Attribuzione 4.0 Internazionale (CC BY 4.0)", "url": "https://creativecommons.org/licenses/by/4.0/deed.it",
                       "dichiarata_in": PAGINE["open_data"]["url"]},
           "pagine": {}, "file": {}}
    testi = {}
    for pid, p in PAGINE.items():
        dest = GREZZI / f"pagina_{pid}.html"
        if rete or not dest.exists():
            print(f"pagina {pid}: {p['url']}")
            st, b = scarica(p["url"])
            dest.write_bytes(b)
            letto = oggi
            time.sleep(2)
        else:
            st, b = 200, dest.read_bytes()
            letto = vecchio.get("pagine", {}).get(pid, {}).get("letto_il", oggi)
        t = testo_html(b)
        testi[pid] = t
        voce = {"url": p["url"], "titolo": p["titolo"], "chi": p["chi"], "http": st, "letto_il": letto,
                "trovate": {c: norm(c) in t for c in p["cerca"]}}
        for k, rx in p.items():
            if k.startswith("data_"):
                m = re.search(rx, t)
                voce[k] = data_iso(m.group(1)) if m else None
        out["pagine"][pid] = voce
    for fid, f in FILE.items():
        dest = GREZZI / f["nome"]
        if rete or not dest.exists():
            print(f"file {fid}: {f['url']}")
            st, b = scarica(f["url"])
            dest.write_bytes(b)
            letto = oggi
            time.sleep(2)
        else:
            st, b = 200, dest.read_bytes()
            letto = vecchio.get("file", {}).get(fid, {}).get("letto_il", oggi)
        out["file"][fid] = {"url": f["url"], "titolo": f["titolo"], "chi": f["chi"], "file_locale": f["nome"], "http": st, "letto_il": letto,
                            "byte": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                            "pubblicato_il": out["pagine"][f["pagina"]].get(f["chiave_data"]),
                            "pagina": out["pagine"][f["pagina"]]["url"]}
    (DATI / "fonti.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for fid, x in out["file"].items():
        print(f"{fid:22} {x['byte']:>9} byte  pubblicato il {x['pubblicato_il']}  sha256 {x['sha256'][:12]}")
    for pid, x in out["pagine"].items():
        manca = [c[:60] for c, ok in x["trovate"].items() if not ok]
        if manca:
            print(f"ATTENZIONE pagina {pid}: frasi non trovate {manca}", file=sys.stderr)


if __name__ == "__main__":
    main()
