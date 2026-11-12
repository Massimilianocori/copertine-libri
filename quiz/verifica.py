"""Controlli di Quiz Ufficiali. Rilegge tutte le banche dai PDF grezzi con un lettore scritto a parte (non usa raccolta/estrai.py).

Uso (dalla radice del repository):
    python3 quiz/verifica.py             # fonti, banche, pagine, SEO, testi, monetizzazione
    python3 quiz/verifica.py --browser   # anche le prove nel browser (Playwright, 375 e 1280 px, richieste esterne bloccate)

1. Fonti: impronta SHA-256 dei PDF = dati/fonti.json; HTTP 200; frasi delle regole d'esame ritrovate nel testo.
2. Banche, ricalcolate dai PDF con metodi diversi da estrai.py:
   - Lazio e Valle d'Aosta: per ogni rettangolo giallo si ritaglia il PDF e si legge il testo evidenziato; numero di domande
     contato dalle righe «a)» del testo; la risposta esatta del JSON deve stare in un'area evidenziata della sua pagina;
   - Sicilia: tabella finale delle risposte riletta dal testo; segni ✓/* contati;
   - Palermo ed Enna, Cagliari-Oristano: [*] contati scheda per scheda; risposta esatta cercata sulla riga [*] del PDF;
   - Sassari: colonna «Esatta» letta per posizione delle parole (senza l'estrazione a tabella);
   per ogni banca: numero di domande e di risposte esatte, chiave completa dove c'è un secondo riferimento, e 50 domande a caso
   (testo, tre risposte, risposta esatta) cercate nella pagina indicata del PDF.
3. Pagine: titoli ≤ 65 e descrizioni ≤ 160 uniche, un h1, canonical, sitemap = canonical, noindex fuori dalla sitemap e senza
   AdSense, link interni, ogni banca con tutte le sue domande e la stessa chiave del JSON, GoatCounter, robots, IndexNow, netlify.toml.
4. Testi: nessun nome di modello di IA, nessun dato personale (il titolare solo nella privacy), nessuna «spiegazione» aggiunta.
5. Monetizzazione: controlli comuni di studio-business/strumenti/monetizzazione.py.
"""
import hashlib
import json
import random
import re
import subprocess
import sys
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

import pdfplumber

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
GREZZI = RADICE / "raccolta" / "_grezzi"
URL_SITO = "https://quiz-ufficiali.netlify.app"  # = URL_SITO in genera.py
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

ERR, AVV = [], []
FJ = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))
BANCHE = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((DATI / "banche").glob("*.json"))}
CAMPIONE = 50
random.seed(20261112)


def errore(m):
    ERR.append(m)


def avviso(m):
    AVV.append(m)


def compatto(t):
    """Testo senza spazi, punteggiatura e maiuscole: serve a cercare un brano del JSON nel PDF qualunque sia l'impaginazione."""
    t = unescape(t).lower().replace("’", "'")
    return re.sub(r"[^0-9a-zàèéìòù]", "", t)


def testo_pagine(nome):
    out = subprocess.run(["pdftotext", str(GREZZI / nome), "-"], capture_output=True, text=True).stdout
    return out.split("\f")


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti():
    for fid, f in FJ["file"].items():
        p = GREZZI / f["file"]
        if f.get("http") != 200:
            errore(f"fonte {fid}: HTTP {f.get('http')}")
            continue
        if not p.exists():
            errore(f"fonte {fid}: manca il file grezzo {p} (rilanciare raccolta/fonti.py)")
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != f["sha256"]:
            errore(f"fonte {fid}: impronta SHA-256 diversa da fonti.json")
        if p.suffix == ".pdf":
            t = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True).stdout)
        else:
            t = re.sub(r"<(script|style)\b.*?</\1>", " ", p.read_text(encoding="utf-8", errors="replace"), flags=re.S | re.I)
            t = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t)))
        for fr in f.get("frasi", {}):
            if re.sub(r"\s+", " ", fr) not in t:
                errore(f"fonte {fid}: frase non trovata nel file: {fr[:70]}")
    print(f"Fonti: {len(FJ['file'])} file, impronte e frasi ricontrollate")


