"""Genera il sito statico "Real Estate Exam Pass Rates" (USA, inglese) in realestate/sito/.

Uso (dalla radice del repository):
    python3 realestate/raccolta/fonti.py       # scarica le fonti ufficiali, controlla le frasi, scrive dati/fonti.json e dati/tassi.json
    python3 realestate/raccolta/domanda.py <cartella con le risposte seodata>   # dati/domanda.json (solo quando si misurano ricerche nuove)
    python3 realestate/genera.py               # pagine in realestate/sito/
    python3 realestate/verifica.py [--browser] # controlli

Prova su 4 Stati (Texas, Alabama, Nebraska, Hawaii): per ogni Stato la tabella ufficiale degli esami di abilitazione per scuola
(esami, promossi, percentuale come la stampa la commissione; primo tentativo e totale dove la fonte li separa) e una pagina
«come ottenere la licenza» fatta solo con le pagine della commissione. Ogni cifra viene da dati/tassi.json, che raccolta/fonti.py
ricava dai file ufficiali in dati/grezzi/. Le frasi tra virgolette sono copiate alla lettera dalle fonti (dati/fonti.json).
Le FAQ nascono da ricerche misurate (dati/domanda.json). Nessuna classifica su campioni piccoli: accanto a ogni percentuale c'è il
numero di esami, sotto i 30 esami la percentuale è segnata «small sample» e nell'ordinamento per percentuale finisce dopo le altre.
Riquadro del partner (AceableAgent): spento finché dati/affiliati.json non ha il link tracciato vero e "attivo": true.
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlparse

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import stile  # noqa: E402
sys.path.insert(0, str(RADICE / "raccolta"))
import testo as TESTO  # noqa: E402

URL_SITO = "https://real-estate-exam-pass-rates.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso (c'è anche in verifica.py)
NOME = "Real Estate Exam Pass Rates"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "realestate"  # nome del sito in monetizzazione.json
ADSENSE_HEAD = MON.script_adsense(SITO_ID)


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


G = carica("tassi.json")
FONTI = carica("fonti.json")["fonti"]
DOM = carica("domanda.json")
AFF = carica("affiliati.json")
FONTI_PARTNER = {"aceable"}   # pagina del programma di affiliazione: non conta tra le fonti ufficiali e non è mai citata in pagina
CONTROLLO = date.fromisoformat(G["letto_il"])
SOGLIA = G["soglia_campione"]
LIC = G["licenza"]
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
STATI = ["TX", "AL", "NE", "HI"]          # ordine delle pagine (per domanda misurata)

# Misure di ogni Stato: (chiave in tassi.json, intestazione di colonna, descrizione lunga). La prima è la «primaria» (ordine iniziale, filtro dei 30 esami).
MISURE = {
    "TX": [("first", "First attempt", "sales agent exam, first attempt")],
    "AL": [("first", "First attempt", "salesperson exam, first attempt"), ("all", "All attempts", "salesperson exam, all attempts including retakes")],
    "NE": [("national_first", "National part, first-time takers", "salesperson exam, national part, first-time takers"),
           ("state_first", "State part, first-time takers", "salesperson exam, state part, first-time takers"),
           ("national_all", "National part, all takers", "salesperson exam, national part, first-time takers and repeaters"),
           ("state_all", "State part, all takers", "salesperson exam, state part, first-time takers and repeaters")],
    "HI": [("national", "National part", "salesperson exam, national part, all exams taken"), ("state", "State part", "salesperson exam, state part, all exams taken")],
}


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def giorno(iso):
    return data_lunga(date.fromisoformat(iso))


def num(n):
    return f"{n:,}"


def usd(cent):
    return f"${cent // 100:,}" + (f".{cent % 100:02d}" if cent % 100 else "")


def pct1(p, n):
    """Percentuale calcolata da noi (somme delle scuole), a un decimale, .5 in su, con interi."""
    d = (p * 2000 + n) // (2 * n)
    return f"{d // 10}.{d % 10}%"


def st(s):
    return G["stati"][s]


def slug(s):
    return st(s)["slug"]


def slug_lic(s):
    return f"{slug(s)}-real-estate-license"


def periodo(s, breve=False):
    p = st(s)["periodo"]
    if not p:
        return "the previous 12 months" if breve else "the 12 months before the commission’s latest monthly update"
    a, b = date.fromisoformat(p["dal"]), date.fromisoformat(p["al"])
    if a.year == b.year:
        return f"{MESI[a.month - 1]} {a.day} to {MESI[b.month - 1]} {b.day}, {b.year}"
    return f"{data_lunga(a)} to {data_lunga(b)}"


def tasso_stato(s, k):
    """Percentuale dello Stato per la misura k: quella ufficiale, oppure la nostra somma delle scuole (a un decimale)."""
    v = st(s)["totale"][k]
    return v["pc"] if st(s)["totale"]["origine"] == "ufficiale" else pct1(v["p"], v["n"])


# ---------------------------------------------------------------- fonti e citazioni
class Rimandi:
    def __init__(self):
        self.ordine = []

    def ref(self, ids):
        if isinstance(ids, str):
            ids = [i.strip() for i in ids.split(",") if i.strip()]
        nums = []
        for i in ids:
            if i not in FONTI or i in FONTI_PARTNER:
                raise SystemExit(f"fonte sconosciuta o non ufficiale: {i}")
            if i not in self.ordine:
                self.ordine.append(i)
            nums.append(self.ordine.index(i) + 1)
        return '<sup class="ref">' + ",".join(f'<a href="#f{n}" aria-label="source {n}">[{n}]</a>' for n in sorted(set(nums))) + "</sup>"

    def t(self, testo):
        return re.sub(r"\[\[([a-z0-9_, ]+)\]\]", lambda m: self.ref(m.group(1)), testo)

    def cit(self, fid, chiave):
        """Frase copiata alla lettera dalla fonte (controllata da raccolta/fonti.py sul file grezzo)."""
        f = FONTI[fid]
        if not f["trovate"].get(chiave):
            raise SystemExit(f"citazione {fid}/{chiave} non trovata nel file grezzo")
        return (f'<blockquote class="cit" data-fonte="{fid}" data-frase="{chiave}"><p>“<span data-cit>{h(f["frasi"][chiave])}</span>”</p>'
                f'<cite>{h(f["chi"])}, {h(f["titolo"])}{self.ref(fid)}</cite></blockquote>')

    def elenco(self, nota=None):
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = FONTI[i]
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. '
                        f'<span class="small">read {giorno(f["letto_il"])}</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2><ol>{"".join(voci)}</ol>'
                + (nota or '<p class="small">Exam counts and percentages are copied from the official publications above; where we add figures up ourselves, the page says so. '
                   'See <a href="/how-we-check/">how we check</a>.</p>') + '</section>')


# ---------------------------------------------------------------- risorse
def _impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:10]


CSS = re.sub(r"\n", "", stile.CSS)
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' + "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in stile.ICONE.items()) + "</svg>\n")
APP_JS = stile.APP_JS.strip() + "\n"
ASSET = {f"site.{_impronta(CSS)}.css": CSS, f"app.{_impronta(APP_JS)}.js": APP_JS,
         f"favicon.{_impronta(stile.FAVICON_SVG)}.svg": stile.FAVICON_SVG, f"icons.{_impronta(SPRITE)}.svg": SPRITE}
CSS_FILE, JS_FILE, FAVICON_FILE, ICONS_FILE = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="32" height="32" alt="">'
LOGO_TESTO = "<span>Real Estate Exam <b>Pass Rates</b></span>"


def ico(nome, cls="ico"):
    if nome not in stile.ICONE:
        raise SystemExit(f"icona sconosciuta: {nome}")
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
TITOLI, DESCRIZIONI = {}, {}
MENU = [("", "All states")] + [(f"{slug(s)}/", st(s)["nome"]) for s in STATI] + [("how-we-check/", "Sources")]
DISCLAIMER = ("<strong>Independent site, not affiliated with any real estate commission, school or exam company.</strong> "
              "The pass rates are copied from official state publications for the period shown. They describe how each school’s past students did on the licensing exam; "
              "they are not a rating of a course and they do not predict your own result. Licensing rules and fees change: confirm them with the commission before you pay for anything.")


def menu_html(percorso, mobile=False):
    return "".join(f'<a href="/{u}"' + (' aria-current="page"' if u == percorso else "") + (' class="w2"' if mobile else "") + f">{h(t)}</a>" for u, t in MENU)


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append(percorso)
        if len(titolo) > 65 or titolo in TITOLI.values():
            raise SystemExit(f"titolo troppo lungo ({len(titolo)}) o doppio: {titolo}")
        if len(descrizione) > 160 or descrizione in DESCRIZIONI.values():
            raise SystemExit(f"descrizione troppo lunga ({len(descrizione)}) o doppia: {descrizione}")
        TITOLI[percorso], DESCRIZIONI[percorso] = titolo, descrizione
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                   "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": f"{URL_SITO}/{p}"} for i, (n, p) in enumerate(briciole, 1)]})
        bc = ('<nav class="briciole" aria-label="Breadcrumb">' + " › ".join([f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    corpo_tr = corpo + MON.riga_trasparenza(corpo, "en")
    f_tassi = "".join(f'<li><a href="/{slug(s)}/">{h(st(s)["nome"])} school pass rates</a></li>' for s in STATI)
    f_lic = "".join(f'<li><a href="/{slug_lic(s)}/">{h(st(s)["nome"])} real estate license</a></li>' for s in STATI)
    guide = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [("", "All states"), ("how-we-check/", "How we check and sources"), ("about/", "About"),
                                                                    ("how-we-check/#corrections", "Report an error"), ("privacy/", "Privacy")])
    testo = f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
<title>{h(titolo)}</title>
<meta name="description" content="{h(descrizione)}">
{f'<link rel="canonical" href="{url_pag}">' if indicizza else '<meta name="robots" content="noindex, follow">'}
<meta property="og:title" content="{h(titolo)}">
<meta property="og:description" content="{h(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#16233B">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}{LOGO_TESTO}</a>
<nav class="menu" aria-label="Main">{menu_html(percorso)}</nav>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Menu">{ico("menu")}</summary><nav aria-label="Main menu">{menu_html(percorso, mobile=True)}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo_tr}
<p class="disclaimer">{DISCLAIMER}</p>
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="/">{LOGO}{LOGO_TESTO}</a>
<p><strong>{NOME}</strong> shows how the students of each real estate school did on the state licensing exam, using only the figures the state real estate commission publishes,
with the number of exams behind every percentage. Independent site, not a government website.</p>
<p>Official sources read on {data_lunga(CONTROLLO)}.</p>
</div><div>
<h2>Pass rates by school</h2><ul>{f_tassi}</ul>
</div><div>
<h2>Getting licensed</h2><ul>{f_lic}</ul>
</div><div>
<h2>Site</h2><ul>{guide}</ul>
</div></div>
<p class="f-base">General information only, not legal or career advice. Not affiliated with the Texas Real Estate Commission, the Alabama Real Estate Commission, the Nebraska Real Estate Commission, the Hawaii Real Estate Commission, or any school or exam company.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, corta=False, icona="chart"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>
</div></section>"""


