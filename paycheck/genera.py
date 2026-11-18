"""Genera il sito statico "US Paycheck Calculator" (USA, inglese) in paycheck/sito/.

Uso (dalla radice del repository):
    python3 paycheck/raccolta/fonti.py       # scarica le fonti ufficiali, controlla le frasi, scrive dati/fonti.json e dati/regole.json
    python3 paycheck/raccolta/domanda.py <cartella con le risposte seodata>   # dati/domanda.json (solo quando si misurano ricerche nuove)
    python3 paycheck/genera.py               # pagine in paycheck/sito/
    python3 paycheck/verifica.py [--browser] # controlli

Prova su 5 Stati (Texas, Florida, California, Illinois, North Carolina): calcolatore della busta paga netta (IRS Pub. 15-T,
Worksheet 1A; FICA; ritenuta statale con la formula ufficiale) e imposte del datore di lavoro (FICA, FUTA, disoccupazione statale).
Ogni cifra viene da dati/regole.json, che raccolta/fonti.py ricava dai file ufficiali in dati/grezzi/. Le frasi tra virgolette
sono copiate alla lettera dalle fonti (dati/fonti.json). Le FAQ nascono da ricerche misurate (dati/domanda.json).
Riquadro dei partner (Gusto, ADP, Patriot): ogni partner è spento finché dati/affiliati.json non ha il suo link tracciato e "attivo": true.
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
import motore  # noqa: E402
import stile  # noqa: E402
sys.path.insert(0, str(RADICE / "raccolta"))
import testo as TESTO  # noqa: E402

URL_SITO = "https://us-paycheck-calculator.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
NOME = "US Paycheck Calculator"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "paycheck"  # nome del sito in monetizzazione.json
ADSENSE_HEAD = MON.script_adsense(SITO_ID)


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


G = carica("regole.json")
FONTI = carica("fonti.json")["fonti"]
DOM = carica("domanda.json")
AFF = carica("affiliati.json")
FONTI_PARTNER = {"patriot", "gusto", "adp", "adp_accordo"}   # pagine dei programmi di affiliazione: non contano tra le fonti ufficiali
R = motore.dati_js(G)
ANNO = G["anno"]
CONTROLLO = date.fromisoformat(G["letto_il"])
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
STATI = ["TX", "FL", "CA", "IL", "NC"]          # ordine delle pagine
PERIODI = [("weekly", "Weekly (52/year)"), ("biweekly", "Every 2 weeks (26/year)"), ("semimonthly", "Twice a month (24/year)"), ("monthly", "Monthly (12/year)")]
STIPENDI = [30000, 50000, 75000, 100000, 150000]  # esempi delle pagine di Stato (dollari l'anno)
PREDEFINITI = {"CA": {"ca_fs": "single", "ca_reg": 0, "ca_est": 0}, "IL": {"il1": 1, "il2": 0}, "NC": {"nc_fs": "single", "nc_all": 0}, "TX": {}, "FL": {}}


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def usd(cent):
    return ("−" if cent < 0 else "") + f"${abs(cent) // 100:,}.{abs(cent) % 100:02d}"


def usd0(dollari):
    return f"${dollari:,.0f}"


def pct(x, cifre=3):
    """0.062 -> '6.2%'"""
    return f"{x * 100:.{cifre}f}".rstrip("0").rstrip(".") + "%"


def nome_stato(s):
    return G["stati"][s]["nome"]


def slug(s):
    return G["stati"][s]["slug"]


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

    def elenco(self, nota=None):
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = FONTI[i]
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. '
                        f'<span class="small">read {data_lunga(date.fromisoformat(f["letto_il"]))}</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2><ol>{"".join(voci)}</ol>'
                + (nota or '<p class="small">Rates, thresholds and tables are copied from the official documents above; the dollar results are our arithmetic on those figures. '
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


def ico(nome, cls="ico"):
    if nome not in stile.ICONE:
        raise SystemExit(f"icona sconosciuta: {nome}")
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
TITOLI, DESCRIZIONI = {}, {}
MENU = [("", "Calculator")] + [(f"{slug(s)}/", "N. Carolina" if s == "NC" else nome_stato(s)) for s in STATI] + [("employer-payroll-taxes/", "Employer taxes"), ("federal-withholding/", "Federal")]
DISCLAIMER = ("<strong>Independent site, not affiliated with the IRS or with any state agency.</strong> "
              f"The results are estimates, not tax, legal or payroll advice. They follow the official {ANNO} withholding formulas, but your real paycheck can differ: "
              "pre-tax benefits, local taxes, other deductions and your employer’s rounding are not included. "
              "Check your pay stub and Form W-4, and ask your employer or a tax professional before making decisions.")


def menu_html(percorso, mobile=False):
    return "".join(f'<a href="/{u}"' + (' aria-current="page"' if u == percorso else "") + (' class="w2"' if mobile else "") + f">{h(t)}</a>" for u, t in MENU)


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None, script_dati=""):
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
    f_stati = "".join(f'<li><a href="/{slug(s)}/">{h(nome_stato(s))} paycheck calculator</a></li>' for s in STATI)
    f_paghe = "".join(f'<li><a href="/{slug(s)}-payroll-taxes/">{h(nome_stato(s))} payroll taxes</a></li>' for s in STATI)
    guide = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [("", "Paycheck calculator"), ("employer-payroll-taxes/", "Employer payroll taxes"), ("how-to-do-payroll/", "How to do payroll"), ("federal-withholding/", "Federal withholding tables"),
                    ("how-we-check/", "How we check"), ("about/", "About"), ("how-we-check/#corrections", "Report an error"), ("privacy/", "Privacy")])
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
<meta name="theme-color" content="#0E2A22">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>US Paycheck <b>Calculator</b></span></a>
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
<a class="logo" href="/">{LOGO}<span>US Paycheck <b>Calculator</b></span></a>
<p><strong>{NOME}</strong> estimates take-home pay and employer payroll taxes for {ANNO} from the official withholding formulas: IRS Publication 15-T for federal income tax,
Publication 15 for Social Security, Medicare and FUTA, and each state’s own withholding and unemployment tax documents. Independent site, not a government website.</p>
<p>Official sources read on {data_lunga(CONTROLLO)}.</p>
</div><div>
<h2>States</h2><ul>{f_stati}</ul>
</div><div>
<h2>Employers</h2><ul>{f_paghe}</ul>
</div><div>
<h2>Guides</h2><ul>{guide}</ul>
</div></div>
<p class="f-base">Estimates for general information only, not tax, legal or payroll advice. Not affiliated with the Internal Revenue Service, the Social Security Administration, the Department of Labor or any state agency.</p>
</div></footer>
{script_dati}<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, corta=False, icona="cash"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>
</div></section>"""


def script_dati():
    return f'<script type="application/json" id="dati-regole">{json.dumps(R, separators=(",", ":"))}</script>\n'


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


# ---------------------------------------------------------------- calcolatori
def caso(stato, lordo, periodo="biweekly", **extra):
    i = {"stato": stato, "periodo": periodo, "lordo": lordo, "fs": "single", "step2": False, "ytd": 0, "step3": 0, "a4": 0, "b4": 0, "c4": 0}
    i.update(PREDEFINITI[stato])
    i.update(extra)
    return i


def calcolatore(stato="TX", importo=2000, titolo=None):
    titolo = titolo or f"Paycheck calculator, {ANNO}"
    op_s = "".join(f'<option value="{s}"{" selected" if s == stato else ""}>{h(nome_stato(s))}</option>' for s in STATI)
    op_p = "".join(f'<option value="{k}"{" selected" if k == "biweekly" else ""}>{h(t)}</option>' for k, t in PERIODI)
    r = motore.busta(R, caso(stato, importo * 100))
    statico = (f'<div class="netto-box"><span>Estimated take-home pay, biweekly</span><b>{usd(r["netto"])}</b><em>{usd(r["totale"])} withheld from {usd(r["lordo"])} gross</em></div>'
               '<p>Turn on JavaScript to change the figures and see every line.</p>')
    d = PREDEFINITI
    return f"""<section class="card calc" data-busta aria-labelledby="calc-h">
<div class="calc-h"><h2 id="calc-h">{ico("calc")}{h(titolo)}</h2></div>
<div class="calc-g">
<form class="calc-in" onsubmit="return false" autocomplete="off">
<div class="due"><label>State<select name="stato">{op_s}</select></label>
<label>Pay frequency<select name="periodo">{op_p}</select></label></div>
<div class="due"><label>I want to enter<select name="tipo"><option value="periodo" selected>Pay per pay period</option><option value="anno">Yearly salary</option><option value="ora">Hourly rate</option></select></label>
<label><span data-lab-importo>Gross pay this pay period ($)</span><input type="text" inputmode="decimal" name="importo" value="{importo:,}" maxlength="14"></label></div>
<label data-tipo="ora" hidden>Hours in the pay period<input type="text" inputmode="decimal" name="ore" value="80" maxlength="6"><small>For example 40 for a week, 80 for two weeks. Overtime pay is not worked out for you: add it to the hours at its own rate, or enter the total pay instead.</small></label>
<hr>
<fieldset><legend>Federal Form W-4</legend>
<label>Step 1(c): filing status<select name="fs"><option value="single" selected>Single or Married filing separately</option><option value="mfj">Married filing jointly</option><option value="hoh">Head of household</option></select></label>
<label class="check"><input type="checkbox" name="step2"><span>Step 2: the box for two jobs (or a working spouse) is checked</span></label>
<details><summary>Steps 3 and 4, and pay earlier this year</summary><div>
<label>Step 3: credits for dependents, per year ($)<input type="text" inputmode="decimal" name="step3" value="0" maxlength="12"></label>
<label>Step 4(a): other income, per year ($)<input type="text" inputmode="decimal" name="a4" value="0" maxlength="12"></label>
<label>Step 4(b): deductions, per year ($)<input type="text" inputmode="decimal" name="b4" value="0" maxlength="12"></label>
<label>Step 4(c): extra withholding, per pay period ($)<input type="text" inputmode="decimal" name="c4" value="0" maxlength="12"></label>
<label>Gross pay already received this year, before this paycheck ($)<input type="text" inputmode="decimal" name="ytd" value="0" maxlength="14"><small>Only matters near the Social Security wage base ({usd0(G["fica"]["ss_base"])}) and the {usd0(G["fica"]["addl_soglia"])} Additional Medicare Tax threshold.</small></label>
</div></details>
</fieldset>
<fieldset data-solo="TX FL"{"" if stato in ("TX", "FL") else " hidden"}><legend>State</legend><p class="small" style="margin:0">Texas and Florida do not withhold state income tax from wages, so there is nothing to enter.</p></fieldset>
<fieldset data-solo="CA"{"" if stato == "CA" else " hidden"}><legend>California Form DE 4</legend>
<label>Filing status<select name="ca_fs"><option value="single" selected>Single, or married with two incomes</option><option value="married">Married (one income)</option><option value="hoh">Head of household</option></select></label>
<div class="due"><label>Regular allowances (line 1)<input type="text" inputmode="numeric" name="ca_reg" value="{d["CA"]["ca_reg"]}" maxlength="3"></label>
<label>Allowances for estimated deductions (line 2)<input type="text" inputmode="numeric" name="ca_est" value="{d["CA"]["ca_est"]}" maxlength="3"></label></div></fieldset>
<fieldset data-solo="IL"{"" if stato == "IL" else " hidden"}><legend>Illinois Form IL-W-4</legend>
<div class="due"><label>Line 1 allowances<input type="text" inputmode="numeric" name="il1" value="{d["IL"]["il1"]}" maxlength="3"></label>
<label>Line 2 allowances<input type="text" inputmode="numeric" name="il2" value="{d["IL"]["il2"]}" maxlength="3"></label></div></fieldset>
<fieldset data-solo="NC"{"" if stato == "NC" else " hidden"}><legend>North Carolina Form NC-4</legend>
<div class="due"><label>Filing status<select name="nc_fs"><option value="single" selected>Single, married or surviving spouse</option><option value="hoh">Head of household</option></select></label>
<label>Allowances<input type="text" inputmode="numeric" name="nc_all" value="{d["NC"]["nc_all"]}" maxlength="3"></label></div></fieldset>
</form>
<div class="calc-out" data-out aria-live="polite">{statico}</div>
</div>
<p class="calc-f">Estimate for {ANNO} from IRS Publication 15-T (Worksheet 1A, for a Form W-4 from 2020 or later), Publication 15 and the state’s own withholding formula. Pre-tax benefits such as 401(k) or health insurance, local taxes and other deductions are not included. Not tax advice. The calculator runs in your browser.</p>
</section>"""


def calcolatore_datore(stato="TX", salario=50000):
    op_s = "".join(f'<option value="{s}"{" selected" if s == stato else ""}>{h(nome_stato(s))}</option>' for s in STATI)
    r = motore.datore(R, stato, salario * 100)
    statico = (f'<div class="netto-box"><span>Estimated employer payroll taxes for the year</span><b>{usd(r["totale"])}</b><em>Wages plus taxes: {usd(r["costo"])}</em></div>'
               '<p>Turn on JavaScript to change the figures and see every line.</p>')
    return f"""<section class="card calc" data-datore aria-labelledby="dat-h">
<div class="calc-h"><h2 id="dat-h">{ico("build")}Employer payroll tax calculator, {ANNO}</h2></div>
<div class="calc-g">
<form class="calc-in" onsubmit="return false" autocomplete="off">
<label>State<select name="stato">{op_s}</select></label>
<label>Wages paid to one employee in the year ($)<input type="text" inputmode="decimal" name="salario" value="{salario:,}" maxlength="14"></label>
<label>Your state unemployment tax rate (%)<input type="text" inputmode="decimal" name="aliquota" value="{pct(G["stati"][stato]["suta"]["nuovo"]).rstrip("%")}" maxlength="6"><small>Filled in with the {ANNO} rate for new employers. Use the rate on your own notice if you have one.</small></label>
</form>
<div class="calc-out" data-out aria-live="polite">{statico}</div>
</div>
<p class="calc-f">Employer share of Social Security and Medicare, FUTA after the state credit and state unemployment tax for one employee, {ANNO}. Workers’ compensation insurance, benefits and local taxes are not included. Estimate, not tax advice.</p>
</section>"""


