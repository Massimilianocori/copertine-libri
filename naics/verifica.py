"""Controlli del sito NAICS Code Lookup. Rilegge i file ufficiali con un lettore xlsx proprio (zipfile + XML, non openpyxl né estrai.py).

Uso (dalla radice del repository):
    python3 naics/verifica.py             # fonti, dati, pagine, FAQ, indicizzazione, testi, monetizzazione
    python3 naics/verifica.py --browser   # anche le prove nel browser (Playwright, 375 e 1280 px, chiaro e scuro)

1. Fonti: impronta SHA-256 dei file in raccolta/_grezzi = dati/fonti.json; HTTP 200; ogni frase cercata è nel testo dei PDF salvati.
2. Dati: codici e titoli riletti dal file 2-6 cifre = naics.json; albero 2→3→4→5→6 (padri, livelli, forma dei codici); conteggi per settore e
   totali = «Structure Summary Table» riletta qui; 50 codici a caso (seme fisso) confrontati con i file ufficiali delle descrizioni, dell'indice
   e della concordanza 2022→2017, e con la loro pagina pubblicata (titolo, testo della descrizione, ogni voce dell'indice, codici 2017, codici SIC).
3. Contenuti: ogni codice ha la sua pagina o ancora con il titolo ufficiale; ogni voce dell'indice ufficiale (20.373) è nella pagina del suo codice;
   tabella 2017 → 2022 e tabella SIC → NAICS complete.
4. Pagine: titoli ≤ 65 e descrizioni ≤ 160 (70-160 per le indicizzate) unici; un h1; canonical = sitemap; noindex senza canonical né pubblicità;
   id unici; link interni e ancore; link esterni solo verso domini previsti; GoatCounter, robots, IndexNow, netlify.toml con `ignore`, og.png.
5. FAQ: ogni domanda nasce da una ricerca salvata; JSON-LD FAQPage = testo visibile, solo dove ci sono FAQ; titoli citati ufficiali.
6. Indicizzazione: ricalcolata dalle pagine scritte (stessa regola di genera.py).
7. Testi: nessun nome di modelli di IA, nessun dato personale, nessuna frase di consiglio; niente soglie SBA né conseguenze fiscali nei testi
   nostri (le pagine di codice riportano i testi ufficiali parola per parola: lì il controllo non si applica); nessuna chiave.
8. Monetizzazione: monetizzazione.controlla_sito("naics").
"""
import hashlib
import json
import random
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
GREZZI = RADICE / "raccolta" / "_grezzi"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

URL_SITO = "https://naics-code-lookup.netlify.app"
FRASE_FISSA = "check with the agency or form that asks for the code"
MIN_PAROLE_PROPRIE, MAX_SOVRAPPOSIZIONE, QUOTA_MODELLO = 120, 0.55, 0.05
MIN_PROPRIE_RICHIESTA, MAX_SOVRAPPOSIZIONE_RICHIESTA = 60, 0.65  # pagine a 6 cifre con domanda dimostrata (dati/richieste.json)
MAX_INDICE_GZ, MAX_FRASI_GZ = 70_000, 260_000  # byte compressi dei due file della ricerca (il secondo si scarica solo se si scrive una parola)
PAROLE_VUOTE = {"naics", "naic", "sic", "code", "codes", "number", "lookup", "for", "a", "an", "the", "and", "of", "in", "business", "company", "service",
                "services", "shop", "store", "2022"}
DOMINI_ESTERNI = ["naics-code-lookup.netlify.app", "census.gov", "irs.gov", "goatcounter.com", "zgo.at", "policies.google.com", "adssettings.google.com", "schema.org"]
ERR, AVV = [], []


def errore(m):
    ERR.append(m)


def carica(n):
    return json.loads((DATI / n).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
NA = carica("naics.json")
DOM = carica("domanda.json")
FAQ = carica("faq.json")["faq"]
VOL = carica("volumi.json")
ATT = carica("attivita.json")["attivita"]
RICH = carica("richieste.json")["codici"]
C = NA["codici"]


def codici_richiesti():
    """Codici a 6 cifre con domanda dimostrata, ricalcolati qui: scritti per numero in un suggerimento salvato, oppure in richieste.json
    con un suggerimento salvato le cui parole sono tutte nel titolo, nella descrizione, negli esempi o nell'indice ufficiale del codice."""
    tutte = {s for v in DOM["radici"].values() for s in v}
    out = {c for s in tutte for c in re.findall(r"(?<!\d)\d{6}(?!\d)", s) if c in C and C[c]["l"] == 6}
    for c, s in RICH.items():
        if c not in C or C[c]["l"] != 6:
            errore(f"richieste.json: {c} non è un codice a 6 cifre del 2022")
            continue
        if s not in tutte:
            errore(f"richieste.json: «{s}» non è tra i suggerimenti salvati")
            continue
        parole = {w for w in re.findall(r"[a-z]+", s.lower()) if w not in PAROLE_VUOTE}
        testo = set(re.findall(r"[a-z]+", " ".join([C[c]["t"]] + C[c]["d"] + C[c]["idx"] + C[c]["es"]).lower()))
        if not parole or any(not any(x.startswith(w[:5]) for x in testo) for w in parole):
            errore(f"richieste.json: «{s}» non corrisponde ai testi ufficiali di {c}")
            continue
        out.add(c)
    return out


def visibile(html):
    t = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("''", '"')
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"\s+([,.;:)»])", r"\1", re.sub(r"([(«])\s+", r"\1", t))


def pagine_html():
    return sorted(SITO.rglob("*.html"))


def leggi_pagina(percorso):
    p = SITO / percorso.lstrip("/")
    if percorso.endswith("/") or not percorso.strip("/"):
        p = SITO / percorso.strip("/") / "index.html"
    return p.read_text(encoding="utf-8") if p.exists() else None