# ---------------------------------------------------------------- domande frequenti (solo da ricerche misurate)
def volume(frase):
    for r in DOM["ricerche"]:
        if r["frase"] == frase:
            return r["volume_mese"]
    return 0


def faq_blocco(voci, rim):
    """voci: (ricerca misurata, domanda, risposta in testo semplice, fonti)."""
    blocchi, ld = [], []
    for ric, q, a, fonti in voci:
        if volume(ric) <= 0:
            raise SystemExit(f"FAQ senza ricerca misurata: {ric}")
        blocchi.append(f'<div class="faq" data-ricerca="{h(ric)}"><h3>{h(q)}</h3><p>{h(a)}{rim.ref(fonti)}</p></div>')
        ld.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    html_ = ('<h2 id="faq">Common questions</h2><p class="small">Questions people in the United States search for, answered from the official sources.</p>' + "".join(blocchi))
    return html_, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


# ---------------------------------------------------------------- tabella delle scuole
def cella(v):
    """Percentuale come la stampa la fonte, con accanto promossi ed esami; sotto la soglia: «small sample»."""
    if not v["n"]:
        return '<td class="r zero">–<span class="nn">no exams</span></td>'
    poco = v["n"] < SOGLIA
    larg = f"{100 * v['p'] / v['n']:.1f}"
    return (f'<td class="r{" poco" if poco else ""}"><span class="pc">{h(v["pc"])}</span>' + ('<span class="tag-s">small sample</span>' if poco else "")
            + f'<span class="barra" aria-hidden="true"><i style="width:{larg}%"></i></span><span class="nn">{num(v["p"])} of {num(v["n"])} passed</span></td>')


def sotto_nome(s, x):
    pezzi = []
    if x.get("citta"):
        pezzi.append(x["citta"])
    if s == "AL" and x.get("formati"):
        pezzi.append(" and ".join(x["formati"]).lower() if len(x["formati"]) > 1 else x["formati"][0])
    if s in ("NE", "HI"):
        pezzi.append(f"school code {x['codice']}")
    if x.get("solo_broker"):
        pezzi.append("broker exams only this quarter")
    return f"<small>{h(' · '.join(pezzi))}</small>" if pezzi else ""


def tabella_scuole(s, rim):
    d, mis = st(s), MISURE[s]
    prim = mis[0][0]
    intest = "".join(f'<th scope="col"><button type="button" class="ord" data-ord="r:{k}" aria-pressed="false">{h(et)}</button></th>' for k, et, _ in mis)
    tot = d["totale"]
    if tot["origine"] == "ufficiale":
        nome_tot = {"TX": "All providers in the table (official row)", "HI": "All salesperson exams (official total)"}[s]
        celle_tot = "".join(cella(tot[k]) for k, _, _ in mis)
    else:
        nome_tot = f"All {len(d['scuole'])} schools (our sum of the rows)"
        celle_tot = "".join(cella({"n": tot[k]["n"], "p": tot[k]["p"], "pc": pct1(tot[k]["p"], tot[k]["n"])}) for k, _, _ in mis)
    righe = [f'<tr class="tot-riga"><th scope="row">{h(nome_tot)}</th>{celle_tot}</tr>']
    for x in d["scuole"]:
        attr = "".join(f' data-n-{k}="{x[k]["n"]}" data-p-{k}="{x[k]["p"]}"' for k, _, _ in mis)
        righe.append(f'<tr data-nome="{h(x["nome"].lower())}" data-formati="{h(" ".join(x.get("formati", [])))}"{attr}><th scope="row">{h(x["nome"])}{sotto_nome(s, x)}</th>'
                     + "".join(cella(x[k]) for k, _, _ in mis) + "</tr>")
    opzioni = '<option value="n">Most exams first</option>' + "".join(f'<option value="r:{k}">Pass rate: {h(et.lower())}</option>' for k, et, _ in mis) + '<option value="nome">School name (A to Z)</option>'
    formato = ""
    if s in ("AL", "HI"):
        formato = '<label>Format<select data-formato><option value="">Classroom and online</option><option value="Online">Online</option><option value="Classroom">Classroom</option></select></label>'
    strumenti = (f'<div class="card strumenti" data-strumenti hidden><label>Find a school<input type="search" data-cerca placeholder="School name" autocomplete="off"></label>'
                 f'<label>Sort by<select data-ordina>{opzioni}</select></label>{formato}'
                 f'<label class="check"><input type="checkbox" data-min>Only schools with at least {SOGLIA} exams</label>'
                 '<p class="stato-t" data-stato aria-live="polite"></p></div>')
    cap = {"TX": f"Texas sales agent licensing exam, first attempts, by education provider. Period: {periodo(s)}.",
           "AL": f"Alabama salesperson licensing exam by school: first attempts and all attempts including retakes. Period: {periodo(s)} (read {giorno(d['letto_il'])}).",
           "NE": f"Nebraska salesperson licensing exam by school, national and state parts: first-time takers and all takers. Period: {periodo(s)}.",
           "HI": f"Hawaii salesperson licensing exam by school, national and state parts: all exams taken. Period: {periodo(s)}."}[s]
    return (f'<div data-tabella data-soglia="{SOGLIA}" data-primaria="{prim}">{strumenti}'
            f'<div class="tab"><table class="dati tassi"><caption><span>{h(cap)} Each cell: the percentage printed by the commission, then passed exams out of exams taken.{rim.ref(d["fonte"])}</span></caption>'
            f'<thead><tr><th scope="col"><button type="button" class="ord" data-ord="nome" aria-pressed="false">School</button></th>{intest}</tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table><p class="vuoto" data-vuoto hidden>No school matches. Clear the search box or the filters.</p></div></div>')


# ---------------------------------------------------------------- riquadro del partner (spento finché non c'è il link vero)
def partner_attivi():
    attivi = []
    for p in AFF["partner"]:
        link = (p.get("link") or "").strip()
        if not p.get("attivo"):
            if link:
                raise SystemExit(f"affiliati.json: {p['id']} è spento ma ha un link: toglierlo o accendere il partner")
            continue
        u = urlparse(link)
        if u.scheme != "https" or not u.hostname or not MON.dominio_ammesso(link):
            raise SystemExit(f"affiliati.json: {p['id']} acceso senza un link https su un dominio ammesso (monetizzazione.json, domini_affiliazione)")
        for s in p["stati"]:
            if s not in STATI or p["nome_tabella"].get(s) not in [x["nome"] for x in st(s)["scuole"]]:
                raise SystemExit(f"affiliati.json: {p['id']} non è nella tabella ufficiale di {s}: il riquadro esce solo dove la sua percentuale è visibile")
        attivi.append(p)
    return attivi


PARTNER = partner_attivi()


def riquadro_partner(s):
    qui = [p for p in PARTNER if s in p["stati"]]
    if not qui:
        return ""
    r = AFF["riquadro"]
    voci = "".join(f'<li><b>{h(p["nome"])}</b><p>Listed in the official table above as “{h(p["nome_tabella"][s])}”.</p>'
                   f'<a class="btn" href="{h(p["link"])}" rel="sponsored nofollow noopener">{h(p["pulsante"])}{ico("arrow")}</a></li>' for p in qui)
    return (f'<aside class="partner" data-partner aria-label="Advertisement"><p class="tag">{h(r["etichetta"])}</p><h3>{h(r["titolo"])}</h3><p>{h(r["testo"])}</p>'
            f'<ul class="partner-l">{voci}</ul><p class="small">{h(r["trasparenza"])}</p></aside>')


# ---------------------------------------------------------------- testi per Stato: tassi
def fatti(voci, sotto):
    return ('<div class="card fatti pull">' + "".join(f'<div class="fatto{" main" if i == 0 else ""}"><b>{b}</b><span>{h(t)}</span></div>' for i, (b, t) in enumerate(voci))
            + f'<p class="asof">{sotto}</p></div>')


