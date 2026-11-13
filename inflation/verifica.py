"""Controlli di Inflation Calculator US·UK·DE (dati, motore, pagine, monetizzazione, browser).

Uso (dalla radice del repository):
    python3 inflation/verifica.py            # dati + motore JS = Python + pagine
    python3 inflation/verifica.py --browser  # in più Playwright (375 e 1280 px, chiaro e scuro, casi del calcolatore)
Esce con codice 1 se c'è anche un solo errore.
"""
import json
import random
import re
import subprocess
import sys
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import genera as G  # noqa: E402
import monetizzazione as MON  # noqa: E402
import motore as M  # noqa: E402
import serie  # noqa: E402

SEGNO_CHIAVE = "sd" + "_" + "live"  # prefisso delle chiavi dello strumento dei volumi (scritto spezzato per non comparire nei file)

SITO = RADICE / "sito"
ERR, AVV, OK = [], [], []
S = G.S
C = G.C


def err(x):
    ERR.append(x)


def ok(x):
    OK.append(x)


# ---------------------------------------------------------------- 1. dati
def tolleranza(c, d0, d1, mezza_unita):
    """Scarto massimo (punti percentuali) tra un tasso calcolato da indici arrotondati e quello pubblicato dall'ufficio,
    che lo calcola dagli indici non arrotondati: errore di arrotondamento dei due indici + 0,05 di arrotondamento del tasso."""
    i0, i1 = M.indice(c, *d0), M.indice(c, *d1)
    return 100 * (i1 / i0) * (mezza_unita / i0 + mezza_unita / i1) + 0.051


