"""Genera il sito statico FloodCost (inglese, pubblico USA) in floodcost/sito/ da floodcost/dati/.

Uso (dalla radice del repository):
    python3 floodcost/raccolta/scarica.py   # dati grezzi OpenFEMA in floodcost/cache/ (fuori da git)
    python3 floodcost/raccolta/aggrega.py   # aggregati compatti in floodcost/dati/
    python3 floodcost/genera.py             # pagine in floodcost/sito/
    python3 floodcost/verifica.py           # controlli prima di pubblicare

Dati (tutti da OpenFEMA, vedi NOTE.md):
    dati/fonti.json     versioni, date di aggiornamento FEMA, data dello scarico, date di riferimento, soglie
    dati/nazionale.json dati nazionali
    dati/stati.json     uno per Stato/territorio
    dati/contee.json    contee con almeno SOGLIA_CONTEA polizze "homes" (una pagina ciascuna)
    dati/zip.json       ZIP con almeno SOGLIA_ZIP polizze "homes" (una pagina ciascuna)
    dati/indice.json    tutti gli ZIP e le altre contee con almeno 10 polizze, per la ricerca nel browser
    dati/affiliati.json riquadro "get a quote": nascosto finché non c'è un URL (mai inventarlo)

Formato dei blocchi statistici: [n, mediana, p25, p75, media] in dollari interi; None = cella con meno di 10 polizze.
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://flood-insurance-cost.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
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
SITO_ID = "floodcost"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_"))


def riquadro_trasparenza(corpo, lingua="en"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Some links are affiliate links: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


NOME = "FloodCost"
API = "https://www.fema.gov/api/open"


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


FONTI = carica("fonti.json")
NAZ = carica("nazionale.json")
STATI = carica("stati.json")
CONTEE = carica("contee.json")
ZIPS = carica("zip.json")
INDICE = carica("indice.json")


def _comunita(c):
    """'Orange County (unincorporated areas)' -> 'unincorporated Orange County' (evita parentesi annidate nei titoli)."""
    s = " (unincorporated areas)"
    c = re.sub(r"(?<=\s)(Of|And|The)(?=\s)", lambda m: m.group(1).lower(), c)  # "Govt. Of Louisville And ..." -> "of", "and"
    return "unincorporated " + c[:-len(s)] if c.endswith(s) else c


for _A in list(CONTEE.values()) + list(ZIPS.values()):
    if _A.get("comm"):
        _A["comm"] = [[_comunita(c), n] for c, n in _A["comm"]]
AFFILIATI = carica("affiliati.json") if (DATI / "affiliati.json").exists() else {}
RIF, RIF0 = FONTI["rif"], FONTI["rif_prec"]
MIN = FONTI["soglie"]["min_cella"]
OGGI = date.today()

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ZONE_ORD = ["VE", "AE", "A", "AO", "AH", "AR", "X", "D"]
ZONE = {
    "VE": {"nome": "Zone VE / V", "breve": "VE", "pag": True, "rischio": "High risk, coastal",
           "def": "Coastal high-hazard areas with an additional hazard from storm waves (velocity flooding). Includes VE, V and the older V1–V30 labels.",
           "fema": "VE, V1-V30 - Velocity Flood with Base Flood Elevation on FIRM; V - Velocity Flood with no Base Flood Elevation on FIRM"},
    "AE": {"nome": "Zone AE", "breve": "AE", "pag": True, "rischio": "High risk",
           "def": "High-risk flood areas where the flood map shows a base flood elevation: the height floodwater has a 1% chance of reaching in any year. Includes the older A1–A30 labels.",
           "fema": "AE, A1-A30 - Special Flood with Base Flood Elevation on FIRM"},
    "A": {"nome": "Zone A", "breve": "A", "pag": True, "rischio": "High risk",
          "def": "High-risk flood areas where no detailed study was done, so the flood map shows no base flood elevation.",
          "fema": "A - Special Flood with no Base Flood Elevation on FIRM"},
    "AO": {"nome": "Zone AO", "breve": "AO", "pag": True, "rischio": "High risk, shallow",
           "def": "High-risk areas with shallow sheet-flow flooding, usually on sloping ground; the map shows flood depths instead of elevations.",
           "fema": "AO, AOB - Special Flood with Sheet Flow"},
    "AH": {"nome": "Zone AH", "breve": "AH", "pag": True, "rischio": "High risk, shallow",
           "def": "High-risk areas with shallow ponding, where water collects in low spots.",
           "fema": "AH, AHB - Special Flood with Shallow Ponding"},
    "AR": {"nome": "Zone A99 / AR", "breve": "A99/AR", "pag": True, "rischio": "High risk, levee areas",
           "def": "High-risk flood areas that will be protected by a flood protection system (such as a levee) still under construction (A99), or behind a system that lost its accreditation and is being restored (AR). Almost all policies here are rated A99.",
           "fema": "A99 - Special Flood with Protection Zone; AR - A Special Flood Hazard Area that results from the decertification of a previously accredited flood protection system that is determined to be in the process of being restored to provide base flood protection"},
    "X": {"nome": "Zone X", "breve": "X", "pag": True, "rischio": "Moderate to low risk",
          "def": "Areas of moderate or minimal flood risk outside the high-risk flood zones (the older maps call them zones B and C). Flood insurance is not required by federal law here, but floods still happen.",
          "fema": "X, B - Moderate Flood from primary water source; X, C - Minimal Flood from primary water source"},
    "D": {"nome": "Zone D", "breve": "D", "pag": False, "rischio": "Undetermined",
          "def": "Areas where flood risk has not been studied, so it is undetermined.",
          "fema": "D - Possible Flood"},
}
SFHA = {"VE", "AE", "A", "AO", "AH", "AR"}
OCC = {"sf": "Single-family home", "mf": "2–4 unit building", "mh": "Manufactured (mobile) home", "cu": "Condo or apartment unit",
       "rb": "Whole residential building (5+ units or condo association)", "nr": "Non-residential building or unit"}
OCC_NOTA = {"rb": "One policy covers the whole building, so the cost is much higher than for a single home.",
            "nr": "Businesses, churches, farm buildings and other non-residential property."}

URL_DIZ_POL = FONTI["dataset"]["NfipPolicies"]["dataDictionary"]
URL_DIZ_CL = FONTI["dataset"]["NfipClaims"]["dataDictionary"]
URL_DIZ_PEN = FONTI["dataset"]["NfipResidentialPenetrationRates"]["dataDictionary"]
FS_ZONE = "https://www.floodsmart.gov/flood-zones-and-maps/what-is-my-flood-zone"
FS_PREMI = "https://www.floodsmart.gov/premiumcosts"
FS_ELIG = "https://www.floodsmart.gov/get-insured/eligibility"
FS_AGENTI = "https://www.floodsmart.gov/get-insured/flood-insurance-provider"
MSC = "https://msc.fema.gov/portal/home"
CONTROLLO_FS = "2026-10-15"  # data in cui abbiamo letto le pagine FloodSmart e il Map Service Center citati


# ---------------------------------------------------------------- utilità
def data_lunga(iso):
    d = date.fromisoformat(iso[:10])
    return f"{MESI[d.month - 1]} {d.day}, {d.year}"


def data_breve(iso):
    d = date.fromisoformat(iso[:10])
    return f"{MESI[d.month - 1][:3]} {d.day}, {d.year}"


def usd(x):
    return "–" if x is None else f"${x:,.0f}"


def usd_lungo(x):
    """Importi grandi nel testo: $89.9 billion, $208.7 million."""
    if x is None:
        return "–"
    if x >= 1e9:
        return f"${x / 1e9:,.1f} billion"
    if x >= 1e7:
        return f"${x / 1e6:,.1f} million"
    return usd(x)


def intero(x):
    return f"{x:,}"


def pc(x):
    return "–" if x is None else f"{x * 100:.1f}%"


def slug(t):
    t = t.lower().replace("&", " and ").replace("'", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def var_pct(nuovo, vecchio):
    if not nuovo or not vecchio:
        return None
    return (nuovo - vecchio) / vecchio * 100


def pct_testo(p, dec=1):
    if p is None:
        return "–"
    s = f"{abs(p):.{dec}f}%"
    return ("+" if p > 0.05 else "−" if p < -0.05 else "±") + s


ABBR = {k: v["nome"] for k, v in STATI.items()}


def nome_stato(st):
    return ABBR.get(st, st)


def url_stato(st):
    return slug(nome_stato(st)) + "/"


def nome_contea(fips):
    n = CONTEE[fips]["nome"] if fips in CONTEE else next((v[1] for k, v in INDICE["contee_altre"].items() if k == fips), fips)
    if n.endswith(" city"):
        return n[:-5] + " (city)"
    return n


def url_contea(fips):
    C = CONTEE[fips]
    return url_stato(C["st"]) + slug(C["nome"]) + "/"


def url_zip(z):
    return f"zip/{z}/"


def url_zona(z):
    return f"flood-zones/zone-{'a99' if z == 'AR' else z.lower()}/"


def h(x):
    return escape(str(x))


# ---------------------------------------------------------------- link ai dati grezzi OpenFEMA (tracciabilità)
SEL_POL = "propertyState,reportedZipCode,censusGeoid,ratedFloodZone,occupancyType,policyCost,policyCount,policyEffectiveDate,policyTerminationDate,cancellationDateOfFloodPolicy"
SEL_CL = "state,reportedZipCode,censusGeoid,yearOfLoss,ratedFloodZone,amountPaidOnBuildingClaim,amountPaidOnContentsClaim,amountPaidOnIncreasedCostOfComplianceClaim"


def filtro_area(tipo, chiave, claims=False):
    if tipo == "stato":
        return f"{'state' if claims else 'propertyState'} eq '{chiave}'"
    if tipo == "contea":
        return f"startswith(censusGeoid,'{chiave}')"
    if tipo == "zip":
        return f"startswith(reportedZipCode,'{chiave}')"
    return ""


def link_api(ds, filtro, sel):
    par = {"$filter": filtro, "$select": sel, "$top": "1000", "$inlinecount": "allpages"} if filtro else {"$select": sel, "$top": "1000", "$inlinecount": "allpages"}
    return f"{API}/v3/{ds}?" + "&".join(f"{k}={quote(v, safe=',()')}" for k, v in par.items())


def link_polizze(tipo, chiave):
    f = f"policyEffectiveDate gt '{int(RIF[:4]) - 1}{RIF[4:]}' and policyEffectiveDate le '{RIF}'"
    a = filtro_area(tipo, chiave)
    return link_api("NfipPolicies", f"{a} and {f}" if a else f, SEL_POL)


def link_sinistri(tipo, chiave):
    return link_api("NfipClaims", filtro_area(tipo, chiave, True), SEL_CL)


def fonte_box(tipo="naz", chiave="", pen=False):
    """Riquadro con le fonti: ogni pagina con numeri ne ha uno (controllato da verifica.py)."""
    dp = FONTI["dataset"]["NfipPolicies"]
    dc = FONTI["dataset"]["NfipClaims"]
    pz = (f'<li><a href="{URL_DIZ_PEN}" rel="noopener">NFIP Residential Penetration Rates (v1)</a> – share of homes with NFIP flood insurance, '
          f'FEMA data as of {data_breve(pen)}.</li>') if pen else ""
    return f"""<aside class="fonti-box" aria-label="Sources">