# ---------------------------------------------------------------- 2. banche dai PDF
def aree_gialle(nome):
    """Per pagina: aree evidenziate in giallo [(top, testo compatto)] lette ritagliando il PDF sul rettangolo, e righe di testo [(top, testo compatto)]."""
    aree, righe = {}, {}
    with pdfplumber.open(GREZZI / nome) as pdf:
        for pn, page in enumerate(pdf.pages, 1):
            out = []
            for r in page.rects:
                if r.get("non_stroking_color") == (1.0, 1.0, 0.0) and r["height"] >= 8:
                    box = (max(0, r["x0"] - 1), max(0, r["top"] - 1), min(page.width, r["x1"] + 1), min(page.height, r["bottom"] + 1))
                    out.append((r["top"], compatto(page.crop(box).extract_text() or "")))
            aree[pn] = out
            righe[pn] = [(ln["top"], compatto(ln["text"])) for ln in page.extract_text_lines()]
    return aree, righe


def controlla_evidenziate(id_, nome, attese_a):
    b = BANCHE[id_]["domande"]
    pag = testo_pagine(nome)
    n_a = sum(len(re.findall(r"(?m)^\s*a\)", p)) for p in pag)
    if n_a != len(b) or n_a != attese_a:
        errore(f"{id_}: il PDF ha {n_a} righe «a)», il JSON {len(b)} domande (attese {attese_a})")
    aree, righe = aree_gialle(nome)

    # Si ritrova ogni domanda dalla riga della sua risposta «a)», scorrendo il documento in ordine (molte domande iniziano uguali).
    tutte_righe = [(p, top, tx) for p in sorted(righe) for top, tx in righe[p]]
    cur, pos = 0, {}
    for d in sorted(b, key=lambda x: x["n"]):
        cerca = "a" + compatto(d["risposte"][0])[:20]
        while cur < len(tutte_righe) and not tutte_righe[cur][2].startswith(cerca):
            cur += 1
        if cur == len(tutte_righe):
            break
        pos[d["n"]] = (tutte_righe[cur][0], tutte_righe[cur][1])
        cur += 1
    if len(pos) != len(b):
        errore(f"{id_}: ritrovate nel PDF {len(pos)} domande su {len(b)}")
        return len(b)
    ordine = sorted(pos.values())
    sbagliate, ambigue = [], []
    for d in b:
        p0 = pos[d["n"]]
        dopo = [x for x in ordine if x > p0]
        p1 = dopo[0] if dopo else (p0[0] + 1, 0)
        # aree gialle dalla risposta «a)» di questa domanda fino alla risposta «a)» della successiva (anche a cavallo di pagina)
        mie = "".join(tx for p in range(p0[0], p1[0] + 1) for top, tx in aree.get(p, [])
                      if (p, top) >= (p0[0], p0[1] - 16) and (p, top) < (p1[0], p1[1] - 16))
        giusta = compatto(d["risposte"][d["esatta"]])
        if giusta[:40] not in mie:
            sbagliate.append(d["n"])
        altre = [compatto(r) for k, r in enumerate(d["risposte"]) if k != d["esatta"]]
        if any(len(a) > 8 and a not in giusta and a[:40] in mie.replace(giusta, "") for a in altre):
            ambigue.append(d["n"])
    if sbagliate:
        errore(f"{id_}: risposta esatta non evidenziata in giallo nel PDF per le domande {sbagliate[:15]}")
    if ambigue:
        errore(f"{id_}: più di una risposta evidenziata per le domande {ambigue[:15]}")
    return len(b)


def chiave_tabella_sicilia(nome):
    t = subprocess.run(["pdftotext", "-layout", str(GREZZI / nome), "-"], capture_output=True, text=True).stdout
    i = t.find("n.     risposta")  # intestazione della tabella finale «n. domanda / risposta esatta»
    coda = t[i:]
    return {int(n): l for n, l in re.findall(r"(?<!\S)(\d{1,3})\s+([abc])(?!\S)", coda)}


