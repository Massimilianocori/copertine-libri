"""Genera il sito statico EsamiDiStato in esamidistato/sito/ a partire da esamidistato/dati/.

Uso (dalla radice del repository):
    python3 esamidistato/genera.py

Dati: professioni.json e sessioni.json (curati a mano, con fonte), sedi.json (da raccolta/raccogli.py),
citta.json (pagine città). Nessuna dipendenza esterna. Stesso motore di esameb1/genera.py.
TODO (fase 2): percentuali di abilitati per ateneo, calcolate dagli elenchi pubblici degli atenei.
"""
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
URL_SITO = "https://esamidistato.netlify.app"  # cambiare qui se il nome del sito su Netlify è diverso
NOME = "EsamiDiStato"
ALTRI_SITI = [  # blocco "Altri strumenti utili" in fondo a ogni pagina (URL dal genera.py dell'altro sito)
    ("https://esameb1.netlify.app/", "EsameB1",
     "date, scadenze e sedi dell'esame di italiano B1 per la cittadinanza (CILS, CELI, PLIDA, CERT.IT), prese dalle fonti ufficiali degli enti."),
    ("https://italy-strikes-today.netlify.app/it/", "Scioperi dei trasporti in Italia oggi e domani",
     "treni, aerei e mezzi pubblici, dal registro ufficiale del Ministero."),
]
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, proprietà https://esamidistato.netlify.app — non rimuovere

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
SITO_ID = "esamidistato"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google
AFFILIATI = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8")) if (DATI / "affiliati.json").exists() else {}  # link di affiliazione: oggi nessuno (file assente)


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_"))


def riquadro_trasparenza(corpo, lingua="it"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Alcuni link sono di affiliazione: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


OGGI = date.today()

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MUR_PAGINA = "https://www.mur.gov.it/it/aree-tematiche/universita/professioni/esami-di-stato"
ENTI = {"MUR": "Ministero dell'Università e della Ricerca", "MIM": "Ministero dell'Istruzione e del Merito",
        "Giustizia": "Ministero della Giustizia"}

professioni = json.loads((DATI / "professioni.json").read_text())
sessioni = json.loads((DATI / "sessioni.json").read_text())
sedi = json.loads((DATI / "sedi.json").read_text())
citta = json.loads((DATI / "citta.json").read_text())
PROF = {p["slug"]: p for p in professioni}


def d(iso):
    return date.fromisoformat(iso)


def data_breve(iso):
    x = d(iso)
    return f"{'1°' if x.day == 1 else x.day} {MESI[x.month - 1]} {x.year}"


def il(iso):
    """Articolo davanti alla data: "il 21 ottobre", "l'11 novembre"."""
    return "l'" if d(iso).day in (8, 11) else "il "


def future(lista):
    return [s for s in lista if d(s["data"]) >= OGGI]


def verificato_ultimo():
    date_v = [s["verificato_il"] for s in sessioni] + [s["verificato_il"] for s in sedi]
    return data_breve(max(date_v))


def sedi_di(slug):
    return [s for s in sedi if slug in s["professioni"]]


def nome_sede(s):
    return s["ateneo"]


# ---------------------------------------------------------------- identità visiva
# Palette "ateneo": blu notte istituzionale, bordeaux per le scadenze, oro come filo decorativo, carta avorio.
# Titoli in Source Serif 4 (SIL OFL, file in assets/fonts/, copiato in sito/fonts/); testo nei font di sistema.
MESI_BREVI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

ICONE = {
    "cal": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "orologio": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "campana": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "web": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "ok": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
    "attenzione": '<path d="m21.7 18-8-14a2 2 0 0 0-3.5 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3Z"/><path d="M12 9v4M12 17h.01"/>',
    "giu": '<path d="m6 9 6 6 6-6"/>',
    "freccia": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M16 13H8M16 17H8"/>',
    "edificio": '<path d="M3 21h18M5 21V10M19 21V10M9 21v-6M15 21v-6M2 10l10-7 10 7"/>',
    "laurea": '<path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12v5c3 2.5 9 2.5 12 0v-5M22 10v6"/>',
    "bilancia": '<path d="M12 3v18M8 21h8M4 7h16M7 7l-3 7a3.5 3.5 0 0 0 6 0L7 7ZM17 7l-3 7a3.5 3.5 0 0 0 6 0l-3-7Z"/>',
    "squadra": '<path d="M4 20V4l16 16Z"/><path d="M8 16v-4l4 4Z"/>',
    "euro": '<path d="M18 7.5A7 7 0 1 0 18 16.5M4 10h10M4 14h10"/>',
    "lingue": '<path d="m5 8 6 6M4 14l6-6 2-3M2 5h12M7 2h1M22 22l-5-10-5 10M14 18h6"/>',
    "persone": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "invia": '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    "lista": '<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01"/>',
    "scudo": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
}
ICONA_ENTE = {"MUR": "laurea", "MIM": "squadra", "Giustizia": "bilancia"}


def ic(nome, classe="i"):
    return f'<svg class="{classe}" aria-hidden="true" focusable="false"><use href="#i-{nome}"/></svg>'


SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
          + "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items())
          + "</defs></svg>")

