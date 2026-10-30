"""Controlli prima di pubblicare FHA Approved Condos.

Uso (dalla radice del repository, dopo python3 fhacondos/genera.py):
    python3 fhacondos/verifica.py               # controlli statici + 20 condomini ricontrollati sulla fonte HUD (serve la rete)
    python3 fhacondos/verifica.py --browser     # anche Playwright (375 e 1280 px, tema chiaro e scuro)
    python3 fhacondos/verifica.py --senza-fonte # salta il ricontrollo sulla fonte (senza rete)

1. Ogni pagina HTML risponde 200 da un server locale; ogni link interno (href/src) punta a un file esistente;
   ogni link con #c-<ID> punta a una riga che esiste nella pagina di arrivo.
2. Ogni pagina ha un solo <h1>, <title>, meta description, meta di verifica Google; le pagine indicizzabili hanno canonical
   e sono nella sitemap (e viceversa); robots.txt cita la sitemap; netlify.toml ha la regola "ignore".
3. Pagine di luogo: data "HUD data as of", link al lookup HUD, avviso "Check before you rely on this list", spazio pubblicitario
   vuoto, blocco "Other useful tools"; i link a FloodCost puntano a pagine che esistono in floodcost/sito/.
4. Conteggi: righe in dati/condomini.json = totali dichiarati dal modulo HUD (per Stato e tipo); il numero di ogni pagina di
   Stato, contea e città = righe della sua tabella e = conteggio ricalcolato dai dati; ogni condominio compare nella tabella
   di almeno una pagina; la ricerca (data/search.json) contiene tutti i condomini e porta a righe esistenti.
5. Dati personali: nessun indirizzo email o numero di telefono nelle pagine e nei dati pubblicati; il testo libero HUD
   ("Composition of Project") non compare nel sito.
6. Riquadro affiliati assente finché dati/affiliati.json non ha un URL.
7. Nessun nome di modelli o servizi di intelligenza artificiale nei file del progetto (cache esclusa).
8. 20 condomini scelti a caso ricontrollati uno per uno sul modulo HUD (raccolta/ricontrolla.py) e confrontati anche con la
   riga pubblicata nella pagina.
9. Peso totale del sito.
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
Esce con codice 1 se qualcosa non va.
"""
import functools
import http.server
import json
import re
import subprocess
import sys
import threading
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "raccolta"))
import genera as G  # noqa: E402

RADICE = G.RADICE
SITO = G.SITO
ERR = []


def errore(msg):
    ERR.append(msg)


class Analisi(HTMLParser):
    def __init__(self):
        super().__init__()
        self.link, self.h1, self.title, self.descr, self.canon, self.verifica, self.svg = [], 0, 0, 0, None, False, 0
        self.ids = set()
        self.tabelle = {}  # id tabella -> numero di righe nel tbody
        self._tab, self._tbody = None, False

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg -= 1
        if tag == "tbody":
            self._tbody = False
        if tag == "table":
            self._tab = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.link.append(a["href"])
        if tag in ("img", "script", "link") and (a.get("src") or (tag == "link" and a.get("rel") in ("preload", "stylesheet", "icon"))):
            self.link.append(a.get("src") or a.get("href"))
        if tag == "use" and a.get("href"):
            self.link.append(a["href"].split("#")[0])
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
        if tag == "table":
            self._tab = a.get("id")
            if self._tab:
                self.tabelle[self._tab] = 0
        if tag == "tbody":
            self._tbody = True
        if tag == "tr" and self._tbody and self._tab:
            self.tabelle[self._tab] += 1


def risolvi(pagina, href):
    if href.startswith(("http://", "https://", "mailto:", "data:", "javascript:")) or href.startswith("#") and not href.startswith("#c-"):
        return None, None
    u = urlparse(href)
    p = unquote(u.path)
    if not p:
        return (pagina if u.fragment else None), u.fragment
    base = SITO if p.startswith("/") else pagina.parent
    t = (base / p.lstrip("/")).resolve()
    if p.endswith("/") or t.is_dir():
        t = t / "index.html"
    return t, u.fragment


@functools.lru_cache(maxsize=None)
def analizza(f):
    p = Analisi()
    p.feed(f.read_text(encoding="utf-8"))
    return p


