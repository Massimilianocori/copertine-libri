"""Genera il sito statico Cruise Health Scores (inglese, pubblico USA) in cruisescores/sito/ da cruisescores/dati/.

Uso (dalla radice del repository):
    python3 cruisescores/raccolta/scarica.py   # pagine del CDC in cruisescores/cache/ (fuori da git)
    python3 cruisescores/raccolta/estrai.py    # dati puliti in cruisescores/dati/
    python3 cruisescores/genera.py             # pagine in cruisescores/sito/
    python3 cruisescores/verifica.py --browser # controlli prima di pubblicare

Dati (tutti dal CDC Vessel Sanitation Program, vedi NOTE.md):
    dati/navi.json       navi con pagina: nome, compagnia, stato (attiva/archiviata), storia [data, voto, id ispezione], rapporti
    dati/rapporti.json   ultime ispezioni di ogni nave: punti tolti per voce e infrazioni per esteso
    dati/ispezioni.json  tutte le ispezioni di tutte le navi del modulo CDC (per anni e bocciature)
    dati/epidemie.json   epidemie gastrointestinali pubblicate dal CDC
    dati/compagnie.json  nome mostrato per ogni compagnia (scritto a mano)
    dati/fonti.json      date e conteggi
    dati/affiliati.json  riquadri di affiliazione (compaiono solo con URL)
"""
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://cruise-health-scores.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti): non rimuoverlo

# Contatore visite GoatCounter, account condiviso "rete-siti" della rete (nessun cookie, nessun dato personale conservato).
# Il percorso inviato comprende l'host (location.host + percorso), così nel cruscotto https://rete-siti.goatcounter.com
# ogni sito si distingue dagli altri. Da localhost, da file:// e dalle reti private count.js non invia nulla
# (allow_local resta spento): le prove in locale non contano come visite. Unico punto da cambiare per tutto il sito.
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
# IndexNow (Bing, Yandex, Naver, Seznam): chiave pubblica uguale per tutti i siti della rete. Il generatore scrive
# sito/<chiave>.txt (contenuto: la chiave) accanto a robots.txt; l'invio degli URL lo fa studio-business/strumenti/indexnow.py.
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"
# Monetizzazione (30/10/2026): codice editore AdSense, elenco dei siti con la pubblicità e domini di affiliazione ammessi stanno
# in un solo file comune, studio-business/strumenti/monetizzazione.json (logica in monetizzazione.py). Con il codice vuoto o con
# questo sito fuori elenco non cambia nulla: niente script nel <head>, niente ads.txt, privacy di oggi.
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
SITO_ID = "cruisescores"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_"))


def frase_monetizzazione():
    """Frase della pagina About su pubblicità e link di affiliazione: vera in ogni combinazione (AdSense acceso o spento,
    link di affiliazione presenti o no)."""
    ads = MON.adsense_attivo(SITO_ID)
    if ads and ci_sono_affiliati():
        return ("The site shows advertising (Google AdSense) and contains clearly marked affiliate links (travel medical insurance); "
                "neither ever changes the data.")
    if ads:
        return "The site shows advertising (Google AdSense); it never changes the data."
    if ci_sono_affiliati():
        return "The site contains clearly marked affiliate links (travel medical insurance); they never change the data."
    return "The site may show advertising in the future; it will never change the data."