# ---------------------------------------------------------------- lettore xlsx proprio
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def xlsx(nome):
    """Righe del primo foglio come liste di testi (celle vuote = ''), lette direttamente dall'XML."""
    with zipfile.ZipFile(GREZZI / nome) as z:
        condivise = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                condivise.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
        fogli = sorted(n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n))
        radice = ET.fromstring(z.read(fogli[0]))
    righe = []
    for r in radice.find("m:sheetData", NS).findall("m:row", NS):
        riga = {}
        for c in r.findall("m:c", NS):
            ref = re.match(r"([A-Z]+)", c.get("r")).group(1)
            col = 0
            for ch in ref:
                col = col * 26 + ord(ch) - 64
            v = c.find("m:v", NS)
            if c.get("t") == "s":
                val = condivise[int(v.text)]
            elif c.get("t") == "inlineStr":
                val = "".join(t.text or "" for t in c.iter("{%s}t" % NS["m"]))
            else:
                val = v.text if v is not None else ""
                if val and re.fullmatch(r"\d+\.0", val):
                    val = val[:-2]
            riga[col - 1] = val or ""
        righe.append([riga.get(i, "") for i in range(max(riga) + 1)] if riga else [])
    return righe


def tit(x):
    t = re.sub(r"\s+", " ", x).strip()
    return t[:-1].rstrip() if t.endswith("T") and not t.endswith(" T") else t


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti():
    n = 0
    for fid, f in FJ["file"].items():
        p = GREZZI / f["file"]
        if not p.exists():
            errore(f"fonte {fid}: file grezzo assente ({p.name}): rilanciare raccolta/fonti.py")
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256"]:
            errore(f"fonte {fid}: impronta diversa da fonti.json")
        if f.get("http") != 200:
            errore(f"fonte {fid}: HTTP {f.get('http')}")
        if f.get("trovate"):
            testo = norm(subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout)
            for c, ok in f["trovate"].items():
                n += 1
                if not ok or norm(c) not in testo:
                    errore(f"fonte {fid}: frase non trovata «{c[:60]}»")
    print(f"Fonti: {len(FJ['file'])} file, impronte uguali a fonti.json, HTTP 200, {n} frasi ritrovate nei PDF salvati")


# ---------------------------------------------------------------- 2. dati
def controlla_dati():
    r = xlsx(FJ["file"]["codici"]["file"])
    ufficiali = {}
    for x in r[2:]:
        if len(x) > 2 and x[1]:
            ufficiali[x[1].strip()] = tit(x[2])
    if set(ufficiali) != set(C):
        errore(f"dati: codici diversi dal file ufficiale {sorted(set(ufficiali) ^ set(C))[:5]}")
    for c, t in ufficiali.items():
        if c in C and C[c]["t"] != t:
            errore(f"dati: titolo di {c} diverso dal file ufficiale")
    rng = {"31": "31-33", "32": "31-33", "33": "31-33", "44": "44-45", "45": "44-45", "48": "48-49", "49": "48-49"}
    figli = defaultdict(list)
    for c, v in C.items():
        if not re.fullmatch(r"\d{2,6}|\d{2}-\d{2}", c):
            errore(f"albero: forma del codice {c}")
        l = 2 if "-" in c else len(c)
        p = None if l == 2 else (rng.get(c[:2], c[:2]) if l == 3 else c[:-1])
        if v["l"] != l or v["p"] != p:
            errore(f"albero: livello o padre di {c} sbagliati")
        if p:
            figli[p].append(c)
    for c, v in C.items():
        if v["l"] < 6 and not figli[c]:
            errore(f"albero: {c} senza figli")
    cnt = defaultdict(Counter)
    for c, v in C.items():
        s = c
        while C[s]["l"] > 2:
            s = C[s]["p"]
        cnt[s][v["l"]] += 1
    tab = xlsx(FJ["file"]["conteggi"]["file"])
    tot = Counter()
    for x in tab[2:]:
        if len(x) < 8 or not x[1]:
            continue
        if x[1] == "Total":
            tot_uff = [int(x[i]) for i in (2, 3, 4, 7)]
            continue
        s = x[0].strip()
        mio = [cnt[s][3], cnt[s][4], cnt[s][5], cnt[s][6]]
        if mio != [int(x[i]) for i in (2, 3, 4, 7)]:
            errore(f"conteggi del settore {s}: {mio} invece di {[x[i] for i in (2, 3, 4, 7)]}")
        tot.update({3: mio[0], 4: mio[1], 5: mio[2], 6: mio[3]})
    if [tot[3], tot[4], tot[5], tot[6]] != tot_uff or len([c for c in C if C[c]["l"] == 2]) != 20:
        errore(f"totali {dict(tot)} diversi da quelli ufficiali {tot_uff}")
    # 50 codici a caso contro i file ufficiali e contro la pagina pubblicata
    desc = {x[0].strip(): x for x in xlsx(FJ["file"]["descrizioni"]["file"])[1:] if x}
    idx = defaultdict(list)
    for x in xlsx(FJ["file"]["indice"]["file"])[1:]:
        if x and x[0] != "******":
            idx[x[0].strip()].append(re.sub(r"\s+", " ", x[1]).strip())
    c17 = defaultdict(set)
    for x in xlsx(FJ["file"]["c22_17"]["file"])[3:]:
        if len(x) > 2 and x[0]:
            c17[x[0].strip()].add(x[2].strip())
    sei = sorted(c for c in C if C[c]["l"] == 6)
    campione = random.Random(20261113).sample(sei, 50)
    for c in campione:
        html = leggi_pagina(f"/{c}/")
        if html is None:
            errore(f"campione {c}: pagina assente")
            continue
        vis = norm(visibile(html))
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        if not h1 or unescape(h1.group(1)) != f"NAICS code {c}: {tit(ufficiali[c])}":
            errore(f"campione {c}: h1 senza il titolo ufficiale")
        d = desc[c][2] if len(desc[c]) > 2 else ""
        if tit(desc[c][1]) != tit(ufficiali[c]):
            errore(f"campione {c}: titolo diverso tra file delle descrizioni e file dei codici")
        corpo = re.split(r"Illustrative Examples:|Cross-References\.", d)[0]
        for par in re.split(r"\n\s*\n", corpo):
            par = norm(par)
            if par and par != "The Sector as a Whole" and par not in vis:
                errore(f"campione {c}: paragrafo della descrizione ufficiale assente dalla pagina «{par[:50]}»")
        if "Illustrative Examples:" in d:
            for e in re.split(r"Illustrative Examples:", d)[1].split("Cross-References.")[0].split("\n"):
                if e.strip() and norm(e) not in vis:
                    errore(f"campione {c}: esempio ufficiale assente «{e.strip()[:40]}»")
        for e in idx[c]:
            if norm(e) not in vis:
                errore(f"campione {c}: voce dell'indice assente «{e[:40]}»")
        for b in c17[c]:
            if f"#v-{b}" not in html and f"{c}: {b}" not in vis and b not in vis:
                errore(f"campione {c}: codice 2017 {b} assente")
        for s in {x["sic"] for x in NA["sic_di_22"][c]["righe"]}:
            if f"/sic-to-naics/#sic-{s}" not in html:
                errore(f"campione {c}: codice SIC {s} assente")
    print(f"Dati: {len(C)} codici e titoli = file ufficiale (lettore proprio); albero 2→3→4→5→6 integro; conteggi di 20 settori e totali = tabella "
          f"ufficiale ({tot_uff}); 50 codici a caso uguali ai file ufficiali (titolo, descrizione, esempi, {sum(len(idx[c]) for c in campione)} voci "
          f"dell'indice, codici 2017 e SIC nella pagina)")


