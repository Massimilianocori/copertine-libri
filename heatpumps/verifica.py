"""Controlli di Heat Pump Grants UK. Uso (dalla radice del repository):
    python3 heatpumps/verifica.py            # tutti i controlli sui file e sulle pagine
    python3 heatpumps/verifica.py --browser  # in più: Playwright a 375 e 1280 px, chiaro e scuro, su 4 pagine

Indipendenza: le cifre attese si ricalcolano qui leggendo direttamente gli xlsx ufficiali in raccolta/_grezzi/ (con codice
proprio, non con estrai.py né con dati/*.json), poi si cercano nelle pagine generate. L'impronta SHA-256 di ogni xlsx deve
essere quella scritta in dati/fonti.json.
"""
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import re
import sys
from html import unescape
from pathlib import Path

import openpyxl

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
GREZZI = RADICE / "raccolta" / "_grezzi"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

URL_SITO = "https://heat-pump-grants-uk.netlify.app"
ERR, AVV = [], []


def errore(m):
    ERR.append(m)


def avviso(m):
    AVV.append(m)


def leggi(p):
    return p.read_text(encoding="utf-8")


SOGLIA_INDICE = 200  # come in genera.py, riscritta qui apposta: il controllo non importa nulla dal generatore


def testo(html_):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t)))


def _arr(x, dec=0):
    # arrotondamento aritmetico sul valore come è scritto nel file (148.95 -> 149.0)
    return Decimal(repr(x)).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)


def f0(x):
    return f"{_arr(x):,}"


def f1(x):
    return f"{_arr(x, 1):,}"


def gbp(x):
    return f"£{_arr(x):,}"


PAGINE = {str(p.relative_to(SITO)): leggi(p) for p in sorted(SITO.rglob("*.html"))}
TESTI = {k: testo(v) for k, v in PAGINE.items()}
FONTI = json.loads(leggi(DATI / "fonti.json"))


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti():
    for fid, d in FONTI["definizioni"].items():
        es = FONTI["fonti"].get(fid, {})
        if es.get("http") != 200:
            errore(f"fonte {fid}: HTTP {es.get('http')}")
        if d["tipo"] == "xlsx":
            f = GREZZI / d["file"]
            if not f.exists():
                errore(f"file grezzo mancante {f} (lanciare raccolta/fonti.py)")
                continue
            if hashlib.sha256(f.read_bytes()).hexdigest() != es.get("sha256"):
                errore(f"{d['file']}: impronta SHA-256 diversa da dati/fonti.json")
        else:
            manca = [c for c, ok in es.get("trovate", {}).items() if not ok]
            if manca:
                errore(f"fonte {fid}: frasi non trovate {manca}")


# ---------------------------------------------------------------- 2. ricalcolo dagli xlsx
def righe(ws):
    return [r for r in ws.iter_rows(values_only=True)]


def dopo(rr, inizio):
    i = next(k for k, r in enumerate(rr) if r[0] is not None and str(r[0]).strip().startswith(inizio))
    return rr[i], rr[i + 1:]


def num(v):
    return isinstance(v, (int, float))