def leggere_tx(rim):
    d = st("TX")
    mpr = f"{float(d['mpr']):.2f}%"
    return ('<h2 id="read">How to read the Texas figures</h2><div class="testo">'
            + rim.t(f'<p>The Texas Real Estate Commission (TREC) counts <strong>first attempts only</strong>: retakes are not in these figures, and TREC does not publish a pass rate that includes them.[[tx_pagina]]</p>')
            + rim.cit("tx_pagina", "sales")
            + '<p>A student’s result goes to the school where they took most of their courses:</p>' + rim.cit("tx_pagina", "affiliazione")
            + rim.t(f'<p>The top row is TREC’s own total: {num(d["totale"]["first"]["n"])} first-attempt sales agent exams, {num(d["totale"]["first"]["p"])} passed, {h(d["totale"]["first"]["pc"])}. '
                    f'The {len(d["scuole"])} providers in the table add up to exactly those numbers.[[tx_tassi]]</p>'
                    f'<p>TREC also uses pass rates to supervise schools. It compares each provider’s overall rate (sales agent and broker exams together, {h(d["complessivo_pc"])} for all providers) with a minimum, which works out at {mpr} for this period:[[tx_tassi]]</p>')
            + rim.cit("tx_pagina", "mpr") + rim.cit("tx_pagina", "standing")
            + rim.t('<p>This page shows the sales agent exam only. Broker exam figures and each provider’s standing against the minimum are on the official page.[[tx_pagina]] '
                    'Some providers register their name with exclamation marks around it; we show the name without them and change nothing else.</p></div>'))


def leggere_al(rim):
    d = st("AL")
    senza = sum(1 for x in d["scuole"] if not x["first"]["n"])
    t = d["totale"]
    return ('<h2 id="read">How to read the Alabama figures</h2><div class="testo">'
            + rim.t('<p>The Alabama Real Estate Commission (AREC) publishes two figures for each school: students who passed on their <strong>first attempt</strong>, and <strong>all attempts</strong> including retakes.[[al_tassi]]</p>')
            + rim.cit("al_tassi", "definizione")
            + '<p>The commission’s page does not print start and end dates. It describes the period like this:</p>' + rim.cit("al_tassi", "periodo")
            + rim.t(f'<p>We read the page on {giorno(d["letto_il"])}. It lists {len(d["scuole"])} approved schools; {senza} of them had no first-attempt salesperson exams in the period and show a dash. '
                    f'The commission prints no statewide total, so the top row is <strong>our sum of the school rows</strong>: {num(t["first"]["p"])} of {num(t["first"]["n"])} first attempts passed ({pct1(t["first"]["p"], t["first"]["n"])}), '
                    f'and {num(t["all"]["p"])} of {num(t["all"]["n"])} of all attempts ({pct1(t["all"]["p"], t["all"]["n"])}).[[al_tassi]]</p>'
                    '<p>The “all attempts” rate is usually lower than the first-attempt rate, because people who fail and try again are counted each time. '
                    'City and format (classroom or online) are the ones on the commission’s page. This page shows the salesperson exam; broker exam figures are on the official page.</p></div>'))


def leggere_ne(rim):
    d = st("NE")
    L = LIC["NE"]
    t = d["totale"]
    return ('<h2 id="read">How to read the Nebraska figures</h2><div class="testo">'
            + rim.t(f'<p>The Nebraska Real Estate Commission (NREC) publishes a report for each quarter. This page shows the latest one we could read, {periodo("NE")}.[[ne_tassi]] '
                    'The exam has two parts, national and state, and the report counts them separately, for first-time takers and for everyone (first-time takers plus repeaters).</p>')
            + rim.cit("ne_indice", "cosa")
            + rim.t(f'<p>The pass mark is {L["soglia_nazionale"][0]} correct answers out of {L["soglia_nazionale"][1]} on the national part and {L["soglia_statale"][0]} out of {L["soglia_statale"][1]} on the state part.[[ne_indice]]</p>')
            + '<p><strong>One quarter in Nebraska is a small number of exams.</strong> The commission says so itself:</p>' + rim.cit("ne_indice", "cautela") + rim.cit("ne_indice", "piccoli")
            + rim.t(f'<p>In this quarter only {sum(1 for x in d["scuole"] if x["national_first"]["n"] >= SOGLIA)} of the {len(d["scuole"])} schools had {SOGLIA} or more first-time takers on the national part. '
                    f'The report we read has no statewide row, so the top row is <strong>our sum of the school rows</strong>: first-time takers passed {num(t["national_first"]["p"])} of {num(t["national_first"]["n"])} national parts '
                    f'({pct1(t["national_first"]["p"], t["national_first"]["n"])}) and {num(t["state_first"]["p"])} of {num(t["state_first"]["n"])} state parts ({pct1(t["state_first"]["p"], t["state_first"]["n"])}).[[ne_tassi]]</p>'
                    '<p>The official report is a scanned document: we typed its figures by hand and checked that every row adds up (passed plus failed equals graded, first-time takers plus repeaters equals the total, the percentages match). '
                    'It shows whole percentages. Broker exam rows are in the official report; a school with broker exams only is marked.</p></div>'))


def leggere_hi(rim):
    d = st("HI")
    altri = d["non_scuole"]
    n_altri = sum(x["national"]["n"] for x in altri)
    return ('<h2 id="read">How to read the Hawaii figures</h2><div class="testo">'
            + rim.t(f'<p>The Hawaii Real Estate Commission publishes pass and fail counts by prelicense school in its quarterly “School Files” bulletin. This page uses the one-year table of the October 2026 issue: {periodo("HI")}.[[hi_tassi]]</p>'
                    '<p>The exam has a national part and a state part, counted separately. The bulletin counts <strong>exams taken</strong> (“Tested”, “Passed”, “Failed”): it does not separate first attempts from retakes, '
                    'so these rates cannot be compared with first-attempt rates in other states.</p>'
                    f'<p>The top row is the bulletin’s own total for all salesperson exams: {num(d["totale"]["national"]["p"])} of {num(d["totale"]["national"]["n"])} national parts passed ({h(d["totale"]["national"]["pc"])}) '
                    f'and {num(d["totale"]["state"]["p"])} of {num(d["totale"]["state"]["n"])} state parts ({h(d["totale"]["state"]["pc"])}). '
                    f'That total also includes {num(n_altri)} national-part exams by candidates who are not attributed to a school (prelicense equivalency, uniform-section equivalency, license restoration, unknown school); those rows are not in the table below.[[hi_tassi]]</p>'
                    '<p>The bulletin cuts percentages to one decimal instead of rounding (4 passed out of 6 is printed as 66.6%); we show them as printed. '
                    'Some schools appear twice, once for classroom and once for online courses, with different school codes: the code is under each name. Broker exam tables and the latest quarter alone are in the bulletin.</p></div>'))


LEGGERE = {"TX": leggere_tx, "AL": leggere_al, "NE": leggere_ne, "HI": leggere_hi}


def faq_tassi(s):
    d, L = st(s), LIC[s]
    n = d["nome"].lower()
    prim = MISURE[s][0][0]
    grandi = sorted((x for x in d["scuole"] if x[prim]["n"] >= SOGLIA), key=lambda x: -x[prim]["n"])
    if s == "TX":
        tot = d["totale"]["first"]
        return [
            ("texas real estate exam pass rate", "What is the pass rate for the Texas real estate exam?",
             f"On the sales agent exam, {tot['pc']} of first attempts passed between {periodo(s)}: {num(tot['p'])} of {num(tot['n'])}. That is the Texas Real Estate Commission's own figure for all education providers together.", "tx_tassi"),
            ("how hard is the texas real estate exam", "How hard is the Texas real estate exam?",
             f"The official numbers give an idea: {tot['pc']} of first attempts at the sales agent exam passed in the period covered, so a little under half did not pass the first time. If you fail either part three times, TREC requires more education before you can test again.", "tx_tassi,tx_licenza"),
            ("online real estate school texas", "Which online real estate schools are in the Texas table?",
             f"TREC's table does not say whether a provider teaches online or in a classroom. It lists {len(d['scuole'])} providers with their first-attempt results; the ones with the most exams in the period are {grandi[0]['nome']} ({num(grandi[0]['first']['n'])} exams, {grandi[0]['first']['pc']}), {grandi[1]['nome']} ({num(grandi[1]['first']['n'])}, {grandi[1]['first']['pc']}) and {grandi[2]['nome']} ({num(grandi[2]['first']['n'])}, {grandi[2]['first']['pc']}).", "tx_tassi"),
            ("trec pass rates", "Where does TREC publish school pass rates?",
             "On its page “Provider Exam Passage Rates for Sales Agents and Brokers”, which loads a data file from the same website. The figures here are copied from that file, with the period and the number of exams next to each rate.", "tx_pagina,tx_tassi"),
        ]
    if s == "AL":
        t = d["totale"]
        return [
            ("alabama real estate exam", "What is the pass rate for the Alabama real estate exam?",
             f"The commission publishes rates by school, not a statewide rate. Adding up the school figures for the previous 12 months, {num(t['first']['p'])} of {num(t['first']['n'])} first attempts at the salesperson exam passed ({pct1(t['first']['p'], t['first']['n'])}), and {num(t['all']['p'])} of {num(t['all']['n'])} of all attempts including retakes ({pct1(t['all']['p'], t['all']['n'])}). The sums are ours.", "al_tassi"),
            ("how hard is the alabama real estate exam", "How hard is the Alabama real estate exam?",
             f"Going by the commission's school figures, about {pct1(t['first']['p'], t['first']['n']).split('.')[0]} in 100 first attempts at the salesperson exam passed in the previous 12 months. You have {L['mesi_esame']} months after finishing the prelicense course to pass; after that the course must be retaken.", "al_tassi,al_licenza"),
            ("real estate classes alabama", "How do I compare real estate classes in Alabama?",
             f"The commission lists {len(d['scuole'])} approved schools with their exam results, city and format (classroom or online). In the table you can filter by format and see, next to each rate, how many students it is based on. Only {len(grandi)} schools had {SOGLIA} or more first-attempt exams in the period.", "al_tassi"),
        ]
    if s == "NE":
        t = d["totale"]
        return [
            ("nebraska real estate exam pass rate", "What is the pass rate for the Nebraska real estate exam?",
             f"In the quarter {periodo(s)}, first-time takers passed {num(t['national_first']['p'])} of {num(t['national_first']['n'])} national parts of the salesperson exam ({pct1(t['national_first']['p'], t['national_first']['n'])}) and {num(t['state_first']['p'])} of {num(t['state_first']['n'])} state parts ({pct1(t['state_first']['p'], t['state_first']['n'])}). These are our sums of the school rows in the commission's report.", "ne_tassi"),
            ("nebraska real estate exam", "How many questions do you need to pass the Nebraska real estate exam?",
             f"The commission says the number of correct answers needed is {L['soglia_nazionale'][0]} out of {L['soglia_nazionale'][1]} on the national part and {L['soglia_statale'][0]} out of {L['soglia_statale'][1]} on the state part. The exam is given by Pearson.", "ne_indice,ne_esame"),
            ("real estate classes nebraska", "How do I compare real estate classes in Nebraska?",
             f"The commission's quarterly report lists {len(d['scuole'])} schools with exam results. Most have very few students in a quarter: only {len(grandi)} had {SOGLIA} or more first-time takers. The commission itself warns that percentages say little when the number of students is small.", "ne_tassi,ne_indice"),
        ]
    t = d["totale"]
    return [
        ("hawaii real estate exam", "What is the pass rate for the Hawaii real estate exam?",
         f"Between {periodo(s)}, {t['national']['pc']} of the national parts of the salesperson exam were passed ({num(t['national']['p'])} of {num(t['national']['n'])}) and {t['state']['pc']} of the state parts ({num(t['state']['p'])} of {num(t['state']['n'])}). The commission's bulletin counts all exams taken, retakes included.", "hi_tassi"),
        ("real estate classes hawaii", "How do I compare real estate classes in Hawaii?",
         f"The commission's School Files bulletin lists {len(d['scuole'])} prelicense school codes with exams taken and passed, classroom and online courses separately. Only {len(grandi)} of them had {SOGLIA} or more national-part exams in the year; for the others one or two results change the percentage a lot.", "hi_tassi"),
        ("hawaii real estate license", "Does the Hawaii commission publish first-attempt pass rates?",
         "No. Its bulletin counts exams tested, passed and failed for each school, without separating first attempts from retakes. That is why the Hawaii percentages look low next to first-attempt rates from other states: the two are not the same measure.", "hi_tassi"),
    ]


