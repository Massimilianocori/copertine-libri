"""Genera il sito statico "Military Pay Chart" (USA, inglese) in milpay/sito/.

Uso (dalla radice del repository):
    python3 milpay/raccolta/tabelle.py     # tabelle ufficiali 2026 (e 2025 di controllo) -> dati/paga_<anno>.json
    python3 milpay/raccolta/storico.py     # aumenti di gennaio dalle tabelle e dalla formula ECI -> dati/storico.json
    python3 milpay/raccolta/fonti.py       # rilegge le fonti e le frasi esatte -> dati/fonti.json
    python3 milpay/genera.py               # pagine in milpay/sito/
    python3 milpay/verifica.py [--browser] # controlli

Ogni cella mostrata viene da dati/paga_2026.json (Schedule 8 dell'ordine esecutivo 14368); prima di scrivere le pagine
`controlla_tabella` verifica il numero di celle, i trattini, l'ordine crescente per anzianità e per grado e i tetti.
Le FAQ nascono da ricerche vere (dati/domanda.json). Nessun dato personale.
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
import stile  # noqa: E402

URL_SITO = "https://military-pay-chart.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
NOME = "Military Pay Chart"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "milpay"  # nome del sito in monetizzazione.json
ADSENSE_HEAD = MON.script_adsense(SITO_ID)


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


P = carica("paga_2026.json")
P25 = carica("paga_2025.json")
ST = carica("storico.json")
DOM = carica("domanda.json")
_F = carica("fonti.json")
FONTI, ESITI = _F["definizioni"], _F["fonti"]
COL = P["colonne"]
NOTE = P["note"]
EO = P["fonte"]
CONTROLLO = date.fromisoformat(P["letto_il"])
ANNO = P["anno"]
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# gradi in ordine di pagina: (slug, etichetta, categoria, chiave nel JSON)
GRADI = ([(f"e-{i}", f"E-{i}", "E", f"E-{i}") for i in range(1, 10)] + [(f"w-{i}", f"W-{i}", "W", f"W-{i}") for i in range(1, 6)]
         + [(f"o-{i}", f"O-{i}", "O", f"O-{i}") for i in range(1, 11)] + [(f"o-{i}e", f"O-{i}E", "OE", f"O-{i}E") for i in range(1, 4)])
E1_4 = ("e-1-under-4-months", "E-1 (under 4 months)", "E", "E-1<4")
CAT_NOME = {"E": "Enlisted", "W": "Warrant officers", "O": "Commissioned officers",
            "OE": "Officers with over 4 years of prior enlisted or warrant officer service"}
TETTO2 = ["o-7", "o-8", "o-9", "o-10"]  # nota *: livello II dell'Executive Schedule
TETTO5 = ["o-1", "o-2", "o-3", "o-4", "o-5", "o-6", "o-1e", "o-2e", "o-3e"]  # nota **: livello V, O-6 e sotto
NOINDEX = {"o-9"}  # riga identica a O-10: la pagina esiste per chi la cerca, ma non va nell'indice (duplicato)


def riga(chiave):
    for cat, t in P["tabelle"].items():
        if chiave in t:
            return t[chiave]
    raise KeyError(chiave)


def massimo(r):
    return max(v for v in r if v is not None)


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def soldi(x, cent=True):
    return f"${x:,.2f}" if cent else f"${x:,.0f}"


def slug_col(i):
    return COL[i].lower().replace(" ", "-")


def anni_txt(i):
    """'2 or less' -> '2 years or less'; 'Over 4' -> 'over 4 years'."""
    return "2 years or less" if i == 0 else f"over {COL[i].split()[1]} years"


# ---------------------------------------------------------------- calcolo (copia Python di stile.APP_JS calcola)
def tetti():
    return {"lvl2": NOTE["tetto_O7_O10"], "lvl5": NOTE["tetto_O6_e_sotto"]}


def pagabile(slug, v):
    if v is None:
        return None
    if slug in TETTO2:
        return min(v, NOTE["tetto_O7_O10"])
    if slug in TETTO5:
        return min(v, NOTE["tetto_O6_e_sotto"])
    return v


def calcola(slug, chiave, c):
    r = riga(chiave)
    v = r[c]
    if v is None:
        return None
    m = pagabile(slug, v)
    pr = None
    for j in range(c + 1, len(r)):
        if r[j] is not None and pagabile(slug, r[j]) > m + 0.001:
            pr = {"col": j, "mese": pagabile(slug, r[j]), "piu": round(pagabile(slug, r[j]) - m, 2)}
            break
    return {"tabella": v, "mese": m, "anno": round(m * 12, 2), "tetto": None if m == v else m, "prossimo": pr}


def dati_js():
    righe, nomi, pagine = {}, {}, {}
    for slug, nome, _, k in GRADI + [E1_4]:
        righe[slug], nomi[slug], pagine[slug] = riga(k), nome, ("e-1" if slug == E1_4[0] else slug)
    return {"colonne": COL, "slug_col": [slug_col(i) for i in range(22)], "righe": righe, "nomi": nomi, "pagine": pagine,
            "tetti": tetti(), "tetto2": TETTO2, "tetto5": TETTO5}


# ---------------------------------------------------------------- controlli sui dati (prima di scrivere qualsiasi pagina)
def controlla_tabella():
    err = []
    t = P["tabelle"]
    attese = {"O": 10, "OE": 3, "W": 5, "E": 10}
    n = 0
    for cat, k in attese.items():
        if len(t.get(cat, {})) != k:
            err.append(f"{cat}: {len(t.get(cat, {}))} righe, attese {k}")
        for g, r in t.get(cat, {}).items():
            if len(r) != 22:
                err.append(f"{g}: {len(r)} colonne")
            n += len(r)
    if n != 616:
        err.append(f"celle totali {n}, attese 616")
    # trattini dove la tabella ufficiale non ha importo
    vuote = {"O-10": range(0, 11), "O-9": range(0, 11), "O-3E": range(0, 3), "O-2E": range(0, 3), "O-1E": range(0, 3), "W-5": range(0, 11),
             "E-9": range(0, 6), "E-8": range(0, 5), "E-1<4": range(1, 22)}
    piene = 0
    for cat in t:
        for g, r in t[cat].items():
            for i, v in enumerate(r):
                deve = i in vuote.get(g, ())
                if deve and v is not None:
                    err.append(f"{g} {COL[i]}: atteso un trattino, trovato {v}")
                if not deve and v is None:
                    err.append(f"{g} {COL[i]}: cella vuota")
                if v is not None:
                    piene += 1
                    if not (1000 <= v <= 20000) or abs(v * 10 - round(v * 10)) > 1e-6:
                        err.append(f"{g} {COL[i]}: valore fuori scala o non in decimi di dollaro: {v}")
            vals = [v for v in r if v is not None]
            if any(b < a for a, b in zip(vals, vals[1:])):
                err.append(f"{g}: la paga scende con l'anzianità")
    # ordine per grado a parità di anzianità
    catene = [["E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9"], ["W-1", "W-2", "W-3", "W-4", "W-5"],
              ["O-1", "O-2", "O-3", "O-4", "O-5", "O-6", "O-7", "O-8", "O-9", "O-10"], ["O-1E", "O-2E", "O-3E"],
              ["O-1", "O-1E"], ["O-2", "O-2E"], ["O-3", "O-3E"], ["E-1<4", "E-1"]]
    for c in catene:
        for a, b in zip(c, c[1:]):
            for i in range(22):
                va, vb = riga(a)[i], riga(b)[i]
                if va is not None and vb is not None and vb < va:
                    err.append(f"{b} < {a} a {COL[i]}")
    # tetti: nessun importo O-6 e sotto sopra il livello V; il livello II è sotto il massimo della tabella (nota * applicata)
    for slug in TETTO5:
        for v in riga(slug.upper()):
            if v is not None and v > NOTE["tetto_O6_e_sotto"]:
                err.append(f"{slug}: {v} sopra il tetto del livello V")
    if not NOTE["tetto_O6_e_sotto"] < NOTE["tetto_O7_O10"]:
        err.append("tetti incoerenti")
    if P["letture"]["A_uguale_B"] != P["letture"]["celle"] or P["letture"]["celle"] != 616:
        err.append(f"letture: {P['letture']}")
    # controllo indipendente: 2026 = gennaio 2025 × 1,038 (± $0,15) sulle righe non toccate a metà 2025 e sotto i tetti
    conf, fuori = 0, []
    for cat in t:
        for g, r in t[cat].items():
            if g in ("E-1", "E-1<4", "E-2", "E-3", "E-4", "E-5"):
                continue
            for i, v in enumerate(r):
                w = P25["tabelle"][cat][g][i]
                if v is None or w is None or w >= P25["note"]["tetto_O7_O10"] or v >= NOTE["tetto_O7_O10"] or (g == "O-6" and v >= NOTE["tetto_O6_e_sotto"]):
                    continue
                conf += 1
                if abs(v - w * 1.038) > 0.15:
                    fuori.append(f"{g} {COL[i]}: {w} × 1,038 = {w * 1.038:.2f}, tabella 2026 {v}")
    if fuori:
        err += fuori
    if conf < 300:
        err.append(f"solo {conf} celle confrontate con il 2025")
    if err:
        raise SystemExit("ERRORI NELLA TABELLA:\n - " + "\n - ".join(err))
    return {"celle": n, "importi": piene, "confronto_2025": conf}


# ---------------------------------------------------------------- fonti e rimandi numerati
class Rimandi:
    def __init__(self):
        self.ordine = []

    def ref(self, ids):
        if isinstance(ids, str):
            ids = [i.strip() for i in ids.split(",") if i.strip()]
        nums = []
        for i in ids:
            if i not in FONTI:
                raise SystemExit(f"fonte sconosciuta: {i}")
            if i not in self.ordine:
                self.ordine.append(i)
            nums.append(self.ordine.index(i) + 1)
        return '<sup class="ref">' + ",".join(f'<a href="#f{n}" aria-label="source {n}">[{n}]</a>' for n in sorted(set(nums))) + "</sup>"

    def t(self, testo):
        return re.sub(r"\[\[([a-z0-9_, ]+)\]\]", lambda m: self.ref(m.group(1)), testo)

    def elenco(self):
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f, es = FONTI[i], ESITI.get(i, {})
            stato = f"checked {data_lunga(es['letto_il'])}" if es.get("http") == 200 else f"last check: HTTP {h(es.get('http'))}"
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. <span class="small">{stato}</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2><ol>{"".join(voci)}</ol>'
                '<p class="small">Pay figures are copied from the official tables above; annual amounts (× 12), differences and the “next step” are our arithmetic on those figures. '
                'See <a href="/how-we-check/">how we check</a>.</p></section>')


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


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
MENU = [("", "2026 chart"), ("calculator/", "Calculator"), ("pay-raise-history/", "Raise history"), ("2027-pay-raise/", "2027 raise")]
DISCLAIMER = ("<strong>Independent site, not affiliated with the Department of Defense, any military branch, the Coast Guard or DFAS.</strong> "
              "We show monthly basic pay as printed in the official tables, nothing else: no allowances, special pays, bonuses or taxes. "
              "This is general information, not financial advice. Your Leave and Earnings Statement and your unit’s finance office are the authority on your own pay; "
              "check with them before making decisions.")


def menu_html(percorso, mobile=False):
    voci = [f'<a href="/{u}"' + (' aria-current="page"' if u == percorso else "") + (' class="w2"' if mobile else "") + f">{h(t)}</a>" for u, t in MENU]
    if mobile:
        voci.append('<span class="sep" aria-hidden="true"></span>')
        voci += [f'<a href="/{s}/">{h(n)}</a>' for s, n, _, _ in GRADI if s not in NOINDEX]
    return "".join(voci)


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None, script_dati=""):
    file = file or (percorso + "index.html" if percorso else "index.html")
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append(percorso)
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                   "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": f"{URL_SITO}/{p}"} for i, (n, p) in enumerate(briciole, 1)]})
        bc = ('<nav class="briciole" aria-label="Breadcrumb">' + " › ".join([f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    corpo_tr = corpo + MON.riga_trasparenza(corpo, "en")
    enl = "".join(f'<li><a href="/{s}/">{n}</a></li>' for s, n, c, _ in GRADI if c == "E")
    alt = "".join(f'<li><a href="/{s}/">{n}</a></li>' for s, n, c, _ in GRADI if c != "E" and s not in NOINDEX)
    guide = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [("calculator/", "Basic pay calculator"), ("pay-raise-history/", "Pay raise history"),
                    ("2027-pay-raise/", "2027 pay raise: status"), ("how-we-check/", "How we check"), ("about/", "About"), ("how-we-check/#corrections", "Contact and corrections"), ("privacy/", "Privacy")])
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
<meta name="theme-color" content="#111A2E">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Military Pay <b>Chart</b></span></a>
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
<a class="logo" href="/">{LOGO}<span>Military Pay <b>Chart</b></span></a>
<p><strong>{NOME}</strong> publishes the {ANNO} monthly basic pay tables of the U.S. uniformed services, copied from Schedule 8 of Executive Order {EO['ordine_esecutivo']}
in the Federal Register, with a page for every pay grade. Independent site, not a government website.</p>
<p>Official tables read on {data_lunga(CONTROLLO)}.</p>
</div><div>
<h2>Enlisted</h2><ul>{enl}</ul>
</div><div>
<h2>Officers and warrant officers</h2><ul class="f-gradi" style="display:grid">{alt}</ul>
<h2 style="margin-top:18px">Guides</h2><ul>{guide}</ul>
</div></div>
<p class="f-base">General information only, not financial advice. Not affiliated with the U.S. Department of Defense, the military services, the Coast Guard or DFAS.</p>
</div></footer>
{script_dati}<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, corta=False, icona="table"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>
</div></section>"""