<h2>{ico("doc")}Where these numbers come from</h2>
<ul>
<li><a href="{URL_DIZ_POL}" rel="noopener">FEMA OpenFEMA – {h(dp["title"])} (v{dp["version"]})</a>: policies in force on {data_lunga(RIF)} (and {data_lunga(RIF0)} for the year-on-year change). FEMA updated the dataset on {data_breve(dp["lastDataSetRefresh"])}.</li>
<li><a href="{URL_DIZ_CL}" rel="noopener">FEMA OpenFEMA – {h(dc["title"])} (v{dc["version"]})</a>: claims by year of loss since {FONTI["anno_sinistri_da"]}. FEMA updated the dataset on {data_breve(dc["lastDataSetRefresh"])}.</li>
{pz}</ul>
<p>Retrieved from the OpenFEMA API on <strong data-recuperato>{data_lunga(FONTI["scaricato_il"])}</strong>. Check the raw records yourself:
<a href="{h(link_polizze(tipo if tipo != "naz" else "", chiave))}" rel="noopener nofollow">policies</a> ·
<a href="{h(link_sinistri(tipo if tipo != "naz" else "", chiave))}" rel="noopener nofollow">claims</a> (OpenFEMA API, JSON). How we count: <a href="{{rel}}methodology/">methodology</a>.</p>
</aside>"""


# ---------------------------------------------------------------- CSS
CSS = """
@font-face{font-family:"Source Serif 4";src:url(/assets/fonts/source-serif-4.woff2) format("woff2");font-weight:200 900;font-style:normal;font-display:swap}
@font-face{font-family:"Figtree";src:url(/assets/fonts/figtree.woff2) format("woff2");font-weight:300 900;font-style:normal;font-display:swap}
:root{--bg:#F2F5F7;--card:#FFFFFF;--ink:#0E1F2B;--ink-2:#364955;--ink-3:#566874;--line:#D8E0E5;--line-2:#C1CDD5;
--deep:#0A2533;--deep-2:#11384B;--on-deep:#EEF5F8;--on-deep-2:#A9C2CE;--accent:#0A6A90;--accent-h:#064F6C;--accent-2:#E2F0F6;--on-accent:#FFFFFF;
--sand:#E9A23B;--sand-ink:#8A5300;--sand-2:#FFF3DF;--up:#A23A1F;--down:#11694A;--mute:#ECF1F4;--track:#E3EAEE;--bar:#0A6A90;--bar-2:#8EC5DC;
--m1:#DCEEF5;--m2:#A6D3E6;--m3:#62AECF;--m4:#2780AA;--m5:#0B4F72;--m-ink-lo:#0E1F2B;--m-ink-hi:#FFFFFF;
--sh-1:0 1px 2px rgba(10,37,51,.06),0 1px 1px rgba(10,37,51,.04);--sh-2:0 20px 40px -22px rgba(10,37,51,.35),0 2px 8px rgba(10,37,51,.06);
--r:14px;--r-s:10px;--serif:"Source Serif 4",Charter,"Iowan Old Style",Georgia,serif;--sans:Figtree,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#081218;--card:#0F1E27;--ink:#E5EEF2;--ink-2:#B7C7D0;--ink-3:#8DA1AD;--line:#1E313D;--line-2:#2A4251;
--deep:#050E13;--deep-2:#0B2230;--on-deep:#E5EEF2;--on-deep-2:#9DB4C0;--accent:#6CC3E8;--accent-h:#9CD8F2;--accent-2:#10303F;--on-accent:#04141C;
--sand:#F0B55A;--sand-ink:#F0B55A;--sand-2:#2A2010;--up:#FF9F87;--down:#72D9AA;--mute:#12232D;--track:#1A2E3A;--bar:#6CC3E8;--bar-2:#2A5D78;
--m1:#1B3E50;--m2:#21566E;--m3:#2B7393;--m4:#4FA3C9;--m5:#8FD3F0;--m-ink-lo:#E5EEF2;--m-ink-hi:#04141C;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 20px 40px -22px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#081218;--card:#0F1E27;--ink:#E5EEF2;--ink-2:#B7C7D0;--ink-3:#8DA1AD;--line:#1E313D;--line-2:#2A4251;
--deep:#050E13;--deep-2:#0B2230;--on-deep:#E5EEF2;--on-deep-2:#9DB4C0;--accent:#6CC3E8;--accent-h:#9CD8F2;--accent-2:#10303F;--on-accent:#04141C;
--sand:#F0B55A;--sand-ink:#F0B55A;--sand-2:#2A2010;--up:#FF9F87;--down:#72D9AA;--mute:#12232D;--track:#1A2E3A;--bar:#6CC3E8;--bar-2:#2A5D78;
--m1:#1B3E50;--m2:#21566E;--m3:#2B7393;--m4:#4FA3C9;--m5:#8FD3F0;--m-ink-lo:#E5EEF2;--m-ink-hi:#04141C;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 20px 40px -22px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--sand);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20}
header.top .wrap{display:flex;align-items:center;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.22rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;letter-spacing:-.01em;margin-right:auto}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:var(--sand);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.08)}
.tema{display:grid;place-items:center;width:42px;height:42px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--sand)}.tema .ico{width:20px;height:20px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:.95rem;padding:9px 13px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep);min-height:42px}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--sand)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{padding:12px 14px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600}.nav-m nav a:hover{background:var(--accent-2)}
.band{background:var(--deep);color:var(--on-deep);position:relative;overflow:hidden}
.band::after{content:"";position:absolute;left:0;right:0;bottom:0;height:56px;background:var(--bg);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 56' preserveAspectRatio='none'%3E%3Cpath d='M0 28c100-18 200-18 300 0s200 18 300 0 200-18 300 0 200 18 300 0v28H0z'/%3E%3C/svg%3E") bottom/100% 100% no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 56' preserveAspectRatio='none'%3E%3Cpath d='M0 28c100-18 200-18 300 0s200 18 300 0 200-18 300 0 200 18 300 0v28H0z'/%3E%3C/svg%3E") bottom/100% 100% no-repeat}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(900px 300px at 85% -10%,rgba(108,195,232,.22),transparent 60%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band-in{position:relative;z-index:1;padding:30px 16px 74px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--sand);margin:0 0 12px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.012em}
h1{font-size:clamp(1.85rem,5vw,2.85rem);line-height:1.1;margin:0 0 12px;text-wrap:balance;max-width:820px}
.band h1{color:#fff}
.sub{font-size:1.08rem;color:var(--on-deep-2);margin:0 0 16px;max-width:700px}
.trust{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--on-deep-2);margin:0;padding:0;list-style:none}
.trust li{display:inline-flex;align-items:center;gap:7px}.trust .ico{color:var(--sand)}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
.hero-plain{padding:28px 0 4px}
h2{font-size:clamp(1.35rem,3vw,1.6rem);line-height:1.2;margin:44px 0 12px}
h3{font-size:1.12rem;margin:24px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:780px;margin:0 0 12px}
.small{font-size:.87rem;color:var(--ink-3)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-58px;position:relative;z-index:2}
.key{padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.key-top{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;background:var(--mute);color:var(--ink-2);padding:10px 20px;font-size:.76rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;border-bottom:1px solid var(--line)}
.key-top .ico{color:var(--accent)}.key-top span:last-child{margin-left:auto;letter-spacing:.03em;text-transform:none;font-weight:600}
.key-body{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:0}
.key-main{padding:22px 24px}
.k-lab{font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin:0}
.k-num{font-family:var(--serif);font-weight:700;font-size:clamp(2.6rem,8vw,3.6rem);line-height:1;letter-spacing:-.02em;margin:8px 0 6px;font-variant-numeric:tabular-nums;color:var(--ink)}
.k-num small{font-family:var(--sans);font-size:1rem;font-weight:600;color:var(--ink-2);letter-spacing:0;margin-left:6px}
.k-txt{margin:6px 0 0;color:var(--ink-2);font-size:.98rem;max-width:520px}
.trend{display:inline-flex;flex-wrap:wrap;align-items:center;gap:6px;font-weight:700;font-size:.9rem;padding:4px 10px;border-radius:999px;background:var(--mute);color:var(--ink-2);margin-top:12px;font-variant-numeric:tabular-nums}
.trend.up{color:var(--up)}.trend.down{color:var(--down)}
.key-side{border-left:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr}
.tile{padding:16px 18px;border-bottom:1px solid var(--line);min-width:0}
.tile:nth-child(odd){border-right:1px solid var(--line)}.tile:nth-last-child(-n+2){border-bottom:0}
.tile b{display:block;font-family:var(--serif);font-size:1.45rem;line-height:1.15;font-variant-numeric:tabular-nums;color:var(--ink)}
.tile span{display:block;font-size:.82rem;color:var(--ink-3);line-height:1.35;margin-top:4px}
.range{margin:16px 0 0}
.range-t{position:relative;height:12px;border-radius:999px;background:var(--track)}
.range-b{position:absolute;top:0;bottom:0;border-radius:999px;background:var(--bar-2)}
.range-m{position:absolute;top:-4px;width:4px;height:20px;border-radius:2px;background:var(--bar);transform:translateX(-2px);box-shadow:0 0 0 2px var(--card)}
.range-l{display:flex;justify-content:space-between;font-size:.8rem;color:var(--ink-3);margin-top:6px;font-variant-numeric:tabular-nums}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1)}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:middle}
td.n,th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
th{background:var(--mute);font-size:.74rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
tbody tr:last-child td{border-bottom:0}
td .rb{display:block;min-width:120px}
.chip{display:inline-flex;align-items:center;gap:8px;font-weight:700;white-space:nowrap}
.chip i{width:12px;height:12px;border-radius:3px;flex:none;background:var(--z)}
.z-VE{--z:#B4233C}.z-AE{--z:#E0702A}.z-A{--z:#D99A12}.z-AO{--z:#B08A10}.z-AH{--z:#9C7A1E}.z-AR{--z:#7B5EA7}.z-X{--z:#2E9C8A}.z-D{--z:#7C8A93}
.muted{color:var(--ink-3)}
.zt td:first-child{min-width:150px}
.scroll-hint{display:none;font-size:.8rem;color:var(--ink-3);margin:0 0 6px}
@media (max-width:640px){.scroll-hint{display:block}
.larga th:first-child,.larga td:first-child{position:sticky;left:0;z-index:1;background:var(--card);box-shadow:1px 0 0 var(--line)}.larga th:first-child{background:var(--mute)}
.ot thead{display:none}.ot,.ot tbody,.ot tr,.ot td{display:block}
.ot tr{display:flex;flex-wrap:wrap;gap:2px 16px;padding:12px 14px;border-bottom:1px solid var(--line)}.ot tbody tr:last-child{border-bottom:0}
.ot td{border:0;padding:0;text-align:left!important}.ot td:first-child{flex:1 1 100%;font-weight:600}.ot td:first-child .small{font-weight:400}
.ot td[data-l]::before{content:attr(data-l) " ";color:var(--ink-3);font-size:.8rem}
.tt th,.tt td{padding:9px 7px}.tt th.n{white-space:normal}.tt td:first-child{min-width:112px}}
@media (max-width:640px){.zt thead{display:none}.zt,.zt tbody,.zt tr,.zt td{display:block;width:100%}
.zt tr{padding:12px 14px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr auto;gap:2px 10px}
.zt tbody tr:last-child{border-bottom:0}.zt td{border:0;padding:0;text-align:left!important}
.zt td[data-l]::before{content:attr(data-l) " ";color:var(--ink-3);font-size:.8rem}
.zt td.zc{grid-column:1;grid-row:1}.zt td.zm{font-family:var(--serif);font-size:1.25rem;font-weight:700;grid-column:2;grid-row:1;text-align:right!important}
.zt td.zr{grid-column:1/-1;margin-top:6px}.zt td.zn,.zt td.za,.zt td.zv{font-size:.88rem}}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;flex-direction:column;justify-content:flex-start;gap:2px;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:700;min-width:0;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px)}
.griglia a span{min-width:0;overflow-wrap:anywhere}.griglia a small{font-weight:500;color:var(--ink-3);font-size:.86rem;font-variant-numeric:tabular-nums}
.cerca-card{padding:18px 20px}
.cerca-card label{display:flex;align-items:center;gap:8px;font-family:var(--serif);font-weight:700;font-size:1.15rem;margin:0 0 10px}
.cerca-card label .ico{color:var(--accent)}
.cerca-box{position:relative}.cerca-box .ico{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--ink-3);pointer-events:none}
.cerca{font:inherit;font-size:1.05rem;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:12px 14px 12px 44px;width:100%;min-height:52px}
.cerca:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.risultati{display:grid;gap:6px;margin-top:10px}.risultati:empty{display:none}
.risultati a{display:flex;justify-content:space-between;gap:12px;align-items:baseline;padding:10px 12px;border-radius:var(--r-s);border:1px solid var(--line);text-decoration:none;color:var(--ink);background:var(--card)}
.risultati a:hover,.risultati a:focus{border-color:var(--accent);background:var(--accent-2)}
.risultati a b{font-weight:700}.risultati a span{font-size:.86rem;color:var(--ink-3);text-align:right;font-variant-numeric:tabular-nums}
.esempi{font-size:.86rem;color:var(--ink-3);margin:10px 0 0}
.mappa{display:grid;grid-template-columns:repeat(11,minmax(0,1fr));gap:4px;margin:6px auto 12px;max-width:760px}
.mappa a,.mappa span{aspect-ratio:1/1;border-radius:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none;font-weight:800;font-size:clamp(.62rem,1.6vw,.95rem);line-height:1.1;min-width:0;color:var(--m-ink-lo)}
.mappa a small{font-weight:600;font-size:.72em;opacity:.92;font-variant-numeric:tabular-nums}
.mappa a:hover{outline:2px solid var(--sand);outline-offset:1px}
.m1{background:var(--m1)}.m2{background:var(--m2)}.m3{background:var(--m3)}.m4{background:var(--m4);color:var(--m-ink-hi)!important}.m5{background:var(--m5);color:var(--m-ink-hi)!important}
.mappa .m0{background:var(--mute);color:var(--ink-3)}
.legenda{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 14px;font-size:.82rem;color:var(--ink-2);margin:0;padding:0;list-style:none}
.legenda li{display:inline-flex;align-items:center;gap:6px}.legenda i{width:14px;height:14px;border-radius:3px;display:inline-block}
@media (max-width:560px){.mappa a small{display:none}.mappa{gap:3px}}
.chart{width:100%;height:auto;display:block}
.chart .b{fill:var(--bar)}.chart .b:hover{fill:var(--sand)}.chart .ax{stroke:var(--line-2);stroke-width:1}.chart .g{stroke:var(--line);stroke-width:1;stroke-dasharray:2 4}
.chart text{fill:var(--ink-3);font-family:var(--sans);font-size:11px}.chart .lbl{fill:var(--ink);font-weight:700}
.stat-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 14px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:14px;box-shadow:var(--sh-1);min-width:0}
.stat b{display:block;font-family:var(--serif);font-size:1.4rem;line-height:1.15;font-variant-numeric:tabular-nums}
.stat span{display:block;font-size:.82rem;color:var(--ink-3);margin-top:4px;line-height:1.35}
.nota{position:relative;background:var(--sand-2);border:1px solid color-mix(in srgb,var(--sand) 45%,transparent);padding:12px 16px 12px 46px;border-radius:var(--r-s);font-size:.93rem;margin:18px 0;color:var(--ink)}
.nota .ico{position:absolute;left:16px;top:14px;color:var(--sand-ink);width:20px;height:20px}
.fonti-box{margin-top:44px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:16px 20px;font-size:.9rem;color:var(--ink-2)}
.fonti-box h2{display:flex;align-items:center;gap:8px;font-size:1.1rem;margin:0 0 8px;color:var(--ink)}.fonti-box h2 .ico{color:var(--accent)}
.fonti-box ul{margin:0 0 8px;padding-left:18px}.fonti-box li{margin-bottom:6px}.fonti-box p{margin:6px 0}
.fonti-box a{overflow-wrap:anywhere}
.quote-box{margin:24px 0;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--accent-2);border:1px solid color-mix(in srgb,var(--accent) 30%,transparent);border-radius:var(--r);padding:18px 20px}
.quote-box p{margin:0;max-width:620px}.quote-box .small{margin-top:4px}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-weight:700;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:12px 20px;cursor:pointer;min-height:46px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}.btn:disabled{opacity:.6;cursor:wait}
.ad-slot{margin:24px 0}.ad-slot:empty{display:none}
.pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:.76rem;font-weight:700;background:var(--mute);color:var(--ink-3);white-space:nowrap;margin:1px 0}
.pill.on{background:color-mix(in srgb,var(--down) 16%,transparent);color:var(--down)}
.risposta{margin:8px 0 0;color:var(--ink);font-size:1rem;max-width:560px}
.irs-card{margin:14px 0}.irs-card h3{margin:6px 0 8px}.irs-top{margin:0;font-size:.86rem;color:var(--ink-3)}
blockquote.irs{margin:8px 0;padding:8px 14px;border-left:3px solid var(--sand);background:var(--sand-2);border-radius:0 var(--r-s) var(--r-s) 0;font-size:.93rem;color:var(--ink)}
.link-uff{padding-left:20px}.link-uff li{margin-bottom:6px}
.dt td:first-child{min-width:170px}
.testo p,.testo li{max-width:780px}
details.tutti{margin-top:10px}details.tutti summary{cursor:pointer;font-weight:700;color:var(--accent);padding:6px 0}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
.form{display:grid;gap:14px}.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}.form .check input{width:auto;min-height:0;margin-top:4px}
.hp{position:absolute;left:-9999px}.ok{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:var(--r-s)}.errore{color:var(--up);font-weight:600}
footer{margin-top:64px;background:var(--deep);color:var(--on-deep-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--on-deep)}footer a:hover{color:var(--sand)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}footer p{margin:0 0 10px;max-width:680px}footer strong{color:var(--on-deep)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--sand);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
@media (max-width:880px){.key-body{grid-template-columns:1fr}.key-side{border-left:0;border-top:1px solid var(--line)}.stat-row{grid-template-columns:repeat(2,minmax(0,1fr))}.cols{grid-template-columns:1fr}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:22px}.key-main{padding:18px}}
@media (max-width:640px){th,td{padding:9px 9px}table{font-size:.87rem}.chart text{font-size:21px}.chart .lbl{font-size:20px}}
@media (max-width:420px){.tile{padding:12px 14px}.tile b{font-size:1.25rem}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""
CSS = re.sub(r"\n", "", CSS)

ICONE = {
    "search": '<circle cx="11" cy="11" r="7.5"/><path d="M21 21l-4.5-4.5"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "doc": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8 13h8M8 17h5"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "house": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/><path d="M10 20v-5h4v5"/>',
    "wave": '<path d="M2 9c2.5-2 5-2 7.5 0s5 2 7.5 0 3.5-1.5 5-1"/><path d="M2 15c2.5-2 5-2 7.5 0s5 2 7.5 0 3.5-1.5 5-1"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "up": '<path d="M7 17 17 7M9 7h8v8"/>',
    "down": '<path d="M7 7l10 10M17 9v8H9"/>',
    "pin": '<path d="M12 21.5s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
}


# Icone in un unico file esterno (/assets/icons.<hash>.svg), richiamate con <use>: prima lo sprite era ripetuto in ogni pagina.
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>\n")
ICONS_FILE = f"icons.{hashlib.sha256(SPRITE.encode()).hexdigest()[:10]}.svg"


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'

# Marchio: casa su onde, in una tessera blu acqua con bordo sabbia (stesso disegno in favicon e immagine Open Graph)
_M = ('<rect width="40" height="40" rx="10" fill="#0A6A90"/><path d="M9 19.5 20 11l11 8.5" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
      '<path d="M12.5 17.5v6h15v-6" fill="none" stroke="#fff" stroke-width="2.6" stroke-linejoin="round"/>'
      '<path d="M6 28.5c2.3-1.8 4.7-1.8 7 0s4.7 1.8 7 0 4.7-1.8 7 0 4.7 1.8 7 0" fill="none" stroke="#E9A23B" stroke-width="2.6" stroke-linecap="round"/>'
      '<path d="M6 33.5c2.3-1.8 4.7-1.8 7 0s4.7 1.8 7 0 4.7-1.8 7 0 4.7 1.8 7 0" fill="none" stroke="#8EC5DC" stroke-width="2.2" stroke-linecap="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{_M}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('fc-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"
APP_JS = r"""
(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('fc-theme',n);}catch(e){}});
  var src=document.querySelectorAll('input[name=source]');var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  var box=document.querySelector('[data-cerca]');if(!box)return;
  var inp=box.querySelector('input'),out=box.querySelector('.risultati'),D=null,carico=false,coda=null,rel=box.getAttribute('data-rel')||'';
  function norm(s){return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function usd(x){return x==null?'–':'$'+Number(x).toLocaleString('en-US');}
  function carica(cb){if(D)return cb();coda=cb;if(carico)return;carico=true;out.innerHTML='<p class="small">Loading the index…</p>';
    fetch(box.getAttribute('data-url')).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){D=d;
      d.s.forEach(function(x){x.k=norm(x[1]);});d.c.forEach(function(x){x.k=norm(x[0]);});if(coda)coda();})
    .catch(function(){out.innerHTML='<p class="errore">Could not load the search index. Please try again.</p>';carico=false;});}
  function riga(href,tit,info){return '<a href="'+esc(rel+href)+'"><b>'+esc(tit)+'</b><span>'+info+'</span></a>';}
  function cerca(){var q=inp.value.trim(),v=norm(q);if(v.length<2){out.innerHTML='';return;}
    carica(function(){var r=[];
      if(/^\d{3,5}$/.test(v)){Object.keys(D.z).forEach(function(z){if(r.length<8&&z.indexOf(v)===0){var x=D.z[z],c=x[1]>=0?D.c[x[1]]:null,st=D.s[x[0]];
          var href=x[4]?'zip/'+z+'/':(c&&c[2]?c[2]:(st?st[2]:''));
          var dove=(c?c[0]+', ':'')+(st?st[0]:'');var info=x[2].toLocaleString('en-US')+' home policies · median '+usd(x[3])+(x[4]?'':' · see '+(c&&c[2]?'county':'state')+' page');
          r.push(riga(href,'ZIP '+z+(dove?' · '+dove:''),info));}});
        if(!r.length)out.innerHTML='<p class="small">No ZIP code starting with '+esc(q)+' has at least 10 NFIP home policies in force. Try the county or state name.</p>';else out.innerHTML=r.join('');return;}
      D.s.forEach(function(s){if(r.length<10&&(s.k.indexOf(v)===0||norm(s[0])===v))r.push(riga(s[2],s[1],s[3].toLocaleString('en-US')+' home policies · median '+usd(s[4])));});
      D.c.forEach(function(c){if(r.length<12&&c.k.indexOf(v)===0){var st=D.s[c[1]];var href=c[2]||(st?st[2]:'');
        r.push(riga(href,c[0]+', '+(st?st[0]:''),c[3].toLocaleString('en-US')+' home policies · median '+usd(c[4])+(c[2]?'':' · see state page')));}});
      if(r.length<12)D.c.forEach(function(c){if(r.length<12&&c.k.indexOf(' '+v)>0){var st=D.s[c[1]];r.push(riga(c[2]||(st?st[2]:''),c[0]+', '+(st?st[0]:''),c[3].toLocaleString('en-US')+' home policies · median '+usd(c[4])));}});
      out.innerHTML=r.length?r.join(''):'<p class="small">Nothing found for "'+esc(q)+'". Try a 5-digit ZIP code, a county or a state.</p>';});}
  inp.addEventListener('input',cerca);inp.addEventListener('focus',function(){carica(function(){});},{once:true});
  box.querySelector('form').addEventListener('submit',function(e){e.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;else cerca();});
})();
"""


# ---------------------------------------------------------------- file condivisi (CSS, JS, favicon) con nome versionato
# Prima il CSS (18 KB) e il JS (4 KB) erano ripetuti in ogni pagina: ora sono file esterni in /assets/, con l'impronta del
# contenuto nel nome (site.<hash>.css), così il browser li tiene in cache e a ogni modifica il nome cambia da solo.
def _impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:10]


ASSET = {
    f"site.{_impronta(CSS)}.css": CSS,
    f"app.{_impronta(APP_JS)}.js": APP_JS.strip() + "\n",
    f"favicon.{_impronta(FAVICON_SVG)}.svg": FAVICON_SVG,
    ICONS_FILE: SPRITE,
}
CSS_FILE, JS_FILE, FAVICON_FILE, _ = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="34" height="34" alt="">'  # marchio: stesso file della favicon, in cache


def scrivi_asset():
    (SITO / "assets").mkdir(parents=True, exist_ok=True)
    for nome, testo in ASSET.items():
        (SITO / "assets" / nome).write_text(testo, encoding="utf-8")


# ---------------------------------------------------------------- scheletro di pagina
URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'


def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, assoluto=False, testata="", jsonld_extra=None):
    file = percorso if percorso.endswith(".html") else (percorso + "index.html")
    prof = file.count("/")
    rel = "/" if assoluto else ("../" * prof or "./")
    url_pag = URL_SITO + "/" + percorso
    if indicizza:
        URLS.append(percorso)
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}] if percorso == "" else []
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL_SITO + "/"}]
        for i, (n, p) in enumerate(briciole, start=2):
            voci.append({"@type": "ListItem", "position": i, "name": n, "item": URL_SITO + "/" + p})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb"><a href="' + rel + '">Home</a>' +
              "".join(f' › <a href="{rel}{p}">{h(n)}</a>' for n, p in briciole[:-1]) + f" › {h(briciole[-1][0])}</nav>")
    if jsonld_extra:
        ld.append(jsonld_extra)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    voci_menu = [("states/", "States"), ("flood-zones/", "Flood zones"), ("disaster-relief/", "Disaster relief"), ("methodology/", "Methodology"), ("about/", "About")]
    menu = "".join(f'<a href="{rel}{u}"' + (' aria-current="page"' if percorso.startswith(u) else "") + f'>{t}</a>' for u, t in voci_menu)
    testata = testata.replace("{bc}", bc)
    corpo = corpo.replace("{rel}", rel).replace("{bc}", bc)
    testata = testata.replace("{rel}", rel)
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
<meta property="og:image:alt" content="{NOME}: what NFIP flood insurance really costs, by ZIP code, county and flood zone">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A2533">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<script>{TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">{LOGO}<span>Flood<b>Cost</b></span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="Open the menu">{ico("menu")}Menu</summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo}{riquadro_trasparenza(corpo)}
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{rel}">{LOGO}<span>Flood<b>Cost</b></span></a>
<p><strong>{NOME}</strong> shows what National Flood Insurance Program (NFIP) policyholders actually pay, from FEMA's public policy and claims data. It is an independent site, not affiliated with FEMA, the NFIP or any insurer.
<strong>These are past prices paid by other policyholders, not a quote.</strong> Your price depends on your building, its elevation and the coverage you choose. Private flood insurance is not included. Nothing here is insurance, financial or legal advice.</p>
<p class="small" style="color:inherit">This product uses the Federal Emergency Management Agency’s OpenFEMA API, but is not endorsed by FEMA. The Federal Government or FEMA cannot vouch for the data or analyses derived from these data after the data have been retrieved from the Agency's website(s).</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="{rel}states/">All states</a></li><li><a href="{rel}flood-zones/">Cost by flood zone</a></li><li><a href="{rel}disaster-relief/">Disaster declarations and IRS relief</a></li><li><a href="{rel}methodology/">Methodology and sources</a></li><li><a href="{rel}about/">About</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li></ul>
</div></div>
<p class="f-base">Data: FEMA OpenFEMA, policies in force on {data_lunga(RIF)}, retrieved {data_lunga(FONTI["scaricato_il"])} · Updated monthly.</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