# ---------------------------------------------------------------- 2b. catena SIC rifatta dai file grezzi e sua presentazione
def controlla_sic():
    """Rifà da zero, dai file ufficiali, la catena 2022 → 2017 → 2012 → 2007 → 2002 → 1997 → SIC 1987 per tutti i codici a 6 cifre e controlla
    che ogni pagina la presenti in modo onesto: «diretto» solo per identità a ogni passo; nelle altre, i SIC principali separati da quelli parziali."""
    try:
        import xlrd
    except ImportError:
        errore("xlrd assente: la catena SIC non si può rifare (pip install xlrd)")
        return

    def xls(chiave, foglio=0):
        wb = xlrd.open_workbook(str(GREZZI / FJ["file"][chiave]["file"]))
        ws = wb.sheet_by_name(foglio) if isinstance(foglio, str) else wb.sheet_by_index(foglio)
        return [ws.row_values(i) for i in range(ws.nrows)]

    def cod(x):
        return str(int(x)) if isinstance(x, float) else str(x or "").strip()

    def sei(x):
        x = cod(x)
        return x + "0" if re.fullmatch(r"\d{5}", x) else x

    def passo(righe, i_vecchio, i_nuovo):
        ind, av = defaultdict(set), defaultdict(set)
        for r in righe:
            if len(r) <= max(i_vecchio, i_nuovo):
                continue
            a, n = cod(r[i_vecchio]), cod(r[i_nuovo])
            if re.fullmatch(r"\d{6}", a) and re.fullmatch(r"\d{6}", n):
                ind[n].add(a)
                av[a].add(n)
        return ind, av
    passi = [passo(xlsx(FJ["file"]["c22_17"]["file"]), 2, 0), passo(xlsx(FJ["file"]["c12_17"]["file"]), 0, 2),
             passo(xls("c07_12"), 0, 2), passo(xls("c02_07"), 0, 2), passo(xls("c97_02", "Concordance 23 US NoD"), 0, 2)]
    if any(len(ind) < 1000 for ind, _ in passi):
        errore("catena SIC: una concordanza è stata letta male (meno di 1000 codici)")
    sic97, t97 = defaultdict(set), {}
    for r in xls("naics97_sic")[1:]:
        n, s = sei(r[0]), cod(r[3])
        if re.fullmatch(r"\d{6}", n) and s:
            sic97[n].add(s.zfill(4))
            t97[n] = str(r[2]).strip()

    def indietro(c):
        att, diretto = {c}, True
        for ind, av in passi:
            if ind.get(c) != {c} or av.get(c) != {c}:
                diretto = False
            att = set().union(*[ind.get(x, set()) for x in att]) if att else set()
        return att, diretto

    def avanti(n):
        att = {n}
        for ind, av in reversed(passi):
            att = set().union(*[av.get(x, set()) for x in att]) if att else set()
        return att
    n_dir = n_cat = n_princ = n_parz = 0
    for c in sorted(x for x in C if C[x]["l"] == 6):
        v97, diretto = indietro(c)
        miei = set().union(*[sic97.get(n, set()) for n in v97]) if v97 else set()
        html = leggi_pagina(f"/{c}/") or ""
        m = re.search(r'<h2 id="sic".*?(?=<h2 |<section class="fonti-box")', html, re.S)
        blocco = m.group(0) if m else ""
        pagina_sic = set(re.findall(r"#sic-(\d{4})", blocco))
        if pagina_sic != miei:
            errore(f"SIC {c}: la pagina ha {sorted(pagina_sic ^ miei)[:5]} diversi dalla catena rifatta dai file ufficiali")
            continue
        testa = unescape(re.sub(r"<[^>]+>", "", re.search(r"<h2 id=\"sic\">(.*?)</h2>", blocco, re.S).group(1)))
        if not miei:
            if "do not link this industry" not in blocco:
                errore(f"SIC {c}: nessun SIC nella catena ma la pagina non lo dice")
            continue
        if diretto:
            n_dir += 1
            if "applies as it is" not in blocco or "our derivation" in blocco:
                errore(f"SIC {c}: codice identico dal 1997 ma la pagina non lo presenta come riga ufficiale")
            continue
        n_cat += 1
        if "applies as it is" in blocco or "no official SIC line" not in blocco or "our derivation" not in blocco:
            errore(f"SIC {c}: codice cambiato dopo il 1997 presentato come riga ufficiale")
        # principali = SIC di un'industria del 1997 finita tutta in c, o con lo stesso titolo; gli altri sono solo pezzi
        princ = {s for n in v97 if avanti(n) == {c} or t97.get(n, "").lower() == C[c]["t"].lower() for s in sic97.get(n, set())}
        pezzi = blocco.split('id="sic-partial"')
        in_alto = set(re.findall(r"#sic-(\d{4})", pezzi[0])) if 'id="sic-closest"' in blocco else set()
        if princ:
            n_princ += 1
            if in_alto != princ or set(re.findall(r"\b\d{4}\b", testa)) - princ:
                errore(f"SIC {c}: i SIC principali in pagina {sorted(in_alto)} non sono quelli ricalcolati {sorted(princ)}")
            if len(pezzi) > 1 and ("<details" not in pezzi[1] or "only a piece" not in pezzi[1]):
                errore(f"SIC {c}: i SIC parziali devono stare chiusi, con la spiegazione")
        else:
            n_parz += 1
            if "partial match" not in testa and "no single equivalent" not in testa:
                errore(f"SIC {c}: solo corrispondenze parziali ma il titolo «{testa}» non lo dice")
        scheda = re.search(r"<span>SIC 1987</span><b>(.*?)</b>", html)
        if scheda and not princ and "(partial)" not in scheda.group(1):
            errore(f"SIC {c}: la scheda in alto mostra SIC parziali senza dirlo")
        if scheda and princ and set(re.findall(r"\d{4}", scheda.group(1))) - princ:
            errore(f"SIC {c}: la scheda in alto mostra SIC non principali")
    print(f"SIC: catena rifatta dai file ufficiali per tutti i codici a 6 cifre: {n_dir} con riga ufficiale diretta, {n_cat} derivati "
          f"({n_princ} con SIC principali separati dai parziali, {n_parz} solo parziali e dichiarati tali)")