# ---------------------------------------------------------------- domande frequenti (solo da ricerche vere)
def volume(frase):
    for r in DOM["ricerche"]:
        if r["frase"] == frase:
            return r["volume_mese"]
        for s in r["simili"]:
            if s["frase"] == frase:
                return s["volume_mese"]
    return 0


def faq_blocco(voci, rim):
    """voci: (ricerca, domanda, risposta testo semplice, fonti)."""
    if not voci:
        return "", None
    blocchi, ld = [], []
    for ric, q, a, fonti in voci:
        if volume(ric) <= 0:
            raise SystemExit(f"FAQ senza ricerca misurata: {ric}")
        blocchi.append(f'<div class="faq" data-ricerca="{h(ric)}"><h3>{h(q)}</h3><p>{h(a)}{rim.ref(fonti)}</p></div>')
        ld.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    html_ = ('<h2 id="faq">Common questions</h2><p class="small">Questions people in the United States search for, answered from the official sources.</p>' + "".join(blocchi))
    return html_, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


# ---------------------------------------------------------------- pezzi comuni
def img_url(cat, meta):
    mappa = {("O", 0): "ED23DE25.104", ("OE", 0): "ED23DE25.105", ("W", 0): "ED23DE25.105", ("O", 1): "ED23DE25.106", ("OE", 1): "ED23DE25.107",
             ("W", 1): "ED23DE25.107", ("E", 0): "ED23DE25.108", ("E", 1): "ED23DE25.109"}
    iid = mappa[(cat, meta)]
    return next(x["url"] for x in EO["immagini_schedule_8"] if x["id"] == iid)


