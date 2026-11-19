"""Genera il sito statico "US College Aid" (USA, inglese) in collegeaid/sito/.

Uso (dalla radice del repository):
    python3 collegeaid/raccolta/fonti.py       # scarica le fonti ufficiali, controlla le frasi, scrive dati/fonti.json e dati/aiuti.json
    python3 collegeaid/raccolta/domanda.py <cartella con le risposte seodata>   # dati/domanda.json (solo quando si misurano ricerche nuove)
    python3 collegeaid/genera.py               # pagine in collegeaid/sito/
    python3 collegeaid/verifica.py [--browser] # controlli

Prova (idea B di studio-business/intelaiatura/fronti-2026-11-18-college.md): scadenze FAFSA 2027-28 per Stato (indice + 10 Stati con più
ricerche misurate), tassi dei prestiti federali 2026-27 e dal 2013, tetti dei prestiti dal 1/7/2026, calcolatore della rata (piano standard),
Repayment Assistance Plan con la formula della legge, prestiti PLUS dei genitori con il conto di quanto resta scoperto.
Ogni cifra viene da dati/aiuti.json, che raccolta/fonti.py ricava dai file ufficiali in dati/grezzi/. Le frasi tra virgolette sono copiate
alla lettera dalle fonti (dati/fonti.json). Le FAQ nascono da ricerche misurate (dati/domanda.json). Solo informazione, non consulenza.
Schede dei costi di 200 università (prova dell'idea A): raccolta/scorecard.py scarica il file College Scorecard e il dizionario dei dati,
raccolta/domanda_universita.py sceglie le 200 con più ricerche misurate; ogni cifra è copiata dal file, l'anno viene dal dizionario.
Riquadro dei partner (Splash Financial, SoFi): spento finché dati/affiliati.json non ha un link tracciato vero e "attivo": true.
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

URL_SITO = "https://us-college-aid.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso (c'è anche in verifica.py)
NOME = "US College Aid"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "collegeaid"  # nome del sito in monetizzazione.json
ADSENSE_HEAD = MON.script_adsense(SITO_ID)


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


A = carica("aiuti.json")
FONTI = carica("fonti.json")["fonti"]
DOM = carica("domanda.json")
AFF = carica("affiliati.json")
CONTROLLO = date.fromisoformat(A["letto_il"])
FAFSA, TASSI, LIM, RAP, STD = A["fafsa"], A["tassi"], A["limiti"], A["rimborso"]["rap"], A["rimborso"]["standard"]
ANNO = FAFSA["anno"]                       # «2027–28»
ANNO_TASSI = f'{TASSI["dal"][:4]}–{TASSI["al"][2:4]}'   # «2026–27»
VOCI = {v["sigla"]: v for v in FAFSA["voci"]}
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MESI_MODULO = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
T_UG, T_GRAD, T_PLUS = (r["tasso"] for r in TASSI["righe"])

# I 10 Stati con una pagina propria: quelli con più ricerche misurate «fafsa deadline <Stato>» (dati/domanda.json, 19/11/2026).
# Per ogni Stato: slug e le righe «che cosa / data / nota», scritte a mano dal testo del modulo. genera.py si ferma se una data qui
# non è nel testo ufficiale di quello Stato o se il testo ufficiale ha una data che qui manca.
STATI = {
    "CA": {"slug": "california", "righe": [
        ("Many state financial aid programs, including Cal Grant", "2027-03-02", "Date postmarked. Cal Grant also needs a school-certified GPA by the same date."),
        ("Additional community college Cal Grants", "2027-09-02", "Date postmarked.")],
        "punti": ["The March 2 date is marked “date postmarked”, an exception to the form’s general rule that dates are when the form must be received.",
                  "For Cal Grant the FAFSA alone is not enough: the form says a school-certified GPA must also be submitted by March 2, 2027.",
                  "Students without a Social Security card, or with one issued through DACA, are told to fill out the California Dream Act Application instead.",
                  "For anything else the form sends you to the California Student Aid Commission or your financial aid office."]},
    "TX": {"slug": "texas", "righe": [
        ("Priority consideration for state aid", "2027-01-15", "Private and two-year institutions may have different deadlines.")],
        "punti": ["January 15, 2027 is a priority date, the earliest fixed date of the ten states on this site.",
                  "The form adds that more forms may be required.",
                  "Private and two-year institutions may have different deadlines: the form tells you to check with your financial aid office."]},
    "FL": {"slug": "florida", "righe": [
        ("State aid", "2027-05-15", "Date processed, not date received.")],
        "punti": ["The Florida date is marked “date processed”. The form does not explain how long processing takes, so do not wait for the last days.",
                  "The form also says to check with your financial aid office."]},
    "MI": {"slug": "michigan", "righe": [
        ("Michigan Competitive Scholarship and Michigan Tuition Grant, priority consideration", "2027-07-01", "")],
        "punti": ["The form names two programs, the Michigan Competitive Scholarship and the Michigan Tuition Grant, and gives July 1, 2027 as their priority date.",
                  "It lists no date for other Michigan aid: ask your financial aid office."]},
    "OH": {"slug": "ohio", "righe": [
        ("State aid", "2027-10-01", "")],
        "punti": ["Ohio’s entry is a single date with no conditions: October 1, 2027, three months into the 2027–28 award year.",
                  "The form’s general rule applies: it is the date by which the form must be received."]},
    "NJ": {"slug": "new-jersey", "righe": [
        ("Renewal applicants (2026–27 Tuition Aid Grant recipients)", "2027-04-15", ""),
        ("All other applicants, fall and spring terms", "2027-09-15", ""),
        ("All other applicants, spring term only", "2028-02-15", "")],
        "punti": ["New Jersey has three dates, and which one is yours depends on whether you received a Tuition Aid Grant in 2026–27.",
                  "Renewal applicants have the earliest date, April 15, 2027.",
                  "Everyone else has until September 15, 2027 for the fall and spring terms, or February 15, 2028 if applying for the spring term only."]},
    "IL": {"slug": "illinois", "righe": [
        ("State aid, including the Monetary Award Program (MAP)", "2026-10-01", "No closing date: apply as soon as possible after this date. MAP awards are made while funds exist.")],
        "punti": ["Illinois has no closing date on the form. The instruction is to apply as soon as possible after October 1, 2026.",
                  "For the Monetary Award Program (MAP) the form says awards are made while funds exist, so an early application matters more than in states with a fixed date.",
                  "The form refers to the Illinois Student Assistance Commission’s website for program information."]},
    "MA": {"slug": "massachusetts", "righe": [
        ("Priority consideration for state aid", "2027-05-01", "")],
        "punti": ["May 1, 2027 is a priority date. The form gives no other Massachusetts date."]},
    "IN": {"slug": "indiana", "righe": [
        ("Frank O’Bannon Grant, 21st Century Scholarship, Workforce Ready Grant and Adult Student Grant", "2027-04-15", "")],
        "punti": ["One date, April 15, 2027, covers the four programs the form names.",
                  "The form’s general rule applies: it is the date by which the form must be received."]},
    "PA": {"slug": "pennsylvania", "righe": [
        ("All other applicants", "2027-05-01", ""),
        ("First-time applicants at a community college, business/trade/technical school, hospital school of nursing, designated Pennsylvania open-admission institution, or in a nontransferable two-year program", "2027-08-01", "")],
        "punti": ["Pennsylvania has two dates. May 1, 2027 applies to everyone who is not in the first group.",
                  "August 1, 2027 applies only to first-time applicants at the kinds of school the form lists.",
                  "The form adds that more forms may be required."]},
}
ORDINE_STATI = ["CA", "TX", "FL", "MI", "OH", "NJ", "IL", "MA", "IN", "PA"]   # per ricerche misurate
RICERCA_STATO = {s: f'fafsa deadline {VOCI[s]["nome"].lower()}' for s in ORDINE_STATI}


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def giorno(iso):
    return data_lunga(date.fromisoformat(iso))


def data_modulo(iso):
    """La data come la scrive il modulo FAFSA: «Jan. 15, 2027», «March 2, 2027»."""
    d = date.fromisoformat(iso)
    return f"{MESI_MODULO[d.month - 1]} {d.day}, {d.year}"


def usd(n):
    return f"${n:,}"


def usdc(cent):
    return f"${cent // 100:,}.{cent % 100:02d}"


def slug_stato(s):
    return f'fafsa-deadlines/{STATI[s]["slug"]}/'


def conto(iso):
    """Segnaposto del conto dei giorni: lo riempie app.js con la data di chi legge (nell'HTML resta nascosto)."""
    return f'<span class="conto" data-giorni="{iso}" hidden></span>'


# ---------------------------------------------------------------- conti per gli esempi in pagina (stesse formule di app.js; verifica.py li rifà a parte)
def mill(tasso):
    """«6.52» -> 6520 (millesimi di punto percentuale)."""
    a, b = tasso.split(".")
    return int(a) * 1000 + int((b + "000")[:3])


def anni_standard(saldo_cent):
    for f in STD["fasce"]:
        if f["sotto"] is None or saldo_cent < f["sotto"] * 100:
            return f["anni"]


def js_round(x):
    import math
    return math.floor(x + 0.5)


def interesse_mese(saldo, tasso):
    return (saldo * tasso * 2 + 1200000) // 2400000


def piano(saldo, tasso, mesi):
    if tasso == 0:
        rata = js_round(saldo / mesi)
    else:
        r = tasso / 1200000
        rata = js_round(saldo * r / (1 - (1 + r) ** (-mesi)))
    if rata < STD["minimo_mese"] * 100:
        raise SystemExit(f"esempio in pagina sotto il pagamento minimo di {STD['minimo_mese']} $: scegliere un saldo più alto")
    resto, pagato, interessi, n = saldo, 0, 0, 0
    while resto > 0:
        i = interesse_mese(resto, tasso)
        dovuto = resto + i
        paga = dovuto if (n == mesi - 1 or dovuto < rata) else rata
        resto, pagato, interessi, n = dovuto - paga, pagato + paga, interessi + i, n + 1
    return {"rata": rata, "mesi": n, "pagato": pagato, "interessi": interessi}


def rap_base_anno(reddito):
    for s in RAP["scaglioni"]:
        if s["fino_a"] is None or reddito <= s["fino_a"]:
            return s["fisso_anno"] * 100 if s["pc"] is None else reddito * s["pc"]


def rap_mese(reddito, carico):
    return max(js_round(rap_base_anno(reddito) / 12) - carico * RAP["per_dipendente_mese"] * 100, RAP["minimo_mese"] * 100)


def buco(costo, anni):
    righe, tot_s, tot_g = [], 0, 0
    for a in range(anni):
        tetto = LIM["dipendente"]["anni"][min(a, 2)]["totale"] * 100
        s = max(0, min(tetto, LIM["dipendente"]["totale"] * 100 - tot_s, costo))
        g = max(0, min(LIM["genitori"]["anno"] * 100, LIM["genitori"]["totale"] * 100 - tot_g, costo - s))
        tot_s, tot_g = tot_s + s, tot_g + g
        righe.append({"anno": a + 1, "costo": costo, "studente": s, "genitori": g, "resto": costo - s - g})
    return righe


# ---------------------------------------------------------------- fonti e citazioni
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

    def cit(self, fid, chiave):
        """Frase copiata alla lettera dalla fonte (controllata da raccolta/fonti.py sul file grezzo)."""
        f = FONTI[fid]
        if not f["trovate"].get(chiave):
            raise SystemExit(f"citazione {fid}/{chiave} non trovata nel file grezzo")
        return (f'<blockquote class="cit" data-fonte="{fid}" data-frase="{chiave}"><p>“<span data-cit>{h(f["frasi"][chiave])}</span>”</p>'
                f'<cite>{h(f["chi"])}, {h(f["titolo"])}{self.ref(fid)}</cite></blockquote>')

    def voce(self, sigla):
        """Il testo del modulo FAFSA per uno Stato, parola per parola (dati/aiuti.json, letto dalla pagina 2 del PDF)."""
        v = VOCI[sigla]
        return (f'<blockquote class="cit" data-voce="{sigla}"><p>“<span data-voce-testo>{h(v["testo"])}</span>”</p>'
                f'<cite>{h(v["nome"])} ({sigla}), {ANNO} FAFSA form, page 2{self.ref("fafsa_2728")}</cite></blockquote>')

    def elenco(self, nota=None):
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = FONTI[i]
            voci.append(f'<li id="f{n}"><a href="{h(f.get("pagina") or f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. '
                        f'<span class="small">read {giorno(f["letto_il"])}</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2><ol>{"".join(voci)}</ol>'
                + (nota or '<p class="small">Dates, rates and dollar limits are copied from the official documents above; where a figure is our own arithmetic, the page says so. '
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
LOGO_TESTO = "<span>US College <b>Aid</b></span>"


def ico(nome, cls="ico"):
    if nome not in stile.ICONE:
        raise SystemExit(f"icona sconosciuta: {nome}")
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
TITOLI, DESCRIZIONI = {}, {}
P_SCAD, P_TASSI, P_LIM, P_RATA, P_RAP, P_PLUS = ("fafsa-deadlines/", "student-loan-interest-rates/", "federal-student-loan-limits/",
                                                 "student-loan-payment-calculator/", "repayment-assistance-plan/", "parent-plus-loans/")
MENU = [(P_SCAD, "FAFSA deadlines"), (P_TASSI, "Loan rates"), (P_LIM, "Loan limits"), (P_RATA, "Payment calculator"), (P_RAP, "RAP"), (P_PLUS, "Parent PLUS"), ("college-costs/", "College costs")]
DISCLAIMER = ("<strong>Information, not financial advice.</strong> This is an independent site, not affiliated with the U.S. Department of Education, Federal Student Aid or any state agency, college or lender. "
              "Dates, rates and limits are copied from the official documents listed under Sources on the date shown; they can change, and your own case can differ. "
              "Before you decide anything, confirm it with the financial aid office of your college or with your loan servicer.")


def menu_html(percorso, mobile=False):
    return "".join(f'<a href="/{u}"' + (' aria-current="page"' if percorso.startswith(u) else "") + (' class="w2"' if mobile else "") + f">{h(t)}</a>" for u, t in MENU)


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
    f_scad = f'<li><a href="/{P_SCAD}">All states, {ANNO}</a></li>' + "".join(f'<li><a href="/{slug_stato(s)}">{h(VOCI[s]["nome"])} FAFSA deadline</a></li>' for s in ORDINE_STATI)
    f_prestiti = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [(P_TASSI, f"Federal loan interest rates {ANNO_TASSI}"), (P_LIM, "Federal loan limits"),
                                                                         (P_RATA, "Student loan payment calculator"), (P_RAP, "Repayment Assistance Plan (RAP)"), (P_PLUS, "Parent PLUS loans")])
    guide = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [("", "Home"), ("college-costs/", "College costs: tuition and net price"), ("how-we-check/", "How we check and sources"), ("about/", "About"),
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
<meta name="theme-color" content="#12312B">
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
<p><strong>{NOME}</strong> puts FAFSA deadlines and federal student loan rates, limits and repayment formulas on plain pages, copied from the official form, the Federal Register and the law,
with the source next to every figure. Independent site, not a government website.</p>
<p>Official sources read on {data_lunga(CONTROLLO)}.</p>
</div><div>
<h2>FAFSA deadlines {ANNO}</h2><ul>{f_scad}</ul>
</div><div>
<h2>Federal student loans</h2><ul>{f_prestiti}</ul>
</div><div>
<h2>Site</h2><ul>{guide}</ul>
</div></div>
<p class="f-base">General information only, not financial, tax or legal advice. Not affiliated with the U.S. Department of Education or Federal Student Aid. FAFSA is a registered trademark of Federal Student Aid, U.S. Department of Education.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, corta=False, icona="chart", extra=""):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def fatti(voci, sotto, classe=""):
    return (f'<div class="card fatti pull{classe}">' + "".join(f'<div class="fatto{" main" if i == 0 else ""}"><b>{b}</b><span>{h(t)}</span></div>' for i, (b, t) in enumerate(voci))
            + f'<p class="asof">{sotto}</p></div>')


def nota(html_, info=False):
    return f'<div class="nota{" info" if info else ""}">{ico("info" if info else "alert")}{html_}</div>'


def tabella(caption, intest, righe, classe="", stretta=False):
    th = "".join(f'<th scope="col"{" class=\"n\"" if n else ""}>{h(t)}</th>' for t, n in intest)
    return (f'<div class="tab{" stretta" if stretta else ""}"><table class="dati {classe}"><caption><span>{caption}</span></caption><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>')


# ---------------------------------------------------------------- domande frequenti (solo da ricerche misurate)
def volume(frase):
    for r in DOM["ricerche"]:
        if r["frase"] == frase:
            return r["volume_mese"]
    return VOLUMI_UNI.get(frase, 0)   # frasi «<università> tuition» e «<università> cost» (dati/domanda_universita.json)


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


# ---------------------------------------------------------------- riquadro dei partner (spento finché non c'è un link vero)
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
        attivi.append(p)
    return attivi


PARTNER = partner_attivi()


def riquadro_partner():
    """Solo nella pagina del calcolatore della rata, sotto il calcolatore e gli esempi: mai sopra la risposta gratuita."""
    if not PARTNER:
        return ""
    r = AFF["riquadro"]
    voci = "".join(f'<li><b>{h(p["nome"])}</b><p>{h(p["riga"])}</p>'
                   f'<a class="btn" href="{h(p["link"])}" rel="sponsored nofollow noopener">{h(p["pulsante"])}{ico("arrow")}</a></li>' for p in PARTNER)
    return (f'<aside class="partner" data-partner aria-label="Advertisement"><p class="tag">{h(r["etichetta"])}</p><h3>{h(r["titolo"])}</h3><p>{h(r["testo"])}</p>'
            f'<ul class="partner-l">{voci}</ul><p class="small">{h(r["trasparenza"])}</p></aside>')


# ---------------------------------------------------------------- scadenze FAFSA
def tipo_voce(v):
    if any(d != FAFSA["apertura"] for d in v["date"]):
        return "date"
    return "asap" if "soon as possible" in v["testo"] else "check"


def chips(v):
    out = [f'<span class="chip">{data_modulo(d)}</span>{conto(d)}' for d in v["date"] if d != FAFSA["apertura"]]
    if "soon as possible" in v["testo"]:
        out.append(f'<span class="chip oro">As soon as possible after {data_modulo(FAFSA["apertura"])}</span>')
    if not out:
        out.append('<span class="chip grigio">No date on the form</span>')
    return "<br>".join(out)


def prima_data(s):
    """La prima data fissa di uno Stato (None se il modulo non ne ha)."""
    d = [x for x in VOCI[s]["date"] if x != FAFSA["apertura"]]
    return d[0] if d else None


def controlla_stati():
    for s, info in STATI.items():
        v = VOCI[s]
        mie = sorted({r[1] for r in info["righe"]})
        if mie != v["date"]:
            raise SystemExit(f"STATI[{s}]: le date delle righe {mie} non sono quelle del modulo {v['date']}")
        for _, iso, _ in info["righe"]:
            if data_modulo(iso) not in v["testo"]:
                raise SystemExit(f"STATI[{s}]: «{data_modulo(iso)}» non è nel testo del modulo")
        if s == "TX" and prima_data("TX") != min(prima_data(o) for o in STATI if prima_data(o)):
            raise SystemExit("STATI[TX]: il Texas non ha più la prima data dei dieci Stati (correggere il testo)")
        if volume(RICERCA_STATO[s]) <= 0:
            raise SystemExit(f"STATI[{s}]: nessuna ricerca misurata")


def righe_federali():
    return (f'<li class="fed"><div class="cosa">FAFSA form opened<small>Earliest date to submit the {ANNO} form, for federal aid in every state.</small></div>'
            f'<div class="quando">{giorno(FAFSA["apertura"])}{conto(FAFSA["apertura"])}</div></li>'
            f'<li class="fed"><div class="cosa">Federal deadline<small>Last day the {ANNO} form can be received for federal aid. Your college also needs your correct, complete information by your last day of enrollment in {ANNO}.</small></div>'
            f'<div class="quando">{giorno(FAFSA["chiusura_federale"])}{conto(FAFSA["chiusura_federale"])}</div></li>')


def indice_scadenze():
    rim = Rimandi()
    con_data = [v for v in FAFSA["voci"] if tipo_voce(v) == "date"]
    asap = [v for v in FAFSA["voci"] if tipo_voce(v) == "asap"]
    check = [v for v in FAFSA["voci"] if tipo_voce(v) == "check"]
    stati_veri = [v for v in FAFSA["voci"] if not v["territorio"]]
    prima = min((d, v["nome"]) for v in con_data for d in v["date"] if d != FAFSA["apertura"])
    prima_prior = "priority consideration" in next(v["testo"] for v in con_data if v["nome"] == prima[1])
    voci = [(giorno(FAFSA["chiusura_federale"]), f"federal deadline for the {ANNO} FAFSA form"), (giorno(FAFSA["apertura"]), "the form opened: earliest date to apply"),
            (str(len(con_data)), f"states and territories with at least one fixed date, out of {len(FAFSA['voci'])}"), (giorno(prima[0]), f"earliest fixed state date ({prima[1]}{', priority' if prima_prior else ''})")]
    sotto = f'{ico("info")} {ANNO} award year: <strong>{giorno(FAFSA["anno_dal"])} to {giorno(FAFSA["anno_al"])}</strong> · official form read on {giorno(FONTI["fafsa_2728"]["letto_il"])}{rim.ref("fafsa_2728")}'
    corpo = fatti(voci, sotto)
    corpo += (f'<h2 id="federal">The two federal dates</h2><div class="testo"><p>The FAFSA form for {ANNO} has one federal window. It is the same in every state, and it is much longer than most state deadlines.</p></div>'
              f'<ul class="date-l">{righe_federali()}</ul>' + rim.cit("fafsa_2728", "federale") + rim.cit("fafsa_2728", "ultimo_giorno"))
    corpo += (f'<h2 id="states">State deadlines for {ANNO}</h2><div class="testo"><p>States and colleges award their own aid, and many set an earlier date than the federal one. '
              f'The table copies, word for word, what page 2 of the official {ANNO} FAFSA form says for each of the 50 states, the District of Columbia and {sum(1 for v in FAFSA["voci"] if v["territorio"])} territories and freely associated states. '
              f'The last column lists every date written in that text.</p></div>' + rim.cit("fafsa_2728", "ricevuto"))
    righe = []
    for v in FAFSA["voci"]:
        nome = f'<a href="/{slug_stato(v["sigla"])}">{h(v["nome"])}</a>' if v["sigla"] in STATI else h(v["nome"])
        righe.append(f'<tr data-nome="{h(v["nome"].lower())} {v["sigla"].lower()}" data-tipo="{tipo_voce(v)}" data-sigla="{v["sigla"]}"><th scope="row">{nome} <span class="small">({v["sigla"]})</span></th>'
                     f'<td class="uff" data-voce-testo>{h(v["testo"])}</td><td class="d">{chips(v)}</td></tr>')
    corpo += (f'<div data-scadenze><div class="card filtri" data-filtri hidden><label>Find a state<input type="search" data-cerca placeholder="For example Ohio or OH" autocomplete="off"></label>'
              f'<label>Show<select data-tipo><option value="">All {len(FAFSA["voci"])} states and territories</option><option value="date">With a fixed date ({len(con_data)})</option>'
              f'<option value="asap">As soon as possible, no fixed date ({len(asap)})</option><option value="check">Check with your financial aid office ({len(check)})</option></select></label>'
              f'<p class="stato-t" data-stato aria-live="polite"></p></div>'
              + tabella(f'{ANNO} FAFSA deadlines by state, as printed on page 2 of the official form.{rim.ref("fafsa_2728")}',
                        [("State", 0), ("What the official form says", 0), ("Dates in that text", 0)], righe, "scad ampia")
              + '<p class="card" data-vuoto hidden>No state matches. Clear the search box to see them all.</p></div>')
    corpo += ('<h2 id="read">How to read a state entry</h2><div class="testo"><ul>'
              f'<li><strong>A plain date</strong> is the day the form must be received, unless the entry says otherwise. California writes “date postmarked” and Florida “date processed”.</li>'
              f'<li><strong>“For priority consideration”</strong> ({sum(1 for v in FAFSA["voci"] if "priority consideration" in v["testo"])} entries) is not written as a final cutoff. The form does not say what happens to later applications, so ask the state agency or your financial aid office.</li>'
              f'<li><strong>“As soon as possible after Oct. 1, 2026”</strong> ({sum(1 for v in FAFSA["voci"] if "soon as possible" in v["testo"])} entries), often with “Awards made while funds exist” ({sum(1 for v in FAFSA["voci"] if "while funds exist" in v["testo"])} entries): there may be no closing date, but the money can run out.</li>'
              f'<li><strong>“Check with your financial aid office”</strong> with nothing else ({len(check)} entries, {sum(1 for v in check if not v["territorio"])} of them states): the form gives no state date at all. The college sets it.</li>'
              f'<li><strong>“More forms may be required”</strong> ({sum(1 for v in FAFSA["voci"] if "ore forms may be required" in v["testo"])} entries): the FAFSA alone may not be enough for state aid.</li></ul></div>'
              + rim.cit("fafsa_2728", "statale"))
    corpo += nota('<p><strong>Colleges have their own dates too.</strong> A college can set a financial aid deadline that is earlier than both the state and the federal one, and the FAFSA form does not list them. '
                  'The college’s financial aid office is the only source for that date.</p>')
    griglia = "".join(f'<li><a href="/{slug_stato(s)}"><b>{h(VOCI[s]["nome"])}</b><small>{data_modulo(prima_data(s)) if prima_data(s) else "As soon as possible"}</small></a></li>' for s in ORDINE_STATI)
    corpo += (f'<h2 id="pages">State pages</h2><div class="testo"><p>The ten states people search for most have a page of their own, with each date explained and the federal dates next to it.</p></div>'
              f'<ul class="griglia larga">{griglia}</ul>')
    faq_html, faq_ld = faq_blocco([
        ("fafsa deadline", f"What is the FAFSA deadline for {ANNO}?",
         f"For federal aid, the {ANNO} FAFSA form must be received no later than {giorno(FAFSA['chiusura_federale'])}. State and college deadlines are usually earlier: the first fixed state date on the official form is {giorno(prima[0])} ({prima[1]}{', for priority consideration' if prima_prior else ''}).", "fafsa_2728"),
        ("when is the fafsa deadline", "When is the FAFSA deadline in my state?",
         f"It depends on the state. On the official {ANNO} form, {len(con_data)} of {len(FAFSA['voci'])} states and territories have at least one fixed date, {len(asap)} say only to apply as soon as possible after {giorno(FAFSA['apertura'])}, and {len(check)} say to check with your financial aid office. The table above has the exact wording for each.", "fafsa_2728"),
        ("when does fafsa close", f"When does the {ANNO} FAFSA close?",
         f"The federal form for {ANNO} closes on {giorno(FAFSA['chiusura_federale'])}, the last day of that award year. The form also says your college must have your correct, complete information by your last day of enrollment in the {ANNO} school year.", "fafsa_2728"),
        ("fafsa priority deadline", "What is a FAFSA priority deadline?",
         f"Some state entries on the form begin with “For priority consideration, submit by” a date. The form does not define the term or say what happens to applications received later, so treat the priority date as the date to meet and ask the state agency or your financial aid office about anything after it.", "fafsa_2728"),
        ("fafsa deadlines by state", "Where do these state deadlines come from?",
         f"From page 2 of the official {ANNO} FAFSA form published by Federal Student Aid, read on {giorno(FONTI['fafsa_2728']['letto_il'])}. Each entry in the table is the form’s own text. States can change their dates after the form is printed, so confirm with the state agency or your college.", "fafsa_2728"),
        ("federal fafsa deadline", "Is the federal FAFSA deadline different from the state one?",
         f"Yes. The federal deadline is one date for everyone, {giorno(FAFSA['chiusura_federale'])} for {ANNO}. State aid has its own deadlines, and the form warns that a state or college deadline may be as early as {giorno(FAFSA['apertura'])} or that aid may be awarded first come, first served.", "fafsa_2728"),
    ], rim)
    corpo += faq_html + rim.elenco()
    testata = banda(f"FAFSA {ANNO} · official form", f"FAFSA deadlines for {ANNO}, state by state",
                    f"The federal deadline and the wording of the official FAFSA form for every state, with the dates pulled out. Read from the form on {giorno(FONTI['fafsa_2728']['letto_il'])}.", icona="calendar",
                    extra=f'<p class="azioni"><a class="btn salta" href="#states">Jump to your state{ico("arrow")}</a></p>')
    pagina(P_SCAD, f"FAFSA Deadline {ANNO} by State: Official Dates, All States",
           f"FAFSA deadlines for {ANNO}: federal deadline {giorno(FAFSA['chiusura_federale'])} and the state deadline for all 50 states, copied from the official form.",
           corpo, testata, briciole=[("Home", ""), ("FAFSA deadlines", P_SCAD)], jsonld=[faq_ld])


def pagina_stato(s):
    rim = Rimandi()
    v, info = VOCI[s], STATI[s]
    nome = v["nome"]
    prima = prima_data(s)
    righe = ""
    for cosa, iso, nota_ in info["righe"]:
        if iso == FAFSA["apertura"]:
            righe += (f'<li><div class="cosa">{h(cosa)}<small>{h(nota_)}</small></div><div class="quando">As soon as possible<small>after {giorno(iso)}</small></div></li>')
        else:
            righe += (f'<li><div class="cosa">{h(cosa)}' + (f'<small>{h(nota_)}</small>' if nota_ else "") + f'</div><div class="quando">{giorno(iso)}{conto(iso)}</div></li>')
    corpo = f'<div class="pull"><ul class="date-l">{righe}{righe_federali()}</ul></div>'
    corpo += (f'<h2 id="official">What the official form says for {h(nome)}</h2><div class="testo"><p>This is the complete {h(nome)} entry on page 2 of the {ANNO} FAFSA form, word for word.</p></div>'
              + rim.voce(s) + rim.cit("fafsa_2728", "ricevuto"))
    corpo += f'<h2 id="means">What that means</h2><div class="testo"><ul>{"".join(f"<li>{h(p)}</li>" for p in info["punti"])}</ul></div>'
    corpo += (f'<h2 id="federal">State aid and federal aid have different dates</h2><div class="testo">'
              f'<p>The {h(nome)} date{"s" if len(info["righe"]) > 1 else ""} above {"are" if len(info["righe"]) > 1 else "is"} for state aid. Federal aid (federal grants, work-study and loans) follows the federal window: '
              f'the form opened on {giorno(FAFSA["apertura"])} and must be received by {giorno(FAFSA["chiusura_federale"])}.{rim.ref("fafsa_2728")} '
              f'Missing a state date does not close the federal form, but it can cost you the state aid that date is for.</p></div>'
              + rim.cit("fafsa_2728", "federale") + rim.cit("fafsa_2728", "statale"))
    corpo += nota(f'<p><strong>Your college may want the form earlier.</strong> The FAFSA form does not list college deadlines. Ask the financial aid office of each college you are applying to; the form calls it '
                  f'“the best place for information about student aid”.{rim.ref("fafsa_2728")}</p>')
    altri = []
    for o in ORDINE_STATI:
        if o == s:
            continue
        p = prima_data(o)
        altri.append(f'<tr><th scope="row"><a href="/{slug_stato(o)}">{h(VOCI[o]["nome"])}</a></th><td class="forte">{data_modulo(p) if p else "As soon as possible"}</td>'
                     f'<td>{h(STATI[o]["righe"][0][0])}</td></tr>')
    corpo += (f'<h2 id="others">Other states</h2>' + tabella(f'First date on the official {ANNO} form in the other nine states with a page here.{rim.ref("fafsa_2728")}',
                                                           [("State", 0), ("First date", 0), ("Applies to", 0)], altri, "ampia")
              + f'<p class="azioni"><a class="btn sec" href="/{P_SCAD}">All states and territories{ico("arrow")}</a></p>')
    corpo += (f'<h2 id="loans">If aid does not cover the bill: federal loan numbers</h2><div class="testo"><p>Federal student loans are requested through the same FAFSA form. For loans first disbursed from {giorno(TASSI["dal"])} '
              f'to June 30, {TASSI["al"][:4]}, the fixed rate for undergraduates is {T_UG}%{rim.ref("fr_tassi")}, and a first-year dependent student can borrow up to {usd(LIM["dipendente"]["anni"][0]["totale"])} for the year{rim.ref("manuale")}.</p>'
              f'<p class="azioni"><a class="btn sec" href="/{P_TASSI}">Loan interest rates</a><a class="btn sec" href="/{P_LIM}">Loan limits</a><a class="btn sec" href="/{P_RATA}">Payment calculator</a></p></div>')
    if prima:
        risposta = (f"For state aid in {nome}, the first date on the official {ANNO} FAFSA form is {giorno(prima)}: {info['righe'][0][0][0].lower() + info['righe'][0][0][1:]}. "
                    + (f"The form lists {len(info['righe'])} dates for {nome} in all. " if len(info["righe"]) > 1 else "") + f"The federal deadline is {giorno(FAFSA['chiusura_federale'])}.")
    else:
        risposta = (f"The official {ANNO} FAFSA form gives no closing date for {nome}: it says to apply as soon as possible after {giorno(FAFSA['apertura'])}, and that Monetary Award Program awards are made while funds exist. "
                    f"The federal deadline is {giorno(FAFSA['chiusura_federale'])}.")
    faq_html, faq_ld = faq_blocco([
        (RICERCA_STATO[s], f"What is the FAFSA deadline in {nome} for {ANNO}?", risposta, "fafsa_2728"),
        ("when is fafsa due", f"When is the FAFSA due for federal aid if I live in {nome}?",
         f"The federal dates are the same in every state: the {ANNO} form opened on {giorno(FAFSA['apertura'])} and must be received by {giorno(FAFSA['chiusura_federale'])}. Only state and college aid follow the earlier {nome} and college dates.", "fafsa_2728"),
        ("when does fafsa open", f"When did the {ANNO} FAFSA open?",
         f"The form says to submit it no earlier than {giorno(FAFSA['apertura'])}. That is the first day the {ANNO} form could be filed, in {nome} and everywhere else.", "fafsa_2728"),
    ], rim)
    corpo += faq_html + rim.elenco()
    if prima:
        titolo = f"{nome} FAFSA Deadline {ANNO}: {giorno(prima)}"
        sub = f"State aid: <strong>{giorno(prima)}</strong>" + (f" is the first of {len(info['righe'])} dates on the official form" if len(info["righe"]) > 1 else " on the official form") + f". Federal aid: {giorno(FAFSA['chiusura_federale'])}."
        descr = f"{nome} FAFSA deadline for {ANNO}: {giorno(prima)} for state aid" + (f" (first of {len(info['righe'])} dates)" if len(info["righe"]) > 1 else "") + f", {giorno(FAFSA['chiusura_federale'])} for federal aid. Official form wording."
    else:
        titolo = f"{nome} FAFSA Deadline {ANNO}: As Soon As Possible"
        sub = f"State aid: <strong>as soon as possible after {giorno(FAFSA['apertura'])}</strong>, no closing date on the official form. Federal aid: {giorno(FAFSA['chiusura_federale'])}."
        descr = f"{nome} FAFSA deadline for {ANNO}: no closing date for state aid, apply as soon as possible after {giorno(FAFSA['apertura'])}. Federal: {giorno(FAFSA['chiusura_federale'])}."
    testata = banda(f"{nome} · FAFSA {ANNO}", f"FAFSA deadline in {nome} for {ANNO}", sub, icona="calendar")
    pagina(slug_stato(s), titolo, descr, corpo, testata, briciole=[("Home", ""), ("FAFSA deadlines", P_SCAD), (nome, slug_stato(s))], jsonld=[faq_ld])


# ---------------------------------------------------------------- tassi
def anno_scol(r):
    return f'{r["dal"][:4]}–{r["al"][2:4]}'


CHI_TASSO = {"ug": ("Direct Subsidized Loans and Direct Unsubsidized Loans", "Undergraduate students"),
             "grad": ("Direct Unsubsidized Loans", "Graduate and professional students"),
             "plus": ("Direct PLUS Loans", "Parents of dependent undergraduate students; graduate and professional students")}


def pagina_tassi():
    rim = Rimandi()
    per = f'{giorno(TASSI["dal"])} to June 30, {TASSI["al"][:4]}'
    voci = [(f"{T_UG}%", "undergraduates: Direct Subsidized and Unsubsidized Loans"), (f"{T_GRAD}%", "graduate and professional students: Direct Unsubsidized Loans"),
            (f"{T_PLUS}%", "Direct PLUS Loans (parents; graduate students who can still get one)"), (f'{TASSI["asta"]}%', f'10-year Treasury note high yield at the {giorno(TASSI["asta_data"])} auction')]
    sotto = f'{ico("info")} Loans first disbursed from <strong>{per}</strong> · fixed for the life of the loan · notice read on {giorno(FONTI["fr_tassi"]["letto_il"])}{rim.ref("fr_tassi")}'
    corpo = fatti(voci, sotto)
    righe = [f'<tr><th scope="row">{h(CHI_TASSO[r["chiave"]][0])}</th><td>{h(CHI_TASSO[r["chiave"]][1])}</td><td class="n">{r["asta"]}%</td><td class="n">+ {r["maggiorazione"]}</td>'
             f'<td class="n">{r["massimo"]}%</td><td class="n forte">{r["tasso"]}%</td></tr>' for r in TASSI["righe"]]
    corpo += (f'<h2 id="current">Federal student loan interest rates for {ANNO_TASSI}</h2><div class="testo"><p>Every federal Direct Loan first paid out between {per} carries one of three fixed rates. '
              f'Each is the yield of one Treasury auction plus a number of percentage points written in the law, up to a cap.</p></div>'
              f'<p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Fixed interest rates for Direct Loans first disbursed on or after {giorno(TASSI["dal"])} and before {giorno(TASSI["al"])} (Chart 1 of the official notice).{rim.ref("fr_tassi")}',
                        [("Loan", 0), ("Borrower", 0), ("Treasury yield", 1), ("Add-on", 1), ("Maximum rate", 1), ("Fixed rate", 1)], righe, "ampia")
              + rim.cit("fr_tassi", "asta") + rim.cit("fr_tassi", "formula"))
    corpo += ('<h2 id="fixed">Fixed for the life of the loan</h2><div class="testo"><p>The rate is set once, when the loan is first disbursed, and does not move afterwards. A student who borrows every year ends up with several loans, each at the rate of its own year.</p></div>'
              + rim.cit("fr_tassi", "fisso") + rim.cit("fr_tassi", "vita") + rim.cit("fr_tassi", "massimo"))
    st = TASSI["storia"]
    minimo, massimo = min(st, key=lambda r: float(r["ug"])), max(st, key=lambda r: float(r["ug"]))
    righe = []
    for r in st:
        ora = r["dal"] == TASSI["dal"]
        righe.append(f'<tr{" class=\"ora\"" if ora else ""}><th scope="row">{anno_scol(r)}<span class="conto">July 1, {r["dal"][:4]} – June 30, {r["al"][:4]}</span></th>'
                     f'<td class="n forte">{r["ug"]}%</td><td class="n">{r["grad"]}%</td><td class="n">{r["plus"]}%</td><td class="small">{"This notice" if r["avviso"] == "N/A" else h(r["avviso"])}</td></tr>')
    corpo += (f'<h2 id="history">Student loan interest rates by year, {st[-1]["dal"][:4]} to {st[0]["al"][:4]}</h2><div class="testo"><p>The same formula has applied since July 1, 2013. '
              f'In these {len(st)} years the undergraduate rate has ranged from {minimo["ug"]}% ({anno_scol(minimo)}) to {massimo["ug"]}% ({anno_scol(massimo)}); the {ANNO_TASSI} rate is {T_UG}%. '
              f'The graduate rate is always {float(st[0]["grad"]) - float(st[0]["ug"]):.2f} points above the undergraduate rate, and the PLUS rate {float(st[0]["plus"]) - float(st[0]["grad"]):.2f} point above the graduate rate, because the add-ons are fixed by law.</p></div>'
              f'<p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Fixed rates by first disbursement date (Chart 2 of the official notice). The last column is the Federal Register notice that announced each year’s rates.{rim.ref("fr_tassi")}',
                        [("Award year", 0), ("Undergraduate", 1), ("Graduate (unsubsidized)", 1), ("PLUS", 1), ("Federal Register notice", 0)], righe, "ampia"))
    righe = []
    for r in TASSI["prima_del_2013"]:
        righe.append(f'<tr><th scope="row">{h({"Subsidized": "Direct Subsidized", "Unsubsidized": "Direct Unsubsidized", "PLUS": "Direct PLUS"}[r["tipo"]])}</th><td>{h(r["chi"])}</td>'
                     f'<td>{giorno(r["dal"])}</td><td>{giorno(r["al"])}</td><td class="n forte">{r["tasso"]}%</td></tr>')
    corpo += ('<h2 id="before-2013">Loans from July 2006 to June 2013</h2><div class="testo"><p>Before the current formula, the rates were written directly in the law. They still apply to loans first disbursed in those years.</p></div>'
              '<p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Fixed rates for Direct Loans first disbursed on or after July 1, 2006 and before July 1, 2013 (Chart 3 of the official notice).{rim.ref("fr_tassi")}',
                        [("Loan", 0), ("Borrower", 0), ("First disbursed on or after", 0), ("And before", 0), ("Rate", 1)], righe, "ampia")
              + '<p class="small">Graduate and professional students have not been eligible for Direct Subsidized Loans for loan periods beginning on or after July 1, 2012, as the notice states.</p>')
    prossimo = int(TASSI["al"][:4])
    corpo += (f'<h2 id="next">The {prossimo}–{str(prossimo + 1)[2:]} rates</h2><div class="testo"><p>The rates for loans first disbursed from July 1, {prossimo} are not known yet. Under the formula quoted above they will come from the last 10-year Treasury note auction held before June 1, {prossimo}. '
              f'This page will change when Federal Student Aid publishes them. Loans you already have keep their rate.</p>'
              '<p><strong>Consolidation loans</strong> follow a different rule: no auction, just the average of the loans being combined.</p></div>' + rim.cit("fr_tassi", "consolidamento"))
    corpo += nota(f'<p><strong>PLUS loans for graduate students ended for new borrowers.</strong> The {T_PLUS}% PLUS rate still matters to parents, and to graduate and professional students who were already enrolled and borrowing before July 1, 2026. '
                  f'For everyone else, see the <a href="/{P_LIM}">loan limits in force from July 1, 2026</a>.</p>', info=True)
    corpo += (f'<h2 id="payment">What a rate means in dollars</h2><div class="testo"><p>At {T_UG}%, {usd(10000)} repaid in fixed payments over 10 years costs about {usdc(piano(1000000, mill(T_UG), 120)["rata"])} a month (our calculation). '
              f'Try your own numbers in the <a href="/{P_RATA}">student loan payment calculator</a>.</p></div>')
    faq_html, faq_ld = faq_blocco([
        ("student loan interest rates", f"What are the federal student loan interest rates for {ANNO_TASSI}?",
         f"For Direct Loans first disbursed from {per}: {T_UG}% for undergraduates (subsidized and unsubsidized), {T_GRAD}% for graduate and professional students (unsubsidized), and {T_PLUS}% for Direct PLUS Loans.", "fr_tassi"),
        ("current student loan interest rates", "Are these the current rates?",
         f"Yes for federal loans first disbursed between {per}. They were announced in the Federal Register on September 10, 2026. Private student loans are priced by each lender and are not covered here.", "fr_tassi"),
        ("parent plus loan interest rate", f"What is the Parent PLUS loan interest rate for {ANNO_TASSI}?",
         f"{T_PLUS}%, fixed for the life of the loan, for Direct PLUS Loans first disbursed from {per}. It is the Treasury yield of {TASSI['asta_arrotondata']}% plus {TASSI['righe'][2]['maggiorazione']} points; the law caps it at {TASSI['righe'][2]['massimo']}%.", "fr_tassi"),
        ("grad plus loan interest rate", "What is the Grad PLUS loan interest rate?",
         f"Direct PLUS Loans first disbursed from {per} carry a fixed {T_PLUS}%. Since July 1, 2026 graduate and professional students cannot take new Direct PLUS Loans unless they fall under the transition rule for students already enrolled and borrowing.", "fr_tassi,legge"),
        ("subsidized loan interest rate", "What is the interest rate on a subsidized loan?",
         f"{T_UG}% for Direct Subsidized Loans first disbursed from {per}. Only undergraduates can receive them.", "fr_tassi"),
        ("unsubsidized loan interest rate", "What is the interest rate on an unsubsidized loan?",
         f"For Direct Unsubsidized Loans first disbursed from {per}: {T_UG}% for undergraduates and {T_GRAD}% for graduate and professional students.", "fr_tassi"),
        ("student loan interest rates by year", "How have federal student loan rates changed over the years?",
         f"Since the current formula began in 2013, the undergraduate rate has been as low as {minimo['ug']}% ({anno_scol(minimo)}) and as high as {massimo['ug']}% ({anno_scol(massimo)}). The table above lists every year with its Federal Register notice.", "fr_tassi"),
        ("are student loan interest rates fixed", "Are federal student loan interest rates fixed?",
         "Yes for loans first disbursed on or after July 1, 2006: the rate set for the year of first disbursement applies for the life of the loan. Older Direct Loans can have variable rates, announced in a separate notice.", "fr_tassi"),
        ("how are student loan interest rates determined", "How are federal student loan interest rates determined?",
         f"By a formula in the Higher Education Act: the high yield of the last 10-year Treasury note auction before June 1, plus an add-on that depends on the loan type ({TASSI['righe'][0]['maggiorazione']}, {TASSI['righe'][1]['maggiorazione']} or {TASSI['righe'][2]['maggiorazione']} points), up to a maximum of {TASSI['righe'][0]['massimo']}%, {TASSI['righe'][1]['massimo']}% or {TASSI['righe'][2]['massimo']}%.", "fr_tassi"),
    ], rim)
    corpo += faq_html + rim.elenco()
    testata = banda(f"Federal Direct Loans · {ANNO_TASSI}", f"Federal student loan interest rates, {ANNO_TASSI} and every year since 2013",
                    f"<strong>{T_UG}%</strong> for undergraduates, <strong>{T_GRAD}%</strong> for graduate students, <strong>{T_PLUS}%</strong> for PLUS loans. Copied from the official Federal Register notice.", icona="percent")
    pagina(P_TASSI, f"Federal Student Loan Interest Rates {ANNO_TASSI} and by Year",
           f"Federal student loan interest rates for {ANNO_TASSI}: {T_UG}% undergraduate, {T_GRAD}% graduate, {T_PLUS}% PLUS. Official table of every year since 2013.",
           corpo, testata, briciole=[("Home", ""), ("Loan interest rates", P_TASSI)], jsonld=[faq_ld])


