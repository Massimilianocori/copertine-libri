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
Monetizzazione (30/10/2026, controllo comune di studio-business/strumenti/monetizzazione.py): i link di affiliazione sono
ammessi solo verso i domini di monetizzazione.json, con rel="sponsored noopener" e la riga di trasparenza nella pagina;
domini bloccati e link sponsorizzati verso altri domini sono errori; script AdSense, ads.txt e sezione privacy ci sono
solo se AdSense è acceso per questo sito in monetizzazione.json.
Sezione "Disaster declarations and IRS tax relief" (30/10/2026, controlla_disastri): impronta di dati/disastri.json, pagine
attese (indice, Stati, contee con domanda) e solo quelle, tutte nella sitemap, titoli <= 70 caratteri, numeri e codici delle pagine
uguali ai dati, frasi obbligatorie e nessun consiglio personale; 10 valori ricontrollati sull'API OpenFEMA (--senza-rete li salta).
Sezione "California home insurance" (7/11/2026, controlla_california): fonti con impronta SHA-256, ogni numero ricalcolato dai PDF
FAIR Plan e dall'XLSX CDI con motori diversi da quelli della raccolta, pagine e sitemap, prima frase con dato e data, limiti scritti,
FAQ da ricerche salvate = JSON-LD, link tra indice, aree, pagine ZIP e pagine NFIP; con la rete, frasi ufficiali citate ancora presenti.
Esce con codice 1 se qualcosa non va.
"""
import json
import re
import subprocess
import sys
from html import unescape
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


def controlla_disastri():
    """Sezione disaster-relief/ (dati/disastri.json): impronta dei dati, pagine attese e solo quelle, tutte nella sitemap, titoli
    <= 70 caratteri, coerenza tra pagine e dati (numero di dichiarazioni, assistenza individuale, scadenza IRS, codici), frasi
    obbligatorie (fonte con data, rimandi ufficiali, nessun consiglio personale) e, se c'è rete, 10 valori ricontrollati sull'API."""
    import hashlib
    if not G.DIS:
        print("Sezione disastri: dati assenti, controllo saltato.")
        return
    D = json.loads((DATI / "disastri.json").read_text(encoding="utf-8"))
    imp = D.pop("impronta", None)
    if hashlib.sha256(json.dumps(D, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest() != imp:
        errore("disastri.json: impronta diversa dal contenuto")
    attese = {G.DIS_URL} | {G.url_dis_stato(st) for st in G.DIS_STATI} | {G.url_dis_contea(f) for f in G.AREE if G.ha_pagina_dis(f)}
    trovate = {p.relative_to(SITO).as_posix()[:-len("index.html")] for p in (SITO / G.DIS_URL).rglob("index.html")}
    for x in sorted(attese - trovate):
        errore(f"disastri: pagina mancante {x}")
    for x in sorted(trovate - attese):
        errore(f"disastri: pagina in più {x}")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8")))
    for x in sorted(attese):
        if f"{G.URL_SITO}/{x}" not in locs:
            errore(f"disastri: {x} non è nella sitemap")
    letto = G.data_lunga(G.DIS_OGGI)
    consiglio = re.compile(r"\byou (?:are eligible|qualify|should|must)\b|\bwe recommend\b|\byour county qualifies\b", re.I)
    for x in sorted(attese & trovate):
        t = (SITO / x / "index.html").read_text(encoding="utf-8")
        tit = re.search(r"<title>(.*?)</title>", t, re.S).group(1)
        if len(unescape(tit)) > 70:
            errore(f"disastri {x}: titolo di {len(unescape(tit))} caratteri")
        for frase in ("check with the IRS or a tax professional", "www.disasterassistance.gov", "www.irs.gov", "OpenFEMA", letto):
            if frase not in t:
                errore(f"disastri {x}: manca '{frase}'")
        corpo = re.sub(r"<[^>]+>", " ", t[t.find("<main"):])
        m = consiglio.search(corpo)
        if m:
            errore(f"disastri {x}: frase da consulenza '{m.group(0)}'")
    # coerenza pagine contea / Stato con i dati
    for f, A in G.AREE.items():
        if not G.ha_pagina_dis(f):
            continue
        x = G.url_dis_contea(f)
        if x not in trovate:
            continue
        t = (SITO / x / "index.html").read_text(encoding="utf-8")
        ia = int(any(r[1] or r[2] for r in A["d"]))
        scad = max((c["scadenza"] for c in G.irs_contea(f) if G.aperto(c)), default="")
        if f'data-n-dich="{len(A["d"])}"' not in t or f'data-ia="{ia}"' not in t or f'data-irs="{scad}"' not in t:
            errore(f"disastri {x}: numeri della scheda diversi dai dati")
        if set(re.findall(r'data-dich="([^"]+)"', t)) != {r[0] for r in A["d"]}:
            errore(f"disastri {x}: dichiarazioni in pagina diverse dai dati")
        for c in G.irs_contea(f):
            if f'data-irs="{c["codice"]}" data-scadenza="{c["scadenza"] or ""}"' not in t:
                errore(f"disastri {x}: comunicato IRS {c['codice']} mancante o con altra scadenza")
        prima = re.search(r'<p class="sub">(.*?)</p>', t, re.S).group(1)
        if not (prima.startswith("Yes:") or prima.startswith("FEMA&#x27;s data shows no")):
            errore(f"disastri {x}: la prima frase non risponde")
    for st in G.DIS_STATI:
        x = G.url_dis_stato(st)
        if x not in trovate:
            continue
        t = (SITO / x / "index.html").read_text(encoding="utf-8")
        n = sum(1 for k, v in G.DICH.items() if v["st"] == st)
        ap = sum(1 for c in G.irs_stato(st) if G.aperto(c))
        if f'data-n-dich="{n}"' not in t or f'data-irs-aperti="{ap}"' not in t:
            errore(f"disastri {x}: numeri dello Stato diversi dai dati")
    print(f"Sezione disastri: {len(trovate)} pagine (indice, {len(G.DIS_STATI)} Stati, {len(trovate) - len(G.DIS_STATI) - 1} contee); dati letti il {G.DIS_OGGI}, impronta {str(imp)[:12]}.")
    if "--senza-rete" not in sys.argv:
        controlla_disastri_api(trovate)


def controlla_disastri_api(trovate):
    """10 valori pubblicati (contea x dichiarazione) ricontrollati con richieste dirette all'API OpenFEMA, senza i dati locali:
    data della dichiarazione e programmi IA/PA/HM per quella contea, come scritti nella pagina."""
    import urllib.parse
    import urllib.request
    coppie = []
    contee = sorted(f for f in G.AREE if G.ha_pagina_dis(f) and G.AREE[f]["d"] and G.url_dis_contea(f) in trovate)
    passo = max(1, len(contee) // 10)
    for f in contee[::passo][:10]:
        coppie.append((f, G.AREE[f]["d"][0][0]))
    righe = []
    for f, k in coppie:
        t = (SITO / G.url_dis_contea(f) / "index.html").read_text(encoding="utf-8")
        riga = re.search(r'<tr data-dich="' + re.escape(k) + r'">(.*?)</tr>', t, re.S).group(1)
        pub = {"data": re.search(r'data-data="([^"]+)"', riga).group(1),
               "IA": "Individual aid: yes" in riga, "PA": "Public aid: yes" in riga, "HM": "Mitigation: yes" in riga}
        filtro = f"femaDeclarationString eq '{k}' and fipsStateCode eq '{f[:2]}' and fipsCountyCode eq '{f[2:]}'"
        url = ("https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?" +
               urllib.parse.urlencode({"$filter": filtro, "$select": "declarationDate,ihProgramDeclared,iaProgramDeclared,paProgramDeclared,hmProgramDeclared"}))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "floodcost-check/1.0"})
            r = json.loads(urllib.request.urlopen(req, timeout=60).read())["DisasterDeclarationsSummaries"]
        except Exception as e:
            errore(f"API FEMA non raggiungibile per {k} {f}: {e} (usare --senza-rete per saltare)")
            return
        if not r:
            errore(f"API FEMA: nessuna riga per {k} contea {f}")
            continue
        api = {"data": r[0]["declarationDate"][:10], "IA": any(x["ihProgramDeclared"] or x["iaProgramDeclared"] for x in r),
               "PA": any(x["paProgramDeclared"] for x in r), "HM": any(x["hmProgramDeclared"] for x in r)}
        ok = api == pub
        if not ok:
            errore(f"API FEMA {k} contea {f}: pubblicato {pub}, API {api}")
        righe.append(f"  {k} · {G.AREE[f]['nome']}, {G.AREE[f]['st']} ({f}): pubblicato {pub['data']} IA={int(pub['IA'])} PA={int(pub['PA'])} HM={int(pub['HM'])}"
                     f" | API {api['data']} IA={int(api['IA'])} PA={int(api['PA'])} HM={int(api['HM'])} → {'OK' if ok else 'DIVERSO'}")
    print("Disastri, 10 valori ricontrollati sull'API OpenFEMA:\n" + "\n".join(righe))


# ---------------------------------------------------------------- sezione California (FAIR Plan e non rinnovi)
CA_CACHE = RADICE / "cache" / "california"


def _ca_file(chiave, F):
    """File sorgente in cache con l'impronta registrata da raccolta/california.py; se manca e c'è rete lo riscarica."""
    import hashlib
    import urllib.request
    v = F[chiave]
    f = CA_CACHE / v["file"]
    if not f.exists():
        if "--senza-rete" in sys.argv:
            return None
        CA_CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(v["url"], headers={"User-Agent": "floodcost-check/1.0"})
        f.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    if hashlib.sha256(f.read_bytes()).hexdigest() != v["sha256"]:
        errore(f"California: {v['file']} ha un'impronta diversa da quella registrata (la fonte è cambiata: rifare raccolta/california.py)")
        return None
    return f


def _ca_num(t):
    t = t.replace("$", "").replace(",", "").replace(" ", "").strip()
    return 0 if t in ("", "-") else int(t)


def _ca_5anni_pdfplumber(f):
    """Polizze o valore per ZIP (5 anni) letti con pdfplumber (raccolta usa pdftotext): celle separate dai token 'NN%'."""
    import pdfplumber
    out = {}
    with pdfplumber.open(str(f)) as pdf:
        for pg in pdf.pages:
            for l in (pg.extract_text() or "").splitlines():
                m = re.match(r"(\d{5}|Total) (.+)$", l)
                if not m:
                    continue
                celle = []
                for tok in m.group(2).replace("$", " ").split():
                    if re.fullmatch(r"-?\d+%", tok):
                        celle.append([int(tok[:-1]), ""])
                    elif celle:
                        celle[-1][1] += tok
                if len(celle) != 5:
                    errore(f"California: riga non letta in {f.name}: {l[:80]}")
                    continue
                out[m.group(1)] = ([_ca_num(c[1]) for c in celle][::-1], [c[0] for c in celle][::-1])
    return out


def _ca_categorie_pdftotext(f, dollari):
    """Polizze o premio per categoria letti con pdftotext -layout (raccolta usa pdfplumber)."""
    testo = subprocess.run(["pdftotext", "-layout", str(f), "-"], check=True, capture_output=True, text=True).stdout
    out = {}
    for l in testo.splitlines():
        m = re.match(r"\s*(\d{5}|All)\s", l)
        if not m:
            continue
        if dollari:
            celle = l.split("$")[1:]
            v = [_ca_num(c) for c in celle]
        else:
            v = [_ca_num(t) for t in l.split()[-15:]]
        if len(v) != 15:
            errore(f"California: riga non letta in {f.name}: {l.strip()[:80]}")
            continue
        out[m.group(1)] = v
    return out


def _ca_xlsx_xml(f):
    """XLSX del CDI letto direttamente dall'XML (raccolta usa openpyxl): {zip: {anno: [nuove, rinnovate, non rinnovate]}}."""
    import xml.etree.ElementTree as ET
    import zipfile
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(f) as zf:
        stringhe = []
        if "xl/sharedStrings.xml" in zf.namelist():
            for si in ET.fromstring(zf.read("xl/sharedStrings.xml")).findall("m:si", ns):
                stringhe.append("".join(t.text or "" for t in si.iter(f"{{{ns['m']}}}t")))
        foglio = sorted(n for n in zf.namelist() if n.startswith("xl/worksheets/sheet"))[0]
        radice = ET.fromstring(zf.read(foglio))
    out = {}
    for riga in radice.iter(f"{{{ns['m']}}}row"):
        celle = {}
        for c in riga.findall("m:c", ns):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v = c.find("m:v", ns)
            if v is None:
                continue
            celle[col] = stringhe[int(v.text)] if c.get("t") == "s" else v.text
        if not str(celle.get("B", "")).strip().replace(".0", "").isdigit():
            continue
        z = f'{int(float(celle["B"])):05d}'
        a = str(int(float(celle["C"])))
        out.setdefault(z, {})[a] = [int(float(celle.get(k, 0) or 0)) for k in ("D", "E", "F")]
    return out


