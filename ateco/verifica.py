"""Controlli del sito Codici ATECO 2025. Ricalcola tutto dai file grezzi con un lettore proprio (non usa estrai.py né genera.py).

Uso (dalla radice del repository):
    python3 ateco/verifica.py             # dati, pagine, FAQ, indicizzazione, testi, monetizzazione
    python3 ateco/verifica.py --browser   # anche le prove nel browser (Playwright, 375 e 1280 px, chiaro e scuro)

1. Fonti: impronta SHA-256 dei file in raccolta/_grezzi = dati/fonti.json; HTTP 200; ogni frase cercata è nel testo salvato (rilette qui).
2. Dati: struttura, note, raccordo e tabella operativa riletti dai file xlsx e confrontati con dati/ateco.json; albero integro
   (padri, livelli, forma dei codici, nessun doppione); coefficienti del forfettario ricavati di nuovo dal testo di legge salvato.
3. Pagine: ogni codice ATECO 2025 ha la sua pagina o ancora con il titolo ufficiale; ogni nota Istat è nella pagina del suo codice;
   ogni corrispondenza 2022 di sesto livello e ogni coefficiente sono quelli ricalcolati; tabella 2022 → 2025 completa; titoli ≤ 65 e
   descrizioni 70-160 unici; canonical, sitemap, noindex, link interni e ancore, risorse, GoatCounter, IndexNow, robots, netlify.toml.
4. FAQ: ogni domanda nasce da una ricerca salvata; JSON-LD = testo visibile; nessun segnaposto.
5. Indicizzazione: nessuna pagina di codice indicizzata con meno di 120 gruppi di 5 parole propri o con il 60% o più del testo in
   comune con un'altra pagina di codice (ricalcolato sulle pagine scritte).
6. Testi: nessun nome di modelli o servizi di IA, nessun dato personale (titolare solo in privacy), frase fissa e licenza in ogni pagina.
7. Monetizzazione: monetizzazione.controlla_sito("ateco"); mestieri pubblicati solo con un volume misurato.
"""
import hashlib
import html as H
import json
import re
import subprocess
import sys
import warnings
from collections import Counter, defaultdict
from html import unescape
from pathlib import Path

import openpyxl

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
GREZZI = RADICE / "raccolta" / "_grezzi"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

URL_SITO = "https://codici-ateco.netlify.app"
FRASE_FISSA = "verifica con il commercialista o la Camera di commercio"
MIN_PAROLE_PROPRIE, MAX_SOVRAPPOSIZIONE = 150, 0.55
ERR, AVV = [], []


def errore(m):
    ERR.append(m)


def avviso(m):
    AVV.append(m)


def carica(n):
    return json.loads((DATI / n).read_text(encoding="utf-8"))


FJ = carica("fonti.json")
AT = carica("ateco.json")
CO = carica("coefficienti.json")
DOM = carica("domanda.json")
FAQ = carica("faq.json")["faq"]
MES = carica("mestieri.json")["mestieri"]
VOL = carica("volumi.json")


def visibile(html):
    t = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def norm(t):
    """Spazi uniformi, e nessuno spazio prima della punteggiatura (i link nelle note lasciano spazi dopo la rimozione dei tag)."""
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"\s+([,.;:)»])", r"\1", re.sub(r"([(«])\s+", r"\1", t))


def testo_html(b):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", b.decode("utf-8", errors="replace"), flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t))).strip()


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti():
    n = 0
    for gruppo in ("file", "pagine"):
        for fid, f in FJ[gruppo].items():
            p = GREZZI / f["file"]
            if not p.exists():
                errore(f"fonte {fid}: file grezzo assente ({p.name}): rilanciare raccolta/fonti.py")
                continue
            b = p.read_bytes()
            if hashlib.sha256(b).hexdigest() != f["sha256"]:
                errore(f"fonte {fid}: impronta diversa da fonti.json")
            if f.get("http") != 200:
                errore(f"fonte {fid}: HTTP {f.get('http')}")
            frasi = f.get("trovate") or {}
            if p.suffix == ".pdf":
                testo = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True).stdout)
            elif p.suffix == ".html":
                testo = testo_html(b)
            else:
                testo = None
            for c in frasi:
                n += 1
                if testo is not None and norm(c) not in norm(testo):
                    errore(f"fonte {fid}: frase non trovata nel file salvato «{c[:60]}»")
                if not frasi[c]:
                    errore(f"fonte {fid}: fonti.json segna la frase come mancante «{c[:60]}»")
    print(f"Fonti: {len(FJ['file'])} file e {len(FJ['pagine'])} pagine, impronte uguali, {n} frasi ritrovate nei testi salvati")