def controlla_sicilia(id_, nome, segno):
    b = BANCHE[id_]
    tab = chiave_tabella_sicilia(nome)
    escl = {e["n"] for e in b.get("escluse", [])}
    tot = len(b["domande"]) + len(escl)
    if len(tab) != tot:
        errore(f"{id_}: tabella finale con {len(tab)} righe, JSON {tot} domande (comprese le escluse)")
    for d in b["domande"]:
        if tab.get(d["n"]) != "abc"[d["esatta"]]:
            errore(f"{id_} n. {d['n']}: risposta {('abc'[d['esatta']])} nel JSON, {tab.get(d['n'])} nella tabella finale")
    for e in b.get("escluse", []):
        if tab.get(e["n"]) != e["tabella_finale"]:
            errore(f"{id_}: domanda esclusa {e['n']} con tabella finale diversa")
    t = subprocess.run(["pdftotext", "-layout", str(GREZZI / nome), "-"], capture_output=True, text=True).stdout
    segni = t.count("✓") if segno == "✓" else len(re.findall(r"(?m)^\s*[a-d][\.\)]?\s*\*|\*\s*[a-d][\.\)]", t))
    if segni != tot:
        errore(f"{id_}: {segni} segni «{segno}» nel PDF, {tot} domande")
    return len(b["domande"])


def controlla_schede(id_, nomi):
    """Palermo ed Enna e Cagliari-Oristano: [*] contati e risposta esatta sulla riga [*] del PDF."""
    b = BANCHE[id_]["domande"]
    righe_star = {}
    tot_star = 0
    for nome in nomi:
        t = subprocess.run(["pdftotext", "-layout", str(GREZZI / nome), "-"], capture_output=True, text=True).stdout
        tot_star += t.count("[*]")
        # testo della risposta [*] con le righe di continuazione (fino alla prossima opzione, domanda o riga vuota)
        righe = t.split("\n")
        stelle = []
        for i, r in enumerate(righe):
            if "[*]" in r:
                pezzo = r.split("[*]", 1)[1]
                for s in righe[i + 1:i + 12]:
                    s = s.replace("\f", "")
                    if not s.strip() or "esamiQuestServlet" in s or "ARCA - Documento" in s or "TESTATA" in s:
                        continue  # righe vuote, intestazioni e piè di pagina della stampa: la risposta può continuare alla pagina dopo
                    if (re.match(r"^\s*([A-D]\s*\[|\d+\))", s)
                            or re.fullmatch(r"\s{0,4}[A-Z][A-Z ’']{5,}\s*", s)):  # titolo di materia (rientro minimo), non riga di continuazione
                        break
                    pezzo += " " + s
                stelle.append(compatto(pezzo))
        righe_star[nome] = stelle
    for d in b:
        g = compatto(d["risposte"][d["esatta"]])
        if not any(g == s or (len(g) > 25 and s.startswith(g[:60])) for s in righe_star[d["file"]]):
            errore(f"{id_} n. {d['n']}: la risposta esatta del JSON non è su una riga [*] di {d['file']}")
    return len(b), tot_star


def controlla_nautica():
    """Elenco del Ministero: per ogni riga numerata si leggono per posizione le lettere V/F sotto le intestazioni «V/F» della pagina
    (senza l'estrazione a tabella usata da estrai.py). Le domande escluse devono avere un motivo; le altre la stessa chiave del JSON."""
    chiavi = {"BASE": {}, "VELA": {}}
    with pdfplumber.open(GREZZI / "mit/allegato_a_dd131_2022.pdf") as pdf:
        for page in pdf.pages:
            parole = page.extract_words()
            intest = [w for w in parole if w["text"].startswith("V/F")]  # a volte «V/F» è attaccato alla parola dopo
            if not intest:
                continue
            cap = "VELA" if len(intest) == 2 else "BASE"
            colonne = sorted(w["x0"] for w in intest)
            numeri = [w for w in parole if w["x0"] < 45 and re.fullmatch(r"\d{1,4}", w["text"]) and w["top"] > intest[0]["bottom"]]
            # lettere sotto le intestazioni V/F (le «v»/«f» minuscole isolate nel testo delle risposte non contano, salvo che stiano proprio nella colonna)
            lettere = [w for w in parole if w["text"] in ("V", "F", "v", "f") and any(c - 1 <= w["x0"] <= c + 9 for c in colonne)]
            for w in numeri:
                riga = []
                for c in colonne:
                    vicine = [x for x in lettere if c - 1 <= x["x0"] <= c + 9 and abs((x["top"] + x["bottom"]) / 2 - (w["top"] + w["bottom"]) / 2) < 14]
                    riga.append(vicine[0]["text"].upper() if len(vicine) == 1 else "?")
                chiavi[cap][int(w["text"])] = riga
    for id_, cap, tot in (("nautica-base", "BASE", 1472), ("nautica-vela", "VELA", 250)):
        b = BANCHE[id_]
        if len(chiavi[cap]) != tot:
            errore(f"{id_}: {len(chiavi[cap])} righe numerate lette per posizione, {tot} attese")
        if len(b["domande"]) + len(b["escluse"]) != tot or b.get("totale_pdf") != tot:
            errore(f"{id_}: {len(b['domande'])} domande + {len(b['escluse'])} escluse diverso da {tot}")
        for d in b["domande"]:
            r = chiavi[cap].get(d["n"], [])
            if r.count("V") != 1 or r.index("V") != d["esatta"] or "?" in r:
                errore(f"{id_} n. {d['n']}: chiave V/F letta per posizione {r}, JSON {d['esatta']}")
            if FIGURA_V.search(d["testo"]):
                errore(f"{id_} n. {d['n']}: domanda che rimanda a una figura")
        for e in b["escluse"]:
            if not e.get("motivo"):
                errore(f"{id_}: domanda esclusa {e['n']} senza motivo")
    return len(BANCHE["nautica-base"]["domande"]), len(BANCHE["nautica-vela"]["domande"])