def ricalcola():
    wb = openpyxl.load_workbook(GREZZI / "bus.xlsx", read_only=True, data_only=True)
    X = {}
    _, q = dopo(righe(wb["Q1.2"]), "Area Codes")
    _, a = dopo(righe(wb["A1.7"]), "Area Codes")
    X["cum"] = {r[0]: r[4] for r in q if r[0]}
    X["anni"] = {r[0]: list(r[4:8]) for r in a if r[0]}
    # struttura: codice -> regione, figli
    reg, figli, livello = None, {}, {}
    ultimo_c = None
    for r in q:
        if not r[0]:
            continue
        if r[1]:
            reg, ultimo_c = r[0], None
            continue
        livello[r[0]] = (reg, "C" if r[2] else "D")
        if r[2]:
            ultimo_c = r[0]
        elif ultimo_c:
            figli.setdefault(ultimo_c, []).append(r[0])
    X["livello"], X["figli"] = livello, figli
    h12, r12 = dopo(righe(wb["1.2A"]), "Area Codes")
    X["reg_tot"] = {r[0]: r for r in r12 if r[0]}
    h12b, r12b = dopo(righe(wb["1.2B"]), "Area Codes")
    X["reg_10k"] = {r[0]: r[25] for r in r12b if r[0]}
    hq, rq = dopo(righe(wb["Q1.1A"]), "Technology type")
    ult = len([x for x in hq if x]) - 1
    X["trim"] = str(hq[ult]).replace("\n", " ")
    X["costi"] = {(str(r[0]).strip(), str(r[1]).strip()): r[ult] for r in rq if r[0] and r[1]}
    hm, rm = dopo(righe(wb["M1.1"]), "Voucher status")
    col = max(k for k, x in enumerate(hm) if x and re.match(r"^[A-Z][a-z]{2}\s\d{4}$", str(x).replace("\n", " ")))
    X["mese"] = str(hm[col]).replace("\n", " ")
    X["m11"] = {(r[0], r[1]): r for r in rm if r[0] and r[1]}
    X["m11_col"] = col
    hm2, rm2 = dopo(righe(wb["M1.2"]), "Status")
    col2 = max(k for k, x in enumerate(hm2) if x and re.match(r"^[A-Z][a-z]{2}\s\d{4}$", str(x).replace("\n", " ")))
    X["m12_dom"] = {r[1]: r[col2] for r in rm2 if r[0] == "Voucher applications received"}
    t11 = {r[0]: r for r in dopo(righe(wb["1.1"]), "Status")[1] if r[0]}
    X["pagati_tot"] = t11["Redemptions paid"][6]
    ha, ra = dopo(righe(wb["A1.3A"]), "Technology type")
    X["fasce"] = {(str(r[0]).strip(), str(r[1]).strip()): r[8] for r in ra if r[0] and r[1]}
    X["fasce_n"] = {(str(r[0]).strip(), str(r[1]).strip()): r[9] for r in ra if r[0] and r[1]}

    ws = openpyxl.load_workbook(GREZZI / "solare_la.xlsx", read_only=True, data_only=True)
    la = {}
    for foglio, campo in (("LA - Sites 2025", "s25"), ("LA - Sites 2020", "s20"), ("LA - Capacity, 2025", "mw25")):
        hh, rr = dopo(righe(ws[foglio]), "Local Authority Code")
        k = next(i for i, x in enumerate(hh) if x and str(x).startswith("Solar PV"))
        for r in rr:
            if r[0] and re.match(r"^[ESWN]\d{8}$", str(r[0]).strip()):
                d = la.setdefault(str(r[0]).strip(), {"nome": str(r[1]).strip()})
                d[campo] = r[k]
                if campo == "s25":
                    d["fam"] = r[4]
                    d["reg"] = str(r[2]).strip()
    X["la"] = la
    we = openpyxl.load_workbook(GREZZI / "solare_et63.xlsx", read_only=True, data_only=True)
    rr = righe(we["Table_4_by_Region"])
    et, blocco = {}, None
    for r in rr:
        if r[0] and str(r[0]).startswith("CUMULATIVE CAPACITY"):
            blocco = "mw"
            ncol = max(k for k, x in enumerate(r) if x)
            continue
        if r[0] and str(r[0]).startswith("CUMULATIVE COUNT"):
            blocco = "n"
            ncol = max(k for k, x in enumerate(r) if x)
            continue
        if blocco and r[0]:
            et.setdefault(str(r[0]).strip(), {})[blocco] = (r[ncol], r[ncol - 12])
    X["et"] = et
    wc = openpyxl.load_workbook(GREZZI / "solare_costi_tic.xlsx", read_only=True, data_only=True)
    _, rr = dopo(righe(wc["Regional costs (TIC)"]), "Financial year")
    ultimo = max(str(r[0]) for r in rr if r[0])
    X["sol_reg"] = {str(r[1]).strip(): (r[7], r[9]) for r in rr if r[0] == ultimo}
    _, rr = dopo(righe(wc["Summary table (TIC)"]), "Financial year")
    X["sol_somm"] = [r for r in rr if r[0] == ultimo][0]
    return X


