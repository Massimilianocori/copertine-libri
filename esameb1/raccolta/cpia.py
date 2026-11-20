"""Controllo ripetibile delle pagine CPIA del 20/11/2026 di EsameB1 (/cpia/ e /cpia/<slug>/).

Uso (dalla radice del repository):
    python3 esameb1/raccolta/cpia.py                 # controlla anagrafe e siti dei CPIA; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/cpia.py --solo padova   # un solo CPIA
    python3 esameb1/raccolta/cpia.py --senza-anagrafe

Cosa controlla, contro dati/cpia.json:
- anagrafe del Ministero (dati aperti, file CSV in 'anagrafe.file'): per ogni CPIA il nome, la sede centrale e i centri territoriali
  (codice, nome, indirizzo, CAP, comune) e il numero delle sedi in carcere sono uguali a quelli salvati;
- sito di ogni CPIA: ogni pagina in 'fonti' si apre e ogni frase in 'citazioni' è ancora nel testo della pagina (gli spazi non contano).
  Le pagine si leggono con Playwright se è installato (molti siti scolastici scrivono il testo dopo il caricamento); senza Playwright
  si legge l'HTML e le fonti con "browser": true restano «non controllate» (il controllo lo dice, non è un errore).
Una pagina che non risponde dopo 3 prove è «non raggiunta»: è un avviso, non un errore (i siti scolastici cadono spesso); una frase che
non c'è più in una pagina che risponde è un errore. Nessun blocco viene aggirato: se un sito rifiuta la lettura, si scrive e basta.
Nessun dato personale: solo scuole.
"""
import csv
import io
import json
import os
import re
import sys
import time
import urllib.request
from html import unescape
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "dati" / "cpia.json"
AGENTE = "Mozilla/5.0 (compatible; esameb1.eu; lettura pagine pubbliche)"


def compatto(t):
    return re.sub(r"\s+", "", unescape(t))


def scarica(url, prove=3):
    for i in range(prove):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENTE}), timeout=60) as r:
                return r.status, r.read()
        except Exception as e:  # rete: si riprova, poi si segnala
            ultimo = e
            time.sleep(3)
    return 0, str(ultimo).encode()


def testo_html(b):
    h = b.decode("utf-8", "replace")
    h = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", h)
    return unescape(re.sub(r"<[^>]+>", " ", h))


def controlla_anagrafe(D, solo):
    cod, corpo = scarica(D["anagrafe"]["file"])
    if cod != 200:
        return [f"anagrafe: il file non risponde ({cod})"]
    righe = list(csv.DictReader(io.StringIO(corpo.decode("utf-8"))))
    err = []
    for c in D["cpia"]:
        if solo and c["slug"] != solo:
            continue
        mie = [x for x in righe if x["CODICEISTITUTORIFERIMENTO"] == c["codice"]]
        ora = {x["CODICESCUOLA"]: (x["DENOMINAZIONESCUOLA"].strip(), x["INDIRIZZOSCUOLA"].strip(), x["CAPSCUOLA"], x["DESCRIZIONECOMUNE"].strip())
               for x in mie if "CARCER" not in x["DESCRIZIONECARATTERISTICASCUOLA"]}
        salvate = {s["codice"]: (s["nome"], s["indirizzo"], s["cap"], s["comune"]) for s in c["sedi"]}
        if ora != salvate:
            err.append(f"{c['slug']}: le sedi dell'anagrafe sono cambiate: {sorted(set(ora.items()) ^ set(salvate.items()))[:4]}")
        if len(mie) - len(ora) != c["sedi_carcerarie"]:
            err.append(f"{c['slug']}: sedi in carcere {len(mie) - len(ora)}, salvate {c['sedi_carcerarie']}")
    return err


def main():
    arg = sys.argv[1:]
    solo = arg[arg.index("--solo") + 1] if "--solo" in arg else None
    D = json.loads(FILE.read_text(encoding="utf-8"))
    err = [] if "--senza-anagrafe" in arg else controlla_anagrafe(D, solo)
    avvisi, n_frasi, n_ok = [], 0, 0
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sync_playwright = None
    pw = sync_playwright().start() if sync_playwright else None
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")  # dietro un proxy il browser non lo legge da solo
    pagina = pw.chromium.launch(proxy={"server": proxy} if proxy else None).new_context(locale="it-IT").new_page() if pw else None
    for c in D["cpia"]:
        if solo and c["slug"] != solo:
            continue
        testi = {}
        for k, f in c["fonti"].items():
            t = None
            if pagina:
                for _ in range(3):
                    try:
                        r = pagina.goto(f["url"], wait_until="networkidle", timeout=45000)
                        if r and r.status == 200:
                            t = pagina.inner_text("body")
                            break
                    except Exception:
                        pass
                    time.sleep(3)
            elif not f.get("browser"):
                cod, corpo = scarica(f["url"])
                t = testo_html(corpo) if cod == 200 else None
            testi[k] = t
            if t is None:
                avvisi.append(f"{c['slug']}: fonte «{f['nome']}» non {'raggiunta' if pagina or not f.get('browser') else 'controllata (serve un browser)'}: {f['url']}")
            time.sleep(1)
        for voci in c["citazioni"].values():
            for x in voci:
                n_frasi += 1
                t = testi.get(x["fonte"])
                if t is None:
                    continue
                if compatto(x["testo"]) in compatto(t):
                    n_ok += 1
                else:
                    err.append(f"{c['slug']}: frase non più nella pagina «{c['fonti'][x['fonte']]['nome']}»: {x['testo'][:70]}")
    if pw:
        pw.stop()
    print(f"CPIA {len([c for c in D['cpia'] if not solo or c['slug'] == solo])}, frasi ritrovate {n_ok}/{n_frasi}, avvisi {len(avvisi)}, errori {len(err)}")
    for a in avvisi:
        print("AVVISO:", a)
    for e in err:
        print("ERRORE:", e)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