FIGURA_V = re.compile(r"figura|disegno|immagine|freccia", re.I)


def controlla_sassari():
    b = BANCHE["taxi-ncc-sassari"]["domande"]
    chiave = {}
    with pdfplumber.open(GREZZI / "taxi_sassari.pdf") as pdf:
        for page in pdf.pages:
            parole = page.extract_words()
            col_n = [w for w in parole if 68 < w["x0"] < 106 and re.fullmatch(r"\d{1,3}", w["text"])]
            col_e = [w for w in parole if w["x0"] > 787 and w["text"] in ("A", "B", "C")]
            for w in col_n:
                vicine = sorted(col_e, key=lambda e: abs((e["top"] + e["bottom"]) / 2 - (w["top"] + w["bottom"]) / 2))
                if vicine and abs(vicine[0]["top"] - w["top"]) < 12:
                    chiave[int(w["text"])] = "ABC".index(vicine[0]["text"])
    if len(chiave) != len(b):
        errore(f"taxi-ncc-sassari: {len(chiave)} numeri con «Esatta» letti per posizione, {len(b)} nel JSON")
    for d in b:
        if chiave.get(d["n"]) != d["esatta"]:
            errore(f"taxi-ncc-sassari n. {d['n']}: chiave {d['esatta']} nel JSON, {chiave.get(d['n'])} letta per posizione")
    return len(b)


def campione(id_):
    """50 domande a caso: testo e tre risposte cercati nella pagina indicata del PDF (e nella successiva, se la domanda va a capo)."""
    b = BANCHE[id_]["domande"]
    cache = {}
    scelte = random.sample(b, min(CAMPIONE, len(b)))
    for d in scelte:
        if d["file"] not in cache:
            cache[d["file"]] = [compatto(p) for p in testo_pagine(d["file"])]
        pag = cache[d["file"]]
        zona = "".join(pag[d["pagina"] - 1:d["pagina"] + 1])
        for parte in [d["testo"]] + d["risposte"]:
            c = compatto(parte)
            if c and c not in zona:
                # nelle tabelle (Sassari) le celle vanno a capo in colonne affiancate: si cerca parola per parola
                parole = [compatto(w) for w in parte.split() if len(compatto(w)) > 3]
                if not parole or sum(w in zona for w in parole) / len(parole) < 0.9:
                    errore(f"{id_} n. {d['n']}: testo non trovato a pagina {d['pagina']} di {d['file']}: «{parte[:60]}»")
    return len(scelte)