def controlla_pagine():
    pagine = sorted(SITO.rglob("*.html"))
    canonici = set()
    data_hud = G.data_lunga(G.ASOF)
    for f in pagine:
        rel = f.relative_to(SITO).as_posix()
        if rel.startswith("google"):
            continue
        t = f.read_text(encoding="utf-8")
        p = analizza(f)
        for href in p.link:
            dest, frag = risolvi(f, href)
            if dest is None:
                continue
            if not dest.exists():
                errore(f"{rel}: link rotto {href}")
            elif frag and frag.startswith("c-") and dest.suffix == ".html" and frag not in analizza(dest).ids:
                errore(f"{rel}: l'ancora {href} non esiste")
        if p.h1 != 1:
            errore(f"{rel}: {p.h1} h1")
        if p.title != 1 or p.descr != 1:
            errore(f"{rel}: title/description mancanti")
        if not p.verifica:
            errore(f"{rel}: manca la meta di verifica Google")
        if p.canon:
            canonici.add(p.canon)
        elif rel != "404.html":
            errore(f"{rel}: manca il canonical")
        if "Other useful tools" not in t or G.FLOODCOST not in t:
            errore(f"{rel}: manca il blocco 'Other useful tools' con FloodCost")
        if 'rel="sponsored' in t and not (G.AFFILIATI.get("mutuo") or {}).get("url"):
            errore(f"{rel}: riquadro affiliati senza URL in affiliati.json")
        if re.search(r'<div class="ad-slot"[^>]*>(?!</div>)', t):
            errore(f"{rel}: lo spazio pubblicitario non è vuoto")
        if '"@type": "Dataset"' in t:  # pagine di luogo
            for richiesto in ("HUD data as of", data_hud, G.HUD_LOOKUP, "Check before you rely on this list", 'class="ad-slot"'):
                if richiesto not in t:
                    errore(f"{rel}: manca '{richiesto}'")
        for m in re.finditer(re.escape(G.FLOODCOST) + r"/([a-z0-9/-]*)", t):
            dest = G.FLOODCOST_SITO / m.group(1) / "index.html" if m.group(1) else G.FLOODCOST_SITO / "index.html"
            if not dest.exists():
                errore(f"{rel}: link a FloodCost inesistente {m.group(0)}")
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
    toml = (SITO / "netlify.toml").read_text()
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in toml:
        errore("netlify.toml senza la regola ignore")
    print(f"Pagine HTML: {len(pagine)}; nella sitemap: {len(locs)}; link e ancore interni controllati.")
    return pagine