def partner_attivi():
    """Partner accesi in dati/affiliati.json, già controllati: link vero, dominio ammesso, descrizione ancora nella pagina del partner."""
    attivi, visti = [], set()
    for p in AFF["partner"]:
        if p["id"] in visti or not re.fullmatch(r"[a-z0-9_]+", p["id"]):
            raise SystemExit(f"affiliati.json: id doppio o non valido ({p['id']})")
        visti.add(p["id"])
        if not p["attivo"]:
            continue
        link = p["link"]
        if not link.startswith("https://") or "DA-INSERIRE" in link or ".invalid" in link or " " in link:
            raise SystemExit(f"affiliati.json: {p['id']} è attivo ma il link tracciato non è stato inserito")
        if not MON.dominio_ammesso(link):
            raise SystemExit(f"affiliati.json: il dominio del link di {p['id']} non è in monetizzazione.json (domini_affiliazione)")
        if not FONTI[p["fonte"]]["trovate"][p["frase"]]:
            raise SystemExit(f"la descrizione di {p['nome']} non è più nella sua pagina: riscrivere il testo in affiliati.json")
        attivi.append(p)
    return attivi


PARTNER = partner_attivi()


def riquadro_partner():
    """Riquadro di affiliazione per i datori di lavoro: scritto in pagina solo se almeno un partner è acceso.

    Va sempre SOTTO il calcolatore del datore (mai sopra la risposta); i link hanno rel="sponsored nofollow noopener"."""
    if not PARTNER:
        return ""
    q = AFF["riquadro"]
    voci = "".join(f'<li data-partner="{h(p["id"])}"><b>{h(p["nome"])}</b><p>{h(p["testo"])}</p>'
                   f'<a class="btn sec" href="{h(p["link"])}" rel="sponsored nofollow noopener" target="_blank">{h(p["pulsante"])}</a></li>' for p in PARTNER)
    return (f'<aside class="partner" data-partner-box aria-labelledby="partner-h"><p class="tag">{h(q["etichetta"])}</p><h3 id="partner-h">{h(q["titolo"])}</h3>'
            f'<p>{h(q["testo"])}</p><ul class="partner-l">{voci}</ul>'
            f'<p class="small">{h(q["trasparenza"])}</p></aside>')


# ---------------------------------------------------------------- pezzi comuni
def griglia_stati(escludi=None):
    voci = []
    for s in STATI:
        if s == escludi:
            continue
        st = G["stati"][s]
        if st["imposta_reddito"] is None:
            sotto = "No state income tax"
        elif s == "CA":
            sotto = f"Method B + SDI {pct(st['sdi']['aliquota'])}"
        elif s == "IL":
            sotto = f"Flat {pct(st['imposta_reddito']['aliquota'])}"
        else:
            sotto = f"Withholding {pct(st['imposta_reddito']['aliquota_ritenuta'])}"
        voci.append(f'<li><a href="/{slug(s)}/"><b>{h(st["nome"])}</b><small>{h(sotto)}</small></a></li>')
    return f'<ul class="griglia stati">{"".join(voci)}</ul>'


def tabella_fed(lato, stato_civile, nome):
    righe = ""
    for r in G["federale"]["tabelle"][lato][stato_civile]:
        righe += (f'<tr><td class="n">{usd0(r["da"])}</td><td class="n">{usd0(r["fino"]) if r["fino"] is not None else "–"}</td>'
                  f'<td class="n">{usd(motore.c(r["base"]))}</td><td class="n">{r["pct"]}%</td><td class="n">{usd0(r["da"])}</td></tr>')
    return (f'<div class="tab"><table class="dati" data-fed="{lato}-{stato_civile}"><caption><span>{h(nome)}</span></caption><thead><tr><th class="n">At least (A)</th><th class="n">But less than (B)</th>'
            f'<th class="n">Tentative amount (C)</th><th class="n">Plus (D)</th><th class="n">Of the amount over (E)</th></tr></thead><tbody>{righe}</tbody></table></div>')


def passi_federali(i):
    """Worksheet 1A scritto riga per riga per un caso (testo delle pagine)."""
    f = motore.federale(R, i)
    P = R["P"][i["periodo"]]
    g1 = 0 if i["step2"] else (R["g1"]["mfj"] if i["fs"] == "mfj" else R["g1"]["altro"])
    anno = f["base"] + motore.mezzo((f["adj"] - f["da"]) * f["pct"], 100)
    return ('<ul class="passi">'
            f'<li>1c. {usd(i["lordo"])} × {P} pay periods = <b>{usd(i["lordo"] * P)}</b></li>'
            f'<li>1g–1i. Subtract {usd(g1)}: adjusted annual wage <b>{usd(f["adj"])}</b></li>'
            f'<li>2b–2g. {usd(f["base"])} + {f["pct"]}% of the amount over {usd(f["da"])} = <b>{usd(anno)}</b> a year</li>'
            f'<li>2h. {usd(anno)} ÷ {P} = <b>{usd(f["tentativo"])}</b> per paycheck</li></ul>'), f


def tabella_esempi(s):
    righe = ""
    st = G["stati"][s]
    for sal in STIPENDI:
        lordo = motore.mezzo(sal * 100, 26)
        r = motore.busta(R, caso(s, lordo))
        righe += (f'<tr data-stipendio="{sal}"><th scope="row">{usd0(sal)}</th><td class="n">{usd(lordo)}</td><td class="n">{usd(r["fed"])}</td>'
                  f'<td class="n">{usd(r["ss"] + r["medicare"])}</td>'
                  + (f'<td class="n">{usd(r["stato"])}</td>' if st["imposta_reddito"] else "")
                  + (f'<td class="n">{usd(r["sdi"])}</td>' if st.get("sdi") else "")
                  + f'<td class="n"><strong>{usd(r["netto"])}</strong></td></tr>')
    ipotesi = {"CA": "California: single, no allowances on Form DE 4.", "IL": "Illinois: one allowance on Line 1 of Form IL-W-4.", "NC": "North Carolina: single, no allowances on Form NC-4.",
               "TX": "Texas has no state income tax on wages.", "FL": "Florida has no state income tax on wages."}[s]
    return (f'<div class="tab"><table class="dati" data-esempi="{s}"><caption><span>Paid every two weeks, federal filing status Single, no other W-4 entries, no pre-tax deductions. {ipotesi}</span></caption>'
            '<thead><tr><th>Yearly salary</th><th class="n">Gross pay</th><th class="n">Federal tax</th><th class="n">Social Security + Medicare</th>'
            + ('<th class="n">State tax</th>' if st["imposta_reddito"] else "") + ('<th class="n">SDI</th>' if st.get("sdi") else "")
            + '<th class="n">Take-home</th></tr></thead><tbody>' + righe + '</tbody></table></div>')


NON_INCLUSO = ('<h2 id="not-included">What the estimate leaves out</h2><ul class="testo">'
               '<li><strong>Pre-tax benefits</strong>: 401(k) contributions, health insurance premiums, HSA and FSA amounts lower your taxable wages. Enter your pay after those amounts for a closer federal figure; Social Security and Medicare will then be slightly understated for a 401(k).</li>'
               '<li><strong>Local taxes</strong> and any deduction that is not a tax (garnishments, union dues, loan repayments).</li>'
               '<li><strong>Bonuses and other supplemental pay</strong>, which employers may tax with a separate flat-rate method.</li>'
               '<li><strong>Forms W-4 from 2019 or earlier</strong> (with allowances), employees who claim to be exempt, and nonresident aliens, who have their own rules in Publication 15-T.</li>'
               '<li><strong>Extra state withholding</strong> you asked for on the state form (an additional amount on Form DE 4, IL-W-4 or NC-4): add it to the state line yourself.</li>'
               '<li><strong>The deductions for tips and overtime</strong> claimed on the tax return.</li>'
               '<li><strong>Rounding</strong>: we keep cents. The IRS lets employers round withholding to whole dollars, so a real pay stub can differ by up to 50 cents per line.</li></ul>')


# ---------------------------------------------------------------- home
def es_base(stato="TX"):
    return motore.busta(R, caso(stato, 200000))