def riquadro_trasparenza(corpo, lingua="en"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Some links are affiliate links: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


NOME = "Cruise Health Scores"
SOGLIA = 86  # il CDC: "Inspections scores of 85 or lower are NOT satisfactory" -> 86 o più = superata

CDC_TOOL = "https://wwwn.cdc.gov/InspectionQueryTool/"
CDC_GREEN = CDC_TOOL + "InspectionGreenSheetRpt.aspx"
CDC_SEARCH = CDC_TOOL + "InspectionSearch.aspx"
CDC_100 = CDC_TOOL + "Inspectionwith100Score.aspx"
CDC_FAQ = "https://www.cdc.gov/vessel-sanitation/faq/index.html"
CDC_AREE = "https://www.cdc.gov/vessel-sanitation/communication-resources/operational-inspections.html"
CDC_ISP = "https://www.cdc.gov/vessel-sanitation/php/our-role/public-health-inspections.html"
CDC_EPID = "https://www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/index.html"
CDC_EPID_PREC = "https://www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/earlier-outbreaks.html"
CDC_EPID_2023 = "https://www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/earlier-outbreaks-2023.html"
CDC_ABOUT = "https://www.cdc.gov/vessel-sanitation/about/index.html"
CDC_SUGGERIMENTI = "https://www.cdc.gov/vessel-sanitation/communication-resources/tips-for-healthy-cruising.html"

ALTRI_SITI = [  # blocco "Other useful tools" (URL presi dai genera.py dei rispettivi siti)
    ("https://before-you-fly.netlify.app", "Before You Fly", "Passport validity, liquids rules by airport, EES and ETIAS"),
    ("https://visa-income-checker.netlify.app", "Visa Income Checker", "Minimum income for digital nomad, retirement and work visas"),
    ("https://flood-insurance-cost.netlify.app", "Flood Insurance Cost", "What NFIP flood insurance really costs, by ZIP code and county"),
]


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


FONTI = carica("fonti.json")
NAVI = carica("navi.json")
RAPPORTI = carica("rapporti.json")
ISPEZIONI = carica("ispezioni.json")
EPIDEMIE = carica("epidemie.json")
_COMP = {k: v for k, v in carica("compagnie.json").items() if not k.startswith("_")}
AFFILIATI = {k: v for k, v in carica("affiliati.json").items() if not k.startswith("_")}
OGGI = date.today()
CONTROLLATO = FONTI["scaricato_il"]
INFO_IL = FONTI.get("info_controllate_il", {})
ANNO = int(FONTI["green_sheet"]["ultima_ispezione"][:4])

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


# ---------------------------------------------------------------- utilità
def h(x):
    return escape(str(x))


def data_lunga(iso):
    d = date.fromisoformat(iso[:10])
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def data_breve(iso):
    d = date.fromisoformat(iso[:10])
    return f"{MESI[d.month - 1][:3]} {d.day}, {d.year}"


def mese_anno(iso):
    d = date.fromisoformat(iso[:10])
    return f"{MESI[d.month - 1]} {d.year}"


def slug(t):
    t = t.lower().replace("&", " and ").replace("'", "").replace("’", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def intero(x):
    return f"{x:,}"


def media(v):
    return sum(v) / len(v) if v else None


def num1(x):
    return "–" if x is None else f"{x:.1f}"


def comp_info(cdc):
    c = _COMP.get(cdc)
    return c if c else {"nome": cdc, "slug": slug(cdc)}


def nome_comp(cdc):
    return comp_info(cdc)["nome"]


def url_nave(s):
    return f"ships/{s}/"


def url_comp(cdc_o_slug, da_slug=False):
    return f"cruise-lines/{cdc_o_slug if da_slug else comp_info(cdc_o_slug)['slug']}/"


def passata(v):
    return v >= SOGLIA


def esito(v):
    return "Passed" if passata(v) else "Failed"


def classe(v):
    if v >= 100:
        return "s100"
    if v >= 95:
        return "s95"
    if v >= 90:
        return "s90"
    if v >= SOGLIA:
        return "s86"
    return "sf"


def chip(v, grande=False):
    return f'<span class="sc {classe(v)}{" sc-l" if grande else ""}" title="{esito(v)}">{v}</span>'


def chip_media(m):
    """Media con un decimale (99.6, non 100: un 100 arrotondato sembrerebbe un voto perfetto di tutte le navi)."""
    return f'<span class="sc {classe(m)}" title="Average of the latest scores">{num1(m)}</span>'


def esito_tag(v):
    return f'<span class="esito {"ok" if passata(v) else "ko"}">{ico("check" if passata(v) else "x")}{esito(v)}</span>'


def elenco_nomi(nomi, max_n=3):
    nomi = list(nomi)
    if len(nomi) <= max_n:
        return ", ".join(nomi[:-1]) + (" and " if len(nomi) > 1 else "") + nomi[-1] if nomi else ""
    return ", ".join(nomi[:max_n]) + f" and {len(nomi) - max_n} more"


def plurale(n, sing, plur=None):
    return f"{intero(n)} {sing if n == 1 else (plur or sing + 's')}"


# ---------------------------------------------------------------- strutture derivate
for _s, _n in NAVI.items():
    _n["slug"] = _s
    _n["nome"] = re.sub(r" Of The ", " of the ", _n["nome"])  # il CDC scrive "Wonder Of The Seas"
    _n["ultima"] = _n["storia"][0]
    _n["linea"] = comp_info(_n["compagnia"])

LINEE = {}
for _s, _n in sorted(NAVI.items(), key=lambda kv: kv[1]["nome"].lower()):
    L = LINEE.setdefault(_n["linea"]["slug"], {"nome": _n["linea"]["nome"], "slug": _n["linea"]["slug"], "cdc": set(), "navi": []})
    L["cdc"].add(_n["compagnia"])
    L["navi"].append(_s)
for _k, _v in _COMP.items():
    if _v["slug"] in LINEE:
        LINEE[_v["slug"]]["cdc"].add(_k)

ATTIVE = [s for s in sorted(NAVI, key=lambda s: NAVI[s]["nome"].lower()) if NAVI[s]["stato"] == "attiva"]
ARCHIVIATE = [s for s in sorted(NAVI, key=lambda s: NAVI[s]["nome"].lower()) if NAVI[s]["stato"] == "archiviata"]
ANNI_ISP = Counter(int(r[0][:4]) for r in ISPEZIONI)
# Pagine degli anni: dal 2010 (prima il modulo del CDC ha poche ispezioni, perché tiene solo le navi ancora nel suo elenco)
ANNI = [y for y in sorted(ANNI_ISP, reverse=True) if y >= 2010 and ANNI_ISP[y] >= 20]
ANNI_CLASSIFICHE = [y for y in (ANNO, ANNO - 1) if ANNI_ISP.get(y)]


def epidemie_nave(s):
    return [e for e in EPIDEMIE if e.get("slug") == s]


# ---------------------------------------------------------------- icone, marchio, CSS, JS
ICONE = {
    "search": '<circle cx="11" cy="11" r="7.5"/><path d="M21 21l-4.5-4.5"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "doc": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8 13h8M8 17h5"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "up": '<path d="M7 17 17 7M9 7h8v8"/>',
    "down": '<path d="M7 7l10 10M17 9v8H9"/>',
    "ship": '<path d="M3 15.5l1.6 4h14.8l1.6-4H3z"/><path d="M6 15.5V10h12v5.5M9 10V6.5h6V10M12 3.5v3"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01"/>',
    "trophy": '<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H4.5v1.5A3.5 3.5 0 0 0 8 11M16 6h3.5v1.5A3.5 3.5 0 0 1 16 11M12 13v4M8.5 20.5h7M9.5 17h5v3.5h-5z"/>',
    "virus": '<circle cx="12" cy="12" r="5"/><path d="M12 2.5v4.5M12 17v4.5M2.5 12H7M17 12h4.5M5.3 5.3l3.2 3.2M15.5 15.5l3.2 3.2M5.3 18.7l3.2-3.2M15.5 8.5l3.2-3.2"/>',
    "drop": '<path d="M12 3s6.5 7 6.5 11.5a6.5 6.5 0 0 1-13 0C5.5 10 12 3 12 3z"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 19V7.5A1.5 1.5 0 0 1 5.5 6H10"/>',
    "tool": '<path d="M4 6.5h16M4 12h16M4 17.5h10"/>',
}
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>\n")
ICONS_FILE = f"icons.{hashlib.sha256(SPRITE.encode()).hexdigest()[:10]}.svg"


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# Marchio: anello del punteggio (quasi chiuso) con un segno di spunta, su tessera blu notte; stesso disegno in favicon e Open Graph
_M = ('<rect width="40" height="40" rx="10" fill="#0C2233"/>'
      '<circle cx="20" cy="20" r="12.5" fill="none" stroke="#2C4A5E" stroke-width="3.4"/>'
      '<path d="M20 7.5a12.5 12.5 0 1 1-11.7 8.1" fill="none" stroke="#3FB8A9" stroke-width="3.4" stroke-linecap="round"/>'
      '<path d="M14.6 20.4l3.7 3.7 7.2-7.6" fill="none" stroke="#F4F1E8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{_M}</svg>\n'

CSS = r"""
@font-face{font-family:"Newsreader";src:url(/assets/fonts/newsreader.woff2) format("woff2");font-weight:200 800;font-style:normal;font-display:swap}
@font-face{font-family:"Public Sans";src:url(/assets/fonts/public-sans.woff2) format("woff2");font-weight:100 900;font-style:normal;font-display:swap}
:root{--bg:#F3F5F4;--card:#FFFFFF;--ink:#0F1D27;--ink-2:#36474F;--ink-3:#56666E;--line:#DBE2E1;--line-2:#C3CECD;
--deep:#0C2233;--deep-2:#13344A;--on-deep:#EEF4F5;--on-deep-2:#AEC2CA;--accent:#0A6A6E;--accent-h:#074D50;--accent-2:#E1F0EE;--on-accent:#FFFFFF;
--brass:#E2B04A;--brass-ink:#7A5208;--brass-2:#FBF3E1;--mute:#ECF0EF;--track:#E2E8E7;
--s100:#0B6639;--s95:#2B7448;--s90:#4F6E1C;--s86:#F0B23E;--s86-ink:#2B1D00;--sf:#B42318;--ok:#0B6639;--ko:#B42318;--fail-band:#FBE9E7;
--sh-1:0 1px 2px rgba(12,34,51,.06),0 1px 1px rgba(12,34,51,.04);--sh-2:0 22px 44px -24px rgba(12,34,51,.38),0 2px 8px rgba(12,34,51,.06);
--r:14px;--r-s:10px;--serif:Newsreader,"Iowan Old Style",Charter,Georgia,serif;--sans:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#09131A;--card:#101D26;--ink:#E5EDF0;--ink-2:#B9C7CD;--ink-3:#91A3AB;--line:#1F3240;--line-2:#2B4353;
--deep:#060F15;--deep-2:#0D2433;--on-deep:#E5EDF0;--on-deep-2:#9FB4BD;--accent:#5EC9C0;--accent-h:#8FDDD6;--accent-2:#0F302F;--on-accent:#04191A;
--brass:#E9BC5E;--brass-ink:#E9BC5E;--brass-2:#2A2112;--mute:#13232D;--track:#1B2E3A;
--s100:#187A4A;--s95:#2F8152;--s90:#5B7D22;--s86:#F0B23E;--s86-ink:#2B1D00;--sf:#D2392B;--ok:#6FD39C;--ko:#FF8A7D;--fail-band:#2A1715;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -24px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#09131A;--card:#101D26;--ink:#E5EDF0;--ink-2:#B9C7CD;--ink-3:#91A3AB;--line:#1F3240;--line-2:#2B4353;
--deep:#060F15;--deep-2:#0D2433;--on-deep:#E5EDF0;--on-deep-2:#9FB4BD;--accent:#5EC9C0;--accent-h:#8FDDD6;--accent-2:#0F302F;--on-accent:#04191A;
--brass:#E9BC5E;--brass-ink:#E9BC5E;--brass-2:#2A2112;--mute:#13232D;--track:#1B2E3A;
--s100:#187A4A;--s95:#2F8152;--s90:#5B7D22;--s86:#F0B23E;--s86-ink:#2B1D00;--sf:#D2392B;--ok:#6FD39C;--ko:#FF8A7D;--fail-band:#2A1715;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -24px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--brass);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.ico{width:1.1em;height:1.1em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.18em}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.06)}
header.top .wrap{display:flex;align-items:center;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:650;font-size:1.25rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;letter-spacing:-.005em;margin-right:auto}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:#7FD6CB;font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.08)}
.tema{display:grid;place-items:center;width:42px;height:42px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--brass)}.tema .ico{width:20px;height:20px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:.95rem;padding:9px 13px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep);min-height:42px}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--brass)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{padding:12px 14px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600}.nav-m nav a:hover{background:var(--accent-2)}
.band{background:linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%);color:var(--on-deep);position:relative;overflow:hidden}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(760px 260px at 88% -20%,rgba(63,184,169,.20),transparent 62%);pointer-events:none}
.band::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:linear-gradient(90deg,transparent,rgba(226,176,74,.55),transparent)}
.band-in{position:relative;z-index:1;padding:30px 16px 78px}
.band.flat .band-in{padding-bottom:40px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.76rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--brass);margin:0 0 12px}
h1,h2,h3{font-family:var(--serif);font-weight:650;letter-spacing:-.01em}
h1{font-size:clamp(1.9rem,5vw,2.9rem);line-height:1.08;margin:0 0 12px;text-wrap:balance;max-width:840px}
.band h1{color:#fff}
.sub{font-size:1.08rem;color:var(--on-deep-2);margin:0 0 16px;max-width:720px}
.trust{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--on-deep-2);margin:0;padding:0;list-style:none}
.trust li{display:inline-flex;align-items:center;gap:7px}.trust .ico{color:var(--brass)}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.4rem,3vw,1.7rem);line-height:1.2;margin:46px 0 12px}
h3{font-size:1.18rem;margin:26px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:780px;margin:0 0 14px}
.small{font-size:.87rem;color:var(--ink-3)}
.muted{color:var(--ink-3)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-56px;position:relative;z-index:2}
/* scheda del voto */
.key{padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.key-top{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;background:var(--mute);color:var(--ink-2);padding:10px 20px;font-size:.76rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;border-bottom:1px solid var(--line)}
.key-top .ico{color:var(--accent)}.key-top span:last-child{margin-left:auto;letter-spacing:.02em;text-transform:none;font-weight:600}
.key-body{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr)}
.key-main{padding:22px 24px;display:flex;gap:22px;align-items:center}
.ring{flex:none;width:132px;height:132px;position:relative}
.ring svg{width:100%;height:100%;transform:rotate(-90deg)}
.ring .tr{fill:none;stroke:var(--track);stroke-width:10}
.ring .va{fill:none;stroke-width:10;stroke-linecap:round}
.ring .v-s100,.ring .v-s95{stroke:var(--s100)}.ring .v-s90{stroke:var(--s90)}.ring .v-s86{stroke:var(--s86)}.ring .v-sf{stroke:var(--sf)}
.ring .rn{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1}
.ring .rn b{font-family:var(--serif);font-size:2.9rem;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.ring .rn span{font-size:.78rem;color:var(--ink-3);margin-top:4px;font-weight:600}.ring.avg .rn b{font-size:2.2rem}
.k-lab{font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin:0 0 6px}
.k-txt{margin:8px 0 0;color:var(--ink-2);font-size:.98rem}
.esito{display:inline-flex;align-items:center;gap:6px;font-weight:800;font-size:.9rem;padding:4px 11px;border-radius:999px;letter-spacing:.01em}
.esito.ok{color:var(--ok);background:color-mix(in srgb,var(--ok) 12%,transparent)}.esito.ko{color:var(--ko);background:color-mix(in srgb,var(--ko) 13%,transparent)}
.key-side{border-left:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr}
.tile{padding:16px 18px;border-bottom:1px solid var(--line);min-width:0}
.tile:nth-child(odd){border-right:1px solid var(--line)}.tile:nth-last-child(-n+2){border-bottom:0}
.tile b{display:block;font-family:var(--serif);font-size:1.45rem;line-height:1.15;font-variant-numeric:tabular-nums;color:var(--ink)}
.tile span{display:block;font-size:.82rem;color:var(--ink-3);line-height:1.35;margin-top:4px}
.trend{display:inline-flex;align-items:center;gap:6px;font-weight:700;font-size:.88rem;padding:3px 10px;border-radius:999px;background:var(--mute);color:var(--ink-2);margin-top:10px;font-variant-numeric:tabular-nums}
/* chip del voto */
.sc{flex:none;white-space:nowrap;display:inline-flex;align-items:center;justify-content:center;min-width:2.6em;height:1.85em;padding:0 .45em;border-radius:8px;font-weight:800;font-variant-numeric:tabular-nums;color:#fff;font-size:.95rem;line-height:1}
.sc.s100{background:var(--s100)}.sc.s95{background:var(--s95)}.sc.s90{background:var(--s90)}.sc.s86{background:var(--s86);color:var(--s86-ink)}.sc.sf{background:var(--sf)}
.sc-l{font-size:1.15rem;min-width:2.8em;height:2em}
.scala{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px;margin:10px 0 4px;padding:0;list-style:none}
.scala li{border-radius:10px;padding:10px 12px;color:#fff;font-size:.86rem;line-height:1.3;min-width:0}
.scala li b{display:block;font-size:1.05rem;font-variant-numeric:tabular-nums}
.scala .s100{background:var(--s100)}.scala .s95{background:var(--s95)}.scala .s90{background:var(--s90)}.scala .s86{background:var(--s86);color:var(--s86-ink)}.scala .sf{background:var(--sf)}
/* tabelle */
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1)}
table{border-collapse:collapse;width:100%;font-size:.94rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:middle}
td.n,th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
td.c,th.c{text-align:center}
th{background:var(--mute);font-size:.74rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
tbody tr:last-child td{border-bottom:0}
tr.ko td{background:var(--fail-band)}
td a{font-weight:600}
.nowrap{white-space:nowrap}
@media (max-width:640px){
.lt thead{display:none}.lt,.lt tbody,.lt tr,.lt td{display:block}
.lt tr{position:relative;padding:11px 74px 11px 14px;border-bottom:1px solid var(--line);min-height:52px}
.lt tbody tr:last-child{border-bottom:0}
.lt td{border:0;padding:0;text-align:left!important;background:none!important}
.lt td.t1{font-weight:600;margin-bottom:2px}.lt td.sc-c{position:absolute;right:14px;top:50%;transform:translateY(-50%)}
.lt td.x{display:inline-block;margin-right:14px;font-size:.86rem;color:var(--ink-3);line-height:1.5}.lt td.x:empty{display:none}
.lt td.x[data-l]::before{content:attr(data-l) ": ";color:var(--ink-3)}
.lt tr.ko{background:var(--fail-band)}
th,td{padding:9px 9px}table{font-size:.9rem}}
/* griglie e liste */
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;align-items:center;justify-content:space-between;gap:10px;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;text-decoration:none;color:var(--ink);min-width:0;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px)}
.griglia a span{display:flex;flex-direction:column;min-width:0;font-weight:700;overflow-wrap:anywhere}
.griglia a small{font-weight:500;color:var(--ink-3);font-size:.84rem}
.stat-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 14px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:14px;box-shadow:var(--sh-1);min-width:0}
.stat b{display:block;font-family:var(--serif);font-size:1.5rem;line-height:1.15;font-variant-numeric:tabular-nums}
.stat span{display:block;font-size:.82rem;color:var(--ink-3);margin-top:4px;line-height:1.35}
.stat a{text-decoration:none;color:inherit}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
/* ricerca */
.cerca-card{padding:18px 20px}
.cerca-card label{display:flex;align-items:center;gap:8px;font-family:var(--serif);font-weight:650;font-size:1.2rem;margin:0 0 10px}
.cerca-card label .ico{color:var(--accent)}
.cerca-box{position:relative}.cerca-box .ico{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--ink-3);pointer-events:none}
.cerca{font:inherit;font-size:1.05rem;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:12px 14px 12px 44px;width:100%;min-height:52px}
.cerca:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.risultati{display:grid;gap:6px;margin-top:10px}.risultati:empty{display:none}
.risultati a{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:9px 12px;border-radius:var(--r-s);border:1px solid var(--line);text-decoration:none;color:var(--ink);background:var(--card)}
.risultati a:hover,.risultati a:focus{border-color:var(--accent);background:var(--accent-2)}
.risultati a b{font-weight:700;display:block}.risultati a small{font-size:.84rem;color:var(--ink-3);display:block}
.esempi{font-size:.86rem;color:var(--ink-3);margin:10px 0 0}
/* grafico */
.chart-card{padding:16px 16px 10px}
.chart{width:100%;height:auto;display:block}.chart-m{display:none}
.chart .fb{fill:var(--fail-band)}.chart .ax{stroke:var(--line-2);stroke-width:1}.chart .g{stroke:var(--line);stroke-width:1;stroke-dasharray:2 4}
.chart .soglia{stroke:var(--sf);stroke-width:1.2;stroke-dasharray:5 4}
.chart .ln{fill:none;stroke:var(--accent);stroke-width:2.2;stroke-linejoin:round}
.chart circle{stroke:var(--card);stroke-width:2}
.chart .p-s100,.chart .p-s95{fill:var(--s100)}.chart .p-s90{fill:var(--s90)}.chart .p-s86{fill:var(--s86)}.chart .p-sf{fill:var(--sf)}
.chart text{fill:var(--ink-3);font-family:var(--sans);font-size:11px}.chart .lbl{fill:var(--ink);font-weight:700}.chart .ls{fill:var(--sf);font-weight:700}
.legenda{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.82rem;color:var(--ink-2);margin:6px 0 0;padding:0;list-style:none}
.legenda li{display:inline-flex;align-items:center;gap:6px}.legenda i{width:12px;height:12px;border-radius:50%;display:inline-block}
/* rapporti */
.isp{margin:18px 0;padding:0;overflow:hidden}
.isp-h{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;padding:16px 20px;border-bottom:1px solid var(--line);background:var(--mute)}
.isp-h h3{margin:0;font-size:1.2rem}.isp-h .small{margin:0}
.isp-b{padding:6px 20px 18px}
.punti{margin:12px 0 4px;padding:0;list-style:none;display:grid;gap:6px}
.punti li{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 12px;align-items:baseline;font-size:.93rem}
.pt{font-weight:800;font-variant-numeric:tabular-nums;color:var(--ko);min-width:4.2em}
.area{margin-top:16px}
.area h4{display:flex;align-items:center;gap:8px;font-family:var(--sans);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.area h4 span{margin-left:auto;font-weight:600;letter-spacing:0;text-transform:none;color:var(--ink-3)}
.viol{margin:0;padding:0;list-style:none;display:grid;gap:10px}
.viol li{border-left:3px solid var(--line-2);padding:2px 0 2px 12px}
.viol li.pp{border-left-color:var(--ko)}
.viol .dove{display:block;font-weight:700;font-size:.92rem;color:var(--ink)}
.viol .it{display:inline-block;font-size:.74rem;font-weight:700;letter-spacing:.04em;color:var(--ink-3);border:1px solid var(--line-2);border-radius:6px;padding:0 6px;margin-right:6px;vertical-align:1px;white-space:nowrap}
.viol p{margin:2px 0 0;color:var(--ink-2);font-size:.94rem}
details.tutte{margin-top:12px}details.tutte>summary{cursor:pointer;font-weight:700;color:var(--accent);padding:6px 0}
/* riquadri */
.nota{position:relative;background:var(--brass-2);border:1px solid color-mix(in srgb,var(--brass) 45%,transparent);padding:12px 16px 12px 46px;border-radius:var(--r-s);font-size:.93rem;margin:18px 0;color:var(--ink)}
.nota .ico{position:absolute;left:16px;top:14px;color:var(--brass-ink);width:20px;height:20px}
.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.fonti-box{margin-top:44px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:16px 20px;font-size:.9rem;color:var(--ink-2)}
.fonti-box h2{display:flex;align-items:center;gap:8px;font-size:1.12rem;margin:0 0 8px;color:var(--ink)}.fonti-box h2 .ico{color:var(--accent)}
.fonti-box ul{margin:0 0 8px;padding-left:18px}.fonti-box li{margin-bottom:6px}.fonti-box p{margin:6px 0}
.fonti-box a{overflow-wrap:anywhere}
.aff{margin:28px 0;display:flex;gap:16px;align-items:flex-start;background:var(--card);border:1px dashed var(--line-2);border-radius:var(--r);padding:16px 18px}
.aff>div{min-width:0;display:grid;gap:4px}
.aff .ic{flex:none;display:grid;place-items:center;width:42px;height:42px;border-radius:10px;background:var(--accent-2);color:var(--accent)}.aff .ic .ico{width:22px;height:22px}
.aff .btn{white-space:normal;text-align:left}
.aff h2{font-family:var(--sans);font-size:1rem;font-weight:700;margin:0;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.aff p{margin:0;font-size:.93rem;color:var(--ink-2)}.aff .small{font-size:.82rem;margin-top:6px}
.aff-tag{font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);border:1px solid var(--line-2);border-radius:999px;padding:1px 8px}
.aff a.btn{margin-top:8px}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-weight:700;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:11px 18px;cursor:pointer;min-height:44px;text-decoration:none;font-size:.95rem}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}.btn:disabled{opacity:.6;cursor:wait}
.btn.sec{background:none;color:var(--accent);border:1.5px solid var(--accent)}.btn.sec:hover{background:var(--accent-2);color:var(--accent-h)}
.ad-slot{margin:24px 0}.ad-slot:empty{display:none}
.testo p,.testo li{max-width:780px}
.testo h2:first-child{margin-top:8px}
.faq details{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 16px;margin:8px 0}
.faq summary{cursor:pointer;font-weight:700}.faq details p{margin:8px 0 0;color:var(--ink-2)}
.form{display:grid;gap:14px}.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}.form .check input{width:auto;min-height:0;margin-top:4px}
.hp{position:absolute;left:-9999px}.ok-msg{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:var(--r-s)}.errore{color:var(--ko);font-weight:600}
.strumenti{margin-top:56px;border-top:1px solid var(--line);padding-top:22px}
.strumenti h2{font-family:var(--sans);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3);margin:0 0 10px}
.strumenti ul{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:0;padding:0;list-style:none}
.strumenti a{display:block;height:100%;padding:12px 14px;border:1px solid var(--line);border-radius:var(--r-s);background:var(--card);text-decoration:none;color:var(--ink);font-weight:700;font-size:.95rem}
.strumenti a:hover{border-color:var(--accent)}.strumenti a small{display:block;font-weight:500;color:var(--ink-3);font-size:.84rem;margin-top:2px}
footer{margin-top:40px;background:var(--deep);color:var(--on-deep-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--on-deep)}footer a:hover{color:var(--brass)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}footer p{margin:0 0 10px;max-width:680px}footer strong{color:var(--on-deep)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--brass);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
@media (max-width:880px){.key-body{grid-template-columns:1fr}.key-side{border-left:0;border-top:1px solid var(--line)}.stat-row{grid-template-columns:repeat(2,minmax(0,1fr))}.cols{grid-template-columns:1fr}.strumenti ul{grid-template-columns:1fr}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:22px}}
@media (max-width:640px){.chart-d{display:none}.chart-m{display:block}.chart text{font-size:13px}.area h4 span{white-space:nowrap}.key-main{padding:18px;gap:16px}.ring{width:108px;height:108px}.ring .rn b{font-size:2.35rem}.ring.avg .rn b{font-size:1.8rem}
.scala{grid-template-columns:repeat(2,minmax(0,1fr))}.scala li:last-child{grid-column:1/-1}.isp-h,.isp-b{padding-left:14px;padding-right:14px}}
@media (max-width:440px){.logo{font-size:1.06rem;gap:8px}.logo img{width:30px;height:30px}header.top .wrap{gap:8px}.nav-m summary{padding:9px 11px}.nav-m summary .lbl{display:none}.tema{width:40px;height:40px}.aff .ic{display:none}}
@media (max-width:420px){.tile{padding:12px 14px}.tile b{font-size:1.25rem}.key-main{flex-direction:column;align-items:flex-start}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""
CSS = re.sub(r"/\*.*?\*/", "", CSS)
CSS = re.sub(r"\n", "", CSS)

TEMA_JS = "(function(){try{var t=localStorage.getItem('chs-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"
APP_JS = r"""
(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('chs-theme',n);}catch(e){}});
  var src=document.querySelectorAll('input[name=source]');var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  var box=document.querySelector('[data-cerca]');if(!box)return;
  var inp=box.querySelector('input'),out=box.querySelector('.risultati'),D=null,carico=false,coda=null;
  function norm(s){return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function cl(v){return v>=100?'s100':v>=95?'s95':v>=90?'s90':v>=86?'s86':'sf';}
  function carica(cb){if(D)return cb();coda=cb;if(carico)return;carico=true;
    fetch(box.getAttribute('data-url')).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){D=d;
      d.forEach(function(x){x.k=norm(x[0]+' '+(x[6]||''));x.l=norm(x[2]);});if(coda)coda();})
    .catch(function(){out.innerHTML='<p class="errore">Could not load the list of ships. Please try again.</p>';carico=false;});}
  function riga(x){return '<a href="/ships/'+esc(x[1])+'/"><span><b>'+esc(x[0])+'</b><small>'+esc(x[2])+' · inspected '+esc(x[4])+(x[5]?'':' · no longer in the CDC list')+'</small></span><span class="sc '+cl(x[3])+'">'+x[3]+'</span></a>';}
  function cerca(){var q=inp.value,v=norm(q);if(v.length<2){out.innerHTML='';return;}
    carica(function(){var a=[],b=[],c=[];
      D.forEach(function(x){if(x.k.indexOf(v)===0)a.push(x);else if((' '+x.k).indexOf(' '+v)>=0)b.push(x);else if(x.l.indexOf(v)===0||(' '+x.l).indexOf(' '+v)>=0)c.push(x);});
      var r=a.concat(b,c).slice(0,10);
      out.innerHTML=r.length?r.map(riga).join(''):'<p class="small">No ship found for "'+esc(q)+'". Try part of the name, such as "Wonder" or "Carnival". Ships that left U.S. waters long ago are not listed.</p>';});}
  inp.addEventListener('input',cerca);inp.addEventListener('focus',function(){carica(function(){});},{once:true});
  box.querySelector('form').addEventListener('submit',function(e){e.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;else cerca();});
})();
"""


def _impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:10]


ASSET = {
    f"site.{_impronta(CSS)}.css": CSS,
    f"app.{_impronta(APP_JS)}.js": APP_JS.strip() + "\n",
    f"favicon.{_impronta(FAVICON_SVG)}.svg": FAVICON_SVG,
    ICONS_FILE: SPRITE,
}
CSS_FILE, JS_FILE, FAVICON_FILE, _ = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="34" height="34" alt="">'


def scrivi_asset():
    (SITO / "assets").mkdir(parents=True, exist_ok=True)
    for nome, testo in ASSET.items():
        (SITO / "assets" / nome).write_text(testo, encoding="utf-8")


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
DISCLAIMER = ("This site is not affiliated with or endorsed by the CDC. A CDC score shows how well a ship met sanitation standards on the day "
              "of the inspection; it is not a safety rating and does not tell you whether a ship is “safe”.")


def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, testata="", jsonld_extra=None, aff=False):
    file = percorso if percorso.endswith(".html") else (percorso + "index.html")
    url_pag = URL_SITO + "/" + percorso
    if indicizza:
        URLS.append(percorso)
    ld = []
    if percorso == "":
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/",
                   "description": "CDC Vessel Sanitation Program inspection scores for every cruise ship that sails from U.S. ports."})
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL_SITO + "/"}]
        for i, (n, p) in enumerate(briciole, start=2):
            voci.append({"@type": "ListItem", "position": i, "name": n, "item": URL_SITO + "/" + p})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb"><a href="/">Home</a>' +
              "".join(f' › <a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]) + f" › {h(briciole[-1][0])}</nav>")
    if jsonld_extra:
        ld.extend(jsonld_extra if isinstance(jsonld_extra, list) else [jsonld_extra])
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    voci_menu = [("ships/", "Ships"), ("cruise-lines/", "Cruise lines"), ("rankings/", "Rankings"),
                 ("how-cdc-cruise-ship-inspections-work/", "How inspections work")]
    menu = "".join(f'<a href="/{u}"' + (' aria-current="page"' if percorso.startswith(u) else "") + f'>{t}</a>' for u, t in voci_menu)
    testata = testata.replace("{bc}", bc)
    altri = "".join(f'<li><a href="{u}" rel="noopener">{h(n)}<small>{h(d)}</small></a></li>' for u, n, d in ALTRI_SITI)
    testo = f"""<!DOCTYPE html>