# ---------------------------------------------------------------- tetti
def pagina_limiti():
    rim = Rimandi()
    dip, ind, gen = LIM["dipendente"], LIM["indipendente"], LIM["genitori"]
    voci = [(f'{usd(dip["anni"][0]["totale"])}–{usd(dip["anni"][2]["totale"])}', "a year for dependent undergraduates, by year of study (unchanged)"),
            (usd(LIM["laureato"]["anno"]), f'a year for graduate students, {usd(LIM["laureato"]["totale"])} in total'),
            (usd(LIM["professionale"]["anno"]), f'a year for professional students, {usd(LIM["professionale"]["totale"])} in total'),
            (usd(gen["anno"]), f'a year in Parent PLUS loans per student, {usd(gen["totale"])} in total')]
    sotto = f'{ico("info")} Limits for periods of enrollment beginning <strong>on or after {giorno(LIM["in_vigore"])}</strong> · final rule and law read on {giorno(FONTI["fr_regola"]["letto_il"])}{rim.ref("fr_regola,legge")}'
    corpo = fatti(voci, sotto)
    corpo += ('<h2 id="new">What changed on July 1, 2026</h2><div class="testo"><p>Public Law 119-21, signed on July 4, 2025, rewrote the federal loan limits for graduate students, professional students and parents. '
              'The Department of Education put the changes into its regulations with a final rule that took effect on July 1, 2026. Undergraduate limits did not change.</p></div>'
              + rim.cit("fr_regola", "sintesi") + rim.cit("fr_regola", "vigore"))
    righe = [f'<tr><th scope="row">Graduate student (not professional)</th><td>Direct Unsubsidized</td><td class="n forte">{usd(LIM["laureato"]["anno"])}</td><td class="n forte">{usd(LIM["laureato"]["totale"])}</td></tr>',
             f'<tr><th scope="row">Professional student</th><td>Direct Unsubsidized</td><td class="n forte">{usd(LIM["professionale"]["anno"])}</td><td class="n forte">{usd(LIM["professionale"]["totale"])}</td></tr>',
             f'<tr><th scope="row">Parents, for each dependent student</th><td>Direct PLUS</td><td class="n forte">{usd(gen["anno"])}</td><td class="n forte">{usd(gen["totale"])}</td></tr>',
             f'<tr><th scope="row">Any student, lifetime</th><td>All federal student loans, except PLUS loans taken as a parent</td><td class="n">–</td><td class="n forte">{usd(LIM["vita"])}</td></tr>']
    corpo += (f'<h2 id="graduate">New limits for graduate students, professional students and parents</h2>'
              '<p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Federal loan limits for periods of enrollment beginning on or after {giorno(LIM["in_vigore"])} (34 CFR 685.203 as amended; section 81001 of Public Law 119-21).{rim.ref("fr_regola,legge")}',
                        [("Borrower", 0), ("Loan", 0), ("Per academic year", 1), ("In total", 1)], righe, "ampia")
              + rim.cit("fr_regola", "laureato") + rim.cit("fr_regola", "professionale") + rim.cit("fr_regola", "genitori_anno") + rim.cit("fr_regola", "genitori_totale") + rim.cit("fr_regola", "vita"))
    corpo += rim.t(f'<div class="testo"><ul><li>The graduate and professional totals are <strong>in addition to</strong> what was borrowed for undergraduate study, as the law puts it. A student who has been both a graduate and a professional student shares one {usd(LIM["professionale"]["totale"])} total between the two.[[legge]]</li>'
                   f'<li>The parent limits count <strong>all parents together</strong> for each dependent student, and the {usd(gen["totale"])} total is “without regard to any amounts repaid”: paying a loan down does not free up room to borrow again.[[fr_regola]]</li>'
                   f'<li>The {usd(LIM["vita"])} lifetime limit is counted the same way, and loan money returned by the school or the borrower does not count against it.[[fr_regola]]</li>'
                   '<li>“Professional student” means a student in a program that awards a professional degree as defined in federal regulations (34 CFR 668.2). Whether a program is graduate or professional is for the school to tell you.[[legge]]</li></ul></div>')
    def righe_ug(d, chi):
        return [f'<tr><th scope="row">{chi}, {x["anno"].lower()}</th><td class="n forte">{usd(x["totale"])}</td><td class="n">{usd(x["sussidiato"])}</td></tr>' for x in d["anni"]] + \
               [f'<tr class="ora"><th scope="row">{chi}, total debt allowed</th><td class="n forte">{usd(d["totale"])}</td><td class="n">{usd(d["totale_sussidiato"])}</td></tr>']
    quattro = sum(dip["anni"][min(i, 2)]["totale"] for i in range(4))
    corpo += (f'<h2 id="undergraduate">Undergraduate limits (unchanged)</h2><div class="testo"><p>Undergraduates borrow Direct Subsidized and Direct Unsubsidized Loans. The limit depends on the year of study and on whether the student is dependent or independent for financial aid purposes. '
              'Only part of each year’s amount can be subsidized.</p></div>'
              + tabella(f'Annual and aggregate limits for Direct Subsidized and Direct Unsubsidized Loans, undergraduates (Tables 1A, 1B and 4 of the handbook chapter; the 2026 final rule states that they remain unchanged).{rim.ref("manuale,fr_regola")}',
                        [("Student and year of study", 0), ("Subsidized + unsubsidized", 1), ("Of which subsidized, at most", 1)],
                        righe_ug(dip, "Dependent") + righe_ug(ind, "Independent"), "ampia")
              + rim.cit("fr_regola", "invariati") + rim.cit("manuale", "esempio") + rim.cit("manuale", "aggregato")
              + rim.t(f'<div class="testo"><p>Four years at the dependent limits add up to {usd(quattro)} ({" + ".join(usd(dip["anni"][min(i, 2)]["totale"]) for i in range(4))}; our addition), under the {usd(dip["totale"])} total. '
                      f'The independent limits also apply to dependent students whose parents cannot get a Direct PLUS Loan.[[manuale]] Unpaid interest that has been added to the balance does not count toward the totals.[[manuale]]</p></div>'))
    righe = [f'<tr><th scope="row">Graduate and professional students: Direct PLUS (Grad PLUS)</th><td>Up to the cost of attendance minus other financial assistance</td><td>No new loans</td></tr>',
             f'<tr><th scope="row">Graduate and professional students: total subsidized and unsubsidized debt</th><td>{usd(LIM["laureati_prima"]["totale"])}, including undergraduate loans</td>'
             f'<td>{usd(LIM["laureato"]["totale"])} (graduate) or {usd(LIM["professionale"]["totale"])} (professional), on top of undergraduate loans</td></tr>',
             f'<tr><th scope="row">Parents: Direct PLUS</th><td>Up to the cost of attendance minus other financial assistance</td><td>{usd(gen["anno"])} a year and {usd(gen["totale"])} in total per student</td></tr>']
    corpo += ('<h2 id="before-after">Before and after</h2><p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Limits for periods of enrollment beginning before July 1, 2026 and from that date (34 CFR 685.203(e), (f) and (g) as amended).{rim.ref("fr_regola")}',
                        [("Loan", 0), ("Before July 1, 2026", 0), ("From July 1, 2026", 0)], righe, "ampia")
              + rim.cit("legge", "grad_plus"))
    corpo += ('<h2 id="exception">Students who were already enrolled keep the old limits for a while</h2><div class="testo">'
              + rim.t(f'<p>The new limits, and the end of Grad PLUS, do not apply to a student who on June 30, 2026 was enrolled in a program and had already received a federal Direct Loan for that program (or whose parent had). '
                      f'The exception lasts for the student’s “expected time to credential”: the time left to finish that program, and never more than {LIM["anni_eccezione"]} academic years. '
                      'It ends early if the student withdraws or leaves the program.[[legge,fr_regola]]</p>'
                      '<p><strong>What counts as the same program.</strong> For undergraduates (and their parents’ PLUS loans), changing major within the same degree or certificate at the same school counts as the same program. '
                      'A graduate or professional student who switches to a different program, or any student who transfers to another school, loses the exception. '
                      'A graduate student who only changes concentration within the same academic field, at the same level and school, keeps it.[[fr_regola]]</p></div>')
              + rim.cit("fr_regola", "major") + rim.cit("fr_regola", "laureati_programma") + rim.cit("fr_regola", "concentrazione") + rim.cit("fr_regola", "trasferimento"))
    corpo += ('<h2 id="other-rules">Two more rules that can lower your limit</h2><div class="testo">'
              + rim.t('<p><strong>Part-time enrollment.</strong> From July 1, 2026 the annual limit is reduced for students enrolled less than full time, in proportion.[[legge]]</p>') + '</div>' + rim.cit("legge", "tempo_parziale")
              + '<div class="testo">' + rim.t('<p><strong>Limits set by the school.</strong> A college may set a lower loan limit for a whole program of study, as long as it applies the same limit to every student in that program.[[legge]] '
                                              'And no federal loan can exceed the school’s cost of attendance minus the student’s other financial assistance.[[fr_regola]]</p>') + '</div>')
    corpo += (f'<h2 id="tools">Work out your own numbers</h2><p class="azioni"><a class="btn" href="/{P_PLUS}#gap">How much do the limits cover?{ico("arrow")}</a>'
              f'<a class="btn sec" href="/{P_RATA}">Payment calculator</a><a class="btn sec" href="/{P_TASSI}">Interest rates</a><a class="btn sec" href="/{P_UNI}">The gap at {len(DOMU["scelte"])} colleges</a></p>')
    faq_html, faq_ld = faq_blocco([
        ("federal student loan limits", "What are the federal student loan limits for 2026–27?",
         f"Dependent undergraduates: {usd(dip['anni'][0]['totale'])}, {usd(dip['anni'][1]['totale'])} and {usd(dip['anni'][2]['totale'])} a year by year of study, {usd(dip['totale'])} in total. Graduate students: {usd(LIM['laureato']['anno'])} a year, {usd(LIM['laureato']['totale'])} in total. "
         f"Professional students: {usd(LIM['professionale']['anno'])} a year, {usd(LIM['professionale']['totale'])} in total. Parents: {usd(gen['anno'])} a year and {usd(gen['totale'])} in total for each dependent student.", "manuale,fr_regola"),
        ("student loan limits", "Did the undergraduate loan limits change in 2026?",
         f"No. The final rule says the undergraduate loan limits remain unchanged: totals of {usd(dip['totale'])} for dependent and {usd(ind['totale'])} for independent undergraduates. The 2026 changes are for graduate students, professional students and parents.", "fr_regola"),
        ("aggregate loan limit", "What is an aggregate loan limit?",
         f"It is the most a borrower may owe or borrow in total, on top of the yearly limit. For undergraduates it is {usd(dip['totale'])} (dependent) or {usd(ind['totale'])} (independent), of which at most {usd(dip['totale_sussidiato'])} subsidized. "
         f"From July 1, 2026 there is also a lifetime limit of {usd(LIM['vita'])} for all federal student loans.", "manuale,fr_regola"),
        ("grad plus loan", "Can graduate students still get a Grad PLUS loan?",
         f"Not for periods of instruction beginning on or after July 1, 2026, unless the student was enrolled in the program on June 30, 2026 and had already received a Direct Loan for it. Those students keep access for the time left in the program, up to {LIM['anni_eccezione']} academic years. The exception is lost if the student switches to a different program or transfers to another school.", "legge,fr_regola"),
        ("big beautiful bill student loans", "What did the “Big Beautiful Bill” change for student loans?",
         f"Public Law 119-21, which the Department of Education first called the One Big Beautiful Bill Act and now calls the Working Families Tax Cuts Act, capped graduate loans at {usd(LIM['laureato']['anno'])} a year, professional loans at {usd(LIM['professionale']['anno'])} a year and Parent PLUS at {usd(gen['anno'])} a year, "
         f"ended new Grad PLUS loans, and replaced the repayment plans for new loans with a standard plan and the Repayment Assistance Plan, all from July 1, 2026.", "fr_regola,legge"),
        ("graduate student loan limits", "How much can a graduate student borrow in federal loans?",
         f"From July 1, 2026, {usd(LIM['laureato']['anno'])} a year and {usd(LIM['laureato']['totale'])} in total in Direct Unsubsidized Loans, in addition to undergraduate borrowing. Students in professional degree programs can borrow {usd(LIM['professionale']['anno'])} a year and {usd(LIM['professionale']['totale'])} in total.", "fr_regola"),
        ("lifetime student loan limit", "Is there a lifetime limit on federal student loans?",
         f"Yes, from July 1, 2026: {usd(LIM['vita'])} for all federal student loans a person borrows as a student, counted without regard to amounts repaid or forgiven. PLUS loans taken as a parent for a child are not included.", "fr_regola"),
        ("subsidized loan limit", "How much of my loan can be subsidized?",
         f"For undergraduates, at most {usd(dip['anni'][0]['sussidiato'])} in the first year, {usd(dip['anni'][1]['sussidiato'])} in the second and {usd(dip['anni'][2]['sussidiato'])} from the third year on, and {usd(dip['totale_sussidiato'])} in total. Graduate and professional students cannot receive subsidized loans.", "manuale,fr_tassi"),
        ("how much can i borrow in student loans", "How much can a dependent student and their parents borrow together?",
         f"Over four years, a dependent undergraduate can borrow up to {usd(quattro)} at the yearly limits (our addition), and the parents up to {usd(gen['totale'])} in PLUS loans for that student: {usd(quattro + gen['totale'])} in all, and never more than the cost of attendance minus other aid.", "manuale,fr_regola"),
    ], rim)
    corpo += faq_html + rim.elenco()
    testata = banda("Federal Direct Loans · from July 1, 2026", "Federal student loan limits for 2026–27",
                    f"New caps for graduate students (<strong>{usd(LIM['laureato']['anno'])}</strong> a year), professional students (<strong>{usd(LIM['professionale']['anno'])}</strong>) and parents (<strong>{usd(gen['anno'])}</strong>), and the unchanged undergraduate limits. From the final rule and the law.", icona="cap")
    pagina(P_LIM, "Federal Student Loan Limits 2026–27: New Annual and Total Caps",
           f"Federal student loan limits from July 1, 2026: undergraduate {usd(dip['anni'][0]['totale'])}–{usd(dip['anni'][2]['totale'])}, graduate {usd(LIM['laureato']['anno'])}, professional {usd(LIM['professionale']['anno'])}, Parent PLUS {usd(gen['anno'])} a year.",
           corpo, testata, briciole=[("Home", ""), ("Loan limits", P_LIM)], jsonld=[faq_ld])