def controlla_banche():
    righe = []
    righe.append(("tartufi-lazio", controlla_evidenziate("tartufi-lazio", "tart_lazio_2015.pdf", 275)))
    righe.append(("fitosanitario-valle-d-aosta", controlla_evidenziate("fitosanitario-valle-d-aosta", "fito_vda.pdf", len(BANCHE["fitosanitario-valle-d-aosta"]["domande"]))))
    righe.append(("fitosanitario-sicilia-utilizzatori", controlla_sicilia("fitosanitario-sicilia-utilizzatori", "fito_sicilia_util.pdf", "✓")))
    righe.append(("fitosanitario-sicilia-consulenti", controlla_sicilia("fitosanitario-sicilia-consulenti", "fito_sicilia_cons.pdf", "*")))
    schede = [f["file"] for k, f in FJ["file"].items() if re.fullmatch(r"paen_\d+", k)]
    n, stelle = controlla_schede("taxi-ncc-palermo-enna", schede)
    pa = BANCHE["taxi-ncc-palermo-enna"]
    if n + pa["scartate"]["doppie"] + pa["scartate"]["nulle"] != stelle:
        errore(f"taxi-ncc-palermo-enna: {stelle} [*] nelle schede, {n} domande + {pa['scartate']['doppie']} doppie + {pa['scartate']['nulle']} nulle")
    righe.append(("taxi-ncc-palermo-enna", n))
    n, stelle = controlla_schede("taxi-ncc-cagliari-oristano", ["taxi_caor.pdf"])
    if n != stelle:
        errore(f"taxi-ncc-cagliari-oristano: {stelle} [*] nel PDF, {n} domande nel JSON")
    righe.append(("taxi-ncc-cagliari-oristano", n))
    righe.append(("taxi-ncc-sassari", controlla_sassari()))
    nb, nv = controlla_nautica()
    righe += [("nautica-base", nb), ("nautica-vela", nv)]
    if set(r[0] for r in righe) != set(BANCHE):
        errore(f"banche senza controllo: {set(BANCHE) - set(r[0] for r in righe)}")
    for id_, d in BANCHE.items():
        for q in d["domande"]:
            attese = 2 if id_ == "nautica-vela" else 3
            if len(q["risposte"]) != attese or not (0 <= q["esatta"] < attese) or not q["testo"] or not all(q["risposte"]):
                errore(f"{id_} n. {q['n']}: domanda incompleta")
        nn = [q["n"] for q in d["domande"]]
        if len(set(nn)) != len(nn):
            errore(f"{id_}: numeri ripetuti")
        campione(id_)
    lz = BANCHE["tartufi-lazio"].get("confronto_guida_2021", {})
    if lz.get("differenze") != 0 or lz.get("domande") != 275:
        avviso(f"Lazio: la guida 2021 e la determinazione 2015 non coincidono ({lz})")
    print("Banche ricontrollate dai PDF: " + ", ".join(f"{k} {v}" for k, v in righe) + f"; {CAMPIONE} domande a caso per banca")


# ---------------------------------------------------------------- 3. pagine
def pagine_html():
    return sorted(SITO.rglob("*.html"))


def percorso(f):
    r = f.relative_to(SITO).as_posix()
    return "/" + (r[:-len("index.html")] if r.endswith("index.html") else r)


