"""Controlli prima di pubblicare FloodCost.

Uso (dalla radice del repository, dopo python3 floodcost/genera.py):
    python3 floodcost/verifica.py            # controlli statici
    python3 floodcost/verifica.py --browser  # anche Playwright (390 e 1280 px, tema chiaro e scuro)

1. Ogni link interno (href/src) punta a un file esistente in sito/.
2. Ogni pagina con numeri cita OpenFEMA con la data di scarico e la data di riferimento delle polizze.
3. Celle piccole: nessun blocco statistico, anno di risarcimenti o voce dell'indice con meno di 10 righe nei dati pubblicati;
   nessun valore minimo/massimo pubblicato.
4. Sitemap: ogni URL esiste, ogni pagina indicizzabile (canonical) è nella sitemap; robots.txt la cita.
5. Meta di verifica Google in ogni pagina HTML; un solo <h1>, <title> e meta description in ogni pagina.
6. Il riquadro affiliati non compare finché dati/affiliati.json non ha URL.
7. Nessun nome di modelli o servizi di intelligenza artificiale nei file del progetto (cache esclusa).
8. Se la cache esiste: la mediana nazionale e i conteggi ricalcolati dai dati grezzi coincidono con nazionale.json.
Esce con codice 1 se qualcosa non va.
"""
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402

RADICE = G.RADICE
SITO = G.SITO
DATI = G.DATI
MIN = G.MIN
ERR = []


def errore(msg):
    ERR.append(msg)


class Link(HTMLParser):
    def __init__(self):
        super().__init__()
        self.link, self.h1, self.title, self.descr, self.canon, self.verifica, self.svg = [], 0, 0, 0, None, False, 0

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg -= 1

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.link.append(a["href"])
        if tag in ("img", "script", "link") and (a.get("src") or (tag == "link" and a.get("rel") in ("preload", "stylesheet"))):
            self.link.append(a.get("src") or a.get("href"))
        if tag == "h1":
            self.h1 += 1
        if tag == "svg":
            self.svg += 1
        if tag == "title" and not self.svg:
            self.title += 1
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.descr += 1
        if tag == "meta" and a.get("name") == "google-site-verification" and a.get("content") == G.GOOGLE_VERIFICA:
            self.verifica = True
        if tag == "link" and a.get("rel") == "canonical":
            self.canon = a.get("href")


def risolvi(pagina, href):
    if href.startswith(("http://", "https://", "mailto:", "data:", "#", "javascript:")):
        return None
    u = urlparse(href)
    p = unquote(u.path)
    if not p:
        return None
    base = SITO if p.startswith("/") else pagina.parent
    t = (base / p.lstrip("/")).resolve()
    if p.endswith("/"):
        t = t / "index.html"
    return t


def controlla_pagine():
    pagine = sorted(SITO.rglob("*.html"))
    canonici = set()
    data_rec = G.data_lunga(G.FONTI["scaricato_il"])
    data_rif = G.data_lunga(G.RIF)
    senza_numeri = {"about/index.html", "contact/index.html", "privacy.html", "404.html"}
    for f in pagine:
        rel = f.relative_to(SITO).as_posix()
        if rel.startswith("google"):
            continue
        t = f.read_text(encoding="utf-8")
        p = Link()
        p.feed(t)
        for href in p.link:
            dest = risolvi(f, href)
            if dest is not None and not dest.exists():
                errore(f"{rel}: link rotto {href}")
        if p.h1 != 1:
            errore(f"{rel}: {p.h1} h1")
        if p.title != 1 or p.descr != 1:
            errore(f"{rel}: title/description mancanti")
        if not p.verifica:
            errore(f"{rel}: manca la meta di verifica Google")
        if p.canon:
            canonici.add(p.canon)
        if rel not in senza_numeri:
            if "OpenFEMA" not in t or data_rec not in t or data_rif not in t:
                errore(f"{rel}: manca la fonte OpenFEMA con data di scarico ({data_rec}) e data di riferimento ({data_rif})")
            if "not a quote" not in t.lower():
                errore(f"{rel}: manca l'avviso 'not a quote'")
        if 'rel="sponsored' in t and not any(isinstance(v, dict) and v.get("url") for k, v in G.AFFILIATI.items() if not k.startswith("_")):
            errore(f"{rel}: riquadro affiliati senza URL in affiliati.json")
        if re.search(r"\b(minimum|maximum|lowest|highest) (cost|premium|policy)\b", t, re.I):
            errore(f"{rel}: pubblica un minimo o massimo?")
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    for u in locs:
        path = u[len(G.URL_SITO) + 1:]
        dest = SITO / (path if path.endswith(".html") else path + "index.html")
        if not dest.exists():
            errore(f"sitemap: {u} non esiste")
    for c in canonici - locs:
        errore(f"canonical non in sitemap: {c}")
    if f"Sitemap: {G.URL_SITO}/sitemap.xml" not in (SITO / "robots.txt").read_text():
        errore("robots.txt senza sitemap")
    print(f"Pagine HTML: {len(pagine)}; nella sitemap: {len(locs)}")
    return pagine


