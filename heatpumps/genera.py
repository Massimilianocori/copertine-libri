"""Genera il sito statico "Heat Pump Grants UK" (inglese, Regno Unito) in heatpumps/sito/.

Uso (dalla radice del repository):
    python3 heatpumps/raccolta/fonti.py     # scarica i 4 xlsx ufficiali (raccolta/_grezzi/, fuori da git) e rilegge le regole -> dati/fonti.json
    python3 heatpumps/raccolta/estrai.py    # cifre dagli xlsx -> dati/bus.json, dati/solare.json
    python3 heatpumps/genera.py             # pagine in heatpumps/sito/
    python3 heatpumps/verifica.py           # controlli (ricalcola ogni cifra dagli xlsx; --browser per Playwright)

Contenuto: Boiler Upgrade Scheme (contributi pagati per regione e per council, costo mediano nazionale e quartili, regole di
GOV.UK e Ofgem) e solare (impianti e potenza per regione e per council, costo per kW per regione) dai file DESNZ (OGL v3.0).
Regola legale: nessuna parola su prestiti o pagamenti a rate (verifica.py le rifiuta). Nessun dato personale.
"""
import hashlib
import json
import re
import shutil
import sys
import unicodedata
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

URL_SITO = "https://heat-pump-grants-uk.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
NOME = "Heat Pump Grants UK"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "heatpumps"  # nome del sito in monetizzazione.json
SOGLIA_INDICE = 100  # pagina council indicizzata solo con almeno 100 contributi pagati e tutti gli anni pubblicati (non oscurati)
OGL = "Contains public sector information licensed under the Open Government Licence v3.0."


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


B = carica("bus.json")
S = carica("solare.json")
_F = carica("fonti.json")
FONTI = _F["definizioni"]
ESITI = _F["fonti"]
FAQ = carica("faq.json")["faq"]
AFF = carica("affiliati.json")
CONTROLLO = date.fromisoformat(max(v["letto_il"] for v in ESITI.values()))

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MESI3 = {m[:3]: m for m in MESI}


def h(x):
    return escape(str(x), quote=True)


def data_lunga(d):
    if isinstance(d, str):
        d = date.fromisoformat(d[:10])
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def n(x, dec=0):
    return f"{x:,.{dec}f}"


def gbp(x):
    return f"£{x:,.0f}"


def pct(x, dec=0):
    return f"{x * 100:.{dec}f}%"


def variazione(d):
    """Variazione percentuale con segno; 'no change' sotto lo 0,5% (mai '+0%')."""
    if abs(d) < 0.005:
        return "no change"
    return f"{'+' if d > 0 else '−'}{abs(d) * 100:.0f}%"


def ordinale(k):
    suf = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
    return f"{k}{suf}"


def cap(s):
    return s[:1].upper() + s[1:]


def mese_lungo(m3):
    """'Sep 2026' -> 'September 2026'."""
    a, b = m3.split()
    return f"{MESI3[a]} {b}"


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def pubblicato(v):
    return isinstance(v, (int, float))


# ---------------------------------------------------------------- cifre nazionali
REG_EW = ["E12000001", "E12000002", "E12000003", "E12000004", "E12000005", "E12000006", "E12000007", "E12000008", "E12000009", "W92000004"]
REG_UK = REG_EW + ["S92000003", "N92000002"]
NOME_REG = {"E12000001": "North East", "E12000002": "North West", "E12000003": "Yorkshire and the Humber", "E12000004": "East Midlands",
            "E12000005": "West Midlands", "E12000006": "East of England", "E12000007": "London", "E12000008": "South East",
            "E12000009": "South West", "W92000004": "Wales", "S92000003": "Scotland", "N92000002": "Northern Ireland"}
NEL_REG = {k: ("the " + v if v in ("North East", "North West", "East Midlands", "West Midlands", "East of England", "South East", "South West")
               else v) for k, v in NOME_REG.items()}
NEL_REG["E12000003"] = "Yorkshire and the Humber"
SLUG_REG = {k: slug(v) for k, v in NOME_REG.items()}
LA_REG = {"North East": "E12000001", "North West": "E12000002", "Yorkshire and Humber": "E12000003", "Yorkshire and the Humber": "E12000003",
          "Yorkshire and The Humber": "E12000003", "East": "E12000006",
          "East Midlands": "E12000004", "West Midlands": "E12000005", "Eastern": "E12000006", "East of England": "E12000006", "London": "E12000007",
          "South East": "E12000008", "South West": "E12000009", "Wales": "W92000004", "Scotland": "S92000003", "Northern Ireland": "N92000002"}

PERIODO = B["periodo"]  # "September 2026"
TRIM = B["trimestri"][-1]  # "2026 Q3: Jul to Sep"


def trimestre_lungo(t):
    m = re.match(r"(\d{4}) Q\d: (\w{3}) to (\w{3})", t)
    return f"{MESI3[m.group(2)]} to {MESI3[m.group(3)]} {m.group(1)}"


TRIM_L = trimestre_lungo(TRIM)
CA = B["costi_trimestre"]["Air-to-Water Heat Pump"]
MED = CA["Median cost of installation (£)"][TRIM]
LQ = CA["Lower quartile cost of installation (£)"][TRIM]
UQ = CA["Upper quartile cost of installation (£)"][TRIM]
CG = B["costi_trimestre"]["Ground Source Heat Pump"]
GMED = CG["Median cost of installation (£)"][TRIM]
GRANT, GRANT9 = 7500, 9000
FASCE = B["costi_fasce"]
ANNO_F = B["anni_fasce"][-1]  # "2025/26"
T11 = B["t11"]
M11 = B["m11"]
MESI_SERIE = list(M11["Voucher applications received"]["All technology types"].keys())
ULTIMO_MESE = MESI_SERIE[-1]
DOM_MESE = M11["Voucher applications received"]["All technology types"][ULTIMO_MESE]
DOM_MAX = max(v for v in M11["Voucher applications received"]["All technology types"].values() if pubblicato(v))
ANNO_PRIMA = MESI_SERIE[-13]
DOM_ANNO_PRIMA = M11["Voucher applications received"]["All technology types"][ANNO_PRIMA]
PAG_MESE = M11["Redemptions paid"]["All technology types"][ULTIMO_MESE]
PAGATI_TOT = T11["Redemptions paid"]["totale"]
PAGATI_POMPE = B["cumulato_regioni_pompe"]["K04000001"]
ANNI = B["anni_la"]  # ["2022/23", ...]
_m9 = re.search(r"([\d,]+) applications for the £9,000 grant were received\. These applications were (\d+)% of the ([\d,]+) total applications",
                " ".join(B["commento"]))
N9000, Q9000, TOT_Q3 = _m9.group(1), _m9.group(2) + "%", _m9.group(3)


def anno_lungo(a):
    y = int(a[:4])
    return f"April {y} to March {y + 1}"


# ---------------------------------------------------------------- enti locali
def nome_pulito(t):
    t = re.sub(r"\s*\[note \d+\]", "", t).strip()
    t = re.sub(r", (City|County) of$", "", t)
    if " / " in t:
        en, cy = [x.strip() for x in t.split(" / ", 1)]
        return en, (cy if cy != en else None)
    return t, None


LA_SOL = S["la"]
_LA_PER_NOME = {v["nome"].lower(): k for k, v in LA_SOL.items() if "nome" in v}


def solare_di(codice, nome):
    if codice in LA_SOL:
        return LA_SOL[codice]
    k = _LA_PER_NOME.get(nome.lower())
    return LA_SOL.get(k) if k else None


AREE = []
for a in B["aree"]:
    en, cy = nome_pulito(a["nome_file"])
    a = dict(a, nome=en, gallese=cy)
    if a["ha_distretti"]:
        a["tipo"] = "contea" if a["codice"].startswith("E10") else "gruppo"
    else:
        a["tipo"] = "council"
    AREE.append(a)
PER_COD = {a["codice"]: a for a in AREE}
COUNCIL = [a for a in AREE if a["tipo"] == "council"]
CONTEE = [a for a in AREE if a["tipo"] == "contea"]
for a in COUNCIL:
    sol = solare_di(a["codice"], a["nome"])
    a["sol"] = sol
    a["famiglie"] = sol.get("famiglie") if sol else None
for c in CONTEE:
    c["distretti"] = [a for a in COUNCIL if a["contea"] == c["codice"]]
    c["famiglie"] = sum(d["famiglie"] for d in c["distretti"] if d["famiglie"])
    c["sol"] = {"siti": {y: sum(d["sol"]["siti"][y] for d in c["distretti"]) for y in ("2020", "2024", "2025")
                         if all(y in d["sol"]["siti"] for d in c["distretti"])},
                "mw": {y: round(sum(d["sol"]["mw"][y] for d in c["distretti"]), 2) for y in ("2020", "2024", "2025")
                       if all(y in d["sol"]["mw"] for d in c["distretti"])}}
for a in COUNCIL:
    a["contea_area"] = PER_COD.get(a["contea"]) if a["contea"] and PER_COD.get(a["contea"], {}).get("tipo") == "contea" else None
for a in COUNCIL + CONTEE:
    a["anni_ok"] = all(pubblicato(a["anni"][y]) for y in ANNI)
    a["ytd"] = a["cumulato"] - sum(a["anni"][y] for y in ANNI) if a["anni_ok"] else None
    a["tasso"] = a["cumulato"] / a["famiglie"] * 1000 if a.get("famiglie") else None
    a["indicizza"] = a["tipo"] == "contea" or (a["cumulato"] >= SOGLIA_INDICE and a["anni_ok"] and a["famiglie"])
    a["slug"] = slug(a["nome"])
    a["url"] = f"heat-pump-grants/{a['slug']}/"
_slugs = [a["slug"] for a in COUNCIL + CONTEE] + [SLUG_REG[r] for r in REG_EW]
assert len(_slugs) == len(set(_slugs)), "slug doppi"

FAM_REG = {r: sum(a["famiglie"] for a in COUNCIL if a["regione"] == r and a["famiglie"]) for r in REG_EW}
FAM_EW = sum(FAM_REG.values())
CUM = B["cumulato_regioni_pompe"]
TASSO_REG = {r: CUM[r] / FAM_REG[r] * 1000 for r in REG_EW}
TASSO_EW = CUM["K04000001"] / FAM_EW * 1000
for r in REG_EW:
    lista = sorted([a for a in COUNCIL if a["regione"] == r], key=lambda a: -a["cumulato"])
    for k, a in enumerate(lista, 1):
        a["rango"], a["n_reg"] = k, len(lista)
    con_tasso = sorted([a for a in lista if a["tasso"] is not None], key=lambda a: -a["tasso"])
    for k, a in enumerate(con_tasso, 1):
        a["rango_tasso"] = k
    for c in CONTEE:
        pass