# ---------------------------------------------------------------- calcolatore della rata
def attr_json(x):
    return h(json.dumps(x, separators=(",", ":")))


def opzioni_tasso(scelto="ug"):
    v = {"ug": (T_UG, f"Undergraduate loan, {ANNO_TASSI}"), "grad": (T_GRAD, f"Graduate unsubsidized loan, {ANNO_TASSI}"), "plus": (T_PLUS, f"PLUS loan, {ANNO_TASSI}")}
    return "".join(f'<option value="{t}"{" selected" if k == scelto else ""}>{h(e)}: {t}%</option>' for k, (t, e) in v.items()) + '<option value="">Another rate (type it below)</option>'


def fasce_testo(f, i):
    prec = STD["fasce"][i - 1]["sotto"] if i else None
    if prec is None:
        return f'Less than {usd(f["sotto"])}'
    if f["sotto"] is None:
        return f"{usd(prec)} or more"
    return f'{usd(prec)} to less than {usd(f["sotto"])}'


def pagina_rata():
    rim = Rimandi()
    saldo0 = sum(LIM["dipendente"]["anni"][min(i, 2)]["totale"] for i in range(4))
    calc = (f'<div class="card calc pull" data-calc="rata" data-regole="{attr_json({"fasce": STD["fasce"], "minimo_mese": STD["minimo_mese"]})}"><form class="calc-in" novalidate>'
            '<h2>Your loan</h2>'
            f'<label>Loan balance when repayment starts<span class="conprefisso"><span>$</span><input type="text" inputmode="decimal" name="saldo" value="{saldo0:,}" autocomplete="off"></span></label>'
            f'<label>Loan type<select name="tipo">{opzioni_tasso()}</select></label>'
            f'<label>Interest rate<span class="consuffisso"><input type="text" inputmode="decimal" name="tasso" value="{T_UG}" autocomplete="off"><span>%</span></span>'
            '<span class="aiuto">Use the rate of your own loan. Several loans: use one balance and an average rate for a rough figure.</span></label>'
            '<label>Standard plan<select name="piano"><option value="nuovo" selected>Loans from July 1, 2026 (10–25 years)</option>'
            '<option value="vecchio">Only loans before July 1, 2026 (10 years)</option></select><span class="aiuto">Choose the first option if at least one of your loans was made on or after July 1, 2026.</span></label>'
            '</form><div class="calc-out" aria-live="polite"><p class="errore" data-errore hidden></p><div data-uscita>'
            '<p class="ris-lab">Estimated monthly payment</p><p class="ris-big" data-o="rata">–</p>'
            '<ul class="ris-righe"><li><span>Repayment period</span><b data-o="anni">–</b></li><li><span>Total paid</span><b data-o="pagato">–</b></li><li><span>Of which interest</span><b data-o="interessi">–</b></li></ul>'
            '<p class="ris-nota" data-o="perche"></p><p class="ris-nota" data-o="minimo"></p></div>'
            '<p class="ris-nota">An estimate from the standard loan payment formula. Your servicer’s figure can differ by a few dollars. Needs JavaScript.</p></div></div>')
    corpo = calc
    corpo += ('<h2 id="how">How the calculator works</h2><div class="testo">'
              '<p>The standard plan is a fixed payment every month until the loan is paid off. The payment is the one that brings the balance to zero in the number of months of the plan:</p></div>'
              '<p class="formula">payment = balance × r ÷ (1 − (1 + r)<sup>−n</sup>)\nr = yearly interest rate ÷ 12, n = number of monthly payments</p>'
              '<div class="testo"><p>The formula is ordinary loan arithmetic, not an official table: interest is counted month by month and each figure is rounded to the cent. Loan servicers count interest by the day, so their numbers differ slightly. '
              'The calculator does not include loan fees, interest that builds up while you are in school, or any period in which you pay less or nothing.</p>'
              + rim.t(f'<p><strong>Minimum payment.</strong> Under the regulations a standard plan payment is at least ${STD["minimo_mese"]} a month, in the 10-year plan and in the new plan alike. '
                      f'If the formula gives less than ${STD["minimo_mese"]}, the calculator uses ${STD["minimo_mese"]} and shows the smaller number of payments and the lower total interest that result; '
                      f'if you owe less than ${STD["minimo_mese"]}, the payment is what you owe.[[fr_regola]]</p></div>')
              + rim.cit("fr_regola", "minimo_std") + rim.cit("fr_regola", "minimo_10"))
    righe = "".join(f'<tr><th scope="row">{fasce_testo(f, i)}</th><td class="n forte">{f["anni"]} years</td><td class="n">{f["anni"] * 12}</td></tr>' for i, f in enumerate(STD["fasce"]))
    corpo += ('<h2 id="standard">The standard plan: 10 years, or 10 to 25</h2><div class="testo">'
              + rim.t(f'<p>Which standard plan you get depends on when your loans were made. If all of them were made before July 1, 2026, the repayment plans that existed before that date still apply, including the standard plan with a fixed payment over 10 years. '
                      f'A borrower who receives a loan on or after July 1, 2026 has two choices for all federal loans: the new standard plan, or the <a href="/{P_RAP}">Repayment Assistance Plan</a>. '
                      'In the new standard plan the length depends on the total principal owed when repayment starts.[[legge]]</p></div>')
              + tabella(f'Length of the standard repayment plan for borrowers with a loan made on or after {giorno(STD["dal"])} (section 455(d)(7) of the Higher Education Act, added by Public Law 119-21).{rim.ref("legge")}',
                        [("Total outstanding principal", 0), ("Repayment period", 1), ("Monthly payments", 1)], [righe], stretta=True)
              + rim.cit("legge", "due_piani") + rim.cit("legge", "standard") + rim.cit("legge", "anticipo") + rim.cit("legge", "vecchi_piani"))
    esempi = []
    for saldo in (10000, 20000, saldo0, 40000, LIM["indipendente"]["totale"], 100000):
        c = saldo * 100
        nuovo, vecchio = piano(c, mill(T_UG), anni_standard(c) * 12), piano(c, mill(T_UG), 120)
        esempi.append(f'<tr data-esempio="{c}"><th scope="row">{usd(saldo)}</th><td class="n">{anni_standard(c)} years</td><td class="n forte">{usdc(nuovo["rata"])}</td><td class="n">{usdc(nuovo["interessi"])}</td>'
                      f'<td class="n forte">{usdc(vecchio["rata"])}</td><td class="n">{usdc(vecchio["interessi"])}</td></tr>')
    corpo += (f'<h2 id="examples">Examples at {T_UG}%</h2><div class="testo"><p>The same balance costs less per month over a longer period, and more in total interest. '
              f'{usd(saldo0)} is what a dependent undergraduate can borrow in four years at the federal limits; {usd(LIM["indipendente"]["totale"])} is the total limit for independent undergraduates. Paying more than the fixed amount is always allowed, without penalty.</p></div>'
              '<p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Our calculation with the formula above at {T_UG}%, the {ANNO_TASSI} undergraduate rate. Not official figures.{rim.ref("fr_tassi,legge")}',
                        [("Balance", 0), ("New plan: period", 1), ("New plan: monthly", 1), ("New plan: interest", 1), ("10-year plan: monthly", 1), ("10-year plan: interest", 1)], esempi, "ampia"))
    corpo += riquadro_partner()
    corpo += (f'<h2 id="income">If the standard payment is too high</h2><div class="testo"><p>For loans made on or after July 1, 2026 the alternative is the Repayment Assistance Plan, where the payment depends on income and family size instead of the balance. '
              f'Parent PLUS loans are the exception: new ones can only be repaid under the standard plan.</p>'
              f'<p class="azioni"><a class="btn" href="/{P_RAP}">Repayment Assistance Plan calculator{ico("arrow")}</a><a class="btn sec" href="/{P_PLUS}">Parent PLUS loans</a></p></div>')
    r10 = piano(1000000, mill(T_UG), 120)
    faq_html, faq_ld = faq_blocco([
        ("student loan calculator", "How do I calculate a student loan payment?",
         f"Take the balance, the yearly interest rate and the number of monthly payments, and apply the fixed-payment formula on this page. For example, {usd(10000)} at {T_UG}% over 10 years comes to about {usdc(r10['rata'])} a month and {usdc(r10['interessi'])} of interest in total (our calculation).", "fr_tassi"),
        ("student loan payment calculator", "Which repayment period should I use for a federal student loan?",
         f"If all your federal loans were made before July 1, 2026, the standard plan is 10 years. If you receive a loan on or after that date, the standard plan lasts {STD['fasce'][0]['anni']}, {STD['fasce'][1]['anni']}, {STD['fasce'][2]['anni']} or {STD['fasce'][3]['anni']} years depending on your total principal, with steps at {usd(STD['fasce'][0]['sotto'])}, {usd(STD['fasce'][1]['sotto'])} and {usd(STD['fasce'][2]['sotto'])}.", "legge"),
        ("student loan repayment calculator", "Can I repay a federal student loan faster than the plan?",
         "Yes. The law says the borrower is entitled to accelerate repayment without penalty. Paying more than the fixed amount shortens the loan and lowers the total interest.", "legge"),
        ("student loan interest calculator", "How much interest will I pay on a student loan?",
         f"It depends on the balance, the rate and above all the time. On {usd(saldo0)} at {T_UG}%, the 10-year plan costs {usdc(piano(saldo0 * 100, mill(T_UG), 120)['interessi'])} of interest and the {anni_standard(saldo0 * 100)}-year plan {usdc(piano(saldo0 * 100, mill(T_UG), anni_standard(saldo0 * 100) * 12)['interessi'])} (our calculation).", "fr_tassi,legge"),
        ("standard repayment plan", "What is the standard repayment plan?",
         f"A plan with a fixed monthly payment over a fixed period. For borrowers with a loan made on or after July 1, 2026 the period is {STD['fasce'][0]['anni']} years below {usd(STD['fasce'][0]['sotto'])} of principal, {STD['fasce'][1]['anni']} years below {usd(STD['fasce'][1]['sotto'])}, {STD['fasce'][2]['anni']} years below {usd(STD['fasce'][2]['sotto'])} and {STD['fasce'][3]['anni']} years from {usd(STD['fasce'][2]['sotto'])}. Payments are at least ${STD['minimo_mese']} a month. It is the plan you get if you do not choose one.", "legge,fr_regola"),
        ("student loan monthly payment calculator", "Does the monthly payment include fees or interest from my school years?",
         "No. The calculator starts from the balance you type. If interest built up while you were in school and was added to the loan, type the balance including it; the figure is on your servicer’s statement.", "legge"),
        ("federal student loan calculator", "Is this an official federal calculator?",
         "No. This is an independent site. The plan lengths and rates come from the law and the Federal Register, and the payment is our arithmetic. For the figures that apply to your loans, ask your loan servicer.", "legge,fr_tassi"),
    ], rim)
    corpo += faq_html + rim.elenco()
    testata = banda("Federal student loans · standard plan", "Student loan payment calculator",
                    "The fixed monthly payment on a federal student loan under the standard plan: 10 years for older loans, 10 to 25 years by balance for loans made from July 1, 2026.", icona="calc")
    pagina(P_RATA, "Student Loan Payment Calculator: Federal Standard Plan 2026",
           "Student loan payment calculator for the federal standard plan: fixed monthly payment, total interest, and the 10 to 25 year periods for loans from July 1, 2026.",
           corpo, testata, briciole=[("Home", ""), ("Payment calculator", P_RATA)], jsonld=[faq_ld])