def dati():
    # continuità
    for k, nome in (("us", "USA CPI-U"), ("uk_cpi", "UK CPI"), ("uk_rpi", "UK RPI lungo"), ("uk_rpi87", "UK RPI 1987"), ("de_vpi", "DE VPI"),
                    ("de_west", "DE Ovest"), ("de", "DE verkettet")):
        e = serie.continuita(S[k], nome)
        ERR.extend(e)
        if not e:
            a, m = sorted(S[k]["annuale"]), sorted(S[k]["mensile"])
            ok(f"continuità {nome}: anni {a[0]}-{a[-1]}, mesi {m[0][0]}-{m[0][1]:02d} … {m[-1][0]}-{m[-1][1]:02d}, mancanti dichiarati {len(S[k].get('mancanti', {}))}")
    if set(S["us"]["mancanti"]) != {(2025, 10)}:
        err(f"USA: mesi mancanti inattesi {S['us']['mancanti']}")
    # BLS: pagina dati = API, mese per mese
    api, api_manc = serie.bls_api()
    diff = [k for k in set(api) | set(S["us"]["mensile"]) if api.get(k) != S["us"]["mensile"].get(k)]
    if diff or set(api_manc) != set(S["us"]["mancanti"]):
        err(f"BLS: pagina dati e API diverse in {sorted(diff)[:5]} / mancanti {api_manc}")
    else:
        ok(f"BLS: pagina dati = API su {len(api)} mesi; ottobre 2025 assente in entrambe ({list(api_manc.values())[0]})")
    # medie annue ricalcolate
    for k, tol_vecchi in (("us", 0.1001), ("uk_cpi", 0.1001), ("uk_rpi", 0.25), ("de_vpi", 0.1001), ("de_west", 0.1001)):
        s, n, mx = S[k], 0, 0
        for y, v in s["annuale"].items():
            ms = [s["mensile"][(y, m)] for m in range(1, 13) if (y, m) in s["mensile"]]
            if len(ms) < 11 or (len(ms) == 11 and (y, 10) not in s.get("mancanti", {})):
                continue
            d = abs(sum(ms) / len(ms) - v)
            tol = 0.0006 if (k == "us" and y >= 2007) else tol_vecchi
            n += 1
            mx = max(mx, d)
            if d > tol:
                err(f"{k} {y}: media dei mesi {sum(ms) / len(ms):.4f} ≠ media annua pubblicata {v}")
        ok(f"{k}: {n} medie annue ricalcolate dai mesi, scarto massimo {mx:.4f}")
    # valori noti
    noti = [("us", 1913, 9.9), ("us", 1970, 38.8), ("us", 1980, 82.4), ("us", 2000, 172.2), ("us", 2020, 258.811), ("us", 2024, 313.689),
            ("uk_cpi", 2015, 100.0), ("de_vpi", 2020, 100.0), ("uk_rpi87", 1987, 101.9)]
    for k, y, v in noti:
        if abs(S[k]["annuale"][y] - v) > 0.051:
            err(f"valore noto {k} {y}: {S[k]['annuale'][y]} invece di {v}")
    if abs(sum(S["uk_rpi87"]["mensile"][(1987, 1)] for _ in [0]) - 100.0) > 1e-9:
        err("RPI CHAW gennaio 1987 ≠ 100")
    if abs(S["uk_rpi"]["mensile"][(1974, 1)] - 100.0) > 1e-9:
        err("RPI CDKO gennaio 1974 ≠ 100")
    ok(f"{len(noti) + 2} valori noti (basi degli indici e medie annue BLS note) confermati")
    # calcolatore ufficiale BLS
    es = json.loads((RADICE / "dati" / "esempi_bls.json").read_text(encoding="utf-8"))["casi"]
    for c in es:
        a0, m0 = map(int, c["da"].split("-"))
        a1, m1 = map(int, c["a"].split("-"))
        r = M.calcola(C["us"], c["importo"], (a0, m0), (a1, m1))
        if c["risultato_ufficiale"] is None or abs(round(r["valore"], 2) - c["risultato_ufficiale"]) > 0.0051:
            err(f"calcolatore BLS {c}: nostro {r['valore']:.4f}")
    ok(f"{len(es)} risultati del CPI Inflation Calculator ufficiale del BLS rifatti al centesimo")
    # ONS: tassi pubblicati
    cpi_r = S["uk_cpi_rate"]
    n, mx = 0, 0
    for (a, m), v in cpi_r["mensile"].items():
        t = M.tasso_12_mesi(C["uk_cpi"], a, m)
        if t is None:
            continue
        d = abs(t * 100 - v)
        n, mx = n + 1, max(mx, d)
        if d > tolleranza(C["uk_cpi"], (a - 1, m), (a, m), 0.05):
            err(f"UK CPI {a}-{m}: tasso calcolato {t * 100:.2f} ≠ ONS {v}")
    for a, v in cpi_r["annuale"].items():
        t = M.tasso_annuo(C["uk_cpi"], a)
        if t is not None and abs(t * 100 - v) > 0.15:
            err(f"UK CPI {a}: tasso annuo calcolato {t * 100:.2f} ≠ ONS {v}")
    ok(f"UK CPI: {n} tassi a 12 mesi calcolati = ONS D7G7 (scarto massimo {mx:.2f} punti, sempre entro l'arrotondamento degli indici a una cifra)")
    rpi_r = S["uk_rpi_rate"]
    n, mx = 0, 0
    for (a, m), v in rpi_r["mensile"].items():
        t = M.tasso_12_mesi(C["uk_rpi"], a, m)
        if t is None:
            continue
        d = abs(t * 100 - v)
        n, mx = n + 1, max(mx, d)
        if d > tolleranza(C["uk_rpi"], (a - 1, m), (a, m), 0.05 if a < 1988 else 0.2):
            err(f"UK RPI {a}-{m}: tasso dal CDKO {t * 100:.2f} ≠ ONS CZBH {v}")
    ok(f"UK RPI: {n} tassi a 12 mesi dal CDKO = ONS CZBH (scarto massimo {mx:.2f} punti)")
    rapp = [S["uk_rpi"]["mensile"][k] / v for k, v in S["uk_rpi87"]["mensile"].items()]
    if max(rapp) / min(rapp) - 1 > 0.0012:
        err(f"RPI: CDKO / CHAW non costante ({min(rapp):.4f}–{max(rapp):.4f})")
    else:
        ok(f"RPI: CDKO = CHAW × {sum(rapp) / len(rapp):.4f} su {len(rapp)} mesi (stessa serie, basi diverse)")
    # Destatis
    L, T = S["de_lange"], S["de_tabelle"]
    sov_m = [k for k in T["mensile"] if k in L["mensile"]]
    sov_a = [k for k in T["annuale"] if k in L["annuale"]]
    diff = [k for k in sov_m if L["mensile"][k] != T["mensile"][k]] + [k for k in sov_a if L["annuale"][k] != T["annuale"][k]]
    if diff or not sov_m:
        err(f"Destatis: lange Reihen e tabella attuale diverse in {diff[:5]}")
    else:
        ok(f"Destatis: lange Reihen = tabella attuale su {len(sov_m)} mesi e {len(sov_a)} anni in comune")
    R = S["de_rate_pubbl"]
    n = 0
    for a, v in R["vpi_jahr"].items():
        t = M.tasso_annuo(C["de"], a)
        if a >= 1992 and t is not None:
            n += 1
            if abs(t * 100 - v) > 0.1001:
                err(f"DE {a}: tasso dal VPI {t * 100:.2f} ≠ Destatis {v}")
    for (a, m), v in R["vpi_monat"].items():
        t = M.tasso_12_mesi(C["de"], a, m)
        n += 1
        if t is None or abs(t * 100 - v) > 0.1001:
            err(f"DE {a}-{m}: tasso mensile {t} ≠ Destatis {v}")
    for a, v in R["west_jahr"].items():
        w = S["de_west"]["annuale"]
        if a - 1 in w and a in w:
            n += 1
            if abs((w[a] / w[a - 1] - 1) * 100 - v) > 0.1001:
                err(f"DE Ovest {a}: tasso {(w[a] / w[a - 1] - 1) * 100:.2f} ≠ Destatis {v}")
    ok(f"Destatis: {n} tassi pubblicati (annui VPI e Ovest, mensili) rifatti dagli indici entro 0,1 punti")
    k = S["de"]["fattore"]
    if abs(S["de"]["annuale"][1990] - round(S["de_west"]["annuale"][1990] * k, 3)) > 1e-9 or S["de"]["annuale"][1991] != S["de_vpi"]["annuale"][1991]:
        err("DE: raccordo 1991 non applicato come descritto")
    # fonti e frasi
    for fid, f in G.FONTI.items():
        if fid.startswith("_"):
            continue
        if f.get("http") != 200:
            err(f"fonte {fid}: HTTP {f.get('http')}")
        if f.get("trovate") and not all(f["trovate"].values()):
            err(f"fonte {fid}: frase non più presente")
        if fid.startswith(("ons", "destatis", "bls")) and fid != "bls_calc" and not f.get("licenza"):
            err(f"fonte {fid}: licenza non registrata")
        if not f.get("letto_il"):
            err(f"fonte {fid}: senza data di lettura")


