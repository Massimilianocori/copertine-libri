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


def main():
    controlla_pagine()
    controlla_dati()
    controlla_parole()
    controlla_cache()
    controlla_indexnow()
    controlla_monetizzazione()
    controlla_disastri()
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