# ---------------------------------------------------------------- 2. dati
def foglio(nome, titolo):
    wb = openpyxl.load_workbook(GREZZI / nome, read_only=True)
    righe = list(wb[titolo].iter_rows(values_only=True))
    return [x if x is None else str(x) for x in righe[0]], righe[1:]


def pulito(x):
    if x is None:
        return ""
    return str(x).replace("_x000D_\n", "\n").replace("_x000D_", "\n").replace("\r\n", "\n").replace("\r", "\n").strip()


RAW = {}


def controlla_dati():
    C = AT["codici"]
    intest, righe = foglio("struttura.xlsx", "ATECO 2025 Struttura")
    i = {k: intest.index(k) for k in intest if k}
    raw = {}
    for r in righe:
        if r[i["CODICE_ATECO_2025"]] is None:
            continue
        c = pulito(r[i["CODICE_ATECO_2025"]])
        raw[c] = {"l": int(r[i["GERARCHIA_ATECO_2025"]]), "p": pulito(r[i["CODICE_PADRE_ATECO_2025"]]) or None, "it": pulito(r[i["TITOLO_ITALIANO_ATECO_2025"]]),
                  "en": pulito(r[i["TITOLO_INGLESE_ATECO_2025"]]), "de": pulito(r[i["TITOLO_TEDESCO_ATECO_2025"]])}
    if len(raw) != len(righe) - sum(1 for r in righe if r[i["CODICE_ATECO_2025"]] is None):
        errore("struttura: codici doppi nel file Istat")
    if set(raw) != set(C):
        errore(f"struttura: codici diversi tra file Istat e ateco.json ({sorted(set(raw) ^ set(C))[:5]})")
    forma = {1: r"[A-V]", 2: r"\d{2}", 3: r"\d{2}\.\d", 4: r"\d{2}\.\d{2}", 5: r"\d{2}\.\d{2}\.\d", 6: r"\d{2}\.\d{2}\.\d{2}"}
    for c, v in raw.items():
        if c not in C:
            continue
        for k in ("l", "p", "it", "en", "de"):
            if C[c][k] != v[k]:
                errore(f"{c}: {k} diverso dal file Istat")
        if not re.fullmatch(forma[v["l"]], c):
            errore(f"{c}: forma non coerente con il livello {v['l']}")
        if v["l"] > 1:
            p = v["p"]
            if p not in raw or raw[p]["l"] != v["l"] - 1:
                errore(f"{c}: padre {p} assente o di livello sbagliato")
            elif v["l"] > 2 and not c.startswith(p):
                errore(f"{c}: il codice non inizia con quello del padre {p}")
    figli = Counter(v["p"] for v in raw.values() if v["p"])
    foglie = [c for c, v in raw.items() if v["l"] < 6 and figli[c] == 0]
    if foglie:
        errore(f"albero: codici senza figli prima del sesto livello {foglie[:5]}")
    per_liv = Counter(v["l"] for v in raw.values())
    # note
    intest, righe = foglio("note.xlsx", "Note esplicative ATECO 2025")
    i = {k: intest.index(k) for k in intest if k}
    note = defaultdict(list)
    for r in righe:
        t = pulito(r[i["NOTA_ITALIANO_ATECO_2025"]])
        if t:
            note[pulito(r[i["CODICE_ATECO_2025"]])].append((int(r[i["CODICE_TIPO_NOTA"]]), t))
    for c in C:
        mie = [(n["t"], n["it"]) for n in C[c]["note"]]
        if mie != note.get(c, []):
            errore(f"{c}: note diverse dal file Istat")
    RAW["note"] = note
    # raccordo
    intest, righe = foglio("raccordo.xlsx", "ATECO 2025 vs ATECO 2022")
    i = {k: intest.index(k) for k in intest if k}
    rac = [(pulito(r[i["CODICE_ATECO_2025"]]), pulito(r[i["CODICE_ATECO_2022"]]) or None, pulito(r[i["CONTENUTO_COMUNE_ITALIANO"]])) for r in righe
           if r[i["CODICE_ATECO_2025"]] is not None]
    mio = [(r["c25"], r["c22"], r["comune"]) for r in AT["raccordo"]]
    if rac != mio:
        errore("raccordo: righe diverse dal file Istat")
    RAW["rac"] = rac
    # operativa
    intest, righe = foglio("operativa.xlsx", "Tabella operativa")
    i = {k: intest.index(k) for k in intest if k}
    op = {}
    for r in righe:
        if r[i["CODICE_ATECO_2022"]] is None:
            continue
        rap, cam = pulito(r[i["CODICE_ATECO_2025_RAPPRESENTATIVO"]]), pulito(r[i["CODICE_ATECO_2025_RAPPRESENTATIVO_SISTEMA_CAMERALE"]])
        op[pulito(r[i["CODICE_ATECO_2022"]])] = (pulito(r[i["TITOLO_ATECO_2022"]]), int(r[i["GERARCHIA_ATECO_2022"]]), None if rap == "n.d." else rap,
                                                  None if cam == "n.d." else cam, pulito(r[i["SOTTOTIPOLOGIA"]]))
    for c22, v in op.items():
        m = AT["operativa"].get(c22)
        if not m or (m["t22"], m["l"], m["rap"], m["cam"], m["tipo"]) != v:
            errore(f"operativa: {c22} diverso dal file Istat")
    if set(op) != set(AT["operativa"]):
        errore("operativa: codici diversi dal file Istat")
    RAW["op"] = op
    # coefficienti: tabella riletta dal testo di legge salvato, codici espansi in prefissi
    testo = testo_html((GREZZI / FJ["pagine"]["l190_all4"]["file"]).read_bytes()).replace("((", "").replace("))", "")
    testo = re.sub(r"\s+", " ", testo[testo.find("Coefficiente di redditività"):])
    gruppi = re.findall(r"\b(\d) ([A-Z][a-zA-Z' ,àèéìòù]+?) ([\d(][\d\s().\-da]*?) (\d{2}) ?%", testo)
    regole = {}
    for n, _, cod, perc in gruppi:
        pref = set()
        for pezzo in re.sub(r"[()]", " ", cod).split("-"):
            pezzo = pezzo.strip()
            m = re.fullmatch(r"da (\d{2})\.(\d) a (\d{2})\.(\d)", pezzo)
            if m:
                pref |= {f"{m.group(1)}.{k}" for k in range(int(m.group(2)), int(m.group(4)) + 1)}
            elif pezzo:
                pref.add(pezzo)
        regole[n] = (pref, int(perc))
    if len(regole) != 9 or {str(k): v[1] for k, v in regole.items()} != {k: v["coefficiente"] for k, v in CO["tabella"].items()}:
        errore(f"coefficienti: la tabella riletta dalla legge ({len(regole)} gruppi) non coincide con coefficienti.json")
    diversi = 0
    for c22, g in CO["gruppo_per_codice_2022"].items():
        trovati = [n for n, (pref, _) in regole.items() if any(c22.startswith(p) for p in pref)]
        if trovati != [str(g)]:
            diversi += 1
            if diversi <= 5:
                errore(f"coefficienti: {c22} → gruppi {trovati} ricalcolati, {g} in coefficienti.json")
    attesi = {c for c, v in op.items() if v[1] >= 4}
    if set(CO["gruppo_per_codice_2022"]) != attesi:
        errore("coefficienti: non tutti i codici ATECO 2022 di livello classe o inferiore hanno un gruppo")
    RAW["regole"] = regole
    print(f"Dati: {len(raw)} codici ATECO 2025 {dict(sorted(per_liv.items()))} = file Istat; albero integro; {sum(len(v) for v in note.values())} note, "
          f"{len(rac)} righe di raccordo, {len(op)} codici della tabella operativa uguali ai file; {len(CO['gruppo_per_codice_2022'])} gruppi del "
          f"forfettario ricalcolati dal testo di legge ({diversi} differenze)")


