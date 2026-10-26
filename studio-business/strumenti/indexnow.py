#!/usr/bin/env python3
"""Invia a IndexNow (api.indexnow.org: Bing, Yandex, Naver, Seznam) gli URL delle sitemap dei siti della rete.

    python3 studio-business/strumenti/indexnow.py            # invia tutti i siti
    python3 studio-business/strumenti/indexnow.py --prova    # non invia: stampa solo i conteggi
    python3 studio-business/strumenti/indexnow.py --solo esameb1.netlify.app   # un solo sito (host)

Per ogni sito legge tutti i <loc> di sito/sitemap.xml e manda un POST JSON a https://api.indexnow.org/indexnow
({"host", "key", "keyLocation", "urlList"}) a blocchi di al massimo 10.000 URL. La chiave (pubblica) è la stessa
per tutti i siti: ogni genera.py la scrive in sito/<chiave>.txt (CHIAVE_INDEXNOW) e deve essere già online,
altrimenti il servizio risponde 403. Solo libreria standard, nessun dato personale.

Stati HTTP: 200/202 = ok (preso in carico); 400 = richiesta malformata; 403 = chiave non ancora pubblicata
(o diversa dal file online); 422 = URL non validi (non dell'host indicato); 429 = troppe richieste, riprovare più tardi.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]  # cartella del repository
CHIAVE = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE_INDEXNOW in ogni genera.py
API = "https://api.indexnow.org/indexnow"
MAX_URL = 10_000  # limite di IndexNow per ogni richiesta
SITI = [  # host -> cartella nel repository (sito/sitemap.xml)
    ("italy-strikes-today.netlify.app", "italystrikes"),
    ("tourist-tax-calculator.netlify.app", "touristtax"),
    ("visa-income-checker.netlify.app", "visaincome"),
    ("before-you-fly.netlify.app", "beforeyoufly"),
    ("esameb1.netlify.app", "esameb1"),
    ("esamidistato.netlify.app", "esamidistato"),
    ("flood-insurance-cost.netlify.app", "floodcost"),
    ("aste-giudiziarie-sconti.netlify.app", "aste"),
    ("fha-approved-condos-list.netlify.app", "fhacondos"),
    ("cruise-health-scores.netlify.app", "cruisescores"),
]
SPIEGAZIONE = {200: "ok", 202: "ok, preso in carico", 400: "richiesta malformata", 403: "chiave non ancora pubblicata (o diversa dal file online)",
               422: "URL non validi per questo host", 429: "troppe richieste: riprovare più tardi"}


def url_sitemap(cartella):
    """Tutti i <loc> di sito/sitemap.xml, senza doppioni e nell'ordine della sitemap."""
    f = RADICE / cartella / "sito" / "sitemap.xml"
    if not f.exists():
        return None
    visti, urls = set(), []
    for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", f.read_text(encoding="utf-8")):
        u = u.replace("&amp;", "&")
        if u not in visti:
            visti.add(u)
            urls.append(u)
    return urls


def invia(host, urls):
    """Un POST a IndexNow; restituisce lo stato HTTP (o il testo dell'errore di rete)."""
    corpo = json.dumps({"host": host, "key": CHIAVE, "keyLocation": f"https://{host}/{CHIAVE}.txt", "urlList": urls},
                       ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(API, data=corpo, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "rete-siti-indexnow/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except (urllib.error.URLError, OSError) as e:
        return f"errore di rete: {e}"


def main():
    argv = sys.argv[1:]
    prova = "--prova" in argv
    solo = argv[argv.index("--solo") + 1] if "--solo" in argv and argv.index("--solo") + 1 < len(argv) else None
    if "--solo" in argv and not solo:
        sys.exit("--solo vuole l'host (es. --solo esameb1.netlify.app)")
    siti = [(h, c) for h, c in SITI if not solo or h == solo or c == solo]
    if not siti:
        sys.exit(f"host sconosciuto: {solo}. Conosciuti: {', '.join(h for h, _ in SITI)}")
    problemi = 0
    for host, cartella in siti:
        urls = url_sitemap(cartella)
        if urls is None:
            print(f"{host}: sitemap mancante in {cartella}/sito/ (genera prima il sito)")
            problemi += 1
            continue
        fuori = [u for u in urls if not u.startswith(f"https://{host}/")]
        if fuori:
            print(f"{host}: {len(fuori)} URL della sitemap non sono di questo host (es. {fuori[0]}): non inviati")
            urls = [u for u in urls if u not in set(fuori)]
        chiave_locale = RADICE / cartella / "sito" / f"{CHIAVE}.txt"
        avviso = "" if chiave_locale.exists() else " (ATTENZIONE: file chiave assente in sito/, rigenera il sito)"
        blocchi = [urls[i:i + MAX_URL] for i in range(0, len(urls), MAX_URL)] or [[]]
        if prova:
            print(f"{host}: {len(urls)} URL in {len(blocchi)} blocco/i (prova, non inviato){avviso}")
            continue
        if not urls:
            print(f"{host}: nessun URL nella sitemap, niente da inviare{avviso}")
            continue
        for i, blocco in enumerate(blocchi, 1):
            stato = invia(host, blocco)
            spiega = SPIEGAZIONE.get(stato, "") if isinstance(stato, int) else ""
            ok = stato in (200, 202)
            problemi += 0 if ok else 1
            print(f"{host}: blocco {i}/{len(blocchi)}, {len(blocco)} URL -> HTTP {stato}{' = ' + spiega if spiega else ''}{avviso}")
    sys.exit(1 if problemi else 0)


if __name__ == "__main__":
    main()