# ---------------------------------------------------------------- Repayment Assistance Plan
def pagina_rap():
    rim = Rimandi()
    sc = RAP["scaglioni"]
    voci = [(f'{sc[1]["pc"]}%–{sc[-1]["pc"]}%', "of adjusted gross income a year, by income band"), (usd(RAP["per_dipendente_mese"]), "less every month for each dependent"),
            (usd(RAP["minimo_mese"]), "minimum monthly payment"), (str(RAP["rate_cancellazione"]), "qualifying monthly payments, then the remaining balance is cancelled")]
    calc = (f'<div class="card calc pull" data-calc="rap" data-regole="{attr_json({"rap": RAP})}"><form class="calc-in" novalidate>'
            '<h2>Your income</h2>'
            '<label>Adjusted gross income (AGI), per year<span class="conprefisso"><span>$</span><input type="text" inputmode="decimal" name="reddito" value="45,000" autocomplete="off"></span>'
            '<span class="aiuto">From your most recent federal tax return. Married filing separately: only your own AGI.</span></label>'
            '<label>Dependents<input type="number" name="carico" value="0" min="0" max="15" step="1" inputmode="numeric">'
            '<span class="aiuto">People you claim as dependents on your tax return.</span></label>'
            '<h3>Optional: what one month does to the loan</h3>'
            '<label>Loan balance<span class="conprefisso"><span>$</span><input type="text" inputmode="decimal" name="saldo" value="30,000" autocomplete="off"></span></label>'
            f'<label>Interest rate<span class="consuffisso"><input type="text" inputmode="decimal" name="tasso" value="{T_UG}" autocomplete="off"><span>%</span></span></label>'
            '</form><div class="calc-out" aria-live="polite"><p class="errore" data-errore hidden></p><div data-uscita>'
            '<p class="ris-lab">Monthly payment under RAP</p><p class="ris-big" data-o="rata">–</p>'
            '<ul class="ris-righe"><li><span>Base payment</span><b data-o="base">–</b></li><li><span>Divided by 12</span><b data-o="dodici">–</b></li><li><span>Dependents</span><b data-o="carico">–</b></li></ul>'
            '<p class="ris-nota" data-o="minimo"></p>'
            '<div data-mese hidden><p class="ris-lab" style="margin-top:8px">One month on this balance</p>'
            '<ul class="ris-righe"><li><span>Interest for the month</span><b data-o="interessi">–</b></li><li><span>Your payment to interest</span><b data-o="ainteressi">–</b></li>'
            '<li><span>Interest not charged to you</span><b data-o="nonaddebitati">–</b></li><li><span>Your payment to principal</span><b data-o="acapitale">–</b></li>'
            '<li><span>Principal reduced by the government</span><b data-o="aggiunta">–</b></li><li><span>Balance after the month</span><b data-o="nuovosaldo">–</b></li></ul></div></div>'
            '<p class="ris-nota">An estimate from the formula in the law, for an on-time payment. Needs JavaScript.</p></div></div>')
    corpo = calc + f'<p class="small">{ico("info")} The Repayment Assistance Plan exists from {giorno(RAP["dal"])}. Law read on {giorno(FONTI["legge"]["letto_il"])}.{rim.ref("legge")}</p>'
    corpo += '<div class="card fatti" style="margin-top:14px">' + "".join(f'<div class="fatto{" main" if i == 0 else ""}"><b>{b}</b><span>{h(t)}</span></div>' for i, (b, t) in enumerate(voci)) + "</div>"
    righe = []
    for i, s in enumerate(sc):
        fascia = f'Not more than {usd(s["fino_a"])}' if i == 0 else (f'More than {usd(sc[i - 1]["fino_a"])}' if s["fino_a"] is None else f'More than {usd(sc[i - 1]["fino_a"])}, up to {usd(s["fino_a"])}')
        base = f'{usd(s["fisso_anno"])} a year' if s["pc"] is None else f'{s["pc"]}% of AGI'
        if s["fino_a"] is None:
            mese = f'{usdc(rap_mese(sc[i - 1]["fino_a"] + 1, 0))} and up'
        else:
            mese = usdc(rap_mese(s["fino_a"], 0))
        righe.append(f'<tr><th scope="row">{fascia}</th><td class="forte">{base}</td><td class="n">{mese}</td></tr>')
    a, b = sc[2]["fino_a"], sc[2]["fino_a"] + 1
    corpo += ('<h2 id="formula">The official formula</h2><div class="testo"><p>The Repayment Assistance Plan (RAP) is the income-based plan created by Public Law 119-21. The payment does not depend on how much you owe. '
              'It is a percentage of your adjusted gross income, set by the band your income falls in, divided by 12, minus a fixed amount for each dependent.</p></div>'
              f'<p class="formula">monthly payment = base payment ÷ 12 − ${RAP["per_dipendente_mese"]} × dependents\nnever less than ${RAP["minimo_mese"]}</p>'
              + tabella(f'Base payment by adjusted gross income (section 455(q)(4)(B)(iv) of the Higher Education Act). Third column: our calculation of the monthly payment at the top of each band, with no dependents.{rim.ref("legge")}',
                        [("Adjusted gross income", 0), ("Base payment", 0), ("Monthly, top of band", 1)], righe, "ampia")
              + rim.cit("legge", "rap_mensile") + rim.cit("legge", "rap_dipendente") + rim.cit("legge", "rap_minimo"))
    corpo += nota(f'<p><strong>The percentage applies to the whole income, not only to the part above the step.</strong> With no dependents, an AGI of {usd(a)} gives {usdc(rap_mese(a, 0))} a month; an AGI of {usd(b)} gives {usdc(rap_mese(b, 0))} (our calculation from the table). '
                  'One dollar more of income can raise the payment by a noticeable amount at each step.</p>')
    redditi, carichi = (20000, 35000, 50000, 65000, 80000, 100000, 150000), (0, 1, 2, 3)
    righe = ["<tr><th scope=\"row\">" + usd(r) + "</th>" + "".join(f'<td class="n{" forte" if c == 0 else ""}" data-rap="{r}-{c}">{usdc(rap_mese(r, c))}</td>' for c in carichi) + "</tr>" for r in redditi]
    corpo += ('<h2 id="examples">Monthly payment by income and dependents</h2><p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Our calculation with the official formula. Not official figures.{rim.ref("legge")}',
                        [("Adjusted gross income", 0)] + [("No dependents" if c == 0 else f"{c} dependent{'s' if c > 1 else ''}", 1) for c in carichi], righe, "ampia"))
    corpo += ('<h2 id="balance">What happens to the balance</h2><div class="testo">'
              + rim.t(f'<p>Each payment goes first to interest, then to fees, then to principal. Two rules protect borrowers whose payment is small compared with the loan, for every month in which the payment is made on time:[[legge]]</p>'
                      f'<ul><li><strong>Unpaid interest is not charged.</strong> If the payment does not cover the month’s interest, the rest of that interest is not added to what you owe.</li>'
                      f'<li><strong>Principal goes down by up to ${RAP["quota_capitale_mese"]} anyway.</strong> If the payment reduces principal by less than ${RAP["quota_capitale_mese"]}, the government reduces it by the difference, up to the smaller of ${RAP["quota_capitale_mese"]} and the amount you paid.</li>'
                      f'<li><strong>Cancellation after {RAP["rate_cancellazione"]} qualifying payments.</strong> That is {RAP["rate_cancellazione"] // 12} years of monthly payments. Certain payments under other plans count too.</li></ul></div>')
              + rim.cit("legge", "rap_interessi") + rim.cit("legge", "rap_360")
              + '<div class="testo">' + rim.t('<p><strong>Both protections need an on-time payment.</strong> The regulations count a payment as on time if it arrives on or before the due date for the current month and after the due date for the previous month. '
                                              'If you pay ahead, so that a payment is credited to a future month and nothing is due that month, you do not receive the matching principal payment for it.[[fr_regola]]</p>') + '</div>'
              + rim.cit("fr_regola", "anticipo_quota"))
    corpo += ('<h2 id="who">Who can use it</h2><div class="testo">'
              + rim.t('<ul><li>Borrowers with a federal Direct Loan made on or after July 1, 2026 choose between two plans only: the standard plan and RAP. All of the borrower’s loans go into the same plan.[[legge]]</li>'
                      '<li>Borrowers whose loans were all made before July 1, 2026 can also choose RAP from that date: the law adds it to the plans available for older loans.[[legge]]</li>'
                      '<li>You can switch from the standard plan to RAP, or back, at any time.[[legge]]</li>'
                      '<li>Parent PLUS loans, and consolidation loans that repaid them, cannot be repaid under RAP.[[legge]]</li>'
                      '<li>Borrowers with older loans in an income-contingent plan have to pick another plan before July 1, 2028; RAP is one of the options the law lists.[[legge]]</li>'
                      '<li>Married borrowers who file a separate federal tax return are assessed on their own income only.[[legge]]</li>'
                      '<li>Married borrowers who file a joint return are assessed on the couple’s combined income. If the spouse also has eligible loans, each borrower’s payment is then reduced to their own share of the couple’s combined loan balance. The calculator on this page does not do that split.[[fr_regola]]</li></ul></div>')
              + rim.cit("legge", "rap_reddito") + rim.cit("fr_regola", "coniugi") + rim.cit("legge", "rap_vecchi") + rim.cit("legge", "rap_esclusi"))
    corpo += (f'<h2 id="compare">Compare with the standard plan</h2><div class="testo"><p>The standard plan is a fixed payment based on the balance; RAP is based on income. Which is lower depends on both.</p>'
              f'<p class="azioni"><a class="btn" href="/{P_RATA}">Standard plan payment calculator{ico("arrow")}</a></p></div>')
    faq_html, faq_ld = faq_blocco([
        ("repayment assistance plan", "What is the Repayment Assistance Plan?",
         f"It is the income-based repayment plan for federal student loans that started on {giorno(RAP['dal'])}. The monthly payment is a share of adjusted gross income ({sc[1]['pc']}% to {sc[-1]['pc']}% a year, by income band) divided by 12, minus ${RAP['per_dipendente_mese']} per dependent, with a ${RAP['minimo_mese']} minimum. Any balance left after {RAP['rate_cancellazione']} qualifying payments is cancelled.", "legge"),
        ("repayment assistance plan calculator", "How is the RAP payment calculated?",
         f"Find your income band, take that percentage of your whole adjusted gross income, divide by 12 and subtract ${RAP['per_dipendente_mese']} for each dependent. Example: an AGI of {usd(50000)} is in the {next(s['pc'] for s in sc if s['fino_a'] and 50000 <= s['fino_a'])}% band, so the payment is {usdc(rap_mese(50000, 0))} a month with no dependents and {usdc(rap_mese(50000, 2))} with two (our calculation).", "legge"),
        ("rap calculator", "What is the lowest payment under RAP?",
         f"${RAP['minimo_mese']} a month. Borrowers with an adjusted gross income of {usd(sc[0]['fino_a'])} or less have a base payment of {usd(sc[0]['fisso_anno'])} a year, which is ${RAP['minimo_mese']} a month, and the payment cannot go below ${RAP['minimo_mese']} after the reduction for dependents.", "legge"),
        ("rap student loan", "Does interest keep growing under RAP if my payment is small?",
         f"No, as long as you pay on time. Interest that the monthly payment does not cover is not charged to you, and if your payment reduces principal by less than ${RAP['quota_capitale_mese']} the government makes up the difference, up to the amount you paid.", "legge"),
        ("what is the repayment assistance plan", "Who has to use RAP or the standard plan?",
         "Anyone who receives a federal Direct Loan on or after July 1, 2026: those are the only two plans for such borrowers, and the choice covers all their loans. Parent PLUS loans made from that date must be repaid under the standard plan.", "legge"),
        ("rap student loan", "Can I use RAP if all my loans are from before July 2026?",
         f"Yes. From {giorno(RAP['dal'])} the law adds the Repayment Assistance Plan to the repayment plans available to borrowers whose loans were all made before that date, except for Parent PLUS loans and consolidation loans that repaid them.", "legge"),
        ("rap repayment plan", "Can I leave RAP later?",
         "Yes. The law lets a borrower change from RAP to the standard plan, or from the standard plan to RAP, at any time.", "legge"),
    ], rim)
    corpo += faq_html + rim.elenco()
    testata = banda("Federal student loans · income-based plan", "Repayment Assistance Plan (RAP): calculator and official formula",
                    f"From July 1, 2026 the payment is <strong>{sc[1]['pc']}% to {sc[-1]['pc']}%</strong> of adjusted gross income a year, minus <strong>${RAP['per_dipendente_mese']}</strong> a month per dependent. Formula copied from the law.", icona="calc")
    pagina(P_RAP, "Repayment Assistance Plan (RAP) Calculator and Official Formula",
           f"Repayment Assistance Plan calculator: monthly payment from your income and dependents, with the official bands ({sc[1]['pc']}% to {sc[-1]['pc']}% of AGI) from the law.",
           corpo, testata, briciole=[("Home", ""), ("Repayment Assistance Plan", P_RAP)], jsonld=[faq_ld])


