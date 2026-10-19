"""Genera il sito statico EsameB1 in esameb1/sito/ a partire da esameb1/dati/.

Uso (dalla radice del repository):
    python3 esameb1/genera.py

Dati: enti.json, sessioni.json (date curate a mano, con fonte), sedi.json (da raccolta/raccogli.py),
citta.json (pagine città). Nessuna dipendenza esterna.
"""
import json
import re
import shutil
import unicodedata
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://esameb1.netlify.app"  # cambiare qui se il nome del sito su Netlify è diverso
NOME = "EsameB1"
ALTRI_SITI = [  # blocco "Altri strumenti utili" in fondo a ogni pagina (URL dal genera.py dell'altro sito)
    ("https://esamidistato.netlify.app/", "EsamiDiStato",
     "date, scadenze e sedi degli esami di Stato per l'abilitazione professionale (ingegnere, psicologo, commercialista, avvocato e altre), prese dalle ordinanze ufficiali."),
]
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, proprietà https://esameb1.netlify.app

# Contatore visite GoatCounter, account condiviso "rete-siti" della rete (nessun cookie, nessun dato personale conservato).
# Il percorso inviato comprende l'host (location.host + percorso), così nel cruscotto https://rete-siti.goatcounter.com
# ogni sito si distingue dagli altri. Da localhost, da file:// e dalle reti private count.js non invia nulla
# (allow_local resta spento): le prove in locale non contano come visite. Unico punto da cambiare per tutto il sito.
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
OGGI = date.today()

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
PREFETTURA = ("https://prefettura.interno.gov.it/sites/default/files/24/2024-06/"
              "certificato_di_conoscenza_della_lingua_italiana_-ente_privato-.pdf")

enti = json.loads((DATI / "enti.json").read_text())
sessioni = json.loads((DATI / "sessioni.json").read_text())
sedi = json.loads((DATI / "sedi.json").read_text())
citta = json.loads((DATI / "citta.json").read_text())
ENTE = {e["sigla"]: e for e in enti}
SLUG_ENTE = {"CILS": "cils", "CELI": "celi", "PLIDA": "plida", "CERT.IT": "certit"}


def d(iso):
    return date.fromisoformat(iso)


def data_lunga(iso):
    x = d(iso)
    return f"{GIORNI[x.weekday()]} {x.day} {MESI[x.month - 1]} {x.year}"


def data_breve(iso):
    x = d(iso)
    return f"{x.day} {MESI[x.month - 1]} {x.year}"


def future(lista):
    return [s for s in lista if d(s["data"]) >= OGGI]


def verificato_ultimo():
    date_v = [s["verificato_il"] for s in sessioni] + [s["verificato_il"] for s in sedi]
    return data_breve(max(date_v))


# ---------------------------------------------------------------- identità visiva
# Palette "carta e tricolore": verde italiano profondo, rosso mattone per le urgenze, carta calda di fondo.
# Font: Figtree (SIL OFL, file in assets/fonts/, copiato in sito/fonts/). Icone: SVG in linea (sprite in ogni pagina).
MESI_BREVI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

ICONE = {
    "cal": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "orologio": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "campana": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "tel": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "web": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "ok": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
    "attenzione": '<path d="m21.7 18-8-14a2 2 0 0 0-3.5 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3Z"/><path d="M12 9v4M12 17h.01"/>',
    "giu": '<path d="m6 9 6 6 6-6"/>',
    "freccia": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M16 13H8M16 17H8"/>',
    "edificio": '<path d="M3 21h18M5 21V10M19 21V10M9 21v-5h6v5M2 10l10-7 10 7"/>',
    "lista": '<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01"/>',
    "scudo": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "euro": '<path d="M18 7.5A7 7 0 1 0 18 16.5"/><path d="M4 10.5h9M4 13.5h9"/>',
    "libro": '<path d="M2 4h7a3 3 0 0 1 3 3v14a2 2 0 0 0-2-2H2Z"/><path d="M22 4h-7a3 3 0 0 0-3 3v14a2 2 0 0 1 2-2h8Z"/>',
}


def ic(nome, classe="i"):
    return f'<svg class="{classe}" aria-hidden="true" focusable="false"><use href="#i-{nome}"/></svg>'


SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
          + "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items())
          + "</defs></svg>")

