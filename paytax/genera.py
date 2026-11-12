"""Genera il sito statico "Payroll Tax by State" (Australia, inglese) in paytax/sito/.

Uso (dalla radice del repository):
    python3 paytax/raccolta/fonti.py     # rilegge le fonti ufficiali -> dati/fonti.json (HTTP, impronta, frasi trovate)
    python3 paytax/raccolta/domanda.py   # ricerche vere (autocompletamento Google gl=au) -> dati/domanda.json
    python3 paytax/genera.py             # pagine in paytax/sito/
    python3 paytax/verifica.py           # controlli (aggiungere --rete per rileggere le fonti, --browser per Playwright)

Dati: dati/giurisdizioni.json (parametri 2026-27 e fatti per Stato), dati/storico.json, dati/esempi_ufficiali.json,
dati/faq.json, dati/affiliati.json (riquadri preparati ma spenti), dati/fonti.json (scritto da raccolta/fonti.py).
Il calcolatore gira solo nel browser (stile.MOTORE_JS = copia di motore.py). Nessun dato personale.
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

URL_SITO = "https://payrolltaxbystate.com"  # unico punto da cambiare se il nome del sito su Netlify è diverso
NOME = "Payroll Tax by State"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "paytax"  # nome del sito in monetizzazione.json
ADSENSE_HEAD = MON.script_adsense(SITO_ID)


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


GJ = carica("giurisdizioni.json")
P = GJ["parametri"]
J = GJ["giurisdizioni"]
ANNO = GJ["anno_fiscale"]
GIORNI_ANNO = GJ["giorni_anno"]
CONTROLLO = date.fromisoformat(GJ["controllato_il"])
_F = carica("fonti.json")
FONTI = _F["definizioni"]
ESITI = _F["fonti"]
STORICO = carica("storico.json")
ESEMPI = carica("esempi_ufficiali.json")
FAQ = carica("faq.json")["faq"]
AFF = carica("affiliati.json")
ORDINE = motore.ORDINE
OGGI = date.today()

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def soldi(x, cent=False):
    if cent:
        return f"${x:,.2f}"
    return f"${x:,.0f}"


def pct(frac, dec=None):
    v = frac * 100
    if dec is None:
        t = f"{v:.4f}".rstrip("0").rstrip(".")
    else:
        t = f"{v:.{dec}f}"
    return t + "%"


def mln(x):
    """1500000 -> $1.5m, 10400000 -> $10.4m, 1250000 -> $1.25m."""
    v = x / 1e6
    t = f"{v:.2f}".rstrip("0").rstrip(".")
    return f"${t}m"


# ---------------------------------------------------------------- fonti e rimandi numerati
class Rimandi:
    """Numera le fonti citate in una pagina nell'ordine in cui compaiono; [[id,id]] nei testi diventa [1],[2]."""

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
        """Sostituisce i segni [[id,id]] con i rimandi numerati (il testo è HTML scritto da noi)."""
        return re.sub(r"\[\[([a-z0-9_, ]+)\]\]", lambda m: self.ref(m.group(1)), testo)

    def elenco(self):
        if not self.ordine:
            return ""
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = FONTI[i]
            es = ESITI.get(i, {})
            if f.get("non_letta"):
                stato = f"not readable from our checking server: {h(f['motivo'])}"
            elif es.get("http") == 200:
                agg = f"; page says “{h(es['aggiornata'])}”" if es.get("aggiornata") else ""
                stato = f"checked {data_lunga(es['letto_il'])}{agg}"
            else:
                stato = f"last check failed (HTTP {h(es.get('http'))})"
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. <span class="small">{stato}</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2>'
                f'<ol>{"".join(voci)}</ol><p class="small">Every figure on this page comes from the official pages above. We re-read them with '
                f'<a href="/how-we-check/">the checks described here</a>; if a page changes, the figure is re-checked before it stays on the site.</p></section>')


def ufficio_con_articolo(g):
    """'Revenue NSW', 'RevenueSA', 'RevenueWA (...)' senza articolo; gli altri uffici con 'the'."""
    return g["ufficio"] if g["ufficio"].startswith("Revenue") else "the " + g["ufficio"]


def url_fonte(i):
    return FONTI[i]["url"]


# ---------------------------------------------------------------- risorse
def _impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:10]


CSS = re.sub(r"\n", "", stile.CSS)
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in stile.ICONE.items()) + "</svg>\n")
ICONS_FILE = f"icons.{_impronta(SPRITE)}.svg"
APP_JS = stile.APP_JS.strip() + "\n"
ASSET = {
    f"site.{_impronta(CSS)}.css": CSS,
    f"app.{_impronta(APP_JS)}.js": APP_JS,
    f"favicon.{_impronta(stile.FAVICON_SVG)}.svg": stile.FAVICON_SVG,
    ICONS_FILE: SPRITE,
}
CSS_FILE, JS_FILE, FAVICON_FILE, _ = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="34" height="34" alt="">'


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
MENU = [("calculator/", "Calculator"), ("#stati", "States"), ("interstate-wages/", "Interstate"), ("due-dates/", "Due dates"),
        ("payday-super/", "Payday Super")]
MENU_M = [("calculator/", "Calculator"), ("interstate-wages/", "Interstate wages"), ("due-dates/", "Due dates"), ("payday-super/", "Payday Super")]
DISCLAIMER = ("<strong>General information, not tax advice.</strong> Figures and formulas are taken from the official revenue office pages and legislation "
              "linked on each page. Payroll tax depends on facts this site cannot check (what counts as wages, exemptions, grouping, contractors). "
              "Confirm your liability with the revenue office of each state where you pay wages, or with a registered tax agent.")


def menu_html(percorso, mobile=False):
    voci = []
    for u, t in (MENU_M if mobile else MENU):
        if u == "#stati":
            continue
        voci.append(f'<a href="/{u}"' + (' aria-current="page"' if u == percorso else "") + f">{h(t)}</a>")
    if mobile:
        voci.append('<span class="sep" aria-hidden="true"></span>')
        voci += [f'<a href="/{s}/">{h(J[s]["breve"])} · {h(J[s]["nome"].split()[-1] if s in ("act", "nt") else J[s]["nome"])}</a>' for s in ORDINE]
    else:
        voci.insert(1, '<a href="/#states">States</a>')
    return "".join(voci)


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append((percorso, CONTROLLO.isoformat()))
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": i, "name": n, "item": f"{URL_SITO}/{p}"} for i, (n, p) in enumerate(briciole, 1)]
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb">' + " › ".join(
            [f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    corpo_tr = corpo + MON.riga_trasparenza(corpo, "en")
    stati_piede = "".join(f'<li><a href="/{s}/">{h(J[s]["nome"])}</a></li>' for s in ORDINE)
    guide_piede = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [
        ("calculator/", "Multi-state calculator"), ("interstate-wages/", "Interstate wages"), ("grouping/", "Grouping"),
        ("regional-rates/", "Regional rates"), ("thresholds-history/", "Thresholds history"), ("due-dates/", "Due dates"),
        ("what-changed-2026-27/", "What changed in 2026-27"), ("payday-super/", "Payday Super"), ("over-the-threshold/", "Over the threshold"),
        ("about/", "About"), ("how-we-check/", "How we check"), ("privacy/", "Privacy")])
    testo = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
<title>{h(titolo)}</title>
<meta name="description" content="{h(descrizione)}">
{f'<link rel="canonical" href="{url_pag}">' if indicizza else '<meta name="robots" content="noindex">'}
<meta property="og:title" content="{h(titolo)}">
<meta property="og:description" content="{h(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:locale" content="en_AU">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0C2F2B">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Payroll Tax <b>by State</b></span></a>
<nav class="menu" aria-label="Main">{menu_html(percorso)}</nav>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Menu">{ico("menu")}</summary><nav aria-label="Main">{menu_html(percorso, mobile=True)}</nav></details>
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
<a class="logo" href="/">{LOGO}<span>Payroll Tax <b>by State</b></span></a>
<p><strong>{NOME}</strong> compares Australian payroll tax in all eight states and territories and estimates your tax with the formulas published by
the revenue offices and in the payroll tax Acts. It is an independent site, not a government website and not linked to any revenue office.</p>
<p>Rates for the {ANNO} financial year (1 July 2026 to 30 June 2027). Official sources checked on {data_lunga(CONTROLLO)}.</p>
</div><div>
<h2>States and territories</h2><ul>{stati_piede}</ul>
</div><div>
<h2>Guides</h2><ul>{guide_piede}</ul>
</div></div>
<p class="f-base">General information only, not tax, legal or financial advice. Payroll tax is administered by each state and territory revenue office:
<a href="https://www.payrolltax.gov.au/" rel="noopener">payrolltax.gov.au</a> lists them all.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="scale"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def trust():
    v = [("check", "Official figures only, each with its source"), ("scale", "Formulas from the payroll tax Acts"),
         ("lock", "Runs in your browser: nothing is sent")]
    return '<ul class="trust">' + "".join(f"<li>{ico(i)}{h(t)}</li>" for i, t in v) + "</ul>"


def faq_blocco(pagina_id, rim, titolo="Common questions"):
    voci = [x for x in FAQ if x["pagina"] == pagina_id]
    if not voci:
        return "", None
    blocchi, ld = [], []
    for x in voci:
        blocchi.append(f'<div class="faq"><h3>{h(x["q"])}</h3><p>{h(x["a"])}{rim.ref(x["fonti"])}</p></div>')
        ld.append({"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": x["a"]}})
    html_ = f'<h2 id="faq">{h(titolo)}</h2><p class="small">Questions people in Australia search for, answered from the official sources.</p>' + "".join(blocchi)
    return html_, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


# ---------------------------------------------------------------- affiliazione (preparata, spenta)
def ci_sono_affiliati():
    return any(v.get("attivo") and (v.get("url") or "").startswith("https://") for k, v in AFF.items() if not k.startswith("_"))


def box_affiliati(contesto, aff=None, titolo_h="h2"):
    """Riquadro dei programmi (Employment Hero, poi MYOB): '' finché i programmi non sono attivi con un URL vero."""
    aff = aff if aff is not None else AFF
    voci = [v for k, v in aff.items() if not k.startswith("_") and v.get("attivo") and (v.get("url") or "").startswith("https://")
            and (contesto in v.get("pagine", []) or (contesto in ORDINE and "stati" in v.get("pagine", [])))]
    if not voci:
        return ""
    righe = "".join(f'<li><a href="{h(v["url"])}" rel="sponsored noopener">{h(v["nome"])}</a>: {h(v["testo"])}</li>' for v in voci)
    return (f'<aside class="aff-box"><{titolo_h}>{h(voci[0]["titolo"])} <span class="aff-tag">Partner</span></{titolo_h}>'
            f'<p>Payroll software can report through Single Touch Payroll and pay super each payday. We list it because readers ask; it does not change any figure on this site.</p>'
            f'<ul>{righe}</ul>{MON.nota_trasparenza("en")}</aside>')


# ---------------------------------------------------------------- calcolatore
TESTI_AVVISI = {
    "vic_phase": "Victoria: your Australian wages are above $3m (scaled by the days you employed), so the threshold is phased out at 50%.",
    "vic_no_soglia": "Victoria: the threshold is fully phased out (Australian wages at or above $5m, scaled by the days you employed).",
    "vic_sovrattasse": "Victoria: includes the mental health and wellbeing surcharge and the COVID-19 debt surcharge (0.5% each above the shared $10m threshold, another 0.5% each above $100m).",
    "qld_levy": "Queensland: includes the mental health levy (0.25% above the shared $10m threshold, plus 0.5% above $100m).",
    "qld_regionale_oltre": ("Queensland: above $350m of wages the regional discount does not apply, so the standard rate is used. QRO describes the cap as Australian taxable wages; "
                            "the Act (s 10A(4)) refers to the taxable wages paid by the employer in the return period. Check with QRO if your Queensland wages alone are below $350m."),
    "wa_no_soglia": "Western Australia: no deductable amount at $7.5m or more of Australian wages (adjusted for part years).",
    "sa_variabile": "South Australia: your annualised Australian wages are between $1.5m and $1.7m, so the rate is between 0% and 4.95%.",
    "tas_due_fasce": "Tasmania: 4% on the band between the two shared thresholds, 6.1% on wages above the upper one.",
    "act_su_tutto": "ACT: the rate is set by your total Australian wages and applies to all ACT wages above the threshold (not slice by slice).",
    "act_anno_parziale": ("ACT: for a part year with total wages of $1.75m or less, the 2026-27 determination sets no rate for that wage level. "
                          "We do not guess: ask the ACT Revenue Office (revenue.act.gov.au) for the amount."),
    "nt_no_soglia": "Northern Territory: the deduction is zero at three times the threshold ($7.5m for a full year).",
    "gruppo": "Group: enter the whole group's wages. Only the designated group employer claims the threshold; the other members pay on all their wages. The group total is the same.",
    "parziale": "Part year: thresholds are reduced by the days you paid wages; South Australia also annualises wages to set its rate.",
    "altro": "Wages in other states are counted in your Australian total (they reduce each threshold share) but their tax is not calculated here.",
    "stima": "Estimate only. Exemptions, contractor rules, apprentices and allowances are not modelled; your revenue office calculates the amount you must pay.",
    "vuoto": "Enter the wages you pay in each state or territory to see your threshold share and payroll tax.",
}

ESEMPIO_HOME = {"nsw": 2400000, "vic": 1100000, "qld": 900000}


def vuoto_html(campi):
    if len(campi) > 2:
        es = '<a href="/calculator/?nsw=2400000&amp;vic=1100000&amp;qld=900000">a payroll split across NSW, Victoria and Queensland</a>'
    else:
        s = campi[0]
        es = f'<a href="/{s}/?{s}=2000000">{h(J[s]["breve"])} wages of $2,000,000</a> or <a href="/{s}/?{s}=1500000&amp;altro=2500000">$1.5m in {h(J[s]["breve"])} and $2.5m elsewhere</a>'
    return (f'<p style="margin:0">{h(TESTI_AVVISI["vuoto"])}</p><ol><li>Type the taxable wages for the {ANNO} financial year (for example 1.5m).</li>'
            f'<li>Change the days if you did not pay wages all year.</li><li>Read the tax state by state, with the working.</li></ol>'
            f'<p style="margin:8px 0 0">Or try an example: {es}.</p>')


def dati_calc(campi, url_stato=True):
    return {"vuoto_html": vuoto_html(campi), "parametri": P, "giorni_anno": GIORNI_ANNO, "anno": ANNO, "campi": campi, "url_stato": url_stato,
            "brevi": {s: J[s]["breve"] for s in ORDINE}, "nomi": {s: J[s]["nome"] for s in ORDINE}, "testi": TESTI_AVVISI}