def home():
    rim = Rimandi()
    F, FU = G["fica"], G["futa"]
    r = es_base()
    corpo = '<div class="pull">' + calcolatore("TX") + '</div>'
    corpo += f'<h2>Pick your state</h2><p class="small">This is a five-state pilot. Each state page has the same calculator, the state’s official withholding formula and what an employer pays there.</p>{griglia_stati()}'
    corpo += ('<div class="stats card" style="margin-top:26px">'
              f'<div class="stat main"><b>{pct(F["ss"])}</b><span>Social Security, up to {usd0(F["ss_base"])} of wages in {ANNO}</span></div>'
              f'<div class="stat"><b>{pct(F["medicare"])}</b><span>Medicare, on all wages</span></div>'
              f'<div class="stat"><b>{pct(F["addl"])}</b><span>Additional Medicare Tax above {usd0(F["addl_soglia"])} in the year</span></div>'
              f'<div class="stat"><b>{usd0(G["federale"]["riga_1g"]["altro"])}</b><span>Subtracted from yearly wages before the federal tables ({usd0(G["federale"]["riga_1g"]["mfj"])} if married filing jointly)</span></div>'
              f'<p class="asof">Figures from IRS Publications 15 and 15-T for {ANNO}, read on {data_lunga(CONTROLLO)}.</p></div>')
    passi, f = passi_federali(caso("TX", 200000))
    corpo += '<h2 id="how">How the estimate is calculated</h2><div class="testo">'
    corpo += rim.t(f'<p>Your take-home pay is your gross pay minus four things: federal income tax, Social Security, Medicare and, in some states, state income tax or disability insurance. '
                   f'Each one follows a published rule.[[irs_p15t,irs_p15]]</p>')
    corpo += f'<h3>1. Federal income tax</h3><p>We follow Worksheet 1A of IRS Publication 15-T, the method written for payroll software:</p>{rim.cit("irs_p15t", "uso")}'
    corpo += (f'<p>The worksheet turns your pay into a yearly figure, subtracts a fixed amount, reads the tax from the yearly table for your filing status and divides it back by the number of pay periods. '
              f'Example: {usd(200000)} every two weeks, Single, nothing else on the W-4.</p>{passi}'
              f'<p>The full tables are on the <a href="/federal-withholding/">federal withholding page</a>.</p>')
    corpo += f'<h3>2. Social Security and Medicare (FICA)</h3>{rim.cit("irs_p15", "ss")}{rim.cit("irs_p15", "medicare")}'
    corpo += (f'<p>On the same {usd(200000)} paycheck that is {usd(r["ss"])} for Social Security and {usd(r["medicare"])} for Medicare. High earners pay a further {pct(F["addl"])}:</p>{rim.cit("irs_p15", "addl")}')
    corpo += rim.t('<h3>3. State income tax</h3><p>Texas and Florida withhold nothing from wages. California, Illinois and North Carolina each publish their own formula, and the calculator uses it as written: '
                   'California’s Method B, the Illinois automated payroll method and North Carolina’s percentage method.[[ca_methb,il_700t,nc_30]] California also withholds State Disability Insurance.[[ca_rates]]</p>')
    corpo += f'<p>Result for the example in Texas: <strong>{usd(r["netto"])}</strong> take-home from {usd(r["lordo"])} gross.</p></div>'
    corpo += NON_INCLUSO
    corpo += (f'<h2>For employers</h2><div class="testo"><p>Hiring someone costs more than the wage. On top of gross pay an employer owes its own {pct(F["ss"])} Social Security and {pct(F["medicare"])} Medicare, '
              f'federal unemployment tax (FUTA) on the first {usd0(FU["base"])} of each employee’s wages and state unemployment tax. '
              f'See <a href="/employer-payroll-taxes/">employer payroll taxes for {ANNO}</a> for the rates in each of the five states and a cost calculator, and <a href="/how-to-do-payroll/">how to do payroll yourself</a> for the deposits and forms.</p></div>')
    faq = [
        ("how much taxes are taken out of a paycheck", "How much tax is taken out of a paycheck?",
         f"It depends on your pay, your Form W-4 and your state. Every paycheck has {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare withheld, plus federal income tax worked out from IRS Publication 15-T. "
         f"For example, on {usd(200000)} paid every two weeks to a single filer in Texas in {ANNO}, {usd(r['fed'])} federal income tax, {usd(r['ss'])} Social Security and {usd(r['medicare'])} Medicare are withheld, leaving {usd(r['netto'])}.", "irs_p15t,irs_p15"),
        ("how to calculate net pay", "How do you calculate net pay?",
         "Start from gross pay for the pay period and subtract federal income tax withholding, Social Security, Medicare, any state income tax or state disability insurance, and then any other deductions your employer takes. "
         "This calculator does the tax part; benefits and other deductions are not included.", "irs_p15t,irs_p15"),
        ("what is fica tax", "What is FICA tax?",
         f"FICA is the pair of federal payroll taxes for Social Security and Medicare. In {ANNO} the employee pays {pct(F['ss'])} for Social Security on wages up to {usd0(F['ss_base'])} and {pct(F['medicare'])} for Medicare on all wages, "
         f"{pct(F['ss'] + F['medicare'])} in total below the wage base. The employer pays the same amounts again.", "irs_p15"),
        ("social security tax rate", f"What is the Social Security tax rate in {ANNO}?",
         f"{pct(F['ss'])} for the employee and {pct(F['ss'])} for the employer, on wages up to the wage base limit of {usd0(F['ss_base'])} for {ANNO}. Wages above that limit are not subject to Social Security tax for the rest of the year.", "irs_p15"),
        ("medicare tax rate", "What is the Medicare tax rate?",
         f"{pct(F['medicare'])} for the employee and {pct(F['medicare'])} for the employer, with no wage limit. An employer must also withhold {pct(F['addl'])} Additional Medicare Tax on wages above {usd0(F['addl_soglia'])} in a calendar year; that extra part is paid only by the employee.", "irs_p15"),
        ("hourly paycheck calculator", "Can I use the calculator for hourly pay?",
         "Yes. Choose “Hourly rate”, enter the rate and the hours in the pay period (for example 80 for two weeks) and the calculator multiplies them to get gross pay. Overtime is not worked out separately: add it at its own rate or enter total pay for the period.", "irs_p15t"),
    ]
    fq, ld = faq_blocco(faq, rim)
    corpo += fq + rim.elenco()
    testata = banda(f"{ANNO} · IRS Publication 15-T", f"Paycheck calculator {ANNO}: take-home pay after taxes",
                    "Enter your pay and your Form W-4 choices to estimate what lands in your bank account. Federal income tax, Social Security, Medicare and state tax for "
                    "<strong>Texas, Florida, California, Illinois and North Carolina</strong>, each from the official formula.")
    ld_sito = {"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}
    pagina("", f"Paycheck Calculator {ANNO}: Take-Home Pay After Taxes",
           f"Free {ANNO} paycheck calculator for Texas, Florida, California, Illinois and North Carolina: federal tax from IRS Pub. 15-T, FICA and state tax. Estimate only.",
           corpo, testata, jsonld=[ld_sito, ld], script_dati=script_dati())


# ---------------------------------------------------------------- pagine di Stato
def blocco_datore(s, rim, titolo_h2=True):
    st, su, F, FU = G["stati"][s], G["stati"][s]["suta"], G["fica"], G["futa"]
    rid = FU["riduzione_credito"].get(s, 0)
    righe = (f'<tr><th scope="row">Social Security (employer share)</th><td class="n">{pct(F["ss"])}</td><td>First {usd0(F["ss_base"])} of each employee’s wages</td></tr>'
             f'<tr><th scope="row">Medicare (employer share)</th><td class="n">{pct(F["medicare"])}</td><td>All wages</td></tr>'
             f'<tr><th scope="row">FUTA (federal unemployment)</th><td class="n">{pct(FU["netta"] + rid)}</td><td>First {usd0(FU["base"])}; '
             + (f'{pct(FU["netta"])} after the full credit plus a {pct(rid)} credit reduction for {st["nome"]} in {ANNO}' if rid else f'{pct(FU["aliquota"])} less a credit of up to {pct(FU["credito_max"])}') + '</td></tr>'
             f'<tr><th scope="row">{h(st["nome"])} {h(su["nome"])}, new employers</th><td class="n">{pct(su["nuovo"])}</td><td>First {usd0(su["base"])}'
             + (f'; experienced employers {pct(su["min"])} to {pct(su["max"])}' if "min" in su else "") + '</td></tr>')
    if "ett" in su:
        righe += f'<tr><th scope="row">California Employment Training Tax (ETT)</th><td class="n">{pct(su["ett"])}</td><td>First {usd0(su["ett_base"])}</td></tr>'
    out = (f'<h2 id="employer">Employer payroll taxes in {h(st["nome"])}, {ANNO}</h2>' if titolo_h2 else "")
    out += rim.t(f'<div class="tab"><table class="dati" data-datore-tab="{s}"><caption><span>What an employer pays on top of wages in {h(st["nome"])}, {ANNO}</span></caption><thead><tr><th>Tax</th><th class="n">Rate</th><th>Applies to</th></tr></thead><tbody>{righe}</tbody></table></div>')
    return out


TESTI_STATO = {}


def stato_tx(rim):
    su = G["stati"]["TX"]["suta"]
    t = ('<h2>Texas income tax on a paycheck</h2><div class="testo"><p>Texas does not tax wages, so a Texas paycheck has only the federal lines: federal income tax, Social Security and Medicare. '
         'There is no state form to fill in next to the federal Form W-4 and no state disability insurance deduction.</p></div>')
    d = ('<div class="testo">' + rim.cit("tx_rates", "base") + rim.cit("tx_rates", "nuovo")
         + rim.t(f'<p>The Texas Workforce Commission (TWC) collects the state unemployment tax from employers only; nothing is withheld from the employee. A new employer starts at the entry-level rate of {pct(su["nuovo"])}, '
                 f'so the tax on an employee who earns at least {usd0(su["base"])} is {usd(motore.quota(su["base"] * 100, motore.m(su["nuovo"])))} for the year. '
                 f'For experience-rated employers TWC adds up five components and gives the range for {ANNO}:[[tx_your]]</p>') + rim.cit("tx_your", "minmax")
         + '<h3>Is 2.7% the whole rate for a new employer?</h3>'
         + '<p>We could not settle this from the TWC pages. The 0.32% minimum is made of three flat parts: the replenishment rate (0.21% for 2026), the interest tax (0.01%) and the employment and training assessment (0.10%). TWC describes the first of them like this:</p>'
         + rim.cit("tx_your", "rtr") + rim.cit("tx_your", "rtr_2026")
         + rim.t(f'<p>The pages do not say whether a new employer pays these parts <em>on top of</em> the entry-level rate. If it does, the effective rate would be 3.02% and the most per employee {usd(motore.quota(su["base"] * 100, 3020))} instead of '
                 f'{usd(motore.quota(su["base"] * 100, motore.m(su["nuovo"])))}. The calculator below starts from 2.7%, the only new-employer rate TWC prints; your TWC tax rate notice shows your effective rate, so type that one in if you have it.[[tx_your]]</p>')
         + '</div>')
    return t, d


def stato_fl(rim):
    su = G["stati"]["FL"]["suta"]
    t = ('<h2>Florida income tax on a paycheck</h2><div class="testo"><p>Florida does not tax wages, so a Florida paycheck has only the federal lines: federal income tax, Social Security and Medicare. '
         'There is no state withholding form and no state disability insurance deduction.</p></div>')
    d = ('<div class="testo">' + rim.cit("fl_rt", "nuovo") + rim.cit("fl_rt", "chi")
         + f'<p>Florida calls its state unemployment tax the reemployment tax. It is paid by the employer and is not taken from the employee’s pay. At the initial rate, an employee who earns at least {usd0(su["base"])} '
           f'costs {usd(motore.quota(su["base"] * 100, motore.m(su["nuovo"])))} in reemployment tax for the year. The Florida Department of Revenue assigns a different rate once the business has a qualifying employment record; '
           'the range of those rates is not on the page we read, so the calculator below lets you type your own.</p></div>')
    return t, d


def stato_ca(rim):
    st = G["stati"]["CA"]
    it, su, sdi = st["imposta_reddito"], st["suta"], st["sdi"]
    b = motore.statale(R, {"stato": "CA", "periodo": "biweekly", "lordo": 160000, "ca_fs": "married", "ca_reg": 2, "ca_est": 1})
    if b["imposta"] != 238:
        raise SystemExit("California: l'esempio B ufficiale (2,38 $) non torna")
    aliq = ", ".join(f'{x["pct"]:g}%' for x in it["scaglioni"]["biweekly"]["single"])
    t = ('<h2>How California withholds income tax</h2><div class="testo">'
         + rim.t('<p>California employers withhold state income tax (PIT) with one of two official methods. This calculator uses Method B, the exact calculation, with the payroll-period tables for weekly, biweekly, semi-monthly and monthly pay.[[ca_methb]]</p>')
         + rim.cit("ca_methb", "metodo")
         + '<ol class="steps"><li>If gross pay is not above the low income exemption for your filing status, nothing is withheld.</li>'
           '<li>Subtract the estimated deduction for any allowances on line 2 of Form DE 4, then the standard deduction.</li>'
           f'<li>Apply the rate table for the pay period and filing status ({aliq}).</li>'
           '<li>Subtract the exemption allowance credit for the regular allowances on line 1.</li></ol>'
         + rim.cit("ca_methb", "step1") + rim.cit("ca_methb", "step3")
         + f'<h3>The EDD’s own example, recalculated</h3><p>Example B in the {ANNO} schedules: biweekly earnings of $1,600, married, three allowances of which one is for estimated deductions. '
           f'The EDD’s answer is $2.38 withheld. Our calculator gives the same result:</p><ul class="passi">'
           f'<li>$1,600.00 is above the low income exemption of {usd(b["soglia"])}</li>'
           f'<li>$1,600.00 − {usd(b["stimate"])} estimated deduction − {usd(b["deduzione"])} standard deduction = <b>{usd(b["imponibile"])}</b> taxable</li>'
           f'<li>{usd(b["riga"][1])} + 2.2% of the amount over {usd(b["riga"][0])} = <b>{usd(b["calcolata"])}</b></li>'
           f'<li>{usd(b["calcolata"])} − {usd(b["credito"])} credit for two regular allowances = <b>{usd(b["imposta"])}</b></li></ul>'
         + '<p>For married employees whose spouse also works, the EDD suggests a different choice, which is why the calculator’s first filing status covers both:</p>' + rim.cit("ca_methb", "sposati")
         + '<p class="small">For the “Married” column of the low income exemption and standard deduction tables (0 or 1 allowances, 2 or more) we count the regular allowances on line 1; the schedule does not spell out which line it means.</p>'
         + f'<h3>State Disability Insurance (SDI)</h3>' + rim.cit("ca_rates", "sdi_2026") + rim.cit("ca_rates", "sdi_tutto")
         + f'<p>SDI is paid by the employee. At {pct(sdi["aliquota"])}, {usd(200000)} of gross pay has {usd(motore.quota(200000, motore.m(sdi["aliquota"])))} withheld. The EDD has already published the rate for 2027:</p>'
         + rim.cit("ca_rates", "sdi_2027") + '</div>')
    rid = G["futa"]["riduzione_credito"]["CA"]
    d = ('<div class="testo">' + rim.cit("ca_rates", "ui_nuovo") + rim.cit("ca_rates", "ett_2026")
         + rim.t(f'<p>California employers pay Unemployment Insurance (UI) and the Employment Training Tax (ETT) on the first {usd0(su["base"])} of each employee’s wages: at the new-employer rate, '
                 f'{usd(motore.quota(su["base"] * 100, motore.m(su["nuovo"])))} of UI and {usd(motore.quota(su["ett_base"] * 100, motore.m(su["ett"])))} of ETT for an employee who earns at least that much. '
                 f'The {ANNO} schedule for experienced employers runs from {pct(su["min"])} to {pct(su["max"])}.[[ca_rates]]</p>')
         + f'<h3>Higher FUTA for California in {ANNO}</h3>'
         + rim.t(f'<p>California still owes the federal government money borrowed for unemployment benefits, so its employers lose part of the usual FUTA credit. For {ANNO} the Department of Labor’s final list gives:[[dol_futa]]</p>')
         + rim.cit("dol_futa_2026", "ca")
         + f'<p>That makes FUTA {pct(G["futa"]["netta"])} + {pct(rid)} = {pct(G["futa"]["netta"] + rid)} of the first {usd0(G["futa"]["base"])}: '
           f'{usd(motore.quota(G["futa"]["base"] * 100, motore.m(G["futa"]["netta"] + rid)))} per employee instead of {usd(motore.quota(G["futa"]["base"] * 100, motore.m(G["futa"]["netta"])))}.</p></div>')
    return t, d


def stato_il(rim):
    st = G["stati"]["IL"]
    it, su = st["imposta_reddito"], st["suta"]
    a = motore.statale(R, {"stato": "IL", "periodo": "weekly", "lordo": 80000, "il1": 2, "il2": 2})
    if a["imposta"] != 3213:
        raise SystemExit("Illinois: l'esempio ufficiale (32,13 $) non torna")
    t = ('<h2>How Illinois withholds income tax</h2><div class="testo">' + rim.cit("il_700t", "aliquota")
         + rim.t(f'<p>Illinois has one flat rate. The calculator uses the automated payroll method in Booklet IL-700-T: take the allowances from Form IL-W-4 ({usd0(it["riga1"])} a year for each one on Line 1, '
                 f'{usd0(it["riga2"])} for each one on Line 2), divide by the number of pay periods, subtract from the pay and multiply by {pct(it["aliquota"])}.[[il_700t]]</p>')
         + rim.cit("il_700t", "riga1") + rim.cit("il_700t", "riga2") + rim.cit("il_700t", "step4")
         + f'<h3>The Department of Revenue’s own example, recalculated</h3><p>The booklet’s example: Alice is paid $800 every week and claims two allowances on Line 1 and two on Line 2. The booklet’s answer is $32.13. Our calculator gives the same result:</p>'
           f'<ul class="passi"><li>(2 × {usd0(it["riga1"])} + 2 × {usd0(it["riga2"])}) ÷ 52 = <b>{usd(a["esenzioni"])}</b> exempt per week</li>'
           f'<li>$800.00 − {usd(a["esenzioni"])} = <b>{usd(a["imponibile"])}</b> taxable</li>'
           f'<li>{usd(a["imponibile"])} × {pct(it["aliquota"])} = <b>{usd(a["imposta"])}</b></li></ul>'
           '<p>Illinois has no state disability insurance deduction, and we found no local income tax to add in the state booklet.</p></div>')
    d = ('<div class="testo">' + rim.cit("il_ea50", "nuovo") + rim.cit("il_ea50", "fondo") + rim.cit("il_ea50", "base")
         + f'<p>The Illinois Department of Employment Security (IDES) collects unemployment contributions from employers only. At the entry rate, an employee who earns at least {usd0(su["base"])} costs '
           f'{usd(motore.quota(su["base"] * 100, motore.m(su["nuovo"])))} for the year. IDES sets a higher entry rate for new employers in sectors whose average rate is above the standard one; the calculator below lets you type your own rate.</p></div>')
    return t, d


def stato_nc(rim):
    st = G["stati"]["NC"]
    it, su = st["imposta_reddito"], st["suta"]
    a = motore.statale(R, {"stato": "NC", "periodo": "weekly", "lordo": 45000, "nc_fs": "single", "nc_all": 2})
    if a["imposta"] != 400:
        raise SystemExit("North Carolina: l'esempio ufficiale (4 $) non torna")
    p = it["periodi"]["biweekly"]
    t = ('<h2>How North Carolina withholds income tax</h2><div class="testo">' + rim.cit("nc_30", "aliquota") + rim.cit("nc_30", "ritenuta")
         + rim.t(f'<p>The income tax rate is {pct(it["aliquota_imposta"])}, but employers withhold at {pct(it["aliquota_ritenuta"])}. The calculator uses the percentage method in Form NC-30: subtract the pay-period share of the N.C. standard deduction '
                 f'(for biweekly pay {usd(motore.c(p["single"]["deduzione"]))}, or {usd(motore.c(p["hoh"]["deduzione"]))} for a head of household) and {usd(motore.c(p["single"]["esenzione"]))} for each allowance on Form NC-4, '
                 f'multiply by {pct(it["aliquota_ritenuta"])} and round to the nearest dollar.[[nc_30]]</p>')
         + f'<h3>The Department of Revenue’s own example, recalculated</h3><p>The NC-30 example: an unmarried employee paid $450.00 weekly, single with two allowances. The department’s answer is $4.00. Our calculator gives the same result:</p>'
           f'<ul class="passi"><li>$450.00 − {usd(a["deduzione"])} standard deduction − {usd(a["esenzioni"])} for two allowances = <b>{usd(a["imponibile"])}</b></li>'
           f'<li>{usd(a["imponibile"])} × {pct(it["aliquota_ritenuta"])} = $4.44, rounded to <b>{usd(a["imposta"])}</b></li></ul>'
           '<p>North Carolina has no state disability insurance deduction, and we found no local income tax to add in Form NC-30.</p></div>')
    d = ('<div class="testo">' + rim.cit("nc_des", "nuovo") + rim.cit("nc_des", "base") + rim.cit("nc_des", "minmax")
         + f'<p>The Division of Employment Security collects the unemployment tax from employers only. The rate for beginning employers is low but the wage base is high: an employee who earns at least {usd0(su["base"])} costs '
           f'{usd(motore.quota(su["base"] * 100, motore.m(su["nuovo"])))} for the year at {pct(su["nuovo"])}.</p></div>')
    return t, d


def faq_stato(s):
    st, su, F = G["stati"][s], G["stati"][s]["suta"], G["fica"]
    n = st["nome"]
    r = motore.busta(R, caso(s, 200000))
    q = {
        "TX": lambda: [("does texas have state income tax", "Does Texas have a state income tax?",
                f"No. Texas does not tax wages, so nothing is withheld for the state. A Texas paycheck still has federal income tax, {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare withheld.", "irs_p15"),
               ("paycheck calculator texas hourly", "How do I work out a Texas paycheck from an hourly wage?",
                f"Multiply the hourly rate by the hours in the pay period to get gross pay, then subtract federal income tax, Social Security and Medicare. In the calculator choose “Hourly rate” and enter the hours. Example: {usd(200000)} gross every two weeks, single filer, leaves {usd(r['netto'])} in {ANNO}.", "irs_p15t,irs_p15"),
               ("texas payroll taxes", "What payroll taxes does a Texas employer pay?",
                f"The employer’s {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare, federal unemployment tax (FUTA) and Texas unemployment tax on the first {usd0(su['base'])} of each employee’s wages. There is no state income tax to withhold.", "irs_p15,tx_rates"),
               ("texas unemployment tax rate", f"What is the Texas unemployment tax rate for {ANNO}?",
                f"New employers start at the entry-level rate of {pct(su['nuovo'])}. For experience-rated employers the Texas Workforce Commission gives a minimum of {pct(su['min'])} and a maximum of {pct(su['max'])} for {ANNO}. The tax applies to the first {usd0(su['base'])} each employee earns in the year.", "tx_rates,tx_your")],
        "FL": lambda: [("does florida have state income tax", "Does Florida have a state income tax?",
                f"No. Florida does not tax wages, so nothing is withheld for the state. A Florida paycheck still has federal income tax, {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare withheld.", "irs_p15"),
               ("florida reemployment tax", "What is the Florida reemployment tax?",
                f"It is Florida’s state unemployment tax, paid by employers and not deducted from employees’ pay. The initial rate for new employers is {pct(su['nuovo'])} on the first {usd0(su['base'])} of wages paid to each employee in a calendar year.", "fl_rt"),
               ("florida payroll taxes", "What payroll taxes does a Florida employer pay?",
                f"The employer’s {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare, federal unemployment tax (FUTA) and Florida reemployment tax on the first {usd0(su['base'])} of each employee’s wages. There is no state income tax to withhold.", "irs_p15,fl_rt")],
        "CA": lambda: [("california sdi tax", "What is the California SDI tax?",
                f"State Disability Insurance (SDI) is a California payroll deduction paid by employees. The withholding rate for {ANNO} is {pct(st['sdi']['aliquota'])} of all wages: since January 1, 2024 there is no taxable wage limit. The rate published for 2027 is {pct(st['sdi']['aliquota_2027'])}.", "ca_rates") if s == "CA" else None,
               ("california state income tax", "How is California state income tax withheld from a paycheck?",
                "Employers use the EDD’s withholding schedules. Under Method B they subtract a standard deduction, apply a rate table with rates from 1.1% to 14.63% for the pay period and filing status, and subtract a credit for each regular allowance on Form DE 4. Pay at or below the low income exemption has nothing withheld.", "ca_methb"),
               ("california payroll taxes", "What payroll taxes does a California employer pay?",
                f"The employer’s {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare, FUTA, California Unemployment Insurance and the {pct(su.get('ett', 0))} Employment Training Tax, the last two on the first {usd0(su['base'])} of each employee’s wages. The employer also withholds the employee’s income tax and SDI.", "irs_p15,ca_rates") if s == "CA" else None,
               ("california unemployment tax rate", "What is the California unemployment tax rate for new employers?",
                f"New employers are assigned a {pct(su['nuovo'])} UI rate for two to three years, on the first {usd0(su['base'])} of each employee’s wages. In {ANNO} experienced employers pay between {pct(su.get('min', 0))} and {pct(su.get('max', 0))}.", "ca_rates") if s == "CA" else None],
        "IL": lambda: [("illinois income tax rate", "What is the Illinois income tax rate?",
                f"{pct(st['imposta_reddito']['aliquota']) if s == 'IL' else ''}. Illinois has one flat rate for withholding, applied to pay after the allowances on Form IL-W-4: {usd0(st['imposta_reddito']['riga1']) if s == 'IL' else ''} a year for each Line 1 allowance and {usd0(st['imposta_reddito']['riga2']) if s == 'IL' else ''} for each Line 2 allowance in {ANNO}.", "il_700t"),
               ("does illinois have state income tax", "Does Illinois have a state income tax?",
                f"Yes. Illinois employers withhold a flat {pct(st['imposta_reddito']['aliquota']) if s == 'IL' else ''} from wages. On {usd(200000)} paid every two weeks with one Line 1 allowance, {usd(r['stato'])} is withheld for Illinois.", "il_700t"),
               ("illinois payroll taxes", "What payroll taxes does an Illinois employer pay?",
                f"The employer’s {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare, FUTA and Illinois unemployment contributions on the first {usd0(su['base'])} of each worker’s wages. The employer also withholds the employee’s Illinois income tax.", "irs_p15,il_ea50"),
               ("illinois unemployment tax rate", f"What is the Illinois unemployment tax rate for new employers in {ANNO}?",
                f"Most new employers pay the entry rate of {pct(su['nuovo'])}, which includes the {pct(su.get('fondo', 0))} Fund Building Rate, on the first {usd0(su['base'])} of each worker’s wages. Some sectors have a higher entry rate.", "il_ea50")],
        "NC": lambda: [("north carolina income tax rate", f"What is the North Carolina income tax rate in {ANNO}?",
                f"{pct(st['imposta_reddito']['aliquota_imposta']) if s == 'NC' else ''}. Employers withhold at {pct(st['imposta_reddito']['aliquota_ritenuta']) if s == 'NC' else ''}, the tax rate plus 0.1%, after subtracting the N.C. standard deduction and the allowances on Form NC-4.", "nc_30"),
               ("does north carolina have state income tax", "Does North Carolina have a state income tax?",
                f"Yes. North Carolina taxes wages at a flat rate and employers withhold it from each paycheck. On {usd(200000)} paid every two weeks, single with no allowances, {usd(r['stato'])} is withheld for North Carolina in {ANNO}.", "nc_30"),
               ("north carolina payroll taxes", "What payroll taxes does a North Carolina employer pay?",
                f"The employer’s {pct(F['ss'])} Social Security and {pct(F['medicare'])} Medicare, FUTA and North Carolina unemployment tax on the first {usd0(su['base'])} of each employee’s wages. The employer also withholds the employee’s state income tax.", "irs_p15,nc_des"),
               ("north carolina unemployment tax rate", f"What is the North Carolina unemployment tax rate for {ANNO}?",
                f"Beginning employers pay {pct(su['nuovo'])} on a taxable wage base of {usd0(su['base'])}. Experience-rated employers pay between {pct(su.get('min', 0))} and {pct(su.get('max', 0))}.", "nc_des")],
    }[s]()
    return [x for x in q if x]


def pagina_stato(s):
    rim = Rimandi()
    st, su = G["stati"][s], G["stati"][s]["suta"]
    n = st["nome"]
    corpo = '<div class="pull">' + calcolatore(s, titolo=f"{n} paycheck calculator, {ANNO}") + '</div>'
    if st["imposta_reddito"] is None:
        a1, a2 = "0%", f"{n} income tax on wages"
    elif s == "CA":
        a1, a2 = "1.1%–14.63%", "California withholding rates (Method B)"
    elif s == "IL":
        a1, a2 = pct(st["imposta_reddito"]["aliquota"]), "Illinois income tax withholding, flat rate"
    else:
        a1, a2 = pct(st["imposta_reddito"]["aliquota_ritenuta"]), f"North Carolina withholding rate (tax rate {pct(st['imposta_reddito']['aliquota_imposta'])})"
    b1, b2 = (pct(st["sdi"]["aliquota"]), "State Disability Insurance, paid by the employee") if st.get("sdi") else ("None", "State disability insurance deduction")
    corpo += ('<div class="stats card" style="margin-top:26px">'
              f'<div class="stat main"><b>{a1}</b><span>{h(a2)}</span></div><div class="stat"><b>{b1}</b><span>{h(b2)}</span></div>'
              f'<div class="stat"><b>{pct(su["nuovo"])}</b><span>State unemployment tax rate for new employers</span></div>'
              f'<div class="stat"><b>{usd0(su["base"])}</b><span>Wages per employee subject to state unemployment tax</span></div>'
              f'<p class="asof">Official {n} and IRS figures for {ANNO}, read on {data_lunga(CONTROLLO)}.</p></div>')
    corpo += f'<h2>{h(n)} take-home pay examples, {ANNO}</h2>' + tabella_esempi(s)
    corpo += '<p class="small">Each row is our arithmetic with the official formulas. Change any entry in the calculator above for your own case.</p>'
    testo, datore_t = {"TX": stato_tx, "FL": stato_fl, "CA": stato_ca, "IL": stato_il, "NC": stato_nc}[s](rim)
    corpo += testo
    corpo += rim.t('<h2>The federal part</h2><div class="testo"><p>Federal income tax, Social Security and Medicare are the same in every state. The calculator follows Worksheet 1A of IRS Publication 15-T and the rates in Publication 15; '
                   'the tables and a worked example are on the <a href="/federal-withholding/">federal withholding page</a>.[[irs_p15t,irs_p15]]</p></div>')
    corpo += blocco_datore(s, rim) + datore_t
    corpo += '<div style="margin-top:22px">' + calcolatore_datore(s) + '</div>' + riquadro_partner()
    corpo += (f'<p>Registering, reports and due dates for employers: <a href="/{slug_paghe(s)}">{h(n)} payroll taxes {ANNO}</a>. '
              f'Rates for all five states side by side: <a href="/employer-payroll-taxes/">employer payroll taxes {ANNO}</a>.</p>')
    fq, ld = faq_blocco(faq_stato(s), rim)
    corpo += fq
    corpo += f'<h2>Other states</h2>{griglia_stati(s)}' + rim.elenco()
    sub = {"TX": "No state income tax: a Texas paycheck has only the federal lines. Estimate your take-home pay, then see what a Texas employer pays on top.",
           "FL": "No state income tax: a Florida paycheck has only the federal lines. Estimate your take-home pay, then see what a Florida employer pays on top.",
           "CA": "Federal tax, California income tax by the EDD’s Method B and State Disability Insurance. Then what a California employer pays on top.",
           "IL": "Federal tax and the flat Illinois income tax, by the Department of Revenue’s own formula. Then what an Illinois employer pays on top.",
           "NC": "Federal tax and North Carolina income tax by the NC-30 percentage method. Then what a North Carolina employer pays on top."}[s]
    testata = banda(f"{n} · {ANNO}", f"{n} paycheck calculator {ANNO}", h(sub), icona="map")
    desc = {"TX": f"Texas paycheck calculator for {ANNO}: no state income tax, federal withholding from IRS Pub. 15-T, FICA. Plus Texas employer taxes: 2.7% entry rate on $9,000.",
            "FL": f"Florida paycheck calculator for {ANNO}: no state income tax, federal withholding from IRS Pub. 15-T, FICA. Plus reemployment tax: 2.7% on the first $7,000.",
            "CA": f"California paycheck calculator for {ANNO}: EDD Method B income tax, SDI 1.3%, federal tax and FICA. Plus employer UI 3.4%, ETT and the higher FUTA rate.",
            "IL": f"Illinois paycheck calculator for {ANNO}: flat 4.95% state tax with IL-W-4 allowances, federal tax and FICA. Plus employer rate 3.35% on $14,250.",
            "NC": f"North Carolina paycheck calculator for {ANNO}: NC-30 percentage method (4.09% withholding), federal tax and FICA. Plus employer UI 1% on $34,200."}[s]
    pagina(f"{slug(s)}/", f"{n} Paycheck Calculator {ANNO} + Employer Payroll Taxes", desc, corpo, testata,
           briciole=[("Home", ""), (n, f"{slug(s)}/")], jsonld=[ld], script_dati=script_dati())


# ---------------------------------------------------------------- imposte del datore di lavoro
def pagina_datore():
    rim = Rimandi()
    F, FU = G["fica"], G["futa"]
    corpo = '<div class="pull">' + calcolatore_datore("TX") + '</div>' + riquadro_partner()
    corpo += f'<h2>Federal payroll taxes paid by the employer, {ANNO}</h2><div class="testo">'
    corpo += rim.cit("irs_p15", "ss") + rim.cit("irs_p15", "medicare") + rim.cit("irs_p15", "addl_solo")
    corpo += (f'<p>The employer matches the employee’s Social Security and Medicare: {pct(F["ss"] + F["medicare"])} of wages up to {usd0(F["ss_base"])}, then {pct(F["medicare"])} above it. '
              f'On a {usd0(50000)} salary that is {usd(motore.quota(5000000, motore.m(F["ss"])) + motore.quota(5000000, motore.m(F["medicare"])))} a year.</p>')
    corpo += '<h3>FUTA: federal unemployment tax</h3>' + rim.cit("irs_p15", "futa") + rim.cit("irs_p15", "futa_credito") + rim.cit("irs_p15", "futa_condizione")
    corpo += (f'<p>So FUTA is normally {pct(FU["netta"])} of the first {usd0(FU["base"])}: {usd(motore.quota(FU["base"] * 100, motore.m(FU["netta"])))} per employee per year. Only the employer pays it.</p>')
    corpo += rim.t(f'<h3>Credit reduction states in {ANNO}</h3><p>When a state has not repaid federal loans for unemployment benefits, its employers get a smaller credit and pay more FUTA.[[dol_futa]] '
                   f'The Department of Labor’s final list for {ANNO} names one of our five states:</p>') + rim.cit("dol_futa_2026", "ca")
    rid = FU["riduzione_credito"]["CA"]
    corpo += (f'<p>For California that means {pct(FU["netta"] + rid)} instead of {pct(FU["netta"])}: {usd(motore.quota(FU["base"] * 100, motore.m(FU["netta"] + rid)))} per employee. '
              'Texas, Florida, Illinois and North Carolina are not on the list.</p></div>')
    corpo += f'<h2 id="states">State unemployment tax (SUTA) in the five states, {ANNO}</h2>'
    righe = ""
    for s in STATI:
        st, su = G["stati"][s], G["stati"][s]["suta"]
        extra = []
        if "ett" in su:
            extra.append(f'ETT {pct(su["ett"])} on {usd0(su["ett_base"])}')
        if FU["riduzione_credito"].get(s):
            extra.append(f'FUTA {pct(FU["netta"] + FU["riduzione_credito"][s])}')
        if st.get("sdi"):
            extra.append(f'SDI {pct(st["sdi"]["aliquota"])} withheld from the employee')
        if s == "TX":
            extra.append("Entry-level rate; flat components of 0.32% may come on top (see the Texas page)")
        mass = motore.datore(R, s, 5000000)
        righe += (f'<tr data-suta="{s}"><th scope="row"><a href="/{slug(s)}/#employer">{h(st["nome"])}</a></th><td>{h(su["nome"])}</td><td class="n">{pct(su["nuovo"])}</td><td class="n">{usd0(su["base"])}</td>'
                  f'<td class="n">{usd(motore.quota(su["base"] * 100, motore.m(su["nuovo"])))}</td><td>{h("; ".join(extra)) or "–"}</td><td class="n">{usd(mass["totale"])}</td></tr>')
    corpo += rim.t('<div class="tab"><table class="dati" data-suta-tab><caption><span>New-employer rate and taxable wage base, from each state agency.[[tx_rates,fl_rt,ca_rates,il_ea50,nc_des]] Last column: all employer payroll taxes on a $50,000 salary (our arithmetic).</span></caption>'
                   '<thead><tr><th>State</th><th>Name of the tax</th><th class="n">New employer rate</th><th class="n">Wage base</th><th class="n">Most per employee</th><th>Also</th><th class="n">Total on $50,000</th></tr></thead>'
                   f'<tbody>{righe}</tbody></table></div>')
    corpo += ('<div class="testo"><p>State unemployment tax is paid by the employer in all five states; none of them deducts it from the employee. After the first years each state replaces the new-employer rate with one based on the business’s own record, '
              'so use the rate on your notice in the calculator.</p>'
              '<p>Federal deposit dates and Forms 941 and 940 are on <a href="/how-to-do-payroll/">how to do payroll yourself</a>; registration and state reports are on each state’s payroll page below. '
              'Workers’ compensation insurance is not a payroll tax and is not included.</p></div>'
              f'<h2 id="by-state">Payroll taxes by state: registration and due dates</h2>{griglia_paghe()}')
    r50 = motore.datore(R, "TX", 5000000)
    faq = [
        ("employer payroll taxes", "What payroll taxes does an employer pay?",
         f"In {ANNO} an employer pays {pct(F['ss'])} Social Security on wages up to {usd0(F['ss_base'])}, {pct(F['medicare'])} Medicare on all wages, federal unemployment tax (FUTA) on the first {usd0(FU['base'])} and state unemployment tax. "
         f"For a {usd0(50000)} salary in Texas at the new-employer rate these come to {usd(r50['totale'])} a year.", "irs_p15,tx_rates"),
        ("what is futa", "What is FUTA?",
         f"FUTA is the Federal Unemployment Tax Act tax, paid only by employers. For {ANNO} the rate is {pct(FU['aliquota'])} on the first {usd0(FU['base'])} of each employee’s wages, less a credit of up to {pct(FU['credito_max'])} for state unemployment taxes paid, which leaves {pct(FU['netta'])}.", "irs_p15"),
        ("futa tax rate", f"What is the FUTA tax rate for {ANNO}?",
         f"{pct(FU['aliquota'])} before the credit and {pct(FU['netta'])} after the maximum credit, on the first {usd0(FU['base'])} paid to each employee: {usd(motore.quota(FU['base'] * 100, motore.m(FU['netta'])))} per employee. In California the {ANNO} credit reduction of {pct(rid)} raises it to {pct(FU['netta'] + rid)}.", "irs_p15,dol_futa_2026"),
        ("suta tax", "What is SUTA tax?",
         f"SUTA is the common name for state unemployment tax, which each state sets. In {ANNO} new employers pay {pct(G['stati']['TX']['suta']['nuovo'])} on the first {usd0(G['stati']['TX']['suta']['base'])} in Texas, {pct(G['stati']['FL']['suta']['nuovo'])} on {usd0(G['stati']['FL']['suta']['base'])} in Florida, "
         f"{pct(G['stati']['CA']['suta']['nuovo'])} on {usd0(G['stati']['CA']['suta']['base'])} in California, {pct(G['stati']['IL']['suta']['nuovo'])} on {usd0(G['stati']['IL']['suta']['base'])} in Illinois and {pct(G['stati']['NC']['suta']['nuovo'])} on {usd0(G['stati']['NC']['suta']['base'])} in North Carolina.", "tx_rates,fl_rt,ca_rates,il_ea50,nc_des"),
        ("how much does it cost to hire an employee", "How much does an employee cost on top of the wage?",
         f"Payroll taxes add roughly 8% to 9% to a {usd0(50000)} salary in these five states: {usd(r50['totale'])} in Texas and {usd(motore.datore(R, 'CA', 5000000)['totale'])} in California in {ANNO}, at new-employer rates. Benefits and workers’ compensation insurance come on top and are not included here.", "irs_p15,tx_rates,ca_rates"),
    ]
    fq, ld = faq_blocco(faq, rim)
    corpo += fq + f'<h2>Paycheck calculators by state</h2>{griglia_stati()}' + rim.elenco()
    testata = banda(f"Employers · {ANNO}", f"Employer payroll taxes {ANNO}",
                    "What an employer pays on top of wages: Social Security, Medicare, FUTA and state unemployment tax, with the rates for Texas, Florida, California, Illinois and North Carolina.", icona="build")
    pagina("employer-payroll-taxes/", f"Employer Payroll Taxes {ANNO}: FICA, FUTA and State Rates",
           f"Employer payroll taxes for {ANNO}: 7.65% FICA, FUTA 0.6% on $7,000 and state unemployment tax for new employers in TX, FL, CA, IL and NC, with a calculator.",
           corpo, testata, briciole=[("Home", ""), ("Employer payroll taxes", "employer-payroll-taxes/")], jsonld=[ld], script_dati=script_dati())


# ---------------------------------------------------------------- pagine per i datori di lavoro: paghe per Stato e «how to do payroll»
def slug_paghe(s):
    return f"{slug(s)}-payroll-taxes/"


SCADENZE_TRIM = "April 30, July 31, October 31 and January 31"   # ultimo giorno del mese dopo il trimestre


def griglia_paghe(escludi=None):
    voci = []
    for s in STATI:
        if s == escludi:
            continue
        su = G["stati"][s]["suta"]
        voci.append(f'<li><a href="/{slug_paghe(s)}"><b>{h(nome_stato(s))}</b><small>{pct(su["nuovo"])} on {usd0(su["base"])}, new employers</small></a></li>')
    return f'<ul class="griglia stati">{"".join(voci)}</ul>'


def stato_iscrizione(s, rim):
    """Iscrizione, dichiarazioni e scadenze dello Stato: solo frasi delle agenzie, citate alla lettera."""
    n = nome_stato(s)
    if s == "TX":
        return ('<div class="testo">'
                + rim.t('<p>Texas has no income tax on wages, so there is no state withholding account to open. The one state registration is the unemployment tax account with the Texas Workforce Commission (TWC).[[tx_ut]]</p>')
                + rim.cit("tx_ut", "registro") + rim.cit("tx_ut", "scadenza")
                + f'<p>That makes the four due dates {SCADENZE_TRIM}; TWC’s own due-date page moves a date that falls on a weekend or holiday.</p>'
                + rim.t('<p>Reports and payments go through TWC’s online systems; paper is allowed only with a hardship waiver.[[tx_filing]]</p>')
                + rim.cit("tx_filing", "elettronico") + rim.cit("tx_filing", "uts") + '</div>')
    if s == "FL":
        return ('<div class="testo">'
                + rim.t('<p>Florida has no income tax on wages, so there is no state withholding account to open. The one state registration is for reemployment tax, with the Florida Department of Revenue.[[fl_rt]]</p>')
                + rim.cit("fl_rt", "registro")
                + '<p>The Department lists the conditions that make an employer liable. The two that matter to most small businesses:</p>'
                + rim.cit("fl_rt", "soglia") + rim.cit("fl_rt", "soglia_20")
                + rim.t('<p>The report is Form RT-6, the Employer’s Quarterly Report.[[fl_return]]</p>') + rim.cit("fl_return", "trimestre")
                + '<p>About Form RT-6 the Department writes that it:</p>' + rim.cit("fl_return", "scadenza")
                + rim.t(f'<p>The Department’s table gives the last timely days as {SCADENZE_TRIM}.[[fl_return]]</p>') + '</div>')
    if s == "CA":
        return ('<div class="testo">'
                + rim.t('<p>California payroll taxes are run by the Employment Development Department (EDD). One EDD payroll tax account covers all four state taxes.[[ca_step5]]</p>')
                + rim.cit("ca_step5", "quattro")
                + rim.t('<p>The two paid by the employer are Unemployment Insurance (UI) and the Employment Training Tax (ETT); the two withheld from pay are State Disability Insurance (SDI) and Personal Income Tax (PIT).[[ca_step5]] '
                        'When to register:[[ca_step1]]</p>')
                + rim.cit("ca_step1", "registro")
                + rim.t('<p>The 15 days start, for a business with employees, once you:[[ca_step1]]</p>') + rim.cit("ca_step1", "soglia")
                + rim.t('<p>Registration is online, through the EDD’s e-Services for Business. New employees are reported to the EDD as well:[[ca_step4]]</p>') + rim.cit("ca_step4", "nuovi")
                + '<p>Deposits and payments:</p>' + rim.cit("ca_step5", "depositi")
                + rim.t('<p>Every quarter you file two reports, the Quarterly Contribution Return and Report of Wages (DE 9) and its continuation (DE 9C). The EDD gives their due dates as January 1, April 1, July 1 and October 1; '
                        'its “Required Filings and Due Dates” page says when a report counts as late.[[ca_step6]]</p>') + '</div>')
    if s == "IL":
        return ('<div class="testo">'
                + rim.t('<p>Illinois has two agencies for payroll: the Department of Revenue (IDOR) for the income tax you withhold and the Department of Employment Security (IDES) for unemployment contributions. '
                        'Both use the MyTax Illinois website.[[il_idor_reg,il_ides_tax]]</p>')
                + rim.cit("il_idor_reg", "registro") + rim.cit("il_idor_reg", "ides")
                + rim.t('<p>For unemployment contributions, IDES says most for-profit employers are liable as soon as they have:[[il_ides_tax]]</p>') + rim.cit("il_ides_tax", "soglia")
                + '<p>Reports and payments:</p>' + rim.cit("il_ides_tax", "mytax")
                + '<p>The return and deposit schedule for Illinois income tax withholding is not covered here: the Department of Revenue assigns it.</p></div>')
    return ('<div class="testo">'
            + rim.t(f'<p>{n} has two agencies for payroll: the Department of Revenue (NCDOR) for the income tax you withhold and the Division of Employment Security (DES) for unemployment tax.[[nc_30,nc_required]]</p>')
            + '<p>For withholding, the NC-30 booklet says that when you begin paying wages:</p>' + rim.cit("nc_30", "registro") + rim.cit("nc_30", "frequenza")
            + '<p>For unemployment tax, DES writes:</p>' + rim.cit("nc_required", "chi_paga")
            + '<p>A general business is liable when it has:</p>' + rim.cit("nc_required", "soglia") + rim.cit("nc_required", "numero")
            + rim.t('<p>You get the number when you create an account in NCSUITS, the DES online tax system. Then, every quarter:[[nc_quarterly]]</p>')
            + rim.cit("nc_quarterly", "trimestre") + rim.cit("nc_quarterly", "online") + '</div>')


def faq_paghe(s, d50):
    st, su, F, FU = G["stati"][s], G["stati"][s]["suta"], G["fica"], G["futa"]
    n = st["nome"]
    nl = n.lower()
    futa = FU["netta"] + FU["riduzione_credito"].get(s, 0)
    fica = pct(F["ss"] + F["medicare"])
    quota_pct = f"{d50['totale'] / 50000:.1f}%"       # centesimi / 5.000.000 × 100
    righe = (f"{usd(d50['ss'])} Social Security, {usd(d50['medicare'])} Medicare, {usd(d50['futa'])} FUTA and {usd(d50['suta'])} {n} unemployment tax"
             + (f", plus {usd(d50['ett'])} Employment Training Tax" if d50["ett"] else ""))
    if st["imposta_reddito"] is None:
        q1 = (f"{nl} payroll tax", f"Is there a payroll tax in {n}?",
              f"{n} has no state income tax on wages, so nothing is withheld for the state. An employer still pays {n} unemployment tax, {pct(su['nuovo'])} on the first {usd0(su['base'])} of each employee’s wages as a new employer in {ANNO}, "
              f"and the federal payroll taxes: Social Security, Medicare and FUTA.", f"irs_p15,{su['fonte']}")
        dip = f"The employee pays {fica} for Social Security and Medicare and no state tax"
    elif s == "CA":
        q1 = ("california payroll tax", "What are the payroll taxes in California?",
              f"California has four state payroll taxes. The employer pays Unemployment Insurance ({pct(su['nuovo'])} for new employers) and the Employment Training Tax ({pct(su['ett'])}), both on the first {usd0(su['base'])} of each employee’s wages. "
              f"State Disability Insurance ({pct(st['sdi']['aliquota'])} in {ANNO}) and Personal Income Tax are withheld from the employee. The federal payroll taxes come on top.", "ca_step5,ca_rates")
        dip = f"The employee pays {fica} for Social Security and Medicare, {pct(st['sdi']['aliquota'])} SDI and California income tax"
    else:
        al = st["imposta_reddito"]["aliquota"] if s == "IL" else st["imposta_reddito"]["aliquota_ritenuta"]
        q1 = (f"{nl} payroll tax", f"What payroll taxes apply in {n}?",
              f"Two state items. The employer withholds {n} income tax from each paycheck, at {pct(al)} after allowances in {ANNO}, and pays state unemployment tax of {pct(su['nuovo'])} on the first {usd0(su['base'])} of each employee’s wages as a new employer. "
              f"The federal payroll taxes (Social Security, Medicare, FUTA) come on top.", f"{st['imposta_reddito']['fonte']},{su['fonte']},irs_p15")
        dip = f"The employee pays {fica} for Social Security and Medicare and has {n} income tax withheld at {pct(al)}"
    ett_txt = f" (plus the {pct(su['ett'])} Employment Training Tax)" if su.get("ett") else ""
    voci = [q1,
            (f"{nl} payroll tax rate", f"What is the payroll tax rate in {n}?",
             f"There is no single rate. In {ANNO} the employer pays {fica} for Social Security and Medicare (Social Security stops at {usd0(F['ss_base'])} of wages), FUTA of {pct(futa)} on the first {usd0(FU['base'])} "
             f"and {n} unemployment tax of {pct(su['nuovo'])} on the first {usd0(su['base'])} as a new employer{ett_txt}. {dip}. On a {usd0(50000)} salary the employer’s taxes come to {usd(d50['totale'])}, about {quota_pct} of the wage.",
             f"irs_p15,{su['fonte']}")]
    ric3 = f"employer payroll taxes {nl}" if volume(f"employer payroll taxes {nl}") > 0 else f"{nl} employer taxes"
    voci.append((ric3, f"How much are employer payroll taxes in {n} on a {usd0(50000)} salary?",
                 f"{usd(d50['totale'])} in {ANNO} at the new-employer rate: {righe}. Wages plus taxes: {usd(d50['costo'])}. Workers’ compensation insurance and benefits are not included.", f"irs_p15,{su['fonte']}"))
    come = {"TX": ("Get an EIN from the IRS, register an unemployment tax account with the Texas Workforce Commission within ten days of becoming liable, take a Form W-4 from each employee and withhold federal income tax, Social Security and Medicare from each paycheck. "
                   "Deposit the federal taxes, file Form 941 every quarter and Form 940 once a year, and file the TWC wage report and pay the state tax by the last day of the month after each quarter. Texas has no state income tax to withhold.", "irs_p15,tx_ut"),
            "FL": ("Get an EIN from the IRS, register for reemployment tax with the Florida Department of Revenue, take a Form W-4 from each employee and withhold federal income tax, Social Security and Medicare from each paycheck. "
                   "Deposit the federal taxes, file Form 941 every quarter and Form 940 once a year, and file Form RT-6 with the reemployment tax each quarter. Florida has no state income tax to withhold.", "irs_p15,fl_rt,fl_return"),
            "CA": ("Get an EIN from the IRS, then register with the EDD within 15 days of paying more than $100 in wages in a calendar quarter. Take a Form W-4 and a DE 4 from each employee, report new hires within 20 days, "
                   "and withhold federal income tax, Social Security, Medicare, California income tax and SDI. Deposit the taxes, file federal Form 941 and the EDD’s DE 9 and DE 9C every quarter, and Form 940 once a year.", "irs_p15,ca_step1,ca_step4,ca_step6")}
    if s in come and volume(f"how to do payroll in {nl}") > 0:
        voci.append((f"how to do payroll in {nl}", f"How do I do payroll in {n}?", come[s][0], come[s][1]))
    if s == "TX":
        voci.append(("texas employer taxes", "When are Texas employer taxes due?",
                     f"The Texas Workforce Commission wants the quarterly wage report and the unemployment tax by the last day of the month after each calendar quarter: {SCADENZE_TRIM}. Both must be filed and paid electronically. "
                     "Federal deposits follow the IRS schedule: for a new employer, by the 15th of the following month.", "tx_ut,tx_filing,irs_p15"))
    elif s == "FL":
        voci.append(("florida employer taxes", "When are Florida employer taxes due?",
                     f"Form RT-6, the Employer’s Quarterly Report, is due the 1st day of the month after each calendar quarter and is late after the last day of that month: {SCADENZE_TRIM}. "
                     "Federal deposits follow the IRS schedule: for a new employer, by the 15th of the following month.", "fl_return,irs_p15"))
    elif s == "CA":
        voci.append(("edd payroll taxes", "Which payroll taxes does the EDD collect?",
                     "Four: Unemployment Insurance and the Employment Training Tax, paid by the employer, and State Disability Insurance and Personal Income Tax, withheld from employees’ wages. "
                     "UI and ETT payments are due every quarter; SDI and PIT deposit dates depend on your federal deposit schedule and on how much PIT you withhold.", "ca_step5"))
        voci.append(("california de 9", "What is the California DE 9?",
                     "The DE 9 is the EDD’s Quarterly Contribution Return and Report of Wages. Employers file it every quarter together with the DE 9C, the continuation that lists wages. The EDD gives the due dates as January 1, April 1, July 1 and October 1.", "ca_step6"))
    elif s == "IL":
        voci.append(("illinois unemployment tax", "Who has to pay Illinois unemployment tax?",
                     "According to the Illinois Department of Employment Security, most for-profit employers are liable as soon as they have paid $1,500 in wages in a single calendar quarter, or employed one or more persons for 20 weeks in a calendar year. "
                     f"New employers then pay {pct(su['nuovo'])} on the first {usd0(su['base'])} of each worker’s wages in {ANNO}.", "il_ides_tax,il_ea50"))
    else:
        voci.append(("north carolina unemployment tax", "Who has to pay North Carolina unemployment tax?",
                     "According to the Division of Employment Security, a general business is liable when it paid quarterly wages of at least $1,500 or employed at least one worker in 20 different weeks during a calendar year. "
                     f"The tax is paid by the employer and is not deducted from employees’ wages. Beginning employers pay {pct(su['nuovo'])} on the first {usd0(su['base'])} in {ANNO}.", "nc_required,nc_des"))
    return voci


def pagina_paghe_stato(s):
    rim = Rimandi()
    st, su, F, FU = G["stati"][s], G["stati"][s]["suta"], G["fica"], G["futa"]
    n = st["nome"]
    rid = FU["riduzione_credito"].get(s, 0)
    d50 = motore.datore(R, s, 5000000)
    b = motore.busta(R, caso(s, 200000))
    corpo = '<div class="pull">' + calcolatore_datore(s) + '</div>'
    if st["imposta_reddito"] is None:
        r1, r2 = "None", f"{n} income tax to withhold from wages"
    elif s == "CA":
        r1, r2 = pct(st["sdi"]["aliquota"]), "SDI withheld from employees, plus California income tax"
    elif s == "IL":
        r1, r2 = pct(st["imposta_reddito"]["aliquota"]), "Illinois income tax to withhold, flat rate"
    else:
        r1, r2 = pct(st["imposta_reddito"]["aliquota_ritenuta"]), "North Carolina income tax withholding rate"
    corpo += ('<div class="stats card" style="margin-top:26px">'
              f'<div class="stat main"><b>{usd(d50["totale"])}</b><span>Employer payroll taxes on a {usd0(50000)} salary, new employer</span></div>'
              f'<div class="stat"><b>{pct(su["nuovo"])}</b><span>{h(n)} unemployment tax rate for new employers</span></div>'
              f'<div class="stat"><b>{usd0(su["base"])}</b><span>Wages per employee subject to it</span></div>'
              f'<div class="stat"><b>{r1}</b><span>{h(r2)}</span></div>'
              f'<p class="asof">Official {n} and IRS figures for {ANNO}, read on {data_lunga(CONTROLLO)}. Dollar amounts are our arithmetic.</p></div>')
    # ---- tabella: chi paga che cosa
    def riga(nome, chi, aliq, su_cosa):
        return f'<tr><th scope="row">{nome}</th><td class="n">{aliq}</td><td>{chi}</td><td>{su_cosa}</td></tr>'
    righe = (riga("Federal income tax", "Employee (withheld)", "Tables", 'By Form W-4 and IRS Publication 15-T: see <a href="/federal-withholding/">federal withholding</a>')
             + riga("Social Security", "Employer and employee", f'{pct(F["ss"])} each', f'First {usd0(F["ss_base"])} of each employee’s wages')
             + riga("Medicare", "Employer and employee", f'{pct(F["medicare"])} each', f'All wages; the employee pays {pct(F["addl"])} more above {usd0(F["addl_soglia"])}')
             + riga("FUTA (federal unemployment)", "Employer", pct(FU["netta"] + rid),
                    f'First {usd0(FU["base"])}' + (f'; includes the {pct(rid)} credit reduction for {h(n)} in {ANNO}' if rid else '; after the full state credit'))
             + riga(f'{h(n)} {h(su["nome"])}', "Employer", pct(su["nuovo"]),
                    f'First {usd0(su["base"])}; rate for new employers' + (f', then {pct(su["min"])} to {pct(su["max"])}' if "min" in su else "")))
    if "ett" in su:
        righe += riga("Employment Training Tax (ETT)", "Employer", pct(su["ett"]), f'First {usd0(su["ett_base"])}')
    if st.get("sdi"):
        righe += riga("State Disability Insurance (SDI)", "Employee (withheld)", pct(st["sdi"]["aliquota"]), "All wages, no limit")
    if st["imposta_reddito"] is None:
        righe += riga(f"{h(n)} income tax", "–", "None", f"{h(n)} does not tax wages")
    elif s == "CA":
        righe += riga("California Personal Income Tax (PIT)", "Employee (withheld)", "1.1%–14.63%", f'By Form DE 4 and the EDD’s Method B: see the <a href="/{slug(s)}/">California paycheck calculator</a>')
    elif s == "IL":
        righe += riga("Illinois income tax", "Employee (withheld)", pct(st["imposta_reddito"]["aliquota"]), f'Pay after Form IL-W-4 allowances: see the <a href="/{slug(s)}/">Illinois paycheck calculator</a>')
    else:
        righe += riga("North Carolina income tax", "Employee (withheld)", pct(st["imposta_reddito"]["aliquota_ritenuta"]), f'Pay after the N.C. standard deduction and Form NC-4 allowances: see the <a href="/{slug(s)}/">North Carolina paycheck calculator</a>')
    fonti_tab = ",".join(dict.fromkeys(["irs_p15", su["fonte"]] + ([st["sdi"]["fonte"]] if st.get("sdi") else []) + ([st["imposta_reddito"]["fonte"]] if st["imposta_reddito"] else [])))
    corpo += f'<h2 id="rates">{h(n)} payroll taxes at a glance, {ANNO}</h2>'
    corpo += rim.t(f'<div class="tab"><table class="dati ampia" data-paghe-tab="{s}"><caption><span>Every payroll tax on wages paid in {h(n)} in {ANNO}, and who pays it.[[{fonti_tab}]]</span></caption>'
                   f'<thead><tr><th>Tax</th><th class="n">Rate</th><th>Who pays</th><th>Applies to</th></tr></thead><tbody>{righe}</tbody></table></div>')
    if s == "TX":
        corpo += ('<p class="small">The Texas rate shown is the entry-level rate TWC prints for new employers; whether its flat components of 0.32% come on top is discussed on the '
                  '<a href="/texas/#employer">Texas page</a>.</p>')
    # ---- costo di un dipendente
    voci = [("Social Security, employer share", d50["ss"]), ("Medicare, employer share", d50["medicare"]), ("FUTA", d50["futa"]), (f"{n} unemployment tax, new employer rate", d50["suta"])]
    if d50["ett"]:
        voci.append(("Employment Training Tax", d50["ett"]))
    costo = "".join(f'<tr><th scope="row">{h(a)}</th><td class="n">{usd(c)}</td></tr>' for a, c in voci)
    costo += (f'<tr><th scope="row">Employer payroll taxes for the year</th><td class="n"><b>{usd(d50["totale"])}</b></td></tr>'
              f'<tr><th scope="row">Wages plus payroll taxes</th><td class="n"><b>{usd(d50["costo"])}</b></td></tr>')
    corpo += f'<h2 id="cost">What a {usd0(50000)} employee costs in {h(n)}</h2>'
    corpo += (f'<div class="tab stretta"><table class="dati" data-costo="{s}"><caption><span>One employee paid {usd0(50000)} in {ANNO}, employer in its first years. Our arithmetic on the official rates; '
              f'workers’ compensation insurance and benefits are not included.</span></caption><tbody>{costo}</tbody></table></div>')
    corpo += (f'<div class="testo"><p>State unemployment tax and FUTA stop once the employee has earned the wage base, so they are paid in the first months of the year; Social Security and Medicare continue on every paycheck. '
              f'After the first years {h(n)} replaces the new-employer rate with one based on your own record: type the rate from your notice into the calculator above.</p></div>')
    # ---- iscrizione e dichiarazioni
    corpo += f'<h2 id="how">How to do payroll in {h(n)}: register, report, pay</h2>' + stato_iscrizione(s, rim)
    corpo += rim.t('<div class="testo"><p>The federal side is the same in every state: an EIN, a Form W-4 from each employee, deposits of the tax you withhold, Form 941 every quarter and Form 940 once a year. '
                   'The steps, with the IRS deadlines, are on <a href="/how-to-do-payroll/">how to do payroll yourself</a>.[[irs_p15]]</p></div>')
    corpo += riquadro_partner()
    # ---- lato dipendente
    tolto = [f"{usd(b['fed'])} federal income tax", f"{usd(b['ss'])} Social Security", f"{usd(b['medicare'])} Medicare"]
    if b["stato"]:
        tolto.append(f"{usd(b['stato'])} {n} income tax")
    if b["sdi"]:
        tolto.append(f"{usd(b['sdi'])} SDI")
    corpo += (f'<h2 id="withhold">What you withhold from {"an" if n[0] in "AEIOU" else "a"} {h(n)} paycheck</h2><div class="testo"><p>Example: {usd(200000)} gross every two weeks, federal filing status Single'
              + {"CA": ", California Single with no allowances", "IL": ", one Line 1 allowance on Form IL-W-4", "NC": ", N.C. Single with no allowances"}.get(s, "")
              + f', nothing else on the forms. You withhold {", ".join(tolto[:-1])} and {tolto[-1]}, and the employee takes home <strong>{usd(b["netto"])}</strong>. '
              f'For any other pay or form entries use the <a href="/{slug(s)}/">{h(n)} paycheck calculator</a>, which shows every line.</p></div>')
    fq, ld = faq_blocco(faq_paghe(s, d50), rim)
    corpo += fq
    corpo += (f'<h2>Payroll taxes in the other states</h2>{griglia_paghe(s)}'
              f'<p>All five states side by side: <a href="/employer-payroll-taxes/">employer payroll taxes {ANNO}</a>.</p>') + rim.elenco()
    sub = {"TX": "No state income tax to withhold. What a Texas employer pays, how to register with the Texas Workforce Commission and when the reports are due.",
           "FL": "No state income tax to withhold. What a Florida employer pays, how to register for reemployment tax and when Form RT-6 is due.",
           "CA": "Four state payroll taxes, two paid by the employer and two withheld from pay. Rates, EDD registration and the quarterly reports.",
           "IL": "Flat income tax to withhold and unemployment contributions paid by the employer. Rates, registration with IDOR and IDES, and what an employee costs.",
           "NC": "Income tax to withhold and unemployment tax paid by the employer. Rates, registration with NCDOR and DES, and the quarterly report."}[s]
    testata = banda(f"Employers · {n} · {ANNO}", f"{n} payroll taxes {ANNO}", h(sub), icona="build")
    desc = {"TX": f"Texas payroll taxes for {ANNO}: no state income tax, unemployment tax {pct(su['nuovo'])} on {usd0(su['base'])} for new employers, FICA and FUTA. TWC registration and due dates.",
            "FL": f"Florida payroll taxes for {ANNO}: no state income tax, reemployment tax {pct(su['nuovo'])} on {usd0(su['base'])} for new employers, FICA and FUTA. Form RT-6 due dates.",
            "CA": f"California payroll taxes for {ANNO}: UI {pct(su['nuovo'])} and ETT {pct(su.get('ett', 0))} paid by the employer, SDI and income tax withheld. EDD registration, DE 9 dates.",
            "IL": f"Illinois payroll taxes for {ANNO}: 4.95% income tax to withhold, unemployment rate {pct(su['nuovo'])} on {usd0(su['base'])} for new employers. IDOR and IDES registration.",
            "NC": f"North Carolina payroll taxes for {ANNO}: 4.09% withholding, unemployment tax {pct(su['nuovo'])} on {usd0(su['base'])} for new employers. NCDOR and DES registration."}[s]
    pagina(slug_paghe(s), f"{n} Payroll Taxes {ANNO}: Employer Rates and Due Dates", desc, corpo, testata,
           briciole=[("Home", ""), ("Employer payroll taxes", "employer-payroll-taxes/"), (n, slug_paghe(s))], jsonld=[ld], script_dati=script_dati())


def pagina_come_fare():
    rim = Rimandi()
    F, FU = G["fica"], G["futa"]
    b = motore.busta(R, caso("TX", 200000))
    fica_dip = b["ss"] + b["medicare"]
    deposito = b["fed"] + 2 * fica_dip
    corpo = '<div class="testo pull card">' + rim.t(
        f'<p>Payroll done by hand is the same handful of jobs repeated every payday, every quarter and every January. This page lists them in order for a small employer in {ANNO}, '
        'with the sentence of IRS Publication 15 behind each federal deadline and the state agency to register with in Texas, Florida, California, Illinois and North Carolina.[[irs_p15]]</p>'
        '<p class="small">A summary of the ordinary case (an employer that files Form 941), for general information: not tax, legal or payroll advice.</p>') + '</div>'
    corpo += '<h2 id="steps">The steps</h2><div class="testo">'
    corpo += '<h3>1. Get an Employer Identification Number (EIN)</h3><p>The IRS identifies every employer by its EIN. It goes on each deposit and return.</p>' + rim.cit("irs_p15", "ein")
    corpo += ('<h3>2. Register with your state</h3><p>Each state has its own account for unemployment tax and, where wages are taxed, a second one for income tax withholding. '
              'The table of the five states is <a href="#states">below</a>.</p>')
    corpo += ('<h3>3. Take a Form W-4 and report the new hire</h3><p>Each employee fills in a federal Form W-4 (and the state form in California, Illinois and North Carolina); their entries decide how much income tax you withhold. '
              'Then the hire is reported to the state:</p>') + rim.cit("irs_p15", "nuovi_assunti")
    corpo += rim.t(f'<h3>4. Work out each paycheck</h3><p>From gross pay you withhold federal income tax (Worksheet 1A of Publication 15-T), {pct(F["ss"])} Social Security up to {usd0(F["ss_base"])} of wages in the year, '
                   f'{pct(F["medicare"])} Medicare and any state income tax. As the employer you owe the same Social Security and Medicare again.[[irs_p15t,irs_p15]] '
                   'The <a href="/">paycheck calculator</a> does the employee’s side line by line; the <a href="/federal-withholding/">federal withholding page</a> shows the tables.</p>')
    corpo += '<h3>5. Deposit the federal taxes</h3><p>The income tax you withheld and both halves of Social Security and Medicare are deposited together, electronically:</p>' + rim.cit("irs_p15", "eft")
    corpo += '<p>How often depends on the taxes you reported in an earlier 12-month “lookback period”:</p>' + rim.cit("irs_p15", "lookback")
    corpo += '<p>For a new business the taxes of the lookback period count as zero, so the publication says:</p>' + rim.cit("irs_p15", "primo_anno") + rim.cit("irs_p15", "mensile")
    corpo += '<p>For the larger employers on the other schedule:</p>' + rim.cit("irs_p15", "semisett")
    corpo += '<h3>6. File Form 941 every quarter</h3><p>Form 941 reports the wages paid and the taxes withheld and deposited in the quarter.</p>' + rim.cit("irs_p15", "f941")
    corpo += f'<p>So the four dates are {SCADENZE_TRIM}; a date on a weekend or legal holiday moves to the next business day.</p>'
    corpo += '<h3>7. Pay FUTA and file Form 940 once a year</h3>' + rim.cit("irs_p15", "futa") + rim.cit("irs_p15", "futa_credito") + rim.cit("irs_p15", "f940_500")
    corpo += (f'<p>After the full credit FUTA is {pct(FU["netta"])} of the first {usd0(FU["base"])}: {usd(motore.quota(FU["base"] * 100, motore.m(FU["netta"])))} per employee, '
              f'or {usd(motore.quota(FU["base"] * 100, motore.m(FU["netta"] + FU["riduzione_credito"]["CA"])))} in California in {ANNO} because of the credit reduction. '
              'Details on the <a href="/employer-payroll-taxes/">employer payroll taxes page</a>.</p>')
    corpo += ('<h3>8. File the state report every quarter</h3><p>All five states want a quarterly wage report with the unemployment tax; the three with an income tax also want the tax you withheld. See the table below.</p></div>')
    # ---- una busta paga svolta
    corpo += (f'<h2 id="example">One payday, worked through</h2><div class="testo"><p>One employee in Texas, {usd(200000)} gross every two weeks, Form W-4 marked Single with nothing else filled in, {ANNO}.</p>'
              '<ul class="passi">'
              f'<li>Withhold federal income tax: <b>{usd(b["fed"])}</b></li>'
              f'<li>Withhold Social Security {pct(F["ss"])}: <b>{usd(b["ss"])}</b> and Medicare {pct(F["medicare"])}: <b>{usd(b["medicare"])}</b></li>'
              f'<li>Pay the employee: {usd(200000)} − {usd(b["totale"])} = <b>{usd(b["netto"])}</b></li>'
              f'<li>Add your own share of Social Security and Medicare: <b>{usd(fica_dip)}</b></li>'
              f'<li>Owed to the IRS for this payday: {usd(b["fed"])} + {usd(fica_dip)} + {usd(fica_dip)} = <b>{usd(deposito)}</b>, deposited by the 15th of the following month on the monthly schedule</li></ul>'
              '<p>State unemployment tax and FUTA are worked out on the same wages but paid separately: use the calculator at the bottom of the page.</p></div>')
    # ---- scadenze
    corpo += '<h2 id="due">When payroll taxes are due</h2>'
    righe = (f'<tr><th scope="row">Federal deposit, monthly schedule</th><td>15th day of the following month</td><td>Income tax withheld, Social Security and Medicare</td></tr>'
             f'<tr><th scope="row">Federal deposit, semiweekly schedule</th><td>The following Wednesday or Friday, by payday</td><td>The same taxes, for employers above $50,000 in the lookback period</td></tr>'
             f'<tr><th scope="row">Form 941</th><td>{SCADENZE_TRIM}</td><td>Quarterly return</td></tr>'
             f'<tr><th scope="row">Form 940 and FUTA</th><td>January 31</td><td>Yearly return; deposit when the amount owed is over $500</td></tr>')
    corpo += rim.t('<div class="tab"><table class="dati ampia" data-scadenze><caption><span>Federal dates from IRS Publication 15; a date on a weekend or legal holiday moves to the next business day.[[irs_p15]]</span></caption>'
                   f'<thead><tr><th>What</th><th>Due</th><th>Covers</th></tr></thead><tbody>{righe}</tbody></table></div>')
    # ---- Stati
    corpo += '<h2 id="states">Where to register and what to file in the five states</h2>'
    stati_r = {
        "TX": ("Texas Workforce Commission, within ten days of becoming liable", "None: no state income tax", f"Wage report and tax by {SCADENZE_TRIM}, online", "tx_ut,tx_filing"),
        "FL": ("Florida Department of Revenue (reemployment tax)", "None: no state income tax", f"Form RT-6, late after {SCADENZE_TRIM}", "fl_rt,fl_return"),
        "CA": ("EDD, within 15 days of paying more than $100 in wages in a quarter", "Personal Income Tax and SDI, same EDD account", "DE 9 and DE 9C every quarter; UI and ETT paid quarterly", "ca_step1,ca_step5,ca_step6"),
        "IL": ("IDES, through MyTax Illinois", "Department of Revenue (IDOR), through MyTax Illinois", "UI contribution and wage report, monthly or quarterly", "il_idor_reg,il_ides_tax"),
        "NC": ("Division of Employment Security (NCSUITS account)", "Department of Revenue, Form NC-BR", "Quarterly Tax and Wage Report; withholding quarterly, monthly or semiweekly", "nc_required,nc_quarterly,nc_30"),
    }
    righe = "".join(f'<tr data-stato="{s}"><th scope="row"><a href="/{slug_paghe(s)}">{h(nome_stato(s))}</a></th><td>{h(v[0])}{rim.ref(v[3])}</td><td>{h(v[1])}</td><td>{h(v[2])}</td></tr>' for s, v in stati_r.items())
    corpo += ('<div class="tab"><table class="dati ampia" data-stati-paghe><caption><span>From each state agency’s own pages; the state pages quote the sentences.</span></caption>'
              f'<thead><tr><th>State</th><th>Unemployment tax account</th><th>Income tax withholding account</th><th>State reports</th></tr></thead><tbody>{righe}</tbody></table></div>')
    corpo += f'<h2 id="cost">What the employer pays on top of wages</h2><div style="margin-top:14px">{calcolatore_datore("TX")}</div>' + riquadro_partner()
    corpo += ('<h2 id="not-covered">What this page leaves out</h2><ul class="testo">'
              '<li>Form I-9 and checking that a new employee may work in the United States.</li>'
              '<li>Year-end forms: Form W-2 for each employee and Form W-3.</li>'
              '<li>The $100,000 next-day deposit rule, Form 944 for the smallest employers, and farm or household employees.</li>'
              '<li>Deposit schedules for state income tax withholding, local taxes, workers’ compensation insurance and benefits.</li>'
              '<li>Wage and hour law: minimum wage, overtime, pay frequency and pay stub rules.</li></ul>')
    faq = [
        ("how to do payroll", "How do I do payroll myself?",
         "Get an EIN, register with your state, take a Form W-4 from each employee, and on every payday withhold federal income tax, Social Security, Medicare and any state tax. "
         "Deposit the federal taxes on your schedule, file Form 941 every quarter and Form 940 once a year, file the state reports, and give each employee a Form W-2 after the year ends.", "irs_p15"),
        ("how to calculate payroll taxes", "How do you calculate payroll taxes?",
         f"For each paycheck in {ANNO}: {pct(F['ss'])} of gross pay for Social Security (up to {usd0(F['ss_base'])} of wages in the year) and {pct(F['medicare'])} for Medicare, withheld from the employee and paid again by the employer; "
         f"federal income tax from the Form W-4 and the tables in IRS Publication 15-T; then state tax. Example: on {usd(200000)} every two weeks, single filer in Texas, {usd(b['fed'])} income tax, {usd(b['ss'])} Social Security and {usd(b['medicare'])} Medicare are withheld.", "irs_p15,irs_p15t"),
        ("how to pay payroll taxes", "How do I pay payroll taxes to the IRS?",
         "By electronic funds transfer: IRS Publication 15 says you must use EFT to make all federal tax deposits, for example through the Electronic Federal Tax Payment System (EFTPS). "
         "The deposit covers the income tax withheld and both the employee and employer shares of Social Security and Medicare.", "irs_p15"),
        ("when are payroll taxes due", "When are payroll taxes due?",
         f"On the monthly schedule, federal deposits are due by the 15th day of the following month. Form 941 is due by the last day of the month after each quarter ({SCADENZE_TRIM}) and Form 940 by January 31. "
         "State unemployment tax reports are quarterly in Texas, Florida, California and North Carolina, and monthly or quarterly in Illinois.", "irs_p15,tx_ut,fl_return,ca_step6,il_ides_tax,nc_quarterly"),
        ("payroll tax deposit schedule", "What is the payroll tax deposit schedule?",
         "There are two. If you reported $50,000 or less of taxes in the lookback period you are a monthly schedule depositor and deposit by the 15th of the following month; above $50,000 you are a semiweekly schedule depositor. "
         "A new business is a monthly schedule depositor for its first calendar year.", "irs_p15"),
        ("form 941", "What is Form 941 and when is it due?",
         f"Form 941 is the quarterly federal return on which an employer reports wages, the income tax withheld and Social Security and Medicare taxes. It must be filed by the last day of the month that follows the end of the quarter: {SCADENZE_TRIM}.", "irs_p15"),
        ("form 940", "What is Form 940?",
         f"Form 940 is the yearly return for FUTA, the federal unemployment tax paid only by employers: {pct(FU['aliquota'])} on the first {usd0(FU['base'])} of each employee’s wages, {pct(FU['netta'])} after the full credit for state unemployment tax. Its due date is January 31.", "irs_p15"),
        ("how to do payroll yourself", "Can a small business do payroll without software?",
         "Yes. The IRS publishes the worksheet and tables for working out withholding by hand, and the deposits and returns can be made on the IRS and state websites. "
         "What it takes is time and care with deadlines: a late deposit or return can bring penalties.", "irs_p15t,irs_p15"),
    ]
    fq, ld = faq_blocco(faq, rim)
    corpo += fq + f'<h2>Payroll taxes by state</h2>{griglia_paghe()}' + rim.elenco()
    testata = banda(f"Employers · {ANNO}", f"How to do payroll yourself, {ANNO}",
                    "The jobs a small employer repeats every payday, every quarter and every January: what to withhold, when to deposit it and which forms to file, from IRS Publication 15.", icona="build")
    pagina("how-to-do-payroll/", f"How to Do Payroll Yourself in {ANNO}: Steps, Taxes, Due Dates",
           f"How to do payroll for a small business in {ANNO}: EIN, Form W-4, what to withhold, when to deposit, Form 941 and Form 940, with IRS quotes and a worked payday.",
           corpo, testata, briciole=[("Home", ""), ("Employer payroll taxes", "employer-payroll-taxes/"), ("How to do payroll", "how-to-do-payroll/")], jsonld=[ld], script_dati=script_dati())


# ---------------------------------------------------------------- ritenuta federale
def pagina_federale():
    rim = Rimandi()
    F = G["fica"]
    g1 = G["federale"]["riga_1g"]
    corpo = '<div class="testo pull card">' + rim.t(
        f'<p>Employers work out federal income tax withholding from IRS Publication 15-T. For payroll software the publication gives one worksheet (Worksheet 1A) and one pair of yearly tables. '
        f'This page shows both for {ANNO} and works through an example.[[irs_p15t]]</p>') + '</div>'
    corpo += '<h2>The worksheet, step by step</h2><div class="testo">' + rim.cit("irs_p15t", "uso")
    corpo += ('<ol class="steps"><li><strong>Make it yearly.</strong> Multiply the taxable wages of the pay period by the number of pay periods (52, 26, 24 or 12).</li>'
              f'<li><strong>Adjust.</strong> Add the other income from Step 4(a) of Form W-4, subtract the deductions from Step 4(b), then subtract {usd0(g1["altro"])} ({usd0(g1["mfj"])} if married filing jointly). If the Step 2 box is checked, subtract nothing here.</li>'
              '<li><strong>Read the table.</strong> Find the row for the adjusted yearly wage: the tentative amount, plus the percentage of the amount over the start of the row.</li>'
              '<li><strong>Divide</strong> by the number of pay periods.</li>'
              '<li><strong>Credits.</strong> Subtract the Step 3 amount divided by the number of pay periods; the result cannot go below zero.</li>'
              '<li><strong>Extra.</strong> Add any extra withholding from Step 4(c).</li></ol>')
    corpo += rim.cit("irs_p15t", "1g") + rim.cit("irs_p15t", "2h") + rim.cit("irs_p15t", "3c") + rim.cit("irs_p15t", "4b")
    es = caso("TX", 300000, periodo="semimonthly", fs="mfj", step3=400000)
    passi, f = passi_federali(es)
    P = 24
    cred = motore.mezzo(es["step3"], P)
    corpo += (f'<h3>Worked example</h3><p>{usd(es["lordo"])} twice a month, married filing jointly, Step 2 box not checked, {usd(es["step3"])} of credits for dependents in Step 3.</p>{passi}'
              f'<ul class="passi"><li>3a–3c. Credits {usd(es["step3"])} ÷ {P} = {usd(cred)}; {usd(f["tentativo"])} − {usd(cred)} = <b>{usd(f["ritenuta"])}</b> withheld per paycheck</li></ul>')
    corpo += '<h3>Rounding</h3>' + rim.cit("irs_p15t", "arrotonda") + '<p>We keep cents and round each worksheet line to the cent (lines 2h and 3b above), so a pay stub from an employer that rounds to whole dollars can differ from our figure by up to 50 cents, and payroll software that carries more decimals by a cent.</p></div>'
    corpo += f'<h2 id="tables">{ANNO} percentage method tables for automated payroll systems</h2><p class="small">Yearly amounts. Copied from Publication 15-T, section 1.</p>'
    corpo += '<h3>Standard withholding (Step 2 box not checked)</h3>'
    nomi = {"mfj": "Married filing jointly", "single": "Single or married filing separately", "hoh": "Head of household"}
    for k in ("mfj", "single", "hoh"):
        corpo += tabella_fed("std", k, f"{nomi[k]}, standard withholding rate schedule, {ANNO}")
    corpo += '<h3>Form W-4, Step 2 box checked</h3>'
    for k in ("mfj", "single", "hoh"):
        corpo += tabella_fed("step2", k, f"{nomi[k]}, Step 2 checkbox withholding rate schedule, {ANNO}")
    corpo += '<h2>Social Security and Medicare</h2><div class="testo">' + rim.cit("irs_p15", "ss") + rim.cit("irs_p15", "medicare") + rim.cit("irs_p15", "addl") + '</div>'
    corpo += ('<h2>2027</h2><div class="testo">' + rim.t(f'<p>As of {data_lunga(CONTROLLO)} the IRS has posted only an early release draft of Publication 15-T for 2027, without the tables in the text. '
              'A draft can still change, so this site stays on the final 2026 publication until the final 2027 one is out.[[irs_p15t_2027]]</p>') + rim.cit("irs_p15t_2027", "tabelle")
              + '<p>We could not read the Social Security Administration’s website (it refuses our checking server), so we show no 2027 wage base until an IRS publication prints it.</p></div>')
    faq = [
        ("what is federal withholding", "What is federal withholding?",
         "It is the federal income tax your employer takes out of each paycheck and sends to the IRS on your behalf. The amount depends on your pay, how often you are paid and what you entered on Form W-4. It is a prepayment: your tax return settles the difference.", "irs_p15t"),
        ("how to calculate federal withholding", "How do you calculate federal withholding?",
         f"With Worksheet 1A of IRS Publication 15-T: multiply the pay by the number of pay periods, add and subtract the Form W-4 Step 4 amounts, subtract {usd0(g1['altro'])} ({usd0(g1['mfj'])} if married filing jointly), read the yearly tax from the table for the filing status, divide by the number of pay periods, then subtract the Step 3 credits and add any extra withholding.", "irs_p15t"),
        ("federal income tax withholding tables", f"Where are the federal income tax withholding tables for {ANNO}?",
         f"In IRS Publication 15-T for {ANNO}. Section 1 has the percentage method tables for automated payroll systems, shown on this page; sections 2 to 5 have wage bracket and percentage tables for payroll done by hand.", "irs_p15t"),
        ("how much is social security tax", "How much is Social Security tax on a paycheck?",
         f"{pct(F['ss'])} of gross wages, until your wages for the year reach {usd0(F['ss_base'])} in {ANNO}. On a {usd(200000)} paycheck that is {usd(motore.quota(200000, motore.m(F['ss'])))}.", "irs_p15"),
    ]
    fq, ld = faq_blocco(faq, rim)
    corpo += fq + f'<p style="margin-top:22px"><a class="btn" href="/">{ico("calc")}Open the paycheck calculator</a></p>' + rim.elenco()
    testata = banda(f"IRS Publication 15-T · {ANNO}", f"Federal withholding {ANNO}: the IRS tables and how to calculate it",
                    "The worksheet payroll software uses, the yearly tables for every filing status and a worked example.", corta=True, icona="table")
    pagina("federal-withholding/", f"Federal Withholding {ANNO}: IRS Tables and How to Calculate",
           f"How federal income tax withholding is calculated in {ANNO}: Worksheet 1A of IRS Publication 15-T, the percentage method tables and a worked example.",
           corpo, testata, briciole=[("Home", ""), ("Federal withholding", "federal-withholding/")], jsonld=[ld])


# ---------------------------------------------------------------- pagine di servizio
MODULO = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card" data-correzioni>
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or figure<input type="text" name="page" required maxlength="300" placeholder="For example /california/, SDI rate"></label>
<label>What is wrong?<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<p class="small">Please do not include your name, email address, pay details or other personal information: the form does not ask for them and we do not reply to messages.</p>
<p class="errore" data-errore hidden>The message was not sent. Please try again.</p>
<button type="submit" class="btn">Send correction</button>
</form>
<p class="ok" data-ok hidden><strong>Thank you.</strong> We will check it against the official source.</p>"""


def come_controlliamo():
    rim = Rimandi()
    ufficiali = {k: f for k, f in FONTI.items() if k not in FONTI_PARTNER}   # le pagine dei programmi di affiliazione non sono documenti ufficiali
    n_frasi = sum(len(f["frasi"]) for f in ufficiali.values())
    corpo = ('<div class="testo pull card">'
             f'<p>A mistake in a paycheck calculator is a mistake about someone’s money. So every rate, threshold and table on this site is read from an official document that we download and keep, '
             f'and the calculator is tested against a second, separately written calculation before the site is built.</p></div>')
    corpo += '<h2>Where the figures come from</h2><div class="testo"><ul>'
    corpo += rim.t(f'<li>We download each official document ({len(ufficiali)} files: IRS publications, state withholding booklets, state unemployment agency pages, the Department of Labor’s FUTA list) and record its address, the date and a fingerprint (SHA-256): of the whole file for PDFs and spreadsheets, of the quoted sentences for web pages, whose code changes at every download.</li>'
                   f'<li>The federal tables are read from Publication 15-T, section 1: six tables of eight rows. The build stops unless the rows join up and each “tentative amount” equals the tax on the rows before it.[[irs_p15t]]</li>'
                   f'<li>California’s twelve rate tables, the low income exemption, standard deduction, estimated deduction and exemption allowance tables are read from the EDD’s Method B schedule, with the same joining-up check.[[ca_methb]]</li>'
                   f'<li>Every sentence shown in a quotation box is copied word for word from the source and searched for in the downloaded file each time ({n_frasi} sentences). If one is no longer there, the build stops.</li></ul></div>')
    corpo += '<h2>How the calculator is tested</h2><div class="testo"><ul>'
    corpo += rim.t('<li>The calculator in your browser works in whole cents. A second program, written separately with exact fractions and its own reading of the official tables, computes the same paychecks; '
                   'the two must agree to the cent on at least 500 random cases for each state, including pay near the Social Security wage base and the Additional Medicare Tax threshold.</li>'
                   '<li>Ten cases worked out by hand, line by line, must match.</li>'
                   '<li>The agencies’ own printed examples must come out exactly: Examples A to D of California’s Method B, the Illinois booklet’s example and the North Carolina NC-30 example.[[ca_methb,il_700t,nc_30]]</li>'
                   '<li>Every figure in the example tables and employer tables on the pages is recomputed and compared.</li></ul></div>')
    corpo += ('<h2>What we could not read or did not include</h2><div class="testo"><ul>'
              '<li>The Social Security Administration’s website refuses our checking server. We do not try to get round such blocks: the wage base comes from IRS Publication 15, which prints it.</li>'
              '<li>This is a five-state pilot. Other states are not covered, and neither are local income taxes.</li>'
              '<li>California’s annual and daily tables, Forms W-4 from before 2020, supplemental wages and nonresident alien rules are not in the calculator.</li>'
              '<li>For Texas, the pages we read do not say whether a new employer pays the flat components (0.32% in all) on top of the 2.7% entry-level rate; the Texas page shows both figures and the calculator lets you type your own rate.</li>'
              '<li>Florida’s range of rates for experienced employers is not on the page we read.</li></ul></div>')
    corpo += ('<h2>When we update</h2><div class="testo"><p>The IRS publishes the final Publication 15-T for the new year in December, and the states publish their new tables between November and January. '
              'The site moves to a new year only when the final documents are out and all the checks above pass again.</p></div>')
    corpo += ('<h2 id="corrections">Report an error</h2><div class="testo"><p>Seen a figure that does not match the official document? Tell us which page and, if you can, link the source: we check it and fix the page. '
              'We cannot answer questions about an individual paycheck or tax situation.</p></div>' + MODULO)
    corpo += rim.elenco()
    testata = banda("How we check", "How we check every figure", "Official documents kept on file, quotations checked word for word and a second calculation that must agree to the cent.", corta=True, icona="shield")
    pagina("how-we-check/", "How We Check the Paycheck Calculator and Its Sources",
           f"How {NOME} reads the official IRS and state documents, checks quotations word for word and tests the calculator against a second calculation.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")])


def about():
    aff = ('<p>Some pages may also carry a clearly marked affiliate link to a payroll software company; if you sign up through it we may earn a commission. It never changes the figures.</p>' if PARTNER else "")
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{NOME}</strong> is an independent publication, part of a small network of websites that turn official data into plain-language reference pages and calculators. '
             f'It estimates take-home pay and employer payroll taxes for {ANNO} in five states, from the official withholding formulas.</p>'
             '<p>We are <strong>not affiliated with</strong> the IRS, the Social Security Administration, the Department of Labor or any state agency, and we are not accountants or tax advisers. '
             'The site gives general information and estimates, not tax, legal or payroll advice.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Only rates, thresholds and formulas printed in official documents, each linked to its source and quoted word for word where it matters.</li>'
             '<li>Arithmetic on those figures (the paycheck estimates and the examples), always labelled as ours.</li>'
             '<li>Where an official source cannot be read, or a rule is not covered, we say so instead of filling the gap.</li></ul>'
             f'<h2>How the site is paid for</h2><div class="testo"><p>The site shows advertising served by Google AdSense. Advertisers never decide what we publish.</p>{aff}</div>'
             '<h2>Corrections</h2><div class="testo"><p>If a figure does not match the official document, use the <a href="/how-we-check/#corrections">corrections form</a>. For questions about your own pay, '
             'ask your employer’s payroll office or a tax professional: they have your records.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, what it publishes and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", f"About {NOME}: an independent site estimating take-home pay and employer payroll taxes from official IRS and state formulas.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")])


def privacy():
    con_aff = bool(PARTNER)
    cookie = MON.privacy_cookie("en", SITO_ID, con_aff) or ("<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. This site shows no advertising.</p>")
    california = MON.frase_california(SITO_ID) or "California residents: we do not sell or share personal information."
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {NOME} ({URL_SITO.replace("https://", "")}) collects. In short: very little.</p></div>'
             '<div class="testo"><h2>The calculators</h2><p>The calculators run in your browser. The pay, the Form W-4 entries and everything else you type stay on your device: they are not sent to us or stored.</p>'
             '<p>The site remembers your choice of light or dark theme in your browser (local storage).</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             '<h2 id="corrections">Corrections form</h2><p>The <a href="/how-we-check/#corrections">corrections form</a> asks for the page, your message and, if you wish, a link to the official source. '
             'It does not ask for your name or email address, and we ask you not to put personal or pay details in the message. The form is processed by Netlify Forms on our behalf. '
             'We use what you send only to check the figure and delete it once that is done. There are no accounts, newsletters or comments on this site.</p>'
             f'<h2>California</h2><p>{california}</p>'
             f'<h2>Changes</h2><p>Last update: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID, con_aff) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", f"Privacy | {NOME}", f"Privacy at {NOME}: the calculators run in your browser, a cookie-free visit counter, and Google AdSense advertising with consent.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = f'<div class="pull card"><p>The page you asked for does not exist. Try the <a href="/">paycheck calculator</a>, <a href="/employer-payroll-taxes/">employer payroll taxes</a> or a state below.</p></div><div style="margin-top:18px">{griglia_stati()}</div>'
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
  # Pubblica solo se è cambiato qualcosa in paycheck/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = paycheck/sito, Build command vuoto, Publish directory = "."
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
    if sorted(G["stati"]) != sorted(STATI):
        raise SystemExit("regole.json: Stati diversi da quelli delle pagine")
    if date.today().year > ANNO:
        print(f"ATTENZIONE: le tabelle sono del {ANNO}. Aggiornare alle tabelle {ANNO + 1} (vedi NOTE.md).")


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
    pagina_datore()
    for s in STATI:
        pagina_paghe_stato(s)
    pagina_come_fare()
    pagina_federale()
    come_controlliamo()
    about()
    privacy()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404. Partner accesi: {', '.join(p['id'] for p in PARTNER) or 'nessuno (riquadro spento)'}.")


if __name__ == "__main__":
    main()