# ---------------------------------------------------------------- 2. motore JS = Python
def motore():
    js_file = next((SITO / "assets").glob("app.*.js"))
    js = js_file.read_text(encoding="utf-8")
    motore_js = js[:js.index("(function(){")]
    rnd = random.Random(7)
    casi = []
    for k in C:
        c = C[k]
        anni = list(range(c["a0"], c["a0"] + len(c["a"])))
        for _ in range(1500):
            def data():
                if rnd.random() < 0.5:
                    return [rnd.choice(anni), None]
                i = rnd.randrange(len(c["m"]))
                return [c["m0"][0] + (c["m0"][1] - 1 + i) // 12, (c["m0"][1] - 1 + i) % 12 + 1]
            casi.append([k, round(rnd.uniform(0, 100000), 2), data(), data(), (rnd.random() < 0.5) if k == "de" else None])
    casi += [["us", 100, [2025, 10], [2026, 10], None], ["us", 100, [1913, None], [1913, None], None], ["de", 100, [1990, None], [2002, None], True],
             ["de", 100, [2005, None], [1980, None], False], ["uk_rpi", 1, [1800, None], [2026, 9], None]]
    prog = motore_js + "\nvar C=" + json.dumps(C) + ";var K=" + json.dumps(casi) + (
        ";var o=K.map(function(x){var r=calcola(C[x[0]],x[1],[x[2][0],x[2][1]||undefined],[x[3][0],x[3][1]||undefined],x[4]);return r?r.valore:null;});"
        "process.stdout.write(JSON.stringify(o));")
    p = subprocess.run(["node", "-"], input=prog, capture_output=True, text=True)
    if p.returncode:
        err("node: " + p.stderr[:300])
        return
    js_out = json.loads(p.stdout)
    diversi = 0
    for (k, imp, da, a, v), j in zip(casi, js_out):
        r = M.calcola(C[k], imp, tuple(da), tuple(a), v)
        py = r["valore"] if r else None
        if (py is None) != (j is None) or (py is not None and abs(py - j) > 1e-6 * max(1, abs(py))):
            diversi += 1
            if diversi < 4:
                err(f"JS ≠ Python: {k} {imp} {da}→{a} {v}: {j} / {py}")
        if py is not None and py < 0:
            err("valore negativo")
    if not diversi:
        ok(f"motore JS pubblicato ({js_file.name}) = Python su {len(casi)} casi (ottobre 2025 USA = nessun risultato in entrambi)")


# ---------------------------------------------------------------- 3. pagine
PAROLE_EN = re.compile(r"\b(the|and|with|from|year|price|prices|which|this|that|calculator)\b", re.I)
_NOMI = [x[::-1] for x in ("edualc", "ciporhtna", "tpgtahc", "ianepo", "inimeg", "amall", "supo", "tennos", "ukiah")]  # nomi di modelli AI da non pubblicare (scritti al contrario: questo file non li contiene)
MODELLI = re.compile(r"\b(" + "|".join(_NOMI) + r"|gpt-?\d)\b", re.I)


def testo(html_):
    return unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S)))