def link_img(cat):
    return (f'page images <a href="{h(img_url(cat, 0))}" rel="noopener">0–18 years</a> and <a href="{h(img_url(cat, 1))}" rel="noopener">20–40 years</a>')


def tabella_categoria(cat, rim, evidenzia=None):
    chiavi = [k for k in P["tabelle"][cat]]
    testa = '<th scope="col">Grade</th>' + "".join(f'<th scope="col" class="n">{h(c)}</th>' for c in COL)
    righe = []
    for k in chiavi:
        if k == "E-1<4":
            nome, link = "E-1 <4 mo.", "/e-1/"
        else:
            nome, link = k, f"/{k.lower()}/"
        celle = "".join(f'<td class="n">{soldi(v)}</td>' if v is not None else '<td class="na">–</td>' for v in riga(k))
        righe.append(f'<tr{" class=\"qui\"" if evidenzia == k else ""}><th scope="row"><a href="{link}">{h(nome)}</a></th>{celle}</tr>')
    cap = (f'{h(CAT_NOME[cat])}: monthly basic pay from January 1, {ANNO}, by years of service. Source: Schedule 8 of Executive Order {EO["ordine_esecutivo"]}'
           f'{rim.ref("eo2026")}, {link_img(cat)}.')
    return f'<div class="tab"><table class="dati grande"><caption>{cap}</caption><thead><tr>{testa}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'


def note_tabella(rim, quali=("2", "5", "e9", "e1", "oe")):
    t = {
        "2": f"<li><strong>O-7 to O-10:</strong> basic pay is limited to the rate for level II of the Executive Schedule, <strong>{soldi(NOTE['tetto_O7_O10'])}</strong> a month in {ANNO}. The table prints {soldi(massimo(riga('O-10')))} in the O-9 and O-10 rows and in the O-8 row from over 22 years, above that cap, so the cap is the monthly amount paid.{rim.ref('eo2026')}</li>",
        "5": f"<li><strong>O-6 and below:</strong> basic pay is limited to the rate for level V of the Executive Schedule, <strong>{soldi(NOTE['tetto_O6_e_sotto'])}</strong> a month in {ANNO}.{rim.ref('eo2026')}</li>",
        "e9": f"<li><strong>Senior enlisted advisors</strong> (Sergeant Major of the Army, Master Chief Petty Officer of the Navy or Coast Guard, Chief Master Sergeant of the Air Force, Sergeant Major of the Marine Corps, Chief Master Sergeant of the Space Force and the senior enlisted advisors to the Chairman of the Joint Chiefs of Staff and to the Chief of the National Guard Bureau): <strong>{soldi(NOTE['E9_incarichi_speciali'])}</strong> a month, whatever their years of service.{rim.ref('eo2026')}</li>",
        "e1": f"<li><strong>E-1:</strong> the full E-1 rate applies after 4 months or more on active duty; with less than 4 months the rate is <strong>{soldi(riga('E-1<4')[0])}</strong>.{rim.ref('eo2026')}</li>",
        "oe": f"<li><strong>O-1E, O-2E, O-3E</strong> rates are for commissioned officers credited with over 4 years of active duty service as an enlisted member or warrant officer; the ordinary O-1 to O-3 rates do not apply to them. Reservists with at least 1,460 points as an enlisted member and/or warrant officer, creditable toward reserve retirement, also qualify.{rim.ref('eo2026')}</li>",
        "cad": f"<li><strong>Cadets and midshipmen:</strong> {soldi(NOTE['cadetti'])} a month.{rim.ref('eo2026')}</li>",
    }
    return '<ul class="testo">' + "".join(t[q] for q in quali) + "</ul>"


def griglia_gradi(escludi=None):
    out = []
    for cat in ("E", "W", "O", "OE"):
        voci = []
        for s, n, c, k in GRADI:
            if c != cat or s == escludi:
                continue
            r = [v for v in riga(k) if v is not None]
            voci.append(f'<li><a href="/{s}/"><b>{n}</b><small>from {soldi(r[0], False)}/mo</small></a></li>')
        out.append(f'<h3>{h(CAT_NOME[cat])}</h3><ul class="griglia">{"".join(voci)}</ul>')
    return "".join(out)


def calcolatore(g="e-5", c=3, titolo="Basic pay calculator, 2026"):
    op_g = ""
    for s, n, cat, _ in GRADI + [E1_4]:
        op_g += f'<option value="{s}"{" selected" if s == g else ""}>{h(n)}</option>'
    op_y = "".join(f'<option value="{i}"{" selected" if i == c else ""}>{h(anni_txt(i).capitalize())}</option>' for i in range(22))
    res = calcola(g, dict((s, k) for s, _, _, k in GRADI + [E1_4])[g], c)
    statico = (f'<div class="tot"><div class="main"><span>Monthly basic pay</span><b>{soldi(res["mese"])}</b></div><div><span>Per year (× 12)</span><b>{soldi(res["anno"])}</b></div></div>'
               if res else "")
    return f"""<section class="card calc" data-calc aria-labelledby="calc-h">
<div class="calc-h"><h2 id="calc-h">{ico("calc")}{h(titolo)}</h2></div>
<div class="calc-g">
<form class="calc-in" onsubmit="return false">
<label>Pay grade<select name="g">{op_g}</select></label>
<label>Years of service (as in the official table)<select name="y">{op_y}</select></label>
<p class="small">“Over 4” means more than 4 years. Years of service are counted under 37 U.S.C. 205; your finance office has your exact date.</p>
</form>
<div class="calc-out" data-out aria-live="polite">{statico}</div>
</div>
<p class="calc-f">Rates from the official {ANNO} table (Executive Order {EO['ordine_esecutivo']}, Schedule 8), with the monthly caps in its notes. Basic pay only. The calculator runs in your browser.</p>
</section>"""


def script_dati():
    return f'<script type="application/json" id="dati-paga">{json.dumps(dati_js(), separators=(",", ":"))}</script>\n'


