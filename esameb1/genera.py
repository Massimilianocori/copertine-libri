"""Genera il sito statico EsameB1 in esameb1/sito/ a partire da esameb1/dati/.

Uso (dalla radice del repository):
    python3 esameb1/genera.py

Dati: enti.json, sessioni.json (date curate a mano, con fonte), sedi.json (da raccolta/raccogli.py),
citta.json (pagine città). Nessuna dipendenza esterna.
"""
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://esameb1.netlify.app"  # cambiare qui se il nome del sito su Netlify è diverso
NOME = "EsameB1"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, proprietà https://esameb1.netlify.app
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
@media (max-width:640px){.chips{flex-wrap:nowrap;overflow-x:auto;margin-right:-16px;padding-right:16px;padding-bottom:6px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}}
/* sessioni */
.sessioni{display:grid;gap:12px}
.sess{display:grid;grid-template-columns:76px 1fr;gap:16px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px;
min-width:0;overflow-wrap:anywhere;box-shadow:var(--ombra)}
.sess[hidden]{display:none}
.tile{display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:12px;background:var(--surface-2);padding:8px 4px;align-self:start;
line-height:1;text-align:center;border-top:4px solid var(--brand)}
.sess[data-tipo="generale"] .tile{border-top-color:var(--line-2)}
.tile .tm{font-size:.76rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--brand-ink)}
.tile .td{font-size:1.9rem;font-weight:800;letter-spacing:-.03em;margin:4px 0 3px;font-variant-numeric:tabular-nums}
.tile .ty{font-size:.75rem;color:var(--ink-3);font-weight:600}
.sess .cosa{min-width:0}
.sess .tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.sess .nome{font-weight:750;font-size:1.06rem;line-height:1.3}
.sess .giorno{font-size:.9rem;color:var(--ink-3);margin-bottom:8px}
.scad{display:grid;grid-template-columns:auto minmax(0,1fr);gap:2px 8px;font-size:.94rem;color:var(--ink-2);padding:10px 12px;background:var(--surface-2);border-radius:10px}
.scad>.i{color:var(--ink-3);margin-top:3px}
.scad .riga{min-width:0;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.scad strong{color:var(--ink)}
.scad.urgente strong{color:var(--rosso)}
.scad.chiusa{color:var(--ink-3)}
.scad.chiusa strong{color:var(--ink-3);text-decoration:line-through;text-decoration-thickness:1px}
.scad.chiusa .stato{white-space:normal;background:none;padding:0;font-weight:600;font-size:.86rem;color:var(--ink-3)}
.scad .nota{grid-column:2;font-size:.84rem;color:var(--ink-3)}
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
.sedi{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.sedi li{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;min-width:0;overflow-wrap:anywhere}
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
@media (max-width:860px){.due{grid-template-columns:1fr;gap:8px}.risposta{grid-template-columns:1fr}}
@media (max-width:640px){body{font-size:16.5px}.lead{font-size:1.02rem}.r-piede span{display:none}.sess{grid-template-columns:1fr;gap:10px;padding:14px}.tile{flex-direction:row;align-items:baseline;justify-self:start;gap:7px;padding:6px 12px;border-top:0;border-left:4px solid var(--brand)}.sess[data-tipo="generale"] .tile{border-left-color:var(--line-2)}.tile .td{font-size:1.3rem;margin:0}
.card{padding:18px}.risposta .slot{padding:16px}.hero{padding-top:22px}}
.altre{display:flex;flex-wrap:wrap;gap:6px}
.altre a{font-size:.9rem;padding:5px 11px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink-2);background:var(--surface)}
.altre a:hover{border-color:var(--brand);color:var(--brand-ink)}
/* piede */
footer.piede{margin-top:64px;background:#13201E;color:#C4D2CD;padding:36px 0 44px;font-size:.9rem}
footer.piede::before{content:"";display:block;height:4px;margin-top:-36px;margin-bottom:32px;background:linear-gradient(90deg,#0B6B4F 0 33.3%,#F4F1EA 33.3% 66.6%,#C8402A 66.6%)}
footer.piede a{color:#E8F0ED}
footer.piede .logo{color:#FFFFFF}
footer.piede .logo b{color:#6AD6AB}
footer.piede .marchio{--brand:#4CC596;--on-brand:#052118}
.piede-griglia{display:grid;grid-template-columns:1.2fr 1fr;gap:28px;align-items:start}
.piede-link{display:flex;flex-wrap:wrap;gap:8px 18px;list-style:none;padding:0;margin:14px 0 0}
.piede-link a{text-decoration:none;font-weight:600}
.piede-link a:hover{text-decoration:underline}
.piede p{margin:0 0 12px;max-width:70ch}
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
  var bott=document.querySelectorAll('.chips button');
  bott.forEach(function(b){b.addEventListener('click',function(){
    bott.forEach(function(x){x.setAttribute('aria-pressed','false');});b.setAttribute('aria-pressed','true');
    var f=b.dataset.filtro;
    document.querySelectorAll('.sess').forEach(function(el){
      el.hidden=!(f==='tutti'||(f==='citt'&&el.dataset.tipo==='cittadinanza')||el.dataset.ente===f);
    });
  });});
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
<li><a href="{rel}#date">Date d'esame</a></li><li><a href="{rel}#citta">Sedi per città</a></li><li><a href="{rel}come-funziona/">Come funziona</a></li>{enti_link}<li><a href="{rel}privacy.html">Privacy</a></li>
</ul>
</div>
<div>
<p><strong>{NOME}</strong> è un sito indipendente, non affiliato agli enti certificatori. CILS, CELI, PLIDA e CERT.IT sono marchi dei rispettivi enti.
Le informazioni vengono dalle fonti ufficiali indicate accanto a ogni dato. <strong>Prima di iscriverti verifica sempre sul sito della sede.</strong>
Questo sito non dà consulenza sulla pratica di cittadinanza: per quella vedi la <a href="https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza" rel="noopener">pagina del Ministero dell'Interno</a>.</p>
<p><span class="dati">{ic("scudo")}Dati controllati il {verificato_ultimo()}.</span> · <a href="{rel}privacy.html">Privacy</a> · <a href="{rel}come-funziona/">Come funziona</a></p>
</div>
</div>
</div></footer>
<script>{JS}</script>
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


def scheda_sessione(s):
    citt = s["tipo"] == "cittadinanza"
    esami = ", ".join(s["esami"])
    badge = (f'<span class="tag citt">{ic("ok")}Esame per la cittadinanza</span>' if citt
             else f'<span class="tag">{ic("ok")}B1 valido per la cittadinanza</span>')
    if s.get("scadenza"):
        scad = (f'<div class="scad" data-scadenza="{s["scadenza"]}">{ic("orologio")}<div class="riga">Iscrizioni entro: <strong>{data_breve(s["scadenza"])}</strong>'
                f'<span class="stato conta"></span></div><span class="nota">{escape(s["nota_scadenza"])}</span></div>')
    else:
        scad = f'<div class="scad">{ic("orologio")}<div class="riga">{escape(s["nota_scadenza"])}</div></div>'
    return f"""<article class="sess" data-data="{s['data']}" data-ente="{escape(s['ente'])}" data-tipo="{s['tipo']}">
{tile(s['data'])}
<div class="cosa"><div class="tags">{eb(s['ente'])}{badge}</div>
<div class="nome">{escape(esami)}</div>
<div class="giorno"><time datetime="{s['data']}">{data_lunga(s['data'])}</time></div>
{scad}
<div class="fonte">{ic("doc")}<span>Fonte: <a href="{escape(s['fonte'])}" rel="noopener">calendario ufficiale {escape(s['ente'])}</a> · controllato il {data_breve(s['verificato_il'])}</span></div>
</div>
</article>"""


def lista_sessioni(lista, con_filtri=True):
    filtri = ""
    if con_filtri:
        bottoni = ['<button type="button" data-filtro="tutti" aria-pressed="true">Tutte</button>',
                   f'<button type="button" data-filtro="citt" aria-pressed="false">{ic("ok")}Solo esami "cittadinanza"</button>']
        bottoni += [f'<button type="button" data-filtro="{e}" aria-pressed="false"><span class="pt" style="background:var(--{e.replace(".", "").lower()})"></span>{e}</button>'
                    for e in ENTE]
        filtri = f'<div class="filtri chips" role="group" aria-label="Filtra per ente">{"".join(bottoni)}</div>'
    return filtri + '<div class="sessioni">' + "\n".join(scheda_sessione(s) for s in lista) + "</div>"


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
<div class="r-data"><small>entro {il(s['scadenza']).strip()}</small> {data_breve(s['scadenza'])}</div>
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
    if s.get("email"):
        contatti.append(f'<a href="mailto:{escape(s["email"])}">{ic("mail")}{escape(s["email"])}</a>')
    if s.get("sito"):
        url = s["sito"] if s["sito"].startswith("http") else "https://" + s["sito"]
        contatti.append(f'<a href="{escape(url)}" rel="noopener nofollow">{ic("web")}sito</a>')
    return f"""<li><div class="nome">{eb(s['ente'])}<span>{escape(s['nome'])}</span></div>
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
            "performer": {"@type": "Organization", "name": e["ente"]},
            "offers": {"@type": "Offer", "url": e["pagina_date"], "availability": "https://schema.org/InStock", "validFrom": s["verificato_il"]},
            "description": f'Sessione d\'esame {s["ente"]} di livello B1, valida per la domanda di cittadinanza italiana.',
        })
    return {"@context": "https://schema.org", "@graph": eventi}


def avviso(testo):
    return f'<div class="avviso">{ic("attenzione")}<div>{testo}</div></div>'


def briciole(*voci):
    parti = [f'<a href="{h}">{escape(t)}</a>' if h else f'<span aria-current="page">{escape(t)}</span>' for t, h in voci]
    return f'<nav class="briciole" aria-label="Sei qui">{" <span aria-hidden=\"true\">›</span> ".join(parti)}</nav>'


def domanda(titolo, testo):
    return f'<details><summary>{titolo}{ic("giu")}</summary>\n<p>{testo}</p></details>'


# ---------------------------------------------------------------- pagine
def home(prossime):
    per_citta = {c["slug"]: sum(1 for s in sedi if s["provincia"] == c["provincia"]) for c in citta}
    griglia = "".join(
        f'<a href="citta/{c["slug"]}/">{ic("pin")}<span>{escape(c["nome"])}<small>{per_citta[c["slug"]]} {"sede" if per_citta[c["slug"]] == 1 else "sedi"}</small></span></a>'
        for c in sorted(citta, key=lambda c: c["nome"]))
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
<section id="citta">
<h2>{ic("pin")}Sedi per città</h2>
<div class="griglia">{griglia}</div>
<p class="small">La tua città non c'è? Guarda le sedi per regione nelle pagine
{", ".join(f'<a href="ente/{SLUG_ENTE[e]}/">{e}</a>' for e in ENTE)}.</p>
</section>
</aside>
</div>
<section>
<h2>{ic("info")}Domande frequenti</h2>
{domanda("Quale esame devo fare per la cittadinanza?", f'Serve un certificato di italiano almeno di livello B1, rilasciato da uno dei 4 enti riconosciuti: CILS (Università per Stranieri di Siena), CELI (Università per Stranieri di Perugia), PLIDA (Società Dante Alighieri) e CERT.IT (Università Roma Tre). Fonte: <a href="{PREFETTURA}" rel="noopener">Prefettura – Ministero dell\'Interno</a>. Per i casi particolari (titoli di studio italiani, esenzioni) chiedi alla Prefettura.')}
{domanda('Che differenza c\'è tra "B1 cittadinanza" e B1 normale?', 'CILS e CELI hanno un esame B1 pensato per la cittadinanza, con più sessioni durante l\'anno. Il B1 "normale" degli stessi enti, il PLIDA B1 e il CERT.IT B1 sono anch\'essi certificati di livello B1. Leggi la <a href="come-funziona/">pagina Come funziona</a>.')}
{domanda("Come mi iscrivo?", "Ci si iscrive presso la sede d'esame, non su questo sito. Scegli una sede nella tua città, contattala e chiedi costo, documenti e scadenza.")}
{domanda("Quanto costa l'esame?", "Il prezzo lo decide la sede. Per esempio: CELI 2 i cittadinanza 90 € all'Università degli Studi di Milano (febbraio 2026), CILS B1 Cittadinanza 100 € all'Università di Padova. Chiedi il prezzo alla sede che scegli.")}
<p class="small">Per chiedere la cittadinanza italiana per residenza o matrimonio serve un certificato di italiano di livello B1.
Qui trovi in un solo posto le date, le scadenze e le sedi dei 4 enti riconosciuti: CILS, CELI, PLIDA e CERT.IT.</p>
</section>"""
    pagina("index.html", "Esame B1 cittadinanza: date 2026-2027, scadenze e sedi | EsameB1",
           "Tutte le date dell'esame di italiano B1 per la cittadinanza (CILS, CELI, PLIDA, CERT.IT), scadenze di iscrizione e "
           f"{len(sedi)} sedi in Italia, in un solo posto.", corpo, jsonld_sessioni(prossime))


def pagina_citta(c, prossime):
    qui = [s for s in sedi if s["provincia"] == c["provincia"]]
    in_citta = [s for s in qui if s["citta"] == c["provincia"] or s["citta"] == c["nome"]]
    in_prov = [s for s in qui if s not in in_citta]
    blocchi = []
    for e in ENTE:
        lista = [s for s in in_citta if s["ente"] == e]
        if lista:
            blocchi.append(f'<h3>{eb(e)} {e} a {escape(c["nome"])} ({len(lista)})</h3><ul class="sedi">{"".join(scheda_sede(s) for s in lista)}</ul>')
    mancano = [e for e in ENTE if not any(s["ente"] == e for s in qui)]
    if in_prov:
        blocchi.append(f'<details><summary>Altre sedi in provincia di {escape(c["nome"])} ({len(in_prov)}){ic("giu")}</summary>'
                       f'<ul class="sedi">{"".join(scheda_sede(s) for s in in_prov)}</ul></details>')
    nota_mancano = ""
    if mancano:
        nota_mancano = (f'<p class="small">In provincia di {escape(c["nome"])} non risultano sedi {", ".join(mancano)}: '
                        f'guarda le sedi nelle province vicine nelle pagine {", ".join(f'<a href="../../ente/{SLUG_ENTE[e]}/">{e}</a>' for e in mancano)}.</p>')
    altre = "".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>' for x in sorted(citta, key=lambda x: x["nome"]) if x != c)
    conteggi = "".join(f'<li>{eb(e)}<span><strong>{n_e}</strong> {"sede" if n_e == 1 else "sedi"}</span></li>'
                       for e in ENTE for n_e in [sum(1 for s in qui if s["ente"] == e)] if n_e)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), ("Città", "../../#citta"), (c["nome"], None))}
<h1>Esame B1 per la cittadinanza a {escape(c['nome'])}: date e sedi 2026-2027</h1>
<p class="lead">A {escape(c['nome'])} e provincia ci sono <strong>{len(qui)} sedi</strong> dove puoi fare l'esame di italiano B1 per la cittadinanza
({", ".join(f"{sum(1 for s in qui if s['ente'] == e)} {e}" for e in ENTE if any(s['ente'] == e for s in qui))}).
Le date d'esame sono le stesse in tutta Italia; la scadenza per iscriversi può cambiare da sede a sede.</p>
{risposta(prossime, "")}
<div class="azioni"><a class="btn" href="#avvisami">{ic("campana")}Avvisami per {escape(c['nome'])}</a><a class="btn btn-2" href="#sedi">{ic("pin")}Vedi le {len(qui)} sedi</a></div>
<ul class="cifre">{conteggi}</ul>
</section>
{avviso("Contatta la sede prima di iscriverti: ti dice costo, documenti e ultimo giorno per iscriverti.")}
<div class="due">
<section>
<h2 id="sedi">{ic("edificio")}Sedi d'esame a {escape(c['nome'])}</h2>
{"".join(blocchi) or "<p>Nessuna sede trovata nelle fonti ufficiali.</p>"}
{nota_mancano}
<h2 id="date">{ic("cal")}Prossime date (valide anche a {escape(c['nome'])})</h2>
{lista_sessioni(prossime)}
</section>
<aside>
{modulo(c['nome'])}
<section><h2>{ic("pin")}Altre città</h2><div class="altre">{altre}</div></section>
</aside>
</div>"""
    pagina(f"citta/{c['slug']}/index.html",
           f"Esame B1 cittadinanza {c['nome']}: date 2026-2027 e {len(qui)} sedi | EsameB1",
           f"Dove fare l'esame di italiano B1 per la cittadinanza a {c['nome']}: {len(qui)} sedi CILS, CELI, PLIDA e CERT.IT, "
           "prossime date e scadenze di iscrizione.", corpo)


def pagina_ente(e, prossime):
    sigla = e["sigla"]
    sue = [s for s in sedi if s["ente"] == sigla]
    regioni = sorted({s["regione"] for s in sue})
    blocchi = "".join(
        f'<details><summary>{escape(r)} ({sum(1 for s in sue if s["regione"] == r)}){ic("giu")}</summary>'
        f'<ul class="sedi">{"".join(scheda_sede(s) for s in sue if s["regione"] == r)}</ul></details>'
        for r in regioni)
    date_ente = [s for s in prossime if s["ente"] == sigla]
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../../"), (sigla, None))}
<h1>{escape(e['nome'])}: date B1 per la cittadinanza e sedi in Italia</h1>
<p class="lead">{escape(e['cittadinanza'])} {escape(e['iscrizione'])}</p>
<ul class="cifre"><li>{eb(sigla)}<span>{escape(e['ente'])}</span></li>
<li>{ic("web")}<a href="{escape(e['sito'])}" rel="noopener">sito ufficiale</a></li>
<li>{ic("cal")}<a href="{escape(e['pagina_date'])}" rel="noopener">calendario ufficiale</a></li>
<li>{ic("lista")}<a href="{escape(e['pagina_sedi'])}" rel="noopener">elenco ufficiale delle sedi</a></li></ul>
</section>
<div class="due">
<section>
<h2 id="date">{ic("cal")}Prossime date {escape(sigla)} (livello B1)</h2>
{lista_sessioni(date_ente, con_filtri=False) if date_ente else "<p>Nessuna data futura pubblicata al momento. Controlliamo il calendario ufficiale ogni settimana.</p>"}
<h2>{ic("edificio")}Sedi {escape(sigla)} in Italia ({len(sue)})</h2>
{blocchi}
</section>
<aside>{modulo()}</aside>
</div>"""
    pagina(f"ente/{SLUG_ENTE[sigla]}/index.html",
           f"Esame {sigla} B1 cittadinanza: date e {len(sue)} sedi in Italia | EsameB1",
           f"Date dell'esame {sigla} di livello B1 per la cittadinanza, scadenze e le {len(sue)} sedi in Italia divise per regione.",
           corpo)


def come_funziona():
    righe = "".join(
        f"<tr><td>{eb(e['sigla'])}<br><span class='small'>{escape(e['ente'])}</span></td>"
        f"<td>{escape(e['cittadinanza'])}</td><td>{sum(1 for s in sedi if s['ente'] == e['sigla'])}</td>"
        f"<td><a href='../ente/{SLUG_ENTE[e['sigla']]}/'>date e sedi</a></td></tr>" for e in enti)
    corpo = f"""<section class="hero">
{briciole(("EsameB1", "../"), ("Come funziona", None))}
<h1>Esame B1 per la cittadinanza: come funziona</h1>
<p class="lead">Spiegato in modo semplice: chi deve farlo, quali esami valgono, come ci si iscrive.</p>
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
<h2>{ic("doc")}Quanto costa</h2>
<p>Lo decide la sede. Esempi reali: CELI 2 i cittadinanza 90 € all'Università degli Studi di Milano (sessione del 18 febbraio 2026),
CILS B1 Cittadinanza 100 € al Centro Linguistico dell'Università di Padova.</p>
{modulo()}"""
    pagina("come-funziona/index.html", "Esame B1 cittadinanza: come funziona, quali esami valgono | EsameB1",
           "Chi deve fare l'esame di italiano B1 per la cittadinanza, i 4 enti riconosciuti (CILS, CELI, PLIDA, CERT.IT), "
           "come ci si iscrive e quanto costa.", corpo)


def privacy():
    corpo = f"""<section class="hero">{briciole(("EsameB1", "./"), ("Privacy", None))}<h1>Informativa privacy</h1><p class="small">Ultimo aggiornamento: ottobre 2026</p></section>
<h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce {NOME} come progetto indipendente. Puoi scriverci rispondendo a qualsiasi email che ti mandiamo.</p>
<h2>Quali dati raccogliamo</h2><p>Solo se compili il modulo "Avvisami": la tua email, la città e l'ente che scegli, e la pagina o il link da cui arrivi (per capire quali canali funzionano).</p>
<h2>Perché</h2><p>Per mandarti avvisi sulle date e sulle scadenze dell'esame B1. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi ritirare quando vuoi.</p>
<h2>Chi li gestisce per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i dati del modulo per nostro conto. Netlify può trattare i dati fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>
<h2>Cookie</h2><p>Questo sito non usa cookie di profilazione né strumenti di statistica.</p>
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
    privacy()
    urls.append("privacy.html")
    extra(urls)
    print(f"Sito generato in {SITO}: {len(urls)} pagine, {len(prossime)} sessioni future, {len(sedi)} sedi.")


if __name__ == "__main__":
    main()
