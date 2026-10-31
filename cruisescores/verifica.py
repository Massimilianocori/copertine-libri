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