# ---------------------------------------------------------------- pagine
def home():
    rim = Rimandi()
    e = riga("E-1")
    st = ST["aumenti"]
    a26 = next(x for x in st if x["anno"] == 2026)
    corpo = (f'<section class="card stats pull" aria-label="Key figures">'
             f'<div class="stat main"><b>{a26["tabelle"]["aumento"]}%</b><span>January {ANNO} raise in the pay table{rim.ref("eo2026,eo2025")}</span></div>'
             f'<div class="stat"><b>{soldi(e[0])}</b><span>E-1 monthly (4+ months of service){rim.ref("eo2026")}</span></div>'
             f'<div class="stat"><b>{soldi(massimo(riga("E-9")))}</b><span>Top of the E-9 table{rim.ref("eo2026")}</span></div>'
             f'<div class="stat"><b>{soldi(NOTE["tetto_O7_O10"])}</b><span>Monthly cap for O-7 to O-10{rim.ref("eo2026")}</span></div>'
             f'<p class="asof">Effective {P["effettiva_dal"]}. Executive Order {EO["ordine_esecutivo"]} of {data_lunga(EO["firmato_il"])}, Federal Register {EO["citazione"]}, Schedule 8. '
             f'Read on {data_lunga(CONTROLLO)}.</p></section>')
    corpo += ('<div class="testo" style="margin-top:22px"><p>The tables below are the official <strong>monthly basic pay</strong> rates for the U.S. uniformed services in '
              f'{ANNO}, cell by cell as printed in Schedule 8 of the President’s annual pay order. Pick your pay grade and find the column for your years of service: '
              '“2 or less” covers the first two years, “Over 2” starts after two full years, and so on. On a phone, swipe the table sideways.</p></div>')
    corpo += '<div class="azioni"><a class="btn" href="/calculator/">' + ico("calc") + 'Open the calculator</a><a class="btn sec" href="#grades">Pay by grade</a></div>'
    corpo += '<h2 id="enlisted">Enlisted pay chart 2026 (E-1 to E-9)</h2>' + tabella_categoria("E", rim) + note_tabella(rim, ("e1", "e9"))
    corpo += AD
    corpo += '<h2 id="warrant">Warrant officer pay chart 2026 (W-1 to W-5)</h2>' + tabella_categoria("W", rim)
    corpo += '<p class="small">The W-5 row starts at “Over 20” years: the official table prints no W-5 rate for shorter service.</p>'
    corpo += '<h2 id="officers">Officer pay chart 2026 (O-1 to O-10)</h2>' + tabella_categoria("O", rim) + note_tabella(rim, ("2", "5"))
    corpo += '<h2 id="prior-enlisted">O-1E to O-3E: officers with prior enlisted service</h2>' + tabella_categoria("OE", rim) + note_tabella(rim, ("oe", "cad"))
    corpo += f'<h2 id="grades">Pay by grade</h2><p>Every grade has its own page with the monthly and yearly figures, each step in years of service and the next increase.</p>{griglia_gradi()}'
    corpo += ('<h2>What the chart covers</h2><div class="testo">'
              + rim.t(f'<p>Schedule 8 sets the “rates of monthly basic pay (37 U.S.C. 203(a)) for members of the uniformed services”, so the same table applies in the Army, Navy, Air Force, Marine Corps, Space Force and Coast Guard.[[eo2026]] '
                      'By law the rates rise every January 1 by the percentage change in the Employment Cost Index for private-industry wages, unless Congress or the President sets a different figure.[[usc1009]] '
                      f'See the <a href="/pay-raise-history/">raise history</a> and the <a href="/2027-pay-raise/">status of the 2027 raise</a>.</p>'
                      '<p>Basic pay is one element of military compensation. The law lists the basic allowance for subsistence and the basic allowance for housing as separate elements;[[usc1009]] '
                      'this site covers basic pay only.</p>') + "</div>")
    voci = [
        ("2026 military pay chart", f"When did the 2026 military pay chart take effect?",
         f"On {P['effettiva_dal']}. The rates are in Schedule 8 of Executive Order {EO['ordine_esecutivo']} of {data_lunga(EO['firmato_il'])}, published in the Federal Register on {data_lunga(EO['pubblicato_il'])}.", "eo2026"),
        ("navy pay chart", "Is the pay chart the same for the Army, Navy, Air Force, Marines, Space Force and Coast Guard?",
         "Yes. Schedule 8 sets one table of monthly basic pay for members of the uniformed services, and its notes name senior positions in all of these services.", "eo2026"),
        ("warrant officer pay", "How much do warrant officers make in 2026?",
         f"Monthly basic pay runs from {soldi(riga('W-1')[0])} for a W-1 with 2 years or less of service to {soldi(massimo(riga('W-5')))} for a W-5 with over 38 years.", "eo2026"),
        ("military base pay", "Is basic pay the whole military paycheck?",
         "No. Basic pay is one element of compensation; the law lists the basic allowance for subsistence and the basic allowance for housing as separate elements. This site covers basic pay only.", "usc1009"),
    ]
    fh, fld = faq_blocco(voci, rim)
    corpo += fh + rim.elenco()
    testata = banda(f"Effective January 1, {ANNO}", f"Military Pay Chart {ANNO}",
                    f"Official monthly basic pay for every pay grade, E-1 to O-10, by years of service, copied from Executive Order {h(EO['ordine_esecutivo'])} in the Federal Register.")
    pagina("", f"Military Pay Chart {ANNO}: Official Basic Pay by Grade",
           f"Official {ANNO} military pay chart: monthly basic pay for E-1 to E-9, W-1 to W-5, O-1 to O-10 and O-1E to O-3E by years of service, from Executive Order {EO['ordine_esecutivo']}.",
           corpo, testata, jsonld=[fld])


def pagina_calcolatore():
    rim = Rimandi()
    corpo = '<div class="pull">' + calcolatore() + "</div>" + AD
    corpo += ('<h2 id="method">How the calculator works</h2><div class="testo">' + rim.t(
        f'<p>It looks up the cell for your grade and years of service in the official {ANNO} table[[eo2026]] and shows it as a monthly figure. The yearly figure is that amount × 12. '
        f'If the table prints a rate above the monthly cap that the order sets for your grade ({soldi(NOTE["tetto_O7_O10"])} for O-7 to O-10, {soldi(NOTE["tetto_O6_e_sotto"])} for O-6 and below), '
        'it shows the capped amount and says so.[[eo2026]]</p>'
        '<p>“Next step” is the next column of the same row with a higher rate: it tells you after how many years of service the table pays more, at today’s rates. '
        'Rates themselves change every January 1.[[usc1009]]</p>'
        '<p>What it does not include: allowances, special and incentive pays, bonuses, drill pay for reservists, tax and deductions. It is not a retirement calculator.</p>') + "</div>")
    corpo += ('<h2>Things to know about the table</h2>' + note_tabella(rim, ("e1", "oe", "e9")))
    voci = [("military pay calculator", "What does this military pay calculator include?",
             f"Monthly basic pay from the official {ANNO} table for your grade and years of service, the yearly amount (× 12) and the next step in the table. It does not include allowances, special pays, bonuses or taxes.", "eo2026")]
    fh, fld = faq_blocco(voci, rim)
    corpo += fh + rim.elenco()
    testata = banda("Calculator", f"Military Basic Pay Calculator {ANNO}",
                    "Choose a pay grade and your years of service: monthly and yearly basic pay from the official table, the cap where it applies, and the next step.", corta=False, icona="calc")
    pagina("calculator/", f"Military Basic Pay Calculator {ANNO} (All Grades)",
           f"Free {ANNO} military basic pay calculator: pick E-1 to O-10 and years of service to see monthly and yearly basic pay from the official table, caps included.",
           corpo, testata, briciole=[("Home", ""), ("Calculator", "calculator/")], jsonld=[fld,
           {"@context": "https://schema.org", "@type": "WebApplication", "name": f"Military Basic Pay Calculator {ANNO}", "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any", "url": f"{URL_SITO}/calculator/", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}], script_dati=script_dati())


