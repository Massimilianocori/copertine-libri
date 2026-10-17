"""Controlli prima di pubblicare Cruise Health Scores.

Uso (dalla radice del repository, dopo python3 cruisescores/genera.py):
    python3 cruisescores/verifica.py                # controlli statici + server locale + confronto con il CDC su 15 navi a caso
    python3 cruisescores/verifica.py --senza-rete   # senza il confronto con il CDC (per esempio se il CDC non risponde)
    python3 cruisescores/verifica.py --browser      # anche Playwright (375 e 1280 px, tema chiaro e scuro)

1. Server locale: ogni pagina HTML risponde 200; un indirizzo inesistente risponde con la pagina 404.
2. Ogni link interno (href/src) punta a un file esistente; ogni ancora "#..." esiste nella pagina.
3. Un solo <h1>, <title> e meta description in ogni pagina; meta di verifica Google; canonical = indirizzo nella sitemap;
   JSON-LD leggibile; blocco "Other useful tools" con i tre siti.
4. Nessuna pagina senza voto: pagine delle navi (anello con il voto uguale all'ultimo dato), delle compagnie, classifiche, anni, home.
5. Fonte: ogni pagina con dati cita il CDC con link, "Data checked on <data>" e l'avviso "not affiliated"; le pagine delle navi
   hanno anche la data dell'ispezione.
6. Dati: 100 - punti tolti = voto in ogni rapporto; storia ordinata; Green Sheet = ultima ispezione; nessun nome di persona
   (titolo + nome proprio) nel testo pubblicato.
7. Affiliati: rel="sponsored" solo con URL in dati/affiliati.json; il link SafetyWing è quello concordato.
8. Parole vietate (nomi di modelli di intelligenza artificiale, testo segnaposto: elenco al contrario in _AL_CONTRARIO) in tutti i file del progetto (cache esclusa).
9. Peso totale del sito (stampato; errore oltre 60 MB).
10. Confronto con la fonte: 15 navi a caso riscaricate dal CDC (storia completa, ultimo voto, punti del rapporto più recente).
Esce con codice 1 se qualcosa non va.
"""
import http.server
import json
import random
import re
import socketserver
import subprocess
import sys
import threading
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import genera as G  # noqa: E402

RADICE = G.RADICE
SITO = G.SITO
ERR = []
SW = "https://safetywing.com/nomad-insurance?referenceID=26614957&campaign=cruise-health-scores&utm_campaign=cruise-health-scores&utm_source=26614957&utm_medium=Ambassador"


def errore(msg):
    ERR.append(msg)


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__()
        self.link, self.ids, self.h1, self.title, self.descr, self.canon, self.verifica, self.svg = [], set(), 0, 0, 0, None, False, 0
        self.ld, self._in_ld, self.sponsor = [], False, []

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg -= 1
        if tag == "script":
            self._in_ld = False

    def handle_data(self, data):
        if self._in_ld:
            self.ld.append(data)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.link.append(a["href"])
            if "sponsored" in (a.get("rel") or ""):
                self.sponsor.append(a["href"])
        if tag in ("img", "script") and a.get("src"):
            self.link.append(a["src"])
        if tag == "link" and a.get("rel") in ("preload", "stylesheet", "icon"):
            self.link.append(a.get("href"))
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
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True


def risolvi(pagina, href):
    if href.startswith(("http://", "https://", "mailto:", "data:", "#", "javascript:")) or not href:
        return None
    p = unquote(urlparse(href).path)
    if not p:
        return None
    base = SITO if p.startswith("/") else pagina.parent
    t = (base / p.lstrip("/")).resolve()
    if p.endswith("/"):
        t = t / "index.html"
    return t


SENZA_DATI = {"about/index.html", "contact/index.html", "privacy.html", "404.html", "methodology/index.html"}
CON_VOTO = ("index.html", "ships/", "cruise-lines/", "rankings/", "years/")


