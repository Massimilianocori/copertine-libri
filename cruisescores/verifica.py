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
7. Affiliati: rel="sponsored" solo con URL in dati/affiliati.json; il link SafetyWing è quello concordato; le altre voci con URL
   solo verso i domini ammessi di monetizzazione.json (dal 30/10/2026).
8. Parole vietate (nomi di modelli di intelligenza artificiale, testo segnaposto: elenco al contrario in _AL_CONTRARIO) in tutti i file del progetto (cache esclusa).
9. Peso totale del sito (stampato; errore oltre 60 MB).
10. Confronto con la fonte: 15 navi a caso riscaricate dal CDC (storia completa, ultimo voto, punti del rapporto più recente).
Controlli del 31/10/2026 (pagine nuove e prime risposte: ogni cifra ricalcolata qui da dati/*.json, senza le funzioni di genera.py):
11. Cleanest cruise lines: finestra di 12 mesi, compagnie in classifica, ispezioni, 100, voto più basso, bocciature, media e ordine.
12. Anno su anno: per ogni anno ispezioni, 100, bocciature, epidemie e media; per ogni compagnia le due medie e la differenza.
13. Pagine delle compagnie: tabella anno per anno uguale alle ispezioni CDC della compagnia (dal 2010) e posto in classifica.
14. Epidemie: conteggi per anno e norovirus, totale per compagnia = elenco CDC, numero dell'anno nel titolo.
15. Bocciature: numero nel titolo, nell'anno in corso e nell'anno prima; somma per compagnia = totale.
16. Home e anno in corso: prima risposta (ispezioni dell'anno, data dell'ultima, media, bocciate, 100) e titolo dell'anno.
17. Sitemap: lastmod = data del controllo dei dati (fonti.json), non nel futuro; pagine nuove presenti; title ≤ 70 e description ≤ 160 caratteri.
Controlli del 27/11/2026 (epidemie per compagnia e per anno, classifica per nave; tutto ricalcolato qui, senza le funzioni di genera.py):
18. Epidemie contro la fonte: dati/epidemie.json = tabelle CDC rilette qui (dalla cache e, senza --senza-rete, dal vivo con curl):
    stesso numero di righe e, per ogni riga, compagnia, nave, date, causa e malati; malati dal 2025 = pagina CDC di ogni epidemia
    (tutte quelle in cache; dal vivo 3 a caso); le frasi del CDC citate tra virgolette ci sono ancora.
19. Pagine delle epidemie: ogni riga di ogni tabella = un'epidemia dei dati (nave, date, causa, malati, link CDC della riga);
    ogni epidemia compare una volta sola tra pagine compagnia e indice; pagina compagnia solo con almeno 4 epidemie e con tutte
    quelle dei nomi CDC che dichiara; pagine anno = epidemie dell'anno; conteggi per anno, per mese, per causa e somme dei malati;
    numero nel titolo; pagina madre: tabella per mese.
20. Classifica per nave (cleanest/dirtiest): navi, ordine, posti, voti e serie di 100 ricalcolati da navi.json e ispezioni.json.
21. Sitemap e link: le pagine nuove sono in sitemap e collegate da home, /outbreaks/, classifiche e pagine compagnia.
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
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
    # dal 30/10/2026 gli altri riquadri (es. crociere, escursioni) si possono accendere, ma solo verso i domini di monetizzazione.json
    for k, v in G.AFFILIATI.items():
        if k != "assicurazione" and v.get("url") and not G.MON.dominio_ammesso(v["url"]):
            errore(f"affiliati.json: '{k}' punta a un dominio non ammesso in monetizzazione.json")


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
    # 28/11/2026: ogni link di affiliazione ha l'evento GoatCounter <dominio>/clic/aff-<programma>-<sezione>; conteggio = monetizzazione.py
    errori, riga = G.MON.verifica_clic(G.SITO_ID, SITO, G.DOMINIO_CLIC, G.PROGRAMMI_CLIC, G.sezione_clic)
    for e in errori:
        errore(e)
    print(riga + ".")


# ---------------------------------------------------------------- controlli 11-17 (31/10/2026)
def _dati_grezzi():
    isp = json.loads((G.DATI / "ispezioni.json").read_text(encoding="utf-8"))
    comp = {k: v for k, v in json.loads((G.DATI / "compagnie.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
    ep = json.loads((G.DATI / "epidemie.json").read_text(encoding="utf-8"))
    fonti = json.loads((G.DATI / "fonti.json").read_text(encoding="utf-8"))
    return isp, comp, ep, fonti


def _slug_c(comp, cdc):
    return comp[cdc]["slug"] if cdc in comp else G.slug(cdc)


def _testo(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).replace("&amp;", "&").strip()


def _tabella(t, ident):
    """Righe con data-k o data-y della tabella <table class="lt" id=ident>: [(chiave, html della riga)]."""
    m = re.search(r'<table class="lt" id="%s".*?</table>' % re.escape(ident), t, re.S)
    if not m:
        return None
    return [(k, r) for k, r in re.findall(r'<tr data-[ky]="([^"]+)"[^>]*>(.*?)</tr>', m.group(0), re.S)]


def _cella(riga, etichetta):
    m = re.search(r'data-l="%s">(.*?)</td>' % re.escape(etichetta), riga, re.S)
    return _testo(m.group(1)) if m else None


def _f1(x):
    return f"{x:.1f}"


def _stat(voti):
    return {"n": len(voti), "media": sum(voti) / len(voti), "cento": voti.count(100), "min": min(voti), "boc": sum(1 for v in voti if v <= 85)}


def _leggi(rel):
    f = SITO / rel
    if not f.exists():
        errore(f"{rel}: pagina mancante")
        return ""
    return f.read_text(encoding="utf-8")


def controlla_classifiche():
    isp, comp, ep, fonti = _dati_grezzi()
    anno = int(fonti["green_sheet"]["ultima_ispezione"][:4])
    fine = max(r[0] for r in isp)
    from datetime import date, timedelta
    f = date.fromisoformat(fine)
    try:
        inizio = (f.replace(year=f.year - 1) + timedelta(days=1)).isoformat()
    except ValueError:
        inizio = (f.replace(year=f.year - 1, day=28) + timedelta(days=1)).isoformat()
    n_contr = 0
    # 11. cleanest cruise lines
    t = _leggi("rankings/cleanest-cruise-lines/index.html")
    per_l = {}
    for r in isp:
        if inizio <= r[0] <= fine:
            per_l.setdefault(_slug_c(comp, r[3]), []).append(r[1])
    attese = {k: _stat(v) for k, v in per_l.items() if len(v) >= G.MIN_ISP_CLASSIFICA}
    righe = _tabella(t, "classifica") or []
    if {k for k, _ in righe} != set(attese):
        errore(f"cleanest: compagnie in classifica diverse ({len(righe)} pagina, {len(attese)} attese)")
    medie_pag = []
    for k, riga in righe:
        s = attese.get(k)
        if not s:
            continue
        for et, v in (("Inspections", s["n"]), ("Perfect 100s", s["cento"]), ("Lowest", s["min"]), ("Failed", s["boc"])):
            if _cella(riga, et) != str(v):
                errore(f"cleanest {k}: {et} {_cella(riga, et)} invece di {v}")
        if _cella(riga, "Average") != _f1(s["media"]):
            errore(f"cleanest {k}: media {_cella(riga, 'Average')} invece di {_f1(s['media'])}")
        medie_pag.append(round(s["media"], 1))
        n_contr += 1
    if medie_pag != sorted(medie_pag, reverse=True):
        errore("cleanest: classifica non ordinata dalla media più alta")
    if f"from {G.data_lunga(inizio)} to {G.data_lunga(fine)}" not in t:
        errore("cleanest: finestra di 12 mesi non scritta o sbagliata")
    if f"<title>Cleanest Cruise Lines {anno}:" not in t:
        errore("cleanest: titolo senza l'anno")
    # 12. anno su anno
    t = _leggi("rankings/year-over-year/index.html")
    righe = _tabella(t, "anni") or []
    anni_att = [y for y in range(2023, anno + 1) if any(r[0][:4] == str(y) for r in isp)]
    if sorted(int(k) for k, _ in righe) != anni_att:
        errore(f"anno su anno: anni {[k for k, _ in righe]} invece di {anni_att}")
    for k, riga in righe:
        v = [r[1] for r in isp if r[0][:4] == k]
        s = _stat(v)
        n_ep = sum(1 for e in ep if str(e["anno"]) == k)
        for et, val in (("Inspections", s["n"]), ("Failed", s["boc"]), ("Outbreaks", n_ep)):
            if _cella(riga, et) != str(val):
                errore(f"anno su anno {k}: {et} {_cella(riga, et)} invece di {val}")
        if not (_cella(riga, "Perfect 100s") or "").startswith(f"{s['cento']} ("):
            errore(f"anno su anno {k}: 100 sbagliati")
        if _cella(riga, "Average") != _f1(s["media"]):
            errore(f"anno su anno {k}: media sbagliata")
        n_contr += 1
    for k, riga in _tabella(t, "linee") or []:
        vy = [r[1] for r in isp if r[0][:4] == str(anno) and _slug_c(comp, r[3]) == k]
        vp = [r[1] for r in isp if r[0][:4] == str(anno - 1) and _slug_c(comp, r[3]) == k]
        if len(vy) < G.MIN_ISP_CONFRONTO or len(vp) < G.MIN_ISP_CONFRONTO:
            errore(f"anno su anno {k}: meno di {G.MIN_ISP_CONFRONTO} ispezioni in un anno")
            continue
        my, mp = round(sum(vy) / len(vy), 1), round(sum(vp) / len(vp), 1)
        if _cella(riga, f"{anno} average") != f"{my:.1f} ({len(vy)})" or _cella(riga, f"{anno - 1} average") != f"{mp:.1f} ({len(vp)})":
            errore(f"anno su anno {k}: medie della compagnia sbagliate")
        d = round(my - mp, 1)
        if _cella(riga, "Change") != (f"+{d:.1f}" if d > 0 else f"−{abs(d):.1f}" if d < 0 else "0.0"):
            errore(f"anno su anno {k}: differenza sbagliata")
        n_contr += 1
    # 13. pagine delle compagnie: anno per anno
    for d in sorted((SITO / "cruise-lines").iterdir()):
        if not (d / "index.html").exists():
            continue
        t = (d / "index.html").read_text(encoding="utf-8")
        righe = _tabella(t, "anno-per-anno")
        per_anno = {}
        for r in isp:
            if _slug_c(comp, r[3]) == d.name and int(r[0][:4]) >= 2010:
                per_anno.setdefault(r[0][:4], []).append(r[1])
        if righe is None:
            if per_anno:
                errore(f"cruise-lines/{d.name}: manca la tabella anno per anno")
            continue
        if sorted(k for k, _ in righe) != sorted(per_anno):
            errore(f"cruise-lines/{d.name}: anni della tabella diversi dai dati")
        for k, riga in righe:
            s = _stat(per_anno.get(k, [0]))
            for et, val in (("Inspections", s["n"]), ("Perfect 100s", s["cento"]), ("Lowest", s["min"]), ("Failed", s["boc"]), ("Average", _f1(s["media"]))):
                if _cella(riga, et) != str(val):
                    errore(f"cruise-lines/{d.name} {k}: {et} {_cella(riga, et)} invece di {val}")
            n_contr += 1
        pos = re.search(r"#(\d+) of (\d+) cruise lines", t)
        if pos:
            medie = sorted((round(s["media"], 1) for s in attese.values()), reverse=True)
            mia = attese.get(d.name)
            if not mia or int(pos.group(2)) != len(attese) or int(pos.group(1)) != 1 + sum(1 for m in medie if m > round(mia["media"], 1)):
                errore(f"cruise-lines/{d.name}: posto in classifica sbagliato")
    # 14. epidemie
    t = _leggi("outbreaks/index.html")
    for k, riga in _tabella(t, "per-anno") or []:
        lista = [e for e in ep if str(e["anno"]) == k]
        noro = sum(1 for e in lista if "norovirus" in (e["agente"] or "").lower())
        if _cella(riga, "Outbreaks") != str(len(lista)) or _cella(riga, "Norovirus") != str(noro):
            errore(f"epidemie {k}: conteggi sbagliati")
        n_contr += 1
    a_ult = max(e["anno"] for e in ep)
    n_ult = sum(1 for e in ep if e["anno"] == a_ult)
    if a_ult == anno and f"<title>Cruise Ship Norovirus &amp; GI Outbreaks {a_ult}: CDC List ({n_ult} So Far)</title>" not in t:
        errore("epidemie: titolo con il numero dell'anno sbagliato")
    tot_l = sum(int(x) for x in re.findall(r'data-l="Since \d{4}">(\d+)</td>', t))
    if tot_l != len(ep):
        errore(f"epidemie: somma per compagnia {tot_l} invece di {len(ep)}")
    # 15. bocciature
    t = _leggi("rankings/failed-inspections/index.html")
    boc = [r for r in isp if r[1] <= 85]
    y0 = min(int(r[0][:4]) for r in boc)
    if f"<title>Cruise Ships That Failed a CDC Inspection: All {len(boc)} Since {y0}</title>" not in t:
        errore("bocciature: titolo con il numero sbagliato")
    n_a = sum(1 for r in boc if r[0][:4] == str(anno))
    n_p = sum(1 for r in boc if r[0][:4] == str(anno - 1))
    if f"{n_a} in {anno} so far and {n_p} in {anno - 1}" not in t:
        errore("bocciature: conteggi dell'anno nella prima risposta sbagliati")
    if sum(int(x) for x in re.findall(r'data-l="Failed inspections">(\d+)</td>', t)) != len(boc):
        errore("bocciature: la somma per compagnia non è il totale")
    # 16. home e anno in corso
    t = _leggi("index.html")
    va = [r[1] for r in isp if r[0][:4] == str(anno)]
    attesa = (f"the CDC has published {len(va)} inspections for {anno} so far, the most recent on {G.data_lunga(fine)}")
    if attesa not in t:
        errore("home: prima risposta con ispezioni dell'anno o data sbagliate")
    if (f"Average {anno} score: {_f1(sum(va) / len(va))} out of 100; {sum(1 for v in va if v <= 85)} failed (85 or lower) and "
            f"{va.count(100)} scored a perfect 100") not in t:
        errore("home: media, bocciate o 100 della prima risposta sbagliati")
    if f"<title>CDC Cruise Ship Inspections List {anno}: All {len(va)} Scores</title>" not in _leggi(f"years/{anno}/index.html"):
        errore(f"years/{anno}: titolo con il numero di ispezioni sbagliato")
    print(f"Classifiche, confronti e prime risposte: {n_contr} righe ricalcolate dai dati CDC.")


# ---------------------------------------------------------------- 18-21: epidemie per compagnia/anno e classifica per nave (27/11/2026)
CDC_EP = "https://www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/"
TABELLE_EP = {"epidemie": CDC_EP + "index.html", "epidemie-2025-2024": CDC_EP + "earlier-outbreaks.html", "epidemie-2023": CDC_EP + "earlier-outbreaks-2023.html"}
FRASI_CDC = ("on voyages including both U.S. and foreign ports", "3% or more of passengers or crew reporting symptoms of GI illness to the ship's medical staff",
             "other outbreaks of public health significance")
RE_CONTO = r"Number of %s who reported being ill[^:]*:\s*(\d[\d,]* of \d[\d,]* \([\d.]+ ?%%\))"


def _righe_cdc(testo):
    """Lettura indipendente di una pagina CDC con le tabelle delle epidemie: [(anno, compagnia, nave, date, causa, passeggeri, equipaggio, url)]."""
    import html as _h
    out = []
    for tab in re.findall(r"<table.*?</table>", testo, re.S):
        cap = re.search(r"<caption.*?</caption>", tab, re.S)
        anno = re.search(r"20\d\d", re.sub(r"<[^>]+>", "", cap.group(0))) if cap else None
        if not anno:
            continue
        for riga in re.findall(r"<tr.*?</tr>", tab, re.S):
            c = [re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", "", x))).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", riga, re.S)]
            if len(c) < 4 or c[0].lower() == "cruise line" or not c[1]:
                continue
            link = re.search(r'href="([^"]+)"', riga)
            url = ("https://www.cdc.gov" + link.group(1) if link and link.group(1).startswith("/") else (link.group(1) if link else ""))
            if len(c) >= 7:
                out.append((int(anno.group(0)), c[0], c[1], c[2], c[4], c[5], c[6], url))
            else:
                out.append((int(anno.group(0)), c[0], c[1], c[2], c[3], None, None, url))
    return out


def _curl(url):
    """www.cdc.gov a volte non risponde entro il tempo: tre tentativi, uno alla volta, con una pausa."""
    import time
    for tentativo in range(3):
        if tentativo:
            time.sleep(5)
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "120", "-w", "\n%{http_code}", url], capture_output=True)
        corpo, _, codice = r.stdout.decode("utf-8", errors="replace").rpartition("\n")
        if codice.strip() == "200":
            return corpo
    return None


def _conti_pagina(testo):
    import html as _h
    x = re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", testo)))
    p, c = re.search(RE_CONTO % "passengers", x), re.search(RE_CONTO % "crew", x)
    return (p.group(1) if p else None, c.group(1) if c else None)


def _confronta_tabelle(ep, pagine, dove):
    """pagine = {nome: html}. Le righe CDC (senza doppioni tra le pagine: la tabella 2023 compare due volte) devono essere quelle dei dati."""
    viste, righe = set(), []
    for nome in ("epidemie", "epidemie-2025-2024", "epidemie-2023"):
        if nome not in pagine:
            continue
        rr = _righe_cdc(pagine[nome])
        for a in sorted({r[0] for r in rr}):
            if a not in viste:
                righe += [r for r in rr if r[0] == a]
        viste |= {r[0] for r in rr}
    if len(righe) != len(ep):
        errore(f"epidemie ({dove}): il CDC elenca {len(righe)} epidemie, i dati {len(ep)}: rilanciare scarica.py --epidemie ed estrai.py")
    dati = [(e["anno"], e["compagnia"], e["nave"], e["date"], e["agente"], e["url"]) for e in ep]
    for r in righe:
        chiave = (r[0], r[1], r[2], r[3], r[4], r[7])
        if chiave not in dati:
            errore(f"epidemie ({dove}): riga CDC non nei dati: {chiave[:5]}")
            continue
        e = ep[dati.index(chiave)]
        if r[5] is not None and (e.get("passeggeri"), e.get("equipaggio")) != (r[5], r[6]):
            errore(f"epidemie ({dove}): malati di {r[2]} {r[3]}: CDC {r[5]} / {r[6]}, dati {e.get('passeggeri')} / {e.get('equipaggio')}")
    for d in dati:
        if d not in [(r[0], r[1], r[2], r[3], r[4], r[7]) for r in righe]:
            errore(f"epidemie ({dove}): nei dati ma non nelle tabelle CDC: {d[:5]}")
    return len(righe)


def controlla_epidemie_fonte():
    """18. dati/epidemie.json contro le pagine del CDC (cache; dal vivo se non c'è --senza-rete)."""
    _, _, ep, _ = _dati_grezzi()
    cache = RADICE / "cache"
    pag = {n: (cache / "info" / f"{n}.html").read_text(encoding="utf-8", errors="replace") for n in TABELLE_EP if (cache / "info" / f"{n}.html").exists()}
    if len(pag) == 3:
        n = _confronta_tabelle(ep, pag, "cache")
        for fr in FRASI_CDC:
            if fr not in pag["epidemie"].replace("’", "'"):
                errore(f"epidemie: la pagina CDC non dice più «{fr}» (frase citata nelle pagine)")
        fatti = 0
        for e in ep:
            f = cache / "epidemie" / e["url"].rsplit("/", 1)[-1] if e["url"] else None
            if f and f.exists():
                if _conti_pagina(f.read_text(encoding="utf-8", errors="replace")) != (e.get("passeggeri"), e.get("equipaggio")):
                    errore(f"epidemie: malati di {e['nave']} {e['date']} diversi dalla pagina CDC in cache ({f.name})")
                fatti += 1
        print(f"Epidemie contro la cache CDC: {n} righe, {fatti} pagine di dettaglio.")
    else:
        print("Epidemie: cache CDC assente (confronto con la cache saltato).")
    for e in ep:
        if e["anno"] >= 2025 and not (e.get("passeggeri") and e.get("equipaggio")):
            errore(f"epidemie: {e['nave']} {e['date']} senza conteggio dei malati (pagina CDC non letta: rilanciare scarica.py --epidemie)")
        for campo in ("passeggeri", "equipaggio"):
            if e.get(campo) and not re.fullmatch(r"[\d,]+ of [\d,]+ \([\d.]+ ?%\)", e[campo]):
                errore(f"epidemie: {e['nave']} {e['date']}: {campo} non leggibile «{e[campo]}»")
    if "--senza-rete" in sys.argv:
        return
    vive = {n: _curl(u) for n, u in TABELLE_EP.items()}
    if not all(vive.values()):
        errore("epidemie: una tabella CDC non risponde (curl): confronto dal vivo non fatto")
        return
    n = _confronta_tabelle(ep, vive, "CDC dal vivo")
    con_url = [e for e in ep if e["url"]]
    for e in random.sample(con_url, min(3, len(con_url))):
        import time
        time.sleep(1.5)
        tx = _curl(e["url"])
        if tx is None:
            errore(f"epidemie: la pagina CDC {e['url']} non risponde")
        elif _conti_pagina(tx) != (e.get("passeggeri"), e.get("equipaggio")):
            errore(f"epidemie: malati di {e['nave']} {e['date']} diversi dalla pagina CDC dal vivo: {_conti_pagina(tx)}")
    print(f"Epidemie contro il CDC dal vivo: {n} righe uguali, 3 pagine di dettaglio a caso.")


def _righe_epid(t, ident):
    """Righe di una tabella delle epidemie: [(nave, compagnia o None, date, causa, passeggeri, equipaggio, href)]."""
    import html as _h
    m = re.search(r'<table class="lt" id="%s".*?</table>' % re.escape(ident), t, re.S)
    if not m:
        return None
    out = []
    for r in re.findall(r"<tr data-inizio=.*?</tr>", m.group(0), re.S):
        prima = re.search(r'<td class="t1">(.*?)</td>', r, re.S).group(1)
        nave, _, comp = prima.partition("<br>")
        href = re.search(r'data-l="Source"><a href="([^"]+)"', r)
        tx = lambda x: _h.unescape(_testo(x))  # noqa: E731
        out.append((tx(nave), tx(comp) if comp else None, _h.unescape(_cella(r, "Sailing dates")), _h.unescape(_cella(r, "Cause (CDC)")),
                    _h.unescape(_cella(r, "Passengers ill")), _h.unescape(_cella(r, "Crew ill")), _h.unescape(href.group(1)) if href else ""))
    return out


def _mese_inizio(e):
    m = re.match(r"\s*(\d{1,2})/\d{1,2}(?:/(\d{4}))?", e["date"])
    return (int(m.group(2) or e["anno"]), int(m.group(1)))


def _n(x):
    m = re.match(r"([\d,]+) of", x or "")
    return int(m.group(1).replace(",", "")) if m else None


def controlla_epidemie_pagine():
    """19 e 21. Pagine delle epidemie per compagnia e per anno, indice, tabella per mese della pagina madre."""
    _, _, ep, _ = _dati_grezzi()
    a_ult = max(e["anno"] for e in ep)
    anni = sorted({e["anno"] for e in ep})
    tab_anno = {2023: CDC_EP + "earlier-outbreaks-2023.html"}

    def attesa(e, con_comp):
        href = e["url"] or (CDC_EP + "index.html" if e["anno"] == a_ult else tab_anno.get(e["anno"], CDC_EP + "earlier-outbreaks.html"))
        return (e["nave"], e["compagnia"] if con_comp else None, e["date"], e["agente"], e.get("passeggeri") or "not given", e.get("equipaggio") or "not given", href)

    def somma(t, lista, rel):
        m = re.search(r"<strong>([\d,]+) passengers and ([\d,]+) crew members</strong>", t)
        sp = sum(_n(e.get("passeggeri")) or 0 for e in lista)
        sc = sum(_n(e.get("equipaggio")) or 0 for e in lista)
        if not m or (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))) != (sp, sc):
            errore(f"{rel}: somma dei malati sbagliata (attesi {sp} passeggeri e {sc} equipaggio)")

    viste = []  # ogni epidemia deve comparire una volta sola tra pagine compagnia e tabella "altre" dell'indice
    cartella = SITO / "outbreaks" / "cruise-lines"
    pagine_linea = sorted(d for d in cartella.iterdir() if d.is_dir()) if cartella.exists() else []
    if not pagine_linea:
        errore("outbreaks/cruise-lines/: nessuna pagina compagnia")
    for d in pagine_linea:
        rel = f"outbreaks/cruise-lines/{d.name}/index.html"
        t = _leggi(rel)
        righe = _righe_epid(t, "epidemie") or []
        import html as _h
        nomi = re.search(r"The CDC names this cruise line as: (.*?)\. An outbreak", t)
        nomi = set(re.findall(r"“([^”]+)”", _h.unescape(nomi.group(1)))) if nomi else set()
        lista = [e for e in ep if e["compagnia"] in nomi]
        if len(lista) < 4:
            errore(f"{rel}: pagina con meno di 4 epidemie ({len(lista)})")
        if righe != [attesa(e, False) for e in lista]:
            errore(f"{rel}: le righe non sono le epidemie CDC di {sorted(nomi)} ({len(righe)} righe, {len(lista)} nei dati)")
        ti = _h.unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        if not ti.endswith(f"Norovirus & GI Outbreaks Since {anni[0]}: CDC List"):
            errore(f"{rel}: titolo inatteso «{ti}»")
        if f"posted <strong>{len(lista)} gastrointestinal illness outbreak" not in t:
            errore(f"{rel}: numero di epidemie nella prima risposta diverso da {len(lista)}")
        for k, riga in _tabella(t, "per-anno") or []:
            ll = [e for e in lista if str(e["anno"]) == k]
            noro = sum(1 for e in ll if "norovirus" in e["agente"].lower())
            if (_cella(riga, "Outbreaks"), _cella(riga, "Norovirus"), _cella(riga, "Other or unknown cause")) != (str(len(ll)), str(noro), str(len(ll) - noro)):
                errore(f"{rel}: anno {k} con conteggi sbagliati")
        if len(_tabella(t, "per-anno") or []) != len(anni):
            errore(f"{rel}: tabella per anno incompleta")
        somma(t, lista, rel)
        viste += lista
        if f"<loc>{G.URL_SITO}/outbreaks/cruise-lines/{d.name}/</loc>" not in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
            errore(f"sitemap: manca outbreaks/cruise-lines/{d.name}/")
    # indice
    rel = "outbreaks/cruise-lines/index.html"
    t = _leggi(rel)
    altre = _righe_epid(t, "altre") or []
    resto = [e for e in ep if e not in viste]
    if altre != [attesa(e, True) for e in resto]:
        errore(f"{rel}: la tabella delle compagnie senza pagina non corrisponde ({len(altre)} righe, {len(resto)} epidemie attese)")
    if len(viste) + len(altre) != len(ep) or any(viste.count(e) != 1 for e in viste):
        errore(f"{rel}: le epidemie non compaiono tutte una volta sola ({len(viste)} + {len(altre)} su {len(ep)})")
    from collections import Counter
    for nome_c, quante in Counter(e["compagnia"] for e in resto).items():
        if quante >= 4:
            errore(f"{rel}: {nome_c} ha {quante} epidemie ma nessuna pagina")
    righe_l = _tabella(t, "linee") or []
    if sum(int(_cella(r, f"Outbreaks since {anni[0]}")) for _, r in righe_l) != len(ep):
        errore(f"{rel}: la somma per compagnia non è {len(ep)}")
    if sum(int(_cella(r, "Norovirus")) for _, r in righe_l) != sum(1 for e in ep if "norovirus" in e["agente"].lower()):
        errore(f"{rel}: somma dei norovirus sbagliata")
    for y in anni:
        if sum(int(_cella(r, str(y))) for _, r in righe_l) != sum(1 for e in ep if e["anno"] == y):
            errore(f"{rel}: colonna {y} sbagliata")
    for k, r in righe_l:
        if (SITO / "outbreaks" / "cruise-lines" / k).is_dir():
            tl = _leggi(f"outbreaks/cruise-lines/{k}/index.html")
            if len(_righe_epid(tl, "epidemie") or []) != int(_cella(r, f"Outbreaks since {anni[0]}")):
                errore(f"{rel}: {k} ha un numero diverso dalla sua pagina")
    if f"posted <strong>{len(ep)} gastrointestinal illness outbreaks on cruise ships</strong>" not in t or f"on ships of {len(righe_l)} cruise lines" not in t:
        errore(f"{rel}: prima risposta con numeri sbagliati")
    # anni
    for y in anni:
        rel = f"outbreaks/{y}/index.html"
        if y == a_ult:
            if (SITO / rel).exists():
                errore(f"{rel}: l'anno più recente sta su /outbreaks/, non deve avere una pagina sua")
            continue
        t = _leggi(rel)
        lista = [e for e in ep if e["anno"] == y]
        if (_righe_epid(t, "epidemie") or []) != [attesa(e, True) for e in lista]:
            errore(f"{rel}: le righe non sono le {len(lista)} epidemie CDC del {y}")
        if f"<title>Cruise Ship Norovirus &amp; GI Outbreaks in {y}: All {len(lista)} on the CDC List</title>" not in t:
            errore(f"{rel}: titolo con il numero sbagliato")
        mesi = Counter(_mese_inizio(e) for e in lista)
        for m, riga in re.findall(r'<tr data-m="(\d+)">(.*?)</tr>', t, re.S):
            if _cella(riga, str(y)) != str(mesi.get((y, int(m)), 0)):
                errore(f"{rel}: mese {m} sbagliato")
        if sum(mesi.values()) != len(lista):
            errore(f"{rel}: {len(lista) - sum(mesi.values())} epidemie cominciano in un altro anno: tabella per mese incompleta")
        somma(t, lista, rel)
        if f"<loc>{G.URL_SITO}/outbreaks/{y}/</loc>" not in (SITO / "sitemap.xml").read_text(encoding="utf-8"):
            errore(f"sitemap: manca outbreaks/{y}/")
    # pagina madre: tabella per mese (tutti gli anni)
    t = _leggi("outbreaks/index.html")
    mesi = Counter(_mese_inizio(e) for e in ep)
    m_tab = re.search(r'<table class="lt" id="mesi".*?</table>', t, re.S)
    if not m_tab:
        errore("outbreaks/: manca la tabella per mese")
    else:
        tot = 0
        for m, riga in re.findall(r'<tr data-m="(\d+)">(.*?)</tr>', m_tab.group(0), re.S):
            for y in anni:
                if _cella(riga, str(y)) != str(mesi.get((y, int(m)), 0)):
                    errore(f"outbreaks/: mese {m} del {y} sbagliato")
            tot += int(_cella(riga, "Total"))
        if tot != len(ep):
            errore(f"outbreaks/: la tabella per mese somma {tot}, non {len(ep)}")
    # 21. link verso le pagine nuove
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    for u in ("outbreaks/cruise-lines/", "rankings/cleanest-dirtiest-cruise-ships/"):
        if f"<loc>{G.URL_SITO}/{u}</loc>" not in sm:
            errore(f"sitemap: manca {u}")
    for rel, link in (("index.html", "/outbreaks/cruise-lines/"), ("index.html", "/rankings/cleanest-dirtiest-cruise-ships/"),
                      ("outbreaks/index.html", "/outbreaks/cruise-lines/"), ("rankings/index.html", "/rankings/cleanest-dirtiest-cruise-ships/"),
                      ("rankings/cleanest-cruise-lines/index.html", "/rankings/cleanest-dirtiest-cruise-ships/")):
        if f'href="{link}"' not in _leggi(rel):
            errore(f"{rel}: manca il link a {link}")
    for d in pagine_linea:
        if (SITO / "cruise-lines" / d.name).is_dir() and f'href="/outbreaks/cruise-lines/{d.name}/"' not in _leggi(f"cruise-lines/{d.name}/index.html"):
            errore(f"cruise-lines/{d.name}/: manca il link alla pagina delle epidemie")
    print(f"Epidemie: {len(pagine_linea)} pagine compagnia + indice, {len(anni) - 1} pagine anno; {len(ep)} epidemie, ognuna una volta sola.")


def controlla_classifica_navi():
    """20. rankings/cleanest-dirtiest-cruise-ships/: tutto ricalcolato da navi.json e ispezioni.json."""
    from datetime import date, timedelta
    navi = json.loads((G.DATI / "navi.json").read_text(encoding="utf-8"))
    isp = json.loads((G.DATI / "ispezioni.json").read_text(encoding="utf-8"))
    fine = max(r[0] for r in isp)
    f = date.fromisoformat(fine)
    try:
        inizio = (f.replace(year=f.year - 1) + timedelta(days=1)).isoformat()
    except ValueError:
        inizio = (f.replace(year=f.year - 1, day=28) + timedelta(days=1)).isoformat()
    nome = lambda s: re.sub(r" Of The ", " of the ", navi[s]["nome"])  # noqa: E731
    pop = [s for s, n in navi.items() if n["stato"] == "attiva" and inizio <= n["storia"][0][0] <= fine]
    ult = {s: navi[s]["storia"][0] for s in pop}

    def serie(s):
        k = 0
        for x in navi[s]["storia"]:
            if x[1] != 100:
                break
            k += 1
        return k
    ordine = sorted(pop, key=lambda s: nome(s))
    ordine.sort(key=lambda s: ult[s][0], reverse=True)
    bassi = sorted(ordine, key=lambda s: ult[s][1])
    limite = ult[bassi[min(25, len(bassi)) - 1]][1]
    bassi = [s for s in bassi if ult[s][1] <= limite]
    alti = sorted((s for s in ordine if ult[s][1] == 100), key=lambda s: -serie(s))
    rel = "rankings/cleanest-dirtiest-cruise-ships/index.html"
    t = _leggi(rel)

    def letta(ident):
        m = re.search(r'<table class="lt" id="%s".*?</table>' % ident, t, re.S)
        return re.findall(r'<tr data-s="([^"]+)">(.*?)</tr>', m.group(0), re.S) if m else []
    for ident, attesa, chiave in (("piu-bassi", bassi, lambda s: ult[s][1]), ("a-100", alti, serie)):
        righe = letta(ident)
        if [s for s, _ in righe] != attesa:
            errore(f"{rel}: tabella {ident}: navi o ordine diversi dal ricalcolo ({len(righe)} righe, attese {len(attesa)})")
            continue
        for i, (s, r) in enumerate(righe):
            posto = 1 + sum(1 for x in attesa[:i] if chiave(x) != chiave(s))
            if not re.search(r'<span class="small">%d\.</span>' % posto, r):
                errore(f"{rel}: {s} dovrebbe essere al posto {posto}")
            if _cella(r, "Score") != str(ult[s][1]):
                errore(f"{rel}: voto di {s} diverso da {ult[s][1]}")
            if ident == "a-100" and _cella(r, "100s in a row") != str(serie(s)):
                errore(f"{rel}: serie di 100 di {s} diversa da {serie(s)}")
    # classifica completa: tutte le navi della finestra, dal voto più alto; data e voto di ogni riga contro navi.json e contro
    # ispezioni.json (l'ispezione più recente della nave nei dati grezzi), link alla pagina della nave esistente
    tutte = sorted(ordine, key=lambda s: -ult[s][1])
    righe = letta("tutte")
    grezze = {}
    for r in isp:
        if r[4] and (r[4] not in grezze or r[0] > grezze[r[4]][0]):
            grezze[r[4]] = (r[0], r[1])
    if [s for s, _ in righe] != tutte:
        errore(f"{rel}: tabella tutte: navi o ordine diversi dal ricalcolo ({len(righe)} righe, attese {len(tutte)})")
    else:
        for s, r in righe:
            posto = 1 + sum(1 for x in pop if ult[x][1] > ult[s][1])
            if not re.search(r'<span class="small">%d\.</span>' % posto, r):
                errore(f"{rel}: tabella tutte: {s} dovrebbe essere al posto {posto}")
            if _cella(r, "Score") != str(ult[s][1]):
                errore(f"{rel}: tabella tutte: voto di {s} diverso da {ult[s][1]}")
            d = date.fromisoformat(ult[s][0])
            if _cella(r, "Inspected") != f"{d:%b} {d.day}, {d.year}":
                errore(f"{rel}: tabella tutte: data di {s} diversa da {ult[s][0]}")
            if grezze.get(s) != (ult[s][0], ult[s][1]):
                errore(f"{rel}: tabella tutte: {s} non coincide con l'ultima ispezione in ispezioni.json ({grezze.get(s)})")
            if f'href="/ships/{s}/"' not in r or not (G.SITO / "ships" / s / "index.html").exists():
                errore(f"{rel}: tabella tutte: link alla pagina di {s} mancante")
            if ("Failed" in r) != (ult[s][1] <= 85):
                errore(f"{rel}: tabella tutte: esito di {s} sbagliato")
            # la pagina della nave dichiara lo stesso posto
            if f"place {posto} of {len(pop)} ships" not in _leggi(f"ships/{s}/index.html"):
                errore(f"ships/{s}/: posto nella classifica diverso da {posto} di {len(pop)}")
    for rel2 in (f"rankings/lowest-scores-{fine[:4]}/index.html", "ships/index.html"):
        if "/rankings/cleanest-dirtiest-cruise-ships/" not in _leggi(rel2).split("<main", 1)[-1].split("</main>")[0]:
            errore(f"{rel2}: manca il link alla classifica per nave")
    boc = sum(1 for s in pop if ult[s][1] <= 85)
    passate = sum(1 for s in bassi if ult[s][1] >= 86)
    for frase in (f"lowest score is {nome(bassi[0])}: {ult[bassi[0]][1]} out of 100", f"<strong>{len(alti)} ships scored a perfect 100</strong>",
                  f"Ranking of {len(pop)} ships", f"{boc} ship", f"Lowest latest CDC scores: {len(bassi)} ships",
                  f"{passate} of these {len(bassi)} ships passed: the pass mark is 86 out of 100, and the list goes up to a score of {ult[bassi[-1]][1]}",
                  f"All {len(pop)} ships ranked by latest CDC score"):
        if frase not in t:
            errore(f"{rel}: frase attesa non trovata: «{frase}»")
    print(f"Classifica per nave: {len(pop)} navi nella finestra {inizio} - {fine}; {len(bassi)} più basse, {len(alti)} a 100, {len(righe)} nella classifica completa: ordine riprodotto.")



def controlla_sitemap_lastmod():
    _, _, _, fonti = _dati_grezzi()
    from datetime import date
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    voci = re.findall(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]*)</lastmod>)?</url>", sm)
    if len(voci) != sm.count("<url>"):
        errore("sitemap: voci non leggibili")
    for u, lm in voci:
        if lm != fonti["scaricato_il"]:
            errore(f"sitemap: lastmod {lm!r} invece di {fonti['scaricato_il']} per {u}")
        elif date.fromisoformat(lm) > date.today():
            errore(f"sitemap: lastmod nel futuro per {u}")
    for p in ("rankings/cleanest-cruise-lines/", "rankings/year-over-year/"):
        if f"<loc>{G.URL_SITO}/{p}</loc>" not in sm:
            errore(f"sitemap: manca {p}")
    for f in SITO.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        ti = re.search(r"<title>(.*?)</title>", t)
        de = re.search(r'<meta name="description" content="([^"]*)"', t)
        import html as _h
        if ti and len(_h.unescape(ti.group(1))) > 70:
            errore(f"{f.relative_to(SITO)}: title di {len(_h.unescape(ti.group(1)))} caratteri")
        if de and len(_h.unescape(de.group(1))) > 160:
            errore(f"{f.relative_to(SITO)}: description di {len(_h.unescape(de.group(1)))} caratteri")
    print(f"Sitemap: {len(voci)} URL, lastmod {fonti['scaricato_il']}.")


def main():
    pagine = controlla_pagine()
    controlla_server(pagine)
    controlla_dati()
    controlla_parole()
    controlla_peso()
    controlla_classifiche()
    controlla_epidemie_fonte()
    controlla_epidemie_pagine()
    controlla_classifica_navi()
    controlla_sitemap_lastmod()
    if "--senza-rete" not in sys.argv:
        controlla_fonte()
    controlla_indexnow()
    controlla_monetizzazione()
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