def pagine():
    files = sorted(SITO.rglob("*.html"))
    canon, noindex = {}, []
    tutti_link = set()
    for f in files:
        rel = str(f.relative_to(SITO))
        t = f.read_text(encoding="utf-8")
        percorso = "" if rel == "index.html" else rel[:-len("index.html")] if rel.endswith("index.html") else rel
        tit = re.search(r"<title>(.*?)</title>", t).group(1)
        des = re.search(r'<meta name="description" content="([^"]*)"', t).group(1)
        if re.search(r'name="robots" content="noindex"', t):
            noindex.append(rel)
        else:
            m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
            if not m or m.group(1) != f"{G.URL_SITO}/{percorso}":
                err(f"{rel}: canonical errato")
            canon[m.group(1)] = rel
            if not (20 <= len(unescape(tit)) <= 70):
                err(f"{rel}: titolo di {len(unescape(tit))} caratteri")
            if not (70 <= len(unescape(des)) <= 165):
                err(f"{rel}: descrizione di {len(unescape(des))} caratteri")
        if t.count("<h1") != 1:
            err(f"{rel}: {t.count('<h1')} h1")
        if "gc.zgo.at/count.js" not in t:
            err(f"{rel}: manca GoatCounter")
        if "{" in testo(t).replace("{}", "") and re.search(r"\{[a-z_]+\}", testo(t)):
            err(f"{rel}: segnaposto non sostituito {re.search(r'{[a-z_]+}', testo(t)).group(0)}")
        if MODELLI.search(t):
            err(f"{rel}: nome di modello AI ({MODELLI.search(t).group(0)})")
        if SEGNO_CHIAVE in t:
            err(f"{rel}: chiave nel sito")
        for m in re.finditer(r'href="(/[^"#?]*)', t):
            tutti_link.add((rel, m.group(1)))
        # JSON-LD
        lds = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        for ld in lds:
            if ld.get("@type") == "FAQPage":
                vis = re.findall(r'<div class="faq"><h3>(.*?)</h3><p>(.*?)</p></div>', t, re.S)
                if len(vis) != len(ld["mainEntity"]):
                    err(f"{rel}: FAQ visibili {len(vis)} ≠ JSON-LD {len(ld['mainEntity'])}")
                for (q, a), e in zip(vis, ld["mainEntity"]):
                    if unescape(q) != e["name"] or re.sub(r"\s+", " ", testo(a)).strip() != re.sub(r"\s+", " ", e["acceptedAnswer"]["text"]).strip():
                        err(f"{rel}: FAQ JSON-LD diversa dal testo visibile ({e['name'][:40]})")
        # lingua tedesca
        if rel.startswith("de/"):
            if 'lang="de-DE"' not in t:
                err(f"{rel}: lang non tedesco")
            main = t[t.index("<main"):t.index("</main>")]
            main = re.sub(r'<section class="fonti-box".*?</section>', "", main, flags=re.S)
            main = re.sub(r'<ul class="griglia">.*?</ul>', "", main, flags=re.S)
            main = re.sub(r'<script type="application/json".*?</script>', "", main, flags=re.S)
            parole = PAROLE_EN.findall(testo(main))
            if parole:
                err(f"{rel}: parole inglesi nel testo tedesco: {sorted(set(parole))}")
            for sbagliata in ("Jahresdurchschnit ", "Inflationrate", "Verbraucherpreisindexes", " dass dass"):
                if sbagliata in testo(main):
                    err(f"{rel}: '{sbagliata}'")
    # link interni
    rotti = set()
    for rel, l in tutti_link:
        p = SITO / l.lstrip("/")
        if not ((p / "index.html").exists() if l.endswith("/") else p.exists()):
            rotti.add(f"{rel} -> {l}")
    for r in sorted(rotti)[:10]:
        err(f"link rotto {r}")
    # sitemap
    sm = re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8"))
    if set(sm) != set(canon) or len(sm) != len(set(sm)):
        err(f"sitemap ({len(sm)}) ≠ pagine con canonical ({len(canon)})")
    if noindex != ["404.html"]:
        err(f"pagine noindex inattese: {noindex}")
    attese = ["", "uk/", "uk/rpi-calculator/", "uk/inflation-rate-by-year/", "de/inflationsrechner/", "de/inflationsrate-deutschland/", "us/inflation-rate-by-year/"]
    attese += [f"us/{y}-dollars-today/" for y in G.ANNI_US] + [f"us/{x}-dollars-in-{y}/" for x in G.IMPORTI_PAGINA for y in G.DECENNI_IMPORTO]
    mancano = [a for a in attese if f"{G.URL_SITO}/{a}" not in canon]
    if mancano:
        err(f"pagine mancanti {mancano[:5]}")
    ok(f"{len(files)} file HTML: {len(canon)} con canonical = sitemap, solo 404 noindex; {len(tutti_link)} link interni controllati, titoli, descrizioni, h1, JSON-LD")
    # file accessori
    for nome, cerca in (("robots.txt", f"Sitemap: {G.URL_SITO}/sitemap.xml"), (f"{G.CHIAVE_INDEXNOW}.txt", G.CHIAVE_INDEXNOW), ("netlify.toml", 'ignore = "git diff --quiet'),
                        ("ads.txt", "google.com, pub-")):
        if cerca not in (SITO / nome).read_text(encoding="utf-8"):
            err(f"{nome}: manca «{cerca}»")
    if not (SITO / "assets" / "og.png").exists():
        err("og.png assente")
    # FAQ da ricerche vere
    dom = json.loads((RADICE / "dati" / "domanda.json").read_text(encoding="utf-8"))
    vol = {}
    for r in dom["richieste"]:
        vol[(r["frase"].lower(), r["paese"])] = max(vol.get((r["frase"].lower(), r["paese"]), 0), r["volume"] or 0)
        for s in r["simili"]:
            vol[(s["frase"].lower(), r["paese"])] = max(vol.get((s["frase"].lower(), r["paese"]), 0), s["volume"] or 0)
    faq = json.loads((RADICE / "dati" / "faq_generate.json").read_text(encoding="utf-8"))["faq"]
    for x in faq:
        if vol.get((x["ricerca"].lower(), x["paese"]), 0) <= 0:
            err(f"FAQ «{x['domanda']}»: la ricerca «{x['ricerca']}» non ha volume misurato")
    ok(f"{len(faq)} FAQ, ognuna da una ricerca con volume misurato ({', '.join(sorted({x['ricerca'] for x in faq})[:4])}…)")
    # numeri stampati = motore
    for y in (1913, 1950, 1970, 1980, 2025):
        t = (SITO / "us" / f"{y}-dollars-today" / "index.html").read_text(encoding="utf-8")
        atteso = G.soldi(G.vale_oggi("us", y), "USD")
        if f'<span class="big">{atteso}</span>' not in t:
            err(f"pagina {y}: valore di $1 non uguale al motore ({atteso})")
    for x, y in ((100, 1970), (1000, 1980)):
        t = (SITO / "us" / f"{x}-dollars-in-{y}" / "index.html").read_text(encoding="utf-8")
        if G.soldi(x * G.vale_oggi("us", y), "USD") not in t:
            err(f"pagina ${x} {y}: valore non uguale al motore")
    for rel, k, imp, da, a, v in (("index.html", "us", 100, (1970, None), G.ULT["us"], None), ("uk/index.html", "uk_cpi", 100, (1990, None), G.ULT["uk_cpi"], None),
                                  ("de/inflationsrechner/index.html", "de", 100, (2002, None), G.ULT["de"], False)):
        t = (SITO / rel).read_text(encoding="utf-8")
        m = re.search(r"<b data-valore>([^<]+)</b>", t)
        r = M.calcola(C[k], imp, da, a, v)
        valuta = "EUR" if k == "de" else ("GBP" if k.startswith("uk") else "USD")
        if not m or unescape(m.group(1)) != G.soldi(r["valore"], valuta):
            err(f"{rel}: risultato statico {m and m.group(1)} ≠ motore {r['valore']:.2f}")
    ok("numeri stampati (pagine anno, pagine importo, risultato iniziale dei tre calcolatori) = motore")
    # monetizzazione
    e, info = MON.controlla_sito(G.SITO_ID, SITO)
    ERR.extend(e)
    if not e:
        ok(MON.riepilogo(G.SITO_ID, info, e))
    # chiave e nomi di modello nei sorgenti
    for f in RADICE.rglob("*"):
        if f.is_file() and f.suffix in (".py", ".js", ".json", ".md", ".html", ".csv", ".txt", ".toml") and "cache" not in f.parts:
            t = f.read_text(encoding="utf-8", errors="replace")
            if SEGNO_CHIAVE in t:
                err(f"{f}: chiave nel repository")
            if f.suffix != ".csv" and MODELLI.search(t):
                err(f"{f.relative_to(RADICE)}: nome di modello AI")