# ---------------------------------------------------------------- prestiti PLUS dei genitori
def pagina_plus():
    rim = Rimandi()
    gen, dip = LIM["genitori"], LIM["dipendente"]
    per = f'{giorno(TASSI["dal"])} to June 30, {TASSI["al"][:4]}'
    quattro = sum(dip["anni"][min(i, 2)]["totale"] for i in range(4))
    voci = [(f"{T_PLUS}%", f"fixed rate, loans first disbursed {per}"), (usd(gen["anno"]), "a year for each dependent student, all parents together"),
            (usd(gen["totale"]), "in total for each dependent student"), ("Standard plan", "the only repayment plan for Parent PLUS loans made from July 1, 2026")]
    sotto = f'{ico("info")} Limits for periods of enrollment beginning <strong>on or after {giorno(LIM["in_vigore"])}</strong> · sources read on {giorno(FONTI["fr_regola"]["letto_il"])}{rim.ref("fr_regola,fr_tassi")}'
    corpo = fatti(voci, sotto)
    corpo += ('<h2 id="limits">The new Parent PLUS limits</h2><div class="testo"><p>A Direct PLUS Loan for parents used to cover whatever was left of the college’s cost of attendance after other aid. '
              f'For periods of enrollment beginning on or after July 1, 2026 there are two caps, counted per student and for all of that student’s parents together.</p></div>'
              + rim.cit("fr_regola", "genitori_anno") + rim.cit("fr_regola", "genitori_totale")
              + rim.t(f'<div class="testo"><ul><li>Two parents borrowing for the same child share the same {usd(gen["anno"])} and {usd(gen["totale"])}; a family with two children in college has the limits twice.</li>'
                      f'<li>The {usd(gen["totale"])} is counted “without regard to any amounts repaid”: repaying part of the loan does not make room for new borrowing.</li>'
                      '<li>The loan still cannot exceed the cost of attendance minus the student’s other financial assistance.[[fr_regola]]</li>'
                      f'<li>If the student was enrolled on June 30, 2026 and a Direct Loan had already been made to the parent or the student for that program, the old rule (up to the cost of attendance) continues for the time left in the program, up to {LIM["anni_eccezione"]} academic years. Changing major within the same degree at the same school keeps the exception; transferring to another school ends it, because the Department treats that as a new program.[[fr_regola,legge]]</li></ul></div>')
              + rim.cit("fr_regola", "trasferimento"))
    calc = (f'<div class="card calc" id="gap" data-calc="buco" data-regole="{attr_json({"limiti": {"dipendente": dip, "genitori": gen}})}"><form class="calc-in" novalidate>'
            '<h2>How much do the federal limits cover?</h2>'
            '<label>Cost left to pay per year, after grants and scholarships<span class="conprefisso"><span>$</span><input type="text" inputmode="decimal" name="costo" value="32,000" autocomplete="off"></span>'
            '<span class="aiuto">Your own figure, from the college’s award letter or net price calculator.</span></label>'
            '<label>Years of study<select name="anni"><option value="1">1 year</option><option value="2">2 years</option><option value="3">3 years</option><option value="4" selected>4 years</option><option value="5">5 years</option><option value="6">6 years</option></select></label>'
            '<p class="aiuto">Assumes a dependent student starting the first year who borrows the full federal limit every year, and parents who borrow PLUS loans for the rest up to their limit. Both can borrow less.</p>'
            '</form><div class="calc-out" aria-live="polite"><p class="errore" data-errore hidden></p><div data-uscita>'
            '<p class="ris-lab">Not covered by federal loans</p><p class="ris-big" data-o="resto">–</p><p class="ris-nota" data-o="frase"></p>'
            '<ul class="ris-righe"><li><span>Total cost entered</span><b data-o="costo">–</b></li><li><span>Student’s federal loans, at most</span><b data-o="studente">–</b></li><li><span>Parent PLUS, at most</span><b data-o="genitori">–</b></li></ul>'
            '<div class="tab" style="margin-top:8px"><table class="dati"><thead><tr><th scope="col">Year</th><th scope="col" class="n">Cost</th><th scope="col" class="n">Student</th><th scope="col" class="n">Parents</th><th scope="col" class="n">Left</th></tr></thead><tbody data-righe></tbody></table></div>'
            '</div><p class="ris-nota">Our arithmetic with the official limits. Needs JavaScript.</p></div></div>')
    es = buco(3200000, 4)
    corpo += ('<h2 id="gap-h">The gap after federal loans</h2><div class="testo">'
              + rim.t(f'<p>With the new caps, federal loans can cover at most {usd(quattro)} (student, four years at the dependent limits) plus {usd(gen["totale"])} (parents): {usd(quattro + gen["totale"])} for a four-year degree (our addition).[[manuale,fr_regola]] '
                      f'If the cost left after grants and scholarships is higher, the difference has to come from savings, income, work, more scholarships, a cheaper college or private loans. '
                      f'For example, at {usd(32000)} a year for four years the limits leave {usd(sum(r["resto"] for r in es) // 100)} uncovered.</p></div>') + calc)
    corpo += ('<div class="testo">' + rim.t('<p><strong>Two things the calculator leaves out.</strong> A loan fee is deducted from each disbursement, so the college receives less than the amount borrowed: the regulations set the fee on a Direct PLUS loan at four percent of the principal; the fee actually charged in a given year can be slightly different. '
                                             'Ask the financial aid office for the exact figure and the net amount of your loan.[[cfr_202]] And a Parent PLUS loan depends on a credit check: the parent must not have an adverse credit history, or must obtain an endorser or document extenuating circumstances.[[cfr_200]]</p>') + '</div>'
              + rim.cit("cfr_202", "rate") + rim.cit("cfr_200", "credito"))
    corpo += (f'<div class="testo"><p>No figure to start from? The <a href="/{P_UNI}">college cost pages</a> show the average net price by family income at {len(DOMU["scelte"])} colleges, from the federal College Scorecard file, with this same sum already done.</p></div>')
    corpo += nota('<p><strong>This is arithmetic, not a recommendation to borrow the maximum.</strong> The limits say how much the federal government will lend, not how much a family can afford to repay. '
                  'The financial aid office of the college can tell you the exact amounts you are eligible for.</p>')
    corpo += (f'<h2 id="rate">Interest rate: {T_PLUS}% for {ANNO_TASSI}</h2><div class="testo">'
              + rim.t(f'<p>Direct PLUS Loans first disbursed from {per} have a fixed rate of {T_PLUS}%: the 10-year Treasury yield of {TASSI["asta_arrotondata"]}% plus {TASSI["righe"][2]["maggiorazione"]} points. The law caps the PLUS rate at {TASSI["righe"][2]["massimo"]}%.[[fr_tassi]] '
                      f'Each year’s loan keeps the rate of its own year. <a href="/{P_TASSI}#history">PLUS rates for every year since 2013</a>.</p></div>'))
    righe = []
    for saldo in (gen["anno"], 2 * gen["anno"], gen["totale"]):
        c = saldo * 100
        p = piano(c, mill(T_PLUS), anni_standard(c) * 12)
        righe.append(f'<tr data-esempio-plus="{c}"><th scope="row">{usd(saldo)}</th><td class="n">{anni_standard(c)} years</td><td class="n forte">{usdc(p["rata"])}</td><td class="n">{usdc(p["interessi"])}</td></tr>')
    corpo += ('<h2 id="repay">Repaying a Parent PLUS loan</h2><div class="testo">'
              + rim.t(f'<p>Parent PLUS loans made on or after July 1, 2026 must be repaid under the standard plan: a fixed monthly payment over {STD["fasce"][0]["anni"]} to {STD["fasce"][-1]["anni"]} years, depending on the principal owed. '
                      f'They cannot go into the <a href="/{P_RAP}">Repayment Assistance Plan</a>. Paying faster is allowed without penalty.[[legge]]</p>'
                      '<p><strong>A new loan also moves the old ones.</strong> A parent who takes a new Parent PLUS loan on or after July 1, 2026 must repay their older Parent PLUS loans under the standard plan too: the law applies the rule to “each excepted loan”, including those made before that date.[[legge]]</p></div>')
              + rim.cit("legge", "genitori_standard") + rim.cit("legge", "eccettuato")
              + tabella(f'Standard plan on a Parent PLUS balance at {T_PLUS}%: our calculation, not official figures. Interest that builds up before repayment starts is not included.{rim.ref("fr_tassi,legge")}',
                        [("Balance", 0), ("Period", 1), ("Monthly payment", 1), ("Total interest", 1)], righe, "ampia")
              + f'<p class="azioni"><a class="btn sec" href="/{P_RATA}">Try other balances and rates{ico("arrow")}</a></p>')
    faq_html, faq_ld = faq_blocco([
        ("parent plus loan", "What is a Parent PLUS loan?",
         f"A federal Direct PLUS Loan that a parent takes out to pay for a dependent undergraduate’s education. For {ANNO_TASSI} the fixed rate is {T_PLUS}%, and from July 1, 2026 parents can borrow up to {usd(gen['anno'])} a year and {usd(gen['totale'])} in total for each student.", "fr_tassi,fr_regola"),
        ("parent plus loan limits", "What are the Parent PLUS loan limits?",
         f"For periods of enrollment beginning on or after July 1, 2026: {usd(gen['anno'])} per academic year and {usd(gen['totale'])} in total, for each dependent student and for all of the student’s parents together.", "fr_regola"),
        ("parent plus loan limit", "Is the Parent PLUS limit per parent or per child?",
         f"Per child. The regulation counts the total of all Direct PLUS Loans that all parents borrow on behalf of each dependent student: {usd(gen['anno'])} a year and {usd(gen['totale'])} overall.", "fr_regola"),
        ("parent plus loan changes", "Do the new limits apply if my child was already in college?",
         f"Not right away. If the student was enrolled on June 30, 2026 and a Direct Loan had already been made for that program to the parent or the student, the limits do not apply for the student’s expected time to finish, up to {LIM['anni_eccezione']} academic years. If the student transfers to another school, the new limits apply.", "fr_regola,legge"),
        ("parent plus loan calculator", "What is the monthly payment on a Parent PLUS loan?",
         f"Under the standard plan at {T_PLUS}%, a balance of {usd(gen['anno'])} is about {usdc(piano(gen['anno'] * 100, mill(T_PLUS), anni_standard(gen['anno'] * 100) * 12)['rata'])} a month over {anni_standard(gen['anno'] * 100)} years, and {usd(gen['totale'])} about {usdc(piano(gen['totale'] * 100, mill(T_PLUS), anni_standard(gen['totale'] * 100) * 12)['rata'])} a month over {anni_standard(gen['totale'] * 100)} years (our calculation).", "fr_tassi,legge"),
        ("direct plus loan", "Can a Parent PLUS loan be repaid based on income?",
         "A Parent PLUS loan made on or after July 1, 2026 has to be repaid under the standard plan; the Repayment Assistance Plan is not available for it.", "legge"),
    ], rim)
    corpo += faq_html + rim.elenco()
    testata = banda(f"Federal Direct PLUS Loans · {ANNO_TASSI}", "Parent PLUS loans: rate, new limits and what they leave uncovered",
                    f"<strong>{T_PLUS}%</strong> fixed, up to <strong>{usd(gen['anno'])}</strong> a year and <strong>{usd(gen['totale'])}</strong> in total per student from July 1, 2026. Figures from the Federal Register and the law.", icona="users")
    pagina(P_PLUS, f"Parent PLUS Loan {ANNO_TASSI}: {T_PLUS}% Rate, {usd(gen['anno'])} Yearly Limit",
           f"Parent PLUS loans for {ANNO_TASSI}: {T_PLUS}% fixed rate, new limits of {usd(gen['anno'])} a year and {usd(gen['totale'])} in total per student, and a calculator of the gap.",
           corpo, testata, briciole=[("Home", ""), ("Parent PLUS loans", P_PLUS)], jsonld=[faq_ld])