# ---------------------------------------------------------------- componenti
def banda(eyebrow, titolo, sub, extra=""):
    return f"""<section class="band"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico("wave")}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def barra_range(p25, med, p75, scala):
    if None in (p25, med, p75) or not scala:
        return ""
    a, m, b = (min(100, x / scala * 100) for x in (p25, med, p75))
    return (f'<div class="range-t" role="img" aria-label="Middle half of policies: {usd(p25)} to {usd(p75)}, median {usd(med)}">'
            f'<span class="range-b" style="left:{a:.1f}%;width:{max(b - a, 1):.1f}%"></span><span class="range-m" style="left:{m:.1f}%"></span></div>')


def scheda_chiave(A, etichetta, confronti):
    """Cifra principale (mediana delle case) con forchetta, media, tendenza e quattro riquadri."""
    H = A["h"]
    n, med, p25, p75, avg = H
    P = (A.get("prev") or {}).get("h")
    tr = ""
    if P:
        v = var_pct(med, P[1])
        cls = "up" if v > 0.5 else "down" if v < -0.5 else ""
        tr = (f'<span class="trend {cls}">{ico("up" if v > 0.5 else "down" if v < -0.5 else "calendar")}{pct_testo(v)} vs {data_breve(RIF0)} '
              f'<span class="muted" style="font-weight:600">(median {usd(P[1])})</span></span>')
    scala = p75 * 1.25
    pct_sfha = A.get("sfha_pct")
    tiles = [
        (intero(n), "home policies in force"),
        (usd(avg), "average cost (mean)"),
        (f"{pct_sfha}%" if pct_sfha is not None else "–", "of insured homes in high-risk zones (A, V)"),
        (usd(A.get("bcov")), "median building coverage"),
    ]
    side = "".join(f'<div class="tile"><b>{v}</b><span>{t}</span></div>' for v, t in tiles)
    return f"""<section class="card key pull" aria-label="Key figures">
<div class="key-top">{ico("house")}<span>{h(etichetta)}</span><span>Policies in force on {data_breve(RIF)}</span></div>
<div class="key-body"><div class="key-main">
<p class="k-lab">Median annual cost of NFIP flood insurance for a home</p>
<p class="k-num">{usd(med)}<small>a year</small></p>
<p class="k-txt">Half of insured homes paid between <strong>{usd(p25)}</strong> and <strong>{usd(p75)}</strong>. {confronti}</p>
<div class="range">{barra_range(p25, med, p75, scala)}<div class="range-l"><span>$0</span><span>{usd(p25)} · {usd(med)} · {usd(p75)}</span><span>{usd(round(scala))}</span></div></div>
{tr}
</div><div class="key-side">{side}</div></div>
</section>"""


def confronto(med, rif_med, nome):
    v = var_pct(med, rif_med)
    if v is None:
        return ""
    if abs(v) < 2:
        return f"That is about the same as {nome} ({usd(rif_med)})."
    return f"That is {abs(v):.0f}% {'more' if v > 0 else 'less'} than {nome} ({usd(rif_med)})."


def tabella_zone(A, link=True, rel_zone=""):
    Z = A.get("z") or {}
    P = (A.get("prev") or {}).get("z") or {}
    righe = [z for z in ZONE_ORD if z in Z]
    if not righe:
        return '<p class="small">Fewer than 10 home policies in every flood zone: figures by zone are not shown.</p>'
    scala = max(Z[z][3] for z in righe) * 1.15
    tot = (A.get("h") or [0])[0] or 1
    out = []
    for z in righe:
        n, med, p25, p75, avg = Z[z]
        pm = (P.get(z) or [None, None])[1]
        v = var_pct(med, pm)
        nome = f'<a href="{{rel}}{url_zona(z)}">{ZONE[z]["nome"]}</a>' if (link and ZONE[z]["pag"]) else ZONE[z]["nome"]
        out.append(f'<tr><td class="zc"><span class="chip z-{z}"><i></i>{nome}</span><br><span class="small">{ZONE[z]["rischio"]}</span></td>'
                   f'<td class="n zm" data-l="">{usd(med)}</td>'
                   f'<td class="zr"><span class="rb">{barra_range(p25, med, p75, scala)}</span><span class="small">{usd(p25)}–{usd(p75)}</span></td>'
                   f'<td class="n za" data-l="Average">{usd(avg)}</td>'
                   f'<td class="n zn" data-l="Policies">{intero(n)} <span class="small">({n / tot * 100:.0f}%)</span></td>'
                   f'<td class="n zv" data-l="vs last year">{pct_testo(v) if v is not None else "–"}</td></tr>')
    nasc = [ZONE[z]["breve"] for z in ZONE_ORD if z not in Z]
    nota = (f'<p class="small">Not shown (fewer than 10 home policies): {", ".join(nasc)}. ' if nasc else '<p class="small">') + \
        'Shares are of all insured homes; a few policies have no rated zone. "vs last year" compares medians with policies in force a year earlier.</p>'
    return (f'<div class="tab"><table class="zt"><thead><tr><th>Flood zone</th><th class="n">Median</th><th>Middle half (25th–75th percentile)</th>'
            f'<th class="n">Average</th><th class="n">Policies</th><th class="n">vs last year</th></tr></thead><tbody>{"".join(out)}</tbody></table></div>{nota}')


def tabella_occ(A):
    O = A.get("o") or {}
    if not O:
        return ""
    righe = "".join(f'<tr><td>{OCC[k]}' + (f'<br><span class="small">{OCC_NOTA[k]}</span>' if k in OCC_NOTA else "") +
                    f'</td><td class="n" data-l="Policies">{intero(O[k][0])}</td><td class="n" data-l="Median"><strong>{usd(O[k][1])}</strong></td><td class="n" data-l="Average">{usd(O[k][4])}</td></tr>'
                    for k in OCC if k in O)
    nasc = [OCC[k].lower() for k in OCC if k not in O]
    return (f'<div class="tab"><table class="ot"><thead><tr><th>Type of building</th><th class="n">Policies</th><th class="n">Median</th><th class="n">Average</th></tr></thead>'
            f'<tbody>{righe}</tbody></table></div>'
            + (f'<p class="small">Not shown (fewer than 10 policies): {", ".join(nasc)}.</p>' if nasc else ""))


def grafico_sinistri(C, titolo):
    """Barre: numero di risarcimenti per anno della perdita (una serie, un colore; tooltip nativo su ogni barra)."""
    anni = {r[0]: r for r in C["y"]}
    a0, a1 = FONTI["anno_sinistri_da"], int(FONTI["scaricato_il"][:4])
    W, H, ml, mb, mt = 720, 250, 58, 30, 26
    n = a1 - a0 + 1
    bw = (W - ml - 8) / n
    mx = max([r[1] for r in C["y"]] or [1])
    passo = next(m * 10 ** e for e in range(0, 9) for m in (1, 2, 2.5, 5) if m * 10 ** e * 4 >= mx)
    top = passo * 4
    g = []
    for k in range(0, 5):
        v = passo * k
        y = mt + (H - mt - mb) * (1 - k / 4)
        etich = f"{v / 1000:g}k" if v >= 1000 else f"{v:g}"
        g.append(f'<line class="{"ax" if k == 0 else "g"}" x1="{ml}" x2="{W - 4}" y1="{y:.1f}" y2="{y:.1f}"/>'
                 f'<text x="{ml - 8}" y="{y + 4:.1f}" text-anchor="end">{etich}</text>')
    top3 = sorted(C["y"], key=lambda r: -r[1])[:3]
    for i in range(n):
        a = a0 + i
        x = ml + i * bw
        r = anni.get(a)
        if r:
            hh = max(1.5, (H - mt - mb) * r[1] / top)
            tip = f"{a}: {r[1]:,} claims" + (f", {r[2]:,} paid, {usd(r[3])} in total" if r[2] else "")
            g.append(f'<rect class="b" x="{x + bw * .15:.1f}" y="{H - mb - hh:.1f}" width="{max(bw * .7, 1):.1f}" height="{hh:.1f}" rx="1.5"><title>{tip}</title></rect>')
            if r in top3:
                g.append(f'<text class="lbl" x="{x + bw / 2:.1f}" y="{H - mb - hh - 5:.1f}" text-anchor="middle">{a}</text>')
        if a % 10 == 0:
            g.append(f'<text x="{x + bw / 2:.1f}" y="{H - 4}" text-anchor="middle">{a}</text>')
    return (f'<figure style="margin:0"><svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{h(titolo)}">{"".join(g)}</svg>'
            f'<figcaption class="small">Flood claims per year of loss, {a0}–{a1}. Years with fewer than 10 claims are left blank. Hover a bar for details.</figcaption></figure>')


def sezione_sinistri(C, area):
    if not C:
        return (f'<h2>Flood claims history</h2><p class="lead">Fewer than 10 NFIP flood claims have been recorded in {h(area)} since '
                f'{FONTI["anno_sinistri_da"]}, so we do not show claim figures here.</p>')
    n, npag, tot = C["tot"]
    righe = sorted(C["y"], key=lambda r: -r[0])
    a_fin = int(FONTI["scaricato_il"][:4])
    a10 = a_fin - 10
    ultimi = [r for r in righe if r[0] >= a10]
    top = sorted(C["y"], key=lambda r: -r[1])[:1]
    medio = (tot / npag) if (tot and npag) else None
    testo = (f'Since {FONTI["anno_sinistri_da"]}, NFIP policyholders in {h(area)} have filed <strong>{intero(n)}</strong> flood claims. '
             f'<strong>{intero(npag)}</strong> received a payment' + (f', for a total of <strong>{usd_lungo(tot)}</strong> (an average of <strong>{usd(round(medio))}</strong> per paid claim)' if medio else "") + ". ")
    if top:
        pari = sorted(r[0] for r in C["y"] if r[1] == top[0][1])
        if len(pari) == 1:
            testo += f'The year with the most claims was <strong>{pari[0]}</strong> ({intero(top[0][1])} claims). '
        else:
            anni = ", ".join(f"<strong>{a}</strong>" for a in pari[:-1]) + f" and <strong>{pari[-1]}</strong>"
            testo += f'The years with the most claims were {anni} ({intero(top[0][1])} claims each). '
    testo += "Amounts are in dollars of the time, not adjusted for inflation."
    tab = "".join(f'<tr><td>{r[0]}</td><td class="n">{intero(r[1])}</td><td class="n">{intero(r[2]) if r[2] is not None else "<10"}</td>'
                  f'<td class="n">{usd(r[3]) if r[3] is not None else "–"}</td><td class="n">{usd(round(r[3] / r[2])) if r[2] and r[3] is not None else "–"}</td></tr>'
                  for r in righe)
    return f"""<h2>Flood claims history</h2>