def pagina_con(marcatore):
    for k, v in PAGINE.items():
        if marcatore in v:
            return k
    return None


SOPPR = {"[c1]": "not published (1 to 4)", "[c2]": "not published", "[c3]": "not published (0 to 4)", "[x]": "no data"}
NOMI_ET = {"E12000001": "North East", "E12000002": "North West", "E12000003": "Yorkshire and the Humber", "E12000004": "East Midlands",
           "E12000005": "West Midlands", "E12000006": "East of England", "E12000007": "London", "E12000008": "South East",
           "E12000009": "South West", "W92000004": "Wales", "S92000003": "Scotland", "N92000002": "Northern Ireland"}
NOMI_COSTI = dict(NOMI_ET, E12000003="Yorkshire and The Humber")


def controlla_cifre(X):
    controllate = 0
    # nazionali
    med = X["costi"][("Air-to-Water Heat Pump", "Median cost of installation (£)")]
    lq = X["costi"][("Air-to-Water Heat Pump", "Lower quartile cost of installation (£)")]
    uq = X["costi"][("Air-to-Water Heat Pump", "Upper quartile cost of installation (£)")]
    gmed = X["costi"][("Ground Source Heat Pump", "Median cost of installation (£)")]
    attese = {"index.html": [gbp(med), gbp(med - 7500), gbp(med - 9000), gbp(lq - 7500), gbp(uq - 7500), f0(X["cum"]["K04000001"]),
                             f0(X["m11"][("Voucher applications received", "All technology types")][X["m11_col"]]), f0(X["pagati_tot"])],
              "heat-pump-cost/index.html": [gbp(med), gbp(lq), gbp(uq), gbp(gmed), gbp(med - 7500),
                                            gbp(X["fasce"][("Air-to-Water Heat Pumps", "All")]), gbp(X["fasce"][("Ground Source Heat Pumps", "All")])],
              "solar-panels/index.html": [gbp(X["sol_somm"][1]), gbp(X["sol_somm"][5]), f0(X["et"]["TOTAL"]["n"][0]),
                                          f0(X["et"]["TOTAL"]["n"][0] - X["et"]["TOTAL"]["n"][1])]}
    for p, valori in attese.items():
        for v in valori:
            controllate += 1
            if v not in TESTI.get(p, ""):
                errore(f"{p}: cifra attesa {v} non trovata")
    # aree (council e contee)
    pagine_area = {m.group(1): k for k, v in PAGINE.items() for m in [re.search(r"<!-- area: (\w+) -->", v)] if m}
    attesi_codici = [c for c, (reg, liv) in X["livello"].items() if (liv == "D" or c not in X["figli"]) or c.startswith("E10")]
    for c in attesi_codici:
        p = pagine_area.get(c)
        if not p:
            errore(f"area {c}: nessuna pagina")
            continue
        t = TESTI[p]
        cum = X["cum"][c]
        anni = X["anni"][c]
        att = [f0(cum)] + [f0(v) if num(v) else SOPPR[v.strip()] for v in anni]
        if all(num(v) for v in anni):
            att.append(f0(cum - sum(anni)))
        sol = X["la"].get(c)
        if c in X["figli"]:  # contea: somma dei distretti
            ds = [X["la"].get(d) for d in X["figli"][c]]
            if all(ds):
                fam = sum(d["fam"] for d in ds)
                att += [f0(sum(d["s25"] for d in ds)), f1(cum / fam * 1000)]
        elif sol:
            att += [f0(sol["s25"]), f1(sol["mw25"]) + " MW", f1(cum / sol["fam"] * 1000), f0(sol["s25"] / sol["fam"] * 1000)]
        att += [gbp(med), gbp(med - 7500)]
        for v in att:
            controllate += 1
            if v not in t:
                errore(f"{p} ({c}): cifra attesa «{v}» non trovata")
        # indicizzazione: soglia 200 e anni tutti pubblicati (contee sempre)
        indice = "noindex" not in PAGINE[p]
        dovrebbe = c.startswith("E10") or (cum >= SOGLIA_INDICE and all(num(v) for v in anni))
        if indice != dovrebbe:
            errore(f"{p}: indicizzazione {indice} ma la regola dice {dovrebbe}")
    # regioni
    for r, nome in NOMI_ET.items():
        if r in ("S92000003", "N92000002"):
            continue
        p = pagina_con(f"<!-- region: {r} -->")
        if not p:
            errore(f"regione {r}: nessuna pagina")
            continue
        t = TESTI[p]
        att = [f0(X["cum"][r]), f1(X["reg_10k"][r]), f0(X["reg_tot"][r][25]), f0(X["m12_dom"][r])] + [f0(v) for v in X["anni"][r]]
        for v in att:
            controllate += 1
            if v not in t:
                errore(f"{p}: cifra attesa {v} non trovata")
    # solare per regione
    for r, nome in NOMI_ET.items():
        p = pagina_con(f"<!-- solar-region: {r} -->")
        if not p:
            errore(f"solare {r}: nessuna pagina")
            continue
        t = TESTI[p]
        n, n0 = X["et"][nome]["n"]
        att = [f0(n), f0(n - n0)]
        if NOMI_COSTI[r] in X["sol_reg"]:
            att += [gbp(x) for x in X["sol_reg"][NOMI_COSTI[r]]]
        for v in att:
            controllate += 1
            if v not in t:
                errore(f"{p}: cifra attesa {v} non trovata")
    print(f"Cifre: {controllate} valori ricalcolati dagli xlsx e trovati nelle pagine; {len(pagine_area)} pagine area, {len(attesi_codici)} attese")