# ---------------------------------------------------------------- 3. contenuti
def url_di(c):
    v = C[c]
    if v["l"] == 5:
        figli = [x for x in C if C[x]["p"] == c]
        return url_di(figli[0]) if len(figli) == 1 else f"/{c[:4]}/#n-{c}"
    return f"/{c}/"


def controlla_contenuti():
    figli = defaultdict(list)
    for c, v in C.items():
        if v["p"]:
            figli[v["p"]].append(c)
    n_voci = 0
    cache = {}
    for c, v in C.items():
        u = url_di(c)
        pag, _, anc = u.partition("#")
        if pag not in cache:
            cache[pag] = leggi_pagina(pag)
        html = cache[pag]
        if html is None:
            errore(f"{c}: pagina {pag} assente")
            continue
        if anc and f'id="{anc}"' not in html:
            errore(f"{c}: ancora {anc} assente in {pag}")
        vis = norm(visibile(html))
        if norm(v["t"]) not in vis:
            errore(f"{c}: titolo ufficiale assente dalla sua pagina")
        if v["l"] == 6:
            for e in v["idx"]:
                n_voci += 1
                if norm(e) not in vis:
                    errore(f"{c}: voce dell'indice assente «{e[:40]}»")
    t17 = leggi_pagina("/naics-2017-to-2022/")
    for a, _, b in NA["c17_22"]:
        if f'id="v-{a}"' not in t17:
            errore(f"tabella 2017: manca {a}")
    righe17 = re.findall(r'<tr id="v-(\d{6})">(.*?)</tr>', t17, re.S)
    attesi = defaultdict(set)
    for a, _, b in NA["c17_22"]:
        attesi[a].add(b)
    for a, riga in righe17:
        trovati = set(re.findall(r'href="/(\d{6})/"', riga))
        if trovati != attesi[a]:
            errore(f"tabella 2017: riga {a} con codici 2022 {sorted(trovati)} invece di {sorted(attesi[a])}")
    ts = leggi_pagina("/sic-to-naics/")
    n_sic = len(re.findall(r'<tr id="sic-\d{4}">', ts))
    if n_sic != len(NA["sic"]):
        errore(f"tabella SIC: {n_sic} righe invece di {len(NA['sic'])}")
    print(f"Contenuti: {len(C)} codici nella loro pagina o ancora con il titolo ufficiale; {n_voci} voci dell'indice ufficiale tutte nella pagina "
          f"del loro codice; tabella 2017 → 2022 ({len(righe17)} righe, codici uguali alla concordanza) e SIC → NAICS ({n_sic} righe) complete")