def pagina_stato(s):
    rim = Rimandi()
    d, mis = st(s), MISURE[s]
    nome, prim = d["nome"], mis[0][0]
    tot = d["totale"][prim]
    con_esami = sum(1 for x in d["scuole"] if x[prim]["n"])
    n_sopra = sum(1 for x in d["scuole"] if x[prim]["n"] >= SOGLIA)
    etich = {"TX": "first attempts passed (sales agent exam)", "AL": "first attempts passed (salesperson exam, our sum)", "NE": "first-time takers passed the national part (our sum)", "HI": "national parts passed (all exams taken)"}[s]
    voci = [(h(tasso_stato(s, prim)), etich), (num(tot["n"]), "exams behind that rate"), (str(len(d["scuole"])), "schools in the official table" + (f", {con_esami} with exams" if con_esami != len(d["scuole"]) else "")),
            (str(n_sopra), f"school{'' if n_sopra == 1 else 's'} with {SOGLIA} or more exams")]
    sotto = f'{ico("info")} Period covered: <strong>{h(periodo(s))}</strong> · official source read on {giorno(d["letto_il"])}{rim.ref(d["fonte"])}'
    corpo = fatti(voci, sotto)
    intro = {"TX": "Every education provider in the Texas Real Estate Commission’s table, with its first-attempt results on the sales agent exam.",
             "AL": "Every school on the Alabama Real Estate Commission’s list, with first-attempt and all-attempt results on the salesperson exam.",
             "NE": "Every school in the Nebraska Real Estate Commission’s latest quarterly report, with the national and state parts of the salesperson exam.",
             "HI": "Every prelicense school in the Hawaii Real Estate Commission’s bulletin, with the national and state parts of the salesperson exam."}[s]
    corpo += (f'<h2 id="schools">{h(nome)} pass rates by school</h2><div class="testo"><p>{intro} The table starts with the schools that had the most exams. '
              f'You can sort by pass rate: schools with fewer than {SOGLIA} exams are then listed after the others, because one or two results move their percentage a lot.</p></div>')
    corpo += tabella_scuole(s, rim)
    corpo += (f'<div class="nota"><svg class="ico" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-alert"/></svg>'
              f'<p><strong>A pass rate is not a rating of a school.</strong> It shows how that school’s past students did on the exam. Schools enroll different students, '
              f'and with few exams the percentage is mostly chance. We publish the official figures as they are and do not rank or recommend schools.</p></div>')
    corpo += riquadro_partner(s)
    corpo += LEGGERE[s](rim)
    L = LIC[s]
    corpo += (f'<h2 id="license">Getting a {h(nome)} real estate license</h2><div class="testo"><p>Before the exam you need {L["ore"]} hours of approved pre-licensing education and you must be at least {L["eta"]} years old. '
              f'The steps, deadlines and official fees are on a separate page.</p><p class="azioni"><a class="btn" href="/{slug_lic(s)}/">{h(nome)} real estate license: steps and fees{ico("arrow")}</a></p></div>')
    faq_html, faq_ld = faq_blocco(faq_tassi(s), rim)
    corpo += faq_html
    altri = "".join(f'<li><a href="/{slug(o)}/"><b>{h(st(o)["nome"])}</b><small>{len(st(o)["scuole"])} schools</small></a></li>' for o in STATI if o != s)
    corpo += f'<h2>Other states</h2><ul class="griglia larga">{altri}</ul>'
    corpo += rim.elenco()
    eyebrow = f'{nome} · official {d["sigla"]} data' if s != "HI" else "Hawaii · official commission data"
    sub = {"TX": f"First-attempt pass rates on the Texas sales agent exam for the {len(d['scuole'])} education providers in TREC’s table, with the number of exams behind every percentage.",
           "AL": f"First-attempt and overall pass rates on the Alabama salesperson exam for the {len(d['scuole'])} schools on the commission’s list, with the number of students behind every percentage.",
           "NE": f"Pass rates on the Nebraska salesperson exam for the {len(d['scuole'])} schools in the commission’s latest quarterly report: first-time takers and all takers, national and state parts.",
           "HI": f"Pass rates on the Hawaii salesperson exam for the {len(d['scuole'])} prelicense school codes in the commission’s bulletin, national and state parts, with the number of exams."}[s]
    testata = banda(eyebrow, f"{nome} real estate school pass rates", h(sub), icona="chart")
    titolo = f"{nome} Real Estate School Pass Rates: Official {d['sigla']} Data" if s != "HI" else "Hawaii Real Estate School Pass Rates: Official Data"
    descr = {"TX": f"Texas real estate exam pass rates by school from TREC: {len(d['scuole'])} providers, first attempts, {periodo(s, True)}, with the number of exams.",
             "AL": f"Alabama real estate exam pass rates by school from the commission: {len(d['scuole'])} schools, first attempt and all attempts, with the number of students.",
             "NE": f"Nebraska real estate exam pass rates by school from the commission’s quarterly report: first-time and all takers, national and state parts.",
             "HI": f"Hawaii real estate exam pass rates by prelicense school from the commission’s bulletin: national and state parts, exams taken and passed."}[s]
    ld = [faq_ld, {"@context": "https://schema.org", "@type": "Dataset", "name": f"{nome} real estate licensing exam pass rates by school",
                   "description": f"Exams taken and passed by school on the {nome} real estate {d['titolo_licenza']} licensing exam, copied from the {d['ente']}. Period: {periodo(s)}.",
                   "url": f"{URL_SITO}/{slug(s)}/", "isBasedOn": FONTI[d["fonte"]]["url"], "creator": {"@type": "Organization", "name": NOME},
                   "spatialCoverage": nome, "dateModified": d["letto_il"], "isAccessibleForFree": True}]
    pagina(f"{slug(s)}/", titolo, descr, corpo, testata, briciole=[("Home", ""), (f"{nome} pass rates", f"{slug(s)}/")], jsonld=ld)


# ---------------------------------------------------------------- testi per Stato: licenza
def kv(righe):
    return '<div class="card piena"><table class="kv"><tbody>' + "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td></tr>" for a, b in righe) + "</tbody></table></div>"


