"""Scarica le fonti ufficiali del sito Paga CCNL e ne registra impronta, pagine e frasi controllate.

Uso (dalla radice del repository):
    python3 ccnl/raccolta/fonti.py            # scarica solo i file che mancano in raccolta/_grezzi/
    python3 ccnl/raccolta/fonti.py --rete     # riscarica tutto (controllo mensile: impronte cambiate = documento cambiato)

Scrive ccnl/dati/fonti.json: per ogni fonte indirizzo pubblico, HTTP, byte, SHA-256, numero di pagine, data di lettura
e l'esito di ogni frase cercata (le frasi che fissano divisori, mensilità e orari). Le frasi delle scansioni si cercano
nel testo letto con la lettura ottica (tesseract, italiano), salvato in raccolta/_grezzi/ocr/.
Scrive anche ccnl/dati/cnel_monitor.json: l'ultimo deposito al CNEL per ogni codice di contratto seguito.

Fonti: CNEL (archivio dei contratti, servizio pubblico usato dal sito cnel.it, licenza IODL 2.0), Ministero del Lavoro
(tabelle del costo del lavoro e tabella del lavoro domestico; robots.txt permette l'accesso), Federmeccanica
(robots: permesso, pausa di 3 secondi), Filcams CGIL. Confcommercio e FIM CISL rispondono 403: non si usano.
Nessun dato personale: si scaricano solo documenti pubblici.
"""
import base64
import hashlib
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
OCR = GREZZI / "ocr"
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (compatible; ccnl-check/1.0)"
CNEL_API = "https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica"
CNEL_OPEN = CNEL_API + "/open-data?type=ARCHIVIO_CORRENTE"
MIN = "https://www.lavoro.gov.it/temi-e-priorita-rapporti-di-lavoro-e-relazioni-industriali/focus/"
PAGINA_MIN = "https://www.lavoro.gov.it/temi-e-priorita/rapporti-di-lavoro-e-relazioni-industriali/focus-on/Analisi-economiche-costo-lavoro/Pagine/"

# Codici CNEL seguiti (controllo mensile dei depositi nuovi). I primi cinque sono i contratti del sito.
CODICI = {"H501": "Lavoro domestico", "H011": "Terziario Confcommercio", "C011": "Metalmeccanici industria",
          "K511": "Pulizia e multiservizi", "I100": "Logistica, trasporto merci e spedizione",
          "H052": "Turismo", "H05Y": "Pubblici esercizi", "F012": "Edilizia", "H442": "Studi professionali",
          "T011": "Sanità privata", "T151": "Cooperative sociali"}