# ---------------------------------------------------------------- 4. browser
def browser():
    lu, uk, de = G.ULT["us"], G.ULT["uk_cpi"], G.ULT["de"]
    casi = [
        {"descr": "US 100 1970 → ultimo mese", "pagina": "/", "importo_testo": "100", "da": [1970, None], "a": list(lu), "k": "us", "foto": "us"},
        {"descr": "US 1,500 gennaio 1980 → 2000 media", "pagina": "/", "importo_testo": "1,500", "da": [1980, 1], "a": [2000, None], "k": "us"},
        {"descr": "US BLS ufficiale 1000 gen 1980 → set 2025", "pagina": "/", "importo_testo": "1000", "da": [1980, 1], "a": [2025, 9], "k": "us", "ufficiale": 4174.81},
        {"descr": "UK CPI 250 2005 → ultimo", "pagina": "/uk/", "importo_testo": "250", "serie": "uk_cpi", "da": [2005, None], "a": list(uk), "k": "uk_cpi", "foto": "uk"},
        {"descr": "UK 1 1950 → ultimo (passa a RPI)", "pagina": "/uk/", "importo_testo": "1", "serie": "uk_cpi", "da": [1950, None], "a": list(uk), "k": "uk_rpi",
         "serie_finale": "uk_rpi"},
        {"descr": "RPI 1000 2000 → ultimo", "pagina": "/uk/rpi-calculator/", "importo_testo": "1000", "da": [2000, None], "a": list(G.ULT["uk_rpi"]), "k": "uk_rpi"},
        {"descr": "DE 1.000 DM 1980 → ultimo", "pagina": "/de/inflationsrechner/", "importo_testo": "1.000", "da": [1980, None], "a": list(de), "k": "de", "valuta": "dm",
         "de": True, "dm": True, "foto": "de"},
        {"descr": "DE 50 € 2010 → 2020", "pagina": "/de/inflationsrechner/", "importo_testo": "50", "da": [2010, None], "a": [2020, None], "k": "de", "de": True, "dm": False},
        {"descr": "DE 100 € 1995 → ultimo", "pagina": "/de/inflationsrechner/", "importo_testo": "100", "da": [1995, None], "a": list(de), "k": "de", "valuta": "eur",
         "de": True, "dm": False},
    ]
    for c in casi:
        imp = float(c["importo_testo"].replace(",", "").replace(".", "")) if c.get("de") else float(c["importo_testo"].replace(",", ""))
        r = M.calcola(C[c["k"]], imp, tuple(c["da"]), tuple(c["a"]), c.get("dm"))
        c["atteso"] = round(r["valore"], 2)
        if c.get("ufficiale") and abs(c["atteso"] - c["ufficiale"]) > 0.005:
            err(f"caso {c['descr']}: motore {c['atteso']} ≠ BLS {c['ufficiale']}")
    link = round(M.calcola(C["us"], 250, (1985, None), (2000, None))["valore"], 2)
    env = {"CASI_CALC": json.dumps(casi), "ATTESO_LINK": str(link), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    import os
    env = dict(os.environ, **env)
    p = subprocess.run(["node", str(RADICE / "verifica_browser.js")], capture_output=True, text=True, env=env, timeout=900)
    try:
        out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        err("browser: " + (p.stderr or p.stdout)[-400:])
        return
    for x in out["problemi"]:
        err("browser: " + x)
    if not out["problemi"]:
        ok(f"browser: {out['viste']} viste (11 pagine × 375/1280 px × chiaro/scuro) senza scorrimento orizzontale, errori JS o testo < 11 px; "
           f"{out['casi']} casi del calcolatore × 2 larghezze uguali al motore (anche 1000 $ gen 1980 → set 2025 = 4.174,81 del BLS), cambio CPI→RPI, link condiviso, tema")


def main():
    dati()
    motore()
    pagine()
    if "--browser" in sys.argv:
        browser()
    for x in OK:
        print("ok  ", x)
    for x in AVV:
        print("AVV ", x)
    for x in ERR:
        print("ERR ", x)
    print(f"\n{len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
