"""Controlli del sito Farmaco Equivalente. Esce con errore se qualcosa non va.

Uso (dalla radice del repository):
    python3 farmaci/verifica.py              # fonti, cifre ricalcolate dai file grezzi, pagine, SEO, FAQ, testi, monetizzazione
    python3 farmaci/verifica.py --browser    # + Playwright: 4 pagine a 375 e 1280 px, tema chiaro e scuro (richieste esterne bloccate)

Le cifre si ricalcolano qui senza usare genera.py né estrai.py: si rileggono i CSV grezzi di AIFA con un lettore proprio,
si ricontrolla ogni differenza (prezzo al pubblico − prezzo di riferimento) e ogni stato di carenza, poi si confrontano
con gli attributi e con il testo visibile di ogni riga di ogni pagina.
"""
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
GREZZI = RADICE / "raccolta" / "_grezzi"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

URL_SITO = "https://farmaci-equivalenti.netlify.app"
FRASE_FISSA = "chiedi al medico o al farmacista"
ERR, AVV = [], []


def errore(m):
    ERR.append(m)


def avviso(m):
    AVV.append(m)


def carica(n):
    return json.loads((DATI / n).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
DOM = carica("domanda.json")
FAQ = carica("faq.json")["faq"]
FAQ_P = carica("faq_pagine.json")["faq"]


def norm(t):
    t = t.replace("’", "'").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def visibile(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return norm(unescape(re.sub(r"<[^>]+>", " ", t)))


def euro(x):
    x = Decimal(str(x)).quantize(Decimal("0.01"))
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def pr(s):
    """Prezzo dal CSV AIFA ("5,63 €") a Decimal, con un lettore indipendente da estrai.py."""
    s = s.replace("€", "").replace(" ", "").strip()
    return Decimal(s.replace(".", "").replace(",", ".")) if s else None


def gg(iso):
    if not iso:
        return ""
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def iso(s):
    m = re.fullmatch(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*", s or "")
    return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else ""


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti():
    for fid, f in FJ["file"].items():
        p = GREZZI / f["file_locale"]
        if not p.exists():
            errore(f"fonte {fid}: file grezzo assente ({p.name}): rilanciare raccolta/fonti.py")
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256"]:
            errore(f"fonte {fid}: impronta diversa da fonti.json")
        if f["http"] != 200 or not f["pubblicato_il"]:
            errore(f"fonte {fid}: HTTP {f['http']} o data di pubblicazione assente")
    for pid, p in FJ["pagine"].items():
        if p["http"] != 200:
            errore(f"pagina {pid}: HTTP {p['http']}")
        grezzo = GREZZI / f"pagina_{pid}.html"
        testo = norm(unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", grezzo.read_text(encoding="utf-8", errors="replace"), flags=re.S))))
        for frase, ok in p["trovate"].items():
            if not ok or norm(frase) not in testo:
                errore(f"pagina {pid}: frase non trovata «{frase[:60]}»")
    if "CC BY 4.0" not in FJ["licenza"]["nome"]:
        errore("licenza non registrata")
    print(f"Fonti: {len(FJ['file'])} file AIFA con impronta verificata, {len(FJ['pagine'])} pagine ufficiali con {sum(len(p['trovate']) for p in FJ['pagine'].values())} frasi ritrovate")


# ---------------------------------------------------------------- 2. dati ricalcolati dai CSV grezzi
def leggi(nome):
    return list(csv.reader(io.StringIO((GREZZI / nome).read_bytes().decode("cp1252"), newline=""), delimiter=";"))


def a9(s):
    s = re.sub(r"\D", "", s)
    return s.zfill(9)


RAW_T, RAW_C = {}, defaultdict(list)


def controlla_dati():
    r = leggi("trasparenza.csv")
    col = {n.strip(): i for i, n in enumerate(r[0])}
    cp = next(k for k in col if k.startswith("Prezzo Pubblico"))
    data_col = cp.replace("Prezzo Pubblico", "").strip()
    pub_t = FJ["file"]["trasparenza"]["pubblicato_il"]
    if data_col.split()[0] != str(int(pub_t[8:])) or data_col.split()[-1] != pub_t[:4]:
        errore(f"trasparenza: colonna «{cp}» non coerente con la data della pagina AIFA {pub_t}")
    nd = 0
    for x in r[1:]:
        if len(x) < 12 or not x[col["AIC"]].strip():
            continue
        aic = a9(x[col["AIC"]])
        rif, prezzo, diff = pr(x[col["Prezzo riferimento SSN"]]), pr(x[col[cp]]), pr(x[col["Differenza"]])
        if prezzo - rif != diff:
            errore(f"trasparenza {aic}: differenza stampata {diff} ≠ {prezzo} − {rif}")
        if diff < 0:
            errore(f"trasparenza {aic}: differenza negativa")
        nd += 1
        if aic in RAW_T:
            errore(f"trasparenza: AIC {aic} doppio")
        RAW_T[aic] = {"farmaco": " ".join(x[col["Farmaco"]].split()), "rif": rif, "prezzo": prezzo, "diff": diff,
                      "gruppo": x[col["Codice gruppo equivalenza"]].strip()}
    g = defaultdict(set)
    for v in RAW_T.values():
        g[v["gruppo"]].add(v["rif"])
    for k, s in g.items():
        if len(s) != 1:
            errore(f"gruppo {k}: più prezzi di riferimento")
    rc = leggi("carenti.csv")
    i = next(k for k, x in enumerate(rc) if x and x[0] == "Nome medicinale")
    data_file = re.search(r"aggiornato al (\d{2}/\d{2}/\d{4})", " ".join(" ".join(x) for x in rc[:i]))
    if not data_file or iso(data_file.group(1)) != FJ["file"]["carenti"]["pubblicato_il"]:
        errore("carenti: data nel file diversa dalla data della pagina AIFA")
    h = rc[i]
    for x in rc[i + 1:]:
        if len(x) < 13 or not x[1].strip():
            continue
        RAW_C[a9(x[1])].append({"nome": " ".join(x[0].split()), "inizio": iso(x[5]), "fine": iso(x[6]), "eq": x[7].strip(), "motivo": " ".join(x[8].split())})
    if h[:3] != ["Nome medicinale", "Codice AIC", "Principio attivo"]:
        errore("carenti: intestazione cambiata")
    # i JSON del sito devono coincidere con la rilettura
    T = carica("trasparenza.json")["righe"]
    C = carica("carenti.json")["righe"]
    if len(T) != len(RAW_T) or any(Decimal(t["diff"]) != RAW_T[t["aic"]]["diff"] or Decimal(t["prezzo"]) != RAW_T[t["aic"]]["prezzo"] for t in T):
        errore("dati/trasparenza.json diverso dal CSV AIFA")
    if len(C) != sum(len(v) for v in RAW_C.values()) or {c["aic"] for c in C} != set(RAW_C):
        errore("dati/carenti.json diverso dal CSV AIFA")
    inT = {a for a in RAW_C if a in RAW_T}
    noncar = [a for a in inT if any(b not in RAW_C and v["gruppo"] == RAW_T[a]["gruppo"] for b, v in RAW_T.items())]
    print(f"Dati: {nd} confezioni della lista di trasparenza (differenza = prezzo − riferimento su tutte), {len(g)} gruppi; "
          f"{sum(len(v) for v in RAW_C.values())} righe carenti ({len(RAW_C)} AIC); {len(inT)} carenti nella lista, {len(noncar)} con equivalente non carente")
    return {"n_conf": len(RAW_T), "n_gruppi": len(g), "n_diff": sum(1 for v in RAW_T.values() if v["diff"] > 0),
            "n_car": sum(len(v) for v in RAW_C.values()), "n_car_t": len(inT), "n_car_t_eq": len(noncar)}


# ---------------------------------------------------------------- 3. cifre nelle pagine
def pagine_html():
    return sorted(SITO.rglob("*.html"))


def num(n):
    return f"{n:,}".replace(",", ".")


def controlla_cifre(tot):
    visti = Counter()
    gruppi_pag = defaultdict(set)
    codici = {v["gruppo"].lower(): v["gruppo"] for v in RAW_T.values()}
    for p in pagine_html():
        html = p.read_text(encoding="utf-8")
        rel = str(p.relative_to(SITO))
        for m in re.finditer(r'<tr(?: class="[^"]*")? data-aic="(\d{9})" data-prezzo="([\d.]+)" data-rif="([\d.]+)" data-diff="([\d.]+)" data-carente="([01])"[^>]*>(.*?)</tr>', html, re.S):
            aic, prezzo, rif, diff, car, riga = m.groups()
            r = RAW_T.get(aic)
            if not r:
                errore(f"{rel}: AIC {aic} non è nella lista di trasparenza")
                continue
            visti[aic] += 1
            gruppi_pag[r["gruppo"]].add(rel)
            if (Decimal(prezzo), Decimal(rif), Decimal(diff)) != (r["prezzo"], r["rif"], r["diff"]):
                errore(f"{rel}: AIC {aic} cifre {prezzo}/{rif}/{diff} diverse dal CSV")
            if Decimal(diff) != Decimal(prezzo) - Decimal(rif):
                errore(f"{rel}: AIC {aic} differenza ≠ prezzo − riferimento")
            vis = visibile(riga)
            if euro(r["prezzo"]) not in vis:
                errore(f"{rel}: AIC {aic} prezzo {euro(r['prezzo'])} non visibile")
            if (r["diff"] == 0 and "nessuna" not in vis) or (r["diff"] > 0 and euro(r["diff"]) not in vis):
                errore(f"{rel}: AIC {aic} differenza non visibile")
            if r["farmaco"] not in vis:
                errore(f"{rel}: AIC {aic} nome {r['farmaco']} non visibile")
            atteso = aic in RAW_C
            if (car == "1") != atteso:
                errore(f"{rel}: AIC {aic} stato di carenza {car} diverso dall'elenco AIFA")
            if atteso:
                c = RAW_C[aic][0]
                etich = (f"Carenza prevista dal {gg(c['inizio'])}" if c["inizio"] > FJ["file"]["carenti"]["pubblicato_il"] else f"Carente dal {gg(c['inizio'])}")
                if etich not in vis:
                    errore(f"{rel}: AIC {aic} manca «{etich}»")
            elif "Non in elenco" not in vis:
                errore(f"{rel}: AIC {aic} manca «Non in elenco»")
        # riferimento e conteggi di ogni gruppo
        for m in re.finditer(r'<section class="gruppo" id="g-([a-z0-9]+)".*?</section>', html, re.S):
            g = codici.get(m.group(1))
            sez = visibile(m.group(0))
            membri = [a for a, v in RAW_T.items() if v["gruppo"] == g]
            rif = RAW_T[membri[0]]["rif"]
            if f"Prezzo di riferimento rimborsato dal Servizio sanitario: {euro(rif)}" not in sez:
                errore(f"{rel}: gruppo {g} prezzo di riferimento {euro(rif)} assente")
            car = [a for a in membri if a in RAW_C]
            nc = [a for a in membri if a not in RAW_C]
            if car and nc and f"Equivalenti non carenti nello stesso gruppo: {len(nc)}" not in sez:
                errore(f"{rel}: gruppo {g} numero di equivalenti non carenti diverso da {len(nc)}")
            if car and not nc and "non c'è un equivalente non carente" not in sez:
                errore(f"{rel}: gruppo {g} tutto carente ma la pagina non lo dice")
            if not car and "di questo gruppo" in sez:
                errore(f"{rel}: gruppo {g} senza carenze ma con la nota di carenza")
            n0 = sum(1 for a in membri if RAW_T[a]["diff"] == 0)
            if len(membri) > 1 and f"{len(membri)} confezioni nel gruppo: {n0} senza differenza da pagare" not in sez:
                errore(f"{rel}: gruppo {g} conteggio «{len(membri)} confezioni, {n0} senza differenza» assente")
    manc = [a for a in RAW_T if visti[a] != 1]
    if manc:
        errore(f"{len(manc)} confezioni della lista non compaiono esattamente una volta nelle pagine (es. {manc[:3]})")
    doppi = [g for g, s in gruppi_pag.items() if len(s) > 1]
    if doppi:
        errore(f"gruppi divisi su più pagine: {doppi[:5]}")
    # elenco carenti
    html = (SITO / "carenze" / "index.html").read_text(encoding="utf-8")
    righe = re.findall(r'<tr data-aic="(\d{9})" data-eq="([01])" data-inizio="([\d-]*)" data-fine="([\d-]*)">(.*?)</tr>', html, re.S)
    if len(righe) != tot["n_car"]:
        errore(f"carenze: {len(righe)} righe invece di {tot['n_car']}")
    cont = Counter(a for a, *_ in righe)
    for a, eq, ini, fine, riga in righe:
        cs = RAW_C.get(a)
        if not cs or not any(c["inizio"] == ini and c["fine"] == fine and (c["eq"].lower().startswith("s")) == (eq == "1") for c in cs):
            errore(f"carenze: riga AIC {a} diversa dall'elenco AIFA")
        if cont[a] != len(cs or []):
            errore(f"carenze: AIC {a} compare {cont[a]} volte invece di {len(cs or [])}")
        vis = visibile(riga)
        if ini and gg(ini) not in vis:
            errore(f"carenze: AIC {a} data di inizio non visibile")
    # numeri generali nella home
    home = visibile((SITO / "index.html").read_text(encoding="utf-8"))
    for k in ("n_conf", "n_gruppi", "n_diff", "n_car", "n_car_t", "n_car_t_eq"):
        if num(tot[k]) not in home:
            errore(f"home: numero {k} = {num(tot[k])} assente")
    print(f"Cifre: {sum(visti.values())} righe di confezione nelle pagine (ognuna una volta, con prezzo, differenza e stato di carenza dal CSV), "
          f"{len(righe)} righe nell'elenco dei carenti, numeri della home ricalcolati")


# ---------------------------------------------------------------- 4. pagine e SEO
DOMINI_ESTERNI = ("aifa.gov.it", "normattiva.it", "creativecommons.org", "garanteprivacy.it", "policies.google.com", "adssettings.google.com",
                  "goatcounter.com", "gc.zgo.at", "farmaci-equivalenti.netlify.app")


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
        if ni:
            noindex += 1
            if c:
                errore(f"{rel}: noindex con canonical")
            if MON.SEGNO_SENZA_ADSENSE not in html and MON.adsense_attivo("farmaci"):
                errore(f"{rel}: pagina noindex senza il segno «niente pubblicità»")
            if "googlesyndication" in html:
                errore(f"{rel}: pubblicità in una pagina noindex")
        else:
            if len(tt) > 65:
                errore(f"{rel}: titolo di {len(tt)} caratteri (max 65)")
            if not 70 <= len(dd) <= 160:
                errore(f"{rel}: descrizione di {len(dd)} caratteri (70-160)")
            if tt in titoli:
                errore(f"{rel}: titolo uguale a {titoli[tt]}")
            if dd in descr:
                errore(f"{rel}: descrizione uguale a {descr[dd]}")
            titoli[tt], descr[dd] = rel, rel
            atteso = URL_SITO + "/" + rel.replace("index.html", "")
            if not c or c.group(1) != atteso:
                errore(f"{rel}: canonical assente o diverso da {atteso}")
            else:
                canon.add(c.group(1))
        if html.count("<h1") != 1:
            errore(f"{rel}: {html.count('<h1')} h1")
        if 'data-goatcounter="https://rete-siti.goatcounter.com/count"' not in html:
            errore(f"{rel}: manca il contatore GoatCounter")
        if '<html lang="it">' not in html:
            errore(f"{rel}: lingua non italiana")
        vis = visibile(html)
        if FRASE_FISSA not in vis:
            errore(f"{rel}: manca la frase fissa «{FRASE_FISSA}»")
        if "non affiliato ad AIFA" not in vis:
            errore(f"{rel}: manca «non affiliato ad AIFA»")
        if "licenza CC BY 4.0" not in vis:
            errore(f"{rel}: manca la citazione della licenza AIFA")
        ids = set(re.findall(r'\bid="([^"]+)"', html))
        for href in set(re.findall(r'href="([^"]+)"', html)):
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
        for src in re.findall(r'(?:src|href|data-indice)="(/assets/[^"#]+)"', html):
            if src.lstrip("/") not in file_esistenti:
                errore(f"{rel}: risorsa assente {src}")
        if 'rel="sponsored' in html or "sponsored" in re.findall(r'rel="([^"]*)"', html):
            errore(f"{rel}: link sponsorizzato (vietato per i farmaci)")
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    if locs != canon:
        errore(f"sitemap diversa dai canonical: {sorted(locs ^ canon)[:5]}")
    rb = (SITO / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {URL_SITO}/sitemap.xml" not in rb:
        errore("robots.txt senza sitemap")
    chiave = "b5a26a844a465f58552debee2c8a0114"
    if (SITO / f"{chiave}.txt").read_text(encoding="utf-8") != chiave:
        errore("file chiave IndexNow assente o diverso")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in (SITO / "netlify.toml").read_text(encoding="utf-8"):
        errore("netlify.toml senza la regola che evita pubblicazioni inutili")
    for f in ("assets/og.png", "404.html"):
        if not (SITO / f).exists():
            errore(f"manca {f}")
    print(f"Pagine: {len(pagine_html())} file HTML, {len(canon)} indicizzabili (= sitemap), {noindex} noindex senza pubblicità; titoli e descrizioni unici")


# ---------------------------------------------------------------- 5. FAQ
def controlla_faq():
    sugg_r = {s for v in DOM["radici"].values() for s in v}
    sugg_n = {s for v in DOM["nomi"].values() for s in v}
    for x in FAQ:
        if x["ricerca"] not in sugg_r:
            errore(f"FAQ «{x['q'][:40]}»: ricerca «{x['ricerca']}» non tra i suggerimenti salvati")
    for x in FAQ_P:
        if x["ricerca"] not in sugg_n | sugg_r:
            errore(f"FAQ di {x['pagina']} «{x['q'][:40]}»: ricerca «{x['ricerca']}» non tra i suggerimenti salvati")
    n = 0
    for p in pagine_html():
        html = p.read_text(encoding="utf-8")
        if re.search(r"\{[a-z_]+\}", visibile(html)):
            errore(f"{p.relative_to(SITO)}: segnaposto non sostituito")
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            ld = json.loads(blocco)
            if ld.get("@type") == "FAQPage":
                vis = visibile(html)
                for q in ld["mainEntity"]:
                    n += 1
                    if norm(q["name"]) not in vis or norm(q["acceptedAnswer"]["text"]) not in vis:
                        errore(f"{p.relative_to(SITO)}: FAQ JSON-LD diversa dal testo visibile ({q['name'][:40]})")
                    domande = {x["q"] for x in FAQ} | {x["q"] for x in FAQ_P}
                    if q["name"] not in domande:
                        errore(f"{p.relative_to(SITO)}: FAQ senza ricerca registrata ({q['name'][:40]})")
    print(f"FAQ: {n} domande nelle pagine, tutte nate da ricerche vere ({len(sugg_r) + len(sugg_n)} suggerimenti salvati il {DOM['letto_il']}); JSON-LD = testo visibile")


# ---------------------------------------------------------------- 5b. indicizzazione (regola del revisore, 12/11/2026)
MIN_CONFEZIONI, MAX_SOVRAPPOSIZIONE = 8, 0.60
PAGINE_FISSE = {"index.html", "404.html", "carenze/index.html", "farmaco-mancante/index.html", "come-lavoriamo/index.html", "chi-siamo/index.html",
                "privacy/index.html"}


def controlla_indicizzazione():
    """Nessuna pagina principio attivo indicizzata con meno di 8 confezioni o con il 60% o più del testo (gruppi di 5 parole)
    in comune con un'altra pagina principio attivo. Ricalcolato qui dalle pagine scritte, senza usare genera.py."""
    insiemi, indic, conf = {}, {}, {}
    for p in pagine_html():
        rel = str(p.relative_to(SITO))
        if rel in PAGINE_FISSE or re.fullmatch(r"google[0-9a-f]+\.html", p.name):
            continue
        html = p.read_text(encoding="utf-8")
        m = re.search(r"<main\b.*?</main>", html, re.S).group(0)
        m = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", m, flags=re.S | re.I)
        w = re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", m)).lower())
        insiemi[rel] = {" ".join(w[i:i + 5]) for i in range(len(w) - 4)}
        indic[rel] = '<meta name="robots" content="noindex">' not in html
        conf[rel] = len(re.findall(r'data-prezzo="', html))
    peggio = 0.0
    for rel, a in insiemi.items():
        if not indic[rel]:
            continue
        if conf[rel] < MIN_CONFEZIONI:
            errore(f"{rel}: indicizzata con {conf[rel]} confezioni (minimo {MIN_CONFEZIONI})")
        q, simile = max(((len(a & b) / len(a), r2) for r2, b in insiemi.items() if r2 != rel), default=(0, ""))
        peggio = max(peggio, q)
        if q >= MAX_SOVRAPPOSIZIONE:
            errore(f"{rel}: indicizzata ma {q:.0%} del testo è in comune con {simile}")
    n = sum(indic.values())
    print(f"Indicizzazione: {n} pagine principio attivo indicizzate su {len(indic)}, tutte con almeno {MIN_CONFEZIONI} confezioni; "
          f"testo in comune con la pagina più simile al massimo {peggio:.0%} (soglia {MAX_SOVRAPPOSIZIONE:.0%})")


# ---------------------------------------------------------------- 6. testi
VIETATE = re.compile(r"\b(claude|anthropic|openai|chatgpt|gpt-?\d|gemini|llama|mistral|copilot|opus|sonnet|haiku)\b", re.I)
TITOLARE = "Titolare del trattamento è Massimiliano Cori (Italia)"
PERSONALI = re.compile(r"massimiliano|\bcori\b|@gmail|@outlook|@libero", re.I)
CONSIGLI = re.compile(r"\b(ti consigliamo|consigliamo di|ti suggeriamo|prendi il|assumi|smetti di prendere|dosaggio consigliato|è meglio prendere|"
                      r"con la marca|la sostituzione la decide|conviene|risparmi\w*|più efficace|migliore|il più economico)\b", re.I)


def controlla_testi():
    files = [p for p in RADICE.rglob("*") if p.is_file() and "_grezzi" not in p.parts and "cache" not in p.parts and "__pycache__" not in p.parts
             and p.suffix in (".py", ".json", ".html", ".md", ".css", ".js", ".txt", ".xml", ".toml")]
    for p in files:
        if p.name in ("verifica.py", "domanda.json"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if VIETATE.search(t):
            errore(f"{p.relative_to(RADICE)}: nome di un modello o servizio di IA ({VIETATE.search(t).group(0)})")
        if p.name == "genera.py" or p.relative_to(RADICE).as_posix() == "sito/privacy/index.html":
            if t.count(TITOLARE) != 1:
                errore(f"{p.relative_to(RADICE)}: la frase sul titolare del trattamento deve comparire una volta")
            t = t.replace(TITOLARE, "")
        if PERSONALI.search(t) and p.name != "NOTE.md":
            errore(f"{p.relative_to(RADICE)}: possibile dato personale ({PERSONALI.search(t).group(0)})")
    note = RADICE / "NOTE.md"
    if note.exists() and re.search(r"[\w.]+@\w+\.\w+", note.read_text(encoding="utf-8")):
        errore("NOTE.md: indirizzo email")
    for p in pagine_html():
        v = visibile(p.read_text(encoding="utf-8"))
        if CONSIGLI.search(v):
            errore(f"{p.relative_to(SITO)}: frase che sembra un consiglio medico («{CONSIGLI.search(v).group(0)}»)")


# ---------------------------------------------------------------- 7. monetizzazione
def controlla_monetizzazione():
    e, info = MON.controlla_sito("farmaci", SITO)
    for x in e:
        errore("monetizzazione: " + x)
    if info["link_affiliati"]:
        errore("link di affiliazione presenti: vietati in questo sito")
    senza = sum(1 for p in pagine_html() if MON.SEGNO_SENZA_ADSENSE in p.read_text(encoding="utf-8"))
    print(MON.riepilogo("farmaci", info, e) + f"; pagine senza pubblicità (noindex o poco testo): {senza}")


def controlla_date():
    oggi = date.today()
    dc = date.fromisoformat(FJ["file"]["carenti"]["pubblicato_il"])
    dt = date.fromisoformat(FJ["file"]["trasparenza"]["pubblicato_il"])
    if (oggi - dc).days > 10:
        avviso(f"elenco carenti del {dc}: più di 10 giorni (AIFA lo aggiorna almeno due volte a settimana): rilanciare l'aggiornamento (NOTE.md)")
    if (oggi - dt).days > 40:
        avviso(f"lista di trasparenza del {dt}: più di 40 giorni (AIFA la pubblica ogni mese): rilanciare l'aggiornamento")


# ---------------------------------------------------------------- 8. browser
PAGINE_BROWSER = ["/", "/carenze/", "/amoxicillina-acido-clavulanico/", "/farmaco-mancante/"]


def controlla_browser():
    import mimetypes
    from playwright.sync_api import sync_playwright
    shot = RADICE / "cache" / "screenshot"
    shot.mkdir(parents=True, exist_ok=True)

    def servi(route):
        url = route.request.url
        if not url.startswith("http://sito.test/"):
            return route.abort()  # niente richieste esterne: solo i file del sito
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
                    pg.goto("http://sito.test" + u)
                    pg.wait_for_load_state("load")
                    largo = pg.evaluate("document.documentElement.scrollWidth")
                    if largo > w + 1:
                        errore(f"browser {w}px {tema} {u}: scorrimento orizzontale ({largo}px)")
                    piccoli = pg.evaluate("""Array.from(document.querySelectorAll('main p, main li, main td, main span, main small')).slice(0,3000).filter(e=>e.offsetParent&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<11).length""")
                    if piccoli:
                        errore(f"browser {w}px {tema} {u}: {piccoli} testi sotto 11px")
                    sfondo = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                    scuro = sfondo == "rgb(10, 21, 20)"
                    if (tema == "dark") != scuro:
                        errore(f"browser {w}px {tema} {u}: sfondo {sfondo} non coerente con il tema")
                    if u == "/":
                        pg.fill("[data-cerca]", "augmentin")
                        pg.wait_for_selector("[data-risultati] a", timeout=5000)
                        hrefs = pg.eval_on_selector_all("[data-risultati] a", "a=>a.map(x=>x.getAttribute('href'))")
                        if "/amoxicillina-acido-clavulanico/" not in hrefs:
                            errore(f"browser: la ricerca «augmentin» non porta alla pagina dell'amoxicillina ({hrefs[:3]})")
                        pg.fill("[data-cerca]", "zzzzqq")
                        if "Nessun farmaco trovato" not in pg.inner_text("[data-risultati]"):
                            errore("browser: ricerca senza risultati senza messaggio")
                        pg.fill("[data-cerca]", "")
                    if u == "/carenze/":
                        tot = pg.locator("#elenco-carenti tbody tr").count()
                        pg.fill("[data-filtro]", "quetiapina")
                        vis = pg.locator("#elenco-carenti tbody tr:visible").count()
                        attese = sum(1 for v in RAW_C.values() for c in v if "quetiapina" in (c["nome"] + " ").lower()) if RAW_C else None
                        if not (0 < vis < tot):
                            errore(f"browser: il filtro «quetiapina» mostra {vis} righe su {tot}")
                        pg.fill("[data-filtro]", "")
                        vis0 = pg.locator("#elenco-carenti tbody tr:visible").count()
                        if vis0 != 100 or not pg.locator("[data-altre]").is_visible():
                            errore(f"browser: l'elenco dei carenti deve aprirsi con 100 righe e il pulsante «Mostra altre» (righe viste: {vis0})")
                        pg.click("[data-altre-piu]")
                        if pg.locator("#elenco-carenti tbody tr:visible").count() != 200:
                            errore("browser: «Mostra altre 100» non porta le righe a 200")
                        pg.click("[data-altre-tutte]")
                        if pg.locator("#elenco-carenti tbody tr:visible").count() != tot or pg.locator("[data-altre]").is_visible():
                            errore("browser: «Mostra tutte» non mostra tutte le righe")
                        pg.check("[data-solo-eq]")
                        vis_eq = pg.locator("#elenco-carenti tbody tr:visible").count()
                        n_eq = sum(1 for v in RAW_C.values() for c in v if c["eq"].lower().startswith("s"))
                        if vis_eq != n_eq:
                            errore(f"browser: «solo con equivalente» mostra {vis_eq} righe invece di {n_eq}")
                        pg.uncheck("[data-solo-eq]")
                        if w == 1280:
                            pg.click('th[data-col="2"] button')
                            pg.click('th[data-col="2"] button')
                            primo = pg.locator("#elenco-carenti tbody tr").first.get_attribute("data-inizio")
                            massimo = max(c["inizio"] for v in RAW_C.values() for c in v)
                            if primo != massimo:
                                errore(f"browser: ordinamento per inizio (decrescente) dà {primo} invece di {massimo}")
                        del attese
                    nome = (u.strip("/").replace("/", "_") or "home")
                    pg.screenshot(path=str(shot / f"{nome}_{w}_{tema}.png"), full_page=(u != "/carenze/"))
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
    print(f"Browser: {len(PAGINE_BROWSER)} pagine × 375/1280 px × chiaro/scuro (richieste esterne bloccate), ricerca, filtro, ordinamento e tema; screenshot in {shot}")


def main():
    controlla_fonti()
    tot = controlla_dati()
    controlla_cifre(tot)
    controlla_pagine()
    controlla_faq()
    controlla_indicizzazione()
    controlla_testi()
    controlla_monetizzazione()
    controlla_date()
    if "--browser" in sys.argv:
        controlla_browser()
    for a in AVV:
        print("AVVISO:", a)
    for e in ERR[:60]:
        print("ERRORE:", e)
    print(f"\n{len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