# id -> definizione. "cnel": id dell'accordo nell'archivio del CNEL (il servizio restituisce il PDF dentro un JSON).
# "ocr": pagine da leggere con la lettura ottica (documenti scansionati o con cifre in caratteri codificati).
# "cerca": frasi che devono esserci (nel testo estratto o nella lettura ottica), con spazi normalizzati.
FONTI = {
    "min_domestico_2026": {
        "titolo": "Lavoro domestico: tabella dei minimi retributivi, decorrenza 1° gennaio 2026", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "tabella-lavoro-domestico-2026", "cerca": ["DECORRENZA 1° GENNAIO 2026", "Variazione indice ISTAT"]},
    "cnel_245798": {
        "titolo": "Verbale dell'11 febbraio 2026 e tabella dei minimi del lavoro domestico (deposito CNEL 245798)", "chi": "CNEL, archivio dei contratti",
        "cnel": 245798, "cerca": ["DECORRENZA 1° GENNAIO 2026"]},
    "cnel_245143": {
        "titolo": "CCNL sulla disciplina del rapporto di lavoro domestico del 28 ottobre 2025 (deposito CNEL 245143)", "chi": "CNEL, archivio dei contratti",
        "cnel": 245143,
        "cerca": ["10 ore giornaliere, non consecutive, per un totale di 54 ore settimanali", "8 ore giornaliere, non consecutive, per un totale di 40 ore settimanali",
                  "Il calcolo della retribuzione giornaliera si ottiene determinando 1/26 della retribuzione mensile",
                  "spetta al lavoratore una mensilità aggiuntiva, pari alla retribuzione globale di fatto", "1° gennaio 2027 € 30,00",
                  "1° gennaio 2028 € 15,00", "1° settembre 2028 € 15,00", "Il presente contratto decorre dal 1° novembre 2025 e scadrà il 31 ottobre 2028"]},
    "cnel_246574": {
        "titolo": "Testo unico del CCNL Terziario, distribuzione e servizi del 3 febbraio 2026 (deposito CNEL 246574)", "chi": "CNEL, archivio dei contratti",
        "cnel": 246574, "ocr": [361, 363, 364],
        "cerca": ["a) 168, per il personale la cui durata normale di lavoro è di 40 ore settimanali", "dividendo l'importo mensile per il divisore convenzionale 26",
                  "Art. 224 - Tredicesima mensilità", "Art. 225 - Quattordicesima Mensilità", "Art. 215 - Quota oraria", "Art. 214 - Quota giornaliera",
                  "è ﬁssata in 40 ore set-", "Paga base dal 1/11/2026", "Paga base dal 1/2/2027"]},
    "filcams_minimi": {
        "titolo": "Terziario Confcommercio: minimi dal 1/04/2023 al 1/02/2027", "chi": "Filcams CGIL (sindacato firmatario)",
        "url": "https://www.filcams.cgil.it/article/confcommercio_terziario/43d4ef3a-29a5-4ba3-9c2d-514d057c4bb9", "html": True,
        "cerca": ["TERZIARIO - MINIMI DAL 1/11/2026", "TERZIARIO - MINIMI DAL 1/02/2027"]},
    "filcams_rinnovo2024": {
        "titolo": "Accordo di rinnovo del CCNL Terziario del 22 marzo 2024 (testo)", "chi": "Filcams CGIL (sindacato firmatario)",
        "url": "https://www.filcams.cgil.it/GetMedia.aspx?id=fcbfb8411f16416da6954603be58d9f5&s=0",
        "cerca": ["Inizio validità: 1 aprile 2023 - Scadenza normativa: 31 marzo 2027"]},
    "min_dd94": {
        "titolo": "Decreto direttoriale n. 94 del 26 ottobre 2026: costo del lavoro dell'industria metalmeccanica", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "decreto-direttoriale-94-del-26102026",
        "cerca": ["accordo per il rinnovo del CCNL per l'industria metalmeccanica e della installazione di impianti del 22 novembre 2025",
                  "verbale d'incontro tra Federmeccanica, Assistal, FIM-CISL, FIOM CGIL e UILM-UIL del 16 giugno 2026"]},
    "min_dd94_operai": {
        "titolo": "Tabelle operai allegate al decreto n. 94 del 26 ottobre 2026 (giugno 2026)", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "tabelle-operai-all-dd-94-del-26102026", "cerca": ["GIUGNO 2026", "Retribuzione tabellare"]},
    "min_dd94_impiegati": {
        "titolo": "Tabelle impiegati allegate al decreto n. 94 del 26 ottobre 2026 (giugno 2026)", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "tabelle-impiegati-all-dd-94-del-26102026", "cerca": ["GIUGNO 2026", "Retribuzione tabellare"]},
    "fm_accordo_2025": {
        "titolo": "Ipotesi di accordo del 22 novembre 2025 per il rinnovo del CCNL metalmeccanici", "chi": "Federmeccanica",
        "url": "https://www.federmeccanica.it/images/ipotesi_di_accordo_22_novembre_2025_1.pdf", "ocr": [2], "pausa": 3,
        "cerca": ["TABELLE DEI MINIMI CONTRATTUALI", "nei mesi di giugno rispettivamente del 2026, 2027 e 2028"]},
    "cnel_157071": {
        "titolo": "CCNL 5 febbraio 2021 dell'industria metalmeccanica e della installazione di impianti (deposito CNEL 157071)", "chi": "CNEL, archivio dei contratti",
        "cnel": 157071,
        "cerca": ["si de- termina dividendo per 173 i minimi tabellari della classificazione unica", "La retribuzione oraria viene determinata sulla base del divisore 173.",
                  "Art. 7. – Tredicesima mensilità.", "confermata in 40 ore settimanali"]},
    "min_dd25": {
        "titolo": "Decreto direttoriale n. 25 del 30 marzo 2026: costo del lavoro di pulizia e multiservizi", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "decreto-direttoriale-n.-25-del-30", "cerca": ["13 giugno 2025"]},
    "min_dd25_operai": {
        "titolo": "Tabelle operai 2025-2029 allegate al decreto n. 25 del 30 marzo 2026", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "tabelle-operai-2025-2029", "cerca": ["OTTOBRE 2026", "MARZO 2029"]},
    "min_dd25_impiegati": {
        "titolo": "Tabelle impiegati 2025-2029 allegate al decreto n. 25 del 30 marzo 2026", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "tabelle-impiegati-2025-2029", "cerca": ["OTTOBRE 2026", "MARZO 2029"]},
    "cnel_234752": {
        "titolo": "Accordo integrativo del 6 agosto 2025 al rinnovo del CCNL pulizia e multiservizi, con le tabelle (deposito CNEL 234752)", "chi": "CNEL, archivio dei contratti",
        "cnel": 234752, "ocr": [1, 2, 3, 4],
        "cerca": ["è pari a complessivi 215,00 euro lordi per il periodo di vigenza"]},
    "cnel_234754": {
        "titolo": "Ipotesi di accordo del 13 giugno 2025 per il rinnovo del CCNL pulizia e multiservizi (deposito CNEL 234754)", "chi": "CNEL, archivio dei contratti",
        "cnel": 234754, "ocr": [2, 13], "cerca": ["sarà valido fino al 31 dicembre 2028"]},
    "cnel_105782": {
        "titolo": "CCNL 31 maggio 2011 per le imprese di pulizia e servizi integrati/multiservizi (deposito CNEL 105782)", "chi": "CNEL, archivio dei contratti",
        "cnel": 105782,
        "cerca": ["Ai fini della determinazione della retribuzione oraria, il divisore mensile è 173.",
                  "dividendo la retribuzione mensile per 22 nel caso di prestazione su 5 giorni settimanali e per 26 nel caso di prestazione su 6 giorni",
                  "Articolo 20 - TREDICESIMA MENSILITA'", "Articolo 21 - QUATTORDICESIMA MENSILITA'", "La durata dell'orario contrattuale di lavoro è di 40 ore settimanali"]},
    "cnel_223634": {
        "titolo": "CCNL logistica, trasporto merci e spedizione, testo del 25 settembre 2025 (deposito CNEL 223634)", "chi": "CNEL, archivio dei contratti",
        "cnel": 223634,
        "cerca": ["La retribuzione giornaliera del personale si ottiene dividendo la retribuzione mensile per 22.",
                  "giornaliera si ottiene dividendo la retribuzione mensile per 26. La retribuzione oraria si ottiene dividendo la retribuzione mensile per 168.",
                  "Art. 18 - Tredicesima mensilità", "Art. 19 - Quattordicesima mensilità", "La durata dell'orario di lavoro è di norma 39 ore settimanali",
                  "L'orario di lavoro ordinario settimanale dei conducenti è di 39 ore.", "MINIMI CONTRATTUALI MENSILI ED ELEMENTO PROFESSIONALE D'AREA (EPA)"]},
    "min_dd135": {
        "titolo": "Decreto direttoriale n. 135 del 19 dicembre 2025 e tabelle: costo del lavoro di logistica, trasporto merci e spedizione", "chi": "Ministero del Lavoro e delle politiche sociali",
        "url": MIN + "decreto-direttoriale-135-del-19", "cerca": ["Gennaio 2025, Gennaio 2026, Gennaio 2027 e Giugno 2027"]},
}

