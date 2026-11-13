"""Controlli di "Statute of Limitations by State" prima di ogni pubblicazione.

Uso (dalla radice del repository):
    python3 limits/verifica.py            # controlli sui file
    python3 limits/verifica.py --browser  # anche Playwright a 375 e 1280 px, chiaro e scuro (richieste esterne bloccate)

1. Fonti: impronta SHA-256 di ogni file grezzo = dati/fonti.json, ultima lettura HTTP 200.
2. Termini: estrattore di testo SCRITTO A PARTE (html.parser, pdftotext -layout; non usa testo.py né genera.py). Per ogni variante
   di ogni cella: frammenti citati presenti nel testo ufficiale e in ordine; numero di anni RILETTO dalla frase della legge con un
   analizzatore suo (parole e cifre) e confrontato con norme.py, con ogni pagina (attributi data-v) e con i dati del calcolatore.
3. Citazioni: ogni <blockquote data-fonte> delle pagine è presente parola per parola nel testo ufficiale.
4. Calcolatore: il JS del sito (eseguito con node) = calcolo Python scritto qui, su più di 300 casi.
5. Pagine: titoli ≤ 65 e descrizioni 70-160 uniche, un h1, canonical, sitemap, link interni, robots, netlify.toml con ignore,
   chiave IndexNow, GoatCounter, frase fissa "not a substitute for the advice of an attorney", parole vietate, temi esclusi,
   nomi di modelli AI, dati personali.
6. FAQ da ricerche vere (dati/domanda.json) e JSON-LD = testo visibile. 7. Monetizzazione (controlli comuni della rete).
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
GREZZI = RADICE / "raccolta" / "_grezzi"
URL_SITO = "https://statute-limits-by-state.netlify.app"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

ERR, AVV = [], []


def errore(m):
    ERR.append(m)


def avviso(m):
    AVV.append(m)


def leggi(p):
    return Path(p).read_text(encoding="utf-8")


# ---------------------------------------------------------------- estrattore indipendente
class _Testo(HTMLParser):
    SALTA = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pezzi, self.salta = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SALTA:
            self.salta += 1

    def handle_endtag(self, tag):
        if tag in self.SALTA and self.salta:
            self.salta -= 1
        elif tag in ("p", "div", "li", "br", "tr", "td", "h1", "h2", "h3", "h4", "section"):
            self.pezzi.append(" ")

    def handle_data(self, data):
        if not self.salta:
            self.pezzi.append(data)


def piatto(t):
    t = t.translate({0x2019: "'", 0x2018: "'", 0x201C: '"', 0x201D: '"', 0xA0: " ", 0x2009: " ", 0x202F: " ", 0xAD: None})
    return " ".join(t.split())


def testo_ufficiale(fid, voce, cache={}):
    if fid in cache:
        return cache[fid]
    f = GREZZI / voce["file"]
    if f.suffix == ".pdf":
        grezzo = subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True, check=True).stdout
    else:
        p = _Testo()
        p.feed(f.read_text(encoding="utf-8", errors="replace"))
        grezzo = "".join(p.pezzi)
    cache[fid] = piatto(grezzo)
    return cache[fid]


PAROLE = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def anni_da_frase(frase):
    """Numero di anni scritto nella frase della legge: 'within two years', 'WITHIN FOUR YEARS', 'is 3 years', 'below three years'."""
    m = re.findall(r"\b(\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)[ -]years?\b", frase, re.I)
    if len(m) != 1:
        return None
    x = m[0].lower()
    return int(x) if x.isdigit() else PAROLE[x]


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti():
    fonti = json.loads(leggi(DATI / "fonti.json"))
    for fid, v in fonti.items():
        if v.get("http") != 200:
            errore(f"fonte {fid}: HTTP {v.get('http')}")
            continue
        f = GREZZI / v.get("file", "-")
        if not f.exists():
            errore(f"fonte {fid}: manca il file grezzo (python3 limits/raccolta/fonti.py)")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != v["sha256"]:
            errore(f"fonte {fid}: impronta SHA-256 diversa da dati/fonti.json")
    ign = leggi(RADICE / ".gitignore")
    if "raccolta/_grezzi/" not in ign:
        errore(".gitignore non esclude raccolta/_grezzi/")
    print(f"Fonti: {len(fonti)} file ufficiali, impronte SHA-256 uguali a dati/fonti.json")
    return fonti


# ---------------------------------------------------------------- 2. termini riletti dalla legge
def controlla_termini(fonti):
    sys.path.insert(0, str(RADICE))
    import norme as N  # solo dati curati (citazioni e anni dichiarati), nessun codice di genera.py
    attesi = {}  # id variante -> anni riletti dalla legge

    def ricontrolla(vid, fid, frammenti, frase, anni_dichiarati):
        t = testo_ufficiale(fid, fonti[fid])
        pos = -1
        for fr in frammenti:
            q = piatto(fr)
            i = t.find(q, pos + 1)
            if i < 0:
                errore(f"{vid}: citazione non trovata in {fid}: «{q[:70]}»")
                return
            if pos >= 0 and i - pos > 6000:
                errore(f"{vid}: frammenti troppo lontani nel testo di {fid}")
            pos = i
        if not any(frase in fr for fr in frammenti):
            errore(f"{vid}: la frase del termine non è nella citazione")
        n = anni_da_frase(frase)
        if n is None:
            errore(f"{vid}: non riesco a leggere il termine da «{frase}»")
        elif n != anni_dichiarati:
            errore(f"{vid}: la legge dice {n} anni, norme.py {anni_dichiarati}")
        attesi[vid] = n

    for k, c in N.CELLE.items():
        for i, v in enumerate(c["varianti"]):
            ricontrolla(f"{k}/{i}", v["fonte"], v["testo"], v["frase"], v["anni"])
            if v.get("prima"):
                p = v["prima"]
                ricontrolla(f"{k}/{i}/prima", p["fonte"], p["testo"], p["frase"], p["anni"])
        if c.get("repose"):
            r = c["repose"]
            ricontrolla(f"{k}/r", r["fonte"], r["testo"], r["frase"], r["anni"])
    print(f"Termini: {len(attesi)} periodi riletti dal testo di legge con un estrattore indipendente, {len(N.CELLE)} celle")
    return N, attesi


# ---------------------------------------------------------------- pagine
PAGINE, TESTI = {}, {}


def carica_pagine():
    for f in sorted(SITO.rglob("*.html")):
        p = str(f.relative_to(SITO))
        PAGINE[p] = leggi(f)
        x = _Testo()
        x.feed(PAGINE[p])
        TESTI[p] = piatto("".join(x.pezzi))


def controlla_periodi_pagine(N, attesi, fonti):
    visti = {}
    for p, html_ in PAGINE.items():
        for vid, interno in re.findall(r'<span data-v="([^"]+)">([^<]*)</span>', html_):
            m = re.fullmatch(r"(\d+) years?", interno.strip())
            if not m:
                errore(f"{p}: periodo illeggibile «{interno}» ({vid})")
                continue
            if vid not in attesi:
                errore(f"{p}: variante sconosciuta {vid}")
            elif int(m.group(1)) != attesi[vid]:
                errore(f"{p}: {vid} mostra {m.group(1)} anni, la legge {attesi[vid]}")
            visti.setdefault(vid, set()).add(p)
        # citazioni
        for fid, corpo in re.findall(r'<blockquote class="legge" data-fonte="([^"]+)">(.*?)</blockquote>', html_, re.S):
            t = testo_ufficiale(fid, fonti[fid])
            for par in re.findall(r"<p>(.*?)</p>", corpo, re.S):
                q = piatto(unescape(par))
                if q not in t:
                    errore(f"{p}: citazione non presente parola per parola in {fid}: «{q[:60]}»")
    for k in N.CELLE:
        s, c = k.split("/")
        pag = f"{N.STATI[s]['slug']}/{c}/index.html"
        for vid in [x for x in attesi if x.startswith(k + "/")]:
            if pag not in visti.get(vid, set()):
                errore(f"{vid}: periodo non mostrato nella sua pagina {pag}")
    n_q = sum(len(re.findall(r"<blockquote", v)) for v in PAGINE.values())
    print(f"Pagine: {sum(len(v) for v in visti.values())} periodi mostrati coincidono con la legge; {n_q} citazioni presenti parola per parola")


# ---------------------------------------------------------------- 4. calcolatore
def py_piu_anni(d, n):
    y = d.year + n
    bis = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    return date(y, 2, 28) if (d.month, d.day) == (2, 29) and not bis else date(y, d.month, d.day)


def py_calcola(cella, d):
    out = []
    for v in cella["v"]:
        if v.get("tr") and d < date.fromisoformat(v["tr"]["data"]):
            out.append([v["l"], None])
            continue
        a, l_ = v["a"], v["l"]
        if v.get("prima") and d <= date.fromisoformat(v["prima"]["fino"]):
            a, l_ = v["prima"]["a"], v["prima"]["l"]
        out.append([l_, py_piu_anni(d + timedelta(days=v.get("g", 0)), a).isoformat()])
    rip = py_piu_anni(d, cella["r"]["a"]).isoformat() if cella.get("r") else None
    return [out, rip]


def controlla_calcolatore(N, attesi):
    m = re.search(r'<script type="application/json" id="dati-calc">(.*?)</script>', PAGINE["index.html"], re.S)
    D = json.loads(m.group(1).replace("<\\/", "</"))
    if set(D["celle"]) != set(N.CELLE):
        errore("calcolatore: celle diverse da norme.py")
    for k, c in D["celle"].items():
        for i, v in enumerate(c["v"]):
            if attesi.get(f"{k}/{i}") != v["a"]:
                errore(f"calcolatore {k}/{i}: {v['a']} anni, la legge {attesi.get(f'{k}/{i}')}")
            if v.get("prima") and attesi.get(f"{k}/{i}/prima") != v["prima"]["a"]:
                errore(f"calcolatore {k}/{i}: periodo precedente diverso dalla legge")
        if c.get("r") and attesi.get(f"{k}/r") != c["r"]["a"]:
            errore(f"calcolatore {k}: outer limit diverso dalla legge")
    date_prova = ["2020-02-29", "2021-06-15", "2021-06-16", "2023-03-23", "2023-03-24", "2023-03-25", "2024-02-29", "2024-12-31",
                  "2025-01-15", "2026-11-13", "2019-07-04", "2022-10-01"]
    casi = [(k, d) for k in sorted(D["celle"]) for d in date_prova]
    js = next(SITO.glob("assets/app.*.js"))
    with tempfile.TemporaryDirectory() as tmp:
        prova = Path(tmp) / "prova.js"
        prova.write_text(f"const SOL=require({json.dumps(str(js))});const D={json.dumps(D)};const casi={json.dumps(casi)};"
                         "const out=casi.map(([k,d])=>{const r=SOL.calcola(D.celle[k],d);"
                         "return [r.varianti.map(v=>[v.l,v.scadenza||null]),r.repose?r.repose.scadenza:null];});"
                         "process.stdout.write(JSON.stringify(out));", encoding="utf-8")
        r = subprocess.run(["node", str(prova)], capture_output=True, text=True)
    if r.returncode:
        errore(f"calcolatore: node non parte ({r.stderr[:200]})")
        return
    risultati = json.loads(r.stdout)
    diversi = 0
    for (k, d), js_out in zip(casi, risultati):
        if py_calcola(D["celle"][k], date.fromisoformat(d)) != js_out:
            diversi += 1
            if diversi <= 5:
                errore(f"calcolatore {k} {d}: JS {js_out} ≠ Python {py_calcola(D['celle'][k], date.fromisoformat(d))}")
    # casi noti scritti a mano
    noti = [("FL/personal-injury", "2023-03-24", 0, "2027-03-24"), ("FL/personal-injury", "2023-03-25", 0, "2025-03-25"),
            ("OH/debt", "2024-01-01", 0, "2030-01-31"), ("TX/personal-injury", "2024-02-29", 0, "2026-02-28"),
            ("OH/medical-malpractice", "2025-05-01", 0, "2026-05-01")]
    for k, d, i, att in noti:
        if py_calcola(D["celle"][k], date.fromisoformat(d))[0][i][1] != att:
            errore(f"calcolatore: caso noto {k} {d} non dà {att}")
    if py_calcola(D["celle"]["OH/breach-of-contract"], date(2021, 6, 15))[0][0][1] is not None:
        errore("calcolatore: Ohio prima del 16/6/2021 dovrebbe non dare una data")
    print(f"Calcolatore: {len(casi)} casi, JS (node) = Python in {len(casi) - diversi}; {len(noti) + 1} casi noti giusti")


# ---------------------------------------------------------------- 5. pagine
VIETATE = [r"you should sue", r"guarantee", r"free consultation", r"lawyers? near me", r"attorneys? near me", r"debt relief",
           r"debt settlement", r"consolidat", r"\bloans?\b", r"you can still sue", r"we recommend (a|the) lawyer", r"sexual abuse",
           r"child sex", r"sexual assault"]
MODELLI = ["Cl" + "aude", "Anth" + "ropic", "Chat" + "GPT", "GP" + "T-", "Gem" + "ini", "Op" + "us 5", "Son" + "net", "Hai" + "ku", "Open" + "AI", "LL" + "M"]


def controlla_pagine():
    sitemap = set(re.findall(r"<loc>([^<]+)</loc>", leggi(SITO / "sitemap.xml")))
    titoli, descr, canon = {}, {}, set()
    for p, html_ in PAGINE.items():
        t = re.search(r"<title>(.*?)</title>", html_)
        d = re.search(r'<meta name="description" content="([^"]*)"', html_)
        if not t or not d:
            errore(f"{p}: titolo o descrizione mancante")
            continue
        tt, dd = unescape(t.group(1)), unescape(d.group(1))
        if len(tt) > 65:
            errore(f"{p}: titolo di {len(tt)} caratteri")
        if not 70 <= len(dd) <= 160:
            errore(f"{p}: descrizione di {len(dd)} caratteri")
        if tt in titoli or dd in descr:
            errore(f"titolo o descrizione doppia: {p}")
        titoli[tt], descr[dd] = p, p
        if html_.count("<h1") != 1:
            errore(f"{p}: {html_.count('<h1')} h1")
        c = re.search(r'<link rel="canonical" href="([^"]+)"', html_)
        noindex = '<meta name="robots" content="noindex">' in html_
        if p == "404.html":
            if not noindex:
                errore("404 senza noindex")
        else:
            atteso = URL_SITO + "/" + (p[:-len("index.html")] if p.endswith("index.html") else p)
            if not c or c.group(1) != atteso:
                errore(f"{p}: canonical {c.group(1) if c else None} invece di {atteso}")
            canon.add(atteso)
        if "gc.zgo.at/count.js" not in html_ or "rete-siti.goatcounter.com" not in html_:
            errore(f"{p}: contatore GoatCounter mancante")
        if "not a substitute for the advice of an attorney" not in TESTI[p] or "Talk to a licensed attorney" not in TESTI[p]:
            errore(f"{p}: manca la frase fissa (informazione, non consulenza)")
        if "<form" in html_ and ("method=" in html_ or "action=" in html_ or "data-netlify" in html_):
            errore(f"{p}: modulo che invia dati (vietato: niente raccolta contatti)")
        for href in re.findall(r'href="(/[^"#?]*)', html_):
            f = SITO / href.lstrip("/") / "index.html" if href.endswith("/") else SITO / href.lstrip("/")
            if not f.exists():
                errore(f"{p}: link interno rotto {href}")
        for anc in re.findall(r'href="/?#([^"]+)"', html_):
            dest = html_ if 'href="#' + anc in html_ else PAGINE["index.html"]
            if f'id="{anc}"' not in dest:
                errore(f"{p}: ancora #{anc} senza destinazione")
        visibile = TESTI[p] + " " + " ".join(re.findall(r'(?:content|title|alt|aria-label|placeholder)="([^"]*)"', html_))
        for pat in VIETATE:
            m = re.search(pat, visibile, re.I)
            if m:
                errore(f"{p}: parola o tema vietato «{m.group(0)}»")
        for mm in MODELLI:
            if mm in html_:
                errore(f"{p}: nome di modello «{mm}»")
        if re.search(r"Massimiliano|\bCori\b", html_):
            errore(f"{p}: dato personale")
        for mail in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", TESTI[p]):
            errore(f"{p}: indirizzo email nel testo ({mail})")
    if sitemap != canon:
        errore(f"sitemap ≠ canonical: {len(sitemap - canon)} in più, {len(canon - sitemap)} mancanti")
    for f in ("robots.txt", "netlify.toml", "ads.txt", "b5a26a844a465f58552debee2c8a0114.txt", "assets/og.png", "assets/fonts/public-sans.woff2",
              "assets/fonts/newsreader.woff2", "404.html"):
        if not (SITO / f).exists():
            errore(f"manca sito/{f}")
    if "Sitemap: " + URL_SITO + "/sitemap.xml" not in leggi(SITO / "robots.txt"):
        errore("robots.txt senza sitemap")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in leggi(SITO / "netlify.toml"):
        errore("netlify.toml senza ignore")
    if leggi(SITO / "b5a26a844a465f58552debee2c8a0114.txt").strip() != "b5a26a844a465f58552debee2c8a0114":
        errore("chiave IndexNow sbagliata")
    for f in list(RADICE.glob("*.py")) + list(RADICE.glob("raccolta/*.py")) + list(DATI.glob("*.json")) + [RADICE / "NOTE.md"]:
        if f.name == "verifica.py" or not f.exists():
            continue
        tx = leggi(f)
        for mm in MODELLI:
            if mm in tx:
                errore(f"{f.relative_to(RADICE)}: nome di modello «{mm}»")
        if "sd_" + "live" in tx:
            errore(f"{f.relative_to(RADICE)}: contiene una chiave")
    n_idx = sum(1 for v in PAGINE.values() if 'rel="canonical"' in v)
    print(f"Pagine: {len(PAGINE)} file html, {n_idx} indicizzabili (sitemap {len(sitemap)}), titoli e descrizioni unici, frase fissa ovunque")


# ---------------------------------------------------------------- 6. FAQ
def controlla_faq():
    dom = json.loads(leggi(DATI / "domanda.json"))["radici"]
    tutte = set(dom) | {s for v in dom.values() if isinstance(v, list) for s in v}
    faq = json.loads(leggi(DATI / "faq.json"))["faq"]
    for x in faq:
        if x["ricerca"] not in tutte:
            errore(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non è in domanda.json")
    n = 0
    for p, html_ in PAGINE.items():
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_, re.S):
            d = json.loads(blocco)
            if d.get("@type") == "FAQPage":
                for q in d["mainEntity"]:
                    n += 1
                    if piatto(q["name"]) not in TESTI[p] or piatto(q["acceptedAnswer"]["text"]) not in TESTI[p]:
                        errore(f"{p}: FAQ JSON-LD diversa dal testo visibile ({q['name']})")
                    if "{" in q["acceptedAnswer"]["text"]:
                        errore(f"{p}: segnaposto non riempito in FAQ")
    if n != len(faq):
        errore(f"FAQ pubblicate {n}, nel file {len(faq)}")
    print(f"FAQ: {n} domande, tutte da ricerche vere (autocompletamento gl=us)")


# ---------------------------------------------------------------- 7. monetizzazione
def controlla_monetizzazione():
    err_m, info = MON.controlla_sito("limits", SITO)
    for e in err_m:
        errore("monetizzazione: " + e)
    if not info["adsense"]:
        avviso("AdSense spento per limits in monetizzazione.json")
    aff = json.loads(leggi(DATI / "affiliati.json"))
    accesi = [k for k, v in aff.items() if not k.startswith("_") and v.get("attivo")]
    n_link = sum(len(MON.link_affiliati(v)) for v in PAGINE.values())
    if not accesi and n_link:
        errore(f"programmi spenti ma {n_link} link di affiliazione nelle pagine")
    for p in ("about/index.html", "privacy/index.html", "how-we-check/index.html", "404.html"):
        if "googlesyndication" in PAGINE[p]:
            errore(f"{p}: pubblicità su una pagina senza contenuto sostanziale")
    con_ads = sum(1 for v in PAGINE.values() if "googlesyndication" in v)
    print(f"Monetizzazione: AdSense su {con_ads} pagine di contenuto, programmi di affiliazione accesi: {accesi or 'nessuno'}")


# ---------------------------------------------------------------- browser
PAGINE_BROWSER = ["/", "/florida/personal-injury/", "/ohio/debt/", "/debt/"]


def controlla_browser():
    import mimetypes
    from playwright.sync_api import sync_playwright
    shot = RADICE / "cache" / "screenshot"
    shot.mkdir(parents=True, exist_ok=True)

    def servi(route):
        url = route.request.url
        if not url.startswith("http://sito.test/"):
            return route.abort()  # solo i file del sito: niente richieste esterne
        p = url[len("http://sito.test"):].split("?")[0].split("#")[0]
        if p.endswith("/"):
            p += "index.html"
        f, stato = SITO / p.lstrip("/"), 200
        if not f.is_file():
            f, stato = SITO / "404.html", 404
        route.fulfill(status=stato, body=f.read_bytes(), content_type=mimetypes.guess_type(str(f))[0] or "text/html")

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in (375, 1280):
            for tema in ("light", "dark"):
                ctx = b.new_context(viewport={"width": w, "height": 900}, color_scheme=tema)
                pg = ctx.new_page()
                errori_js = []
                pg.on("pageerror", lambda e: errori_js.append(str(e)))
                pg.route("**/*", servi)
                for u in PAGINE_BROWSER:
                    r = pg.goto("http://sito.test" + u)
                    if r.status != 200:
                        errore(f"browser {u}: HTTP {r.status}")
                    pg.wait_for_load_state("load")
                    pg.locator("input[name=data]").first.fill("2023-03-24")
                    pg.locator("[data-calc] form button").first.click()
                    esito = pg.locator(".esito").first
                    if not esito.is_visible() or "General deadline" not in esito.inner_text():
                        errore(f"browser {w}px {tema} {u}: il calcolatore non mostra il risultato")
                    largo = pg.evaluate("document.documentElement.scrollWidth")
                    if largo > w + 1:
                        errore(f"browser {w}px {tema} {u}: scorrimento orizzontale ({largo}px)")
                    piccoli = pg.evaluate("""Array.from(document.querySelectorAll('main p, main li, main td, main span, main small')).filter(e=>e.offsetParent&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<11).length""")
                    if piccoli:
                        errore(f"browser {w}px {tema} {u}: {piccoli} testi sotto 11px")
                    sfondo = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                    if (tema == "dark") != (sfondo == "rgb(14, 19, 32)"):
                        errore(f"browser {w}px {tema} {u}: sfondo {sfondo} non coerente con il tema")
                    nome = u.strip("/").replace("/", "_") or "home"
                    pg.screenshot(path=str(shot / f"{nome}_{w}_{tema}.png"), full_page=(w == 375 and u == "/"))
                prima = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                pg.click("[data-tema]")
                if prima == pg.evaluate("getComputedStyle(document.body).backgroundColor"):
                    errore(f"browser {w}px {tema}: il pulsante del tema non cambia lo sfondo")
                if errori_js:
                    errore(f"browser {w}px {tema}: errori JS {errori_js[:3]}")
                ctx.close()
        b.close()
    print(f"Browser: {len(PAGINE_BROWSER)} pagine × 375/1280 px × chiaro/scuro, calcolatore provato, richieste esterne bloccate, screenshot in {shot}")


def main():
    fonti = controlla_fonti()
    N, attesi = controlla_termini(fonti)
    carica_pagine()
    controlla_periodi_pagine(N, attesi, fonti)
    controlla_calcolatore(N, attesi)
    controlla_pagine()
    controlla_faq()
    controlla_monetizzazione()
    if "--browser" in sys.argv:
        controlla_browser()
    for a in AVV:
        print("AVVISO:", a)
    for e in ERR[:80]:
        print("ERRORE:", e)
    print(f"\n{len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