COSTI_SOL = S["costi_regioni"]
ANNO_SOL = sorted(next(iter(COSTI_SOL.values())).keys())[-1]  # "2025/26"
SOMM_SOL = S["costi_sommario"][ANNO_SOL]
ET = S["regioni_et63"]
MESE_ET = list(ET["UK"]["numero"].keys())[-1]  # "Sep 2026"
MESE_ET_PRIMA = list(ET["UK"]["numero"].keys())[-13]
LA_UK = {k: v for k, v in LA_SOL.items() if re.match(r"^[ESWN]\d{8}$", k) and "2025" in v.get("siti", {}) and v.get("famiglie")}
for k, v in LA_UK.items():
    v["regione"] = LA_REG[v["regione_file"]]
    v["codice"] = k
    v["nome_pulito"] = nome_pulito(v["nome"])[0]


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
        return '<sup class="ref">' + ",".join(f'<a href="#f{k}" aria-label="source {k}">[{k}]</a>' for k in sorted(set(nums))) + "</sup>"

    def t(self, testo):
        return re.sub(r"\[\[([a-z0-9_, ]+)\]\]", lambda m: self.ref(m.group(1)), testo)

    def elenco(self):
        if not self.ordine:
            return ""
        voci = []
        for k, i in enumerate(self.ordine, 1):
            f, es = FONTI[i], ESITI.get(i, {})
            if f["tipo"] == "xlsx":
                stato = (f"{h(f['uscita'])}, published {data_lunga(es['pubblicato'])}; file downloaded and checked on {data_lunga(es['letto_il'])}. "
                         "Open Government Licence v3.0.")
                link = f'<a href="{h(f["pagina"])}" rel="noopener">{h(f["titolo"])}</a>'
            else:
                stato = f"checked {data_lunga(es['letto_il'])}" if es.get("http") == 200 else f"last check failed (HTTP {h(es.get('http'))})"
                link = f'<a href="{h(f["url"])}" rel="noopener">{h(f["titolo"])}</a>'
            voci.append(f'<li id="f{k}">{link} · {h(f["chi"])}. <span class="small">{stato}</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}Sources</h2>'
                f'<ol>{"".join(voci)}</ol><p class="small">{OGL} Figures are re-checked against these files before every update; see '
                f'<a href="/how-we-check/">how we check</a>.</p></section>')


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
TITOLI = {}
AD = '<div class="ad-slot" aria-hidden="true"></div>'
MENU = [("heat-pump-grants/", "Grants by area"), ("eligibility/", "Eligibility"), ("heat-pump-cost/", "Cost"), ("solar-panels/", "Solar panels"),
        ("how-we-check/", "How we check")]
DISCLAIMER = ("<strong>General information, not advice.</strong> Grant amounts and rules are taken from GOV.UK and Ofgem; counts and costs from the "
              "official DESNZ statistics linked on each page. Whether a property qualifies is checked by your installer and by Ofgem, who runs the scheme. "
              "This site is independent and is not a government website.")


def menu_html(percorso):
    return "".join(f'<a href="/{u}"' + (' aria-current="page"' if u == percorso else "") + f">{h(t)}</a>" for u, t in MENU)