def controlla_pagine():
    titoli, descr, canon = {}, {}, set()
    for f in pagine_html():
        t = f.read_text(encoding="utf-8")
        u = percorso(f)
        if re.fullmatch(r"google[0-9a-f]+\.html", f.name):
            continue
        m = re.search(r"<title>(.*?)</title>", t)
        md = re.search(r'<meta name="description" content="([^"]*)"', t)
        tit, des = unescape(m.group(1)) if m else "", unescape(md.group(1)) if md else ""
        if not tit or len(tit) > 65:
            errore(f"{u}: titolo assente o oltre 65 caratteri ({len(tit)}): {tit}")
        if not des or len(des) > 160 or (f.name != "404.html" and len(des) < 70):
            errore(f"{u}: descrizione di {len(des)} caratteri")
        titoli.setdefault(tit, []).append(u)
        descr.setdefault(des, []).append(u)
        if t.count("<h1") != 1:
            errore(f"{u}: {t.count('<h1')} h1")
        noindex = '<meta name="robots" content="noindex">' in t
        c = re.search(r'<link rel="canonical" href="([^"]+)">', t)
        if noindex:
            if c:
                errore(f"{u}: noindex con canonical")
            if "googlesyndication" in t:
                errore(f"{u}: noindex con AdSense")
        else:
            if not c or c.group(1) != URL_SITO + u:
                errore(f"{u}: canonical {c.group(1) if c else None} diverso da {URL_SITO + u}")
            else:
                canon.add(c.group(1))
        if "rete-siti.goatcounter.com/count" not in t:
            errore(f"{u}: manca GoatCounter")
        for href in re.findall(r'href="(/[^"#?]*)', t):
            p = SITO / href.lstrip("/")
            if not (p.is_file() or (p / "index.html").is_file()):
                errore(f"{u}: link interno rotto {href}")
        for href in re.findall(r'href="#([^"]+)"', t):
            if f'id="{href}"' not in t:
                errore(f"{u}: ancora #{href} senza destinazione")
    for k, v in titoli.items():
        if len(v) > 1:
            errore(f"titolo ripetuto in {v}: {k}")
    for k, v in descr.items():
        if len(v) > 1:
            errore(f"descrizione ripetuta in {v}")
    sm = set(re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8")))
    if sm != canon:
        errore(f"sitemap diversa dai canonical: solo sitemap {sorted(sm - canon)[:5]}, solo canonical {sorted(canon - sm)[:5]}")
    rb = (SITO / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {URL_SITO}/sitemap.xml" not in rb:
        errore("robots.txt senza sitemap")
    chiave = "b5a26a844a465f58552debee2c8a0114"
    if (SITO / f"{chiave}.txt").read_text(encoding="utf-8") != chiave:
        errore("file della chiave IndexNow assente o diverso")
    nt = (SITO / "netlify.toml").read_text(encoding="utf-8")
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in nt or "quiz/sito" not in nt:
        errore("netlify.toml senza regola ignore o base directory")
    if not (SITO / "assets" / "og.png").exists():
        errore("manca assets/og.png")
    if not (SITO / "404.html").exists():
        errore("manca 404.html")
    print(f"Pagine: {len(pagine_html())} file HTML, {len(canon)} indicizzate = sitemap")


def controlla_banche_nelle_pagine():
    mappa = {"nautica-base": "patente-nautica/quiz-base", "nautica-vela": "patente-nautica/quiz-vela", "tartufi-lazio": "tartufi/lazio", "fitosanitario-valle-d-aosta": "patentino-fitosanitario/valle-d-aosta",
             "fitosanitario-sicilia-utilizzatori": "patentino-fitosanitario/sicilia-utilizzatori",
             "fitosanitario-sicilia-consulenti": "patentino-fitosanitario/sicilia-consulenti",
             "taxi-ncc-palermo-enna": "ruolo-conducenti/palermo-enna", "taxi-ncc-sassari": "ruolo-conducenti/sassari",
             "taxi-ncc-cagliari-oristano": "ruolo-conducenti/cagliari-oristano"}
    if set(mappa) != set(BANCHE):
        errore("mappa banche -> pagine incompleta in verifica.py")
    for id_, p in mappa.items():
        t = (SITO / p / "index.html").read_text(encoding="utf-8")
        voci = re.findall(r'<li id="d-(\d+)" data-dom data-n="\d+" data-s="\d+" data-e="(\d)" data-p="(\d+)"[^>]*><p class="dq"><span class="num">\d+\.</span> '
                          r'<span class="t">(.*?)</span></p><ol class="opz" type="a">(.*?)</ol>', t)
        D = {d["n"]: d for d in BANCHE[id_]["domande"]}
        if len(voci) != len(D):
            errore(f"/{p}/: {len(voci)} domande nella pagina, {len(D)} nel JSON")
        for n, e, pg, testo, opz in voci:
            d = D.get(int(n))
            if not d:
                errore(f"/{p}/: domanda {n} non nel JSON")
                continue
            risp = [unescape(x) for x in re.findall(r'<span class="r">(.*?)</span>', opz)]
            if int(e) != d["esatta"] or int(pg) != d["pagina"] or unescape(testo) != d["testo"] or risp != d["risposte"]:
                errore(f"/{p}/ n. {n}: pagina diversa dal JSON")
            if opz.count("risposta ufficiale") != 1 or 'class="esatta"' not in opz.split("</li>")[d["esatta"]]:
                errore(f"/{p}/ n. {n}: segno della risposta ufficiale sulla risposta sbagliata")
        m = re.search(r"<h1>(.*?)</h1>", t)
        if m and f"{len(D):,}".replace(",", ".") not in m.group(1):
            errore(f"/{p}/: il titolo non riporta il numero di domande ({len(D)})")
    print(f"Pagine delle banche: {sum(len(b['domande']) for b in BANCHE.values())} domande, testo e chiave uguali ai JSON")


# ---------------------------------------------------------------- 4. testi
MODELLI_IA = re.compile(r"\b(ChatGPT|GPT-?\d|OpenAI|Claude|Anthropic|Gemini|Copilot|Llama|Mistral|Sonnet|Opus|Haiku)\b")


def controlla_testi():
    # Il testo ufficiale delle domande (elenco nella pagina, JSON delle banche) è escluso: nella banca di Cagliari «Mistral» è il vento.
    file_ = list(pagine_html()) + [RADICE / "NOTE.md"] + [p for p in DATI.rglob("*.json") if p.parent.name != "banche"]
    for f in file_:
        if not f.exists():
            errore(f"manca {f}")
            continue
        t = re.sub(r'<ol class="domande">.*?</ol></details>', " ", f.read_text(encoding="utf-8"), flags=re.S)
        m = MODELLI_IA.search(t)
        if m:
            errore(f"{f.relative_to(RADICE)}: nome di modello di IA «{m.group(0)}»")
    for f in pagine_html():
        t = f.read_text(encoding="utf-8")
        if "Massimiliano" in t and "/privacy/" not in percorso(f):
            errore(f"{percorso(f)}: nome del titolare fuori dalla privacy")
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", re.sub(r"<script.*?</script>", "", t, flags=re.S)):
            errore(f"{percorso(f)}: indirizzo email nella pagina")
        vis = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S))
        if re.search(r"\bspiegazione:|\bperché la risposta", vis, re.I):
            errore(f"{percorso(f)}: sembra una spiegazione aggiunta")
    print("Testi: nessun nome di modello di IA, nessun dato personale fuori dalla privacy")


