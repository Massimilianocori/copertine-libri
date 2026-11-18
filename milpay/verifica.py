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

Sezione per diem e miglia (13/11/2026, controlla_perdiem): celle delle tabelle per Stato e per località = xlsx GSA riletto qui in modo indipendente;
dati dei calcolatori = grezzo; JS = Python su centinaia di viaggi e di casi di miglia; casi a mano; tabella M&IE = API GSA; citazioni = frasi ritrovate nelle fonti.
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
import sezione_perdiem as SP  # noqa: E402
import sezione_va as SV  # noqa: E402

SP.carica(G)
SV.carica(G)

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
            elif nomi not in ({"g", "y"}, {"l", "da", "a"}, {"data", "scopo", "miglia"}, {"q"}, {"g", "lista", "s", "p", "u", "c"}):
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
        sez_pd = p.startswith("per-diem/") or p.startswith("irs-mileage-rate/")
        sez_va = p.startswith("va-disability-")
        if sez_va:
            if "not affiliated with the Department of Veterans Affairs, the Department of Defense or any other federal agency" not in html or "not benefits advice" not in html \
                    or "Only VA decides your rating, your dependents and what you are paid" not in html:
                err(f"{nome}: avviso della sezione VA (non affiliazione, informazione e non consulenza) assente")
        elif not sez_pd and "not affiliated with the Department of Defense" not in html:
            err(f"{nome}: avviso di non affiliazione assente")
        if sez_pd and "not affiliated with the General Services Administration, the IRS, the Department of Defense or any other federal agency" not in html:
            err(f"{nome}: avviso di non affiliazione (GSA, IRS, DoD) assente")
        if not sez_va and "finance office" not in html:
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
    attese = ({"", "calculator/", "pay-raise-history/", "2027-pay-raise/", "how-we-check/", "about/", "privacy/", "per-diem/", "per-diem/calculator/", "irs-mileage-rate/"}
              | {f"{s}/" for s, *_ in G.GRADI} | {f"per-diem/{SP.slug_stato(st)}/" for st in SP.PD["stati"]}
              | {f"per-diem/{SP.slug_stato(st)}/{sl}/" for st, sl, *_ in SP.LOC_PAGINE}
              | {"va-disability-rates/", "va-disability-calculator/", "va-disability-rates/2027/"} | {SV.slug_grado(g) for g in range(10, 101, 10)})
    if not attese <= {percorso(f) for f in pagine()}:
        err(f"pagine mancanti: {attese - {percorso(f) for f in pagine()}}")
    return len(locs)


# ---------------------------------------------------------------- sezione per diem e chilometri (13/11/2026)
MESI_FY = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]

# Casi calcolati a mano dai file grezzi GSA (non dal calcolatore del costruttore): (località, primo giorno, ultimo giorno, alloggio, M&IE, totale).
# New York City FY2027: Oct-Dec $342?, letti nell'xlsx; vedi controlla_perdiem, che li ricalcola dai valori grezzi e li confronta con queste cifre.
CASI_PD_MANO = [
    ("std", "2026-12-07", "2026-12-10", 3 * 113, 51 + 68 + 68 + 51),        # standard FY2027: 113 / 68
    ("std", "2026-09-29", "2026-10-02", 110 + 110 + 113, 51 + 68 + 68 + 51),  # attraversa il 1/10/2026: 110 (FY2026) poi 113 (FY2027)
    ("std", "2026-12-07", "2026-12-07", 0, 51),                               # stesso giorno: 75 % del M&IE, niente alloggio
]


# Parti di Maryland e Virginia dentro l'area GSA "District of Columbia": parole che devono stare nel file grezzo e nelle due pagine.
DC_FUORI = {"MD": {"grezzo": ["Montgomery and Prince George's in Maryland"], "pagina": ["Montgomery", "Prince George's"]},
            "VA": {"grezzo": ["Alexandria, Falls Church and Fairfax", "Arlington and Fairfax, in Virginia"], "pagina": ["Alexandria", "Falls Church", "Arlington", "Fairfax"]}}


def grezzo_fy(fy):
    """Lettura indipendente del file xlsx GSA: {(stato, destinazione): {"mesi", "mie", "contee"}}, tariffa standard."""
    import openpyxl
    ws = openpyxl.load_workbook(RADICE / "dati" / "grezzi" / f"gsa_fy{fy}.xlsx", data_only=True).worksheets[0]
    righe = list(ws.iter_rows(values_only=True))
    o = 1 if fy == "2026" else 0
    std = (righe[2][o + 5], righe[2][o + 6])
    out = {}
    for r in righe[3:]:
        st, dest, cty, b, e, lod, mie = (r[o + i] for i in range(7))
        k = (str(st).strip(), str(dest).strip())
        x = out.setdefault(k, {"mesi": [None] * 12, "mie": mie, "contee": str(cty).strip()})
        if not str(b or "").strip():
            ia, ib = 0, 11
        else:
            ia, ib = MESI_FY.index(str(b).strip()[:3]), MESI_FY.index(str(e).strip()[:3])
        for i in range(ia, ib + 1):
            x["mesi"][i] = lod
    return out, std


def usd_txt(v):
    return f"${v:,}" if float(v).is_integer() else f"${v:,.2f}"