# Marchio: fumetto (la lingua) con "B1" e una piccola banda tricolore.
MARCHIO = """<svg class="marchio" viewBox="0 0 40 40" aria-hidden="true" focusable="false">
<path d="M8 4h24a6 6 0 0 1 6 6v15a6 6 0 0 1-6 6H17l-7.5 6.2c-.7.6-1.5.1-1.5-.7V31a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6Z" fill="var(--brand)"/>
<text x="20" y="21.6" text-anchor="middle" font-family="Figtree,system-ui,sans-serif" font-weight="800" font-size="15" fill="var(--on-brand)">B1</text>
<rect x="11" y="25.6" width="6" height="2.4" rx="1.1" fill="#3FB37F"/><rect x="17" y="25.6" width="6" height="2.4" rx="1.1" fill="#FFFFFF"/><rect x="23" y="25.6" width="6" height="2.4" rx="1.1" fill="#E4573D"/>
</svg>"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E"
           "%3Cpath d='M8 4h24a6 6 0 0 1 6 6v15a6 6 0 0 1-6 6H17l-7.5 6.2c-.7.6-1.5.1-1.5-.7V31a6 6 0 0 1-6-6V10a6 6 0 0 1 6-6Z' fill='%230B6B4F'/%3E"
           "%3Ctext x='20' y='21.6' text-anchor='middle' font-family='Arial' font-weight='700' font-size='15' fill='white'%3EB1%3C/text%3E"
           "%3Crect x='11' y='25.6' width='6' height='2.4' fill='%233FB37F'/%3E%3Crect x='17' y='25.6' width='6' height='2.4' fill='white'/%3E"
           "%3Crect x='23' y='25.6' width='6' height='2.4' fill='%23E4573D'/%3E%3C/svg%3E")

CSS = """
@font-face{font-family:"Figtree";src:url("/fonts/figtree.woff2") format("woff2");font-weight:300 900;font-style:normal;font-display:swap}
:root{--bg:#FAF7F2;--surface:#FFFFFF;--surface-2:#F3EEE5;--ink:#1B2A28;--ink-2:#40504C;--ink-3:#5A6965;--line:#E5DDD0;--line-2:#D6CCBC;
--brand:#0B6B4F;--brand-2:#08573F;--on-brand:#FFFFFF;--brand-soft:#E2F0E9;--brand-ink:#08573F;
--rosso:#B3361F;--rosso-soft:#FBE6E0;--warn:#8A4B00;--warn-soft:#FFF2DF;--focus:#1B5FD1;
--hero-a:#0B6B4F;--hero-b:#0A4F3B;--hero-ink:#FFFFFF;--hero-ink-2:#D5ECE2;
--cils:#0D5A8A;--cils-bg:#E1EEF7;--celi:#6A3E9E;--celi-bg:#EEE6F7;--plida:#9A3412;--plida-bg:#FCE9DC;--certit:#7A5E00;--certit-bg:#F8EFCB;
--r-s:8px;--r:14px;--r-l:20px;--ombra:0 1px 2px rgba(27,42,40,.06),0 4px 14px rgba(27,42,40,.06);color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0E1615;--surface:#15201E;--surface-2:#1B2826;--ink:#ECF2EF;--ink-2:#BCCAC5;--ink-3:#97A7A2;
--line:#283734;--line-2:#34463F;--brand:#4CC596;--brand-2:#6AD6AB;--on-brand:#052118;--brand-soft:#13332A;--brand-ink:#7FE0B9;
--rosso:#FF8D74;--rosso-soft:#3B1D16;--warn:#FFB45E;--warn-soft:#33250F;--focus:#8AB4FF;
--hero-a:#123D31;--hero-b:#0C2A22;--hero-ink:#ECF2EF;--hero-ink-2:#B5D6C8;
--cils:#8CC4EE;--cils-bg:#132A3B;--celi:#C9A8F0;--celi-bg:#271D36;--plida:#FFA57A;--plida-bg:#3A2116;--certit:#E8C95A;--certit-bg:#332B10;
--ombra:0 1px 2px rgba(0,0,0,.3);color-scheme:dark}}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:12px}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Figtree",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
font-size:17px;line-height:1.6;font-feature-settings:"tnum" 0}
a{color:var(--brand-ink);text-underline-offset:2px;text-decoration-thickness:1px}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px;border-radius:6px}
.i{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
.salta{position:absolute;left:-9999px;top:8px;background:var(--surface);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:10}
.salta:focus{left:16px}
/* testata */
header.top{background:var(--surface);border-bottom:1px solid var(--line);position:relative}
header.top::before{content:"";display:block;height:4px;background:linear-gradient(90deg,#0B6B4F 0 33.3%,#F4F1EA 33.3% 66.6%,#C8402A 66.6%)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:60px}
.logo{display:inline-flex;align-items:center;gap:9px;font-weight:800;font-size:1.2rem;color:var(--ink);text-decoration:none;letter-spacing:-.015em;flex:none}
.logo b{color:var(--brand);font-weight:800}
.marchio{width:34px;height:34px;flex:none}
nav.menu{display:flex;align-items:center;gap:2px;white-space:nowrap;min-width:0}
nav.menu a{color:var(--ink-2);text-decoration:none;font-weight:600;font-size:.97rem;padding:8px 10px;border-radius:999px}
nav.menu a:hover{color:var(--brand-ink);background:var(--brand-soft)}
nav.menu a.nav-cta{display:inline-flex;align-items:center;gap:6px;background:var(--brand);color:var(--on-brand);margin-left:6px;padding:8px 14px}
nav.menu a.nav-cta:hover{background:var(--brand-2);color:var(--on-brand)}
.corto{display:none}
@media (max-width:640px){.lungo{display:none}.corto{display:inline}nav.menu a{padding:8px 7px;font-size:.95rem}
nav.menu a.nav-cta{padding:0;width:40px;height:40px;justify-content:center;margin-left:4px}.logo{font-size:1.1rem;gap:7px}.marchio{width:30px;height:30px}}
@media (max-width:350px){.logo-testo{display:none}}
/* titoli */
h1{font-size:clamp(1.55rem,4.2vw,2.4rem);line-height:1.15;letter-spacing:-.025em;margin:0 0 10px;font-weight:800;text-wrap:balance}
h2{font-size:clamp(1.25rem,2.6vw,1.5rem);line-height:1.25;margin:44px 0 14px;letter-spacing:-.015em;font-weight:750;display:flex;align-items:flex-start;gap:10px}
h2 .i{color:var(--brand);width:1em;height:1em;margin-top:.13em}
h3{font-size:1.08rem;margin:22px 0 10px;font-weight:700}
.lead{font-size:1.1rem;color:var(--ink-2);max-width:62ch;margin:0 0 6px}
.small{font-size:.9rem;color:var(--ink-3)}
.briciole{font-size:.88rem;color:var(--ink-3);margin:0 0 10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.briciole a{color:var(--ink-3)}
.hero{padding:30px 0 6px}
.occhiello{display:inline-flex;align-items:center;gap:8px;font-size:.85rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--brand-ink);
background:var(--brand-soft);padding:5px 12px;border-radius:999px;margin-bottom:14px}
/* scheda risposta (prossimo esame / iscrizioni aperte) */
.risposta{margin:22px 0 8px;border-radius:var(--r-l);background:linear-gradient(135deg,var(--hero-a),var(--hero-b));color:var(--hero-ink);
padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:8px;box-shadow:var(--ombra)}
.risposta .slot{padding:18px 20px;border-radius:14px;min-width:0}
.risposta .slot+.slot{background:var(--surface);color:var(--ink)}
.r-et{display:flex;align-items:center;gap:8px;font-size:.82rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;opacity:.92}
.r-data{font-size:clamp(1.9rem,5.4vw,2.7rem);font-weight:800;letter-spacing:-.03em;line-height:1.05;margin:8px 0 6px;font-variant-numeric:tabular-nums}
.r-data small{font-size:.5em;font-weight:700;letter-spacing:-.01em;opacity:.85}
.r-cosa{font-size:1rem;display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}
.risposta .slot:first-child .r-cosa{color:var(--hero-ink-2)}
.risposta .slot:first-child .eb{background:rgba(255,255,255,.16);color:var(--hero-ink)}
.r-nota{font-size:.86rem;color:var(--ink-3);margin:10px 0 0}
.r-piede{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between;padding:6px 12px 6px}
.r-piede a{color:var(--hero-ink);font-weight:700;display:inline-flex;align-items:center;gap:6px}
.r-piede span{font-size:.88rem;color:var(--hero-ink-2);display:inline-flex;align-items:center;gap:6px}
.azioni{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px;align-items:center}
.cifre{display:flex;flex-wrap:wrap;gap:8px 20px;margin:14px 0 0;padding:0;list-style:none;color:var(--ink-2);font-size:.95rem}
.cifre li{display:flex;align-items:center;gap:7px}
.cifre .i{color:var(--brand)}
.cifre strong{color:var(--ink)}
/* conteggi */
.conta{display:inline-flex;align-items:center;gap:5px;font-size:.8rem;font-weight:800;letter-spacing:.01em;padding:3px 10px;border-radius:999px;
background:var(--surface-2);color:var(--ink-2);white-space:nowrap;font-variant-numeric:tabular-nums}
.conta:empty{display:none}
.conta.urg{background:var(--rosso-soft);color:var(--rosso)}
.conta.vicino{background:var(--brand-soft);color:var(--brand-ink)}
.risposta .slot:first-child .conta{background:rgba(255,255,255,.18);color:var(--hero-ink)}
/* avvisi */
.avviso{display:flex;gap:12px;align-items:flex-start;background:var(--warn-soft);color:var(--ink);border:1px solid color-mix(in srgb,var(--warn) 25%,transparent);
padding:12px 16px;border-radius:12px;font-size:.95rem;margin:18px 0}
.avviso .i{color:var(--warn);margin-top:3px}
/* bottoni */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font:inherit;font-weight:750;background:var(--brand);color:var(--on-brand);border:0;
border-radius:12px;padding:12px 20px;min-height:48px;cursor:pointer;text-decoration:none;transition:background .15s,transform .15s}
.btn:hover{background:var(--brand-2)}
.btn:active{transform:scale(.98)}
.btn:disabled{opacity:.6;cursor:wait}
.btn-2{background:transparent;color:var(--brand-ink);box-shadow:inset 0 0 0 1.5px var(--line-2)}
.btn-2:hover{background:var(--brand-soft)}
/* schede */
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-l);padding:22px;box-shadow:var(--ombra)}
.eb{display:inline-flex;align-items:center;font-size:.76rem;font-weight:800;letter-spacing:.04em;padding:3px 9px;border-radius:6px;white-space:nowrap}
.eb-CILS{background:var(--cils-bg);color:var(--cils)}.eb-CELI{background:var(--celi-bg);color:var(--celi)}
.eb-PLIDA{background:var(--plida-bg);color:var(--plida)}.eb-CERTIT{background:var(--certit-bg);color:var(--certit)}
.tag{display:inline-flex;align-items:center;gap:5px;font-size:.8rem;font-weight:700;padding:3px 9px;border-radius:999px;background:var(--surface-2);color:var(--ink-2)}
.tag.citt{background:var(--brand-soft);color:var(--brand-ink)}
/* filtri a chip */
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:4px 0 16px}
.chips button{font:inherit;font-size:.9rem;font-weight:650;display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line-2);background:var(--surface);
color:var(--ink-2);padding:7px 13px;min-height:40px;border-radius:999px;cursor:pointer;white-space:nowrap;transition:background .15s,border-color .15s}
.chips button:hover{border-color:var(--brand)}
.chips button[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--bg)}
.chips .pt{width:9px;height:9px;border-radius:50%;flex:none}
@media (max-width:640px){.chips{flex-wrap:nowrap;overflow-x:auto;margin-right:-16px;padding-right:16px;padding-bottom:6px;scrollbar-width:none;
-webkit-mask-image:linear-gradient(90deg,#000 85%,transparent);mask-image:linear-gradient(90deg,#000 85%,transparent)}
.chips::-webkit-scrollbar{display:none}.chips button:last-child{margin-right:24px}}
.esito{font-size:.9rem;color:var(--ink-3);margin:-6px 0 12px;font-weight:600}
.esito:empty{display:none}
.mostra{width:100%;margin-top:12px}
/* sessioni */
.sessioni{display:grid;gap:12px}
.sess{display:grid;grid-template-columns:64px minmax(0,1fr);gap:16px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;
min-width:0;overflow-wrap:anywhere;box-shadow:var(--ombra)}
.sess[hidden],.sess.oltre{display:none}
.tile{display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:10px;background:var(--surface-2);padding:9px 4px 7px;align-self:start;
line-height:1;text-align:center;box-shadow:inset 0 4px 0 var(--brand)}
.sess[data-tipo="generale"] .tile{box-shadow:inset 0 4px 0 var(--line-2)}
.tile .tm{font-size:.76rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--brand-ink)}
.tile .td{font-size:1.7rem;font-weight:800;letter-spacing:-.03em;margin:4px 0 3px;font-variant-numeric:tabular-nums}
.tile .ty{font-size:.75rem;color:var(--ink-3);font-weight:600}
.sess .cosa{min-width:0}
.sess .testa{display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.sess .nome{font-weight:750;font-size:1.06rem;line-height:1.3}
.sess .testa .tag{font-size:.76rem;padding:2px 8px;margin-left:auto}
.sess .quando{display:flex;flex-wrap:wrap;gap:2px 14px;align-items:center;font-size:.94rem;color:var(--ink-2);margin-top:4px}
.sess .quando .sep{color:var(--line-2)}
.sess .quando time{color:var(--ink-3)}
.scad{display:inline-flex;flex-wrap:wrap;gap:2px 6px;align-items:center;min-width:0}
.scad.chiusa .stato{flex-basis:100%}
.scad>.i{color:var(--ink-3)}
.scad strong{color:var(--ink)}
.scad.urgente strong{color:var(--rosso)}
.scad.chiusa{color:var(--ink-3)}
.scad.chiusa strong{color:var(--ink-3);text-decoration:line-through;text-decoration-thickness:1px}
.scad.chiusa .stato{white-space:normal;background:none;padding:0;font-weight:600;font-size:.86rem;color:var(--ink-3)}
.sess .nota{font-size:.86rem;color:var(--ink-3);margin-top:4px}
.sess .fonte{margin-top:4px}
.note-scad{list-style:none;margin:0 0 14px;padding:12px 14px;background:var(--surface-2);border-radius:12px;display:grid;gap:6px;font-size:.9rem;color:var(--ink-2)}
.note-scad li{display:flex;gap:8px;align-items:baseline}
.note-scad .eb{flex:none}
.fonte{font-size:.8rem;color:var(--ink-3);margin-top:8px;display:flex;gap:6px;align-items:flex-start}
.fonte .i{margin-top:2px}
.fonte a{color:var(--ink-3)}
/* griglia città */
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.griglia a{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 12px;min-height:52px;
text-decoration:none;color:var(--ink);font-weight:700;line-height:1.25;transition:border-color .15s,background .15s}
.griglia a .i{color:var(--brand)}
.griglia a small{display:block;font-weight:500;color:var(--ink-3);font-size:.82rem}
.griglia a:hover{border-color:var(--brand);background:var(--brand-soft)}
/* sedi */
.sedi{list-style:none;padding:0;margin:0;display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.sedi li{position:relative;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px 14px 18px;min-width:0;overflow-wrap:anywhere}
.sedi li::before{content:"";position:absolute;left:-1px;top:14px;bottom:14px;width:4px;border-radius:0 4px 4px 0;background:var(--brand)}
.sedi li.s-CILS::before{background:var(--cils)}.sedi li.s-CELI::before{background:var(--celi)}
.sedi li.s-PLIDA::before{background:var(--plida)}.sedi li.s-CERTIT::before{background:var(--certit)}
details .sedi li{background:var(--bg)}
.sedi .nome{font-weight:700;display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;margin-bottom:6px}
.sedi .det{font-size:.92rem;color:var(--ink-2);display:flex;gap:8px;align-items:flex-start;margin-top:3px}
.sedi .det .i{color:var(--ink-3);margin-top:3px}
.sedi .contatti{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.92rem;margin-top:6px}
.sedi .contatti span,.sedi .contatti a{display:inline-flex;gap:6px;align-items:center}
.sedi .contatti .i{color:var(--ink-3)}
/* domande, tabelle */
details{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:0;margin:8px 0}
details summary{cursor:pointer;font-weight:700;padding:14px 16px;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px}
details summary::-webkit-details-marker{display:none}
details summary .i{transition:transform .2s;color:var(--ink-3)}
details[open] summary .i{transform:rotate(180deg)}
details>:not(summary){margin:0 16px 14px}
details>p{color:var(--ink-2)}
table.conf{width:100%;border-collapse:collapse;font-size:.95rem;background:var(--surface);border-radius:12px;overflow:hidden}
table.conf th{font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-3);background:var(--surface-2)}
table.conf th,table.conf td{border-bottom:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
.tab-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
ol.passi{counter-reset:p;list-style:none;padding:0;display:grid;gap:10px}
ol.passi li{counter-increment:p;display:grid;grid-template-columns:36px 1fr;gap:12px;align-items:start;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
ol.passi li::before{content:counter(p);display:grid;place-items:center;width:32px;height:32px;border-radius:50%;background:var(--brand);color:var(--on-brand);font-weight:800}
/* modulo */
.modulo-testa{display:flex;gap:12px;align-items:flex-start;margin-bottom:6px}
.modulo-testa .bolla{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;background:var(--brand-soft);color:var(--brand);flex:none}
.modulo-testa .bolla .i{width:22px;height:22px}
.modulo-testa h2{margin:0;font-size:1.25rem}
.form{display:grid;gap:14px;margin-top:14px}
.form label{display:grid;gap:6px;font-weight:650;font-size:.95rem}
.form input,.form select{font:inherit;font-size:1rem;padding:11px 12px;min-height:48px;border:1.5px solid var(--line-2);border-radius:10px;background:var(--bg);color:var(--ink);width:100%;min-width:0}
.form input:focus,.form select:focus{border-color:var(--brand)}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:20px;height:20px;min-height:0;padding:0;margin-top:2px;flex:none;accent-color:var(--brand)}
.form .btn{width:100%}
.hp{position:absolute;left:-9999px}
.ok{display:flex;gap:10px;background:var(--brand-soft);border:1px solid var(--brand);padding:14px;border-radius:12px;margin-top:12px}
.ok .i{color:var(--brand);margin-top:3px}
.errore{color:var(--rosso);font-weight:650}
/* impaginazione */
.due{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:32px;align-items:start}
.due>*{min-width:0}
.due>aside>section+section{margin-top:8px}
.due>section>h2:first-child,.due>aside>.card:first-child{margin-top:28px}
@media (min-width:861px){.due>aside{position:sticky;top:16px;align-self:start}}
@media (max-width:860px){.due{grid-template-columns:1fr;gap:8px}.risposta{grid-template-columns:1fr}}
@media (max-width:640px){body{font-size:16.5px}.lead{font-size:1.02rem}.r-piede span{display:none}.sess{grid-template-columns:1fr;gap:8px;padding:14px}.tile{flex-direction:row;align-items:baseline;justify-self:start;gap:7px;padding:6px 12px;border-radius:8px;box-shadow:none;background:var(--brand-soft)}.sess[data-tipo="generale"] .tile{box-shadow:none;background:var(--surface-2)}.tile .td{font-size:1.3rem;margin:0}
.sess .testa .tag{margin-left:0}.azioni .btn{flex:1 1 100%;justify-content:center}.sedi{grid-template-columns:minmax(0,1fr)}
.card{padding:18px}.risposta .slot{padding:16px}.hero{padding-top:22px}}
.altre{display:flex;flex-wrap:wrap;gap:6px}
.altre a{font-size:.9rem;padding:5px 11px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink-2);background:var(--surface)}
.altre a:hover{border-color:var(--brand);color:var(--brand-ink)}
.regioni{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:16px 28px;margin:6px 0 14px}
.regioni>div{min-width:0}
.regioni h4{margin:0 0 6px;font-size:.92rem;font-weight:750;color:var(--ink-2)}
/* piede */
footer.piede{margin-top:64px;background:#13201E;color:#C4D2CD;padding:36px 0 44px;font-size:.9rem}
footer.piede::before{content:"";display:block;height:4px;margin-top:-36px;margin-bottom:32px;background:linear-gradient(90deg,#0B6B4F 0 33.3%,#F4F1EA 33.3% 66.6%,#C8402A 66.6%)}
footer.piede a{color:#E8F0ED}
footer.piede .logo{color:#FFFFFF}
footer.piede .piede-altri{margin-top:26px;padding-top:18px;border-top:1px solid rgba(255,255,255,.16)}
footer.piede .piede-altri h2{font-size:1rem;line-height:1.3;color:#FFFFFF;margin:0 0 8px;font-family:inherit}
footer.piede .piede-altri ul{list-style:none;padding:0;margin:0}
footer.piede .piede-altri li{margin:0 0 6px;max-width:70ch}
footer.piede .piede-altri a{font-weight:700}
footer.piede .logo b{color:#6AD6AB}
footer.piede .marchio{--brand:#4CC596;--on-brand:#052118}
.piede-griglia{display:grid;grid-template-columns:1.2fr 1fr;gap:28px;align-items:start}
.piede-link{display:flex;flex-wrap:wrap;gap:8px 18px;list-style:none;padding:0;margin:14px 0 0}
.piede-link a{text-decoration:none;font-weight:600}
.piede-link a:hover{text-decoration:underline}
.piede p{margin:0 0 12px;max-width:70ch}
/* scheda per ente nella pagina città */
.perente{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.pe{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--brand);border-radius:var(--r);padding:14px 16px;box-shadow:var(--ombra);
min-width:0;overflow-wrap:anywhere;display:grid;gap:12px;align-content:start}
.pe-CILS{border-top-color:var(--cils)}.pe-CELI{border-top-color:var(--celi)}.pe-PLIDA{border-top-color:var(--plida)}.pe-CERTIT{border-top-color:var(--certit)}
.pe-testa{display:flex;justify-content:space-between;align-items:center;gap:6px 10px;flex-wrap:wrap;font-size:.9rem}
.pe-testa a{font-weight:700;display:inline-flex;align-items:center;gap:5px}
.pe-et{font-size:.74rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);display:flex;gap:6px;align-items:center;margin-bottom:2px}
.pe-data{font-size:1.12rem;font-weight:800;letter-spacing:-.01em;font-variant-numeric:tabular-nums;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.pe-cosa{font-size:.88rem;color:var(--ink-3);margin:2px 0 0}
/* fatti per ente (costo, durata, risultati...) */
.fatti{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.fatto{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;min-width:0;overflow-wrap:anywhere;box-shadow:var(--ombra);display:flex;flex-direction:column}
.f-et{display:flex;gap:8px;align-items:center;font-weight:750;flex-wrap:wrap}
.f-et .i{color:var(--brand)}
.f-breve{font-size:1.45rem;font-weight:800;letter-spacing:-.02em;line-height:1.2;margin:8px 0 0}
.fatto p{margin:8px 0 0;color:var(--ink-2);font-size:.95rem}
.fatto .fonte{margin-top:auto;padding-top:10px}
.fatto .btn{margin-top:12px;min-height:44px;padding:9px 14px;font-size:.95rem;align-self:flex-start}
.griglia.link3{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
.piede .dati{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.07);padding:6px 12px;border-radius:999px;font-weight:600;color:#E8F0ED}
@media (max-width:760px){.piede-griglia{grid-template-columns:1fr}}
"""

JS = """
(function(){
  var oggi=new Date();oggi.setHours(0,0,0,0);
  function giorni(iso){var p=iso.split('-');var x=new Date(+p[0],+p[1]-1,+p[2]);return Math.round((x-oggi)/86400000);}
  function conta(el,g,modo){
    el.classList.remove('urg','vicino');
    if(modo==='esame'){el.textContent=g===0?'oggi':g===1?'domani':'tra '+g+' giorni';if(g<=15)el.classList.add('vicino');return;}
    el.textContent=g===0?'scade oggi':'mancano '+g+(g===1?' giorno':' giorni');if(g<=15)el.classList.add('urg');
  }
  document.querySelectorAll('.sess').forEach(function(el){
    if(giorni(el.dataset.data)<0){el.remove();return;}
    var sc=el.querySelector('.scad[data-scadenza]');
    if(!sc)return;
    var g=giorni(sc.dataset.scadenza);var t=sc.querySelector('.stato');
    sc.classList.remove('urgente','chiusa');t.classList.remove('urg','vicino');
    if(g<0){sc.classList.add('chiusa');t.textContent='termine nazionale passato: chiedi alla sede se accetta ancora iscrizioni';}
    else if(g===0){sc.classList.add('urgente');conta(t,g,'scad');}
    else if(g<=15){sc.classList.add('urgente');conta(t,g,'scad');}
    else{t.textContent='';}
  });
  document.querySelectorAll('[data-slot]').forEach(function(slot){
    var vista=false;
    slot.querySelectorAll('[data-fino]').forEach(function(o){var ok=!vista&&giorni(o.dataset.fino)>=0;o.hidden=!ok;if(ok)vista=true;});
    var r=slot.querySelector('[data-riserva]');if(r)r.hidden=vista;
  });
  document.querySelectorAll('[data-conta]').forEach(function(el){var g=giorni(el.dataset.conta);if(g>=0)conta(el,g,el.dataset.modo);});
  /* elenco corto: le prossime 6 date, poi "Mostra tutte" */
  var LIMITE=6;
  document.querySelectorAll('[data-elenco]').forEach(function(box){
    var lista=box.querySelector('.sessioni'),piu=box.querySelector('.mostra'),esito=box.querySelector('.esito');
    var bott=box.querySelectorAll('.chips button'),aperto=false;
    function aggiorna(etichetta){
      var vis=[].filter.call(lista.querySelectorAll('.sess'),function(el){return !el.hidden;});
      vis.forEach(function(el,i){el.classList.toggle('oltre',!aperto&&i>=LIMITE);});
      if(piu){piu.hidden=aperto||vis.length<=LIMITE;piu.textContent='Mostra tutte le '+vis.length+' date';}
      if(esito&&etichetta!==undefined)esito.textContent=vis.length+(vis.length===1?' sessione':' sessioni')+etichetta;
    }
    if(piu)piu.addEventListener('click',function(){aperto=true;aggiorna();});
    bott.forEach(function(b){b.addEventListener('click',function(){
      bott.forEach(function(x){x.setAttribute('aria-pressed','false');});b.setAttribute('aria-pressed','true');
      var f=b.dataset.filtro;
      lista.querySelectorAll('.sess').forEach(function(el){
        el.hidden=!(f==='tutti'||(f==='citt'&&el.dataset.tipo==='cittadinanza')||el.dataset.ente===f);
      });
      aggiorna(f==='tutti'?'':f==='citt'?' per la cittadinanza':' '+f);
    });});
    aggiorna();
  });
  /* link a una regione (#lombardia): apre il riquadro */
  try{var h=location.hash&&document.getElementById(decodeURIComponent(location.hash.slice(1)));if(h&&h.tagName==='DETAILS')h.open=true;}catch(e){}
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


def il(iso):
    """Articolo davanti alla data: "il 24 ottobre", "l'8 maggio", "l'11 novembre"."""
    return "l'" if d(iso).day in (8, 11) else "il "


def del_(iso):
    """Preposizione articolata davanti alla data: "del 3 dicembre", "dell'8 aprile", "dell'11 novembre"."""
    return "dell'" if d(iso).day in (8, 11) else "del "


def testo_conta(iso, modo):
    g = (d(iso) - OGGI).days
    if modo == "esame":
        return "oggi" if g == 0 else "domani" if g == 1 else f"tra {g} giorni"
    return "scade oggi" if g == 0 else f"mancano {g} {'giorno' if g == 1 else 'giorni'}"


def classe_conta(iso, modo):
    g = (d(iso) - OGGI).days
    return "" if g > 15 else ("vicino" if modo == "esame" else "urg")


def eb(sigla):
    return f'<span class="eb eb-{sigla.replace(".", "")}">{escape(sigla)}</span>'


def pagina(percorso, titolo, descrizione, corpo, jsonld=None, base=None):
    """Scrive sito/<percorso> con la struttura comune. base: prefisso dei link ("/" per la 404)."""
    profondita = percorso.count("/")
    rel = base if base is not None else ("../" * profondita or "./")
    avvisami = "#avvisami" if 'id="avvisami"' in corpo else f"{rel or '/'}#avvisami"
    canonico = URL_SITO + "/" + (percorso[:-10] if percorso.endswith("index.html") else percorso)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    home_href = rel or "./"
    enti_link = "".join(f'<li><a href="{rel}ente/{SLUG_ENTE[e]}/">{e}</a></li>' for e in ENTE)
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
<meta name="theme-color" content="#0B6B4F">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
{ld}
</head>
<body>
{SPRITE}
<a class="salta" href="#contenuto">Vai al contenuto</a>
<header class="top"><div class="wrap">
<a class="logo" href="{home_href}" aria-label="{NOME}, pagina iniziale">{MARCHIO}<span class="logo-testo">Esame<b>B1</b></span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}#date">Date</a><a href="{rel}#citta">Città</a><a href="{rel}come-funziona/"><span class="lungo">Come funziona</span><span class="corto">Guida</span></a><a class="nav-cta" href="{avvisami}" aria-label="Avvisami">{ic("campana")}<span class="lungo">Avvisami</span></a>
</nav>
</div></header>
<main class="wrap" id="contenuto">
{corpo}
</main>
<footer class="piede"><div class="wrap">
<div class="piede-griglia">
<div>
<a class="logo" href="{home_href}">{MARCHIO}<span class="logo-testo">Esame<b>B1</b></span></a>
<ul class="piede-link">
<li><a href="{rel}#date">Date d'esame</a></li><li><a href="{rel}#citta">Sedi per città</a></li><li><a href="{rel}come-funziona/">Come funziona</a></li><li><a href="{rel}costo/">Costo</a></li><li><a href="{rel}risultati/">Risultati</a></li>{enti_link}<li><a href="{rel}privacy.html">Privacy</a></li>
</ul>
</div>
<div>
<p><strong>{NOME}</strong> è un sito indipendente, non affiliato agli enti certificatori. CILS, CELI, PLIDA e CERT.IT sono marchi dei rispettivi enti.
Le informazioni vengono dalle fonti ufficiali indicate accanto a ogni dato. <strong>Prima di iscriverti verifica sempre sul sito della sede.</strong>
Questo sito non dà consulenza sulla pratica di cittadinanza: per quella vedi la <a href="https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza" rel="noopener">pagina del Ministero dell'Interno</a>.</p>
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


def tile(iso):
    x = d(iso)
    return (f'<div class="tile" aria-hidden="true"><span class="tm">{MESI_BREVI[x.month - 1]}</span>'
            f'<span class="td">{x.day}</span><span class="ty">{x.year}</span></div>')


def nota_comune(s):
    """Le note sulla scadenza ripetute in più sessioni (es. "le sedi possono chiudere prima") si dicono una volta sola, in testa all'elenco."""
    return sum(1 for x in sessioni if x["nota_scadenza"] == s["nota_scadenza"]) > 1


def scheda_sessione(s):
    citt = s["tipo"] == "cittadinanza"
    esami = ", ".join(s["esami"])
    badge = (f'<span class="tag citt">{ic("ok")}Esame per la cittadinanza</span>' if citt
             else f'<span class="tag">{ic("ok")}B1 valido per la cittadinanza</span>')
    nota = "" if nota_comune(s) else f'<div class="nota">{escape(s["nota_scadenza"])}</div>'
    if s.get("scadenza"):
        scad = (f'<span class="scad" data-scadenza="{s["scadenza"]}">{ic("orologio")}Iscrizioni entro <strong>{data_breve(s["scadenza"])}</strong>'
                f'<span class="stato conta"></span></span>')
    else:
        scad = ""
    return f"""<article class="sess" data-data="{s['data']}" data-ente="{escape(s['ente'])}" data-tipo="{s['tipo']}">
{tile(s['data'])}
<div class="cosa"><div class="testa">{eb(s['ente'])}<span class="nome">{escape(esami)}</span>{badge}</div>
<div class="quando"><time datetime="{s['data']}">{data_lunga(s['data'])}</time>{scad}</div>
{nota}
<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(s['fonte'])}" rel="noopener">calendario ufficiale {escape(s['ente'])}</a> · controllato il {data_breve(s['verificato_il'])}</span></div>
</div>
</article>"""


def note_scadenze(lista):
    """Una riga per ente con la nota sulla scadenza, detta una volta per tutto l'elenco."""
    righe, viste = [], set()
    for e in ENTE:
        for s in lista:
            if s["ente"] == e and nota_comune(s) and s["nota_scadenza"] not in viste:
                viste.add(s["nota_scadenza"])
                righe.append(f'<li>{eb(e)}<span>{escape(s["nota_scadenza"])}</span></li>')
    return f'<ul class="note-scad" aria-label="Come leggere le scadenze">{"".join(righe)}</ul>' if righe else ""


def lista_sessioni(lista, con_filtri=True):
    filtri = ""
    if con_filtri:
        bottoni = ['<button type="button" data-filtro="tutti" aria-pressed="true">Tutte</button>',
                   f'<button type="button" data-filtro="citt" aria-pressed="false">{ic("ok")}Solo cittadinanza</button>']
        bottoni += [f'<button type="button" data-filtro="{e}" aria-pressed="false"><span class="pt" style="background:var(--{e.replace(".", "").lower()})"></span>{e}</button>'
                    for e in ENTE]
        filtri = (f'<div class="filtri chips" role="group" aria-label="Filtra per ente">{"".join(bottoni)}</div>'
                  '<p class="esito" aria-live="polite"></p>')
    return (f'<div data-elenco>{note_scadenze(lista)}{filtri}<div class="sessioni">' + "\n".join(scheda_sessione(s) for s in lista)
            + '</div><button class="btn btn-2 mostra" type="button" hidden>Mostra tutte le date</button></div>')


def risposta(prossime, rel=""):
    """Scheda in cima: prossimo esame e prossima scadenza nazionale ancora aperta. Il JS la tiene aggiornata tra un rilascio e l'altro."""
    esami = prossime[:12]
    opz_e = []
    for i, s in enumerate(esami):
        x = d(s["data"])
        opz_e.append(f"""<div data-fino="{s['data']}"{"" if i == 0 else " hidden"}>
<div class="r-data">{x.day} {MESI[x.month - 1]} <small>{x.year}</small></div>
<div class="r-cosa">{eb(s['ente'])}<span>{escape(", ".join(s['esami']))}</span></div>
<p style="margin:12px 0 0"><span class="conta {classe_conta(s['data'], 'esame')}" data-conta="{s['data']}" data-modo="esame">{testo_conta(s['data'], 'esame')}</span></p>
</div>""")
    con_scad = sorted((s for s in prossime if s.get("scadenza")), key=lambda s: (s["scadenza"], s["data"]))
    opz_s, primo = [], True
    for s in con_scad:
        visibile = primo and d(s["scadenza"]) >= OGGI
        if visibile:
            primo = False
        x = d(s["data"])
        opz_s.append(f"""<div data-fino="{s['scadenza']}"{"" if visibile else " hidden"}>
<div class="r-data"><small>entro {il(s['scadenza']).strip()}</small>{" " if il(s['scadenza']).endswith(" ") else ""}{data_breve(s['scadenza'])}</div>
<div class="r-cosa">per l'esame {eb(s['ente'])} del <strong>{x.day} {MESI[x.month - 1]}</strong></div>
<p style="margin:12px 0 0"><span class="conta {classe_conta(s['scadenza'], 'scad')}" data-conta="{s['scadenza']}" data-modo="scad">{testo_conta(s['scadenza'], 'scad')}</span></p>
<p class="r-nota">È il termine nazionale: la sede può chiudere prima. Chiedi sempre conferma.</p>
</div>""")
    riserva = ('<p data-riserva class="r-nota"{}>In questo momento non ci sono termini nazionali aperti: per PLIDA e CERT.IT la scadenza '
               'la decide ogni centro. Chiedi alla sede.</p>').format("" if primo else " hidden")
    return f"""<div class="risposta">
<div class="slot" data-slot><div class="r-et">{ic("cal")}Prossimo esame</div>{"".join(opz_e)}</div>
<div class="slot" data-slot><div class="r-et">{ic("orologio")}Iscrizioni ancora aperte</div>{"".join(opz_s)}{riserva}</div>
<div class="r-piede"><a href="{rel}#date">Tutte le date {ic("freccia")}</a><span>{ic("info")}Le date d'esame sono le stesse in tutta Italia.</span></div>
</div>"""


def modulo(citta_scelta=""):
    opzioni = "".join(
        f'<option value="{escape(c["nome"])}"{" selected" if c["nome"] == citta_scelta else ""}>{escape(c["nome"])}</option>'
        for c in sorted(citta, key=lambda c: c["nome"]))
    enti_opt = "".join(f'<option value="{e}">{e}</option>' for e in ENTE)
    return f"""<section class="card" id="avvisami">
<div class="modulo-testa"><span class="bolla">{ic("campana")}</span><div>
<h2>Avvisami quando ci sono nuove date</h2>
<p class="small" style="margin:4px 0 0">Gratis. Ti scriviamo quando esce una nuova sessione o quando una scadenza sta per chiudere nella tua città.</p></div></div>
<form class="form avvisami" name="avvisami" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="avvisami">
<input type="hidden" name="source" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>La tua email<input type="email" name="email" required autocomplete="email" placeholder="nome@esempio.it"></label>
<label>Città dove vuoi fare l'esame
<select name="citta" required><option value="">Scegli la città</option>{opzioni}<option value="Altra città">Altra città</option></select></label>
<label>Ente preferito (facoltativo)
<select name="ente"><option value="">Nessuna preferenza</option>{enti_opt}</select></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required>
<span>Accetto di ricevere email da {NOME} sulle date dell'esame B1. Posso cancellarmi quando voglio. Ho letto la <a href="/privacy.html">privacy</a>.</span></label>
<button class="btn" type="submit">{ic("campana")}Avvisami</button>
<p class="errore" data-errore hidden>Non è stato possibile inviare. Riprova tra poco.</p>
</form>
<div class="ok" data-ok hidden>{ic("ok")}<span><strong>Fatto!</strong> Ti scriveremo quando ci sono novità per la tua città.</span></div>
</section>"""


def scheda_sede(s, con_citta=False):
    righe = [escape(s["indirizzo"])] if s["indirizzo"] else []
    luogo = " ".join(x for x in [s.get("cap", ""), s["citta"], f'({s["sigla"]})' if s.get("sigla") else ""] if x)
    if luogo:
        righe.append(escape(luogo))
    contatti = []
    if s.get("telefono"):
        contatti.append(f'<span>{ic("tel")}Tel. {escape(s["telefono"])}</span>')
    for mail in [x for x in re.split(r"[;,:\s]+", s.get("email") or "") if "@" in x]:
        contatti.append(f'<a href="mailto:{escape(mail)}">{ic("mail")}{escape(mail)}</a>')
    if s.get("sito"):
        url = s["sito"] if s["sito"].startswith("http") else "https://" + s["sito"]
        contatti.append(f'<a href="{escape(url)}" rel="noopener nofollow">{ic("web")}sito</a>')
    return f"""<li class="s-{s['ente'].replace('.', '')}"><div class="nome">{eb(s['ente'])}<span>{escape(s['nome'])}</span></div>
{f'<div class="det">{ic("pin")}<span>{"<br>".join(righe)}</span></div>' if righe else ""}
{f'<div class="contatti">{"".join(contatti)}</div>' if contatti else ""}
<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(s['fonte'])}" rel="noopener">elenco ufficiale {escape(s['ente'])}</a></span></div></li>"""


def jsonld_sessioni(lista):
    eventi = []
    for s in lista[:20]:
        e = ENTE[s["ente"]]
        eventi.append({
            "@type": "EducationEvent", "name": f'Esame {", ".join(s["esami"])}', "startDate": s["data"], "endDate": s["data"], "image": URL_SITO + "/og.png",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "Place", "name": f'Sedi d\'esame {s["ente"]} in Italia',
                         "address": {"@type": "PostalAddress", "addressCountry": "IT"}},
            "organizer": {"@type": "Organization", "name": e["ente"], "url": e["sito"]},
            "performer": {"@type": "Organization", "name": e["ente"], "url": e["sito"]},
            "description": f'Sessione d\'esame {s["ente"]} di livello B1, valida per la domanda di cittadinanza italiana.',
        })
        offerta = offerta_ufficiale(s)
        if offerta:
            eventi[-1]["offers"] = offerta
    return {"@context": "https://schema.org", "@graph": eventi}


def offerta_ufficiale(s):
    """Offer solo se l'ente pubblica una tassa unica per quell'esame (oggi: CILS B1 Cittadinanza, 100 €). Altrimenti niente prezzo inventato."""
    e = ENTE[s["ente"]]
    if not e.get("prezzo_eur") or e.get("prezzo_esame") not in s["esami"]:
        return None
    o = {"@type": "Offer", "name": e["prezzo_esame"], "price": e["prezzo_eur"], "priceCurrency": "EUR", "url": e["prezzo_url"]}
    if s.get("scadenza") and d(s["scadenza"]) >= OGGI:
        o["availability"] = "https://schema.org/InStock"
    return o


def avviso(testo):
    return f'<div class="avviso">{ic("attenzione")}<div>{testo}</div></div>'


def briciole(*voci):
    parti = [f'<a href="{h}">{escape(t)}</a>' if h else f'<span aria-current="page">{escape(t)}</span>' for t, h in voci]
    return f'<nav class="briciole" aria-label="Sei qui">{" <span aria-hidden=\"true\">›</span> ".join(parti)}</nav>'


def domanda(titolo, testo):
    return f'<details><summary>{titolo}{ic("giu")}</summary>\n<p>{testo}</p></details>'


def slug(testo):
    t = testo.lower().split("/")[0]
    for a, b in (("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u"), ("'", "-")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def anni(lista):
    a = sorted({d(s["data"]).year for s in lista})
    return f"{a[0]}-{a[-1]}" if len(a) > 1 else (str(a[0]) if a else str(OGGI.year))


def ancora_regione(ente, regione):
    """Ancora nella pagina ente: la regione se l'ente ha sedi lì, altrimenti l'elenco completo."""
    return slug(regione) if any(s["ente"] == ente and s["regione"] == regione for s in sedi) else "sedi"


def regione_di(c):
    regs = [s["regione"] for s in sedi if s["provincia"] == c["provincia"]]
    return max(set(regs), key=regs.count) if regs else ""


PAROLE_VUOTE = {"di", "e", "della", "del", "nell", "nella"}


def norma_luogo(testo):
    """"Reggio di Calabria", "Reggio Calabria" → "reggio calabria"; "Reggio nell'Emilia" → "reggio emilia"."""
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode().lower()
    return " ".join(w for w in re.split(r"[^a-z0-9]+", t) if w and w not in PAROLE_VUOTE)


def nomi_capoluogo(c):
    """Nomi con cui le fonti scrivono il capoluogo: nome della pagina e nome della provincia (anche bilingue, es. Bolzano/Bozen)."""
    return {norma_luogo(c["nome"])} | {norma_luogo(x) for x in c["provincia"].split("/")}


def nel_capoluogo(s, c):
    return norma_luogo(s["citta"]) in nomi_capoluogo(c)


def nome_provincia(c):
    """Per "in provincia di …": il nome della pagina se coincide con la provincia, altrimenti il nome ufficiale (es. Monza e della Brianza)."""
    return c["nome"] if norma_luogo(c["nome"]) in {norma_luogo(x) for x in c["provincia"].split("/")} else c["provincia"].split("/")[0]


def sedi_di(c):
    return sum(1 for s in sedi if s["provincia"] == c["provincia"])


def principali(n=12):
    """Le città con più sedi, per la griglia in evidenza e i link "altre città"."""
    return sorted(citta, key=lambda c: (-sedi_di(c), c["nome"]))[:n]


def citta_per_regione(rel):
    """Tutte le città con pagina, raggruppate per regione (link relativi a rel)."""
    gruppi = {}
    for c in sorted(citta, key=lambda c: c["nome"]):
        gruppi.setdefault(regione_di(c), []).append(c)
    return '<div class="regioni">' + "".join(
        f'<div><h4>{escape(r)}</h4><div class="altre">'
        + "".join(f'<a href="{rel}citta/{c["slug"]}/">{escape(c["nome"])}</a>' for c in cs) + "</div></div>"
        for r, cs in sorted(gruppi.items())) + "</div>"


# Fatti per ente (dati/enti.json → "fatti"): ogni voce ha testo, fonti e data di verifica.
VOCI_FATTI = {"costo": ("euro", "Quanto costa"), "durata": ("orologio", "Quanto dura"), "risultati": ("ok", "Risultati"),
              "documenti": ("doc", "Documenti e cosa portare"), "esempi": ("libro", "Esempi d'esame gratis"), "nota": ("info", "Da sapere")}


def fonte_fatto(f):
    link = " · ".join(f'<a href="{escape(x["url"])}" rel="noopener">{escape(x["nome"])}</a>' for x in f["fonti"])
    return f'<div class="fonte">{ic("doc")}<span>Fonte: {link} · controllato il {data_breve(f["verificato_il"])}</span></div>'


def scheda_fatto(e, chiave, titolo=None, breve=False, bottone=None):
    """Una scheda: ente (o voce) + testo + fonte. Se l'ente non pubblica il dato, lo dice e rimanda alla sede."""
    f = e.get("fatti", {}).get(chiave)
    icona, etichetta = VOCI_FATTI[chiave]
    testa = titolo if titolo is not None else f'{ic(icona)}<span>{etichetta}</span>'
    if not f:
        v = max(x["verificato_il"] for x in e["fatti"].values())
        return (f'<div class="fatto"><div class="f-et">{testa}</div><p>Il sito ufficiale {escape(e["sigla"])} non lo indica: chiedilo alla sede d\'esame.</p>'
                f'<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(e["sito"])}" rel="noopener">sito ufficiale {escape(e["sigla"])}</a> · controllato il {data_breve(v)}</span></div></div>')
    grande = f'<div class="f-breve">{escape(f["breve"])}</div>' if breve and f.get("breve") else ""
    btn = f'<a class="btn btn-2" href="{escape(f["url"])}" rel="noopener">{bottone} {ic("freccia")}</a>' if bottone and f.get("url") else ""
    return f'<div class="fatto"><div class="f-et">{testa}</div>{grande}<p>{escape(f["testo"])}</p>{btn}{fonte_fatto(f)}</div>'


def schede_per_ente(chiave, breve=False, bottone=None):
    return '<div class="fatti">' + "".join(
        scheda_fatto(e, chiave, titolo=f'{eb(e["sigla"])}<span>{escape(e["ente"])}</span>', breve=breve, bottone=bottone) for e in enti) + "</div>"


def link_guide(rel, salta=None):
    voci = [("costo/", "euro", "Quanto costa", "i prezzi di ogni ente"),
            ("come-funziona/", "lista", "Come si svolge", "durata, cosa portare, esempi"),
            ("risultati/", "ok", "Risultati", "quando arrivano e dove vederli")]
    return '<div class="griglia link3">' + "".join(
        f'<a href="{rel}{h}">{ic(i)}<span>{t}<small>{sm}</small></span></a>' for h, i, t, sm in voci if h != salta) + "</div>"


# ---------------------------------------------------------------- pagine
def home(prossime):
    griglia = "".join(
        f'<a href="citta/{c["slug"]}/">{ic("pin")}<span>{escape(c["nome"])}<small>{sedi_di(c)} {"sede" if sedi_di(c) == 1 else "sedi"}</small></span></a>'
        for c in sorted(principali(), key=lambda c: c["nome"]))
    corpo = f"""<section class="hero">
<span class="occhiello">{ic("scudo")}CILS · CELI · PLIDA · CERT.IT</span>
<h1>Esame di italiano B1 per la cittadinanza: tutte le date 2026 e 2027</h1>
<p class="lead">Date, scadenze e sedi dei 4 enti riconosciuti, per chi chiede la cittadinanza italiana per residenza o matrimonio.</p>
{risposta(prossime)}
<div class="azioni"><a class="btn" href="#avvisami">{ic("campana")}Avvisami per la mia città</a><a class="btn btn-2" href="#citta">{ic("pin")}Trova una sede</a></div>
<ul class="cifre"><li>{ic("edificio")}<span><strong>{len(sedi)}</strong> sedi d'esame in Italia</span></li>
<li>{ic("cal")}<span><strong>{len(prossime)}</strong> sessioni in programma</span></li>
<li>{ic("doc")}<span>dati presi dalle fonti ufficiali</span></li></ul>
</section>
{avviso("Ogni sede può avere una scadenza diversa da quella nazionale. <strong>Prima di iscriverti, chiedi sempre conferma alla sede.</strong>")}
<div class="due">
<section id="date">
<h2>{ic("cal")}Prossime date d'esame</h2>
{lista_sessioni(prossime)}
</section>
<aside>
{modulo()}
</aside>
</div>
<section id="citta">
<h2>{ic("pin")}Sedi per città</h2>
<h3>Le città con più sedi</h3>
<div class="griglia">{griglia}</div>
<h3>Tutte le {len(citta)} città, per regione</h3>
{citta_per_regione("")}
<p class="small">La tua città non c'è? Guarda le sedi per regione nelle pagine
{", ".join(f'<a href="ente/{SLUG_ENTE[e]}/">{e}</a>' for e in ENTE)}.</p>
</section>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{domanda("Quale esame devo fare per la cittadinanza?", f'Serve un certificato di italiano almeno di livello B1, rilasciato da uno dei 4 enti riconosciuti: CILS (Università per Stranieri di Siena), CELI (Università per Stranieri di Perugia), PLIDA (Società Dante Alighieri) e CERT.IT (Università Roma Tre). Fonte: <a href="{PREFETTURA}" rel="noopener">Prefettura – Ministero dell\'Interno</a>. Per i casi particolari (titoli di studio italiani, esenzioni) chiedi alla Prefettura.')}
{domanda('Che differenza c\'è tra "B1 cittadinanza" e B1 normale?', 'CILS e CELI hanno un esame B1 pensato per la cittadinanza, con più sessioni durante l\'anno. Il B1 "normale" degli stessi enti, il PLIDA B1 e il CERT.IT B1 sono anch\'essi certificati di livello B1. Leggi la <a href="come-funziona/">pagina Come funziona</a>.')}
{domanda("Come mi iscrivo?", "Ci si iscrive presso la sede d'esame, non su questo sito. Scegli una sede nella tua città, contattala e chiedi costo, documenti e scadenza.")}
{domanda("Quanto costa l'esame B1 per la cittadinanza?", "CILS B1 Cittadinanza: 100 €, la stessa tassa in tutta Italia. CERT.IT B1: 80 € alla sede di Roma Tre. CELI e PLIDA: il prezzo lo decide il centro d'esame (per esempio CELI 2 i cittadinanza 90 € all'Università degli Studi di Milano). <a href=\"costo/\">Tutti i costi, con le fonti</a>.")}
{domanda("Quanto dura l'esame?", "Lo scritto dura da 1 ora e 30 minuti (CERT.IT) a 2 ore e 20 minuti (CELI e PLIDA), secondo l'ente. Poi c'è un orale di 10-15 minuti, di solito lo stesso giorno. <a href=\"come-funziona/#durata\">Durata di ogni esame e cosa portare</a>.")}
{domanda("Quando arrivano i risultati?", "CILS: circa 3 mesi dopo l'esame. CELI: circa 90 giorni lavorativi. PLIDA: li vedi online nel tuo account PLIDA. <a href=\"risultati/\">Dove vedere il risultato e come avere il certificato</a>.")}
{domanda("Si può fare l'esame online?", "No. L'esame B1 per la cittadinanza si fa in presenza, in una sede d'esame, con un documento d'identità. <a href=\"come-funziona/#online\">Fonti ufficiali</a>.")}
<p class="small">Per chiedere la cittadinanza italiana per residenza o matrimonio serve un certificato di italiano di livello B1.
Qui trovi in un solo posto le date, le scadenze e le sedi dei 4 enti riconosciuti: CILS, CELI, PLIDA e CERT.IT.</p>
</section>"""
    pagina("index.html", "Esame B1 cittadinanza: date 2026-2027, scadenze e sedi | EsameB1",
           "Tutte le date dell'esame di italiano B1 per la cittadinanza (CILS, CELI, PLIDA, CERT.IT), scadenze di iscrizione, costi e "
           f"{len(sedi)} sedi in Italia, in un solo posto.", corpo, jsonld_sessioni(prossime))


def per_ente(c, qui, in_citta, prossime):
    """Una scheda per ente con sedi in provincia: prossimo esame e prima scadenza nazionale ancora aperta.
    Il JS (data-slot / data-fino) nasconde le voci passate anche tra un aggiornamento e l'altro."""
    schede = []
    for e in ENTE:
        n_c = sum(1 for s in in_citta if s["ente"] == e)
        n_q = sum(1 for s in qui if s["ente"] == e)
        lista = [s for s in prossime if s["ente"] == e]
        if not n_q:
            continue
        dove = f'{n_c} {"sede" if n_c == 1 else "sedi"} a {escape(c["nome"])}' if n_c else f'{n_q} in provincia'
        if not lista:
            schede.append(f"""<article class="pe pe-{e.replace('.', '')}">
<div class="pe-testa">{eb(e)}<a href="#sedi-{SLUG_ENTE[e]}">{ic("pin")}{dove}</a></div>
<div><div class="pe-et">{ic("cal")}Prossimo esame</div><p class="pe-cosa" style="margin:0">Nessuna nuova data pubblicata dall'ente per ora.
Controlliamo il calendario ogni settimana: <a href="#avvisami">avvisami quando esce</a>.</p></div>
</article>""")
            continue
        esami = "".join(
            f'<div data-fino="{s["data"]}"{"" if i == 0 else " hidden"}><div class="pe-data">{data_breve(s["data"])}'
            f'<span class="conta {classe_conta(s["data"], "esame")}" data-conta="{s["data"]}" data-modo="esame">{testo_conta(s["data"], "esame")}</span></div>'
            f'<p class="pe-cosa">{escape(", ".join(s["esami"]))}</p></div>' for i, s in enumerate(lista[:10]))
        con_scad = [s for s in lista if s.get("scadenza")]
        if con_scad:
            righe, primo = [], True
            for s in con_scad:
                vis = primo and d(s["scadenza"]) >= OGGI
                primo = primo and not vis
                righe.append(f'<div data-fino="{s["scadenza"]}"{"" if vis else " hidden"}><div class="pe-data">entro {il(s["scadenza"])}{data_breve(s["scadenza"])}'
                             f'<span class="conta {classe_conta(s["scadenza"], "scad")}" data-conta="{s["scadenza"]}" data-modo="scad">{testo_conta(s["scadenza"], "scad")}</span></div>'
                             f'<p class="pe-cosa">per l\'esame {del_(s["data"])}{data_breve(s["data"])}</p></div>')
            iscr = "".join(righe) + (f'<p class="pe-cosa" data-riserva{"" if primo else " hidden"}>Nessun termine nazionale aperto: chiedi alla sede.</p>')
        else:
            iscr = f'<p class="pe-cosa" style="margin:0">La scadenza la decide ogni centro {escape(e)}: chiedila alla sede.</p>'
        schede.append(f"""<article class="pe pe-{e.replace('.', '')}">
<div class="pe-testa">{eb(e)}<a href="#sedi-{SLUG_ENTE[e]}">{ic("pin")}{dove}</a></div>
<div data-slot><div class="pe-et">{ic("cal")}Prossimo esame</div>{esami}</div>
<div data-slot><div class="pe-et">{ic("orologio")}Iscrizioni (termine nazionale)</div>{iscr}</div>
</article>""")
    return f'<div class="perente">{"".join(schede)}</div>'


def pagina_citta(c, prossime):
    qui = [s for s in sedi if s["provincia"] == c["provincia"]]
    in_citta = [s for s in qui if nel_capoluogo(s, c)]
    prov = escape(nome_provincia(c))
    in_prov = [s for s in qui if s not in in_citta]
    regione = regione_di(c)
    blocchi = []
    for e in ENTE:
        lista = [s for s in in_citta if s["ente"] == e]
        tutte = (f'<p class="small"><a href="../../ente/{SLUG_ENTE[e]}/#{slug(regione)}">Tutte le sedi {e} in {escape(regione)}</a></p>'
                 if regione else "")
        if lista:
            blocchi.append(f'<h3 id="sedi-{SLUG_ENTE[e]}">{eb(e)} {e} a {escape(c["nome"])} ({len(lista)})</h3><ul class="sedi">{"".join(scheda_sede(s) for s in lista)}</ul>{tutte}')
        elif any(s["ente"] == e for s in in_prov):
            blocchi.append(f'<h3 id="sedi-{SLUG_ENTE[e]}">{eb(e)} {e} in provincia di {prov}</h3>'
                           f'<ul class="sedi">{"".join(scheda_sede(s) for s in in_prov if s["ente"] == e)}</ul>{tutte}')
    mancano = [e for e in ENTE if not any(s["ente"] == e for s in qui)]
    altre_prov = [s for s in in_prov if any(s["ente"] == e for e in ENTE) and any(x["ente"] == s["ente"] for x in in_citta)]
    if altre_prov:
        blocchi.append(f'<details><summary>Altre sedi in provincia di {prov} ({len(altre_prov)}){ic("giu")}</summary>'
                       f'<ul class="sedi">{"".join(scheda_sede(s) for s in altre_prov)}</ul></details>')
    nota_mancano = ""
    if mancano:
        nota_mancano = (f'<p class="small">In provincia di {prov} non risultano sedi {", ".join(mancano)}: '
                        f'guarda le sedi nelle province vicine nelle pagine {", ".join(f'<a href="../../ente/{SLUG_ENTE[e]}/#{ancora_regione(e, regione)}">{e}</a>' for e in mancano)}.</p>')
    ordinate = sorted(citta, key=lambda x: x["nome"])
    vicine = [x for x in ordinate if x != c and regione and regione_di(x) == regione]
    altre = "".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>'
                    for x in sorted(principali(), key=lambda x: x["nome"]) if x != c and x not in vicine)
    altre += f'<a href="../../#citta">Tutte le {len(citta)} città</a>'
    vicine_html = (f'<h3>{ic("pin")}In {escape(regione)}</h3><div class="altre">{"".join(f"<a href=\"../{x["slug"]}/\">{escape(x["nome"])}</a>" for x in vicine)}</div><h3>Altre città in Italia</h3>'
                   if vicine else "")
    enti_qui = [e for e in ENTE if any(s["ente"] == e for s in qui)]
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), ("Città", "../../#citta"), (c["nome"], None))}
<h1>Esame B1 per la cittadinanza a {escape(c['nome'])}: date e sedi {anni(prossime)}</h1>
<p class="lead">A {escape(c['nome'])} e provincia ci sono <strong>{len(qui)} sedi</strong> dove puoi fare l'esame di italiano B1 per la cittadinanza
({", ".join(f"{sum(1 for s in qui if s['ente'] == e)} {e}" for e in enti_qui)}).
Le date d'esame sono le stesse in tutta Italia; la scadenza per iscriversi può cambiare da sede a sede.</p>
{risposta(prossime, "")}
<div class="azioni"><a class="btn" href="#avvisami">{ic("campana")}Avvisami per {escape(c['nome'])}</a><a class="btn btn-2" href="#sedi">{ic("pin")}Vedi le {len(qui)} sedi</a></div>
</section>
{avviso("Contatta la sede prima di iscriverti: ti dice costo, documenti e ultimo giorno per iscriverti.")}
<section>
<h2 id="per-ente">{ic("cal")}Prossime date a {escape(c['nome'])}, ente per ente</h2>
{per_ente(c, qui, in_citta, prossime)}
</section>
<div class="due">
<section>
<h2 id="date">{ic("lista")}Tutte le prossime date (valide anche a {escape(c['nome'])})</h2>
{lista_sessioni(prossime)}
</section>
<aside>
{modulo(c['nome'])}
</aside>
</div>
<section>
<h2 id="sedi">{ic("edificio")}Sedi d'esame a {escape(c['nome'])}</h2>
{"".join(blocchi) or "<p>Nessuna sede trovata nelle fonti ufficiali.</p>"}
{nota_mancano}
</section>
<section>
<h2>{ic("info")}Prima di iscriverti</h2>
{link_guide("../../")}
</section>
<section><h2>{ic("pin")}Altre città</h2>{vicine_html}<div class="altre">{altre}</div></section>"""
    pagina(f"citta/{c['slug']}/index.html",
           f"Esame B1 cittadinanza {c['nome']}: date {anni(prossime)} e {len(qui)} sedi | EsameB1",
           f"Dove fare l'esame di italiano B1 per la cittadinanza a {c['nome']}: {len(qui)} sedi {', '.join(enti_qui)}, "
           "prossime date, scadenze di iscrizione e costi.", corpo)


# Come la gente cerca ogni esame (Google, suggerimenti di ricerca del 12/10/2026).
NOME_RICERCA = {"CILS": "CILS B1 Cittadinanza", "CELI": "CELI B1 cittadinanza", "PLIDA": "PLIDA B1 per la cittadinanza",
                "CERT.IT": "CERT.IT B1 cittadinanza (Roma Tre)"}


def pagina_ente(e, prossime):
    sigla = e["sigla"]
    sue = [s for s in sedi if s["ente"] == sigla]
    regioni = sorted({s["regione"] for s in sue})
    blocchi = "".join(
        f'<details id="{slug(r)}"><summary>{escape(r)} ({sum(1 for s in sue if s["regione"] == r)}){ic("giu")}</summary>'
        f'<ul class="sedi">{"".join(scheda_sede(s) for s in sue if s["regione"] == r)}</ul></details>'
        for r in regioni)
    date_ente = [s for s in prossime if s["ente"] == sigla]
    nome_r = NOME_RICERCA[sigla]
    breve = e.get("fatti", {}).get("costo", {}).get("breve", "")
    citta_ente = [(c, sum(1 for s in sue if s["provincia"] == c["provincia"])) for c in sorted(citta, key=lambda c: c["nome"])]
    citta_link = "".join(f'<a href="../../citta/{c["slug"]}/">{escape(c["nome"])} ({n})</a>' for c, n in citta_ente if n)
    fatti = "".join(scheda_fatto(e, k, bottone=("Vedi il tuo risultato" if k == "risultati" else "Apri la prova" if k == "esempi" else None))
                    for k in VOCI_FATTI if k in e.get("fatti", {}) or k in ("costo", "risultati"))
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), (sigla, None))}
<span class="occhiello">{ic("scudo")}{escape(e['ente'])}</span>
<h1>{escape(nome_r)}: date, costo e sedi in Italia</h1>
<p class="lead">{escape(e['cittadinanza'])} {escape(e['iscrizione'])}</p>
<ul class="cifre"><li>{eb(sigla)}<span>{escape(e['nome'])}</span></li>
<li>{ic("web")}<a href="{escape(e['sito'])}" rel="noopener">sito ufficiale</a></li>
<li>{ic("cal")}<a href="{escape(e['pagina_date'])}" rel="noopener">calendario ufficiale</a></li>
<li>{ic("lista")}<a href="{escape(e['pagina_sedi'])}" rel="noopener">elenco ufficiale delle sedi</a></li></ul>
</section>
<div class="due">
<section>
<h2 id="date">{ic("cal")}Prossime date {escape(sigla)} (livello B1)</h2>
{lista_sessioni(date_ente, con_filtri=False) if date_ente else "<p>Nessuna data futura pubblicata al momento. Controlliamo il calendario ufficiale ogni settimana.</p>"}
</section>
<aside>{modulo()}</aside>
</div>
<section>
<h2 id="in-breve">{ic("info")}{escape(sigla)} B1 in breve: costo, durata, risultati</h2>
<div class="fatti">{fatti}</div>
</section>
<section>
<h2 id="sedi">{ic("edificio")}Sedi {escape(sigla)} in Italia ({len(sue)})</h2>
{f'<p class="small" style="margin:0 0 8px">Nelle città con una pagina dedicata (con le date e il modulo Avvisami):</p><div class="altre" style="margin-bottom:18px">{citta_link}</div>' if citta_link else ""}
{blocchi}
</section>"""
    periodo = f" {anni(date_ente)}" if date_ente else ""
    pagina(f"ente/{SLUG_ENTE[sigla]}/index.html",
           f"{nome_r}: date{periodo}, costo e {len(sue)} sedi | EsameB1",
           f"Date{periodo} dell'esame {nome_r}, scadenze, costo{f': {breve}' if breve else ''}, durata, risultati "
           f"e le {len(sue)} sedi in Italia divise per regione.",
           corpo)


def come_funziona():
    righe = "".join(
        f"<tr><td>{eb(e['sigla'])}<br><span class='small'>{escape(e['ente'])}</span></td>"
        f"<td>{escape(e['cittadinanza'])}</td><td>{sum(1 for s in sedi if s['ente'] == e['sigla'])}</td>"
        f"<td><a href='../ente/{SLUG_ENTE[e['sigla']]}/'>date e sedi</a></td></tr>" for e in enti)
    # Fonti per "si può fare online?": FAQ PLIDA, regole del giorno d'esame CILS e CELI, svolgimento CERT.IT.
    online_fonti = []
    for e in enti:
        f = e.get("fatti", {}).get("nota" if e["sigla"] in ("PLIDA", "CERT.IT") else "documenti")
        if f:
            online_fonti.append(f["fonti"][0])
    online_link = " · ".join(f'<a href="{escape(x["url"])}" rel="noopener">{escape(x["nome"])}</a>' for x in online_fonti)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Come funziona", None))}
<h1>Esame B1 per la cittadinanza: come funziona, quanto dura, cosa portare</h1>
<p class="lead">Spiegato in modo semplice: chi deve farlo, quali esami valgono, quanto dura, cosa portare, dove trovare esempi d'esame gratis.</p>
</section>
<h2>{ic("info")}Chi deve fare l'esame</h2>
<p>Dal 4 dicembre 2018 chi chiede la cittadinanza italiana <strong>per residenza o per matrimonio</strong> deve dimostrare di conoscere l'italiano
almeno al livello B1 (art. 9.1 della legge 91/1992). Si può farlo con un titolo di studio italiano oppure con un certificato di un ente riconosciuto.
Fonte: <a href="{PREFETTURA}" rel="noopener">Prefettura – Ministero dell'Interno</a>. Per il tuo caso specifico chiedi alla Prefettura: questo sito non dà consulenza.</p>
<h2>{ic("scudo")}I 4 enti riconosciuti</h2>
<div class="tab-wrap"><table class="conf"><thead><tr><th>Ente</th><th>Esame per la cittadinanza</th><th>Sedi in Italia</th><th></th></tr></thead>
<tbody>{righe}</tbody></table></div>
<h2>{ic("lista")}Come ci si iscrive</h2>
<ol class="passi">
<li><span>Scegli una data dal <a href="../#date">calendario</a>.</span></li>
<li><span>Scegli una sede nella tua città (<a href="../#citta">elenco per città</a>).</span></li>
<li><span>Contatta la sede: ti dice costo, documenti e ultimo giorno per iscriverti. Alcune sedi chiudono le iscrizioni prima della scadenza nazionale.</span></li>
<li><span>Paga e conserva la ricevuta. Il giorno dell'esame porta un documento d'identità valido.</span></li>
</ol>
<h2 id="durata">{ic("orologio")}Quanto dura l'esame</h2>
<p>Prima c'è lo scritto (ascolto, lettura, scrittura), poi un orale di 10-15 minuti con un esaminatore, di solito lo stesso giorno.</p>
{schede_per_ente("durata")}
<h2 id="documenti">{ic("doc")}Documenti e cosa portare</h2>
{schede_per_ente("documenti")}
<h2 id="online">{ic("attenzione")}Si può fare l'esame online?</h2>
<p><strong>No.</strong> L'esame si fa in presenza, in una sede d'esame: PLIDA lo scrive nelle sue FAQ ufficiali, CILS e CELI chiedono di presentarsi con un documento d'identità,
per CERT.IT l'orale si fa in presenza. A Roma Tre lo scritto del CERT.IT B1 si fa al computer, ma sempre in sede.</p>
<div class="fonte">{ic("doc")}<span>Fonti: {online_link}</span></div>
<h2 id="esempi">{ic("libro")}Esempi d'esame gratis (sito ufficiale)</h2>
<p>Ogni ente pubblica una prova d'esempio gratuita: è il modo migliore per capire com'è l'esame.</p>
{schede_per_ente("esempi", bottone="Apri la prova d'esempio")}
<h2>{ic("euro")}Costo e risultati</h2>
<p>CILS B1 Cittadinanza costa 100 €, CERT.IT B1 80 € a Roma Tre; per CELI e PLIDA il prezzo lo decide il centro. <a href="../costo/">Tutti i costi</a> ·
<a href="../risultati/">Quando arrivano i risultati</a>.</p>
{modulo()}"""
    pagina("come-funziona/index.html", "Esame B1 cittadinanza: come funziona, quanto dura, esempi d'esame | EsameB1",
           "Chi deve fare l'esame di italiano B1 per la cittadinanza, i 4 enti riconosciuti (CILS, CELI, PLIDA, CERT.IT), "
           "quanto dura, cosa portare, esempi d'esame gratis e come ci si iscrive.", corpo)


def pagina_costo():
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Costo", None))}
<h1>Quanto costa l'esame B1 per la cittadinanza</h1>
<p class="lead">Il prezzo cambia secondo l'ente e, per CELI e PLIDA, secondo la sede. Qui trovi le cifre pubblicate dagli enti, con la fonte.</p>
</section>
{schede_per_ente("costo", breve=True)}
{avviso("Chiedi sempre alla sede il <strong>prezzo finale</strong> prima di pagare: alcune sedi aggiungono spese amministrative (all'Università degli Studi di Milano, per esempio, 25 € sui 90 € del CELI 2 i cittadinanza).")}
<div class="due">
<section>
<h2>{ic("pin")}Trova una sede e chiedi il prezzo</h2>
<p>Scegli la tua città: per ogni sede trovi indirizzo, telefono, email e sito.</p>
{citta_per_regione("../")}
<h2>{ic("info")}Altre domande</h2>
{link_guide("../", salta="costo/")}
</section>
<aside>{modulo()}</aside>
</div>"""
    pagina("costo/index.html", "Esame B1 cittadinanza: quanto costa (CILS, CELI, PLIDA, CERT.IT) | EsameB1",
           "Quanto costa l'esame di italiano B1 per la cittadinanza: CILS B1 Cittadinanza 100 €, CERT.IT B1 80 € a Roma Tre, "
           "CELI e PLIDA a prezzo del centro d'esame. Con le fonti ufficiali.", corpo)


def pagina_risultati(prossime):
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Risultati", None))}
<h1>Risultati dell'esame B1 per la cittadinanza: quando arrivano e dove vederli</h1>
<p class="lead">Il risultato non arriva il giorno dell'esame: lo pubblica l'ente, online, dopo alcuni mesi. Ecco i tempi e dove guardare per ogni ente.</p>
</section>
{schede_per_ente("risultati", breve=True, bottone="Vedi il tuo risultato")}
<div class="due">
<section>
<h2 id="date">{ic("cal")}Non hai superato l'esame? Le prossime date</h2>
{lista_sessioni(prossime[:6], con_filtri=False)}
<p><a href="../#date">Tutte le date</a></p>
</section>
<aside>{modulo()}</aside>
</div>
<section>
<h2>{ic("info")}Altre domande</h2>
{link_guide("../", salta="risultati/")}
</section>"""
    pagina("risultati/index.html", "Risultati esame B1 cittadinanza: quando arrivano e dove vederli | EsameB1",
           "Quando escono i risultati dell'esame B1 per la cittadinanza (CILS circa 3 mesi, CELI circa 90 giorni lavorativi), "
           "dove vederli online e come avere il certificato.", corpo)


def privacy():
    corpo = f"""<section class="hero">{briciole(("EsameB1", "./"), ("Privacy", None))}<h1>Informativa privacy</h1><p class="small">Ultimo aggiornamento: ottobre 2026</p></section>
<h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce {NOME} come progetto indipendente. Puoi scriverci rispondendo a qualsiasi email che ti mandiamo.</p>
<h2>Quali dati raccogliamo</h2><p>Solo se compili il modulo "Avvisami": la tua email, la città e l'ente che scegli, e la pagina o il link da cui arrivi (per capire quali canali funzionano).</p>
<h2>Perché</h2><p>Per mandarti avvisi sulle date e sulle scadenze dell'esame B1. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi ritirare quando vuoi.</p>
<h2>Chi li gestisce per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i dati del modulo per nostro conto. Netlify può trattare i dati fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>
<h2>Cookie e contatore visite</h2><p>Questo sito non usa cookie di profilazione. Per contare le visite usiamo <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, un contatore rispettoso della privacy: non usa cookie e non salva nulla nel browser, non crea profili e non conserva l'indirizzo IP, la firma completa del browser né altri identificativi. Tiene solo numeri aggregati (pagina, ora o giorno, browser, Paese, larghezza dello schermo) su server nell'Unione europea e non cede nulla a terzi; vedi l'<a href="https://www.goatcounter.com/help/privacy" rel="noopener">informativa privacy di GoatCounter</a>.</p>
<h2>Per quanto tempo</h2><p>Finché resti iscritto agli avvisi. Se chiedi la cancellazione, cancelliamo i tuoi dati.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e puoi fare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>"""
    pagina("privacy.html", "Privacy | EsameB1", "Informativa privacy del sito EsameB1.", corpo)


def extra(urls):
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in urls)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in esameb1/sito (ogni pubblicazione consuma crediti Netlify).
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
""")
    pagina("404.html", "Pagina non trovata | EsameB1", "Pagina non trovata.",
           '<section class="hero"><span class="occhiello">Errore 404</span><h1>Pagina non trovata</h1><p class="lead">Torna al <a href="/">calendario delle date</a>.</p>'
           f'<div class="azioni"><a class="btn" href="/">{ic("cal")}Vedi tutte le date</a><a class="btn btn-2" href="/#citta">{ic("pin")}Sedi per città</a></div></section>',
           base="/")


def controlli(prossime):
    errori = []
    for s in sessioni:
        if not s.get("fonte") or not s.get("verificato_il"):
            errori.append(f"sessione senza fonte: {s}")
        if s.get("scadenza") and d(s["scadenza"]) >= d(s["data"]):
            errori.append(f"scadenza non prima dell'esame: {s['ente']} {s['data']}")
    for s in sedi:
        if not s.get("fonte") or not s.get("citta"):
            errori.append(f"sede incompleta: {s['ente']} {s['nome']}")
    for c in citta:
        if not any(s["provincia"] == c["provincia"] for s in sedi):
            errori.append(f"città senza sedi: {c['nome']}")
    if not prossime:
        errori.append("nessuna sessione futura")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    prossime = sorted(future(sessioni), key=lambda s: (s["data"], s["ente"]))
    controlli(prossime)
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}  # verifica Search Console
        shutil.rmtree(SITO)
    else:
        conserva = {}
    SITO.mkdir()
    shutil.copy(RADICE / "assets" / "og.png", SITO / "og.png")
    shutil.copytree(RADICE / "assets" / "fonts", SITO / "fonts")  # Figtree (SIL OFL), servito dal sito stesso
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    home(prossime)
    urls = [""]
    for c in citta:
        pagina_citta(c, prossime)
        urls.append(f"citta/{c['slug']}/")
    for e in enti:
        pagina_ente(e, prossime)
        urls.append(f"ente/{SLUG_ENTE[e['sigla']]}/")
    come_funziona()
    urls.append("come-funziona/")
    pagina_costo()
    urls.append("costo/")
    pagina_risultati(prossime)
    urls.append("risultati/")
    privacy()
    urls.append("privacy.html")
    extra(urls)
    print(f"Sito generato in {SITO}: {len(urls)} pagine, {len(prossime)} sessioni future, {len(sedi)} sedi.")


if __name__ == "__main__":
    main()
