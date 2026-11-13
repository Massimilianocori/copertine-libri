"""Genera il sito statico "Inflation Calculator US·UK·DE" in inflation/sito/.

Uso (dalla radice del repository):
    python3 -I inflation/raccolta/scarica.py   # serie ufficiali BLS, ONS, Destatis -> dati/grezzi/ e dati/fonti.json
    python3 inflation/genera.py                # pagine in inflation/sito/ (si ferma se una serie ha buchi o non torna)
    python3 inflation/verifica.py --browser    # controlli (vedi NOTE.md)

Pagine: calcolatore USA (home), Regno Unito (/uk/, /uk/rpi-calculator/), Germania (/de/inflationsrechner/), tassi per anno
(USA, UK, DE), una pagina per anno USA 1913-2025 (/us/1970-dollars-today/), 20 pagine importo × decennio USA
(/us/100-dollars-in-1970/). Solo i modelli con domanda misurata (dati/domanda.json): niente pagine anno per UK e DE.
Il calcolatore gira nel browser (stile.MOTORE_JS = copia di motore.py). Nessun dato personale.
Sezione tedesca dietro l'interruttore SEZIONE_DE (spenta dal 13/11/2026: niente Impressum; vedi NOTE.md): da spenta il sito è "US & UK".
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
import motore as M  # noqa: E402
import serie  # noqa: E402
import stile  # noqa: E402

# Sezione tedesca (/de/, Destatis): spenta = nessuna pagina /de/, nessun link, nessuna menzione di Germania/Destatis nelle pagine pubblicate.
# Codice e dati tedeschi restano qui sotto e in dati/: basta rimettere True, rigenerare e rifare verifica.py --browser.
SEZIONE_DE = False  # niente Impressum: decisione del 13/11/2026; per riaccendere serve "ok Impressum" di Massimiliano

URL_SITO = "https://inflation-calculator-us-uk-de.netlify.app"  # unico punto da cambiare se il nome su Netlify è diverso
NOME = "Inflation Calculator US·UK·DE" if SEZIONE_DE else "Inflation Calculator US & UK"
FONTI_DE = ("destatis_tabelle", "destatis_lange_reihen", "ecb_euro", "eurlex_2866")  # fonti usate solo dalle pagine tedesche
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
SITO_ID = "inflation"
ADSENSE_HEAD = MON.script_adsense(SITO_ID)

FONTI = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))
DOMANDA = json.loads((DATI / "domanda.json").read_text(encoding="utf-8"))
ESEMPI_BLS = json.loads((DATI / "esempi_bls.json").read_text(encoding="utf-8"))["casi"]
S = serie.tutte()
C = {k: M.compatta(S[k]) for k in ("us", "uk_cpi", "uk_rpi", "de")}
ULT = {k: max(S[k]["mensile"]) for k in C}
CONTROLLO = date.fromisoformat(FONTI["bls_cpiu"]["letto_il"])
ANNI_US = list(range(1913, max(S["us"]["annuale"]) + 1))
ULTIMO_ANNO_US = ANNI_US[-1]
DECENNI_IMPORTO = list(range(1920, 2011, 10))
IMPORTI_PAGINA = [100, 1000]

MESI = {"en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]}
NOME_SERIE = {"us": "CPI-U, 1982-84=100", "uk_cpi": "CPI, 2015=100", "uk_rpi": "RPI long-run series, Jan 1974=100", "de": "VPI, 2020=100"}
LINGUA = {"us": ("en-US", "en_US", "en"), "uk": ("en-GB", "en_GB", "en"), "de": ("de-DE", "de_DE", "de")}
FAQ_USATE = []  # FAQ pubblicate con la frase di ricerca d'origine: scritte in dati/faq_generate.json, controllate da verifica.py


def h(x):
    return escape(str(x), quote=True)


# ---------------------------------------------------------------- formati
def _migliaia(s, de):
    return s.replace(",", "X").replace(".", ",").replace("X", ".") if de else s


def soldi(x, valuta, dec=2):
    de = valuta in ("EUR", "DEM")
    s = _migliaia(f"{abs(x):,.{dec}f}", de)
    seg = "−" if x < 0 else ""
    return {"USD": f"{seg}${s}", "GBP": f"{seg}£{s}", "EUR": f"{seg}{s} €", "DEM": f"{seg}{s} DM"}[valuta]


def numero(x, dec, de=False):
    return _migliaia(f"{x:,.{dec}f}", de)


def pct(x, dec=1, de=False, segno=True):
    s = numero(abs(x * 100), dec, de)
    zero = round(abs(x * 100), dec) == 0  # 0.0% senza segno (né "+0.0%" né "−0.0%")
    seg = "" if zero else (("+" if x >= 0 else "−") if segno else ("−" if x < 0 else ""))
    return f"{seg}{s}{chr(160) + '%' if de else '%'}"


def cifre(x):
    r = repr(float(x))
    return max(1, min(3, len(r.split(".")[1]))) if "." in r else 1


def idx(x, de=False):
    return numero(x, cifre(x), de)


def mese_lungo(a, m, lingua="en"):
    return f"{MESI[lingua][m - 1]} {a}"


def mese_breve(a, m):
    return f"{MESI['en'][m - 1][:3]} {a}"


def ult_lungo(k, lingua="en"):
    return mese_lungo(*ULT[k], lingua)


def data_lunga(d, lingua="en"):
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return f"{d.day} {MESI[lingua][d.month - 1]} {d.year}" if lingua == "en" else f"{d.day}. {MESI['de'][d.month - 1]} {d.year}"


def val(k, anno, mese=None):
    return M.indice(C[k], anno, mese)


def vale_oggi(k, anno, mese=None):
    """Rapporto indice ultimo mese / indice di partenza."""
    return val(k, *ULT[k]) / val(k, anno, mese)


# ---------------------------------------------------------------- risorse
def _impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:10]


CSS = re.sub(r"\n", "", stile.CSS)
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in stile.ICONE.items()) + "</svg>\n")
APP_JS = stile.APP_JS.strip() + "\n"
ASSET = {f"site.{_impronta(CSS)}.css": CSS, f"app.{_impronta(APP_JS)}.js": APP_JS,
         f"favicon.{_impronta(stile.FAVICON_SVG)}.svg": stile.FAVICON_SVG, f"icons.{_impronta(SPRITE)}.svg": SPRITE}
CSS_FILE, JS_FILE, FAVICON_FILE, ICONS_FILE = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="32" height="32" alt="">'


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# ---------------------------------------------------------------- fonti
LICENZA_TESTO = {
    "bls": "U.S. Bureau of Labor Statistics. Public domain (work of the U.S. federal government).",
    "ons": "Source: Office for National Statistics licensed under the Open Government Licence v.3.0.",
    "destatis": "Quelle: Statistisches Bundesamt (Destatis). Vervielfältigung und Verbreitung, auch auszugsweise, mit Quellenangabe gestattet. "
                "Für Inhalte der Datenbank GENESIS-Online gilt die Datenlizenz Deutschland – Namensnennung – Version 2.0:",
}


def fonti_box(ids, lingua="en"):
    voci = []
    for i in ids:
        f = FONTI[i]
        lic = ""
        if i.startswith("bls"):
            lic = LICENZA_TESTO["bls"]
        elif i.startswith("ons"):
            lic = (LICENZA_TESTO["ons"] + ' <a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noopener">OGL v3.0</a>')
        elif i.startswith("destatis"):
            lic = LICENZA_TESTO["destatis"] + ' <a href="https://www.govdata.de/dl-de/by-2-0" rel="noopener">dl-de/by-2-0</a>'
        letto = (f"Abgerufen am {data_lunga(f['letto_il'], 'de')}" if lingua == "de" else f"Read on {data_lunga(f['letto_il'])}")
        if f.get("stand"):
            letto += f"; Stand der Tabelle: {h(f['stand'])}" if lingua == "de" else f"; table dated {h(f['stand'])}"
        uscita = ""
        if f.get("uscita"):
            uscita = f"; release of {h(f['uscita'].replace('-', '/'))}" if lingua != "de" else f"; Veröffentlichung vom {h(f['uscita'].replace('-', '.'))}"
        lic_html = f"<br><span class=\"small\">{lic if '<a' in lic else h(lic)}</span>" if lic else ""
        voci.append(f'<li><a href="{h(f.get("pagina") or f["url"])}" rel="noopener">{h(f["titolo"])}</a> · {h(f["chi"])}. '
                    f'<span class="small">{letto}{uscita}.</span>{lic_html}</li>')
    tit = "Quellen" if lingua == "de" else "Sources"
    piede = ("Alle Indexwerte stammen aus den amtlichen Dateien oben; wir laden sie jeden Monat neu und prüfen sie, bevor die Seite aktualisiert wird "
             f'(<a href="/how-we-check/">Methodik, auf Englisch</a>).' if lingua == "de" else
             'Every index value comes from the official files above. We download them again each month and check them before the pages change '
             '(<a href="/how-we-check/">how we check</a>).')
    return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}{tit}</h2><ol>{"".join(voci)}</ol>'
            f'<p class="small">{piede}</p></section>')


# ---------------------------------------------------------------- scheletro
URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
DISCLAIMER = {
    "en": ("<strong>General information, not financial or investment advice.</strong> The results show how an official consumer price index changed "
           "between two dates. Your own costs, pay and savings may have changed by more or less. Index values come from the BLS (US)"
           + (", the ONS (UK) and Destatis (Germany)" if SEZIONE_DE else " and the ONS (UK)") + ", linked on each page."),
    "de": ("<strong>Allgemeine Information, keine Finanz- oder Anlageberatung.</strong> Die Ergebnisse zeigen, wie sich ein amtlicher Verbraucherpreisindex "
           "zwischen zwei Zeitpunkten verändert hat. Ihre eigenen Ausgaben, Löhne und Ersparnisse können sich stärker oder schwächer verändert haben. "
           "Die Indexwerte stammen vom Statistischen Bundesamt (Destatis)."),
}


def menu(percorso, paese):
    voci = [("", "US"), ("uk/", "UK")] + ([("de/inflationsrechner/", "Deutschland")] if SEZIONE_DE else [])
    if paese == "de":
        voci.append(("de/inflationsrate-deutschland/", "Inflationsrate"))
    elif paese == "uk":
        voci += [("uk/inflation-rate-by-year/", "UK rates by year"), ("uk/rpi-calculator/", "RPI")]
    else:
        voci += [("us/inflation-rate-by-year/", "US rates by year")]
    return "".join(f'<a href="/{u}"' + (' aria-current="page"' if u == percorso else "") + f">{h(t)}</a>" for u, t in voci)


def pagina(percorso, titolo, descrizione, corpo, testata="", paese="us", briciole=None, jsonld=None, indicizza=True, file=None):
    file = file or (percorso + "index.html" if percorso else "index.html")
    lang, og_loc, lingua = LINGUA[paese]
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append(percorso)
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": i, "name": n, "item": f"{URL_SITO}/{p}"} for i, (n, p) in enumerate(briciole, 1)]
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb">' + " › ".join(
            [f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    de = lingua == "de"
    if de:
        piede_testo = (f"<p><strong>{h(NOME)}</strong> rechnet Geldbeträge mit amtlichen Verbraucherpreisindizes um: Destatis für Deutschland, "
                       "ONS für das Vereinigte Königreich, BLS für die USA. Unabhängige Website, keine Behörde und mit keiner Behörde verbunden.</p>"
                       f"<p>Indexwerte bis {ult_lungo('de', 'de')} (Deutschland). Daten abgerufen am {data_lunga(CONTROLLO, 'de')}.</p>")
        links = [("de/inflationsrechner/", "Inflationsrechner"), ("de/inflationsrate-deutschland/", "Inflationsrate Deutschland"),
                 ("", "US inflation calculator"), ("uk/", "UK inflation calculator")]
        info = [("about/", "Über uns (englisch)"), ("how-we-check/", "Methodik (englisch)"), ("privacy/", "Datenschutz (englisch)")]
        h_calc, h_info, skip, tema_lbl, base = "Rechner", "Info", "Zum Inhalt springen", "Helles oder dunkles Design", \
            "Allgemeine Information, keine Finanzberatung. Amtliche Daten: <a href=\"https://www.destatis.de/\" rel=\"noopener\">destatis.de</a>."
    else:
        if SEZIONE_DE:
            paesi_txt = "the BLS CPI-U for the United States, the ONS CPI and RPI for the United Kingdom and the Destatis VPI for Germany"
            ultimi_txt = f"{ult_lungo('us')} (US), {ult_lungo('uk_cpi')} (UK), {ult_lungo('de')} (Germany)"
        else:
            paesi_txt = "the BLS CPI-U for the United States and the ONS CPI and RPI for the United Kingdom"
            ultimi_txt = f"{ult_lungo('us')} (US), {ult_lungo('uk_cpi')} (UK)"
        piede_testo = (f"<p><strong>{h(NOME)}</strong> converts amounts of money between years with official consumer price indexes: {paesi_txt}. "
                       "It is an independent site, not a government website and not linked to any statistics office.</p>"
                       f"<p>Latest index: {ultimi_txt}. Data read on {data_lunga(CONTROLLO)}.</p>")
        links = [("", "US inflation calculator"), ("us/inflation-rate-by-year/", "US inflation rate by year"), ("uk/", "UK inflation calculator"),
                 ("uk/rpi-calculator/", "RPI calculator"), ("uk/inflation-rate-by-year/", "UK inflation rate by year")]
        if SEZIONE_DE:
            links.append(("de/inflationsrechner/", "Inflationsrechner (DE)"))
        info = [("about/", "About"), ("how-we-check/", "How we check"), ("privacy/", "Privacy")]
        h_calc, h_info, skip, tema_lbl, base = "Calculators", "Site", "Skip to content", "Switch light or dark theme", \
            ('General information only, not financial advice. Official data: <a href="https://www.bls.gov/cpi/" rel="noopener">bls.gov/cpi</a>, '
             '<a href="https://www.ons.gov.uk/economy/inflationandpriceindices" rel="noopener">ons.gov.uk</a>'
             + (', <a href="https://www.destatis.de/" rel="noopener">destatis.de</a>.' if SEZIONE_DE else "."))
    testo = f"""<!DOCTYPE html>