def controlla_perdiem():
    n_celle = 0
    raw = {fy: grezzo_fy(fy) for fy in ("2026", "2027")}
    for fy, (d, s) in raw.items():
        if any(None in x["mesi"] for x in d.values()):
            err(f"FY{fy}: mesi senza tariffa nel file grezzo")
    stati = SP.PD["stati"]
    # 1) ogni cella delle tabelle per Stato = file grezzo
    for st, nome_st in stati.items():
        f = SITO / "per-diem" / SP.slug_stato(st) / "index.html"
        html = f.read_text(encoding="utf-8")
        for fy, (d, s) in raw.items():
            t = next((t for t in tabelle_html(html) if f"{testo(nome_st)}, FY {fy} (" in testo(re.search(r"<caption>(.*?)</caption>", t, re.S).group(1))), None)
            if not t:
                err(f"/per-diem/{SP.slug_stato(st)}/: tabella FY{fy} assente")
                continue
            righe = righe_html(t)[1:]
            attese = {k[1]: v for k, v in d.items() if k[0] == st}
            # revisione del 13/11/2026: l'area GSA di Washington DC comprende contee di Maryland e Virginia (testo GSA nel file grezzo).
            # Le due pagine devono mostrarla come riga, con i valori della riga DC: prima chi cercava Bethesda o Arlington leggeva la tariffa standard.
            if st in DC_FUORI:
                dc = d[("DC", "District of Columbia")]
                if not all(x in dc["contee"].replace("’", "'") for x in DC_FUORI[st]["grezzo"]):
                    err(f"FY{fy}: la definizione GSA dell'area di Washington DC non nomina più {DC_FUORI[st]['grezzo']}")
                attese["Washington, DC area"] = dc
                riga_dc = next((r for r in righe if r[0] == "Washington, DC area"), None)
                if not riga_dc or not all(x in riga_dc[1].replace("’", "'") for x in DC_FUORI[st]["pagina"]):
                    err(f"/per-diem/{SP.slug_stato(st)}/ FY{fy}: manca la riga dell'area di Washington DC con {DC_FUORI[st]['pagina']}")
                tp = testo(html).replace("’", "'")
                if not all(x in tp for x in DC_FUORI[st]["pagina"]) or "not the standard rate" not in tp:
                    err(f"/per-diem/{SP.slug_stato(st)}/: il testo non dice che {DC_FUORI[st]['pagina']} hanno la tariffa di Washington DC")
            elif any("Washington, DC area" == r[0] for r in righe):
                err(f"/per-diem/{SP.slug_stato(st)}/ FY{fy}: riga dell'area di Washington DC in uno Stato che non ne fa parte")
            if righe[0][0] != "Standard rate" or righe[0][2] != usd_txt(s[1]) or any(c != usd_txt(s[0]) for c in righe[0][3:]):
                err(f"/per-diem/{SP.slug_stato(st)}/ FY{fy}: riga standard {righe[0]}")
            if sorted(r[0] for r in righe[1:]) != sorted(attese):
                err(f"/per-diem/{SP.slug_stato(st)}/ FY{fy}: località {sorted(r[0] for r in righe[1:])} ≠ grezzo {sorted(attese)}")
            for r in righe[1:]:
                x = attese.get(r[0])
                if not x:
                    continue
                n_celle += 13
                if r[2] != usd_txt(x["mie"]) or r[3:] != [usd_txt(v) for v in x["mesi"]]:
                    err(f"/per-diem/{SP.slug_stato(st)}/ FY{fy} {r[0]}: pagina {r[2:]} ≠ grezzo {x['mie']} {x['mesi']}")
    # 2) pagine di località: tabella per mese = grezzo; frasi obbligatorie
    for st, sl, ric, disp in SP.LOC_PAGINE:
        html = (SITO / "per-diem" / SP.slug_stato(st) / sl / "index.html").read_text(encoding="utf-8")
        nome = next(L["nome"] for L in SP.PD["fy"]["2027"]["localita"] if L["stato"] == st and L["slug"] == sl)
        t = next((t for t in tabelle_html(html) if "lodging rate per night by month" in t), "")
        righe = righe_html(t)[1:]
        a, b = raw["2027"][0][(st, nome)], raw["2026"][0][(st, nome)]
        if [r[0] for r in righe] != MESI_FY or [r[1] for r in righe] != [usd_txt(v) for v in a["mesi"]] or [r[2] for r in righe] != [usd_txt(v) for v in b["mesi"]]:
            err(f"/per-diem/{SP.slug_stato(st)}/{sl}/: tabella per mese ≠ grezzo")
        n_celle += 24
        tv = testo(html)
        if "travel under the Joint Travel Regulations" in tv:
            err(f"/per-diem/{SP.slug_stato(st)}/{sl}/: afferma una regola del JTR senza fonte letta")
        if f"M&IE per day" not in tv or usd_txt(a["mie"]) not in tv or "Joint Travel Regulations" not in tv:
            err(f"/per-diem/{SP.slug_stato(st)}/{sl}/: mancano M&IE o la nota sui viaggi militari")
        if G.volume(ric) < SP.SOGLIA:
            err(f"/per-diem/{SP.slug_stato(st)}/{sl}/: domanda misurata sotto soglia")
    # 3) tabella M&IE = API grezza; tariffa standard e 75 % nell'indice
    mie_api = json.loads((RADICE / "dati" / "grezzi" / "gsa_api_mie_2027.json").read_text())
    idx = (SITO / "per-diem" / "index.html").read_text(encoding="utf-8")
    t = next((t for t in tabelle_html(idx) if "M&amp;IE breakdown" in t), "")
    attese = [[usd_txt(m["total"]), usd_txt(m["breakfast"]), usd_txt(m["lunch"]), usd_txt(m["dinner"]), usd_txt(m["incidental"]), f"${m['FirstLastDay']:.2f}"] for m in mie_api]
    if righe_html(t)[1:] != attese:
        err(f"/per-diem/: tabella M&IE ≠ API GSA: {righe_html(t)[1:]}")
    ti = testo(idx)
    for frase in ("On the first and last travel day, Federal employees are only eligible for 75 percent of the total M&IE rate",
                  f"{usd_txt(raw['2027'][1][0])} + {usd_txt(raw['2027'][1][1])}", "Joint Travel Regulations", "(403)", "Alaska, Hawaii, and U.S. territories and possessions"):
        if frase not in ti:
            err(f"/per-diem/: manca «{frase}»")
    # 4) dati del calcolatore in ogni pagina = file grezzo; JS = Python su molti viaggi; casi a mano
    js = next((SITO / "assets").glob("app.*.js"))
    import random
    rnd = random.Random(13112026)
    pagine_calc = [f for f in pagine() if 'id="dati-pd"' in f.read_text(encoding="utf-8")]
    if len(pagine_calc) != 1 + len(stati) + len(SP.LOC_PAGINE):
        err(f"calcolatore per diem in {len(pagine_calc)} pagine")
    D_tutto = None
    for f in pagine_calc:
        D = json.loads(re.search(r'<script type="application/json" id="dati-pd">(.*?)</script>', f.read_text(encoding="utf-8"), re.S).group(1))
        for fy, (d, s) in raw.items():
            F = D["fy"][fy]
            if F["std"] != [[s[0]] * 12, s[1]]:
                err(f"/{percorso(f)}: tariffa standard FY{fy} del calcolatore ≠ grezzo")
            for k, (mesi, mie) in F["loc"].items():
                st = k.split("/")[0].upper()
                x = next((v for (s2, n2), v in d.items() if s2 == st and SP.PD and any(L["slug"] == k.split("/")[1] and L["nome"] == n2 for L in SP.PD["fy"][fy]["localita"])), None)
                if x is None:  # rinomina: la chiave FY2027 porta i valori FY2026 della località con le stesse contee
                    x = next((v for (s2, n2), v in d.items() if s2 == st and v["contee"] == next(L["contee"] for L in SP.PD["fy"]["2027"]["localita"] if f"{L['stato'].lower()}/{L['slug']}" == k)), None)
                if x is None or x["mesi"] != mesi or x["mie"] != mie:
                    err(f"/{percorso(f)}: calcolatore {k} FY{fy} ≠ grezzo")
        if percorso(f) == "per-diem/calculator/":
            D_tutto = D
    chiavi = ["std"] + list(D_tutto["fy"]["2027"]["loc"])
    giorni = [date_iso(2025, 10, 1, i) for i in range(0, 730)]
    casi = []
    for _ in range(500):
        k = rnd.choice(chiavi)
        a = rnd.choice(giorni)
        casi.append((k, a, add_days(a, rnd.choice([0, 0, 1, 2, 3, 4, 6, 9, 13, 30, 60, 200]))))
    casi += [(k, "2026-09-28", "2026-10-03") for k in rnd.sample(chiavi, 40)]  # passaggio d'anno fiscale
    casi += [("std", "2025-09-30", "2025-10-02"), ("std", "2027-09-29", "2027-10-01"), ("std", "2026-05-10", "2026-05-01"), ("std", "", "2026-05-01"),
             ("std", "2026-02-30", "2026-03-01"), ("il/oakbrook-terrace", "2026-09-29", "2026-10-02"), ("pa/allentown-easton-bethlehem", "2026-09-29", "2026-10-02")]
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(D_tutto)};const C={json.dumps(casi)};"
            "console.log(JSON.stringify(C.map(x=>m.viaggio(D,x[0],x[1],x[2]))));")
    out = json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)
    diversi = 0
    for c, r in zip(casi, out):
        py = SP.viaggio(D_tutto, *c)
        if json.dumps(py, sort_keys=True) != json.dumps(r, sort_keys=True).replace(".0,", ",") and py != r:
            diversi += 1
            if diversi < 4:
                err(f"calcolatore per diem JS ≠ Python {c}: {str(r)[:200]} / {str(py)[:200]}")
    if diversi:
        err(f"calcolatore per diem: {diversi} viaggi diversi su {len(casi)}")
    errori_attesi = {2: "errore", 3: "errore", 4: "errore"}
    if out[-7].get("errore") != "fuori" or out[-6].get("errore") != "fuori" or out[-5].get("errore") != "ordine" or out[-4].get("errore") != "data" or out[-3].get("errore") != "data":
        err(f"calcolatore per diem: casi di errore non riconosciuti {out[-7:-2]}")
    if "errore" in out[-2] or out[-1].get("errore") != "non_listata":
        err(f"calcolatore per diem: rinomina Oak Brook Terrace o Allentown (non più elencata) {out[-2:]}")
    # casi a mano e un caso reale ricalcolato a mano dai valori grezzi (New York City, 30/12/2026 - 2/1/2027)
    nyc = raw["2027"][0][("NY", "New York City")]
    casi_m = CASI_PD_MANO + [("ny/new-york-city", "2026-12-30", "2027-01-02", nyc["mesi"][2] + nyc["mesi"][2] + nyc["mesi"][3], nyc["mie"] * (0.75 * 2 + 2))]
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(D_tutto)};const C={json.dumps([c[:3] for c in casi_m])};"
            "console.log(JSON.stringify(C.map(x=>m.viaggio(D,x[0],x[1],x[2]))));")
    for c, r in zip(casi_m, json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)):
        if abs(r.get("alloggio", -1) - c[3]) > 1e-9 or abs(r.get("mie", -1) - c[4]) > 1e-9 or abs(r["totale"] - c[3] - c[4]) > 1e-9:
            err(f"calcolatore per diem, caso a mano {c}: {r}")
    # 5) chilometri: valori della pagina = testo grezzo IRS/GSA; JS = Python
    km = (SITO / "irs-mileage-rate" / "index.html").read_text(encoding="utf-8")
    tk = testo(km)
    for frase in ("72.5¢", "76¢", "20.5¢", "23.5¢", "14¢", "$0.760", "$0.725", "$0.235", "$0.205", "Announcement 2026-11", "Notice 2026-10", "had not published 2027 rates"):
        if frase not in tk:
            err(f"/irs-mileage-rate/: manca «{frase}»")
    import subprocess as sp_
    nt = re.sub(r"\s+", " ", sp_.run(["pdftotext", str(RADICE / "dati" / "grezzi" / "irs_notice_2026-10.pdf"), "-"], capture_output=True, text=True).stdout)
    irb = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", (RADICE / "dati" / "grezzi" / "irs_irb_2026-29.html").read_text(encoding="utf-8", errors="replace"))))
    for frase, dove in (("is 72.5 cents per mile for all miles of business use", nt), ("is 20.5 cents per mile for use of an automobile", nt), ("(1) Business 76 cents per mile", irb),
                        ("(2) Medical and moving 23.5 cents per mile", irb)):
        if frase not in dove:
            err(f"file grezzo IRS: manca «{frase}»")
    DK = json.loads(re.search(r'<script type="application/json" id="dati-km">(.*?)</script>', km, re.S).group(1))
    if [p_["tariffe"]["business"] for p_ in DK["periodi"]] != [725, 760] or [p_["tariffe"]["medical"] for p_ in DK["periodi"]] != [205, 235] or {p_["tariffe"]["charity"] for p_ in DK["periodi"]} != {140} \
            or [p_["tariffe"]["gsa_auto"] for p_ in DK["periodi"]] != [725, 760] or [p_["tariffe"]["gsa_auto_gov"] for p_ in DK["periodi"]] != [205, 235]:
        err(f"/irs-mileage-rate/: tariffe del calcolatore {DK}")
    casi_k = [(date_iso(2026, 1, 1, rnd.randrange(365)), rnd.choice(["business", "medical", "charity", "gsa_auto", "gsa_auto_gov"]), str(rnd.choice([1, 12.5, 100, 0.05, 0.15, 333.3, 1234.45, 99999])))
              for _ in range(300)]
    casi_k += [("2026-06-30", "business", "100"), ("2026-07-01", "business", "100"), ("2027-01-01", "business", "10"), ("2026-03-01", "business", "0"), ("2026-03-01", "x", "5")]
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(DK)};const C={json.dumps(casi_k)};console.log(JSON.stringify(C.map(x=>m.miglia(D,x[0],x[1],x[2]))));")
    outk = json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)
    dk = sum(1 for c, r in zip(casi_k, outk) if json.dumps(SP.miglia(DK, *c), sort_keys=True) != json.dumps(r, sort_keys=True) and SP.miglia(DK, *c) != r)
    if dk:
        err(f"calcolatore miglia: {dk} casi JS ≠ Python")
    if outk[-5]["importo"] != 72.5 or outk[-4]["importo"] != 76.0 or outk[-3].get("errore") != "fuori" or outk[-2].get("errore") != "miglia" or outk[-1].get("errore") != "scopo":
        err(f"calcolatore miglia: casi a mano {outk[-5:]}")
    # 6) ogni citazione tra virgolette nelle pagine della sezione è una frase ritrovata nella fonte ufficiale (fonti.json, "cerca")
    def nrm(s):
        return re.sub(r"\s+", " ", s.replace("’", "'").replace("–", "-").replace("—", "-")).strip().rstrip(".,;")
    frasi = [nrm(c) for fid, fd in G.FONTI.items() for c, ok in G.ESITI.get(fid, {}).get("trovate", {}).items() if ok]
    n_cit = 0
    for f in pagine():
        p_ = percorso(f)
        if not (p_.startswith("per-diem/") or p_.startswith("irs-mileage-rate/") or p_.startswith("va-disability-")):
            continue
        for q in re.findall(r"“([^”]{20,})”", testo(f.read_text(encoding="utf-8"))):
            n_cit += 1
            if not any(nrm(q) in fr for fr in frasi):
                err(f"/{p_}: citazione non ritrovata nelle fonti «{q[:80]}»")
    return {"celle": n_celle, "viaggi": len(casi), "casi_miglia": len(casi_k), "pagine_calcolatore": len(pagine_calc), "citazioni": n_cit}