<p class="lead">{testo}</p>
<div class="card">{grafico_sinistri(C, "Flood claims per year in " + area)}</div>
<details class="tutti"><summary>All years with at least 10 claims ({len(righe)})</summary>
<p class="scroll-hint">Swipe the table sideways to see all columns.</p><div class="tab"><table class="larga"><thead><tr><th>Year of loss</th><th class="n">Claims</th><th class="n">Paid claims</th><th class="n">Total paid</th><th class="n">Average per paid claim</th></tr></thead><tbody>{tab}</tbody></table></div></details>
<p class="small">{f"From {a10} to {a_fin}: {intero(sum(r[1] for r in ultimi))} claims (counting only years with at least 10). " if ultimi else ""}{a_fin} is a partial year. Claims are counted where the insured property is; they include buildings and contents, homes and businesses.</p>"""


def box_quote():
    """Riquadro "get a quote": compare solo quando dati/affiliati.json ha un URL (mai inventato)."""
    voci = [v for k, v in AFFILIATI.items() if not k.startswith("_") and isinstance(v, dict) and v.get("url")]
    if not voci:
        return ""
    v = voci[0]
    return (f'<aside class="quote-box" aria-label="Get a quote"><div><p><strong>{h(v["titolo"])}</strong></p><p class="small">{h(v["testo"])} '
            f'Sponsored link. {MON.RIGA_EN}</p></div>'
            f'<a class="btn" href="{h(v["url"])}" rel="sponsored noopener" target="_blank">{h(v.get("bottone", "Get a quote"))}{ico("arrow")}</a></aside>')


NON_QUOTE = (f'<p class="nota">{ico("info")}<strong>This is what policyholders paid, not a quote.</strong> Two neighbors can pay very different prices: '
             f'NFIP prices depend on the building (elevation, foundation, number of floors, replacement cost), the coverage and deductible chosen and the '
             f'distance to water (<a href="{FS_PREMI}" rel="noopener">FEMA FloodSmart: premium factors</a>). For a price for your building, ask an insurance agent. '
             'Private flood insurance is not included in these figures.</p>')


def rr2_testo():
    a, b = NAZ["rr2"]
    if min(a, b) >= 99.5:
        return ("Nationwide, practically all policies in both years carry FEMA's Risk Rating 2.0 occupancy codes, so both years use the same pricing system.")
    return f"Nationwide, {a}% of the policies a year earlier and {b}% now carry FEMA's Risk Rating 2.0 occupancy codes."


def tabella_trend(A, nome):
    P = A.get("prev")
    if not P or not P.get("h") or not A.get("h"):
        return ""
    c, p = A["h"], P["h"]
    righe = [("Home policies in force", intero(p[0]), intero(c[0]), pct_testo(var_pct(c[0], p[0]))),
             ("Median annual cost", usd(p[1]), usd(c[1]), pct_testo(var_pct(c[1], p[1]))),
             ("Average annual cost", usd(p[4]), usd(c[4]), pct_testo(var_pct(c[4], p[4]))),
             ("All policies in force (any building)", intero(P["n"]), intero(A["n"]), pct_testo(var_pct(A["n"], P["n"])))]
    corpo = "".join(f'<tr><td>{a}</td><td class="n">{b}</td><td class="n"><strong>{c_}</strong></td><td class="n">{d}</td></tr>' for a, b, c_, d in righe)
    return (f'<h2>One year on: {h(nome)}</h2><p class="lead">Policies in force on {data_lunga(RIF)} compared with a year earlier. {rr2_testo()} The policies are not the same: some were new, some lapsed.</p>'
            f'<div class="tab"><table class="tt"><thead><tr><th></th><th class="n">{data_breve(RIF0)}</th><th class="n">{data_breve(RIF)}</th><th class="n">Change</th></tr></thead><tbody>{corpo}</tbody></table></div>')


def zl(nome):
    """'Zone AE' -> 'zone AE' dentro una frase."""
    return nome[0].lower() + nome[1:]


def frase_zona_top(A):
    Z = A.get("z") or {}
    if not Z or not A.get("h"):
        return ""
    z = max(Z, key=lambda k: Z[k][0])
    quota = Z[z][0] / A['h'][0] * 100
    if quota > 50:
        return f"Most insured homes here are rated in {zl(ZONE[z]['nome'])} ({quota:.0f}%)."
    return f"The most common flood zone for insured homes here is {zl(ZONE[z]['nome'])} ({quota:.0f}%)."


def griglia(voci):
    return '<ul class="griglia">' + "".join(f'<li><a href="{{rel}}{u}"><span>{h(t)}</span><small>{s}</small></a></li>' for u, t, s in voci) + "</ul>"


# ---------------------------------------------------------------- pagine area
def pagina_area(tipo, chiave):
    if tipo == "stato":
        A = STATI[chiave]
        nome, nome_lungo = A["nome"], A["nome"]
        percorso = url_stato(chiave)
        brc = [(nome, percorso)]
        sup = NAZ
        cfr = confronto(A["h"][1], NAZ["h"][1], "the national median") if A.get("h") else ""
        eyebrow = "Flood insurance cost · " + chiave
    elif tipo == "contea":
        A = CONTEE[chiave]
        S = STATI.get(A["st"], {})
        nome = nome_contea(chiave)
        nome_lungo = f"{nome}, {nome_stato(A['st'])}"
        percorso = url_contea(chiave)
        brc = [(nome_stato(A["st"]), url_stato(A["st"])), (nome, percorso)]
        cfr = " ".join(x for x in (confronto(A["h"][1], S["h"][1], f"the {nome_stato(A['st'])} median") if S.get("h") else "",) if x)
        eyebrow = f"Flood insurance cost · {nome}, {A['st']}"
    else:
        A = ZIPS[chiave]
        st, cty = A["st"], A.get("cty")
        comm = A.get("comm") or []
        luogo = comm[0][0] if comm else ""
        nome = f"ZIP code {chiave}"
        nome_lungo = f"ZIP code {chiave}" + (f" ({luogo}, {st})" if luogo else f", {nome_stato(st)}")
        percorso = url_zip(chiave)
        brc = [(nome_stato(st), url_stato(st))] + ([(nome_contea(cty), url_contea(cty))] if cty in CONTEE else []) + [(f"ZIP {chiave}", percorso)]
        rif_c = CONTEE.get(cty)
        cfr = confronto(A["h"][1], rif_c["h"][1], f"the {nome_contea(cty)} median") if (rif_c and rif_c.get("h")) else \
            (confronto(A["h"][1], STATI[st]["h"][1], f"the {nome_stato(st)} median") if st in STATI else "")
        eyebrow = f"Flood insurance cost · ZIP {chiave}" + (f" · {st}" if st else "")
    if not A.get("h"):
        return False
    med = A["h"][1]
    titolo_h1 = (f"Flood insurance cost in {nome_lungo}" if tipo != "zip" else
                 f"Flood insurance cost in ZIP {chiave}" + (f" ({luogo}, {st})" if luogo else ""))
    # <title> breve, con le parole chiave e la cifra all'inizio (Google tronca verso i 60 caratteri)
    if tipo == "stato":
        titolo = f"Flood insurance cost in {nome}: median {usd(med)} a year"
    elif tipo == "contea":
        titolo = f"Flood insurance cost in {nome}, {A['st']}: median {usd(med)} a year"
    else:
        titolo = f"ZIP {chiave} flood insurance cost: median {usd(med)} a year" + (f" ({luogo}, {st})" if luogo else f" ({st})")
    p25_, p75_ = A["h"][2], A["h"][3]
    descr = (f"NFIP flood insurance in {nome_lungo}: homes paid a median {usd(med)} a year (middle half {usd(p25_)}–{usd(p75_)}). "
             f"Cost by flood zone, 1-year change and flood claims. FEMA data.")
    sub = (f"What homeowners with a National Flood Insurance Program policy actually pay, from FEMA's records of "
           f"{intero(A['h'][0])} home policies in force on {data_lunga(RIF)}.")
    corpo = [scheda_chiave(A, nome_lungo, " ".join(x for x in (cfr, frase_zona_top(A)) if x)), AD, NON_QUOTE, box_quote(),
             rimando_disastri(tipo, chiave) if tipo in ("stato", "contea") else ""]
    corpo.append(f'<h2>Cost by flood zone in {h(nome)}</h2><p class="lead">The flood zone on FEMA\'s map is one of the main price factors. '
                 f'Median and middle half of what insured homes paid, by the zone used to rate the policy.</p>{tabella_zone(A)}')
    occ = tabella_occ(A)
    if occ:
        corpo.append(f'<h2>Cost by type of building</h2><p class="lead">All NFIP policies in force in {h(nome)}, by what they insure.</p>{occ}'
                     f'<div class="stat-row" style="margin-top:14px">'
                     f'<div class="stat"><b>{intero(A["n"])}</b><span>NFIP policies in force, any building</span></div>'
                     f'<div class="stat"><b>{intero(A["u"])}</b><span>insured units (condo association policies count every unit)</span></div>'
                     f'<div class="stat"><b>{str(A.get("ccov_pct")) + "%" if A.get("ccov_pct") is not None else "–"}</b><span>of home policies also cover contents</span></div>'
                     f'<div class="stat"><b>{usd(A.get("ccov"))}</b><span>median contents coverage, when bought</span></div></div>')
    corpo.append(tabella_trend(A, nome))
    pen = None
    if tipo == "contea" and A.get("pen") and A["pen"].get("all") is not None:
        p = A["pen"]
        pen = p["asof"]
        corpo.append(f'<h2>How many homes have flood insurance?</h2><div class="stat-row">'
                     f'<div class="stat"><b>{pc(p["all"])}</b><span>of all homes in {h(nome)} have an NFIP policy</span></div>'
                     f'<div class="stat"><b>{pc(p["sfha"])}</b><span>of homes in high-risk zones (special flood hazard area) have one</span></div>'
                     f'<div class="stat"><b>{intero(p["res"]) if p.get("res") is not None else "–"}</b><span>residential buildings counted by FEMA</span></div>'
                     f'<div class="stat"><b>{intero(p["res_sfha"]) if p.get("res_sfha") is not None else "–"}</b><span>of them in high-risk zones</span></div></div>'
                     f'<p class="small">FEMA NFIP Residential Penetration Rates, data as of {data_lunga(p["asof"])}: residential contracts in force divided by residential structures.</p>')
    nome_area_cl = nome_lungo if tipo != "zip" else f"ZIP {chiave}"
    corpo.append(sezione_sinistri(A.get("c"), nome_area_cl))
    # collegamenti
    if tipo == "stato":
        cc = sorted((k for k, v in CONTEE.items() if v["st"] == chiave), key=lambda k: CONTEE[k]["nome"])
        if cc:
            corpo.append(f'<h2>Counties in {h(nome)}</h2><p class="lead">Counties with at least {FONTI["soglie"]["contea"]} NFIP home policies in force have their own page.</p>' +
                         griglia([(url_contea(k), nome_contea(k), f'median {usd(CONTEE[k]["h"][1])} · {intero(CONTEE[k]["h"][0])} homes') for k in cc]))
        altre = sorted((v for k, v in INDICE["contee_altre"].items() if v[0] == chiave), key=lambda v: v[1])
        if altre:
            corpo.append('<details class="tutti"><summary>Other counties (fewer policies, no separate page)</summary><div class="tab"><table><thead><tr><th>County</th>'
                         '<th class="n">Home policies</th><th class="n">Median</th></tr></thead><tbody>' +
                         "".join(f'<tr><td>{h(v[1])}</td><td class="n">{intero(v[2])}</td><td class="n">{usd(v[3])}</td></tr>' for v in altre) + "</tbody></table></div></details>")
        zz = sorted((z for z, v in ZIPS.items() if v["st"] == chiave), key=lambda z: -ZIPS[z]["h"][0])[:24]
        if zz:
            corpo.append(f'<h2>ZIP codes with the most insured homes</h2>' +
                         griglia([(url_zip(z), f'ZIP {z}' + (f' · {ZIPS[z]["comm"][0][0]}' if ZIPS[z].get("comm") else ""), f'median {usd(ZIPS[z]["h"][1])} · {intero(ZIPS[z]["h"][0])} homes') for z in zz]))
    if tipo == "contea":
        zz = sorted(z for z, v in ZIPS.items() if v.get("cty") == chiave)
        if zz:
            corpo.append(f'<h2>ZIP codes in {h(nome)}</h2><p class="lead">ZIP codes with at least {FONTI["soglie"]["zip"]} NFIP home policies in force have their own page.</p>' +
                         griglia([(url_zip(z), f'ZIP {z}' + (f' · {ZIPS[z]["comm"][0][0]}' if ZIPS[z].get("comm") else ""), f'median {usd(ZIPS[z]["h"][1])} · {intero(ZIPS[z]["h"][0])} homes') for z in zz]))
        if A.get("comm"):
            corpo.append('<h3>Main NFIP communities in the county</h3><p class="small">' + " · ".join(f'{h(c[:1].upper() + c[1:])} ({intero(n)} home policies)' for c, n in A["comm"]) + "</p>")
    if tipo == "zip" and A.get("comm"):
        corpo.append('<h3>NFIP communities in this ZIP code</h3><p class="small">' + " · ".join(f'{h(c[:1].upper() + c[1:])} ({intero(n)} home policies)' for c, n in A["comm"]) +
                     '. A ZIP code can cross city and county lines; each policy is counted once, in the ZIP code reported for the insured building.</p>')
    corpo.append(fonte_box(tipo, chiave, pen))
    testata = banda(eyebrow, titolo_h1, sub)
    pagina(percorso, titolo + " | " + NOME, descr, "\n".join(x for x in corpo if x), briciole=brc, testata=testata)
    return True


# ---------------------------------------------------------------- mappa a tessere degli Stati
TESSERE = {"AK": (0, 0), "ME": (0, 10), "VT": (1, 9), "NH": (1, 10), "WA": (2, 0), "ID": (2, 1), "MT": (2, 2), "ND": (2, 3), "MN": (2, 4),
           "IL": (2, 5), "WI": (2, 6), "MI": (2, 7), "NY": (2, 8), "RI": (2, 9), "MA": (2, 10), "OR": (3, 0), "NV": (3, 1), "WY": (3, 2),
           "SD": (3, 3), "IA": (3, 4), "IN": (3, 5), "OH": (3, 6), "PA": (3, 7), "NJ": (3, 8), "CT": (3, 9), "CA": (4, 0), "UT": (4, 1),
           "CO": (4, 2), "NE": (4, 3), "MO": (4, 4), "KY": (4, 5), "WV": (4, 6), "VA": (4, 7), "MD": (4, 8), "DE": (4, 9), "AZ": (5, 1),
           "NM": (5, 2), "KS": (5, 3), "AR": (5, 4), "TN": (5, 5), "NC": (5, 6), "SC": (5, 7), "DC": (5, 8), "OK": (6, 3), "LA": (6, 4),
           "MS": (6, 5), "AL": (6, 6), "GA": (6, 7), "HI": (7, 0), "TX": (7, 3), "FL": (7, 8), "PR": (7, 10)}


def estremi_zone():
    Z = {z: v for z, v in NAZ["z"].items() if v[0] >= 10000}
    a = max(Z, key=lambda z: Z[z][1])
    b = min(Z, key=lambda z: Z[z][1])
    x = NAZ["z"].get("X")
    return (f"Among zones with at least 10,000 insured homes, the median is highest in {zl(ZONE[a]['nome'])} ({usd(Z[a][1])}) and lowest in "
            f"{zl(ZONE[b]['nome'])} ({usd(Z[b][1])})" + (f"; zone X, outside the mapped high-risk areas, is at {usd(x[1])}." if x and b != "X" else "."))


def estremi_stati():
    """Frase con gli Stati più cari e meno cari (solo i 50 Stati e DC con almeno 1.000 polizze), calcolata dai dati."""
    v = sorted((s for s in TESSERE if s in STATI and STATI[s].get("h") and STATI[s]["h"][0] >= 1000 and s != "PR"), key=lambda s: -STATI[s]["h"][1])
    alto = ", ".join(f"{STATI[s]['nome']} ({usd(STATI[s]['h'][1])})" for s in v[:3])
    basso = ", ".join(f"{STATI[s]['nome']} ({usd(STATI[s]['h'][1])})" for s in v[-3:][::-1])
    return f"Among states and territories with at least 1,000 insured homes, the highest medians are in {alto}; the lowest in {basso}."


def mappa_stati():
    meds = sorted(STATI[s]["h"][1] for s in TESSERE if s in STATI and STATI[s].get("h"))
    k = len(meds)
    soglie = [meds[min(k - 1, int(k * q))] for q in (0.2, 0.4, 0.6, 0.8)]

    def classe(m):
        return 1 + sum(m >= s for s in soglie)
    celle = []
    for r in range(8):
        for c in range(11):
            st = next((s for s, p in TESSERE.items() if p == (r, c)), None)
            if st and st in STATI and STATI[st].get("h"):
                m = STATI[st]["h"][1]
                celle.append(f'<a class="m{classe(m)}" href="{{rel}}{url_stato(st)}" title="{h(nome_stato(st))}: median {usd(m)} a year" '
                             f'style="grid-row:{r + 1};grid-column:{c + 1}">{st}<small>{usd(m)}</small></a>')
            elif st:
                celle.append(f'<span class="m0" style="grid-row:{r + 1};grid-column:{c + 1}">{st}</span>')
    lim = [meds[0]] + soglie + [meds[-1]]
    leg = "".join(f'<li><i class="m{i + 1}"></i>{usd(lim[i])}–{usd(lim[i + 1] - (1 if i < 4 else 0))}</li>' for i in range(5))
    return (f'<div class="card"><div class="mappa" role="list" aria-label="Median annual cost of NFIP home policies by state">{"".join(celle)}</div>'
            f'<ul class="legenda" aria-label="Legend">{leg}</ul><p class="small" style="margin:8px 0 0">Median annual cost of NFIP home policies in force on {data_lunga(RIF)}, '
            f'in five groups with about the same number of states. Each tile links to the state page.</p></div>')


def blocco_cerca(rel_id=""):
    return f"""<section class="card cerca-card" id="search" data-cerca data-url="{{rel}}data/search.json" data-rel="{{rel}}">