# ---------------------------------------------------------------- 5. monetizzazione
def controlla_monetizzazione():
    errori, info = MON.controlla_sito("quiz", SITO)
    for e in errori:
        errore("monetizzazione: " + e)
    print(MON.riepilogo("quiz", info, errori))
    aff = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8"))
    if aff.get("easy_quizzz", {}).get("attivo") or aff.get("easy_quizzz", {}).get("url"):
        errore("affiliati.json: Easy-Quizzz acceso senza un link presente nel repository")
    for f in pagine_html():
        t = f.read_text(encoding="utf-8")
        if "amazon." in t and not percorso(f).startswith(("/ruolo-conducenti/", "/patente-nautica/")):
            errore(f"{percorso(f)}: link Amazon fuori dai moduli con manuali d'esame (taxi/NCC, patente nautica)")


# ---------------------------------------------------------------- 6. browser
PAGINE_BROWSER = ["/", "/patente-nautica/quiz-base/", "/ruolo-conducenti/sassari/", "/patentino-fitosanitario/sicilia-utilizzatori/"]


def controlla_browser():
    import mimetypes
    from playwright.sync_api import sync_playwright
    shot = RADICE / "cache" / "screenshot"
    shot.mkdir(parents=True, exist_ok=True)
    esterne = []

    def servi(route):
        url = route.request.url
        if not url.startswith("http://sito.test/"):
            esterne.append(url)
            return route.abort()  # niente rete: solo i file del sito (il simulatore deve funzionare senza connessione)
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
                    if (tema == "dark") != (sfondo == "rgb(11, 15, 28)"):
                        errore(f"browser {w}px {tema} {u}: sfondo {sfondo} non coerente con il tema")
                    nome = (u.strip("/").replace("/", "_") or "home")
                    pg.screenshot(path=str(shot / f"{nome}_{w}_{tema}.png"))
                    if u.count("/") == 3 and w == 375 and tema == "light":
                        prova_simulatore(pg, u)
                pg.goto("http://sito.test/")
                prima = pg.evaluate("getComputedStyle(document.body).backgroundColor")
                pg.click("[data-tema]")
                if prima == pg.evaluate("getComputedStyle(document.body).backgroundColor"):
                    errore(f"browser {w}px {tema}: il pulsante del tema non cambia lo sfondo")
                if errori_js:
                    errore(f"browser {w}px {tema}: errori JS {errori_js[:3]}")
                ctx.close()
        b.close()
    print(f"Browser: {len(PAGINE_BROWSER)} pagine × 375/1280 px × chiaro/scuro, simulatore provato senza rete "
          f"({len(esterne)} richieste esterne bloccate); screenshot in {shot}")