<html lang="en-US">
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
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NOME}: CDC sanitation inspection scores for every cruise ship that sails from U.S. ports">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0C2233">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/public-sans.woff2" as="font" type="font/woff2" crossorigin>
<script>{TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Cruise <b>Health</b> Scores</span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Open the menu">{ico("menu")}<span class="lbl">Menu</span></summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo}{riquadro_trasparenza(corpo)}
{box_affiliati() if aff else ""}
<aside class="strumenti" aria-labelledby="strumenti-h"><h2 id="strumenti-h">Other useful tools</h2><ul>{altri}</ul></aside>
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="/">{LOGO}<span>Cruise <b>Health</b> Scores</span></a>
<p><strong>{NOME}</strong> republishes the cruise ship inspection scores and reports of the <a href="{CDC_TOOL}" rel="noopener">CDC Vessel Sanitation Program</a>, in a form that is easier to read. {DISCLAIMER}</p>
<p>Ships fail a CDC inspection when they score 85 or lower. For the official record, always check the <a href="{CDC_GREEN}" rel="noopener">CDC Green Sheet</a>.</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="/ships/">All ships</a></li><li><a href="/cruise-lines/">Cruise lines</a></li><li><a href="/rankings/">Rankings</a></li><li><a href="/years/">Scores by year</a></li><li><a href="/outbreaks/">Outbreaks</a></li><li><a href="/methodology/">Methodology</a></li><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/privacy.html">Privacy</a></li></ul>
</div></div>
<p class="f-base">Data: CDC Vessel Sanitation Program, Inspection Query Tool · data checked on {data_lunga(CONTROLLATO)} · updated weekly.{' Some links are affiliate links and are marked as such.' if ci_sono_affiliati() else ''}</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", piatta=False):
    return f"""<section class="band{' flat' if piatta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico("shield")}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def trust():
    return (f'<ul class="trust"><li>{ico("doc")}Source: CDC public records</li><li>{ico("calendar")}Data checked on {data_lunga(CONTROLLATO)}</li>'
            f'<li>{ico("check")}Pass mark: 86 out of 100</li><li>{ico("info")}Independent site, not the CDC</li></ul>')


def box_affiliati():
    """Riquadri di affiliazione: solo le voci con URL (oggi solo SafetyWing). Testo prudente, dicitura di affiliazione chiara."""
    out = []
    for k, v in AFFILIATI.items():
        if not v.get("url"):
            continue
        out.append(f'<aside class="aff" aria-labelledby="aff-{k}"><span class="ic">{ico("shield")}</span><div>'
                   f'<h2 id="aff-{k}">{h(v["titolo"])} <span class="aff-tag">Affiliate</span></h2>'
                   f'<p>{h(v["testo"])} {h(v.get("avvertenza", ""))}</p>'
                   f'<p><a class="btn sec" href="{h(v["url"])}" rel="sponsored noopener" target="_blank">{h(v["bottone"])}{ico("external")}<span class="sr"> (opens in a new tab)</span></a></p>'
                   f'<p class="small">{MON.RIGA_EN} It never changes the scores on this site.</p></div></aside>')
    return "".join(out)


ULTIMA_CDC = FONTI["green_sheet"]["ultima_ispezione"][:10]
_GIORNI_RITARDO = (date.fromisoformat(CONTROLLATO) - date.fromisoformat(ULTIMA_CDC)).days
# Il CDC pubblica le ispezioni con ritardo (il 17/10/2026 la più recente era del 29/8/2026): lo si dice senza inventare il motivo.
RITARDO = (f"The most recent inspection the CDC has published is from {data_lunga(ULTIMA_CDC)}; inspections done after that date "
           f"will appear here once the CDC posts them." if _GIORNI_RITARDO > 14 else
           f"The most recent inspection the CDC has published is from {data_lunga(ULTIMA_CDC)}.")


def fonte_box(data_isp=None, extra=""):
    """Riquadro delle fonti (in ogni pagina con dati): CDC con link, data dell'ispezione, data del controllo, avviso."""
    di = f"<li>Inspection date: <strong>{data_lunga(data_isp)}</strong>.</li>" if data_isp else ""
    return f"""<aside class="fonti-box" aria-label="Sources">
<h2>{ico("doc")}Source</h2>
<ul>
<li><a href="{CDC_TOOL}" rel="noopener">CDC Vessel Sanitation Program, Inspection Query Tool</a>: <a href="{CDC_GREEN}" rel="noopener">Green Sheet</a> (latest score of each ship), inspection search and inspection reports.</li>
{di}<li>Data checked on <strong data-controllato>{data_lunga(CONTROLLATO)}</strong>. {RITARDO}</li>{extra}
</ul>
<p>{DISCLAIMER} How we read the CDC data: <a href="/methodology/">methodology</a>.</p>
</aside>"""


def come_trovare(nome):
    return (f'<p class="small">To see this report on the CDC site: open the <a href="{CDC_SEARCH}" rel="noopener">CDC inspection search</a>, choose '
            f'<em>{h(nome)}</em> in the list of cruise ships, select “All Dates” and press Search, then open “Report” next to the inspection date. '
            f'(The CDC tool does not allow direct links to a single report.)</p>')


# ---------------------------------------------------------------- componenti
def anello(v, etichetta="out of 100"):
    r = 52
    circ = 2 * 3.14159265 * r
    media_ = isinstance(v, float)
    testo = num1(v) if media_ else str(v)
    aria = (f"Average latest score {testo} out of 100" if media_ else f"Score {v} out of 100, {esito(v).lower()}")
    return (f'<div class="ring{" avg" if media_ else ""}" role="img" aria-label="{aria}"><svg viewBox="0 0 120 120" aria-hidden="true">'
            f'<circle class="tr" cx="60" cy="60" r="{r}"/><circle class="va v-{classe(v)}" cx="60" cy="60" r="{r}" '
            f'stroke-dasharray="{circ * v / 100:.1f} {circ:.1f}"/></svg><div class="rn" aria-hidden="true"><b>{testo}</b><span>{etichetta}</span></div></div>')


def tabella_navi(slugs, colonne=("linea",), titolo_col="Ship"):
    """Elenco di navi con ultimo voto: a schede su telefono."""
    righe = []
    for s in slugs:
        n = NAVI[s]
        d, v, _ = n["ultima"]
        prec = n["storia"][1][1] if len(n["storia"]) > 1 else None
        celle = [f'<td class="t1"><a href="/{url_nave(s)}">{h(n["nome"])}</a>' + (' <span class="small">(archived)</span>' if n["stato"] == "archiviata" else "") + "</td>"]
        if "linea" in colonne:
            celle.append(f'<td class="x" data-l="Line"><a href="/{url_comp(n["linea"]["slug"], True)}" style="font-weight:500">{h(n["linea"]["nome"])}</a></td>')
        celle.append(f'<td class="x nowrap" data-l="Inspected">{data_breve(d)}</td>')
        if "prec" in colonne:
            celle.append(f'<td class="x n" data-l="Previous">{prec if prec is not None else "–"}</td>')
        if "n" in colonne:
            celle.append(f'<td class="x n" data-l="Inspections">{len(n["storia"])}</td>')
        celle.append(f'<td class="c sc-c">{chip(v)}<span class="sr"> {esito(v)}</span></td>')
        righe.append(f'<tr{" class=ko" if not passata(v) else ""}>{"".join(celle)}</tr>')
    th = [f"<th>{titolo_col}</th>"]
    if "linea" in colonne:
        th.append("<th>Cruise line</th>")
    th.append("<th>Last inspection</th>")
    if "prec" in colonne:
        th.append('<th class="n">Previous score</th>')
    if "n" in colonne:
        th.append('<th class="n">Inspections</th>')
    th.append('<th class="c">Score</th>')
    return f'<div class="tab"><table class="lt"><thead><tr>{"".join(th)}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'


def tabella_ispezioni(righe_isp, con_linea=True, limite=None):
    """righe_isp: [data, voto, nome nave, compagnia CDC, slug]."""
    righe = []
    for d, v, nave, comp, s in righe_isp[:limite] if limite else righe_isp:
        nome = f'<a href="/{url_nave(s)}">{h(NAVI[s]["nome"])}</a>' if s else h(nave)
        if s and C_norm(nave) != C_norm(NAVI[s]["nome"]):
            nome += f' <span class="small">(as {h(nave)})</span>'
        celle = [f'<td class="t1">{nome}</td>']
        if con_linea:
            celle.append(f'<td class="x" data-l="Line">{h(nome_comp(comp))}</td>')
        celle.append(f'<td class="x nowrap" data-l="Date">{data_breve(d)}</td><td class="c sc-c">{chip(v)}<span class="sr"> {esito(v)}</span></td>')
        righe.append(f'<tr{" class=ko" if not passata(v) else ""}>{"".join(celle)}</tr>')
    th = "<th>Ship</th>" + ("<th>Cruise line</th>" if con_linea else "") + '<th>Inspection date</th><th class="c">Score</th>'
    return f'<div class="tab"><table class="lt"><thead><tr>{th}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'


def C_norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def scala_voti():
    return (f'<ul class="scala" aria-label="How to read a CDC score">'
            f'<li class="s100"><b>100</b>Perfect: no points deducted</li><li class="s95"><b>95–99</b>Passed, few problems</li>'
            f'<li class="s90"><b>90–94</b>Passed</li><li class="s86"><b>86–89</b>Passed, close to the line</li>'
            f'<li class="sf"><b>85 or lower</b>Failed (not satisfactory)</li></ul>'
            f'<p class="small">The CDC only says that 85 or lower is “not satisfactory”. The color bands above are ours, to make the list easier to scan.</p>')


def grafico_storia(n):
    """Due versioni (computer e telefono, una sola visibile): stesso grafico con proporzioni diverse."""
    return (f'<figure class="card chart-card" style="margin:0">{_svg_storia(n, 720, 250, "chart chart-d")}{_svg_storia(n, 400, 280, "chart chart-m")}'
            '<ul class="legenda" aria-hidden="true">'
            f'<li><i style="background:var(--s100)"></i>95–100</li><li><i style="background:var(--s90)"></i>90–94</li>'
            f'<li><i style="background:var(--s86)"></i>86–89</li><li><i style="background:var(--sf)"></i>85 or lower (failed)</li></ul></figure>')


def _svg_storia(n, W, H, cls):
    """Linea dei voti nel tempo con la fascia di bocciatura. Accessibile: role=img con descrizione; i dati sono nella tabella sotto."""
    st = list(reversed(n["storia"]))  # dalla più vecchia
    L, R, T, B = 40, 14, 14, 30
    voti = [x[1] for x in st]
    ymin = min(75, (min(voti) - 4) // 5 * 5)
    d0 = date.fromisoformat(st[0][0]).toordinal()
    d1 = date.fromisoformat(st[-1][0]).toordinal()
    a0, a1 = date.fromisoformat(st[0][0]).year, date.fromisoformat(st[-1][0]).year
    t0 = date(a0, 1, 1).toordinal()
    t1 = date(a1 + 1, 1, 1).toordinal() if d1 > date(a1, 7, 1).toordinal() else max(d1 + 60, date(a1, 12, 31).toordinal())
    t1 = max(t1, t0 + 365)

    def X(o):
        return L + (o - t0) / (t1 - t0) * (W - L - R)

    def Y(v):
        return T + (100 - v) / (100 - ymin) * (H - T - B)

    out = [f'<rect class="fb" x="{L}" y="{Y(85.5):.1f}" width="{W - L - R}" height="{H - B - Y(85.5):.1f}"/>']
    passo = 5 if 100 - ymin <= 30 else 10
    for v in range(int(ymin), 101, passo):
        out.append(f'<line class="g" x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    out.append(f'<line class="soglia" x1="{L}" x2="{W - R}" y1="{Y(85.5):.1f}" y2="{Y(85.5):.1f}"/>')
    out.append(f'<text class="ls" x="{L + 8}" y="{H - B - 7}">Fail zone: 85 or lower</text>')
    anni = list(range(a0, a1 + 1))
    salto = max(1, -(-len(anni) // (8 if W > 500 else 5)))
    for a in anni[::salto]:
        xa = X(date(a, 1, 1).toordinal())
        out.append(f'<line class="ax" x1="{xa:.1f}" x2="{xa:.1f}" y1="{H - B}" y2="{H - B + 5}"/><text x="{xa + 3:.1f}" y="{H - 8}">{a}</text>')
    out.append(f'<line class="ax" x1="{L}" x2="{W - R}" y1="{H - B}" y2="{H - B}"/>')
    pts = [(X(date.fromisoformat(d).toordinal()), Y(v), d, v) for d, v, _ in st]
    if len(pts) > 1:
        out.append('<path class="ln" d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y, _, _ in pts) + '"/>')
    for x, y, d, v in pts:
        out.append(f'<circle class="p-{classe(v)}" cx="{x:.1f}" cy="{y:.1f}" r="5"><title>{data_breve(d)}: {v}</title></circle>')
    lo = min(st, key=lambda x: (x[1], x[0]))
    hi_ultima = st[-1]
    desc = (f"Line chart of {len(st)} CDC inspection scores of {n['nome']} from {a0} to {a1}. Latest score {hi_ultima[1]} on {data_lunga(hi_ultima[0])}; "
            f"lowest {lo[1]} on {data_lunga(lo[0])}; {plurale(sum(1 for v in voti if v < SOGLIA), 'failed inspection')}. All scores are listed in the table below.")
    return f'<svg class="{cls}" viewBox="0 0 {W} {H}" role="img" aria-label="{h(desc)}">' + "".join(out) + '</svg>'


# Aree dei rapporti: il CDC scrive "Galley-Deck 12 ..." (area prima del trattino). Etichette più chiare per i lettori.
AREE = {
    "Galley": "Galleys (kitchens)", "Crew Galley": "Crew galley", "Pantry": "Pantries", "Bar": "Bars", "Buffet": "Buffets",
    "Provisions": "Food storage (provisions)", "Preparation Room": "Food preparation rooms", "Food Service General": "Food safety, general",
    "Dining Room": "Dining rooms", "Potable Water": "Drinking water", "Recreational Water Facilities": "Pools, hot tubs and water play areas",
    "Housekeeping": "Housekeeping", "Child Activity Center": "Child activity centers", "HVAC": "Air conditioning and ventilation (HVAC)",
    "Medical": "Medical center", "Integrated Pest Management": "Pest control", "Pest": "Pest control", "Warewash": "Dishwashing",
    "Crew Mess": "Crew mess", "Other": "Other areas", "Children Area": "Children’s areas", "Ventilation": "Ventilation",
    "General Comments": "General comments", "Deli": "Delis", "Room Service": "Room service", "Garbage Room": "Garbage room",
}


def area_di(sito):
    a, _, resto = sito.partition("-")
    a = a.strip().lstrip("*").strip()
    return a, resto.strip(" -")


def blocco_rapporto(id_isp, nome_nave, aperto=True, titolo_livello="h3"):
    r = RAPPORTI[id_isp]
    v = r["voto"]
    tolti = [p for p in r["punti"] if p[2] > 0]
    desc_voce = {p[0]: p[1] for p in r["punti"]}
    punti_voce = {p[0]: p[2] for p in r["punti"]}
    n_voci = len(r["voci"])
    gruppi = defaultdict(list)
    for num, sito, viol in r["voci"]:
        a, dettaglio = area_di(sito)
        gruppi[a].append((num, dettaglio, viol))
    ordine = sorted(gruppi, key=lambda a: (-sum(punti_voce.get(x[0], 0) > 0 for x in gruppi[a]), -len(gruppi[a]), a))
    corpo_aree = []
    for a in ordine:
        lis = []
        for num, dettaglio, viol in gruppi[a]:
            pp = punti_voce.get(num, 0) > 0
            tit = f' title="{h(desc_voce.get(num, ""))}"' if desc_voce.get(num) else ""
            lis.append(f'<li{" class=pp" if pp else ""}><span class="dove"><span class="it"{tit}>Item {h(num)}</span>{h(dettaglio) or h(a)}</span><p>{h(viol)}</p></li>')
        etich = AREE.get(a, a)
        corpo_aree.append(f'<div class="area"><h4>{h(etich)}<span>{plurale(len(gruppi[a]), "finding")}</span></h4><ul class="viol">{"".join(lis)}</ul></div>')
    if tolti:
        lista_punti = "".join(f'<li><span class="pt">−{p[2]} {"pt" if p[2] == 1 else "pts"}</span><span>Item {h(p[0])}: {h(p[1])}</span></li>' for p in sorted(tolti, key=lambda p: (-p[2], p[0])))
        riepilogo = f'<p class="small" style="margin:12px 0 0">Points deducted (100 − {sum(p[2] for p in tolti)} = {v}):</p><ul class="punti">{lista_punti}</ul>'
    else:
        riepilogo = '<p class="small" style="margin:12px 0 0">No points deducted.</p>'
    if n_voci:
        testo_voci = (f'<p class="small" style="margin:14px 0 0">All {plurale(n_voci, "finding")} the inspectors wrote down, grouped by area of the ship. '
                      f'Findings with a red edge belong to an item that lost points; the others were noted without a deduction.</p>' + "".join(corpo_aree))
    else:
        testo_voci = '<p class="small" style="margin:14px 0 0">The CDC report lists no violations for this inspection.</p>'
    tag = "h3" if titolo_livello == "h3" else "h2"
    inner = f'{riepilogo}{testo_voci}'
    if not aperto and n_voci:
        inner = f'{riepilogo}<details class="tutte"><summary>Show all {plurale(n_voci, "finding")}</summary>{testo_voci}</details>'
    return (f'<article class="card isp" id="i{h(id_isp)}"><div class="isp-h"><{tag}>{data_lunga(r["data"])}</{tag}>{chip(v, True)}{esito_tag(v)}'
            f'<p class="small">{plurale(n_voci, "finding")} · {plurale(sum(p[2] for p in tolti), "point")} deducted</p></div>'
            f'<div class="isp-b">{inner}</div></article>')


# ---------------------------------------------------------------- pagine delle navi
def pagina_nave(s):
    n = NAVI[s]
    st = n["storia"]
    d, v, _ = n["ultima"]
    L = n["linea"]
    voti = [x[1] for x in st]
    prec = st[1] if len(st) > 1 else None
    bocciate = [x for x in st if x[1] < SOGLIA]
    ult5 = voti[:5]
    lo = min(st, key=lambda x: (x[1], x[0]))
    anno_prima = st[-1][0][:4]
    cento = sum(1 for x in voti if x == 100)
    trend = ""
    if prec:
        diff = v - prec[1]
        trend = (f'<span class="trend">{ico("up" if diff > 0 else "down" if diff < 0 else "calendar")}'
                 f'{"+" if diff > 0 else "−" if diff < 0 else "±"}{abs(diff)} vs previous inspection ({prec[1]}, {data_breve(prec[0])})</span>')
    archiviata = n["stato"] == "archiviata"
    stato_txt = ("" if not archiviata else
                 f'<div class="nota">{ico("info")}<p><strong>No longer in the CDC’s current list.</strong> {h(n["nome"])} is not on the CDC Green Sheet, '
                 f'which shows “the most recent inspection score for each ship in VSP jurisdiction”. When a ship sails outside the United States for an extended period, '
                 f'it drops out of the CDC database and is inspected again if it returns (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>). Its last score is from {data_lunga(d)}.</p></div>')
    giorni = (date.fromisoformat(CONTROLLATO) - date.fromisoformat(d)).days
    if not archiviata and giorni > 365:
        stato_txt = (f'<div class="nota">{ico("info")}<p><strong>No CDC inspection in over a year.</strong> {h(n["nome"])} is on the CDC Green Sheet, '
                     f'but its latest published inspection is from {data_lunga(d)}. The CDC says that a ship sailing outside the United States for an extended period '
                     f'“may not be inspected twice a year” and is inspected again when it returns (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</p></div>')
    tiles = [
        (f"{num1(media(ult5))}", f"average of the last {len(ult5)} inspections") if len(ult5) > 1 else (f"{v}", "only score on record"),
        (f"{lo[1]}", f"lowest score ({mese_anno(lo[0])})"),
        (f"{len(st)}", f"inspections since {anno_prima}" if len(st) > 1 else f"inspection, in {anno_prima}"),
        (f"{len(bocciate)}", "failed inspections" if len(bocciate) != 1 else "failed inspection"),
    ]
    side = "".join(f'<div class="tile"><b>{a}</b><span>{b}</span></div>' for a, b in tiles)
    key = f"""<section class="card key pull" aria-label="Latest CDC score">
<div class="key-top">{ico("ship")}<span>{h(L["nome"])}</span><span>Inspected {data_lunga(d)}</span></div>
<div class="key-body"><div class="key-main">{anello(v)}<div>
<p class="k-lab">Latest CDC sanitation score</p>
{esito_tag(v)}
<p class="k-txt">{h(n["nome"])} scored <strong>{v} out of 100</strong> in its {"latest" if not archiviata else "last"} CDC Vessel Sanitation Program inspection, on {data_lunga(d)}. {"It passed: ships pass with 86 or more." if passata(v) else "It failed: 85 or lower is not satisfactory."}</p>
{trend}
</div></div><div class="key-side">{side}</div></div>
</section>"""
    # storia
    righe = []
    for dd, vv, idi in st:
        link = f'<a href="#i{h(idi)}">findings below</a>' if idi in n["rapporti"] else ""
        righe.append(f'<tr{" class=ko" if not passata(vv) else ""}><td class="t1 nowrap">{data_lunga(dd)}</td><td class="x" data-l="Result">{esito(vv)}</td>'
                     f'<td class="x">{link}</td><td class="c sc-c">{chip(vv)}</td></tr>')
    tab_storia = f'<div class="tab"><table class="lt"><thead><tr><th>Inspection date</th><th>Result</th><th>Report</th><th class="c">Score</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>'
    if len(st) > 12:
        tab_storia = (f'<details class="tutte"><summary>Show all {len(st)} inspections</summary>{tab_storia}</details>')
    # rapporti
    rapp = "".join(blocco_rapporto(i, n["nome"], aperto=(k == 0)) for k, i in enumerate(n["rapporti"]))
    if not n["rapporti"]:
        rapp = '<p class="lead">The detailed reports for this ship could not be downloaded from the CDC at the last update.</p>'
    # epidemie
    ep = epidemie_nave(s)
    blocco_ep = ""
    if ep:
        li = "".join(f'<li><strong>{h(e["date"])}</strong> · cause: {h(e["agente"] or "unknown")}' +
                     (f' · ill: {h(e["passeggeri"])} passengers, {h(e["equipaggio"])} crew' if e.get("passeggeri") else "") +
                     (f' · <a href="{h(e["url"])}" rel="noopener">CDC outbreak page</a>' if e.get("url") else "") + "</li>" for e in ep)
        blocco_ep = (f'<h2>Gastrointestinal illness outbreaks</h2><p class="lead">The CDC posts an outbreak when 3% or more of passengers or crew report '
                     f'gastrointestinal symptoms to the ship’s medical staff on a voyage, and may also post other outbreaks of public health significance (<a href="{CDC_EPID}" rel="noopener">CDC outbreak list</a>). Outbreaks posted for {h(n["nome"])} since 2023:</p>'
                     f'<ul>{li}</ul><p class="small">An outbreak is reported separately from the inspection score. See <a href="/outbreaks/">all cruise ship outbreaks</a>.</p>')
    altre = [x for x in LINEE[L["slug"]]["navi"] if x != s]
    altre.sort(key=lambda x: (NAVI[x]["stato"] != "attiva", -NAVI[x]["ultima"][1], NAVI[x]["nome"]))
    griglia = "".join(f'<li><a href="/{url_nave(x)}"><span>{h(NAVI[x]["nome"])}<small>{data_breve(NAVI[x]["ultima"][0])}</small></span>{chip(NAVI[x]["ultima"][1])}</a></li>' for x in altre[:12])
    altri_nomi = (f'<p class="small">The CDC record of this ship also lists it as: {h(", ".join(n["altri_nomi"]))}.</p>' if n["altri_nomi"] else "")
    altre_comp = (f'<p class="small">Earlier inspections list a different operator: {h(", ".join(nome_comp(c) for c in n["altre_compagnie"]))}.</p>' if n["altre_compagnie"] else "")
    n_r = len(n["rapporti"])
    corpo = f"""{key}
{stato_txt}
{AD}
<h2>Inspection history of {h(n["nome"])}</h2>
<p class="lead">{f'Every CDC inspection score on record for {h(n["nome"])}: {plurale(len(st), "inspection")} from {data_lunga(st[-1][0])} to {data_lunga(st[0][0])}, {plurale(cento, "perfect score") if cento else "no perfect scores"} of 100 and {plurale(len(bocciate), "failed inspection") if bocciate else "no failed inspections"}.' if len(st) > 1 else f'The CDC records list one inspection of {h(n["nome"])} so far, on {data_lunga(st[0][0])}.'}</p>
{grafico_storia(n)}
<h3>All scores</h3>
{tab_storia}
{altri_nomi}{altre_comp}
<h2>What the inspectors found</h2>
<p class="lead">The full findings of the {"latest inspection" if n_r <= 1 else f"last {n_r} inspections"}, as written in the CDC reports. Each finding refers to an item of the CDC’s Vessel Sanitation Program standards; points are deducted by item, for a single significant violation or for a pattern of similar ones (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</p>
{rapp}
{come_trovare(n["nome"])}
{blocco_ep}
<h2>Other {h(L["nome"])} ships</h2>
{('<ul class="griglia">' + griglia + '</ul>') if griglia else '<p class="lead">No other ships of this cruise line are in the CDC list.</p>'}
<p><a href="/{url_comp(L["slug"], True)}">All {h(L["nome"])} CDC scores</a> · <a href="/ships/">All ships</a> · <a href="/how-cdc-cruise-ship-inspections-work/">How CDC inspections work</a></p>
{fonte_box(d)}"""
    anno = d[:4]
    titolo = f"{n['nome']} CDC Inspection Score: {v}/100 ({mese_anno(d)[:3]} {anno})"
    if len(titolo) < 52:
        titolo += " and History"
    descr = (f"{n['nome']} scored {v}/100 in its {'latest' if not archiviata else 'last'} CDC sanitation inspection ({data_breve(d)})"
             f"{'' if passata(v) else ', a fail'}. "
             + (f"See all {len(st)} scores since {anno_prima} and what inspectors found." if len(st) > 1 else "See what the inspectors found, item by item."))
    if len(descr) > 160:
        descr = descr.replace(" sanitation inspection", " inspection")
    testata = banda(f"{L['nome']} · CDC inspection record", f"{n['nome']} CDC inspection score",
                    f"Latest score, full inspection history and the violations CDC inspectors found on {h(n['nome'])}.", trust())
    pagina(url_nave(s), titolo, descr, corpo, briciole=[("Cruise lines", "cruise-lines/"), (L["nome"], url_comp(L["slug"], True)), (n["nome"], url_nave(s))],
           testata=testata, aff=True)


# ---------------------------------------------------------------- pagine delle compagnie
def stats_linea(L):
    att = [s for s in L["navi"] if NAVI[s]["stato"] == "attiva"]
    ult = [NAVI[s]["ultima"][1] for s in att]
    isp_anno = [r for r in ISPEZIONI if r[0][:4] == str(ANNO) and comp_info(r[3])["slug"] == L["slug"]]
    return att, ult, isp_anno


def pagina_linea(ls):
    L = LINEE[ls]
    att, ult, isp_anno = stats_linea(L)
    arch = [s for s in L["navi"] if NAVI[s]["stato"] == "archiviata"]
    ordinate = sorted(att, key=lambda s: (-NAVI[s]["ultima"][1], NAVI[s]["nome"]))
    corpo = []
    if att:
        best_v = max(ult)
        worst_v = min(ult)
        best = [NAVI[s]["nome"] for s in ordinate if NAVI[s]["ultima"][1] == best_v]
        worst = [NAVI[s]["nome"] for s in reversed(ordinate) if NAVI[s]["ultima"][1] == worst_v]
        boc = [s for s in att if not passata(NAVI[s]["ultima"][1])]
        tiles = [(num1(media(ult)), "average latest score"), (f"{best_v}", "best latest score"), (f"{worst_v}", "lowest latest score"),
                 (f"{len(boc)}", "ships whose latest inspection failed" if len(boc) != 1 else "ship whose latest inspection failed")]
        if len(att) == 1:
            nv = NAVI[att[0]]
            tiles = [(f"{best_v}", "latest score"), (f"{len(nv['storia'])}", "inspection on record" if len(nv['storia']) == 1 else "inspections on record"),
                     (f"{sum(1 for x in nv['storia'] if x[1] < SOGLIA)}", "failed inspections"), (data_breve(nv["ultima"][0]), "latest inspection")]
        side = "".join(f'<div class="tile"><b>{a}</b><span>{b}</span></div>' for a, b in tiles)
        media_anno = media([r[1] for r in isp_anno])
        if len(att) > 1:
            txt = (f"{h(L['nome'])} has {plurale(len(att), 'ship')} on the CDC Green Sheet. Best latest score: {best_v} ({h(elenco_nomi(best))}); "
                   f"lowest: {worst_v} ({h(elenco_nomi(worst))}).")
        else:
            txt = (f"{h(L['nome'])} has one ship on the CDC Green Sheet, {h(best[0])}, which scored {best_v} at its latest inspection "
                   f"on {data_lunga(NAVI[att[0]]['ultima'][0])}.")
        if isp_anno:
            txt += f" In {ANNO} so far the CDC inspected its ships {plurale(len(isp_anno), 'time')}, with an average score of {num1(media_anno)}."
        corpo.append(f"""<section class="card key pull" aria-label="Cruise line summary">
<div class="key-top">{ico("ship")}<span>{h(L["nome"])}</span><span>{plurale(len(att), "ship")} inspected by the CDC</span></div>
<div class="key-body"><div class="key-main">{anello(float(media(ult)), "average") if len(att) > 1 else anello(ult[0])}<div><p class="k-lab">{"Average latest CDC score" if len(att) > 1 else "Latest CDC score"}</p>
<p class="k-txt">{txt}</p></div></div><div class="key-side">{side}</div></div></section>""")
        corpo.append(AD)
        corpo.append(f"<h2>CDC scores of every {h(L['nome'])} ship</h2>" if len(att) > 1 else f"<h2>CDC score of the {h(L['nome'])} ship</h2>")
        corpo.append(f'<p class="lead">Latest score of each ship on the CDC Green Sheet, from best to worst. Select a ship for its full history and the violations found.</p>' if len(att) > 1 else
                     f'<p class="lead">Select the ship for its full history and the violations found.</p>')
        corpo.append(tabella_navi(ordinate, colonne=("prec", "n")))
    else:
        corpo.append(f'<div class="card pull"><p class="lead" style="margin:0">None of the {h(L["nome"])} ships on this site is in the CDC’s current list: '
                     f'they no longer sail from U.S. ports, so their latest CDC scores may be old.</p></div>')
    if arch:
        corpo.append(f"<h2>Ships no longer in the CDC list</h2><p class='lead'>Last scores of {h(L['nome'])} ships that the CDC inspected since {FONTI['archiviate_dal'][:4]} but that are no longer on the Green Sheet.</p>")
        corpo.append(tabella_navi(arch, colonne=("n",)))
    # bocciature della compagnia (tutte le ispezioni del modulo con il nome CDC di questa compagnia)
    boc_tutte = [r for r in ISPEZIONI if r[1] < SOGLIA and comp_info(r[3])["slug"] == ls]
    if boc_tutte:
        corpo.append(f"<h2>Failed inspections</h2><p class='lead'>Every {h(L['nome'])} inspection with a score of 85 or lower in the CDC records, most recent first.</p>")
        corpo.append(tabella_ispezioni(boc_tutte, con_linea=False))
    else:
        corpo.append(f"<h2>Failed inspections</h2><p class='lead'>No {h(L['nome'])} inspection in the CDC records scored 85 or lower.</p>")
    ep = [e for e in EPIDEMIE if comp_info_da_nome(e["compagnia"]) == ls or (e.get("slug") and NAVI[e["slug"]]["linea"]["slug"] == ls)]
    if ep:
        def nave_ep(e):
            return f'<a href="/{url_nave(e["slug"])}">{h(NAVI[e["slug"]]["nome"])}</a>' if e.get("slug") else h(e["nave"])
        li = "".join(f'<li>{nave_ep(e)}: {h(e["date"])} · {h(e["agente"] or "unknown cause")}</li>' for e in ep)
        corpo.append(f'<h2>Outbreaks posted by the CDC</h2><p class="lead">Gastrointestinal illness outbreaks on {h(L["nome"])} ships posted by the CDC since 2023.</p><ul>{li}</ul>'
                     f'<p class="small"><a href="/outbreaks/">All cruise ship outbreaks</a></p>')
    cdc_nomi = sorted(L["cdc"])
    corpo.append(f'<p class="small">The CDC lists this cruise line as: {"; ".join("“" + h(x) + "”" for x in cdc_nomi)}.</p>')
    corpo.append(fonte_box())
    n_att = len(att)
    if n_att > 1:
        titolo = f"{L['nome']} CDC Inspection Scores ({ANNO}): All {n_att} Ships"
        if len(titolo) > 65:
            titolo = f"{L['nome']} CDC Inspection Scores: All {n_att} Ships"
        descr = (f"CDC sanitation scores of all {n_att} {L['nome']} ships, best to worst (average {num1(media(ult))}), "
                 f"plus every failed inspection. Official CDC data.")
    elif n_att == 1:
        nave1 = NAVI[att[0]]
        titolo = f"{L['nome']} CDC Inspection Score: {nave1['nome']} ({ult[0]}/100)"
        if len(titolo) > 65:
            titolo = f"{L['nome']} CDC Inspection Score ({ult[0]}/100)"
        descr = (f"{L['nome']}’s only ship on the CDC Green Sheet, {nave1['nome']}, scored {ult[0]}/100 ({data_breve(nave1['ultima'][0])}). "
                 f"Full history and failed inspections.")
    else:
        titolo = f"{L['nome']} CDC Inspection Scores (Archived Ships)"
        descr = (f"Last CDC sanitation scores of {L['nome']} ships no longer on the CDC Green Sheet, and every failed inspection of the line. Official CDC data.")
    testata = banda("Cruise line · CDC inspection scores", f"{L['nome']} CDC inspection scores",
                    (f"The latest CDC Vessel Sanitation Program score of every {h(L['nome'])} ship, with links to each ship’s history and reports." if n_att > 1 else
                     f"The CDC Vessel Sanitation Program scores of {h(L['nome'])}, with a link to the ship’s full history and reports."), trust())
    pagina(url_comp(ls, True), titolo, descr, "\n".join(corpo), briciole=[("Cruise lines", "cruise-lines/"), (L["nome"], url_comp(ls, True))], testata=testata, aff=True)


def comp_info_da_nome(nome_epid):
    """Le tabelle delle epidemie usano nomi commerciali ("Princess Cruises"): si confrontano con i nomi curati."""
    k = C_norm(nome_epid)
    for v in _COMP.values():
        if C_norm(v["nome"]) == k:
            return v["slug"]
    return ""


def pagina_linee():
    righe = []
    ordine = sorted(LINEE, key=lambda k: (-len(stats_linea(LINEE[k])[0]), LINEE[k]["nome"]))
    for k in ordine:
        L = LINEE[k]
        att, ult, _ = stats_linea(L)
        best = max(ult) if ult else None
        worst = min(ult) if ult else None
        righe.append(f'<tr><td class="t1"><a href="/{url_comp(k, True)}">{h(L["nome"])}</a></td><td class="x n" data-l="Ships">{len(att) or "–"}</td>'
                     f'<td class="x n" data-l="Best">{best if best is not None else "–"}</td><td class="x n" data-l="Lowest">{worst if worst is not None else "–"}</td>'
                     f'<td class="c sc-c">{chip_media(media(ult)) if ult else "<span class=small>archived</span>"}</td></tr>')
    tab = (f'<div class="tab"><table class="lt"><thead><tr><th>Cruise line</th><th class="n">Ships</th><th class="n">Best</th><th class="n">Lowest</th>'
           f'<th class="c">Average</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    top = [k for k in ordine if len(stats_linea(LINEE[k])[0]) >= 5]
    rank = sorted(top, key=lambda k: -media(stats_linea(LINEE[k])[1]))
    li = "".join(f'<li><a href="/{url_comp(k, True)}"><span>{h(LINEE[k]["nome"])}<small>{len(stats_linea(LINEE[k])[0])} ships</small></span>'
                 f'{chip_media(media(stats_linea(LINEE[k])[1]))}</a></li>' for k in rank)
    corpo = f"""<div class="card pull"><p class="lead" style="margin:0">{len(LINEE)} cruise lines have ships on this site. “Average” is the average of the latest CDC score of each ship of the line that is on the CDC Green Sheet, to one decimal place; lines with only archived ships show no average.</p></div>
{AD}
<h2>Largest cruise lines ranked by average score</h2>
<p class="lead">Cruise lines with at least five ships in the CDC list, from the highest average latest score to the lowest.</p>
<ul class="griglia">{li}</ul>
<h2>All cruise lines</h2>
{tab}
{fonte_box()}"""
    testata = banda("Cruise lines", "CDC inspection scores by cruise line",
                    "Average, best and lowest latest CDC sanitation scores of every cruise line that sails from U.S. ports.", trust())
    pagina("cruise-lines/", f"Cruise Line CDC Inspection Scores ({ANNO}): All {len(LINEE)} Lines Ranked",
           f"CDC sanitation inspection scores by cruise line: average, best and lowest latest score for Carnival, Royal Caribbean, Norwegian, Princess and {len(LINEE) - 4} more lines.",
           corpo, briciole=[("Cruise lines", "cruise-lines/")], testata=testata)


# ---------------------------------------------------------------- elenco navi
def pagina_navi():
    lettere = defaultdict(list)
    for s in ATTIVE:
        c = NAVI[s]["nome"][0].upper()
        lettere[c if c.isalpha() else "#"].append(s)
    indice = " ".join(f'<a href="#l-{k}">{k}</a>' for k in sorted(lettere))
    sezioni = "".join(f'<h2 id="l-{k}">{k}</h2>{tabella_navi(lettere[k])}' for k in sorted(lettere))
    arch = (f'<h2 id="archived">Ships no longer in the CDC list</h2><p class="lead">Ships inspected since {FONTI["archiviate_dal"][:4]} that are no longer on the CDC Green Sheet '
            f'(usually because they now sail outside the U.S.). Their last score may be old.</p>{tabella_navi(ARCHIVIATE)}') if ARCHIVIATE else ""
    corpo = f"""<div class="card pull cerca-card">{form_cerca()}</div>
<p class="small" style="margin-top:18px">Jump to: {indice}{' · <a href="#archived">archived ships</a>' if ARCHIVIATE else ''}</p>
{sezioni}
{arch}
{fonte_box()}"""
    testata = banda("All ships", f"CDC inspection scores of all {len(ATTIVE)} cruise ships",
                    f"Every ship on the CDC Green Sheet, A to Z, with its latest sanitation score and inspection date.", trust())
    pagina("ships/", f"All Cruise Ships' CDC Inspection Scores A–Z ({len(ATTIVE)} Ships)",
           f"Latest CDC sanitation inspection score of all {len(ATTIVE)} cruise ships in the CDC Vessel Sanitation Program, A to Z, with inspection dates and full histories.",
           corpo, briciole=[("Ships", "ships/")], testata=testata)


def form_cerca(etichetta="Find your ship"):
    return f"""<div data-cerca data-url="/data/ships.json"><form role="search" action="/ships/">
<label for="q">{ico("search")}{h(etichetta)}</label>
<div class="cerca-box">{ico("search")}<input id="q" class="cerca" type="search" name="q" placeholder="e.g. Wonder of the Seas" autocomplete="off" aria-describedby="q-hint"></div>
</form><div class="risultati" aria-live="polite"></div>
<p class="esempi" id="q-hint">Type part of the name. Try <em>Carnival Breeze</em>, <em>Norwegian Dawn</em> or <em>Disney Wish</em>.</p></div>"""


# ---------------------------------------------------------------- classifiche e anni
def pagina_perfetti(y):
    righe = [r for r in ISPEZIONI if r[0][:4] == str(y) and r[1] == 100]
    navi_set = {r[4] or r[2] for r in righe}
    tot = sum(1 for r in ISPEZIONI if r[0][:4] == str(y))
    corpo = f"""<div class="card pull"><p class="lead" style="margin:0">In {y}{" so far" if y == ANNO else ""} the CDC recorded <strong>{plurale(len(righe), "perfect score")}</strong> of 100, out of {plurale(tot, "inspection")}: {plurale(len(navi_set), "ship")} had at least one inspection with no points deducted.</p></div>
{AD}
<h2>Every 100 in {y}</h2>
{tabella_ispezioni(righe) if righe else '<p class="lead">No inspection scored 100 this year.</p>'}
<p class="small">The CDC also keeps its own list of <a href="{CDC_100}" rel="noopener">ships that scored 100 in the last 365 days</a>.</p>
{fonte_box()}"""
    testata = banda(f"Rankings · {y}", f"Cruise ships with a perfect 100 CDC score in {y}",
                    f"Every CDC Vessel Sanitation Program inspection that ended with no points deducted in {y}.", trust())
    pagina(f"rankings/perfect-scores-{y}/", f"Cruise Ships With a Perfect 100 CDC Score in {y} ({len(navi_set)} Ships)",
           f"{len(navi_set)} cruise ships scored a perfect 100 in a CDC sanitation inspection in {y}{' so far' if y == ANNO else ''}. Full list with dates and cruise lines, from official CDC data.",
           corpo, briciole=[("Rankings", "rankings/"), (f"Perfect scores {y}", f"rankings/perfect-scores-{y}/")], testata=testata)


def bassi(y):
    """Le 25 ispezioni con il voto più basso dell'anno, più quelle a pari merito con la venticinquesima."""
    righe = sorted((r for r in ISPEZIONI if r[0][:4] == str(y)), key=lambda r: (r[1], r[0]))
    if not righe:
        return righe, []
    limite = righe[min(24, len(righe) - 1)][1]
    return righe, [r for r in righe if r[1] <= limite]


def pagina_bassi(y):
    righe, scelte = bassi(y)
    if not righe:
        return
    boc = [r for r in righe if r[1] < SOGLIA]
    corpo = f"""<div class="card pull"><p class="lead" style="margin:0">The {len(scelte)} lowest CDC inspection scores of {y}{" so far" if y == ANNO else ""}, out of {plurale(len(righe), "inspection")}{" (ties included)" if len(scelte) > 25 else ""}. {plurale(len(boc), "inspection")} scored 85 or lower and failed.</p></div>
{AD}
<h2>Lowest scores of {y}</h2>
{tabella_ispezioni(scelte)}
{fonte_box()}"""
    testata = banda(f"Rankings · {y}", f"Lowest cruise ship CDC inspection scores of {y}",
                    f"The worst CDC Vessel Sanitation Program scores of {y}. Ships fail with 85 or lower.", trust())
    pagina(f"rankings/lowest-scores-{y}/", f"Lowest Cruise Ship CDC Inspection Scores of {y}",
           f"The {len(scelte)} lowest CDC cruise ship sanitation scores of {y}{' so far' if y == ANNO else ''}, from {scelte[0][1]} up, with {plurale(len(boc), 'failed inspection')}. Official CDC data.",
           corpo, briciole=[("Rankings", "rankings/"), (f"Lowest scores {y}", f"rankings/lowest-scores-{y}/")], testata=testata)


def pagina_bocciate():
    righe = [r for r in ISPEZIONI if r[1] < SOGLIA]
    per_anno = defaultdict(list)
    for r in righe:
        per_anno[int(r[0][:4])].append(r)
    sezioni = "".join(f'<h2 id="y{y}">{y} <span class="small">({plurale(len(per_anno[y]), "failed inspection")})</span></h2>{tabella_ispezioni(per_anno[y])}' for y in sorted(per_anno, reverse=True))
    ultima = righe[0] if righe else None
    corpo = f"""<div class="card pull"><p class="lead" style="margin:0">The CDC records list <strong>{plurale(len(righe), "failed inspection")}</strong> (score of 85 or lower) since {min(per_anno)}.{f" The most recent: {h(NAVI[ultima[4]]['nome'] if ultima[4] else ultima[2])}, {ultima[1]} on {data_lunga(ultima[0])}." if ultima else ""} A failed ship must correct the violations and is reinspected “within a reasonable period” (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</p></div>
{AD}
<p class="small" style="margin-top:18px">Jump to: {" ".join(f'<a href="#y{y}">{y}</a>' for y in sorted(per_anno, reverse=True))}</p>
{sezioni}
<p class="small">Older records may be incomplete: the CDC search tool only keeps the history of ships that are still in its list.</p>
{fonte_box()}"""
    testata = banda("Rankings", "Cruise ships that failed a CDC inspection",
                    "Every cruise ship inspection with a score of 85 or lower in the CDC Vessel Sanitation Program records, most recent first.", trust())
    pagina("rankings/failed-inspections/", "Cruise Ships That Failed a CDC Health Inspection (Full List)",
           f"All {len(righe)} failed CDC cruise ship sanitation inspections (85 or lower) since {min(per_anno)}, by year, with ship, cruise line, date and score.",
           corpo, briciole=[("Rankings", "rankings/"), ("Failed inspections", "rankings/failed-inspections/")], testata=testata)


def pagina_classifiche():
    voci = []
    for y in ANNI_CLASSIFICHE:
        voci.append((f"rankings/perfect-scores-{y}/", f"Perfect 100 scores in {y}", f"{sum(1 for r in ISPEZIONI if r[0][:4] == str(y) and r[1] == 100)} inspections"))
        voci.append((f"rankings/lowest-scores-{y}/", f"Lowest scores of {y}", f"{len(bassi(y)[1])} lowest, {bassi(y)[1][-1][1]} or below" if bassi(y)[1] else ""))
    voci.append(("rankings/failed-inspections/", "All failed inspections", f"{sum(1 for r in ISPEZIONI if r[1] < SOGLIA)} since {min(int(r[0][:4]) for r in ISPEZIONI if r[1] < SOGLIA)}"))
    voci.append(("cruise-lines/", "Cruise lines ranked by average score", f"{len(LINEE)} lines"))
    voci.append(("outbreaks/", "Gastrointestinal illness outbreaks", "posted by the CDC since 2023"))
    li = "".join(f'<li><a href="/{u}"><span>{h(t)}<small>{h(s)}</small></span>{ico("arrow")}</a></li>' for u, t, s in voci)
    att = [NAVI[s]["ultima"][1] for s in ATTIVE]
    top = sorted(ATTIVE, key=lambda s: (-NAVI[s]["ultima"][1], NAVI[s]["ultima"][0]))
    peggiori = sorted(ATTIVE, key=lambda s: (NAVI[s]["ultima"][1], NAVI[s]["ultima"][0]))[:10]
    corpo = f"""<div class="pull"><ul class="griglia">{li}</ul></div>
{AD}
<h2>Lowest latest scores right now</h2>
<p class="lead">The ten ships on the CDC Green Sheet with the lowest latest score. Average latest score of all {len(att)} ships: {num1(media(att))}.</p>
{tabella_navi(peggiori)}
<h2>Ships whose latest score is 100</h2>
<p class="lead">{plurale(sum(1 for v in att if v == 100), "ship")} on the Green Sheet scored 100 at their latest inspection.</p>
<ul class="griglia">{"".join(f'<li><a href="/{url_nave(s)}"><span>{h(NAVI[s]["nome"])}<small>{h(NAVI[s]["linea"]["nome"])} · {data_breve(NAVI[s]["ultima"][0])}</small></span>{chip(100)}</a></li>' for s in top if NAVI[s]["ultima"][1] == 100)}</ul>
{fonte_box()}"""
    testata = banda("Rankings", "Cruise ship CDC score rankings", "Perfect scores, the lowest scores and every failed inspection, from official CDC data.", trust())
    pagina("rankings/", f"Cruise Ship CDC Inspection Rankings {ANNO}: Best and Worst Scores",
           f"Rankings of CDC cruise ship sanitation scores: ships with a perfect 100 in {ANNO}, the lowest scores, failed inspections and cruise lines ranked by average.",
           corpo, briciole=[("Rankings", "rankings/")], testata=testata)


def pagina_anno(y):
    righe = [r for r in ISPEZIONI if r[0][:4] == str(y)]
    voti = [r[1] for r in righe]
    navi_set = {r[4] or r[2] for r in righe}
    boc = [r for r in righe if r[1] < SOGLIA]
    stat = [(intero(len(righe)), "inspections"), (intero(len(navi_set)), "ships inspected"), (num1(media(voti)), "average score"),
            (intero(sum(1 for v in voti if v == 100)), "perfect scores (100)")]
    stats = "".join(f'<div class="stat"><b>{a}</b><span>{b}</span></div>' for a, b in stat)
    mesi = Counter(int(r[0][5:7]) for r in righe)
    nota_vecchio = ('<p class="small">For earlier years the CDC search tool only shows ships that are still in its list, so the totals undercount the inspections of that year.</p>'
                    if y < ANNO - 3 else "")
    nota_covid = ('<div class="nota">' + ico("info") + f'<p>Few inspections in {y}: cruising from U.S. ports was largely suspended during the COVID-19 pandemic, '
                  'and the CDC records show no inspections at all in 2021.</p></div>' if y in (2020, 2021, 2022) else "")
    link_cl = (f'<p>See also: <a href="/rankings/perfect-scores-{y}/">perfect scores of {y}</a> · <a href="/rankings/lowest-scores-{y}/">lowest scores of {y}</a></p>'
               if y in ANNI_CLASSIFICHE else "")
    corpo = f"""<div class="stat-row pull">{stats}</div>
<p class="lead">{plurale(len(boc), "inspection")} failed (85 or lower){": " + h(elenco_nomi([(NAVI[r[4]]["nome"] if r[4] else r[2]) + f" ({r[1]})" for r in boc], 6)) if boc else ""}. The busiest month was {MESI[mesi.most_common(1)[0][0] - 1] if mesi else "–"}.</p>
{nota_covid}{nota_vecchio}{link_cl}
{AD}
<h2>All CDC inspections of {y}</h2>
{tabella_ispezioni(righe)}
{fonte_box()}"""
    altri = " · ".join(f'<a href="/years/{a}/">{a}</a>' for a in ANNI if a != y)
    corpo += f'<p class="small" style="margin-top:18px">Other years: {altri}</p>'
    testata = banda(f"Scores by year · {y}", f"Cruise ship sanitation scores {y}",
                    f"Every CDC Vessel Sanitation Program inspection of {y}{' so far' if y == ANNO else ''}, most recent first.", trust())
    pagina(f"years/{y}/", f"Cruise Ship Sanitation Scores {y}: All {len(righe)} CDC Inspections",
           f"All {len(righe)} CDC cruise ship sanitation inspections of {y}{' so far' if y == ANNO else ''}: average score {num1(media(voti))}, {len(boc)} failed, "
           f"{sum(1 for v in voti if v == 100)} perfect scores. Ship, cruise line, date and score.",
           corpo, briciole=[("Scores by year", "years/"), (str(y), f"years/{y}/")], testata=testata)


def pagina_anni():
    righe = "".join(f'<tr><td class="t1"><a href="/years/{y}/">{y}</a></td><td class="x n" data-l="Inspections">{ANNI_ISP[y]}</td>'
                    f'<td class="x n" data-l="Failed">{sum(1 for r in ISPEZIONI if r[0][:4] == str(y) and r[1] < SOGLIA)}</td>'
                    f'<td class="c sc-c">{chip_media(media([r[1] for r in ISPEZIONI if r[0][:4] == str(y)]))}</td></tr>' for y in ANNI)
    corpo = f"""<div class="card pull"><p class="lead" style="margin:0">Number of CDC inspections, failed inspections and average score for each year from {ANNI[-1]} to {ANNI[0]}. Older years undercount: the CDC tool only keeps ships still in its list.</p></div>
<div class="tab" style="margin-top:24px"><table class="lt"><thead><tr><th>Year</th><th class="n">Inspections</th><th class="n">Failed</th><th class="c">Average</th></tr></thead><tbody>{righe}</tbody></table></div>
{fonte_box()}"""
    testata = banda("Scores by year", "Cruise ship CDC inspection scores by year", "Every CDC Vessel Sanitation Program inspection, year by year.", trust())
    pagina("years/", f"Cruise Ship CDC Inspection Scores by Year ({ANNI[-1]}–{ANNI[0]})",
           f"CDC cruise ship sanitation inspections year by year from {ANNI[-1]} to {ANNI[0]}: number of inspections, failures and average score, with every inspection listed.",
           corpo, briciole=[("Scores by year", "years/")], testata=testata)


# ---------------------------------------------------------------- epidemie
def pagina_epidemie():
    per_anno = defaultdict(list)
    for e in EPIDEMIE:
        per_anno[e["anno"]].append(e)
    sezioni = []
    for y in sorted(per_anno, reverse=True):
        con_casi = any(e.get("passeggeri") for e in per_anno[y])
        righe = []
        for e in per_anno[y]:
            nave = f'<a href="/{url_nave(e["slug"])}">{h(e["nave"])}</a>' if e.get("slug") else h(e["nave"])
            casi = (f'<td class="x" data-l="Ill passengers">{h(e.get("passeggeri", ""))}</td><td class="x" data-l="Ill crew">{h(e.get("equipaggio", ""))}</td>' if con_casi else "")
            fonte = f'<a href="{h(e["url"])}" rel="noopener">CDC</a>' if e.get("url") else ""
            righe.append(f'<tr><td class="t1">{nave}<br><span class="small">{h(e["compagnia"])}</span></td><td class="x" data-l="Sailing">{h(e["date"])}</td>'
                         f'<td class="x" data-l="Cause">{h(e["agente"])}</td>{casi}<td class="x">{fonte}</td></tr>')
        th = "<th>Ship</th><th>Sailing dates</th><th>Cause</th>" + ("<th>Ill passengers</th><th>Ill crew</th>" if con_casi else "") + "<th>Details</th>"
        sezioni.append(f'<h2 id="y{y}">{y} <span class="small">({plurale(len(per_anno[y]), "outbreak")})</span></h2>'
                       f'<div class="tab"><table class="lt"><thead><tr>{th}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    anni = sorted(per_anno)
    ult = EPIDEMIE[0] if EPIDEMIE else None
    corpo = f"""<div class="card pull"><p class="lead" style="margin:0">The CDC posts an outbreak when a ship in its jurisdiction has 3% or more of passengers or crew reporting gastrointestinal symptoms to the ship’s medical staff, and “may also post other outbreaks of public health significance”. {plurale(len(EPIDEMIE), "outbreak")} were posted from {anni[0]} to {anni[-1]}{f"; the most recent on {h(ult['nave'])} ({h(ult['date'])})" if ult else ""}.</p></div>
{AD}
<div class="nota">{ico("info")}<p>An outbreak is not the same as a failed inspection: the inspection score measures sanitation on the day of the inspection; an outbreak counts people who got sick on one voyage. Illnesses such as norovirus “can spread quickly in closed and semienclosed environments, such as cruise ships” (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</p></div>
{"".join(sezioni)}
<p class="small">The CDC tables list outbreaks posted on {h(CDC_EPID)} (current year), the earlier-outbreaks pages for 2025–2024 and 2023. Case counts are shown only where the CDC table includes them. Tables checked on {data_lunga(INFO_IL.get("epidemie", CONTROLLATO))}.</p>
{fonte_box(extra=f'<li><a href="{CDC_EPID}" rel="noopener">CDC: Outbreaks on cruise ships in VSP’s jurisdiction</a>, <a href="{CDC_EPID_PREC}" rel="noopener">2025–2024</a> and <a href="{CDC_EPID_2023}" rel="noopener">2023</a>.</li>')}"""
    testata = banda("Outbreaks", f"Cruise ship norovirus and GI outbreaks, {anni[0]}–{anni[-1]}",
                    "Gastrointestinal illness outbreaks on cruise ships posted by the CDC Vessel Sanitation Program, with cause and sailing dates.", trust())
    pagina("outbreaks/", f"Cruise Ship Norovirus Outbreaks {anni[-1]} (and Since {anni[0]}): CDC List",
           f"All {len(EPIDEMIE)} cruise ship gastrointestinal illness outbreaks posted by the CDC since {anni[0]}: ship, cruise line, sailing dates and cause (norovirus, E. coli and others).",
           corpo, briciole=[("Outbreaks", "outbreaks/")], testata=testata)


# ---------------------------------------------------------------- home
def home():
    att = [NAVI[s]["ultima"][1] for s in ATTIVE]
    anno_r = [r for r in ISPEZIONI if r[0][:4] == str(ANNO)]
    boc_ora = [s for s in ATTIVE if not passata(NAVI[s]["ultima"][1])]
    cento_anno = [r for r in anno_r if r[1] == 100]
    ultime = ISPEZIONI[:12]
    stats = [(intero(len(ATTIVE)), "ships on the CDC Green Sheet", "/ships/"), (num1(media(att)), "average latest score", "/rankings/"),
             (intero(len(anno_r)), f"inspections in {ANNO} so far", f"/years/{ANNO}/"),
             (intero(len({r[4] or r[2] for r in cento_anno})), f"ships with a perfect 100 in {ANNO}", f"/rankings/perfect-scores-{ANNO}/")]
    stats_html = "".join(f'<div class="stat"><a href="{u}"><b>{a}</b><span>{b}</span></a></div>' for a, b, u in stats)
    li_ult = "".join(f'<li><a href="/{url_nave(r[4])}"><span>{h(NAVI[r[4]]["nome"])}<small>{h(nome_comp(r[3]))} · {data_breve(r[0])}</small></span>{chip(r[1])}</a></li>'
                     if r[4] else f'<li><a href="/years/{r[0][:4]}/"><span>{h(r[2])}<small>{data_breve(r[0])}</small></span>{chip(r[1])}</a></li>' for r in ultime)
    boc_anno = [r for r in anno_r if r[1] < SOGLIA]
    blocco_boc = (f'<h2>Failed inspections in {ANNO}</h2><p class="lead">{plurale(len(boc_anno), "inspection")} scored 85 or lower in {ANNO} so far.</p>{tabella_ispezioni(boc_anno)}'
                  if boc_anno else f'<h2>Failed inspections in {ANNO}</h2><p class="lead">No ship has failed a CDC inspection in {ANNO} so far.</p>')
    if boc_ora:
        blocco_boc += (f'<p class="small">Ships whose latest score on the Green Sheet is a fail: '
                       + ", ".join(f'<a href="/{url_nave(s)}">{h(NAVI[s]["nome"])}</a> ({NAVI[s]["ultima"][1]}, {data_breve(NAVI[s]["ultima"][0])})' for s in boc_ora) + ".</p>")
    linee_top = sorted((k for k in LINEE if stats_linea(LINEE[k])[0]), key=lambda k: (-len(stats_linea(LINEE[k])[0]), LINEE[k]["nome"]))[:12]
    li_linee = "".join(f'<li><a href="/{url_comp(k, True)}"><span>{h(LINEE[k]["nome"])}<small>{len(stats_linea(LINEE[k])[0])} ships · average</small></span>'
                       f'{chip_media(media(stats_linea(LINEE[k])[1]))}</a></li>' for k in linee_top)
    faq = [
        ("What is a passing CDC score for a cruise ship?",
         f"Ships are scored out of 100. A score of 86 or higher passes; the CDC says that scores of 85 or lower are “not satisfactory” and counts them as a failed inspection (<a href=\"{CDC_FAQ}\" rel=\"noopener\">CDC FAQ</a>)."),
        ("How often are cruise ships inspected?",
         f"Cruise ships under the CDC’s jurisdiction (international voyages with a stop at a U.S. port) are subject to two unannounced inspections each year, done while the ship is in a U.S. port (<a href=\"{CDC_FAQ}\" rel=\"noopener\">CDC FAQ</a>, <a href=\"{CDC_ISP}\" rel=\"noopener\">CDC</a>)."),
        ("Does a low score mean a ship is unsafe?",
         "Not on its own. The score shows how well the ship met the CDC’s sanitation standards on the day of the inspection. It is not a safety rating and it cannot tell you whether you will get sick. Read the findings to see what the inspectors actually saw."),
        ("Why can’t I find my ship?",
         f"The CDC only covers cruise ships on international voyages with a stop at a U.S. port. Ships that sail outside the United States for an extended period drop out of the CDC database and are added back when they return and are inspected (<a href=\"{CDC_FAQ}\" rel=\"noopener\">CDC FAQ</a>)."),
    ]
    faq_html = "".join(f"<details><summary>{h(q)}</summary><p>{a}</p></details>" for q, a in faq)
    corpo = f"""<div class="card pull cerca-card">{form_cerca()}</div>
<div class="stat-row" style="margin-top:16px">{stats_html}</div>
{AD}
<h2>How to read a CDC score</h2>
<p class="lead">CDC inspectors start from 100 and deduct points for violations of the Vessel Sanitation Program standards, in eight areas from the galleys to the pools and the medical center. A ship fails with 85 or lower.</p>
{scala_voti()}
<h2>Latest inspections</h2>
<p class="lead">The 12 most recent inspections published by the CDC, checked on {data_lunga(CONTROLLATO)}.</p>
<p class="small">{RITARDO}</p>
<ul class="griglia">{li_ult}</ul>
{blocco_boc}
<h2>Cruise lines</h2>
<p class="lead">Average latest score of the largest cruise lines. <a href="/cruise-lines/">All {len(LINEE)} cruise lines</a>.</p>
<ul class="griglia">{li_linee}</ul>
<h2>Rankings and lists</h2>
<ul class="griglia">
<li><a href="/rankings/perfect-scores-{ANNO}/"><span>Perfect 100 scores in {ANNO}<small>{len(cento_anno)} inspections</small></span>{ico("trophy")}</a></li>
<li><a href="/rankings/lowest-scores-{ANNO}/"><span>Lowest scores of {ANNO}<small>every score of {bassi(ANNO)[1][-1][1]} or below</small></span>{ico("down")}</a></li>
<li><a href="/rankings/failed-inspections/"><span>All failed inspections<small>since {min(int(r[0][:4]) for r in ISPEZIONI if r[1] < SOGLIA)}</small></span>{ico("alert")}</a></li>
<li><a href="/years/{ANNO}/"><span>Cruise ship sanitation scores {ANNO}<small>every inspection</small></span>{ico("calendar")}</a></li>
<li><a href="/outbreaks/"><span>Norovirus and GI outbreaks<small>posted by the CDC since 2023</small></span>{ico("virus")}</a></li>
<li><a href="/how-cdc-cruise-ship-inspections-work/"><span>How CDC inspections work<small>what inspectors check</small></span>{ico("info")}</a></li>
</ul>
<h2>Questions</h2>
<div class="faq">{faq_html}</div>
{fonte_box()}"""
    testata = banda("CDC Vessel Sanitation Program data", "Cruise ship health inspection scores",
                    f"The latest CDC sanitation score of all {len(ATTIVE)} cruise ships that sail from U.S. ports, with every past inspection and the violations inspectors found.", trust())
    pagina("", f"Cruise Ship CDC Inspection Scores {ANNO}: Health Score of Every Ship",
           f"Look up the CDC sanitation score of any cruise ship: the latest score of all {len(ATTIVE)} ships, every past inspection, violations, and the {ANNO} fails and 100s.",
           corpo, testata=testata, aff=True,
           jsonld_extra={"@context": "https://schema.org", "@type": "Dataset", "name": "Cruise ship CDC inspection scores",
                         "description": "Latest and past CDC Vessel Sanitation Program inspection scores of cruise ships that sail from U.S. ports, republished from the CDC Inspection Query Tool.",
                         "url": URL_SITO + "/", "isBasedOn": CDC_TOOL, "license": "https://www.usa.gov/government-works",
                         "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
                         "temporalCoverage": f"{FONTI['prima_ispezione'][:4]}/{FONTI['green_sheet']['ultima_ispezione'][:10]}", "dateModified": CONTROLLATO})


# ---------------------------------------------------------------- guida
def guida():
    il = data_lunga(INFO_IL.get("faq", CONTROLLATO))
    corpo = f"""<div class="testo">
<div class="card pull"><p class="lead" style="margin:0"><strong>In short:</strong> cruise ships on international voyages that stop at a U.S. port are subject to two unannounced CDC inspections a year. Inspectors score the ship out of 100, deducting points for violations in areas such as food safety, drinking water, pools and illness control. A ship fails with 85 or lower.</p></div>
{AD}
<h2>Who inspects cruise ships</h2>
<p>The <a href="{CDC_ABOUT}" rel="noopener">Vessel Sanitation Program</a> (VSP) of the Centers for Disease Control and Prevention “helps the cruise industry prevent and control public health issues”. According to the CDC, it does this by inspecting cruise ships, monitoring illness data and responding to outbreaks, reviewing ship design and construction plans, and training cruise ship staff. It covers “cruise ships with international voyages with a stop at a U.S. port” (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</p>
<h2>How often, and how</h2>
<ul>
<li><strong>Twice a year, unannounced.</strong> Cruise ships under the CDC’s jurisdiction “are subject to two unannounced inspections each year”. A ship that sails outside the United States for an extended period may not be inspected twice a year; it is inspected again when it returns (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</li>
<li><strong>In a U.S. port, in 6 to 8 hours.</strong> Inspections are done while the ship is in a U.S. port and usually take 6 to 8 hours, depending on the number of inspectors, the size of the ship, its time in port and the issues found (<a href="{CDC_ISP}" rel="noopener">CDC</a>). One to five inspectors take part, depending on the size of the ship (<a href="{CDC_AREE}" rel="noopener">CDC</a>).</li>
<li><strong>The ship owner pays.</strong> Owners pay a fee based on the ship’s size for each inspection and reinspection, from $8,073 for ships under 30,000 gross tons to $64,584 for ships over 180,000 gross tons (<a href="{CDC_ISP}" rel="noopener">CDC fee schedule</a>).</li>
</ul>
<h2>The eight areas inspectors check</h2>
<p>According to the <a href="{CDC_AREE}" rel="noopener">CDC</a>, inspectors evaluate eight areas:</p>
<ol>
<li><strong>Medical center</strong>: records of people who reported diarrhea or vomiting, specimen collection supplies, and interviews to check that no crew member works while sick.</li>
<li><strong>Drinking water</strong>: halogen (chlorine) and pH logs since the last inspection, the water system itself and water samples.</li>
<li><strong>Galleys and dining rooms</strong>: how food is stored, prepared and served, dishwashers and other equipment, what food workers know about safe food handling, and their health and hygiene.</li>
<li><strong>Swimming pools and whirlpools</strong>: logs, water samples, and the staff’s procedure for accidents involving feces or vomit.</li>
<li><strong>Housekeeping</strong>: the outbreak prevention and response plan, and the disinfection of public areas.</li>
<li><strong>Pest and insect management</strong>: the ship’s pest management plan and what staff know about it.</li>
<li><strong>Child activity centers</strong>: diaper-changing, toilet and handwashing facilities, clean toys, and what staff do when a child is sick.</li>
<li><strong>Heating, ventilation and air conditioning</strong>: that units are clean and that water does not collect inside them.</li>
</ol>
<h2>How the score works</h2>
<p>Inspectors use the VSP Environmental Public Health Standards and a 100-point scale. They “deduct points for a single, significant violation or for patterns of similar violations”, and “cruise ships fail inspections when they score 85 or below” (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>). The CDC <a href="{CDC_GREEN}" rel="noopener">Green Sheet</a> says the same: scores of 85 or lower “are NOT satisfactory”.</p>
{scala_voti()}
<p>Each CDC report lists the findings by <em>item number</em> of the standards (for example item 10, “RWF maintenance, safety equipment”, where RWF means recreational water facilities, or item 33, “Decks / bulkheads / deckheads construction, repair, clean”), the place on the ship and what the inspector saw. The CDC summary of the same inspection shows the points deducted for each item, and the score is 100 minus those points. Many findings are written down without a deduction, so even a ship that scored 100 can have findings. On this site every ship page shows both, for the last {FONTI["n_rapporti"]} inspections.</p>
<h2>After the inspection</h2>
<ul>
<li>Cruise ships must correct all violations, and certain critical violations immediately. Each ship then submits a <em>corrective action statement</em> describing how the violations were corrected (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</li>
<li>A ship that fails is reinspected “within a reasonable period”. The CDC can recommend that a ship not sail, but says this is “rarely needed” and that it would only do so for imminent public health risks (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</li>
</ul>
<h2>What a score does not tell you</h2>
<ul>
<li><strong>It describes one inspection.</strong> The CDC inspects ships “to determine how well they are operating and maintaining public health standards” (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>), on the day the inspectors are on board. A score does not describe the rest of the year.</li>
<li><strong>It is not a safety rating.</strong> The areas the CDC checks are the eight listed above. Fire safety, navigation and security are not among them, so a CDC score does not tell you whether a ship is safe.</li>
<li><strong>Outbreaks are posted separately.</strong> The CDC posts a gastrointestinal illness outbreak when 3% or more of passengers or crew on a voyage report symptoms to the ship’s medical staff, and may also post other outbreaks of public health significance (<a href="{CDC_EPID}" rel="noopener">CDC</a>). See our <a href="/outbreaks/">list of outbreaks</a>.</li>
<li><strong>Some ships are missing.</strong> Ships outside the CDC’s jurisdiction are not inspected, and ships that sail outside the United States for an extended period do not appear in the CDC database until they return (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>).</li>
</ul>
<h2>Staying healthy on board</h2>
<p>The CDC’s advice to passengers: tell the ship’s medical center if you are sick, wash your hands often rather than relying on hand sanitizer, drink plenty of water and get plenty of rest, and leave the area if you see someone get sick (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>, <a href="{CDC_SUGGERIMENTI}" rel="noopener">tips for healthy cruising</a>).</p>
<p class="small">All quotations come from the CDC pages linked above, checked on {il}.</p>
</div>
{fonte_box(extra=f'<li>CDC Vessel Sanitation Program pages: <a href="{CDC_ABOUT}" rel="noopener">about VSP</a>, <a href="{CDC_FAQ}" rel="noopener">FAQ</a>, <a href="{CDC_ISP}" rel="noopener">public health operational inspections</a>, <a href="{CDC_AREE}" rel="noopener">the eight areas inspected</a>, <a href="{CDC_EPID}" rel="noopener">outbreaks</a>, checked on {il}.</li>')}"""
    testata = banda("Guide", "How CDC cruise ship inspections work",
                    "Who inspects cruise ships, how often, what inspectors check, how the 100-point score works and what a failed inspection means.", piatta=False)
    pagina("how-cdc-cruise-ship-inspections-work/", "How CDC Cruise Ship Inspections Work (and Why 86 Is a Pass)",
           "How the CDC inspects cruise ships: two unannounced inspections a year, eight areas checked, a 100-point score, and what happens when a ship scores 85 or lower.",
           corpo, briciole=[("How inspections work", "how-cdc-cruise-ship-inspections-work/")], testata=testata,
           jsonld_extra={"@context": "https://schema.org", "@type": "Article", "headline": "How CDC cruise ship inspections work",
                         "image": URL_SITO + "/assets/og.png", "datePublished": "2026-10-17", "dateModified": CONTROLLATO, "author": {"@type": "Organization", "name": NOME},
                         "publisher": {"@type": "Organization", "name": NOME}, "mainEntityOfPage": URL_SITO + "/how-cdc-cruise-ship-inspections-work/"})


# ---------------------------------------------------------------- pagine fisse
def metodologia():
    f = FONTI
    corpo = f"""<div class="testo">
<h2>Where the data comes from</h2>
<p>Every score and finding on this site comes from the <a href="{CDC_TOOL}" rel="noopener">CDC Vessel Sanitation Program Inspection Query Tool</a>, read on {data_lunga(CONTROLLATO)}:</p>
<ul>
<li>the <a href="{CDC_GREEN}" rel="noopener">Green Sheet</a>, which shows “the most recent inspection score for each ship in VSP jurisdiction” ({f["green_sheet"]["navi"]} ships; latest inspection on {data_lunga(f["green_sheet"]["ultima_ispezione"])});</li>
<li>the <a href="{CDC_SEARCH}" rel="noopener">inspection search</a>, which lists {f["modulo"]["navi"]} ships and {f["modulo"]["compagnie"]} cruise lines; for each ship we ask for “All Dates” and record every inspection with its date, score and cruise line ({intero(len(ISPEZIONI))} inspections, the oldest from {f["prima_ispezione"][:4]});</li>
<li>the inspection report and summary of the last {f["n_rapporti"]} inspections of each ship on this site ({intero(f["rapporti"])} reports): the findings (item, place on the ship, violation) and the points deducted for each item.</li>
</ul>
<p>The explanations of how inspections work quote the CDC’s <a href="{CDC_FAQ}" rel="noopener">FAQ</a> and VSP pages; the outbreak list comes from the CDC’s <a href="{CDC_EPID}" rel="noopener">outbreak pages</a>. CDC data is a work of the U.S. government and in the public domain.</p>
<h2>Which ships have a page</h2>
<ul>
<li><strong>Every ship on the Green Sheet</strong> ({f["pubblicate"]["attive"]} ships), the CDC’s list of ships in its jurisdiction. A few of them have not been inspected for more than a year (for example because they sailed outside the United States); their pages say so.</li>
<li><strong>Archived ships</strong> ({f["pubblicate"]["archiviate"]} ships): ships that are still in the CDC search but no longer on the Green Sheet, only if their last inspection was on or after {data_lunga(f["archiviate_dal"])} and they have at least {f["archiviate_min"]} inspections. Older archived ships are left out: their records are years old and a page would say little that is useful. They still count in the yearly totals and in the list of failed inspections.</li>
</ul>
<h2>Pass and fail</h2>
<p>The CDC says that “cruise ships fail inspections when they score 85 or below” (<a href="{CDC_FAQ}" rel="noopener">CDC FAQ</a>), and its Green Sheet says that scores of 85 or lower “are NOT satisfactory”. So we show 86 or more as <strong>Passed</strong> and 85 or lower as <strong>Failed</strong>. The color bands (100, 95–99, 90–94, 86–89) are ours, to make lists easier to scan.</p>
<h2>How we check our reading</h2>
<ul>
<li>For every report we check that 100 minus the points in the CDC summary equals the score, and that the date and score match the ship’s inspection history and the Green Sheet.</li>
<li>Before each update is published, an automatic check reloads the CDC pages of 15 ships picked at random and compares them with this site.</li>
</ul>
<h2>Changes we make to the CDC text</h2>
<ul>
<li>In the CDC database many apostrophes and degree signs have turned into question marks (“manufacturer?s”, “128?F”). We restore them only where the meaning is obvious.</li>
<li>We do not publish names of people. If a finding contains what looks like a personal name, we replace it with “[name removed]”.</li>
<li>We group findings by the area written at the start of the CDC “site” field (for example “Galley”, “Potable Water”, “Recreational Water Facilities”) and give some areas a plainer name.</li>
<li>We leave out the CDC’s recommendation for each finding (it repeats the text of the standard) and the corrective action statements; both are in the CDC reports.</li>
<li>Cruise line names are shortened (for example “Carnival Cruise Lines, Inc.” becomes “Carnival Cruise Line”), and companies the CDC lists under more than one name (such as the three Viking companies) share one page. Each cruise line page shows the CDC names.</li>
</ul>
<h2>Limits</h2>
<ul>
<li><strong>A score is not a safety rating.</strong> It shows how a ship met the CDC’s sanitation standards on the day of the inspection. It says nothing about fire safety, navigation or security, and it cannot tell you whether you will get sick.</li>
<li><strong>Older years are incomplete.</strong> The CDC tool only keeps the history of ships still in its list; ships that left the U.S. market for good are not searchable, so yearly totals before {ANNO - 3} undercount.</li>
<li><strong>Delays.</strong> Inspections appear here only after the CDC publishes them, and the CDC does not say how long that takes. On {data_lunga(CONTROLLATO)} the most recent inspection in the CDC records was from {data_lunga(ULTIMA_CDC)}, so recent inspections may be missing. We check the CDC every week; a newly published inspection appears here within about a week.</li>
<li><strong>Errors.</strong> We read the CDC pages automatically. If something looks wrong, the CDC record is the official one: <a href="/contact/?ref=methodology">tell us</a> and we will fix it.</li>
</ul>
<h2>Updates</h2>
<p>Data checked on {data_lunga(CONTROLLATO)}; pages built on {data_lunga(OGGI.isoformat())}. We check the Green Sheet every week and download the new reports.</p>
</div>"""
    testata = banda("Methodology", "How we read the CDC data", "Sources, which ships get a page, how we check the numbers and what we change in the CDC text.", piatta=True)
    pagina("methodology/", f"Methodology and Sources | {NOME}",
           "How Cruise Health Scores reads the CDC Vessel Sanitation Program Green Sheet, inspection history and reports, and how every number is checked.",
           corpo, briciole=[("Methodology", "methodology/")], testata=testata)


def about():
    corpo = f"""<div class="testo">
<p class="lead">{NOME} answers one question with official data: <em>how did my cruise ship do in its CDC health inspection?</em></p>
<p>The CDC publishes every cruise ship inspection, but in a search tool that is hard to use on a phone and that search engines cannot read. We copy the scores and reports into one simple page per ship, with the full history, a chart, and the findings written out in full, and we check the CDC every week.</p>
<h2>Rules we follow</h2>
<ul><li>Every number comes from the CDC, with the inspection date and the date we checked the data on the page.</li>
<li>We do not rate ships ourselves and we do not say whether a ship is “safe”: a CDC score is a sanitation snapshot.</li>
<li>We do not publish names of people.</li>
<li>No advertiser or partner can change a score or a page.</li></ul>
<h2>Who we are</h2>
<p>{NOME} is an independent project run by Massimiliano Cori. It is not affiliated with the CDC, any government agency or any cruise line. {frase_monetizzazione()}</p>
<h2>Corrections</h2>
<p>Found a mistake? <a href="/contact/?ref=about">Write to us</a>; we check the CDC record and correct the page at the next update.</p></div>"""
    testata = banda("About", f"About {NOME}", "An independent site that makes the CDC’s cruise ship inspection records easy to read.", piatta=True)
    pagina("about/", f"About | {NOME}", f"About {NOME}: an independent site that republishes CDC cruise ship inspection scores and reports.",
           corpo, briciole=[("About", "about/")], testata=testata)


def contatti():
    corpo = f"""<section class="card pull"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email"></label>
<label>Ship or page (optional)<input type="text" name="ship" maxlength="200"></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I have read the <a href="/privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send</button><p class="errore" data-errore hidden>Sorry, it did not work. Please try again.</p></form>
<div class="ok-msg" data-ok hidden><strong>Thank you.</strong> We will check the CDC record and reply by email.</div></section>
<p class="small" style="margin-top:16px">We cannot answer questions about a specific cruise, refunds or illnesses on board: please contact your cruise line. Health questions about a ship can go to the CDC (<a href="{CDC_ABOUT}" rel="noopener">Vessel Sanitation Program</a>).</p>"""
    testata = banda("Contact", "Contact us", "Spotted a mistake or have a question about the data?")
    pagina("contact/", f"Contact | {NOME}", f"Contact {NOME} to report a mistake in a cruise ship score or to ask a question about the CDC inspection data.", corpo, briciole=[("Contact", "contact/")], testata=testata)


def privacy():
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    # SafetyWing nominato solo quando il suo link è attivo (dal 17 al 30/10/2026 era sospeso e la frase non era vera).
    sw = bool(AFFILIATI.get("assicurazione", {}).get("url"))
    FRASE_SW = (" Some pages contain an affiliate link to SafetyWing (marked “Affiliate”): our site sets no cookie for it, but if you click it you go "
                "to SafetyWing’s website, which uses its own cookies under its own privacy policy and tells SafetyWing that you came from us."
                if sw else "")
    cookie = MON.privacy_cookie("en", SITO_ID, ci_sono_affiliati())
    if cookie and sw:
        cookie += ("\n<p>Today the affiliate links on this site go to SafetyWing (travel medical insurance), in the box marked “Affiliate” "
                   "on the home page and on ship and cruise line pages.</p>")
    cookie = cookie or f"""<h2>Cookies and visit counter</h2><p>This site sets no cookies and uses no tracking tools. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>.{FRASE_SW} If we add advertising in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>"""
    corpo = f"""<div class="testo"><p class="small">Last updated: {MESI[OGGI.month - 1]} {OGGI.year}</p>
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. Contact: the <a href="/contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the ship or page and your message, plus the page you came from. The ship search runs in your browser: what you type is not sent to us. If you switch between the light and dark theme, your choice is stored in your browser only.</p>
{cookie}
<h2>The data on this site</h2><p>The inspection data comes from the CDC’s public records. We do not publish names of people.</p>
<h2>Why we process your message</h2><p>To answer you and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). Netlify keeps technical server logs (such as IP addresses) for security. We do not sell or share your data.</p>
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority where you live. {MON.frase_california(SITO_ID) or 'California residents: we do not sell or share personal information.'}</p></div>"""
    testata = banda("Privacy", "Privacy notice", "What we collect (very little) and why.", piatta=True)
    # La descrizione dice "no cookies and no tracking": con AdSense acceso o con link di affiliazione si usa la frase breve
    # di monetizzazione.py, altrimenti resta il testo di oggi.
    breve = MON.privacy_breve("en", SITO_ID, ci_sono_affiliati())
    descr = (f"Privacy notice of {NOME}: {breve[0].lower()}{breve[1:]}" if breve else
             f"Privacy notice of {NOME}: no cookies and no tracking, a privacy-friendly visit counter. What we collect through the contact form, and why.")
    pagina("privacy.html", f"Privacy | {NOME}", descr, corpo, testata=testata)


def pagina_404():
    corpo = f"""<div class="card pull cerca-card">{form_cerca("Search for a ship")}</div><p class="lead" style="margin-top:20px">Or go to the <a href="/">home page</a>, the <a href="/ships/">list of ships</a> or the <a href="/cruise-lines/">cruise lines</a>.</p>"""
    pagina("404.html", f"Page not found | {NOME}", "Page not found.", corpo, indicizza=False,
           testata=banda("Error 404", "Page not found", "The ship may have been renamed or removed from the CDC list. Search for it by name."))


# ---------------------------------------------------------------- file accessori
def indice_ricerca():
    righe = []
    for s, n in sorted(NAVI.items(), key=lambda kv: kv[1]["nome"].lower()):
        righe.append([n["nome"], s, n["linea"]["nome"], n["ultima"][1], data_breve(n["ultima"][0]), 1 if n["stato"] == "attiva" else 0, " ".join(n["altri_nomi"])])
    (SITO / "data").mkdir(parents=True, exist_ok=True)
    (SITO / "data" / "ships.json").write_text(json.dumps(righe, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{CONTROLLATO}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in cruisescores/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = cruisescores/sito, Build command vuoto, Publish directory = "."
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

[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=86400"
""")


def copia_grafica():
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").iterdir():
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")


def controlli():
    err = []
    for s, n in NAVI.items():
        if not n["storia"]:
            err.append(f"{s}: nessuna ispezione")
        for i in n["rapporti"]:
            if i not in RAPPORTI:
                err.append(f"{s}: rapporto {i} mancante")
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err[:50]))


def main():
    controlli()
    if SITO.exists():
        shutil.rmtree(SITO)
    SITO.mkdir()
    copia_grafica()
    scrivi_asset()
    home()
    pagina_navi()
    for s in NAVI:
        pagina_nave(s)
    pagina_linee()
    for k in LINEE:
        pagina_linea(k)
    pagina_classifiche()
    for y in ANNI_CLASSIFICHE:
        pagina_perfetti(y)
        pagina_bassi(y)
    pagina_bocciate()
    pagina_anni()
    for y in ANNI:
        pagina_anno(y)
    pagina_epidemie()
    guida()
    metodologia()
    about()
    contatti()
    privacy()
    pagina_404()
    indice_ricerca()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; navi {len(NAVI)} ({len(ATTIVE)} attive, {len(ARCHIVIATE)} archiviate), "
          f"compagnie {len(LINEE)}, anni {len(ANNI)}. Dati controllati il {CONTROLLATO}.")


if __name__ == "__main__":
    main()
