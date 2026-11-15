"""Controllo ripetibile delle pagine del 15/11/2026 di EsameB1: /dopo-esame/ (indice, una pagina per ente, «non superato»)
e /esempi/a2/, /esempi/b2/.

Uso (dalla radice del repository):
    python3 esameb1/raccolta/dopo_esame.py           # controlla fonti, frasi e file; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/dopo_esame.py --salva   # in più, se è tutto a posto, porta 'verificato_il' a oggi

Cosa controlla: ogni fonte di dati/dopo_esame.json risponde 200 e ogni frase in "citazioni" è ancora nel testo della fonte
(HTML senza tag, PDF con pdftotext; spazi e virgolette tipografiche non contano); ogni file d'esempio in "esempi" risponde 200.
Le fonti con "browser": true (sito PLIDA: il testo compare solo dopo il caricamento della pagina) si leggono con Playwright
se è installato, aprendo anche le domande chiuse; senza Playwright restano «non controllate» e il controllo lo dice (non è un errore).
Usa le funzioni di lettura di raccolta/esempi.py. Nessun dato personale.
"""
import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import esempi as E  # noqa: E402

FILE = QUI.parent / "dati" / "dopo_esame.json"


def testi_browser(urls):
    """Testo visibile delle pagine che si riempiono nel browser (FAQ PLIDA: tutte le pagine dell'elenco, ogni domanda aperta)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {}
    testi = {}
    with sync_playwright() as p:
        proxy = os.environ.get("HTTPS_PROXY")
        b = p.chromium.launch(proxy={"server": proxy} if proxy else None)
        pg = b.new_page()
        for url in urls:
            try:
                r = pg.goto(url, wait_until="networkidle", timeout=90000)
                if not r or r.status != 200:
                    continue
                pezzi = [pg.inner_text("body")]
                n_pagine = max(1, len(pg.query_selector_all("ul.pagination li.page-item a.page-link")) - 2) if "/faq" in url else 1
                for n in range(1, n_pagine + 1):
                    if n > 1:
                        pg.click(f"ul.pagination >> text='{n}'")
                        pg.wait_for_timeout(2500)
                    for i in range(len(pg.query_selector_all(".accordion-contact [aria-controls]"))):
                        h = pg.query_selector_all(".accordion-contact [aria-controls]")[i]
                        if h.get_attribute("aria-expanded") != "true":
                            h.click()
                            pg.wait_for_timeout(500)
                        pezzi.append(h.evaluate_handle("e => e.closest('.accordion-contact')").as_element().inner_text())
                testi[url] = E.normalizza(" ".join(pezzi))
            except Exception as e:  # una pagina che non si apre resta «non controllata»
                print("  browser:", url, str(e)[:80])
        b.close()
    return testi


def main(salva=False):
    D = json.loads(FILE.read_text(encoding="utf-8"))
    errori, saltate = [], []
    nel_browser = testi_browser([f["url"] for f in D["fonti"].values() if f.get("browser")])
    with tempfile.TemporaryDirectory() as cartella:
        def leggi(k):
            f = D["fonti"][k]
            return nel_browser.get(f["url"]) if f.get("browser") else E.testo_di(f["url"], cartella)
        for k, f in D["fonti"].items():
            testo = leggi(k)
            if f.get("browser") and not testo:
                saltate.append(k)
                print(f"  --  {k} (serve un browser: non controllata)")
                continue
            print(f"  {'ok ' if testo else 'NO '} {k}")
            if not testo:
                errori.append(f"{k}: fonte non leggibile ({f['url']})")
        n = 0
        for cit in D["citazioni"]:
            if cit["fonte"] in saltate:
                continue
            testo = leggi(cit["fonte"])
            if testo and E.normalizza(cit["testo"]) in testo:
                n += 1
            elif testo:
                errori.append(f"{cit['fonte']}: frase non trovata: «{cit['testo']}»")
        print(f"  frasi citate: {n}/{len(D['citazioni'])} trovate nelle fonti")
        n_file = 0
        for gruppo in D["esempi"].values():
            for x in gruppo:
                stato, h, _ = E.richiesta(x["url"], metodo="HEAD", leggi=False)
                if stato == 200:
                    n_file += 1
                else:
                    errori.append(f"file d'esempio {stato}: {x['url']}")
        print(f"  file d'esempio: {n_file} rispondono 200")
    print(f"\nFonti: {len(D['fonti'])} ({len(saltate)} non controllate senza browser); frasi: {len(D['citazioni'])}; errori: {len(errori)}")
    for e in errori:
        print("ERRORE:", e)
    if errori:
        sys.exit(1)
    if salva and not saltate:
        D["verificato_il"] = date.today().isoformat()
        FILE.write_text(json.dumps(D, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("verificato_il aggiornato")


if __name__ == "__main__":
    main("--salva" in sys.argv)