# ---------------------------------------------------------------- schede dei costi delle università (prova di 200, dal file College Scorecard)
P_UNI = "college-costs/"
SC = carica("fonti_scorecard.json")
DOMU = carica("domanda_universita.json")
FONTI.update(SC["fonti"])
SC_AGG = date.fromisoformat(SC["fonti"]["scorecard"]["aggiornato_il"])
VOLUMI_UNI = {f["frase"]: f["volume_mese"] for s in DOMU["scelte"] for f in s["frasi"]}
TIPO_UNI = {"1": ("public", "Public"), "2": ("nonprofit", "Private nonprofit"), "3": ("forprofit", "Private for-profit")}
MANCA = {"NA": "Not reported in the file", "PS": "Suppressed in the file (privacy)"}


def _righe_scorecard():
    import csv
    with open(RADICE / SC["fonti"]["scorecard"]["estratto"], encoding="utf-8", newline="") as f:
        return {r["UNITID"]: r for r in csv.DictReader(f)}


def _anno_colonna(col):
    """L'anno di una colonna, come lo scrive il dizionario ufficiale (foglio Most_Recent_Inst_Cohort_Map), reso leggibile. Si ferma se il testo cambia forma."""
    t = SC["anni"][col]
    m = re.fullmatch(r"AcadYr (\d{4})-(\d{2}), reported in IPEDS DCY\d{4}-\d{2}", t)
    if m:
        return f"{m[1]}–{m[2]}", f"{m[1]}–{m[2]} academic year"
    m = re.fullmatch(r"Fall (\d{4}), reported in IPEDS DCY\d{4}-\d{2}", t)
    if m:
        return f"fall {m[1]}", f"fall {m[1]}"
    m = re.fullmatch(r"Fall (\d{4}) or AcadYr (\d{4})-(\d{2}) cohort \(differs by institutional calendar\), reported in IPEDS DCY(\d{4})-(\d{2})", t)
    if m:
        return f"{m[2]}–{m[3]} entering class", f"students who started in fall {m[1]} or during {m[2]}–{m[3]}, counted in the {m[4]}–{m[5]} data collection"
    m = re.fullmatch(r"NSLDS FY(\d{4}), FY(\d{4}) pooled cohorts", t)
    if m:
        return f"fiscal years {m[1]} and {m[2]}", f"federal fiscal years {m[1]} and {m[2]}, pooled"
    m = re.fullmatch(r"NSLDS AY(\d{4})-(\d{2}), AY(\d{4})-(\d{2}) pooled cohorts", t)
    if m:
        return f"{m[1]}–{m[2]} and {m[3]}–{m[4]}", f"award years {m[1]}–{m[2]} and {m[3]}–{m[4]}, pooled"
    raise SystemExit(f"dizionario Scorecard: anno di {col} in una forma non prevista: {t}")


ANNO_COL = {c: _anno_colonna(c) for c in SC["anni"]}
A_TASSE, A_COSTO, A_NETTO, A_AMM, A_LAUREA, A_DEBITO, A_PLUS, A_ISCR = (ANNO_COL[c][0] for c in ("TUITIONFEE_IN", "COSTT4_A", "NPT4_PUB", "ADM_RATE", "C150_4", "GRAD_DEBT_MDN", "PLUS_DEBT_INST_MD", "UGDS"))
if ANNO_COL["TUITIONFEE_IN"] != ANNO_COL["TUITIONFEE_OUT"] or len({ANNO_COL[c] for c in SC["anni"] if c.startswith("NPT4")}) != 1:
    raise SystemExit("dizionario Scorecard: tasse o prezzi netti con anni diversi tra loro")


def _fasce_reddito():
    out = []
    for i in "12345":
        m = re.search(r"for (\$[\d,]+)(?:-(\$[\d,]+)|\+) family income", SC["nomi"][f"NPT4{i}_PUB"])
        if not m or SC["nomi"][f"NPT4{i}_PRIV"].split(" (")[0] != SC["nomi"][f"NPT4{i}_PUB"].split(" (")[0]:
            raise SystemExit(f"dizionario Scorecard: fascia di reddito {i} in una forma non prevista")
        out.append(f"{m[1]} to {m[2]}" if m[2] else f"{m[1]} or more")
    return out


FASCE_REDDITO = _fasce_reddito()


def num(v):
    return re.fullmatch(r"-?\d+(\.\d+)?", v) is not None


def usd_s(n):
    return f"−${-n:,}" if n < 0 else f"${n:,}"


def soldi_sc(v):
    """Importo del file («64796») -> «$64,796»; NA e PS restano detti a parole."""
    return usd_s(int(v)) if num(v) else MANCA[v]


def pc_sc(v):
    """Quota del file («0.0365») -> «3.65%» (la stessa cifra, per cento, senza arrotondare)."""
    if not num(v):
        return MANCA[v]
    from decimal import Decimal
    x = Decimal(v) * 100
    if x != x.quantize(Decimal("0.01")):
        raise SystemExit(f"file Scorecard: quota {v} con più di quattro decimali")
    return f"{x.quantize(Decimal('0.01'))}%"   # sempre due decimali: è la cifra del file, non un arrotondamento


def cella(col, v, forte=False, pc=False):
    testo = pc_sc(v) if pc else soldi_sc(v)
    if not num(v):
        return f'<td class="na" data-c="{col}">{testo}</td>'
    return f'<td class="n{" forte" if forte else ""}" data-c="{col}">{testo}</td>'


def slug_uni(nome):
    return re.sub(r"[^a-z0-9]+", "-", nome.lower().replace("&", " and ").replace("'", "")).strip("-")


def url_calcolatore(v):
    """L'indirizzo del calcolatore del prezzo netto scritto nel file (NPCURL); None se manca o non è un indirizzo web pulito."""
    if v in ("NA", "PS", ""):
        return None
    u = v.strip() if re.match(r"https?://", v.strip(), re.I) else "https://" + v.strip()
    p = urlparse(u)
    if not p.hostname or " " in u or '"' in u or "<" in u or "." not in p.hostname:
        return None
    return u


def prepara_universita():
    righe = _righe_scorecard()
    out, slug_visti = [], set()
    for s in DOMU["scelte"]:
        r = righe[s["unitid"]]
        if r["INSTNM"] != s["nome"] or r["CONTROL"] not in TIPO_UNI or r["STABBR"] not in VOCI:
            raise SystemExit(f"università {s['unitid']}: nome, tipo o Stato non previsti ({r['INSTNM']}, {r['CONTROL']}, {r['STABBR']})")
        suff = "PUB" if r["CONTROL"] == "1" else "PRIV"
        u = {"r": r, "s": s, "nome": r["INSTNM"], "slug": slug_uni(r["INSTNM"]), "suff": suff, "pubblica": r["CONTROL"] == "1",
             "netto": r[f"NPT4_{suff}"], "fasce": [(f"NPT4{i}_{suff}", r[f"NPT4{i}_{suff}"]) for i in "12345"], "col_netto": f"NPT4_{suff}"}
        if u["slug"] in slug_visti or not num(r["TUITIONFEE_IN"]) or not num(u["netto"]):
            raise SystemExit(f"università {u['nome']}: slug doppio o dati di base mancanti")
        slug_visti.add(u["slug"])
        u["percorso"] = f'{P_UNI}{u["slug"]}/'
        u["buco_medio"] = buco_4(u["netto"])
        out.append(u)
    # confronti calcolati dal file: posto del prezzo netto medio (1 = il più basso; a pari prezzo, stesso posto) tra le 200, nel tipo e nello Stato
    for u in out:
        n = int(u["netto"])
        tipo = [x for x in out if x["r"]["CONTROL"] == u["r"]["CONTROL"]]
        stato = [x for x in out if x["r"]["STABBR"] == u["r"]["STABBR"]]
        u["posto"] = {k: (1 + sum(1 for x in g if int(x["netto"]) < n), len(g)) for k, g in (("tutte", out), ("tipo", tipo), ("stato", stato))}
        u["vicine"] = sorted((x for x in stato if x is not u), key=lambda x: x["nome"])[:8]
        u["simili"] = [] if u["vicine"] else sorted((x for x in out if x is not u), key=lambda x: (abs(int(x["netto"]) - n), x["nome"]))[:6]
    return out