# ---------------------------------------------------------------- 4. pagine
def controlla_pagine():
    titoli, descr, canon = {}, {}, set()
    noindex = 0
    file_esistenti = {str(p.relative_to(SITO)) for p in SITO.rglob("*") if p.is_file()}
    cache_ids = {}
    for p in pagine_html():
        rel = str(p.relative_to(SITO))
        if re.fullmatch(r"google[0-9a-f]+\.html", p.name):
            continue
        html = p.read_text(encoding="utf-8")
        t = re.search(r"<title>(.*?)</title>", html)
        dsc = re.search(r'<meta name="description" content="([^"]*)"', html)
        if not t or not dsc:
            errore(f"{rel}: titolo o descrizione assenti")
            continue
        tt, dd = unescape(t.group(1)), unescape(dsc.group(1))
        ni = '<meta name="robots" content="noindex">' in html
        c = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        if len(tt) > 65:
            errore(f"{rel}: titolo di {len(tt)} caratteri (max 65)")
        if len(dd) > 160:
            errore(f"{rel}: descrizione di {len(dd)} caratteri (max 160)")
        if tt in titoli:
            errore(f"{rel}: titolo uguale a {titoli[tt]}")
        titoli[tt] = rel
        if ni:
            noindex += 1
            if c:
                errore(f"{rel}: noindex con canonical")
            if MON.adsense_attivo("naics") and MON.SEGNO_SENZA_ADSENSE not in html:
                errore(f"{rel}: pagina noindex senza il segno «niente pubblicità»")
            if "googlesyndication" in html:
                errore(f"{rel}: pubblicità in una pagina noindex")
        else:
            if len(dd) < 70:
                errore(f"{rel}: descrizione di {len(dd)} caratteri (min 70)")
            if dd in descr:
                errore(f"{rel}: descrizione uguale a {descr[dd]}")
            descr[dd] = rel
            atteso = URL_SITO + "/" + rel.replace("index.html", "")
            if not c or c.group(1) != atteso:
                errore(f"{rel}: canonical assente o diverso da {atteso}")
            else:
                canon.add(c.group(1))
        if html.count("<h1") != 1:
            errore(f"{rel}: {html.count('<h1')} h1")
        if 'data-goatcounter="https://rete-siti.goatcounter.com/count"' not in html:
            errore(f"{rel}: manca il contatore GoatCounter")
        if '<html lang="en-US">' not in html:
            errore(f"{rel}: lingua non en-US")
        vis = visibile(html)
        if FRASE_FISSA not in vis:
            errore(f"{rel}: manca la frase fissa")
        if "not affiliated with the U.S. Census Bureau" not in vis or "public domain" not in vis:
            errore(f"{rel}: manca la dichiarazione di indipendenza o l'attribuzione")
        ids = re.findall(r'\bid="([^"]+)"', html)
        doppi = [x for x, n in Counter(ids).items() if n > 1]
        if doppi:
            errore(f"{rel}: id doppi {doppi[:3]}")
        ids = set(ids)
        for href in set(re.findall(r'href="([^"]+)"', html)):
            href = unescape(href)
            if href.startswith(("http://", "https://")):
                host = re.match(r"https?://([^/]+)", href).group(1)
                if not any(host == d or host.endswith("." + d) for d in DOMINI_ESTERNI):
                    errore(f"{rel}: link esterno non previsto {host}")
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in ids:
                    errore(f"{rel}: ancora {href} inesistente")
                continue
            percorso, _, ancora = href.partition("#")
            percorso = percorso.split("?")[0]
            if not percorso.startswith("/"):
                errore(f"{rel}: link relativo {href}")
                continue
            dest = percorso.lstrip("/")
            if dest == "" or dest.endswith("/"):
                dest += "index.html"
            if dest not in file_esistenti:
                errore(f"{rel}: link interno rotto {href}")
            elif ancora:
                if dest not in cache_ids:
                    cache_ids[dest] = set(re.findall(r'\bid="([^"]+)"', (SITO / dest).read_text(encoding="utf-8")))
                if ancora not in cache_ids[dest]:
                    errore(f"{rel}: ancora {href} inesistente")
        for src in re.findall(r'(?:src|href|data-indice|data-frasi)="(/assets/[^"#]+)"', html):
            if src.lstrip("/") not in file_esistenti:
                errore(f"{rel}: risorsa assente {src}")
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    if locs != canon:
        errore(f"sitemap diversa dai canonical: {sorted(locs ^ canon)[:5]}")
    if f"Sitemap: {URL_SITO}/sitemap.xml" not in (SITO / "robots.txt").read_text(encoding="utf-8"):
        errore("robots.txt senza sitemap")
    chiave = "b5a26a844a465f58552debee2c8a0114"
    if not (SITO / f"{chiave}.txt").exists() or (SITO / f"{chiave}.txt").read_text(encoding="utf-8") != chiave:
        errore("file chiave IndexNow assente o diverso")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in (SITO / "netlify.toml").read_text(encoding="utf-8"):
        errore("netlify.toml senza la regola che evita pubblicazioni inutili")
    for f in ("assets/og.png", "404.html", "privacy/index.html", "about/index.html"):
        if not (SITO / f).exists():
            errore(f"manca {f}")
    # modulo delle correzioni: nessun campo per dati personali (stesso modulo approvato per milpay)
    moduli = 0
    for p in pagine_html():
        html = p.read_text(encoding="utf-8")
        rel = str(p.relative_to(SITO))
        for form in re.findall(r"<form\b.*?</form>", html, re.S):
            nomi = set(re.findall(r'name="([^"]+)"', form))
            if "data-netlify" in form:
                moduli += 1
                if rel != "how-we-check/index.html" or nomi != {"corrections", "form-name", "bot-field", "page", "message", "source"} or "data-correzioni" not in form:
                    errore(f"{rel}: il modulo delle correzioni deve avere solo pagina, messaggio e fonte: {sorted(nomi)}")
            elif 'role="search"' not in form:
                errore(f"{rel}: modulo inatteso con i campi {sorted(nomi)}")
        if re.search(r'type="(email|tel|password)"|autocomplete="(email|name|tel)"|name="(email|name|phone|consent)"', html):
            errore(f"{rel}: campo per dati personali")
    if moduli != 1:
        errore(f"moduli Netlify: {moduli} (atteso 1, in /how-we-check/)")
    priv = visibile((SITO / "privacy" / "index.html").read_text(encoding="utf-8"))
    if "does not ask for your name or email address" not in priv or re.search(r"your email address\b(?! or)|only if you give it|tick box", priv):
        errore("privacy: il testo sul modulo delle correzioni non corrisponde al modulo (nessun campo email, nessuna casella)")
    js = next(SITO.glob("assets/app.*.js")).read_text(encoding="utf-8")
    if "form[data-correzioni]" not in js or "caricaFrasi" not in js:
        errore("app.js: manca l'invio del modulo delle correzioni o il caricamento ritardato delle voci dell'indice")
    import gzip
    for modello, tetto in (("assets/index.*.json", MAX_INDICE_GZ), ("assets/entries.*.json", MAX_FRASI_GZ)):
        f = next(SITO.glob(modello), None)
        peso = len(gzip.compress(f.read_bytes())) if f else 0
        if not f or peso > tetto:
            errore(f"{modello}: {peso} byte compressi (max {tetto})")
    indice = next(SITO.glob("assets/index.*.json"), None)
    voci = json.loads(indice.read_text(encoding="utf-8")) if indice else []
    unici5 = {c for c in C if C[c]["l"] == 5 and sum(1 for x in C if C[x]["p"] == c) == 1}
    if {v[0] for v in voci if v[3] in ("2", "3", "4", "5", "6")} != set(C) - unici5:
        errore("indice di ricerca: non contiene tutti i codici NAICS 2022")
    if {v[0] for v in voci if v[3] == "sic"} != set(NA["sic"]):
        errore("indice di ricerca: non contiene tutti i codici SIC")
    print(f"Pagine: {len(pagine_html())} file HTML, {len(canon)} indicizzabili (= sitemap), {noindex} noindex senza pubblicità; "
          "titoli ≤ 65 e descrizioni ≤ 160 unici; link e ancore interne a posto; indice di ricerca completo")