def pagina(percorso, titolo, descrizione, corpo, testata="", briciole=None, jsonld=None, indicizza=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append((percorso, CONTROLLO.isoformat()))
    if titolo in TITOLI:
        raise SystemExit(f"titolo doppio: {titolo} ({percorso}, {TITOLI[titolo]})")
    TITOLI[titolo] = percorso
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": i, "name": nn, "item": f"{URL_SITO}/{p}"} for i, (nn, p) in enumerate(briciole, 1)]
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb">' + " › ".join(
            [f'<a href="/{p}">{h(nn)}</a>' for nn, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    corpo_tr = corpo + MON.riga_trasparenza(corpo, "en")
    reg_piede = "".join(f'<li><a href="/heat-pump-grants/{SLUG_REG[r]}/">{h(NOME_REG[r])}</a></li>' for r in REG_EW)
    guide_piede = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [
        ("heat-pump-grants/", "Grants by council"), ("eligibility/", "Who can get the grant"), ("heat-pump-cost/", "Heat pump cost"),
        ("solar-panels/", "Solar panels by region"), ("about/", "About"), ("how-we-check/", "How we check"), ("privacy/", "Privacy")])
    testa_ads = MON.script_adsense(SITO_ID, con_pubblicita=indicizza)
    testo = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{testa_ads}
<title>{h(titolo)}</title>
<meta name="description" content="{h(descrizione)}">
{f'<link rel="canonical" href="{url_pag}">' if indicizza else '<meta name="robots" content="noindex">'}
<meta property="og:title" content="{h(titolo)}">
<meta property="og:description" content="{h(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0E2A2F">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Heat Pump <b>Grants UK</b></span></a>
<nav class="menu" aria-label="Main">{menu_html(percorso)}</nav>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Menu">{ico("menu")}</summary><nav aria-label="Main">{menu_html(percorso)}</nav></details>
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
<a class="logo" href="/">{LOGO}<span>Heat Pump <b>Grants UK</b></span></a>
<p><strong>{NOME}</strong> shows how many heat pumps the Boiler Upgrade Scheme has paid for in every council area of England and Wales, what
they cost after the grant, and how much solar is installed in each region and council, from official government statistics.</p>
<p>Heat pump figures to the end of {PERIODO} (DESNZ, published {data_lunga(B["pubblicato"])}; next update {data_lunga(B["prossima"])}). Sources checked on {data_lunga(CONTROLLO)}.</p>
</div><div>
<h2>Regions</h2><ul>{reg_piede}</ul>
</div><div>
<h2>Guides</h2><ul>{guide_piede}</ul>
</div></div>
<p class="f-base">{OGL} The Boiler Upgrade Scheme is run by <a href="https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme-bus" rel="noopener">Ofgem</a>
for the Department for Energy Security and Net Zero. This site is not affiliated with either.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="fan"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def titolo_corto(*varianti):
    for v in varianti:
        if len(v) <= 65:
            return v
    raise SystemExit(f"nessun titolo ≤ 65: {varianti}")


def descr_corta(*varianti):
    for v in varianti:
        if 70 <= len(v) <= 160:
            return v
    raise SystemExit(f"nessuna descrizione 70-160: {varianti}")


# ---------------------------------------------------------------- FAQ
VAL = {
    "n9000": N9000, "quota9000": Q9000, "mese": PERIODO, "pagati_pompe": n(PAGATI_POMPE), "pagati_totale": n(PAGATI_TOT),
    "aahp_domande": n(T11["Voucher applications received"]["aahp"]), "pagati_galles": n(B["regioni"]["W92000004"]["pagati_totale"]),
    "trimestre": TRIM_L, "mediana": gbp(MED), "lq": gbp(LQ), "uq": gbp(UQ), "netto": gbp(MED - GRANT), "netto_lq": gbp(LQ - GRANT),
    "netto_uq": gbp(UQ - GRANT), "netto9000": gbp(MED - GRANT9), "gshp_mediana": gbp(GMED),
    "gshp_anno": gbp(FASCE["Ground Source Heat Pumps"]["All"][ANNO_F]["mediana"]),
    "gshp_numero": n(FASCE["Ground Source Heat Pumps"]["All"][ANNO_F]["numero"]), "awhp_numero": n(FASCE["Air-to-Water Heat Pumps"]["All"][ANNO_F]["numero"]),
    "sol_mediana_0_4": gbp(SOMM_SOL["mediana_0_4"]), "sol_es_3kw": gbp(3 * SOMM_SOL["mediana_0_4"]), "sol_mediana_4_10": gbp(SOMM_SOL["mediana_4_10"]),
    "sol_mediana_10_50": gbp(SOMM_SOL["mediana_10_50"]),
}
_gb = {r: COSTI_SOL[r][ANNO_SOL]["media_0_4"] for r in COSTI_SOL}
_rmin, _rmax = min(_gb, key=_gb.get), max(_gb, key=_gb.get)
VAL.update({"sol_min": gbp(_gb[_rmin]), "sol_min_reg": NEL_REG[_rmin], "sol_max": gbp(_gb[_rmax]), "sol_max_reg": NEL_REG[_rmax]})


def riempi(t):
    return re.sub(r"\{([a-z0-9_]+)\}", lambda m: VAL[m.group(1)], t)


def faq_blocco(pagina_id, rim, titolo="Common questions"):
    voci = [x for x in FAQ if x["pagina"] == pagina_id]
    if not voci:
        return "", None
    blocchi, ld = [], []
    for x in voci:
        a = riempi(x["a"])
        blocchi.append(f'<div class="faq"><h3>{h(x["q"])}</h3><p>{h(a)}{rim.ref(x["fonti"])}</p></div>')
        ld.append({"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": a}})
    html_ = f'<h2 id="faq">{h(titolo)}</h2><p class="small">Questions people in the UK search for, answered from the official sources.</p>' + "".join(blocchi)
    return html_, {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


# ---------------------------------------------------------------- riquadro preventivi (affiliazione preparata, spenta)
def ci_sono_affiliati():
    return any(v.get("attivo") and (v.get("url") or "").startswith("https://") for k, v in AFF.items() if not k.startswith("_"))


def box_preventivo(contesto, aff=None):
    """Riquadro 'get a quote': '' finché nessun programma è attivo con un URL vero."""
    aff = aff if aff is not None else AFF
    voci = [v for k, v in aff.items() if not k.startswith("_") and v.get("attivo") and (v.get("url") or "").startswith("https://")
            and contesto in v.get("pagine", [])]
    if not voci:
        return "<!-- quote box: off -->"
    righe = "".join(f'<li><a href="{h(v["url"])}" rel="sponsored noopener">{h(v["nome"])}</a>: {h(v["testo"])}</li>' for v in voci)
    return (f'<aside class="aff-box"><h2>Get a quote <span class="aff-tag">Partner</span></h2>'
            f'<p>Ofgem recommends getting quotes from more than one MCS certified installer. The installer applies for the grant and takes it off the quote. '
            f'These partners can give you a quote; they do not change any figure on this site.</p>'
            f'<ul>{righe}</ul>{MON.nota_trasparenza("en")}</aside>')


# ---------------------------------------------------------------- pezzi comuni
def cifre(voci, asof):
    """voci: (valore, etichetta, principale)."""
    celle = "".join(f'<div class="cifra{" main" if m else ""}"><b>{v}</b><span>{e}</span></div>' for v, e, m in voci)
    return f'<div class="card cifre pull">{celle}<p class="asof">{ico("check")}{asof}</p></div>'


def asof_bus():
    return (f"Official DESNZ figures to the end of {PERIODO}, published {data_lunga(B['pubblicato'])}. Next update {data_lunga(B['prossima'])}.")


def barre(righe, titolo="", nota=""):
    """righe: (etichetta, valore numerico o testo, suggerimento). Barre orizzontali, un solo colore, valore alla punta."""
    numeri = [v for _, v, _ in righe if pubblicato(v)]
    mx = max(numeri) if numeri and max(numeri) > 0 else 1
    li = []
    for et, v, tip in righe:
        if pubblicato(v):
            f = v / mx
            barra = f'<span class="b{" zero" if v == 0 else ""}" style="width:calc((100% - 6.5em) * {f:.4f})"></span>'
            val = n(v)
        else:
            barra, val = '<span class="b zero" style="width:2px"></span>', h(v)
        li.append(f'<li title="{h(tip)}"><span class="et">{h(et)}</span><span class="tr">{barra}<span class="v">{val}</span></span></li>')
    testa = f'<div class="barre-h"><h3>{h(titolo)}</h3><span class="small">{nota}</span></div>' if titolo else ""
    return f'<div class="card" style="padding:0">{testa}<ul class="barre">{"".join(li)}</ul></div>'


SOPPRESSI = {"[c1]": "not published (1 to 4)", "[c2]": "not published", "[c3]": "not published (0 to 4)", "[x]": "no data"}


def val_anno(v):
    return v if pubblicato(v) else SOPPRESSI.get(v, "not published")


def tabella_costo(rim, chi=""):
    righe = [("Lower quartile", LQ), ("Median", MED), ("Upper quartile", UQ)]
    tr = "".join(f'<tr{" class=qui" if "Median" in e else ""}><td>{e}</td><td class="n">{gbp(v)}</td><td class="n">{gbp(v - GRANT)}</td>'
                 f'<td class="n">{gbp(v - GRANT9)}</td></tr>' for e, v in righe)
    return (f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Air source, {h(TRIM_L)}</th><th scope="col" class="n">Installed cost</th>'
            f'<th scope="col" class="n">After £7,500 grant</th><th scope="col" class="n">After £9,000 (oil or LPG, off gas grid)</th></tr></thead><tbody>{tr}</tbody>'
            f'<caption>Costs reported for installations with a grant paid, England and Wales as a whole; they include the grant value. A quarter of installations cost '
            f'less than the lower quartile and a quarter more than the upper quartile; the median is the typical installation. '
            f'“After grant” is our subtraction.{rim.ref("bus_xlsx")}</caption></table></div>')


def nota_costo_nazionale(luogo):
    return (f'<div class="nota info">{ico("info")}<p><strong>These costs are national, not local.</strong> DESNZ publishes installation costs only for England '
            f'and Wales as a whole, so the same figures appear on every area page of this site. Prices in {h(luogo)} can be higher or lower: the only way to '
            f'know yours is a quote from an MCS certified installer.</p></div>')


def regole_brevi(rim):
    return rim.t(
        '<ul class="testo">'
        "<li><strong>£7,500</strong> off an air source (air-to-water) or ground source heat pump; <strong>£9,000</strong> if the property is heated by oil or LPG and has no mains gas, until 31 March 2027; <strong>£2,500</strong> off an air-to-air heat pump (homes only); £5,000 off a biomass boiler (rural, off the gas grid).[[gov_apply,ofgem_bus]]</li>"
        "<li>You must own the property (your home, a second home, a property you let or a business building) and replace fossil fuel or electric heating. Hybrid systems, most new builds and social housing are excluded.[[gov_apply,ofgem_owners]]</li>"
        "<li>An MCS certified installer applies for you and takes the grant off the quote; Ofgem asks you to confirm within 14 days.[[ofgem_owners]]</li>"
        '</ul><p><a href="/eligibility/">All the rules, with the official wording</a></p>')


def griglia_regioni(attuale=None):
    voci = []
    for r in REG_EW:
        if r == attuale:
            continue
        voci.append(f'<li><a href="/heat-pump-grants/{SLUG_REG[r]}/"><b>{h(NOME_REG[r])}</b><span><em>{n(CUM[r])}</em> heat pumps with a grant paid · '
                    f'{n(TASSO_REG[r], 1)} per 1,000 households</span></a></li>')
    return f'<ul class="griglia">{"".join(voci)}</ul>'


def frase_trend(a):
    y1, y2 = a["anni"][ANNI[-2]], a["anni"][ANNI[-1]]
    if not (pubblicato(y1) and pubblicato(y2)) or y1 == 0:
        return ""
    d = (y2 - y1) / y1
    if abs(d) < 0.005:
        return f"The {ANNI[-1]} total was the same as in {ANNI[-2]}."
    return f"That is {'up' if d > 0 else 'down'} {pct(abs(d))} on {ANNI[-2]} ({n(y1)})."


def righe_anni(a):
    righe = [(y, val_anno(a["anni"][y]), f"{y} ({anno_lungo(y)}): {n(a['anni'][y]) if pubblicato(a['anni'][y]) else val_anno(a['anni'][y])} grants paid") for y in ANNI]
    if a.get("ytd") is not None:
        righe.append(("2026/27 so far", a["ytd"], f"April to {PERIODO}: {n(a['ytd'])} grants paid (our calculation)"))
    return righe


def solare_area(a, nome, rim, regione):
    sol = a.get("sol")
    if not sol:
        return ""
    s25, s20, mw25 = sol["siti"]["2025"], sol["siti"].get("2020"), sol["mw"]["2025"]
    fam = a.get("famiglie")
    cr = COSTI_SOL[regione][ANNO_SOL]
    per = f" That is <strong>{n(s25 / fam * 1000)}</strong> installations per 1,000 households." if fam else ""
    return rim.t(
        f'<h2 id="solar">Solar panels in {h(nome)}</h2>'
        f'<div class="testo"><p>At the end of 2025 {h(nome)} had <strong>{n(s25)}</strong> solar PV installations with a combined capacity of <strong>{n(mw25, 1)} MW</strong>'
        + (f', up from {n(s20)} installations at the end of 2020.' if s20 is not None else '.') + f'{per}[[solare_la_xlsx]] The count is mostly rooftop systems on homes; the capacity also includes '
        f'business roofs and any solar farms in the area. DESNZ warns that many 2025 installations could not yet be placed in a local authority, so the latest '
        f'figures will be revised upwards.[[solare_la_xlsx]]</p>'
        f'<p>In {h(NEL_REG[regione])}, small solar systems up to 4 kW installed in {ANNO_SOL} cost on average <strong>{gbp(cr["media_0_4"])} per kW</strong> and '
        f'systems of 4 to 10 kW {gbp(cr["media_4_10"])} per kW, including installation and VAT where applicable but not batteries.[[solare_costi_xlsx]] '
        f'That puts a 3 kW system at about {gbp(3 * cr["media_0_4"])} and a 6 kW system at about {gbp(6 * cr["media_4_10"])} (our arithmetic on the regional average). '
        f'<a href="/solar-panels/{SLUG_REG[regione]}/">Solar in {h(NEL_REG[regione])}, council by council</a>.</p></div>')


# ---------------------------------------------------------------- pagine council e contea
def pagina_area(a):
    rim = Rimandi()
    nome = a["nome"]
    reg = a["regione"]
    contea = a.get("contea_area")
    nome_h = nome + (f" ({a['gallese']})" if a.get("gallese") else "")
    tot = a["cumulato"]
    y = a["anni"][ANNI[-1]]
    voci = [(n(tot), f"heat pumps with a grant paid, May 2022 to {PERIODO}", True),
            (n(y) if pubblicato(y) else "n/p", f"paid in {ANNI[-1]} ({anno_lungo(ANNI[-1])})", False)]
    if a.get("tasso") is not None:
        voci.append((n(a["tasso"], 1), f"per 1,000 households ({NOME_REG[reg]}: {n(TASSO_REG[reg], 1)})", False))
    if a["tipo"] == "council":
        voci.append((ordinale(a["rango"]), f"of {a['n_reg']} councils in {NEL_REG[reg]} by grants paid", False))
    else:
        voci.append((n(len(a["distretti"])), "district councils in the county", False))
    corpo = f"<!-- area: {a['codice']} -->" + cifre(voci, asof_bus())
    quota_reg = tot / CUM[reg]
    corpo += rim.t(
        f'<h2 id="years">Heat pump grants paid in {h(nome)}, year by year</h2>'
        f'<div class="testo"><p>The Boiler Upgrade Scheme had paid grants for <strong>{n(tot)}</strong> heat pumps in {h(nome_h)} by the end of {PERIODO}: '
        f'{pct(quota_reg, 1)} of all those paid in {h(NEL_REG[reg])} and {pct(tot / CUM["K04000001"], 2)} of England and Wales.[[bus_xlsx]] '
        + (f'In the {ANNI[-1]} financial year {n(y)} were paid. {frase_trend(a)} ' if pubblicato(y) else "")
        + (f'From April to {PERIODO} another <strong>{n(a["ytd"])}</strong> were paid (our calculation: the total to date minus the four full years).' if a.get("ytd") is not None else
           'DESNZ does not publish one or more yearly figures for this area because the numbers are small (it hides counts of 1 to 4 to protect privacy).')
        + "</p></div>")
    corpo += barre(righe_anni(a), "Grants paid by financial year", "Heat pumps; financial years run April to March")
    corpo += ('<p class="small">A grant counts here when Ofgem has paid it, after the installation is finished; DESNZ counts it by the property\'s postcode. '
              'Heat pumps installed without the grant are not included.</p>')
    corpo += AD
    # confronto
    righe = []
    if a.get("tasso") is not None:
        righe.append(("Grants paid per 1,000 households", n(a["tasso"], 1), n(TASSO_REG[reg], 1), n(TASSO_EW, 1)))
    ar = B["anni_regioni_pompe"]
    def cambio(d):
        v1, v2 = d[ANNI[-2]], d[ANNI[-1]]
        return variazione((v2 - v1) / v1) if pubblicato(v1) and pubblicato(v2) and v1 else "n/p"
    righe.append((f"Change {ANNI[-2]} to {ANNI[-1]}", cambio(a["anni"]), cambio(ar[reg]), cambio(ar["K04000001"])))
    tr = "".join(f'<tr><td>{e}</td><td class="n">{x}</td><td class="n">{r}</td><td class="n">{w}</td></tr>' for e, x, r, w in righe)
    corpo += (f'<h2 id="compare">How {h(nome)} compares</h2>'
              f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Measure</th><th scope="col" class="n">{h(nome)}</th><th scope="col" class="n">{h(NOME_REG[reg])}</th>'
              f'<th scope="col" class="n">England and Wales</th></tr></thead><tbody>{tr}</tbody><caption>Per 1,000 households is our calculation: grants paid to date divided by '
              f'the household estimates published with the DESNZ local authority renewables tables.{rim.ref("bus_xlsx,solare_la_xlsx")}</caption></table></div>')
    if a["tipo"] == "contea":
        vicini = sorted(a["distretti"], key=lambda d: -d["cumulato"])
        titolo_v = f"District councils in {nome}"
    elif contea:
        vicini = sorted([d for d in contea["distretti"] if d is not a], key=lambda d: -d["cumulato"])
        titolo_v = f"Other councils in {contea['nome']}"
    else:
        lista = sorted([d for d in COUNCIL if d["regione"] == reg], key=lambda d: -d["cumulato"])
        k = lista.index(a)
        vicini = [d for d in lista[max(0, k - 4):k + 5] if d is not a]
        titolo_v = f"Councils with similar numbers in {NEL_REG[reg]}"
    if vicini:
        tr = "".join(f'<tr data-riga="{h(d["nome"])}"><td><a href="/{d["url"]}">{h(d["nome"])}</a></td><td class="n">{n(d["cumulato"])}</td>'
                     f'<td class="n">{n(d["anni"][ANNI[-1]]) if pubblicato(d["anni"][ANNI[-1]]) else "n/p"}</td>'
                     f'<td class="n">{n(d["tasso"], 1) if d["tasso"] is not None else "–"}</td></tr>' for d in vicini)
        corpo += (f'<h3>{h(titolo_v)}</h3><div class="tab"><table class="dati"><thead><tr><th scope="col">Council</th><th scope="col" class="n">Grants paid to date</th>'
                  f'<th scope="col" class="n">In {ANNI[-1]}</th><th scope="col" class="n">Per 1,000 households</th></tr></thead><tbody>{tr}</tbody></table></div>')
    corpo += f'<p><a href="/heat-pump-grants/{SLUG_REG[reg]}/">All councils in {h(NEL_REG[reg])}</a> · <a href="/heat-pump-grants/">every council in England and Wales</a></p>'
    # costo
    corpo += f'<h2 id="cost">What a heat pump costs after the grant</h2>' + nota_costo_nazionale(nome)
    corpo += rim.t(f'<div class="testo"><p>For air source heat pumps with a grant paid in {TRIM_L}, the median installed cost was <strong>{gbp(MED)}</strong>. '
                   f'Taking off the £7,500 grant leaves about <strong>{gbp(MED - GRANT)}</strong> for a typical installation.[[bus_xlsx]]</p></div>')
    corpo += tabella_costo(rim)
    corpo += '<p><a href="/heat-pump-cost/">Costs by heat pump size and over time</a></p>'
    corpo += f'<h2 id="rules">Who can get the grant in {h(nome)}</h2>' + regole_brevi(rim)
    corpo += box_preventivo("contea" if a["tipo"] == "contea" else "council")
    corpo += solare_area(a, nome, rim, reg)
    corpo += rim.elenco()
    sub = (f"<strong>{n(tot)}</strong> heat pumps in {h(nome)} have had a Boiler Upgrade Scheme grant paid since May 2022. "
           f"Official figures year by year, how the area compares, and what a heat pump costs after the £7,500 grant.")
    testata = banda(f"Boiler Upgrade Scheme · {NOME_REG[reg]}", f"Heat pump grants in {nome}", sub, icona="map")
    tot_s = n(tot)
    titolo = titolo_corto(f"Heat Pump Grants in {nome}: {tot_s} Paid Since 2022", f"Heat Pump Grants in {nome}: {tot_s} Paid",
                          f"{nome} Heat Pump Grants: {tot_s} Paid", f"{nome} Heat Pump Grants")
    yd = f", {n(y)} in {ANNI[-1]}" if pubblicato(y) else ""
    descr = descr_corta(
        f"{tot_s} Boiler Upgrade Scheme grants paid for heat pumps in {nome} to {PERIODO}{yd}. Year by year, compared with {NOME_REG[reg]}, and the cost after the grant.",
        f"{tot_s} heat pump grants paid in {nome} to {PERIODO}{yd}: official figures by year and the cost after the £7,500 grant.",
        f"{tot_s} heat pump grants paid in {nome} to {PERIODO}: official figures and the cost after the grant.",
        f"Heat pump grants paid in {nome}: official DESNZ figures and the cost after the grant.")
    bric = [("Home", ""), ("Grants by area", "heat-pump-grants/"), (NOME_REG[reg], f"heat-pump-grants/{SLUG_REG[reg]}/")]
    if contea:
        bric.append((contea["nome"], contea["url"]))
    bric.append((nome, a["url"]))
    pagina(a["url"], titolo, descr, corpo, testata, briciole=bric, indicizza=bool(a["indicizza"]))


# ---------------------------------------------------------------- regioni
def pagina_regione(r):
    rim = Rimandi()
    nome, nel = NOME_REG[r], NEL_REG[r]
    R = B["regioni"][r]
    tot = CUM[r]
    anni = B["anni_regioni_pompe"][r]
    lista = sorted([a for a in COUNCIL if a["regione"] == r], key=lambda a: -a["cumulato"])
    md = R["mesi_domande"]
    km = list(md.keys())
    ult, prima = md[km[-1]], md[km[-13]]
    voci = [(n(tot), f"heat pumps with a grant paid, May 2022 to {PERIODO}", True),
            (n(anni[ANNI[-1]]), f"paid in {ANNI[-1]}", False),
            (n(R["per10k_pagati"], 1), "grants paid per 10,000 households (DESNZ, homes only)", False),
            (n(ult), f"applications in {mese_lungo(km[-1])} ({variazione((ult - prima) / prima)} on a year earlier)", False)]
    corpo = f"<!-- region: {r} -->" + cifre(voci, asof_bus())
    corpo += rim.t(
        f'<h2 id="years">Heat pump grants in {h(nel)}, year by year</h2><div class="testo"><p>{h(cap(nel))} accounts for <strong>{pct(tot / CUM["K04000001"], 1)}</strong> '
        f'of the {n(CUM["K04000001"])} heat pumps paid for by the Boiler Upgrade Scheme in England and Wales. Counting biomass boilers too, '
        f'{n(R["pagati_totale"])} installations had a grant paid, from {n(R["domande"])} applications and {n(R["buoni"])} vouchers issued.[[bus_xlsx]] '
        f'DESNZ puts the region at {n(R["per10k_pagati"], 1)} grants paid per 10,000 households, against {n(B["regioni"]["K04000001"]["per10k_pagati"], 1)} for '
        f'England and Wales.[[bus_xlsx]]</p></div>')
    righe = [(y, anni[y], f"{y}: {n(anni[y])} grants paid") for y in ANNI]
    righe.append(("2026/27 so far", tot - sum(anni[y] for y in ANNI), f"April to {PERIODO} (our calculation)"))
    corpo += barre(righe, "Heat pump grants paid by financial year", "April to March")
    ultimi = km[-12:]
    corpo += barre([(k, md[k], f"{mese_lungo(k)}: {n(md[k])} applications") for k in ultimi], "Applications per month, last 12 months",
                   "Heat pump voucher applications received by Ofgem")
    corpo += rim.t(f'<p class="small">The £9,000 grant for oil and LPG homes opened on 21 July 2026.[[bus_xlsx]] '
                   'Not every application leads to a voucher, and not every voucher to an installation.</p>')
    corpo += AD
    cb = B["combustibile_regione"][r].get(ANNI[-1], {})
    tot_cb = sum(cb.values())
    if tot_cb:
        nomi_cb = {"Gas": "Mains gas", "Oil": "Oil", "Direct Electric": "Electric heating", "LPG": "LPG", "Coal": "Coal", "None": "No previous heating",
                   "Other": "Other", "Unknown": "Unknown"}
        tr = "".join(f'<tr><td>{nomi_cb.get(k, k)}</td><td class="n">{n(v)}</td><td class="n">{pct(v / tot_cb) if v / tot_cb >= 0.005 else "under 1%"}</td></tr>'
                     for k, v in sorted(cb.items(), key=lambda x: -x[1]) if v)
        corpo += (f'<h2 id="replaced">What the new heating replaced in {ANNI[-1]}</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Heating replaced</th>'
                  f'<th scope="col" class="n">Installations</th><th scope="col" class="n">Share</th></tr></thead><tbody>{tr}</tbody><caption>Grants paid in {h(nel)} in '
                  f'{ANNI[-1]}, all technologies. “No previous heating” is mostly self-builds.{rim.ref("bus_xlsx")}</caption></table></div>')
    tr = "".join(f'<tr data-riga="{h(a["nome"])}"><td><a href="/{a["url"]}">{h(a["nome"])}</a></td><td class="n">{n(a["cumulato"])}</td>'
                 f'<td class="n">{n(a["anni"][ANNI[-1]]) if pubblicato(a["anni"][ANNI[-1]]) else "n/p"}</td>'
                 f'<td class="n">{n(a["tasso"], 1) if a["tasso"] is not None else "–"}</td></tr>' for a in lista)
    corpo += (f'<h2 id="councils">Heat pump grants by council in {h(nel)}</h2>'
              f'<div class="cerca"><input type="search" data-cerca="tab-reg" placeholder="Find a council" aria-label="Find a council"></div>'
              f'<div class="tab" id="tab-reg"><table class="dati"><thead><tr><th scope="col">Council</th><th scope="col" class="n">Grants paid to date</th>'
              f'<th scope="col" class="n">In {ANNI[-1]}</th><th scope="col" class="n">Per 1,000 households</th></tr></thead><tbody>{tr}'
              f'<tr data-vuoto hidden><td colspan="4">No council matches.</td></tr></tbody>'
              f'<caption>“n/p”: not published by DESNZ because the number is small. Per 1,000 households: our calculation.{rim.ref("bus_xlsx,solare_la_xlsx")}</caption></table></div>')
    contee = [c for c in CONTEE if c["regione"] == r]
    if contee:
        corpo += ('<p>County totals: ' + " · ".join(f'<a href="/{c["url"]}">{h(c["nome"])}</a> ({n(c["cumulato"])})' for c in contee) + "</p>")
    corpo += f'<h2 id="cost">What a heat pump costs after the grant</h2>' + nota_costo_nazionale(nel) + tabella_costo(rim)
    corpo += f'<h2 id="rules">Who can get the grant</h2>' + regole_brevi(rim)
    corpo += box_preventivo("regione")
    et = ET[r]
    sn, sp = et["numero"][MESE_ET], et["numero"][MESE_ET_PRIMA]
    corpo += rim.t(f'<h2 id="solar">Solar panels in {h(nel)}</h2><div class="testo"><p>By the end of {mese_lungo(MESE_ET)} {h(nel)} had <strong>{n(sn)}</strong> solar '
                   f'installations ({n(et["mw"][MESE_ET], 0)} MW), {n(sn - sp)} more than a year earlier.[[solare_et63_xlsx]] Small systems up to 4 kW cost on average '
                   f'{gbp(COSTI_SOL[r][ANNO_SOL]["media_0_4"])} per kW in {ANNO_SOL}.[[solare_costi_xlsx]] '
                   f'<a href="/solar-panels/{SLUG_REG[r]}/">Solar panels in {h(nel)} by council</a>.</p></div>')
    corpo += '<h2>Other regions</h2>' + griglia_regioni(r)
    corpo += rim.elenco()
    sub = (f"<strong>{n(tot)}</strong> heat pumps in {h(nel)} have had a Boiler Upgrade Scheme grant paid. Year-by-year and monthly figures, every council, "
           f"and the cost after the grant.")
    testata = banda("Boiler Upgrade Scheme · region", f"Heat pump grants in {nel}", sub, icona="map")
    titolo = titolo_corto(f"Heat Pump Grants in {nel}: {n(tot)} Paid, by Council", f"Heat Pump Grants in {nel}: {n(tot)} Paid")
    descr = descr_corta(f"{n(tot)} Boiler Upgrade Scheme grants paid for heat pumps in {nel} to {PERIODO}: by year, by month and for each of its {len(lista)} councils.",
                        f"{n(tot)} heat pump grants paid in {nel}: by year, by month and for each council, from DESNZ figures.")
    pagina(f"heat-pump-grants/{SLUG_REG[r]}/", titolo, descr, corpo, testata,
           briciole=[("Home", ""), ("Grants by area", "heat-pump-grants/"), (nome, f"heat-pump-grants/{SLUG_REG[r]}/")])


def hub_aree():
    rim = Rimandi()
    tutte = sorted(COUNCIL, key=lambda a: a["nome"])
    tr = "".join(f'<tr data-riga="{h(a["nome"])} {h(a["gallese"] or "")} {h(NOME_REG[a["regione"]])}"><td><a href="/{a["url"]}">{h(a["nome"])}</a></td>'
                 f'<td>{h(NOME_REG[a["regione"]])}</td><td class="n">{n(a["cumulato"])}</td>'
                 f'<td class="n">{n(a["anni"][ANNI[-1]]) if pubblicato(a["anni"][ANNI[-1]]) else "n/p"}</td>'
                 f'<td class="n">{n(a["tasso"], 1) if a["tasso"] is not None else "–"}</td></tr>' for a in tutte)
    corpo = cifre([(n(PAGATI_POMPE), f"heat pumps with a grant paid in England and Wales, May 2022 to {PERIODO}", True),
                   (n(len(COUNCIL)), "council areas", False), (n(TASSO_EW, 1), "per 1,000 households", False),
                   (n(B["anni_regioni_pompe"]["K04000001"][ANNI[-1]]), f"paid in {ANNI[-1]}", False)], asof_bus())
    corpo += rim.t(f'<div class="testo"><p>DESNZ counts every Boiler Upgrade Scheme grant paid by the postcode of the property and publishes the total for each '
                   f'local authority every three months.[[bus_xlsx]] Find your council below, or start from your region.</p></div>')
    corpo += '<h2 id="regions">By region</h2>' + griglia_regioni()
    corpo += AD
    corpo += (f'<h2 id="councils">Every council in England and Wales</h2><div class="cerca"><input type="search" data-cerca="tab-tutti" placeholder="Type a council or region" '
              f'aria-label="Find a council"></div><div class="tab" id="tab-tutti"><table class="dati"><thead><tr><th scope="col">Council</th><th scope="col">Region</th>'
              f'<th scope="col" class="n">Grants paid</th><th scope="col" class="n">In {ANNI[-1]}</th><th scope="col" class="n">Per 1,000 households</th></tr></thead>'
              f'<tbody>{tr}<tr data-vuoto hidden><td colspan="5">No council matches.</td></tr></tbody><caption>Heat pumps with a grant paid, May 2022 to {PERIODO}. '
              f'“n/p”: not published by DESNZ because the number is small.{rim.ref("bus_xlsx,solare_la_xlsx")}</caption></table></div>')
    corpo += '<h2>County councils</h2><ul class="pillole">' + "".join(f'<li><a href="/{c["url"]}">{h(c["nome"])} · {n(c["cumulato"])}</a></li>' for c in CONTEE) + "</ul>"
    corpo += rim.elenco()
    testata = banda("Boiler Upgrade Scheme · by area", "Heat pump grants by council", f"How many heat pumps the grant has paid for in each of the {len(COUNCIL)} "
                    f"council areas of England and Wales, from the official statistics to {PERIODO}.", icona="map")
    pagina("heat-pump-grants/", "Heat Pump Grants by Council: England and Wales", f"Boiler Upgrade Scheme grants paid in every council area of England and Wales: "
           f"{n(PAGATI_POMPE)} heat pumps to {PERIODO}, with yearly figures and rates per household.", corpo, testata,
           briciole=[("Home", ""), ("Grants by area", "heat-pump-grants/")])


# ---------------------------------------------------------------- home
def home():
    rim = Rimandi()
    record = DOM_MESE == DOM_MAX
    voci = [(gbp(GRANT), "off an air source or ground source heat pump (£9,000 for oil and LPG homes)", True),
            (gbp(MED - GRANT), f"typical cost left to pay: median {gbp(MED)} minus the grant", False),
            (n(PAGATI_POMPE), f"heat pumps with a grant paid, May 2022 to {PERIODO}", False),
            (n(DOM_MESE), f"applications in {PERIODO}" + (", a record" if record else ""), False)]
    corpo = cifre(voci, asof_bus())
    corpo += '<h2 id="grants">What the Boiler Upgrade Scheme pays</h2>'
    corpo += ('<ul class="grant">'
              '<li><b>£7,500</b><span>air source (air-to-water) heat pump</span></li>'
              '<li><b>£7,500</b><span>ground source or water source heat pump</span></li>'
              '<li><b>£9,000</b><span>air or ground source, oil or LPG home with no mains gas, until 31 March 2027</span></li>'
              '<li><b>£2,500</b><span>air-to-air heat pump, homes only, since 28 April 2026</span></li>'
              '<li><b>£5,000</b><span>biomass boiler, rural and off the gas grid only</span></li></ul>')
    corpo += rim.t('<p class="small">Grant amounts from GOV.UK and Ofgem.[[gov_apply,ofgem_bus,ofgem_owners]] One grant per property, in England and Wales only. '
                   'The installer takes the grant off your quote.</p>')
    corpo += rim.t(f'<h2 id="cost">What you pay after the grant</h2><div class="testo"><p>DESNZ publishes the cost reported for every installation with a grant paid. '
                   f'In {TRIM_L} the median air source heat pump cost <strong>{gbp(MED)}</strong> including the grant, so a typical owner paid about '
                   f'<strong>{gbp(MED - GRANT)}</strong> after £7,500, or {gbp(MED - GRANT9)} with the £9,000 grant.[[bus_xlsx]]</p></div>')
    corpo += tabella_costo(rim)
    corpo += '<p><a href="/heat-pump-cost/">Cost by size of heat pump, ground source costs and the trend since 2022</a></p>'
    corpo += AD
    tm = M11["Voucher applications received"]["All technology types"]
    corpo += rim.t(f'<h2 id="demand">{"Applications are at a record" if record else "Applications month by month"}</h2><div class="testo"><p>Ofgem received <strong>{n(DOM_MESE)}</strong> applications in {PERIODO}, '
                   f'{pct((DOM_MESE - DOM_ANNO_PRIMA) / DOM_ANNO_PRIMA)} more than in {mese_lungo(ANNO_PRIMA)}. From July to September 2026, {N9000} of the {TOT_Q3} '
                   f'applications ({Q9000}) were for the new £9,000 grant. {n(PAG_MESE)} grants were paid in {PERIODO}.[[bus_xlsx]] The 2026/27 budget is £400 million, '
                   f'and vouchers are issued first come, first served until the year\'s budget is used.[[bus_xlsx]]</p></div>')
    corpo += barre([(k, tm[k], f"{mese_lungo(k)}: {n(tm[k])} applications") for k in MESI_SERIE[-12:]], "Applications per month, England and Wales",
                   "All technologies")
    corpo += '<h2 id="eligible">Who can get it</h2>' + regole_brevi(rim)
    corpo += box_preventivo("home")
    per_n = sorted(REG_EW, key=lambda r: -CUM[r])
    per_t = sorted(REG_EW, key=lambda r: -TASSO_REG[r])
    corpo += rim.t(f'<h2 id="areas">Grants paid in your area</h2><div class="testo"><p>{h(cap(NEL_REG[per_n[0]]))} ({n(CUM[per_n[0]])}) and {h(NEL_REG[per_n[1]])} '
                   f'({n(CUM[per_n[1]])}) have had the most heat pump grants paid; per household, {h(NEL_REG[per_t[0]])} leads with {n(TASSO_REG[per_t[0]], 1)} per 1,000 '
                   f'households and {h(NEL_REG[per_t[-1]])} has the fewest ({n(TASSO_REG[per_t[-1]], 1)}). Each region page lists every council, with year-by-year figures.[[bus_xlsx]]</p></div>')
    corpo += griglia_regioni()
    top = sorted([a for a in COUNCIL if a["indicizza"]], key=lambda a: -a["cumulato"])[:12]
    corpo += ('<h3>Councils with the most heat pump grants paid</h3><ul class="pillole">' +
              "".join(f'<li><a href="/{a["url"]}">{h(a["nome"])} · {n(a["cumulato"])}</a></li>' for a in top) +
              '</ul><p><a href="/heat-pump-grants/">Find any council in England and Wales</a></p>')
    uk = ET["UK"]
    corpo += rim.t(f'<h2 id="solar">Solar panels</h2><div class="testo"><p>The UK had <strong>{n(uk["numero"][MESE_ET])}</strong> solar installations at the end of '
                   f'{mese_lungo(MESE_ET)}, {n(uk["numero"][MESE_ET] - uk["numero"][MESE_ET_PRIMA])} more than a year earlier.[[solare_et63_xlsx]] Small systems up to '
                   f'4 kW installed in {ANNO_SOL} had a median cost of {gbp(SOMM_SOL["mediana_0_4"])} per kW.[[solare_costi_xlsx]] '
                   f'<a href="/solar-panels/">Solar installations and cost per kW, region by region</a>.</p></div>')
    f_html, f_ld = faq_blocco("home", rim)
    corpo += f_html
    corpo += rim.elenco()
    sub = (f"The Boiler Upgrade Scheme takes <strong>£7,500</strong> off a heat pump in England and Wales, or <strong>£9,000</strong> in oil and LPG homes. "
           f"Official figures on what it pays, what heat pumps cost and how many grants each council has had.")
    testata = banda(f"Official figures to {PERIODO}", "Heat pump grants in England and Wales", sub, icona="fan")
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}]
    if f_ld:
        ld.append(f_ld)
    pagina("", "Heat Pump Grant UK 2026: £7,500 Boiler Upgrade Scheme Figures",
           f"Boiler Upgrade Scheme 2026: £7,500 or £9,000 off a heat pump, median cost {gbp(MED)} before the grant, and grants paid in every council area.",
           corpo, testata, jsonld=ld)