<form role="search"><label for="q">{ico("pin")}Find your ZIP code, county or state</label>
<div class="cerca-box">{ico("search")}<input id="q" class="cerca" type="search" placeholder="e.g. 33904, Harris County, Louisiana" autocomplete="off" inputmode="search"></div></form>
<div class="risultati" aria-live="polite"></div>
<p class="esempi">Searches run in your browser on a list of {intero(len(INDICE["zip"]))} ZIP codes and {intero(len(CONTEE) + len(INDICE["contee_altre"]))} counties with at least {MIN} NFIP home policies.</p>
</section>"""


def home():
    H = NAZ["h"]
    P = NAZ["prev"]["h"]
    st_ord = sorted((s for s in STATI if STATI[s].get("h")), key=lambda s: STATI[s]["nome"])
    big = sorted(CONTEE, key=lambda k: -CONTEE[k]["h"][0])[:12]
    testata = banda("FEMA data · updated monthly", "What does flood insurance really cost here?",
                    f"The median NFIP home policy costs <strong style=\"color:#fff\">{usd(H[1])} a year</strong>. Look up what policyholders actually pay "
                    f"in your ZIP code, county, state and flood zone, from FEMA's records of {intero(H[0])} home policies in force.",
                    f'<ul class="trust"><li>{ico("db")}Official FEMA NFIP data</li><li>{ico("calendar")}Policies in force on {data_breve(RIF)}</li>'
                    f'<li>{ico("shield")}No sign-up, no personal data</li></ul>')
    corpo = f"""<div class="pull">{blocco_cerca()}</div>
<div style="margin-top:22px">{scheda_chiave(NAZ, "United States, all NFIP home policies", frase_zona_top(NAZ)).replace(" pull", "")}</div>
{AD}
{NON_QUOTE}
{teaser_disastri()}
<h2>Flood insurance cost by state</h2>
<p class="lead">Median annual cost of an NFIP home policy. {estremi_stati()} Open a state for its counties, ZIP codes and flood zones.</p>
{mappa_stati()}
<details class="tutti"><summary>All states and territories in a list</summary>{griglia([(url_stato(s), STATI[s]["nome"], f'median {usd(STATI[s]["h"][1])}') for s in st_ord])}</details>
<h2>Cost by flood zone, nationwide</h2>
<p class="lead">{estremi_zone()} Open a zone for state-by-state figures.</p>
{tabella_zone(NAZ)}
<h2>Counties with the most insured homes</h2>
{griglia([(url_contea(k), f"{nome_contea(k)}, {CONTEE[k]['st']}", f'median {usd(CONTEE[k]["h"][1])} · {intero(CONTEE[k]["h"][0])} homes') for k in big])}
{tabella_trend(NAZ, "the United States")}
{sezione_sinistri(NAZ["c"], "the United States")}
<h2>How this works</h2>
<div class="cols"><div class="card"><h3 style="margin-top:0">What the numbers are</h3><p class="small">FEMA publishes every NFIP policy, without names or addresses, in its OpenFEMA data. We take the policies in force on {data_lunga(RIF)}, keep the total annual cost (premium plus the fees and surcharges in the bill) and compute medians by area, flood zone and building type. Areas or groups with fewer than {MIN} policies are not shown.</p></div>
<div class="card"><h3 style="margin-top:0">What they are not</h3><p class="small">They are not a quote and not an estimate for your home: they describe what other policyholders paid. Private flood insurance, which FEMA does not report, is not included. <a href="{{rel}}methodology/">Read the full methodology</a>.</p></div></div>
{fonte_box()}"""
    pagina("", f"Flood insurance cost by ZIP code, county and state | {NOME}",
           f"What NFIP flood insurance really costs: median {usd(H[1])} a year for a home. Look up the median cost by ZIP code, county, state and flood zone, "
           f"from FEMA's policy data, with flood claims since {FONTI['anno_sinistri_da']}.", corpo, testata=testata)


def teaser_disastri():
    if not DIS:
        return ""
    ap = [c for c in IRS_N if aperto(c)]
    return (f'<p class="nota">{ico("alert")}<strong>Was your county in a federal disaster?</strong> FEMA declarations, individual assistance and '
            f'IRS postponed tax deadlines ({len(ap)} IRS notices open today), county by county: <a href="{{rel}}{DIS_URL}">disaster declarations and IRS tax relief</a>.</p>')


def pagina_stati():
    st_ord = sorted((s for s in STATI if STATI[s].get("h")), key=lambda s: STATI[s]["nome"])
    righe = "".join(f'<tr><td><a href="{{rel}}{url_stato(s)}">{h(STATI[s]["nome"])}</a></td><td class="n">{intero(STATI[s]["h"][0])}</td>'
                    f'<td class="n"><strong>{usd(STATI[s]["h"][1])}</strong></td><td class="n">{usd(STATI[s]["h"][2])}–{usd(STATI[s]["h"][3])}</td>'
                    f'<td class="n">{pct_testo(var_pct(STATI[s]["h"][1], (STATI[s].get("prev") or {}).get("h", [None, None])[1] if (STATI[s].get("prev") or {}).get("h") else None))}</td></tr>'
                    for s in st_ord)
    corpo = f"""{mappa_stati()}
<h2>All states and territories</h2>
<p class="scroll-hint">Swipe the table sideways to see all columns.</p><div class="tab"><table class="larga"><thead><tr><th>State</th><th class="n">Home policies</th><th class="n">Median</th><th class="n">Middle half</th><th class="n">vs last year</th></tr></thead><tbody>{righe}</tbody></table></div>
{NON_QUOTE}
{fonte_box()}"""
    testata = banda("Flood insurance cost · by state", "Flood insurance cost by state",
                    f"Median annual cost of NFIP home policies in force on {data_lunga(RIF)}, from FEMA data. National median: {usd(NAZ['h'][1])}.")
    pagina("states/", f"Flood insurance cost by state ({RIF[:4]}): NFIP medians | {NOME}",
           "Median annual cost of NFIP flood insurance for a home in every state, with the middle half of prices and the change since last year. FEMA data.",
           corpo, briciole=[("States", "states/")], testata=testata)


# ---------------------------------------------------------------- pagine delle zone
def pagina_zona(z):
    Zn = NAZ["z"].get(z)
    if not Zn:
        return False
    Z = ZONE[z]
    n, med, p25, p75, avg = Zn
    pm = (NAZ["prev"]["z"].get(z) or [None, None])[1]
    v = var_pct(med, pm)
    stati = sorted((s for s in STATI if STATI[s].get("z", {}).get(z)), key=lambda s: -STATI[s]["z"][z][1])
    righe = "".join(f'<tr><td><a href="{{rel}}{url_stato(s)}">{h(STATI[s]["nome"])}</a></td><td class="n">{intero(STATI[s]["z"][z][0])}</td>'
                    f'<td class="n"><strong>{usd(STATI[s]["z"][z][1])}</strong></td><td class="n">{usd(STATI[s]["z"][z][2])}–{usd(STATI[s]["z"][z][3])}</td>'
                    f'<td class="n">{usd(STATI[s]["z"][z][4])}</td></tr>' for s in stati)
    contee = sorted((k for k in CONTEE if CONTEE[k].get("z", {}).get(z) and CONTEE[k]["z"][z][0] >= 100), key=lambda k: -CONTEE[k]["z"][z][0])[:20]
    altre = "".join(f'<li><a href="{{rel}}{url_zona(o)}">{ZONE[o]["nome"]}</a>: {usd(NAZ["z"][o][1])}</li>' for o in ZONE_ORD if o != z and ZONE[o]["pag"] and o in NAZ["z"])
    obblig = ("Federal law requires flood insurance for buildings in high-risk zones (A and V) with a government-backed mortgage, "
              f"in communities that take part in the NFIP (<a href=\"{FS_ELIG}\" rel=\"noopener\">FEMA FloodSmart</a>). Some lenders ask for it elsewhere too."
              if z in SFHA else
              f"Federal law does not require flood insurance in zone {Z['breve']}, but lenders can ask for it (<a href=\"{FS_ELIG}\" rel=\"noopener\">FEMA FloodSmart</a>).")
    corpo = f"""<section class="card key pull"><div class="key-top">{ico("wave")}<span>{Z["nome"]} · United States</span><span>Policies in force on {data_breve(RIF)}</span></div>
<div class="key-body"><div class="key-main"><p class="k-lab">Median annual cost of an NFIP home policy in {zl(Z["nome"])}</p>
<p class="k-num">{usd(med)}<small>a year</small></p>
<p class="k-txt">Half of the {intero(n)} insured homes rated in this zone paid between <strong>{usd(p25)}</strong> and <strong>{usd(p75)}</strong>. All homes nationwide: {usd(NAZ["h"][1])}.</p>
<div class="range">{barra_range(p25, med, p75, p75 * 1.25)}<div class="range-l"><span>$0</span><span>{usd(p25)} · {usd(med)} · {usd(p75)}</span><span>{usd(round(p75 * 1.25))}</span></div></div>
{f'<span class="trend {"up" if v > 0.5 else "down" if v < -0.5 else ""}">{ico("up" if v > 0.5 else "down")}{pct_testo(v)} vs {data_breve(RIF0)} <span class="muted" style="font-weight:600">(median {usd(pm)})</span></span>' if v is not None else ""}
</div><div class="key-side">
<div class="tile"><b>{intero(n)}</b><span>home policies in this zone</span></div><div class="tile"><b>{usd(avg)}</b><span>average cost (mean)</span></div>
<div class="tile"><b>{n / NAZ["h"][0] * 100:.1f}%</b><span>of all insured homes</span></div><div class="tile"><b>{len(stati)}</b><span>states and territories with 10+ policies here</span></div>
</div></div></section>
{AD}
<h2>What is {zl(Z["nome"])}?</h2>
<p class="lead">{Z["def"]} {obblig}</p>
<p class="small">FEMA's data dictionary label: "{h(Z["fema"])}". To find the zone of an address, use the <a href="{MSC}" rel="noopener">FEMA Flood Map Service Center</a>; the zone printed on a policy is the one used to rate it.</p>
{NON_QUOTE}
{box_quote()}
<h2>{Z["nome"]}: cost by state</h2>
<p class="lead">Median annual cost of NFIP home policies rated in {zl(Z["nome"])}, in every state with at least {MIN} such policies, from the most to the least expensive.</p>
<p class="scroll-hint">Swipe the table sideways to see all columns.</p><div class="tab"><table class="larga"><thead><tr><th>State</th><th class="n">Policies</th><th class="n">Median</th><th class="n">Middle half</th><th class="n">Average</th></tr></thead><tbody>{righe}</tbody></table></div>
{('<h2>Counties with the most ' + Z["nome"] + ' policies</h2>' + griglia([(url_contea(k), f"{nome_contea(k)}, {CONTEE[k]['st']}", f'median {usd(CONTEE[k]["z"][z][1])} · {intero(CONTEE[k]["z"][z][0])} homes') for k in contee])) if contee else ""}
<h2>Other flood zones</h2><ul>{altre}</ul>
{fonte_box()}"""
    testata = banda(f"Flood insurance cost · {Z['nome']}", f"Cost of flood insurance in {zl(Z['nome'])}",
                    f"What homeowners with an NFIP policy rated in {zl(Z['nome'])} actually pay, nationwide and state by state. {Z['rischio']}.")
    pagina(url_zona(z), f"Cost of flood insurance in {zl(Z['nome'])}: median {usd(med)} a year ({RIF[:4]}) | {NOME}",
           f"How much flood insurance costs in {zl(Z['nome'])}: the median NFIP home policy costs {usd(med)} a year (middle half {usd(p25)}–{usd(p75)}), "
           f"with state-by-state medians. FEMA data, not a quote.", corpo, briciole=[("Flood zones", "flood-zones/"), (Z["nome"], url_zona(z))], testata=testata)
    return True


def pagina_zone_hub():
    voci = [(url_zona(z), ZONE[z]["nome"], f'median {usd(NAZ["z"][z][1])} · {ZONE[z]["rischio"].lower()}') for z in ZONE_ORD if ZONE[z]["pag"] and z in NAZ["z"]]
    corpo = f"""<div class="pull card"><p class="lead" style="margin:0">Your flood zone is the area on FEMA's Flood Insurance Rate Map where the building stands. Zones starting with A or V are high-risk areas (the "special flood hazard area"); zone X is moderate to low risk. Under Risk Rating 2.0 the zone is no longer the only price factor, but it still tracks the cost closely.</p></div>