# ---------------------------------------------------------------- 3. pagine
def pagine_html():
    return sorted(SITO.rglob("*.html"))


def pagina_classe(c):
    x = c
    C = AT["codici"]
    while C[x]["l"] > 4:
        x = C[x]["p"]
    return x.replace(".", "-") + "/index.html"


DOMINI_ESTERNI = ("istat.it", "normattiva.it", "agenziaentrate.gov.it", "creativecommons.org", "garanteprivacy.it", "policies.google.com",
                  "adssettings.google.com", "goatcounter.com", "gc.zgo.at", "codici-ateco.netlify.app")


def controlla_contenuti():
    """Ogni codice, nota, corrispondenza e coefficiente nella pagina giusta."""
    C = AT["codici"]
    cache = {}

    def leggi(rel):
        if rel not in cache:
            p = SITO / rel
            cache[rel] = p.read_text(encoding="utf-8") if p.exists() else ""
        return cache[rel]

    n_note = n_rac = n_coef = 0
    gruppo22 = {}
    for c22, (_, liv, _, _, _) in RAW["op"].items():
        if liv >= 4:
            for n, (pref, _) in RAW["regole"].items():
                if any(c22.startswith(p) for p in pref):
                    gruppo22.setdefault(c22, set()).add(int(n))
    perc = {int(n): v[1] for n, v in RAW["regole"].items()}
    for c, v in C.items():
        if v["l"] == 1:
            rel = f"sezione-{c.lower()}/index.html"
        elif v["l"] == 2:
            rel = f"{c}/index.html"
        elif v["l"] == 3:
            rel = f"{c[:2]}/index.html"
        else:
            rel = pagina_classe(c)
        html = leggi(rel)
        if not html:
            errore(f"{c}: pagina {rel} assente")
            continue
        if v["l"] in (3, 5, 6):
            ancora = f'id="g-{c}"' if v["l"] == 3 else f'id="c-{c}"'
            if v["l"] == 5 and ancora not in html:
                # categoria con un solo figlio di uguale titolo e senza note: basta la sottocategoria
                continue
            if ancora not in html:
                errore(f"{c}: ancora assente in {rel}")
                continue
        vis = norm(visibile(html))
        if v["it"] not in vis and not (v["l"] == 1 and v["it"].lower() in vis.lower()):
            errore(f"{c}: titolo ufficiale assente in {rel}")
        for t, testo in RAW["note"].get(c, []):
            n_note += 1
            if norm(testo) not in vis:
                errore(f"{c}: nota Istat assente in {rel} «{testo[:50]}»")
        if v["l"] == 6:
            blocco = html[html.find(f'id="c-{c}"'):]
            blocco = blocco[:blocco.find("</section>")]
            vecchi = [r for r in RAW["rac"] if r[0] == c and r[1] and len(r[1]) == 8]
            for r in vecchi:
                n_rac += 1
                if r[1] not in blocco:
                    errore(f"{c}: vecchio codice {r[1]} assente nella scheda")
            gg = sorted({g for r in vecchi for g in gruppo22.get(r[1], ())})
            m = re.search(r'<p class="coef"><span>Forfettario[^<]*</span>(.*?)</p>', blocco, re.S)
            if not m:
                errore(f"{c}: riga del forfettario assente")
                continue
            n_coef += 1
            visto = sorted({int(x) for x in re.findall(r"<b>(\d{2})%</b>", m.group(1))})
            if visto != sorted({perc[g] for g in gg}):
                errore(f"{c}: coefficienti mostrati {visto}, ricalcolati {sorted({perc[g] for g in gg})}")
    # tabella 2022 -> 2025
    d22 = leggi("da-ateco-2022-a-2025/index.html")
    righe = dict(re.findall(r'<tr id="v-([\d.]+)">(.*?)</tr>', d22, re.S))
    sei = {c22: v for c22, v in RAW["op"].items() if v[1] == 6}
    if set(righe) != set(sei):
        errore(f"tabella 2022 → 2025: righe diverse dai codici della tabella operativa ({len(righe)} contro {len(sei)})")
    for c22, v in sei.items():
        r = righe.get(c22, "")
        if v[2] and f">{v[2]}</a>" not in r:
            errore(f"tabella 2022 → 2025: {c22} senza il codice rappresentativo {v[2]}")
        tutte = {x[0] for x in RAW["rac"] if x[1] == c22 and len(x[0]) == 8}
        if len(tutte) > 1 and set(re.findall(r'href="/[\d-]+/#c-([\d.]+)"', r)) < tutte:
            errore(f"tabella 2022 → 2025: {c22} non elenca tutte le {len(tutte)} corrispondenze")
    print(f"Contenuti: {len(C)} codici nella pagina giusta con il titolo ufficiale; {n_note} note Istat ritrovate; {n_rac} vecchi codici e "
          f"{n_coef} coefficienti delle sottocategorie uguali al ricalcolo; tabella 2022 → 2025 con {len(righe)} righe")


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
        if ni:
            noindex += 1
            if c:
                errore(f"{rel}: noindex con canonical")
            if MON.adsense_attivo("ateco") and MON.SEGNO_SENZA_ADSENSE not in html:
                errore(f"{rel}: pagina noindex senza il segno «niente pubblicità»")
            if "googlesyndication" in html:
                errore(f"{rel}: pubblicità in una pagina noindex")
        else:
            if len(dd) < 70:
                errore(f"{rel}: descrizione di {len(dd)} caratteri (min 70)")
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
        if "CC BY 4.0" not in vis or "Istat" not in vis:
            errore(f"{rel}: manca l'attribuzione Istat con la licenza")
        if "non affiliato a Istat" not in vis:
            errore(f"{rel}: manca «non affiliato a Istat»")
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
        for src in re.findall(r'(?:src|href|data-indice)="(/assets/[^"#]+)"', html):
            if src.lstrip("/") not in file_esistenti:
                errore(f"{rel}: risorsa assente {src}")
    sm = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    if locs != canon:
        errore(f"sitemap diversa dai canonical: {sorted(locs ^ canon)[:5]}")
    rb = (SITO / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {URL_SITO}/sitemap.xml" not in rb:
        errore("robots.txt senza sitemap")
    chiave = "b5a26a844a465f58552debee2c8a0114"
    if not (SITO / f"{chiave}.txt").exists() or (SITO / f"{chiave}.txt").read_text(encoding="utf-8") != chiave:
        errore("file chiave IndexNow assente o diverso")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in (SITO / "netlify.toml").read_text(encoding="utf-8"):
        errore("netlify.toml senza la regola che evita pubblicazioni inutili")
    for f in ("assets/og.png", "404.html"):
        if not (SITO / f).exists():
            errore(f"manca {f}")
    indice = next(SITO.glob("assets/indice.*.json"), None)
    if not indice:
        errore("indice di ricerca assente")
    else:
        voci = json.loads(indice.read_text(encoding="utf-8"))
        codici25 = {v[0] for v in voci if v[3] == "25"}
        if codici25 != set(AT["codici"]):
            errore("indice di ricerca: non contiene tutti i codici ATECO 2025")
    print(f"Pagine: {len(pagine_html())} file HTML, {len(canon)} indicizzabili (= sitemap), {noindex} noindex senza pubblicità; "
          "titoli ≤ 65 e descrizioni ≤ 160 unici; link e ancore interne a posto")


# ---------------------------------------------------------------- 4. FAQ
def controlla_faq():
    sugg = {s for v in DOM["radici"].values() for s in v}
    domande = {}
    for x in FAQ:
        if x["ricerca"] not in sugg:
            errore(f"FAQ «{x['q'][:40]}»: ricerca «{x['ricerca']}» non tra i suggerimenti salvati")
        for fid in x["fonti"]:
            if fid not in FJ["file"] and fid not in FJ["pagine"]:
                errore(f"FAQ «{x['q'][:40]}»: fonte sconosciuta {fid}")
        domande[x["q"]] = x
    C, OP = AT["codici"], AT["operativa"]
    n = 0
    for p in pagine_html():
        html = p.read_text(encoding="utf-8")
        vis = visibile(html)
        if re.search(r"\{[a-z_0-9]+\}", vis):
            errore(f"{p.relative_to(SITO)}: segnaposto non sostituito")
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            ld = json.loads(blocco)
            if ld.get("@type") != "FAQPage":
                continue
            for q in ld["mainEntity"]:
                n += 1
                a = q["acceptedAnswer"]["text"]
                if norm(q["name"]) not in vis or norm(a) not in vis:
                    errore(f"{p.relative_to(SITO)}: FAQ JSON-LD diversa dal testo visibile ({q['name'][:40]})")
                if q["name"] not in domande:
                    errore(f"{p.relative_to(SITO)}: FAQ senza ricerca registrata ({q['name'][:40]})")
                for cod, tit in re.findall(r"(\d{2}\.\d{2}\.\d{2}) «([^»]+)»", a):
                    if not ((cod in C and C[cod]["it"] == tit) or (cod in OP and OP[cod]["t22"] == tit)):
                        errore(f"{p.relative_to(SITO)}: FAQ con un titolo non ufficiale per {cod}")
    print(f"FAQ: {n} domande nelle pagine, tutte da ricerche vere ({len(sugg)} suggerimenti salvati il {DOM['letto_il']}); JSON-LD = testo visibile")


# ---------------------------------------------------------------- 5. indicizzazione
def controlla_indicizzazione():
    insiemi, indic = {}, {}
    for p in pagine_html():
        rel = str(p.relative_to(SITO))
        if not (re.fullmatch(r"(sezione-[a-v]|\d{2}|\d{2}-\d{2})/index\.html", rel)):
            continue
        html = p.read_text(encoding="utf-8")
        m = re.search(r"<main\b.*?</main>", html, re.S).group(0)
        m = re.sub(r'<p class="disclaimer">.*?</p>', " ", m, flags=re.S)
        m = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", m, flags=re.S | re.I)
        w = re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", m)).lower())
        insiemi[rel] = {" ".join(w[i:i + 5]) for i in range(len(w) - 4)}
        indic[rel] = '<meta name="robots" content="noindex">' not in html
    conta = Counter(g for s in insiemi.values() for g in s)
    peggio, poche = 0.0, 10 ** 9
    for rel, a in insiemi.items():
        if not indic[rel]:
            continue
        proprie = sum(1 for g in a if conta[g] == 1)
        poche = min(poche, proprie)
        if proprie < MIN_PAROLE_PROPRIE - 10:  # margine: la briciola di pane non entra nella misura di genera.py
            errore(f"{rel}: indicizzata con solo {proprie} gruppi di parole propri")
        q, simile = max(((len(a & b) / len(a), r2) for r2, b in insiemi.items() if r2 != rel), default=(0, ""))
        peggio = max(peggio, q)
        if q >= MAX_SOVRAPPOSIZIONE + 0.02:
            errore(f"{rel}: indicizzata ma {q:.0%} del testo è in comune con {simile}")
    n = sum(indic.values())
    print(f"Indicizzazione: {n} pagine di codice indicizzate su {len(indic)}; testo in comune con la pagina più simile al massimo {peggio:.0%} "
          f"(soglia {MAX_SOVRAPPOSIZIONE:.0%}); gruppi di parole propri almeno {poche}")


# ---------------------------------------------------------------- 6. testi e mestieri
VIETATE = re.compile(r"\b(claude|anthropic|openai|chatgpt|gpt-?\d|gemini|llama|mistral|copilot|opus|sonnet|haiku)\b", re.I)
TITOLARE = "Titolare del trattamento è Massimiliano Cori (Italia)"
PERSONALI = re.compile(r"massimiliano|\bcori\b|@gmail|@outlook|@libero", re.I)
CONSIGLI = re.compile(r"\b(ti consigliamo|consigliamo di|ti suggeriamo|conviene|è meglio scegliere|devi scegliere|scegli il codice)\b", re.I)


def controlla_testi():
    files = [p for p in RADICE.rglob("*") if p.is_file() and "_grezzi" not in p.parts and "cache" not in p.parts and "__pycache__" not in p.parts
             and p.suffix in (".py", ".json", ".html", ".md", ".css", ".js", ".txt", ".xml", ".toml")]
    for p in files:
        if p.name in ("verifica.py", "domanda.json") or p.parent.name == "assets":
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
            errore(f"{p.relative_to(SITO)}: frase che sembra un consiglio («{CONSIGLI.search(v).group(0)}»)")
    # mestieri: pagina solo con volume misurato
    for m in MES:
        vol = sum(VOL["frasi"][f]["volume"] for f in m["frasi"] if f in VOL["frasi"])
        esiste = (SITO / m["slug"] / "index.html").exists()
        if esiste and not vol:
            errore(f"{m['slug']}: pagina pubblicata senza un volume di ricerca misurato")
        if vol and not esiste:
            errore(f"{m['slug']}: volume misurato ma pagina assente")
        for c in m["codici"] + m["vicini"]:
            if c not in AT["codici"]:
                errore(f"{m['slug']}: codice {c} non esiste in ATECO 2025")
        for c in m["vecchi"]:
            if c not in AT["operativa"]:
                errore(f"{m['slug']}: codice 2022 {c} non esiste")
    print(f"Testi: nessun nome di IA, nessun dato personale fuori dalla privacy, nessuna frase di consiglio; mestieri pubblicati solo con volume misurato")


# ---------------------------------------------------------------- 7. monetizzazione
def controlla_monetizzazione():
    e, info = MON.controlla_sito("ateco", SITO)
    for x in e:
        errore("monetizzazione: " + x)
    aff = carica("affiliati.json")
    if info["link_affiliati"] != 0 and not any(v.get("url") for k, v in aff.items() if not k.startswith("_")):
        errore("link di affiliazione presenti ma dati/affiliati.json è spento")
    senza = sum(1 for p in pagine_html() if MON.SEGNO_SENZA_ADSENSE in p.read_text(encoding="utf-8"))
    print(MON.riepilogo("ateco", info, e) + f"; pagine senza pubblicità (noindex o poco testo): {senza}")


# ---------------------------------------------------------------- 8. browser
PAGINE_BROWSER = ["/", "/56-11/", "/codice-ateco-parrucchiere/", "/da-ateco-2022-a-2025/"]


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
                    scuro = sfondo == "rgb(11, 16, 32)"
                    if (tema == "dark") != scuro:
                        errore(f"browser {w}px {tema} {u}: sfondo {sfondo} non coerente con il tema")
                    if u == "/":
                        prove = [("pizzeria", "/56-11/#c-56.11.11"), ("96.21", "/96-21/"), ("96.02.01", "/da-ateco-2022-a-2025/#v-96.02.01"),
                                 ("programmazione informatica", "/62-10/")]
                        for q, atteso in prove:
                            pg.fill("[data-cerca]", q)
                            pg.wait_for_selector("[data-risultati] a", timeout=5000)
                            hrefs = pg.eval_on_selector_all("[data-risultati] a", "a=>a.map(x=>x.getAttribute('href'))")
                            if not any(hh.startswith(atteso) for hh in hrefs[:5]):
                                errore(f"browser: la ricerca «{q}» non porta a {atteso} tra i primi 5 ({hrefs[:5]})")
                        pg.fill("[data-cerca]", "zzzzqq")
                        if "Nessun codice trovato" not in pg.inner_text("[data-risultati]"):
                            errore("browser: ricerca senza risultati senza messaggio")
                        pg.fill("[data-cerca]", "")
                    if u == "/da-ateco-2022-a-2025/":
                        tot = pg.locator("[data-tabella] tbody tr").count()
                        if pg.locator("[data-tabella] tbody tr:visible").count() != 100 or not pg.locator("[data-altre]").is_visible():
                            errore("browser: la tabella 2022 → 2025 deve aprirsi con 100 righe e il pulsante «Mostra altri»")
                        pg.fill("[data-filtro]", "47.91.10")
                        vis = pg.locator("[data-tabella] tbody tr:visible").count()
                        if vis != 1:
                            errore(f"browser: il filtro «47.91.10» mostra {vis} righe invece di 1")
                        pg.fill("[data-filtro]", "parrucchiere")
                        if pg.locator("[data-tabella] tbody tr:visible").count() < 1:
                            errore("browser: il filtro «parrucchiere» non trova righe")
                        pg.fill("[data-filtro]", "")
                        pg.click("[data-altre-tutte]")
                        if pg.locator("[data-tabella] tbody tr:visible").count() != tot:
                            errore("browser: «Mostra tutti» non mostra tutte le righe")
                    nome = (u.strip("/").replace("/", "_") or "home")
                    pg.screenshot(path=str(shot / f"{nome}_{w}_{tema}.png"), full_page=(u != "/da-ateco-2022-a-2025/"))
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
    print(f"Browser: {len(PAGINE_BROWSER)} pagine × 375/1280 px × chiaro/scuro (richieste esterne bloccate), ricerca, filtro e tema; screenshot in {shot}")


def main():
    controlla_fonti()
    controlla_dati()
    controlla_contenuti()
    controlla_pagine()
    controlla_faq()
    controlla_indicizzazione()
    controlla_testi()
    controlla_monetizzazione()
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