# ---------------------------------------------------------------- 3. pagine, SEO, file
VIETATE = [(r"\bloans?\b", re.I), (r"\bfinanc(e|ed|es|ing)\b", re.I), (r"\bAPR\b", 0), (r"\bcredit", re.I), (r"(?<![\d.,])0\s?%", 0),
           (r"interest[- ]free", re.I), (r"monthly payments?", re.I), (r"pay monthly", re.I), (r"\bborrow", re.I), (r"\blend(er|ing)?\b", re.I)]
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
        if tt in titoli:
            errore(f"titolo doppio: {p} e {titoli[tt]}")
        if dd in descr:
            errore(f"descrizione doppia: {p} e {descr[dd]}")
        titoli[tt], descr[dd] = p, p
        if html_.count("<h1") != 1:
            errore(f"{p}: {html_.count('<h1')} h1")
        c = re.search(r'<link rel="canonical" href="([^"]+)"', html_)
        noindex = '<meta name="robots" content="noindex">' in html_
        if p == "404.html":
            if not noindex:
                errore("404 senza noindex")
        elif noindex:
            if c:
                errore(f"{p}: noindex con canonical")
            if MON.SEGNO_SENZA_ADSENSE not in html_:
                errore(f"{p}: noindex ma con pubblicità")
        else:
            atteso = URL_SITO + "/" + (p[:-len("index.html")] if p.endswith("index.html") else p)
            if not c or c.group(1) != atteso:
                errore(f"{p}: canonical {c.group(1) if c else None} invece di {atteso}")
            canon.add(atteso)
        if "gc.zgo.at/count.js" not in html_ or "rete-siti.goatcounter.com" not in html_:
            errore(f"{p}: contatore GoatCounter mancante")
        # link interni
        for href in re.findall(r'href="(/[^"#?]*)', html_):
            if href.startswith("/assets/"):
                f = SITO / href.lstrip("/")
            else:
                f = SITO / href.lstrip("/") / "index.html" if href.endswith("/") else SITO / href.lstrip("/")
            if not f.exists():
                errore(f"{p}: link interno rotto {href}")
        for anc in re.findall(r'href="#([^"]+)"', html_):
            if f'id="{anc}"' not in html_:
                errore(f"{p}: ancora #{anc} senza destinazione")
        # parole vietate (testo visibile e attributi) e nomi di modelli
        visibile = TESTI[p] + " " + " ".join(re.findall(r'(?:content|title|alt|aria-label|placeholder)="([^"]*)"', html_))
        for pat, fl in VIETATE:
            m = re.search(pat, visibile, fl)
            if m:
                errore(f"{p}: parola vietata «{m.group(0)}» (niente contenuti su prestiti o pagamenti)")
        for mm in MODELLI:
            if mm in html_:
                errore(f"{p}: nome di modello «{mm}»")
        if re.search(r"Massimiliano|\bCori\b", html_):
            errore(f"{p}: dato personale")
        for mail in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", TESTI[p]):
            errore(f"{p}: indirizzo email nel testo ({mail})")
    if sitemap != canon:
        errore(f"sitemap ≠ canonical: {len(sitemap - canon)} in più, {len(canon - sitemap)} mancanti")
    for f in ("robots.txt", "netlify.toml", "ads.txt", "b5a26a844a465f58552debee2c8a0114.txt", "assets/og.png", "assets/fonts/figtree.woff2"):
        if not (SITO / f).exists():
            errore(f"manca sito/{f}")
    if "Sitemap: " + URL_SITO + "/sitemap.xml" not in leggi(SITO / "robots.txt"):
        errore("robots.txt senza sitemap")
    toml = leggi(SITO / "netlify.toml")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in toml:
        errore("netlify.toml senza ignore")
    if leggi(SITO / "b5a26a844a465f58552debee2c8a0114.txt").strip() != "b5a26a844a465f58552debee2c8a0114":
        errore("chiave IndexNow sbagliata")
    # nomi di modelli nel codice e nei dati del sito (questa verifica esclusa: contiene l'elenco)
    for f in list(RADICE.glob("*.py")) + list(RADICE.glob("raccolta/*.py")) + list(DATI.glob("*.json")) + [RADICE / "NOTE.md"]:
        if f.name == "verifica.py" or not f.exists():
            continue
        tx = leggi(f)
        for mm in MODELLI:
            if mm in tx:
                errore(f"{f.relative_to(RADICE)}: nome di modello «{mm}»")
    n_idx = sum(1 for v in PAGINE.values() if 'rel="canonical"' in v)
    print(f"Pagine: {len(PAGINE)} file html, {n_idx} indicizzabili (sitemap {len(sitemap)}), titoli e descrizioni unici")