<h2>Median cost by flood zone</h2>
{tabella_zone(NAZ)}
<h2>Zone guides</h2>
{griglia(voci)}
<p class="small">Zone definitions: <a href="{FS_ZONE}" rel="noopener">FEMA FloodSmart, "What is my flood zone"</a> and the FEMA data dictionary, checked on {data_lunga(CONTROLLO_FS)}.</p>
{NON_QUOTE}
{fonte_box()}"""
    testata = banda("Flood insurance cost · flood zones", "Flood insurance cost by flood zone",
                    f"What NFIP home policies cost in each FEMA flood zone, from {intero(NAZ['h'][0])} policies in force on {data_lunga(RIF)}.")
    pagina("flood-zones/", f"Flood insurance cost by flood zone (AE, VE, A, X) | {NOME}",
           "Median annual cost of NFIP flood insurance in each FEMA flood zone: VE, AE, A, AO, AH and X, from FEMA policy data.",
           corpo, briciole=[("Flood zones", "flood-zones/")], testata=testata)


# ---------------------------------------------------------------- sezione "Disaster declarations and IRS tax relief" (dati/disastri.json)
# Dati da raccolta/disastri.py (OpenFEMA DisasterDeclarationsSummaries v2 + comunicati IRS). Pagine: /disaster-relief/ (indice),
# una per Stato, una per contea solo dove c'è una dichiarazione negli ultimi 24 mesi e domanda (regola in dati/disastri-domanda.json).
DIS = carica("disastri.json") if (DATI / "disastri.json").exists() else None
DIS_URL = "disaster-relief/"
DA_URL = "https://www.disasterassistance.gov/"
IRS_INDICE = "https://www.irs.gov/newsroom/tax-relief-in-disaster-situations"
IRS_FAQ = "https://www.irs.gov/businesses/small-businesses-self-employed/faqs-for-disaster-victims"
TIPO_DICH = {"DR": "Major disaster", "EM": "Emergency", "FM": "Fire management"}
PROG = [("IA", "Individual assistance", "help for households: FEMA's Individuals and Households Program"),
        ("PA", "Public assistance", "help for state and local governments and some nonprofits to repair public facilities"),
        ("HM", "Hazard mitigation", "funding to reduce the risk from future disasters")]
AVVISO_DIS = (f'<p class="nota">{ico("info")}<strong>Official notices, not advice.</strong> This page reports what FEMA and the IRS have published. '
              'Whether a postponed deadline or a FEMA program applies to you depends on where you live or do business and on your situation: '
              f'check with the IRS or a tax professional, and apply for FEMA help only through <a href="{DA_URL}" rel="noopener">DisasterAssistance.gov</a>, FEMA\'s official site.</p>')


def _dis_nomi():
    sys.path.insert(0, str(RADICE / "raccolta"))
    from disastri import STATI_NOMI  # noqa: E402
    return STATI_NOMI


if DIS:
    DIS_NOMI = _dis_nomi()
    DICH = DIS["dichiarazioni"]
    AREE = DIS["aree"]
    IRS_N = DIS["irs"]
    DIS_OGGI = DIS["letto_il"]
    DIS_DA = DIS["finestra_da"]
    DIS_STATI = sorted({a["st"] for a in AREE.values()} | {c["st"] for c in IRS_N} | set(DIS["aree_speciali"]),
                       key=lambda s: DIS_NOMI.get(s, s))
    LASTMOD = {}


def titolo_fema(t):
    """'SEVERE STORMS, STRAIGHT-LINE WINDS, AND FLOODING' -> 'Severe Storms, Straight-Line Winds, and Flooding'."""
    t = t.title()
    t = re.sub(r"(?<=\s)(And|Of|The|In|On|For|To|A)(?=\s)", lambda m: m.group(1).lower(), t)
    return re.sub(r"'S\b", "'s", t)


def nome_dis_stato(st):
    return DIS_NOMI.get(st, st)


def url_dis_stato(st):
    return DIS_URL + slug(nome_dis_stato(st)) + "/"


def nome_dis_contea(f):
    n = AREE[f]["nome"]
    return n[:-5] + " (city)" if n.endswith(" city") else n


def url_dis_contea(f):
    return url_dis_stato(AREE[f]["st"]) + slug(AREE[f]["nome"]) + "/"


def ha_pagina_dis(f):
    return bool(AREE.get(f, {}).get("pagina"))


def aperto(c):
    return bool(c["scadenza"]) and c["scadenza"] >= DIS_OGGI


def evento_irs(c):
    t = c["titolo"]
    m = re.search(r"(?:impacted by|affected by|victims of) (?:the )?(.+?)(?: in the | in | that |;|, various| various)", t)
    e = m.group(1) if m else re.sub(r"^IRS[^,;]*?(announces|provides) tax relief for ", "", t)
    return e[:1].upper() + e[1:]


def irs_stato(st):
    return [c for c in IRS_N if c["st"] == st]


def irs_contea(f):
    st = AREE[f]["st"]
    return [c for c in IRS_N if c["st"] == st and (f in (c["contee"] or []) or c.get("intero_stato"))]


def programmi(riga):
    """riga = [codice, IH, IA, PA, HM] -> {'IA': bool, 'PA': bool, 'HM': bool}"""
    return {"IA": bool(riga[1] or riga[2]), "PA": bool(riga[3]), "HM": bool(riga[4])}


def pill(on, testo):
    return f'<span class="pill{" on" if on else ""}">{testo}: {"yes" if on else "no"}</span>'


def link_fema_api(filtro):
    sel = "femaDeclarationString,declarationType,declarationDate,incidentType,declarationTitle,designatedArea,ihProgramDeclared,iaProgramDeclared,paProgramDeclared,hmProgramDeclared,incidentBeginDate,incidentEndDate,lastIAFilingDate"
    par = {"$filter": filtro, "$select": sel, "$orderby": "declarationDate desc", "$top": "1000"}
    return f"{API}/v2/DisasterDeclarationsSummaries?" + "&".join(f"{k}={quote(v, safe=',()')}" for k, v in par.items())


def fonte_dis(filtro, notices=()):
    F = DIS["fonti"]["fema"]
    righe_irs = "".join(f'<li><a href="{h(c["url"])}" rel="noopener">IRS news release {h(c["codice"])}</a>'
                        f'{", published " + data_breve(c["pubblicato"]) if c.get("pubblicato") else ""}'
                        f'{", updated " + data_breve(c["aggiornato"]) if c.get("aggiornato") else ""}.</li>' for c in notices)
    return f"""<aside class="fonti-box" aria-label="Sources">
<h2>{ico("doc")}Where this comes from</h2>
<ul>
<li><a href="{h(F["dizionario"])}" rel="noopener">FEMA OpenFEMA – {h(F["titolo"])} (v{F["versione"]})</a>: every federal disaster declaration with the counties and programs it covers. We read the declarations made since {data_lunga(DIS_DA)}. FEMA describes this dataset as raw data from its emergency management system, "subject to a small percentage of human error".</li>
<li><a href="{IRS_INDICE}" rel="noopener">IRS: Tax relief in disaster situations</a> and the IRS news releases it lists for {DIS_OGGI[:4]} and {int(DIS_OGGI[:4]) - 1}.</li>
{righe_irs}</ul>
<p>Read by our script on <strong data-letto>{data_lunga(DIS_OGGI)}</strong>{" at " + DIS["letto_alle_utc"] + " UTC" if DIS.get("letto_alle_utc") else ""}; we check for new declarations and IRS notices every week. Check the raw FEMA records yourself:
<a href="{h(link_fema_api(filtro))}" rel="noopener nofollow">OpenFEMA API (JSON)</a>. Sentences in quotation marks are copied from the IRS releases.</p>
</aside>"""


def tabella_dich(righe, contea=None):
    """righe: lista di [codice, IH, IA, PA, HM] (contea) o codici (Stato)."""
    out = []
    for r in righe:
        k = r[0] if isinstance(r, list) else r
        D = DICH[k]
        if isinstance(r, list):
            P = programmi(r)
        else:
            P = {"IA": D["ih"] or D["ia"], "PA": D["pa"], "HM": D["hm"]}
        inc = data_breve(D["inizio"]) + (f" – {data_breve(D['fine'])}" if D.get("fine") and D["fine"] != D["inizio"] else "") if D.get("inizio") else "–"
        aree = "" if contea else f'<td class="n" data-l="Areas">{intero(D["aree"])}</td>'
        out.append(f'<tr data-dich="{k}"><td><strong>{k}</strong><br><span class="small">{h(titolo_fema(D["titolo"]))}</span></td>'
                   f'<td data-l="Type">{TIPO_DICH.get(D["tipo"], D["tipo"])}<br><span class="small">{h(D["incidente"])}</span></td>'
                   f'<td data-l="Incident">{inc}</td><td data-l="Declared" class="n" data-data="{D["data"]}">{data_breve(D["data"])}</td>'
                   f'<td data-l="">{pill(P["IA"], "Individual aid")} {pill(P["PA"], "Public aid")} {pill(P["HM"], "Mitigation")}</td>{aree}</tr>')
    th_aree = "" if contea else '<th class="n">Areas</th>'
    return (f'<div class="tab"><table class="ot dt"><thead><tr><th>Declaration</th><th>Type</th><th>Incident period</th><th class="n">Declared</th>'
            f'<th>Programs{" here" if contea else ""}</th>{th_aree}</tr></thead><tbody>{"".join(out)}</tbody></table></div>')


def scheda_irs(c, evidenzia=None):
    stato = ("open" if aperto(c) else "passed")
    lista = ""
    if c["contee"]:
        voci = []
        for f in c["contee"]:
            n = h(nome_dis_contea(f)) if f in AREE else h(f)
            if f == evidenzia:
                voci.append(f"<strong>{n}</strong>")
            elif ha_pagina_dis(f):
                voci.append(f'<a href="{{rel}}{url_dis_contea(f)}">{n}</a>')
            else:
                voci.append(n)
        lista = f'<p class="small"><strong>{len(c["contee"])} {"county" if len(c["contee"]) == 1 else "counties"} named in the notice:</strong> {", ".join(voci)}.</p>'
        if c.get("nomi_non_trovati"):
            lista += ('<p class="small">The notice also names ' + ", ".join(f"“{h(n)}”" for n in c["nomi_non_trovati"]) +
                      ", which we could not match to a county in the Census list (for example an independent city or a name spelled "
                      "differently): read the official list in the IRS release.</p>")
    elif c.get("intero_stato"):
        lista = '<p class="small">The notice covers the whole state or territory.</p>'
    else:
        lista = ('<p class="small">The notice does not name the areas in a form we can match to counties automatically'
                 + (" (for example a tribal area, a territory or a name we could not find in the Census list)" if c.get("motivo_senza_contee") else "")
                 + ': read the official list in the IRS release.</p>')
    fonte = "a FEMA disaster declaration" if c.get("dichiarato_da") == "FEMA" else (f"a disaster declaration by the {h(c['dichiarato_da'])}" if c.get("dichiarato_da") else "a disaster declaration")
    return f"""<article class="card irs-card" data-irs="{h(c["codice"])}" data-scadenza="{c["scadenza"] or ""}">
<p class="irs-top"><span class="pill{" on" if aperto(c) else ""}">{"Open" if aperto(c) else "Deadline passed"}</span> <strong>{h(c["codice"])}</strong>{" · published " + data_breve(c["pubblicato"]) if c.get("pubblicato") else ""}{" · updated " + data_breve(c["aggiornato"]) if c.get("aggiornato") else ""}</p>
<h3>{h(evento_irs(c))}: deadlines postponed to {data_lunga(c["scadenza"]) if c["scadenza"] else "see the notice"}</h3>
{f'<blockquote class="irs">“{h(c["frase_scadenza"])}”</blockquote>' if c.get("frase_scadenza") else ""}
{f'<blockquote class="irs">“{h(c["frase_localita"])}”</blockquote>' if c.get("frase_localita") else ""}
{lista}
<p class="small">The relief follows {fonte}. The new date has {"not passed yet" if stato == "open" else "passed"} (as of {data_breve(DIS_OGGI)}). <a href="{h(c["url"])}" rel="noopener">Read the IRS release {h(c["codice"])}</a>.</p>
</article>"""


def pl(n):
    return "" if n == 1 else "s"


def taglia(t, n=300):
    """Meta description: al massimo n caratteri, tagliata a fine parola."""
    return t if len(t) <= n else t[:n - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def titolo_corto(varianti):
    """Il primo titolo che sta in 70 caratteri, con " | FloodCost" se c'entra."""
    for v in varianti:
        if len(v) + len(" | " + NOME) <= 70:
            return v + " | " + NOME
    for v in varianti:
        if len(v) <= 70:
            return v
    return varianti[-1][:70]


def link_nfip(f=None, st=None):
    """Rimando alle pagine FloodCost esistenti sul premio NFIP (stessa contea o stesso Stato)."""
    if f and f in CONTEE:
        C = CONTEE[f]
        return (f'<p>{ico("house")} <strong>Flood insurance in {h(nome_contea(f))}:</strong> NFIP home policies here cost a median '
                f'<strong>{usd(C["h"][1])} a year</strong> ({intero(C["h"][0])} homes insured on {data_lunga(RIF)}). Most homeowners policies do not cover flood damage. '
                f'<a href="{{rel}}{url_contea(f)}">See flood insurance costs in {h(nome_contea(f))}</a>.</p>')
    st = st or (AREE[f]["st"] if f else None)
    if st in STATI and STATI[st].get("h"):
        S = STATI[st]
        return (f'<p>{ico("house")} <strong>Flood insurance in {h(S["nome"])}:</strong> NFIP home policies cost a median '
                f'<strong>{usd(S["h"][1])} a year</strong> ({intero(S["h"][0])} homes insured on {data_lunga(RIF)}). Most homeowners policies do not cover flood damage. '
                f'<a href="{{rel}}{url_stato(st)}">See flood insurance costs in {h(S["nome"])}</a>.</p>')
    return ""


def cosa_fare(f=None, st=None, notices=()):
    irs_l = "".join(f'<li><a href="{h(c["url"])}" rel="noopener">IRS release {h(c["codice"])}</a>: {h(evento_irs(c))}</li>' for c in notices[:3])
    return f"""<h2>Official links</h2>
<ul class="link-uff">
<li><a href="{DA_URL}" rel="noopener">DisasterAssistance.gov</a>: FEMA's official site to apply for individual assistance or check an application.</li>
<li><a href="{IRS_INDICE}" rel="noopener">IRS: Tax relief in disaster situations</a>, the list of every IRS disaster notice, and the <a href="{IRS_FAQ}" rel="noopener">IRS FAQs for disaster victims</a>.</li>
{irs_l}</ul>
{link_nfip(f, st)}"""


def frase_risposta(f):
    """Prima frase della pagina contea: dichiarazione sì/no, assistenza individuale sì/no, scadenza IRS."""
    A = AREE[f]
    nome = nome_dis_contea(f)
    d = A["d"]
    parti = []
    if d:
        u = DICH[d[0][0]]
        parti.append(f"Yes: FEMA lists {len(d)} federal disaster declaration{'s' if len(d) > 1 else ''} for {nome} since {data_lunga(DIS_DA)}; "
                     f"the latest is {d[0][0]} ({titolo_fema(u['titolo'])}), declared {data_lunga(u['data'])}.")
        con_ia = [r[0] for r in d if r[1] or r[2]]
        if con_ia:
            D = DICH[con_ia[0]]
            ia = f"Individual assistance for households: yes ({', '.join(con_ia[:3])}{'…' if len(con_ia) > 3 else ''})"
            if D.get("ultimo_ia"):
                ia += (f"; FEMA's last date to apply under {con_ia[0]} is {data_lunga(D['ultimo_ia'])}." if D["ultimo_ia"] >= DIS_OGGI else
                       f"; the last date to apply under {con_ia[0]} was {data_lunga(D['ultimo_ia'])}.")
            else:
                ia += "."
            parti.append(ia)
        else:
            parti.append("Individual assistance for households: no, these declarations do not include it for this county.")
    else:
        c0 = max(irs_contea(f), key=lambda c: c["scadenza"] or "")
        da_chi = "FEMA" if c0.get("dichiarato_da") == "FEMA" else (f"the {c0['dichiarato_da']}" if c0.get("dichiarato_da") else "a government authority")
        parti.append(f"FEMA's data shows no federal declaration for {nome} since {data_lunga(DIS_DA)}, but the IRS names the county in notice {c0['codice']}, "
                     f"which follows a disaster declaration by {da_chi}.")
        parti.append("Individual assistance from FEMA: no.")
    ap = [c for c in irs_contea(f) if aperto(c)]
    pas = [c for c in irs_contea(f) if not aperto(c) and c["scadenza"]]
    if ap:
        c = max(ap, key=lambda c: c["scadenza"])
        parti.append(f"IRS: federal tax deadlines are postponed to {data_lunga(c['scadenza'])} for {'the whole state' if c.get('intero_stato') else nome} (notice {c['codice']}).")
    elif pas:
        c = max(pas, key=lambda c: c["scadenza"])
        parti.append(f"IRS: deadlines were postponed to {data_lunga(c['scadenza'])} (notice {c['codice']}); that date has passed and no IRS notice is open for {nome} today.")
    else:
        altri = [c for c in irs_stato(A["st"]) if aperto(c) and (not c["contee"] or c.get("nomi_non_trovati")) and not c.get("intero_stato")]
        if altri:
            parti.append(f"IRS: no notice we could read names {nome}, but an open IRS notice for {nome_dis_stato(A['st'])} ({altri[0]['codice']}) names areas we could not match to counties automatically, so check the official list.")
        else:
            parti.append(f"IRS: no disaster tax relief notice since {data_lunga(DIS_DA)} names {nome}.")
    return parti