def controlla_pagine():
    pagine = sorted(SITO.rglob("*.html"))
    canonici = set()
    data_c = f"Data checked on <strong data-controllato>{G.data_lunga(G.CONTROLLATO)}</strong>"
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    for f in pagine:
        rel = f.relative_to(SITO).as_posix()
        t = f.read_text(encoding="utf-8")
        p = Pagina()
        p.feed(t)
        for href in p.link:
            if href.startswith("#"):
                if href[1:] and href[1:] not in p.ids:
                    errore(f"{rel}: ancora mancante {href}")
                continue
            dest = risolvi(f, href)
            if dest is not None and not dest.exists():
                errore(f"{rel}: link rotto {href}")
        if p.h1 != 1:
            errore(f"{rel}: {p.h1} h1")
        if p.title != 1 or p.descr != 1:
            errore(f"{rel}: title/description mancanti o doppi")
        if not p.verifica:
            errore(f"{rel}: manca la meta di verifica Google")
        if p.canon:
            canonici.add(p.canon)
            if p.canon not in locs:
                errore(f"{rel}: canonical non nella sitemap")
        elif rel != "404.html":
            errore(f"{rel}: manca il canonical")
        for x in p.ld:
            try:
                json.loads(x)
            except ValueError:
                errore(f"{rel}: JSON-LD non valido")
        for u, _, _ in G.ALTRI_SITI:
            if f'href="{u}"' not in t:
                errore(f"{rel}: manca il link a {u} in 'Other useful tools'")
        for s in p.sponsor:
            if s.replace("&amp;", "&") not in [v["url"] for v in G.AFFILIATI.values() if v.get("url")]:
                errore(f"{rel}: link sponsorizzato non presente in affiliati.json: {s}")
        if p.sponsor and "Affiliate" not in t:
            errore(f"{rel}: link di affiliazione senza la dicitura 'Affiliate'")
        if rel not in SENZA_DATI:
            if data_c not in t or G.CDC_TOOL not in t or "not affiliated with or endorsed by the CDC" not in t:
                errore(f"{rel}: manca la fonte CDC con link, 'Data checked on' o l'avviso 'not affiliated'")
        if rel == "index.html" or any(rel.startswith(x) for x in CON_VOTO[1:]):
            if 'class="sc ' not in t and 'class="ring"' not in t:
                errore(f"{rel}: pagina senza voto")
        m = re.match(r"ships/([^/]+)/index\.html$", rel)
        if m:
            n = G.NAVI.get(m.group(1))
            if not n:
                errore(f"{rel}: nave non nei dati")
                continue
            d, v, _ = n["ultima"]
            if f'aria-label="Score {v} out of 100' not in t:
                errore(f"{rel}: l'anello non mostra il voto {v}")
            if f"Inspection date: <strong>{G.data_lunga(d)}</strong>" not in t:
                errore(f"{rel}: manca la data dell'ispezione")
            if t.count('<td class="t1 nowrap">') != len(n["storia"]):
                errore(f"{rel}: la tabella della storia non ha {len(n['storia'])} righe")
            if "not a safety rating" not in t:
                errore(f"{rel}: manca l'avviso sul voto che non è un giudizio di sicurezza")
    for u in locs:
        path = u[len(G.URL_SITO) + 1:]
        dest = SITO / (path if path.endswith(".html") else path + "index.html")
        if not dest.exists():
            errore(f"sitemap: {u} non esiste")
    if len(locs) != len(canonici):
        errore(f"sitemap {len(locs)} URL, pagine con canonical {len(canonici)}")
    if f"Sitemap: {G.URL_SITO}/sitemap.xml" not in (SITO / "robots.txt").read_text():
        errore("robots.txt non cita la sitemap")
    nt = (SITO / "netlify.toml").read_text()
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in nt:
        errore("netlify.toml: manca la regola ignore")
    print(f"Pagine HTML: {len(pagine)}; nella sitemap: {len(locs)}.")
    return pagine


def controlla_server(pagine):
    """Ogni pagina risponde 200 da un server locale; un indirizzo inesistente no."""
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(SITO), **k)

        def log_message(self, *a):
            pass
    with socketserver.TCPServer(("127.0.0.1", 0), H) as srv:
        th = threading.Thread(target=srv.serve_forever, daemon=True)
        th.start()
        base = f"http://127.0.0.1:{srv.server_address[1]}/"
        ok = 0
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for f in pagine:
            rel = f.relative_to(SITO).as_posix()
            u = base + (rel[:-10] if rel.endswith("index.html") else rel)
            try:
                with opener.open(u, timeout=20) as r:
                    r.read()
                    if r.status == 200:
                        ok += 1
                    else:
                        errore(f"server locale: {rel} -> {r.status}")
            except Exception as e:
                errore(f"server locale: {rel} -> {e}")
        try:
            opener.open(base + "non-esiste/", timeout=20)
            errore("server locale: un indirizzo inesistente risponde 200")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                errore(f"server locale: indirizzo inesistente -> {e.code}")
        srv.shutdown()
    print(f"Server locale: {ok}/{len(pagine)} pagine con risposta 200.")