def ordinale(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def frase_posto(u, stato):
    def posto(k, di_che):
        p, su = u["posto"][k]
        return f'<span data-posto="{k}:{p}:{su}">{"the lowest" if p == 1 else f"the {ordinale(p)} lowest"} of the {su} {di_che}</span>'
    tipo = TIPO_UNI[u["r"]["CONTROL"]][1].lower()
    testo = (f'<p>Among the {u["posto"]["tutte"][1]} colleges with a page on this site, the average net price at {h(u["nome"])} ({usd_s(int(u["netto"]))}) is {posto("tutte", "colleges")}, '
             f'and {posto("tipo", f"{tipo} colleges")}. ')
    if u["posto"]["stato"][1] > 1:
        testo += f'In {h(stato)} it is {posto("stato", f"colleges with a page here")}. '
    else:
        testo += f'It is the only college in {h(stato)} with a page here so far. '
    return testo + 'Net prices at public colleges count in-state students only, so a public and a private figure are not measured on quite the same students.</p>'



def sigla_nome(nome):
    return "".join(w[0] for w in re.sub(r"[^A-Za-z ]", " ", nome).split() if w.lower() not in ("of", "at", "and", "the", "in", "for", "a", "an", "on")).lower()


def parole_ricerca(u):
    """Che cosa trova la ricerca dell'indice: nome, città, Stato, i nomi misurati, gli alias scritti nel file e le iniziali del nome
    (con e senza campus). Una sigla di più università, come «usc» o «msu», sta su tutte: la ricerca le mostra tutte."""
    r = u["r"]
    senza_campus = re.sub(r"^The ", "", re.split(r"\s*-\s*(?=[^-]*$)", r["INSTNM"])[0]) if re.search(r"(University|College|Institute)[^-]*-", r["INSTNM"]) else r["INSTNM"]
    pezzi = [u["nome"], r["CITY"], VOCI[r["STABBR"]]["nome"], r["STABBR"]] + [f["frase"].rsplit(" ", 1)[0] for f in u["s"]["frasi"]]
    if r["ALIAS"] not in ("NA", ""):
        pezzi += [x.strip() for x in re.split(r"[|;,]", r["ALIAS"]) if x.strip()]
    pezzi += [sigla_nome(re.sub(r"^The ", "", r["INSTNM"]).replace("-", " ")), sigla_nome(senza_campus)]
    visti, out = set(), []
    for x in pezzi:
        x = re.sub(r"\s+", " ", x.lower()).strip()
        if x and x not in visti:
            visti.add(x)
            out.append(x)
    return " | ".join(out)


def buco_4(v):
    """Quattro anni al prezzo annuo v (dollari, dal file): totali di studente, genitori e resto. Un prezzo negativo conta zero."""
    c = max(int(v), 0) * 100
    rr = buco(c, 4)
    return {"anno": int(v), "quattro": 4 * c // 100, "studente": sum(x["studente"] for x in rr) // 100, "genitori": sum(x["genitori"] for x in rr) // 100, "resto": sum(x["resto"] for x in rr) // 100}


def link_fafsa(sigla):
    return slug_stato(sigla) if sigla in STATI else P_SCAD


def titolo_universita(u):
    r, s = u["r"], u["s"]
    F = s["frase_titolo_scritta"]
    tin, tout, costo = r["TUITIONFEE_IN"], r["TUITIONFEE_OUT"], r["COSTT4_A"]
    if s["frase_titolo"].endswith(" tuition") or not num(costo):
        cifra = f"{usd(int(tin))} In-State" if (u["pubblica"] and tin != tout) else usd(int(tin))
        prove = [f"{F} {A_TASSE}: {cifra}, Net Price by Income, Loan Gap", f"{F} {A_TASSE}: {cifra}, Net Price, Loan Gap", f"{F}: {cifra}, Net Price, Loan Gap"]
        if cifra.endswith("In-State"):   # università pubbliche: «In-State» resta nel titolo finché ci sta
            prove += [f"{F}: {cifra}, Net Price", f"{F}: {cifra}"]
        prove += [f"{F} {A_TASSE}: {usd(int(tin))}, Net Price, Loan Gap",
                 f"{F}: {usd(int(tin))}, Net Price, Loan Gap", f"{F}: {usd(int(tin))} and Net Price", f"{F}: Net Price, Loan Gap",
                 f"{F}: {usd(int(tin))}, Loan Gap", f"{F}: {usd(int(tin))} a Year", f"{F} and Net Price", f"{F} {A_TASSE}", F]
    else:
        dentro = [f"{F}: {usd(int(costo))} a Year In-State, Net Price, Loan Gap", f"{F}: {usd(int(costo))} a Year In-State, Net Price", f"{F}: {usd(int(costo))} a Year In-State"] if u["pubblica"] else []
        prove = dentro + [f"{F}: {usd(int(costo))} a Year, Net Price by Income, Loan Gap", f"{F}: {usd(int(costo))} a Year, Net Price, Loan Gap", f"{F}: {usd(int(costo))} a Year and Net Price", f"{F}: Net Price, Loan Gap", F]
    for t in prove:
        if len(t) <= 65 and t not in TITOLI.values():
            return t
    raise SystemExit(f"università {u['nome']}: nessun titolo entro 65 caratteri che cominci con «{F}»")


def descrizione_universita(u):
    r = u["r"]
    n, tin, tout = u["nome"], usd(int(r["TUITIONFEE_IN"])), soldi_sc(r["TUITIONFEE_OUT"])
    tasse = f"{tin} in-state, {tout} out-of-state" if (num(r["TUITIONFEE_OUT"]) and r["TUITIONFEE_IN"] != r["TUITIONFEE_OUT"]) else tin
    prove = [f"{n}: tuition and fees {tasse} ({A_TASSE}), average net price {usd_s(int(u['netto']))} by family income, and the gap after federal loans. Official data.",
             f"{n}: tuition and fees {tasse} ({A_TASSE}), net price {usd_s(int(u['netto']))} by income, gap after federal loans. Official data.",
             f"{n}: tuition and fees {tasse} ({A_TASSE}), net price by income, gap after federal loans.",
             f"{n}: tuition {tin} ({A_TASSE}), net price by income, loan gap. Official data."]
    for d in prove:
        if 70 <= len(d) <= 160 and d not in DESCRIZIONI.values():
            return d
    raise SystemExit(f"università {u['nome']}: nessuna descrizione entro 160 caratteri")


def riga_buco(etichetta, col, v):
    if not num(v):
        return f'<tr data-gap="{col}"><th scope="row">{etichetta}</th><td class="na" colspan="5" data-c="{col}">{MANCA[v]}</td></tr>'
    b = buco_4(v)
    return (f'<tr data-gap="{col}"><th scope="row">{etichetta}</th><td class="n" data-c="{col}">{usd_s(b["anno"])}</td><td class="n" data-g="quattro">{usd(b["quattro"])}</td>'
            f'<td class="n" data-g="studente">{usd(b["studente"])}</td><td class="n" data-g="genitori">{usd(b["genitori"])}</td><td class="n forte" data-g="resto">{usd(b["resto"])}</td></tr>')


def pagina_universita(u, tutte):
    rim = Rimandi()
    r, s, nome = u["r"], u["s"], u["nome"]
    sigla = r["STABBR"]
    stato = VOCI[sigla]["nome"]
    tipo = TIPO_UNI[r["CONTROL"]][1]
    if SC["etichette"]["CONTROL"][r["CONTROL"]] != tipo:
        raise SystemExit("dizionario Scorecard: etichette di CONTROL diverse")
    dip, gen = LIM["dipendente"], LIM["genitori"]
    quattro = sum(dip["anni"][min(i, 2)]["totale"] for i in range(4))
    agg = data_lunga(SC_AGG)
    tin, tout, costo, netto = r["TUITIONFEE_IN"], r["TUITIONFEE_OUT"], r["COSTT4_A"], u["netto"]
    stesse = tin == tout
    ref = rim.ref("scorecard,scorecard_diz")
    chi_netto = ("first-time, full-time undergraduates who paid in-state tuition and received federal student aid" if u["pubblica"]
                 else "first-time, full-time undergraduates who received federal student aid")
    # ---- riquadro in alto
    voci = [(soldi_sc(tin), f"tuition and fees, {A_TASSE}" + ("" if stesse else ", in-state")),
            (soldi_sc(tout) if not stesse else soldi_sc(costo), (f"tuition and fees, {A_TASSE}, out-of-state" if not stesse else f"average cost of attendance, {A_COSTO}" + (", in-state students" if u["pubblica"] else ""))),
            (usd_s(int(netto)), f"average net price a year, {A_NETTO}" + (", in-state students with federal aid" if u["pubblica"] else ", students with federal aid")),
            (pc_sc(r["ADM_RATE"]) if num(r["ADM_RATE"]) else "Not reported", f"admission rate, {A_AMM}")]
    sotto = (f'{ico("info")} From the U.S. Department of Education’s College Scorecard file updated <strong>{agg}</strong>, read on {giorno(FONTI["scorecard"]["letto_il"])}{ref} · '
             f'each figure carries the year the Department assigns to it')
    corpo = f'<div data-universita="{r["UNITID"]}">' + fatti(voci, sotto)
    # ---- tasse e costo totale
    righe = [f'<tr><th scope="row">Tuition and fees, in-state</th>{cella("TUITIONFEE_IN", tin, True)}<td>{A_TASSE}</td></tr>',
             f'<tr><th scope="row">Tuition and fees, out-of-state</th>{cella("TUITIONFEE_OUT", tout, True)}<td>{A_TASSE}</td></tr>',
             f'<tr><th scope="row">Average cost of attendance{", in-state students" if u["pubblica"] else ""}: tuition, fees, books, supplies and living expenses</th>{cella("COSTT4_A", costo, True)}<td>{A_COSTO}</td></tr>']
    corpo += (f'<h2 id="tuition">{h(nome)} tuition and total cost</h2><div class="testo"><p>'
              + (f'The College Scorecard file lists the same tuition and required fees for in-state and out-of-state students at {h(nome)}: {soldi_sc(tin)} for the {ANNO_COL["TUITIONFEE_IN"][1]}. '
                 if stesse else
                 f'For the {ANNO_COL["TUITIONFEE_IN"][1]}, the College Scorecard file lists tuition and required fees of {soldi_sc(tin)} for in-state students and {soldi_sc(tout)} for out-of-state students at {h(nome)}. ')
              + (f'The average cost of attendance{" for in-state students" if u["pubblica"] else ""}, which adds books, supplies and living expenses, was {soldi_sc(costo)} in {A_COSTO}, the latest year in the file.' if num(costo)
                 else 'The file has no average cost of attendance for this college.') + f'{ref}</p></div>'
              + tabella(f'Published price at {h(nome)} ({h(r["CITY"])}, {sigla}; {tipo.lower()}). Source: College Scorecard file updated {agg}.{ref}',
                        [("Figure", 0), ("Amount a year", 1), ("Year of the data", 0)], righe, "ampia"))
    # ---- prezzo netto per fascia di reddito
    righe = [f'<tr><th scope="row">{etich}</th>{cella(col, v, True)}</tr>' for etich, (col, v) in zip(FASCE_REDDITO, u["fasce"])]
    righe.append(f'<tr class="ora"><th scope="row">All income levels (average)</th>{cella(u["col_netto"], netto, True)}</tr>')
    corpo += (f'<h2 id="net-price">Average net price by family income</h2><div class="testo"><p>Net price is the cost of attendance minus the average grant and scholarship aid. '
              f'It is what families paid on average for one year, before loans. The file gives it for {chi_netto}, in {A_NETTO}, by the family income used to work out aid.{ref}</p></div>'
              + tabella(f'Average net price for one year at {h(nome)}, {A_NETTO}, {chi_netto}.{ref}', [("Family income", 0), ("Average net price a year", 1)], righe, stretta=True)
              + f'<div class="testo" data-confronto>{frase_posto(u, stato)}</div>')
    if u["pubblica"]:
        corpo += nota(f'<p><strong>Out-of-state students are not in these averages.</strong> For public colleges the file counts only students who pay in-state tuition, and it has no net price for out-of-state students. '
                      f'Out-of-state tuition and fees at {h(nome)} are {soldi_sc(tout)}, against {soldi_sc(tin)} in-state. '
                      'The cost of attendance and the gap table are also in-state only; the file has no out-of-state cost of attendance.</p>', info=True)
    # ---- ammissione, laurea, debito
    righe = [f'<tr><th scope="row">Admission rate</th>{cella("ADM_RATE", r["ADM_RATE"], True, pc=True)}<td>{A_AMM}</td></tr>',
             f'<tr><th scope="row">Graduation rate: first-time, full-time students who finished within 150% of the normal time (six years for a bachelor’s degree)</th>{cella("C150_4", r["C150_4"], True, pc=True)}<td>{A_LAUREA}</td></tr>',
             f'<tr><th scope="row">Median federal student loan debt of borrowers who completed</th>{cella("GRAD_DEBT_MDN", r["GRAD_DEBT_MDN"], True)}<td>{A_DEBITO}</td></tr>',
             f'<tr><th scope="row">Median Parent PLUS loan debt at this college</th>{cella("PLUS_DEBT_INST_MD", r["PLUS_DEBT_INST_MD"], True)}<td>{A_PLUS}</td></tr>',
             f'<tr><th scope="row">Undergraduate students</th><td class="n forte" data-c="UGDS">{int(r["UGDS"]):,}</td><td>{A_ISCR}</td></tr>']
    corpo += (f'<h2 id="outcomes">Admission rate, graduation rate and median debt</h2>'
              + tabella(f'{h(nome)}: admission, completion and debt figures in the College Scorecard file. The debt figures count federal loans only.{ref}',
                        [("Figure", 0), ("Value", 1), ("Year of the data", 0)], righe, "ampia"))
    assenti = [c for c in ("TUITIONFEE_OUT", "COSTT4_A", "ADM_RATE", "C150_4", "GRAD_DEBT_MDN", "PLUS_DEBT_INST_MD") + tuple(c for c, _ in u["fasce"]) if not num(r[c])]
    if assenti:
        ps = any(r[c] == "PS" for c in assenti)
        na = any(r[c] == "NA" for c in assenti)
        corpo += nota('<p><strong>Some figures are missing.</strong> '
                      + ('“Not reported in the file” means the Department’s file has no value for this college (it is written NA there). ' if na else '')
                      + ('“Suppressed in the file” means the Department hides the value to protect the privacy of a small group of students (it is written PS there). ' if ps else '')
                      + 'We do not fill the gaps with estimates or with figures from other sites.</p>', info=True)
    # ---- il buco dopo i prestiti federali
    b = u["buco_medio"]
    righe = [riga_buco(etich, col, v) for etich, (col, v) in zip(FASCE_REDDITO, u["fasce"])]
    righe.append(riga_buco("All income levels (average)", u["col_netto"], netto).replace("<tr ", '<tr class="ora" ', 1))
    if num(costo):
        righe.append(riga_buco("No grants at all: full in-state cost of attendance" if u["pubblica"] else "No grants at all: full cost of attendance", "COSTT4_A", costo))
    frase_buco = (f'the federal limits could cover all of it' if b["resto"] == 0 else f'the federal limits leave <strong>{usd(b["resto"])}</strong> to find elsewhere')
    corpo += (f'<h2 id="gap">The gap after federal loans at {h(nome)}</h2><div class="testo">'
              + rim.t(f'<p>For students starting now, federal loans have a ceiling. A dependent undergraduate can borrow {usd(dip["anni"][0]["totale"])} in the first year, {usd(dip["anni"][1]["totale"])} in the second and {usd(dip["anni"][2]["totale"])} a year after that, '
                      f'up to {usd(dip["totale"])} in all.[[manuale]] Since July 1, 2026 parents can borrow at most {usd(gen["anno"])} a year and {usd(gen["totale"])} in total for each student with Parent PLUS loans.[[fr_regola]] '
                      f'Over four years that is at most {usd(quattro)} for the student plus {usd(gen["totale"])} for the parents: {usd(quattro + gen["totale"])} (our addition).</p>'
                      f'<p>At the average net price of {usd_s(b["anno"])} a year, four years at {h(nome)} come to {usd(b["quattro"])}; {frase_buco}. '
                      f'The table does the same sum for each income band, holding the {A_NETTO} price flat for four years.</p></div>')
              + '<p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Four years at {h(nome)} at the {A_NETTO} net price, against the federal loan limits for a dependent student starting on or after July 1, 2026. Our arithmetic on official figures.{rim.ref("scorecard,manuale,fr_regola")}',
                        [("Family income", 0), ("Net price a year", 1), ("Four years", 1), ("Student loans, at most", 1), ("Parent PLUS, at most", 1), ("Left uncovered", 1)], righe, "ampia")
              + nota('<p><strong>This is arithmetic, not a forecast and not advice to borrow the maximum.</strong> Prices usually rise each year, a family can borrow less than the limit, a loan fee is taken from each disbursement, '
                     'and a Parent PLUS loan needs a credit check. “Left uncovered” has to come from savings, income, work, more scholarships or private loans. '
                     f'Students who were already enrolled and borrowing before July 1, 2026 may keep the old Parent PLUS rules for a time: see <a href="/{P_LIM}">federal loan limits</a>. '
                     f'Independent students have higher limits of their own and no Parent PLUS: see <a href="/{P_LIM}#undergraduate">federal loan limits</a>.</p>')
              + f'<p class="azioni"><a class="btn" href="/{P_PLUS}#gap">Try your own cost in the gap calculator{ico("arrow")}</a><a class="btn sec" href="/{P_LIM}">All federal loan limits</a></p>')
    # ---- come leggere
    npc = url_calcolatore(r["NPCURL"])
    corpo += ('<h2 id="read">How to read this page</h2><div class="testo"><ul>'
              f'<li><strong>Every figure is copied from one federal file</strong>, the College Scorecard institution file the Department of Education updated on {agg}. Nothing is estimated or taken from other websites.</li>'
              f'<li><strong>The file runs behind the college’s own website.</strong> Tuition and fees are for {A_TASSE}; cost of attendance and net price are for {A_NETTO}. For next year’s price, check {h(nome)} directly.</li>'
              f'<li><strong>Net price is an average, not an offer.</strong> It covers {chi_netto}. Your own price depends on your aid package.</li>'
              '<li><strong>Family income</strong> is the income the college used to work out financial aid: for a dependent student, the student’s and the parents’ income together.</li>'
              f'<li><strong>The graduation rate</strong> follows the {A_LAUREA}; the admission rate is for {A_AMM}.</li>'
              '<li><strong>The gap is our own arithmetic</strong> on the file’s net price and the official loan limits. It is not a figure published by the college or the Department.</li></ul></div>')
    if npc:
        corpo += (f'<p class="azioni"><a class="btn sec" href="{h(npc)}" rel="nofollow noopener" data-npc>{h(nome)} net price calculator (address listed in the file){ico("arrow")}</a></p>')
    else:
        corpo += '<p class="small">The file lists no usable address for this college’s net price calculator.</p>'
    # ---- scadenza FAFSA dello Stato
    ha_pagina = sigla in STATI
    corpo += (f'<h2 id="fafsa">FAFSA deadline in {h(stato)} for {ANNO}</h2><div class="testo"><p>{h(nome)} is in {h(r["CITY"])}, {h(stato)}. Aid starts with the FAFSA form: for federal aid the {ANNO} form must be received by {giorno(FAFSA["chiusura_federale"])}, '
              f'and this is what the official form says about state aid in {h(stato)}.{rim.ref("fafsa_2728")} The college can set an earlier date of its own: ask its financial aid office.</p></div>'
              + rim.voce(sigla)
              + f'<p class="azioni"><a class="btn sec" href="/{link_fafsa(sigla)}">{h(stato) + " FAFSA deadline, explained" if ha_pagina else "FAFSA deadlines for every state"}{ico("arrow")}</a></p>')
    # ---- prestiti
    corpo += (f'<h2 id="loans">Federal loan numbers for {ANNO_TASSI}</h2><div class="testo"><p>Loans first disbursed from {giorno(TASSI["dal"])} to June 30, {TASSI["al"][:4]} carry a fixed rate of {T_UG}% for undergraduates and {T_PLUS}% for Parent PLUS loans.{rim.ref("fr_tassi")}</p></div>'
              f'<p class="azioni"><a class="btn sec" href="/{P_TASSI}">Loan interest rates</a><a class="btn sec" href="/{P_LIM}">Loan limits</a><a class="btn sec" href="/{P_PLUS}">Parent PLUS loans</a>'
              f'<a class="btn sec" href="/{P_RATA}">Payment calculator</a><a class="btn sec" href="/{P_RAP}">Repayment Assistance Plan</a></p>')
    # ---- altre università dello stesso Stato
    vicine = u["vicine"] or u["simili"]
    if vicine:
        griglia = "".join(f'<li><a href="/{x["percorso"]}"><b>{h(x["nome"])}</b><small>{soldi_sc(x["r"]["TUITIONFEE_IN"])} tuition and fees{"" if x["r"]["TUITIONFEE_IN"] == x["r"]["TUITIONFEE_OUT"] else ", in-state"}</small></a></li>' for x in vicine)
        corpo += (f'<h2 id="others">Other colleges in {h(stato)}</h2>' if u["vicine"] else
                  f'<h2 id="others">Colleges with a similar net price</h2><p class="small">No other college in {h(stato)} has a page here yet. These are the closest by average net price.</p>') + f'<ul class="griglia larga uni">{griglia}</ul>'
    corpo += f'<p class="azioni"><a class="btn sec" href="/{P_UNI}">All {len(tutte)} colleges{ico("arrow")}</a></p>'
    # ---- FAQ da ricerche misurate
    faq = []
    if s["tuition"] and s["tuition"]["volume_mese"] > 0:
        faq.append((s["tuition"]["frase"], f"How much is tuition at {nome}?",
                    (f"Tuition and required fees at {nome} are {soldi_sc(tin)} for the {ANNO_COL['TUITIONFEE_IN'][1]}, the same for in-state and out-of-state students. " if stesse else
                     f"Tuition and required fees at {nome} are {soldi_sc(tin)} for in-state students and {soldi_sc(tout)} for out-of-state students for the {ANNO_COL['TUITIONFEE_IN'][1]}. ")
                    + f"The figure comes from the U.S. Department of Education’s College Scorecard file updated on {agg}.", "scorecard,scorecard_diz"))
    if s["cost"] and s["cost"]["volume_mese"] > 0:
        con = [(e, int(v)) for e, (c, v) in zip(FASCE_REDDITO, u["fasce"]) if num(v)]
        faq.append((s["cost"]["frase"], f"What does {nome} cost per year after grants and scholarships?",
                    f"The average net price at {nome} was {usd_s(int(netto))} a year in {A_NETTO}, for {chi_netto}. "
                    + (f"By family income it went from {usd_s(con[0][1])} (income of {con[0][0]}) to {usd_s(con[-1][1])} (income of {con[-1][0]}). " if len(con) >= 2 else "")
                    + (f"The average cost of attendance{' for in-state students' if u['pubblica'] else ''} before aid was {soldi_sc(costo)}." + (" The file has no out-of-state cost of attendance." if u["pubblica"] else "") if num(costo) else ""), "scorecard,scorecard_diz"))
    ld = []
    if faq:
        faq_html, faq_ld = faq_blocco(faq, rim)
        corpo += faq_html
        ld.append(faq_ld)
    corpo += rim.elenco(nota='<p class="small">College figures are copied from the College Scorecard data file; the year of each figure comes from the Department’s data dictionary. '
                             'The gap figures are our own arithmetic. See <a href="/how-we-check/">how we check</a>.</p>') + "</div>"
    testata = banda(f"{r['CITY']}, {sigla} · {tipo} · College Scorecard data", f"{nome}: tuition, net price and the gap after federal loans",
                    (f"Tuition and fees <strong>{soldi_sc(tin)}</strong>" + ("" if stesse else f" in-state, <strong>{soldi_sc(tout)}</strong> out-of-state") + f" for {A_TASSE}. "
                     f"Average net price <strong>{usd_s(int(netto))}</strong> a year ({A_NETTO}). From the federal file updated {agg}."), icona="cap")
    pagina(u["percorso"], titolo_universita(u), descrizione_universita(u), corpo, testata,
           briciole=[("Home", ""), ("College costs", P_UNI), (nome, u["percorso"])], jsonld=ld)


def indice_universita(tutte):
    rim = Rimandi()
    ref = rim.ref("scorecard,scorecard_diz")
    agg = data_lunga(SC_AGG)
    dip, gen = LIM["dipendente"], LIM["genitori"]
    quattro = sum(dip["anni"][min(i, 2)]["totale"] for i in range(4))
    per_tipo = {k: sum(1 for u in tutte if u["r"]["CONTROL"] == k) for k in TIPO_UNI}
    oltre = sum(1 for u in tutte if u["buco_medio"]["resto"] > 0)
    sigle = {u["r"]["STABBR"] for u in tutte}
    stati = len([x for x in sigle if x != "DC" and not VOCI[x]["territorio"]])
    if any(VOCI[x]["territorio"] for x in sigle):
        raise SystemExit("indice delle università: c'è un territorio tra gli Stati: riscrivere l'etichetta")
    voci = [(str(len(tutte)), "colleges with a page: the ones people search for most"), (str(stati), "states, plus the District of Columbia" if "DC" in sigle else "states"),
            (str(oltre), f"where four years at the average net price cost more than federal loans can cover"), (A_TASSE, f"year of the tuition figures; net price is for {A_NETTO}")]
    sotto = f'{ico("info")} College Scorecard file updated <strong>{agg}</strong>, read on {giorno(FONTI["scorecard"]["letto_il"])}{ref}'
    corpo = fatti(voci, sotto)
    corpo += (f'<h2 id="list">Tuition, net price and loan gap at {len(tutte)} colleges</h2><div class="testo"><p>Each row is copied from the U.S. Department of Education’s College Scorecard file. '
              f'Tuition and fees are for {A_TASSE}. Net price is the {A_NETTO} average after grants and scholarships'
              f'{" (in-state students only at public colleges)" if per_tipo["1"] else ""}. The last column is our arithmetic: four years at that net price, minus the most a dependent student ({usd(quattro)}) '
              f'and the parents ({usd(gen["totale"])}) can borrow in federal loans from July 1, 2026.{rim.ref("manuale,fr_regola")}</p></div>')
    righe = []
    for u in sorted(tutte, key=lambda x: x["nome"].lower()):
        r = u["r"]
        cerca = parole_ricerca(u)
        righe.append(f'<tr data-nome="{h(cerca)}" data-tipo="{TIPO_UNI[r["CONTROL"]][0]}" data-sigla="{r["UNITID"]}"><th scope="row"><a href="/{u["percorso"]}">{h(u["nome"])}</a><br><span class="small">{h(r["CITY"])}, {r["STABBR"]} · {TIPO_UNI[r["CONTROL"]][1]}</span></th>'
                     f'{cella("TUITIONFEE_IN", r["TUITIONFEE_IN"])}{cella("TUITIONFEE_OUT", r["TUITIONFEE_OUT"])}{cella(u["col_netto"], u["netto"], True)}<td class="n" data-g="resto">{usd(u["buco_medio"]["resto"])}</td></tr>')
    corpo += (f'<div data-scadenze data-cosa="colleges"><div class="card filtri" data-filtri hidden><label>Find a college<input type="search" data-cerca placeholder="Name, city or state, for example Ohio" autocomplete="off"></label>'
              f'<label>Show<select data-tipo><option value="">All {len(tutte)} colleges</option>'
              + "".join(f'<option value="{TIPO_UNI[k][0]}">{TIPO_UNI[k][1]} ({per_tipo[k]})</option>' for k in TIPO_UNI if per_tipo[k])
              + '</select></label><p class="stato-t" data-stato aria-live="polite"></p></div><p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella(f'Tuition and fees ({A_TASSE}), average net price ({A_NETTO}) and what four years leave uncovered after federal loans. Source: College Scorecard file updated {agg}; last column, our arithmetic.{ref}',
                        [("College", 0), ("Tuition, in-state", 1), ("Tuition, out-of-state", 1), ("Average net price a year", 1), ("Left after federal loans, 4 years", 1)], righe, "ampia uni")
              + '<p class="card" data-vuoto hidden>No college matches. Clear the search box to see them all.</p></div>')
    corpo += ('<h2 id="read">How to read the table</h2><div class="testo"><ul>'
              f'<li><strong>One federal file, one date.</strong> Every figure comes from the College Scorecard institution file updated on {agg}. The file runs about a year behind colleges’ own websites.</li>'
              '<li><strong>Net price is an average.</strong> It is the cost of attendance minus average grants and scholarships, for first-time, full-time undergraduates who received federal aid. Each college page splits it into five family income bands.</li>'
              '<li><strong>Public colleges:</strong> the net price counts only students paying in-state tuition. The file has no net price for out-of-state students.</li>'
              f'<li><strong>“Left after federal loans”</strong> assumes the {A_NETTO} net price for four years, a dependent student borrowing the full federal limit each year and parents borrowing Parent PLUS loans up to their limit. It is arithmetic, not advice to borrow.</li>'
              '<li><strong>Missing values</strong> are shown as missing. We do not estimate them.</li></ul></div>')
    corpo += (f'<h2 id="which">Why these {len(tutte)} colleges</h2><div class="testo"><p>The Scorecard file has {SC["fonti"]["scorecard"]["istituti"]:,} institutions. This first set covers the {len(tutte)} four-year colleges whose tuition and cost people in the United States search for most, '
              f'by measured monthly searches. A college without a page here is not better or worse; it is just not in the first set.</p></div>'
              f'<p class="azioni"><a class="btn sec" href="/{P_SCAD}">FAFSA deadlines by state</a><a class="btn sec" href="/{P_LIM}">Federal loan limits</a><a class="btn sec" href="/{P_PLUS}">Parent PLUS loans</a></p>')
    corpo += rim.elenco(nota='<p class="small">College figures are copied from the College Scorecard data file; the year of each figure comes from the Department’s data dictionary. '
                             'The gap figures are our own arithmetic. See <a href="/how-we-check/">how we check</a>.</p>')
    testata = banda(f"College Scorecard data · updated {agg}", f"College costs: tuition, net price and loan gap at {len(tutte)} colleges",
                    f"Tuition and fees for {A_TASSE}, average net price by family income, and what federal loans leave uncovered under the limits in force since July 1, 2026. Copied from the Department of Education’s file.", icona="cap")
    pagina(P_UNI, f"College Tuition and Net Price {A_TASSE}: {len(tutte)} Colleges Compared",
           f"Tuition and fees ({A_TASSE}), average net price and the gap after federal loans at {len(tutte)} U.S. colleges, copied from the official College Scorecard file.",
           corpo, testata, briciole=[("Home", ""), ("College costs", P_UNI)])