def _ca_appendice_fact_sheet(f):
    import pdfplumber
    out = {}
    with pdfplumber.open(str(f)) as pdf:
        testo = "\n".join(pg.extract_text() or "" for pg in pdf.pages)
    i = testo.find("Appendix A")
    for a, n, r, nr in re.findall(r"^(20\d\d) ([\d,]+) ([\d,]+) ([\d,]+) ", testo[i:i + 3000], re.M):
        out.setdefault(a, [_ca_num(n), _ca_num(r), _ca_num(nr)])
    return out


def _ca_attesi(Z, zips, ult):
    """Numeri di un gruppo di ZIP calcolati qui, dai file riletti (non dalle funzioni di genera.py)."""
    pif = sum(Z[z]["pif"][-1] for z in zips if "pif" in Z[z])
    pif0 = sum(Z[z]["pif"][0] for z in zips if "pif" in Z[z])
    tiv = sum(Z[z]["tiv"][-1] for z in zips if "pif" in Z[z])
    n = sum(Z[z]["pol"][i] for z in zips if "pol" in Z[z] and "prem" in Z[z] for i in (0, 5, 10))
    p = sum(Z[z]["prem"][i] for z in zips if "pol" in Z[z] and "prem" in Z[z] for i in (0, 5, 10))
    c = [sum((Z[z].get("cdi") or {}).get(ult, [0, 0, 0])[i] for z in zips) for i in range(3)]
    avg = round(p / n) if n >= G.CA_MIN else None
    tasso = round(c[2] / (c[0] + c[1]) * 100, 1) if c[0] + c[1] >= G.CA_MIN_CDI else None
    return {"pif": pif, "pif0": pif0, "tiv": tiv, "avg": avg, "nr": c[2], "tasso": tasso}