# ---------------------------------------------------------------- 4. FAQ
def controlla_faq():
    dom = json.loads(leggi(DATI / "domanda.json"))["radici"]
    tutte = set(dom) | {s for v in dom.values() if isinstance(v, list) for s in v}
    faq = json.loads(leggi(DATI / "faq.json"))["faq"]
    for x in faq:
        if x["ricerca"] not in tutte:
            errore(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non è in domanda.json")
        for f in x["fonti"]:
            if f not in FONTI["definizioni"]:
                errore(f"FAQ «{x['q']}»: fonte {f} sconosciuta")
    n = 0
    for p, html_ in PAGINE.items():
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_, re.S):
            d = json.loads(blocco)
            if d.get("@type") == "FAQPage":
                for q in d["mainEntity"]:
                    n += 1
                    if q["name"] not in TESTI[p] or q["acceptedAnswer"]["text"] not in TESTI[p]:
                        errore(f"{p}: FAQ JSON-LD diversa dal testo visibile ({q['name']})")
                    if "{" in q["acceptedAnswer"]["text"]:
                        errore(f"{p}: segnaposto non riempito in FAQ")
    if n != len(faq):
        errore(f"FAQ pubblicate {n}, nel file {len(faq)}")
    print(f"FAQ: {n} domande, tutte da ricerche vere (autocompletamento gl=gb)")