# ---------------------------------------------------------------- 5. FAQ
def controlla_faq():
    sugg = {s for v in DOM["radici"].values() for s in v}
    domande = {}
    for x in FAQ:
        if x["ricerca"] not in sugg:
            errore(f"FAQ «{x['q'][:40]}»: ricerca «{x['ricerca']}» non tra i suggerimenti salvati")
        for fid in x["fonti"]:
            if fid not in FJ["file"]:
                errore(f"FAQ «{x['q'][:40]}»: fonte sconosciuta {fid}")
        domande[x["q"]] = x
    n, pagine_faq = 0, 0
    for p in pagine_html():
        html = p.read_text(encoding="utf-8")
        vis = norm(visibile(html))
        if re.search(r"\{[a-z_0-9]+\}", vis):
            errore(f"{p.relative_to(SITO)}: segnaposto non sostituito")
        blocchi_ld = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        ld_faq = [b for b in blocchi_ld if b.get("@type") == "FAQPage"]
        visibili = re.findall(r'<div class="faq"><h3>(.*?)</h3>', html)
        if bool(ld_faq) != bool(visibili):
            errore(f"{p.relative_to(SITO)}: FAQ visibili e JSON-LD FAQPage non coincidono")
        pagine_faq += bool(ld_faq)
        nomi_ld = [q["name"] for b in ld_faq for q in b["mainEntity"]]
        if sorted(nomi_ld) != sorted(unescape(x) for x in visibili):
            errore(f"{p.relative_to(SITO)}: domande del JSON-LD diverse da quelle visibili")
        for b in ld_faq:
            for q in b["mainEntity"]:
                n += 1
                a = q["acceptedAnswer"]["text"]
                if norm(q["name"]) not in vis or norm(a) not in vis:
                    errore(f"{p.relative_to(SITO)}: FAQ JSON-LD diversa dal testo visibile ({q['name'][:40]})")
                if q["name"] not in domande:
                    errore(f"{p.relative_to(SITO)}: FAQ senza ricerca registrata ({q['name'][:40]})")
                for cod, tt in re.findall(r"(?<![\d-])(\d{2,6}(?:-\d{2})?) «([^»]+)»", a):
                    if not ((cod in C and C[cod]["t"] == tt) or (cod in NA["sic"] and NA["sic"][cod]["t"] == tt) or NA["gruppi_sic"].get(cod) == tt):
                        errore(f"{p.relative_to(SITO)}: FAQ con un titolo non ufficiale per {cod}")
    if n != len(FAQ):
        errore(f"FAQ: {n} nelle pagine, {len(FAQ)} in faq.json")
    print(f"FAQ: {n} domande in {pagine_faq} pagine, tutte da ricerche vere ({len(sugg)} suggerimenti salvati il {DOM['letto_il']}); "
          "JSON-LD FAQPage = testo visibile e solo dove ci sono FAQ")


# ---------------------------------------------------------------- 6. indicizzazione
def controlla_indicizzazione():
    insiemi, indic, parole = {}, {}, {}
    richiesti = codici_richiesti()
    salvate = 0
    for p in pagine_html():
        rel = str(p.relative_to(SITO))
        if not re.fullmatch(r"(\d{2}-\d{2}|\d{2,4}|\d{6})/index\.html", rel):
            continue
        html = p.read_text(encoding="utf-8")
        m = re.search(r"<main\b.*?</main>", html, re.S).group(0)
        m = re.sub(r'<p class="disclaimer">.*?</p>', " ", m, flags=re.S)
        m = re.sub(r'<nav class="briciole".*?</nav>', " ", m, flags=re.S)
        m = re.sub(r"<section data-ripreso>.*?</section>", " ", m, flags=re.S)  # rimandi ripresi da altre pagine: non sono testo proprio
        m = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", m, flags=re.S | re.I)
        w = re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", m)).lower())
        parole[rel] = len(w)
        insiemi[rel] = {" ".join(w[i:i + 5]) for i in range(len(w) - 4)}
        indic[rel] = '<meta name="robots" content="noindex">' not in html
    conta = Counter(g for s in insiemi.values() for g in s)
    soglia = QUOTA_MODELLO * len(insiemi)
    insiemi = {r: {g for g in s if conta[g] < soglia} for r, s in insiemi.items()}
    per_gruppo = defaultdict(list)
    for r, s in insiemi.items():
        for g in s:
            if conta[g] <= 40:
                per_gruppo[g].append(r)
    peggio, poche = 0.0, 10 ** 9
    for rel, a in insiemi.items():
        if not indic[rel]:
            continue
        proprie = sum(1 for g in a if conta[g] == 1)
        poche = min(poche, proprie)
        cand = Counter(r2 for g in a if conta[g] <= 40 for r2 in per_gruppo[g] if r2 != rel)
        q, simile = max(((len(a & insiemi[r2]) / len(a), r2) for r2, _ in cand.most_common(40)), default=(0, ""))
        peggio = max(peggio, q)
        cod = rel.split("/")[0]
        if cod in richiesti and (proprie < MIN_PAROLE_PROPRIE - 10 or q >= MAX_SOVRAPPOSIZIONE + 0.02):
            # pagina corta ma cercata: soglie più basse, mai sotto il minimo assoluto
            salvate += 1
            if proprie < MIN_PROPRIE_RICHIESTA - 10:
                errore(f"{rel}: indicizzata per domanda con solo {proprie} gruppi di parole propri")
            if q >= MAX_SOVRAPPOSIZIONE_RICHIESTA + 0.02:
                errore(f"{rel}: indicizzata per domanda ma {q:.0%} del testo è in comune con {simile}")
            if parole[rel] < 300:
                errore(f"{rel}: indicizzata per domanda con sole {parole[rel]} parole")
            continue
        if proprie < MIN_PAROLE_PROPRIE - 10:
            errore(f"{rel}: indicizzata con solo {proprie} gruppi di parole propri")
        if q >= MAX_SOVRAPPOSIZIONE + 0.02:
            errore(f"{rel}: indicizzata ma {q:.0%} del testo è in comune con {simile}")
    for c in sorted(richiesti):
        if not indic.get(f"{c}/index.html"):
            AVV.append(f"{c}: codice con domanda dimostrata ma pagina noindex (troppo simile a un'altra o troppo corta)")
    n = sum(indic.values())
    print(f"Indicizzazione: {len(richiesti)} codici con domanda dimostrata, {salvate} indicizzati con le soglie basse "
          f"({MIN_PROPRIE_RICHIESTA} gruppi, {MAX_SOVRAPPOSIZIONE_RICHIESTA:.0%})")
    print(f"Indicizzazione: {n} pagine di codice indicizzate su {len(indic)}; testo in comune con la pagina più simile al massimo {peggio:.0%} "
          f"(soglia {MAX_SOVRAPPOSIZIONE:.0%}, frasi di modello escluse); gruppi di parole propri almeno {poche}")