def pagina_dis_contea(f):
    A = AREE[f]
    st = A["st"]
    nome = nome_dis_contea(f)
    nst = nome_dis_stato(st)
    parti = frase_risposta(f)
    notices = irs_contea(f)
    ap = [c for c in notices if aperto(c)]
    d = A["d"]
    con_ia = any(r[1] or r[2] for r in d)
    scad = max((c["scadenza"] for c in ap), default=None)
    tiles = [(intero(len(d)), f"FEMA declaration{pl(len(d))} since {data_breve(DIS_DA)}"),
             ("Yes" if con_ia else "No", "FEMA individual assistance declared"),
             (data_breve(scad), "IRS postponed deadline") if scad else ("No", "open IRS postponed deadline today"),
             (data_breve(DICH[d[0][0]]["data"]) if d else "–", "latest FEMA declaration")]
    side = "".join(f'<div class="tile"><b>{v}</b><span>{t}</span></div>' for v, t in tiles)
    key = f"""<section class="card key pull" aria-label="Answer" data-contea="{f}" data-n-dich="{len(d)}" data-ia="{int(con_ia)}" data-irs="{scad or ''}">
<div class="key-top">{ico("alert")}<span>{h(nome)}, {h(st)}</span><span>Checked {data_breve(DIS_OGGI)}</span></div>
<div class="key-body"><div class="key-main"><p class="k-lab">Disaster declarations and tax relief</p>
{"".join(f'<p class="risposta">{h(p)}</p>' for p in parti[1:])}
</div><div class="key-side">{side}</div></div></section>"""
    corpo = [key, AD, AVVISO_DIS]
    if d:
        corpo.append(f'<h2>FEMA declarations for {h(nome)}</h2><p class="lead">Federal disaster declarations since {data_lunga(DIS_DA)} that include {h(nome)}, newest first, '
                     f'with the programs FEMA declared for this county.</p>{tabella_dich(d, contea=f)}')
        ia_aperte = [r[0] for r in d if (r[1] or r[2]) and DICH[r[0]].get("ultimo_ia") and DICH[r[0]]["ultimo_ia"] >= DIS_OGGI]
        if ia_aperte:
            corpo.append(f'<p class="small">FEMA\'s last date to apply for individual assistance: ' + "; ".join(f'{k}: <strong>{data_lunga(DICH[k]["ultimo_ia"])}</strong>' for k in ia_aperte) +
                         f' (field "lastIAFilingDate" in FEMA\'s data). Apply at <a href="{DA_URL}" rel="noopener">DisasterAssistance.gov</a>.</p>')
    corpo.append(f'<h2>IRS tax relief for {h(nome)}</h2>')
    if notices:
        corpo.append(f'<p class="lead">IRS disaster notices since {data_lunga(DIS_DA)} that name {h(nome)} or cover all of {h(nst)}, newest first.</p>' +
                     "".join(scheda_irs(c, evidenzia=f) for c in sorted(notices, key=lambda c: c["scadenza"] or "", reverse=True)))
    else:
        altri = [c for c in irs_stato(st) if (not c["contee"] or c.get("nomi_non_trovati")) and not c.get("intero_stato")]
        corpo.append(f'<p class="lead">No IRS disaster notice since {data_lunga(DIS_DA)} names {h(nome)} in a list we can read.'
                     + (f' {len(altri)} notice{"s" if len(altri) > 1 else ""} for {h(nst)} name{"" if len(altri) > 1 else "s"} areas we could not match to counties automatically: '
                        + ", ".join(f'<a href="{h(c["url"])}" rel="noopener">{h(c["codice"])}</a>' for c in altri) + "." if altri else "")
                     + f' See all notices for <a href="{{rel}}{url_dis_stato(st)}">{h(nst)}</a>.</p>')
    corpo.append(cosa_fare(f, st, notices))
    vicine = sorted((g for g in AREE if g != f and AREE[g]["st"] == st and ha_pagina_dis(g)), key=lambda g: AREE[g]["nome"])
    if vicine:
        corpo.append(f'<h2>Other counties in {h(nst)}</h2>' + griglia([(url_dis_contea(g), nome_dis_contea(g), riassunto_contea(g)) for g in vicine[:24]]) +
                     f'<p class="small"><a href="{{rel}}{url_dis_stato(st)}">All declarations and IRS notices for {h(nst)}</a></p>')
    if d:
        filtro = f"fipsStateCode eq '{f[:2]}' and fipsCountyCode eq '{f[2:]}' and declarationDate ge '{DIS_DA}'"
    else:
        filtro = f"fipsStateCode eq '{f[:2]}' and fipsCountyCode eq '{f[2:]}'"
    corpo.append(fonte_dis(filtro, notices))
    if ap:
        c = max(ap, key=lambda c: c["scadenza"])
        tv = [f"{nome}, {st}: FEMA declaration, IRS deadline {data_breve(c['scadenza'])}" if d else f"{nome}, {st}: IRS disaster deadline {data_breve(c['scadenza'])}",
              f"{nome}, {st}: IRS disaster deadline {data_breve(c['scadenza'])}"]
    else:
        tv = []
    tv += [f"{nome}, {st}: FEMA disaster declarations and IRS relief", f"{nome}, {st}: disaster declarations and IRS relief",
           f"{nome}, {st}: FEMA and IRS disaster relief"]
    titolo = titolo_corto(tv)
    descr = taglia(" ".join(parti))
    sub = h(parti[0])
    testata = banda(f"Disaster relief · {nome}, {st}", f"Disaster declarations and IRS tax relief in {nome}, {nst}", sub)
    percorso = url_dis_contea(f)
    LASTMOD[percorso] = DIS_OGGI
    pagina(percorso, titolo, descr, "\n".join(x for x in corpo if x),
           briciole=[("Disaster relief", DIS_URL), (nst, url_dis_stato(st)), (nome, percorso)], testata=testata)
    return True


def riassunto_contea(f):
    d = AREE[f]["d"]
    ia = any(r[1] or r[2] for r in d)
    ap = [c for c in irs_contea(f) if aperto(c)]
    s = (f"{len(d)} FEMA declaration{'s' if len(d) != 1 else ''}" if d else "No FEMA declaration") + (" · individual aid" if ia else "")
    if ap:
        s += f" · IRS {data_breve(max(c['scadenza'] for c in ap))}"
    return s


def pagina_dis_stato(st):
    nst = nome_dis_stato(st)
    codici = sorted({k for k, D in DICH.items() if D["st"] == st}, key=lambda k: (DICH[k]["data"], k), reverse=True)
    notices = irs_stato(st)
    ap = [c for c in notices if aperto(c)]
    contee = sorted((f for f, A in AREE.items() if A["st"] == st), key=lambda f: AREE[f]["nome"])
    con_pag = [f for f in contee if ha_pagina_dis(f)]
    n_ia = sum(1 for k in codici if DICH[k]["ih"] or DICH[k]["ia"])
    tipi = {t: sum(1 for k in codici if DICH[k]["tipo"] == t) for t in ("DR", "EM", "FM")}
    if codici:
        nomi_t = {"DR": ("major disaster", "major disasters"), "EM": ("emergency", "emergencies"), "FM": ("fire management", "fire management")}
        dett = ", ".join(f"{tipi[t]} {nomi_t[t][tipi[t] != 1]}" for t in ("DR", "EM", "FM") if tipi[t])
        ia_t = (("it does not include" if len(codici) == 1 else "none includes") + " FEMA individual assistance" if n_ia == 0 else
                f"{'it includes' if len(codici) == 1 else f'{n_ia} include' + ('s' if n_ia == 1 else '')} FEMA individual assistance")
        f1 = f"FEMA lists {len(codici)} federal disaster declaration{'s' if len(codici) != 1 else ''} for {nst} since {data_lunga(DIS_DA)} ({dett}); {ia_t}."
    else:
        f1 = f"FEMA's data shows no federal disaster declaration for {nst} since {data_lunga(DIS_DA)}."
    if ap:
        f2 = (f"The IRS has {len(ap)} open disaster notice{'s' if len(ap) != 1 else ''} for {nst}, with federal tax deadlines postponed to "
              + ", ".join(sorted({data_lunga(c['scadenza']) for c in ap})) + ".")
    elif notices:
        f2 = f"No IRS disaster notice for {nst} is open today; the latest postponed deadline was {data_lunga(max(c['scadenza'] for c in notices if c['scadenza']))}."
    else:
        f2 = f"The IRS has published no disaster tax relief notice for {nst} in {int(DIS_OGGI[:4]) - 1} or {DIS_OGGI[:4]}."
    tiles = [(intero(len(codici)), f"FEMA declaration{pl(len(codici))} since {data_breve(DIS_DA)}"), (intero(n_ia), "with individual assistance"),
             (intero(len(ap)), f"open IRS notice{pl(len(ap))}"), (intero(len(contee)), f"{'county' if len(contee) == 1 else 'counties'} in a declaration or IRS notice")]
    side = "".join(f'<div class="tile"><b>{v}</b><span>{t}</span></div>' for v, t in tiles)
    corpo = [f"""<section class="card key pull" aria-label="Summary" data-stato="{st}" data-n-dich="{len(codici)}" data-irs-aperti="{len(ap)}">
<div class="key-top">{ico("alert")}<span>{h(nst)}</span><span>Checked {data_breve(DIS_OGGI)}</span></div>
<div class="key-body"><div class="key-main"><p class="k-lab">Disaster declarations and tax relief</p><p class="risposta">{h(f2)}</p>
{f'<p class="risposta">Latest FEMA declaration: {codici[0]} ({h(titolo_fema(DICH[codici[0]]["titolo"]))}), declared {data_lunga(DICH[codici[0]]["data"])}.</p>' if codici else ""}
</div><div class="key-side">{side}</div></div></section>""", AD, AVVISO_DIS]
    if ap:
        corpo.append(f'<h2>Open IRS tax relief in {h(nst)}</h2><p class="lead">Notices whose postponed deadline has not passed yet (as of {data_lunga(DIS_OGGI)}).</p>' +
                     "".join(scheda_irs(c) for c in sorted(ap, key=lambda c: c["scadenza"])))
    vecchi = [c for c in notices if not aperto(c)]
    if vecchi:
        corpo.append(f'<h2>Earlier IRS notices for {h(nst)}</h2><div class="tab"><table class="ot"><thead><tr><th>Notice</th><th class="n">Deadline was</th><th class="n">Counties</th></tr></thead><tbody>' +
                     "".join(f'<tr><td><a href="{h(c["url"])}" rel="noopener">{h(c["codice"])}</a><br><span class="small">{h(evento_irs(c))}</span></td>'
                             f'<td class="n" data-l="Deadline was">{data_breve(c["scadenza"]) if c["scadenza"] else "–"}</td>'
                             f'<td class="n" data-l="Counties">{len(c["contee"]) if c["contee"] else ("whole state" if c.get("intero_stato") else "see notice")}</td></tr>'
                             for c in sorted(vecchi, key=lambda c: c["scadenza"] or "", reverse=True)) + "</tbody></table></div>")
    if con_pag:
        corpo.append(f'<h2>Counties in {h(nst)}</h2><p class="lead">Each county page answers three questions: is there a federal declaration, does it include individual assistance, '
                     f'and has the IRS postponed tax deadlines.</p>' + griglia([(url_dis_contea(f), nome_dis_contea(f), riassunto_contea(f)) for f in con_pag]))
    if codici:
        corpo.append(f'<h2>FEMA declarations in {h(nst)}</h2><p class="lead">Every federal declaration since {data_lunga(DIS_DA)}, newest first. '
                     f'"Areas" is the number of counties and other areas FEMA designated.</p>{tabella_dich(codici)}')
    altre = [f for f in contee if not ha_pagina_dis(f)]
    if altre:
        corpo.append('<details class="tutti"><summary>All other counties with a declaration or IRS notice (' + intero(len(altre)) + ')</summary>'
                     '<div class="tab"><table class="ot"><thead><tr><th>County</th><th class="n">Declarations</th><th>Latest</th><th>Individual aid</th></tr></thead><tbody>' +
                     "".join(f'<tr><td>{h(nome_dis_contea(f))}</td><td class="n" data-l="Declarations">{len(AREE[f]["d"])}</td>'
                             f'<td data-l="Latest">{AREE[f]["d"][0][0] if AREE[f]["d"] else "IRS notice only"}</td>'
                             f'<td data-l="Individual aid">{"yes" if any(r[1] or r[2] for r in AREE[f]["d"]) else "no"}</td></tr>' for f in altre) +
                     '</tbody></table></div><p class="small">These counties have no separate page: they have a declaration without individual assistance and no open IRS notice, '
                     'or we found few searches about them.</p></details>')
    sp = DIS["aree_speciali"].get(st) or {}
    if sp:
        corpo.append('<h3>Tribal and statewide areas in FEMA declarations</h3><p class="small">' +
                     " · ".join(f'{h(n)} ({", ".join(r[0] for r in v)})' for n, v in sorted(sp.items())) + "</p>")
    corpo.append(cosa_fare(None, st, ap or notices))
    corpo.append(fonte_dis(f"state eq '{st}' and declarationDate ge '{DIS_DA}'", notices))
    titolo = titolo_corto([f"{nst} disaster declarations and IRS tax relief ({DIS_OGGI[:4]})", f"{nst}: disaster declarations and IRS tax relief",
                           f"{nst}: FEMA declarations, IRS relief"])
    percorso = url_dis_stato(st)
    LASTMOD[percorso] = DIS_OGGI
    testata = banda(f"Disaster relief · {nst}", f"Disaster declarations and IRS tax relief in {nst}", h(f1))
    pagina(percorso, titolo, taglia(f1 + " " + f2), "\n".join(x for x in corpo if x),
           briciole=[("Disaster relief", DIS_URL), (nst, percorso)], testata=testata)
    return True


def pagina_dis_indice():
    ap = sorted((c for c in IRS_N if aperto(c)), key=lambda c: (c["scadenza"], nome_dis_stato(c["st"])))
    codici = sorted(DICH, key=lambda k: (DICH[k]["data"], k), reverse=True)
    n_pag = sum(1 for f in AREE if ha_pagina_dis(f))
    n_ia = sum(1 for k in codici if DICH[k]["ih"] or DICH[k]["ia"])
    f1 = (f"FEMA's data lists {len(codici)} federal disaster declarations made since {data_lunga(DIS_DA)} ({n_ia} with individual assistance for households), "
          f"and {len(ap)} IRS disaster notices are open today, with federal tax deadlines postponed to as late as {data_lunga(max(c['scadenza'] for c in ap))}." if ap else
          f"FEMA's data lists {len(codici)} federal disaster declarations made since {data_lunga(DIS_DA)}; no IRS disaster notice is open today.")
    righe_ap = "".join(f'<tr><td><a href="{{rel}}{url_dis_stato(c["st"])}">{h(nome_dis_stato(c["st"]))}</a></td>'
                       f'<td data-l="">{h(evento_irs(c))}<br><span class="small"><a href="{h(c["url"])}" rel="noopener">{h(c["codice"])}</a></span></td>'
                       f'<td class="n" data-l="New deadline"><strong>{data_breve(c["scadenza"])}</strong></td>'
                       f'<td class="n" data-l="Counties">{len(c["contee"]) if c["contee"] else ("whole state" if c.get("intero_stato") else "see notice")}</td></tr>' for c in ap)
    tiles = [(intero(len(codici)), f"FEMA declarations since {data_breve(DIS_DA)}"), (intero(n_ia), "with individual assistance"),
             (intero(len(ap)), "open IRS notices"), (intero(n_pag), "county pages")]
    side = "".join(f'<div class="tile"><b>{v}</b><span>{t}</span></div>' for v, t in tiles)
    st_voci = []
    for st in DIS_STATI:
        n = sum(1 for k in codici if DICH[k]["st"] == st)
        a = [c for c in irs_stato(st) if aperto(c)]
        st_voci.append((url_dis_stato(st), nome_dis_stato(st), f"{n} declaration{'s' if n != 1 else ''}" + (f" · IRS {data_breve(max(c['scadenza'] for c in a))}" if a else "")))
    corpo = f"""<section class="card key pull" aria-label="Summary" data-n-dich="{len(codici)}" data-irs-aperti="{len(ap)}">
<div class="key-top">{ico("alert")}<span>United States</span><span>Checked {data_breve(DIS_OGGI)}</span></div>
<div class="key-body"><div class="key-main"><p class="k-lab">Is my county a federal disaster area?</p>
<p class="risposta">Pick your state below, then your county. Each county page says whether there is a federal disaster declaration, whether FEMA declared individual assistance, and whether the IRS has postponed tax deadlines, with the official sentence and link.</p>
</div><div class="key-side">{side}</div></div></section>
{AD}
<h2>IRS tax relief open today</h2>
<p class="lead">IRS disaster notices whose postponed deadline has not passed yet (as of {data_lunga(DIS_OGGI)}), soonest first. The IRS postpones many federal filing and payment deadlines for people who live or have a business in the covered area.</p>
<div class="tab"><table class="ot"><thead><tr><th>State</th><th>Event and notice</th><th class="n">New deadline</th><th class="n">Counties</th></tr></thead><tbody>{righe_ap}</tbody></table></div>
{AVVISO_DIS}
<h2>Choose your state</h2>
{griglia(st_voci)}
<h2>Newest FEMA declarations</h2>
<p class="lead">The {min(25, len(codici))} most recent federal declarations, newest first. Open a state for the full list and its counties.</p>
{tabella_dich(codici[:25])}
<h2>What the terms mean</h2>
<div class="cols"><div class="card"><h3 style="margin-top:0">Types of declaration</h3><p class="small"><strong>Major disaster (DR)</strong> and <strong>emergency (EM)</strong> declarations are made by the President at a governor's or tribal leader's request; <strong>fire management (FM)</strong> declarations help pay to fight a wildfire. A county is in a declaration when FEMA lists it as a designated area.</p></div>
<div class="card"><h3 style="margin-top:0">Programs</h3><p class="small">{" ".join(f"<strong>{n}</strong>: {d}." for _, n, d in PROG)} A declaration can include some programs and not others, and the programs can differ from county to county.</p></div></div>
<div class="cols" style="margin-top:16px"><div class="card"><h3 style="margin-top:0">IRS tax relief</h3><p class="small">After a disaster declaration the IRS can postpone federal tax deadlines for people and businesses in the covered area. The IRS writes the covered counties in each news release; some recent releases follow a state's own disaster declaration, not FEMA's. In its releases the IRS writes that it "automatically identifies taxpayers located in the covered disaster area and applies filing and payment relief".</p></div>
<div class="card"><h3 style="margin-top:0">What this site is</h3><p class="small">{NOME} is an independent site about flood insurance costs, built on FEMA's open data. This section gathers the official declarations and IRS notices by county so you can find yours quickly. It is not affiliated with FEMA or the IRS and gives no tax or legal advice.</p></div></div>
{cosa_fare(None, None, ap)}
{fonte_dis(f"declarationDate ge '{DIS_DA}'", ())}"""
    testata = banda("FEMA + IRS · checked every week", "Disaster declarations and IRS tax relief by county", h(f1))
    LASTMOD[DIS_URL] = DIS_OGGI
    pagina(DIS_URL, titolo_corto(["Disaster declarations and IRS tax relief by county"]),
           taglia(f"{f1} Find your state and county: FEMA declaration, individual assistance and the IRS deadline, with official links."),
           corpo, briciole=[("Disaster relief", DIS_URL)], testata=testata)