# ---------------------------------------------------------------- regole
def eligibility():
    rim = Rimandi()
    fs = B["frasi_scheda"]
    corpo = '<div class="card pull testo">' + rim.t(
        '<p>The Boiler Upgrade Scheme gives a grant towards replacing fossil fuel or electric heating with a heat pump (or, in limited cases, a biomass boiler) '
        'in England and Wales. It is run by Ofgem for the Department for Energy Security and Net Zero, and it is <strong>installer-led</strong>: your MCS certified '
        'installer applies for you and takes the grant off your quote.[[ofgem_bus,gov_apply]]</p>') + "</div>"
    corpo += '<h2 id="amounts">How much you can get</h2>'
    corpo += ('<div class="tab"><table class="dati"><thead><tr><th scope="col">Technology</th><th scope="col" class="n">Grant</th><th scope="col">Conditions</th></tr></thead><tbody>'
              '<tr><td>Air source (air-to-water) heat pump</td><td class="n">£7,500</td><td>Replaces fossil fuel or electric heating</td></tr>'
              '<tr><td>Ground source heat pump (including water source and shared ground loops)</td><td class="n">£7,500</td><td>As above</td></tr>'
              '<tr class="qui"><td>Air source or ground source heat pump, off the gas grid</td><td class="n">£9,000</td><td>Property heated by oil or LPG with no mains gas connection; from 21 July 2026 until 31 March 2027</td></tr>'
              '<tr><td>Air-to-air heat pump</td><td class="n">£2,500</td><td>Residential properties only; since 28 April 2026</td></tr>'
              '<tr><td>Biomass boiler</td><td class="n">£5,000</td><td>Rural property with no gas grid connection; not self-builds</td></tr>'
              f'</tbody><caption>One grant per property.{rim.ref("gov_apply,ofgem_bus,ofgem_owners")}</caption></table></div>')
    corpo += rim.t('<div class="testo"><p>GOV.UK describes the £9,000 rate as an additional £1,500 “until March 2027” for a property heated by oil or LPG that does not have '
                   'a mains gas connection; Ofgem lists it as £9,000 “available from 21 July 2026 until 31 March 2027”. Both describe the same grant.[[gov_apply,ofgem_owners]]</p></div>')
    corpo += '<h2 id="who">Who is eligible</h2>' + rim.t(
        '<ul class="testo"><li><strong>You own the property</strong>: your home, a second home, a property you rent out to tenants or a business building.[[gov_apply]]</li>'
        '<li><strong>You replace fossil fuel or electric heating</strong>, such as gas, oil, LPG or electric heaters. You cannot get a grant to replace an existing low carbon system.[[gov_apply,ofgem_owners]]</li>'
        '<li>You are still eligible if you have already had funding for insulation or other energy efficiency work.[[gov_apply]]</li>'
        '<li>The property is in England or Wales. Scotland and Northern Ireland are not covered.[[gov_apply,ofgem_bus]]</li></ul>')
    corpo += '<h2 id="excluded">Properties that cannot get the grant</h2>' + rim.t(
        '<ul class="testo"><li><strong>Most new builds</strong>, and any new build the developer is still building. If you move into a finished new build that has a fossil fuel boiler, you may be able to get the grant.[[gov_apply]]</li>'
        '<li><strong>Social housing</strong>: Ofgem means accommodation provided at lower than market value to people who could not otherwise afford it, including shared ownership.[[ofgem_owners]]</li>'
        '<li>A property that has already had government funding (or Energy Company Obligation funding) for a heat pump or biomass boiler.[[gov_apply,ofgem_owners]]</li>'
        '<li>Non-residential buildings, if the system is an air-to-air heat pump.[[ofgem_owners]]</li></ul>'
        '<p class="testo">Self-builds can qualify if you or the original owner built the property (or paid a builder to) and it has never been owned by a business or organisation.[[gov_apply]]</p>')
    corpo += '<h2 id="system">What the system must be</h2>' + rim.t(
        '<ul class="testo"><li>Not a hybrid: a heat pump combined with a gas or oil boiler is not eligible.[[gov_apply,ofgem_owners]]</li>'
        '<li>Able to meet the full space heating and hot water needs of the property, and sized for the full space heating need.[[ofgem_owners]]</li>'
        '<li>Up to 45 kWth for a single system (70 kWth with more than one heat pump, 300 kWth for shared ground loops).[[gov_apply]]</li>'
        '<li>Installed and commissioned by an MCS certified installer; since 28 April 2026 MCS is the only certification scheme accepted.[[gov_apply,bus_xlsx]]</li>'
        '<li>Biomass boilers only in rural properties with no gas grid connection, with an emissions certificate.[[gov_apply,ofgem_owners]]</li></ul>')
    corpo += AD
    corpo += '<h2 id="apply">How the application works</h2>' + rim.t(
        '<ol class="testo"><li>Get quotes from MCS certified installers. Ofgem recommends getting more than one.[[gov_apply,ofgem_owners,mcs_find]]</li>'
        '<li>Your installer confirms you are eligible, you agree a quote, and the installer applies to Ofgem for you.[[gov_apply]]</li>'
        '<li>Ofgem contacts you to confirm the installer is acting for you. If you do not confirm within 14 calendar days, the application may be rejected.[[ofgem_owners]]</li>'
        '<li>Once the voucher is approved the installer has three months to finish the work (six months for a ground source heat pump), then claims the grant from Ofgem.[[ofgem_owners,bus_xlsx]]</li>'
        '<li>The grant appears as a discount on your quote and invoice. Since 28 April 2026 installers must take it off the upfront cost.[[gov_apply,bus_xlsx]]</li></ol>'
        '<p class="testo">Ofgem or MCS may contact you, or visit, to check the installation, including after the grant has been paid.[[gov_apply,ofgem_owners]]</p>')
    corpo += '<h2 id="vat">VAT</h2>' + rim.t('<p class="testo">From 1 April 2022 to 31 March 2027, the installation of heat pumps and biomass boilers is charged VAT at the zero rate, according to Ofgem.[[ofgem_owners]]</p>')
    corpo += '<h2 id="changes">How the rules have changed</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Date</th><th scope="col">Change (DESNZ wording)</th></tr></thead><tbody>'
    for k in ("ottobre2023", "maggio2024", "aprile2026", "luglio2026"):
        dt, testo = fs[k].split(": ", 1)
        testo = testo.split(" Statistics on the uptake")[0]
        corpo += f"<tr><td>{h(dt)}</td><td>{h(testo)}</td></tr>"
    corpo += f'</tbody><caption>From the “Scheme background” sheet of the DESNZ statistics.{rim.ref("bus_xlsx")}</caption></table></div>'
    corpo += rim.t(f'<div class="testo"><p>{h(fs["budget"])} {h(fs["fino"])} {h(fs["primo_arrivato"])}[[bus_xlsx]]</p></div>')
    corpo += box_preventivo("eligibility")
    f_html, f_ld = faq_blocco("eligibility", rim)
    corpo += f_html + rim.elenco()
    testata = banda("Boiler Upgrade Scheme · rules", "Who can get the heat pump grant", "Eligibility for the Boiler Upgrade Scheme in England and Wales, with the "
                    f"official wording from GOV.UK and Ofgem, checked on {data_lunga(CONTROLLO)}.", corta=True, icona="shield")
    pagina("eligibility/", "Boiler Upgrade Scheme Eligibility 2026: Who Can Get the Grant",
           "Who can get the £7,500, £9,000 or £2,500 heat pump grant: owners, landlords, new builds, EPC, hybrid systems and how the installer applies.",
           corpo, testata, briciole=[("Home", ""), ("Eligibility", "eligibility/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- costi
def costo():
    rim = Rimandi()
    corpo = cifre([(gbp(MED), f"median air source heat pump, {TRIM_L}", True), (gbp(MED - GRANT), "median after the £7,500 grant", False),
                   (f"{gbp(LQ)}–{gbp(UQ)}", "middle half of installations", False), (gbp(GMED), f"median ground source heat pump, {TRIM_L}", False)], asof_bus())
    corpo += rim.t(f'<div class="testo"><p>These are the costs installers reported for every installation with a Boiler Upgrade Scheme grant paid, published by DESNZ. '
                   f'They include the grant value and cover England and Wales as a whole: there are no official figures by region or council.[[bus_xlsx]] '
                   f'{h(B["frasi_scheda"]["prezzo_pagato"])}[[bus_xlsx]]</p></div>')
    corpo += '<h2 id="after">Cost after the grant</h2>' + tabella_costo(rim)
    corpo += AD
    # trimestri
    med = CA["Median cost of installation (£)"]
    lqs, uqs = CA["Lower quartile cost of installation (£)"], CA["Upper quartile cost of installation (£)"]
    reali = B["costi_reali"]["Air-to-Water Heat Pump"]["Median real cost of installation (£)"]
    tr = "".join(f'<tr><td>{h(trimestre_lungo(t))}</td><td class="n">{gbp(lqs[t])}</td><td class="n">{gbp(med[t])}</td><td class="n">{gbp(uqs[t])}</td>'
                 f'<td class="n">{gbp(reali[t]) if pubblicato(reali.get(t)) else "–"}</td></tr>' for t in reversed(B["trimestri"]))
    primo = B["trimestri"][1]
    _m14 = re.search(r"After adjusting for inflation, the median cost of an AWHP in (20\d\d Q\d) is (\d+)% lower than the same period in the first year of the scheme \((20\d\d Q\d); £([\d,]+)\)", " ".join(B["commento"]))
    corpo += rim.t(f'<h2 id="trend">Air source heat pump costs since 2022</h2><div class="testo"><p>In cash terms the median has stayed between '
                   f'{gbp(min(med.values()))} and {gbp(max(med.values()))} a quarter since the scheme began. After inflation it has fallen: DESNZ says the median in '
                   f'{_m14.group(1)} was {_m14.group(2)}% lower than in {_m14.group(3)}, when it was £{_m14.group(4)} in today\'s prices.[[bus_xlsx]] DESNZ notes that the '
                   f'mix of heat pump sizes also moves the median.</p></div>')
    corpo += barre([(t[:7], med[t], f"{trimestre_lungo(t)}: median {gbp(med[t])}") for t in B["trimestri"][-12:]], "Median installed cost by quarter (£)", "Air source, cash terms")
    corpo += (f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Quarter</th><th scope="col" class="n">Lower quartile</th><th scope="col" class="n">Median</th>'
              f'<th scope="col" class="n">Upper quartile</th><th scope="col" class="n">Median, adjusted for inflation</th></tr></thead><tbody>{tr}</tbody>'
              f'<caption>Air source (air-to-water) heat pumps with a grant paid, England and Wales.{rim.ref("bus_xlsx")}</caption></table></div>')
    # fasce
    fa = FASCE["Air-to-Water Heat Pumps"]
    tr = "".join(f'<tr{" class=qui" if b == "All" else ""}><td>{"All sizes" if b == "All" else h(b)}</td><td class="n">{n(fa[b][ANNO_F]["numero"]) if pubblicato(fa[b][ANNO_F]["numero"]) else "–"}</td>'
                 f'<td class="n">{gbp(fa[b][ANNO_F]["mediana"]) if pubblicato(fa[b][ANNO_F]["mediana"]) else "–"}</td>'
                 f'<td class="n">{gbp(fa[b][ANNO_F]["mediana"] - GRANT) if pubblicato(fa[b][ANNO_F]["mediana"]) else "–"}</td></tr>' for b in fa)
    corpo += rim.t(f'<h2 id="size">Cost by size of heat pump, {ANNO_F}</h2><div class="testo"><p>Heat pumps are sized by their heat output in kilowatts, and the official cost rises with size. '
                   f'The median air source heat pump paid through the scheme in {TRIM_L} was {B["costi_trimestre"]["Air-to-Water Heat Pump"]["Median capacity of installation (kW)"][TRIM]} kW.[[bus_xlsx]]</p></div>')
    corpo += (f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Capacity</th><th scope="col" class="n">Installations</th><th scope="col" class="n">Median cost</th>'
              f'<th scope="col" class="n">After £7,500</th></tr></thead><tbody>{tr}</tbody><caption>Air source heat pumps with a grant paid in the {ANNO_F} financial year '
              f'({anno_lungo(ANNO_F)}). Each band includes its lower limit.{rim.ref("bus_xlsx")}</caption></table></div>')
    fg = FASCE["Ground Source Heat Pumps"]
    tr = "".join(f'<tr{" class=qui" if b == "All" else ""}><td>{"All sizes" if b == "All" else h(b)}</td><td class="n">{n(fg[b][ANNO_F]["numero"]) if pubblicato(fg[b][ANNO_F]["numero"]) else "not published"}</td>'
                 f'<td class="n">{gbp(fg[b][ANNO_F]["mediana"]) if pubblicato(fg[b][ANNO_F]["mediana"]) else "not published"}</td></tr>' for b in fg)
    corpo += rim.t(f'<h2 id="ground">Ground source heat pumps</h2><div class="testo"><p>Ground source systems cost much more than air source ones. '
                   f'The median was {gbp(GMED)} in {TRIM_L} and {gbp(fg["All"][ANNO_F]["mediana"])} over {ANNO_F}; with far fewer installations, the quarterly '
                   f'figure moves a lot.[[bus_xlsx]]</p></div>'
                   f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Capacity</th><th scope="col" class="n">Installations</th><th scope="col" class="n">Median cost</th></tr></thead>'
                   f'<tbody>{tr}</tbody><caption>Ground source heat pumps with a grant paid in {ANNO_F}. “Not published”: DESNZ hides medians based on 1 to 4 installations.[[bus_xlsx]]</caption></table></div>')
    corpo += box_preventivo("cost")
    f_html, f_ld = faq_blocco("cost", rim)
    corpo += f_html + rim.elenco()
    testata = banda("Boiler Upgrade Scheme · cost", "How much a heat pump costs after the grant", f"Official installed costs for heat pumps with a grant paid in England "
                    f"and Wales: median {gbp(MED)} in {TRIM_L}, about {gbp(MED - GRANT)} after the £7,500 grant.", corta=True, icona="pound")
    pagina("heat-pump-cost/", "Heat Pump Cost UK 2026: Official Median After the Grant",
           f"Air source heat pumps cost a median {gbp(MED)} in {TRIM_L} ({gbp(MED - GRANT)} after the £7,500 grant). Costs by size, since 2022 and for ground source.",
           corpo, testata, briciole=[("Home", ""), ("Heat pump cost", "heat-pump-cost/")], jsonld=[f_ld] if f_ld else None)


# ---------------------------------------------------------------- solare
def tabella_solare_regioni(rim):
    tr = ""
    for r in REG_UK:
        et, cr = ET[r], COSTI_SOL.get(r, {}).get(ANNO_SOL)
        tr += (f'<tr><td><a href="/solar-panels/{SLUG_REG[r]}/">{h(NOME_REG[r])}</a></td><td class="n">{n(et["numero"][MESE_ET])}</td>'
               f'<td class="n">{n(et["numero"][MESE_ET] - et["numero"][MESE_ET_PRIMA])}</td><td class="n">{n(et["mw"][MESE_ET])}</td>'
               f'<td class="n">{gbp(cr["media_0_4"]) if cr else "–"}</td><td class="n">{gbp(cr["media_4_10"]) if cr else "–"}</td></tr>')
    return (f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Region</th><th scope="col" class="n">Installations, {mese_lungo(MESE_ET)}</th>'
            f'<th scope="col" class="n">Added in 12 months</th><th scope="col" class="n">Capacity (MW)</th><th scope="col" class="n">£ per kW, up to 4 kW</th>'
            f'<th scope="col" class="n">£ per kW, 4–10 kW</th></tr></thead><tbody>{tr}</tbody><caption>Installations and capacity: all solar PV, homes and businesses '
            f'(DESNZ Energy Trends table 6.3).{rim.ref("solare_et63_xlsx")} Cost: average (mean) per kW of panel capacity for systems installed in {ANNO_SOL}, '
            f'Great Britain only, so no figure for Northern Ireland is published in the regional table.{rim.ref("solare_costi_xlsx")}</caption></table></div>')


def solare_hub():
    rim = Rimandi()
    uk = ET["UK"]
    corpo = cifre([(n(uk["numero"][MESE_ET]), f"solar installations in the UK, end of {mese_lungo(MESE_ET)}", True),
                   (n(uk["numero"][MESE_ET] - uk["numero"][MESE_ET_PRIMA]), "added in the last 12 months", False),
                   (gbp(SOMM_SOL["mediana_0_4"]), f"median cost per kW, systems up to 4 kW, {ANNO_SOL}", False),
                   (gbp(3 * SOMM_SOL["mediana_0_4"]), "a 3 kW system at that rate (our arithmetic)", False)],
                  f"DESNZ solar deployment to {mese_lungo(MESE_ET)} (published {data_lunga(S['et63_pubblicato'])}) and solar cost data for {ANNO_SOL} (published {data_lunga(S['costi_pubblicato'])}).")
    corpo += rim.t(f'<div class="testo"><p>{h(S["et63_commento"][0])}[[solare_et63_xlsx]]</p></div>')
    corpo += '<h2 id="regions">Solar installations and cost per kW by region</h2>' + tabella_solare_regioni(rim)
    corpo += AD
    ss = S["costi_sommario"]
    anni = sorted(ss)[-6:]
    tr = "".join(f'<tr><td>{a}</td><td class="n">{gbp(ss[a]["mediana_0_4"])}</td><td class="n">{gbp(ss[a]["mediana_4_10"])}</td><td class="n">{gbp(ss[a]["mediana_10_50"])}</td></tr>'
                 for a in reversed(anni))
    corpo += rim.t(f'<h2 id="cost">What solar panels cost per kW</h2><div class="testo"><p>DESNZ calculates these costs from the Microgeneration Certification Scheme '
                   f'database. They include the panels, installation, connection and VAT where applicable, but not batteries or other devices. The table uses the '
                   f'total installed capacity of the panels; DESNZ also publishes a second series per declared net capacity (the most a system can export), not used here.[[solare_costi_xlsx]]</p></div>'
                   f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Financial year</th><th scope="col" class="n">Up to 4 kW</th><th scope="col" class="n">4–10 kW</th>'
                   f'<th scope="col" class="n">10–50 kW</th></tr></thead><tbody>{tr}</tbody><caption>Median cost per kW, Great Britain, cash terms.[[solare_costi_xlsx]]</caption></table></div>')
    dom = S["costi_domestici"].get(f"{ANNO_SOL} Domestic")
    if dom:
        corpo += rim.t(f'<p class="testo">On homes alone, {n(dom["n"])} installations in {ANNO_SOL} averaged {gbp(dom["media_0_4"])} per kW up to 4 kW and '
                       f'{gbp(dom["media_4_10"])} per kW from 4 to 10 kW.[[solare_costi_xlsx]]</p>')
    corpo += box_preventivo("solar")
    f_html, f_ld = faq_blocco("solar", rim)
    corpo += f_html + rim.elenco()
    testata = banda("Solar panels · official figures", "Solar panels: installations and cost by region", "How many solar installations each UK region has, how fast "
                    "they are growing, and what small systems cost per kW, from DESNZ statistics.", corta=True, icona="solar")
    pagina("solar-panels/", "Solar Panel Cost UK 2026 by Region: Official £ per kW",
           f"Solar panels cost a median {gbp(SOMM_SOL['mediana_0_4'])} per kW (up to 4 kW) in {ANNO_SOL}. Installations and average cost per kW in every UK region.",
           corpo, testata, briciole=[("Home", ""), ("Solar panels", "solar-panels/")], jsonld=[f_ld] if f_ld else None)


def solare_regione(r):
    rim = Rimandi()
    nel = NEL_REG[r]
    et, cr = ET[r], COSTI_SOL.get(r, {}).get(ANNO_SOL)
    la = sorted([v for v in LA_UK.values() if v["regione"] == r], key=lambda v: -v["siti"]["2025"])
    def s(v, y):
        return v["siti"].get(str(y))
    def m(v, y):
        return v["mw"].get(str(y))
    sol_mw = et["mw"][MESE_ET]
    voci = [(n(et["numero"][MESE_ET]), f"solar installations, end of {mese_lungo(MESE_ET)}", True),
            (n(et["numero"][MESE_ET] - et["numero"][MESE_ET_PRIMA]), "added in the last 12 months", False)]
    if cr:
        voci += [(gbp(cr["media_0_4"]), f"average per kW, up to 4 kW, {ANNO_SOL}", False), (gbp(cr["media_4_10"]), f"average per kW, 4–10 kW, {ANNO_SOL}", False)]
    else:
        voci += [(n(sol_mw), f"MW of solar capacity, end of {mese_lungo(MESE_ET)}", False), (n(len(la)), "councils", False)]
    corpo = f"<!-- solar-region: {r} -->" + cifre(voci,
                  f"DESNZ figures: deployment to {mese_lungo(MESE_ET)} (published {data_lunga(S['et63_pubblicato'])}), costs for {ANNO_SOL}, local authorities to the end of 2025.")
    corpo += rim.t(f'<div class="testo"><p>{h(cap(nel))} had <strong>{n(et["numero"][MESE_ET])}</strong> solar installations with {n(et["mw"][MESE_ET])} MW of capacity at the end of '
                   f'{mese_lungo(MESE_ET)}.[[solare_et63_xlsx]] '
                   + (f'In {ANNO_SOL}, {n(cr["n_0_4"])} systems up to 4 kW were installed in the region at an average of '
                      f'{gbp(cr["media_0_4"])} per kW, and {n(cr["n_4_10"])} systems of 4 to 10 kW at {gbp(cr["media_4_10"])} per kW. At those averages a 3 kW system '
                      f'comes to about {gbp(3 * cr["media_0_4"])} and a 6 kW system to about {gbp(6 * cr["media_4_10"])} (our arithmetic).[[solare_costi_xlsx]]' if cr else
                      'DESNZ cost statistics cover Great Britain only, so there is no official cost per kW for Northern Ireland.[[solare_costi_xlsx]]')
                   + '</p></div>')
    ms = list(et["numero"].keys())[-12:]
    corpo += barre([(k, et["numero"][k] - et["numero"][list(et["numero"].keys())[list(et["numero"].keys()).index(k) - 1]],
                     f"{mese_lungo(k)}: new installations") for k in ms], "New solar installations per month", "Change in the cumulative count; provisional")
    corpo += AD
    tr = "".join(f'<tr data-riga="{h(v["nome_pulito"])}"><td>' + (f'<a href="/{PER_COD[v["codice"]]["url"]}#solar">{h(v["nome_pulito"])}</a>' if v["codice"] in PER_COD and PER_COD[v["codice"]]["tipo"] == "council" else h(v["nome_pulito"]))
                 + f'</td><td class="n">{n(s(v, 2025))}</td><td class="n">{n(s(v, 2020)) if s(v, 2020) is not None else "–"}</td><td class="n">{n(m(v, 2025), 1)}</td>'
                 f'<td class="n">{n(s(v, 2025) / v["famiglie"] * 1000) if v.get("famiglie") else "–"}</td></tr>' for v in la)
    corpo += (f'<h2 id="councils">Solar installations by council in {h(nel)}</h2><div class="cerca"><input type="search" data-cerca="tab-sol" placeholder="Find a council" aria-label="Find a council"></div>'
              f'<div class="tab" id="tab-sol"><table class="dati"><thead><tr><th scope="col">Council</th><th scope="col" class="n">Installations, end 2025</th>'
              f'<th scope="col" class="n">End 2020</th><th scope="col" class="n">Capacity 2025 (MW)</th><th scope="col" class="n">Per 1,000 households</th></tr></thead>'
              f'<tbody>{tr}<tr data-vuoto hidden><td colspan="5">No council matches.</td></tr></tbody><caption>All solar PV in each local authority (homes, businesses, solar farms). '
              f'Many 2025 installations could not yet be assigned to a local authority, so 2025 counts will be revised up. Per 1,000 households: our calculation with the '
              f'household estimates in the same file.{rim.ref("solare_la_xlsx")}</caption></table></div>')
    if r in REG_EW:
        corpo += rim.t(f'<p>Heat pumps: <a href="/heat-pump-grants/{SLUG_REG[r]}/">{n(CUM[r])} Boiler Upgrade Scheme grants paid in {h(nel)}</a>.[[bus_xlsx]]</p>')
    else:
        corpo += rim.t(f'<p class="small">The Boiler Upgrade Scheme does not cover {h(nel)}: it is open in England and Wales only.[[gov_apply]]</p>')
    corpo += box_preventivo("solar_regione")
    corpo += '<h2>Other regions</h2><ul class="pillole">' + "".join(f'<li><a href="/solar-panels/{SLUG_REG[x]}/">{h(NOME_REG[x])}</a></li>' for x in REG_UK if x != r) + "</ul>"
    corpo += rim.elenco()
    testata = banda("Solar panels · region", f"Solar panels in {nel}", f"<strong>{n(et['numero'][MESE_ET])}</strong> installations, "
                    + (f"the average cost per kW in {ANNO_SOL} " if cr else "the monthly growth ") + f"and the count for each of its {len(la)} councils.", icona="solar")
    titolo = titolo_corto(f"Solar Panels in {nel}: Installations and Cost per kW", f"Solar Panels in {nel}: Cost per kW", f"Solar Panels in {nel}")
    descr = descr_corta((f"Solar panels in {nel}: {n(et['numero'][MESE_ET])} installations, {gbp(cr['media_0_4'])} per kW for systems up to 4 kW in {ANNO_SOL}, and the count for every council." if cr else
                         f"Solar panels in {nel}: {n(et['numero'][MESE_ET])} installations and {n(sol_mw)} MW at the end of {mese_lungo(MESE_ET)}, and the count for each of its councils."),
                        f"Solar panels in {nel}: {n(et['numero'][MESE_ET])} installations, cost per kW and the count for every council.")
    pagina(f"solar-panels/{SLUG_REG[r]}/", titolo, descr, corpo, testata,
           briciole=[("Home", ""), ("Solar panels", "solar-panels/"), (NOME_REG[r], f"solar-panels/{SLUG_REG[r]}/")])


# ---------------------------------------------------------------- pagine istituzionali
def about():
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{NOME}</strong> is an independent publication, part of a small network of websites that turn official data into plain-language guides. '
             'It shows what the Boiler Upgrade Scheme pays, what heat pumps cost after the grant, and how many grants have been paid in each council area of England '
             'and Wales, using the statistics DESNZ publishes every month. The council figures exist in the official spreadsheets but are hard to find; this site puts '
             'each one on its own page.</p>'
             '<p>We are not a government website, an installer or an energy company, and we are not linked to Ofgem, DESNZ or MCS.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Only figures that are in an official file or on an official page, each with its source and date.</li>'
             '<li>Where DESNZ hides a small number, or does not publish a figure at all (costs by region, for example), we say so instead of estimating it.</li>'
             '<li>Our own arithmetic (cost after the grant, rates per household) is labelled as ours.</li></ul>'
             '<h2>How the site is paid for</h2><div class="testo"><p>The site shows advertising served by Google AdSense. In future it may show a labelled “get a quote” '
             'link to installers through partner programmes. Partners never decide what we publish or change a figure.</p></div>'
             '<h2>Corrections</h2><div class="testo"><p>If you spot an error, use the <a href="/how-we-check/#corrections">corrections form</a>: we check it against the '
             'official source and fix the page.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, what it publishes and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", "About Heat Pump Grants UK: an independent guide to the Boiler Upgrade Scheme and solar statistics built only from official sources.",
           corpo, testata, briciole=[("Home", ""), ("About", "about/")])


MODULO_CORREZIONI = """<form name="corrections" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card">
<input type="hidden" name="form-name" value="corrections">
<p class="hp"><label>Leave this field empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Page or figure<input type="text" name="page" required maxlength="300" placeholder="For example /heat-pump-grants/cornwall/"></label>
<label>What is wrong?<textarea name="message" required rows="5" maxlength="3000"></textarea></label>
<label>Official source (optional)<input type="url" name="source" maxlength="500" placeholder="https://"></label>
<label>Your email (optional, only if you want a reply)<input type="email" name="email" maxlength="200" autocomplete="email"></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I agree that this message, and my email if I gave one, is stored to check and answer the correction (see <a href="/privacy/#corrections">privacy</a>).</span></label>
<button type="submit" class="btn">Send correction</button>
</form>"""


def come_controlliamo():
    rim = Rimandi()
    frasi = sum(len(FONTI[k].get("cerca", [])) for k in FONTI if FONTI[k]["tipo"] == "pagina")
    n_idx = sum(1 for a in COUNCIL if a["indicizza"])
    corpo = ('<div class="testo pull card">'
             f'<p>Every figure on this site comes from four official spreadsheets published by the Department for Energy Security and Net Zero, and every rule from '
             f'GOV.UK and Ofgem. On {data_lunga(CONTROLLO)} we downloaded the latest files, recorded their fingerprints, and checked <strong>{frasi}</strong> exact '
             'sentences on the official rule pages. Before any update, a separate program re-reads the spreadsheets and recalculates every number printed on the site.</p></div>')
    corpo += rim.t('<h2>The files</h2><ul class="testo">'
                   f'<li>Boiler Upgrade Scheme statistics: grants paid by council and region, applications by month, installed costs. Monthly; council and cost tables every three months.[[bus_xlsx]]</li>'
                   '<li>Renewable electricity by local authority: solar installations and capacity in every UK council at the end of each year, with household estimates.[[solare_la_xlsx]]</li>'
                   '<li>Solar photovoltaics deployment (Energy Trends table 6.3): installations and capacity by region, monthly.[[solare_et63_xlsx]]</li>'
                   '<li>Solar PV cost data: cost per kW by size and region, every year.[[solare_costi_xlsx]]</li>'
                   '<li>The rules: GOV.UK “Apply for the Boiler Upgrade Scheme” and Ofgem\'s scheme and property owner pages.[[gov_apply,ofgem_bus,ofgem_owners]]</li></ul>')
    corpo += ('<h2>What we calculate ourselves</h2><ul class="testo">'
              '<li><strong>Cost after the grant</strong>: the official installed cost minus £7,500 (or £9,000). DESNZ costs include the grant value.</li>'
              '<li><strong>Grants paid per 1,000 households</strong>: grants paid to date divided by the household estimates in the DESNZ local authority renewables file. '
              'Region pages also show DESNZ\'s own rate per 10,000 households, which counts homes only.</li>'
              '<li><strong>2026/27 so far</strong>: the total to date minus the four complete financial years, only where none of them is hidden.</li>'
              '<li><strong>Example solar system costs</strong>: kW times the official cost per kW.</li></ul>')
    corpo += (f'<h2>Small numbers and missing figures</h2><div class="testo"><p>DESNZ hides counts of 1 to 4 (and some others, so they cannot be worked out) to protect '
              f'privacy. We show these as “not published” and never estimate them. Council pages are listed for search engines only when the council has at least '
              f'{SOGLIA_INDICE} grants paid and every year is published: {n_idx} of {len(COUNCIL)} councils today. The others stay available from the tables.</p>'
              '<p>DESNZ does not publish heat pump costs by region or council, so the cost on every area page is the national figure, and each page says so.</p></div>')
    corpo += ('<h2>Licence and attribution</h2><div class="testo"><p>' + OGL + ' The council and region tables of the Boiler Upgrade Scheme statistics also contain OS data '
              '© Crown copyright and database right 2026 and Royal Mail data © Royal Mail copyright and database right 2026, and use the National Statistics Postcode '
              'Lookup (Office for National Statistics, Open Government Licence v3.0). GOV.UK content is also Crown copyright under the Open Government Licence.</p></div>')
    corpo += ('<h2>When we update</h2><div class="testo"><p>DESNZ publishes the Boiler Upgrade Scheme statistics once a month (next: '
              f'{data_lunga(B["prossima"])}); the council and cost tables change each quarter. Solar deployment is monthly, solar costs every May and the local '
              'authority solar file every September. The site is regenerated after each release, once every figure has passed the checks.</p></div>')
    corpo += ('<h2 id="corrections">Report an error</h2><div class="testo"><p>Seen a figure that does not match the official file, or a rule that has changed? Tell us which '
              'page and, if you can, link the source. Your email is optional.</p></div>' + MODULO_CORREZIONI)
    corpo += rim.elenco()
    testata = banda("How we check", "How we check every figure", "Our sources, what we calculate, how small numbers are handled and how to report an error.", corta=True, icona="shield")
    pagina("how-we-check/", "How We Check Heat Pump Grant and Solar Figures",
           "How Heat Pump Grants UK checks its figures: four official DESNZ files with fingerprints, rule pages re-read, every number recalculated, and corrections.",
           corpo, testata, briciole=[("Home", ""), ("How we check", "how-we-check/")])


def privacy():
    cookie = MON.privacy_cookie("en", SITO_ID, affiliati=ci_sono_affiliati())
    if not cookie:
        cookie = "<h2>Cookies and visit counter</h2><p>To count visits we use GoatCounter, which sets no cookies. This site does not use profiling cookies and shows no advertising.</p>"
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {NOME} ({URL_SITO.replace("https://", "")}) collects. In short: very little.</p></div>'
             '<div class="testo"><h2>Your choices on the site</h2><p>The search boxes in the tables work in your browser; nothing you type is sent to us. The site '
             'remembers your choice of light or dark theme in your browser (local storage). Nothing else is stored on your device by us.</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             '<h2 id="corrections">Corrections form</h2><p>If you use the <a href="/how-we-check/#corrections">corrections form</a>, we receive the page you name, your message, '
             'the source link and, only if you give it, your email address. The form is processed by Netlify Forms on our behalf. We use what you send only to check and '
             'answer the correction, and keep it only as long as that takes. The legal basis is your consent, given with the tick box; you can ask us to delete your '
             'message by sending another one through the form. There are no accounts or newsletters on this site.</p>'
             f'<h2>Changes</h2><p>We update this page when the site changes. Last update: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID, affiliati=ci_sono_affiliati()) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", f"Privacy | {NOME}", f"Privacy at {NOME}: a cookie-free visit counter, Google AdSense advertising only with consent, and the corrections form.",
           corpo, testata, briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = ('<div class="pull card"><p>The page you asked for does not exist. Try <a href="/heat-pump-grants/">grants by council</a>, '
             '<a href="/eligibility/">who can get the grant</a> or one of the regions below.</p></div>' + griglia_regioni())
    testata = banda("404", "Page not found", "This address has no page.", corta=True, icona="alert")
    pagina("", f"Page not found | {NOME}", "Page not found on Heat Pump Grants UK: try grants by council, eligibility or a region.", corpo, testata.replace("{bc}", ""),
           indicizza=False, file="404.html")


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
  # Pubblica solo se è cambiato qualcosa in heatpumps/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = heatpumps/sito, Build command vuoto, Publish directory = "."
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
        if es.get("http") != 200:
            err.append(f"fonte {fid}: HTTP {es.get('http')} all'ultima lettura")
        mancano = [c for c, ok in es.get("trovate", {}).items() if not ok]
        if mancano:
            err.append(f"fonte {fid}: frasi non più presenti {mancano}")
    if date.today() > date.fromisoformat("2027-03-31"):
        err.append("il contributo da £9,000 e l'IVA a zero valevano fino al 31/3/2027: rileggere le regole (NOTE.md)")
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
    eligibility()
    costo()
    hub_aree()
    for r in REG_EW:
        pagina_regione(r)
    for c in CONTEE:
        pagina_area(c)
    for a in COUNCIL:
        pagina_area(a)
    solare_hub()
    for r in REG_UK:
        solare_regione(r)
    about()
    come_controlliamo()
    privacy()
    pagina_404()
    extra()
    n_no = len(COUNCIL) - sum(1 for a in COUNCIL if a["indicizza"])
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili, {n_no} pagine council noindex + 404. Dati BUS a {PERIODO}, fonti controllate il {data_lunga(CONTROLLO)}.")


if __name__ == "__main__":
    main()