# Pagine ufficiali di settore (link "documento ufficiale" per i lettori); si controlla solo che rispondano.
PAGINE = {
    "pagina_metalm": PAGINA_MIN + "Settore-metalmeccanico-industria",
    "pagina_pulizia": PAGINA_MIN + "Settore-pulizia-e-multiservizi",
    "pagina_logistica": "https://www.lavoro.gov.it/temi-e-priorita/rapporti-di-lavoro-e-relazioni-industriali/focus/settore-della-logistica-trasporto-merci-spedizione",
    "cnel_archivio": "https://www.cnel.it/Archivio-Contratti",
}


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=240) as r:
        return r.status, r.read()


def testo_pdf(pdf):
    r = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True)
    return r.stdout


def pagine_pdf(pdf):
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    m = re.search(r"^Pages:\s+(\d+)", r.stdout, re.M)
    return int(m.group(1)) if m else None


def ocr_pagina(pdf, fid, n):
    """Lettura ottica di una pagina (300 dpi, italiano, segmentazione a colonne: psm 4). Il risultato resta in _grezzi/ocr/ e si riusa."""
    OCR.mkdir(parents=True, exist_ok=True)
    out = OCR / f"{fid}_p{n:04d}.txt"
    if out.exists() and out.stat().st_size:
        return out.read_text(encoding="utf-8")
    base = OCR / f"_tmp_{fid}_{n}"
    subprocess.run(["pdftoppm", "-r", "300", "-gray", "-f", str(n), "-l", str(n), "-png", "-singlefile", str(pdf), str(base)], check=True)
    subprocess.run(["tesseract", str(base) + ".png", str(out)[:-4], "-l", "ita", "--psm", "4"], check=True, capture_output=True)
    (Path(str(base) + ".png")).unlink()
    return out.read_text(encoding="utf-8")