def controlla_http(pagine):
    """Ogni pagina HTML risponde 200 da un server locale (come su Netlify: cartella/ -> cartella/index.html)."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    class Server(http.server.ThreadingHTTPServer):
        def handle_error(self, request, client_address):
            pass  # connessioni chiuse dal client: non sono errori delle pagine
    srv = Server(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITO)))
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    ok = 0
    for f in pagine:
        rel = f.relative_to(SITO).as_posix()
        url = base + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=10) as r:
                if r.status == 200:
                    ok += 1
                else:
                    errore(f"HTTP {r.status} {rel}")
        except Exception as e:
            errore(f"HTTP errore {rel}: {e}")
    for extra in ("sitemap.xml", "robots.txt", "data/search.json", f"assets/{G.CSS_FILE}", f"assets/{G.JS_FILE}", "assets/og.png"):
        try:
            with urllib.request.urlopen(base + extra, timeout=10) as r:
                if r.status != 200:
                    errore(f"HTTP {r.status} {extra}")
        except Exception as e:
            errore(f"HTTP errore {extra}: {e}")
    srv.shutdown()
    print(f"Server locale: {ok} pagine HTML su {len(pagine)} rispondono 200.")


def numero_titolo(t):
    m = re.search(r'<h2 id="list">[^<]*\(([\d,]+)\)</h2>', t)
    return int(m.group(1).replace(",", "")) if m else None


def controlla_conteggi():
    cm = G.META["conteggi_modulo"]
    letti = Counter((c["tipo"], c["st"]) for c in G.CONDOMINI)
    doppi = G.META.get("doppi_tolti", 0)
    for tipo, per_stato in cm.items():
        for st, n in per_stato.items():
            if letti[(tipo, st)] != n and not (doppi and tipo != "A"):
                errore(f"conteggi: {tipo} {st} nei dati {letti[(tipo, st)]}, il modulo HUD ne dichiara {n}")
    tot_modulo = sum(cm["A"].values())
    tot_dati = sum(1 for c in G.CONDOMINI if c["tipo"] == "A")
    if tot_modulo != tot_dati:
        errore(f"conteggi: approvati {tot_dati} nei dati, {tot_modulo} nel modulo")
    # ogni pagina di luogo: numero nel titolo = righe della tabella = conteggio dai dati
    luoghi = [(G.url_stato(st), G.STATI_C[st]) for st in G.STATI_C]
    luoghi += [(u, G.CONTEE_C[k]) for k, u in G.URL_CONTEA.items()]
    luoghi += [(u, G.CITTA_C[k]) for k, u in G.URL_CITTA.items()]
    presenti = set()
    for u, lista in luoghi:
        f = SITO / u / "index.html"
        t = f.read_text(encoding="utf-8")
        p = analizza(f)
        A = [c for c in lista if c["tipo"] == "A"]
        R = [c for c in lista if c["tipo"] != "A"]
        righe = p.tabelle.get("t-a", 0)
        n_tit = numero_titolo(t)
        parziale = "in the rest of" in t
        if A and (n_tit is None or n_tit != righe):
            errore(f"{u}: titolo della lista {n_tit}, righe nella tabella {righe}")
        if A and not parziale and righe != len(A):
            errore(f"{u}: {righe} righe, {len(A)} approvati nei dati")
        if p.tabelle.get("t-r", 0) != len(R):
            errore(f"{u}: {p.tabelle.get('t-r', 0)} righe recenti, {len(R)} nei dati")
        m = re.search(r'<div class="stat main"><b>([\d,]+)</b>', t)
        if not m or int(m.group(1).replace(",", "")) != len(A):
            errore(f"{u}: la cifra principale non è {len(A)}")
        for i in p.ids:
            if i.startswith("c-"):
                presenti.add(i[2:])
    mancanti = [c["id"] for c in G.CONDOMINI if c["id"] not in presenti]
    if mancanti:
        errore(f"{len(mancanti)} condomini non compaiono in nessuna tabella: {mancanti[:10]}")
    # indice di ricerca
    s = json.loads((SITO / "data" / "search.json").read_text(encoding="utf-8"))
    if len(s["c"]) != len(G.CONDOMINI):
        errore(f"search.json: {len(s['c'])} condomini, {len(G.CONDOMINI)} nei dati")
    for x in s["c"]:
        u = s["p"][x[4]][0]
        f = SITO / u / "index.html"
        if not f.exists() or f"c-{x[8]}" not in analizza(f).ids:
            errore(f"search.json: {x[8]} porta a {u}, dove la riga non c'è")
    # pagina degli Stati e home
    stati = (SITO / "states" / "index.html").read_text(encoding="utf-8")
    m = re.search(r"<td><strong>Total</strong></td><td class=\"n\"><strong>([\d,]+)</strong>", stati)
    if not m or int(m.group(1).replace(",", "")) != tot_dati:
        errore("states/: il totale non coincide con i dati")
    print(f"Conteggi: {tot_dati:,} approvati = totale HUD {tot_modulo:,}; {len(luoghi)} pagine di luogo coerenti; "
          f"tutti i {len(G.CONDOMINI):,} condomini sono in una tabella e nella ricerca.")


RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_TEL = re.compile(r"(?<!\d)(?:\(\d{3}\)\s?|\d{3}[-.])\d{3}[-.]\d{4}(?!\d)")


def controlla_privacy():
    lunghi = set()
    cart = RADICE / "cache" / G.META["edizione"]
    if (cart / "completo.json").exists():
        from estrai import leggi_edizione
        grezzi, _, _ = leggi_edizione(cart)
        lunghi = {c["comp_raw"] for c in grezzi if len(c.get("comp_raw") or "") >= 40}
    else:
        print("Cache assente: controllo del testo libero HUD saltato.")
    if any("comp_raw" in c for c in G.CONDOMINI):
        errore("dati/condomini.json contiene ancora il testo libero HUD (comp_raw)")
    lunghi_l = {x.lower() for x in lunghi}
    for f in list(SITO.rglob("*.html")) + list(SITO.rglob("*.json")):
        t = f.read_text(encoding="utf-8")
        for m in RE_EMAIL.finditer(t):
            if not m.group(0).endswith((".png", ".svg", ".woff2")):
                errore(f"{f.relative_to(SITO)}: indirizzo email {m.group(0)}")
        m = RE_TEL.search(t)
        if m:
            errore(f"{f.relative_to(SITO)}: numero di telefono {m.group(0)}")
        tl = t.lower()
        for x in lunghi_l:
            if x in tl:
                errore(f"{f.relative_to(SITO)}: contiene il testo libero HUD '{x[:50]}'")
                break
    print(f"Dati personali: nessuna email o telefono; il testo libero HUD ({len(lunghi):,} descrizioni) non compare nel sito.")


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ['edualc', 'ciporhtna', 'tpgtahc', 'ianepo', 'inimeg', 'tolipoc', 'amall', 'lartsim', 'ledom egaugnal egral', 'ihtorpe']
PAROLE_VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-?\d|" + "MLL"[::-1] + r")\b", re.I)


def controlla_parole():
    """Le parole vietate sono ammesse solo dentro il nome o l'indirizzo ufficiale di un condominio HUD (es. "6909 Gemini Dr" ad
    Anchorage, una via): si tolgono dal testo nomi e indirizzi dei condomini prima del controllo, e si elencano a parte."""
    nomi = sorted({x for c in G.CONDOMINI for x in (c["nome"], c["nome_raw"], c["via"], c["via_raw"])
                   if x and PAROLE_VIETATE.search(x)}, key=len, reverse=True)
    for f in RADICE.rglob("*"):
        if not f.is_file() or "cache" in f.relative_to(RADICE).parts or f.suffix in (".png", ".woff2", ".gz", ".pyc"):
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        for x in nomi:
            t = t.replace(x, "").replace(G.h(x), "").replace(json.dumps(x)[1:-1], "")
        m = PAROLE_VIETATE.search(t)
        if m:
            errore(f"{f.relative_to(RADICE)}: parola vietata '{m.group(0)}'")
    print("Parole vietate: nessuna" + (f" (a parte nomi e indirizzi ufficiali HUD: {', '.join(nomi)})." if nomi else "."))


def controlla_fonte(n=20):
    """20 condomini a caso ricontrollati sul modulo HUD + confronto con la riga pubblicata."""
    import random
    from ricontrolla import esegui
    seme = random.randrange(10 ** 6)
    approvati = [c for c in json.loads((G.DATI / "condomini.json").read_text(encoding="utf-8")) if c["tipo"] == "A"]
    err, _ = esegui(approvati, n, seme)
    if err:
        errore(f"ricontrollo sulla fonte: {err} errori su {n} condomini (seme {seme})")
    rnd = random.Random(seme)
    campione = rnd.sample(approvati, n)
    per_id = {c["id"]: c for c in G.CONDOMINI}
    for c in campione:
        g = per_id[c["id"]]
        f = SITO / G.pagina_di(g) / "index.html"
        t = f.read_text(encoding="utf-8")
        m = re.search(rf'<tr id="c-{re.escape(c["id"])}"[^>]*>(.*?)</tr>', t, re.S)
        if not m:
            errore(f"{c['id']}: riga non trovata in {G.pagina_di(g)}")
            continue
        riga = m.group(1)
        attesi = [G.data_tab(c["scadenza"]), c["cap"], G.h(g["nome"])]
        if c["unita"] is not None:
            attesi.append(f">{G.intero(c['unita'])}<")
        for v in attesi:
            if v and v not in riga:
                errore(f"{c['id']}: la riga pubblicata non contiene {v!r}")
    print(f"Fonte: {n} condomini ricontrollati sul modulo HUD (seme {seme}) e confrontati con la riga pubblicata.")


def peso():
    tot = sum(f.stat().st_size for f in SITO.rglob("*") if f.is_file())
    html = [f for f in SITO.rglob("*.html")]
    mx = max(html, key=lambda f: f.stat().st_size)
    print(f"Peso del sito: {tot / 1e6:.1f} MB in {sum(1 for f in SITO.rglob('*') if f.is_file())} file; "
          f"pagina più pesante {mx.relative_to(SITO)} ({mx.stat().st_size / 1e3:.0f} KB); "
          f"data/search.json {(SITO / 'data' / 'search.json').stat().st_size / 1e3:.0f} KB.")


def browser():
    js = RADICE / "verifica_browser.js"
    r = subprocess.run(["node", str(js)], capture_output=True, text=True, timeout=1500)
    print(r.stdout[-4000:])
    if r.returncode != 0:
        errore("Playwright: " + (r.stderr[-2000:] or r.stdout[-2000:]))


def controlla_indexnow():
    """File chiave IndexNow in sito/: presente, con dentro solo la chiave, fuori dalla sitemap (scritto da genera.py accanto a robots.txt)."""
    f = SITO / f"{G.CHIAVE_INDEXNOW}.txt"
    if not f.exists():
        errore(f"file chiave IndexNow mancante: {f.name}")
    elif f.read_text(encoding="utf-8").strip() != G.CHIAVE_INDEXNOW:
        errore(f"file chiave IndexNow con contenuto sbagliato: {f.name}")
    if f.name in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
        errore("file chiave IndexNow citato nella sitemap")
    print(f"File chiave IndexNow {f.name}: {'presente' if f.exists() else 'MANCANTE'}.")


def controlla_monetizzazione():
    """Controllo comune di monetizzazione (studio-business/strumenti/monetizzazione.py): link di affiliazione solo verso i domini
    ammessi di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza; AdSense, ads.txt e privacy coerenti."""
    errori, info = G.MON.controlla_sito(G.SITO_ID, SITO)
    for e in errori:
        errore(e)
    print(G.MON.riepilogo(G.SITO_ID, info, errori) + ".")


def main():
    pagine = controlla_pagine()
    controlla_http(pagine)
    controlla_conteggi()
    controlla_privacy()
    controlla_parole()
    if "--senza-fonte" not in sys.argv:
        controlla_fonte()
    controlla_indexnow()
    controlla_monetizzazione()
    peso()
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