def _ca_attr_ok(t, dove, e, cosa):
    m = re.search(r'data-pif="(\d+)" data-pif0="(\d+)" data-tiv="(\d+)" data-avg="(\d*)" data-nr="(\d+)" data-tasso="([\d.]*)"', dove)
    if not m:
        errore(f"California {cosa}: attributi dei numeri mancanti")
        return
    pub = {"pif": int(m.group(1)), "pif0": int(m.group(2)), "tiv": int(m.group(3)), "avg": int(m.group(4)) if m.group(4) else None,
           "nr": int(m.group(5)), "tasso": float(m.group(6)) if m.group(6) else None}
    if pub != e:
        errore(f"California {cosa}: pubblicato {pub}, ricalcolato dalle fonti {e}")
    testo = unescape(re.sub(r"<[^>]+>", " ", dove))
    for v in (G.intero(e["pif"]), G.usd(e["avg"]) if e["avg"] else None, f'{e["tasso"]:.1f}%' if e["tasso"] is not None else None):
        if v and v not in testo:
            errore(f"California {cosa}: il numero {v} non è nel testo")


def controlla_california():
    """Sezione California home insurance (dati/california.json):
    - impronta dei dati; fonti con url, data di lettura e impronta SHA-256; file in cache con la stessa impronta (riscaricati se mancano);
    - ricalcolo indipendente dai file sorgente con motori diversi da raccolta/california.py (pdfplumber per i PDF a 5 anni, pdftotext
      per i PDF per categoria, XML grezzo per l'XLSX CDI): ogni numero di ogni ZIP uguale ai dati; somme = righe Total/All; totali CDI
      = appendice A del fact sheet; crescite stampate nel PDF = crescite ricalcolate (±1 punto);
    - pagine attese (indice + aree con domanda) e solo quelle, nella sitemap con lastmod = data di lettura, titoli <= 70 caratteri;
      numeri della scheda, di ogni riga ZIP, delle contee, dei blocchi nelle pagine ZIP NFIP e della ricerca uguali al ricalcolo;
    - prima frase con il dato e la data; limiti scritti (2023, 75-80%), avviso "not a quote", rimandi CDI e FAIR Plan, fonti con impronta;
      nessuna frase da consulenza; nessun link di affiliazione finché casa_california.url è vuoto;
    - FAQ: ogni domanda viene da una ricerca salvata (autocomplete) e il JSON-LD FAQPage è uguale al testo visibile;
    - link: indice <-> aree, blocchi ZIP -> indice, pagine NFIP California (Stato, contee) -> sezione;
    - con la rete: le frasi ufficiali citate sono ancora nelle pagine d'origine e la pagina FAIR Plan collega ancora gli stessi file."""
    import hashlib
    if not G.CA:
        print("Sezione California: dati assenti, controllo saltato.")
        return
    D = json.loads((DATI / "california.json").read_text(encoding="utf-8"))
    imp = D.pop("impronta", None)
    if hashlib.sha256(json.dumps(D, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest() != imp:
        errore("california.json: impronta diversa dal contenuto")
    F = D["fonti"]
    for k in ("pif_zip", "tiv_zip", "pol_cat", "prem_cat", "cdi_zip", "cdi_fact", "geonames"):
        v = F.get(k) or {}
        if not (str(v.get("url", "")).startswith("https://") and re.fullmatch(r"[0-9a-f]{64}", v.get("sha256", "")) and v.get("letto_il")):
            errore(f"California: fonte {k} senza url https, impronta o data di lettura")
    ult = G.CA_CDI_ULT
    Z = D["zip"]
    # 1. ricalcolo dai file sorgente
    file_ = {k: _ca_file(k, F) for k in ("pif_zip", "tiv_zip", "pol_cat", "prem_cat", "cdi_zip", "cdi_fact")}
    ricalcolati = 0
    if all(file_.values()):
        pif = _ca_5anni_pdfplumber(file_["pif_zip"])
        tiv = _ca_5anni_pdfplumber(file_["tiv_zip"])
        pol = _ca_categorie_pdftotext(file_["pol_cat"], False)
        prem = _ca_categorie_pdftotext(file_["prem_cat"], True)
        cdi = _ca_xlsx_xml(file_["cdi_zip"])
        app = _ca_appendice_fact_sheet(file_["cdi_fact"])
        diversi = []
        for z, r in Z.items():
            for chiave, fonte in (("pif", pif), ("tiv", tiv)):
                atteso = fonte.get(z)
                if (chiave in r) != (atteso is not None) or (atteso and (r[chiave] != atteso[0] or r[chiave + "_g"] != atteso[1])):
                    diversi.append(f"{z} {chiave}")
            for chiave, fonte in (("pol", pol), ("prem", prem)):
                if r.get(chiave) != fonte.get(z):
                    diversi.append(f"{z} {chiave}")
            if r.get("cdi") != cdi.get(z):
                diversi.append(f"{z} cdi")
            ricalcolati += 1
        mancanti = (set(pif) - {"Total"} - set(Z)) | (set(cdi) - set(Z)) | (set(pol) - {"All"} - set(Z))
        if mancanti:
            errore(f"California: ZIP delle fonti assenti nei dati: {sorted(mancanti)[:10]}")
        if diversi:
            errore(f"California: {len(diversi)} valori diversi tra dati e fonti rilette, es. {diversi[:8]}")
        for i in range(5):
            for nome, fonte in (("polizze", pif), ("valore", tiv)):
                s = sum(v[0][i] for k, v in fonte.items() if k != "Total")
                if s != fonte["Total"][0][i]:
                    errore(f"California: {nome} {G.CA_ANNI[i]}: somma ZIP {s:,} ≠ Total {fonte['Total'][0][i]:,}")
        if G.CA_F["pif_tot"] != pif["Total"][0] or G.CA_F["tiv_tot"] != tiv["Total"][0]:
            errore("California: totali FAIR Plan dei dati diversi dalla riga Total del PDF")
        for i in range(15):
            if sum(v[i] for k, v in prem.items() if k != "All") != prem["All"][i]:
                errore(f"California: premi, colonna {i}: le righe non sommano alla riga All")
        assenti = sorted(set(prem) - set(pol))
        if sum(pol["All"]) - sum(sum(v) for k, v in pol.items() if k != "All") != sum(pif[z][0][-1] for z in assenti if z in pif):
            errore(f"California: polizze per categoria: la differenza con la riga All non è spiegata dagli ZIP assenti {assenti}")
        if sum(pol["All"]) != pif["Total"][0][-1]:
            errore("California: riga All delle polizze per categoria ≠ totale polizze per ZIP")
        for a in G.CA_CDI_ANNI:
            s = [sum(v.get(a, [0, 0, 0])[i] for v in cdi.values()) for i in range(3)]
            if s != G.CA["cdi"]["stato"][a] or (a in app and app[a] != s):
                errore(f"California: totali CDI {a}: XLSX {s}, dati {G.CA['cdi']['stato'][a]}, fact sheet {app.get(a)}")
        if not app:
            errore("California: appendice A del fact sheet non letta")
        cresc = 0
        for k, (v, g) in pif.items():
            for i in range(1, 5):
                if v[i - 1] > 0 and abs((v[i] - v[i - 1]) / v[i - 1] * 100 - g[i]) > 1:
                    cresc += 1
        if cresc:
            errore(f"California: {cresc} crescite stampate nel PDF diverse dal ricalcolo")
        Zv = {z: {"pif": pif[z][0], "tiv": tiv[z][0]} if z in pif else {} for z in Z}
        for z in Zv:
            if z in pol and z in prem:
                Zv[z]["pol"], Zv[z]["prem"] = pol[z], prem[z]
            if z in cdi:
                Zv[z]["cdi"] = cdi[z]
        print(f"California: {ricalcolati:,} ZIP ricontrollati sui file sorgente (pdfplumber, pdftotext, XML), totali e fact sheet coincidono.")
    else:
        print("California: file sorgente non disponibili (--senza-rete): ricalcolo dai PDF/XLSX saltato, controlli sulle pagine con i dati.")
        Zv = Z
    # 2. pagine
    aree = G.ca_aree()
    attese = {G.CA_DIR} | {u for _, _, u, _ in aree}
    trovate = {p.relative_to(SITO).as_posix()[:-len("index.html")] for p in (SITO / G.CA_DIR).rglob("index.html")}
    for x in sorted(attese ^ trovate):
        errore(f"California: pagina {'mancante' if x in attese else 'in più'} {x}")
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    for x in sorted(attese):
        if f"<loc>{G.URL_SITO}/{x}</loc><lastmod>{G.CA_OGGI}</lastmod>" not in sm:
            errore(f"California: {x} non è nella sitemap con lastmod {G.CA_OGGI}")
    ricerche = G.ca_ricerche()
    consiglio = re.compile(r"\byou should\b|\bwe recommend\b|\bbest (?:home )?insurance\b|\bcheapest\b|\bswitch to\b|\byou qualify\b|\byou are eligible\b", re.I)
    aff_acceso = bool((G.AFFILIATI.get("casa_california") or {}).get("url"))
    data_al = G.data_lunga(G.CA_AL)
    data_pub = G.data_lunga(G.CA_PUB)
    for x in sorted(attese & trovate):
        t = (SITO / x / "index.html").read_text(encoding="utf-8")
        tit = unescape(re.search(r"<title>(.*?)</title>", t, re.S).group(1))
        if len(tit) > 70:
            errore(f"California {x}: titolo di {len(tit)} caratteri")
        prima = unescape(re.search(r'<p class="sub">(.*?)</p>', t, re.S).group(1))
        if not (prima.startswith(f"On {data_al}, the California FAIR Plan had ") and f"dated {data_pub}" in prima):
            errore(f"California {x}: la prima frase non dà il dato con la data")
        corpo = unescape(re.sub(r"<[^>]+>", " ", t[t.find("<main"):t.find("</main>")]))
        for frase in ("not a quote", f"Non-renewals stop in {ult}", "75-80%", G.TEL_CDI, "Questions people ask"):
            if frase not in corpo:
                errore(f"California {x}: manca '{frase}'")
        for u in (G.URL_CDI_AIUTO, G.URL_CFP_APPLY, G.URL_CDI_FINDER, G.URL_CFP, G.URL_CDI_DATI):
            if f'href="{u}"' not in t:
                errore(f"California {x}: manca il rimando {u}")
        for k in ("pif_zip", "tiv_zip", "pol_cat", "prem_cat", "cdi_zip", "cdi_fact"):
            if F[k]["sha256"][:12] not in t or f'href="{F[k]["url"]}"' not in t:
                errore(f"California {x}: fonte {k} senza link o impronta")
        m = consiglio.search(corpo)
        if m:
            errore(f"California {x}: frase da consulenza '{m.group(0)}'")
        if not aff_acceso and ('rel="sponsored' in t or "quote-box" in t):
            errore(f"California {x}: riquadro o link di affiliazione con casa_california spento")
        # FAQ = JSON-LD, domande da ricerche vere
        faq_dati = G.ca_faq_indice_dati() if x == G.CA_DIR else next(G.ca_faq_area_dati(tp, nm, zz) for tp, nm, u, zz in aree if u == x)
        vis = [(unescape(q), unescape(a)) for q, a in re.findall(r'<details class="faq"><summary>(.*?)</summary><p>(.*?)</p></details>', t, re.S)]
        ld = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        fq = [b for b in ld if b.get("@type") == "FAQPage"]
        if not fq:
            errore(f"California {x}: manca il JSON-LD FAQPage")
        else:
            ldq = [(q["name"], q["acceptedAnswer"]["text"]) for q in fq[0]["mainEntity"]]
            if ldq != vis or vis != [(f["q"], f["a"]) for f in faq_dati]:
                errore(f"California {x}: FAQ visibili, JSON-LD e dati diversi")
        for f in faq_dati:
            if f["ricerca"].lower() not in ricerche:
                errore(f"California {x}: la FAQ '{f['q']}' non viene da una ricerca salvata ({f['ricerca']})")
        # numeri: scheda e righe ZIP
        zips = sorted(Zv) if x == G.CA_DIR else next(zz for _, _, u, zz in aree if u == x)
        if x == G.CA_DIR:
            e = _ca_attesi(Zv, [z for z in Zv if z != "Total"], ult)
        else:
            e = _ca_attesi(Zv, zips, ult)
        sch = re.search(r'<section class="card key[^"]*" aria-label="Key figures"(.*?)</section>', t, re.S)
        _ca_attr_ok(t, sch.group(0) if sch else "", e, f"{x} scheda")
        for z, riga in re.findall(r'<tr data-z="(\d{5})">(.*?)</tr>', t, re.S):
            ez = _ca_attesi(Zv, [z], ult)
            celle = [unescape(re.sub(r"<[^>]+>", " ", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", riga, re.S)]
            r = Zv.get(z, {})
            atteso = [G.intero(ez["pif0"]) if "pif" in r else "–", G.intero(ez["pif"]) if "pif" in r else "–", G.usd(ez["avg"]),
                      G.intero(ez["nr"]) if "cdi" in r else "–", f'{ez["tasso"]:.1f}%' if ez["tasso"] is not None else "–"]
            if [celle[1], celle[2], celle[4], celle[5], celle[6]] != atteso:
                errore(f"California {x}: riga ZIP {z} {celle[1:]} diversa dal ricalcolo {atteso}")
            if G.ca_ha_zip_nfip(z) and f'href="../{G.url_zip(z)}"' not in riga and f'href="../../{G.url_zip(z)}"' not in riga:
                errore(f"California {x}: la riga {z} non collega la pagina ZIP")
        for c, riga in re.findall(r'<tr data-contea="([^"]+)">(.*?)</tr>', t, re.S):
            ec = _ca_attesi(Zv, [z for z in Zv if Z.get(z, {}).get("contea") == unescape(c) and Z[z].get("fips")], ult)
            testo = unescape(re.sub(r"<[^>]+>", " ", riga))
            if G.intero(ec["pif"]) not in testo or G.usd(ec["avg"]) not in testo:
                errore(f"California {x}: contea {c} con numeri diversi dal ricalcolo")
        if x == G.CA_DIR:
            for _, _, u, _ in aree:
                if f'href="../{u}"' not in t:
                    errore(f"California: l'indice non collega {u}")
        elif f'href="../../{G.CA_DIR}"' not in t:
            errore(f"California {x}: non collega l'indice")
    # 3. blocco nelle pagine ZIP NFIP della California, rimandi da Stato e contee
    n_blocchi = 0
    for z, v in G.ZIPS.items():
        if v["st"] != "CA":
            continue
        t = (SITO / G.url_zip(z) / "index.html").read_text(encoding="utf-8")
        if z not in Z or ("pif" not in Z[z] and "cdi" not in Z[z]):
            if "data-ca-zip" in t:
                errore(f"California: blocco nella pagina ZIP {z} senza dati")
            continue
        m = re.search(r'<section class="ca-zip" data-ca-zip="' + z + r'"(.*?)</section>', t, re.S)
        if not m:
            errore(f"California: manca il blocco FAIR Plan nella pagina ZIP {z}")
            continue
        n_blocchi += 1
        _ca_attr_ok(t, m.group(0), _ca_attesi(Zv, [z], ult), f"ZIP {z} blocco")
        b = unescape(re.sub(r"<[^>]+>", " ", m.group(0)))
        if f"On {data_al}" not in b or f"stop in {ult}" not in b or "75-80%" not in b or "not a quote" not in b:
            errore(f"California: blocco ZIP {z} senza data, limiti o avviso")
        if f'href="../../{G.CA_DIR}"' not in m.group(0):
            errore(f"California: il blocco ZIP {z} non collega la sezione")
    t = (SITO / G.url_stato("CA") / "index.html").read_text(encoding="utf-8")
    if f'href="../{G.CA_DIR}"' not in t:
        errore("California: la pagina NFIP dello Stato non collega la sezione")
    for f_, C in G.CONTEE.items():
        if C["st"] == "CA" and any(r.get("fips") == f_ for r in Z.values()):
            if G.CA_DIR not in (SITO / G.url_contea(f_) / "index.html").read_text(encoding="utf-8"):
                errore(f"California: la contea NFIP {f_} non collega la sezione")
    # 4. ricerca nel browser
    s = json.loads((SITO / "data" / "california-zip.json").read_text(encoding="utf-8"))
    for row in s["z"]:
        e = _ca_attesi(Zv, [row[0]], ult)
        r = Zv.get(row[0], {})
        if [row[3], row[4], row[5], row[6], row[7]] != [e["pif0"] if "pif" in r else None, e["pif"] if "pif" in r else None, e["avg"],
                                                        e["nr"] if "cdi" in r else None, e["tasso"]]:
            errore(f"California: ricerca, ZIP {row[0]} diverso dal ricalcolo")
            break
    print(f"Sezione California: {len(trovate)} pagine ({', '.join(sorted(trovate))}), blocco FAIR Plan in {n_blocchi} pagine ZIP; "
          f"dati letti il {G.CA_OGGI}, impronta {str(imp)[:12]}.")
    if "--senza-rete" not in sys.argv:
        controlla_california_rete(F)


def controlla_california_rete(F):
    """Le frasi ufficiali citate sono ancora nelle pagine d'origine; la pagina FAIR Plan collega ancora i file usati (altrimenti: nuovo rilascio)."""
    import urllib.request

    def testo(u):
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (floodcost-check)"})
        h_ = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", errors="replace")
        h_ = re.sub(r"<(script|style).*?</\1>", " ", h_, flags=re.S | re.I)
        return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", h_))).replace("’", "'")
    ok = 0
    for u, frasi in G.CA_CITAZIONI.items():
        try:
            t = testo(u)
        except Exception as e:
            errore(f"California: pagina citata non leggibile {u}: {e} (usare --senza-rete per saltare)")
            continue
        for f in frasi:
            if f.replace("’", "'") not in t:
                errore(f"California: la frase citata non è più in {u}: {f[:70]}")
            else:
                ok += 1
    try:
        pag = urllib.request.urlopen(urllib.request.Request(G.URL_CFP, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "replace")
        for k in ("pif_zip", "tiv_zip", "pol_cat", "prem_cat"):
            if F[k]["file"] not in pag:
                print(f"  AVVISO California: la pagina FAIR Plan non collega più {F[k]['file']}: c'è un rilascio nuovo, rifare raccolta/california.py")
    except Exception as e:
        errore(f"California: pagina FAIR Plan non leggibile: {e}")
    print(f"California, citazioni ufficiali ricontrollate: {ok} su {sum(len(v) for v in G.CA_CITAZIONI.values())}.")


def main():
    controlla_pagine()
    controlla_dati()
    controlla_parole()
    controlla_cache()
    controlla_indexnow()
    controlla_monetizzazione()
    controlla_disastri()
    controlla_california()
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