def main():
    rete = "--rete" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    vecchio = json.loads((DATI / "fonti.json").read_text(encoding="utf-8")) if (DATI / "fonti.json").exists() else {"fonti": {}}
    esiti = {}
    oggi = date.today().isoformat()
    for fid, f in FONTI.items():
        est = ".html" if f.get("html") else ".pdf"
        dest = GREZZI / f"{fid}{est}"
        es = dict(vecchio["fonti"].get(fid, {}))
        if rete or not dest.exists():
            time.sleep(f.get("pausa", 1))
            try:
                if "cnel" in f:
                    http, corpo = scarica(f"{CNEL_API}/accordi/scarica/accordi/{f['cnel']}")
                    m = json.loads(corpo)["model"]
                    dest.write_bytes(base64.b64decode(m["fileContent"]))
                    es["url"] = m["fileUrl"]
                    es["nome_file"] = m["simpleFileName"]
                else:
                    http, corpo = scarica(f["url"])
                    dest.write_bytes(corpo)
                    es["url"] = f["url"]
                es["http"] = http
                es["letto_il"] = oggi
            except Exception as e:  # noqa: BLE001
                es["http"] = getattr(e, "code", None) or str(e)[:80]
                es["letto_il"] = oggi
                esiti[fid] = es
                print(f"{fid}: lettura fallita ({es['http']})")
                continue
        dati = dest.read_bytes()
        es["byte"] = len(dati)
        es["sha256"] = hashlib.sha256(dati).hexdigest()
        if est == ".pdf":
            testo = testo_pdf(dest)
            (GREZZI / f"{fid}.txt").write_text(testo, encoding="utf-8")
            es["pagine"] = pagine_pdf(dest)
            es["caratteri_testo"] = len(testo.strip())
            ocr = {n: ocr_pagina(dest, fid, n) for n in f.get("ocr", [])}
            es["ocr_pagine"] = sorted(ocr)
            pool = norm(testo + " " + " ".join(ocr.values()))
        else:
            testo = re.sub(r"<script.*?</script>|<style.*?</style>", " ", dati.decode("utf-8", "replace"), flags=re.S)
            testo = re.sub(r"<[^>]+>", " ", testo)
            import html as _h
            testo = _h.unescape(testo)
            (GREZZI / f"{fid}.txt").write_text(testo, encoding="utf-8")
            pool = norm(testo)
        if "url" not in es:
            es["url"] = f.get("url")
        es["trovate"] = {c: norm(c) in pool for c in f.get("cerca", [])}
        esiti[fid] = es
        manca = [c for c, ok in es["trovate"].items() if not ok]
        print(f"{fid}: HTTP {es.get('http')}, {es['byte']} byte, pagine {es.get('pagine')}, frasi {len(es['trovate']) - len(manca)}/{len(es['trovate'])}"
              + (f"  MANCANO {manca}" if manca else ""))
    pagine = {}
    for pid, url in PAGINE.items():
        try:
            http, _ = scarica(url)
        except Exception as e:  # noqa: BLE001
            http = getattr(e, "code", None) or str(e)[:80]
        pagine[pid] = {"url": url, "http": http, "letto_il": oggi}
        time.sleep(1)
    defs = {k: {x: v[x] for x in ("titolo", "chi", "cerca", "ocr", "cnel") if x in v} for k, v in FONTI.items()}
    (DATI / "fonti.json").write_text(json.dumps({"definizioni": defs, "fonti": esiti, "pagine": pagine}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    monitor()


def monitor():
    """Ultimo deposito al CNEL per ogni codice seguito (dal file aperto dell'archivio corrente, licenza IODL 2.0)."""
    http, corpo = scarica(CNEL_OPEN)
    (GREZZI / "cnel_open.json").write_bytes(corpo)
    righe = json.loads(corpo)["data"]
    out = {"fonte": CNEL_OPEN, "letto_il": date.today().isoformat(), "http": http, "sha256": hashlib.sha256(corpo).hexdigest(),
           "accordi_totali": len(righe), "ultimo_deposito_archivio": max(r.get("dataInserimento") or "" for r in righe), "codici": {}}
    for cod, nome in CODICI.items():
        acc = sorted([r for r in righe if r.get("codiceCcnl") == cod], key=lambda r: (r.get("dataStipula") or "", r["idAccordo"]))
        out["codici"][cod] = {"nome": nome, "accordi": len(acc), "ultimi": [
            {"id": r["idAccordo"], "stipula": r.get("dataStipula"), "decorrenza": r.get("dataDecorrenza"), "scadenza": r.get("dataScadenzaContrattuale"),
             "inserito": r.get("dataInserimento"), "tipo": r.get("tipologiaAccordo"), "titolo": r.get("titolo")} for r in acc[-3:]]}
    (DATI / "cnel_monitor.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"CNEL: {len(righe)} accordi nell'archivio corrente, ultimo inserimento {out['ultimo_deposito_archivio']}")


if __name__ == "__main__":
    main()