def risultato_statico(res, campi):
    """Stessa struttura del rendering JS, con i numeri del motore Python (si vede anche senza JavaScript)."""
    if not res["righe"]:
        return f'<div class="vuoto">{vuoto_html(campi)}</div>'
    quota = res["complessivo"] / res["W"] * 100 if res["W"] else 0
    esc_act = bool(res["non_calcolati"])
    et = f"Estimated payroll tax, {ANNO}" + (": total excludes ACT (not calculated)" if esc_act else "")
    out = (f'<div class="tot"><div class="main"><span>{et}</span><b data-o="totale">{soldi(res["complessivo"])}</b></div>'
           f'<div class="mensile"><span>Monthly average (annual ÷ 12)</span><b data-o="mensile">{soldi(res["mensile"])}</b></div>'
           f'<div><span>Total Australian wages</span><b>{soldi(res["W"])}</b></div><div><span>Share of wages</span><b>{quota:.2f}%</b></div></div>')
    out += '<table class="ris"><thead><tr><th scope="col">State</th><th scope="col" class="col-w">Wages</th><th scope="col">Threshold used</th><th scope="col">Rate</th><th scope="col">Tax</th></tr></thead><tbody>'
    for r in res["righe"]:
        nome = f'<a href="/{r["s"]}/">{J[r["s"]]["breve"]}</a>'
        if r["stato"] == "non_calcolato":
            out += f'<tr><td class="st">{nome}</td><td class="col-w">{soldi(r["w"])}</td><td colspan="3">not calculated</td></tr>'
            continue
        rate = ("–" if r["stato"] == "sotto" else "4% / 6.1%") if r["aliquota"] is None else pct(r["aliquota"])
        out += (f'<tr><td class="st">{nome}</td><td class="col-w">{soldi(r["w"])}</td><td>{soldi(r["soglia"])}</td><td>{rate}</td>'
                f'<td data-o="tassa-{r["s"]}">{soldi(r["tassa"])}</td></tr>')
        if r["extra"] > 0:
            out += f'<tr class="extra"><td colspan="4">{"Queensland mental health levy" if r["s"] == "qld" else "Victorian surcharges"}</td><td>{soldi(r["extra"])}</td></tr>'
    out += f'</tbody><tfoot><tr><td>Total{" excl. ACT" if esc_act else ""}<span class="solo-m"> · wages {soldi(res["W"])}</span></td><td class="col-w">{soldi(res["W"])}</td><td></td><td></td><td>{soldi(res["complessivo"])}</td></tr></tfoot></table>'
    out += f'<ul class="avvisi"><li>{h(TESTI_AVVISI["stima"])}</li></ul>'
    return out


def campo_soldi(nome, etichetta, valore, largo=False, descr=""):
    v = f"{valore:,.0f}" if valore else ""
    return (f'<label{" class=\"largo\"" if largo else ""}><span>{h(etichetta)}</span><span class="campo"><input type="text" name="{nome}" data-soldi '
            f'inputmode="decimal" autocomplete="off" spellcheck="false" placeholder="0" value="{v}"{f" aria-label=\"{h(descr)}\"" if descr else ""}></span></label>')


def calcolatore(stato=None, esempio=None, pull=True, titolo="Payroll tax calculator, 2026-27"):
    """stato=None: tutti gli 8 Stati; stato='nsw' ecc.: lo Stato più un campo 'altri Stati'. esempio: valori iniziali."""
    esempio = esempio or {}
    if stato is None:
        campi = list(ORDINE)
        celle = "".join(campo_soldi(s, J[s]["breve"], esempio.get(s, 0), descr=f"{J[s]['nome']} taxable wages") for s in ORDINE)
        legenda = f"Taxable wages paid in {ANNO} (AUD)"
        pill = "8 states and territories"
    else:
        campi = [stato, "altro"]
        celle = (campo_soldi(stato, f"{J[stato]['nome']} taxable wages", esempio.get(stato, 0), largo=True)
                 + campo_soldi("altro", "Taxable wages in all other states and territories", esempio.get("altro", 0), largo=True))
        legenda = f"Wages paid in {ANNO} (AUD)"
        pill = J[stato]["breve"]
    reg = ""
    if stato in (None, "vic"):
        reg += '<label class="check"><input type="checkbox" name="rv"><span>Regional Victorian employer (at least 85% of Victorian wages paid to regional employees)</span></label>'
    if stato in (None, "qld"):
        reg += '<label class="check"><input type="checkbox" name="rq"><span>Regional Queensland employer (eligible for the 1% discount)</span></label>'
    sal = {k: v for k, v in esempio.items()}
    res = motore.calcola(P, sal, GIORNI_ANNO, GIORNI_ANNO)
    formule = "".join(f'<li><a href="/{s}/">{h(J[s]["nome"])}</a>: {FORMULE[s]}</li>' for s in ([stato] if stato else ORDINE))
    ufficiali = ", ".join(f'<a href="{h(url_fonte(J[s]["fonti"]["calcolatore"]))}" rel="noopener">{h(J[s]["breve"])}</a>'
                          for s in ORDINE if "calcolatore" in J[s]["fonti"] and (stato is None or s == stato))
    uff = (f" Official calculators: {ufficiali}." if ufficiali else
           f" There is no official calculator we can link for {h(J[stato]['breve'])}: see the <a href=\"{h(J[stato]['url_ufficio'])}\" rel=\"noopener\">{h(J[stato]['ufficio'])}</a>.")
    nota_es = ('<span class="small" style="display:block;font-weight:600">Example figures: replace them with yours.</span>' if esempio else "")
    id_out = f"risultato-{stato or 'tutti'}"
    aff = box_affiliati("calculator-risultato", titolo_h="h3")
    aff_html = f'<div data-aff-calc hidden>{aff}</div>' if aff else ""
    return f"""<section class="card calc{' pull' if pull else ''}" id="calculator" aria-labelledby="calc-titolo">
<div class="calc-h"><h2 id="calc-titolo">{ico("calc")}{h(titolo)}</h2><span class="pill">{h(pill)}</span></div>
<form data-calc class="calc-g" novalidate>
<div class="calc-in">
<fieldset><legend>{h(legenda)}{nota_es}</legend><div class="salari">{celle}</div></fieldset>
<p class="anteprima" data-anteprima>Estimated payroll tax: <b>{soldi(res["complessivo"])}</b> · <a href="#{id_out}">see the breakdown</a></p>
<div class="calc-2">
<label>Days you paid wages in Australia<input type="number" name="giorni" value="{GIORNI_ANNO}" min="1" max="{GIORNI_ANNO}" step="1" inputmode="numeric"></label>
<label>Part of a group?<select name="gruppo"><option value="no">No, single employer</option><option value="si">Yes: I entered group totals</option></select></label>
</div>
{f'<fieldset><legend>Regional rates</legend>{reg}</fieldset>' if reg else ''}
<p class="small">Tip: you can type 1.5m or 800k. Wages include salaries, super, fringe benefits, directors' fees and other taxable payments.</p>
</div>
<div class="calc-out">
<div data-out id="{id_out}" aria-live="polite">{risultato_statico(res, campi)}</div>
<div class="azioni"><button type="button" class="btn" data-copia>{ico("copy")}Copy as text</button><button type="button" class="btn sec" data-link>{ico("link")}Copy link</button><button type="button" class="btn sec" data-azzera>{ico("reset")}Clear</button></div>
{aff_html}
</div>
</form>
<div class="calc-f">This is an estimate for the whole {ANNO} financial year. The amount you must lodge is worked out by each revenue office.{uff}
<details><summary>Formulas used</summary><ol>{formule}</ol><p>Where W is total Australian wages (yours or your group's), the share is the state's wages ÷ W and days is the days you paid wages ÷ {GIORNI_ANNO}. <a href="/calculator/#method">Method and sources</a>.</p></details></div>
<script type="application/json" id="calc-dati">{json.dumps(dati_calc(campi, url_stato=True), ensure_ascii=False)}</script>
</section>"""


FORMULE = {
    "nsw": "threshold = $1,200,000 × share × days; tax = (NSW wages − threshold) × 5.45%.",
    "vic": "threshold = the lesser of $1,000,000 × share × days and that amount minus 50% of (Victorian wages − $3m × share × days), never below nil (so it shrinks from $3m × days and is nil from $5m × days); tax at 4.85% (1.2125% regional); surcharges 1% above $10m and another 1% above $100m (shared thresholds).",
    "qld": "deduction = share × ($1.3m × days − (W − $1.3m × days) ÷ 7), not below nil; tax at 4.75% (4.95% if W is above $6.5m; 1% less for regional employers); mental health levy 0.25% above $10m and 0.5% above $100m (shared thresholds).",
    "wa": "nil if W ≤ $1m × days; 5.5% of all WA wages if W ≥ $7.5m × days; otherwise deductable amount = ($1m × days − (W − $1m × days) × 2/13) × share, tax = (WA wages − deductable amount) × 5.5%.",
    "sa": "nil if W ≤ $1.5m × days; deduction = $600,000 × share × days; rate 4.95%, or (annualised W − $1.5m) ÷ $200,000 × 4.95% when annualised W is $1.7m or less.",
    "tas": "nil if W ≤ $1.25m × days; 4% on wages above the lower threshold ($1.25m × share × days); above $2m × days, 4% on the band between the two thresholds and 6.1% above the upper one.",
    "act": "nil if W ≤ $1.75m × days; tax = (ACT wages − $1.75m × share × days) × rate, where the rate is 6.75%, 6.85%, 7.35%, 7.85% or 8.75% according to W.",
    "nt": "nil if W ≤ $2.5m × days; deduction = $2.5m × days − half of the excess, not below nil; tax = (NT wages − deduction × share) × 5.5% (6.5% if W is $100m or more).",
}