def licenza_tx(rim):
    L = LIC["TX"]
    d = L["domanda"]
    somma = d["totale"] + L["esame"] + L["impronte"]
    corsi = ", ".join(f'{c["nome"]} ({c["ore"]} hours)' for c in L["corsi"])
    passi = ('<h2 id="steps">The steps, in TREC’s order</h2><ol class="steps">'
             + rim.t(f'<li><strong>Check that you qualify.</strong> You must be a citizen of the United States or a lawfully admitted alien, at least {L["eta"]} years old, and meet TREC’s standards of honesty, trustworthiness and integrity.[[tx_licenza]]</li>'
                     '<li><strong>Register for a REALM Portal account.</strong> It gives you the pre-license education application number that your school needs.[[tx_licenza]]</li>'
                     f'<li><strong>Complete {L["ore"]} classroom hours</strong> of qualifying courses with a TREC-approved provider: {h(corsi)}.[[tx_licenza]]</li>'
                     f'<li><strong>Apply online and pay the fee</strong> ({usd(d["totale"])} in all) in the REALM Portal, after your courses are finished and uploaded.[[tx_licenza,tx_tariffe]]</li>'
                     f'<li><strong>Have your fingerprints taken</strong> and pass the background check ({usd(L["impronte"])}, paid to the fingerprint company, if you were never fingerprinted for TREC).[[tx_licenza,tx_tariffe]]</li>'
                     f'<li><strong>Pass the exam</strong>, given by Pearson ({usd(L["esame"])}, paid to the exam provider).[[tx_licenza,tx_tariffe]]</li>'
                     '<li><strong>Find a sponsoring broker.</strong> Your license is issued inactive and becomes active when a broker sponsors you.[[tx_licenza]]</li></ol>'))
    testo = (passi + '<h2>What TREC says, word for word</h2>' + rim.cit("tx_licenza", "ore") + rim.cit("tx_licenza", "prima") + rim.cit("tx_licenza", "anno")
             + rim.cit("tx_licenza", "impronte") + rim.cit("tx_licenza", "pearson") + rim.cit("tx_licenza", "tre") + rim.cit("tx_licenza", "inattiva"))
    tariffe = ('<h2 id="fees">Official fees</h2><div class="testo">' + rim.t(f'<p>From TREC’s fee schedule, effective {h(L["in_vigore"])}.[[tx_tariffe]]</p>') + "</div>"
               + kv([("Sales agent original application", f'<b>{usd(d["totale"])}</b><small>{usd(d["tassa"])} fee + {usd(d["texas_online"])} Texas Online fee + {usd(d["centro_ricerca"])} Texas A&amp;M Research Center + {usd(d["fondo"])} Real Estate Recovery fee</small>'),
                     ("Real estate sales examination", f'<b>{usd(L["esame"])}</b><small>paid to the exam provider</small>'),
                     ("Fingerprints", f'<b>{usd(L["impronte"])}</b><small>paid to the fingerprint company, if not already fingerprinted for TREC</small>'),
                     ("Total of these three", f'<b>{usd(somma)}</b><small>our sum; the price of the {L["ore"]}-hour courses is set by each school and is not included</small>')])
             + rim.cit("tx_licenza", "tasse"))
    fatti_ = [(f'{L["ore"]} hours', "of qualifying courses"), (usd(somma), "application, exam and fingerprints (our sum)"), (str(L["eta"]), "minimum age"), ("Pearson", "gives the exam")]
    non = ('<li>How many questions the exam has and the passing score: they are in the exam company’s candidate handbook, which we did not use as a source.</li>'
           '<li>The price of the courses: each provider sets its own.</li><li>Renewal and continuing education after the first license.</li>')
    faq = [
        ("texas real estate license requirements", "What are the requirements for a Texas real estate license?",
         f"You must be at least {L['eta']}, a U.S. citizen or lawfully admitted alien, and meet TREC's standards of honesty, trustworthiness and integrity. You need {L['ore']} classroom hours of qualifying courses, a fingerprint background check, a pass on the exam and a sponsoring broker to be active.", "tx_licenza"),
        ("texas real estate license cost", "How much does a Texas real estate license cost?",
         f"The official fees add up to {usd(somma)}: {usd(d['totale'])} for the application, {usd(L['esame'])} for the exam and {usd(L['impronte'])} for fingerprints, under the fee schedule effective {L['in_vigore']}. The price of the {L['ore']} hours of courses is on top and depends on the school.", "tx_tariffe"),
        ("texas real estate license online", "Can I get a Texas real estate license online?",
         "The application is filed online in TREC's REALM Portal, and TREC's table of approved providers includes schools that teach online. Fingerprints are taken in person, and the exam is given by Pearson.", "tx_licenza"),
        ("how to become a real estate agent in texas", "How do I become a real estate agent in Texas?",
         f"In TREC's order: register in the REALM Portal, complete {L['ore']} hours of qualifying courses, apply and pay the fee, have your fingerprints taken, pass the exam and find a sponsoring broker. The application expires one year after it is filed.", "tx_licenza"),
        ("trec fingerprinting", "Do I need fingerprints for a TREC license?",
         f"Yes. TREC says you are required by law to have fingerprints on file with the Texas Department of Public Safety so that a background check can be done; fingerprints on file for other agencies are not accepted. The fee is {usd(L['impronte'])}.", "tx_licenza,tx_tariffe"),
    ]
    return fatti_, testo + tariffe, non, faq


def licenza_al(rim):
    L = LIC["AL"]
    passi = ('<h2 id="steps">The steps</h2><ol class="steps">'
             + rim.t(f'<li><strong>Check that you qualify.</strong> You must be at least {L["eta"]}, a U.S. citizen, permanent resident alien or legally present in the U.S., a resident of any U.S. state, and a high school graduate or the equivalent. '
                     'A felony or a crime involving moral turpitude, or a real estate license rejected or revoked in any state in the past two years, stands in the way.[[al_licenza]]</li>'
                     f'<li><strong>Complete the {L["ore"]} clock hour prelicense course</strong> with an approved school.[[al_licenza]]</li>'
                     f'<li><strong>Pass the exam within {L["mesi_esame"]} months</strong> of finishing the course. The exam is scheduled with Pearson.[[al_licenza,al_esame]]</li>'
                     f'<li><strong>Apply within {L["giorni_domanda"]} days of the exam date</strong>, with the fees, and have your fingerprints taken for the background check.[[al_domanda]]</li>'
                     f'<li><strong>Complete the {L["ore_post"]} hour post license course</strong> within the first twelve months to receive the original (permanent) license.[[al_licenza]]</li></ol>'))
    testo = (passi + '<h2>What the commission says, word for word</h2>' + rim.cit("al_licenza", "ore") + rim.cit("al_licenza", "post") + rim.cit("al_domanda", "novanta") + rim.cit("al_domanda", "nullo")
             + rim.cit("al_domanda", "impronte") + rim.cit("al_esame", "pearson"))
    tariffe = ('<h2 id="fees">Official fees</h2><div class="testo"><p>The commission’s pages that we read do not print the license fee or the exam fee. They say:</p></div>'
               + rim.cit("al_domanda", "tariffe")
               + '<div class="testo"><p>So we do not give a figure here. The fee is on the license application you receive after passing the exam; the exam fee is on the exam company’s site.</p></div>')
    fatti_ = [(f'{L["ore"]} hours', "prelicense course"), (f'{L["mesi_esame"]} months', "to pass the exam after the course"), (f'{L["giorni_domanda"]} days', "to apply after the exam"), (str(L["eta"]), "minimum age")]
    non = ('<li>The license fee and the exam fee (see above).</li><li>How many questions the exam has and the passing score.</li>'
           '<li>The rules for people already licensed in another state (reciprocal license) are on the commission’s page and not repeated here.</li>')
    faq = [
        ("alabama real estate license requirements", "What are the requirements for an Alabama real estate license?",
         f"For a salesperson license: be at least {L['eta']}, a U.S. citizen, permanent resident alien or legally present in the U.S., a resident of any U.S. state and a high school graduate or equivalent; complete an approved {L['ore']} clock hour prelicense course; pass the exam; and apply with a fingerprint background check.", "al_licenza,al_domanda"),
        ("how to get a real estate license in alabama", "How do I get a real estate license in Alabama?",
         f"Complete the {L['ore']}-hour prelicense course, pass the exam within {L['mesi_esame']} months of finishing it, and send the complete application with fees within {L['giorni_domanda']} days of your exam date. Then complete the {L['ore_post']}-hour post license course within the first twelve months.", "al_licenza,al_domanda"),
        ("alabama real estate license cost", "How much does an Alabama real estate license cost?",
         "The commission's pages we read do not print the amount: they say fees vary with the license type and refer you to the license application. We do not publish a figure we could not read in an official source.", "al_domanda"),
        ("alabama real estate license online", "Can I take the Alabama prelicense course online?",
         "The commission's list of schools marks each one as classroom, online or both, and several approved schools are online. The application itself must be mailed or delivered to the commission's office, according to its instructions.", "al_tassi,al_domanda"),
        ("how to become a real estate agent in alabama", "How long do I have to pass the Alabama exam after the course?",
         f"{L['mesi_esame']} months. The commission says applicants have {L['mesi_esame']} months to pass the state exam after completing the course, and if the deadline is not met the course must be retaken.", "al_licenza"),
    ]
    return fatti_, testo + tariffe, non, faq