# ---------------------------------------------------------------- 7. testi
VIETATE = re.compile(r"\b(claude|anthropic|openai|chatgpt|gpt-?\d|gemini|llama|mistral|copilot|opus|sonnet|haiku)\b", re.I)
PERSONALI = re.compile(r"massimiliano|\bcori\b|@gmail|@outlook|@libero", re.I)
CONSIGLI = re.compile(r"\b(we recommend|you should choose|we suggest|best code for you|the right code for you is)\b", re.I)
FISCO = re.compile(r"\b(deduct\w*|tax rate|taxable|tax credit|tax savings|lower taxes|size standard is|\$\s?\d[\d,.]*\s*(million|in receipts))\b", re.I)


def controlla_testi():
    files = [p for p in RADICE.rglob("*") if p.is_file() and "_grezzi" not in p.parts and "cache" not in p.parts and "__pycache__" not in p.parts
             and p.suffix in (".py", ".json", ".html", ".md", ".css", ".js", ".txt", ".xml", ".toml")]
    for p in files:
        t = p.read_text(encoding="utf-8", errors="replace")
        if ("sd" + "_live") in t:  # prefisso delle chiavi di api.seodata.dev (scritto spezzato: questo file non deve contenerlo)
            errore(f"{p.relative_to(RADICE)}: chiave di uno strumento esterno nel file")
        if p.name in ("verifica.py", "domanda.json", "naics.json") or p.parent.name == "assets":
            continue
        if p.suffix == ".html":
            t = re.sub(r"\b[Ll]lamas?\b(?= production| farming| ranch| and alpaca|,| \(| farm)", "", t)  # l'animale, nell'indice ufficiale
        if VIETATE.search(t):
            errore(f"{p.relative_to(RADICE)}: nome di un modello o servizio di IA ({VIETATE.search(t).group(0)})")
        if PERSONALI.search(t) and p.name != "NOTE.md":
            errore(f"{p.relative_to(RADICE)}: possibile dato personale ({PERSONALI.search(t).group(0)})")
    note = RADICE / "NOTE.md"
    if note.exists() and re.search(r"[\w.]+@\w+\.\w+", note.read_text(encoding="utf-8")):
        errore("NOTE.md: indirizzo email")
    sba = 0
    for p in pagine_html():
        v = visibile(p.read_text(encoding="utf-8"))
        if CONSIGLI.search(v):
            errore(f"{p.relative_to(SITO)}: frase che sembra un consiglio («{CONSIGLI.search(v).group(0)}»)")
        if FISCO.search(v) and not re.fullmatch(r"(\d{2}-\d{2}|\d{2,4}|\d{6})/index\.html", str(p.relative_to(SITO))):
            errore(f"{p.relative_to(SITO)}: frase su soglie SBA o conseguenze fiscali («{FISCO.search(v).group(0)}»)")
        if "size standard" in v:
            sba += 1
            if "The NAICS manual says that NAICS categories do not distinguish between small and large business" not in v:
                errore(f"{p.relative_to(SITO)}: «size standard» fuori dalla FAQ che cita il manuale")
    for a in ATT:
        vol = sum(VOL["frasi"][f]["volume"] for f in a["frasi"] if f in VOL["frasi"])
        esiste = (SITO / a["slug"] / "index.html").exists()
        if esiste != bool(vol):
            errore(f"{a['slug']}: pagina {'pubblicata senza volume' if esiste else 'assente con volume'}")
        for c in a["evidenza"]:
            if c not in C:
                errore(f"{a['slug']}: codice {c} inesistente")
    print(f"Testi: nessun nome di IA, nessun dato personale, nessuna chiave, nessun consiglio; SBA solo nella FAQ che cita il manuale ({sba} pagina); "
          "pagine per attività solo con volume misurato")


# ---------------------------------------------------------------- 8. monetizzazione
def controlla_monetizzazione():
    e, info = MON.controlla_sito("naics", SITO)
    for x in e:
        errore("monetizzazione: " + x)
    if info["link_affiliati"]:
        errore("link di affiliazione presenti: per ora il sito non ne ha")
    senza = sum(1 for p in pagine_html() if MON.SEGNO_SENZA_ADSENSE in p.read_text(encoding="utf-8"))
    print(MON.riepilogo("naics", info, e) + f"; pagine senza pubblicità (noindex o poco testo): {senza}")


# ---------------------------------------------------------------- 9. browser
PAGINE_BROWSER = ["/", "/541511/", "/425120/", "/812113/", "/5415/", "/sic-to-naics/", "/naics-2017-to-2022/", "/how-we-check/"]