FAQ_GRADO = {
    "e-1": ("e1 pay", "How much does an E-1 make in 2026?",
            lambda: f"{soldi(riga('E-1')[0])} a month in basic pay after 4 months of active duty, {soldi(riga('E-1<4')[0])} before that. The E-1 rate is the same at every length of service."),
    "e-4": ("how much does an e4 make", "How much does an E-4 make in 2026?",
            lambda: f"Monthly basic pay is {soldi(riga('E-4')[0])} with 2 years or less of service and reaches {soldi(massimo(riga('E-4')))} at over 6 years, the top of the E-4 table."),
    "e-5": ("e5 pay", "What is E-5 pay in 2026?",
            lambda: f"From {soldi(riga('E-5')[0])} a month with 2 years or less of service to {soldi(massimo(riga('E-5')))} at over 12 years, the top of the E-5 table."),
    "o-1": ("how much does an o1 make", "How much does an O-1 make in 2026?",
            lambda: f"{soldi(riga('O-1')[0])} a month with 2 years or less of service, {soldi(riga('O-1')[1])} over 2 years and {soldi(riga('O-1')[2])} from over 3 years on. Officers with over 4 years of prior enlisted or warrant service are paid as O-1E."),
    "o-3": ("o3 pay", "What is O-3 pay in 2026?",
            lambda: f"From {soldi(riga('O-3')[0])} a month with 2 years or less of service to {soldi(massimo(riga('O-3')))} from over 14 years."),
    "o-1e": ("o1e pay", "What is O-1E pay?",
             lambda: f"The O-1E rate is for commissioned officers credited with over 4 years of active duty service as an enlisted member or warrant officer. In {ANNO} it starts at {soldi(riga('O-1E')[3])} a month (over 4 years) and reaches {soldi(massimo(riga('O-1E')))}."),
    "w-1": ("warrant officer 1 pay", "How much does a W-1 warrant officer make?",
            lambda: f"From {soldi(riga('W-1')[0])} a month with 2 years or less of service to {soldi(massimo(riga('W-1')))} from over 20 years."),
}


def controlla_faq_grado():
    """Le FAQ dei gradi nominano colonne precise: devono restare vere con la tabella dell'anno."""
    attese = [("E-4", 4), ("E-5", 7), ("O-3", 8), ("O-1E", 3), ("W-1", 11), ("W-5", 20)]
    for k, i in attese:
        r = riga(k)
        prima = next(j for j, v in enumerate(r) if v is not None)
        if k == "O-1E" and prima != i:
            raise SystemExit(f"FAQ {k}: la riga ora inizia a {COL[prima]}")
        if k != "O-1E" and r.index(max(v for v in r if v is not None)) != i:
            raise SystemExit(f"FAQ {k}: il massimo non è più a {COL[i]}")
    if riga("O-1")[2] != massimo(riga("O-1")) or len(set(riga("E-1"))) != 1:
        raise SystemExit("FAQ O-1/E-1 da riscrivere")