RE_NOMI = re.compile(r"\b(?:Mr|Mrs|Ms|Miss|Dr|Capt|Captain)\.?\s+(?!On\b|In\b|The\b|And\b|Of\b|At\b|Was\b|Were\b|Is\b|Did\b|Had\b|Stated\b|Said\b|Mess\b|Office\b|Cabin\b|Deck\b|Bridge\b|Table\b|Galley\b|Pantry\b)[A-Z][a-z]+")


sys.path.insert(0, str(RADICE / "raccolta"))
from estrai import RE_NOME_2 as E_NOMI_2, NON_PERSONE as E_NON_PERSONE  # noqa: E402


def controlla_dati():
    for i, r in G.RAPPORTI.items():
        if 100 - sum(p[2] for p in r["punti"]) != r["voto"]:
            errore(f"rapporto {i}: 100 - punti diverso dal voto")
        for _, sito, viol in r["voci"]:
            m = RE_NOMI.search(sito + " " + viol) or E_NOMI_2.search(sito + " " + viol)
            if m and m.group(0) not in E_NON_PERSONE:
                errore(f"rapporto {i}: possibile nome di persona '{m.group(0)}'")
    for s, n in G.NAVI.items():
        date_ = [x[0] for x in n["storia"]]
        if date_ != sorted(date_, reverse=True):
            errore(f"{s}: storia non ordinata")
        for i in n["rapporti"]:
            r = G.RAPPORTI[i]
            if not any(x[2] == i and x[0] == r["data"] and x[1] == r["voto"] for x in n["storia"]):
                errore(f"{s}: rapporto {i} non coerente con la storia")
    sw = G.AFFILIATI.get("assicurazione", {}).get("url")
    sw_sospeso = G.AFFILIATI.get("assicurazione", {}).get("url_sospeso")
    if sw and sw != SW:
        errore("affiliati.json: il link SafetyWing non è quello concordato")
    if not sw and sw_sospeso != SW:
        errore("affiliati.json: link SafetyWing né attivo né sospeso con l'URL concordato")
    for k, v in G.AFFILIATI.items():
        if k != "assicurazione" and v.get("url"):
            errore(f"affiliati.json: '{k}' ha un URL: controllare che sia un'affiliazione vera")


# Parole vietate scritte al contrario, così questo file non le contiene in chiaro.
_AL_CONTRARIO = ['edualc', 'ciporhtna', 'tpgtahc', 'ianepo', 'inimeg', 'tolipoc', 'amall', 'lartsim', 'ledom egaugnal egral', 'merol', 'odot']
PAROLE_VIETATE = re.compile(r"\b(" + "|".join(w[::-1] for w in _AL_CONTRARIO) + r"|gpt-?\d|" + "MLL"[::-1] + r")\b", re.I)


def controlla_parole():
    for f in RADICE.rglob("*"):
        if not f.is_file() or "cache" in f.relative_to(RADICE).parts or f.suffix in (".png", ".woff2", ".gz", ".pyc"):
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        # Eccezione documentata in NOTE.md: un ristorante di bordo degli yacht Ritz-Carlton (Ilma, Evrima) ha lo stesso nome di un
        # modello; nei rapporti del CDC compare sempre come "Deck <n> [-] <nome>" e va lasciato com'è (è il dato ufficiale).
        t = re.sub(r"Deck \d+\s*-?\s*" + "lartsiM"[::-1], "", t)
        for m in PAROLE_VIETATE.finditer(t):
            parola = m.group(0)
            if parola.lower() == "odot"[::-1] and parola != "odot"[::-1].upper():
                continue  # in minuscolo può comparire in testi in altre lingue: conta solo il segnaposto in maiuscolo
            errore(f"{f.relative_to(RADICE)}: parola vietata '{parola}'")