def licenza_ne(rim):
    L = LIC["NE"]
    somma = L["domanda"] + L["esame"] + L["licenza"]
    passi = ('<h2 id="steps">The steps, from the commission’s checklist</h2><ol class="steps">'
             + rim.t(f'<li><strong>Check the basics.</strong> At least {L["eta"]} years old, a high school diploma or equivalent, legally eligible to work in the U.S.[[ne_licenza]]</li>'
                     f'<li><strong>Complete {L["ore"]} hours of education</strong>: {L["ore_corsi"]} clock hours of approved pre-license courses (three 30-hour courses) and the {L["ore_standard"]}-hour Professional Practice Standards course.[[ne_licenza]]</li>'
                     f'<li><strong>Submit the application</strong> with the application fee ({usd(L["domanda"])}) and the examination fee ({usd(L["esame"])} per exam).[[ne_licenza,ne_tariffe]]</li>'
                     '<li><strong>Fingerprints and criminal history check.</strong>[[ne_licenza]]</li>'
                     f'<li><strong>Pass the exam</strong>, scheduled with Pearson. You need {L["soglia_nazionale"][0]} of {L["soglia_nazionale"][1]} on the national part and {L["soglia_statale"][0]} of {L["soglia_statale"][1]} on the state part.[[ne_esame,ne_indice]]</li>'
                     '<li><strong>Buy errors and omissions insurance and find a designated broker.</strong>[[ne_licenza]]</li>'
                     f'<li><strong>Send the license issuance form and fee</strong> ({usd(L["licenza"])}) within 30 days of passing.[[ne_licenza,ne_tariffe]]</li></ol>'))
    testo = (passi + '<h2>What the commission says, word for word</h2>' + rim.cit("ne_licenza", "ore") + rim.cit("ne_licenza", "tempi") + rim.cit("ne_licenza", "trenta") + rim.cit("ne_licenza", "valida")
             + rim.cit("ne_esame", "pearson") + rim.cit("ne_esame", "ripetere") + rim.cit("ne_esame", "tassa"))
    tariffe = ('<h2 id="fees">Official fees</h2><div class="testo">' + rim.t('<p>From the commission’s fee schedule, updated January 2026.[[ne_tariffe]]</p>') + "</div>"
               + kv([("License application, salespersons and brokers", f'<b>{usd(L["domanda"])}</b>'),
                     ("License examination, per exam", f'<b>{usd(L["esame"])}</b><small>a retake within one year of application costs {usd(L["ripetizione"])}</small>'),
                     ("Salesperson original license (current year only)", f'<b>{usd(L["licenza"])}</b>'),
                     ("Total of these three", f'<b>{usd(somma)}</b><small>our sum; courses, fingerprints and insurance are not included</small>'),
                     ("Salesperson renewal, 2 years", f'<b>{usd(L["rinnovo"])}</b>')]))
    fatti_ = [(f'{L["ore"]} hours', "of education in all"), (usd(somma), "application, exam and license (our sum)"), (str(L["eta"]), "minimum age"), ("Pearson", "gives the exam")]
    non = ('<li>The cost of fingerprints and of errors and omissions insurance.</li><li>The price of the courses: each school sets its own.</li>'
           '<li>The rules for people licensed in another state (license recognition) are in a separate commission document.</li>')
    faq = [
        ("nebraska real estate license", "What do I need for a Nebraska real estate license?",
         f"To be at least {L['eta']} with a high school diploma or equivalent, {L['ore']} hours of education ({L['ore_corsi']} hours of approved pre-license courses plus the {L['ore_standard']}-hour Professional Practice Standards course), a criminal history check, a pass on both parts of the exam, errors and omissions insurance and a designated broker.", "ne_licenza"),
        ("how to get a real estate license in nebraska", "How long does it take to get a real estate license in Nebraska?",
         "The commission says the typical application process takes approximately 4 to 8 weeks, not counting the time you need for the courses. Your application and background report are valid for one year from the date the application is received.", "ne_licenza"),
        ("nebraska real estate license requirements", "How many hours of classes does Nebraska require?",
         f"{L['ore']} hours in total: three approved 30-hour pre-license courses ({L['ore_corsi']} clock hours) and the {L['ore_standard']}-hour Professional Practice Standards course.", "ne_licenza"),
        ("real estate license nebraska", "How much does a Nebraska real estate license cost?",
         f"The commission's fee schedule lists {usd(L['domanda'])} for the license application, {usd(L['esame'])} for each examination and {usd(L['licenza'])} for the salesperson original license: {usd(somma)} in all, before courses, fingerprints and insurance.", "ne_tariffe"),
        ("how to become a real estate agent in nebraska", "Can I retake the Nebraska real estate exam?",
         f"Yes. The commission says applicants may retake the examination multiple times during their eligibility period, and that an appointment and a fee are required for each retake ({usd(L['ripetizione'])} within one year of application).", "ne_esame,ne_tariffe"),
    ]
    return fatti_, testo + tariffe, non, faq


def licenza_hi(rim):
    L = LIC["HI"]
    anno = CONTROLLO.year
    questa = L["licenza_pari"] if anno % 2 == 0 else L["licenza_dispari"]
    passi = ('<h2 id="steps">The steps, from the commission’s flowchart</h2><ol class="steps">'
             + rim.t(f'<li><strong>Check the exam prerequisites.</strong> At least {L["eta"]} years old on the exam date, a U.S. citizen, U.S. national or alien authorized to work in the United States, with a high school diploma or equivalent.[[hi_requisiti]]</li>'
                     f'<li><strong>Complete the {L["ore"]}-hour Hawaii salesperson prelicensing course</strong> at a registered prelicense school. The completion certificate is valid for two years.[[hi_licenza]]</li>'
                     '<li><strong>Book the exam</strong> with PSI, the company that gives it.[[hi_prelicenza,hi_licenza]]</li>'
                     '<li><strong>Pass the exam.</strong> You receive a score report and information on how to apply.[[hi_licenza]]</li>'
                     '<li><strong>Apply within two years of passing.</strong>[[hi_licenza]]</li>'
                     '<li><strong>To work, join a brokerage.</strong> An active license requires being employed by or associated with an active Hawaii brokerage firm or sole proprietor.[[hi_licenza]]</li></ol>'))
    testo = (passi + '<h2>What the commission says, word for word</h2>' + rim.cit("hi_licenza", "ore") + rim.cit("hi_licenza", "certificato") + rim.cit("hi_requisiti", "eta") + rim.cit("hi_prelicenza", "psi")
             + rim.cit("hi_licenza", "domanda") + rim.cit("hi_licenza", "attivo") + rim.cit("hi_faq", "attesa"))
    tariffe = ('<h2 id="fees">Official fees</h2><div class="testo">' + rim.t('<p>From the commission’s fee page. The salesperson license fee depends on whether the year is odd or even.[[hi_tariffe]]</p>') + "</div>"
               + kv([("Salesperson license, even-numbered year", f'<b>{usd(L["licenza_pari"])}</b>' + (f"<small>{anno} is an even-numbered year</small>" if anno % 2 == 0 else "")),
                     ("Salesperson license, odd-numbered year", f'<b>{usd(L["licenza_dispari"])}</b>' + (f"<small>{anno} is an odd-numbered year</small>" if anno % 2 else "")),
                     ("Renewal", f'<b>{usd(L["rinnovo"])}</b>')])
               + '<div class="testo"><p>The exam fee is not on the commission’s pages that we read: it is set out in the exam company’s candidate bulletin.</p></div>')
    fatti_ = [(f'{L["ore"]} hours', "prelicensing course"), (usd(questa), f"salesperson license fee in {anno}"), (str(L["eta"]), "minimum age on the exam date"), ("PSI", "gives the exam")]
    non = ('<li>The exam fee, the number of questions and the passing score: they are in the exam company’s candidate bulletin, which we did not use as a source.</li>'
           '<li>The price of the prelicensing course: each school sets its own.</li><li>Equivalency certificates for people licensed in another state are described on the commission’s pages and not repeated here.</li>')
    faq = [
        ("hawaii real estate license requirements", "What are the requirements for a Hawaii real estate license?",
         f"To sit the exam you must have completed the {L['ore']}-hour Hawaii prelicense course (or hold an equivalency), be a U.S. citizen, U.S. national or alien authorized to work in the United States, be at least {L['eta']} on the exam date and have a high school diploma or equivalent.", "hi_requisiti,hi_licenza"),
        ("how to get a real estate license in hawaii", "How do I get a real estate license in Hawaii?",
         f"Complete the {L['ore']}-hour salesperson prelicensing course at a registered school, book and pass the exam with PSI, then submit a complete license application within two years of passing. To be active you must be associated with a Hawaii brokerage.", "hi_licenza,hi_prelicenza"),
        ("hawaii real estate license cost", "How much does a Hawaii real estate license cost?",
         f"The commission's fee page lists {usd(L['licenza_pari'])} for a salesperson license in an even-numbered year and {usd(L['licenza_dispari'])} in an odd-numbered year. The exam fee and the price of the course are separate and are not on the commission's pages we read.", "hi_tariffe"),
        ("how to become a real estate agent in hawaii", "Do I have to live in Hawaii to get a real estate license?",
         "No. The commission's FAQ answers the question “Do I have to be a resident of Hawaii to secure a real estate license?” with “No”.", "hi_faq"),
        ("real estate license hawaii", "What happens if I fail the Hawaii real estate exam?",
         f"The commission's FAQ says you must wait {L['ore_attesa']} hours before rescheduling an examination. The prelicense course certificate stays valid for two years from the date it was issued.", "hi_faq,hi_licenza"),
    ]
    return fatti_, testo + tariffe, non, faq


LICENZA = {"TX": licenza_tx, "AL": licenza_al, "NE": licenza_ne, "HI": licenza_hi}