<html lang="{lang}">
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
<meta property="og:site_name" content="{h(NOME)}">
<meta property="og:locale" content="{og_loc}">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#161A33">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<script>{stile.TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">{skip}</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Inflation <b>Calculator</b></span></a>
<nav class="menu" aria-label="Main">{menu(percorso, paese)}</nav>
<button type="button" class="tema" data-tema aria-label="{tema_lbl}">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Menu">{ico("menu")}</summary><nav aria-label="Main">{menu(percorso, paese)}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo}
<p class="disclaimer">{DISCLAIMER[lingua]}</p>
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="/">{LOGO}<span>Inflation <b>Calculator</b></span></a>
{piede_testo}
</div><div>
<h2>{h_calc}</h2><ul>{"".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in links)}</ul>
</div><div>
<h2>{h_info}</h2><ul>{"".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in info)}</ul>
</div></div>
<p class="f-base">{base}</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="trend"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def trust(voci):
    return '<ul class="trust">' + "".join(f"<li>{ico(i)}{h(t)}</li>" for i, t in voci) + "</ul>"


# ---------------------------------------------------------------- FAQ (solo da ricerche misurate)
def faq_blocco(pagina_id, voci, lingua="en"):
    """voci: [(domanda, risposta_html, frase_di_ricerca, paese)]. JSON-LD = testo visibile."""
    if not voci:
        return "", None
    blocchi, ld = [], []
    for q, a, frase, paese in voci:
        FAQ_USATE.append({"pagina": pagina_id, "domanda": q, "ricerca": frase, "paese": paese})
        blocchi.append(f'<div class="faq"><h3>{h(q)}</h3><p>{a}</p></div>')
        ld.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).replace("&amp;", "&")}})
    tit = "Häufige Fragen" if lingua == "de" else "Common questions"
    return (f'<h2 id="faq">{tit}</h2>' + "".join(blocchi)), {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


# ---------------------------------------------------------------- grafici (SVG + etichette HTML, leggibili a ogni larghezza)
def _passo(span):
    for p in (5, 10, 20, 25, 50, 100):
        if span / p <= 4:
            return p
    return 200


def _etichette_x(x0, x1, fx):
    out = [f'<span class="gx first" style="left:0">{h(fx(x0))}</span>', f'<span class="gx last" style="left:100%">{h(fx(x1))}</span>']
    p = _passo(x1 - x0)
    a = (int(x0) // p + 1) * p
    while a < x1 - p * 0.45:
        if a - x0 > p * 0.45:
            out.append(f'<span class="gx" style="left:{(a - x0) / (x1 - x0) * 100:.1f}%">{a}</span>')
        a += p
    return "".join(out)


def tacche(mn, mx, massimo=5):
    """Tacche tonde (1, 2, 2,5 o 5 × 10^k) da sotto il minimo a sopra il massimo, al massimo `massimo` intervalli."""
    import math
    span = (mx - mn) or abs(mx) or 1
    for base in (1, 2, 2.5, 5, 10):
        passo = base * 10 ** math.floor(math.log10(span / 4))
        a, b = math.floor(mn / passo + 1e-9) * passo, math.ceil(mx / passo - 1e-9) * passo
        if (b - a) / passo <= massimo + 0.0001:
            break
    n = round((b - a) / passo)
    return [round(a + passo * i, 10) for i in range(n + 1)]


def graf_linea(punti, fy, aria, didascalia, fx=lambda x: str(int(x))):
    xs, ys = [p[0] for p in punti], [p[1] for p in punti]
    x0, x1 = xs[0], xs[-1]
    tk = tacche(min(0, min(ys)), max(ys))
    mn, mx = tk[0], tk[-1]
    sx = lambda x: (x - x0) / (x1 - x0) * 1000  # noqa: E731
    sy = lambda v: (1 - (v - mn) / ((mx - mn) or 1)) * 300  # noqa: E731
    d = " ".join(f"{'L' if i else 'M'}{sx(x):.1f} {sy(y):.1f}" for i, (x, y) in enumerate(punti))
    g, lab = "", ""
    for v in tk:
        g += f'<line class="gr" x1="0" x2="1000" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>'
        lab += f'<span class="gy" style="top:{sy(v) / 3:.1f}%">{h(fy(v))}</span>'
    return (f'<figure class="graf" role="img" aria-label="{h(aria)}"><div class="graf-area"><svg viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true">'
            f'{g}<path class="area" d="{d} L1000 300 L0 300 Z"/><path class="lin" d="{d}"/></svg>{lab}{_etichette_x(x0, x1, fx)}</div>'
            f'<figcaption>{didascalia}</figcaption></figure>')


def graf_barre(punti, aria, didascalia, de=False, evid=None):
    """punti: [(anno, frazione)]. Barre sopra lo zero blu, sotto verdi; evid = anno in ambra."""
    n = len(punti)
    tk = tacche(min(0, min(v for _, v in punti)), max(0, max(v for _, v in punti)), 7)
    mn, mx = tk[0], tk[-1]
    sy = lambda v: (1 - (v - mn) / ((mx - mn) or 1)) * 300  # noqa: E731
    w = 1000 / n
    g = ""
    for v in tk:
        g += f'<line class="gr" x1="0" x2="1000" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>'
    for i, (a, v) in enumerate(punti):
        y0, y1 = sy(max(v, 0)), sy(min(v, 0))
        cl = "bh" if a == evid else ("bp" if v >= 0 else "bn")
        g += (f'<rect class="{cl}" x="{i * w + w * 0.12:.2f}" y="{y0:.1f}" width="{w * 0.76:.2f}" height="{max(y1 - y0, 0.8):.1f}">'
              f'<title>{a}: {pct(v, 1, de, segno=False)}</title></rect>')
    g += f'<line class="zero" x1="0" x2="1000" y1="{sy(0):.1f}" y2="{sy(0):.1f}"/>'
    lab = "".join(f'<span class="gy" style="top:{sy(v) / 3:.1f}%">{pct(v, 0 if abs(v * 100 - round(v * 100)) < 1e-9 else 1, de, segno=False)}</span>' for v in tk)
    x0, x1 = punti[0][0], punti[-1][0]
    return (f'<figure class="graf alta" role="img" aria-label="{h(aria)}"><div class="graf-area"><svg viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true">'
            f'{g}</svg>{lab}{_etichette_x(x0, x1, str)}</div><figcaption>{didascalia}</figcaption></figure>')


# ---------------------------------------------------------------- calcolatore
TESTI = {
    "en": {"media_suffix": "(annual average)", "vale": "{importo} in {da} is worth", "in_": "in {a}", "cumulata": "price rise",
           "cumulata_neg": "price fall", "media": "average a year", "inverso": "Put the other way: {importo} in {a} buys what {valore} bought in {da}.",
           "copia": "Copy link to this result", "copiato": "Link copied.", "importo_errato": "Enter an amount, for example 100 or 1,500.",
           "manca": "No index value is published for this date. Choose another month or year.",
           "cambio_serie": "The CPI starts in 1988, so both dates use the RPI long-run series. Results differ from CPI-based calculators (see below).", "grafico_aria": "Value of the amount in each year"},
    "de": {"media_suffix": "(Jahresdurchschnitt)", "vale": "{importo} von {da} entsprechen", "in_": "in Preisen von {a}", "cumulata": "Preisanstieg",
           "cumulata_neg": "Preisrückgang", "media": "pro Jahr im Schnitt",
           "inverso": "Umgekehrt: {importo} von {a} entsprechen {valore} in Preisen von {da}.",
           "copia": "Link zu diesem Ergebnis kopieren", "copiato": "Link kopiert.", "importo_errato": "Bitte einen Betrag eingeben, zum Beispiel 100 oder 1.500.",
           "manca": "Für diesen Zeitpunkt gibt es keinen veröffentlichten Indexwert. Bitte einen anderen Monat oder ein anderes Jahr wählen.",
           "cambio_serie": "", "grafico_aria": "Wert des Betrags in jedem Jahr"},
}


def _etichetta(a, m, lingua):
    return mese_lungo(a, m, lingua) if m else f"{a} {TESTI[lingua]['media_suffix']}"


def risultato_statico(k, importo, da, a, lingua, valuta, dm=None):
    """Lo stesso testo che scrive il JS (senza grafico): il browser lo sostituisce al primo calcolo."""
    T, de = TESTI[lingua], lingua == "de"
    r = M.calcola(C[k], importo, da, a, dm)
    v_in = ("DEM" if dm and da[0] < 2002 else "EUR") if dm is not None else valuta
    v_out = ("DEM" if a[0] < 2002 else "EUR") if dm is not None else valuta
    da_e, a_e = _etichetta(*da, lingua), _etichetta(*a, lingua)
    hh = (f'<div class="ris-main"><span>{h(T["vale"].format(importo=soldi(importo, v_in), da=da_e))}</span><b data-valore>{h(soldi(r["valore"], v_out))}</b>'
          f'<span>{h(T["in_"].format(a=a_e))}</span></div>')
    hh += (f'<ul class="mini"><li><b>{h(pct(r["cumulata"], 1, de))}</b><span>{h(T["cumulata"] if r["cumulata"] >= 0 else T["cumulata_neg"])}</span></li>'
           f'<li><b>{h(pct(r["media"], 2, de)) if r["media"] is not None else "–"}</b><span>{h(T["media"])}</span></li>'
           f'<li><b>{h(idx(r["i0"], de))} → {h(idx(r["i1"], de))}</b><span>{h(NOME_SERIE[k] if k != "de" else "VPI, 2020=100")}</span></li></ul>')
    fs = f"{numero(importo, 2, de)} × {idx(r['i1'], de)} ÷ {idx(r['i0'], de)}"
    if r["fattore_valuta"] != 1:
        fs += (" ÷ " if r["fattore_valuta"] < 1 else " × ") + numero(M.DM_PER_EURO, 5, de)
    hh += f'<p class="formula">{h(fs)} = {h(numero(r["valore"], 2, de))}</p>'
    return hh, r


def calcolatore(paese, titolo, importo, da, a, serie_def=None, pill=""):
    lingua = LINGUA[paese][2]
    de = lingua == "de"
    if paese == "us":
        ids, valuta, locale = ["us"], "USD", "en-US"
    elif paese == "uk":
        ids, valuta, locale = ["uk_cpi", "uk_rpi"], "GBP", "en-GB"
    else:
        ids, valuta, locale = ["de"], "EUR", "de-DE"
    serie_def = serie_def or ids[0]
    dati = {"locale": locale, "valuta": valuta, "dm": paese == "de", "serie_def": serie_def,
            "serie": {k: dict(C[k], nome=NOME_SERIE[k]) for k in ids}, "serie_alt": {"uk_cpi": "uk_rpi"} if paese == "uk" else {},
            "t": dict(TESTI[lingua], mesi=MESI[lingua])}
    if paese == "de":  # prima del 1991 l'indice è il nostro raccordo con la Germania Ovest: lo dice anche accanto al risultato
        dati["avviso"] = {"prima": serie.ANNO_RACCORDO_DE, "testo": "Vor 1991: Index für das frühere Bundesgebiet (Westdeutschland), mit dem VPI verkettet – "
                                                                 "eigene Berechnung, nur eine Näherung (siehe unten)."}
    a0 = min(C[k]["a0"] for k in ids)
    a1 = max(ULT[k][0] for k in ids)
    anni = "".join(f'<option value="{y}"{{sel}}>{y}</option>' for y in range(a0, a1 + 1))

    def sel_anni(y):
        return anni.replace(f'value="{y}"{{sel}}', f'value="{y}" selected').replace("{sel}", "")

    def sel_mesi(m):
        prima = "Jahresdurchschnitt" if de else "Annual average"
        o = f'<option value=""{" selected" if not m else ""}>{prima}</option>'
        o += "".join(f'<option value="{i}"{" selected" if i == m else ""}>{MESI[lingua][i - 1]}</option>' for i in range(1, 13))
        return o
    sym = {"USD": "$", "GBP": "£", "EUR": "DM"}[valuta]
    L = {"importo": "Betrag" if de else "Amount", "da": "Von" if de else "From", "a": "Bis" if de else "To",
         "anno": "Jahr" if de else "Year", "mese": "Monat" if de else "Month"}
    sel_serie = ""
    if paese == "uk":
        sel_serie = (f'<label><span class="lab">Index</span><select name="s"><option value="uk_cpi"{" selected" if serie_def == "uk_cpi" else ""}>CPI (from 1988)</option>'
                     f'<option value="uk_rpi"{" selected" if serie_def == "uk_rpi" else ""}>RPI long-run series (from 1800)</option></select></label>')
    valuta_html = ""
    if paese == "de":
        valuta_html = ('<fieldset data-valuta><legend>Betrag in</legend><div class="radio"><label><input type="radio" name="c" value="dm" checked> D-Mark</label>'
                       '<label><input type="radio" name="c" value="eur"> Euro</label></div></fieldset>')
    campo_cls = "campo dopo" if paese == "de" else "campo"
    stat, _ = risultato_statico(serie_def, importo, da, a, lingua, valuta, (da[0] < 2002) if paese == "de" else None)
    importo_txt = numero(importo, 0, de)
    form = f"""<form class="calc-in" novalidate>
<label><span class="lab">{L['importo']}</span><span class="{campo_cls}" data-sym="{h('DM' if paese == 'de' and da[0] < 2002 else ('€' if paese == 'de' else sym))}"><input type="text" name="a" inputmode="decimal" autocomplete="off" value="{importo_txt}" aria-label="{L['importo']}"></span></label>
{sel_serie}
<fieldset><legend>{L['da']}</legend><div class="calc-2"><select name="fy" aria-label="{L['da']}: {L['anno']}">{sel_anni(da[0])}</select><select name="fm" aria-label="{L['da']}: {L['mese']}">{sel_mesi(da[1])}</select></div></fieldset>
<fieldset><legend>{L['a']}</legend><div class="calc-2"><select name="ty" aria-label="{L['a']}: {L['anno']}">{sel_anni(a[0])}</select><select name="tm" aria-label="{L['a']}: {L['mese']}">{sel_mesi(a[1])}</select></div></fieldset>
{valuta_html}
<p class="nota-calc" data-nota hidden></p>
</form>"""
    js = json.dumps(dati, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<section class="card calc" id="calc" data-calc><div class="calc-h"><h2>{ico("calc")}{h(titolo)}</h2>{pill}</div>'
            f'<div class="calc-g">{form}<div class="calc-out" data-out aria-live="polite">{stat}</div></div>'
            f'</section><script type="application/json" id="calc-dati">{js}</script>')


def jsonld_app(nome, url, lingua):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": nome, "url": url, "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any", "inLanguage": lingua, "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}


# ---------------------------------------------------------------- numeri ricorrenti
def media_annua(k, a0, a1):
    return (val(k, a1) / val(k, a0)) ** (1 / (a1 - a0)) - 1


def tassi_annui(k, a0, a1):
    return [(y, M.tasso_annuo(C[k], y)) for y in range(a0, a1 + 1)]


def ultimo_12_mesi(k):
    """Ultimo mese con variazione sui 12 mesi calcolabile dall'indice (US: ottobre 2025 non raccolto)."""
    a, m = ULT[k]
    while True:
        r = M.tasso_12_mesi(C[k], a, m)
        if r is not None:
            return a, m, r
        m -= 1
        if m == 0:
            a, m = a - 1, 12


US_LU = ULT["us"]
US_ULT_TXT = ult_lungo("us")
US_ULT_BR = mese_breve(*US_LU)
OTT25 = S["us"]["mancanti"]


# ---------------------------------------------------------------- pagine USA
def home():
    a12, m12, r12 = ultimo_12_mesi("us")
    corpo = '<div class="pull">' + calcolatore("us", "US inflation calculator (CPI-U)", 100, (1970, None), US_LU,
                                               pill=f'<span class="pill">Latest: {h(US_ULT_BR)}</span>') + "</div>" + AD
    v1970 = vale_oggi("us", 1970)
    corpo += ('<h2>How the calculator works</h2><div class="testo">'
              f'<p>The calculator multiplies your amount by the ratio of two values of the Consumer Price Index for All Urban Consumers (CPI-U), '
              f'U.S. city average, all items, published by the Bureau of Labor Statistics. Example: $100 in 1970, when the annual average CPI-U was '
              f'{idx(val("us", 1970))}, is worth 100 × {idx(val("us", *US_LU))} ÷ {idx(val("us", 1970))} = <strong>{soldi(100 * v1970, "USD")}</strong> '
              f'in {US_ULT_TXT}.</p>'
              '<p>Choose a year on its own to use that year\'s <strong>annual average</strong>, or pick a month to use the index for that month. The '
              'index is not seasonally adjusted (series CUUR0000SA0, 1982-84=100), which is the version the BLS uses for its own CPI Inflation Calculator '
              'and for annual averages. Monthly values start in January 1913.</p>'
              f'<p>One month is missing: <strong>October 2025</strong>. The BLS footnote reads “{h(list(OTT25.values())[0])}”. The calculator does not '
              'invent a value for that month; choose September or November 2025 instead. The 2025 annual average published by the BLS '
              f'({idx(val("us", 2025))}) is based on the eleven published months.</p></div>')
    corpo += (f'<div class="card stats"><div class="stat main"><b>{pct(r12, 1, segno=False)}</b><span>12-month change to {h(mese_lungo(a12, m12))}</span></div>'
              f'<div class="stat"><b>{pct(M.tasso_annuo(C["us"], 2025), 1, segno=False)}</b><span>inflation in 2025 (annual average)</span></div>'
              f'<div class="stat"><b>{pct(vale_oggi("us", 2000) - 1, 0)}</b><span>prices since 2000</span></div>'
              f'<div class="stat"><b>{pct(media_annua("us", 1913, 2025), 1, segno=False)}</b><span>average a year, 1913–2025</span></div></div>')
    if (a12, m12) != US_LU:
        corpo += (f'<p class="small">The 12-month change for {h(US_ULT_TXT)} cannot be computed from the published index because the October 2025 value '
                  f'was not collected; the figure above is for {h(mese_lungo(a12, m12))}.</p>')
    # dollaro per decennio
    righe = "".join(f'<tr><td><a href="/us/{y}-dollars-today/">{y}</a></td><td class="n">{idx(val("us", y))}</td><td class="n">{soldi(vale_oggi("us", y), "USD")}</td>'
                    f'<td class="n">{soldi(100 * vale_oggi("us", y), "USD")}</td></tr>' for y in range(1920, 2021, 10))
    corpo += (f'<h2 id="years">What a dollar from each decade is worth today</h2><p>Value in {h(US_ULT_TXT)} of money from the start of each decade '
              '(annual average CPI-U). Every year from 1913 has its own page with a table, a chart and that year\'s inflation rate.</p>'
              f'<div class="tab"><table class="dati"><thead><tr><th scope="col">Year</th><th scope="col" class="n">CPI-U</th><th scope="col" class="n">$1 is worth today</th>'
              f'<th scope="col" class="n">$100 is worth today</th></tr></thead><tbody>{righe}</tbody></table></div>')
    corpo += griglia_anni()
    corpo += (f'<h2>{"Other countries and tables" if SEZIONE_DE else "UK calculator and more tables"}</h2><ul class="griglia">'
              '<li><a href="/uk/"><b>UK</b>Inflation calculator<small>ONS CPI from 1988 and the RPI long-run series from 1800</small></a></li>'
              + ('<li><a href="/de/inflationsrechner/"><b>DE</b>Inflationsrechner<small>Destatis-VPI, D-Mark und Euro, ab 1962</small></a></li>' if SEZIONE_DE else "") +
              '<li><a href="/us/inflation-rate-by-year/"><b>%</b>US inflation rate by year<small>Every year since 1914, annual average and December to December</small></a></li>'
              '<li><a href="/uk/rpi-calculator/"><b>RPI</b>RPI calculator<small>Retail Prices Index increases since 1800</small></a></li></ul>')
    m2000 = media_annua("us", 2000, 2025)
    faq, ld_faq = faq_blocco("home", [
        ("What is the normal inflation rate?",
         ('There is no single normal rate. The Federal Reserve judges that inflation of 2 percent over the longer run, measured by the price index for '
          f'personal consumption expenditures (PCE), is most consistent with its mandate. The CPI-U used here is a different index: from 2000 to 2025 it rose '
          f'on average {pct(m2000, 1, segno=False)} a year.'), "normal inflation rate", "us"),
        ("What is the average inflation rate in the US?",
         (f'Measured with the annual average CPI-U, prices rose on average {pct(media_annua("us", 1913, 2025), 1, segno=False)} a year from 1913 to 2025, '
          f'{pct(media_annua("us", 1995, 2025), 1, segno=False)} a year over the 30 years from 1995 to 2025 and {pct(media_annua("us", 2015, 2025), 1, segno=False)} '
          'a year over the 10 years from 2015 to 2025.'), "average inflation rate", "us"),
        ("How do you adjust an amount for inflation?",
         ('Multiply the amount by the price index of the later date and divide by the index of the earlier date. With the CPI-U, $50 in 2000 (index '
          f'{idx(val("us", 2000))}) becomes 50 × {idx(val("us", 2025))} ÷ {idx(val("us", 2000))} = {soldi(50 * val("us", 2025) / val("us", 2000), "USD")} '
          'in 2025 dollars. The calculator above does the same with any month or year.'), "adjusting for inflation calculator", "us"),
    ])
    corpo += faq + fonti_box(["bls_cpiu", "bls_calc", "fed_target"])
    testata = banda("US · UK · Germany" if SEZIONE_DE else "US & UK", "Inflation calculator: what is your money worth today?",
                    f"Convert any amount between years with the official consumer price index: CPI-U for the US (to <strong>{h(US_ULT_TXT)}</strong>), "
                    + ("plus the ONS indexes for the UK and the Destatis VPI for Germany." if SEZIONE_DE else "plus the ONS CPI and RPI for the UK."),
                    trust([("check", "Official BLS, ONS and Destatis indexes" if SEZIONE_DE else "Official BLS and ONS indexes"),
                           ("calendar", "Updated every month"), ("lock", "Runs in your browser")]))
    pagina("", f"Inflation Calculator: US Dollar Value 1913–{US_LU[0]} (CPI)",
           f"Free inflation calculator with the official BLS CPI-U from 1913 to {US_ULT_TXT}: see what a past amount is worth today, with the formula. "
           + ("UK and Germany too." if SEZIONE_DE else "UK too."),
           corpo, testata, "us", jsonld=[jsonld_app("US inflation calculator", URL_SITO + "/", "en-US")] + ([ld_faq] if ld_faq else []))


def griglia_anni(attuale=None):
    out = '<div class="decade-box">'
    for d in range(1910, ULTIMO_ANNO_US + 1, 10):
        anni = [y for y in range(d, d + 10) if y in ANNI_US]
        out += (f'<div class="decade"><h3>{d}s</h3><ul class="anni">' +
                "".join(f'<li><a href="/us/{y}-dollars-today/"' + (' aria-current="page"' if y == attuale else "") + f">{y}</a></li>" for y in anni) + "</ul></div>")
    return out + "</div>"


def tasso_rank(y):
    t = [(a, M.tasso_annuo(C["us"], a)) for a in ANNI_US[1:]]
    ordinati = sorted(t, key=lambda x: -x[1])
    return [a for a, _ in ordinati].index(y) + 1, len(t)


def ordinale(n):
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


FAQ_ANNI = {
    1950: ("How much was 1 dollar worth in 1950?", "how much was 1 dollar worth in 1950"),
    1960: ("What was the dollar worth in 1960?", "what was the dollar worth in 1960"),
    1970: ("How much was a dollar worth in 1970?", "how much was a dollar worth in 1970"),
    1980: ("What was the inflation rate in 1980?", "what was the inflation rate in 1980"),
}


def pagina_anno(y):
    i_y = val("us", y)
    r = vale_oggi("us", y)
    t_y = M.tasso_annuo(C["us"], y)
    t_dic = M.tasso_dicembre(C["us"], y)
    importi = [1, 5, 10, 20, 50, 100, 500, 1000, 10000]
    righe = "".join(f'<tr><td class="n">{soldi(x, "USD", 0)}</td><td class="n">{soldi(x * r, "USD")}</td></tr>' for x in importi)
    risposta = (f'<div class="card risposta pull"><p>$1 in {y} has the same buying power as<span class="big">{soldi(r, "USD")}</span>'
                f'in {h(US_ULT_TXT)}. Prices are <strong>{pct(r - 1, 0, segno=False)}</strong> higher than the {y} average'
                + (f', and inflation in {y} itself was <strong>{pct(t_y, 1, segno=False) if t_y >= 0 else pct(t_y, 1)}</strong>.' if t_y is not None else ".")
                + f'</p><p class="small">Official CPI-U (BLS): {y} annual average {idx(i_y)}; {h(US_ULT_TXT)} {idx(val("us", *US_LU))}.</p></div>')
    corpo = risposta
    # precisione e anni con la stessa media annua (dati veri della serie, diversi per ogni anno)
    note_anno = ""
    if cifre(i_y) == 1 and 0.05 / i_y >= 0.002:
        note_anno += (f'<p>The BLS publishes the {y} index to one decimal place ({idx(i_y)}), so amounts converted from {y} are accurate to about '
                      f'±{pct(0.05 / i_y, 1, segno=False)}: {soldi(100 * r, "USD")} for $100 could be up to {soldi(100 * r * 0.05 / i_y, "USD")} higher or lower.</p>')
    gemelli = [a for a in ANNI_US if a != y and val("us", a) == i_y]
    if gemelli:
        ll = [f'<a href="/us/{a}-dollars-today/">{a}</a>' for a in gemelli]
        elenco = ll[0] if len(ll) == 1 else ", ".join(ll[:-1]) + " and " + ll[-1]
        note_anno += (f'<p>The annual average CPI-U was also {idx(i_y)} in {elenco}, so the annual-average amounts for {"that year" if len(gemelli) == 1 else "those years"} '
                      f'are the same as for {y}. The months were different: see the monthly table below.</p>')
    corpo += (f'<h2>{y} dollars in today\'s money</h2><div class="cols"><div class="tab"><table class="dati"><thead><tr><th scope="col" class="n">In {y}</th>'
              f'<th scope="col" class="n">In {h(US_ULT_BR)}</th></tr></thead><tbody>{righe}</tbody></table></div><div class="testo">'
              f'<p>Each row multiplies the {y} amount by {idx(val("us", *US_LU))} ÷ {idx(i_y)} = {numero(r, 4)}. The other way round, '
              f'$100 in {h(US_ULT_TXT)} buys what {soldi(100 / r, "USD")} bought in {y}.</p>'
              f'{note_anno}<p><a class="btn" href="/?a=100&amp;f={y}#calc">{ico("calc")}Any amount or month from {y}</a></p></div></div>')
    corpo += AD
    # grafico
    punti = [(a, val("us", a) / i_y) for a in range(y, ULTIMO_ANNO_US + 1)]
    punti.append((US_LU[0] + (US_LU[1] - 0.5) / 12, r))
    if len(punti) >= 3:
        corpo += (f'<h2>How $1 from {y} grew with prices</h2>' +
                  graf_linea(punti, lambda v: soldi(v, "USD", 0 if v >= 10 else 2), f"Value of $1 from {y} in each later year",
                             f'Dollars needed in each year to match $1 of {y} (annual average CPI-U; last point {h(US_ULT_TXT)}).'))
    later = [a for a in range((y // 10 + 1) * 10, ULTIMO_ANNO_US + 1, 10)] + ([ULTIMO_ANNO_US] if ULTIMO_ANNO_US % 10 else [])
    if later:
        corpo += ('<div class="tab"><table class="dati"><thead><tr><th scope="col">Year</th><th scope="col" class="n">CPI-U</th>'
                  f'<th scope="col" class="n">$1 from {y} is worth</th><th scope="col" class="n">Change since {y}</th></tr></thead><tbody>' +
                  "".join(f'<tr><td><a href="/us/{a}-dollars-today/">{a}</a></td><td class="n">{idx(val("us", a))}</td>'
                          f'<td class="n">{soldi(val("us", a) / i_y, "USD")}</td><td class="n">{pct(val("us", a) / i_y - 1, 1)}</td></tr>' for a in later) +
                  "</tbody></table></div>")
    # inflazione dell'anno
    corpo += f'<h2>Inflation in {y}</h2><div class="testo">'
    if t_y is not None:
        rank, n = tasso_rank(y)
        corpo += (f'<p>The annual average CPI-U went from {idx(val("us", y - 1))} in {y - 1} to {idx(i_y)} in {y}: a change of '
                  f'<strong>{pct(t_y, 1)}</strong>. '
                  + (f'From December {y - 1} to December {y} prices changed {pct(t_dic, 1)}. ' if t_dic is not None else "")
                  + f'Among the {n} years from 1914 to {ULTIMO_ANNO_US}, {y} had the {ordinale(rank)} highest annual inflation rate.</p>')
    else:
        corpo += f'<p>{y} is the first year of the CPI-U, so there is no earlier year to compare it with.</p>'
    corpo += (f'<p>Average inflation from {y} to {ULTIMO_ANNO_US}: {pct(media_annua("us", y, ULTIMO_ANNO_US), 2, segno=False)} a year.</p></div>'
              if y < ULTIMO_ANNO_US else "</div>")
    mesi_r = ""
    for m in range(1, 13):
        v = val("us", y, m)
        t12 = M.tasso_12_mesi(C["us"], y, m)
        mesi_r += (f'<tr><td>{MESI["en"][m - 1]}</td><td class="n">{idx(v) if v else "–"}</td>'
                   f'<td class="n">{pct(t12, 1) if t12 is not None else "–"}</td>'
                   f'<td class="n">{soldi(100 * val("us", *US_LU) / v, "USD") if v else "–"}</td></tr>')
    vm = {m: val("us", y, m) for m in range(1, 13) if val("us", y, m)}
    v_min, v_max = min(vm.values()), max(vm.values())

    def _quali(v):
        ms = [MESI["en"][m - 1] for m in vm if vm[m] == v]
        return ", ".join(ms) if len(ms) <= 3 else f"{len(ms)} months"
    estremi = (f'. Lowest monthly index of {y}: {idx(v_min)} ({_quali(v_min)}); highest: {idx(v_max)} ({_quali(v_max)}).'
               if v_min != v_max else f'. The index was {idx(v_min)} in every published month of {y}.')
    nota_mesi = ""
    if any(k[0] in (y, y + 1) for k in OTT25):
        nota_mesi = f'<p class="small">October 2025: {h(list(OTT25.values())[0])} (BLS).</p>'
    corpo += (f'<h3>Monthly CPI-U in {y}</h3><div class="tab"><table class="dati"><thead><tr><th scope="col">Month</th><th scope="col" class="n">CPI-U</th>'
              f'<th scope="col" class="n">12-month change</th><th scope="col" class="n">$100 from that month in {h(US_ULT_BR)}</th></tr></thead>'
              f'<tbody>{mesi_r}</tbody></table></div>{nota_mesi}'
              f'<p class="small">12-month changes and the value of $100 are calculated here from the published monthly index (not seasonally adjusted){estremi}</p>')
    if y in FAQ_ANNI:
        q, frase = FAQ_ANNI[y]
        if y == 1980:
            a_txt = (f'Measured with the annual average CPI-U, inflation in 1980 was {pct(t_y, 1, segno=False)}: the index rose from {idx(val("us", 1979))} '
                     f'in 1979 to {idx(i_y)} in 1980. From December 1979 to December 1980 the rise was {pct(t_dic, 1, segno=False)}.')
        else:
            a_txt = (f'A dollar from {y} had the buying power of {soldi(r, "USD")} in {US_ULT_TXT}, based on the official CPI-U ({idx(i_y)} for {y}, '
                     f'{idx(val("us", *US_LU))} for {US_ULT_TXT}). Put the other way, a dollar today buys what {soldi(1 / r, "USD")} bought in {y}.')
        faq, ld_faq = faq_blocco(f"us-{y}", [(q, h(a_txt), frase, "us")])
    else:
        faq, ld_faq = "", None
    corpo += faq
    vic = ""
    if y - 1 in ANNI_US:
        vic += f'<a class="btn sec" href="/us/{y - 1}-dollars-today/">← {y - 1} dollars</a>'
    if y + 1 in ANNI_US:
        vic += f'<a class="btn sec" href="/us/{y + 1}-dollars-today/">{y + 1} dollars →</a>'
    corpo += f'<div class="vicini">{vic}</div><h2>Other years</h2>' + griglia_anni(y)
    if y in DECENNI_IMPORTO:
        corpo += ('<p>' + " · ".join(f'<a href="/us/{x}-dollars-in-{y}/">${x:,} in {y}</a>' for x in IMPORTI_PAGINA) + "</p>")
    corpo += fonti_box(["bls_cpiu"])
    testata = banda("Value of a dollar", f"What is a {y} dollar worth today?",
                    f"$1 from {y} = <strong>{soldi(r, 'USD')}</strong> in {h(US_ULT_TXT)}, with the official CPI-U of the US Bureau of Labor Statistics.",
                    corta=True, icona="coins")
    tit = f"{y} Dollars Today: $1 Is Worth {soldi(r, 'USD')} in {US_ULT_BR}"
    descr = (f"$1 from {y} has the buying power of {soldi(r, 'USD')} in {US_ULT_TXT} (official CPI-U). "
             + (f"Inflation in {y}: {pct(t_y, 1, segno=False) if t_y >= 0 else pct(t_y, 1)}. " if t_y is not None else "")
             + "Table from $1 to $10,000, chart and monthly CPI.")
    pagina(f"us/{y}-dollars-today/", tit, descr, corpo, testata, "us",
           briciole=[("Home", ""), ("US inflation rate by year", "us/inflation-rate-by-year/"), (f"{y} dollars today", f"us/{y}-dollars-today/")],
           jsonld=[ld_faq] if ld_faq else None)


FAQ_IMPORTI = {(100, 1970): ("How much was 100 dollars worth in 1970?", "how much was 100 dollars worth in 1970"),
               (1000, 1980): ("How much was 1000 dollars worth in 1980?", "how much was 1000 dollars worth in 1980")}


def pagina_importo(x, y):
    i_y = val("us", y)
    r = vale_oggi("us", y)
    corpo = (f'<div class="card risposta pull"><p>{soldi(x, "USD", 0)} in {y} has the same buying power as<span class="big">{soldi(x * r, "USD")}</span>'
             f'in {h(US_ULT_TXT)}, using the official CPI-U ({idx(i_y)} in {y}, {idx(val("us", *US_LU))} in {h(US_ULT_TXT)}).</p>'
             f'<p class="formula">{numero(x, 2)} × {idx(val("us", *US_LU))} ÷ {idx(i_y)} = {numero(x * r, 2)}</p></div>')
    corpo += AD
    punti = [(a, x * val("us", a) / i_y) for a in range(y, ULTIMO_ANNO_US + 1)] + [(US_LU[0] + (US_LU[1] - 0.5) / 12, x * r)]
    corpo += (f'<h2>{soldi(x, "USD", 0)} from {y}, year by year</h2>' +
              graf_linea(punti, lambda v: soldi(v, "USD", 0), f"Value of ${x:,} from {y} in each later year",
                         f'Dollars needed in each year to match {soldi(x, "USD", 0)} of {y} (annual average CPI-U; last point {h(US_ULT_TXT)}).'))
    righe = ""
    for a in range(y, ULTIMO_ANNO_US + 1):
        v = val("us", a)
        righe += (f'<tr><td><a href="/us/{a}-dollars-today/">{a}</a></td><td class="n">{idx(v)}</td><td class="n">{soldi(x * v / i_y, "USD")}</td>'
                  f'<td class="n">{pct(M.tasso_annuo(C["us"], a), 1) if a > 1913 else "–"}</td></tr>')
    righe += (f'<tr class="evid"><td>{h(US_ULT_TXT)}</td><td class="n">{idx(val("us", *US_LU))}</td><td class="n">{soldi(x * r, "USD")}</td><td class="n">–</td></tr>')
    corpo += (f'<div class="tab alta"><table class="dati"><thead><tr><th scope="col">Year</th><th scope="col" class="n">CPI-U (annual average)</th>'
              f'<th scope="col" class="n">{soldi(x, "USD", 0)} from {y} =</th><th scope="col" class="n">Inflation that year</th></tr></thead><tbody>{righe}</tbody></table></div>')
    corpo += (f'<h2>The other way: today\'s money in {y} dollars</h2><div class="testo"><p>{soldi(x, "USD", 0)} in {h(US_ULT_TXT)} buys what '
              f'{soldi(x / r, "USD")} bought in {y}. Prices have risen {pct(r - 1, 0, segno=False)} since then, an average of '
              f'{pct(media_annua("us", y, ULTIMO_ANNO_US), 2, segno=False)} a year from {y} to {ULTIMO_ANNO_US}.</p>'
              f'<p><a class="btn" href="/?a={x}&amp;f={y}#calc">{ico("calc")}Change the amount, year or month</a></p></div>')
    altri = "".join(f'<li><a href="/us/{x}-dollars-in-{d}/"><b>{d}</b>{soldi(x, "USD", 0)} → {soldi(x * vale_oggi("us", d), "USD", 0)}</a></li>'
                    for d in DECENNI_IMPORTO if d != y)
    corpo += f'<h2>{soldi(x, "USD", 0)} from other decades</h2><ul class="griglia">{altri}</ul>'
    altro_importo = [z for z in IMPORTI_PAGINA if z != x][0]
    corpo += (f'<p>See also <a href="/us/{altro_importo}-dollars-in-{y}/">{soldi(altro_importo, "USD", 0)} in {y}</a> and '
              f'<a href="/us/{y}-dollars-today/">the {y} dollar page</a> (all amounts, monthly CPI and the {y} inflation rate).</p>')
    faq, ld_faq = "", None
    if (x, y) in FAQ_IMPORTI:
        q, frase = FAQ_IMPORTI[(x, y)]
        faq, ld_faq = faq_blocco(f"us-{x}-{y}", [(q, h(f'{soldi(x, "USD", 0)} in {y} was worth what {soldi(x * r, "USD")} is worth in {US_ULT_TXT}, '
                                                       f'according to the official CPI-U of the Bureau of Labor Statistics ({idx(i_y)} in {y}, '
                                                       f'{idx(val("us", *US_LU))} in {US_ULT_TXT}).'), frase, "us")])
    corpo += faq + fonti_box(["bls_cpiu"])
    testata = banda("Value of money", f"How much is {soldi(x, 'USD', 0)} from {y} worth today?",
                    f"{soldi(x, 'USD', 0)} in {y} = <strong>{soldi(x * r, 'USD')}</strong> in {h(US_ULT_TXT)} (official CPI-U).", corta=True, icona="coins")
    pagina(f"us/{x}-dollars-in-{y}/", f"${x:,} in {y} Is Worth {soldi(x * r, 'USD', 0)} Today ({US_ULT_BR} CPI)",
           f"${x:,} in {y} equals {soldi(x * r, 'USD')} in {US_ULT_TXT} with the official BLS CPI-U. Year-by-year table, chart and the formula.",
           corpo, testata, "us", briciole=[("Home", ""), (f"{y} dollars today", f"us/{y}-dollars-today/"), (f"${x:,} in {y}", f"us/{x}-dollars-in-{y}/")],
           jsonld=[ld_faq] if ld_faq else None)


def us_tassi():
    tassi = tassi_annui("us", 1914, ULTIMO_ANNO_US)
    t25 = dict(tassi)[ULTIMO_ANNO_US]
    a12, m12, r12 = ultimo_12_mesi("us")
    corpo = (f'<div class="card risposta pull"><p>US inflation in {ULTIMO_ANNO_US} was<span class="big">{pct(t25, 1, segno=False)}</span>'
             f'measured with the annual average CPI-U. The latest 12-month change that the published index allows is <strong>{pct(r12, 1, segno=False)}</strong> '
             f'({h(mese_lungo(a12, m12))}).</p></div>')
    alto = max(tassi, key=lambda x: x[1])
    basso = min(tassi, key=lambda x: x[1])
    corpo += graf_barre(tassi, "US inflation rate by year, 1914 to " + str(ULTIMO_ANNO_US),
                        f'Annual average change of the CPI-U. Highest: {alto[0]} ({pct(alto[1], 1)}); lowest: {basso[0]} ({pct(basso[1], 1)}).')
    corpo += AD
    corpo += ('<h2>Two ways to measure a year\'s inflation</h2><div class="testo"><p><strong>Annual average change</strong> compares the average index of '
              'the whole year with the average of the year before. <strong>December to December</strong> compares the last month of each year. Both are '
              'calculated here from the official CPI-U published by the Bureau of Labor Statistics (not seasonally adjusted, 1982-84=100).</p></div>')
    righe = ""
    for y, t in reversed(tassi):
        td = M.tasso_dicembre(C["us"], y)
        righe += (f'<tr><td><a href="/us/{y}-dollars-today/">{y}</a></td><td class="n">{idx(val("us", y))}</td><td class="n">{pct(t, 1)}</td>'
                  f'<td class="n">{pct(td, 1) if td is not None else "–"}</td><td class="n">{soldi(vale_oggi("us", y), "USD")}</td></tr>')
    corpo += (f'<h2>US inflation rate by year, 1914–{ULTIMO_ANNO_US}</h2><div class="tab alta"><table class="dati"><thead><tr><th scope="col">Year</th>'
              '<th scope="col" class="n">CPI-U (annual average)</th><th scope="col" class="n">Annual average change</th><th scope="col" class="n">Dec to Dec</th>'
              f'<th scope="col" class="n">$1 then is worth in {h(US_ULT_BR)}</th></tr></thead><tbody>{righe}</tbody></table></div>'
              '<p class="small">The December 2024 to December 2025 comparison uses the published December values; October 2025 was not collected by the BLS.</p>')
    mesi_r = ""
    for m in range(1, US_LU[1] + 1):
        t12 = M.tasso_12_mesi(C["us"], US_LU[0], m)
        mesi_r += f'<tr><td>{MESI["en"][m - 1]} {US_LU[0]}</td><td class="n">{idx(val("us", US_LU[0], m))}</td><td class="n">{pct(t12, 1) if t12 is not None else "– (October 2025 not collected)"}</td></tr>'
    corpo += (f'<h2>{US_LU[0]} so far, month by month</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Month</th><th scope="col" class="n">CPI-U</th>'
              f'<th scope="col" class="n">12-month change</th></tr></thead><tbody>{mesi_r}</tbody></table></div>')
    decenni = "".join(f'<tr><td>{d}s</td><td class="n">{pct(media_annua("us", d - 1 if d > 1913 else 1913, min(d + 9, ULTIMO_ANNO_US)), 1)}</td></tr>'
                      for d in range(1920, ULTIMO_ANNO_US + 1, 10))
    corpo += (f'<h2>Average inflation by decade</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Decade</th><th scope="col" class="n">Average a year</th>'
              f'</tr></thead><tbody>{decenni}</tbody></table></div><p class="small">From the annual average of the year before the decade to the last year of the decade '
              f'(2020s: to {ULTIMO_ANNO_US}).</p>')
    faq, ld_faq = faq_blocco("us-rates", [
        ("What is the annual inflation rate?",
         h(f'It is the change in prices over a year. With the CPI-U, the annual average for {ULTIMO_ANNO_US} was {idx(val("us", ULTIMO_ANNO_US))} against '
           f'{idx(val("us", ULTIMO_ANNO_US - 1))} in {ULTIMO_ANNO_US - 1}, an annual inflation rate of {pct(t25, 1, segno=False)}. Over the 12 months to '
           f'{mese_lungo(a12, m12)} the index rose {pct(r12, 1, segno=False)}.'), "annual inflation rate", "us")])
    corpo += faq + fonti_box(["bls_cpiu"])
    testata = banda("United States · CPI-U", f"US inflation rate by year (1914–{ULTIMO_ANNO_US})",
                    "Every year's inflation from the official Consumer Price Index of the Bureau of Labor Statistics, with the value of a dollar from each year today.",
                    corta=True, icona="trend")
    pagina("us/inflation-rate-by-year/", f"US Inflation Rate by Year 1914–{ULTIMO_ANNO_US} (CPI-U Table)",
           f"US inflation rate for every year since 1914 from the official BLS CPI-U: annual average and December-to-December changes, chart, {US_LU[0]} months.",
           corpo, testata, "us", briciole=[("Home", ""), ("US inflation rate by year", "us/inflation-rate-by-year/")], jsonld=[ld_faq] if ld_faq else None)


# ---------------------------------------------------------------- Regno Unito
UK_LU = ULT["uk_cpi"]
UK_ULT_TXT = ult_lungo("uk_cpi")
CPI_RATE = S["uk_cpi_rate"]
RPI_RATE = S["uk_rpi_rate"]
BOE = (23, 1975, 1985, 17.78, 44.6, 57.68)  # esempio scritto nella pagina del calcolatore della Banca d'Inghilterra (frasi controllate in fonti.json: boe_calc)


def tasso_rpi(y):
    """(tasso, pubblicato): tasso annuo RPI pubblicato dall'ONS (serie CZBH, dal 1949); prima, calcolato dall'indice lungo CDKO."""
    v = RPI_RATE["annuale"].get(y)
    return (v / 100, True) if v is not None else (M.tasso_annuo(C["uk_rpi"], y), False)


def uk_spiega():
    return ('<h2>CPI or RPI?</h2><div class="testo">'
            f'<p>The <strong>CPI</strong> (Consumer Prices Index, series D7BT, 2015=100) is the UK\'s headline measure of inflation. The ONS publishes it '
            f'monthly from January 1988; the latest value is {idx(val("uk_cpi", *UK_LU))} for {h(UK_ULT_TXT)}.</p>'
            f'<p>For earlier years the calculator uses the ONS <strong>Retail Prices Index long-run series</strong> (series CDKO, January 1974=100). It has an '
            f'annual value for every year from 1800 and monthly values from June 1947, so it can answer questions such as the value of £1 in 1950.</p>'
            '<p>The two indexes measure prices differently and the RPI has usually risen faster, so the calculator never mixes them in one calculation: '
            'it uses the CPI when both dates are from 1988 on (unless you choose the RPI) and the RPI long-run series for <em>both</em> dates otherwise. '
            'No CPI value is linked to an RPI value.</p>'
            '<p>Choose a year on its own to use that year\'s <strong>annual average</strong> index, or pick a month to use the index of that month.</p>'
            '<h3 id="boe">Why results before 1988 differ from the Bank of England calculator</h3>'
            '<p>The Bank of England\'s inflation calculator also uses the ONS CPI from 1988, but for earlier years it uses CPI estimates that, in its words, '
            '“are modelled based on data collected for the Retail Price Index (RPI)”. This site uses the published RPI long-run series itself for those '
            f'years, and the RPI rose faster. Example from the Bank\'s page: £{BOE[0]} in {BOE[1]} becomes {soldi(BOE[5], "GBP")} in {BOE[2]} (its price indexes: '
            f'{BOE[3]} and {BOE[4]}). With the RPI long-run series ({idx(val("uk_rpi", BOE[1]))} and {idx(val("uk_rpi", BOE[2]))}) the same £{BOE[0]} becomes '
            f'{soldi(BOE[0] * val("uk_rpi", BOE[2]) / val("uk_rpi", BOE[1]), "GBP")}. The two answers use different indexes, so for dates before 1988 '
            'expect a higher figure here than at the Bank of England.</p></div>')


def uk_calc():
    a12 = CPI_RATE["mensile"][UK_LU]
    corpo = '<div class="pull">' + calcolatore("uk", "UK inflation calculator", 100, (1990, None), UK_LU,
                                               pill=f'<span class="pill">Latest: {h(mese_breve(*UK_LU))}</span>') + "</div>" + AD
    corpo += (f'<div class="card stats"><div class="stat main"><b>{pct(a12 / 100, 1, segno=False)}</b><span>CPI 12-month rate, {h(UK_ULT_TXT)} (ONS)</span></div>'
              f'<div class="stat"><b>{pct(CPI_RATE["annuale"][2025] / 100, 1, segno=False)}</b><span>CPI inflation in 2025 (ONS)</span></div>'
              f'<div class="stat"><b>{pct(vale_oggi("uk_cpi", 2000) - 1, 0)}</b><span>CPI prices since 2000</span></div>'
              f'<div class="stat"><b>{pct(vale_oggi("uk_rpi", 1950) - 1, 0)}</b><span>RPI prices since 1950</span></div></div>')
    corpo += uk_spiega()
    righe = ""
    for y in (1900, 1920, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020):
        cpi = soldi(100 * vale_oggi("uk_cpi", y), "GBP") if y >= 1988 else "–"
        righe += f'<tr><td>{y}</td><td class="n">{cpi}</td><td class="n">{soldi(100 * vale_oggi("uk_rpi", y), "GBP")}</td></tr>'
    corpo += (f'<h2>What £100 from past years is worth today</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Year (annual average)</th>'
              f'<th scope="col" class="n">With CPI, {h(mese_breve(*UK_LU))}</th><th scope="col" class="n">With RPI long-run, {h(mese_breve(*ULT["uk_rpi"]))}</th></tr></thead>'
              f'<tbody>{righe}</tbody></table></div><p class="small">Formula: £100 × index of {h(UK_ULT_TXT)} ÷ annual average index of the year.</p>')
    corpo += ('<ul class="griglia"><li><a href="/uk/inflation-rate-by-year/"><b>%</b>UK inflation rate by year<small>CPI since 1989, RPI since 1801</small></a></li>'
              '<li><a href="/uk/rpi-calculator/"><b>RPI</b>RPI calculator<small>Increases by the Retail Prices Index</small></a></li>'
              '<li><a href="/"><b>US</b>US inflation calculator<small>BLS CPI-U from 1913</small></a></li>'
              + ('<li><a href="/de/inflationsrechner/"><b>DE</b>Inflationsrechner<small>Destatis-VPI, D-Mark und Euro</small></a></li>' if SEZIONE_DE else "")
              + '</ul>')
    faq, ld_faq = faq_blocco("uk", [
        ("Can I use the inflation calculator for a salary?",
         h(f'Yes: enter the pay and the year it was paid. The result is the pay needed in {UK_ULT_TXT} to buy the same as before, measured with the CPI '
           f'(or, when a date is before 1988, with the RPI long-run series). For example £25,000 in 2015 corresponds to {soldi(25000 * vale_oggi("uk_cpi", 2015), "GBP", 0)} with the CPI. '
           'It does not show what pay rises were actually agreed or what any employer must pay.'), "uk inflation calculator salary", "gb"),
        ("What is the current UK CPI?",
         h(f'The ONS CPI index (2015=100) was {idx(val("uk_cpi", *UK_LU))} in {UK_ULT_TXT}, {pct(a12 / 100, 1, segno=False)} higher than a year earlier. '
           f'The next figures are due on {FONTI["ons_d7bt"].get("prossima_uscita") or "the date shown by the ONS"}.'), "current uk cpi", "gb"),
    ])
    corpo += faq + fonti_box(["ons_d7bt", "ons_cdko", "ons_d7g7", "boe_calc"])
    testata = banda("United Kingdom · ONS", "UK inflation calculator (CPI and RPI)",
                    f"What money from any year since 1800 is worth today, with the official ONS Consumer Prices Index and the Retail Prices Index long-run series (to <strong>{h(UK_ULT_TXT)}</strong>).",
                    trust([("check", "Official ONS indexes"), ("calendar", "Updated every month"), ("lock", "Runs in your browser")]))
    pagina("uk/", "UK Inflation Calculator: Value of £ from 1800 to Today (ONS)",
           f"Free UK inflation calculator with the official ONS CPI (from 1988) and RPI long-run series (from 1800), updated to {UK_ULT_TXT}. Formula and sources shown.",
           corpo, testata, "uk", briciole=[("Home", ""), ("UK inflation calculator", "uk/")],
           jsonld=[jsonld_app("UK inflation calculator", URL_SITO + "/uk/", "en-GB")] + ([ld_faq] if ld_faq else []))


def uk_tassi():
    cpi = [(y, CPI_RATE["annuale"][y] / 100) for y in sorted(CPI_RATE["annuale"])]
    rpi = [(y, tasso_rpi(y)[0]) for y in range(1801, max(S["uk_rpi"]["annuale"]) + 1)]
    rpi_dal = min(RPI_RATE["annuale"])
    ultimi = [(y, v) for y, v in cpi if y > cpi[-1][0] - 10]
    corpo = (f'<div class="card risposta pull"><p>UK CPI inflation in {cpi[-1][0]} was<span class="big">{pct(cpi[-1][1], 1, segno=False)}</span>'
             f'according to the ONS; the 12-month rate for {h(UK_ULT_TXT)} is <strong>{pct(CPI_RATE["mensile"][UK_LU] / 100, 1, segno=False)}</strong>.</p></div>')
    corpo += graf_barre(cpi, f"UK CPI inflation rate by year, {cpi[0][0]} to {cpi[-1][0]}", "CPI annual rate published by the ONS (series D7G7).")
    corpo += AD
    righe = "".join(f'<tr><td>{y}</td><td class="n">{idx(val("uk_cpi", y))}</td><td class="n">{pct(v, 1)}</td><td class="n">{soldi(vale_oggi("uk_cpi", y), "GBP")}</td></tr>'
                    for y, v in reversed(cpi))
    corpo += (f'<h2>UK CPI inflation rate by year, {cpi[0][0]}–{cpi[-1][0]}</h2><div class="tab alta"><table class="dati"><thead><tr><th scope="col">Year</th>'
              '<th scope="col" class="n">CPI (annual average, 2015=100)</th><th scope="col" class="n">Annual rate (ONS)</th>'
              f'<th scope="col" class="n">£1 then is worth in {h(mese_breve(*UK_LU))}</th></tr></thead><tbody>{righe}</tbody></table></div>')
    mesi = sorted(k for k in CPI_RATE["mensile"] if k > (UK_LU[0] - 1, UK_LU[1]))
    righe = "".join(f'<tr><td>{mese_lungo(a, m)}</td><td class="n">{idx(val("uk_cpi", a, m))}</td><td class="n">{pct(CPI_RATE["mensile"][(a, m)] / 100, 1)}</td></tr>'
                    for a, m in reversed(mesi))
    corpo += (f'<h2>The last 12 months</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Month</th><th scope="col" class="n">CPI</th>'
              f'<th scope="col" class="n">12-month rate (ONS)</th></tr></thead><tbody>{righe}</tbody></table></div>')
    rpi_vis = [p for p in rpi if p[0] >= 1900]
    corpo += (f'<h2>RPI long-run series: inflation since 1801</h2>' +
              graf_barre(rpi_vis, "UK RPI long-run inflation by year since 1900",
                         f'RPI annual rate: published by the ONS from {rpi_dal} (series CZBH); earlier years calculated here from the RPI long-run index (series CDKO). 1900 onwards shown.'))
    righe = "".join(f'<tr><td>{y}</td><td class="n">{idx(val("uk_rpi", y))}</td><td class="n">{pct(v, 1)}{"" if y >= rpi_dal else " *"}</td></tr>' for y, v in reversed(rpi))
    corpo += (f'<details><summary>Show all years 1801–{rpi[-1][0]}</summary><div class="tab alta"><table class="dati"><thead><tr><th scope="col">Year</th>'
              f'<th scope="col" class="n">RPI long-run (Jan 1974=100)</th><th scope="col" class="n">Annual rate</th></tr></thead><tbody>{righe}</tbody></table></div>'
              f'<p class="small">{rpi_dal}–{rpi[-1][0]}: RPI annual rate published by the ONS (series CZBH). * Before {rpi_dal} the ONS publishes no rate: '
              'the change is calculated here from the annual RPI long-run index, which is published to one decimal place.</p></details>')
    media10 = (val("uk_cpi", cpi[-1][0]) / val("uk_cpi", cpi[-1][0] - 10)) ** 0.1 - 1
    faq, ld_faq = faq_blocco("uk-rates", [
        ("What is the average UK inflation rate?",
         h(f'With the CPI, prices rose on average {pct(media_annua("uk_cpi", 1988, cpi[-1][0]), 1, segno=False)} a year from 1988 to {cpi[-1][0]} and '
           f'{pct(media10, 1, segno=False)} a year over the last ten years ({cpi[-1][0] - 10}–{cpi[-1][0]}). Over the long run the RPI series rose '
           f'{pct(media_annua("uk_rpi", 1900, cpi[-1][0]), 1, segno=False)} a year from 1900.'), "uk inflation average", "gb"),
        ("What were UK inflation rates over the last 10 years?",
         h("CPI annual rates published by the ONS: " + "; ".join(f"{y}: {pct(v, 1, segno=False)}" for y, v in ultimi) + "."), "uk inflation rate last 10 years", "gb"),
    ])
    corpo += faq + fonti_box(["ons_d7g7", "ons_d7bt", "ons_cdko", "ons_czbh"])
    testata = banda("United Kingdom · ONS", f"UK inflation rate by year ({cpi[0][0]}–{cpi[-1][0]})",
                    "Official CPI inflation from the Office for National Statistics, the last 12 months, and the Retail Prices Index long-run series back to 1801.",
                    corta=True)
    pagina("uk/inflation-rate-by-year/", f"UK Inflation Rate by Year: CPI {cpi[0][0]}–{cpi[-1][0]} and RPI since 1801",
           f"UK inflation by year from the ONS: CPI annual rates {cpi[0][0]}–{cpi[-1][0]}, the last 12 months to {UK_ULT_TXT} and the RPI long-run series since 1801.",
           corpo, testata, "uk", briciole=[("Home", ""), ("UK inflation calculator", "uk/"), ("UK inflation rate by year", "uk/inflation-rate-by-year/")],
           jsonld=[ld_faq] if ld_faq else None)


def uk_rpi():
    lu = ULT["uk_rpi"]
    corpo = '<div class="pull">' + calcolatore("uk", "RPI calculator", 1000, (2000, None), lu, serie_def="uk_rpi",
                                               pill=f'<span class="pill">Latest: {h(mese_breve(*lu))}</span>') + "</div>" + AD
    a0, m0 = lu[0] - 1, lu[1]
    corpo += ('<h2>How to calculate an RPI increase</h2><div class="testo">'
              '<p>Divide the RPI of the later month by the RPI of the earlier month. The result minus one is the percentage increase; multiplied by an amount '
              f'it gives the increased amount. Example with the long-run series: {mese_lungo(a0, m0)} {idx(val("uk_rpi", a0, m0))}, {mese_lungo(*lu)} '
              f'{idx(val("uk_rpi", *lu))}. Increase: {idx(val("uk_rpi", *lu))} ÷ {idx(val("uk_rpi", a0, m0))} − 1 = '
              f'<strong>{pct(val("uk_rpi", *lu) / val("uk_rpi", a0, m0) - 1, 1)}</strong>; £1,000 becomes {soldi(1000 * val("uk_rpi", *lu) / val("uk_rpi", a0, m0), "GBP")}.</p>'
              f'<p>The ONS also publishes the RPI with January 1987=100 (series CHAW, {idx(val_chaw(*lu))} in {mese_lungo(*lu)}). It moves exactly in step with '
              'the long-run series used here, so percentage increases are the same apart from rounding.</p>'
              '<p>A contract, lease or pension that is linked to the RPI may say which month to use, whether to round and whether there is a cap. '
              'Follow the wording of the document: the calculator only applies the published index.</p></div>')
    righe = ""
    for y in range(lu[0] - 10, lu[0]):
        rc, rp = CPI_RATE["annuale"][y] / 100, RPI_RATE["annuale"][y] / 100
        righe += f'<tr><td>{y}</td><td class="n">{pct(rp, 1)}</td><td class="n">{pct(rc, 1)}</td></tr>'
    corpo += ('<h2>RPI and CPI side by side</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Year</th><th scope="col" class="n">RPI annual rate</th>'
              f'<th scope="col" class="n">CPI annual rate</th></tr></thead><tbody>{righe}</tbody></table></div>'
              f'<p class="small">Annual rates published by the ONS (series CZBH and D7G7). Since 1988 the RPI rose {pct(vale_oggi("uk_rpi", 1988) - 1, 0, segno=False)} '
              f'and the CPI {pct(vale_oggi("uk_cpi", 1988) - 1, 0, segno=False)} (to {h(mese_lungo(*lu))}).</p>')
    corpo += uk_spiega()
    faq, ld_faq = faq_blocco("uk-rpi", [
        ("How do you calculate an RPI increase?",
         h(f'New amount = old amount × RPI of the later month ÷ RPI of the earlier month. From {mese_lungo(a0, m0)} to {mese_lungo(*lu)} the RPI long-run series '
           f'went from {idx(val("uk_rpi", a0, m0))} to {idx(val("uk_rpi", *lu))}, an increase of {pct(val("uk_rpi", *lu) / val("uk_rpi", a0, m0) - 1, 1, segno=False)}.'),
         "rpi increase calculator", "gb")])
    corpo += faq + fonti_box(["ons_cdko", "ons_chaw", "ons_czbh", "ons_d7bt", "ons_d7g7", "boe_calc"])
    testata = banda("United Kingdom · Retail Prices Index", "RPI calculator: increases by the Retail Prices Index",
                    f"Apply the official ONS Retail Prices Index to any amount between 1800 and {h(mese_lungo(*lu))}, with the formula and the index values used.",
                    trust([("check", "ONS RPI long-run series"), ("calc", "Formula shown"), ("lock", "Runs in your browser")]))
    pagina("uk/rpi-calculator/", "RPI Calculator UK: Retail Prices Index Increase (ONS)",
           f"RPI calculator with the official ONS Retail Prices Index long-run series, 1800 to {mese_lungo(*lu)}: increase between any two dates, formula and RPI vs CPI.",
           corpo, testata, "uk", briciole=[("Home", ""), ("UK inflation calculator", "uk/"), ("RPI calculator", "uk/rpi-calculator/")],
           jsonld=[jsonld_app("RPI calculator", URL_SITO + "/uk/rpi-calculator/", "en-GB")] + ([ld_faq] if ld_faq else []))


def val_chaw(a, m):
    return S["uk_rpi87"]["mensile"][(a, m)]


# ---------------------------------------------------------------- Germania
DE_LU = ULT["de"]
DE_ULT = ult_lungo("de", "de")
RATE_DE = S["de_rate_pubbl"]
K_DE = S["de"]["fattore"]


def de_rechner():
    m_rate = RATE_DE["vpi_monat"][DE_LU]
    corpo = '<div class="pull">' + calcolatore("de", "Inflationsrechner (VPI)", 100, (2002, None), DE_LU,
                                               pill=f'<span class="pill">Stand: {h(DE_ULT)}</span>') + "</div>" + AD
    corpo += (f'<div class="card stats"><div class="stat main"><b>{pct(m_rate / 100, 1, True, segno=False)}</b><span>Inflationsrate {h(DE_ULT)} (Destatis)</span></div>'
              f'<div class="stat"><b>{pct(RATE_DE["vpi_jahr"][2025] / 100, 1, True, segno=False)}</b><span>Inflationsrate 2025</span></div>'
              f'<div class="stat"><b>{pct(vale_oggi("de", 2002) - 1, 0, True)}</b><span>Preisanstieg seit 2002 (Euro-Bargeld)</span></div>'
              f'<div class="stat"><b>{idx(val("de", *DE_LU), True)}</b><span>VPI {h(DE_ULT)} (2020 = 100)</span></div></div>')
    v2000 = vale_oggi("de", 2000)
    corpo += ('<h2>So rechnet der Inflationsrechner</h2><div class="testo">'
              '<p>Der Rechner multipliziert Ihren Betrag mit dem Verhältnis zweier Werte des Verbraucherpreisindex für Deutschland (VPI, 2020 = 100) '
              'des Statistischen Bundesamtes: Betrag × VPI (Ziel) ÷ VPI (Start). Beispiel: 100 Euro im Jahr 2000 (Jahresdurchschnitt '
              f'{idx(val("de", 2000), True)}) entsprechen 100 × {idx(val("de", *DE_LU), True)} ÷ {idx(val("de", 2000), True)} = '
              f'<strong>{soldi(100 * v2000, "EUR")}</strong> im {h(DE_ULT)}.</p>'
              '<p>Wählen Sie nur ein Jahr, nimmt der Rechner den Jahresdurchschnitt; wählen Sie einen Monat, nimmt er den Indexwert dieses Monats. '
              'Das Ergebnis zeigt auch den gesamten Preisanstieg und die durchschnittliche Teuerung pro Jahr.</p></div>')
    corpo += ('<h2>D-Mark und Euro</h2><div class="testo">'
              '<p>Bis Ende 2001 bezahlte man in Deutschland mit der D-Mark; seit 2002 gibt es Euro-Bargeld. Der Umrechnungskurs ist unwiderruflich festgelegt: '
              '<strong>1 Euro = 1,95583 DM</strong>. Liegt das Startjahr vor 2002, können Sie den Betrag in D-Mark oder in Euro eingeben. Liegt das Zieljahr im Jahr 2002 oder später, '
              'rechnet der Rechner das Ergebnis in Euro um (geteilt durch 1,95583); sonst bleibt es in D-Mark.</p>'
              f'<p>Beispiel: 1.000 DM im Jahr 1995 entsprechen 1.000 × {idx(val("de", *DE_LU), True)} ÷ {idx(val("de", 1995), True)} ÷ 1,95583 = '
              f'<strong>{soldi(1000 * vale_oggi("de", 1995) / M.DM_PER_EURO, "EUR")}</strong> im {h(DE_ULT)}.</p></div>')
    sprung = val("de", 1991, 1) / (S["de_west"]["mensile"][(1991, 1)] * K_DE) - 1
    corpo += ('<h2>Vor 1991: früheres Bundesgebiet (Westdeutschland)</h2><div class="testo">'
              '<p>Der Verbraucherpreisindex für Deutschland beginnt mit dem Jahr 1991. Für die Jahre 1962 bis 1990 verwendet der Rechner den Preisindex für die '
              'Lebenshaltung aller privaten Haushalte im früheren Bundesgebiet (1995 = 100), den Destatis in den „Langen Reihen“ veröffentlicht. Damit beide Reihen '
              f'zusammenpassen, wird dieser Index im Jahr 1991 mit dem VPI verkettet: VPI 1991 ({idx(val("de", 1991), True)}) ÷ Index früheres Bundesgebiet 1991 '
              f'({idx(S["de_west"]["annuale"][1991], True)}) = {numero(K_DE, 5, True)}. Jeder Jahres- und Monatswert vor 1991 wird mit diesem Faktor multipliziert.</p>'
              '<p>Die verketteten Werte sind unsere eigene Berechnung auf Grundlage der Destatis-Daten, kein amtlicher Index, und nur eine Näherung: '
              'Der frühere Index gilt nur für Westdeutschland und beruht auf einem anderen Warenkorb. Destatis veröffentlicht beide Indizes mit einer Nachkommastelle; '
              'die verketteten Werte sind deshalb nicht genauer, auch wenn sie hier mit drei Nachkommastellen stehen. Weil über die Jahresdurchschnitte verkettet wird, '
              f'entsteht bei Monatswerten zwischen Dezember 1990 und Januar 1991 ein kleiner Sprung von rund {pct(abs(sprung), 1, True, segno=False)}. '
              'Für die DDR gibt es keinen vergleichbaren Index.</p></div>')
    righe = ""
    for y in (1965, 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2002, 2005, 2010, 2015, 2020, 2025):
        dm = y < 2002
        wert = 100 * vale_oggi("de", y) / (M.DM_PER_EURO if dm else 1)
        righe += (f'<tr><td>{y}{" *" if y < 1991 else ""}</td><td class="n">{idx(val("de", y), True)}</td><td class="n">{"100 DM" if dm else "100 €"}</td>'
                  f'<td class="n">{soldi(wert, "EUR")}</td><td class="n">{pct(vale_oggi("de", y) - 1, 0, True)}</td></tr>')
    corpo += (f'<h2>So viel sind 100 D-Mark oder 100 Euro von damals heute wert</h2><div class="tab"><table class="dati"><thead><tr><th scope="col">Jahr</th>'
              f'<th scope="col" class="n">VPI (2020 = 100)</th><th scope="col" class="n">Betrag damals</th><th scope="col" class="n">Wert im {h(DE_ULT)}</th>'
              f'<th scope="col" class="n">Preisanstieg seitdem</th></tr></thead><tbody>{righe}</tbody></table></div>'
              '<p class="small">* Vor 1991: Index für das frühere Bundesgebiet, mit dem VPI verkettet (eigene Berechnung auf Grundlage der Destatis-Daten). Jahreswerte sind Jahresdurchschnitte.</p>')
    corpo += ('<ul class="griglia"><li><a href="/de/inflationsrate-deutschland/"><b>%</b>Inflationsrate Deutschland<small>Jahre seit 1992, Monate seit 2021</small></a></li>'
              '<li><a href="/"><b>US</b>US inflation calculator<small>BLS CPI-U seit 1913 (englisch)</small></a></li>'
              '<li><a href="/uk/"><b>UK</b>UK inflation calculator<small>ONS CPI und RPI (englisch)</small></a></li></ul>')
    a, b = 2015, 2025
    faq, ld_faq = faq_blocco("de", [
        ("Wie berechnet man einen inflationsbereinigten Betrag?",
         h(f'Man multipliziert den Betrag mit dem Verbraucherpreisindex des Zieljahres und teilt durch den Index des Ausgangsjahres. Beispiel: 500 Euro aus dem Jahr '
           f'{a} entsprechen 500 × {idx(val("de", b), True)} ÷ {idx(val("de", a), True)} = {soldi(500 * val("de", b) / val("de", a), "EUR")} in Preisen von {b}.'),
         "inflationsbereinigung rechner", "de"),
        ("Wie berechnet man die Inflation zwischen zwei Jahren?",
         h(f'Man teilt den Indexwert des späteren Jahres durch den des früheren und zieht 1 ab. Von {a} bis {b} stieg der VPI von {idx(val("de", a), True)} auf '
           f'{idx(val("de", b), True)}, also um {pct(val("de", b) / val("de", a) - 1, 1, True, segno=False)}; das sind im Schnitt '
           f'{pct(media_annua("de", a, b), 1, True, segno=False)} pro Jahr.'), "inflation berechnen", "de"),
    ], "de")
    corpo += faq + fonti_box(["destatis_tabelle", "destatis_lange_reihen", "eurlex_2866", "ecb_euro"], "de")
    testata = banda("Deutschland · Verbraucherpreisindex", "Inflationsrechner: Was ist Ihr Geld heute wert?",
                    f"Der Rechner rechnet Beträge mit dem amtlichen Verbraucherpreisindex des Statistischen Bundesamtes um – von 1962 bis <strong>{h(DE_ULT)}</strong>, auch in D-Mark.",
                    trust([("check", "Amtliche Indexwerte von Destatis"), ("coins", "D-Mark und Euro"), ("lock", "Berechnung nur in Ihrem Browser")]))
    pagina("de/inflationsrechner/", "Inflationsrechner: Kaufkraft von Euro und D-Mark (VPI)",
           f"Kostenloser Inflationsrechner mit dem amtlichen Verbraucherpreisindex von Destatis, 1962 bis {DE_ULT}: Euro und D-Mark, Formel und Quellen.",
           corpo, testata, "de", briciole=[("Start", ""), ("Inflationsrechner", "de/inflationsrechner/")],
           jsonld=[jsonld_app("Inflationsrechner", URL_SITO + "/de/inflationsrechner/", "de-DE")] + ([ld_faq] if ld_faq else []))


def de_rate():
    anni = sorted(a for a in RATE_DE["vpi_jahr"] if a >= 1992)
    jahre = [(a, RATE_DE["vpi_jahr"][a] / 100) for a in anni]
    m_rate = RATE_DE["vpi_monat"][DE_LU]
    corpo = (f'<div class="card risposta pull"><p>Die Inflationsrate in Deutschland lag im {h(DE_ULT)} bei<span class="big">{pct(m_rate / 100, 1, True, segno=False)}</span>'
             f'gegenüber dem Vorjahresmonat. Im Jahresdurchschnitt {anni[-1]} betrug sie <strong>{pct(jahre[-1][1], 1, True, segno=False)}</strong> (Destatis).</p></div>')
    corpo += graf_barre(jahre, f"Inflationsrate in Deutschland {anni[0]} bis {anni[-1]}", "Veränderung des Verbraucherpreisindex gegenüber dem Vorjahr, amtliche Werte von Destatis.", de=True)
    corpo += AD
    righe = "".join(f'<tr><td>{a}</td><td class="n">{idx(val("de", a), True)}</td><td class="n">{pct(v, 1, True)}</td></tr>' for a, v in reversed(jahre))
    corpo += (f'<h2>Inflationsrate nach Jahren, {anni[0]}–{anni[-1]}</h2><div class="tab alta"><table class="dati"><thead><tr><th scope="col">Jahr</th>'
              '<th scope="col" class="n">VPI (2020 = 100)</th><th scope="col" class="n">Veränderung zum Vorjahr</th></tr></thead>'
              f'<tbody>{righe}</tbody></table></div>')
    mesi = sorted(RATE_DE["vpi_monat"], reverse=True)
    righe = "".join(f'<tr><td>{mese_lungo(a, m, "de")}</td><td class="n">{idx(val("de", a, m), True)}</td><td class="n">{pct(RATE_DE["vpi_monat"][(a, m)] / 100, 1, True)}</td></tr>'
                    for a, m in mesi)
    corpo += (f'<h2>Monatswerte seit {mese_lungo(*mesi[-1], "de")}</h2><div class="tab alta"><table class="dati"><thead><tr><th scope="col">Monat</th>'
              '<th scope="col" class="n">VPI</th><th scope="col" class="n">Veränderung zum Vorjahresmonat</th></tr></thead>'
              f'<tbody>{righe}</tbody></table></div>')
    west = sorted((a, v / 100) for a, v in RATE_DE["west_jahr"].items() if 1963 <= a <= 1991)
    righe = "".join(f'<tr><td>{a}</td><td class="n">{idx(S["de_west"]["annuale"][a], True)}</td><td class="n">{pct(v, 1, True)}</td></tr>' for a, v in reversed(west))
    corpo += (f'<h2>Früheres Bundesgebiet, {west[0][0]}–{west[-1][0]}</h2><div class="testo"><p>Für die Zeit vor 1991 gibt es keinen Index für ganz Deutschland. '
              'Für Westdeutschland veröffentlicht Destatis den Preisindex für die Lebenshaltung aller privaten Haushalte (1995 = 100); die Veränderungsraten sind amtliche Werte.</p></div>'
              '<div class="tab alta"><table class="dati"><thead><tr><th scope="col">Jahr</th><th scope="col" class="n">Index (1995 = 100)</th>'
              f'<th scope="col" class="n">Veränderung zum Vorjahr</th></tr></thead><tbody>{righe}</tbody></table></div>')
    vorher = (DE_LU[0] - 1, DE_LU[1])
    faq, ld_faq = faq_blocco("de-rate", [
        ("Wie hoch ist die Inflation in Deutschland aktuell?",
         h(f'Laut Statistischem Bundesamt lagen die Verbraucherpreise im {DE_ULT} um {pct(m_rate / 100, 1, True, segno=False)} höher als im '
           f'{mese_lungo(*vorher, "de")}. Der Verbraucherpreisindex (2020 = 100) stand bei {idx(val("de", *DE_LU), True)}.'), "aktuelle inflation deutschland", "de")], "de")
    corpo += faq + fonti_box(["destatis_tabelle", "destatis_lange_reihen"], "de")
    testata = banda("Deutschland · Destatis", f"Inflationsrate in Deutschland nach Jahren ({anni[0]}–{anni[-1]})",
                    "Jährliche und monatliche Veränderung des Verbraucherpreisindex – amtliche Werte des Statistischen Bundesamtes, dazu die Reihe für Westdeutschland ab 1963.",
                    corta=True)
    pagina("de/inflationsrate-deutschland/", f"Inflationsrate Deutschland: alle Jahre {anni[0]}–{anni[-1]} und Monate",
           f"Inflationsrate in Deutschland für jedes Jahr seit {anni[0]} und jeden Monat seit 2021, amtliche Werte von Destatis; aktuell {DE_ULT}: {pct(m_rate / 100, 1, True, segno=False)}.",
           corpo, testata, "de", briciole=[("Start", ""), ("Inflationsrechner", "de/inflationsrechner/"), ("Inflationsrate", "de/inflationsrate-deutschland/")],
           jsonld=[ld_faq] if ld_faq else None)


# ---------------------------------------------------------------- pagine di servizio
def about():
    corpo = ('<div class="testo pull card">'
             f'<p><strong>{h(NOME)}</strong> is an independent publication, part of a small network of websites that turn official data into plain tools. '
             + ('It converts amounts of money between dates with the consumer price indexes published by three statistics offices: the Bureau of Labor '
                'Statistics (United States), the Office for National Statistics (United Kingdom) and the Statistisches Bundesamt (Germany).</p>' if SEZIONE_DE else
                'It converts amounts of money between dates with the consumer price indexes published by two statistics offices: the Bureau of Labor '
                'Statistics (United States) and the Office for National Statistics (United Kingdom).</p>') +
             '<p>We are not a government website, a bank or a financial adviser, and we are not linked to any statistics office.</p></div>'
             '<h2>What we publish</h2><ul class="testo"><li>Only index values taken from the official files, with the date we read them.</li>'
             '<li>The formula and the two index values behind every result.</li><li>Where an index has a gap (such as October 2025 in the US), we say so and do not fill it.</li></ul>'
             f'<h2>Why the pages exist</h2><div class="testo"><p>People search for the value of a dollar from a given year, the inflation rate of a year, '
             + ('and calculators for the UK and Germany. ' if SEZIONE_DE else 'and a calculator for the UK. ') +
             'We built a page for each question that real searches show, and no more: one page per US year, '
             'ten decades for $100 and $1,000, the inflation tables of each country, and the calculators.</p></div>'
             '<h2>How the site is paid for</h2><div class="testo"><p>The site shows advertising served by Google AdSense. Advertisers never decide what we publish '
             'or change a figure.</p></div>'
             '<h2>Your data</h2><div class="testo"><p>The calculators run entirely in your browser: the amounts you type are not sent to us. See the '
             '<a href="/privacy/">privacy page</a>.</p></div>')
    testata = banda("About", f"About {NOME}", "What this site is, where its numbers come from and how it is paid for.", corta=True, icona="info")
    pagina("about/", f"About {NOME}", f"About {NOME}: an independent site that converts money between years with official "
           + ("BLS, ONS and Destatis price indexes." if SEZIONE_DE else "BLS and ONS price indexes for the US and the UK."),
           corpo, testata, "us", briciole=[("Home", ""), ("About", "about/")])


def come_controlliamo():
    nl = FONTI["_non_lette"]
    corpo = ('<div class="testo pull card"><p>Every index value on this site comes from an official file that we download from the statistics office and keep '
             f'with its address, the date we read it and a fingerprint (SHA-256). The current files were read on {data_lunga(CONTROLLO)}.</p></div>')
    boe_par = ('<p>UK results for dates before 1988 use the RPI long-run series and are higher than those of the Bank of England calculator, which uses modelled CPI '
               'estimates for those years; the <a href="/uk/#boe">UK page</a> shows the difference with an example.</p>')
    corpo += "<h2>Sources and licences</h2>" + "".join([
        '<h3>United States: BLS CPI-U</h3><div class="testo"><p>Consumer Price Index for All Urban Consumers, U.S. city average, all items, not seasonally adjusted '
        '(series CUUR0000SA0, 1982-84=100), monthly from January 1913 with the annual averages, read from the BLS data viewer. A second copy from the BLS Public Data '
        'API is kept to check it month by month. BLS data are in the public domain as works of the U.S. federal government.</p></div>',
        '<h3>United Kingdom: ONS CPI and RPI</h3><div class="testo"><p>CPI index (D7BT, 2015=100) and CPI annual rate (D7G7); Retail Prices Index long-run series '
        '(CDKO, Jan 1974=100), RPI (CHAW, Jan 1987=100) and its 12-month rate (CZBH), all from dataset MM23. Source: Office for National Statistics licensed under the '
        '<a href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/" rel="noopener">Open Government Licence v.3.0</a>.</p>'
        + ("" if SEZIONE_DE else boe_par) + '</div>',
        ('<h3>Germany: Destatis VPI</h3><div class="testo"><p>Verbraucherpreisindex für Deutschland (2020=100): the current monthly and annual table on destatis.de '
        'and the “Lange Reihen ab 1948” statistical report (VPI from 1991 and the index for all private households in the former West Germany, 1995=100). '
        '© Statistisches Bundesamt (Destatis); reproduction and distribution, also in part, permitted with the source cited. Contents of the GENESIS-Online '
        'database are under the <a href="https://www.govdata.de/dl-de/by-2-0" rel="noopener">Datenlizenz Deutschland – Namensnennung – Version 2.0</a>.</p>'
        f'<p>Before 1991 the German calculator links the West German index to the VPI at 1991 (factor {numero(K_DE, 5)}). This is our only calculated series and it is labelled on the page as our own calculation, not an official index.</p>'
        + boe_par + '</div>') if SEZIONE_DE else ""])
    corpo += ('<h2>What the checks do</h2><div class="testo"><ul>'
              '<li><strong>Continuity:</strong> no year or month may be missing between the first and the last value of a series. The only gap allowed is a month the '
              'office itself marks as not collected (October 2025 in the US), and it is shown on the pages.</li>'
              '<li><strong>Annual averages:</strong> the average of the twelve monthly values must match the published annual average within the rounding of the index.</li>'
              '<li><strong>Published rates:</strong> the rates we calculate from the indexes must match the rates the offices publish (ONS CPI and RPI 12-month rates'
              + (', Destatis yearly and monthly rates' if SEZIONE_DE else '') +
              ') within the rounding of the published indexes: 0.1 to 0.2 percentage points, and up to 0.3 for the RPI long-run '
              'series, which is published to one decimal place. Where an office publishes a rate (ONS CPI and RPI annual rates'
              + (', Destatis rates' if SEZIONE_DE else '') + ') the tables show the published rate, not our own calculation.</li>'
              f'<li><strong>Official calculator:</strong> {len(ESEMPI_BLS)} results are compared with the BLS CPI Inflation Calculator, to the cent.</li>'
              '<li><strong>Two files, one series:</strong> where two official files overlap (BLS viewer and API; '
              + ('Destatis report and current table; ' if SEZIONE_DE else '') + 'RPI long-run and RPI 1987=100) they must agree.</li>'
              '<li><strong>Browser = reference:</strong> the calculator in your browser is run against our reference implementation on thousands of random cases.</li></ul></div>')
    corpo += ('<h2>What we could not read</h2><div class="testo"><ul>' +
              "".join(f'<li><a href="{h(v["url"])}" rel="noopener">{h(v["url"].split("//")[1].split("/")[0])}</a>: {h(v["motivo"])}.</li>' for v in nl.values()
                      if SEZIONE_DE or "destatis" not in v["url"]) +
              '</ul><p>We never try to get round a block.</p></div>')
    corpo += ('<h2>When we update</h2><div class="testo"><p>' +
              ('Each office publishes a new month in the middle of the following month (the BLS and the ONS) or at '
               'the end of the month with a final figure in the middle of the next (Destatis). ' if SEZIONE_DE else
               'The BLS and the ONS publish a new month in the middle of the following month. ') +
              'We download the files again each month, run the checks and update the pages only if all of them pass.</p></div>')
    corpo += fonti_box([i for i in ["bls_cpiu", "bls_api", "bls_calc", "ons_d7bt", "ons_d7g7", "ons_cdko", "ons_chaw", "ons_czbh", "boe_calc", "destatis_tabelle",
                                    "destatis_lange_reihen", "fed_target", "ecb_euro", "eurlex_2866"] if SEZIONE_DE or i not in FONTI_DE])
    testata = banda("How we check", "How we check every index value", "Our sources and licences, the checks the data must pass and what we could not read.",
                    corta=True, icona="shield")
    pagina("how-we-check/", "How We Check: Sources, Licences and Data Checks",
           f"Where the {'BLS, ONS and Destatis' if SEZIONE_DE else 'BLS and ONS'} index values come from, their licences, the continuity and recalculation checks they pass, and how often we update.",
           corpo, testata, "us", briciole=[("Home", ""), ("How we check", "how-we-check/")])


def privacy():
    cookie = MON.privacy_cookie("en", SITO_ID)
    cal = MON.frase_california(SITO_ID)
    corpo = ('<div class="testo pull card">'
             f'<p>This page explains what {h(NOME)} ({URL_SITO.replace("https://", "")}) collects. In short: very little.</p></div>'
             '<div class="testo"><h2>The calculators</h2><p>The calculators run in your browser. The amounts and dates you type are not sent to us or to anyone else '
             'and are not stored. If you use “Copy link”, they are written into the address of the page so that you can share it; they leave your device only if you '
             'send that link to someone.</p><p>The site remembers your choice of light or dark theme in your browser (local storage). Nothing else is stored on your device by us.</p>'
             f'{cookie}'
             '<h2>Hosting</h2><p>The site is hosted on Netlify, which processes technical data (such as IP addresses) to deliver pages and protect the service.</p>'
             '<h2>Contact and accounts</h2><p>There are no accounts, forms or newsletters on this site.</p>'
             + (f"<p>{cal}</p>" if cal else "") +
             f'<h2>Changes</h2><p>We update this page when the site changes. Last update: {data_lunga(CONTROLLO)}.</p></div>')
    breve = MON.privacy_breve("en", SITO_ID) or "What we collect (very little) and how the visit counter works."
    testata = banda("Privacy", "Privacy", h(breve), corta=True, icona="lock")
    pagina("privacy/", f"Privacy | {NOME}",
           f"Privacy at {NOME}: the calculators run in your browser, a cookie-free visit counter, and Google AdSense advertising with consent.",
           corpo, testata, "us", briciole=[("Home", ""), ("Privacy", "privacy/")])


def pagina_404():
    corpo = ('<div class="pull card"><p>The page you asked for does not exist. Try one of the calculators below.</p></div>'
             '<ul class="griglia" style="margin-top:20px"><li><a href="/"><b>US</b>US inflation calculator</a></li><li><a href="/uk/"><b>UK</b>UK inflation calculator</a></li>'
             + ('<li><a href="/de/inflationsrechner/"><b>DE</b>Inflationsrechner</a></li>' if SEZIONE_DE else '') + '<li><a href="/us/inflation-rate-by-year/"><b>%</b>US inflation rate by year</a></li></ul>')
    testata = banda("404", "Page not found", "This address has no page.", corta=True, icona="alert")
    pagina("", f"Page not found | {NOME}", "Page not found.", corpo, testata.replace("{bc}", ""), "us", indicizza=False, file="404.html")


# ---------------------------------------------------------------- file accessori
NETLIFY = """[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in inflation/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = inflation/sito, Build command vuoto, Publish directory = "."
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[redirects]]
  from = "/us/"
  to = "/"
  status = 301

{redirect_de}[[headers]]
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
"""


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{CONTROLLO.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n', encoding="utf-8")
    redirect_de = '[[redirects]]\n  from = "/de/"\n  to = "/de/inflationsrechner/"\n  status = 301\n\n' if SEZIONE_DE else ""
    (SITO / "netlify.toml").write_text(NETLIFY.replace("{redirect_de}", redirect_de), encoding="utf-8")
    (DATI / "faq_generate.json").write_text(json.dumps({"_nota": "Scritto da genera.py: ogni FAQ pubblicata con la frase di ricerca da cui nasce (dati/domanda.json).",
                                                       "faq": FAQ_USATE}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def copia_grafica():
    (SITO / "assets").mkdir(parents=True, exist_ok=True)
    og = RADICE / "grafica" / ("og.png" if SEZIONE_DE else "og_us_uk.png")  # og_us_uk.png: stessa immagine senza la pillola DE
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")
    for nome, testo in ASSET.items():
        (SITO / "assets" / nome).write_text(testo, encoding="utf-8")


# ---------------------------------------------------------------- controlli sui dati prima di generare
def controlli():
    err = []
    err += serie.continuita(S["us"], "USA CPI-U")
    err += serie.continuita(S["uk_cpi"], "UK CPI")
    err += serie.continuita(S["uk_rpi"], "UK RPI lungo")
    if SEZIONE_DE:
        err += serie.continuita(S["de"], "DE VPI verkettet")
    for k, f in FONTI.items():
        if k.startswith("_") or (not SEZIONE_DE and k in FONTI_DE):
            continue
        if f.get("http") != 200:
            err.append(f"fonte {k}: HTTP {f.get('http')}")
        if f.get("trovate") and not all(f["trovate"].values()):
            err.append(f"fonte {k}: frasi non trovate {[c for c, ok in f['trovate'].items() if not ok]}")
    # valori noti (ricalcolati: media dei mesi = media annua pubblicata)
    for y in range(1913, ULTIMO_ANNO_US + 1):
        ms = [S["us"]["mensile"][(y, m)] for m in range(1, 13) if (y, m) in S["us"]["mensile"]]
        tol = 0.1001 if y < 2007 else 0.0006
        if abs(sum(ms) / len(ms) - S["us"]["annuale"][y]) > tol:
            err.append(f"USA {y}: media dei mesi {sum(ms) / len(ms):.3f} ≠ media annua {S['us']['annuale'][y]}")
    for y, atteso in ((1970, 38.8), (1980, 82.4), (2000, 172.2), (2020, 258.811), (2024, 313.689)):
        if S["us"]["annuale"].get(y) != atteso:
            err.append(f"USA {y}: media annua {S['us']['annuale'].get(y)} invece di {atteso} (valore noto BLS)")
    if not (2025, 10) in S["us"]["mancanti"]:
        err.append("USA: ottobre 2025 non più segnato come mancante: rivedere i testi")
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
    us_tassi()
    for y in ANNI_US:
        pagina_anno(y)
    for x in IMPORTI_PAGINA:
        for y in DECENNI_IMPORTO:
            pagina_importo(x, y)
    uk_calc()
    uk_tassi()
    uk_rpi()
    if SEZIONE_DE:  # spenta: nessuna pagina /de/ (la cartella sito/ è stata appena svuotata, quindi niente avanzi)
        de_rechner()
        de_rate()
    about()
    come_controlliamo()
    privacy()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404. Ultimi indici: US {US_ULT_TXT}, UK {UK_ULT_TXT}"
          + (f", DE {DE_ULT}." if SEZIONE_DE else ". Sezione tedesca spenta (SEZIONE_DE = False)."))


if __name__ == "__main__":
    main()