def controlla_blocchi(nome, B):
    """B è il blocco di un'area: controlla che nessuna cella abbia meno di MIN righe."""
    def s(x, dove):
        if x is not None and x[0] < MIN:
            errore(f"{nome} {dove}: cella con {x[0]} righe")
    s(B.get("h"), "h")
    for k, v in (B.get("z") or {}).items():
        s(v, f"zona {k}")
    for k, v in (B.get("o") or {}).items():
        s(v, f"occ {k}")
    P = B.get("prev") or {}
    s(P.get("h"), "prev h")
    for k, v in (P.get("z") or {}).items():
        s(v, f"prev zona {k}")
    C = B.get("c")
    if C:
        if C["tot"][0] < MIN:
            errore(f"{nome}: totale risarcimenti < {MIN}")
        for r in C["y"]:
            if r[1] < MIN or (r[2] is not None and r[2] < MIN):
                errore(f"{nome}: anno {r[0]} con meno di {MIN} risarcimenti")


def controlla_dati():
    controlla_blocchi("nazionale", G.NAZ)
    for k, v in G.STATI.items():
        controlla_blocchi(f"stato {k}", v)
    for k, v in G.CONTEE.items():
        controlla_blocchi(f"contea {k}", v)
        if v["h"][0] < G.FONTI["soglie"]["contea"]:
            errore(f"contea {k} sotto soglia")
    for k, v in G.ZIPS.items():
        controlla_blocchi(f"zip {k}", v)
        if v["h"][0] < G.FONTI["soglie"]["zip"]:
            errore(f"zip {k} sotto soglia")
        for c, n in v.get("comm") or []:
            if n < MIN:
                errore(f"zip {k}: comunità con {n} polizze")
    for k, v in G.INDICE["zip"].items():
        if v[2] < MIN:
            errore(f"indice zip {k}: {v[2]} polizze")
    for k, v in G.INDICE["contee_altre"].items():
        if v[2] < MIN:
            errore(f"indice contea {k}: {v[2]} polizze")
    s = json.loads((SITO / "data" / "search.json").read_text(encoding="utf-8"))
    for k, v in s["z"].items():
        if v[2] < MIN:
            errore(f"search.json zip {k}: {v[2]}")
    for x in s["c"]:
        if x[3] < MIN:
            errore(f"search.json contea {x[0]}: {x[3]}")
    for f in DATI.glob("*.json"):
        if re.search(r'"(min|max)"', f.read_text(encoding="utf-8")):
            errore(f"{f.name}: contiene min/max")


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ['edualc', 'ciporhtna', 'tpgtahc', 'ianepo', 'inimeg', 'tolipoc', 'amall', 'lartsim', 'ledom egaugnal egral']
PAROLE_VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-?\d|" + "MLL"[::-1] + r")\b", re.I)


def controlla_parole():
    for f in RADICE.rglob("*"):
        if not f.is_file() or "cache" in f.relative_to(RADICE).parts or f.suffix in (".png", ".woff2", ".gz", ".pyc"):
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        m = PAROLE_VIETATE.search(t)
        if m:
            errore(f"{f.relative_to(RADICE)}: parola vietata '{m.group(0)}'")


def controlla_cache():
    """Ricalcolo indipendente (senza pandas) della mediana nazionale delle case dai file grezzi, se presenti."""
    import csv
    import gzip
    cart = RADICE / "cache" / "polizze" / G.RIF
    if not cart.exists():
        print("Cache assente: ricalcolo dai dati grezzi saltato.")
        return
    costi, tutte = [], 0
    for f in sorted(cart.glob("*.csv.gz")):
        with gzip.open(f, "rt", encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                try:
                    c = int(float(r["policyCost"]))
                except ValueError:
                    continue
                eff, term, canc = r["policyEffectiveDate"][:10], r["policyTerminationDate"][:10], r["cancellationDateOfFloodPolicy"][:10]
                if not (eff <= G.RIF < term) or (canc and canc <= G.RIF) or c <= 0:
                    continue
                tutte += 1
                try:
                    occ = int(float(r["occupancyType"]))
                except ValueError:
                    occ = None
                if occ in (11, 12, 14, 16, 1, 2):
                    costi.append(c)
    costi.sort()
    n = len(costi)
    med = (costi[n // 2] if n % 2 else (costi[n // 2 - 1] + costi[n // 2]) / 2)
    atteso = G.NAZ["h"]
    if n != atteso[0] or round(med) != atteso[1] or tutte != G.NAZ["n"]:
        errore(f"ricalcolo nazionale: {n} case, mediana {med}, {tutte} polizze; nei dati {atteso[0]}, {atteso[1]}, {G.NAZ['n']}")
    else:
        print(f"Ricalcolo indipendente dai dati grezzi: {n:,} case, mediana ${med:,.0f}, {tutte:,} polizze: coincide.")


def browser():
    js = RADICE / "verifica_browser.js"
    r = subprocess.run(["node", str(js)], capture_output=True, text=True, timeout=900)
    print(r.stdout[-4000:])
    if r.returncode != 0:
        errore("Playwright: " + (r.stderr[-2000:] or r.stdout[-2000:]))


def main():
    controlla_pagine()
    controlla_dati()
    controlla_parole()
    controlla_cache()
    if "--browser" in sys.argv:
        browser()
    if ERR:
        print(f"{len(ERR)} PROBLEMI:")
        for e in ERR[:200]:
            print(" -", e)
        sys.exit(1)
    print("Tutti i controlli superati.")


if __name__ == "__main__":
    main()