# ---------------------------------------------------------------- tabelle comuni
def tabella_2026(rim):
    righe = []
    for s in ORDINE:
        g = J[s]
        fid = g["fonti"]["tariffe"]
        righe.append(f'<tr><td><a href="/{s}/">{h(g["nome"])}</a></td><td class="n" data-l="Annual threshold">{h(g["soglia_testo"])}</td><td data-l="Rate">{h(g["aliquota_testo"])}{rim.ref([fid])}</td>'
                     f'<td data-l="How the threshold works">{h(g["deduzione_testo"])}</td><td data-l="Annual return due">{h(g["annuale"])}</td></tr>')
    return (f'<div class="tab"><table class="dati stack"><caption class="small" style="caption-side:bottom;text-align:left;padding:8px 12px">'
            f'Annual figures for 1 July 2026 to 30 June 2027. Thresholds are tested on total Australian wages (or group wages). '
            f'Checked on {data_lunga(CONTROLLO)}.</caption><thead><tr><th scope="col">State or territory</th><th scope="col" class="n">Annual threshold</th>'
            f'<th scope="col">Rate</th><th scope="col">How the threshold works</th><th scope="col">Annual return due</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def barre_soglie():
    mx = max(P[s]["soglia"] for s in ORDINE)
    a = "".join(f'<li><b>{J[s]["breve"]}</b><i style="width:{P[s]["soglia"] / mx * 100:.1f}%"></i><span>{mln(P[s]["soglia"])}</span></li>' for s in ORDINE)
    tassi = TASSO_INIZIALE
    mt = 8.75
    b = "".join(f'<li><b>{J[s]["breve"]}</b><i style="width:{tassi[s] / mt * 100:.1f}%"></i><span>{tassi[s]:g}%</span></li>' for s in ORDINE)
    return (f'<div class="cols"><div class="card"><h3 style="margin-top:0">Annual threshold, {ANNO}</h3><ul class="barre">{a}</ul></div>'
            f'<div class="card"><h3 style="margin-top:0">Starting rate above the threshold</h3><ul class="barre r">{b}</ul>'
            f'<p class="small" style="margin:10px 0 0">Starting (lowest standard) rate. Higher rates apply to bigger payrolls in Queensland, South Australia (above its variable band), Tasmania, the ACT and the Northern Territory; Victoria and Queensland have lower regional rates.</p></div></div>')


TASSO_INIZIALE = {"nsw": P["nsw"]["aliquota"], "vic": P["vic"]["aliquota"], "qld": P["qld"]["aliquota"], "wa": P["wa"]["aliquota"], "sa": P["sa"]["aliquota"],
                  "tas": P["tas"]["aliquota1"], "act": P["act"]["scaglioni"][0][1], "nt": P["nt"]["aliquota"]}


CONSIGLI_VIC = ["Alpine Shire", "Ararat Rural City", "Ballarat City", "Bass Coast Shire", "Baw Baw Shire", "Benalla Rural City", "Buloke Shire", "Campaspe Shire",
                "Central Goldfields Shire", "Colac Otway Shire", "Corangamite Shire", "East Gippsland Shire", "Gannawarra Shire", "Glenelg Shire", "Golden Plains Shire",
                "Greater Bendigo City", "Greater Geelong City", "Greater Shepparton City", "Hepburn Shire", "Hindmarsh Shire", "Horsham Rural City", "Indigo Shire", "Latrobe City",
                "Loddon Shire", "Macedon Ranges Shire", "Mansfield Shire", "Mildura Rural City", "Mitchell Shire", "Moira Shire", "Moorabool Shire", "Mount Alexander Shire",
                "Moyne Shire", "Murrindindi Shire", "Northern Grampians Shire", "Pyrenees Shire", "Borough of Queenscliffe", "South Gippsland Shire", "Southern Grampians Shire",
                "Strathbogie Shire", "Surf Coast Shire", "Swan Hill Rural City", "Towong Shire", "Wangaratta Rural City", "Warrnambool City", "Wellington Shire", "West Wimmera Shire",
                "Wodonga City", "Yarriambiack Shire"]


def griglia_stati():
    return ('<ul class="griglia stati">' + "".join(
        f'<li><a href="/{s}/"><b>{J[s]["breve"]}</b>{h(J[s]["nome"])}<small>{mln(P[s]["soglia"])} threshold · from {TASSO_INIZIALE[s]:g}%</small></a></li>' for s in ORDINE) + "</ul>")


GUIDE = [("calculator/", "Multi-state calculator", "All 8 jurisdictions at once, with the threshold shared by state"),
         ("interstate-wages/", "Interstate wages", "How each state shares its threshold, with the official examples"),
         ("grouping/", "Grouping", "When related businesses count as one employer"),
         ("regional-rates/", "Regional rates", "Victoria 1.2125% and the Queensland 1% discount"),
         ("thresholds-history/", "Thresholds history", "Every state, 2021-22 to 2026-27"),
         ("due-dates/", "Due dates", "Monthly returns and the 21 or 28 July annual return"),
         ("what-changed-2026-27/", "What changed in 2026-27", "New ACT brackets, NT 6.5% rate"),
         ("payday-super/", "Payday Super", "Super due within 7 business days of payday from 1 July 2026"),
         ("over-the-threshold/", "Over the threshold?", "Registering and what to do next, state by state")]


def griglia_guide(escludi=""):
    return ('<ul class="griglia">' + "".join(f'<li><a href="/{u}">{h(t)}<small>{h(d)}</small></a></li>' for u, t, d in GUIDE if u != escludi) + "</ul>")


def esempio_html(caso, rim, nota=""):
    """Un esempio ufficiale: dati, cifra ufficiale e la stessa cifra ricalcolata dal nostro motore."""
    par = json.loads(json.dumps(P))
    for s, v in caso.get("parametri", {}).items():
        par[s].update(v)
    giorni = caso.get("giorni", GIORNI_ANNO)
    res = motore.calcola(par, caso["salari"], giorni, GIORNI_ANNO)
    per = {r["s"]: r for r in res["righe"]}
    righe = []
    for chiave, atteso in caso["atteso"].items():
        s, campo = chiave.split(".")
        div = 1
        if "/" in campo:
            campo, d = campo.split("/")
            div = int(d)
        v = per[s][campo] / div
        etich = {"soglia": "threshold / deduction", "imponibile": "wages taxed", "tassa": "payroll tax", "extra": "levy", "aliquota": "rate"}[campo]
        if div == 12:
            etich = "monthly deduction"
        if campo == "aliquota":
            uff, nos = pct(atteso), pct(v)
        else:
            cent = abs(atteso - round(atteso)) > 1e-9
            uff, nos = soldi(atteso, cent), soldi(v, cent)
        nota_arr = " (the office rounds each step)" if uff != nos else ""
        righe.append(f'{h(etich)}: official <strong>{uff}</strong> · our calculator <span class="ok">{nos}</span>{nota_arr}')
    return (f'<div class="esempio"><p><strong>{h(caso["descr"])}</strong>{rim.ref([caso["fonte"]])}</p>'
            f'<p class="small">{"<br>".join(righe)}{(" · " + nota) if nota else ""}</p></div>')


def caso(id_):
    for c in ESEMPI["casi"]:
        if c["id"] == id_:
            return c
    raise SystemExit(f"esempio sconosciuto: {id_}")


def tabella_storico(stati, rim):
    anni = STORICO["anni"]
    th = "".join(f'<th scope="col">{a}</th>' for a in anni)
    righe = []
    for s in stati:
        celle = []
        for a in anni:
            v = STORICO["righe"][s].get(a)
            if not v:
                celle.append(f'<td class="na" data-l="{a}">not on a source we can read</td>')
            else:
                celle.append(f'<td data-l="{a}"><strong>{soldi(v["soglia"])}</strong><br><span class="small">{h(v["aliquota"])}</span>{rim.ref(v["fonti"])}</td>')
        righe.append(f'<tr><th scope="row"><a href="/{s}/">{h(J[s]["breve"])}</a></th>{"".join(celle)}</tr>')
    return f'<div class="tab"><table class="dati stack"><thead><tr><th scope="col">State</th>{th}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'


# ---------------------------------------------------------------- testi per giurisdizione
STATI = {
    "nsw": {
        "sub": "5.45% on NSW wages above a $1,200,000 threshold, shared by your NSW share of Australian wages and the days you paid wages.",
        "come": [
            "NSW charges <strong>5.45%</strong> on the wages you pay in NSW above your tax-free threshold of <strong>$1,200,000</strong>.[[nsw_rates]] "
            "You get the whole threshold only if you pay wages only in NSW, for the whole year, and are not part of a group.",
            "If you also pay wages in another state or territory, your threshold is $1,200,000 × NSW wages ÷ total Australian wages. "
            "If you paid wages for only part of the year, it is reduced again by the days you paid wages ÷ the days in the financial year "
            "(days you paid wages anywhere in Australia: an employer that keeps paying wages interstate keeps the full year).[[nsw_rates,nsw_interstate]]",
            "In a group, only one member claims the threshold (the designated group employer, or the group single lodger), worked out on the group's NSW and Australian wages.[[nsw_rates]]",
        ],
        "formula": "threshold = $1,200,000 × (NSW wages ÷ Australian wages) × (days paid ÷ 365)\ntax       = (NSW wages − threshold) × 5.45%",
        "esempi": ["nsw_interstate_900k", "nsw_part_year_184", "nsw_interstate_part_year", "nsw_group"],
        "mensile": "The monthly threshold for 2026-27 is <strong>$92,055</strong> for a 28-day month, <strong>$98,630</strong> for a 30-day month and <strong>$101,918</strong> for a 31-day month.[[nsw_rates]] "
                   "Register with Revenue NSW within 7 days after the month in which your total Australian wages (or your group's) go above it.[[nsw_register]]",
        "scadenze": "Monthly returns are due on the 7th of the following month; the December 2026 return is due on 14 January 2027. There is no June monthly return: June goes into the annual return, due on <strong>28 July 2027</strong>.[[nsw_keydates]]",
        "cambiato": "Nothing changed on 1 July 2026: the threshold ($1,200,000) and the rate (5.45%) have been the same in every year since 2022-23.[[nsw_rates]]",
        "extra": [],
    },
    "vic": {
        "sub": "4.85% (1.2125% regional) above a $1,000,000 threshold that is phased out between $3m and $5m of Australian wages (scaled by days for a part year).",
        "come": [
            "Victoria charges <strong>4.85%</strong> on Victorian taxable wages above your threshold, or <strong>1.2125%</strong> for regional employers.[[vic_rates,vic_csv]] "
            "The full threshold is <strong>$1,000,000</strong> a year ($83,333 a month).",
            "The State Revenue Office works the threshold out in four steps:[[vic_phase]] (1) multiply $1,000,000 by your Victorian share of Australian wages and the share of the year you employed; "
            "(2) multiply $3 million by the same two shares; (3) subtract step 2 from your Victorian wages and multiply by the phase-out rate, <strong>50%</strong> from 2025-26 onwards; "
            "(4) subtract step 3 from step 1. Schedule 1 of the Payroll Tax Act 2007 takes the lesser of step 4 and step 1, and treats a negative step 4 as nil.[[vic_act]]",
            "Because the $3 million is scaled by the days you employed, the phase-out starts at $3 million × days ÷ 365 of Australian wages and the threshold reaches nil at $5 million × days ÷ 365. "
            "For a full year that is $3 million and $5 million; for an employer that paid wages on only 183 days, $1.5 million and $2.5 million: with $2.9 million of Victorian wages over 183 days there is no threshold and the tax is $140,650.[[vic_act]]",
            "Employers and groups with Australian wages above $10 million also pay two surcharges on their Victorian wages above the shared thresholds (see below).[[vic_surcharges]]",
        ],
        "formula": "D1        = $1,000,000 × share × days ÷ 365\nphase-out = D1 − (VIC wages − $3,000,000 × share × days ÷ 365) × 50%, not below 0\nthreshold = the lesser of D1 and the phase-out amount\ntax       = (VIC wages − threshold) × 4.85%   (1.2125% regional)",
        "esempi": ["vic_example1_2024_25", "vic_example2_2024_25"],
        "nota_esempi": "The two official examples use the 2024-25 rules ($900,000 threshold, 45% phase-out); our calculator gives the same figures when run with those rules.",
        "mensile": "The monthly threshold is <strong>$83,333</strong>.[[vic_rates]] You must register if you pay wages in Victoria and your taxable Australian wages exceed the threshold.[[vic_register]]",
        "scadenze": "Monthly returns and payments are due by the 7th of the next month (or the next business day).[[vic_monthly]] The annual reconciliation is due by <strong>21 July</strong>.[[vic_annual]]",
        "cambiato": "Nothing new on 1 July 2026. The threshold rose to $1,000,000 and the phase-out rate to 50% from 1 July 2025, and both apply to 2026-27.[[vic_rates,vic_phase]]",
        "extra": [
            ("Regional employers: 1.2125%",
             "You pay 1.2125% instead of 4.85% if at least <strong>85%</strong> of your Victorian taxable wages go to regional employees, who must do more than half of their work for you in regional Victoria "
             "(48 listed councils and six alpine resorts). For the annual reconciliation the 85% test applies to the whole year. In a group, each business is tested on its own.[[vic_regional]] "
             "See <a href=\"/regional-rates/\">regional rates</a>."),
            ("Surcharges above $10 million",
             "The mental health and wellbeing surcharge and the COVID-19 debt temporary surcharge (until 30 June 2033) are each <strong>0.5%</strong> when Australian wages are over $10 million "
             "(1% together) and each another 0.5% over $100 million (2% together). They apply only to Victorian taxable wages above the thresholds, which are shared by your Victorian "
             "share of wages and by days employed: for example, $80m in Victoria and $70m in NSW gives a first threshold of $5,333,333.33.[[vic_surcharges]] The calculator adds them as a separate line."),
        ],
    },
    "qld": {
        "sub": "4.75% (4.95% above $6.5m) after a $1.3m deduction that falls by $1 for every $7 of wages, plus a mental health levy above $10m.",
        "come": [
            "Queensland charges <strong>4.75%</strong> on Queensland taxable wages above your deduction if you (or your group) pay $6.5 million or less in Australian taxable wages, "
            "and <strong>4.95%</strong> above $6.5 million.[[qld_rates]] Eligible regional employers get 1% off the rate until 30 June 2030.[[qld_regional]]",
            "The threshold is <strong>$1.3 million</strong>. Above it, the deduction falls by $1 for every $7 of wages, reaching zero at $10.4 million.[[qld_deductions]] "
            "The Payroll Tax Act 1971 sets the annual deduction as: Queensland share of Australian wages × (K × days ÷ days in year − (Australian wages − K × days ÷ days in year) ÷ 7), with K = $1,300,000, never below zero.[[qld_act,qld_act_formula]]",
            "A mental health levy is added for employers and groups with Australian wages over $10 million.[[qld_mhl]]",
        ],
        "formula": "Kd        = $1,300,000 × days paid ÷ 365\ndeduction = (QLD wages ÷ W) × (Kd − (W − Kd) ÷ 7), not below 0\ntax       = (QLD wages − deduction) × 4.75%  (4.95% if W > $6.5m; 1% less if regional)\nlevy      = 0.25% × (QLD wages − $10m × share × days) + 0.5% × (QLD wages − $100m × share × days), each not below 0",
        "esempi": ["qld_annual_deduction", "qld_fixed_periodic", "qld_levy_112m", "qld_levy_interstate", "qld_levy_group"],
        "mensile": "The monthly deduction starts at <strong>$108,333</strong>.[[qld_deductions]] Register within 7 days of the first month in which your Australian wages (or your group's) exceed <strong>$25,000 a week</strong>.[[qld_register]]",
        "scadenze": "Periodic returns are due 7 days after the end of the month (December 2026: 14 January 2027). There is no June periodic return; the 2026-27 annual return is due on <strong>21 July 2027</strong>.[[qld_due]]",
        "cambiato": "Rates and threshold are unchanged. The regional discount runs until 30 June 2030; on 11 November 2026 QRO announced a temporary amnesty, until 31 December 2026, for certain employers who incorrectly claimed it.[[qld_regional,qld_amnesty]]",
        "extra": [
            ("Mental health levy",
             "The levy is 0.25% of Queensland taxable wages above the primary threshold of $10 million, plus 0.5% above the additional threshold of $100 million. Both thresholds are shared by the "
             "Queensland share of Australian wages (and reduced for part years). A Queensland-only employer paying $112 million owes $255,000 + $60,000 = $315,000; an employer paying $4 million "
             "in Queensland out of $16 million owes $3,750.[[qld_mhl]] The calculator shows it as a separate line."),
            ("Regional discount",
             "Regional employers pay <strong>3.75%</strong> (or 3.95% above $6.5 million) until 30 June 2030. You qualify if your registered ABN address is in regional Queensland and at least 85% of "
             "your Queensland taxable wages go to employees who live there. The discount does not apply above $350 million of wages.[[qld_regional]] See <a href=\"/regional-rates/\">regional rates</a>."),
        ],
    },
    "wa": {
        "sub": "5.5% above a $1,000,000 threshold that shrinks by $2 for every $13 of wages and disappears at $7.5m.",
        "come": [
            "Western Australia charges <strong>5.5%</strong> on WA taxable wages above your deductable amount.[[wa_calc]] The annual threshold is <strong>$1,000,000</strong> and the upper threshold "
            "<strong>$7,500,000</strong>; between them the threshold diminishes by the tapering value 2/13, that is $2 for every $13 of wages over $1 million.[[wa_calc,wa_act]]",
            "If you also pay wages interstate, the deductable amount is multiplied by WA wages ÷ Australian wages. For a part year, the Pay-roll Tax Assessment Act 2002 apportions both the annual "
            "and the upper threshold by days before the taper is applied.[[wa_interstate,wa_act]]",
        ],
        "formula": "AT = $1,000,000 × days paid ÷ 365;  UT = $7,500,000 × days paid ÷ 365\nif W ≤ AT: no tax\nif W ≥ UT: tax = WA wages × 5.5%\notherwise: deductable = (AT − (W − AT) × 2/13) × (WA wages ÷ W);  tax = (WA wages − deductable) × 5.5%",
        "esempi": ["wa_local_1_2m", "wa_interstate", "wa_monthly_92k"],
        "mensile": "The monthly threshold is <strong>$83,333</strong>. Register within seven days after the end of the month in which your total Australian taxable wages exceed it.[[wa_register,wa_calc]]",
        "scadenze": "Returns are due on the 7th day of the month after the return period (April by 7 May). The annual reconciliation, with the June return, is due on or before <strong>21 July</strong>.[[wa_returns]]",
        "cambiato": "Unchanged for 2026-27. The extra rates on very large payrolls (6% on wages from $100m to $1.5bn and 6.5% above) applied only up to 30 June 2023.[[wa_calc]]",
        "extra": [],
    },
    "sa": {
        "sub": "No tax up to $1.5m of Australian wages, a rate rising from 0% to 4.95% up to $1.7m, and a deduction of up to $600,000.",
        "come": [
            "South Australia has two separate numbers: a <strong>$1,500,000 threshold</strong> that decides whether you pay at all, and a <strong>$600,000 deduction</strong> that is subtracted from your SA wages.[[sa_rates]]",
            "The rate is set by your total Australian wages, annualised if you paid wages for only part of the year: <strong>4.95%</strong> above $1.7 million and, between $1.5 million and $1.7 million, "
            "(annualised wages − $1,500,000) ÷ $200,000 × 4.95%.[[sa_act]] RevenueSA's rate table rounds these figures and is described as an indication only.[[sa_table]]",
            "The deduction is $600,000 × SA wages ÷ Australian wages × days paid ÷ days in the year.[[sa_how,sa_act]]",
        ],
        "formula": "no tax if W ≤ $1,500,000 × days ÷ 365\nannualised W = W × 365 ÷ days\nrate         = 4.95%  if annualised W > $1.7m,  else (annualised W − $1.5m) ÷ $200,000 × 4.95%\ndeduction    = $600,000 × (SA wages ÷ W) × days ÷ 365\ntax          = (SA wages − deduction) × rate",
        "esempi": ["sa_interstate", "sa_only_1_6m", "sa_annualised"],
        "mensile": "Register when Australian wages (or group wages) exceed the threshold: <strong>$28,846 a week</strong>, $125,000 a month.[[sa_register,sa_rates]]",
        "scadenze": "Monthly returns are due on the 7th of the following month (next business day if it falls on a weekend or holiday). The annual reconciliation is due on <strong>28 July</strong>: Wednesday 28 July 2027 for 2026-27.[[sa_returns]]",
        "cambiato": "Unchanged: the $1.5m threshold and the 0% to 4.95% variable band have applied since 1 January 2019, and the $600,000 deduction since 1 July 2009.[[sa_rates]]",
        "extra": [],
    },
    "tas": {
        "sub": "4% on wages between $1.25m and $2m, 6.1% above $2m, with both thresholds shared by your Tasmanian share of wages.",
        "come": [
            "Tasmania has two thresholds: <strong>$1,250,000</strong> and <strong>$2,000,000</strong>. Wages from $1,250,001 to $2,000,000 are taxed at <strong>4%</strong> and wages above $2,000,000 at <strong>6.1%</strong>.[[tas_rates]]",
            "The 6.1% rate applies only to the part above the upper threshold. Schedule 1 of the Payroll Tax Act 2008 adds 4% of the band between the two thresholds to 6.1% of the wages above the upper threshold, "
            "with both thresholds multiplied by the Tasmanian share of Australian wages and the share of the year you paid wages.[[tas_act,tas_act_formula]]",
        ],
        "formula": "T1 = $1,250,000 × days ÷ 365;  T2 = $2,000,000 × days ÷ 365;  share = TAS wages ÷ W\nif W ≤ T1:        no tax\nif T1 < W ≤ T2:   tax = (TAS wages − T1 × share) × 4%\nif W > T2:        tax = (T2 − T1) × share × 4% + (TAS wages − T2 × share) × 6.1%",
        "esempi": ["tas_ex1_full", "tas_ex1_part", "tas_ex2_full", "tas_ex2_part", "tas_ex3_group_full"],
        "mensile": "Monthly thresholds are the number of days in the month ÷ days in the year × $1.25 million (and × $2 million), rounded to the dollar.[[tas_rates]] "
                   "You are liable once Australian wages (or group wages) exceed $1.25 million a year or <strong>$24,038 a week</strong> during a month; all Tasmanian wage-paying group members must register.[[tas_register]]",
        "scadenze": "Monthly returns are due by the 7th of the following month; the annual adjustment return is due by <strong>21 July</strong>.[[tas_lodge]]",
        "cambiato": "Unchanged: the two thresholds and the 4% and 6.1% rates have applied since 1 July 2018.[[tas_rates]]",
        "extra": [],
    },
    "act": {
        "sub": "A $1,750,000 threshold and five rates from 6.75% to 8.75%, set by total Australian wages and charged on all ACT wages above the threshold.",
        "come": [
            "From 1 July 2026 the ACT threshold is <strong>$1,750,000</strong> a year ($145,833.33 a month).[[act_det2026]] The rate depends on your total Australian wages (or your group's): "
            "<strong>6.75%</strong> above $1.75 million up to $20 million; <strong>6.85%</strong> up to $50 million; <strong>7.35%</strong> up to $100 million; <strong>7.85%</strong> up to $150 million; "
            "<strong>8.75%</strong> above $150 million. Eligible universities are capped at 6.85%.[[act_det2026,portal_rates]]",
            "These are not marginal brackets. The Payroll Tax Act 2011 applies a single rate R to all your ACT wages above your share of the threshold, and the 2026 determination sets R from the bracket "
            "your total wages fall in.[[act_act,act_det2026]] Crossing a bracket limit therefore raises the rate on all your ACT wages above the threshold.",
            "The ACT Revenue Office website does not answer our checking server (Cloudflare), so the figures here come from the determination on the ACT legislation register and from the joint portal of the revenue offices.[[act_revenue]]",
        ],
        "formula": "no tax if W ≤ $1,750,000 × days ÷ 365\nrate = 6.75% (W ≤ $20m), 6.85% (≤ $50m), 7.35% (≤ $100m), 7.85% (≤ $150m), 8.75% (above)\ntax  = (ACT wages − $1,750,000 × (ACT wages ÷ W) × days ÷ 365) × rate",
        "esempi": [],
        "mensile": "The monthly threshold is <strong>$145,833.33</strong>, and the monthly rate is set by total monthly wages using brackets of $1,666,666.66, $4,166,666.66, $8,333,333.33 and $12,500,000.[[act_det2026]]",
        "scadenze": "Payroll tax for each month is due within 7 days after the end of the month; for June, within 28 days, which is why the ACT annual return is due on <strong>28 July</strong>.[[act_act,portal_rates]]",
        "cambiato": "The ACT made the biggest change of 2026-27: the threshold fell from $2,000,000 to $1,750,000, and the old 6.85% rate plus surcharges for large employers was replaced by five rates from 6.75% to 8.75%.[[act_det2026,act_det2025,act_es2026]]",
        "extra": [
            ("What the calculator does not do for the ACT",
             "With a part year and total wages of $1.75 million or less (but above your reduced threshold), you are liable but the determination's rate table starts above $1.75 million, "
             "so it sets no rate for your wage level. We do not guess: the calculator flags the case and you should ask the ACT Revenue Office.[[act_det2026,act_act]]"),
        ],
    },
    "nt": {
        "sub": "5.5% (6.5% from $100m of Australian wages) above a $2.5m threshold, with a deduction that falls by $1 for every $2 and ends at $7.5m.",
        "come": [
            "The Northern Territory has the highest threshold in Australia: <strong>$2,500,000</strong> a year ($208,333 a month).[[portal_rates]] The rate is <strong>5.5%</strong>; from 1 July 2026 it is "
            "<strong>6.5%</strong> for employers and groups whose Australian wages for the year are $100 million or more.[[nt_act,portal_rates]]",
            "Schedule 1 of the Payroll Tax Act 2009 sets the annual deduction as the threshold (apportioned by days) minus half of the wages above it, never below zero. It reaches zero at three times the "
            "threshold, $7.5 million for a full year, and is then shared by the NT share of Australian wages.[[nt_act]]",
            "The NT Treasury website does not answer our checking server (Cloudflare), so the figures here come from the Act on the NT legislation website and from the joint portal of the revenue offices.[[nt_treasury]]",
        ],
        "formula": "ETA       = $2,500,000 × days ÷ 365\nno tax if W ≤ ETA\ndeduction = ETA − (W − ETA) ÷ 2, not below 0\ntax       = (NT wages − deduction × NT wages ÷ W) × 5.5%   (6.5% if W ≥ $100m)",
        "esempi": [],
        "mensile": "The monthly threshold is <strong>$208,333</strong> (weekly $48,077).[[portal_rates]]",
        "scadenze": "Under the Payroll Tax Act 2009, returns are due within <strong>21 days</strong> after the end of each month, and the June return with the annual adjustment within 21 days after the end of June.[[nt_act]]",
        "cambiato": "From 1 July 2026 the Treasury Legislation Amendment Act 2026 added a 6.5% rate for employers and groups with Australian wages of $100 million or more. The $2.5m threshold, the deduction and the 5.5% rate are unchanged.[[nt_act,portal_rates]]",
        "extra": [],
    },
}

FAQ_TITOLO = {"nsw": "NSW payroll tax: common questions", "vic": "Victorian payroll tax: common questions", "qld": "Queensland payroll tax: common questions",
              "wa": "WA payroll tax: common questions", "sa": "SA payroll tax: common questions", "tas": "Tasmanian payroll tax: common questions",
              "act": "ACT payroll tax: common questions", "nt": "NT payroll tax: common questions"}


def nostro_esempio(salari, giorni=GIORNI_ANNO, rim=None, descr=""):
    res = motore.calcola(P, salari, giorni, GIORNI_ANNO)
    r = res["righe"][0]
    return (f'<div class="esempio"><p><strong>{h(descr)}</strong> <span class="etich">our calculation</span></p>'
            f'<p class="small">threshold used {soldi(r["soglia"])} · wages taxed {soldi(r["imponibile"])} · rate {pct(r["aliquota"]) if r["aliquota"] is not None else "4% / 6.1%"} · '
            f'payroll tax <span class="ok">{soldi(r["tassa"])}</span>{(" + " + soldi(r["extra"])) if r["extra"] else ""}</p></div>')


def pagina_stato(s):
    g, T = J[s], STATI[s]
    rim = Rimandi()
    mens = {"nsw": "$101,918", "vic": "$83,333", "qld": "$108,333", "wa": "$83,333", "sa": "$125,000", "tas": "$106,164", "act": "$145,833.33", "nt": "$208,333"}[s]
    mens_l = "31-day month" if s in ("nsw", "tas") else "monthly"
    fonte_asof = {"act": "the ACT legislation register (2026 determination) and the joint revenue office portal",
                  "nt": "the Payroll Tax Act 2009 (NT) and the joint revenue office portal"}.get(s, f"{h(ufficio_con_articolo(g))} and the joint revenue office portal")
    stats = (f'<section class="card stats pull" aria-label="Key figures {ANNO}">'
             f'<div class="stat main"><b>{h(g["soglia_testo"])}</b><span>annual threshold, {ANNO}</span></div>'
             f'<div class="stat"><b>{h(g["aliquota_testo"].split(" ")[0])}</b><span>rate{" from" if s in ("act", "sa", "tas") else ""}{" (standard)" if s in ("vic", "qld") else ""}</span></div>'
             f'<div class="stat"><b>{mens}</b><span>{mens_l} threshold</span></div>'
             f'<div class="stat"><b>{h(g["annuale"])}</b><span>annual return due</span></div>'
             f'<p class="asof">Figures for 1 July 2026 to 30 June 2027 from {fonte_asof}, checked on {data_lunga(CONTROLLO)}.</p></section>')
    if s == "tas":
        stats = stats.replace("$106,164</b><span>31-day month threshold", "$106,164</b><span>31-day month threshold (lower)")
    corpo = stats
    corpo += f'<h2 id="how">How {h(g["breve"])} payroll tax is worked out</h2><div class="testo">' + "".join(f"<p>{rim.t(p)}</p>" for p in T["come"]) + "</div>"
    corpo += f'<pre class="formula" aria-label="Formula">{h(T["formula"])}</pre>'
    if T["esempi"]:
        corpo += f'<h3>Official worked examples, checked against our calculator</h3>'
        if T.get("nota_esempi"):
            corpo += f'<p class="small">{h(T["nota_esempi"])}</p>'
        corpo += "".join(esempio_html(caso(e), rim) for e in T["esempi"])
    else:
        es = {"act": ({"act": 5000000}, "ACT-only employer, $5,000,000 of wages, full year"),
              "nt": ({"nt": 4000000}, "NT-only employer, $4,000,000 of wages, full year")}[s]
        corpo += ('<h3>Worked example</h3><p class="small">The revenue office publishes no worked example we can read, so this one applies the formula in the Act; the result is ours, not an official figure.</p>'
                  + nostro_esempio(es[0], descr=es[1]))
    corpo += f'<h2 id="calc">{h(g["breve"])} payroll tax calculator</h2><p>Enter your {h(g["nome"])} wages and, if you pay wages elsewhere, the total for the other states: the calculator applies the formula above. For several states at once, use the <a href="/calculator/">multi-state calculator</a>.</p>'
    corpo += calcolatore(stato=s, pull=False, titolo=f"{g['breve']} payroll tax calculator, {ANNO}")
    corpo += AD
    for tit, testo in T["extra"]:
        corpo += f'<h2>{h(tit)}</h2><div class="testo"><p>{rim.t(testo)}</p></div>'
    corpo += f'<h2 id="register">Monthly threshold and registration</h2><div class="testo"><p>{rim.t(T["mensile"])}</p></div>'
    corpo += f'<h2 id="due">Due dates</h2><div class="testo"><p>{rim.t(T["scadenze"])}</p><p>All states: see <a href="/due-dates/">payroll tax due dates</a>.</p></div>'
    corpo += f'<h2 id="changed">What changed in 2026-27</h2><div class="testo"><p>{rim.t(T["cambiato"])}</p></div>'
    corpo += f'<h2 id="history">{h(g["breve"])} thresholds and rates since 2021-22</h2>' + tabella_storico([s], rim)
    gr = g["fonti"].get("grouping")
    gruppo = (f'Businesses linked by ownership, control or shared employees are grouped and share one threshold. Read <a href="{h(url_fonte(gr))}" rel="noopener">the grouping page of {h(ufficio_con_articolo(g))}</a>{rim.ref([gr])} '
              f'and our <a href="/grouping/">grouping summary</a>.' if gr else
              f'Businesses linked by ownership, control or shared employees are grouped and share one threshold (Part 5 of the Act).{rim.ref([g["fonti"]["legge"]])} See our <a href="/grouping/">grouping summary</a>.')
    corpo += f'<h2 id="grouping">Grouping</h2><div class="testo"><p>{gruppo}</p></div>'
    calc = g["fonti"].get("calcolatore")
    uff = (f'<li><a href="{h(url_fonte(calc))}" rel="noopener">Official {h(g["breve"])} payroll tax calculator</a>{rim.ref([calc])}</li>' if calc else "")
    corpo += (f'<h2 id="official">Official tools and pages</h2><ul class="testo">{uff}'
              f'<li><a href="{h(g["url_ufficio"])}" rel="noopener">{h(g["ufficio"])}: payroll tax</a></li>'
              f'<li><a href="https://www.payrolltax.gov.au/resources" rel="noopener">payrolltax.gov.au: rates and thresholds of all states</a>{rim.ref(["portal_rates"])}</li></ul>')
    corpo += box_affiliati(s)
    faq_html, faq_ld = faq_blocco(s, rim, FAQ_TITOLO[s])
    corpo += faq_html
    corpo += '<h2>Other states and territories</h2>' + griglia_stati().replace(f'<li><a href="/{s}/">', f'<li hidden><a href="/{s}/">')
    corpo += rim.elenco()
    tit = f"{g['breve']} Payroll Tax 2026-27: Threshold, Rate, Calculator"
    if len(tit) > 60:
        tit = f"{g['breve']} Payroll Tax 2026-27: Rates and Calculator"
    desc = f"{g['nome']} payroll tax {ANNO}: {g['soglia_testo']} threshold, {g['aliquota_testo'].split(';')[0]}. Official formula, worked examples, due dates and a calculator."
    if len(desc) > 160:
        desc = f"{g['nome']} payroll tax {ANNO}: {g['soglia_testo']} threshold, rates, official formula, worked examples, due dates and calculator."
    testata = banda(f"{g['breve']} · {ANNO}", f"{g['nome']} payroll tax {ANNO}", h(T["sub"]), trust(), icona="map")
    pagina(f"{s}/", tit, desc, corpo, testata, briciole=[("Home", ""), (g["nome"], f"{s}/")], jsonld=[faq_ld] if faq_ld else None)


# ---------------------------------------------------------------- pagine principali
def home():
    rim = Rimandi()
    corpo = calcolatore(esempio=ESEMPIO_HOME)
    corpo += AD
    corpo += (f'<h2 id="states">{ANNO} payroll tax rates and thresholds at a glance</h2>'
              f'<p class="lead">Each state and territory taxes the wages paid there, but tests its threshold against your <strong>total Australian wages</strong>. '
              f'Here are the {ANNO} figures, read from the revenue offices and the joint portal of the eight offices.{rim.ref(["portal_rates"])}</p>')
    corpo += tabella_2026(rim)
    corpo += barre_soglie()
    corpo += griglia_stati()
    corpo += (f'<h2>What changed on 1 July 2026</h2><ul class="testo">'
              f'<li><strong>ACT</strong>: threshold down from $2,000,000 to $1,750,000; five rates from 6.75% to 8.75%, chosen by total wages and charged on all ACT wages above the threshold.{rim.ref(["act_det2026"])}</li>'
              f'<li><strong>Northern Territory</strong>: a 6.5% rate for employers and groups with Australian wages of $100 million or more; 5.5% and the $2.5m threshold unchanged for everyone else.{rim.ref(["portal_rates", "nt_act"])}</li>'
              f'<li><strong>Payday Super</strong>: from 1 July 2026 employers must get super into the fund within 7 business days of each payday.{rim.ref(["payday_act"])} <a href="/payday-super/">What it means</a>.</li>'
              f'<li>NSW, Victoria, Queensland, WA, SA and Tasmania kept their 2025-26 thresholds and rates.{rim.ref(["portal_rates"])}</li></ul>'
              f'<p><a href="/what-changed-2026-27/">All changes for {ANNO}</a></p>')
    c = caso("nsw_interstate_900k")
    corpo += (f'<h2>Paying wages in more than one state?</h2><div class="testo"><p>You do not get a full threshold in every state. Each state gives you its threshold multiplied by the share of your '
              f'Australian wages paid there. With $900,000 of NSW wages out of $3,000,000, your NSW threshold is $1,200,000 × 900,000 ÷ 3,000,000 = <strong>$360,000</strong>.{rim.ref([c["fonte"]])} '
              f'Victoria, Queensland, Western Australia and the Northern Territory also shrink the threshold as total wages grow, so the order in which you add wages matters less than the total.</p>'
              f'<p><a href="/interstate-wages/">How interstate wages work, with every official example</a></p></div>')
    corpo += '<h2>Guides</h2>' + griglia_guide()
    faq_html, faq_ld = faq_blocco("home", rim)
    corpo += faq_html + rim.elenco()
    sub = (f"Every rate and threshold for 1 July 2026 to 30 June 2027, checked against the revenue offices on {data_lunga(CONTROLLO)}. "
           f"Enter wages for each state to see your share of each threshold and your tax.")
    testata = banda(f"{ANNO} · all 8 states and territories", "Payroll tax by state: 2026-27 rates, thresholds and calculator", h(sub), trust())
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": f"{URL_SITO}/", "inLanguage": "en-AU"}]
    if faq_ld:
        ld.append(faq_ld)
    pagina("", "Payroll Tax by State 2026-27: Rates, Thresholds, Calculator",
           "Australian payroll tax 2026-27 for NSW, VIC, QLD, WA, SA, TAS, ACT and NT: thresholds, rates and a multi-state calculator that shares each threshold.",
           corpo, testata, jsonld=ld)


def pagina_calcolatore():
    rim = Rimandi()
    corpo = calcolatore()
    corpo += AD
    corpo += f'<h2 id="method">How the calculator works</h2><div class="testo">'
    corpo += (f'<p>The calculator adds up the wages you enter to get your total Australian wages (W). For each state it works out your share of that state\'s threshold, '
              f'then applies the state\'s own formula, taken from the revenue office pages and the payroll tax Acts:{rim.ref(["portal_rates"])}</p><ol>')
    fonti_formule = {"nsw": ["nsw_rates"], "vic": ["vic_phase", "vic_surcharges"], "qld": ["qld_act", "qld_mhl"], "wa": ["wa_act", "wa_interstate"],
                     "sa": ["sa_act"], "tas": ["tas_act"], "act": ["act_act", "act_det2026"], "nt": ["nt_act"]}
    for s in ORDINE:
        corpo += f'<li><a href="/{s}/">{h(J[s]["nome"])}</a>: {FORMULE[s]}{rim.ref(fonti_formule[s])}</li>'
    corpo += ('</ol><p>Days are the days in the financial year in which you (or a member of your group) paid taxable or interstate wages, which is how the Acts define the part-year '
              'adjustment.[[sa_act,act_act,nt_act]] The calculator is checked against every official worked example we could find (see <a href="/how-we-check/">how we check</a>).</p></div>')
    corpo = rim.t(corpo)
    corpo += ('<h2>What the calculator does not do</h2><ul class="testo">'
              '<li>It does not decide what counts as taxable wages, exemptions (charities, apprentices and trainees, some health and education employers), contractor rules or allowances: enter wages already adjusted.</li>'
              '<li>It does not split a group\'s tax between members: enter the group\'s totals; the result is the group total.</li>'
              '<li>It does not produce monthly return figures: monthly returns use monthly thresholds and estimates, and the annual return reconciles them. The monthly figure shown is the annual estimate divided by 12.</li>'
              '<li>For the ACT, a part year with total wages of $1.75 million or less has no rate in the 2026-27 determination: the calculator says so instead of guessing.</li></ul>')
    corpo += box_affiliati("calculator-risultato")
    faq_html, faq_ld = faq_blocco("calculator", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("calculator/") + rim.elenco()
    testata = banda(f"Calculator · {ANNO}", "Multi-state payroll tax calculator 2026-27",
                    "Enter the wages you pay in each state and territory. The calculator shares every threshold by your wage share and days, applies each state's formula and shows the working.", trust(), corta=False, icona="calc")
    ld = [{"@context": "https://schema.org", "@type": "WebApplication", "name": "Multi-state payroll tax calculator 2026-27", "url": f"{URL_SITO}/calculator/",
           "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "inLanguage": "en-AU",
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "AUD"}}]
    if faq_ld:
        ld.append(faq_ld)
    pagina("calculator/", "Payroll Tax Calculator 2026-27: All Australian States",
           "Free 2026-27 payroll tax calculator for all 8 Australian states and territories: shares each threshold by state wages and days, with the official formulas.",
           corpo, testata, briciole=[("Home", ""), ("Calculator", "calculator/")], jsonld=ld)


def interstate():
    rim = Rimandi()
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t("<p><strong>Interstate wages</strong> are wages that are taxable under the payroll tax law of another state or territory.[[nsw_interstate]] Every state counts them, because every "
                   "threshold is tested against your total Australian wages and then shared by the part of those wages paid in that state. Interstate wages must be declared in each state's returns "
                   "even when you are under that state's threshold.[[nsw_interstate]]</p></div>")
    corpo += "<h2>The rule in every state</h2><div class=\"testo\">"
    corpo += rim.t("<p>Your share of a state's threshold = the state's threshold × wages paid in that state ÷ total Australian wages, and × days you paid wages ÷ days in the year for a part year.[[nsw_rates,sa_how]] "
                   "On top of that, some states reduce the threshold itself as total wages grow, before sharing it:</p><ul>"
                   "<li>Victoria: phased out at 50% from $3m, nil from $5m (both scaled by days for a part year).[[vic_phase,vic_act]]</li>"
                   "<li>Queensland: $1 less for every $7 above $1.3m, nil at $10.4m.[[qld_deductions]]</li>"
                   "<li>Western Australia: $2 less for every $13 above $1m, nil at $7.5m.[[wa_calc]]</li>"
                   "<li>Northern Territory: $1 less for every $2 above $2.5m, nil at $7.5m.[[nt_act]]</li></ul>"
                   "<p>Tasmania shares both of its thresholds ($1.25m and $2m),[[tas_act]] and South Australia shares its $600,000 deduction while its rate depends on total wages.[[sa_act]]</p></div>")
    corpo += "<h2>Official examples, recalculated</h2>"
    corpo += "".join(esempio_html(caso(e), rim) for e in ["nsw_interstate_900k", "nsw_interstate_qld", "nsw_interstate_part_year", "vic_example2_2024_25", "qld_annual_deduction", "wa_interstate", "sa_interstate", "tas_ex2_full"])
    corpo += '<p class="small">The Victorian example uses the 2024-25 rules ($900,000, 45%); our calculator gives the same figure with those rules.</p>'
    corpo += AD
    sal = {"nsw": 1800000, "vic": 1200000, "qld": 900000, "wa": 600000}
    res = motore.calcola(P, sal, GIORNI_ANNO, GIORNI_ANNO)
    righe = "".join(f'<tr><td>{J[r["s"]]["breve"]}</td><td class="n">{soldi(r["w"])}</td><td class="n">{r["w"] / res["W"] * 100:.1f}%</td><td class="n">{soldi(r["soglia"])}</td><td class="n">{soldi(r["tassa"] + r["extra"])}</td></tr>' for r in res["righe"])
    corpo += (f'<h2>One payroll across four states</h2><p>A business that is not grouped pays $4.5 million of wages for the whole of {ANNO}: our calculator applies each state\'s formula. '
              f'Note how Victoria, Queensland and WA give less than their share of the full threshold, because total wages of $4.5 million are inside their taper ranges.</p>'
              f'<div class="tab"><table class="dati"><thead><tr><th scope="col">State</th><th scope="col" class="n">Wages</th><th scope="col" class="n">Share</th><th scope="col" class="n">Threshold used</th><th scope="col" class="n">Payroll tax</th></tr></thead>'
              f'<tbody>{righe}</tbody><tfoot><tr><td><strong>Total</strong></td><td class="n"><strong>{soldi(res["W"])}</strong></td><td></td><td></td><td class="n"><strong>{soldi(res["complessivo"])}</strong></td></tr></tfoot></table></div>'
              f'<p><a class="btn" href="/calculator/?nsw=1800000&amp;vic=1200000&amp;qld=900000&amp;wa=600000">Open this example in the calculator</a></p>')
    corpo += "<h2>Which state taxes an employee who works in several states?</h2><div class=\"testo\">"
    corpo += rim.t("<p>The harmonised nexus rules decide where each month's wages are taxable. If the employee works only in one state, it is that state. Otherwise the tests apply in order: "
                   "where the employee is based (principal place of residence); if not based in Australia, where the employer is based; then where the wages are paid; and finally where the services are mainly performed.[[act_act,tas_guide]] "
                   "RevenueSA has a page on the same rules.[[sa_nexus]]</p></div>")
    faq_html, faq_ld = faq_blocco("interstate-wages", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("interstate-wages/") + rim.elenco()
    testata = banda("Interstate wages", "Payroll tax and interstate wages: how the threshold is shared",
                    "If you pay wages in more than one state, each state gives you only a share of its threshold. Here is the rule, every official example, and a four-state worked case.", corta=True, icona="map")
    pagina("interstate-wages/", "Payroll Tax Interstate Wages: Sharing the Threshold",
           "How Australian payroll tax thresholds are shared when you pay wages in several states: the rule, official examples from NSW, VIC, QLD, WA, SA and TAS, and nexus.",
           corpo, testata, briciole=[("Home", ""), ("Interstate wages", "interstate-wages/")], jsonld=[faq_ld] if faq_ld else None)


def grouping():
    rim = Rimandi()
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t("<p>Grouping rules stop a business from splitting into several entities to claim several thresholds. Businesses that are grouped are treated as a single employer: the group's wages "
                   "are added together, one member claims the threshold, and the others pay on all their wages.[[vic_grouping,nsw_rates]] The rules are harmonised across the states,[[portal_rates]] "
                   "but each office has its own pages and decisions.</p></div>")
    corpo += "<h2>How businesses become grouped</h2><div class=\"testo\"><ul>"
    corpo += rim.t("<li><strong>Related corporations</strong>: companies that are related bodies corporate (holding company and subsidiaries, including through an overseas parent). They cannot apply to be excluded.[[vic_grouping]]</li>"
                   "<li><strong>Shared employees</strong>: an employer whose employees perform duties for another business, or are employed mainly to work for it.[[vic_grouping]]</li>"
                   "<li><strong>Common control</strong>: the same person or set of persons has a controlling interest (more than 50%) in two businesses, whether they are companies, partnerships, trusts or sole traders; "
                   "beneficiaries of discretionary trusts are treated as holding more than 50%.[[vic_grouping]]</li>"
                   "<li><strong>Tracing</strong>: interests held through other entities are traced, and groups that share a member are combined.[[vic_grouping]]</li></ul></div>")
    corpo += "<h2>What grouping changes</h2><div class=\"testo\">"
    corpo += rim.t("<p>Only the designated group employer (DGE) is entitled to the threshold or deduction; in some states an unused part can be allocated to another member in the annual return.[[portal_lodging]] "
                   "The DGE works out the threshold on the group's wages: in NSW, $1,200,000 × group NSW wages ÷ group Australian wages.[[nsw_rates]] Use the group's totals in our <a href=\"/calculator/\">calculator</a>: "
                   "the result is the group total.</p>"
                   "<p>Failing to register a related entity under the grouping provisions is one of the reasons unregistered employers are penalised each year.[[portal_registration]]</p>"
                   "<p>The Commissioner has discretion to exclude a member from a group in certain circumstances (not related corporations): in Victoria the factors are in Revenue Ruling PTA-031v2.[[vic_grouping]] "
                   "In Queensland, the Home Ownership and Other Legislation Amendment Act 2026, assented on 22 October 2026, confirms that the Commissioner may exclude a set of persons from a group.[[qld_hoola]]</p></div>")
    corpo += AD
    links = []
    for s in ORDINE:
        fid = J[s]["fonti"].get("grouping") or J[s]["fonti"].get("legge")
        lab = "grouping page" if J[s]["fonti"].get("grouping") else "Payroll Tax Act (grouping provisions)"
        links.append(f'<li><strong>{h(J[s]["nome"])}</strong>: <a href="{h(url_fonte(fid))}" rel="noopener">{h(J[s]["ufficio"] if J[s]["fonti"].get("grouping") else FONTI[fid]["chi"])}, {lab}</a>{rim.ref([fid])}</li>')
    corpo += f'<h2>Official grouping pages</h2><ul class="testo">{"".join(links)}</ul>'
    corpo += '<p class="small">We summarise the rules but do not decide whether your businesses are grouped: that depends on facts the revenue offices assess case by case.</p>'
    faq_html, faq_ld = faq_blocco("grouping", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("grouping/") + rim.elenco()
    testata = banda("Grouping", "Payroll tax grouping: when businesses share one threshold",
                    "Related companies, shared employees and common control can make several businesses one employer for payroll tax. A short guide with the official page for every state.", corta=True, icona="people")
    pagina("grouping/", "Payroll Tax Grouping Rules in Australia, State by State",
           "Payroll tax grouping in Australia: related corporations, shared employees, common control, the designated group employer and the official page for every state.",
           corpo, testata, briciole=[("Home", ""), ("Grouping", "grouping/")], jsonld=[faq_ld] if faq_ld else None)


def regionale():
    rim = Rimandi()
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t("<p>Two states charge regional employers less: <strong>Victoria</strong> taxes them at <strong>1.2125%</strong> instead of 4.85%,[[vic_regional]] and <strong>Queensland</strong> takes "
                   "<strong>1%</strong> off its rate until 30 June 2030.[[qld_regional]] No other state or territory has a regional rate for 2026-27.[[portal_rates]]</p></div>")
    corpo += ('<div class="tab"><table class="dati"><thead><tr><th scope="col"></th><th scope="col">Victoria</th><th scope="col">Queensland</th></tr></thead><tbody>'
              + rim.t('<tr><th scope="row">Rate</th><td>1.2125% (standard 4.85%)[[vic_regional]]</td><td>3.75%, or 3.95% above $6.5m (standard 4.75% / 4.95%)[[qld_regional]]</td></tr>'
                      '<tr><th scope="row">Wage test</th><td>At least 85% of Victorian taxable wages paid to regional employees</td><td>At least 85% of Queensland taxable wages paid to regional employees</td></tr>'
                      '<tr><th scope="row">Who is regional</th><td>Employees who do more than half of their work for you in regional Victoria</td><td>Employees whose principal place of residence is in regional Queensland</td></tr>'
                      '<tr><th scope="row">Employer test</th><td>No separate test: only the 85% rule</td><td>Principal place of employment (registered ABN address) in regional Queensland</td></tr>'
                      '<tr><th scope="row">Limits</th><td>Tested monthly; for the annual return, over the whole year</td><td>Until 30 June 2030; not above $350 million of wages</td></tr>'
                      '<tr><th scope="row">Groups</th><td>Each member tested on its own</td><td>Each member can qualify on its own</td></tr>')
              + "</tbody></table></div>")
    corpo += "<h2>Regional Victoria</h2><div class=\"testo\">"
    corpo += rim.t("<p>Regional Victoria means 48 regional councils, from Alpine Shire to Yarriambiack Shire (including Ballarat, Greater Bendigo, Greater Geelong, Latrobe, Mildura, Warrnambool and Wodonga), "
                   "plus the six alpine resorts of Mt Baw Baw, Mt Buller, Mt Hotham, Mt Stirling, Falls Creek and Lake Mountain. Only work done in Victoria counts: an employee who spends 60% of a month interstate, "
                   "10% in Melbourne and 30% in regional Victoria spent 75% of their Victorian time in regional Victoria, so is a regional employee.[[vic_regional]]</p>"
                   "<p>If you meet the 85% rule for the year but not every month, you pay 4.85% in those months and get a refund in the annual reconciliation.[[vic_regional]]</p></div>")
    corpo += "<h2>Regional Queensland</h2><div class=\"testo\">"
    corpo += rim.t("<p>Regional Queensland is defined by seven ABS statistical areas (SA4): Cairns, Central Queensland, Darling Downs – Maranoa, Mackay – Isaac – Whitsunday, Queensland – Outback, "
                   "Townsville and Wide Bay. Short-term residents such as working holiday makers and PALM scheme workers generally do not have their principal place of residence there.[[qld_regional]]</p>"
                   "<p>On 11 November 2026 QRO announced a temporary amnesty, until 31 December 2026, for certain employers who incorrectly claimed the discount.[[qld_amnesty]]</p></div>")
    corpo += "<h2>The 48 regional Victorian councils</h2><div class=\"testo\">"
    corpo += rim.t("<p>" + ", ".join(CONSIGLI_VIC) + ". The six alpine resorts (Mt Baw Baw, Mt Buller, Mt Hotham, Mt Stirling, Falls Creek and Lake Mountain) also count.[[vic_regional]]</p></div>")
    corpo += "<h2>Victoria: monthly returns versus the annual test</h2><div class=\"testo\">"
    corpo += rim.t("<p>The SRO's own example: in 2024-25 RedCar paid $100,000 of Victorian taxable wages every month ($1,200,000 for the year). Its regional employees received $90,000 a month "
                   "from July to October and from March to June, but only $80,000 a month from November to February. In those four months it was below 85%, so its monthly returns used 4.85%; "
                   "in the other eight months it used 1.2125%. Over the year it paid $1,040,000 to regional employees, 86.67% of its wages, so the annual reconciliation applied 1.2125% to the "
                   "whole year and refunded the overpaid tax for November to February.[[vic_regional]]</p>"
                   "<p>Groups that lodge a joint (schedule) return split the taxable amount: the share of wages paid by regional members is taxed at 1.2125% and the rest at 4.85%. In the SRO example, "
                   "three grouped businesses paid $90,000 in July 2024 against a $75,000 monthly threshold; one third of the wages came from a regional member, so $5,000 of the $15,000 taxable amount "
                   "was taxed at 1.2125% and $10,000 at 4.85%.[[vic_regional]] For a joint return, enter only the group totals in our calculator and work the split out by hand.</p></div>")
    corpo += "<h2>Queensland: residence, ABN address and groups</h2><div class=\"testo\">"
    corpo += rim.t("<p>An employee's principal place of residence is where they usually live, judged on facts such as whether they live there daily, where their belongings and immediate family are, "
                   "how long they have lived there, their mail and electoral roll address, the address on their driver licence and whose name the utility accounts are in.[[qld_regional]]</p>"
                   "<p>Your principal place of employment is your registered ABN business address on the Australian Business Register; without an ABN, your principal place of business.[[qld_regional]]</p>"
                   "<p>In a group, each member is tested on its own: in QRO's example, two companies grouped with $7 million of Australian wages pay 3.95% (the regional member) and 4.95% "
                   "(the member that is not regional).[[qld_regional]]</p>"
                   "<p>The discount stops above $350 million of wages. QRO's page describes the cap as Australian taxable wages; the Payroll Tax Act 1971, s 10A(4), refers to the taxable wages paid by "
                   "the employer during the return period. Our calculator applies the cap to total Australian wages and says so; if your Queensland wages alone are under $350 million but your "
                   "Australian wages are above it, ask QRO.[[qld_regional,qld_act]]</p></div>")
    corpo += AD
    e1 = nostro_esempio({"vic": 2000000}, descr="Victoria-only employer, $2,000,000 of wages, standard rate")
    corpo += "<h2>What the regional rate is worth</h2>" + e1
    res = motore.calcola(P, {"vic": 2000000}, GIORNI_ANNO, GIORNI_ANNO, regionale_vic=True)
    r = res["righe"][0]
    corpo += (f'<div class="esempio"><p><strong>The same employer as a regional employer</strong> <span class="etich">our calculation</span></p><p class="small">threshold {soldi(r["soglia"])} · '
              f'rate {pct(r["aliquota"])} · payroll tax <span class="ok">{soldi(r["tassa"])}</span></p></div>')
    res2 = motore.calcola(P, {"qld": 3000000}, GIORNI_ANNO, GIORNI_ANNO)
    res3 = motore.calcola(P, {"qld": 3000000}, GIORNI_ANNO, GIORNI_ANNO, regionale_qld=True)
    corpo += (f'<div class="esempio"><p><strong>Queensland-only employer, $3,000,000 of wages</strong> <span class="etich">our calculation</span></p><p class="small">deduction {soldi(res2["righe"][0]["soglia"])} · '
              f'standard 4.75%: <span class="ok">{soldi(res2["complessivo"])}</span> · regional 3.75%: <span class="ok">{soldi(res3["complessivo"])}</span></p></div>')
    corpo += '<p><a class="btn" href="/calculator/?vic=2000000&amp;rv=1">Try it in the calculator</a></p>'
    faq_html, faq_ld = faq_blocco("regional-rates", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("regional-rates/") + rim.elenco()
    testata = banda("Regional rates", "Regional payroll tax rates: Victoria 1.2125% and the Queensland 1% discount",
                    "Who qualifies, which areas count and what the lower rate is worth, from the State Revenue Office Victoria and the Queensland Revenue Office.", corta=True, icona="map")
    pagina("regional-rates/", "Regional Payroll Tax Rates: Victoria and Queensland",
           "Regional payroll tax 2026-27: Victoria 1.2125% (85% rule) and Queensland's 1% discount to 2030 (3.75%/3.95%), who qualifies and what it saves.",
           corpo, testata, briciole=[("Home", ""), ("Regional rates", "regional-rates/")], jsonld=[faq_ld] if faq_ld else None)


def storico_pagina():
    rim = Rimandi()
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t("<p>Annual thresholds and rates for each financial year since 2021-22, from the historical tables of the revenue offices and the ACT legislation register. Where we could not read an official "
                   "figure for a year we leave the cell empty rather than fill it from memory.</p></div>")
    corpo += tabella_storico(ORDINE, rim)
    corpo += "<h2>The main changes, year by year</h2><div class=\"testo\"><ul>"
    corpo += rim.t("<li><strong>2022-23</strong>: Queensland widened its deduction range so that the deduction reaches zero at $10.4 million instead of $6.5 million, from 1 January 2023.[[qld_deductions]]</li>"
                   "<li><strong>2023-24</strong>: Western Australia's extra 6% and 6.5% rates for payrolls above $100 million ended on 30 June 2023.[[wa_calc]] Victoria's COVID-19 debt surcharge began on 1 July 2023 (the mental health and wellbeing surcharge started on 1 January 2022).[[vic_rates]]</li>"
                   "<li><strong>2024-25</strong>: Victoria raised its threshold from $700,000 to $900,000 and started phasing it out between $3m and $5m (45%); the ACT added surcharges for employers above $50 million.[[vic_hist,vic_phase,act_det2024]]</li>"
                   "<li><strong>2025-26</strong>: Victoria went to $1,000,000 and a 50% phase-out; the ACT raised its surcharges and, from 1 January 2026, charged 8.75% on employers above $150 million.[[vic_rates,act_det2025,act_act]]</li>"
                   "<li><strong>2026-27</strong>: the ACT threshold fell to $1,750,000 with five rates from 6.75% to 8.75%; the NT added 6.5% for payrolls of $100 million or more.[[act_det2026,nt_act]]</li></ul></div>")
    corpo += AD
    corpo += box_affiliati("thresholds-history")
    faq_html, faq_ld = faq_blocco("thresholds-history", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("thresholds-history/") + rim.elenco()
    testata = banda("Thresholds history", "Payroll tax thresholds and rates by year, 2021-22 to 2026-27",
                    "How the threshold and rate have changed in every state and territory, with the official source for each figure.", corta=True, icona="trend")
    pagina("thresholds-history/", "Payroll Tax Thresholds History by State, 2021-2027",
           "Payroll tax thresholds and rates for every Australian state and territory from 2021-22 to 2026-27, each figure linked to its official source.",
           corpo, testata, briciole=[("Home", ""), ("Thresholds history", "thresholds-history/")], jsonld=[faq_ld] if faq_ld else None)


def scadenze():
    rim = Rimandi()
    righe = []
    fonti = {"nsw": ["nsw_keydates"], "vic": ["vic_monthly", "vic_annual"], "qld": ["qld_due"], "wa": ["wa_returns"], "sa": ["sa_returns"], "tas": ["tas_lodge"], "act": ["act_act"], "nt": ["nt_act"]}
    mensile = {"nsw": "7th of the next month (December: 14 January 2027)", "vic": "7th of the next month", "qld": "7 days after the month (December: 14 January 2027)",
               "wa": "7th of the next month", "sa": "7th of the next month", "tas": "7th of the next month", "act": "Within 7 days after the end of the month",
               "nt": "Within 21 days after the end of the month"}
    annuale = {"nsw": "28 July 2027", "vic": "21 July", "qld": "21 July 2027", "wa": "21 July", "sa": "28 July 2027", "tas": "21 July", "act": "28 July (28 days after June)", "nt": "21 July (21 days after June)"}
    for s in ORDINE:
        righe.append(f'<tr><td><a href="/{s}/">{h(J[s]["nome"])}</a></td><td data-l="Monthly return and payment">{h(mensile[s])}</td><td data-l="Annual return">{h(annuale[s])}{rim.ref(fonti[s])}</td></tr>')
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t("<p>Registered employers generally lodge a return every month, due on the 7th of the following month, and an annual return at the end of the financial year: by <strong>21 July</strong>, "
                   "or by <strong>28 July</strong> in the ACT, NSW and South Australia. When a due date falls on a weekend or public holiday, lodgement and payment are accepted on the next business day.[[portal_lodging,portal_rates]]</p></div>")
    corpo += (f'<h2>Due dates by state, {ANNO}</h2><div class="tab"><table class="dati stack"><thead><tr><th scope="col">State or territory</th><th scope="col">Monthly return and payment</th>'
              f'<th scope="col">Annual return ({ANNO})</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    corpo += rim.t('<p class="small">The Northern Territory dates come from the Payroll Tax Act 2009, s 87 (the NT revenue website does not answer our checking server). Some offices let small payrolls lodge '
                   'quarterly, half-yearly or annually: Western Australia, for example, allows quarterly returns under $150,000 of estimated annual tax and annual returns under $20,000.[[wa_returns]]</p>')
    cal = [("July 2026", "7 August 2026"), ("August 2026", "7 September 2026"), ("September 2026", "7 October 2026"), ("October 2026", "9 November 2026"),
           ("November 2026", "7 December 2026"), ("December 2026", "14 January 2027"), ("January 2027", "8 February 2027"), ("February 2027", "8 March 2027"),
           ("March 2027", "7 April 2027"), ("April 2027", "7 May 2027"), ("May 2027", "7 June 2027"), ("June 2027 and annual return", "21 July 2027 (QLD) · 28 July 2027 (NSW)")]
    corpo += (f'<h2>NSW and Queensland monthly calendar, {ANNO}</h2><p>Both offices publish the same monthly dates for {ANNO}; there is no June monthly return because June is included in the annual return.{rim.ref(["nsw_keydates", "qld_due"])}</p>'
              '<div class="tab"><table class="dati"><thead><tr><th scope="col">Return for</th><th scope="col">Due</th></tr></thead><tbody>'
              + "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in cal) + "</tbody></table></div>")
    corpo += rim.t('<p class="small">South Australia lists the same monthly dates from August 2026 to June 2027 except 9 March 2027 for February.[[sa_returns]]</p>')
    corpo += AD
    corpo += box_affiliati("due-dates")
    faq_html, faq_ld = faq_blocco("due-dates", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("due-dates/") + rim.elenco()
    testata = banda(f"Due dates · {ANNO}", "Payroll tax due dates 2026-27: monthly returns and annual reconciliation",
                    "When each state wants its monthly return and the annual return, with the official calendars of NSW and Queensland.", corta=True, icona="calendar")
    pagina("due-dates/", "Payroll Tax Due Dates 2026-27 by State (21 and 28 July)",
           "Payroll tax due dates 2026-27 in every state: monthly returns by the 7th (NT 21 days) and the annual return by 21 July or 28 July (NSW, SA, ACT).",
           corpo, testata, briciole=[("Home", ""), ("Due dates", "due-dates/")], jsonld=[faq_ld] if faq_ld else None)


def cambiamenti():
    rim = Rimandi()
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t("<p>Two jurisdictions changed their payroll tax on 1 July 2026: the <strong>ACT</strong> and the <strong>Northern Territory</strong>. The joint portal of the revenue offices, "
                   "last updated on 28 October 2026, shows the other six unchanged.[[portal_rates]] Payday Super, a federal change for every employer, also started on 1 July 2026.[[payday_act]]</p></div>")
    corpo += "<h2>ACT: lower threshold, five rates</h2><div class=\"testo\">"
    corpo += rim.t("<p>The 2026 determination lowered the threshold from $2,000,000 to <strong>$1,750,000</strong> (monthly $145,833.33) and folded the surcharges for larger employers into a single "
                   "general rate set by total wages: 6.75% up to $20m, 6.85% up to $50m, 7.35% up to $100m, 7.85% up to $150m and 8.75% above.[[act_det2026,act_es2026]] "
                   "In 2025-26 the rate was 6.85%, plus 0.5% above $50m and 1% above $100m, with 8.75% from 1 January 2026 for employers above $150m.[[act_det2025,act_act]]</p></div>")
    righe = []
    for w in (3000000, 10000000, 30000000):
        t26 = motore.calcola(P, {"act": w}, GIORNI_ANNO, GIORNI_ANNO)["complessivo"]
        t25 = (w - 2000000) * 0.0685
        righe.append(f'<tr><td class="n">{soldi(w)}</td><td class="n">{soldi(t25)}</td><td class="n">{soldi(t26)}</td><td class="n">{"+" if t26 >= t25 else "−"}{soldi(abs(t26 - t25))}</td></tr>')
    corpo += ('<h3>What it means for an ACT-only employer</h3><p class="small">Our calculation with the two determinations: (wages − threshold) × rate; 2025-26 at 6.85% with the $2m threshold (no surcharge below $50m).</p>'
              '<div class="tab"><table class="dati"><thead><tr><th scope="col" class="n">ACT wages, full year</th><th scope="col" class="n">2025-26</th><th scope="col" class="n">2026-27</th><th scope="col" class="n">Change</th></tr></thead><tbody>'
              + "".join(righe) + "</tbody></table></div>")
    corpo += "<h2>Northern Territory: 6.5% for payrolls of $100 million or more</h2><div class=\"testo\">"
    corpo += rim.t("<p>From 1 July 2026 the Payroll Tax Act 2009 charges <strong>6.5%</strong> instead of 5.5% when the Australian wages of the employer, or of its group, are $100 million or more for the year. "
                   "The $2.5 million threshold, the deduction and the 5.5% rate are unchanged for everyone else.[[nt_act,portal_rates]]</p></div>")
    corpo += "<h2>The other states</h2><div class=\"testo\"><ul>"
    corpo += rim.t("<li><strong>NSW</strong>: $1,200,000 and 5.45%, as every year since 2022-23.[[nsw_rates]]</li>"
                   "<li><strong>Victoria</strong>: $1,000,000 and the 50% phase-out, both from 2025-26; the two surcharges for Australian wages above $10 million continue, the COVID-19 debt surcharge until 30 June 2033.[[vic_rates,vic_surcharges]]</li>"
                   "<li><strong>Queensland</strong>: unchanged rates; regional discount to 30 June 2030 with an amnesty until 31 December 2026 for certain incorrect claims; "
                   "the Home Ownership and Other Legislation Amendment Act 2026, assented on 22 October 2026, confirms the Commissioner may exclude a set of persons from a group.[[qld_regional,qld_amnesty,qld_hoola]]</li>"
                   "<li><strong>Western Australia</strong>: $1,000,000, 5.5%, diminishing to $7.5m.[[wa_calc]]</li>"
                   "<li><strong>South Australia</strong>: $1,500,000 and up to 4.95%.[[sa_rates]]</li>"
                   "<li><strong>Tasmania</strong>: $1.25m and $2m, 4% and 6.1%.[[tas_rates]]</li></ul></div>")
    a = motore.calcola(P, {"act": 20000000}, GIORNI_ANNO, GIORNI_ANNO)["complessivo"]
    b = motore.calcola(P, {"act": 20000001}, GIORNI_ANNO, GIORNI_ANNO)["complessivo"]
    corpo += "<h2>ACT: watch the bracket limits</h2><div class=\"testo\">"
    corpo += rim.t(f"<p>Because the ACT rate is chosen by total wages and then applied to all ACT wages above the threshold, one more dollar of wages at a bracket limit changes the tax on everything. "
                   f"An ACT-only employer paying $20,000,000 for the full year pays {soldi(a)} at 6.75%; at $20,000,001 the rate is 6.85% and the tax {soldi(b)}, "
                   f"{soldi(b - a)} more (our calculation with the formula of the Act).[[act_act,act_det2026]]</p>"
                   "<p>Monthly returns use their own brackets on total monthly wages: 6.75% above $145,833.33 up to $1,666,666.66, 6.85% up to $4,166,666.66, 7.35% up to $8,333,333.33, "
                   "7.85% up to $12,500,000 and 8.75% above.[[act_det2026]] The annual return then settles the year on the annual brackets.</p>"
                   "<p>Five eligible universities are capped at 6.85%: Australian Catholic University, Charles Sturt University, The Australian National University, The University of New South Wales "
                   "and University of Canberra. One in the lowest bracket pays 6.75%.[[act_det2026,act_es2026]]</p></div>")
    n1 = motore.calcola(P, {"nt": 120000000}, GIORNI_ANNO, GIORNI_ANNO)["complessivo"]
    corpo += "<h2>NT: what 6.5% means in dollars</h2><div class=\"testo\">"
    corpo += rim.t(f"<p>The deduction is already nil at $7.5 million, so the new rate applies to every NT dollar. An NT-only employer with $120 million of wages pays {soldi(n1)} at 6.5%, "
                   f"{soldi(120000000 * 0.01)} more than at 5.5% (our calculation). A group whose Australian wages reach $100 million pays 6.5% on its NT wages even if only a small part is paid "
                   "in the Territory.[[nt_act]]</p></div>")
    righe = []
    for s_ in ORDINE:
        v25 = STORICO["righe"][s_].get("2025-26")
        v26 = STORICO["righe"][s_].get("2026-27")
        righe.append(f'<tr><td><a href="/{s_}/">{h(J[s_]["nome"])}</a></td><td data-l="2025-26">{soldi(v25["soglia"]) if v25 else "–"}<br><span class="small">{h(v25["aliquota"]) if v25 else ""}</span></td>'
                     f'<td data-l="2026-27">{soldi(v26["soglia"])}<br><span class="small">{h(v26["aliquota"])}</span>{rim.ref(v26["fonti"])}</td></tr>')
    corpo += ('<h2>2025-26 and 2026-27 side by side</h2><div class="tab"><table class="dati stack"><thead><tr><th scope="col">State or territory</th><th scope="col">2025-26</th>'
              '<th scope="col">2026-27</th></tr></thead><tbody>' + "".join(righe) + "</tbody></table></div>")
    corpo += ("<h2>Payday Super, for every employer</h2><div class=\"testo\">" + rim.t("<p>Separate from state payroll tax, the Payday Superannuation Act moved super guarantee "
              "contributions from quarterly to every payday from 1 July 2026: the fund must receive them within 7 business days of each payday.[[payday_act]] "
              "<a href=\"/payday-super/\">How it works, with a worked example</a>.</p></div>"))
    corpo += AD
    faq_html, faq_ld = faq_blocco("what-changed-2026-27", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("what-changed-2026-27/") + rim.elenco()
    testata = banda("What changed · 1 July 2026", "Payroll tax changes for 2026-27",
                    "New ACT threshold and brackets, a 6.5% NT rate for large payrolls, and what stayed the same in the other six states.", corta=True, icona="trend")
    pagina("what-changed-2026-27/", "Payroll Tax Changes 2026-27: ACT Brackets, NT 6.5%",
           "What changed in Australian payroll tax on 1 July 2026: ACT $1.75m threshold and 6.75%-8.75% rates, NT 6.5% above $100m, other states unchanged.",
           corpo, testata, briciole=[("Home", ""), ("What changed in 2026-27", "what-changed-2026-27/")], jsonld=[faq_ld] if faq_ld else None)


PS = carica("payday_super.json")


def payday():
    rim = Rimandi()
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t(f"<p>Payday Super is a federal change, separate from state payroll tax. The {PS['legge']} (assented to on {data_lunga(PS['assenso'])}) "
                   f"commenced on <strong>{data_lunga(PS['inizio'])}</strong>.[[payday_act]] Instead of paying super guarantee contributions quarterly, employers must make sure contributions reach each "
                   "employee's fund shortly after every payday.</p></div>")
    for sez in PS["sezioni"]:
        corpo += f'<h2>{h(sez["titolo"])}</h2><div class="testo">' + "".join(f"<p>{rim.t(x)}</p>" for x in sez["paragrafi"]) + "</div>"
        if sez is PS["sezioni"][1]:
            es = PS["esempio"]
            righe = "".join(f'<tr><td>{h(a)}</td><td>{h(b)}</td></tr>' for a, b in es["righe"])
            corpo += (f'<h2>{h(es["titolo"])}</h2><p class="small">{h(es["intro"])}{rim.ref(["payday_act"])}</p>'
                      f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Step</th><th scope="col">Result</th></tr></thead><tbody>{righe}</tbody></table></div>'
                      f'<p>{h(es["nota"])}</p>')
    corpo += AD
    corpo += box_affiliati("payday-super")
    corpo += ('<h2>Payday Super and payroll tax</h2><div class="testo"><p>The two are separate, but connected: employer super contributions are taxable wages for payroll tax in every state.'
              + rim.ref(["nsw_register"]) + ' A payroll that grows past a state threshold has to manage both: monthly payroll tax returns and super paid within days of each payday. '
              'See <a href="/over-the-threshold/">what to do when you go over the threshold</a>.</p></div>')
    faq_html, faq_ld = faq_blocco("payday-super", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("payday-super/") + rim.elenco()
    testata = banda("Payday Super · from 1 July 2026", "Payday Super: super due within 7 business days of payday",
                    "What the Payday Superannuation Act 2025 requires of employers from 1 July 2026, read from the Act itself, with a worked example.", corta=True, icona="clock")
    pagina("payday-super/", "Payday Super from 1 July 2026: 7 Business Days Rule",
           "Payday Super from 1 July 2026: super must reach the fund within 7 business days of each payday. The rules, the 20-day exception, the charge and a worked example.",
           corpo, testata, briciole=[("Home", ""), ("Payday Super", "payday-super/")], jsonld=[faq_ld] if faq_ld else None)


def oltre_soglia():
    rim = Rimandi()
    corpo = '<div class="testo pull card" style="margin-bottom:8px">'
    corpo += rim.t("<p>Payroll tax is self-assessed: you must register with <strong>each</strong> state and territory where you pay taxable wages once your Australia-wide wages (or your group's) exceed "
                   "the threshold.[[portal_registration]] It is collected monthly but it is an annual tax, based on the wages paid in the whole financial year,[[act_es2026]] so the annual return "
                   "settles the year.</p></div>")
    corpo += "<h2>Step by step</h2><ol class=\"testo\">"
    corpo += rim.t("<li><strong>Watch the monthly figure.</strong> Most offices test a monthly (or weekly) threshold against total Australian wages: see the table below.</li>"
                   "<li><strong>Register on time.</strong> NSW and Western Australia want you registered within 7 days after the month in which you go over; Queensland within 7 days of the first month "
                   "in which wages exceed $25,000 a week.[[nsw_register,wa_register,qld_register]] Registration takes your wage history: NSW asks for wages for the current year and the 4 previous ones.[[nsw_register]]</li>"
                   "<li><strong>Check grouping.</strong> If related businesses are grouped, the group's wages decide whether you register, and one member claims the threshold.[[portal_registration,portal_lodging]] See <a href=\"/grouping/\">grouping</a>.</li>"
                   "<li><strong>Lodge monthly.</strong> Returns are generally due on the 7th of the next month.[[portal_lodging]] See <a href=\"/due-dates/\">due dates</a>.</li>"
                   "<li><strong>Reconcile in July.</strong> The annual return (21 July, or 28 July in NSW, SA and the ACT) works out the tax for the whole year with your real threshold share.[[portal_rates]]</li></ol>")
    reg = {"nsw": ("$92,055 to $101,918 a month", "nsw_rates"), "vic": ("$83,333 a month", "vic_rates"), "qld": ("$25,000 a week", "qld_register"),
           "wa": ("$83,333 a month", "wa_register"), "sa": ("$125,000 a month ($28,846 a week)", "sa_register"), "tas": ("$24,038 a week during a month", "tas_register"),
           "act": ("$145,833.33 a month", "act_det2026"), "nt": ("$208,333 a month", "portal_rates")}
    righe = "".join(f'<tr><td><a href="/{s}/">{h(J[s]["nome"])}</a></td><td>{h(reg[s][0])}{rim.ref([reg[s][1]])}</td></tr>' for s in ORDINE)
    corpo += f'<h2>Registration thresholds</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">State or territory</th><th scope="col">Register when Australian wages are above</th></tr></thead><tbody>{righe}</tbody></table></div>'
    corpo += "<h2>If you registered late</h2><div class=\"testo\">"
    corpo += rim.t("<p>The revenue offices audit employers and match data with the ATO. Penalties may apply for failing to register on time, for not registering in every state where you pay wages, "
                   "and for not registering a related entity under the grouping rules. Employers who voluntarily declare their liabilities may receive significantly lower penalties than those who do not.[[portal_registration]]</p></div>")
    corpo += AD
    corpo += box_affiliati("over-the-threshold")
    corpo += '<p><a class="btn" href="/calculator/">Estimate your payroll tax</a></p>'
    faq_html, faq_ld = faq_blocco("over-the-threshold", rim)
    corpo += faq_html + '<h2>Guides</h2>' + griglia_guide("over-the-threshold/") + rim.elenco()
    testata = banda("Over the threshold", "Over the payroll tax threshold? What to do next",
                    "Registering in each state, the monthly and weekly thresholds, grouping, and what happens in the annual return.", corta=True, icona="alert")
    pagina("over-the-threshold/", "Over the Payroll Tax Threshold? Registering, State by State",
           "Gone over the payroll tax threshold? Register in each state where you pay wages: monthly and weekly thresholds, the 7-day deadlines, grouping and penalties.",
           corpo, testata, briciole=[("Home", ""), ("Over the threshold", "over-the-threshold/")], jsonld=[faq_ld] if faq_ld else None)


def about():
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{NOME}</strong> is an independent publication, part of a small network of websites that turn official data into plain-language guides and tools. '
             'This site puts the payroll tax rules of Australia\'s eight states and territories side by side and estimates the tax with the formulas they publish. It exists because each revenue '
             'office explains its own rules well, but none compares the states or shares a threshold across several of them in one tool.</p>'
             '<p>We are not a government website, a tax agent or an accounting firm, and we are not linked to any revenue office or software company. The site gives general information, '
             'not tax advice.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Only figures we have read on an official page or in the legislation, each linked to its source with the date we checked it.</li>'
             '<li>Formulas taken from the revenue offices and the payroll tax Acts, tested against every official worked example we could find.</li>'
             '<li>Where an official source cannot be read, or the law leaves a case open, we say so instead of filling the gap.</li></ul>'
             '<h2>How the site is paid for</h2><div class="testo"><p>The site shows advertising served by Google AdSense. Google\'s automatic placement decides where ads appear on a page; '
             'the space we reserve for ads comes after the calculator. In future the site may link to payroll software through partner programmes; any such link will be labelled, '
             'and partners will never decide what we publish or change a figure.</p></div>'
             '<h2>Your data</h2><div class="testo"><p>The calculator runs entirely in your browser: the wages you type are not sent to us or to anyone else. See the <a href="/privacy/">privacy page</a>.</p></div>'
             '<h2>Corrections</h2><div class="testo"><p>Rates change every 1 July and sometimes mid-year. We re-read every official source on a schedule and before each update. If you spot an error, '
             'use the <a href="/how-we-check/#corrections">corrections form</a>: we check it against the official source and fix the page.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, what it publishes and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", "About Payroll Tax by State: an independent Australian payroll tax comparison and calculator built only from official sources.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")])


MODULO_CORREZIONI = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card" data-correzioni>
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or figure<input type="text" name="page" required maxlength="300" placeholder="For example /vic/ or the ACT threshold"></label>
<label>What is wrong?<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<label>Your email (optional, only if you want a reply)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I agree that this message, and my email if I gave one, is stored to check and answer the correction (see <a href="/privacy/#corrections">privacy</a>).</span></label>
<p class="errore" data-errore hidden>The message was not sent. Please try again.</p>
<button type="submit" class="btn">Send correction</button>
</form>
<p class="ok" data-ok hidden><strong>Thank you.</strong> We will check it against the official source.</p>"""


def come_controlliamo():
    rim = Rimandi()
    lette = sum(1 for k, v in ESITI.items() if not FONTI[k].get("non_letta") and v.get("http") == 200)
    frasi = sum(len(FONTI[k].get("cerca", [])) for k in FONTI if not FONTI[k].get("non_letta"))
    ufficiali = [c for c in ESEMPI["casi"] if not c.get("legge")]
    corpo = ('<div class="testo pull card">'
             f'<p>Every figure on this site comes from an official page or a piece of legislation. On {data_lunga(CONTROLLO)} we read <strong>{lette}</strong> official sources and checked '
             f'<strong>{frasi}</strong> exact phrases and figures in them (for example “$1,200,000 x (184 ÷ 365) = $604,931.51” on the Revenue NSW page). If a phrase disappears from its page, '
             'our checks fail and the figure is reviewed before it stays on the site.</p></div>')
    corpo += "<h2>Where the figures come from</h2><div class=\"testo\"><ul>"
    corpo += rim.t("<li>The joint portal of the eight revenue offices, payrolltax.gov.au, for the current rates and thresholds of every state.[[portal_rates]]</li>"
                   "<li>The pages of Revenue NSW, the State Revenue Offices of Victoria and Tasmania, the Queensland Revenue Office, RevenueWA and RevenueSA.[[nsw_rates,vic_rates,qld_rates,wa_calc,sa_rates,tas_rates]]</li>"
                   "<li>The legislation itself where the formula matters: the payroll tax Acts of Victoria, Queensland, Western Australia, South Australia, Tasmania, the ACT and the Northern Territory, and the ACT 2026 determination.[[vic_act,qld_act,wa_act,sa_act,tas_act,act_act,act_det2026,nt_act]]</li>"
                   "<li>The Federal Register of Legislation for Payday Super.[[payday_act]]</li></ul></div>")
    conteggio = {}
    for k in FONTI:
        pref = k.split("_")[0]
        conteggio[pref] = conteggio.get(pref, 0) + 1
    nomi = {"portal": "Joint revenue office portal", "nsw": "New South Wales", "vic": "Victoria", "qld": "Queensland", "wa": "Western Australia", "sa": "South Australia",
            "tas": "Tasmania", "act": "Australian Capital Territory", "nt": "Northern Territory", "payday": "Payday Super (Commonwealth)", "ato": "Payday Super (Commonwealth)"}
    agg = {}
    for k, n in conteggio.items():
        agg[nomi[k]] = agg.get(nomi[k], 0) + n
    corpo += ('<h2>Sources by jurisdiction</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Jurisdiction</th><th scope="col" class="n">Pages and documents we read</th></tr></thead><tbody>'
              + "".join(f'<tr><td>{h(k)}</td><td class="n">{v}</td></tr>' for k, v in agg.items()) + "</tbody></table></div>")
    corpo += "<h2>What we could not read</h2><div class=\"testo\">"
    corpo += rim.t("<p>Three websites answer our checking server with a 403 (bot protection): the ATO, the ACT Revenue Office and the NT Treasury.[[ato_payday,act_revenue,nt_treasury]] We do not try to get "
                   "round these blocks. ACT and NT figures come from the joint portal and from the legislation; for Payday Super we rely on the Act and point you to the ATO page.</p></div>")
    corpo += "<h2>How the calculator is tested</h2><div class=\"testo\">"
    corpo += (f"<p>The calculator in your browser is a copy of a reference implementation that we run before every update. The checks:</p><ul>"
              f"<li>recalculate <strong>{len(ufficiali)}</strong> worked examples published by the revenue offices (listed below), each within a dollar or two of the official figure where the office rounds its steps;</li>"
              f"<li>recalculate cases worked out by hand from the formula in an Act where no office publishes an example (for instance Victoria for a part year);</li>"
              f"<li>compare every row of RevenueSA's indicative rate table with the formula in the South Australian Act;</li>"
              f"<li>check the ACT brackets and the NT rules at their limits;</li>"
              f"<li>run the browser calculator and the reference implementation on thousands of random payrolls and require identical results;</li>"
              f"<li>check that the official calculators and pages we link still answer.</li></ul>"
              f"<p>The formulas are listed on the <a href=\"/calculator/#method\">calculator page</a>.</p></div>")
    corpo += ('<h2>The official worked examples we test against</h2><ul class="testo">'
              + "".join(f'<li>{h(c["descr"])}{rim.ref([c["fonte"]])}</li>' for c in ufficiali) + "</ul>")
    corpo += "<h2>The one case we do not calculate</h2><div class=\"testo\">"
    corpo += rim.t("<p>For the ACT, an employer that paid wages for only part of the year and whose total Australian wages are $1.75 million or less, but above its reduced threshold, is liable. "
                   "The 2026 determination's rate table starts above $1.75 million, so it sets no rate for that level. Rather than guess, the calculator shows “not calculated” and sends you to the ACT Revenue Office.[[act_det2026,act_act]]</p></div>")
    corpo += "<h2>When we update</h2><div class=\"testo\"><p>Payroll tax rates and thresholds change on 1 July, and state budgets in May and June announce them. Each year the site moves to the new financial year only after every figure has been re-read on the official pages; between updates, the checks above run again and flag any page that has changed. A page whose “last updated” date moves after our check is re-read by hand.</p></div>"
    corpo += ('<h2 id="corrections">Report an error</h2><div class="testo"><p>Seen a figure that does not match the official page, or a rule that has changed? Tell us which page and, if you can, '
              'link the official source. Your email is optional: give it only if you want a reply.</p></div>' + MODULO_CORREZIONI)
    corpo += rim.elenco()
    testata = banda("How we check", "How we check every figure", "Our sources, what we could not read, the tests the calculator passes before each update, and how to report an error.", corta=True, icona="shield")
    pagina("how-we-check/", "How We Check Payroll Tax Figures and Formulas",
           "How Payroll Tax by State checks its figures: official sources, exact phrases re-read on each page, official worked examples, calculator tests and corrections.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")])


def privacy():
    cookie = MON.privacy_cookie("en", SITO_ID, affiliati=ci_sono_affiliati())
    if not cookie:
        cookie = ("<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. This site does not use profiling cookies and shows no advertising.</p>")
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {NOME} ({URL_SITO.replace("https://", "")}) collects. In short: very little.</p></div>'
             '<div class="testo"><h2>The calculator</h2><p>The calculator runs in your browser. The wages and days you type are not sent to us or to anyone else and are not stored. If you use '
             '“Copy link”, the figures are written into the address of the page so that you can share it; they leave your device only if you send that link to someone.</p>'
             '<p>The site remembers your choice of light or dark theme in your browser (local storage). Nothing else is stored on your device by us.</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             '<h2 id="corrections">Corrections form</h2><p>If you use the <a href="/how-we-check/#corrections">corrections form</a>, we receive the page you name, your message, the source link '
             'and, only if you give it, your email address. The form is processed by Netlify Forms on our behalf. We use what you send only to check and answer the correction, and keep it only as long '
             'as that takes. The legal basis is your consent, given with the tick box; you can ask us to delete your message by sending another one through the form. '
             'There are no accounts or newsletters on this site.</p>'
             f'<h2>Changes</h2><p>We update this page when the site changes. Last update: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID, affiliati=ci_sono_affiliati()) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", f"Privacy | {NOME}", f"Privacy at {NOME}: the calculator runs in your browser, a cookie-free visit counter, and Google AdSense advertising with consent.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    carte = "".join(f'<li><a href="/{s}/"><b>{J[s]["breve"]}</b>{h(J[s]["nome"])}</a></li>' for s in ORDINE)
    corpo = (f'<div class="pull card"><p>The page you asked for does not exist. Try the <a href="/calculator/">calculator</a> or one of the states below.</p></div>'
             f'<ul class="griglia stati" style="margin-top:20px">{carte}</ul>')
    testata = banda("404", "Page not found", "This address has no page.", corta=True, icona="alert")
    pagina("", f"Page not found | {NOME}", "Page not found.", corpo, testata.replace("{bc}", ""), indicizza=False, file="404.html")


# ---------------------------------------------------------------- file accessori
def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{d}</lastmod></url>" for u, d in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in paytax/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = paytax/sito, Build command vuoto, Publish directory = "."
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

# Dominio proprio dal 13/11/2026: il vecchio indirizzo payroll-tax-by-state.netlify.app porta al nuovo, pagina per pagina.
[[redirects]]
  from = "https://payroll-tax-by-state.netlify.app/*"
  to = "https://payrolltaxbystate.com/:splat"
  status = 301
  force = true

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


def copia_grafica():
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").glob("*.woff2"):
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")
    for nome, testo in ASSET.items():
        (SITO / "assets" / nome).write_text(testo, encoding="utf-8")


def controlli():
    err = []
    for fid, f in FONTI.items():
        es = ESITI.get(fid)
        if not es:
            err.append(f"fonte {fid} mai letta: lanciare raccolta/fonti.py")
            continue
        if f.get("non_letta"):
            continue
        if es.get("http") != 200:
            err.append(f"fonte {fid}: HTTP {es.get('http')} all'ultima lettura")
        mancano = [c for c, ok in es.get("trovate", {}).items() if not ok]
        if mancano:
            err.append(f"fonte {fid}: frasi non più presenti {mancano}")
    fine = date.fromisoformat(GJ["fine"])
    if OGGI > fine:
        err.append(f"anno fiscale {ANNO} finito il {fine}: aggiornare i dati al nuovo anno (NOTE.md)")
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err))


def main():
    controlli()
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_grafica()
    home()
    pagina_calcolatore()
    for s in ORDINE:
        pagina_stato(s)
    interstate()
    grouping()
    regionale()
    storico_pagina()
    scadenze()
    cambiamenti()
    payday()
    oltre_soglia()
    about()
    come_controlliamo()
    privacy()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404. Anno fiscale {ANNO}, fonti controllate il {data_lunga(CONTROLLO)}.")


if __name__ == "__main__":
    main()