# Marchio: frontone classico (le istituzioni) su un sigillo blu notte, con il punto d'oro.
MARCHIO = """<svg class="marchio" viewBox="0 0 40 40" aria-hidden="true" focusable="false">
<rect width="40" height="40" rx="10" fill="#1B2F5B"/><rect x="1.5" y="1.5" width="37" height="37" rx="8.8" fill="none" stroke="#C9A24A" stroke-width="1.2"/>
<path d="M20 8.5 31.5 15h-23Z" fill="#F5F1E6"/><circle cx="20" cy="12.6" r="1.4" fill="#C9A24A"/>
<rect x="11" y="16.6" width="3.2" height="10.4" rx=".6" fill="#F5F1E6"/><rect x="18.4" y="16.6" width="3.2" height="10.4" rx=".6" fill="#F5F1E6"/><rect x="25.8" y="16.6" width="3.2" height="10.4" rx=".6" fill="#F5F1E6"/>
<rect x="8.5" y="28.4" width="23" height="3.2" rx="1" fill="#F5F1E6"/>
</svg>"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E"
           "%3Crect width='40' height='40' rx='10' fill='%231B2F5B'/%3E%3Cpath d='M20 8.5 31.5 15h-23Z' fill='%23F5F1E6'/%3E"
           "%3Ccircle cx='20' cy='12.6' r='1.4' fill='%23C9A24A'/%3E%3Crect x='11' y='16.6' width='3.2' height='10.4' fill='%23F5F1E6'/%3E"
           "%3Crect x='18.4' y='16.6' width='3.2' height='10.4' fill='%23F5F1E6'/%3E%3Crect x='25.8' y='16.6' width='3.2' height='10.4' fill='%23F5F1E6'/%3E"
           "%3Crect x='8.5' y='28.4' width='23' height='3.2' fill='%23F5F1E6'/%3E%3C/svg%3E")

SCURO = """--bg:#0C1220;--surface:#131B2C;--surface-2:#1A2337;--ink:#EDF0F6;--ink-2:#BEC7D7;--ink-3:#97A2B6;--line:#253049;--line-2:#34415E;
--brand:#E9C977;--brand-2:#F2D88F;--on-brand:#0C1220;--brand-soft:#1B2946;--link:#A9C0F2;--bord:#FF9DAA;--bord-soft:#3A1820;
--oro:#D9B566;--oro-t:#D9B566;--tile-tm:#13234A;--warn:#FFB45E;--warn-soft:#33250F;--focus:#F2C46B;--testata:#0A1222;--hero-a:#17264B;--hero-b:#0E1833;
--ombra:0 1px 2px rgba(0,0,0,.35);color-scheme:dark"""

CSS = """
@font-face{font-family:"Source Serif 4";src:url("/fonts/source-serif-4.woff2") format("woff2");font-weight:200 900;font-style:normal;font-display:swap}
:root{--bg:#F5F3EE;--surface:#FFFFFF;--surface-2:#EFECE4;--ink:#141C2B;--ink-2:#3A4456;--ink-3:#566070;--line:#E1DCD1;--line-2:#CDC6B8;
--brand:#1B2F5B;--brand-2:#13234A;--on-brand:#FFFFFF;--brand-soft:#E6EBF5;--link:#24479A;--bord:#8C1D2F;--bord-soft:#F8E5E7;
--oro:#B08A36;--oro-t:#8A6A22;--tile-tm:#E9C977;--warn:#8A4B00;--warn-soft:#FFF2DF;--focus:#B45309;--testata:#1B2F5B;--hero-a:#1B2F5B;--hero-b:#111F42;
--serif:"Source Serif 4","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
--r:12px;--r-l:18px;--ombra:0 1px 2px rgba(20,28,43,.05),0 6px 18px rgba(20,28,43,.06);color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){""" + SCURO + """}}
:root[data-theme="dark"]{""" + SCURO + """}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-size:17px;line-height:1.6}
a{color:var(--link);text-underline-offset:2px;text-decoration-thickness:1px}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px;border-radius:6px}
.i{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
.salta{position:absolute;left:-9999px;top:8px;background:var(--surface);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:10}
.salta:focus{left:16px}
/* testata blu notte con filo d'oro */
header.top{background:var(--testata);border-bottom:2px solid var(--oro)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:62px}
.logo{display:inline-flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.28rem;color:#FFFFFF;text-decoration:none;letter-spacing:-.01em;flex:none}
.logo i{font-style:italic;color:#E9C977;font-weight:600}
.marchio{width:36px;height:36px;flex:none}
nav.menu{display:flex;align-items:center;gap:2px;white-space:nowrap;min-width:0}
nav.menu a{color:#DCE3F2;text-decoration:none;font-weight:600;font-size:.95rem;padding:8px 10px;border-radius:8px}
nav.menu a:hover{color:#FFFFFF;background:rgba(255,255,255,.1)}
nav.menu a.nav-cta{flex:none;display:inline-flex;align-items:center;gap:6px;background:#E9C977;color:#1B2F5B;margin-left:6px;padding:8px 14px}
nav.menu a.nav-cta:hover{background:#F2D88F;color:#1B2F5B}
@media (max-width:700px){.lungo{display:none}nav.menu a{padding:8px 5px;font-size:.92rem}header.top .wrap{gap:8px}
nav.menu a.nav-cta{padding:0;width:40px;height:40px;justify-content:center;margin-left:4px}.logo{font-size:1.08rem;gap:7px}.marchio{width:30px;height:30px}}
@media (max-width:420px){.logo{font-size:1rem;gap:6px}.marchio{width:28px;height:28px}nav.menu a{padding:8px 4px;font-size:.9rem}}
@media (max-width:400px){nav.menu a.nav-date{display:none}}
@media (max-width:640px){.occhiello .solo-largo{display:none}}
@media (max-width:350px){.logo-testo{display:none}}
/* titoli */
h1,h2,h3,.serif{font-family:var(--serif)}
h1{font-size:clamp(1.6rem,4.2vw,2.5rem);line-height:1.14;letter-spacing:-.015em;margin:0 0 10px;font-weight:700;text-wrap:balance}
h2{font-size:clamp(1.3rem,2.6vw,1.6rem);line-height:1.25;margin:44px 0 14px;font-weight:650;display:flex;align-items:flex-start;gap:10px}
h2 .i{color:var(--oro);width:.95em;height:.95em;margin-top:.17em}
h3{font-size:1.12rem;margin:22px 0 10px;font-weight:650}
.lead{font-size:1.1rem;color:var(--ink-2);max-width:64ch;margin:0 0 6px}
.small{font-size:.9rem;color:var(--ink-3)}
.briciole{font-size:.88rem;color:var(--ink-3);margin:0 0 10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.briciole a{color:var(--ink-3)}
.hero{padding:30px 0 6px}
.occhiello{display:inline-flex;align-items:center;gap:8px;font-size:.8rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--bord);margin-bottom:12px}
.occhiello::before{content:"";width:28px;height:2px;background:var(--oro)}
/* bacheca: prossima scadenza / prossimo esame */
.risposta{margin:22px 0 8px;border-radius:var(--r-l);background:linear-gradient(135deg,var(--hero-a),var(--hero-b));color:#FFFFFF;
display:grid;grid-template-columns:1.15fr 1fr;gap:0;box-shadow:var(--ombra);overflow:hidden;position:relative}
.risposta::after{content:"";position:absolute;inset:8px;border:1px solid rgba(233,201,119,.35);border-radius:12px;pointer-events:none}
.risposta .slot{padding:24px 26px;min-width:0}
.risposta .slot+.slot{border-left:1px solid rgba(255,255,255,.14)}
.r-et{display:flex;align-items:center;gap:8px;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#E9C977}
.r-data{font-family:var(--serif);font-size:clamp(2rem,5.4vw,3rem);font-weight:700;letter-spacing:-.02em;line-height:1.02;margin:10px 0 8px;font-variant-numeric:lining-nums}
.r-data small{font-size:.5em;font-weight:600;color:#C9D3EA}
.r-cosa{font-size:.98rem;color:#DCE3F2}
.r-cosa strong{color:#FFFFFF}
.r-nota{font-size:.85rem;color:#B9C4DD;margin:10px 0 0}
.r-piede{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between;padding:12px 26px 18px;border-top:1px solid rgba(255,255,255,.14)}
.r-piede a{color:#FFFFFF;font-weight:700;display:inline-flex;align-items:center;gap:6px}
.r-piede span{font-size:.88rem;color:#C9D3EA;display:inline-flex;align-items:center;gap:6px}
.risposta .conta{background:rgba(255,255,255,.14);color:#FFFFFF}
.risposta .conta.urg{background:#F6D7DC;color:#7A1426}
.azioni{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px;align-items:center}
.cifre{display:flex;flex-wrap:wrap;gap:8px 22px;margin:14px 0 0;padding:0;list-style:none;color:var(--ink-2);font-size:.95rem}
.cifre li{display:flex;align-items:center;gap:7px}
.cifre .i{color:var(--oro)}
.cifre strong{color:var(--ink);font-family:var(--serif);font-size:1.08em}
.conta{display:inline-flex;align-items:center;font-size:.8rem;font-weight:700;padding:3px 10px;border-radius:999px;background:var(--surface-2);color:var(--ink-2);white-space:nowrap;font-variant-numeric:tabular-nums}
.conta:empty{display:none}
.conta.urg{background:var(--bord-soft);color:var(--bord)}
/* avvisi, bottoni */
.avviso{display:flex;gap:12px;align-items:flex-start;background:var(--warn-soft);color:var(--ink);border-left:3px solid var(--warn);padding:12px 16px;border-radius:10px;font-size:.95rem;margin:18px 0}
.avviso .i{color:var(--warn);margin-top:3px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font:inherit;font-weight:700;background:var(--brand);color:var(--on-brand);border:0;
border-radius:10px;padding:12px 20px;min-height:48px;cursor:pointer;text-decoration:none;transition:background .15s,transform .15s}
.btn:hover{background:var(--brand-2)}
.btn:active{transform:scale(.98)}
.btn:disabled{opacity:.6;cursor:wait}
.btn-2{background:transparent;color:var(--link);box-shadow:inset 0 0 0 1.5px var(--line-2)}
.btn-2:hover{background:var(--brand-soft)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-l);padding:22px;box-shadow:var(--ombra)}
.badge{display:inline-flex;align-items:center;font-size:.8rem;font-weight:650;padding:3px 10px;border-radius:999px;border:1px solid var(--line-2);
background:var(--surface);color:var(--ink-2);margin:0 6px 6px 0;text-decoration:none;white-space:nowrap}
a.badge:hover{border-color:var(--link);color:var(--link)}
.badge.ente{background:var(--brand);border-color:var(--brand);color:var(--on-brand);font-weight:700;letter-spacing:.02em}
/* filtro professione (menu a tendina, schema GOV.UK) */
.filtro{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin:4px 0 16px}
.filtro label{font-weight:700;font-size:.95rem;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.filtro select{font:inherit;font-size:1rem;padding:10px 40px 10px 12px;min-height:46px;min-width:240px;max-width:100%;border:1.5px solid var(--line-2);border-radius:10px;
background:var(--surface);color:var(--ink);cursor:pointer}
.filtro select:focus{border-color:var(--link)}
.esito{font-size:.92rem;color:var(--ink-3);font-weight:600}
@media (max-width:640px){.filtro label{width:100%}.filtro select{width:100%;min-width:0}}
/* sessioni */
.sessioni{display:grid;gap:12px}
.sess{display:grid;grid-template-columns:80px minmax(0,1fr);gap:18px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px;
min-width:0;overflow-wrap:anywhere;box-shadow:var(--ombra)}
.tile{display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:10px;background:var(--brand);color:var(--on-brand);padding:9px 4px 8px;align-self:start;line-height:1;text-align:center}
.tile .tm{font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--tile-tm)}
.tile .td{font-family:var(--serif);font-size:2rem;font-weight:700;margin:5px 0 4px}
.tile .ty{font-size:.74rem;opacity:.8}
.sess .cosa{min-width:0}
.sess .tags{display:flex;flex-wrap:wrap;margin-bottom:2px}
.sess .tags .badge{margin:0 6px 6px 0}
.sess .tags .badge.oltre{display:none}
.sess.tutte .tags .badge.oltre,.sess.filtrata .tags .badge.oltre{display:inline-flex}
.sess.tutte .tags .piu{display:none}
.badge.piu{font:inherit;font-size:.8rem;font-weight:650;cursor:pointer;background:transparent;border-style:dashed;color:var(--link)}
.badge.piu:hover{border-color:var(--link)}
.sess .tags .badge[aria-current]{background:var(--brand);border-color:var(--brand);color:var(--on-brand)}
.sess .chi{font-family:var(--serif);font-weight:650;font-size:1.12rem;line-height:1.3}
.sess .giorno{font-size:.9rem;color:var(--ink-3);margin:2px 0 8px}
.scad{display:grid;grid-template-columns:auto minmax(0,1fr);gap:2px 8px;font-size:.94rem;color:var(--ink-2);padding:9px 12px;background:var(--surface-2);border-radius:10px;margin-top:8px}
.scad>.i{color:var(--ink-3);margin-top:3px}
.scad .riga>span:first-child{margin-right:2px}
.nota-comune{display:flex;gap:10px;align-items:flex-start;font-size:.9rem;color:var(--ink-2);background:var(--surface-2);border-radius:10px;padding:10px 14px;margin:0 0 14px}
.nota-comune .i{color:var(--oro);margin-top:3px}
.scad .riga{min-width:0;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.scad strong{color:var(--ink)}
.scad.urgente strong{color:var(--bord)}
.scad.chiusa{color:var(--ink-3)}
.scad.chiusa strong{color:var(--ink-3)}
.scad .nota{grid-column:2;font-size:.84rem;color:var(--ink-3)}
.fonte{font-size:.8rem;color:var(--ink-3);margin-top:8px;display:flex;gap:6px;align-items:flex-start}
.fonte .i{margin-top:2px}
.fonte a{color:var(--ink-3)}
/* griglie */
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.griglia a{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 12px;min-height:54px;
text-decoration:none;color:var(--ink);font-weight:650;line-height:1.25;overflow-wrap:normal;hyphens:auto;transition:border-color .15s,background .15s}
.griglia a .i{color:var(--brand)}
.griglia a small{display:block;font-weight:400;color:var(--ink-3);font-size:.82rem}
.griglia a:hover{border-color:var(--link);background:var(--brand-soft)}
/* sedi */
.sedi{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.sedi li{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;min-width:0;overflow-wrap:anywhere}
details .sedi li{background:var(--bg)}
.regioni{columns:2;column-gap:32px;margin-top:10px}
.regione{break-inside:avoid;margin:0 0 22px}
.regione h3{font-family:inherit;font-size:.8rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:0 0 8px;
display:flex;align-items:center;gap:8px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.regione h3 span{font-weight:700;color:var(--oro-t)}
.regione .sedi{gap:0}
.regione .sedi li{background:none;border:0;border-bottom:1px solid var(--line);border-radius:0;padding:10px 2px 12px}
.regione .sedi li:last-child{border-bottom:0}
.regione .sedi .fonte{margin-top:4px}
@media (max-width:760px){.regioni{columns:1}}
.sedi .nome{font-family:var(--serif);font-weight:650;font-size:1.05rem;display:flex;gap:8px;align-items:flex-start}
.sedi .nome .i{color:var(--oro);margin-top:4px}
.sedi .det{font-size:.92rem;color:var(--ink-2);margin-top:4px}
.sedi .det .badge{font-size:.76rem;padding:2px 8px;margin:4px 4px 0 0}
.sedi .collegamenti{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.92rem;margin-top:6px}
.sedi .collegamenti a{display:inline-flex;gap:6px;align-items:center}
details{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:0;margin:8px 0}
details summary{cursor:pointer;font-weight:650;padding:14px 16px;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px}
details summary::-webkit-details-marker{display:none}
details summary .i{transition:transform .2s;color:var(--ink-3)}
details[open] summary .i{transform:rotate(180deg)}
details>:not(summary){margin:0 16px 14px}
details>p{color:var(--ink-2)}
/* in breve */
.info dl{margin:0;display:grid;grid-template-columns:200px minmax(0,1fr);gap:0}
.info dt,.info dd{padding:12px 0;border-top:1px solid var(--line)}
.info dt{font-weight:700;color:var(--ink);display:flex;gap:8px;align-items:flex-start}
.info dt .i{color:var(--oro);margin-top:3px}
.info dd{margin:0;min-width:0;overflow-wrap:anywhere;color:var(--ink-2)}
.info dt:first-of-type,.info dd:first-of-type{border-top:0}
table.conf{width:100%;border-collapse:collapse;font-size:.95rem;background:var(--surface)}
table.conf th{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3);background:var(--surface-2)}
table.conf th,table.conf td{border-bottom:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
.tab-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
ol.passi{counter-reset:p;list-style:none;padding:0;display:grid;gap:10px}
ol.passi li{counter-increment:p;display:grid;grid-template-columns:36px minmax(0,1fr);gap:12px;align-items:start;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
ol.passi li::before{content:counter(p);display:grid;place-items:center;width:32px;height:32px;border-radius:50%;background:var(--brand);color:var(--on-brand);font-family:var(--serif);font-weight:700}
/* modulo */
.modulo-testa{display:flex;gap:12px;align-items:flex-start}
.modulo-testa .bolla{display:grid;place-items:center;width:44px;height:44px;border-radius:10px;background:var(--testata);color:#E9C977;flex:none;box-shadow:inset 0 0 0 1px rgba(233,201,119,.45)}
.modulo-testa .bolla .i{width:22px;height:22px}
.modulo-testa h2{margin:0;font-size:1.3rem}
.form{display:grid;gap:14px;margin-top:14px}
.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form input,.form select{font:inherit;font-size:1rem;padding:11px 12px;min-height:48px;border:1.5px solid var(--line-2);border-radius:10px;background:var(--bg);color:var(--ink);width:100%;min-width:0}
.form input:focus,.form select:focus{border-color:var(--link)}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:20px;height:20px;min-height:0;padding:0;margin-top:2px;flex:none;accent-color:var(--brand)}
.form .btn{width:100%}
.hp{position:absolute;left:-9999px}
.ok{display:flex;gap:10px;background:var(--brand-soft);border:1px solid var(--link);padding:14px;border-radius:10px;margin-top:12px}
.errore{color:var(--bord);font-weight:600}
.due{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:32px;align-items:start}
.due>*{min-width:0}
.due>section>h2:first-child,.due>aside>.card:first-child{margin-top:28px}
@media (min-width:861px){.due>aside{position:sticky;top:16px;align-self:start}}
.altre{display:flex;flex-wrap:wrap;gap:6px}
.altre a{font-size:.9rem;padding:5px 11px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink-2);background:var(--surface)}
.altre a:hover{border-color:var(--link);color:var(--link)}
@media (max-width:860px){.due{grid-template-columns:1fr;gap:8px}.risposta{grid-template-columns:1fr}.risposta .slot+.slot{border-left:0;border-top:1px solid rgba(255,255,255,.14)}}
@media (max-width:640px){body{font-size:16.5px}.lead{font-size:1.02rem}.hero{padding-top:22px}.card{padding:18px}.risposta .slot{padding:20px}.r-piede{padding:12px 20px 16px}.r-piede span{display:none}
.sess{grid-template-columns:1fr;gap:10px;padding:16px}.tile{flex-direction:row;align-items:baseline;justify-self:start;gap:7px;padding:6px 12px}.tile .td{font-size:1.35rem;margin:0}
.azioni .btn{flex:1 1 100%}
.info dl{grid-template-columns:1fr}.info dd{border-top:0;padding-top:0}}
/* piede */
footer.piede{margin-top:64px;background:#101B36;color:#C3CCDF;padding:36px 0 44px;font-size:.9rem;border-top:2px solid #B08A36}
footer.piede a{color:#E8EDF7}
footer.piede .logo{color:#FFFFFF}
footer.piede .piede-altri{margin-top:26px;padding-top:18px;border-top:1px solid rgba(255,255,255,.16)}
footer.piede .piede-altri h2{font-size:1rem;line-height:1.3;color:#FFFFFF;margin:0 0 8px;font-family:inherit}
footer.piede .piede-altri ul{list-style:none;padding:0;margin:0}
footer.piede .piede-altri li{margin:0 0 6px;max-width:70ch}
footer.piede .piede-altri a{font-weight:700}
.piede-griglia{display:grid;grid-template-columns:1.1fr 1.4fr;gap:28px;align-items:start}
.piede-link{display:flex;flex-wrap:wrap;gap:8px 18px;list-style:none;padding:0;margin:14px 0 0}
.piede-link a{text-decoration:none;font-weight:600}
.piede-link a:hover{text-decoration:underline}
.piede p{margin:0 0 12px;max-width:72ch}
.piede .dati{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.07);padding:6px 12px;border-radius:999px;font-weight:600;color:#E8EDF7}
.piede .dati .i{color:#E9C977}
@media (max-width:760px){.piede-griglia{grid-template-columns:1fr}}
"""

JS = """
(function(){
  var oggi=new Date();oggi.setHours(0,0,0,0);
  function giorni(iso){var p=iso.split('-');var x=new Date(+p[0],+p[1]-1,+p[2]);return Math.round((x-oggi)/86400000);}
  function conta(el,g,modo){
    el.classList.remove('urg');
    if(modo==='esame'){el.textContent=g===0?'oggi':g===1?'domani':'tra '+g+' giorni';return;}
    if(modo==='apre'){el.textContent='le domande si aprono tra '+g+(g===1?' giorno':' giorni');return;}
    el.textContent=g===0?'scade oggi':'mancano '+g+(g===1?' giorno':' giorni');if(g<=15)el.classList.add('urg');
  }
  document.querySelectorAll('.sess').forEach(function(el){
    if(giorni(el.dataset.data)<0){el.remove();return;}
    var sc=el.querySelector('.scad[data-scadenza]');
    if(!sc)return;
    var g=giorni(sc.dataset.scadenza);var t=sc.querySelector('.stato');
    var ap=sc.dataset.apertura?giorni(sc.dataset.apertura):-1;
    sc.classList.remove('urgente','chiusa');t.classList.remove('urg');
    if(g<0){sc.classList.add('chiusa');t.textContent='domande chiuse';}
    else if(ap>0){conta(t,ap,'apre');}
    else if(g===0){sc.classList.add('urgente');conta(t,g,'scad');}
    else if(g<=15){sc.classList.add('urgente');conta(t,g,'scad');}
    else{conta(t,g,'scad');}
  });
  document.querySelectorAll('.sessioni').forEach(function(box){
    var v=box.parentNode.querySelector('[data-vuoto]');
    if(v&&!box.querySelector('.sess'))v.hidden=false;
  });
  document.querySelectorAll('[data-slot]').forEach(function(slot){
    var vista=false;
    slot.querySelectorAll('[data-fino]').forEach(function(o){var ok=!vista&&giorni(o.dataset.fino)>=0;o.hidden=!ok;if(ok)vista=true;});
    var r=slot.querySelector('[data-riserva]');if(r)r.hidden=vista;
  });
  document.querySelectorAll('[data-conta]').forEach(function(el){var g=giorni(el.dataset.conta);if(g>=0)conta(el,g,el.dataset.modo);});
  document.querySelectorAll('.badge.piu').forEach(function(b){b.addEventListener('click',function(){
    var s=b.closest('.sess');s.classList.add('tutte');var a=s.querySelector('.badge.oltre');if(a)a.focus();
  });});
  document.querySelectorAll('select.filtro-prof').forEach(function(sel){
    var box=sel.closest('[data-elenco]'),esito=box.querySelector('.esito');
    sel.addEventListener('change',function(){
      var f=sel.value,n=0,nome=sel.options[sel.selectedIndex].text;
      box.querySelectorAll('.sess').forEach(function(el){
        var ok=f===''||(' '+el.dataset.prof+' ').indexOf(' '+f+' ')>=0;el.hidden=!ok;if(ok)n++;
        el.classList.toggle('filtrata',!!f);
        el.querySelectorAll('.tags .badge[data-p]').forEach(function(a){
          if(a.dataset.p===f){a.setAttribute('aria-current','true');}else{a.removeAttribute('aria-current');}
          a.hidden=!!f&&a.dataset.p!==f;
        });
        var piu=el.querySelector('.badge.piu');if(piu)piu.hidden=!!f;
      });
      if(esito)esito.textContent=f?(n+(n===1?' data per ':' date per ')+nome):'';
    });
  });
  var src=document.querySelectorAll('input[name=source]');
  var v='';try{var q=new URLSearchParams(location.search);v=q.get('ref')||q.get('utm_source')||document.referrer||'diretto';}catch(e){v='diretto';}
  src.forEach(function(i){i.value=String(v).slice(0,200);});
  document.querySelectorAll('form.avvisami').forEach(function(form){
    form.addEventListener('submit',function(ev){
      ev.preventDefault();
      var err=form.querySelector('[data-errore]');err.hidden=true;
      if(!form.checkValidity()){form.reportValidity();return;}
      var b=form.querySelector('button');b.disabled=true;
      fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:new URLSearchParams(new FormData(form)).toString()})
      .then(function(r){if(!r.ok)throw new Error(r.status);
        form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
      .catch(function(){err.hidden=false;b.disabled=false;});
    });
  });
})();
"""


def testo_conta(iso, modo):
    g = (d(iso) - OGGI).days
    if modo == "esame":
        return "oggi" if g == 0 else "domani" if g == 1 else f"tra {g} giorni"
    return "scade oggi" if g == 0 else f"mancano {g} {'giorno' if g == 1 else 'giorni'}"


def data_lunga(iso):
    x = d(iso)
    return f"{GIORNI[x.weekday()]} {data_breve(iso)}"


def pagina(percorso, titolo, descrizione, corpo, jsonld=None, base=None):
    """Scrive sito/<percorso> con la struttura comune. base: prefisso dei link (\"/\" per la 404)."""
    profondita = percorso.count("/")
    rel = base if base is not None else ("../" * profondita or "./")
    avvisami = "#avvisami" if 'id="avvisami"' in corpo else f"{rel}#avvisami"
    canonico = URL_SITO + "/" + (percorso[:-10] if percorso.endswith("index.html") else percorso)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    verifica = f'<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">\n' if GOOGLE_VERIFICA else ""
    verifica += ADSENSE_HEAD.lstrip("\n") + "\n" if ADSENSE_HEAD else ""  # AdSense (monetizzazione.json): niente finché è spento
    logo = f'{MARCHIO}<span class="logo-testo">EsamiDi<i>Stato</i></span>'
    altri_siti = "".join(f'<li><a href="{u}" rel="noopener">{n}</a>: {escape(d)} Un altro sito gratuito e indipendente dello stesso gestore.</li>'
                         for u, n, d in ALTRI_SITI)
    testo = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descrizione)}">
<link rel="canonical" href="{canonico}">
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{URL_SITO}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{canonico}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1B2F5B">
{verifica}<link rel="icon" href="{FAVICON}">
<link rel="preload" href="/fonts/source-serif-4.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
{ld}
</head>
<body>
{SPRITE}
<a class="salta" href="#contenuto">Vai al contenuto</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}" aria-label="{NOME}, pagina iniziale">{logo}</a>
<nav class="menu" aria-label="Menu">
<a class="nav-date" href="{rel}#date">Date</a><a href="{rel}#professioni">Professioni</a><a href="{rel}#citta">Città</a><a class="lungo" href="{rel}come-funziona/">Come funziona</a><a class="nav-cta" href="{avvisami}" aria-label="Avvisami">{ic("campana")}<span class="lungo">Avvisami</span></a>
</nav>
</div></header>
<main class="wrap" id="contenuto">
{corpo}{riquadro_trasparenza(corpo)}
</main>
<footer class="piede"><div class="wrap">
<div class="piede-griglia">
<div>
<a class="logo" href="{rel}">{logo}</a>
<ul class="piede-link">
<li><a href="{rel}#date">Date d'esame</a></li><li><a href="{rel}#professioni">Professioni</a></li><li><a href="{rel}#citta">Sedi per città</a></li><li><a href="{rel}come-funziona/">Come funziona</a></li><li><a href="{rel}privacy.html">Privacy</a></li>
</ul>
</div>
<div>
<p><strong>{NOME}</strong> è un sito indipendente: non è affiliato al Ministero dell'Università e della Ricerca, al Ministero dell'Istruzione e del Merito,
al Ministero della Giustizia, alle università né agli Ordini professionali. I nomi delle università e degli enti appartengono ai rispettivi titolari.
Le informazioni vengono dalle fonti ufficiali indicate accanto a ogni dato. <strong>Prima di fare la domanda leggi sempre il bando della tua sede.</strong>
Questo sito non dà consulenza: per i casi particolari chiedi alla segreteria esami di Stato della tua università o al tuo Ordine.</p>
<p><span class="dati">{ic("scudo")}Dati controllati il {verificato_ultimo()}.</span></p>
</div>
</div>
<div class="piede-altri"><h2>Altri strumenti utili</h2><ul>{altri_siti}</ul></div>
</div></footer>
<script>{JS}</script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / percorso
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo)


def link_prof(slug, rel, classe=""):
    return f'<a class="badge{classe}" data-p="{slug}" href="{rel}professione/{slug}/">{escape(PROF[slug]["nome"])}</a>'


def tile(iso):
    x = d(iso)
    return (f'<div class="tile" aria-hidden="true"><span class="tm">{MESI_BREVI[x.month - 1]}</span>'
            f'<span class="td">{x.day}</span><span class="ty">{x.year}</span></div>')


def scheda_sessione(s, rel, solo=None):
    """solo: slug della professione della pagina (mostra solo quella nei badge)."""
    profs = [solo] if solo else sorted(s["professioni"], key=lambda x: PROF[x]["nome"])
    VISIBILI = 2
    badge = "".join(link_prof(p, rel, " oltre" if i >= VISIBILI else "") for i, p in enumerate(profs))
    if len(profs) > VISIBILI:
        badge += f'<button type="button" class="badge piu">+{len(profs) - VISIBILI} {"professione" if len(profs) - VISIBILI == 1 else "professioni"}</button>'

    ente = PROF[s["professioni"][0]]["ente"]
    apertura = f' data-apertura="{s["apertura"]}"' if s.get("apertura") else ""
    dal = f'Domande dal <strong>{data_breve(s["apertura"])}</strong> ' if s.get("apertura") else "Domande "
    nota_sc = "" if nota_comune(s) else f'<span class="nota">{escape(s["nota_scadenza"])}</span>'
    scad = (f'<div class="scad" data-scadenza="{s["scadenza"]}"{apertura}>{ic("orologio")}<div class="riga"><span>{dal}entro {il(s["scadenza"])}<strong>{data_breve(s["scadenza"])}</strong></span>'
            f'<span class="stato conta"></span></div>{nota_sc}</div>')
    nota = f'<div class="small">{escape(s["nota_data"])}</div>' if s.get("nota_data") else ""
    fonte = PROF[solo]["fonte"] if solo and ente == "MIM" else s["fonte"]
    termine = (f' · termine: <a href="{escape(s["fonte_scadenza"])}" rel="noopener">nota dell\'Ufficio scolastico regionale</a>'
               if s.get("fonte_scadenza") else "")
    return f"""<article class="sess" data-data="{s['data']}" data-prof="{' '.join(s['professioni'])}">
{tile(s['data'])}
<div class="cosa"><div class="tags">{badge}</div>
<div class="chi">{escape(s['chi'])}</div>
<div class="giorno"><time datetime="{s['data']}">{data_lunga(s['data'])}</time> · inizio esame · {escape(s['sessione'])}</div>
{nota}
{scad}
<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(fonte)}" rel="noopener">atto ufficiale ({escape(ENTI[ente])})</a>, {escape(s['articolo'])}{termine} · controllato il {data_breve(s['verificato_il'])}</span></div>
</div>
</article>"""


def nota_comune(s):
    """Le note sulla scadenza uguali per più sessioni si dicono una volta sola, in testa all'elenco."""
    return sum(1 for x in sessioni if x["nota_scadenza"] == s["nota_scadenza"]) > 1


def lista_sessioni(lista, rel, con_filtri=False, solo=None):
    filtri = ""
    if con_filtri:
        opz = "".join(f'<option value="{p["slug"]}">{escape(p["nome"])}</option>'
                      for p in sorted(professioni, key=lambda p: p["nome"]))
        filtri = (f'<div class="filtro"><label>Professione <select class="filtro-prof">'
                  f'<option value="">Tutte le professioni</option>{opz}</select></label>'
                  '<span class="esito" aria-live="polite"></span></div>')
    comuni = []
    for s in lista:
        if nota_comune(s) and s["nota_scadenza"] not in comuni:
            comuni.append(s["nota_scadenza"])
    note = "".join(f'<p class="nota-comune">{ic("info")}<span>{escape(n)}</span></p>' for n in comuni)
    vuoto = ('<p data-vuoto hidden>Nessuna data futura pubblicata al momento. Le date 2027 escono di solito in primavera con le nuove '
             'ordinanze: controlliamo le fonti ufficiali ogni settimana. <a href="#avvisami">Avvisami</a>.</p>')
    return ('<div data-elenco>' + note + filtri + '<div class="sessioni">' + "\n".join(scheda_sessione(s, rel, solo) for s in lista) + "</div>" + vuoto + "</div>")


def elenco_nomi(slugs, quanti=6):
    nomi = sorted((PROF[p]["nome"] for p in slugs))
    return ", ".join(escape(n) for n in nomi[:quanti]) + ("…" if len(nomi) > quanti else "")


def risposta(lista, rel, ancora="#date", solo=None):
    """Bacheca in cima: prossima scadenza per la domanda e prossimo esame. Il JS la tiene aggiornata tra un rilascio e l'altro."""
    scadenze = sorted({s["scadenza"] for s in lista})
    opz_s, primo = [], True
    for sc in scadenze:
        stesse = [s for s in lista if s["scadenza"] == sc]
        visibile = primo and d(sc) >= OGGI
        if visibile:
            primo = False
        profs = {p for s in stesse for p in s["professioni"]}
        sess = sorted({s["sessione"] for s in stesse})
        ap = next((s["apertura"] for s in stesse if s.get("apertura")), None)
        dal = f" · domande aperte dal {data_breve(ap)}" if ap else ""
        opz_s.append(f"""<div data-fino="{sc}"{"" if visibile else " hidden"}>
<div class="r-data">{d(sc).day} {MESI[d(sc).month - 1]} <small>{d(sc).year}</small></div>
<div class="r-cosa">Domande per la <strong>{escape(", ".join(x.lower() for x in sess))}</strong>{dal}{"" if solo else f'<br>{len(profs)} {"professione" if len(profs) == 1 else "professioni"}: {elenco_nomi(profs)}'}</div>
<p style="margin:14px 0 0"><span class="conta{" urg" if (d(sc) - OGGI).days <= 15 else ""}" data-conta="{sc}" data-modo="scad">{testo_conta(sc, "scad") if d(sc) >= OGGI else ""}</span></p>
</div>""")
    riserva = ('<p data-riserva class="r-nota"{}>Nessuna domanda aperta adesso. Le date 2027 escono di solito in primavera con le nuove ordinanze.</p>'
               ).format("" if primo else " hidden")
    date_es = sorted({s["data"] for s in lista})[:8]
    opz_e = []
    for i, dt in enumerate(date_es):
        stesse = [s for s in lista if s["data"] == dt]
        profs = {p for s in stesse for p in s["professioni"]}
        sess = sorted({s["sessione"] for s in stesse})
        opz_e.append(f"""<div data-fino="{dt}"{"" if i == 0 else " hidden"}>
<div class="r-data">{d(dt).day} {MESI[d(dt).month - 1]} <small>{d(dt).year}</small></div>
<div class="r-cosa">{GIORNI[d(dt).weekday()]} · {escape(", ".join(sess))}<br>{escape("; ".join(x["chi"] for x in stesse)) if solo else f'inizio esame per {len(profs)} {"professione" if len(profs) == 1 else "professioni"}'}</div>
<p style="margin:14px 0 0"><span class="conta" data-conta="{dt}" data-modo="esame">{testo_conta(dt, "esame")}</span></p>
</div>""")
    return f"""<div class="risposta">
<div class="slot" data-slot><div class="r-et">{ic("orologio")}Ultimo giorno per la domanda</div>{"".join(opz_s)}{riserva}</div>
<div class="slot" data-slot><div class="r-et">{ic("cal")}Prossimo esame</div>{"".join(opz_e)}<p data-riserva class="r-nota" hidden>Le date del prossimo anno non sono ancora uscite.</p></div>
<div class="r-piede"><a href="{ancora}">Tutte le date {ic("freccia")}</a><span>{ic("info")}Le date valgono in tutta Italia: il bando della sede può chiedere passaggi prima.</span></div>
</div>"""


def modulo(rel, prof_scelta="", citta_scelta=""):
    opz_c = "".join(
        f'<option value="{escape(c["nome"])}"{" selected" if c["nome"] == citta_scelta else ""}>{escape(c["nome"])}</option>'
        for c in sorted(citta, key=lambda c: c["nome"]))
    opz_p = "".join(
        f'<option value="{escape(p["slug"])}"{" selected" if p["slug"] == prof_scelta else ""}>{escape(p["nome"])}</option>'
        for p in sorted(professioni, key=lambda p: p["nome"]))
    return f"""<section class="card" id="avvisami">
<div class="modulo-testa"><span class="bolla">{ic("campana")}</span><div>
<h2>Avvisami su date e scadenze</h2>
<p class="small" style="margin:4px 0 0">Gratis. Ti scriviamo quando escono le nuove date della tua professione o quando una scadenza sta per chiudere.</p></div></div>
<form class="form avvisami" name="avvisami" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="avvisami">
<input type="hidden" name="source" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>La tua email<input type="email" name="email" required autocomplete="email" placeholder="nome@esempio.it"></label>
<label>Professione
<select name="professione" required><option value="">Scegli la professione</option>{opz_p}</select></label>
<label>Città dove vuoi fare l'esame
<select name="citta" required><option value="">Scegli la città</option>{opz_c}<option value="Altra città">Altra città</option></select></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required>
<span>Accetto di ricevere email da {NOME} sulle date degli esami di Stato. Posso cancellarmi quando voglio. Ho letto la <a href="{rel}privacy.html">privacy</a>.</span></label>
<button class="btn" type="submit">{ic("campana")}Avvisami</button>
<p class="errore" data-errore hidden>Non è stato possibile inviare. Riprova tra poco.</p>
</form>
<div class="ok" data-ok hidden>{ic("ok")}<span><strong>Fatto!</strong> Ti scriveremo quando ci sono novità per la tua professione.</span></div>
</section>"""


def etichetta_fonte(url):
    """Nome leggibile della fonte: "OM 694/2026" per le ordinanze MUR, "decreto Giustizia" per l'avvocato."""
    if "giustizia" in url:
        return "decreto Giustizia"
    m = re.search(r"n\.(?:%20|\s)*(\d+)(?:%20|\s)+del(?:%20|\s)+\d+-\d+-(\d{4})", url)
    return f"OM {m.group(1)}/{m.group(2)}" if m else "ordinanza"


def scheda_sede(s, rel, prof=None, con_prof=True):
    righe = [f'{ic("pin")} ' + escape(f'{s["citta"]} ({s["sigla"]}) · {s["regione"]}')]
    if prof and s["note"].get(prof):
        righe.append(escape(s["note"][prof]))
    if con_prof:
        righe.append("Esami di Stato per: " + " ".join(link_prof(p, rel) for p in s["professioni"]))
    link = []
    if s.get("url_esami_stato"):
        link.append(f'<a href="{escape(s["url_esami_stato"])}" rel="noopener">{ic("doc")}pagina esami di Stato</a>')
    if s.get("sito"):
        link.append(f'<a href="{escape(s["sito"])}" rel="noopener">{ic("web")}sito ufficiale</a>')
    elenco = [PROF[prof]["fonte"]] if prof and PROF[prof]["fonte"] in s["fonti"] else s["fonti"]
    fonti = " · ".join(f'<a href="{escape(f)}" rel="noopener">{etichetta_fonte(f)}</a>' for f in elenco)
    icona = "bilancia" if s["tipo"] == "corte_appello" else "edificio"
    return f"""<li><div class="nome">{ic(icona)}<span>{escape(nome_sede(s))}</span></div>
<div class="det">{"<br>".join(righe)}</div>
{f'<div class="collegamenti">{"".join(link)}</div>' if link else ""}
<div class="fonte">{ic("doc")}<span>Fonte: {fonti} · controllato il {data_breve(s['verificato_il'])}</span></div></li>"""


def jsonld_sessioni(lista):
    eventi = []
    for s in lista[:20]:
        nomi = ", ".join(PROF[p]["nome"] for p in s["professioni"])
        ente = PROF[s["professioni"][0]]["ente"]
        eventi.append({
            "@type": "EducationEvent", "name": f"Esame di Stato {nomi} – {s['sessione']}", "startDate": s["data"], "endDate": s["data"], "image": URL_SITO + "/og.png",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "Place", "name": "Sedi d'esame in Italia",
                         "address": {"@type": "PostalAddress", "addressCountry": "IT"}},
            "organizer": {"@type": "Organization", "name": ENTI[ente]},
            "performer": {"@type": "Organization", "name": ENTI[ente]},
            "offers": {"@type": "Offer", "url": s["fonte"] if isinstance(s.get("fonte"), str) else URL_SITO + "/", "availability": "https://schema.org/InStock", "validFrom": s["verificato_il"]},
            "description": f"{s['chi']}. Domande entro {il(s['scadenza'])}{data_breve(s['scadenza'])}.",
        })
    return {"@context": "https://schema.org", "@graph": eventi}


def prossima_scadenza(prossime):
    aperte = sorted((s for s in prossime if d(s["scadenza"]) >= OGGI), key=lambda s: s["scadenza"])
    return aperte[0] if aperte else None


def griglia_prof(rel):
    return "".join(
        f'<a href="{rel}professione/{p["slug"]}/">{ic(ICONA_ENTE[p["ente"]])}<span>{escape(p["nome"])}<small>'
        f'{f"{len(sedi_di(p["slug"]))} sedi" if sedi_di(p["slug"]) else "istituti tecnici"}</small></span></a>'
        for p in sorted(professioni, key=lambda p: p["nome"]))


def griglia_citta(rel):
    return "".join(
        f'<a href="{rel}citta/{c["slug"]}/">{ic("pin")}<span>{escape(c["nome"])}<small>{(n := sum(1 for s in sedi if s["citta"] == c["comune"]))} {"sede" if n == 1 else "sedi"}</small></span></a>'
        for c in sorted(citta, key=lambda c: c["nome"]))


def avviso(testo):
    return f'<div class="avviso">{ic("attenzione")}<div>{testo}</div></div>'


def briciole(*voci):
    parti = [f'<a href="{h}">{escape(t)}</a>' if h else f'<span aria-current="page">{escape(t)}</span>' for t, h in voci]
    return f'<nav class="briciole" aria-label="Sei qui">{" <span aria-hidden=\"true\">›</span> ".join(parti)}</nav>'


def domanda(titolo, testo):
    return f'<details><summary>{titolo}{ic("giu")}</summary>\n<p>{testo}</p></details>'


# ---------------------------------------------------------------- pagine
def home(prossime):
    n_atenei = len({s["ateneo"].split(" - Campus")[0] for s in sedi if s["tipo"] == "ateneo"})
    corpo = f"""<section class="hero">
<span class="occhiello"><span class="solo-largo">Abilitazione professionale ·&nbsp;</span>fonti ufficiali</span>
<h1>Esami di Stato 2026: date, scadenze e sedi per ogni professione</h1>
<p class="lead">Data d'esame, ultimo giorno per la domanda e università sede d'esame, dalle ordinanze ufficiali.</p>
{risposta(prossime, "")}
<div class="azioni"><a class="btn" href="#avvisami">{ic("campana")}Avvisami per la mia professione</a><a class="btn btn-2" href="#professioni">{ic("laurea")}Scegli la professione</a></div>
<ul class="cifre"><li>{ic("laurea")}<span><strong>{len(professioni)}</strong> professioni</span></li>
<li>{ic("edificio")}<span><strong>{n_atenei}</strong> università e <strong>{sum(1 for s in sedi if s["tipo"] == "corte_appello")}</strong> Corti di appello sede d'esame</span></li>
<li>{ic("cal")}<span><strong>{len(prossime)}</strong> date in programma</span></li></ul>
</section>
{avviso("Le date valgono in tutta Italia. Ogni università pubblica poi un bando con le sue regole (domanda online, contributo, calendario delle prove). <strong>Prima di fare la domanda leggi sempre il bando della tua sede.</strong>")}
<div class="due">
<section id="date">
<h2>{ic("cal")}Prossime date degli esami di Stato</h2>
{lista_sessioni(prossime, "", con_filtri=True)}
<p class="small">Le date 2027 non sono ancora uscite (controllato il {data_breve(max(s["verificato_il"] for s in sessioni))}): di solito le ordinanze escono in primavera.</p>
</section>
<aside>
{modulo("")}
</aside>
</div>
<section id="professioni">
<h2>{ic("laurea")}Professioni</h2>
<div class="griglia">{griglia_prof("")}</div>
</section>
<section id="citta">
<h2>{ic("pin")}Sedi per città</h2>
<div class="griglia">{griglia_citta("")}</div>
<p class="small">La tua città non c'è? Ogni pagina professione ha l'elenco completo delle sedi, regione per regione.</p>
</section>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{domanda("Dove faccio la domanda?", "Per le professioni delle ordinanze del Ministero dell'Università (ingegnere, architetto, psicologo, commercialista, farmacista…) la domanda si consegna alla segreteria dell'università dove vuoi fare l'esame, entro la data indicata. Puoi scegliere una sola sede. Per geometra, perito agrario e agrotecnico la domanda passa dal Collegio; per avvocato si fa solo online sul sito del Ministero della Giustizia. Tutti i dettagli nella <a href=\"come-funziona/\">pagina Come funziona</a>.")}
{domanda("Quanto costa?", f'Per le professioni universitarie c\'è una tassa di 49,58 € più il contributo deciso da ogni ateneo (lo trovi nel bando). Per avvocato il totale è 90,91 €. Fonti: <a href="{escape(PROF["ingegnere"]["fonte"])}" rel="noopener">OM 694/2026, art. 3</a>, <a href="{escape(PROF["avvocato"]["fonte"])}" rel="noopener">decreto 3/9/2026, art. 3</a>.')}
{domanda("Ho fatto domanda per la prima sessione ma non mi sono presentato: cosa faccio?", "Puoi presentarti alla seconda sessione facendo una nuova domanda entro il 21 ottobre 2026, usando i documenti già consegnati (art. 3 delle ordinanze MUR 2026).")}
{domanda("E il medico?", "La professione di medico non compare nelle ordinanze MUR 2026 sugli esami di Stato, quindi non ha date in queste sessioni.")}
<p class="small">Ingegnere, architetto, psicologo, commercialista, biologo, farmacista, avvocato e altre professioni:
in un solo posto le date d'esame, l'ultimo giorno per fare la domanda e le università dove si può sostenere, prese dalle ordinanze ufficiali.</p>
</section>"""
    pagina("index.html", "Esami di Stato 2026: date, scadenze e sedi per professione | EsamiDiStato",
           "Date degli esami di Stato 2026 (seconda sessione dal 16 novembre), scadenze delle domande e università sede d'esame "
           "per ingegnere, architetto, psicologo, commercialista, farmacista, avvocato e altre professioni.", corpo, jsonld_sessioni(prossime))


ICONA_RIGA = {"Come è organizzato": "persone", "Come fare la domanda": "invia", "Quanto costa": "euro", "Esame in tedesco": "lingue",
              "Da sapere": "info", "Atto ufficiale": "doc"}


def pagina_professione(p, prossime):
    slug = p["slug"]
    sue = sedi_di(slug)
    rel = "../../"
    date_p = [s for s in sessioni if slug in s["professioni"]]
    date_p.sort(key=lambda s: s["data"])
    regioni = sorted({s["regione"] for s in sue})
    if sue:
        tipo = "Corti di appello" if slug == "avvocato" else "università"
        fonte_elenco = ("Elenco dell'art. 1 del decreto" if slug == "avvocato"
                        else "Elenco della tabella allegata all'ordinanza")
        blocchi = "".join(
            f'<div class="regione"><h3>{escape(r)} <span>{sum(1 for s in sue if s["regione"] == r)}</span></h3>'
            f'<ul class="sedi">{"".join(scheda_sede(s, rel, slug, con_prof=False) for s in sue if s["regione"] == r)}</ul></div>'
            for r in regioni)
        sedi_html = (f'<h2 id="sedi">{ic("edificio")}Dove si fa l\'esame: {len(sue)} {tipo}</h2>'
                     f'<p class="small">{fonte_elenco}, con la città indicata lì. Sedi divise per regione.</p><div class="regioni">{blocchi}</div>')
    else:
        sedi_html = (f'<h2 id="sedi">{ic("edificio")}Dove si fa l\'esame</h2><p>{escape(p["nota"])} L\'elenco degli istituti disponibili è nella Tabella A '
                     f'dell\'<a href="{escape(p["fonte"])}" rel="noopener">ordinanza</a>.</p>')
    righe = [("Come è organizzato", p["sezioni"]), ("Come fare la domanda", p["domanda"]), ("Quanto costa", p["costo"])]
    if p["sede_tedesco"]:
        righe.append(("Esame in tedesco", f"Per i cittadini UE residenti in Italia che vogliono l'esame in lingua tedesca: sede di {p['sede_tedesco']}."))
    if p["nota"] and sue:
        righe.append(("Da sapere", p["nota"]))
    righe.append(("Atto ufficiale", None))
    dl = "".join(
        f"<dt>{ic(ICONA_RIGA[k])}{escape(k)}</dt><dd>{escape(v) if v is not None else f'<a href=\"{escape(p['fonte'])}\" rel=\"noopener\">{escape(p['atto'])}</a> · <a href=\"{escape(p['pagina_fonte'])}\" rel=\"noopener\">pagina ufficiale</a>'}</dd>"
        for k, v in righe)
    future_p = [s for s in date_p if d(s["data"]) >= OGGI]
    gia = [s for s in date_p if d(s["data"]) < OGGI]
    passate = (f'<p class="small">Già svolta: {escape(gia[0]["sessione"].lower())}, iniziata il '
               f'{" e il ".join(data_breve(s["data"]) for s in gia)}.</p>' if gia else "")
    prima = future_p[0] if future_p else None
    sottotitolo = (f"Prossimo esame: <strong>{data_breve(prima['data'])}</strong>, domande entro {il(prima['scadenza'])}<strong>{data_breve(prima['scadenza'])}</strong>."
                   if prima else "Le date del prossimo anno non sono ancora uscite.")
    titolo_h1 = f"Esame di Stato {p['nome'].lower() if slug != 'commercialista' else 'commercialista ed esperto contabile'} 2026: date, scadenze e sedi"
    corpo = f"""<section class="hero">
{briciole(("EsamiDiStato", rel), ("Professioni", rel + "#professioni"), (p["nome"], None))}
<h1>{escape(titolo_h1)}</h1>
<p class="lead">{escape(p['nome_completo'])}. {sottotitolo}
{f"L'esame si può fare in {len(sue)} sedi in Italia." if sue else ""}</p>
{risposta(future_p, rel, solo=slug) if future_p else ""}
<div class="azioni"><a class="btn" href="#avvisami">{ic("campana")}Avvisami per {escape(p['nome'].lower())}</a><a class="btn btn-2" href="#sedi">{ic("edificio")}Dove si fa l'esame</a></div>
</section>
{avviso("Ogni sede pubblica un bando con le sue regole e il calendario delle prove. <strong>Leggi il bando della tua sede prima di fare la domanda.</strong>")}
<div class="due">
<section>
<h2 id="date">{ic("cal")}Date {escape(p['nome'].lower())} 2026</h2>
{lista_sessioni(future_p, rel, solo=slug)}
{passate}
<p class="small">Date 2027: non ancora pubblicate (controllato il {data_breve(p['verificato_il'])}).</p>
<section class="card info"><h2 style="margin-top:0">{ic("lista")}In breve</h2><dl>{dl}</dl></section>
</section>
<aside>
{modulo(rel, prof_scelta=slug)}
</aside>
</div>
<section>
{sedi_html}
</section>
<section><h2>{ic("laurea")}Altre professioni</h2><div class="altre">{"".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>' for x in sorted(professioni, key=lambda x: x["nome"]) if x != p)}</div></section>"""
    n = f" e {len(sue)} sedi" if sue else ""
    pagina(f"professione/{slug}/index.html",
           f"Esame di Stato {p['nome'].lower()} 2026: date, scadenze{n} | EsamiDiStato",
           f"Esame di Stato {p['nome'].lower()} 2026: date d'inizio, ultimo giorno per la domanda"
           f"{f', le {len(sue)} sedi in Italia' if sue else ''}, costi e fonti ufficiali.",
           corpo, jsonld_sessioni([s for s in prossime if slug in s["professioni"]]))


def pagina_citta(c, prossime):
    qui = [s for s in sedi if s["citta"] == c["comune"]]
    regione = qui[0]["regione"]
    rel = "../../"
    prof_qui = {p for s in qui for p in s["professioni"]}
    atenei = [s for s in qui if s["tipo"] == "ateneo"]
    corti = [s for s in qui if s["tipo"] == "corte_appello"]
    blocchi = f'<ul class="sedi">{"".join(scheda_sede(s, rel) for s in atenei + corti)}</ul>'
    mancano = [p for p in sorted(professioni, key=lambda p: p["nome"]) if p["slug"] not in prof_qui and sedi_di(p["slug"])]
    righe_m = []
    for p in mancano:
        vicine = [s for s in sedi_di(p["slug"]) if s["regione"] == regione]
        dove = ", ".join(f'{escape(s["ateneo"])} ({escape(s["citta"])})' for s in vicine) or "nessuna sede nella regione"
        righe_m.append(f'<li><a href="../../professione/{p["slug"]}/">{escape(p["nome"])}</a>: {dove}</li>')
    nota_mancano = ""
    nota_avv = (" Per avvocato la Corte di appello giusta dipende dal distretto del tuo Consiglio dell'ordine: leggi il bando."
                if any(p["slug"] == "avvocato" for p in mancano) else "")
    if righe_m:
        nota_mancano = (f'<h2>{ic("pin")}Professioni senza sede a {escape(c["nome"])}</h2>'
                        f'<p class="small">Sedi nella stessa regione ({escape(regione)}).{nota_avv}</p><ul>{"".join(righe_m)}</ul>')
    date_c = [s for s in prossime if any(p in prof_qui for p in s["professioni"])]
    tabella = "".join(
        f'<tr><td><a href="../../professione/{p}/">{escape(PROF[p]["nome"])}</a></td><td>'
        f'{"<br>".join(escape(s["ateneo"]) for s in qui if p in s["professioni"])}</td></tr>'
        for p in sorted(prof_qui, key=lambda x: PROF[x]["nome"]))
    altre = "".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>' for x in sorted(citta, key=lambda x: x["nome"]) if x != c)
    corpo = f"""<section class="hero">
{briciole(("EsamiDiStato", rel), ("Città", rel + "#citta"), (c["nome"], None))}
<h1>Esami di Stato a {escape(c['nome'])} 2026: sedi, date e scadenze</h1>
<p class="lead">A {escape(c['nome'])} si può sostenere l'esame di Stato per <strong>{len(prof_qui)} professioni</strong>
in {len(atenei)} {"università" if len(atenei) != 1 else "università"}{f" e alla Corte di appello (avvocato)" if corti else ""}.
Le date sono le stesse in tutta Italia; la domanda va fatta alla sede scelta.</p>
{risposta(date_c, rel) if date_c else ""}
<div class="azioni"><a class="btn" href="#avvisami">{ic("campana")}Avvisami per {escape(c['nome'])}</a><a class="btn btn-2" href="#sedi">{ic("edificio")}Sedi a {escape(c['nome'])}</a></div>
</section>
{avviso("Ogni sede pubblica un bando con regole e calendario delle prove: <strong>leggilo prima di fare la domanda.</strong>")}
<div class="due">
<section>
<h2>{ic("laurea")}Quale professione, dove</h2>
<div class="tab-wrap"><table class="conf"><thead><tr><th>Professione</th><th>Sede a {escape(c['nome'])}</th></tr></thead><tbody>{tabella}</tbody></table></div>
<h2 id="sedi">{ic("edificio")}Sedi d'esame a {escape(c['nome'])}</h2>
{blocchi}
{nota_mancano}
<h2 id="date">{ic("cal")}Prossime date (valide anche a {escape(c['nome'])})</h2>
{lista_sessioni(date_c, rel)}
</section>
<aside>
{modulo(rel, citta_scelta=c['nome'])}
</aside>
</div>
<section><h2>{ic("pin")}Altre città</h2><div class="altre">{altre}</div></section>"""
    pagina(f"citta/{c['slug']}/index.html",
           f"Esami di Stato {c['nome']} 2026: sedi, date e scadenze | EsamiDiStato",
           f"Dove fare l'esame di Stato a {c['nome']}: {len(qui)} sedi per {len(prof_qui)} professioni, "
           "date della seconda sessione 2026 e scadenze delle domande.", corpo)


def come_funziona():
    righe = "".join(
        f"<tr><td><a href='../professione/{p['slug']}/'>{escape(p['nome'])}</a></td><td>{escape(ENTI[p['ente']])}</td>"
        f"<td>{len(sedi_di(p['slug'])) or 'istituti tecnici'}</td><td><a href='{escape(p['fonte'])}' rel='noopener'>{escape(p['atto'].split(' (')[0])}</a></td></tr>"
        for p in sorted(professioni, key=lambda p: (p["ente"], p["nome"])))
    om = {n: PROF[s]["fonte"] for n, s in (("694", "ingegnere"), ("693", "farmacista"), ("692", "commercialista"))}
    corpo = f"""<section class="hero">
{briciole(("EsamiDiStato", "../"), ("Come funziona", None))}
<h1>Esame di Stato: come funziona, passo per passo</h1>
<p class="lead">Spiegato in modo semplice: chi decide le date, dove si fa la domanda, quanto costa. Ogni regola ha accanto la fonte.</p>
</section>
<h2>{ic("cal")}Chi decide le date</h2>
<p>Per quasi tutte le professioni le date le fissa ogni anno il Ministero dell'Università e della Ricerca con tre ordinanze
(<a href="{escape(om['694'])}" rel="noopener">OM 694</a>, <a href="{escape(om['693'])}" rel="noopener">OM 693</a> e
<a href="{escape(om['692'])}" rel="noopener">OM 692</a> del 27 maggio 2026; elenco sulla <a href="{MUR_PAGINA}" rel="noopener">pagina del MUR</a>).
Nel 2026 ci sono due sessioni: luglio e novembre. Le date sono le stesse in tutte le sedi.</p>
<p>Fanno eccezione geometra, perito agrario e agrotecnico (ordinanze del Ministero dell'Istruzione e del Merito, una sessione l'anno)
e avvocato (bando del Ministero della Giustizia, una sessione l'anno).</p>
<h2>{ic("invia")}Come si fa la domanda (professioni universitarie)</h2>
<ol class="passi">
<li><span>Scegli <strong>una sola sede</strong> tra quelle dell'elenco della tua professione (art. 2 delle ordinanze).</span></li>
<li><span>Leggi il bando dell'università: ti dice come fare la domanda (di solito online), il contributo e il calendario delle prove.</span></li>
<li><span>Consegna la domanda entro la data dell'ordinanza: per la seconda sessione 2026 <strong>entro il 21 ottobre 2026</strong> (art. 3).</span></li>
<li><span>Paga la tassa di ammissione di 49,58 € e il contributo dell'ateneo (art. 3).</span></li>
<li><span>Presentati alla prima prova: nel 2026 la seconda sessione inizia il 16 novembre (laurea magistrale) o il 20 novembre (laurea triennale, titoli «iunior»).</span></li>
</ol>
<p>Se hai fatto domanda per la prima sessione ma eri assente, puoi rifare domanda per la seconda entro il 21 ottobre 2026 usando i documenti già consegnati (art. 3).</p>
<h2>{ic("lingue")}Esame in lingua tedesca</h2>
<p>I cittadini dell'Unione europea residenti in Italia che vogliono sostenere l'esame in tedesco devono fare domanda in una sede precisa (art. 5 delle ordinanze):
la trovi nella pagina di ogni professione.</p>
<h2>{ic("laurea")}Tutte le professioni</h2>
<div class="tab-wrap"><table class="conf"><thead><tr><th>Professione</th><th>Chi fissa le date</th><th>Sedi</th><th>Atto</th></tr></thead>
<tbody>{righe}</tbody></table></div>
<h2>{ic("info")}Professioni che qui non trovi</h2>
<p><strong>Medico</strong>: non compare nelle ordinanze MUR 2026 sugli esami di Stato. <strong>Perito industriale</strong>: non abbiamo trovato l'ordinanza 2026; la aggiungeremo quando la troviamo nelle fonti ufficiali.</p>
{modulo("../")}"""
    pagina("come-funziona/index.html", "Esame di Stato: come funziona, domanda, costi e sedi | EsamiDiStato",
           "Come funziona l'esame di Stato di abilitazione: chi fissa le date, dove e quando fare la domanda, quanto costa, "
           "con le fonti ufficiali per ogni professione.", corpo)


def privacy():
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("it", SITO_ID, ci_sono_affiliati()) or """<h2>Cookie e contatore visite</h2><p>Questo sito non usa cookie di profilazione. Per contare le visite usiamo <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, un contatore rispettoso della privacy: non usa cookie e non salva nulla nel browser, non crea profili e non conserva l'indirizzo IP, la firma completa del browser né altri identificativi. Tiene solo numeri aggregati (pagina, ora o giorno, browser, Paese, larghezza dello schermo) su server nell'Unione europea e non cede nulla a terzi; vedi l'<a href="https://www.goatcounter.com/help/privacy" rel="noopener">informativa privacy di GoatCounter</a>.</p>"""
    corpo = f"""<section class="hero">{briciole(("EsamiDiStato", "./"), ("Privacy", None))}<h1>Informativa privacy</h1><p class="small">Ultimo aggiornamento: ottobre 2026</p></section>
<h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce {NOME} come progetto indipendente. Puoi scriverci rispondendo a qualsiasi email che ti mandiamo.</p>
<h2>Quali dati raccogliamo</h2><p>Solo se compili il modulo "Avvisami": la tua email, la professione e la città che scegli, e la pagina o il link da cui arrivi (per capire quali canali funzionano).</p>
<h2>Perché</h2><p>Per mandarti avvisi sulle date e sulle scadenze degli esami di Stato. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi ritirare quando vuoi.</p>
<h2>Chi li gestisce per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i dati del modulo per nostro conto. Netlify può trattare i dati fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>
{cookie}
<h2>Per quanto tempo</h2><p>Finché resti iscritto agli avvisi. Se chiedi la cancellazione, cancelliamo i tuoi dati.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e puoi fare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>"""
    pagina("privacy.html", "Privacy | EsamiDiStato", "Informativa privacy del sito EsamiDiStato.", corpo)


def extra(urls):
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in urls)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in esamidistato/sito (ogni pubblicazione consuma crediti Netlify).
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
""")
    pagina("404.html", "Pagina non trovata | EsamiDiStato", "Pagina non trovata.",
           '<section class="hero"><span class="occhiello">Errore 404</span><h1>Pagina non trovata</h1><p class="lead">Torna al <a href="/">calendario degli esami di Stato</a>.</p>'
           f'<div class="azioni"><a class="btn" href="/">{ic("cal")}Vedi tutte le date</a><a class="btn btn-2" href="/#professioni">{ic("laurea")}Professioni</a></div></section>',
           base="/")


def controlli(prossime):
    errori = []
    for s in sessioni:
        if not s.get("fonte") or not s.get("verificato_il"):
            errori.append(f"sessione senza fonte: {s['id']}")
        if d(s["scadenza"]) >= d(s["data"]):
            errori.append(f"scadenza non prima dell'esame: {s['id']}")
        if s.get("apertura") and d(s["apertura"]) > d(s["scadenza"]):
            errori.append(f"apertura dopo la scadenza: {s['id']}")
        errori += [f"professione sconosciuta {p} in {s['id']}" for p in s["professioni"] if p not in PROF]
    for p in professioni:
        if not any(p["slug"] in s["professioni"] for s in sessioni):
            errori.append(f"professione senza sessioni: {p['slug']}")
        if p["ente"] != "MIM" and not sedi_di(p["slug"]):
            errori.append(f"professione senza sedi: {p['slug']}")
    for s in sedi:
        if not s.get("fonti") or not s.get("citta") or not s.get("regione"):
            errori.append(f"sede incompleta: {s['ateneo']}")
        errori += [f"professione sconosciuta {p} in {s['ateneo']}" for p in s["professioni"] if p not in PROF]
    for c in citta:
        if not any(s["citta"] == c["comune"] for s in sedi):
            errori.append(f"città senza sedi: {c['nome']}")
    if not prossime:
        errori.append("nessuna sessione futura")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    prossime = sorted(future(sessioni), key=lambda s: (s["data"], s["sessione"], s["id"]))
    controlli(prossime)
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}  # verifica Search Console
        shutil.rmtree(SITO)
    else:
        conserva = {}
    SITO.mkdir()
    shutil.copy(RADICE / "assets" / "og.png", SITO / "og.png")
    shutil.copytree(RADICE / "assets" / "fonts", SITO / "fonts")  # Source Serif 4 (SIL OFL), servito dal sito stesso
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    home(prossime)
    urls = [""]
    for p in professioni:
        pagina_professione(p, prossime)
        urls.append(f"professione/{p['slug']}/")
    for c in citta:
        pagina_citta(c, prossime)
        urls.append(f"citta/{c['slug']}/")
    come_funziona()
    urls.append("come-funziona/")
    privacy()
    urls.append("privacy.html")
    extra(urls)
    print(f"Sito generato in {SITO}: {len(urls)} pagine, {len(prossime)} sessioni future, {len(sedi)} sedi.")


if __name__ == "__main__":
    main()