def prova_simulatore(pg, u):
    """Esame completo rispondendo sempre giusto (poi sempre sbagliato), ripasso di un argomento, scelta della lingua (Sassari)."""
    pg.goto("http://sito.test" + u)
    q = pg.locator("[data-quiz]")
    n = int(q.get_attribute("data-n"))
    # chiave di una domanda = testo + risposte (molte domande hanno lo stesso testo: per esempio la stessa frase in quattro lingue)
    tutte = pg.eval_on_selector_all("[data-dom]", "l=>l.map(x=>[x.querySelector('.dq .t').textContent+'|'+Array.from(x.querySelectorAll('.opz .r')).map(r=>r.textContent).join('|'),+x.getAttribute('data-e'),x.getAttribute('data-sez')])")
    chiave = {t: e for t, e, _ in tutte}
    sez_di = {t: s for t, _, s in tutte}
    doppie = {k for k, c in __import__("collections").Counter(x[0] for x in tutte).items() if c > 1}
    if any(len({e for k, e, _ in tutte if k == d}) > 1 for d in doppie):
        errore(f"simulatore {u}: la stessa domanda compare due volte con chiavi diverse")
    if u == "/ruolo-conducenti/sassari/":
        pg.select_option('[data-scelta="0"]', label="Francese")
    for giusto in (True, False):
        pg.click('[data-avvia="esame"]')
        viste = []
        for k in range(n):
            testo = pg.evaluate("document.querySelector('[data-q]').lastChild.textContent+'|'+Array.from(document.querySelectorAll('[data-opz] button span')).map(s=>s.textContent).join('|')")
            viste.append(testo)
            e = chiave[testo]
            n_ris = pg.locator("[data-opz] button").count()
            scelta = e if giusto else (e + 1) % n_ris
            pg.click(f"[data-opz] button >> nth={scelta}")
            fb = pg.inner_text("[data-fb]")
            if ("Giusto" in fb) != giusto:
                errore(f"simulatore {u}: esito della risposta sbagliato ({fb[:40]})")
            pg.click("[data-avanti]")
        fine = pg.locator("[data-fine]")
        g = int(fine.get_attribute("data-giuste"))
        if g != (n if giusto else 0) or int(fine.get_attribute("data-totale")) != n:
            errore(f"simulatore {u}: {g} giuste su {fine.get_attribute('data-totale')} (attese {n if giusto else 0} su {n})")
        voto = pg.inner_text("[data-fine]")
        if giusto and "Non superato" in voto or (not giusto and "Superato" in voto.replace("Non superato", "")):
            errore(f"simulatore {u}: esito finale errato: {voto[:80]}")
        if len(set(viste)) != n and not set(v for v in viste if viste.count(v) > 1) <= doppie:  # l'elenco del Ministero ripete una domanda (n. 1148 e 1214)
            errore(f"simulatore {u}: domande ripetute nella stessa prova")
        if u == "/ruolo-conducenti/sassari/":
            altre = [t for t in viste if "lingua straniera" in (sez_di.get(t) or "") and not sez_di[t].endswith("francese")]
            if altre:
                errore(f"simulatore {u}: con il francese escono domande di altre lingue ({len(altre)})")
        pg.click("text=Cambia modalità")
    # ripasso del primo argomento: tutte le sue domande
    pg.select_option("[data-sezione]", index=0)
    attese = sum(1 for _, _, s in tutte if s == tutte[0][2])
    pg.click('[data-avvia="ripasso"]')
    pos = pg.inner_text("[data-pos]")
    if not pos.endswith(f"di {attese}"):
        errore(f"simulatore {u}: il ripasso del primo argomento ha «{pos}», attese {attese} domande")


def main():
    controlla_fonti()
    controlla_banche()
    controlla_pagine()
    controlla_banche_nelle_pagine()
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