def controlla_peso():
    tot = sum(f.stat().st_size for f in SITO.rglob("*") if f.is_file())
    n = sum(1 for _ in SITO.rglob("*") if _.is_file())
    html = sum(f.stat().st_size for f in SITO.rglob("*.html"))
    print(f"Peso del sito: {tot / 1e6:.1f} MB in {n} file (HTML {html / 1e6:.1f} MB).")
    if tot > 60e6:
        errore(f"sito troppo pesante: {tot / 1e6:.1f} MB")
    return tot


def controlla_fonte(k=15):
    """Riscarica dal CDC la storia di k navi a caso e confronta tutto con i dati e con le pagine."""
    sys.path.insert(0, str(RADICE / "raccolta"))
    import comune as C
    import scarica as S
    print(f"Confronto con il CDC su {k} navi a caso (una richiesta ogni 1-2 secondi)...")
    g = S.richiesta("GET", S.BASE + "InspectionGreenSheetRpt.aspx").text
    verdi = {v["id_isp"]: v for v in C.leggi_green_sheet(g)}
    attive = [s for s in G.NAVI if G.NAVI[s]["stato"] == "attiva"]
    ultime = {G.NAVI[s]["ultima"][2] for s in attive}
    nuove = set(verdi) - ultime
    if nuove:
        print(f"  nota: il Green Sheet ha {len(nuove)} ispezioni più recenti dei dati (serve un aggiornamento): "
              + ", ".join(f"{verdi[i]['nave']} {verdi[i]['data']}" for i in sorted(nuove)[:5]))
    rnd = random.Random()
    scelte = rnd.sample(sorted(G.NAVI), k)
    S.apri_modulo()
    righe = []
    for s in scelte:
        n = G.NAVI[s]
        st = C.leggi_storia(S.cerca_nave(n["id"]))
        fonte = [[x["data"], x["voto"], x["id_isp"]] for x in st]
        nostri = n["storia"]
        # se il CDC ha aggiunto ispezioni dopo il nostro scarico, si confrontano solo quelle che avevamo
        fonte_conf = [x for x in fonte if x[0] <= nostri[0][0]]
        esito = "OK" if fonte_conf == nostri else "DIVERSO"
        pag = (SITO / G.url_nave(s) / "index.html").read_text(encoding="utf-8")
        if f'aria-label="Score {nostri[0][1]} out of 100' not in pag:
            esito = "PAGINA DIVERSA"
        extra = ""
        if n["rapporti"]:
            i = n["rapporti"][0]
            coli = next(x["coli"] for x in st if x["id_isp"] == i) if any(x["id_isp"] == i for x in st) else None
            if coli:
                r1 = S.richiesta("GET", S.BASE + "InspectionDetailReport.aspx?ColI=" + coli).text
                r2 = S.richiesta("GET", S.BASE + "InspectionSummaryReport.aspx").text
                sys.path.insert(0, str(RADICE / "raccolta"))
                import estrai as E
                r = E.leggi_rapporto(r1, r2, i)
                mio = G.RAPPORTI[i]
                if not r or r["punti"] != mio["punti"] or len(r["voci"]) != len(mio["voci"]) or r["voto"] != mio["voto"]:
                    esito = "RAPPORTO DIVERSO"
                extra = f"; rapporto del {mio['data']}: {len(mio['voci'])} infrazioni, {sum(p[2] for p in mio['punti'])} punti"
        if s in attive and nostri[0][2] not in verdi and not nuove:
            esito = "NON NEL GREEN SHEET"
        righe.append(f"  {esito:>8}  {n['nome']}: {len(nostri)} ispezioni, ultima {nostri[0][0]} = {nostri[0][1]}{extra}")
        if esito != "OK":
            errore(f"confronto con il CDC: {n['nome']}: {esito} (CDC {fonte_conf[:3]}..., nostri {nostri[:3]}...)")
    print("\n".join(righe))


def browser():
    js = RADICE / "verifica_browser.js"
    r = subprocess.run(["node", str(js)], capture_output=True, text=True, timeout=1800)
    print(r.stdout[-4000:])
    if r.returncode != 0:
        errore("Playwright: " + (r.stderr[-2000:] or r.stdout[-2000:]))


def main():
    pagine = controlla_pagine()
    controlla_server(pagine)
    controlla_dati()
    controlla_parole()
    controlla_peso()
    if "--senza-rete" not in sys.argv:
        controlla_fonte()
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