def pagina_licenza(s):
    rim = Rimandi()
    d, L = st(s), LIC[s]
    nome = d["nome"]
    fatti_, testo, non, faq = LICENZA[s](rim)
    prim = MISURE[s][0][0]
    fonti_lic = sorted(k for k in FONTI if k.startswith(s.lower() + "_") and k not in (d["fonte"],))
    sotto = f'{ico("info")} Taken only from the {h(d["ente"])}’s own pages and documents, read on {data_lunga(CONTROLLO)}. Confirm with the commission before you pay.'
    corpo = fatti([(h(a), b) for a, b in fatti_], sotto)
    corpo += (f'<div class="testo"><p>This page covers a first {h(d["titolo_licenza"])} license for someone who is not licensed in another state. '
              f'Every step and figure comes from the commission; where its pages do not give a figure, we say so instead of guessing.</p></div>')
    corpo += testo
    corpo += (f'<h2 id="schools">Choosing a school: the official pass rates</h2><div class="testo"><p>The commission publishes exam results for each school. In the latest figures, '
              f'{h(tasso_stato(s, prim))} of {MISURE[s][0][2].split(", ", 1)[1] if s != "HI" else "the national parts taken"} '
              f'{"were passed" if s == "HI" else "passed"} ({num(d["totale"][prim]["p"])} of {num(d["totale"][prim]["n"])}; {periodo(s)}).{rim.ref(d["fonte"])}</p>'
              f'<p class="azioni"><a class="btn" href="/{slug(s)}/">{h(nome)} pass rates by school{ico("arrow")}</a></p></div>')
    corpo += f'<h2 id="not-covered">What this page does not cover</h2><ul class="testo">{non}</ul>'
    faq_html, faq_ld = faq_blocco(faq, rim)
    corpo += faq_html
    altri = "".join(f'<li><a href="/{slug_lic(o)}/"><b>{h(st(o)["nome"])}</b><small>{LIC[o]["ore"]} hours</small></a></li>' for o in STATI if o != s)
    corpo += f'<h2>Other states</h2><ul class="griglia larga">{altri}</ul>'
    corpo += rim.elenco('<p class="small">Hours, ages, deadlines and fees are copied from the official pages above; the totals marked “our sum” are our arithmetic on those figures. See <a href="/how-we-check/">how we check</a>.</p>')
    testata = banda(f"{nome} · {d['ente']}", f"How to get a {nome} real estate license",
                    h(f"The steps, hours, deadlines and official fees for a {nome} real estate {d['titolo_licenza']} license, taken from the commission’s own pages and quoted word for word."), icona="key")
    titolo = f"{nome} Real Estate License: Steps, Hours and Fees ({CONTROLLO.year})"
    if s == "TX":
        descr = f"How to get a Texas real estate license: {L['ore']} hours of courses, TREC application, fingerprints, exam and official fees, from TREC’s own pages."
    elif s == "AL":
        descr = f"How to get an Alabama real estate license: {L['ore']}-hour course, {L['mesi_esame']} months to pass the exam, {L['giorni_domanda']} days to apply, from the commission’s pages."
    elif s == "NE":
        descr = f"How to get a Nebraska real estate license: {L['ore']} hours of education, exam pass marks and official fees, from the commission’s documents."
    else:
        descr = f"How to get a Hawaii real estate license: {L['ore']}-hour prelicensing course, exam prerequisites and license fees, from the commission’s pages."
    assert all(f in FONTI for f in fonti_lic)
    pagina(f"{slug_lic(s)}/", titolo, descr, corpo, testata, briciole=[("Home", ""), (f"{nome} pass rates", f"{slug(s)}/"), (f"{nome} license", f"{slug_lic(s)}/")], jsonld=[faq_ld])


# ---------------------------------------------------------------- home
def home():
    rim = Rimandi()
    schede = []
    for s in STATI:
        d, prim = st(s), MISURE[s][0][0]
        tot = d["totale"][prim]
        cosa = {"TX": "of first attempts passed", "AL": "of first attempts passed (our sum of the schools)", "NE": "of first-time takers passed the national part (our sum)", "HI": "of national parts passed (all exams taken)"}[s]
        schede.append(f'<li><h3>{h(d["nome"])}</h3><p class="big">{h(tasso_stato(s, prim))}</p><p class="lab">{cosa}: {num(tot["p"])} of {num(tot["n"])}{rim.ref(d["fonte"])}</p>'
                      f'<p class="per">{len(d["scuole"])} schools · {h(periodo(s, True))}</p>'
                      f'<p class="azioni"><a class="btn" href="/{slug(s)}/">Pass rates by school</a><a class="btn sec" href="/{slug_lic(s)}/">License steps</a></p></li>')
    corpo = f'<div class="pull"><ul class="stati">{"".join(schede)}</ul></div>'
    corpo += ('<div class="testo"><p class="small">The four figures are not comparable with each other: each state counts in its own way (first attempts in Texas, all exams in Hawaii, one quarter in Nebraska). Each state page explains what is counted.</p></div>')
    corpo += ('<h2>What you find here</h2><div class="testo"><p>Before the licensing exam you have to take a pre-licensing course, and the schools that sell it often advertise their own pass rates. '
              'Some state real estate commissions publish the real results: how many students of each school took the exam and how many passed. '
              'This site copies those official tables, state by state, and puts three things next to every percentage: <strong>the number of exams</strong> it is based on, <strong>the period</strong> it covers and <strong>the source</strong>.</p>'
              f'<p>We do not rank or recommend schools. When you sort a table by pass rate, schools with fewer than {SOGLIA} exams are listed after the others, because with so few results the percentage is mostly chance.</p></div>')
    righe = []
    for s in STATI:
        d = st(s)
        primo = {"TX": "Yes (only first attempts)", "AL": "Yes, and all attempts", "NE": "Yes, and all takers", "HI": "No: all exams taken"}[s]
        righe.append(f'<tr><th scope="row"><a href="/{slug(s)}/">{h(d["nome"])}</a></th><td>{h(d["ente"])}{rim.ref(d["fonte"])}</td><td>{h(periodo(s, True))}</td><td>{primo}</td><td class="n">{len(d["scuole"])}</td><td class="n">{LIC[s]["ore"]}</td></tr>')
    corpo += ('<h2>The four states at a glance</h2><div class="tab"><table class="dati ampia"><caption><span>What each commission publishes. Hours: pre-licensing education required for a first license.</span></caption>'
              '<thead><tr><th scope="col">State</th><th scope="col">Published by</th><th scope="col">Period</th><th scope="col">First attempts separated?</th><th scope="col" class="n">Schools</th><th scope="col" class="n">Course hours</th></tr></thead>'
              f'<tbody>{"".join(righe)}</tbody></table></div>')
    corpo += ('<h2>Why the number of exams matters</h2><div class="testo"><p>A school with 4 students and 3 passes shows 75%; one more fail and it shows 60%. A school with 8,000 exams does not move like that. '
              'The Nebraska commission puts it plainly in its own report:</p>' + rim.cit("ne_indice", "cautela") + rim.cit("ne_indice", "piccoli")
              + f'<p>So every rate on this site has its count next to it, and rates based on fewer than {SOGLIA} exams carry a “small sample” label.</p></div>')
    tx, al = st("TX")["totale"]["first"], st("AL")["totale"]
    faq = [
        ("real estate exam pass rate", "What is the pass rate for the real estate exam?",
         f"It depends on the state and on what is counted. In Texas, {tx['pc']} of first attempts at the sales agent exam passed between {periodo('TX')}. In Alabama, the school figures add up to {pct1(al['first']['p'], al['first']['n'])} of first attempts over the previous 12 months, and {pct1(al['all']['p'], al['all']['n'])} when retakes are counted.", "tx_tassi,al_tassi"),
        ("how hard is the real estate exam", "How hard is the real estate exam?",
         f"Official results show that many people do not pass the first time. In Texas {num(tx['n'] - tx['p'])} of {num(tx['n'])} first attempts failed in the two years covered. States let you retake the exam; in Texas three fails on either part mean more education before you can test again.", "tx_tassi,tx_licenza"),
        ("is the real estate exam hard", "Is the real estate exam hard to pass on the first try?",
         f"In the states that separate first attempts, the first-try rate was {tx['pc']} in Texas and {pct1(al['first']['p'], al['first']['n'])} in Alabama (our sum of the commission's school figures). The rate differs a lot from school to school, and for small schools it is based on very few students.", "tx_tassi,al_tassi"),
    ]
    faq_html, faq_ld = faq_blocco(faq, rim)
    corpo += faq_html
    corpo += rim.elenco()
    testata = banda("Official state data · 4 states", "Real estate school pass rates, from the state’s own data",
                    "How the students of each school did on the licensing exam in <strong>Texas, Alabama, Nebraska and Hawaii</strong>: the percentage the commission publishes, with the number of exams, the period and the source next to it.", icona="chart")
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}, faq_ld]
    pagina("", "Real Estate School Pass Rates by State (Official Data)",
           "Real estate exam pass rates by school from state commissions in Texas, Alabama, Nebraska and Hawaii, with the number of exams, the period and the source.",
           corpo, testata, jsonld=ld)