def controlla_browser():
    import mimetypes
    from playwright.sync_api import sync_playwright
    shot = RADICE / "cache" / "screenshot"
    shot.mkdir(parents=True, exist_ok=True)
    bloccate, chieste, inviati = [], [], []

    def servi(route):
        url = route.request.url
        if not url.startswith("http://sito.test/"):
            bloccate.append(url)
            return route.abort()  # niente richieste esterne: solo i file del sito
        chieste.append(url)
        if route.request.method == "POST":
            inviati.append(route.request.post_data or "")
            return route.fulfill(status=200, body="ok", content_type="text/plain")
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
                pg.on("console", lambda m: errori_js.append(m.text) if m.type == "error" and "ERR_FAILED" not in m.text else None)
                pg.route("**/*", servi)
                for u in PAGINE_BROWSER:
                    pg.goto("http://sito.test" + u)
                    pg.wait_for_load_state("load")
                    largo = pg.evaluate("document.documentElement.scrollWidth")
                    if largo > w + 1:
                        errore(f"browser {w}px {tema} {u}: scorrimento orizzontale ({largo}px)")
                    piccoli = pg.evaluate("""Array.from(document.querySelectorAll('main p, main li, main td, main span, main small')).slice(0,3000).filter(e=>e.offsetParent&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<11).length""")
                    if piccoli:
                        errore(f"browser {w}px {tema} {u}: {piccoli} testi sotto 11px")
                    sfondo = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                    if (tema == "dark") != (sfondo == "rgb(10, 22, 25)"):
                        errore(f"browser {w}px {tema} {u}: sfondo {sfondo} non coerente con il tema")
                    if u == "/":
                        prove = [("541511", "/541511/"), ("72251", "/7225/#n-72251"), ("454110", "/naics-2017-to-2022/#v-454110"),
                                 ("7371", "/sic-to-naics/#sic-7371"), ("plumbing", "/238220/"), ("bakery", "/311811/"), ("software publishers", "/513210/"),
                                 ("pet grooming", "/812910/")]
                        del chieste[:]
                        pg.focus("[data-cerca]")
                        pg.wait_for_selector("[data-cerca][data-pronto]", timeout=10000)  # codici e titoli caricati
                        for q, atteso in prove:
                            pg.fill("[data-cerca]", q)
                            if q.isdigit():
                                if any("/assets/entries." in x for x in chieste):
                                    errore("browser: la ricerca per numero scarica anche le voci dell'indice (file grande)")
                            else:
                                pg.wait_for_selector("[data-cerca][data-frasi-pronte]", timeout=10000)  # voci dell'indice: solo quando si scrive una parola
                            pg.wait_for_selector("[data-risultati] a", timeout=8000)
                            hrefs = pg.eval_on_selector_all("[data-risultati] a", "a=>a.map(x=>x.getAttribute('href'))")
                            if not any(hh == atteso for hh in hrefs[:5]):
                                errore(f"browser: la ricerca «{q}» non porta a {atteso} tra i primi 5 ({hrefs[:5]})")
                        pg.fill("[data-cerca]", "zzzzqq")
                        if "No code found" not in pg.inner_text("[data-risultati]"):
                            errore("browser: ricerca senza risultati senza messaggio")
                        pg.fill("[data-cerca]", "")
                    if u == "/naics-2017-to-2022/":
                        tot = pg.locator("[data-tabella] tbody tr").count()
                        if pg.locator("[data-tabella] tbody tr:visible").count() != 100 or not pg.locator("[data-altre]").is_visible():
                            errore("browser: la tabella 2017 → 2022 deve aprirsi con 100 righe e il pulsante «Show 100 more»")
                        pg.fill("[data-filtro]", "454110")
                        if pg.locator("[data-tabella] tbody tr:visible").count() != 1:
                            errore("browser: il filtro «454110» non mostra 1 riga")
                        pg.fill("[data-filtro]", "")
                        pg.click("[data-altre-tutte]")
                        if pg.locator("[data-tabella] tbody tr:visible").count() != tot:
                            errore("browser: «Show all» non mostra tutte le righe")
                    if u in ("/425120/", "/541511/", "/812113/"):
                        pg.evaluate("document.querySelectorAll('main details').forEach(d=>d.open=true)")
                        larghe = pg.evaluate("Array.from(document.querySelectorAll('main .tab')).filter(t=>t.scrollWidth>t.clientWidth+1).length")
                        if larghe:
                            errore(f"browser {w}px {u}: {larghe} tabelle più larghe dello schermo (scorrono di lato)")
                        pg.evaluate("document.querySelectorAll('main details').forEach(d=>d.open=false)")
                    if u == "/425120/":
                        if pg.locator("#sic ~ details.tutte table").first.is_visible() or "no single equivalent" not in pg.inner_text("#sic"):
                            errore("browser /425120/: le 71 righe SIC parziali devono essere chiuse e dichiarate senza equivalente unico")
                    if u == "/how-we-check/" and w == 375 and tema == "light":
                        if pg.locator("form[data-correzioni] input[type=email], form[data-correzioni] input[type=checkbox]").count():
                            errore("browser: il modulo delle correzioni chiede dati personali")
                        pg.fill("form[data-correzioni] input[name=page]", "/541511/")
                        pg.fill("form[data-correzioni] textarea", "test")
                        pg.click("form[data-correzioni] button")
                        pg.wait_for_selector("[data-ok]:not([hidden])", timeout=5000)
                        if not inviati or "form-name=corrections" not in inviati[-1] or "email" in inviati[-1]:
                            errore(f"browser: invio del modulo inatteso ({inviati[-1][:80] if inviati else 'nessun invio'})")
                    if u == "/sic-to-naics/":
                        pg.fill("[data-filtro]", "7371")
                        if pg.locator("[data-tabella] tbody tr:visible").count() != 1:
                            errore("browser: il filtro SIC «7371» non mostra 1 riga")
                        pg.fill("[data-filtro]", "")
                    nome = (u.strip("/").replace("/", "_") or "home")
                    pg.screenshot(path=str(shot / f"{nome}_{w}_{tema}.png"), full_page=u not in ("/sic-to-naics/", "/naics-2017-to-2022/"))
                pg.goto("http://sito.test/")
                prima = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                pg.click("[data-tema]")
                dopo = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                if prima == dopo:
                    errore(f"browser {w}px {tema}: il pulsante del tema non cambia lo sfondo")
                if errori_js:
                    errore(f"browser {w}px {tema}: errori JS {errori_js[:3]}")
                ctx.close()
        b.close()
    esterne = sorted({re.match(r"https?://[^/]+", u).group(0) for u in bloccate if u.startswith("http")})
    print(f"Browser: {len(PAGINE_BROWSER)} pagine × 375/1280 px × chiaro/scuro (richieste esterne bloccate: {', '.join(esterne) or 'nessuna'}), "
          f"ricerca (8 prove; le voci dell'indice si scaricano solo scrivendo una parola), modulo delle correzioni senza dati personali, filtri delle tabelle e tema, nessun errore JS; screenshot in {shot}")


def main():
    controlla_fonti()
    controlla_dati()
    controlla_sic()
    controlla_contenuti()
    controlla_pagine()
    controlla_faq()
    controlla_indicizzazione()
    controlla_testi()
    controlla_monetizzazione()
    if "--browser" in sys.argv:
        controlla_browser()
    for e in ERR[:60]:
        print("ERRORE:", e)
    if len(ERR) > 60:
        print(f"... e altri {len(ERR) - 60} errori")
    print(f"\n{len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
