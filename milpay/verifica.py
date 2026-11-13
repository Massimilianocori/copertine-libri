"""Controlli di Military Pay Chart. Uso: python3 milpay/verifica.py [--browser]

Dati: tabella ufficiale (conteggi, trattini, ordine, tetti, confronto con il 2025: genera.controlla_tabella), fonti lette.
Pagine: ogni cella delle tabelle pubblicate = dato grezzo; dati del calcolatore = dato grezzo; JS = Python su tutte le
combinazioni; link interni e ancore; sitemap = pagine con canonical; noindex fuori dalla sitemap; JSON-LD FAQPage = FAQ
visibili e ogni FAQ nata da una ricerca misurata; titoli, descrizioni, un h1; contatore, AdSense, avviso; file accessori;
nessun nome di modelli AI, nessuna chiave, nessuna promessa sull'indennità di alloggio, nessun invito ad arruolarsi.

Aggiunti dalla revisione indipendente del 13/11/2026 (non dipendono dai dati del costruttore):
- impronta delle 616 celle confrontate a occhio con le immagini del Federal Register (se i dati cambiano, vanno riguardati);
- 37 casi scelti a mano e letti sulle immagini (primi anni, trattini, soglie "2 or less"/"Over 2", tetti) provati sul JS e sulle pagine;
- tetto O-7…O-10 = 18.999,90 $ (tabella, Schedule 5, Air Force); la cifra della nota stampata (18.899,90) solo dove si spiega la differenza;
- 2026 = tabella di legge del 1° aprile 2025 × 1,038 su tutte le righe (in genera.controlla_tabella);
- modulo delle correzioni senza campi per dati personali e pagina privacy coerente;
- pagina 2027: piano del Presidente del 26/8/2026 citato alla lettera, nessuna frase che dia la cifra per approvata dal Congresso.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
import genera as G  # noqa: E402

MON = G.MON
errori, avvisi = [], []


# impronte (SHA-256, primi 16 caratteri) di parole che non devono comparire: nomi di modelli e servizi di IA e il nome del titolare.
# Si confrontano le impronte per non scrivere le parole stesse in questo file.
IMPRONTE_VIETATE = {'7d3194f79e645c42', '3ea125d0bff386e6', '053ea4804ef1bb33', 'c70eca6b0f88f44d', '5d72436256ada538', '60965168ce762e94',
                    'c857d09db23e6822', 'fc5a1047f5919892', '32119eab4ae12e0d', '5e9286da8261a15d'}


def parole_vietate(t):
    return [w for w in set(re.findall(r"[a-z0-9]+", t.lower())) if hashlib.sha256(w.encode()).hexdigest()[:16] in IMPRONTE_VIETATE]


# Impronta di P["tabelle"] nel giorno in cui tutte le 616 celle sono state confrontate a occhio con le sei immagini dello Schedule 8.
TABELLE_VISTE = "a4df24e76111a9677c09adb8591b3725f37fc9012d9feb8472c5ce3e65871a7d"

# Casi letti a mano sulle immagini del Federal Register: (grado, colonna, mensile o None se la tabella ha un trattino,
# al limite mensile?, prossimo scatto (colonna, mensile) o None). Colonne: 0 = "2 or less", 1 = "Over 2", 2 = "Over 3", 3 = "Over 4",
# 4 = "Over 6" … 10 = "Over 18", 11 = "Over 20" … 21 = "Over 40".
CASI_MANO = [
    ("e-1", 0, 2407.20, False, None), ("e-1-under-4-months", 0, 2225.70, False, None), ("e-1-under-4-months", 1, None, False, None),
    ("e-2", 0, 2697.90, False, None), ("e-3", 0, 2836.80, False, (1, 3015.00)), ("e-3", 1, 3015.00, False, (2, 3198.00)),
    ("e-4", 0, 3142.20, False, (1, 3303.00)), ("e-4", 1, 3303.00, False, (2, 3482.40)), ("e-4", 4, 3815.40, False, None),
    ("e-5", 3, 3946.80, False, (4, 4110.00)), ("e-5", 7, 4421.70, False, None), ("e-6", 0, 3401.10, False, (1, 3743.10)),
    ("e-7", 11, 6245.70, False, (12, 6475.20)), ("e-8", 4, None, False, None), ("e-8", 5, 5656.50, False, (6, 5907.00)),
    ("e-9", 5, None, False, None), ("e-9", 6, 6910.20, False, (7, 7066.50)), ("e-9", 21, 10729.20, False, None),
    ("w-1", 0, 4056.60, False, (1, 4493.70)), ("w-2", 12, 7591.50, False, (13, 7714.20)), ("w-5", 10, None, False, None),
    ("w-5", 11, 10169.70, False, (12, 10685.70)), ("w-5", 15, 11495.10, False, (16, 12070.80)), ("o-1", 1, 4320.00, False, (2, 5222.40)),
    ("o-1e", 2, None, False, None), ("o-1e", 3, 5222.40, False, (4, 5576.70)), ("o-2", 4, 6617.70, False, None),
    ("o-3", 8, 9004.20, False, None), ("o-3e", 10, 9609.60, False, None), ("o-4", 0, 6294.60, False, (1, 7286.40)),
    ("o-6", 15, 15188.70, False, (16, 15408.30)), ("o-6", 16, 15408.30, True, None), ("o-7", 16, 17242.20, False, None),
    ("o-8", 11, 18598.20, False, (12, 18999.90)), ("o-8", 12, 18999.90, True, None), ("o-9", 10, None, False, None),
    ("o-10", 11, 18999.90, True, None),
]


def err(x):
    errori.append(x)


def testo(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def pagine():
    return sorted(SITO.rglob("*.html"))


def percorso(f):
    r = str(f.relative_to(SITO))
    return "" if r == "index.html" else (r[:-len("index.html")] if r.endswith("index.html") else r)


def tabelle_html(html):
    return re.findall(r"<table[^>]*>(.*?)</table>", html, re.S)


def righe_html(tab):
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tab, re.S):
        celle = [testo(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
        out.append(celle)
    return out


def controlla_dati():
    stat = G.controlla_tabella()
    G.controlla_faq_grado()
    for fid, es in G.ESITI.items():
        if es.get("http") != 200:
            err(f"fonte {fid}: HTTP {es.get('http')}")
        for c, ok in es.get("trovate", {}).items():
            if not ok:
                err(f"fonte {fid}: frase non trovata «{c}»")
    if G.ESITI.get("bls_eci", {}).get("api") != "REQUEST_SUCCEEDED":
        avvisi.append("API BLS non ha risposto all'ultima lettura (limite giornaliero?): valori ECI da dati/storico.json")
    return stat


def controlla_celle():
    """Ogni cella delle tabelle grandi della home e delle tabelle di grado = dato grezzo."""
    home = (SITO / "index.html").read_text(encoding="utf-8")
    tabs = [t for t in tabelle_html(home) if 'class="dati grande"' in home and "<caption>" in t]
    n = 0
    viste = set()
    for t in tabelle_html(home):
        righe = righe_html(t)
        if not righe or righe[0][:2] != ["Grade", "2 or less"]:
            continue
        if righe[0][1:] != G.COL:
            err(f"intestazione della tabella diversa dalle colonne ufficiali: {righe[0]}")
        for r in righe[1:]:
            k = "E-1<4" if r[0] == "E-1 <4 mo." else r[0]
            viste.add(k)
            dati = G.riga(k)
            for i, (cel, v) in enumerate(zip(r[1:], dati)):
                atteso = "–" if v is None else G.soldi(v)
                n += 1
                if cel != atteso:
                    err(f"home {k} {G.COL[i]}: pagina «{cel}» dato «{atteso}»")
            if len(r) != 23:
                err(f"home {k}: {len(r) - 1} celle")
    if n != 616 or len(viste) != 28:
        err(f"home: {n} celle in {len(viste)} righe (attese 616 in 28)")
    # pagine di grado
    m = 0
    for slug, nome, cat, k in G.GRADI:
        html = (SITO / slug / "index.html").read_text(encoding="utf-8")
        t = next((t for t in tabelle_html(html) if "Years of service" in t), None)
        if not t:
            err(f"/{slug}/: tabella del grado assente")
            continue
        righe = righe_html(t)[1:]
        dati = G.riga(k)
        attese = [(G.COL[i], dati[i]) for i in range(22) if dati[i] is not None]
        if k == "E-1":
            attese.insert(0, ("Under 4 months", G.riga("E-1<4")[0]))
        if len(righe) != len(attese):
            err(f"/{slug}/: {len(righe)} righe, attese {len(attese)}")
        for r, (col, v) in zip(righe, attese):
            p = G.pagabile(slug, v)
            mese = r[1].replace(" cap", "")
            if r[0] != col or mese != G.soldi(p) or r[2] != G.soldi(p * 12):
                err(f"/{slug}/ {col}: pagina {r[:3]} attesi {G.soldi(p)} e {G.soldi(p * 12)}")
            if (" cap" in r[1]) != (G.al_tetto(slug, v) is not None):
                err(f"/{slug}/ {col}: segno del tetto sbagliato")
            m += 1
    return n, m


def controlla_calcolatore():
    html = (SITO / "calculator" / "index.html").read_text(encoding="utf-8")
    d = json.loads(re.search(r'<script type="application/json" id="dati-paga">(.*?)</script>', html, re.S).group(1))
    if d != json.loads(json.dumps(G.dati_js())):
        err("dati del calcolatore diversi dal dato grezzo")
    js = next((SITO / "assets").glob("app.*.js"))
    casi = [(s, k, c) for s, _, _, k in G.GRADI + [G.E1_4] for c in range(22)]
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(d)};const C={json.dumps([[s, c] for s, _, c in casi])};"
            "console.log(JSON.stringify(C.map(x=>m.calcola(D,x[0],x[1]))));")
    out = json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)
    diversi = 0
    for (s, k, c), r in zip(casi, out):
        p = G.calcola(s, k, c)
        if (p is None) != (r is None):
            diversi += 1
            continue
        if p is None:
            continue
        pr_js = r["prossimo"]
        if (abs(p["mese"] - r["mese"]) > 1e-6 or abs(p["anno"] - r["anno"]) > 1e-6 or (p["tetto"] is None) != (r["tetto"] is None)
                or (p["prossimo"] is None) != (pr_js is None) or (pr_js and (pr_js["col"] != p["prossimo"]["col"] or abs(pr_js["piu"] - p["prossimo"]["piu"]) > 1e-6))):
            diversi += 1
            err(f"calcolatore JS ≠ Python: {s} {G.COL[c]} JS {r} PY {p}")
    if diversi:
        err(f"calcolatore: {diversi} combinazioni diverse")
    # casi letti a mano sulle immagini ufficiali: il JS deve dare proprio quelle cifre (non il confronto con il Python del costruttore)
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(d)};const C={json.dumps([[g, c] for g, c, *_ in CASI_MANO])};"
            "console.log(JSON.stringify(C.map(x=>m.calcola(D,x[0],x[1]))));")
    out = json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)
    for (g, c, mese, limite, pross), r in zip(CASI_MANO, out):
        dove = f"caso a mano {g} {G.COL[c]}"
        if mese is None:
            if r is not None:
                err(f"{dove}: la tabella ha un trattino, il calcolatore dà {r}")
            continue
        if r is None:
            err(f"{dove}: atteso {mese}, il calcolatore non dà niente")
            continue
        if abs(r["mese"] - mese) > 1e-6 or abs(r["anno"] - round(mese * 12, 2)) > 1e-6 or abs(r["tabella"] - mese) > 1e-6:
            err(f"{dove}: attesi {mese} al mese e {round(mese * 12, 2)} l'anno, calcolatore {r}")
        if (r["tetto"] is not None) != limite:
            err(f"{dove}: segno del limite mensile sbagliato ({r['tetto']})")
        if (r["prossimo"] is None) != (pross is None) or (pross and (r["prossimo"]["col"] != pross[0] or abs(r["prossimo"]["mese"] - pross[1]) > 1e-6
                                                                    or abs(r["prossimo"]["piu"] - round(pross[1] - mese, 2)) > 1e-6)):
            err(f"{dove}: prossimo scatto atteso {pross}, calcolatore {r['prossimo']}")
        # la stessa cifra deve stare nella pagina del grado, nella riga di quella colonna
        pag = "e-1" if g == "e-1-under-4-months" else g
        html_g = (SITO / pag / "index.html").read_text(encoding="utf-8")
        t = next((t for t in tabelle_html(html_g) if "Years of service" in t), "")
        etich = "Under 4 months" if g == "e-1-under-4-months" else G.COL[c]
        riga_p = next((x for x in righe_html(t) if x and x[0] == etich), None)
        if not riga_p or riga_p[1].replace(" cap", "") != G.soldi(mese) or riga_p[2] != G.soldi(mese * 12) or (" cap" in riga_p[1]) != limite:
            err(f"{dove}: nella pagina /{pag}/ la riga è {riga_p}")
    return len(casi)


def controlla_revisione():
    """Controlli aggiunti dalla revisione indipendente: non usano il calcolo del costruttore come riferimento."""
    imp = hashlib.sha256(json.dumps(G.P["tabelle"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if imp != TABELLE_VISTE:
        err("le tabelle in dati/paga_2026.json non sono più quelle confrontate a occhio con le immagini ufficiali: riguardarle e aggiornare TABELLE_VISTE")
    # tetti
    if G.TETTO_II != 18999.90 or G.TETTO_V != 15408.30 or G.mensile_es(225700) != 18808.20 or G.mensile_es(221900) != 18491.70:
        err(f"tetti: livello II {G.TETTO_II}, livello V {G.TETTO_V} (attesi 18999.90 e 15408.30; il metodo deve ridare 18808.20 per il 2025 e 18491.70 per il 2024)")
    nota = G.soldi(G.TETTO_II_NOTA)
    for f in pagine():
        html = f.read_text(encoding="utf-8")
        nome = "/" + percorso(f)
        tv = testo(html)
        if G.TETTO_II_NOTA != G.TETTO_II:
            for m in re.finditer(re.escape(nota), tv):
                if "footnote" not in tv[max(0, m.start() - 160):m.start()].lower():
                    err(f"{nome}: {nota} (cifra della nota stampata) usata fuori dalla frase che spiega la differenza con la tabella")
        # nessun campo per dati personali, nessun modulo oltre al calcolatore e alle correzioni
        for form in re.findall(r"<form\b.*?</form>", html, re.S):
            nomi = set(re.findall(r'name="([^"]+)"', form))
            if "data-netlify" in form:
                if nomi != {"corrections", "form-name", "bot-field", "page", "message", "source"} or "data-correzioni" not in form:
                    err(f"{nome}: il modulo delle correzioni ha campi diversi da pagina, messaggio e fonte: {sorted(nomi)}")
            elif nomi != {"g", "y"}:
                err(f"{nome}: modulo inatteso con i campi {sorted(nomi)}")
        if re.search(r'type="(email|tel|password)"|autocomplete="(email|name|tel)"|name="(email|name|phone|consent)"', html):
            err(f"{nome}: campo per dati personali")
        if re.search(r"\b(newsletter|subscribe|sign up)\b", re.sub(r"no accounts, newsletters or comments", "", tv), re.I):
            err(f"{nome}: iscrizioni o newsletter")
        if re.search(r"\b(you should|we recommend|our advice|best time to (join|enlist|retire)|worth joining|sign-?on bonus)\b", tv, re.I):
            err(f"{nome}: frase di consiglio o di reclutamento")
    cc = testo((SITO / "how-we-check" / "index.html").read_text(encoding="utf-8"))
    pr = testo((SITO / "privacy" / "index.html").read_text(encoding="utf-8"))
    if "does not ask for your name or email address" not in pr or "Netlify Forms" not in pr or "only if you give it" in pr:
        err("/privacy/: non descrive il modulo com'è (pagina, messaggio, fonte; niente nome né email)")
    if "do not include your name, email address or other personal details" not in cc:
        err("/how-we-check/: manca l'invito a non scrivere dati personali nel modulo")
    # pagina O-10: la cifra pagata è quella della tabella
    o10 = testo((SITO / "o-10" / "index.html").read_text(encoding="utf-8"))
    if "$18,999.90" not in o10 or "$227,998.80" not in o10:
        err("/o-10/: mancano 18.999,90 al mese e 227.998,80 l'anno")
    # pagina 2027
    p27 = testo((SITO / "2027-pay-raise" / "index.html").read_text(encoding="utf-8"))
    for frase in ("7.0 percent for grades E1 to E5, 6.0 percent for grades E6 to O3, and 5.0 percent for grades O4 and above", "August 26, 2026",
                  "House Document 119-189", "shall take effect on January 1, 2027", "3.6%", "A budget is a request to Congress, not a pay table",
                  "Congress can set different rates by law", "not published yet"):
        if frase not in p27:
            err(f"/2027-pay-raise/: manca «{frase}»")
    for vietata in (r"signed into law", r"\b(has|have|was|were) (been )?(enacted|approved|passed)\b", r"\bCongress (has )?(approved|passed|enacted)\b", r"\bwill (get|receive|be paid)\b", r"\bguaranteed\b",
                    r"2027 pay chart:?\s*\$"):
        if re.search(vietata, p27, re.I):
            err(f"/2027-pay-raise/: frase che dà l'aumento per approvato o promesso ({vietata})")
    pl = G.ESITI.get("plaw119", {})
    if pl.get("ndaa_2027"):
        err(f"è stata pubblicata una legge sulla difesa per il 2027: {pl['ndaa_2027']} — riscrivere /2027-pay-raise/")
    if not pl.get("ultima_legge"):
        avvisi.append("elenco delle leggi pubblicate (govinfo) non letto: la pagina 2027 non dice fino a quale legge è stato controllato")
    elif pl["ultima_legge"]["numero"] not in p27:
        err("/2027-pay-raise/: non dice fino a quale legge pubblicata è stato controllato")
    # storico: la spiegazione delle righe E-1…E-5 con la sua fonte
    st = testo((SITO / "pay-raise-history" / "index.html").read_text(encoding="utf-8"))
    for frase in ("effective April 1, 2025", "Public Law 118-159", "3.8% in every row"):
        if frase not in st:
            err(f"/pay-raise-history/: manca «{frase}»")
    # titoli e descrizioni unici
    visti_t, visti_d = {}, {}
    for f in pagine():
        if f.name == "404.html":
            continue
        html = f.read_text(encoding="utf-8")
        for visti, rx in ((visti_t, r"<title>(.*?)</title>"), (visti_d, r'<meta name="description" content="(.*?)"')):
            x = re.search(rx, html).group(1)
            if x in visti:
                err(f"/{percorso(f)}: stesso titolo o descrizione di /{visti[x]}")
            visti[x] = percorso(f)


def controlla_pagine():
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>(.*?)</loc>", sitemap)
    canon = set()
    esistenti = {percorso(f) for f in pagine()}
    vietate = [r"\bBAH\b", r"housing allowance (is )?coming", r"coming soon", r"\benlist (now|today)\b", r"\bjoin the (army|navy|air force|marines)\b", r"talk to a recruiter",
               "_".join(["sd", "live"])]
    for f in pagine():
        html = f.read_text(encoding="utf-8")
        p = percorso(f)
        nome = "/" + p
        tv = testo(html)
        if parole_vietate(html):
            err(f"{nome}: nome di modello AI o dato personale")
        for v in vietate:
            if re.search(v, html, re.I):
                err(f"{nome}: testo vietato «{v}»")
        if html.count("<h1") != 1:
            err(f"{nome}: {html.count('<h1')} h1")
        tit = re.search(r"<title>(.*?)</title>", html).group(1)
        des = re.search(r'<meta name="description" content="(.*?)"', html).group(1)
        if f.name != "404.html" and not (10 <= len(unescape(tit)) <= 65):
            err(f"{nome}: titolo di {len(unescape(tit))} caratteri")
        if f.name != "404.html" and not (70 <= len(unescape(des)) <= 165):
            err(f"{nome}: descrizione di {len(unescape(des))} caratteri")
        if G.GOATCOUNTER_URL not in html:
            err(f"{nome}: contatore assente")
        if "not affiliated with the Department of Defense" not in html:
            err(f"{nome}: avviso di non affiliazione assente")
        if "finance office" not in html:
            err(f"{nome}: invito a verificare con l'ufficio finanziario assente")
        ext = re.findall(r'<script[^>]+src="(https?://[^"]+)"', html)
        for u in ext:
            if not (u.startswith("https://pagead2.googlesyndication.com/") or u.startswith("https://gc.zgo.at/")):
                err(f"{nome}: script esterno non ammesso {u}")
        c = re.search(r'<link rel="canonical" href="(.*?)"', html)
        noindex = '<meta name="robots" content="noindex' in html
        if c:
            canon.add(c.group(1))
            if c.group(1) != f"{G.URL_SITO}/{p}":
                err(f"{nome}: canonical {c.group(1)}")
            if noindex:
                err(f"{nome}: canonical e noindex insieme")
        elif not noindex:
            err(f"{nome}: né canonical né noindex")
        # link interni e ancore
        ids = set(re.findall(r'id="([^"]+)"', html))
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith("#"):
                if href[1:] not in ids:
                    err(f"{nome}: ancora {href} assente")
            elif href.startswith("/") and not href.startswith("//"):
                path, _, anc = href.partition("#")
                path = path.split("?")[0]
                if path.startswith("/assets/"):
                    if not (SITO / path.lstrip("/")).exists():
                        err(f"{nome}: risorsa {path} assente")
                    continue
                if path.lstrip("/") not in esistenti:
                    err(f"{nome}: link interno rotto {href}")
                elif anc:
                    dest = (SITO / path.lstrip("/") / "index.html") if path.endswith("/") else SITO / path.lstrip("/")
                    if f'id="{anc}"' not in dest.read_text(encoding="utf-8"):
                        err(f"{nome}: ancora {href} assente nella pagina di arrivo")
        # rimandi alle fonti: ogni [n] ha la sua voce e ogni tabella dice da dove vengono i numeri
        for n_ in re.findall(r'href="#f(\d+)"', html):
            if f'id="f{n_}"' not in html:
                err(f"{nome}: rimando [{n_}] senza fonte")
        for t in tabelle_html(html):
            cap = re.search(r"<caption>(.*?)</caption>", t, re.S)
            if not cap or not re.search(r'href="(#f\d+|https://)', cap.group(1)):
                err(f"{nome}: tabella senza fonte nella didascalia")
        # FAQ visibili = JSON-LD
        ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        faq_ld = [x for x in ld if x.get("@type") == "FAQPage"]
        vis = [(testo(q), testo(re.sub(r'<sup class="ref">.*?</sup>', "", a))) for q, a in re.findall(r'<div class="faq"[^>]*><h3>(.*?)</h3><p>(.*?)</p></div>', html, re.S)]
        if vis or faq_ld:
            if len(faq_ld) != 1:
                err(f"{nome}: FAQ visibili senza un JSON-LD FAQPage (o doppio)")
            else:
                jl = [(q["name"], q["acceptedAnswer"]["text"]) for q in faq_ld[0]["mainEntity"]]
                if jl != vis:
                    err(f"{nome}: JSON-LD FAQ diverso dal testo visibile\n   {jl}\n   {vis}")
            for ric in re.findall(r'data-ricerca="([^"]+)"', html):
                if G.volume(unescape(ric)) <= 0:
                    err(f"{nome}: FAQ senza ricerca misurata ({ric})")
        if f.name != "404.html" and p not in ("about/", "privacy/") and 'class="fonti-box"' not in html:
            err(f"{nome}: elenco delle fonti assente")
    if set(locs) != canon:
        err(f"sitemap ≠ canonical: solo sitemap {sorted(set(locs) - canon)[:5]}, solo canonical {sorted(canon - set(locs))[:5]}")
    if len(locs) != len(set(locs)):
        err("sitemap con doppioni")
    for s in G.NOINDEX:
        if f"{G.URL_SITO}/{s}/" in locs:
            err(f"/{s}/ noindex ma in sitemap")
    attese = {"", "calculator/", "pay-raise-history/", "2027-pay-raise/", "how-we-check/", "about/", "privacy/"} | {f"{s}/" for s, *_ in G.GRADI}
    if not attese <= {percorso(f) for f in pagine()}:
        err(f"pagine mancanti: {attese - {percorso(f) for f in pagine()}}")
    return len(locs)


def controlla_file():
    if (SITO / "robots.txt").read_text() != f"User-agent: *\nAllow: /\nSitemap: {G.URL_SITO}/sitemap.xml\n":
        err("robots.txt diverso")
    if (SITO / f"{G.CHIAVE_INDEXNOW}.txt").read_text() != G.CHIAVE_INDEXNOW:
        err("chiave IndexNow")
    nt = (SITO / "netlify.toml").read_text()
    if 'ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' not in nt:
        err("netlify.toml senza la regola ignore")
    for f in ("assets/og.png", "404.html", "ads.txt"):
        if not (SITO / f).exists():
            err(f"manca {f}")
    if '<meta name="robots" content="noindex' not in (SITO / "404.html").read_text():
        err("404 senza noindex")
    e, info = MON.controlla_sito(G.SITO_ID, SITO)
    errori.extend(f"monetizzazione: {x}" for x in e)
    # nessun nome di modelli AI, chiavi o dati personali nei file sorgente e nei dati
    for f in list(RADICE.rglob("*.py")) + list(RADICE.rglob("*.json")) + list(RADICE.rglob("*.js")) + list(RADICE.rglob("*.md")) + list(RADICE.rglob("*.html")):
        if "cache" in f.parts or "__pycache__" in f.parts:
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        if ("_".join(["sd", "live"])) in t or parole_vietate(t):
            err(f"{f.relative_to(RADICE)}: nome di modello AI, chiave o dato personale")
    return info


def main():
    stat = controlla_dati()
    n_home, n_gradi = controlla_celle()
    n_calc = controlla_calcolatore()
    n_url = controlla_pagine()
    controlla_revisione()
    info = controlla_file()
    print(f"Dati: {stat['celle']} celle ({stat['importi']} importi), {stat['confronto_2025']} confrontate con gennaio 2025 e {stat['confronto_aprile_2025']} con la tabella di legge di aprile 2025 "
          f"(× 1,038 ± $0,15), {stat['al_tetto']} al tetto; tetto O-7…O-10 {G.soldi(G.TETTO_II)}; {len(CASI_MANO)} casi letti a mano sulle immagini.")
    print(f"Pagine: {len(pagine())} file HTML, {n_url} nella sitemap; celle pubblicate controllate: home {n_home}, pagine di grado {n_gradi}; calcolatore JS = Python su {n_calc} combinazioni.")
    print(f"Monetizzazione: {info}")
    if "--browser" in sys.argv:
        casi = []
        for s, k, c in [("e-5", "E-5", 3), ("o-8", "O-8", 13), ("e-9", "E-9", 0), ("w-5", "W-5", 21), ("e-1-under-4-months", "E-1<4", 0), ("o-6", "O-6", 21), ("o-2e", "O-2E", 5),
                        ("o-10", "O-10", 11), ("o-8", "O-8", 11), ("e-4", "E-4", 0), ("e-4", "E-4", 1), ("o-1e", "O-1E", 2)]:
            r = G.calcola(s, k, c)
            if r is None:
                casi.append({"g": s, "y": c, "slug": G.slug_col(c), "contiene": ["No rate in the 2026 table"]})
            else:
                cont = [G.soldi(r["mese"]), G.soldi(r["anno"])]
                if r["tetto"] is not None:
                    cont.append("At the monthly limit.")
                cont.append(G.soldi(r["prossimo"]["mese"]) if r["prossimo"] else "Top of the")
                casi.append({"g": s, "y": c, "slug": G.slug_col(c), "contiene": cont})
        env = dict(os.environ, CASI_CALC=json.dumps(casi))
        p = subprocess.run(["node", str(RADICE / "verifica_browser.js")], env=env, capture_output=True, text=True)
        print(p.stdout.strip())
        if p.returncode:
            err("controllo nel browser fallito" + (": " + p.stderr.strip()[-500:] if p.stderr.strip() else ""))
    for a in avvisi:
        print("AVVISO:", a)
    if errori:
        print(f"{len(errori)} ERRORI:\n - " + "\n - ".join(errori[:80]))
        sys.exit(1)
    print("0 errori.")


if __name__ == "__main__":
    main()