# ---------------------------------------------------------------- pagine di servizio
MODULO = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card" data-correzioni>
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or figure<input type="text" name="page" required maxlength="300" placeholder="For example /texas/, a school’s exam count"></label>
<label>What is wrong?<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<p class="small">Please do not include your name, email address, exam results or other personal information: the form does not ask for them and we do not reply to messages.</p>
<p class="errore" data-errore hidden>The message was not sent. Please try again.</p>
<button type="submit" class="btn">Send correction</button>
</form>
<p class="ok" data-ok hidden><strong>Thank you.</strong> We will check it against the official source.</p>"""


def come_controlliamo():
    rim = Rimandi()
    ufficiali = {k: f for k, f in FONTI.items() if k not in FONTI_PARTNER}
    n_frasi = sum(len(f["frasi"]) for f in ufficiali.values())
    corpo = ('<div class="testo pull card"><p>People use a pass rate to choose where to spend several hundred dollars and weeks of study. So this site publishes only what a state real estate commission has published, '
             'keeps a copy of every official file, and never shows a percentage without the number of exams behind it.</p></div>')
    righe = []
    for s in STATI:
        d = st(s)
        f = FONTI[d["fonte"]]
        conta = {"TX": "Sales agent exam, first attempts; a result is attributed to the provider where the student took most courses",
                 "AL": "Salesperson exam: first attempts, and all attempts including retakes",
                 "NE": "Salesperson exam, national and state parts: first-time takers, and all takers",
                 "HI": "Salesperson exam, national and state parts: all exams taken (first attempts not separated)"}[s]
        forma = {"TX": "Data file (JSON) loaded by the commission’s page", "AL": "The commission’s web page, one card per school", "NE": "Scanned PDF report; typed by hand and checked row by row", "HI": "PDF bulletin with text tables"}[s]
        righe.append(f'<tr><th scope="row"><a href="/{slug(s)}/">{h(d["nome"])}</a></th><td><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a>{rim.ref(d["fonte"])}<br><span class="small">{h(d["ente"])}</span></td>'
                     f'<td>{h(forma)}</td><td>{h(conta)}</td><td>{h(periodo(s))}</td><td>{giorno(d["letto_il"])}</td></tr>')
    corpo += ('<h2 id="sources">The four data sources</h2><div class="tab"><table class="dati ampia"><caption><span>Where each state table comes from, what it counts and when we read it.</span></caption>'
              '<thead><tr><th scope="col">State</th><th scope="col">Official publication</th><th scope="col">Form</th><th scope="col">What is counted</th><th scope="col">Period</th><th scope="col">Read on</th></tr></thead>'
              f'<tbody>{"".join(righe)}</tbody></table></div>')
    corpo += '<h2>How the figures get from the commission to the page</h2><div class="testo"><ul>'
    corpo += rim.t(f'<li>We download each official file ({len(ufficiali)} in all: the four data sources and the commissions’ licensing pages, fee schedules and exam information) with a program that identifies itself as a robot, '
                   'and record its address, the date and a fingerprint (SHA-256).</li>'
                   '<li>Exam counts and percentages are read from the file by a program and copied as printed. The build stops if a percentage does not match its own counts (passed ÷ exams), '
                   'if passed plus failed does not equal the exams taken, or if a total printed by the commission is not the sum of its rows.[[tx_tassi,hi_tassi]]</li>'
                   '<li>Nebraska’s report is a scan, so its numbers are typed by hand from the page images. Each row has to add up in three ways (passed + failed = graded; first-time takers + repeaters = total; the rows of a school = its total row) before the site is built, and the typed figures are tied to the fingerprint of that exact PDF.[[ne_tassi]]</li>'
                   f'<li>Every sentence in a quotation box is copied word for word and searched for in the downloaded file each time ({n_frasi} sentences). If one is no longer there, the build stops.</li>'
                   '<li>A second program, written separately, reads the raw files again in its own way and compares every number on every page.</li></ul></div>')
    corpo += ('<h2>Small samples</h2><div class="testo">'
              f'<p>Every rate has its count next to it. Below {SOGLIA} exams a rate is labelled “small sample”, and when a table is sorted by pass rate those schools are listed after the others. '
              f'{SOGLIA} is our own threshold, not an official one: with 30 exams, one more pass or fail still moves the rate by more than three points.</p>'
              '<p>Where a commission prints no statewide total (Alabama, Nebraska), the top row of the table is our sum of the school rows and is labelled as such; its percentage is our division, rounded to one decimal.</p></div>')
    corpo += ('<h2>What we do not do</h2><div class="testo"><ul>'
              '<li>We do not rank, score or recommend schools, and we do not estimate figures a commission has not published.</li>'
              '<li>We do not use pass rates advertised by schools, surveys or other websites.</li>'
              '<li>We publish nothing about individual candidates: the sources contain only counts by school.</li>'
              '<li>This is a four-state pilot. Other commissions publish school results too; some of their websites refuse our checking server or the files could not be found, and we do not try to get round such blocks. Those states are simply not here yet.</li>'
              '<li>Broker exam results are in the official sources but not on these pages.</li></ul></div>')
    corpo += ('<h2>When we update</h2><div class="testo"><p>Texas publishes a two-year window, Alabama refreshes its page on the 10th of each month, Nebraska and Hawaii publish every quarter. '
              'A state page changes only when the new official file has been read and all the checks pass again; the period and the reading date are always shown at the top.</p></div>')
    corpo += ('<h2 id="corrections">Report an error</h2><div class="testo"><p>Seen a figure that does not match the official publication, or run a school whose row is wrong? Tell us which page and, if you can, link the source: we check it and fix the page. '
              'The figures themselves come from the commission, so a correction to the official data has to be asked of the commission.</p></div>' + MODULO)
    corpo += rim.elenco()
    testata = banda("How we check", "How we check every figure, and the sources", "Official files kept on record, counts that must add up, and the number of exams next to every percentage.", corta=True, icona="shield")
    pagina("how-we-check/", "How We Check Real Estate School Pass Rates and Our Sources",
           f"How {NOME} copies school exam results from state real estate commissions, checks that every row adds up and handles small samples.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")])


def about():
    aff = ('<p>Some state pages may also carry one clearly marked affiliate link to a school that appears in the official table; if you enroll through it we may earn a commission. It never changes the figures or their order.</p>' if PARTNER else "")
    pub = ('<p>The site shows advertising served by Google AdSense. Advertisers never decide what we publish.</p>' if MON.adsense_attivo(SITO_ID)
           else '<p>The site currently shows no advertising.</p>')
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{NOME}</strong> is an independent publication, part of a small network of websites that turn official data into plain reference pages. '
             'It shows real estate licensing exam results by school in four states, copied from the state real estate commissions, and the steps to a first license from the same commissions’ pages.</p>'
             '<p>We are <strong>not affiliated with</strong> any real estate commission, school or exam company, and we do not sell courses. '
             'The site gives general information, not legal or career advice.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Only exam counts, percentages, hours, deadlines and fees printed in official publications, each linked to its source and quoted word for word where it matters.</li>'
             '<li>Sums of those figures where a commission prints no total, always labelled as ours.</li>'
             '<li>Where an official source does not give a figure, we say so instead of filling the gap.</li></ul>'
             f'<h2>How the site is paid for</h2><div class="testo">{pub}{aff}</div>'
             '<h2>Corrections</h2><div class="testo"><p>If a figure does not match the official publication, use the <a href="/how-we-check/#corrections">corrections form</a>. For questions about your own application or exam, '
             'ask the commission of your state: it has your records.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, what it publishes and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", f"About {NOME}: an independent site that copies real estate exam results by school from state commissions.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")])


def privacy():
    con_aff = bool(PARTNER)
    cookie = MON.privacy_cookie("en", SITO_ID, con_aff) or ("<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. This site shows no advertising.</p>")
    california = MON.frase_california(SITO_ID) or "California residents: we do not sell or share personal information."
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {NOME} ({URL_SITO.replace("https://", "")}) collects. In short: very little.</p></div>'
             '<div class="testo"><h2>The tables</h2><p>Searching, sorting and filtering the tables happens in your browser: what you type is not sent to us or stored. '
             'The tables contain figures about schools, which are businesses and institutions; the site holds no information about individual exam candidates.</p>'
             '<p>The site remembers your choice of light or dark theme in your browser (local storage).</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             '<h2 id="corrections">Corrections form</h2><p>The <a href="/how-we-check/#corrections">corrections form</a> asks for the page, your message and, if you wish, a link to the official source. '
             'It does not ask for your name or email address, and we ask you not to put personal details in the message. The form is processed by Netlify Forms on our behalf. '
             'We use what you send only to check the figure and delete it once that is done. There are no accounts, newsletters or comments on this site.</p>'
             f'<h2>California</h2><p>{california}</p>'
             f'<h2>Changes</h2><p>Last update: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID, con_aff) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", f"Privacy | {NOME}", f"Privacy at {NOME}: tables that work in your browser, a cookie-free visit counter, and Google AdSense advertising with consent.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    griglia = "".join(f'<li><a href="/{slug(s)}/"><b>{h(st(s)["nome"])}</b><small>{len(st(s)["scuole"])} schools</small></a></li>' for s in STATI)
    corpo = f'<div class="pull card"><p>The page you asked for does not exist. Go to <a href="/">all states</a> or pick one below.</p></div><ul class="griglia larga" style="margin-top:18px">{griglia}</ul>'
    testata = banda("404", "Page not found", "This address has no page.", corta=True, icona="alert")
    pagina("", f"Page not found | {NOME}", "Page not found.", corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


# ---------------------------------------------------------------- file accessori
def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{CONTROLLO.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in realestate/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = realestate/sito, Build command vuoto, Publish directory = "."
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
""", encoding="utf-8")


def copia_risorse():
    (SITO / "assets").mkdir(parents=True, exist_ok=True)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")
    for nome, testo in ASSET.items():
        (SITO / "assets" / nome).write_text(testo, encoding="utf-8")


def controlla():
    for fid, f in FONTI.items():
        mancano = [k for k, ok in f["trovate"].items() if not ok]
        if f["http"] != 200 or mancano:
            raise SystemExit(f"fonte {fid}: HTTP {f['http']}, frasi mancanti {mancano} (rilanciare raccolta/fonti.py)")
        grezzo = RADICE / f["file"]
        if f.get("impronta") == "frasi":
            # Pagina HTML: i byte cambiano a ogni scarico (parti dinamiche), quindi fa fede l'impronta delle frasi citate, ritrovate nel file.
            if TESTO.impronta_frasi(TESTO.norm(TESTO.testo(grezzo)), f["frasi"]) != f["sha256_frasi"]:
                raise SystemExit(f"fonte {fid}: le frasi citate non sono più nel file grezzo come registrate (rilanciare raccolta/fonti.py)")
        elif hashlib.sha256(grezzo.read_bytes()).hexdigest() != f["sha256"]:
            raise SystemExit(f"fonte {fid}: il file grezzo non ha più l'impronta registrata (rilanciare raccolta/fonti.py)")
    if sorted(G["stati"]) != sorted(STATI) or sorted(LIC) != sorted(STATI):
        raise SystemExit("tassi.json: Stati diversi da quelli delle pagine")
    for s in STATI:
        for x in st(s)["scuole"]:
            for k, _, _ in MISURE[s]:
                v = x[k]
                if v["p"] > v["n"] or (v["n"] and not v["pc"]):
                    raise SystemExit(f"tassi.json: {s}/{x['nome']}/{k} non torna")
    eta = (date.today() - CONTROLLO).days
    if eta > 45:
        print(f"ATTENZIONE: le fonti sono state lette {eta} giorni fa. Rilanciare raccolta/fonti.py (Alabama cambia ogni mese, Nebraska e Hawaii ogni trimestre).")


def main():
    controlla()
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_risorse()
    home()
    for s in STATI:
        pagina_stato(s)
    for s in STATI:
        pagina_licenza(s)
    come_controlliamo()
    about()
    privacy()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404. Partner accesi: {', '.join(p['id'] for p in PARTNER) or 'nessuno (riquadro spento)'}.")


if __name__ == "__main__":
    main()