# ---------------------------------------------------------------- sezione VA disability (15/11/2026)
# Lettura indipendente dei file grezzi (non usa raccolta/va.py né dati/va.json): ogni cella pubblicata = pagina va.gov scaricata; il calcolatore JS =
# calcolo rifatto dagli importi di legge dell'avviso nel Federal Register (38 U.S.C. 1114 e 1115) = copia Python; gradi combinati JS = formula del 38 CFR 4.25.
VA_STATI = ["alone", "spouse", "spouse_p1", "spouse_p2", "p1", "p2", "child", "child_spouse", "child_spouse_p1", "child_spouse_p2", "child_p1", "child_p2"]
VA_AGG = ["child_u18", "child_school", "spouse_aa"]
# casi letti a mano il 15/11/2026: esempi scritti nella pagina va.gov e celle guardate nella pagina (grado, coniuge, A&A, genitori, figli <18, figli a scuola, centesimi)
CASI_VA_MANO = [(30, 1, 0, 0, 0, 0, 61747), (70, 1, 1, 0, 3, 0, 236745), (70, 1, 0, 0, 3, 0, 222645), (100, 0, 0, 0, 0, 0, 393858), (100, 1, 0, 0, 1, 0, 431899), (10, 1, 0, 2, 3, 1, 18042),
                 (20, 0, 0, 0, 0, 0, 35666), (60, 1, 0, 2, 1, 0, 187302), (90, 0, 0, 1, 0, 0, 252030), (50, 0, 0, 0, 1, 0, 120590), (100, 1, 1, 2, 2, 1, 467147 + 10911 + 35245 + 20141)]