def sezione_disastri():
    if not DIS:
        return {"stati": 0, "contee": 0}
    pagina_dis_indice()
    n_s = sum(pagina_dis_stato(st) for st in DIS_STATI)
    n_c = sum(pagina_dis_contea(f) for f in sorted(AREE) if ha_pagina_dis(f))
    return {"stati": n_s, "contee": n_c}


def rimando_disastri(tipo, chiave):
    """Riga nelle pagine NFIP (Stato o contea) verso la pagina dei disastri, se esiste."""
    if not DIS:
        return ""
    if tipo == "contea" and ha_pagina_dis(chiave):
        return (f'<p class="nota">{ico("alert")}<strong>Disaster declarations:</strong> {h(riassunto_contea(chiave))}. '
                f'<a href="{{rel}}{url_dis_contea(chiave)}">FEMA declarations and IRS tax relief in {h(nome_dis_contea(chiave))}</a>.</p>')
    st = chiave if tipo == "stato" else None
    if st and st in DIS_STATI:
        return (f'<p class="nota">{ico("alert")}<strong>Disaster declarations:</strong> see <a href="{{rel}}{url_dis_stato(st)}">FEMA declarations and IRS tax relief in {h(nome_dis_stato(st))}</a>, county by county.</p>')
    return ""


# ---------------------------------------------------------------- pagine fisse
def metodologia():
    dp, dc, dpen = (FONTI["dataset"][k] for k in ("NfipPolicies", "NfipClaims", "NfipResidentialPenetrationRates"))
    s = FONTI["soglie"]
    corpo = f"""<div class="testo">
<h2>The data</h2>
<p>Everything on this site comes from FEMA's open data platform, <strong>OpenFEMA</strong>, retrieved through its API on {data_lunga(FONTI["scaricato_il"])}:</p>
<ul>
<li><a href="{URL_DIZ_POL}" rel="noopener">{h(dp["title"])}, version {dp["version"]}</a> ({intero(dp["recordCount"])} records, all NFIP policy transactions since 2009; FEMA last updated it on {data_lunga(dp["lastDataSetRefresh"])}). API: <code>{API}/v{dp["version"]}/NfipPolicies</code>.</li>
<li><a href="{URL_DIZ_CL}" rel="noopener">{h(dc["title"])}, version {dc["version"]}</a> ({intero(dc["recordCount"])} claims since 1978; updated {data_lunga(dc["lastDataSetRefresh"])}). API: <code>{API}/v{dc["version"]}/NfipClaims</code>.</li>
<li><a href="{URL_DIZ_PEN}" rel="noopener">{h(dpen["title"])}, version {dpen["version"]}</a> (share of homes with NFIP flood insurance, by county; updated {data_lunga(dpen["lastDataSetRefresh"])}).</li>
</ul>
<p>FEMA removes names, street addresses and exact locations before publishing these files. The older "FIMA NFIP" version 2 datasets were retired on October 15, 2026; this site uses the current versions above.</p>
<h2>Which policies we count</h2>
<p>A policy is counted if it was <strong>in force on {data_lunga(RIF)}</strong>: it started on or before that day, it had not expired, and it had not been cancelled by then. In practice we take the policies whose current term started between {data_lunga(str(date.fromordinal(date.fromisoformat(str(int(RIF[:4]) - 1) + RIF[4:]).toordinal() + 1)))} and {data_lunga(RIF)}. In FEMA's data, practically every home policy in force on that date started in that window (home policies run for one year). A small number of multi-year condominium association policies (about 0.7% of all policies) started earlier and are not counted, so the "all policies" and "type of building" figures slightly undercount whole-building policies; figures for homes are not affected. Records with a zero or negative cost (refunds and rewrites) are left out. For the year-on-year comparison we repeat the same steps for {data_lunga(RIF0)}.</p>
<h2>What "cost" means</h2>
<p>We use FEMA's <code>policyCost</code> field: "calculated in dollars by adding together calculated premium, reserve fund assessment, federal policy fee, and HFIAA surcharge" (FEMA data dictionary). It is the total yearly amount on the policyholder's bill. FEMA's <a href="{FS_PREMI}" rel="noopener">premium costs page</a> lists those charges: a reserve fund assessment of 18% of the discounted premium, an HFIAA surcharge of $25 for primary residences and $250 for other occupancies, and a federal policy fee of $47 for most policies. Each policy counts once, whatever its coverage.</p>
<h2>Homes and other buildings</h2>
<p>The headline figure on every page is for <strong>homes</strong>: single-family homes, buildings with 2 to 4 units, manufactured (mobile) homes and single condo or apartment units (FEMA occupancy codes 11, 12, 14 and 16). Policies on whole buildings with 5 or more units, condominium association policies and non-residential buildings cost much more and would distort the figure, so they appear only in the "type of building" table.</p>
<h2>Medians, percentiles and averages</h2>
<p>The <strong>median</strong> is the middle value: half of the policies cost less, half more. The <strong>middle half</strong> runs from the 25th to the 75th percentile (linear interpolation). The <strong>average</strong> (mean) is pulled up by a minority of expensive policies, so it is usually higher than the median. All amounts are rounded to the nearest dollar.</p>
<h2>Places and flood zones</h2>
<ul>
<li><strong>State</strong>: the property state in FEMA's record.</li>
<li><strong>County</strong>: the first five digits of the census block group code in the record (state and county FIPS codes); county names from the U.S. Census Bureau. A county has its own page when it has at least {s["contea"]} home policies in force.</li>
<li><strong>ZIP code</strong>: the first five digits of the ZIP code reported by the insurer. A ZIP code has its own page when it has at least {s["zip"]} home policies in force; smaller ZIP codes (with at least {MIN} home policies) appear in the search with their median.</li>
<li><strong>Flood zone</strong>: the zone used to rate the policy (<code>ratedFloodZone</code>), grouped as AE (AE, A1–A30), VE (VE, V, V1–V30), A, AO (AO, AOB), AH (AH, AHB), A99/AR, X (X, B, C) and D.</li>
</ul>
<h2>Claims</h2>
<p>Claims are counted by year of loss, from {FONTI["anno_sinistri_da"]}, where the insured property is: state and ZIP code as reported, county from the census block group code (or FEMA's county code when the block group is missing). A claim is "paid" when the building, contents and Increased Cost of Compliance payments add up to more than zero. Amounts are in dollars of the time, not adjusted for inflation.</p>
<h2>Privacy and small numbers</h2>
<p>We never publish a single policy or claim. Any group with fewer than <strong>{MIN}</strong> policies (or claims) is not shown, neither its count nor its amounts, and we do not publish minimum or maximum values.</p>
<h2>Limits</h2>
<ul>
<li><strong>Not a quote.</strong> These are prices other policyholders paid. A price for your building depends on its elevation, foundation, replacement cost, the coverage and deductible you choose and more (<a href="{FS_PREMI}" rel="noopener">FEMA FloodSmart: premium costs</a>).</li>
<li><strong>NFIP only.</strong> Private flood insurance is not in FEMA's data and is not included.</li>
<li><strong>Who buys matters.</strong> Most policies in high-risk zones are bought because a lender requires them; in zone X they are often voluntary. Medians describe the people who bought, not every building.</li>
<li><strong>Yearly increase caps.</strong> FEMA explains that for most policyholders the premium "cannot increase more than 18–25% per year", and that this "usually does not apply to new policies" (<a href="{FS_PREMI}" rel="noopener">FloodSmart: premium costs</a>, checked {data_lunga(CONTROLLO_FS)}). A long-time policyholder may still be moving toward the full-risk price, so two similar homes can pay different amounts.</li>
<li><strong>Reporting delays.</strong> FEMA updates the data monthly; insurers can report changes late, so recent months can move slightly at the next update.</li>
<li><strong>Geography.</strong> ZIP codes and counties are taken from FEMA's records as reported; a few records have a missing or wrong code and are counted only in the state and national figures.</li>
</ul>
<h2>Updates</h2>
<p>We refresh the data every month after FEMA's update. This edition: policies in force on {data_lunga(RIF)}, data retrieved {data_lunga(FONTI["scaricato_il"])}, pages built {data_lunga(FONTI["generato_il"])}.</p>
<h2>Check any number</h2>
<p>Each page has links to the OpenFEMA API with the filter for that area, so you can download the same records and recompute the figures. Spotted a problem? <a href="{{rel}}contact/?ref=methodology">Tell us</a>.</p>
<p class="small">This product uses the Federal Emergency Management Agency’s OpenFEMA API, but is not endorsed by FEMA. The Federal Government or FEMA cannot vouch for the data or analyses derived from these data after the data have been retrieved from the Agency's website(s).</p>
</div>"""
    testata = banda("Methodology", "How we calculate flood insurance costs", "What the data is, which policies we count, how we compute medians, and what the numbers cannot tell you.")
    pagina("methodology/", f"Methodology and sources | {NOME}",
           "How FloodCost turns FEMA's NFIP policy and claims data into median flood insurance costs: definitions, thresholds, privacy rules and limits.",
           corpo, briciole=[("Methodology", "methodology/")], testata=testata)


def about():
    corpo = f"""<div class="testo">
<p class="lead">{NOME} answers one question with official data: <em>what does flood insurance really cost here?</em></p>
<p>Most flood insurance in the United States is sold through FEMA's National Flood Insurance Program. FEMA publishes every policy and claim, without personal details, but as raw data with tens of millions of rows. We turn it into simple pages: the median cost by state, county, ZIP code and flood zone, how it changed in a year, and how often the area has flooded.</p>
<h2>Rules we follow</h2>
<ul><li>Every number comes from FEMA's OpenFEMA data, with the dataset version and the date we retrieved it on the page, and a link to the raw records.</li>
<li>No estimates of our own, no "calculators" that pretend to quote a price.</li>
<li>No groups smaller than {MIN} policies, no single policy, no personal data.</li>
<li>No advice: this is information about past prices, not a recommendation to buy or not buy insurance.</li></ul>
<h2>Who we are</h2>
<p>{NOME} is an independent project run by Massimiliano Cori. It is not affiliated with FEMA, the NFIP, any insurer or insurance agency. The site may show advertising and, in the future, a clearly marked link to compare quotes; they never change the numbers.</p>
<h2>Corrections</h2>
<p>Found a mistake? <a href="{{rel}}contact/?ref=about">Write to us</a>; we check the data and correct the page at the next update.</p></div>"""
    testata = banda("About", f"About {NOME}", "An independent site that shows what NFIP flood insurance really costs, from FEMA's public data.")
    pagina("about/", f"About | {NOME}", f"About {NOME}: an independent site that publishes what NFIP flood insurance costs, from FEMA's OpenFEMA data.",
           corpo, briciole=[("About", "about/")], testata=testata)


def contatti():
    corpo = f"""<section class="card pull"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email"></label>
<label>Page or place (optional)<input type="text" name="place" maxlength="200"></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I have read the <a href="{{rel}}privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send</button><p class="errore" data-errore hidden>Sorry, it did not work. Please try again.</p></form>
<div class="ok" data-ok hidden><strong>Thank you.</strong> We will check the data and reply by email.</div></section>"""
    testata = banda("Contact", "Contact us", "Spotted a mistake or have a question about the data? We cannot give advice on individual policies or quotes.")
    pagina("contact/", f"Contact | {NOME}", f"Contact {NOME}: report a mistake or ask about the data.", corpo, briciole=[("Contact", "contact/")], testata=testata)


def privacy():
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("en", SITO_ID, ci_sono_affiliati()) or """<h2>Cookies and visit counter</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. If we add advertising or affiliate links, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>"""
    corpo = f"""<div class="testo"><p class="small">Last updated: {MESI[OGGI.month - 1]} {OGGI.year}</p>
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. Contact: the <a href="{{rel}}contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the page or place and your message, plus the page you came from. The search box runs in your browser: what you type is not sent to us. If you switch the light or dark theme, your choice is stored in your browser only.</p>
<h2>The data on this site</h2><p>The figures come from FEMA's public OpenFEMA data, which FEMA publishes without names or addresses. We publish only totals and medians of at least {MIN} policies or claims.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). Netlify keeps technical server logs (such as IP addresses) for security. We do not sell or share your data.</p>
{cookie}
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority where you live. {MON.frase_california(SITO_ID) or 'California residents: we do not sell or share personal information.'}</p></div>"""
    testata = banda("Privacy", "Privacy notice", "What we collect (very little) and why.")
    pagina("privacy.html", f"Privacy | {NOME}", f"Privacy notice of {NOME}.", corpo, testata=testata)


# ---------------------------------------------------------------- file accessori
def indice_ricerca():
    s_keys = sorted(s for s in STATI if STATI[s].get("h"))
    s_idx = {s: i for i, s in enumerate(s_keys)}
    s = [[k, STATI[k]["nome"], url_stato(k), STATI[k]["h"][0], STATI[k]["h"][1]] for k in s_keys]
    c, c_idx = [], {}
    for k in sorted(CONTEE, key=lambda k: CONTEE[k]["nome"]):
        if CONTEE[k]["st"] in s_idx:
            c_idx[k] = len(c)
            c.append([nome_contea(k), s_idx[CONTEE[k]["st"]], url_contea(k), CONTEE[k]["h"][0], CONTEE[k]["h"][1]])
    for k, v in sorted(INDICE["contee_altre"].items(), key=lambda kv: kv[1][1]):
        if v[0] in s_idx:
            c_idx[k] = len(c)
            nm = v[1][:-5] + " (city)" if v[1].endswith(" city") else v[1]
            c.append([nm, s_idx[v[0]], "", v[2], v[3]])
    z = {}
    for k, v in INDICE["zip"].items():
        if v[0] in s_idx:
            z[k] = [s_idx[v[0]], c_idx.get(v[1], -1), v[2], v[3], v[4]]
    (SITO / "data").mkdir(parents=True, exist_ok=True)
    (SITO / "data" / "search.json").write_text(json.dumps({"s": s, "c": c, "z": z}, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
    lm = LASTMOD if DIS else {}
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{lm.get(u, FONTI['generato_il'])}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in floodcost/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = floodcost/sito, Build command vuoto, Publish directory = "."
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
    corpo = f"""<div class="pull">{blocco_cerca()}</div><p class="lead" style="margin-top:20px">Or go to the <a href="/">home page</a>, the <a href="/states/">list of states</a> or the <a href="/flood-zones/">flood zones</a>.</p>"""
    pagina("404.html", f"Page not found | {NOME}", "Page not found.", corpo, indicizza=False, assoluto=True,
           testata=banda("Error 404", "Page not found", "The page may have moved after a data update: search for your ZIP code, county or state."))


def copia_grafica():
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").iterdir():
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")


def controlli():
    err = []
    for k, v in CONTEE.items():
        if v.get("st") not in STATI:
            err.append(f"contea {k}: Stato {v.get('st')} sconosciuto")
    url_c = [url_contea(k) for k in CONTEE if CONTEE[k].get("st") in STATI]
    if len(url_c) != len(set(url_c)):
        err.append("URL di contea duplicati")
    for z, v in ZIPS.items():
        if v.get("st") not in STATI:
            err.append(f"ZIP {z}: Stato sconosciuto")
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err[:50]))


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
    scrivi_asset()
    home()
    pagina_stati()
    conti = {"stato": 0, "contea": 0, "zip": 0, "zona": 0}
    for s in sorted(STATI):
        conti["stato"] += pagina_area("stato", s)
    for c in sorted(CONTEE):
        conti["contea"] += pagina_area("contea", c)
    for z in sorted(ZIPS):
        conti["zip"] += pagina_area("zip", z)
    pagina_zone_hub()
    for z in ZONE_ORD:
        if ZONE[z]["pag"]:
            conti["zona"] += pagina_zona(z)
    dis = sezione_disastri()
    metodologia()
    about()
    contatti()
    privacy()
    indice_ricerca()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; Stati {conti['stato']}, contee {conti['contea']}, "
          f"ZIP {conti['zip']}, zone {conti['zona']}; disastri: indice, Stati {dis['stati']}, contee {dis['contee']}. "
          f"Polizze in vigore al {RIF}, dati scaricati il {FONTI['scaricato_il']}.")


if __name__ == "__main__":
    main()