# ---------------------------------------------------------------- 5. monetizzazione e riquadro preventivi
def controlla_monetizzazione():
    err_m, info = MON.controlla_sito("heatpumps", SITO)
    for e in err_m:
        errore("monetizzazione: " + e)
    if not info["adsense"]:
        avviso("AdSense spento per heatpumps in monetizzazione.json")
    aff = json.loads(leggi(DATI / "affiliati.json"))
    accesi = [k for k, v in aff.items() if not k.startswith("_") and v.get("attivo")]
    n_link = sum(len(MON.link_affiliati(v)) for v in PAGINE.values())
    if not accesi and n_link:
        errore(f"programmi spenti ma {n_link} link di affiliazione nelle pagine")
    for k, v in aff.items():
        if k.startswith("_"):
            continue
        for pat, fl in VIETATE:
            if re.search(pat, v.get("testo", ""), fl):
                errore(f"affiliati.json {k}: parola vietata nel testo")
    # prova del riquadro acceso con un indirizzo finto su awin1.com
    sys.path.insert(0, str(RADICE))
    import genera
    prova = {k: dict(v, attivo=True, url="https://www.awin1.com/cread.php?awinmid=0&awinaffid=0") for k, v in aff.items() if not k.startswith("_")}
    box = genera.box_preventivo("council", prova)
    e, n = MON.controlla_link_pagina(box, "riquadro di prova")
    if n == 0 or e:
        errore(f"riquadro preventivi acceso: {e or 'nessun link'}")
    for pat, fl in VIETATE:
        if re.search(pat, testo(box), fl):
            errore("riquadro preventivi acceso: parola vietata")
    if genera.box_preventivo("council") != "<!-- quote box: off -->" and not accesi:
        errore("riquadro preventivi visibile con i programmi spenti")
    print(f"Monetizzazione: AdSense e privacy coerenti, programmi accesi: {accesi or 'nessuno'}, riquadro di prova corretto")


# ---------------------------------------------------------------- 6. browser
PAGINE_BROWSER = ["/", "/heat-pump-grants/cornwall/", "/heat-pump-grants/south-west/", "/solar-panels/"]


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
        f = SITO / p.lstrip("/")
        stato = 200
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
                    largo = pg.evaluate("document.documentElement.scrollWidth")
                    if largo > w + 1:
                        errore(f"browser {w}px {tema} {u}: scorrimento orizzontale ({largo}px)")
                    piccoli = pg.evaluate("""Array.from(document.querySelectorAll('main p, main li, main td, main span')).filter(e=>e.offsetParent&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<11).length""")
                    if piccoli:
                        errore(f"browser {w}px {tema} {u}: {piccoli} testi sotto 11px")
                    font = pg.evaluate("document.fonts.check('16px Figtree')")
                    if not font:
                        avviso(f"browser {w}px {tema} {u}: carattere Figtree non caricato")
                    sfondo = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                    if (tema == "dark") != (sfondo == "rgb(11, 20, 22)"):
                        errore(f"browser {w}px {tema} {u}: sfondo {sfondo} non coerente con il tema")
                    if pg.locator("[data-cerca]").count():
                        q = pg.locator("[data-cerca]").first
                        prima = pg.locator("[data-riga]:visible").count()
                        q.fill("zzzz")
                        if pg.locator("[data-riga]:visible").count() != 0:
                            errore(f"browser {u}: il filtro della tabella non nasconde le righe")
                        q.fill("")
                        if pg.locator("[data-riga]:visible").count() != prima:
                            errore(f"browser {u}: il filtro non ripristina le righe")
                    nome = (u.strip("/").replace("/", "_") or "home")
                    pg.screenshot(path=str(shot / f"{nome}_{w}_{tema}.png"), full_page=(w == 375 and u == "/"))
                pg.goto("http://sito.test/")
                prima = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                pg.click("[data-tema]") if w == 1280 else (pg.click("[data-tema]"))
                if prima == pg.evaluate("getComputedStyle(document.body).backgroundColor"):
                    errore(f"browser {w}px {tema}: il pulsante del tema non cambia lo sfondo")
                if errori_js:
                    errore(f"browser {w}px {tema}: errori JS {errori_js[:3]}")
                ctx.close()
        b.close()
    print(f"Browser: {len(PAGINE_BROWSER)} pagine × 375/1280 px × chiaro/scuro, richieste esterne bloccate, screenshot in {shot}")


def main():
    controlla_fonti()
    X = ricalcola()
    controlla_cifre(X)
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