# esempi del 38 CFR 4.25 e nota della Table I: (gradi, valore combinato, grado finale)
CASI_COMB_MANO = [([50, 30], 65, 70), ([40, 20], 52, 50), ([60, 40, 20], 81, 80), ([10, 10], 19, 20), ([20, 60, 40], 81, 80), ([100, 10], 100, 100), ([70], 70, 70), ([90, 90], 99, 100)]


def _cent(t):
    m = re.fullmatch(r"\+?\$?(\d{1,3}(?:,\d{3})*|\d+)\.(\d\d)", t.strip())
    return int(m.group(1).replace(",", "")) * 100 + int(m.group(2)) if m else None


def va_grezzo(nome):
    """Pagina va.gov scaricata -> (base 10 gradi, righe 12 × 8, aggiunte 3 × 8), per posizione nelle tabelle della pagina."""
    t = (RADICE / "dati" / "grezzi" / nome).read_text(encoding="utf-8")
    tab = []
    for blocco in re.findall(r"<va-table\b.*?</va-table>", t, re.S):
        righe = []
        for r in re.findall(r"<va-table-row[^>]*>(.*?)</va-table-row>", blocco, re.S):
            celle = [testo(c) for c in r.split("</span><span>")]
            righe.append(celle)
        tab.append(righe)
    base = {10: _cent(tab[0][1][1]), 20: _cent(tab[0][2][1])}
    righe = {k: {} for k in VA_STATI}
    agg = {k: {} for k in VA_AGG}
    for i, (figli, gg) in enumerate([(0, [30, 40, 50, 60]), (0, [70, 80, 90, 100]), (1, [30, 40, 50, 60]), (1, [70, 80, 90, 100])]):
        b, a = tab[1 + 2 * i], tab[2 + 2 * i]
        for k, r in zip(VA_STATI[6:] if figli else VA_STATI[:6], b[1:]):
            for g, v in zip(gg, r[1:]):
                righe[k][g] = _cent(v)
        for r in a[1:]:
            nome_r = r[0].lower()
            k = "child_u18" if "under age 18" in nome_r else ("child_school" if "school" in nome_r else "spouse_aa")
            for g, v in zip(gg, r[1:]):
                agg[k][g] = _cent(v)
    for g in range(30, 101, 10):
        base[g] = righe["alone"][g]
    return base, righe, agg