# ---------------------------------------------------------------- home
def home():
    rim = Rimandi()
    gen, dip = LIM["genitori"], LIM["dipendente"]
    con_data = sum(1 for v in FAFSA["voci"] if tipo_voce(v) == "date")
    schede = [
        ("calendar", f"FAFSA deadlines {ANNO}", giorno(FAFSA["chiusura_federale"]), f"Federal deadline. {con_data} states and territories set earlier dates of their own: the official wording for all {len(FAFSA['voci'])}.", P_SCAD, "Deadlines by state", "fafsa_2728"),
        ("percent", f"Loan interest rates {ANNO_TASSI}", f"{T_UG}%", f"Undergraduate rate; {T_GRAD}% for graduate students and {T_PLUS}% for PLUS loans. Every year since 2013.", P_TASSI, "Rates by year", "fr_tassi"),
        ("cap", "Loan limits from July 1, 2026", f"{usd(dip['anni'][0]['totale'])}–{usd(LIM['professionale']['anno'])}", f"A year, from first-year undergraduates to professional students. New caps for graduate students and parents.", P_LIM, "All limits", "fr_regola,manuale"),
        ("calc", "Payment calculator", f"{STD['fasce'][0]['anni']}–{STD['fasce'][-1]['anni']} years", "The standard plan for new loans lasts longer the more you owe. Monthly payment and total interest for your balance.", P_RATA, "Calculate a payment", "legge"),
        ("chart", "Repayment Assistance Plan", f"{RAP['scaglioni'][1]['pc']}%–{RAP['scaglioni'][-1]['pc']}% of income", f"The income-based plan that started on July 1, 2026, with the formula from the law and a calculator.", P_RAP, "RAP calculator", "legge"),
        ("users", "Parent PLUS loans", f"{usd(gen['anno'])} a year", f"And {usd(gen['totale'])} in total per student, at {T_PLUS}%. See how much the federal limits leave uncovered.", P_PLUS, "Parent PLUS", "fr_regola,fr_tassi"),
        ("doc", f"College costs {A_TASSE}", f"{len(DOMU['scelte'])} colleges", "Tuition, net price by family income and what federal loans leave uncovered, college by college, copied from the federal College Scorecard file.", P_UNI, "College costs", "scorecard"),
    ]
    corpo = '<div class="pull"><ul class="schede">' + "".join(
        f'<li><h3>{ico(i)}{h(t)}</h3><p class="big">{h(big)}</p><p>{h(txt)}{rim.ref(f)}</p><p class="azioni"><a class="btn" href="/{u}">{h(b)}{ico("arrow")}</a></p></li>' for i, t, big, txt, u, b, f in schede) + "</ul></div>"
    corpo += (f'<h2 id="what">What this site is</h2><div class="testo"><p>Paying for college in the United States runs on a handful of official numbers: the date your state wants the FAFSA form, the interest rate Congress’s formula produces each year, '
              f'the most the federal government will lend, and the formula that turns a balance or an income into a monthly payment. They are public, but scattered across a 23-page form, Federal Register notices and a law.</p>'
              f'<p>{NOME} copies those numbers onto plain pages, quotes the sentence they come from, links the document and shows the date we read it. The calculators use only those official figures and ordinary arithmetic. '
              f'Nothing here is advice about what you should borrow.</p></div>')
    prossime = sorted(((prima_data(s), s) for s in ORDINE_STATI if prima_data(s)), key=lambda x: x[0])
    righe = "".join(f'<li><div class="cosa"><a href="/{slug_stato(s)}">{h(VOCI[s]["nome"])}</a><small>{h(STATI[s]["righe"][0][0])}</small></div><div class="quando">{giorno(d)}{conto(d)}</div></li>' for d, s in prossime)
    senza = [s for s in ORDINE_STATI if not prima_data(s)]
    corpo += (f'<h2 id="deadlines">State FAFSA deadlines for {ANNO}</h2><div class="testo"><p>The first date on the official form for the states people search for most.{rim.ref("fafsa_2728")} '
              + "".join(f'<a href="/{slug_stato(s)}">{h(VOCI[s]["nome"])}</a> has no closing date: the form says to apply as soon as possible after {giorno(FAFSA["apertura"])}. ' for s in senza)
              + f'</p></div><ul class="date-l">{righe}</ul><p class="azioni"><a class="btn sec" href="/{P_SCAD}">All {len(FAFSA["voci"])} states and territories{ico("arrow")}</a></p>')
    corpo += (f'<h2 id="new">What changed for federal loans on July 1, 2026</h2><div class="testo">'
              + rim.t(f'<ul><li>Graduate students can borrow {usd(LIM["laureato"]["anno"])} a year and {usd(LIM["laureato"]["totale"])} in total; professional students {usd(LIM["professionale"]["anno"])} and {usd(LIM["professionale"]["totale"])}. New Grad PLUS loans ended.[[fr_regola,legge]]</li>'
                      f'<li>Parents can borrow {usd(gen["anno"])} a year and {usd(gen["totale"])} in total for each dependent student, instead of up to the full cost of attendance.[[fr_regola]]</li>'
                      f'<li>New borrowers choose between two repayment plans: a standard plan of {STD["fasce"][0]["anni"]} to {STD["fasce"][-1]["anni"]} years and the Repayment Assistance Plan.[[legge]]</li>'
                      f'<li>Undergraduate limits did not change, and students who were already enrolled and borrowing keep the old limits for up to {LIM["anni_eccezione"]} academic years.[[fr_regola,legge]]</li></ul></div>')
              + rim.cit("fr_regola", "sintesi"))
    faq_html, faq_ld = faq_blocco([
        ("when is fafsa due", f"When is the FAFSA due for {ANNO}?",
         f"For federal aid the {ANNO} form must be received by {giorno(FAFSA['chiusura_federale'])}. State and college aid usually have earlier dates: {con_data} of the {len(FAFSA['voci'])} states and territories on the official form list at least one.", "fafsa_2728"),
        ("when does fafsa open", f"When did the {ANNO} FAFSA open?",
         f"On {giorno(FAFSA['apertura'])}: the form says to submit it as early as possible, but no earlier than that date.", "fafsa_2728"),
        ("direct unsubsidized loan", "What does a Direct Unsubsidized Loan cost in 2026–27?",
         f"The fixed rate for loans first disbursed from {giorno(TASSI['dal'])} to June 30, {TASSI['al'][:4]} is {T_UG}% for undergraduates and {T_GRAD}% for graduate and professional students. Graduate students can borrow up to {usd(LIM['laureato']['anno'])} a year.", "fr_tassi,fr_regola"),
    ], rim)
    corpo += faq_html + rim.elenco()
    testata = banda("Official dates and numbers · independent site", "College aid deadlines and federal student loan numbers, from the official documents",
                    f"FAFSA deadlines for {ANNO} in every state, federal loan interest rates and limits for {ANNO_TASSI}, and payment calculators built on the formulas in the law. Sources read on {data_lunga(CONTROLLO)}.", icona="cap")
    ld = [faq_ld, {"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/", "inLanguage": "en-US"}]
    pagina("", f"FAFSA Deadlines {ANNO}, Federal Student Loan Rates and Limits",
           f"FAFSA deadlines for {ANNO} by state, federal student loan interest rates ({T_UG}% for {ANNO_TASSI}), new loan limits and payment calculators, from official sources.",
           corpo, testata, jsonld=ld)


# ---------------------------------------------------------------- pagine di servizio
MODULO = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card" data-correzioni>
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or figure<input type="text" name="page" required maxlength="300" placeholder="For example /fafsa-deadlines/ohio/, the state date"></label>
<label>What is wrong?<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<p class="small">Please do not include your name, email address, income, loan details or other personal information: the form does not ask for them and we do not reply to messages.</p>
<p class="errore" data-errore hidden>The message was not sent. Please try again.</p>
<button type="submit" class="btn">Send correction</button>
</form>
<p class="ok" data-ok hidden><strong>Thank you.</strong> We will check it against the official source.</p>"""

USO_FONTE = {"fafsa_2728": ("PDF form", "Federal and state FAFSA deadlines"), "fr_tassi": ("Federal Register notice (text)", "Interest rates for 2026–27 and every year since 2006"),
             "fr_regola": ("Federal Register final rule (text)", "Loan limits in the regulations from July 1, 2026"), "legge": ("Public law (text)", "Loan limits, standard plan periods, Repayment Assistance Plan formula"),
             "manuale": ("Web page of the official handbook", "Undergraduate annual and aggregate loan limits"),
             "cfr_200": ("Code of Federal Regulations (PDF)", "Credit requirement for Parent PLUS loans"), "cfr_202": ("Code of Federal Regulations (PDF)", "Loan fee deducted from each disbursement"),
             "scorecard": ("Data file (CSV in a ZIP archive)", "College pages: tuition, cost of attendance, net price, admission and graduation rates, median debt"),
             "scorecard_diz": ("Spreadsheet (data dictionary)", "The year each College Scorecard figure refers to, and what each column means")}


def come_controlliamo():
    rim = Rimandi()
    n_frasi = sum(len(f["frasi"]) for f in FONTI.values())
    corpo = ('<div class="testo pull card"><p>A wrong deadline or a wrong rate costs real money. So this site publishes only what an official document says, keeps a copy of every document, '
             'and stops building its pages if a figure can no longer be found where it was.</p></div>')
    righe = []
    for fid, f in FONTI.items():
        forma, uso = USO_FONTE[fid]
        righe.append(f'<tr><th scope="row"><a href="{h(f.get("pagina") or f["url"])}" rel="noopener">{h(f["titolo"])}</a>{rim.ref(fid)}<br><span class="small">{h(f["chi"])}</span></th><td>{h(forma)}</td><td>{h(uso)}</td><td>{giorno(f["letto_il"])}</td></tr>')
    corpo += (f'<h2 id="sources">The {len(FONTI)} official sources</h2><p class="small scorri">Swipe the table sideways to see every column.</p>'
              + tabella("Every figure on the site comes from one of these documents.", [("Document", 0), ("Form", 0), ("Used for", 0), ("Read on", 0)], righe, "ampia"))
    corpo += '<h2>How the figures get from the document to the page</h2><div class="testo"><ul>'
    corpo += rim.t('<li>We download each document with a program that identifies itself as a robot, and record its address, the date and a fingerprint (SHA-256) of the file.</li>'
                   f'<li><strong>FAFSA deadlines.</strong> The text for each of the {len(FAFSA["voci"])} states and territories is read from page 2 of the form twice, with two different text extractions, and the two readings must agree. '
                   'The dates shown next to each entry are the dates written in that text, nothing else.[[fafsa_2728]]</li>'
                   '<li><strong>Interest rates.</strong> A program reads the tables of the notice. The build stops unless the Treasury yield plus the add-on equals the published rate on every line, and the 2026–27 line of the history table matches the first table.[[fr_tassi]]</li>'
                   '<li><strong>Loan limits.</strong> Each new limit is read from the final rule and from the law, and the two must give the same number. The undergraduate limits come from the official handbook and must match the totals the final rule repeats.[[fr_regola,legge,manuale]]</li>'
                   f'<li><strong>College costs.</strong> The figures on the <a href="/college-costs/">college pages</a> are copied, cell by cell, from the College Scorecard file the Department of Education updated on {data_lunga(SC_AGG)} '
                   f'({SC["fonti"]["scorecard"]["istituti"]:,} institutions). The file itself does not say which year a column refers to: we take the year from the Department’s data dictionary. '
                   'A value the file marks as not available or privacy-suppressed is shown as missing, never estimated.[[scorecard,scorecard_diz]]</li>'
                   '<li><strong>Repayment formulas.</strong> The income bands, the $50 per dependent, the $10 minimum and the repayment periods are read from the text of the law; the bands must be consecutive.[[legge]]</li>'
                   f'<li>Every sentence in a quotation box is copied word for word and searched for in the downloaded file each time ({n_frasi} sentences). If one is no longer there, the build stops.</li>'
                   '<li>A second program, written separately with the key figures typed in by hand from the documents, compares every number on every page and re-runs the calculators with its own arithmetic.</li></ul></div>')
    corpo += ('<h2>What is ours and what is official</h2><div class="testo"><ul>'
              '<li><strong>Official:</strong> dates, rates, dollar limits, income bands, repayment periods and every quoted sentence.</li>'
              '<li><strong>Ours:</strong> monthly payments, total interest, sums of yearly limits and the “gap” figures. They are arithmetic on the official numbers and are labelled “our calculation”. '
              'The payment formula counts interest by the month; loan servicers count it by the day, so their figures differ slightly.</li>'
              '<li><strong>Yours:</strong> the college cost you type into the gap calculator. On the college pages the cost is the net price from the federal file, held flat for four years: an assumption, stated on each page.</li></ul></div>')
    corpo += ('<h2>What we do not do</h2><div class="testo"><ul>'
              '<li>We do not give financial advice, recommend lenders or tell anyone how much to borrow.</li>'
              '<li>We do not use figures from other websites, lenders or news articles.</li>'
              '<li>We do not cover private student loans, loan forgiveness programs, the exact loan fee of each year, or the deadlines of individual colleges. College prices come only from the federal file, which runs about a year behind the colleges’ own websites.</li>'
              '<li>Some official web pages cannot be read by our checking program (they need a browser, or refuse automated visits). We do not try to get round that: we use the official PDF or legal text instead, and say which document we read.</li>'
              '<li>The 2026–27 volume of the official handbook on loan limits was not published when we read the sources, so the undergraduate table comes from the 2025–26 volume, together with the 2026 final rule stating that those limits did not change.</li></ul></div>')
    corpo += ('<h2>When we update</h2><div class="testo"><p>The FAFSA form is published once a year; states sometimes change a date afterwards, and the form is then reissued. Interest rates are announced once a year, after the May Treasury auction. '
              'Loan limits and repayment formulas change only when the law or the regulations do. A page changes only when the new official document has been read and all the checks pass again; the reading date is always shown.</p></div>')
    corpo += ('<h2 id="corrections">Report an error</h2><div class="testo"><p>Seen a date or a figure that does not match the official document? Tell us which page and, if you can, link the source: we check it and fix the page.</p></div>' + MODULO)
    corpo += rim.elenco()
    testata = banda("How we check", "How we check every figure, and the sources", "Official documents kept on record, numbers that must agree between the rule and the law, and a source next to every figure.", corta=True, icona="shield")
    pagina("how-we-check/", "How We Check FAFSA Deadlines and Loan Figures, and Our Sources",
           f"How {NOME} copies FAFSA deadlines, federal loan rates and limits from official documents, checks them and labels its own calculations.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")])


def about():
    aff = ('<p>The payment calculator page may also carry clearly marked affiliate links to lenders; if you take a loan through one we may earn a commission. They never change the figures.</p>' if PARTNER else "")
    pub = ('<p>The site shows advertising served by Google AdSense. Advertisers never decide what we publish.</p>' if MON.adsense_attivo(SITO_ID)
           else '<p>The site currently shows no advertising.</p>')
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{NOME}</strong> is an independent publication, part of a small network of websites that turn official data into plain reference pages. '
             'It shows FAFSA deadlines by state, federal student loan interest rates and limits, and the official repayment formulas, each copied from the document it comes from.</p>'
             '<p>We are <strong>not affiliated with</strong> the U.S. Department of Education, Federal Student Aid, any state agency, college, loan servicer or lender. '
             'The site gives general information, not financial, tax or legal advice.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Dates, rates, limits and formulas printed in official documents, each linked to its source and quoted word for word where it matters.</li>'
             '<li>Calculations made from those figures, always labelled as ours.</li>'
             '<li>Where an official source does not say something, we say so instead of filling the gap.</li></ul>'
             f'<h2>How the site is paid for</h2><div class="testo">{pub}{aff}</div>'
             '<h2>Corrections</h2><div class="testo"><p>If a figure does not match the official document, use the <a href="/how-we-check/#corrections">corrections form</a>. For questions about your own aid or loans, '
             'ask the financial aid office of your college or your loan servicer: they have your records.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, what it publishes and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", f"About {NOME}: an independent site that copies FAFSA deadlines and federal student loan figures from official documents.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")])


def privacy():
    con_aff = bool(PARTNER)
    cookie = MON.privacy_cookie("en", SITO_ID, con_aff) or ("<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. This site shows no advertising.</p>")
    california = MON.frase_california(SITO_ID) or "California residents: we do not sell or share personal information."
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {NOME} ({URL_SITO.replace("https://", "")}) collects. In short: very little.</p></div>'
             '<div class="testo"><h2>The calculators</h2><p>The calculators run in your browser. The income, loan balance, cost and other numbers you type are not sent to us, not stored and not shared with anyone. '
             'They disappear when you close or reload the page.</p>'
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
    pagina("privacy/", f"Privacy | {NOME}", f"Privacy at {NOME}: calculators that run in your browser, a cookie-free visit counter, and Google AdSense advertising with consent.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    griglia = "".join(f'<li><a href="/{u}"><b>{h(t)}</b></a></li>' for u, t in MENU)
    corpo = f'<div class="pull card"><p>The page you asked for does not exist. Go to the <a href="/">home page</a> or pick a section below.</p></div><ul class="griglia larga" style="margin-top:18px">{griglia}</ul>'
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
  # Pubblica solo se è cambiato qualcosa in collegeaid/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = collegeaid/sito, Build command vuoto, Publish directory = "."
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
        if fid == "scorecard":
            # lo zip ufficiale (24 MB) sta in cache/ e può non esserci: fa fede l'estratto, con la sua impronta registrata insieme a quella dello zip
            if hashlib.sha256((RADICE / f["estratto"]).read_bytes()).hexdigest() != f["estratto_sha256"] or (grezzo.exists() and hashlib.sha256(grezzo.read_bytes()).hexdigest() != f["sha256"]):
                raise SystemExit("fonte scorecard: l'estratto o lo zip non hanno più l'impronta registrata (rilanciare raccolta/scorecard.py)")
            continue
        if f.get("impronta") == "frasi":
            # Pagina HTML dinamica: i byte cambiano a ogni scarico, quindi fa fede l'impronta delle frasi citate, ritrovate nel file.
            if TESTO.impronta_frasi(TESTO.testo_norm(grezzo), f["frasi"]) != f["sha256_frasi"]:
                raise SystemExit(f"fonte {fid}: le frasi citate non sono più nel file grezzo come registrate (rilanciare raccolta/fonti.py)")
        elif hashlib.sha256(grezzo.read_bytes()).hexdigest() != f["sha256"]:
            raise SystemExit(f"fonte {fid}: il file grezzo non ha più l'impronta registrata (rilanciare raccolta/fonti.py)")
    if set(FONTI) != set(USO_FONTE):
        raise SystemExit("fonti.json: fonti diverse da quelle descritte in USO_FONTE")
    controlla_stati()
    if [r["chiave"] for r in TASSI["righe"]] != ["ug", "grad", "plus"]:
        raise SystemExit("aiuti.json: righe dei tassi in un ordine diverso")
    eta = (date.today() - CONTROLLO).days
    if eta > 45:
        print(f"ATTENZIONE: le fonti sono state lette {eta} giorni fa. Rilanciare raccolta/fonti.py (il modulo FAFSA viene ristampato quando uno Stato cambia data).")


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
    indice_scadenze()
    for s in ORDINE_STATI:
        pagina_stato(s)
    pagina_tassi()
    pagina_limiti()
    pagina_rata()
    pagina_rap()
    pagina_plus()
    uni = prepara_universita()
    indice_universita(uni)
    for u in uni:
        pagina_universita(u, uni)
    come_controlliamo()
    about()
    privacy()
    pagina_404()
    extra()
    print(f"Schede delle università: {len(uni)} + indice (file Scorecard aggiornato il {SC_AGG.isoformat()}).")
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404. Partner accesi: {', '.join(p['id'] for p in PARTNER) or 'nessuno (riquadro spento)'}.")


if __name__ == "__main__":
    main()