def pagina_grado(slug, nome, cat, k):
    rim = Rimandi()
    r = riga(k)
    idx = [i for i, v in enumerate(r) if v is not None]
    pag = [pagabile(slug, r[i]) for i in idx]
    top = max(pag)
    i_top = idx[pag.index(top)]
    passi = [(idx[j], pag[j], pag[j] - pag[j - 1]) for j in range(1, len(idx)) if pag[j] > pag[j - 1] + 0.001]
    capped = any(pagabile(slug, r[i]) != r[i] for i in idx)
    eo_ref = rim.ref("eo2026")
    corpo = (f'<section class="card stats pull" aria-label="Key figures">'
             f'<div class="stat main"><b>{soldi(pag[0])}</b><span>Monthly at {anni_txt(idx[0])}{eo_ref}</span></div>'
             f'<div class="stat"><b>{soldi(top)}</b><span>Top monthly rate, from {anni_txt(i_top)}{eo_ref}</span></div>'
             f'<div class="stat"><b>{soldi(top * 12, False)}</b><span>Top rate per year (× 12, our arithmetic)</span></div>'
             f'<div class="stat"><b>{len(passi)}</b><span>Steps up with years of service in the {nome} row</span></div>'
             f'<p class="asof">{h(CAT_NOME[cat])} · effective {P["effettiva_dal"]} · Executive Order {EO["ordine_esecutivo"]}, Schedule 8 ({link_img(cat)}).</p></section>')
    # tabella del grado
    righe = []
    prec = None
    for i in idx:
        v, m = r[i], pagabile(slug, r[i])
        diff = "" if prec is None else ("–" if m - prec < 0.005 else f"+{soldi(m - prec)}")
        tetto = f' <span class="cap" title="capped">cap</span>' if m != v else ""
        righe.append(f'<tr><th scope="row">{h(COL[i])}</th><td class="n">{soldi(m)}{tetto}</td><td class="n">{soldi(m * 12)}</td><td class="n">{diff}</td></tr>')
        prec = m
    if k == "E-1":
        righe.insert(0, f'<tr><th scope="row">Under 4 months</th><td class="n">{soldi(riga("E-1<4")[0])}</td><td class="n">{soldi(riga("E-1<4")[0] * 12)}</td><td class="n"></td></tr>')
    cap = (f'{h(nome)} monthly basic pay, {ANNO}, by years of service. Monthly column: Schedule 8 of Executive Order {EO["ordine_esecutivo"]}{eo_ref}'
           + (" with the monthly cap applied" if capped else "") + '. Per year and change: our arithmetic.')
    corpo += (f'<h2 id="table">{h(nome)} pay table {ANNO}</h2>'
              f'<div class="tab"><table class="dati"><caption>{cap}</caption><thead><tr><th scope="col">Years of service</th><th scope="col" class="n">Monthly</th>'
              f'<th scope="col" class="n">Per year</th><th scope="col" class="n">Change</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    if len(idx) < 22:
        corpo += f'<p class="small">The official table prints no {h(nome)} rate before “{h(COL[idx[0]])}”, so those columns are left out.</p>'
    corpo += AD
    # quando arriva il prossimo aumento
    corpo += f'<h2 id="next-raise">When the next {h(nome)} raise comes</h2><div class="testo">'
    corpo += ('<p>Two things raise basic pay. The first is <strong>time in service</strong>: you move to the next column of the table when you pass the number of years it names. '
              f'In the {h(nome)} row the rate goes up at:</p>')
    if passi:
        corpo += '<ul class="passi">' + "".join(f'<li><b>{h(anni_txt(i).capitalize())}</b>: {soldi(m)} a month (+{soldi(d)})</li>' for i, m, d in passi) + "</ul>"
        corpo += f'<p>After {anni_txt(passi[-1][0])} the {h(nome)} rate does not rise with more service in the {ANNO} table.</p>'
    else:
        corpo += f'<p>No step: the {h(nome)} rate is the same at every length of service shown.</p>'
    corpo += rim.t('<p>The second is the <strong>annual adjustment</strong>: by law the rates of basic pay rise on January 1 of each year.[[usc1009]] '
                   f'In {ANNO} the table rose {next(x for x in ST["aumenti"] if x["anno"] == 2026)["tabelle"]["aumento"]}% over {ANNO - 1} in the rows we compared.[[eo2026,eo2025]] '
                   'See the <a href="/2027-pay-raise/">status of the 2027 raise</a> and the <a href="/pay-raise-history/">raise history</a>.</p></div>')
    # note del grado
    note = []
    if k == "E-1":
        note.append("e1")
    if k == "E-9":
        note.append("e9")
    if slug in TETTO2:
        note.append("2")
    if slug in TETTO5 and cat == "O" and k == "O-6":
        note.append("5")
    if cat == "OE" or k in ("O-1", "O-2", "O-3"):
        note.append("oe")
    if note:
        corpo += f'<h2>Notes in the official table</h2>{note_tabella(rim, tuple(note))}'
    if k == "O-9":
        corpo += f'<p class="testo">The O-9 and O-10 rows of the {ANNO} table are identical. <a href="/o-10/">See the O-10 page</a>.</p>'
    # confronto con i gradi vicini
    pos = [g for g in GRADI if g[2] == cat]
    j = [g[3] for g in pos].index(k)
    vicini = pos[max(0, j - 1): j + 2]
    cols = [i for i in (0, 3, 6, 10, 11, 15) if any(riga(g[3])[i] is not None for g in vicini)]
    if len(vicini) > 1 and cols:
        th = "".join(f'<th scope="col" class="n">{h(COL[i])}</th>' for i in cols)
        tr = ""
        for s2, n2, _, k2 in vicini:
            celle = "".join((f'<td class="n">{soldi(pagabile(s2, riga(k2)[i]))}</td>' if riga(k2)[i] is not None else '<td class="na">–</td>') for i in cols)
            tr += f'<tr{" class=\"qui\"" if k2 == k else ""}><th scope="row">' + (h(n2) if k2 == k else f'<a href="/{s2}/">{h(n2)}</a>') + f"</th>{celle}</tr>"
        corpo += (f'<h2>{h(nome)} compared with nearby grades</h2><div class="tab"><table class="dati"><caption>Monthly basic pay {ANNO} at selected years of service, caps applied. '
                  f'Source: Executive Order {EO["ordine_esecutivo"]}, Schedule 8{eo_ref}.</caption><thead><tr><th scope="col">Grade</th>{th}</tr></thead><tbody>{tr}</tbody></table></div>')
    c0 = idx[0] if len(idx) < 4 else 3
    corpo += f'<h2 id="calculator">Check a different grade or year</h2>' + calcolatore(slug, c0, f"{nome} and other grades")
    f = FAQ_GRADO.get(slug)
    fh, fld = faq_blocco([(f[0], f[1], f[2](), "eo2026")] if f else [], rim)
    corpo += fh
    corpo += f'<h2>Other pay grades</h2>{griglia_gradi(escludi=slug)}'
    corpo += rim.elenco()
    testata = banda(CAT_NOME[cat], f"{nome} Pay {ANNO}",
                    f"Monthly basic pay for {h(nome)} from <strong>{soldi(pag[0])}</strong> to <strong>{soldi(top)}</strong> in {ANNO}, by years of service, from the official table.")
    titolo = f"{nome} Pay {ANNO}: Monthly and Yearly Basic Pay by Years"
    descr = (f"{nome} basic pay {ANNO}: {soldi(pag[0])} to {soldi(top)} a month by years of service, yearly amounts, every step and the next raise, "
             f"from the official table (EO {EO['ordine_esecutivo']}).")
    pagina(f"{slug}/", titolo, descr, corpo, testata, briciole=[("Home", ""), (f"{nome} pay", f"{slug}/")], jsonld=[fld] if fld else None,
           indicizza=slug not in NOINDEX, script_dati=script_dati())


def storico_pagina():
    rim = Rimandi()
    righe = []
    for x in ST["aumenti"]:
        a = x["anno"]
        t = x.get("tabelle")
        if a > ANNO:
            continue
        fonte = rim.ref([f"eo{a}", f"eo{a - 1}"]) if f"eo{a - 1}" in FONTI and f"eo{a}" in FONTI else ""
        cel_t = (f'<td class="n">{t["aumento"]}%{fonte}</td><td class="n">{t["celle_alla_mediana"]} of {t["celle_confrontate"]}</td>' if t else
                 '<td class="na">not read</td><td class="na">–</td>')
        cel_e = f'<td class="n">{x["eci_formula"]}%{rim.ref("bls_eci")}</td>' if "eci_formula" in x else '<td class="na">–</td>'
        righe.append(f'<tr><th scope="row">January 1, {a}</th>{cel_t}{cel_e}</tr>')
    corpo = '<div class="testo pull card">' + rim.t(
        '<p>Each January 1 the basic pay tables of the uniformed services go up by one percentage for all grades, unless Congress or the President sets a different figure.[[usc1009]] '
        'Below, the raise is measured directly on the official tables: for each year we compare the same cells (grade × years of service) in two consecutive Schedule 8 tables of the '
        'Federal Register and take the median change, rounded to 0.1%. Next to it is the percentage the law’s formula gives: the 12-month change in the Employment Cost Index '
        'for private-industry wages and salaries in the July–September quarter two years earlier.[[usc1009,bls_eci]]</p>') + "</div>"
    corpo += (f'<h2>January pay raises {ST["aumenti"][0]["anno"]}–{ANNO}</h2><div class="tab"><table class="dati"><caption>Raise in the official pay table (our comparison of two Federal Register tables) '
              f'and the figure from the formula in 37 U.S.C. 1009{rim.ref("usc1009")} (BLS data{rim.ref("bls_eci")}).</caption><thead><tr><th scope="col">Effective</th><th scope="col" class="n">Raise in the table</th>'
              '<th scope="col" class="n">Cells at that raise</th><th scope="col" class="n">Formula (ECI)</th></tr></thead><tbody>' + "".join(righe) + "</tbody></table></div>")
    corpo += ('<p class="small">“Cells at that raise”: how many of the cells we could compare changed by the median percentage (within 0.06 points). The others are mostly rows that changed by a different amount '
              'and cells at a monthly cap. “Not read”: for January 2021 too few cells of the 2020 and 2021 tables (scanned images) could be read reliably, so we show only the formula figure. '
              'The ECI figure for January 2017 is not in the data we read.</p>')
    corpo += AD
    corpo += '<h2>What the table shows</h2><div class="testo">'
    corpo += rim.t('<p>In every year we could measure, the raise in the table equals the formula figure from the Employment Cost Index. '
                   'In the 2026 table, rows E-1 to E-5 are more than 3.8% above the January 2025 table at some years of service; the 2026 rates on the <a href="/e-1/">E-1</a> to <a href="/e-5/">E-5</a> pages are the figures in force.[[eo2026,eo2025]]</p>'
                   '<p>The law also lets the President send Congress an alternative pay plan before September 1 of the previous year, in a national emergency or serious economic conditions.[[usc1009]]</p></div>')
    serie = []
    for x in ST["aumenti"]:
        if 2018 <= x["anno"] <= ANNO:
            serie.append(f'{x["tabelle"]["aumento"]}%' if x.get("tabelle") else f'{x["eci_formula"]}% (formula figure)')
    voci = [("military pay increases by year", "How much did military pay go up each year?",
             f"From 2018 to {ANNO} the January raises were " + ", ".join(serie[:-1]) + " and " + serie[-1] + ", measured on the official pay tables.", "usc1009"),
            ("when do military pay raises take effect", "When do military pay raises take effect?",
             "On January 1. The law says the rates of basic pay are increased effective on January 1 of each year.", "usc1009")]
    fh, fld = faq_blocco(voci, rim)
    corpo += fh + rim.elenco()
    testata = banda("Raise history", f"Military Pay Raise History, {ST['aumenti'][0]['anno']}–{ANNO}",
                    "Every January raise measured on the official Federal Register pay tables, next to the figure from the Employment Cost Index formula in the law.", corta=True, icona="up")
    pagina("pay-raise-history/", f"Military Pay Raise History by Year ({ST['aumenti'][0]['anno']}–{ANNO})",
           f"Military pay raises by year, {ST['aumenti'][0]['anno']}–{ANNO}: each January raise measured on the official pay tables, with the Employment Cost Index formula figure.",
           corpo, testata, briciole=[("Home", ""), ("Pay raise history", "pay-raise-history/")], jsonld=[fld])


def pagina_2027():
    rim = Rimandi()
    x27 = next(x for x in ST["aumenti"] if x["anno"] == ANNO + 1)
    ric = ST["ricerca_2027"]
    if ric["risultati"]:
        raise SystemExit("C'è un ordine nuovo nel Federal Register: aggiornare il sito alle tabelle 2027 (NOTE.md)")
    corpo = (f'<section class="card stats pull" aria-label="2027 status">'
             f'<div class="stat main"><b>{x27["eci_formula"]}%</b><span>Formula figure for January 2027 (ECI, {x27["eci_trimestre"]}){rim.ref("usc1009,bls_eci")}</span></div>'
             f'<div class="stat"><b>5–7%</b><span>Proposed in the FY2027 budget, by grade group{rim.ref("budget2027")}</span></div>'
             f'<div class="stat"><b>Not yet</b><span>2027 pay table in the Federal Register{rim.ref("fr_search")}</span></div>'
             f'<div class="stat"><b>Jan 1</b><span>When the annual raise takes effect{rim.ref("usc1009")}</span></div>'
             f'<p class="asof">Status as of {data_lunga(ric["data"])}. Nothing on this page is a forecast: each line is what an official source says on that date.</p></section>')
    corpo += '<h2>Proposed, formula and enacted: three different things</h2><div class="testo">'
    corpo += rim.t(
        f'<p><strong>Formula figure: {x27["eci_formula"]}%.</strong> 37 U.S.C. 1009 sets the default raise: the percentage by which the Employment Cost Index for private-industry wages and salaries '
        f'in the July–September quarter of the year before the preceding year exceeds the same quarter a year earlier, rounded to 0.1%.[[usc1009]] For January 2027 that is the {x27["eci_trimestre"]} figure '
        f'published by the Bureau of Labor Statistics: {x27["eci_formula"]}%.[[bls_eci]]</p>'
        '<p><strong>Proposed: 7%, 6% or 5%.</strong> The President’s budget for fiscal year 2027 says that “the Budget funds a military pay raise of 7 percent for all military personnel ranked E-5 and below, '
        '6 percent for E-6 to O-3, and 5 percent for O-4 and above”. A budget is a request to Congress, not a pay table.[[budget2027]]</p>'
        f'<p><strong>Enacted: not published yet.</strong> The 2027 rates become official when the President’s annual order with a new Schedule 8 is published in the Federal Register. '
        f'On {data_lunga(ric["data"])} the Federal Register held no “Adjustments of Certain Rates of Pay” order published since January 1, {ANNO}.[[fr_search]] '
        f'In each of the last three years the order was published between December 23 and December 30.[[eo2026,eo2025,eo2024]]</p>') + "</div>"
    corpo += AD
    corpo += ('<h2>What we will not tell you</h2><div class="testo"><p>We do not publish a “2027 pay chart” before the official one exists: any such table would be a guess built on one of the figures above. '
              f'Until the new order is published, the official rates are the <a href="/">{ANNO} chart</a>.</p></div>')
    voci = [("2027 military pay chart", "When will the 2027 military pay chart come out?",
             f"When the President's annual pay order with Schedule 8 is published in the Federal Register. As of {data_lunga(ric['data'])} it had not been published; the last three were published between December 23 and December 30.", "fr_search,eo2026"),
            ("pay raise military", "Will military pay go up in 2027?",
             f"The law's formula gives {x27['eci_formula']}% for January 1, 2027, and the FY2027 budget proposed 7% for E-5 and below, 6% for E-6 to O-3 and 5% for O-4 and above. The final figure is the one in the 2027 pay table, not yet published as of {data_lunga(ric['data'])}.", "usc1009,bls_eci,budget2027")]
    fh, fld = faq_blocco(voci, rim)
    corpo += fh + rim.elenco()
    testata = banda(f"Status on {data_lunga(ric['data'])}", f"{ANNO + 1} Military Pay Raise: What Is Official So Far",
                    "The formula figure, the President’s budget proposal and the final pay table are different things. Here is what each official source says, with its date.", corta=True, icona="cal")
    pagina("2027-pay-raise/", f"{ANNO + 1} Military Pay Raise: Proposed vs Official (Status)",
           f"{ANNO + 1} military pay raise: {x27['eci_formula']}% formula figure, 5-7% proposed in the FY2027 budget, and whether the official 2027 pay table is out yet. Dated, sourced status.",
           corpo, testata, briciole=[("Home", ""), ("2027 pay raise", "2027-pay-raise/")], jsonld=[fld])


MODULO = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card">
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or figure<input type="text" name="page" required maxlength="300" placeholder="For example /e-5/, Over 4"></label>
<label>Your message<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<label>Your email (optional, only if you want a reply)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I agree that this message, and my email if I gave one, is stored to check and answer it (see <a href="/privacy/#corrections">privacy</a>).</span></label>
<button type="submit" class="btn">Send</button>
</form>"""


def come_controlliamo(stat):
    rim = Rimandi()
    L = P["letture"]
    corpo = '<div class="testo pull card">' + rim.t(
        f'<p>The {ANNO} tables in the Federal Register are printed as <strong>images</strong>, not text.[[eo2026]] So every one of the {L["celle"]} cells ({stat["importi"]} amounts and '
        f'{L["celle"] - stat["importi"]} dashes) was read three separate ways, and the site is built only if they agree.</p>') + "</div>"
    corpo += '<h2>How each cell is read</h2><div class="testo"><ol>'
    corpo += rim.t(f'<li>We download the original images of Schedule 8 from the Federal Register ({len(EO["immagini_schedule_8"])} images) and record a fingerprint (SHA-256) of each.[[eo2026]]</li>'
                   f'<li>A text-recognition program reads each cell on its own, cut out along the table’s grid lines, at two different magnifications. Both readings matched on <strong>{L["A_uguale_B"]} of {L["celle"]}</strong> cells.</li>'
                   f'<li>The official PDF from the Government Publishing Office carries its own text layer for the same images. Where that layer is readable it matched our reading on <strong>{L["C_uguale"]}</strong> cells and disagreed on none; on {L["C_illeggibile"]} cells it was garbled and could not be compared.</li>'
                   '<li>Any disagreement stops the build and the cell is checked by eye on the image.</li></ol></div>')
    corpo += '<h2>Checks on the numbers</h2><div class="testo"><ul>'
    corpo += rim.t(f'<li>Count: 28 rows × 22 columns = 616 cells, with dashes exactly where the official table prints them (for example W-5 before 20 years, E-9 before 10).</li>'
                   '<li>Order: in every row pay never falls as years of service rise, and at the same years a higher grade never pays less (O-1E pays at least O-1, and so on).</li>'
                   f'<li>Caps: no rate for O-6 and below is above the level V cap of {soldi(NOTE["tetto_O6_e_sotto"])}.</li>'
                   f'<li>Last year: {stat["confronto_2025"]} cells compared with the January 2025 table (Executive Order {P25["fonte"]["ordine_esecutivo"]}) are within 15 cents of the 2025 figure × 1.038. '
                   'Rows E-1 to E-5 and capped cells are left out of this check because they changed by a different amount.[[eo2025,eo2026]]</li>'
                   '<li>The calculator in your browser is checked against our own reference calculation on every grade and every column.</li></ul></div>')
    corpo += '<h2>What we could not read</h2><div class="testo">'
    corpo += ('<p>The pay pages of the Defense Finance and Accounting Service and of the Department of Defense answer our checking server with an error (403). We do not try to get round these blocks, so this site uses the Federal Register and govinfo.gov, '
              'where the official order is published. The 2020 table could not be read reliably enough for the raise history, which shows only the formula figure for that year.</p></div>')
    corpo += ('<h2>When we update</h2><div class="testo"><p>The pay order for the next year is normally published in the Federal Register in late December and takes effect on January 1. '
              'The site moves to the new table only after the same three readings and checks pass.</p></div>')
    corpo += ('<h2 id="corrections">Contact and corrections</h2><div class="testo"><p>Seen a figure that does not match the official table, or have a question about the site? Tell us the page and, if you can, the official source. '
              'Your email is optional. We cannot answer questions about individual pay: your finance office can.</p></div>' + MODULO)
    corpo += rim.elenco()
    testata = banda("How we check", "How we check every figure", "Three independent readings of each official cell, arithmetic checks, and the sources we could and could not read.", corta=True, icona="shield")
    pagina("how-we-check/", "How We Check the Military Pay Tables",
           "How Military Pay Chart reads the official 2026 pay tables: three readings of every cell, count and order checks, comparison with 2025, sources and corrections.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")])


def about():
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{NOME}</strong> is an independent publication, part of a small network of websites that turn official data into plain-language reference pages. '
             'It shows the U.S. military basic pay tables in a form that is easy to read on a phone, with one page per pay grade.</p>'
             '<p>We are <strong>not affiliated with</strong> the Department of Defense, any military branch, the Coast Guard, DFAS or any recruiter. We do not encourage anyone to enlist '
             'or advise on careers or money. The site gives general information, not financial advice.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Only figures printed in the official tables of the Federal Register, each linked to its source.</li>'
             '<li>Arithmetic on those figures (yearly amounts, differences, the next step), always labelled as ours.</li>'
             '<li>Where an official source cannot be read, or a figure is not final, we say so instead of filling the gap.</li></ul>'
             '<h2>How the site is paid for</h2><div class="testo"><p>The site shows advertising served by Google AdSense. Advertisers never decide what we publish.</p></div>'
             '<h2>Contact</h2><div class="testo"><p>Use the <a href="/how-we-check/#corrections">contact and corrections form</a>. For questions about your own pay, '
             'ask your unit’s finance office: they have your records.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, what it publishes and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", f"About {NOME}: an independent site publishing the official U.S. military basic pay tables. Not affiliated with the Department of Defense.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")])


def privacy():
    cookie = MON.privacy_cookie("en", SITO_ID) or ("<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. This site shows no advertising.</p>")
    california = MON.frase_california(SITO_ID) or "California residents: we do not sell or share personal information."
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {NOME} ({URL_SITO.replace("https://", "")}) collects. In short: very little.</p></div>'
             '<div class="testo"><h2>The calculator</h2><p>The calculator runs in your browser. The grade and years you choose are not sent to us; they appear in the page address only so you can share the result.</p>'
             '<p>The site remembers your choice of light or dark theme in your browser (local storage).</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             '<h2 id="corrections">Contact form</h2><p>If you use the <a href="/how-we-check/#corrections">contact and corrections form</a>, we receive the page you name, your message, the source link '
             'and, only if you give it, your email address, through Netlify Forms. We use it only to check and answer your message and keep it only as long as that takes. '
             'The legal basis is your consent, given with the tick box; you can ask us to delete your message through the same form.</p>'
             f'<h2>California</h2><p>{california}</p>'
             f'<h2>Changes</h2><p>Last update: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", f"Privacy | {NOME}", f"Privacy at {NOME}: the calculator runs in your browser, a cookie-free visit counter, and Google AdSense advertising with consent.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = f'<div class="pull card"><p>The page you asked for does not exist. Try the <a href="/">{ANNO} pay chart</a>, the <a href="/calculator/">calculator</a> or a pay grade below.</p></div>{griglia_gradi()}'
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
  # Pubblica solo se è cambiato qualcosa in milpay/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = milpay/sito, Build command vuoto, Publish directory = "."
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


def main():
    stat = controlla_tabella()
    controlla_faq_grado()
    for fid, es in ESITI.items():
        mancano = [c for c, ok in es.get("trovate", {}).items() if not ok]
        if es.get("http") != 200 or mancano:
            raise SystemExit(f"fonte {fid}: HTTP {es.get('http')} frasi mancanti {mancano} (rilanciare raccolta/fonti.py)")
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_risorse()
    home()
    pagina_calcolatore()
    for g in GRADI:
        pagina_grado(*g)
    storico_pagina()
    pagina_2027()
    come_controlliamo(stat)
    about()
    privacy()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + {len(NOINDEX)} noindex + 404. Celle {stat}.")


if __name__ == "__main__":
    main()