def va_avviso(nome):
    """Avviso del VA nel Federal Register -> importi di legge in centesimi (lettura a parte, per righe)."""
    t = unescape(re.sub(r"<[^>]+>", "", (RADICE / "dati" / "grezzi" / nome).read_text(encoding="utf-8")))
    v = {}
    for riga in t.splitlines():
        m = re.match(r"\s*(\S.*?)\.{5,}\s+(\S.*)$", riga)
        if m:
            v[re.sub(r"\s+", "", m.group(1)).replace("38U.S.C.Sec.", "").replace("38U.S.C.", "")] = [_cent(x) for x in re.findall(r"[\d,]+\.\d\d", m.group(2))]
    return v


def va_atteso(av, g, coniuge, aa, genitori, u18, scuola):
    """Importo dagli importi di legge: 38 U.S.C. 1114 (base) + 1115(1) (familiari, al 100 %) con la proporzione e l'arrotondamento per difetto del 1115(2)."""
    q = (lambda x: x) if g == 100 else (lambda x: (g * x // 10000) * 100)
    tot = av[str(g)][0]
    if g < 30:
        return tot
    if coniuge and u18:
        tot += q(av["1115(1)(B)"][0])
    elif coniuge:
        tot += q(av["1115(1)(A)"][0])
    elif u18:
        tot += q(av["1115(1)(C)"][0])
    tot += genitori * q(av["1115(1)(D)"][0])
    tot += max(0, u18 - 1) * q(av["1115(1)(B)"][1]) + scuola * q(av["1115(1)(F)"][0])
    if coniuge and aa:
        tot += q(av["1115(1)(E)"][0]) - q(av["1115(1)(A)"][0])
    return tot


def controlla_va():
    n_celle = 0
    R = {"2026": va_grezzo("va_rates_2026.html"), "2025": va_grezzo("va_rates_2025.html")}
    b26, r26, a26 = R["2026"]
    b25, r25, a25 = R["2025"]
    GG = list(range(30, 101, 10))
    for anno, (b, r, a) in R.items():
        if len(b) != 10 or any(v is None for v in b.values()) or any(len(r[k]) != 8 or None in r[k].values() for k in VA_STATI) or any(len(a[k]) != 8 or None in a[k].values() for k in VA_AGG):
            err(f"VA {anno}: file grezzo non letto per intero")
            return {"celle": 0, "combinazioni": 0, "liste": 0}
    usd = lambda c: f"${c // 100:,}.{c % 100:02d}"  # noqa: E731

    def tabella_base_ok(nome, html):
        nonlocal n_celle
        t = next((x for x in tabelle_html(html) if "Veteran with no dependents" in x), None)
        if t is None:
            err(f"{nome}: tabella base assente")
            return
        rr = righe_html(t)[1:]
        if len(rr) != 10:
            err(f"{nome}: tabella base con {len(rr)} righe")
        for g, r in zip(range(10, 101, 10), rr):
            att = [f"{g}%", usd(b26[g]), usd(b26[g] * 12), usd(b25[g]), "+" + usd(b26[g] - b25[g])]
            n_celle += 4
            if r != att:
                err(f"{nome}: riga {g}% {r} ≠ grezzo {att}")

    # 1) pagina delle tabelle
    hp = (SITO / "va-disability-rates" / "index.html").read_text(encoding="utf-8")
    tabella_base_ok("/va-disability-rates/", hp)
    tt = [righe_html(x) for x in tabelle_html(hp) if 'class="dati va"' in hp[max(0, hp.find(x) - 40):hp.find(x)]]
    if len(tt) != 3:
        err(f"/va-disability-rates/: {len(tt)} tabelle con familiari (attese 3)")
    else:
        for tab, chiavi, src, nomi in ((tt[0], VA_STATI[:6], r26, SV.STATO_NOME), (tt[1], VA_STATI[6:], r26, SV.STATO_NOME), (tt[2], VA_AGG, a26, SV.AGG_NOME)):
            if tab[0][1:] != [f"{g}%" for g in GG] or len(tab) != len(chiavi) + 1:
                err(f"/va-disability-rates/: intestazioni o righe inattese {tab[0]}")
            for k, r in zip(chiavi, tab[1:]):
                n_celle += 8
                if r != [nomi[k]] + [usd(src[k][g]) for g in GG]:
                    err(f"/va-disability-rates/: riga {k} {r} ≠ grezzo")
    # 2) pagine di grado
    for g in range(10, 101, 10):
        f = SITO / "va-disability-rates" / f"{g}-percent" / "index.html"
        if not f.exists():
            err(f"pagina del {g}% assente")
            continue
        hg = f.read_text(encoding="utf-8")
        tabs = [righe_html(x) for x in tabelle_html(hg)]
        tv = testo(hg)
        if f"{g}% VA Disability Pay 2026" not in tv or usd(b26[g]) not in re.search(r"<title>(.*?)</title>", hg).group(1):
            err(f"/{g}-percent/: titolo o importo assente")
        if g >= 30:
            if len(tabs) != 2 or len(tabs[0]) != 13 or len(tabs[1]) != 4:
                err(f"/{g}-percent/: tabelle inattese")
                continue
            for k, r in zip(VA_STATI, tabs[0][1:]):
                n_celle += 4
                if r != [SV.STATO_NOME[k], usd(r26[k][g]), usd(r26[k][g] * 12), usd(r25[k][g]), "+" + usd(r26[k][g] - r25[k][g])]:
                    err(f"/{g}-percent/: riga {k} {r} ≠ grezzo")
            for k, r in zip(VA_AGG, tabs[1][1:]):
                n_celle += 2
                if r != [SV.AGG_NOME[k], usd(a26[k][g]), usd(a25[k][g])]:
                    err(f"/{g}-percent/: aggiunta {k} {r} ≠ grezzo")
        else:
            n_celle += 6
            att = [usd(b26[g]), usd(b26[g] * 12), usd(b25[g]), usd(b25[g] * 12), "+" + usd(b26[g] - b25[g]), "+" + usd((b26[g] - b25[g]) * 12)]
            if len(tabs) != 1 or [c for r in tabs[0][1:] for c in r[1:]] != att:
                err(f"/{g}-percent/: tabella {tabs} ≠ grezzo {att}")
            if "won’t receive a higher rate even if you have a dependent spouse, child, or parent" not in tv:
                err(f"/{g}-percent/: manca la frase del VA sui familiari al 10-20 %")
    tabella_base_ok("/va-disability-calculator/", (SITO / "va-disability-calculator" / "index.html").read_text(encoding="utf-8"))
    h27 = (SITO / "va-disability-rates" / "2027" / "index.html").read_text(encoding="utf-8")
    tabella_base_ok("/va-disability-rates/2027/", h27)
    # 3) Table I: XML dell'eCFR riletto qui = dati del calcolatore = tabella pubblicata = formula del testo
    xml = (RADICE / "dati" / "grezzi" / "ecfr_38_4_25.xml").read_text(encoding="utf-8")
    TI = {}
    for tr in re.findall(r"<TR\b.*?</TR>", xml, re.S):
        c = [testo(x) for x in re.findall(r"<T[DH]\b[^>]*>(.*?)</T[DH]>", tr, re.S)]
        if len(c) == 10 and all(x.isdigit() for x in c):
            TI[c[0]] = [int(x) for x in c[1:]]
    formula = lambda a, b: (2 * (10000 - (100 - a) * (100 - b)) + 100) // 200  # noqa: E731
    if sorted(TI, key=int) != [str(i) for i in range(19, 95)] or any(TI[a][i] != formula(int(a), 10 * (i + 1)) for a in TI for i in range(9)):
        err("Table I (eCFR): righe mancanti o valori diversi dalla formula del testo")
    hc = (SITO / "va-disability-calculator" / "index.html").read_text(encoding="utf-8")
    tpub = next((righe_html(x) for x in tabelle_html(hc) if "Table I of 38 CFR 4.25" in x), [])
    if {r[0]: [int(x) for x in r[1:]] for r in tpub[1:]} != TI:
        err("/va-disability-calculator/: Table I pubblicata ≠ eCFR")
    n_celle += len(TI) * 9
    # 4) dati dei calcolatori in ogni pagina = grezzo
    js = SITO / "assets" / G.JS_FILE
    DV = None
    pagine_calc = 0
    for f in pagine():
        hh = f.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="dati-va">(.*?)</script>', hh, re.S)
        if ("data-va" in hh) != bool(m):
            err(f"/{percorso(f)}: calcolatore VA senza dati (o dati senza calcolatore)")
        if not m:
            continue
        pagine_calc += 1
        D = json.loads(m.group(1))
        if (D["base"] != {str(g): v for g, v in b26.items()} or D["righe"] != {k: {str(g): v for g, v in r26[k].items()} for k in VA_STATI}
                or D["agg"] != {k: {str(g): v for g, v in a26[k].items()} for k in VA_AGG} or D["T"] != TI or D["anno"] != "2026"):
            err(f"/{percorso(f)}: dati del calcolatore VA ≠ file grezzi")
        DV = D
    if pagine_calc != 12 or DV is None:
        err(f"calcolatore VA in {pagine_calc} pagine (attese 12)")
        return {"celle": n_celle, "combinazioni": 0, "liste": 0}
    # 5) JS = importi di legge dell'avviso (calcolo rifatto qui) = copia Python, su tutte le combinazioni
    av = va_avviso("va_fr_2026-02997.htm")
    casi = [(g, c, aa, p, u, sc) for g in range(10, 101, 10) for c in (0, 1) for aa in (0, 1) for p in (0, 1, 2) for u in range(0, 6) for sc in range(0, 4)]
    casi += [(100, 1, 1, 2, 12, 12), (30, 0, 0, 0, 13, 0), (25, 0, 0, 0, 0, 0), (110, 0, 0, 0, 0, 0), (50, 2, 0, 0, 0, 0), (50, 0, 0, 3, 0, 0), (50, 0, 0, 0, 1.5, 0), (50, 0, 0, 0, -1, 0)]
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(DV)};const C={json.dumps(casi)};console.log(JSON.stringify(C.map(x=>m.vaPaga(D,x[0],x[1],x[2],x[3],x[4],x[5]))));")
    out = json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)
    diversi = 0
    for c, r in zip(casi[:-8], out):
        g, co, aa, p, u, sc = c
        if g >= 30 and sc and not u:
            ok = r.get("errore") == "scuola"
        else:
            ok = r.get("cent") == va_atteso(av, *c) and r.get("anno") == 12 * r.get("cent")
        if ok and (g < 30 or u or not sc) and c[4] == int(c[4]):
            py = SV.paga(DV, *c)
            ok = json.dumps(py, sort_keys=True) == json.dumps(r, sort_keys=True)
        if not ok:
            diversi += 1
            if diversi < 4:
                err(f"calcolatore VA {c}: JS {r} ≠ importi di legge {va_atteso(av, *c)} o ≠ Python")
    if diversi:
        err(f"calcolatore VA: {diversi} combinazioni diverse su {len(casi)}")
    if out[-8].get("cent") != va_atteso(av, 100, 1, 1, 2, 12, 12) or [x.get("errore") for x in out[-7:]] != ["dati", "grado", "grado", "dati", "dati", "dati", "dati"]:
        err(f"calcolatore VA: casi limite {out[-8:]}")
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(DV)};const C={json.dumps([c[:6] for c in CASI_VA_MANO])};console.log(JSON.stringify(C.map(x=>m.vaPaga(D,x[0],x[1],x[2],x[3],x[4],x[5]))));")
    for c, r in zip(CASI_VA_MANO, json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)):
        if r.get("cent") != c[6]:
            err(f"calcolatore VA, caso letto a mano {c}: {r}")
    # 6) gradi combinati: JS = formula applicata in ordine di gravità (calcolo rifatto qui) = copia Python
    import random
    rnd = random.Random(20261115)
    liste = [[rnd.choice(range(10, 101, 10)) for _ in range(rnd.choice([1, 2, 2, 3, 3, 4, 5, 7, 10]))] for _ in range(3000)]
    liste += [[a, b] for a in range(10, 101, 10) for b in range(10, 101, 10)]
    brutte = [[], [15], [0], [110], ["50"], [50, 30.5], list(range(10, 101, 10)) * 3]
    prog = (f"const m=require({json.dumps(str(js))});const D={json.dumps(DV)};const C={json.dumps(liste + brutte + [c[0] for c in CASI_COMB_MANO])};console.log(JSON.stringify(C.map(x=>m.vaCombina(D,x))));")
    outc = json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)
    dc = 0
    for L, r in zip(liste, outc):
        v = None
        for x in sorted(L, reverse=True):
            v = x if v is None else formula(v, x)
        fin = min(100, (v + 5) // 10 * 10)
        py = SV.combina(DV, L)
        if r.get("finale") != fin or (r["valore"] != v and not (r["valore"] >= 95 and v >= 95)) or json.dumps(py, sort_keys=True) != json.dumps(r, sort_keys=True):
            dc += 1
            if dc < 4:
                err(f"gradi combinati {L}: JS {r} ≠ formula ({v} → {fin}) o ≠ Python")
    if dc:
        err(f"gradi combinati: {dc} liste diverse su {len(liste)}")
    if [x.get("errore") for x in outc[len(liste):len(liste) + len(brutte)]] != ["lista", "grado", "grado", "grado", "grado", "grado", "lista"]:
        err(f"gradi combinati: liste non valide non riconosciute {outc[len(liste):len(liste) + len(brutte)]}")
    for (L, v, fin), r in zip(CASI_COMB_MANO, outc[len(liste) + len(brutte):]):
        if (r.get("valore"), r.get("finale")) != (v, fin):
            err(f"gradi combinati, esempio del regolamento {L}: {r}")
    # 7) nessun importo 2027 calcolato: finché il VA non pubblica la tabella, nelle pagine non deve comparire nessun importo base × 1,036
    stimati = set()
    for g, c in b26.items():
        for k in (c * 1036 // 1000, (c * 1036 + 500) // 1000, c * 1036 // 1000 + 1):
            stimati.add(usd(k))
            stimati.add(usd(k)[1:])
    for f in pagine():
        tv = testo(f.read_text(encoding="utf-8"))
        trovati = [x for x in stimati if re.search(r"(?<![\d,.])" + re.escape(x) + r"(?!\d)", tv)]
        if trovati:
            err(f"/{percorso(f)}: importo 2027 calcolato in pagina {trovati[:3]} (vietato finché il VA non pubblica la tabella)")
    t27 = testo(h27)
    for frase in ("3.6 percent cost-of-living increase in Social Security benefits effective December 2026", "Not yet", "We do not publish a “2027 VA pay chart” worked out from the percentage",
                  "still showed the tables effective December 1, 2025", "H.R. 8552", "Nothing on this page is a forecast"):
        if frase not in t27:
            err(f"/va-disability-rates/2027/: manca «{frase}»")
    for vietata in (r"\bwill be \$", r"\bestimated\b", r"\bprojected\b", r"you should", r"we recommend", r"\bfile a claim\b", r"\bappeal\b", r"\blawyer\b", r"\battorney\b"):
        for f in pagine():
            if percorso(f).startswith("va-disability-") and re.search(vietata, testo(f.read_text(encoding="utf-8")), re.I):
                err(f"/{percorso(f)}: testo vietato nella sezione VA «{vietata}» (previsioni o consigli)")
    es = G.ESITI
    if es.get("plaw119", {}).get("va_cola_2026") != [] or (es.get("fr_va_search", {}).get("avvisi") or [{}])[0].get("numero") != "2026-02997":
        err("stato 2027: la legge o l'avviso nuovo risultano pubblicati, ma il sito dice di no")
    return {"celle": n_celle, "combinazioni": len(casi), "liste": len(liste), "pagine_calcolatore": pagine_calc}


def date_iso(y, m, d, piu):
    from datetime import date as _d, timedelta
    return (_d(y, m, d) + timedelta(days=piu)).isoformat()


def add_days(iso, n):
    from datetime import date as _d, timedelta
    return (_d.fromisoformat(iso) + timedelta(days=n)).isoformat()


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
    st_pd = controlla_perdiem()
    st_va = controlla_va()
    print(f"Dati: {stat['celle']} celle ({stat['importi']} importi), {stat['confronto_2025']} confrontate con gennaio 2025 e {stat['confronto_aprile_2025']} con la tabella di legge di aprile 2025 "
          f"(× 1,038 ± $0,15), {stat['al_tetto']} al tetto; tetto O-7…O-10 {G.soldi(G.TETTO_II)}; {len(CASI_MANO)} casi letti a mano sulle immagini.")
    print(f"Pagine: {len(pagine())} file HTML, {n_url} nella sitemap; celle pubblicate controllate: home {n_home}, pagine di grado {n_gradi}; calcolatore JS = Python su {n_calc} combinazioni.")
    print(f"Per diem: {st_pd['celle']} celle pubblicate = file grezzi GSA; calcolatore JS = Python su {st_pd['viaggi']} viaggi ({st_pd['pagine_calcolatore']} pagine); "
          f"miglia JS = Python su {st_pd['casi_miglia']} casi; {st_pd['citazioni']} citazioni ritrovate nelle fonti.")
    print(f"VA disability: {st_va['celle']} celle pubblicate = file grezzi (va.gov, eCFR); calcolatore JS = importi di legge del Federal Register = Python su {st_va['combinazioni']} combinazioni "
          f"({st_va.get('pagine_calcolatore', 0)} pagine); gradi combinati JS = formula del 38 CFR 4.25 su {st_va['liste']} liste; nessun importo 2027 calcolato in pagina.")
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
